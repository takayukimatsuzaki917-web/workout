"""適正重量（推定1RM・目安重量）算出ロジック。

体重・経験レベル・種目ごとの体重比係数から推定1RM（最大挙上重量）を求め、
トレーニング目的（筋力向上／筋肥大／筋持久力）に応じた%1RMを掛けて
目安重量を算出する。すべて外部状態に依存しない純粋関数として実装する。
"""

from __future__ import annotations

# トレーニング目的ごとの %1RM レンジと推奨回数レンジ。
# 筋力向上は高強度・低回数、筋持久力は低強度・高回数という一般的なセオリーに基づく。
TRAINING_PURPOSE_TABLE = {
    "筋力": {"percent_1rm_range": (85, 95), "reps_range": "3-5回"},
    "筋肥大": {"percent_1rm_range": (67, 85), "reps_range": "8-12回"},
    "筋持久力": {"percent_1rm_range": (50, 67), "reps_range": "15回以上"},
}


def estimate_one_rm(exercise: dict, bodyweight_kg: float, level: str) -> float | None:
    """体重比係数テーブルから推定1RM(kg)を算出する。

    引数:
        exercise: エクササイズマスタの1件分の辞書
        bodyweight_kg: ユーザーの体重(kg)
        level: 筋トレ経験レベル（"初心者" / "中級者" / "上級者"）
    戻り値:
        推定1RM(kg)。体重比係数が定義されていない種目（自重種目など）は None。
    """
    coefficients = exercise.get("bodyweight_coefficient")
    if not coefficients or level not in coefficients:
        return None

    coeff_min, coeff_max = coefficients[level]
    coeff_mid = (coeff_min + coeff_max) / 2
    return round(bodyweight_kg * coeff_mid, 1)


def recommend_weight(
    exercise: dict,
    bodyweight_kg: float,
    level: str,
    training_purpose: str,
) -> dict:
    """種目・体重・レベル・トレーニング目的から目安重量を算出する。

    引数:
        exercise: エクササイズマスタの1件分の辞書
        bodyweight_kg: ユーザーの体重(kg)
        level: 筋トレ経験レベル（"初心者" / "中級者" / "上級者"）
        training_purpose: トレーニング目的（"筋力" / "筋肥大" / "筋持久力"）
    戻り値:
        has_weight_target: 重量目安を算出できたかどうか
        weight_kg: 目安重量(kg)。算出不可の場合はNone
        bodyweight_ratio: 体重に対する倍率。算出不可の場合はNone
        percent_1rm: 使用した%1RM（目的別レンジの中央値）
        reps_range: 目的に応じた回数レンジ
        display_text: 画面表示用の文言
    """
    if training_purpose not in TRAINING_PURPOSE_TABLE:
        raise ValueError(f"未知のtraining_purposeです: {training_purpose}")

    purpose_setting = TRAINING_PURPOSE_TABLE[training_purpose]
    percent_min, percent_max = purpose_setting["percent_1rm_range"]
    percent_1rm = (percent_min + percent_max) / 2

    one_rm = estimate_one_rm(exercise, bodyweight_kg, level)

    if one_rm is None:
        return {
            "has_weight_target": False,
            "weight_kg": None,
            "bodyweight_ratio": None,
            "percent_1rm": percent_1rm,
            "reps_range": purpose_setting["reps_range"],
            "display_text": "自重・可変重量種目のため重量目安は算出していません",
        }

    weight_kg = round(one_rm * percent_1rm / 100, 1)
    bodyweight_ratio = round(weight_kg / bodyweight_kg, 2) if bodyweight_kg else None

    return {
        "has_weight_target": True,
        "weight_kg": weight_kg,
        "bodyweight_ratio": bodyweight_ratio,
        "percent_1rm": percent_1rm,
        "reps_range": purpose_setting["reps_range"],
        "display_text": f"目安重量：{weight_kg}kg（体重の{bodyweight_ratio}倍）※あくまで目安です",
    }
