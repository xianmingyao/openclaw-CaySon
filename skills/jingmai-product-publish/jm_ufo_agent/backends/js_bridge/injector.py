"""JS Bridge 注入器 — Web 页面 JavaScript 注入与执行。

在 Web 页面（如京麦内嵌浏览器）中注入和执行 JavaScript，
用于 DOM 操作、数据读取和事件触发。
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class JSBridgeInjector:
    """JavaScript 注入器 — 在 Web 页面中执行 JS 脚本。

    # 通过 COM 自动化控制 WebBrowser 控件执行 JS。
    # 支持 DOM 查询、表单填充、事件触发等操作。
    # 在非 Windows 或无 COM 环境下降级为空操作。
    # 返回 JS 执行结果，JSON 序列化传递复杂数据。
    """

    def __init__(self, web_control: Any | None = None):
        """初始化 JS 注入器。"""
        self._web_control = web_control

    def is_available(self) -> bool:
        """检查 JS 注入能力是否可用。"""
        return self._web_control is not None

    def execute_script(self, script: str) -> Any:
        """执行 JavaScript 脚本并返回结果。

        # script 是要执行的 JavaScript 代码字符串。
        # 返回 JS 表达式的求值结果。
        # 复杂返回值通过 JSON 序列化传递。
        """
        if self._web_control is None:
            logger.debug("JSBridgeInjector: 无 web_control")
            return None

        try:
            # 尝试通过 COM Document 执行
            return self._execute_via_com(script)
        except Exception as exc:
            logger.warning("JS 注入执行异常: %s", exc)
            return None

    def query_selector(self, selector: str) -> dict[str, Any] | None:
        """通过 CSS 选择器查询 DOM 元素。"""
        script = f"""
        (function() {{
            var el = document.querySelector('{selector}');
            if (!el) return null;
            return {{
                tagName: el.tagName,
                id: el.id,
                className: el.className,
                textContent: el.textContent ? el.textContent.substring(0, 200) : '',
                value: el.value || '',
                rect: el.getBoundingClientRect() ? {{
                    left: el.getBoundingClientRect().left,
                    top: el.getBoundingClientRect().top,
                    right: el.getBoundingClientRect().right,
                    bottom: el.getBoundingClientRect().bottom
                }} : null
            }};
        }})()
        """
        result = self.execute_script(script)
        if isinstance(result, str):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return None
        return result

    def fill_input(self, selector: str, value: str) -> bool:
        """通过 JS 向输入框填充值。

        # 使用 value setter + input 事件触发，兼容 React/Vue 等框架。
        """
        script = f"""
        (function() {{
            var el = document.querySelector('{selector}');
            if (!el) return false;
            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value'
            ).set;
            nativeInputValueSetter.call(el, '{value}');
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return true;
        }})()
        """
        result = self.execute_script(script)
        return bool(result)

    def click_element(self, selector: str) -> bool:
        """通过 JS 点击元素。"""
        script = f"""
        (function() {{
            var el = document.querySelector('{selector}');
            if (!el) return false;
            el.click();
            return true;
        }})()
        """
        result = self.execute_script(script)
        return bool(result)

    def get_page_text(self) -> str:
        """获取页面可见文本。"""
        script = """
        (function() {
            return document.body ? document.body.innerText : '';
        })()
        """
        result = self.execute_script(script)
        return str(result) if result else ""

    def _execute_via_com(self, script: str) -> Any:
        """通过 COM Document 执行 JavaScript。"""
        try:
            doc = self._web_control.Document
            if doc is None:
                return None

            # 包装脚本以返回 JSON
            wrapped = f"""
            (function() {{
                try {{
                    var result = {script};
                    return typeof result === 'object' ? JSON.stringify(result) : result;
                }} catch(e) {{
                    return JSON.stringify({{error: e.message}});
                }}
            }})()
            """
            result = doc.parentWindow.eval(wrapped)
            return result
        except AttributeError:
            # 尝试替代方式
            try:
                doc = self._web_control.element_info.element.CurrentName
                return None
            except Exception:
                return None
        except Exception as exc:
            logger.debug("COM JS 执行异常: %s", exc)
            return None
