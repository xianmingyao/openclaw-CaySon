#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
web_clipper.py - 统一 Web Clipper 框架

支持多平台内容抓取，自动存入 raw/ 并触发 ingest

支持的平台：
- Bilibili 视频/专栏
- 抖音视频
-微信公众号文章
- GitHub Issues/PR
- HuggingFace Papers

使用说明：
    python web_clipper.py "URL"                    # 抓取单个 URL
    python web_clipper.py --batch "urls.txt"     # 批量抓取
    python web_clipper.py --bilibili "BV号"       # 抓取 B 站视频
"""

import os
import sys
import re
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# ============== 配置 ==============
RAW_DIR = Path(__file__).parent / "raw"
PROCESSED_URLS = Path(__file__).parent / ".clipper_history.json"
OUTPUT_DIR = RAW_DIR


# ============== 通用工具 ==============

def get_url_hash(url: str) -> str:
    """获取 URL 的短 hash"""
    return hashlib.md5(url.encode()).hexdigest()[:8]


def load_history() -> Dict:
    """加载抓取历史"""
    if PROCESSED_URLS.exists():
        return json.loads(PROCESSED_URLS.read_text(encoding='utf-8'))
    return {}


def save_history(history: Dict):
    """保存抓取历史"""
    PROCESSED_URLS.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding='utf-8')


def save_raw_content(url: str, title: str, content: str, platform: str) -> Path:
    """保存到 raw/ 目录"""
    url_hash = get_url_hash(url)
    timestamp = datetime.now().strftime('%Y%m%d')
    
    safe_title = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', title)[:50]
    filename = f"{timestamp}-{platform}-{url_hash}-{safe_title}.md"
    
    filepath = OUTPUT_DIR / filename
    filepath.write_text(content, encoding='utf-8')
    
    return filepath


# ============== 平台抓取器 ==============

class BilibiliClipper:
    """Bilibili 抓取器"""
    
    @staticmethod
    def extract_bvid(url: str) -> Optional[str]:
        """从 URL 提取 BV 号"""
        patterns = [
            r'BV(\w+)',
            r'bilibili\.com/video/BV(\w+)',
            r'b23\.tv/(\w+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1) if match.group(1) else match.group(0)
        return None
    
    @staticmethod
    def fetch_video_info(bvid: str) -> Dict:
        """获取视频信息（通过 API）"""
        import requests
        
        # B 站 API
        api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        
        try:
            resp = requests.get(api_url, timeout=10)
            data = resp.json()
            
            if data['code'] == 0:
                info = data['data']
                return {
                    'title': info.get('title', ''),
                    'desc': info.get('desc', ''),
                    'author': info.get('owner', {}).get('name', ''),
                    'tname': info.get('tname', ''),
                    'pubdate': info.get('pubdate', 0),
                    'duration': info.get('duration', 0),
                    'stat': info.get('stat', {})
                }
        except Exception as e:
            pass
        
        return {}
    
    @staticmethod
    def clip(url: str) -> Dict:
        """抓取 B 站视频信息"""
        bvid = BilibiliClipper.extract_bvid(url)
        if not bvid:
            return {'success': False, 'error': '无效的 B 站 URL'}
        
        info = BilibiliClipper.fetch_video_info(bvid)
        if not info:
            return {'success': False, 'error': '无法获取视频信息'}
        
        # 生成 Markdown
        content = f"""# {info['title']}

> 平台: Bilibili
> 作者: {info['author']}
> 分类: {info['tname']}
> 发布时间: {datetime.fromtimestamp(info['pubdate']).strftime('%Y-%m-%d')}
> 原始URL: {url}

## 视频信息

- **BV号**: {bvid}
- **时长**: {info['duration']} 秒
- **播放量**: {info['stat'].get('view', 'N/A')}
- **点赞**: {info['stat'].get('like', 'N/A')}
- **投币**: {info['stat'].get('coin', 'N/A')}
- **收藏**: {info['stat'].get('favorite', 'N/A')}
- **分享**: {info['stat'].get('share', 'N/A')}

