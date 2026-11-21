import React from "react";
import {
  AbsoluteFill,
  OffthreadVideo,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";

export type Caption = {
  text: string;
  startFrame: number;
  endFrame: number;
};

type Props = {
  src: string;
  captions: Caption[];
  style: "reels" | "youtube";
  aspectRatio: "9:16" | "16:9";
};

const HEBREW_FONTS = `
  @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@700;900&display=swap');
`;

export const CaptionedVideo: React.FC<Props> = ({
  src,
  captions,
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const activeCaption = captions.find(
    (c) => frame >= c.startFrame && frame <= c.endFrame
  );

  const captionProgress =
    activeCaption
      ? spring({
          fps,
          frame: frame - activeCaption.startFrame,
          config: { damping: 12, stiffness: 200, mass: 0.5 },
        })
      : 0;

  const scale = interpolate(captionProgress, [0, 1], [0.85, 1]);
  const opacity = interpolate(captionProgress, [0, 1], [0, 1]);

  const isReels = style === "reels";

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <style>{HEBREW_FONTS}</style>
      {src ? (
        <OffthreadVideo src={src} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      ) : null}
      {activeCaption && (
        <AbsoluteFill
          style={{
            justifyContent: "flex-end",
            alignItems: "center",
            paddingBottom: isReels ? "18%" : "10%",
          }}
        >
          <div
            style={{
              direction: "rtl",
              textAlign: "center",
              fontFamily: "'Heebo', sans-serif",
              fontWeight: 900,
              fontSize: isReels ? 72 : 56,
              color: "#fff",
              textShadow: "0 4px 24px rgba(0,0,0,0.9), 0 2px 8px rgba(0,0,0,0.8)",
              backgroundColor: isReels
                ? "rgba(0,0,0,0.55)"
                : "rgba(0,0,0,0.65)",
              padding: "16px 32px",
              borderRadius: 16,
              maxWidth: "90%",
              lineHeight: 1.3,
              transform: `scale(${scale})`,
              opacity,
              letterSpacing: isReels ? 1 : 0.5,
            }}
          >
            {activeCaption.text}
          </div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
