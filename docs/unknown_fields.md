# 未知字段与状态冲突队列

> 由 `field_registry.json.source_fields` 自动生成；每行身份是来源加完整 code path。
> 修改状态必须先核对 `reference_evidence` 与 `registry_aggregate`，并保留证据来源。
> 碰撞候选须人工复核后使用 `apply_collision_adjudications.py` 同步状态；流程见 `field_verification/ADJUDICATION_WORKFLOW.md`。
> 聚合层的同码异义与定义缺口见 [`field_aggregate_review.md`](field_aggregate_review.md)，不代表逐源记录状态冲突。

> 注册字段路径 2550；日常来源路径 2406：unverified 1387、candidate 1、conflict 81、disproved 2；历史来源路径 144。
> 另有 182 条虽标 verified、但含义/单位元数据未达到碰撞锚条件；这些记录会重新进入碰撞目标，详见 [字段元数据复核](field_metadata_gaps.md)。
> 以下两组未验证字段统计是不同维度，不能相加：含义栏文本只表示存在文字，不代表语义正确；状态判定反映旧字典状态证据能否映射到逐源身份。

## 未验证字段的复核分层

### 含义栏状态（仅表示文字是否存在）

| 分类 | 数量 |
|:--|--:|
| 含义栏为空/占位 | 1203 |
| 含义栏有文本（仍未验证） | 184 |

### 历史状态证据的解析结果

| 状态判定 | 数量 | 说明 |
|:--|--:|:--|
| `aggregate_status_scope_unresolved` | 458 | 历史聚合状态尚不能可靠映射到逐源身份 |
| `live_observed_not_documented` | 1 | 按注册表原始状态判定代码保留 |
| `matched` | 59 | 历史逐源状态与聚合状态一致，但仍未定案 |
| `reference_status_missing` | 35 | 按注册表原始状态判定代码保留 |
| `registry_status_only_single_source` | 791 | 只有来源自身状态，历史聚合信息不足以进一步归属 |
| `status_missing` | 43 | 缺少可用的历史状态记录 |

## 一、状态冲突（禁止作为锚点，优先复核）（81）

| 来源 | 完整 code path | 规范名 | 含义 | 单位 | 含义栏提示 | 状态判定 | 证据章节 |
|:--|:--|:--|:--|:--|:--|:--|:--|
| ZHB-tdxstat | `stat.unknown_26` | stat.unknown_26 | 年内涨停天数 YearZTDay·L2候选(列[26]已定YearZTDay: ihelp.dat L64官方定义+事件级Δ实证, 待≥90%命中升L1) | - | 含义栏有文本（仍未验证） | status_conflict | 1.1 tdxstat.cfg 标准契约表（stat.*，20260918 对撞定案）🆕 |
| reports | `attachPages` | — | — | — | 含义栏为空/占位 | reference_status_conflict | 12.8.4 东财 reportapi（个股/行业研报 + PDF）✅；12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `attachSize` | — | — | — | 含义栏为空/占位 | reference_status_conflict | 12.8.4 东财 reportapi（个股/行业研报 + PDF）✅；12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `author` | — | — | — | 含义栏为空/占位 | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `emRatingCode` | — | — | — | 含义栏为空/占位 | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `emRatingValue` | — | — | — | 含义栏为空/占位 | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `encodeUrl` | encodeUrl | — | — | 含义栏为空/占位 | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `lastEmRatingName` | lastEmRatingName | — | — | 含义栏为空/占位 | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `newIssuePrice` | — | — | — | 含义栏为空/占位 | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `newListingDate` | — | — | — | 含义栏为空/占位 | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `newPeIssueA` | — | — | — | 含义栏为空/占位 | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `predictNextTwoYearPe` | — | — | — | 含义栏为空/占位 | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `predictNextYearPe` | — | — | — | 含义栏为空/占位 | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `predictThisYearPe` | — | — | — | 含义栏为空/占位 | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `researcher` | — | 研究员姓名 | — | 含义栏有文本（仍未验证） | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| 东财-clist | `f136` | f140 / f136 | 领涨股名称 / 领涨涨跌幅 | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.6 东财 clist（板块排名/板块资金流）✅ |
| 东财-datacenter(英文键) | `margin_trading.balance_gr` | margin_trading.balance_gr | 融资余额单日环比增长率(%) | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `margin_trading.chg_10d` | margin_trading.chg_10d | 标的证券近 10 日区间累计涨跌幅(%) | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `margin_trading.chg_5d` | margin_trading.chg_5d | 标的证券近 5 日区间累计涨跌幅(%) | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `margin_trading.rqjmg` | margin_trading.rqjmg | 融券净卖出量（股） | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `margin_trading.rzche_10d` | margin_trading.rzche_10d | 融资偿还额近 10 日累计（元） | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `margin_trading.rzche_5d` | margin_trading.rzche_5d | 融资偿还额近 5 日累计（元） | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `margin_trading.rzjme` | margin_trading.rzjme | 融资净买入额（元） | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `margin_trading.rzmre_10d` | margin_trading.rzmre_10d | 融资买入额近 10 日累计（元） | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `margin_trading.rzmre_5d` | margin_trading.rzmre_5d | 融资买入额近 5 日累计（元） | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `northbound_hold.change_ratio` | northbound_hold.change_ratio | 较上一期持股比例增减变动幅度(%) | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `northbound_hold.change_shares` | northbound_hold.change_shares | 较上一期持股增减变动数(股) | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `northbound_hold.date` | northbound_hold.date | 北向持股快照报告期(YYYY-MM-DD) | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `northbound_hold.hold_ratio` | northbound_hold.hold_ratio | 北向持股占流通股本比例(%) | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `northbound_hold.hold_shares` | northbound_hold.hold_shares | 北向持股总数(股) | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `northbound_hold.market_cap` | northbound_hold.market_cap | 北向持股市值(元) | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-em_kline_f61 | `f59` | f59 | 涨跌幅 | % | 含义栏有文本（仍未验证） | status_conflict | 12.3.3 日K线 `stock/kline/get`（🆕 V17.0.14 新增——CYQ 筹码分布数据入口） |
| 东财-push2(stock/get) | `f135` | f135 | — | 元 | 含义栏为空/占位 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-push2(stock/get) | `f136` | f136 | — | 元 | 含义栏为空/占位 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-push2(stock/get) | `f138` | f138 | — | 元 | 含义栏为空/占位 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-push2(stock/get) | `f139` | f139 | — | 元 | 含义栏为空/占位 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-push2(stock/get) | `f149` | — | 待破解 | 元 | 含义栏为空/占位 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**）；12.9.1 push2 stock/get 全字段破解（114 字段实测，项目只用 19 个） |
| 东财-push2(stock/get) | `f59` | f59 | 涨跌幅 | % | 含义栏有文本（仍未验证） | reference_status_conflict | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池）；12.3.3 日K线 `stock/kline/get`（🆕 V17.0.14 新增——CYQ 筹码分布数据入口） |
| 东财-ulist239(np/get) | `f135` | — | 净资产 | — | 含义栏有文本（仍未验证） | reference_status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f137` | — | — | — | 含义栏为空/占位 | status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f139` | — | — | — | 含义栏为空/占位 | reference_status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f140` | — | — | — | 含义栏为空/占位 | status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f141` | — | — | — | 含义栏为空/占位 | status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f142` | — | — | — | 含义栏为空/占位 | reference_status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f143` | — | — | — | 含义栏为空/占位 | reference_status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f144` | — | — | — | 含义栏为空/占位 | reference_status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f145` | — | — | — | 含义栏为空/占位 | status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f146` | — | — | — | 含义栏为空/占位 | reference_status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f59` | f59 | — | — | 含义栏为空/占位 | status_conflict | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-资金流(em_fund_flow) | `f135` | f135 | — | 元 | 含义栏为空/占位 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f136` | f136 | — | 元 | 含义栏为空/占位 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f138` | f138 | — | 元 | 含义栏为空/占位 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f139` | f139 | — | 元 | 含义栏为空/占位 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f149` | f149 | — | 元 | 含义栏为空/占位 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 同花顺-fuyao | `growth` | growth | — | — | 含义栏为空/占位 | status_conflict | 12.8.12f fuyao 财务指标 index_id 完整度与接入分类（2026-09-01）🆕 |
| 同花顺-fuyao | `growth.calculate_operating_income_yoy_growth_ratio` | growth.calculate_operating_income_yoy_growth_ratio | — | — | 含义栏为空/占位 | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `growth.calculate_parent_holder_net_profit_yoy_growth_ratio` | growth.calculate_parent_holder_net_profit_yoy_growth_ratio | — | — | 含义栏为空/占位 | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `last_price` | 派生 `last_price ÷ f92(BPS) | — | — | 含义栏为空/占位 | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `net_profit` | net_profit | 净利润 | JLY（净利润） | 含义栏有文本（仍未验证） | status_conflict | 12.8.12i fuyao 财务报表叶字段补录（V17.1.1 全量登记） |
| 同花顺-fuyao | `prev_price` | 派生 `prev_price × 板块涨停幅度 | — | — | 含义栏为空/占位 | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `profitability` | profitability | — | — | 含义栏为空/占位 | status_conflict | 12.8.12f fuyao 财务指标 index_id 完整度与接入分类（2026-09-01）🆕 |
| 同花顺-fuyao | `profitability.index_weighted_avg_roe` | profitability.index_weighted_avg_roe | — | — | 含义栏为空/占位 | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `profitability.sale_gross_margin` | profitability.sale_gross_margin | — | — | 含义栏为空/占位 | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `profitability.sale_net_interest_ratio` | profitability.sale_net_interest_ratio | — | — | 含义栏为空/占位 | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `solvency` | solvency | — | — | 含义栏为空/占位 | status_conflict | 12.8.12f fuyao 财务指标 index_id 完整度与接入分类（2026-09-01）🆕 |
| 同花顺-fuyao | `solvency.assets_debt_ratio` | solvency.assets_debt_ratio | — | — | 含义栏为空/占位 | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `valuation.pb_mrq` | valuation.pb_mrq | — | — | 含义栏为空/占位 | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `valuation.pe_mrq` | valuation.pe_mrq | — | — | 含义栏为空/占位 | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `valuation.pe_ttm` | valuation.pe_ttm | — | — | 含义栏为空/占位 | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `valuation.ps_ttm` | valuation.ps_ttm | — | — | 含义栏为空/占位 | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 开盘啦(kpl) | `pe_dynamic` | pe_dynamic | 动态PE（最新报告期年化） | 倍 | 含义栏有文本（仍未验证） | status_conflict | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `pe_static` | pe_static | 静态PE（上年度年报 LYR） | 倍 | 含义栏有文本（仍未验证） | status_conflict | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `pe_ttm` | pe_ttm | PE(TTM) | 倍 | 含义栏有文本（仍未验证） | status_conflict | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 新浪(扩展API) | `item_tongbi` | item_tongbi | 同比（有才附 `_同比` 键） | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `item_value` | item_value | 科目值（字符串） | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `netamount` | netamount | 净流入额 | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `opendate` | opendate | 日期 | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `report_type` | report_type | fzb(资产负债)/lrb(利润)/llb(现金流) | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `trade` | trade | 收盘价 | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `turnover` | turnover | 换手率% | — | 含义栏有文本（仍未验证） | status_conflict | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 腾讯(qt.gtimg) | `[86]` | — | 收盘集合竞价净未匹配手数(带符号)（L2 机制确认） | 手 | 含义栏有文本（仍未验证） | reference_status_conflict | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |

