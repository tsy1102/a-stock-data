# 2026-11-17 Eastmoney Ulist239 `f149` source-level semantics

## Decision

Confirm the meaning of the exact path `东财-ulist239(np/get)::f149` as the stock's cumulative percentage price change across six trading intervals: the current session close compared with the close six trading sessions earlier. The result is reported in percent (`%`). This is a source-internal empirical decision; it does not create a cross-source mapping and does not transfer to `stock/get::f149` or another endpoint's `f149`.

The old candidate `ulist239.f149 ↔ ZHB-tdxstat2::stat2.change_mtd` remains rejected. That rejection concerns only the proposed equivalence to month-to-date change; it does not conflict with this source-level meaning.

## Path and sample qualification

The project collector requests `f149` from Eastmoney's `ulist.np/get` response and stores it in `raw_ulist239.json`. The Ulist data date is taken from each record's `f297`, whose source-internal meaning was separately verified as the trading date for that security's current Ulist record. The K-line collector requests Eastmoney daily K-lines with `fqt=0`; its rows carry explicit trading dates and unadjusted close prices.

The audit covers the five eligible source dates 2026-11-05, 11-06, 11-09, 11-10, and 11-17, with the same 20 stocks on each date (100 unique source-date/security pairs). The 2026-11-17 Ulist raw was captured at 17:30:46 and its K-line raw at 17:29:05 China Standard Time; both are marked `closed`. The separately authorized 20:10 capture reused the completed Ulist and K-line sources and did not refresh these raw files. It attempted ZHB, which returned data dated 2026-11-16 and was preserved as stale. Therefore, the 2026-11-17 values in this audit are the latest retained Ulist/K-line samples for that data date, not values newly fetched at 20:10.

All source dates are verified against the Ulist `f297` values and K-line row dates, not inferred from run dates or folder names. No pre-retention samples are used. The complete row-level audit, including source dates, close prices, formula values, adjustments, residuals, and precision flags, is [`research/20261117_ulist239_f149_rolling_window_audit_v2.csv`](../research/20261117_ulist239_f149_rolling_window_audit_v2.csv); canonical LF SHA-256: `e7ef544aeb060e29e4c6fe5948693771c9a01562ed54ddd16c40ebc5ff4e351b`.

Raw sample SHA-256 values:

| Source date | `raw_ulist239.json` | `raw_em_kline_f61.json` |
|---|---|---|
| 2026-11-05 | `10a6f6eba28a406799ccf73d366482ce23913234da33020c752858ea9140cf68` | `73bfd0dea078a69088f1b549080c9edadc68094d101a1ec953c03dbbbbfc71a2` |
| 2026-11-06 | `fd4a54c15fc2aecd4edadbab8e50bfed75f610e989490d33ccb16676049feac2` | `873360060220fd38dafb1ebc14db5e5ac2d43900caae80e2629e27256864371c` |
| 2026-11-09 | `7d8bfc4b6d12e4d8bce1aa1cb1e93b5fbe6abbf4b3b05126887775c9838afa4c` | `df1c832c6b312bd19dab9dac254d5fec998bea000703aca600aa81e9dd6f793a` |
| 2026-11-10 | `386416eaaf7a3e4146e5679f47e86dc8f6ec08dd117bb3c6d4f2e62845a396c0` | `dbc01380f333a497cce2c565aa7048a5731e826ed4c945a03800cef6c614f461` |
| 2026-11-17 | `d8f0cd0092412ab8f33fc0cbdccc9643e10367001c667857ec6a16ea73b033bf` | `fd51603bfc254b3877149a9812c25442f9d1316aaeebf7b6f46f588086d757a4` |

## Formula and evidence

For target session `t`, the tested formula is:

```text
change_pct = ((close[t] / reference_close[t-6]) - 1) * 100
```

For `300788` on 2026-11-05 and 11-06, the reference close predates its 2026-10-30 ex-dividend date while the target close follows it. The issuer's official implementation notice states a cash dividend of RMB 1.02 per 10 shares, an ex-dividend date of 2026-10-30, and no bonus shares or capital-reserve conversion; this corresponds to RMB 0.102 per share. For those two comparisons only, the audit subtracts RMB 0.102 from the pre-event reference close before calculating the return. This company-action adjustment improves the comparison but does not establish Eastmoney's exact internal adjustment-factor or rounding implementation. [Official issuer notice](https://static.cninfo.com.cn/finalpage/2026-10-23/1225620807.PDF).

| Ulist source date | Samples | Exact after 2-decimal display rounding |
|---|---:|---:|
| 2026-11-05 | 20 | 19 |
| 2026-11-06 | 20 | 19 |
| 2026-11-09 | 20 | 20 |
| 2026-11-10 | 20 | 20 |
| 2026-11-17 | 20 | 20 |
| **Total** | **100** | **98** |

The remaining two comparisons are both `300788` during the dividend-adjustment interval. Each differs by `0.01` percentage point, one increment at the output's two-decimal precision; maximum residual is `0.01` percentage point and maximum relative residual, normalized by the larger absolute observed/model return, is `0.237037%`. They are recorded as approximate matches, not exact matches, and are not asserted to be proven rounding effects. No sample indicates a different return window or a different semantic field. The unresolved implementation detail is the precise corporate-action adjustment and rounding used to produce those two values; it does not change the supported six-interval return meaning.

The 2026-11-09 `f149` ↔ ZHB month-to-date equality is not a competing explanation: the separate source-date audit found 0/20 equality on 2026-11-06, while the 2026-11-09 rolling six-interval window happened to begin at the prior month-end. See [`20261117_ulist239_f149_mtd_candidate_rejection.md`](20261117_ulist239_f149_mtd_candidate_rejection.md).

## Scope and remaining limit

The verified scope is the meaning of `东财-ulist239(np/get)::f149` on the 20-stock sample and the five retained source dates above. The exact service-side adjustment factor, extra precision before display, and official Chinese field label were not exposed by the response. These remain calculation/label details; this decision does not claim a provider-published field label, does not declare every adjustment edge case solved, and does not establish equivalence with another endpoint or provider.
