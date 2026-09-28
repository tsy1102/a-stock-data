# tests/test_seat_db_audit_fix.py
# 审计(2026-09-01) P1-6 修复回归: 龙虎榜席位全部未匹配到已知游资库时,
# 席位质量评分应降级为 None / premium_signal="unknown", 不再恒输出伪精确的 50 分 + neutral。
import pytest

from stock_common import seat_db


def _fake_info(tier="unknown", short_name="", premium="未知"):
    return {
        "tier": tier,
        "short_name": short_name,
        "style": "未知",
        "traits": [],
        "premium": premium,
        "winning_rate": "未知",
    }


def test_seat_score_degraded_when_no_known_seat(monkeypatch):
    """全部席位都未匹配到已知游资库 → 评分 None / 信号 unknown"""
    monkeypatch.setattr(seat_db, "get_seat_info", lambda name: _fake_info())
    res = seat_db.enhance_lhb_seats(
        {
            "seats": {
                "buy": [{"name": "某券商营业部A"}, {"name": "某券商营业部B"}],
                "sell": [{"name": "某券商营业部C"}],
            }
        }
    )
    assert res["seat_quality_score"] is None
    assert res["premium_signal"] == "unknown"


def test_seat_score_normal_with_legend(monkeypatch):
    """存在 legend 席位 → 正常评分(>=50) 且非 unknown"""

    def fake(name):
        if "传奇" in name:
            return _fake_info(tier="legend", short_name="传奇", premium="正面")
        return _fake_info()

    monkeypatch.setattr(seat_db, "get_seat_info", fake)
    res = seat_db.enhance_lhb_seats(
        {
            "seats": {
                "buy": [{"name": "传奇席位"}],
                "sell": [{"name": "某券商营业部C"}],
            }
        }
    )
    assert res["seat_quality_score"] is not None
    assert res["seat_quality_score"] >= 50
    assert res["premium_signal"] != "unknown"
