"""アプリ全体で共通のCSS注入・免責事項フッターを提供する。"""

import streamlit as st

_BASE_CSS = """
<style>
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px;
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

/* ===== 種目カード ===== */
.ex-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #1d3557;
    line-height: 1.35;
    word-break: break-word;   /* 長い種目名も折り返して見切れを防ぐ */
}
.ex-sub {
    color: #6b7280;
    font-size: 0.85rem;
    margin: 0.15rem 0 0.6rem 0;
}
.ex-demo {
    background: linear-gradient(180deg, #f5f8fc 0%, #eaf0f7 100%);
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.ex-demo-caption {
    text-align: center;
    color: #6b7280;
    font-size: 0.75rem;
    margin-top: 2px;
}
.ex-desc {
    font-size: 0.9rem;
    color: #374151;
    line-height: 1.55;
    margin-bottom: 0.55rem;
}
.ex-info div {
    font-size: 0.88rem;
    color: #374151;
    margin-bottom: 5px;
    line-height: 1.4;
}
.ex-label {
    display: inline-block;
    min-width: 4.2em;
    font-weight: 600;
    color: #1d3557;
    background: #eef2f7;
    border-radius: 6px;
    padding: 1px 7px;
    margin-right: 6px;
    font-size: 0.8rem;
}
.ex-weight-strong { color: #b02a37; font-weight: 600; }
.ex-weight-body   { color: #6b7280; }
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
