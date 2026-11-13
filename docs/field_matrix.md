# 字段×源矩阵

> 本文件由 `scripts/gen_field_matrix.py` 从字段登记表生成；请修改 registry 后重生成。

<!-- GEN:field-matrix -->

### 零·B 字段×源总表（自动生成，勿手改）

> 生成：`scripts/gen_field_matrix.py`（Phase 2 起从 field_registry.json 单一真相源读取，不再解析 field_dict.md 体积）。共 1680 个字段 / 1955 条字段×源记录（去重配对口径，取代旧版按行出现的 1412 重复计数）。

> 来源展示顺序为易→难的风险参考，不代表运行时调用优先级；TDX-0x0010/F10 与 TDX-eltdx 属同一来源族，不能按独立来源计证据。（V17.0.7 层级定案；2026-09-07 thsdk 已退役，不再列为活体源）：ZHB（离线零网络）→ TDX TCP（0x0010/F10/eltdx）→ 腾讯（不封 IP）→ **同花顺-fuyao（官方 REST，盘后可查+独立风控域，V17.0.7 升为财务 TTM 族主源）** → 新浪 → 巨潮 → 东财（限流最严）→ 其他。

> 字段名基于章节标题分类推断，精确接口见各节；正文修改后重跑本脚本即同步。

**B.1 多来源字段（186 个；表示登记了多个来源标签，不等同于独立来源，也不是运行时 fallback 表）**

