# -*- coding: utf-8 -*-
"""tests/reports/test_reports_strategy.py — val 报告 26 策略注册表防线

针对 docs/roadmap.md 注记 B 记录的**报告层测试空白**，补上 val 策略侧的守护。

为什么值得测（历史上真实存在的退化风险）：
  1. **策略函数与调度表脱节**——新增 `strategy_26_xxx` 却漏登记到 `_strategy_defs`，
     代码不报错、报告静默少一节；反之调度表里写了不存在函数名则要等运行时才炸。
     `_strategy_defs` 是 `execute_pipeline` 的**局部变量**，无法直接 import，
     故用源码解析做结构校验。
  2. **空池崩溃**——休市日/预筛后股票池为空时，25 个策略必须优雅返回空列表，
     不能把整份 val 报告带崩（历史上 `[:top_n]` 传错类型就抛过
     `TypeError: slice indices must be integers`）。
  3. **配置键名笔误**——策略用 `_sc.get("strategy", {}).get("KEY", 默认值)` 读配置，
     键名写错时**静默走默认值**，回测口径被悄悄改掉却无人察觉。

设计约束：**纯离线**——所有策略在空池输入下不触网；`_load_strategy_config()` 读本地 YAML。
"""
from __future__ import annotations

import asyncio
import inspect
import re
import unittest

import get_val_report as V

# 形如 ("策略01【龙回头】", strategy_01_longhuitou, (...))
_RE_DISPLAY = re.compile(r"策略(\d{2})【")
_RE_FNREF = re.compile(r"\bstrategy_(\d{2})_")


def _strategy_functions():
    """收集模块内所有 strategy_NN_* 可调用对象，按编号排序。"""
    out = []
    for name, obj in vars(V).items():
        m = re.fullmatch(r"strategy_(\d{2})_[A-Za-z0-9_]+", name)
        if m and callable(obj):
            out.append((int(m.group(1)), name, obj))
    return sorted(out)


def _dispatch_source():
    """定位 _strategy_defs 调度表代码块。

    `_strategy_defs` 是 `run_discovery_async` 的**局部变量**（不是
    `ValReportRunner.execute_pipeline` 里的），无法直接 import，只能解析源码。
    这里按变量名动态截取，避免把测试钉死在某个函数名上。
    """
    src = inspect.getsource(V)
    m = re.search(r"_strategy_defs\s*=\s*\[.*?\n    \]", src, re.S)
    if not m:
        raise AssertionError(
            "未在 get_val_report.py 中找到 _strategy_defs 调度表——"
            "变量若已改名，请同步更新本测试的定位正则")
    return m.group(0)


def _call_empty_pool(fn):
    """用空股票池调用策略：首个参数传 []，其余用默认值（缺失默认值则补 []）。"""
    params = list(inspect.signature(fn).parameters.values())
    args = []
    for i, p in enumerate(params):
        if i == 0:
            args.append([])
        elif p.default is inspect.Parameter.empty:
            args.append([])
        else:
            break
    if inspect.iscoroutinefunction(fn):
        return asyncio.run(fn(*args))
    return fn(*args)


class TestStrategyRegistry(unittest.TestCase):
    """策略函数清单与编号完整性。"""

    def test_exactly_25_strategies(self):
        fns = _strategy_functions()
        self.assertEqual(len(fns), 26, f"策略数量应为 26，实际 {len(fns)}")

    def test_numbering_is_contiguous_01_to_25(self):
        nums = [n for n, _name, _f in _strategy_functions()]
        self.assertEqual(nums, list(range(1, 27)))

    def test_all_are_callable_and_have_docstring_or_name(self):
        for num, name, fn in _strategy_functions():
            self.assertTrue(callable(fn), f"{name} 不可调用")
            self.assertTrue(name.startswith(f"strategy_{num:02d}_"))


