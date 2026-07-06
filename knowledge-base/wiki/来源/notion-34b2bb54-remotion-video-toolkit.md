# Remotion Video Toolkit - React视频生成Skill研究报告

> 研究日期：2026-04-03

> 来源：抖音@艾伦2077v 视频「Remotion的Skill」

> 相关项目：`Arxchibobo/openclaw-remotion-video-toolkit`

---

## 1. 🎯 这是什么（简介）

**Remotion** 是一个用**React代码生成MP4视频**的框架，Video Toolkit是它的OpenClaw Skill封装。写React组件 → 输出真实视频文件。

| 项目 | 信息 |

|------|------|

| GitHub | `Arxchibobo/openclaw-remotion-video-toolkit` |

| 安装命令 | `openclaw skill install github:Arxchibobo/openclaw-remotion-video-toolkit` |

| 核心依赖 | Node.js 18+ / React 18+ / FFmpeg（内置） |

| 规则数 | 29条规则，覆盖所有核心功能 |

| 官方 | https://www.remotion.dev/ |

---

## 2. 📝 关键功能点

| 功能 | 说明 |

|------|------|

| **程序化视频** | 用React组件代码生成视频，无需GUI剪辑软件 |

| **个性化批量视频** | JSON数据驱动，一套模板生成千个个性化视频 |

| **自动化社交媒体** | 拉取实时数据自动生成日报/周报视频 |

| **动态广告营销** | 替换用户名、产品图、价格，无限变体 |

| **数据可视化视频** | 图表动画转视频，KPI报告变短视频 |

| **TikTok字幕** | 音频转字幕，逐字高亮，导入即用 |

| **产品展示视频** | 数据库驱动，自动生成产品介绍 |

| **教育内容** | 动画课程、证书、步骤引导 |

| **视频即服务** | HTTP API方式，对外提供视频渲染服务 |

---

## 3. ⚡ 怎么安装

### 方式1：OpenClaw CLI（推荐）

openclaw skill install github:Arxchibobo/openclaw-remotion-video-toolkit

### 方式2：手动安装

git clone https://github.com/Arxchibobo/openclaw-remotion-video-toolkit.git <skill-dir>

### 环境准备

# 需要 Node.js 18+

node --version

# 创建Remotion项目

npx create-video@latest my-video

# 预览

cd my-video && npm start

# 渲染

npx remotion render src/index.ts MyComposition out/video.mp4

---

## 4. ✅ 优点

- ✅ **代码即视频** - 用React组件思维做视频，开发体验好

- ✅ **批量个性化** - 一套模板，千人千面（Spotify Wrapped模式）

- ✅ **数据驱动** - JSON → 视频自动化，适合数据可视化

- ✅ **TikTok字幕** - 音频转逐字高亮字幕，吸睛神器

- ✅ **服务端渲染** - 支持Lambda/Cloud Run，企业级应用

- ✅ **免费开源** - 框架免费，FFmpeg内置

- ✅ **29条规则** - 覆盖动画/时间/字幕/3D/图表全场景

---

## 5. ❌ 缺点

- ❌ **需要React基础** - 不适合纯小白，需懂React组件

- ❌ **渲染耗时** - 本地渲染需要GPU/CPU时间

- ❌ **调试成本高** - 代码改视频，调试不如预览直观

- ❌ **复杂动画耗性能** - 动画越复杂，渲染越慢

---

## 6. 🎬 使用场景

| 场景 | 示例 |

|------|------|

| **个性化视频批量生成** | Spotify Wrapped风格，用户数据驱动生成个人年度总结视频 |

| **社交媒体自动化** | 每日自动拉取数据，生成数据日报/周报短视频 |

| **营销视频变体** | 一套模板，替换姓名/产品图/价格，生成1000个广告变体 |

| **数据可视化** | 图表动画转视频，KPI报告变分享短视频 |

| **TikTok字幕** | 音频转逐字高亮字幕，视频更有吸引力 |

| **产品介绍** | 数据库驱动，自动生成产品展示视频 |

| **在线课程** | 动画课件、证书颁发、步骤引导视频 |

| **视频API服务** | HTTP API方式，对外提供视频渲染服务 |

---

## 7. 🔧 核心规则详解（29条）

### 核心规则

| 规则 | 功能 |

|------|------|

| `compositions.md` | 定义视频/静帧/文件夹/默认props |

| `rendering.md` | CLI/Node.js API/Lambda/Cloud Run渲染 |

| `calculate-metadata.md` | 动态设置时长/尺寸/props |

### 动画与时间

| 规则 | 功能 |

|------|------|

| `animations.md` | 淡入/缩放/旋转/滑动 |

| `timing.md` | 插值曲线/缓动/弹簧物理 |

| `sequencing.md` | 延迟/链式/场景编排 |

| `transitions.md` | 场景转场效果 |

| `trimming.md` | 修剪动画起止点 |

### 文字排版

| 规则 | 功能 |

|------|------|

| `text-animations.md` | 打字机/单词高亮/揭示效果 |

| `fonts.md` | Google Fonts和本地字体加载 |

| `measuring-text.md` | 文字适配容器/溢出检测 |

### 媒体处理

| 规则 | 功能 |

|------|------|

| `videos.md` | 嵌入/裁剪/变速/音量/循环 |

| `audio.md` | 导入/裁剪/淡入淡出/音量控制 |

| `images.md` | 图片组件 |

| `gifs.md` | 时间轴同步GIF播放 |

| `assets.md` | 导入任意媒体 |

| `can-decode.md` | 浏览器兼容性验证 |