| 字段 | 登记来源标签数 | 来源标签（按风险参考顺序） |
|:---|:---:|:---|
| amount | 6 | TDX-0x0010/F10、TDX-eltdx、开盘啦(kpl)、开盘红、AxData、东财 |
| change_pct | 6 | TDX-0x0010/F10、TDX-eltdx、开盘啦(kpl)、AxData、TDX-eltdx(适配层)、东财-push2ex |
| name | 5 | TDX-0x0010/F10、TDX-eltdx、FTShare REST、AxData、东财 |
| open | 5 | TDX-eltdx、FTShare REST、新浪、AxData、TDX-eltdx(适配层) |
| price | 5 | TDX-0x0010/F10、TDX-eltdx、开盘啦(kpl)、东财、东财-push2ex |
| seal_amount | 5 | TDX-eltdx、开盘啦(kpl)、开盘红、AxData、TDX-eltdx(适配层) |
| close | 4 | TDX-eltdx、FTShare REST、东财、TDX-eltdx(适配层) |
| date | 4 | TDX-0x0010/F10、TDX-eltdx、AxData、东财 |
| high | 4 | TDX-eltdx、FTShare REST、AxData、TDX-eltdx(适配层) |
| low | 4 | TDX-eltdx、FTShare REST、AxData、TDX-eltdx(适配层) |
| rank | 4 | TDX-0x0010/F10、TDX-eltdx、财联社、东财 |
| time | 4 | TDX-0x0010/F10、TDX-eltdx、东财、TDX-eltdx(适配层) |
| turnover | 4 | FTShare REST、新浪、开盘红、新浪(扩展API) |
| auction_prev_volume_ratio | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| change | 3 | TDX-eltdx、FTShare REST、AxData |
| code | 3 | TDX-0x0010/F10、TDX-eltdx、东财 |
| eps_annual(f160) | 3 | 同花顺-fuyao、东财、东财-push2(stock/get) |
| eps_raw | 3 | TDX-eltdx、TDX(双命名源)、TDX-eltdx(适配层) |
| float_market_value | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| float_shares | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| free_float_market_value | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| free_float_shares | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| ipo_date | 3 | TDX-0x0010/F10、TDX-eltdx、TDX-eltdx(适配层) |
| jing_li_run_raw_float | 3 | TDX-eltdx、TDX(双命名源)、TDX-eltdx(适配层) |
| last_price | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| limit_board_text | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| limit_down_price | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| limit_stat_days | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| limit_status | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| limit_up_count_in_stat_days | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| limit_up_price | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| limit_up_streak_days | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| liu_tong_gu_ben_raw_float | 3 | TDX-eltdx、TDX(双命名源)、TDX-eltdx(适配层) |
| locked_amount | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| min2_amount | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| ocf_ttm(f103) | 3 | 同花顺-fuyao、东财、东财-push2(stock/get) |
| open_amount | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| open_change_pct | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| open_prev_amount_ratio | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| open_prev_seal_ratio | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| open_price | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| open_turnover_z | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| open_volume_hand | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| open_volume_ratio | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| opening_rush | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| pe_ttm | 3 | TDX-eltdx、FTShare REST、TDX-eltdx(适配层) |
| prev2_seal_amount | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| prev_amount | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| prev_open_amount | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| prev_open_volume_hand | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| prev_seal_amount | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| rise_speed | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| seal_prev_ratio | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| seal_to_amount_ratio | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| seal_to_float_ratio | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| short_turnover | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| stats_date | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| turnover_rate | 3 | FTShare REST、开盘红、东财 |
| updated_date | 3 | TDX-0x0010/F10、TDX-eltdx、TDX-eltdx(适配层) |
| vol_rise_speed | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| volume | 3 | TDX-eltdx、FTShare REST、AxData |
| year_limit_up_days | 3 | TDX-eltdx、AxData、TDX-eltdx(适配层) |
| zong_gu_ben_raw_float | 3 | TDX-eltdx、TDX(双命名源)、TDX-eltdx(适配层) |
| zong_zi_chan_raw_float | 3 | TDX-eltdx、TDX(双命名源)、TDX-eltdx(适配层) |
| 行情 | 3 | TDX-0x0010/F10、同花顺-fuyao、东财 |
| fund_mid_buy | 3 | 东财-push2(stock/get)、东财-ulist239(np/get)、东财-资金流(em_fund_flow) |
| fund_mid_sell | 3 | 东财-push2(stock/get)、东财-ulist239(np/get)、东财-资金流(em_fund_flow) |
| fund_mid_today | 3 | 东财-push2(stock/get)、东财-ulist239(np/get)、东财-资金流(em_fund_flow) |
| RQJMG | 2 | akshare、东财 |
| absolute_index | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| alignment_status | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| auction_matched_volume | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| auction_unmatched_signed_volume | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| beta_60d | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| change_rate | 2 | FTShare REST、东财 |
| change_type | 2 | TDX-0x0010/F10、东财 |
| circulating_shares | 2 | TDX-eltdx、TDX(双命名源) |
| current_hand | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| down_count | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| eltdx_auction_prev_volume_ratio | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| eltdx_has_shortline | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| eltdx_ladder_level | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| eltdx_limit_board_text | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| eltdx_limit_up_streak_days | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| eltdx_open_change_pct | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| eltdx_open_prev_amount_ratio | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| eltdx_open_turnover_z | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| eltdx_open_volume_ratio | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| eltdx_seal_amount | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| eltdx_seal_to_float_ratio | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| emRatingValue | 2 | 东财、reports |
| event_kind | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| exchange | 2 | TDX-eltdx、AxData |
| fenhong | 2 | TDX-eltdx、TDX(双命名源) |
| gudongrenshu | 2 | TDX-0x0010/F10、TDX(双命名源) |
| high_price | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| inside_dish | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| is_new | 2 | 财联社、东财 |
| ladder_level | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| limit_count | 2 | TDX-0x0010/F10、开盘红 |
| limit_up_streak_count | 2 | 开盘啦(kpl)、东财-push2ex |
| limit_time | 2 | TDX-0x0010/F10、开盘红 |
| liudongfuzhai | 2 | TDX-0x0010/F10、TDX(双命名源) |
| low_price | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| main_inflow | 2 | 开盘啦(kpl)、开盘红 |
| market | 2 | TDX-0x0010/F10、东财 |
| market_cap | 2 | FTShare REST、开盘红 |
| max_seal | 2 | 开盘啦(kpl)、开盘红 |
| net_profit_annual(f109) | 2 | 同花顺-fuyao、东财 |
| net_profit_period(f105) | 2 | 同花顺-fuyao、东财 |
| net_profit_yuan | 2 | TDX-eltdx、TDX(双命名源) |
| netamount | 2 | 新浪、新浪(扩展API) |
| northbound_hold.date | 2 | 东财、东财-datacenter(英文键) |
| open_amount_yuan | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| order_count | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| outer_disc | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| peigu | 2 | TDX-eltdx、TDX(双命名源) |
| peigujia | 2 | TDX-eltdx、TDX(双命名源) |
| plate_code | 2 | TDX-0x0010/F10、财联社 |
| plate_name | 2 | TDX-0x0010/F10、财联社 |
| plates | 2 | TDX-0x0010/F10、财联社 |
| pre_close | 2 | TDX-eltdx、AxData |
| pre_close_price | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| prev_close | 2 | FTShare REST、新浪 |
| previous_trade_date | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| reason | 2 | 开盘红、东财 |
| record_hex | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| revenue_ttm(f104) | 2 | 同花顺-fuyao、东财 |
| side | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| songzhuangu | 2 | TDX-eltdx、TDX(双命名源) |
| stat.change_20k_bar | 2 | ZHB、ZHB-tdxstat |
| stat.change_60k_bar | 2 | ZHB、ZHB-tdxstat |
| stat2.high_52w | 2 | ZHB、ZHB-tdxstat2 |
| status_raw | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| symbol | 2 | FTShare REST、AxData |
| target_trade_date | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| total_assets_yuan | 2 | TDX-eltdx、TDX(双命名源) |
| total_hand | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| total_shares | 2 | TDX-eltdx、TDX(双命名源) |
| trade | 2 | 新浪、新浪(扩展API) |
| trade_date | 2 | 财联社、AxData |
| turnover_real | 2 | 开盘啦(kpl)、开盘红 |
| up_count | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| volume_hand | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| volume_lots | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| zhuyingshouru | 2 | TDX-0x0010/F10、TDX(双命名源) |
| zibengongjijin | 2 | TDX-0x0010/F10、TDX(双命名源) |
| zongzichan | 2 | TDX-0x0010/F10、TDX(双命名源) |
| 上市日期 | 2 | 东财、reports |
| 价值 | 2 | 腾讯、新浪 |
| 全市场快照 | 2 | TDX-0x0010/F10、同花顺-fuyao |
| 封单额 | 2 | 同花顺-fuyao、东财 |
| 市净率 | 2 | 同花顺-fuyao、东财 |
| 市场情绪 | 2 | TDX-0x0010/F10、同花顺-fuyao |
| 市现率 | 2 | 同花顺-fuyao、东财 |
| 市盈率(TTM) | 2 | 同花顺-fuyao、东财 |
| 市销率 | 2 | 同花顺-fuyao、东财 |
| 开盘价 | 2 | 同花顺-fuyao、东财 |
| 成交量 | 2 | 同花顺-fuyao、东财 |
| 成交额 | 2 | 同花顺-fuyao、东财 |
| 最低价 | 2 | 同花顺-fuyao、东财 |
| 最高价 | 2 | 同花顺-fuyao、东财 |
| 板块强度 | 2 | TDX-0x0010/F10、同花顺-fuyao |
| 板块轮动 | 2 | TDX-0x0010/F10、同花顺-fuyao |
| 流通市值 | 2 | 同花顺-fuyao、东财 |
| 涨停池 | 2 | TDX-0x0010/F10、同花顺-fuyao |
| 涨跌幅 | 2 | TDX-0x0010/F10、东财 |
| 涨跌额 | 2 | 同花顺-fuyao、东财 |
| 现价 | 2 | 同花顺-fuyao、东财 |
| 股东户数 | 2 | TDX-0x0010/F10、akshare |
| 行业 | 2 | TDX-0x0010/F10、东财 |
| 资金 | 2 | TDX-0x0010/F10、东财 |
| 资金流 | 2 | TDX-0x0010/F10、akshare |
| 返回 | 2 | 腾讯、新浪 |
| 连板天数 | 2 | 同花顺-fuyao、东财 |
| finance_batch[].fa_qi_ren_fa_ren_gu_raw_float | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| finance_batch[].fa_ren_gu_raw_float | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| finance_batch[].gu_dong_ren_shu_raw_float | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| finance_batch[].zhu_ying_shou_ru_raw_float | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| finance_batch[].ying_ye_li_run_raw_float | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| finance_batch[].zong_xian_jin_liu_raw_float | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| finance_batch[].zhu_ying_li_run_raw_float | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| fund_main_buy | 2 | 东财-push2(stock/get)、东财-资金流(em_fund_flow) |
| fund_main_sell | 2 | 东财-push2(stock/get)、东财-资金流(em_fund_flow) |
| fund_large_sell | 2 | 东财-push2(stock/get)、东财-资金流(em_fund_flow) |
| fund_large_today | 2 | 东财-push2(stock/get)、东财-资金流(em_fund_flow) |

