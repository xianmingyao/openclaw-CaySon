$oldFiles = @('03-27','03-28','03-31','04-02','04-03','04-06','04-07','04-08','04-09','04-10','04-12','04-13')
foreach($f in $oldFiles) {
    $path = "E:\workspace\memory\2026-$f.md"
    if(Test-Path $path) {
        Add-Content -Path $path -Value '' -Encoding UTF8
        Add-Content -Path $path -Value '<!-- consolidated to MEMORY.md on 2026-05-03 -->' -Encoding UTF8
        Write-Output "Marked: 2026-$f.md"
    }
}
