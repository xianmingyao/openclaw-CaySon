---
name: ai-video-editing-software
version: "1.0.0"
displayName: "AI Video Editing Software — Smart Cuts, Captions & Polished Videos Fast"
description: >
  Turn raw footage into share-ready videos without spending hours in a timeline. This skill brings the power of ai-video-editing-software directly into your workflow — helping you cut scenes, write captions, suggest transitions, generate scripts for voiceovers, and structure edits for any platform. Built for content creators, marketers, and social media teams who need professional-looking results without a steep learning curve.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome to your AI video editing assistant — whether you're cutting a YouTube vlog, a product promo, or a social media reel, I'll help you plan edits, write captions, and structure your footage for maximum impact. Tell me about your video and let's get it polished.

**Try saying:**
- "Cut this interview to 90 seconds"
- "Write captions for my product demo"
- "Format my video for TikTok"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Edit Smarter — Let AI Do the Heavy Lifting

Most video editing tools hand you a blank timeline and expect you to figure the rest out. This skill works differently. Describe your footage, your goal, or the platform you're targeting — and get back a structured edit plan, caption suggestions, scene-by-scene cut recommendations, and even b-roll ideas tailored to your content.

Whether you're trimming a long interview into a punchy 60-second reel, adapting a landscape video for TikTok, or building a product demo from scratch, this skill guides every decision. You don't need to be a professional editor to produce something that looks like you are.

This is especially useful for solo creators, small marketing teams, and agencies juggling multiple video projects at once. Instead of staring at raw clips wondering where to start, you get a clear editing roadmap — complete with pacing notes, text overlay ideas, and platform-specific formatting guidance — so you can move from footage to final cut in a fraction of the usual time.

## Routing Edits to the Right Engine

Each request — whether you're triggering smart cuts, generating auto-captions, applying B-roll suggestions, or exporting a polished timeline — is parsed and routed to the appropriate AI processing pipeline based on the detected edit intent and media context.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

All render jobs, transcription requests, and scene-detection tasks are handled via ClawHub's cloud backend, which offloads heavy frame analysis and model inference away from your local machine. Latency varies by clip length, resolution, and queue depth — longer timelines with 4K assets will take more processing cycles than short-form vertical cuts.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-video-editing-software`
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

## Best Practices for AI-Assisted Video Editing

Get the most out of this skill by being specific about your footage before asking for edit suggestions. Instead of saying 'help me edit my video,' describe the content type, approximate length, target platform, and the emotional tone you want — for example, 'I have a 7-minute cooking tutorial I want to cut to 2 minutes for YouTube Shorts with an upbeat feel.'

For caption and text overlay requests, mention your brand voice. Casual and punchy captions for TikTok look very different from professional subtitles for a corporate training video — giving that context upfront produces much sharper results.

When planning cuts, share the rough structure of your footage (e.g., 'the first 3 minutes are setup, minutes 3-6 are the main demo, the last minute is a call to action'). This lets the skill generate a precise scene-by-scene edit plan rather than generic advice. Use the output as a blueprint you bring into your actual editing software — whether that's Premiere, DaVinci Resolve, CapCut, or anything else.

## Frequently Asked Questions

**Can this skill actually edit my video files?** This skill works with text — it creates edit plans, scripts, captions, transition notes, and structure guides. You then apply those decisions in your preferred video editing software. Think of it as your AI editor who tells you exactly what to do, cut by cut.

**What platforms can I optimize videos for?** You can request formatting and pacing guidance for YouTube, Instagram Reels, TikTok, LinkedIn, Facebook, X (Twitter), and more. Each platform has different aspect ratio, length, and caption style norms — just mention your target platform.

**Can it help with voiceovers and scripts?** Yes — if you need a narration script, a spoken intro, or a voiceover to lay over b-roll, describe your footage and audience and the skill will write it for you.

**Is this useful if I'm a complete beginner?** Absolutely. The skill is designed to translate your raw idea or footage description into a clear, actionable edit plan — no prior editing knowledge required to get value from it.
