# 字段聚合歧义与待拆分复核

> 本文由 `field_registry.json.source_fields` 生成。逐源完整路径记录是权威定义；本文只揭示按短 code 聚合时无法安全呈现的差异。
> `aggregation_status` 只描述兼容聚合视图，不会改写逐源 `status`。疑似合并文本由分隔符启发式识别，仅供人工检查，不自动拆字段或定案。
> 本文统计的定义缺口仅限列出的复核组；单来源或全空的定义缺口仍见 [元数据缺口](field_metadata_gaps.md) 与 [未知字段队列](unknown_fields.md)。

> 聚合歧义 136 个 code；聚合定义不完整 199 个 code；疑似合并文本 479 条逐源记录。

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
| ZHB-tipinfo · `[13]` | [13] | 解禁日 = 官方 RecentReleaseDate（二进制 `解禁数量:%.2f万` 实证；旧标"股权登记日/配股"为误译——Col[14] 量级=解禁股数万股, 与 Col[11]/[12] 配股重复赋值矛盾已解） | — | `verified` |
| 新浪(hq.sinajs) · `[13]` | [13] | 买二价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[13]` | [13] | 买三价 | 元 | `verified` |

### `[14]` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[14]` | [14] | 扣非净利润 (万元) = 官方 KfEarnMoney | — | `verified` |
| ZHB-tdxstat2 · `[14]` | [14] | 当日开盘集合竞价成交额 | 万元 | `verified` |
| ZHB-tipinfo · `[14]` | [14] | 解禁数量(万股) = 官方 ReleaseShares（二进制 `解禁数量:%.2f万` 实证） | — | `verified` |
| 新浪(hq.sinajs) · `[14]` | — | — | — | `unverified` |
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

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[16]` | [16] | 研发投入 RDInputFee（万元） | — | `verified` |
| ZHB-tdxstat2 · `[16]` | [16] | IPO 发行价 = 官方 IPO_Price | 元 | `verified` |
| ZHB-tipinfo · `[16]` | [16] | (老)增发募集金额(万元) | — | `verified` |
| 新浪(hq.sinajs) · `[16]` | — | — | — | `unverified` |
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

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[18]` | [18] | 截至T-1的20根K线涨跌幅 | — | `verified` |
| ZHB-tdxstat2 · `[18]` | [18] | 52周最低价 = 官方 HisLow | 元 | `verified` |
| ZHB-tipinfo · `[18]` | [18] | 恒空占位符 | — | `unverified` |
| 新浪(hq.sinajs) · `[18]` | — | — | — | `unverified` |
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

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[22]` | [22] | 形态/板块代码 ShapeValue | — | `verified` |
| 新浪(hq.sinajs) · `[22]` | [22]-[29] | 卖二~卖五 量/价 | 股/元 | `verified` |
| 腾讯(qt.gtimg) · `[22]` | — | — | — | `unverified` |

### `[23]` — ambiguous

聚合问题：meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[23]` | [23] | 待破解 | — | `verified` |
| 新浪(hq.sinajs) · `[23]` | [23] | 卖二价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[23]` | [23] | 卖三价 | 元 | `verified` |

### `[24]` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[24]` | [24] | 现金总额 CashZJ（万元） | — | `verified` |
| 新浪(hq.sinajs) · `[24]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[24]` | — | — | — | `unverified` |

### `[25]` — ambiguous

聚合问题：meaning_differs；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[25]` | [25] | 合同负债（万元） | 万元 | `verified` |
| 新浪(hq.sinajs) · `[25]` | [25] | 卖三价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[25]` | [25] | 卖四价 | 元 | `verified` |

### `[26]` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[26]` | [26] | 年内涨停天数 YearZTDay | — | `verified` |
| 新浪(hq.sinajs) · `[26]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[26]` | — | — | — | `unverified` |

### `[27]` — ambiguous

聚合问题：meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[27]` | [27] | 近 5 根K线涨跌幅 (%) | — | `verified` |
| 新浪(hq.sinajs) · `[27]` | [27] | 卖四价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[27]` | [27] | 卖五价 | 元 | `verified` |

### `[28]` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[28]` | [28] | 近 5 日涨跌幅 (%) | — | `verified` |
| 新浪(hq.sinajs) · `[28]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[28]` | — | — | — | `unverified` |

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

聚合问题：meaning_differs；source_statuses_differ；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[32]` | [32] | “几天几板”统计中的涨停板数（通达信 LastZTHzNum，官方接口说明为“几板”；精确统计口径未公开） | 板 | `verified` |
| 新浪(hq.sinajs) · `[32]` | [32] | 状态码 | - | `unverified` |
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

聚合问题：meaning_differs；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[7]` | [7] | T-1 日涨跌幅 (%) | — | `verified` |
| ZHB-tdxstat2 · `[7]` | [7] | 前日成交额 | 万元 | `verified` |
| ZHB-tipinfo · `[7]` | [7] | 重大事项停牌起始日 | — | `verified` |
| 新浪(hq.sinajs) · `[7]` | [7] | 卖一价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[7]` | [7] | 外盘 | 手 | `unverified` |

### `[86]` — incomplete

聚合问题：canonical_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 腾讯(qt.gtimg) · `[86]` | — | 收盘集合竞价净未匹配手数(带符号)（L2 机制确认） | 手 | `conflict` |

### `[8]` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[8]` | [8] | T-2 日涨跌幅 (%) | — | `verified` |
| ZHB-tdxstat2 · `[8]` | [8] | 前第二交易日涨跌停封单额（涨停为正，跌停为负） | 万元 | `verified` |
| ZHB-tipinfo · `[8]` | tipinfo.shareholder_change_date | 股东持股变动记录关联日期；可为交易日、区间截止日或权益变动协议签署日 | YYYYMMDD | `verified` |
| 新浪(hq.sinajs) · `[8]` | [8] | 成交量 | 股 | `verified` |
| 腾讯(qt.gtimg) · `[8]` | [8] | 内盘 | 手 | `unverified` |

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

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `amount` | amount | 成交额 | 元 | `verified` |
| TDX-eltdx(适配层) · `amount` | amount | 实时行情快照截至该时点的累计成交额；收盘样本与同一数据日 K 线成交额一致。 | 元 | `verified` |
| ZHB-tdxstat2 · `amount` | amount | T日总成交额 | 万元 | `verified` |
| reports · `amount` | amount | 成交额 | — | `verified` |
| 东财-datacenter(英文键) · `amount` | — | — | — | `unverified` |
| 东财-push2ex · `amount` | amount | 成交额 | 元 | `verified` |
| 市场源(market_sources) · `amount` | amount | 成交额 | — | `verified` |
| 开盘啦(kpl) · `amount` | amount | 成交额 | 元 | `unverified` |
| 开盘啦(kpl_limit_up_detail) · `amount` | amount | 成交额；与 KPH turnover 两日逐值一致 | 元 | `verified` |

### `amount_1d` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `amount_1d` | — | — | — | `unverified` |
| ZHB-tdxstat2 · `amount_1d` | amount_1d | 前一交易日总成交额 | 万元 | `verified` |
| 同花顺-fuyao · `amount_1d` | — | — | — | `unverified` |

### `amount_2d` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `amount_2d` | — | — | — | `unverified` |
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

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `change` | change | 价格涨跌额 | 元/股 | `verified` |
| TDX(双命名源) · `change` | — | — | — | `unverified` |
| 同花顺-fuyao · `change` | change | 当日涨跌幅，小数形式。 | 比例（小数） | `verified` |

### `change_pct` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `change_pct` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `change_pct` | change_pct | 涨跌幅 | % | `verified` |
| ZHB-tdxstat · `change_pct` | change_pct | 当日涨跌幅 | % | `verified` |
| 东财-push2ex · `change_pct` | change_pct | 当日涨跌幅（百分比）；接口原始值保留比 KPL col_22 更多的小数位，三个有效日期 271 组对照均在 0.02 个百分点内，按两位小数四舍五入后相等。 | % | `verified` |
| 市场源(market_sources) · `change_pct` | change_pct | 涨跌幅 | — | `verified` |
| 开盘啦(kpl) · `change_pct` | change_pct | 涨跌幅% | % | `unverified` |

