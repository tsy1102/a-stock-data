# 2026-11-24 开盘啦市场情绪字段来源内实证定案

## 裁决范围

本批只裁决来源 `开盘啦(kpl)` 的 8 个精确字段身份：`Day`、`date`、`ZTJS`、`ztjs`、`df_num`、`strong`、`lbgd`、`tip`。接口键级 schema 未由开盘啦公开；官方网页仅作为产品语义证据，具体字段解释还结合当前适配器映射、同批 KPL 子接口及已有已验证字段。

没有运行采集。样本严格限于 `scripts/capture_retention.py::MIN_CAPTURE_DATE`（2026-10-15）及之后的 22 个归档目录。逐目录输入文件及 SHA-256 见[样本审计 CSV](../research/20261124_kpl_market_sentiment_samples.csv)。接口路径由 [`stock_common/sc_kpl.py`](../../../stock_common/sc_kpl.py) 确认。

开盘啦官网的产品语义和证据边界见[官方页面核验](public_web/20261124_kpl_market_sentiment.md)。官网称市场情绪功能覆盖涨跌家数、量能、涨停表现、大幅回撤和权重表现；它没有公开下述私有接口键级 schema。

## 字段与精确运行路径

| 注册字段 | 精确运行路径 | 定案语义 | 单位 | 样本支持 |
| --- | --- | --- | --- | --- |
| `ztjs` | `raw_market_sources.kpl_sentiment.__raw_response__.info[0].ztjs`；归一化为 `kpl_sentiment.ztjs` | 市场当日涨停股票家数 | 只 | `ChangeStatistics` 成功的 21/21 与同批 `MoodNumCount.list.ZTJS`、`RiseFallAnalysis.info[0][0]` 相等 |
| `ZTJS` | `raw_market_sources.kpl_up_down.__raw_response__.list.ZTJS`；归一化为 `kpl_up_down.zt_num` | 市场当日涨停股票家数 | 只 | 与同批 `RiseFallAnalysis.info[0][0]` 为 22/22；与成功的 `ChangeStatistics.ztjs` 为 21/21 |
| `df_num` | `raw_market_sources.kpl_sentiment.__raw_response__.info[0].df_num`；归一化为 `kpl_sentiment.df_num` | 市场情绪功能中的大幅回撤个股数；不是跌停家数 | 只 | 21 个成功响应中均为整数 1–24，且 21/21 均不同于同日 `MoodNumCount.DTJS` 和 `RiseFallAnalysis.info[0][1]` |
| `strong` | `raw_market_sources.kpl_sentiment.__raw_response__.info[0].strong`；归一化为 `kpl_sentiment.strong` | 市场情绪指标分值 | 未声明物理单位 | 21 个成功响应均为 0–100 内整数；同响应 `tip` 对情绪指标给出 75/25 阈值提示 |
| `lbgd` | `raw_market_sources.kpl_sentiment.__raw_response__.info[0].lbgd`；归一化为 `kpl_sentiment.lbgd` | 市场最高当前连续涨停板数（连板高度） | 板 | 20 个可比归档中，逐日最大 `raw_kpl.stocks[*].raw_columns.col_15` 与 `lbgd` 为 20/20 完全一致 |
| `Day` | `raw_market_sources.kpl_sentiment.__raw_response__.info[0].Day`；归一化为 `kpl_sentiment.day` | `ChangeStatistics` 响应附带的统计日期标签 | — | 21/21 与同批 `RiseFallAnalysis.date` 相同 |
| `date` | `raw_market_sources.kpl_broken_ratio.__raw_response__.info[0][6]`；归一化为 `kpl_broken_ratio.date` | `RiseFallAnalysis` 响应附带的统计日期标签 | — | 22/22 为可解析日期文本；其中 21/21 与 `ChangeStatistics.Day` 相同 |
| `tip` | `raw_market_sources.kpl_sentiment.__raw_response__.tip`；归一化为 `kpl_sentiment.tip` | 市场情绪指标的解释提示文本 | — | 21/21 成功响应均返回相同的提示文本，含 75/25 阈值说明 |

