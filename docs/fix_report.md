# 自动修复流水线报告（Auto-Fix Pipeline）

- 生成时间: 2026-08-01T14:46:00
- Phase: analyze
- diff_specs 总数: 29（resolved=0 blocked=0 进行中=29）

## 未解决 diff_specs

| 优先级 | ID | 状态 |
|:---:|:---|:---:|
| P2 | `ful.field.pe_vs_industry` | pending |
| P1 | `lng.data_call.get_tencent_quote` | pending |
| P1 | `lng.data_call.tdx_get_quote_full` | pending |
| P2 | `lng.field.industry` | pending |
| P2 | `lng.field.pb` | pending |
| P1 | `med.data_call.get_eastmoney_fund_flow_120d` | pending |
| P1 | `med.data_call.get_stock_sector_rank` | pending |
| P1 | `med.data_call.get_tencent_quote` | pending |
| P1 | `med.data_call.tdx_get_history_fund_flow` | pending |
| P1 | `med.data_call.tdx_get_quote_full` | pending |
| P2 | `med.field._pe_ttm` | pending |
| P2 | `med.field.float_shares` | pending |
| P1 | `sht.data_call.get_tencent_quote` | pending |
| P1 | `sht.data_call.tdx_get_quote_full` | pending |
| P2 | `sht.field._pe_s_str` | pending |
| P2 | `sht.field._pe_t` | pending |
| P2 | `sht.field.amount_wan` | pending |
| P2 | `sht.field.amplitude_pct` | pending |
| P2 | `sht.field.change_amt` | pending |
| P2 | `sht.field.float_shares` | pending |
| P2 | `sht.field.last_close` | pending |
| P2 | `sht.field.limit_down_price` | pending |
| P2 | `sht.field.limit_up` | pending |
| P2 | `sht.field.total_shares` | pending |
| P2 | `sht.field.vol_ratio` | pending |
| P1 | `sht.label.⚠️ 盘前模式（9` | pending |
| P1 | `sht.label.涨停价` | pending |
| P1 | `sht.label.涨跌额` | pending |
| P1 | `sht.label.量比` | pending |

## 已解决 diff_specs

| 优先级 | ID | 状态 |
|:---:|:---|:---:|

## CHANGELOG 建议

全部 P0/P1 解决后，建议在 CHANGELOG.md 顶部新增:
```
## [15.x] - <日期>
**数据精度回归修复**：对照 a-stock-data-v9.6 恢复字段（详见 docs/fix_report.md）
```
