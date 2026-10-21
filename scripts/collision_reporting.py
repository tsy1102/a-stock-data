from __future__ import annotations

from typing import Any

from scripts import collision_candidate_reviews as CCR


def append_source_coverage_report(markdown, source_coverage):
    """Render complete per-source contract, observed-data, and collision coverage."""
    lines = [markdown.rstrip(), "", "## 来源字段覆盖与碰撞参与", ""]
    lines.append(
        "_窗口字段值样本是经日期筛选、重复折叠和快照择优后载入的非空值；"
        "右侧比较次数另受字段类型及来源规则筛选。官方契约字段须有逐字段审定证据，"
        "契约语义本身不证明底层数据来源独立。_"
    )
    lines.extend(
        [
            "",
            "| 来源 | 已确认字段 | 契约已确认 | 契约锚 | 独立锚 | L1-C 锚 | 窗口字段 / 字段值样本 / 交易日 |",
            "|:--|--:|--:|--:|--:|--:|--:|",
        ]
    )
    for row in source_coverage:
        lines.append(
            "| {source} | {verified_field_count} | {official_contract_verified_field_count} | "
            "{official_contract_anchor_field_count} | {independent_anchor_field_count} | "
            "{contract_only_anchor_field_count} | {observed_window_field_count} / "
            "{observed_window_field_value_count} / {observed_window_trading_day_count} |".format(
                **row
            )
        )
    if not source_coverage:
        lines.append("| _无来源数据_ | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |")
    lines.extend(
        [
            "",
            "| 来源 | 破解目标 | 比较字段 | 作目标比较 | 作右侧比较 | L1-C 锚比较 | L1 / L1-C / L4 关系 | 方法候选涉及 |",
            "|:--|--:|--:|--:|--:|--:|--:|--:|",
        ]
    )
    for row in source_coverage:
        lines.append(
            "| {source} | {cracking_target_field_count} | {comparison_field_count} | "
            "{comparisons_as_target} | {comparisons_as_right_field} | {L1_C_anchor_comparisons} | "
            "{L1_relation_count} / {L1_C_relation_count} / {L4_relation_count} | "
            "{method_candidate_pair_count} |".format(**row)
        )
    if not source_coverage:
        lines.append("| _无来源数据_ | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |")
    lines.append("")
    return "\n".join(lines) + "\n"


def append_source_identity_report(report_md, result):
    """Append active REST and retired legacy FTShare identities to the report."""
    lines = [report_md.rstrip(), "", "## 来源身份状态（不参与字段语义定案）", ""]
    if isinstance(result, dict) and result.get("active_runtime_source") == "ftshare_rest":
        lines.append(
            "_FTShare 公共 REST 接口已进入日常采集；官方字段契约作为语义锚，"
            "底层数据提供方仍未确认。与其匹配的强候选列在 L1-C，不混入独立来源 L1。_"
        )
        lines.append("_旧私有托管 MCP 采集器已退役，历史样本仅供 `--all` / `--exploratory` 追溯。_")
    else:
        lines.append("_当前没有运行来源身份核验；历史核验摘要见每日辅助证据。_")
    lines.append("")
    return "\n".join(lines) + "\n"


def append_contract_anchor_candidates(report_md, candidates):
    """Render contract-backed candidates without presenting them as independent-source L1."""
    lines = [
        report_md.rstrip(),
        "",
        f"## 官方契约锚候选 L1-C（{len(candidates)}）",
        "",
        "_L1-C 使用逐字段审定的官方接口契约语义作锚，并满足多日数值匹配门槛；"
        "仅当该接口底层数据来源独立性未确认时才列入此处，不属于独立来源 L1，也不自动定案。_",
        "",
    ]
    if candidates:
        lines.extend(
            [
                "| 左字段（待确认） | 官方契约字段 | 等级 | 命中率 | 交易日数 | 样本 | 信息样本 | 比值 | hub | registry |",
                "|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|",
            ]
        )
        lines.extend(_l1_row(candidate) for candidate in candidates)
    else:
        lines.append("_本轮无达到多日门槛的官方契约锚候选。_")
    lines.append("")
    return "\n".join(lines) + "\n"


