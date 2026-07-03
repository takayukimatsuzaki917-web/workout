// 解剖図SVG（react-native-body-highlighter, MIT）を用いた筋肉ハイライト描画。
// muscles.json のパスデータを、対象筋肉だけ色分けして表示する。

// 我々の muscle_svg_id -> 解剖図ライブラリの (side, slug)
const MUSCLE_MAP = {
  quadriceps: [["front", "quadriceps"]],
  hip_flexors: [["front", "quadriceps"]],
  glutes: [["back", "gluteal"]],
  hamstrings: [["back", "hamstring"]],
  core: [["front", "abs"]],
  obliques: [["front", "obliques"]],
  calves: [["front", "calves"], ["back", "calves"]],
  chest: [["front", "chest"]],
  chest_upper: [["front", "chest"]],
  shoulders: [["front", "deltoids"], ["back", "deltoids"]],
  rear_delts: [["back", "deltoids"]],
  rotator_cuff: [["back", "deltoids"]],
  triceps: [["front", "triceps"], ["back", "triceps"]],
  biceps: [["front", "biceps"]],
  lats: [["back", "upper-back"]],
  trapezius: [["front", "trapezius"], ["back", "trapezius"]],
  erector_spinae: [["back", "lower-back"]],
  forearms: [["front", "forearm"], ["back", "forearm"]],
  finger_flexors: [["front", "forearm"], ["back", "forearm"]],
};

const BODY_FILL = "#e2e8f0";
const BODY_STROKE = "#cbd5e1";
export const PRIMARY_COLOR = "#f43f5e"; // 主動筋（rose）
export const SECONDARY_COLOR = "#fbbf24"; // 協働筋（amber）

const VIEWBOX = { front: "0 0 724 1448", back: "724 0 724 1448" };

/**
 * 解剖図SVGを描画。全身をニュートラル色で敷き、対象筋肉を色付けする。
 * @param {Object} muscles muscles.json（{front:{slug:[path]}, back:{...}}）
 * @param {Object} highlight {muscle_svg_id: "primary"|"secondary"}
 * @param {"front"|"back"} side
 * @param {{maxH?:number}} opts
 */
export function renderMuscleMap(muscles, highlight, side, opts = {}) {
  const maxH = opts.maxH || 220;
  const label = side === "front" ? "前面" : "背面";
  const parts = [
    `<svg viewBox="${VIEWBOX[side]}" xmlns="http://www.w3.org/2000/svg" ` +
      `style="width:100%;height:auto;max-height:${maxH}px;" role="img" aria-label="${label}の筋肉図">`,
  ];
  // 全身（対象外を含む）をニュートラル色で
  for (const paths of Object.values(muscles[side])) {
    for (const d of paths) {
      parts.push(`<path d="${d}" fill="${BODY_FILL}" stroke="${BODY_STROKE}" stroke-width="2"/>`);
    }
  }
  // 対象筋肉を色付け
  for (const [id, level] of Object.entries(highlight)) {
    const color = level === "primary" ? PRIMARY_COLOR : SECONDARY_COLOR;
    for (const [s, slug] of MUSCLE_MAP[id] || []) {
      if (s !== side) continue;
      for (const d of muscles[side][slug] || []) {
        parts.push(`<path d="${d}" fill="${color}" stroke="#ffffff" stroke-width="2"/>`);
      }
    }
  }
  parts.push("</svg>");
  return parts.join("");
}

/** 種目の主動筋（先頭のmuscle_svg_id）が属する側を返す。 */
export function primarySide(exercise) {
  const first = exercise.muscle_svg_ids[0];
  const mappings = MUSCLE_MAP[first] || [["front"]];
  return mappings[0][0];
}
