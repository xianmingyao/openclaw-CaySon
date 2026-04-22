---
name: free-video-editor
version: 1.3.1
displayName: "Free Video Editor — Edit Videos Online with AI Powered Tools and Effects"
description: >
  Edit videos online with AI powered tools and effects — trim, cut, merge, add text, apply transitions, adjust speed, add music, color grade, and export professional video from any device without downloading software. NemoVideo provides a complete video editing workflow through chat: describe what you want to change and the AI applies professional edits instantly. Trim unwanted sections, merge multiple clips, add animated text overlays, apply cinematic color grading, adjust playback speed, layer background music, add transitions between scenes, and export in any format for any platform. Free video editor online, edit video AI, video editor no download, online video editing tool, AI video editor free, edit video online, cloud video editor, browser video editor, simple video editor AI.
metadata: {"openclaw": {"emoji": "🎞️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# Free Video Editor — Professional Editing. Zero Software. Just Describe What You Want.

Video editing software is the gatekeeping bottleneck of video creation. Adobe Premiere Pro costs $263/year and requires months of learning. DaVinci Resolve is free but demands a powerful computer and hundreds of hours of skill development. CapCut and iMovie lower the barrier but still require understanding timelines, tracks, keyframes, and export settings. The vast majority of people who need to edit video — small business owners creating product clips, teachers producing lesson content, social media managers crafting posts, students building presentations — do not need the full complexity of editing software. They need specific, describable changes: "remove the first 10 seconds," "add my logo in the corner," "put music under this," "make it vertical for Instagram," "speed up the boring middle part." NemoVideo is editing through conversation. Instead of learning software, you describe the edit. Instead of dragging on a timeline, you say "cut from 0:30 to 1:15." Instead of hunting for the speed ramping panel, you say "slow down the moment when I catch the ball." Every edit that traditional software accomplishes through menus, panels, and keyframes, NemoVideo accomplishes through natural language description. The full power of professional editing — accessible to anyone who can describe what they want.

## Use Cases

1. **Trim and Tighten — Remove Unwanted Sections (any length)** — A 5-minute recording has a bad start (fumbling with the camera for 15 seconds), a tangent in the middle (45 seconds of off-topic rambling), and an abrupt ending (the last 8 seconds are the creator reaching to stop recording). NemoVideo: removes the first 15 seconds (clean start on the actual content), cuts the 45-second tangent (seamless edit that jumps from the last on-topic sentence to the next), trims the last 8 seconds (ending on the final intentional statement), adds a 1-second fade-out at the end, and exports a tightened 3:52 video that feels intentionally produced. The most common editing need — solved in one sentence.

2. **Multi-Clip Merge — Combine Multiple Videos (any number)** — A creator has 8 short clips from different moments that need to become one cohesive video: morning shots, afternoon activity, evening dinner, each from different locations and lighting conditions. NemoVideo: merges all 8 clips in the specified order, applies color grading to match them visually (correcting the different lighting conditions so they feel like one continuous shoot), adds transitions between clips (smooth crossfades for calm content, quick cuts for energetic content), layers a continuous music bed across all clips, and exports one unified video. Eight fragments become one story.

3. **Add Text and Music — Production Polish (any length)** — A basic video needs professional polish: a title at the beginning, key points displayed as text overlays throughout, and background music that sets the mood. NemoVideo: adds an animated title card at the opening (text flies in, holds, fades out), inserts text overlays at specified moments ("Key Insight: Customers prefer simplicity" appearing at 2:30 and fading at 2:37), layers background music matched to the content's mood (upbeat for marketing, calm for wellness, corporate for business), mixes the music volume to sit beneath any speech (auto-ducking), and adds a closing card with CTA text. Raw recording becomes produced content with three additions.

4. **Speed Adjustment — Fast and Slow for Impact (any length)** — A cooking video has 20 minutes of content but the middle 10 minutes is waiting for things to bake. A skateboard video has 30 seconds of routine skating and 3 seconds of an incredible trick. NemoVideo: speeds up the baking wait time to 8x (10 minutes becomes 75 seconds of satisfying time-lapse), adds a timer overlay during the speed-up ("Bake for 25 minutes" with a fast-counting clock), slows the skateboard trick to 0.2x (3 seconds becomes 15 seconds of appreciable slow motion), adds a sound effect at the slow-mo snap point, and exports with smooth transitions between speed changes. Time manipulation that serves the content.

5. **Platform Conversion — One Video to Every Format (any length)** — A creator has one 16:9 landscape video that needs to go on YouTube (16:9), TikTok (9:16), Instagram Feed (1:1), Instagram Reels (9:16 with captions), LinkedIn (16:9 with captions), and Facebook (4:5). NemoVideo: creates all 6 versions with intelligent reframing per platform (AI subject tracking keeps the speaker centered in vertical crops), adds animated captions to the versions that need them (Reels, LinkedIn), adjusts pacing for short-form versions (tightening for TikTok), and exports platform-native files. One recording, six platforms, each version optimized.

## How It Works

### Step 1 — Upload Your Video
Any video file from any device. Phone recordings, screen captures, webcam footage, drone clips, or existing edited content. Upload one or multiple files.

### Step 2 — Describe Your Edits
In plain language: "Trim the first 15 seconds. Speed up from 2:00 to 4:00 at 4x. Add the text 'Subscribe!' at 6:30. Put calm music under the whole thing. Make a vertical version for TikTok with captions."

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "free-video-editor",
    "prompt": "Edit a 7-minute product review video. Trim: cut first 12 seconds (bad start) and last 5 seconds (reaching for camera). Tighten: remove all pauses over 2 seconds. Text: add title Product Review — Sony WH-1000XM6 at 0:00 for 4 seconds, add Verdict: 9/10 at 5:30 for 6 seconds. Music: lo-fi hip hop, low volume under speech. Color: slightly warm, boost contrast for product close-ups. Speed: slow motion at 3:15-3:20 (unboxing reveal) at 0.3x. Export: 16:9 for YouTube at 1080p + 60-second highlight at 9:16 for TikTok with animated captions.",
    "edits": [
      {"type": "trim", "cut_start": "0:00-0:12", "cut_end": "last-5s"},
      {"type": "remove-pauses", "threshold": 2.0},
      {"type": "text", "text": "Product Review — Sony WH-1000XM6", "at": "0:00", "duration": 4},
      {"type": "text", "text": "Verdict: 9/10", "at": "5:30", "duration": 6},
      {"type": "music", "style": "lofi-hiphop", "volume": "under-speech"},
      {"type": "color", "style": "warm-contrast-boost"},
      {"type": "speed", "segment": "3:15-3:20", "speed": 0.3}
    ],
    "outputs": [
      {"format": "16:9", "resolution": "1080p", "platform": "youtube"},
      {"format": "9:16", "duration": 60, "captions": "animated", "platform": "tiktok"}
    ]
  }'
```

### Step 4 — Review and Iterate
Watch the edited video. Want changes? Just describe them: "Make the title bigger," "Remove the slow-motion," "Change the music to something more upbeat." Each instruction refines the edit. No timelines, no panels, no learning curve.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Edit instructions in plain language |
| `edits` | array | | [{type, ...params}] structured edit list |
| `trim` | object | | {start, end} sections to remove |
| `merge` | array | | File order for multi-clip merge |
| `text` | array | | [{text, at, duration, style}] overlays |
| `music` | string | | Background music style |
| `color` | string | | Color grading style |
| `speed` | array | | [{segment, speed}] speed changes |
| `captions` | object | | {style, languages} |
| `outputs` | array | | [{format, resolution, platform}] |

## Output Example

```json
{
  "job_id": "fved-20260329-001",
  "status": "completed",
  "source_duration": "7:12",
  "output_duration": "5:48",
  "edits_applied": {
    "trimmed": "17s",
    "pauses_removed": "1:07",
    "text_overlays": 2,
    "music_added": true,
    "color_grade": "warm-contrast",
    "slow_motion": "3:15-3:20 at 0.3x"
  },
  "outputs": {
    "youtube": {"file": "review-edited-16x9.mp4", "resolution": "1920x1080"},
    "tiktok": {"file": "review-highlight-9x16.mp4", "duration": "0:58", "captions": true}
  }
}
```

## Tips

1. **Describe edits in plain language — NemoVideo translates to technical execution** — You do not need to know what "keyframing opacity at 85% on track 3" means. "Add my logo in the upper-right corner, mostly transparent" accomplishes the same thing. Describe the result you want, not the technique.
2. **Trimming and pause removal are the highest-impact edits for most content** — Before adding effects, music, or graphics, simply cutting dead air and unwanted sections transforms amateur recordings into watchable content. Tight pacing is the foundation of professional video.
3. **Music transforms the emotional register instantly** — The same footage with lo-fi music feels casual and approachable. With orchestral music, it feels epic. With no music, it feels raw and documentary. Music is the fastest way to set the mood for any video.
4. **Multi-platform export saves hours of reformatting** — Requesting YouTube + TikTok + Instagram versions in one prompt produces optimized versions for each platform. Each version is reframed, re-paced, and re-captioned for its specific audience and format requirements.
5. **Iterate rather than perfect the first prompt** — Edit in rounds: first, get the structure right (trim, order, pacing). Then add polish (music, color, text). Then finalize (captions, platform versions). Each round builds on the previous, producing better results than trying to specify everything at once.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / website |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 1:1 | 1080x1080 | Instagram / LinkedIn |
| MP4 4:5 | 1080x1350 | Instagram / Facebook ads |
| GIF | 720p | Preview / social embed |

## Related Skills

- [ai-video-caption-generator](/skills/ai-video-caption-generator) — Auto captions
- [ai-video-speed-changer](/skills/ai-video-speed-changer) — Speed control
- [ai-video-text-overlay](/skills/ai-video-text-overlay) — Text graphics
- [ai-video-filters](/skills/ai-video-filters) — Visual filters
