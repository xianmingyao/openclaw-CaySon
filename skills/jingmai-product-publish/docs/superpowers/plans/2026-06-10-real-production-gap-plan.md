# jm_ufo_agent v2 真实生产缺口修复计划

## 目标

把当前“可注入、可本地验证”的生产骨架继续推进到更接近真实验收的状态。本轮优先修复不需要真实点击京麦、不需要默认访问外部网络的基础设施缺口，让后续真实小批量验证有稳定门禁和可复用运行能力。

## 本轮范围

1. F02 京东抓取稳定性：补重试、限速、Cookie/User-Agent 注入、失败证据。
2. F03 图片下载稳定性：补下载重试、失败 URL 证据、批量失败不伪装成功。
3. F19 MiniMax 生产预检：补可执行 preflight 报告，确认 `/models` 是否包含 `MiniMax-M3`。
4. CLI/测试：新增本地可测入口和 fake transport 测试，不默认触发真实外部请求。

## 非本轮范围

- 不点击真实京麦窗口。
- 不写系统剪贴板。
- 不保存真实草稿。
- 不默认访问真实京东或 MiniMax；真实调用必须由用户显式运行命令并提供配置。

## 任务分解

1. 新增京东 transport 包装器：`RetryingJdTransport` / `RateLimitedJdTransport` / `CookieJdTransport`。
2. 新增图片下载包装器：`RetryingImageDownloader`，保留每个 URL 的失败证据。
3. 新增 MiniMax preflight 报告：`ReviewPreflightReport` / `preflight_minimax_review_scorer()`。
4. CLI 增加 `minimax-preflight` 命令，仅用户显式调用时访问配置中的 MiniMax。
5. 补测试覆盖 fake transport 的重试、限速钩子、preflight 成功/失败。

## 验收标准

- `python -m pytest` 通过。
- `uv run --extra test python -m pytest` 通过或仅保留既有 skip。
- `python scripts\check_safety_policy.py jm_ufo_agent\agents` 通过。
- `graphify update .` 完成。
- 新增实现默认不进行真实网络请求或真实京麦写操作。

