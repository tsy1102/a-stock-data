# ELTDX limit_ladder exact-path contract evidence

Review date: 2026-11-20. The audit reads retained local captures only; it sends no network requests.

## Scope and date qualification

- Retention boundary: `20261015` (`scripts/capture_retention.py`).
- Raw ELTDX files inspected: 22; files with `global_helpers.limit_ladder.rows`: 12.
- Qualified observations: 12 data dates, 16 stock rows, 64 field comparisons.
- Qualified data dates: 20261016, 20261020, 20261021, 20261023, 20261026, 20261028, 20261030, 20261102, 20261104, 20261110, 20261117, 20261119.
- Every observation satisfies directory date = `meta.data_date` = row `target_trade_date`; `stats_date` and `previous_trade_date` are retained separately and are not replaced with the directory date.
- `global_helpers.limit_ladder.rows[*]` was compared with both its folded `stocks.<code>.limit_ladder` copy and `stocks.<code>.shortline` output for the exact four fields below.

## Same-response path comparisons

| Exact field path suffix | Same-raw shortline equality | Non-null pairs | Both null | Differences |
|---|---:|---:|---:|---:|
| `limit_board_text` | 16/16 | 15 | 1 | 0 |
| `limit_stat_days` | 16/16 | 12 | 4 | 0 |
| `limit_up_count_in_stat_days` | 16/16 | 12 | 4 | 0 |
| `prev2_seal_amount` | 16/16 | 7 | 9 | 0 |

All four fields also match their folded `stocks.<code>.limit_ladder` copies in every row; the CSV stores both comparisons and the raw/meta SHA-256 values for each source file.

## Source contract boundary

The fixed ELTDX v3.3.2 Helper contract defines `limit_stat_days` and `limit_up_count_in_stat_days` as direct `tdxstat.cfg` values, `prev2_seal_amount` as the seal amount from the second actual trading day before the target date in `tdxstat2.cfg`, and `limit_board_text` as a readable window/count string with the documented previous-session adjustment when the target day is sealed. The ELTDX limit-ladder helper returns `ShortlineIndicator` rows. This is an ELTDX adapter output contract, not a claim that the four names are native TDX wire fields.

No cross-source mapping is inferred or added. The sample comparison only validates the two ELTDX helper output paths against each other.

Sample file: [`20261120_eltdx_limit_ladder_path_contract_samples.csv`](20261120_eltdx_limit_ladder_path_contract_samples.csv); SHA-256: `081467fe3a154902d876e736a065e32c5fd0d13ca920b6b4527971c0d325719c`.

Pinned upstream references: [ELTDX v3.3.2 Shortline Indicators](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/helpers/%E7%9F%AD%E7%BA%BF%E6%8C%87%E6%A0%87.md), [ELTDX v3.3.2 Limit Ladder](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/helpers/%E8%BF%9E%E6%9D%BF%E5%A4%A9%E6%A2%AF.md).
