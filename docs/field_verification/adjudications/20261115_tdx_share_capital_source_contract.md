# 2026-11-15 TDX 股本字段官方契约核验

## 裁决

| 完整来源路径 | 字典释义 | 单位 | 结论范围 |
|---|---|---|---|
| `TDX(双命名源)::Zgb` | 总股本 | 官方文档未注明 | 通达信官方接口字段定义；不代表本项目当前调用该接口 |
| `TDX(双命名源)::Ltgb` | 流通股本 | 官方文档未注明 | 通达信官方接口字段定义；不代表本项目当前调用该接口 |

通达信官方 [`get_gb_info_by_date` 接口文档](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1hc4303vsv1fk.html) 的输出表将 `Zgb`（double）定义为“总股本”，将 `Ltgb`（double）定义为“流通股本”。官方[版本更新说明](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1cfsjkbf8f3is/TdxQuantVersion.html)记载该接口于 2026-05-15 新增。精确路径、类型和释义足以确认这两个 TDX 来源字段的上游含义。

## 单位与证据边界

- `get_gb_info_by_date` 字段表没有给 `Zgb` 或 `Ltgb` 标注单位，故单位保持未注明。官方样例值只记录返回格式，不把样例值单独当作单位证明。
- 另一个官方接口 `get_stock_info` 使用不同字段名 `J_zgb` 与 `ActiveCapital`，并将其单位标为“万股”。这不能移植成 `Zgb` / `Ltgb` 的单位。
- 按保留边界扫描了 18 个含 `raw_tdx.json` 的目录，未发现这两个键的当前样本。因此本裁决是来源内官方契约，不声称完成项目采集值复算，不建立 ZHB 或其他来源的 `mappings`，也不证明项目当前运行时调用 `get_gb_info_by_date`。
- 同一接口的 `Date` 虽表示该接口返回的股本记录日期，但项目登记路径尚无足够证据绑定到此接口；它还可能表示其他数据域的日期。本次不修改 `TDX(双命名源)::Date`，不推断其实际项目路径。

结构化决策及前态快照见 [`20261115_tdx_share_capital_source_contract.json`](20261115_tdx_share_capital_source_contract.json)。
