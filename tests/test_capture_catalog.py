from scripts import capture_catalog
from scripts.capture_field_probe import build_collectors


def test_capture_catalog_covers_every_registered_collector_and_contract():
    collector_names = set(build_collectors())

    assert collector_names == set(capture_catalog.SOURCE_SCHEME)
    assert capture_catalog.FULL_POOL_STOCK_SOURCES <= collector_names
    assert set(capture_catalog.SOURCE_REQUIRED_PATHS) <= collector_names
    assert set(capture_catalog.NON_RAW_SOURCE_STATUS) <= collector_names


def test_capture_catalog_keeps_eastmoney_field_schemes_distinct():
    assert capture_catalog.SOURCE_SCHEME["push2"] == "em.stock_get"
    assert capture_catalog.SOURCE_SCHEME["em_fund_flow"] == "em.stock_get"
    assert capture_catalog.SOURCE_SCHEME["ulist239"] == "em.ulist_np"
    assert capture_catalog.EM_FULL_FIELDS.split(",")[0] == "f1"
    assert capture_catalog.EM_FULL_FIELDS.split(",")[-1] == "f250"
