# 未知字段与状态冲突队列

> 由 `field_registry.json.source_fields` 自动生成；每行身份是来源加完整 code path。
> 修改状态必须先核对 `reference_evidence` 与 `registry_aggregate`，并保留证据来源。
> 碰撞候选须人工复核后使用 `apply_collision_adjudications.py` 同步状态；流程见 `field_verification/ADJUDICATION_WORKFLOW.md`。

> 总字段路径 2469；unverified 1548、candidate 1、conflict 90、disproved 0。

## 一、状态冲突（禁止作为锚点，优先复核）（90）

| 来源 | 完整 code path | 规范名 | 含义 | 单位 | 状态判定 | 证据章节 |
|:--|:--|:--|:--|:--|:--|:--|
| ZHB-tdxstat | `stat.unknown_26` | stat.unknown_26 | 年内涨停天数 YearZTDay·L2候选(列[26]已定YearZTDay: ihelp.dat L64官方定义+事件级Δ实证, 待≥90%命中升L1) | - | status_conflict | 1.1 tdxstat.cfg 标准契约表（stat.*，20260918 对撞定案）🆕 |
| reports | `attachPages` | — | — | — | reference_status_conflict | 12.8.4 东财 reportapi（个股/行业研报 + PDF）✅；12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `attachSize` | — | — | — | reference_status_conflict | 12.8.4 东财 reportapi（个股/行业研报 + PDF）✅；12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `author` | — | — | — | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `emRatingCode` | — | — | — | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `emRatingValue` | — | — | — | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `encodeUrl` | encodeUrl | — | — | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `lastEmRatingName` | lastEmRatingName | — | — | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `newIssuePrice` | — | — | — | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `newListingDate` | — | — | — | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `newPeIssueA` | — | — | — | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `predictNextTwoYearPe` | — | — | — | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `predictNextYearPe` | — | — | — | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `predictThisYearPe` | — | — | — | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| reports | `researcher` | — | 研究员姓名 | — | reference_status_conflict | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记）；12.9.2 其他接口实测发现 |
| 东财-clist | `f136` | f140 / f136 | 领涨股名称 / 领涨涨跌幅 | — | status_conflict | 12.8.6 东财 clist（板块排名/板块资金流）✅ |
| 东财-datacenter(英文键) | `margin_trading.balance_gr` | margin_trading.balance_gr | 融资余额单日环比增长率(%) | — | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `margin_trading.chg_10d` | margin_trading.chg_10d | 标的证券近 10 日区间累计涨跌幅(%) | — | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `margin_trading.chg_5d` | margin_trading.chg_5d | 标的证券近 5 日区间累计涨跌幅(%) | — | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `margin_trading.rqjmg` | margin_trading.rqjmg | 融券净卖出量（股） | — | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `margin_trading.rzche_10d` | margin_trading.rzche_10d | 融资偿还额近 10 日累计（元） | — | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `margin_trading.rzche_5d` | margin_trading.rzche_5d | 融资偿还额近 5 日累计（元） | — | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `margin_trading.rzjme` | margin_trading.rzjme | 融资净买入额（元） | — | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `margin_trading.rzmre_10d` | margin_trading.rzmre_10d | 融资买入额近 10 日累计（元） | — | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `margin_trading.rzmre_5d` | margin_trading.rzmre_5d | 融资买入额近 5 日累计（元） | — | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `northbound_hold.change_ratio` | northbound_hold.change_ratio | 较上一期持股比例增减变动幅度(%) | — | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `northbound_hold.change_shares` | northbound_hold.change_shares | 较上一期持股增减变动数(股) | — | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `northbound_hold.date` | northbound_hold.date | 北向持股快照报告期(YYYY-MM-DD) | — | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `northbound_hold.hold_ratio` | northbound_hold.hold_ratio | 北向持股占流通股本比例(%) | — | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `northbound_hold.hold_shares` | northbound_hold.hold_shares | 北向持股总数(股) | — | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-datacenter(英文键) | `northbound_hold.market_cap` | northbound_hold.market_cap | 北向持股市值(元) | — | status_conflict | 12.8.3.1 datacenter 北向持股 + 两融衍生字段补录（V17.1.1 全量登记） |
| 东财-em_kline_f61 | `f59` | f59 | 涨跌幅 | % | status_conflict | 12.3.3 日K线 `stock/kline/get`（🆕 V17.0.14 新增——CYQ 筹码分布数据入口） |
| 东财-push2(stock/get) | `f135` | f135 | — | 元 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-push2(stock/get) | `f136` | f136 | — | 元 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-push2(stock/get) | `f138` | f138 | — | 元 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-push2(stock/get) | `f139` | f139 | — | 元 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-push2(stock/get) | `f149` | — | 待破解 | 元 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**）；12.9.1 push2 stock/get 全字段破解（114 字段实测，项目只用 19 个） |
| 东财-push2(stock/get) | `f59` | f59 | 涨跌幅 | % | reference_status_conflict | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池）；12.3.3 日K线 `stock/kline/get`（🆕 V17.0.14 新增——CYQ 筹码分布数据入口） |
| 东财-ulist239(np/get) | `f135` | — | 净资产 | — | reference_status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f137` | — | — | — | status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f139` | — | — | — | reference_status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f140` | — | — | — | status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f141` | — | — | — | status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f142` | — | — | — | reference_status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f143` | — | — | — | reference_status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f144` | — | — | — | reference_status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f145` | — | — | — | status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f146` | — | — | — | reference_status_conflict | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f59` | f59 | — | — | status_conflict | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-资金流(em_fund_flow) | `f135` | f135 | — | 元 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f136` | f136 | — | 元 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f138` | f138 | — | 元 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f139` | f139 | — | 元 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f149` | f149 | — | 元 | status_conflict | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 同花顺-fuyao | `accounts_receivable` | accounts_receivable | 应收账款 | YSZK（应收账款） | status_conflict | 12.8.12i fuyao 财务报表叶字段补录（V17.1.1 全量登记） |
| 同花顺-fuyao | `auction.float_market_cap` | auction.float_market_cap | — | — | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `auction.pre_close_price` | snapshot.prev_price` = `auction.pre_close_price | — | — | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `cash_equivalents_net_addition` | cash_equivalents_net_addition | 现金及等价物净增加额 | ZXJL（现金及等价物净增加额） | status_conflict | 12.8.12i fuyao 财务报表叶字段补录（V17.1.1 全量登记） |
| 同花顺-fuyao | `float_market_cap` | 派生 `float_market_cap × (总股本÷流通股本) | — | — | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `growth` | growth | — | — | status_conflict | 12.8.12f fuyao 财务指标 index_id 完整度与接入分类（2026-09-01）🆕 |
| 同花顺-fuyao | `growth.calculate_operating_income_yoy_growth_ratio` | growth.calculate_operating_income_yoy_growth_ratio | — | — | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `growth.calculate_parent_holder_net_profit_yoy_growth_ratio` | growth.calculate_parent_holder_net_profit_yoy_growth_ratio | — | — | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `holder_equity_total` | holder_equity_total | 股东权益合计 | JZC（净资产/股东权益） | status_conflict | 12.8.12i fuyao 财务报表叶字段补录（V17.1.1 全量登记） |
| 同花顺-fuyao | `last_price` | 派生 `last_price ÷ f92(BPS) | — | — | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `net_profit` | net_profit | 净利润 | JLY（净利润） | status_conflict | 12.8.12i fuyao 财务报表叶字段补录（V17.1.1 全量登记） |
| 同花顺-fuyao | `operating_profit` | operating_profit | 营业利润 | YYLR（营业利润） | status_conflict | 12.8.12i fuyao 财务报表叶字段补录（V17.1.1 全量登记） |
| 同花顺-fuyao | `prev_price` | 派生 `prev_price × 板块涨停幅度 | — | — | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `profit_total` | profit_total | 利润总额 | LYZE（利润总额） | status_conflict | 12.8.12i fuyao 财务报表叶字段补录（V17.1.1 全量登记） |
| 同花顺-fuyao | `profitability` | profitability | — | — | status_conflict | 12.8.12f fuyao 财务指标 index_id 完整度与接入分类（2026-09-01）🆕 |
| 同花顺-fuyao | `profitability.index_weighted_avg_roe` | profitability.index_weighted_avg_roe | — | — | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `profitability.sale_gross_margin` | profitability.sale_gross_margin | — | — | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `profitability.sale_net_interest_ratio` | profitability.sale_net_interest_ratio | — | — | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `solvency` | solvency | — | — | status_conflict | 12.8.12f fuyao 财务指标 index_id 完整度与接入分类（2026-09-01）🆕 |
| 同花顺-fuyao | `solvency.assets_debt_ratio` | solvency.assets_debt_ratio | — | — | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `total_debt` | total_debt | 总债务(=总负债) | LDFZ（流动负债）+CPFZ（长期负债） | status_conflict | 12.8.12i fuyao 财务报表叶字段补录（V17.1.1 全量登记） |
| 同花顺-fuyao | `valuation.pb_mrq` | valuation.pb_mrq | — | — | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `valuation.pe_mrq` | valuation.pe_mrq | — | — | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `valuation.pe_ttm` | valuation.pe_ttm | — | — | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `valuation.ps_ttm` | valuation.ps_ttm | — | — | status_conflict | 12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 开盘啦(kpl) | `pe_dynamic` | pe_dynamic | 动态PE（最新报告期年化） | 倍 | status_conflict | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `pe_static` | pe_static | 静态PE（上年度年报 LYR） | 倍 | status_conflict | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `pe_ttm` | pe_ttm | PE(TTM) | 倍 | status_conflict | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 新浪(扩展API) | `item_tongbi` | item_tongbi | 同比（有才附 `_同比` 键） | — | status_conflict | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `item_value` | item_value | 科目值（字符串） | — | status_conflict | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `netamount` | netamount | 净流入额 | — | status_conflict | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `opendate` | opendate | 日期 | — | status_conflict | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `report_type` | report_type | fzb(资产负债)/lrb(利润)/llb(现金流) | — | status_conflict | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `trade` | trade | 收盘价 | — | status_conflict | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `turnover` | turnover | 换手率% | — | status_conflict | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 腾讯(qt.gtimg) | `[86]` | — | 收盘集合竞价净未匹配手数(带符号)（L2 机制确认） | 手 | reference_status_conflict | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |

## 二、候选字段（1）

| 来源 | 完整 code path | 规范名 | 含义 | 单位 | 状态判定 | 证据章节 |
|:--|:--|:--|:--|:--|:--|:--|
| ZHB-tdxstat | `stat.unknown_2` | stat.unknown_2 | 贝塔系数(60日)·L2候选(列[2]已定BetaValue: ihelp.dat L63官方定义+慢变特征实证自相关0.91, 待真实指数基准复现升L1) | - | matched | 1.1 tdxstat.cfg 标准契约表（stat.*，20260918 对撞定案）🆕 |

## 三、待破解字段（1548）

| 来源 | 完整 code path | 规范名 | 含义 | 单位 | 状态判定 | 证据章节 |
|:--|:--|:--|:--|:--|:--|:--|
| TDX(双命名源) | `Amount` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Average` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `BCancel` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Before5MinNow` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `BetaValue` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `CJJEPre1` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `CJJEPre3` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `CashZJ` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ConZAFDateNum` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `DTDate_Recent` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `DTPrice` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `DYRatio` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Date` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `DownHome` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `DynaPE` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ErrorId` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `EverZTCount` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `FCAmo` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `FCb` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `FDEPre1` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `FDEPre2` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `FreeLtgb` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `FzAmo` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Fzhsl` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `HisHigh` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `HisLow` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `HqDate` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `IPO_Price` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `InOutFlag` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Inside` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `IsKzz` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `IsT0Fund` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `IsZCZGP` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ItemNum` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Jjjz` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `KfEarnMoney` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Kzz_HSCode` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `L2OrderNum` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `L2TicNum` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `LastClose` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `LastStartZT` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `LastZTHzNum` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Ltgb` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Ltsz` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `MA5Value` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `MainBusiness` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Max` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Min` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `MorePE` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `More_YJL` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `NoticeDate_Recent` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Now` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `NowVol` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Open` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `OpenAmo` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `OpenAmoPre1` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `OpenVolPre1` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `OpenZAF` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `OpenZTBuy` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `OtherQYJzc` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Outside` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `PB_MRQ` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `PreReceiveZJ` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `QHMainYYMM` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `RDInputFee` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `RecentDZDate` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `RecentGGJYDate` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `RecentHGDate` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `RecentIncentDate` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `RecentReleaseDate` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ReportDate` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `SCancel` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `SafeValue` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ShapeValue` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ShineValue` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `StaffNum` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `StaticPE_TTM` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `StopJYDate_Recent` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `TPFlag` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `TickDiff` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `TopDate_Recent` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `TotalBVol` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `TotalSVol` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `UpHome` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `VOpenZAF` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Volume` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Wtb` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `XsFlag` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `YYYYMMDD` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `YearZTDay` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Yield` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAF` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPre10` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPre20` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPre2D` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPre3` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPre30` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPre5` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPre60` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPreMyMonth` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFPreOneYear` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFYear` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ZAFYesterday` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ZTDate_Recent` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ZTGPNum` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ZTPrice` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Zangsu` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Zgb` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Zjl` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Zjl_HB` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `Zsz` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `amount` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `amount_1d` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `amount_2d` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `amount_wan` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `amplitude_pct` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ask1` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `ask2` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ask3` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ask4` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ask5` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `average_price` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `b_gu` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `b_vol` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `baoliu2` | baoliu2 | 保留字段2 | - | matched | 2.1 协议完整 36 字段表（权威定义） |
| TDX(双命名源) | `bid1` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `bid1_vol` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `bid2` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `bid3` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `bid4` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `bid5` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `bvps` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `byte` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `category_name` | date / category_name | 事件日期 / 类别名称 | — | registry_status_only_single_source | 12.13.3 除权除息（get_gbbq / get_xdxr，0x000f）文档确认 |
| TDX(双命名源) | `change` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `change_amt` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `change_pct` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `change_pct_1d` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `change_pct_2d` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `changqi_fuzhai` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `circulating_shares` | circulating_shares / total_shares | 待破解 | 股 | registry_status_only_single_source | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `date` | date / category_name | 事件日期 / 类别名称 | — | aggregate_status_scope_unresolved | 12.13.3 除权除息（get_gbbq / get_xdxr，0x000f）文档确认 |
| TDX(双命名源) | `entrust_ratio` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `eps` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `eps_raw` | eps_raw | 每股收益原始值 | - | aggregate_status_scope_unresolved | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `fHSL` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `fLianB` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `fajirenfarengu` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `faqiren_faren_gu` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `faren_gu` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `fenhong` | fenhong / peigujia | 分红 / 配股价（XdxrRecord） | — | registry_status_only_single_source | 12.13.3 除权除息（get_gbbq / get_xdxr，0x000f）文档确认 |
| TDX(双命名源) | `float` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `float_capital` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `float_mcap_yi` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `gross_margin` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `guding_zichan` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `gudong_renshu` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `guojia_gu` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `h_gu` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `high` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `huobi_zijin` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `inside_volume` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ipodate` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `jing_li_run_raw_float` | jing_li_run_raw_float | 净利润原始值 | 千元 | aggregate_status_scope_unresolved | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `jing_lirun` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `jing_zichan` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `jingying_xianjinliu` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `last_close` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `last_price` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `latest_indicators` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `limit_down` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `limit_down_price` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `limit_up` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `lirun_zonghe` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `liu_tong_gu_ben_raw_float` | liu_tong_gu_ben_raw_float | 流通股本原始值 | 万股 | aggregate_status_scope_unresolved | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `liudong_fuzhai` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `liudong_zichan` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `liutong_guben` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `locked_amount` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `long_term_debt` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `low` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `market/code/guojiagu/faqirenfarengu/farengu/bgu/hgu/zhigonggu/liudongzichan/gudingzichan/wuxingzichan/zhuyinglirun/yingyelirun/touzishouyu/zongxianjinliu/lirunzonghe/shuihoulirun/baoliu2` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `market_snapshot` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `mcap_yi` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `meigugongji` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `meigujing_zichan` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `meiguweifenpei` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `more_info` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `name` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `net_profit` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `net_profit_yuan` | total_assets_yuan / net_profit_yuan | 待破解 | 元 | registry_status_only_single_source | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `open` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `outside_volume` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `pb` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `pe_lyr` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `pe_static` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `pe_ttm` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `peigu` | songzhuangu / peigu | 送转股 / 配股（XdxrRecord） | — | registry_status_only_single_source | 12.13.3 除权除息（get_gbbq / get_xdxr，0x000f）文档确认 |
| TDX(双命名源) | `peigujia` | fenhong / peigujia | 分红 / 配股价（XdxrRecord） | — | registry_status_only_single_source | 12.13.3 除权除息（get_gbbq / get_xdxr，0x000f）文档确认 |
| TDX(双命名源) | `pre_close` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `price` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `reserve2` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `rise_speed` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `roe` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `s_vol` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `shiyebianma` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `short_term_debt` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `shuihou_lirun` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `songzhuangu` | songzhuangu / peigu | 送转股 / 配股（XdxrRecord） | — | registry_status_only_single_source | 12.13.3 除权除息（get_gbbq / get_xdxr，0x000f）文档确认 |
| TDX(双命名源) | `str` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `total_assets_yuan` | total_assets_yuan / net_profit_yuan | 待破解 | 元 | registry_status_only_single_source | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `total_capital` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `total_shares` | circulating_shares / total_shares | 待破解 | 股 | aggregate_status_scope_unresolved | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `touzi_shouyu` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `turnover_pct` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `uint` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `updateddate` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ushort` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `vol_ratio` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `volume` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX(双命名源) | `vzangsu` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `weifen_lirun` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `weifenlirun` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `wuxing_zichan` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `yingshou_zhangkuan` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `yingye_lirun` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `zhigong_gu` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `zhongguben` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `zhuying_lirun` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `zhuying_shouru` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `zhuyinglyrun` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `ziben_gongjijin` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `zong_gu_ben_raw_float` | zong_gu_ben_raw_float | 总股本原始值 | 万股 | aggregate_status_scope_unresolved | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `zong_guben` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `zong_xianjinliu` | — | — | — | registry_status_only_single_source | — |
| TDX(双命名源) | `zong_zi_chan_raw_float` | zong_zi_chan_raw_float | 总资产原始值 | 千元 | aggregate_status_scope_unresolved | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| TDX(双命名源) | `zong_zichan` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `ColName` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `Content` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `Count` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `ErrorCode` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `ResultSetKey` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `absolute_index` | absolute_index | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `action` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `active1` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `active2` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `adjust_mode` | adjust_mode | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `adjust_mode_raw` | adjust_mode_raw | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `after_outer_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `alignment_status` | alignment_status | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `amount` | amount | 成交额 | — | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞）；12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `amount_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `anchor_date` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `anchor_date_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `ask1` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `ask_vol1` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `auction_matched_volume` | auction_matched_volume | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `auction_prev_volume_ratio` | auction_prev_volume_ratio | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `auction_unmatched_signed_volume` | auction_unmatched_signed_volume | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `b_gu_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `bao_liu_2_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `beta_60d` | beta_60d | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `bid1` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `bid_vol1` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `bin` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `bool` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `category` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `chang_qi_fu_zhai_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `change_pct` | change_pct | — | — | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `close` | time / open / high / low / close | 时间 / OHLC | — | aggregate_status_scope_unresolved | 12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `close_delta_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `close_price_milli` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `code` | code | — | — | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `columns` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `cun_huo_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `current_hand` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `depth` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `down_count` | up_count / down_count | 指数类上涨/下跌家数 | — | registry_status_only_single_source | 12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `eltdx` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `eltdx_auction_prev_volume_ratio` | eltdx_auction_prev_volume_ratio | — | — | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_has_shortline` | eltdx_has_shortline | — | — | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_ladder_level` | eltdx_ladder_level | — | — | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_limit_board_text` | eltdx_limit_board_text | — | — | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_limit_up_streak_days` | eltdx_limit_up_streak_days | — | — | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_open_change_pct` | eltdx_open_change_pct | — | — | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_open_prev_amount_ratio` | eltdx_open_prev_amount_ratio | — | — | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_open_turnover_z` | eltdx_open_turnover_z | — | — | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_open_volume_ratio` | eltdx_open_volume_ratio | — | — | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_opening_rush` | eltdx_opening_rush | — | — | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_seal_amount` | eltdx_seal_amount | — | — | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `eltdx_seal_to_float_ratio` | eltdx_seal_to_float_ratio | — | — | registry_status_only_single_source | 12.13.11 eltdx 统一层契约字段（cdata.eltdx_*，V17.2.22 接入 canonical） |
| TDX-eltdx(适配层) | `entry` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `eps_raw` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `error_code` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `event_kind` | event_kind | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `exchange` | exchange | — | — | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `extra_meta_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `extra_pair_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `fa_qi_ren_fa_ren_gu_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `fa_ren_gu_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `finance_info_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `float` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `float_market_value` | float_market_value | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `float_shares` | float_shares | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `free_float_market_value` | free_float_market_value | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `free_float_shares` | free_float_shares | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `full_code` | full_code | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `gu_ding_zi_chan_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `gu_dong_ren_shu_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `guo_jia_gu_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `h_gu_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `high` | time / open / high / low / close | 时间 / OHLC | — | aggregate_status_scope_unresolved | 12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `high_delta_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `high_price` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `high_price_milli` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `highest_ladder_level` | highest_ladder_level | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `hitCache` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `index` | index | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `industry_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `inside_dish` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `int` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `ipo_date` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `ipo_date_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `issue_date` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `jing_li_run_raw_float` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `jing_ying_xian_jin_liu_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `jing_zi_chan_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `key` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `kline_day` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `ladder_level` | ladder_level | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `last_close_price_milli` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `last_price` | last_price | — | — | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `leader_code` | leader_code | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `leader_ladder_level` | leader_ladder_level | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `li_run_zong_he_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `lianban_count` | lianban_count | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `limit_board_text` | limit_board_text | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `limit_down_price` | limit_up_price / limit_down_price | 涨停价 / 跌停价 | — | aggregate_status_scope_unresolved | 12.13.4 涨跌停限制（limits.special / scan_special，0x0452）文档确认 |
| TDX-eltdx(适配层) | `limit_or_count_raw` | limit_or_count_raw | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `limit_stat_days` | limit_stat_days | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `limit_status` | limit_status | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `limit_up_count` | limit_up_count | — | — | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `limit_up_count_in_stat_days` | limit_up_count_in_stat_days | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `limit_up_price` | limit_up_price / limit_down_price | 涨停价 / 跌停价 | — | aggregate_status_scope_unresolved | 12.13.4 涨跌停限制（limits.special / scan_special，0x0452）文档确认 |
| TDX-eltdx(适配层) | `limit_up_streak_days` | limit_up_streak_days | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `liu_dong_fu_zhai_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `liu_dong_zi_chan_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `liu_tong_gu_ben_raw_float` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `locked_amount` | vol_rise_speed / locked_amount | 量涨速 / 封单额（=bid1×bid_vol1×100） | — | aggregate_status_scope_unresolved | 12.13.6 行情列表（quotes.list_by_category，0x054b）文档确认 |
| TDX-eltdx(适配层) | `low` | time / open / high / low / close | 时间 / OHLC | — | aggregate_status_scope_unresolved | 12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `low_delta_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `low_price` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `low_price_milli` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `market_id` | market_id | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `mei_gu_jing_zi_chan_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `min2_amount` | min2_amount / opening_rush | 近2分钟金额 / 开盘抢筹 | — | registry_status_only_single_source | 12.13.6 行情列表（quotes.list_by_category，0x054b）文档确认 |
| TDX-eltdx(适配层) | `mode_or_selector_raw` | mode_or_selector_raw | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `name` | name | — | — | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `neg_price_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `open` | time / open / high / low / close | 时间 / OHLC | — | aggregate_status_scope_unresolved | 12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `open_amount` | open_amount | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `open_amount_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `open_amount_yuan` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `open_change_pct` | open_change_pct | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `open_delta_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `open_prev_amount_ratio` | open_prev_amount_ratio | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `open_prev_seal_ratio` | open_prev_seal_ratio | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `open_price` | open_price | — | — | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `open_price_milli` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `open_turnover_z` | open_turnover_z | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `open_volume_hand` | open_volume_hand | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `open_volume_ratio` | open_volume_ratio | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `opening_rush` | — | 近2分钟金额 / 开盘抢筹 | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞）；12.13.6 行情列表（quotes.list_by_category，0x054b）文档确认 |
| TDX-eltdx(适配层) | `opening_rush_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `order_count` | order_count | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `outer_disc` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `pe_ttm` | pe_ttm | — | — | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `period_name` | period_name | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `period_param_raw` | period_param_raw | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `period_raw` | period_raw | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `points` | points | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `pre_close` | pre_close | — | — | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `pre_close_price` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `prev2_seal_amount` | prev2_seal_amount | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `prev_amount` | prev_amount | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `prev_open_amount` | prev_open_amount | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `prev_open_volume_hand` | prev_open_volume_hand | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `prev_seal_amount` | prev_seal_amount | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `previous_trade_date` | previous_trade_date | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `price` | price | — | — | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `price_acc_raw` | price_acc_raw | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `price_delta_raw` | price_delta_raw | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `price_milli` | price_milli | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `province_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `qsid` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `rank` | rank | — | — | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `raw_payload` | raw_payload | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `rec_id` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `record_hex` | record_hex | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `redistime` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `relatecolumn` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `request_count` | request_count | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `reserved_zero` | reserved_zero | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `rise_speed` | rise_speed / short_turnover | 涨速 / 短换手 | — | aggregate_status_scope_unresolved | 12.13.6 行情列表（quotes.list_by_category，0x054b）文档确认 |
| TDX-eltdx(适配层) | `rise_speed_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `row_cells` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `rows` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `seal_amount` | seal_amount | — | — | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `seal_prev_ratio` | seal_prev_ratio | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `seal_to_amount_ratio` | seal_to_amount_ratio | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `seal_to_float_ratio` | seal_to_float_ratio | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `server_time_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `short_turnover` | rise_speed / short_turnover | 涨速 / 短换手 | — | registry_status_only_single_source | 12.13.6 行情列表（quotes.list_by_category，0x054b）文档确认 |
| TDX-eltdx(适配层) | `short_turnover_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `shortline_error` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `shui_hou_li_run_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `side` | side | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `snapshot_error` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `sort_by` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `source` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `start` | start | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `start_raw` | start_raw | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `stats_date` | stats_date | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `status_or_sort_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `status_raw` | status_raw | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `str` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `tableid` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `tail_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `target_trade_date` | target_trade_date | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `time` | time / open / high / low / close | 时间 / OHLC | — | aggregate_status_scope_unresolved | 12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `time_label` | time_label | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `time_minutes` | time_minutes | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `time_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `title` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `token` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `topic_id` | topic_id | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `topic_name` | topic_name | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `total_hand` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `total_seal_amount` | total_seal_amount | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `tou_zi_shou_yu_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `trade_date` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `trade_datetime` | trade_datetime | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `trading_date` | trading_date | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `unknown_after_outer_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `unknown_after_time_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `unknown_tail_raw` | unknown_tail_raw | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `up_count` | up_count / down_count | 指数类上涨/下跌家数 | — | registry_status_only_single_source | 12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `updated_date` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `updated_date_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `value` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `vol_rise_speed` | vol_rise_speed / locked_amount | 量涨速 / 封单额（=bid1×bid_vol1×100） | — | registry_status_only_single_source | 12.13.6 行情列表（quotes.list_by_category，0x054b）文档确认 |
| TDX-eltdx(适配层) | `volume` | volume | — | — | aggregate_status_scope_unresolved | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `volume_hand` | volume_hand | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `volume_lots` | volume_lots | 成交量（手） | — | registry_status_only_single_source | 12.13.5 K线（bars.get，0x052d）文档确认 |
| TDX-eltdx(适配层) | `volume_raw` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `volume_wire_value` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `wei_fen_li_run_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `wu_xing_zi_chan_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `year_limit_up_days` | year_limit_up_days | — | — | registry_status_only_single_source | 12.13.10 eltdx Helpers 净新增字段破解（V17.2.15 实测，collect_eltdx 采集 + 黄金锚对撞） |
| TDX-eltdx(适配层) | `ying_shou_zhang_kuan_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `ying_ye_li_run_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `zhu_ying_li_run_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `zhu_ying_shou_ru_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `zi_ben_gong_ji_jin_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `zong_gu_ben_raw_float` | — | — | — | aggregate_status_scope_unresolved | — |
| TDX-eltdx(适配层) | `zong_xian_jin_liu_raw_float` | — | — | — | registry_status_only_single_source | — |
| TDX-eltdx(适配层) | `zong_zi_chan_raw_float` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `YYYYMMDD` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `[31]` | [31] | 连板类计数(口径待终核: 当日涨停时==[33]连板数, 非涨停日保留历史高位值>count) | — | aggregate_status_scope_unresolved | 1. `tdxstat.cfg` (个股综合统计快照，35 个字段，7,951 行) |
| ZHB-tdxstat | `[32]` | [32] | 待破解 | — | aggregate_status_scope_unresolved | 1. `tdxstat.cfg` (个股综合统计快照，35 个字段，7,951 行) |
| ZHB-tdxstat | `board_count` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat | `change_10d` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat | `change_10k_bar` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat | `change_20d` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat | `change_30d` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat | `change_5d` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat | `change_5k_bar` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat | `change_60d` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat | `change_60d_alt` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat | `change_pct` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `change_pct_1d` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `change_pct_2d` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `change_ytd` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat | `code` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `date` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `dividend_yield` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat | `employee_count` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat | `float` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `int` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `market` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `pe_lyr` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `pe_ttm` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat | `streak_days` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat | `unseal_date` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `YYYYMMDD` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `[10]` | [10] | 待破解 | 手 | aggregate_status_scope_unresolved | 2. `tdxstat2.cfg` (成交与资金流向表，21 个字段，7,951 行) |
| ZHB-tdxstat2 | `[14]` | [14] | 待破解 | 万元 | aggregate_status_scope_unresolved | 2. `tdxstat2.cfg` (成交与资金流向表，21 个字段，7,951 行) |
| ZHB-tdxstat2 | `[15]` | [15] | 待破解 | 万元 | aggregate_status_scope_unresolved | 2. `tdxstat2.cfg` (成交与资金流向表，21 个字段，7,951 行) |
| ZHB-tdxstat2 | `[9]` | [9] | 待破解 | 手 | aggregate_status_scope_unresolved | 2. `tdxstat2.cfg` (成交与资金流向表，21 个字段，7,951 行) |
| ZHB-tdxstat2 | `amount` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `amount_1d` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `amount_2d` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `change_250k_bar` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `change_30k_bar` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `change_30k_bar_ref` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `change_mtd` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `code` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `date` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `float` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `high_52w` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `industry_code` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `ipo_price` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `low_52w` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `main_net_buy_amount` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `main_net_buy_amount_1d` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `main_net_buy_hands` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `main_net_buy_hands_1d` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `market` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `zt_seal_amount` | — | — | — | registry_status_only_single_source | — |
| ZHB-tdxstat2 | `zt_seal_amount_1d` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tdxstat2 | `zt_seal_amount_2d` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tipinfo | `YYYYMMDD` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tipinfo | `[0]` | [0] | 市场代码 | — | aggregate_status_scope_unresolved | 3. `tipinfo.dat` (财报日历与业绩快照，22 列，5,612 行) |
| ZHB-tipinfo | `[17]` | [17] | 待破解 | — | aggregate_status_scope_unresolved | 3. `tipinfo.dat` (财报日历与业绩快照，22 列，5,612 行) |
| ZHB-tipinfo | `[18]` | [18] | 恒空占位符 | — | aggregate_status_scope_unresolved | 3. `tipinfo.dat` (财报日历与业绩快照，22 列，5,612 行) |
| ZHB-tipinfo | `code` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tipinfo | `disclose_date` | — | — | — | registry_status_only_single_source | — |
| ZHB-tipinfo | `div_amount` | — | — | — | registry_status_only_single_source | — |
| ZHB-tipinfo | `div_date` | — | — | — | registry_status_only_single_source | — |
| ZHB-tipinfo | `eps` | — | — | — | aggregate_status_scope_unresolved | — |
| ZHB-tipinfo | `equity_incentive_date` | — | — | — | registry_status_only_single_source | — |
| ZHB-tipinfo | `forecast_date_recent` | — | — | — | registry_status_only_single_source | — |
| ZHB-tipinfo | `forecast_type` | — | — | — | registry_status_only_single_source | — |
| ZHB-tipinfo | `hg_amount_yi` | — | — | — | registry_status_only_single_source | — |
| ZHB-tipinfo | `hg_date` | — | — | — | registry_status_only_single_source | — |
| ZHB-tipinfo | `report_period` | — | — | — | registry_status_only_single_source | — |
| ZHB-tipinfo | `suspend_major_event_date` | — | — | — | registry_status_only_single_source | — |
| ZHB-tipinfo | `zt_date_recent` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `amount` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `amplitude` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `avg_change` | avg_change | 待破解 | — | registry_status_only_single_source | 12.10.7 开盘红板块排行（sector_ranking_kph）补充字段 |
| levistock(ftshare) | `buy_amount` | buy_amount / sell_amount | 待破解 | — | registry_status_only_single_source | 12.10.7 开盘红板块排行（sector_ranking_kph）补充字段 |
| levistock(ftshare) | `category` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `change` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `change_pct` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `change_rate` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `change_type` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `circ_market` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `circ_mv` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `circ_share` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `close_price` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `close_seal_amount` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `content` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `continuous` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `dapan_flow` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `date` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `diagnose_date` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `dict` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `down_0pct_to_1pct` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `down_1pct_to_5pct` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `down_5pct_to_limited` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `down_limit` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `down_limited` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `dt` | zt / dt | 涨停 / 跌停总数 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| levistock(ftshare) | `fall_dist` | rise_dist / fall_dist | 待破解 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| levistock(ftshare) | `fall_num` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| levistock(ftshare) | `filter_st` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `first_limit_up_time` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `first_zt_time` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `flat` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| levistock(ftshare) | `float_mv` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `goodwill_scale` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `goodwill_to_net_assets_ratio` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `hs300_index` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `hs300_week_change_ratio` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `industry_id` | industry_id / industry_zt | 行业 ID / 同行业涨停数 | — | registry_status_only_single_source | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| levistock(ftshare) | `industry_zt` | industry_id / industry_zt | 行业 ID / 同行业涨停数 | — | registry_status_only_single_source | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| levistock(ftshare) | `large_net` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `large_pct` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `last_px` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `last_zt_time` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `limit_count` | limit_tag / limit_count | 待破解 | — | aggregate_status_scope_unresolved | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| levistock(ftshare) | `limit_tag` | limit_tag / limit_count | 待破解 | — | registry_status_only_single_source | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| levistock(ftshare) | `limit_time` | limit_time / open_time | 待破解 | — | aggregate_status_scope_unresolved | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| levistock(ftshare) | `limit_up_break_count` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `limit_up_pool_yesterday` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `limit_up_price` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `main_inflow` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `main_net` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `main_pct` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `market_cap` | — | — | — | aggregate_status_scope_unresolved | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕；12.10.7 开盘红板块排行（sector_ranking_kph）补充字段 |
| levistock(ftshare) | `market_focus` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `market_focus_change` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `market_focus_rank` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `market_index_all_em` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `market_snapshot` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `mid_net` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `mid_pct` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `name` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `net_inflow` | net_inflow / market_cap | 待破解 | — | registry_status_only_single_source | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| levistock(ftshare) | `net_inflow_5d` | net_inflow_5d | 待破解 | — | registry_status_only_single_source | 12.10.7 开盘红板块排行（sector_ranking_kph）补充字段 |
| levistock(ftshare) | `net_profit_scale` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `net_profit_yoy_ratio` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `open_time` | limit_time / open_time | 待破解 | — | registry_status_only_single_source | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| levistock(ftshare) | `open_times` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `org_participate` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `participation_wish` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `participation_wish_5days` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `participation_wish_5days_change` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `participation_wish_change` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `pb` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `pe_dynamic` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `pe_static` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `pe_ttm` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `plate_code` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `pledge_company_count` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `pledge_deal_count` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `pledge_summary` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `pledge_total_market_value` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `pledge_total_ratio` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `pledge_total_shares` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `pre_close` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `prev_turnover` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `price` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `probe_trading_day` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `q_zrcs` | s_zrcs / q_zrcs | 昨日沪市 / 昨日全市成交额 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| levistock(ftshare) | `qscln` | szln / qscln | 待破解 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| levistock(ftshare) | `ready` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `reason` | reason | 涨停原因 | — | aggregate_status_scope_unresolved | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| levistock(ftshare) | `resume_time` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `rise_dist` | rise_dist / fall_dist | 待破解 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| levistock(ftshare) | `rise_num` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| levistock(ftshare) | `s_zrcs` | s_zrcs / q_zrcs | 昨日沪市 / 昨日全市成交额 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| levistock(ftshare) | `seal_amount` | seal_amount / seal_money | 待破解 | — | aggregate_status_scope_unresolved | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| levistock(ftshare) | `seal_money` | seal_amount / seal_money | 待破解 | — | aggregate_status_scope_unresolved | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| levistock(ftshare) | `sector` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `sector_ranking_kph` | sector_ranking_kph | — | — | registry_status_only_single_source | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `sector_stocks_his_kph` | sector_stocks_his_kph | — | — | registry_status_only_single_source | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `secu_code` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `secu_name` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `security_code` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `sell_amount` | buy_amount / sell_amount | 待破解 | — | registry_status_only_single_source | 12.10.7 开盘红板块排行（sector_ranking_kph）补充字段 |
| levistock(ftshare) | `sh_change_pct` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `sh_close` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `shares` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `sign` | sign | 市场人气判断文字 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| levistock(ftshare) | `sjdt` | sjzt / sjdt | 待破解 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| levistock(ftshare) | `sjzt` | sjzt / sjdt | 待破解 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| levistock(ftshare) | `small_net` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `small_pct` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `speed` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `status` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `stdt` | stzt / stdt | ST 涨停 / 跌停 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| levistock(ftshare) | `stock_code` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `stock_count` | stock_count | 成分股数量 | — | registry_status_only_single_source | 12.10.7 开盘红板块排行（sector_ranking_kph）补充字段 |
| levistock(ftshare) | `stock_name` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `stzt` | stzt / stdt | ST 涨停 / 跌停 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| levistock(ftshare) | `suspend` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `suspend_time` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `suspension_list` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `suspension_type` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `symbol` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `sz_change_pct` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `sz_close` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `szln` | szln / qscln | 待破解 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| levistock(ftshare) | `themes` | themes | 题材 | — | registry_status_only_single_source | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| levistock(ftshare) | `time` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `title` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `total_market` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `total_mv` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `total_score` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `trade_date` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `ts_code` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `turnover` | turnover / turnover_rate | 成交额 / 换手率% | — | aggregate_status_scope_unresolved | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕 |
| levistock(ftshare) | `turnover_pct` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `turnover_rate` | — | — | — | aggregate_status_scope_unresolved | 12.10.4 开盘红复盘（get_zttt 涨停天梯 / get_pmsl 盘面梳理 / get_his_limit_resumption 历史涨停复盘）🆕；12.10.7 开盘红板块排行（sector_ranking_kph）补充字段 |
| levistock(ftshare) | `unlock_by_date` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `up_0pct_to_1pct` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `up_1pct_to_5pct` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `up_5pct_to_limited` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `up_limit` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `up_limited` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `vol_ratio` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `volume` | — | — | — | aggregate_status_scope_unresolved | — |
| levistock(ftshare) | `xlarge_net` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `xlarge_pct` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `zt` | zt / dt | 涨停 / 跌停总数 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| levistock(ftshare) | `zt_count` | — | — | — | registry_status_only_single_source | — |
| levistock(ftshare) | `zt_days` | — | — | — | aggregate_status_scope_unresolved | — |
| reports | `ACCUM_AMOUNT` | ACCUM_AMOUNT | 累计成交额 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `AP202608211828244348` | — | — | — | registry_status_only_single_source | — |
| reports | `BEIJING` | — | — | — | registry_status_only_single_source | — |
| reports | `BUY_RATIO` | BUY_RATIO / SELL_RATIO | 买入/卖出占比 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `BUY_SEAT` | BUY_SEAT / SELL_SEAT | 买入/卖出前5席位数 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `CHANGE_TYPE` | CHANGE_TYPE | 异动类型代码 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `DEAL_AMOUNT_RATIO` | DEAL_AMOUNT_RATIO | 成交额占比 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `DEAL_NET_RATIO` | DEAL_NET_RATIO | 净额占比 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `EXPLAIN` | EXPLAIN | 待破解 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `FIN_BALANCE_GR` | FIN_BALANCE_GR | 融资余额增长率 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `FREE_MARKET_CAP` | FREE_MARKET_CAP | 流通市值 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `NET_BS_AMT` | NET_BS_AMT | 净买卖额 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `OTHER` | — | — | — | registry_status_only_single_source | — |
| reports | `RQJMG` | RZJME / RQJMG | 融资净买入 / 融券净卖出 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `RQYL` | RQYL | 融券余量 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `RZJME` | RZJME / RQJMG | 融资净买入 / 融券净卖出 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `RZRQYECZ` | RZRQYECZ | 两融余额差值 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `RZYEZB` | RZYEZB | 融资余额占比 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `SELL_RATIO` | BUY_RATIO / SELL_RATIO | 买入/卖出占比 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `SELL_SEAT` | BUY_SEAT / SELL_SEAT | 买入/卖出前5席位数 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `SH600519` | — | — | — | registry_status_only_single_source | — |
| reports | `SHANGHAI` | — | — | — | registry_status_only_single_source | — |
| reports | `SHENZHEN` | — | — | — | registry_status_only_single_source | — |
| reports | `TRADE_MARKET` | TRADE_MARKET | 待破解 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `actualLastTwoYearEps` | actualLastTwoYearEps | 前年实际 EPS | — | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `actualLastYearEps` | actualLastYearEps | 去年实际 EPS | — | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `adjunctSize` | adjunctSize / adjunctType | 附件大小/类型 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `adjunctType` | adjunctSize / adjunctType | 附件大小/类型 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `adjunctUrl` | adjunctUrl | 待破解 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `analyse` | analyse / analyse_title | 待破解 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `analyse_title` | analyse / analyse_title | 待破解 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `announcementType` | announcementType | 公告类型代码 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `attachType` | attachType | 附件类型 | — | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `audio_url` | audio_url | 音频链接 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `column` | column | 栏目代码 | — | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `emIndustryCode` | emIndustryCode | 东财行业码 | — | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `get_industry_reports` | — | — | — | registry_status_only_single_source | — |
| reports | `get_reports` | — | — | — | registry_status_only_single_source | — |
| reports | `indvAimPriceL` | indvAimPriceL | 目标价 L | — | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `indvAimPriceT` | indvAimPriceT | 目标价 T | — | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `indvIsNew` | indvIsNew | 新研报标记 | — | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `level` | level | 待破解 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `orgId` | secName / orgId | 证券名 / 机构ID | — | matched | 12.9.2 其他接口实测发现 |
| reports | `orgType` | orgType | 机构类型标记 | — | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `reading_num` | reading_num / share_num | 阅读数/分享数 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `sRatingCode` | sRatingCode | 待破解 | — | registry_status_only_single_source | 12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `secName` | secName / orgId | 证券名 / 机构ID | — | matched | 12.9.2 其他接口实测发现 |
| reports | `share_num` | reading_num / share_num | 阅读数/分享数 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `shortTitle` | shortTitle | 短标题 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `stock_list` | stock_list | 待破解 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `subject_name` | subjects / subject_name | 主题分类 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `subjects` | subjects / subject_name | 主题分类 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `topic` | topic | 话题 | — | matched | 12.9.2 其他接口实测发现 |
| reports | `white` | — | — | — | registry_status_only_single_source | — |
| 东财-clist | `f128` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-clist | `f13` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-clist | `f141` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-clist | `f2` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-clist | `f207` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-clist | `f257` | — | — | — | registry_status_only_single_source | — |
| 东财-clist | `f4` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-datacenter(英文键) | `able_shares` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `amount` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-datacenter(英文键) | `avg_shares` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `balance_gr` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `bonus_ratio` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `bonus_rmb` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `buyer` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `change_num` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `change_ratio` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `change_shares` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `chg_10d` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `chg_5d` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `close` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-datacenter(英文键) | `date` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-datacenter(英文键) | `hold_ratio` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `hold_shares` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `holder_num` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `lockup_expiry` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `margin_trading` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `market_cap` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-datacenter(英文键) | `northbound_hold` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `plan` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `price` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-datacenter(英文键) | `ratio` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rqchl` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rqjmg` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rqmcl` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rqye` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzche` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzche_10d` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzche_5d` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzjme` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzmre` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzmre_10d` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzmre_5d` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzrqye` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `rzye` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `seller` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `shares` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-datacenter(英文键) | `transfer_ratio` | — | — | — | registry_status_only_single_source | — |
| 东财-datacenter(英文键) | `type` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-datacenter(英文键) | `vol` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-em_kline_f61 | `f43` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-em_kline_f61 | `f85` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f1` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f10` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f100` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f102` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f103` | ocf_ttm(f103) | 经营活动现金流量净额 TTM | 元 | aggregate_status_scope_unresolved | 12.9.1 push2 stock/get 全字段破解（114 字段实测，项目只用 19 个） |
| 东财-push2(stock/get) | `f106` | f106 | 待破解 | - | aggregate_status_scope_unresolved | 12.3.1 单股行情 `stock/get`（已由 get_em_quote_full 验证） |
| 东财-push2(stock/get) | `f108` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f109` | net_profit_annual(f109) | 归母净利润 最新年报 | 元 | aggregate_status_scope_unresolved | 12.9.1 push2 stock/get 全字段破解（114 字段实测，项目只用 19 个） |
| 东财-push2(stock/get) | `f113` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f114` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f115` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f12` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f123` | f123 | — | — | aggregate_status_scope_unresolved | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f124` | f124 | — | — | aggregate_status_scope_unresolved | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f125` | f125 | — | — | aggregate_status_scope_unresolved | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f126` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f129` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f13` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f130` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f131` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f132` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f133` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f134` | f134 | — | — | aggregate_status_scope_unresolved | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f15` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f150` | — | — | — | registry_status_only_single_source | — |
| 东财-push2(stock/get) | `f151` | — | — | — | registry_status_only_single_source | — |
| 东财-push2(stock/get) | `f153` | f153 | — | — | aggregate_status_scope_unresolved | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f154` | f154 | — | — | aggregate_status_scope_unresolved | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f155` | — | — | — | registry_status_only_single_source | — |
| 东财-push2(stock/get) | `f157` | — | — | — | registry_status_only_single_source | — |
| 东财-push2(stock/get) | `f160` | eps_annual(f160) | 待破解 | 元/股 | aggregate_status_scope_unresolved | 12.9.1 push2 stock/get 全字段破解（114 字段实测，项目只用 19 个） |
| 东财-push2(stock/get) | `f161` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f17` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f172` | f172 | — | — | aggregate_status_scope_unresolved | 12.9.1 push2 stock/get 全字段破解（114 字段实测，项目只用 19 个） |
| 东财-push2(stock/get) | `f174` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f176` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f178` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f18` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f19` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f191` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f192` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f199` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f2` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f216` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f23` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f24` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f25` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f250` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f26` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f27` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f29` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f3` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f37` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f38` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f39` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f4` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f40` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f41` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f49` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f62` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f63` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f64` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f65` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f66` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f69` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f7` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f70` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f72` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f73` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f74` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f75` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f76` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f77` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f8` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f80` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f81` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f82` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f83` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f87` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2(stock/get) | `f9` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `HHMMSS` | — | — | — | registry_status_only_single_source | — |
| 东财-push2ex | `broken_count` | — | — | — | registry_status_only_single_source | — |
| 东财-push2ex | `change_pct` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `circulating_value` | — | — | — | registry_status_only_single_source | — |
| 东财-push2ex | `code` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `first_limit_time` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `last_limit_time` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `limit_broken_pool` | — | — | — | status_missing | — |
| 东财-push2ex | `limit_count` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `limit_down_pool` | — | — | — | registry_status_only_single_source | — |
| 东财-push2ex | `limit_fund` | — | — | — | registry_status_only_single_source | — |
| 东财-push2ex | `limit_up_pool` | — | — | — | status_missing | — |
| 东财-push2ex | `name` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `price` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `sector` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `total_value` | — | — | — | registry_status_only_single_source | — |
| 东财-push2ex | `turnover_rate` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-push2ex | `y_first_seal` | — | — | — | registry_status_only_single_source | — |
| 东财-push2ex | `y_limit_count` | — | — | — | registry_status_only_single_source | — |
| 东财-push2ex | `yfbt` | yfbt / ylbc | 昨日首次封板时间 / 昨日连板数 | HHMMSS / 板 | registry_status_only_single_source | 12.8.1 东财 push2ex（涨停/炸板/跌停/昨涨停四池）✅ |
| 东财-push2ex | `ylbc` | yfbt / ylbc | 昨日首次封板时间 / 昨日连板数 | HHMMSS / 板 | registry_status_only_single_source | 12.8.1 东财 push2ex（涨停/炸板/跌停/昨涨停四池）✅ |
| 东财-push2ex | `zt_continuous` | — | — | — | registry_status_only_single_source | — |
| 东财-push2ex | `zt_days` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-ulist239(np/get) | `f104` | f104 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f105` | f105 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f106` | f106 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f107` | f107 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f108` | f108 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f11` | f11 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f111` | f111 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f116` | f116 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f117` | f117 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f118` | f118 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f119` | f119 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f120` | f120 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f121` | — | — | — | aggregate_status_scope_unresolved | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f122` | — | — | — | aggregate_status_scope_unresolved | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f123` | f123 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f125` | f125 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f126` | f126 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f127` | f127 | 委比 | — | aggregate_status_scope_unresolved | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f128` | f128 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f13` | f13 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f133` | f133 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f134` | f134 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f136` | — | — | — | matched | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f138` | — | — | — | matched | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f148` | f148 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f149` | — | — | — | matched | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f152` | f152 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f153` | f153 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f154` | f154 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f194` | f194 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f204` | f204 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f205` | f205 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f206` | f206 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f207` | f207 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f208` | f208 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f209` | f209 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f210` | f210 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f213` | f213 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f214` | f214 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f215` | f215 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f216` | f216 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f217` | f217 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f218` | f218 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f219` | f219 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f22` | f22 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f220` | f220 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f222` | f222 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f223` | f223 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f227` | f227 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f235` | f235 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f236` | f236 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f237` | f237 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f238` | f238 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f239` | f239 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f240` | f240 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f241` | f241 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f242` | f242 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f243` | f243 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f244` | f244 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f245` | f245 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f246` | f246 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f247` | f247 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f248` | f248 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f249` | f249 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f250` | f250 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f27` | f27 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f28` | f28 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f30` | f30 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f45` | f45 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f46` | f46 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f49` | f49 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f63` | f63 | — | — | aggregate_status_scope_unresolved | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f93` | f93 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f97` | f97 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f98` | f98 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f99` | f99 | — | — | registry_status_only_single_source | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-热榜(em_hot) | `hot_rank` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f48` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f51` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f52` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f53` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f54` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f55` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f56` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f57` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f62` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f66` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f69` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f72` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f75` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f78` | — | — | — | aggregate_status_scope_unresolved | — |
| 东财-资金流(em_fund_flow) | `f84` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `BPS` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `act_cash_flow_net` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `amount_1d` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `amount_2d` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `amplitude` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `analysis_content` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `anomaly_list` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `asset_type` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `assets_debt_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `assets_total` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `auction_amount` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `auction_pct` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `auction_price` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `auction_turnover_pct` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `auction_unmatched` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `auction_volume` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `auction_volume_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `auction_yesterday_ratio_pct` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `basic_eps` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `buy_value` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `calculate_operating_income_yoy_growth_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `calculate_operating_profit_yoy_growth_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `calculate_parent_holder_net_profit_yoy_growth_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `calendar` | a-share/calendar/trading-days | — | — | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `cash` | — | — | — | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕；12.8.12f fuyao 财务指标 index_id 完整度与接入分类（2026-09-01）🆕 |
| 同花顺-fuyao | `cash_meet_invest_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `cash_operating_index` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `cash_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `catalog` | a-share-index/catalog/ths-index-list | — | — | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `change` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `close_price` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `companies` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `constituents` | a-share-index/constituents/ths-stock-list | — | — | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `continue_day_cnt` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `continue_day_text` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `count_captured` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `currency` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `current_assets_turnover_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `current_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `date` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `date_ms` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `day` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `ded_weighted_roe` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `diagnostics` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `diagnostics/detail` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `dividend_per_share` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `dividends` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `dragon_tiger` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `drawdowns` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `dump` | dump/market-dumps/{daily-k,daily-k-10d,adjustment-factors}/download-url | — | — | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `earned_interest_multiple` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `ex_date_ms` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `exchange` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `experience` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `fin_report` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `financials` | — | — | — | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `financing_cash_flow_net` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `first_limit_time` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `fiscal_period` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `fiscal_year` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `fixed_asset_invest_expansion_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `fund/companies/detail` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund/holders/top` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund/managers/detail` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund/market/snapshot` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund/performance/nav` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund/profile/detail` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund_large_buy` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund_large_sell` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund_mid_buy` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund_mid_sell` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund_super_buy` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `fund_super_sell` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `h1_indicators` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `h1_indicators_ready` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `heat` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `high` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `high_price` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `historical` | — | — | — | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `holders` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `holders/detail` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `hot_rank` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `income_tax_expense` | income_tax_expense | 所得税费用 | —（云不暴露; F10 利润表） | matched | 12.8.12i fuyao 财务报表叶字段补录（V17.1.1 全量登记） |
| 同花顺-fuyao | `index_deduct_weighted_avg_roe` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `index_weighted_avg_roe` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `indicators` | a-share/financials/indicators | — | — | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `interest_expenses` | interest_expenses | 利息支出 | —（云不暴露; F10 利润表财务费用内含） | matched | 12.8.12i fuyao 财务报表叶字段补录（V17.1.1 全量登记） |
| 同花顺-fuyao | `inventory_turnover_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `invest_cash_flow_net` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `is_new` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `is_st` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `item` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `keyword_list` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `last_limit_time` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `limit_reason` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `limit_up_reason` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `limit_up_time` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `list` | meta/tickers/list | — | — | aggregate_status_scope_unresolved | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `long_term_debt_equity_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `low` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `low_price` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `main_net_buy_hands` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `manage_fee` | manage_fee | 管理费用 | —（云不暴露; TDX F10 利润表 line 98） | matched | 12.8.12i fuyao 财务报表叶字段补录（V17.1.1 全量登记） |
| 同花顺-fuyao | `managers` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `market` | dump/market-dumps/{daily-k,daily-k-10d,adjustment-factors}/download-url | — | — | aggregate_status_scope_unresolved | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `max_seal_money` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `meta` | — | — | — | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `meta/tickers/list` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `meta/tickers/search` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `name` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `nav` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `net_profit_cash_content` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `net_rate` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `net_value` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `news` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `non_current_nets_total` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `offerings` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `offerings/list` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `open` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `open_price` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `open_times` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `operating_cash_flow_net_divide_income` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `operating_costs` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `operating_expenses` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `operating_income` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `operation` | operation | — | — | registry_status_only_single_source | 12.8.12f fuyao 财务指标 index_id 完整度与接入分类（2026-09-01）🆕 |
| 同花顺-fuyao | `parent_holder_net_profit` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `pay_dividends_profits_interest_cash` | pay_dividends_profits_interest_cash | 分红/利息现金支出 | —（云不暴露; F10 现金流量表） | matched | 12.8.12i fuyao 财务报表叶字段补录（V17.1.1 全量登记） |
| 同花顺-fuyao | `pay_fixed_assets_etc_cash` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `pb_mrq` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `pcf_ttm` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `pe_mrq` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `pe_ttm` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `per_share_bonus` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `performance` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `period` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `period_end_ms` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `pre_close_price` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `price_change` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `price_change_ratio_pct` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `prices` | — | — | — | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `probe_trading_day` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `profile` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `ps_ttm` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `quick_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `range_days` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `rank` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `rank_change` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `rank_trend` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `receive_account_turnover_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `report_date_ms` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `research_and_development_expenses` | research_and_development_expenses | 研发费用 | —（云不暴露; F10 利润表） | matched | 12.8.12i fuyao 财务报表叶字段补录（V17.1.1 全量登记） |
| 同花顺-fuyao | `returns` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `revenue_ttm` | — | 营业总收入 TTM（push2 f104）；富耀 operating_income 回算口径约差 1.8%，仅近似兜底 | 元 | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕；12.8.12d THS 族替代 push 域能力矩阵（V17.0.7，2026-08-25 实测定案）🆕 |
| 同花顺-fuyao | `roa` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `sale_gross_margin` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `sale_net_interest_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `sales_fee` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `seal_money` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `search` | meta/tickers/search | — | — | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `sell_value` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `snake_case` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `stock_name` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `tag_name` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `thscode` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `ticker` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `tickers` | — | — | — | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `top` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `total` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `total_assets_growth_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `total_assets_net_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `total_assets_turnover_ratio` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `total_current_assets` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `turnover` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `turnover_ratio_pct` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `valuations` | a-share/valuations/snapshot | — | — | registry_status_only_single_source | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `volume` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `week` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `weighted_roe` | — | — | — | registry_status_only_single_source | — |
| 同花顺-fuyao | `zt_seal_amount_1d` | — | — | — | aggregate_status_scope_unresolved | — |
| 同花顺-fuyao | `zt_seal_amount_2d` | — | — | — | aggregate_status_scope_unresolved | — |
| 巨潮(cninfo) | `answer` | — | — | — | registry_status_only_single_source | — |
| 巨潮(cninfo) | `answerer` | — | — | — | registry_status_only_single_source | — |
| 巨潮(cninfo) | `ask_time` | — | — | — | registry_status_only_single_source | — |
| 巨潮(cninfo) | `code` | — | — | — | aggregate_status_scope_unresolved | — |
| 巨潮(cninfo) | `company` | — | — | — | registry_status_only_single_source | — |
| 巨潮(cninfo) | `date` | — | — | — | aggregate_status_scope_unresolved | — |
| 巨潮(cninfo) | `question` | — | — | — | registry_status_only_single_source | — |
| 巨潮(cninfo) | `title` | — | — | — | aggregate_status_scope_unresolved | — |
| 巨潮(cninfo) | `type` | — | — | — | aggregate_status_scope_unresolved | — |
| 巨潮(cninfo) | `url` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `ACCUM_AMOUNT` | — | — | — | status_missing | — |
| 市场源(market_sources) | `BILLBOARD_BUY_AMT` | — | — | — | status_missing | — |
| 市场源(market_sources) | `BILLBOARD_DEAL_AMT` | — | — | — | status_missing | — |
| 市场源(market_sources) | `BILLBOARD_NET_AMT` | — | — | — | status_missing | — |
| 市场源(market_sources) | `BILLBOARD_SELL_AMT` | — | — | — | status_missing | — |
| 市场源(market_sources) | `BUY_RATIO` | — | — | — | status_missing | — |
| 市场源(market_sources) | `BUY_SEAT` | — | — | — | status_missing | — |
| 市场源(market_sources) | `BUY_SEAT_NEW` | — | — | — | status_missing | — |
| 市场源(market_sources) | `CHANGE_RATE` | — | — | — | status_missing | — |
| 市场源(market_sources) | `CHANGE_TYPE` | — | — | — | status_missing | — |
| 市场源(market_sources) | `CLOSE_PRICE` | — | — | — | status_missing | — |
| 市场源(market_sources) | `D10_CLOSE_ADJCHRATE` | — | — | — | status_missing | — |
| 市场源(market_sources) | `D1_CLOSE_ADJCHRATE` | — | — | — | status_missing | — |
| 市场源(market_sources) | `D20_CLOSE_ADJCHRATE` | — | — | — | status_missing | — |
| 市场源(market_sources) | `D2_CLOSE_ADJCHRATE` | — | — | — | status_missing | — |
| 市场源(market_sources) | `D30_CLOSE_ADJCHRATE` | — | — | — | status_missing | — |
| 市场源(market_sources) | `D5_CLOSE_ADJCHRATE` | — | — | — | status_missing | — |
| 市场源(market_sources) | `DEAL_AMOUNT_RATIO` | — | — | — | status_missing | — |
| 市场源(market_sources) | `DEAL_NET_RATIO` | — | — | — | status_missing | — |
| 市场源(market_sources) | `EXPLAIN` | — | — | — | status_missing | — |
| 市场源(market_sources) | `EXPLANATION` | — | — | — | status_missing | — |
| 市场源(market_sources) | `FREE_MARKET_CAP` | — | — | — | status_missing | — |
| 市场源(market_sources) | `MARKET` | — | — | — | status_missing | — |
| 市场源(market_sources) | `NET_BS_AMT` | — | — | — | status_missing | — |
| 市场源(market_sources) | `SECUCODE` | — | — | — | status_missing | — |
| 市场源(market_sources) | `SECURITY_CODE` | — | — | — | status_missing | — |
| 市场源(market_sources) | `SECURITY_INNER_CODE` | — | — | — | status_missing | — |
| 市场源(market_sources) | `SECURITY_NAME_ABBR` | — | — | — | status_missing | — |
| 市场源(market_sources) | `SECURITY_TYPE_CODE` | — | — | — | status_missing | — |
| 市场源(market_sources) | `SELL_RATIO` | — | — | — | status_missing | — |
| 市场源(market_sources) | `SELL_SEAT` | — | — | — | status_missing | — |
| 市场源(market_sources) | `SELL_SEAT_NEW` | — | — | — | status_missing | — |
| 市场源(market_sources) | `SUM_BUY_AMT` | — | — | — | status_missing | — |
| 市场源(market_sources) | `SUM_SELL_AMT` | — | — | — | status_missing | — |
| 市场源(market_sources) | `TRADE_DATE` | — | — | — | status_missing | — |
| 市场源(market_sources) | `TRADE_ID` | — | — | — | status_missing | — |
| 市场源(market_sources) | `TRADE_MARKET` | — | — | — | status_missing | — |
| 市场源(market_sources) | `TRADE_MARKET_CODE` | — | — | — | status_missing | — |
| 市场源(market_sources) | `TURNOVERRATE` | — | — | — | status_missing | — |
| 市场源(market_sources) | `amplitude` | — | — | — | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `broken_num` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `broken_ratio` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `change_type` | change_type | 变动类型 | — | aggregate_status_scope_unresolved | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `color` | color | 待破解 | — | aggregate_status_scope_unresolved | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `continuous_rate` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `count` | — | — | — | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `dates` | dates | 日期序列 | — | registry_status_only_single_source | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `day` | — | — | — | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `df_num` | — | — | — | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `down_10` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `down_2` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `down_4` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `down_6` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `down_8` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `down_num` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `dragon_tiger_today` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `dt` | zt / dt | 涨停 / 跌停总数 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `dt_ever` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `dt_num` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `fall_dist` | rise_dist / fall_dist | 待破解 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `fall_num` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `flat` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `flat_num` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `kpl_error` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `lbgd` | — | — | — | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `limit_time` | limit_time | 涨停时间 | — | aggregate_status_scope_unresolved | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `limit_up_board` | limit_up_board | 待破解 | — | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `main_buy` | — | — | — | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `main_inflow` | — | — | — | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `main_sell` | — | — | — | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `market_degree` | market_degree | 待破解 | — | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `max_seal` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `one_word` | one_word | 一句话点评 | — | registry_status_only_single_source | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `performance` | performance | 昨涨停今表现 | — | aggregate_status_scope_unresolved | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `plate_rotation_top` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `plates` | plates | 相关板块列表 | — | aggregate_status_scope_unresolved | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `popular` | popular | 人气值 | — | registry_status_only_single_source | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `prev_amount_wan` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `preview_balance` | preview_balance | 盘前余额 | — | registry_status_only_single_source | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `preview_balance_change_px` | preview_balance_change_px | 盘前余额变化价 | — | registry_status_only_single_source | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `profit_ratio` | profit_ratio | 获利率 | — | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `q_zrcs` | s_zrcs / q_zrcs | 昨日沪市 / 昨日全市成交额 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `qscln` | szln / qscln | 待破解 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `reason` | — | — | — | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `rise_dist` | rise_dist / fall_dist | 待破解 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `rise_num` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `s_zrcs` | s_zrcs / q_zrcs | 昨日沪市 / 昨日全市成交额 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `seal_amount` | — | — | — | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `sector` | — | — | — | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `sector_code` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `shsz_balance` | shsz_balance | 两市成交额 | — | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `shsz_balance_change_px` | shsz_balance_change_px | 较上日成交额变化 | — | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `sign` | sign | 市场人气判断文字 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `sjdt` | sjzt / sjdt | 待破解 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `sjzt` | sjzt / sjdt | 待破解 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `source` | source | 数据来源标识 | — | aggregate_status_scope_unresolved | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `status` | — | — | — | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `stdt` | stzt / stdt | ST 涨停 / 跌停 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `stock_changes_8201` | — | — | — | status_missing | — |
| 市场源(market_sources) | `strong` | — | — | — | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `stzt` | stzt / stdt | ST 涨停 / 跌停 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `suspend_num` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `szln` | szln / qscln | 待破解 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `tip` | — | — | — | aggregate_status_scope_unresolved | — |
| 市场源(market_sources) | `total_amount_wan` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `trade_date` | — | — | — | status_missing | — |
| 市场源(market_sources) | `turnover_real` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `up_10` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `up_2` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `up_4` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `up_6` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `up_8` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `up_down_dis` | up_down_dis | 待破解 | — | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `up_num` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `up_open_num` | up_open_num | 炸板数量 | — | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `up_open_ratio` | up_open_ratio | 高开率 | — | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `up_ratio` | up_ratio / up_ratio_num | 封板率 / 封板数量 | — | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `up_ratio_num` | up_ratio / up_ratio_num | 封板率 / 封板数量 | — | registry_status_only_single_source | 12.10.2 财联社市场情绪（market_emotion_cls）🆕 |
| 市场源(market_sources) | `value` | value | 待破解 | — | aggregate_status_scope_unresolved | 12.10.7a 市场源 market_sources 原始字段补录（V17.1.1 全量登记） |
| 市场源(market_sources) | `zt` | zt / dt | 涨停 / 跌停总数 | — | aggregate_status_scope_unresolved | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 市场源(market_sources) | `zt_natural` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `zt_num` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `zt_time` | — | — | — | registry_status_only_single_source | — |
| 市场源(market_sources) | `ztjs` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `Ad_x` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `BaceFaceList` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `BoomReason` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Boom_ZS` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `BuyIn` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `CQ` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `CYWWZS` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `D3` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `DJI` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `DT` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `DTJS` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Date` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `Day` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `DongXiang` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `FAIL` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `GNSM` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `ID` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `IncreaseAmount` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `IsBoom` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Item` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `JoinNum` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `LBstatus` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `LZInfo` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `List` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `List_Special` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Money` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Name` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `OHLC` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `PidType` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `PlateID` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `QD` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Reason` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `SCLT` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `ST` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `SZJS` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Special` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `TTMPeRate` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Theme` | Theme/InfoBKR | — | — | registry_status_only_single_source | 12.17.1 kaipanla-data-parser 补充（2026-08-09 实测 10 接口 + 63 字段映射验证）🆕 |
| 开盘啦(kpl) | `Time` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Title` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Topic` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Tur` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Turnover` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `Vol` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `XDJS` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `ZBL` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `ZT` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `ZTJS` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `ZTNum` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `actual_float_mv` | actual_float_mv | 实际流通市值 | 元 | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `actualcirculation_value` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `amount` | amount | 成交额 | 元 | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `amount_in` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `amplitude` | amplitude | 振幅% | % | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `apiv` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `avg_px` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `bal` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `bid` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `big_order_net_3m` | big_order_net_3m | 300万以上大单净额 | 元 | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `bl` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `board_tag` | board_tag | 所属板块标签 | — | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `break_limit_up_times` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `buy_lock_volume_ratio` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `change_pct` | change_pct | 涨跌幅% | % | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `change_percent` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `circ_mv` | circ_mv | 流通市值 | 元 | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `circulation_amount` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `circulation_value` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `close_seal_amount` | close_seal_amount | 收盘封单额 | 元 | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `code` | code | 股票代码 | — | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `color` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `content` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `content2` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `cur_price` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `data` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `date` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `description` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `df_num` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `down_px` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `dyn_pb_rate` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `entrust_rate` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `errcode` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `f162` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `f163` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `fall_count` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `fields` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `hprice` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `info` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `inst_increase_q1` | inst_increase_q1 | 机构增仓Q1金额 | 元 | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `institutionIncrease` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `jtPeRate` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `last_px` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `lbgd` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `lead_count` | lead_count | 领涨次数 | 次 | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `limit_down_count` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `limit_pattern_text` | limit_pattern_text | 几天几板(如"3天2板") | 文本 | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `limit_up_broken_count` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `limit_up_count` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `list` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `lprice` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `main_buy` | main_buy | 主力买入额 | 元 | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `main_net` | main_net | 主力净额(≡主力净买入额) | 元 | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `main_sell` | main_sell | 主力卖出额 | 元 | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `market_temperature` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `market_value` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `max_seal_amount` | max_seal_amount | 最大封单额 | 元 | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `name` | name | 股票名称 | — | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `net_flow_ratio` | net_flow_ratio | 净流占比 | % | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `nums` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `out` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `pankou` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `pb` | pb | 市净率 | 倍 | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `pe_rate` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `period_change` | period_change | 区间涨跌幅 | % | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `phcj_volume` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `plate_type` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `popularity_rank_chg` | popularity_rank_chg | 人气排名变化 | — | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `popularity_value` | popularity_value | 人气值 | — | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `preclose` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `price` | price | 现价 | 元 | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `prod_name` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `px_change` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `px_change_rate` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `q_zrcs` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `qscln` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `real` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `real_turnover_rate` | real_turnover_rate | ★实际换手率% | % | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `rise_count` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `sell_flow_ratio` | sell_flow_ratio | 卖流占比 | % | registry_status_only_single_source | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `speed` | speed | 涨速 | — | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `state` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `state1` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `stateZT` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `status` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `status_color` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `stock_name` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `stockid` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `strong` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `time` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `tip` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `total_amount` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `total_mv` | total_mv | 总市值 | 元 | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `total_shares` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `total_turnover` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `trend` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `turnover` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `turnover_pct` | turnover_pct | 换手率% | % | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `turnover_ratio` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `up_px` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `value` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `vol` | — | — | — | aggregate_status_scope_unresolved | — |
| 开盘啦(kpl) | `volRatio` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `vol_ratio` | vol_ratio | 量比 | — | aggregate_status_scope_unresolved | 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现） |
| 开盘啦(kpl) | `weituo` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `yestRase` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `yesterday_limit_up_avg_pcp` | — | — | — | registry_status_only_single_source | — |
| 开盘啦(kpl) | `ztjs` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[11]` | [11] | 待破解 | 元 | aggregate_status_scope_unresolved | 12.2 新浪 hq.sinajs.cn 完整字段字典（33-34 字段） |
| 新浪(hq.sinajs) | `[13]` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[14]` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[15]` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[16]` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[17]` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[18]` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[19]` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[23]` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[24]` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[25]` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[26]` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[27]` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[28]` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[29]` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[32]` | [32] | 状态码 | - | aggregate_status_scope_unresolved | 12.2 新浪 hq.sinajs.cn 完整字段字典（33-34 字段） |
| 新浪(hq.sinajs) | `[58]` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(hq.sinajs) | `[59]` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(扩展API) | `ask` | bid_vol/bid/last/ask/ask_vol | 五档价量 | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `ask_vol` | bid_vol/bid/last/ask/ask_vol | 五档价量 | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `bid` | bid_vol/bid/last/ask/ask_vol | 五档价量 | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `bid_vol` | bid_vol/bid/last/ask/ask_vol | 五档价量 | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `close` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(扩展API) | `date` | — | — | — | aggregate_status_scope_unresolved | — |
| 新浪(扩展API) | `delta` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `gamma` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `iv` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `last` | bid_vol/bid/last/ask/ask_vol | 五档价量 | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `limit_down` | limit_up / limit_down | 涨跌停价 | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `limit_up` | limit_up / limit_down | 涨跌停价 | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `net_amount` | — | — | — | registry_status_only_single_source | — |
| 新浪(扩展API) | `open` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `open_interest` | open_interest | 持仓量 | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `prev_close` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `strike` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `theory` | theory | 理论价值 | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `theta` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 新浪(扩展API) | `vega` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | — | matched | 12.8.14 新浪（行情/三表/期权/资金流备胎）✅/⏸️ |
| 沪深交易所 | `sse_raw` | — | — | — | registry_status_only_single_source | — |
| 百度(baidu) | `ma10avgprice` | ma5avgprice/ma10avgprice/ma20avgprice | 待破解 | — | matched | 12.8.16 百度股市通（K线带MA）❌→⏸️ |
| 百度(baidu) | `ma20avgprice` | ma5avgprice/ma10avgprice/ma20avgprice | 待破解 | — | matched | 12.8.16 百度股市通（K线带MA）❌→⏸️ |
| 百度(baidu) | `ma5avgprice` | ma5avgprice/ma10avgprice/ma20avgprice | 待破解 | — | matched | 12.8.16 百度股市通（K线带MA）❌→⏸️ |
| 腾讯(qt.gtimg) | `[10]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[11]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[12]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[13]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[14]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[15]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[16]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[17]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[18]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[20]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[21]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[22]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[23]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[24]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[25]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[26]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[27]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[28]` | — | — | — | aggregate_status_scope_unresolved | — |
| 腾讯(qt.gtimg) | `[29]` | — | 最近逐笔成交 | - | aggregate_status_scope_unresolved | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |
| 腾讯(qt.gtimg) | `[55]` | — | — | — | registry_status_only_single_source | — |
| 腾讯(qt.gtimg) | `[7]` | [7] | 外盘 | 手 | aggregate_status_scope_unresolved | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |
| 腾讯(qt.gtimg) | `[87]` | — | 科创板/两融标记（688 段值='100'） | - | registry_status_only_single_source | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |
| 腾讯(qt.gtimg) | `[8]` | [8] | 内盘 | 手 | aggregate_status_scope_unresolved | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |
| 财联社(cls) | `catalyst` | catalyst | 催化剂描述 | — | registry_status_only_single_source | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |
| 财联社(cls) | `code` | — | — | — | aggregate_status_scope_unresolved | — |
| 财联社(cls) | `cur_heat` | rank / cur_heat | 当前热度排名 / 热度值 | — | registry_status_only_single_source | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |
| 财联社(cls) | `id` | — | — | — | registry_status_only_single_source | — |
| 财联社(cls) | `int` | — | — | — | aggregate_status_scope_unresolved | — |
| 财联社(cls) | `is_new` | is_new | 是否新上榜（1=是） | — | aggregate_status_scope_unresolved | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |
| 财联社(cls) | `level` | level | 快讯等级（重要性分级） | — | aggregate_status_scope_unresolved | 12.8.13.1 财联社快讯 telegraph 原始字段补录（V17.1.1 全量登记） |
| 财联社(cls) | `list` | — | — | — | aggregate_status_scope_unresolved | — |
| 财联社(cls) | `name` | — | — | — | aggregate_status_scope_unresolved | — |
| 财联社(cls) | `pct` | — | — | — | aggregate_status_scope_unresolved | — |
| 财联社(cls) | `plate_code` | plate_code / plate_name | 板块代码 / 名称（风口板块） | — | aggregate_status_scope_unresolved | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |
| 财联社(cls) | `plate_name` | plate_code / plate_name | 板块代码 / 名称（风口板块） | — | aggregate_status_scope_unresolved | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |
| 财联社(cls) | `plates` | trade_date / plates | 轮动日期 / 当日 top10 板块列表 | — | aggregate_status_scope_unresolved | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |
| 财联社(cls) | `rank` | rank / cur_heat | 当前热度排名 / 热度值 | — | aggregate_status_scope_unresolved | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |
| 财联社(cls) | `rank_change` | rank_change | 排名变化（正=上升，负=下降） | — | aggregate_status_scope_unresolved | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |
| 财联社(cls) | `reading_num` | reading_num | 阅读数 | — | aggregate_status_scope_unresolved | 12.8.13.1 财联社快讯 telegraph 原始字段补录（V17.1.1 全量登记） |
| 财联社(cls) | `stock_list` | stock_list | 关联股票代码列表 | — | aggregate_status_scope_unresolved | 12.8.13.1 财联社快讯 telegraph 原始字段补录（V17.1.1 全量登记） |
| 财联社(cls) | `subjects` | subjects | 主题/题材标签列表 | — | aggregate_status_scope_unresolved | 12.8.13.1 财联社快讯 telegraph 原始字段补录（V17.1.1 全量登记） |
| 财联社(cls) | `time` | — | — | — | aggregate_status_scope_unresolved | — |
| 财联社(cls) | `trade_date` | trade_date / plates | 轮动日期 / 当日 top10 板块列表 | — | aggregate_status_scope_unresolved | 12.10.5 板块轮动与热度（财联社 get_sector_rotation / get_sector_heat / market_wind_cls）🆕 |

## 四、已证伪（默认不重复破解）（0）

_无记录。_
