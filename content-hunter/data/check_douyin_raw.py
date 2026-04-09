import json

# Check the large douyin raw file
with open("E:\\workspace\\content-hunter\\data\\douyin_raw_1775696874698.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Type: {type(data)}")
if isinstance(data, list):
    print(f"List length: {len(data)}")
    if len(data) > 0:
        print(f"First item keys: {data[0].keys() if isinstance(data[0], dict) else 'N/A'}")
        print(f"First item: {str(data[0])[:200]}")
elif isinstance(data, dict):
    print(f"Dict keys: {data.keys()}")
    # Find aweme_list
    if "aweme_list" in data:
        aweme_list = data["aweme_list"]
        print(f"aweme_list length: {len(aweme_list)}")
        if aweme_list:
            print(f"First aweme: {str(aweme_list[0])[:300]}")
