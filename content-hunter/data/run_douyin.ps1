$env:NODE_PATH = Split-Path -Parent (Get-Command node).Source
$scriptDir = "E:\workspace\skills\apify-ultimate-scraper\reference\scripts"
$inputJson = @{"hashtag"="AI";"maxItems"=100} | ConvertTo-Json -Compress
$outputFile = "E:\workspace\content-hunter\data\douyin_raw.json"

Write-Host "Running Douyin/TikTok AI hashtag scraper..."
Write-Host "Input: $inputJson"

node "$scriptDir\run_actor.js" --actor "clockworks/tiktok-hashtag-scraper" --input $inputJson --output $outputFile --format json 2>&1
