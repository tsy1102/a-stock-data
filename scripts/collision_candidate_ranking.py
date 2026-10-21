from __future__ import annotations


def _method_candidate_score(candidate):
    return (
        len(candidate["methods"]),
        candidate["sample_count"],
        candidate["left"],
        candidate["right"],
    )


def _compact_method_candidate(candidate):
    """Keep useful method evidence while bounding the target-frontier report size."""
    compact = {key: value for key, value in candidate.items()}
    compact_methods = []
    for method in candidate.get("methods", []):
        item = dict(method)
        if item.get("method") == "per_stock_time_series":
            item["stock_correlations"] = item.get("stock_correlations", [])[:5]
        compact_methods.append(item)
    compact["methods"] = compact_methods
    return compact


def _method_candidate_summary(candidate):
    details = []
    for method in candidate.get("methods", []):
        detail = dict(method)
        if detail.get("method") == "per_stock_time_series":
            detail["stock_correlations"] = detail.get("stock_correlations", [])[:5]
        details.append(detail)
    return {
        "right": candidate["right"],
        "methods": details,
        "sample_count": candidate["sample_count"],
        "sample_dates": candidate["sample_dates"],
        "evidence_sources": candidate["evidence_sources"],
    }


def select_method_candidate_frontier(method_candidates_by_left, global_candidates, max_candidates):
    """Retain one best candidate per target when it falls outside the global cap."""
    global_pairs = {(row["left"], row["right"]) for row in global_candidates}
    frontier = []
    for left_id in sorted(method_candidates_by_left):
        candidates = method_candidates_by_left[left_id]
        for candidate in candidates:
            if (candidate["left"], candidate["right"]) in global_pairs:
                continue
            frontier.append(_compact_method_candidate(candidate))
            if len(frontier) >= max_candidates:
                break
    return frontier
