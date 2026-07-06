$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Continue"
$urls = @(
    "https://clawhub.com/skills/douyin-transcribe-skill",
    "https://clawhub.com/api/skills/douyin-transcribe-skill",
    "https://www.clawhub.com/skills/douyin-transcribe-skill",
    "https://openclaw.cc/tools/clawhub.html"
)
foreach($u in $urls){
    Write-Host "=== $u ===" -ForegroundColor Cyan
    try {
        $r = Invoke-WebRequest -Uri $u -UseBasicParsing -Headers @{"User-Agent"="Mozilla/5.0";"Accept"="application/json,text/html"} -TimeoutSec 20
        Write-Host ("Status: " + $r.StatusCode)
        $body = $r.Content
        if($body.Length -gt 1500){ $body = $body.Substring(0, 1500) + "..." }
        Write-Host $body
    } catch {
        Write-Host ("ERR: " + $_.Exception.Message)
    }
    Write-Host ""
}