# 2026-11-17 采集后破解记录

## 本轮范围与数据日

- 自然日/采集运行日：2026-11-17；碰撞目标数据日：2026-11-16。
- 本次运行是 `missing_source_supplement`：KPH 于 2026-11-17 01:12:52 新采集，来源实际数据日为 2026-11-16，31 行完整返回，`pagination.complete=true`；ZHB 仍为 2026-11-13，按来源日期规则标记过期，不作为 11 月 16 日碰撞样本。目标目录里的 KPL 和 Push2EX 单元记录时间分别是 2026-11-16 21:27:38、21:28:41，并非本次补采新请求；东财其他请求被已持久化的 `ip_banned` 熔断状态抑制，没有重试。因此本轮新增正式来源样本是 KPH；KPL `col_16` 复核使用同数据日已归档的 KPL/Push2EX 值，不能称为本次新采集的两源样本。
- 复核报告：[`20261117_collision_report.md`](20261117_collision_report.md)；人工复核后的报告：[`kph_reviewed_20261117/20261117_collision_report.md`](kph_reviewed_20261117/20261117_collision_report.md)。两份报告完整，均无 L1/L1-C 新候选；18 个 L4 关系仍是探索线索。

## KPH × KPL 候选

- 11 月 16 日 KPH `industry_limit_up_count` 与 KPL `raw_columns.col_20` 在 31 对样本上 31/31 相等；行业 ID 30/31 相等。
- 纳入新日的历史诊断结果为计数 481/531 相等、行业 ID 527/531 相等。旧 KPH 样本没有完整分页证明，以上历史汇总只作诊断，不作为正式碰撞资格；正式报告只采用带分页完成标记的当日 KPH 样本。
- 开盘红没有找到公开的官方接口字段契约，第三方客户端文档只能提供线索。因此字段仍保持 `unverified`，候选 `cc1_5d69a92e08405bfcfcc024fabdb117ee0a85d5346fdacae12960ff1bc36150db` 已按 `needs_external_evidence` 复核；不建立 KPH→KPL 映射。完整依据见 [`adjudications/20261117_kph_industry_count_followup.md`](../adjudications/20261117_kph_industry_count_followup.md)。

## 日期候选的官方语义核验

本轮报告 `candidate_triage.date_value_candidates` 中的 `etf.date` 和 `etf.listing_date` 是上下文采集器输出，不是 `field_registry.json.source_fields` 中的破解字段身份；在注册表和未知字段队列中均没有 `etf` 来源路径。因此本节确认其业务含义和日期域，不写入主字典。

11 月 16 日归档 `raw_etf.json` 中，沪市 ETF 返回 924 行，行字段 `date` 全为 2026-11-13；深市 ETF 返回 772 行，`date` 全为 2026-11-16，且 772 行均有 `listing_date`。例如代码 158000 的数据日为 2026-11-16，上市日为 2026-08-26。这两个日期含义不同。

项目解析器 [`stock_common/sc_datasource/_etf.py`](../../../stock_common/sc_datasource/_etf.py) 对沪市按 `STAT_DATE` 请求，并要求每条响应记录的 `STAT_DATE` 等于请求日，输出 `date=day`。深市接口返回 `metadata.subname` 作为本次快照日，解析器输出 `date=snap[0]`；同时把响应字段 `ssrq` 原样输出为 `listing_date`。采集器因而保留来源实际数据日，不把调用时的自然日写作 ETF 数据日。

