# LibTV-Skill - AI漫剧制作技能

> 学习来源：抖音 @赛博自由老爹《Openclaw隐藏玩法：全流程做AI漫剧》
> 安装日期：2026-04-29
> 版本：huguanjin-libtv-skill v1.0.4

---

## 1. 🎯 这是什么（简介）

**LibTV-Skill** 是 OpenClaw 的 AI 视频/图片生成技能，通过 liblib.tv 平台提供 AI 生成和编辑能力。

- **定位**：AI 漫剧制作全流程工具
- **入口**：OpenClaw SkillHub
- **依赖平台**：liblib.tv（LiblibAI 推出的 AI 视频创作平台）
- **兼容模式**：LibTV 会话 + Gemini 文生图 + Sora/Veo/Grok/豆包/Vidu 视频直连

---

## 2. 📝 关键功能点

### 核心能力矩阵

| 类别 | 功能 | 说明 |
|------|------|------|
| **生成** | 文生图 | 文字描述 → 图片 |
| **生成** | 文生视频 | 文字描述 → 视频 |
| **生成** | 图生视频 | 参考图 → 视频 |
| **生成** | 做动画 | 动画风格视频生成 |
| **编辑** | 元素替换 | 把xxx换成yyy |
| **编辑** | 局部修改 | 局部细节调整 |
| **编辑** | 去掉/加元素 | 去掉xxx、加上xxx |
| **编辑** | 改镜头 | 镜头调整 |
| **风格** | 风格迁移 | 转绘、换风格 |
| **风格** | 视频续写 | 延长视频内容 |
| **复杂创作** | 短剧生成 | 剧本→分镜→成片 |
| **复杂创作** | MV生成 | 音乐+视频 |
| **复杂创作** | 分镜设计 | 故事板生成 |

### 支持模型

- Seedance 2.0
- Kling 3.0/O3
- Wan 2.6
- NanoBanana
- Midjourney
- Seedream 5.0
- Gemini（文生图直连）
- Sora/Veo/Grok/豆包/Vidu（视频直连）

---

## 3. ⚡ 怎么使用

### 环境配置

```bash
# LibTV 会话模式（默认）
export LIBTV_ACCESS_KEY="your-access-key"

# 可选配置
export OPENAPI_IM_BASE="https://im.liblib.tv"  # 默认值

# Gemini / Sora / Veo / Grok / 豆包 / Vidu 直连模式
export API_KEY="your-api-key"
export API_BASE_URL="https://your-api-host"  # 只写域名，不带路径
```

### 核心脚本

```bash
# 1. 创建会话并发送创作需求
python3 {baseDir}/scripts/create_session.py "生一个动漫视频"
python3 {baseDir}/scripts/create_session.py "再生成一张风景图" --session-id SESSION_ID

# 2. 查询会话进展（轮询）
python3 {baseDir}/scripts/query_session.py SESSION_ID --after-seq 5

# 3. 上传参考文件
python3 {baseDir}/scripts/upload_file.py /path/to/image.png

# 4. 下载生成结果
python3 {baseDir}/scripts/download_results.py SESSION_ID --output-dir ./output

# 5. Gemini 文生图
python3 {baseDir}/scripts/gemini_generate_image.py "赛博朋克风格城市夜景" --aspect-ratio 16:9 --image-size 2K

# 6. Sora 视频生成
python3 {baseDir}/scripts/sora_generate_video.py "猫咪听歌摇头晃脑" --model sora-2 --seconds 10

# 7. Vidu 视频生成
python3 {baseDir}/scripts/vidu_generate_video.py "一个美女在雨中跳舞" --seconds 5
```

### 触发词

> 画、生成、做动画、改镜头、换风格、转绘、复刻、liblib、libtv、上传参考图

---

## 4. ✅ 优点

- ✅ **一站式漫剧制作**：覆盖从分镜到成片的全流程
- ✅ **多模型兼容**：集成 Seedance/Kling/Wan 等顶级视频模型
- ✅ **编辑能力强**：局部修改、元素替换等精细化编辑
- ✅ **OpenClaw 集成**：可通过对话式交互触发
- ✅ **直连多平台**：Gemini/Sora/Veo/Grok/豆包/Vidu 视频直连
- ✅ **开源技能**：Apache-2.0 许可证

