#!/usr/bin/env python3
"""trap_detector.py — 杀猪盘8信号检测 V1.0 (V8.5内置模块)

版本信息:
    V1.0 2026-06-22 - 初始版本，支持8维杀猪盘检测
    V8.5 - 集成到个股分析系统

基于 UZI-Skill 的杀猪盘检测方法论，实现8维检测框架：
1. 大量低质量账号同时推荐
2. 推荐话术模板化
3. 付费社群/VIP直播间引流
4. 基本面与热度脱节
5. K线异常配合
6. "老师/股神"人设推广
7. 跨平台联动推广
8. 虚假研报/伪造消息

Usage:
    from trap_detector import detect_trap_signals, get_trap_score
"""

import re
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# 用户输入关键词加权
USER_KEYWORDS = {
    "朋友推荐": 1, "群里": 1, "老师": 1, "带我": 1,
    "内幕": 2, "稳赚": 2, "必涨": 1, "翻倍": 1,
    "稳赚不赔": 2, "包赚": 2,
}

# 推荐话术模板关键词
TRAP_PHRASES = [
    "即将爆发", "重大利好", "主力建仓完毕", "庄家洗盘结束",
    "目标翻倍", "目标价", "最后上车机会", "错过等十年",
    "底部反转信号", "技术面突破", "内部消息", "知情人爆料",
    "赶紧买入", "满仓干", "重仓", "梭哈", "跟上", "赚钱",
    "布局", "拉升", "牛股", "涨停板"
]

# 高风险板块（容易被杀猪盘利用）
HIGH_RISK_PLATES = [
    "ST", "*ST", "S", "S*",
    "创业板", "科创板", "北交所",
    "次新股", "新股", "壳资源"
]


@dataclass
class TrapSignal:
    """单个信号检测结果"""
    hit: bool = False
    weight: int = 0
    evidence: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class TrapDetectionResult:
    """杀猪盘检测结果"""
    code: str = ""
    name: str = ""
    trap_score: int = 10  # 1-10, 10=最安全
    level: str = "安全"  # 安全/注意/警惕/高度可疑
    signals: Dict[str, TrapSignal] = field(default_factory=dict)
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)

    def is_trap_suspected(self) -> bool:
        """是否疑似杀猪盘"""
        return self.level in ("警惕", "高度可疑")

    def get_warning_level(self) -> int:
        """获取警告级别 0-3"""
        if self.level == "高度可疑":
            return 3
        elif self.level == "警惕":
            return 2
        elif self.level == "注意":
            return 1
        return 0


def _safe_float(val: Any, default: float = 0.0) -> float:
    """安全转换为float"""
    try:
        v = float(val)
        return v if abs(v) < 1e10 else default
    except (TypeError, ValueError):
        return default


def _detect_signal_1_low_quality_recommendations(code: str, name: str) -> TrapSignal:
    """信号1: 大量低质量账号同时推荐

    检测方法:
    - 搜索 "{name} 推荐" 返回 ≥ 10 个标题相似的内容
    - 内容来自 0-100 粉的小号 / 新建公众号
    - 推荐时间集中在近 7-30 天

    注意: 此检测需要web search API，暂时返回未检测状态
    """
    signal = TrapSignal(
        hit=False,
        weight=2,
        description="大量低质量账号同时推荐"
    )

    # TODO: 需要web search API支持
    # 目前标记为需要人工判断
    signal.evidence.append("⚠️ 需要Web搜索验证")

    return signal


def _detect_signal_2_template_phrases(code: str, name: str, news_titles: List[str] = None) -> TrapSignal:
    """信号2: 推荐话术模板化

    检测方法:
    - news_titles 或搜索结果中出现 ≥ 2 个模板关键词
    """
    signal = TrapSignal(
        hit=False,
        weight=1,
        description="推荐话术模板化"
    )

    # 如果没有传入news_titles，无法检测
    if not news_titles:
        signal.evidence.append("⚠️ 无舆情数据，无法检测话术模板化")
        return signal

    # 合并股名和代码搜索
    search_text = " ".join(news_titles)
    search_text += f" {name} {code}"

    matched_phrases = []
    for phrase in TRAP_PHRASES:
        if phrase in search_text:
            matched_phrases.append(phrase)

    if len(matched_phrases) >= 2:
        signal.hit = True
        signal.evidence.append(f"命中话术模板: {', '.join(matched_phrases)}")

    return signal


