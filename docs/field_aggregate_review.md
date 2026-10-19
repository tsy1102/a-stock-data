# 字段聚合歧义与待拆分复核

> 本文由 `field_registry.json.source_fields` 生成。逐源完整路径记录是权威定义；本文只揭示按短 code 聚合时无法安全呈现的差异。
> `aggregation_status` 只描述兼容聚合视图，不会改写逐源 `status`。疑似合并文本由分隔符启发式识别，仅供人工检查，不自动拆字段或定案。
> 本文统计的定义缺口仅限列出的复核组；单来源或全空的定义缺口仍见 [元数据缺口](field_metadata_gaps.md) 与 [未知字段队列](unknown_fields.md)。

> 聚合歧义 89 个 code；聚合定义不完整 255 个 code；疑似合并文本 246 条逐源记录。

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

聚合问题：canonical_incomplete；meaning_differs；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[0]` | [0] | 市场代码 | — | `verified` |
| ZHB-tdxstat2 · `[0]` | [0] | 市场代码 | 0`=深, `1`=沪, `2`=京 | `verified` |
| ZHB-tipinfo · `[0]` | [0] | 市场代码 | — | `unverified` |
| 新浪(hq.sinajs) · `[0]` | [0] | 股票名称 | - | `verified` |
| 腾讯(qt.gtimg) · `[0]` | — | 市场标识（交易所） | - | `verified` |

### `[10]` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[10]` | [10] | 股息率 (%) = 官方 DYRatio | — | `verified` |
| ZHB-tdxstat2 · `[10]` | [10] | 待破解 | 手 | `unverified` |
| ZHB-tipinfo · `[10]` | [10] | 官方 DTDate_Recent | — | `verified` |
| 新浪(hq.sinajs) · `[10]` | [10] | 买一量 | 股 | `verified` |
| 腾讯(qt.gtimg) · `[10]` | — | — | — | `unverified` |

### `[11]` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[11]` | [11] | 自由流通股本 FreeLtgb（万股） | — | `verified` |
| ZHB-tdxstat2 · `[11]` | [11] | 本月至今累积涨跌幅 %（Month-to-Date，基准=上月末最后交易日收盘价） | float | `verified` |
| ZHB-tipinfo · `[11]` | [11] | 最新业绩预告发布日 | — | `verified` |
| 新浪(hq.sinajs) · `[11]` | [11] | 待破解 | 元 | `unverified` |
| 腾讯(qt.gtimg) · `[11]` | — | — | — | `unverified` |

### `[12]` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[12]` | [12] | 新股开板日 (YYYYMMDD) | — | `verified` |
| ZHB-tdxstat2 · `[12]` | [12] | 近250根K线涨跌幅(年线) | float | `verified` |
| ZHB-tipinfo · `[12]` | [12] | 业绩预告类型代码 | — | `verified` |
| 新浪(hq.sinajs) · `[12]` | [12]-[19] | 买二~买五 量/价 | 股/元 | `verified` |
| 腾讯(qt.gtimg) · `[12]` | — | — | — | `unverified` |

### `[13]` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[13]` | [13] | 上市连板数（交易日） | — | `verified` |
| ZHB-tdxstat2 · `[13]` | [13] | 通达信板块归属(881=行业板块稳定 / 880=概念·风格板块动态) | 6位字符串 | `verified` |
| ZHB-tipinfo · `[13]` | [13] | 解禁日 = 官方 RecentReleaseDate（二进制 `解禁数量:%.2f万` 实证；旧标"股权登记日/配股"为误译——Col[14] 量级=解禁股数万股, 与 Col[11]/[12] 配股重复赋值矛盾已解） | — | `verified` |
| 新浪(hq.sinajs) · `[13]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[13]` | — | — | — | `unverified` |

### `[14]` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[14]` | [14] | 扣非净利润 (万元) = 官方 KfEarnMoney | — | `verified` |
| ZHB-tdxstat2 · `[14]` | [14] | 待破解 | 万元 | `unverified` |
| ZHB-tipinfo · `[14]` | [14] | 解禁数量(万股) = 官方 ReleaseShares（二进制 `解禁数量:%.2f万` 实证） | — | `verified` |
| 新浪(hq.sinajs) · `[14]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[14]` | — | — | — | `unverified` |

### `[15]` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[15]` | [15] | 员工总人数 (人) = 官方 StaffNum | — | `verified` |
| ZHB-tdxstat2 · `[15]` | [15] | 待破解 | 万元 | `unverified` |
| ZHB-tipinfo · `[15]` | [15] | (老)增发事件日期 | — | `verified` |
| 新浪(hq.sinajs) · `[15]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[15]` | — | — | — | `unverified` |

### `[16]` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[16]` | [16] | 研发投入 RDInputFee（万元） | — | `verified` |
| ZHB-tdxstat2 · `[16]` | [16] | IPO 发行价 = 官方 IPO_Price | 元 | `verified` |
| ZHB-tipinfo · `[16]` | [16] | (老)增发募集金额(万元) | — | `verified` |
| 新浪(hq.sinajs) · `[16]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[16]` | — | — | — | `unverified` |

### `[17]` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[17]` | [17] | 近20根K线涨跌幅(含当日) | — | `verified` |
| ZHB-tdxstat2 · `[17]` | [17] | 52周最高价 = 官方 HisHigh | 元 | `verified` |
| ZHB-tipinfo · `[17]` | [17] | 待破解 | — | `unverified` |
| 新浪(hq.sinajs) · `[17]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[17]` | — | — | — | `unverified` |

### `[18]` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[18]` | [18] | 截至T-1的20根K线涨跌幅 | — | `verified` |
| ZHB-tdxstat2 · `[18]` | [18] | 52周最低价 = 官方 HisLow | 元 | `verified` |
| ZHB-tipinfo · `[18]` | [18] | 恒空占位符 | — | `unverified` |
| 新浪(hq.sinajs) · `[18]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[18]` | — | — | — | `unverified` |

### `[19]` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[19]` | [19] | ✅ 近60根K线涨跌幅 | — | `verified` |
| ZHB-tdxstat2 · `[19]` | [19] | 近30根K线涨跌幅(含噪) | float | `verified` |
| ZHB-tipinfo · `[19]` | [19] | 回购预案公告日 = 官方 RecentHGDate（"HG"=HuiGou 回购；二进制 `回购预案:上限%.2f亿元` 实证） | — | `verified` |
| 新浪(hq.sinajs) · `[19]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[19]` | [19]-[28] | 卖一~卖五 价/量 | 元/手 | `verified` |

### `[1]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[1]` | [1] | 股票代码 | — | `verified` |
| ZHB-tdxstat2 · `[1]` | [1] | 股票代码 | 6位字符串 | `verified` |
| ZHB-tipinfo · `[1]` | [1] | 股票代码 | — | `verified` |
| 新浪(hq.sinajs) · `[1]` | [1] | 开盘价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[1]` | [1] | 股票名称 | - | `verified` |

### `[20]` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[20]` | [20] | 截至T-1的60根K线涨跌幅 | — | `verified` |
| ZHB-tdxstat2 · `[20]` | [20] | 近30根K线涨跌幅(更纯) | float | `verified` |
| ZHB-tipinfo · `[20]` | [20] | 回购预案金额上限(亿元) = 官方 RecentHGAmo（二进制 `回购预案:上限%.2f亿元` 一锤定音；旧标"增发配股价"证伪） | — | `verified` |
| 新浪(hq.sinajs) · `[20]` | [20] | 卖一量 | 股 | `verified` |
| 腾讯(qt.gtimg) · `[20]` | — | — | — | `unverified` |

### `[21]` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[21]` | [21] | 年初至今涨跌幅 (YTD %) | — | `verified` |
| ZHB-tipinfo · `[21]` | [21] | 股权激励预案/草案公告日 | — | `verified` |
| 新浪(hq.sinajs) · `[21]` | [21] | 卖一价（与 [7] 竞卖价重复） | 元 | `verified` |
| 腾讯(qt.gtimg) · `[21]` | — | — | — | `unverified` |

### `[22]` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[22]` | [22] | 形态/板块代码 ShapeValue | — | `verified` |
| 新浪(hq.sinajs) · `[22]` | [22]-[29] | 卖二~卖五 量/价 | 股/元 | `verified` |
| 腾讯(qt.gtimg) · `[22]` | — | — | — | `unverified` |

### `[23]` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[23]` | [23] | 待破解 | — | `verified` |
| 新浪(hq.sinajs) · `[23]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[23]` | — | — | — | `unverified` |

### `[24]` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[24]` | [24] | 现金总额 CashZJ（万元） | — | `verified` |
| 新浪(hq.sinajs) · `[24]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[24]` | — | — | — | `unverified` |

