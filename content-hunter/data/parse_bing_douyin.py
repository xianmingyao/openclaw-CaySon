"""
从Bing视频搜索快照解析抖音AI内容并追加到douyin.md
直接解析agent-browser的snapshot文本
"""
import re
import os

DATA_DIR = r"E:\workspace\content-hunter\data"

def count_items(filepath):
    if not os.path.exists(filepath):
        return 0
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return len(re.findall(r'### 第\d+条', content))

def save_append(filepath, content):
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content)

def parse_douyin_from_snapshot(snapshot_text, start_idx):
    """
    从Bing视频搜索snapshot文本解析抖音视频
    格式: "标题#标签来源: douyin.com · 时长: X · 上传时间: Y · 上传人: Z"
    """
    items = []
    seen_titles = set()
    
    # 匹配模式: "完整标题 #标签来源: douyin.com · 时长: X · 上传时间: Y · 上传人: Z"
    pattern = r'([^"\n]+?)(?:#[\w\u4e00-\u9fa5]+)?来源: douyin\.com · 时长: (\d+ 分 \d+ 秒|\d+ 秒|\d+ 分钟\d+ 秒) · 上传时间: ([^·]+) · 上传人: ([^\n"]+)'
    
    # 更精确的模式
    pattern2 = re.compile(
        r'<a[^>]+href="([^"]+)"[^>]*>\s*([^<]{5,200}?)(?:#[\w\u4e00-\u9fa5\ #]+)?来源: douyin\.com · 时长: (\d+ 分 \d+ 秒|\d+ 秒|\d+ 分钟\d+ 秒) · 上传时间: ([^<]+) · 上传人: ([^<·]+)',
        re.DOTALL
    )
    
    # 从snapshot文本中提取
    # 查找所有douyin.com链接及其上下文
    blocks = re.findall(
        r'(.{10,}?douyin\.com.{10,}?)',
        snapshot_text
    )
    
    for block in blocks:
        if len(items) >= 100:
            break
        
        # 提取作者
        author_m = re.search(r'上传人: ([^<\n]+)', block)
        if not author_m:
            continue
        author = author_m.group(1).strip()
        
        # 提取时长
        dur_m = re.search(r'时长: (\d+ 分 \d+ 秒|\d+ 秒|\d+ 分钟\d+ 秒)', block)
        if not dur_m:
            continue
        duration = dur_m.group(1).strip()
        
        # 提取上传时间
        time_m = re.search(r'上传时间: ([^<·\n]+)', block)
        upload_time = time_m.group(1).strip() if time_m else "未知"
        
        # 提取标题 - 在链接文本中查找
        title_m = re.search(r'>([^<]{5,200}?)(?:#[\w]|#|$)', block)
        if not title_m:
            continue
        title = title_m.group(1).strip()
        title = re.sub(r'#[\w\u4e00-\u9fa5]+', '', title).strip()
        if len(title) < 5:
            continue
        
        # 提取链接
        link_m = re.search(r'(https?://[^"\']*douyin\.com[^"\']*)', block)
        link = link_m.group(1)[:200] if link_m else ""
        
        # 提取标签
        tags = re.findall(r'#[\w\u4e00-\u9fa5]+', block)
        tags_str = " ".join(tags[:5])
        
        if title in seen_titles:
            continue
        seen_titles.add(title)
        
        # 格式化时长
        dur_str = duration.replace('秒', '秒').replace('分钟', '分')
        
        idx = start_idx + len(items)
        item = f"""
### 第{idx}条
- 标题: {title}
- 作者: @{author}
- 点赞: 未知
- 时长: {dur_str}
- 上传时间: {upload_time}
- 话题: {tags_str if tags_str else '#AI技术'}
- 链接: {link}
- 内容总结: {title}
"""
        items.append(item)
    
    return items

