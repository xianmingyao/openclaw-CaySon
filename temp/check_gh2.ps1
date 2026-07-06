$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Continue"

# 抓 _meta.json 内容
$meta = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/junweiren98-rgb/douyin-transcribe-skill/main/_meta.json" -UseBasicParsing -TimeoutSec 15
Write-Host "=== _meta.json ===" -ForegroundColor Cyan
Write-Host $meta.Content

Write-Host ""
# 抓 README
$rm = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/junweiren98-rgb/douyin-transcribe-skill/main/README.md" -UseBasicParsing -TimeoutSec 15
Write-Host "=== README.md (first 1500 chars) ===" -ForegroundColor Cyan
Write-Host $rm.Content.Substring(0, [Math]::Min(1500, $rm.Content.Length))

Write-Host ""
# 抓 .gitignore
$gi = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/junweiren98-rgb/douyin-transcribe-skill/main/.gitignore" -UseBasicParsing -TimeoutSec 15
Write-Host "=== .gitignore ===" -ForegroundColor Cyan
Write-Host $gi.Content

Write-Host ""
# 抓 .env.example
$env = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/junweiren98-rgb/douyin-transcribe-skill/main/.env.example" -UseBasicParsing -TimeoutSec 15
Write-Host "=== .env.example ===" -ForegroundColor Cyan
Write-Host $env.Content