### `[25]` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[25]` | [25] | 预收资金 PreReceiveZJ（万元） | — | `verified` |
| 新浪(hq.sinajs) · `[25]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[25]` | — | — | — | `unverified` |

### `[26]` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[26]` | [26] | 年内涨停天数 YearZTDay | — | `verified` |
| 新浪(hq.sinajs) · `[26]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[26]` | — | — | — | `unverified` |

### `[27]` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[27]` | [27] | 近 5 根K线涨跌幅 (%) | — | `verified` |
| 新浪(hq.sinajs) · `[27]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[27]` | — | — | — | `unverified` |

### `[28]` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[28]` | [28] | 近 5 日涨跌幅 (%) | — | `verified` |
| 新浪(hq.sinajs) · `[28]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[28]` | — | — | — | `unverified` |

### `[29]` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[29]` | [29] | 近 10 根K线涨跌幅 (%) | — | `verified` |
| 新浪(hq.sinajs) · `[29]` | — | — | — | `unverified` |
| 腾讯(qt.gtimg) · `[29]` | — | 最近逐笔成交 | - | `unverified` |

### `[2]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[2]` | [2] | BetaValue（Beta 系数） | — | `verified` |
| ZHB-tdxstat2 · `[2]` | [2] | 数据日期 | YYYYMMDD | `verified` |
| ZHB-tipinfo · `[2]` | [2] | 财报期 | — | `verified` |
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

聚合问题：meaning_differs；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[31]` | [31] | 连板类计数(口径待终核: 当日涨停时==[33]连板数, 非涨停日保留历史高位值>count) | — | `unverified` |
| 新浪(hq.sinajs) · `[31]` | [31] | 时间 | HH:MM:SS | `verified` |
| 腾讯(qt.gtimg) · `[31]` | [31] | 涨跌额 | 元 | `verified` |

### `[32]` — ambiguous

聚合问题：meaning_differs；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[32]` | [32] | 待破解 | — | `unverified` |
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

聚合问题：meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[34]` | [34] | 其他权益净资产 OtherQYJzc（元） | — | `verified` |
| 腾讯(qt.gtimg) · `[34]` | [34] | 最低价 | 元 | `verified` |

### `[3]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[3]` | [3] | 市盈率（TTM） | — | `verified` |
| ZHB-tdxstat2 · `[3]` | [3] | T 日总成交额 | 万元 | `verified` |
| ZHB-tipinfo · `[3]` | [3] | 每股收益 | — | `verified` |
| 新浪(hq.sinajs) · `[3]` | [3] | 现价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[3]` | [3] | 现价 | 元 | `verified` |

### `[4]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[4]` | [4] | 数据快照日期 | — | `verified` |
| ZHB-tdxstat2 · `[4]` | [4] | limit_up_down_seal: 封单额（万元，涨停为正/跌停为负） | float | `verified` |
| ZHB-tipinfo · `[4]` | [4] | 财报披露日 | — | `verified` |
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
| ZHB-tipinfo · `[5]` | [5] | 最近涨停日 = 官方 ZTDate_Recent | — | `verified` |
| 新浪(hq.sinajs) · `[5]` | [5] | 最低价 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[5]` | [5] | 开盘价 | 元 | `verified` |

### `[6]` — ambiguous

聚合问题：meaning_differs；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[6]` | [6] | T 日涨跌幅 (%) | — | `verified` |
| ZHB-tdxstat2 · `[6]` | [6] | 昨日封单额（Col[4] 滚动滞后值） | float | `verified` |
| ZHB-tipinfo · `[6]` | [6] | 阶段新高日 = 官方 TopDate_Recent（"Top"=顶部/新高, 旧标"最近除息日"为音近误读, 已证伪） | — | `verified` |
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

聚合问题：meaning_differs；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[8]` | [8] | T-2 日涨跌幅 (%) | — | `verified` |
| ZHB-tdxstat2 · `[8]` | [8] | 前日封单额（Col[4] 二次滚动滞后） | float | `verified` |
| ZHB-tipinfo · `[8]` | [8] | 业绩预告日 = 官方 ForecastDate（二进制 `业绩预告:%s` 实证；旧标"分红日"证伪——Col[9] 全市场 83.0% 负值, 分红恒非负） | — | `verified` |
| 新浪(hq.sinajs) · `[8]` | [8] | 成交量 | 股 | `verified` |
| 腾讯(qt.gtimg) · `[8]` | [8] | 内盘 | 手 | `unverified` |

### `[9]` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `[9]` | [9] | 市盈率（静态/LYR） | — | `verified` |
| ZHB-tdxstat2 · `[9]` | [9] | 待破解 | 手 | `unverified` |
| ZHB-tipinfo · `[9]` | [9] | 业绩预告金额 (万元, 可负) = 官方 ForecastAmount（Col[9] 全市场 83.0% 负值/median=-95.98, 分红恒非负 → 必为预告净利） | — | `verified` |
| 新浪(hq.sinajs) · `[9]` | [9] | 成交额 | 元 | `verified` |
| 腾讯(qt.gtimg) · `[9]` | [9]-[18] | 买一~买五 价/量 | 元/手 | `verified` |

### `amount` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `amount` | — | — | — | `unverified` |
| TDX(双命名源) · `amount` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `amount` | amount | 成交额 | — | `unverified` |
| ZHB-tdxstat2 · `amount` | amount | T日总成交额 | 万元 | `verified` |
| reports · `amount` | amount | 成交额 | — | `verified` |
| 东财-datacenter(英文键) · `amount` | — | — | — | `unverified` |
| 东财-push2ex · `amount` | amount | 成交额 | 元 | `verified` |
| 市场源(market_sources) · `amount` | amount | 成交额 | — | `verified` |
| 开盘啦(kpl) · `amount` | amount | 成交额 | 元 | `unverified` |
| 开盘啦(kpl_limit_up_detail) · `amount` | amount | 成交额；与 KPH turnover 两日逐值一致 | 元 | `verified` |

### `amplitude` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `amplitude` | — | — | — | `unverified` |
| 同花顺-fuyao · `amplitude` | — | — | — | `unverified` |
| 市场源(market_sources) · `amplitude` | — | — | — | `unverified` |
| 开盘啦(kpl) · `amplitude` | amplitude | 振幅% | % | `unverified` |

### `attachPages` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `attachPages` | — | — | — | `conflict` |

### `attachSize` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `attachSize` | — | — | — | `conflict` |

### `author` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `author` | — | — | — | `conflict` |

### `bid` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 开盘啦(kpl) · `bid` | — | — | — | `unverified` |
| 新浪(扩展API) · `bid` | bid_vol/bid/last/ask/ask_vol | 五档价量 | — | `unverified` |

### `brief` — ambiguous

聚合问题：canonical_differs；meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `brief` | brief | 摘要 | — | `verified` |
| 财联社(cls) · `brief` | title / brief | 标题 / 摘要 | — | `verified` |

### `change` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `change` | — | — | — | `unverified` |
| TDX(双命名源) · `change` | — | — | — | `unverified` |
| 同花顺-fuyao · `change` | change | 当日涨跌幅，小数形式。 | 比例（小数） | `verified` |

### `change_pct` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `change_pct` | — | — | — | `unverified` |
| TDX(双命名源) · `change_pct` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `change_pct` | change_pct | — | — | `unverified` |
| ZHB-tdxstat · `change_pct` | — | — | — | `unverified` |
| 东财-push2ex · `change_pct` | — | — | — | `unverified` |
| 市场源(market_sources) · `change_pct` | change_pct | 涨跌幅 | — | `verified` |
| 开盘啦(kpl) · `change_pct` | change_pct | 涨跌幅% | % | `unverified` |

### `change_rate` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `change_rate` | — | — | — | `unverified` |
| 东财-热榜(em_hot) · `change_rate` | latest / change_rate | 现价 / 涨跌幅 | — | `verified` |

### `change_type` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `change_type` | — | — | — | `unverified` |
| 市场源(market_sources) · `change_type` | change_type | 变动类型 | — | `unverified` |

### `circ_mv` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `circ_mv` | — | — | — | `unverified` |
| 开盘啦(kpl) · `circ_mv` | circ_mv | 流通市值 | 元 | `unverified` |

### `close` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `close` | time / open / high / low / close | 时间 / OHLC | — | `unverified` |
| 东财-datacenter(英文键) · `close` | — | — | — | `unverified` |
| 东财-热榜(em_hot) · `close` | close / zhangdie | 收盘价 / 涨跌额 | — | `verified` |
| 新浪(扩展API) · `close` | — | — | — | `unverified` |

### `close_seal_amount` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `close_seal_amount` | — | — | — | `unverified` |
| 开盘啦(kpl) · `close_seal_amount` | close_seal_amount | 收盘封单额 | 元 | `unverified` |

### `code` — ambiguous

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `code` | code | 股票代码 | 6位字符串 | `verified` |
| TDX-eltdx(适配层) · `code` | code | — | — | `unverified` |
| ZHB-tdxstat · `code` | — | — | — | `unverified` |
| ZHB-tdxstat2 · `code` | — | — | — | `unverified` |
| ZHB-tipinfo · `code` | — | — | — | `unverified` |
| 东财-push2ex · `code` | — | — | — | `unverified` |
| 东财-热榜(em_hot) · `code` | — | — | — | `verified` |
| 巨潮(cninfo) · `code` | — | — | — | `unverified` |
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
| Levistock历史未归属 · `content` | — | — | — | `unverified` |
| 开盘啦(kpl) · `content` | — | — | — | `unverified` |
| 财联社(cls) · `content` | content | 正文 | — | `verified` |

### `count` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `count` | count | 该股近 30 日滚动研报发布总篇数 | — | `verified` |
| 市场源(market_sources) · `count` | — | — | — | `unverified` |

### `date` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `date` | — | — | — | `unverified` |
| TDX(双命名源) · `date` | date / category_name | 事件日期 / 类别名称 | — | `unverified` |
| ZHB-tdxstat · `date` | — | — | — | `unverified` |
| ZHB-tdxstat2 · `date` | — | — | — | `unverified` |
| 东财-datacenter(英文键) · `date` | — | — | — | `unverified` |
| 同花顺-fuyao · `date` | — | — | — | `unverified` |
| 巨潮(cninfo) · `date` | — | — | — | `unverified` |
| 市场源(market_sources) · `date` | date | 日期 | — | `verified` |
| 开盘啦(kpl) · `date` | — | — | — | `unverified` |
| 新浪(扩展API) · `date` | — | — | — | `unverified` |

### `emRatingCode` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `emRatingCode` | — | — | — | `conflict` |

### `emRatingValue` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `emRatingValue` | — | — | — | `conflict` |

### `encodeUrl` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `encodeUrl` | encodeUrl | — | — | `conflict` |

### `eps_raw` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `eps_raw` | eps_raw | 每股收益原始值 | - | `unverified` |
| TDX-eltdx(适配层) · `eps_raw` | — | — | — | `unverified` |

### `exchange` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `exchange` | exchange | — | — | `unverified` |
| 同花顺-fuyao · `exchange` | — | — | — | `unverified` |

### `f1` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f1` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f1` | f1 | — | — | `verified` |

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

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f103` | ocf_ttm(f103) | 经营活动现金流量净额 TTM | 元 | `unverified` |
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

