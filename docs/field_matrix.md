# 字段×源矩阵

> 本文件由 `scripts/gen_field_matrix.py` 从字段登记表生成；请修改 registry 后重生成。

<!-- GEN:field-matrix -->

### 零·B 字段×源总表（自动生成，勿手改）

> 生成：`scripts/gen_field_matrix.py`（Phase 2 起从 field_registry.json 单一真相源读取，不再解析 field_dict.md 体积）。共 1434 个字段 / 1550 条字段×源记录（去重配对口径，取代旧版按行出现的 1412 重复计数）。

> 源排序按易→难（V17.0.7 层级定案；2026-09-07 thsdk 已退役，不再列为活体源）：ZHB（离线零网络）→ TDX TCP（0x0010/F10/eltdx）→ 腾讯（不封 IP）→ **同花顺-fuyao（官方 REST，盘后可查+独立风控域，V17.0.7 升为财务 TTM 族主源）** → 新浪 → 巨潮 → 东财（限流最严）→ 其他。

> 字段名基于章节标题分类推断，精确接口见各节；正文修改后重跑本脚本即同步。

**B.1 多源字段（101 个，fallback 路由表）**

| 字段 | 源数 | 源（按易→难） |
|:---|:---:|:---|
| amount | 4 | TDX-0x0010/F10、TDX-eltdx、AxData、东财 |
| date | 4 | TDX-0x0010/F10、TDX-eltdx、AxData、东财 |
| name | 4 | TDX-0x0010/F10、TDX-eltdx、AxData、东财 |
| rank | 4 | TDX-0x0010/F10、TDX-eltdx、财联社、东财 |
| 行情 | 3 | TDX-0x0010/F10、同花顺-fuyao、东财 |
| code | 3 | TDX-0x0010/F10、TDX-eltdx、东财 |
| time | 3 | TDX-0x0010/F10、TDX-eltdx、东财 |
| price | 3 | TDX-0x0010/F10、TDX-eltdx、东财 |
| open | 3 | TDX-eltdx、新浪、AxData |
| seal_amount | 3 | TDX-eltdx、开盘红、AxData |
| change_pct | 3 | TDX-0x0010/F10、TDX-eltdx、AxData |
| 股东户数 | 2 | TDX-0x0010/F10、akshare |
| ipo_date | 2 | TDX-0x0010/F10、TDX-eltdx |
| updated_date | 2 | TDX-0x0010/F10、TDX-eltdx |
| 返回 | 2 | 腾讯、新浪 |
| 价值 | 2 | 腾讯、新浪 |
| 资金 | 2 | TDX-0x0010/F10、东财 |
| reason | 2 | 开盘红、东财 |
| close | 2 | TDX-eltdx、东财 |
| market | 2 | TDX-0x0010/F10、东财 |
| turnover_rate | 2 | 开盘红、东财 |
| is_new | 2 | 财联社、东财 |
| ocf_ttm(f103) | 2 | 同花顺-fuyao、东财 |
| revenue_ttm(f104) | 2 | 同花顺-fuyao、东财 |
| net_profit_period(f105) | 2 | 同花顺-fuyao、东财 |
| net_profit_annual(f109) | 2 | 同花顺-fuyao、东财 |
| eps_annual(f160) | 2 | 同花顺-fuyao、东财 |
| 行业 | 2 | TDX-0x0010/F10、东财 |
| 现价 | 2 | 同花顺-fuyao、东财 |
| 开盘价 | 2 | 同花顺-fuyao、东财 |
| 最高价 | 2 | 同花顺-fuyao、东财 |
| 最低价 | 2 | 同花顺-fuyao、东财 |
| 涨跌幅 | 2 | TDX-0x0010/F10、东财 |
| 涨跌额 | 2 | 同花顺-fuyao、东财 |
| 成交量 | 2 | 同花顺-fuyao、东财 |
| 成交额 | 2 | 同花顺-fuyao、东财 |
| 流通市值 | 2 | 同花顺-fuyao、东财 |
| 市净率 | 2 | 同花顺-fuyao、东财 |
| 市销率 | 2 | 同花顺-fuyao、东财 |
| 市现率 | 2 | 同花顺-fuyao、东财 |
| 封单额 | 2 | 同花顺-fuyao、东财 |
| 连板天数 | 2 | 同花顺-fuyao、东财 |
| 涨停池 | 2 | TDX-0x0010/F10、同花顺-fuyao |
| 市盈率(TTM) | 2 | 同花顺-fuyao、东财 |
| turnover | 2 | 新浪、开盘红 |
| RQJMG | 2 | akshare、东财 |
| change_type | 2 | TDX-0x0010/F10、东财 |
| limit_count | 2 | TDX-0x0010/F10、开盘红 |
| limit_time | 2 | TDX-0x0010/F10、开盘红 |
| plate_code | 2 | TDX-0x0010/F10、财联社 |
| plate_name | 2 | TDX-0x0010/F10、财联社 |
| trade_date | 2 | 财联社、AxData |
| plates | 2 | TDX-0x0010/F10、财联社 |
| 资金流 | 2 | TDX-0x0010/F10、akshare |
| exchange | 2 | TDX-eltdx、AxData |
| stats_date | 2 | TDX-eltdx、AxData |
| open_price | 2 | TDX-eltdx、AxData |
| pre_close | 2 | TDX-eltdx、AxData |
| open_change_pct | 2 | TDX-eltdx、AxData |
| open_amount | 2 | TDX-eltdx、AxData |
| open_volume_hand | 2 | TDX-eltdx、AxData |
| open_volume_ratio | 2 | TDX-eltdx、AxData |
| open_turnover_z | 2 | TDX-eltdx、AxData |
| open_prev_amount_ratio | 2 | TDX-eltdx、AxData |
| auction_prev_volume_ratio | 2 | TDX-eltdx、AxData |
| opening_rush | 2 | TDX-eltdx、AxData |
| open_prev_seal_ratio | 2 | TDX-eltdx、AxData |
| prev_amount | 2 | TDX-eltdx、AxData |
| prev_seal_amount | 2 | TDX-eltdx、AxData |
| prev2_seal_amount | 2 | TDX-eltdx、AxData |
| prev_open_volume_hand | 2 | TDX-eltdx、AxData |
| prev_open_amount | 2 | TDX-eltdx、AxData |
| float_shares | 2 | TDX-eltdx、AxData |
| float_market_value | 2 | TDX-eltdx、AxData |
| free_float_shares | 2 | TDX-eltdx、AxData |
| free_float_market_value | 2 | TDX-eltdx、AxData |
| seal_to_amount_ratio | 2 | TDX-eltdx、AxData |
| seal_to_float_ratio | 2 | TDX-eltdx、AxData |
| seal_prev_ratio | 2 | TDX-eltdx、AxData |
| limit_stat_days | 2 | TDX-eltdx、AxData |
| limit_up_count_in_stat_days | 2 | TDX-eltdx、AxData |
| limit_board_text | 2 | TDX-eltdx、AxData |
| limit_up_streak_days | 2 | TDX-eltdx、AxData |
| year_limit_up_days | 2 | TDX-eltdx、AxData |
| last_price | 2 | TDX-eltdx、AxData |
| high | 2 | TDX-eltdx、AxData |
| low | 2 | TDX-eltdx、AxData |
| change | 2 | TDX-eltdx、AxData |
| volume | 2 | TDX-eltdx、AxData |
| locked_amount | 2 | TDX-eltdx、AxData |
| rise_speed | 2 | TDX-eltdx、AxData |
| short_turnover | 2 | TDX-eltdx、AxData |
| min2_amount | 2 | TDX-eltdx、AxData |
| vol_rise_speed | 2 | TDX-eltdx、AxData |
| limit_up_price | 2 | TDX-eltdx、AxData |
| limit_down_price | 2 | TDX-eltdx、AxData |
| limit_status | 2 | TDX-eltdx、AxData |
| 全市场快照 | 2 | TDX-0x0010/F10、同花顺-fuyao |
| 板块强度 | 2 | TDX-0x0010/F10、同花顺-fuyao |
| 市场情绪 | 2 | TDX-0x0010/F10、同花顺-fuyao |
| 板块轮动 | 2 | TDX-0x0010/F10、同花顺-fuyao |