def _detect_signal_3_paid_groups(code: str, name: str) -> TrapSignal:
    """信号3: 付费社群/VIP直播间引流

    检测方法:
    - 搜索 "{name} 微信群"、"{name} 直播间"、"{name} VIP" 命中
    - 推荐内容附带二维码 / 加群链接 / 老师微信
    - 抖音 / 快手直播间出现该股

    注意: 此检测需要web search API，暂时返回未检测状态
    """
    signal = TrapSignal(
        hit=False,
        weight=2,
        description="付费社群/VIP直播间引流"
    )

    # TODO: 需要web search API支持
    signal.evidence.append("⚠️ 需要Web搜索验证")

    return signal


def _detect_signal_4_fundamental_mismatch(code: str, name: str,
                                         info: Dict[str, Any] = None,
                                         sentiment_data: Dict[str, Any] = None) -> TrapSignal:
    """信号4: 基本面与热度脱节

    检测方法 (任一命中即触发):
    - 公司亏损或 ROE < 5%，但近 30 天讨论量翻倍
    - 行业景气度下行，但股价异动
    - 财务造假嫌疑（应收账款/存货异常）+ 推广热度高

    Args:
        info: 基本面信息 {"roe": float, "net_profit": float, "industry": str}
        sentiment_data: 情绪数据 {"hot_score": int, "hot_trend": str}
    """
    signal = TrapSignal(
        hit=False,
        weight=3,
        description="基本面与热度脱节"
    )

    # ROE检查
    if info:
        roe = info.get("roe", 0)
        net_profit = info.get("net_profit", 0)

        # 亏损检测
        if net_profit < 0:
            if sentiment_data and sentiment_data.get("hot_score", 0) > 500:
                signal.hit = True
                signal.evidence.append(f"⚠️ 公司亏损但热度较高(热度:{sentiment_data.get('hot_score')})")

        # ROE过低
        if 0 < roe < 5:
            if sentiment_data and sentiment_data.get("hot_score", 0) > 500:
                signal.hit = True
                signal.evidence.append(f"⚠️ ROE={roe:.1f}%<5%但热度较高(热度:{sentiment_data.get('hot_score')})")

    # 热度异常检测
    if sentiment_data:
        hot_trend = sentiment_data.get("hot_trend", "")
        if hot_trend in ("surge", "explosion") and (not info or info.get("roe", 0) < 10):
            signal.hit = True
            signal.evidence.append(f"⚠️ 热度异常飙升({hot_trend})但基本面一般")

    if not signal.hit:
        signal.evidence.append("✅ 基本面与热度未发现明显脱节")

    return signal


def _detect_signal_5_kline_anomaly(code: str, name: str,
                                   kline_data: Dict[str, Any] = None,
                                   price_change_pct: float = 0) -> TrapSignal:
    """信号5: K线异常配合

    检测方法:
    - 推荐密集期前 30-60 天内已有 ≥ 50% 涨幅
    - 推荐密集期出现放量横盘 / 拉升出货特征
    - 大宗交易折价 + 推广同时发生

    Args:
        kline_data: K线数据 {"prices": [float], "volumes": [float], "ma5": float, "ma20": float}
        price_change_pct: 近期涨跌幅
    """
    signal = TrapSignal(
        hit=False,
        weight=3,
        description="K线异常配合"
    )

    # 短期暴涨检测（可能是出货前兆）
    if price_change_pct > 50:
        signal.hit = True
        signal.evidence.append(f"⚠️ 近期涨幅{price_change_pct:.1f}%，存在出货嫌疑")

    # K线数据异常检测
    if kline_data:
        prices = kline_data.get("prices", [])
        volumes = kline_data.get("volumes", [])

        if len(prices) >= 20 and len(volumes) >= 20:
            # 检测放量滞涨（量增价不动）
            recent_vol = volumes[-5:]
            avg_vol = sum(volumes[-20:-5]) / 15 if len(volumes) >= 20 else sum(volumes) / len(volumes)

            if avg_vol > 0 and sum(recent_vol) / 5 > avg_vol * 2:
                price_change_recent = (prices[-1] / prices[-5] - 1) * 100 if prices[-5] > 0 else 0
                if abs(price_change_recent) < 5:
                    signal.hit = True
                    signal.evidence.append(f"⚠️ 放量滞涨(量放大2倍但涨幅{price_change_recent:.1f}%)")

            # 检测高位横盘
            if prices[-1] > 0 and prices[-20] > 0:
                high_price = max(prices[-20:])
                current_price = prices[-1]
                if current_price > high_price * 0.95:  # 维持在高位5%以内
                    if sum(volumes[-10:]) / 10 > sum(volumes[-20:-10]) / 10:  # 近期量能放大
                        signal.hit = True
                        signal.evidence.append("⚠️ 高位横盘+量能放大，可能为出货做准备")

    if not signal.hit:
        signal.evidence.append("✅ K线形态未发现明显异常")

    return signal


