# Eastmoney Push2 `f109` public-page observation

Reviewed: 2026-11-10 (Asia/Shanghai)<br>
Capture date: 2026-11-09<br>
Source path: `东财-push2(stock/get)::f109`

## Scope

This review checks the existing source-level meaning and unit for `f109`. It does not claim an API field contract, change the registered metadata, or create a cross-source mapping. Both official Eastmoney stock pages show the `净利润` row for the same annual report period, 2025-12-31. The project capture date is 2026-11-09; the report period is 2025-12-31.

The archived raw sample is `docs/field_verification/20261109/raw_push2.json` (59,374 bytes; SHA-256 `e3cd1504635b48176bd6eeefdce313923a05871ad03735bf90db9a85d173c3fc`). Its `stocks[code].data.f109` values are yuan. The page displays the corresponding annual financial summary in 亿元 at two decimal places, so the comparison uses the explicit factor `1e-8` and a `0.01` 亿元 increment.

## Page observations

| Stock | Eastmoney display, 2025-12-31 | Raw `f109` (元) | Converted (亿元) | Difference from display |
|---|---:|---:|---:|---:|
| 贵州茅台 (600519) | 823.20亿 | 82,320,067,101.68 | 823.2006710168 | 0.0006710168亿 |
| 农业银行 (601288) | 2910.41亿 | 291,041,000,000 | 2910.41 | 0亿 |

Both differences are below half the displayed increment (0.005亿元). The visible page label is `净利润`; this evidence supports the existing source meaning and report period at the displayed precision. It does not independently define the upstream API schema or establish a cross-source equivalence.

Official pages:

- https://data.eastmoney.com/stockdata/600519.html — 财务数据 → 财务摘要（按报告期分） → 2025-12-31 → 利润表(元) → 净利润：823.20亿。
- https://data.eastmoney.com/stockdata/601288.html — 财务数据 → 财务摘要（按报告期分） → 2025-12-31 → 利润表(元) → 净利润：2910.41亿。

The archived values, page labels, and display values are recorded below in the exact structured format required by registry parity.

[observation] {"code":"f109","data_date":"20261109","display_increment":"0.01","display_text":"2025-12-31 净利润 823.20亿","display_unit":"亿元","display_value":"823.20","missing_as_zero":false,"page_metric":"财务数据 > 财务摘要（按报告期分） > 2025-12-31 > 利润表(元) > 净利润","page_url":"https://data.eastmoney.com/stockdata/600519.html","raw_to_display_factor":"0.00000001","raw_value":82320067101.68,"source":"东财-push2(stock/get)","source_file":"20261109/raw_push2.json","stock_code":"600519"}
[observation] {"code":"f109","data_date":"20261109","display_increment":"0.01","display_text":"2025-12-31 净利润 2910.41亿","display_unit":"亿元","display_value":"2910.41","missing_as_zero":false,"page_metric":"财务数据 > 财务摘要（按报告期分） > 2025-12-31 > 利润表(元) > 净利润","page_url":"https://data.eastmoney.com/stockdata/601288.html","raw_to_display_factor":"0.00000001","raw_value":291041000000.0,"source":"东财-push2(stock/get)","source_file":"20261109/raw_push2.json","stock_code":"601288"}