**B.2 单来源关系字段（1494 个；仅登记一个来源标签）**

- **ZHB（85）**：A 实时、B 准实时、C 日频、D 静态、PE TTM、shareholder_change_date、shareholder_change_shares_wan、stat.board_count、stat.cash_reserve_wan、stat.change_10d、stat.change_10k_bar、stat.change_20d、stat.change_30d、stat.change_30k_bar、stat.change_5d、stat.change_5k_bar、stat.change_60d、stat.change_pct、stat.change_pct_1d、stat.change_pct_2d、stat.change_ytd、stat.code、stat.date、stat.dividend_yield、stat.employee_count、stat.free_ltgb、stat.market、stat.net_profit_kcf、stat.other_qy_jzc、stat.pe_dynamic、stat.pe_ttm、stat.pre_receive_zj、stat.rd_input_fee、stat.shape_value、stat.streak_days、stat.unknown_2、stat.unknown_26、stat.unseal_date、stat.zt_count、stat.zt_lianban、stat.zt_streak_cycle、stat.zt_type_code、stat2.amount、stat2.amount_1d、stat2.amount_2d、stat2.change_250k_bar、stat2.change_30k_bar、stat2.change_30k_bar_ref、stat2.change_mtd、stat2.code、stat2.date、stat2.industry_code、stat2.ipo_price、stat2.low_52w、stat2.main_net_buy_amount、stat2.main_net_buy_amount_1d、stat2.main_net_buy_hands、stat2.main_net_buy_hands_1d、stat2.market、stat2.zt_seal_amount
  - … 其余 25 个见正文
