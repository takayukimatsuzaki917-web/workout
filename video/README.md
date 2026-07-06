# video/ — 種目説明動画の自動生成（Remotion）

[Remotion](https://www.remotion.dev/)（Reactで動画を作るツール）で、種目ごとの説明動画をプログラム的に生成する。
和装のトレーナーキャラを"案内役"に、桜吹雪・ゆっくりズーム・情報テロップの演出を重ねた縦型（1080×1920）ショート動画を出力する。

## 構成（約16.5秒・案内役キャラ＋下部テロップ）
全編を通して、和装トレーナーの一枚絵を全画面背景に、桜吹雪とゆっくりズーム（Ken Burns）を重ねる。
下部テロップが4段階で切り替わる：
1. **本日のトレーニング** — 種目名・カテゴリ・器具
2. **鍛える部位** — 対象筋肉
3. **やり方** — セット×回数・休憩・ポイント
4. **締め** — ブランド＋免責

- `src/ExerciseVideo.tsx` — 背景画像・桜・スクリム・下部テロップを合成（テロップは Sequence で切替）
- `src/SakuraPetals.tsx` — 桜の花びらが舞う演出（フレームから決定的に位置を計算）
- `public/trainer.png` — 案内役キャラの一枚絵（Canva AI 生成のイラストを書き出したもの）
- `src/data/exercises_master.json` — 種目マスタ（`web/data/` のコピー）
- `src/theme.ts` — 配色・日本語フォント（Noto Sans JP）
- `src/exerciseData.ts` — 種目データの読み込み

種目は `exerciseId`（props）で切り替え可能。既定は `squat_barbell`。

## セットアップ
```bash
cd video
npm install
```

## プレビュー（Remotion Studio）
```bash
npm run dev
# ブラウザで各種目・各フレームを確認・編集できる
```

## 動画を書き出す（MP4）
```bash
# 既定（バーベルスクワット）
npx remotion render ExerciseVideo out/squat_barbell.mp4

# 別の種目を指定（例：ベンチプレス）
npx remotion render ExerciseVideo out/bench.mp4 --props='{"exerciseId":"bench_press_barbell"}'
```

## 1フレームだけ確認（レイアウトチェック）
```bash
npx remotion still ExerciseVideo out/frame.png --frame=140 --scale=0.5
```

## データ更新時
`web/data/*.json` を変えたら、このディレクトリの `src/data/` にコピーし直す。

## メモ
- キャラは"案内役"。実際の動作（正しいフォーム）は web版アプリに埋め込んだ実写YouTube動画で確認する想定。
- `public/trainer.png` を差し替えれば、キャラの見た目を変更できる（別のイラストやご自身で用意したPNGでも可）。
- 今後は全38種目のバッチ書き出し（各 `exerciseId` をループ）に拡張可能。種目ごとに雰囲気の違うキャラ絵を用意することもできる。
