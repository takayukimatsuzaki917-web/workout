// アプリ本体：状態管理・画面遷移・レンダリング。
// プロフィール入力 → 競技選択 → 結果 の3画面を、#app に描画して切り替える。

import { loadData } from "./data.js";
import {
  buildProgram,
  findAlternativeExercises,
  classifyExerciseMuscles,
  aggregateCoverage,
} from "./logic.js";
import { renderMuscleMap, primarySide, PRIMARY_COLOR, SECONDARY_COLOR } from "./musclemap.js";

// ---- 定数・アイコン（絵文字は使わずSVGで統一）----
const PLAY_SVG =
  '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>';
const PLAY_SVG_LG =
  '<svg viewBox="0 0 24 24" width="26" height="26" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>';

/**
 * YouTube動画の埋め込みプレイヤー（サムネイル→クリックでiframe読み込み）。
 * 一覧に複数あってもiframeを一斉に読み込まないよう、既定はサムネイルのみ表示する。
 */
function videoEmbed(youtubeId) {
  if (!youtubeId) return "";
  return `
  <div class="mt-3">
    <div class="video-thumb relative aspect-video cursor-pointer overflow-hidden rounded-xl bg-slate-900 group"
      data-action="play-video" data-yt="${youtubeId}" role="button" aria-label="やり方を動画で見る">
      <img src="https://i.ytimg.com/vi/${youtubeId}/hqdefault.jpg" alt="やり方動画のサムネイル" loading="lazy"
        class="h-full w-full object-cover opacity-95 transition group-hover:opacity-100">
      <div class="absolute inset-0 flex items-center justify-center">
        <div class="grid h-14 w-14 place-items-center rounded-full bg-rose-600/90 pl-1 text-white shadow-lg transition group-hover:scale-105">${PLAY_SVG_LG}</div>
      </div>
      <div class="absolute bottom-2 left-2 rounded bg-black/60 px-2 py-0.5 text-[11px] font-medium text-white">やり方を動画で見る</div>
    </div>
    <a href="https://www.youtube.com/watch?v=${youtubeId}" target="_blank" rel="noopener"
      class="mt-1 block text-right text-[11px] text-slate-400 hover:text-slate-600">再生できない場合はYouTubeで開く ›</a>
  </div>`;
}
const LEVELS = ["初心者", "中級者", "上級者"];
const GENDERS = ["男性", "女性"];
const PROFILE_KEY = "workout_profile";

// ---- 状態 ----
const state = { data: null, profile: null, sportId: null, step: "profile" };

const $app = () => document.getElementById("app");

// ---- 初期化 ----
async function init() {
  state.data = await loadData();
  const saved = localStorage.getItem(PROFILE_KEY);
  if (saved) {
    state.profile = JSON.parse(saved);
    state.step = "sport"; // プロフィール保存済みなら競技選択から
  }
  render();
}

function navigate(step) {
  state.step = step;
  render();
  window.scrollTo(0, 0);
}

function render() {
  let html = "";
  if (state.step === "profile") html = profileScreen();
  else if (state.step === "sport") html = sportScreen();
  else if (state.step === "result") html = resultScreen();
  $app().innerHTML = html;
}

// ============ 画面1: プロフィール入力 ============
function segButton(group, value, active) {
  const cls = active
    ? "bg-indigo-500 text-white"
    : "bg-white text-slate-600 hover:bg-slate-50";
  return `<button type="button" data-seg="${group}" data-value="${value}"
    class="seg-btn flex-1 rounded-lg px-3 py-2 text-sm font-medium transition ${cls}">${value}</button>`;
}

function profileScreen() {
  const p = state.profile || {};
  const gender = p.gender || "男性";
  const level = p.level || "初心者";
  const num = (id, label, val, min, max, step, unit) => `
    <label class="block">
      <span class="text-sm font-medium text-slate-600">${label}</span>
      <div class="mt-1 flex items-center gap-2">
        <input id="${id}" type="number" value="${val}" min="${min}" max="${max}" step="${step}"
          class="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-slate-800 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100">
        <span class="shrink-0 text-sm text-slate-400">${unit}</span>
      </div>
    </label>`;
  return `
  <div class="px-4 py-5">
    <h1 class="text-xl font-bold text-slate-800">プロフィール入力</h1>
    <p class="mt-1 text-sm text-slate-500">体格・経験レベルを入力してください。競技に応じた重量目安の算出に使います。</p>
    <div class="mt-5 space-y-5 rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-100">
      <div>
        <span class="text-sm font-medium text-slate-600">性別</span>
        <div class="mt-1 flex gap-1 rounded-xl border border-slate-200 p-1" data-seg-group="gender">
          ${GENDERS.map((g) => segButton("gender", g, g === gender)).join("")}
        </div>
      </div>
      ${num("age", "年齢", p.age ?? 25, 10, 100, 1, "歳")}
      ${num("bodyweight", "体重", p.bodyweight_kg ?? 65, 20, 200, 0.5, "kg")}
      ${num("height", "身長", p.height_cm ?? 170, 100, 220, 0.5, "cm")}
      <div>
        <span class="text-sm font-medium text-slate-600">筋トレ経験レベル</span>
        <div class="mt-1 flex gap-1 rounded-xl border border-slate-200 p-1" data-seg-group="level">
          ${LEVELS.map((l) => segButton("level", l, l === level)).join("")}
        </div>
      </div>
    </div>
    <button type="button" data-action="submit-profile"
      class="mt-5 w-full rounded-2xl bg-indigo-500 py-3.5 text-center font-bold text-white shadow-lg shadow-indigo-200 active:scale-[.99] transition">
      競技を選ぶ
    </button>
  </div>`;
}

