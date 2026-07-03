from logic.muscle_coverage import aggregate_program_coverage, classify_exercise_muscles

SQUAT_ENTRY = {
    "id": "squat_barbell",
    "muscle_svg_ids": ["quadriceps", "glutes", "hamstrings", "core"],
}

HIP_THRUST_ENTRY = {
    "id": "hip_thrust",
    "muscle_svg_ids": ["glutes", "hamstrings", "core"],
}


def test_classify_exercise_muscles_marks_first_as_primary():
    result = classify_exercise_muscles(SQUAT_ENTRY)
    assert result["quadriceps"] == "primary"
    assert result["glutes"] == "secondary"
    assert result["hamstrings"] == "secondary"
    assert result["core"] == "secondary"


def test_classify_exercise_muscles_handles_empty_list():
    assert classify_exercise_muscles({"muscle_svg_ids": []}) == {}


def test_aggregate_program_coverage_merges_across_exercises():
    coverage = aggregate_program_coverage([SQUAT_ENTRY, HIP_THRUST_ENTRY])
    # quadriceps: squatでのみ主動筋
    assert coverage["quadriceps"] == "primary"
    # glutes: squatでは協働筋だが、hip_thrustでは主動筋 -> primaryが優先される
    assert coverage["glutes"] == "primary"
    # hamstrings: 両種目とも協働筋
    assert coverage["hamstrings"] == "secondary"
    # core: 両種目とも協働筋
    assert coverage["core"] == "secondary"


def test_aggregate_program_coverage_empty_list():
    assert aggregate_program_coverage([]) == {}
