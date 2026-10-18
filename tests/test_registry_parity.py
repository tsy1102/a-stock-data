from scripts import registry_parity


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
