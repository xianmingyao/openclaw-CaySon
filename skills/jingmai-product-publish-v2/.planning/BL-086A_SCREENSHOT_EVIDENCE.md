# BL-086A Screenshot Evidence Archive

Updated: 2026-05-17

## Verdict

Status: `IN_PROGRESS`

The project contains runtime JSONL records that reference P0 desktop screenshots, but the referenced PNG files are not present in the current working tree. Because BL-086A requires before/after screenshots or equivalent evidence for each critical T1-T8 action, this task must not be marked `DONE` until the image files are restored or recaptured.

Current score impact: keep delivery score at `90/100`. DX/security work has improved release readiness, but the BL-086A score gate is not satisfied by missing screenshot paths.

## Evidence Sources Checked

Command:

```powershell
python -m jingmai_publish.cli check-evidence --root .
```

Latest command result: `success=false`, `artifact_count=253`, `present_count=72`, `missing_count=181`.

Recovery/recapture attempts on 2026-05-17:

- Git history check for `resources/screenshots/*.png` and `logs/screenshots/*.png`: no tracked screenshot files found.
- Workspace search for `window-1187102-*.png` under `E:\workspace`: no matching files found.
- Initial probe recapture with `t8-probe` and `t6-probe`: blocked because no Jingmai desktop window was found.
- Retry with previous real-run hints `--window-keyword jd_ --preferred-class JMMainFrameBase`: still no matching foreground window.
- Process check initially found background services only: `JMCoreService`, `JdHostsafe`, `JdHostagent`, `JdHostagent64`.
- Candidate foreground executable found and launched after user continued: `E:\Program Files\JMWorkStation\13.3.2.0\DongDong64\jdm_dd_workbench.exe`.
- Fresh Jingmai window captured: handle `527564`, title `jd_465d1abd3ee76`, class `JMMainFrameBase`.
- Fresh `t4` recapture initially exposed retry-lane `input_mode` compatibility gap, then succeeded after fix: `resources/screenshots/window-527564-20260517-160739-586827.png`; message included `标题填充=成功`, `型号校验=成功`, `必填属性校验=成功`, and `page_state=base_info_completed`.
- Fresh `t4` rerun after optional `brand` dispatch fix succeeded: `resources/screenshots/window-527564-20260517-161040-517484.png`; however the real Jingmai account/category selected fallback brand `志倍（ZHIBEI）-长沙飞戈电子技术有限公司` instead of requested `公牛（BULL）`, so this remains a business-data correctness gap.
- Fresh `t4` rerun after removing unmatched-brand fallback now fails correctly instead of silently choosing the wrong brand: `resources/screenshots/window-527564-20260517-174009-419311.png`; message included `品牌校验=失败`, `品牌值=公牛（BULL）`, and `page_state=publish_entry`. This blocks 100% business-data correctness until the Jingmai account/category exposes the requested brand or input data is changed to an allowed brand.
- Fresh `t4-option-probe` confirmed the brand dropdown currently exposes only `志倍（ZHIBEI）-长沙飞戈电子技术有限公司`; `公牛（BULL）` is not available for this account/category. Probe screenshots: `resources/screenshots/window-527564-20260517-174135-789833.png`, `resources/screenshots/window-527564-20260517-174136-230684.png`.
- Fresh `t6-main-image` recapture succeeded after picker-selection fix: `resources/screenshots/window-527564-20260517-153403-428577.png`; message included `图片出现=成功` and `page_state=main_image_uploaded`.
- Fresh `t6-transparent-image` recapture succeeded after remaining-empty-slot index fix: `resources/screenshots/window-527564-20260517-155838-201045.png`; message included `图片出现=成功` and `page_state=transparent_image_uploaded`.
- Fresh `t6-detail-editor` recapture succeeded: `resources/screenshots/window-527564-20260517-155921-006320.png`; message included `内容写入=成功`, `内容可见=成功`, and `page_state=detail_content_written`.
- Fresh `t7` recapture succeeded: `resources/screenshots/window-527564-20260517-160016-844997.png`; message included all logistics/after-sales field fills and validations as `成功`, with `page_state=logistics_completed`.
- Fresh `t8-save-draft` recapture succeeded after retry-lane `click_mode` compatibility fix: `resources/screenshots/window-527564-20260517-160353-183910.png`; message included `草稿点击=成功`, `草稿确认=成功`, `触发模式=draft_list`, and `page_state=draft_saved`.

