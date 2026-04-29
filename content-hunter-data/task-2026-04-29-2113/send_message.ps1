$msg = Get-Content "E:\workspace\content-hunter-data\task-2026-04-29-2113\report_message.txt" -Raw
& openclaw message send --channel feishu --target ou_29ce355d02cb91c7c2f58c8844dc7177 --message $msg