def _detect_signal_6_teacher_marketing(code: str, name: str, news_titles: List[str] = None) -> TrapSignal:
    """信号6: "老师/股神"人设推广

    检测方法:
    - 关键词: "X老师"、"操盘手X"、"内部老师"、"打板高手"
    - 配图常为豪车/名表/高额对账单截图
    - 历史"战绩"无法验证（无龙虎榜、无实盘账户）

    Args:
        news_titles: 新闻/帖子标题列表
    """
    signal = TrapSignal(
        hit=False,
        weight=2,
        description=""老师/股神"人设推广"
    )

    teacher_keywords = [
        "老师", "股神", "操盘手", "内部老师", "打板高手",
        "带单", "跟单", "代客理财", "私募", "公募",
        "专业团队", "老师带你", "跟上老师", "加群",
        "微信号", "二维码", "直播间", "VIP群"
    ]

    if news_titles:
        search_text = " ".join(news_titles)
        matched = [kw for kw in teacher_keywords if kw in search_text]

        if matched:
            signal.hit = True
            signal.evidence.append(f"⚠️ 命中营销话术: {', '.join(matched)}")
    else:
        signal.evidence.append("⚠️ 无舆情数据，无法检测人设推广")

    if not signal.hit:
        signal.evidence.append("✅ 未发现老师/股神营销话术")

    return signal


def _detect_signal_7_cross_platform(code: str, name: str, social_data: Dict[str, Any] = None) -> TrapSignal:
    """信号7: 跨平台联动推广

    检测方法:
    - 在 ≥ 3 个平台同时找到推荐
    - 平台: 小红书/抖音/快手/B站/知乎/公众号/Twitter/微博

    Args:
        social_data: 社交平台数据 {"weibo": bool, "zhihu": bool, "douyin": bool, ...}
    """
    signal = TrapSignal(
        hit=False,
        weight=2,
        description="跨平台联动推广"
    )

    if not social_data:
        signal.evidence.append("⚠️ 无社交平台数据，无法检测跨平台推广")
        return signal

    platforms = social_data.get("active_platforms", [])
    if len(platforms) >= 3:
        signal.hit = True
        signal.evidence.append(f"⚠️ 同时在{len(platforms)}个平台推广: {', '.join(platforms)}")
    elif len(platforms) >= 2:
        signal.evidence.append(f"⚠️ 在{len(platforms)}个平台推广(≥3平台更可疑): {', '.join(platforms)}")
    else:
        signal.evidence.append("✅ 未发现跨平台联动推广")

    return signal


def _detect_signal_8_fake_research(code: str, name: str,
                                   reports: List[Dict] = None,
                                   announcements: List[Dict] = None) -> TrapSignal:
    """信号8: 虚假研报/伪造消息

    检测方法:
    - 搜索 "{name} 谣言" / "{name} 辟谣" 命中公司公告
    - 网传研报无券商水印 / 无分析师签名
    - 公司主动澄清传闻

    Args:
        reports: 研报列表 [{"title": str, "broker": str, "analyst": str}]
        announcements: 公告列表 [{"title": str, "date": str}]
    """
    signal = TrapSignal(
        hit=False,
        weight=3,
        description="虚假研报/伪造消息"
    )

    # 检测无来源研报
    if reports:
        for report in reports[:5]:  # 检查最近5篇
            title = report.get("title", "")
            broker = report.get("broker", "")
            analyst = report.get("analyst", "")

            # 无券商来源
            if not broker or broker in ("", "未知", "网络流传"):
                signal.hit = True
                signal.evidence.append(f"⚠️ 研报无券商来源: {title[:30]}...")
                continue

            # 无分析师签名
            if not analyst or analyst in ("", "未知"):
                signal.hit = True
                signal.evidence.append(f"⚠️ 研报无分析师签名: {title[:30]}...")

    # 检测辟谣公告
    if announcements:
        rumor_keywords = ["澄清", "辟谣", "不存在", "未发生", "虚假信息", "不实信息"]
        for ann in announcements[:10]:  # 检查最近10条
            title = ann.get("title", "")
            for keyword in rumor_keywords:
                if keyword in title:
                    signal.hit = True
                    signal.evidence.append(f"⚠️ 公司发布澄清公告: {title}")
                    break

    if not signal.hit:
        signal.evidence.append("✅ 未发现虚假研报或伪造消息")

    return signal


