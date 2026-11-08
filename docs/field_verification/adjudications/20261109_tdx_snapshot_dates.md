# TDX 扩展数据日期字段定案

日期：2026-11-09<br>
来源身份：`TDX(双命名源)`，按完整 code path 分别登记。

## 结论

更正：本记录最初将这 11 个日期字段误归入 `get_market_snapshot_batch`。复核通达信官方文档的分节与字段表后，确认它们实际列在 `get_more_info_batch`（批量获取股票扩展数据）返回字段表中。注册表字段语义和状态不变，仅修正接口归属。

| 完整 code path | 官方含义 | 注册单位备注 |
|---|---|---|
| `DTDate_Recent` | 近 2 年最近跌停板日期 | 日期字符串；官方未注明格式 |
| `NoticeDate_Recent` | 最近业绩预告日 | 日期字符串；官方未注明格式 |
| `RecentDZDate` | 最近定增日 | 日期字符串；官方未注明格式 |
| `RecentGGJYDate` | 最近北上大额交易日 | 日期字符串；官方未注明格式 |
| `RecentHGDate` | 最近回购预案日 | 日期字符串；官方未注明格式 |
| `RecentIncentDate` | 最近股权激励预案日 | 日期字符串；官方未注明格式 |
| `RecentReleaseDate` | 最近解禁日 | 日期字符串；官方未注明格式 |
| `ReportDate` | 最近财报公告日期 | 日期字符串；官方未注明格式 |
| `StopJYDate_Recent` | 最近停牌日期 | 日期字符串；官方未注明格式 |
| `TopDate_Recent` | 近 2 年最近龙虎榜日期 | 日期字符串；官方未注明格式 |
| `ZTDate_Recent` | 近 2 年最近涨停板日期 | 日期字符串；官方未注明格式 |

官方 `get_more_info_batch` 字段表将它们的数据类型列为 `str`，但没有给日期编码格式，因此不擅自写成 `YYYYMMDD`。`ReportDate` 表示最近财报公告日期，不等同于财报报告期截止日，也不等同于预约披露日。

## 证据边界

- 依据：[通达信官方 `get_more_info_batch` 扩展数据接口文档](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html)，字段表中的日期字段从 `RecentGGJYDate` 至 `StopJYDate_Recent`。
- 本次确认的是 TDX 公开接口的字段名、业务描述和字符串类型。
- 当前项目代码没有调用这些字段名；不据此宣称它们已进入项目采集、缓存或报告链路。
- 不新增任何 TDX 与 ZHB 的列号映射或跨源逐值映射，也不推断字段值对应哪一个项目数据日期。
- 官方接口返回类型和日期格式是两件事：类型为字符串已确认，具体格式保留未说明状态。

机器可读裁决：[`20261109_tdx_snapshot_dates.json`](20261109_tdx_snapshot_dates.json)，ID `tdx-snapshot-date-fields-20261109`；更正说明与网页核验记录见 [`public_web/20261109_tdx_snapshot_dates.md`](public_web/20261109_tdx_snapshot_dates.md)。
