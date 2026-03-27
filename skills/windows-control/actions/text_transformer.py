#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文本转换器 - TextTransformer

将文本中的特殊字符转换为 pywinauto 兼容的格式

来源: UFO/ufo/automator/ui_control/controller.py:TextTransformer
"""

import re


class TextTransformer:
    """
    文本转换器 - 处理特殊字符的转换

    确保文本正确输入到 Windows 应用中
    """

    # pywinauto 特殊键格式参考:
    # {ENTER} - 回车
    # {TAB} - Tab
    # {+} - 加号 (本身是特殊字符)
    # {^} - Caret
    # {%} - Percent
    # {ASC nnnn} - ASCII 字符
    # {VK} - 虚拟键码

    @staticmethod
    def transform_text(text: str, transform_tag: str = "all") -> str:
        """
        转换文本中的特殊字符

        Args:
            text: 要转换的文本
            transform_tag: 转换标记，支持:
                - "all": 全部转换
                - "+": 加号转换
                - "^": Caret 转换
                - "%": Percent 转换
                - "\n": 换行符转换
                - "\t": 制表符转换
                - "(", ")": 括号转换
                - "{VK_CONTROL}": Ctrl 键
                - "{VK_SHIFT}": Shift 键
                - "{VK_MENU}": Alt 键

        Returns:
            str: 转换后的文本
        """
        if transform_tag == "all":
            # 全部转换，按优先级排序
            transform_tag = "+\n\t^%{VK_CONTROL}{VK_SHIFT}{VK_MENU}()"

        if "\n" in transform_tag:
            text = TextTransformer.transform_enter(text)
        if "\t" in transform_tag:
            text = TextTransformer.transform_tab(text)
        if "+" in transform_tag:
            text = TextTransformer.transform_plus(text)
        if "^" in transform_tag:
            text = TextTransformer.transform_caret(text)
        if "%" in transform_tag:
            text = TextTransformer.transform_percent(text)
        if "{VK_CONTROL}" in transform_tag:
            text = TextTransformer.transform_control(text)
        if "{VK_SHIFT}" in transform_tag:
            text = TextTransformer.transform_shift(text)
        if "{VK_MENU}" in transform_tag:
            text = TextTransformer.transform_alt(text)
        if "(" in transform_tag or ")" in transform_tag:
            text = TextTransformer.transform_brace(text)

        return text

    @staticmethod
    def transform_enter(text: str) -> str:
        """将 \\n 转换为 {ENTER}"""
        return text.replace("\\n", "{ENTER}").replace("\n", "{ENTER}")

    @staticmethod
    def transform_tab(text: str) -> str:
        """将 \\t 转换为 {TAB}"""
        return text.replace("\\t", "{TAB}").replace("\t", "{TAB}")

    @staticmethod
    def transform_plus(text: str) -> str:
        """将 + 转换为 {+} (pywinauto 中 + 是修饰键)"""
        return text.replace("+", "{+}")

    @staticmethod
    def transform_caret(text: str) -> str:
        """将 ^ 转换为 {^} (pywinauto 中 ^ 是 Alt 修饰符)"""
        return text.replace("^", "{^}")

    @staticmethod
    def transform_percent(text: str) -> str:
        """将 % 转换为 {%} (pywinauto 中 % 是 Alt 修饰符)"""
        return text.replace("%", "{%}")

    @staticmethod
    def transform_brace(text: str) -> str:
        """将 () 转换为 {(} {)} (pywinauto 中大括号是特殊语法)"""
        text = text.replace("{", "{{}")
        text = text.replace("}", "}}")
        return text

    @staticmethod
    def transform_control(text: str) -> str:
        """将 {VK_CONTROL} 或 Ctrl 转换为 ^"""
        text = re.sub(r"\{VK_CONTROL\}", "^", text, flags=re.IGNORECASE)
        text = re.sub(r"\bCtrl\b", "^", text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def transform_shift(text: str) -> str:
        """将 {VK_SHIFT} 或 Shift 转换为 +"""
        text = re.sub(r"\{VK_SHIFT\}", "+", text, flags=re.IGNORECASE)
        text = re.sub(r"\bShift\b", "+", text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def transform_alt(text: str) -> str:
        """将 {VK_MENU} 或 Alt 转换为 %"""
        text = re.sub(r"\{VK_MENU\}", "%", text, flags=re.IGNORECASE)
        text = re.sub(r"\bAlt\b", "%", text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def transform_to_pyautogui(text: str) -> str:
        """
        将 pywinauto 格式转换为 pyautogui 兼容格式

        例如:
        - {ENTER} -> 'enter'
        - {TAB} -> 'tab'
        - {+} -> '+'
        - ^ -> 'ctrl' (不直接支持，需要用 hotkey)
        """
        # 简单的转换规则
        result = text
        result = result.replace("{ENTER}", "enter")
        result = result.replace("{TAB}", "tab")
        result = result.replace("{BACKSPACE}", "backspace")
        result = result.replace("{DELETE}", "delete")
        result = result.replace("{HOME}", "home")
        result = result.replace("{END}", "end")
        result = result.replace("{PGUP}", "pageup")
        result = result.replace("{PGDN}", "pagedown")
        result = result.replace("{UP}", "up")
        result = result.replace("{DOWN}", "down")
        result = result.replace("{LEFT}", "left")
        result = result.replace("{RIGHT}", "right")
        result = result.replace("{ESC}", "escape")
        result = result.replace("{F1}", "f1")
        result = result.replace("{F2}", "f2")
        result = result.replace("{F3}", "f3")
        result = result.replace("{F4}", "f4")
        result = result.replace("{F5}", "f5")
        result = result.replace("{F6}", "f6")
        result = result.replace("{F7}", "f7")
        result = result.replace("{F8}", "f8")
        result = result.replace("{F9}", "f9")
        result = result.replace("{F10}", "f10")
        result = result.replace("{F11}", "f11")
        result = result.replace("{F12}", "f12")
        result = result.replace("{+}", "+")
        result = result.replace("{^}", "^")
        result = result.replace("{%}", "%")
        result = result.replace("{{}", "{")
        result = result.replace("}}", "}")
        return result


__all__ = ["TextTransformer"]