## 二、候选字段（1）

| 来源 | 完整 code path | 规范名 | 含义 | 单位 | 含义栏提示 | 状态判定 | 证据章节 |
|:--|:--|:--|:--|:--|:--|:--|:--|
| ZHB-tdxstat | `stat.unknown_2` | stat.unknown_2 | 贝塔系数(60日)·L2候选(列[2]已定BetaValue: ihelp.dat L63官方定义+慢变特征实证自相关0.91, 待真实指数基准复现升L1) | - | 含义栏有文本（仍未验证） | matched | 1.1 tdxstat.cfg 标准契约表（stat.*，20260918 对撞定案）🆕 |

## 三、待破解字段（1387）

| 来源 | 完整 code path | 规范名 | 含义 | 单位 | 含义栏提示 | 状态判定 | 证据章节 |
|:--|:--|:--|:--|:--|:--|:--|:--|
| FTShare REST | `symbol_id` | — | — | — | 含义栏为空/占位 | live_observed_not_documented | FTShare REST 官方接口契约：A股行情列表 |
| TDX(双命名源) | `Amount` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Average` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `BCancel` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Before5MinNow` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `BetaValue` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `CJJEPre1` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `CJJEPre3` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `CashZJ` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ConZAFDateNum` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `DTDate_Recent` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `DTPrice` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `DYRatio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Date` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `DownHome` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `DynaPE` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ErrorId` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `EverZTCount` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `FCAmo` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `FCb` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `FDEPre1` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `FDEPre2` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `FreeLtgb` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `FzAmo` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Fzhsl` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `HisHigh` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `HisLow` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `HqDate` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `IPO_Price` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `InOutFlag` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Inside` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `IsKzz` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `IsT0Fund` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `IsZCZGP` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ItemNum` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Jjjz` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `KfEarnMoney` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Kzz_HSCode` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `L2OrderNum` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `L2TicNum` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `LastClose` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `LastStartZT` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `LastZTHzNum` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Ltgb` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Ltsz` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `MA5Value` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `MainBusiness` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Max` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Min` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `MorePE` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `More_YJL` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `NoticeDate_Recent` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Now` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `NowVol` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Open` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `OpenAmo` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `OpenAmoPre1` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `OpenVolPre1` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `OpenZAF` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `OpenZTBuy` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `OtherQYJzc` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Outside` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `PB_MRQ` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `PreReceiveZJ` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `QHMainYYMM` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `RDInputFee` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `RecentDZDate` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `RecentGGJYDate` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `RecentHGDate` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `RecentIncentDate` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `RecentReleaseDate` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ReportDate` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `SCancel` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `SafeValue` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ShapeValue` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ShineValue` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `StaffNum` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `StaticPE_TTM` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `StopJYDate_Recent` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `TPFlag` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `TickDiff` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `TopDate_Recent` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `TotalBVol` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `TotalSVol` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `UpHome` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `VOpenZAF` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Volume` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Wtb` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `XsFlag` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `YYYYMMDD` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `YearZTDay` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Yield` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAF` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPre10` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPre20` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPre2D` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPre3` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPre30` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPre5` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPre60` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPreMyMonth` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPreOneYear` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFYear` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFYesterday` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ZTDate_Recent` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ZTGPNum` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ZTPrice` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Zangsu` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Zgb` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Zjl` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Zjl_HB` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `Zsz` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `amount` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `amount_1d` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `amount_2d` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `amount_wan` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `amplitude_pct` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ask1` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `ask1_vol` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| TDX(双命名源) | `ask2` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ask3` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ask4` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ask5` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `average_price` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `b_gu` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `b_vol` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `baoliu2` | baoliu2 | 保留字段2 | - | 含义栏有文本（仍未验证） | matched | 2.1 协议完整 36 字段表（权威定义） |
| TDX(双命名源) | `bid1` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `bid1_vol` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `bid2` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `bid3` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `bid4` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `bid5` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `bvps` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `byte` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `category_name` | date / category_name | 事件日期 / 类别名称 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.13.3 除权除息（get_gbbq / get_xdxr，0x000f）文档确认 |
| TDX(双命名源) | `change` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `change_amt` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `change_pct` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `change_pct_1d` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `change_pct_2d` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `changqi_fuzhai` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `circulating_shares` | circulating_shares / total_shares | 待破解 | 股 | 含义栏为空/占位 | registry_status_only_single_source | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `date` | date / category_name | 事件日期 / 类别名称 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.13.3 除权除息（get_gbbq / get_xdxr，0x000f）文档确认 |
| TDX(双命名源) | `entrust_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `eps` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `eps_raw` | eps_raw | 每股收益原始值 | - | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `fHSL` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `fLianB` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `fajirenfarengu` | — | 发起人法人股（项目输出键拼写为 fajirenfarengu） | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | — |
| TDX(双命名源) | `faqiren_faren_gu` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `faren_gu` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `fenhong` | — | 每股现金分红（XDXR category=1） | 元/股 | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.13.3 除权除息（get_gbbq / get_xdxr，0x000f）文档确认 |
| TDX(双命名源) | `float` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `float_capital` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `float_mcap_yi` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `gross_margin` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `gudong_renshu` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `guojia_gu` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `h_gu` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `high` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `huobi_zijin` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `inside_volume` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ipodate` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `jing_li_run_raw_float` | jing_li_run_raw_float | 净利润原始值 | 千元 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `jing_lirun` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `jing_zichan` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `jingying_xianjinliu` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `last_close` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `last_price` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `latest_indicators` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `limit_down` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `limit_down_price` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `limit_up` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `liu_tong_gu_ben_raw_float` | liu_tong_gu_ben_raw_float | 流通股本原始值 | 万股 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `liutong_guben` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `locked_amount` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `long_term_debt` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `low` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `market/code/guojiagu/faqirenfarengu/farengu/bgu/hgu/zhigonggu/liudongzichan/gudingzichan/wuxingzichan/zhuyinglirun/yingyelirun/touzishouyu/zongxianjinliu/lirunzonghe/shuihoulirun/baoliu2` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `market_snapshot` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `mcap_yi` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `meigugongji` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `meigujing_zichan` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `meiguweifenpei` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `more_info` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `name` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `net_profit` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `net_profit_yuan` | total_assets_yuan / net_profit_yuan | 待破解 | 元 | 含义栏为空/占位 | registry_status_only_single_source | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `open` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `outside_volume` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `pb` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `pe_lyr` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `pe_static` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `pe_ttm` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `peigu` | — | 每股配股比例（XDXR category=1） | 股/股 | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.13.3 除权除息（get_gbbq / get_xdxr，0x000f）文档确认 |
| TDX(双命名源) | `peigujia` | — | 配股价（XDXR category=1） | 元/股 | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.13.3 除权除息（get_gbbq / get_xdxr，0x000f）文档确认 |
| TDX(双命名源) | `pre_close` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `price` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `reserve2` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `rise_speed` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `roe` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `s_vol` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `shiyebianma` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `short_term_debt` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `shuihou_lirun` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `songzhuangu` | — | 每股送转股比例（XDXR category=1） | 股/股 | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.13.3 除权除息（get_gbbq / get_xdxr，0x000f）文档确认 |
| TDX(双命名源) | `str` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `total_assets_yuan` | total_assets_yuan / net_profit_yuan | 待破解 | 元 | 含义栏为空/占位 | registry_status_only_single_source | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `total_capital` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `total_shares` | circulating_shares / total_shares | 待破解 | 股 | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `touzi_shouyu` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `turnover_pct` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `uint` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `updateddate` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `ushort` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `vol_ratio` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `volume` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `vzangsu` | — | 量涨速（具体计算窗口待确认） | % | 含义栏有文本（仍未验证） | registry_status_only_single_source | — |
| TDX(双命名源) | `wuxing_zichan` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `yingshou_zhangkuan` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `zhigong_gu` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `zhuying_lirun` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `zhuying_shouru` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `zhuyinglyrun` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `zong_gu_ben_raw_float` | zong_gu_ben_raw_float | 总股本原始值 | 万股 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `zong_guben` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `zong_xianjinliu` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX(双命名源) | `zong_zi_chan_raw_float` | zong_zi_chan_raw_float | 总资产原始值 | 千元 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX-eltdx(适配层) | `ColName` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `Content` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `Count` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `ErrorCode` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `ResultSetKey` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `absolute_index` | absolute_index | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `action` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `active1` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `active2` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `adjust_mode` | adjust_mode | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `adjust_mode_raw` | adjust_mode_raw | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `after_outer_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `alignment_status` | alignment_status | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `amount` | amount | 成交额 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞）；12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `amount_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `anchor_date` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `anchor_date_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `ask1` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `ask_vol1` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `auction_matched_volume` | auction_matched_volume | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `auction_prev_volume_ratio` | auction_prev_volume_ratio | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `auction_unmatched_signed_volume` | auction_unmatched_signed_volume | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `b_gu_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `bao_liu_2_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `beta_60d` | beta_60d | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `bid1` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `bid_vol1` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `bin` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `bool` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `category` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `chang_qi_fu_zhai_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `change_pct` | change_pct | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `close` | time / open / high / low / close | 时间 / OHLC | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `close_delta_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `close_price_milli` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `code` | code | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `columns` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `cun_huo_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `current_hand` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `depth` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `down_count` | up_count / down_count | 指数类上涨/下跌家数 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `eltdx` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `eltdx_auction_prev_volume_ratio` | eltdx_auction_prev_volume_ratio | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_has_shortline` | eltdx_has_shortline | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_ladder_level` | eltdx_ladder_level | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_limit_board_text` | eltdx_limit_board_text | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_limit_up_streak_days` | eltdx_limit_up_streak_days | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_open_change_pct` | eltdx_open_change_pct | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_open_prev_amount_ratio` | eltdx_open_prev_amount_ratio | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_open_turnover_z` | eltdx_open_turnover_z | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_open_volume_ratio` | eltdx_open_volume_ratio | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_opening_rush` | eltdx_opening_rush | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_seal_amount` | eltdx_seal_amount | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_seal_to_float_ratio` | eltdx_seal_to_float_ratio | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `entry` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `eps_raw` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `error_code` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `event_kind` | event_kind | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `exchange` | exchange | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `extra_meta_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `extra_pair_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `fa_qi_ren_fa_ren_gu_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `fa_ren_gu_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `finance_info_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `float` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `float_market_value` | float_market_value | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `float_shares` | float_shares | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `free_float_market_value` | free_float_market_value | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `free_float_shares` | free_float_shares | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `full_code` | full_code | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `gu_ding_zi_chan_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `gu_dong_ren_shu_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `guo_jia_gu_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `h_gu_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `high` | time / open / high / low / close | 时间 / OHLC | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `high_delta_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `high_price` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `high_price_milli` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `highest_ladder_level` | highest_ladder_level | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `hitCache` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `index` | index | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `industry_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `inside_dish` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `int` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `ipo_date` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `ipo_date_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `issue_date` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `jing_li_run_raw_float` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `jing_ying_xian_jin_liu_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `jing_zi_chan_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `key` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `kline_day` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `ladder_level` | ladder_level | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `last_close_price_milli` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `last_price` | last_price | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `leader_code` | leader_code | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `leader_ladder_level` | leader_ladder_level | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `li_run_zong_he_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `lianban_count` | lianban_count | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `limit_board_text` | limit_board_text | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `limit_down_price` | limit_up_price / limit_down_price | 涨停价 / 跌停价 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.13.4 涨跌停限制（limits.special / scan_special，0x0452）文档确认 |
| TDX-eltdx(适配层) | `limit_or_count_raw` | limit_or_count_raw | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `limit_stat_days` | limit_stat_days | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `limit_status` | limit_status | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `limit_up_count` | limit_up_count | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `limit_up_count_in_stat_days` | limit_up_count_in_stat_days | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `limit_up_price` | limit_up_price / limit_down_price | 涨停价 / 跌停价 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.13.4 涨跌停限制（limits.special / scan_special，0x0452）文档确认 |
| TDX-eltdx(适配层) | `limit_up_streak_days` | limit_up_streak_days | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `liu_dong_fu_zhai_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `liu_dong_zi_chan_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `liu_tong_gu_ben_raw_float` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `locked_amount` | vol_rise_speed / locked_amount | 量涨速 / 封单额（=bid1×bid_vol1×100） | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.13.6 行情列表（quotes.list_by_category，0x054b）文档确认 |
| TDX-eltdx(适配层) | `low` | time / open / high / low / close | 时间 / OHLC | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `low_delta_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `low_price` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `low_price_milli` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `market_id` | market_id | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `mei_gu_jing_zi_chan_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `min2_amount` | min2_amount / opening_rush | 近2分钟金额 / 开盘抢筹 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.13.6 行情列表（quotes.list_by_category，0x054b）文档确认 |
| TDX-eltdx(适配层) | `mode_or_selector_raw` | mode_or_selector_raw | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `name` | name | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `neg_price_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `open` | time / open / high / low / close | 时间 / OHLC | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `open_amount` | open_amount | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `open_amount_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `open_amount_yuan` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `open_change_pct` | open_change_pct | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `open_delta_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `open_prev_amount_ratio` | open_prev_amount_ratio | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `open_prev_seal_ratio` | open_prev_seal_ratio | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `open_price` | open_price | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `open_price_milli` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `open_turnover_z` | open_turnover_z | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `open_volume_hand` | open_volume_hand | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `open_volume_ratio` | open_volume_ratio | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `opening_rush` | — | 近2分钟金额 / 开盘抢筹 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞）；12.13.6 行情列表（quotes.list_by_category，0x054b）文档确认 |
| TDX-eltdx(适配层) | `opening_rush_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `order_count` | order_count | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `outer_disc` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `pe_ttm` | pe_ttm | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `period_name` | period_name | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `period_param_raw` | period_param_raw | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `period_raw` | period_raw | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `points` | points | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `pre_close` | pre_close | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `pre_close_price` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `prev2_seal_amount` | prev2_seal_amount | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `prev_amount` | prev_amount | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `prev_open_amount` | prev_open_amount | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `prev_open_volume_hand` | prev_open_volume_hand | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `prev_seal_amount` | prev_seal_amount | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `previous_trade_date` | previous_trade_date | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `price` | price | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `price_acc_raw` | price_acc_raw | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `price_delta_raw` | price_delta_raw | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `price_milli` | price_milli | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `province_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `qsid` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `rank` | rank | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `raw_payload` | raw_payload | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `rec_id` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `record_hex` | record_hex | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `redistime` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `relatecolumn` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `request_count` | request_count | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `reserved_zero` | reserved_zero | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `rise_speed` | rise_speed / short_turnover | 涨速 / 短换手 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.13.6 行情列表（quotes.list_by_category，0x054b）文档确认 |
| TDX-eltdx(适配层) | `rise_speed_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `row_cells` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `rows` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `seal_amount` | seal_amount | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `seal_prev_ratio` | seal_prev_ratio | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `seal_to_amount_ratio` | seal_to_amount_ratio | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `seal_to_float_ratio` | seal_to_float_ratio | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `server_time_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `short_turnover` | rise_speed / short_turnover | 涨速 / 短换手 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.13.6 行情列表（quotes.list_by_category，0x054b）文档确认 |
| TDX-eltdx(适配层) | `short_turnover_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `shortline_error` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `shui_hou_li_run_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `side` | side | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `snapshot_error` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `sort_by` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `source` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `start` | start | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `start_raw` | start_raw | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `stats_date` | stats_date | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `status_or_sort_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `status_raw` | status_raw | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `str` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `tableid` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `tail_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `target_trade_date` | target_trade_date | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `time` | time / open / high / low / close | 时间 / OHLC | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `time_label` | time_label | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `time_minutes` | time_minutes | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `time_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `title` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `token` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `topic_id` | topic_id | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `topic_name` | topic_name | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `total_hand` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `total_seal_amount` | total_seal_amount | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `tou_zi_shou_yu_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `trade_date` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `trade_datetime` | trade_datetime | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `trading_date` | trading_date | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `unknown_after_outer_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `unknown_after_time_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `unknown_tail_raw` | unknown_tail_raw | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `up_count` | up_count / down_count | 指数类上涨/下跌家数 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `updated_date` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `updated_date_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `value` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `vol_rise_speed` | vol_rise_speed / locked_amount | 量涨速 / 封单额（=bid1×bid_vol1×100） | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.13.6 行情列表（quotes.list_by_category，0x054b）文档确认 |
| TDX-eltdx(适配层) | `volume` | volume | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `volume_hand` | volume_hand | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `volume_lots` | volume_lots | 成交量（手） | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `volume_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `volume_wire_value` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `wei_fen_li_run_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `wu_xing_zi_chan_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `year_limit_up_days` | year_limit_up_days | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `ying_shou_zhang_kuan_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `ying_ye_li_run_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `zhu_ying_li_run_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `zhu_ying_shou_ru_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `zi_ben_gong_ji_jin_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `zong_gu_ben_raw_float` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `zong_xian_jin_liu_raw_float` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `zong_zi_chan_raw_float` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `YYYYMMDD` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `[31]` | [31] | 连板类计数(口径待终核: 当日涨停时==[33]连板数, 非涨停日保留历史高位值>count) | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 1. `tdxstat.cfg` (个股综合统计快照，35 个字段，7,951 行) |
| ZHB-tdxstat | `[32]` | [32] | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 1. `tdxstat.cfg` (个股综合统计快照，35 个字段，7,951 行) |
| ZHB-tdxstat | `board_count` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat | `change_10k_bar` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat | `change_5k_bar` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat | `change_60d_alt` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat | `change_pct` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `change_pct_1d` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `change_pct_2d` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `change_ytd` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat | `code` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `date` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `dividend_yield` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat | `employee_count` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat | `float` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `int` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `market` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `pe_lyr` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `streak_days` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat | `unseal_date` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `YYYYMMDD` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `[10]` | [10] | 待破解 | 手 | 含义栏为空/占位 | aggregate_status_scope_unresolved | 2. `tdxstat2.cfg` (成交与资金流向表，21 个字段，7,951 行) |
| ZHB-tdxstat2 | `[14]` | [14] | 待破解 | 万元 | 含义栏为空/占位 | aggregate_status_scope_unresolved | 2. `tdxstat2.cfg` (成交与资金流向表，21 个字段，7,951 行) |
| ZHB-tdxstat2 | `[15]` | [15] | 待破解 | 万元 | 含义栏为空/占位 | aggregate_status_scope_unresolved | 2. `tdxstat2.cfg` (成交与资金流向表，21 个字段，7,951 行) |
| ZHB-tdxstat2 | `[9]` | [9] | 待破解 | 手 | 含义栏为空/占位 | aggregate_status_scope_unresolved | 2. `tdxstat2.cfg` (成交与资金流向表，21 个字段，7,951 行) |
| ZHB-tdxstat2 | `amount_1d` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `amount_2d` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `change_250k_bar` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `change_30k_bar` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `change_30k_bar_ref` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `change_mtd` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `code` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `date` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `float` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `high_52w` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `industry_code` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `ipo_price` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `main_net_buy_amount` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `main_net_buy_amount_1d` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `main_net_buy_hands` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `main_net_buy_hands_1d` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `market` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `zt_seal_amount` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `zt_seal_amount_1d` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `zt_seal_amount_2d` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tipinfo | `YYYYMMDD` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tipinfo | `[0]` | [0] | 市场代码 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 3. `tipinfo.dat` (财报日历与业绩快照，22 列，5,612 行) |
| ZHB-tipinfo | `[17]` | [17] | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 3. `tipinfo.dat` (财报日历与业绩快照，22 列，5,612 行) |
| ZHB-tipinfo | `[18]` | [18] | 恒空占位符 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 3. `tipinfo.dat` (财报日历与业绩快照，22 列，5,612 行) |
| ZHB-tipinfo | `code` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tipinfo | `disclose_date` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tipinfo | `div_amount` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tipinfo | `div_date` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tipinfo | `eps` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| ZHB-tipinfo | `equity_incentive_date` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tipinfo | `forecast_date_recent` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tipinfo | `forecast_type` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tipinfo | `hg_amount_yi` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tipinfo | `hg_date` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tipinfo | `report_period` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tipinfo | `suspend_major_event_date` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| ZHB-tipinfo | `zt_date_recent` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| reports | `ACCUM_AMOUNT` | ACCUM_AMOUNT | 累计成交额 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `AP202608211828244348` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| reports | `BEIJING` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| reports | `BUY_RATIO` | BUY_RATIO / SELL_RATIO | 买入/卖出占比 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `BUY_SEAT` | BUY_SEAT / SELL_SEAT | 买入/卖出前5席位数 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `CHANGE_TYPE` | CHANGE_TYPE | 异动类型代码 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `DEAL_AMOUNT_RATIO` | DEAL_AMOUNT_RATIO | 成交额占比 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `DEAL_NET_RATIO` | DEAL_NET_RATIO | 净额占比 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `EXPLAIN` | EXPLAIN | 待破解 | — | 含义栏为空/占位 | matched | 12.9.2 其他接口实测发现 |
| reports | `FIN_BALANCE_GR` | FIN_BALANCE_GR | 融资余额增长率 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `FREE_MARKET_CAP` | FREE_MARKET_CAP | 流通市值 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `NET_BS_AMT` | NET_BS_AMT | 净买卖额 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `OTHER` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| reports | `RQJMG` | RZJME / RQJMG | 融资净买入 / 融券净卖出 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `RQYL` | RQYL | 融券余量 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `RZJME` | RZJME / RQJMG | 融资净买入 / 融券净卖出 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `RZRQYECZ` | RZRQYECZ | 两融余额差值 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `RZYEZB` | RZYEZB | 融资余额占比 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `SELL_RATIO` | BUY_RATIO / SELL_RATIO | 买入/卖出占比 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `SELL_SEAT` | BUY_SEAT / SELL_SEAT | 买入/卖出前5席位数 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `SH600519` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| reports | `SHANGHAI` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| reports | `SHENZHEN` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| reports | `TRADE_MARKET` | TRADE_MARKET | 待破解 | — | 含义栏为空/占位 | matched | 12.9.2 其他接口实测发现 |
| reports | `actualLastTwoYearEps` | actualLastTwoYearEps | 前年实际 EPS | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `actualLastYearEps` | actualLastYearEps | 去年实际 EPS | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `adjunctSize` | adjunctSize / adjunctType | 附件大小/类型 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `adjunctType` | adjunctSize / adjunctType | 附件大小/类型 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `adjunctUrl` | adjunctUrl | 待破解 | — | 含义栏为空/占位 | matched | 12.9.2 其他接口实测发现 |
| reports | `analyse` | analyse / analyse_title | 待破解 | — | 含义栏为空/占位 | matched | 12.9.2 其他接口实测发现 |
| reports | `analyse_title` | analyse / analyse_title | 待破解 | — | 含义栏为空/占位 | matched | 12.9.2 其他接口实测发现 |
| reports | `announcementType` | announcementType | 公告类型代码 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `attachType` | attachType | 附件类型 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `audio_url` | audio_url | 音频链接 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `column` | column | 栏目代码 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `emIndustryCode` | emIndustryCode | 东财行业码 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `get_industry_reports` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| reports | `get_reports` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| reports | `indvAimPriceL` | indvAimPriceL | 目标价 L | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `indvAimPriceT` | indvAimPriceT | 目标价 T | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `indvIsNew` | indvIsNew | 新研报标记 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `level` | level | 待破解 | — | 含义栏为空/占位 | matched | 12.9.2 其他接口实测发现 |
| reports | `orgId` | secName / orgId | 证券名 / 机构ID | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `orgType` | orgType | 机构类型标记 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `reading_num` | reading_num / share_num | 阅读数/分享数 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `sRatingCode` | sRatingCode | 待破解 | — | 含义栏为空/占位 | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `secName` | secName / orgId | 证券名 / 机构ID | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `share_num` | reading_num / share_num | 阅读数/分享数 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `shortTitle` | shortTitle | 短标题 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `stock_list` | stock_list | 待破解 | — | 含义栏为空/占位 | matched | 12.9.2 其他接口实测发现 |
| reports | `subject_name` | subjects / subject_name | 主题分类 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `subjects` | subjects / subject_name | 主题分类 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `topic` | topic | 话题 | — | 含义栏有文本（仍未验证） | matched | 12.9.2 其他接口实测发现 |
| reports | `white` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-clist | `f128` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-clist | `f13` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-clist | `f141` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-clist | `f2` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-clist | `f207` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-clist | `f257` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-clist | `f4` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-datacenter(英文键) | `able_shares` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `amount` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-datacenter(英文键) | `avg_shares` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `balance_gr` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `bonus_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `bonus_rmb` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `buyer` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `change_num` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `change_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `change_shares` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `chg_10d` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `chg_5d` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `close` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-datacenter(英文键) | `date` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-datacenter(英文键) | `hold_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `hold_shares` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `holder_num` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `lockup_expiry` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `margin_trading` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `market_cap` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-datacenter(英文键) | `northbound_hold` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `plan` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `price` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-datacenter(英文键) | `ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rqchl` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rqjmg` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rqmcl` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rqye` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzche` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzche_10d` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzche_5d` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzjme` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzmre` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzmre_10d` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzmre_5d` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzrqye` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzye` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `seller` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `shares` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-datacenter(英文键) | `transfer_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `type` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-datacenter(英文键) | `vol` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-em_kline_f61 | `f43` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-em_kline_f61 | `f85` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f1` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f10` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f100` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f102` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f103` | ocf_ttm(f103) | 经营活动现金流量净额 TTM | 元 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.9.1 push2 stock/get 全字段破解（114 字段实测，项目只用 19 个） |
| 东财-push2(stock/get) | `f106` | f106 | 待破解 | - | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.1 单股行情 `stock/get`（已由 get_em_quote_full 验证） |
| 东财-push2(stock/get) | `f108` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f109` | net_profit_annual(f109) | 归母净利润 最新年报 | 元 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.9.1 push2 stock/get 全字段破解（114 字段实测，项目只用 19 个） |
| 东财-push2(stock/get) | `f113` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f114` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f115` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f12` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f123` | f123 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f124` | f124 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f125` | f125 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f126` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f129` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f13` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f130` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f131` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f132` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f133` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f134` | f134 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f15` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f150` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-push2(stock/get) | `f151` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-push2(stock/get) | `f153` | f153 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f154` | f154 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f155` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-push2(stock/get) | `f157` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-push2(stock/get) | `f160` | eps_annual(f160) | 待破解 | 元/股 | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.9.1 push2 stock/get 全字段破解（114 字段实测，项目只用 19 个） |
| 东财-push2(stock/get) | `f161` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f17` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f172` | f172 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.9.1 push2 stock/get 全字段破解（114 字段实测，项目只用 19 个） |
| 东财-push2(stock/get) | `f174` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f176` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f178` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f18` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f19` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f191` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f192` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f199` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f2` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f216` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f23` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f24` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f25` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f250` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f26` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f27` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f29` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f3` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f37` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f38` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f39` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f4` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f40` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f41` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f49` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f62` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f63` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f64` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f65` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f66` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f69` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f7` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f70` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f72` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f73` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f74` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f75` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f76` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f77` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f8` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f80` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f81` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f82` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f83` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f87` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f9` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `HHMMSS` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-push2ex | `broken_count` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-push2ex | `change_pct` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `circulating_value` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-push2ex | `code` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `first_limit_time` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `last_limit_time` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `limit_broken_pool` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 东财-push2ex | `limit_count` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `limit_down_pool` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-push2ex | `limit_up_pool` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 东财-push2ex | `name` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `price` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `sector` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `total_value` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-push2ex | `turnover_rate` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `y_first_seal` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-push2ex | `y_limit_count` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-push2ex | `yfbt` | yfbt / ylbc | 昨日首次封板时间 / 昨日连板数 | HHMMSS / 板 | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.8.1 东财 push2ex（涨停/炸板/跌停/昨涨停四池）✅ |
| 东财-push2ex | `ylbc` | yfbt / ylbc | 昨日首次封板时间 / 昨日连板数 | HHMMSS / 板 | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.8.1 东财 push2ex（涨停/炸板/跌停/昨涨停四池）✅ |
| 东财-push2ex | `zt_continuous` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 东财-push2ex | `zt_days` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-ulist239(np/get) | `f104` | f104 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f105` | f105 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f106` | f106 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f107` | f107 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f108` | f108 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f11` | f11 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f111` | f111 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f116` | f116 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f117` | f117 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f118` | f118 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f119` | f119 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f120` | f120 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f121` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f122` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f123` | f123 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f125` | f125 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f126` | f126 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f127` | f127 | 委比 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f128` | f128 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f13` | f13 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f133` | f133 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f134` | f134 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f136` | — | — | — | 含义栏为空/占位 | matched | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f138` | — | — | — | 含义栏为空/占位 | matched | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f148` | f148 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f149` | — | — | — | 含义栏为空/占位 | matched | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f152` | f152 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f153` | f153 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f154` | f154 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f194` | f194 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f204` | f204 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f205` | f205 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f206` | f206 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f207` | f207 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f208` | f208 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f209` | f209 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f210` | f210 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f213` | f213 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f214` | f214 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f215` | f215 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f216` | f216 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f217` | f217 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f218` | f218 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f219` | f219 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f22` | f22 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f220` | f220 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f222` | f222 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f223` | f223 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f227` | f227 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f235` | f235 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f236` | f236 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f237` | f237 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f238` | f238 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f239` | f239 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f240` | f240 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f241` | f241 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f242` | f242 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f243` | f243 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f244` | f244 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f245` | f245 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f246` | f246 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f247` | f247 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f248` | f248 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f249` | f249 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f250` | f250 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f27` | f27 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f28` | f28 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f30` | f30 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f45` | f45 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f46` | f46 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f49` | f49 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f63` | f63 | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f93` | f93 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f97` | f97 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f98` | f98 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f99` | f99 | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-热榜(em_hot) | `hot_rank` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f48` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f51` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f52` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f53` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f54` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f55` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f56` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f57` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f62` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f66` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f69` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f72` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f75` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f78` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f84` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `BPS` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `amount_1d` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `amount_2d` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `amplitude` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `anomaly_list` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `asset_type` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `assets_debt_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `auction_pct` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `calculate_operating_income_yoy_growth_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `calculate_operating_profit_yoy_growth_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `calculate_parent_holder_net_profit_yoy_growth_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `calendar` | a-share/calendar/trading-days | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `cash_meet_invest_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `cash_operating_index` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `cash_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `catalog` | a-share-index/catalog/ths-index-list | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `close_price` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `companies` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `constituents` | a-share-index/constituents/ths-stock-list | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `count_captured` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `currency` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `current_assets_turnover_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `current_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `date` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `date_ms` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `day` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `ded_weighted_roe` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `diagnostics` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `diagnostics/detail` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `dividends` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `dragon_tiger` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `drawdowns` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `dump` | dump/market-dumps/{daily-k,daily-k-10d,adjustment-factors}/download-url | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `earned_interest_multiple` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `exchange` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `experience` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `fin_report` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `financials` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `fixed_asset_invest_expansion_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `fund/companies/detail` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund/holders/top` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund/managers/detail` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund/market/snapshot` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund/performance/nav` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund/profile/detail` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund_large_buy` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund_large_sell` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund_mid_buy` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund_mid_sell` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund_super_buy` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund_super_sell` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `h1_indicators` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `h1_indicators_ready` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `high` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `high_price` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `historical` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `holders` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `holders/detail` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `index_deduct_weighted_avg_roe` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `index_weighted_avg_roe` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `indicators` | a-share/financials/indicators | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `inventory_turnover_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `item` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `list` | meta/tickers/list | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `long_term_debt_equity_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `low` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `low_price` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `main_net_buy_hands` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `managers` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `market` | dump/market-dumps/{daily-k,daily-k-10d,adjustment-factors}/download-url | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `meta` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `meta/tickers/list` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `meta/tickers/search` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `name` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `nav` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `net_profit_cash_content` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `news` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `offerings` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `offerings/list` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `open` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `open_price` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `operating_cash_flow_net_divide_income` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `operation` | operation | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.8.12f fuyao 财务指标 index_id 完整度与接入分类（2026-09-01）🆕 |
| 同花顺-fuyao | `pb_mrq` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `pcf_ttm` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `pe_mrq` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `pe_ttm` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `performance` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `period` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `price_change` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `price_change_ratio_pct` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `prices` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `probe_trading_day` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `profile` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `ps_ttm` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `quick_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `rank` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `receive_account_turnover_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `report_date_ms` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `returns` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `revenue_ttm` | — | 营业总收入 TTM（push2 f104）；富耀 operating_income 回算口径约差 1.8%，仅近似兜底 | 元 | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕；12.8.12d THS 族替代 push 域能力矩阵（V17.0.7，2026-08-25 实测定案）🆕 |
| 同花顺-fuyao | `roa` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `sale_gross_margin` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `sale_net_interest_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `search` | meta/tickers/search | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `snake_case` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `stock_name` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `thscode` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `ticker` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `tickers` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `total` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `total_assets_growth_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `total_assets_net_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `total_assets_turnover_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `turnover` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `turnover_ratio_pct` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `valuations` | a-share/valuations/snapshot | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `volume` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `weighted_roe` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 同花顺-fuyao | `zt_seal_amount_1d` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `zt_seal_amount_2d` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 巨潮(cninfo) | `answer` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 巨潮(cninfo) | `answerer` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 巨潮(cninfo) | `ask_time` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 巨潮(cninfo) | `code` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 巨潮(cninfo) | `company` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 巨潮(cninfo) | `date` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 巨潮(cninfo) | `question` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 巨潮(cninfo) | `title` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 巨潮(cninfo) | `type` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 巨潮(cninfo) | `url` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `ACCUM_AMOUNT` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `BILLBOARD_BUY_AMT` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `BILLBOARD_DEAL_AMT` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `BILLBOARD_NET_AMT` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `BILLBOARD_SELL_AMT` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `BUY_RATIO` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `BUY_SEAT` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `BUY_SEAT_NEW` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `CHANGE_RATE` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `CHANGE_TYPE` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `CLOSE_PRICE` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `D10_CLOSE_ADJCHRATE` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `D1_CLOSE_ADJCHRATE` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `D20_CLOSE_ADJCHRATE` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `D2_CLOSE_ADJCHRATE` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `D30_CLOSE_ADJCHRATE` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `D5_CLOSE_ADJCHRATE` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `DEAL_AMOUNT_RATIO` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `DEAL_NET_RATIO` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `DTJS` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `Day` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `EXPLAIN` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `EXPLANATION` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `FREE_MARKET_CAP` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `MARKET` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `NET_BS_AMT` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `SECUCODE` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `SECURITY_CODE` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `SECURITY_INNER_CODE` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `SECURITY_NAME_ABBR` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `SECURITY_TYPE_CODE` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `SELL_RATIO` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `SELL_SEAT` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `SELL_SEAT_NEW` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `SUM_BUY_AMT` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `SUM_SELL_AMT` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `SZJS` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `TRADE_DATE` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `TRADE_ID` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `TRADE_MARKET` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `TRADE_MARKET_CODE` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `TURNOVERRATE` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `XDJS` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `ZTJS` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `amplitude` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `big_order_300w_net` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `bl` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `broken_num` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `broken_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `change_type` | change_type | 变动类型 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `circulation_value` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_02` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_03` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_04` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_05` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_06` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_07` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_08` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_09` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_10` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_11` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_12` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_13` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_14` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_15` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_16` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_17` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `col_18` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `color` | color | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `continuous_rate` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `count` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `dates` | dates | 日期序列 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `day` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `df_num` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `down_10` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `down_2` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `down_4` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `down_6` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `down_8` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `down_num` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `dragon_tiger_today` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `dt` | zt / dt | 涨停 / 跌停总数 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `dt_ever` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `dt_num` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `errcode` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `fall_dist` | rise_dist / fall_dist | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `fall_num` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `flat` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `flat_num` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `institution_add` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `kpl_error` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `lbgd` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `limit_time` | limit_time | 涨停时间 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `limit_up_board` | limit_up_board | 待破解 | — | 含义栏为空/占位 | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `main_buy` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `main_inflow` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `main_sell` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `market_degree` | market_degree | 待破解 | — | 含义栏为空/占位 | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `max_seal` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `one_word` | one_word | 一句话点评 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `pe_next` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `pe_now` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `performance` | performance | 昨涨停今表现 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `plate_rotation_top` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `plates` | plates | 相关板块列表 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `popular` | popular | 人气值 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `prev_amount_wan` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `preview_balance` | preview_balance | 盘前余额 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `preview_balance_change_px` | preview_balance_change_px | 盘前余额变化价 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `profit_ratio` | profit_ratio | 获利率 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `q_zrcs` | s_zrcs / q_zrcs | 昨日沪市 / 昨日全市成交额 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `qscln` | szln / qscln | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `reason` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `rise_dist` | rise_dist / fall_dist | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `rise_num` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `s_zrcs` | s_zrcs / q_zrcs | 昨日沪市 / 昨日全市成交额 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `seal_amount` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `sector` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `sector_code` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `shsz_balance` | shsz_balance | 两市成交额 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `shsz_balance_change_px` | shsz_balance_change_px | 较上日成交额变化 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `sign` | sign | 市场人气判断文字 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `sjdt` | sjzt / sjdt | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `sjzt` | sjzt / sjdt | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `source` | source | 数据来源标识 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `speed` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `status` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `stdt` | stzt / stdt | ST 涨停 / 跌停 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `stock_changes_8201` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `strength` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `strong` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `stzt` | stzt / stdt | ST 涨停 / 跌停 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `suspend_num` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `szln` | szln / qscln | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `tip` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `total_amount_wan` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `total_value` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `trade_date` | — | — | — | 含义栏为空/占位 | status_missing | — |
| 市场源(market_sources) | `ttag` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `turnover_real` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `up_10` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `up_2` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `up_4` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `up_6` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `up_8` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `up_down_dis` | up_down_dis | 待破解 | — | 含义栏为空/占位 | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `up_num` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `up_open_num` | up_open_num | 炸板数量 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `up_open_ratio` | up_open_ratio | 高开率 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `up_ratio` | up_ratio / up_ratio_num | 封板率 / 封板数量 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `up_ratio_num` | up_ratio / up_ratio_num | 封板率 / 封板数量 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `value` | value | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `vol_ratio` | — | — | — | 含义栏为空/占位 | reference_status_missing | — |
| 市场源(market_sources) | `zt` | zt / dt | 涨停 / 跌停总数 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `zt_natural` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `zt_num` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `zt_time` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 市场源(market_sources) | `ztjs` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `Ad_x` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `BaceFaceList` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `BoomReason` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Boom_ZS` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `BuyIn` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `CQ` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `CYWWZS` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `D3` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `DJI` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `DT` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `DTJS` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Date` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `Day` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `DongXiang` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `FAIL` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `GNSM` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `ID` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `IncreaseAmount` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `IsBoom` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Item` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `JoinNum` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `LBstatus` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `LZInfo` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `List` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `List_Special` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Money` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Name` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `OHLC` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `PidType` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `PlateID` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `QD` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Reason` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `SCLT` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `ST` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `SZJS` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Special` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `TTMPeRate` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Theme` | Theme/InfoBKR | — | — | 含义栏为空/占位 | registry_status_only_single_source | 12.17.1 kaipanla-data-parser 补充（2026-08-09 实测 10 接口 + 63 字段映射验证）🆕 |
| 开盘啦(kpl) | `Time` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Title` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Topic` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Tur` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Turnover` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Vol` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `XDJS` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `ZBL` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `ZT` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `ZTJS` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `ZTNum` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `actual_float_mv` | actual_float_mv | 实际流通市值 | 元 | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `actualcirculation_value` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `amount` | amount | 成交额 | 元 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `amount_in` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `amplitude` | amplitude | 振幅% | % | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `apiv` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `avg_px` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `bal` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `bid` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `big_order_net_3m` | big_order_net_3m | 300万以上大单净额 | 元 | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `bl` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `board_tag` | board_tag | 所属板块标签 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `break_limit_up_times` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `buy_lock_volume_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `change_pct` | change_pct | 涨跌幅% | % | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `change_percent` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `circ_mv` | circ_mv | 流通市值 | 元 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `circulation_amount` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `circulation_value` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `close_seal_amount` | close_seal_amount | 收盘封单额 | 元 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `code` | code | 股票代码 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `color` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `content` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `content2` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `cur_price` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `data` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `date` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `description` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `df_num` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `down_px` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `dyn_pb_rate` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `entrust_rate` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `errcode` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `f162` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `f163` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `fall_count` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `fields` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `hprice` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `info` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `inst_increase_q1` | inst_increase_q1 | 机构增仓Q1金额 | 元 | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `institutionIncrease` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `jtPeRate` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `last_px` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `lbgd` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `lead_count` | lead_count | 领涨次数 | 次 | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `limit_down_count` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `limit_pattern_text` | limit_pattern_text | 几天几板(如"3天2板") | 文本 | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `limit_up_broken_count` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `limit_up_count` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `list` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `lprice` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `main_buy` | main_buy | 主力买入额 | 元 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `main_net` | main_net | 主力净额(≡主力净买入额) | 元 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `main_sell` | main_sell | 主力卖出额 | 元 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `market_temperature` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `market_value` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `max_seal_amount` | max_seal_amount | 最大封单额 | 元 | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `name` | name | 股票名称 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `net_flow_ratio` | net_flow_ratio | 净流占比 | % | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `nums` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `out` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `pankou` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `pb` | pb | 市净率 | 倍 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `pe_rate` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `period_change` | period_change | 区间涨跌幅 | % | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `phcj_volume` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `plate_type` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `popularity_rank_chg` | popularity_rank_chg | 人气排名变化 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `popularity_value` | popularity_value | 人气值 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `preclose` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `price` | price | 现价 | 元 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `prod_name` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `px_change` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `px_change_rate` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `q_zrcs` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `qscln` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `real` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `real_turnover_rate` | real_turnover_rate | ★实际换手率% | % | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `rise_count` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `sell_flow_ratio` | sell_flow_ratio | 卖流占比 | % | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `speed` | speed | 涨速 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `state` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `state1` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `stateZT` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `status` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `status_color` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `stock_name` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `stockid` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `strong` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `time` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `tip` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `total_amount` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `total_mv` | total_mv | 总市值 | 元 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `total_shares` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `total_turnover` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `trend` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `turnover` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `turnover_pct` | turnover_pct | 换手率% | % | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `turnover_ratio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `up_px` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `value` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `vol` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `volRatio` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `vol_ratio` | vol_ratio | 量比 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `weituo` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `yestRase` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `yesterday_limit_up_avg_pcp` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 开盘啦(kpl) | `ztjs` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 开盘红(Levistock适配) | `avg_change` | avg_change | 待破解 | — | 含义栏为空/占位 | registry_status_only_single_source | 12.10.7 开盘红板块排行（sector_ranking_kph）补充字段 |
| 开盘红(Levistock适配) | `buy_amount` | buy_amount / sell_amount | 待破解 | — | 含义栏为空/占位 | registry_status_only_single_source | 12.10.7 开盘红板块排行（sector_ranking_kph）补充字段 |
| 开盘红(Levistock适配) | `dt` | zt / dt | 涨停 / 跌停总数 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 开盘红(Levistock适配) | `fall_dist` | rise_dist / fall_dist | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 开盘红(Levistock适配) | `fall_num` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 开盘红(Levistock适配) | `flat` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 开盘红(Levistock适配) | `industry_id` | industry_id / industry_zt | 行业 ID / 同行业涨停数 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| 开盘红(Levistock适配) | `industry_zt` | industry_id / industry_zt | 行业 ID / 同行业涨停数 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| 开盘红(Levistock适配) | `limit_count` | limit_tag / limit_count | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| 开盘红(Levistock适配) | `limit_tag` | limit_tag / limit_count | 待破解 | — | 含义栏为空/占位 | registry_status_only_single_source | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| 开盘红(Levistock适配) | `limit_time` | limit_time / open_time | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| 开盘红(Levistock适配) | `net_inflow` | net_inflow / market_cap | 待破解 | — | 含义栏为空/占位 | registry_status_only_single_source | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| 开盘红(Levistock适配) | `net_inflow_5d` | net_inflow_5d | 待破解 | — | 含义栏为空/占位 | registry_status_only_single_source | 12.10.7 开盘红板块排行（sector_ranking_kph）补充字段 |
| 开盘红(Levistock适配) | `open_time` | limit_time / open_time | 待破解 | — | 含义栏为空/占位 | registry_status_only_single_source | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| 开盘红(Levistock适配) | `q_zrcs` | s_zrcs / q_zrcs | 昨日沪市 / 昨日全市成交额 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 开盘红(Levistock适配) | `qscln` | szln / qscln | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 开盘红(Levistock适配) | `reason` | reason | 涨停原因 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| 开盘红(Levistock适配) | `rise_dist` | rise_dist / fall_dist | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 开盘红(Levistock适配) | `rise_num` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 开盘红(Levistock适配) | `s_zrcs` | s_zrcs / q_zrcs | 昨日沪市 / 昨日全市成交额 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 开盘红(Levistock适配) | `seal_amount` | seal_amount / seal_money | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| 开盘红(Levistock适配) | `seal_money` | seal_amount / seal_money | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| 开盘红(Levistock适配) | `sell_amount` | buy_amount / sell_amount | 待破解 | — | 含义栏为空/占位 | registry_status_only_single_source | 12.10.7 开盘红板块排行（sector_ranking_kph）补充字段 |
| 开盘红(Levistock适配) | `sign` | sign | 市场人气判断文字 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 开盘红(Levistock适配) | `sjdt` | sjzt / sjdt | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 开盘红(Levistock适配) | `sjzt` | sjzt / sjdt | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 开盘红(Levistock适配) | `stdt` | stzt / stdt | ST 涨停 / 跌停 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 开盘红(Levistock适配) | `stock_count` | stock_count | 成分股数量 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.7 开盘红板块排行（sector_ranking_kph）补充字段 |
| 开盘红(Levistock适配) | `stzt` | stzt / stdt | ST 涨停 / 跌停 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 开盘红(Levistock适配) | `szln` | szln / qscln | 待破解 | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 开盘红(Levistock适配) | `themes` | themes | 题材 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| 开盘红(Levistock适配) | `turnover` | turnover / turnover_rate | 成交额 / 换手率% | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| 开盘红(Levistock适配) | `zt` | zt / dt | 涨停 / 跌停总数 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 新浪(hq.sinajs) | `[11]` | [11] | 待破解 | 元 | 含义栏为空/占位 | aggregate_status_scope_unresolved | 12.2 新浪 hq.sinajs.cn 完整字段字典（33-34 字段） |
| 新浪(hq.sinajs) | `[13]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[14]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[15]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[16]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[17]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[18]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[19]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[23]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[24]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[25]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[26]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[27]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[28]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[29]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[32]` | [32] | 状态码 | - | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.2 新浪 hq.sinajs.cn 完整字段字典（33-34 字段） |
| 新浪(hq.sinajs) | `[58]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[59]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(扩展API) | `ask` | bid_vol/bid/last/ask/ask_vol | 五档价量 | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `ask_vol` | bid_vol/bid/last/ask/ask_vol | 五档价量 | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `bid` | bid_vol/bid/last/ask/ask_vol | 五档价量 | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `bid_vol` | bid_vol/bid/last/ask/ask_vol | 五档价量 | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `close` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(扩展API) | `date` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 新浪(扩展API) | `delta` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `gamma` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `iv` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `last` | bid_vol/bid/last/ask/ask_vol | 五档价量 | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `limit_down` | limit_up / limit_down | 涨跌停价 | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `limit_up` | limit_up / limit_down | 涨跌停价 | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `net_amount` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 新浪(扩展API) | `open` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `open_interest` | open_interest | 持仓量 | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `prev_close` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `strike` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `theory` | theory | 理论价值 | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `theta` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `vega` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | — | 含义栏有文本（仍未验证） | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 沪深交易所 | `sse_raw` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 百度(baidu) | `ma10avgprice` | ma5avgprice/ma10avgprice/ma20avgprice | 待破解 | — | 含义栏为空/占位 | matched | 12.8.16 百度股市通（K线带MA）❌→⏸️ |
| 百度(baidu) | `ma20avgprice` | ma5avgprice/ma10avgprice/ma20avgprice | 待破解 | — | 含义栏为空/占位 | matched | 12.8.16 百度股市通（K线带MA）❌→⏸️ |
| 百度(baidu) | `ma5avgprice` | ma5avgprice/ma10avgprice/ma20avgprice | 待破解 | — | 含义栏为空/占位 | matched | 12.8.16 百度股市通（K线带MA）❌→⏸️ |
| 腾讯(qt.gtimg) | `[10]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[11]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[12]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[13]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[14]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[15]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[16]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[17]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[18]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[20]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[21]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[22]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[23]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[24]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[25]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[26]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[27]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[28]` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[29]` | — | 最近逐笔成交 | - | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |
| 腾讯(qt.gtimg) | `[55]` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 腾讯(qt.gtimg) | `[7]` | [7] | 外盘 | 手 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |
| 腾讯(qt.gtimg) | `[87]` | — | 科创板/两融标记（688 段值='100'） | - | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |
| 腾讯(qt.gtimg) | `[8]` | [8] | 内盘 | 手 | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |
| 财联社(cls) | `catalyst` | catalyst | 催化剂描述 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |
| 财联社(cls) | `code` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 财联社(cls) | `cur_heat` | rank / cur_heat | 当前热度排名 / 热度值 | — | 含义栏有文本（仍未验证） | registry_status_only_single_source | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |
| 财联社(cls) | `id` | — | — | — | 含义栏为空/占位 | registry_status_only_single_source | — |
| 财联社(cls) | `int` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 财联社(cls) | `is_new` | is_new | 是否新上榜（1=是） | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |
| 财联社(cls) | `level` | level | 快讯等级（重要性分级） | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.8.13.1 财联社快讯 telegraph 原始字段补录（V17.1.1 全量登记） |
| 财联社(cls) | `list` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 财联社(cls) | `name` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 财联社(cls) | `pct` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 财联社(cls) | `plate_code` | plate_code / plate_name | 板块代码 / 名称（风口板块） | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |
| 财联社(cls) | `plate_name` | plate_code / plate_name | 板块代码 / 名称（风口板块） | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |
| 财联社(cls) | `plates` | trade_date / plates | 轮动日期 / 当日 top10 板块列表 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |
| 财联社(cls) | `rank` | rank / cur_heat | 当前热度排名 / 热度值 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |
| 财联社(cls) | `rank_change` | rank_change | 排名变化（正=上升，负=下降） | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |
| 财联社(cls) | `reading_num` | reading_num | 阅读数 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.8.13.1 财联社快讯 telegraph 原始字段补录（V17.1.1 全量登记） |
| 财联社(cls) | `stock_list` | stock_list | 关联股票代码列表 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.8.13.1 财联社快讯 telegraph 原始字段补录（V17.1.1 全量登记） |
| 财联社(cls) | `subjects` | subjects | 主题/题材标签列表 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.8.13.1 财联社快讯 telegraph 原始字段补录（V17.1.1 全量登记） |
| 财联社(cls) | `time` | — | — | — | 含义栏为空/占位 | aggregate_status_scope_unresolved | — |
| 财联社(cls) | `trade_date` | trade_date / plates | 轮动日期 / 当日 top10 板块列表 | — | 含义栏有文本（仍未验证） | aggregate_status_scope_unresolved | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |

## 四、已证伪（默认不重复破解）（2）

| 来源 | 完整 code path | 规范名 | 含义 | 单位 | 含义栏提示 | 状态判定 | 证据章节 |
|:--|:--|:--|:--|:--|:--|:--|:--|
| ZHB-tdxstat | `change_30d` | change_20d | 与同来源同路径 change_20d 完全重复的历史兼容键，不是独立的 30 日涨跌幅 | % | 含义栏有文本（仍未验证） | empirical_duplicate_alias | 2026-10-17 change_30d 纠错审计 |
| ZHB-tdxstat | `stat.change_30d` | stat.change_20d | 与同来源同路径 stat.change_20d 完全重复的历史兼容键，不是独立的 30 日涨跌幅 | % | 含义栏有文本（仍未验证） | empirical_duplicate_alias | 2026-10-17 change_30d 纠错审计 |

## 已退出来源字段（仅历史证据，不进入默认破解）

| 来源 | 路径数 | verified | unverified | candidate | conflict | disproved |
|:--|--:|--:|--:|--:|--:|--:|
| FTShare | 15 | 6 | 9 | 0 | 0 | 0 |
| Levistock历史未归属 | 129 | 18 | 111 | 0 | 0 | 0 |
