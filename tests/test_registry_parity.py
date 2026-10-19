from pathlib import Path

from scripts import registry_parity


def test_strict_parity_count_target_keeps_missing_pairs_visible():
    expected = {("source-a", "field-a"), ("source-b", "field-b")}
    missing = {("source-a", "field-a")}

    assert registry_parity._pairs_for_count_check(expected, missing, None) == expected
    assert registry_parity._pairs_for_count_check(expected, missing, missing) == expected - missing


def test_native_parity_remains_strict_without_accepted_debt():
    expected = {("source-a", "field-a"), ("source-b", "field-b")}
    actual = {("source-b", "field-b")}

    missing, extra, problems, warnings = registry_parity._native_pair_problems(expected, actual)

    assert missing == {("source-a", "field-a")}
    assert extra == set()
    assert any("registry 缺 1" in problem for problem in problems)
    assert warnings == []


def test_native_parity_accepts_declared_missing_pairs():
    expected = {("source-a", "field-a"), ("source-b", "field-b")}
    actual = {("source-b", "field-b")}
    accepted = {("source-a", "field-a")}

    missing, extra, problems, warnings = registry_parity._native_pair_problems(
        expected, actual, accepted
    )

    assert missing == accepted
    assert extra == set()
    assert problems == []
    assert warnings == []


def test_native_parity_allows_a_shrinking_accepted_delta_with_warning():
    expected = {("source-a", "field-a"), ("source-b", "field-b")}
    actual = expected
    accepted = {("source-a", "field-a"), ("source-b", "field-b")}

    missing, extra, problems, warnings = registry_parity._native_pair_problems(
        expected, actual, accepted
    )

    assert missing == set()
    assert extra == set()
    assert problems == []
    assert any("已补齐" in warning for warning in warnings)


def test_native_parity_rejects_an_unlisted_new_missing_pair():
    expected = {
        ("source-a", "field-a"),
        ("source-b", "field-b"),
        ("source-c", "field-c"),
    }
    actual = {("source-b", "field-b")}
    accepted = {("source-a", "field-a")}

    _, _, problems, _ = registry_parity._native_pair_problems(expected, actual, accepted)

    assert any("未登记的新缺失配对" in problem for problem in problems)


def test_native_parity_warns_when_resolved_debt_remains_in_manifest():
    expected = {("source-a", "field-a"), ("source-b", "field-b")}
    actual = expected
    accepted = {("source-a", "field-a")}

    _, _, problems, warnings = registry_parity._native_pair_problems(expected, actual, accepted)

    assert problems == []
    assert any("已补齐" in warning for warning in warnings)


def test_native_parity_rejects_a_manifest_pair_removed_from_the_baseline():
    expected = {("source-b", "field-b")}
    actual = expected
    accepted = {("source-a", "field-a")}

    _, _, problems, _ = registry_parity._native_pair_problems(expected, actual, accepted)

    assert any("不再属于基线" in problem for problem in problems)


def test_native_parity_never_accepts_extra_registry_pairs():
    expected = {("source-a", "field-a"), ("source-b", "field-b")}
    actual = {("source-b", "field-b"), ("source-c", "field-c")}
    accepted = {("source-a", "field-a")}

    _, extra, problems, _ = registry_parity._native_pair_problems(expected, actual, accepted)

    assert extra == {("source-c", "field-c")}
    assert any("registry 多出" in problem for problem in problems)


def test_accepted_debt_manifest_rejects_duplicate_pairs():
    manifest = {
        "schema_version": 1,
        "debt_id": "DEBT-020",
        "reason": "pending cross-check",
        "review_trigger": "cross-check complete",
        "accepted_missing_pairs": [
            {"source": "source-a", "code": "field-a"},
            {"source": "source-a", "code": "field-a"},
        ],
    }

    pairs, problems = registry_parity._validate_accepted_debt_manifest(manifest)

    assert pairs is None
    assert any("重复配对" in problem for problem in problems)


