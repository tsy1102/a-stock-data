# 字段聚合歧义与待拆分复核

> 本文由 `field_registry.json.source_fields` 生成。逐源完整路径记录是权威定义；本文只揭示按短 code 聚合时无法安全呈现的差异。
> `aggregation_status` 只描述兼容聚合视图，不会改写逐源 `status`。疑似合并文本由分隔符启发式识别，仅供人工检查，不自动拆字段或定案。
> 本文统计的定义缺口仅限列出的复核组；单来源或全空的定义缺口仍见 [元数据缺口](field_metadata_gaps.md) 与 [未知字段队列](unknown_fields.md)。

> 聚合歧义 180 个 code；聚合定义不完整 154 个 code；疑似合并文本 748 条逐源记录。

## 同码聚合存在差异或定义缺口

### `ACCUM_AMOUNT` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `ACCUM_AMOUNT` | ACCUM_AMOUNT | 累计成交额 | — | `unverified` |
| 市场源(market_sources) · `ACCUM_AMOUNT` | — | — | — | `unverified` |

### `BILLBOARD_BUY_AMT` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `BILLBOARD_BUY_AMT` | BILLBOARD_BUY_AMT / SELL_AMT | 买入/卖出资 | 元 | `verified` |
| 市场源(market_sources) · `BILLBOARD_BUY_AMT` | — | — | — | `unverified` |

### `BILLBOARD_NET_AMT` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `BILLBOARD_NET_AMT` | BILLBOARD_NET_AMT | 龙虎榜净买额 | 元 | `verified` |
| 市场源(market_sources) · `BILLBOARD_NET_AMT` | — | — | — | `unverified` |

### `BUY_RATIO` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `BUY_RATIO` | BUY_RATIO / SELL_RATIO | 买入/卖出占比 | — | `unverified` |
| 市场源(market_sources) · `BUY_RATIO` | — | — | — | `unverified` |

### `BUY_SEAT` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `BUY_SEAT` | BUY_SEAT / SELL_SEAT | 买入/卖出前5席位数 | — | `unverified` |
| 市场源(market_sources) · `BUY_SEAT` | — | — | — | `unverified` |

### `CHANGE_RATE` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `CHANGE_RATE` | CLOSE_PRICE / CHANGE_RATE | 收盘价 / 涨跌幅 | 元/% | `verified` |
| 市场源(market_sources) · `CHANGE_RATE` | — | — | — | `unverified` |

### `CHANGE_TYPE` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `CHANGE_TYPE` | CHANGE_TYPE | 异动类型代码 | — | `unverified` |
| 市场源(market_sources) · `CHANGE_TYPE` | — | — | — | `unverified` |

### `CLOSE_PRICE` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `CLOSE_PRICE` | — | — | — | `verified` |
| 市场源(market_sources) · `CLOSE_PRICE` | — | — | — | `unverified` |

### `DEAL_AMOUNT_RATIO` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `DEAL_AMOUNT_RATIO` | DEAL_AMOUNT_RATIO | 成交额占比 | — | `unverified` |
| 市场源(market_sources) · `DEAL_AMOUNT_RATIO` | — | — | — | `unverified` |

### `DEAL_NET_RATIO` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `DEAL_NET_RATIO` | DEAL_NET_RATIO | 净额占比 | — | `unverified` |
| 市场源(market_sources) · `DEAL_NET_RATIO` | — | — | — | `unverified` |

### `Date` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `Date` | — | 日期键本身有效，但该旧 registry 身份未限定接口或父对象，无法唯一指向 K 线日、股本记录日、统计数据日或公式结果日。只退役裸路径身份；精确日期含义保存在接口级契约中。 | — | `disproved` |
| 开盘啦(kpl) · `Date` | — | — | — | `unverified` |

### `EXPLAIN` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `EXPLAIN` | EXPLAIN | 待破解 | — | `unverified` |
| 市场源(market_sources) · `EXPLAIN` | — | — | — | `unverified` |

### `EXPLANATION` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `EXPLANATION` | EXPLANATION | 上榜原因 | - | `verified` |
| 市场源(market_sources) · `EXPLANATION` | — | — | — | `unverified` |

### `FREE_MARKET_CAP` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `FREE_MARKET_CAP` | FREE_MARKET_CAP | 流通市值 | — | `unverified` |
| 市场源(market_sources) · `FREE_MARKET_CAP` | — | — | — | `unverified` |

### `NET_BS_AMT` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `NET_BS_AMT` | NET_BS_AMT | 净买卖额 | — | `unverified` |
| 市场源(market_sources) · `NET_BS_AMT` | — | — | — | `unverified` |

### `Name` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `Name` | Name | 证券名称 | — | `verified` |
| 开盘啦(kpl) · `Name` | — | — | — | `unverified` |

### `SECURITY_CODE` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `SECURITY_CODE` | SECURITY_CODE / SECURITY_NAME_ABBR | 代码 / 名称 | - | `verified` |
| 市场源(market_sources) · `SECURITY_CODE` | — | — | — | `unverified` |

### `SECURITY_NAME_ABBR` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `SECURITY_NAME_ABBR` | SECURITY_CODE / SECURITY_NAME_ABBR | 代码 / 名称 | - | `verified` |
| 市场源(market_sources) · `SECURITY_NAME_ABBR` | — | — | — | `unverified` |

### `SELL_RATIO` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `SELL_RATIO` | BUY_RATIO / SELL_RATIO | 买入/卖出占比 | — | `unverified` |
| 市场源(market_sources) · `SELL_RATIO` | — | — | — | `unverified` |

### `SELL_SEAT` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `SELL_SEAT` | BUY_SEAT / SELL_SEAT | 买入/卖出前5席位数 | — | `unverified` |
| 市场源(market_sources) · `SELL_SEAT` | — | — | — | `unverified` |

### `TRADE_DATE` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `TRADE_DATE` | TRADE_DATE | 交易日期 | — | `verified` |
| 市场源(market_sources) · `TRADE_DATE` | — | — | — | `unverified` |

### `TRADE_MARKET` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `TRADE_MARKET` | TRADE_MARKET | 待破解 | — | `unverified` |
| 市场源(market_sources) · `TRADE_MARKET` | — | — | — | `unverified` |

### `TURNOVERRATE` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `TURNOVERRATE` | TURNOVERRATE | 换手率% | % | `verified` |
| 市场源(market_sources) · `TURNOVERRATE` | — | — | — | `unverified` |

### `[0]` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[0]` | [0] | 市场代码 | — | `verified` |
| ZHB-tdxstat2 · `[0]` | [0] | 市场代码 | 0`=深, `1`=沪, `2`=京 | `verified` |
| ZHB-tipinfo · `[0]` | [0] | 市场代码 | 0`=深, `1`=沪, `2`=京 | `verified` |
| 新浪(hq.sinajs) · `[0]` | [0] | 股票名称 | - | `verified` |
| 腾讯(qt.gtimg) · `[0]` | — | 市场标识（交易所） | - | `verified` |

### `[10]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[10]` | [10] | 股息率 (%) = 官方 DYRatio | — | `verified` |
| ZHB-tdxstat2 · `[10]` | [10] | 前一交易日开盘集合竞价成交量 | 手 | `verified` |
| ZHB-tipinfo · `[10]` | [10] | 官方 DTDate_Recent | — | `verified` |
| 新浪(hq.sinajs) · `[10]` | [10] | 买一量 | 股 | `verified` |
| 腾讯(qt.gtimg) · `[10]` | [10] | 买1量 | 手 | `verified` |

### `[11]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[11]` | [11] | 自由流通股本 FreeLtgb（万股） | — | `verified` |
| ZHB-tdxstat2 · `[11]` | [11] | 本月至今累积涨跌幅 %（Month-to-Date，基准=上月末最后交易日收盘价） | float | `verified` |
| ZHB-tipinfo · `[11]` | [11] | 最新业绩预告发布日 | — | `verified` |
| 新浪(hq.sinajs) · `[11]` | [11] | 买一价（与同一响应的 [6] 竞买报价逐值重复） | 元 | `verified` |
| 腾讯(qt.gtimg) · `[11]` | [11] | 买二价 | 元 | `verified` |

### `[12]` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[12]` | [12] | 新股开板日 (YYYYMMDD) | — | `verified` |
| ZHB-tdxstat2 · `[12]` | [12] | 近250根K线涨跌幅(年线) | float | `verified` |
| ZHB-tipinfo · `[12]` | [12] | 业绩预告类型代码 | — | `verified` |
| 新浪(hq.sinajs) · `[12]` | [12]-[19] | 买二~买五 量/价 | 股/元 | `verified` |
| 腾讯(qt.gtimg) · `[12]` | [12] | 买2量 | 手 | `verified` |

### `[13]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[13]` | [13] | 上市连板数（交易日） | — | `verified` |
| ZHB-tdxstat2 · `[13]` | [13] | 通达信板块归属(881=行业板块稳定 / 880=概念·风格板块动态) | 6位字符串 | `verified` |
| ZHB-tipinfo · `[13]` | [13] | 对应限售股解禁/上市流通事件的日期，原始格式为 YYYYMMDD。两项发行人公告样本确认其为事件日期；多事件时的选取规则尚未确认。 | 日期（YYYYMMDD） | `verified` |
| 新浪(hq.sinajs) · `[13]` | [13] | 买二价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[13]` | [13] | 买三价 | 元 | `verified` |

### `[14]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[14]` | [14] | 扣非净利润 (万元) = 官方 KfEarnMoney | — | `verified` |
| ZHB-tdxstat2 · `[14]` | [14] | 当日开盘集合竞价成交额 | 万元 | `verified` |
| ZHB-tipinfo · `[14]` | [14] | 对应限售股上市流通事件的股份数量，单位万股。两个公告样本均与事件总数量吻合，ZHB 值按 0.01 万股粒度保留；多事件或分项数量的选取规则尚未确认。 | 万股 | `verified` |
| 新浪(hq.sinajs) · `[14]` | [14] | 买三档委托数量 | 股 | `verified` |
| 腾讯(qt.gtimg) · `[14]` | [14] | 买3量 | 手 | `verified` |

### `[15]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[15]` | [15] | 员工总人数 (人) = 官方 StaffNum | — | `verified` |
| ZHB-tdxstat2 · `[15]` | [15] | 前一交易日开盘集合竞价成交额 | 万元 | `verified` |
| ZHB-tipinfo · `[15]` | [15] | (老)增发事件日期 | — | `verified` |
| 新浪(hq.sinajs) · `[15]` | [15] | 买三价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[15]` | [15] | 买四价 | 元 | `verified` |

### `[16]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[16]` | [16] | 研发投入 RDInputFee（万元） | — | `verified` |
| ZHB-tdxstat2 · `[16]` | [16] | IPO 发行价 = 官方 IPO_Price | 元 | `verified` |
| ZHB-tipinfo · `[16]` | [16] | (老)增发募集金额(万元) | — | `verified` |
| 新浪(hq.sinajs) · `[16]` | [16] | 买四档委托数量 | 股 | `verified` |
| 腾讯(qt.gtimg) · `[16]` | [16] | 买4量 | 手 | `verified` |

### `[17]` — ambiguous

聚合问题：meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[17]` | [17] | 近20根K线涨跌幅(含当日) | — | `verified` |
| ZHB-tdxstat2 · `[17]` | [17] | 52周最高价 = 官方 HisHigh | 元 | `verified` |
| ZHB-tipinfo · `[17]` | [17] | 待破解 | — | `unverified` |
| 新浪(hq.sinajs) · `[17]` | [17] | 买四价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[17]` | [17] | 买五价 | 元 | `verified` |

### `[18]` — ambiguous

聚合问题：meaning_differs；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[18]` | [18] | 截至T-1的20根K线涨跌幅 | — | `verified` |
| ZHB-tdxstat2 · `[18]` | [18] | 52周最低价 = 官方 HisLow | 元 | `verified` |
| ZHB-tipinfo · `[18]` | [18] | 恒空占位符 | — | `unverified` |
| 新浪(hq.sinajs) · `[18]` | [18] | 买五档委托数量 | 股 | `verified` |
| 腾讯(qt.gtimg) · `[18]` | [18] | 买5量 | 手 | `verified` |

### `[19]` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[19]` | [19] | ✅ 近60根K线涨跌幅 | — | `verified` |
| ZHB-tdxstat2 · `[19]` | [19] | 近30根K线涨跌幅(含噪) | float | `verified` |
| ZHB-tipinfo · `[19]` | [19] | 最近回购预案日 = TDX 官方 RecentHGDate | YYYYMMDD | `verified` |
| 新浪(hq.sinajs) · `[19]` | [19] | 买五价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[19]` | [19]-[28] | 卖一~卖五 价/量 | 元/手 | `verified` |

### `[1]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[1]` | [1] | 股票代码 | — | `verified` |
| ZHB-tdxstat2 · `[1]` | [1] | 股票代码 | 6位字符串 | `verified` |
| ZHB-tipinfo · `[1]` | [1] | 股票代码 | 6位字符串 | `verified` |
| 新浪(hq.sinajs) · `[1]` | [1] | 开盘价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[1]` | [1] | 股票名称 | - | `verified` |

### `[20]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[20]` | [20] | 截至T-1的60根K线涨跌幅 | — | `verified` |
| ZHB-tdxstat2 · `[20]` | [20] | 近30根K线涨跌幅(更纯) | float | `verified` |
| ZHB-tipinfo · `[20]` | [20] | 回购预案金额上限(亿元) = TdxW 二进制提示 `回购预案:上限%.2f亿元` | 亿元 | `verified` |
| 新浪(hq.sinajs) · `[20]` | [20] | 卖一量 | 股 | `verified` |
| 腾讯(qt.gtimg) · `[20]` | [20] | 卖1量 | 手 | `verified` |

### `[21]` — ambiguous

聚合问题：meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[21]` | [21] | 年初至今涨跌幅 (YTD %) | — | `verified` |
| ZHB-tipinfo · `[21]` | [21] | 股权激励预案/草案公告日 | — | `verified` |
| 新浪(hq.sinajs) · `[21]` | [21] | 卖一价（与 [7] 竞卖价重复） | 元 | `verified` |
| 腾讯(qt.gtimg) · `[21]` | [21] | 卖二价 | 元 | `verified` |

### `[22]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[22]` | [22] | 形态/板块代码 ShapeValue | — | `verified` |
| 新浪(hq.sinajs) · `[22]` | [22] | 卖二档委托数量 | 股 | `verified` |
| 腾讯(qt.gtimg) · `[22]` | [22] | 卖二档委托数量 | 手 | `verified` |

### `[23]` — ambiguous

聚合问题：meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[23]` | [23] | 待破解 | — | `verified` |
| 新浪(hq.sinajs) · `[23]` | [23] | 卖二价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[23]` | [23] | 卖三价 | 元 | `verified` |

### `[24]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[24]` | [24] | 现金总额 CashZJ（万元） | — | `verified` |
| 新浪(hq.sinajs) · `[24]` | [24] | 卖三档委托数量 | 股 | `verified` |
| 腾讯(qt.gtimg) · `[24]` | [24] | 卖三档委托数量 | 手 | `verified` |

### `[25]` — ambiguous

聚合问题：meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[25]` | [25] | 合同负债（万元） | 万元 | `verified` |
| 新浪(hq.sinajs) · `[25]` | [25] | 卖三价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[25]` | [25] | 卖四价 | 元 | `verified` |

### `[26]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[26]` | [26] | 年内涨停天数 YearZTDay | — | `verified` |
| 新浪(hq.sinajs) · `[26]` | [26] | 卖四档委托数量 | 股 | `verified` |
| 腾讯(qt.gtimg) · `[26]` | [26] | 卖四档委托数量 | 手 | `verified` |

### `[27]` — ambiguous

聚合问题：meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[27]` | [27] | 近 5 根K线涨跌幅 (%) | — | `verified` |
| 新浪(hq.sinajs) · `[27]` | [27] | 卖四价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[27]` | [27] | 卖五价 | 元 | `verified` |

### `[28]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[28]` | [28] | 近 5 日涨跌幅 (%) | — | `verified` |
| 新浪(hq.sinajs) · `[28]` | [28] | 卖五档委托数量 | 股 | `verified` |
| 腾讯(qt.gtimg) · `[28]` | [28] | 卖五档委托数量 | 手 | `verified` |

### `[29]` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[29]` | [29] | 近 10 根K线涨跌幅 (%) | — | `verified` |
| 新浪(hq.sinajs) · `[29]` | [29] | 卖五价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[29]` | — | 最近逐笔成交 | - | `unverified` |

### `[2]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[2]` | [2] | BetaValue（Beta 系数） | — | `verified` |
| ZHB-tdxstat2 · `[2]` | [2] | 数据日期 | YYYYMMDD | `verified` |
| ZHB-tipinfo · `[2]` | [2] | 财报报告期截止日 | YYYYMMDD | `verified` |
| 新浪(hq.sinajs) · `[2]` | [2] | 昨收盘 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[2]` | [2] | 股票代码 | - | `verified` |

### `[30]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[30]` | [30] | 近 10 日涨跌幅 (%) | — | `verified` |
| 新浪(hq.sinajs) · `[30]` | [30] | 日期 | YYYY-MM-DD | `verified` |
| 腾讯(qt.gtimg) · `[30]` | [30] | 时间戳 | YYYYMMDDHHMMSS | `verified` |

### `[31]` — ambiguous

聚合问题：meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[31]` | [31] | “几天几板”统计中的天数（通达信 LastStartZT，官方接口说明为“几天”；精确窗口边界未公开） | 天 | `verified` |
| 新浪(hq.sinajs) · `[31]` | [31] | 时间 | HH:MM:SS | `verified` |
| 腾讯(qt.gtimg) · `[31]` | [31] | 涨跌额 | 元 | `verified` |

### `[32]` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[32]` | [32] | “几天几板”统计中的涨停板数（通达信 LastZTHzNum，官方接口说明为“几板”；精确统计口径未公开） | 板 | `verified` |
| 新浪(hq.sinajs) · `[32]` | quote_trading_status_code | 新浪实时行情交易状态码。本次保留样本中 00 表示常规交易状态（439/439 条均有正成交量）；03 表示停牌（唯一样本与发行人停牌公告、独立行情标记一致）。只确认已观察的 00、03，不外推未观察代码。 | - | `verified` |
| 腾讯(qt.gtimg) · `[32]` | [32] | 涨跌幅 | % | `verified` |

### `[33]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[33]` | [33] | 连板数 | — | `verified` |
| 新浪(hq.sinajs) · `[33]` | [33] | 逐笔成交串 | - | `verified` |
| 腾讯(qt.gtimg) · `[33]` | [33] | 最高价 | 元 | `verified` |

### `[34]` — ambiguous

聚合问题：meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[34]` | [34] | 其他权益工具（万元） | 万元 | `verified` |
| 腾讯(qt.gtimg) · `[34]` | [34] | 最低价 | 元 | `verified` |

### `[3]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[3]` | [3] | 市盈率（TTM） | — | `verified` |
| ZHB-tdxstat2 · `[3]` | [3] | T 日总成交额 | 万元 | `verified` |
| ZHB-tipinfo · `[3]` | [3] | 报告期累计每股收益（基本/稀释/扣非口径未区分） | 元/股 | `verified` |
| 新浪(hq.sinajs) · `[3]` | [3] | 现价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[3]` | [3] | 现价 | 元 | `verified` |

### `[4]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[4]` | [4] | 数据快照日期 | — | `verified` |
| ZHB-tdxstat2 · `[4]` | [4] | 当日涨跌停封单额（涨停为正，跌停为负） | 万元 | `verified` |
| ZHB-tipinfo · `[4]` | [4] | 财报预约披露日 | YYYYMMDD | `verified` |
| 新浪(hq.sinajs) · `[4]` | [4] | 最高价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[4]` | [4] | 昨收盘 | 元 | `verified` |

### `[58]` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 新浪(hq.sinajs) · `[58]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[58]` | [58] | 最新逐笔成交金额 | 万元 | `verified` |

### `[59]` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 新浪(hq.sinajs) · `[59]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[59]` | [59] | 最新逐笔成交量 | 手 | `verified` |

### `[5]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[5]` | [5] | 连涨/连跌天数 | — | `verified` |
| ZHB-tdxstat2 · `[5]` | [5] | 昨日成交额 | 万元 | `verified` |
| ZHB-tipinfo · `[5]` | [5] | 近2年最近涨停板日期 = TDX 官方 ZTDate_Recent | YYYYMMDD | `verified` |
| 新浪(hq.sinajs) · `[5]` | [5] | 最低价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[5]` | [5] | 开盘价 | 元 | `verified` |

### `[6]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[6]` | [6] | T 日涨跌幅 (%) | — | `verified` |
| ZHB-tdxstat2 · `[6]` | [6] | 前一交易日涨跌停封单额（涨停为正，跌停为负） | 万元 | `verified` |
| ZHB-tipinfo · `[6]` | [6] | 近 2 年最近龙虎榜日期（通达信 TopDate_Recent） | — | `verified` |
| 新浪(hq.sinajs) · `[6]` | [6] | 买一价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[6]` | [6] | 成交量 | 手 | `verified` |

### `[7]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[7]` | [7] | T-1 日涨跌幅 (%) | — | `verified` |
| ZHB-tdxstat2 · `[7]` | [7] | 前日成交额 | 万元 | `verified` |
| ZHB-tipinfo · `[7]` | [7] | 重大事项停牌起始日 | — | `verified` |
| 新浪(hq.sinajs) · `[7]` | [7] | 卖一价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[7]` | [7] | 外盘成交量 | 手 | `verified` |

### `[8]` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[8]` | [8] | T-2 日涨跌幅 (%) | — | `verified` |
| ZHB-tdxstat2 · `[8]` | [8] | 前第二交易日涨跌停封单额（涨停为正，跌停为负） | 万元 | `verified` |
| ZHB-tipinfo · `[8]` | tipinfo.shareholder_change_date | 股东持股变动记录关联日期；可为交易日、区间截止日或权益变动协议签署日 | YYYYMMDD | `verified` |
| 新浪(hq.sinajs) · `[8]` | [8] | 成交量 | 股 | `verified` |
| 腾讯(qt.gtimg) · `[8]` | [8] | 内盘成交量 | 手 | `verified` |

### `[9]` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[9]` | [9] | 市盈率（静态/LYR） | — | `verified` |
| ZHB-tdxstat2 · `[9]` | [9] | 当日开盘集合竞价成交量 | 手 | `verified` |
| ZHB-tipinfo · `[9]` | tipinfo.shareholder_change_shares_wan | 股东持股变动数量；正值为增持/转入，负值为减持/转出 | 万股 | `verified` |
| 新浪(hq.sinajs) · `[9]` | [9] | 成交额 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[9]` | [9]-[18] | 买一~买五 价/量 | 元/手 | `verified` |

### `amount` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `amount` | amount | 成交额 | 元 | `verified` |
| TDX-eltdx(适配层) · `amount` | amount | 实时行情快照截至该时点的累计成交额；收盘样本与同一数据日 K 线成交额一致。 | 元 | `verified` |
| ZHB-tdxstat2 · `amount` | amount | T日总成交额 | 万元 | `verified` |
| reports · `amount` | amount | 成交额 | — | `verified` |
| 东财-datacenter(英文键) · `amount` | block_trade.amount | 旧未限定短路径已退役。get_block_trade 的成交金额输出，单位元。 完整路径：block_trade.amount。多目标别名只用于说明路径拆分，不表示这些字段同义。 | — | `disproved` |
| 东财-push2ex · `amount` | amount | 成交额 | 元 | `verified` |
| 市场源(market_sources) · `amount` | amount | 成交额 | — | `verified` |
| 开盘啦(kpl) · `amount` | amount | 成交额 | 元 | `unverified` |
| 开盘啦(kpl_limit_up_detail) · `amount` | amount | 成交额；与 KPH turnover 两日逐值一致 | 元 | `verified` |

### `amount_1d` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `amount_1d` | amount_1d | 旧版 tdx_get_quote_full() 返回键；2026-10-15 只见于 quote_full.amount_1d，20/20 同股值与 ZHB stat2.amount_1d 和合并对象 full.amount_1d 精确相同；同股 quote_raw 不含该键。当前 TDX 专用采集改用 tdx_get_quote_raw()，本审计仅撤销该历史样本对 TDX 原始字段归属的支持，不裁定业务语义；未来 raw 若出现该键须重新审查。 | — | `disproved` |
| ZHB-tdxstat2 · `amount_1d` | amount_1d | 前一交易日总成交额 | 万元 | `verified` |
| 同花顺-fuyao · `amount_1d` | — | — | — | `unverified` |

### `amount_2d` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `amount_2d` | amount_2d | 旧版 tdx_get_quote_full() 返回键；2026-10-15 只见于 quote_full.amount_2d，20/20 同股值与 ZHB stat2.amount_2d 和合并对象 full.amount_2d 精确相同；同股 quote_raw 不含该键。当前 TDX 专用采集改用 tdx_get_quote_raw()，本审计仅撤销该历史样本对 TDX 原始字段归属的支持，不裁定业务语义；未来 raw 若出现该键须重新审查。 | — | `disproved` |
| ZHB-tdxstat2 · `amount_2d` | amount_2d | 前第二交易日总成交额 | 万元 | `verified` |
| 同花顺-fuyao · `amount_2d` | — | — | — | `unverified` |

### `amplitude` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `amplitude` | amplitude | 价格振幅 | — | `verified` |
| 同花顺-fuyao · `amplitude` | — | — | — | `unverified` |
| 市场源(market_sources) · `amplitude` | — | — | — | `unverified` |
| 开盘啦(kpl) · `amplitude` | amplitude | 振幅% | % | `unverified` |
| 开盘啦(kpl_limit_up_detail) · `amplitude` | amplitude | 当日振幅=(当日最高价-最低价)/前一交易日收盘价×100% | % | `verified` |

### `ask1` — ambiguous

聚合问题：meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `ask1` | ask1 | 卖一价 | 元 | `verified` |
| TDX-eltdx(适配层) · `ask1` | ask1 | 卖一价格 | — | `verified` |

### `bid` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 开盘啦(kpl) · `bid` | — | — | — | `unverified` |
| 新浪(扩展API) · `bid` | bid_vol/bid/last/ask/ask_vol | 五档价量 | — | `unverified` |

### `bid1` — ambiguous

聚合问题：meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `bid1` | bid1 | 买一价 | 元 | `verified` |
| TDX-eltdx(适配层) · `bid1` | bid1 | 买一价格 | — | `verified` |

### `brief` — ambiguous

聚合问题：canonical_differs；meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `brief` | brief | 摘要 | — | `verified` |
| 财联社(cls) · `brief` | title / brief | 标题 / 摘要 | — | `verified` |

### `change` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `change` | change | 价格涨跌额 | 元/股 | `verified` |
| TDX(双命名源) · `change` | change | 涨跌额，按最新价减前收盘价计算（AxData TDX 快照模型语义，不证明当前项目采集路径） | — | `verified` |
| 同花顺-fuyao · `change` | change | 当日涨跌幅，小数形式。 | 比例（小数） | `verified` |

### `change_pct` — ambiguous

聚合问题：meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `change_pct` | change_pct | 涨跌幅，按（最新价－前收盘价）÷前收盘价×100 计算（AxData TDX 快照模型语义，不证明当前项目采集路径） | % | `verified` |
| TDX-eltdx(适配层) · `change_pct` | change_pct | 涨跌幅 | % | `verified` |
| ZHB-tdxstat · `change_pct` | change_pct | 当日涨跌幅 | % | `verified` |
| 东财-push2ex · `change_pct` | change_pct | 当日涨跌幅（百分比）；接口原始值保留比 KPL col_22 更多的小数位，三个有效日期 271 组对照均在 0.02 个百分点内，按两位小数四舍五入后相等。 | % | `verified` |
| 市场源(market_sources) · `change_pct` | change_pct | 涨跌幅 | — | `verified` |
| 开盘啦(kpl) · `change_pct` | change_pct | 涨跌幅% | % | `unverified` |

### `change_pct_1d` — ambiguous

聚合问题：meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `change_pct_1d` | change_pct_1d | 旧版 tdx_get_quote_full() 返回键；2026-10-15 只见于 quote_full.change_pct_1d，20/20 同股值与 ZHB stat.change_pct_1d 和合并对象 full.change_pct_1d 精确相同；同股 quote_raw 不含该键。当前 TDX 专用采集改用 tdx_get_quote_raw()，本审计仅撤销该历史样本对 TDX 原始字段归属的支持，不裁定业务语义；未来 raw 若出现该键须重新审查。 | — | `disproved` |
| ZHB-tdxstat · `change_pct_1d` | change_pct_1d | T-1 日涨跌幅 | % | `verified` |

### `change_pct_2d` — ambiguous

聚合问题：meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `change_pct_2d` | change_pct_2d | 旧版 tdx_get_quote_full() 返回键；2026-10-15 只见于 quote_full.change_pct_2d，20/20 同股值与 ZHB stat.change_pct_2d 和合并对象 full.change_pct_2d 精确相同；同股 quote_raw 不含该键。当前 TDX 专用采集改用 tdx_get_quote_raw()，本审计仅撤销该历史样本对 TDX 原始字段归属的支持，不裁定业务语义；未来 raw 若出现该键须重新审查。 | — | `disproved` |
| ZHB-tdxstat · `change_pct_2d` | change_pct_2d | T-2 日涨跌幅 | % | `verified` |

### `change_rate` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `change_rate` | change_rate | 日涨跌幅；0.03 表示 3% | 比率 | `verified` |
| 东财-热榜(em_hot) · `change_rate` | latest / change_rate | 现价 / 涨跌幅 | — | `verified` |

### `close` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `close` | close | 收盘价/最新价 | 元/股 | `verified` |
| TDX-eltdx(适配层) · `close` | close | 日K收盘价 | 元 | `verified` |
| 东财-datacenter(英文键) · `close` | block_trade.close | 旧未限定短路径已退役。get_block_trade 的对应证券收盘价输出。 完整路径：block_trade.close。多目标别名只用于说明路径拆分，不表示这些字段同义。 | — | `disproved` |
| 东财-热榜(em_hot) · `close` | close / zhangdie | 收盘价 / 涨跌额 | — | `verified` |
| 新浪(扩展API) · `close` | — | — | — | `unverified` |

### `code` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `code` | code | 股票代码 | 6位字符串 | `verified` |
| TDX-eltdx(适配层) · `code` | shortline.code | 已退役的未限定旧路径身份 | — | `disproved` |
| ZHB-tdxstat · `code` | code | 代码 | - | `verified` |
| ZHB-tdxstat2 · `code` | code | 代码 | - | `verified` |
| ZHB-tipinfo · `code` | code | 股票代码 | 6位字符串 | `verified` |
| 东财-push2ex · `code` | stock_code | 六位 A 股证券代码字符串，对应东方财富官方涨停股池“代码”列。 | — | `verified` |
| 东财-热榜(em_hot) · `code` | — | — | — | `verified` |
| 巨潮(cninfo) · `code` | code | 问答所属的六位股票代码 | 6位字符串 | `verified` |
| 市场源(market_sources) · `code` | code | 股票代码 | — | `verified` |
| 开盘啦(kpl) · `code` | code | 股票代码 | — | `unverified` |
| 财联社(cls) · `code` | — | — | — | `unverified` |

### `color` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `color` | color | 待破解 | — | `unverified` |
| 开盘啦(kpl) · `color` | — | — | — | `unverified` |

### `content` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 开盘啦(kpl) · `content` | — | — | — | `unverified` |
| 财联社(cls) · `content` | content | 正文 | — | `verified` |

### `count` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `count` | count | 该股近 30 日滚动研报发布总篇数 | — | `verified` |
| 市场源(market_sources) · `count` | — | — | — | `unverified` |

### `date` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `date` | event_date | TDX XDXR（0x000f）权息/股本变迁事件日期；不是采集日期。现有契约未进一步区分公告日、股权登记日或除权除息日。 | - | `verified` |
| ZHB-tdxstat · `date` | date | 统计日期 | - | `verified` |
| ZHB-tdxstat2 · `date` | date | 统计日期 | - | `verified` |
| 东财-datacenter(英文键) · `date` | date_legacy_flat_alias | 旧未限定短路径已退役。旧扁平日期短名混合交易日、持仓日、解禁事件日、股东报告截止日和旧分红事件日；不再作为单一字段身份。 完整路径：margin_trading.date; northbound_hold.date; lockup_expiry.date; block_trade.date; holder_fetch_em.date; EX_DIVIDEND_DATE。多目标别名只用于说明路径拆分，不表示这些字段同义。 | — | `disproved` |
| 同花顺-fuyao · `date` | — | — | — | `unverified` |
| 央视网(新闻联播) · `date` | cctv_news_broadcast_edition_date | 央视网《新闻联播》按日栏目页所对应的节目期次日期。它不表示单条新闻的事件日、单条报道的独立发布时间或本次采集日。 | YYYY-MM-DD | `verified` |
| 巨潮(cninfo) · `date` | — | — | — | `unverified` |
| 市场源(market_sources) · `date` | date | 日期 | — | `verified` |
| 开盘啦(kpl) · `date` | — | — | — | `unverified` |
| 新浪(扩展API) · `date` | — | — | — | `unverified` |
| 新浪(研报列表) · `date` | sina_research_report_publication_date | 新浪财经机构研报列表记录中标为“发布日期”的日期。它表示研报发布日期，不等同于财报报告期、报告正文所述事件日或本次列表响应的更新时间。 | 日期 | `verified` |

### `encodeUrl` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `encodeUrl` | encodeUrl | — | — | `conflict` |

### `eps` — ambiguous

聚合问题：canonical_differs；meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `eps` | eps_raw | 每股收益原始值（上游契约及现有可区分样本未确认基本/稀释子口径、报告期选择规则或小数精度/舍入规则） | 元/股 | `verified` |
| ZHB-tipinfo · `eps` | eps | 报告期累计每股收益（基本/稀释/扣非口径未区分） | 元/股 | `verified` |

### `eps_raw` — ambiguous

聚合问题：meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `eps_raw` | eps_raw | 每股收益原始值 | 元/股 | `verified` |
| TDX-eltdx(适配层) · `eps_raw` | eps_raw | 每股收益原始值；样本对应最近已披露报告期的年初至报告期末累计值，接口未区分基本与稀释口径 | 元/股 | `verified` |

### `exchange` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `exchange` | shortline.exchange | 已退役的未限定旧路径身份 | — | `disproved` |
| 同花顺-fuyao · `exchange` | — | — | — | `unverified` |

### `f1` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f1` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f1` | quote_price_precision_digits | 该证券实时行情报价的显示小数位数；在 fltt=1 响应中用于将价格整数还原为 fltt=2 报价。 | 位（小数位数） | `verified` |

### `f10` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f10` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f10` | f10 | — | — | `verified` |

### `f100` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f100` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f100` | f100 | 所属行业名称 | — | `verified` |

### `f102` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f102` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f102` | f102 | 所属地域板块 | — | `verified` |

### `f103` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f103` | ocf_ttm(f103) | 经营活动现金流量净额 TTM：上年全年 + 本年最新报告期年初至今 − 上年同期年初至今；合并现金流口径。 | 元 | `verified` |
| 东财-ulist239(np/get) · `f103` | f103 | 所属概念列表 | — | `verified` |

