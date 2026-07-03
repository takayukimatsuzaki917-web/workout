"""競技×ユーザープロフィールから筋トレプログラム一式を組み立てるロジック。

マスタデータ(data/配下のJSON)を読み込み、競技に紐づく推奨種目それぞれについて
目安重量・消費カロリーを算出してプログラムとしてまとめる。
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .calorie_calculator import (
    calculate_exercise_calories,
    calculate_session_calories,
    calculate_weekly_calories,
)
from .weight_calculator import recommend_weight

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# 回数指定の種目における、1レップあたりの概算所要時間(秒)。
SECONDS_PER_REP = 3
# 時間・距離指定などレップ数を読み取れない種目に使う、セットあたりの既定所要時間(秒)。
DEFAULT_SET_DURATION_SECONDS = 45


def load_sports_master() -> list[dict]:
    """競技マスタデータ(sports_master.json)を読み込む。"""
    with open(DATA_DIR / "sports_master.json", encoding="utf-8") as f:
        return json.load(f)


def load_exercises_master() -> list[dict]:
    """エクササイズマスタデータ(exercises_master.json)を読み込む。"""
    with open(DATA_DIR / "exercises_master.json", encoding="utf-8") as f:
        return json.load(f)


def _find_sport(sports: list[dict], sport_id: str) -> dict:
    """競技IDから該当する競技マスタのレコードを探す。見つからない場合はエラー。"""
    for sport in sports:
        if sport["id"] == sport_id:
            return sport
    raise ValueError(f"未知のsport_idです: {sport_id}")


def _find_exercise(exercises: list[dict], exercise_id: str) -> dict:
    """種目IDから該当するエクササイズマスタのレコードを探す。見つからない場合はエラー。"""
    for exercise in exercises:
        if exercise["id"] == exercise_id:
            return exercise
    raise ValueError(f"未知のexercise_idです: {exercise_id}")


def _extract_max_rep_count(default_reps: str) -> int | None:
    """"8-12"のような回数表記から概算レップ数（レンジの上限値）を取り出す。

    "30-60秒"や"20-40分"のような時間・距離表記の場合は数値は取れても
    レップ数としての意味を持たないため、呼び出し側でセットあたりの
    既定時間にフォールバックする前提。数字を一切含まない場合はNoneを返す。
    """
    numbers = [int(n) for n in re.findall(r"\d+", default_reps)]
    return max(numbers) if numbers else None


def _estimate_exercise_duration_minutes(exercise: dict) -> float:
    """セット数×回数（休憩込み）から1種目あたりの概算所要時間(分)を見積もる。"""
    sets = exercise["default_sets"]
    rest_seconds = exercise["rest_seconds"]
    reps_text = exercise["default_reps"]

    is_time_or_distance_based = any(unit in reps_text for unit in ("秒", "分", "m"))
    rep_count = None if is_time_or_distance_based else _extract_max_rep_count(reps_text)

    if rep_count is not None:
        work_seconds_per_set = rep_count * SECONDS_PER_REP
    else:
        work_seconds_per_set = DEFAULT_SET_DURATION_SECONDS

    total_seconds = sets * (work_seconds_per_set + rest_seconds)
    return round(total_seconds / 60, 1)


def build_program(profile: dict, sport_id: str) -> dict:
    """ユーザープロフィールと競技IDから筋トレプログラム一式を組み立てる。

    引数:
        profile: {
            "gender": str, "age": int, "bodyweight_kg": float, "height_cm": float,
            "level": "初心者" | "中級者" | "上級者",
        }
        sport_id: 競技ID（sports_master.jsonのid）
    戻り値:
        競技情報・種目一覧（重量目安・消費カロリー付き）・
        セッション/週間の想定消費カロリー合計を含む辞書
    """
    sports = load_sports_master()
    exercises = load_exercises_master()

    sport = _find_sport(sports, sport_id)
    bodyweight_kg = profile["bodyweight_kg"]
    level = profile["level"]
    training_purpose = sport["training_purpose"]

    exercise_entries = []
    exercise_calories = []

    for exercise_id in sport["recommended_exercise_ids"]:
        exercise = _find_exercise(exercises, exercise_id)
        weight_info = recommend_weight(exercise, bodyweight_kg, level, training_purpose)
        duration_minutes = _estimate_exercise_duration_minutes(exercise)
        calories = calculate_exercise_calories(exercise, bodyweight_kg, duration_minutes)
        exercise_calories.append(calories)

        exercise_entries.append({
            "id": exercise["id"],
            "name_ja": exercise["name_ja"],
            "equipment": exercise["equipment"],
            "description": exercise["description"],
            "target_muscles": exercise["target_muscles"],
            "muscle_svg_ids": exercise["muscle_svg_ids"],
            "sets": exercise["default_sets"],
            "reps": exercise["default_reps"],
            "rest_seconds": exercise["rest_seconds"],
            "estimated_duration_minutes": duration_minutes,
            "weight_recommendation": weight_info,
            "calories_kcal": calories,
        })

    session_calories = calculate_session_calories(exercise_calories)
    weekly_calories = calculate_weekly_calories(session_calories, sport["sessions_per_week"])

    return {
        "sport": {
            "id": sport["id"],
            "name_ja": sport["name_ja"],
            "primary_muscles": sport["primary_muscles"],
            "training_purpose": training_purpose,
            "sessions_per_week": sport["sessions_per_week"],
            "minutes_per_session": sport["minutes_per_session"],
        },
        "exercises": exercise_entries,
        "session_calories_kcal": session_calories,
        "weekly_calories_kcal": weekly_calories,
    }


def find_alternative_exercises(exercise_id: str, limit: int = 2) -> list[dict]:
    """指定した種目と同じ主動筋（muscle_svg_idsの先頭）を持つ代替種目を探す。

    引数:
        exercise_id: 起点となる種目ID
        limit: 返す代替種目の最大件数
    戻り値:
        エクササイズマスタ形式の辞書のリスト（自分自身は除外）。
        主動筋が定義されていない種目の場合は空リストを返す。
    """
    exercises = load_exercises_master()
    target = _find_exercise(exercises, exercise_id)
    target_muscle_ids = target["muscle_svg_ids"]
    if not target_muscle_ids:
        return []

    primary_muscle_id = target_muscle_ids[0]
    alternatives = [
        exercise
        for exercise in exercises
        if exercise["id"] != exercise_id and exercise["muscle_svg_ids"][:1] == [primary_muscle_id]
    ]
    return alternatives[:limit]
