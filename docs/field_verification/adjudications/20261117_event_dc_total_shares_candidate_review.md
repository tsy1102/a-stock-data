# IPO 日历 `TOTAL_SHARES` 候选关系复核

复核时间：2026-11-17 11:26 Asia/Shanghai。此记录只处理碰撞候选关系，不为未登记的 `event_dc.TOTAL_SHARES` 建立字段定义或注册表身份。

## 报告与字段路径

- 完整碰撞报告：[`preopen_20261117_1105/20261117_collision_report.json`](../20261117/preopen_20261117_1105/20261117_collision_report.json)，SHA-256：`9399bc82b19ffb96eac3cdec9d18795b3a7fc31072bf1b8fc68da046ecf7edcc`；报告完整性为 `complete`。
- 左侧值来自 `raw_event_dc.json::ipo_calendar[*].TOTAL_SHARES`。`stock_common/sc_datasource/_events.py` 将 IPO 日历路由到东方财富数据中心 `RPTA_APP_IPOAPPLY`；记录同时含 `LISTING_DATE`。它不是每个交易日更新的股票总股本快照。
- 右侧值来自 `raw_ftshare_rest.json::stocks[code].shares`、`float_a_shares` 或行情指标。
- 报告对 `event_dc.TOTAL_SHARES` 的来源覆盖为 `source_count=0`、`source_as_of_days=[]`，没有可确认的来源有效日；`field_registry.json` 也没有这个简写身份。不得将该候选路径直接写入主字典。

## 看似强相关的原因

报告为该目标列出 8 个 FTShare 候选关系。每个关系都只有证券 `000007` 和 `000011` 两个不同股票，样本数 32 是这两个历史 IPO 日历值在 16 个交易日期键上重复出现。报告给 `TOTAL_SHARES` 与当前 `shares` 的 Pearson、Spearman 和仿射公式 `R²` 均报 1.0；两个不同数值点总能被一条直线完全拟合，这些重复日期没有增加独立的 IPO 样本或来源日期证据。

保留期内 raw 核查显示，IPO 日历的两个值在 17 份日期化上下文采集中保持不变；FTShare 的当前值在 16 个可比采集日保持不变。该历史重复用于识别候选生成的统计假象，不作为独立日期碰撞证据。

## 两只股票的官方资料与样本

| 股票 | IPO 日历 `TOTAL_SHARES` | IPO 日历上市日 | FTShare 当前 `shares` | `float_a_shares` |
|---|---:|---|---:|---:|
| 000007 全新好 | 15,833,500 | 1992-04-13 | 346,448,044 | 346,448,044 |
| 000011 深物业 A | 257,511,890 | 1992-03-30 | 595,979,092 | 526,475,543 |

- 全新好 2025 年公司章程记载其 1992 年上市的普通股总数为 2,123.35 万元，并记载当前已发行股份 346,448,044 股。当前 FTShare `shares` 与章程当前股数一致；IPO 日历样本 15,833,500 则既不等于当前股数，也与章程所述上市普通股总数不一致。[公司章程](https://static.cninfo.com.cn/finalpage/2025-04-25/1223275562.PDF)
- 深物业的估值报告记载，截至 1992-01-31 实收股本为 25,751.189 万元，和 IPO 日历值 257,511,890 一致；这支持该样本具有历史股本口径。深物业 2018 年年度报告以 595,979,092 股为利润分配基数，和 FTShare 当前 `shares` 一致。[估值报告](https://static.cninfo.com.cn/finalpage/2007-02-01/20603692.PDF)、[2018 年年度报告摘要](https://static.cninfo.com.cn/finalpage/2019-03-30/1205965131.PDF)
- 全新好 IPO 日历值与公司章程不一致，说明不能仅凭 Eastmoney 键名和单只股票样本，把该完整来源路径定为“IPO 时总股数”。其确切接口字段口径仍待核。

## 候选处置

将下列 8 个候选关系逐项标为 `rejected`：

1. `event_dc.TOTAL_SHARES` ↔ `ftshare_rest.shares`：前者来自 IPO 日历历史记录，后者是 2026-11-16 的当前总股数；两只股票均明显不同。
2. `event_dc.TOTAL_SHARES` ↔ `ftshare_rest.float_a_shares`：历史 IPO 日历计数与当前流通股数不是同一时间或口径。
3. `event_dc.TOTAL_SHARES` ↔ `ftshare_rest.volume`、`turnover_rate`、`turnover`、`change_rate_ytd`、`change_rate_day60`、`change_rate_day120`：字段量纲或时间语义不同；两点重复形成的相关性不构成关系证据。

这只拒绝上述字段对，不表示 `event_dc.TOTAL_SHARES` 已被定义、证伪或成为可用字典锚；不更新主字典、不新增 `mappings`。后续应先核实 IPO 日历精确字段口径及全新好历史记录差异，再决定是否登记其完整路径。

候选 ID 与处置写入同目录的 `20261117_event_dc_total_shares_candidate_reviews.json`，由 `review_collision_candidates.py` 按稳定候选身份追加至审阅台账。
