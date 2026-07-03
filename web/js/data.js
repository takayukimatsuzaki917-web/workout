// マスタデータ（競技・エクササイズ・筋肉図）をブラウザから読み込むモジュール。
// 静的サイトなので fetch で web/data/ 配下のJSONを取得する。

let cache = null;

/**
 * 全マスタデータを一度だけ読み込んでキャッシュする。
 * @returns {Promise<{sports:Array, exercises:Array, muscles:Object}>}
 */
export async function loadData() {
  if (cache) return cache;
  const [sports, exercises, muscles] = await Promise.all([
    fetch("data/sports_master.json").then((r) => r.json()),
    fetch("data/exercises_master.json").then((r) => r.json()),
    fetch("data/muscles.json").then((r) => r.json()),
  ]);
  cache = { sports, exercises, muscles };
  return cache;
}