| Source | Result |
|---|---|
| `resources/screenshots/` | Contains fresh 2026-05-17 recapture screenshots for T4/T6/T7/T8. |
| `logs/screenshots/` | Directory exists; current fresh evidence is under `resources/screenshots/`. |
| `resources/memory/runtime-memory.jsonl` | Contains runtime records and screenshot path references. |
| `logs/memory/runtime-memory.jsonl` | Contains current runtime memory output. |
| `resources/probe-images/main-probe.png` | Exists, but this is an input image, not UI evidence. |
| `resources/probe-images/transparent-probe.png` | Exists, but this is an input image, not UI evidence. |

## Required P0 Evidence Matrix

| Flow | Required evidence | Current record | File present | Status |
|---|---|---|---|---|
| T1/T2 import and product preparation | command, task/job id, prepared product record | runtime/task records exist indirectly | n/a | `PARTIAL` |
| T4 base product fields | after screenshot and success message | old `window-1187102-*` reference missing; latest fresh run `resources/screenshots/window-527564-20260517-174009-419311.png` fails on requested-brand validation | yes | `BLOCKED_BRAND_MISMATCH` |
| T5 required SKU fields | command output and validation result | textual evidence in `progress.md` | n/a | `PARTIAL` |
| T6 main image upload | after screenshot and slot state | old `window-1187102-*` reference missing; fresh recapture `resources/screenshots/window-527564-20260517-153403-428577.png` | yes | `RECAPTURED_PRESENT` |
| T6 transparent image upload | after screenshot and slot state | old `window-1187102-*` reference missing; fresh recapture `resources/screenshots/window-527564-20260517-155838-201045.png` | yes | `RECAPTURED_PRESENT` |
| T6 detail editor | after screenshot and content-visible state | old `window-1187102-*` reference missing; fresh recapture `resources/screenshots/window-527564-20260517-155921-006320.png` | yes | `RECAPTURED_PRESENT` |
| T7 logistics/after-sales | command output and page state | fresh recapture `resources/screenshots/window-527564-20260517-160016-844997.png`; `resources/runtime/t7_probe.log` also exists | yes | `RECAPTURED_PRESENT` |
| T8 save draft | final screenshot and draft-list row | old `window-1187102-*` references missing; fresh recapture `resources/screenshots/window-527564-20260517-160353-183910.png` | yes | `RECAPTURED_PRESENT` |
| T8 formal publish | explicit user approval plus final state | intentionally not executed | n/a | `OUT_OF_SCOPE_UNTIL_APPROVED` |

## Completion Criteria

BL-086A can be marked `DONE` only when one of these is true for every required flow:

1. The referenced PNG file is restored into the working tree and the index above is updated to `PRESENT`.
2. The step is rerun against the Jingmai desktop app and fresh screenshots are generated.
3. A deliberate alternative evidence artifact is created, such as a structured UI artifact row with a stable screenshot hash, page text, command, job id, and timestamp.

## Next Actions

1. Recover existing `resources/screenshots/window-*.png` files if they exist outside this checkout.
2. If recovery is not possible, rerun draft-mode P0 steps and capture fresh screenshots.
3. Add screenshot hash, file size, timestamp, command, and page state to this archive.
4. Only then update `.planning/BACKLOG.md`, `.planning/STATE.md`, and `100_SCORE_RECOVERY_PLAN.md` to count BL-086A as complete.
