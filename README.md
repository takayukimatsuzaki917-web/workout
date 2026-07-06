# 競技別筋トレプログラム提案アプリ

競技と体格情報を入力するだけで、その競技のパフォーマンス向上に直結する筋トレプログラム（種目・回数・セット数・重量目安・対象筋肉部位・消費カロリー）を自動提案するWebアプリ。

## 公開URL

https://ubiquitous-syrniki-c8e4f0.netlify.app/

`main` ブランチの `web/` 配下を更新してpushすると、Netlifyが自動で再デプロイします。

## 使い方

```bash
python -m http.server 8080 --directory web
# http://localhost:8080
```

ビルド不要（HTML + Tailwind CSS + 素のJavaScript）。ブラウザで直接動作します。

1. **プロフィール入力** — 性別・年齢・体重・身長・経験レベル
2. **競技選択** — サッカー・野球・水泳・ロードバイク・マラソン・ボルダリング・柔道・ラグビー
3. **結果** — 競技別の5〜8種目（推奨重量・消費カロリー・全身の筋肉ハイライト図）。各種目から「やり方を動画で見る」「詳細（代替種目）」へ

詳細は [web/README.md](web/README.md) を参照。

## 構成

- `web/index.html` — アプリの土台（Tailwind CDN・ヘッダー）
- `web/js/app.js` — 画面描画・状態管理（プロフィール／競技選択／結果の3画面）
- `web/js/logic.js` — 適正重量・消費カロリー・プログラム組み立て・筋肉分類ロジック
- `web/js/data.js` — マスタデータ読み込み
- `web/js/musclemap.js` — 解剖図SVGの体図描画
- `web/data/sports_master.json` — 対象8競技のマスタデータ
- `web/data/exercises_master.json` — 38種目のエクササイズマスタデータ（YouTube動画ID含む）
- `web/data/muscles.json` — 体図SVGの座標データ
- `web/vendor/` — 体図SVG素材の出所（[react-native-body-highlighter](https://github.com/HichamELBSI/react-native-body-highlighter), MIT License）
- `netlify.toml` — Netlifyデプロイ設定

## 対象競技

サッカー、野球、水泳、ロードバイク、マラソン、ボルダリング、柔道、ラグビー

## 今後の拡張候補

- プロフィール・選択履歴のサーバ側保存（現状はブラウザの `localStorage`）
- 種目データの拡充・代替種目提案ロジックの高度化
- 未検出のYouTube動画（MELOS/ティップネス以外）の継続的な差し替え

## 注意事項

本アプリで算出される重量・カロリー等の数値は目安であり、医療的な助言ではありません。実際のトレーニングは体調やケガのリスクを踏まえ、無理のない範囲で行ってください。
