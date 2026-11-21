# מפעל עריכת וידאו אוטומטי

## סביבה
- Python venv: `.venv/` — הרץ תמיד עם `.venv/bin/python` ו-`.venv/bin/auto-editor`
- Node: `video-studio/` — Remotion 4.x, `npm run render` לייצוא
- FFmpeg: מותקן ברמת המערכת
- MCP: `.mcp.json` מגדיר שרת `ffmpeg` (mcp-ffmpeg) לכלי עיבוד וידאו מובנים

## תיקיות
```
input/    ← קבצי וידאו גולמיים (MP4/MOV/MKV)
temp/     ← קבצי ביניים (ניקוי שתיקות, נרמול אודיו, JSON תמלול)
output/   ← תוצרים סופיים
video-studio/  ← פרויקט Remotion עם כתוביות ואנימציות
```

## פרוטוקול עריכה אוטומטי

### שאלה חובה לפני כל עיבוד
בכל בקשת עריכה מ-`input/`, שאל תמיד שתי שאלות:
1. **פורמט**: 9:16 (ורטיקל - ריילס/טיקטוק/שורטס) או 16:9 (רחב - יוטיוב/פרזנטציה)?
2. **סגנון כתוביות**: ריילס/טיקטוק (מילים בודדות גדולות, קצב גבוה) או יוטיוב (שורות מלאות, קריאה נוחה)?

### צינור עיבוד (Pipeline)

#### שלב 1 — ניקוי שתיקות (auto-editor)
```bash
.venv/bin/auto-editor input/VIDEO.mp4 \
  --edit audio:threshold=4% \
  --output-file temp/VIDEO_cut.mp4 \
  --no-open
```

#### שלב 2 — נרמול אודיו ל-14- LUFS (FFmpeg two-pass)
```bash
# מדידה
ffmpeg -i temp/VIDEO_cut.mp4 -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 | tail -20

# יישום עם ערכים שנמדדו (החלף measured_* בפועל)
ffmpeg -i temp/VIDEO_cut.mp4 \
  -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=MEASURED_I:measured_TP=MEASURED_TP:measured_LRA=MEASURED_LRA:measured_thresh=MEASURED_THRESH:offset=OFFSET:linear=true" \
  -c:v copy \
  temp/VIDEO_norm.mp4
```

#### שלב 3 — תמלול עברית ברמת המילה (faster-whisper)
```python
# .venv/bin/python scripts/transcribe.py temp/VIDEO_norm.mp4
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cpu", compute_type="int8")
segments, _ = model.transcribe(
    "temp/VIDEO_norm.mp4",
    language="he",
    word_timestamps=True,
    vad_filter=True,
)

# מייצר temp/VIDEO_words.json עם { text, start, end } לכל מילה
```

#### שלב 4 — בניית כתוביות + Remotion render
```bash
# המרת words.json לפורמט Remotion captions
.venv/bin/python scripts/build_captions.py \
  temp/VIDEO_words.json \
  --style reels|youtube \
  --fps 30 \
  > video-studio/src/captions.json

# Render
cd video-studio && npx remotion render \
  src/index.ts \
  CaptionedVideo \           # או CaptionedVideoWide ל-16:9
  ../output/VIDEO_final.mp4 \
  --props '{"src":"../temp/VIDEO_norm.mp4","captionsFile":"src/captions.json","style":"reels","aspectRatio":"9:16"}'
```

## כללי איכות
- **עברית RTL**: תמיד `direction: rtl` ופונט Heebo (מותקן ב-Remotion)
- **כתוביות ריילס**: מקסימום 3 מילים בשורה, גופן 72px+, אנימציית spring
- **כתוביות יוטיוב**: מקסימום 38 תווים לשורה, גופן 56px, 2 שורות מקסימום
- **משך כתובית**: מינימום 1.2 שניות, מקסימום 6 שניות
- **פלט**: H.264 CRF 18 למקסימום איכות, AAC 192kbps

## כלי MCP נוספים
שרת `ffmpeg` ב-`.mcp.json` מספק כלים מובנים לפעולות FFmpeg ישירות — השתמש בהם לחיתוך, הסקת מידע, וקידוד.

