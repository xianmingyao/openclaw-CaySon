# OpenMAIC - 清华大学开源多智能体互动课堂

> 2026-04-10 更新 | 来源：抖音视频 + GitHub

> 更新内容：Stars 13.6k / Vivi 2.0 PDF转课堂 / JCST 2026学术发表

---

## 一句话

**OpenMAIC = 一键把任何主题/文档变成沉浸式AI课堂，支持生成完整的课堂视频**

---

## 项目信息

| 项目 | 信息 |

|------|------|

| **全称** | Open Multi-Agent Interactive Classroom |

| **来源** | 清华大学 |

| **官网** | https://openmaic.io/zh/ |

| **GitHub** | THU-MAIC/OpenMAIC |

| **Stars** | **13.6k** ⭐ |

| **Forks** | 2.3k |

| **最新版本** | Vivi 2.0 |

| **学术发表** | JCST 2026 |

| **特点** | 多智能体AI课堂，重现真实课堂社交动态 |

| **实测** | 清华700+学生，2年多测试迭代 |

---

## 核心功能

| 功能 | 说明 |

|------|------|

| **主题转课堂** | 把任意主题/文档变成沉浸式AI课堂 |

| **交互幻灯片** | 自动生成PPT风格的课件 |

| **测验题目** | 自动出题测试理解 |

| **多角色讨论** | 学生/老师/助教多个AI角色互动 |

| **课堂视频** | 一键生成完整长课堂视频 |

| **实时问答** | AI回答学生问题 |

| **📄 PDF转课堂** | 一键将PDF转化为包含AI教师+白板+测验的沉浸式学习场景（Vivi 2.0新功能）|

| **🎓 AI教师** | 虚拟AI教师角色，模拟真实课堂互动 |

| **📊 白板互动** | 课堂画图解释，帮助理解复杂概念 |

---

## 工作原理

输入：主题/文档/PDF/视频

↓

┌─────────────────────────────────┐

│      多智能体协作               │

│                                 │

│  ┌─────────┐  ┌─────────┐      │

│  │ 教师Agent│  │学生Agent│      │

│  └────┬────┘  └────┬────┘      │

│       │             │           │

│  ┌────┴────────────┴────┐      │

│  │     课堂编排系统       │      │

│  └───────────┬───────────┘      │

│              ↓                  │

│  ┌─────────────────────────┐    │

│  │   生成：课件+测验+视频  │    │

│  └─────────────────────────┘    │

└─────────────────────────────────┘

↓

输出：完整AI课堂（幻灯片+测验+视频）

---

## 安装部署

### 方式1: Docker一键部署（推荐）

# 克隆仓库

git clone https://github.com/THU-MAIC/OpenMAIC.git

cd OpenMAIC

# Docker启动

docker-compose up -d

# 访问

# http://localhost:3000

### 方式2: 本地安装

# Python环境要求

python >= 3.10

# 安装依赖

pip install openmaic

# 启动

python -m openmaic.app

---

## 使用流程

### 1. 创建课堂

# 方式1: Web界面

# 访问 http://localhost:3000

# 输入主题："机器学习基础"

# 选择：课程长度、难度、角色数量

# 方式2: 命令行

openmaic create --topic "机器学习基础" --duration long

### 2. 生成内容

# 输入源类型

# - 主题描述

# - PDF文档

# - 视频文件

# - 网页链接

# 示例：从PDF生成

openmaic generate --input lecture.pdf --type pdf

### 3. 生成课堂视频

# 生成完整课堂视频

openmaic video --duration 45 --style lecture

# 参数

# --duration: 视频时长（分钟）

# --style: lecture/classroom/debate

# --agents: 参与角色数量

---

## 演示案例

### 案例：生成"人工智能导论"课堂

# Step 1: 创建项目

openmaic create --topic "人工智能导论" --level beginner