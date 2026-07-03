"""種目の「やり方」を動きで見せるアニメーション動作デモ。

38種目を1つずつ作画するのは非現実的なため、種目を「動作パターン」
（スクワット系・ヒンジ系・プッシュ系・プル系・体幹系・回旋系・有酸素系など）
に分類し、パターンごとに共通のスティックフィギュア・アニメーションを用意する。

各パターンは「開始ポーズ(a)」と「終了ポーズ(b)」の2つの姿勢を持ち、
SVGのSMILアニメーション（<animate> / <animateTransform>）で滑らかに往復させる。
CSSやJavaScriptに依存しないため、st.markdown(unsafe_allow_html=True) で確実に動く。

ポーズは横向きのスティックフィギュアで表現する。
各ポーズは以下のキーを持つ辞書:
    head : 頭の中心座標 (x, y)
    spine: 背骨（首→腰）の2点 [(x, y), (x, y)]
    arm  : 手前側の腕 [肩, 肘, 手]（省略可）
    leg  : 手前側の脚 [腰, 膝, 足首, つま先]（省略可）
    arm2 : 奥側の腕（左右で動きが違う種目用・省略可）
    leg2 : 奥側の脚（同上・省略可）
"""

from __future__ import annotations

# SVGの表示領域（縦長）。全ポーズの座標はこの座標系で定義する。
VIEW_WIDTH = 120
VIEW_HEIGHT = 170
GROUND_Y = 156

# 配色（親しみやすいキャラクター風・オリジナルデザイン）
SKIN = "#f7c49a"             # 手前側の肌
SKIN_FAR = "#e6b083"         # 奥側の肌（少し濃くして奥行きを表現）
HAIR = "#5a3825"             # 髪
SHIRT = "#ef6f6c"            # シャツ（胴体・袖）
SHORTS = "#3f6d9e"           # ショートパンツ
SHOE = "#f4a259"             # 靴（手前）
SHOE_FAR = "#dc9350"         # 靴（奥）
FACE = "#4a3b32"             # 目・口
PROP_BAR_COLOR = "#495057"   # バーベルの棒
PROP_PLATE_COLOR = "#e63946" # プレート（重り）
GROUND_COLOR = "#ced4da"

# 体パーツの太さ・大きさ
LIMB_WIDTH = 8       # 手前の手足
FAR_LIMB_WIDTH = 7   # 奥の手足
TORSO_WIDTH = 16     # 胴体（シャツ）
HEAD_R = 11          # 頭の半径
SHOE_RX = 6          # 靴の横幅

# アニメーションのイージング（滑らかな加減速）
_EASE = "0.42 0 0.58 1"

