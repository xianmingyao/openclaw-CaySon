import asyncio
import subprocess
import json
import re

async def get_github_info(query, index):
    """获取GitHub搜索结果"""
    url = f"https://github.com/search?q={query.replace(' ', '+')}&type=repositories"
    
    # 用PowerShell获取页面
    cmd = f'''
    $ErrorActionPreference = 'SilentlyContinue'
    $html = Invoke-WebRequest -Uri "{url}" -UseBasicParsing -TimeoutSec 15
    $html.Content
    '''
    
    try:
        result = subprocess.run(
            ['powershell', '-Command', cmd],
            capture_output=True,
            text=True,
            timeout=20
        )
        html = result.stdout
        
        # 解析HTML提取项目信息
        items = []
        
        # 提取仓库名和链接
        repo_pattern = r'<a href="/([^"]+)"[^>]*class="[^"]*RepoStar[^"]*"[^>]*>'
        repos = re.findall(r'<h3[^>]*><a[^>]*href="/([^"]+)"[^>]*>([^<]+)</a>', html)
        
        # 提取描述
        desc_pattern = r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>([^<]+)</p>'
        descs = re.findall(desc_pattern, html)
        
        # 提取stars
        stars_pattern = r'<strong>([0-9k.]+)</strong>'
        stars = re.findall(stars_pattern, html)
        
        print(f"\n=== {query} ===")
        print(f"URL: {url}")
        
        for i, (repo, name) in enumerate(repos[:5]):
            desc = descs[i] if i < len(descs) else "N/A"
            star = stars[i] if i < len(stars) else "N/A"
            print(f"{i+1}. {name} | Stars: {star}")
            print(f"   {desc[:100]}")
            print(f"   https://github.com/{repo}")
        
        return True
    except Exception as e:
        print(f"Error for {query}: {e}")
        return False

async def main():
    queries = [
        ("Claude+Mythos+Anthropic", "Claude Mythos"),
        ("GLM-5.1+智谱", "GLM-5.1"),
        ("HappyHorse+阿里+视频", "HappyHorse"),
        ("Vanast+虚拟试穿", "Vanast"),
        ("ACE-Step+音乐模型", "ACE-Step"),
    ]
    
    for query, name in queries:
        await get_github_info(query, name)
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
