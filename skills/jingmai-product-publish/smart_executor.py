"""
SmartExecutor - 带截图验证的Executor
每个action执行前/后截图，用LLM视觉分析验证是否真正生效
失败重试3次，成功才执行下一步
"""
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image


class SmartExecutor:
    """带视觉验证的智能执行器"""
    
    def __init__(self, locator=None, llm=None, settings=None, logger=None):
        self.locator = locator
        self.llm = llm
        self.settings = settings
        self.logger = logger
        
        # 如果没有locator，尝试初始化
        if self.locator is None:
            try:
                from infrastructure.locator import JingmaiLocator
                self.locator = JingmaiLocator()
                self.locator.find_window()
            except Exception as e:
                print(f"[WARNING] 初始化locator失败: {e}")
        
        if self.settings is None:
            try:
                from settings import get_settings
                self.settings = get_settings()
            except Exception:
                pass
    
    def _log(self, level: str, msg: str):
        safe_msg = str(msg)
        if self.logger:
            try:
                getattr(self.logger, level)(safe_msg)
            except (AttributeError, UnicodeEncodeError):
                try:
                    self.logger.info(safe_msg)
                except Exception:
                    pass
        try:
            print(f"[{level.upper()}] {safe_msg}".encode('utf-8', errors='replace').decode('utf-8'))
        except Exception:
            print(f"[{level.upper()}] (log message)")
    
    def take_screenshot(self, save_path: str = None) -> Optional[str]:
        """截图当前窗口"""
        if not self.locator:
            self._log("warning", "无locator，无法截图")
            return None
        try:
            if not save_path:
                screenshot_dir = getattr(self.settings, 'SCREENSHOT_DIR', 'resources/screenshots')
                Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
                save_path = f"{screenshot_dir}/verify_{int(time.time()*1000)}.png"
            result = self.locator.take_screenshot(save_path)
            return save_path if result else None
        except Exception as e:
            self._log("error", f"截图失败: {e}")
            return None
    
    def get_image_hash(self, img_path: str) -> str:
        """计算图片hash，用于判断两张图是否相同"""
        try:
            with Image.open(img_path) as img:
                img_small = img.resize((200, 200), Image.Resampling.LANCZOS)
                import tempfile
                tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                img_small.convert('RGB').save(tmp.name, 'JPEG', quality=50)
                with open(tmp.name, 'rb') as f:
                    return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            self._log("warning", f"图片hash计算失败: {e}")
            return ""
    
    def compare_screenshots(self, before: str, after: str) -> Dict[str, Any]:
        """比较两张截图，判断是否有变化"""
        try:
            hash_before = self.get_image_hash(before) if Path(before).exists() else ""
            hash_after = self.get_image_hash(after) if Path(after).exists() else ""
            
            if not hash_before or not hash_after:
                return {"changed": False, "reason": "截图不存在"}
            
            changed = hash_before != hash_after
            return {
                "changed": changed,
                "before_hash": hash_before[:8],
                "after_hash": hash_after[:8],
                "reason": "UI有变化" if changed else "UI无变化"
            }
        except Exception as e:
            return {"changed": False, "reason": f"比较失败: {e}"}
    
    def vision_verify_action(self, action_name: str, screenshot: str, 
                            expected_effect: str = "") -> Dict[str, Any]:
        """用LLM视觉分析验证action是否生效"""
        if not self.llm or not screenshot or not Path(screenshot).exists():
            return {"verified": False, "reason": "LLM或截图不可用"}
        
        try:
            prompt = f"""分析这张京麦客户端截图，验证Action "{action_name}" 是否成功执行。

预期效果: {expected_effect or '表单字段值变化/按钮点击效果/页面跳转'}

请分析：
1. 截图中的关键元素是否有预期变化？
2. 操作是否真的生效了？
3. 是否有错误提示？

返回JSON格式：
{{"verified": true/false, "reason": "原因", "details": "详细分析"}}
"""
            response = self.llm.invoke_multimodal(prompt, screenshot)
            if not response:
                return {"verified": False, "reason": "LLM无响应"}
            
            import json, re
            try:
                return json.loads(response.strip())
            except json.JSONDecodeError:
                match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group())
                    except:
                        pass
                return {"verified": False, "reason": f"LLM响应解析失败"}
        except Exception as e:
            return {"verified": False, "reason": f"视觉验证异常: {e}"}
    
    def execute_with_verification(self, action_name: str, params: Dict[str, Any],
                                 expected_effect: str = "",
                                 max_retries: int = 3) -> Dict[str, Any]:
        """执行action并验证结果"""
        from actions import ActionRegistry
        
        for attempt in range(1, max_retries + 1):
            self._log("info", f"\n{'='*50}")
            self._log("info", f"执行Action: {action_name} (尝试 {attempt}/{max_retries})")
            self._log("info", f"{'='*50}")
            
            # 1. 执行前截图
            before_path = self.take_screenshot()
            if before_path:
                self._log("info", f"执行前截图: {before_path}")
            
            # 2. 执行action
            try:
                exec_params = dict(params)
                if "locator" not in exec_params:
                    exec_params["locator"] = self.locator
                    
                result = ActionRegistry.execute(action_name, **exec_params)
                self._log("info", f"执行结果: success={result.get('success')}")
            except Exception as e:
                self._log("error", f"执行异常: {e}")
                result = {"success": False, "error": str(e)}
            
            # 3. 等待UI更新
            time.sleep(1.5)
            
            # 4. 执行后截图
            after_path = self.take_screenshot()
            if after_path:
                self._log("info", f"执行后截图: {after_path}")
            
            # 5. 截图比较
            if before_path and after_path:
                compare_result = self.compare_screenshots(before_path, after_path)
                self._log("info", f"截图比较: {compare_result}")
                
                if not compare_result.get("changed"):
                    self._log("warning", "UI无变化，Action可能未生效")
                    result["needs_retry"] = True
                    result["verify_reason"] = compare_result.get("reason", "UI无变化")
                    continue
            
            # 6. LLM视觉验证
            if after_path and self.llm:
                vision_result = self.vision_verify_action(action_name, after_path, expected_effect)
                self._log("info", f"视觉验证: {vision_result}")
                
                if not vision_result.get("verified", False):
                    self._log("warning", f"视觉验证失败: {vision_result.get('reason', 'unknown')}")
                    result["needs_retry"] = True
                    result["verify_reason"] = vision_result.get("reason", "验证失败")
                    continue
            
            if not result.get("needs_retry"):
                result["verified"] = True
                result["screenshot"] = after_path
                self._log("info", "[OK] Action验证通过")
                return result
        
        self._log("error", f"[FAIL] Action执行失败，已重试{max_retries}次")
        result["verified"] = False
        result["failed_after_retries"] = True
        return result
    
    def run_plan(self, plan: List[Dict[str, Any]], task_id: str = "") -> Dict[str, Any]:
        """执行计划，每步都验证"""
        self._log("info", f"开始执行计划，共{len(plan)}步")
        
        results = []
        for i, step in enumerate(plan):
            action_name = step.get("action", "")
            params = step.get("params", {})
            expected_effect = step.get("expected_effect", "")
            
            self._log("info", f"\n步骤 {i+1}/{len(plan)}: {action_name}")
            
            result = self.execute_with_verification(
                action_name, 
                params, 
                expected_effect,
                max_retries=3
            )
            
            results.append(result)
            
            if not result.get("verified") and not result.get("success"):
                self._log("error", f"步骤{i+1}失败，停止执行")
                return {
                    "success": False,
                    "failed_step": i+1,
                    "action": action_name,
                    "results": results,
                    "error": result.get("verify_reason") or result.get("error", "验证失败")
                }
        
        self._log("info", f"[OK] 计划执行完成，{len(plan)}步全部成功")
        return {"success": True, "results": results}


def create_smart_executor(locator=None, llm=None, settings=None, logger=None) -> SmartExecutor:
    """工厂函数：创建SmartExecutor"""
    return SmartExecutor(locator=locator, llm=llm, settings=settings, logger=logger)