### `change_pct_1d` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `change_pct_1d` | — | — | — | `unverified` |
| ZHB-tdxstat · `change_pct_1d` | change_pct_1d | T-1 日涨跌幅 | % | `verified` |

### `change_pct_2d` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `change_pct_2d` | — | — | — | `unverified` |
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
| 东财-datacenter(英文键) · `close` | — | — | — | `unverified` |
| 东财-热榜(em_hot) · `close` | close / zhangdie | 收盘价 / 涨跌额 | — | `verified` |
| 新浪(扩展API) · `close` | — | — | — | `unverified` |

### `code` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `code` | code | 股票代码 | 6位字符串 | `verified` |
| TDX-eltdx(适配层) · `code` | code | — | — | `unverified` |
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

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `date` | event_date | TDX XDXR（0x000f）权息/股本变迁事件日期；不是采集日期。现有契约未进一步区分公告日、股权登记日或除权除息日。 | - | `verified` |
| ZHB-tdxstat · `date` | date | 统计日期 | - | `verified` |
| ZHB-tdxstat2 · `date` | date | 统计日期 | - | `verified` |
| 东财-datacenter(英文键) · `date` | — | — | — | `unverified` |
| 同花顺-fuyao · `date` | — | — | — | `unverified` |
| 巨潮(cninfo) · `date` | — | — | — | `unverified` |
| 市场源(market_sources) · `date` | date | 日期 | — | `verified` |
| 开盘啦(kpl) · `date` | — | — | — | `unverified` |
| 新浪(扩展API) · `date` | — | — | — | `unverified` |

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

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `exchange` | exchange | — | — | `unverified` |
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

### `f111` — incomplete

聚合问题：meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f111` | f111 | 板级枚举 | - | `verified` |
| 东财-ulist239(np/get) · `f111` | f111 | — | — | `unverified` |

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

### `f126` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f126` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f126` | f126 | — | — | `unverified` |

### `f127` — ambiguous

聚合问题：meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f127` | f127 | 行业名称 | - | `verified` |
| 东财-ulist239(np/get) · `f127` | f127 | 委比 | — | `unverified` |

### `f128` — ambiguous

聚合问题：meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f128` | f128 | 板块领涨股名称 | - | `verified` |
| 东财-push2(stock/get) · `f128` | f128 | 地域板块名称 | - | `verified` |
| 东财-slist · `f128` | f128 | 板块龙头股名 | — | `verified` |
| 东财-ulist239(np/get) · `f128` | f128 | — | — | `unverified` |

### `f129` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f129` | — | — | — | `unverified` |
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

### `f139` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f139` | fund_super_sell | 东方财富“超大单”类别资金流出金额（当日，按该页面的资金流分类口径；不代表账户身份）。 | 元 | `verified` |
| 东财-ulist239(np/get) · `f139` | — | — | — | `conflict` |
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

### `f141` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f141` | — | — | — | `unverified` |
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

聚合问题：canonical_differs；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f148` | fund_small_sell | 小单类别的资金流出金额，不表示投资者账户身份 | 元 | `verified` |
| 东财-ulist239(np/get) · `f148` | f148 | — | — | `unverified` |
| 东财-资金流(em_fund_flow) · `f148` | fund_small_sell | 小单类别的资金流出金额，不表示投资者账户身份。 | 元 | `verified` |

### `f149` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f149` | fund_small_today | 小单类别资金净流入金额，等于流入金额减流出金额 | 元 | `verified` |
| 东财-ulist239(np/get) · `f149` | — | — | — | `unverified` |
| 东财-资金流(em_fund_flow) · `f149` | fund_small_today | 小单类别资金净流入金额，等于流入金额减流出金额。 | 元 | `verified` |

### `f15` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f15` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f15` | f15 | 最高价 | 元 | `verified` |

### `f152` — incomplete

聚合问题：meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f152` | f152 | — | — | `candidate` |
| 东财-ulist239(np/get) · `f152` | f152 | — | — | `unverified` |

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

### `f161` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f161` | — | — | — | `unverified` |
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

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f176` | — | — | — | `unverified` |
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

### `f185` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f185` | f185 | — | — | `verified` |
| 东财-ulist239(np/get) · `f185` | f185 | — | — | `verified` |

### `f186` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f186` | f186 | — | — | `verified` |
| 东财-ulist239(np/get) · `f186` | f186 | — | — | `verified` |

### `f187` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f187` | f187 | — | — | `verified` |
| 东财-ulist239(np/get) · `f187` | f187 | — | — | `verified` |

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

### `f190` — incomplete

聚合问题：meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f190` | f190 | 每股未分配利润 | 元/股 | `verified` |
| 东财-ulist239(np/get) · `f190` | f190 | — | — | `unverified` |

### `f191` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f191` | f191 | 委比 | % | `verified` |
| 东财-ulist239(np/get) · `f191` | f191 | — | — | `verified` |

### `f192` — incomplete

聚合问题：meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f192` | f192 | 委差 | 手 | `verified` |
| 东财-ulist239(np/get) · `f192` | f192 | — | — | `unverified` |

### `f193` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f193` | f193 | — | — | `verified` |
| 东财-ulist239(np/get) · `f193` | f193 | — | — | `verified` |

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

### `f2` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f2` | — | — | — | `unverified` |
| 东财-push2(stock/get) · `f2` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f2` | f2 | 现价 | 元 | `verified` |

### `f207` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f207` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f207` | f207 | — | — | `unverified` |

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

### `f250` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f250` | — | — | — | `unverified` |
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

### `f4` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f4` | — | — | — | `unverified` |
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

### `f49` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f49` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f49` | f49 | — | — | `unverified` |

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

聚合问题：canonical_differs；meaning_differs；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f59` | f59 | 涨跌幅 | % | `verified` |
| 东财-push2(stock/get) · `f59` | quote_price_precision_digits | 该证券实时行情报价的显示小数位数；在 fltt=1 响应中用于将价格整数还原为 fltt=2 报价。 | 位（小数位数） | `verified` |
| 东财-ulist239(np/get) · `f59` | f59 | — | — | `conflict` |

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

### `f80` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f80` | — | — | — | `unverified` |
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

### `growth` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `growth` | growth | — | — | `conflict` |

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

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 开盘红 · `industry_id` | industry_id | 行业分类 ID；与 KPL sector_code 在来源日期对齐的 420 组对照中 417 组相同、3 组不同；分类体系或层级未确认，保留各来源原码 | — | `verified` |
| 开盘红(Levistock适配) · `industry_id` | industry_id / industry_zt | 行业 ID / 同行业涨停数 | — | `unverified` |

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

### `item_tongbi` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 新浪(扩展API) · `item_tongbi` | item_tongbi | 同比（有才附 `_同比` 键） | — | `conflict` |

### `item_value` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 新浪(扩展API) · `item_value` | item_value | 科目值（字符串） | — | `conflict` |

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

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `last_price` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `last_price` | last_price | 最新价 / 现价 | — | `verified` |
| 同花顺-fuyao · `last_price` | snapshot.last_price | 旧无分组根路径身份；当前完整采集路径为 snapshot.last_price。官方接口将 last_price 列在 data.item[]，项目采集输出将 item 保存在 stocks.<代码>.snapshot。本记录只退役裸叶来源路径。 | 元 | `disproved` |

### `level` — ambiguous

聚合问题：meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `level` | level | 待破解 | — | `unverified` |
| 财联社(cls) · `level` | level | 快讯等级（重要性分级） | — | `unverified` |

### `limit_count` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2ex · `limit_count` | limit_up_streak_count | 当前连续涨停板数（当前连板数）；与同数据日 KPL col_15 的三个有效日期 271 组对照逐值相等。11 月 5 日次日回查存在集合和值差异，已单独记录且不计入正证据。 | 板 | `verified` |
| 市场源(market_sources) · `limit_count` | limit_count | 连板数 | — | `verified` |
| 开盘红 · `limit_count` | limit_count | 连板数；从 KPL 原始 row[18] 的 N天M板解析 M，30 个可解析值 30/30 一致 | 板 | `verified` |
| 开盘红(Levistock适配) · `limit_count` | limit_tag / limit_count | 待破解 | — | `unverified` |

