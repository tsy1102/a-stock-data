# Sina `trade` source-contract adjudication

**Decision date:** 2026-11-10<br>
**Identity:** `新浪(扩展API)::trade`<br>
**Decision:** confirm the field as a price snapshot associated with the `opendate` row; reject the old “closing price” description. Do not register a strict point-in-time mapping to another provider's quote field.

## Source path

`stock_common.sc_datasource._eastmoney.get_sina_stock_fund_flow_raw()` calls Sina's `MoneyFlow.ssl_qsfx_zjlrqs` endpoint. `scripts.capture_http_collectors.collect_sina_extended()` stores the returned per-stock money-flow rows and uses the latest row for scalar capture fields. The project preserves the returned `trade` value; it does not calculate or normalize it.

Sina's official [capital-flow help page](https://finance.sina.com.cn/temp/guest4377.shtml) says individual-stock rankings can use the latest price, the page refreshes every five minutes, real-time data is usually delayed by five to ten minutes, and differences among providers can come from calculation methods and statistical times. The help page does not publish a JSON schema for the `trade` key; that limitation is retained in the decision.

## Retained-sample checks

The collision report `20261110/20261110_after_fuyao_ps_ttm/20261110_collision_report.json` contains the 14-date, 20-stock candidate comparison for `sina_extended.trade` and `tdx.quote_raw.price`:

- 278 paired records across 14 trading dates and 20 stocks.
- Pearson and Spearman correlation are both 1.0; affine-fit R² is 0.999998.
- Median per-stock time-series correlation is 0.9999; the lowest is 0.9902.
- Direct price equality is not reliable at a fixed timestamp: 228/278 pairs are within 0.01 yuan and 249/278 within 0.05 yuan. The remaining differences are consistent with asynchronous refresh/statistical time, but their exact cause cannot be proven because the capture does not record a Sina row timestamp.
- `changeratio` equals `trade / TDX quote_full.last_close - 1` within 1e-6 for 278/278 pairs. This independently supports that `trade` is a quote price used to calculate the row's change ratio.
- Eastmoney daily close is available for 120 pairs across six dates; only 94/120 `trade` values are within 0.01 yuan of that close. `trade` therefore cannot be labeled as a guaranteed close value.

The underlying comparisons can be reproduced from each retained capture directory's `raw_sina_extended.json`, `raw_tdx.json`, and, where present, `raw_em_kline_f61.json`. Capture directories before 2026-10-15 are outside the current sample-retention baseline and were not read.

## Decision boundary

The registry meaning is now **行情价格快照（元/股）**, not **收盘价**. The evidence supports the field's price role and unit, but does not establish an exact synchronization point. No cross-source mapping to `tdx.quote_raw.price` is added. Do not infer a trade timestamp from the capture folder date or use this field as the official daily close without a separate close-qualified source.
