from stock_common.sc_datasource import _industry


class _Response:
    def json(self):
        return {
            "data": {
                "diff": [
                    {
                        "f2": 12.34,
                        "f3": 1.25,
                        "f12": "BK0001",
                        "f14": "示例行业",
                        "f104": 10,
                        "f105": 2,
                        "f128": "示例公司",
                        "f136": 3.5,
                        "f140": "600000",
                    }
                ]
            }
        }


def test_eastmoney_board_adapters_use_leader_name_and_change(monkeypatch):
    monkeypatch.setattr(_industry, "em_get", lambda *args, **kwargs: _Response())

    board = _industry.get_em_board_list(0)[0]
    sectors = _industry._get_eastmoney_industry_sectors()

    assert board["leader_name"] == "示例公司"
    assert board["leader_change"] == 3.5
    assert sectors[0]["leader"] == "示例公司"
    assert sectors[0]["leader_change"] == 3.5
