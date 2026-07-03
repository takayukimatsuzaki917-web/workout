import pytest

from logic.program_builder import build_program, find_alternative_exercises, load_sports_master

PROFILE = {
    "gender": "男性",
    "age": 25,
    "bodyweight_kg": 70,
    "height_cm": 170,
    "level": "中級者",
}

ALL_SPORT_IDS = [sport["id"] for sport in load_sports_master()]


@pytest.mark.parametrize("sport_id", ALL_SPORT_IDS)
def test_build_program_returns_valid_structure_for_every_sport(sport_id):
    program = build_program(PROFILE, sport_id)

    assert program["sport"]["id"] == sport_id
    assert program["exercises"], "種目リストが空であってはならない"
    assert 5 <= len(program["exercises"]) <= 8

    for exercise in program["exercises"]:
        assert exercise["name_ja"]
        assert exercise["equipment"]
        assert exercise["description"]
        assert exercise["target_muscles"]
        assert exercise["muscle_svg_ids"]
        assert exercise["calories_kcal"] > 0
        assert "has_weight_target" in exercise["weight_recommendation"]

    assert program["session_calories_kcal"] > 0
    assert program["weekly_calories_kcal"] == pytest.approx(
        program["session_calories_kcal"] * program["sport"]["sessions_per_week"]
    )


def test_build_program_raises_for_unknown_sport_id():
    with pytest.raises(ValueError):
        build_program(PROFILE, "unknown_sport")


def test_build_program_bodyweight_only_exercise_has_no_weight_target():
    program = build_program(PROFILE, "marathon")
    plank = next(e for e in program["exercises"] if e["id"] == "plank")
    assert plank["weight_recommendation"]["has_weight_target"] is False


def test_find_alternative_exercises_shares_primary_muscle():
    alternatives = find_alternative_exercises("squat_barbell", limit=2)
    assert len(alternatives) == 2
    for exercise in alternatives:
        assert exercise["id"] != "squat_barbell"
        assert exercise["muscle_svg_ids"][0] == "quadriceps"


def test_find_alternative_exercises_respects_limit():
    alternatives = find_alternative_exercises("squat_barbell", limit=1)
    assert len(alternatives) == 1


def test_find_alternative_exercises_empty_when_no_other_exercise_shares_primary_muscle():
    # incline_bench_press の主動筋(chest_upper)を持つ種目は他に存在しない
    assert find_alternative_exercises("incline_bench_press", limit=5) == []
