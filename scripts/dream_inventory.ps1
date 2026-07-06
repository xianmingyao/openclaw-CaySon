# Dream Phase 1 inventory script
Set-Location E:\workspace

$memoryDir = 'E:\workspace\memory'
if (-not (Test-Path $memoryDir)) {
    Write-Host 'memory/ 目录不存在'
    exit 1
}

$files = Get-ChildItem -Path $memoryDir -Filter '*.md' -ErrorAction SilentlyContinue | Sort-Object Name
$totalFiles = $files.Count
$totalLines = 0
$recentFiles = @()
$today = Get-Date
$cutoff = $today.AddDays(-7)
$oldFiles = @()

Write-Host '===== Phase 1 Inventory ====='
Write-Host ('Total files: ' + $totalFiles)

foreach ($f in $files) {
    $lines = (Get-Content $f.FullName | Measure-Object -Line).Lines
    $totalLines += $lines
    if ($f.LastWriteTime -gt $cutoff) {
        $recentFiles += [PSCustomObject]@{
            Name = $f.Name
            Lines = $lines
            LastModified = $f.LastWriteTime.ToString('yyyy-MM-dd HH:mm')
        }
    } else {
        $oldFiles += [PSCustomObject]@{
            Name = $f.Name
            DaysOld = [int]((New-TimeSpan -Start $f.LastWriteTime -End $today).TotalDays)
        }
    }
}

Write-Host ('Total lines: ' + $totalLines)
Write-Host ''
Write-Host '===== Recent files (last 7 days) ====='
$recentFiles | Format-Table -AutoSize | Out-String | Write-Host

Write-Host '===== Old files older than 30 days ====='
$oldFiles30 = $oldFiles | Where-Object { $_.DaysOld -gt 30 }
$oldFiles30Count = ($oldFiles30 | Measure-Object).Count
Write-Host ('Files older than 30 days: ' + $oldFiles30Count)

$marker = 'consolidated to MEMORY.md'
$unmarked = @()
foreach ($o in $oldFiles30) {
    $fpath = Join-Path $memoryDir $o.Name
    $content = Get-Content $fpath -Raw -ErrorAction SilentlyContinue
    if ($content -and $content -notmatch [regex]::Escape($marker)) {
        $unmarked += $o
    }
}
$unmarkedCount = ($unmarked | Measure-Object).Count
Write-Host ('Unmarked older than 30 days: ' + $unmarkedCount)
if ($unmarkedCount -gt 0) {
    $unmarked | Format-Table -AutoSize | Out-String | Write-Host
}
