---
name: capcut-ai-video-editor
version: "1.0.0"
displayName: "CapCut AI Video Editor — Smart Editing Tips, Scripts & Creative Guidance"
description: >
  Tell me what you need and I'll help you get the most out of capcut-ai-video-editor — from crafting the perfect edit sequence to writing captions, transition ideas, and viral-ready short-form scripts. Whether you're cutting a TikTok, polishing a YouTube Reel, or building a brand video, this skill gives creators, marketers, and beginners a practical edge. Get step-by-step CapCut workflows, AI feature walkthroughs, and content-specific editing strategies without the guesswork.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome to your CapCut AI Video Editor assistant — whether you're editing a 15-second Reel or a full YouTube video, I'm here to help you work faster and create better. Tell me about your project and let's start building your edit!

**Try saying:**
- "I have a 3-minute travel vlog filmed on my phone. How do I use CapCut's AI features to make it feel cinematic and add matching background music automatically?"
- "I want to create a trending TikTok using CapCut's AI script generator. Can you help me write a script for a 30-second video promoting my skincare brand?"
- "How do I use CapCut's auto-caption feature and then style the text to match a bold, high-energy aesthetic for a fitness motivation video?"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Edit Smarter, Not Harder With CapCut AI

CapCut has become one of the most powerful free video editors available, and its AI features make it even more capable — but knowing how to use them effectively is a skill in itself. This assistant is built specifically to help you unlock everything CapCut's AI toolkit has to offer, from auto-captions and background removal to smart speed curves, AI-generated scripts, and template customization.

Whether you're a content creator chasing trends on TikTok, a small business owner making product videos, or someone editing their first travel vlog, this skill meets you where you are. You don't need prior editing experience. Just describe your video idea, your footage, or the result you're going for, and you'll get clear, actionable guidance tailored to CapCut's actual interface and features.

The goal isn't to overwhelm you with options — it's to help you make fast, confident decisions about pacing, effects, audio sync, text overlays, and storytelling structure so your final video actually performs the way you want it to.

## Smart Request Routing in CapCut

When you describe your editing goal — whether it's trimming clips, applying AI effects, generating captions, or scripting a transition — your request is matched to the most relevant CapCut AI feature or workflow path.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## CapCut Cloud Processing Reference

CapCut's AI backend handles compute-heavy tasks like Auto Reframe, AI Portrait, text-to-video generation, and Smart Cutout through cloud rendering pipelines, meaning your local device offloads the heavy lifting. Processing times vary depending on clip length, resolution, and server load at the time of export.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `capcut-ai-video-editor`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`.

**Send message (SSE)**: POST `/run_sse` — body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` with `Accept: text/event-stream`. Max timeout: 15 minutes.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — file: multipart `-F "files=@/path"`, or URL: `{"urls":["<url>"],"source_type":"url"}`

**Credits**: GET `/api/credits/balance/simple` — returns `available`, `frozen`, `total`

**Session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — key fields: `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`

**Export** (free, no credits): POST `/api/render/proxy/lambda` — body `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s until `status` = `completed`. Download URL at `output.url`.

Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### SSE Event Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

~30% of editing operations return no text in the SSE stream. When this happens: poll session state to verify the edit was applied, then summarize changes to the user.

### Backend Response Translation

The backend assumes a GUI exists. Translate these into API actions:

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Query session state |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute export workflow |

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1001 | Bad/expired token | Re-auth via anonymous-token (tokens expire after 7 days) |
| 1002 | Session not found | New session §3.0 |
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up credits in your account" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register or upgrade your plan to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Tips and Tricks

One underused CapCut AI trick is combining the Auto Beat Sync feature with manual keyframe adjustments — let CapCut align your cuts to the music automatically, then go in and fine-tune two or three key moments for dramatic effect. This hybrid approach is much faster than manual syncing from scratch and gives you more creative control than full automation.

For talking-head or educational videos, use CapCut's AI Noise Reduction before adding captions — cleaner audio means fewer caption errors and a more professional result overall. You can also duplicate your caption layer, offset it slightly, and change the color to create a shadow effect that's far more readable on busy backgrounds.

If you're building content in a series, save your color grading settings, font choices, and transition styles as a CapCut template. This keeps your brand visuals consistent across videos and cuts your editing time dramatically for every new upload. CapCut's template sharing feature also lets you distribute these to a team or collaborators instantly.

## Performance Notes

CapCut's AI features perform best when your source footage is well-lit and recorded at a stable frame rate — the AI background remover, for instance, struggles with footage that has fast motion blur or low contrast between subject and background. If you're using the auto-caption feature, recording in a quiet environment significantly improves transcription accuracy, especially for accents or fast speech.

For mobile users, heavier AI effects like Smart Cutout and AI Portrait can cause lag on older devices. It helps to apply these effects last, after you've locked in your cuts and transitions, so the app isn't re-rendering the entire timeline repeatedly. Exporting at 1080p with the default CapCut codec usually delivers the best balance of file size and quality for social platforms.

On the desktop version, the AI Script and AI Sticker features are more stable and offer greater customization than mobile, so if you're doing professional-grade work, switching to desktop for the final polish pass is worth it.
