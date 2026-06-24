#!/usr/bin/env python3
"""social_sentiment.py — 社交热榜聚合 V1.0 (V8.5内置模块)

版本信息:
    V1.0 2026-06-22 - 初始版本，支持6平台情绪聚合
    V8.5 - 集成到个股分析系统

支持6平台情绪聚合：
- 微博
- 知乎
- 抖音
- 今日头条
- 百度
- B站

Usage:
    from social_sentiment import get_social_sentiment, get_social_sentiment_async
"""

import re
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

# 平台配置
PLATFORMS = ["weibo", "zhihu", "douyin", "toutiao", "baidu", "bilibili"]


@dataclass
class PlatformData:
    """单个平台数据"""
    platform: str
    hot_score: int = 0
    sentiment: float = 0.0  # -1到1，负数为负面
    trending: bool = False
    posts_count: int = 0
    error: str = ""


@dataclass
class SocialSentimentResult:
    """综合社交情绪结果"""
    code: str = ""
    name: str = ""
    total_hot: int = 0
    sentiment: float = 0.0
    active_platforms: List[str] = None
    platform_data: Dict[str, PlatformData] = None
    summary: str = ""
    trending_signals: List[str] = None

    def __post_init__(self):
        if self.active_platforms is None:
            self.active_platforms = []
        if self.platform_data is None:
            self.platform_data = {}
        if self.trending_signals is None:
            self.trending_signals = []


def _safe_float(val: Any, default: float = 0.0) -> float:
    """安全转换为float"""
    try:
        v = float(val)
        return max(-1.0, min(1.0, v))  # 限制在-1到1之间
    except (TypeError, ValueError):
        return default


def _get_weibo_sentiment(code: str, name: str) -> PlatformData:
    """获取微博情绪数据

    注意: 微博API需要认证，这里返回模拟数据或需要真实API
    """
    # TODO: 微博API需要认证，暂时返回基础数据
    # 实际实现需要微博开放平台API
    return PlatformData(
        platform="weibo",
        hot_score=0,
        sentiment=0.0,
        trending=False,
        posts_count=0,
        error="微博API需要认证"
    )


def _get_zhihu_sentiment(code: str, name: str) -> PlatformData:
    """获取知乎讨论数据

    注意: 知乎API需要认证，这里返回模拟数据或需要真实API
    """
    # TODO: 知乎API需要认证，暂时返回基础数据
    return PlatformData(
        platform="zhihu",
        hot_score=0,
        sentiment=0.0,
        trending=False,
        posts_count=0,
        error="知乎API需要认证"
    )


def _get_douyin_sentiment(code: str, name: str) -> PlatformData:
    """获取抖音热度数据

    注意: 抖音API需要认证，这里返回模拟数据或需要真实API
    """
    # TODO: 抖音API需要认证，暂时返回基础数据
    return PlatformData(
        platform="douyin",
        hot_score=0,
        sentiment=0.0,
        trending=False,
        posts_count=0,
        error="抖音API需要认证"
    )


def _get_toutiao_sentiment(code: str, name: str) -> PlatformData:
    """获取今日头条热度数据

    注意: 头条API可能需要认证，这里返回模拟数据或需要真实API
    """
    # TODO: 头条API需要认证，暂时返回基础数据
    return PlatformData(
        platform="toutiao",
        hot_score=0,
        sentiment=0.0,
        trending=False,
        posts_count=0,
        error="头条API需要认证"
    )


def _get_baidu_sentiment(code: str, name: str) -> PlatformData:
    """获取百度搜索指数数据

    百度指数API需要认证，暂时返回模拟数据
    """
    # TODO: 百度指数API需要认证，暂时返回基础数据
    return PlatformData(
        platform="baidu",
        hot_score=0,
        sentiment=0.0,
        trending=False,
        posts_count=0,
        error="百度指数API需要认证"
    )


def _get_bilibili_sentiment(code: str, name: str) -> PlatformData:
    """获取B站热度数据

    注意: B站API需要认证，这里返回模拟数据或需要真实API
    """
    # TODO: B站API需要认证，暂时返回基础数据
    return PlatformData(
        platform="bilibili",
        hot_score=0,
        sentiment=0.0,
        trending=False,
        posts_count=0,
        error="B站API需要认证"
    )