# 各パターンの姿勢定義。座標は上記VIEW_WIDTH×VIEW_HEIGHT基準。
MOVEMENT_PATTERNS: dict[str, dict] = {
    "squat": {
        "label": "しゃがんで立ち上がる動作",
        "dur": 2.4, "mid": 0.5, "prop": "bar",
        "a": {"head": (60, 22), "spine": [(60, 32), (60, 90)],
              "arm": [(60, 40), (74, 50), (88, 50)],
              "leg": [(60, 90), (58, 120), (57, 152), (72, 154)]},
        "b": {"head": (58, 44), "spine": [(58, 54), (66, 102)],
              "arm": [(60, 60), (80, 60), (92, 58)],
              "leg": [(66, 102), (92, 118), (57, 152), (72, 154)]},
    },
    "hinge": {
        "label": "股関節を曲げて引き上げる動作",
        "dur": 2.2, "mid": 0.5, "prop": "bar",
        "a": {"head": (40, 58), "spine": [(46, 62), (72, 92)],
              "arm": [(52, 66), (52, 90), (52, 116)],
              "leg": [(72, 92), (66, 122), (62, 152), (74, 154)]},
        "b": {"head": (60, 22), "spine": [(60, 32), (60, 90)],
              "arm": [(60, 40), (60, 64), (60, 90)],
              "leg": [(60, 90), (58, 120), (57, 152), (72, 154)]},
    },
    "lunge": {
        "label": "片脚を前に踏み込む動作",
        "dur": 2.4, "mid": 0.5, "prop": None,
        "a": {"head": (60, 22), "spine": [(60, 32), (60, 90)],
              "arm": [(60, 40), (62, 64), (64, 86)],
              "leg": [(60, 90), (60, 120), (60, 152), (72, 154)],
              "leg2": [(60, 90), (56, 120), (54, 152), (46, 154)]},
        "b": {"head": (60, 30), "spine": [(60, 40), (60, 96)],
              "arm": [(60, 48), (60, 72), (60, 92)],
              "leg": [(60, 96), (84, 120), (84, 152), (96, 154)],
              "leg2": [(60, 96), (48, 126), (34, 150), (28, 150)]},
    },
    "horizontal_push": {
        "label": "前方に押し出す動作",
        "dur": 1.8, "mid": 0.5, "prop": "bar",
        "a": {"head": (52, 22), "spine": [(52, 32), (52, 92)],
              "arm": [(52, 44), (42, 54), (58, 56)],
              "leg": [(52, 92), (50, 120), (49, 152), (64, 154)]},
        "b": {"head": (52, 22), "spine": [(52, 32), (52, 92)],
              "arm": [(52, 44), (72, 50), (92, 52)],
              "leg": [(52, 92), (50, 120), (49, 152), (64, 154)]},
    },
    "vertical_push": {
        "label": "頭上に押し上げる動作",
        "dur": 2.0, "mid": 0.5, "prop": "bar",
        "a": {"head": (60, 24), "spine": [(60, 34), (60, 92)],
              "arm": [(60, 40), (44, 46), (54, 32)],
              "leg": [(60, 92), (58, 120), (57, 152), (72, 154)]},
        "b": {"head": (60, 24), "spine": [(60, 34), (60, 92)],
              "arm": [(60, 40), (58, 18), (60, 4)],
              "leg": [(60, 92), (58, 120), (57, 152), (72, 154)]},
    },
    "vertical_pull": {
        "label": "体を上へ引き上げる動作",
        "dur": 2.2, "mid": 0.5, "prop": "fixed_bar",
        "a": {"head": (60, 40), "spine": [(60, 50), (60, 104)],
              "arm": [(60, 50), (58, 26), (58, 8)],
              "leg": [(60, 104), (59, 128), (58, 150), (72, 152)]},
        "b": {"head": (60, 26), "spine": [(60, 36), (60, 90)],
              "arm": [(60, 36), (48, 22), (58, 8)],
              "leg": [(60, 90), (62, 116), (62, 140), (76, 142)]},
    },
    "horizontal_pull": {
        "label": "手前に引き寄せる動作",
        "dur": 1.9, "mid": 0.5, "prop": "bar",
        "a": {"head": (54, 24), "spine": [(54, 34), (58, 92)],
              "arm": [(56, 44), (74, 50), (92, 54)],
              "leg": [(58, 92), (56, 120), (55, 152), (70, 154)]},
        "b": {"head": (54, 24), "spine": [(54, 34), (58, 92)],
              "arm": [(56, 44), (44, 50), (32, 56)],
              "leg": [(58, 92), (56, 120), (55, 152), (70, 154)]},
    },
    "core_hold": {
        "label": "体幹を一直線に保つ動作",
        "dur": 2.6, "mid": 0.5, "prop": None,
        "a": {"head": (30, 100), "spine": [(38, 102), (98, 116)],
              "arm": [(40, 102), (42, 120), (44, 138)],
              "leg": [(98, 116), (110, 128), (118, 138), (124, 138)]},
        "b": {"head": (30, 96), "spine": [(38, 98), (98, 110)],
              "arm": [(40, 98), (42, 120), (44, 138)],
              "leg": [(98, 110), (110, 126), (118, 138), (124, 138)]},
    },
    "core_rotation": {
        "label": "体をひねる（回旋）動作",
        "dur": 1.6, "mid": 0.5, "prop": "ball",
        "a": {"head": (58, 30), "spine": [(58, 40), (60, 94)],
              "arm": [(58, 52), (44, 58), (32, 66)],
              "leg": [(60, 94), (82, 102), (104, 106), (112, 104)]},
        "b": {"head": (62, 30), "spine": [(62, 40), (60, 94)],
              "arm": [(58, 52), (76, 58), (90, 66)],
              "leg": [(60, 94), (82, 102), (104, 106), (112, 104)]},
    },
    "carry": {
        "label": "重りを保持する動作",
        "dur": 1.4, "mid": 0.5, "prop": "dumbbell",
        "a": {"head": (60, 22), "spine": [(60, 32), (60, 90)],
              "arm": [(60, 40), (63, 64), (66, 90)],
              "leg": [(60, 90), (58, 120), (57, 152), (72, 154)]},
        "b": {"head": (60, 25), "spine": [(60, 35), (60, 93)],
              "arm": [(60, 43), (63, 67), (66, 93)],
              "leg": [(60, 93), (58, 122), (57, 152), (72, 154)]},
    },
    "calf_raise": {
        "label": "かかとを上げ下げする動作",
        "dur": 1.4, "mid": 0.5, "prop": None,
        "a": {"head": (60, 30), "spine": [(60, 40), (60, 98)],
              "arm": [(60, 48), (62, 72), (64, 96)],
              "leg": [(60, 98), (58, 126), (57, 152), (72, 154)]},
        "b": {"head": (60, 22), "spine": [(60, 32), (60, 90)],
              "arm": [(60, 40), (62, 64), (64, 88)],
              "leg": [(60, 90), (58, 120), (58, 146), (72, 150)]},
    },
    "power": {
        "label": "全身で爆発的に伸び上がる動作",
        "dur": 1.5, "mid": 0.4, "prop": "bar",
        "a": {"head": (54, 46), "spine": [(54, 56), (66, 100)],
              "arm": [(56, 62), (56, 86), (56, 110)],
              "leg": [(66, 100), (88, 116), (57, 150), (72, 152)]},
        "b": {"head": (60, 16), "spine": [(60, 26), (60, 84)],
              "arm": [(60, 34), (60, 16), (60, 2)],
              "leg": [(60, 84), (59, 112), (58, 146), (72, 150)]},
    },
    "cardio_cycle": {
        "label": "ペダルをこぐ動作",
        "dur": 1.2, "mid": 0.5, "prop": None,
        "a": {"head": (50, 30), "spine": [(50, 40), (56, 92)],
              "arm": [(52, 48), (70, 54), (84, 58)],
              "leg": [(56, 92), (78, 102), (86, 120), (92, 120)],
              "leg2": [(56, 92), (48, 108), (42, 124), (36, 122)]},
        "b": {"head": (50, 30), "spine": [(50, 40), (56, 92)],
              "arm": [(52, 48), (70, 54), (84, 58)],
              "leg": [(56, 92), (48, 108), (42, 124), (36, 122)],
              "leg2": [(56, 92), (78, 102), (86, 120), (92, 120)]},
    },
    "cardio_row": {
        "label": "引いて漕ぐ（ローイング）動作",
        "dur": 2.0, "mid": 0.5, "prop": None,
        "a": {"head": (46, 44), "spine": [(48, 50), (56, 92)],
              "arm": [(50, 56), (70, 60), (88, 62)],
              "leg": [(56, 92), (76, 84), (82, 104), (94, 104)]},
        "b": {"head": (36, 40), "spine": [(40, 46), (58, 94)],
              "arm": [(46, 54), (34, 60), (24, 64)],
              "leg": [(58, 94), (86, 96), (106, 100), (116, 98)]},
    },
    "cardio_run": {
        "label": "走る（脚を交互に動かす）動作",
        "dur": 0.9, "mid": 0.5, "prop": None,
        "a": {"head": (58, 22), "spine": [(58, 32), (58, 86)],
              "arm": [(58, 40), (48, 52), (42, 62)],
              "arm2": [(58, 40), (70, 52), (78, 60)],
              "leg": [(58, 86), (74, 102), (80, 124), (90, 126)],
              "leg2": [(58, 86), (50, 110), (46, 138), (40, 140)]},
        "b": {"head": (58, 22), "spine": [(58, 32), (58, 86)],
              "arm": [(58, 40), (70, 52), (78, 60)],
              "arm2": [(58, 40), (48, 52), (42, 62)],
              "leg": [(58, 86), (50, 110), (46, 138), (40, 140)],
              "leg2": [(58, 86), (74, 102), (80, 124), (90, 126)]},
    },
    "generic": {
        "label": "動作イメージ",
        "dur": 1.6, "mid": 0.5, "prop": None,
        "a": {"head": (60, 22), "spine": [(60, 32), (60, 90)],
              "arm": [(60, 40), (60, 64), (60, 88)],
              "leg": [(60, 90), (58, 120), (57, 152), (72, 154)]},
        "b": {"head": (60, 22), "spine": [(60, 32), (60, 90)],
              "arm": [(60, 40), (48, 26), (44, 12)],
              "leg": [(60, 90), (66, 120), (70, 152), (84, 154)]},
    },
}