- **TDX-0x0010/F10（260）**：*ST湘邮、AI解读、BKFenShiZhiBo、ChangeStatistics、C中芯、DR 茅台、DailyLimitPerformance、DailyLimitPerformance2、GetBaseFaceListZDEvnArtNew、GetDayBaseFaceListZDEvnArt、GetDayNewHigh_W28、GetGPCPHBTS_Tag、GetHotPHB、GetInfo、GetKLineDay_W14、GetKLineZhangTing、GetMainMonitor_w30、GetPanKou、GetPlateInfo_w38、GetPlate_Info_QJ、GetStockBid、GetStockList、GetStockList（龙虎榜）、GetStockPanKou、GetStockTrendIncremental、GetWeiTuo_W14、GetYTFP_BKHX、GetYTFP_SCTD、GlobalCommon、GroupCount_w28、Index、InfoBKR、MarketStockZDNum、MoodNumCount、MorningBiddingList、NewGetList、N百花医药、Radar、RealRankingInfo、RiseFallAnalysis、ST百花医药、SharpWithdrawal、SonPlate_Info、Theme、XD、XR、ZhiShuStockList_W8、[..、[verify、all、api、axdata_verify.md)、axdata_verify.md](verify、balance_sheet` 资产负债表、belong、cash_flow` 现金流量表、changqifuzhai、client_fields_enum.md)、client_fields_enum.md](verify、color
  - … 其余 200 个见正文
- **TDX-eltdx（146）**：AuctionPoint.index、AuctionPoint.matched_volume、AuctionPoint.minute_of_day_raw、AuctionPoint.price、AuctionPoint.price_milli、AuctionPoint.record_hex、AuctionPoint.reserved_zero_0e、AuctionPoint.second_raw、AuctionPoint.time_label、AuctionPoint.time_seconds、AuctionPoint.unmatched_direction_raw、AuctionPoint.unmatched_volume、Enum `Market、FinanceInfo`（财务）、FundFlow、HistoricalFundFlow、KlineCategory、MarketStat、SecurityBar`（K 线）、SecurityInfo`（证券列表）、SecurityQuote`（五档）、XdxrRecord`（除权除息）、adjust、adjust_mode、adjust_mode_raw、auctions.series（0x056a）、business_composition、buy_levels、c1_value~c4_value、category_name、dividend_financing、eltdx_opening_rush、finance_diagnosis、full_code、get_auction_0925、highest_ladder_level、history、hot_topics、index、leader_code、leader_ladder_level、lianban_count、limit_or_count_raw、limit_up_count、market_id、minutes.aux（0x051b）、minutes.today、mode_or_selector_raw、northbound_holding、period、period_name、period_param_raw、period_raw、points、price_acc_raw、price_delta_raw、price_milli、profit_forecast、quote_snapshot.active1、quote_snapshot.amount
  - … 其余 86 个见正文
- **腾讯（12）**：[0] 市场标识、[29][54][55][77][78] 占位符、[40] 停牌标记、[56] Beta 族、[76] A股流通股本、[85] 收盘参考基准价（L2 机制确认）、[86] 收盘集合竞价净未匹配手数(带符号)（L2 机制确认）、[87] 科创板、两融标记、分钟 K线、实测、月 K线
- **FTShare REST（18）**：amplitude、avg、bid_ask_ratio、board、change_rate_day10、change_rate_day120、change_rate_day20、change_rate_day5、change_rate_day60、change_rate_ytd、float_a_shares、listing_date、shares、st、status、symbol_id、tradable_a_market_cap、ts_millis
- **同花顺-fuyao（134）**：K线、PB、ROA、`big_order_flow(ths_code)`、a-share、a-share-index、accounts_receivable、adjustment-factors、anomaly-analysis-list、anomaly-analysis-stock、auction、auction.auction_price、auction.float_market_cap、balance-sheets、calendar、cash-flow、cash-flow-statements、cash_equivalents_net_addition、catalog、constituents、corporate-actions、download-url、dragon-tiger-list、dump、eps_deduct_ttm(f108)、fflow 历史资金流窗口、financials、get 财务 TTM 族、growth、growth.calculate_operating_income_yoy_growth_ratio、growth.calculate_parent_holder_net_profit_yoy_growth_ratio、historical、holder_equity_total、hot-stock-list、hot-stock-list-history、hot-stock-rank-trend、income-statements、income_tax_expense、indicators、interest_expenses、klines(count=N)、limit-break-pool` 🆕、limit-down-pool` 🆕、limit-up-ladder、limit-up-pool、list、manage_fee、market-dumps、meta、net_profit、net_profit_annual、net_profit_period、ocf_ttm、operating_profit、operation、pay_dividends_profits_interest_cash、pb、pcf、prices、profit_total
  - … 其余 74 个见正文
- **新浪（22）**：URL、ask、ask_vol、bid、bid_vol、delta、gamma、item_tongbi、item_value、iv、last、limit_down、limit_up、open_interest、opendate、report_list.{期次}.data[].item_title、report_type、strike、theory、theta、vega、参数
- **财联社（14）**：catalyst、cur_heat、limit_up_board、market_degree、performance、profit_ratio、rank_change、shsz_balance、shsz_balance_change_px、up_down_dis、up_open_num、up_open_ratio、up_ratio、up_ratio_num
- **开盘啦(kpl)（3）**：actual_float_mv、sector_code、zt_time
- **开盘红（35）**：Detail、StockList、TagID、TagName、TagShuXing、ZSCode、ZSName、avg_change、buy_amount、dt、fall_dist、fall_num、flat、industry_id、industry_zt、limit_tag、net_inflow、net_inflow_5d、open_time、q_zrcs、qscln、rise_dist、rise_num、s_zrcs、seal_money、sell_amount、sign、sjdt、sjzt、stdt、stock_count、stzt、szln、themes、zt
- **akshare（13）**：BPS、EPS、PE 历史百分位、push2 f137、push2 f51、push2 f55、两融 RZJME、历史分红、扣非净利、板块资金流 f62、涨跌停价、股息率、龙虎榜 EXPLAIN
- **AxData（65）**：activity、amplitude_pct、ask1_price、ask1_volume、attack_pct、average_change_pct、average_price、bid1_ask1_balance_pct、bid1_ask1_volume_diff、bid1_price、bid1_volume、capital_score、concept_capital_flow_tdx（题材资金走势）、cost70_concentration、cost70_range、cost90_concentration、cost90_range、current_volume、drawdown_pct、entrust_ratio、finance_updated_date、float_share、free_float_share_z、fundamental_score、high_change_pct、industry_name、industry_rank、industry_rank_total、inside_outside_ratio、inside_volume、instrument_id、limit_ratio_pct、limit_rule、low_change_pct、market_rank、market_rank_total、market_win_pct、name_flag、news_score、open_amount_ratio_pct、option_chain_tdx（期权T型）、outside_volume、pre_close_source、pre_close_trade_date、profit_ratio_pct、score、share_source、stock_allotment_cninfo（配股）、stock_financial_diagnosis_tdx（财务诊断）、stock_forecast_consensus_tdx（盈利预测）、stock_name、stock_realtime_rank_tdx（实时榜单）、stock_share_change_cninfo（股本变动）、stock_theme_strength_rank_tdx（题材强度排行）、tdx_code、theme_score、total_share、事件流、华证、开盘红复盘 ×3（天梯
  - … 其余 5 个见正文
- **东财（477）**：ABLE_FREE_SHARES、ACCUM_AMOUNT、ASSIGN_PROGRESS、AVG_FREE_SHARES、BILLBOARD_BUY_AMT、BILLBOARD_NET_AMT、BONUS_RATIO、BUY、BUYER_NAME、BUY_RATIO、BUY_SEAT、CHANGE_RATE、CHANGE_TYPE、CLOSE_PRICE、CPFZ、D1~D30_CLOSE_ADJCHRATE、DATE、DCP、DEAL_AMOUNT_RATIO、DEAL_AMT、DEAL_NET_RATIO、DEAL_PRICE、DEAL_VOLUME、END_DATE、EXPLAIN、EXPLANATION、EX_DIVIDEND_DATE、FIN_BALANCE_GR、FREE_DATE、FREE_MARKET_CAP、FREE_RATIO、FREE_SHARES、FREE_SHARES_TYPE、HOLDER_NUM、HOLDER_NUM_CHANGE、HOLDER_NUM_RATIO、JLY、JZC、LDFZ、LINK_URL、LYZE、MARKET、NET、NET_BS_AMT、NextTwoYear、NextYear、OPERATEDEPT_CODE、OPERATEDEPT_NAME、PRETAX_BONUS_RMB、RCHANGE3D、RPTA_WEB_RZRQ_GGMX（两融）、RPT_DAILYBILLBOARD_DETAILSNEW（龙虎榜）、RPT_HOLDERNUMLATEST（股东户数）、RPT_LIFT_STAGE（解禁）、RPT_SHAREBONUS_DET（分红）、RQCHL、RQMCL、RQYE、RQYL、RZCHE
  - … 其余 417 个见正文

<!-- /GEN:field-matrix -->
