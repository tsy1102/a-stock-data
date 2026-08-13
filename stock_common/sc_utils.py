#!/usr/bin/env python3
"""sc_utils.py — 工具函数 / 常量 / 配置加载

从原 stock_common.py 提取的通用工具函数：
  - get_version: 从 VERSION 文件读取项目版本号
  - _safe_float: 安全浮点转换
  - ensure_output_dir / get_script_dir: 目录工具
  - get_board_type / is_limit_up / is_limit_down: 板块判断
  - clean_codes / parse_args: 命令行工具
  - _load_settings / _load_strategy_config: YAML 配置加载
  - _safe_cleanup_tdx: TDX 连接清理

依赖关系：
  - sc_network (日志/调试)
  - stock_cache (cached 装饰器，用于 get_board_type)
"""

from __future__ import annotations

import os
import sys
import math
import time
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_version() -> str:
    """从项目根目录的 VERSION 文件读取版本号（单一来源）。

    Returns:
        版本号字符串，如 "9.4"
    """
    _version_path = Path(__file__).resolve().parent.parent / "VERSION"
    try:
        return _version_path.read_text(encoding="utf-8").strip()
    except (FileNotFoundError, OSError):
        return "unknown"

# 从 sc_network 复用日志和调试工具
from stock_common.sc_network import _debug_log

# 缓存装饰器（get_board_type 用到）
from core.stock_cache import cached, TTL

# ═══════════════════════════════════════
# 导出接口
# ═══════════════════════════════════════
__all__ = [
    '_safe_float',
    'ensure_output_dir', 'get_script_dir',
    'get_board_type', 'is_limit_up', 'is_limit_down',
    'clean_codes', 'parse_args',
    '_safe_cleanup_tdx',
    '_load_settings', '_load_strategy_config',
    '_settings_cache', '_strategy_config_cache',
]

# ═══════════════════════════════════════
# 基础工具函数
# ═══════════════════════════════════════

def _safe_float(val: Any, default: float = 0.0) -> float:
    """安全转换为 float，异常或非有限值返回 default"""
    try:
        # pandas Series 单元素直接 float() 会触发 FutureWarning
        if hasattr(val, 'iloc') and hasattr(val, '__len__'):
            if len(val) == 0:
                return default
            val = val.iloc[0]
        v = float(val)
        return v if math.isfinite(v) else default
    except (TypeError, ValueError):
        return default


# ═══════════════════════════════════════
# 目录工具
# ═══════════════════════════════════════

def ensure_output_dir(output_dir: str) -> str:
    """确保输出目录存在，返回规范化的路径。"""
    _dir = os.path.abspath(output_dir)
    os.makedirs(_dir, exist_ok=True)
    return _dir


def get_script_dir() -> str:
    """获取当前脚本所在目录（供 main.py 和各报告脚本共用）。

    注意：模块化后返回项目根目录（stock_common 的上级目录），
    以保持与原 stock_common.py 行为一致。
    """
    # 原 stock_common.py 在项目根目录，__file__ 即根目录
    # 现在 sc_utils.py 在 stock_common/ 子目录，需返回上级
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ═══════════════════════════════════════
# 板块判断
# ═══════════════════════════════════════

# V16.3.3 (2026-08-10 字典 12.1/12.15.7): 股票名称临时标记（应忽略——名称主体不变）
_TEMP_NAME_PREFIXES = ("N", "C", "XD", "XR", "DR", "S")