### `f104` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f104` | f104 / f105 | 上涨 / 下跌家数 | — | `verified` |
| 东财-push2(stock/get) · `f104` | — | 营业总收入 TTM | 元 | `verified` |
| 东财-ulist239(np/get) · `f104` | f104 | — | — | `unverified` |

### `f105` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f105` | f104 / f105 | 上涨 / 下跌家数 | — | `verified` |
| 东财-push2(stock/get) · `f105` | — | 归母净利润 最新报告期 | 元 | `verified` |
| 东财-ulist239(np/get) · `f105` | f105 | — | — | `unverified` |

### `f106` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f106` | f106 | 待破解 | - | `unverified` |
| 东财-ulist239(np/get) · `f106` | f106 | — | — | `unverified` |

### `f107` — incomplete

聚合问题：meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f107` | f107 | 市场标记（布尔 0/1，北交=0） | - | `verified` |
| 东财-ulist239(np/get) · `f107` | f107 | — | — | `unverified` |

### `f108` — ambiguous

聚合问题：canonical_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f108` | eps_ttm(f108) | 归母净利润 TTM 按当前总股本折算的每股收益；TTM 归母净利润 = 上年度全年归母净利润 + 本年度最新报告期年初至今归母净利润 - 上年度同期年初至今归母净利润，分母为 Push2 f84 当前总股本。不是扣非 EPS，也不推断法定基本/稀释 EPS 的加权平均股数口径。 | 元/股 | `verified` |
| 东财-ulist239(np/get) · `f108` | f108 | — | — | `unverified` |

### `f109` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f109` | f109 / f160 | 涨跌幅 | % | `verified` |
| 东财-push2(stock/get) · `f109` | net_profit_annual(f109) | 归母净利润 最新年报 | 元 | `verified` |
| 东财-ulist239(np/get) · `f109` | change_5d | 5日涨跌幅 | % | `verified` |

### `f110` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f110` | f110 | 市场标记（布尔 0/1，北交=0） | - | `verified` |
| 东财-ulist239(np/get) · `f110` | change_20d | 20日涨跌幅 | % | `verified` |

### `f111` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f111` | f111 | 板级枚举 | - | `verified` |
| 东财-ulist239(np/get) · `f111` | registration_system_listing_bitmask | 东方财富 ulist.np/get 返回的证券上市制度标记位掩码。保留样本支持 bit17（131072）表示注册制试点/注册制板块上市批次，bit19（524288）表示注册制改革前进入当前上市板块的存量批次。该定义描述 Eastmoney 当前证券分类中的上市批次标记，不等同于发行人最早一次公开发行所经历的审批方式；920508 殷图网联先在新三板精选层挂牌、后平移至北交所，是此边界的实例。bit10、bit21、bit3、bit6、bit11、bit18 等其他观察位含义未定。未观察 2023-04 全面注册制后沪深主板新 IPO，不外推 bit17 在该类证券中的编码。 | — | `verified` |

### `f112` — ambiguous

聚合问题：meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f112` | f112 | 板级枚举 | - | `verified` |
| 东财-ulist239(np/get) · `f112` | f112 | 每股收益 EPS | — | `verified` |

### `f113` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f113` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f113` | f113 | 每股净资产 BPS | — | `verified` |

### `f114` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f114` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f114` | f114 | 市盈率(静态/年报 LYR) | — | `verified` |

### `f115` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f115` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f115` | f115 | 市盈率（TTM） | — | `verified` |

### `f116` — incomplete

聚合问题：meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f116` | f116 | 总市值 | 元 | `verified` |
| 东财-ulist239(np/get) · `f116` | f116 | — | — | `unverified` |

### `f117` — incomplete

聚合问题：meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f117` | f117 | 流通市值 | 元 | `verified` |
| 东财-ulist239(np/get) · `f117` | f117 | — | — | `unverified` |

### `f118` — incomplete

聚合问题：meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f118` | f118 | 市场/板块状态标记（≡ ulist:f107） | - | `verified` |
| 东财-ulist239(np/get) · `f118` | f118 | — | — | `unverified` |

### `f119` — incomplete

聚合问题：meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f119` | f119 | — | — | `verified` |
| 东财-ulist239(np/get) · `f119` | f119 | — | — | `unverified` |

### `f12` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f12` | f12 | 板块代码 | — | `verified` |
| 东财-push2(stock/get) · `f12` | — | — | — | `unverified` |
| 东财-slist · `f12` | f12 | BK 板块代码 | — | `verified` |
| 东财-ulist239(np/get) · `f12` | f12 | 股票代码 | - | `verified` |

### `f120` — incomplete

聚合问题：meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f120` | f120 | — | — | `verified` |
| 东财-ulist239(np/get) · `f120` | f120 | — | — | `unverified` |

### `f121` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f121` | f121 | 资金流衍生指标 | - | `verified` |
| 东财-ulist239(np/get) · `f121` | — | — | — | `unverified` |

### `f122` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f122` | f122 | 年初至今涨跌幅(%)（YTD, 前复权） | % | `verified` |
| 东财-ulist239(np/get) · `f122` | — | — | — | `unverified` |

### `f123` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f123` | f123 | — | — | `unverified` |
| 东财-ulist239(np/get) · `f123` | f123 | — | — | `unverified` |

### `f124` — incomplete

聚合问题：meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f124` | f124 | — | — | `unverified` |
| 东财-ulist239(np/get) · `f124` | f124 | 行情更新时间戳 | Unix 秒 | `verified` |

### `f125` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f125` | f125 | — | — | `unverified` |
| 东财-ulist239(np/get) · `f125` | f125 | — | — | `unverified` |

### `f126` — ambiguous

聚合问题：canonical_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f126` | eastmoney_stock_get_dividend_yield | 东方财富分红融资页定义的股息率：经调整后的最近四个季度分红总额相对于最近一个交易日总市值 | % | `verified` |
| 东财-ulist239(np/get) · `f126` | f126 | — | — | `unverified` |

### `f127` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f127` | f127 | 行业名称 | - | `verified` |
| 东财-ulist239(np/get) · `f127` | change_3d | 3日涨跌幅 | % | `verified` |

### `f128` — ambiguous

聚合问题：meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f128` | f128 | 板块领涨股名称 | - | `verified` |
| 东财-push2(stock/get) · `f128` | f128 | 地域板块名称 | - | `verified` |
| 东财-slist · `f128` | f128 | 板块龙头股名 | — | `verified` |
| 东财-ulist239(np/get) · `f128` | f128 | — | — | `unverified` |

### `f129` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f129` | eastmoney_quote_concept_theme_labels | 逗号分隔的个股概念 / 题材标签列表；是 `stock/get` 路径含义，不套用 `ulist239::f129` 的净利率释义。 | 逗号分隔文本（解析后为字符串数组） | `verified` |
| 东财-ulist239(np/get) · `f129` | f129 | 净利率 | — | `verified` |

### `f13` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f13` | — | — | — | `unverified` |
| 东财-push2(stock/get) · `f13` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f13` | f13 | 市场标志：本项目 A 股样本中沪市=1，非沪市=0（含深市、北交）；保留期样本与 f27 同值。 | — | `verified` |

### `f130` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f130` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f130` | f130 | 毛利率 | — | `verified` |

### `f131` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f131` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f131` | f131 | 市现率 PCF_TTM（总市值 / 经营现金流 TTM） | 倍 | `verified` |

### `f132` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f132` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f132` | f132 | 总资产 | — | `verified` |

### `f133` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f133` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f133` | dividend_yield_lfy_observed | 股息率（%）；在本次保留的善水科技、万华化学、贵州茅台样本中，数值符合最近已实施完整年度现金分红/当日价格的 LFY-like 口径。东方财富整体算法会按分红期切换 TTM/LFY 并可含预案；特别股利及切换条件未由本字段样本充分确认。 | % | `verified` |

### `f134` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f134` | f134 | — | — | `unverified` |
| 东财-ulist239(np/get) · `f134` | f134 | — | — | `unverified` |

### `f135` — ambiguous

聚合问题：canonical_differs；meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f135` | fund_main_buy | 东方财富个股资金流分类口径下，当日主力类别买入金额；留存可比较样本均满足 f135 = 超大单买入 f138 + 大单买入 f141。该值描述东方财富分类结果，不代表特定账户或真实机构身份。 | 元 | `verified` |
| 东财-ulist239(np/get) · `f135` | ulist239_total_equity_consolidated | 所有者权益合计（合并口径，含少数股东权益） | 元 | `verified` |
| 东财-资金流(em_fund_flow) · `f135` | fund_main_buy | 东方财富个股资金流分类口径下，当日主力类别买入金额；留存可比较样本均满足 f135 = 超大单买入 f138 + 大单买入 f141。该值描述东方财富分类结果，不代表特定账户或真实机构身份。 | 元 | `verified` |

### `f136` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f136` | f136 | 板块领涨股涨跌幅 | % | `verified` |
| 东财-push2(stock/get) · `f136` | fund_main_sell | 东方财富个股资金流分类口径下，当日主力类别卖出金额；留存可比较样本均满足 f136 = 超大单卖出 f139 + 大单卖出 f142。该值描述东方财富分类结果，不代表特定账户或真实机构身份。 | 元 | `verified` |
| 东财-ulist239(np/get) · `f136` | — | — | — | `unverified` |
| 东财-资金流(em_fund_flow) · `f136` | fund_main_sell | 东方财富个股资金流分类口径下，当日主力类别卖出金额；留存可比较样本均满足 f136 = 超大单卖出 f139 + 大单卖出 f142。该值描述东方财富分类结果，不代表特定账户或真实机构身份。 | 元 | `verified` |

### `f137` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f137` | fund_main_today | 主力资金净流入金额（当日）；与超大单和大单净流入之和一致，不表示投资者账户身份。 | 元 | `verified` |
| 东财-ulist239(np/get) · `f137` | — | — | — | `conflict` |
| 东财-资金流(em_fund_flow) · `f137` | fund_main_today | 主力资金净流入金额（当日）；与超大单和大单净流入之和一致，不表示投资者账户身份。 | 元 | `verified` |

### `f138` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f138` | fund_super_buy | 东方财富“超大单”类别资金流入金额（当日，按该页面的资金流分类口径；不代表账户身份）。 | 元 | `verified` |
| 东财-ulist239(np/get) · `f138` | — | — | — | `unverified` |
| 东财-资金流(em_fund_flow) · `f138` | fund_super_buy | 东方财富“超大单”类别资金流入金额（当日，按该页面的资金流分类口径；不代表账户身份）。 | 元 | `verified` |

### `f139` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f139` | fund_super_sell | 东方财富“超大单”类别资金流出金额（当日，按该页面的资金流分类口径；不代表账户身份）。 | 元 | `verified` |
| 东财-ulist239(np/get) · `f139` | listing_board_type | 证券上市板块类型代码；本次日期合格 A 股样本中 2=主板、5=创业板、32=科创板、80=北交所。仅确认四种已观测枚举，不声称完整码表；该值不代表交易所市场号。 | - | `verified` |
| 东财-资金流(em_fund_flow) · `f139` | fund_super_sell | 东方财富“超大单”类别资金流出金额（当日，按该页面的资金流分类口径；不代表账户身份）。 | 元 | `verified` |

### `f14` — ambiguous

聚合问题：meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f14` | f14 | 板块名称 | — | `verified` |
| 东财-slist · `f14` | f14 | 板块名称 | — | `verified` |
| 东财-ulist239(np/get) · `f14` | f14 | 股票名称 | - | `verified` |

### `f140` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f140` | f140 | 板块领涨股代码 | - | `verified` |
| 东财-push2(stock/get) · `f140` | fund_super_today | 东方财富“超大单”类别资金净流入金额（当日；不表示账户身份）。 | 元 | `verified` |
| 东财-slist · `f140` | f140 | 板块龙头股代码 | — | `verified` |
| 东财-ulist239(np/get) · `f140` | — | — | — | `conflict` |
| 东财-资金流(em_fund_flow) · `f140` | fund_super_today | 东方财富“超大单”类别资金净流入金额（当日；不表示账户身份）。 | 元 | `verified` |

### `f141` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f141` | clist_leader_stock_market_id | 领涨股票的市场编号；与 f140 股票代码组合成东方财富 unify/r/{market}.{code} 行情路由。 | 市场编号 | `verified` |
| 东财-push2(stock/get) · `f141` | fund_large_buy | 东方财富“大单”类别资金流入金额（当日，按该页面的资金流分类口径；不代表账户身份）。 | 元 | `verified` |
| 东财-ulist239(np/get) · `f141` | — | — | — | `conflict` |
| 东财-资金流(em_fund_flow) · `f141` | fund_large_buy | 东方财富“大单”类别资金流入金额（当日，按该页面的资金流分类口径；不代表账户身份）。 | 元 | `verified` |

### `f142` — ambiguous

聚合问题：canonical_differs；meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f142` | fund_large_sell | 东方财富个股资金流分类口径下，当日大单类别卖出金额；由大单买入 f141 减大单净流入 f143 反推，并经留存可比较样本逐项复算。该值描述东方财富分类结果，不代表特定账户或真实机构身份。 | 元 | `verified` |
| 东财-ulist239(np/get) · `f142` | f142 | 买二价 | 元 | `verified` |
| 东财-资金流(em_fund_flow) · `f142` | fund_large_sell | 东方财富个股资金流分类口径下，当日大单类别卖出金额；由大单买入 f141 减大单净流入 f143 反推，并经留存可比较样本逐项复算。该值描述东方财富分类结果，不代表特定账户或真实机构身份。 | 元 | `verified` |

### `f143` — ambiguous

聚合问题：canonical_differs；meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f143` | fund_large_today | 东方财富个股资金流历史表“大单净流入/净额”对应的当日金额；按东方财富资金分类口径解释，不代表特定账户或真实机构身份。 | 元 | `verified` |
| 东财-ulist239(np/get) · `f143` | f143 | 卖二价 | 元 | `verified` |
| 东财-资金流(em_fund_flow) · `f143` | fund_large_today | 东方财富个股资金流历史表“大单净流入/净额”对应的当日金额；按东方财富资金分类口径解释，不代表特定账户或真实机构身份。 | 元 | `verified` |

### `f144` — ambiguous

聚合问题：canonical_differs；meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f144` | fund_mid_buy | 东方财富个股资金流分类口径下，当日中单类别流入/买入金额；此分类不表示投资者账户身份。 | 元 | `verified` |
| 东财-ulist239(np/get) · `f144` | f144 | 最新价/现价 | 元 | `verified` |
| 东财-资金流(em_fund_flow) · `f144` | fund_mid_buy | 东方财富个股资金流分类口径下，当日中单类别流入/买入金额；此分类不表示投资者账户身份。 | 元 | `verified` |

### `f145` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f145` | fund_mid_sell | 东方财富个股资金流分类口径下，当日中单类别流出/卖出金额；此分类不表示投资者账户身份。 | 元 | `verified` |
| 东财-ulist239(np/get) · `f145` | — | — | — | `conflict` |
| 东财-资金流(em_fund_flow) · `f145` | fund_mid_sell | 东方财富个股资金流分类口径下，当日中单类别流出/卖出金额；此分类不表示投资者账户身份。 | 元 | `verified` |

### `f146` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f146` | fund_mid_today | 东方财富个股资金流分类口径下，当日中单净流入金额，等于中单流入减中单流出；此分类不表示投资者账户身份。 | 元 | `verified` |
| 东财-ulist239(np/get) · `f146` | f146 | 所属行业领涨股代码 | - | `verified` |
| 东财-资金流(em_fund_flow) · `f146` | fund_mid_today | 东方财富个股资金流分类口径下，当日中单净流入金额，等于中单流入减中单流出；此分类不表示投资者账户身份。 | 元 | `verified` |

### `f147` — ambiguous

聚合问题：canonical_differs；meaning_differs；meaning_incomplete；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f147` | fund_small_buy | 小单类别的资金流入金额，不表示投资者账户身份 | 元 | `verified` |
| 东财-ulist239(np/get) · `f147` | f147 | — | — | `verified` |
| 东财-资金流(em_fund_flow) · `f147` | fund_small_buy | 小单类别的资金流入金额，不表示投资者账户身份。 | 元 | `verified` |

### `f148` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f148` | fund_small_sell | 小单类别的资金流出金额，不表示投资者账户身份 | 元 | `verified` |
| 东财-ulist239(np/get) · `f148` | security_eligibility_bitmask | 东方财富 ulist.np/get 返回的证券资格标志位掩码。当前证据确认 bit6（64）表示交易所融资融券标的资格，bit9（512）表示沪股通下一北向交易日可买可卖资格，bit10（1024）表示深股通下一北向交易日可买可卖资格。bit0 与未观察到的其他位含义未定；这些资格标记不代表特定券商或投资者账户的实际可交易性。 | — | `verified` |
| 东财-资金流(em_fund_flow) · `f148` | fund_small_sell | 小单类别的资金流出金额，不表示投资者账户身份。 | 元 | `verified` |

### `f149` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f149` | fund_small_today | 小单类别资金净流入金额，等于流入金额减流出金额 | 元 | `verified` |
| 东财-ulist239(np/get) · `f149` | ulist239_change_6_intervals_pct | 相对前第六个交易日收盘价的累计涨跌幅（六个交易间隔）；观测值以百分数表示。 | % | `verified` |
| 东财-资金流(em_fund_flow) · `f149` | fund_small_today | 小单类别资金净流入金额，等于流入金额减流出金额。 | 元 | `verified` |

### `f15` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f15` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f15` | f15 | 最高价 | 元 | `verified` |

### `f152` — ambiguous

聚合问题：canonical_differs；meaning_incomplete；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f152` | f152 | — | — | `candidate` |
| 东财-ulist239(np/get) · `f152` | 行情百分比/比例缩放位数 | 东方财富官方行情中心把 f152 作为多个涨跌幅、涨速和比例字段的十进制缩放/显示精度参数，而非该指标的数值本身。官方 fltt=1 前端格式器按 e / 10^f152 还原并显示 f152 位；项目采集使用 fltt=2，已转换行情数值不得再次缩放。 | — | `verified` |

### `f153` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f153` | f153 | — | — | `unverified` |
| 东财-ulist239(np/get) · `f153` | f153 | — | — | `unverified` |

### `f154` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f154` | f154 | — | — | `unverified` |
| 东财-ulist239(np/get) · `f154` | f154 | — | — | `unverified` |

### `f160` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f160` | f109 / f160 | 涨跌幅 | % | `verified` |
| 东财-push2(stock/get) · `f160` | eps_annual(f160) | 上年度归母净利润按最新总股本折算的每股金额（不同于年报披露基本每股收益） | 元/股 | `verified` |
| 东财-ulist239(np/get) · `f160` | change_10d | 10日涨跌幅 | % | `verified` |

### `f161` — ambiguous

聚合问题：canonical_differs；meaning_incomplete；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f161` | eastmoney_stock_get_inner_volume | 内盘成交量 | 手 | `verified` |
| 东财-ulist239(np/get) · `f161` | f161 | — | — | `verified` |

### `f162` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f162` | f162 | — | — | `verified` |
| 东财-ulist239(np/get) · `f162` | f162 | — | — | `verified` |
| 开盘啦(kpl) · `f162` | — | — | — | `unverified` |

### `f163` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f163` | f163 | 静态市盈率（总市值/上年度净利润） | 倍 | `verified` |
| 东财-ulist239(np/get) · `f163` | f163 | — | — | `verified` |
| 开盘啦(kpl) · `f163` | — | — | — | `unverified` |

### `f164` — ambiguous

聚合问题：canonical_differs；meaning_incomplete；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f164` | f164 / f165 | 主力净额 | 元/% | `verified` |
| 东财-push2(stock/get) · `f164` | f164 | — | — | `verified` |
| 东财-ulist239(np/get) · `f164` | f164 | — | — | `verified` |

### `f165` — ambiguous

聚合问题：canonical_differs；meaning_incomplete；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f165` | f164 / f165 | 主力净额 | 元/% | `verified` |
| 东财-push2(stock/get) · `f165` | f165 | — | — | `verified` |
| 东财-ulist239(np/get) · `f165` | f165 | — | — | `verified` |

### `f166` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f166` | f166 | — | — | `verified` |
| 东财-ulist239(np/get) · `f166` | f166 | — | — | `verified` |

### `f167` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f167` | f167 | — | — | `verified` |
| 东财-ulist239(np/get) · `f167` | f167 | — | — | `verified` |

### `f168` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f168` | f168 | 换手率% | % | `verified` |
| 东财-ulist239(np/get) · `f168` | f168 | — | — | `verified` |

### `f169` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f169` | f169 | 涨跌额 | 元 | `verified` |
| 东财-ulist239(np/get) · `f169` | f169 | — | — | `verified` |

### `f17` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f17` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f17` | f17 | 开盘价 | 元 | `verified` |

### `f170` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f170` | f170 | 涨跌幅 | % | `verified` |
| 东财-ulist239(np/get) · `f170` | f170 | — | — | `verified` |

### `f171` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f171` | f171 | 振幅% | % | `verified` |
| 东财-ulist239(np/get) · `f171` | f171 | — | — | `verified` |

### `f172` — incomplete

聚合问题：meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f172` | f172 | — | — | `unverified` |
| 东财-ulist239(np/get) · `f172` | f172 | — | — | `verified` |

### `f173` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f173` | f173 | 加权净资产收益率（最新报告期 %） | % | `verified` |
| 东财-ulist239(np/get) · `f173` | f173 | — | — | `verified` |

### `f174` — ambiguous

聚合问题：canonical_differs；meaning_differs；meaning_incomplete；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f174` | f174 / f175 | 主力净额 | 元/% | `verified` |
| 东财-push2(stock/get) · `f174` | f174 | 52周滚动最高价 | 元 | `verified` |
| 东财-ulist239(np/get) · `f174` | f174 | — | — | `verified` |

### `f175` — ambiguous

聚合问题：canonical_differs；meaning_incomplete；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f175` | f174 / f175 | 主力净额 | 元/% | `verified` |
| 东财-push2(stock/get) · `f175` | f175 | — | — | `verified` |
| 东财-ulist239(np/get) · `f175` | f175 | — | — | `verified` |

### `f176` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f176` | f176 | 按最新报告期年初至期末累计营收年化的市销率；在已观察到的季度中，按 f116 总市值 ÷ (f183 × 4 / q) 计算，q 为最新报告期季度序号。当前实证覆盖 Q2、Q3，不等同市销率 TTM，也不外推 Q1、Q4。发行人报告样本确认了 f183 对应的报告期累计营收，但本定义不统一各行业财报中的具体行项目名称。 | 倍 | `verified` |
| 东财-ulist239(np/get) · `f176` | f176 | — | — | `verified` |

### `f177` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f177` | f177 | — | — | `verified` |
| 东财-ulist239(np/get) · `f177` | f177 | — | — | `verified` |

### `f178` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f178` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f178` | f178 | — | — | `verified` |

### `f179` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f179` | f179 | 现价 | 元 | `verified` |
| 东财-ulist239(np/get) · `f179` | f179 | — | — | `verified` |

### `f18` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f18` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f18` | f18 | 昨收盘 | 元 | `verified` |

### `f180` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f180` | f180 | — | — | `verified` |
| 东财-ulist239(np/get) · `f180` | f180 | — | — | `verified` |

### `f181` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f181` | f181 | — | — | `verified` |
| 东财-ulist239(np/get) · `f181` | f181 | — | — | `verified` |

### `f182` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f182` | f182 | 市场类型枚举 | - | `verified` |
| 东财-ulist239(np/get) · `f182` | f182 | — | — | `verified` |

### `f183` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f183` | f183 | — | — | `verified` |
| 东财-ulist239(np/get) · `f183` | f183 | — | — | `verified` |

### `f184` — ambiguous

聚合问题：meaning_differs；meaning_incomplete；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f184` | f184 | 主力净占比 | % | `verified` |
| 东财-push2(stock/get) · `f184` | f184 | — | — | `verified` |
| 东财-ulist239(np/get) · `f184` | f184 | 换手率% | % | `verified` |

### `f185` — ambiguous

聚合问题：canonical_differs；meaning_incomplete；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f185` | f185 | — | — | `verified` |
| 东财-ulist239(np/get) · `f185` | H 股上一香港交易日收盘价 | 该 A 股记录关联 H 股证券的上一香港交易日正式收盘价。它与同日 Push2 f250 对齐；价格内容日期是上一港股交易日，不是同一行观测日。 | HKD/股 | `verified` |

### `f186` — ambiguous

聚合问题：canonical_differs；meaning_incomplete；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f186` | f186 | — | — | `verified` |
| 东财-ulist239(np/get) · `f186` | H 股最新价 | 该 A 股记录关联 H 股证券的最新成交/行情价。盘中为最新行情价；收盘后样本等于当日收盘价。 | HKD/股 | `verified` |

### `f187` — ambiguous

聚合问题：canonical_differs；meaning_incomplete；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f187` | f187 | — | — | `verified` |
| 东财-ulist239(np/get) · `f187` | H 股当日涨跌幅 | 该 A 股记录关联 H 股证券的当日涨跌幅。收盘样本中按 (f186 / f185 - 1) × 100 计算并四舍五入到两位小数。 | % | `verified` |

### `f188` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f188` | f188 | — | — | `verified` |
| 东财-ulist239(np/get) · `f188` | f188 | — | — | `verified` |

### `f189` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f189` | f189 | 上市日期 | YYYY-MM-DD | `verified` |
| 东财-ulist239(np/get) · `f189` | f189 | — | — | `verified` |

### `f19` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f19` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f19` | f19 | — | — | `verified` |

### `f190` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f190` | f190 | 每股未分配利润 | 元/股 | `verified` |
| 东财-ulist239(np/get) · `f190` | H股关联A股价格缩放位数 | 东方财富行情中心把 f190 用作 f186（H股对应的A股最新价）的十进制缩放/显示精度参数：官方前端在 fltt=1 价格值场景中按 f186 / 10^f190 还原并显示 f190 位小数。项目采集使用 fltt=2，留存的 f186 已为小数形式，不应重复缩放。该字段不是 H 股股数。 | — | `verified` |

### `f191` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f191` | f191 | 委比 | % | `verified` |
| 东财-ulist239(np/get) · `f191` | h_share_code | A 股记录所关联 H 股证券的代码。当前经核对样本为 601288 对应 01288；结论仅适用于东财 Ulist239 该完整来源路径。 | — | `verified` |

### `f192` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f192` | f192 | 委差 | 手 | `verified` |
| 东财-ulist239(np/get) · `f192` | h_share_market_code | A 股记录所关联 H 股证券的东方财富 secid 市场编号。当前经核对样本为 116，对应 secid 116.01288 中的港股市场前缀；该字段是市场编号，不是 A+H 布尔标记。结论仅适用于东财 Ulist239 该完整来源路径及已观察到的编号。 | — | `verified` |

### `f193` — ambiguous

聚合问题：canonical_differs；meaning_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f193` | f193 | — | — | `verified` |
| 东财-ulist239(np/get) · `f193` | h_share_name | A 股记录所关联 H 股证券的简称。当前经核对样本为农业银行；结论仅适用于东财 Ulist239 该完整来源路径。 | — | `verified` |

### `f194` — incomplete

聚合问题：meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f194` | f194 | — | — | `verified` |
| 东财-ulist239(np/get) · `f194` | f194 | — | — | `unverified` |

### `f195` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f195` | f195 | — | — | `verified` |
| 东财-ulist239(np/get) · `f195` | f195 | — | — | `verified` |

### `f196` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f196` | f196 | — | — | `verified` |
| 东财-ulist239(np/get) · `f196` | f196 | — | — | `verified` |

### `f197` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f197` | f197 | — | — | `verified` |
| 东财-ulist239(np/get) · `f197` | f197 | — | — | `verified` |

### `f199` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f199` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f199` | f199 | — | — | `verified` |

### `f2` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f2` | clist_board_current_index_value | 东方财富板块排行记录的当前板块指数值。 | 点 | `verified` |
| 东财-push2(stock/get) · `f2` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f2` | f2 | 现价 | 元 | `verified` |

### `f207` — ambiguous

聚合问题：canonical_differs；meaning_incomplete；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f207` | clist_loser_stock_name | 东方财富板块排行中领跌股票简称。 | — | `verified` |
| 东财-ulist239(np/get) · `f207` | f207 | — | — | `unverified` |

### `f208` — ambiguous

聚合问题：canonical_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f208` | clist_loser_stock_code | 领跌股票的证券代码；与 f207 名称和 f209 市场编号组成同一领跌股票链接。 | 证券代码 | `verified` |
| 东财-ulist239(np/get) · `f208` | f208 | — | — | `unverified` |

### `f209` — ambiguous

聚合问题：canonical_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f209` | clist_loser_stock_market_id | 领跌股票的市场编号；与 f208 股票代码组合成东方财富 unify/r/{market}.{code} 行情路由。 | 市场编号 | `verified` |
| 东财-ulist239(np/get) · `f209` | f209 | — | — | `unverified` |

### `f216` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f216` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f216` | f216 | — | — | `unverified` |

### `f23` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f23` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f23` | f23 | 市净率 PB | 倍 | `verified` |

### `f24` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f24` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f24` | f24 | — | — | `verified` |

### `f25` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f25` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f25` | f25 | — | — | `verified` |

### `f250` — ambiguous

聚合问题：canonical_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f250` | H 股上一香港交易日收盘价 | 该 A 股记录关联 H 股证券的上一香港交易日正式收盘价。此字段所指价格日期早于同一记录行的行情观测日期；同一行的已验证 Push2 f86 只确认观测日期。 | HKD/股 | `verified` |
| 东财-ulist239(np/get) · `f250` | f250 | — | — | `unverified` |

### `f26` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f26` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f26` | f26 | — | — | `verified` |

### `f27` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f27` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f27` | f27 | 市场标志：本项目 A 股样本中沪市=1，非沪市=0（含深市、北交）；与同源 f13 为实证别名。 | — | `verified` |

### `f29` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f29` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f29` | f29 | — | — | `verified` |

### `f3` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f3` | f3 | 涨跌幅 | — | `verified` |
| 东财-push2(stock/get) · `f3` | — | — | — | `unverified` |
| 东财-slist · `f3` | f3 | 板块当日涨跌幅 | — | `verified` |
| 东财-ulist239(np/get) · `f3` | f3 | 涨跌幅 | % | `verified` |

### `f37` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f37` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f37` | f37 | — | — | `verified` |

### `f38` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f38` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f38` | f38 | — | — | `verified` |

### `f39` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f39` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f39` | liutongguben | 流通股本 | 股 | `verified` |

### `f4` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f4` | clist_board_change_amount | 东方财富板块指数相对前收的涨跌额。 | 点 | `verified` |
| 东财-push2(stock/get) · `f4` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f4` | f4 | 涨跌额 | 元 | `verified` |

### `f40` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f40` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f40` | f40 | — | — | `verified` |

### `f41` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f41` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f41` | f41 | — | — | `verified` |

### `f43` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f43` | f43 | 现价 | 元 | `verified` |
| 东财-ulist239(np/get) · `f43` | f43 | — | — | `verified` |

