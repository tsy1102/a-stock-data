# sc_network.py 代码审查报告

## 概述
`stock_common/sc_network.py` 负责网络请求的底层实现，包括同步的 `_request_with_retry`、`_quick_request` 以及异步包装函数 `_async_request_with_retry`、`_async_quick_request`。它是所有数据源模块（如 `sc_datasource.py`）的基础。

## 关键问题

### 类型检查 (mypy)
- **返回 `Any`**：多个函数未明确返回类型，导致 `Any` 向上传播。尤其是 `asyncio.to_thread` 包装的函数签名不匹配，期待返回 `dict[str, Any]` 或 `list[dict[str, Any]]`，但实际返回 `Any`。
- **函数参数缺失注解**：如 `def _request_with_retry(url: str, params: dict | None = None, ..., timeout: int = 30) -> requests.Response | None:` 未显式声明返回 `Optional[requests.Response]`，易导致后续 `None` 使用错误。
- **`sort` 参数类型**：在使用 `list.sort(key=...)` 时，`key` 的类型被检测为 `Callable[[dict[str, object]], object]`，但期望 `SupportsDunderLT/GT`，建议使用 `key=lambda x: x.get('field')` 并确保返回可比较类型。

### 性能与设计
- **同步请求阻塞**：`_request_with_retry` 采用同步 `requests`，在高并发场景（如批量报告生成）会导致线程池饱和。
- **异常捕获过宽**：捕获所有 `Exception` 并返回 `None`，会隐藏网络错误并导致后续 `NoneType` 错误。建议细分 `requests.exceptions.RequestException` 并记录错误细节。
- **重复超时逻辑**：超时和重试逻辑遍布多个函数，可抽象为通用装饰器以降低代码重复度。

## 改进建议
1. **完善类型注解**：为所有公共函数添加完整的 `typing` 注解（返回 `Optional[requests.Response]`、`Dict[str, Any]` 等），避免使用 `Any`。
2. **原生异步实现**：在该模块实现基于 `aiohttp` 的 `async_fetch`，让上层调用直接使用异步 IO，删除大量 `asyncio.to_thread` 包装。
3. **细化异常处理**：捕获 `requests.exceptions.*`，在日志中记录状态码、URL、异常信息，必要时抛出自定义异常供上层处理。
4. **统一重试装饰器**：实现 `@retry` 装饰器，统一重试次数、延迟、超时设置，提高可维护性。
5. **代码风格**：当前 `flake8` 对该文件无明显错误，保持现有代码格式即可。

---

如需针对具体函数提供示例类型注解或重构实现，请告诉我！
