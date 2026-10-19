from scripts.audit_field_source_quality import audit_registry, render_report


def test_source_quality_audit_separates_semantic_and_canonical_issues():
    registry = {
        "meta": {"updated": "2026-10-18"},
        "source_fields": [
            {
                "source": "source-a",
                "code": "clear",
                "status": "verified",
                "meaning": "清晰含义",
                "attribute_conflicts": {"canonical": ["alias_a", "alias_b"]},
            },
            {
                "source": "source-a",
                "code": "missing",
                "status": "verified",
                "meaning": "待确认",
            },
            {
                "source": "source-b",
                "code": "conflict",
                "status": "verified",
                "meaning": "含义甲",
                "attribute_conflicts": {"meaning": ["含义甲", "含义乙"]},
            },
        ],
    }

    audit = audit_registry(registry)
    report = render_report(registry)

    assert audit["source_count"] == 2
    assert len(audit["flagged_verified"]) == 2
    assert len(audit["canonical_alias_variants"]) == 1
    assert "source-a" in report and "source-b" in report
    assert "规范名变体（不单独阻止锚）" in report
