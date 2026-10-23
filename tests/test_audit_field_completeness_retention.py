import pytest

from scripts import audit_field_completeness as audit


def _add_raw_capture(root, capture_date):
    folder = root / capture_date
    folder.mkdir()
    (folder / "raw_push2.json").write_text("{}", encoding="utf-8")


def test_latest_capture_date_ignores_pre_retention_samples(tmp_path):
    _add_raw_capture(tmp_path, "20261014")
    _add_raw_capture(tmp_path, "20261015")
    _add_raw_capture(tmp_path, "20261020")

    assert audit._latest_retained_capture_date(str(tmp_path)) == "20261020"


def test_explicit_pre_retention_audit_date_is_rejected():
    with pytest.raises(ValueError, match="早于采集数据保留起始日 20261015"):
        audit.main(["20261014"])
