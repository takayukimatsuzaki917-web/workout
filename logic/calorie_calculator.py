"""消費カロリー算出ロジック（MET法）。

MET値 × 体重(kg) × 実施時間(h) の計算式に基づく純粋関数群。
"""

from __future__ import annotations


def calculate_exercise_calories(exercise: dict, bodyweight_kg: float, duration_minutes: float) -> float:
    """1種目分の消費カロリー(kcal)を算出する。

    引数:
        exercise: エクササイズマスタの1件分の辞書（met_valueを含む）
        bodyweight_kg: ユーザーの体重(kg)
        duration_minutes: 実施時間(分)
    戻り値:
        消費カロリー(kcal)
    """
    met_value = exercise["met_value"]
    duration_hours = duration_minutes / 60
    return round(met_value * bodyweight_kg * duration_hours, 1)


def calculate_session_calories(exercise_calories: list[float]) -> float:
    """1回のトレーニングセッション全体の消費カロリー合計(kcal)を算出する。"""
    return round(sum(exercise_calories), 1)


def calculate_weekly_calories(session_calories: float, sessions_per_week: int) -> float:
    """週あたりの想定消費カロリー(kcal)を算出する。"""
    return round(session_calories * sessions_per_week, 1)
