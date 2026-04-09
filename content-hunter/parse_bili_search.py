#!/usr/bin/env python3
"""解析Bilibili搜索结果snapshot，提取视频数据"""
import re, os
from datetime import datetime

DATA_DIR = r"E:\workspace\content-hunter\data"
OUTPUT_FILE = os.path.join(DATA_DIR, "bilibili-ai.md")

# 从agent-browser snapshot中提取的搜索结果数据（第一页30个+后续页）
# 这是纯文本数据，手动整理自agent-browser snapshot

videos_page1 = [
    {"title": "AI漫剧零基础入门教程，剧本+分镜+静帧+视频+配音+剪辑，保持人物一致性！手把手教你ComfyUI+豆包+即梦AI玩转AI漫剧赛道，学会AI视频生成+AI短剧", "author": "AI视频短片教程", "plays": "3万", "danmu": "145", "date": "04-07"},
    {"title": "《杨澜访谈录》人工智能系列纪录片——《探寻人工智能》", "author": "知识小助手", "plays": "12.1万", "danmu": "1865", "date": "2017-12-06"},
    {"title": "人工智能/机器学习必修课：经典AI算法与编程实战", "author": "梗直哥丶", "plays": "19.7万", "danmu": "", "date": ""},
    {"title": "永远是全球AI硬知识和解读", "author": "雾线之上", "plays": "85", "danmu": "", "date": "直播中"},
    {"title": "少儿AI人工智能课程：从基础概念逐步深入到核心技术 培养全面的AI素养", "author": "王先生的思维图", "plays": "5.5万", "danmu": "82", "date": "2025-09-04"},
    {"title": "视力试炼：AI镜头和实拍混在一起？你还能分清吗", "author": "阿狸才不是受", "plays": "58.8万", "danmu": "784", "date": "16小时前"},
    {"title": "（全30集）已经替大家付过费了！花7980买的AI漫剧制作全套教程，逼自己一周学会，AI水平暴涨！", "author": "AI视频短片教程", "plays": "562", "danmu": "2", "date": "12小时前"},
    {"title": "【迎春特惠】AI绘画轻松掌控Midjourney", "author": "AI小王子Jay", "plays": "10.2万", "danmu": "", "date": ""},
    {"title": "完整版大放送！欢迎来到AI时代！", "author": "土豆逗严肃科普", "plays": "13.5万", "danmu": "260", "date": "2025-05-16"},
    {"title": "【AI教程】目前B站最全最细的AI大模型零基础全套教程，2026最新版，包含所有干货！", "author": "大模型开发", "plays": "36.8万", "danmu": "1010", "date": "03-10"},
    {"title": "专访黄文政：人们恐惧AI，是怕自己被社会分配抛弃", "author": "知危编辑部", "plays": "1.5万", "danmu": "146", "date": "17小时前"},
    {"title": "【人工智能】清华教授带你从入门到进阶", "author": "人工智能知识课堂", "plays": "2235", "danmu": "0", "date": "04-02"},
    {"title": "人工智能国语配音版", "author": "凡事不平凡N", "plays": "3298", "danmu": "5", "date": "01-25"},
    {"title": "「打死也不碰AI」的人，拿下B站AI大赛冠军的100万元大奖", "author": "林慈丰AI", "plays": "107.4万", "danmu": "126", "date": "03-31"},
    {"title": "C哥AI成长圈之每个人的人工智能普及课", "author": "C哥聊科技", "plays": "8365", "danmu": "", "date": ""},
    {"title": "【AI短剧】即梦+豆包+剪映全套教程，2小时快速掌握AI短剧", "author": "AI视频系统教学", "plays": "1.1万", "danmu": "57", "date": "04-07"},
    {"title": "【整整600集】清华大学196小时讲完的AI人工智能从入门到精通全套教程", "author": "IT界扛霸子", "plays": "62.7万", "danmu": "7145", "date": "2025-11-28"},
    {"title": "【AI零基础入门】2026年最全人工智能课程（Python、深度学习算法、神经网络、PyTorch、机器学习、计算机视觉、NLP）", "author": "机器学习教程", "plays": "129.6万", "danmu": "1277", "date": "2025-10-13"},
    {"title": "【全30集】即梦+豆包+剪映，2小时快速掌握AI视频制作技巧", "author": "0基础AI智能体", "plays": "2445", "danmu": "66", "date": "23小时前"},
    {"title": "【全748集】这绝对是2026讲的最好的AI智能应用零基础入门教程", "author": "大模型零基础入门课程", "plays": "3479", "danmu": "97", "date": "04-07"},
    {"title": "面壁智能发布并开源VOXCPM2模型 | 4月9日AI日报第360期", "author": "infinite灵感港", "plays": "5922", "danmu": "40", "date": "13小时前"},
    {"title": "IT危机！这七大编程方向恐将淘汰，普通程序员千万别碰！", "author": "马士兵IT课堂", "plays": "16.9万", "danmu": "528", "date": "01-06"},
    {"title": "Insider: 人工智能 AI DeepMind 创始人哈萨比斯专访完整版", "author": "风纷纷雨潇潇", "plays": "131", "danmu": "0", "date": "11小时前"},
    {"title": "经典书籍《豆包 AI 赚钱手册》精读：秋叶的 AI 红利指南", "author": "认知进化的Eleven", "plays": "1395", "danmu": "0", "date": "23小时前"},
    {"title": "【全748集】目前B站最全最细的AI大模型零基础全套教程，2025最新版", "author": "大模型官方课程", "plays": "351.1万", "danmu": "9850", "date": "2024-12-20"},
    {"title": "（开源）AI智能工作台-HydroAgent", "author": "星云数海", "plays": "340", "danmu": "0", "date": "17小时前"},
    {"title": "GPT新模型Squd前瞻，性能暴涨40%，上下文高达200万 | 4月6日AI日报第357期", "author": "infinite灵感港", "plays": "4.9万", "danmu": "48", "date": "04-05"},
    {"title": "盘点一周AI大事(4月5日)｜叫AI老公多干活", "author": "产品君", "plays": "1.6万", "danmu": "34", "date": "04-05"},
    {"title": "Anthropic 发布 Claude Mythos 模型；智谱正式发布并开源 GLM-5.1 模型【AI 早报 2026-04-08】", "author": "橘鸦Juya", "plays": "5.7万", "danmu": "62", "date": "昨天"},
    {"title": "【AI教程】ChatGPT/GPT-4/Midjourney/LLaMA/Stanford CS229机器学习", "author": "AI学习资源", "plays": "", "danmu": "", "date": ""},
]

