import re

# Read existing douyin.md
with open(r'C:\Users\Administrator\.openclaw\workspace\content-hunter\data\douyin.md', 'r', encoding='utf-8') as f:
    existing_content = f.read()

# Count existing items
existing_items = re.findall(r'### 第(\d+)条', existing_content)
print(f"Existing douyin.md: {len(existing_items)} items")

# Read douyin-ai.md
with open(r'C:\Users\Administrator\.openclaw\workspace\content-hunter\data\douyin-ai.md', 'r', encoding='utf-8', errors='ignore') as f:
    ai_content = f.read()

# Find all items in douyin-ai.md
ai_items = re.findall(r'(### 第\d+条\n.*?)(?=\n### 第\d+条|\n---|\Z)', ai_content, re.DOTALL)
print(f"Found {len(ai_items)} items in douyin-ai.md")

# Also try splitting by "### 第" 
all_items = re.split(r'(?=### 第\d+条)', ai_content)
ai_items2 = [item for item in all_items if item.strip().startswith('### 第')]
print(f"Alternative split: {len(ai_items2)} items")

# Take first 74 items from douyin-ai.md (after existing 26)
items_to_append = ai_items2[:74]
print(f"Will append {len(items_to_append)} items")

# Create the append content with renumbered items
append_lines = []
append_lines.append("\n\n---\n\n## AI人工智能 热门内容（追加）\n")
for i, item in enumerate(items_to_append):
    new_num = 27 + i  # Start from 27
    # Replace the original item number with new number
    renamed = re.sub(r'### 第\d+条', f'### 第{new_num}条', item, count=1)
    append_lines.append(renamed)

# Write to file
with open(r'C:\Users\Administrator\.openclaw\workspace\content-hunter\data\douyin.md', 'w', encoding='utf-8') as f:
    f.write(existing_content)
    f.write(''.join(append_lines))

print(f"Done! douyin.md now should have {26 + 74} = 100 items")

# Verify
with open(r'C:\Users\Administrator\.openclaw\workspace\content-hunter\data\douyin.md', 'r', encoding='utf-8') as f:
    final_content = f.read()
final_items = re.findall(r'### 第(\d+)条', final_content)
print(f"Final count: {len(final_items)} items, range {min(final_items)} to {max(final_items)}")
