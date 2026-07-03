# web/ — 静的サイト版アプリ（メインUI）

競技と体格情報から筋トレプログラムを提案する **静的Webアプリ**（HTML + Tailwind CSS + 素のJavaScript）。
ビルドツール不要で、そのまま静的ホスティング（GitHub Pages / Netlify 等）へデプロイできる。

## 画面
1. **プロフィール入力** — 性別・年齢・体重・身長・経験レベル（`localStorage` に保存）
2. **競技選択** — 8競技から選択
3. **結果** — 競技別プログラム（種目・回数・重量目安・消費カロリー）＋全身の筋肉ハイライト図
   - 各種目カード: 対象筋肉のミニ解剖図・「やり方を動画で見る」（YouTube）・詳細モーダル（代替種目）

## 構成
- `index.html` — アプリシェル（Tailwind CDN・フォント読み込み・`#app`）
- `js/`
  - `data.js` — マスタJSONの読み込み
  - `logic.js` — 適正重量・消費カロリー・プログラム組み立て・筋肉分類（Python版 `logic/` の移植）
  - `musclemap.js` — 解剖図SVGの描画・筋肉IDの対応表
  - `app.js` — 状態管理・画面遷移・レンダリング
- `data/`
  - `sports_master.json` / `exercises_master.json` — マスタ（リポジトリ直下 `data/` のコピー）
  - `muscles.json` — 筋肉ハイライト用SVGパス（`vendor/parse_muscles.py` で生成）
- `vendor/` — [react-native-body-highlighter](https://github.com/HichamELBSI/react-native-body-highlighter)（MIT）の筋肉図データと `LICENSE`、生成スクリプト

## デザイン方針
- **体図**: オープンソースの解剖図SVGを色分け（主動筋=ピンク／協働筋=アンバー）
- **動作**: 種目名でのYouTube検索リンク（「やり方を動画で見る」）
- **絵文字は使わない**（モノクロSVGアイコン＋タイポグラフィで統一）
- モバイルファースト（最大幅440px）／PCでは中央寄せ表示

## ローカルで動かす
```bash
python -m http.server 8080 --directory web
# http://localhost:8080
```

## データ更新時
- 競技・種目マスタを変えたら、`data/*.json`（リポジトリ直下）を `web/data/` にコピーする。
- 筋肉図データ（`vendor/*.ts`）を更新したら `python web/vendor/parse_muscles.py` で `muscles.json` を再生成する。