def append_research_state_report(report_md: str, state_summary: dict) -> str:
    """Show research carry-forward status without promoting candidates."""
    lines = [report_md.rstrip(), "", "## 探索候选持续跟踪", ""]
    lines.append(
        f"研究台账：`{state_summary.get('path', 'collision_research_state.json.gz')}`；"
        f"累计历史跟踪候选对 {state_summary.get('tracked_candidate_pairs', 0)}，"
        f"本报告候选对 {state_summary.get('current_candidate_pairs', 0)}，"
        f"历史复现 {state_summary.get('previously_tracked_pairs', 0)}，"
        f"新发现 {state_summary.get('new_candidate_pairs', 0)}。"
    )
    lines.append(
        "台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，"
        "不会自动改变字段状态、碰撞锚或主字典。新报告只将 `actionable_L1`、L4 和主动方法候选"
        "写入待研究队列；已登记关系的复验单独展示，历史跟踪记录不会被删除。"
    )
    if state_summary.get("persisted") is False:
        lines.append("_本轮台账没有写入；请查看诊断，已有台账保持原样。_")
    lines.append("")
    return "\n".join(lines) + "\n"


def _l1_row(p):
    return (
        f"| `{p['left']}` | `{p['right']}` | {p['level']} | "
        f"{p['overall_hit']:.2%} | {p['n_days']} | {p['n_pairs']} | "
        f"{p.get('n_informative_pairs') if p.get('n_informative_pairs') is not None else '—'} | "
        f"{p.get('ratio') or '-'} | {'⚠' if p.get('hub_flag') else ''} | "
        f"{'✅' if p.get('in_registry') else '—'} |"
    )


