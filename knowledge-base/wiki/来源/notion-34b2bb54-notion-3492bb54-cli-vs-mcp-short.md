# CLI vs MCP 专题 - 精简版

> 2026-04-03 | 来源：抖音@技术爬爬虾

---

## 一句话理解

| 方案 | 核心理念 | 谁需要 |

|------|---------|--------|

| **MCP** | Anthropic提出的标准化协议 | 需要官方支持的LLM扩展 |

| **CLI** | 把软件变成命令行，AI敲命令控制 | 需要稳定控制专业软件 |

**核心矛盾：** GUI自动化太脆弱（页面改一下就失败），需要稳定的软件控制方式。

---

## 两大项目

| 项目 | Stars | 网址 | 一句话 |

|------|-------|------|--------|

| **CLI-Anything** | 1.4k | github.com/HKUDS/CLI-Anything | 港大开源，7阶段自动为软件生成CLI |

| **OpenCLI** | **9.6k** | github.com/jackwener/opencli | 任意网站/工具→CLI |

### CLI-Anything（港大开源）

- **Slogan：** 今天的软件为人而生 👨‍💻，明天的用户是 Agent 🤖

- **支持：** GIMP、Blender、LibreOffice、OBS等数百款

- **工作流：** 分析软件 → 设计命令 → 生成CLI → 结构化输出 → 测试验证 → 发布Hub

### OpenCLI（社区主流）

- **功能：** 网站/Electron/二进制 → CLI

- **特点：** 复用Chrome登录态、AI驱动发现、AGENT.md集成

---

## 巨头CLI军备

| 公司 | 产品 |

|------|------|

| Anthropic | Claude Code |

| OpenAI | Codex CLI |

| 钉钉/飞书/网易云 | 官方CLI |

**Karpathy预言：** "为Agent重写软件"正在成为现实

---

## MCP vs CLI 对比

| 维度 | MCP | CLI |

|------|-----|-----|

| 标准化 | 高（官方协议） | 低（各自为战） |

| 需要官方支持 | ✅ 需要 | ❌ 不需要 |

| 自动生成 | ❌ 不能 | ✅ CLI-Anything可以 |

| 稳定性 | 依赖官方 | 稳定可靠 |

| 适用场景 | LLM上下文扩展 | 专业软件控制 |

**结论：** MCP需要官方支持，CLI可绕过官方自动生成

---

## 与现有工具关系

AI Agent控制软件

├── GUI自动化（脆弱）→ browser-use / agent-browser

├── MCP协议（需官方）→ WebMCP

└── CLI方案（稳定）→ CLI-Anything / OpenCLI / 官方CLI

**选择指南：**

- 浏览器 → browser-use / agent-browser

- 专业软件 → CLI-Anything

- 网站 → OpenCLI

- 企业服务 → 官方CLI

---

## 安装命令

# CLI-Anything

git clone https://github.com/HKUDS/CLI-Anything.git

cd CLI-Anything && pip install -r requirements.txt

python -m cli_anything <software-path>

# OpenCLI

npm install -g opencli

opencli register mycli

---

## 演示案例

# 1. 为GIMP生成CLI

python -m cli_anything "C:\Program Files\GIMP 2\bin\gimp-2.10.exe"

gimp-cli open "photo.jpg"

gimp-cli resize "photo.jpg" --width 800 --height 600

# 2. OpenCLI抓取网页

opencli fetch "https://mp.weixin.qq.com/s/xxx"

# 3. 控制Blender

blender-cli create-sphere --name "my_sphere" --color red

# 4. LibreOffice批量转换

libreoffice-cli convert "doc.docx" --format pdf

---

## 优缺点

| ✅ 优点 | ❌ 缺点 |

|---------|---------|

| 稳定可靠，不受GUI变化影响 | 学习曲线（需了解CLI） |

| 无需官方支持（CLI-Anything自动生成） | 不是所有软件都适合CLI |

| AI友好，自然语言→结构化命令 | CLI-Anything还在早期（1.4k Stars） |

| 历史沉淀，CLI工具几十年积累 | OpenCLI依赖Chrome环境 |

---

## 相关链接

- CLI-Anything: https://github.com/HKUDS/CLI-Anything

- OpenCLI: https://github.com/jackwener/opencli

- 知乎详解: 「OpenCLI vs CLI-Anything：AI Agent 时代的 CLI 革命」