// ============ 画面2: 競技選択 ============
function sportScreen() {
  const cards = state.data.sports
    .map(
      (s) => `
    <button type="button" data-action="select-sport" data-sport="${s.id}"
      class="text-left rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-100 active:scale-[.98] transition hover:ring-indigo-200">
      <div class="text-lg font-bold text-slate-800">${s.name_ja}</div>
      <div class="mt-1 text-[11px] leading-snug text-slate-400 line-clamp-2">${s.primary_muscles.slice(0, 3).join("・")}</div>
      <span class="mt-2 inline-block rounded-full bg-indigo-50 px-2.5 py-0.5 text-[11px] font-medium text-indigo-500">目的 · ${s.training_purpose}</span>
    </button>`
    )
    .join("");
  return `
  <div class="px-4 py-5">
    <button type="button" data-action="go-profile" class="text-sm font-medium text-slate-400 hover:text-slate-600">‹ プロフィールを編集</button>
    <h1 class="mt-2 text-xl font-bold text-slate-800">競技を選択</h1>
    <p class="mt-1 text-sm text-slate-500">パフォーマンス向上を目指す競技を選んでください。</p>
    <div class="mt-4 grid grid-cols-2 gap-3">${cards}</div>
  </div>`;
}

// ============ 画面3: 結果 ============
function weightBlock(w) {
  if (w.has_weight_target) {
    return `<div class="mt-3 flex items-center justify-between rounded-xl bg-rose-50 px-3 py-2">
      <span class="text-xs font-semibold text-rose-500">推奨重量の目安</span>
      <span class="font-bold text-rose-600">${w.weight_kg}<span class="text-xs">kg</span>
      <span class="ml-1 text-xs font-normal text-rose-400">体重の${w.bodyweight_ratio}倍</span></span></div>`;
  }
  return `<div class="mt-3 flex items-center justify-between rounded-xl bg-slate-100 px-3 py-2">
    <span class="text-xs font-semibold text-slate-400">推奨重量の目安</span>
    <span class="text-sm font-medium text-slate-500">自重・可変重量</span></div>`;
}

function exerciseCard(ex) {
  const side = primarySide(ex);
  const sideLabel = side === "front" ? "前面" : "背面";
  const mini = renderMuscleMap(state.data.muscles, classifyExerciseMuscles(ex), side, { maxH: 150 });
  return `
  <article class="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-100">
    <div class="flex items-center gap-1.5 flex-wrap">
      <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-medium text-slate-500">${ex.equipment}</span>
      <span class="rounded-full bg-indigo-50 px-2.5 py-0.5 text-[11px] font-medium text-indigo-500">${ex.category || ""}</span>
    </div>
    <h3 class="mt-1.5 text-lg font-bold text-slate-800 leading-snug">${ex.name_ja}</h3>
    <div class="mt-3 flex gap-3">
      <div class="w-[92px] shrink-0 rounded-xl bg-slate-50 ring-1 ring-slate-100 flex flex-col items-center justify-center p-1.5">
        ${mini}<span class="mt-0.5 text-[10px] text-slate-400">${sideLabel}</span>
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-[13px] leading-relaxed text-slate-500">${ex.description}</p>
        <dl class="mt-2.5 space-y-1.5 text-[13px]">
          <div class="flex gap-2"><dt class="w-9 shrink-0 font-semibold text-slate-400">対象</dt><dd class="text-slate-700">${ex.target_muscles.join("、")}</dd></div>
          <div class="flex gap-2"><dt class="w-9 shrink-0 font-semibold text-slate-400">量</dt><dd class="text-slate-700">${ex.sets}セット × ${ex.reps}</dd></div>
          <div class="flex gap-2"><dt class="w-9 shrink-0 font-semibold text-slate-400">休憩</dt><dd class="text-slate-700">${ex.rest_seconds}秒</dd></div>
          <div class="flex gap-2"><dt class="w-9 shrink-0 font-semibold text-slate-400">消費</dt><dd class="text-slate-700">約${ex.calories_kcal}kcal</dd></div>
        </dl>
      </div>
    </div>
    ${ex.youtube_id ? videoEmbed(ex.youtube_id) : ""}
    <button type="button" data-action="open-detail" data-ex="${ex.id}"
      class="mt-2 w-full rounded-xl bg-slate-100 py-2 text-sm font-medium text-slate-600 hover:bg-slate-200 transition">
      詳細・対象筋肉・代替種目を見る</button>
    ${weightBlock(ex.weight_recommendation)}
  </article>`;
}