def append_candidate_triage_report(
    markdown: str,
    triage: dict[str, Any],
    frontier: list[dict[str, Any]],
    formulas: list[dict[str, Any]],
    controls: dict[str, Any],
    max_method_candidates: int = 500,
) -> str:
    summary = triage.get("summary", {})
    targets = triage.get("targets", [])
    lines = ["\n## 候选覆盖、公式与下一步采样\n"]
    lines.append(
        "本节用于定位证据缺口和安排后续取样。相关性、公式与样本优先级均为探索候选；"
        "不会改变 L1/L1-U 门槛、来源独立性或主字典。\n"
    )
    lines.append(
        f"- 未知目标 {summary.get('target_count', 0)} 个；其中有方法候选 "
        f"{summary.get('targets_with_method_candidates', 0)} 个、无候选 "
        f"{summary.get('targets_without_method_candidates', 0)} 个；多候选目标 "
        f"{summary.get('targets_with_multiple_candidates', 0)} 个。"
    )
    lines.append(
        f"- 方法候选生成 {summary.get('candidate_pairs_generated', 0)} 条；"
        f"全局详细项保留 {summary.get('global_details_retained', 0)}/"
        f"{summary.get('global_detail_limit', max_method_candidates)}，"
        f"另按目标字段保留 {summary.get('field_frontier_details_retained', 0)} 条；"
        f"完整明细 {summary.get('method_candidate_inventory_count', 0)} 条在 JSON "
        "`method_candidate_inventory`；"
        f"未归档明细 {summary.get('candidate_pairs_without_full_detail', 0)} 条。"
    )
    field_coverage = summary.get("field_coverage", {})
    lines.append(
        f"- 字段覆盖详情：{field_coverage.get('detail_status', 'unavailable')}；"
        f"覆盖身份 {field_coverage.get('coverage_identity_count', 0)}，"
        f"读取 {field_coverage.get('coverage_detail_files', 0)} 份本地索引。"
    )

    status_labels = {
        "formula_candidate_needs_independent_review": "公式候选待独立复核",
        "multiple_method_candidates_need_discrimination": "存在多个候选，需区分",
        "single_method_candidate_needs_external_check": "单候选，需外部证据",
        "source_lineage_gap": "来源血缘缺口",
        "field_coverage_identity_unmapped": "覆盖字段未映射到运行路径",
        "independent_source_coverage_gap": "独立来源覆盖缺口",
        "joint_sample_coverage_gap": "共同样本不足",
        "no_current_method_signal": "当前方法未发现信号",
        "no_eligible_comparison": "无可用独立对比",
    }
    lines.append("\n### 优先处理字段\n")
    lines.append(
        "| 未知字段 | 当前诊断 | 独立对比/候选数 | 独立锚家族/本源日期 | 建议复核股票 | 最强候选线索 |"
    )
    lines.append("|:--|:--|--:|:--|:--|:--|")
    for target in targets[:50]:
        coverage = target.get("coverage", {})
        families = coverage.get("independent_anchor_families", [])
        dates = coverage.get("source_as_of_days", [])
        candidate_names = [
            (
                f"{item.get('right')} "
                f"({','.join(m.get('method', '') for m in item.get('methods', []))})"
            )
            for item in target.get("top_candidates", [])
        ]
        candidate_text = "; ".join(candidate_names) or "—"
        formula_text = "; ".join(
            item.get("formula", "") for item in target.get("formula_candidates", [])
        )
        evidence_text = (candidate_text + ("; " + formula_text if formula_text else ""))[:240]
        sample = target.get("next_sample") or {}
        sample_text = (
            f"{sample.get('stock_code')} ({sample.get('normalized_prediction_spread')})"
            if sample.get("status") == "prioritize_recheck"
            else sample.get("status", "—")
        )
        pair_counts = target.get("pair_counts", {})
        comparisons = (
            f"{pair_counts.get('independent_pairs', 0)} / {target.get('candidate_count', 0)}"
        )
        anchor_text = f"{len(families)} 家族 / {coverage.get('independent_anchor_pairs', 0)} 对"
        coverage_text = (
            f"{anchor_text} / 本源 {len(dates)} 日"
            if coverage.get("status") == "available"
            else f"{anchor_text} / 本源详情不可用"
        )
        label = status_labels.get(target.get("status"), target.get("status", "未知"))
        lines.append(
            f"| `{target.get('left', '')}` | {label} | {comparisons} | "
            f"{coverage_text} | {sample_text} | {evidence_text} |"
        )
    if len(targets) > 50:
        lines.append(f"\n_此表显示优先级最高的 50 / 共 {len(targets)} 个目标；完整清单见 JSON。_\n")

    if frontier:
        lines.append(f"\n### 补足全局截断的字段候选（{len(frontier)}）\n")
        lines.append("| 未知字段 | 候选字段 | 方法 | 样本 | 日期 | 来源 |")
        lines.append("|:--|:--|:--|--:|:--|:--|")
        for candidate in frontier[:100]:
            lines.append(
                f"| `{candidate.get('left')}` | `{candidate.get('right')}` | "
                f"{', '.join(item.get('method', '') for item in candidate.get('methods', []))} | "
                f"{candidate.get('sample_count', 0)} | "
                f"{', '.join(candidate.get('sample_dates', [])[:5])} | "
                f"{', '.join(candidate.get('evidence_sources', []))} |"
            )
        if len(frontier) > 100:
            lines.append(f"\n_仅显示前 100 / 共 {len(frontier)} 条字段前沿候选。_\n")

    if formulas:
        lines.append(f"\n### 双输入公式候选（{len(formulas)}）\n")
        lines.append(
            "公式使用按股票代码分组的留出样本验证；至少 3 个留出股票，验证 R²≥0.985、"
            "误差不超过训练目标标准差的 5%，并要求优于最佳单输入线性模型至少 0.05。"
            "这些阈值只筛选探索候选，不构成语义证明。\n"
        )
        lines.append("| 目标字段 | 候选公式 | 留出 R² | 相对误差尺度 | 验证样本/股票 |")
        lines.append("|:--|:--|--:|--:|--:|")
        for formula in formulas[:50]:
            lines.append(
                f"| `{formula.get('left')}` | `{formula.get('formula')}` | "
                f"{formula.get('validation_r2')} | {formula.get('normalized_rmse')} | "
                f"{formula.get('validation_samples')}/{formula.get('validation_stocks')} |"
            )
        if len(formulas) > 50:
            lines.append(f"\n_仅显示前 50 / 共 {len(formulas)} 条公式候选。_\n")
    else:
        lines.append(
            f"\n### 双输入公式候选\n本轮未发现通过留出筛选的公式候选；"
            f"测试组合 {summary.get('formula_combinations_tested', 0)} 个。\n"
        )

    positive = controls.get("positive_control", {})
    negative = controls.get("negative_control", {})
    lines.append("\n### 已知映射与已证伪关系的候选校准\n")
    lines.append(
        f"- 已登记正向对照：当前窗口有 {positive.get('eligible_numeric_pairs', 0)} 组独立数值关系可评估，"
        f"{positive.get('with_method_signal', 0)} 组被方法候选识别；样本不足 "
        f"{positive.get('insufficient_numeric_samples', 0)} 组。此计数仅检查方法覆盖，不是准确率。"
    )
    lines.append(
        f"- 已证伪负向对照：数值关系 {negative.get('numeric_refuted_pairs', 0)} 组，"
        f"其中仍有方法信号 {negative.get('with_method_signal', 0)} 组；这些信号被隔离，不进入普通候选。"
    )
    failed_sources = []
    for source, status in summary.get("capture_source_statuses", {}).items():
        if status.get("non_ok_dates"):
            failed_sources.append(
                f"{source}: {', '.join(status['non_ok_dates'][-3:])} "
                f"({status.get('status_counts', {})})"
            )
    if failed_sources:
        lines.append("\n### 采集覆盖异常源\n")
        lines.extend(f"- {item}" for item in failed_sources[:30])
        if len(failed_sources) > 30:
            lines.append(
                f"- 另有 {len(failed_sources) - 30} 个来源见 JSON "
                "`candidate_triage.summary.capture_source_statuses`。"
            )
    return markdown.rstrip() + "\n" + "\n".join(lines) + "\n"