def detect_trap_signals(code: str, name: str,
                        info: Dict[str, Any] = None,
                        kline_data: Dict[str, Any] = None,
                        sentiment_data: Dict[str, Any] = None,
                        social_data: Dict[str, Any] = None,
                        reports: List[Dict] = None,
                        announcements: List[Dict] = None,
                        news_titles: List[str] = None,
                        price_change_pct: float = 0,
                        user_keywords: List[str] = None) -> TrapDetectionResult:
    """杀猪盘8信号检测主函数

    Args:
        code: 股票代码
        name: 股票名称
        info: 基本面信息 {"roe": float, "net_profit": float, "industry": str}
        kline_data: K线数据 {"prices": [float], "volumes": [float], "ma5": float, "ma20": float}
        sentiment_data: 情绪数据 {"hot_score": int, "hot_trend": str}
        social_data: 社交平台数据 {"active_platforms": [str]}
        reports: 研报列表 [{"title": str, "broker": str, "analyst": str}]
        announcements: 公告列表 [{"title": str, "date": str}]
        news_titles: 新闻/帖子标题列表
        price_change_pct: 近期涨跌幅
        user_keywords: 用户输入的关键词 ["朋友推荐", "群里", "老师", ...]

    Returns:
        TrapDetectionResult: 包含8个信号检测结果和综合评分
    """
    result = TrapDetectionResult(code=code, name=name)

    # 执行8个信号检测
    signals = []

    # 信号1: 大量低质量账号同时推荐
    s1 = _detect_signal_1_low_quality_recommendations(code, name)
    result.signals["signal_1_low_quality"] = s1
    signals.append((s1.hit, s1.weight))

    # 信号2: 推荐话术模板化
    s2 = _detect_signal_2_template_phrases(code, name, news_titles)
    result.signals["signal_2_template"] = s2
    signals.append((s2.hit, s2.weight))

    # 信号3: 付费社群/VIP直播间引流
    s3 = _detect_signal_3_paid_groups(code, name)
    result.signals["signal_3_paid_groups"] = s3
    signals.append((s3.hit, s3.weight))

    # 信号4: 基本面与热度脱节
    s4 = _detect_signal_4_fundamental_mismatch(code, name, info, sentiment_data)
    result.signals["signal_4_fundamental_mismatch"] = s4
    signals.append((s4.hit, s4.weight))

    # 信号5: K线异常配合
    s5 = _detect_signal_5_kline_anomaly(code, name, kline_data, price_change_pct)
    result.signals["signal_5_kline_anomaly"] = s5
    signals.append((s5.hit, s5.weight))

    # 信号6: "老师/股神"人设推广
    s6 = _detect_signal_6_teacher_marketing(code, name, news_titles)
    result.signals["signal_6_teacher_marketing"] = s6
    signals.append((s6.hit, s6.weight))

    # 信号7: 跨平台联动推广
    s7 = _detect_signal_7_cross_platform(code, name, social_data)
    result.signals["signal_7_cross_platform"] = s7
    signals.append((s7.hit, s7.weight))

    # 信号8: 虚假研报/伪造消息
    s8 = _detect_signal_8_fake_research(code, name, reports, announcements)
    result.signals["signal_8_fake_research"] = s8
    signals.append((s8.hit, s8.weight))

    # 计算加权命中数
    weighted_hits = sum(weight for hit, weight in signals if hit)

    # 用户关键词加权
    user_keyword_bonus = 0
    if user_keywords:
        for kw in user_keywords:
            user_keyword_bonus += USER_KEYWORDS.get(kw, 0)

    # 计算最终评分 (10 - 加权命中数 - 用户关键词加权)
    # 基础分10分，每个命中扣相应权重
    final_score = max(1, min(10, 10 - weighted_hits - user_keyword_bonus))
    result.trap_score = final_score

    # 确定风险等级
    if final_score >= 9:
        result.level = "安全"
    elif final_score >= 6:
        result.level = "注意"
    elif final_score >= 3:
        result.level = "警惕"
    else:
        result.level = "高度可疑"

    # 生成摘要
    hit_signals = [s.description for s in result.signals.values() if s.hit]
    if hit_signals:
        result.summary = f"命中{len(hit_signals)}个风险信号: {', '.join(hit_signals[:3])}"
        if len(hit_signals) > 3:
            result.summary += f"等({len(hit_signals)}个)"
    else:
        result.summary = "未发现明显杀猪盘特征"

    # 生成建议
    if result.level == "高度可疑":
        result.recommendations = [
            "⚠️ 高度警惕：疑似杀猪盘，建议立即远离",
            "不要轻信任何荐股信息",
            "不要加入任何收费群或直播间",
            "不要跟随所谓的"老师"操作"
        ]
    elif result.level == "警惕":
        result.recommendations = [
            "⚠️ 保持警惕：存在多个风险信号",
            "谨慎评估信息来源",
            "不要仅凭荐股信息做出投资决策",
            "建议通过正规渠道获取投资信息"
        ]
    elif result.level == "注意":
        result.recommendations = [
            "⚠️ 注意：存在部分可疑特征",
            "保持理性判断",
            "核实信息来源的可靠性"
        ]
    else:
        result.recommendations = [
            "✅ 暂未发现明显杀猪盘特征",
            "，但仍需保持理性投资",
            "通过正规渠道获取投资信息"
        ]

    return result


