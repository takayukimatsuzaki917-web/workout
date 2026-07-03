// 計算ロジック（Python版 logic/ の忠実な移植）。
// 適正重量・消費カロリー・プログラム組み立て・筋肉分類の純粋関数群。

// ---- 数値の丸め（小数第1位／第2位） ----
const round1 = (x) => Math.round(x * 10) / 10;
const round2 = (x) => Math.round(x * 100) / 100;

// ---- 適正重量 ----

// トレーニング目的ごとの %1RM レンジと推奨回数レンジ
export const TRAINING_PURPOSE_TABLE = {
  筋力: { percent: [85, 95], reps: "3-5回" },
  筋肥大: { percent: [67, 85], reps: "8-12回" },
  筋持久力: { percent: [50, 67], reps: "15回以上" },
};

/** 体重比係数から推定1RM(kg)を算出。係数未定義の種目は null。 */
export function estimateOneRm(exercise, bodyweightKg, level) {
  const coeff = exercise.bodyweight_coefficient;
  if (!coeff || !(level in coeff)) return null;
  const [lo, hi] = coeff[level];
  return round1(bodyweightKg * ((lo + hi) / 2));
}

/** 種目・体重・レベル・目的から目安重量を算出。 */
export function recommendWeight(exercise, bodyweightKg, level, purpose) {
  const setting = TRAINING_PURPOSE_TABLE[purpose];
  const [pmin, pmax] = setting.percent;
  const percent = (pmin + pmax) / 2;
  const oneRm = estimateOneRm(exercise, bodyweightKg, level);

  if (oneRm === null) {
    return {
      has_weight_target: false,
      weight_kg: null,
      bodyweight_ratio: null,
      percent_1rm: percent,
      reps_range: setting.reps,
      display_text: "自重・可変重量種目のため重量目安は算出していません",
    };
  }
  const weight = round1((oneRm * percent) / 100);
  const ratio = bodyweightKg ? round2(weight / bodyweightKg) : null;
  return {
    has_weight_target: true,
    weight_kg: weight,
    bodyweight_ratio: ratio,
    percent_1rm: percent,
    reps_range: setting.reps,
    display_text: `目安重量：${weight}kg（体重の${ratio}倍）※あくまで目安です`,
  };
}

// ---- 消費カロリー（MET法） ----

export function exerciseCalories(exercise, bodyweightKg, durationMinutes) {
  return round1(exercise.met_value * bodyweightKg * (durationMinutes / 60));
}
export function sessionCalories(caloriesList) {
  return round1(caloriesList.reduce((a, b) => a + b, 0));
}
export function weeklyCalories(session, sessionsPerWeek) {
  return round1(session * sessionsPerWeek);
}

// ---- 所要時間の概算（Python版と同じ係数） ----

const SECONDS_PER_REP = 3;
const DEFAULT_SET_DURATION_SECONDS = 45;

function maxRepCount(repsText) {
  const nums = (repsText.match(/\d+/g) || []).map(Number);
  return nums.length ? Math.max(...nums) : null;
}

function estimateDurationMinutes(exercise) {
  const reps = exercise.default_reps;
  const timeOrDistance = ["秒", "分", "m"].some((u) => reps.includes(u));
  const repCount = timeOrDistance ? null : maxRepCount(reps);
  const workSeconds = repCount !== null ? repCount * SECONDS_PER_REP : DEFAULT_SET_DURATION_SECONDS;
  const total = exercise.default_sets * (workSeconds + exercise.rest_seconds);
  return round1(total / 60);
}

// ---- 筋肉分類（主動筋 / 協働筋） ----

export function classifyExerciseMuscles(exercise) {
  const ids = exercise.muscle_svg_ids;
  if (!ids || ids.length === 0) return {};
  const result = { [ids[0]]: "primary" };
  for (const id of ids.slice(1)) if (!(id in result)) result[id] = "secondary";
  return result;
}

export function aggregateCoverage(exercises) {
  const coverage = {};
  for (const ex of exercises) {
    const cls = classifyExerciseMuscles(ex);
    for (const [id, level] of Object.entries(cls)) {
      if (coverage[id] === "primary") continue;
      coverage[id] = level;
    }
  }
  return coverage;
}

// ---- プログラム組み立て ----

/** 競技×プロフィールから筋トレプログラム一式を組み立てる。 */
export function buildProgram(data, profile, sportId) {
  const sport = data.sports.find((s) => s.id === sportId);
  if (!sport) throw new Error(`未知のsport_id: ${sportId}`);

  const byId = new Map(data.exercises.map((e) => [e.id, e]));
  const bodyweight = profile.bodyweight_kg;
  const level = profile.level;
  const purpose = sport.training_purpose;

  const entries = [];
  const calories = [];

  for (const exId of sport.recommended_exercise_ids) {
    const ex = byId.get(exId);
    if (!ex) throw new Error(`未知のexercise_id: ${exId}`);
    const weight = recommendWeight(ex, bodyweight, level, purpose);
    const duration = estimateDurationMinutes(ex);
    const cal = exerciseCalories(ex, bodyweight, duration);
    calories.push(cal);
    entries.push({
      id: ex.id,
      name_ja: ex.name_ja,
      equipment: ex.equipment,
      category: ex.category,
      youtube_id: ex.youtube_id,
      description: ex.description,
      target_muscles: ex.target_muscles,
      muscle_svg_ids: ex.muscle_svg_ids,
      sets: ex.default_sets,
      reps: ex.default_reps,
      rest_seconds: ex.rest_seconds,
      estimated_duration_minutes: duration,
      weight_recommendation: weight,
      calories_kcal: cal,
    });
  }

  const session = sessionCalories(calories);
  return {
    sport: {
      id: sport.id,
      name_ja: sport.name_ja,
      primary_muscles: sport.primary_muscles,
      training_purpose: purpose,
      sessions_per_week: sport.sessions_per_week,
      minutes_per_session: sport.minutes_per_session,
    },
    exercises: entries,
    session_calories_kcal: session,
    weekly_calories_kcal: weeklyCalories(session, sport.sessions_per_week),
  };
}

/** 同じ主動筋を持つ代替種目を探す。 */
export function findAlternativeExercises(data, exerciseId, limit = 2) {
  const target = data.exercises.find((e) => e.id === exerciseId);
  if (!target || !target.muscle_svg_ids.length) return [];
  const primary = target.muscle_svg_ids[0];
  return data.exercises
    .filter((e) => e.id !== exerciseId && e.muscle_svg_ids[0] === primary)
    .slice(0, limit);
}