function resultScreen() {
  const program = buildProgram(state.data, state.profile, state.sportId);
  const sport = program.sport;
  const coverage = aggregateCoverage(program.exercises);
  const frontMap = renderMuscleMap(state.data.muscles, coverage, "front", { maxH: 260 });
  const backMap = renderMuscleMap(state.data.muscles, coverage, "back", { maxH: 260 });
  const cards = program.exercises.map(exerciseCard).join("");

  return `
  <div class="px-4 pt-4 pb-2 flex items-center justify-between text-sm">
    <button type="button" data-action="go-sport" class="font-medium text-slate-400 hover:text-slate-600">‹ 競技を変更</button>
    <button type="button" data-action="go-profile" class="font-medium text-slate-400 hover:text-slate-600">プロフィール編集</button>
  </div>

  <section class="px-4">
    <div class="rounded-3xl bg-gradient-to-br from-indigo-500 via-indigo-500 to-violet-500 p-6 text-white shadow-lg shadow-indigo-200">
      <div class="text-[13px] font-medium tracking-wide text-white/70">あなたの競技向けプログラム</div>
      <div class="mt-1 text-4xl font-black tracking-tight">${sport.name_ja}</div>
      <div class="mt-4 flex flex-wrap gap-2 text-[13px]">
        <span class="rounded-full bg-white/20 px-3 py-1 font-medium backdrop-blur">目的 · ${sport.training_purpose}</span>
        <span class="rounded-full bg-white/20 px-3 py-1 font-medium backdrop-blur">週${sport.sessions_per_week}回</span>
        <span class="rounded-full bg-white/20 px-3 py-1 font-medium backdrop-blur">1回${sport.minutes_per_session}分</span>
      </div>
    </div>
  </section>

  <section class="px-4 pt-6">
    <h2 class="section-title">鍛える部位</h2>
    <div class="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-100">
      <div class="mb-3 flex items-center justify-center gap-4 text-xs text-slate-500">
        <span class="flex items-center gap-1"><span class="inline-block h-2.5 w-2.5 rounded-full" style="background:${PRIMARY_COLOR}"></span>主動筋</span>
        <span class="flex items-center gap-1"><span class="inline-block h-2.5 w-2.5 rounded-full" style="background:${SECONDARY_COLOR}"></span>協働筋</span>
      </div>
      <div class="flex justify-center gap-8">
        <div class="w-28"><div class="mb-1 text-center text-xs text-slate-400">前面</div>${frontMap}</div>
        <div class="w-28"><div class="mb-1 text-center text-xs text-slate-400">背面</div>${backMap}</div>
      </div>
    </div>
  </section>

  <section class="px-4 pt-6">
    <h2 class="section-title">メニュー <span class="text-sm font-normal text-slate-400">全${program.exercises.length}種目</span></h2>
    <div class="space-y-4">${cards}</div>
  </section>

  <section class="px-4 pt-6">
    <h2 class="section-title">消費カロリー</h2>
    <div class="grid grid-cols-2 gap-3">
      <div class="rounded-2xl bg-white p-4 text-center shadow-sm ring-1 ring-slate-100">
        <div class="text-xs text-slate-400">1回あたり</div>
        <div class="mt-1 text-2xl font-black text-slate-800">${program.session_calories_kcal}<span class="ml-0.5 text-sm font-medium text-slate-400">kcal</span></div>
      </div>
      <div class="rounded-2xl bg-white p-4 text-center shadow-sm ring-1 ring-slate-100">
        <div class="text-xs text-slate-400">週の想定</div>
        <div class="mt-1 text-2xl font-black text-slate-800">${program.weekly_calories_kcal}<span class="ml-0.5 text-sm font-medium text-slate-400">kcal</span></div>
      </div>
    </div>
  </section>

  <footer class="px-5 py-6 mt-4 text-[11px] leading-relaxed text-slate-400">
    ※表示される推奨重量・消費カロリー等はすべて目安であり、医療的・専門的な助言ではありません。体調やケガのリスクを踏まえ、無理のない範囲で行ってください。<br>
    筋肉図: react-native-body-highlighter (MIT License)
  </footer>`;
}

