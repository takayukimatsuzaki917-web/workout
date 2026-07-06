// 桜の花びらが舞い散る演出。フレームから各花びらの位置を決定的に計算する。
import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";

const COLORS = ["#f7c1d4", "#f9a8c4", "#ffd6e6", "#f4b6c8", "#fbc7d8"];

// 決定的な擬似乱数（seed から 0..1）
const rand = (i: number, salt: number) => {
  const x = Math.sin(i * 12.9898 + salt * 78.233) * 43758.5453;
  return x - Math.floor(x);
};

export const SakuraPetals: React.FC<{ count?: number }> = ({ count = 26 }) => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();
  const t = frame / fps;

  return (
    <>
      {new Array(count).fill(0).map((_, i) => {
        const size = 16 + rand(i, 1) * 26;
        const startX = rand(i, 2) * width;
        const fallSec = 6 + rand(i, 3) * 5; // 落下にかかる秒数
        const delay = rand(i, 4) * fallSec;
        const swayAmp = 24 + rand(i, 5) * 46;
        const swayFreq = 0.4 + rand(i, 6) * 0.8;
        const rotSpeed = 40 + rand(i, 7) * 120;
        const color = COLORS[Math.floor(rand(i, 8) * COLORS.length)];

        const prog = ((t + delay) % fallSec) / fallSec; // 0..1
        const y = prog * (height + 120) - 60;
        const x = startX + Math.sin((t + delay) * swayFreq * Math.PI + i) * swayAmp;
        const rot = (t + delay) * rotSpeed;
        const opacity = 0.55 + rand(i, 9) * 0.4;

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: 0,
              top: 0,
              width: size,
              height: size * 0.72,
              background: color,
              borderRadius: "60% 60% 60% 4%",
              opacity,
              translate: `${x}px ${y}px`,
              rotate: `${rot}deg`,
              filter: "drop-shadow(0 1px 1px rgba(0,0,0,0.05))",
            }}
          />
        );
      })}
    </>
  );
};
