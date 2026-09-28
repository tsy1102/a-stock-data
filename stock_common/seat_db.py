#!/usr/bin/env python3
"""seat_db.py — 龙虎榜席位识别工具

版本信息:
    V1.0 2026-06-22 - 初始版本，支持22位游资席位识别
    V8.5 - 集成到个股分析系统
    V9.0 2026-09-09 - 第四匹配层(seats真实营业部全称) + 补全14位游资；
                      修复"效果不明显"根因：真实龙虎榜完整营业部名此前无法命中已知库
"""

import os
import json
from typing import Optional, Dict, Any, Tuple

from stock_common.sc_network import _debug_log

# 席位数据库路径
_SEAT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seats.json")

# 全局缓存
_seat_db_cache: Optional[Dict[str, Any]] = None


def _load_seat_db() -> Dict[str, Any]:
    """加载席位数据库（模块级缓存）"""
    global _seat_db_cache
    if _seat_db_cache is not None:
        return _seat_db_cache
    try:
        with open(_SEAT_DB_PATH, 'r', encoding='utf-8') as f:
            _seat_db_cache = json.load(f)
    except Exception as _e:
        _debug_log(f"seat_db load error: {_e}")
        _seat_db_cache = {"tiers": {}, "seat_details": {}, "seat_aliases": {}}
    return _seat_db_cache


def identify_seat_tier(seat_name: str) -> Tuple[str, str]:
    """识别席位等级

    Args:
        seat_name: 席位名称（如"国泰君安上海江苏路"、"赵老哥"等）

    Returns:
        (tier, short_name) - 等级和简称
        tier: legend/new_gen/regional/new_2025/unknown
        short_name: 席位简称（如"章盟主"）
    """
    if not seat_name:
        return "unknown", ""

    db = _load_seat_db()
    tiers = db.get("tiers", {})
    aliases = db.get("seat_aliases", {})
    seat_details = db.get("seat_details", {})

    # M7 修复（2026-08-30）：原匹配用"双向子串 + 字典序首命中、无最长匹配"，
    # 短席位名（如"盟主"）易误判为顶级游资、长名反被抢匹配。现改为：
    #   1) 仍保留双向子串（member/alias in seat_name OR seat_name in member/alias）——
    #      反向子句不可删：锁定回归 test_removed_keywords_still_work_via_aliases
    #      要求 "拉萨" → "拉萨天团"（alias "拉萨团结路" 含 "拉萨" 仅能反向命中）；
    #   2) 收集全部候选后按"命中最长子串"优先（最具体者胜），等长再按
    #      tiers>aliases>keywords 的 priority 排序，消除字典序首命中的不确定性。
    keywords_map = {
        "光大佛山": ("legend", "佛山无影脚"),
        "中信杭州延安路": ("legend", "章盟主"),
        "宁波彩虹北路": ("legend", "章盟主"),
        "银河绍兴": ("legend", "赵老哥"),
        "中金财富南京": ("new_gen", "小鳄鱼"),
        "广发上海东方路": ("new_gen", "毛老板"),
    }

    _candidates = []  # (matched_len, priority, tier, short_name)  priority 越小越优先

    # 1) tiers 层（双向子串，最长匹配）
    for tier_name, members in tiers.items():
        for member in members:
            if member and (member in seat_name or seat_name in member):
                _candidates.append((len(member), 0, tier_name, member))

    # 2) aliases 层（双向子串，最长匹配）
    for short_name, alias_list in aliases.items():
        _matched_alias = None
        for alias in alias_list:
            if alias and (alias in seat_name or seat_name in alias):
                _matched_alias = alias
                break
        if (
            _matched_alias is None
            and short_name
            and (short_name in seat_name or seat_name in short_name)
        ):
            _matched_alias = short_name
        if _matched_alias is not None:
            details = seat_details.get(short_name, {})
            _candidates.append((len(_matched_alias), 1, details.get("tier", "unknown"), short_name))

    # 3) keywords_map 兜底（双向子串，最长匹配）
    for keyword, (tier, short) in keywords_map.items():
        if keyword and (keyword in seat_name or seat_name in keyword):
            _candidates.append((len(keyword), 2, tier, short))

    # 4) seats 层（2026-09 补全）：消费 seat_details[*].seats 的真实营业部全称。
    #    根因修复：真实龙虎榜输入为完整营业部名（OPERATEDEPT_NAME，如"国泰君安上海江苏路证券营业部"），
    #    而前两层只匹配昵称/片段，覆盖率极低导致大量席位落空 unknown。本层直接对真实营业部全称做
    #    双向子串匹配，使"国泰君安上海江苏路"命中章盟主、完整名亦命中。
    #    priority=3（最低），仅当无更长/更优先的前三层命中时才兜底，故不破坏三层测试契约。
    for sname, details in seat_details.items():
        for seat_full in details.get("seats", []):
            if not seat_full or seat_full in ("N/A",):
                continue
            if seat_full in seat_name:
                # 真实全称是 seat_name 的子串：重叠长度 = 真实全称长度
                _candidates.append((len(seat_full), 3, details.get("tier", "unknown"), sname))
            elif seat_name in seat_full:
                # seat_name 是真实全称的子串（如输入即片段）：重叠长度 = 输入长度
                _candidates.append((len(seat_name), 3, details.get("tier", "unknown"), sname))

    if _candidates:
        # 最长子串优先；等长则 priority 小者优先（tiers>aliases>keywords>seats）
        _candidates.sort(key=lambda c: (-c[0], c[1]))
        _best = _candidates[0]
        return _best[2], _best[3]

    return "unknown", ""


