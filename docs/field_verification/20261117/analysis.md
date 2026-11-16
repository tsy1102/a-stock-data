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

**结论：**东财官方历史页面已在 2026-11-16 核验 6 只股票的“炸板次数”，这 6 例均与 KPL 第 16 列的 0/1 指示关系一致；另有 216 组按 Push2EX 请求日配对的历史探索数据，四天均无反例，但 Push2EX 未回显来源日期，不能把全部 216 组当成正式同日证据。当前最强的候选解释是：KPL 第 16 列表示“当日炸板次数是否大于零”的二值状态，仍需将官方页面值与 KPL 精确原始路径建立完整可复核对应。KPL 官方未公开该字段标签，且 `field_registry.json` 尚无精确身份 `开盘啦(kpl_limit_up_detail)::raw_columns.col_16`；已有 `开盘啦(kpl)::IsBoom` 与 `开盘啦(kpl)::limit_up_broken_count` 是其他完整来源路径，不能按名字合并。故本轮不改主字典、不建跨源映射。后续需补登记精确路径，并用来源契约或覆盖全部可比 KPL 样本的官方页面观测按单源实证流程裁决。

## 本轮定案结果

- 主字典无新增字段定案：KPH 跨源候选缺少官方契约且仅有一日合格样本；KPL 第 16 列形成稳定的二值关系证据，但精确 KPL 官方字段释义和注册路径仍缺失；ETF 日期已由官方接口明确解释，但不属于当前注册表字段身份。
- 下一轮如要继续 KPH 映射，优先补可将 KPH 原始字段与官方产品定义直接对应的证据；仅增加相同来源日期的重复采集不能替代独立日期样本或接口契约。

## 授权补采后的 `ulist239.f149` 候选复核

- 随后的补采目标数据日仍为 2026-11-16。Eastmoney 返回 `ip_banned`，Ulist 没有新增来源日样本；因此本节使用留存的 Ulist、Eastmoney K 线和 ZHB raw，不把本次运行说成新增 Ulist 采集。
- 对碰撞报告中的 `ulist239.f149 ↔ zhb.stat2.change_mtd` 逐日核对后，2026-11-06 为 0/20、2026-11-09 为 20/20。11 月 9 日的滚动六个交易间隔恰好从 10 月 30 日起算，与月初至今使用同一基准，构成单日偶合。候选 `cc1_3541505a690aeb171f9c6a16db22c25988351cdda7e941190e71572f4f1f37d5` 已正式标记 `rejected`，只拒绝该跨源同义关系。
- 80 个来源日股票值与未复权 K 线复算表现为滚动六个交易间隔涨幅的强线索；300788 官方除息记录支持调整该窗口的历史基准，但仍有两行各差 0.01 个百分点。因 `ulist.np/get` 未公开 `f149` 字段标签，且残差计算口径未完全解释，来源内字段保持 `unverified`，不修改主字典。完整分析、逐行 CSV 和候选审阅记录见 [`20261117_ulist239_f149_mtd_candidate_rejection.md`](../adjudications/20261117_ulist239_f149_mtd_candidate_rejection.md)。
- 同轮检查了 `ulist239.f190 ↔ tdx.finance_info.hgu` 的 L4 95% 重合：40 组里 38 组只是 0=0；两个非零项均为 601288 跨相邻日重复，`f190=3` 与 `hgu=3,073,882.25` 不等，且 TDX 的来源实际数据日未确认。已记为 `insufficient_evidence`；不能把零值比例解释成语义支持。逐值表与审阅见 [`20261117_ulist239_f190_hgu_low_information_review.md`](../adjudications/20261117_ulist239_f190_hgu_low_information_review.md)。

## `ulist239.f192` 字段假设与拟合候选复核

- 读取 2026-11-05、11-06、11-09、11-10 四个保留目录的 Ulist `f297` 后，80 行中 76 行为 `f192=-1`，4 行为 `116`；后者全是 601288，只有一个不同的非占位股票样本。该结构支持追查 A/H 对应证券的市场号，但仍不足以来源内定案。
- 碰撞报告为此路径产生 25 条高相关/公式候选。它们只有一个不同的 `f192` 有效股票值，且 TDX/Tencent 的高拟合由同一 601288 样本驱动；25 项统一标为 `insufficient_evidence`，不等于证伪字段含义。第三方字段表把 f192 对应到 A/H 市场号，东方财富 A/H 页面核对了农行证券配对；官方字段契约或第二只 A/H 项目的原始样本仍缺。完整样本、候选清单和理由见 [`20261117_ulist239_f192_placeholder_outlier_review.md`](../adjudications/20261117_ulist239_f192_placeholder_outlier_review.md)。
