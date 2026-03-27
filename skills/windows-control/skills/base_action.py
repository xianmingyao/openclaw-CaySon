#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基础动作定义
定义技能系统中所有动作的抽象基类
"""
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, Field
from enum import Enum
from loguru import logger
import inspect
import json


class ParameterType(str, Enum):
    """参数类型枚举"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    FILE = "file"


class ActionParameter(BaseModel):
    """动作参数定义"""
    name: str = Field(description="参数名称")
    type: ParameterType = Field(description="参数类型")
    description: str = Field(description="参数描述")
    required: bool = Field(default=True, description="是否必需")
    default: Any = Field(default=None, description="默认值")
    enum: Optional[List[Any]] = Field(default=None, description="枚举值")


class ActionResult(BaseModel):
    """动作执行结果"""
    success: bool = Field(description="是否成功")
    data: Optional[Dict[str, Any]] = Field(default=None, description="返回数据")
    error: Optional[str] = Field(default=None, description="错误信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class ActionExecutionError(Exception):
    """动作执行异常"""

    def __init__(self, message: str, action_name: str, parameters: Dict[str, Any] = None):
        self.message = message
        self.action_name = action_name
        self.parameters = parameters or {}
        super().__init__(f"Action '{action_name}' failed: {message}")


class BaseAction:
    """
    基础动作抽象类

    所有技能动作必须继承此类并实现 execute 方法
    """

    # 子类必须定义的类属性
    name: str = None
    description: str = None
    parameters: List[ActionParameter] = []

    def __init__(self):
        """初始化动作"""
        if self.name is None:
            raise ValueError(f"{self.__class__.__name__} must define 'name' class attribute")
        if self.description is None:
            raise ValueError(f"{self.__class__.__name__} must define 'description' class attribute")

    async def execute(self, **kwargs) -> ActionResult:
        """
        执行动作

        Args:
            **kwargs: 动作参数

        Returns:
            ActionResult: 执行结果

        Raises:
            ActionExecutionError: 执行失败时抛出
        """
        # 验证参数
        try:
            validated_params = await self.validate_parameters(kwargs)
        except ValueError as e:
            raise ActionExecutionError(str(e), self.name, kwargs)

        # 执行具体动作
        try:
            result = await self._execute(**validated_params)
            if isinstance(result, ActionResult):
                return result
            return ActionResult(success=True, data={"result": result})
        except Exception as e:
            logger.error(f"Action '{self.name}' execution failed: {str(e)}")
            raise ActionExecutionError(str(e), self.name, validated_params)

    async def _execute(self, **kwargs) -> Any:
        """
        实际执行动作的方法

        子类必须实现此方法

        Args:
            **kwargs: 验证后的参数

        Returns:
            Any: 执行结果
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement _execute method")

    async def validate_parameters(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        验证参数

        Args:
            params: 输入参数

        Returns:
            Dict[str, Any]: 验证后的参数

        Raises:
            ValueError: 参数验证失败
        """
        validated = {}

        # 检查必需参数
        param_dict = {p.name: p for p in self.parameters}

        for param in self.parameters:
            value = params.get(param.name)

            # 检查必需参数
            if param.required and value is None:
                if param.default is not None:
                    value = param.default
                else:
                    raise ValueError(
                        f"Required parameter '{param.name}' is missing"
                    )

            # 如果值仍为 None 且非必需，使用默认值
            if value is None:
                if param.default is not None:
                    value = param.default
                else:
                    continue

            # 类型验证
            try:
                validated[param.name] = self._validate_type(
                    value,
                    param.type,
                    param.enum
                )
            except ValueError as e:
                raise ValueError(
                    f"Parameter '{param.name}' type validation failed: {str(e)}"
                )

        # 检查未知参数 (排除以下划线开头的内部注入参数，如 _hover_injected)
        unknown_params = {k for k in params.keys() if not k.startswith('_')} - set(param_dict.keys())
        if unknown_params:
            logger.warning(
                f"Unknown parameters for action '{self.name}': {unknown_params}"
            )

        return validated

    def _validate_type(
        self,
        value: Any,
        param_type: ParameterType,
        enum_values: Optional[List[Any]] = None
    ) -> Any:
        """
        验证参数类型

        Args:
            value: 参数值
            param_type: 期望类型
            enum_values: 枚举值（可选）

        Returns:
            Any: 转换后的值

        Raises:
            ValueError: 类型不匹配
        """
        try:
            if param_type == ParameterType.STRING:
                return str(value)
            elif param_type == ParameterType.INTEGER:
                return int(value)
            elif param_type == ParameterType.FLOAT:
                return float(value)
            elif param_type == ParameterType.BOOLEAN:
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                return bool(value)
            elif param_type == ParameterType.ARRAY:
                if isinstance(value, str):
                    return json.loads(value)
                return list(value)
            elif param_type == ParameterType.OBJECT:
                if isinstance(value, str):
                    return json.loads(value)
                return dict(value)
            elif param_type == ParameterType.FILE:
                # 文件类型，返回路径字符串
                return str(value)
            else:
                return value
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            raise ValueError(f"Cannot convert {value!r} to {param_type.value}")

        # 枚举值验证
        if enum_values is not None:
            if value not in enum_values:
                raise ValueError(
                    f"Value {value!r} not in allowed values: {enum_values}"
                )

    def get_schema(self) -> Dict[str, Any]:
        """
        获取动作的 JSON Schema

        Returns:
            Dict[str, Any]: JSON Schema
        """
        properties = {}
        required = []

        for param in self.parameters:
            prop_schema = {
                "type": param.type.value,
                "description": param.description
            }

            if param.enum:
                prop_schema["enum"] = param.enum

            if param.default is not None:
                prop_schema["default"] = param.default

            properties[param.name] = prop_schema

            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

    @classmethod
    def from_function(cls, func: callable, name: str = None) -> Type['BaseAction']:
        """
        从函数创建动作类

        Args:
            func: 函数对象
            name: 动作名称（默认使用函数名）

        Returns:
            Type[BaseAction]: 动作类
        """
        action_name = name or func.__name__

        # 从函数签名提取参数
        sig = inspect.signature(func)
        parameters = []

        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue

            param_type = ParameterType.STRING
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = ParameterType.INTEGER
                elif param.annotation == float:
                    param_type = ParameterType.FLOAT
                elif param.annotation == bool:
                    param_type = ParameterType.BOOLEAN
                elif param.annotation == list:
                    param_type = ParameterType.ARRAY
                elif param.annotation == dict:
                    param_type = ParameterType.OBJECT

            action_param = ActionParameter(
                name=param_name,
                type=param_type,
                description=f"Parameter {param_name}",
                required=param.default == inspect.Parameter.empty
            )
            parameters.append(action_param)

        # 创建动态类
        class DynamicAction(cls):
            name = action_name
            description = func.__doc__ or f"Action {action_name}"
            parameters = parameters

            async def _execute(self, **kwargs):
                return await func(**kwargs)

        DynamicAction.__name__ = f"{action_name.capitalize()}Action"
        return DynamicAction


__all__ = [
    'ParameterType',
    'ActionParameter',
    'ActionResult',
    'ActionExecutionError',
    'BaseAction',
]