# テスト・検証で使う、利用可能なパターンID一覧
MOVEMENT_PATTERN_IDS = frozenset(MOVEMENT_PATTERNS)


def get_movement_label(pattern_id: str) -> str:
    """動作パターンの日本語ラベルを返す（未知のパターンは汎用ラベル）。"""
    return MOVEMENT_PATTERNS.get(pattern_id, MOVEMENT_PATTERNS["generic"])["label"]


def _points_str(points: list) -> str:
    """[(x, y), ...] を SVG polyline の points 属性文字列に変換する。"""
    return " ".join(f"{x},{y}" for x, y in points)


def _animated_polyline(part_a: list, part_b: list, dur: float, mid: float, color: str, width: int) -> str:
    """開始→終了→開始を往復するアニメーション付きpolylineを生成する。

    part_a / part_b: 同じ点数の座標リスト。片方しか無い場合は呼び出し側で揃える。
    """
    values = f"{_points_str(part_a)};{_points_str(part_b)};{_points_str(part_a)}"
    return (
        f'<polyline fill="none" stroke="{color}" stroke-width="{width}" '
        f'stroke-linecap="round" stroke-linejoin="round" points="{_points_str(part_a)}">'
        f'<animate attributeName="points" dur="{dur}s" repeatCount="indefinite" '
        f'calcMode="spline" keyTimes="0;{mid};1" keySplines="{_EASE};{_EASE}" values="{values}"/>'
        f'</polyline>'
    )


