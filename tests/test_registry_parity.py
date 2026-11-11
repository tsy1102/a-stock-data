import copy
import json
from datetime import date
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


def test_repository_scope_manifest_contains_only_current_baseline_pairs():
    entries, problems = registry_parity._load_scope_manifest(registry_parity.SCOPE_MANIFEST)

    assert problems == []
    assert entries is not None
    expected = {
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
    assert entries[("同花顺-fuyao", "tags")]["disposition"] == "captured_context"
    assert entries[("同花顺-fuyao", "tags")]["capture_path"] == (
        "raw_fuyao.json:market.short_term_benchmark[*].tags"
    )


def test_repository_parity_classifies_all_nonbaseline_paths(capsys):
    assert registry_parity.main([]) == 0

    output = capsys.readouterr().out
    assert "registry-core(1872/2486/347)" in output
    assert "parity[unverified-candidates]: PASS 119" in output
    assert "parity[source-contract-adjudications]: PASS 10" in output
    assert "parity[adjudication-addenda]: PASS 8" in output
    assert "parity[capture-path-addenda]: PASS 2" in output
    assert "parity[field_matrix]: PASS" in output


def test_source_contract_adjudications_are_validated_and_counted_separately():
    registry = registry_parity.fra.load_registry()
    records = registry_parity.fra.source_field_records(registry)
    base = registry_parity.afc.registered_field_sets()
    base_pairs = {(source, code) for source, codes in base.items() for code in codes}
    e3_pairs, _, _ = registry_parity._validated_addenda(registry, records, base_pairs)
    contract_pairs, _, _ = registry_parity._validated_contract_addenda(
        registry, records, base_pairs
    )
    observation_pairs, _, _ = registry_parity._validated_observation_addenda(
        registry, records, base_pairs
    )
    declared_pairs = e3_pairs | contract_pairs | observation_pairs

    pairs, matrix, problems = registry_parity._validated_source_contract_adjudications(
        registry, records, base_pairs, declared_pairs
    )

    assert problems == []
    assert pairs == {
        ("TDX(双命名源)", "bid2"),
        ("TDX(双命名源)", "bid3"),
        ("TDX(双命名源)", "bid4"),
        ("TDX(双命名源)", "bid5"),
        ("TDX(双命名源)", "ask2"),
        ("TDX(双命名源)", "ask3"),
        ("TDX(双命名源)", "ask4"),
        ("TDX(双命名源)", "ask5"),
        ("TDX(双命名源)", "zhuying_shouru"),
        ("TDX(双命名源)", "zong_xianjinliu"),
    }
    assert matrix == {
        "equity_incentive_date": {"ZHB-tipinfo"},
        "eps_raw": {"TDX(双命名源)", "TDX-eltdx(适配层)"},
        "f59": {"东财-em_kline_f61"},
        "forecast_date_recent": {"ZHB-tipinfo"},
        "forecast_type": {"ZHB-tipinfo"},
        "gudong_renshu": {"TDX(双命名源)"},
        "gu_dong_ren_shu_raw_float": {"TDX-eltdx(适配层)"},
        "guo_jia_gu_raw_float": {"TDX-eltdx(适配层)"},
        "updated_date": {"TDX-eltdx(适配层)"},
        "ipo_date": {"TDX-eltdx(适配层)"},
        "updated_date_raw": {"TDX-eltdx(适配层)"},
        "ipo_date_raw": {"TDX-eltdx(适配层)"},
        "limit_up_price": {"TDX-eltdx(适配层)"},
        "limit_down_price": {"TDX-eltdx(适配层)"},
        "absolute_index": {"TDX-eltdx(适配层)"},
        "auction_matched_volume": {"TDX-eltdx(适配层)"},
        "auction_unmatched_signed_volume": {"TDX-eltdx(适配层)"},
        "event_kind": {"TDX-eltdx(适配层)"},
        "order_count": {"TDX-eltdx(适配层)"},
        "side": {"TDX-eltdx(适配层)"},
        "status_raw": {"TDX-eltdx(适配层)"},
        "province_raw": {"TDX-eltdx(适配层)"},
        "industry_raw": {"TDX-eltdx(适配层)"},
        "record_hex": {"TDX-eltdx(适配层)"},
        "b_gu_raw_float": {"TDX-eltdx(适配层)"},
        "h_gu_raw_float": {"TDX-eltdx(适配层)"},
        "finance_info_raw": {"TDX-eltdx(适配层)"},
        "jing_li_run_raw_float": {"TDX(双命名源)", "TDX-eltdx(适配层)"},
        "liu_tong_gu_ben_raw_float": {"TDX(双命名源)", "TDX-eltdx(适配层)"},
        "zong_gu_ben_raw_float": {"TDX(双命名源)", "TDX-eltdx(适配层)"},
        "zong_zi_chan_raw_float": {"TDX(双命名源)", "TDX-eltdx(适配层)"},
        "chang_qi_fu_zhai_raw_float": {"TDX-eltdx(适配层)"},
        "gu_ding_zi_chan_raw_float": {"TDX-eltdx(适配层)"},
        "jing_zi_chan_raw_float": {"TDX-eltdx(适配层)"},
        "liu_dong_fu_zhai_raw_float": {"TDX-eltdx(适配层)"},
        "liu_dong_zi_chan_raw_float": {"TDX-eltdx(适配层)"},
        "wu_xing_zi_chan_raw_float": {"TDX-eltdx(适配层)"},
        "zi_ben_gong_ji_jin_raw_float": {"TDX-eltdx(适配层)"},
        "bao_liu_2_raw_float": {"TDX-eltdx(适配层)"},
        "cun_huo_raw_float": {"TDX-eltdx(适配层)"},
        "jing_ying_xian_jin_liu_raw_float": {"TDX-eltdx(适配层)"},
        "li_run_zong_he_raw_float": {"TDX-eltdx(适配层)"},
        "mei_gu_jing_zi_chan_raw_float": {"TDX-eltdx(适配层)"},
        "shui_hou_li_run_raw_float": {"TDX-eltdx(适配层)"},
        "tou_zi_shou_yu_raw_float": {"TDX-eltdx(适配层)"},
        "wei_fen_li_run_raw_float": {"TDX-eltdx(适配层)"},
        "ying_ye_li_run_raw_float": {"TDX-eltdx(适配层)"},
        "ying_shou_zhang_kuan_raw_float": {"TDX-eltdx(适配层)"},
        "zhu_ying_li_run_raw_float": {"TDX-eltdx(适配层)"},
        "zhu_ying_shou_ru_raw_float": {"TDX-eltdx(适配层)"},
        "zong_xian_jin_liu_raw_float": {"TDX-eltdx(适配层)"},
        "open": {"TDX-eltdx(适配层)"},
        "high": {"TDX-eltdx(适配层)"},
        "low": {"TDX-eltdx(适配层)"},
        "close": {"TDX-eltdx(适配层)"},
        "time": {"TDX-eltdx(适配层)"},
        "suspend_major_event_date": {"ZHB-tipinfo"},
        "circulating_shares": {"TDX(双命名源)"},
        "total_shares": {"TDX(双命名源)"},
        "total_assets_yuan": {"TDX(双命名源)"},
        "net_profit_yuan": {"TDX(双命名源)"},
        "netamount": {"新浪(扩展API)"},
        "fenhong": {"TDX(双命名源)"},
        "peigujia": {"TDX(双命名源)"},
        "songzhuangu": {"TDX(双命名源)"},
        "peigu": {"TDX(双命名源)"},
        "open_price_milli": {"TDX-eltdx(适配层)"},
        "high_price_milli": {"TDX-eltdx(适配层)"},
        "low_price_milli": {"TDX-eltdx(适配层)"},
        "close_price_milli": {"TDX-eltdx(适配层)"},
        "last_close_price_milli": {"TDX-eltdx(适配层)"},
        "volume_lots": {"TDX-eltdx(适配层)"},
        "volume_wire_value": {"TDX-eltdx(适配层)"},
        "volume_hand": {"TDX-eltdx(适配层)"},
        "up_count": {"TDX-eltdx(适配层)"},
        "down_count": {"TDX-eltdx(适配层)"},
        "open_delta_raw": {"TDX-eltdx(适配层)"},
        "high_delta_raw": {"TDX-eltdx(适配层)"},
        "low_delta_raw": {"TDX-eltdx(适配层)"},
        "close_delta_raw": {"TDX-eltdx(适配层)"},
        "total_hand": {"TDX-eltdx(适配层)"},
        "current_hand": {"TDX-eltdx(适配层)"},
        "inside_dish": {"TDX-eltdx(适配层)"},
        "outer_disc": {"TDX-eltdx(适配层)"},
        "open_amount": {"TDX-eltdx(适配层)"},
        "open_amount_yuan": {"TDX-eltdx(适配层)"},
        "last_price": {"TDX-eltdx(适配层)"},
        "pre_close_price": {"TDX-eltdx(适配层)"},
        "open_price": {"TDX-eltdx(适配层)"},
        "high_price": {"TDX-eltdx(适配层)"},
        "low_price": {"TDX-eltdx(适配层)"},
        "bid1": {"TDX-eltdx(适配层)"},
        "ask1": {"TDX-eltdx(适配层)"},
        "bid_vol1": {"TDX-eltdx(适配层)"},
        "ask_vol1": {"TDX-eltdx(适配层)"},
        "change_pct": {"TDX-eltdx(适配层)"},
        "depth": {"TDX-eltdx(适配层)"},
        "min2_amount": {"TDX-eltdx(适配层)"},
        "rise_speed": {"TDX-eltdx(适配层)"},
        "short_turnover": {"TDX-eltdx(适配层)"},
        "vol_rise_speed": {"TDX-eltdx(适配层)"},
        "trade": {"新浪(扩展API)"},
        "turnover": {"新浪(扩展API)"},
        "alignment_status": {"TDX-eltdx(适配层)"},
        "auction_prev_volume_ratio": {"TDX-eltdx(适配层)"},
        "beta_60d": {"TDX-eltdx(适配层)"},
        "float_market_value": {"TDX-eltdx(适配层)"},
        "float_shares": {"TDX-eltdx(适配层)"},
        "free_float_market_value": {"TDX-eltdx(适配层)"},
        "free_float_shares": {"TDX-eltdx(适配层)"},
        "ladder_level": {"TDX-eltdx(适配层)"},
        "limit_board_text": {"TDX-eltdx(适配层)"},
        "limit_stat_days": {"TDX-eltdx(适配层)"},
        "limit_status": {"TDX-eltdx(适配层)"},
        "limit_up_count_in_stat_days": {"TDX-eltdx(适配层)"},
        "limit_up_streak_days": {"TDX-eltdx(适配层)"},
        "locked_amount": {"TDX-eltdx(适配层)"},
        "open_change_pct": {"TDX-eltdx(适配层)"},
        "open_prev_amount_ratio": {"TDX-eltdx(适配层)"},
        "open_prev_seal_ratio": {"TDX-eltdx(适配层)"},
        "open_turnover_z": {"TDX-eltdx(适配层)"},
        "open_volume_hand": {"TDX-eltdx(适配层)"},
        "open_volume_ratio": {"TDX-eltdx(适配层)"},
        "opening_rush": {"TDX-eltdx(适配层)"},
        "pe_ttm": {"TDX-eltdx(适配层)"},
        "prev2_seal_amount": {"TDX-eltdx(适配层)"},
        "prev_amount": {"TDX-eltdx(适配层)"},
        "prev_open_amount": {"TDX-eltdx(适配层)"},
        "prev_open_volume_hand": {"TDX-eltdx(适配层)"},
        "prev_seal_amount": {"TDX-eltdx(适配层)"},
        "previous_trade_date": {"TDX-eltdx(适配层)"},
        "seal_amount": {"TDX-eltdx(适配层)"},
        "seal_prev_ratio": {"TDX-eltdx(适配层)"},
        "seal_to_amount_ratio": {"TDX-eltdx(适配层)"},
        "seal_to_float_ratio": {"TDX-eltdx(适配层)"},
        "stats_date": {"TDX-eltdx(适配层)"},
        "target_trade_date": {"TDX-eltdx(适配层)"},
        "year_limit_up_days": {"TDX-eltdx(适配层)"},
        "eltdx_auction_prev_volume_ratio": {"TDX-eltdx(适配层)"},
        "eltdx_has_shortline": {"TDX-eltdx(适配层)"},
        "eltdx_ladder_level": {"TDX-eltdx(适配层)"},
        "eltdx_limit_board_text": {"TDX-eltdx(适配层)"},
        "eltdx_limit_up_streak_days": {"TDX-eltdx(适配层)"},
        "eltdx_open_change_pct": {"TDX-eltdx(适配层)"},
        "eltdx_open_prev_amount_ratio": {"TDX-eltdx(适配层)"},
        "eltdx_open_turnover_z": {"TDX-eltdx(适配层)"},
        "eltdx_open_volume_ratio": {"TDX-eltdx(适配层)"},
        "eltdx_seal_amount": {"TDX-eltdx(适配层)"},
        "eltdx_seal_to_float_ratio": {"TDX-eltdx(适配层)"},
        "bid2": {"TDX(双命名源)"},
        "bid3": {"TDX(双命名源)"},
        "bid4": {"TDX(双命名源)"},
        "bid5": {"TDX(双命名源)"},
        "ask2": {"TDX(双命名源)"},
        "ask3": {"TDX(双命名源)"},
        "ask4": {"TDX(双命名源)"},
        "ask5": {"TDX(双命名源)"},
        "zhuying_shouru": {"TDX(双命名源)"},
        "zong_xianjinliu": {"TDX(双命名源)"},
    }


def test_source_contract_parity_rejects_registry_adjudication_tampering():
    registry = copy.deepcopy(registry_parity.fra.load_registry())
    records = registry_parity.fra.source_field_records(registry)
    target = next(
        row for row in records if row["source"] == "TDX(双命名源)" and row["code"] == "bid2"
    )
    target["adjudications"][0]["rationale"] = "tampered"

    _, _, problems = registry_parity._validated_source_contract_adjudications(
        registry, registry_parity.fra.source_field_records(registry), set(), set()
    )

    assert any("注册表定案记录与决策文件不一致" in problem for problem in problems)


def test_adjudication_plan_validates_target_source_and_allows_runtime_alias_paths():
    pair = ("开盘啦(kpl_limit_up_detail)", "zt_time")
    target = {"source": pair[0], "code": pair[1]}
    candidate = {"left": "kpl.raw_columns.col_04", "right": "kph.limit_time"}
    adjudication = {
        "id": "review-1",
        "candidate": candidate,
        "reviewed_on": "2026-10-23",
        "target": target,
    }
    plan = {
        "report": "20261023/20261023_collision_report.json",
        "reviewed_on": "2026-10-23",
        "decisions": [
            {
                "id": "review-1",
                "action": "verify",
                "candidate": candidate,
                "target": target,
            }
        ],
    }
    problems = []

    matched = registry_parity._match_adjudication_plan(
        pair,
        adjudication,
        "review-1",
        "20261023/20261023_collision_report.json",
        plan,
        problems,
    )

    assert matched == candidate
    assert problems == []


def test_adjudication_plan_rejects_candidate_from_a_different_source():
    pair = ("另一来源", "[11]")
    candidate = {"left": "sina.[11]", "right": "tdx.quote_raw.bid1"}
    adjudication = {
        "id": "review-2",
        "candidate": candidate,
        "reviewed_on": "2026-10-23",
    }
    plan = {
        "report": "20261023/report.json",
        "reviewed_on": "2026-10-23",
        "decisions": [
            {
                "id": "review-2",
                "action": "verify",
                "candidate": candidate,
                "target": {"source": "新浪(hq.sinajs)", "code": "[11]"},
            }
        ],
    }
    problems = []

    matched = registry_parity._match_adjudication_plan(
        pair, adjudication, "review-2", "20261023/report.json", plan, problems
    )

    assert matched is None
    assert any("目标身份" in problem for problem in problems)


def test_adjudication_validation_uses_persisted_decision_without_local_full_report(
    tmp_path: Path,
):
    pair = ("TDX(双命名源)", "amount")
    decision_id = "review-with-local-report"
    report = "20261023/20261023_collision_report.json"
    candidate = {"left": "tdx.quote_raw.amount", "right": "fuyao.snapshot.turnover"}
    target = {"source": pair[0], "code": pair[1]}
    verification_root = tmp_path / "field_verification"
    decision_path = verification_root / "adjudications" / "decision.json"
    decision_path.parent.mkdir(parents=True)
    decision_path.write_text(
        json.dumps(
            {
                "report": report,
                "reviewed_on": "2026-10-23",
                "decisions": [
                    {
                        "id": decision_id,
                        "action": "verify",
                        "candidate": candidate,
                        "target": target,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    adjudication = {
        "id": decision_id,
        "action": "verify",
        "status": "verified",
        "decision_file": "adjudications/decision.json",
        "report": report,
        "candidate": candidate,
        "reviewed_on": "2026-10-23",
        "evidence": {"n_days": 3, "n_pairs": 60, "evidence_sources": ["tdx", "fuyao"]},
    }
    row = {
        "canonical": "amount",
        "meaning": "成交额",
        "unit": "元",
        "reference_evidence": [
            {
                "adjudication_id": decision_id,
                "status": "verified",
                "canonical": "amount",
                "meaning": "成交额",
                "unit": "元",
            }
        ],
    }
    problems: list[str] = []

    valid = registry_parity._validate_adjudication_record(
        pair, row, adjudication, verification_root, {}, set(), problems
    )

    assert valid
    assert not (verification_root / report).exists()
    assert problems == []


def test_capture_path_manifest_rejects_pre_retention_evidence(tmp_path: Path):
    evidence_path = (
        tmp_path / "docs" / "field_verification" / "20261014" / "raw_market_sources.json"
    )
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text(
        json.dumps({"cls_market_emotion": {"market_degree": 1}}), encoding="utf-8"
    )
    source = "市场源(market_sources)"
    code = "cls_market_emotion"
    manifest = {
        "schema_version": 1,
        "purpose": "Reject capture evidence before the retained-data floor.",
        "entries": [
            {
                "source": source,
                "code": code,
                "evidence_file": ("docs/field_verification/20261014/raw_market_sources.json"),
                "capture_path": "/cls_market_emotion",
            }
        ],
    }
    records = [
        {
            "source": source,
            "code": code,
            "status": "verified",
            "status_resolution": "registry_status_only_single_source",
            "canonical": "",
            "meaning": "",
            "unit": "",
            "reference_evidence": [],
        }
    ]

    pairs, problems = registry_parity._validate_capture_path_manifest(
        manifest,
        records,
        {source},
        set(),
        tmp_path,
        date(2026, 10, 15),
    )

    assert pairs == set()
    assert any("早于保留起始日" in problem for problem in problems)


def test_capture_evidence_preserves_adjudicated_status_and_traceability():
    registry = registry_parity.fra.load_registry()
    captured = [row for row in registry["source_fields"] if "capture_evidence" in row]

    assert len(captured) == 40
    verified = [row for row in captured if row["status"] == "verified"]
    assert {(row["source"], row["code"]) for row in verified} == {
        ("TDX(双命名源)", "ask1_vol"),
        ("开盘啦(kpl_limit_up_detail)", "raw_columns.col_13"),
        ("开盘啦(kpl_limit_up_detail)", "raw_columns.col_15"),
        ("开盘啦(kpl_limit_up_detail)", "raw_columns.col_19"),
        ("开盘啦(kpl_limit_up_detail)", "raw_columns.col_21"),
        ("开盘啦(kpl_limit_up_detail)", "raw_columns.col_22"),
    }
    ask1_vol_field = next(row for row in verified if row["code"] == "ask1_vol")
    assert ask1_vol_field["canonical"] == "ask1_vol"
    assert ask1_vol_field["meaning"] == "卖一量"
    assert ask1_vol_field["unit"] == "手"
    assert ask1_vol_field["status_resolution"] == "manual_collision_adjudication"
    assert (
        "historical-recrack-tdx-ask1-vol-20261107"
        in ask1_vol_field["status_evidence"]["adjudication_ids"]
    )
    assert ask1_vol_field["capture_evidence"] == [
        {
            "file": "docs/field_verification/20261016/raw_tdx.json",
            "path": "stocks.[*].quote_raw.ask1_vol",
        }
    ]
    sector_field = next(row for row in verified if row["code"] == "raw_columns.col_19")
    assert sector_field["status_resolution"] == "verified_by_empirical_addendum"
    assert sector_field["canonical"] == "sector_code"
    assert sector_field["status_evidence"]["evidence_file"] == (
        "docs/field_verification/adjudications/20261105_kpl_sector_code_semantics.md"
    )
    actual_float_mv = next(row for row in verified if row["code"] == "raw_columns.col_13")
    assert actual_float_mv["canonical"] == "actual_float_mv"
    assert actual_float_mv["meaning"] == "实际流通市值"
    assert actual_float_mv["unit"] == "元"
    assert actual_float_mv["status_resolution"] == "verified_by_empirical_addendum"
    assert actual_float_mv["status_evidence"]["evidence_file"] == (
        "docs/field_verification/adjudications/20261110_kpl_col13_actual_float_mv.md"
    )
    assert actual_float_mv["capture_evidence"] == [
        {
            "file": "docs/field_verification/20261109/raw_kpl.json",
            "path": "stocks.[*].raw_columns.col_13",
        }
    ]

    unverified = [row for row in captured if row["status"] == "unverified"]
    assert len(unverified) == 34
    for row in unverified:
        assert row["status"] == "unverified"
        assert not row["canonical"]
        assert not row["meaning"]
        assert not row["unit"]
    for row in captured:
        assert row["capture_evidence"]
        for evidence in row["capture_evidence"]:
            assert set(evidence) == {"file", "path"}
            assert (Path(registry_parity.REPO_ROOT) / evidence["file"]).is_file()