**B.2 单源字段（1333 个，无 fallback）**

- **ZHB（84）**：A 实时、B 准实时、C 日频、D 静态、PE TTM、stat.board_count、stat.cash_reserve_wan、stat.change_10d、stat.change_10k_bar、stat.change_20d、stat.change_20k_bar、stat.change_30d、stat.change_30k_bar、stat.change_5d、stat.change_5k_bar、stat.change_60d、stat.change_60k_bar、stat.change_pct、stat.change_pct_1d、stat.change_pct_2d、stat.change_ytd、stat.code、stat.date、stat.dividend_yield、stat.employee_count、stat.free_ltgb、stat.market、stat.net_profit_kcf、stat.other_qy_jzc、stat.pe_dynamic、stat.pe_ttm、stat.pre_receive_zj、stat.rd_input_fee、stat.shape_value、stat.streak_days、stat.unknown_2、stat.unknown_26、stat.unseal_date、stat.zt_count、stat.zt_lianban、stat.zt_streak_cycle、stat.zt_type_code、stat2.amount、stat2.amount_1d、stat2.amount_2d、stat2.change_250k_bar、stat2.change_30k_bar、stat2.change_30k_bar_ref、stat2.change_mtd、stat2.code、stat2.date、stat2.high_52w、stat2.industry_code、stat2.ipo_price、stat2.low_52w、stat2.main_net_buy_amount、stat2.main_net_buy_amount_1d、stat2.main_net_buy_hands、stat2.main_net_buy_hands_1d、stat2.market
  - … 其余 24 个见正文