def get_seat_info(seat_name: str) -> Dict[str, Any]:
    """获取席位详细信息

    Args:
        seat_name: 席位名称

    Returns:
        席位信息字典，包含:
        - tier: 等级
        - short_name: 简称
        - style: 风格描述
        - traits: 特征列表
        - premium: 溢价判断
        - winning_rate: 胜率
    """
    tier, short_name = identify_seat_tier(seat_name)
    if not short_name:
        return {
            "tier": "unknown",
            "short_name": "",
            "style": "未知",
            "traits": [],
            "premium": "未知",
            "winning_rate": "未知",
        }

    db = _load_seat_db()
    details = db.get("seat_details", {}).get(short_name, {})

    return {
        "tier": tier,
        "short_name": short_name,
        "style": details.get("style", "未知"),
        "traits": details.get("traits", []),
        "premium": details.get("premium", "未知"),
        "winning_rate": details.get("winning_rate", "N/A"),
    }


def enhance_lhb_seats(lhb_data: Dict[str, Any]) -> Dict[str, Any]:
    """增强龙虎榜数据，添加席位分析

    Args:
        lhb_data: 原始龙虎榜数据，包含 seats: {buy: [...], sell: [...]}

    Returns:
        增强后的数据，增加:
        - buy_seats_analysis: 买方席位分析列表
        - sell_seats_analysis: 卖方席位分析列表
        - seat_quality_score: 席位质量评分 (0-100)
        - premium_signal: 溢价信号 (buy_high/sell_high/neutral)
    """
    result = dict(lhb_data)

    # 分析买方席位
    buy_analysis = []
    legend_count = 0
    positive_count = 0
    negative_count = 0

    for seat in lhb_data.get("seats", {}).get("buy", []):
        seat_name = seat.get("name", "")
        info = get_seat_info(seat_name)
        enhanced_seat = dict(seat)
        enhanced_seat["tier"] = info["tier"]
        enhanced_seat["short_name"] = info["short_name"]
        enhanced_seat["style"] = info["style"]
        enhanced_seat["premium"] = info["premium"]
        enhanced_seat["traits"] = info["traits"]

        buy_analysis.append(enhanced_seat)

        if info["tier"] == "legend":
            legend_count += 1
        if info["premium"] == "正面":
            positive_count += 1
        elif info["premium"] == "反向指标":
            negative_count += 1

    # 分析卖方席位
    sell_analysis = []
    sell_legend_count = 0
    sell_positive_count = 0
    sell_negative_count = 0

    for seat in lhb_data.get("seats", {}).get("sell", []):
        seat_name = seat.get("name", "")
        info = get_seat_info(seat_name)
        enhanced_seat = dict(seat)
        enhanced_seat["tier"] = info["tier"]
        enhanced_seat["short_name"] = info["short_name"]
        enhanced_seat["style"] = info["style"]
        enhanced_seat["premium"] = info["premium"]
        enhanced_seat["traits"] = info["traits"]

        sell_analysis.append(enhanced_seat)

        if info["tier"] == "legend":
            sell_legend_count += 1
        if info["premium"] == "正面":
            sell_positive_count += 1
        elif info["premium"] == "反向指标":
            sell_negative_count += 1

    # 计算席位质量评分 (0-100)
    # V17.0.25(2026-09-02) P1-6 修复: 当龙虎榜席位全部未匹配到已知游资库(_recognized==0)时,
    # 原逻辑恒输出基础分50 + neutral, 是伪精确评分(审计发现22份恒50/恒neutral)。此时评分无意义,
    # 降级为 None / "unknown", 由渲染层标注「席位库未收录, 无法评级」。
    _recognized = (
        legend_count
        + sell_legend_count
        + positive_count
        + sell_positive_count
        + negative_count
        + sell_negative_count
    )
    if _recognized == 0:
        seat_quality_score = None
        premium_signal = "unknown"
    else:
        # 基础分50
        seat_quality_score = 50

        # legend席位每次加10分
        seat_quality_score += legend_count * 10
        seat_quality_score += sell_legend_count * 5  # 卖方legend权重稍低

        # 正面席位加分
        seat_quality_score += positive_count * 5
        # 反向席位扣分
        seat_quality_score -= negative_count * 8

        seat_quality_score = max(0, min(100, seat_quality_score))

        # 判断溢价信号
        if legend_count >= 2 and positive_count > negative_count:
            premium_signal = "buy_high"  # 强势买入信号
        elif sell_negative_count >= 2:
            premium_signal = "sell_high"  # 强势卖出信号
        elif negative_count > positive_count:
            premium_signal = "sell_caution"  # 卖出警示
        else:
            premium_signal = "neutral"

    result["buy_seats_analysis"] = buy_analysis
    result["sell_seats_analysis"] = sell_analysis
    result["seat_quality_score"] = seat_quality_score
    result["premium_signal"] = premium_signal
    result["legend_count"] = legend_count
    result["positive_seats"] = positive_count
    result["negative_seats"] = negative_count

    # 知名席位列表（有 short_name 的席位）
    notable_seats = [s["short_name"] for s in buy_analysis + sell_analysis if s.get("short_name")]
    result["notable_seats"] = notable_seats

    return result


def get_tier_label(tier: str) -> str:
    """获取等级中文标签"""
    labels = {
        "legend": "殿堂级",
        "new_gen": "新生代",
        "regional": "区域帮派",
        "new_2025": "2025新晋",
        "unknown": "未知",
    }
    return labels.get(tier, "未知")


# 测试
if __name__ == "__main__":
    # 测试用例
    test_seats = [
        "国泰君安上海江苏路",
        "中信上海溧阳路",
        "光大佛山绿景路",
        "华鑫上海红宝石路",
        "东方财富拉萨团结路第二证券营业部",
        "华泰成都南一环路第二证券营业部",
        "招商证券福州六一中路证券营业部",
        "拉萨天团",
    ]

    print("=== 席位识别测试 ===\n")
    for seat in test_seats:
        tier, short = identify_seat_tier(seat)
        info = get_seat_info(seat)
        print(f"输入: {seat}")
        print(f"  等级: {tier} ({get_tier_label(tier)})")
        print(f"  简称: {short}")
        print(f"  风格: {info['style']}")
        print(f"  溢价: {info['premium']}")
        print()