def _translated_group(inner: str, ax: float, ay: float, bx: float, by: float, dur: float, mid: float) -> str:
    """静的パーツ inner を (ax,ay)→(bx,by) へ、手足のpolylineと同じイージングで往復移動させる。

    肌の手足の端点（手・足）や頭に置くパーツ（靴・手・頭部）を、
    ポーズ間の端点の動きにぴったり追従させるために使う。
    """
    dx, dy = bx - ax, by - ay
    anim = (
        f'<animateTransform attributeName="transform" type="translate" dur="{dur}s" '
        f'repeatCount="indefinite" calcMode="spline" keyTimes="0;{mid};1" '
        f'keySplines="{_EASE};{_EASE}" values="0 0;{dx} {dy};0 0"/>'
    )
    return f'<g>{inner}{anim}</g>'


def _head_svg(cx: float, cy: float) -> str:
    """肌色の顔＋髪＋目＋口のキャラクター頭部を描く（静的パーツ）。"""
    r = HEAD_R
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{SKIN}"/>'
        # 頭頂を覆う髪（上半円を太いストロークで）
        f'<path d="M {cx - r} {cy - 1} A {r} {r} 0 0 1 {cx + r} {cy - 1}" '
        f'fill="none" stroke="{HAIR}" stroke-width="7" stroke-linecap="round"/>'
        # 目（正面向きで親しみやすく）
        f'<circle cx="{cx - 3.6}" cy="{cy + 1.5}" r="1.5" fill="{FACE}"/>'
        f'<circle cx="{cx + 3.6}" cy="{cy + 1.5}" r="1.5" fill="{FACE}"/>'
        # 口（にっこり）
        f'<path d="M {cx - 3} {cy + 5.5} Q {cx} {cy + 8} {cx + 3} {cy + 5.5}" '
        f'fill="none" stroke="{FACE}" stroke-width="1.2" stroke-linecap="round"/>'
    )


