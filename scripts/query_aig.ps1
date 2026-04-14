$skills = @(
  'feishu-doc','feishu-drive','feishu-perm','feishu-wiki','feishu-message',
  'feishu-reaction','feishu-task','feishu-urgent','coding-agent','healthcheck',
  'node-connect','skill-creator','weather','tmux','github','mcporter','summarize',
  'video-frames','find-skills','agent-browser','agent-reach','apify-ultimate-scraper',
  'auto-publisher','cloudbase','content-hunter','frontend-design',
  'playwright-scraper-skill','nano-banana-pro'
)
foreach ($s in $skills) {
  Write-Host "===$s==="
  curl.exe -s "https://matrix.tencent.com/clawscan/skill_security?skill_name=$s&source=clawhub"
  Write-Host ""
}
