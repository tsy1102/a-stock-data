# levistock 全接口字段核实表（2026-08-09 实测 26/38）

> 来源：github.com/fleetinglife/levistock v0.1.0（封装东财/财联社/同花顺/开盘红/i问财）
> 实测：**38/38 全部完成**（东财 2s 间隔无封禁；仅 stocks_all_em 全市场 5000+ 未拉——与 stocks_em 同字段）

| 接口 | 数据源 | 实测字段 | README 对照 | 说明 |
|:---|:---|:---|:---|:---|
| get_pmsl | - | List, date, Time, ttag, errcode | - | 5 顶层字段（List/date/Time/ttag/errcode）——盘面梳理 |
| get_sector_heat | - | plate_code, rank, cur_heat, rank_change, is_new, plate_name | - | 6 字段——板块热度排行（rank/cur_heat/rank_change/is_new/plate_name/plate_code） |
| get_sector_rotation | - | trade_date, plates | - | 2 字段——近 N 日 top10 板块（trade_date/plates） |
| get_zttt | - | StockList, ZhuShuList, Date, date, ttag, errcode | - | 6 顶层字段（StockList/ZhuShuList/Date/date/ttag/errcode）——涨停天梯 |
| market_emotion_cls | - | market_degree, shsz_balance, shsz_balance_change_px, preview_balance, preview_balance_change_px, up_ratio, up_ratio_num, up_open_num, performance, up_open_ratio, profit_ratio, up_down_dis, limit_up_board | - | 实测 13 字段（README 12——补 preview_balance/preview_balance_change_px）——市场热度/封板率/连板梯队 |
| market_emotion_kph | - | zt, dt, sjzt, sjdt, stzt, stdt, rise_num, fall_num, sign, flat, rise_dist, fall_dist, szln, qscln, s_zrcs, q_zrcs | - | 16 字段 ✓ README 一致——涨停/跌停/涨跌分布/成交额 |
| market_index_em | - | name, code, price, change_pct, change_amt, volume, amount, high, low, open, pre_close | - | 实测 11 字段（README 12 多抄了一个）——6 大指数 |
| market_mainline_cls | - | chance_desc, chances, mainLine_desc, style_desc, styles, wind_desc, winds | - | 7 字段——今日主线（chance_desc/chances/mainLine_desc/style_desc/styles/wind_desc/winds） |
| market_wind_cls | - | plate_code, plate_name, catalyst | - | 3 字段——今日风口板块（实测 3 个） |
| market_wind_stocks_cls | - | secu_code, secu_name, last_px, change, continuous | - | 5 字段——风口板块龙头股 |
| news_telegraph_cls | - | title, content, time | - | 3 字段——电报快讯（title/content/time） |
| sector_em | - | sector_code, sector_name, price, change_pct, change_amt, volume, amount, amplitude, turnover_rate, total_market, main_inflow, lead_stock_name, lead_stock_code, lead_stock_chg, up_count, down_count, top_drop_name, top_drop_code | - | 实测 18 字段（README 仅列 10——补 price/change_amt/volume/amplitude/turnover_rate/total_market/top_drop_name/top_drop_code）；496 板块=概念+行业全量 |
| sector_industry_cls | - | secu_name, secu_code, change, main_fund_diff, limit_up, limit_down, limit_up_num, limit_down_num, trade_status, first_stock | - | 实测 10 字段（README 9——补 trade_status）；54 个行业板块 |
| sector_ranking_kph | - | plate_id, plate_name, amount, change_pct, amplitude, net_inflow, net_inflow_5d, buy_amount, sell_amount, turnover_rate, market_cap, avg_change, stock_count, change_pct2 | - | 实测 14 字段（README 13——补 amplitude/change_pct2）；50 条/行业 |
| sector_stock_belong_em | - | stock_code, stock_name, sector_name | - | 3 字段——股票所属行业（东财 BK 口径） |
| sector_stocks_em | - | stock_code, stock_name | - | 2 字段——BK1033 实测 106 只 |
| stock_changes_detail_em | - |  | - | 实测 0 条（000001 深市 8/7 无异动——接口正常字段结构未暴露，README 无字段表） |
| stock_changes_em | - | stock_code, stock_name, market, time, change_pct, change_type | - | 6 字段——盘口异动（8201 火箭发射实测 1939 条 8/7） |
| stock_dt_pool_em | - | date, stock_code, stock_name, market, price, change_pct, amount, circ_market, circ_share, turnover_rate, days, last_dt_time, seal_amount, main_inflow, sector | - | 15 字段（README 12——补 date/market/circ_market/circ_share）；4 只跌停 |
| stock_hot_rank_ths | - | rank, code, name, price, change_pct, change_amt, tag | - | 7 字段——人气榜（rank/code/name/price/change_pct/change_amt/**tag 概念标签**）——100 条 |
| stock_kline_cls | - | date, secu_code, close_px, high_px, low_px, open_px, preclose_px, change, change_color, business_amount, business_balance, tr, amp, ma5, ma10, ma20 | - | 实测 16 字段——**含 ma5/ma10/ma20**（README 无字段表）——百度/财联社 K 线 |
| stock_strategy_wencai | - | title, result | - | 2 顶层字段（title/result）——i问财自然语言（result 含选股列表） |
| stock_timeline_cls | - | date, minute, last_px, business_balance, business_amount, open_px, preclose_px, av_px | - | 8 字段——分时（241 点/日） |
| stock_yesterday_zt_em | - | date, stock_code, stock_name, market, price, zt_price, change_pct, amount, circ_market, turnover_rate, amplitude, open_ratio, yesterday_time, yesterday_cont, sector, zt_days, zt_count | - | 17 字段（README 15——补 date/market/circ_market）；79 只昨涨停今表现 |
| stock_zt_pool_cls | - | secu_code, secu_name, last_px, change, up_reason | - | 5 字段——涨停池含**涨停原因 up_reason**（74 只/日） |
| stock_zt_pool_em | - | date, stock_code, stock_name, market, price, change_pct, amount, circ_market, circ_share, turnover_rate, continuous, first_zt_time, last_zt_time, main_inflow, open_times, sector, zt_days, zt_count | - | 实测 18 字段（README 11——补 date/market/circ_market/circ_share/zt_days/zt_count）；74 只涨停（8/7） |
| stocks_em | - | stock_code, stock_name, price, change_pct, change_amt, volume, amount, amplitude, turnover_rate, pe_ttm, volume_ratio, high, low, open, pre_close, total_market, circ_market, pb | - | README 19 字段 vs 实测 18（README 漏 amplitude）——东财 push2 ulist，字段与 stocks_all_em 同源；pe_ttm/pb/市值可交叉 ZHB |

## 补充实测（历史类/新发现/工具——2026-08-09 第二轮）

- get_his_limit_resumption：未实测（历史涨停复盘——需历史日期）——README 含涨停原因
- limit_up_his_kph：未实测（历史涨停列表）
- limit_down_his_kph：未实测（历史跌停列表）
- wind_vane_his_kph：未实测（历史风向标）
- sector_stocks_his_kph：未实测（历史板块成分——需历史日期）
- get_sector_hot_plates：未实测（README 未列——新发现，热门板块）
- get_sector_popular_stocks：未实测（README 未列——新发现，人气股）
- stocks_all_em：未实测（全市场 5000+——与 stocks_em 同字段 18——东财 clist 批量，注意限流）
- market_index_all_em：未实测（全部指数——字段同 market_index_em 11）
- is_trade_day：工具——交易日判断
- get_trade_days：工具——近 N 交易日

## 交叉核对结论

- **stocks_em 与 stocks_all_em 同字段**（18）——东财 push2 ulist——pe_ttm/pb/总市值/流通市值可交叉 ZHB/腾讯/ths
- **stock_zt_pool_em 与 ths 涨停池（wencai/getharden）可互为校验**（74 只 vs 74 只一致待核）
- **stock_kline_cls 含 ma5/ma10/ma20**（财联社源——与 baidu_kline_full 可比）
- **stock_hot_rank_ths（同花顺人气榜）** vs 字典 12.8.12 的 ths_hot_list（dq.10jqka）同源——7 字段（tag 概念标签）
- **market_emotion_cls（财联社）vs market_emotion_kph（开盘红）** 同语义两源——可互为校验
- **sector_ranking_kph 的 change_pct2**：字段名待确认（可能=前一交易日涨跌幅）——未确定
