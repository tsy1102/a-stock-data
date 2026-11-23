# 东方财富 IPO 日期字段裁决

核验日期：2026-11-23。适用身份为 `东财-event_dc(IPO发行记录)` 的完整路径；不创建跨来源映射，也不修改行情日期继承策略。

## 裁决

| 完整来源路径 | 规范名 | 定案含义 | 单位/格式 |
|:--|:--|:--|:--|
| `ipo_calendar[].MARKET_CAP_CONFIRMDATE` | `ipo_market_value_confirm_date_rule` | 该字段是网上申购市值确认基准日规则文本。这里的 T 是网上申购日，T-2 是它之前两个交易日。深市规则按 T-2 前 20 个交易日（含 T-2）的日均市值计算。本字段不表示某条历史 IPO 记录的绝对日期。它也不表示行情观测日，不能表示接口更新时间。现有样本仅覆盖深市，未据此推广到北交所。 | 规则文本（相对交易日） |
| `ipo_calendar[].UP_DATE` | `ipo_source_update_date` | 东财 IPO 发行记录接口提供的上游更新日期标记。它不是 IPO 申购日期，也不是上市日期。它不等同于采集运行日。它也不等同于目录目标数据日。它不是行情观测日期。留存样本显示同一接口批次中的多条记录共享此值。目前只确认它是来源更新标记。底层逐行更新时间和整个数据集刷新日期的精确关系仍未证实。 | 日期时间字符串；样本时分秒为 `00:00:00` |

两个字段均按官方 `RPTA_APP_IPOAPPLY` 响应原键登记。路径来自 `stock_common/sc_datasource/_events.py::ipo_calendar()`，经 `eastmoney_datacenter(columns="ALL")` 透传至 `raw_event_dc.ipo_calendar[]`。

## 证据

- 保留期内 20 个响应批次、400 条 IPO 记录均有这两个字段。`MARKET_CAP_CONFIRMDATE` 的 400 个值完全相同，均为 `T-2日(T:申购日)`；样本代码均属深市。`UP_DATE` 在每批内唯一且各记录共享，跨批次日期变化；它与目标数据日、采集运行日和来源运行日均不恒等。逐行值和每个 raw 文件的 SHA-256 见[审计 CSV](../research/20261123_eventdc_ipo_date_fields_audit.csv)。
- 对同一个证券代码 002520，东方财富官方 Data Center 响应返回 `APPLY_DATE=2010-12-01`、`MARKET_CAP_CONFIRMDATE=T-2日(T:申购日)`、`UP_DATE=2026-11-23`。这排除了将 `UP_DATE` 解释为该股票申购日或上市日。
- 东方财富[002520 新股详情页](https://data.eastmoney.com/xg/xg/detail/002520.html)把相应显示项标为“网上申购市值确认日”，显示 `T-2日(T:网上申购日)`。深交所[网上发行实施细则第 4 条](https://www.szse.cn/lawrules/rule/stock/issue/P020190228664910292959.pdf)规定 T 日为发行公告确定的网上申购日，市值按 T-2 日前 20 个交易日（含 T-2 日）的日均值计算。
- 本轮通过一次公开接口样本查询和官方页面核对，没有运行项目采集器。

## 适用边界

- `MARKET_CAP_CONFIRMDATE` 是相对交易日规则文本；旧 IPO 行中的 `T-2` 不是历史发行时的绝对日期。样本只覆盖深市，不据此外推北交所申购规则。
- Eastmoney 未公开该响应的版本化字段 schema。详情页标签和值与同证券代码的 API 原始键相符，但详情 HTML 的显示节点使用 `OFFLINE_END_DATE` 样式类，因此本裁决不声称已取得 API 的正式字段映射文档。
- `UP_DATE` 的精确后端更新粒度未公开。它不可作为行情日期锚或同批行情字段的 `as_of_date`；批次共同值只说明来源更新标记，不证明批次内其他字段属于同一业务日期域。
- 未修改 `temporal_policy.json`、日期继承配置、来源优先级或采集行为。

完整历史逐批审计、当前官方 API 样本和来源链接见[日期类字段研究记录](../research/20261123_eventdc_ipo_date_fields_audit.md)。结构化裁决见[JSON](20261123_eventdc_ipo_date_fields.json)。
