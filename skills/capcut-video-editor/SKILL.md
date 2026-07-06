---
name: capcut-video-editor
version: "1.0.0"
displayName: "CapCut Video Editor — AI-Powered Editing Guidance for Stunning Clips"
description: >
  Tell me what you need and I'll walk you through exactly how to pull it off in CapCut. This capcut-video-editor skill helps creators, marketers, and casual editors get the most out of CapCut's toolset — from trimming and transitions to text overlays, speed ramping, and trending effects. Whether you're cutting a TikTok, polishing a YouTube short, or building a brand reel, get step-by-step guidance tailored to your footage. Supports mp4, mov, avi, webm, and mkv formats.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm your dedicated CapCut editing guide — ready to help you cut, style, and export videos that actually stand out. Tell me what you're working on and let's build something worth posting.

**Try saying:**
- "How do I create a speed ramp effect in CapCut that syncs with a beat drop in my audio?"
- "What's the best way to add animated text captions to a vertical video in CapCut for TikTok?"
- "Can you walk me through removing a green screen background in CapCut and replacing it with a custom clip?"

On first use, the skill connects to NemoVideo automatically:
1. Check for `NEMO_TOKEN` env var, or acquire one via `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` (100 free credits)
2. Persist a Client-ID to `~/.config/nemovideo/client_id` for rate-limit tracking (UUID only, no secrets)
3. Create a session and start working immediately

# Edit Smarter in CapCut — No Guesswork Required

CapCut has quietly become one of the most powerful free video editors available — but its depth can be overwhelming. Between keyframe animations, auto-captions, chroma key, and a library of filters that grows weekly, it's easy to spend more time hunting for features than actually editing. That's exactly where this skill comes in.

The capcut-video-editor skill acts as your on-demand editing companion. Describe what you're trying to create — a cinematic slow-motion clip, a punchy social media ad, a vlog with smooth transitions — and get clear, specific instructions for doing it inside CapCut. No vague advice, no generic tutorials. Just the exact steps, settings, and CapCut-specific menu paths you need.

This skill is built for content creators at every level. Beginners get guided walkthroughs that skip the confusion. Intermediate editors discover shortcuts and features they didn't know existed. Advanced users can fine-tune effects, master timing curves, and replicate trending styles seen across TikTok and Instagram Reels — all within CapCut's native environment.

### Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEMO_TOKEN` | Auto-acquired on first use (100 free credits, 7-day expiry) | API authentication |
| `NEMO_API_URL` | `https://mega-api-prod.nemovideo.ai` | API base URL |

## Routing Your CapCut Requests

Every editing request — whether you're asking about Auto Captions, keyframe animation, chroma key, or beat sync — gets routed to the most relevant CapCut workflow based on the intent and context you provide.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend powers real-time CapCut guidance by processing your project details, timeline data, and effect parameters through its AI pipeline. It translates your editing goals into precise, step-by-step CapCut instructions tailored to your clip.

**Required headers** on all requests: `X-Skill-Source: $SKILL_NAME`, `X-Skill-Version: $SKILL_VERSION`, `X-Skill-Platform: $SKILL_SOURCE`

**Create session**: `POST $API/api/tasks/me/with-session/nemo_agent` — returns `task_id` and `session_id`

**Send message (SSE)**: `POST $API/run_sse` with `session_id` and user message. Stream responses; ~30% of edits return no text (query state to confirm changes).

**Upload**: `POST $API/api/upload-video/nemo_agent/me/<sid>` — file or URL upload. Supports: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

**Check credits**: `GET $API/api/credits/balance/simple`

**Query state**: `GET $API/api/state/nemo_agent/me/<sid>/latest` — check draft, tracks, generated media

**Export**: `POST $API/api/render/proxy/lambda` — export does NOT cost credits. Poll `GET $API/api/render/proxy/lambda/<id>` until `status: completed`.

**Task link**: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### Common Errors

If your token has expired, simply re-authenticate to restore your session and pick up right where your edit left off. A 'session not found' error means your previous session timed out — just start a fresh session and reload your project context. Running low on credits? Head over to nemovideo.ai to register or top up so your CapCut workflow stays uninterrupted.

## Tips and Tricks

One of CapCut's most underused features is the Curve editor inside the Speed panel — instead of using preset slow-motion options, custom curves let you design a speed ramp that feels hand-crafted rather than templated. Ask this skill to walk you through it point by point.

For text animations, CapCut's 'Bubble' and 'Karaoke' caption styles get a lot of attention, but the real power is in the 'Basic' style with manually set entrance and exit animations — you get far more control over timing and feel.

When working with longer footage (mp4 or mov files especially), use CapCut's 'Auto Reframe' feature before doing any fine cuts. It saves time repositioning subjects for different aspect ratios across platforms. Always export at the highest bitrate your platform supports — CapCut's compression on lower settings is noticeable on OLED screens.

## Performance Notes

CapCut handles mp4 and mov files most efficiently — these formats load fastest in the timeline and preview with the least dropped frames on mid-range devices. If you're working with avi or mkv source files, consider converting them to mp4 (H.264) before importing to avoid stuttering during playback and rendering delays.

Webm files are supported but may cause timeline lag on mobile versions of CapCut, particularly when effects or overlays are stacked on top. For complex projects with multiple tracks, effects layers, and transitions, the desktop version of CapCut consistently outperforms the mobile app in both preview smoothness and export speed.

If you notice proxy-related slowdowns, CapCut's 'Smart HDR' and 'AI Enhance' features are the most GPU-intensive — toggling these off during the editing phase and applying them only at export can significantly reduce lag on older hardware.

## Integration Guide

CapCut integrates natively with TikTok, allowing direct publishing from the editor without re-uploading — a major time saver for creators posting daily. To use this, ensure your TikTok account is linked inside CapCut's profile settings before you start a project, since the export destination is selected during the final export step.

For teams or brand accounts, CapCut's cloud sync (available in the desktop version) lets multiple editors work from the same asset library. This is especially useful when a social media manager and a video editor are collaborating on campaign content — both can access the same footage, fonts, and brand overlays.

If you're pulling footage from external sources like drone cameras (often exporting mkv or mov) or screen recorders (commonly webm), this skill can advise on the cleanest import workflow and whether any pre-processing steps will save you headaches once you're deep into the edit.
