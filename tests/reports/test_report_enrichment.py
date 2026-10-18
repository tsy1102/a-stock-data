from types import SimpleNamespace

import pytest

from stock_common.enrich_helpers import (
    cash_content_lines,
    earnings_quality_lines,
    fuyao_report_period_candidates,
    tdx_snapshot_period_context,
)


@pytest.mark.parametrize(
    ("report_period", "expected"),
    [
        ("20260630", ["2026-2", "2026-1"]),
        ("2026-09-30", ["2026-3", "2026-2"]),
        ("2025-12-31", ["2025-4", "2025-3"]),
        ("20260331", ["2026-1", "2025-4"]),
    ],
)
def test_fuyao_period_candidates_follow_latest_report_date(report_period, expected):
    assert fuyao_report_period_candidates(report_period) == expected


@pytest.mark.parametrize("report_period", ["", "20261015", "not-a-date", None])
def test_fuyao_period_candidates_reject_missing_or_nonquarter_dates(report_period):
    assert fuyao_report_period_candidates(report_period) == []


def test_tdx_snapshot_context_does_not_claim_canonical_period_is_tdx_confirmed():
    assert tdx_snapshot_period_context("20260630", "20260830") == (
        "统一层参考报告期 2026-06-30（TDX 未独立确认期别），TDX 披露日 20260830"
    )
    assert tdx_snapshot_period_context("bad-date") == "TDX 快照报告期未由接口字段确认"


def test_cash_content_does_not_divide_ttm_cash_flow_by_report_period_profit():
    cdata = SimpleNamespace(
        report_period="20260630",
        ocf_ttm=60.05 * 1e8,
        net_profit=42.22 * 1e8,
    )

    text = "\n".join(cash_content_lines(cdata))

    assert "经营现金流净额(TTM)=60.05亿" in text
    assert "净利润(报告期 2026-06-30)=42.22亿" in text
    assert "期间不同，不计算现金含量比" in text
    assert "→ 比值" not in text
    assert "真金白银" not in text


def test_earnings_quality_does_not_infer_from_missing_or_mismatched_periods():
    cdata = SimpleNamespace(
        report_period="20260630",
        eps=0,
        eps_deduct_ttm=0,
        roe=9.92,
        roe_deduct_ttm=12.12,
    )

    text = "\n".join(earnings_quality_lines(cdata))

    assert "归母EPS(统一层字段)未取到" in text
    assert "扣非EPS(TTM)未取到" in text
    assert "ROE(报告期 2026-06-30)=9.9%" in text
    assert "扣非ROE(TTM)=12.1%" in text
    assert "不以差额推断非经常性损益影响" in text