### `f44` — ambiguous

聚合问题：canonical_differs；meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f44` | f44 | 最高价 | 元 | `verified` |
| 东财-ulist239(np/get) · `f44` | lirunzonghe | 利润总额 | 元 | `verified` |

### `f45` — ambiguous

聚合问题：canonical_differs；meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f45` | f45 | 最低价 | 元 | `verified` |
| 东财-ulist239(np/get) · `f45` | latest_report_parent_net_profit_ytd | 最新已披露定期报告中归属于上市公司股东的净利润，按年初至报告期末累计。 | 元 | `verified` |

### `f46` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f46` | f46 | 开盘价 | 元 | `verified` |
| 东财-ulist239(np/get) · `f46` | ulist239_parent_net_profit_yoy_growth_pct | 归属于母公司股东的净利润同比增长率（东方财富财报展示口径；亏损基期算法另行保留） | % | `verified` |

### `f47` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f47` | f47 | 成交量 | 手 | `verified` |
| 东财-ulist239(np/get) · `f47` | weifenlirun | 未分配利润 | 元 | `verified` |

### `f48` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f48` | f48 | 成交额 | 元 | `verified` |
| 东财-ulist239(np/get) · `f48` | f48 | — | — | `verified` |
| 东财-资金流(em_fund_flow) · `f48` | — | — | — | `unverified` |

### `f49` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f49` | eastmoney_stock_get_outer_volume | 外盘成交量 | 手 | `verified` |
| 东财-ulist239(np/get) · `f49` | ulist239_sales_gross_margin_report_period_pct | 报告期销售毛利率（东方财富财报展示口径；单位为%；本次 2026-09-30 样本对应年初至 9 月累计报告期） | % | `verified` |

### `f50` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f50` | f50 | 量比 | - | `verified` |
| 东财-ulist239(np/get) · `f50` | zongzichan | 总资产 | 元 | `verified` |

### `f51` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f51` | f51 | 日期 | YYYY-MM-DD | `verified` |
| 东财-push2(stock/get) · `f51` | f51 | 涨停价 | 元 | `verified` |
| 东财-ulist239(np/get) · `f51` | liudongzichan | 流动资产 | 元 | `verified` |
| 东财-资金流(em_fund_flow) · `f51` | — | — | — | `unverified` |

### `f52` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f52` | f52 | 开盘价 | 元 | `verified` |
| 东财-push2(stock/get) · `f52` | f52 | 跌停价 | 元 | `verified` |
| 东财-ulist239(np/get) · `f52` | gudingzichan | 固定资产 | 元 | `verified` |
| 东财-资金流(em_fund_flow) · `f52` | — | — | — | `unverified` |

### `f53` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f53` | f53 | 收盘价 | 元 | `verified` |
| 东财-push2(stock/get) · `f53` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f53` | f53 | — | — | `verified` |
| 东财-资金流(em_fund_flow) · `f53` | — | — | — | `unverified` |

### `f54` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f54` | f54 | 最高价 | 元 | `verified` |
| 东财-push2(stock/get) · `f54` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f54` | f54 | — | — | `verified` |
| 东财-资金流(em_fund_flow) · `f54` | — | — | — | `unverified` |

### `f55` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f55` | f55 | 最低价 | 元 | `verified` |
| 东财-push2(stock/get) · `f55` | f55 | 基本每股收益计算值（最新报告期归母净利润/最新总股本） | 元/股 | `verified` |
| 东财-ulist239(np/get) · `f55` | liudongfuzhai | 流动负债 | 元 | `verified` |
| 东财-资金流(em_fund_flow) · `f55` | — | — | — | `unverified` |

### `f56` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f56` | f56 | 成交量 | 手 | `verified` |
| 东财-push2(stock/get) · `f56` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f56` | f56 | — | — | `verified` |
| 东财-资金流(em_fund_flow) · `f56` | — | — | — | `unverified` |

### `f57` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f57` | f57 | 成交额 | 元 | `verified` |
| 东财-push2(stock/get) · `f57` | f57 | 股票代码 | - | `verified` |
| 东财-ulist239(np/get) · `f57` | f57 | — | — | `verified` |
| 东财-资金流(em_fund_flow) · `f57` | — | — | — | `unverified` |

### `f58` — ambiguous

聚合问题：meaning_differs；meaning_incomplete；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f58` | f58 | 振幅% | % | `verified` |
| 东财-push2(stock/get) · `f58` | f58 | 股票名称 | - | `verified` |
| 东财-ulist239(np/get) · `f58` | f58 | — | — | `verified` |

### `f59` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f59` | f59 | 涨跌幅 | % | `verified` |
| 东财-push2(stock/get) · `f59` | quote_price_precision_digits | 该证券实时行情报价的显示小数位数；在 fltt=1 响应中用于将价格整数还原为 fltt=2 报价。 | 位（小数位数） | `verified` |
| 东财-ulist239(np/get) · `f59` | parent_equity_to_total_assets_ratio | 报告期末合并资产负债表中归属于母公司股东（或所有者）权益占总资产的比例；按 TOTAL_PARENT_EQUITY ÷ TOTAL_ASSETS × 100 计算。 | % | `verified` |

### `f60` — ambiguous

聚合问题：canonical_differs；meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f60` | f60 | 涨跌额 | 元 | `verified` |
| 东财-push2(stock/get) · `f60` | f60 | 昨收盘 | 元 | `verified` |
| 东财-ulist239(np/get) · `f60` | zibengongjijin | 资本公积金 | 元 | `verified` |

### `f61` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f61` | f61 | 换手率% | % | `verified` |
| 东财-ulist239(np/get) · `f61` | f61 | — | — | `verified` |

### `f62` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f62` | f62 | 主力净流入额 | 元 | `verified` |
| 东财-push2(stock/get) · `f62` | f62 | 最新已发布报告期的季度序号（如 2=中报、3=三季报；不含年份） | 季度序号 | `verified` |
| 东财-ulist239(np/get) · `f62` | f62 | 主力净流入额 | 元 | `verified` |
| 东财-资金流(em_fund_flow) · `f62` | — | — | — | `unverified` |

### `f64` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f64` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f64` | f64 | — | — | `verified` |

### `f65` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f65` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f65` | f65 | — | — | `verified` |

### `f66` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f66` | f66 / f72 / f78 / f84 | 超大/大/中/小单净额 | 元 | `verified` |
| 东财-push2(stock/get) · `f66` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f66` | f66 | — | — | `verified` |
| 东财-资金流(em_fund_flow) · `f66` | — | — | — | `unverified` |

### `f69` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f69` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f69` | f69 | — | — | `verified` |
| 东财-资金流(em_fund_flow) · `f69` | — | — | — | `unverified` |

### `f7` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f7` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f7` | f7 | — | — | `verified` |

### `f70` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f70` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f70` | f70 | — | — | `verified` |

### `f71` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f71` | f71 | — | — | `verified` |
| 东财-ulist239(np/get) · `f71` | f71 | — | — | `verified` |

### `f72` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f72` | f66 / f72 / f78 / f84 | 超大/大/中/小单净额 | 元 | `verified` |
| 东财-push2(stock/get) · `f72` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f72` | f72 | — | — | `verified` |
| 东财-资金流(em_fund_flow) · `f72` | — | — | — | `unverified` |

### `f73` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f73` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f73` | f73 | — | — | `verified` |

### `f74` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f74` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f74` | f74 | — | — | `verified` |

### `f75` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f75` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f75` | f75 | — | — | `verified` |
| 东财-资金流(em_fund_flow) · `f75` | — | — | — | `unverified` |

### `f76` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f76` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f76` | fund_mid_buy | 东方财富个股资金流分类口径下，当日中单类别流入/买入金额；此分类不表示投资者账户身份。 | 元 | `verified` |

### `f77` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f77` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f77` | fund_mid_sell | 东方财富个股资金流分类口径下，当日中单类别流出/卖出金额；此分类不表示投资者账户身份。 | 元 | `verified` |

### `f78` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f78` | f66 / f72 / f78 / f84 | 超大/大/中/小单净额 | 元 | `verified` |
| 东财-push2(stock/get) · `f78` | f78 | — | — | `verified` |
| 东财-ulist239(np/get) · `f78` | fund_mid_today | 东方财富个股资金流分类口径下，当日中单净流入金额，等于中单流入减中单流出；此分类不表示投资者账户身份。 | 元 | `verified` |
| 东财-资金流(em_fund_flow) · `f78` | — | — | — | `unverified` |

### `f8` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f8` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f8` | f8 | — | — | `verified` |

### `f80` — ambiguous

聚合问题：canonical_differs；meaning_incomplete；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f80` | stock_trading_session_intervals | 该证券当日宽泛交易时段区间列表。源值为 JSON 数组，每项 `b` / `e` 是北京时间 YYYYMMDDHHmm；区间覆盖交易会话，下午区间包含收盘集合竞价，不等同于连续竞价分段。 | 数组；时间戳格式 YYYYMMDDHHmm（北京时间） | `verified` |
| 东财-ulist239(np/get) · `f80` | f80 | — | — | `verified` |

### `f81` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f81` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f81` | f81 | — | — | `verified` |

### `f82` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f82` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f82` | f82 | — | — | `verified` |

### `f83` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f83` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f83` | f83 | — | — | `verified` |

### `f84` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f84` | f66 / f72 / f78 / f84 | 超大/大/中/小单净额 | 元 | `verified` |
| 东财-push2(stock/get) · `f84` | f84 | 总股本 | 股→万股 | `verified` |
| 东财-ulist239(np/get) · `f84` | f84 | — | — | `verified` |
| 东财-资金流(em_fund_flow) · `f84` | — | — | — | `unverified` |

### `f85` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f85` | f85 | 流通股本 | 股→万股 | `verified` |
| 东财-ulist239(np/get) · `f85` | f85 | — | — | `verified` |

### `f86` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f86` | f86 | 当日收盘/最后行情时间戳 | Unix 秒 | `verified` |
| 东财-ulist239(np/get) · `f86` | f86 | — | — | `verified` |

### `f87` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f87` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f87` | f87 | — | — | `verified` |

### `f9` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f9` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f9` | f9 | 市盈率（动态/最新报告期年化） | 倍 | `verified` |

### `f92` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f92` | f92 | 每股净资产计算值（最新公告归母股东权益剔除其他权益工具后/最新总股本） | 元/股 | `verified` |
| 东财-ulist239(np/get) · `f92` | f92 | — | — | `verified` |

### `first_limit_time` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2ex · `first_limit_time` | limit_pool_first_seal_time | 东财涨停股池个股当日首次封板时间；项目原值为 HHMMSS 数字字符串，左补零后格式化为页面显示的 HH:MM:SS。 | HHMMSS | `verified` |
| 同花顺-fuyao · `first_limit_time` | first_limit_time | 首次与最后跌停时间，上海时区 `HH:mm`。 | HH:mm | `verified` |

### `fund` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2ex · `fund` | fund | 封单额 | 元 | `verified` |
| 同花顺-fuyao · `fund` | — | — | — | `unverified` |

### `high` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `high` | high | 最高价 | 元/股 | `verified` |
| TDX(双命名源) · `high` | high | 最高价 | 元 | `verified` |
| TDX-eltdx(适配层) · `high` | high | 日K最高价 | 元 | `verified` |
| 同花顺-fuyao · `high` | — | — | — | `unverified` |

### `high_price` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `high_price` | high_price | 最高价 | — | `verified` |
| 同花顺-fuyao · `high_price` | snapshot.high_price | 旧无分组根路径身份；当前完整采集路径为 snapshot.high_price。官方接口将 high_price 列在 data.item[]，项目采集输出将 item 保存在 stocks.<代码>.snapshot。本记录只退役裸叶来源路径。 | 元 | `disproved` |

### `hot_rank` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-热榜(em_hot) · `hot_rank` | — | — | — | `unverified` |
| 同花顺-fuyao · `hot_rank` | hot_rank | 同花顺人气排名，数值越小越靠前。 | — | `verified` |

### `industry_id` — ambiguous

聚合问题：meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 开盘红 · `industry_id` | industry_id | 行业分类 ID；与 KPL sector_code 在来源日期对齐的 420 组对照中 417 组相同、3 组不同；分类体系或层级未确认，保留各来源原码 | — | `verified` |
| 开盘红(Levistock适配) · `industry_id` | industry_id | 开盘红接口返回的行业分类 ID，作为 KPH 自身记录的分类键。具体分类体系和层级未公开；本定义不意味着该 ID 与 KPL sector_code 等价，也不推断它对应任何特定行业标准。 | — | `verified` |

### `int` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `int` | — | — | — | `disproved` |
| ZHB-tdxstat · `int` | — | — | — | `disproved` |
| 财联社(cls) · `int` | — | — | — | `unverified` |

### `ipo_date` — ambiguous

聚合问题：unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `ipo_date` | ipo_date | 上市日期 | YYYYMMDD | `verified` |
| TDX-eltdx(适配层) · `ipo_date` | ipo_date | 上市日期 | 日期字符串（样本格式 YYYY-MM-DD） | `verified` |

### `is_new` — ambiguous

聚合问题：meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-热榜(em_hot) · `is_new` | is_new | 是否新股 | — | `verified` |
| 同花顺-fuyao · `is_new` | is_new | 是否未开板新股，仅展示。 | 布尔值 | `verified` |
| 财联社(cls) · `is_new` | is_new | 是否新上榜（1=是） | — | `unverified` |

### `jing_li_run_raw_float` — ambiguous

聚合问题：meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `jing_li_run_raw_float` | jing_li_run_raw_float | 净利润原始值 | 千元 | `verified` |
| TDX-eltdx(适配层) · `jing_li_run_raw_float` | jing_li_run_raw_float | 归属于上市公司股东的净利润原始值；样本对应报告期累计值 | 千元 | `verified` |

### `last_limit_time` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2ex · `last_limit_time` | limit_pool_last_seal_time | 东财涨停股池个股当日最后封板时间；项目原值为 HHMMSS 数字字符串，左补零后格式化为页面显示的 HH:MM:SS。 | HHMMSS | `verified` |
| 同花顺-fuyao · `last_limit_time` | last_limit_time | 首次与最后跌停时间，上海时区 `HH:mm`。 | HH:mm | `verified` |

### `last_price` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `last_price` | last_price | 最新价或最新值（AxData TDX 实时快照模型语义；不表示当前项目采集路径） | — | `verified` |
| TDX-eltdx(适配层) · `last_price` | last_price | 最新价 / 现价 | — | `verified` |
| 同花顺-fuyao · `last_price` | snapshot.last_price | 旧无分组根路径身份；当前完整采集路径为 snapshot.last_price。官方接口将 last_price 列在 data.item[]，项目采集输出将 item 保存在 stocks.<代码>.snapshot。本记录只退役裸叶来源路径。 | 元 | `disproved` |

### `level` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `level` | level | 待破解 | — | `unverified` |
| 财联社(cls) · `level` | cls_telegraph_display_level_code | 财联社电报记录的网页展示等级代码。当前官方电报页对 A、B 使用红色文本，对 A 额外加粗；其他值走默认文本样式。官方页面脚本没有给出完整代码全集、代码业务名称、重要性排序或分类判定规则。 | 代码 | `verified` |

### `limit_count` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2ex · `limit_count` | limit_up_streak_count | 当前连续涨停板数（当前连板数）；与同数据日 KPL col_15 的三个有效日期 271 组对照逐值相等。11 月 5 日次日回查存在集合和值差异，已单独记录且不计入正证据。 | 板 | `verified` |
| 市场源(market_sources) · `limit_count` | limit_count | 连板数 | — | `verified` |
| 开盘红 · `limit_count` | limit_count | 连板数；从 KPL 原始 row[18] 的 N天M板解析 M，30 个可解析值 30/30 一致 | 板 | `verified` |
| 开盘红(Levistock适配) · `limit_count` | limit_tag / limit_count | 待破解 | — | `unverified` |

### `limit_down` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `limit_down` | tdx_get_quote_full.limit_down | 项目行情包装层按昨收和证券价格限制规则计算的跌停价（元）；可能在缺值时再由其他行情回退补充，不是 TDX wire 字段。 | 元 | `disproved` |
| 新浪(扩展API) · `limit_down` | limit_up / limit_down | 涨跌停价 | — | `unverified` |

### `limit_down_price` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `limit_down_price` | tdx_get_quote_full.limit_down_price | Tencent 行情槽位包装出的跌停价（元）；不是 TDX 原始响应字段。官方 TQ DTPrice 是另一接口的独立契约路径。 | 元 | `disproved` |
| TDX-eltdx(适配层) · `limit_down_price` | limit_down_price | 跌停价 | — | `verified` |

### `limit_tag` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 开盘红 · `limit_tag` | limit_tag | 连板标签；与 KPL 原始 row[18] 可见的 33 条非空值 33/33 一致 | — | `verified` |
| 开盘红(Levistock适配) · `limit_tag` | limit_tag / limit_count | 待破解 | — | `unverified` |

### `limit_time` — ambiguous

聚合问题：meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `limit_time` | limit_time | 涨停时间；值为 Unix 秒时间戳。首次封板或末次封板口径未由本证据单独确认。 | Unix 秒 | `verified` |
| 开盘红 · `limit_time` | limit_time | 涨停时间；与 KPL zt_time 370 组、8 个交易日逐值一致 | Unix 秒 | `verified` |
| 开盘红(Levistock适配) · `limit_time` | limit_time | 涨停时间；值为 Unix 秒时间戳。首次封板或末次封板口径未由本证据单独确认。 | Unix 秒 | `verified` |

### `limit_up` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `limit_up` | tdx_get_quote_full.limit_up | 项目行情包装层按昨收和证券价格限制规则计算的涨停价（元）；可能在缺值时再由其他行情回退补充，不是 TDX wire 字段。 | 元 | `disproved` |
| 新浪(扩展API) · `limit_up` | limit_up / limit_down | 涨跌停价 | — | `unverified` |

### `limit_up_count` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `limit_up_count` | limit_up_count | Helper 返回的目标交易日内，本次请求股票池中已封涨停且关联该题材的股票数；不含仅触板股票，也不是全市场计数。 | 只 | `verified` |
| 开盘啦(kpl) · `limit_up_count` | — | — | — | `unverified` |

### `list` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `list` | meta/tickers/list | — | — | `unverified` |
| 开盘啦(kpl) · `list` | — | — | — | `unverified` |
| 财联社(cls) · `list` | — | — | — | `unverified` |

### `locked_amount` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `locked_amount` | — | TDX(双命名源) 的旧错误来源身份；项目已验证的 locked_amount 属于 TDX-eltdx(适配层) 的不同来源/完整路径，不移植到此身份。 | — | `disproved` |
| TDX-eltdx(适配层) · `locked_amount` | locked_amount | 买一档挂单金额；按 bid1 × bid_vol1 × 100 计算，不等同涨停总封单金额 | 元 | `verified` |

### `low` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `low` | low | 最低价 | 元/股 | `verified` |
| TDX(双命名源) · `low` | low | 最低价 | 元 | `verified` |
| TDX-eltdx(适配层) · `low` | low | 日K最低价 | 元 | `verified` |
| 同花顺-fuyao · `low` | — | — | — | `unverified` |

### `low_price` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `low_price` | low_price | 最低价 | — | `verified` |
| 同花顺-fuyao · `low_price` | snapshot.low_price | 旧无分组根路径身份；当前完整采集路径为 snapshot.low_price。官方接口将 low_price 列在 data.item[]，项目采集输出将 item 保存在 stocks.<代码>.snapshot。本记录只退役裸叶来源路径。 | 元 | `disproved` |

### `main_buy` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `main_buy` | — | — | — | `unverified` |
| 开盘啦(kpl) · `main_buy` | main_buy | 主力买入额 | 元 | `unverified` |
| 开盘啦(kpl_limit_up_detail) · `main_buy` | main_buy | 主力买入额 | 元 | `verified` |

### `main_inflow` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `main_inflow` | — | — | — | `unverified` |
| 开盘啦(kpl_limit_up_detail) · `main_inflow` | main_inflow | 主力净流入；与 KPH net_inflow 两日逐值一致 | 元 | `verified` |

### `main_net_buy_hands` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat2 · `main_net_buy_hands` | [9] | 当日开盘集合竞价成交量；历史兼容键，不表示主力净买入手数。 | 手 | `verified` |
| 同花顺-fuyao · `main_net_buy_hands` | — | — | — | `unverified` |

### `main_sell` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `main_sell` | — | — | — | `unverified` |
| 开盘啦(kpl) · `main_sell` | main_sell | 主力卖出额 | 元 | `unverified` |
| 开盘啦(kpl_limit_up_detail) · `main_sell` | main_sell | 主力卖出额（负值表示卖出流出） | 元 | `verified` |

### `market` — ambiguous

聚合问题：meaning_differs；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `market` | market | 市场代码 | 0=深/1=沪/2=京 | `verified` |
| ZHB-tdxstat · `market` | market | 市场 | - | `verified` |
| ZHB-tdxstat2 · `market` | market | 市场 | - | `verified` |
| reports · `market` | market | 交易所 | — | `verified` |
| 东财-热榜(em_hot) · `market` | market | 市场 | — | `verified` |
| 同花顺-fuyao · `market` | market | Fuyao 采集器保存市场级结果的顶层对象容器，包含基准、涨跌停池和异动等独立输出路径；不是单一市场业务指标。各子路径按对应采集单元维护。 | — | `disproved` |
| 市场源(market_sources) · `market` | market | 市场 | — | `verified` |

### `market_cap` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `market_cap` | market_cap | 总市值 | 元 | `verified` |
| 东财-datacenter(英文键) · `market_cap` | northbound_hold.market_cap | 旧未限定短路径已退役。完整北向持股市值路径已按来源契约核验。 完整路径：northbound_hold.market_cap。多目标别名只用于说明路径拆分，不表示这些字段同义。 | — | `disproved` |
| 开盘红 · `market_cap` | float_market_value | 流通市值；与 KPL 实际流通字段 369/370 逐值一致；1 组相差约 0.8025%，不按舍入等价处理 | 元 | `verified` |

### `max_seal` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `max_seal` | — | — | — | `unverified` |
| 开盘啦(kpl_limit_up_detail) · `max_seal` | max_seal | 最大封单金额；与 KPH seal_money 三个交易日逐股逐值一致 | 元 | `verified` |

### `name` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `name` | name | 证券名称 | — | `verified` |
| TDX(双命名源) · `name` | tdx_get_quote_full.name | 统一行情包装层中的证券名称字段；TDX 快照 SecurityQuote 不含名称，当前包装值来自回退上下文。raw_eltdx 中的 name 是 global_helpers.realtime_rank.rows[].name 的另一来源/完整路径。 | — | `disproved` |
| TDX-eltdx(适配层) · `name` | name | — | — | `unverified` |
| 东财-push2ex · `name` | stock_name | 东财涨停股池记录对应的证券简称，对应东方财富官方页面“名称”列。 | — | `verified` |
| 东财-热榜(em_hot) · `name` | — | — | — | `verified` |
| 同花顺-fuyao · `name` | — | — | — | `unverified` |
| 市场源(market_sources) · `name` | name | 股票名称 | — | `verified` |
| 开盘啦(kpl) · `name` | name | 股票名称 | — | `unverified` |
| 财联社(cls) · `name` | — | — | — | `unverified` |

### `net_inflow` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 开盘红 · `net_inflow` | main_inflow | 主力净流入；与 KPL main_inflow 370 组、8 个交易日逐值一致 | 元 | `verified` |
| 开盘红(Levistock适配) · `net_inflow` | net_inflow / market_cap | 待破解 | — | `unverified` |

### `net_profit` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `net_profit` | finance_info.jinglirun | 旧统一层别名，不是独立 TDX 原始路径；当前原始路径为 finance_info.jinglirun | — | `disproved` |
| 同花顺-fuyao · `net_profit` | net_profit | 合并净利润（含少数股东损益） | 原币元 | `verified` |

### `open` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `open` | open | 开盘价 | 元/股 | `verified` |
| TDX(双命名源) · `open` | open | 开盘价 | 元 | `verified` |
| TDX-eltdx(适配层) · `open` | open | 日K开盘价 | 元 | `verified` |
| 同花顺-fuyao · `open` | — | — | — | `unverified` |
| 新浪(扩展API) · `open` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | — | `unverified` |

### `open_price` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `open_price` | open_price | 今开价 | — | `verified` |
| 同花顺-fuyao · `open_price` | snapshot.open_price | 旧无分组根路径身份；当前完整采集路径为 snapshot.open_price。官方接口将 open_price 列在 data.item[]，项目采集输出将 item 保存在 stocks.<代码>.snapshot。本记录只退役裸叶来源路径。 | 元 | `disproved` |

### `open_time` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 开盘红 · `open_time` | — | 开板时间；AxData 0.1.4 将原始 row[7] 映射为时间戳；370 组样本均为 0，暂无非零值核验 | — | `unverified` |
| 开盘红(Levistock适配) · `open_time` | limit_time / open_time | 待破解 | — | `unverified` |

### `pb` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `pb` | tdx_get_quote_full.pb | 统一行情包装层的市净率值；当前 TDX 快照模型没有 PB 字段，包装层可由 ZHB/Tencent 回退填充。官方 TQ PB_MRQ 是另一接口路径，不自动映射。 | 倍 | `disproved` |
| 开盘啦(kpl) · `pb` | pb | 市净率 | 倍 | `unverified` |

### `pct` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-热榜(em_hot) · `pct` | pct | 涨跌幅 | % | `verified` |
| 财联社(cls) · `pct` | — | — | — | `unverified` |

### `pe_lyr` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `pe_lyr` | tdx_get_quote_full.pe_lyr | 统一行情包装层从 Tencent 静态 PE 槽位透传的值；当前 TDX 快照模型无该字段。官方 TQ MorePE 的口径按证券类型变化，不自动映射。 | 倍 | `disproved` |
| ZHB-tdxstat · `pe_lyr` | pe_lyr | 静态市盈率（LYR/上一完整年度业绩口径）；180 组、9 个来源日期与已验证静态 PE 参照相符，最大差 0.006 倍；精度差异不证明跨源逐值相同。 | 倍 | `verified` |

### `pe_static` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `pe_static` | — | 已删除的重复包装输出键；代码自 2026-09-04 起只保留 pe_lyr，当前 TDX adapter/raw 也没有 pe_static 原始路径。 | — | `disproved` |
| 开盘啦(kpl) · `pe_static` | pe_static | 静态市盈率（LYR）：总市值 ÷ 上一年度净利润。 | 倍 | `verified` |

### `pe_ttm` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `pe_ttm` | pe_ttm | 滚动市盈率（TTM） | — | `verified` |
| TDX(双命名源) · `pe_ttm` | pe_ttm | 旧版 tdx_get_quote_full() 返回键；2026-10-15 只见于 quote_full.pe_ttm，20/20 同股值与 ZHB stat.pe_ttm 和合并对象 full.pe_ttm 精确相同；同股 quote_raw 不含该键。当前 TDX 专用采集改用 tdx_get_quote_raw()，本审计仅撤销该历史样本对 TDX 原始字段归属的支持，不裁定业务语义；未来 raw 若出现该键须重新审查。 | — | `disproved` |
| TDX-eltdx(适配层) · `pe_ttm` | pe_ttm | 滚动市盈率 | 倍 | `verified` |
| ZHB-tdxstat · `pe_ttm` | pe_ttm | 市盈率（TTM） | 倍 | `verified` |
| 同花顺-fuyao · `pe_ttm` | valuation.pe_ttm | 旧无分组根路径身份；当前完整采集路径为 valuation.pe_ttm。接口响应把该叶字段放在 data.item[]，项目采集输出则将 item 保存在 stocks.<代码>.valuation。本记录只退役裸叶来源路径。 | 倍 | `disproved` |
| 开盘啦(kpl) · `pe_ttm` | pe_ttm | 滚动市盈率（PE TTM）：最新价 ÷ 最近四个季度每股收益。 | 倍 | `verified` |

### `performance` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `performance` | — | — | — | `unverified` |
| 市场源(market_sources) · `performance` | performance | 昨涨停今表现 | — | `unverified` |

### `plate_code` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `plate_code` | plate_code | 板块代码 | — | `verified` |
| 财联社(cls) · `plate_code` | plate_code / plate_name | 板块代码 / 名称（风口板块） | — | `unverified` |

### `plate_name` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `plate_name` | plate_name | 板块名称 | — | `verified` |
| 财联社(cls) · `plate_name` | plate_code / plate_name | 板块代码 / 名称（风口板块） | — | `unverified` |

### `plates` — ambiguous

聚合问题：canonical_differs；meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `plates` | plates | 相关板块列表 | — | `unverified` |
| 财联社(cls) · `plates` | trade_date / plates | 轮动日期 / 当日 top10 板块列表 | — | `unverified` |

### `pre_close` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `pre_close` | pre_close | 前收盘价或上一期值（AxData TDX 实时快照模型语义；不表示当前项目采集路径） | — | `verified` |
| TDX-eltdx(适配层) · `pre_close` | shortline.pre_close | 已退役的未限定旧路径身份 | — | `disproved` |

### `pre_close_price` — ambiguous

聚合问题：meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `pre_close_price` | pre_close_price | 昨收价 | — | `verified` |
| 同花顺-fuyao · `pre_close_price` | pre_close_price | 集合竞价快照中的前收盘价。 | — | `verified` |

### `prev_close` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `prev_close` | prev_close | 前收盘价 | 元/股 | `verified` |
| 新浪(扩展API) · `prev_close` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | — | `unverified` |

### `price` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `price` | price | 现价 | 元 | `verified` |
| TDX-eltdx(适配层) · `price` | price | 实时行情快照最新价；收盘阶段与该数据日收盘价一致。 | 元 | `verified` |
| 东财-datacenter(英文键) · `price` | block_trade.price | 旧未限定短路径已退役。get_block_trade 的大宗交易成交价输出。 完整路径：block_trade.price。多目标别名只用于说明路径拆分，不表示这些字段同义。 | — | `disproved` |
| 东财-push2ex · `price` | price | 现价；接口原始数值以 0.001 元为单位，除以 1,000 后与同数据日 KPL col_21 的三个有效日期 271 组对照逐值相等。 | 0.001元 | `verified` |
| 东财-热榜(em_hot) · `price` | price | 现价 | 元 | `verified` |
| 市场源(market_sources) · `price` | price | 现价 | — | `verified` |
| 开盘啦(kpl) · `price` | price | 现价 | 元 | `verified` |

### `q_zrcs` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `q_zrcs` | s_zrcs / q_zrcs | 昨日沪市 / 昨日全市成交额 | — | `unverified` |
| 开盘啦(kpl) · `q_zrcs` | — | — | — | `unverified` |
| 开盘红(Levistock适配) · `q_zrcs` | s_zrcs / q_zrcs | 昨日沪市 / 昨日全市成交额 | — | `unverified` |

### `qscln` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `qscln` | szln / qscln | 待破解 | — | `unverified` |
| 开盘啦(kpl) · `qscln` | — | — | — | `unverified` |
| 开盘红(Levistock适配) · `qscln` | szln / qscln | 待破解 | — | `unverified` |

### `rank` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `rank` | rank | — | — | `unverified` |
| 东财-热榜(em_hot) · `rank` | rank | 人气排名 | - | `verified` |
| 同花顺-fuyao · `rank` | — | — | — | `unverified` |
| 市场源(market_sources) · `rank` | rank | 排名 | — | `verified` |
| 财联社(cls) · `rank` | rank / cur_heat | 当前热度排名 / 热度值 | — | `unverified` |

### `rank_change` — ambiguous

聚合问题：meaning_differs；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `rank_change` | rank_change | 排名变化，正数表示上升，负数表示下降；上游缺失时为 `null`。 | — | `verified` |
| 财联社(cls) · `rank_change` | rank_change | 排名变化（正=上升，负=下降） | — | `unverified` |

### `reading_num` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `reading_num` | reading_num / share_num | 阅读数/分享数 | — | `unverified` |
| 财联社(cls) · `reading_num` | reading_num | 阅读数 | — | `verified` |

### `reason` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-热榜(em_hot) · `reason` | reason | 题材归因 | — | `verified` |
| 市场源(market_sources) · `reason` | — | — | — | `unverified` |
| 开盘红 · `reason` | limit_up_reason | 涨停原因；与 KPL reason 367/370 逐字一致，3 组文本差异保留来源原值 | — | `verified` |
| 开盘红(Levistock适配) · `reason` | reason | 涨停原因 | — | `unverified` |

### `rise_speed` — ambiguous

聚合问题：meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `rise_speed` | rise_speed | 涨速百分比指标；具体计算窗口及与官方协议槽位的对应关系未确认（AxData TDX 快照模型语义，不证明当前项目采集路径） | % | `verified` |
| TDX-eltdx(适配层) · `rise_speed` | rise_speed | 涨速指标 | — | `verified` |

