# -*- coding: utf-8 -*-
"""
MAGMA 实体识别和因果推断
"""
import re
from typing import List, Dict, Tuple
from .core import MemoryNode


class EntityExtractor:
    """实体识别器"""
    
    # 常用模式
    SUBJECT_PATTERNS = [
        r'^([A-Za-z0-9\u4e00-\u9fa5]+)',  # 句首作为主语
    ]
    
    # 概念词汇
    CONCEPT_WORDS = {
        'AI', 'Agent', 'LLM', '模型', '系统', '架构', '设计', '原理',
        '技术', '算法', '框架', '工具', '平台', '服务', '接口', '协议'
    }
    
    def extract(self, content: str) -> Dict[str, List[str]]:
        """
        提取实体
        
        Returns:
            {
                'subjects': [...],
                'objects': [...],
                'concepts': [...]
            }
        """
        result = {
            'subjects': [],
            'objects': [],
            'concepts': []
        }
        
        # 提取引号内容作为实体
        quoted = re.findall(r'[""]([^""]+)[""]', content)
        result['subjects'].extend(quoted[:2])  # 最多2个
        
        # 提取@提及
        mentions = re.findall(r'@(\w+)', content)
        result['subjects'].extend(mentions[:2])
        
        # 提取概念词
        for word in self.CONCEPT_WORDS:
            if word in content:
                result['concepts'].append(word)
        
        # 提取URL作为对象
        urls = re.findall(r'https?://\S+', content)
        if urls:
            result['objects'].append(urls[0][:50])  # 截断
        
        # 提取代码片段引用
        code_refs = re.findall(r'`([^`]+)`', content)
        result['concepts'].extend(code_refs[:3])
        
        # 去重
        result['subjects'] = list(set(result['subjects']))
        result['objects'] = list(set(result['objects']))
        result['concepts'] = list(set(result['concepts']))
        
        return result


class CausalExtractor:
    """因果关系推断器"""
    
    # 因果连接词
    CAUSE_WORDS = {'因为', '由于', '为了', '所以', '导致', '造成', '引起', '因此'}
    EFFECT_WORDS = {'所以', '因此', '导致', '造成', '结果', '使得', '为了'}
    
    def extract(self, content: str, context: Dict = None) -> Dict[str, List[str]]:
        """
        推断因果关系
        
        Returns:
            {
                'causes': [node_id, ...],
                'effects': [node_id, ...],
                'strength': 0.5
            }
        """
        result = {
            'causes': [],
            'effects': [],
            'strength': 0.5
        }
        
        # 简单的关键词检测
        content_lower = content.lower()
        
        # 检测原因标记
        cause_score = 0
        for word in self.CAUSE_WORDS:
            if word in content:
                cause_score += 0.2
        
        # 检测结果标记
        effect_score = 0
        for word in self.EFFECT_WORDS:
            if word in content:
                effect_score += 0.2
        
        # 检测"如果...那么..."模式
        if re.search(r'如果.+,?那么', content):
            cause_score += 0.3
            effect_score += 0.3
        
        # 检测"因为...所以..."模式
        if '因为' in content and '所以' in content:
            cause_score += 0.4
            effect_score += 0.4
        
        # 归一化强度
        total_score = cause_score + effect_score
        if total_score > 0:
            result['strength'] = min(total_score / 2, 1.0)
        
        # 如果有上下文中的相关节点，建立关联
        if context:
            # 查找内容相似的已有节点作为因果关联
            keywords = context.get('keywords', [])
            for kw in keywords[:3]:
                if kw in content_lower:
                    # 找到可能的因果关联
                    pass  # 简化版暂不实现跨节点关联
        
        return result


class KeywordExtractor:
    """关键词提取器"""
    
    STOPWORDS = {
        '的', '了', '是', '在', '和', '与', '或', '以及', '等', '这', '那',
        '有', '没有', '一个', '可以', '我们', '你', '他', '她', '它',
        '什么', '怎么', '如何', '为什么', '因为', '所以', '但是', '然而',
        '然后', '接着', '首先', '其次', '最后', '总之', '因此', '例如'
    }
    
    def extract(self, content: str, max_keywords: int = 10) -> List[str]:
        """提取关键词"""
        # 简单分词
        words = re.findall(r'[\w]+', content)
        
        # 过滤停用词和短词
        keywords = [w for w in words if len(w) >= 2 and w not in self.STOPWORDS]
        
        # 统计词频
        freq = {}
        for w in keywords:
            freq[w] = freq.get(w, 0) + 1
        
        # 按频率排序
        sorted_kw = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        
        return [kw for kw, _ in sorted_kw[:max_keywords]]