### `limit_down` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `limit_down` | — | — | — | `unverified` |
| 新浪(扩展API) · `limit_down` | limit_up / limit_down | 涨跌停价 | — | `unverified` |

### `limit_down_price` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `limit_down_price` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `limit_down_price` | limit_down_price | 跌停价 | — | `verified` |

### `limit_tag` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 开盘红 · `limit_tag` | limit_tag | 连板标签；与 KPL 原始 row[18] 可见的 33 条非空值 33/33 一致 | — | `verified` |
| 开盘红(Levistock适配) · `limit_tag` | limit_tag / limit_count | 待破解 | — | `unverified` |

### `limit_time` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `limit_time` | limit_time | 涨停时间 | — | `unverified` |
| 开盘红 · `limit_time` | limit_time | 涨停时间；与 KPL zt_time 370 组、8 个交易日逐值一致 | Unix 秒 | `verified` |
| 开盘红(Levistock适配) · `limit_time` | limit_time / open_time | 待破解 | — | `unverified` |

### `limit_up` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `limit_up` | — | — | — | `unverified` |
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

### `locked_amount` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `locked_amount` | — | — | — | `unverified` |
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

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `main_buy` | — | — | — | `unverified` |
| 开盘啦(kpl) · `main_buy` | main_buy | 主力买入额 | 元 | `unverified` |

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

### `main_sell` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `main_sell` | — | — | — | `unverified` |
| 开盘啦(kpl) · `main_sell` | main_sell | 主力卖出额 | 元 | `unverified` |

### `margin_trading.balance_gr` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `margin_trading.balance_gr` | margin_trading.balance_gr | 融资余额单日环比增长率(%) | — | `conflict` |

### `margin_trading.chg_10d` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `margin_trading.chg_10d` | margin_trading.chg_10d | 标的证券近 10 日区间累计涨跌幅(%) | — | `conflict` |

### `margin_trading.chg_5d` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `margin_trading.chg_5d` | margin_trading.chg_5d | 标的证券近 5 日区间累计涨跌幅(%) | — | `conflict` |

### `margin_trading.rqjmg` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `margin_trading.rqjmg` | margin_trading.rqjmg | 融券净卖出量（股） | — | `conflict` |

### `margin_trading.rzche_10d` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `margin_trading.rzche_10d` | margin_trading.rzche_10d | 融资偿还额近 10 日累计（元） | — | `conflict` |

### `margin_trading.rzche_5d` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `margin_trading.rzche_5d` | margin_trading.rzche_5d | 融资偿还额近 5 日累计（元） | — | `conflict` |

### `margin_trading.rzjme` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `margin_trading.rzjme` | margin_trading.rzjme | 融资净买入额（元） | — | `conflict` |

### `margin_trading.rzmre_10d` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `margin_trading.rzmre_10d` | margin_trading.rzmre_10d | 融资买入额近 10 日累计（元） | — | `conflict` |

### `margin_trading.rzmre_5d` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `margin_trading.rzmre_5d` | margin_trading.rzmre_5d | 融资买入额近 5 日累计（元） | — | `conflict` |

### `market` — ambiguous

聚合问题：canonical_differs；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `market` | market | 市场代码 | 0=深/1=沪/2=京 | `verified` |
| ZHB-tdxstat · `market` | market | 市场 | - | `verified` |
| ZHB-tdxstat2 · `market` | market | 市场 | - | `verified` |
| reports · `market` | market | 交易所 | — | `verified` |
| 东财-热榜(em_hot) · `market` | market | 市场 | — | `verified` |
| 同花顺-fuyao · `market` | dump/market-dumps/{daily-k,daily-k-10d,adjustment-factors}/download-url | — | — | `unverified` |
| 市场源(market_sources) · `market` | market | 市场 | — | `verified` |

### `market_cap` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `market_cap` | market_cap | 总市值 | 元 | `verified` |
| 东财-datacenter(英文键) · `market_cap` | — | — | — | `unverified` |
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
| TDX(双命名源) · `name` | — | — | — | `unverified` |
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

### `northbound_hold.change_ratio` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `northbound_hold.change_ratio` | northbound_hold.change_ratio | 较上一期持股比例增减变动幅度(%) | — | `conflict` |

### `northbound_hold.change_shares` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `northbound_hold.change_shares` | northbound_hold.change_shares | 较上一期持股增减变动数(股) | — | `conflict` |

### `northbound_hold.hold_ratio` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `northbound_hold.hold_ratio` | northbound_hold.hold_ratio | 北向持股占流通股本比例(%) | — | `conflict` |

### `northbound_hold.hold_shares` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `northbound_hold.hold_shares` | northbound_hold.hold_shares | 北向持股总数(股) | — | `conflict` |

### `northbound_hold.market_cap` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `northbound_hold.market_cap` | northbound_hold.market_cap | 北向持股市值(元) | — | `conflict` |

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

### `pb` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `pb` | — | — | — | `unverified` |
| 开盘啦(kpl) · `pb` | pb | 市净率 | 倍 | `unverified` |

### `pct` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-热榜(em_hot) · `pct` | pct | 涨跌幅 | % | `verified` |
| 财联社(cls) · `pct` | — | — | — | `unverified` |

### `pe_dynamic` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 开盘啦(kpl) · `pe_dynamic` | pe_dynamic | 动态PE（最新报告期年化） | 倍 | `conflict` |

### `pe_lyr` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `pe_lyr` | — | — | — | `unverified` |
| ZHB-tdxstat · `pe_lyr` | pe_lyr | 静态市盈率（LYR/上一完整年度业绩口径）；180 组、9 个来源日期与已验证静态 PE 参照相符，最大差 0.006 倍；精度差异不证明跨源逐值相同。 | 倍 | `verified` |

### `pe_static` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `pe_static` | — | — | — | `unverified` |
| 开盘啦(kpl) · `pe_static` | pe_static | 静态PE（上年度年报 LYR） | 倍 | `conflict` |

### `pe_ttm` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `pe_ttm` | pe_ttm | 滚动市盈率（TTM） | — | `verified` |
| TDX(双命名源) · `pe_ttm` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `pe_ttm` | pe_ttm | 滚动市盈率 | 倍 | `verified` |
| ZHB-tdxstat · `pe_ttm` | pe_ttm | 市盈率（TTM） | 倍 | `verified` |
| 同花顺-fuyao · `pe_ttm` | valuation.pe_ttm | 旧无分组根路径身份；当前完整采集路径为 valuation.pe_ttm。接口响应把该叶字段放在 data.item[]，项目采集输出则将 item 保存在 stocks.<代码>.valuation。本记录只退役裸叶来源路径。 | 倍 | `disproved` |
| 开盘啦(kpl) · `pe_ttm` | pe_ttm | PE(TTM) | 倍 | `conflict` |

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

### `pre_close` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `pre_close` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `pre_close` | pre_close | — | — | `unverified` |

### `pre_close_price` — ambiguous

聚合问题：meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `pre_close_price` | pre_close_price | 昨收价 | — | `verified` |
| 同花顺-fuyao · `pre_close_price` | pre_close_price | 集合竞价快照中的前收盘价。 | — | `verified` |

### `predictNextTwoYearPe` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `predictNextTwoYearPe` | — | — | — | `conflict` |

### `predictNextYearPe` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `predictNextYearPe` | — | — | — | `conflict` |

### `predictThisYearPe` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `predictThisYearPe` | — | — | — | `conflict` |

### `prev_close` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `prev_close` | prev_close | 前收盘价 | 元/股 | `verified` |
| 新浪(扩展API) · `prev_close` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | — | `unverified` |