- **TDX-0x0010/F10（274）**：*ST湘邮、AI解读、BKFenShiZhiBo、ChangeStatistics、C中芯、DR 茅台、DailyLimitPerformance、DailyLimitPerformance2、GetBaseFaceListZDEvnArtNew、GetDayBaseFaceListZDEvnArt、GetDayNewHigh_W28、GetGPCPHBTS_Tag、GetHotPHB、GetInfo、GetKLineDay_W14、GetKLineZhangTing、GetMainMonitor_w30、GetPanKou、GetPlateInfo_w38、GetPlate_Info_QJ、GetStockBid、GetStockList、GetStockList（龙虎榜）、GetStockPanKou、GetStockTrendIncremental、GetWeiTuo_W14、GetYTFP_BKHX、GetYTFP_SCTD、GlobalCommon、GroupCount_w28、Index、InfoBKR、MarketStockZDNum、MoodNumCount、MorningBiddingList、NewGetList、N百花医药、Radar、RealRankingInfo、RiseFallAnalysis、ST百花医药、SharpWithdrawal、SonPlate_Info、Theme、XD、XR、ZhiShuStockList_W8、[..、[verify、all、api、axdata_verify.md)、axdata_verify.md](verify、balance_sheet` 资产负债表、belong、cash_flow` 现金流量表、changqifuzhai、client_fields_enum.md)、client_fields_enum.md](verify、color
  - … 其余 214 个见正文
- **TDX-eltdx（195）**：AuctionPoint.index、AuctionPoint.matched_volume、AuctionPoint.minute_of_day_raw、AuctionPoint.price、AuctionPoint.price_milli、AuctionPoint.record_hex、AuctionPoint.reserved_zero_0e、AuctionPoint.second_raw、AuctionPoint.time_label、AuctionPoint.time_seconds、AuctionPoint.unmatched_direction_raw、AuctionPoint.unmatched_volume、Enum `Market、FinanceInfo`（财务）、FundFlow、HistoricalFundFlow、KlineCategory、MarketStat、SecurityBar`（K 线）、SecurityInfo`（证券列表）、SecurityQuote`（五档）、XdxrRecord`（除权除息）、absolute_index、adjust、adjust_mode、adjust_mode_raw、alignment_status、auction_matched_volume、auction_unmatched_signed_volume、auctions.series（0x056a）、beta_60d、business_composition、buy_levels、c1_value~c4_value、category_name、circulating_shares、current_hand、dividend_financing、down_count、eltdx_auction_prev_volume_ratio、eltdx_has_shortline、eltdx_ladder_level、eltdx_limit_board_text、eltdx_limit_up_streak_days、eltdx_open_change_pct、eltdx_open_prev_amount_ratio、eltdx_open_turnover_z、eltdx_open_volume_ratio、eltdx_opening_rush、eltdx_seal_amount、eltdx_seal_to_float_ratio、eps_raw、event_kind、fenhong、finance_diagnosis、full_code、get_auction_0925、high_price、highest_ladder_level、history
  - … 其余 135 个见正文
- **腾讯（12）**：[0] 市场标识、[29][54][55][77][78] 占位符、[40] 停牌标记、[56] Beta 族、[76] A股流通股本、[85] 收盘参考基准价（L2 机制确认）、[86] 收盘集合竞价净未匹配手数(带符号)（L2 机制确认）、[87] 科创板、两融标记、分钟 K线、实测、月 K线
- **同花顺-fuyao（133）**：K线、PB、ROA、`big_order_flow(ths_code)`、a-share、a-share-index、accounts_receivable、adjustment-factors、anomaly-analysis-list、anomaly-analysis-stock、auction、auction.auction_price、auction.float_market_cap、balance-sheets、calendar、cash-flow、cash-flow-statements、cash_equivalents_net_addition、catalog、constituents、corporate-actions、download-url、dragon-tiger-list、dump、eps_deduct_ttm(f108)、fflow 历史资金流窗口、financials、get 财务 TTM 族、growth、growth.calculate_operating_income_yoy_growth_ratio、growth.calculate_parent_holder_net_profit_yoy_growth_ratio、historical、holder_equity_total、hot-stock-list、hot-stock-list-history、hot-stock-rank-trend、income-statements、income_tax_expense、indicators、interest_expenses、klines(count=N)、limit-break-pool` 🆕、limit-down-pool` 🆕、limit-up-ladder、limit-up-pool、list、manage_fee、market-dumps、meta、net_profit、net_profit_annual、net_profit_period、ocf_ttm、operating_profit、operation、pay_dividends_profits_interest_cash、pb、pcf、prices、profit_total
  - … 其余 73 个见正文
- **新浪（25）**：URL、ask、ask_vol、bid、bid_vol、delta、gamma、item_tongbi、item_value、iv、last、limit_down、limit_up、netamount、open_interest、opendate、prev_close、report_list.{期次}.data[].item_title、report_type、strike、theory、theta、trade、vega、参数
- **财联社（14）**：catalyst、cur_heat、limit_up_board、market_degree、performance、profit_ratio、rank_change、shsz_balance、shsz_balance_change_px、up_down_dis、up_open_num、up_open_ratio、up_ratio、up_ratio_num
- **开盘红（36）**：Detail、StockList、TagID、TagName、TagShuXing、ZSCode、ZSName、avg_change、buy_amount、dt、fall_dist、fall_num、flat、industry_id、industry_zt、limit_tag、market_cap、net_inflow、net_inflow_5d、open_time、q_zrcs、qscln、rise_dist、rise_num、s_zrcs、seal_money、sell_amount、sign、sjdt、sjzt、stdt、stock_count、stzt、szln、themes、zt
- **akshare（13）**：BPS、EPS、PE 历史百分位、push2 f137、push2 f51、push2 f55、两融 RZJME、历史分红、扣非净利、板块资金流 f62、涨跌停价、股息率、龙虎榜 EXPLAIN
- **AxData（66）**：activity、amplitude_pct、ask1_price、ask1_volume、attack_pct、average_change_pct、average_price、bid1_ask1_balance_pct、bid1_ask1_volume_diff、bid1_price、bid1_volume、capital_score、concept_capital_flow_tdx（题材资金走势）、cost70_concentration、cost70_range、cost90_concentration、cost90_range、current_volume、drawdown_pct、entrust_ratio、finance_updated_date、float_share、free_float_share_z、fundamental_score、high_change_pct、industry_name、industry_rank、industry_rank_total、inside_outside_ratio、inside_volume、instrument_id、limit_ratio_pct、limit_rule、low_change_pct、market_rank、market_rank_total、market_win_pct、name_flag、news_score、open_amount_ratio_pct、option_chain_tdx（期权T型）、outside_volume、pre_close_source、pre_close_trade_date、profit_ratio_pct、score、share_source、stock_allotment_cninfo（配股）、stock_financial_diagnosis_tdx（财务诊断）、stock_forecast_consensus_tdx（盈利预测）、stock_name、stock_realtime_rank_tdx（实时榜单）、stock_share_change_cninfo（股本变动）、stock_theme_strength_rank_tdx（题材强度排行）、symbol、tdx_code、theme_score、total_share、事件流、华证
  - … 其余 6 个见正文
- **东财（481）**：A+H 双上市标识、ABLE_FREE_SHARES、ACCUM_AMOUNT、ASSIGN_PROGRESS、AVG_FREE_SHARES、BILLBOARD_BUY_AMT、BILLBOARD_NET_AMT、BONUS_RATIO、BUY、BUYER_NAME、BUY_RATIO、BUY_SEAT、CHANGE_RATE、CHANGE_TYPE、CLOSE_PRICE、CPFZ、D1~D30_CLOSE_ADJCHRATE、DATE、DCP、DEAL_AMOUNT_RATIO、DEAL_AMT、DEAL_NET_RATIO、DEAL_PRICE、DEAL_VOLUME、END_DATE、EXPLAIN、EXPLANATION、EX_DIVIDEND_DATE、FIN_BALANCE_GR、FREE_DATE、FREE_MARKET_CAP、FREE_RATIO、FREE_SHARES、FREE_SHARES_TYPE、HOLDER_NUM、HOLDER_NUM_CHANGE、HOLDER_NUM_RATIO、JLY、JZC、LDFZ、LINK_URL、LYZE、MARKET、NET、NET_BS_AMT、NextTwoYear、NextYear、OPERATEDEPT_CODE、OPERATEDEPT_NAME、PRETAX_BONUS_RMB、RCHANGE3D、RPTA_WEB_RZRQ_GGMX（两融）、RPT_DAILYBILLBOARD_DETAILSNEW（龙虎榜）、RPT_HOLDERNUMLATEST（股东户数）、RPT_LIFT_STAGE（解禁）、RPT_SHAREBONUS_DET（分红）、RQCHL、RQMCL、RQYE、RQYL
  - … 其余 421 个见正文

<!-- /GEN:field-matrix -->