def _shoe_svg(cx: float, cy: float, color: str) -> str:
    """靴（楕円）を描く。"""
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{SHOE_RX}" ry="3.6" fill="{color}"/>'


def _hand_svg(cx: float, cy: float, color: str) -> str:
    """手（円）を描く。"""
    return f'<circle cx="{cx}" cy="{cy}" r="3.6" fill="{color}"/>'


def _shorts_svg(cx: float, cy: float) -> str:
    """ショートパンツ（腰まわり）を描く。"""
    return f'<rect x="{cx - 10}" y="{cy - 2}" width="20" height="13" rx="6" fill="{SHORTS}"/>'


def _sleeve_svg(cx: float, cy: float) -> str:
    """袖（肩のシャツ）を描く。"""
    return f'<circle cx="{cx}" cy="{cy}" r="6" fill="{SHIRT}"/>'


def _prop_svg(kind: str, hand_a: tuple, hand_b: tuple, dur: float, mid: float) -> str:
    """器具（バーベル・ダンベル・ボール・懸垂バー）のSVGを生成する。

    バー等の剛体は手の位置に合わせてグループごと平行移動させる
    （<animateTransform>）ため、点ごとのアニメーションは不要でコードが簡潔になる。
    """
    if kind == "fixed_bar":
        # 懸垂バー：頭上に固定表示（動かない）
        return f'<line x1="36" y1="8" x2="84" y2="8" stroke="{PROP_BAR_COLOR}" stroke-width="4" stroke-linecap="round"/>'

    if kind is None:
        return ""

    ax, ay = hand_a
    dx, dy = hand_b[0] - ax, hand_b[1] - ay
    transform = (
        f'<animateTransform attributeName="transform" type="translate" dur="{dur}s" '
        f'repeatCount="indefinite" calcMode="spline" keyTimes="0;{mid};1" '
        f'keySplines="{_EASE};{_EASE}" values="0 0;{dx} {dy};0 0"/>'
    )

    if kind == "bar":
        # バーベル：手の位置を中心に水平な棒＋両端のプレート
        inner = (
            f'<line x1="{ax - 16}" y1="{ay}" x2="{ax + 16}" y2="{ay}" '
            f'stroke="{PROP_BAR_COLOR}" stroke-width="3" stroke-linecap="round"/>'
            f'<circle cx="{ax - 16}" cy="{ay}" r="5" fill="{PROP_PLATE_COLOR}"/>'
            f'<circle cx="{ax + 16}" cy="{ay}" r="5" fill="{PROP_PLATE_COLOR}"/>'
        )
    elif kind == "dumbbell":
        # ダンベル：手の位置に小さな重り
        inner = (
            f'<rect x="{ax - 6}" y="{ay - 4}" width="12" height="8" rx="2" fill="{PROP_PLATE_COLOR}"/>'
        )
    elif kind == "ball":
        # メディシンボール：手の位置に円
        inner = f'<circle cx="{ax}" cy="{ay}" r="7" fill="{PROP_PLATE_COLOR}"/>'
    else:
        return ""

    return f'<g>{inner}{transform}</g>'