### `price` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `price` | price | 现价 | 元 | `verified` |
| TDX-eltdx(适配层) · `price` | price | 实时行情快照最新价；收盘阶段与该数据日收盘价一致。 | 元 | `verified` |
| 东财-datacenter(英文键) · `price` | — | — | — | `unverified` |
| 东财-push2ex · `price` | price | 现价；接口原始数值以 0.001 元为单位，除以 1,000 后与同数据日 KPL col_21 的三个有效日期 271 组对照逐值相等。 | 0.001元 | `verified` |
| 东财-热榜(em_hot) · `price` | price | 现价 | 元 | `verified` |
| 市场源(market_sources) · `price` | price | 现价 | — | `verified` |
| 开盘啦(kpl) · `price` | price | 现价 | 元 | `unverified` |

### `profitability` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `profitability` | profitability | — | — | `conflict` |

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

聚合问题：canonical_differs；meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `reading_num` | reading_num / share_num | 阅读数/分享数 | — | `unverified` |
| 财联社(cls) · `reading_num` | reading_num | 阅读数 | — | `unverified` |

### `reason` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-热榜(em_hot) · `reason` | reason | 题材归因 | — | `verified` |
| 市场源(market_sources) · `reason` | — | — | — | `unverified` |
| 开盘红 · `reason` | limit_up_reason | 涨停原因；与 KPL reason 367/370 逐字一致，3 组文本差异保留来源原值 | — | `verified` |
| 开盘红(Levistock适配) · `reason` | reason | 涨停原因 | — | `unverified` |

### `report_type` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 新浪(扩展API) · `report_type` | report_type | fzb(资产负债)/lrb(利润)/llb(现金流) | — | `conflict` |

### `rise_speed` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `rise_speed` | — | — | — | `unverified` |
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

### `shares` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `shares` | shares | 总股本 | 股 | `verified` |
| 东财-datacenter(英文键) · `shares` | — | — | — | `unverified` |

### `solvency` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `solvency` | solvency | — | — | `conflict` |

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

聚合问题：meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `stock_list` | stock_list | 待破解 | — | `unverified` |
| 财联社(cls) · `stock_list` | stock_list | 关联股票代码列表 | — | `unverified` |

### `subjects` — ambiguous

聚合问题：canonical_differs；meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `subjects` | subjects / subject_name | 主题分类 | — | `unverified` |
| 财联社(cls) · `subjects` | subjects | 主题/题材标签列表 | — | `unverified` |

### `themes` — ambiguous

聚合问题：meaning_differs；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 开盘红 · `themes` | themes | 题材标签列表；与 KPL sector 完整列表 360/370 一致、至少一项重合 369/370；保留来源标签口径差异 | — | `verified` |
| 开盘红(Levistock适配) · `themes` | themes | 题材 | — | `unverified` |

### `time` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `time` | time | 日K时间戳；按上海时区记录，本批样本时间为15:00 | ISO 8601 日期时间（Asia/Shanghai） | `verified` |
| 东财-热榜(em_hot) · `time` | time | 分钟时间点 | — | `verified` |
| 市场源(market_sources) · `time` | time | 时间 | — | `verified` |
| 开盘啦(kpl) · `time` | — | — | — | `unverified` |
| 财联社(cls) · `time` | — | — | — | `unverified` |

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
| 同花顺-fuyao · `turnover` | — | — | — | `unverified` |
| 开盘啦(kpl) · `turnover` | — | — | — | `unverified` |
| 开盘红 · `turnover` | amount | 成交额；与 KPL amount 370 组、8 个交易日逐值一致 | 元 | `verified` |
| 开盘红(Levistock适配) · `turnover` | turnover / turnover_rate | 成交额 / 换手率% | — | `unverified` |
| 新浪(扩展API) · `turnover` | turnover | 换手率原始值（万分比；换算为百分数时原值除以100） | 万分比 | `verified` |

### `turnover_pct` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `turnover_pct` | — | — | — | `unverified` |
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

### `vol_ratio` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `vol_ratio` | — | — | — | `unverified` |
| 市场源(market_sources) · `vol_ratio` | — | — | — | `unverified` |
| 开盘啦(kpl) · `vol_ratio` | vol_ratio | 量比 | — | `unverified` |

