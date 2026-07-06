openclaw cron add `
  --name "content-hunter-report" `
  --cron "0 18 * * *" `
  --exact `
  --session isolated `
  --timeout-seconds 300 `
  --message "Run: E:\workspace\scripts\content_hunter_report.py" `
  --announce `
  --to "user:ou_29ce355d02cb91c7c2f58c8844dc7177" `
  --description "content-hunter report lightweight"
