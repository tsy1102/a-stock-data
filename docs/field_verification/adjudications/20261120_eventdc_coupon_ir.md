# Eastmoney RPT_BOND_CB_LIST COUPON_IR 来源内定案

复核日期：2026-11-20。精确字段身份：东财-event_dc(可转债列表)::convertible_bonds[].COUPON_IR。

## 定案

- 规范名：bond_coupon_rate_current_interest_year_pct；单位：%。原值 2 表示 2.0%。
- 含义：按采样时点所处计息年度，从合同票面利率序列中选出的票面利率。计息年度按起息日 VALUE_DATE 的周年日切换。
- 该字段不表示债券当前仍存续或仍有应付利息。提前赎回、退市的记录仍可能按原始利率表继续滚动；它也不是到期收益率、实际收益率或利息金额。
- 不建立跨源映射。精确字段身份只覆盖 Eastmoney RPT_BOND_CB_LIST 返回路径。

## 代码与字段路径

- stock_common/sc_datasource/_convertible.py::convertible_bonds() 请求 Eastmoney Data Center RPT_BOND_CB_LIST，将响应行原始键保留；scripts/capture_context_collectors.py::collect_event_dc() 将其写入 raw_event_dc.json 的 convertible_bonds[]。
- _trace() 在响应返回后写入项目本地 fetched_at。它是采样观察时点，不是上游明确提供的 as_of_date。下列检验使用这个观察时间，不用目录名代替来源日期。
- 东方财富可转债详情页展示“起息日”“债券年度”和“利率说明”；发行人公告给出发行日期、票面利率逐年序列及计息年度规则：[鹤21转债详情页](https://data.eastmoney.com/kzz/detail/113632.html)、[寿22转债详情页](https://data.eastmoney.com/kzz/detail/113660.html)。

## 保留样本检验

核查 docs/field_verification/20261116 至 20261119 四份 raw_event_dc.json。每份均有500条可转债记录，其中261条 COUPON_IR 非空。逐行按该行本地 fetched_at 的北京时间日期、VALUE_DATE 已完整周年数，以及 INTEREST_RATE_EXPLAIN 中的逐年利率序列计算；四份快照分别为 **261/261 精确匹配**。总计1044条非空日样本均匹配，无例外。

逐行输入、期望利率、实际利率和匹配结果保存于[1044行审计 CSV](research/20261120_eventdc_coupon_ir_anniversary_audit.csv)。规范 LF SHA-256：0269e48454c592832dd88e2ea2b53b1e015289f3ae051c4afbd690d6fcaa5781。

两条跨周年样本直接验证了字段切换时间：

| 代码 / 债券 | 起息日 VALUE_DATE | 发行人公开利率序列 | 11月16日 | 11月17日起 |
|:--|:--|:--|--:|--:|
| 113632 鹤21转债 | 2021-11-17 | 0.3%、0.5%、1.0%、1.5%、1.8%、2.0% | 1.8 | 2.0 |
| 113660 寿22转债 | 2022-11-17 | 0.5%、0.8%、1.0%、1.5%、2.0%、2.5% | 1.5 | 2.0 |

仙鹤股份公告确认鹤21转债于2021-11-17发行，利率逐年为0.3%、0.5%、1.0%、1.5%、1.8%、2.0%：[2026-06-17公告](https://static.cninfo.com.cn/finalpage/2026-06-17/1225372960.PDF)。寿仙谷公告确认寿22转债于2022-11-17发行，利率逐年为0.5%、0.8%、1.0%、1.5%、2.0%、2.5%：[2026-11-14公告](https://static.cninfo.com.cn/finalpage/2026-11-14/1225671277.PDF)。两项数据于各自周年日后切到对应下一计息年度利率。

提前赎回样本说明字段不能被误用为“当前仍应付利率”。鹤21转债于2026-07-27赎回并摘牌；发行人公告明确本次赎回所在计息年度（2025-11-17至2026-11-16）的实际票面利率为1.8%：[赎回安排公告](https://static.cninfo.com.cn/finalpage/2026-07-22/1225434768.PDF)、[摘牌公告](https://static.cninfo.com.cn/finalpage/2026-07-24/1225438783.PDF)。但项目在2026-11-17之后采到的同一债券 COUPON_IR=2.0，这是原利率表下一个计息年度的值，不能解释为退市后仍有2.0%实际利息。淮22转债已于2024-04-03提前赎回摘牌；其2026-11-19归档行仍为 COUPON_IR=1.8，恰为起息日2022-09-14后按周年计算的第五年度利率：[赎回完成公告](https://static.cninfo.com.cn/finalpage/2024-04-04/1219515659.PDF)。

保留样本 SHA-256：

| 样本文件 | SHA-256 |
|:--|:--|
| 20261116/raw_event_dc.json | a5cd24596c82044172bca57ef4d2fb6b145e7afd7dda862df9b591f4dbbbdc37 |
| 20261117/raw_event_dc.json | a90631853d5a3f93f08c2af59f70fb9965c1e33ce237fd34782812287a035de2 |
| 20261118/raw_event_dc.json | 121aa5ef015340a4465679ecd593ca4be70149fbf571173bbd27d17cb3c58ab5 |
| 20261119/raw_event_dc.json | 736515264e120d739ba4d85f77a11513b98ab08218b5dc170d1d748e6729ce93 |

## 日期与适用边界

采集接口未给该值提供独立的 as_of_date；项目 fetched_at 只记录响应观察时间。此字段以起息日周年为周期变化，碰撞比较时必须按计息年度对齐，不能把自然日、交易日或目录日期直接当成字段生效日。即使含义已经定案，来源样本的生效年度仍须按 VALUE_DATE 和实际观察时点解释。

## 裁决依据

含义由 Eastmoney 原始响应键路径、东方财富详情页显示的起息日与利率说明、两项发行人正式利率公告，以及四日共1044条非空观测的逐行精确匹配共同支持。公开资料未给出内部 COUPON_IR 字段计算公式；本结论只定案观察到的“当前合同计息年度票面利率选择”行为，不外推为债券存续状态或实际付息事实。
