"""symbol_norm.py — 代码格式归一（P2-A，A3 边界归一）。

统一沪深京（沪/深/北交所）股票代码的多种书写格式，消除各源适配器内
散落的 `sh/sz/bj` 前缀拼接、`.XSHG/.XSHE/.BJ` 后缀拼接、东财 `em_secid_prefix`
等碎片化（且部分有 bug，如 sc_ftshare.ft_sfx 把北交所 8x/4x/43x/83x/87x 错判为 .XSHE）。

设计：
  - 规范内部表示 = 裸 6 位 + 市场(SH/SZ/BJ)。市场由**代码号段规则**权威判定
    （复用 sc_utils.em_secid_prefix，北交所 92/8/4/43/83/87 优先于 "9→沪"）。
  - 各源适配器通过 `.eastmoney()/.tencent()/.sina()/.joinquant()/.upper_suffix()`
    取得对应格式，避免重复拼接与号段错判。
  - 输入含显式前缀/后缀但与代码号段矛盾时**显式报错**（不静默猜测，遵守 A5）。

典型输入：
  600519 / sh600519 / SH600519 / 600519.XSHG / 600519.SH
  000001 / sz000001 / 000001.XSHE
  830799 / bj830799 / 830799.BJ / 920002 / 430047
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from stock_common.sc_utils import em_secid_prefix

_BJ_PREFIXES = ("92", "8", "4", "43", "83", "87")  # 北交所（新 92 + 老 43/83/87 + 老三板 8/4）
_SUFFIX_MARKET = {"XSHG": "SH", "SH": "SH", "XSHE": "SZ", "SZ": "SZ", "BJ": "BJ"}
_PREFIX_MARKET = {"SH": "SH", "SZ": "SZ", "BJ": "BJ"}


def market_of(code: str) -> str:
    """由裸 6 位代码权威判定市场（SH/SZ/BJ）。

    北交所号段(92/8/4/43/83/87) 必须先于 "9→沪" 判定，否则会拼出错误的 "1.92xxx"。
    """
    c = str(code)
    if c.startswith(_BJ_PREFIXES):
        return "BJ"
    if em_secid_prefix(c) == "1.":
        return "SH"
    return "SZ"


@dataclass(frozen=True)
class Symbol:
    """归一后的规范证券代码。"""

    code: str  # 裸 6 位
    market: str  # "SH" | "SZ" | "BJ"

    def eastmoney(self) -> str:
        """东财 secid：em_secid_prefix + 裸码（如 1.600519 / 0.000001 / 0.830799）。"""
        return f"{em_secid_prefix(self.code)}{self.code}"

    def tencent(self) -> str:
        """腾讯/新浪格式：小写市场前缀 + 裸码（sh600519 / sz000001 / bj830799）。"""
        return f"{self.market.lower()}{self.code}"

    # 新浪与腾讯同构（sh/sz/bj 小写前缀）
    sina = tencent

    def joinquant(self) -> str:
        """聚宽格式：裸码 + 后缀（600519.XSHG / 000001.XSHE / 830799.BJ）。"""
        return f"{self.code}{_SUFFIX_MARKET_INV[self.market]}"

    def upper_suffix(self) -> str:
        """大写后缀格式（600519.SH / 000001.SZ / 830799.BJ），供 fuyao 等使用。"""
        return f"{self.code}.{self.market}"


_SUFFIX_MARKET_INV = {"SH": ".XSHG", "SZ": ".XSHE", "BJ": ".BJ"}


_RE_PLAIN = re.compile(r"^(\d{6})$")
_RE_SUFFIX = re.compile(r"^(\d{6})\.(XSHG|XSHE|BJ|SH|SZ)$", re.I)
_RE_PREFIX = re.compile(r"^(sh|sz|bj)(\d{6})$", re.I)


def normalize_symbol(raw: object) -> Symbol:
    """将任意书写格式归一为 `Symbol`（裸 6 位 + 市场）。

    Raises:
        ValueError: 输入无法解析，或显式前缀/后缀与代码号段矛盾。
    """
    s = str(raw).strip()
    if not s:
        raise ValueError("空股票代码")

    m = _RE_SUFFIX.match(s)
    if m:
        code = m.group(1)
        derived = market_of(code)
        sfx_mkt = _SUFFIX_MARKET[m.group(2).upper()]
        if sfx_mkt != derived:
            raise ValueError(f"代码矛盾：{raw!r} 后缀暗示 {sfx_mkt}，但号段规则判定为 {derived}")
        return Symbol(code, derived)

    m = _RE_PREFIX.match(s)
    if m:
        code = m.group(2)
        derived = market_of(code)
        pfx_mkt = _PREFIX_MARKET[m.group(1).upper()]
        if pfx_mkt != derived:
            raise ValueError(f"代码矛盾：{raw!r} 前缀暗示 {pfx_mkt}，但号段规则判定为 {derived}")
        return Symbol(code, derived)

    if _RE_PLAIN.match(s):
        return Symbol(s, market_of(s))

    raise ValueError(f"无法解析股票代码：{raw!r}")
