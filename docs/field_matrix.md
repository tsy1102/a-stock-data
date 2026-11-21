# 字段×源矩阵

> 本文件由 `scripts/gen_field_matrix.py` 从字段登记表生成；请修改 registry 后重生成。

<!-- GEN:field-matrix -->

### 零·B 字段×源总表（自动生成，勿手改）

> 生成：`scripts/gen_field_matrix.py`（Phase 2 起从 field_registry.json 单一真相源读取，不再解析 field_dict.md 体积）。共 1794 个字段 / 2003 条字段×源记录（去重配对口径，取代旧版按行出现的 1412 重复计数）。

> 来源展示顺序为易→难的风险参考，不代表运行时调用优先级；TDX-0x0010/F10 与 TDX-eltdx 属同一来源族，不能按独立来源计证据。（V17.0.7 层级定案；2026-09-07 thsdk 已退役，不再列为活体源）：ZHB（离线零网络）→ TDX TCP（0x0010/F10/eltdx）→ 腾讯（不封 IP）→ **同花顺-fuyao（官方 REST，盘后可查+独立风控域，V17.0.7 升为财务 TTM 族主源）** → 新浪 → 巨潮 → 东财（限流最严）→ 其他。

> 字段名基于章节标题分类推断，精确接口见各节；正文修改后重跑本脚本即同步。

**B.1 多来源字段（168 个；表示登记了多个来源标签，不等同于独立来源，也不是运行时 fallback 表）**

