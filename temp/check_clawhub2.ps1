$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Continue"

$urls = @(
    "https://clawhub.ai/skills/skills/douyin-transcribe-skill",
    "https://clawhub.ai/skills/douyin-transcribe-skill",
    "https://clawhub.com/skills/douyin-transcribe-skill"
)

foreach($u in $urls){
    Write-Host "=== $u ===" -ForegroundColor Cyan
    try {
        $r = Invoke-WebRequest -Uri $u -UseBasicParsing -Headers @{"User-Agent"="Mozilla/5.0";"Accept"="text/html"} -TimeoutSec 20
        Write-Host ("Status: " + $r.StatusCode)
        $html = $r.Content
        # 提取 meta 标签
        $metaMatches = [regex]::Matches($html, '<meta[^>]+(?:property|name)="([^"]+)"[^>]+content="([^"]+)"')
        foreach($m in $metaMatches){
            $name = $m.Groups[1].Value
            $content = $m.Groups[2].Value
            Write-Host ("  " + $name + " = " + $content)
        }
        # 提取 title
        $titleMatch = [regex]::Match($html, '<title>([^<]+)</title>')
        if($titleMatch.Success){
            Write-Host ("  title = " + $titleMatch.Groups[1].Value)
        }
    } catch {
        Write-Host ("ERR: " + $_.Exception.Message)
    }
    Write-Host ""
}

# 也尝试 clawhub 的 API 端点
Write-Host "=== API endpoints ===" -ForegroundColor Cyan
$apis = @(
    "https://clawhub.ai/api/skills/douyin-transcribe-skill",
    "https://clawhub.com/api/v1/skills/douyin-transcribe-skill",
    "https://clawhub.com/api/skills"
)
foreach($u in $apis){
    try {
        $r = Invoke-WebRequest -Uri $u -UseBasicParsing -Headers @{"User-Agent"="Mozilla/5.0";"Accept"="application/json"} -TimeoutSec 15
        Write-Host ("OK " + $u + " Status=" + $r.StatusCode + " len=" + $r.Content.Length)
        if($r.Content.Length -lt 3000){
            Write-Host $r.Content
        } else {
            Write-Host ($r.Content.Substring(0, 3000))
        }
    } catch {
        Write-Host ("ERR " + $u + " " + $_.Exception.Message)
    }
    Write-Host ""
}