import pytest
from zhb_client import (
    get_zhb, invalidate_cache, list_sp_blocks, get_sp_block,
    get_sw_industries, get_industry_map, market_stat_snapshot,
    get_stock_stat, get_stock_stat2, get_high_52w, get_low_52w,
    get_industry_code, is_data_fresh, get_tip_info, get_ipo_list,
    get_ah_stocks, get_broker_name, get_holidays, get_csrc_industries,
    get_adr_stocks, get_convertible_bonds, get_delisted_stocks
)
from stock_common.sc_datasource import (
    get_zhb_sp_block, get_zhb_sp_block_list, get_zhb_sw_industries,
    get_zhb_industry_map, get_zhb_data_date, is_zhb_data_fresh,
    get_zhb_holidays, get_zhb_csrc_industries, get_zhb_adr_stocks,
    get_zhb_convertible_bonds, get_zhb_delisted_stocks
)

def test_zhb_client_download():
    invalidate_cache()
    zhb = get_zhb()
    assert zhb is not None
    assert len(zhb.raw_files) > 0

def test_zhb_spblock():
    blocks = list_sp_blocks()
    assert len(blocks) > 0
    codes = get_sp_block("中证2000")
    if codes is not None:
        assert isinstance(codes, list)

def test_zhb_sw_industries():
    sw = get_sw_industries()
    assert len(sw) > 0

def test_zhb_industry_map():
    ind_map = get_industry_map()
    assert len(ind_map) > 0

def test_zhb_sc_datasource_integration():
    blocks = get_zhb_sp_block_list()
    assert isinstance(blocks, list)
    sw = get_zhb_sw_industries()
    assert isinstance(sw, dict)

def test_zhb_tdxstat_snapshot():
    snapshot = market_stat_snapshot()
    assert len(snapshot) > 0
    stat = get_stock_stat("600519")
    if stat:
        assert "change_pct" in stat

def test_zhb_tdxstat2():
    s2 = get_stock_stat2("600519")
    if s2:
        high = get_high_52w("600519")
        low = get_low_52w("600519")
        assert high is not None and low is not None

def test_zhb_freshness():
    assert is_data_fresh(30) in (True, False)
    assert is_zhb_data_fresh(30) in (True, False)

def test_zhb_tipinfo():
    zhb = get_zhb()
    if zhb and len(zhb.tip_info) > 0:
        tip = get_tip_info("600519")
        assert isinstance(tip, dict) or tip is None

def test_zhb_ipo_list():
    ipo_list = get_ipo_list()
    assert isinstance(ipo_list, list)

def test_zhb_ah_and_brokers():
    ah = get_ah_stocks()
    assert isinstance(ah, list)
    name = get_broker_name("1")
    assert isinstance(name, str)

def test_zhb_holidays():
    holidays = get_holidays()
    assert isinstance(holidays, list)

def test_zhb_csrc_industries():
    csrc = get_csrc_industries()
    assert isinstance(csrc, dict)

def test_zhb_adr_bonds_delisted():
    adr = get_adr_stocks()
    assert isinstance(adr, list)
    bonds = get_convertible_bonds()
    assert isinstance(bonds, list)
    delisted = get_delisted_stocks()
    assert isinstance(delisted, dict)