def parse_stock_name(raw_name: str) -> tuple:
    """结构化股票名称（2026-08-10 字典名称设计）。

    返回 (name_core, is_st, is_new)：
      - name_core: 核心名称——去除临时前缀（N 上市首日/C 次日至第5日/XD 除息/XR 除权/DR 除权除息/S 未股改）
                  与 ST/*ST 标记。**名称主体永久不变**（缓存可无限 TTL）。
      - is_st: 是否 ST/*ST（退市风险信号——**不可忽略**，报告/策略依赖）
      - is_new: 是否次新股（N/C 前缀——上市 ≤5 日）

    规则（相对 get_board_type 的 `"ST" in name` 全包含判定更严谨）：
      - ST 判定：名称**开头**为 ST/*ST（避免误判名称中部含 ST 的股票，如历史遗留简称）
      - 临时前缀：优先匹配长前缀（XD/XR/DR > N/C/S），去除后即为核心名
    """
    raw = (raw_name or "").strip()
    if not raw:
        return "", False, False

    name_core = raw
    is_st = False
    is_new = False

    # 1. ST/*ST 判定（前缀）——保留核心名中其余部分
    if name_core.startswith("*ST"):
        is_st = True
        name_core = name_core[3:]
    elif name_core.startswith("ST"):
        is_st = True
        name_core = name_core[2:]

    # 2. 临时前缀去除（XD/XR/DR 先匹配——更长前缀优先）
    for pfx in ("XD", "XR", "DR"):
        if name_core.startswith(pfx):
            name_core = name_core[len(pfx):]
            break
    else:
        for pfx in ("N", "C"):
            if name_core.startswith(pfx):
                is_new = True
                name_core = name_core[len(pfx):]
                break
        else:
            if name_core.startswith("S") and len(name_core) > 1:
                name_core = name_core[1:]  # S=未股改（历史遗留，极罕见）

    return name_core.strip(), is_st, is_new


@cached(category="board_type", ttl_seconds=TTL["board_type"])
def get_board_type(code: str, name: str = "") -> str:
    """V7.5: 统一板块判断。返回: 主板 / 创业板 / 科创板 / 北交所 / ST。"""
    if name:
        _, is_st, _ = parse_stock_name(name)
        if is_st:
            return "ST"
    if code.startswith("688"):
        return "科创板"
    if code.startswith(("300", "301")):
        return "创业板"
    if code.startswith(("8", "4", "92")):  # V16.1.7: 北交所（43/83/87 老号段+920 新号段）
        return "北交所"
    return "主板"


# V17.0 S3: A 股代码前缀统一判定（收敛 get_mak/get_val 双份定义）
A_STOCK_PREFIXES = ("00", "30", "60", "68", "92")


def is_a_stock(code: str) -> bool:
    """V17.0 S3: 统一 A 股代码判定（沪深主板/创业板/科创板/北交所）。

    过滤非 A 股: ETF(15/51/56/58 等)、LOF(50)、可转债(11/12/18)、基金等
    (ZHB 全市场快照 7948 只含基金/ETF)。原 get_mak/get_val 双份本地实现收敛于此。
    """
    c = str(code or "")
    if len(c) != 6 or not c.isdigit():
        return False
    return c[:2] in A_STOCK_PREFIXES


def em_secid_prefix(code: str) -> str:
    """V17.0 S3: 东财 secid 市场前缀统一判定。

    规则: 北交所(92 新号段 + 43/83/87 老号段 + 8/4) → "0."; 沪市(6xx/5x ETF/9xx 沪B) → "1.";
    其余(深市 00/30/15/16/159/399 指数等) → "0."。
    ⚠️ 北交所 92 号段以 "9" 开头——必须先于 "9→沪" 判断, 否则拼出 "1.92xxx" 恒失败。
    """
    c = str(code)
    if c.startswith(("92", "8", "4", "43", "83", "87")):
        return "0."
    if c[0] in "569":
        return "1."
    return "0."


def name_mark(name: str) -> str:
    """V17.0 S5: ST/次新标注后缀统一（原 get_mak._name_mark / get_val 内联块收敛）。

    返回 ' ⚠️ST' / ' 🆕次新'，正常名返回空串。
    """
    try:
        _, _st, _new = parse_stock_name(name or "")
        if _st:
            return " ⚠️ST"
        if _new:
            return " 🆕次新"
    except Exception:
        pass
    return ""


def save_text_report(path: str, lines: list) -> str:
    """V17.0 S5: 报告写尾样板统一（5 报告脚本原逐字重复）。

    合并 filter(None) + open(...utf-8).write 三步, 返回最终文本(供调用方后续使用)。
    """
    output = "\n".join(filter(None, lines))
    with open(path, "w", encoding="utf-8") as _f:
        _f.write(output)
    return output


