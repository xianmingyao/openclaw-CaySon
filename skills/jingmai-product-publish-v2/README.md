# 京麦桌面商品上架系统

Python CLI 驱动的京麦桌面商品上架自动化项目。当前以 Excel 输入、京东商品数据补全、Windows UIA 桌面自动化、截图/反思审计为主链路。

## 快速开始

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -e .[dev]
python -m playwright install chromium
copy .env.example .env
jingmai-publish check-config --root .
```

也可以继续使用兼容入口：

```powershell
python cli.py check-config --root .
```

## 常用命令

```powershell
jingmai-publish init-db --root .
jingmai-publish run-import --excel ".\\湖南上架表格.xlsx" --mode draft --root .
jingmai-publish run-desktop-check --step both --debug --root .
jingmai-publish check-evidence --root .
jingmai-publish cleanup-runtime-logs --root .
```

正式发布有人工守卫，必须显式确认：

```powershell
jingmai-publish run-desktop-check --step t8-publish-product --confirm-publish --root .
```

## 调试日志

所有命令支持：

```powershell
--verbose
--log-file logs/cli-debug.log
```
