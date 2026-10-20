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


def test_routine_collision_suppression_excludes_retired_ftshare_service():
    snapshot = SimpleNamespace(source="ftshare", folder="20261019")
    diagnostics = []
    store = defaultdict(lambda: {"vals": {}, "scheme": None, "src": None, "sample_meta": {}})

    count = collide.load_snapshots(
        [snapshot],
        store,
        diagnostics,
        excluded_sources={
            "ftshare": {
                "interface_id": "FTShare private hosted MCP",
                "status": "retired",
            }
        },
    )

    assert count == 0
    assert not store
    assert any("FTShare private hosted MCP" in item for item in diagnostics)
