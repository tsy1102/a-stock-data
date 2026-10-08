# 已验证字段的描述缺口

> 由 `field_registry.json.source_fields` 自动生成；本表只发现缺失的展示元数据，不改变字段状态或锚点资格。
> 请依据来源定义、原始样本和已存证据逐条补充，禁止按相邻字段或字段代码猜测含义。

> 缺口记录 239 条；缺少含义 207 条；缺少规范名 47 条。

| 来源 | 完整 code path | 规范名 | 含义 | 单位 | 证据章节 |
|:--|:--|:--|:--|:--|:--|
| TDX(双命名源) | `changqifuzhai` | — | 长期负债 | 角 | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `cunhuo` | — | 存货 | 角 | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `gudongrenshu` | — | 股东户数 | 户 | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `industry` | — | 通达信行业编码 | 编码值（需查表） | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `ipo_date` | — | — | — | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认；2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `jinglirun` | — | 净利润 | 角 | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `jingyingxianjinliu` | — | 经营活动现金流 | 角 | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `jingzichan` | — | 净资产 / 股东权益 | 角 | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `liudongfuzhai` | — | 流动负债 | 角 | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `liutongguben` | — | 流通股本 | 万股 | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `meigujingzichan` | — | 每股净资产 | 元/股 | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `province` | — | 省份编码 | 编码值（需查表） | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `updated_date` | — | — | — | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认；2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `weifenpeilirun` | — | 未分配利润 | 角 | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `yingshouzhangkuan` | — | 应收账款 | 角 | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `zhuyingshouru` | — | 主营业务收入 | 角 | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `zibengongjijin` | — | 资本公积金 | 角 | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `zongguben` | — | 总股本 | 万股 | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| TDX(双命名源) | `zongzichan` | — | 总资产 | 角（→元需角(/10得元)） | 2.1 协议完整 36 字段表（权威定义）；2.6 与 Gemini 核实 18 字段的对比 |
| levistock(ftshare) | `all` | market_index_em / all | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `belong` | sector_stocks_em / belong | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `is_trade_day` | is_trade_day / get_trade_days | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `limit_up_his_kph` | limit_up_his_kph / wind_vane | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `market_emotion_kph` | market_emotion_kph | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `market_index_em` | market_index_em / all | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `rotation` | get_sector_heat / rotation | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `sector_em` | sector_em | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `sector_stocks_em` | sector_stocks_em / belong | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `stock_changes_em` | stock_changes_em | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `stock_dt_pool_em` | stock_dt_pool_em | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `stock_strategy_wencai` | stock_strategy_wencai | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `stock_yesterday_zt_em` | stock_yesterday_zt_em | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `stock_zt_pool_em` | stock_zt_pool_em | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `stocks_all_em` | stocks_em / stocks_all_em | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `stocks_em` | stocks_em / stocks_all_em | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `wind_stocks` | market_wind_cls / wind_stocks | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| levistock(ftshare) | `wind_vane` | limit_up_his_kph / wind_vane | — | — | 12.10.9 levistock 全接口字段核实（2026-08-09 复测，**38/38 全部实测**）🆕 |
| reports | `emRatingName` | emRatingName | — | — | 12.8.4 东财 reportapi（个股/行业研报 + PDF）✅；12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `industryCode` | — | — | — | 12.8.4 东财 reportapi（个股/行业研报 + PDF）✅；12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `industryName` | — | — | — | 12.8.4 东财 reportapi（个股/行业研报 + PDF）✅；12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `indvInduName` | indvInduName | — | — | 12.8.4 东财 reportapi（个股/行业研报 + PDF）✅；12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `infoCode` | infoCode | — | — | 12.8.4 东财 reportapi（个股/行业研报 + PDF）✅；12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `predictThisYearEps` | — | — | — | 12.8.4 东财 reportapi（个股/行业研报 + PDF）✅；12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| reports | `reportType` | — | — | — | 12.8.4 东财 reportapi（个股/行业研报 + PDF）✅；12.8.4.1 东财 reportapi 全量 51 字段表（V17.1.x 全量登记） |
| 东财-datacenter(英文键) | `CLOSE_PRICE` | — | — | — | 12.8.3 东财 datacenter-web（龙虎榜/两融/大宗/股东/分红/解禁）✅ |
| 东财-em_kline_f61 | `f168` | f168 | — | — | 12.3.3 日K线 `stock/kline/get`（🆕 V17.0.14 新增——CYQ 筹码分布数据入口） |
| 东财-push2(stock/get) | `f104` | — | 营业总收入 TTM | 元 | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池）；12.9.1 push2 stock/get 全字段破解（114 字段实测，项目只用 19 个） |
| 东财-push2(stock/get) | `f105` | — | 归母净利润 最新报告期 | 元 | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池）；12.9.1 push2 stock/get 全字段破解（114 字段实测，项目只用 19 个） |
| 东财-push2(stock/get) | `f119` | f119 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f120` | f120 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f137` | f137 | — | 元 | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池）；12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-push2(stock/get) | `f140` | f140 | — | 元 | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池）；12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-push2(stock/get) | `f141` | f141 | — | 元 | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池）；12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-push2(stock/get) | `f142` | f142 | — | 元 | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池）；12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-push2(stock/get) | `f143` | f143 | — | 元 | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池）；12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-push2(stock/get) | `f144` | f144 | — | 元 | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池）；12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-push2(stock/get) | `f145` | f145 | — | 元 | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池）；12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-push2(stock/get) | `f146` | f146 | — | 元 | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池）；12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-push2(stock/get) | `f147` | — | 待破解 | 元 | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**）；12.9.1 push2 stock/get 全字段破解（114 字段实测，项目只用 19 个） |
| 东财-push2(stock/get) | `f148` | — | 待破解 | 元 | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**）；12.9.1 push2 stock/get 全字段破解（114 字段实测，项目只用 19 个） |
| 东财-push2(stock/get) | `f152` | f152 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f162` | f162 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f163` | f163 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f164` | f164 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f165` | f165 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f166` | f166 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f167` | f167 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f175` | f175 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f177` | f177 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f180` | f180 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f181` | f181 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f183` | f183 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f184` | f184 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f185` | f185 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f186` | f186 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f187` | f187 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f188` | f188 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f190` | f190 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f193` | f193 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f194` | f194 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f195` | f195 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f196` | f196 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f197` | f197 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f57` | f57 | — | — | 12.3.1 单股行情 `stock/get`（已由 get_em_quote_full 验证）；12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池）；12.3.3 日K线 `stock/kline/get`（🆕 V17.0.14 新增——CYQ 筹码分布数据入口） |
| 东财-push2(stock/get) | `f58` | f58 | — | — | 12.3.1 单股行情 `stock/get`（已由 get_em_quote_full 验证）；12.3.3 日K线 `stock/kline/get`（🆕 V17.0.14 新增——CYQ 筹码分布数据入口） |
| 东财-push2(stock/get) | `f60` | f60 | — | 元 | 12.3.1 单股行情 `stock/get`（已由 get_em_quote_full 验证）；12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池）；12.3.3 日K线 `stock/kline/get`（🆕 V17.0.14 新增——CYQ 筹码分布数据入口） |
| 东财-push2(stock/get) | `f71` | f71 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f78` | f78 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-push2(stock/get) | `f92` | f92 | — | — | 12.3.1.2 push2 × ulist/tencent 全量对撞再确认（2026-09-04，修复锚池） |
| 东财-ulist239(np/get) | `f1` | f1 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f10` | f10 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f101` | f101 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f109` | f109 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f110` | f110 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f147` | f147 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f160` | f160 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f161` | f161 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f162` | f162 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f163` | f163 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f164` | f164 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f165` | f165 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f166` | f166 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f167` | f167 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f168` | f168 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f169` | f169 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f170` | f170 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f171` | f171 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f172` | f172 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f173` | f173 | — | — | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f174` | f174 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f175` | f175 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f176` | f176 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f177` | f177 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f178` | f178 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f179` | f179 | — | — | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f180` | f180 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f181` | f181 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f182` | f182 | — | — | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f183` | f183 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f185` | f185 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f186` | f186 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f187` | f187 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f188` | f188 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f189` | f189 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f19` | f19 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f191` | f191 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f192` | f192 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f193` | f193 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f195` | f195 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f196` | f196 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f197` | f197 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f199` | f199 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f201` | f201 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f202` | f202 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f203` | f203 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f211` | f211 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f212` | f212 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f221` | f221 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f225` | f225 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f226` | f226 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f228` | f228 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f229` | f229 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f230` | f230 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f232` | f232 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f233` | f233 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f234` | f234 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f24` | f24 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f25` | f25 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f26` | f26 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f29` | f29 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f31` | f31 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f32` | f32 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f33` | f33 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f34` | f34 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f35` | f35 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f36` | f36 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f37` | f37 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f38` | f38 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f39` | f39 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f40` | f40 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f41` | f41 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f42` | f42 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f43` | f43 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f44` | f44 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f47` | f47 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f48` | f48 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f50` | f50 | — | — | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f51` | f51 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f52` | f52 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f53` | f53 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f54` | f54 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f55` | f55 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f56` | f56 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f57` | f57 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f58` | f58 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f60` | f60 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f61` | f61 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f64` | f64 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f65` | f65 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f66` | f66 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f67` | f67 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f68` | f68 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f69` | f69 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f7` | f7 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f70` | f70 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f71` | f71 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f72` | f72 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f73` | f73 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f74` | f74 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f75` | f75 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f76` | f76 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f77` | f77 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f78` | f78 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f79` | f79 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f8` | f8 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f80` | f80 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f81` | f81 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f82` | f82 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f83` | f83 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f84` | f84 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f85` | f85 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f86` | f86 | — | — | 12.3.2 板块/排行 `ulist.np/get`（本次联网新发现）；12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f87` | f87 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f88` | f88 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f89` | f89 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f90` | f90 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f91` | f91 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f92` | f92 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f94` | f94 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-ulist239(np/get) | `f95` | f95 | — | — | 12.3.2.3 ulist239 全字段清单（np/get 真实返回 239 字段，V17.1.1 全量登记） |
| 东财-热榜(em_hot) | `code` | — | — | — | 12.8.12 同花顺（热点/北向/涨停揭秘/热榜/EPS）✅ |
| 东财-热榜(em_hot) | `name` | — | — | — | 12.8.12 同花顺（热点/北向/涨停揭秘/热榜/EPS）✅ |
| 东财-资金流(em_fund_flow) | `f137` | f137 | — | 元 | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f140` | f140 | — | 元 | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f141` | f141 | — | 元 | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f142` | f142 | — | 元 | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f143` | f143 | — | 元 | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f144` | f144 | — | 元 | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f145` | f145 | — | 元 | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f146` | f146 | — | 元 | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f147` | f147 | — | 元 | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 东财-资金流(em_fund_flow) | `f148` | f148 | — | 元 | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 同花顺-fuyao | `auction` | — | — | — | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `auction.auction_price` | — | 开盘价 | 元 | 12.8.12c-z 适配层快照字段契约（20260918 对撞定案）；12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `net_profit_annual` | — | 归母净利润 最新年报 | 元 | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕；12.8.12d THS 族替代 push 域能力矩阵（V17.0.7，2026-08-25 实测定案）🆕 |
| 同花顺-fuyao | `net_profit_period` | — | 归母净利润 最新报告期 | 元 | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕；12.8.12d THS 族替代 push 域能力矩阵（V17.0.7，2026-08-25 实测定案）🆕 |
| 同花顺-fuyao | `ocf_ttm` | — | 经营活动现金流量净额 TTM | 元 | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕；12.8.12d THS 族替代 push 域能力矩阵（V17.0.7，2026-08-25 实测定案）🆕 |
| 同花顺-fuyao | `snapshot` | — | — | — | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 同花顺-fuyao | `snapshot.open_price` | — | 开盘价 | 元 | 12.8.12c-z 适配层快照字段契约（20260918 对撞定案）；12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 同花顺-fuyao | `snapshot.prev_price` | — | 昨收价 | 元 | 12.8.12c-z 适配层快照字段契约（20260918 对撞定案）；12.8.12g fuyao 黄金锚 × 5 源 × 多日 对撞总表（2026-09-01）🆕 |
| 市场源(market_sources) | `cls_market_emotion` | — | — | — | — |
| 市场源(market_sources) | `kph_limit_ladder` | — | — | — | — |
| 开盘啦(kpl) | `PE` | — | — | — | — |
| 腾讯(qt.gtimg) | `[0]` | — | 市场标识（交易所） | - | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |
| 腾讯(qt.gtimg) | `[40]` | — | 待破解 | - | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |
| 腾讯(qt.gtimg) | `[56]` | — | Beta 族·高置信（非 BetaValue 原值） | - | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |
| 腾讯(qt.gtimg) | `[76]` | — | A股流通股本（= [72]） | 股 | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |
| 腾讯(qt.gtimg) | `[78]` | — | — | — | — |
| 腾讯(qt.gtimg) | `[85]` | — | 收盘参考基准价（L2 机制确认） | - | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |
