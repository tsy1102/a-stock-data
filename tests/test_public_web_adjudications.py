import json

import pytest

from scripts import public_web_adjudications as adjudications

SOURCE = "东财-push2(stock/get)"
URLS = [
    "https://data.eastmoney.com/zjlx/000001.html",
    "https://data.eastmoney.com/zjlx/000002.html",
]


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def _raw_payload(date_index):
    stocks = {}
    for index in range(1, 6):
        buy = "-" if index == 1 else index * 100 + date_index
        sell = index * 17 + date_index
        buy_value = 0 if buy == "-" else buy
        stocks[f"00000{index}"] = {"data": {"f147": buy, "f148": sell, "f149": buy_value - sell}}
    return {"stocks": stocks}


def _registry():
    records = []
    for code in ("f147", "f148", "f149"):
        conflict = {"canonical": [code, f"legacy-{code}"]}
        status = "conflict" if code == "f149" else "verified"
        resolution = "status_conflict" if code == "f149" else "matched"
        status_evidence = {
            "reference_statuses": ["verified"],
            "registry_aggregate_status": "unverified" if code == "f149" else "verified",
            "values": ["verified", "unverified"] if code == "f149" else ["verified"],
        }
        records.append(
            {
                "source": SOURCE,
                "code": code,
                "canonical": "",
                "meaning": "待破解",
                "unit": "元",
                "status": status,
                "status_resolution": resolution,
                "status_evidence": status_evidence,
                "reference_evidence": [{"status": "verified"}],
                "attribute_conflicts": conflict,
                "attribute_ambiguities": {},
                "adjudications": [],
            }
        )
    return {"source_fields": records, "fields": [], "mappings": []}


def _decision(code, meaning, canonical, url, page_label, obs):
    return {
        "id": f"20261109-{code}",
        "action": "verify_public_web_observation",
        "target": {"source": SOURCE, "code": code},
        "previous_status": "conflict" if code == "f149" else "verified",
        "previous_status_resolution": "status_conflict" if code == "f149" else "matched",
        "previous": {"canonical": "", "meaning": "待破解", "unit": "元"},
        "previous_attribute_conflicts": {"canonical": [code, f"legacy-{code}"]},
        "canonical": canonical,
        "meaning": meaning,
        "unit": "元",
        "rationale": "同日官方页面标签与至少两只股票的原始字段值对应；保留数据公式由多日样本复核。",
        "external_evidence": [url],
        "page_observations": obs,
    }


def _inputs(root):
    verification = root / "docs" / "field_verification"
    _write_json(
        verification / "source_lineage.json",
        {
            "sources": {
                SOURCE: {
                    "provider": "Eastmoney",
                    "independence_status": "confirmed",
                    "runtime_aliases": ["push2"],
                }
            }
        },
    )
    source_files = []
    numeric_samples = numeric_matches = dash_samples = dash_matches = 0
    for date_index, date_name in enumerate(("20261104", "20261105", "20261106"), start=1):
        relative = f"{date_name}/raw_push2.json"
        _write_json(verification / relative, _raw_payload(date_index))
        source_files.append(relative)
        for code, values in _raw_payload(date_index)["stocks"].items():
            data = values["data"]
            if data["f147"] == "-":
                dash_samples += 1
                dash_matches += int(data["f149"] == -data["f148"])
            else:
                numeric_samples += 1
                numeric_matches += int(data["f149"] == data["f147"] - data["f148"])

    observations = {}
    fields = {
        "f147": ("fund_small_buy", "小单买入金额", "小单 / 流入"),
        "f148": ("fund_small_sell", "小单卖出金额", "小单 / 流出"),
        "f149": ("fund_small_today", "小单净流入金额", "小单净流入"),
    }
    pages = [
        {"stock_code": "000001", "page_value": None, "page_text": None, "display_increment": 1},
        {"stock_code": "000002", "page_value": None, "page_text": None, "display_increment": 1},
    ]
    date_path = "20261106/raw_push2.json"
    latest = json.loads((verification / date_path).read_text(encoding="utf-8"))["stocks"]
    for field_code, (canonical, meaning, metric) in fields.items():
        page_rows = []
        for index, sample in enumerate(pages):
            stock_code = sample["stock_code"]
            raw_value = latest[stock_code]["data"][field_code]
            display_value = 0 if raw_value == "-" else raw_value
            display_text = str(display_value)
            page_rows.append(
                {
                    "stock_code": stock_code,
                    "data_date": "20261106",
                    "source_file": date_path,
                    "raw_value": raw_value,
                    "display_value": display_value,
                    "display_increment": sample["display_increment"],
                    "display_unit": "元",
                    "page_url": URLS[index],
                    "page_metric": metric,
                    "display_text": display_text,
                    "missing_as_zero": raw_value == "-",
                }
            )
        decision = _decision(field_code, meaning, canonical, URLS[0], metric, page_rows)
        decision["external_evidence"] = URLS
        observations[field_code] = decision

    memo_path = "adjudications/public_web/20261109_public_web_research.md"
    memo = verification / memo_path
    memo.parent.mkdir(parents=True, exist_ok=True)
    evidence_lines = ["# Official page observation evidence"]
    for code, decision in observations.items():
        evidence_lines.append(f"## {SOURCE}::{code}")
        for url in URLS:
            evidence_lines.append(url)
        for row in decision["page_observations"]:
            evidence_lines.extend(
                [row["stock_code"], row["data_date"], row["page_metric"], row["display_text"]]
            )
            normalized = {
                **row,
                "display_value": str(row["display_value"]),
                "display_increment": str(row["display_increment"]),
            }
            evidence_lines.append(
                adjudications._observation_evidence_line(SOURCE, code, normalized)
            )
    memo.write_text("\n".join(evidence_lines) + "\n", encoding="utf-8")
    formula = {
        "target_code": "f149",
        "left_code": "f147",
        "right_code": "f148",
        "operator": "-",
        "source_files": source_files,
        "numeric_samples": numeric_samples,
        "numeric_matches": numeric_matches,
        "dash_samples": dash_samples,
        "dash_matches": dash_matches,
        "distinct_dates": len(source_files),
        "distinct_stocks": 5,
    }
    reverse_formula = {
        "target_code": "f148",
        "left_code": "f147",
        "right_code": "f149",
        "operator": "-",
        "source_files": source_files,
        "numeric_samples": numeric_samples,
        "numeric_matches": numeric_matches,
        "dash_samples": dash_samples,
        "dash_matches": dash_matches,
        "distinct_dates": len(source_files),
        "distinct_stocks": 5,
    }
    document = {
        "schema_version": 1,
        "evidence_basis": "public_web_observation",
        "reviewer": "test reviewer",
        "reviewed_on": "2026-11-09",
        "evidence_file": memo_path,
        "formula_validation": formula,
        "formula_validations": [reverse_formula],
        "decisions": list(observations.values()),
    }
    decision_path = "adjudications/public_web/20261109_push2_fund_flow.json"
    _write_json(verification / decision_path, document)
    return _registry(), document, decision_path, memo_path


def test_public_page_observations_resolve_source_semantics_without_cross_source_mapping(tmp_path):
    registry, document, decision_path, _ = _inputs(tmp_path)

    updated, stats = adjudications.apply_public_web_observation_adjudications(
        registry, document, decision_path, tmp_path
    )

    records = {row["code"]: row for row in updated["source_fields"]}
    assert records["f147"]["canonical"] == "fund_small_buy"
    assert records["f148"]["canonical"] == "fund_small_sell"
    assert records["f149"]["canonical"] == "fund_small_today"
    assert all(row["status"] == "verified" for row in records.values())
    assert all(
        row["status_resolution"] == "verified_by_public_web_observation" for row in records.values()
    )
    assert all(row["attribute_conflicts"] == {} for row in records.values())
    assert updated["mappings"] == []
    assert stats["public_web_observation_verified"] == 3
    assert stats["status_conflicts_resolved"] == 1
    assert stats["mappings_added"] == 0


