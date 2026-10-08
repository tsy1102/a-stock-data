from scripts.gen_field_dict import render_field_metadata_gaps, render_source_repository_map


def test_metadata_gap_report_lists_only_verified_missing_descriptions():
    registry = {
        "source_fields": [
            {
                "source": "source-a",
                "code": "verified.missing",
                "status": "verified",
                "canonical": "",
                "meaning": "",
                "unit": "",
                "sections": ["evidence-a.md"],
            },
            {
                "source": "source-b",
                "code": "verified.meaning",
                "status": "verified",
                "canonical": "canonical-b",
                "meaning": "meaning-b",
            },
            {
                "source": "source-c",
                "code": "unknown.missing",
                "status": "unverified",
                "canonical": "",
                "meaning": "",
            },
        ]
    }

    rendered = render_field_metadata_gaps(registry)

    assert "缺口记录 1 条；缺少含义 1 条；缺少规范名 1 条。" in rendered
    assert "source-a" in rendered and "verified.missing" in rendered
    assert "source-c" not in rendered
    assert "不改变字段状态或锚点资格" in rendered


def test_source_map_displays_project_evidence_separately_from_dialog_confirmation():
    registry = {"sources": [{"name": "source-a"}]}
    lineage = {
        "sources": {
            "source-a": {
                "runtime_aliases": ["runtime-a"],
                "provider": "provider-a",
                "independence_family": "family-a",
                "independence_status": "confirmed",
                "anchor_eligible": True,
                "anchor_note": "source note",
                "repository_mapping_status": "confirmed",
                "dialog_confirmation": {
                    "status": "confirmed",
                    "confirmed_on": "2026-10-06",
                    "note": "user-confirmed scope",
                },
                "repositories": [
                    {
                        "url": "https://github.com/example/repo",
                        "relation": "runtime client",
                        "status": "confirmed",
                        "evidence_files": ["requirements.txt"],
                        "note": "project evidence",
                    }
                ],
            }
        }
    }

    rendered = render_source_repository_map(registry, lineage)

    assert "项目证据 | 对话确认" in rendered
    assert "confirmed | confirmed（2026-10-06）" in rendered
    assert "user-confirmed scope" in rendered
    assert "runtime client" in rendered