### `seal_amount` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `seal_amount` | seal_amount | 当前买一档挂单金额；不代表涨停总封单金额 | 元 | `verified` |
| 市场源(market_sources) · `seal_amount` | — | — | — | `unverified` |
| 开盘啦(kpl_limit_up_detail) · `seal_amount` | seal_amount | 封单量；与 KPH seal_amount 三个交易日逐股逐值一致，计量单位未确认 | — | `verified` |
| 开盘红 · `seal_amount` | seal_amount | 封单量；与 KPL seal_amount 370 组、8 个交易日逐值一致，计量单位未确认 | — | `verified` |
| 开盘红(Levistock适配) · `seal_amount` | seal_amount / seal_money | 待破解 | — | `unverified` |

### `seal_money` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `seal_money` | seal_money | 当前封单额，单位元。 | 元 | `verified` |
| 开盘红 · `seal_money` | max_seal | 封单金额；与 KPL max_seal 370 组、8 个交易日逐值一致 | 元 | `verified` |
| 开盘红(Levistock适配) · `seal_money` | seal_amount / seal_money | 待破解 | — | `unverified` |

### `sector` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2ex · `sector` | sector | 涨停池记录中的所属行业板块标签文本；项目直接映射自同源 Push2EX 字段 hybk。 | - | `verified` |
| 市场源(market_sources) · `sector` | — | — | — | `unverified` |

### `shares` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `shares` | shares | 总股本 | 股 | `verified` |
| 东财-datacenter(英文键) · `shares` | lockup_expiry.shares | 旧未限定短路径已退役。根据实际可流通量是否可用选择实际解禁量或报告总量。 完整路径：lockup_expiry.shares。多目标别名只用于说明路径拆分，不表示这些字段同义。 | — | `disproved` |

### `source` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `source` | — | — | — | `unverified` |
| 市场源(market_sources) · `source` | source | 数据来源标识 | — | `unverified` |

### `speed` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `speed` | — | — | — | `unverified` |
| 开盘啦(kpl) · `speed` | speed | 涨速 | — | `unverified` |

### `status` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `status` | status | 证券状态 | — | `verified` |
| 市场源(market_sources) · `status` | — | — | — | `unverified` |
| 开盘啦(kpl) · `status` | — | — | — | `unverified` |

### `stock_list` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `stock_list` | stock_list | 待破解 | — | `unverified` |
| 财联社(cls) · `stock_list` | cls_telegraph_related_stocks | 财联社电报条目附加的关联证券列表；列表项含证券代码与名称。空列表只表示该记录没有返回关联项，不推断正文未提及证券。列表项 pct 的单位、来源实际数据时点和是否固定为文章发布时状态尚未核实。 | — | `verified` |

### `subjects` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `subjects` | subjects / subject_name | 主题分类 | — | `unverified` |
| 财联社(cls) · `subjects` | cls_telegraph_subjects | 财联社电报条目关联的主题/题材标签列表；每项含官方主题 ID 与名称。该裁决不外推完整分类体系或标签互斥规则。 | — | `verified` |

### `themes` — ambiguous

聚合问题：meaning_differs；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 开盘红 · `themes` | themes | 题材标签列表；与 KPL sector 完整列表 360/370 一致、至少一项重合 369/370；保留来源标签口径差异 | — | `verified` |
| 开盘红(Levistock适配) · `themes` | themes | 题材 | — | `unverified` |

### `time` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `time` | time | 日K时间戳；按上海时区记录，本批样本时间为15:00 | ISO 8601 日期时间（Asia/Shanghai） | `verified` |
| 东财-热榜(em_hot) · `time` | time | 分钟时间点 | — | `verified` |
| 市场源(market_sources) · `time` | time | 时间 | — | `verified` |
| 开盘啦(kpl) · `time` | — | — | — | `unverified` |
| 财联社(cls) · `time` | cls_telegraph_publish_time | 财联社电报页面展示的发布时间。采集器将 CLS roll_data[].ctime（Unix 秒）格式化为 YYYY-MM-DD HH:MM:SS。当前主机按东八区输出。正文事件时间和采集开始时间另行记录。时间文本不代表采集目录目标数据日。 | 东八区本地日期时间文本（YYYY-MM-DD HH:MM:SS） | `verified` |

### `title` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `title` | — | — | — | `unverified` |
| reports · `title` | title | 研报标题 | — | `verified` |
| 巨潮(cninfo) · `title` | — | — | — | `unverified` |
| 财联社(cls) · `title` | title / brief | 标题 / 摘要 | — | `verified` |

### `total_shares` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `total_shares` | total_shares | 总股本；由 zong_gu_ben_raw_float（万股）乘 10000 得到 | 股 | `verified` |
| 开盘啦(kpl) · `total_shares` | — | — | — | `unverified` |

### `total_value` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2ex · `total_value` | push2ex.total_market_value | A股总市值；按总股本乘该涨停/跌停/炸板池记录的A股现价计算，输出单位元。 | 元 | `verified` |
| 市场源(market_sources) · `total_value` | — | — | — | `unverified` |

### `trade_date` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `trade_date` | trade_date | 连板天梯及题材强度结果对应的目标交易日；由 ShortlineIndicatorTable.target_trade_date 派生，题材强度 Helper 继承该日期 | 日期 | `verified` |
| 市场源(market_sources) · `trade_date` | — | — | — | `unverified` |
| 财联社(cls) · `trade_date` | trade_date / plates | 轮动日期 / 当日 top10 板块列表 | — | `unverified` |

### `tshare` — incomplete

聚合问题：unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `tshare` | tshare | 总市值 | — | `verified` |
| 东财-push2ex · `tshare` | tshare | 总市值 | 元 | `verified` |

### `turnover` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `turnover` | turnover | 成交额 | 元 | `verified` |
| 同花顺-fuyao · `turnover` | snapshot.turnover | 已退役的旧无分组来源路径；当前完整采集路径为 snapshot.turnover。本条只处置路径身份，不否定目标字段的语义或单位。 | 元 | `disproved` |
| 开盘啦(kpl) · `turnover` | — | — | — | `unverified` |
| 开盘红 · `turnover` | amount | 成交额；与 KPL amount 370 组、8 个交易日逐值一致 | 元 | `verified` |
| 开盘红(Levistock适配) · `turnover` | turnover / turnover_rate | 成交额 / 换手率% | — | `unverified` |
| 新浪(扩展API) · `turnover` | turnover | 换手率原始值（万分比；换算为百分数时原值除以100） | 万分比 | `verified` |

### `turnover_pct` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `turnover_pct` | tdx_get_quote_full.turnover_pct | 统一行情包装层的换手率值；当前 easy_tdx 快照模型不含该字段，值由 ZHB/Tencent 回退提供。官方 TQ fHSL 是另一接口路径，不自动映射。 | % | `disproved` |
| 开盘啦(kpl) · `turnover_pct` | turnover_pct | 换手率% | % | `unverified` |

### `turnover_rate` — ambiguous

聚合问题：canonical_differs；meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `turnover_rate` | turnover_rate | 换手率 | — | `verified` |
| 东财-push2ex · `turnover_rate` | limit_pool_turnover_rate | 东财涨停股池个股当日换手率；官方页面值以百分比显示。本裁决只确认该来源路径对应官方涨停池“换手率”列，不推断自由流通或其他计算口径。 | % | `verified` |
| 东财-热榜(em_hot) · `turnover_rate` | turnover_rate | 换手率% | — | `verified` |
| 开盘红 · `turnover_rate` | turnover_real | 实际换手率；与 KPL turnover_real 370 组、8 个交易日逐值一致 | % | `verified` |

### `turnover_real` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `turnover_real` | — | — | — | `unverified` |
| 开盘啦(kpl_limit_up_detail) · `turnover_real` | turnover_real | 实际换手率；与 KPH turnover_rate 两日逐值一致 | % | `verified` |

### `type` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `type` | lockup_expiry.type | 旧未限定短路径已退役。解禁适配器的规范化类别文本。 完整路径：lockup_expiry.type。多目标别名只用于说明路径拆分，不表示这些字段同义。 | — | `disproved` |
| 巨潮(cninfo) · `type` | — | — | — | `unverified` |
| 新浪(研报列表) · `type` | sina_research_report_category | 新浪研报列表中“报告类型”列的分类文本。 | 分类文本 | `verified` |

### `updated_date` — ambiguous

聚合问题：meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `updated_date` | updated_date | 财报更新日期 | YYYYMMDD | `verified` |
| TDX-eltdx(适配层) · `updated_date` | updated_date | 财务数据更新日期 | 日期字符串（样本格式 YYYY-MM-DD） | `verified` |

### `value` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `value` | — | — | — | `unverified` |
| 市场源(market_sources) · `value` | value | 待破解 | — | `unverified` |
| 开盘啦(kpl) · `value` | — | — | — | `unverified` |

### `vol` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `vol` | block_trade.vol | 旧未限定短路径已退役。get_block_trade 的成交股数输出，单位股。 完整路径：block_trade.vol。多目标别名只用于说明路径拆分，不表示这些字段同义。 | — | `disproved` |
| 开盘啦(kpl) · `vol` | — | — | — | `unverified` |

### `vol_ratio` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `vol_ratio` | tdx_get_quote_full.vol_ratio | 统一行情包装层从 Tencent 槽位透传的量比值；当前 TDX 快照模型不含该字段。其它来源的同名字段按其完整路径独立处理。 | — | `disproved` |
| 市场源(market_sources) · `vol_ratio` | — | — | — | `unverified` |
| 开盘啦(kpl) · `vol_ratio` | vol_ratio | 量比 | — | `unverified` |

### `volume` — ambiguous

聚合问题：canonical_differs；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `volume` | volume | 成交量 | 股 | `verified` |
| TDX(双命名源) · `volume` | volume | 成交量，按 AxData TDX 快照模型的源端行情口径返回；不表示当前项目采集路径 | — | `verified` |
| TDX-eltdx(适配层) · `volume` | volume | — | — | `unverified` |
| 同花顺-fuyao · `volume` | snapshot.volume | 已退役的旧无分组来源路径；当前完整采集路径为 snapshot.volume。本条只处置路径身份，不否定目标字段的语义或单位。 | 股 | `disproved` |

### `zong_zi_chan_raw_float` — ambiguous

聚合问题：meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `zong_zi_chan_raw_float` | zong_zi_chan_raw_float | 总资产原始值 | 千元 | `verified` |
| TDX-eltdx(适配层) · `zong_zi_chan_raw_float` | zong_zi_chan_raw_float | 总资产原始值；样本对应季报资产总计 | 千元 | `verified` |

### `zt_seal_amount_1d` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat2 · `zt_seal_amount_1d` | [6] | 前一交易日涨跌停封单额；涨停为正、跌停为负。 | 万元 | `verified` |
| 同花顺-fuyao · `zt_seal_amount_1d` | — | — | — | `unverified` |

### `zt_seal_amount_2d` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat2 · `zt_seal_amount_2d` | [8] | 前第二交易日涨跌停封单额；涨停为正、跌停为负。 | 万元 | `verified` |
| 同花顺-fuyao · `zt_seal_amount_2d` | — | — | — | `unverified` |

### `zt_time` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `zt_time` | — | — | — | `unverified` |
| 开盘啦(kpl_limit_up_detail) · `zt_time` | limit_time | 涨停时间；与 KPH limit_time 两日逐值一致 | Unix 秒 | `verified` |

## 疑似合并文本（启发式候选）

下列规范名或含义包含 `/`、`+`、`、`、分号、`或` 或 `兼`。分隔符可能只是正常描述格式，需结合原始路径和证据判断。

