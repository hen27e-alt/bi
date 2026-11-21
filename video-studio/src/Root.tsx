import { Composition } from "remotion";
import { CaptionedVideo } from "./CaptionedVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="CaptionedVideo"
        component={CaptionedVideo}
        durationInFrames={300}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          src: "",
          captions: [],
          style: "reels",
          aspectRatio: "9:16",
        }}
      />
      <Composition
        id="CaptionedVideoWide"
        component={CaptionedVideo}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          src: "",
          captions: [],
          style: "youtube",
          aspectRatio: "16:9",
        }}
      />
    </>
  );
};
