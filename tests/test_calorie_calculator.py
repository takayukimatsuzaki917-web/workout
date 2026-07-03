from logic.calorie_calculator import (
    calculate_exercise_calories,
    calculate_session_calories,
    calculate_weekly_calories,
)

EXERCISE = {"id": "dummy", "met_value": 6.0}


def test_calculate_exercise_calories():
    # MET6.0 × 体重70kg × 時間(10分/60) = 70.0kcal
    assert calculate_exercise_calories(EXERCISE, bodyweight_kg=70, duration_minutes=10) == 70.0


def test_calculate_session_calories_sums_list():
    assert calculate_session_calories([70.0, 30.5, 10.0]) == 110.5


def test_calculate_session_calories_empty_list():
    assert calculate_session_calories([]) == 0.0


def test_calculate_weekly_calories():
    assert calculate_weekly_calories(session_calories=300.0, sessions_per_week=3) == 900.0
