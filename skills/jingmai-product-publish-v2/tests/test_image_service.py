from pathlib import Path

from PIL import Image

from jingmai_publish.services.image_service import ProductImageService


class DummyImageRecord:
    def __init__(
        self,
        image_id: int,
        image_local_path: str,
        image_sha256: str = "abc",
        image_format: str = "png",
        image_width: int = 500,
        image_height: int = 500,
        is_converted: int = 0,
    ):
        self.id = image_id
        self.image_local_path = image_local_path
        self.image_sha256 = image_sha256
        self.image_format = image_format
        self.image_width = image_width
        self.image_height = image_height
        self.is_converted = is_converted


class DummyImageRepo:
    def __init__(self, source_record=None, hash_record=None):
        self.source_record = source_record
        self.hash_record = hash_record
        self.created_records = []

    def find_by_source_url(self, image_source_url: str, image_role: str | None = None):
        return self.source_record

    def find_by_sha256(self, image_sha256: str, image_role: str | None = None):
        return self.hash_record

    def create_image_record(self, **kwargs):
        record = type("ImageRecord", (), {"id": len(self.created_records) + 1, **kwargs})
        self.created_records.append(record)
        return record


def test_should_download_when_no_existing_record(tmp_path: Path):
    service = ProductImageService(DummyImageRepo(), image_root=tmp_path)
    assert service.should_download("https://example.com/a.png", "main") is True


def test_should_not_download_when_file_exists(tmp_path: Path):
    image_path = tmp_path / "a.png"
    image_path.write_bytes(b"demo")
    service = ProductImageService(DummyImageRepo(source_record=DummyImageRecord(1, str(image_path))), image_root=tmp_path)
    assert service.should_download("https://example.com/a.png", "main") is False


def test_process_image_reuses_existing_source_record(tmp_path: Path):
    image_path = tmp_path / "reused.png"
    image = Image.new("RGB", (500, 500), color="white")
    image.save(image_path, format="PNG")

    record = DummyImageRecord(1, str(image_path), image_sha256="sha-demo")
    service = ProductImageService(DummyImageRepo(source_record=record), image_root=tmp_path)

    result = service.process_image(1, "main", "https://example.com/a.png")
    assert result.reused is True
    assert result.local_path == str(image_path)


def test_process_image_converts_transparent_role_to_png(tmp_path: Path):
    source_path = tmp_path / "source.jpg"
    image = Image.new("RGB", (600, 600), color="white")
    image.save(source_path, format="JPEG")

    repo = DummyImageRepo()
    service = ProductImageService(repo, image_root=tmp_path)
    service.download_to_cache = lambda image_source_url: source_path

    result = service.process_image(1, "transparent", "https://example.com/a.jpg")
    assert result.converted is True
    assert result.image_format == "png"
    assert repo.created_records[0].is_valid is True