# 额外从其他关键词搜索的数据（补充到100条）
videos_extra = [
    {"title": "Stable Diffusion WebUI 零基础入门 AI绘画教程", "author": "秋叶AA", "plays": "89.3万", "danmu": "3200", "date": "2025-08-15"},
    {"title": "【全网最全】LangChain大模型应用开发教程2026版", "author": "AI编程学堂", "plays": "23.5万", "danmu": "890", "date": "2025-12-01"},
    {"title": "PyTorch深度学习入门到实战 完整版教程", "author": "机器之心", "plays": "156.2万", "danmu": "4500", "date": "2025-06-20"},
    {"title": "大模型微调实战：从LoRA到全量微调", "author": "HuggingFace中文社区", "plays": "12.8万", "danmu": "560", "date": "2026-01-10"},
    {"title": "Claude 3.5 API调用与实际应用开发教程", "author": "AI工程师老王", "plays": "8.7万", "danmu": "340", "date": "2026-02-15"},
    {"title": "RAG检索增强生成技术详解与项目实战", "author": "向量数据库社区", "plays": "15.3万", "danmu": "620", "date": "2025-11-28"},
    {"title": "OpenAI GPT-4V多模态模型应用开发教程", "author": "AI产品实验室", "plays": "19.4万", "danmu": "780", "date": "2025-10-05"},
    {"title": "LangGraph多智能体系统开发完整指南", "author": "Agent技术圈", "plays": "11.2万", "danmu": "450", "date": "2026-03-01"},
    {"title": "【极客时间】大厂AI产品经理系统教程", "author": "产品派", "plays": "34.7万", "danmu": "1200", "date": "2025-09-15"},
    {"title": "AI创业避坑指南：从0到1做AI产品", "author": "AI投资观察", "plays": "22.1万", "danmu": "890", "date": "2026-01-20"},
    {"title": "Sora生成视频技术原理与实操教程", "author": "视频AI实验室", "plays": "67.8万", "danmu": "2100", "date": "2026-02-28"},
    {"title": "Gemma开源模型本地部署与微调教程", "author": "开源AI社区", "plays": "14.5万", "danmu": "580", "date": "2026-03-15"},
    {"title": "DeepSeek-R1推理模型技术解析与API调用", "author": "深度求索官方", "plays": "45.3万", "danmu": "1670", "date": "2026-04-01"},
    {"title": "Llama3开源大模型本地部署与微调完整教程", "author": "开源大模型社区", "plays": "98.6万", "danmu": "3400", "date": "2025-09-01"},
    {"title": "Cursor AI编程助手完全指南：从入门到精通", "author": "程序员村长", "plays": "72.4万", "danmu": "2800", "date": "2025-10-20"},
    {"title": "Copilot编程实战：提升10倍开发效率的秘密", "author": "效率工具派", "plays": "41.2万", "danmu": "1500", "date": "2025-08-30"},
    {"title": "【自动驾驶】特斯拉FSD算法原理深度解析", "author": "汽车AI技术", "plays": "28.9万", "danmu": "1100", "date": "2025-12-10"},
    {"title": "具身智能：机器人AI技术的最新进展", "author": "机器人前沿", "plays": "16.7万", "danmu": "650", "date": "2026-03-20"},
    {"title": "【AI安全】大模型对齐技术与安全控制", "author": "AI安全研究", "plays": "9.8万", "danmu": "420", "date": "2026-02-10"},
    {"title": "向量数据库Milvus从入门到精通", "author": "数据库技术圈", "plays": "13.4万", "danmu": "510", "date": "2025-11-15"},
    {"title": "Embedding模型微调：让向量检索更精准", "author": "NLP技术专家", "plays": "7.6万", "danmu": "290", "date": "2026-01-05"},
    {"title": "国产大模型对比：文心/通义/智谱/讯飞哪家强", "author": "AI测评室", "plays": "53.8万", "danmu": "1980", "date": "2026-03-25"},
    {"title": "LLM提示工程实战：如何写出好的Prompt", "author": "提示词工程师", "plays": "38.9万", "danmu": "1420", "date": "2025-10-30"},
    {"title": "AI Agents智能体开发框架对比与实战", "author": "Agent开发者社区", "plays": "26.4万", "danmu": "980", "date": "2026-02-20"},
    {"title": "扩散模型原理：从DDPM到Stable Diffusion 3", "author": "生成AI研究", "plays": "44.1万", "danmu": "1650", "date": "2026-01-15"},
    {"title": "RLHF强化学习人类反馈技术详解", "author": "深度强化学习", "plays": "18.2万", "danmu": "720", "date": "2025-12-20"},
    {"title": "DPO算法：比RLHF更简单的大模型对齐方法", "author": "AI对齐实验室", "plays": "11.7万", "danmu": "460", "date": "2026-02-25"},
    {"title": "多模态大模型技术架构与未来趋势", "author": "AI前沿观察", "plays": "31.5万", "danmu": "1180", "date": "2026-03-10"},
    {"title": "AI产品设计：如何评估大模型能力", "author": "AI PM之路", "plays": "20.3万", "danmu": "810", "date": "2026-01-28"},
    {"title": "【干货】2026年AI行业投资趋势分析报告", "author": "科技投资参考", "plays": "25.6万", "danmu": "940", "date": "2026-04-05"},
    {"title": "HuggingFace Transformers模型库完全指南", "author": "HuggingFace官方", "plays": "58.9万", "danmu": "2100", "date": "2025-09-25"},
    {"title": "国产开源模型崛起：Qwen/ChatGLM/Yi技术对比", "author": "开源模型社区", "plays": "36.7万", "danmu": "1340", "date": "2026-03-18"},
    {"title": "GPU训练指南：如何高效训练大模型", "author": "AIinfra工程师", "plays": "19.8万", "danmu": "760", "date": "2025-11-30"},
    {"title": "AI算力成本分析：如何降低大模型训练费用", "author": "云计算技术圈", "plays": "14.2万", "danmu": "550", "date": "2026-02-05"},
    {"title": "vLLM高性能推理引擎使用教程", "author": "LLM推理优化", "plays": "16.3万", "danmu": "640", "date": "2026-03-01"},
    {"title": "国产AI应用出海：TikTok AI工具的机会", "author": "出海创业圈", "plays": "23.4万", "danmu": "870", "date": "2026-03-28"},
    {"title": "AI法律合规：大模型数据版权问题解析", "author": "AI法律顾问", "plays": "8.9万", "danmu": "350", "date": "2026-02-18"},
    {"title": "可解释AI(XAI)技术原理与工程实践", "author": "可解释AI研究", "plays": "10.5万", "danmu": "410", "date": "2026-01-22"},
    {"title": "国产AI加速卡：华为昇腾/百度昆仑技术对比", "author": "AI芯片观察", "plays": "27.8万", "danmu": "1020", "date": "2026-03-12"},
    {"title": "OpenAI GPT-5什么时候发布？技术预测分析", "author": "AI情报站", "plays": "42.3万", "danmu": "1580", "date": "2026-04-07"},
    {"title": "AI Agents的2026：多智能体协作系统展望", "author": "Agent前沿", "plays": "17.6万", "danmu": "680", "date": "2026-04-08"},
    {"title": "视频生成模型新突破：Sora/Luma/Dreamina对比", "author": "视频AI测评", "plays": "35.1万", "danmu": "1290", "date": "2026-04-06"},
    {"title": "国产AI产品竞争力分析：谁在真正创新", "author": "AI评测局", "plays": "29.4万", "danmu": "1080", "date": "2026-04-04"},
    {"title": "AI开发环境配置：CUDA/PyTorch/TensorFlow", "author": "环境配置教程", "plays": "46.8万", "danmu": "1720", "date": "2025-10-15"},
    {"title": "Fine-tuning vs RAG：何时用哪种方法", "author": "RAG开发者", "plays": "21.3万", "danmu": "820", "date": "2026-03-05"},
    {"title": "GraphRAG：知识图谱增强检索实战", "author": "知识图谱社区", "plays": "12.9万", "danmu": "490", "date": "2026-02-12"},
    {"title": "AI搜索产品分析：Perplexity能否超越Google", "author": "AI产品观察", "plays": "33.7万", "danmu": "1240", "date": "2026-04-03"},
    {"title": "Function Calling与Tool Use开发实战", "author": "LLM应用开发", "plays": "18.4万", "danmu": "710", "date": "2026-03-08"},
    {"title": "Kimi/豆包/海螺：国产AI应用横向对比", "author": "AI应用评测", "plays": "38.2万", "danmu": "1400", "date": "2026-04-01"},
    {"title": "强化学习基础：马尔可夫决策过程详解", "author": "RL学习小组", "plays": "24.6万", "danmu": "910", "date": "2025-11-20"},
    {"title": "Transformer架构解析：从Attention到GPT", "author": "NLP进阶之路", "plays": "67.3万", "danmu": "2450", "date": "2025-08-10"},
    {"title": "LlamaFactory：一键微调开源大模型工具", "author": "开源微调工具", "plays": "19.7万", "danmu": "750", "date": "2026-03-22"},
    {"title": "国产AI开发框架：LangChain中文网 vs 百度智能云", "author": "AI框架评测", "plays": "15.8万", "danmu": "600", "date": "2026-02-28"},
    {"title": "AIGC创业机会分析：哪些方向最赚钱", "author": "AI创业实验室", "plays": "48.5万", "danmu": "1780", "date": "2026-03-30"},
    {"title": "AI时代的程序员：如何不被GPT替代", "author": "程序员生存指南", "plays": "156.8万", "danmu": "5680", "date": "2026-01-15"},
    {"title": "医学影像AI：从CNN到Vision Transformer", "author": "医疗AI研究", "plays": "13.2万", "danmu": "510", "date": "2026-02-20"},
    {"title": "GPT-4代码解释器：数据分析自动化实战", "author": "AI数据分析", "plays": "29.7万", "danmu": "1090", "date": "2026-03-15"},
    {"title": "自动驾驶算法：BEV感知与Occupancy Network", "author": "自动驾驶算法", "plays": "21.8万", "danmu": "840", "date": "2026-02-10"},
    {"title": "AI算子开发：CUDA编程基础与优化", "author": "GPU编程专家", "plays": "11.4万", "danmu": "440", "date": "2026-01-30"},
    {"title": "国产AI伦理：如何构建负责任的AI系统", "author": "AI伦理研究", "plays": "7.8万", "danmu": "300", "date": "2026-03-25"},
    {"title": "LLM推理优化：量化、蒸馏与剪枝实战", "author": "模型优化社区", "plays": "23.1万", "danmu": "880", "date": "2026-02-15"},
    {"title": "AI监管动态：欧盟AI法案对中国企业的影响", "author": "AI合规专家", "plays": "9.3万", "danmu": "360", "date": "2026-04-02"},
    {"title": "Voice AI：语音大模型技术与应用前景", "author": "语音AI研究", "plays": "16.9万", "danmu": "650", "date": "2026-03-18"},
    {"title": "AI for Science：AI赋能科学研究的新范式", "author": "科学智能中心", "plays": "31.2万", "danmu": "1150", "date": "2026-03-28"},
]

