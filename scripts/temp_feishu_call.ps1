$json = @'
{"action":"create_and_write","title":"PaddleOCR Skill for OpenClaw - 解决识别难题","content":"# PaddleOCR Skill for OpenClaw - 解决识别难题\n\n**来源：跟着阿亮学AI（抖音）| 发布时间：2026-03-14**\n\n---\n\n## 痛点问题\n\n- OpenClaw 对低质量图片/PDF 识别不准\n- 大模型都是\"近视眼\"\n- 手写内容和拍摄不规范的图片识别特别差\n\n---\n\n## 解决方案：PaddleOCR Skill\n\nPaddleOCR Skill 是针对 OpenClaw 的免费高精度 PDF 阅读插件。\n\n> \"全球唯一能免费实现高精度 PDF 阅读的 OpenClaw Skill\"\n\n---\n\n## 核心功能\n\n- 免费高精度 OCR 识别\n- 低质量图片优化识别\n- 手写内容识别增强\n- 非规范拍摄图片处理\n- PDF 文档高精度阅读\n\n---\n\n## 使用场景\n\n- 低分辨率图片 OCR\n- 手写文档识别\n- 拍摄不规范的文档处理\n- PDF 内容提取\n- 非高清版资料识别\n\n---\n\n## 价值总结\n\n- 免费 + 高精度 + PDF 阅读\n- 解决 OpenClaw 核心痛点（近视眼问题）\n- 强烈建议每个 OpenClaw 用户安装\n\n---\n\n*数据来源：跟着阿亮学AI抖音图文作品 | 2026-03-14*","folder_token":"33d2bb5417c380f6baaff3467dea91c8"}
'@
$result = npx openclaw tools call feishu_doc --json $json
Write-Host $result
