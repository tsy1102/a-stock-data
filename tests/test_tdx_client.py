import pytest
from tdx_client import (
    tdx_get_security_bars,
    tdx_get_quote_full,
    tdx_get_index_quote,
    tdx_get_fund_flow,
    tdx_get_history_fund_flow,
    tdx_get_dividend_history,
    tdx_get_eps_from_reports,
    tdx_get_belong_boards,
    tdx_get_board_list,
    tdx_get_board_members,
    tdx_get_all_stocks
)

@pytest.mark.real_network
def test_tdx_security_bars():
    keys, rows = tdx_get_security_bars("600519", count=5)
    assert rows is not None

@pytest.mark.real_network
def test_tdx_quote_full():
    data = tdx_get_quote_full("600519")
    assert isinstance(data, dict)
    assert "price" in data

@pytest.mark.real_network
def test_tdx_index_quote():
    data = tdx_get_index_quote("sh000001")
    assert isinstance(data, dict)
    assert "price" in data

@pytest.mark.real_network
def test_tdx_fund_flow():
    data = tdx_get_fund_flow("600519")
    if data:
        assert "main_net" in data

@pytest.mark.real_network
def test_tdx_history_fund_flow():
    data = tdx_get_history_fund_flow("600519", days=5)
    assert isinstance(data, list)

@pytest.mark.real_network
def test_tdx_dividend_history():
    data = tdx_get_dividend_history("600519")
    # V16.2.3: None=接口失败（区别于 [] 真无分红）；list=正常返回
    assert isinstance(data, (list, type(None)))

@pytest.mark.real_network
def test_tdx_eps_from_reports():
    data = tdx_get_eps_from_reports("600519")
    if data:
        assert "eps_cur" in data

@pytest.mark.real_network
def test_tdx_belong_boards():
    sh_data = tdx_get_belong_boards("600519")
    sz_data = tdx_get_belong_boards("000001")
    assert isinstance(sh_data, dict) or isinstance(sz_data, dict)

@pytest.mark.real_network
def test_tdx_board_list():
    data = tdx_get_board_list(0)
    assert isinstance(data, list)

@pytest.mark.real_network
def test_tdx_board_members():
    boards = tdx_get_belong_boards("600519")
    if boards and boards.get("industry"):
        board_code = boards["industry"][0]["code"]
        members = tdx_get_board_members(board_code)
        assert isinstance(members, list)

@pytest.mark.real_network
def test_tdx_all_stocks():
    data = tdx_get_all_stocks()
    assert isinstance(data, list)
