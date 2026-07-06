$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Continue"

$urls = @(
    "https://clawhub.com/skills/douyin-transcribe-skill",
    "https://www.clawhub.com/skills/douyin-transcribe-skill"
)

foreach($u in $urls){
    Write-Host "=== $u ===" -ForegroundColor Cyan
    try {
        $r = Invoke-WebRequest -Uri $u -UseBasicParsing -Headers @{"User-Agent"="Mozilla/5.0";"Accept"="text/html"} -TimeoutSec 20
        Write-Host ("Status: " + $r.StatusCode)
        $html = $r.Content
        # 提取 meta 标签
        $metaMatches = [regex]::Matches($html, '<meta[^>]+(?:property|name)="([^"]+)"[^>]+content="([^"]+)"')
        foreach($m in $metaMatches){
            $name = $m.Groups[1].Value
            $content = $m.Groups[2].Value
            if($name -match 'og:|description|title|keywords|license|author'){
                Write-Host ("  " + $name + " = " + $content)
            }
        }
        # 提取 title
        $titleMatch = [regex]::Match($html, '<title>([^<]+)</title>')
        if($titleMatch.Success){
            Write-Host ("  title = " + $titleMatch.Groups[1].Value)
        }
        # 查找 JSON-LD
        $jsonLdMatches = [regex]::Matches($html, '<script type="application/ld\+json">([\s\S]+?)</script>')
        foreach($m in $jsonLdMatches){
            Write-Host ("  ld+json: " + $m.Groups[1].Value.Substring(0, [Math]::Min(500, $m.Groups[1].Value.Length)))
        }
    } catch {
        Write-Host ("ERR: " + $_.Exception.Message)
    }
    Write-Host ""
}