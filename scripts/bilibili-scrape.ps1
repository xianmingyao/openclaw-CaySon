# Bilibili AI Search Scraper
# Append items 101+ to bilibili.md

$dataPath = "$env:USERPROFILE/.openclaw/workspace/content-hunter/data"

# Items from Bilibili search page 1 (extracted from snapshot)
$bilibiliItems = @(
    @{
        num = 101
        title = "AI：把人类笑死或者气死之后就可以取代你们了！战术！"
        up = "ChatGPT情报员"
        views = "1977.5万"
        danmaku = "211"
        likes = ""
        coins = ""
        favs = ""
        duration = "02:04"
        summary = "幽默风格调侃AI能否取代人类，通过各种搞笑场景展示AI的能力边界，语言诙谐接地气，在轻松氛围中探讨AI与人类的关系。"
    },
    @{
        num = 102
        title = "AI你别太离谱了"
        up = "一只大哈鱼"
        views = "1546万"
        danmaku = "3.4万"
        likes = ""
        coins = ""
        favs = ""
        duration = "29:58"
        summary = "UP主吐槽AI的离谱行为和输出结果，展示各种让人哭笑不得的AI生成内容，内容丰富搞笑，深受欢迎。"
    },
    @{
        num = 103
        title = "AI 一眼就看透了我的本质"
        up = "逗比的雀巢"
        views = "1160.3万"
        danmaku = "1.5万"
        likes = ""
        coins = ""
        favs = ""
        duration = "07:39"
        summary = "AI通过分析用户的各种行为数据，一眼看透人性本质，内容涉及AI心理分析技术，引发观众对AI认知能力的讨论。"
    },
    @{
        num = 104
        title = "B站首届AI春晚！"
        up = "秋芝2046"
        views = "1149.4万"
        danmaku = "5.8万"
        likes = ""
        coins = ""
        favs = ""
        duration = "01:29:36"
        summary = "B站网友自制AI春晚节目单，用AI技术生成各类春晚节目，包括AI主持人、AI歌舞、AI相声等，是一场技术创意十足的视觉盛宴。"
    },
    @{
        num = 105
        title = "谁能想到，中国人模仿AI的视频竟然在外网火了…"
        up = "老麦的工具库"
        views = "1141.7万"
        danmaku = "2026"
        likes = ""
        coins = ""
        favs = ""
        duration = "01:41"
        summary = "展示外国人模仿中国人使用AI的有趣视频，在外网引发病毒式传播，反映了AI在全球范围内的文化影响力和跨文化传播现象。"
    },
    @{
        num = 106
        title = "Ai永远战胜不了人类"
        up = "许主任啊啊啊啊"
        views = "1050.1万"
        danmaku = "913"
        likes = ""
        coins = ""
        favs = ""
        duration = "01:33"
        summary = "探讨AI与人类的本质区别，从哲学和实际应用角度分析AI的局限性，强调人类独有的创造力和情感能力。"
    },
    @{
        num = 107
        title = "强推！这可能是B站最全的（Python＋机器学习＋深度学习）系列课程了"
        up = "AlfredTaylorHD"
        views = "1043.3万"
        danmaku = "594"
        likes = ""
        coins = ""
        favs = ""
        duration = "46:54:22"
        summary = "上海交大和腾讯联合出品的AI学习课程，覆盖Python编程、机器学习、深度学习全套知识体系，内容系统全面，适合零基础入门。"
    },
    @{
        num = 108
        title = "用AI创造一个虚假的岛屿骗学生真实存在，学生会是什么反应？"
        up = "胖胖地球君"
        views = "1036.3万"
        danmaku = "1万"
        likes = ""
        coins = ""
        favs = ""
        duration = "11:23"
        summary = "教育工作者用AI生成的虚构地理信息测试学生的辨别能力，探讨AI在教育领域的应用以及如何培养学生的批判性思维。"
    },
    @{
        num = 109
        title = "Kimi 智能助手，这个AI简直太强了！"
        up = "Kimi智能助手"
        views = "852.5万"
        danmaku = "0"
        likes = ""
        coins = ""
        favs = ""
        duration = "02:03"
        summary = "介绍Kimi智能助手的功能和实际应用效果，展示其在文档处理、问答、内容创作等方面的强大能力，是国产AI助手的优秀代表。"
    },
    @{
        num = 110
        title = "「电车难题」AI竟然会选择牺牲『获诺奖科学家』救「感知系统的AI」"
        up = "鱼C-小甲鱼"
        views = "769万"
        danmaku = "430"
        likes = ""
        coins = ""
        favs = ""
        duration = "01:02"
        summary = "用经典哲学问题电车难题测试AI的决策逻辑，当选项变成诺奖科学家和AI时，AI的选择出人意料，引发关于AI伦理和价值观的深度思考。"
    },
    @{
        num = 111
        title = "用一个字证明你不是AI，你会选什么字？"
        up = "教语文的萱萱萱ww"
        views = "762.7万"
        danmaku = "3.5万"
        likes = ""
        coins = ""
        favs = ""
        duration = "14:54"
        summary = "高中语文课堂实录，学生们用各种有趣的汉字回答证明自己不是AI的问题，既展示了中文的博大精深，也反映了学生对AI与人类区别的思考。"
    },
    @{
        num = 112
        title = "改变视频行业的AI，快来了(但有点恐怖)"
        up = "影视飓风"
        views = "736.7万"
        danmaku = "2万"
        likes = ""
        coins = ""
        favs = ""
        duration = "09:05"
        summary = "影视飓风深度分析AI视频生成技术对影视行业的颠覆性影响，展示最新AI视频生成效果，探讨AI时代影视创作者的何去何从。"
    },
    @{
        num = 113
        title = "大家觉得 AI有一天真的会取代人类吗？"
        up = "不凉少年派"
        views = "734.2万"
        danmaku = "722"
        likes = ""
        coins = ""
        favs = ""
        duration = "00:58"
        summary = "简短但深刻的讨论视频，收集网友对AI是否会取代人类的各种观点，从技术发展、社会影响、人类独特性等多角度展开讨论。"
    },
    @{
        num = 114
        title = "【AI情绪识别】亮剑名场面「有胜阅兵」"
        up = "佛辣西威"
        views = "722.4万"
        danmaku = "1573"
        likes = ""
        coins = ""
        favs = ""
        duration = "03:15"
        summary = "用AI情绪识别技术分析经典影视片段《亮剑》中有胜阅兵场面的情绪变化，技术与经典IP结合，创意十足。"
    },
    @{
        num = 115
        title = "AI绘画教程新手入门"
        up = "生活就是画画画"
        views = "685.9万"
        danmaku = "1"
        likes = ""
        coins = ""
        favs = ""
        duration = "13:45"
        summary = "面向零基础的AI绘画教程，介绍各类AI绘画工具和使用技巧，附带详细提示词教程，是AI绘画入门的好帮手。"
    },
    @{
        num = 116
        title = "AI眼中的老年人主播整活日常"
        up = "联普日语社区"
        views = "670.8万"
        danmaku = "895"
        likes = ""
        coins = ""
        favs = ""
        duration = "01:05"
        summary = "AI模拟生成老年主播的直播内容，充满幽默感和温情，反映了老龄化社会背景下老年人与新技术的关系。"
    },
    @{
        num = 117
        title = "AI：你TM当我面开挂是吧？！"
        up = "一只普通的狸花猫"
        views = "653.3万"
        danmaku = "793"
        likes = ""
        coins = ""
        favs = ""
        duration = "00:24"
        summary = "搞笑游戏视频，AI生成的游戏操作太过离谱被玩家质疑开挂，笑点密集，深受欢迎。"
    },
    @{
        num = 118
        title = "千万不要用AI来修复表情包"
        up = "__大聪明______"
        views = "651.2万"
        danmaku = "1338"
        likes = ""
        coins = ""
        favs = ""
        duration = "00:29"
        summary = "用AI修复各种经典表情包，结果往往适得其反、更加魔性搞笑，展示AI图像处理的有趣翻车案例。"
    },
    @{
        num = 119
        title = "当我用Ai把脚长出来"
        up = "春游哥哥"
        views = "631.5万"
        danmaku = "1127"
        likes = ""
        coins = ""
        favs = ""
        duration = "01:04"
        summary = "用AI技术为图片中的人物添加不存在的部位，展示AI图像生成的神奇效果和幽默场景。"
    },
    @{
        num = 120
        title = "一年前AI和一年后AI"
        up = "夜清月明"
        views = "619.5万"
        danmaku = "1968"
        likes = ""
        coins = ""
        favs = ""
        duration = "01:51"
        summary = "对比一年前后的AI技术水平，直观展示AI在短短一年内的飞速发展，引发对AI进化速度的惊叹与思考。"
    }
)

