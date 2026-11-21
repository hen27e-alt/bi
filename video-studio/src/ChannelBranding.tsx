import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  OffthreadVideo,
  spring,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
} from "remotion";
import { getTheme, type GenreTheme } from "./themes";

// ── Props ─────────────────────────────────────────────────────────────────────
export interface ChannelBrandingProps {
  src: string;
  artist: string;
  song: string;
  year: string;
  genre: string;
  themeKey: string;
  durationInFrames: number;
}

// ── Intro duration (frames) ───────────────────────────────────────────────────
const INTRO_FRAMES = 90;   // 3s
const FADE_FRAMES  = 15;   // 0.5s crossfade

// ── Logo badge (top-left, persistent) ────────────────────────────────────────
const LogoBadge: React.FC<{ theme: GenreTheme; small?: boolean }> = ({ theme, small }) => {
  const size = small ? 0.65 : 1;
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 10 * size,
      background: "rgba(10,10,10,0.88)",
      borderRadius: 14 * size,
      padding: `${10 * size}px ${16 * size}px`,
      backdropFilter: "blur(6px)",
      border: `1.5px solid rgba(255,255,255,0.08)`,
    }}>
      {/* Amber accent strip with VHS icon */}
      <div style={{
        width: 36 * size, height: 48 * size,
        background: theme.accent,
        borderRadius: 8 * size,
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center", gap: 3 * size,
      }}>
        {/* Cassette body */}
        <div style={{
          width: 22 * size, height: 14 * size,
          background: "rgba(10,10,10,0.9)",
          borderRadius: 2 * size,
          display: "flex", alignItems: "center", justifyContent: "space-around",
          padding: `2px ${3 * size}px`,
        }}>
          <div style={{ width: 6*size, height: 6*size, borderRadius: "50%", background: theme.accent }} />
          <div style={{ width: 6*size, height: 6*size, borderRadius: "50%", background: theme.accent }} />
        </div>
        <div style={{ width: 14*size, height: 2*size, background: "rgba(10,10,10,0.7)", borderRadius: 1 }} />
      </div>

      {/* Text block */}
      <div style={{ display: "flex", flexDirection: "column" }}>
        <span style={{
          fontFamily: "'Inter', sans-serif",
          fontWeight: 900, fontSize: 28 * size,
          color: theme.accent, lineHeight: 1,
          letterSpacing: "-0.5px",
          textShadow: theme.textShadow,
        }}>RP</span>
        <span style={{
          fontFamily: "'Heebo', sans-serif",
          fontWeight: 400, fontSize: 11 * size,
          color: "rgba(220,215,205,0.85)",
          lineHeight: 1.2, direction: "rtl",
          marginTop: 2 * size,
        }}>חזרה לעבר</span>
      </div>
    </div>
  );
};

// ── Intro card ────────────────────────────────────────────────────────────────
const IntroCard: React.FC<{ theme: GenreTheme; artist: string; song: string; year: string; opacity: number }> = (
  { theme, artist, song, year, opacity }
) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();

  const logoScale = spring({ frame, fps, config: { damping: 14, mass: 0.8 }, durationInFrames: 25 });
  const textY     = interpolate(frame, [15, 45], [40, 0], { extrapolateRight: "clamp" });
  const textOp    = interpolate(frame, [15, 45], [0, 1],  { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{
      opacity,
      background: `radial-gradient(ellipse at 50% 40%, ${theme.glow.replace("0.5", "0.35")} 0%, ${theme.secondary} 70%, #000 100%)`,
      alignItems: "center", justifyContent: "center", flexDirection: "column",
    }}>
      {/* Top glow bar */}
      <div style={{
        position: "absolute", top: 0, left: 0, right: 0, height: 3,
        background: `linear-gradient(90deg, transparent, ${theme.accent}, transparent)`,
        opacity: 0.8,
      }} />

      {/* Logo */}
      <div style={{ transform: `scale(${logoScale})`, marginBottom: 48 }}>
        <LogoBadge theme={theme} />
      </div>

      {/* Channel name large */}
      <div style={{
        fontFamily: "'Heebo', sans-serif",
        fontWeight: 900, fontSize: 72,
        color: "white", letterSpacing: "-1px",
        direction: "rtl", textAlign: "center",
        textShadow: "0 4px 30px rgba(0,0,0,0.6)",
        transform: `translateY(${textY * 0.3}px)`,
        opacity: textOp,
      }}>חזרה לעבר</div>

      {/* Accent divider */}
      <div style={{
        width: 160, height: 2,
        background: `linear-gradient(90deg, transparent, ${theme.accent}, transparent)`,
        margin: "20px 0",
        opacity: textOp,
        transform: `translateY(${textY}px)`,
      }} />

      {/* Artist + song info */}
      <div style={{
        display: "flex", flexDirection: "column", alignItems: "center", gap: 10,
        opacity: textOp, transform: `translateY(${textY * 1.2}px)`,
      }}>
        <div style={{
          fontFamily: "'Inter', sans-serif", fontWeight: 800,
          fontSize: 48, color: "white",
          textTransform: "uppercase", letterSpacing: "2px",
        }}>{artist}</div>

        <div style={{
          fontFamily: "'Heebo', sans-serif", fontStyle: "italic",
          fontSize: 32, color: "rgba(220,215,205,0.9)",
        }}>{song}</div>

        {/* Year badge */}
        <div style={{
          background: theme.accent, color: "#000",
          fontFamily: "'Inter', sans-serif", fontWeight: 900,
          fontSize: 22, padding: "4px 20px", borderRadius: 6,
          marginTop: 4,
        }}>{year}</div>
      </div>

      {/* Bottom glow bar */}
      <div style={{
        position: "absolute", bottom: 0, left: 0, right: 0, height: 3,
        background: `linear-gradient(90deg, transparent, ${theme.accent}, transparent)`,
        opacity: 0.8,
      }} />
    </AbsoluteFill>
  );
};

