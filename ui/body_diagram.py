"""筋肉ハイライトSVGボディ図の生成。

前面・背面それぞれについて、体の部位を単純な矩形/楕円で表した
簡易シルエットを定義し、`highlight_map`（muscle_svg_id -> "primary"|"secondary"）
に応じて色分けしたSVGを組み立てる。解剖学的な精密さより、
どの部位が対象かが一目で分かることを優先したプロトタイプ品質の図。
"""

from __future__ import annotations

VIEW_WIDTH = 200
VIEW_HEIGHT = 320

PRIMARY_COLOR = "#e63946"
SECONDARY_COLOR = "#f4a261"
UNHIGHLIGHTED_COLOR = "#d9dde1"
DECORATION_COLOR = "#cfd8dc"
STROKE_COLOR = "#6b7280"

# 装飾用の図形（頭・首・足先）。ハイライト対象外で常に同じ色。
_FRONT_DECORATION_SHAPES = [
    {"shape": "circle", "cx": 100, "cy": 25, "r": 16},
    {"shape": "rect", "x": 94, "y": 39, "width": 12, "height": 8, "rx": 2},
    {"shape": "ellipse", "cx": 81, "cy": 308, "rx": 14, "ry": 7},
    {"shape": "ellipse", "cx": 119, "cy": 308, "rx": 14, "ry": 7},
]
_BACK_DECORATION_SHAPES = _FRONT_DECORATION_SHAPES

# 前面から見える部位の座標定義。左右対称の部位は図形を複数持つ。
FRONT_MUSCLE_SHAPES: dict[str, list[dict]] = {
    "shoulders": [
        {"shape": "ellipse", "cx": 62, "cy": 58, "rx": 16, "ry": 11},
        {"shape": "ellipse", "cx": 138, "cy": 58, "rx": 16, "ry": 11},
    ],
    "chest_upper": [
        {"shape": "rect", "x": 72, "y": 55, "width": 56, "height": 18, "rx": 6},
    ],
    "chest": [
        {"shape": "rect", "x": 68, "y": 74, "width": 64, "height": 30, "rx": 10},
    ],
    "biceps": [
        {"shape": "rect", "x": 40, "y": 70, "width": 16, "height": 45, "rx": 8},
        {"shape": "rect", "x": 144, "y": 70, "width": 16, "height": 45, "rx": 8},
    ],
    "forearms": [
        {"shape": "rect", "x": 32, "y": 118, "width": 14, "height": 50, "rx": 7},
        {"shape": "rect", "x": 154, "y": 118, "width": 14, "height": 50, "rx": 7},
    ],
    "finger_flexors": [
        {"shape": "circle", "cx": 39, "cy": 176, "r": 9},
        {"shape": "circle", "cx": 161, "cy": 176, "r": 9},
    ],
    "core": [
        {"shape": "rect", "x": 76, "y": 106, "width": 48, "height": 42, "rx": 10},
    ],
    "obliques": [
        {"shape": "rect", "x": 64, "y": 106, "width": 14, "height": 42, "rx": 6},
        {"shape": "rect", "x": 122, "y": 106, "width": 14, "height": 42, "rx": 6},
    ],
    "hip_flexors": [
        {"shape": "rect", "x": 70, "y": 150, "width": 60, "height": 20, "rx": 8},
    ],
    "quadriceps": [
        {"shape": "rect", "x": 68, "y": 172, "width": 26, "height": 70, "rx": 10},
        {"shape": "rect", "x": 106, "y": 172, "width": 26, "height": 70, "rx": 10},
    ],
    "calves": [
        {"shape": "rect", "x": 70, "y": 245, "width": 22, "height": 55, "rx": 10},
        {"shape": "rect", "x": 108, "y": 245, "width": 22, "height": 55, "rx": 10},
    ],
}