## 简介

{info['desc']}

---

*由 Web Clipper 自动抓取 | {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        filepath = save_raw_content(url, info['title'], content, 'bilibili')
        
        return {
            'success': True,
            'title': info['title'],
            'filepath': str(filepath),
            'platform': 'bilibili'
        }


class DouyinClipper:
    """抖音抓取器（简化版，需要登录）"""
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """从 URL 提取视频 ID"""
        patterns = [
            r'v\.douyin\.com/(\w+)',
            r'www\.douyin\.com/video/(\d+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def clip(url: str) -> Dict:
        """抓取抖音视频（需要 Cookie）"""
        # 抖音需要登录态，这里返回提示
        return {
            'success': False,
            'error': '抖音抓取需要登录态，请使用 agent-browser 手动抓取',
            'tip': '打开 https://www.douyin.com 登录后，使用 Ctrl+Shift+S 截图保存到 raw/screenshots/'
        }


class WechatClipper:
    """微信公众号抓取器"""
    
    @staticmethod
    def extract_mp_url(url: str) -> Optional[str]:
        """处理微信文章 URL（可能需要通过中间页）"""
        if 'mp.weixin.qq.com' in url:
            return url
        return None
    
    @staticmethod
    def fetch_article(url: str) -> Dict:
        """获取文章内容（简化版）"""
        import requests
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
        }
        
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.encoding = 'utf-8'
            
            # 简单提取标题和正文（实际应该用更复杂的解析）
            title_match = re.search(r'<h1[^>]*id="activity-name"[^>]*>([^<]+)</h1>', resp.text)
            title = title_match.group(1).strip() if title_match else '未知标题'
            
            # 提取正文
            content_match = re.search(r'id="js_content"[^>]*>(.*?)</div>', resp.text, re.DOTALL)
            content = content_match.group(1) if content_match else ''
            
            # 清理 HTML 标签
            content = re.sub(r'<[^>]+>', '', content)
            content = re.sub(r'\s+', '\n', content).strip()
            
            return {'title': title, 'content': content}
            
        except Exception as e:
            return {'title': '', 'content': '', 'error': str(e)}
    
    @staticmethod
    def clip(url: str) -> Dict:
        """抓取微信公众号文章"""
        if not WechatClipper.extract_mp_url(url):
            return {'success': False, 'error': '无效的微信文章 URL'}
        
        article = WechatClipper.fetch_article(url)
        
        if not article.get('title'):
            return {'success': False, 'error': article.get('error', '无法获取文章')}
        
        content = f"""# {article['title']}

> 平台: 微信公众号
> 原文URL: {url}
> 抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 正文

{article['content'][:5000]}

---

*由 Web Clipper 自动抓取 | {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        filepath = save_raw_content(url, article['title'], content, 'wechat')
        
        return {
            'success': True,
            'title': article['title'],
            'filepath': str(filepath),
            'platform': 'wechat'
        }


class HuggingFaceClipper:
    """HuggingFace Papers 抓取器"""
    
    @staticmethod
    def extract_paper_id(url: str) -> Optional[str]:
        """从 URL 提取论文 ID"""
        patterns = [
            r'papers\.huggingface\.co/papers/(\w+)',
            r'arxiv\.org/abs/([\w.]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def clip(url: str) -> Dict:
        """抓取 HuggingFace Papers"""
        paper_id = HuggingFaceClipper.extract_paper_id(url)
        
        if not paper_id:
            return {'success': False, 'error': '无效的 Papers URL'}
        
        # HF Papers 有公开的 API
        import requests
        
        api_url = f"https://huggingface.co/api/papers/{paper_id}"
        
        try:
            resp = requests.get(api_url, timeout=15)
            if resp.status_code != 200:
                return {'success': False, 'error': f'API 返回 {resp.status_code}'}
            
            paper = resp.json()
            
            content = f"""# {paper.get('title', '未知标题')}

> 平台: HuggingFace Papers
> 论文ID: {paper_id}
> 来源: {url}
> 抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 基本信息

- **作者**: {', '.join(paper.get('authors', [])[:5])}
- **发表时间**: {paper.get('published', 'N/A')}
- **热度**: ⬆️ {paper.get('upvotes', 0)} upvotes

## 摘要

{paper.get('abstract', 'N/A')[:2000]}

## 标签

{', '.join(['#' + t for t in paper.get('tags', [])])}

---

*由 Web Clipper 自动抓取 | {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
            
            filepath = save_raw_content(url, paper.get('title', paper_id), content, 'huggingface')
            
            return {
                'success': True,
                'title': paper.get('title', paper_id),
                'filepath': str(filepath),
                'platform': 'huggingface'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


# ============== 路由 ==============

def detect_platform(url: str) -> str:
    """检测 URL 平台"""
    if 'bilibili.com' in url or 'b23.tv' in url:
        return 'bilibili'
    elif 'douyin.com' in url:
        return 'douyin'
    elif 'mp.weixin.qq.com' in url:
        return 'wechat'
    elif 'huggingface.co/papers' in url or 'arxiv.org' in url:
        return 'huggingface'
    elif 'github.com' in url:
        return 'github'
    else:
        return 'generic'


CLIPPERS = {
    'bilibili': BilibiliClipper,
    'douyin': DouyinClipper,
    'wechat': WechatClipper,
    'huggingface': HuggingFaceClipper,
}


def clip_url(url: str) -> Dict:
    """抓取单个 URL"""
    print(f"\n📎 抓取: {url}")
    
    # 检查历史
    history = load_history()
    url_hash = get_url_hash(url)
    
    if url_hash in history:
        print(f"   ⏭️ 已抓取过，跳过")
        return history[url_hash]
    
    # 检测平台
    platform = detect_platform(url)
    print(f"   平台: {platform}")
    
    # 执行抓取
    clipper_class = CLIPPERS.get(platform)
    
    if clipper_class:
        result = clipper_class.clip(url)
    else:
        result = {'success': False, 'error': '暂不支持此平台'}
    
    # 保存历史
    history[url_hash] = result
    save_history(history)
    
    # 输出结果
    if result['success']:
        print(f"   ✅ 已保存: {Path(result['filepath']).name}")
    else:
        print(f"   ❌ {result.get('error', '未知错误')}")
    
    return result


def clip_batch(urls: List[str]) -> List[Dict]:
    """批量抓取"""
    results = []
    
    print(f"\n🔗 批量抓取 {len(urls)} 个 URL")
    print("-" * 50)
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}]", end="")
        result = clip_url(url)
        results.append(result)
        
        # 避免请求过快
        if i < len(urls):
            time.sleep(1)
    
    # 统计
    success = sum(1 for r in results if r.get('success'))
    failed = len(results) - success
    
    print()
    print("=" * 50)
    print(f"[DONE] 成功: {success} / 失败: {failed}")
    
    return results


# ============== 主入口 ==============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Web Clipper - 多平台内容抓取")
    parser.add_argument('url', nargs='?', help='要抓取的 URL')
    parser.add_argument('--batch', '-b', help='批量抓取文件路径')
    parser.add_argument('--list', '-l', nargs='+', help='多个 URL')
    
    args = parser.parse_args()
    
    if args.batch:
        # 批量模式
        urls_file = Path(args.batch)
        if urls_file.exists():
            urls = urls_file.read_text(encoding='utf-8').splitlines()
            urls = [u.strip() for u in urls if u.strip() and not u.startswith('#')]
            clip_batch(urls)
        else:
            print(f"[ERROR] 文件不存在: {args.batch}")
    
    elif args.list:
        # 列表模式
        clip_batch(args.list)
    
    elif args.url:
        # 单个 URL 模式
        result = clip_url(args.url)
        if not result['success']:
            sys.exit(1)
    
    else:
        # 帮助信息
        print(__doc__)
        print("\n支持的平台:")
        for name, clipper in CLIPPERS.items():
            print(f"  • {name}")


if __name__ == '__main__':
    main()
