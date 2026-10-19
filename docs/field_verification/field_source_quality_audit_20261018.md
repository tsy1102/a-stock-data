# 主字典逐源定义质量审计

> 由 `scripts/audit_field_source_quality.py` 从 `field_registry.json.source_fields` 生成；本报告只检查状态与逐源元数据的一致性，不代替原始数据或上游契约核验。
> `verified_metadata_ready` 仅表示含义文本及含义/单位属性可用于锚点审核；还须满足来源独立性、运行时路径精确匹配等碰撞规则。
> 规范名别名差异单列展示，不单独阻止锚；含义缺失/占位、含义或单位冲突/分组无法对齐会阻止 verified 字段作为已知项或锚。

> Registry 日期 2026-10-18；来源身份 30 个；逐源路径 2481 条；verified 917 条，其中元数据可用 714 条、需复核 203 条。

## 全来源统计

| 来源身份 | 路径数 | verified | 元数据可用 | 缺义/占位 | 含义冲突 | 单位冲突 | 对齐歧义 | 规范名变体 | conflict 状态 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| FTShare | 6 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| Levistock历史未归属 | 136 | 18 | 0 | 18 | 0 | 0 | 0 | 0 | 0 |
| TDX(双命名源) | 305 | 68 | 66 | 2 | 2 | 2 | 0 | 19 | 0 |
| TDX-eltdx(适配层) | 294 | 64 | 64 | 0 | 0 | 0 | 0 | 0 | 0 |
| ZHB-tdxstat | 97 | 71 | 70 | 1 | 0 | 0 | 0 | 0 | 1 |
| ZHB-tdxstat2 | 65 | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| ZHB-tipinfo | 49 | 32 | 32 | 0 | 0 | 0 | 0 | 0 | 0 |
| reports | 101 | 33 | 26 | 7 | 7 | 0 | 0 | 4 | 14 |
| 东财-clist | 26 | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 1 |
| 东财-datacenter(英文键) | 100 | 43 | 41 | 1 | 1 | 2 | 0 | 1 | 15 |
| 东财-em_kline_f61 | 14 | 11 | 10 | 1 | 0 | 0 | 0 | 0 | 1 |
| 东财-push2(stock/get) | 166 | 80 | 39 | 41 | 3 | 2 | 0 | 4 | 6 |
| 东财-push2ex | 43 | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0 |
| 东财-slist | 5 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| 东财-ulist239(np/get) | 240 | 153 | 41 | 112 | 0 | 0 | 0 | 0 | 11 |
| 东财-热榜(em_hot) | 42 | 41 | 39 | 2 | 2 | 0 | 0 | 2 | 0 |
| 东财-资金流(em_fund_flow) | 30 | 10 | 0 | 10 | 0 | 0 | 0 | 0 | 5 |
| 同花顺-fuyao | 223 | 85 | 83 | 2 | 0 | 0 | 0 | 9 | 16 |
| 巨潮(cninfo) | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 市场源(market_sources) | 140 | 16 | 14 | 2 | 0 | 0 | 0 | 0 | 0 |
| 开盘啦(kpl) | 161 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 3 |
| 开盘啦(kpl_limit_up_detail) | 6 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 开盘红 | 6 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| 开盘红(Levistock适配) | 33 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 新浪(hq.sinajs) | 36 | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 0 |
| 新浪(扩展API) | 27 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 |
| 沪深交易所 | 5 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| 百度(baidu) | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 腾讯(qt.gtimg) | 88 | 64 | 62 | 2 | 0 | 0 | 0 | 5 | 1 |
| 财联社(cls) | 24 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |

## Verified 路径的语义元数据复核项

