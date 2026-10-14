from scripts.gen_field_dict import (
    render_field_aggregate_review,
    render_field_dict,
    render_field_metadata_gaps,
    render_source_repository_map,
)


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


def test_field_dictionary_distinguishes_sources_from_framework_and_historical_references():
    registry = {
        "source_fields": [
            {
                "source": "FTShare",
                "code": "comment_score",
                "status": "verified",
                "canonical": "comment_score",
                "meaning": "comment sentiment score",
            }
        ],
        "sources": [
            {
                "name": "AxData",
                "source_role": "framework_reference",
                "verify_file": "axdata_verify.md",
                "section_patterns": ["interface inventory"],
            },
            {
                "name": "FTShare",
                "source_role": "service_endpoint",
                "verify_file": "ftshare_fields_mirror.md",
                "section_patterns": ["FTShare MCP fields"],
            },
            {
                "name": "Levistock历史未归属",
                "source_role": "historical_unattributed",
                "verify_file": "levistock_field_verify.md",
                "section_patterns": ["historical evidence"],
            },
        ],
    }

    rendered = render_field_dict(registry)

    assert "来源身份与框架参考索引" in rendered
    assert "AxData | 多源框架参考（非独立来源）" in rendered
    assert "FTShare | 服务接口（底层来源族未确认）" in rendered
    assert "Levistock历史未归属 | 历史未归属（不作来源锚）" in rendered
    assert "AxData 是多提供方接口框架" in rendered
    assert "field_aggregate_review.md" in rendered


def test_aggregate_review_lists_source_scoped_meanings_without_splitting_them():
    source_fields = [
        {
            "source": "eastmoney.stock_get",
            "code": "f44",
            "canonical": "high_price",
            "meaning": "最高价",
            "unit": "元",
            "status": "verified",
        },
        {
            "source": "eastmoney.ulist_np",
            "code": "f44",
            "canonical": "total_profit",
            "meaning": "利润总额",
            "unit": "元",
            "status": "verified",
        },
        {
            "source": "source-c",
            "code": "metric.composite",
            "canonical": "metric.value",
            "meaning": "利润/现金流复合值",
            "unit": "元",
            "status": "candidate",
        },
    ]
    registry = {"source_fields": source_fields}

    rendered = render_field_aggregate_review(registry)

    assert "聚合歧义 1 个 code" in rendered
    assert "`f44` — ambiguous" in rendered
    assert "eastmoney.stock_get" in rendered and "最高价" in rendered
    assert "eastmoney.ulist_np" in rendered and "利润总额" in rendered
    assert "metric.composite" in rendered
    assert "仅供人工检查，不自动拆字段或定案" in rendered
    assert "单来源或全空的定义缺口" in rendered
    assert "field_metadata_gaps.md" in rendered and "unknown_fields.md" in rendered
    assert registry["source_fields"] == source_fields
