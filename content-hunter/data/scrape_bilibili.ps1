# B站AI视频数据抓取
$headers = @{
    'User-Agent' = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    'Referer' = 'https://search.bilibili.com'
}

$keywords = @('AI人工智能', 'ChatGPT', '大模型', 'AIGC', '深度学习', '机器学习')
$allVideos = @()
$seenBVIds = @{}

foreach ($kw in $keywords) {
    Write-Host "Searching: $kw"
    
    for ($page = 1; $page -le 3; $page++) {
        $url = "https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=$kw&page=$page&page_size=30&order=totalrank"
        
        try {
            $response = Invoke-WebRequest -Uri $url -Headers $headers -TimeoutSec 10 -ErrorAction Stop
            $data = $response.Content | ConvertFrom-Json
            
            if ($data.code -ne 0) {
                Write-Host "  API Error: $($data.message)"
                break
            }
            
            $videos = $data.data.result
            if ($videos.Count -eq 0) {
                break
            }
            
            foreach ($v in $videos) {
                $bvid = $v.bvid
                if ($bvid -and -not $seenBVIds.ContainsKey($bvid)) {
                    $seenBVIds[$bvid] = $true
                    
                    $allVideos += [PSCustomObject]@{
                        title = $v.title -replace '<[^>]+>', ''
                        author = $v.author
                        plays = $v.play
                        danmu = $v.video_review
                        likes = $v.like
                        coins = $v.coins
                        favorite = $v.favorite
                        duration = $v.duration
                        bvid = $bvid
                        desc = $v.description
                    }
                }
            }
            
            Write-Host "  Page $page : $($videos.Count) videos"
            Start-Sleep -Milliseconds 500
        }
        catch {
            Write-Host "  Error: $($_.Exception.Message)"
            break
        }
    }
}

Write-Host "`nTotal unique videos: $($allVideos.Count)"

# 生成Markdown
$md = "# B站AI技术热门内容`n`n抓取时间: 2026-04-09`n`n---`n`n"

for ($i = 0; $i -lt [Math]::Min(100, $allVideos.Count); $i++) {
    $v = $allVideos[$i]
    $num = $i + 1
    
    # 清理标题中的HTML
    $title = $v.title -replace '<[^>]+>', ''
    $title = $title -replace '&amp;', '&' -replace '&quot;', '"' -replace '&lt;', '<' -replace '&gt;', '>'
    
    # 格式化描述
    $desc = if ($v.desc) { $v.desc.Substring(0, [Math]::Min(200, $v.desc.Length)) } else { '暂无简介' }
    
    $md += "### 第$num`条`n"
    $md += "- 标题: $title`n"
    $md += "- UP主: $($v.author)`n"
    $md += "- 播放: $($v.plays)`n"
    $md += "- 弹幕: $($v.danmu)`n"
    $md += "- 点赞: $($v.likes)`n"
    $md += "- 投币: $($v.coins)`n"
    $md += "- 收藏: $($v.favorite)`n"
    $md += "- 时长: $($v.duration)`n"
    $md += "- 内容总结: $desc`n`n"
}

# 保存
$md | Out-File -FilePath "E:\workspace\content-hunter\data\bilibili.md" -Encoding UTF8

# 保存JSON
$allVideos | ConvertTo-Json -Depth 10 | Out-File -FilePath "E:\workspace\content-hunter\data\bilibili_videos.json" -Encoding UTF8

Write-Host "Saved $($allVideos.Count) videos to bilibili.md and bilibili_videos.json"