def test_public_page_observation_is_idempotent_and_parity_validates_it(tmp_path):
    registry, document, decision_path, _ = _inputs(tmp_path)
    once, _ = adjudications.apply_public_web_observation_adjudications(
        registry, document, decision_path, tmp_path
    )
    twice, stats = adjudications.apply_public_web_observation_adjudications(
        once, document, decision_path, tmp_path
    )

    assert twice == once
    assert stats["already_applied"] == 3
    assert adjudications.validate_registry_adjudications(once, tmp_path) == []
    f148 = next(item for item in once["source_fields"] if item["code"] == "f148")
    f149 = next(item for item in once["source_fields"] if item["code"] == "f149")
    assert f148["adjudications"][-1]["formula_validation"]["target_code"] == "f148"
    assert f149["adjudications"][-1]["formula_validation"]["target_code"] == "f149"


def test_public_page_observation_rejects_raw_sample_mismatch(tmp_path):
    registry, document, decision_path, _ = _inputs(tmp_path)
    document["decisions"][0]["page_observations"][0]["raw_value"] = 999

    with pytest.raises(ValueError, match="differs from archived"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, tmp_path
        )


def test_public_page_observation_rejects_non_https_or_unrounded_match(tmp_path):
    registry, document, decision_path, _ = _inputs(tmp_path)
    document["decisions"][0]["external_evidence"] = ["http://data.example.test/stock"]

    with pytest.raises(ValueError, match="HTTPS"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, tmp_path
        )

    registry, document, decision_path, _ = _inputs(tmp_path / "rounding")
    document["decisions"][0]["page_observations"][1]["display_value"] = 1000
    with pytest.raises(ValueError, match="rounding precision"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, tmp_path / "rounding"
        )


def test_public_page_observation_cannot_resolve_meaning_or_unit_conflicts(tmp_path):
    registry, document, decision_path, _ = _inputs(tmp_path)
    record = registry["source_fields"][0]
    record["attribute_conflicts"] = {"meaning": ["小单买入", "买入"]}
    document["decisions"][0]["previous_attribute_conflicts"] = record["attribute_conflicts"]

    with pytest.raises(ValueError, match="cannot resolve meaning or unit conflicts"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, tmp_path
        )


def test_public_page_observation_rejects_unallowlisted_host_and_unlinked_evidence(tmp_path):
    registry, document, decision_path, _ = _inputs(tmp_path)
    document["decisions"][0]["external_evidence"] = ["https://evil.example/stock/000001"]
    with pytest.raises(ValueError, match="allowlisted official"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, tmp_path
        )

    registry, document, decision_path, memo_path = _inputs(tmp_path / "evidence")
    memo = tmp_path / "evidence" / "docs" / "field_verification" / memo_path
    memo.write_text("# Same page values but no structured observation links\n", encoding="utf-8")
    with pytest.raises(ValueError, match="exact structured observation"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, tmp_path / "evidence"
        )


def test_public_page_observation_cannot_change_known_unit_or_hide_bad_conflict_shape(tmp_path):
    registry, document, decision_path, _ = _inputs(tmp_path)
    decision = document["decisions"][0]
    decision["unit"] = "万元"
    evidence_path = tmp_path / "docs" / "field_verification" / document["evidence_file"]
    evidence_lines = []
    for observation in decision["page_observations"]:
        observation["display_unit"] = "万元"
        normalized = {
            **observation,
            "display_value": str(observation["display_value"]),
            "display_increment": str(observation["display_increment"]),
        }
        evidence_lines.append(adjudications._observation_evidence_line(SOURCE, "f147", normalized))
    evidence_path.write_text(
        evidence_path.read_text(encoding="utf-8") + "\n" + "\n".join(evidence_lines),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="cannot overwrite an established unit"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, tmp_path
        )

    registry, document, decision_path, _ = _inputs(tmp_path / "status")
    row = next(item for item in registry["source_fields"] if item["code"] == "f149")
    row["status_evidence"]["values"] = None
    with pytest.raises(ValueError, match="cannot resolve this status conflict"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, tmp_path / "status"
        )