def get_trap_score_short(code: str, name: str,
                         info: Dict[str, Any] = None,
                         price_change_pct: float = 0) -> Tuple[int, str]:
    """快速杀猪盘评分（简化版，不需要完整数据）

    Returns:
        (trap_score, level): 评分(1-10)和等级描述
    """
    result = detect_trap_signals(
        code=code,
        name=name,
        info=info,
        price_change_pct=price_change_pct
    )
    return result.trap_score, result.level


def format_trap_detection_report(result: TrapDetectionResult) -> str:
    """格式化杀猪盘检测报告

    Args:
        result: 检测结果

    Returns:
        格式化的报告字符串
    """
    lines = []
    lines.append("=" * 50)
    lines.append(f"【杀猪盘检测报告】 {result.code} {result.name}")
    lines.append("=" * 50)

    # 风险等级
    level_emoji = {
        "安全": "🟢",
        "注意": "🟡",
        "警惕": "🟠",
        "高度可疑": "🔴"
    }
    emoji = level_emoji.get(result.level, "⚪")
    lines.append(f"\n风险等级: {emoji} {result.level} (评分: {result.trap_score}/10)")
    lines.append(f"检测结论: {result.summary}")

    # 详细信号
    lines.append("\n--- 8维风险信号检测 ---")
    signal_names = {
        "signal_1_low_quality": "1.低质量账号推荐",
        "signal_2_template": "2.话术模板化",
        "signal_3_paid_groups": "3.付费社群引流",
        "signal_4_fundamental_mismatch": "4.基本面热度脱节",
        "signal_5_kline_anomaly": "5.K线异常配合",
        "signal_6_teacher_marketing": "6.老师人设推广",
        "signal_7_cross_platform": "7.跨平台联动",
        "signal_8_fake_research": "8.虚假研报"
    }

    for key, signal in result.signals.items():
        name = signal_names.get(key, key)
        status = "❌ 命中" if signal.hit else "✅ 未命中"
        lines.append(f"\n{status} {name}")
        for evidence in signal.evidence:
            lines.append(f"   {evidence}")

    # 建议
    lines.append("\n--- 投资建议 ---")
    for rec in result.recommendations:
        lines.append(rec)

    lines.append("")
    return "\n".join(lines)


# 测试
if __name__ == "__main__":
    # 测试用例
    test_cases = [
        {
            "code": "600519",
            "name": "贵州茅台",
            "info": {"roe": 25.0, "net_profit": 10000000000},
            "price_change_pct": 5.0
        },
        {
            "code": "300999",
            "name": "某疑似股票",
            "info": {"roe": 2.0, "net_profit": -100000000},
            "price_change_pct": 60.0,
            "news_titles": ["某疑似股票即将暴涨", "重大利好", "老师带你赚钱", "加群获取内幕"]
        }
    ]

    print("=== 杀猪盘检测测试 ===\n")
    for tc in test_cases:
        result = detect_trap_signals(
            code=tc["code"],
            name=tc["name"],
            info=tc.get("info"),
            price_change_pct=tc.get("price_change_pct", 0),
            news_titles=tc.get("news_titles")
        )
        print(format_trap_detection_report(result))