### `volume` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare REST · `volume` | volume | 成交量 | 股 | `verified` |
| TDX(双命名源) · `volume` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `volume` | volume | — | — | `unverified` |
| 同花顺-fuyao · `volume` | — | — | — | `unverified` |

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
| TDX(双命名源) | `Inside` | Inside | 内盘；板块指数时表示跌停家数 | `verified` |
| TDX(双命名源) | `IsT0Fund` | IsT0Fund | 是否是 T+0 基金 | `verified` |
| TDX(双命名源) | `JZC` | JZC | 净资产/股东权益 | `verified` |
| TDX(双命名源) | `More_YJL` | More_YJL | ETF/LOF 溢价率 | `verified` |
| TDX(双命名源) | `Outside` | Outside | 外盘；板块指数时表示涨停家数 | `verified` |
| TDX(双命名源) | `ShapeValue` | ShapeValue | 短期形态+中期形态+长期形态编号 | `verified` |
| TDX(双命名源) | `Yield` | Yield | 应计利息(债券)/占款天数(回购) | `verified` |
| TDX(双命名源) | `amount_wan` | amount_wan | TDX 行情快照成交金额；由原始 amount 以元计值除以 10000 得到，输出单位为万元。 | `verified` |
| TDX(双命名源) | `b_vol` | b_vol | 外盘成交量（主动买入侧）；板块指数时表示涨停家数。 | `verified` |
| TDX(双命名源) | `baoliu2` | report_period_end_month | 财务记录对应的报告期末月份；本轮实测 6 对应 2026-06-30、9 对应 2026-09-30，其他月份和年份未验证 | `verified` |
| TDX(双命名源) | `category_name` | category_name | ELTDX CapitalChangeRecord 中 XDXR 事件类别的可读名称；与 category_raw/category 类别编号区分。具体类别码表不在本次确认范围内。 | `verified` |
| TDX(双命名源) | `change_amt` | change_amt | TDX 行情快照涨跌额，即最新价减昨收价；价格单位为元/股。 | `verified` |
| TDX(双命名源) | `circulating_shares` | circulating_shares | 流通股本；由 liu_tong_gu_ben_raw_float（万股）乘 10000 得到 | `verified` |
| TDX(双命名源) | `date` | event_date | TDX XDXR（0x000f）权息/股本变迁事件日期；不是采集日期。现有契约未进一步区分公告日、股权登记日或除权除息日。 | `verified` |
| TDX(双命名源) | `eps` | eps_raw | 每股收益原始值（上游契约及现有可区分样本未确认基本/稀释子口径、报告期选择规则或小数精度/舍入规则） | `verified` |
| TDX(双命名源) | `gudongrenshu` | gudongrenshu | 股东户数；样本对应发行人报告期末普通股股东总数，按来源计数口径记录。 | `verified` |
| TDX(双命名源) | `ipodate` | ipodate | ipo_date 的无下划线兼容别名，表示证券上市日期；不是报告或采集日期。 | `verified` |
| TDX(双命名源) | `jingzichan` | — | 净资产 / 股东权益 | `verified` |
| TDX(双命名源) | `net_profit` | finance_info.jinglirun | 旧统一层别名，不是独立 TDX 原始路径；当前原始路径为 finance_info.jinglirun | `disproved` |
| TDX(双命名源) | `net_profit_yuan` | net_profit_yuan | 净利润金额；由 jing_li_run_raw_float（千元）乘 1000 得到 | `verified` |
| TDX(双命名源) | `s_vol` | s_vol | 内盘成交量（主动卖出侧）；板块指数时表示跌停家数。 | `verified` |
| TDX(双命名源) | `total_assets_yuan` | total_assets_yuan | 总资产金额；由 zong_zi_chan_raw_float（千元）乘 1000 得到 | `verified` |
| TDX(双命名源) | `total_shares` | total_shares | 总股本；由 zong_gu_ben_raw_float（万股）乘 10000 得到 | `verified` |
| TDX(双命名源) | `updateddate` | updateddate | updated_date 的无下划线兼容别名，表示该证券财务记录的更新日期；不等同报告期末、公告披露日、采集日或来源级数据日期。 | `verified` |
| TDX(双命名源) | `vzangsu` | vzangsu | 量涨速（官方未说明单位、计算窗口和算法） | `verified` |
| TDX(双命名源) | `zhuyinglyrun` | zhuyinglyrun | 财务输出值对应发行人合并利润表“营业成本”；当前官方报告核验样本为 2026 年第三季度年初至报告期末值。 | `verified` |
| TDX(双命名源) | `zhuyingshouru` | zhuyingshouru | 主营收入槽位；样本对应合并利润表“营业收入”行，不对应“营业总收入”合计。 | `verified` |
| TDX(双命名源) | `zongxianjinliu` | zongxianjinliu | 经营、投资、筹资活动产生的现金流量净额之和；不含汇率变动对现金及现金等价物的影响。 | `verified` |
| TDX-eltdx(适配层) | `amount` | amount | 实时行情快照截至该时点的累计成交额；收盘样本与同一数据日 K 线成交额一致。 | `verified` |
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
| TDX-eltdx(适配层) | `ipo_date_raw` | ipo_date_raw | 上市日期原始整数；YYYYMMDD 编码，不是采集来源数据日 | `verified` |
| TDX-eltdx(适配层) | `jing_li_run_raw_float` | jing_li_run_raw_float | 归属于上市公司股东的净利润原始值；样本对应报告期累计值 | `verified` |
| TDX-eltdx(适配层) | `last_close_price_milli` | last_close_price_milli | 前一根K线收盘价的千分之一元值；返回序列首条无前收盘字段 | `verified` |
| TDX-eltdx(适配层) | `last_price` | last_price | 最新价 / 现价 | `verified` |
| TDX-eltdx(适配层) | `leader_code` | leader_code | Helper 在目标交易日选出的该题材最高连板成分股完整证券代码；同高度时遵循连板天梯的封单金额降序、完整代码升序顺序。 | `verified` |
| TDX-eltdx(适配层) | `li_run_zong_he_raw_float` | li_run_zong_he_raw_float | 利润总额原始值；样本对应报告期累计值 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.float_market_value` | limit_ladder.float_market_value | 普通流通市值；普通流通股本乘当前行情价 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.float_shares` | limit_ladder.float_shares | 普通流通股本；财务快照口径 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.free_float_market_value` | limit_ladder.free_float_market_value | 自由流通市值；自由流通股本乘当前行情价 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.free_float_shares` | limit_ladder.free_float_shares | 自由流通股本；TDX 自由流通口径 | `verified` |
| TDX-eltdx(适配层) | `limit_ladder.seal_amount` | limit_ladder.seal_amount | 当前买一金额；封板时解释为封单额 | `verified` |
| TDX-eltdx(适配层) | `limit_up_count` | limit_up_count | Helper 返回的目标交易日内，本次请求股票池中已封涨停且关联该题材的股票数；不含仅触板股票，也不是全市场计数。 | `verified` |
| TDX-eltdx(适配层) | `locked_amount` | locked_amount | 买一档挂单金额；按 bid1 × bid_vol1 × 100 计算，不等同涨停总封单金额 | `verified` |
| TDX-eltdx(适配层) | `open_delta_raw` | open_delta_raw | 日K开盘价相对前一根收盘价的协议差分值；返回序列首条无前收盘基准时以开盘价为基值 | `verified` |
| TDX-eltdx(适配层) | `opening_rush` | opening_rush | 开盘抢筹指标；算法及正负方向口径未公开 | `verified` |
| TDX-eltdx(适配层) | `order_count` | order_count | 成交明细中的原始笔数字段；集合竞价快照不赋予其未匹配量含义 | `verified` |
| TDX-eltdx(适配层) | `price` | price | 实时行情快照最新价；收盘阶段与该数据日收盘价一致。 | `verified` |
| TDX-eltdx(适配层) | `seal_amount` | seal_amount | 当前买一档挂单金额；不代表涨停总封单金额 | `verified` |
| TDX-eltdx(适配层) | `shortline.auction_prev_volume_ratio` | shortline.auction_prev_volume_ratio | 竞价量/昨量比 | `verified` |
| TDX-eltdx(适配层) | `shortline.open_prev_amount_ratio` | shortline.open_prev_amount_ratio | 开盘额/昨额比 | `verified` |
| TDX-eltdx(适配层) | `shortline.open_prev_seal_ratio` | shortline.open_prev_seal_ratio | 开盘额/昨封单额比 | `verified` |
| TDX-eltdx(适配层) | `shortline.seal_prev_ratio` | shortline.seal_prev_ratio | 封单/前封单比 | `verified` |
| TDX-eltdx(适配层) | `shortline.seal_to_amount_ratio` | shortline.seal_to_amount_ratio | 封单/成交额比 | `verified` |
| TDX-eltdx(适配层) | `shortline.seal_to_float_ratio` | shortline.seal_to_float_ratio | 封单/流通市值比 | `verified` |
| TDX-eltdx(适配层) | `shui_hou_li_run_raw_float` | shui_hou_li_run_raw_float | 税后利润原始值；保留样本对应合并利润表的净利润行 | `verified` |
| TDX-eltdx(适配层) | `side` | side | 成交方向或状态标签：buy、sell、neutral 或状态名；完整数值状态码映射未确认 | `verified` |
| TDX-eltdx(适配层) | `status_raw` | status_raw | 成交明细方向或状态的原始值；具体状态码映射未在本裁决中扩展 | `verified` |
| TDX-eltdx(适配层) | `time` | time | 日K时间戳；按上海时区记录，本批样本时间为15:00 | `verified` |
| TDX-eltdx(适配层) | `topic_id` | topic_id | 题材 ID；由参与聚合股票的 F10 题材关系提供，可为空；ID 缺失时 Helper 回退到题材名称作为分组键。 | `verified` |
| TDX-eltdx(适配层) | `topic_name` | topic_name | 题材名称；取自参与聚合股票的 F10 题材关系，作为聚合组的可读名称。 | `verified` |
| TDX-eltdx(适配层) | `total_seal_amount` | total_seal_amount | Helper 返回的目标交易日内，本次请求股票池中该题材封板成分股当前买一金额之和；单股金额缺失按 0，聚合值保留 6 位小数。共享题材股票会计入各自题材。 | `verified` |
| TDX-eltdx(适配层) | `tou_zi_shou_yu_raw_float` | tou_zi_shou_yu_raw_float | 投资收益；样本值对应报告期累计金额 | `verified` |
| TDX-eltdx(适配层) | `trade_date` | trade_date | 连板天梯及题材强度结果对应的目标交易日；由 ShortlineIndicatorTable.target_trade_date 派生，题材强度 Helper 继承该日期 | `verified` |
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
| ZHB-tipinfo | `[13]` | [13] | 解禁日 = 官方 RecentReleaseDate（二进制 `解禁数量:%.2f万` 实证；旧标"股权登记日/配股"为误译——Col[14] 量级=解禁股数万股, 与 Col[11]/[12] 配股重复赋值矛盾已解） | `verified` |
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
| reports | `reading_num` | reading_num / share_num | 阅读数/分享数 | `unverified` |
| reports | `sRatingCode` | sRatingCode | 机构原始评级类别代码；须结合机构和同记录 sRatingName 解释，未确立跨机构代码表。 | `verified` |
| reports | `secName` | secName / orgId | 证券名 / 机构ID | `unverified` |
| reports | `share_num` | reading_num / share_num | 阅读数/分享数 | `unverified` |
| reports | `subject_name` | subjects / subject_name | 主题分类 | `unverified` |
| reports | `subjects` | subjects / subject_name | 主题分类 | `unverified` |
| 东财-clist | `f104` | f104 / f105 | 上涨 / 下跌家数 | `verified` |
| 东财-clist | `f105` | f104 / f105 | 上涨 / 下跌家数 | `verified` |
| 东财-clist | `f109` | f109 / f160 | 涨跌幅 | `verified` |
| 东财-clist | `f160` | f109 / f160 | 涨跌幅 | `verified` |
| 东财-clist | `f164` | f164 / f165 | 主力净额 | `verified` |
| 东财-clist | `f165` | f164 / f165 | 主力净额 | `verified` |
| 东财-clist | `f174` | f174 / f175 | 主力净额 | `verified` |
| 东财-clist | `f175` | f174 / f175 | 主力净额 | `verified` |
| 东财-clist | `f66` | f66 / f72 / f78 / f84 | 超大/大/中/小单净额 | `verified` |
| 东财-clist | `f72` | f66 / f72 / f78 / f84 | 超大/大/中/小单净额 | `verified` |
| 东财-clist | `f78` | f66 / f72 / f78 / f84 | 超大/大/中/小单净额 | `verified` |
| 东财-clist | `f84` | f66 / f72 / f78 / f84 | 超大/大/中/小单净额 | `verified` |
| 东财-datacenter(英文键) | `BILLBOARD_BUY_AMT` | BILLBOARD_BUY_AMT / SELL_AMT | 买入/卖出资 | `verified` |
| 东财-datacenter(英文键) | `BUY` | BUY / SELL | 买入额 / 卖出额 | `verified` |
| 东财-datacenter(英文键) | `BUYER_NAME` | BUYER_NAME / SELLER_NAME | 买方 / 卖方营业部 | `verified` |
| 东财-datacenter(英文键) | `CHANGE_RATE` | CLOSE_PRICE / CHANGE_RATE | 收盘价 / 涨跌幅 | `verified` |
| 东财-datacenter(英文键) | `DEAL_PRICE` | DEAL_PRICE / CLOSE_PRICE | 成交价 / 收盘价 | `verified` |
| 东财-datacenter(英文键) | `RQCHL` | RQMCL / RQCHL | 融券卖出 / 偿还量 | `verified` |
| 东财-datacenter(英文键) | `RQMCL` | RQMCL / RQCHL | 融券卖出 / 偿还量 | `verified` |
| 东财-datacenter(英文键) | `RZCHE` | RZMRE / RZCHE | 融资买入 / 偿还额 | `verified` |
| 东财-datacenter(英文键) | `RZMRE` | RZMRE / RZCHE | 融资买入 / 偿还额 | `verified` |
| 东财-datacenter(英文键) | `SECURITY_CODE` | SECURITY_CODE / SECURITY_NAME_ABBR | 代码 / 名称 | `verified` |
| 东财-datacenter(英文键) | `SECURITY_NAME_ABBR` | SECURITY_CODE / SECURITY_NAME_ABBR | 代码 / 名称 | `verified` |
| 东财-datacenter(英文键) | `SELL` | BUY / SELL | 买入额 / 卖出额 | `verified` |
| 东财-datacenter(英文键) | `SELLER_NAME` | BUYER_NAME / SELLER_NAME | 买方 / 卖方营业部 | `verified` |
| 东财-datacenter(英文键) | `SELL_AMT` | BILLBOARD_BUY_AMT / SELL_AMT | 买入/卖出资 | `verified` |
| 东财-push2(stock/get) | `f103` | ocf_ttm(f103) | 经营活动现金流量净额 TTM：上年全年 + 本年最新报告期年初至今 − 上年同期年初至今；合并现金流口径。 | `verified` |
| 东财-push2(stock/get) | `f107` | f107 | 市场标记（布尔 0/1，北交=0） | `verified` |
| 东财-push2(stock/get) | `f108` | eps_ttm(f108) | 归母净利润 TTM 按当前总股本折算的每股收益；TTM 归母净利润 = 上年度全年归母净利润 + 本年度最新报告期年初至今归母净利润 - 上年度同期年初至今归母净利润，分母为 Push2 f84 当前总股本。不是扣非 EPS，也不推断法定基本/稀释 EPS 的加权平均股数口径。 | `verified` |
| 东财-push2(stock/get) | `f110` | f110 | 市场标记（布尔 0/1，北交=0） | `verified` |
| 东财-push2(stock/get) | `f118` | f118 | 市场/板块状态标记（≡ ulist:f107） | `verified` |
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
| 东财-push2(stock/get) | `f55` | f55 | 基本每股收益计算值（最新报告期归母净利润/最新总股本） | `verified` |
| 东财-push2(stock/get) | `f59` | quote_price_precision_digits | 该证券实时行情报价的显示小数位数；在 fltt=1 响应中用于将价格整数还原为 fltt=2 报价。 | `verified` |
| 东财-push2(stock/get) | `f62` | f62 | 最新已发布报告期的季度序号（如 2=中报、3=三季报；不含年份） | `verified` |
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
| 东财-ulist239(np/get) | `f1` | quote_price_precision_digits | 该证券实时行情报价的显示小数位数；在 fltt=1 响应中用于将价格整数还原为 fltt=2 报价。 | `verified` |
| 东财-ulist239(np/get) | `f114` | f114 | 市盈率(静态/年报 LYR) | `verified` |
| 东财-ulist239(np/get) | `f13` | f13 | 市场标志：本项目 A 股样本中沪市=1，非沪市=0（含深市、北交）；保留期样本与 f27 同值。 | `verified` |
| 东财-ulist239(np/get) | `f131` | f131 | 市现率 PCF_TTM（总市值 / 经营现金流 TTM） | `verified` |
| 东财-ulist239(np/get) | `f133` | dividend_yield_lfy_observed | 股息率（%）；在本次保留的善水科技、万华化学、贵州茅台样本中，数值符合最近已实施完整年度现金分红/当日价格的 LFY-like 口径。东方财富整体算法会按分红期切换 TTM/LFY 并可含预案；特别股利及切换条件未由本字段样本充分确认。 | `verified` |
| 东财-ulist239(np/get) | `f144` | f144 | 最新价/现价 | `verified` |
| 东财-ulist239(np/get) | `f231` | f231 | 有转债标志（0=无/3=有） | `verified` |
| 东财-ulist239(np/get) | `f27` | f27 | 市场标志：本项目 A 股样本中沪市=1，非沪市=0（含深市、北交）；与同源 f13 为实证别名。 | `verified` |
| 东财-ulist239(np/get) | `f46` | ulist239_parent_net_profit_yoy_growth_pct | 归属于母公司股东的净利润同比增长率（东方财富财报展示口径；亏损基期算法另行保留） | `verified` |
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
| 同花顺-fuyao | `dump` | dump/market-dumps/{daily-k,daily-k-10d,adjustment-factors}/download-url | — | `unverified` |
| 同花顺-fuyao | `earned_interest_multiple` | solvency.earned_interest_multiple | 旧登记的无分组叶名身份；当前完整路径为 solvency.earned_interest_multiple。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `ex_date_ms` | ex_date_ms | 除权除息日，Asia/Shanghai 00:00:00 毫秒 Unix 时间戳。 | `verified` |
| 同花顺-fuyao | `first_seal_time` | first_seal_time | 炸板股票当日首次封板时间，上海时区 HH:mm；上游缺失时为 null。 | `verified` |
| 同花顺-fuyao | `fiscal_period` | fiscal_period | `FY` / `Q1` / `Q2` / `Q3` / `Q4`。 | `verified` |
| 同花顺-fuyao | `fixed_asset_invest_expansion_ratio` | growth.fixed_asset_invest_expansion_ratio | 旧登记将 ability/index_id 叶名误作 fin_indicators 根级路径；当前响应与解析器不输出该无分组根键，实际路径为 fin_indicators.growth.fixed_asset_invest_expansion_ratio。此记录只退役旧路径身份，不否定嵌套字段语义。 | `disproved` |
| 同花顺-fuyao | `growth.calculate_operating_income_yoy_growth_ratio` | growth.calculate_operating_income_yoy_growth_ratio | 该股票所选财报期营业收入相较上年同期的同比增长率；按百分数值返回。2026H1 样本按（本期营业收入－上年同期营业收入）／abs（上年同期营业收入）×100 复算吻合。 | `verified` |
| 同花顺-fuyao | `growth.calculate_operating_profit_yoy_growth_ratio` | growth.calculate_operating_profit_yoy_growth_ratio | 该股票所选财报期营业利润相较上年同期的同比增长率；按百分数值返回。2026H1 样本按（本期营业利润－上年同期营业利润）／abs（上年同期营业利润）×100 复算吻合。 | `verified` |
| 同花顺-fuyao | `growth.calculate_parent_holder_net_profit_yoy_growth_ratio` | growth.calculate_parent_holder_net_profit_yoy_growth_ratio | 该股票所选财报期归属于母公司股东、所有者或上市公司股东的净利润相较上年同期的同比增长率；按百分数值返回。2026H1 样本按（本期归母净利润－上年同期归母净利润）／abs（上年同期归母净利润）×100 复算吻合。 | `verified` |
| 同花顺-fuyao | `growth.fixed_asset_invest_expansion_ratio` | growth.fixed_asset_invest_expansion_ratio | 固定资产账面价值同比变动率，按百分数值返回；2026H1正式报告横向实证支持合并口径固定资产账面价值变化率。具体上游计算和基期修订策略未获接口契约确认。 | `verified` |
| 同花顺-fuyao | `growth.total_assets_growth_ratio` | growth.total_assets_growth_ratio | 总资产增长率；接口值按百分数表达。2026H1样本中按本期末合并总资产相对上期末未调整合并总资产复算；中华企业报告使用调整后比较基数，差异另行保留。 | `verified` |
| 同花顺-fuyao | `high_price` | snapshot.high_price | 旧无分组根路径身份；当前完整采集路径为 snapshot.high_price。官方接口将 high_price 列在 data.item[]，项目采集输出将 item 保存在 stocks.<代码>.snapshot。本记录只退役裸叶来源路径。 | `disproved` |
| 同花顺-fuyao | `index_deduct_weighted_avg_roe` | profitability.index_deduct_weighted_avg_roe | 旧登记的无分组叶名身份；当前完整路径为 profitability.index_deduct_weighted_avg_roe。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `index_weighted_avg_roe` | profitability.index_weighted_avg_roe | 旧无分组根路径身份；当前完整字段路径为 profitability.index_weighted_avg_roe，裸叶不是当前解析响应的根级独立字段。 | `disproved` |
| 同花顺-fuyao | `indicators` | a-share/financials/indicators | — | `unverified` |
| 同花顺-fuyao | `inventory_turnover_ratio` | operation.inventory_turnover_ratio | 旧登记的无分组叶名身份；当前完整路径为 operation.inventory_turnover_ratio。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `keyword_list` | keyword_list | 关键词列表；无关键词时返回空数组。 | `verified` |
| 同花顺-fuyao | `last_price` | snapshot.last_price | 旧无分组根路径身份；当前完整采集路径为 snapshot.last_price。官方接口将 last_price 列在 data.item[]，项目采集输出将 item 保存在 stocks.<代码>.snapshot。本记录只退役裸叶来源路径。 | `disproved` |
| 同花顺-fuyao | `last_seal_time` | last_seal_time | 炸板股票当日最后一次封板时间，上海时区 HH:mm；上游缺失时为 null。 | `verified` |
| 同花顺-fuyao | `limit_up_reason` | limit_up_reason | 涨停原因；上游空字符串会标准化为 `null`。 | `verified` |
| 同花顺-fuyao | `list` | meta/tickers/list | — | `unverified` |
| 同花顺-fuyao | `long_term_debt_equity_ratio` | operation.long_term_debt_equity_ratio | 旧登记的无分组叶名身份；当前完整路径为 operation.long_term_debt_equity_ratio。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `low_price` | snapshot.low_price | 旧无分组根路径身份；当前完整采集路径为 snapshot.low_price。官方接口将 low_price 列在 data.item[]，项目采集输出将 item 保存在 stocks.<代码>.snapshot。本记录只退役裸叶来源路径。 | `disproved` |
| 同花顺-fuyao | `market` | dump/market-dumps/{daily-k,daily-k-10d,adjustment-factors}/download-url | — | `unverified` |
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
| 同花顺-fuyao | `pe_mrq` | valuation.pe_mrq | 旧无分组根路径身份；当前完整采集路径为 valuation.pe_mrq。接口响应把该叶字段放在 data.item[]，项目采集输出则将 item 保存在 stocks.<代码>.valuation。本记录只退役裸叶来源路径。 | `disproved` |
| 同花顺-fuyao | `pe_ttm` | valuation.pe_ttm | 旧无分组根路径身份；当前完整采集路径为 valuation.pe_ttm。接口响应把该叶字段放在 data.item[]，项目采集输出则将 item 保存在 stocks.<代码>.valuation。本记录只退役裸叶来源路径。 | `disproved` |
| 同花顺-fuyao | `period_end_ms` | period_end_ms | 报告期末（Asia/Shanghai 零点毫秒戳）。 | `verified` |
| 同花顺-fuyao | `prev_price` | snapshot.prev_price | 旧无分组根路径身份；当前完整采集路径为 snapshot.prev_price。官方接口将 prev_price 列在 data.item[]，项目采集输出将 item 保存在 stocks.<代码>.snapshot。本记录只退役裸叶来源路径。 | `disproved` |
| 同花顺-fuyao | `profitability.index_deduct_weighted_avg_roe` | profitability.index_deduct_weighted_avg_roe | 扣非加权净资产收益率；接口值按百分数表达。 | `verified` |
| 同花顺-fuyao | `profitability.index_weighted_avg_roe` | profitability.index_weighted_avg_roe | 加权平均净资产收益率；接口值按百分数表达。年化与非年化比较按发行人报告明确披露的口径归一。 | `verified` |
| 同花顺-fuyao | `profitability.sale_gross_margin` | profitability.sale_gross_margin | 销售毛利率；可比样本按（合并营业收入－合并营业成本）/合并营业收入×100%复算。 | `verified` |
| 同花顺-fuyao | `profitability.sale_net_interest_ratio` | profitability.sale_net_interest_ratio | 销售净利率；可比样本按合并净利润/合并营业收入×100%复算。 | `verified` |
| 同花顺-fuyao | `profitability.total_assets_net_ratio` | profitability.total_assets_net_ratio | 总资产收益率；接口值按百分数表达。2026H1样本中按当期合并净利润除以本期末与上期末未调整合并总资产的均值复算；该样本关系不外推为所有期间的通用算法。 | `verified` |
| 同花顺-fuyao | `quick_ratio` | solvency.quick_ratio | 旧登记的无分组叶名身份；当前完整路径为 solvency.quick_ratio。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `rank_change` | rank_change | 排名变化，正数表示上升，负数表示下降；上游缺失时为 `null`。 | `verified` |
| 同花顺-fuyao | `rank_trend` | rank_trend | 排名趋势：`up` / `down` / `flat` / `unknown`。 | `verified` |
| 同花顺-fuyao | `receive_account_turnover_ratio` | operation.receive_account_turnover_ratio | 旧登记的无分组叶名身份；当前完整路径为 operation.receive_account_turnover_ratio。此记录只退役 fin_indicators.<leaf> 根路径，不否定分组路径。 | `disproved` |
| 同花顺-fuyao | `report_date_ms` | report_date_ms | 财务报表披露日，即该报表公开披露的日期；不是报告期末 | `verified` |
| 同花顺-fuyao | `revenue_ttm` | — | 营业总收入 TTM（push2 f104）；富耀 operating_income 回算口径约差 1.8%，仅近似兜底 | `unverified` |
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
| 同花顺-fuyao | `valuation.pcf_ttm` | valuation.pcf_ttm | 市现率 PCF_TTM（总市值 / 经营现金流 TTM） | `verified` |
| 同花顺-fuyao | `valuations` | a-share/valuations/snapshot | — | `unverified` |
| 巨潮(cninfo) | `answer` | answer | 上市公司对该问题的回复正文；尚无回复时为空 | `verified` |
| 巨潮(cninfo) | `answerer` | answerer | 回复记录标注的答复主体/作者；尚无回复时为空，不据此推断自然人身份 | `verified` |
| 巨潮(cninfo) | `ask_time` | ask_time | 互动易问答记录的发布时间戳；由 pubDate Unix 毫秒转换为本机本地时区的分钟字符串 | `verified` |
| 市场源(market_sources) | `dt` | zt / dt | 涨停 / 跌停总数 | `unverified` |
| 市场源(market_sources) | `fall_dist` | rise_dist / fall_dist | 待破解 | `unverified` |
| 市场源(market_sources) | `fall_num` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | `unverified` |
| 市场源(market_sources) | `flat` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | `unverified` |
| 市场源(market_sources) | `q_zrcs` | s_zrcs / q_zrcs | 昨日沪市 / 昨日全市成交额 | `unverified` |
| 市场源(market_sources) | `qscln` | szln / qscln | 待破解 | `unverified` |
| 市场源(market_sources) | `rise_dist` | rise_dist / fall_dist | 待破解 | `unverified` |
| 市场源(market_sources) | `rise_num` | rise_num / fall_num / flat | 上涨 / 下跌 / 平盘家数 | `unverified` |
| 市场源(market_sources) | `s_zrcs` | s_zrcs / q_zrcs | 昨日沪市 / 昨日全市成交额 | `unverified` |
| 市场源(market_sources) | `sjdt` | sjzt / sjdt | 待破解 | `unverified` |
| 市场源(market_sources) | `sjzt` | sjzt / sjdt | 待破解 | `unverified` |
| 市场源(market_sources) | `stdt` | stzt / stdt | ST 涨停 / 跌停 | `unverified` |
| 市场源(market_sources) | `stzt` | stzt / stdt | ST 涨停 / 跌停 | `unverified` |
| 市场源(market_sources) | `szln` | szln / qscln | 待破解 | `unverified` |
| 市场源(market_sources) | `up_ratio` | up_ratio / up_ratio_num | 封板率 / 封板数量 | `unverified` |
| 市场源(market_sources) | `up_ratio_num` | up_ratio / up_ratio_num | 封板率 / 封板数量 | `unverified` |
| 市场源(market_sources) | `zt` | zt / dt | 涨停 / 跌停总数 | `unverified` |
| 开盘啦(kpl) | `Theme` | Theme/InfoBKR | — | `unverified` |
| 开盘啦(kpl_limit_up_detail) | `amount` | amount | 成交额；与 KPH turnover 两日逐值一致 | `verified` |
| 开盘啦(kpl_limit_up_detail) | `main_inflow` | main_inflow | 主力净流入；与 KPH net_inflow 两日逐值一致 | `verified` |
| 开盘啦(kpl_limit_up_detail) | `max_seal` | max_seal | 最大封单金额；与 KPH seal_money 三个交易日逐股逐值一致 | `verified` |
| 开盘啦(kpl_limit_up_detail) | `raw_columns.col_15` | limit_up_streak_count | 当前连续涨停板数（当前连板数）；不是 N 天 M 板标签中的窗口涨停次数 M | `verified` |
| 开盘啦(kpl_limit_up_detail) | `raw_columns.col_19` | sector_code | 行业/板块分类代码（具体分类体系与层级未确认；不与 KPH industry_id 保证逐值等同） | `verified` |
| 开盘啦(kpl_limit_up_detail) | `raw_columns.col_21` | price | 现价（元；数据日收盘后采集时对应当日收盘价） | `verified` |
| 开盘啦(kpl_limit_up_detail) | `seal_amount` | seal_amount | 封单量；与 KPH seal_amount 三个交易日逐股逐值一致，计量单位未确认 | `verified` |
| 开盘啦(kpl_limit_up_detail) | `turnover_real` | turnover_real | 实际换手率；与 KPH turnover_rate 两日逐值一致 | `verified` |
| 开盘啦(kpl_limit_up_detail) | `zt_time` | limit_time | 涨停时间；与 KPH limit_time 两日逐值一致 | `verified` |
| 开盘红 | `industry_id` | industry_id | 行业分类 ID；与 KPL sector_code 在来源日期对齐的 420 组对照中 417 组相同、3 组不同；分类体系或层级未确认，保留各来源原码 | `verified` |
| 开盘红 | `industry_limit_up_count` | — | 同行业涨停数；与 KPL 原始 row[20] 有 320/370 组相同，日期及个股差异含 +15、-27，计数范围未确认 | `unverified` |
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
| 开盘红(Levistock适配) | `industry_id` | industry_id / industry_zt | 行业 ID / 同行业涨停数 | `unverified` |
| 开盘红(Levistock适配) | `industry_zt` | industry_id / industry_zt | 行业 ID / 同行业涨停数 | `unverified` |
| 开盘红(Levistock适配) | `limit_count` | limit_tag / limit_count | 待破解 | `unverified` |
| 开盘红(Levistock适配) | `limit_tag` | limit_tag / limit_count | 待破解 | `unverified` |
| 开盘红(Levistock适配) | `limit_time` | limit_time / open_time | 待破解 | `unverified` |
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
| 新浪(hq.sinajs) | `[22]` | [22]-[29] | 卖二~卖五 量/价 | `verified` |
| 新浪(扩展API) | `ask` | bid_vol/bid/last/ask/ask_vol | 五档价量 | `unverified` |
| 新浪(扩展API) | `ask_vol` | bid_vol/bid/last/ask/ask_vol | 五档价量 | `unverified` |
| 新浪(扩展API) | `bid` | bid_vol/bid/last/ask/ask_vol | 五档价量 | `unverified` |
| 新浪(扩展API) | `bid_vol` | bid_vol/bid/last/ask/ask_vol | 五档价量 | `unverified` |
| 新浪(扩展API) | `delta` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | `unverified` |
| 新浪(扩展API) | `gamma` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | `unverified` |
| 新浪(扩展API) | `iv` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | `unverified` |
| 新浪(扩展API) | `last` | bid_vol/bid/last/ask/ask_vol | 五档价量 | `unverified` |
| 新浪(扩展API) | `limit_down` | limit_up / limit_down | 涨跌停价 | `unverified` |
| 新浪(扩展API) | `limit_up` | limit_up / limit_down | 涨跌停价 | `unverified` |
| 新浪(扩展API) | `netamount` | netamount | 个股资金流记录中的净流入金额原始值（元；新浪帮助页展示单位为万元） | `verified` |
| 新浪(扩展API) | `open` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | `unverified` |
| 新浪(扩展API) | `prev_close` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | `unverified` |
| 新浪(扩展API) | `report_type` | report_type | fzb(资产负债)/lrb(利润)/llb(现金流) | `conflict` |
| 新浪(扩展API) | `strike` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | `unverified` |
| 新浪(扩展API) | `theta` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | `unverified` |
| 新浪(扩展API) | `trade` | trade | 个股资金流记录中 opendate 对应行的行情价格快照（元/股）；不能默认视为官方收盘价 | `verified` |
| 新浪(扩展API) | `turnover` | turnover | 换手率原始值（万分比；换算为百分数时原值除以100） | `verified` |
| 新浪(扩展API) | `vega` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | `unverified` |
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
| 腾讯(qt.gtimg) | `[87]` | — | 科创板/两融标记（688 段值='100'） | `unverified` |
| 腾讯(qt.gtimg) | `[9]` | [9]-[18] | 买一~买五 价/量 | `verified` |
| 财联社(cls) | `brief` | title / brief | 标题 / 摘要 | `verified` |
| 财联社(cls) | `cur_heat` | rank / cur_heat | 当前热度排名 / 热度值 | `unverified` |
| 财联社(cls) | `plate_code` | plate_code / plate_name | 板块代码 / 名称（风口板块） | `unverified` |
| 财联社(cls) | `plate_name` | plate_code / plate_name | 板块代码 / 名称（风口板块） | `unverified` |
| 财联社(cls) | `plates` | trade_date / plates | 轮动日期 / 当日 top10 板块列表 | `unverified` |
| 财联社(cls) | `rank` | rank / cur_heat | 当前热度排名 / 热度值 | `unverified` |
| 财联社(cls) | `subjects` | subjects | 主题/题材标签列表 | `unverified` |
| 财联社(cls) | `title` | title / brief | 标题 / 摘要 | `verified` |
| 财联社(cls) | `trade_date` | trade_date / plates | 轮动日期 / 当日 top10 板块列表 | `unverified` |
