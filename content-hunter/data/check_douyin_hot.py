import json
with open('E:\\workspace\\content-hunter\\data\\douyin_hot.json','r',encoding='utf-8') as f:
    data = json.load(f)
print(f'Total: {len(data)} items')
for item in data[:15]:
    word = item.get('word','未知')
    hot = item.get('hot_value',0)
    print(f'  - {word} (hot: {hot})')
