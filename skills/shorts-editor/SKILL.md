---
name: shorts-editor
version: "1.0.5"
displayName: "Shorts Editor — AI Video Editor for YouTube Shorts TikTok and Instagram Reels"
description: >
  Edit short-form vertical videos with AI — trim, cut, add captions, transitions, music, effects, text overlays, and speed changes for YouTube Shorts, TikTok, and Instagram Reels. NemoVideo edits raw footage into polished short-form content: remove dead air, add word-by-word captions, sync cuts to music beats, apply zoom effects, insert hook text, color grade for mobile screens, and export platform-ready vertical video. The complete editing workflow for short-form creators — described in words, executed by AI. Shorts editor online, edit Shorts with AI, TikTok editor, Reels editor, vertical video editor, short form video editor free, edit videos for Shorts.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Shorts Editor — Raw Footage to Platform-Ready in One Description

Short-form editing has its own grammar. It is not long-form editing compressed into 60 seconds — it is a fundamentally different discipline with different rules: every second must earn its place (no slow starts, no filler, no natural pauses), visual changes must happen every 2-4 seconds (the human attention span on vertical feeds is measured in moments), the first frame must stop the scroll (a split-second decision by the viewer determines the video's fate), captions are the primary content delivery for the sound-off majority, and music is not background — it is structural (beats define cut timing, drops define emphasis, energy level defines pacing). Editing software designed for long-form content — timelines, keyframes, layer stacks, effect panels — is overkill for Shorts and yet simultaneously inadequate. Overkill because a 30-second Short does not need a 47-track timeline. Inadequate because the software does not understand short-form grammar: it does not know that captions should be word-by-word animated, that cuts should land on beats, that hooks belong in the first frame, or that vertical safe zones differ by platform. NemoVideo understands short-form grammar natively. Describe the edit and every short-form convention is applied: silence removal, attention-maintaining zoom cuts, word-by-word caption animation, beat-synced transitions, hook frame insertion, platform-safe text positioning, and duration targeting for algorithmic optimization.

## Use Cases

1. **Talking-Head Polish — Raw to Viral (15-60s)** — A creator records 3 minutes of talking into their phone. The content is good but the delivery is raw: pauses, ums, false starts, flat energy in places. NemoVideo: removes all silences over 0.6 seconds (tightens pacing by 30-40%%), cuts the "ums" and false starts, selects the strongest 35-second segment, applies zoom-cuts every 4 seconds (100%/115% alternating — creates visual energy from a static camera), adds word-by-word captions (white bold, accent color highlight, dark pill background), inserts hook text in the first frame, overlays lo-fi music at -22dB with speech ducking, and exports at exactly 35 seconds for the Shorts algorithm sweet spot. Unpolished phone footage becomes a professional Short.
2. **Multi-Clip Assembly — Best Moments Compilation (15-55s)** — A food creator has 12 short clips from a cooking session: chopping, sizzling, plating, tasting. NemoVideo: selects the most visually appealing moment from each clip (2-4 seconds per clip), arranges by cooking workflow (prep → cook → plate → taste), applies smooth transitions synced to upbeat music beats, color grades for food content (warm saturation, enhanced oranges and greens), adds ingredient text overlays on each prep clip, and creates a 45-second cooking Short that makes viewers hungry. Twelve scattered clips become one compelling story.
3. **Repurpose Long-Form — Extract the Best Short (15-55s)** — A podcaster has a 45-minute episode and needs 3 Shorts extracted from it. NemoVideo: transcribes the full episode, identifies the 3 most quotable/insightful moments (based on information density, emotional peaks, and hook potential), extracts each as a standalone clip, reframes to 9:16 vertical with speaker face tracking, adds word-by-word captions, inserts hook text per clip (generated from the clip's content), and exports all 3 as individual Shorts. Three pieces of viral-potential content from one long recording.
4. **Speed Edit — Velocity Effects for Gaming/Action (15-45s)** — A gaming creator has a highlight clip that needs the velocity edit treatment: fast-forward through setup, snap to slow-mo on the kill. NemoVideo: accelerates low-action segments (3-4x), snaps to slow-mo at peak moments (0.2x), returns to normal speed between highlights, syncs the speed changes to music beat structure, applies zoom effect at each slow-mo moment, adds impact sound effects, and overlays kill counter and game context text. The "velocity edit" style that dominates gaming Shorts content.
5. **Batch Edit — Weekly Content Production (multiple)** — A brand needs 7 Shorts for the week: 3 talking-head tips, 2 product showcases, 2 behind-the-scenes clips. NemoVideo: batch-processes all 7 with consistent branding (same caption style, color grade, music genre, intro/outro format) but varied editing style per content type (zoom-cuts for talking head, smooth transitions for product, handheld energy for BTS). A full week of platform-ready Shorts from one editing session.

## How It Works

### Step 1 — Upload Raw Footage
Single clip or multiple clips. Phone footage, camera footage, screen recording, or extracted segment from long-form content.

### Step 2 — Describe the Edit
Plain language: "Remove the pauses, add captions, put music, make it 30 seconds for TikTok." Or detailed: specify exact edits, timing, styles, and effects.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "shorts-editor",
    "prompt": "Edit a raw 2-minute talking-head clip into a 35-second YouTube Short. Remove all silences over 0.6s. Remove ums and false starts. Zoom-cuts every 4 sec (100%%/115%% alternating). Word-by-word captions: white bold #FFFFFF, highlight #FFD700 gold, dark pill bg, bottom center, large. Hook: first frame text — This one habit will change your mornings (white on dark, 1.2s). Music: chill lo-fi at -22dB with speech ducking. Color: warm-clean. CTA: last 2s — Follow for more ✨. Export for YouTube Shorts + TikTok + Reels.",
    "edits": {
      "silence_removal": 0.6,
      "um_removal": true,
      "zoom_cuts": {"interval": 4, "range": "100-115"},
      "target_duration": 35
    },
    "captions": {"style": "word-highlight", "text": "#FFFFFF", "highlight": "#FFD700", "bg": "pill-dark", "position": "bottom-center", "size": "large"},
    "hook": {"text": "This one habit will change your mornings", "duration": 1.2},
    "music": {"style": "chill-lofi", "volume": "-22dB", "ducking": true},
    "cta": {"text": "Follow for more ✨", "duration": 2},
    "color_grade": "warm-clean",
    "platforms": ["shorts", "tiktok", "reels"]
  }'
```

### Step 4 — Preview and Post
Check: pacing feels tight (no dead air), captions sync perfectly, hook stops the scroll, music complements without competing. Download all platform versions and post.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Edit instructions in plain language |
| `edits` | object | | {silence_removal, um_removal, zoom_cuts, target_duration} |
| `captions` | object | | {style, text, highlight, bg, position, size} |
| `hook` | object | | {text, duration} — first-frame scroll stopper |
| `cta` | object | | {text, duration} — ending call to action |
| `music` | object | | {style, volume, ducking} |
| `transitions` | string | | "smooth-zoom", "whip-pan", "cut", "beat-synced" |
| `speed` | object | | {segments: [{start, end, speed}]} for velocity edits |
| `color_grade` | string | | "warm-clean", "vibrant", "moody", "cool" |
| `platforms` | array | | ["shorts", "tiktok", "reels"] |
| `batch` | array | | Multiple videos in one request |

## Output Example

```json
{
  "job_id": "se-20260328-001",
  "status": "completed",
  "source_duration": "2:05",
  "edited_duration": "0:35",
  "edits_applied": {
    "silences_removed": "0:48 (23 cuts)",
    "ums_removed": 7,
    "zoom_cuts": 9,
    "hook": "This one habit will change your mornings (1.2s)",
    "cta": "Follow for more ✨ (2s)",
    "captions": "word-highlight (white + #FFD700 gold)",
    "music": "chill lo-fi at -22dB with ducking",
    "color_grade": "warm-clean"
  },
  "outputs": {
    "shorts": {"file": "morning-habit-shorts.mp4", "resolution": "1080x1920"},
    "tiktok": {"file": "morning-habit-tiktok.mp4", "resolution": "1080x1920"},
    "reels": {"file": "morning-habit-reels.mp4", "resolution": "1080x1920"}
  }
}
```

## Tips

1. **Silence removal is the single biggest upgrade to raw talking-head footage** — Natural speech contains 20-35%% dead air. Removing pauses over 0.6 seconds instantly creates the fast-paced delivery that short-form audiences expect without making the speaker sound unnaturally rushed.
2. **Zoom-cuts create visual energy from a single static camera angle** — Alternating between 100%% and 110-120%% zoom every 3-5 seconds simulates a multi-camera setup. The subtle visual change resets viewer attention at every cut. Free production value.
3. **Beat-synced cuts make amateur edits feel professional** — When transitions land on musical beats, the edit feels rhythmic and intentional. When cuts happen at random intervals, the edit feels choppy. Music-driven editing is the difference between "nice video" and "who edited this?"
4. **35 seconds is the sweet spot for Shorts** — Long enough to deliver value, short enough to get replayed. YouTube Shorts algorithm rewards completion rate — a 35-second video that gets watched to the end outperforms a 60-second video that gets abandoned at 40 seconds.
5. **Batch editing with consistent branding builds recognizable channels** — When every Short has the same caption style, color grade, and music genre, viewers develop brand recognition. After seeing 3-4 Shorts with the same visual style, they recognize the creator's content in the feed before reading the username.

## Output Formats

| Format | Resolution | Platform |
|--------|-----------|----------|
| MP4 9:16 | 1080x1920 | YouTube Shorts |
| MP4 9:16 | 1080x1920 | TikTok |
| MP4 9:16 | 1080x1920 | Instagram Reels |
| MP4 1:1 | 1080x1080 | Instagram Feed (alt) |

## Related Skills

- [nemo-shorts](/skills/nemo-shorts) — Short video creation from text
- [nemo-generate](/skills/nemo-generate) — AI video generation
- [nemo-subtitle](/skills/nemo-subtitle) — Subtitle tool
