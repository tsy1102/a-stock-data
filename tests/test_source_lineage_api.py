import json

import pytest

from scripts import field_registry_api as registry_api
from scripts import source_lineage_api as lineage_api


def test_lineage_covers_registered_sources_and_runtime_aliases():
    registry = registry_api.load_registry()
    lineage = lineage_api.load_source_lineage(registry=registry)

    assert set(lineage["sources"]) == {record["name"] for record in registry["sources"]}
    assert all(
        alias in lineage["runtime_sources"] for alias in lineage["source_aliases"].values() if alias
    )
    assert all(
        not record["anchor_eligible"] or record["independence_status"] == "confirmed"
        for record in lineage["sources"].values()
    )


def test_repository_evidence_and_dialog_confirmation_are_separate_states():
    lineage = lineage_api.load_source_lineage()
    confirmed = {
        source
        for source, record in lineage["sources"].items()
        if record.get("dialog_confirmation", {}).get("status") == "confirmed"
    }

    assert confirmed == {
        "同花顺-fuyao",
        "TDX(双命名源)",
        "ZHB-tdxstat",
        "ZHB-tdxstat2",
        "ZHB-tipinfo",
        "TDX-eltdx(适配层)",
        "levistock(ftshare)",
        "东财-push2(stock/get)",
        "东财-资金流(em_fund_flow)",
        "东财-ulist239(np/get)",
        "东财-push2ex",
        "东财-datacenter(英文键)",
        "东财-slist",
        "东财-clist",
        "腾讯(qt.gtimg)",
        "新浪(hq.sinajs)",
        "新浪(扩展API)",
        "AxData",
        "东财-push2_full",
        "财联社(cls)",
        "东财-em_kline_f61",
        "东财-热榜(em_hot)",
        "开盘啦(kpl)",
    }
    assert all(
        lineage["sources"][source]["repository_mapping_status"] == "confirmed"
        for source in confirmed
    )
    assert (
        sum(
            record.get("dialog_confirmation", {}).get("status") == "pending"
            for record in lineage["sources"].values()
        )
        == 5
    )
    assert lineage["project_reference"]["url"] == "https://github.com/simonlin1212/a-stock-data"
    assert lineage["sources"]["AxData"]["anchor_eligible"] is False
    assert lineage["sources"]["AxData"]["independence_status"] == "unconfirmed"
    assert (
        "不代表它托管 ZHB 缓存" in lineage["sources"]["ZHB-tipinfo"]["dialog_confirmation"]["note"]
    )


def test_confirmed_dialog_relation_requires_date_note_and_https_repository(tmp_path):
    malformed = tmp_path / "lineage.json"
    lineage = {
        "schema_version": 1,
        "source_aliases": {"source": None},
        "runtime_sources": {},
        "sources": {
            "source": {
                "runtime_aliases": [],
                "independence_family": None,
                "independence_status": "unconfirmed",
                "anchor_eligible": False,
                "repository_mapping_status": "unconfirmed",
                "repositories": [
                    {"url": "https://github.com/example/repo", "status": "unconfirmed"}
                ],
                "dialog_confirmation": {
                    "status": "confirmed",
                    "confirmed_on": "2026-13-40",
                    "note": "confirmed by user",
                },
            }
        },
    }
    malformed.write_text(json.dumps(lineage), encoding="utf-8")

    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        lineage_api.load_source_lineage(path=str(malformed))


def test_unconfirmed_and_unknown_runtime_sources_have_no_independence_family():
    lineage = lineage_api.load_source_lineage()

    assert lineage_api.runtime_family("market_sources", lineage) is None
    assert lineage_api.runtime_family("not-registered", lineage) is None


def test_runtime_alias_resolution_includes_non_anchor_sources():
    lineage = lineage_api.load_source_lineage()

    aliases = lineage_api.runtime_aliases_for_source("开盘啦(kpl)", lineage)

    assert aliases == ["market_sources"]
    assert lineage_api.source_aliases("开盘啦(kpl)", lineage) == []


def test_load_lineage_rejects_non_object_json_root(tmp_path):
    malformed = tmp_path / "lineage.json"
    malformed.write_text("[]", encoding="utf-8")

    with pytest.raises(TypeError, match="root must be an object"):
        lineage_api.load_source_lineage(path=str(malformed))