def limit_pct_for(code: str, name: str = "") -> float:
    """V16.2: 统一涨跌停理论阈值（%）。规则: 主板/ST 10 / 创业板·科创板 20 / 北交所 30。
    供脚本连板/偏离/涨停判断复用（替代各处硬编码 9.5/19.5/10/20）。"""
    board = get_board_type(code, name)
    if board == "北交所":
        return 30.0
    if board in ("创业板", "科创板"):
        return 20.0
    return 10.0


def is_limit_up(code: str, name: str, change_pct: float, is_st: Optional[bool] = None) -> bool:
    """V7.5: 统一涨停判断。区分板块阈值。
    V10.0: ST 涨跌幅已放宽至 10%（与主板一致）。
    V16.1.8: 北交所 30%（老 8/4 号段 + 新 92 号段）；创业板·科创板 20%。
    V16.2: 用 limit_pct_for 统一阈值。
    V16.3.3: is_st 显式传入优先（canonical 提供——避免 name 缺失/缓存过期导致 ST 判定失效）"""
    if not change_pct:
        return False
    thr = limit_pct_for(code, name)
    return change_pct >= thr - 0.5


def is_limit_down(code: str, name: str, change_pct: float, is_st: Optional[bool] = None) -> bool:
    """V7.5: 统一跌停判断。区分板块阈值。
    V10.0: ST 涨跌幅已放宽至 10%（与主板一致）。
    V16.2: 用 limit_pct_for 统一阈值。
    V16.3.3: is_st 显式传入优先（canonical 提供）。"""
    if not change_pct:
        return False
    thr = limit_pct_for(code, name)
    return change_pct <= -(thr - 0.5)


# ═══════════════════════════════════════
# TDX 清理
# ═══════════════════════════════════════

def _safe_cleanup_tdx() -> None:
    """安全清理 TDX 连接（忽略异常）。"""
    try:
        from core.tdx_client import cleanup_tdx
        cleanup_tdx()
    except Exception as _e:
        _debug_log(f"sc_utils safe_cleanup_tdx: {_e}")


# ═══════════════════════════════════════
# 命令行工具
# ═══════════════════════════════════════

def clean_codes(raw_list, verbose=False):
    """清洗股票代码列表：提取6位数字、去重、保持顺序、过滤无效项。

    支持的输入格式示例:
      - '600519'         -> '600519'
      - '002193如意'    -> '002193'
      - '300990同飞'    -> '300990'
      - '600143 金发'   -> '600143'  ('金发' 被过滤为无6位数字)
      - '601208东材'    -> '601208'  (重复出现时自动去重)

    Args:
        raw_list: 原始代码列表（可含中文/空格/符号）
        verbose: 是否打印清洗结果

    Returns:
        清洗后的6位代码列表（去重、保持首次出现顺序）
    """
    if not raw_list:
        return []

    seen = set()
    clean = []
    skipped = []
    flag_warnings = []
    for raw in raw_list:
        if not raw or not isinstance(raw, str):
            continue
        # V11.2: 检测命令行参数粘连（如 "601718际华--all"）
        if "--" in raw and not raw.strip().startswith("--"):
            flag_warnings.append(raw)
        raw_s = raw.strip().upper()
        # V16.3 O16: 显式前缀提取（sh/sz/bj）
        prefix = None
        for _p in ("SH", "SZ", "BJ"):
            if raw_s.startswith(_p):
                prefix = _p
                break
        # 前后缀矛盾拒绝（SH000001.SZ 自相矛盾——参考仓库 v3.6.0 norm_ticker）
        if prefix and (".SH" in raw_s or ".SZ" in raw_s or ".BJ" in raw_s):
            skipped.append(raw + "(前后缀矛盾)")
            continue
        # V16.3 O16: 不再截断 7 位数字（6005190 会截成 600519 返回另一只票的数据——参考仓库 v3.6.0）
        digits = "".join(c for c in raw if c.isdigit())
        if len(digits) != 6:
            skipped.append(raw)
            continue
        code = digits
        # V16.3 O16: 显式前缀与号段一致性（sh+6 沪市 / sz+0/3 深市 / bj+92/8/4 北交所；
        # sh000001 上证指数等 000 号段沪市指数被拒——参考仓库 v3.5.1/v3.6.0）
        if prefix:
            ok = (
                (prefix == "SH" and code.startswith("6"))
                or (prefix == "SZ" and code.startswith(("0", "3")))
                or (prefix == "BJ" and code.startswith(("92", "8", "4")))
            )
            if not ok:
                skipped.append(raw + "(前缀与号段矛盾)")
                continue
        if code in seen:
            skipped.append(raw + "(重复)")
            continue
        seen.add(code)
        clean.append(code)

    if verbose and flag_warnings:
        print(f"  ⚠️ 警告: 以下参数可能含命令行flag粘连（请检查空格）: "
              f"{', '.join(flag_warnings[:5])}", flush=True)

    if verbose and skipped:
        print(f"  🧹 代码清洗: 保留 {len(clean)} 个, 跳过 {len(skipped)} 个 "
              f"({', '.join(skipped[:5])}{'...' if len(skipped) > 5 else ''})", flush=True)

    return clean


