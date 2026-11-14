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
    assert len(capture_catalog.EM_FULL_FIELDS.split(",")) == 250
    assert capture_catalog.EM_ULIST_RESEARCH_FIELDS == ("f297",)


def test_push2ex_pool_endpoints_are_individually_catalogued():
    expected = {
        "push2ex.limit_up_pool": ("getTopicZTPool", ("limit_up_pool",)),
        "push2ex.limit_down_pool": ("getTopicDTPool", ("limit_down_pool",)),
        "push2ex.limit_broken_pool": ("getTopicZBPool", ("limit_broken_pool",)),
        "push2ex.yesterday_limit_pool": ("getYesterdayZTPool", ("yesterday_limit_pool",)),
    }

    assert set(expected) <= set(capture_catalog.CAPTURE_UNIT_CATALOG)
    for unit_id, (endpoint, output_path) in expected.items():
        spec = capture_catalog.CAPTURE_UNIT_CATALOG[unit_id]
        assert spec["collector"] == "push2ex"
        assert spec["interface_id"].endswith(endpoint)
        assert spec["output_paths"] == [output_path]
    assert set(capture_catalog.SOURCE_REQUIRED_PATHS["push2ex"]) == {
        output_path for _, output_path in expected.values()
    }
