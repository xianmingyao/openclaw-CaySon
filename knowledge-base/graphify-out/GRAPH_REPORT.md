# Graph Report - knowledge-base  (2026-05-07)

## Corpus Check
- 82 files · ~18,316,775 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 270 nodes · 337 edges · 19 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]

## God Nodes (most connected - your core abstractions)
1. `run_ingest()` - 16 edges
2. `main()` - 13 edges
3. `run_lint_async()` - 9 edges
4. `query_unified()` - 8 edges
5. `sync_pull()` - 8 edges
6. `clip()` - 8 edges
7. `clip_url()` - 8 edges
8. `RawDirectoryHandler` - 7 edges
9. `scan_and_ingest()` - 7 edges
10. `main()` - 7 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Communities

### Community 0 - "Community 0"
Cohesion: 0.19
Nodes (20): append_log(), batch_generate_concept_articles(), call_llm(), compile_single_file(), extract_json_from_response(), get_cache_dir(), get_file_hash(), load_processed_cache() (+12 more)

### Community 1 - "Community 1"
Cohesion: 0.17
Nodes (19): BilibiliClipper, clip(), clip_batch(), clip_url(), detect_platform(), DouyinClipper, extract_bvid(), extract_mp_url() (+11 more)

### Community 2 - "Community 2"
Cohesion: 0.23
Nodes (15): call_llm(), get_skills_content(), get_wiki_content(), log_query(), main(), print_result(), query_once(), query_unified() (+7 more)

### Community 3 - "Community 3"
Cohesion: 0.27
Nodes (10): append_to_log(), get_file_hash(), load_processed_files(), main(), RawDirectoryHandler, run_compile_for_files(), save_processed_files(), scan_and_ingest() (+2 more)

### Community 4 - "Community 4"
Cohesion: 0.27
Nodes (14): create_doc(), get_feishu_config(), get_tenant_access_token(), is_synced(), load_sync_state(), load_wiki_files(), main(), mark_failed() (+6 more)

### Community 5 - "Community 5"
Cohesion: 0.26
Nodes (13): create_notion_database(), create_notion_page(), get_headers(), get_notion_token(), get_or_create_database(), load_wiki_files(), main(), notion_blocks_from_markdown() (+5 more)

### Community 6 - "Community 6"
Cohesion: 0.24
Nodes (13): get_database_id(), get_filtered_pages(), get_notion_token(), get_page_content(), load_last_sync(), notion_api(), notion_blocks_to_markdown(), 获取 Database 页面（API级别过滤，仅返回需要更新的页面）          优化笔记（2026-05-06）：     - 原问题：双重遍历（计数+ (+5 more)

### Community 7 - "Community 7"
Cohesion: 0.27
Nodes (12): check_conflicts(), check_duplicate_titles(), check_empty_short_pages(), check_missing_structure(), check_orphan_links(), extract_links(), generate_log_entry(), main() (+4 more)

### Community 8 - "Community 8"
Cohesion: 0.29
Nodes (11): blocks_to_markdown(), feishu_api(), get_feishu_doc_content(), get_feishu_documents(), get_feishu_token(), load_last_sync(), 将飞书 blocks 转换为 Markdown, 从飞书拉回更新          Returns:         {pulled: int, skipped: int, errors: int} (+3 more)

### Community 9 - "Community 9"
Cohesion: 0.39
Nodes (8): build_graph_data(), export_to_vault(), extract_links(), generate_graph_json(), get_node_type(), main(), 导出到 Obsidian Vault          Args:         vault_path: Obsidian Vault 路径, 生成 Obsidian Graph View 所需的 JSON

### Community 10 - "Community 10"
Cohesion: 0.47
Nodes (8): create_doc(), get_feishu_config(), get_tenant_access_token(), load_sync_state(), main(), markdown_to_blocks(), save_sync_state(), write_blocks_with_retry()

### Community 11 - "Community 11"
Cohesion: 0.47
Nodes (8): create_doc(), get_feishu_config(), get_tenant_access_token(), load_sync_state(), main(), markdown_to_blocks(), save_sync_state(), write_blocks_with_retry()

### Community 12 - "Community 12"
Cohesion: 0.73
Nodes (5): extract_concepts_from_file(), load_state(), log(), main(), save_state()

### Community 13 - "Community 13"
Cohesion: 0.5
Nodes (2): get_all_pages(), notion_api()

### Community 14 - "Community 14"
Cohesion: 0.5
Nodes (2): extract_links(), scan_wiki_pages()

### Community 15 - "Community 15"
Cohesion: 0.7
Nodes (4): get_embedding(), load_wiki_entries(), main(), upload_to_milvus()

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (2): get_all_pages(), notion_api()

### Community 80 - "Community 80"
Cohesion: 1.0
Nodes (1): 处理微信文章 URL（可能需要通过中间页）

### Community 81 - "Community 81"
Cohesion: 1.0
Nodes (1): 抓取 HuggingFace Papers

## Knowledge Gaps
- **24 isolated node(s):** `批量为多个概念生成wiki段落，大幅减少LLM调用`, `导出到 Obsidian Vault          Args:         vault_path: Obsidian Vault 路径`, `生成 Obsidian Graph View 所需的 JSON`, `检查重复标题（相似名称的页面可能是重复的）`, `检查矛盾说法（简化版：检查同一关键词在不同页面的定义）` (+19 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 13`** (5 nodes): `get_all_pages()`, `get_database_id()`, `get_notion_token()`, `notion_api()`, `debug_sync2.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (5 nodes): `lint_quick.py`, `check_orphan_links()`, `check_short_pages()`, `extract_links()`, `scan_wiki_pages()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (3 nodes): `test_full_flow.py`, `get_all_pages()`, `notion_api()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 80`** (1 nodes): `处理微信文章 URL（可能需要通过中间页）`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 81`** (1 nodes): `抓取 HuggingFace Papers`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `批量为多个概念生成wiki段落，大幅减少LLM调用`, `导出到 Obsidian Vault          Args:         vault_path: Obsidian Vault 路径`, `生成 Obsidian Graph View 所需的 JSON` to the rest of the system?**
  _24 weakly-connected nodes found - possible documentation gaps or missing edges._