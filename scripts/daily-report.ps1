$ErrorActionPreference = "SilentlyContinue"
$workspace = "E:\workspace"
$today = Get-Date -Format "yyyy.MM.dd"
$todayStart = (Get-Date).Date

$out = @()
$out += "=== DAILY REPORT DATA ==="
$out += "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

Push-Location $workspace

# Git commits today
$out += "--- GIT COMMITS ---"
$gitToday = git log --oneline --since="$($todayStart.ToString('yyyy-MM-ddT00:00:00'))" --until="$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')" 2>$null
if ($gitToday) {
    $gitToday | ForEach-Object { $out += "  $_" }
} else {
    $out += "  (none today)"
}

# Modified files today
$out += "--- FILES MODIFIED ---"
$todayFiles = Get-ChildItem -Path $workspace -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -ge $todayStart } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 20

if ($todayFiles) {
    $todayFiles | ForEach-Object {
        $rel = $_.FullName.Replace("$workspace\", "")
        $out += "  $($_.LastWriteTime.ToString('HH:mm')) | $rel"
    }
} else {
    $out += "  (none today)"
}

# Session count
$out += "--- SESSIONS ---"
$sessionFiles = Get-ChildItem "C:\Users\Administrator\.openclaw\agents\main\sessions\*.jsonl" -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -ge $todayStart }
$out += "  Count: $($sessionFiles.Count)"
if ($sessionFiles) {
    $sessionFiles | Select-Object -First 3 | ForEach-Object {
        $out += "  - $($_.Name) [$($_.LastWriteTime.ToString('HH:mm'))]"
    }
}

# Skills
$out += "--- SKILLS ---"
$recentSkills = Get-ChildItem "$workspace\skills" -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -ge $todayStart }
if ($recentSkills) {
    $recentSkills | ForEach-Object { $out += "  + $($_.Name)" }
} else {
    $out += "  (none today)"
}

Pop-Location

# Structured output for AI
$structured = @{
    date = $today
    dayOfWeek = (Get-Date).DayOfWeek.ToString()
    gitCommits = if ($gitToday) { $gitToday } else { ,@() }
    modifiedFiles = @($todayFiles | ForEach-Object { $_.FullName })
    sessionCount = [int]($sessionFiles.Count)
    skillsUpdated = @($recentSkills | ForEach-Object { $_.Name })
} | ConvertTo-Json -Compress -Depth 3

$out += "--- STRUCTURED ---"
$out += $structured

$out | Out-File "$workspace\memory\daily-report-raw.txt" -Encoding UTF8
Write-Output ($out -join "`n")