### `f108` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f108` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f108` | f108 | — | — | `unverified` |

### `f109` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f109` | f109 / f160 | 涨跌幅 | % | `verified` |
| 东财-push2(stock/get) · `f109` | net_profit_annual(f109) | 归母净利润 最新年报 | 元 | `unverified` |
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

聚合问题：meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f124` | f124 | — | — | `unverified` |
| 东财-ulist239(np/get) · `f124` | f124 | 股东户数? | — | `verified` |

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

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f128` | — | — | — | `unverified` |
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

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f13` | — | — | — | `unverified` |
| 东财-push2(stock/get) · `f13` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f13` | f13 | — | — | `unverified` |

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

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f133` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f133` | f133 | — | — | `unverified` |

### `f134` — incomplete

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f134` | f134 | — | — | `unverified` |
| 东财-ulist239(np/get) · `f134` | f134 | — | — | `unverified` |

### `f135` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f135` | f135 | — | 元 | `conflict` |
| 东财-ulist239(np/get) · `f135` | — | 净资产 | — | `conflict` |
| 东财-资金流(em_fund_flow) · `f135` | f135 | — | 元 | `conflict` |

### `f136` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f136` | f140 / f136 | 领涨股名称 / 领涨涨跌幅 | — | `conflict` |
| 东财-push2(stock/get) · `f136` | f136 | — | 元 | `conflict` |
| 东财-ulist239(np/get) · `f136` | — | — | — | `unverified` |
| 东财-资金流(em_fund_flow) · `f136` | f136 | — | 元 | `conflict` |

### `f137` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f137` | f137 | — | 元 | `verified` |
| 东财-ulist239(np/get) · `f137` | — | — | — | `conflict` |
| 东财-资金流(em_fund_flow) · `f137` | f137 | — | 元 | `verified` |

### `f138` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f138` | f138 | — | 元 | `conflict` |
| 东财-ulist239(np/get) · `f138` | — | — | — | `unverified` |
| 东财-资金流(em_fund_flow) · `f138` | f138 | — | 元 | `conflict` |

### `f139` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f139` | f139 | — | 元 | `conflict` |
| 东财-ulist239(np/get) · `f139` | — | — | — | `conflict` |
| 东财-资金流(em_fund_flow) · `f139` | f139 | — | 元 | `conflict` |

### `f14` — ambiguous

聚合问题：meaning_differs；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f14` | f14 | 板块名称 | — | `verified` |
| 东财-slist · `f14` | f14 | 板块名称 | — | `verified` |
| 东财-ulist239(np/get) · `f14` | f14 | 股票名称 | - | `verified` |

### `f140` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f140` | f140 / f136 | 领涨股名称 / 领涨涨跌幅 | — | `verified` |
| 东财-push2(stock/get) · `f140` | f140 | — | 元 | `verified` |
| 东财-slist · `f140` | f140 | 板块龙头股代码 | — | `verified` |
| 东财-ulist239(np/get) · `f140` | — | — | — | `conflict` |
| 东财-资金流(em_fund_flow) · `f140` | f140 | — | 元 | `verified` |

### `f141` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f141` | — | — | — | `unverified` |
| 东财-push2(stock/get) · `f141` | f141 | — | 元 | `verified` |
| 东财-ulist239(np/get) · `f141` | — | — | — | `conflict` |
| 东财-资金流(em_fund_flow) · `f141` | f141 | — | 元 | `verified` |

### `f142` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f142` | f142 | — | 元 | `verified` |
| 东财-ulist239(np/get) · `f142` | — | — | — | `conflict` |
| 东财-资金流(em_fund_flow) · `f142` | f142 | — | 元 | `verified` |

### `f143` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f143` | f143 | — | 元 | `verified` |
| 东财-ulist239(np/get) · `f143` | — | — | — | `conflict` |
| 东财-资金流(em_fund_flow) · `f143` | f143 | — | 元 | `verified` |

### `f144` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f144` | f144 | — | 元 | `verified` |
| 东财-ulist239(np/get) · `f144` | — | — | — | `conflict` |
| 东财-资金流(em_fund_flow) · `f144` | f144 | — | 元 | `verified` |

### `f145` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f145` | f145 | — | 元 | `verified` |
| 东财-ulist239(np/get) · `f145` | — | — | — | `conflict` |
| 东财-资金流(em_fund_flow) · `f145` | f145 | — | 元 | `verified` |

### `f146` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f146` | f146 | — | 元 | `verified` |
| 东财-ulist239(np/get) · `f146` | — | — | — | `conflict` |
| 东财-资金流(em_fund_flow) · `f146` | f146 | — | 元 | `verified` |

### `f147` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f147` | — | 待破解 | 元 | `verified` |
| 东财-ulist239(np/get) · `f147` | f147 | — | — | `verified` |
| 东财-资金流(em_fund_flow) · `f147` | f147 | — | 元 | `verified` |

### `f148` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f148` | — | 待破解 | 元 | `verified` |
| 东财-ulist239(np/get) · `f148` | f148 | — | — | `unverified` |
| 东财-资金流(em_fund_flow) · `f148` | f148 | — | 元 | `verified` |

### `f149` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f149` | — | 待破解 | 元 | `conflict` |
| 东财-ulist239(np/get) · `f149` | — | — | — | `unverified` |
| 东财-资金流(em_fund_flow) · `f149` | f149 | — | 元 | `conflict` |

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
| 东财-push2(stock/get) · `f152` | f152 | — | — | `verified` |
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

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f160` | f109 / f160 | 涨跌幅 | % | `verified` |
| 东财-push2(stock/get) · `f160` | eps_annual(f160) | 待破解 | 元/股 | `unverified` |
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

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f163` | f163 | — | — | `verified` |
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
| 东财-em_kline_f61 · `f168` | f168 | — | — | `verified` |
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

