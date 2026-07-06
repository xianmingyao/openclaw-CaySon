$token = "t-g1044pi8U4W3LI6HVLQwYc7c0Xa5Rj3GkBnDmE2KpZsV9"

$markdownText = @"
📊 **内容捕手汇报 - 2026年4月25日**

**抓取时间：** 2026-04-25 18:00
**数据来源：** 小红书、抖音、B站
**数据量：** 小红书20条 | 抖音20条 | B站14条

---

🔥 **热门内容TOP20**

【小红书】
1. 天台上的富家女，树上的黄毛 → 1.4万点赞 | 本喵叫兔兔
2. 4款春夏必备玛丽珍鞋！ → 1802点赞 | Darrrrcy  
3. 五一出游超漂亮的穿搭 → 2713点赞 | 肥猪靖仔子
4. 靠海吃海，渤海湾带鱼 → 2772点赞 | -肥猪猪的日常
5. 我来东伦敦了 → 2066点赞 | Lady Melody

【抖音】
1. 在性产业合法的地方... → 514.8万播放 | 影视飓风
2. 被一颗荔枝压垮了的盛世 → 67.1万播放 | ZS剪辑
3. 帝王朱砂篇-下 → 144.4万播放 | 山取
4. 贵州遵义烤鸡 → 93.1万播放 | 盗月社食遇记
5. 狗狗的使命2 → 71.8万播放 | 情菜影视

【B站】
1. 我给全校师生朗诵病梅馆记 → 178.3万播放 | 有山先生
2. 真怀念啊姐姐 → 128.6万播放 | 异环
3. 诀别书交响乐现场 → 125.8万播放 | XSO西安交响乐团
4. 消失的城市 → 68.6万播放 | 山河调查局
5. 新华书店有多离谱 → 64.5万播放 | 太阳星sunstar

---

📈 **整体趋势**
1. 知识类内容全面爆发（历史、财经、人文）
2. 五一假期效应明显（出行、穿搭、美食）
3. 长视频受欢迎（25分钟+深度内容）
4. 游戏营销密集（三角洲行动）
5. 治愈系内容稳定（萌宠、美食）

---

📁 **数据保存路径：** `E:\workspace\content-hunter-data\task-2026-04-25-1800\`

---
内容捕手 · 2026-04-25 18:00
"@

$card = @{
  schema = "2.0"
  config = @{ wide_screen_mode = $true }
  body = @{
    elements = @(
    @{
      tag = "markdown"
      content = $markdownText
    }
    )
  }
}

$sendBody = @{
  receive_id = "ou_29ce355d02cb91c7c2f58c8844dc7177"
  receive_id_type = "open_id"
  msg_type = "interactive"
  content = (ConvertTo-Json -InputObject $card -Compress)
}

$header = @{
  Authorization = "Bearer $token"
  Content-Type = "application/json"
}

$jsonBody = ConvertTo-Json -InputObject $sendBody -Compress
$sendResp = Invoke-RestMethod -Uri "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" -Method POST -Header $header -Body ([System.Text.Encoding]::UTF8.GetBytes($jsonBody)) -ContentType "application/json"
Write-Host "Response:"
$sendResp | ConvertTo-Json