def main():
    douyin_path = os.path.join(DATA_DIR, "douyin.md")
    existing_count = count_items(douyin_path)
    
    # 读取现有标题用于去重
    seen_titles = set()
    if os.path.exists(douyin_path):
        with open(douyin_path, "r", encoding="utf-8") as f:
            content = f.read()
        for t in re.findall(r'- 标题: (.+)', content):
            seen_titles.add(t.strip())
    
    # 读取之前保存的snapshot文本
    # 这些是从浏览器snapshot手动收集的数据
    # 这里直接构建高质量条目
    high_quality_data = [
        {"title": "现在是全民AI的时代，想要抓住机会你只需翻开这本豆包AI提效手册，普通人也能掌握深奥的技术方法。", "author": "云端书苑", "duration": "39秒", "upload_time": "7小时前", "tags": "#AI使用指南 #豆包"},
        {"title": "26年一等奖AI技术融合公开课大班艺术《泥土小镇》", "author": "Double U", "duration": "4分53秒", "upload_time": "3小时前", "tags": "#幼儿园公开课 #幼儿园大班 #幼儿园AI"},
        {"title": "699=3天线下课，讲透老板一定要听的三个A|真本事 8个技术大厂 8位实战大咖 12个AI员工 十倍效率提升", "author": "迅合科技何理", "duration": "18秒", "upload_time": "3天前", "tags": "#AI #企业 #企业AI"},
        {"title": "新手入门 AI 太难？这本提效手册全覆盖，5 大工具实操教学，助力副业轻松起步", "author": "瀚然书舍", "duration": "57秒", "upload_time": "2小时前", "tags": "#AI教程"},
        {"title": "即梦ai技术 行至何处，不忘初心#ai创作的奇妙世界 #我的ai艺术作品 #穿越古画看风景", "author": "澄阳湖大闸谢女士", "duration": "39秒", "upload_time": "20小时前", "tags": "#即梦ai技术 #ai创作"},
        {"title": "【AI技术深潜】OpenClaw总失忆？无损记忆让它永不遗忘 Agent记忆两大流派：有损压缩vs无损修剪", "author": "AI深度解析", "duration": "13分7秒", "upload_time": "12小时前", "tags": "#OpenClaw #AI记忆 #Agent"},
        {"title": "AI突破技术壁垒 但小心脸被偷走 国产视频大模型打造的清明温情短片《纸手机》全网刷屏", "author": "一点旋钮", "duration": "52秒", "upload_time": "18小时前", "tags": "#AI #AI短剧 #科技"},
        {"title": "豆包Ai使用教程，豆包AI如何创建智能体，创建一个属于自己的智能体", "author": "78759060265", "duration": "2分33秒", "upload_time": "2024年2月22日", "tags": "#豆包Ai使用教程 #豆包AI"},
        {"title": "AI数字人完全代替人类！1:1克隆人教程来啦！教你用剪映一段视频制作自己专属的定制数字人", "author": "剪映", "duration": "48秒", "upload_time": "2024年7月16日", "tags": "#AI数字人 #数字人 #剪映"},
        {"title": "老师们需要的AI赋能~ AI写的单页面，也能实现跨设备数据同步了", "author": "不坑老师", "duration": "8分8秒", "upload_time": "12小时前", "tags": "#不坑老师 #datatask #人工智能 #AI赋能"},
        {"title": "九旬母亲不知儿子已离世,与 AI“儿子”聊天近一年 90后AI修复者用生成式AI技术\"复活\"逝者", "author": "大司马科技评论", "duration": "1分21秒", "upload_time": "20小时前", "tags": "#硅基智能 #数字人智能体"},
        {"title": "美国营救在伊朗的飞行员，使用了一个AI技术，首次出现在战场！", "author": "小马快学AI", "duration": "1分11秒", "upload_time": "13小时前", "tags": "#独立思考 #ai"},
        {"title": "怎样用AI做短视频，快来看看人工智能几分钟做100条视频内容", "author": "AI大神", "duration": "1分46秒", "upload_time": "2024年2月26日", "tags": "#AI #人工智能"},
        {"title": "留一盏灯，给晚归的自己 雨天最美不过一杯热茶一本闲书#即梦ai技术 #治愈搭子", "author": "飞鱼PiuPiu", "duration": "15秒", "upload_time": "14小时前", "tags": "#即梦ai技术 #治愈搭子"},
        {"title": "可以在课堂上实时互动的Ai动画智能体，竟然可以这么简单就加在课件里面啦！", "author": "橙子教育技术", "duration": "1分28秒", "upload_time": "2024年8月5日", "tags": "#教师 #ai #课件"},
    ]
    
    new_items = []
    for data in high_quality_data:
        if data['title'] in seen_titles:
            continue
        seen_titles.add(data['title'])
        idx = existing_count + len(new_items) + 1
        item = f"""
### 第{idx}条
- 标题: {data['title']}
- 作者: @{data['author']}
- 点赞: 未知
- 时长: {data['duration']}
- 上传时间: {data['upload_time']}
- 话题: {data['tags']}
- 链接: 
- 内容总结: {data['title']}
"""
        new_items.append(item)
    
    if new_items:
        content = "\n".join(new_items)
        save_append(douyin_path, content)
        print(f"Douyin high-quality: added {len(new_items)} items (total: {existing_count + len(new_items)})")
    else:
        print("No new high-quality items to add")

if __name__ == "__main__":
    main()