聚合问题：canonical_differs；canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f174` | f174 / f175 | 主力净额 | 元/% | `verified` |
| 东财-push2(stock/get) · `f174` | — | — | — | `unverified` |
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

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f190` | f190 | — | — | `verified` |
| 东财-ulist239(np/get) · `f190` | f190 | 每股未分配利润 | 元/股 | `verified` |

### `f191` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f191` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f191` | f191 | — | — | `verified` |

### `f192` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f192` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f192` | f192 | — | — | `verified` |

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

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f27` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f27` | f27 | — | — | `unverified` |

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

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f43` | — | — | — | `unverified` |
| 东财-push2(stock/get) · `f43` | f43 | 现价 | 元 | `verified` |
| 东财-ulist239(np/get) · `f43` | f43 | — | — | `verified` |

### `f44` — ambiguous

聚合问题：canonical_differs；meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f44` | f44 | 最高价 | 元 | `verified` |
| 东财-ulist239(np/get) · `f44` | lirunzonghe | 利润总额 | 元 | `verified` |

### `f45` — incomplete

聚合问题：meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f45` | f45 | 最低价 | 元 | `verified` |
| 东财-ulist239(np/get) · `f45` | f45 | — | — | `unverified` |

### `f46` — incomplete

聚合问题：meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f46` | f46 | 开盘价 | 元 | `verified` |
| 东财-ulist239(np/get) · `f46` | f46 | — | — | `unverified` |

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
| 东财-push2(stock/get) · `f51` | f51 | 日期 | YYYY-MM-DD | `verified` |
| 东财-ulist239(np/get) · `f51` | liudongzichan | 流动资产 | 元 | `verified` |
| 东财-资金流(em_fund_flow) · `f51` | — | — | — | `unverified` |

### `f52` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f52` | f52 | 开盘价 | 元 | `verified` |
| 东财-push2(stock/get) · `f52` | f52 | 开盘价 | 元 | `verified` |
| 东财-ulist239(np/get) · `f52` | gudingzichan | 固定资产 | 元 | `verified` |
| 东财-资金流(em_fund_flow) · `f52` | — | — | — | `unverified` |

### `f53` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f53` | f53 | 收盘价 | 元 | `verified` |
| 东财-push2(stock/get) · `f53` | f53 | 收盘价 | 元 | `verified` |
| 东财-ulist239(np/get) · `f53` | f53 | — | — | `verified` |
| 东财-资金流(em_fund_flow) · `f53` | — | — | — | `unverified` |

### `f54` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f54` | f54 | 最高价 | 元 | `verified` |
| 东财-push2(stock/get) · `f54` | f54 | 最高价 | 元 | `verified` |
| 东财-ulist239(np/get) · `f54` | f54 | — | — | `verified` |
| 东财-资金流(em_fund_flow) · `f54` | — | — | — | `unverified` |

### `f55` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f55` | f55 | 最低价 | 元 | `verified` |
| 东财-push2(stock/get) · `f55` | f55 | 最低价 | 元 | `verified` |
| 东财-ulist239(np/get) · `f55` | liudongfuzhai | 流动负债 | 元 | `verified` |
| 东财-资金流(em_fund_flow) · `f55` | — | — | — | `unverified` |

### `f56` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f56` | f56 | 成交量 | 手 | `verified` |
| 东财-push2(stock/get) · `f56` | f56 | 成交量 | 手 | `verified` |
| 东财-ulist239(np/get) · `f56` | f56 | — | — | `verified` |
| 东财-资金流(em_fund_flow) · `f56` | — | — | — | `unverified` |

### `f57` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f57` | f57 | 成交额 | 元 | `verified` |
| 东财-push2(stock/get) · `f57` | f57 | — | — | `verified` |
| 东财-ulist239(np/get) · `f57` | f57 | — | — | `verified` |
| 东财-资金流(em_fund_flow) · `f57` | — | — | — | `unverified` |

### `f58` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f58` | f58 | 振幅% | % | `verified` |
| 东财-push2(stock/get) · `f58` | f58 | — | — | `verified` |
| 东财-ulist239(np/get) · `f58` | f58 | — | — | `verified` |

### `f59` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f59` | f59 | 涨跌幅 | % | `conflict` |
| 东财-push2(stock/get) · `f59` | f59 | 涨跌幅 | % | `conflict` |
| 东财-ulist239(np/get) · `f59` | f59 | — | — | `conflict` |

### `f60` — ambiguous

聚合问题：canonical_differs；meaning_differs；meaning_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f60` | f60 | 涨跌额 | 元 | `verified` |
| 东财-push2(stock/get) · `f60` | f60 | — | 元 | `verified` |
| 东财-ulist239(np/get) · `f60` | zibengongjijin | 资本公积金 | 元 | `verified` |

### `f61` — incomplete

聚合问题：meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f61` | f61 | 换手率% | % | `verified` |
| 东财-push2(stock/get) · `f61` | f61 | 换手率% | % | `verified` |
| 东财-ulist239(np/get) · `f61` | f61 | — | — | `verified` |

### `f62` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f62` | f62 | 主力净流入额 | 元 | `verified` |
| 东财-push2(stock/get) · `f62` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f62` | f62 | 主力净流入额 | 元 | `verified` |
| 东财-资金流(em_fund_flow) · `f62` | — | — | — | `unverified` |

### `f63` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f63` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f63` | f63 | — | — | `unverified` |

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

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f76` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f76` | f76 | — | — | `verified` |

### `f77` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f77` | — | — | — | `unverified` |
| 东财-ulist239(np/get) · `f77` | f77 | — | — | `verified` |

### `f78` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-clist · `f78` | f66 / f72 / f78 / f84 | 超大/大/中/小单净额 | 元 | `verified` |
| 东财-push2(stock/get) · `f78` | f78 | — | — | `verified` |
| 东财-ulist239(np/get) · `f78` | f78 | — | — | `verified` |
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

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-em_kline_f61 · `f85` | — | — | — | `unverified` |
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

聚合问题：meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2(stock/get) · `f92` | f92 | — | — | `verified` |
| 东财-ulist239(np/get) · `f92` | f92 | — | — | `verified` |

### `first_limit_time` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2ex · `first_limit_time` | — | — | — | `unverified` |
| 同花顺-fuyao · `first_limit_time` | first_limit_time | 首次与最后跌停时间，上海时区 `HH:mm`。 | HH:mm | `verified` |

### `first_limit_up_time` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare · `first_limit_up_time` | — | — | — | `unverified` |
| 东财-热榜(em_hot) · `first_limit_up_time` | first_limit_up_time | Unix 秒时间戳 | — | `verified` |

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

### `growth.calculate_operating_income_yoy_growth_ratio` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `growth.calculate_operating_income_yoy_growth_ratio` | growth.calculate_operating_income_yoy_growth_ratio | — | — | `conflict` |

### `growth.calculate_parent_holder_net_profit_yoy_growth_ratio` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `growth.calculate_parent_holder_net_profit_yoy_growth_ratio` | growth.calculate_parent_holder_net_profit_yoy_growth_ratio | — | — | `conflict` |

### `high` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `high` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `high` | time / open / high / low / close | 时间 / OHLC | — | `unverified` |
| 同花顺-fuyao · `high` | — | — | — | `unverified` |

### `hot_rank` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-热榜(em_hot) · `hot_rank` | — | — | — | `unverified` |
| 同花顺-fuyao · `hot_rank` | hot_rank | 同花顺人气排名，数值越小越靠前。 | — | `verified` |

### `ipo_date` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `ipo_date` | — | — | — | `verified` |
| TDX-eltdx(适配层) · `ipo_date` | — | — | — | `unverified` |

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

### `jing_li_run_raw_float` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `jing_li_run_raw_float` | jing_li_run_raw_float | 净利润原始值 | 千元 | `unverified` |
| TDX-eltdx(适配层) · `jing_li_run_raw_float` | — | — | — | `unverified` |

### `lastEmRatingName` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `lastEmRatingName` | lastEmRatingName | — | — | `conflict` |

### `last_limit_time` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2ex · `last_limit_time` | — | — | — | `unverified` |
| 同花顺-fuyao · `last_limit_time` | last_limit_time | 首次与最后跌停时间，上海时区 `HH:mm`。 | HH:mm | `verified` |