def test_public_page_observation_can_resolve_aggregate_status_conflict_without_attribute_conflict(
    tmp_path,
):
    registry, document, decision_path, _ = _inputs(tmp_path)
    row = next(item for item in registry["source_fields"] if item["code"] == "f149")
    decision = next(item for item in document["decisions"] if item["target"]["code"] == "f149")
    row["attribute_conflicts"] = {}
    decision["previous_attribute_conflicts"] = {}
    _write_json(
        tmp_path / "docs" / "field_verification" / decision_path,
        document,
    )

    updated, stats = adjudications.apply_public_web_observation_adjudications(
        registry, document, decision_path, tmp_path
    )
    resolved = next(item for item in updated["source_fields"] if item["code"] == "f149")
    assert resolved["status"] == "verified"
    assert resolved["attribute_conflicts"] == {}
    assert stats["status_conflicts_resolved"] == 1
    assert adjudications.validate_registry_adjudications(updated, tmp_path) == []


def test_formula_validations_must_match_one_decision_target(tmp_path):
    registry, document, decision_path, _ = _inputs(tmp_path)
    document["formula_validations"].append(document["formula_validations"][0].copy())
    with pytest.raises(ValueError, match="duplicate formula validation target"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, tmp_path
        )

    registry, document, decision_path, _ = _inputs(tmp_path / "unmatched")
    formula = document["formula_validations"][0]
    formula.update(
        {
            "target_code": "f999",
            "left_code": "f148",
            "right_code": "f149",
            "operator": "+",
            "numeric_samples": 15,
            "numeric_matches": 15,
            "dash_samples": 0,
            "dash_matches": 0,
        }
    )
    for source_file in formula["source_files"]:
        sample_path = tmp_path / "unmatched" / "docs" / "field_verification" / source_file
        payload = json.loads(sample_path.read_text(encoding="utf-8"))
        for stock in payload["stocks"].values():
            stock["data"]["f999"] = stock["data"]["f148"] + stock["data"]["f149"]
        _write_json(sample_path, payload)
    with pytest.raises(
        ValueError, match="formula validation target must match exactly one decision"
    ):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, tmp_path / "unmatched"
        )


def test_registry_parity_detects_audit_observation_tampering(tmp_path):
    registry, document, decision_path, _ = _inputs(tmp_path)
    updated, _ = adjudications.apply_public_web_observation_adjudications(
        registry, document, decision_path, tmp_path
    )
    f149 = next(item for item in updated["source_fields"] if item["code"] == "f149")
    assert "formula_validation" in f149["adjudications"][-1]
    f147 = next(item for item in updated["source_fields"] if item["code"] == "f147")
    assert "formula_validation" not in f147["adjudications"][-1]
    f147["adjudications"][-1]["page_observations"][0]["display_value"] = "999999"
    assert any(
        "observations differ from decision evidence" in problem
        for problem in adjudications.validate_registry_adjudications(updated, tmp_path)
    )


def test_formula_validation_rejects_empty_sample_files_and_parity_reports_malformed_snapshots(
    tmp_path,
):
    registry, document, decision_path, _ = _inputs(tmp_path)
    empty_sample = "20261107/raw_push2.json"
    _write_json(tmp_path / "docs" / "field_verification" / empty_sample, {"stocks": {}})
    document["formula_validation"]["source_files"].append(empty_sample)
    document["formula_validation"]["distinct_dates"] += 1
    with pytest.raises(ValueError, match="contains no formula rows"):
        adjudications.apply_public_web_observation_adjudications(
            registry, document, decision_path, tmp_path
        )

    registry, document, decision_path, _ = _inputs(tmp_path / "tampered")
    updated, _ = adjudications.apply_public_web_observation_adjudications(
        registry, document, decision_path, tmp_path / "tampered"
    )
    f147 = next(item for item in updated["source_fields"] if item["code"] == "f147")
    f147["adjudications"][-1]["metadata_change"] = "malformed"
    assert any(
        "public-page adjudication invalid" in problem
        for problem in adjudications.validate_registry_adjudications(updated, tmp_path / "tampered")
    )
