import pytest
from stock_common import (
    eastmoney_datacenter,
    get_reports,
    get_eastmoney_stock_news,
    get_holder_structure,
    get_northbound_hold,
    get_margin_trading,
    get_block_trade,
    get_lockup_expiry,
    get_industry_comparison,
    get_industry_peers,
    get_stock_sector_rank,
    get_gross_margin_and_roe,
    em_hot_concept,
    eastmoney_stock_info_push2
)

@pytest.mark.real_network
def test_eastmoney_datacenter():
    data = eastmoney_datacenter("600519", "RPT_DAILYBILLBOARD_DETAILSNEW",
                                columns="SECURITY_CODE,SECURITY_NAME_ABBR,TRADE_DATE",
                                page_size=5, sort_columns="TRADE_DATE", sort_types="-1")
    assert isinstance(data, list)

@pytest.mark.real_network
def test_get_reports():
    data = get_reports("600519", max_pages=1)
    assert isinstance(data, list)

@pytest.mark.real_network
def test_get_eastmoney_stock_news():
    data = get_eastmoney_stock_news("600519", page_size=5)
    assert isinstance(data, list)

@pytest.mark.real_network
def test_get_holder_structure():
    data = get_holder_structure("600519")
    assert isinstance(data, list)

@pytest.mark.real_network
def test_get_northbound_hold():
    data = get_northbound_hold("600519", days=2)
    assert isinstance(data, list)

@pytest.mark.real_network
def test_get_margin_trading():
    data = get_margin_trading("600519")
    assert isinstance(data, list)

@pytest.mark.real_network
def test_get_block_trade():
    data = get_block_trade("600519")
    assert isinstance(data, list)

@pytest.mark.real_network
def test_get_lockup_expiry():
    data = get_lockup_expiry("600519", days=90)
    assert isinstance(data, list)

@pytest.mark.real_network
def test_get_industry_comparison():
    data = get_industry_comparison(top_n=2)
    assert isinstance(data, dict)

@pytest.mark.real_network
def test_get_industry_peers():
    data = get_industry_peers("600519", top_n=2)
    assert isinstance(data, dict)

@pytest.mark.real_network
def test_get_stock_sector_rank():
    data = get_stock_sector_rank("600519")
    assert data is None or isinstance(data, dict)

@pytest.mark.real_network
def test_get_gross_margin_and_roe():
    data = get_gross_margin_and_roe("600519")
    assert data is None or isinstance(data, dict)

@pytest.mark.real_network
def test_em_hot_concept():
    data = em_hot_concept("600519")
    assert isinstance(data, list)

@pytest.mark.real_network
def test_eastmoney_push2():
    data = eastmoney_stock_info_push2("600519")
    assert isinstance(data, dict)
