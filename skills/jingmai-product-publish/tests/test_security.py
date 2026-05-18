import pytest

from jingmai_publish.security import UnsafeUrlError, validate_http_url


def test_validate_http_url_accepts_allowed_subdomain():
    url = validate_http_url(
        "https://img14.360buyimg.com/n1/demo.jpg",
        allowed_hosts=("360buyimg.com",),
        purpose="test",
    )
    assert url.endswith("demo.jpg")


def test_validate_http_url_rejects_private_ip():
    with pytest.raises(UnsafeUrlError, match="非公网 IP"):
        validate_http_url(
            "http://127.0.0.1/latest",
            allowed_hosts=("360buyimg.com",),
            purpose="test",
        )


def test_validate_http_url_rejects_unlisted_host():
    with pytest.raises(UnsafeUrlError, match="白名单"):
        validate_http_url(
            "https://example.com/a.png",
            allowed_hosts=("360buyimg.com",),
            purpose="test",
        )