// ── Video overlay (persistent branding on top of footage) ────────────────────
const VideoOverlay: React.FC<{
  theme: GenreTheme; artist: string; song: string; year: string; opacity: number
}> = ({ theme, artist, song, year, opacity }) => (
  <AbsoluteFill style={{ opacity, pointerEvents: "none" }}>
    {/* Top gradient */}
    <div style={{
      position: "absolute", top: 0, left: 0, right: 0, height: 180,
      background: "linear-gradient(to bottom, rgba(0,0,0,0.75) 0%, transparent 100%)",
    }} />

    {/* Logo top-left */}
    <div style={{ position: "absolute", top: 20, left: 20 }}>
      <LogoBadge theme={theme} small />
    </div>

    {/* Bottom gradient card */}
    <div style={{
      position: "absolute", bottom: 0, left: 0, right: 0, height: 260,
      background: "linear-gradient(to top, rgba(0,0,0,0.92) 0%, rgba(0,0,0,0.6) 60%, transparent 100%)",
    }} />

    {/* Bottom info card content */}
    <div style={{
      position: "absolute", bottom: 40, left: 24, right: 24,
    }}>
      {/* NOW PLAYING label + accent line */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
        <div style={{ width: 100, height: 2, background: theme.accent, opacity: 0.8 }} />
        <span style={{
          fontFamily: "'Inter', sans-serif", fontWeight: 700,
          fontSize: 11, color: theme.accent,
          letterSpacing: "2.5px", textTransform: "uppercase",
          opacity: 0.9,
        }}>NOW PLAYING</span>
      </div>

      {/* Artist */}
      <div style={{
        fontFamily: "'Inter', sans-serif", fontWeight: 900,
        fontSize: 42, color: "white",
        textTransform: "uppercase", letterSpacing: "1px",
        lineHeight: 1.1, marginBottom: 6,
        textShadow: "0 2px 20px rgba(0,0,0,0.8)",
      }}>{artist}</div>

      {/* Song title */}
      <div style={{
        fontFamily: "'Heebo', sans-serif", fontStyle: "italic",
        fontSize: 26, color: "rgba(220,215,205,0.88)",
        marginBottom: 14,
      }}>{song}</div>

      {/* Year + genre */}
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <div style={{
          background: "#CC1A1A", color: "white",
          fontFamily: "'Inter', sans-serif", fontWeight: 900,
          fontSize: 18, padding: "4px 14px", borderRadius: 5,
        }}>{year}</div>
        <span style={{
          fontFamily: "'Inter', sans-serif",
          fontSize: 15, color: "rgba(200,195,185,0.75)",
        }}>{/* genre label is handled by parent */}</span>
      </div>
    </div>

    {/* Corner vignette */}
    <div style={{
      position: "absolute", inset: 0,
      background: "radial-gradient(ellipse at 50% 50%, transparent 55%, rgba(0,0,0,0.5) 100%)",
    }} />
  </AbsoluteFill>
);

// ── Main composition ──────────────────────────────────────────────────────────
export const ChannelBranding: React.FC<ChannelBrandingProps> = ({
  src, artist, song, year, genre, themeKey, durationInFrames,
}) => {
  const frame  = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme   = getTheme(themeKey || "default");

  // Intro fades out at INTRO_FRAMES → INTRO_FRAMES + FADE_FRAMES
  const introOp = interpolate(
    frame,
    [INTRO_FRAMES - FADE_FRAMES, INTRO_FRAMES],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Video + overlay fade in at INTRO_FRAMES - FADE_FRAMES
  const videoOp = interpolate(
    frame,
    [INTRO_FRAMES - FADE_FRAMES, INTRO_FRAMES],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const showVideo = frame >= INTRO_FRAMES - FADE_FRAMES;

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {/* ── Intro card ── */}
      {frame < INTRO_FRAMES && (
        <IntroCard
          theme={theme}
          artist={artist}
          song={song}
          year={year}
          opacity={introOp}
        />
      )}

      {/* ── Video + overlay ── */}
      {showVideo && (
        <>
          <AbsoluteFill style={{ opacity: videoOp }}>
            <OffthreadVideo
              src={src}
              startFrom={0}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          </AbsoluteFill>
          <VideoOverlay
            theme={theme}
            artist={artist}
            song={song}
            year={year}
            opacity={videoOp}
          />
        </>
      )}
    </AbsoluteFill>
  );
};
