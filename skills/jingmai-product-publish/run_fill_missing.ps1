$ErrorActionPreference = "Continue"
$json = Get-Content -Raw -Path "product_row4.json" -Encoding UTF8
$tempFile = [System.IO.Path]::GetTempFileName() + ".json"
[System.IO.File]::WriteAllText($tempFile, $json, [System.Text.Encoding]::UTF8)

Write-Host "=== Filling missing fields on Jingmai ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Make sure Jingmai is on the product form!" -ForegroundColor Yellow
Write-Host ""

cd "E:\workspace\skills\jingmai-product-publish"

& ".venv\Scripts\jm-ufo-agent.exe" run `
    --task-id T001 `
    --row-index 4 `
    --product-json "@$tempFile" `
    --backend webview-act `
    --confirm-real-jingmai `
    --no-observe-only

$exitCode = $LASTEXITCODE

Remove-Item $tempFile -Force

if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Fields filled!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[DONE] Exit code: $exitCode" -ForegroundColor Yellow
}

exit $exitCode
