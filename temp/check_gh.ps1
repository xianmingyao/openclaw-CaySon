$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Continue"

$urls = @(
    "https://github.com/junweiren98-rgb/douyin-transcribe-skill",
    "https://raw.githubusercontent.com/junweiren98-rgb/douyin-transcribe-skill/main/_meta.json",
    "https://raw.githubusercontent.com/junweiren98-rgb/douyin-transcribe-skill/main/.env.example",
    "https://raw.githubusercontent.com/junweiren98-rgb/douyin-transcribe-skill/main/.gitignore"
)

foreach($u in $urls){
    Write-Host "=== $u ===" -ForegroundColor Cyan
    try {
        $r = Invoke-WebRequest -Uri $u -UseBasicParsing -Headers @{"User-Agent"="Mozilla/5.0"} -TimeoutSec 15
        Write-Host ("Status: " + $r.StatusCode)
        Write-Host $r.Content
    } catch {
        Write-Host ("ERR: " + $_.Exception.Message)
    }
    Write-Host ""
}

# 抓 GitHub 页面查找 license
Write-Host "=== License check ===" -ForegroundColor Cyan
$gh = Invoke-WebRequest -Uri "https://github.com/junweiren98-rgb/douyin-transcribe-skill" -UseBasicParsing -Headers @{"User-Agent"="Mozilla/5.0"} -TimeoutSec 20
$html = $gh.Content
# 查找 license 字段
$licMatches = [regex]::Matches($html, '(?:"licenseInfo"|"spdxId"|license)[^}]{0,200}')
$licMatches | Select-Object -First 5 | ForEach-Object { Write-Host $_.Value }
Write-Host "---"
# 查找 sidebar 区块
$sb = [regex]::Match($html, 'About[\s\S]{0,3000}')
if($sb.Success){
    Write-Host "About section found"
    # 抽取 About 区域里的关键字段
    $about = $sb.Value.Substring(0, [Math]::Min(3000, $sb.Value.Length))
    $licField = [regex]::Match($about, 'octicon-law[^<]*[\s\S]{0,500}')
    if($licField.Success){ Write-Host "License area:"; Write-Host $licField.Value.Substring(0, [Math]::Min(500, $licField.Value.Length)) }
}
Write-Host "---"
# 找 Readme 顶部是否有 license badge
$badgeMatches = [regex]::Matches($html, 'img[^>]+alt="[^"]*[Ll]icense[^"]*"[\s\S]{0,200}')
$badgeMatches | Select-Object -First 3 | ForEach-Object { Write-Host "Badge: $($_.Value.Substring(0, [Math]::Min(200, $_.Value.Length)))" }
# 找仓库大小、tag 标签
Write-Host "---"
$count = [regex]::Matches($html, '"stargazerCount":(\d+)')
if($count.Count -gt 0){ Write-Host ("stargazerCount: " + $count[0].Groups[1].Value) }
$count = [regex]::Matches($html, '"forkCount":(\d+)')
if($count.Count -gt 0){ Write-Host ("forkCount: " + $count[0].Groups[1].Value) }