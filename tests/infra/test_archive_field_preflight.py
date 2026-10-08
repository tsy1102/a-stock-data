"""Regression tests for source-map coverage after the field dictionary split."""

import importlib

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
