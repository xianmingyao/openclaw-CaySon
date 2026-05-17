"""图片处理服务。"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen
import mimetypes
import shutil

from PIL import Image

from jingmai_publish.repositories.product_image import ProductImageRepository
from jingmai_publish.repositories.runtime_log import RuntimeLogRepository
from jingmai_publish.security import validate_http_url


@dataclass(slots=True)
class ImageProcessResult:
    """图片处理结果。"""

    image_id: int
    local_path: str
    image_sha256: str
    image_format: str
    width: int
    height: int
    reused: bool
    converted: bool


class ProductImageService:
    """负责图片下载、查重、格式转换与记录落库。"""

    MAIN_ALLOWED_FORMATS = {"jpg", "jpeg", "png"}
    TRANSPARENT_ALLOWED_FORMATS = {"png"}
    ALLOWED_IMAGE_HOSTS = ("360buyimg.com",)

    def __init__(
        self,
        image_repo: ProductImageRepository,
        runtime_log_repo: RuntimeLogRepository | None = None,
        image_root: str | Path = "logs/images",
    ) -> None:
        """注入图片仓库、日志仓库和图片根目录。"""

        self.image_repo = image_repo
        self.runtime_log_repo = runtime_log_repo
        self.image_root = Path(image_root)
        self.source_cache_dir = self.image_root / "source-cache"
        self.converted_dir = self.image_root / "converted"
        self.source_cache_dir.mkdir(parents=True, exist_ok=True)
        self.converted_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def calculate_file_sha256(file_path: str | Path) -> str:
        """计算本地文件 SHA256。"""

        digest = sha256()
        with Path(file_path).open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def infer_extension_from_url(image_source_url: str) -> str:
        """从图片链接推断扩展名。"""

        parsed = urlparse(image_source_url)
        suffix = Path(parsed.path).suffix.lower().lstrip(".")
        if suffix:
            return suffix
        guessed, _ = mimetypes.guess_type(image_source_url)
        if guessed:
            return guessed.split("/")[-1]
        return "bin"

    @staticmethod
    def inspect_image(file_path: str | Path) -> tuple[str, int, int]:
        """读取图片格式与尺寸。"""

        with Image.open(file_path) as image:
            image_format = (image.format or "UNKNOWN").lower()
            width, height = image.size
        return image_format, width, height

    def should_download(self, image_source_url: str, image_role: str) -> bool:
        """判断图片是否需要重新下载。"""

        existing = self.image_repo.find_by_source_url(image_source_url, image_role=image_role)
        if existing is None:
            return True
        return not Path(existing.image_local_path).exists()

    def download_to_cache(self, image_source_url: str) -> Path:
        """下载远程图片到本地缓存目录。"""

        image_source_url = validate_http_url(
            image_source_url,
            allowed_hosts=self.ALLOWED_IMAGE_HOSTS,
            purpose="商品图片下载",
        )
        extension = self.infer_extension_from_url(image_source_url)
        target_path = self.source_cache_dir / f"tmp-{sha256(image_source_url.encode('utf-8')).hexdigest()[:20]}.{extension}"

        with urlopen(image_source_url) as response, target_path.open("wb") as handle:
            shutil.copyfileobj(response, handle)
        return target_path

    def ensure_valid_format(self, source_path: Path, image_role: str, image_sha256: str) -> tuple[Path, str, bool]:
        """确保图片格式满足业务要求，必要时做格式转换。"""

        image_format, width, height = self.inspect_image(source_path)
        allowed_formats = self.TRANSPARENT_ALLOWED_FORMATS if image_role == "transparent" else self.MAIN_ALLOWED_FORMATS

        if image_format in allowed_formats:
            return source_path, image_format, False

        target_path = self.converted_dir / f"{image_sha256}.png"
        with Image.open(source_path) as image:
            if image.mode not in {"RGBA", "RGB"}:
                image = image.convert("RGBA" if image_role == "transparent" else "RGB")
            image.save(target_path, format="PNG")
        return target_path, "png", True

    def validate_business_rule(self, image_role: str, image_format: str, width: int, height: int) -> bool:
        """根据角色校验图片业务规则。"""

        if width < 480 or height < 480:
            return False
        if width != height:
            return False
        if image_role == "transparent":
            return image_format in self.TRANSPARENT_ALLOWED_FORMATS
        return image_format in self.MAIN_ALLOWED_FORMATS

    def process_image(
        self,
        job_item_id: int,
        image_role: str,
        image_source_url: str,
    ) -> ImageProcessResult:
        """处理单张图片，完成下载/查重/转换/落库。"""

        existing = self.image_repo.find_by_source_url(image_source_url, image_role=image_role)
        if existing is not None and Path(existing.image_local_path).exists():
            return ImageProcessResult(
                image_id=existing.id,
                local_path=existing.image_local_path,
                image_sha256=existing.image_sha256,
                image_format=existing.image_format or "unknown",
                width=existing.image_width or 0,
                height=existing.image_height or 0,
                reused=True,
                converted=bool(existing.is_converted),
            )

        source_path = self.download_to_cache(image_source_url)
        original_sha256 = self.calculate_file_sha256(source_path)

        reused_by_hash = self.image_repo.find_by_sha256(original_sha256, image_role=image_role)
        if reused_by_hash is not None and Path(reused_by_hash.image_local_path).exists():
            return ImageProcessResult(
                image_id=reused_by_hash.id,
                local_path=reused_by_hash.image_local_path,
                image_sha256=reused_by_hash.image_sha256,
                image_format=reused_by_hash.image_format or "unknown",
                width=reused_by_hash.image_width or 0,
                height=reused_by_hash.image_height or 0,
                reused=True,
                converted=bool(reused_by_hash.is_converted),
            )

        normalized_path, image_format, converted = self.ensure_valid_format(source_path, image_role, original_sha256)
        final_sha256 = self.calculate_file_sha256(normalized_path)
        image_format, width, height = self.inspect_image(normalized_path)
        is_valid = self.validate_business_rule(image_role, image_format, width, height)
        file_size_bytes = normalized_path.stat().st_size

        record = self.image_repo.create_image_record(
            job_item_id=job_item_id,
            image_role=image_role,
            image_source_url=image_source_url,
            image_local_path=str(normalized_path),
            image_sha256=final_sha256,
            image_format=image_format,
            image_width=width,
            image_height=height,
            file_size_bytes=file_size_bytes,
            is_valid=is_valid,
            is_converted=converted,
            converted_from_format=None if not converted else source_path.suffix.lower().lstrip("."),
            download_status="converted" if converted else "downloaded",
        )

        if self.runtime_log_repo is not None:
            self.runtime_log_repo.append_log(
                session_id=f"image-{job_item_id}",
                job_item_id=job_item_id,
                log_type="process",
                message=f"已处理图片: role={image_role}, url={image_source_url}",
                detail_path=str(normalized_path),
            )

        return ImageProcessResult(
            image_id=record.id,
            local_path=str(normalized_path),
            image_sha256=final_sha256,
            image_format=image_format,
            width=width,
            height=height,
            reused=False,
            converted=converted,
        )