class TestDispatchTable(unittest.TestCase):
    """调度表 _strategy_defs 与策略函数的双向一致性。"""

    def test_dispatch_has_25_entries(self):
        src = _dispatch_source()
        found = _RE_DISPLAY.findall(src)
        self.assertEqual(len(found), 26, f"调度表条目应为 26，实际 {len(found)}")
        self.assertEqual(sorted(int(x) for x in found), list(range(1, 27)))

    def test_every_strategy_function_is_registered(self):
        """定义了却漏登记 → 报告静默少一节，必须拦住。"""
        src = _dispatch_source()
        registered = {int(x) for x in _RE_FNREF.findall(src)}
        defined = {n for n, _name, _f in _strategy_functions()}
        missing = sorted(defined - registered)
        self.assertEqual(missing, [], f"已定义但未登记到调度表: {missing}")

    def test_every_dispatch_entry_has_a_function(self):
        """登记了却不存在的函数 → 运行时才炸，必须拦住。"""
        src = _dispatch_source()
        registered = {int(x) for x in _RE_FNREF.findall(src)}
        defined = {n for n, _name, _f in _strategy_functions()}
        orphan = sorted(registered - defined)
        self.assertEqual(orphan, [], f"调度表引用了不存在的策略: {orphan}")

    def test_display_names_are_unique(self):
        src = _dispatch_source()
        names = re.findall(r'策略\d{2}【[^】]+】', src)
        self.assertEqual(len(names), 26)
        self.assertEqual(len(set(names)), 26, f"策略展示名重复: {names}")

    def test_display_number_matches_function_number(self):
        """展示名编号必须与函数名编号一致（防止复制粘贴串行）。"""
        src = _dispatch_source()
        pairs = re.findall(r'策略(\d{2})【[^】]+】",\s*strategy_(\d{2})_', src)
        self.assertEqual(len(pairs), 26, "展示名与函数名应能一一配对")
        for disp, fn in pairs:
            self.assertEqual(disp, fn, f"编号错位: 展示 策略{disp} ↔ 函数 strategy_{fn}_")


class TestEmptyPoolSafety(unittest.TestCase):
    """空股票池不得崩溃——休市日/预筛后为空的真实场景。"""

    def test_all_strategies_survive_empty_pool(self):
        failures = []
        for num, name, fn in _strategy_functions():
            try:
                result = _call_empty_pool(fn)
            except Exception as e:  # noqa: BLE001
                failures.append(f"{name}: {type(e).__name__}: {e}")
                continue
            # 约定：策略返回 list（空池 → 空 list）
            # 例外：策略17【龙虎榜】数据来自本地龙虎榜缓存，与入参无关，可能非空
            if not isinstance(result, list):
                failures.append(f"{name}: 返回 {type(result).__name__}，期望 list")
        self.assertEqual(failures, [], "空池崩溃/返回类型异常:\n  " + "\n  ".join(failures))

    def test_empty_pool_results_are_lists_of_dicts(self):
        """非空的返回项必须是 dict（策略17 走本地缓存可能非空）。"""
        for num, name, fn in _strategy_functions():
            result = _call_empty_pool(fn)
            for item in result:
                self.assertIsInstance(item, dict, f"{name} 返回项不是 dict: {item!r}")


class TestStrategyConfigKeys(unittest.TestCase):
    """策略读取的配置键必须真实存在——防止键名笔误静默走默认值。"""

    def test_config_loads_with_strategy_section(self):
        cfg = V._load_strategy_config()
        self.assertIsInstance(cfg, dict)
        self.assertIn("strategy", cfg)
        self.assertTrue(cfg["strategy"], "strategy 配置段不应为空")

    def test_referenced_strategy_keys_exist(self):
        """扫描 val 源码里 `_sc.get("strategy", {}).get("KEY", ...)` 引用的键名。"""
        src = inspect.getsource(V)
        refs = set(re.findall(
            r'_sc\.get\(\s*["\']strategy["\']\s*,\s*\{\s*\}\s*\)\.get\(\s*["\']([A-Za-z0-9_]+)["\']',
            src))
        self.assertTrue(refs, "未扫描到任何 strategy 配置键引用，正则可能已失效")
        cfg = V._load_strategy_config().get("strategy", {})
        missing = sorted(refs - set(cfg))
        self.assertEqual(
            missing, [],
            f"策略引用了配置中不存在的键（会静默走默认值）: {missing}\n"
            f"  现有键: {sorted(cfg)}")


if __name__ == "__main__":
    unittest.main()