这些日期字段只表示相应响应携带的日期标签。采集目录名仅用于定位样本，不被当作来源实际数据日证据；本批不登记 `Day` 或 `date` 为 `as_of_date`，不更新 `temporal_policy.json`，也不允许它们为其他端点继承日期。

## 关键核验与历史冲突更正

### 涨停家数

`MoodNumCount.list.ZTJS` 与 `RiseFallAnalysis.info[0][0]` 在 22 个归档批次中 22/22 相等。`ChangeStatistics.info[0].ztjs` 有 21 个成功响应，其中 21/21 同时与两项相等；2026-10-26 的该接口请求失败，按错误处理，不当作空值或零。KPL 涨停明细的 `row_count` 有 21/22 与涨停家数相等；2026-10-15 的明细只有 30 行而统计为 36，且旧格式没有列完整性元数据及 `col_15`，因此不把这一个明细批次用于名单完备性比较，也不当作统计字段的反例。

### `df_num` 与大幅回撤

开盘啦官方页面明确把“大幅回撤个股数”列为市场情绪的一项，并说明其用于衡量追涨后的亏钱效应。项目适配器把 `ChangeStatistics.info[0].df_num` 与同响应的涨停数、情绪指标和连板高度一起采集。留存的 21 个有效 `df_num` 值均与两套同日跌停家数 (`DTJS`/`dt`) 不同，排除了旧参考表中将其写成“跌停数”的解释。故将其定为大幅回撤个股数；官网没有公布“大幅回撤”的阈值、证券范围和刷新规则，这些不在本次释义范围内。该结论是依据官方产品功能、精确运行路径和同批样本作出的来源内解释，不声称存在未公开的官方键级 schema。

### `strong` 与 `tip`

`strong` 在全部 21 个成功响应中为 24–98 的整数。相同 `ChangeStatistics` 响应返回的 `tip` 说明情绪指标高于 75 和低于 25 时的解释方向，且该提示在 21/21 中一致。这支持将 `strong` 定为情绪指标分值、`tip` 定为该指标说明文字；公式、是否经过平滑及阈值来源仍未公开，不把分值解释为百分比或概率。

### `lbgd` 的锚定验证

本次没有再用未定案文本列猜测板高，而是使用既有来源内已验证的 KPL `raw_columns.col_15`（当前连续涨停板数）。在 20 个 `ChangeStatistics` 成功且 `raw_kpl` 每行都含 `col_15` 的归档中，`lbgd` 逐日等于全体返回涨停股 `col_15` 的最大值，20/20 相等。2026-10-15 的旧明细不含 `col_15`，2026-10-26 的 `ChangeStatistics` 请求失败，均不纳入比较。

`col_18` 中的“N天M板”是窗口内涨停次数，不等于当前连续涨停板数；2026-11-06 的 KPL `col_15` 裁决已记录其反例。因此本次只用已验证的 `col_15`，不以 `col_18` 推翻或代替 `lbgd` 结论。比较范围是 `DailyLimitPerformance` 该批完整返回的涨停行；若上游改变名单范围或字段结构，应重新核验最大值逻辑。

## 更新边界与后续重启条件

- 本批只更新精确逐源语义，不建立任何跨源 `mappings`，不把 KPL 与 KPH 合并，也不更改采集路由。
- `df_num` 的回撤阈值和股票筛选范围、`strong` 的算法、`tip` 提示阈值的维护规则仍未知；只有出现官方字段级说明、可定位的官方页面数值或能区分当前解释的反例时才重开，不因每日重复样本而反复追查。
- `Day`/`date` 是响应日期标签，不是已验证的来源实际数据日锚；只有接口契约或具备逐批来源日期证据的审计，才可改变时效资格。
- `lbgd` 20/20 由已验证锚闭环；仅当 `DailyLimitPerformance` 的返回范围或 `col_15` 契约变化、出现同批反例时重开。
- 历史资料 [`field_source_reference.md`](../../field_source_reference.md) 中“`df_num=7跌停`”的映射已由保留期同批证据否定，已更正为本次定案释义；旧值不作为当前证明。
