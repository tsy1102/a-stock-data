# Eastmoney IPO `ISSUE_WAY_EXPLAIN` 发行方式说明定案

复核日期：2026-11-21。

## 定案

将 `东财-event_dc(IPO发行记录)::ipo_calendar[].ISSUE_WAY_EXPLAIN` 定义为 IPO 发行记录中对**发行方式的文字说明**，规范名 `ipo_issue_way_explanation`，无单位。

该字段与 `ISSUE_WAY`（发行方式类型）分开。当前保留样本中的“历史遗留”“本地发行”“认购证”是已观察到的说明值；本裁决不表示完整的发行流程分类，也不穷尽所有可能取值。不建立跨来源映射。

## 官方字段定义与项目运行路径

- 东方财富官方[新股详情前端脚本 `xgdetail.js`](https://data.eastmoney.com/newstatic/js/xg/xgdetail.js) 请求 `RPT_IPO_OTHERDETAILS`，请求列包含 `ISSUE_WAY`、`ISSUE_WAY_EXPLAIN`。脚本将 `data.ISSUE_WAY` 标为“发行方式类型”，将 `data.ISSUE_WAY_EXPLAIN` 标为“发行方式说明”。这两个官方标签明确区分类型与说明。
- 项目 [`_events.py`](../../../stock_common/sc_datasource/_events.py) 将 `ipo_calendar` 请求配置为 `RPTA_APP_IPOAPPLY`，使用 `columns=ALL`；[`_datacenter.py`](../../../stock_common/sc_datasource/_datacenter.py) 原样返回 `result.data[*]`；`ipo_calendar()` 不重命名或换算响应字段。精确运行路径为 `RPTA_APP_IPOAPPLY response.data[*].ISSUE_WAY_EXPLAIN -> ipo_calendar() -> raw_event_dc.ipo_calendar[].ISSUE_WAY_EXPLAIN`。
- `RPT_IPO_OTHERDETAILS` 是官方详情前端使用的独立报表端点，不等同于项目采集的 `RPTA_APP_IPOAPPLY`。本裁决以同名官方字段标签、项目直接透传路径和代表记录逐值核对共同确认当前路径的语义；不推断两个报表未来的完整 schema 相同。

## 留存样本与跨端点核对

`docs/field_verification/20261119/raw_event_dc.json` 的目标数据日为 2026-11-19，采集自然日为 2026-11-20，`event_dc` 来源采集始于 2026-11-20 06:57:34。响应共 20 条，全部接收成功。该归档未提供 `event_dc.as_of_date`；这里核验的是历史 IPO 事件属性，以每行股票代码和 `APPLY_DATE` 定位，不将目录数据日或采集自然日当作事件日期。

全部 20 行的 `ISSUE_WAY_EXPLAIN` 均非空：`历史遗留` 16 行、`本地发行` 3 行、`认购证` 1 行。相同 20 行的 `ISSUE_WAY` 均为 `其他发行方式`，支持将说明字段与类型字段分开解释。

对官方 `RPT_IPO_OTHERDETAILS` 响应抽核四条，覆盖全部三种已观察说明值；两字段均与归档的 `RPTA_APP_IPOAPPLY` 对应记录精确一致：

| 代码 | 股票 | `APPLY_DATE` | 归档 `ISSUE_WAY` | 归档 `ISSUE_WAY_EXPLAIN` | 官方详情接口对照 |
|---|---|---|---|---|---|
| 000001 | 平安银行 | 1989-03-10 | 其他发行方式 | 历史遗留 | 两字段完全一致 |
| 000002 | 万科A | 1988-12-28 | 其他发行方式 | 历史遗留 | 两字段完全一致 |
| 000011 | 深物业A | 1991-11-01 | 其他发行方式 | 本地发行 | 两字段完全一致 |
| 000025 | 特力A | 1993-03-15 | 其他发行方式 | 认购证 | 两字段完全一致 |

官方详情查询分别按 `SECURITY_CODE` 过滤：[000001](https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_IPO_OTHERDETAILS&columns=SECURITY_CODE%2CISSUE_WAY%2CISSUE_WAY_EXPLAIN&filter=%28SECURITY_CODE%3D%22000001%22%29&pageNumber=1&pageSize=5&source=WEB&client=WEB)、[000002](https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_IPO_OTHERDETAILS&columns=SECURITY_CODE%2CISSUE_WAY%2CISSUE_WAY_EXPLAIN&filter=%28SECURITY_CODE%3D%22000002%22%29&pageNumber=1&pageSize=5&source=WEB&client=WEB)、[000011](https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_IPO_OTHERDETAILS&columns=SECURITY_CODE%2CISSUE_WAY%2CISSUE_WAY_EXPLAIN&filter=%28SECURITY_CODE%3D%22000011%22%29&pageNumber=1&pageSize=5&source=WEB&client=WEB)、[000025](https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_IPO_OTHERDETAILS&columns=SECURITY_CODE%2CISSUE_WAY%2CISSUE_WAY_EXPLAIN&filter=%28SECURITY_CODE%3D%22000025%22%29&pageNumber=1&pageSize=5&source=WEB&client=WEB)。逐行数据与未抽核行见[完整样本表](../research/20261121_eventdc_ipo_issue_way_explain_samples.csv)。

## 碰撞回归

按 2026-11-19 归档窗口重跑六个采集目录、七个有效交易日。报告 `report_completeness.status=complete`、问题数为 0；主攻未知目标由 64 降为 63，目标清单不再包含该完整路径。回归报告的 L1/L1-C 为 0、L4 为 2；另有 81 条候选审阅记录仍待人工处置，不影响本次单源契约裁决，但仍属于总体破解积压。详见[完整碰撞报告](../20261119/issue_way_explain_adjudication/20261119_collision_report.md)。

## 适用范围与限制

- 确认的是该精确运行路径中 `ISSUE_WAY_EXPLAIN` 的字段角色及与 `ISSUE_WAY` 的区别。
- 官方前端字段标签来自 `RPT_IPO_OTHERDETAILS`；四条代表详情响应覆盖了当前归档的全部三种说明值。未逐项查询其余 16 条详情响应，因此不声称完成 20 条跨端点复核。
- 东方财富未提供版本化 schema。若将来 `RPTA_APP_IPOAPPLY` 与 `RPT_IPO_OTHERDETAILS` 同证券记录的值出现分歧，应重新核对端点与路径映射。
- 此字段是历史 IPO 事件的说明文本，不按行情交易日或来源数据日做跨日碰撞；本裁决也不把当前详情接口值当作当年网页页面的历史快照。

## 证据摘要

- 原始归档 SHA-256：`41fe019b29d038e1cf4726f69700af303aae0206a6fdb8d7399912290065b091`
- 完整样本 CSV 规范 LF SHA-256：`99a9c0a04785c722578ac4093c9628b385efb8b50c1c6dfacbdebe7f48047d4a`
- 官方 `xgdetail.js` SHA-256：`e681def470ece2ae827fd9a870baf108e692f8020d48d316ef45d5108c9aeeef`

结构化决定见 [`20261121_eventdc_ipo_issue_way_explain.json`](20261121_eventdc_ipo_issue_way_explain.json)。
