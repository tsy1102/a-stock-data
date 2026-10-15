import get_mak_report


def test_star_market_stocks_use_the_star_composite_index():
    assert get_mak_report.get_stock_index("688981") == "sh000680"
    assert get_mak_report.INDEX_MAP["sh000680"] == "科创综指"