| 来源身份 | 完整 code path | 含义 | 单位 | 复核原因 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) | `ipo_date` | — | — | 含义冲突；含义为空/占位；单位冲突 |
| TDX(双命名源) | `updated_date` | — | — | 含义冲突；含义为空/占位；单位冲突 |
| ZHB-tdxstat | `[23]` | 待破解 | — | 含义为空/占位 |
| Levistock历史未归属 | `all` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `belong` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `is_trade_day` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `limit_up_his_kph` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `market_emotion_kph` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `market_index_em` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `rotation` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `sector_em` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `sector_stocks_em` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `stock_changes_em` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `stock_dt_pool_em` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `stock_strategy_wencai` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `stock_yesterday_zt_em` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `stock_zt_pool_em` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `stocks_all_em` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `stocks_em` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `wind_stocks` | — | — | 含义为空/占位 |
| Levistock历史未归属 | `wind_vane` | — | — | 含义为空/占位 |
| reports | `emRatingName` | — | — | 含义冲突；含义为空/占位 |
| reports | `industryCode` | — | — | 含义冲突；含义为空/占位 |
| reports | `industryName` | — | — | 含义冲突；含义为空/占位 |
| reports | `indvInduName` | — | — | 含义冲突；含义为空/占位 |
| reports | `infoCode` | — | — | 含义冲突；含义为空/占位 |
| reports | `predictThisYearEps` | — | — | 含义冲突；含义为空/占位 |
| reports | `reportType` | — | — | 含义冲突；含义为空/占位 |
| 东财-datacenter(英文键) | `CLOSE_PRICE` | — | — | 含义冲突；含义为空/占位；单位冲突 |
| 东财-datacenter(英文键) | `TRADE_DATE` | 交易日期 | — | 单位冲突 |
| 东财-em_kline_f61 | `f168` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f119` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f120` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f137` | — | 元 | 含义为空/占位 |
| 东财-push2(stock/get) | `f140` | — | 元 | 含义为空/占位 |
| 东财-push2(stock/get) | `f141` | — | 元 | 含义为空/占位 |
| 东财-push2(stock/get) | `f142` | — | 元 | 含义为空/占位 |
| 东财-push2(stock/get) | `f143` | — | 元 | 含义为空/占位 |
| 东财-push2(stock/get) | `f144` | — | 元 | 含义为空/占位 |
| 东财-push2(stock/get) | `f145` | — | 元 | 含义为空/占位 |
| 东财-push2(stock/get) | `f146` | — | 元 | 含义为空/占位 |
| 东财-push2(stock/get) | `f147` | 待破解 | 元 | 含义为空/占位 |
| 东财-push2(stock/get) | `f148` | 待破解 | 元 | 含义为空/占位 |
| 东财-push2(stock/get) | `f152` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f162` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f163` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f164` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f165` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f166` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f167` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f175` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f177` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f180` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f181` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f183` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f184` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f185` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f186` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f187` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f188` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f190` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f193` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f194` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f195` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f196` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f197` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f57` | — | — | 含义冲突；含义为空/占位；单位冲突 |
| 东财-push2(stock/get) | `f58` | — | — | 含义冲突；含义为空/占位；单位冲突 |
| 东财-push2(stock/get) | `f60` | — | 元 | 含义冲突；含义为空/占位 |
| 东财-push2(stock/get) | `f71` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f78` | — | — | 含义为空/占位 |
| 东财-push2(stock/get) | `f92` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f1` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f10` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f101` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f109` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f110` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f147` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f160` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f161` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f162` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f163` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f164` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f165` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f166` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f167` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f168` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f169` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f170` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f171` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f172` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f173` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f174` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f175` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f176` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f177` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f178` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f179` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f180` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f181` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f182` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f183` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f185` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f186` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f187` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f188` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f189` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f19` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f191` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f192` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f193` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f195` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f196` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f197` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f199` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f201` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f202` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f203` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f211` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f212` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f221` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f225` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f226` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f228` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f229` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f230` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f232` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f233` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f234` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f24` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f25` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f26` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f29` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f31` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f32` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f33` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f34` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f35` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f36` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f37` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f38` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f40` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f41` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f43` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f48` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f53` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f54` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f56` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f57` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f58` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f61` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f64` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f65` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f66` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f67` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f68` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f69` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f7` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f70` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f71` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f72` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f73` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f74` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f75` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f76` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f77` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f78` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f79` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f8` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f80` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f81` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f82` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f83` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f84` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f85` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f86` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f87` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f88` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f89` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f90` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f91` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f92` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f94` | — | — | 含义为空/占位 |
| 东财-ulist239(np/get) | `f95` | — | — | 含义为空/占位 |
| 东财-热榜(em_hot) | `code` | — | — | 含义冲突；含义为空/占位 |
| 东财-热榜(em_hot) | `name` | — | — | 含义冲突；含义为空/占位 |
| 东财-资金流(em_fund_flow) | `f137` | — | 元 | 含义为空/占位 |
| 东财-资金流(em_fund_flow) | `f140` | — | 元 | 含义为空/占位 |
| 东财-资金流(em_fund_flow) | `f141` | — | 元 | 含义为空/占位 |
| 东财-资金流(em_fund_flow) | `f142` | — | 元 | 含义为空/占位 |
| 东财-资金流(em_fund_flow) | `f143` | — | 元 | 含义为空/占位 |
| 东财-资金流(em_fund_flow) | `f144` | — | 元 | 含义为空/占位 |
| 东财-资金流(em_fund_flow) | `f145` | — | 元 | 含义为空/占位 |
| 东财-资金流(em_fund_flow) | `f146` | — | 元 | 含义为空/占位 |
| 东财-资金流(em_fund_flow) | `f147` | — | 元 | 含义为空/占位 |
| 东财-资金流(em_fund_flow) | `f148` | — | 元 | 含义为空/占位 |
| 同花顺-fuyao | `auction` | — | — | 含义为空/占位 |
| 同花顺-fuyao | `snapshot` | — | — | 含义为空/占位 |
| 市场源(market_sources) | `cls_market_emotion` | — | — | 含义为空/占位 |
| 市场源(market_sources) | `kph_limit_ladder` | — | — | 含义为空/占位 |
| 开盘啦(kpl) | `PE` | — | — | 含义为空/占位 |
| 腾讯(qt.gtimg) | `[40]` | 待破解 | - | 含义为空/占位 |
| 腾讯(qt.gtimg) | `[78]` | — | — | 含义为空/占位 |