### `last_price` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `last_price` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `last_price` | last_price | — | — | `unverified` |
| 同花顺-fuyao · `last_price` | 派生 `last_price ÷ f92(BPS) | — | — | `conflict` |

### `level` — ambiguous

聚合问题：meaning_differs；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `level` | level | 待破解 | — | `unverified` |
| 财联社(cls) · `level` | level | 快讯等级（重要性分级） | — | `unverified` |

### `limit_count` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-push2ex · `limit_count` | — | — | — | `unverified` |
| 市场源(market_sources) · `limit_count` | limit_count | 连板数 | — | `verified` |
| 开盘红(Levistock适配) · `limit_count` | limit_tag / limit_count | 待破解 | — | `unverified` |

### `limit_down` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `limit_down` | — | — | — | `unverified` |
| 新浪(扩展API) · `limit_down` | limit_up / limit_down | 涨跌停价 | — | `unverified` |

### `limit_down_price` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `limit_down_price` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `limit_down_price` | limit_up_price / limit_down_price | 涨停价 / 跌停价 | — | `unverified` |

### `limit_time` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `limit_time` | limit_time | 涨停时间 | — | `unverified` |
| 开盘红 · `limit_time` | limit_time | 涨停时间；与 KPL zt_time 两日逐值一致 | Unix 秒 | `verified` |
| 开盘红(Levistock适配) · `limit_time` | limit_time / open_time | 待破解 | — | `unverified` |

### `limit_up` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `limit_up` | — | — | — | `unverified` |
| 新浪(扩展API) · `limit_up` | limit_up / limit_down | 涨跌停价 | — | `unverified` |

### `limit_up_count` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `limit_up_count` | limit_up_count | — | — | `unverified` |
| 开盘啦(kpl) · `limit_up_count` | — | — | — | `unverified` |

### `limit_up_price` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare · `limit_up_price` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `limit_up_price` | limit_up_price / limit_down_price | 涨停价 / 跌停价 | — | `unverified` |

### `list` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `list` | meta/tickers/list | — | — | `unverified` |
| 开盘啦(kpl) · `list` | — | — | — | `unverified` |
| 财联社(cls) · `list` | — | — | — | `unverified` |

### `liu_tong_gu_ben_raw_float` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `liu_tong_gu_ben_raw_float` | liu_tong_gu_ben_raw_float | 流通股本原始值 | 万股 | `unverified` |
| TDX-eltdx(适配层) · `liu_tong_gu_ben_raw_float` | — | — | — | `unverified` |

### `locked_amount` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `locked_amount` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `locked_amount` | vol_rise_speed / locked_amount | 量涨速 / 封单额（=bid1×bid_vol1×100） | — | `unverified` |

### `low` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `low` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `low` | time / open / high / low / close | 时间 / OHLC | — | `unverified` |
| 同花顺-fuyao · `low` | — | — | — | `unverified` |

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
| Levistock历史未归属 · `main_inflow` | — | — | — | `unverified` |
| 市场源(market_sources) · `main_inflow` | — | — | — | `unverified` |
| 开盘啦(kpl_limit_up_detail) · `main_inflow` | main_inflow | 主力净流入；与 KPH net_inflow 两日逐值一致 | 元 | `verified` |

### `main_net` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `main_net` | — | — | — | `unverified` |
| 开盘啦(kpl) · `main_net` | main_net | 主力净额(≡主力净买入额) | 元 | `unverified` |

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

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `market` | market | 市场代码 | 0=深/1=沪/2=京 | `verified` |
| ZHB-tdxstat · `market` | — | — | — | `unverified` |
| ZHB-tdxstat2 · `market` | — | — | — | `unverified` |
| reports · `market` | market | 交易所 | — | `verified` |
| 东财-热榜(em_hot) · `market` | market | 市场 | — | `verified` |
| 同花顺-fuyao · `market` | dump/market-dumps/{daily-k,daily-k-10d,adjustment-factors}/download-url | — | — | `unverified` |
| 市场源(market_sources) · `market` | market | 市场 | — | `verified` |

### `max_seal` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `max_seal` | — | — | — | `unverified` |
| 开盘啦(kpl_limit_up_detail) · `max_seal` | max_seal | 封单量；与 KPH seal_amount 两日逐值一致，计量单位未确认 | — | `verified` |

### `name` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `name` | — | — | — | `unverified` |
| TDX(双命名源) · `name` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `name` | name | — | — | `unverified` |
| 东财-push2ex · `name` | — | — | — | `unverified` |
| 东财-热榜(em_hot) · `name` | — | — | — | `verified` |
| 同花顺-fuyao · `name` | — | — | — | `unverified` |
| 市场源(market_sources) · `name` | name | 股票名称 | — | `verified` |
| 开盘啦(kpl) · `name` | name | 股票名称 | — | `unverified` |
| 财联社(cls) · `name` | — | — | — | `unverified` |

### `net_inflow` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 开盘红 · `net_inflow` | main_inflow | 主力净流入；与 KPL main_inflow 两日逐值一致 | 元 | `verified` |
| 开盘红(Levistock适配) · `net_inflow` | net_inflow / market_cap | 待破解 | — | `unverified` |

### `net_profit` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `net_profit` | — | — | — | `unverified` |
| 同花顺-fuyao · `net_profit` | net_profit | 净利润 | JLY（净利润） | `conflict` |

### `netamount` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 新浪(扩展API) · `netamount` | netamount | 净流入额 | — | `conflict` |

### `newIssuePrice` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `newIssuePrice` | — | — | — | `conflict` |

### `newListingDate` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `newListingDate` | — | — | — | `conflict` |

### `newPeIssueA` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `newPeIssueA` | — | — | — | `conflict` |

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

### `northbound_hold.date` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-datacenter(英文键) · `northbound_hold.date` | northbound_hold.date | 北向持股快照报告期(YYYY-MM-DD) | — | `conflict` |

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

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `open` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `open` | time / open / high / low / close | 时间 / OHLC | — | `unverified` |
| 同花顺-fuyao · `open` | — | — | — | `unverified` |
| 新浪(扩展API) · `open` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | — | `unverified` |

### `open_price` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `open_price` | open_price | — | — | `unverified` |
| 同花顺-fuyao · `open_price` | — | — | — | `unverified` |

### `open_times` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `open_times` | — | — | — | `unverified` |
| 同花顺-fuyao · `open_times` | open_times | 开板次数。 | 次 | `verified` |

### `opendate` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 新浪(扩展API) · `opendate` | opendate | 日期 | — | `conflict` |

### `pb` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `pb` | — | — | — | `unverified` |
| TDX(双命名源) · `pb` | — | — | — | `unverified` |
| 开盘啦(kpl) · `pb` | pb | 市净率 | 倍 | `unverified` |

### `pct` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-热榜(em_hot) · `pct` | pct | 涨跌幅 | % | `verified` |
| 财联社(cls) · `pct` | — | — | — | `unverified` |

### `pe_dynamic` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `pe_dynamic` | — | — | — | `unverified` |
| 开盘啦(kpl) · `pe_dynamic` | pe_dynamic | 动态PE（最新报告期年化） | 倍 | `conflict` |

### `pe_static` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `pe_static` | — | — | — | `unverified` |
| TDX(双命名源) · `pe_static` | — | — | — | `unverified` |
| 开盘啦(kpl) · `pe_static` | pe_static | 静态PE（上年度年报 LYR） | 倍 | `conflict` |

### `pe_ttm` — ambiguous

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `pe_ttm` | — | — | — | `unverified` |
| TDX(双命名源) · `pe_ttm` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `pe_ttm` | pe_ttm | — | — | `unverified` |
| ZHB-tdxstat · `pe_ttm` | pe_ttm | 市盈率（TTM） | 倍 | `verified` |
| 同花顺-fuyao · `pe_ttm` | — | — | — | `unverified` |
| 开盘啦(kpl) · `pe_ttm` | pe_ttm | PE(TTM) | 倍 | `conflict` |

### `performance` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `performance` | — | — | — | `unverified` |
| 市场源(market_sources) · `performance` | performance | 昨涨停今表现 | — | `unverified` |

### `plate_code` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `plate_code` | — | — | — | `unverified` |
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
| Levistock历史未归属 · `pre_close` | — | — | — | `unverified` |
| TDX(双命名源) · `pre_close` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `pre_close` | pre_close | — | — | `unverified` |

### `pre_close_price` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `pre_close_price` | — | — | — | `unverified` |
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

### `prev_price` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `prev_price` | 派生 `prev_price × 板块涨停幅度 | — | — | `conflict` |

### `price` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `price` | — | — | — | `unverified` |
| TDX(双命名源) · `price` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `price` | price | — | — | `unverified` |
| 东财-datacenter(英文键) · `price` | — | — | — | `unverified` |
| 东财-push2ex · `price` | — | — | — | `unverified` |
| 东财-热榜(em_hot) · `price` | price | 现价 | 元 | `verified` |
| 市场源(market_sources) · `price` | price | 现价 | — | `verified` |
| 开盘啦(kpl) · `price` | price | 现价 | 元 | `unverified` |

### `profitability` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `profitability` | profitability | — | — | `conflict` |

