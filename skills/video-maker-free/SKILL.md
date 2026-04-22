---
name: video-maker-free
version: 1.2.1
displayName: "Video Maker Free — Make Videos from Photos Text and Clips with AI for Free"
description: >
  Make videos for free using AI — combine photos, text, and video clips into polished content with transitions, music, voiceover, subtitles, and effects. NemoVideo creates videos from whatever you have: a set of product photos becomes a promotional video, a text script becomes a narrated explainer, scattered phone clips become a cohesive story, and raw ideas become publishable content — all free, all full quality, no watermarks.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# Video Maker Free — Make Any Video from Photos, Text or Clips

Most people who need a video don't start with footage — they start with whatever they have. A real estate agent has 15 property photos. A small business owner has a product description. A student has presentation slides. A parent has scattered phone clips from a birthday party. A marketing team has bullet points from a strategy meeting. None of these are "footage" in the traditional sense, but every one of them could be a compelling video. The gap between "what I have" and "a finished video" is the editing process: importing assets into software, arranging them on a timeline, adding motion to photos (Ken Burns, pan-and-zoom), timing text overlays, finding and mixing music, recording or generating voiceover, adding transitions between elements, and exporting at the right settings for each platform. NemoVideo bridges that gap with one command. Provide whatever you have — photos, text, clips, or a combination — and describe the video you want. The AI assembles, animates, narrates, scores, and exports a finished video. Photos get motion and transitions. Text becomes narrated scenes with supporting visuals. Clips get trimmed, color-matched, and joined. The output is a real video — not a slideshow with a filter, but a produced piece of content with professional pacing, audio, and visual quality.

## Use Cases

1. **Photos → Product Video (30-60s)** — An Etsy seller has 8 product photos and needs a video for Instagram. NemoVideo: sequences photos with smooth Ken Burns motion (slow zoom on detail shots, pan across wide shots), adds product name and price as animated text overlays, underlays upbeat acoustic music, applies a consistent warm color grade, and exports 9:16 for Instagram and 1:1 for the listing page. Eight static images become a dynamic product showcase.
2. **Text → Explainer Video (60-180s)** — A SaaS startup has a 300-word product description and needs a landing page video. NemoVideo: breaks the text into Problem → Solution → Benefits → CTA scenes, generates supporting visuals for each scene (office frustration, clean dashboard UI, happy team, pricing page), narrates with a professional voice, adds animated statistics, and exports 16:9 for the website. No filming, no stock footage budget.
3. **Mixed Media → Story Video (2-5 min)** — A parent has 20 phone photos and 8 short clips from their child's first birthday party. NemoVideo: sorts by timestamp, sequences photos with gentle motion and clips at key moments (cake smash, candle blowing, gift opening), adds cheerful background music, overlays the child's name and age as animated titles, and exports as a shareable family video with a clean opening and closing.
4. **Slides → Training Video (5-15 min)** — An HR department has a 30-slide presentation that nobody reads. NemoVideo: converts each slide into a video scene with animated bullet points, generates voiceover narration from the slide notes, adds transitions between topics, inserts knowledge-check pause points, and exports as a training module that employees actually watch. Slide decks become engaging video content.
5. **Bullet Points → Social Content (15-30s per video)** — A marketing manager has 10 product features as bullet points and needs 10 short social videos. NemoVideo batch-generates: each bullet becomes a 15-second video with bold animated text, supporting visual, music, and CTA. Ten social videos from ten lines of text — a month of daily posts produced in one batch.

## How It Works

### Step 1 — Provide Your Materials
Upload photos, video clips, text, or any combination. NemoVideo accepts all formats and intelligently assembles mixed media.

