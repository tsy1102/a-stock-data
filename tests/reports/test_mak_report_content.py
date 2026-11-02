import get_mak_report


def test_unqueried_limit_pool_source_is_not_reported_as_failed():
    source_text, status = get_mak_report._format_limit_pool_source_summary(
        {"cls": 47, "kpl": 47, "fupan": 47, "push2ex": None},
        47,
        unqueried_sources=["push2ex"],
    )

    assert "push2ex=未查询" in source_text
    assert "可用来源全数一致（3/3）" in status
    assert "失败" not in status


def test_missing_main_net_summary_explains_shared_cooldown():
    lines = get_mak_report._main_flow_summary_lines(
        {}, 3159, 0, source_status="shared_cooldown"
    )

    assert any("push2delay 共享风控冷却中" in line for line in lines)
    assert any("不代表零净流" in line for line in lines)
