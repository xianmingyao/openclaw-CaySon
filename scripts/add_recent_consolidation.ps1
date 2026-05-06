$recentFiles = @('04-20','04-23','04-24','04-27','04-28','04-29','04-30')
foreach($f in $recentFiles) {
    $path = "E:\workspace\memory\2026-$f.md"
    if(Test-Path $path) {
        $lastLines = Get-Content $path -Tail 3 -Encoding UTF8
        $combined = $lastLines -join "|"
        if(-not ($combined -match 'consolidated|consolidation')) {
            Add-Content -Path $path -Value '' -Encoding UTF8
            Add-Content -Path $path -Value '<!-- consolidated to MEMORY.md on 2026-05-03 -->' -Encoding UTF8
            Write-Output "Marked: 2026-$f.md"
        } else {
            Write-Output "Already marked: 2026-$f.md"
        }
    }
}
