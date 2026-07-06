# 港大开源万物皆可RAG：RAG-Anything
日期: 2026-05-19 | 来源: 抖音-骋风算力（第196集）

---

## 一、项目概览

| 项目 | 信息 |
|------|------|
| **项目名** | RAG-Anything |
| **团队** | HKUDS（香港大学数据科学团队） |
| **Stars** | 20.3k ⭐ |
| **定位** | All-in-One Multimodal RAG Framework（万物皆可RAG） |
| **arXiv** | 2510.12323 |
| **基础** | 基于 LightRAG |
| **协议** | 开源 |
| **Discord** | https://discord.gg/yF2MmDJyGJ |

---

## 二、核心问题解决

**痛点**：现代文档包含多模态内容（文本、图片、表格、公式、图表），传统纯文本RAG无法有效处理。

**RAG-Anything解决方案**：统一的全链路多模态文档处理RAG系统，一个框架搞定所有内容类型。

---

## 三、架构流程（5阶段）

```
文档解析 → 内容分析 → 知识图谱 → 智能检索 → 查询回答
   📄           🧠           🔍          🎯
```

### Stage 1: 文档解析
- **MinerU集成**：高保真文档结构提取，保留语义和复杂布局
- **自适应内容分解**：自动分割文本块、视觉元素、表格、数学公式
- **通用格式支持**：PDF、Office(DOC/DOCX/PPT/PPTX/XLS/XLSX)、图片

### Stage 2: 多模态内容理解
- **自主内容分类路由**：自动识别内容类型并路由到优化执行通道
- **并发多Pipeline架构**：文本和图像并行处理，最大化吞吐
- **文档层次结构提取**：提取并保留原始文档层次和元素关系

### Stage 3: 多模态分析引擎
| 分析器 | 功能 |
|--------|------|
| **视觉内容分析** | 图像分析、上下文描述字幕、空间关系提取 |
| **结构化数据解释** | 表格系统解析、统计模式识别、趋势分析 |
| **数学表达式解析** | LaTeX原生支持、概念映射到知识库 |
| **可扩展模态处理器** | 插件架构支持自定义内容类型 |

### Stage 4: 多模态知识图谱索引
- **多模态实体提取**：将内容转换为结构化知识图谱实体
- **跨模态关系映射**：文本实体与多模态组件间的语义连接
- **层次结构保留**：通过"belongs_to"关系链保持逻辑层次
- **加权关系评分**：基于语义 proximity 和上下文重要性

### Stage 5: 模态感知检索
- **向量-图融合**：向量相似度搜索 + 图遍历算法
- **模态感知排名**：根据内容类型相关性加权检索结果
- **关系一致性维护**：保持检索元素间的语义和结构关系

---

## 四、三种查询模式

### 1. 纯文本查询（Text Query）
```python
text_result = await rag.aquery("问题", mode="hybrid")
# 支持模式：hybrid / local / global / naive
```

### 2. VLM增强查询（自动分析图像）
```python
# 当文档含图像时，自动用VLM分析
vlm_result = await rag.aquery(
    "分析图表和数字",
    mode="hybrid"
)
# 自动：检索→加载图像→发送到VLM→综合分析
```

### 3. 多模态查询（指定模态内容）
```python
# 带表格数据查询
result = await rag.aquery_with_multimodal(
    "比较性能指标",
    multimodal_content=[{
        "type": "table",
        "table_data": "Method,Accuracy\nRAGAnything,95.2%",
        "table_caption": "性能对比"
    }],
    mode="hybrid"
)
```

---

## 五、安装使用

### PyPI安装（推荐）
```bash
pip install raganything              # 基础安装
pip install 'raganything[all]'      # 所有功能
pip install 'raganything[image]'    # 图像格式支持
pip install 'raganything[text]'     # 文本文件处理
```

### 源码安装
```bash
git clone https://github.com/HKUDS/RAG-Anything.git
cd RAG-Anything
uv sync --all-extras
uv run python examples/raganything_example.py --help
```

### 依赖要求
- Office文档处理需要 **LibreOffice**
- 图像格式需要 **Pillow**
- 文本格式需要 **ReportLab**

---

## 六、核心代码示例

```python
import asyncio
from raganything import RAGAnything, RAGAnythingConfig

config = RAGAnythingConfig(
    working_dir="./rag_storage",
    parser="mineru",  # mineru / docling / paddleocr
    enable_image_processing=True,
    enable_table_processing=True,
    enable_equation_processing=True,
)

rag = RAGAnything(config=config, llm_model_func=llm_model_func, ...)

# 处理文档
await rag.process_document_complete(
    file_path="document.pdf",
    output_dir="./output"
)

# 查询
result = await rag.aquery("问题", mode="hybrid")
```

---

## 七、HKUDS生态关联

| 项目 | Stars | 定位 |
|------|-------|------|
| **LightRAG** | - | 基础RAG引擎 |
| **RAG-Anything** | 20.3k | 万物皆可RAG（当前） |
| **VideoRAG** | - | 极长上下文视频RAG |
| **MiniRAG** | - | 极简RAG |

---

## 八、学习价值

- **工程价值**: ⭐⭐⭐⭐⭐（5星）- 多模态RAG标准框架
- **研究价值**: ⭐⭐⭐⭐⭐（5星）- arXiv论文支撑
- **实用价值**: ⭐⭐⭐⭐⭐（5星）- 统一多格式文档处理
- **投资价值**: ⭐⭐⭐⭐（4星）- 港大背书，生态完整

---

## 九、关键链接

- GitHub: https://github.com/HKUDS/RAG-Anything
- arXiv: https://arxiv.org/abs/2510.12323
- PyPI: https://pypi.org/project/raganything/
- Discord: https://discord.gg/yF2MmDJyGJ