| 字段 | 登记来源标签数 | 来源标签（按风险参考顺序） |
|:---|:---:|:---|
| amount | 6 | TDX-0x0010/F10、TDX-eltdx、开盘啦(kpl)、开盘红、AxData、东财 |
| change_pct | 5 | TDX-0x0010/F10、TDX-eltdx、开盘啦(kpl)、AxData、东财-push2ex |
| name | 5 | TDX-0x0010/F10、TDX-eltdx、FTShare REST、AxData、东财 |
| price | 5 | TDX-0x0010/F10、TDX-eltdx、开盘啦(kpl)、东财、东财-push2ex |
| date | 4 | TDX-0x0010/F10、TDX-eltdx、AxData、东财 |
| limit_time | 4 | TDX-0x0010/F10、开盘红、市场源(market_sources)、开盘红(Levistock适配) |
| open | 4 | TDX-eltdx、FTShare REST、新浪、AxData |
| rank | 4 | TDX-0x0010/F10、TDX-eltdx、财联社、东财 |
| seal_amount | 4 | TDX-eltdx、开盘啦(kpl)、开盘红、AxData |
| turnover | 4 | FTShare REST、新浪、开盘红、新浪(扩展API) |
| change | 3 | TDX-eltdx、FTShare REST、AxData |
| change_type | 3 | TDX-0x0010/F10、东财、市场源(market_sources) |
| close | 3 | TDX-eltdx、FTShare REST、东财 |
| code | 3 | TDX-0x0010/F10、TDX-eltdx、东财 |
| eps_annual(f160) | 3 | 同花顺-fuyao、东财、东财-push2(stock/get) |
| fund_mid_buy | 3 | 东财-push2(stock/get)、东财-ulist239(np/get)、东财-资金流(em_fund_flow) |
| fund_mid_sell | 3 | 东财-push2(stock/get)、东财-ulist239(np/get)、东财-资金流(em_fund_flow) |
| fund_mid_today | 3 | 东财-push2(stock/get)、东财-ulist239(np/get)、东财-资金流(em_fund_flow) |
| high | 3 | TDX-eltdx、FTShare REST、AxData |
| low | 3 | TDX-eltdx、FTShare REST、AxData |
| ocf_ttm(f103) | 3 | 同花顺-fuyao、东财、东财-push2(stock/get) |
| rise_speed | 3 | TDX-eltdx、AxData、TDX(双命名源) |
| time | 3 | TDX-0x0010/F10、TDX-eltdx、东财 |
| turnover_rate | 3 | FTShare REST、开盘红、东财 |
| volume | 3 | TDX-eltdx、FTShare REST、AxData |
| 行情 | 3 | TDX-0x0010/F10、同花顺-fuyao、东财 |
| RQJMG | 2 | akshare、东财 |
| [14] | 2 | ZHB-tipinfo、新浪(hq.sinajs) |
| [22] | 2 | 新浪(hq.sinajs)、腾讯(qt.gtimg) |
| [24] | 2 | 新浪(hq.sinajs)、腾讯(qt.gtimg) |
| [26] | 2 | 新浪(hq.sinajs)、腾讯(qt.gtimg) |
| [28] | 2 | 新浪(hq.sinajs)、腾讯(qt.gtimg) |
| amplitude | 2 | FTShare REST、开盘啦(kpl_limit_up_detail) |
| auction_prev_volume_ratio | 2 | TDX-eltdx、AxData |
| category_name | 2 | TDX-eltdx、TDX(双命名源) |
| change_rate | 2 | FTShare REST、东财 |
| circulating_shares | 2 | TDX-eltdx、TDX(双命名源) |
| emRatingValue | 2 | 东财、reports |
| eps_raw | 2 | TDX-eltdx、TDX(双命名源) |
| exchange | 2 | TDX-eltdx、AxData |
| fenhong | 2 | TDX-eltdx、TDX(双命名源) |
| finance_batch[].gu_dong_ren_shu_raw_float | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| finance_batch[].ying_ye_li_run_raw_float | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| finance_batch[].zhu_ying_shou_ru_raw_float | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| finance_batch[].zong_xian_jin_liu_raw_float | 2 | TDX-eltdx、TDX-eltdx(适配层) |
| float_market_value | 2 | TDX-eltdx、AxData |
| float_shares | 2 | TDX-eltdx、AxData |
| free_float_market_value | 2 | TDX-eltdx、AxData |
| free_float_shares | 2 | TDX-eltdx、AxData |
| fund_large_sell | 2 | 东财-push2(stock/get)、东财-资金流(em_fund_flow) |
| fund_large_today | 2 | 东财-push2(stock/get)、东财-资金流(em_fund_flow) |
| fund_main_buy | 2 | 东财-push2(stock/get)、东财-资金流(em_fund_flow) |
| fund_main_sell | 2 | 东财-push2(stock/get)、东财-资金流(em_fund_flow) |
| gudongrenshu | 2 | TDX-0x0010/F10、TDX(双命名源) |
| industry_id | 2 | 开盘红、开盘红(Levistock适配) |
| ipo_date | 2 | TDX-0x0010/F10、TDX-eltdx |
| is_new | 2 | 财联社、东财 |
| item_tongbi | 2 | 新浪、新浪(扩展API) |
| item_value | 2 | 新浪、新浪(扩展API) |
| jing_li_run_raw_float | 2 | TDX-eltdx、TDX(双命名源) |
| last_price | 2 | TDX-eltdx、AxData |
| limit_board_text | 2 | TDX-eltdx、AxData |
| limit_count | 2 | TDX-0x0010/F10、开盘红 |
| limit_down_price | 2 | TDX-eltdx、AxData |
| limit_stat_days | 2 | TDX-eltdx、AxData |
| limit_status | 2 | TDX-eltdx、AxData |
| limit_up_count_in_stat_days | 2 | TDX-eltdx、AxData |
| limit_up_price | 2 | TDX-eltdx、AxData |
| limit_up_streak_count | 2 | 开盘啦(kpl)、东财-push2ex |
| limit_up_streak_days | 2 | TDX-eltdx、AxData |
| liu_tong_gu_ben_raw_float | 2 | TDX-eltdx、TDX(双命名源) |
| liudongfuzhai | 2 | TDX-0x0010/F10、TDX(双命名源) |
| locked_amount | 2 | TDX-eltdx、AxData |
| main_inflow | 2 | 开盘啦(kpl)、开盘红 |
| market | 2 | TDX-0x0010/F10、东财 |
| market_cap | 2 | FTShare REST、开盘红 |
| max_seal | 2 | 开盘啦(kpl)、开盘红 |
| min2_amount | 2 | TDX-eltdx、AxData |
| net_profit_annual(f109) | 2 | 同花顺-fuyao、东财 |
| net_profit_period(f105) | 2 | 同花顺-fuyao、东财 |
| net_profit_yuan | 2 | TDX-eltdx、TDX(双命名源) |
| netamount | 2 | 新浪、新浪(扩展API) |
| northbound_hold.change_ratio | 2 | 东财、东财-datacenter(英文键) |
| northbound_hold.date | 2 | 东财、东财-datacenter(英文键) |
| northbound_hold.hold_ratio | 2 | 东财、东财-datacenter(英文键) |
| northbound_hold.hold_shares | 2 | 东财、东财-datacenter(英文键) |
| northbound_hold.market_cap | 2 | 东财、东财-datacenter(英文键) |
| open_amount | 2 | TDX-eltdx、AxData |
| open_change_pct | 2 | TDX-eltdx、AxData |
| open_prev_amount_ratio | 2 | TDX-eltdx、AxData |
| open_prev_seal_ratio | 2 | TDX-eltdx、AxData |
| open_price | 2 | TDX-eltdx、AxData |
| open_turnover_z | 2 | TDX-eltdx、AxData |
| open_volume_hand | 2 | TDX-eltdx、AxData |
| open_volume_ratio | 2 | TDX-eltdx、AxData |
| opendate | 2 | 新浪、新浪(扩展API) |
| opening_rush | 2 | TDX-eltdx、AxData |
| pe_ttm | 2 | TDX-eltdx、FTShare REST |
| peigu | 2 | TDX-eltdx、TDX(双命名源) |
| peigujia | 2 | TDX-eltdx、TDX(双命名源) |
| plate_code | 2 | TDX-0x0010/F10、财联社 |
| plate_name | 2 | TDX-0x0010/F10、财联社 |
| plates | 2 | TDX-0x0010/F10、财联社 |
| pre_close | 2 | TDX-eltdx、AxData |
| predictNextTwoYearPe | 2 | 东财、reports |
| predictNextYearPe | 2 | 东财、reports |
| predictThisYearPe | 2 | 东财、reports |
| prev2_seal_amount | 2 | TDX-eltdx、AxData |
| prev_amount | 2 | TDX-eltdx、AxData |
| prev_close | 2 | FTShare REST、新浪 |
| prev_open_amount | 2 | TDX-eltdx、AxData |
| prev_open_volume_hand | 2 | TDX-eltdx、AxData |
| prev_seal_amount | 2 | TDX-eltdx、AxData |
| quote_price_precision_digits | 2 | 东财-push2(stock/get)、东财-ulist239(np/get) |
| reading_num | 2 | 东财、财联社(cls) |
| reason | 2 | 开盘红、东财 |
| revenue_ttm(f104) | 2 | 同花顺-fuyao、东财 |
| seal_prev_ratio | 2 | TDX-eltdx、AxData |
| seal_to_amount_ratio | 2 | TDX-eltdx、AxData |
| seal_to_float_ratio | 2 | TDX-eltdx、AxData |
| short_turnover | 2 | TDX-eltdx、AxData |
| songzhuangu | 2 | TDX-eltdx、TDX(双命名源) |
| stat.change_20k_bar | 2 | ZHB、ZHB-tdxstat |
| stat.change_60k_bar | 2 | ZHB、ZHB-tdxstat |
| stat2.high_52w | 2 | ZHB、ZHB-tdxstat2 |
| stats_date | 2 | TDX-eltdx、AxData |
| symbol | 2 | FTShare REST、AxData |
| total_assets_yuan | 2 | TDX-eltdx、TDX(双命名源) |
| total_shares | 2 | TDX-eltdx、TDX(双命名源) |
| trade | 2 | 新浪、新浪(扩展API) |
| trade_date | 2 | 财联社、AxData |
| turnover_real | 2 | 开盘啦(kpl)、开盘红 |
| updated_date | 2 | TDX-0x0010/F10、TDX-eltdx |
| vol_rise_speed | 2 | TDX-eltdx、AxData |
| year_limit_up_days | 2 | TDX-eltdx、AxData |
| zhuyingshouru | 2 | TDX-0x0010/F10、TDX(双命名源) |
| zibengongjijin | 2 | TDX-0x0010/F10、TDX(双命名源) |
| zong_gu_ben_raw_float | 2 | TDX-eltdx、TDX(双命名源) |
| zong_zi_chan_raw_float | 2 | TDX-eltdx、TDX(双命名源) |
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
| kph_industry_limit_up_count | 2 | 开盘红、开盘红(Levistock适配) |

