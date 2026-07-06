"""Milvus 客户端封装 — 连接 / 集合管理 / 向量搜索。"""

from __future__ import annotations

from typing import Any

from jm_ufo_agent.core.settings import MilvusSettings


class MilvusClient:
    """延迟创建的 Milvus 连接，支持集合创建和向量搜索。"""

    def __init__(self, settings: MilvusSettings):
        """保存 Milvus 配置。"""

        # Milvus 连接通常比较重，构造函数只记录配置。
        # connected 用于后续运行时判断是否完成初始化。
        self.settings = settings
        self.connected = False

    def connect(self) -> Any:
        """连接 Milvus 服务。

        # pymilvus 是可选依赖，不强制安装。
        # alias 固定使用 jingmai_v2，避免污染默认连接名。
        # 成功连接后只标记状态，collection 建模交给 create_collection。
        """

        try:
            from pymilvus import connections
        except ImportError as exc:
            raise RuntimeError("缺少 pymilvus，无法连接 Milvus") from exc
        connections.connect(
            alias="jingmai_v2",
            host=self.settings.host,
            port=str(self.settings.port),
            db_name=self.settings.db,
        )
        self.connected = True
        return connections

    def _ensure_connected(self) -> None:
        """断言已连接。

        # 所有需要与 Milvus 交互的方法都应先调用此方法。
        # 避免在未连接状态下操作导致 pymilvus 抛出难以理解的底层错误。
        """

        if not self.connected:
            raise RuntimeError("未连接 Milvus，请先调用 connect()")

    def create_collection(
        self,
        name: str,
        dimension: int = 768,
        description: str = "",
    ) -> Any:
        """创建向量集合（如不存在）。

        # dimension 默认 768，适配常见 embedding 模型输出维度。
        # 使用 L2 距离度量，适合检索相似失败案例。
        # 自动加载到内存，避免首次查询延迟。
        """

        self._ensure_connected()
        try:
            from pymilvus import Collection, FieldSchema, DataType, CollectionSchema
        except ImportError as exc:
            raise RuntimeError("缺少 pymilvus") from exc

        if Collection.exists(name, using="jingmai_v2"):
            return Collection(name, using="jingmai_v2")

        pk_field = FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True)
        vector_field = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dimension)
        text_field = FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096)
        schema = CollectionSchema(fields=[pk_field, vector_field, text_field], description=description)
        collection = Collection(name=name, schema=schema, using="jingmai_v2")

        # 创建 IVF_FLAT 索引，nlist=128 适合中小规模数据集
        index_params = {"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 128}}
        collection.create_index(field_name="vector", index_params=index_params)
        collection.load()
        return collection

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        top_k: int = 5,
        output_fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """向量相似度搜索。

        # query_vector 维度必须与集合 dimension 一致。
        # output_fields 控制返回哪些标量字段，默认返回 text。
        # 返回列表中每项包含 id, distance, entity。
        """

        self._ensure_connected()
        try:
            from pymilvus import Collection
        except ImportError as exc:
            raise RuntimeError("缺少 pymilvus") from exc

        collection = Collection(collection_name, using="jingmai_v2")
        search_params = {"metric_type": "L2", "params": {"nprobe": 16}}
        results = collection.search(
            data=[query_vector],
            anns_field="vector",
            param=search_params,
            limit=top_k,
            output_fields=output_fields or ["text"],
        )
        # 展平搜索结果为 dict 列表
        output: list[dict[str, Any]] = []
        for hits in results:
            for hit in hits:
                output.append({
                    "id": hit.id,
                    "distance": hit.distance,
                    "entity": hit.entity._row_data if hasattr(hit.entity, "_row_data") else {},
                })
        return output

    # ---- 预定义集合 ----

    def ensure_collections(self) -> dict[str, Any]:
        """确保所有业务集合存在。

        # 设计文档要求 3 个集合：
        # - jingmai_experience: 失败案例经验库（已有，768 维）
        # - jingmai_field_evidence: 字段填充证据库（512 维，轻量 embedding）
        # - jingmai_page_signature: 页面签名库（256 维，截图特征向量）
        # 返回集合名到状态的映射。
        """

        self._ensure_connected()
        collections: dict[str, Any] = {}

        # 1. 经验库（主集合，默认已存在）
        try:
            col = self.create_collection(
                name=self.settings.collection,
                dimension=self.settings.dimension,
                description="失败案例经验库 — L2 检索相似失败场景",
            )
            collections[self.settings.collection] = {"status": "ok", "dimension": self.settings.dimension}
        except Exception as exc:
            collections[self.settings.collection] = {"status": "error", "message": str(exc)}

        # 2. 字段填充证据库
        try:
            col = self.create_collection(
                name="jingmai_field_evidence",
                dimension=512,
                description="字段填充证据 — 检索相似字段的填充策略和验证结果",
            )
            collections["jingmai_field_evidence"] = {"status": "ok", "dimension": 512}
        except Exception as exc:
            collections["jingmai_field_evidence"] = {"status": "error", "message": str(exc)}

        # 3. 页面签名库
        try:
            col = self.create_collection(
                name="jingmai_page_signature",
                dimension=256,
                description="页面签名 — 检索相似页面状态，辅助 OBSERVE_PAGE 判断页面变化",
            )
            collections["jingmai_page_signature"] = {"status": "ok", "dimension": 256}
        except Exception as exc:
            collections["jingmai_page_signature"] = {"status": "error", "message": str(exc)}

        return collections

    def insert_experience(
        self,
        experience_id: str,
        vector: list[float],
        text: str,
    ) -> None:
        """向经验库插入一条记录。"""
        self._ensure_connected()
        try:
            from pymilvus import Collection

            collection = Collection(self.settings.collection, using="jingmai_v2")
            collection.insert([ [experience_id], [vector], [text] ])
        except Exception as exc:
            raise RuntimeError(f"插入经验记录失败: {exc}") from exc

    def insert_field_evidence(
        self,
        evidence_id: str,
        vector: list[float],
        text: str,
    ) -> None:
        """向字段证据库插入一条记录。"""
        self._ensure_connected()
        try:
            from pymilvus import Collection

            collection = Collection("jingmai_field_evidence", using="jingmai_v2")
            collection.insert([ [evidence_id], [vector], [text] ])
        except Exception as exc:
            raise RuntimeError(f"插入字段证据失败: {exc}") from exc

    def insert_page_signature(
        self,
        signature_id: str,
        vector: list[float],
        text: str,
    ) -> None:
        """向页面签名库插入一条记录。"""
        self._ensure_connected()
        try:
            from pymilvus import Collection

            collection = Collection("jingmai_page_signature", using="jingmai_v2")
            collection.insert([ [signature_id], [vector], [text] ])
        except Exception as exc:
            raise RuntimeError(f"插入页面签名失败: {exc}") from exc
