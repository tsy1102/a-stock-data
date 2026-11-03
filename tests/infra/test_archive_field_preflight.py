"""Regression tests for source-map coverage after the field dictionary split."""

import importlib
import builtins

import pytest


@pytest.mark.parametrize(
    ("link_reference", "expected_orphans"),
    [
        (True, []),
        (False, [("source", "source_verify.md")]),
    ],
)
def test_mapping_reference_must_be_linked_from_main_entrypoint(
    tmp_path, monkeypatch, link_reference, expected_orphans
):
    monkeypatch.syspath_prepend("scripts")
    preflight = importlib.import_module("archive_field_preflight")
    docs = tmp_path / "docs"
    verify = docs / "verify"
    verify.mkdir(parents=True)
    (verify / "source_verify.md").write_text("# Source mirror\n", encoding="utf-8")

    field_dict = docs / "field_dict.md"
    main_text = "# Field dictionary\n"
    if link_reference:
        main_text += "[Historical source reference](field_source_reference.md)\n"
    field_dict.write_text(main_text, encoding="utf-8")
    (docs / "field_source_reference.md").write_text(
        "<!-- MAPPING: source -> source_verify.md -->\n", encoding="utf-8"
    )

    monkeypatch.setattr(preflight, "DOCS_DIR", str(docs))
    monkeypatch.setattr(preflight, "FIELD_DICT", str(field_dict))
    monkeypatch.setattr(preflight, "VERIFY_DIR", str(verify))
    monkeypatch.setattr(preflight, "_load_verify_mapping", lambda: {"source": "source_verify.md"})

    missing, orphan = preflight._check_mapping_coverage()

    assert missing == []
    assert orphan == expected_orphans


def test_section_map_accepts_markdown_code_formatted_source_title(monkeypatch):
    monkeypatch.syspath_prepend("scripts")
    preflight = importlib.import_module("archive_field_preflight")
    monkeypatch.setattr(
        preflight,
        "_load_section_map",
        lambda: [("TDX(双命名源)", ["TCP GetFinanceInfo"])],
    )

    corpus = [("field_source_reference.md", "## 二、 TCP `GetFinanceInfo` (0x0010)")]

    assert preflight._check_section_map(corpus) == []


@pytest.mark.parametrize(
    ("module_name", "loader_name"),
    [
        ("audit_field_completeness", "_load_section_map"),
        ("verify_sync_check", "_load_verify_mapping"),
    ],
)
def test_authoritative_mapping_import_failure_does_not_fall_back_to_empty(
    monkeypatch, module_name, loader_name
):
    monkeypatch.syspath_prepend("scripts")
    preflight = importlib.import_module("archive_field_preflight")
    original_import = builtins.__import__

    def fail_authority(name, *args, **kwargs):
        if name == module_name:
            raise ImportError("injected authoritative import failure")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_authority)

    with pytest.raises(preflight.PreflightInputError, match="无法加载权威"):
        getattr(preflight, loader_name)()


def test_docs_corpus_read_failure_aborts_preflight(monkeypatch, tmp_path):
    preflight = importlib.import_module("archive_field_preflight")
    docs = tmp_path / "docs"
    docs.mkdir()
    markdown = docs / "unreadable.md"
    markdown.write_text("# Required evidence\n", encoding="utf-8")
    monkeypatch.setattr(preflight, "DOCS_DIR", str(docs))

    def fail_read(_path):
        raise PermissionError("injected unreadable document")

    monkeypatch.setattr(preflight, "io_open", fail_read)

    with pytest.raises(preflight.PreflightInputError, match="unreadable.md"):
        preflight._collect_docs_corpus()


def test_missing_docs_directory_fails_preflight(monkeypatch, tmp_path, capsys):
    preflight = importlib.import_module("archive_field_preflight")
    monkeypatch.setattr(preflight, "DOCS_DIR", preflight.DOCS_DIR)
    monkeypatch.setattr(preflight, "FIELD_DICT", preflight.FIELD_DICT)
    monkeypatch.setattr(preflight, "VERIFY_DIR", preflight.VERIFY_DIR)

    result = preflight.main(["--repo", str(tmp_path)])

    assert result == 1
    assert "docs 目录不存在" in capsys.readouterr().err
