@echo off
:: 京麦 Session1 Helper 启动脚本
:: 用法: 双击此脚本或在命令行运行
:: 需要 Python 环境变量已配置

cd /d "%~dp0"
title 京麦Session1 Helper
echo ========================================
echo 京麦 Session1 Helper
echo 等待命令输入...
echo ========================================
python session1_helper.py
pause
