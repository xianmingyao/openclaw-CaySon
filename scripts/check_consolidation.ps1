Get-ChildItem 'E:\workspace\memory\2026-05-*.md' | ForEach-Object {
    $lines = Get-Content $_.FullName -Tail 5 -Encoding UTF8
    $combined = $lines -join "`n"
    $hasMarker = $combined -match 'consolidated|consolidation'
    $status = if($hasMarker){'OK'}else{'MISSING'}
    Write-Output "$($_.Name): $status"
}
