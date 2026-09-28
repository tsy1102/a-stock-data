from pathlib import Path
from runpy import run_path


def test_ulist_count_excludes_reserved_index_placeholder():
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "gen_ulist_subdict.py"
    extract_main_ulist_details = run_path(str(script_path))["extract_main_ulist_details"]
    documented_fields, placeholders = extract_main_ulist_details()

    assert placeholders == {93}
    assert len(documented_fields) == 240
    assert len(documented_fields - placeholders) == 239
