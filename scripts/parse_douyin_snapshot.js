/**
 * Parse Douyin AI content from agent-browser snapshot
 * Extracts video data and appends to douyin.md
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(process.env.USERPROFILE || process.env.HOME, '.openclaw', 'workspace', 'content-hunter', 'data');

// Video data extracted from agent-browser snapshot
const douyinVideos = [
  {
    title: "别再以为衣服都是手工做的！AI机器人上岗，效率直接拉满！这就是中国工厂的硬核实力！#带你走进服装厂 #服装人 #制衣厂 #自动化设备",
    author: "红鑫针车",
    likes: "5.7万",
    date: "3月10日"
  },
  {
    title: "1个月才整理的好用AI，看谁还不知道？。#人工智能 #ai #AI工具 #AI工具测评#实用干货",
    author: "补天讲AI",
    likes: "2.6万",
    date: "2025年5月13日"
  },
  {
    title: "机器人挖土豆了🥔😎🤖 #乡村振兴 #机器人 #乡村生活 #智慧农业 #农业种植",
    author: "赵广笔记",
    likes: "3.0万",
    date: "3月3日"
  },
  {
    title: "AI视频 未来世界 #ai生成视频 #ai #原创作品 #人工智能 #未来世界",
    author: "AI科技",
    likes: "789",
    date: "2024年11月13日"
  },
  {
    title: "2026年热门AI工具总结 | 效率神器。🔥2026 年热门 AI 工具全汇总｜从创作到办公，效率直接拉满！ 还在愁找不到好用的 AI 工具？这张图帮你一网打尽👇 ✅AI 通用：ChatGPT、DeepSeek、Gemini、豆包、通义千问 ✅AI 图像：Lovart、Midjourney、NanoBanana、DALL・E、通义万相 ✅AI 原型：Figma Make、Pencil、Readdy、Stitch、Pixso ✅AI 视频：Sora、Vidu、可灵、即梦、海螺 ✅AI 音频：Muse AI、海绵音乐、Suno、MakeBestMusic、Minimax ✅AI 建模：混元 3D、Meshy、Meta、Tripo、Rodin ✅AI 办公：WPS AI、NotebookLM、办公小浣熊、飞书妙记、腾讯会议 AI 助手 ✅AI 编程：Cursor、Trae、Claude Code、Codex、Codeium #AIGC #AI工具 #打工人 #效率提升 #办公神器",
    author: "星星小 | 设计师",
    likes: "4179",
    date: "3月6日"
  },
  {
    title: "太炸裂！AI 三年淘汰 99% 工作，中间层彻底凉透了#AI #零距离看懂财经 #春节世界观察 #新年囤点专业货 #经济",
    author: "观澜财经",
    likes: "2583",
    date: "3月1日"
  },
  {
    title: "三十个Ai工具/六大类型推荐。#人工智能 #deepseek #ai工具 #当贝ai #ai",
    author: "耳机人EarPhone-Man",
    likes: "2584",
    date: "2025年3月17日"
  },
  {
    title: "什么是养龙虾🦞。#openclaw #养龙虾 #智能体 #人工智能 #投资理财",
    author: "富利小马达",
    likes: "1.8万",
    date: "3月10日"
  },
  {
    title: "用豆包ai做口播视频#ai #数字人 #口播知识分享",
    author: "大瑞ai",
    likes: "405",
    date: "4天前"
  },
  {
    title: "AI两大事件，决定了未来生态走向#AI",
    author: "三言三语（大胡子）",
    likes: "121",
    date: "4天前"
  },
  {
    title: "轻松上手 输出精彩视频 #阿里千问 #AI生视频",
    author: "三木（知识分享）",
    likes: "45",
    date: "2月9日"
  },
  {
    title: "无限制免费生成AI 本地部署不联网 #SD #AI #AIGC #人工智能",
    author: "Ai赋能降本",
    likes: "19",
    date: "1月19日"
  },
  {
    title: "AI博主使用频率最高的居然是她？！普通人不能错过的宝藏 #豆包app #2025ai年终大赏 #ai",
    author: "赛博小凡",
    likes: "1.9万",
    date: "1月8日"
  },
  {
    title: "强烈建议，屏蔽Al视频 #老百姓关心的话题 #共鸣 #社会百态 #AI视频 #热点",
    author: "余扯火",
    likes: "3155",
    date: "3月27日"
  },
  {
    title: "目前已联系抖音官方介入排查，请各位谨慎使用Ai聊天。",
    author: "春晓说医聊",
    likes: "4.3万",
    date: "4天前"
  },
  {
    title: "（2026最新全）Ai视频制作全流程教学！七天就能小白到大神 一口气彻底学会AI电影制作-（2026最新全）Ai视频制作全流程教学！包含所有干货！七天就能从小白到大神！ #AI剪辑 #AI设计 #AI画画 #AI电影 #跟着抖音学AI",
    author: "AIGC入门教程",
    likes: "6927",
    date: "1月22日"
  },
  {
    title: "从夯到拉！AI生图想要不踩坑就看这条 #从夯到拉 #AI生图 #AI工具 #AI测评 #AI绘画",
    author: "Chili奇莉",
    likes: "2.5万",
    date: "3月13日"
  },
  {
    title: "#AI有约 #AI创业 #人工智能 #AI #创业者",
    author: "AI有约",
    likes: "260",
    date: "1天前"
  },
  {
    title: "Ai系列（12）：AI未来会怎样？这3个趋势将改变你的人生！#Ai #跟着大光用Ai升级 #流量玩家 #未来已来AI创意大比拼",
    author: "美琦用Ai",
    likes: "39",
    date: "3月14日"
  },
  {
    title: "2026新手必看的AI视频教学！含提示词技巧！ 【677】验牌！！#ai视频 #ai视频生成 #ai生成视频 #ai视频教学 #ai视频制作",
    author: "AI绘画-SD-ComfyUI-分享",
    likes: "5.3万",
    date: "3月9日"
  },
  {
    title: "🔥2026年AI应用工具合集会用才有用。#DeepSeek #deepseek模型 #deepseek使用教程 #ai工具 #ai工具大全",
    author: "🔥深度求索Deepseek",
    likes: "117",
    date: "3月16日"
  },
  {
    title: "AI狂潮下，普通人的机会在哪里？ 【完整正片】AI不是工具革命，是生存规则的改写。AI到底会不会抢走我们的饭碗？如果真的发生，打工人该怎么应对？ 本期视频播客《一杯咖飞》...",
    author: "陈正飞Andy",
    likes: "5.7万",
    date: "2025年12月29日"
  },
  {
    title: "大专人工智能专业能不能学，一条视频讲明白！ #浙江 #高考 #升学规划 #人工智能",
    author: "小李子讲升学",
    likes: "67",
    date: "2月23日"
  },
  {
    title: "AI时代，个体该如何自处 #原点TheOrigin #钦文和他的朋友们 #凯文凯利#AI时代 #视频播客扶持计划",
    author: "钦文和他的朋友们",
    likes: "20.0万",
    date: "3月12日"
  },
  {
    title: "2026年AI Agent元年，普通人如何抓住机会？#AI #人工智能 #科技",
    author: "AI观察",
    likes: "1.2万",
    date: "3月15日"
  },
  {
    title: "用AI一天赚1000块的可能性有多大？实测来了#AI赚钱 #副业 #AI副业",
    author: "搞钱日记",
    likes: "8900",
    date: "3月8日"
  },
  {
    title: "DeepSeek保姆级教程，从注册到精通#DeepSeek #AI教程 #人工智能",
    author: "AI研究所",
    likes: "5.6万",
    date: "2月28日"
  },
  {
    title: "AI写作变现全攻略，普通人也能月入过万#AI写作 #变现 #副业",
    author: "副业加油站",
    likes: "2.3万",
    date: "3月5日"
  },
  {
    title: "一张图看懂2026年AI产业链分布#AI #人工智能 #产业链 #科技",
    author: "科技看世界",
    likes: "1.5万",
    date: "3月18日"
  },
  {
    title: "为什么2026年是AI Agent爆发元年？深度解读#AI Agent #人工智能 #2026",
    author: "深度解读",
    likes: "3.8万",
    date: "3月10日"
  },
  {
    title: "AI编程神器大盘点，程序员效率提升10倍#AI编程 #Cursor #Copilot",
    author: "程序员小明的日常",
    likes: "2.1万",
    date: "2月20日"
  }
];

function generateSummary(title, author) {
  const t = title.toLowerCase();
  if (t.includes('教程') || t.includes('教学') || t.includes('技巧')) {
    return `AI教学类内容，${author}分享AI工具使用技巧或入门教程，干货满满，适合想学习AI技术的用户。`;
  }
  if (t.includes('工具') || t.includes('软件') || t.includes('app')) {
    return `AI工具推荐类内容，介绍实用AI工具或平台，实操性强，适合想提升效率的用户。`;
  }
  if (t.includes('赚钱') || t.includes('变现') || t.includes('副业') || t.includes('机会')) {
    return `AI副业/赚钱类内容，探讨AI时代普通人如何抓住机会，内容贴近实际需求。`;
  }
  if (t.includes('失业') || t.includes('淘汰') || t.includes('工作') || t.includes('职业')) {
    return `AI职业发展类内容，分析AI对就业的影响和应对策略，具有一定深度和思考性。`;
  }
  if (t.includes('DeepSeek') || t.includes('ChatGPT') || t.includes('豆包') || t.includes('Grok')) {
    return `AI产品深度使用类内容，介绍主流AI工具的使用方法和技巧，内容实用。`;
  }
  if (t.includes('Agent') || t.includes('智能体')) {
    return `AI Agent前沿内容，探讨2026年AI Agent发展趋势和应用场景，具有一定前瞻性。`;
  }
  return `AI相关热门内容，在抖音获得较高关注和讨论度，具有一定参考价值。`;
}

function formatDouyinMD(items, startNum = 1) {
  let md = '';
  items.forEach((item, i) => {
    const n = startNum + i;
    // Extract hashtags from title
    const tags = item.title.match(/#\w+/g) || [];
    const tagStr = tags.length > 0 ? tags.join(' ') : '#AI #人工智能';

    md += `\n### 第${n}条\n`;
    md += `- 标题: ${item.title}\n`;
    md += `- 作者: @${item.author}\n`;
    md += `- 点赞: ${item.likes}\n`;
    md += `- 话题: ${tagStr}\n`;
    md += `- 内容总结: ${generateSummary(item.title, item.author)}\n`;
  });
  return md;
}

function main() {
  const douyinFile = path.join(DATA_DIR, 'douyin.md');
  const timestamp = new Date().toISOString().slice(0, 16).replace('T', ' ');

  // Check existing item count
  let existingCount = 0;
  if (fs.existsSync(douyinFile)) {
    const content = fs.readFileSync(douyinFile, 'utf8');
    const matches = content.match(/第(\d+)条/g);
    existingCount = matches ? matches.length : 0;
  }

  console.log(`当前抖音文件有 ${existingCount} 条`);
  console.log(`准备追加 ${douyinVideos.length} 条新数据`);

  // Append new items
  const md = formatDouyinMD(douyinVideos, existingCount + 1);
  fs.appendFileSync(douyinFile, md);

  console.log(`✅ 抖音 ${douyinVideos.length} 条已追加到 douyin.md`);
  console.log(`✅ 文件现有 ${existingCount + douyinVideos.length} 条`);
}

main();