**B.2 单来源关系字段（1626 个；仅登记一个来源标签）**

- **ZHB（85）**：A 实时、B 准实时、C 日频、D 静态、PE TTM、shareholder_change_date、shareholder_change_shares_wan、stat.board_count、stat.cash_reserve_wan、stat.change_10d、stat.change_10k_bar、stat.change_20d、stat.change_30d、stat.change_30k_bar、stat.change_5d、stat.change_5k_bar、stat.change_60d、stat.change_pct、stat.change_pct_1d、stat.change_pct_2d、stat.change_ytd、stat.code、stat.date、stat.dividend_yield、stat.employee_count、stat.free_ltgb、stat.market、stat.net_profit_kcf、stat.other_qy_jzc、stat.pe_dynamic、stat.pe_ttm、stat.pre_receive_zj、stat.rd_input_fee、stat.shape_value、stat.streak_days、stat.unknown_2、stat.unknown_26、stat.unseal_date、stat.zt_count、stat.zt_lianban、stat.zt_streak_cycle、stat.zt_type_code、stat2.amount、stat2.amount_1d、stat2.amount_2d、stat2.change_250k_bar、stat2.change_30k_bar、stat2.change_30k_bar_ref、stat2.change_mtd、stat2.code、stat2.date、stat2.industry_code、stat2.ipo_price、stat2.low_52w、stat2.main_net_buy_amount、stat2.main_net_buy_amount_1d、stat2.main_net_buy_hands、stat2.main_net_buy_hands_1d、stat2.market、stat2.zt_seal_amount
  - … 其余 25 个见正文
