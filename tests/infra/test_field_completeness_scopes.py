"""Regression tests for Markdown source scoping in the field registry audit."""

import importlib

import pytest


def test_unmapped_sibling_isolated_and_markdown_child_inherits(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend("scripts")
    afc = importlib.import_module("audit_field_completeness")
    dictionary = tmp_path / "field_dict.md"
    dictionary.write_text(
        "### Source A\nparent-token\n#### Child section\nchild-token\n"
        "### Unmapped sibling\nforeign-token\n### Source B\nother-token\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(afc, "DICT", str(dictionary))
    source_by_title = {"Source A": ["A"], "Source B": ["B"]}
    monkeypatch.setattr(afc, "section_to_sources", lambda title: source_by_title.get(title, []))
    monkeypatch.setattr(
        afc,
        "reg_tokens_for_section",
        lambda source, text: {line.strip() for line in text.splitlines() if line.strip()},
    )

    registered = afc.registered_field_sets()

    assert registered["A"] == {"parent-token", "child-token"}
    assert registered["B"] == {"other-token"}
    assert "foreign-token" not in registered["A"]


def test_known_same_level_field_sections_have_explicit_source_maps(monkeypatch):
    monkeypatch.syspath_prepend("scripts")
    afc = importlib.import_module("audit_field_completeness")

    assert afc.section_to_sources("12.8.3.1 datacenter 北向持股 + 两融衍生字段补录") == [
        "东财-datacenter(英文键)"
    ]
    assert "东财-热榜(em_hot)" not in afc.section_to_sources("12.8.12b THS SDK（已退役）")
    assert afc.section_to_sources("12.21 开盘啦 App 数据解析工具") == ["开盘啦(kpl)"]
    assert afc.section_to_sources("12.17 KPL 开盘啦（longhuvip.com 私有 API）") == ["开盘啦(kpl)"]
    assert afc.section_to_sources("12.8.14 新浪（行情/三表/期权/资金流备胎）") == ["新浪(扩展API)"]
    sina_table = "| field | meaning |\n|:--|:--|\n| ask_vol/ask/last/bid | 盘口价量 |\n"
    assert {"ask_vol", "ask", "last", "bid"} <= afc.reg_tokens_for_section(
        "新浪(扩展API)", sina_table
    )
    kpl_table = (
        "| 索引 | 字段名 | 含义 | 对应项目字段 |\n"
        "|:--:|:--|:--|:--|\n"
        "| [0] | code | 股票代码 | code |\n"
        "| [1] | volRatio | 量比 | volume_ratio(tx49) |\n"
    )
    assert afc.reg_tokens_for_section("开盘啦(kpl)", kpl_table) == {"code", "volRatio"}
    eltdx_tokens = afc.reg_tokens_for_section(
        "TDX-eltdx(适配层)",
        "| field |\n|:--|\n| adjust |\n| period |\n| limit_up_price |\n| locked_amount |\n",
    )
    assert {"limit_up_price", "locked_amount"} <= eltdx_tokens
    assert not {"adjust", "period"} & eltdx_tokens


def test_levistock_legacy_identity_is_reclassified_without_promoting_archive_only_tokens(
    monkeypatch,
):
    import json
    from collections import Counter
    from pathlib import Path

    monkeypatch.syspath_prepend("scripts")
    afc = importlib.import_module("audit_field_completeness")
    manifest_path = (
        Path(afc.ROOT) / "docs/field_verification/source_identity_reclassifications.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    registered = afc.registered_field_sets()

    expected = {row["code"]: row["to_source"] for row in manifest["mappings"]}
    observed = {
        code: source
        for source, codes in registered.items()
        for code in codes
        if source in manifest["counts"]
    }
    assert observed == expected
    assert Counter(observed.values()) == Counter(manifest["counts"])
    assert manifest["counts_total"] == len(expected) == 175
    assert manifest["archive_only_count"] == len(manifest["archive_only_tokens"]) == 56
    for source in manifest["counts"]:
        assert not set(manifest["archive_only_tokens"]) & registered.get(source, set())
    assert manifest["from_source"] not in registered


def test_extracted_registry_source_metadata_is_unique(monkeypatch):
    monkeypatch.syspath_prepend("scripts")
    extractor = importlib.import_module("extract_registry")

    registry, _stats = extractor.extract()

    source_names = [source["name"] for source in registry["sources"]]
    assert len(source_names) == len(set(source_names))
    assert source_names.count("东财-datacenter(英文键)") == 1
    assert "levistock(ftshare)" not in source_names
    metadata = {source["name"]: source for source in registry["sources"]}
    assert metadata["AxData"]["source_role"] == "framework_reference"
    assert metadata["FTShare"]["source_role"] == "service_endpoint"
    assert metadata["Levistock历史未归属"]["source_role"] == "historical_unattributed"
    assert metadata["开盘红(Levistock适配)"]["source_role"] == "provider_component"
    source_counts = {}
    for row in registry["source_fields"]:
        source_counts[row["source"]] = source_counts.get(row["source"], 0) + 1
    assert source_counts["Levistock历史未归属"] == 136
    assert source_counts["开盘红(Levistock适配)"] == 33
    assert source_counts["FTShare"] == 6


def test_audit_help_does_not_create_a_report(tmp_path, monkeypatch, capsys):
    monkeypatch.syspath_prepend("scripts")
    afc = importlib.import_module("audit_field_completeness")
    monkeypatch.setattr(afc, "ROOT", str(tmp_path))

    with pytest.raises(SystemExit) as exc_info:
        afc.main(["--help"])

    assert exc_info.value.code == 0
    assert "--report-output" in capsys.readouterr().out
    assert not (tmp_path / "docs/field_verification/20260906/completeness_audit.json").exists()


def test_leaf_keys_excludes_capture_metadata_containers(monkeypatch):
    monkeypatch.syspath_prepend("scripts")
    afc = importlib.import_module("audit_field_completeness")
    capture = {
        "stocks": {
            "600519": {
                "auction_final": {
                    "auction_volume": 1200,
                    "__source_meta__": {
                        "auction_phase": "final",
                        "collision_eligible": True,
                        "data_status": "final",
                        "exclusion_reason": None,
                        "expected_trading_day": "2026-10-08",
                    },
                }
            }
        },
        "auction_snapshot_meta": {
            "item_count": 1,
            "requested_stage": "final",
            "response_code": 0,
            "response_timestamp": 1791446066469,
            "source_data_date": "2026-10-08",
        },
    }

    assert afc._leaf_keys(capture) == {"auction_volume"}
