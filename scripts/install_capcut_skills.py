import subprocess
import sys

skills = ['capcut-video-editor', 'free-ai-video-editing', 'capcut-ai-video-editor']

for s in skills:
    print(f'Installing {s}...')
    result = subprocess.run(['openclaw', 'skills', 'install', s], 
                          capture_output=True, text=True, encoding='utf-8', errors='replace')
    stdout = result.stdout[:300] if result.stdout else ''
    stderr = result.stderr[:300] if result.stderr else ''
    print(f'  Result: {stdout or stderr}')
    print()