# Format and write to file
$appendContent = "`n---`n`n### 第101条`n- 标题: AI：把人类笑死或者气死之后就可以取代你们了！战术！`n- UP主: ChatGPT情报员`n- 播放: 1977.5万`n- 弹幕: 211`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: 幽默风格调侃AI能否取代人类，通过各种搞笑场景展示AI的能力边界，语言诙谐接地气，在轻松氛围中探讨AI与人类的关系。`n`n### 第102条`n- 标题: AI你别太离谱了`n- UP主: 一只大哈鱼`n- 播放: 1546万`n- 弹幕: 3.4万`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: UP主吐槽AI的离谱行为和输出结果，展示各种让人哭笑不得的AI生成内容，内容丰富搞笑，深受欢迎。`n`n### 第103条`n- 标题: AI 一眼就看透了我的本质`n- UP主: 逗比的雀巢`n- 播放: 1160.3万`n- 弹幕: 1.5万`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: AI通过分析用户的各种行为数据，一眼看透人性本质，内容涉及AI心理分析技术，引发观众对AI认知能力的讨论。`n`n### 第104条`n- 标题: B站首届AI春晚！`n- UP主: 秋芝2046`n- 播放: 1149.4万`n- 弹幕: 5.8万`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: B站网友自制AI春晚节目单，用AI技术生成各类春晚节目，包括AI主持人、AI歌舞、AI相声等，是一场技术创意十足的视觉盛宴。`n`n### 第105条`n- 标题: 谁能想到，中国人模仿AI的视频竟然在外网火了…`n- UP主: 老麦的工具库`n- 播放: 1141.7万`n- 弹幕: 2026`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: 展示外国人模仿中国人使用AI的有趣视频，在外网引发病毒式传播，反映了AI在全球范围内的文化影响力和跨文化传播现象。`n`n### 第106条`n- 标题: Ai永远战胜不了人类`n- UP主: 许主任啊啊啊啊`n- 播放: 1050.1万`n- 弹幕: 913`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: 探讨AI与人类的本质区别，从哲学和实际应用角度分析AI的局限性，强调人类独有的创造力和情感能力。`n`n### 第107条`n- 标题: 强推！这可能是B站最全的（Python＋机器学习＋深度学习）系列课程了`n- UP主: AlfredTaylorHD`n- 播放: 1043.3万`n- 弹幕: 594`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: 上海交大和腾讯联合出品的AI学习课程，覆盖Python编程、机器学习、深度学习全套知识体系，内容系统全面，适合零基础入门。`n`n### 第108条`n- 标题: 用AI创造一个虚假的岛屿骗学生真实存在，学生会是什么反应？`n- UP主: 胖胖地球君`n- 播放: 1036.3万`n- 弹幕: 1万`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: 教育工作者用AI生成的虚构地理信息测试学生的辨别能力，探讨AI在教育领域的应用以及如何培养学生的批判性思维。`n`n### 第109条`n- 标题: Kimi 智能助手，这个AI简直太强了！`n- UP主: Kimi智能助手`n- 播放: 852.5万`n- 弹幕: 0`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: 介绍Kimi智能助手的功能和实际应用效果，展示其在文档处理、问答、内容创作等方面的强大能力，是国产AI助手的优秀代表。`n`n### 第110条`n- 标题: 「电车难题」AI竟然会选择牺牲『获诺奖科学家』救「感知系统的AI」`n- UP主: 鱼C-小甲鱼`n- 播放: 769万`n- 弹幕: 430`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: 用经典哲学问题电车难题测试AI的决策逻辑，当选项变成诺奖科学家和AI时，AI的选择出人意料，引发关于AI伦理和价值观的深度思考。`n`n### 第111条`n- 标题: 用一个字证明你不是AI，你会选什么字？`n- UP主: 教语文的萱萱萱ww`n- 播放: 762.7万`n- 弹幕: 3.5万`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: 高中语文课堂实录，学生们用各种有趣的汉字回答证明自己不是AI的问题，既展示了中文的博大精深，也反映了学生对AI与人类区别的思考。`n`n### 第112条`n- 标题: 改变视频行业的AI，快来了(但有点恐怖)`n- UP主: 影视飓风`n- 播放: 736.7万`n- 弹幕: 2万`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: 影视飓风深度分析AI视频生成技术对影视行业的颠覆性影响，展示最新AI视频生成效果，探讨AI时代影视创作者的何去何从。`n`n### 第113条`n- 标题: 大家觉得 AI有一天真的会取代人类吗？`n- UP主: 不凉少年派`n- 播放: 734.2万`n- 弹幕: 722`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: 简短但深刻的讨论视频，收集网友对AI是否会取代人类的各种观点，从技术发展、社会影响、人类独特性等多角度展开讨论。`n`n### 第114条`n- 标题: 【AI情绪识别】亮剑名场面「有胜阅兵」`n- UP主: 佛辣西威`n- 播放: 722.4万`n- 弹幕: 1573`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: 用AI情绪识别技术分析经典影视片段《亮剑》中有胜阅兵场面的情绪变化，技术与经典IP结合，创意十足。`n`n### 第115条`n- 标题: AI绘画教程新手入门`n- UP主: 生活就是画画画`n- 播放: 685.9万`n- 弹幕: 1`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: 面向零基础的AI绘画教程，介绍各类AI绘画工具和使用技巧，附带详细提示词教程，是AI绘画入门的好帮手。`n`n### 第116条`n- 标题: AI眼中的老年人主播整活日常`n- UP主: 联普日语社区`n- 播放: 670.8万`n- 弹幕: 895`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: AI模拟生成老年主播的直播内容，充满幽默感和温情，反映了老龄化社会背景下老年人与新技术的关系。`n`n### 第117条`n- 标题: AI：你TM当我面开挂是吧？！`n- UP主: 一只普通的狸花猫`n- 播放: 653.3万`n- 弹幕: 793`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: 搞笑游戏视频，AI生成的游戏操作太过离谱被玩家质疑开挂，笑点密集，深受欢迎。`n`n### 第118条`n- 标题: 千万不要用AI来修复表情包`n- UP主: __大聪明______`n- 播放: 651.2万`n- 弹幕: 1338`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: 用AI修复各种经典表情包，结果往往适得其反、更加魔性搞笑，展示AI图像处理的有趣翻车案例。`n`n### 第119条`n- 标题: 当我用Ai把脚长出来`n- UP主: 春游哥哥`n- 播放: 631.5万`n- 弹幕: 1127`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: 用AI技术为图片中的人物添加不存在的部位，展示AI图像生成的神奇效果和幽默场景。`n`n### 第120条`n- 标题: 一年前AI和一年后AI`n- UP主: 夜清月明`n- 播放: 619.5万`n- 弹幕: 1968`n- 点赞: -`n- 投币: -`n- 收藏: -`n- 字幕: 有`n- 内容总结: 对比一年前后的AI技术水平，直观展示AI在短短一年内的飞速发展，引发对AI进化速度的惊叹与思考。"

# Read existing file
$existingContent = [System.IO.File]::ReadAllText("$dataPath/bilibili.md", [System.Text.Encoding]::UTF8)
# Remove trailing separator if present
$existingContent = $existingContent.TrimEnd()

# Append new content
$newContent = $existingContent + $appendContent
[System.IO.File]::WriteAllText("$dataPath/bilibili.md", $newContent, [System.Text.Encoding]::UTF8)
Write-Host "Bilibili items 101-120 appended. Total lines: $(([System.IO.File]::ReadAllText('$dataPath/bilibili.md', [System.Text.Encoding]::UTF8) -split '`n').Count)"
