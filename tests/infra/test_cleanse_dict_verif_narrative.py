import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "cleanse_dict_verif_narrative.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("cleanse_dict_verif_narrative", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sample_dictionary() -> str:
    return "| 字段 | 状态 | 含义 |\n| --- | --- | --- |\n| f2 | ✅ 跨源精确吻合 | ✅ **东财网页CDP对撞**：ulist f2 ↔ `最新价` |\n"


def test_dry_run_does_not_write_without_explicit_plan_path(tmp_path, monkeypatch, capsys):
    module = _load_script()
    source = tmp_path / "field_source_reference.md"
    provenance = tmp_path / "PROVENANCE.md"
    source.write_text(_sample_dictionary(), encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "SRC", source)
    monkeypatch.setattr(module, "PROV", provenance)
    monkeypatch.setattr(sys, "argv", [str(SCRIPT_PATH)])

    module.main()

    assert source.read_text(encoding="utf-8") == _sample_dictionary()
    assert not provenance.exists()
    assert not (tmp_path / "docs" / "field_verification" / "SECOND_PASS_PLAN.md").exists()
    assert "no files changed" in capsys.readouterr().out


def test_dry_run_writes_only_to_explicit_plan_path(tmp_path, monkeypatch):
    module = _load_script()
    source = tmp_path / "field_source_reference.md"
    provenance = tmp_path / "PROVENANCE.md"
    plan = Path("plan.md")
    source.write_text(_sample_dictionary(), encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "SRC", source)
    monkeypatch.setattr(module, "PROV", provenance)
    monkeypatch.setattr(sys, "argv", [str(SCRIPT_PATH), "--plan-output", str(plan)])

    module.main()

    assert (tmp_path / plan).is_file()
    assert source.read_text(encoding="utf-8") == _sample_dictionary()
    assert not provenance.exists()


def test_apply_requires_a_separate_output_file(tmp_path, monkeypatch):
    module = _load_script()
    source = tmp_path / "field_source_reference.md"
    provenance = tmp_path / "PROVENANCE.md"
    source.write_text(_sample_dictionary(), encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "SRC", source)
    monkeypatch.setattr(module, "PROV", provenance)
    monkeypatch.setattr(sys, "argv", [str(SCRIPT_PATH), "--apply"])

    try:
        module.main()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("--apply without --output must be rejected")

    assert source.read_text(encoding="utf-8") == _sample_dictionary()
    assert not provenance.exists()


def test_apply_writes_only_to_explicit_output(tmp_path, monkeypatch):
    module = _load_script()
    source = tmp_path / "field_source_reference.md"
    output = tmp_path / "cleaned_copy.md"
    provenance = tmp_path / "PROVENANCE.md"
    source.write_text(_sample_dictionary(), encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "SRC", source)
    monkeypatch.setattr(module, "PROV", provenance)
    monkeypatch.setattr(sys, "argv", [str(SCRIPT_PATH), "--apply", "--output", str(output)])

    module.main()

    assert source.read_text(encoding="utf-8") == _sample_dictionary()
    assert output.is_file()