def test_scope_manifest_accepts_archive_only_and_captured_context_entries():
    manifest = {
        "schema_version": 1,
        "purpose": "Test source-scope distinctions.",
        "entries": [
            {
                "source": "source-a",
                "code": "archived-field",
                "disposition": "archive_only",
                "reason": "Archived protocol is outside runtime scope.",
                "evidence_files": ["docs/example.md"],
                "capture_path": None,
            },
            {
                "source": "source-b",
                "code": "context-tags",
                "disposition": "captured_context",
                "reason": "Kept in raw context but excluded from cracking registry.",
                "evidence_files": ["docs/example.md"],
                "capture_path": "raw.json:market.items[*].tags",
            },
        ],
    }

    entries, problems = registry_parity._validate_scope_manifest(manifest)

    assert problems == []
    assert entries is not None
    assert set(entries) == {("source-a", "archived-field"), ("source-b", "context-tags")}


def test_scope_manifest_rejects_duplicate_pairs_and_invalid_runtime_contract():
    entry = {
        "source": "source-a",
        "code": "field-a",
        "disposition": "archive_only",
        "reason": "Explicitly archival.",
        "evidence_files": ["docs/example.md"],
        "capture_path": None,
    }
    manifest = {
        "schema_version": 1,
        "purpose": "Test duplicate checking.",
        "entries": [entry, dict(entry)],
    }

    entries, problems = registry_parity._validate_scope_manifest(manifest)

    assert entries is None
    assert any("重复配对" in problem for problem in problems)

    invalid_context = dict(entry, disposition="captured_context")
    entries, problems = registry_parity._validate_scope_manifest(
        {"schema_version": 1, "purpose": "Test path requirement.", "entries": [invalid_context]}
    )

    assert entries is None
    assert any("必须声明 capture_path" in problem for problem in problems)


def test_repository_scope_manifest_matches_only_the_five_reviewed_baseline_pairs():
    entries, problems = registry_parity._load_scope_manifest(registry_parity.SCOPE_MANIFEST)

    assert problems == []
    assert entries is not None
    expected = {
        ("TDX(双命名源)", "Buyp"),
        ("TDX(双命名源)", "Buyv"),
        ("TDX(双命名源)", "Sellp"),
        ("TDX(双命名源)", "Sellv"),
        ("同花顺-fuyao", "tags"),
    }
    assert set(entries) == expected

    base = registry_parity.afc.registered_field_sets()
    baseline_pairs = {(source, code) for source, codes in base.items() for code in codes}
    assert set(entries) <= baseline_pairs

    with open(registry_parity.REGISTRY, encoding="utf-8") as handle:
        registry = registry_parity.json.load(handle)
    current_pairs = {
        (record["source"], record["code"])
        for record in registry_parity.fra.source_field_records(registry)
    }
    assert set(entries).isdisjoint(current_pairs)
    for code in ("Buyp", "Buyv", "Sellp", "Sellv"):
        assert entries[("TDX(双命名源)", code)]["disposition"] == "captured_runtime"
    assert entries[("同花顺-fuyao", "tags")]["disposition"] == "captured_context"
    assert entries[("同花顺-fuyao", "tags")]["capture_path"] == (
        "raw_fuyao.json:market.short_term_benchmark[*].tags"
    )


def test_reconciled_capture_pairs_stay_unverified_and_traceable():
    registry = registry_parity.fra.load_registry()
    captured = [row for row in registry["source_fields"] if "capture_evidence" in row]

    assert len(captured) == 35
    for row in captured:
        assert row["status"] == "unverified"
        assert not row["canonical"]
        assert not row["meaning"]
        assert not row["unit"]
        assert row["capture_evidence"]
        for evidence in row["capture_evidence"]:
            assert set(evidence) == {"file", "path"}
            assert (Path(registry_parity.REPO_ROOT) / evidence["file"]).is_file()
