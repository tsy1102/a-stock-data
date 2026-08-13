"""sc_render.py — 报告渲染公共模块(V17.0 R5 新增)

V17.0 R5 实测结论(2026-08-13): 三脚本(sht/med/lng)渲染章节逐段对比——
- **多评委评审团评分**: 三处逐字相同(12 行×3) → 抽取为本模块 render_multi_school_scores
- 北向宏观/北向持仓/股东户数/评分明细与档位: 文案**异构**(sht 短线风格 vs med/lng 中线长线
  风格, 单位/符号/结构均不同), 参数化成本 > 去重收益, 按仓库 DRY 纪律保留各脚本本地实现
"""
from __future__ import annotations

from typing import Any, Callable, Optional


def render_multi_school_scores(emit: Callable[[str], None], score_data: Any) -> Any:
    """V17.0 R5: 多评委评审团评分渲染(原 sht/med/lng 三处逐字重复)。

    Args:
        emit: 行输出回调(各脚本的 L 闭包或 lines.append)
        score_data: 评分输入数据(calculate_multi_school_scores 入参)
    返回: multi_scores 结果 dict(调用方后续读取 consensus 等), 异常时返回 None
    """
    try:
        from stock_common.sc_scoring import calculate_multi_school_scores

        multi_scores = calculate_multi_school_scores(score_data)
        emit("")
        emit("  ★ 多评委评审团评分")
        emit(f"    价值派评分: {multi_scores['value'].total_score:.1f}分")
        emit(f"    成长派评分: {multi_scores['growth'].total_score:.1f}分")
        emit(f"    投机派评分: {multi_scores['speculator'].total_score:.1f}分")
        emit(f"    综合共识: {multi_scores['consensus'].total_score:.1f}分")
        if multi_scores['dispersion'] > 15:
            emit(f"    ⚠️ 派别分歧度较大({multi_scores['dispersion']:.1f})，投资需谨慎")
        return multi_scores
    except Exception as e:
        emit(f"    多评委评分异常: {e}")
        return None