### Step 2 — Describe the Video
Tell NemoVideo what you want: the story, the style, the mood, the platform. Detailed instructions or "make something beautiful from these photos" — both work.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "video-maker-free",
    "prompt": "Make a 45-second product showcase video from 8 product photos. Style: clean and modern with white background accents. Each photo gets 4-5 seconds with smooth Ken Burns motion (slow zoom on details, pan on wide shots). Add product name as animated text: Artisan Ceramic Mug Collection. Price: from $28. Music: warm acoustic guitar at -14dB. Color grade: bright and clean. End frame: Shop now at artisanceramics.com. Export 9:16 for Instagram and 1:1 for website.",
    "media_type": "photos",
    "photo_count": 8,
    "style": "clean-modern",
    "music": "acoustic-guitar-warm",
    "music_volume": "-14dB",
    "text_overlays": ["Artisan Ceramic Mug Collection", "From $28"],
    "cta": "Shop now at artisanceramics.com",
    "exports": ["9:16", "1:1"],
    "watermark": false
  }'
```

### Step 4 — Preview and Share
Preview. Adjust photo order, transition timing, text placement, or music. Export and share — free, full quality.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the video and materials |
| `media_type` | string | | "photos", "clips", "text", "mixed" |
| `style` | string | | "clean-modern", "cinematic", "playful", "elegant", "bold" |
| `music` | string | | "acoustic", "lo-fi", "corporate", "cinematic", "electronic" |
| `music_volume` | string | | "-12dB" to "-22dB" |
| `voice` | string | | Voiceover: "warm-male", "friendly-female", "none" |
| `text_overlays` | array | | Text to display as animated overlays |
| `cta` | string | | Call-to-action text |
| `photo_motion` | string | | "ken-burns", "parallax", "slide", "zoom" |
| `duration` | string | | "30 sec", "45 sec", "60 sec", "natural" |
| `exports` | array | | ["16:9", "9:16", "1:1"] |
| `batch` | array | | Multiple videos from separate material sets |
| `watermark` | boolean | | Always false |

## Output Example

```json
{
  "job_id": "vmf-20260328-001",
  "status": "completed",
  "source_materials": "8 photos",
  "watermark": false,
  "outputs": [
    {
      "format": "9:16",
      "resolution": "1080x1920",
      "duration": "0:44",
      "file_size_mb": 12.4,
      "photo_motion": "ken-burns (zoom + pan)",
      "text_overlays": 3,
      "music": "acoustic-guitar-warm at -14dB"
    },
    {
      "format": "1:1",
      "resolution": "1080x1080",
      "duration": "0:44",
      "file_size_mb": 11.8
    }
  ]
}
```

## Tips

1. **Photos with motion beat static slideshows** — Ken Burns pan-and-zoom adds life to still images. A slow zoom into a product detail feels cinematic. A gentle pan across a room feels like a camera movement. Static photos displayed full-frame feel like PowerPoint.
2. **4-5 seconds per photo is the engagement sweet spot** — Shorter than 3 seconds feels rushed and the viewer can't absorb the image. Longer than 6 seconds and attention drifts. 4-5 seconds with smooth motion holds attention perfectly.
3. **Music without speech can be louder** — Photo/product videos without voiceover benefit from music at -12 to -14dB (louder than the -18dB used under speech). The music carries the emotional energy that speech would normally provide.
4. **Batch generation scales content instantly** — 10 products × 1 video each = 10 social media posts. Batch-process with consistent style for brand cohesion but unique content per product.
5. **Multi-format export from one generation** — 9:16 for Instagram/TikTok + 1:1 for feed + 16:9 for website. Three formats, one command, one consistent video.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 9:16 | 1080x1920 | Instagram / TikTok / Stories |
| MP4 16:9 | 1920x1080 | YouTube / website / email |
| MP4 1:1 | 1080x1080 | Instagram feed / Twitter |
| GIF | 720p | Preview / thumbnail |

## Related Skills

- [free-youtube-video-editor](/skills/free-youtube-video-editor) — YouTube editing
- [how-to-add-music-to-video](/skills/how-to-add-music-to-video) — Add music
- [free-video-generator-ai](/skills/free-video-generator-ai) — AI video generation
