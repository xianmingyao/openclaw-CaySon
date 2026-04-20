# CLI工具 5分钟快速上手

> 2026-04-03 精简版

---

## 一句话

**CLI = 命令行控制软件，比GUI自动化稳定10倍**

---

## 安装（2选1）

```bash
# 方式1：CLI-Anything（为软件自动生成CLI）
git clone https://github.com/HKUDS/CLI-Anything.git
cd CLI-Anything && pip install -r requirements.txt

# 方式2：OpenCLI（网站/工具→CLI）
npm install -g opencli
```

---

## 演示案例：GIMP图片处理

**目标：** 让AI用命令行控制GIMP，自动裁剪+导出图片

```bash
# Step 1: 为GIMP生成CLI
python -m cli_anything "C:\Program Files\GIMP 2\bin\gimp-2.10.exe"

# Step 2: 安装生成的CLI
pip install -e ./generated/gimp-cli

# Step 3: AI Agent执行操作
gimp-cli open "photo.jpg"                    # 打开图片
gimp-cli crop "photo.jpg" --x 100 --y 100 --width 500 --height 500  # 裁剪
gimp-cli export "photo.jpg" --format png --output "output.png"       # 导出
```

**你说：** "帮我把这张照片裁剪成正方形，保存为PNG"
**AI做：** 自动执行上面3条命令

---

## 核心对比

| 工具 | 用途 | 安装 |
|------|------|------|
| CLI-Anything | 软件→CLI | `git clone + pip` |
| OpenCLI | 网站→CLI | `npm install -g` |

---

## 记住这个

```
browser-use → 控制浏览器（截图/点击）
CLI-Anything → 控制专业软件（GIMP/Blender/LibreOffice）
OpenCLI → 控制网站（opencli fetch url）
```

---

## 文档位置

- `knowledge/cli-vs-mcp-short.md` - 完整版
- `knowledge/jianying-editor-skill.md` - 剪映Skill
- `knowledge/remotion-video-toolkit.md` - React视频Skill
