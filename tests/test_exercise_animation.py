import xml.etree.ElementTree as ET

from logic.program_builder import load_exercises_master
from ui.exercise_animation import (
    MOVEMENT_PATTERN_IDS,
    get_movement_label,
    render_exercise_animation,
)


def test_every_exercise_movement_pattern_has_animation():
    """全種目の movement_pattern が、アニメーションモジュールで定義済みであること。"""
    exercises = load_exercises_master()
    for exercise in exercises:
        assert exercise["movement_pattern"] in MOVEMENT_PATTERN_IDS, (
            f"{exercise['id']} の動作パターン {exercise['movement_pattern']} が未定義"
        )


def test_all_patterns_render_wellformed_svg():
    """全パターンが整形式のSVGを生成すること（SMILアニメーション含む）。"""
    for pattern_id in MOVEMENT_PATTERN_IDS:
        svg = render_exercise_animation(pattern_id)
        # 例外なくパースできれば整形式XML
        ET.fromstring(svg)
        assert svg.startswith("<svg")
        assert "<animate" in svg  # 何らかのアニメーションが含まれる


def test_unknown_pattern_falls_back_to_generic():
    """未知のパターンIDでもエラーにならず汎用アニメーションにフォールバックすること。"""
    svg = render_exercise_animation("does_not_exist")
    ET.fromstring(svg)
    assert get_movement_label("does_not_exist") == get_movement_label("generic")
