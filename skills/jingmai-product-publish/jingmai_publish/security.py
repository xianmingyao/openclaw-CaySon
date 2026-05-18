"""网络输入安全校验。"""

from __future__ import annotations

from ipaddress import ip_address
from urllib.parse import urlparse


class UnsafeUrlError(ValueError):
    """URL 不满足外部抓取安全约束。"""


def validate_http_url(
        url: str,
        *,
        allowed_hosts: tuple[str, ...],
        purpose: str,
) -> str:
    """校验外部 HTTP URL，阻止 SSRF 常见入口。

    当前策略以域名白名单为主，并显式拒绝本地、内网、链路本地和
    带凭据 URL。京东商品页和京东图片资源都应落在固定域名集合内。
    """

    parsed = urlparse((url or "").strip())
    if parsed.scheme not in {"http", "https"}:
        raise UnsafeUrlError(f"{purpose} URL 只允许 http/https: {url}")
    if not parsed.hostname:
        raise UnsafeUrlError(f"{purpose} URL 缺少主机名: {url}")
    if parsed.username or parsed.password:
        raise UnsafeUrlError(f"{purpose} URL 不允许携带用户名或密码: {url}")

    host = parsed.hostname.lower().rstrip(".")
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost"):
        raise UnsafeUrlError(f"{purpose} URL 不允许访问本地主机: {host}")

    try:
        ip = ip_address(host)
    except ValueError:
        if not _host_allowed(host, allowed_hosts):
            allowed = ", ".join(allowed_hosts)
            raise UnsafeUrlError(f"{purpose} URL 域名不在白名单内: {host}; allowed={allowed}")
    else:
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise UnsafeUrlError(f"{purpose} URL 不允许访问非公网 IP: {host}")
        if not _host_allowed(host, allowed_hosts):
            allowed = ", ".join(allowed_hosts)
            raise UnsafeUrlError(f"{purpose} URL IP 不在白名单内: {host}; allowed={allowed}")

    return url.strip()


def _host_allowed(host: str, allowed_hosts: tuple[str, ...]) -> bool:
    for allowed in allowed_hosts:
        normalized = allowed.lower().lstrip(".").rstrip(".")
        if host == normalized or host.endswith(f".{normalized}"):
            return True
    return False
