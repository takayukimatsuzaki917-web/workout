# web/ — 静的サイト版プロトタイプ（WIP）

Streamlit版のデザイン上の限界を踏まえ、UIを **静的サイト（HTML + Tailwind + 素のJS）** へ移行する作業中のディレクトリ。

## 現状
- `index.html` — 結果画面の**デザインモック**（現時点では柔道1競技・データ埋め込みの生成物）。
  デザイン確定用で、次段階でJSによる動的レンダリング（プロフィール入力→競技選択→結果）に置き換える。
- `data/muscles.json` — 筋肉ハイライト用のSVGパス。`vendor/bodyFront.ts` / `vendor/bodyBack.ts` から抽出したもの。
- `vendor/` — [react-native-body-highlighter](https://github.com/HichamELBSI/react-native-body-highlighter)（MIT License）の筋肉図データ。`LICENSE-body-highlighter` に原ライセンスを保存。

## デザイン方針
- **体図**: オープンソースの解剖図SVG（`vendor/`）を色分け表示。
- **動作の見せ方**: 種目名でのYouTube検索リンク（「やり方を動画で見る」）。手描きアニメは廃止。
- **絵文字は使わない**（モノクロSVGアイコン＋タイポグラフィで統一）。

## ローカルで見る
```bash
python -m http.server 8080 --directory web
# http://localhost:8080
```

## 今後
1. 計算ロジック（重量・カロリー・プログラム生成・筋肉分類）をJSへ移植
2. プロフィール入力→競技選択→結果 の3画面、8競技すべてに対応
3. モバイル/PC両対応で仕上げ
