#!/usr/bin/env python3
"""seat_db.py — 龙虎榜席位识别工具

版本信息:
    V1.0 2026-06-22 - 初始版本，支持22位游资席位识别
    V8.5 - 集成到个股分析系统
"""

import os
import json
from typing import Optional, Dict, Any, List, Tuple

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

    # 精确匹配简称
    for tier_name, members in tiers.items():
        for member in members:
            if member in seat_name or seat_name in member:
                return tier_name, member

    # 匹配别名
    for short_name, alias_list in aliases.items():
        for alias in alias_list:
            if alias in seat_name or seat_name in alias:
                # 找到对应的tier
                details = seat_details.get(short_name, {})
                tier = details.get("tier", "unknown")
                return tier, short_name
        # 别名列表中的名称本身也要检查
        if short_name in seat_name:
            details = seat_details.get(short_name, {})
            tier = details.get("tier", "unknown")
            return tier, short_name

    # 模糊匹配席位的关键词
    keywords_map = {
        "拉萨": ("regional", "拉萨天团"),
        "东财拉萨": ("regional", "拉萨天团"),
        "东方财富拉萨": ("regional", "拉萨天团"),
        "成都": ("regional", "成都帮"),
        "南一环路": ("regional", "成都帮"),
        "苏南帮": ("regional", "苏南帮"),
        "无锡": ("regional", "苏南帮"),
        "镇江": ("regional", "苏南帮"),
        "宁波桑田路": ("regional", "宁波桑田路"),
        "桑田路": ("regional", "宁波桑田路"),
        "光大佛山": ("legend", "佛山无影脚"),
        "佛山绿景路": ("legend", "佛山无影脚"),
        "季华六路": ("legend", "佛山无影脚"),
        "国泰君安上海江苏路": ("legend", "章盟主"),
        "上海江苏路": ("legend", "章盟主"),
        "章建平": ("legend", "章盟主"),
        "中信杭州延安路": ("legend", "章盟主"),
        "宁波彩虹北路": ("legend", "章盟主"),
        "中信上海溧阳路": ("legend", "孙哥"),
        "溧阳路": ("legend", "孙哥"),
        "古北路": ("new_2025", "古北路"),
        "赵老哥": ("legend", "赵老哥"),
        "赵强": ("legend", "赵老哥"),
        "绍兴解放北路": ("legend", "赵老哥"),
        "银河绍兴": ("legend", "赵老哥"),
        "华鑫红宝石路": ("legend", "炒股养家"),
        "宛平南路": ("legend", "炒股养家"),
        "炒股养家": ("legend", "炒股养家"),
        "大连黄河路": ("new_gen", "陈小群"),
        "陈小群": ("new_gen", "陈小群"),
        "中信上海凯滨路": ("new_gen", "呼家楼"),
        "凯滨路": ("new_gen", "呼家楼"),
        "呼家楼": ("new_gen", "呼家楼"),
        "北京总部": ("new_gen", "呼家楼"),
        "西安朱雀大街": ("new_gen", "方新侠"),
        "方新侠": ("new_gen", "方新侠"),
        "兴业陕西": ("new_gen", "方新侠"),
        "南京太平南路": ("new_gen", "作手新一"),
        "作手新一": ("new_gen", "作手新一"),
        "南京大钟亭": ("new_gen", "小鳄鱼"),
        "小鳄鱼": ("new_gen", "小鳄鱼"),
        "中金财富南京": ("new_gen", "小鳄鱼"),
        "天津东丽": ("new_gen", "交易猿"),
        "交易猿": ("new_gen", "交易猿"),
        "六一中路": ("new_2025", "六一中路"),
        "北京光华路": ("new_gen", "毛老板"),
        "毛老板": ("new_gen", "毛老板"),
        "广发上海东方路": ("new_gen", "毛老板"),
        "华泰浙江分公司": ("new_gen", "消闲派"),
        "消闲派": ("new_gen", "消闲派"),
    }

    for keyword, (tier, short) in keywords_map.items():
        if keyword in seat_name:
            return tier, short

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
            "winning_rate": "未知"
        }

    db = _load_seat_db()
    details = db.get("seat_details", {}).get(short_name, {})

    return {
        "tier": tier,
        "short_name": short_name,
        "style": details.get("style", "未知"),
        "traits": details.get("traits", []),
        "premium": details.get("premium", "未知"),
        "winning_rate": details.get("winning_rate", "N/A")
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
        "unknown": "未知"
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
        "拉萨天团"
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
