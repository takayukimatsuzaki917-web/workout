import "./index.css";
import { Composition } from "remotion";
import { ExerciseVideo, TOTAL_FRAMES } from "./ExerciseVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ExerciseVideo"
        component={ExerciseVideo}
        durationInFrames={TOTAL_FRAMES}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ exerciseId: "squat_barbell" }}
      />
    </>
  );
};
