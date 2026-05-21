$skills = @(
    "agent-browser","agent-reach","ai-social-pro","apify-ultimate-scraper","auto-publisher",
    "browser-automation","canvas","caveman","claude-code-runner","cloudbase","competitive-analysis",
    "competitor-teardown","content-generator","content-hunter","context-product-manager",
    "CPO / Chief Product Officer","cron-mastery","customer-persona","desktop-control",
    "desktop-control-1-0-0","diagnose","diagram-generator","diagram-maker","doubao-chat",
    "douyin-transcribe","easy-opencode","edgeone-clawscan","evomap",
    "feature-requirements-clarification","feishu-doc","feishu-drive","feishu-perm",
    "feishu-smart-doc-writer","feishu-wiki","filesystem","find-skills","free-ai-video-editor",
    "free-video-editor","Frontend Design","frontend-design","frontend-design-pro","github",
    "grill-me","hd-infoimage","healthcheck","huashu-nuwa","jianying","jingmai-product-publish",
    "Market Research","mcporter","mem0","memory-dream","memory-hygiene","Mobile",
    "multi-agent-collaboration","multi-search-engine","nano-banana-pro","node-connect",
    "node-inspect-debugger","Office","openclaw-ledger","opencli","opencli-agent",
    "opencli-explorer","opencli-oneshot","opencode","opencode-acp-control","opencode-cli",
    "opencode-controller","openmaic","phoenixclaw-ledger","playwright-cli",
    "playwright-scraper-skill","prd-writer","Product Manager","product-strategy",
    "python-debugpy","ralph-loop","react-best-practices","remotion-video-toolkit",
    "requirements-analysis","searxng","Self-Improving + Proactive Agent",
    "Self-Improving Agent (Proactive Self-Reflection)","shorts-editor","simplify",
    "skill-creator","social-content","social-media-agent","social-media-manager",
    "social-media-publish","spike","taskflow","taskflow-inbox-triage","triple-memory",
    "ui-design","ui-ux-pro-max","user-research","video-frames","video-maker-free","weather",
    "web-access","web-monitor","web-scraper-as-a-service","wechat","wechat-article-scraper",
    "wechat-mp-cn","wechat-video-editor","wiki-knowledge-base","windows-control","wireframe"
)

$baseUrl = "https://matrix.tencent.com/clawscan/skill_security"
$results = @()

foreach ($skill in $skills) {
    $url = "$baseUrl?skill_name=$([Uri]::EscapeDataString($skill))&source=clawhub"
    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 10 -UseBasicParsing
        $content = $response.Content | ConvertFrom-Json
        $verdict = $content.verdict
        $reason = $content.reason
        $results += [PSCustomObject]@{
            Skill = $skill
            Verdict = $verdict
            Reason = $reason
        }
        Write-Host "[$verdict] $skill" -ForegroundColor (
            if ($verdict -eq "safe") { "Green" }
            elseif ($verdict -eq "risky") { "Yellow" }
            elseif ($verdict -eq "malicious") { "Red" }
            else { "Gray" }
        )
    } catch {
        $results += [PSCustomObject]@{
            Skill = $skill
            Verdict = "unknown"
            Reason = "Request failed: $($_.Exception.Message)"
        }
        Write-Host "[unknown] $skill - Request failed" -ForegroundColor Gray
    }
}

$results | Export-Csv -Path "E:\workspace\scripts\skill_scan_results.csv" -NoTypeInformation -Encoding UTF8
Write-Host "`nResults saved to E:\workspace\scripts\skill_scan_results.csv"