// ============ 詳細モーダル ============
function openDetail(exId) {
  const ex = state.data.exercises.find((e) => e.id === exId);
  if (!ex) return;
  const cls = classifyExerciseMuscles(ex);
  const front = renderMuscleMap(state.data.muscles, cls, "front", { maxH: 200 });
  const back = renderMuscleMap(state.data.muscles, cls, "back", { maxH: 200 });
  const alts = findAlternativeExercises(state.data, ex.id);
  const altHtml = alts.length
    ? alts.map((a) => `<li class="text-sm text-slate-700">・${a.name_ja}<span class="text-slate-400">（${a.equipment}）</span></li>`).join("")
    : '<li class="text-sm text-slate-400">代替種目は見つかりませんでした。</li>';

  const overlay = document.createElement("div");
  overlay.id = "detail-modal";
  overlay.className = "fixed inset-0 z-30 flex items-end sm:items-center justify-center bg-black/40 p-0 sm:p-4";
  overlay.innerHTML = `
    <div class="w-full max-w-[440px] max-h-[90vh] overflow-y-auto rounded-t-3xl sm:rounded-3xl bg-white p-5 shadow-2xl">
      <div class="flex items-start justify-between">
        <div>
          <h3 class="text-xl font-bold text-slate-800">${ex.name_ja}</h3>
          <div class="mt-1 text-xs text-slate-400">${ex.equipment}｜${ex.category || ""}</div>
        </div>
        <button type="button" data-action="close-modal" class="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-slate-100 text-slate-500 hover:bg-slate-200">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
        </button>
      </div>
      <div class="mt-3 flex justify-center gap-6 rounded-2xl bg-slate-50 p-3">
        <div class="w-24"><div class="mb-1 text-center text-xs text-slate-400">前面</div>${front}</div>
        <div class="w-24"><div class="mb-1 text-center text-xs text-slate-400">背面</div>${back}</div>
      </div>
      <p class="mt-4 text-sm leading-relaxed text-slate-600">${ex.description}</p>
      <div class="mt-4">
        <div class="mb-1 text-sm font-bold text-slate-700">やり方の動画</div>
        ${videoEmbed(ex.youtube_id)}
      </div>
      <div class="mt-4">
        <div class="text-sm font-bold text-slate-700">代替種目の候補</div>
        <ul class="mt-1 space-y-0.5">${altHtml}</ul>
      </div>
    </div>`;
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay || e.target.closest('[data-action="close-modal"]')) overlay.remove();
  });
  document.body.appendChild(overlay);
}

// ============ イベント ============
document.addEventListener("click", (e) => {
  // セグメントボタン（性別・レベル）
  const seg = e.target.closest("[data-seg]");
  if (seg) {
    const group = seg.getAttribute("data-seg");
    document.querySelectorAll(`[data-seg="${group}"]`).forEach((b) => {
      b.classList.remove("bg-indigo-500", "text-white");
      b.classList.add("bg-white", "text-slate-600");
    });
    seg.classList.add("bg-indigo-500", "text-white");
    seg.classList.remove("bg-white", "text-slate-600");
    return;
  }

  const actionEl = e.target.closest("[data-action]");
  if (!actionEl) return;
  const action = actionEl.getAttribute("data-action");

  if (action === "submit-profile") {
    const getSeg = (g) => document.querySelector(`[data-seg="${g}"].bg-indigo-500`)?.getAttribute("data-value");
    const profile = {
      gender: getSeg("gender") || "男性",
      age: Number(document.getElementById("age").value),
      bodyweight_kg: Number(document.getElementById("bodyweight").value),
      height_cm: Number(document.getElementById("height").value),
      level: getSeg("level") || "初心者",
    };
    state.profile = profile;
    localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
    navigate("sport");
  } else if (action === "go-profile") {
    navigate("profile");
  } else if (action === "go-sport") {
    navigate("sport");
  } else if (action === "select-sport") {
    state.sportId = actionEl.getAttribute("data-sport");
    navigate("result");
  } else if (action === "open-detail") {
    openDetail(actionEl.getAttribute("data-ex"));
  } else if (action === "play-video") {
    // サムネイルをクリックしたら、その場でiframeに差し替えて再生する
    const id = actionEl.getAttribute("data-yt");
    actionEl.outerHTML =
      `<div class="aspect-video overflow-hidden rounded-xl bg-black">` +
      `<iframe class="h-full w-full" src="https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0" ` +
      `title="やり方の動画" frameborder="0" allow="autoplay; encrypted-media; fullscreen" allowfullscreen></iframe></div>`;
  }
});

init();