| 来源身份 | 完整 code path | 规范名 | 含义 | 状态 |
|:--|:--|:--|:--|:--|
| AxData | `data.auction_prev_volume_ratio` | data.auction_prev_volume_ratio | 今日开盘成交量 / 昨开盘成交量 | `verified` |
| AxData | `data.exchange` | data.exchange | AxData 交易所代码（SSE / SZSE / BSE） | `verified` |
| AxData | `data.free_float_shares` | data.free_float_shares | 流通股本 Z / 自由流通股本口径 | `verified` |
| AxData | `data.open_prev_amount_ratio` | data.open_prev_amount_ratio | 开盘金额 / 昨成交额 × 100 | `verified` |
| AxData | `data.open_prev_seal_ratio` | data.open_prev_seal_ratio | 开盘金额 / 昨封单额 × 100 | `verified` |
| AxData | `data.open_turnover_z` | data.open_turnover_z | 开盘成交量 / 流通股本 Z 口径 | `verified` |
| AxData | `data.open_volume_hand` | data.open_volume_hand | 按开盘金额 / 开盘价 / 100 估算的开盘成交量 | `verified` |
| AxData | `data.open_volume_ratio` | data.open_volume_ratio | 开盘成交量 / 近 5 个完整交易日平均每分钟成交量 | `verified` |
| AxData | `data.prev_seal_amount` | data.prev_seal_amount | 昨封单额；负值通常表示昨日收盘跌停封单 | `verified` |
| AxData | `data.seal_prev_ratio` | data.seal_prev_ratio | 当前封单额 / 昨封单额 | `verified` |
| AxData | `data.seal_to_amount_ratio` | data.seal_to_amount_ratio | 封单额 / 当前成交额 | `verified` |
| AxData | `data.seal_to_float_ratio` | data.seal_to_float_ratio | 封单额 / 流通市值 Z × 100 | `verified` |
| AxData | `data.stats_date` | data.stats_date | 历史统计分母日期，来自 tdxstat / tdxstat2 | `verified` |
| FTShare REST | `change_rate` | change_rate | 日涨跌幅；0.03 表示 3% | `verified` |
| FTShare REST | `close` | close | 收盘价/最新价 | `verified` |
| FTShare REST | `symbol_id` | symbol_id | FTShare A股行情列表返回中的六位证券代码字符串；与同一记录 symbol 去除交易所后缀后的数字部分相同。结论限于该接口及已观察 A 股样本，不推定为跨接口通用证券 ID。 | `verified` |
| TDX(双命名源) | `Date` | — | 日期键本身有效，但该旧 registry 身份未限定接口或父对象，无法唯一指向 K 线日、股本记录日、统计数据日或公式结果日。只退役裸路径身份；精确日期含义保存在接口级契约中。 | `disproved` |
| TDX(双命名源) | `ErrorId` | ErrorId | get_stock_info 官方样例响应中的 ErrorId 键；示例值为 0，完整错误码表及成功/失败映射未说明 | `verified` |
| TDX(双命名源) | `Inside` | Inside | 内盘；板块指数时表示跌停家数 | `verified` |
| TDX(双命名源) | `IsT0Fund` | IsT0Fund | 是否是 T+0 基金 | `verified` |
| TDX(双命名源) | `JZC` | JZC | 净资产/股东权益 | `verified` |
| TDX(双命名源) | `More_YJL` | More_YJL | ETF/LOF 溢价率 | `verified` |
| TDX(双命名源) | `Outside` | Outside | 外盘；板块指数时表示涨停家数 | `verified` |
| TDX(双命名源) | `ShapeValue` | ShapeValue | 短期形态+中期形态+长期形态编号 | `verified` |
| TDX(双命名源) | `Yield` | Yield | 应计利息(债券)/占款天数(回购) | `verified` |
| TDX(双命名源) | `amount_1d` | amount_1d | 旧版 tdx_get_quote_full() 返回键；2026-10-15 只见于 quote_full.amount_1d，20/20 同股值与 ZHB stat2.amount_1d 和合并对象 full.amount_1d 精确相同；同股 quote_raw 不含该键。当前 TDX 专用采集改用 tdx_get_quote_raw()，本审计仅撤销该历史样本对 TDX 原始字段归属的支持，不裁定业务语义；未来 raw 若出现该键须重新审查。 | `disproved` |
| TDX(双命名源) | `amount_2d` | amount_2d | 旧版 tdx_get_quote_full() 返回键；2026-10-15 只见于 quote_full.amount_2d，20/20 同股值与 ZHB stat2.amount_2d 和合并对象 full.amount_2d 精确相同；同股 quote_raw 不含该键。当前 TDX 专用采集改用 tdx_get_quote_raw()，本审计仅撤销该历史样本对 TDX 原始字段归属的支持，不裁定业务语义；未来 raw 若出现该键须重新审查。 | `disproved` |
| TDX(双命名源) | `amount_wan` | amount_wan | TDX 行情快照成交金额；由原始 amount 以元计值除以 10000 得到，输出单位为万元。 | `verified` |
| TDX(双命名源) | `average_price` | average_price | 均价；源端有值时返回（AxData TDX 实时快照模型语义；不表示当前项目采集路径） | `verified` |
| TDX(双命名源) | `b_vol` | b_vol | 外盘成交量（主动买入侧）；板块指数时表示涨停家数。 | `verified` |
| TDX(双命名源) | `baoliu2` | report_period_end_month | 财务记录对应的报告期末月份；本轮实测 6 对应 2026-06-30、9 对应 2026-09-30，其他月份和年份未验证 | `verified` |
| TDX(双命名源) | `bvps` | — | 旧英文别名登记，不是当前 TDX adapter 的原始响应路径；项目 0x0010 的 meigujingzichan 及 TQ FN4/J_mgjzc 是各自独立路径，本裁决不建立别名。 | `disproved` |
| TDX(双命名源) | `category_name` | category_name | ELTDX CapitalChangeRecord 中 XDXR 事件类别的可读名称；与 category_raw/category 类别编号区分。具体类别码表不在本次确认范围内。 | `verified` |
| TDX(双命名源) | `change_amt` | change_amt | TDX 行情快照涨跌额，即最新价减昨收价；价格单位为元/股。 | `verified` |
| TDX(双命名源) | `change_pct_1d` | change_pct_1d | 旧版 tdx_get_quote_full() 返回键；2026-10-15 只见于 quote_full.change_pct_1d，20/20 同股值与 ZHB stat.change_pct_1d 和合并对象 full.change_pct_1d 精确相同；同股 quote_raw 不含该键。当前 TDX 专用采集改用 tdx_get_quote_raw()，本审计仅撤销该历史样本对 TDX 原始字段归属的支持，不裁定业务语义；未来 raw 若出现该键须重新审查。 | `disproved` |
| TDX(双命名源) | `change_pct_2d` | change_pct_2d | 旧版 tdx_get_quote_full() 返回键；2026-10-15 只见于 quote_full.change_pct_2d，20/20 同股值与 ZHB stat.change_pct_2d 和合并对象 full.change_pct_2d 精确相同；同股 quote_raw 不含该键。当前 TDX 专用采集改用 tdx_get_quote_raw()，本审计仅撤销该历史样本对 TDX 原始字段归属的支持，不裁定业务语义；未来 raw 若出现该键须重新审查。 | `disproved` |
| TDX(双命名源) | `circulating_shares` | circulating_shares | 流通股本；由 liu_tong_gu_ben_raw_float（万股）乘 10000 得到 | `verified` |
| TDX(双命名源) | `date` | event_date | TDX XDXR（0x000f）权息/股本变迁事件日期；不是采集日期。现有契约未进一步区分公告日、股权登记日或除权除息日。 | `verified` |
| TDX(双命名源) | `dividend_history.bonus_ratio` | rights_issue_ratio | 配股股数与原股数之比；旧兼容键名 bonus_ratio 实际映射到 peigu，不是送股比例。 | `verified` |
| TDX(双命名源) | `dividend_history.bonus_rmb` | cash_dividend_per_share | 现金派息金额；项目适配器已按每股归一。 | `verified` |
| TDX(双命名源) | `dividend_history.date` | dividend_event_date | TDX XDXR 权息/股本变迁事件日期；现有契约未进一步限定公告日、登记日或除权除息日。 | `verified` |
| TDX(双命名源) | `dividend_history.transfer_ratio` | stock_bonus_transfer_ratio | 每股对应的送转股数；上游键 songzhuangu，不缩窄为单独转增。 | `verified` |
| TDX(双命名源) | `entrust_ratio` | tdx_get_quote_full.entrust_ratio | 统一行情包装层的委比值；当前 easy_tdx SecurityQuote 模型不含该字段，值只能来自包装层回退，不是本项目当前 TDX 原始快照字段。 | `disproved` |
| TDX(双命名源) | `eps` | eps_raw | 每股收益原始值（上游契约及现有可区分样本未确认基本/稀释子口径、报告期选择规则或小数精度/舍入规则） | `verified` |
| TDX(双命名源) | `float_capital` | reminders.latest_indicators.float_capital | 项目从 TDX F10「最新提示」中的“实际流通A股(万股)”文本解析并组装出的字段；不是 TDX 上游返回键。通达信 Quant 的 ActiveCapital 属于另一接口路径，不据名称相近建立别名。 | `disproved` |
| TDX(双命名源) | `float_mcap_yi` | tdx_get_quote_full.float_mcap_yi | 统一行情包装层的流通市值值（亿元）；来自 Tencent 行情回退，不是 TDX 原始快照字段。官方 TQ Ltsz 为另一接口路径，不自动映射。 | `disproved` |
| TDX(双命名源) | `get_gpjy_value.<GPxx>[].Date` | get_gpjy_value.<GPxx>[].Date | 个股交易/事件指标序列记录日期 | `verified` |
| TDX(双命名源) | `get_market_data.Date` | get_market_data.Date | K线记录日期；具体粒度由 period 指定 | `verified` |
| TDX(双命名源) | `gross_margin` | get_gross_margin_and_roe.gross_margin | 项目财务 helper 输出：优先解析 TDX F10“营业毛利率”，缺失时可按营业收入与营业成本计算或走新浪回退；不是单一 TDX 原始字段。官方 FN202“销售毛利率”是另一精确接口路径，未据此合并。 | `disproved` |
| TDX(双命名源) | `gudongrenshu` | gudongrenshu | 股东户数；样本对应发行人报告期末普通股股东总数，按来源计数口径记录。 | `verified` |
| TDX(双命名源) | `huobi_zijin` | — | 旧文档伪字段名，不是当前 TDX 0x0010 或行情原始响应键；TQ CashZJ 是另一精确接口代码，不自动映射。 | `disproved` |
| TDX(双命名源) | `inside_volume` | inside_volume | 内盘量（指数场景为跌停家数；AxData TDX 快照模型路径，官方概念为 Inside） | `verified` |
| TDX(双命名源) | `ipodate` | ipodate | ipo_date 的无下划线兼容别名，表示证券上市日期；不是报告或采集日期。 | `verified` |
| TDX(双命名源) | `jing_zichan` | jingzichan | 净资产 / 股东权益 | `verified` |
| TDX(双命名源) | `jingzichan` | jingzichan | 净资产 / 股东权益 | `verified` |
| TDX(双命名源) | `last_price` | last_price | 最新价或最新值（AxData TDX 实时快照模型语义；不表示当前项目采集路径） | `verified` |
| TDX(双命名源) | `latest_indicators` | reminders.latest_indicators | 项目从 TDX F10「最新提示」文本按标签和模式解析后组装的指标容器，不是上游独立响应字段；当前归档位置为 stocks.<code>.reminders.latest_indicators。此裁决只确认输出路径来源，不确认子项语义、报告期或单位。 | `disproved` |
| TDX(双命名源) | `limit_down` | tdx_get_quote_full.limit_down | 项目行情包装层按昨收和证券价格限制规则计算的跌停价（元）；可能在缺值时再由其他行情回退补充，不是 TDX wire 字段。 | `disproved` |
| TDX(双命名源) | `limit_down_price` | tdx_get_quote_full.limit_down_price | Tencent 行情槽位包装出的跌停价（元）；不是 TDX 原始响应字段。官方 TQ DTPrice 是另一接口的独立契约路径。 | `disproved` |
| TDX(双命名源) | `limit_up` | tdx_get_quote_full.limit_up | 项目行情包装层按昨收和证券价格限制规则计算的涨停价（元）；可能在缺值时再由其他行情回退补充，不是 TDX wire 字段。 | `disproved` |
| TDX(双命名源) | `locked_amount` | — | TDX(双命名源) 的旧错误来源身份；项目已验证的 locked_amount 属于 TDX-eltdx(适配层) 的不同来源/完整路径，不移植到此身份。 | `disproved` |
| TDX(双命名源) | `long_term_debt` | — | 旧文档伪路径；项目没有 TDX long_term_debt 原始字段。现存 changqifuzhai 等负债项不能改释为长期借款或长期债务。 | `disproved` |
| TDX(双命名源) | `market_snapshot` | — | 当前 TDX registry 中的未限定名称不是响应字段；TDX Quant 文档中的 market snapshot 是接口/方法概念，其他来源出现的同名容器必须按其来源及父级路径登记。 | `disproved` |
| TDX(双命名源) | `mcap_yi` | tdx_get_quote_full.mcap_yi | 统一行情包装层的总市值值（亿元）；来自 Tencent 行情回退，不是 TDX 原始快照字段。官方 TQ Zsz 为另一接口路径，不自动映射。 | `disproved` |
| TDX(双命名源) | `meigugongji` | — | 旧拼音伪路径，不是当前 TDX 0x0010 返回键；TQ J_mggjj 是另一接口精确字段，不证明本路径存在。 | `disproved` |
| TDX(双命名源) | `meiguweifenpei` | — | 旧拼音伪路径，不是当前 TDX 0x0010 返回键；TQ J_mgwfp 是另一接口精确字段，不证明本路径存在。 | `disproved` |
| TDX(双命名源) | `more_info` | — | 接口方法名的旧缩写 token，不是响应字段；官方接口名为 get_more_info_batch，返回键需逐个登记。 | `disproved` |
| TDX(双命名源) | `name` | tdx_get_quote_full.name | 统一行情包装层中的证券名称字段；TDX 快照 SecurityQuote 不含名称，当前包装值来自回退上下文。raw_eltdx 中的 name 是 global_helpers.realtime_rank.rows[].name 的另一来源/完整路径。 | `disproved` |
| TDX(双命名源) | `net_profit` | finance_info.jinglirun | 旧统一层别名，不是独立 TDX 原始路径；当前原始路径为 finance_info.jinglirun | `disproved` |
| TDX(双命名源) | `net_profit_yuan` | net_profit_yuan | 净利润金额；由 jing_li_run_raw_float（千元）乘 1000 得到 | `verified` |
| TDX(双命名源) | `outside_volume` | outside_volume | 外盘量（指数场景为涨停家数；AxData TDX 快照模型路径，官方概念为 Outside） | `verified` |
| TDX(双命名源) | `pb` | tdx_get_quote_full.pb | 统一行情包装层的市净率值；当前 TDX 快照模型没有 PB 字段，包装层可由 ZHB/Tencent 回退填充。官方 TQ PB_MRQ 是另一接口路径，不自动映射。 | `disproved` |
| TDX(双命名源) | `pe_lyr` | tdx_get_quote_full.pe_lyr | 统一行情包装层从 Tencent 静态 PE 槽位透传的值；当前 TDX 快照模型无该字段。官方 TQ MorePE 的口径按证券类型变化，不自动映射。 | `disproved` |
| TDX(双命名源) | `pe_static` | — | 已删除的重复包装输出键；代码自 2026-09-04 起只保留 pe_lyr，当前 TDX adapter/raw 也没有 pe_static 原始路径。 | `disproved` |
| TDX(双命名源) | `pe_ttm` | pe_ttm | 旧版 tdx_get_quote_full() 返回键；2026-10-15 只见于 quote_full.pe_ttm，20/20 同股值与 ZHB stat.pe_ttm 和合并对象 full.pe_ttm 精确相同；同股 quote_raw 不含该键。当前 TDX 专用采集改用 tdx_get_quote_raw()，本审计仅撤销该历史样本对 TDX 原始字段归属的支持，不裁定业务语义；未来 raw 若出现该键须重新审查。 | `disproved` |
| TDX(双命名源) | `pre_close` | pre_close | 前收盘价或上一期值（AxData TDX 实时快照模型语义；不表示当前项目采集路径） | `verified` |
| TDX(双命名源) | `quote_full.amount_1d` | quote_full.amount_1d | 历史复合采集回退值；保留期仅在 2026-10-15 记录中出现，逐值来自 ZHB。该路径不是通达信行情适配器字段。 | `disproved` |
| TDX(双命名源) | `quote_full.amount_2d` | quote_full.amount_2d | 历史复合采集回退值；保留期仅在 2026-10-15 记录中出现，逐值来自 ZHB。该路径不是通达信行情适配器字段。 | `disproved` |
| TDX(双命名源) | `quote_full.change_pct` | quote_full.change_pct | 涨跌幅；当前字段探针按 (price - last_close) / last_close * 100 派生，并非通达信行情适配器原始键。2026-10-15 的历史复合采集值来自 ZHB 回退。 | `disproved` |
| TDX(双命名源) | `quote_full.pe_ttm` | quote_full.pe_ttm | 历史复合采集回退值；保留期仅在 2026-10-15 记录中出现，逐值来自 ZHB。该路径不是通达信行情适配器字段。 | `disproved` |
| TDX(双命名源) | `reserve2` | report_period_end_month | 财务记录对应的报告期末月份；本轮实测 6 对应 2026-06-30、9 对应 2026-09-30，其他月份和年份未验证 | `verified` |
| TDX(双命名源) | `rise_speed` | rise_speed | 涨速百分比指标；具体计算窗口及与官方协议槽位的对应关系未确认（AxData TDX 快照模型语义，不证明当前项目采集路径） | `verified` |
| TDX(双命名源) | `roe` | get_gross_margin_and_roe.roe | 项目财务 helper 输出：优先解析 TDX F10“加权净资产收益率”，缺失时可能经财务公式或新浪数据回退；不是单一 TDX 原始字段。官方 FN281/J_jyl 属于各自接口的独立路径，未建立别名。 | `disproved` |
| TDX(双命名源) | `s_vol` | s_vol | 内盘成交量（主动卖出侧）；板块指数时表示跌停家数。 | `verified` |
| TDX(双命名源) | `shiyebianma` | — | 旧拼音/错字伪路径，不是当前 TDX 返回键；项目中的 industry 字段为独立路径，不据此建立别名。 | `disproved` |
| TDX(双命名源) | `short_term_debt` | — | 旧文档伪路径；项目没有 TDX short_term_debt 原始字段，liudongfuzhai 表示流动负债而非短期借款/短期债务。 | `disproved` |
| TDX(双命名源) | `total_assets_yuan` | total_assets_yuan | 总资产金额；由 zong_zi_chan_raw_float（千元）乘 1000 得到 | `verified` |
| TDX(双命名源) | `total_capital` | reminders.latest_indicators.total_capital | 项目从 TDX F10「最新提示」中的“总股本(万股)”文本解析并组装出的字段；不是 TDX 上游返回键。通达信 Quant 的 J_zgb 属于另一接口路径，不据名称相近建立别名。 | `disproved` |
| TDX(双命名源) | `total_shares` | total_shares | 总股本；由 zong_gu_ben_raw_float（万股）乘 10000 得到 | `verified` |
| TDX(双命名源) | `turnover_pct` | tdx_get_quote_full.turnover_pct | 统一行情包装层的换手率值；当前 easy_tdx 快照模型不含该字段，值由 ZHB/Tencent 回退提供。官方 TQ fHSL 是另一接口路径，不自动映射。 | `disproved` |
| TDX(双命名源) | `updateddate` | updateddate | updated_date 的无下划线兼容别名，表示该证券财务记录的更新日期；不等同报告期末、公告披露日、采集日或来源级数据日期。 | `verified` |
| TDX(双命名源) | `ushort` | — | 协议/编程类型 token，不是 JSON 响应字段或 TDX 采集路径。 | `disproved` |
| TDX(双命名源) | `vol_ratio` | tdx_get_quote_full.vol_ratio | 统一行情包装层从 Tencent 槽位透传的量比值；当前 TDX 快照模型不含该字段。其它来源的同名字段按其完整路径独立处理。 | `disproved` |
| TDX(双命名源) | `volume` | volume | 成交量，按 AxData TDX 快照模型的源端行情口径返回；不表示当前项目采集路径 | `verified` |
| TDX(双命名源) | `vzangsu` | vzangsu | 量涨速（官方未说明单位、计算窗口和算法） | `verified` |
| TDX(双命名源) | `zhuying_lirun` | zhuyinglirun | 营业成本；当前实证范围为非金融发行人合并利润表 2026 年第三季度年初至报告期末值。 | `verified` |
| TDX(双命名源) | `zhuying_shouru` | zhuyingshouru | 主营收入槽位；样本对应合并利润表“营业收入”行，不对应“营业总收入”合计。 | `verified` |
| TDX(双命名源) | `zhuyinglirun` | zhuyinglirun | 营业成本；当前实证范围为非金融发行人合并利润表 2026 年第三季度年初至报告期末值。 | `verified` |
| TDX(双命名源) | `zhuyinglyrun` | zhuyinglyrun | 财务输出值对应发行人合并利润表“营业成本”；当前官方报告核验样本为 2026 年第三季度年初至报告期末值。 | `verified` |
| TDX(双命名源) | `zhuyingshouru` | zhuyingshouru | 主营收入槽位；样本对应合并利润表“营业收入”行，不对应“营业总收入”合计。 | `verified` |
| TDX(双命名源) | `zongxianjinliu` | zongxianjinliu | 经营、投资、筹资活动产生的现金流量净额之和；不含汇率变动对现金及现金等价物的影响。 | `verified` |
| TDX-eltdx(适配层) | `adjust_mode` | adjust_mode | SDK 规范化的K线复权模式：none（不复权）、qfq（前复权）、hfq（后复权）、fixed_qfq（定点前复权）、fixed_hfq（定点后复权）。 | `verified` |
| TDX-eltdx(适配层) | `adjust_mode_raw` | adjust_mode_raw | K线复权模式的底层编号：0 不复权、1 前复权、2 后复权、3 定点前复权、4 定点后复权。 | `verified` |
| TDX-eltdx(适配层) | `amount` | amount | 实时行情快照截至该时点的累计成交额；收盘样本与同一数据日 K 线成交额一致。 | `verified` |
| TDX-eltdx(适配层) | `anchor_date` | anchor_date | 定点复权使用的锚定日期；仅 fixed_qfq 或 fixed_hfq 模式需要。 | `verified` |
| TDX-eltdx(适配层) | `anchor_date_raw` | anchor_date_raw | 定点复权日期的底层原始值；0 表示未使用。官方字段手册未说明非零值的具体编码格式。 | `verified` |
| TDX-eltdx(适配层) | `auction_matched_volume` | auction_matched_volume | 成交明细模型中的竞价匹配量占位字段，固定为 None；实际竞价匹配量由 auctions.series 的 AuctionPoint.matched_volume 提供 | `verified` |
| TDX-eltdx(适配层) | `auction_unmatched_signed_volume` | auction_unmatched_signed_volume | 成交明细模型中的带符号竞价未匹配量占位字段，固定为 None；实际未匹配量由 auctions.series 返回 | `verified` |
| TDX-eltdx(适配层) | `bao_liu_2_raw_float` | bao_liu_2_raw_float | 上游保留字段 2；未公开业务语义 | `verified` |
| TDX-eltdx(适配层) | `chang_qi_fu_zhai_raw_float` | chang_qi_fu_zhai_raw_float | 少数股东权益原始值（合并资产负债表口径；最近一期财务数据） | `verified` |
| TDX-eltdx(适配层) | `depth` | depth | 盘口强弱 / 盘口深度口径指标 | `verified` |
| TDX-eltdx(适配层) | `eltdx_seal_amount` | eltdx_seal_amount | 当前买一金额；仅已封板时解释为涨停封单额 | `verified` |
| TDX-eltdx(适配层) | `eltdx_seal_to_float_ratio` | eltdx_seal_to_float_ratio | 当前买一金额占自由流通市值Z比；仅已封板时解释为封板强度 | `verified` |
| TDX-eltdx(适配层) | `eps_raw` | eps_raw | 每股收益原始值；样本对应最近已披露报告期的年初至报告期末累计值，接口未区分基本与稀释口径 | `verified` |
| TDX-eltdx(适配层) | `event_kind` | event_kind | 成交记录事件分类标签：trade、auction_snapshot 或 opening_match | `verified` |
| TDX-eltdx(适配层) | `fa_qi_ren_fa_ren_gu_raw_float` | finance_batch[].fa_qi_ren_fa_ren_gu_raw_float | 未限定旧叶名；当前完整采集路径为 finance_batch[].fa_qi_ren_fa_ren_gu_raw_float，此无前缀身份不是独立输出字段。 | `disproved` |
| TDX-eltdx(适配层) | `fa_ren_gu_raw_float` | finance_batch[].fa_ren_gu_raw_float | 未限定旧叶名；当前完整采集路径为 finance_batch[].fa_ren_gu_raw_float，此无前缀身份不是独立输出字段。 | `disproved` |
| TDX-eltdx(适配层) | `finance_batch[].zhu_ying_li_run_raw_float` | finance_batch[].zhu_ying_li_run_raw_float | 营业成本原始值（保留样本对应报告营业成本；上游标签“主营利润”冲突） | `verified` |
| TDX-eltdx(适配层) | `finance_batch[].zong_xian_jin_liu_raw_float` | finance_batch[].zong_xian_jin_liu_raw_float | 总现金流（经营、投资、筹资活动净额之和，不含汇率影响） | `verified` |
| TDX-eltdx(适配层) | `finance_info_raw` | finance_info_raw | 0x0010 财务基础信息记录的原始主体；解码后为 136 字节，JSON 中以十六进制字符串保存 | `verified` |
| TDX-eltdx(适配层) | `gu_dong_ren_shu_raw_float` | gu_dong_ren_shu_raw_float | 股东人数（按股东账户计；具体有效报告期以来源记录为准） | `verified` |
| TDX-eltdx(适配层) | `guo_jia_gu_raw_float` | guo_jia_gu_raw_float | 国家股原始值（与发起人法人股、法人股为不同股本分类） | `verified` |
| TDX-eltdx(适配层) | `index` | index | ELTDX v3.3.2 TradeTick 当前返回页内的成交记录序号；与 absolute_index 的服务端全局序号区分。 | `verified` |
| TDX-eltdx(适配层) | `ipo_date_raw` | ipo_date_raw | 上市日期原始整数；YYYYMMDD 编码，不是采集来源数据日 | `verified` |
| TDX-eltdx(适配层) | `jing_li_run_raw_float` | jing_li_run_raw_float | 归属于上市公司股东的净利润原始值；样本对应报告期累计值 | `verified` |
| TDX-eltdx(适配层) | `last_close_price_milli` | last_close_price_milli | 前一根K线收盘价的千分之一元值；返回序列首条无前收盘字段 | `verified` |
| TDX-eltdx(适配层) | `last_price` | last_price | 最新价 / 现价 | `verified` |
| TDX-eltdx(适配层) | `leader_code` | leader_code | Helper 在目标交易日选出的该题材最高连板成分股完整证券代码；同高度时遵循连板天梯的封单金额降序、完整代码升序顺序。 | `verified` |
| TDX-eltdx(适配层) | `li_run_zong_he_raw_float` | li_run_zong_he_raw_float | 利润总额原始值；样本对应报告期累计值 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.alignment_status` | limit_ladder.alignment_status | 统计资源日期与目标交易日的对齐状态；v3.3.2 文档列举 same_day、previous_trading_day 等枚举值。 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.beta_60d` | limit_ladder.beta_60d | 近 60 日 Beta；相对 TDX 统计资源使用的市场基准，具体基准未公开 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.exchange` | limit_ladder.exchange | 该证券的交易所市场前缀代码；当前留存审计样本见 sh、sz。 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.float_market_value` | limit_ladder.float_market_value | 普通流通市值；普通流通股本乘当前行情价 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.float_shares` | limit_ladder.float_shares | 普通流通股本；财务快照口径 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.free_float_market_value` | limit_ladder.free_float_market_value | 自由流通市值；自由流通股本乘当前行情价 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.free_float_shares` | limit_ladder.free_float_shares | 自由流通股本；TDX 自由流通口径 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.ladder_level` | limit_ladder.ladder_level | 当前连续封住涨停的板数；仅 limit_status=sealed 时有值 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.limit_board_text` | limit_ladder.limit_board_text | 统计窗口天数与窗口内涨停次数构成的“几天几板”文本；统计资源日期为上一交易日且目标交易日封板时，展示会计入目标日 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.limit_stat_days` | limit_ladder.limit_stat_days | “几天几板”统计所用的窗口长度；ELTDX 从 tdxstat.cfg 直接读取 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.limit_up_count_in_stat_days` | limit_ladder.limit_up_count_in_stat_days | 涨停统计窗口内记录的涨停次数，是“几天几板”中的板数；ELTDX 从 tdxstat.cfg 直接读取 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.limit_up_streak_days` | limit_ladder.limit_up_streak_days | 统计文件日期记录的连续涨停天数原值；不自动把目标交易日计入。 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.open_prev_seal_ratio` | limit_ladder.open_prev_seal_ratio | 目标交易日 09:25 竞价成交金额 / 上一实际交易日统计资源记录的封单金额 × 100；返回百分比并保留分母符号。 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.open_turnover_z` | limit_ladder.open_turnover_z | 09:25 竞价成交量占自由流通股本 Z 的比例；Z 为自由流通口径 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.open_volume_ratio` | limit_ladder.open_volume_ratio | 开盘成交量相对最近 5 个完整交易日平均每分钟成交量的倍数；需至少 5 根完整日 K | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.pe_ttm` | limit_ladder.pe_ttm | 滚动市盈率；当前估值相对最近 12 个月利润的倍数 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.prev2_seal_amount` | limit_ladder.prev2_seal_amount | 目标交易日前第二个实际交易日统计资源记录的涨停封单金额；按交易日对齐 tdxstat2.cfg | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.prev_seal_amount` | limit_ladder.prev_seal_amount | 上一实际交易日统计资源记录的封单金额原值；上游文档称为昨日涨停封单金额。原值可带符号；负值方向语义未由文档解释。 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.seal_amount` | limit_ladder.seal_amount | 当前买一金额；封板时解释为封单额 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.seal_prev_ratio` | limit_ladder.seal_prev_ratio | 当前买一金额 / 上一实际交易日统计资源记录的封单金额；以倍数返回并保留分母符号，解读为封单强度时须同时确认当前已封板。 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.seal_to_amount_ratio` | limit_ladder.seal_to_amount_ratio | 当前买一金额相对当日成交额的倍数；只有已封板时才按封单成交额比解释 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.seal_to_float_ratio` | limit_ladder.seal_to_float_ratio | 当前买一金额占自由流通市值 Z 的比例；Z 为自由流通口径，只有已封板时才按封流比解释 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.year_limit_up_days` | limit_ladder.year_limit_up_days | 截至统计文件日期记录的当年累计涨停天数；统计文件日期落后目标日时不包含目标日新增结果 | `verified` |
| TDX-eltdx(适配层) | `limit_up_count` | limit_up_count | Helper 返回的目标交易日内，本次请求股票池中已封涨停且关联该题材的股票数；不含仅触板股票，也不是全市场计数。 | `verified` |
| TDX-eltdx(适配层) | `locked_amount` | locked_amount | 买一档挂单金额；按 bid1 × bid_vol1 × 100 计算，不等同涨停总封单金额 | `verified` |
| TDX-eltdx(适配层) | `open_delta_raw` | open_delta_raw | 日K开盘价相对前一根收盘价的协议差分值；返回序列首条无前收盘基准时以开盘价为基值 | `verified` |
| TDX-eltdx(适配层) | `opening_rush` | opening_rush | 开盘抢筹指标；算法及正负方向口径未公开 | `verified` |
| TDX-eltdx(适配层) | `order_count` | order_count | 成交明细中的原始笔数字段；集合竞价快照不赋予其未匹配量含义 | `verified` |
| TDX-eltdx(适配层) | `period_name` | period_name | ELTDX SDK 规范化后的K线周期名称，例如 day、1m。 | `verified` |
| TDX-eltdx(适配层) | `period_param_raw` | period_param_raw | K线周期的底层参数；固定周期通常为 1，扩展周期中的 N 表示 N 分钟、N 日或 N 秒。 | `verified` |
| TDX-eltdx(适配层) | `period_raw` | period_raw | K线周期的底层类型编号；需与 period_param_raw 配对解释，例如 4/1 表示日K、8/N 表示 N 分钟扩展周期。 | `verified` |
| TDX-eltdx(适配层) | `price` | price | 实时行情快照最新价；收盘阶段与该数据日收盘价一致。 | `verified` |
| TDX-eltdx(适配层) | `price_milli` | price_milli | ELTDX v3.3.2 TradeTick 成交价格的千分值；通常 price = price_milli / 1000。 | `verified` |
| TDX-eltdx(适配层) | `request_count` | request_count | K线请求条数元数据；单页结果记录请求条数，自动分页合并结果将其更新为合并后的K线总条数。 | `verified` |
| TDX-eltdx(适配层) | `seal_amount` | seal_amount | 当前买一档挂单金额；不代表涨停总封单金额 | `verified` |
| TDX-eltdx(适配层) | `shortline.beta_60d` | shortline.beta_60d | 近 60 日 Beta；相对 TDX 统计资源使用的市场基准，具体基准未公开 | `verified` |
| TDX-eltdx(适配层) | `shortline.ladder_level` | shortline.ladder_level | 当前连续封住涨停的板数；仅 limit_status=sealed 时有值 | `verified` |
| TDX-eltdx(适配层) | `shortline.limit_board_text` | shortline.limit_board_text | 统计窗口天数与窗口内涨停次数构成的“几天几板”文本；统计资源日期为上一交易日且目标交易日封板时，展示会计入目标日 | `verified` |
| TDX-eltdx(适配层) | `shortline.open_prev_seal_ratio` | shortline.open_prev_seal_ratio | 开盘额/昨封单额比 | `verified` |
| TDX-eltdx(适配层) | `shortline.open_turnover_z` | shortline.open_turnover_z | 09:25 竞价成交量占自由流通股本 Z 的比例；Z 为自由流通口径 | `verified` |
| TDX-eltdx(适配层) | `shortline.open_volume_ratio` | shortline.open_volume_ratio | 开盘成交量相对最近 5 个完整交易日平均每分钟成交量的倍数；需至少 5 根完整日 K | `verified` |
| TDX-eltdx(适配层) | `shortline.pe_ttm` | shortline.pe_ttm | 滚动市盈率；当前估值相对最近 12 个月利润的倍数 | `verified` |
| TDX-eltdx(适配层) | `shortline.prev2_seal_amount` | shortline.prev2_seal_amount | 目标交易日前第二个实际交易日统计资源记录的涨停封单金额；按交易日对齐 tdxstat2.cfg | `verified` |
| TDX-eltdx(适配层) | `shortline.seal_prev_ratio` | shortline.seal_prev_ratio | 封单/前封单比 | `verified` |
| TDX-eltdx(适配层) | `shortline.seal_to_amount_ratio` | shortline.seal_to_amount_ratio | 当前买一金额相对当日成交额的倍数；只有已封板时才按封单成交额比解释 | `verified` |
| TDX-eltdx(适配层) | `shortline.seal_to_float_ratio` | shortline.seal_to_float_ratio | 当前买一金额占自由流通市值 Z 的比例；Z 为自由流通口径，只有已封板时才按封流比解释 | `verified` |
| TDX-eltdx(适配层) | `shortline.year_limit_up_days` | shortline.year_limit_up_days | 截至统计文件日期记录的当年累计涨停天数；统计文件日期落后目标日时不包含目标日新增结果 | `verified` |
| TDX-eltdx(适配层) | `shui_hou_li_run_raw_float` | shui_hou_li_run_raw_float | 税后利润原始值；保留样本对应合并利润表的净利润行 | `verified` |
| TDX-eltdx(适配层) | `side` | side | 成交方向或状态标签：buy、sell、neutral 或状态名；完整数值状态码映射未确认 | `verified` |
| TDX-eltdx(适配层) | `status_raw` | status_raw | 成交明细方向或状态的原始值；具体状态码映射未在本裁决中扩展 | `verified` |
| TDX-eltdx(适配层) | `time` | time | 日K时间戳；按上海时区记录，本批样本时间为15:00 | `verified` |
| TDX-eltdx(适配层) | `time_label` | time_label | ELTDX v3.3.2 TradeTick 的成交时间文本；09:25 正式撮合接口中固定为 09:25。该字段不含来源日期。 | `verified` |
| TDX-eltdx(适配层) | `time_minutes` | time_minutes | ELTDX v3.3.2 TradeTick 的分钟数时间属性，与 time_label 一同描述逐笔记录时间；文档未明确分钟起算基准或 wire 编码。 | `verified` |
| TDX-eltdx(适配层) | `topic_id` | topic_id | 题材 ID；由参与聚合股票的 F10 题材关系提供，可为空；ID 缺失时 Helper 回退到题材名称作为分组键。 | `verified` |
| TDX-eltdx(适配层) | `topic_name` | topic_name | 题材名称；取自参与聚合股票的 F10 题材关系，作为聚合组的可读名称。 | `verified` |
| TDX-eltdx(适配层) | `total_seal_amount` | total_seal_amount | Helper 返回的目标交易日内，本次请求股票池中该题材封板成分股当前买一金额之和；单股金额缺失按 0，聚合值保留 6 位小数。共享题材股票会计入各自题材。 | `verified` |
| TDX-eltdx(适配层) | `tou_zi_shou_yu_raw_float` | tou_zi_shou_yu_raw_float | 投资收益；样本值对应报告期累计金额 | `verified` |
| TDX-eltdx(适配层) | `trade_date` | trade_date | 连板天梯及题材强度结果对应的目标交易日；由 ShortlineIndicatorTable.target_trade_date 派生，题材强度 Helper 继承该日期 | `verified` |
| TDX-eltdx(适配层) | `trade_datetime` | trade_datetime | ELTDX v3.3.2 TradeTick 的成交事件时间。历史 0x0fc6 接口按指定交易日返回成交时间；当日 0x0fc5 原始响应不带日期，因此 TradePage.trading_date 为空，trade_datetime 可为 None。它表示事件时间，不是采集时间，也不能单独代表来源数据日。文档未注明时区。 | `verified` |
| TDX-eltdx(适配层) | `trading_date` | trading_date | ELTDX v3.3.2 AuctionSeries 的历史请求日期元数据；当日请求返回 None。该字段记录请求日期角色，不证明服务器实际返回值对应的来源数据日，也不表示采集运行日期或事件日期。 | `verified` |
| TDX-eltdx(适配层) | `updated_date_raw` | updated_date_raw | 财务数据更新日期原始整数；YYYYMMDD 编码，不是采集来源数据日 | `verified` |
| TDX-eltdx(适配层) | `volume_wire_value` | volume_wire_value | 协议解码后的成交量值；普通A股单位为股，已验证的可转债品种单位为手 | `verified` |
| TDX-eltdx(适配层) | `zhu_ying_li_run_raw_float` | zhu_ying_li_run_raw_float | 营业成本原始值（保留样本对应报告营业成本；上游标签“主营利润”冲突） | `verified` |
| TDX-eltdx(适配层) | `zong_xian_jin_liu_raw_float` | zong_xian_jin_liu_raw_float | 总现金流；样本中对应经营、投资、筹资三类活动净现金流量之和，不含汇率变动影响 | `verified` |
| TDX-eltdx(适配层) | `zong_zi_chan_raw_float` | zong_zi_chan_raw_float | 总资产原始值；样本对应季报资产总计 | `verified` |
| ZHB-tdxstat | `[22]` | [22] | 形态/板块代码 ShapeValue | `verified` |
| ZHB-tdxstat | `[31]` | [31] | “几天几板”统计中的天数（通达信 LastStartZT，官方接口说明为“几天”；精确窗口边界未公开） | `verified` |
| ZHB-tdxstat | `[32]` | [32] | “几天几板”统计中的涨停板数（通达信 LastZTHzNum，官方接口说明为“几板”；精确统计口径未公开） | `verified` |
| ZHB-tdxstat | `[5]` | [5] | 连涨/连跌天数 | `verified` |
| ZHB-tdxstat | `[9]` | [9] | 市盈率（静态/LYR） | `verified` |
| ZHB-tdxstat | `change_30d` | change_20d | 与同来源同路径 change_20d 完全重复的历史兼容键，不是独立的 30 日涨跌幅 | `disproved` |
| ZHB-tdxstat | `change_60d_alt` | change_60d | 历史解析键；当前解析器将 tdxstat.cfg 第[20]列输出为 change_60d，change_60d_alt 不再是独立输出路径。 | `disproved` |
| ZHB-tdxstat | `change_ytd` | change_ytd | 年初至今涨跌幅（YTD，%）；历史对照支持该字段类别，但复权基准未证实与其他来源相同。 | `verified` |
| ZHB-tdxstat | `pe_lyr` | pe_lyr | 静态市盈率（LYR/上一完整年度业绩口径）；180 组、9 个来源日期与已验证静态 PE 参照相符，最大差 0.006 倍；精度差异不证明跨源逐值相同。 | `verified` |
| ZHB-tdxstat | `stat.change_30d` | stat.change_20d | 与同来源同路径 stat.change_20d 完全重复的历史兼容键，不是独立的 30 日涨跌幅 | `disproved` |
| ZHB-tdxstat | `stat.streak_days` | stat.streak_days | 连涨/连跌天数（正值为连涨，负值为连跌） | `verified` |
| ZHB-tdxstat | `stat.zt_type_code` | stat.zt_type_code | 行情状态/涨跌强度分档码 | `verified` |
| ZHB-tdxstat | `streak_days` | streak_days | 连涨/连跌天数（正值为连涨，负值为连跌） | `verified` |
| ZHB-tdxstat2 | `[13]` | [13] | 通达信板块归属(881=行业板块稳定 / 880=概念·风格板块动态) | `verified` |
| ZHB-tdxstat2 | `change_250k_bar` | change_250d_return | 近250根日K线滚动涨跌幅；复权方式、窗口端点和细部基准未确认跨源一致。 | `verified` |
| ZHB-tdxstat2 | `change_30k_bar` | change_30d_return | 30 个收盘价样本的累计涨跌幅，以目标数据日之前第 29 根日 K 收盘价为基准：100 × (C[t] / C[t-29] - 1)；前复权公开日 K 对照 95/100 组误差不超过 0.01 个百分点，600825 的五组偏差未解释。 | `verified` |
| ZHB-tdxstat2 | `change_30k_bar_ref` | change_30bar_lag30_return | 目标数据日收盘价相对之前第 30 根日 K 收盘价的累计涨跌幅：100 × (C[t] / C[t-30] - 1)；前复权公开日 K 对照 95/100 组误差不超过 0.01 个百分点，600825 的五组偏差未解释。 | `verified` |
| ZHB-tdxstat2 | `high_52w` | stat2.high_52w | 52周最高价；full.high_52w 是 stat2.high_52w 的直接合并别名。 | `verified` |
| ZHB-tdxstat2 | `industry_code` | tdx_board_code | 当日通达信板块归属代码；样本包含行业类与主题/风格类板块，不是行业专属代码。 | `verified` |
| ZHB-tdxstat2 | `main_net_buy_amount` | [14] | 当日开盘集合竞价成交额；历史兼容键，不表示主力净流入额。 | `verified` |
| ZHB-tdxstat2 | `main_net_buy_amount_1d` | [15] | 前一交易日开盘集合竞价成交额；历史兼容键，不表示主力净流入额。 | `verified` |
| ZHB-tdxstat2 | `main_net_buy_hands` | [9] | 当日开盘集合竞价成交量；历史兼容键，不表示主力净买入手数。 | `verified` |
| ZHB-tdxstat2 | `main_net_buy_hands_1d` | [10] | 前一交易日开盘集合竞价成交量；历史兼容键，不表示主力净买入手数。 | `verified` |
| ZHB-tdxstat2 | `stat2.change_250k_bar` | change_250d_return | 近250根日K线滚动涨跌幅；复权方式、窗口端点和细部基准未确认跨源一致。 | `verified` |
| ZHB-tdxstat2 | `stat2.change_30k_bar` | change_30d_return | 30 个收盘价样本的累计涨跌幅，以目标数据日之前第 29 根日 K 收盘价为基准：100 × (C[t] / C[t-29] - 1)；前复权公开日 K 对照 95/100 组误差不超过 0.01 个百分点，600825 的五组偏差未解释。 | `verified` |
| ZHB-tdxstat2 | `stat2.change_30k_bar_ref` | change_30bar_lag30_return | 目标数据日收盘价相对之前第 30 根日 K 收盘价的累计涨跌幅：100 × (C[t] / C[t-30] - 1)；前复权公开日 K 对照 95/100 组误差不超过 0.01 个百分点，600825 的五组偏差未解释。 | `verified` |
| ZHB-tdxstat2 | `stat2.industry_code` | tdx_board_code | 当日通达信板块归属代码；样本包含行业类与主题/风格类板块，不是行业专属代码。 | `verified` |
| ZHB-tdxstat2 | `stat2.main_net_buy_amount` | [14] | 当日开盘集合竞价成交额；历史兼容键，不表示主力净流入额。 | `verified` |
| ZHB-tdxstat2 | `stat2.main_net_buy_amount_1d` | [15] | 前一交易日开盘集合竞价成交额；历史兼容键，不表示主力净流入额。 | `verified` |
| ZHB-tdxstat2 | `stat2.main_net_buy_hands` | [9] | 当日开盘集合竞价成交量；历史兼容键，不表示主力净买入手数。 | `verified` |
| ZHB-tdxstat2 | `stat2.main_net_buy_hands_1d` | [10] | 前一交易日开盘集合竞价成交量；历史兼容键，不表示主力净买入手数。 | `verified` |
| ZHB-tdxstat2 | `stat2.zt_seal_amount` | [4] | 当日涨跌停封单额；涨停为正、跌停为负。 | `verified` |
| ZHB-tdxstat2 | `stat2.zt_seal_amount_1d` | [6] | 前一交易日涨跌停封单额；涨停为正、跌停为负。 | `verified` |
| ZHB-tdxstat2 | `stat2.zt_seal_amount_2d` | [8] | 前第二交易日涨跌停封单额；涨停为正、跌停为负。 | `verified` |
| ZHB-tdxstat2 | `zt_seal_amount` | [4] | 当日涨跌停封单额；涨停为正、跌停为负。 | `verified` |
| ZHB-tdxstat2 | `zt_seal_amount_1d` | [6] | 前一交易日涨跌停封单额；涨停为正、跌停为负。 | `verified` |
| ZHB-tdxstat2 | `zt_seal_amount_2d` | [8] | 前第二交易日涨跌停封单额；涨停为正、跌停为负。 | `verified` |
| ZHB-tipinfo | `[13]` | [13] | 对应限售股解禁/上市流通事件的日期，原始格式为 YYYYMMDD。两项发行人公告样本确认其为事件日期；多事件时的选取规则尚未确认。 | `verified` |
| ZHB-tipinfo | `[14]` | [14] | 对应限售股上市流通事件的股份数量，单位万股。两个公告样本均与事件总数量吻合，ZHB 值按 0.01 万股粒度保留；多事件或分项数量的选取规则尚未确认。 | `verified` |
| ZHB-tipinfo | `[21]` | [21] | 股权激励预案/草案公告日 | `verified` |
| ZHB-tipinfo | `[3]` | [3] | 报告期累计每股收益（基本/稀释/扣非口径未区分） | `verified` |
| ZHB-tipinfo | `[8]` | tipinfo.shareholder_change_date | 股东持股变动记录关联日期；可为交易日、区间截止日或权益变动协议签署日 | `verified` |
| ZHB-tipinfo | `[9]` | tipinfo.shareholder_change_shares_wan | 股东持股变动数量；正值为增持/转入，负值为减持/转出 | `verified` |
| ZHB-tipinfo | `div_amount` | shareholder_change_shares_wan | 股东持股变动数量；正值为增持/转入，负值为减持/转出 | `disproved` |
| ZHB-tipinfo | `div_date` | shareholder_change_date | 股东持股变动记录关联日期；可为交易日、区间截止日或权益变动协议签署日 | `disproved` |
| ZHB-tipinfo | `eps` | eps | 报告期累计每股收益（基本/稀释/扣非口径未区分） | `verified` |
| ZHB-tipinfo | `equity_incentive_date` | equity_incentive_date | 股权激励预案/草案公告日 | `verified` |
| ZHB-tipinfo | `shareholder_change_date` | shareholder_change_date | 股东持股变动记录关联日期；可为交易日、区间截止日或权益变动协议签署日 | `verified` |
| ZHB-tipinfo | `shareholder_change_shares_wan` | shareholder_change_shares_wan | 股东持股变动数量；正值为增持/转入，负值为减持/转出 | `verified` |
| ZHB-tipinfo | `tipinfo.div_amount` | tipinfo.shareholder_change_shares_wan | 股东持股变动数量；正值为增持/转入，负值为减持/转出 | `disproved` |
| ZHB-tipinfo | `tipinfo.div_date` | tipinfo.shareholder_change_date | 股东持股变动记录关联日期；可为交易日、区间截止日或权益变动协议签署日 | `disproved` |
| ZHB-tipinfo | `tipinfo.equity_incentive_date` | tipinfo.equity_incentive_date | 股权激励预案/草案公告日 | `verified` |
| ZHB-tipinfo | `tipinfo.shareholder_change_date` | tipinfo.shareholder_change_date | 股东持股变动记录关联日期；可为交易日、区间截止日或权益变动协议签署日 | `verified` |
| ZHB-tipinfo | `tipinfo.shareholder_change_shares_wan` | tipinfo.shareholder_change_shares_wan | 股东持股变动数量；正值为增持/转入，负值为减持/转出 | `verified` |
| reports | `BUY_RATIO` | BUY_RATIO / SELL_RATIO | 买入/卖出占比 | `unverified` |
| reports | `BUY_SEAT` | BUY_SEAT / SELL_SEAT | 买入/卖出前5席位数 | `unverified` |
| reports | `NextTwoYear` | predictThisYearEps / NextYear / NextTwoYear | 今年/明年/后年 EPS 预测 | `verified` |
| reports | `NextYear` | predictThisYearEps / NextYear / NextTwoYear | 今年/明年/后年 EPS 预测 | `verified` |
| reports | `RQJMG` | RZJME / RQJMG | 融资净买入 / 融券净卖出 | `unverified` |
| reports | `RZJME` | RZJME / RQJMG | 融资净买入 / 融券净卖出 | `unverified` |
| reports | `SELL_RATIO` | BUY_RATIO / SELL_RATIO | 买入/卖出占比 | `unverified` |
| reports | `SELL_SEAT` | BUY_SEAT / SELL_SEAT | 买入/卖出前5席位数 | `unverified` |
| reports | `actualLastTwoYearEps` | actualLastYearEps | 保留期内全部非空样本与同条 actualLastYearEps 完全重复；不能作为独立的前两年实际 EPS 字段（当前接口响应行为） | `disproved` |
| reports | `actualLastYearEps` | 上一年度实际每股收益 | 东方财富 report/list 研报记录中对应报告发布日期之前一完整会计年度的实际 EPS，单位元/股。该字段为东方财富研报口径；不等同发行人按加权平均普通股数披露的法定基本/稀释 EPS。股本变化可能导致历史每股值采用不同分母；本裁决不确认统一分母算法。 | `verified` |
| reports | `adjunctSize` | adjunctSize / adjunctType | 附件大小/类型 | `unverified` |
| reports | `adjunctType` | adjunctSize / adjunctType | 附件大小/类型 | `unverified` |
| reports | `analyse` | analyse / analyse_title | 待破解 | `unverified` |
| reports | `analyse_title` | analyse / analyse_title | 待破解 | `unverified` |
| reports | `attachSize` | 研报 PDF 附件大小 | 东方财富研报记录所链接 PDF 附件的大小；当前接口整数值等于所测 PDF Content-Length 字节数除以 1,024 后向下取整。 | `verified` |
| reports | `attachType` | 研报附件类型代码 | 东方财富 report/list 研报记录中的附件类型代码。保留样本只观察到代码 0；三条按股票和 infoCode 精确绑定的东方财富详情页均链接至 PDF 原文，支持本样本中 0 对应 PDF 附件。其他未观察或未解码的代码不作推断。 | `verified` |
| reports | `author` | report_author_id_name_list | 研报作者列表；每项由作者 ID 和姓名组成，原始格式为“ID.姓名”。 | `verified` |
| reports | `column` | column | 东方财富个股研报栏目代码；保留样本观测 11 个代码，其中 002004003 对应新股研报栏目；其余代码释义未扩展。 | `verified` |
| reports | `emRatingCode` | emRatingCode | 东财统一评级类别代码；与同记录 emRatingName 关联，完整代码表未知。 | `verified` |
| reports | `emRatingValue` | emRatingValue | 东财研报 API 统一评级的数值档位；本次留存样本观察到 1=持有、2=增持、3=买入，不推断未观察到的其他数值。 | `verified` |
| reports | `indvAimPriceL` | 研报目标价区间下限 | 东方财富 report/list 研报记录中目标价或合理估值区间的下端点；若报告仅给出单一目标价，接口可表现为 L=T。该字段不代表当前股价或分析师目标价共识。 | `verified` |
| reports | `indvAimPriceT` | 研报目标价区间上限 | 东方财富 report/list 研报记录中目标价或合理估值区间的上端点；若报告仅给出单一目标价，接口可表现为 L=T。该字段不代表当前股价或分析师目标价共识。 | `verified` |
| reports | `indvIsNew` | indvIsNew | 东财个股研报的新股研报栏目标记；观测到 002=新股研报（column=002004003）、001=其他个股研报栏目；空值保持缺失，不外推未观察的代码。 | `verified` |
| reports | `newIssuePrice` | 首次公开发行价格 | 该股票首次公开发行（IPO）的发行价格；逐值对应东方财富 F10 ISSUE_PRICE。 | `verified` |
| reports | `newListingDate` | 上市日期 | 该股票在交易所上市交易的日期；逐值对应东方财富 F10 LISTING_DATE。空值表示 reportapi 记录未返回日期，不表示股票没有上市。 | `verified` |
| reports | `newPeIssueA` | 首次公开发行市盈率 | 该股票首次公开发行时的发行市盈率；逐值对应东方财富 F10 AFTER_ISSUE_PE。 | `verified` |
| reports | `orgId` | secName / orgId | 证券名 / 机构ID | `unverified` |
| reports | `predictNextTwoYearPe` | predictNextTwoYearPe | 东方财富 report/list 研报记录中，currentYear 后第 2 年的预测市盈率。 | `verified` |
| reports | `predictNextYearPe` | predictNextYearPe | 东方财富 report/list 研报记录中，currentYear 后第 1 年的预测市盈率。 | `verified` |
| reports | `predictThisYearPe` | predictThisYearPe | 东方财富 report/list 研报记录中，与响应 currentYear 同年度的预测市盈率。 | `verified` |
| reports | `reading_num` | reading_num / share_num | 阅读数/分享数 | `unverified` |
| reports | `sRatingCode` | sRatingCode | 机构原始评级类别代码；须结合机构和同记录 sRatingName 解释，未确立跨机构代码表。 | `verified` |
| reports | `secName` | secName / orgId | 证券名 / 机构ID | `unverified` |
| reports | `share_num` | reading_num / share_num | 阅读数/分享数 | `unverified` |
| reports | `subject_name` | subjects / subject_name | 主题分类 | `unverified` |
| reports | `subjects` | subjects / subject_name | 主题分类 | `unverified` |
| 东财-clist | `f104` | f104 / f105 | 上涨 / 下跌家数 | `verified` |
| 东财-clist | `f105` | f104 / f105 | 上涨 / 下跌家数 | `verified` |
| 东财-clist | `f109` | f109 / f160 | 涨跌幅 | `verified` |
| 东财-clist | `f141` | clist_leader_stock_market_id | 领涨股票的市场编号；与 f140 股票代码组合成东方财富 unify/r/{market}.{code} 行情路由。 | `verified` |
| 东财-clist | `f160` | f109 / f160 | 涨跌幅 | `verified` |
| 东财-clist | `f164` | f164 / f165 | 主力净额 | `verified` |
| 东财-clist | `f165` | f164 / f165 | 主力净额 | `verified` |
| 东财-clist | `f174` | f174 / f175 | 主力净额 | `verified` |
| 东财-clist | `f175` | f174 / f175 | 主力净额 | `verified` |
| 东财-clist | `f208` | clist_loser_stock_code | 领跌股票的证券代码；与 f207 名称和 f209 市场编号组成同一领跌股票链接。 | `verified` |
| 东财-clist | `f209` | clist_loser_stock_market_id | 领跌股票的市场编号；与 f208 股票代码组合成东方财富 unify/r/{market}.{code} 行情路由。 | `verified` |
| 东财-clist | `f257` | clist.f257 | 板块 3 日/5 日统计行关联证券简称；东方财富页面脚本将 f257 映射为 zdname。脚本未公开关联对象选择规则，不据此称为领涨股。 | `verified` |
| 东财-clist | `f258` | clist.f258 | 板块 3 日/5 日统计行中与 f257 关联的六位证券代码；东方财富页面脚本将 f258 映射为 zdcode。脚本未公开关联对象选择规则。 | `verified` |
| 东财-clist | `f259` | clist_associated_security_market_id | 同一板块统计行中与 f258 证券代码对应的东方财富行情路由市场编号；本批观察到 0 与 1，未观察值不作外推。 | `verified` |
| 东财-clist | `f66` | f66 / f72 / f78 / f84 | 超大/大/中/小单净额 | `verified` |
| 东财-clist | `f72` | f66 / f72 / f78 / f84 | 超大/大/中/小单净额 | `verified` |
| 东财-clist | `f78` | f66 / f72 / f78 / f84 | 超大/大/中/小单净额 | `verified` |
| 东财-clist | `f84` | f66 / f72 / f78 / f84 | 超大/大/中/小单净额 | `verified` |
| 东财-datacenter(英文键) | `BILLBOARD_BUY_AMT` | BILLBOARD_BUY_AMT / SELL_AMT | 买入/卖出资 | `verified` |
| 东财-datacenter(英文键) | `BUY` | BUY / SELL | 买入额 / 卖出额 | `verified` |
| 东财-datacenter(英文键) | `BUYER_NAME` | BUYER_NAME / SELLER_NAME | 买方 / 卖方营业部 | `verified` |
| 东财-datacenter(英文键) | `CHANGE_RATE` | CLOSE_PRICE / CHANGE_RATE | 收盘价 / 涨跌幅 | `verified` |
| 东财-datacenter(英文键) | `DEAL_PRICE` | DEAL_PRICE / CLOSE_PRICE | 成交价 / 收盘价 | `verified` |
| 东财-datacenter(英文键) | `HOLDER_TOTAL_NUM` | shareholder_account_count | 股东户数；统计截止日由同一响应的 END_DATE 指定。 | `verified` |
| 东财-datacenter(英文键) | `RQCHL` | RQMCL / RQCHL | 融券卖出 / 偿还量 | `verified` |
| 东财-datacenter(英文键) | `RQMCL` | RQMCL / RQCHL | 融券卖出 / 偿还量 | `verified` |
| 东财-datacenter(英文键) | `RZCHE` | RZMRE / RZCHE | 融资买入 / 偿还额 | `verified` |
| 东财-datacenter(英文键) | `RZMRE` | RZMRE / RZCHE | 融资买入 / 偿还额 | `verified` |
| 东财-datacenter(英文键) | `SECURITY_CODE` | SECURITY_CODE / SECURITY_NAME_ABBR | 代码 / 名称 | `verified` |
| 东财-datacenter(英文键) | `SECURITY_NAME_ABBR` | SECURITY_CODE / SECURITY_NAME_ABBR | 代码 / 名称 | `verified` |
| 东财-datacenter(英文键) | `SELL` | BUY / SELL | 买入额 / 卖出额 | `verified` |
| 东财-datacenter(英文键) | `SELLER_NAME` | BUYER_NAME / SELLER_NAME | 买方 / 卖方营业部 | `verified` |
| 东财-datacenter(英文键) | `SELL_AMT` | BILLBOARD_BUY_AMT / SELL_AMT | 买入/卖出资 | `verified` |
| 东财-datacenter(英文键) | `able_shares` | lockup_expiry.able_shares | 旧未限定短路径已退役。解禁适配器归一输出；来源可能为 TDX F10 或 Eastmoney 回退。 完整路径：lockup_expiry.able_shares。多目标别名只用于说明路径拆分，不表示这些字段同义。 | `disproved` |
| 东财-datacenter(英文键) | `block_trade.amount` | block_trade_amount | 大宗交易成交金额；页面按万元显示，接口适配器输出元。 | `verified` |
| 东财-datacenter(英文键) | `block_trade.premium_pct` | block_trade_premium_pct | 项目计算折溢率 round((成交价/收盘价-1)*100, 2)；收盘价为 0 时返回 0。 这是项目归一化/计算的采集输出，不是提供方原始字段。 | `disproved` |
| 东财-datacenter(英文键) | `block_trade.vol` | block_trade_volume | 大宗交易成交股数；页面按万股显示，接口适配器输出股。 | `verified` |
| 东财-datacenter(英文键) | `bonus_ratio` | BONUS_RATIO | 旧未限定短路径已退役。旧 Eastmoney RPT_SHAREBONUS_DET 原始键；当前分红 getter 已切换 TDX，另见 TDX dividend_history.bonus_ratio，二者不映射。 完整路径：BONUS_RATIO。多目标别名只用于说明路径拆分，不表示这些字段同义。 | `disproved` |
| 东财-datacenter(英文键) | `bonus_rmb` | PRETAX_BONUS_RMB | 旧未限定短路径已退役。旧 Eastmoney RPT_SHAREBONUS_DET 原始键；当前分红 getter 已切换 TDX，另见 TDX dividend_history.bonus_rmb，二者不映射。 完整路径：PRETAX_BONUS_RMB。多目标别名只用于说明路径拆分，不表示这些字段同义。 | `disproved` |
| 东财-datacenter(英文键) | `change_num` | HOLDER_NUM_CHANGE | 旧未限定短路径已退役。旧 RPT_HOLDERNUMLATEST 上游列；当前 holder_change 的变化户数由相邻报告期项目计算。 完整路径：HOLDER_NUM_CHANGE。多目标别名只用于说明路径拆分，不表示这些字段同义。 | `disproved` |
| 东财-datacenter(英文键) | `change_ratio` | change_ratio_legacy_flat_alias | 旧未限定短路径已退役。同名曾混合北向持仓行对应证券涨跌幅与旧股东户数环比字段，语义不同，分别保留。 完整路径：northbound_hold.change_ratio; HOLDER_NUM_RATIO。多目标别名只用于说明路径拆分，不表示这些字段同义。 | `disproved` |
| 东财-datacenter(英文键) | `date` | date_legacy_flat_alias | 旧未限定短路径已退役。旧扁平日期短名混合交易日、持仓日、解禁事件日、股东报告截止日和旧分红事件日；不再作为单一字段身份。 完整路径：margin_trading.date; northbound_hold.date; lockup_expiry.date; block_trade.date; holder_fetch_em.date; EX_DIVIDEND_DATE。多目标别名只用于说明路径拆分，不表示这些字段同义。 | `disproved` |
| 东财-datacenter(英文键) | `free_shares` | lockup_expiry.free_shares | 旧未限定短路径已退役。完整输出路径；由适配器将来源万股值换算为股，不是 Eastmoney 原始键。 完整路径：lockup_expiry.free_shares。多目标别名只用于说明路径拆分，不表示这些字段同义。 | `disproved` |
| 东财-datacenter(英文键) | `holder_fetch_em.date` | holder_report_date | 股东户数统计截止日；是报告期截止日期，不是采集日。 | `verified` |
| 东财-datacenter(英文键) | `holder_num` | holder_num_legacy_flat_alias | 旧未限定短路径已退役。当前 RPT_F10_EH_HOLDERNUM 使用 HOLDER_TOTAL_NUM；旧 RPT_HOLDERNUMLATEST 原始键为 HOLDER_NUM。 完整路径：holder_fetch_em.holder_num; HOLDER_NUM。多目标别名只用于说明路径拆分，不表示这些字段同义。 | `disproved` |
| 东财-datacenter(英文键) | `lockup_expiry.able_shares` | lockup_actual_tradable_shares | 实际可流通解禁数量，Eastmoney 输入万股转股；来源或数值不可用时为空。 这是项目归一化/计算的采集输出，不是提供方原始字段。 | `disproved` |
| 东财-datacenter(英文键) | `lockup_expiry.date` | lockup_event_date | 事件日期由 TDX F10/Eastmoney 字段解析并规范化；不等同采集日。 这是项目归一化/计算的采集输出，不是提供方原始字段。 | `disproved` |
| 东财-datacenter(英文键) | `lockup_expiry.free_shares` | lockup_total_shares | 报告解禁总量；统一适配器将来源万股转为股。 这是项目归一化/计算的采集输出，不是提供方原始字段。 | `disproved` |
| 东财-datacenter(英文键) | `lockup_expiry.ratio` | lockup_ratio_pct | 解禁比例；0 到 1 的输入按小数转百分数，输出保留两位小数。 这是项目归一化/计算的采集输出，不是提供方原始字段。 | `disproved` |
| 东财-datacenter(英文键) | `lockup_expiry.shares` | lockup_shares_selected | 适配器按 able_shares 可用性选择实际可流通解禁量，否则使用报告解禁总量；万股转股。 这是项目归一化/计算的采集输出，不是提供方原始字段。 | `disproved` |
| 东财-datacenter(英文键) | `lockup_expiry.shares_is_actual` | lockup_shares_is_actual | 项目标记 shares 是否取实际可流通解禁量；不是上游原始字段。 这是项目归一化/计算的采集输出，不是提供方原始字段。 | `disproved` |
| 东财-datacenter(英文键) | `lockup_expiry.type` | lockup_event_type | 解禁类型的统一适配器输出，输入可能来自 TDX F10 或 Eastmoney FREE_SHARES_TYPE。 这是项目归一化/计算的采集输出，不是提供方原始字段。 | `disproved` |
| 东财-datacenter(英文键) | `margin_trading` | margin_trading | collect_datacenter 在 stocks.<code>.margin_trading 写入 list/dict，是对象容器。 这是序列化对象边界，不是业务字段。 | `disproved` |
| 东财-datacenter(英文键) | `margin_trading.date` | margin_trade_date | 融资融券交易明细所属交易日；取原始 DATE 的前 10 位，不是采集运行日。 | `verified` |
| 东财-datacenter(英文键) | `northbound_hold` | northbound_hold | collect_datacenter 在 stocks.<code>.northbound_hold 写入 list/dict，是对象容器。 这是序列化对象边界，不是业务字段。 | `disproved` |
| 东财-datacenter(英文键) | `northbound_hold.change_shares` | northbound_hold.change_shares | 直接核验的 600519、601288 两条 2026-09-30 响应均未提供 CHANGE_SHARES；旧适配器将缺失填为 0，本路径是项目占位输出，不代表持股未变化。 | `disproved` |
| 东财-datacenter(英文键) | `northbound_hold.hold_ratio` | northbound_hold.hold_ratio | 北向持股比例（当前接口样本优先键为 FREE_SHARES_RATIO；回退键命中时分母口径随实际上游键确定），数值为百分数刻度。 | `verified` |
| 东财-datacenter(英文键) | `plan` | ASSIGN_PROGRESS | 旧未限定短路径已退役。历史 RPT_SHAREBONUS_DET 字段；当前 getter 不再调用该端点。 完整路径：ASSIGN_PROGRESS。多目标别名只用于说明路径拆分，不表示这些字段同义。 | `disproved` |
| 东财-datacenter(英文键) | `premium_pct` | premium_pct | 项目计算折溢率 round((成交价/收盘价-1)*100, 2)；收盘价为 0 时返回 0。 | `disproved` |
| 东财-datacenter(英文键) | `shares` | lockup_expiry.shares | 旧未限定短路径已退役。根据实际可流通量是否可用选择实际解禁量或报告总量。 完整路径：lockup_expiry.shares。多目标别名只用于说明路径拆分，不表示这些字段同义。 | `disproved` |
| 东财-datacenter(英文键) | `shares_is_actual` | lockup_expiry.shares_is_actual | 旧未限定短路径已退役。完整输出路径；适配器根据路线和 ABLE_FREE_SHARES 可用性生成的布尔标记。 完整路径：lockup_expiry.shares_is_actual。多目标别名只用于说明路径拆分，不表示这些字段同义。 | `disproved` |
| 东财-datacenter(英文键) | `transfer_ratio` | TRANSFER_RATIO | 旧未限定短路径已退役。旧 Eastmoney RPT_SHAREBONUS_DET 原始键；当前 TDX 的送转值另登记为 TDX::dividend_history.transfer_ratio，不建立映射。 完整路径：TRANSFER_RATIO。多目标别名只用于说明路径拆分，不表示这些字段同义。 | `disproved` |
| 东财-em_kline_f61 | `dktotal` | daily_kline_record_count | Eastmoney 日 K 查询结果中，服务端报告的可用历史日 K 记录总数。结论限于项目当前请求：klt=101（日线）、fqt=0（不复权）、未传 beg、end=20500101、lmt=150；不等于本次返回 klines 数量，也不外推为上市以来全部交易日数或其他请求参数下的总记录数。 | `verified` |
| 东财-em_kline_f61 | `n_klines` | n_klines | 项目派生的 K 线返回条目数：collect_em_kline_f61 对响应 data.klines 计算 len(klines) 后写入；不是 Eastmoney 响应字段。当前请求 lmt=150，完整成功样本均返回 150 条。 | `disproved` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].AFTER_ISSUE_PE` | ipo_record_after_issue_pe | 该 IPO 记录的发行市盈率。官方新股页在原始值存在时直接使用该值显示；原始值为空时页面可回退到预测值。此定义只适用于原始字段，不包括页面回退计算值。具体估值时点未由该字段模板说明。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].AMPLITUDE` | ipo_first_day_amplitude_pct | 该 IPO 证券上市首日振幅；以 `(首日最高价 - 首日最低价) / 前收 × 100` 对照首日 K 线，6/6 在 0.005 个百分点内吻合。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].APPLY_DATE` | ipo_record_subscription_date | 该 IPO 记录所列的申购日期，是发行事件日期；不是采集日、来源数据日或上市日期。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].AVERAGE_PRICE` | ipo_yield_price_reference_yuan | IPO_YIELD 使用的价格基准。6 只跨 2023–2026 年、沪深不同板块样本中，均匹配上市后第 5 个交易日成交量加权均价，绝对误差不超过 0.0018 元；它不同于首日 LD_AVERAGE_PRICE、开板日 OPEN_AVERAGE_PRICE，也不是 TOTAL_CHANGE 的基价。当前只把第五交易日口径限定到已核样本，不外推所有历史发行制度。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].BALLOT_PAY_DATE` | ipo_subscription_payment_date | 该 IPO 记录对应发行安排中需缴纳申购/中签认购款的日期；日期随发行制度变化，不能统一假设等于申购日或 T+2。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].CHANGE` | ipo_latest_quote_change_yuan | IPO 列表所列的最新报价涨跌额；5 条同股同日可比样本与官方最新报价变化值一致。 对未核明的来源实际报价日不外推为采集目标数据日。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].CHANGE_RATE` | ipo_latest_quote_change_rate_pct | IPO 列表所列的最新报价涨跌幅；5 条同股同日可比样本与官方最新报价涨幅值一致。 对未核明的来源实际报价日不外推为采集目标数据日。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].CLOSE_PRICE` | ipo_record_first_day_close_price | 该证券上市首日收盘价；不是当前最新价或发行价。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].CONTINUOUS_1WORD_NUM` | ipo_consecutive_one_word_board_count | 该 IPO 记录对应股票连续一字板数；东方财富页面不对注册制 IPO 统计此指标，空值不得解释为零。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].DEC_SUMFINA` | ipo_gross_funds_raised_native_unit | IPO 募集资金总额。两份发行人正式文件与接口值经单位换算后吻合；另有 420/500 条记录与 ISSUE_PRICE × ISSUE_NUM（万股）按市场原生单位折算相符。其余 80 条差异未逐项归因，不视为公式反例。沪深以亿元计，北交所以元计。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].EACHBALLOT_SHARES` | ipo_lottery_lot_shares | 中一签对应的获配股数；与 MZYQ_PAY_FUND / ISSUE_PRICE 的反算在 343 条可比记录中一致。按发行板块/时期保留实际股数，不假设所有历史签号都固定为 500 股。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].INDUSTRY_PE` | ipo_legacy_industry_pe | IPO 记录中的参考行业市盈率；在 20 条历史记录中与已核的 INDUSTRY_PE_NEW 数值 20/20 一致，但本结论限于该历史接口样本，不外推到当前发行制度或其他市场。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].INFO_CODE` | ipo_prospectus_document_code | 东方财富用于构造该 IPO 记录招股说明书/意向书 PDF 链接的文档代码。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].IPO_YIELD` | ipo_yield_pct | IPO 价格基准收益率，按 `(AVERAGE_PRICE / ISSUE_PRICE - 1) × 100`；样本中 AVERAGE_PRICE 是该字段自己的收益价格基准，不与 TOTAL_CHANGE 混用。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].ISSUE_NUM` | ipo_total_issue_shares_wan | 该 IPO 发行记录的发行总股数，官方页面以万股显示；不是网上发行数量或发行后总股本。历史记录可能存在取整、截断或旧数据差异，万科样本与正式股数折算结果相差约 0.31%。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].ISSUE_PRICE` | ipo_issue_price_per_share | 该 IPO 发行记录的每股发行价格，不是上市首日价格或当前价格。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].ISSUE_WAY_EXPLAIN` | ipo_issue_way_explanation | 该 IPO 发行记录中对发行方式的文字说明；它与 ISSUE_WAY（发行方式类型）是不同字段。当前保留样本观察到“历史遗留”“本地发行”“认购证”等说明值。本结论确认字段角色，不表示完整发行流程分类，也不穷尽所有可能取值。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].IS_REGISTRATION` | ipo_registration_system_flag | 东方财富用于区分注册制与审批制页面展示分支的标记；1 表示注册制，0 表示非注册制分支。未确认其它可能编码。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].IS_RISKWARNING` | ipo_risk_warning_flag | 东方财富 IPO 记录中的风险警示标记（0/1）。保留样本中值 1 均对应 *ST 记录；深交所规则将 *ST 定义为退市风险警示标识、将 ST 定义为其他风险警示标识。样本未含纯 ST 记录，不外推该枚举情形。该字段没有单独来源日期，不以 UP_DATE 或采集目录日作为状态生效日。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].LATELY_PRICE` | ipo_record_latest_price | 东方财富新股申购页所列的该证券最新价；响应没有给出此价格自身的来源实际日期，不得自动解释为目录目标数据日的收盘价。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].LD_CLOSE_CHANGE` | ipo_first_day_close_change_pct | 该 IPO 记录对应股票上市首日收盘价相对于发行价的涨幅；留存样本符合 (CLOSE_PRICE / ISSUE_PRICE - 1) × 100，不等同于基于成交均价的 TOTAL_CHANGE。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].LD_HIGH_CHANG` | ipo_first_day_high_change_pct | 该 IPO 记录对应股票上市首日最高涨幅；本次不推断其详细基准价公式。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].LD_OPEN_PREMIUM` | ipo_first_day_open_premium_pct | 该 IPO 记录对应股票上市首日开盘价相对于发行价的溢价率；留存样本符合 (OPEN_PRICE / ISSUE_PRICE - 1) × 100。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].LIMIT_UP_PRICE` | ipo_reference_limit_price_yuan | RPTA_APP_IPOAPPLY 提供的发行价 1.44 倍参考价；在 343 条沪深记录中等于 `ISSUE_PRICE × 1.44`。这不是注册制新股上市前五个交易日的法定涨跌幅上限，不能用于当日涨停价判断。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].LISTING_DATE` | ipo_record_listing_date | 该 IPO 记录所列的上市日期，是证券开始上市交易的业务日期；不是申购日期或采集日期。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].MAIN_BUSINESS` | ipo_record_main_business_description | IPO 发行记录附带的发行人主营业务文字描述。与 BUSINESS_SCOPE（经营范围）为不同字段。RPTA_APP_IPOAPPLY 未单独提供该文本的更新时间或有效日期；不能据目录目标数据日或采集自然日推断其为 IPO 时点或当前时点的经营状态，也不推断其历史版本或更新机制。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].MZYQ_PAY_FUND` | ipo_lottery_payment_amount_yuan | IPO 中签后每签应缴金额；等于发行价乘以每签获配股数，343/343 复算吻合。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].NETSUMFINA` | ipo_net_funds_raised_native_unit | IPO 募集资金净额。两份发行人正式招股说明书金额与接口值经单位换算后吻合；单位随市场：沪深亿元、北交所元。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].OD_HIGH_CHANGE` | ipo_first_day_high_change_pct | 同一 IPO 发行记录中的首日最高涨幅历史字段；20 条历史记录中与官方页面已标注的 LD_HIGH_CHANG 20/20 一致。该同路径关系限于现有历史记录，未见现代记录，不外推字段版本。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].ONLINE_ISSUE_NUM` | ipo_online_issue_shares | 该 IPO 记录对应网上发行的股票数量；原始接口单位为股，东方财富列表按万股显示。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].OPEN_DATE` | ipo_open_board_date | 该 IPO 记录对应股票的开板日期，不等同于上市日期；早期样本相同仅源于上市首日开板。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].ORG_TYPE` | ipo_record_bank_stock_classification | IPO 发行记录返回的银行股/非银行股分类文本。当前保留样本的值分别为“银行股”和“非银行股”。只确认该路径提供这类分类文字；东方财富未公开分类规则，不据此断言公司的法律组织形式、行业分类体系或未观察到的其他枚举。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].PAR_VALUE` | ipo_record_par_value | 该 IPO/发行历史记录对应普通股的每股面值；这是发行记录属性，不保证等于当前每股面值。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].PREDICT_ISSUE_PRICE1` | ipo_issue_price_prediction_candidate_1_yuan | 东方财富 IPO 发行价预测的候选价格 1；第一方详情页脚本将 PREDICT_ISSUE_PRICE1 读作价格1并纳入预测价格候选逻辑，不是实际发行价 ISSUE_PRICE。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].PREDICT_RAISE_FUNDS` | ipo_planned_fundraising_target_yi_cny | 东方财富 IPO 发行记录中的募资计划预测目标，单位为亿元。七个不同 IPO 事件的值与发行人招股文件所列拟投入募集资金或募资需求总额按万元换算为亿元后精确相等。它不等同于发行价乘发行股数得出的发行募集总额，不等同于扣除发行费用后的实际净额，也不保证代表发行完成后最新调整的募投预算。计划可在发行过程中调整；不以采集自然日或目录目标数据日推断方案版本时间。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].PROFIT` | ipo_record_per_sign_profit_yuan | 每中一签的获利金额。注册制个股按上市首日成交均价相对发行价计算；审批制个股按上市日期以外第一个非一字板交易日的成交均价计算。每签股数不跨板块、年代固定化。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].RECOMMEND_ORG` | ipo_sponsor_recommendation_org | IPO 保荐/推荐机构名称；两份发行人招股书锚点一致，并保留证券机构后续更名的法人连续性说明。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].TCHANGE_RATE` | ipo_issue_price_to_latest_price_change_pct | 接口最新价 TNEW_PRICE 相对发行价 ISSUE_PRICE 的涨幅，按 `(TNEW_PRICE / ISSUE_PRICE - 1) × 100`。接口没有在此字段内明确最新价自身的来源实际日期；未核日期时不得将其作为目标日行情。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].TNEW_PRICE` | ipo_latest_price_yuan | 东方财富 IPO 列表所列的该证券最新价；6 股逐股核验均与截至 2026-11-20 的最新日 K 收盘价一致。响应的更新日期不等于价格来源日期；仍按最新报价字段保留日期资格限制。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].TOTAL_CHANGE` | ipo_record_total_gain_pct | 东方财富新股页定义的 IPO 涨幅：注册制个股按上市首日成交均价相对发行价计算；审批制个股按上市日期以外第一个非一字板交易日的成交均价相对发行价计算。参照交易日依发行制度而异，不等同于统一的首日收盘涨幅。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].TOTAL_RAISE_FUNDS` | ipo_actual_fundraising_total_yi_cny | 东方财富 IPO 发行记录中标注的实际募集资金总额，单位为亿元；这是平台报告值，历史个例可能与发行人原始公告存在精度差异。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].TOTAL_SHARES` | ipo_total_share_capital_after_issue_shares | IPO 后总股本/总股本数量，单位为股；不是本次发行数量。三份发行人招股书锚点均与接口一致，含超额配售前口径。 | `verified` |
| 东财-event_dc(IPO发行记录) | `ipo_calendar[].UNDERWRITER_ORG` | ipo_underwriter_org_list | IPO 承销机构名称列表；可包含主承销商与联席主承销商，不保证等于单一保荐人。两份发行人招股书锚点一致，保留多机构列表和机构更名沿革。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].ACTUAL_ISSUE_SCALE` | convertible_bond_issue_scale | 可转债初始发行规模/债券发行总额（发行面值合计）；不是当前剩余规模，也不表示扣除发行费用后的净募集资金。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].BOND_EXPIRE` | convertible_bond_term_years | 东方财富详情页标注的可转债存续期限（年）。提前终止或赎回后，该值可短于募集说明书原始约定期限；蓝思转债样本为2.1671年，正式募集说明书原始约定为6年。该字段不是剩余期限或到期日期。保留样本显示其与起息日至有效终止期间接近，但统一年化和终止日取值规则未公开。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].BOND_START_DATE` | convertible_bond_lottery_number_publication_date | 东方财富可转债申购列表中以 `BOND_START_DATE` 绑定到“中签号发布日”的日期字段。该页面定义它为中签号码发布日；它不同于申购日期、股权登记日和上市时间。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].COUPON_IR` | bond_coupon_rate_current_interest_year_pct | 按采样时点所处计息年度从原票面利率表选出的票面利率，数值单位为百分比（例如2表示2.0%）。计息年度以起息日VALUE_DATE的周年日切换。提前赎回或退市记录仍可能按原利率表继续滚动该值，因此它不证明债券仍存续、当前仍有应付利息，也不是实际收益率或利息金额。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].CURRENT_BOND_PRICE` | convertible_bond_current_market_price | 可转债当前市场价格；当前页面回退字段，仅在 CURRENT_BOND_PRICENEW 为空时显示。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].CURRENT_BOND_PRICENEW` | convertible_bond_current_market_price | 可转债当前市场价格；东方财富详情页在该值非空时优先显示，空时回退至 CURRENT_BOND_PRICE。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].EXECUTE_PRICE_HS` | convertible_bond_put_execution_price_yuan_per_bond | 东方财富可转债记录中最近一次回售的执行价格，单位为元/张。该字段对应回售事件，不是赎回价格或转股价格。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].EXECUTE_PRICE_SH` | convertible_bond_redemption_execution_price_yuan_per_bond | 东方财富可转债记录中最近一次赎回的执行/兑付价格，单位为元/张。该字段对应赎回事件，不是回售价格或转股价格。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].EXECUTE_REASON_HS` | convertible_bond_execution_reason_code | 东方财富可转债详情页显示的回售/赎回执行原因码：1 满足回售条款；2 满足赎回条件；3 满足附加回售条款；4 强制赎回；5 到期赎回。接口样本另见代码 6，但当前第一方 switch 未定义 6，故 6 仍未定案。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].EXECUTE_REASON_SH` | convertible_bond_execution_reason_code | 东方财富可转债详情页显示的回售/赎回执行原因码：1 满足回售条款；2 满足赎回条件；3 满足附加回售条款；4 强制赎回；5 到期赎回。接口样本另见代码 6，但当前第一方 switch 未定义 6，故 6 仍未定案。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].EXECUTE_START_DATESH` | convertible_bond_redemption_execution_date | 东方财富可转债记录中最近一次赎回执行日/兑付日；不同于赎回公告日、赎回登记日或债券退市日。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].FIRST_PER_PREPLACING` | convertible_bond_priority_placement_amount_yuan_per_share | 东方财富可转债申购列表中原股东优先配售的每股配售额。页面明确说明适用对象为股权登记日持股的原股东，单位为元/股。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].INITIAL_TRANSFER_PRICE` | convertible_bond_initial_conversion_price | 发行时确定的初始转股价格；它与可因后续权益分派或修正而变化的当前转股价是不同字段。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].ISSUE_TYPE` | convertible_bond_issue_type_code_set | 发行类型代码组合。基于同记录 ISSUE_TYPE 与 PARAM_NAME 的全部出现组合，唯一反推出：1 网上向社会公众投资者发行；2 网下向机构投资者协议发行；4 网上向原 A 股无限售股东优先配售；5 网下向原 A 股有限售股东优先配售。组合顺序不相同，按位置配对是错误的；未观测代码不外推。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].ISSUE_YEAR` | convertible_bond_approval_year | 东方财富可转债详情页将 `ISSUE_YEAR` 绑定到“债券年度”。完整的 500 条保留样本中，5 条字段年度与实际公开发行/申购日期年份不同的记录，均与发行人正式公告中的中国证监会核准批复文号年份一致。因此该字段表示可转债核准年度，不是实际发行、申购或上市年份。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].IS_CONVERT_STOCK` | convertible_bond_conversion_status | 东方财富可转债记录中的当前转股状态标记，原始值为“是/否”。在保留样本中，该状态与同一响应记录的转股开始日、转股结束日及采集观察时点相符；它表示当前是否处于可转股期间，不是债券是否具有转股条款的静态属性。具体盘中切换时刻和接口刷新规则未公开。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].ONLINE_GENERAL_AAU` | convertible_bond_online_subscription_limit_thousand_yuan | 东方财富可转债申购列表中的网上申购上限金额。接口原始单位为千元；页面显示时除以 10 换算为万元。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].ONLINE_GENERAL_LWR` | convertible_bond_online_lottery_win_rate_pct | 东方财富可转债申购列表中“中签率”字段，页面以百分比显示至四位小数；接口未提供可确认的来源实际日期。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].PAYDAYNEW` | convertible_bond_payday_signed_day_code | 每年付息日的负日号编码：`PAYDAYNEW = -日(PAY_INTEREST_DAY)`。例如 `04-18` 对应 `-18`；它不是 YYYYMMDD 日期，也不是采集日期。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].PBV_RATIO` | convertible_bond_underlying_stock_pb_ratio | 对应正股的市净率；页面标签为“正股市净率”，未标百分比或其他显示单位。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].RATING` | convertible_bond_credit_rating | 东方财富可转债申购列表在“信用评级”列显示的评级值；页面未为其指定数值单位。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].SECURITY_START_DATE` | convertible_bond_equity_registration_date | 东方财富可转债申购列表中以 `SECURITY_START_DATE` 绑定到“股权登记日”的日期字段；不能替代申购日期、上市时间或来源采集日期。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].TRANSFER_PREMIUM_RATIO` | convertible_bond_conversion_premium_ratio | 东方财富可转债详情页显示的转股溢价率，按百分比展示。按当前债券现价及转股价值复算，153/154条可比记录吻合到2位小数；113655相差0.01个百分点，原因未确认。 | `verified` |
| 东财-event_dc(可转债列表) | `convertible_bonds[].TRANSFER_VALUE` | convertible_bond_conversion_value | 东方财富可转债详情页显示的转股价值。当前样本中与100×正股价/当前转股价按4位小数计算相符；该公式是样本观察，未认定为官网发布的统一算法。 | `verified` |
| 东财-push2(stock/get) | `f103` | ocf_ttm(f103) | 经营活动现金流量净额 TTM：上年全年 + 本年最新报告期年初至今 − 上年同期年初至今；合并现金流口径。 | `verified` |
| 东财-push2(stock/get) | `f107` | f107 | 市场标记（布尔 0/1，北交=0） | `verified` |
| 东财-push2(stock/get) | `f108` | eps_ttm(f108) | 归母净利润 TTM 按当前总股本折算的每股收益；TTM 归母净利润 = 上年度全年归母净利润 + 本年度最新报告期年初至今归母净利润 - 上年度同期年初至今归母净利润，分母为 Push2 f84 当前总股本。不是扣非 EPS，也不推断法定基本/稀释 EPS 的加权平均股数口径。 | `verified` |
| 东财-push2(stock/get) | `f110` | f110 | 市场标记（布尔 0/1，北交=0） | `verified` |
| 东财-push2(stock/get) | `f118` | f118 | 市场/板块状态标记（≡ ulist:f107） | `verified` |
| 东财-push2(stock/get) | `f129` | eastmoney_quote_concept_theme_labels | 逗号分隔的个股概念 / 题材标签列表；是 `stock/get` 路径含义，不套用 `ulist239::f129` 的净利率释义。 | `verified` |
| 东财-push2(stock/get) | `f135` | fund_main_buy | 东方财富个股资金流分类口径下，当日主力类别买入金额；留存可比较样本均满足 f135 = 超大单买入 f138 + 大单买入 f141。该值描述东方财富分类结果，不代表特定账户或真实机构身份。 | `verified` |
| 东财-push2(stock/get) | `f136` | fund_main_sell | 东方财富个股资金流分类口径下，当日主力类别卖出金额；留存可比较样本均满足 f136 = 超大单卖出 f139 + 大单卖出 f142。该值描述东方财富分类结果，不代表特定账户或真实机构身份。 | `verified` |
| 东财-push2(stock/get) | `f137` | fund_main_today | 主力资金净流入金额（当日）；与超大单和大单净流入之和一致，不表示投资者账户身份。 | `verified` |
| 东财-push2(stock/get) | `f138` | fund_super_buy | 东方财富“超大单”类别资金流入金额（当日，按该页面的资金流分类口径；不代表账户身份）。 | `verified` |
| 东财-push2(stock/get) | `f139` | fund_super_sell | 东方财富“超大单”类别资金流出金额（当日，按该页面的资金流分类口径；不代表账户身份）。 | `verified` |
| 东财-push2(stock/get) | `f140` | fund_super_today | 东方财富“超大单”类别资金净流入金额（当日；不表示账户身份）。 | `verified` |
| 东财-push2(stock/get) | `f141` | fund_large_buy | 东方财富“大单”类别资金流入金额（当日，按该页面的资金流分类口径；不代表账户身份）。 | `verified` |
| 东财-push2(stock/get) | `f142` | fund_large_sell | 东方财富个股资金流分类口径下，当日大单类别卖出金额；由大单买入 f141 减大单净流入 f143 反推，并经留存可比较样本逐项复算。该值描述东方财富分类结果，不代表特定账户或真实机构身份。 | `verified` |
| 东财-push2(stock/get) | `f143` | fund_large_today | 东方财富个股资金流历史表“大单净流入/净额”对应的当日金额；按东方财富资金分类口径解释，不代表特定账户或真实机构身份。 | `verified` |
| 东财-push2(stock/get) | `f144` | fund_mid_buy | 东方财富个股资金流分类口径下，当日中单类别流入/买入金额；此分类不表示投资者账户身份。 | `verified` |
| 东财-push2(stock/get) | `f145` | fund_mid_sell | 东方财富个股资金流分类口径下，当日中单类别流出/卖出金额；此分类不表示投资者账户身份。 | `verified` |
| 东财-push2(stock/get) | `f146` | fund_mid_today | 东方财富个股资金流分类口径下，当日中单净流入金额，等于中单流入减中单流出；此分类不表示投资者账户身份。 | `verified` |
| 东财-push2(stock/get) | `f163` | f163 | 静态市盈率（总市值/上年度净利润） | `verified` |
| 东财-push2(stock/get) | `f176` | f176 | 按最新报告期年初至期末累计营收年化的市销率；在已观察到的季度中，按 f116 总市值 ÷ (f183 × 4 / q) 计算，q 为最新报告期季度序号。当前实证覆盖 Q2、Q3，不等同市销率 TTM，也不外推 Q1、Q4。发行人报告样本确认了 f183 对应的报告期累计营收，但本定义不统一各行业财报中的具体行项目名称。 | `verified` |
| 东财-push2(stock/get) | `f250` | H 股上一香港交易日收盘价 | 该 A 股记录关联 H 股证券的上一香港交易日正式收盘价。此字段所指价格日期早于同一记录行的行情观测日期；同一行的已验证 Push2 f86 只确认观测日期。 | `verified` |
| 东财-push2(stock/get) | `f55` | f55 | 基本每股收益计算值（最新报告期归母净利润/最新总股本） | `verified` |
| 东财-push2(stock/get) | `f59` | quote_price_precision_digits | 该证券实时行情报价的显示小数位数；在 fltt=1 响应中用于将价格整数还原为 fltt=2 报价。 | `verified` |
| 东财-push2(stock/get) | `f62` | f62 | 最新已发布报告期的季度序号（如 2=中报、3=三季报；不含年份） | `verified` |
| 东财-push2(stock/get) | `f80` | stock_trading_session_intervals | 该证券当日宽泛交易时段区间列表。源值为 JSON 数组，每项 `b` / `e` 是北京时间 YYYYMMDDHHmm；区间覆盖交易会话，下午区间包含收盘集合竞价，不等同于连续竞价分段。 | `verified` |
| 东财-push2(stock/get) | `f86` | f86 | 当日收盘/最后行情时间戳 | `verified` |
| 东财-push2(stock/get) | `f92` | f92 | 每股净资产计算值（最新公告归母股东权益剔除其他权益工具后/最新总股本） | `verified` |
| 东财-push2ex | `change_pct` | change_pct | 当日涨跌幅（百分比）；接口原始值保留比 KPL col_22 更多的小数位，三个有效日期 271 组对照均在 0.02 个百分点内，按两位小数四舍五入后相等。 | `verified` |
| 东财-push2ex | `circulating_value` | push2ex.tradable_a_market_value | A股流通市值；按非限售流通A股股本乘该涨停/跌停/炸板池记录的A股现价计算，输出单位元；不表示自由流通市值。 | `verified` |
| 东财-push2ex | `first_limit_time` | limit_pool_first_seal_time | 东财涨停股池个股当日首次封板时间；项目原值为 HHMMSS 数字字符串，左补零后格式化为页面显示的 HH:MM:SS。 | `verified` |
| 东财-push2ex | `last_limit_time` | limit_pool_last_seal_time | 东财涨停股池个股当日最后封板时间；项目原值为 HHMMSS 数字字符串，左补零后格式化为页面显示的 HH:MM:SS。 | `verified` |
| 东财-push2ex | `limit_count` | limit_up_streak_count | 当前连续涨停板数（当前连板数）；与同数据日 KPL col_15 的三个有效日期 271 组对照逐值相等。11 月 5 日次日回查存在集合和值差异，已单独记录且不计入正证据。 | `verified` |
| 东财-push2ex | `price` | price | 现价；接口原始数值以 0.001 元为单位，除以 1,000 后与同数据日 KPL col_21 的三个有效日期 271 组对照逐值相等。 | `verified` |
| 东财-push2ex | `sector` | sector | 涨停池记录中的所属行业板块标签文本；项目直接映射自同源 Push2EX 字段 hybk。 | `verified` |
| 东财-push2ex | `total_value` | push2ex.total_market_value | A股总市值；按总股本乘该涨停/跌停/炸板池记录的A股现价计算，输出单位元。 | `verified` |
| 东财-push2ex | `turnover_rate` | limit_pool_turnover_rate | 东财涨停股池个股当日换手率；官方页面值以百分比显示。本裁决只确认该来源路径对应官方涨停池“换手率”列，不推断自由流通或其他计算口径。 | `verified` |
| 东财-push2ex | `yfbt` | yfbt / ylbc | 昨日首次封板时间 / 昨日连板数 | `unverified` |
| 东财-push2ex | `ylbc` | yfbt / ylbc | 昨日首次封板时间 / 昨日连板数 | `unverified` |
| 东财-push2ex | `zt_continuous` | limit_up_stat_count | 东财涨停股池“涨停统计”组合中的涨停板次数分量（对应原始 zttj.ct；不等同页面单列的“连板数”；统计窗口及累计规则未公开）。 | `verified` |
| 东财-push2ex | `zt_days` | limit_up_stat_days | 东财涨停股池“涨停统计”组合中的天数分量（对应原始 zttj.days；自然日/交易日口径、起算点及回看窗口未公开）。 | `verified` |
| 东财-push2ex | `zttj.ct` | zttj.days / zttj.ct | N天M板 | `verified` |
| 东财-push2ex | `zttj.days` | zttj.days / zttj.ct | N天M板 | `verified` |
| 东财-slist | `n_boards` | n_boards | 项目派生的板块列表条目数：collect_slist 读取 Eastmoney 响应 data.diff，并以 len(diff) 生成此键；不是提供方响应字段。 | `disproved` |
| 东财-ulist239(np/get) | `f1` | quote_price_precision_digits | 该证券实时行情报价的显示小数位数；在 fltt=1 响应中用于将价格整数还原为 fltt=2 报价。 | `verified` |
| 东财-ulist239(np/get) | `f11` | 5分钟涨跌幅 | 东方财富行情中心官方字段映射定义的5分钟涨跌幅，按百分比展示。精确计算公式、窗口边界及复权细节未由本证据确认。 | `verified` |
| 东财-ulist239(np/get) | `f111` | registration_system_listing_bitmask | 东方财富 ulist.np/get 返回的证券上市制度标记位掩码。保留样本支持 bit17（131072）表示注册制试点/注册制板块上市批次，bit19（524288）表示注册制改革前进入当前上市板块的存量批次。该定义描述 Eastmoney 当前证券分类中的上市批次标记，不等同于发行人最早一次公开发行所经历的审批方式；920508 殷图网联先在新三板精选层挂牌、后平移至北交所，是此边界的实例。bit10、bit21、bit3、bit6、bit11、bit18 等其他观察位含义未定。未观察 2023-04 全面注册制后沪深主板新 IPO，不外推 bit17 在该类证券中的编码。 | `verified` |
| 东财-ulist239(np/get) | `f114` | f114 | 市盈率(静态/年报 LYR) | `verified` |
| 东财-ulist239(np/get) | `f13` | f13 | 市场标志：本项目 A 股样本中沪市=1，非沪市=0（含深市、北交）；保留期样本与 f27 同值。 | `verified` |
| 东财-ulist239(np/get) | `f131` | f131 | 市现率 PCF_TTM（总市值 / 经营现金流 TTM） | `verified` |
| 东财-ulist239(np/get) | `f133` | dividend_yield_lfy_observed | 股息率（%）；在本次保留的善水科技、万华化学、贵州茅台样本中，数值符合最近已实施完整年度现金分红/当日价格的 LFY-like 口径。东方财富整体算法会按分红期切换 TTM/LFY 并可含预案；特别股利及切换条件未由本字段样本充分确认。 | `verified` |
| 东财-ulist239(np/get) | `f139` | listing_board_type | 证券上市板块类型代码；本次日期合格 A 股样本中 2=主板、5=创业板、32=科创板、80=北交所。仅确认四种已观测枚举，不声称完整码表；该值不代表交易所市场号。 | `verified` |
| 东财-ulist239(np/get) | `f144` | f144 | 最新价/现价 | `verified` |
| 东财-ulist239(np/get) | `f148` | security_eligibility_bitmask | 东方财富 ulist.np/get 返回的证券资格标志位掩码。当前证据确认 bit6（64）表示交易所融资融券标的资格，bit9（512）表示沪股通下一北向交易日可买可卖资格，bit10（1024）表示深股通下一北向交易日可买可卖资格。bit0 与未观察到的其他位含义未定；这些资格标记不代表特定券商或投资者账户的实际可交易性。 | `verified` |
| 东财-ulist239(np/get) | `f149` | ulist239_change_6_intervals_pct | 相对前第六个交易日收盘价的累计涨跌幅（六个交易间隔）；观测值以百分数表示。 | `verified` |
| 东财-ulist239(np/get) | `f152` | 行情百分比/比例缩放位数 | 东方财富官方行情中心把 f152 作为多个涨跌幅、涨速和比例字段的十进制缩放/显示精度参数，而非该指标的数值本身。官方 fltt=1 前端格式器按 e / 10^f152 还原并显示 f152 位；项目采集使用 fltt=2，已转换行情数值不得再次缩放。 | `verified` |
| 东财-ulist239(np/get) | `f185` | H 股上一香港交易日收盘价 | 该 A 股记录关联 H 股证券的上一香港交易日正式收盘价。它与同日 Push2 f250 对齐；价格内容日期是上一港股交易日，不是同一行观测日。 | `verified` |
| 东财-ulist239(np/get) | `f186` | H 股最新价 | 该 A 股记录关联 H 股证券的最新成交/行情价。盘中为最新行情价；收盘后样本等于当日收盘价。 | `verified` |
| 东财-ulist239(np/get) | `f187` | H 股当日涨跌幅 | 该 A 股记录关联 H 股证券的当日涨跌幅。收盘样本中按 (f186 / f185 - 1) × 100 计算并四舍五入到两位小数。 | `verified` |
| 东财-ulist239(np/get) | `f190` | H股关联A股价格缩放位数 | 东方财富行情中心把 f190 用作 f186（H股对应的A股最新价）的十进制缩放/显示精度参数：官方前端在 fltt=1 价格值场景中按 f186 / 10^f190 还原并显示 f190 位小数。项目采集使用 fltt=2，留存的 f186 已为小数形式，不应重复缩放。该字段不是 H 股股数。 | `verified` |
| 东财-ulist239(np/get) | `f191` | h_share_code | A 股记录所关联 H 股证券的代码。当前经核对样本为 601288 对应 01288；结论仅适用于东财 Ulist239 该完整来源路径。 | `verified` |
| 东财-ulist239(np/get) | `f192` | h_share_market_code | A 股记录所关联 H 股证券的东方财富 secid 市场编号。当前经核对样本为 116，对应 secid 116.01288 中的港股市场前缀；该字段是市场编号，不是 A+H 布尔标记。结论仅适用于东财 Ulist239 该完整来源路径及已观察到的编号。 | `verified` |
| 东财-ulist239(np/get) | `f193` | h_share_name | A 股记录所关联 H 股证券的简称。当前经核对样本为农业银行；结论仅适用于东财 Ulist239 该完整来源路径。 | `verified` |
| 东财-ulist239(np/get) | `f22` | 3分钟涨速 | 东方财富金融终端默认行情列表涨速字段对应的3分钟涨速，按百分比展示。精确计算公式、窗口边界及复权细节未由本证据确认。 | `verified` |
| 东财-ulist239(np/get) | `f221` | report_period_end_date | 财务报告截止日期（报告期末日期），原始值采用 YYYYMMDD；不表示公告日期或采集/行情快照日期。 | `verified` |
| 东财-ulist239(np/get) | `f231` | f231 | 有转债标志（0=无/3=有） | `verified` |
| 东财-ulist239(np/get) | `f27` | f27 | 市场标志：本项目 A 股样本中沪市=1，非沪市=0（含深市、北交）；与同源 f13 为实证别名。 | `verified` |
| 东财-ulist239(np/get) | `f30` | current_trade_hand_count | 最近一笔成交的手数；实测绝对值对应已验证的现手量，原始正负号编码含义未确认。 | `verified` |
| 东财-ulist239(np/get) | `f46` | ulist239_parent_net_profit_yoy_growth_pct | 归属于母公司股东的净利润同比增长率（东方财富财报展示口径；亏损基期算法另行保留） | `verified` |
| 东财-ulist239(np/get) | `f49` | ulist239_sales_gross_margin_report_period_pct | 报告期销售毛利率（东方财富财报展示口径；单位为%；本次 2026-09-30 样本对应年初至 9 月累计报告期） | `verified` |
| 东财-ulist239(np/get) | `f59` | parent_equity_to_total_assets_ratio | 报告期末合并资产负债表中归属于母公司股东（或所有者）权益占总资产的比例；按 TOTAL_PARENT_EQUITY ÷ TOTAL_ASSETS × 100 计算。 | `verified` |
| 东财-ulist239(np/get) | `f76` | fund_mid_buy | 东方财富个股资金流分类口径下，当日中单类别流入/买入金额；此分类不表示投资者账户身份。 | `verified` |
| 东财-ulist239(np/get) | `f77` | fund_mid_sell | 东方财富个股资金流分类口径下，当日中单类别流出/卖出金额；此分类不表示投资者账户身份。 | `verified` |
| 东财-ulist239(np/get) | `f78` | fund_mid_today | 东方财富个股资金流分类口径下，当日中单净流入金额，等于中单流入减中单流出；此分类不表示投资者账户身份。 | `verified` |
| 东财-ulist239(np/get) | `f9` | f9 | 市盈率（动态/最新报告期年化） | `verified` |
| 东财-热榜(em_hot) | `change_rate` | latest / change_rate | 现价 / 涨跌幅 | `verified` |
| 东财-热榜(em_hot) | `chengjiaoe` | chengjiaoe / chengjiaoliang | 成交额 | `verified` |
| 东财-热榜(em_hot) | `chengjiaoliang` | chengjiaoe / chengjiaoliang | 成交额 | `verified` |
| 东财-热榜(em_hot) | `close` | close / zhangdie | 收盘价 / 涨跌额 | `verified` |
| 东财-热榜(em_hot) | `hgt` | hgt / sgt | 沪/深股通累计净买入 | `verified` |
| 东财-热榜(em_hot) | `huanshou` | zhangfu / huanshou | 涨跌幅% / 换手率% | `verified` |
| 东财-热榜(em_hot) | `latest` | latest / change_rate | 现价 / 涨跌幅 | `verified` |
| 东财-热榜(em_hot) | `order` | order / code / name | 排名 / 代码 / 名称 | `verified` |
| 东财-热榜(em_hot) | `sgt` | hgt / sgt | 沪/深股通累计净买入 | `verified` |
| 东财-热榜(em_hot) | `zhangdie` | close / zhangdie | 收盘价 / 涨跌额 | `verified` |
| 东财-热榜(em_hot) | `zhangfu` | zhangfu / huanshou | 涨跌幅% / 换手率% | `verified` |
| 东财-资金流(em_fund_flow) | `f135` | fund_main_buy | 东方财富个股资金流分类口径下，当日主力类别买入金额；留存可比较样本均满足 f135 = 超大单买入 f138 + 大单买入 f141。该值描述东方财富分类结果，不代表特定账户或真实机构身份。 | `verified` |
| 东财-资金流(em_fund_flow) | `f136` | fund_main_sell | 东方财富个股资金流分类口径下，当日主力类别卖出金额；留存可比较样本均满足 f136 = 超大单卖出 f139 + 大单卖出 f142。该值描述东方财富分类结果，不代表特定账户或真实机构身份。 | `verified` |
| 东财-资金流(em_fund_flow) | `f137` | fund_main_today | 主力资金净流入金额（当日）；与超大单和大单净流入之和一致，不表示投资者账户身份。 | `verified` |
| 东财-资金流(em_fund_flow) | `f138` | fund_super_buy | 东方财富“超大单”类别资金流入金额（当日，按该页面的资金流分类口径；不代表账户身份）。 | `verified` |
| 东财-资金流(em_fund_flow) | `f139` | fund_super_sell | 东方财富“超大单”类别资金流出金额（当日，按该页面的资金流分类口径；不代表账户身份）。 | `verified` |
| 东财-资金流(em_fund_flow) | `f140` | fund_super_today | 东方财富“超大单”类别资金净流入金额（当日；不表示账户身份）。 | `verified` |
| 东财-资金流(em_fund_flow) | `f141` | fund_large_buy | 东方财富“大单”类别资金流入金额（当日，按该页面的资金流分类口径；不代表账户身份）。 | `verified` |
| 东财-资金流(em_fund_flow) | `f142` | fund_large_sell | 东方财富个股资金流分类口径下，当日大单类别卖出金额；由大单买入 f141 减大单净流入 f143 反推，并经留存可比较样本逐项复算。该值描述东方财富分类结果，不代表特定账户或真实机构身份。 | `verified` |
| 东财-资金流(em_fund_flow) | `f143` | fund_large_today | 东方财富个股资金流历史表“大单净流入/净额”对应的当日金额；按东方财富资金分类口径解释，不代表特定账户或真实机构身份。 | `verified` |
| 东财-资金流(em_fund_flow) | `f144` | fund_mid_buy | 东方财富个股资金流分类口径下，当日中单类别流入/买入金额；此分类不表示投资者账户身份。 | `verified` |
| 东财-资金流(em_fund_flow) | `f145` | fund_mid_sell | 东方财富个股资金流分类口径下，当日中单类别流出/卖出金额；此分类不表示投资者账户身份。 | `verified` |
| 东财-资金流(em_fund_flow) | `f146` | fund_mid_today | 东方财富个股资金流分类口径下，当日中单净流入金额，等于中单流入减中单流出；此分类不表示投资者账户身份。 | `verified` |
| 同花顺-fuyao | `assets_debt_ratio` | solvency.assets_debt_ratio | 旧无分组根路径身份；当前完整字段路径为 solvency.assets_debt_ratio，裸叶不是当前解析响应的根级独立字段。 | `disproved` |
| 同花顺-fuyao | `auction.auction_price` | auction_final.auction_price | 已退役的旧采集路径 auction.auction_price；当前完整运行路径为 auction_final.auction_price。旧“开盘价”释义已撤回；目标字段是竞价价格。本记录只处置路径身份，不创建跨源映射。 | `disproved` |
| 同花顺-fuyao | `auction_final.auction_volume_ratio` | auction_final.auction_volume_ratio | 竞价量比（官方未说明分母、计算窗口和公式）。 | `verified` |
| 同花顺-fuyao | `auction_pct` | auction_final.auction_pct | 已退役的旧无分组来源路径；当前完整采集路径为 auction_final.auction_pct。本条只处置路径身份，不否定目标字段的语义或单位。 | `disproved` |
| 同花顺-fuyao | `basic_eps` | basic_eps | 基本每股收益（元/股）。 | `verified` |
| 同花顺-fuyao | `calculate_operating_income_yoy_growth_ratio` | growth.calculate_operating_income_yoy_growth_ratio | 旧登记将 营业收入同比增长率 的 index_id 叶名当作来源根路径；当前响应中该根路径不存在，实际字段位于 growth.calculate_operating_income_yoy_growth_ratio。此记录仅退役旧路径身份，不改变嵌套字段的语义裁决。 | `disproved` |
| 同花顺-fuyao | `calculate_operating_profit_yoy_growth_ratio` | growth.calculate_operating_profit_yoy_growth_ratio | 旧登记把 index_id 叶名当作来源根字段；当前响应和解析器不输出 fin_indicators.calculate_operating_profit_yoy_growth_ratio 根路径。对应指标实际位于 growth.calculate_operating_profit_yoy_growth_ratio；此记录只退役旧路径身份，不否定嵌套字段语义。 | `disproved` |
| 同花顺-fuyao | `calculate_parent_holder_net_profit_yoy_growth_ratio` | growth.calculate_parent_holder_net_profit_yoy_growth_ratio | 旧登记将 归母净利润同比增长率 的 index_id 叶名当作来源根路径；当前响应中该根路径不存在，实际字段位于 growth.calculate_parent_holder_net_profit_yoy_growth_ratio。此记录仅退役旧路径身份，不改变嵌套字段的语义裁决。 | `disproved` |
| 同花顺-fuyao | `calendar` | a-share/calendar/trading-days | — | `unverified` |
| 同花顺-fuyao | `cash-flow.cash_meet_invest_ratio` | cash-flow.cash_meet_invest_ratio | 现金满足投资比率；官方契约未明确具体数值量纲，本次保留空单位，不作推断。 | `verified` |
| 同花顺-fuyao | `cash-flow.cash_operating_index` | cash-flow.cash_operating_index | 现金营运指数；官方契约未明确具体数值量纲，本次保留空单位，不作推断。 | `verified` |
| 同花顺-fuyao | `cash-flow.net_profit_cash_content` | cash-flow.net_profit_cash_content | 净利润现金含量；官方契约未明确具体数值量纲，本次保留空单位，不作推断。 | `verified` |
| 同花顺-fuyao | `cash-flow.operating_cash_flow_net_divide_income` | cash-flow.operating_cash_flow_net_divide_income | 销售现金比率；接口值按百分数表达。 | `verified` |
| 同花顺-fuyao | `cash_meet_invest_ratio` | cash-flow.cash_meet_invest_ratio | 旧登记的无分组叶名身份；当前完整路径为 cash-flow.cash_meet_invest_ratio。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `cash_operating_index` | cash-flow.cash_operating_index | 旧登记的无分组叶名身份；当前完整路径为 cash-flow.cash_operating_index。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `cash_ratio` | solvency.cash_ratio | 旧登记的无分组叶名身份；当前完整路径为 solvency.cash_ratio。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `catalog` | a-share-index/catalog/ths-index-list | — | `unverified` |
| 同花顺-fuyao | `constituents` | a-share-index/constituents/ths-stock-list | — | `unverified` |
| 同花顺-fuyao | `continue_day_text` | continue_day_text | 连板文本，例如 `首板`、`5天4板`。 | `verified` |
| 同花顺-fuyao | `current_assets_turnover_ratio` | operation.current_assets_turnover_ratio | 旧登记的无分组叶名身份；当前完整路径为 operation.current_assets_turnover_ratio。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `current_ratio` | solvency.current_ratio | 旧登记的无分组叶名身份；当前完整路径为 solvency.current_ratio。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `date_ms` | date_ms | 项目按 probe_trading_day 生成的 Asia/Shanghai 零点毫秒 Unix 时间戳，作为涨停、跌停及炸板池接口的 date_ms 请求参数；该根字段不是 Fuyao 响应字段，也不能代替来源实际数据日。 | `disproved` |
| 同花顺-fuyao | `ded_weighted_roe` | profitability.index_deduct_weighted_avg_roe | 项目生成的 H1 摘要别名：将 profitability.index_deduct_weighted_avg_roe 原值复制到 market.h1_indicators.<code>.ded_weighted_roe；不是 Fuyao 上游键。完整源字段释义为扣非加权净资产收益率，单位 %。 | `disproved` |
| 同花顺-fuyao | `dump` | dump/market-dumps/{daily-k,daily-k-10d,adjustment-factors}/download-url | — | `unverified` |
| 同花顺-fuyao | `earned_interest_multiple` | solvency.earned_interest_multiple | 旧登记的无分组叶名身份；当前完整路径为 solvency.earned_interest_multiple。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `ex_date_ms` | ex_date_ms | 除权除息日，Asia/Shanghai 00:00:00 毫秒 Unix 时间戳。 | `verified` |
| 同花顺-fuyao | `fin_report` | fin_report | 项目财务指标采集器记录成功返回非空指标所用的 report 请求期标签；它不是指标响应中的独立上游字段，也不单独证明指标实际所属报告期。 | `disproved` |
| 同花顺-fuyao | `financials` | stocks.<ticker>.financials | 采集器按股票归并 income_q、income_a、balance_q、cashflow_q 四个报表输出数组的对象容器；不是可独立解释或赋予单一单位的财务指标。叶路径语义按各自接口字段维护。 | `disproved` |
| 同花顺-fuyao | `first_seal_time` | first_seal_time | 炸板股票当日首次封板时间，上海时区 HH:mm；上游缺失时为 null。 | `verified` |
| 同花顺-fuyao | `fiscal_period` | fiscal_period | `FY` / `Q1` / `Q2` / `Q3` / `Q4`。 | `verified` |
| 同花顺-fuyao | `fixed_asset_invest_expansion_ratio` | growth.fixed_asset_invest_expansion_ratio | 旧登记将 ability/index_id 叶名误作 fin_indicators 根级路径；当前响应与解析器不输出该无分组根键，实际路径为 fin_indicators.growth.fixed_asset_invest_expansion_ratio。此记录只退役旧路径身份，不否定嵌套字段语义。 | `disproved` |
| 同花顺-fuyao | `growth.calculate_operating_income_yoy_growth_ratio` | growth.calculate_operating_income_yoy_growth_ratio | 该股票所选财报期营业收入相较上年同期的同比增长率；按百分数值返回。2026H1 样本按（本期营业收入－上年同期营业收入）／abs（上年同期营业收入）×100 复算吻合。 | `verified` |
| 同花顺-fuyao | `growth.calculate_operating_profit_yoy_growth_ratio` | growth.calculate_operating_profit_yoy_growth_ratio | 该股票所选财报期营业利润相较上年同期的同比增长率；按百分数值返回。2026H1 样本按（本期营业利润－上年同期营业利润）／abs（上年同期营业利润）×100 复算吻合。 | `verified` |
| 同花顺-fuyao | `growth.calculate_parent_holder_net_profit_yoy_growth_ratio` | growth.calculate_parent_holder_net_profit_yoy_growth_ratio | 该股票所选财报期归属于母公司股东、所有者或上市公司股东的净利润相较上年同期的同比增长率；按百分数值返回。2026H1 样本按（本期归母净利润－上年同期归母净利润）／abs（上年同期归母净利润）×100 复算吻合。 | `verified` |
| 同花顺-fuyao | `growth.fixed_asset_invest_expansion_ratio` | growth.fixed_asset_invest_expansion_ratio | 固定资产账面价值同比变动率，按百分数值返回；2026H1正式报告横向实证支持合并口径固定资产账面价值变化率。具体上游计算和基期修订策略未获接口契约确认。 | `verified` |
| 同花顺-fuyao | `growth.total_assets_growth_ratio` | growth.total_assets_growth_ratio | 总资产增长率；接口值按百分数表达。2026H1样本中按本期末合并总资产相对上期末未调整合并总资产复算；中华企业报告使用调整后比较基数，差异另行保留。 | `verified` |
| 同花顺-fuyao | `h1_indicators` | market.h1_indicators | 项目按股票代码组装的 H1 指标摘要对象容器；不是 Fuyao 响应中的单一业务字段。 | `disproved` |
| 同花顺-fuyao | `h1_indicators_ready` | market.h1_indicators_ready | 项目生成的 H1 可用性哨兵；取首只股票的当年中报指标请求是否返回，不是 Fuyao 原始字段，也不保证每只股票都完整返回。 | `disproved` |
| 同花顺-fuyao | `high_price` | snapshot.high_price | 旧无分组根路径身份；当前完整采集路径为 snapshot.high_price。官方接口将 high_price 列在 data.item[]，项目采集输出将 item 保存在 stocks.<代码>.snapshot。本记录只退役裸叶来源路径。 | `disproved` |
| 同花顺-fuyao | `index_deduct_weighted_avg_roe` | profitability.index_deduct_weighted_avg_roe | 旧登记的无分组叶名身份；当前完整路径为 profitability.index_deduct_weighted_avg_roe。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `index_weighted_avg_roe` | profitability.index_weighted_avg_roe | 旧无分组根路径身份；当前完整字段路径为 profitability.index_weighted_avg_roe，裸叶不是当前解析响应的根级独立字段。 | `disproved` |
| 同花顺-fuyao | `indicators` | a-share/financials/indicators | 财务能力分组中的指标条目数组容器；每个条目以 index_id 标识指标并以 value 保存对应值，不是单一财务指标。项目适配器读取该数组后展平为 {ability: {index_id: value}}，采集输出路径为 stocks.<ticker>.fin_indicators.<ability>.<index_id>。 | `verified` |
| 同花顺-fuyao | `inventory_turnover_ratio` | operation.inventory_turnover_ratio | 旧登记的无分组叶名身份；当前完整路径为 operation.inventory_turnover_ratio。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `keyword_list` | keyword_list | 关键词列表；无关键词时返回空数组。 | `verified` |
| 同花顺-fuyao | `last_price` | snapshot.last_price | 旧无分组根路径身份；当前完整采集路径为 snapshot.last_price。官方接口将 last_price 列在 data.item[]，项目采集输出将 item 保存在 stocks.<代码>.snapshot。本记录只退役裸叶来源路径。 | `disproved` |
| 同花顺-fuyao | `last_seal_time` | last_seal_time | 炸板股票当日最后一次封板时间，上海时区 HH:mm；上游缺失时为 null。 | `verified` |
| 同花顺-fuyao | `limit_up_reason` | limit_up_reason | 涨停原因；上游空字符串会标准化为 `null`。 | `verified` |
| 同花顺-fuyao | `list` | meta/tickers/list | — | `unverified` |
| 同花顺-fuyao | `long_term_debt_equity_ratio` | operation.long_term_debt_equity_ratio | 旧登记的无分组叶名身份；当前完整路径为 operation.long_term_debt_equity_ratio。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `low_price` | snapshot.low_price | 旧无分组根路径身份；当前完整采集路径为 snapshot.low_price。官方接口将 low_price 列在 data.item[]，项目采集输出将 item 保存在 stocks.<代码>.snapshot。本记录只退役裸叶来源路径。 | `disproved` |
| 同花顺-fuyao | `market` | market | Fuyao 采集器保存市场级结果的顶层对象容器，包含基准、涨跌停池和异动等独立输出路径；不是单一市场业务指标。各子路径按对应采集单元维护。 | `disproved` |
| 同花顺-fuyao | `net_profit_cash_content` | cash-flow.net_profit_cash_content | 旧登记的无分组叶名身份；当前完整路径为 cash-flow.net_profit_cash_content。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `open_price` | snapshot.open_price | 旧无分组根路径身份；当前完整采集路径为 snapshot.open_price。官方接口将 open_price 列在 data.item[]，项目采集输出将 item 保存在 stocks.<代码>.snapshot。本记录只退役裸叶来源路径。 | `disproved` |
| 同花顺-fuyao | `operating_cash_flow_net_divide_income` | cash-flow.operating_cash_flow_net_divide_income | 旧登记的无分组叶名身份；当前完整路径为 cash-flow.operating_cash_flow_net_divide_income。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `operation.current_assets_turnover_ratio` | operation.current_assets_turnover_ratio | 流动资产周转率；官方文档说明周转率通常按“次”展示。 | `verified` |
| 同花顺-fuyao | `operation.inventory_turnover_ratio` | operation.inventory_turnover_ratio | 存货周转率；官方文档说明周转率通常按“次”展示。 | `verified` |
| 同花顺-fuyao | `operation.long_term_debt_equity_ratio` | operation.long_term_debt_equity_ratio | 长期负债权益比率；官方契约未明确具体数值量纲，本次保留空单位，不作推断。 | `verified` |
| 同花顺-fuyao | `operation.receive_account_turnover_ratio` | operation.receive_account_turnover_ratio | 应收账款周转率；官方文档说明周转率通常按“次”展示。 | `verified` |
| 同花顺-fuyao | `operation.total_assets_turnover_ratio` | operation.total_assets_turnover_ratio | 总资产周转率；官方文档说明周转率通常按“次”展示。 | `verified` |
| 同花顺-fuyao | `pay_dividends_profits_interest_cash` | pay_dividends_profits_interest_cash | 分配股利、利润或偿付利息支付的现金（原币元）。 | `verified` |
| 同花顺-fuyao | `pay_fixed_assets_etc_cash` | pay_fixed_assets_etc_cash | 购建固定资产、无形资产和其他长期资产支付的现金（原币元）。 | `verified` |
| 同花顺-fuyao | `pb_mrq` | valuation.pb_mrq | 已退役的旧无分组来源路径；当前完整采集路径为 valuation.pb_mrq。本条只处置路径身份，不否定目标字段的语义或单位。 | `disproved` |
| 同花顺-fuyao | `pcf_ttm` | valuation.pcf_ttm | 已退役的旧无分组来源路径；当前完整采集路径为 valuation.pcf_ttm。本条只处置路径身份，不否定目标字段的语义或单位。 | `disproved` |
| 同花顺-fuyao | `pe_mrq` | valuation.pe_mrq | 旧无分组根路径身份；当前完整采集路径为 valuation.pe_mrq。接口响应把该叶字段放在 data.item[]，项目采集输出则将 item 保存在 stocks.<代码>.valuation。本记录只退役裸叶来源路径。 | `disproved` |
| 同花顺-fuyao | `pe_ttm` | valuation.pe_ttm | 旧无分组根路径身份；当前完整采集路径为 valuation.pe_ttm。接口响应把该叶字段放在 data.item[]，项目采集输出则将 item 保存在 stocks.<代码>.valuation。本记录只退役裸叶来源路径。 | `disproved` |
| 同花顺-fuyao | `period_end_ms` | period_end_ms | 报告期末（Asia/Shanghai 零点毫秒戳）。 | `verified` |
| 同花顺-fuyao | `prev_price` | snapshot.prev_price | 旧无分组根路径身份；当前完整采集路径为 snapshot.prev_price。官方接口将 prev_price 列在 data.item[]，项目采集输出将 item 保存在 stocks.<代码>.snapshot。本记录只退役裸叶来源路径。 | `disproved` |
| 同花顺-fuyao | `price_change` | snapshot.price_change | 已退役的旧无分组来源路径；当前完整采集路径为 snapshot.price_change。本条只处置路径身份，不否定目标字段的语义或单位。 | `disproved` |
| 同花顺-fuyao | `price_change_ratio_pct` | snapshot.price_change_ratio_pct | 已退役的旧无分组来源路径；当前完整采集路径为 snapshot.price_change_ratio_pct。本条只处置路径身份，不否定目标字段的语义或单位。 | `disproved` |
| 同花顺-fuyao | `probe_trading_day` | probe_trading_day | 项目调用 last_completed_trading_day() 后生成的请求日期标签，并用于构造 date_ms；不是 Fuyao 响应字段，也不单独证明响应的实际数据日期。 | `disproved` |
| 同花顺-fuyao | `profitability.index_deduct_weighted_avg_roe` | profitability.index_deduct_weighted_avg_roe | 扣非加权净资产收益率；接口值按百分数表达。 | `verified` |
| 同花顺-fuyao | `profitability.index_weighted_avg_roe` | profitability.index_weighted_avg_roe | 加权平均净资产收益率；接口值按百分数表达。年化与非年化比较按发行人报告明确披露的口径归一。 | `verified` |
| 同花顺-fuyao | `profitability.sale_gross_margin` | profitability.sale_gross_margin | 销售毛利率；可比样本按（合并营业收入－合并营业成本）/合并营业收入×100%复算。 | `verified` |
| 同花顺-fuyao | `profitability.sale_net_interest_ratio` | profitability.sale_net_interest_ratio | 销售净利率；可比样本按合并净利润/合并营业收入×100%复算。 | `verified` |
| 同花顺-fuyao | `profitability.total_assets_net_ratio` | profitability.total_assets_net_ratio | 总资产收益率；接口值按百分数表达。2026H1样本中按当期合并净利润除以本期末与上期末未调整合并总资产的均值复算；该样本关系不外推为所有期间的通用算法。 | `verified` |
| 同花顺-fuyao | `ps_ttm` | valuation.ps_ttm | 已退役的旧无分组来源路径；当前完整采集路径为 valuation.ps_ttm。本条只处置路径身份，不否定目标字段的语义或单位。 | `disproved` |
| 同花顺-fuyao | `quick_ratio` | solvency.quick_ratio | 旧登记的无分组叶名身份；当前完整路径为 solvency.quick_ratio。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `rank_change` | rank_change | 排名变化，正数表示上升，负数表示下降；上游缺失时为 `null`。 | `verified` |
| 同花顺-fuyao | `rank_trend` | rank_trend | 排名趋势：`up` / `down` / `flat` / `unknown`。 | `verified` |
| 同花顺-fuyao | `receive_account_turnover_ratio` | operation.receive_account_turnover_ratio | 旧登记的无分组叶名身份；当前完整路径为 operation.receive_account_turnover_ratio。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `report_date_ms` | report_date_ms | 财务报表披露日，即该报表公开披露的日期；不是报告期末 | `verified` |
| 同花顺-fuyao | `revenue_ttm` | revenue_ttm | 项目回算的营业收入 TTM 近似兜底值：最近上一年度 Q4 累计 operating_income + 本期累计 operating_income − 上年同期累计 operating_income。不是 Fuyao 原始响应字段；与东财 Push2 f104 的营业总收入 TTM 口径不同，仅在统一输出缺少值时填入。 | `disproved` |
| 同花顺-fuyao | `sale_gross_margin` | profitability.sale_gross_margin | 旧无分组根路径身份；当前完整字段路径为 profitability.sale_gross_margin，裸叶不是当前解析响应的根级独立字段。 | `disproved` |
| 同花顺-fuyao | `sale_net_interest_ratio` | profitability.sale_net_interest_ratio | 旧无分组根路径身份；当前完整字段路径为 profitability.sale_net_interest_ratio，裸叶不是当前解析响应的根级独立字段。 | `disproved` |
| 同花顺-fuyao | `search` | meta/tickers/search | — | `unverified` |
| 同花顺-fuyao | `solvency.assets_debt_ratio` | solvency.assets_debt_ratio | 资产负债率；可比样本按合并负债合计/合并资产总计×100%复算。 | `verified` |
| 同花顺-fuyao | `solvency.cash_ratio` | solvency.cash_ratio | 现金比率；接口值按百分数表达。 | `verified` |
| 同花顺-fuyao | `solvency.current_ratio` | solvency.current_ratio | 流动比率；官方契约未明确具体数值量纲，本次保留空单位，不作推断。 | `verified` |
| 同花顺-fuyao | `solvency.earned_interest_multiple` | solvency.earned_interest_multiple | 已获利息倍数；官方文档说明已获利息倍数按“倍”展示。 | `verified` |
| 同花顺-fuyao | `solvency.quick_ratio` | solvency.quick_ratio | 速动比率；官方契约未明确具体数值量纲，本次保留空单位，不作推断。 | `verified` |
| 同花顺-fuyao | `total_assets_growth_ratio` | growth.total_assets_growth_ratio | 旧登记的无分组叶名身份；当前完整路径为 growth.total_assets_growth_ratio。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `total_assets_net_ratio` | profitability.total_assets_net_ratio | 旧登记的无分组叶名身份；当前完整路径为 profitability.total_assets_net_ratio。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `total_assets_turnover_ratio` | operation.total_assets_turnover_ratio | 旧登记的无分组叶名身份；当前完整路径为 operation.total_assets_turnover_ratio。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `turnover` | snapshot.turnover | 已退役的旧无分组来源路径；当前完整采集路径为 snapshot.turnover。本条只处置路径身份，不否定目标字段的语义或单位。 | `disproved` |
| 同花顺-fuyao | `valuation.pcf_ttm` | valuation.pcf_ttm | 市现率 PCF_TTM（总市值 / 经营现金流 TTM） | `verified` |
| 同花顺-fuyao | `valuations` | a-share/valuations/snapshot | — | `unverified` |
| 同花顺-fuyao | `volume` | snapshot.volume | 已退役的旧无分组来源路径；当前完整采集路径为 snapshot.volume。本条只处置路径身份，不否定目标字段的语义或单位。 | `disproved` |
| 同花顺-fuyao | `weighted_roe` | profitability.index_weighted_avg_roe | 项目生成的 H1 摘要别名：将 profitability.index_weighted_avg_roe 原值复制到 market.h1_indicators.<code>.weighted_roe；不是 Fuyao 上游键。完整源字段释义为加权平均净资产收益率，单位 %。 | `disproved` |
| 央视网(新闻联播) | `date` | cctv_news_broadcast_edition_date | 央视网《新闻联播》按日栏目页所对应的节目期次日期。它不表示单条新闻的事件日、单条报道的独立发布时间或本次采集日。 | `verified` |
| 巨潮(cninfo) | `answer` | answer | 上市公司对该问题的回复正文；尚无回复时为空 | `verified` |
| 巨潮(cninfo) | `answerer` | answerer | 回复记录标注的答复主体/作者；尚无回复时为空，不据此推断自然人身份 | `verified` |
| 巨潮(cninfo) | `ask_time` | ask_time | 互动易问答记录的发布时间戳；由 pubDate Unix 毫秒转换为本机本地时区的分钟字符串 | `verified` |
| 市场源(market_sources) | `change_type` | change_type | 盘口异动类型请求代码回显。market_sources.stock_changes_8201 采集单元固定回显字符串 8201，项目代码将其标为“火箭发射”；这是查询类别标记，不是上游逐条行情记录独立返回的业务字段。其他 type 代码未由本次证据确认。 | `verified` |
| 市场源(market_sources) | `col_02` | kpl_sector_strength_value | 开盘啦精选板块强度综合数值；在 kpl_plate_strength 子接口中，原始 row[2] 与解析后的 strength 同值。该指标用于比较板块强度，具体公式与计量单位未公开。 | `verified` |
| 市场源(market_sources) | `col_03` | change_pct | 板块涨跌幅；在 kpl_plate_strength 子接口中，原始 row[3] 与同记录已登记字段 change_pct 同值。 | `verified` |
| 市场源(market_sources) | `col_05` | amount | 板块成交额；在 kpl_plate_strength 子接口中，原始 row[5] 与同记录已登记字段 amount 同值。金额单位未由本核验确定。 | `verified` |
| 市场源(market_sources) | `dt` | zt / dt | 涨停 / 跌停总数 | `unverified` |
| 市场源(market_sources) | `fall_dist` | rise_dist / fall_dist | 待破解 | `unverified` |
| 市场源(market_sources) | `fall_num` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | `unverified` |
| 市场源(market_sources) | `flat` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | `unverified` |
| 市场源(market_sources) | `limit_time` | limit_time | 涨停时间；值为 Unix 秒时间戳。首次封板或末次封板口径未由本证据单独确认。 | `verified` |
| 市场源(market_sources) | `q_zrcs` | s_zrcs / q_zrcs | 昨日沪市 / 昨日全市成交额 | `unverified` |
| 市场源(market_sources) | `qscln` | szln / qscln | 待破解 | `unverified` |
| 市场源(market_sources) | `rise_dist` | rise_dist / fall_dist | 待破解 | `unverified` |
| 市场源(market_sources) | `rise_num` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | `unverified` |
| 市场源(market_sources) | `s_zrcs` | s_zrcs / q_zrcs | 昨日沪市 / 昨日全市成交额 | `unverified` |
| 市场源(market_sources) | `sjdt` | sjzt / sjdt | 待破解 | `unverified` |
| 市场源(market_sources) | `sjzt` | sjzt / sjdt | 待破解 | `unverified` |
| 市场源(market_sources) | `stdt` | stzt / stdt | ST 涨停 / 跌停 | `unverified` |
| 市场源(market_sources) | `strength` | kpl_sector_strength_value | 开盘啦精选板块强度综合数值；开盘啦官方说明其由板块权重个股、涨停数量、人气、成交额及市场情绪等多维度综合形成，用于比较板块强度。具体公式与计量单位未公开。 | `verified` |
| 市场源(market_sources) | `stzt` | stzt / stdt | ST 涨停 / 跌停 | `unverified` |
| 市场源(market_sources) | `szln` | szln / qscln | 待破解 | `unverified` |
| 市场源(market_sources) | `up_ratio` | up_ratio / up_ratio_num | 封板率 / 封板数量 | `unverified` |
| 市场源(market_sources) | `up_ratio_num` | up_ratio / up_ratio_num | 封板率 / 封板数量 | `unverified` |
| 市场源(market_sources) | `zt` | zt / dt | 涨停 / 跌停总数 | `unverified` |
| 开盘啦(kpl) | `Theme` | Theme/InfoBKR | — | `unverified` |
| 开盘啦(kpl_limit_up_detail) | `amount` | amount | 成交额；与 KPH turnover 两日逐值一致 | `verified` |
| 开盘啦(kpl_limit_up_detail) | `amplitude` | amplitude | 当日振幅=(当日最高价-最低价)/前一交易日收盘价×100% | `verified` |
| 开盘啦(kpl_limit_up_detail) | `main_inflow` | main_inflow | 主力净流入；与 KPH net_inflow 两日逐值一致 | `verified` |
| 开盘啦(kpl_limit_up_detail) | `max_seal` | max_seal | 最大封单金额；与 KPH seal_money 三个交易日逐股逐值一致 | `verified` |
| 开盘啦(kpl_limit_up_detail) | `raw_columns.col_15` | limit_up_streak_count | 当前连续涨停板数（当前连板数）；不是 N 天 M 板标签中的窗口涨停次数 M | `verified` |
| 开盘啦(kpl_limit_up_detail) | `raw_columns.col_16` | has_intraday_limit_up_break | 涨停个股在当日是否曾发生炸板的二值状态标记（1=东财官方涨停股池“炸板次数”>0，0=炸板次数=0）。2026-11-12、11-16、11-17 三个完整数据日全量逐股对照 106/106 命中；不代表炸板次数或具体时点，也不等同于进入东财“炸板股池”。开盘啦未公开该原始列标签，这是实证释义，不是 KPL 官方接口契约。 | `verified` |
| 开盘啦(kpl_limit_up_detail) | `raw_columns.col_17` | amplitude | 当日振幅=(当日最高价-最低价)/前一交易日收盘价×100% | `verified` |
| 开盘啦(kpl_limit_up_detail) | `raw_columns.col_18` | kpl_limit_up_sequence_label | 开盘啦涨停表现列表的描述性板数标签；保留样本非空值均形如 `N天M板` 或 `N连板`。这只是 KPL 自身的文字标签，不与 KPH 的 limit_tag/limit_count 建立等价。 | `verified` |
| 开盘啦(kpl_limit_up_detail) | `raw_columns.col_19` | sector_code | 行业/板块分类代码（具体分类体系与层级未确认；不与 KPH industry_id 保证逐值等同） | `verified` |
| 开盘啦(kpl_limit_up_detail) | `raw_columns.col_20` | kpl_category_limit_up_stock_count | 同一来源交易日内，按 raw_columns.col_19 分类代码分组后，该代码对应的 KPL DailyLimitPerformance 涨停梯队返回记录数（采集器合并 PidType=1..5 响应）；不确认 col_19 的具体分类体系/层级，也不等同于 KPH 或开盘红的同名计数 | `verified` |
| 开盘啦(kpl_limit_up_detail) | `raw_columns.col_21` | price | 现价（元；数据日收盘后采集时对应当日收盘价） | `verified` |
| 开盘啦(kpl_limit_up_detail) | `seal_amount` | seal_amount | 封单量；与 KPH seal_amount 三个交易日逐股逐值一致，计量单位未确认 | `verified` |
| 开盘啦(kpl_limit_up_detail) | `turnover_real` | turnover_real | 实际换手率；与 KPH turnover_rate 两日逐值一致 | `verified` |
| 开盘啦(kpl_limit_up_detail) | `zt_time` | limit_time | 涨停时间；与 KPH limit_time 两日逐值一致 | `verified` |
| 开盘红 | `industry_id` | industry_id | 行业分类 ID；与 KPL sector_code 在来源日期对齐的 420 组对照中 417 组相同、3 组不同；分类体系或层级未确认，保留各来源原码 | `verified` |
| 开盘红 | `industry_limit_up_count` | kph_industry_limit_up_count | 按开盘红接口自身 industry_id 分类关联的当日涨停股票家数。统计集合及行业分类体系未公开；部分值不等于本接口当前完整分页响应内该分类的记录数，不外推为全市场完整行业总数。 | `verified` |
| 开盘红 | `limit_count` | limit_count | 连板数；从 KPL 原始 row[18] 的 N天M板解析 M，30 个可解析值 30/30 一致 | `verified` |
| 开盘红 | `limit_tag` | limit_tag | 连板标签；与 KPL 原始 row[18] 可见的 33 条非空值 33/33 一致 | `verified` |
| 开盘红 | `limit_time` | limit_time | 涨停时间；与 KPL zt_time 370 组、8 个交易日逐值一致 | `verified` |
| 开盘红 | `market_cap` | float_market_value | 流通市值；与 KPL 实际流通字段 369/370 逐值一致；1 组相差约 0.8025%，不按舍入等价处理 | `verified` |
| 开盘红 | `net_inflow` | main_inflow | 主力净流入；与 KPL main_inflow 370 组、8 个交易日逐值一致 | `verified` |
| 开盘红 | `open_time` | — | 开板时间；AxData 0.1.4 将原始 row[7] 映射为时间戳；370 组样本均为 0，暂无非零值核验 | `unverified` |
| 开盘红 | `reason` | limit_up_reason | 涨停原因；与 KPL reason 367/370 逐字一致，3 组文本差异保留来源原值 | `verified` |
| 开盘红 | `seal_amount` | seal_amount | 封单量；与 KPL seal_amount 370 组、8 个交易日逐值一致，计量单位未确认 | `verified` |
| 开盘红 | `seal_money` | max_seal | 封单金额；与 KPL max_seal 370 组、8 个交易日逐值一致 | `verified` |
| 开盘红 | `themes` | themes | 题材标签列表；与 KPL sector 完整列表 360/370 一致、至少一项重合 369/370；保留来源标签口径差异 | `verified` |
| 开盘红 | `turnover` | amount | 成交额；与 KPL amount 370 组、8 个交易日逐值一致 | `verified` |
| 开盘红 | `turnover_rate` | turnover_real | 实际换手率；与 KPL turnover_real 370 组、8 个交易日逐值一致 | `verified` |
| 开盘红(Levistock适配) | `buy_amount` | buy_amount / sell_amount | 待破解 | `unverified` |
| 开盘红(Levistock适配) | `dt` | zt / dt | 涨停 / 跌停总数 | `unverified` |
| 开盘红(Levistock适配) | `fall_dist` | rise_dist / fall_dist | 待破解 | `unverified` |
| 开盘红(Levistock适配) | `fall_num` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | `unverified` |
| 开盘红(Levistock适配) | `flat` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | `unverified` |
| 开盘红(Levistock适配) | `industry_id` | industry_id | 开盘红接口返回的行业分类 ID，作为 KPH 自身记录的分类键。具体分类体系和层级未公开；本定义不意味着该 ID 与 KPL sector_code 等价，也不推断它对应任何特定行业标准。 | `verified` |
| 开盘红(Levistock适配) | `industry_zt` | kph_industry_limit_up_count | 按开盘红接口自身 industry_id 分类关联的当日涨停股票家数。统计集合及行业分类体系未公开；部分值不等于本接口当前完整分页响应内该分类的记录数，不外推为全市场完整行业总数。 | `verified` |
| 开盘红(Levistock适配) | `limit_count` | limit_tag / limit_count | 待破解 | `unverified` |
| 开盘红(Levistock适配) | `limit_tag` | limit_tag / limit_count | 待破解 | `unverified` |
| 开盘红(Levistock适配) | `limit_time` | limit_time | 涨停时间；值为 Unix 秒时间戳。首次封板或末次封板口径未由本证据单独确认。 | `verified` |
| 开盘红(Levistock适配) | `net_inflow` | net_inflow / market_cap | 待破解 | `unverified` |
| 开盘红(Levistock适配) | `open_time` | limit_time / open_time | 待破解 | `unverified` |
| 开盘红(Levistock适配) | `q_zrcs` | s_zrcs / q_zrcs | 昨日沪市 / 昨日全市成交额 | `unverified` |
| 开盘红(Levistock适配) | `qscln` | szln / qscln | 待破解 | `unverified` |
| 开盘红(Levistock适配) | `rise_dist` | rise_dist / fall_dist | 待破解 | `unverified` |
| 开盘红(Levistock适配) | `rise_num` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | `unverified` |
| 开盘红(Levistock适配) | `s_zrcs` | s_zrcs / q_zrcs | 昨日沪市 / 昨日全市成交额 | `unverified` |
| 开盘红(Levistock适配) | `seal_amount` | seal_amount / seal_money | 待破解 | `unverified` |
| 开盘红(Levistock适配) | `seal_money` | seal_amount / seal_money | 待破解 | `unverified` |
| 开盘红(Levistock适配) | `sell_amount` | buy_amount / sell_amount | 待破解 | `unverified` |
| 开盘红(Levistock适配) | `sjdt` | sjzt / sjdt | 待破解 | `unverified` |
| 开盘红(Levistock适配) | `sjzt` | sjzt / sjdt | 待破解 | `unverified` |
| 开盘红(Levistock适配) | `stdt` | stzt / stdt | ST 涨停 / 跌停 | `unverified` |
| 开盘红(Levistock适配) | `stzt` | stzt / stdt | ST 涨停 / 跌停 | `unverified` |
| 开盘红(Levistock适配) | `szln` | szln / qscln | 待破解 | `unverified` |
| 开盘红(Levistock适配) | `turnover` | turnover / turnover_rate | 成交额 / 换手率% | `unverified` |
| 开盘红(Levistock适配) | `zt` | zt / dt | 涨停 / 跌停总数 | `unverified` |
| 新浪(hq.sinajs) | `[12]` | [12]-[19] | 买二~买五 量/价 | `verified` |
| 新浪(hq.sinajs) | `[32]` | quote_trading_status_code | 新浪实时行情交易状态码。本次保留样本中 00 表示常规交易状态（439/439 条均有正成交量）；03 表示停牌（唯一样本与发行人停牌公告、独立行情标记一致）。只确认已观察的 00、03，不外推未观察代码。 | `verified` |
| 新浪(扩展API) | `ask` | bid_vol/bid/last/ask/ask_vol | 五档价量 | `unverified` |
| 新浪(扩展API) | `ask_vol` | bid_vol/bid/last/ask/ask_vol | 五档价量 | `unverified` |
| 新浪(扩展API) | `bid` | bid_vol/bid/last/ask/ask_vol | 五档价量 | `unverified` |
| 新浪(扩展API) | `bid_vol` | bid_vol/bid/last/ask/ask_vol | 五档价量 | `unverified` |
| 新浪(扩展API) | `delta` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | `unverified` |
| 新浪(扩展API) | `gamma` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | `unverified` |
| 新浪(扩展API) | `item_tongbi` | item_tongbi | 同一报表项目相对上年同期的变动率，以小数比例表示；例如 0.01959 表示增长 1.959%。空字符串表示没有可用同比值，数值 0 表示同比变化为 0。 | `verified` |
| 新浪(扩展API) | `item_value` | item_value | 指定报表类别、报告期及主体口径下的财务报表科目值，与同一行的 item_field / item_title 绑定；不同科目的量纲不统一。已核实金额项目以人民币元存档，基本每股收益以元/股存档。空字符串用于无科目代码的分组行，null 表示缺值，均不是数值 0。 | `verified` |
| 新浪(扩展API) | `iv` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | `unverified` |
| 新浪(扩展API) | `last` | bid_vol/bid/last/ask/ask_vol | 五档价量 | `unverified` |
| 新浪(扩展API) | `limit_down` | limit_up / limit_down | 涨跌停价 | `unverified` |
| 新浪(扩展API) | `limit_up` | limit_up / limit_down | 涨跌停价 | `unverified` |
| 新浪(扩展API) | `netamount` | netamount | 个股资金流记录中的净流入金额原始值（元；新浪帮助页展示单位为万元） | `verified` |
| 新浪(扩展API) | `open` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | `unverified` |
| 新浪(扩展API) | `prev_close` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | `unverified` |
| 新浪(扩展API) | `strike` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | `unverified` |
| 新浪(扩展API) | `theta` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | `unverified` |
| 新浪(扩展API) | `trade` | trade | 个股资金流记录中 opendate 对应行的行情价格快照（元/股）；不能默认视为官方收盘价 | `verified` |
| 新浪(扩展API) | `turnover` | turnover | 换手率原始值（万分比；换算为百分数时原值除以100） | `verified` |
| 新浪(扩展API) | `vega` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | `unverified` |
| 新浪(研报列表) | `date` | sina_research_report_publication_date | 新浪财经机构研报列表记录中标为“发布日期”的日期。它表示研报发布日期，不等同于财报报告期、报告正文所述事件日或本次列表响应的更新时间。 | `verified` |
| 新浪(研报列表) | `report_id` | sina_research_report_id | 新浪研报详情页 URL `/rptid/{id}/` 中的数字报告标识。 | `verified` |
| 沪深交易所 | `etf_sh.date` | sse_etf_scale_statistics_date | 上交所 ETF 规模统计记录中对应的统计日期（接口原始字段 STAT_DATE）。它是来源数据日期，不是目录目标数据日或采集运行日。 | `verified` |
| 沪深交易所 | `etf_sh.etf_type` | sse_etf_subcategory | 上交所 ETF 细分类型，由上交所 `ETF_TYPE` 原值提供；保留官方分类文本，不压缩成单市/跨市/跨境规则。 | `verified` |
| 沪深交易所 | `etf_sz.date` | szse_etf_current_scale_measurement_date | 深交所 ETF 列表中“当前规模（万份）”数值对应的统计日期，由官方列元数据 metadata.cols.dqgm 标题括号中的日期确定；不是列表页面日期、采集运行日或目录目标数据日。 | `verified` |
| 沪深交易所 | `etf_sz.listing_date` | szse_etf_listing_date | 深交所基金列表中，该基金在深圳证券交易所开始上市交易的日期；不是基金合同生效日、募集成立日或公告日。 | `verified` |
| 沪深交易所 | `etf_sz.shares_10k` | szse_etf_current_scale_shares_10k | 深交所 ETF 列表“当前规模（万份）”列所报的 ETF 基金份额数值，由每条记录 dqgm 列的展示数值解析。该列对应日期由同一响应 metadata.cols.dqgm 标题中的括号日期确定；官方说明 T 日晚间更新的 T 日规模仅供参考，以 T+1 日早间更新的 T 日规模为准。此定义仅适用于 etf_sz 分支。 | `verified` |
| 沪深交易所 | `sse_e_interaction[].answer_time` | sse_e_interaction_answer_time | 上证 e 互动条目中上市公司回答的显示时间；仅在存在回答块时有值，项目解析后输出标准化时间。 | `verified` |
| 沪深交易所 | `zqdm` | zqdm / zqjc | 代码 / 简称 | `verified` |
| 沪深交易所 | `zqjc` | zqdm / zqjc | 代码 / 简称 | `verified` |
| 百度(baidu) | `ma10avgprice` | ma5avgprice/ma10avgprice/ma20avgprice | 待破解 | `unverified` |
| 百度(baidu) | `ma20avgprice` | ma5avgprice/ma10avgprice/ma20avgprice | 待破解 | `unverified` |
| 百度(baidu) | `ma5avgprice` | ma5avgprice/ma10avgprice/ma20avgprice | 待破解 | `unverified` |
| 腾讯(qt.gtimg) | `[19]` | [19]-[28] | 卖一~卖五 价/量 | `verified` |
| 腾讯(qt.gtimg) | `[35]` | [35] | 价格/量/额 汇总 | `verified` |
| 腾讯(qt.gtimg) | `[53]` | [53] | 市盈率(静态/年报 LYR) | `verified` |
| 腾讯(qt.gtimg) | `[62]` | [62] | 年初至今涨跌幅(YTD, 前复权)（≡ push2 f122 / ulist f25 同源同值） | `verified` |
| 腾讯(qt.gtimg) | `[71]` | [71] | 近60交易日涨跌幅(前复权)（≡ push2 f121 / ulist f24 同值 84-86%） | `verified` |
| 腾讯(qt.gtimg) | `[84]` | [84] | 状态码(2026-08-15 20股破译): W=未盈利(688553)/U=同股不同权(688327 UW)/Y=科创板(688 全部)/D/F/N=交易状态(沪市恒定); 深市=空; 北交所920=NBFND | `verified` |
| 腾讯(qt.gtimg) | `[86]` | [86] 竞价失衡方向信号 | 方向级的收盘竞价失衡信号：在保留期内359条有信息样本中，[86]的正负号均与同条[3]-[85]同向。该关系与交易所公开的竞价参考价及未匹配量机制相容，但不证明[86]的数值就是未匹配量。尚未确认买卖侧、精确算法、单位、具体竞价阶段或腾讯官方字段标签。 | `verified` |
| 腾讯(qt.gtimg) | `[87]` | [87] 科创板标记 | 科创板相关标记；本次 18 个来源日中，3 只上交所公告确认的科创板样本均为 100，15 只非 688 对照证券均为空。上交所融资融券标的贵州茅台在相同来源日均为空，不支持通用两融资格标记解释。未证实腾讯官方字段契约、完整市场全集规则或其他枚举值。 | `verified` |
| 腾讯(qt.gtimg) | `[9]` | [9]-[18] | 买一~买五 价/量 | `verified` |
| 财联社(cls) | `brief` | title / brief | 标题 / 摘要 | `verified` |
| 财联社(cls) | `cur_heat` | rank / cur_heat | 当前热度排名 / 热度值 | `unverified` |
| 财联社(cls) | `level` | cls_telegraph_display_level_code | 财联社电报记录的网页展示等级代码。当前官方电报页对 A、B 使用红色文本，对 A 额外加粗；其他值走默认文本样式。官方页面脚本没有给出完整代码全集、代码业务名称、重要性排序或分类判定规则。 | `verified` |
| 财联社(cls) | `plate_code` | plate_code / plate_name | 板块代码 / 名称（风口板块） | `unverified` |
| 财联社(cls) | `plate_name` | plate_code / plate_name | 板块代码 / 名称（风口板块） | `unverified` |
| 财联社(cls) | `plates` | trade_date / plates | 轮动日期 / 当日 top10 板块列表 | `unverified` |
| 财联社(cls) | `rank` | rank / cur_heat | 当前热度排名 / 热度值 | `unverified` |
| 财联社(cls) | `stock_list` | cls_telegraph_related_stocks | 财联社电报条目附加的关联证券列表；列表项含证券代码与名称。空列表只表示该记录没有返回关联项，不推断正文未提及证券。列表项 pct 的单位、来源实际数据时点和是否固定为文章发布时状态尚未核实。 | `verified` |
| 财联社(cls) | `subjects` | cls_telegraph_subjects | 财联社电报条目关联的主题/题材标签列表；每项含官方主题 ID 与名称。该裁决不外推完整分类体系或标签互斥规则。 | `verified` |
| 财联社(cls) | `title` | title / brief | 标题 / 摘要 | `verified` |
| 财联社(cls) | `trade_date` | trade_date / plates | 轮动日期 / 当日 top10 板块列表 | `unverified` |
