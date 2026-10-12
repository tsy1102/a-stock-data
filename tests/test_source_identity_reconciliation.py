import json
from datetime import date, timedelta

import pytest

from scripts import collision_dates
from scripts import source_identity_reconciliation as identity


@pytest.fixture
def identity_fixture(tmp_path, monkeypatch):
    data_dir = tmp_path / "captures"
    state_path = tmp_path / "state.json"
    rows = {
        endpoint.field_code: {
            "source": "FTShare",
            "code": endpoint.field_code,
            "path": endpoint.output_key,
        }
        for endpoint in identity.FTSHARE_ENDPOINTS
    }
    registry = {"source_fields": []}
    lineage = {"sources": {}}
    fingerprint = {"value": "contract-v1"}
    monkeypatch.setattr(
        identity,
        "_load_policy_context",
        lambda registry=None, lineage=None: ({}, {}, rows, None),
    )
    monkeypatch.setattr(
        identity,
        "_anchor_aliases",
        lambda _registry, _lineage: {"tencent": "tencent-family"},
    )
    monkeypatch.setattr(
        identity,
        "_contract_fingerprint",
        lambda _endpoint, _field_row, _lineage: fingerprint["value"],
    )
    monkeypatch.setattr(collision_dates, "is_trading_session", lambda _day: True)

    def write_day(day, endpoint_values, *, mismatch_symbol=None, ftshare_meta=None):
        folder = data_dir / day
        folder.mkdir(parents=True, exist_ok=True)
        stock_codes = [f"{index:06d}" for index in range(1, 19)]
        candidate_stocks = {}
        reference_stocks = {}
        for index, code in enumerate(stock_codes):
            record = {
                "trade_date": f"{day[:4]}-{day[4:6]}-{day[6:]}",
                "value": index,
                "category": "A",
            }
            stock_record = {
                endpoint.output_key: [
                    dict(record) for _ in endpoint_values[endpoint.field_code]
                ]
                for endpoint in identity.FTSHARE_ENDPOINTS
                if endpoint.field_code in endpoint_values
            }
            candidate_stocks[code] = stock_record
            anchor_record = dict(record)
            if code == mismatch_symbol:
                anchor_record["value"] = -1
            reference_stocks[code] = {"records": [anchor_record]}

        raw = {"stocks": candidate_stocks}
        meta = {
            "data_date": day,
            "data_date_domain": "trading",
            "market_phase": "closed",
            "sources": {
                "ftshare": {
                    "ok": True,
                    "status": "ok",
                    "as_of_date": day,
                    **(ftshare_meta or {}),
                },
                "tencent": {"ok": True, "status": "ok", "as_of_date": day},
            },
        }
        (folder / "raw_ftshare.json").write_text(
            json.dumps(raw), encoding="utf-8"
        )
        (folder / "raw_tencent.json").write_text(
            json.dumps({"stocks": reference_stocks}), encoding="utf-8"
        )
        (folder / "meta.json").write_text(json.dumps(meta), encoding="utf-8")

    def reconcile(persist=True):
        return identity.reconcile_source_identity(
            data_dir=data_dir,
            state_path=state_path,
            persist=persist,
        )

    return {
        "data_dir": data_dir,
        "state_path": state_path,
        "fingerprint": fingerprint,
        "write_day": write_day,
        "reconcile": reconcile,
    }


def _ggmx_values():
    return {"ggmx": [{"trade_date": "unused", "value": 1, "category": "A"}]}


def test_date_and_null_measurement_alone_cannot_prove_identity():
    candidate = {"trade_date": "20261009", "value": None}
    reference = {"trade_date": "20261009", "value": None}
    assert not identity._record_matches(candidate, reference)


def test_business_source_value_participates_in_exact_match():
    candidate = {"trade_date": "20261009", "value": 1, "source": "eastmoney"}
    same_source = {"trade_date": "20261009", "value": 1, "source": "eastmoney"}
    other_source = {"trade_date": "20261009", "value": 1, "source": "tencent"}

    assert identity._record_matches(candidate, same_source)
    assert not identity._record_matches(candidate, other_source)


def test_exact_endpoint_match_suppresses_only_that_endpoint(identity_fixture, monkeypatch):
    fixture = identity_fixture
    for day in ("20261008", "20261009", "20261012"):
        fixture["write_day"](day, _ggmx_values())

    result = fixture["reconcile"]()
    endpoint = result["endpoints"]["ggmx"]
    assert endpoint["status"] == "operationally_redundant"
    assert endpoint["reference_source"] == "tencent"
    assert endpoint["evidence_dates"] == ["20261008", "20261009", "20261012"]

    state = json.loads(fixture["state_path"].read_text(encoding="utf-8"))
    assert state["endpoints"]["ggmx"]["status"] == "operationally_redundant"
    monkeypatch.setattr(identity, "STATE_PATH", fixture["state_path"])
    monkeypatch.setattr(identity, "DATA_DIR", fixture["data_dir"])
    plan = identity.get_ftshare_identity_plan(data_date="20261013")
    assert "ggmx" in plan["skip"]
    assert set(plan["skip"]) == {"ggmx"}


def test_one_mismatched_stock_prevents_endpoint_suppression(identity_fixture):
    fixture = identity_fixture
    for day in ("20261008", "20261009", "20261012"):
        fixture["write_day"](
            day, _ggmx_values(), mismatch_symbol="000018"
        )

    result = fixture["reconcile"](persist=False)
    endpoint = result["endpoints"]["ggmx"]
    assert endpoint["status"] == "pending"
    assert endpoint["observations"][-1]["references"]["tencent"]["matched_symbols"] == 17
    assert not fixture["state_path"].exists()


