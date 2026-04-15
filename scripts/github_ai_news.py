"""
扒取AI周报5个项目的GitHub信息
"""
import requests
import re
import json
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def search_github(query, label):
    """搜索GitHub仓库"""
    url = f"https://github.com/search?q={query.replace(' ', '+')}&type=repositories&s=stars"
    print(f"\n{'='*60}")
    print(f"[{label}]")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        r = requests.get(url, headers=headers, timeout=20)
        html = r.text
        
        # 提取仓库列表
        repo_matches = re.findall(
            r'<a href="/([^"]+)"[^>]*class="[^"]*js-snippet-toggle[^"]*"[^>]*>([^<]+)</a>',
            html
        )
        
        # 提取stars
        stars_matches = re.findall(r'<strong>([0-9,.]+[kKmM]?)</strong>.*?(?:star|stars)', html, re.DOTALL)
        
        # 提取描述
        desc_matches = re.findall(
            r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>([^<]+)</p>',
            html
        )
        
        if not repo_matches:
            # 尝试另一种匹配
            repo_matches = re.findall(r'<h3[^>]*><a[^>]*href="/([^"]+)"[^>]*>([^<]+)</a>', html)
        
        print(f"\n找到 {len(repo_matches)} 个结果")
        
        results = []
        for i, match in enumerate(repo_matches[:5]):
            if len(match) == 2:
                repo_path = match[0]
                repo_name = match[1]
            else:
                continue
                
            desc = desc_matches[i] if i < len(desc_matches) else "N/A"
            star = stars_matches[i] if i < len(stars_matches) else "N/A"
            
            # 清理数据
            desc = re.sub(r'<[^>]+>', '', desc).strip()[:100]
            star = star.strip()
            
            result = {
                'name': repo_name.strip(),
                'path': repo_path.strip(),
                'url': f"https://github.com/{repo_path.strip()}",
                'stars': star,
                'desc': desc
            }
            results.append(result)
            
            print(f"\n{i+1}. {result['name']}")
            print(f"   Stars: {result['stars']}")
            print(f"   Desc: {result['desc'][:80]}")
            print(f"   URL: {result['url']}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def main():
    projects = [
        ("Claude+Mythos+Anthropic", "1. Claude Mythos (Anthropic最强模型)"),
        ("GLM-5.1+智谱+开源", "2. GLM-5.1 (智谱最强开源)"),
        ("HappyHorse+阿里+视频模型", "3. HappyHorse (阿里视频模型)"),
        ("Vanast+虚拟试穿", "4. Vanast (虚拟试穿模型)"),
        ("ACE-Step+音乐模型", "5. ACE-Step (Ace音乐模型)"),
    ]
    
    all_results = {}
    
    for query, label in projects:
        print(f"\n\n{'#'*60}")
        print(f"# {label}")
        print(f"{'#'*60}")
        results = search_github(query, label)
        all_results[label] = results
        time.sleep(1)  # 避免限流
    
    # 保存结果
    with open('E:/workspace/OPC/ai_news_5projects.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n✅ 结果已保存到 ai_news_5projects.json")

if __name__ == "__main__":
    main()
