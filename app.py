import streamlit as st

from ui.screens import render_profile_screen, render_result_screen, render_sport_screen
from ui.styles import inject_base_styles, render_disclaimer_footer

st.set_page_config(page_title="競技別筋トレプログラム提案", page_icon="💪", layout="wide")
inject_base_styles()

if "step" not in st.session_state:
    st.session_state.step = "profile"

st.title("競技別筋トレプログラム提案アプリ")

with st.sidebar:
    st.subheader("ナビゲーション")
    has_profile = "profile" in st.session_state
    has_sport = "selected_sport_id" in st.session_state

    if st.button("① プロフィールを編集", use_container_width=True):
        st.session_state.step = "profile"
        st.rerun()

    if has_profile and st.button("② 競技を選び直す", use_container_width=True):
        st.session_state.step = "sport"
        st.rerun()

    if has_profile and has_sport and st.button("③ プログラム結果を見る", use_container_width=True):
        st.session_state.step = "result"
        st.rerun()

if st.session_state.step == "profile":
    render_profile_screen()
elif st.session_state.step == "sport":
    render_sport_screen()
elif st.session_state.step == "result":
    render_result_screen()

render_disclaimer_footer()
