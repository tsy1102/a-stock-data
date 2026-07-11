# seat_db.py 代码审查报告

## 概览
`seat_db.py` 负责龙虎榜席位识别与分析，提供了席位等级辨识、详细信息获取、风格标签、溢价标签以及综合质量评分等功能。文件结构清晰，使用了模块级缓存 `_seat_db_cache`，并通过 `_load_seat_db` 进行懒加载。整体代码逻辑可读，但在类型注解、异常处理、性能与可维护性方面仍有提升空间。

## 代码质量问题
1. **类型注解缺失或不完整**
   - `identify_seat_tier`、`get_seat_info`、`enhance_lhb_seats` 等函数缺少返回类型注解，导致 `mypy` 报错。建议为所有公共函数补全 `typing` 注解，如 `Tuple[str, str]`、`Dict[str, Any]`、`Dict[str, Any]`。
   - `_load_seat_db` 返回 `Dict[str, Any]`，但内部使用了 `json.load`，若 JSON 结构不符会产生 `KeyError`，应使用 `TypedDict` 描述结构以提升检查精度。

2. **异常捕获过宽**
   - `_load_seat_db` 使用 `except Exception:` 捕获所有异常并返回空结构，隐藏了文件读取、JSON 解码错误。建议捕获 `FileNotFoundError`、`json.JSONDecodeError` 并记录日志后返回空结构。
   - `enhance_lhb_seats`、`identify_seat_tier` 等函数未对外部数据做校验，若 `seats.json` 中缺失字段会导致 `KeyError`。可在访问前使用 `.get` 并提供默认值。

3. **硬编码数据 & 可维护性**
   - `keywords_map` 在函数内部硬编码，若需要扩展或本地化需要修改代码。建议抽取至单独的 JSON/YAML 配置文件或模块常量，便于维护。
   - `seat_quality_score` 计算逻辑使用了硬编码的加分规则（如 `legend` 每次加 10 分），缺少配置化。可考虑将权重抽到配置文件，支持灵活调节。

4. **性能优化**
   - `identify_seat_tier` 对每个席位遍历 `tiers`、`aliases`、`keywords_map` 进行多轮匹配，时间复杂度为 O(N*M)。若席位库规模扩大（数千条），性能会下降。可构建倒排索引或预编译正则，提高匹配速度。
   - `enhance_lhb_seats` 对买卖两侧分别遍历并进行 `get_seat_info` 调用，若 `lhb_data` 中席位数量很大，会产生大量重复查询。可以一次性批量获取信息，或在 `identify_seat_tier` 中加入缓存。

5. **日志与可观测性**
   - 代码中仅在 `_load_seat_db` 失败时使用 `_debug_log`，其余关键路径缺少日志（如 `enhance_lhb_seats` 的评分计算、异常标记）。建议在关键分支加入统一 `logging`，方便排障。

6. **文档不足**
   - 函数 docstring 只描述了输入输出，缺少对业务意义、返回值结构的详细说明。例如 `get_seat_info` 返回的 `premium`、`winning_rate` 含义未解释。
   - `seat_quality_score` 计算公式未在文档中说明，导致后续维护者难以理解加分依据。

## 重构建议与评估
| 改动 | 难度 | 风险 | 预期收益 |
|------|------|------|----------|
| 为所有函数补全类型注解（使用 `TypedDict` 描述 JSON 结构） | 低 | 低 | `mypy` 错误消除，提升 IDE 提示与代码可读性 |
| 将 `keywords_map`、加分权重抽到外部配置文件（JSON/YAML） | 中 | 低 | 配置化后业务规则可快速迭代，无需改代码 |
| 精细化异常捕获并记录日志 | 低 | 低 | 更快定位文件读取或解析错误，提升稳定性 |
| 构建席位名称倒排索引（预处理一次）或使用正则编译 | 中 | 中 | 大幅降低 `identify_seat_tier` 的匹配时间，适用于席位库扩展 |
| 在 `enhance_lhb_seats` 中批量缓存 `identify_seat_tier` 结果 | 低 | 低 | 减少重复计算，提升批量处理性能 |
| 引入统一 `logging`（INFO/DEBUG）并在关键路径记录 | 低 | 低 | 运行时可观测性提升，便于追踪异常和评分变化 |
| 完善 docstring，使用 Google 风格或 NumPy 风格说明每个字段 | 低 | 低 | 文档质量提升，新成员上手更快 |

## 具体实现示例（示例代码片段）
```python
# 使用 TypedDict 定义席位数据库结构
from typing import TypedDict, List, Dict, Any

class SeatDetails(TypedDict, total=False):
    style: str
    traits: List[str]
    premium: str
    winning_rate: str
    tier: str

class SeatDB(TypedDict):
    tiers: Dict[str, List[str]]
    seat_details: Dict[str, SeatDetails]
    seat_aliases: Dict[str, List[str]]

def _load_seat_db() -> SeatDB:
    """加载席位数据库（返回 TypedDict），出现异常时记录日志并返回空结构"""
    global _seat_db_cache
    if _seat_db_cache is not None:
        return _seat_db_cache
    try:
        with open(_SEAT_DB_PATH, "r", encoding="utf-8") as f:
            _seat_db_cache = json.load(f)  # type: ignore[assignment]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        _debug_log(f"load seat db error: {e}")
        _seat_db_cache = {"tiers": {}, "seat_details": {}, "seat_aliases": {}}
    return _seat_db_cache
```

## 结论
`seat_db.py` 已具备核心功能，但在类型安全、异常处理、性能、日志以及文档方面仍有显著提升空间。上述改进大多属于低到中等难度，风险可控，能够提升代码可维护性、运行时鲁棒性以及后续功能扩展的灵活性，建议在下一个迭代周期内逐步落实。