## הוראות אוטומציה
- כשמוצאים קבצים ב-`input/` → שאל פורמט+סגנון → הרץ pipeline מלא
- אל תשאל שאלות ביניים — הרץ כל שלב עד הסוף
- כל קובץ ביניים ל-`temp/`, רק תוצר סופי ל-`output/`
- דווח על כל שלב עם זמן ריצה וגודל קובץ

---

## ערוץ "חזרה לעבר" — פרוטוקול בקשת שיר

### זיהוי בקשה אוטומטי
כל הודעה שמכילה **שם זמר + שם שיר** (עם או בלי שנה/ג'אנר) מפעילה את הזרימה הזו.
לא צריך פקודה מפורשת — גם "תעשה סרטון על Thriller של מייקל ג'קסון" מספיק.

### שלבי הזרימה (הפעל בסדר)

#### שלב 0 — פרמטרים
חלץ מההודעה (ואם חסר, שאל שאלה אחת בלבד):
| פרמטר | חובה | ברירת מחדל |
|--------|------|------------|
| `--artist` | כן | — |
| `--song` | כן | — |
| `--year` | לא | שנה ידועה / "?" |
| `--genre` | לא | "pop" |
| `--source` | לא | ריק (nnSUאנסה הורדה) |
| `--clip-start` | לא | 0 |
| `--clip-duration` | לא | 30 |

#### שלב 1 — הרץ pipeline מלא
```bash
.venv/bin/python scripts/channel_video.py \
  --artist "ARTIST" --song "SONG" --year YEAR --genre "GENRE" \
  [--source input/FILE.mp4] [--clip-start SEC] [--clip-duration SEC]
```

הסקריפט מבצע **אוטומטית**:
1. חיפוש קובץ מקומי ב-`input/` → הורדת yt-dlp אם לא קיים
2. חיתוך קטע (`--clip-start` / `--clip-duration`)
3. ניקוי שתיקות (auto-editor)
4. נרמול אודיו (-14 LUFS, FFmpeg two-pass)
5. Remotion render של `ChannelBranding` (9:16, 1080×1920)
6. ייצוא ל-`output/{artist}_{song}_final.mp4`

#### טיפול בחסימת הורדה
אם yt-dlp נחסם (429/bot-detection/timeout):
- הסבר קצר (שורה אחת)
- בקש: "שים קובץ ב-`input/` ואציין `--source`"
- אל תנסה שוב ללא מקור חדש

### ערכת הז'אנרים (`video-studio/src/themes.ts`)
| מפתח | ג'אנר | אקסנט | עידן |
|------|-------|-------|------|
| `jazz` | Jazz | זהב | שנות ה-40–50 |
| `blues` | Blues | כחול | שנות ה-50–60 |
| `rock` | Rock | אדום | שנות ה-60–70 |
| `funk` | Funk/Soul | ענבר | שנות ה-70–80 |
| `disco` | Disco | זהב ניאון | שנות ה-70 |
| `pop_80s` | Pop | ורוד ניאון | שנות ה-80 |
| `synth` | Synth/Electronic | טורקיז | שנות ה-80 |
| `new_wave` | New Wave | סגול | שנות ה-80 |
| `hip_hop` | Hip-Hop | זהב | שנות ה-90 |
| `grunge` | Grunge/Alt | ירוק-אפור | שנות ה-90 |
| `rnb` | R&B | סגול | שנות ה-90–2000 |
| `default` | כל השאר | ענבר (#F5A800) | — |

### Remotion compositions
| ID | תיאור |
|----|-------|
| `ChannelBranding` | סרטון ערוץ 9:16: כרטיס פתיחה (3s) + וידאו + שכבת מיתוג |
| `CaptionedVideo` | כתוביות ריילס/טיקטוק 9:16 |
| `CaptionedVideoWide` | כתוביות יוטיוב 16:9 |

### render ידני (ללא סקריפט)
```bash
cd video-studio && npx remotion render src/index.ts ChannelBranding \
  ../output/OUTPUT.mp4 \
  --props '{"src":"../temp/NORM.mp4","artist":"NAME","song":"TITLE","year":"1980","genre":"rock","themeKey":"rock","durationInFrames":900}'
```
