import React from "react";
import { Composition } from "remotion";
import { CaptionedVideo } from "./CaptionedVideo";
import { ChannelBranding } from "./ChannelBranding";
import type { ChannelBrandingProps } from "./ChannelBranding";

const defaultBrandingProps: ChannelBrandingProps = {
  src: "",
  artist: "Artist Name",
  song: "Song Title",
  year: "1980",
  genre: "pop",
  themeKey: "default",
  durationInFrames: 900,
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* ── Channel "חזרה לעבר" — per-song branding (9:16 TikTok) ── */}
      <Composition
        id="ChannelBranding"
        component={ChannelBranding as unknown as React.ComponentType<Record<string, unknown>>}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={defaultBrandingProps as unknown as Record<string, unknown>}
        calculateMetadata={({ props }) => {
          const p = props as unknown as ChannelBrandingProps;
          return { durationInFrames: p.durationInFrames ?? 900, fps: 30 };
        }}
      />

      {/* ── Captioned subtitle overlays ── */}
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