def test_skipped_endpoint_is_not_used_as_identity_evidence(identity_fixture):
    fixture = identity_fixture
    for day in ("20261008", "20261009", "20261012"):
        fixture["write_day"](
            day,
            {},
            ftshare_meta={
                "identity_skipped_endpoints": {
                    "ggmx": {"status": "operationally_redundant"}
                }
            },
        )

    result = fixture["reconcile"](persist=False)
    assert result["endpoints"]["ggmx"]["status"] == "pending"
    assert result["endpoints"]["ggmx"]["observations"] == []


def test_contract_change_requires_three_new_capture_dates(identity_fixture):
    fixture = identity_fixture
    for day in ("20261008", "20261009", "20261012"):
        fixture["write_day"](day, _ggmx_values())
    initial = fixture["reconcile"]()
    assert initial["endpoints"]["ggmx"]["status"] == "operationally_redundant"

    fixture["fingerprint"]["value"] = "contract-v2"
    changed = fixture["reconcile"]()
    assert changed["endpoints"]["ggmx"]["status"] == "pending_revalidation"
    state = json.loads(fixture["state_path"].read_text(encoding="utf-8"))
    assert state["endpoints"]["ggmx"]["status"] == "pending_revalidation"

    for day in ("20261013", "20261014", "20261015"):
        fixture["write_day"](day, _ggmx_values())
    revalidated = fixture["reconcile"]()
    assert revalidated["endpoints"]["ggmx"]["status"] == "operationally_redundant"
    assert revalidated["endpoints"]["ggmx"]["evidence_dates"] == [
        "20261013",
        "20261014",
        "20261015",
    ]


def test_scheduled_recheck_opens_endpoint_after_any_mismatch(identity_fixture):
    fixture = identity_fixture
    for day in ("20261008", "20261009", "20261012"):
        fixture["write_day"](day, _ggmx_values())
    fixture["reconcile"]()

    fixture["write_day"](
        "20261013",
        _ggmx_values(),
        mismatch_symbol="000018",
        ftshare_meta={
            "identity_sampled_endpoints": ["ggmx"],
            "identity_recheck_endpoints": ["ggmx"],
            "identity_contract_fingerprints": {"ggmx": "contract-v1"},
        },
    )
    result = fixture["reconcile"]()

    assert result["endpoints"]["ggmx"]["status"] == "reopened"
    state = json.loads(fixture["state_path"].read_text(encoding="utf-8"))
    assert "ggmx" not in state["endpoints"]


def test_periodic_recheck_waits_for_twenty_distinct_trading_data_dates(
    identity_fixture,
):
    fixture = identity_fixture
    start = date(2026, 10, 13)
    for offset in range(19):
        day = (start + timedelta(days=offset)).strftime("%Y%m%d")
        folder = fixture["data_dir"] / day
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "meta.json").write_text(
            json.dumps(
                {
                    "data_date": day,
                    "data_date_domain": "trading",
                    "market_phase": "pre_open",
                }
            ),
            encoding="utf-8",
        )

    state = {
        "schema_version": 1,
        "endpoints": {
            "ggmx": {
                "status": "operationally_redundant",
                "contract_fingerprint": "contract-v1",
                "last_probe_date": "20261012",
            }
        },
    }
    fingerprints = {"ggmx": "contract-v1"}
    plan = identity._plan_from_state(
        state, fingerprints, fixture["data_dir"], "20261201", False
    )
    assert "ggmx" in plan["skip"]
    assert "ggmx" not in plan["recheck"]

    day = (start + timedelta(days=19)).strftime("%Y%m%d")
    folder = fixture["data_dir"] / day
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "meta.json").write_text(
        json.dumps(
            {
                "data_date": day,
                "data_date_domain": "trading",
                "market_phase": "non_trading_day",
            }
        ),
        encoding="utf-8",
    )
    plan = identity._plan_from_state(
        state, fingerprints, fixture["data_dir"], "20261201", False
    )
    assert "ggmx" not in plan["skip"]
    assert "ggmx" in plan["recheck"]


def test_snapshot_requires_matching_source_date_and_project_trade_day(identity_fixture):
    fixture = identity_fixture
    fixture["write_day"]("20261012", _ggmx_values())
    folder = fixture["data_dir"] / "20261012"
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    meta["sources"]["ftshare"]["as_of_date"] = "20261009"
    (folder / "meta.json").write_text(json.dumps(meta), encoding="utf-8")

    result = fixture["reconcile"](persist=False)
    assert result["endpoints"]["ggmx"]["status"] == "pending"
    assert result["endpoints"]["ggmx"]["observations"] == []


def test_anchor_without_exact_data_date_cannot_prove_identity(identity_fixture):
    fixture = identity_fixture
    for day in ("20261008", "20261009", "20261012"):
        fixture["write_day"](day, _ggmx_values())
    folder = fixture["data_dir"] / "20261009"
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    meta["sources"]["tencent"].pop("as_of_date")
    (folder / "meta.json").write_text(json.dumps(meta), encoding="utf-8")

    result = fixture["reconcile"](persist=False)
    assert result["endpoints"]["ggmx"]["status"] == "pending"
    assert result["endpoints"]["ggmx"]["observations"][-2]["references"] == {}


def test_pre_open_capture_is_eligible_when_data_dates_match(identity_fixture):
    fixture = identity_fixture
    fixture["write_day"]("20261012", _ggmx_values())
    folder = fixture["data_dir"] / "20261012"
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    meta["market_phase"] = "pre_open"
    (folder / "meta.json").write_text(json.dumps(meta), encoding="utf-8")

    result = fixture["reconcile"](persist=False)
    assert result["endpoints"]["ggmx"]["status"] == "pending"
    assert [item["date"] for item in result["endpoints"]["ggmx"]["observations"]] == [
        "20261012"
    ]
