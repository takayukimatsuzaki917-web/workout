"""3画面（プロフィール入力／競技選択／プログラム結果）のレンダリング関数。"""

from __future__ import annotations

import streamlit as st

from logic.muscle_coverage import aggregate_program_coverage, classify_exercise_muscles
from logic.program_builder import build_program, find_alternative_exercises, load_sports_master
from ui.body_diagram import render_body_diagram_svg
from ui.exercise_animation import get_movement_label, render_exercise_animation

LEVEL_OPTIONS = ["初心者", "中級者", "上級者"]

SPORT_ICONS = {
    "soccer": "⚽",
    "baseball": "⚾",
    "swimming": "🏊",
    "road_bike": "🚴",
    "marathon": "🏃",
    "bouldering": "🧗",
    "judo": "🥋",
    "rugby": "🏉",
}


def render_profile_screen() -> None:
    """プロフィール入力画面。既存のプロフィールがあれば初期値として表示する。"""
    st.header("① プロフィール入力")
    st.write("あなたの体格・経験レベルを入力してください。競技に応じた重量目安の算出に使用します。")

    existing = st.session_state.get("profile", {})

    with st.form("profile_form"):
        gender = st.radio(
            "性別", ["男性", "女性"],
            index=["男性", "女性"].index(existing.get("gender", "男性")),
            horizontal=True,
        )
        age = st.number_input("年齢", min_value=10, max_value=100, value=existing.get("age", 25))
        bodyweight_kg = st.number_input(
            "体重(kg)", min_value=20.0, max_value=200.0,
            value=float(existing.get("bodyweight_kg", 65.0)), step=0.5,
        )
        height_cm = st.number_input(
            "身長(cm)", min_value=100.0, max_value=220.0,
            value=float(existing.get("height_cm", 170.0)), step=0.5,
        )
        level = st.selectbox(
            "筋トレ経験レベル", LEVEL_OPTIONS,
            index=LEVEL_OPTIONS.index(existing.get("level", "初心者")),
        )
        submitted = st.form_submit_button("次へ（競技を選ぶ）", type="primary")

    if submitted:
        st.session_state.profile = {
            "gender": gender,
            "age": age,
            "bodyweight_kg": bodyweight_kg,
            "height_cm": height_cm,
            "level": level,
        }
        st.session_state.step = "sport"
        st.rerun()


def render_sport_screen() -> None:
    """競技選択画面。8競技をアイコン付きボタンで表示する。"""
    st.header("② 競技を選択")
    st.write("パフォーマンス向上を目指す競技を選んでください。")

    sports = load_sports_master()
    columns_per_row = 4

    for row_start in range(0, len(sports), columns_per_row):
        row_sports = sports[row_start : row_start + columns_per_row]
        columns = st.columns(columns_per_row)
        for column, sport in zip(columns, row_sports):
            with column:
                icon = SPORT_ICONS.get(sport["id"], "🏅")
                if st.button(f"{icon}\n{sport['name_ja']}", key=f"sport_{sport['id']}", use_container_width=True):
                    st.session_state.selected_sport_id = sport["id"]
                    st.session_state.step = "result"
                    st.rerun()


def _weight_short_html(weight_recommendation: dict) -> str:
    """カード表示用に、推奨重量を簡潔なHTML文字列にまとめる。"""
    if weight_recommendation["has_weight_target"]:
        weight_kg = weight_recommendation["weight_kg"]
        ratio = weight_recommendation["bodyweight_ratio"]
        return (
            f'<span class="ex-weight-strong">{weight_kg}kg</span>'
            f'<span class="ex-weight-body">（体重の{ratio}倍・目安）</span>'
        )
    return '<span class="ex-weight-body">自重・可変重量（重量目安なし）</span>'


def _render_animation_demo(exercise: dict) -> None:
    """動作アニメーションのデモを枠付きで描画する。"""
    animation_svg = render_exercise_animation(exercise["movement_pattern"])
    st.markdown(f'<div class="ex-demo">{animation_svg}</div>', unsafe_allow_html=True)
    st.markdown('<div class="ex-demo-caption">▶ 動作イメージ（自動再生）</div>', unsafe_allow_html=True)