def build_report_completeness(report_data: dict[str, Any]) -> dict[str, Any]:
    """Reconcile complete JSON evidence against intentionally summarized Markdown views."""
    triage = report_data.get("candidate_triage")
    triage = triage if isinstance(triage, dict) else {}
    triage_summary = triage.get("summary")
    triage_summary = triage_summary if isinstance(triage_summary, dict) else {}
    targets = triage.get("targets")
    if not isinstance(targets, list):
        targets = []

    section_specs = {
        "L1": (report_data.get("L1"), None, "完整 L1 关系清单"),
        "L1-C": (report_data.get("L1-C"), None, "完整官方契约锚候选清单"),
        "actionable_L1": (report_data.get("actionable_L1"), None, "完整新候选清单"),
        "mapped_pair_revalidations": (
            report_data.get("mapped_pair_revalidations"),
            None,
            "完整已登记映射复验清单",
        ),
        "L4": (report_data.get("L4"), 60, "完整 L4 清单"),
        "source_coverage": (
            report_data.get("source_coverage"),
            None,
            "完整逐来源契约定义、窗口观察与碰撞参与统计",
        ),
        "guardrail_hits": (
            report_data.get("guardrail_hits"),
            None,
            "完整证伪护栏命中清单",
        ),
        "method_candidates": (
            report_data.get("method_candidates"),
            100,
            "全局排序摘要；完整清单见 method_candidate_inventory",
        ),
        "method_candidate_inventory": (
            report_data.get("method_candidate_inventory"),
            0,
            "完整方法候选明细；仅存于 JSON",
        ),
        "method_candidate_frontier": (
            report_data.get("method_candidate_frontier"),
            100,
            "按目标补充的前沿清单；完整清单见 JSON",
        ),
        "candidate_triage.targets": (
            targets,
            50,
            "逐个未知目标的完整诊断清单；完整清单见 JSON",
        ),
        "formula_candidates": (
            report_data.get("formula_candidates"),
            50,
            "完整通过筛选的公式候选；完整清单见 JSON",
        ),
        "diagnostics": (report_data.get("diagnostics"), 100, "完整告警清单"),
    }

    issues = []
    sections = {}
    markdown_omissions = []
    for name, (records, markdown_limit, scope) in section_specs.items():
        if not isinstance(records, list):
            issues.append(f"{name}: missing_or_invalid_json_list")
            records = []
        record_count = len(records)
        visible_count = (
            record_count if markdown_limit is None else min(record_count, markdown_limit)
        )
        omitted_count = record_count - visible_count
        if omitted_count:
            markdown_omissions.append(
                {
                    "section": name,
                    "available": record_count,
                    "visible": visible_count,
                    "omitted_from_markdown": omitted_count,
                }
            )
        sections[name] = {
            "json_record_count": record_count,
            "markdown_display_limit": markdown_limit,
            "markdown_display_count": visible_count,
            "markdown_omitted_count": omitted_count,
            "detail_scope": scope,
        }

    generated_count = report_data.get("method_candidate_count")
    if type(generated_count) is not int or generated_count < 0:
        generated_count = 0
        issues.append("method_candidate_count: missing_or_invalid")
    inventory = report_data.get("method_candidate_inventory")
    if not isinstance(inventory, list):
        inventory = []
    candidate_pairs = []
    invalid_pair_identity_count = 0
    for row in inventory:
        if not isinstance(row, dict):
            invalid_pair_identity_count += 1
            continue
        left, right = row.get("left"), row.get("right")
        if not isinstance(left, str) or not left or not isinstance(right, str) or not right:
            invalid_pair_identity_count += 1
            continue
        candidate_pairs.append((left, right))
    unique_pair_count = len(set(candidate_pairs))
    missing_detail_count = max(0, generated_count - len(inventory))
    excess_detail_count = max(0, len(inventory) - generated_count)
    duplicate_pair_count = len(candidate_pairs) - unique_pair_count

    summary_rows = report_data.get("method_candidates")
    if not isinstance(summary_rows, list):
        summary_rows = []
    summary_pairs = []
    invalid_summary_pair_count = 0
    for row in summary_rows:
        if not isinstance(row, dict):
            invalid_summary_pair_count += 1
            continue
        left, right = row.get("left"), row.get("right")
        if isinstance(left, str) and left and isinstance(right, str) and right:
            summary_pairs.append((left, right))
        else:
            invalid_summary_pair_count += 1
    if invalid_summary_pair_count or summary_pairs != candidate_pairs[: len(summary_pairs)]:
        issues.append("method_candidates: ranked_summary_not_a_prefix_of_full_inventory")

    frontier_rows = report_data.get("method_candidate_frontier")
    if not isinstance(frontier_rows, list):
        frontier_rows = []
    frontier_pairs = []
    invalid_frontier_pair_count = 0
    for row in frontier_rows:
        if not isinstance(row, dict):
            invalid_frontier_pair_count += 1
            continue
        left, right = row.get("left"), row.get("right")
        if isinstance(left, str) and left and isinstance(right, str) and right:
            frontier_pairs.append((left, right))
        else:
            invalid_frontier_pair_count += 1
    inventory_pair_set = set(candidate_pairs)
    summary_pair_set = set(summary_pairs)
    if (
        invalid_frontier_pair_count
        or len({left for left, _ in frontier_pairs}) != len(frontier_pairs)
        or any(
            pair not in inventory_pair_set or pair in summary_pair_set for pair in frontier_pairs
        )
    ):
        issues.append("method_candidate_frontier: pair_identity_mismatch")

    if (
        missing_detail_count
        or excess_detail_count
        or duplicate_pair_count
        or invalid_pair_identity_count
    ):
        issues.append("method_candidate_inventory: count_or_pair_identity_mismatch")

    expected_target_count = triage_summary.get("target_count")
    if type(expected_target_count) is not int or expected_target_count != len(targets):
        issues.append("candidate_triage.targets: count_mismatch")
    target_candidate_count_sum = 0
    invalid_target_candidate_counts = 0
    for target in targets:
        count = target.get("candidate_count") if isinstance(target, dict) else None
        if type(count) is not int or count < 0:
            invalid_target_candidate_counts += 1
        else:
            target_candidate_count_sum += count
    if invalid_target_candidate_counts or target_candidate_count_sum != generated_count:
        issues.append("candidate_triage.targets: candidate_count_mismatch")

    candidate_review_validation = None
    if report_data.get("schema_version", 0) >= 5 or "candidate_review" in report_data:
        candidate_review_validation = CCR.validate_report_summary(report_data)
        if candidate_review_validation.get("status") != "complete":
            issues.extend(
                f"candidate_review:{issue}"
                for issue in candidate_review_validation.get("issues", [])
            )

    top_level_sections = {}
    for name, value in report_data.items():
        if name == "report_completeness":
            continue
        if name not in sections:
            sections[name] = {
                "json_record_count": len(value) if isinstance(value, (list, dict)) else None,
                "markdown_display_limit": None,
                "markdown_display_count": None,
                "markdown_omitted_count": None,
                "detail_scope": "完整 JSON 顶层内容；需按实际结构逐项审阅",
            }
        top_level_sections[name] = {
            "value_type": type(value).__name__,
            "record_count": len(value) if isinstance(value, (list, dict)) else None,
        }

    completeness = {
        "schema_version": 1,
        "status": "complete" if not issues else "incomplete",
        "markdown_is_summary": True,
        "top_level_sections": top_level_sections,
        "method_candidate_inventory": {
            "generated_count": generated_count,
            "saved_count": len(inventory),
            "unique_pair_count": unique_pair_count,
            "missing_detail_count": missing_detail_count,
            "excess_detail_count": excess_detail_count,
            "duplicate_pair_count": duplicate_pair_count,
            "invalid_pair_identity_count": invalid_pair_identity_count,
            "target_candidate_count_sum": target_candidate_count_sum,
            "invalid_target_candidate_count_rows": invalid_target_candidate_counts,
            "json_key": "method_candidate_inventory",
        },
        "sections": sections,
        "markdown_omissions": markdown_omissions,
        "issues": issues,
    }
    if candidate_review_validation is not None:
        completeness["candidate_review"] = candidate_review_validation
        candidate_review = report_data.get("candidate_review", {})
        human_review = candidate_review.get("human_review", {})
        reviewed_candidates = human_review.get("reviewed_candidates", [])
        if not isinstance(reviewed_candidates, list):
            reviewed_candidates = []
        visible = 0
        omitted = len(reviewed_candidates)
        sections["candidate_review.human_review.reviewed_candidates"] = {
            "json_record_count": len(reviewed_candidates),
            "markdown_display_limit": 0,
            "markdown_display_count": visible,
            "markdown_omitted_count": omitted,
            "detail_scope": "完整审阅事件摘要；仅存于 JSON，审阅历史台账为权威来源",
        }
        if omitted:
            markdown_omissions.append(
                {
                    "section": "candidate_review.human_review.reviewed_candidates",
                    "available": omitted,
                    "visible": visible,
                    "omitted_from_markdown": omitted,
                }
            )
        completeness["sections"] = sections
        completeness["markdown_omissions"] = markdown_omissions
        completeness["status"] = "complete" if not issues else "incomplete"
    return completeness


