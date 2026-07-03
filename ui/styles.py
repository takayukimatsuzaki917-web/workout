"""アプリ全体で共通のCSS注入・免責事項フッターを提供する。"""

import streamlit as st

_BASE_CSS = """
<style>
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px;
}
.disclaimer-footer {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #e0e0e0;
    color: #757575;
    font-size: 0.8rem;
    line-height: 1.6;
}
.sport-card-label {
    text-align: center;
    font-weight: 600;
}
</style>
"""

_DISCLAIMER_TEXT = (
    "※本アプリで表示される推奨重量・消費カロリー等の数値はすべて目安であり、"
    "医療的・専門的な助言ではありません。実際のトレーニングは体調やケガのリスクを踏まえ、"
    "無理のない範囲で行ってください。"
)


def inject_base_styles() -> None:
    """カード風の見た目やフッター用の最小限CSSを注入する（1回呼べば全画面に適用される）。"""
    st.markdown(_BASE_CSS, unsafe_allow_html=True)


def render_disclaimer_footer() -> None:
    """画面下部に免責事項を表示する（非機能要件：医療的助言ではない旨の明記）。"""
    st.markdown(f'<div class="disclaimer-footer">{_DISCLAIMER_TEXT}</div>', unsafe_allow_html=True)
