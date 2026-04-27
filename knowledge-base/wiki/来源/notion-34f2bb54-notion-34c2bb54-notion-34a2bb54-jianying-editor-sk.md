# 剪映AI剪辑Skill - jianying-editor-skill 深度研究报告

> 研究日期：2026-04-03

> 来源：抖音@艾伦2077v + GitHub/全网搜索

---

## 1. 🎯 这是什么（简介）

**剪映（jianying-editor-skill）** 是一个OpenClaw/AI Agent视频自动化剪辑Skill，通过自然语言控制剪映专业版完成从写文案、配音、加字幕、选音乐到最终导出的全流程。

| 项目 | 信息 |

|------|------|

| GitHub | `luoluoluo22/jianying-editor-skill` |

| 一键安装 | `irm is.gd/rpb65M \| iex` |

| 依赖 | Python + 剪映专业版 + playwright |

| 支持平台 | Antigravity/Trae/Claude Code/Cursor/OpenClaw |

| 核心版本 | v1.4 (2026-02-09) |

---

## 2. 📝 关键功能点

| 功能 | 说明 |

|------|------|

| **素材导入** | 视频、音频、图片一句话丢进时间轴，自动排列 |

| **AI配音** | 输入文案自动生成语音，支持剪映原生音色和微软语音 |

| **字幕生成** | 根据配音自动拆句、逐句对齐字幕，支持打字机等动画效果 |

| **自动配乐** | 本地音乐或剪映素材库的云端音乐曲 |

| **特效/转场/滤镜** | 按名字搜索剪映自带的特效库，一句话应用 |

| **网页动效转视频** | HTML/JS/Canvas写动画，自动录屏变成视频素材导入剪映 |

| **录屏+智能变焦** | 录制屏幕操作，自动给鼠标点击位置加缩放和红圈标记 |

| **影视解说** | AI分析视频内容，自动生成分镜脚本并合成解说视频 |

| **自动导出** | 剪完直接导出MP4，支持1080P/4K |

| **关键帧动画** | 缩放、位移、透明度等关键帧，做出运镜效果 |

| **复合片段** | 像嵌套工程一样，把多个子项目组合成一个完整视频 |

---

## 3. ⚡ 怎么安装

### 🔥 Windows一键安装（推荐）

irm is.gd/rpb65M | iex

### 手动安装（OpenClaw/Antigravity）

git clone https://github.com/luoluoluo22/jianying-editor-skill.git .agent/skills/jianying-editor

### 手动安装（Trae IDE）

git clone https://github.com/luoluoluo22/jianying-editor-skill.git .trae/skills/jianying-editor

### 手动安装（Claude Code）

git clone https://github.com/luoluoluo22/jianying-editor-skill.git .claude/skills/jianying-editor

### 通用方式（Cursor/VSCode）

git clone https://github.com/luoluoluo22/jianying-editor-skill.git skills/jianying-editor

### 安装后初始化

# 安装Python依赖

pip install -r requirements.txt

# 初始化网页捕获环境（Web-to-Video功能必须）

playwright install chromium

---

## 4. ✅ 优点

- ✅ **自然语言驱动** - 说话就能剪辑，无需手动操作

- ✅ **全流程自动化** - 文案→配音→字幕→配乐→特效→导出一条龙

- ✅ **录屏自动化** - 教程视频制作神器，鼠标点击自动红圈标记

- ✅ **影视解说** - AI自动分析视频内容+生成分镜脚本

- ✅ **网页动效转视频** - 前端动效库（Three.js/GSAP/Lottie）成为素材库

- ✅ **支持多种AI IDE** - Antigravity/Trae/Claude Code/Cursor都支持

- ✅ **持续更新** - v1.4版本，2026-02-09更新

---

## 5. ❌ 缺点

- ❌ **不是剪映替代品** - 最终渲染、预览还是靠剪映完成

- ❌ **不能用实时特效** - 智能抠图、美颜、GPU实时处理无法调用

- ❌ **不能操作全部UI** - "一键成片"等内置AI功能无法触发

- ❌ **自动导出依赖老版本** - 仅支持剪映5.9及以下（5.0+弹窗太多）

- ❌ **不支持手机端** - 只能配合Windows/Mac桌面版

- ❌ **需要手动重启草稿** - 生成草稿后需重启剪映才能看到

---

## 6. 🎬 使用场景

| 场景 | 示例Prompt |

|------|-----------|

| **随便试试** | "帮我随便剪一个视频看看效果" |

| **Vlog剪辑** | "把D:\旅行素材文件夹里的视频和照片剪成Vlog，配轻快音乐，加标题'周末露营'" |

| **文案配音出片** | "写一段关于'秋天的第一杯奶茶'的短视频文案，配温柔女声旁白和字幕，找温馨BGM" |

| **影视解说** | "D:\电影片段.mp4，帮我做60秒影视解说" |

| **录软件教程** | "我要录操作教程，帮我启动录屏，录完自动导入剪映" |

| **炫酷片头** | "用网页写一个星空粒子的片头动画，5秒钟，然后导入剪映" |

| **字幕配画面** | "旁白.mp3识别字幕，从F:\素材\里自动挑画面配上" |

---

## 7. 🔧 运行依赖环境

| 依赖 | 版本要求 | 说明 |

|------|---------|------|

| **Python** | 3.x | 核心运行环境 |

| **剪映专业版** | **≤5.9** | ⚠️ 自动导出必须用5.9或更低 |

| **playwright** | 最新 | 网页动效录制必须 |

| **pyJianYingDraft** | 内置 | 剪映草稿操作库 |

| **系统** | Windows/Mac | 不支持手机端 |

### ⚠️ 重要：剪映版本要求

- **自动导出功能深度依赖剪映 5.9 或更低版本**

- 5.0+ 版本弹窗太多会干扰自动化脚本

- **[点击下载剪映5.9（夸克网盘）](https://pan.quark.cn/s/81566e9c6e08)**

### 默认剪映草稿目录

C:\Users\Administrator\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft

如剪映安装在其他位置，使用时告诉AI：`"我的剪映草稿目录是 D:\JianyingPro\..."`

---

## 8. 🚀 部署使用注意点

### 坑1：看不到新生成的草稿

- **问题**：剪映软件不会实时刷新文件列表

- **解决**：重启剪映，或随便点进一个旧草稿再退出来

### 坑2：自动导出失败

- **问题**：自动导出脚本模拟鼠标键盘操作

- **解决**：运行时**不要动鼠标和键盘**，且仅支持剪映5.9

### 坑3：脚本存放位置规范

- **规则**：禁止在Skill内部目录创建剪辑脚本

- **正确**：将脚本放在项目根目录或`scripts/`子目录