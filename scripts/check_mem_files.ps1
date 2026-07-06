Get-ChildItem 'E:\workspace\memory\2026-*.md' | ForEach-Object {
    $lines = @(Get-Content $_.FullName -Tail 3 -Encoding UTF8)
    $combined = $lines -join "|"
    $hasMarker = $combined -match 'consolidated|consolidation'
    $status = if($hasMarker){'OK'}else{'MISSING'}
    Write-Output "$($_.Name): $status"
}