2026-11-17 在深交所官方基金列表接口核验到：响应 `metadata.subname` 为 `2026-11-16`、`recordcount` 为 772；同一响应的官方列元数据明确给出 `ssrq` = “上市日期”。接口第 1 页记录中，代码 158000 的 `ssrq` 为 `2026-08-26`，与归档值一致。[深交所官方基金列表接口](https://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1000_lf&TABKEY=tab1&selectJjlb=ETF&PAGENO=1&pagesize=2000)。上交所官方 ETF 规模页面按“日期”列示每日总份额，页面说明统计数据为当日清算后数据，与本项目按 `STAT_DATE` 标注的沪市数据日相符。[上交所 ETF 规模](https://www.sse.com.cn/market/funddata/volumn/etfvolumn/)。

**结论：**`etf.date` 表示基金份额记录对应的统计/快照日；沪市是被请求且经响应确认的统计日，深市是官方列表的当前快照日，可能早于或不同于运行自然日。`etf.listing_date` 表示该 ETF 在交易所上市的日期，不是基金成立日、报告期或采集日。该结论用于解释上下文数据的日期域，不增加注册表字段或跨源映射。

## KPL `raw_columns.col_16` 的布尔关系复核

本轮报告列出的探索方法候选为 `kpl.raw_columns.col_16` 对 `push2ex.broken_count`（方法候选 ID `cc1_839524d5cf77b99eaa05b6b0c187d1a4cda545c318ce68efa0cfd52575e07bb8`）。直接数字相等仅 151/216（69.91%），不支持把两个字段作为同值映射。进一步检查保留边界后的有效样本后，得到以下更有区分力的关系：

- 2026-11-09、11-10、11-12、11-16 的配对数依次为 54、93、37、32，共 216 组。KPL 行的 `trade_date` 与目录交易日一致；Push2EX 仅有采集时间或请求参数，响应没有来源日期回显，`capture_units.push2ex.limit_up_pool.source_as_of_date` 也为 `null`。因此这 216 组只能作为按请求日对齐的探索性比较，不能计作两侧来源日期均确认的正式碰撞样本。其他历史目录因缺少可与目标日匹配的 Push2EX 日期元数据（11-06 元数据日期指向 11-08）而未纳入。
- `source_lineage.json` 将 KPL 明细和东财 Push2EX 列为不同且已确认的来源族，因此这些数值配对不是同一来源的重复转存；网页只用于确认东财 `broken_count` 的官方列标签和值。
- `col_16` 在 216 行中只观察到 0 或 1；107 行为 0，109 行为 1。对所有配对，`col_16 == (broken_count > 0)`，即 216/216；数值不等的 65 行全部是 `col_16=1` 而 `broken_count>1`。因此证据支持“二值标记与当日炸板次数是否大于零一致”，不支持将二者登记成同一数值字段。
- 通过 Chrome 将东方财富官方涨停池页面日期选为 2026-11-16，直接抽核 6 只股票：“炸板次数”显示 000819=10、002148=7、002419=2、002356=3、002905=0、002548=0；与同日 Push2EX raw 精确一致，并且 KPL `col_16` 分别为 1、1、1、1、0、0。逐股网页观测及 KPL 并列值见 [`20261117_kpl_col16_em_page_observations.md`](../adjudications/public_web/20261117_kpl_col16_em_page_observations.md)。这为当天样本提供了官方页面佐证，但不能替代 KPL 自身字段定义。
- 2026-11-16 当日 KPL 涨停明细中 18 行 `col_16=1`；东财另一个 `limit_broken_pool` 集合与这些股票无交集。该观察说明不能把 `col_16` 直接等同于该池成员；它与已验证的涨停池 `broken_count`（官方页面“炸板次数”）关系更直接。现有东财裁决文件已记录该字段路径、官方页面标签与采集路径。[Push2EX `broken_count` 官方页面观测记录](../adjudications/public_web/20261114_public_web_research.md)
- KPL 官方主页只提供产品介绍和 App 入口，没有公开 `DailyLimitPerformance` 的字段字典；已查阅的第三方 [KPL 接口说明](https://github.com/LowellLee/kpl/blob/master/KPL%E6%8E%A5%E5%8F%A3.md)说明了该接口和 `PidType` 梯队，但没有定义第 16 列。因此它只能支持接口识别，不能当作 KPL 官方字段释义。[开盘啦官网](https://www.kaipanla.com/)

**阶段结论（早期复核状态）：**当时只有 6 只股票的官方页面抽核，且尚未登记 `开盘啦(kpl_limit_up_detail)::raw_columns.col_16`；因此当时没有定案。后续完整页面复核与登记结果见本文末尾“收盘后 KPL `col_16` 定案与回归”，该更新取代本段的待办状态。

## 本轮定案结果

- 截至这轮早期研究，主字典没有新增字段定案：KPH 跨源候选缺少官方契约且仅有一日合格样本；KPL 第 16 列的完整路径和全量官方页面对照尚未补齐；ETF 日期已由官方接口明确解释，但不属于当前注册表字段身份。KPL 结论后来已按下方续研完成来源内定案。
- 下一轮如要继续 KPH 映射，优先补可将 KPH 原始字段与官方产品定义直接对应的证据；仅增加相同来源日期的重复采集不能替代独立日期样本或接口契约。

## 授权补采后的 `ulist239.f149` 候选复核

- 随后的补采目标数据日仍为 2026-11-16。Eastmoney 返回 `ip_banned`，Ulist 没有新增来源日样本；因此本节使用留存的 Ulist、Eastmoney K 线和 ZHB raw，不把本次运行说成新增 Ulist 采集。
- 对碰撞报告中的 `ulist239.f149 ↔ zhb.stat2.change_mtd` 逐日核对后，2026-11-06 为 0/20、2026-11-09 为 20/20。11 月 9 日的滚动六个交易间隔恰好从 10 月 30 日起算，与月初至今使用同一基准，构成单日偶合。候选 `cc1_3541505a690aeb171f9c6a16db22c25988351cdda7e941190e71572f4f1f37d5` 已正式标记 `rejected`，只拒绝该跨源同义关系。
- 80 个来源日股票值与未复权 K 线复算表现为滚动六个交易间隔涨幅的强线索；300788 官方除息记录支持调整该窗口的历史基准，但仍有两行各差 0.01 个百分点。因 `ulist.np/get` 未公开 `f149` 字段标签，且残差计算口径未完全解释，来源内字段保持 `unverified`，不修改主字典。完整分析、逐行 CSV 和候选审阅记录见 [`20261117_ulist239_f149_mtd_candidate_rejection.md`](../adjudications/20261117_ulist239_f149_mtd_candidate_rejection.md)。
- 同轮检查了 `ulist239.f190 ↔ tdx.finance_info.hgu` 的 L4 95% 重合：40 组里 38 组只是 0=0；两个非零项均为 601288 跨相邻日重复，`f190=3` 与 `hgu=3,073,882.25` 不等，且 TDX 的来源实际数据日未确认。已记为 `insufficient_evidence`；不能把零值比例解释成语义支持。逐值表与审阅见 [`20261117_ulist239_f190_hgu_low_information_review.md`](../adjudications/20261117_ulist239_f190_hgu_low_information_review.md)。

## `ulist239.f192` 字段假设与拟合候选复核

- 读取 2026-11-05、11-06、11-09、11-10 四个保留目录的 Ulist `f297` 后，80 行中 76 行为 `f192=-1`，4 行为 `116`；后者全是 601288，只有一个不同的非占位股票样本。该结构支持追查 A/H 对应证券的市场号，但仍不足以来源内定案。
- 碰撞报告为此路径产生 25 条高相关/公式候选。它们只有一个不同的 `f192` 有效股票值，且 TDX/Tencent 的高拟合由同一 601288 样本驱动；25 项统一标为 `insufficient_evidence`，不等于证伪字段含义。第三方字段表把 f192 对应到 A/H 市场号，东方财富 A/H 页面核对了农行证券配对；官方字段契约或第二只 A/H 项目的原始样本仍缺。完整样本、候选清单和理由见 [`20261117_ulist239_f192_placeholder_outlier_review.md`](../adjudications/20261117_ulist239_f192_placeholder_outlier_review.md)。

## 04:11 授权补采后的续研

- 运行自然日/采集日为 2026-11-17，目标数据日为 2026-11-16。04:11:39 启动后，东财 `push2`、`em_kline_f61`、`em_fund_flow`、`ulist239`、`clist`、`slist` 均被既有 `ip_banned` 熔断拦截，诊断为 `attempts=0`；没有强制重试。`st_list` 返回 313 条，但没有来源实际日期且不含 Ulist 字段，不能增加 `f192` 证据。ZHB 没有在 08:00 前补采，归档来源日仍是 2026-11-13。运行和各源日期/状态见 [`20261116/meta.json`](../20261116/meta.json)。
- **窗口错误更正：**`capture_0411` 以及同日早先的 `post_capture_0230`、`capture_0508` 系列、`capture_0656_after_capture_v4` 和本轮初次生成的 `preopen_0908` 均把尚未完成的 2026-11-17 纳入 7 日窗口，实际遗漏了已完成的 2026-11-06。它们的 JSON 完整性状态只表示报告结构完整，不表示窗口选择正确；这些同日 7 日报告不得用于当前碰撞结论。保留原报告作为审计历史，正确窗口报告见 [`preopen_completed_0917/20261117_collision_report.md`](../20261117/preopen_completed_0917/20261117_collision_report.md)。该报告按 2026-11-16 最近已完成交易日取 7 个交易日；全历史初始复核见 [`preopen_all_history_0950/20261117_collision_report.md`](../20261117/preopen_all_history_0950/20261117_collision_report.md)，候选审阅后的最终报告见 [`preopen_all_history_reviewed/20261117_collision_report.md`](../20261117/preopen_all_history_reviewed/20261117_collision_report.md)。
- 对保留边界内全部 19 份 Ulist raw 再扫描后，确认 7 份各含 20 条股票记录，共 140 条：`f192=-1` 有 133 条、`f192=116` 有 7 条；7 条 `116` 仍全为 601288。4 个 `f297` 与目录日一致的数据日提供 80 条合格样本；另 3 条 601288 的 `116` 位于 11 月 2–4 日 raw，但缺少 `f297`，已排除。逐目录摘要见 [`research/20261117_ulist239_f192_retention_scan.csv`](../research/20261117_ulist239_f192_retention_scan.csv)。

**续研结论：**本次采集没有增加 `f192` 的来源样本，历史全量复扫也没有找到第二只正值股票。A/H 市场号仍是有第三方字段表和农行官方证券页面共同支持的强语义假设，但当前证据不能验证接口字段身份与一般适用性；注册表和主字典继续保持不变。下一项有区分力的证据应是另一只 A/H 发行人的合格 Ulist 原始记录，或东方财富对 `ulist.np/get` 的正式字段定义。

## ZHB-tipinfo `[17]` / `[18]` 留存窗口复核

扫描了保留起点 2026-10-15 之后全部 20 个 ZHB 日期包，`tipinfo.dat` 共 113,098 行；每行均为 22 列且代码唯一。原始列 `[17]`、`[18]` 均为 0 个非空值。它们在当前留存窗口内属于低信息字段，仍标记 `unverified`，不把通达信公式函数 `DYNAINFO(17/18)` 的定义误套到 ZHB 文件列，也不推断为永久无意义占位符。明细见 [`adjudications/20261117_zhb_tipinfo_17_18_low_information_review.md`](../adjudications/20261117_zhb_tipinfo_17_18_low_information_review.md) 和 [`research/20261117_zhb_tipinfo_17_18_retention_scan.csv`](../research/20261117_zhb_tipinfo_17_18_retention_scan.csv)。本次没有发现足以更新主字典语义的证据。

## ZHB-tipinfo `[13]` / `[14]` 限售股上市流通字段

从 2026-11-16 目录读取 ZHB 来源日期为 2026-11-13 的样本，按精确解析位置核对贵州茅台、农业银行两只股票。`unlock_date` 分别为 `20090525`、`20230703`；`unlock_shares_wan` 分别为 `48867.90`、`1995967.25`。两家发行人公告均明确列出限售股上市流通日期和总股数：茅台 488,679,034 股、农业银行 19,959,672,543 股。换算为万股并按 0.01 万股精度四舍五入后，数量差分别为 34 股和 43 股，均在半个量化步长内；日期均精确命中。

据此将 `[13]` 的来源内含义定为限售股解禁/上市流通事件日（`YYYYMMDD`），`[14]` 定为该事件上市流通数量（万股）。样本支持事件日期和数量单位，不足以说明多事件时的选取顺序；其他 18 只样本未在本轮逐项核对。详细计算、原始样本哈希和官方公告见 [`adjudications/20261117_zhb_tipinfo_unlock_semantics.md`](../adjudications/20261117_zhb_tipinfo_unlock_semantics.md)。

## L4 共同空值误报修正

本轮发现旧规则将 `tencent[29]` / `tencent[55]` 与 `zhb.tipinfo.forecast_type` 的共同缺失配对显示为 100% L4。旧样本的 20 对没有信息配对；它们不构成语义证据。L4 现要求每个数据日至少 8 个信息配对，只按信息配对算命中率，并排除恒定字段；报告列出配对总数和信息配对数。候选身份版本升至 v4，旧 v1–v3 报告仍可校验。旧报告候选标记为证据不足，不作语义拒绝。

修复后按同一份 2026-11-16 目标数据生成 v4 报告：5 个采集目录、7 个有效交易日、1,292 个字段和 313,896 个值；L1/L1-C 均为 0，L4 为 12。12 个关系每天至少有 8 个信息配对；此前两个 Tencent 共同空值项均已消失。完整报告见 [`capture_0508_v4_final/20261117_collision_report.md`](../collision_research_20261117/exploratory/20261117/capture_0508_v4_final/20261117_collision_report.md)。因身份算法升至 v4，新候选 ID 不继承 v3 人工审阅；报告机器完整性为 complete，尚未审阅项继续作为探索候选，不作定案。

## 2026-11-17 08:14 开盘前采集与 `f126` 来源内定案

- 本次运行自然日为 2026-11-17，开盘前目标交易数据日为 2026-11-16。ZHB 在 08:14 成功返回 20/20 股票，`as_of_date=20261116`，与 ZHB 文件日期一致；`raw_zhb.json` SHA-256 为 `EC1048D2F7E7DD4DF246A61D2B62D4F32ABB0A327D175E24C6C73425717CCF7E`。Eastmoney `push2`、`em_kline_f61`、`em_fund_flow`、`ulist239`、`clist`、`slist` 均在请求前被现有 `ip_banned` 熔断器拦截（`attempts=0`）。
- `meta.json` 标记 `previous_probe_snapshot_preserved=true`：当前 `raw_push2.json` 是 2026-11-16 21:25:38 的旧快照，来源日期为 `null`；本轮 Push2 20/20 未发出请求。因此不将该快照冒充为 11 月 17 日新采集，也不把它纳入正式日期样本。
- 新 ZHB 的茅台、农业银行 `full.dividend_yield` 分别为 1.93、3.42。结合本轮碰撞报告的股息率线索，我于 08:24:40 通过 Chrome 核对东方财富官方 `stock/get` 接口和两只股票的 F10 分红融资页：`data.f126` 同为 1.93、3.42，F10 标签为“股息率”，更新日均为 11 月 16 日，页面定义也与该字段口径相符。两项官网比较均精确命中。旧 Push2 快照中另有 10 个数值型 `f126`，与新 ZHB 值 9/10 相同、万华化学一项不同，另有 3 个 `-` 占位；因旧快照来源日期为空，这仅作为诊断线索，不进入裁决样本。
- 依单源实证流程定案 `东财-push2(stock/get)::f126` 为股息率（%），证据和逐项链接见 [`adjudications/20261117_push2_f126_dividend_yield_evidence.md`](../adjudications/20261117_push2_f126_dividend_yield_evidence.md)。此决定仅确认 `stock/get` 精确路径，不确认 Tencent `[64]`、Ulist239 `f133`、ZHB 或其他接口映射；应用器报告 `mappings_added=0`。
- 最新碰撞报告 [`capture_0814_after_push2_f126_semantics/20261116_collision_report.md`](../collision_research_20261116/exploratory/20261116/capture_0814_after_push2_f126_semantics/20261116_collision_report.md) 覆盖 7 个交易日、1,295 个字段及 392,531 条样本值。`f126` 从 `unverified` 主攻目标中退出，主攻未知字段从 128 降为 127；本轮 L1/L1-C 均为 0、L4 从 10 降为 7，未产生新的数值定案。`ulist239.f63` 仍是优先破解项，但当前 Ulist 没有新的来源日样本，不能据本次 ZHB 刷新宣称取得新的 `f63` 证据。

## 2026-11-17 官方行情页内外盘核验

- 按官方页面中文标签、项目精确响应路径和同日总成交量校验，来源内定案 `东财-push2(stock/get)::f49/f161` 为外盘/内盘成交量（手），以及 `腾讯(qt.gtimg)::[7]/[8]` 为外盘/内盘成交量（手）。茅台与农行两例分别匹配对应页面，且两组字段之和均等于页面总成交量。
- 结论各自限定于对应来源路径。东财 `f49/f161` 与腾讯 `[7]/[8]` 标签相同，不代表逐笔分类算法相同或存在跨源等值映射；证据及不一致替代假设见 [`adjudications/20261117_eastmoney_push2_volume_sides.md`](../adjudications/20261117_eastmoney_push2_volume_sides.md) 和 [`adjudications/20261117_tencent_outer_inner_volume_semantics.md`](../adjudications/20261117_tencent_outer_inner_volume_semantics.md)。

## 2026-11-17 09:09 开盘前补采与窗口校正

- 运行自然日为 2026-11-17，目标数据日为 2026-11-16。09:09:13 的补采复用 08:14 已确认的 ZHB `as_of_date=20261116`、20/20 样本；东财 `push2`、`em_kline_f61`、`em_fund_flow`、`ulist239`、`clist`、`slist` 均被既有熔断器在请求前拦截，`attempts=0`。没有发出强制重试；Push2 旧快照的来源日期为 `null`，不作为新样本。其他已归档来源日期按 `meta.json` 中的来源字段核对，不能把运行自然日当成来源实际数据日。
- 发现碰撞日期选择函数在报告日期等于当前自然日时，将当前尚未收盘交易日算作已完成日。修复后，报告日期与行情截止日分开计算：开盘前/盘中报告只截至最近已收盘交易日，历史显式报告日仍按该日处理。对应实现见 `scripts/collision_dates.py`、`scripts/collide.py`、`scripts/collision_reporting.py`；定向回归已通过（25 项日期测试、66 项碰撞测试）。
- 修正后的 7 日报告选择 `20261106, 20261109, 20261110, 20261111, 20261112, 20261113, 20261116`，报告完整；全历史报告覆盖 2026-10-15 至 2026-11-16 共 21 个交易日，也报告完整。全历史报告有 153 个未知目标、1,344 个锚字段、1,413,022 个样本值；L1/L1-C 为 0、L4 为 5、方法候选 1,111 条，没有新候选对。碰撞报告先生成，再审阅 `f11` 候选并生成带审阅状态的最终全历史报告；该报告显示 1 条已审阅、1,115 条待审阅，`f11 ↔ 腾讯[80]` 为 `needs_external_evidence`。报告路径为 [`preopen_completed_0917/20261117_collision_report.md`](../20261117/preopen_completed_0917/20261117_collision_report.md) 与 [`preopen_all_history_reviewed/20261117_collision_report.md`](../20261117/preopen_all_history_reviewed/20261117_collision_report.md)。

## Ulist `f11` / `f63` 本轮破解结果

- `东财-ulist239(np/get)::f11` 与已验证的 `腾讯(qt.gtimg)::[80]`“涨速（%）”有较强的跨源实证线索：7 个来源日期确认的交易日、140 对样本，122 对有信息量；80 对精确相等，Pearson 0.987、Spearman 0.9721。逐对值、两侧时间戳和 raw 哈希见 [`research/20261117_ulist239_f11_tencent_candidate_audit.csv`](../research/20261117_ulist239_f11_tencent_candidate_audit.csv)。但时间戳差异较大，且东方财富公开页面的 `zs` 标签没有映射到 Ulist 的 `f11`。网页研究见 [`adjudications/public_web/20261117_public_web_research.md`](../adjudications/public_web/20261117_public_web_research.md)；候选 `cc1_25aa1fb7bb4504e28c28ed1e5bcf386c4b576891bf95217f17af9b2e6c09e3bc` 已记为 `needs_external_evidence`。主字典不变，待补的是 `ulist.np/get` 精确响应键到官方涨速标签的映射或同日官方逐值样本。
- `东财-ulist239(np/get)::f63` 在 2026-11-06、09、10 的 60 条可比样本中均为正，但没有与同日 `em_fund_flow f135–f149` 任一字段精确相等；其与成交额的比例只作为探索性量级指标，不确认单位或含义。11 月 10 日东方财富贵州茅台资金流页面显示的主力净流入与 `f62` 在页面显示精度内吻合，`f63` 不对应页面显示的主力/分档指标。逐值材料见 [`research/20261117_ulist239_f63_recent_window_audit.csv`](../research/20261117_ulist239_f63_recent_window_audit.csv)。`f63` 继续保持 `unverified`，没有更新主字典。
- Chrome 浏览器核验尝试在工具安全层被终止：工具无法充分确认当前浏览器 URL，并要求停止本轮 Computer Use。没有绕过安全限制。本节当时的网页结论以已读取的公开官方页面/页面脚本信息及历史留存样本为研究线索；后续 KPL 全量页面核验另见下文。

## 2026-11-17 收盘后采集、KPL `col_16` 定案与回归

- 本次单独运行采集的实际记录是 15:36:09 启动、`market_phase=closed`、`data_date=20261117`，耗时 450.9 秒；因此按运行记录归为收盘后采集。ZHB 返回 20/20，但来源实际日期是 2026-11-16；东财 Push2、K 线、资金流、Ulist 等端点都被既有 `ip_banned` 熔断器在请求前阻止（`attempts=0`），没有重试。KPL `DailyLimitPerformance` 返回 37 行，来源日期为 2026-11-17。完整运行状态见 [`meta.json`](meta.json)。
- 在[东财官方涨停股池](https://quote.eastmoney.com/ztb/detail)将日期分别选为 2026-11-12、11-16、11-17，并展开至“无更多数据”。三个完整页面分别为 37、32、37 行，股票代码集合和同日 KPL raw 完全相同；106 条逐股记录均满足 `KPL col_16 == int(炸板次数 > 0)`，没有反例，94 只不同股票。`col_16` 仅为 0/1；炸板次数直接相等只有 65/106，因此不能把它登记为次数。
- 按此证据将精确来源路径 `开盘啦(kpl_limit_up_detail)::raw_columns.col_16` 定案为当日是否曾发生炸板的二值状态（无量纲 0/1），canonical 为 `has_intraday_limit_up_break`。KPL 未公开原始列标签；这是来源内实证释义，不是 KPL 官方接口契约。此前 216 组 KPL/Push2EX 请求日配对仍因 Push2EX 来源实际日期未确认而仅作探索，不计入正式样本；未建立跨源数值映射。逐值、网页时间和 KPL raw 摘要见 [`adjudications/20261117_kpl_col16_empirical_semantics.md`](../adjudications/20261117_kpl_col16_empirical_semantics.md)、[`adjudications/20261117_kpl_col16_samples.csv`](../adjudications/20261117_kpl_col16_samples.csv) 与 [`adjudications/20261117_kpl_col16_empirical_semantics.json`](../adjudications/20261117_kpl_col16_empirical_semantics.json)。
- 重新碰撞发现 `ZHB-tipinfo::[14]` 虽已验证为限售股上市流通数量（万股），但适配器键 `tipinfo.unlock_shares_wan` 未映射回该精确路径，仍以未知目标产生拟合候选。修复 [`scripts/collision_registry_context.py`](../../../scripts/collision_registry_context.py) 的原始列到运行时键映射并增加回归用例后，该键作为已验证锚而不再成为破解目标。
- 最终 7 日报告覆盖 2026-11-09 至 11-17，完整性为 `complete`；主攻未知目标由 145 先因 KPL 定案降为 144，再因 ZHB 已验证别名回连降为 143。最终报告为 [`after_kpl_col16_and_zhb_tipinfo14_alias/20261117_collision_report.md`](after_kpl_col16_and_zhb_tipinfo14_alias/20261117_collision_report.md)：L1/L1-C 为 0，L4 为 3，未发现其他可据本轮数据直接定案的候选。
