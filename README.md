# 競技別筋トレプログラム提案アプリ

競技と体格情報を入力するだけで、その競技のパフォーマンス向上に直結する筋トレプログラム（種目・回数・セット数・重量目安・対象筋肉部位・消費カロリー）を自動提案するWebアプリ。

## 実装バージョン

本リポジトリには2つのUIがあります。**現在のメインは静的サイト版（`web/`）** です。

| バージョン | 場所 | 技術 | 位置づけ |
|---|---|---|---|
| **静的サイト版（メイン）** | `web/` | HTML + Tailwind CSS + 素のJS | 洗練したモバイルUI。解剖図SVG＋YouTube動画。ビルド不要でそのままデプロイ可 |
| Streamlit版（初期プロトタイプ） | `app.py` / `ui/` / `logic/` | Python + Streamlit | データ・計算ロジックの検証用。pytest済み |

計算ロジックは Python（`logic/`）で設計・テストし、それを `web/js/logic.js` へ移植しています。

## 使い方（静的サイト版）

```bash
python -m http.server 8080 --directory web
# http://localhost:8080
```

1. **プロフィール入力** — 性別・年齢・体重・身長・経験レベル
2. **競技選択** — サッカー・野球・水泳・ロードバイク・マラソン・ボルダリング・柔道・ラグビー
3. **結果** — 競技別の5〜8種目（推奨重量・消費カロリー・全身の筋肉ハイライト図）。各種目から「やり方を動画で見る」「詳細（代替種目）」へ

詳細は [web/README.md](web/README.md) を参照。

## Streamlit版（ロジック検証用）の構成

- `app.py` — 画面ルーター（プロフィール／競技選択／結果画面の切り替え）
- `data/sports_master.json` — 対象8競技のマスタデータ（主動筋群・エネルギー系比率・推奨種目など）
- `data/exercises_master.json` — 38種目のエクササイズマスタデータ
- `logic/weight_calculator.py` — 適正重量（推定1RM・目安重量）算出ロジック
- `logic/calorie_calculator.py` — MET法による消費カロリー算出ロジック
- `logic/program_builder.py` — 競技×プロフィールからのプログラム組み立て・代替種目検索ロジック
- `logic/muscle_coverage.py` — 筋肉ハイライト（主動筋/協働筋）の分類ロジック
- `ui/body_diagram.py` — 前面/背面SVGボディ図の生成
- `ui/screens.py` — 3画面（プロフィール入力／競技選択／プログラム結果）のUI
- `ui/styles.py` — 共通CSS・免責事項フッター

## Streamlit版のセットアップ

### ローカル実行

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Docker実行

```bash
docker compose up --build
```

`http://localhost:8501` でアクセスできます。

## テスト

```bash
pytest tests/
```

ロジック層（重量算出・カロリー算出・プログラム組み立て・筋肉分類）は純粋関数として実装されており、pytestで検証済みです。

## 対象競技

サッカー、野球、水泳、ロードバイク、マラソン、ボルダリング、柔道、ラグビー

## 今後の拡張候補

- プロフィール・選択履歴のサーバ側保存（現状はブラウザの `localStorage`）
- 種目データの拡充・代替種目提案ロジックの高度化
- GitHub Pages 等への静的デプロイ・公開

## 注意事項

本アプリで算出される重量・カロリー等の数値は目安であり、医療的な助言ではありません。実際のトレーニングは体調やケガのリスクを踏まえ、無理のない範囲で行ってください。
