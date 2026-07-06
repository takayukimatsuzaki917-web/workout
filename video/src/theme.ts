// 動画全体で使う配色・フォント。アプリ(web/)のデザイントークンに合わせている。
import { loadFont } from "@remotion/google-fonts/NotoSansJP";

// 日本語フォント（Noto Sans JP）を読み込む。レンダリングはフォント準備まで待機される。
export const { fontFamily } = loadFont("normal", {
  weights: ["400", "700", "900"],
});

export const COLORS = {
  bgTop: "#eef2ff", // indigo-50
  bgBottom: "#f8fafc", // slate-50
  indigo: "#6366f1", // indigo-500
  indigoDeep: "#4f46e5", // indigo-600
  slate900: "#0f172a",
  slate700: "#334155",
  slate500: "#64748b",
  slate400: "#94a3b8",
  rose: "#f43f5e",
  amber: "#fbbf24",
  white: "#ffffff",
};
