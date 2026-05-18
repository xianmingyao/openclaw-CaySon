"""图片本地化 Repository。"""

from __future__ import annotations

from jingmai_publish.models import ProductImage
from sqlalchemy.orm import Session


class ProductImageRepository:
    """图片查重与落库仓库。"""

    def __init__(self, session: Session) -> None:
        """注入数据库会话。"""

        self.session = session

    def find_by_source_url(
            self,
            image_source_url: str,
            image_role: str | None = None,
    ) -> ProductImage | None:
        """按图片来源链接查找可复用记录。"""

        query = self.session.query(ProductImage).filter(ProductImage.image_source_url == image_source_url)
        if image_role is not None:
            query = query.filter(ProductImage.image_role == image_role)
        return query.one_or_none()

    def find_by_sha256(self, image_sha256: str, image_role: str | None = None) -> ProductImage | None:
        """按文件哈希查找图片。"""

        query = self.session.query(ProductImage).filter(ProductImage.image_sha256 == image_sha256)
        if image_role is not None:
            query = query.filter(ProductImage.image_role == image_role)
        return query.one_or_none()

    def create_image_record(self, **kwargs) -> ProductImage:
        """创建图片本地化记录。"""

        record = ProductImage(**kwargs)
        self.session.add(record)
        self.session.flush()
        return record

    def update_image_record(self, image_id: int, **kwargs) -> ProductImage:
        """更新图片记录并返回更新后的对象。"""

        record = self.session.query(ProductImage).filter(ProductImage.id == image_id).one()
        for key, value in kwargs.items():
            if hasattr(record, key) and value is not None:
                setattr(record, key, value)
        self.session.flush()
        return record

    def list_images_by_job_item(self, job_item_id: int, image_role: str | None = None) -> list[ProductImage]:
        """列出某个商品行下的图片记录。"""

        query = self.session.query(ProductImage).filter(ProductImage.job_item_id == job_item_id)
        if image_role is not None:
            query = query.filter(ProductImage.image_role == image_role)
        return query.all()
