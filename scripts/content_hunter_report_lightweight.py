"""
轻量级内容捕手汇报脚本 - 直接执行，不走 Agent
直接运行内容抓取，生成简单汇报
"""
import subprocess
import sys
import os
import json
from datetime import datetime

REPORT_DIR = r"E:\workspace\content-hunter-data"
SKILL_DIR = r"C:\Users\Administrator\.openclaw\workspace\content-hunter"
LOG_FILE = r"E:\workspace\logs\content_hunter_report.log"

def log(msg):
    """写入日志"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    print(msg)

def create_task_dir():
    """创建当天任务目录"""
    today = datetime.now().strftime("%Y-%m-%d")
    task_id = datetime.now().strftime("%Y-%m-%d-%H%M")
    task_dir = os.path.join(REPORT_DIR, f"task-{task_id}")
    os.makedirs(task_dir, exist_ok=True)
    return task_dir, today

def run_command(cmd, timeout=300, cwd=None):
    """执行命令"""
    log(f"执行: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
            cwd=cwd
        )
        if result.returncode == 0:
            log(f"✓ 成功")
            return True, result.stdout
        else:
            log(f"✗ 失败 (code={result.returncode})")
            return False, result.stderr[:500] if result.stderr else ""
    except subprocess.TimeoutExpired:
        log(f"✗ 超时 ({timeout}s)")
        return False, "超时"
    except Exception as e:
        log(f"✗ 异常: {e}")
        return False, str(e)

def generate_simple_report(task_dir, data_files):
    """生成简单汇报"""
    report_path = os.path.join(task_dir, "report.md")
    
    content = f"""# 内容捕手汇报 - {datetime.now().strftime("%Y-%m-%d %H:%M")}

## 抓取概况
- 任务目录: {task_dir}
- 数据文件数: {len(data_files)}

## 数据文件
"""
    for f in data_files:
        fname = os.path.basename(f)
        size = os.path.getsize(f)
        content += f"- {fname} ({size} bytes)\n"
    
    content += f"""
## 生成时间
{datetime.now().isoformat()}

---
自动生成 by CaySon
"""
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    log(f"汇报已生成: {report_path}")
    return report_path

def main():
    log("=" * 50)
    log("开始内容捕手汇报")
    
    # 1. 创建任务目录
    task_dir, today = create_task_dir()
    log(f"任务目录: {task_dir}")
    
    # 2. 运行内容抓取 (如果有 content-hunter skill)
    if os.path.exists(SKILL_DIR):
        log("检测到 content-hunter skill")
        # 这里可以调用 skill 的脚本
        # 暂时跳过，因为 skill 可能需要 AI 驱动
    else:
        log("未检测到 content-hunter skill，跳过抓取")
    
    # 3. 查找已有的数据文件
    data_files = []
    data_dir = os.path.join(REPORT_DIR, today)
    if os.path.exists(data_dir):
        data_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith(".md")]
    
    # 4. 生成汇报
    report_path = generate_simple_report(task_dir, data_files)
    
    log("=" * 50)
    log(f"汇报完成: {report_path}")
    
    # 5. 尝试发送到飞书（简单版本）
    try:
        # 读取汇报内容
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
        
        log("汇报内容已保存，可手动查看")
    except Exception as e:
        log(f"读取汇报失败: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
