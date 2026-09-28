#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""field_meta.py — 字段级 raw/computed 与窗口溯源元数据注册表 (V17.2.7, 2026-09-09)

为采集层(raw_{source}.json)与对撞工具提供字段身份元数据, 解决 13 轮对撞暴露的
根本误判风险: 把"服务端计算指标(computed)"误当"交易所原始字段(raw)"去跨源对撞。

字段元数据维度:
  - kind         : RAW(交易所原始) / COMPUTED(服务端计算衍生) / PLACEHOLDER(恒空/恒0占位) / UNKNOWN
  - window       : 取值窗口(snapshot / intraday / rolling 等), 时间依赖字段的复算前提
  - anchor_source: 独立重算锚源(tdx_kline / fuyao / ulist_np / none), 供对撞器分发
  - note         : 已知语义 / 定级摘要

消费方:
  1) capture_field_probe.py  —— 采集时把 field_meta_block(source) 嵌入 raw 文件顶层 `field_meta` 键,
     使原始采集物自带字段身份溯源(非事后补注)。
  2) 跨源对撞分析脚本    —— 按 anchor_source 分发"该用哪个锚源独立重算"。

设计约束: 本模块仅依赖标准库, 零 import 负担, 可被采集脚本与分析脚本安全引入,
不触发 stock_common 重依赖链路。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class FieldKind(str, Enum):
    RAW = "raw"  # 交易所原始字段
    COMPUTED = "computed"  # 服务端计算指标(衍生)
    PLACEHOLDER = "placeholder"  # 恒空 / 恒0 占位符, 无信息量
    UNKNOWN = "unknown"  # 尚未判定


@dataclass
class FieldMeta:
    idx: int
    kind: FieldKind
    window: str = "snapshot"
    anchor_source: str = "none"  # tdx_kline / fuyao / ulist_np / none
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "idx": self.idx,
            "kind": self.kind.value,
            "window": self.window,
            "anchor_source": self.anchor_source,
            "note": self.note,
        }


# ---------------------------------------------------------------------------
# 腾讯(tx)方案字段注册表 —— 依据 docs/field_verification 各轮对撞定案播种
# 仅登记已判定的字段; 未登记字段 classify_field 回退 UNKNOWN。
# ---------------------------------------------------------------------------
TENCENT_FIELD_META: Dict[int, FieldMeta] = {
    7: FieldMeta(
        7, FieldKind.RAW, "intraday", "tdx_quotes", "外盘(主动买盘, 手; 科创板688=股), L1 三源确认"
    ),
    8: FieldMeta(
        8, FieldKind.RAW, "intraday", "tdx_quotes", "内盘(主动卖盘, 手; 科创板688=股), L1 三源确认"
    ),
    29: FieldMeta(
        29,
        FieldKind.PLACEHOLDER,
        "snapshot",
        "none",
        "最近逐笔成交, 恒空占位符(H12 全日期 237/237 判定)",
    ),
    40: FieldMeta(
        40, FieldKind.RAW, "snapshot", "none", "停牌状态标记('S'=停牌中), L3 方向确证覆盖不完整"
    ),
    45: FieldMeta(
        45,
        FieldKind.COMPUTED,
        "snapshot",
        "fuyao",
        "总市值(亿元)=fuyao float_market_cap×(总股本/流通股本)÷1e8, L1 fuyao锚; "
        "2026-09-09 通达信官方 get_more_info `Zsz`=总市值 命名字段语义交叉确认(双官方 L1); "
        "qt[45]同源自洽(18/18 同量级)佐证; TDX Zsz 实时严格比值待13:00重试",
    ),
    47: FieldMeta(
        47,
        FieldKind.COMPUTED,
        "snapshot",
        "fuyao",
        "涨停价(元)=prev_price×板块自适应幅度(主板1.10/双创1.20/北交1.30), L1 fuyao锚; "
        "2026-09-09 通达信官方 `ZTPrice`=涨停价 命名字段语义交叉确认(双官方 L1); "
        "qt 实时定位 prev_close×板幅同值下标(7/18精确一致,余基准日错位解释); TDX ZTPrice 严格比对待13:00重试",
    ),
    51: FieldMeta(
        51,
        FieldKind.COMPUTED,
        "intraday",
        "tdx_kline",
        "均价/VWAP(元)=amount÷volume, L1 实测命中 tx[51] 20/20; "
        "2026-09-09 TDX K线独立重算 VWAP=RawAmount/RawVolume Pearson=1.0/"
        "slope=1.0/残差<0.005 第四源精确定案 L1(TDX K线独立重算)",
    ),
    56: FieldMeta(
        56,
        FieldKind.COMPUTED,
        "rolling",
        "tdx_kline",
        "Beta(系统风险), 基准=宽基全市场指数(类中证全指/国证A指); "
        "round13 第四源 TDX K线 β_中证全指 Pearson=0.991 身份确认(L4), 待腾讯字段表升L1",
    ),
    83: FieldMeta(
        83, FieldKind.PLACEHOLDER, "snapshot", "none", "恒'0'占位符(H12 全日期 237/237 判定)"
    ),
    85: FieldMeta(
        85,
        FieldKind.COMPUTED,
        "intraday",
        "tdx_kline",
        "价格类字段, L3 候选强; 2026-09-09 VWAP 扩展对撞 slope=0.998/残差max 0.54 "
        "→ 第四源确认非均价(与 round12 均价锚证伪一致); 近似当前价/最新价类(单快照"
        "无法用结算 close 精确复现), 维持 L3, 待腾讯字段文档",
    ),
    86: FieldMeta(
        86, FieldKind.RAW, "intraday", "none", "手级带符号量(交易所原始量, 语义未破解), L4"
    ),
}

# 各源注册表(目前仅 tencent 有逐字段语义; 其余源按 SOURCE_SCHEME 族管理)
SOURCE_FIELD_META: Dict[str, Dict[int, FieldMeta]] = {
    "tencent": TENCENT_FIELD_META,
}


def classify_field(source: str, idx: int) -> FieldMeta:
    """返回某源某字段的身份元数据; 未登记回退 UNKNOWN。"""
    reg = SOURCE_FIELD_META.get(source, {})
    if idx in reg:
        return reg[idx]
    return FieldMeta(idx, FieldKind.UNKNOWN, "unknown", "none", "未登记")


def field_meta_block(source: str) -> Optional[dict]:
    """返回可嵌入 raw_{source}.json 顶层的 field_meta 块; 该源无注册表返回 None。"""
    reg = SOURCE_FIELD_META.get(source)
    if not reg:
        return None
    return {
        "scheme": source if source != "tencent" else "tencent",
        "kind_enum": [k.value for k in FieldKind],
        "n_registered": len(reg),
        "fields": {str(idx): m.to_dict() for idx, m in sorted(reg.items())},
        "generated_by": "field_meta.py@V17.2.7",
        "note": "kind=raw/computed/placeholder; computed 字段须按 anchor_source 独立重算后对错, "
        "禁止与 raw 交易所字段直接跨源对撞(须按 anchor_source 独立重算后比对)",
    }


if __name__ == "__main__":
    print(json.dumps(field_meta_block("tencent"), ensure_ascii=False, indent=1))
