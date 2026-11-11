# Sina `turnover` source-contract adjudication

**Decision date:** 2026-11-10<br>
**Identity:** `新浪(扩展API)::turnover`<br>
**Decision:** confirm this as turnover rate, with raw values expressed in ten-thousandths of a ratio. Do not register a strict equality mapping to Tencent quote field 38.

## Evidence

The project obtains `turnover` as a row field from Sina's `MoneyFlow.ssl_qsfx_zjlrqs` request and preserves it without conversion. Sina's [official capital-flow help page](https://finance.sina.com.cn/temp/guest4377.shtml) lists turnover rate among individual-stock stage statistics. It also says the page updates every five minutes, real-time data is usually delayed by five to ten minutes, and providers can differ because of calculation methods and statistical times. The official page does not publish the JSON response schema or a unit for the `turnover` key.

An independent [ZVT Sina MoneyFlow adapter](https://github.com/zvtvz/zvt/blob/master/src/zvt/recorders/sina/money_flow/sina_stock_money_flow_recorder.py#L458-L459) requests the same family of Sina rows and converts `item["turnover"] / 10000` to its decimal `turnover_rate` value at lines 564-568. This is community implementation evidence, not an official Sina specification.

The retained project captures provide a second check. Across 14 trading dates and 20 stocks, `Sina turnover / 100` compared with Tencent quote `fields[38]` as a displayed percentage produced 280 pairs:

- Pearson correlation: 0.9998; affine-fit R²: 0.999528.
- Median absolute difference: 0.003313 percentage points.
- 217/280 pairs differ by at most 0.01 percentage points; 252/280 by at most 0.05 percentage points.
- 28 pairs exceed 0.05 percentage points; the largest difference is 1.61983 percentage points (920118, 2026-11-02).

For example, on 2026-10-19 the raw value 31.7811 for 600519 converts to 0.317811%, while Tencent reports 0.32%. The project collision report contains the broader candidate series: `20261110/20261110_after_sina_trade/20261110_collision_report.json`.

## Decision boundary

The registry now describes the raw `turnover` unit as **万分比**: divide the raw value by 10,000 for a decimal ratio, or by 100 for a percentage. The source meaning and scale are supported by the public Sina help page, the independent adapter, and retained cross-source samples. The material outliers and lack of synchronized source timestamps mean the data does not establish strict pairwise equality with Tencent field 38. No cross-source mapping is added, and the larger differences are not dismissed as rounding alone.