## 规范名变体（不单独阻止锚）

| 来源身份 | 完整 code path | 规范名候选 | 含义 |
|:--|:--|:--|:--|
| TDX(双命名源) | `changqifuzhai` | changqifuzhai / gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry | 长期负债 |
| TDX(双命名源) | `cunhuo` | cunhuo / gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry | 存货 |
| TDX(双命名源) | `gudongrenshu` | gudongrenshu / gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry | 股东户数 |
| TDX(双命名源) | `industry` | gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry / industry | 通达信行业编码 |
| TDX(双命名源) | `ipo_date` | gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry / ipo_date / updated_date / ipo_date | — |
| TDX(双命名源) | `jinglirun` | gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry / jinglirun | 净利润 |
| TDX(双命名源) | `jingyingxianjinliu` | gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry / jingyingxianjinliu | 经营活动现金流 |
| TDX(双命名源) | `jingzichan` | gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry / jingzichan | 净资产 / 股东权益 |
| TDX(双命名源) | `liudongfuzhai` | gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry / liudongfuzhai | 流动负债 |
| TDX(双命名源) | `liutongguben` | gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry / liutongguben | 流通股本 |
| TDX(双命名源) | `meigujingzichan` | gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry / meigujingzichan | 每股净资产 |
| TDX(双命名源) | `province` | gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry / province | 省份编码 |
| TDX(双命名源) | `updated_date` | gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry / updated_date / updated_date / ipo_date | — |
| TDX(双命名源) | `weifenpeilirun` | gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry / weifenpeilirun | 未分配利润 |
| TDX(双命名源) | `yingshouzhangkuan` | gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry / yingshouzhangkuan | 应收账款 |
| TDX(双命名源) | `zhuyingshouru` | gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry / zhuyingshouru | 主营业务收入 |
| TDX(双命名源) | `zibengongjijin` | gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry / zibengongjijin | 资本公积金 |
| TDX(双命名源) | `zongguben` | gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry / zongguben | 总股本 |
| TDX(双命名源) | `zongzichan` | gudongrenshu/zongzichan/liudongfuzhai/changqifuzhai/jingzichan/zhuyingshouru/jinglirun/jingyingxianjinliu/ipo_date/liutongguben/zongguben/meigujingzichan/cunhuo/yingshouzhangkuan/zibengongjijin/weifenpeilirun/updated_date/province/industry / zongzichan | 总资产 |
| reports | `industryCode` | industryCode / industryName / industryCode | — |
| reports | `industryName` | industryName / industryName / industryCode | — |
| reports | `predictThisYearEps` | predictThisYearEps / predictThisYearEps / NextYear / NextTwoYear | — |
| reports | `reportType` | reportType / reportType / attachPages / attachSize | — |
| 东财-datacenter(英文键) | `CLOSE_PRICE` | CLOSE_PRICE / CHANGE_RATE / DEAL_PRICE / CLOSE_PRICE | — |
| 东财-push2(stock/get) | `f104` | f104 / revenue_ttm(f104) | 营业总收入 TTM |
| 东财-push2(stock/get) | `f105` | f105 / net_profit_period(f105) | 归母净利润 最新报告期 |
| 东财-push2(stock/get) | `f147` | f147 / fund_san_buy(f147) / fund_san_sell(f148) / fund_san_net(f149) | 待破解 |
| 东财-push2(stock/get) | `f148` | f148 / fund_san_buy(f147) / fund_san_sell(f148) / fund_san_net(f149) | 待破解 |
| 东财-热榜(em_hot) | `code` | code / name / order / code / name | — |
| 东财-热榜(em_hot) | `name` | code / name / order / code / name | — |
| 同花顺-fuyao | `auction` | a-share/auction/short-term-benchmark / a-share/auction/snapshot | — |
| 同花顺-fuyao | `auction.auction_price` | auction.auction_price / snapshot.open_price` = `auction.auction_price | 开盘价 |
| 同花顺-fuyao | `cash` | a-share/financials/cash-flow-statements / cash-flow | 货币资金（原币元）。 |
| 同花顺-fuyao | `net_profit_annual` | f109 net_profit_annual / net_profit_annual(f109) | 归母净利润 最新年报 |
| 同花顺-fuyao | `net_profit_period` | f105 net_profit_period / net_profit_period(f105) | 归母净利润 最新报告期 |
| 同花顺-fuyao | `ocf_ttm` | f103 ocf_ttm / ocf_ttm(f103) | 经营活动现金流量净额 TTM |
| 同花顺-fuyao | `snapshot` | a-share-index/prices/snapshot / a-share/auction/snapshot / a-share/prices/snapshot / a-share/valuations/snapshot | — |
| 同花顺-fuyao | `snapshot.open_price` | snapshot.open_price / snapshot.open_price` = `auction.auction_price | 开盘价 |
| 同花顺-fuyao | `snapshot.prev_price` | snapshot.prev_price / snapshot.prev_price` = `auction.pre_close_price | 昨收价 |
| 腾讯(qt.gtimg) | `[0]` | [0] / [0] 市场标识 | 市场标识（交易所） |
| 腾讯(qt.gtimg) | `[40]` | [40] / [40] 停牌标记 | 待破解 |
| 腾讯(qt.gtimg) | `[56]` | [56] / [56] Beta 族 | Beta 族·高置信（非 BetaValue 原值） |
| 腾讯(qt.gtimg) | `[76]` | [76] / [76] A股流通股本 | A股流通股本（= [72]） |
| 腾讯(qt.gtimg) | `[85]` | [85] / [85] 收盘参考基准价（L2 机制确认） | 收盘参考基准价（L2 机制确认） |
