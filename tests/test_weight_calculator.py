from logic.weight_calculator import estimate_one_rm, recommend_weight

WEIGHTED_EXERCISE = {
    "id": "dummy_squat",
    "bodyweight_coefficient": {
        "初心者": [0.5, 0.75],
        "中級者": [0.75, 1.0],
        "上級者": [1.0, 1.5],
    },
}

BODYWEIGHT_EXERCISE = {"id": "dummy_pushup"}


def test_estimate_one_rm_uses_midpoint_of_coefficient_range():
    # 中級者の係数レンジ[0.75, 1.0]の中央値0.875 × 体重80kg = 70.0kg
    assert estimate_one_rm(WEIGHTED_EXERCISE, bodyweight_kg=80, level="中級者") == 70.0


def test_estimate_one_rm_returns_none_when_no_coefficient_defined():
    assert estimate_one_rm(BODYWEIGHT_EXERCISE, bodyweight_kg=80, level="中級者") is None


def test_estimate_one_rm_returns_none_for_unknown_level():
    assert estimate_one_rm(WEIGHTED_EXERCISE, bodyweight_kg=80, level="超上級者") is None


def test_recommend_weight_for_strength_purpose():
    result = recommend_weight(WEIGHTED_EXERCISE, bodyweight_kg=80, level="中級者", training_purpose="筋力")
    # 推定1RM=70.0kg, 筋力の%1RM中央値=90% -> 70.0 * 0.9 = 63.0kg
    assert result["has_weight_target"] is True
    assert result["weight_kg"] == 63.0
    assert result["bodyweight_ratio"] == 0.79
    assert result["reps_range"] == "3-5回"


def test_recommend_weight_for_bodyweight_exercise_has_no_target():
    result = recommend_weight(BODYWEIGHT_EXERCISE, bodyweight_kg=80, level="中級者", training_purpose="筋肥大")
    assert result["has_weight_target"] is False
    assert result["weight_kg"] is None
    assert "重量目安は算出していません" in result["display_text"]


def test_recommend_weight_rejects_unknown_training_purpose():
    try:
        recommend_weight(WEIGHTED_EXERCISE, bodyweight_kg=80, level="中級者", training_purpose="謎の目的")
        assert False, "ValueErrorが発生するはず"
    except ValueError:
        pass
