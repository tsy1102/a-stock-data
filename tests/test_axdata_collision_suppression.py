from collections import defaultdict
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace


COLLIDE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "collide.py"
SPEC = spec_from_file_location("axdata_collision_suppression_test_module", COLLIDE_PATH)
assert SPEC is not None and SPEC.loader is not None
collide = module_from_spec(SPEC)
SPEC.loader.exec_module(collide)


def test_routine_collision_suppression_excludes_confirmed_axdata_source():
    snapshot = SimpleNamespace(source="axdata", folder="20261009")
    diagnostics = []
    store = defaultdict(lambda: {"vals": {}, "scheme": None, "src": None, "sample_meta": {}})

    count = collide.load_snapshots(
        [snapshot],
        store,
        diagnostics,
        excluded_sources={
            "axdata": {
                "interface_id": "stock_shortline_indicators_tdx",
                "status": "operationally_redundant",
            }
        },
    )

    assert count == 0
    assert not store
    assert any("stock_shortline_indicators_tdx" in item for item in diagnostics)


def test_ftshare_suppression_removes_only_confirmed_endpoint_fields():
    document = {
        "stocks": {
            "000001": {
                "comment_score": [1, 2, 3],
                "comment_desire": 4.5,
                "unconfirmed_candidate": 99,
            }
        },
        "market": {"unlock_by_date": [{"amount": 5}]},
    }

    filtered, removed = collide._without_identity_fields(document, {"comment_score"})

    assert removed == 1
    assert "comment_score" not in filtered["stocks"]["000001"]
    assert filtered["stocks"]["000001"]["comment_desire"] == 4.5
    assert filtered["stocks"]["000001"]["unconfirmed_candidate"] == 99
    assert filtered["market"] == document["market"]
    assert "comment_score" in document["stocks"]["000001"]
