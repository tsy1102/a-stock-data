from __future__ import annotations

from scripts import collide


def _field(source: str) -> dict:
    values = {}
    sample_meta = {}
    for day in ("20261016", "20261019", "20261020"):
        for index in range(20):
            key = (f"{index:06d}", day)
            values[key] = float(index + 1)
            sample_meta[key] = {"phase": "closed"}
    return {
        "src": source,
        "type": "num",
        "is_identifier": False,
        "is_constant": False,
        "vals": values,
        "sample_meta": sample_meta,
    }


def test_ftshare_rest_suffix_is_normalized_for_stock_join():
    assert collide._record_code({"symbol": "600000.SH"}, "600000", "ftshare_rest") == "600000"
    assert collide._record_code({"symbol": "000001.XSHE"}, "000001", "ftshare_rest") == "000001"


def test_official_contract_anchor_emits_distinct_l1c_level():
    left = _field("tdx")
    right = _field("ftshare_rest")

    result = collide.collide_pair(left, right, contract_anchor=True)

    assert result is not None
    assert result["level"] == "L1-C"
    assert result["statistical_level"] == "L1"
    assert result["anchor_basis"] == "official_contract"
    assert result["source_independence_confirmed"] is False


def test_unconfirmed_ftshare_rest_is_not_an_independent_l1_source():
    result = collide.collide_pair(_field("tdx"), _field("ftshare_rest"))
    assert result is None