# 背面から見える部位の座標定義。
BACK_MUSCLE_SHAPES: dict[str, list[dict]] = {
    "trapezius": [
        {"shape": "rect", "x": 76, "y": 50, "width": 48, "height": 24, "rx": 8},
    ],
    "rear_delts": [
        {"shape": "ellipse", "cx": 62, "cy": 58, "rx": 16, "ry": 11},
        {"shape": "ellipse", "cx": 138, "cy": 58, "rx": 16, "ry": 11},
    ],
    "rotator_cuff": [
        {"shape": "circle", "cx": 78, "cy": 70, "r": 7},
        {"shape": "circle", "cx": 122, "cy": 70, "r": 7},
    ],
    "erector_spinae": [
        {"shape": "rect", "x": 92, "y": 78, "width": 16, "height": 70, "rx": 8},
    ],
    "lats": [
        {"shape": "rect", "x": 64, "y": 78, "width": 28, "height": 48, "rx": 10},
        {"shape": "rect", "x": 108, "y": 78, "width": 28, "height": 48, "rx": 10},
    ],
    "triceps": [
        {"shape": "rect", "x": 40, "y": 70, "width": 16, "height": 45, "rx": 8},
        {"shape": "rect", "x": 144, "y": 70, "width": 16, "height": 45, "rx": 8},
    ],
    "forearms": [
        {"shape": "rect", "x": 32, "y": 118, "width": 14, "height": 50, "rx": 7},
        {"shape": "rect", "x": 154, "y": 118, "width": 14, "height": 50, "rx": 7},
    ],
    "glutes": [
        {"shape": "ellipse", "cx": 84, "cy": 160, "rx": 18, "ry": 16},
        {"shape": "ellipse", "cx": 116, "cy": 160, "rx": 18, "ry": 16},
    ],
    "hamstrings": [
        {"shape": "rect", "x": 68, "y": 180, "width": 26, "height": 62, "rx": 10},
        {"shape": "rect", "x": 106, "y": 180, "width": 26, "height": 62, "rx": 10},
    ],
    "calves": [
        {"shape": "rect", "x": 70, "y": 245, "width": 22, "height": 55, "rx": 10},
        {"shape": "rect", "x": 108, "y": 245, "width": 22, "height": 55, "rx": 10},
    ],
}


def _shape_to_svg(shape: dict, fill: str) -> str:
    """図形定義1件をSVGタグ文字列に変換する。"""
    common = f'fill="{fill}" stroke="{STROKE_COLOR}" stroke-width="1.5"'
    if shape["shape"] == "rect":
        rx = shape.get("rx", 4)
        return (
            f'<rect x="{shape["x"]}" y="{shape["y"]}" width="{shape["width"]}" '
            f'height="{shape["height"]}" rx="{rx}" {common} />'
        )
    if shape["shape"] == "ellipse":
        return f'<ellipse cx="{shape["cx"]}" cy="{shape["cy"]}" rx="{shape["rx"]}" ry="{shape["ry"]}" {common} />'
    if shape["shape"] == "circle":
        return f'<circle cx="{shape["cx"]}" cy="{shape["cy"]}" r="{shape["r"]}" {common} />'
    raise ValueError(f"未対応の図形タイプです: {shape['shape']}")


def render_body_diagram_svg(highlight_map: dict[str, str], view: str) -> str:
    """筋肉ハイライトマップから前面/背面のSVGボディ図を組み立てる。

    引数:
        highlight_map: {muscle_svg_id: "primary" | "secondary"} の辞書
        view: "front"（前面） または "back"（背面）
    戻り値:
        SVGマークアップ文字列（st.markdownでunsafe_allow_html=Trueとともに描画する想定）
    """
    if view == "front":
        muscle_shapes, decoration_shapes, label = FRONT_MUSCLE_SHAPES, _FRONT_DECORATION_SHAPES, "前面"
    elif view == "back":
        muscle_shapes, decoration_shapes, label = BACK_MUSCLE_SHAPES, _BACK_DECORATION_SHAPES, "背面"
    else:
        raise ValueError(f"未知のviewです: {view}")

    color_by_level = {"primary": PRIMARY_COLOR, "secondary": SECONDARY_COLOR}

    svg_parts = [
        f'<svg viewBox="0 0 {VIEW_WIDTH} {VIEW_HEIGHT}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{label}の筋肉ハイライト図" style="width:100%;height:auto;">'
    ]
    for shape in decoration_shapes:
        svg_parts.append(_shape_to_svg(shape, DECORATION_COLOR))
    for muscle_id, shapes in muscle_shapes.items():
        fill = color_by_level.get(highlight_map.get(muscle_id), UNHIGHLIGHTED_COLOR)
        for shape in shapes:
            svg_parts.append(_shape_to_svg(shape, fill))
    svg_parts.append("</svg>")

    return "".join(svg_parts)
