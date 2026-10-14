import csv
import json

from scripts import field_name_candidates as candidates


def _write_inventory(path, rows):
    columns = [
        "source",
        "path",
        "code",
        "canonical",
        "current_meaning",
        "unit",
        "status",
        "name_form",
        "lexical_tokens",
        "lexical_token_hint_not_meaning",
        "review_note",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def test_name_candidates_use_exact_identity_and_current_registry_status(tmp_path):
    registry_path = tmp_path / "field_registry.json"
    inventory_path = tmp_path / "inventory.csv"
    registry_path.write_text(
        json.dumps(
            {
                "source_fields": [
                    {
                        "source": "TDX",
                        "code": "lirunzonghe",
                        "status": "unverified",
                        "canonical": "",
                        "meaning": "",
                        "unit": "",
                    },
                    {
                        "source": "TDX",
                        "code": "returnOnEquity",
                        "status": "verified",
                        "canonical": "ROE",
                        "meaning": "",
                        "unit": "%",
                    },
                    {
                        "source": "TDX",
                        "code": "f13",
                        "status": "unverified",
                        "canonical": "",
                        "meaning": "",
                        "unit": "",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    _write_inventory(
        inventory_path,
        [
            {
                "source": "TDX",
                "path": "lirunzonghe",
                "code": "lirunzonghe",
                "status": "verified",
                "name_form": "recognized_pinyin_phrase_candidate",
                "lexical_tokens": "lirun zonghe",
                "lexical_token_hint_not_meaning": "利润总额（拼音候选）",
            },
            {
                "source": "TDX",
                "path": "returnOnEquity",
                "code": "returnOnEquity",
                "name_form": "camel_case_or_mixed",
                "lexical_tokens": "return On Equity",
                "lexical_token_hint_not_meaning": "收益 + 权益（需看接口）",
            },
            {
                "source": "OTHER",
                "path": "lirunzonghe",
                "code": "lirunzonghe",
                "name_form": "recognized_pinyin_phrase_candidate",
                "lexical_tokens": "wrong source",
                "lexical_token_hint_not_meaning": "错误映射",
            },
        ],
    )
    store = {
        "tdx.lirunzonghe": {"vals": {("600519", "T:20261012"): 3.5}},
        "tdx.returnOnEquity": {"vals": {("600519", "T:20261013"): 0.2}},
        "tdx.f13": {"vals": {("600519", "T:20261013"): 1}},
    }
    lineage = {
        "sources": {"TDX": {"runtime_aliases": ["tdx"]}},
        "source_aliases": {},
        "runtime_sources": {"tdx": {}},
    }

    result = candidates.build_field_name_candidates(
        store,
        list(store),
        registry_path,
        lineage,
        inventory_path,
    )

    by_path = {item["path"]: item for item in result["candidates"]}
    assert set(by_path) == {"lirunzonghe", "returnOnEquity"}
    assert by_path["lirunzonghe"]["registry_status"] == "unverified"
    assert by_path["lirunzonghe"]["lexical_hint_not_meaning"] == "利润总额（拼音候选）"
    assert by_path["lirunzonghe"]["sample_dates"] == ["T:20261012"]
    assert by_path["returnOnEquity"]["review_scope"] == "verified_metadata_gap"
    assert "3.5" not in json.dumps(result, ensure_ascii=False)


def test_ambiguous_runtime_identity_is_not_guessed(tmp_path):
    registry_path = tmp_path / "field_registry.json"
    inventory_path = tmp_path / "inventory.csv"
    registry_path.write_text(
        json.dumps(
            {
                "source_fields": [
                    {"source": source, "code": "profitTotal", "status": "unverified"}
                    for source in ("TDX", "ELTDX")
                ]
            }
        ),
        encoding="utf-8",
    )
    _write_inventory(inventory_path, [])
    lineage = {
        "sources": {
            "TDX": {"runtime_aliases": ["same_runtime"]},
            "ELTDX": {"runtime_aliases": ["same_runtime"]},
        },
        "source_aliases": {},
        "runtime_sources": {"same_runtime": {}},
    }

    result = candidates.build_field_name_candidates(
        {"same_runtime.profitTotal": {"vals": {}}},
        ["same_runtime.profitTotal"],
        registry_path,
        lineage,
        inventory_path,
    )

    assert result["candidate_count"] == 0
    assert result["ambiguous_runtime_paths"] == 1