def append_report_completeness_report(markdown: str, completeness: dict[str, Any]) -> str:
    """Expose truncation and completeness checks at the end of the human-readable report."""
    inventory = completeness.get("method_candidate_inventory", {})
    lines = ["\n## 报告完整性与审阅范围\n"]
    lines.append(
        f"- 机器可读完整性：`{completeness.get('status', 'incomplete')}`；"
        f"方法候选生成 {inventory.get('generated_count', 0)} 条，"
        f"完整明细保存 {inventory.get('saved_count', 0)} 条，"
        f"缺失 {inventory.get('missing_detail_count', 0)} 条，"
        f"多余 {inventory.get('excess_detail_count', 0)} 条，"
        f"重复 {inventory.get('duplicate_pair_count', 0)} 条，"
        f"身份无效 {inventory.get('invalid_pair_identity_count', 0)} 条。"
    )
    lines.append(
        "- 全量方法候选位于同名 JSON 的 `method_candidate_inventory`；"
        "Markdown 的 Top-N 表格是导航摘要，不能代替全量 JSON 审阅。"
    )
    review_validation = completeness.get("candidate_review")
    if isinstance(review_validation, dict):
        lines.append(
            f"- 候选审阅数据对账：`{review_validation.get('status', 'incomplete')}`；"
            f"唯一候选 {review_validation.get('unique_candidate_count', 0)} 个，"
            f"审阅 {review_validation.get('reviewed_count', 0)} 个，"
            f"待处理 {review_validation.get('pending_count', 0)} 个；"
            "人工审阅进度与机器清单完整性分别统计。"
        )
    omissions = completeness.get("markdown_omissions", [])
    if omissions:
        lines.append("- Markdown 未逐行展示、但 JSON 保留的部分：")
        lines.extend(
            f"  - `{item.get('section')}`：展示 {item.get('visible', 0)} / "
            f"{item.get('available', 0)}，摘要省略 {item.get('omitted_from_markdown', 0)} 条。"
            for item in omissions
        )
    issues = completeness.get("issues", [])
    if issues:
        lines.append("- **审阅阻断**：完整性对账失败；不得据此断言无候选、无字段或提交定案。")
        lines.extend(f"  - `{issue}`" for issue in issues)
    else:
        lines.append(
            "- 完整性对账通过；逐目标复核仍须覆盖 JSON 的全部明细，并为每项记录"
            "已检查、重复归并、证据不足或需外部核验的处置。"
        )
    return markdown.rstrip() + "\n" + "\n".join(lines) + "\n"