def get_social_sentiment(code: str, name: str, platforms: List[str] = None) -> SocialSentimentResult:
    """获取社交热榜聚合数据（同步版本）

    Args:
        code: 股票代码
        name: 股票名称
        platforms: 要查询的平台列表，None表示全部

    Returns:
        SocialSentimentResult: 社交情绪综合结果
    """
    if platforms is None:
        platforms = PLATFORMS

    result = SocialSentimentResult(code=code, name=name)
    platform_data = {}
    total_hot = 0
    sentiment_sum = 0.0
    sentiment_count = 0
    active_platforms = []

    # 获取各平台数据
    platform_functions = {
        "weibo": _get_weibo_sentiment,
        "zhihu": _get_zhihu_sentiment,
        "douyin": _get_douyin_sentiment,
        "toutiao": _get_toutiao_sentiment,
        "baidu": _get_baidu_sentiment,
        "bilibili": _get_bilibili_sentiment,
    }

    for platform in platforms:
        if platform in platform_functions:
            try:
                data = platform_functions[platform](code, name)
                platform_data[platform] = data

                if data.error == "" and data.hot_score > 0:
                    total_hot += data.hot_score
                    sentiment_sum += data.sentiment
                    sentiment_count += 1
                    active_platforms.append(platform)

                    if data.trending:
                        result.trending_signals.append(f"{platform}热门话题中")
            except Exception as e:
                platform_data[platform] = PlatformData(
                    platform=platform,
                    error=str(e)
                )

    result.platform_data = platform_data
    result.active_platforms = active_platforms
    result.total_hot = total_hot

    if sentiment_count > 0:
        result.sentiment = sentiment_sum / sentiment_count
    else:
        result.sentiment = 0.0

    # 生成摘要
    if active_platforms:
        result.summary = f"在{len(active_platforms)}个平台有热度讨论(总热度{total_hot})"
        if result.sentiment > 0.2:
            result.summary += "，情绪偏正面"
        elif result.sentiment < -0.2:
            result.summary += "，情绪偏负面"
        else:
            result.summary += "，情绪中性"
    else:
        result.summary = "各平台暂无可用数据"

    return result


async def get_social_sentiment_async(session, code: str, name: str,
                                      platforms: List[str] = None) -> SocialSentimentResult:
    """获取社交热榜聚合数据（异步版本）

    注意: 社交平台API多为同步且需要认证，此处使用同步版本包装
    """
    import asyncio
    return await asyncio.to_thread(get_social_sentiment, code, name, platforms)


def format_social_sentiment(result: SocialSentimentResult) -> str:
    """格式化社交情绪结果为可读字符串

    Args:
        result: 社交情绪结果

    Returns:
        格式化的字符串
    """
    lines = []
    lines.append("【社交热榜聚合】")

    if not result.active_platforms:
        lines.append(f"  ⚠️ {result.summary}")
        return "\n".join(lines)

    lines.append(f"  总热度: {result.total_hot}")
    lines.append(f"  情绪倾向: {'正面📈' if result.sentiment > 0.2 else ('负面📉' if result.sentiment < -0.2 else '中性➖')}")

    lines.append(f"\n  平台明细:")
    for platform, data in result.platform_data.items():
        emoji = "✅" if data.error == "" else "❌"
        hot_str = f"热度:{data.hot_score}" if data.error == "" else f"错误:{data.error}"
        sentiment_str = f"情绪:{data.sentiment:.2f}" if data.error == "" else ""
        trending_str = "🔥" if data.trending else ""
        lines.append(f"    {emoji} {platform:<10} {hot_str} {sentiment_str} {trending_str}")

    if result.trending_signals:
        lines.append(f"\n  🔥 热门信号:")
        for signal in result.trending_signals:
            lines.append(f"    - {signal}")

    lines.append("")
    return "\n".join(lines)


# 测试
if __name__ == "__main__":
    # 测试用例
    test_cases = [
        {"code": "600519", "name": "贵州茅台"},
        {"code": "300999", "name": "某股票"},
    ]

    print("=== 社交热榜聚合测试 ===\n")
    for tc in test_cases:
        result = get_social_sentiment(tc["code"], tc["name"])
        print(format_social_sentiment(result))
