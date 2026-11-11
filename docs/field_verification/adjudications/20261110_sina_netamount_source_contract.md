# Sina `netamount` source-contract adjudication

**Decision date:** 2026-11-10<br>
**Identity:** `新浪(扩展API)::netamount`<br>
**Decision:** confirm the raw API value is net inflow in yuan. Sina's help page displays net inflow in ten-thousand yuan. Do not register a strict cross-source equality mapping.

## Evidence

The project stores `netamount` from rows returned by Sina's `MoneyFlow.ssl_qsfx_zjlrqs` endpoint. Sina's [official capital-flow help page](https://finance.sina.com.cn/temp/guest4377.shtml) defines net inflow as inflow minus outflow, lists the page unit as 万元, and defines net inflow rate as net inflow divided by turnover times 100%. The page does not publish the JSON response schema or the raw unit of the `netamount` key. It also says provider methods and statistical times can cause differences.

The raw unit was checked against the response's `ratioamount` and the independent TDX `quote_raw.amount` sample. Across 14 trading dates and 20 stocks, 278 pairs had both Sina values and TDX turnover. `netamount / ratioamount` estimates gross turnover when `ratioamount` is a ratio value. Its median relative difference from TDX turnover was 0.0001468%; 218/278 pairs were within 1%, and 276/278 within 5%. This scale fits yuan. A ten-thousand-yuan interpretation would be four orders of magnitude off. The check supports the raw unit, but does not establish identical capital-flow calculations across providers.

Two 920118 pairs remain material outliers: 30.36% on 2026-10-30 and 38.27% on 2026-11-02. They are retained as source or timing differences, not attributed to rounding. The 2026-11-09 example for 600519 has raw `netamount=125,841,868.22`, `ratioamount=0.0364231`, and TDX turnover `3,578,407,168` yuan; the ratio-implied turnover is `3,455,001,585` yuan, 3.45% lower.

## Decision boundary

The registry records the raw Sina field in yuan and retains the official page's ten-thousand-yuan display scale in the meaning. Convert by 10,000 only when reproducing the page display. No exact equality mapping to TDX or another provider is added; the official help page itself warns that methods and statistical times differ.