def build_report_md(
    today,
    window,
    nfields,
    nsamples,
    left_ids,
    l1,
    l4,
    new_count,
    verified,
    guardrail_hits,
    method_candidates=None,
    diagnostics=None,
    event_window=None,
    window_selection=None,
    *,
    hit_rate_l1_ratio: float,
    min_daily_l1: int,
    min_informative_daily_l1: int,
    multi_day_min: int,
):
    # Keep already-registered pairs visible for revalidation, outside the new-candidate queue.
    revalidations = [p for p in l1 if p.get("in_registry", False)]
    actionable = [p for p in l1 if not p.get("in_registry", False)]
    cross = [p for p in actionable if not p.get("same_code")]
    same = [p for p in actionable if p.get("same_code")]
    cross.sort(key=lambda p: (-p["overall_hit"], -p["n_days"]))
    same.sort(key=lambda p: (-p["overall_hit"], -p["n_days"]))
    revalidations.sort(key=lambda p: (-p["overall_hit"], -p["n_days"]))

    L = []
    L.append(f"# 全源对撞报告（{today}）\n")
    if window_selection:
        if window_selection.get("mode") == "all_history":
            L.append("> 交易数据窗口配置：全部历史日期（`--all`）")
        else:
            requested_days = window_selection.get("requested_trading_days")
            L.append(f"> 交易数据窗口配置：近 {requested_days} 个交易日（`--window`）")
    trading_window = f"{window[0]} ~ {window[-1]}" if window else "无有效交易日样本"
    L.append(
        f"> 行情窗口：{trading_window}（{len(window)} 个不同交易日）｜"
        f"字段 {nfields} 个｜样本值 {nsamples} 条"
    )
    if event_window:
        L.append(f"> 新闻/公告自然日窗口：{event_window[0]:%Y%m%d} ~ {event_window[1]:%Y%m%d}")
    L.append(
        f"> 主攻目标（unverified）={len(left_ids)}｜可审定新候选={len(actionable)}｜"
        f"首次发现新候选对={new_count}｜已登记关系复验={len(revalidations)}｜"
        f"异号同义 {len(cross)} / 同号镜像 {len(same)}\n"
    )
    L.append(
        f"> **规则**：L1 每日需≥{min_daily_l1} 组有效配对，并至少有"
        f"{min_informative_daily_l1} 组信息配对；双方同时为 0 或同时缺失不计命中率，"
        f"一侧为 0、另一侧非 0 按失配计。信息配对命中率≥{hit_rate_l1_ratio:.0%}，"
        f"且覆盖至少 {multi_day_min} 个独立交易日/自然事件日；同一来源族不作为跨源证据；"
        "盘中快照不计入 L1。JSON `daily_sample_counts` 与 `daily_informative_sample_counts`"
        "分别保留每日有效配对数和 L1 信息配对数。"
        "（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；"
        "新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。\n"
    )
    L.append("---\n")
    L.append(f"## 一、L1 / L1-U 新候选 — 异号同义（跨编号，高价值）({len(cross)})\n")
    if cross:
        L.append(
            "| 左字段(unverified) | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |"
        )
        L.append("|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|")
        for p in cross:
            L.append(_l1_row(p))
    else:
        L.append("_本轮无异号同义候选。_\n")
    L.append(f"\n## 二、L1 / L1-U 新候选 — 同号镜像（同编号，低优先级）({len(same)})\n")
    if same:
        L.append(
            "| 左字段 | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |"
        )
        L.append("|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|")
        for p in same:
            L.append(_l1_row(p))
    else:
        L.append("_本轮无同号镜像候选。_\n")
    L.append(f"\n## 三、已登记映射的本窗口复验（{len(revalidations)}）\n")
    L.append(
        "_这些关系已在主注册表登记，只用于观察当前样本是否仍支持既有映射；"
        "它们不是新的未知字段候选，也不能再次提交为新定案。_\n"
    )
    if revalidations:
        L.append(
            "| 左字段 | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |"
        )
        L.append("|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|")
        for pair in revalidations:
            L.append(_l1_row(pair))
    else:
        L.append("_本轮没有已登记关系进入复验窗口。_\n")
    L.append("\n## 四、L4 存疑候选（{0}）\n".format(len(l4)))
    if l4:
        L.append("| 左字段 | 右字段 | 命中率 | 天数 | 样本 |")
        L.append("|:--|:--|--:|--:|--:|")
        for p in l4[:60]:
            L.append(
                f"| `{p['left']}` | `{p['right']}` | {p['overall_hit']:.2%} | "
                f"{p['n_days']} | {p['n_pairs']} |"
            )
        if len(l4) > 60:
            L.append(f"\n_（仅显示前 60 / 共 {len(l4)}）_")
    else:
        L.append("_本轮无 L4 候选。_\n")
    L.append("\n## 五、已证伪护栏命中（被拦截的伪结论候选）（{0}）\n".format(len(guardrail_hits)))
    if guardrail_hits:
        L.append("| 左字段 | 右字段 | 命中护栏ID | 伪主张 |")
        L.append("|:--|:--|:--|:--|")
        for h in guardrail_hits:
            L.append(f"| `{h['left']}` | `{h['right']}` | {h['id']} | {h['false_claim']} |")
        L.append("\n_以上候选因命中 REFUTED_CONCLUSIONS（数值实证推翻）已被自动判伪，未进入 L1。_")
    else:
        L.append("_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_\n")
    method_candidates = method_candidates or []
    L.append(f"\n## 六、主动方法候选（不直接定案）（{len(method_candidates)}）\n")
    L.append(
        "_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；"
        "每项保留样本日期和来源，仍需人工复核并以独立证据终判。_\n"
    )
    if method_candidates:
        L.append("| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |")
        L.append("|:--|:--|:--|--:|:--|:--|:--|")
        for candidate in method_candidates[:100]:
            method_names = ", ".join(method["method"] for method in candidate["methods"])
            dates = ", ".join(candidate["sample_dates"][:6])
            sources = ", ".join(candidate["evidence_sources"])
            evidence = candidate["methods"][0]
            if evidence["method"] == "robust_correlation":
                summary = (
                    f"Pearson={evidence['pearson']}, Spearman={evidence['spearman']}, "
                    f"LOO稳号={evidence['leave_one_out_sign_stable']}"
                )
            elif evidence["method"] == "affine_formula":
                summary = evidence["formula"]
            elif evidence["method"] == "per_stock_time_series":
                summary = (
                    f"逐股相关={evidence['median_abs_pearson']}, "
                    f"方向一致={evidence['sign_consistency']}"
                )
            else:
                summary = ", ".join(evidence.get("shared_tokens", [])) or "标签线索"
            L.append(
                f"| `{candidate['left']}` | `{candidate['right']}` | {method_names} | "
                f"{candidate['sample_count']} | {dates} | {sources} | {summary} |"
            )
        if len(method_candidates) > 100:
            L.append(f"\n_仅显示前 100 / 共 {len(method_candidates)} 条。_\n")
    else:
        L.append("_本轮无达到门槛的主动方法候选。_\n")

    diagnostics = list(dict.fromkeys(diagnostics or []))
    L.append(f"\n## 七、日期与数据质量告警（{len(diagnostics)}）\n")
    if diagnostics:
        for message in diagnostics[:100]:
            L.append(f"- {message}")
        if len(diagnostics) > 100:
            L.append(f"- 另有 {len(diagnostics) - 100} 条告警，详见同名 JSON 报告。")
    else:
        L.append("_无日期或数据质量告警。_")
    L.append("\n---\n")
    L.append("> 数据来源：通达信 / 项目字段对撞体系。以上为方法论梳理，不构成投资建议。\n")
    return "\n".join(L)
