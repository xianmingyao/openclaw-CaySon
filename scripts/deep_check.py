import os, re

p = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "content-hunter", "data", "bilibili.md")

# Read as bytes
with open(p, 'rb') as f:
    raw = f.read()

print(f"File size: {len(raw)} bytes")
print(f"Byte 0-20: {raw[:20]}")

# Decode as utf-8
try:
    text = raw.decode('utf-8')
    print(f"UTF-8 decoded: {len(text)} chars")
except Exception as e:
    print(f"UTF-8 decode failed: {e}")
    try:
        text = raw.decode('utf-16')
        print(f"UTF-16 decoded: {len(text)} chars")
    except:
        text = ""

# Count markers
marker_count = text.count("###")
print(f"'###' count: {marker_count}")

# Try different patterns
p1 = len(re.findall(r'###\s*第\s*\d+\s*条', text))
p2 = text.count("##")
print(f"Pattern '第X条' count: {p1}")
print(f"'##' count: {p2}")

# Show structure
idx = text.find("###")
if idx >= 0:
    print(f"\nFirst 500 chars from '###':")
    print(text[idx:idx+500])