---

## 5. ❌ 缺点

- ❌ **需要 LibTV API Key**：需注册 liblib.tv 获取 access key
- ❌ **复杂创作耗时长**：短剧、MV 等任务需耐心轮询
- ❌ **文件大小限制**：上传文件需在 200MB 以下
- ❌ **会话模式依赖**：默认模式需要轮询等待

---

## 6. 🎬 使用场景

| 场景 | 适用功能 |
|------|----------|
| **AI 漫剧制作** | 文生图 → 图生视频 → 剪辑 |
| **产品展示片** | 文生视频 + 风格迁移 |
| **MV 制作** | 音乐 + 视频生成 |
| **短剧创作** | 剧本 → 分镜 → 成片 |
| **分镜设计** | 九宫格分镜图生成 |
| **风格复刻** | 参考图风格迁移到新视频 |

---

## 7. 🔧 运行依赖环境

```yaml
环境要求:
  - Python3 (标准库即可，无需额外依赖)
  
必需环境变量:
  - LIBTV_ACCESS_KEY (LibTV 会话模式)
  - API_KEY (直连模式)
  - API_BASE_URL (直连模式)
  
可选配置:
  - OPENAPI_IM_BASE: "https://im.liblib.tv"
```

---

## 8. 🚀 部署使用注意点

### 安装步骤

```bash
# 1. 搜索技能
openclaw skills search libtv

# 2. 安装（推荐最新版）
openclaw skills install huguanjin-libtv-skill

# 3. 配置环境变量
export LIBTV_ACCESS_KEY="your-key"

# 4. 测试运行
python3 {skills_dir}/huguanjin-libtv-skill/scripts/create_session.py "画一只戴墨镜的猫"
```

### 输出格式规范

| 模式 | 展示内容 |
|------|----------|
| **LibTV 任务完成** | 视频/图片URL + projectUrl |
| **Gemini 文生图** | 仅图片 saved 文件路径 |
| **Sora/Veo/Grok/豆包/Vidu** | 仅 videoUrl |

---

## 9. 🕳️ 避坑指南

### 🔴 坑1：用户侧不要扩写 prompt

**问题**：用户说"帮我推演分镜"，Agent 直接传话即可，不要自己扩写

**正确做法**：
```bash
# ✅ 正确：原封不动传话
create_session.py "帮我推演后续的故事，来个分镜大爆炸"

# ❌ 错误：自己先写分镜表再发
create_session.py "对峙→交锋→危机→..."  # 不要自己编！
```

### 🔴 坑2：不要拆解任务步骤

**问题**：把"生成9张分镜图"拆成9次请求

**正确做法**：一次发送，让后端 Agent 编排工作流

### 🔴 坑3：上传文件格式

**问题**：上传非图片/视频文件

**正确做法**：只上传 `image/*` 或 `video/*` 类型，文件 ≤ 200MB

### 🔴 坑4：生成中不要给 projectUrl

**问题**：任务还在生成中就提前展示链接

**正确做法**：只告知"正在生成中"，完成后同时给出**结果链接 + projectUrl**

---

## 10. 📊 总结

| 维度 | 评分 |
|------|------|
| **功能完整性** | ⭐⭐⭐⭐⭐ |
| **漫剧制作适配度** | ⭐⭐⭐⭐⭐ |
| **易用性** | ⭐⭐⭐⭐ |
| **多模型支持** | ⭐⭐⭐⭐⭐ |
| **社区热度** | ⭐⭐⭐⭐ |

**推荐指数**：⭐⭐⭐⭐⭐（5星）

**适用人群**：AI 漫剧创作者、短视频创作者、内容自动化生产

**学习价值**：⭐⭐⭐⭐⭐（5星）

**核心价值**：通过 OpenClaw Skill 实现"用户描述需求 → AI 自动编排工作流 → 漫剧级内容产出"的完整闭环。

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-04-29 | 1.0.4 | 初始安装，记录抖音 @赛博自由老爹 分享的 AI 漫剧制作流程 |
