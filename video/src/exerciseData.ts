// 種目マスタからの読み込みヘルパー。
import exercises from "./data/exercises_master.json";

export type Exercise = {
  id: string;
  name_ja: string;
  category: string;
  equipment: string;
  target_muscles: string[];
  muscle_svg_ids: string[];
  default_sets: number;
  default_reps: string;
  rest_seconds: number;
  description: string;
};

const ALL = exercises as unknown as Exercise[];

/** 種目IDから1件取得（見つからなければ先頭）。 */
export function getExercise(id: string): Exercise {
  return ALL.find((e) => e.id === id) ?? ALL[0];
}