@st.dialog("種目詳細")
def _render_exercise_detail_dialog(exercise: dict) -> None:
    """種目1件分の詳細（動作デモ・説明・対象筋肉の体図・代替種目）をモーダル表示する。"""
    st.subheader(exercise["name_ja"])
    st.caption(f"使用器具: {exercise['equipment']}｜{get_movement_label(exercise['movement_pattern'])}")

    _render_animation_demo(exercise)
    st.write(exercise["description"])

    st.markdown("**対象筋肉**")
    highlight_map = classify_exercise_muscles(exercise)
    diagram_columns = st.columns(2)
    with diagram_columns[0]:
        st.caption("前面")
        st.markdown(render_body_diagram_svg(highlight_map, "front"), unsafe_allow_html=True)
    with diagram_columns[1]:
        st.caption("背面")
        st.markdown(render_body_diagram_svg(highlight_map, "back"), unsafe_allow_html=True)

    st.markdown("**代替種目の候補**")
    alternatives = find_alternative_exercises(exercise["id"])
    if alternatives:
        for alternative in alternatives:
            st.write(f"- {alternative['name_ja']}（{alternative['equipment']}）")
    else:
        st.caption("代替種目は見つかりませんでした。")


def _render_exercise_card(exercise: dict) -> None:
    """種目一覧の1カード分を表示する。動作アニメーション＋初心者向け説明＋各種情報。"""
    with st.container(border=True):
        # 種目名は全幅で表示し、長い名前でも折り返して見切れないようにする
        st.markdown(f'<div class="ex-title">{exercise["name_ja"]}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="ex-sub">🏋️ {exercise["equipment"]}　｜　'
            f'▶ {get_movement_label(exercise["movement_pattern"])}</div>',
            unsafe_allow_html=True,
        )

        demo_column, info_column = st.columns([1, 1.6])

        with demo_column:
            _render_animation_demo(exercise)

        with info_column:
            # 「どんな種目か」を常に表示（初心者がイメージを掴めるように）
            st.markdown(f'<div class="ex-desc">{exercise["description"]}</div>', unsafe_allow_html=True)
            info_html = (
                '<div class="ex-info">'
                f'<div><span class="ex-label">🎯 対象</span>{"、".join(exercise["target_muscles"])}</div>'
                f'<div><span class="ex-label">🔁 量</span>{exercise["sets"]}セット × {exercise["reps"]}</div>'
                f'<div><span class="ex-label">⏱ 休憩</span>{exercise["rest_seconds"]}秒</div>'
                f'<div><span class="ex-label">🏋 重量</span>{_weight_short_html(exercise["weight_recommendation"])}</div>'
                f'<div><span class="ex-label">🔥 消費</span>約{exercise["calories_kcal"]}kcal</div>'
                '</div>'
            )
            st.markdown(info_html, unsafe_allow_html=True)

        if st.button("詳細・対象筋肉・代替種目を見る", key=f"detail_{exercise['id']}", use_container_width=True):
            _render_exercise_detail_dialog(exercise)


def render_result_screen() -> None:
    """プログラム提案結果画面。"""
    profile = st.session_state.get("profile")
    sport_id = st.session_state.get("selected_sport_id")
    if not profile or not sport_id:
        st.warning("プロフィールと競技を選択してください。")
        return

    program = build_program(profile, sport_id)
    sport = program["sport"]
    icon = SPORT_ICONS.get(sport["id"], "🏅")

    st.header(f"③ {icon} {sport['name_ja']}向け筋トレプログラム")
    st.write(
        f"目的: **{sport['training_purpose']}** ／ "
        f"週{sport['sessions_per_week']}回 × 1回{sport['minutes_per_session']}分が目安です。"
    )

    st.subheader("全身カバレッジビュー")
    st.caption("🔴 主動筋（メイン）　🟠 協働筋（サブ）")
    coverage = aggregate_program_coverage(program["exercises"])
    coverage_columns = st.columns(2)
    with coverage_columns[0]:
        st.caption("前面")
        st.markdown(render_body_diagram_svg(coverage, "front"), unsafe_allow_html=True)
    with coverage_columns[1]:
        st.caption("背面")
        st.markdown(render_body_diagram_svg(coverage, "back"), unsafe_allow_html=True)

    st.subheader("種目一覧")
    for exercise in program["exercises"]:
        _render_exercise_card(exercise)

    st.subheader("消費カロリー サマリー")
    summary_columns = st.columns(2)
    summary_columns[0].metric("1回あたりの消費カロリー", f"{program['session_calories_kcal']} kcal")
    summary_columns[1].metric("週間の想定消費カロリー", f"{program['weekly_calories_kcal']} kcal")