def render_exercise_animation(movement_pattern: str) -> str:
    """動作パターンIDから、往復アニメーションするスティックフィギュアSVGを生成する。

    引数:
        movement_pattern: MOVEMENT_PATTERNS のキー（未知の値は "generic" にフォールバック）
    戻り値:
        SVGマークアップ文字列（st.markdown(..., unsafe_allow_html=True) で描画する想定）
    """
    pattern = MOVEMENT_PATTERNS.get(movement_pattern, MOVEMENT_PATTERNS["generic"])
    pose_a, pose_b = pattern["a"], pattern["b"]
    dur, mid = pattern["dur"], pattern["mid"]

    def part(pose: dict, key: str):
        """指定パーツの座標を返す。片方のポーズに無ければ相手側の値で代用する。"""
        return pose.get(key) or pose_b.get(key) or pose_a.get(key)

    def endpoints(key: str):
        """指定パーツの端点（手・足）の開始/終了座標を返す。"""
        return part(pose_a, key)[-1], part(pose_b, key)[-1]

    svg = [
        f'<svg viewBox="0 0 {VIEW_WIDTH} {VIEW_HEIGHT}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{pattern["label"]}のアニメーション" style="width:100%;height:auto;max-height:230px;">',
        f'<line x1="8" y1="{GROUND_Y}" x2="{VIEW_WIDTH - 8}" y2="{GROUND_Y}" '
        f'stroke="{GROUND_COLOR}" stroke-width="2" stroke-linecap="round"/>',
    ]

    # --- 奥側（薄い肌色）：奥行きのため先に描く ---
    for far_key in ("arm2", "leg2"):
        if far_key in pose_a or far_key in pose_b:
            svg.append(_animated_polyline(part(pose_a, far_key), part(pose_b, far_key), dur, mid, SKIN_FAR, FAR_LIMB_WIDTH))
    if "leg2" in pose_a or "leg2" in pose_b:
        (ax, ay), (bx, by) = endpoints("leg2")
        svg.append(_translated_group(_shoe_svg(ax, ay, SHOE_FAR), ax, ay, bx, by, dur, mid))
    if "arm2" in pose_a or "arm2" in pose_b:
        (ax, ay), (bx, by) = endpoints("arm2")
        svg.append(_translated_group(_hand_svg(ax, ay, SKIN_FAR), ax, ay, bx, by, dur, mid))

    # 懸垂バーなど固定器具は体の後ろに描く
    if pattern["prop"] == "fixed_bar":
        svg.append(_prop_svg("fixed_bar", (0, 0), (0, 0), dur, mid))

    # --- 手前の脚（肌）＋靴 ---
    svg.append(_animated_polyline(pose_a["leg"], pose_b["leg"], dur, mid, SKIN, LIMB_WIDTH))
    (ax, ay), (bx, by) = endpoints("leg")
    svg.append(_translated_group(_shoe_svg(ax, ay, SHOE), ax, ay, bx, by, dur, mid))

    # --- ショートパンツ（腰） ---
    (hax, hay), (hbx, hby) = pose_a["spine"][1], pose_b["spine"][1]
    svg.append(_translated_group(_shorts_svg(hax, hay), hax, hay, hbx, hby, dur, mid))

    # --- 胴体（シャツ）---
    svg.append(_animated_polyline(pose_a["spine"], pose_b["spine"], dur, mid, SHIRT, TORSO_WIDTH))

    # --- 手前の腕（肌）＋袖＋手 ---
    svg.append(_animated_polyline(pose_a["arm"], pose_b["arm"], dur, mid, SKIN, LIMB_WIDTH))
    (sax, say), (sbx, sby) = pose_a["spine"][0], pose_b["spine"][0]
    svg.append(_translated_group(_sleeve_svg(sax, say), sax, say, sbx, sby, dur, mid))
    (ax, ay), (bx, by) = endpoints("arm")
    svg.append(_translated_group(_hand_svg(ax, ay, SKIN), ax, ay, bx, by, dur, mid))

    # --- 頭 ---
    (hdax, hday), (hdbx, hdby) = pose_a["head"], pose_b["head"]
    svg.append(_translated_group(_head_svg(hdax, hday), hdax, hday, hdbx, hdby, dur, mid))

    # --- 手に持つ器具（バーベル・ダンベル・ボール）---
    if pattern["prop"] and pattern["prop"] != "fixed_bar":
        hand_a = part(pose_a, "arm")[-1]
        hand_b = part(pose_b, "arm")[-1]
        svg.append(_prop_svg(pattern["prop"], hand_a, hand_b, dur, mid))

    svg.append("</svg>")
    return "".join(svg)
