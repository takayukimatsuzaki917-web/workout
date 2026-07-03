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
BODY_FILL = "#dfe4ea"          # 体のシルエット（対象外の部位）
BODY_STROKE = "#b6c0cc"        # シルエットの輪郭
HIGHLIGHT_STROKE = "#ffffff"   # ハイライト筋肉の縁取り（体から浮き立たせる）

# 体のシルエット（頭〜足先の連続した人体形状）。
# ハイライト対象の筋肉ブロックはこの上に色付きで重ねる。
# 前面・背面で体の外形は共通なので同じ定義を使う。
_SILHOUETTE_SHAPES = [
    {"shape": "circle", "cx": 100, "cy": 28, "r": 17},                          # 頭
    {"shape": "rect", "x": 92, "y": 42, "width": 16, "height": 12, "rx": 4},    # 首
    {"shape": "ellipse", "cx": 62, "cy": 60, "rx": 20, "ry": 13},               # 左肩
    {"shape": "ellipse", "cx": 138, "cy": 60, "rx": 20, "ry": 13},              # 右肩
    {"shape": "rect", "x": 64, "y": 54, "width": 72, "height": 104, "rx": 22},  # 胴体
    {"shape": "rect", "x": 38, "y": 62, "width": 20, "height": 64, "rx": 10},   # 左上腕
    {"shape": "rect", "x": 142, "y": 62, "width": 20, "height": 64, "rx": 10},  # 右上腕
    {"shape": "rect", "x": 30, "y": 122, "width": 16, "height": 58, "rx": 8},   # 左前腕
    {"shape": "rect", "x": 154, "y": 122, "width": 16, "height": 58, "rx": 8},  # 右前腕
    {"shape": "circle", "cx": 38, "cy": 184, "r": 8},                           # 左手
    {"shape": "circle", "cx": 162, "cy": 184, "r": 8},                          # 右手
    {"shape": "rect", "x": 68, "y": 150, "width": 64, "height": 30, "rx": 14},  # 骨盤
    {"shape": "rect", "x": 66, "y": 174, "width": 28, "height": 76, "rx": 13},  # 左太もも
    {"shape": "rect", "x": 106, "y": 174, "width": 28, "height": 76, "rx": 13}, # 右太もも
    {"shape": "rect", "x": 68, "y": 246, "width": 24, "height": 60, "rx": 11},  # 左すね
    {"shape": "rect", "x": 108, "y": 246, "width": 24, "height": 60, "rx": 11}, # 右すね
    {"shape": "ellipse", "cx": 80, "cy": 310, "rx": 15, "ry": 7},               # 左足
    {"shape": "ellipse", "cx": 120, "cy": 310, "rx": 15, "ry": 7},             # 右足
]

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


def _shape_to_svg(shape: dict, fill: str, stroke: str = "none", stroke_width: float = 0) -> str:
    """図形定義1件をSVGタグ文字列に変換する。"""
    common = f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"'
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
        muscle_shapes, label = FRONT_MUSCLE_SHAPES, "前面"
    elif view == "back":
        muscle_shapes, label = BACK_MUSCLE_SHAPES, "背面"
    else:
        raise ValueError(f"未知のviewです: {view}")

    color_by_level = {"primary": PRIMARY_COLOR, "secondary": SECONDARY_COLOR}

    svg_parts = [
        f'<svg viewBox="0 0 {VIEW_WIDTH} {VIEW_HEIGHT}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{label}の筋肉ハイライト図" style="width:100%;height:auto;">'
    ]

    # まず体のシルエット（対象外の部位を含む人体の外形）を敷く
    for shape in _SILHOUETTE_SHAPES:
        svg_parts.append(_shape_to_svg(shape, BODY_FILL, stroke=BODY_STROKE, stroke_width=1.5))

    # その上に、ハイライト対象の筋肉だけを色付きで重ねる（白縁取りで体から浮き立たせる）
    for muscle_id, shapes in muscle_shapes.items():
        level = highlight_map.get(muscle_id)
        if level not in color_by_level:
            continue
        for shape in shapes:
            svg_parts.append(_shape_to_svg(shape, color_by_level[level], stroke=HIGHLIGHT_STROKE, stroke_width=1.2))

    svg_parts.append("</svg>")

    return "".join(svg_parts)
