from scripts.gen_zhb_subdict import (
    build_mirror,
    extract_main_contract,
    extract_subdict_contract,
)


def test_tipinfo_current_contract_replaces_retracted_history(tmp_path):
    mirror = build_mirror()
    mirror_path = tmp_path / "zhb_verify.md"
    mirror_path.write_text(mirror, encoding="utf-8")

    current = extract_main_contract()["tipinfo"]
    mirrored = extract_subdict_contract(str(mirror_path))["tipinfo"]

    assert current == mirrored
    assert "tipinfo.shareholder_change_date" in current
    assert "tipinfo.shareholder_change_shares_wan" in current
    assert "tipinfo.div_date" not in current
    assert "tipinfo.div_amount" not in current
    assert "div_date" not in mirror
    assert "div_amount" not in mirror