- **TDX-0x0010/F10（259）**：*ST湘邮、AI解读、BKFenShiZhiBo、ChangeStatistics、C中芯、DR 茅台、DailyLimitPerformance、DailyLimitPerformance2、GetBaseFaceListZDEvnArtNew、GetDayBaseFaceListZDEvnArt、GetDayNewHigh_W28、GetGPCPHBTS_Tag、GetHotPHB、GetInfo、GetKLineDay_W14、GetKLineZhangTing、GetMainMonitor_w30、GetPanKou、GetPlateInfo_w38、GetPlate_Info_QJ、GetStockBid、GetStockList、GetStockList（龙虎榜）、GetStockPanKou、GetStockTrendIncremental、GetWeiTuo_W14、GetYTFP_BKHX、GetYTFP_SCTD、GlobalCommon、GroupCount_w28、Index、InfoBKR、MarketStockZDNum、MoodNumCount、MorningBiddingList、NewGetList、N百花医药、Radar、RealRankingInfo、RiseFallAnalysis、ST百花医药、SharpWithdrawal、SonPlate_Info、Theme、XD、XR、ZhiShuStockList_W8、[..、[verify、all、api、axdata_verify.md)、axdata_verify.md](verify、balance_sheet` 资产负债表、belong、cash_flow` 现金流量表、changqifuzhai、client_fields_enum.md)、client_fields_enum.md](verify、color
  - … 其余 199 个见正文
- **TDX-eltdx（184）**：AuctionPoint.index、AuctionPoint.matched_volume、AuctionPoint.minute_of_day_raw、AuctionPoint.price、AuctionPoint.price_milli、AuctionPoint.record_hex、AuctionPoint.reserved_zero_0e、AuctionPoint.second_raw、AuctionPoint.time_label、AuctionPoint.time_seconds、AuctionPoint.unmatched_direction_raw、AuctionPoint.unmatched_volume、Enum `Market、FinanceInfo`（财务）、FundFlow、HistoricalFundFlow、KlineCategory、MarketStat、SecurityBar`（K 线）、SecurityInfo`（证券列表）、SecurityQuote`（五档）、XdxrRecord`（除权除息）、absolute_index、adjust、adjust_mode、adjust_mode_raw、alignment_status、auction_matched_volume、auction_unmatched_signed_volume、auctions.series（0x056a）、beta_60d、business_composition、buy_levels、c1_value~c4_value、current_hand、dividend_financing、down_count、eltdx_auction_prev_volume_ratio、eltdx_has_shortline、eltdx_ladder_level、eltdx_limit_board_text、eltdx_limit_up_streak_days、eltdx_open_change_pct、eltdx_open_prev_amount_ratio、eltdx_open_turnover_z、eltdx_open_volume_ratio、eltdx_opening_rush、eltdx_seal_amount、eltdx_seal_to_float_ratio、event_kind、finance_batch[].fa_qi_ren_fa_ren_gu_raw_float、finance_batch[].fa_ren_gu_raw_float、finance_batch[].zhu_ying_li_run_raw_float、finance_diagnosis、full_code、get_auction_0925、high_price、highest_ladder_level、history、hot_topics
  - … 其余 124 个见正文
- **腾讯（14）**：[0] 市场标识、[29][54][55][77][78] 占位符、[40] 停牌标记、[56] Beta 族、[76] A股流通股本、[7]、[85] 收盘参考基准价（L2 机制确认）、[86] 竞价失衡方向信号、[87] 科创板标记、[87] 科创板相关标记、[8]、分钟 K线、实测、月 K线
- **FTShare REST（17）**：avg、bid_ask_ratio、board、change_rate_day10、change_rate_day120、change_rate_day20、change_rate_day5、change_rate_day60、change_rate_ytd、float_a_shares、listing_date、shares、st、status、symbol_id、tradable_a_market_cap、ts_millis
- **同花顺-fuyao（155）**：K线、PB、ROA、`big_order_flow(ths_code)`、a-share、a-share-index、a-share/financials/indicators、accounts_receivable、adjustment-factors、anomaly-analysis-list、anomaly-analysis-stock、auction、auction.auction_price、auction.float_market_cap、auction_final.auction_pct、auction_final.auction_price、auction_final.open_price、balance-sheets、calendar、cash-flow、cash-flow-statements、cash-flow.cash_meet_invest_ratio、cash-flow.cash_operating_index、cash-flow.net_profit_cash_content、cash-flow.operating_cash_flow_net_divide_income、cash_equivalents_net_addition、catalog、constituents、corporate-actions、download-url、dragon-tiger-list、dump、fflow 历史资金流窗口、financials、get 财务 TTM 族、growth、growth.calculate_operating_income_yoy_growth_ratio、growth.calculate_operating_profit_yoy_growth_ratio、growth.calculate_parent_holder_net_profit_yoy_growth_ratio、growth.fixed_asset_invest_expansion_ratio、growth.total_assets_growth_ratio、historical、holder_equity_total、hot-stock-list、hot-stock-list-history、hot-stock-rank-trend、income-statements、income_tax_expense、indicators、interest_expenses、klines(count=N)、limit-break-pool` 🆕、limit-down-pool` 🆕、limit-up-ladder、limit-up-pool、list、manage_fee、market-dumps、meta、net_profit
  - … 其余 95 个见正文
- **新浪（19）**：URL、ask、ask_vol、bid、bid_vol、delta、gamma、iv、last、limit_down、limit_up、open_interest、report_list.{期次}.data[].item_title、report_type、strike、theory、theta、vega、参数
- **财联社（14）**：catalyst、cur_heat、limit_up_board、market_degree、performance、profit_ratio、rank_change、shsz_balance、shsz_balance_change_px、up_down_dis、up_open_num、up_open_ratio、up_ratio、up_ratio_num
- **开盘啦(kpl)（3）**：actual_float_mv、sector_code、zt_time
- **开盘红（34）**：Detail、StockList、TagID、TagName、TagShuXing、ZSCode、ZSName、avg_change、buy_amount、dt、fall_dist、fall_num、flat、industry_zt、limit_tag、net_inflow、net_inflow_5d、open_time、q_zrcs、qscln、rise_dist、rise_num、s_zrcs、seal_money、sell_amount、sign、sjdt、sjzt、stdt、stock_count、stzt、szln、themes、zt
- **akshare（13）**：BPS、EPS、PE 历史百分位、push2 f137、push2 f51、push2 f55、两融 RZJME、历史分红、扣非净利、板块资金流 f62、涨跌停价、股息率、龙虎榜 EXPLAIN
- **沪深交易所（5）**：sse_etf_scale_statistics_date、sse_etf_total_shares_10k、szse_etf_current_scale_measurement_date、szse_etf_current_scale_shares_10k、szse_etf_listing_date
- **AxData（65）**：activity、amplitude_pct、ask1_price、ask1_volume、attack_pct、average_change_pct、average_price、bid1_ask1_balance_pct、bid1_ask1_volume_diff、bid1_price、bid1_volume、capital_score、concept_capital_flow_tdx（题材资金走势）、cost70_concentration、cost70_range、cost90_concentration、cost90_range、current_volume、drawdown_pct、entrust_ratio、finance_updated_date、float_share、free_float_share_z、fundamental_score、high_change_pct、industry_name、industry_rank、industry_rank_total、inside_outside_ratio、inside_volume、instrument_id、limit_ratio_pct、limit_rule、low_change_pct、market_rank、market_rank_total、market_win_pct、name_flag、news_score、open_amount_ratio_pct、option_chain_tdx（期权T型）、outside_volume、pre_close_source、pre_close_trade_date、profit_ratio_pct、score、share_source、stock_allotment_cninfo（配股）、stock_financial_diagnosis_tdx（财务诊断）、stock_forecast_consensus_tdx（盈利预测）、stock_name、stock_realtime_rank_tdx（实时榜单）、stock_share_change_cninfo（股本变动）、stock_theme_strength_rank_tdx（题材强度排行）、tdx_code、theme_score、total_share、事件流、华证、开盘红复盘 ×3（天梯
  - … 其余 5 个见正文
- **东财（470）**：ABLE_FREE_SHARES、ACCUM_AMOUNT、ASSIGN_PROGRESS、AVG_FREE_SHARES、BILLBOARD_BUY_AMT、BILLBOARD_NET_AMT、BONUS_RATIO、BUY、BUYER_NAME、BUY_RATIO、BUY_SEAT、CHANGE_RATE、CHANGE_TYPE、CLOSE_PRICE、CPFZ、D1~D30_CLOSE_ADJCHRATE、DATE、DCP、DEAL_AMOUNT_RATIO、DEAL_AMT、DEAL_NET_RATIO、DEAL_PRICE、DEAL_VOLUME、END_DATE、EXPLAIN、EXPLANATION、EX_DIVIDEND_DATE、FIN_BALANCE_GR、FREE_DATE、FREE_MARKET_CAP、FREE_RATIO、FREE_SHARES、FREE_SHARES_TYPE、HOLDER_NUM、HOLDER_NUM_CHANGE、HOLDER_NUM_RATIO、JLY、JZC、LDFZ、LINK_URL、LYZE、MARKET、NET、NET_BS_AMT、NextTwoYear、NextYear、OPERATEDEPT_CODE、OPERATEDEPT_NAME、PRETAX_BONUS_RMB、RCHANGE3D、RPTA_WEB_RZRQ_GGMX（两融）、RPT_DAILYBILLBOARD_DETAILSNEW（龙虎榜）、RPT_HOLDERNUMLATEST（股东户数）、RPT_LIFT_STAGE（解禁）、RPT_SHAREBONUS_DET（分红）、RQCHL、RQMCL、RQYE、RQYL、RZCHE
  - … 其余 410 个见正文
- **TDX(双命名源)（138）**：Amount、Average、BCancel、Before5MinNow、BetaValue、CJJEPre1、CJJEPre3、CashZJ、ConZAFDateNum、DTDate_Recent、DTPrice、DYRatio、DownHome、DynaPE、EverZTCount、FCAmo、FCb、FDEPre1、FDEPre2、FreeLtgb、FzAmo、Fzhsl、HisHigh、HisLow、HqDate、IPO_Price、InOutFlag、Inside、IsKzz、IsT0Fund、IsZCZGP、ItemNum、Jjjz、KfEarnMoney、Kzz_HSCode、L2OrderNum、L2TicNum、LastClose、LastStartZT、LastZTHzNum、Ltgb、Ltsz、MA5Value、MainBusiness、Max、Min、MorePE、More_YJL、NoticeDate_Recent、Now、NowVol、Open、OpenAmo、OpenAmoPre1、OpenVolPre1、OpenZAF、OpenZTBuy、OtherQYJzc、Outside、PB_MRQ
  - … 其余 78 个见正文
- **TDX-eltdx(适配层)（22）**：limit_ladder.auction_prev_volume_ratio、limit_ladder.beta_60d、limit_ladder.ladder_level、limit_ladder.limit_board_text、limit_ladder.limit_stat_days、limit_ladder.limit_up_count_in_stat_days、limit_ladder.open_amount、limit_ladder.open_change_pct、limit_ladder.open_prev_amount_ratio、limit_ladder.open_price、limit_ladder.open_turnover_z、limit_ladder.open_volume_hand、limit_ladder.open_volume_ratio、limit_ladder.pe_ttm、limit_ladder.pre_close、limit_ladder.prev2_seal_amount、limit_ladder.prev_amount、limit_ladder.prev_open_amount、limit_ladder.prev_open_volume_hand、limit_ladder.seal_to_amount_ratio、limit_ladder.seal_to_float_ratio、limit_ladder.year_limit_up_days
- **ZHB-tdxstat（2）**：change_ytd、pe_lyr
- **ZHB-tipinfo（5）**：[13]、equity_incentive_date、forecast_date_recent、forecast_type、suspend_major_event_date
- **reports（10）**：column、indvIsNew、上一年度实际每股收益、研报 PDF 附件大小、研报 PDF 附件页数、研报目标价区间上限、研报目标价区间下限、研报附件类型代码、首次公开发行价格、首次公开发行市盈率
- **东财-em_kline_f61（2）**：daily_kline_record_count、f59
- **东财-event_dc(IPO发行记录)（33）**：ipo_ballot_number_announcement_date、ipo_consecutive_one_word_board_count、ipo_first_day_average_price_yuan、ipo_first_day_close_change_pct、ipo_first_day_high_change_pct、ipo_first_day_open_premium_pct、ipo_first_day_open_price_yuan、ipo_first_day_turnover_rate_pct、ipo_issue_price_per_share、ipo_issue_way_explanation、ipo_offline_initial_inquiry_cumulative_multiple、ipo_offline_placement_quote_object_count、ipo_online_issue_shares、ipo_online_subscription_upper_shares、ipo_online_winning_rate_pct、ipo_open_board_average_price_yuan、ipo_open_board_date、ipo_prospectus_document_code、ipo_record_after_issue_pe、ipo_record_first_day_close_price、ipo_record_industry_pe、ipo_record_latest_price、ipo_record_listing_date、ipo_record_main_business_description、ipo_record_par_value、ipo_record_per_sign_profit_yuan、ipo_record_subscription_date、ipo_record_total_gain_pct、ipo_registration_system_flag、ipo_subscription_payment_date、ipo_top_subscription_market_value_wan_yuan、ipo_total_change_reference_average_price_yuan、ipo_total_issue_shares_wan
- **东财-event_dc(可转债列表)（24）**：bond_coupon_rate_current_interest_year_pct、convertible_bond_conversion_premium_ratio、convertible_bond_conversion_value、convertible_bond_credit_rating、convertible_bond_current_conversion_price、convertible_bond_current_market_price、convertible_bond_equity_registration_date、convertible_bond_initial_conversion_price、convertible_bond_issue_scale、convertible_bond_lottery_number_publication_date、convertible_bond_online_lottery_win_rate_pct、convertible_bond_online_subscription_limit_thousand_yuan、convertible_bond_priority_placement_amount_yuan_per_share、convertible_bond_profit_per_lot_yuan、convertible_bond_put_application_end_date、convertible_bond_put_application_start_date、convertible_bond_put_execution_price_yuan_per_bond、convertible_bond_redemption_execution_date、convertible_bond_redemption_execution_price_yuan_per_bond、convertible_bond_redemption_trigger_price、convertible_bond_resale_trigger_price、convertible_bond_term_years、convertible_bond_underlying_stock_pb_ratio、convertible_bond_underlying_stock_price
- **东财-push2(stock/get)（9）**：eastmoney_stock_get_dividend_yield、eastmoney_stock_get_inner_volume、eastmoney_stock_get_outer_volume、eps_ttm(f108)、f163、f176、f190、f55、f92
- **东财-push2ex（3）**：push2ex.total_market_value、push2ex.tradable_a_market_value、sector
- **东财-ulist239(np/get)（24）**：3分钟涨速、5分钟涨跌幅、H股关联A股价格缩放位数、change_3d、current_trade_hand_count、dividend_yield_lfy_observed、f88_positive_days_10d、f88_positive_days_5d、f88_positive_streak_days、h_share_code、h_share_market_code、h_share_name、listing_board_type、order_imbalance_ratio、parent_equity_to_total_assets_ratio、registration_system_listing_bitmask、report_period_end_date、security_eligibility_bitmask、ulist239_change_6_intervals_pct、ulist239_parent_net_profit_yoy_growth_pct、ulist239_quote_data_date、ulist239_sales_gross_margin_report_period_pct、ulist239_total_equity_consolidated、行情百分比/比例缩放位数
- **东财-资金流(em_fund_flow)（8）**：fund_large_buy、fund_main_today、fund_small_buy、fund_small_sell、fund_small_today、fund_super_buy、fund_super_sell、fund_super_today
- **央视网(新闻联播)（1）**：cctv_news_broadcast_edition_date
- **开盘啦(kpl_limit_up_detail)（4）**：has_intraday_limit_up_break、kpl_category_limit_up_stock_count、main_buy、main_sell
- **新浪(hq.sinajs)（2）**：[16]、[18]
- **新浪(研报列表)（1）**：sina_research_report_publication_date
- **财联社(cls)（1）**：cls_telegraph_publish_time

<!-- /GEN:field-matrix -->
