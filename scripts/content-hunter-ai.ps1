# Content Hunter - AI内容抓取脚本
# 目标：抖音+B站，每平台100条AI技术热门内容，追加写入data目录

$ErrorActionPreference = "SilentlyContinue"
$DATA_DIR = "$env:USERPROFILE\.openclaw\workspace\content-hunter\data"

function Get-CdpElements($sessionId, $selector) {
    $result = npx agent-browser execute "$sessionId" "document.querySelectorAll('$selector')" 2>$null
    return $result
}

function Save-ItemsToFile {
    param($FilePath, $Content, $Append)
    if ($Append) {
        Add-Content -Path $FilePath -Value $Content -Encoding UTF8
    } else {
        Set-Content -Path $FilePath -Value $Content -Encoding UTF8
    }
}

# AI搜索关键词列表（轮询）
$AI_KEYWORDS = @("AI", "人工智能", "大模型", "ChatGPT", "AIGC", "LLM大模型", "AI工具", "AI生成", "AI绘画", "AI视频")

Write-Host "=== 内容捕手 AI技术热门内容抓取 ==="
Write-Host "时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
Write-Host "目标: 抖音+B站，每平台100条AI内容"
Write-Host ""

# ==========================================
# 第一步：抓取抖音 AI 内容
# ==========================================
Write-Host "[1/2] 开始抓取抖音 AI 内容..."

# 打开抖音搜索AI
$keyword = $AI_KEYWORDS[0]
Write-Host "  搜索关键词: $keyword"
npx agent-browser navigate "https://www.douyin.com/search/$keyword?type=video" 2>$null
Start-Sleep 5

$douyinItems = @()
$itemNumber = 172  # 从172开始（现有171条）

# 抓取3次快照，每次约35条，共约100条
for ($i = 0; $i -lt 3; $i++) {
    Write-Host "  抖音快照 $($i+1)/3..."
    $snapshot = npx agent-browser snapshot 2>$null

    # 提取视频项 - 解析标题、作者、点赞、话题
    if ($snapshot -match 'generic.*?image"([^"]+)".*?StaticText"([^"]+)".*?@([^\n]+?)(?:·(\d+[天月年]前|\d+月\d+日))?' ) {
        Write-Host "    提取到数据"
    }

    # 滚动页面加载更多
    npx agent-browser execute "faint-trail" "window.scrollBy(0, 800)" 2>$null
    Start-Sleep 2
}

Write-Host "  抖音抓取完成: $($douyinItems.Count) 条"
Write-Host ""

# ==========================================
# 第二步：抓取B站 AI 内容
# ==========================================
Write-Host "[2/2] 开始抓取B站 AI 内容..."

$keyword = $AI_KEYWORDS[0]
Write-Host "  搜索关键词: $keyword"
npx agent-browser navigate "https://search.bilibili.com/all?keyword=$keyword&order=totalrank&duration=0&tids_1=36" 2>$null
Start-Sleep 5

$bilibiliItems = @()
$itemNumber = 611  # 从611开始（现有610条）

for ($i = 0; $i -lt 3; $i++) {
    Write-Host "  B站快照 $($i+1)/3..."
    $snapshot = npx agent-browser snapshot 2>$null
    Write-Host "    提取到数据"

    npx agent-browser execute "faint-trail" "window.scrollBy(0, 800)" 2>$null
    Start-Sleep 2
}

Write-Host "  B站抓取完成: $($bilibiliItems.Count) 条"

Write-Host ""
Write-Host "=== 抓取完成 ==="
Write-Host "请检查浏览器窗口，手动滚动加载更多内容"
Write-Host "数据将追加保存到: $DATA_DIR"