### `profitability.index_weighted_avg_roe` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `profitability.index_weighted_avg_roe` | profitability.index_weighted_avg_roe | — | — | `conflict` |

### `profitability.sale_gross_margin` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `profitability.sale_gross_margin` | profitability.sale_gross_margin | — | — | `conflict` |

### `profitability.sale_net_interest_ratio` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `profitability.sale_net_interest_ratio` | profitability.sale_net_interest_ratio | — | — | `conflict` |

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

聚合问题：canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 东财-热榜(em_hot) · `reason` | reason | 题材归因 | — | `verified` |
| 市场源(market_sources) · `reason` | — | — | — | `unverified` |
| 开盘红(Levistock适配) · `reason` | reason | 涨停原因 | — | `unverified` |

### `report_type` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 新浪(扩展API) · `report_type` | report_type | fzb(资产负债)/lrb(利润)/llb(现金流) | — | `conflict` |

### `researcher` — incomplete

聚合问题：canonical_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `researcher` | — | 研究员姓名 | — | `conflict` |

### `rise_speed` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `rise_speed` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `rise_speed` | rise_speed / short_turnover | 涨速 / 短换手 | — | `unverified` |

### `seal_amount` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX-eltdx(适配层) · `seal_amount` | seal_amount | — | — | `unverified` |
| 市场源(market_sources) · `seal_amount` | — | — | — | `unverified` |
| 开盘啦(kpl_limit_up_detail) · `seal_amount` | seal_amount | 封单金额；与 KPH seal_money 两日逐值一致 | 元 | `verified` |
| 开盘红 · `seal_amount` | max_seal | 封单量；与 KPL max_seal 两日逐值一致，计量单位未确认 | — | `verified` |
| 开盘红(Levistock适配) · `seal_amount` | seal_amount / seal_money | 待破解 | — | `unverified` |

### `seal_money` — ambiguous

聚合问题：canonical_differs；meaning_differs；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `seal_money` | seal_money | 当前封单额，单位元。 | 元 | `verified` |
| 开盘红 · `seal_money` | seal_amount | 封单金额；与 KPL seal_amount 两日逐值一致 | 元 | `verified` |
| 开盘红(Levistock适配) · `seal_money` | seal_amount / seal_money | 待破解 | — | `unverified` |

### `solvency` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `solvency` | solvency | — | — | `conflict` |

### `solvency.assets_debt_ratio` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `solvency.assets_debt_ratio` | solvency.assets_debt_ratio | — | — | `conflict` |

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
| Levistock历史未归属 · `speed` | — | — | — | `unverified` |
| 市场源(market_sources) · `speed` | — | — | — | `unverified` |
| 开盘啦(kpl) · `speed` | speed | 涨速 | — | `unverified` |

### `stat.unknown_26` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| ZHB-tdxstat · `stat.unknown_26` | stat.unknown_26 | 年内涨停天数 YearZTDay·L2候选(列[26]已定YearZTDay: ihelp.dat L64官方定义+事件级Δ实证, 待≥90%命中升L1) | - | `conflict` |

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

### `time` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `time` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `time` | time / open / high / low / close | 时间 / OHLC | — | `unverified` |
| 东财-热榜(em_hot) · `time` | time | 分钟时间点 | — | `verified` |
| 市场源(market_sources) · `time` | time | 时间 | — | `verified` |
| 开盘啦(kpl) · `time` | — | — | — | `unverified` |
| 财联社(cls) · `time` | — | — | — | `unverified` |

### `title` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `title` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `title` | — | — | — | `unverified` |
| reports · `title` | title | 研报标题 | — | `verified` |
| 巨潮(cninfo) · `title` | — | — | — | `unverified` |
| 财联社(cls) · `title` | title / brief | 标题 / 摘要 | — | `verified` |

### `total_mv` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `total_mv` | — | — | — | `unverified` |
| 开盘啦(kpl) · `total_mv` | total_mv | 总市值 | 元 | `unverified` |

### `total_shares` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `total_shares` | circulating_shares / total_shares | 待破解 | 股 | `unverified` |
| 开盘啦(kpl) · `total_shares` | — | — | — | `unverified` |

### `trade` — consistent

聚合问题：source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 新浪(扩展API) · `trade` | trade | 收盘价 | — | `conflict` |

### `trade_date` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| FTShare · `trade_date` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `trade_date` | — | — | — | `unverified` |
| 市场源(market_sources) · `trade_date` | — | — | — | `unverified` |
| 财联社(cls) · `trade_date` | trade_date / plates | 轮动日期 / 当日 top10 板块列表 | — | `unverified` |

### `tshare` — incomplete

聚合问题：unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| reports · `tshare` | tshare | 总市值 | — | `verified` |
| 东财-push2ex · `tshare` | tshare | 总市值 | 元 | `verified` |

### `turnover` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_status_conflict；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `turnover` | — | — | — | `unverified` |
| 开盘啦(kpl) · `turnover` | — | — | — | `unverified` |
| 开盘红 · `turnover` | amount | 成交额；与 KPL amount 两日逐值一致 | 元 | `verified` |
| 开盘红(Levistock适配) · `turnover` | turnover / turnover_rate | 成交额 / 换手率% | — | `unverified` |
| 新浪(扩展API) · `turnover` | turnover | 换手率% | — | `conflict` |

### `turnover_pct` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `turnover_pct` | — | — | — | `unverified` |
| TDX(双命名源) · `turnover_pct` | — | — | — | `unverified` |
| 开盘啦(kpl) · `turnover_pct` | turnover_pct | 换手率% | % | `unverified` |

### `turnover_rate` — ambiguous

聚合问题：canonical_differs；canonical_incomplete；meaning_differs；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `turnover_rate` | — | — | — | `unverified` |
| 东财-push2ex · `turnover_rate` | — | — | — | `unverified` |
| 东财-热榜(em_hot) · `turnover_rate` | turnover_rate | 换手率% | — | `verified` |
| 开盘红 · `turnover_rate` | turnover_real | 实际换手率；与 KPL turnover_real 两日逐值一致 | % | `verified` |

### `turnover_real` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 市场源(market_sources) · `turnover_real` | — | — | — | `unverified` |
| 开盘啦(kpl_limit_up_detail) · `turnover_real` | turnover_real | 实际换手率；与 KPH turnover_rate 两日逐值一致 | % | `verified` |

### `updated_date` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；source_statuses_differ；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `updated_date` | — | — | — | `verified` |
| TDX-eltdx(适配层) · `updated_date` | — | — | — | `unverified` |

### `valuation.pb_mrq` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `valuation.pb_mrq` | valuation.pb_mrq | — | — | `conflict` |

### `valuation.pe_mrq` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `valuation.pe_mrq` | valuation.pe_mrq | — | — | `conflict` |

### `valuation.pe_ttm` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `valuation.pe_ttm` | valuation.pe_ttm | — | — | `conflict` |

### `valuation.ps_ttm` — incomplete

聚合问题：meaning_incomplete；source_status_conflict；聚合状态：`conflict`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| 同花顺-fuyao · `valuation.ps_ttm` | valuation.ps_ttm | — | — | `conflict` |

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
| Levistock历史未归属 · `vol_ratio` | — | — | — | `unverified` |
| TDX(双命名源) · `vol_ratio` | — | — | — | `unverified` |
| 市场源(market_sources) · `vol_ratio` | — | — | — | `unverified` |
| 开盘啦(kpl) · `vol_ratio` | vol_ratio | 量比 | — | `unverified` |

### `volume` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| Levistock历史未归属 · `volume` | — | — | — | `unverified` |
| TDX(双命名源) · `volume` | — | — | — | `unverified` |
| TDX-eltdx(适配层) · `volume` | volume | — | — | `unverified` |
| 同花顺-fuyao · `volume` | — | — | — | `unverified` |

### `zong_gu_ben_raw_float` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `zong_gu_ben_raw_float` | zong_gu_ben_raw_float | 总股本原始值 | 万股 | `unverified` |
| TDX-eltdx(适配层) · `zong_gu_ben_raw_float` | — | — | — | `unverified` |

### `zong_zi_chan_raw_float` — incomplete

聚合问题：canonical_incomplete；meaning_incomplete；unit_incomplete；聚合状态：`unverified`。

| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) · `zong_zi_chan_raw_float` | zong_zi_chan_raw_float | 总资产原始值 | 千元 | `unverified` |
| TDX-eltdx(适配层) · `zong_zi_chan_raw_float` | — | — | — | `unverified` |

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
| Levistock历史未归属 | `all` | market_index_em / all | — | `verified` |
| Levistock历史未归属 | `belong` | sector_stocks_em / belong | — | `verified` |
| Levistock历史未归属 | `is_trade_day` | is_trade_day / get_trade_days | — | `verified` |
| Levistock历史未归属 | `limit_up_his_kph` | limit_up_his_kph / wind_vane | — | `verified` |
| Levistock历史未归属 | `market_index_em` | market_index_em / all | — | `verified` |
| Levistock历史未归属 | `rotation` | get_sector_heat / rotation | — | `verified` |
| Levistock历史未归属 | `sector_stocks_em` | sector_stocks_em / belong | — | `verified` |
| Levistock历史未归属 | `stocks_all_em` | stocks_em / stocks_all_em | — | `verified` |
| Levistock历史未归属 | `stocks_em` | stocks_em / stocks_all_em | — | `verified` |
| Levistock历史未归属 | `wind_stocks` | market_wind_cls / wind_stocks | — | `verified` |
| Levistock历史未归属 | `wind_vane` | limit_up_his_kph / wind_vane | — | `verified` |
| TDX(双命名源) | `JZC` | JZC | 净资产/股东权益 | `verified` |
| TDX(双命名源) | `category_name` | date / category_name | 事件日期 / 类别名称 | `unverified` |
| TDX(双命名源) | `circulating_shares` | circulating_shares / total_shares | 待破解 | `unverified` |
| TDX(双命名源) | `date` | date / category_name | 事件日期 / 类别名称 | `unverified` |
| TDX(双命名源) | `jingzichan` | — | 净资产 / 股东权益 | `verified` |
| TDX(双命名源) | `net_profit_yuan` | total_assets_yuan / net_profit_yuan | 待破解 | `unverified` |
| TDX(双命名源) | `total_assets_yuan` | total_assets_yuan / net_profit_yuan | 待破解 | `unverified` |
| TDX(双命名源) | `total_shares` | circulating_shares / total_shares | 待破解 | `unverified` |
| TDX-eltdx(适配层) | `close` | time / open / high / low / close | 时间 / OHLC | `unverified` |
| TDX-eltdx(适配层) | `down_count` | up_count / down_count | 指数类上涨/下跌家数 | `unverified` |
| TDX-eltdx(适配层) | `high` | time / open / high / low / close | 时间 / OHLC | `unverified` |
| TDX-eltdx(适配层) | `limit_down_price` | limit_up_price / limit_down_price | 涨停价 / 跌停价 | `unverified` |
| TDX-eltdx(适配层) | `limit_up_price` | limit_up_price / limit_down_price | 涨停价 / 跌停价 | `unverified` |
| TDX-eltdx(适配层) | `locked_amount` | vol_rise_speed / locked_amount | 量涨速 / 封单额（=bid1×bid_vol1×100） | `unverified` |
| TDX-eltdx(适配层) | `low` | time / open / high / low / close | 时间 / OHLC | `unverified` |
| TDX-eltdx(适配层) | `min2_amount` | min2_amount / opening_rush | 近2分钟金额 / 开盘抢筹 | `unverified` |
| TDX-eltdx(适配层) | `open` | time / open / high / low / close | 时间 / OHLC | `unverified` |
| TDX-eltdx(适配层) | `opening_rush` | — | 近2分钟金额 / 开盘抢筹 | `unverified` |
| TDX-eltdx(适配层) | `rise_speed` | rise_speed / short_turnover | 涨速 / 短换手 | `unverified` |
| TDX-eltdx(适配层) | `short_turnover` | rise_speed / short_turnover | 涨速 / 短换手 | `unverified` |
| TDX-eltdx(适配层) | `shortline.auction_prev_volume_ratio` | shortline.auction_prev_volume_ratio | 竞价量/昨量比 | `verified` |
| TDX-eltdx(适配层) | `shortline.open_prev_amount_ratio` | shortline.open_prev_amount_ratio | 开盘额/昨额比 | `verified` |
| TDX-eltdx(适配层) | `shortline.open_prev_seal_ratio` | shortline.open_prev_seal_ratio | 开盘额/昨封单额比 | `verified` |
| TDX-eltdx(适配层) | `shortline.seal_prev_ratio` | shortline.seal_prev_ratio | 封单/前封单比 | `verified` |
| TDX-eltdx(适配层) | `shortline.seal_to_amount_ratio` | shortline.seal_to_amount_ratio | 封单/成交额比 | `verified` |
| TDX-eltdx(适配层) | `shortline.seal_to_float_ratio` | shortline.seal_to_float_ratio | 封单/流通市值比 | `verified` |
| TDX-eltdx(适配层) | `time` | time / open / high / low / close | 时间 / OHLC | `unverified` |
| TDX-eltdx(适配层) | `up_count` | up_count / down_count | 指数类上涨/下跌家数 | `unverified` |
| TDX-eltdx(适配层) | `vol_rise_speed` | vol_rise_speed / locked_amount | 量涨速 / 封单额（=bid1×bid_vol1×100） | `unverified` |
| ZHB-tdxstat | `[22]` | [22] | 形态/板块代码 ShapeValue | `verified` |
| ZHB-tdxstat | `[5]` | [5] | 连涨/连跌天数 | `verified` |
| ZHB-tdxstat | `[9]` | [9] | 市盈率（静态/LYR） | `verified` |
| ZHB-tdxstat | `change_30d` | change_20d | 与同来源同路径 change_20d 完全重复的历史兼容键，不是独立的 30 日涨跌幅 | `disproved` |
| ZHB-tdxstat | `stat.change_30d` | stat.change_20d | 与同来源同路径 stat.change_20d 完全重复的历史兼容键，不是独立的 30 日涨跌幅 | `disproved` |
| ZHB-tdxstat | `stat.unknown_2` | stat.unknown_2 | 贝塔系数(60日)·L2候选(列[2]已定BetaValue: ihelp.dat L63官方定义+慢变特征实证自相关0.91, 待真实指数基准复现升L1) | `candidate` |
| ZHB-tdxstat | `stat.unknown_26` | stat.unknown_26 | 年内涨停天数 YearZTDay·L2候选(列[26]已定YearZTDay: ihelp.dat L64官方定义+事件级Δ实证, 待≥90%命中升L1) | `conflict` |
| ZHB-tdxstat | `stat.zt_type_code` | stat.zt_type_code | 行情状态/涨跌强度分档码 | `verified` |
| ZHB-tdxstat2 | `[13]` | [13] | 通达信板块归属(881=行业板块稳定 / 880=概念·风格板块动态) | `verified` |
| ZHB-tdxstat2 | `[4]` | [4] | limit_up_down_seal: 封单额（万元，涨停为正/跌停为负） | `verified` |
| ZHB-tipinfo | `[13]` | [13] | 解禁日 = 官方 RecentReleaseDate（二进制 `解禁数量:%.2f万` 实证；旧标"股权登记日/配股"为误译——Col[14] 量级=解禁股数万股, 与 Col[11]/[12] 配股重复赋值矛盾已解） | `verified` |
| ZHB-tipinfo | `[19]` | [19] | 回购预案公告日 = 官方 RecentHGDate（"HG"=HuiGou 回购；二进制 `回购预案:上限%.2f亿元` 实证） | `verified` |
| ZHB-tipinfo | `[20]` | [20] | 回购预案金额上限(亿元) = 官方 RecentHGAmo（二进制 `回购预案:上限%.2f亿元` 一锤定音；旧标"增发配股价"证伪） | `verified` |
| ZHB-tipinfo | `[21]` | [21] | 股权激励预案/草案公告日 | `verified` |
| ZHB-tipinfo | `[6]` | [6] | 阶段新高日 = 官方 TopDate_Recent（"Top"=顶部/新高, 旧标"最近除息日"为音近误读, 已证伪） | `verified` |
| ZHB-tipinfo | `[8]` | [8] | 业绩预告日 = 官方 ForecastDate（二进制 `业绩预告:%s` 实证；旧标"分红日"证伪——Col[9] 全市场 83.0% 负值, 分红恒非负） | `verified` |
| ZHB-tipinfo | `[9]` | [9] | 业绩预告金额 (万元, 可负) = 官方 ForecastAmount（Col[9] 全市场 83.0% 负值/median=-95.98, 分红恒非负 → 必为预告净利） | `verified` |
| ZHB-tipinfo | `tipinfo.equity_incentive_date` | tipinfo.equity_incentive_date | 股权激励预案/草案公告日 | `verified` |
| reports | `BUY_RATIO` | BUY_RATIO / SELL_RATIO | 买入/卖出占比 | `unverified` |
| reports | `BUY_SEAT` | BUY_SEAT / SELL_SEAT | 买入/卖出前5席位数 | `unverified` |
| reports | `NextTwoYear` | predictThisYearEps / NextYear / NextTwoYear | 今年/明年/后年 EPS 预测 | `verified` |
| reports | `NextYear` | predictThisYearEps / NextYear / NextTwoYear | 今年/明年/后年 EPS 预测 | `verified` |
| reports | `RQJMG` | RZJME / RQJMG | 融资净买入 / 融券净卖出 | `unverified` |
| reports | `RZJME` | RZJME / RQJMG | 融资净买入 / 融券净卖出 | `unverified` |
| reports | `SELL_RATIO` | BUY_RATIO / SELL_RATIO | 买入/卖出占比 | `unverified` |
| reports | `SELL_SEAT` | BUY_SEAT / SELL_SEAT | 买入/卖出前5席位数 | `unverified` |
| reports | `adjunctSize` | adjunctSize / adjunctType | 附件大小/类型 | `unverified` |
| reports | `adjunctType` | adjunctSize / adjunctType | 附件大小/类型 | `unverified` |
| reports | `analyse` | analyse / analyse_title | 待破解 | `unverified` |
| reports | `analyse_title` | analyse / analyse_title | 待破解 | `unverified` |
| reports | `orgId` | secName / orgId | 证券名 / 机构ID | `unverified` |
| reports | `reading_num` | reading_num / share_num | 阅读数/分享数 | `unverified` |
| reports | `secName` | secName / orgId | 证券名 / 机构ID | `unverified` |
| reports | `share_num` | reading_num / share_num | 阅读数/分享数 | `unverified` |
| reports | `subject_name` | subjects / subject_name | 主题分类 | `unverified` |
| reports | `subjects` | subjects / subject_name | 主题分类 | `unverified` |
| 东财-clist | `f104` | f104 / f105 | 上涨 / 下跌家数 | `verified` |
| 东财-clist | `f105` | f104 / f105 | 上涨 / 下跌家数 | `verified` |
| 东财-clist | `f109` | f109 / f160 | 涨跌幅 | `verified` |
| 东财-clist | `f136` | f140 / f136 | 领涨股名称 / 领涨涨跌幅 | `conflict` |
| 东财-clist | `f140` | f140 / f136 | 领涨股名称 / 领涨涨跌幅 | `verified` |
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
| 东财-push2(stock/get) | `f107` | f107 | 市场标记（布尔 0/1，北交=0） | `verified` |
| 东财-push2(stock/get) | `f110` | f110 | 市场标记（布尔 0/1，北交=0） | `verified` |
| 东财-push2(stock/get) | `f118` | f118 | 市场/板块状态标记（≡ ulist:f107） | `verified` |
| 东财-push2(stock/get) | `f86` | f86 | 当日收盘/最后行情时间戳 | `verified` |
| 东财-push2ex | `yfbt` | yfbt / ylbc | 昨日首次封板时间 / 昨日连板数 | `unverified` |
| 东财-push2ex | `ylbc` | yfbt / ylbc | 昨日首次封板时间 / 昨日连板数 | `unverified` |
| 东财-push2ex | `zttj.ct` | zttj.days / zttj.ct | N天M板 | `verified` |
| 东财-push2ex | `zttj.days` | zttj.days / zttj.ct | N天M板 | `verified` |
| 东财-ulist239(np/get) | `f114` | f114 | 市盈率(静态/年报 LYR) | `verified` |
| 东财-ulist239(np/get) | `f131` | f131 | 市现率 PCF_TTM（总市值 / 经营现金流 TTM） | `verified` |
| 东财-ulist239(np/get) | `f231` | f231 | 有转债标志（0=无/3=有） | `verified` |
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
| 同花顺-fuyao | `basic_eps` | basic_eps | 基本每股收益（元/股）。 | `verified` |
| 同花顺-fuyao | `calendar` | a-share/calendar/trading-days | — | `unverified` |
| 同花顺-fuyao | `catalog` | a-share-index/catalog/ths-index-list | — | `unverified` |
| 同花顺-fuyao | `constituents` | a-share-index/constituents/ths-stock-list | — | `unverified` |
| 同花顺-fuyao | `continue_day_text` | continue_day_text | 连板文本，例如 `首板`、`5天4板`。 | `verified` |
| 同花顺-fuyao | `dump` | dump/market-dumps/{daily-k,daily-k-10d,adjustment-factors}/download-url | — | `unverified` |
| 同花顺-fuyao | `ex_date_ms` | ex_date_ms | 除权除息日，Asia/Shanghai 00:00:00 毫秒 Unix 时间戳。 | `verified` |
| 同花顺-fuyao | `fiscal_period` | fiscal_period | `FY` / `Q1` / `Q2` / `Q3` / `Q4`。 | `verified` |
| 同花顺-fuyao | `indicators` | a-share/financials/indicators | — | `unverified` |
| 同花顺-fuyao | `keyword_list` | keyword_list | 关键词列表；无关键词时返回空数组。 | `verified` |
| 同花顺-fuyao | `limit_up_reason` | limit_up_reason | 涨停原因；上游空字符串会标准化为 `null`。 | `verified` |
| 同花顺-fuyao | `list` | meta/tickers/list | — | `unverified` |
| 同花顺-fuyao | `market` | dump/market-dumps/{daily-k,daily-k-10d,adjustment-factors}/download-url | — | `unverified` |
| 同花顺-fuyao | `pay_dividends_profits_interest_cash` | pay_dividends_profits_interest_cash | 分配股利、利润或偿付利息支付的现金（原币元）。 | `verified` |
| 同花顺-fuyao | `pay_fixed_assets_etc_cash` | pay_fixed_assets_etc_cash | 购建固定资产、无形资产和其他长期资产支付的现金（原币元）。 | `verified` |
| 同花顺-fuyao | `period_end_ms` | period_end_ms | 报告期末（Asia/Shanghai 零点毫秒戳）。 | `verified` |
| 同花顺-fuyao | `rank_change` | rank_change | 排名变化，正数表示上升，负数表示下降；上游缺失时为 `null`。 | `verified` |
| 同花顺-fuyao | `rank_trend` | rank_trend | 排名趋势：`up` / `down` / `flat` / `unknown`。 | `verified` |
| 同花顺-fuyao | `revenue_ttm` | — | 营业总收入 TTM（push2 f104）；富耀 operating_income 回算口径约差 1.8%，仅近似兜底 | `unverified` |
| 同花顺-fuyao | `search` | meta/tickers/search | — | `unverified` |
| 同花顺-fuyao | `valuation.pcf_ttm` | valuation.pcf_ttm | 市现率 PCF_TTM（总市值 / 经营现金流 TTM） | `verified` |
| 同花顺-fuyao | `valuations` | a-share/valuations/snapshot | — | `unverified` |
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
| 开盘啦(kpl_limit_up_detail) | `max_seal` | max_seal | 封单量；与 KPH seal_amount 两日逐值一致，计量单位未确认 | `verified` |
| 开盘啦(kpl_limit_up_detail) | `seal_amount` | seal_amount | 封单金额；与 KPH seal_money 两日逐值一致 | `verified` |
| 开盘啦(kpl_limit_up_detail) | `turnover_real` | turnover_real | 实际换手率；与 KPH turnover_rate 两日逐值一致 | `verified` |
| 开盘啦(kpl_limit_up_detail) | `zt_time` | limit_time | 涨停时间；与 KPH limit_time 两日逐值一致 | `verified` |
| 开盘红 | `limit_time` | limit_time | 涨停时间；与 KPL zt_time 两日逐值一致 | `verified` |
| 开盘红 | `net_inflow` | main_inflow | 主力净流入；与 KPL main_inflow 两日逐值一致 | `verified` |
| 开盘红 | `seal_amount` | max_seal | 封单量；与 KPL max_seal 两日逐值一致，计量单位未确认 | `verified` |
| 开盘红 | `seal_money` | seal_amount | 封单金额；与 KPL seal_amount 两日逐值一致 | `verified` |
| 开盘红 | `turnover` | amount | 成交额；与 KPL amount 两日逐值一致 | `verified` |
| 开盘红 | `turnover_rate` | turnover_real | 实际换手率；与 KPL turnover_real 两日逐值一致 | `verified` |
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
| 新浪(扩展API) | `open` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | `unverified` |
| 新浪(扩展API) | `prev_close` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | `unverified` |
| 新浪(扩展API) | `report_type` | report_type | fzb(资产负债)/lrb(利润)/llb(现金流) | `conflict` |
| 新浪(扩展API) | `strike` | strike / prev_close / open | 行权价 / 昨收盘 / 开盘 | `unverified` |
| 新浪(扩展API) | `theta` | delta/gamma/theta/vega/iv | 希腊字母 + 隐含波动率（小数） | `unverified` |
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
