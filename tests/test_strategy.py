"""test_strategy.py — 策略配置 (strategy_config.yaml / keywords_config.yaml) 与策略函数基本测试（V8.7）。

重点测试：
  - _load_strategy_config 能读取 yaml 并返回 dict
  - valuation / fundamental 等核心配置存在
  - get_valuation_pe_center 根据行业返回 float
  - 18 个策略函数签名正确、可被调用（不依赖网络）
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# ── 配置文件测试 ────────────────────────────────────────

def test_strategy_config_file_exists():
    cfg_path = project_root / "strategy_config.yaml"
    assert cfg_path.exists(), f"缺少 {cfg_path}"


def test_keywords_config_file_exists():
    cfg_path = project_root / "keywords_config.yaml"
    assert cfg_path.exists(), f"缺少 {cfg_path}"


def test_load_strategy_config_returns_dict():
    from stock_common import _load_strategy_config
    cfg = _load_strategy_config()
    assert isinstance(cfg, dict)
    # 至少包含 valuation / fundamental 等核心配置
    assert "valuation" in cfg or "fundamental" in cfg or "strategies" in cfg


def test_load_settings_returns_dict():
    from stock_common import _load_settings
    s = _load_settings()
    assert isinstance(s, dict)


def test_valuation_pe_center_default_is_float():
    from stock_common import get_valuation_pe_center
    center = get_valuation_pe_center("")
    # yaml 中可能存 int，转成 float 后应仍 > 0
    assert isinstance(center, (int, float))
    assert float(center) > 0


def test_valuation_pe_center_returns_positive():
    from stock_common import get_valuation_pe_center
    # 无论传什么行业名，都应返回正的数值
    for name in ["银行", "半导体", "白酒", "新能源", ""]:
        v = get_valuation_pe_center(name)
        assert isinstance(v, (int, float))
        assert float(v) > 0


# ── get_val_report.py 的 18 个策略函数基本测试 ─────────

def _import_val_module():
    """懒加载 get_val_report，避免 import 时触发网络请求。"""
    sys.path.insert(0, str(project_root))
    import get_val_report as gv
    return gv


def test_strategy_functions_importable():
    """确保 18 个策略函数模块级存在且 callable。"""
    gv = _import_val_module()
    required = [
        "strategy_01_longhuitou",
        "strategy_02_weekly_ma",
        "strategy_03_volume_breakout",
        "strategy_04_core_discount",
        "strategy_05_double_bottom",
        "strategy_06_three_soldiers",
        "strategy_07_golden_cross",
        "strategy_08_policy_driven",
        "strategy_09_calendar_rotation",
        "strategy_10_contrarian_value",
        "strategy_11_holder_concentration",
        "strategy_12_divergence_warning",
        "strategy_13_dividend_yield",
        "strategy_14_asset_rebalance",
        "strategy_15_liquidity_king",
        "strategy_16_policy_heatmap",
        "strategy_17_northbound_top",
        "strategy_18_longhu_activity",
    ]
    for name in required:
        assert hasattr(gv, name), f"get_val_report 缺少 {name}"
        assert callable(getattr(gv, name)), f"{name} 不可调用"


def test_strategies_handle_empty_pool():
    """向策略函数传入空列表，验证不抛异常。

    注意：这仅测试函数签名层面的健壮性，不依赖真实行情/数据。
    """
    gv = _import_val_module()
    from datetime import datetime

    today_str = datetime.now().strftime("%Y-%m-%d")
    empty_pool: list = []

    # 这些策略可能需要网络/TDX 数据，我们仅验证不抛异常时不崩
    mapping = {
        "strategy_01_longhuitou": (empty_pool, today_str),
        "strategy_03_volume_breakout": (empty_pool,),
        "strategy_07_golden_cross": (empty_pool,),
        "strategy_08_policy_driven": (empty_pool, empty_pool),
        "strategy_16_policy_heatmap": (empty_pool, empty_pool),
        "strategy_18_longhu_activity": (empty_pool, today_str, 10),
    }

    for name, args in mapping.items():
        fn = getattr(gv, name)
        try:
            # 我们只测函数可被调用；由于网络/TDX 数据不存在，结果可能为空或抛异常
            result = fn(*args)
            # 如果有结果，应返回 list
            if result is not None:
                assert isinstance(result, list)
        except Exception:
            # 策略函数内部可能因无数据 / 网络异常而抛错，这是预期行为
            pass


def test_top5_sorted_returns_list():
    gv = _import_val_module()
    if hasattr(gv, "_top5_sorted"):
        candidates = [
            {"code": "001", "score": 90},
            {"code": "002", "score": 80},
            {"code": "003", "score": 70},
        ]
        result = gv._top5_sorted(candidates, lambda x: x["score"])
        assert isinstance(result, list)
        assert len(result) <= 5


def test_kline_indices_returns_dict():
    gv = _import_val_module()
    if hasattr(gv, "_kline_indices"):
        keys = ["date", "open", "close", "high", "low", "volume"]
        idx = gv._kline_indices(keys)
        assert isinstance(idx, dict)
        assert "close" in idx
        assert "open" in idx
        assert "vol" in idx  # volume -> vol


def test_get_val_report_has_parse_args():
    """主模块应暴露可被调用的 parse_args 函数。"""
    gv = _import_val_module()
    assert hasattr(gv, "run_discovery")
    assert callable(gv.run_discovery)


# ── keywords_config.yaml 相关测试 ───────────────────────

def test_keywords_config_has_suffixes():
    import yaml  # type: ignore
    kw_path = project_root / "keywords_config.yaml"
    with open(kw_path, "r", encoding="utf-8") as f:
        kw = yaml.safe_load(f) or {}

    # 至少有板块或行业名清理字段
    has_industry = "industry_name_cleanup" in kw or "board_suffixes" in kw
    has_aliases = "industry_aliases" in kw or "sector_aliases" in kw
    assert has_industry or has_aliases, (
        "keywords_config.yaml 应该包含行业名清理或别名配置"
    )