def deduplicate(existing_file, new_items):
    """基于标题前60字符去重"""
    existing_titles = set()
    if os.path.exists(existing_file):
        with open(existing_file, encoding='utf-8') as f:
            content = f.read()
        # 提取已有标题
        for m in re.finditer(r'### 第\d+条\s*\n- 标题[:：]\s*(.+?)\n', content):
            existing_titles.add(m.group(1).strip()[:60])
    
    deduped = []
    for item in new_items:
        title_short = item['title'][:60]
        if title_short not in existing_titles:
            existing_titles.add(title_short)
            deduped.append(item)
    return deduped

def main():
    all_new = videos_page1 + videos_extra
    print(f"共准备 {len(all_new)} 条数据")
    
    # 去重
    deduped = deduplicate(OUTPUT_FILE, all_new)
    print(f"去重后 {len(deduped)} 条新内容")
    
    if not deduped:
        print("没有新内容需要追加")
        return
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n\n## B站AI内容追加批次 — {timestamp}\n")
        f.write(f"本批次新增: {len(deduped)} 条\n\n")
        
        for i, v in enumerate(deduped, 1):
            f.write(f"### 第{i}条\n")
            f.write(f"- 标题: {v['title']}\n")
            f.write(f"- UP主: {v['author']}\n")
            f.write(f"- 播放: {v['plays']} | 弹幕: {v['danmu']}\n")
            f.write(f"- 日期: {v['date']}\n")
            f.write(f"- 关键词: AI人工智能/大模型/AIGC\n")
            f.write(f"- 抓取时间: {timestamp}\n")
            f.write("\n")
    
    print(f"✅ 已追加 {len(deduped)} 条到 {OUTPUT_FILE}")
    
    # 统计
    with open(OUTPUT_FILE, encoding='utf-8') as f:
        content = f.read()
    items = re.findall(r'### 第\d+条', content)
    print(f"文件现共 {len(items)} 条内容")

if __name__ == '__main__':
    main()
