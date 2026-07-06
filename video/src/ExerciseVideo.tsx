// 種目説明動画（案内役キャラ版）。
// 和装トレーナーの一枚絵を全画面の背景に、桜吹雪・ゆっくりズーム・下部テロップの演出を重ねる。
import React from "react";
import {
  AbsoluteFill,
  Img,
  Sequence,
  staticFile,
  useCurrentFrame,
  interpolate,
  Easing,
} from "remotion";
import { SakuraPetals } from "./SakuraPetals";
import { COLORS, fontFamily } from "./theme";
import { getExercise } from "./exerciseData";

export type ExerciseVideoProps = {
  exerciseId: string;
};

// 下部テロップ各セクションの長さ（フレーム, 30fps）
const SEC = { name: 120, muscle: 138, howto: 150, outro: 90 };
export const TOTAL_FRAMES = SEC.name + SEC.muscle + SEC.howto + SEC.outro; // 498

const EASE = Easing.bezier(0.16, 1, 0.3, 1);

// セクションの出入りフェード（各Sequenceのローカルframe基準）
const useFade = (len: number) => {
  const f = useCurrentFrame();
  return interpolate(f, [0, 12, len - 12, len], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};
// 少し下から上がってくる
const useRise = (len: number) => {
  const f = useCurrentFrame();
  return interpolate(f, [0, 16], [26, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE });
};

const Label: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ fontSize: 34, fontWeight: 700, letterSpacing: 4, color: "#ffd9e6" }}>{children}</div>
);

const lowerBase: React.CSSProperties = {
  position: "absolute",
  left: 70,
  right: 70,
  bottom: 140,
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  textAlign: "center",
  gap: 14,
};

const NameSection: React.FC<{ name: string; category: string; equipment: string }> = ({
  name,
  category,
  equipment,
}) => {
  const opacity = useFade(SEC.name);
  const y = useRise(SEC.name);
  return (
    <div style={{ ...lowerBase, opacity, translate: `0px ${y}px` }}>
      <Label>本日のトレーニング</Label>
      <div style={{ fontSize: 92, fontWeight: 900, color: "#fff", lineHeight: 1.15, textShadow: "0 4px 24px rgba(0,0,0,0.5)" }}>
        {name}
      </div>
      <div style={{ fontSize: 40, fontWeight: 700, color: "#fff" }}>
        {category}　/　{equipment}
      </div>
    </div>
  );
};

const MuscleSection: React.FC<{ muscles: string[] }> = ({ muscles }) => {
  const opacity = useFade(SEC.muscle);
  const y = useRise(SEC.muscle);
  return (
    <div style={{ ...lowerBase, opacity, translate: `0px ${y}px` }}>
      <Label>鍛える部位</Label>
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 16 }}>
        {muscles.map((m) => (
          <span
            key={m}
            style={{
              fontSize: 44,
              fontWeight: 700,
              color: "#fff",
              background: "rgba(244,63,94,0.85)",
              borderRadius: 999,
              padding: "10px 28px",
            }}
          >
            {m}
          </span>
        ))}
      </div>
    </div>
  );
};

const HowToSection: React.FC<{ sets: number; reps: string; rest: number; desc: string }> = ({
  sets,
  reps,
  rest,
  desc,
}) => {
  const opacity = useFade(SEC.howto);
  const y = useRise(SEC.howto);
  return (
    <div style={{ ...lowerBase, opacity, translate: `0px ${y}px` }}>
      <Label>やり方</Label>
      <div style={{ fontSize: 78, fontWeight: 900, color: "#fff", textShadow: "0 4px 24px rgba(0,0,0,0.5)" }}>
        {sets}セット<span style={{ color: "#ffd9e6" }}> × </span>{reps}
      </div>
      <div style={{ fontSize: 38, fontWeight: 700, color: "#fff" }}>セット間の休憩 {rest}秒</div>
      <div style={{ fontSize: 40, fontWeight: 400, color: "#fff", lineHeight: 1.5, maxWidth: 900 }}>{desc}</div>
    </div>
  );
};

const OutroSection: React.FC = () => {
  const opacity = useFade(SEC.outro);
  const y = useRise(SEC.outro);
  return (
    <div style={{ ...lowerBase, opacity, translate: `0px ${y}px` }}>
      <div style={{ fontSize: 60, fontWeight: 900, color: "#fff", textShadow: "0 4px 24px rgba(0,0,0,0.5)" }}>
        競技別トレーニング
      </div>
      <div style={{ fontSize: 30, color: "rgba(255,255,255,0.85)", lineHeight: 1.55, maxWidth: 820 }}>
        ※回数・重量などの数値は目安です。医療的助言ではありません。無理のない範囲で行ってください。
      </div>
    </div>
  );
};

export const ExerciseVideo: React.FC<ExerciseVideoProps> = ({ exerciseId }) => {
  const exercise = getExercise(exerciseId);
  const frame = useCurrentFrame();

  // ゆっくりズーム（Ken Burns）で一枚絵に生命感を出す
  const scale = interpolate(frame, [0, TOTAL_FRAMES], [1.04, 1.14], { extrapolateRight: "clamp" });
  const drift = interpolate(frame, [0, TOTAL_FRAMES], [0, -26], { extrapolateRight: "clamp" });

  let at = 0;
  const next = (len: number) => {
    const from = at;
    at += len;
    return { from, durationInFrames: len };
  };

  return (
    <AbsoluteFill style={{ fontFamily, background: "#1b1020" }}>
      {/* 背景：案内役キャラの一枚絵（ゆっくりズーム） */}
      <AbsoluteFill style={{ scale: String(scale), translate: `0px ${drift}px` }}>
        <Img src={staticFile("trainer.png")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>

      {/* 桜吹雪 */}
      <SakuraPetals />

      {/* 下部を暗くして文字を読みやすくするスクリム */}
      <AbsoluteFill
        style={{
          background: "linear-gradient(180deg, rgba(10,8,20,0) 45%, rgba(10,8,20,0.5) 66%, rgba(10,8,20,0.86) 100%)",
        }}
      />

      {/* 上部のブランドチップ（常時） */}
      <div
        style={{
          position: "absolute",
          top: 70,
          left: 70,
          display: "flex",
          alignItems: "center",
          gap: 14,
          padding: "12px 22px",
          borderRadius: 999,
          background: "rgba(255,255,255,0.16)",
        }}
      >
        <div style={{ width: 30, height: 30, borderRadius: 9, background: COLORS.indigo, display: "grid", placeItems: "center" }}>
          <svg viewBox="0 0 24 24" width={18} height={18} fill="none" stroke="#fff" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
            <path d="M6.5 6.5v11M17.5 6.5v11M4 9v6M20 9v6M6.5 12h11" />
          </svg>
        </div>
        <span style={{ fontSize: 30, fontWeight: 700, color: "#fff" }}>競技別トレーニング</span>
      </div>

      {/* 下部テロップ（セクション切り替え） */}
      <Sequence {...next(SEC.name)} layout="none">
        <NameSection name={exercise.name_ja} category={exercise.category} equipment={exercise.equipment} />
      </Sequence>
      <Sequence {...next(SEC.muscle)} layout="none">
        <MuscleSection muscles={exercise.target_muscles} />
      </Sequence>
      <Sequence {...next(SEC.howto)} layout="none">
        <HowToSection sets={exercise.default_sets} reps={exercise.default_reps} rest={exercise.rest_seconds} desc={exercise.description} />
      </Sequence>
      <Sequence {...next(SEC.outro)} layout="none">
        <OutroSection />
      </Sequence>
    </AbsoluteFill>
  );
};
