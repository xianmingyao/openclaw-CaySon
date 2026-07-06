"""扫描 Python 源码中的 f-string SQL 拼接(危险模式)"""
import re, os, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else r'E:\PY\yunfanshujing\GEO-Platform\apps\backend\src'

# 匹配 text(f"...") / text(f'...') / execute(f"...") / f"SELECT ... {var} ..."
patterns = [
    (r'text\(f"[^"]*\{[^"]+\}[^"]*"', 'text(f"...") f-string'),
    (r"text\(f'[^']*\{[^']+\}[^']*'", "text(f'...') f-string"),
    (r'execute\(f"[^"]*\{[^"]+\}[^"]*"', 'execute(f"...") f-string'),
    (r"execute\(f'[^']*\{[^']+\}[^']*'", "execute(f'...') f-string"),
    (r'f"SELECT[^"]*\{', 'f-string SQL with var'),
    (r"f'SELECT[^']*\{", "f-string SQL with var"),
    (r'\.execute\(\s*f"', '.execute(f"...) f-string'),
]

for dirpath, _, filenames in os.walk(ROOT):
    for f in filenames:
        if not f.endswith('.py'): continue
        p = os.path.join(dirpath, f)
        try:
            with open(p, 'r', encoding='utf-8') as fp:
                content = fp.read()
        except Exception:
            continue
        for pat, name in patterns:
            for m in re.finditer(pat, content):
                line_no = content[:m.start()].count('\n') + 1
                snippet = m.group(0)
                rel = p.replace(ROOT, '').lstrip('\\/')
                print(f'{rel}:{line_no}  [{name}]')
                print(f'  >> {snippet[:150]}')
                print()
