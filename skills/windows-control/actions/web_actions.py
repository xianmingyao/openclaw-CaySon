#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web 浏览器自动化 Actions

提供网页爬取、导航、元素交互、截图等能力。
使用 Playwright 实现完整浏览器自动化（替代 UFO 的 requests+BS4 方案）。

依赖: playwright (pip install playwright && playwright install chromium)
"""
import asyncio
import base64
from typing import Any, Dict, List, Optional
from io import BytesIO

from loguru import logger

from app.service.actions.ufo_base_action import UFOBaseAction
from app.service.skills.base_action import (
    ActionResult,
    ActionParameter,
    ParameterType,
)


# ==================== Playwright 浏览器管理器 ====================

class PlaywrightBrowserManager:
    """Playwright 浏览器单例管理器（懒加载）"""

    _instance: Optional["PlaywrightBrowserManager"] = None
    _browser = None
    _page = None
    _playwright = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def is_available(self) -> bool:
        try:
            import playwright
            return True
        except ImportError:
            return False

    async def get_page(self):
        """获取或创建浏览器页面"""
        if self._page is not None:
            return self._page

        try:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)
            self._page = await self._browser.new_page()
            logger.info("[PlaywrightBrowser] 浏览器已启动 (headless)")
            return self._page
        except ImportError:
            raise RuntimeError(
                "playwright 未安装。请运行: pip install playwright && playwright install chromium"
            )
        except Exception as e:
            raise RuntimeError(f"启动 Playwright 失败: {e}")

    async def close(self):
        """关闭浏览器"""
        try:
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception:
            pass
        finally:
            self._browser = None
            self._page = None
            self._playwright = None

    @classmethod
    def reset(cls):
        """重置单例（用于测试）"""
        if cls._instance:
            cls._instance._browser = None
            cls._instance._page = None
            cls._instance._playwright = None
        cls._instance = None


def _get_manager() -> PlaywrightBrowserManager:
    return PlaywrightBrowserManager()


# ==================== Action 类 ====================

class WebCrawlerAction(UFOBaseAction):
    """网页爬虫，提取页面内容"""
    name = "web_crawler"
    description = "爬取指定 URL 的网页内容，提取文本和链接"
    parameters = [
        ActionParameter(name="url", type=ParameterType.STRING, description="要爬取的 URL"),
    ]

    async def _execute(self, url: str) -> ActionResult:
        try:
            # 优先使用 playwright，回退到 requests+BS4
            mgr = _get_manager()
            if mgr.is_available:
                page = await mgr.get_page()
                response = await page.goto(url, timeout=15000)
                content = await page.content()
                text = await page.inner_text("body")
                title = await page.title()
                links = []
                for a in await page.query_selector_all("a[href]"):
                    href = await a.get_attribute("href")
                    link_text = (await a.inner_text()).strip()
                    if href:
                        links.append({"text": link_text[:80], "href": href})
                return ActionResult(success=True, data={
                    "title": title,
                    "content": text[:5000] if text else "",
                    "links_count": len(links),
                    "links": links[:50],
                })
            else:
                import requests
                from bs4 import BeautifulSoup
                resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                text = soup.get_text(separator="\n", strip=True)
                links = [{"text": a.get_text(strip=True)[:80], "href": a.get("href", "")}
                         for a in soup.find_all("a", href=True)]
                return ActionResult(success=True, data={
                    "title": soup.title.string if soup.title else "",
                    "content": text[:5000],
                    "links_count": len(links),
                    "links": links[:50],
                })
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class NavigateToUrlAction(UFOBaseAction):
    """导航到指定 URL"""
    name = "navigate_to_url"
    description = "在浏览器中导航到指定 URL"
    parameters = [
        ActionParameter(name="url", type=ParameterType.STRING, description="目标 URL"),
        ActionParameter(name="wait_until", type=ParameterType.STRING,
                         description="等待条件 (load/domcontentloaded/networkidle)", required=False, default="load"),
    ]

    async def _execute(self, url: str, wait_until: str = "load") -> ActionResult:
        try:
            page = await _get_manager().get_page()
            response = await page.goto(url, wait_until=wait_until, timeout=30000)
            title = await page.title()
            return ActionResult(success=True, data={
                "url": page.url,
                "title": title,
                "status": response.status if response else None,
            })
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class ClickElementAction(UFOBaseAction):
    """点击页面元素"""
    name = "click_element"
    description = "点击页面上匹配 CSS 选择器的元素"
    parameters = [
        ActionParameter(name="selector", type=ParameterType.STRING, description="CSS 选择器"),
    ]

    async def _execute(self, selector: str) -> ActionResult:
        try:
            page = await _get_manager().get_page()
            element = await page.query_selector(selector)
            if not element:
                return ActionResult(success=False, error=f"未找到元素: {selector}")
            await element.click()
            await asyncio.sleep(0.5)
            return ActionResult(success=True, data={"selector": selector})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class TypeTextAction(UFOBaseAction):
    """在页面元素中输入文本"""
    name = "type_text"
    description = "在页面上匹配选择器的输入框中输入文本"
    parameters = [
        ActionParameter(name="selector", type=ParameterType.STRING, description="CSS 选择器"),
        ActionParameter(name="text", type=ParameterType.STRING, description="要输入的文本"),
        ActionParameter(name="clear", type=ParameterType.BOOLEAN,
                         description="是否先清空输入框", required=False, default=True),
    ]

    async def _execute(self, selector: str, text: str, clear: bool = True) -> ActionResult:
        try:
            page = await _get_manager().get_page()
            element = await page.query_selector(selector)
            if not element:
                return ActionResult(success=False, error=f"未找到元素: {selector}")
            if clear:
                await element.fill("")
            await element.fill(text)
            return ActionResult(success=True, data={"selector": selector, "text_length": len(text)})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class GetPageContentAction(UFOBaseAction):
    """获取当前页面的全部内容"""
    name = "get_page_content"
    description = "获取当前浏览器页面的全部文本内容"
    parameters = [
        ActionParameter(name="selector", type=ParameterType.STRING,
                         description="CSS 选择器（可选，默认获取 body）", required=False, default="body"),
    ]

    async def _execute(self, selector: str = "body") -> ActionResult:
        try:
            page = await _get_manager().get_page()
            content = await page.inner_text(selector)
            return ActionResult(success=True, data={
                "content": content[:10000],
                "length": len(content),
            })
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class GetPageTitleAction(UFOBaseAction):
    """获取当前页面的标题"""
    name = "get_page_title"
    description = "获取当前浏览器页面的标题"
    parameters = []

    async def _execute(self) -> ActionResult:
        try:
            page = await _get_manager().get_page()
            title = await page.title()
            return ActionResult(success=True, data={"title": title})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class ScrollPageAction(UFOBaseAction):
    """滚动页面"""
    name = "scroll_page"
    description = "在页面中向下或向上滚动"
    parameters = [
        ActionParameter(name="direction", type=ParameterType.STRING,
                         description="滚动方向 (up/down)", required=False, default="down"),
        ActionParameter(name="amount", type=ParameterType.INTEGER,
                         description="滚动像素量", required=False, default=500),
    ]

    async def _execute(self, direction: str = "down", amount: int = 500) -> ActionResult:
        try:
            page = await _get_manager().get_page()
            scroll_amount = amount if direction == "down" else -amount
            await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await asyncio.sleep(0.3)
            return ActionResult(success=True, data={"direction": direction, "amount": amount})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class WaitForElementAction(UFOBaseAction):
    """等待页面元素出现"""
    name = "wait_for_element"
    description = "等待页面上匹配选择器的元素出现"
    parameters = [
        ActionParameter(name="selector", type=ParameterType.STRING, description="CSS 选择器"),
        ActionParameter(name="timeout", type=ParameterType.FLOAT,
                         description="超时时间（秒）", required=False, default=10.0),
    ]

    async def _execute(self, selector: str, timeout: float = 10.0) -> ActionResult:
        try:
            page = await _get_manager().get_page()
            await page.wait_for_selector(selector, timeout=timeout * 1000)
            return ActionResult(success=True, data={"selector": selector, "found": True})
        except Exception as e:
            return ActionResult(success=False, error=f"等待元素超时: {selector}, {e}")


class TakeScreenshotAction(UFOBaseAction):
    """对网页截图"""
    name = "take_screenshot"
    description = "对当前浏览器页面截图"
    parameters = [
        ActionParameter(name="full_page", type=ParameterType.BOOLEAN,
                         description="是否截取完整页面", required=False, default=False),
        ActionParameter(name="selector", type=ParameterType.STRING,
                         description="CSS 选择器（截取特定元素）", required=False, default=""),
    ]

    async def _execute(self, full_page: bool = False, selector: str = "") -> ActionResult:
        try:
            page = await _get_manager().get_page()
            if selector:
                element = await page.query_selector(selector)
                if not element:
                    return ActionResult(success=False, error=f"未找到元素: {selector}")
                screenshot_bytes = await element.screenshot()
            else:
                screenshot_bytes = await page.screenshot(full_page=full_page)
            img_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
            return ActionResult(success=True, data={"screenshot_base64": img_b64})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class ExecuteJavascriptAction(UFOBaseAction):
    """在页面中执行 JavaScript"""
    name = "execute_javascript"
    description = "在当前浏览器页面中执行 JavaScript 代码并返回结果"
    parameters = [
        ActionParameter(name="script", type=ParameterType.STRING, description="JavaScript 代码"),
    ]

    async def _execute(self, script: str) -> ActionResult:
        try:
            page = await _get_manager().get_page()
            result = await page.evaluate(script)
            return ActionResult(success=True, data={"result": result})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class GetElementTextAction(UFOBaseAction):
    """获取页面元素的文本内容"""
    name = "get_element_text"
    description = "获取页面上匹配选择器的元素的文本内容"
    parameters = [
        ActionParameter(name="selector", type=ParameterType.STRING, description="CSS 选择器"),
    ]

    async def _execute(self, selector: str) -> ActionResult:
        try:
            page = await _get_manager().get_page()
            element = await page.query_selector(selector)
            if not element:
                return ActionResult(success=False, error=f"未找到元素: {selector}")
            text = await element.inner_text()
            return ActionResult(success=True, data={"text": text, "selector": selector})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class GetElementAttributeAction(UFOBaseAction):
    """获取页面元素的属性值"""
    name = "get_element_attribute"
    description = "获取页面上匹配选择器的元素的指定属性值"
    parameters = [
        ActionParameter(name="selector", type=ParameterType.STRING, description="CSS 选择器"),
        ActionParameter(name="attribute", type=ParameterType.STRING, description="属性名 (如 href, src, class 等)"),
    ]

    async def _execute(self, selector: str, attribute: str) -> ActionResult:
        try:
            page = await _get_manager().get_page()
            element = await page.query_selector(selector)
            if not element:
                return ActionResult(success=False, error=f"未找到元素: {selector}")
            value = await element.get_attribute(attribute)
            return ActionResult(success=True, data={"attribute": attribute, "value": value})
        except Exception as e:
            return ActionResult(success=False, error=str(e))