def parse_args(report_type="unknown"):
    """命令行参数解析（参数化版本，兼容6个报告脚本）。

    V8.5新增：--depth参数，支持lite/medium/deep三档分析深度。

    - codes: 可选（默认空列表），个股分析脚本（sht/med/lng/ful）会用到；
             全市场扫描脚本（val/mak）不需要此参数，传空即可。
    - --depth: 分析深度 (lite=快速30秒/medium=标准5分钟/deep=深度15分钟，默认deep)
    """
    parser = argparse.ArgumentParser(description=report_type)
    parser.add_argument("codes", nargs="*", default=[],
                        help="股票代码，支持 1 个或多个（全市场扫描脚本不需要此参数）")
    parser.add_argument("-o", "--output",
                        default=os.path.join(get_script_dir(), "reports"),
                        help="报告输出目录（默认: 脚本目录下的 reports/）")
    parser.add_argument("--no-upload", action="store_true", help="跳过 Google Drive 上传")
    parser.add_argument("--depth", choices=["lite", "medium", "deep"], default="deep",
                        help="分析深度: lite=快速(30秒)/medium=标准(5分钟)/deep=深度(15分钟，默认)")
    return parser.parse_args()


# ═══════════════════════════════════════
# 配置文件加载（游资标签 / 公告关键词等）
# ═══════════════════════════════════════

_settings_cache = None  # 模块级缓存，只加载一次


def _load_settings() -> Dict[str, Any]:
    """从 keywords_config.yaml 加载关键词与标签配置（席位标签/公告关键词/政策关键词/日历映射）。

    返回 dict，模块级缓存（只读一次）。
    """
    global _settings_cache
    if _settings_cache is not None:
        return _settings_cache
    _path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keywords_config.yaml")
    try:
        import yaml
        with open(_path, 'r', encoding='utf-8') as f:
            _settings_cache = yaml.safe_load(f)
    except Exception as _e:
        _debug_log(f"_load_settings: {_e}")
        _settings_cache = {}
    return _settings_cache


# ═══════════════════════════════════════
# 策略阈值配置加载（strategy_config.yaml）
# ═══════════════════════════════════════

_strategy_config_cache: Optional[Dict[str, Any]] = None  # 模块级缓存


def _load_strategy_config() -> Dict[str, Any]:
    """从 strategy_config.yaml 加载量化策略阈值配置。

    返回嵌套 dict，模块级缓存（只读一次）。
    顶层键：market / technical / valuation / fundamental /
           fundflow / trader / holder / strategy / abnormal / report
    """
    global _strategy_config_cache
    if _strategy_config_cache is not None:
        return _strategy_config_cache
    _path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "strategy_config.yaml")
    try:
        import yaml
        with open(_path, 'r', encoding='utf-8') as f:
            _strategy_config_cache = yaml.safe_load(f)
    except Exception as _e:
        _debug_log(f"_load_strategy_config: {_e}")
        _strategy_config_cache = {}
    return _strategy_config_cache


# ═══════════════════════════════════════
# 报告工具（已迁移到 sc_datasource.py）
# ═══════════════════════════════════════
