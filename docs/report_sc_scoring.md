# sc_scoring.py 代码审查报告

## 概览
`sc_scoring.py` 实现了多维度评分系统，提供了 `ScoreData`、`ScoreResult` 数据结构以及一套针对技术面、基本面、估值面、资金面、筹码面、分红面的评分函数。文件结构层次分明，使用 `dataclass` 简化模型定义，支持多派别（价值、成长、游资、综合）的加权评分与报告生成。

## 代码质量问题
1. **类型注解缺失或不完整**
   - 大多数内部评分函数 (`_score_technical`、`_score_fundamental` 等) 的返回值标注为 `tuple`，未具体指明内部元素类型。建议使用 `Tuple[float, List[str]]` 提高可读性。
   - `calculate_score_by_school` 的 `precomputed_dimensions` 参数类型标注为 `Optional[Dict[str, Tuple[float, List[str]]]]`，但在函数体内未对空值进行显式检查，可能导致 `KeyError`。
   - `calculate_multi_school_scores` 返回的字典结构未使用 TypedDict，建议定义返回类型以配合 `mypy` 检查。

2. **硬编码权重比例**
   - 在 `calculate_score`（`ful` 路径）中，权重从配置中读取后除以 100，但没有容错处理，若配置缺失会导致除零或错误的默认值。建议提供默认权重并校验总和为 100%。

3. **异常处理缺失**
   - 代码几乎没有 `try/except` 包裹关键计算，若传入异常数据（如 `None` 或 `NaN`）会导致 `TypeError`。在数据转换前加入安全检查或使用 `_safe_float` 类似的工具函数可以提升稳健性。

4. **重复逻辑**
   - 多个评分函数在处理 `cfg` 时重复 `cfg or {}`，可以抽取为统一的 `cfg = cfg or {}` 写在函数顶部，减少重复代码。

5. **日志缺失**
   - 除了报告生成外，整个模块缺乏日志记录。建议在关键路径（如 `calculate_score`、`calculate_multi_school_scores`）加入 `logging`，以便排查异常分数来源。

6. **文档不完整**
   - 虽然函数都有简要的 docstring，但缺少对参数意义、返回值结构的详细说明，尤其是 `calculate_score_by_school` 与 `calculate_multi_school_scores` 的复杂返回结构。

7. **性能可优化点**
   - `calculate_multi_school_scores` 每次调用都会重新计算所有维度评分，即使在 `calculate_score_by_school` 中使用了 `precomputed_dimensions`，但在 `precomputed_dimensions` 的生成过程中仍调用六个 `_score_*` 函数。若在外层缓存这些结果（如全局 LRU 缓存），可以在多次评估同一只股票时减少重复计算。

## 重构建议与评估
| 改动 | 难度 | 风险 | 预期收益 |
|------|------|------|----------|
| 完整补全类型注解（包括返回的 `Tuple[float, List[str]]`、返回字典的 `TypedDict`） | 低 | 低 | `mypy` 错误显著下降，提高代码可读性 |
| 将硬编码权重抽取到配置并添加校验（总和 100%） | 中 | 低 | 防止配置错误导致评分失真 |
| 在关键计算前加入安全校验（`None`/`NaN` 检查） | 低 | 低 | 增强运行时稳健性，避免异常中断 |
| 引入统一日志框架（`logging`），记录评分入口、异常、关键权重） | 中 | 低 | 便于后期调试和运营监控 |
| 将维度评分结果缓存（例如使用 `functools.lru_cache`） | 中 | 中 | 对批量评估大量股票时提升 20%+ 性能 |
| 完善 docstring，使用 Sphinx 或 `google` 风格文档 | 低 | 低 | 改善团队协作，上手更快 |

## 具体实现示例（示例代码片段）
```python
# 为内部评分函数补全返回类型
from typing import Tuple, List, Dict, Optional

def _score_technical(data: ScoreData, cfg: Optional[Dict] = None) -> Tuple[float, List[str]]:
    """技术面评分，返回 (score, details)"""
    cfg = cfg or {}
    # ... 省略实现
    return max(0, min(100, score)), details

# 为多派别评分返回值定义 TypedDict（可放在模块顶部）
from typing import TypedDict, Any

class MultiSchoolResult(TypedDict):
    value: ScoreResult
    growth: ScoreResult
    speculator: ScoreResult
    consensus: ScoreResult
    consensus_score: float
    dispersion: float
    dominant_school: str
    school_labels: Dict[str, Dict[str, Any]]
```

## 结论
`sc_scoring.py` 已具备完整的评分逻辑，但在类型安全、异常防护、日志可观测性以及配置健壮性方面仍有提升空间。上述改进难度大多在低到中等之间，风险可控，能够显著提升代码质量、可维护性以及运行时可靠性，建议在下一个迭代周期内逐步落实。
