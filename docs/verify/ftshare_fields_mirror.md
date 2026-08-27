# FTShare MCP 全字段镜像（2026-08-25 实弹采样 v2）

> 字段表来自实际响应首行；❌ 条目为参数需人工复核或上游空数据。

## capital_flow（资金流）

- 参数: {} | 行数: 50
- 字段(8): net_inflow_extra_large、net_inflow_large、net_inflow_main、net_inflow_medium、net_inflow_small、symbol、symbol_name、ts_nanos
- 样例: {"net_inflow_extra_large": "1505559951.17", "net_inflow_large": "731358838.97", "net_inflow_main": "2236918790.14", "net_inflow_medium": "-2146431496.46", "net_inflow_small": "-90487293.68", "symbol": "688835.SH", "symbol_name": "N高凯", "ts_nanos": 1787643000000000000}

## daily_ohlc（日频 OHLC）

- 状态: ❌ {"error":{"code":"MISSING_PARAMETER","field":"symbol","message":"缺少必填或条件必填参数，字段 （参数变体已试: [{}]）

## ft_abnormal_trading_details（龙虎榜明细）

- 参数: {} | 行数: 20
- 字段(6): change_rate、close、symbol、top_buyers、top_sellers、turnover
- 样例: {"change_rate": 0.09991079393398744, "close": "12.33", "symbol": "002412.SZ", "top_buyers": [{"buy": "21217001.34", "name": "机构专用", "net": "12229515.68", "sell": "8987485.66"}, {"buy": "21133726.27", "name": "机构专用", "net": "16883714.27", "sell": "4250012"}, {"buy": "16867561.2", "name": "机构专用", "net": "512575.66", "sel

## ft_abnormal_trading_overview（龙虎榜总览）

- 参数: {} | 行数: 1
- 字段(3): bjse、xshe、xshg
- 样例: {"bjse": [{"change_rate": -0.019194262813752305, "close": "46.5", "symbol": "920206.BJ", "symbol_name": "彩客科技", "turnover": "311026639"}, {"change_rate": 0.009798865394533148, "close": "19.58", "symbol": "920093.BJ", "symbol_name": "信胜科技", "turnover": "138062928"}, {"change_rate": 0.006016042780748653, "close": "15.05"

## ft_auction_results（集合竞价结果）

- 参数: {} | 行数: 50
- 字段(8): amount、close、high、low、open、symbol、volume、vwap
- 样例: {"amount": "9576776.0000", "close": "11.5600", "high": "11.5900", "low": "11.5600", "open": "11.5700", "symbol": "000001.XSHE", "volume": 827500, "vwap": "11.5731"}

## ft_baidu_financial_calendar（百度财经日历）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","message":"时间范围不能超过 3 天","retryable":false}}（参数变体已试: [{"start_date": "20260818", "end_date": "20260825"}, {"start_date": "20260818", "end_date": "2026-08-25"}]）

## ft_balance（A股资产负债表）

- 状态: ❌ {"error":{"code":"MISSING_PARAMETER","details":{"required_any_of":[["stock_code"（参数变体已试: [{}]）

## ft_block_trades（大宗交易）

- 参数: {} | 行数: 32
- 字段(9): buyer_name、close、date、name、premium_rate、price、seller_name、symbol、volume
- 样例: {"buyer_name": "中信证券股份有限公司徐州建国西路证券营业部", "close": "51.56", "date": "2026-08-25", "name": "飞龙股份", "premium_rate": -0.1001, "price": "46.4", "seller_name": "申万宏源证券有限公司南阳新华西路证券营业部", "symbol": "002536.SZ", "volume": 85700}

## ft_cashflow（A股现金流量表）

- 状态: ❌ {"error":{"code":"MISSING_PARAMETER","details":{"required_any_of":[["stock_code"（参数变体已试: [{}]）

## ft_convertible_bond_candlesticks（可转债K线）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","details":{"constraint":"enum:Minute/Day/Wee（参数变体已试: [{"symbol": "600519.XSHG", "interval_unit": "", "until_ts_millis": ""}, {"symbol": "600519", "interval_unit": "", "until_ts_millis": ""}]）

## ft_convertible_bond_candlesticks_batch（批量可转债K线）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","details":{"constraint":"enum:Minute/Day/Wee（参数变体已试: [{"symbols": "600519.XSHG", "interval_unit": "", "until_ts_millis": ""}, {"symbols": "600519", "interval_unit": "", "until_ts_millis": ""}]）

## ft_daec_distribution_history（DAEC日内涨跌停分布历史）

- 参数: {} | 行数: 242
- 字段(3): down_limited、ts_ms、up_limited
- 样例: {"down_limited": 0, "ts_ms": 1787554800000, "up_limited": 0}

## ft_daec_market_snapshot（DAEC市场行情快照）

- 参数: {} | 行数: 1
- 字段(6): change_rate、distribution、prev_turnover、status、turnover、volume
- 样例: {"change_rate": 0.0, "distribution": {"down_0pct_to_1pct": 528, "down_1pct_to_5pct": 660, "down_5pct_to_limited": 54, "down_limited": 4, "flat": 70, "up_0pct_to_1pct": 918, "up_1pct_to_5pct": 2982, "up_5pct_to_limited": 264, "up_limited": 70}, "prev_turnover": "0", "status": "closed", "turnover": "1844278181062.57", "v

## ft_daec_ohlcs（DAEC历史OHLC）

- 状态: ❌ {"error":{"code":"MISSING_PARAMETER","details":{"required_any_of":[["since","unt（参数变体已试: [{"symbol": "600519.XSHG"}, {"symbol": "600519"}]）

## ft_daec_prev_closes（DAEC标的昨收价）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","field":"since","message":"参数值不满足约束，字段 `sinc（参数变体已试: [{"symbol": "600519.XSHG", "since": "", "until": ""}, {"symbol": "600519", "since": "", "until": ""}]）

## ft_daec_prices（DAEC分时价格）

- 参数: {"symbol": "600519.XSHG"} | 行数: 437
- 字段(5): avg_price、price、ts_ms、turnover、volume
- 样例: {"avg_price": 1301.1242146596858, "price": 1300.23, "ts_ms": 1787103300000, "turnover": 24851472.5, "volume": 19100}

## ft_daec_stocks_all（DAEC全市场A股行情）

- 参数: {} | 行数: 20
- 字段(32): amplitude、avg、bid_ask_ratio、board、change、change_rate、change_rate_day10、change_rate_day120、change_rate_day20、change_rate_day5、change_rate_day60、change_rate_ytd、close、float_a_shares、high、listing_date、low、market_cap、name、open、pe_ttm、prev_close、shares、st、status、symbol、symbol_id、tradable_a_market_cap、ts_millis、turnover、turnover_rate、volume
- 样例: {"amplitude": 0.009515570934256003, "avg": 11.58170960089052, "bid_ask_ratio": -0.6332807859219335, "board": "XsheMain", "change": "0.03", "change_rate": 0.0025951557093425604, "change_rate_day10": 0.02930728241563055, "change_rate_day120": 0.1017110266159696, "change_rate_day20": 0.03482142857142857, "change_rate_day5

## ft_daec_stocks_bjse（DAEC北证A股行情）

- 参数: {} | 行数: 20
- 字段(32): amplitude、avg、bid_ask_ratio、board、change、change_rate、change_rate_day10、change_rate_day120、change_rate_day20、change_rate_day5、change_rate_day60、change_rate_ytd、close、float_a_shares、high、listing_date、low、market_cap、name、open、pe_ttm、prev_close、shares、st、status、symbol、symbol_id、tradable_a_market_cap、ts_millis、turnover、turnover_rate、volume
- 样例: {"amplitude": 0.01696165191740403, "avg": 13.610197897672425, "bid_ask_ratio": -0.019549924210035367, "board": "Bjse", "change": "0.11", "change_rate": 0.008112094395280236, "change_rate_day10": -0.0800807537012113, "change_rate_day120": -0.23072594259988743, "change_rate_day20": 0.06796875, "change_rate_day5": -0.0346

## ft_daec_stocks_xshe（DAEC深证A股行情）

- 参数: {} | 行数: 20
- 字段(32): amplitude、avg、bid_ask_ratio、board、change、change_rate、change_rate_day10、change_rate_day120、change_rate_day20、change_rate_day5、change_rate_day60、change_rate_ytd、close、float_a_shares、high、listing_date、low、market_cap、name、open、pe_ttm、prev_close、shares、st、status、symbol、symbol_id、tradable_a_market_cap、ts_millis、turnover、turnover_rate、volume
- 样例: {"amplitude": 0.009515570934256003, "avg": 11.58170960089052, "bid_ask_ratio": -0.6332807859219335, "board": "XsheMain", "change": "0.03", "change_rate": 0.0025951557093425604, "change_rate_day10": 0.02930728241563055, "change_rate_day120": 0.1017110266159696, "change_rate_day20": 0.03482142857142857, "change_rate_day5

## ft_daec_stocks_xshg（DAEC上证A股行情）

- 参数: {} | 行数: 20
- 字段(32): amplitude、avg、bid_ask_ratio、board、change、change_rate、change_rate_day10、change_rate_day120、change_rate_day20、change_rate_day5、change_rate_day60、change_rate_ytd、close、float_a_shares、high、listing_date、low、market_cap、name、open、pe_ttm、prev_close、shares、st、status、symbol、symbol_id、tradable_a_market_cap、ts_millis、turnover、turnover_rate、volume
- 样例: {"amplitude": 0.023861171366594235, "avg": 9.123593584662355, "bid_ask_ratio": 0.4999211039432541, "board": "XshgMain", "change": "-0.14", "change_rate": -0.015184381778741866, "change_rate_day10": -0.014115092290988056, "change_rate_day120": -0.024704618689581095, "change_rate_day20": -0.011969532100108817, "change_ra

## ft_earnings_reports_paginated（业绩快报）

- 状态: ❌ {"error":{"code":"MISSING_PARAMETER","details":{"required_any_of":[["stock_code"（参数变体已试: [{}]）

## ft_eastmoney_board_constituents（东方财富板块成份股）

- 状态: ❌ {"error":{"code":"UPSTREAM_UNAVAILABLE","message":"上游服务暂时不可用","retryable":true}}（参数变体已试: [{"board_code": ""}]）

## ft_eastmoney_board_daily_kline（东方财富板块日线OHLC）

- 状态: ❌ {"error":{"code":"UPSTREAM_UNAVAILABLE","message":"上游服务暂时不可用","retryable":true}}（参数变体已试: [{"board_code": ""}]）

## ft_eastmoney_board_latest_kline（东方财富板块最新OHLC）

- 参数: {} | 行数: 50
- 字段(14): amplitude、board_code、board_name、change、change_rate、close、date、high、low、market、open、turnover、turnover_rate、volume
- 样例: {"amplitude": 2.51, "board_code": "BK0425", "board_name": "工程建设", "change": "407.86", "change_rate": 1.65, "close": "25087.88", "date": "2026-08-25", "high": "25137.69", "low": "24518.52", "market": 90, "open": "24548.06", "turnover": "14004474309"}

## ft_eastmoney_concept_boards（东方财富概念板块）

- 参数: {} | 行数: 486
- 字段(2): code、name
- 样例: {"code": "BK1645", "name": "昨日打二板以上表现"}

## ft_eastmoney_futures_strange（东方财富期货龙虎榜）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","message":"字段 `exchange` 不能为空","retryable":f（参数变体已试: [{"exchange": "", "variety": "", "contract": "", "trade_date": "20260822"}, {"exchange": "", "variety": "", "contract": "", "trade_date": "2026-08-22"}]）

## ft_eastmoney_rank（东方财富股票排名）

- 参数: {} | 行数: 50
- 字段(9): change_amount、change_pct、hot_score、latest_price、normalized_symbol、rank_change、rank_no、raw_symbol、stock_name
- 样例: {"change_amount": "-0.280000", "change_pct": "-0.050000", "hot_score": "23681135.929325", "latest_price": "602.800000", "normalized_symbol": "688836", "rank_change": 0, "rank_no": 1, "raw_symbol": "688836", "stock_name": "C宇树-W"}

## ft_eastmoney_us_stock_daily_kline（东方财富美股日OHLC）

- 状态: ❌ {"error":{"code":"UPSTREAM_REJECTED","message":"上游拒绝处理该请求","retryable":false}}（参数变体已试: [{"stock_code": "600519.XSHG"}, {"stock_code": "600519"}]）

## ft_eastmoney_us_stock_latest_kline（东方财富美股最新OHLC）

- 状态: ❌ {"error":{"code":"UPSTREAM_REJECTED","message":"上游拒绝处理该请求","retryable":false}}（参数变体已试: [{"stock_code": "600519.XSHG"}, {"stock_code": "600519"}]）

## ft_eastmoney_us_stock_list（东方财富美股列表）

- 参数: {} | 行数: 50
- 字段(10): amount、change_pct、code、latest_price、market、market_value_usd、name、pe_ttm、secid、volume
- 样例: {"amount": "", "change_pct": "-291", "code": "NVDA", "latest_price": "208480", "market": "105", "market_value_usd": "5045216000000", "name": "英伟达", "pe_ttm": "3161", "secid": "105.NVDA", "volume": ""}

## ft_etf_adjust_factor（ETF复权因子）

- 参数: {} | 行数: 50
- 字段(4): adj_factor、ex_adj_factor、symbol、trade_date
- 样例: {"adj_factor": 1.0, "ex_adj_factor": 1.0, "symbol": "158003.SZ", "trade_date": "20260825"}

## ft_etf_candlesticks（ETFK线）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","details":{"constraint":"enum:Minute/Day/Wee（参数变体已试: [{"symbol": "600519.XSHG", "interval_unit": "", "until_ts_millis": ""}, {"symbol": "600519", "interval_unit": "", "until_ts_millis": ""}]）

## ft_etf_candlesticks_batch（批量ETFK线）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","details":{"constraint":"enum:Minute/Day/Wee（参数变体已试: [{"symbols": "600519.XSHG", "interval_unit": "", "until_ts_millis": ""}, {"symbols": "600519", "interval_unit": "", "until_ts_millis": ""}]）

## ft_etf_components_all（ETF成份列表）

- 参数: {} | 行数: 5
- 字段(3): components、components_name、symbol
- 样例: {"components": ["000938.SZ", "000977.SZ", "002049.SZ", "002230.SZ", "002236.SZ", "002371.SZ", "002415.SZ", "002920.SZ", "300033.SZ", "300059.SZ", "300124.SZ", "300339.SZ", "300408.SZ", "300442.SZ", "300454.SZ", "300604.SZ", "300803.SZ", "300857.SZ", "301269.SZ", "301308.SZ", "301638.SZ", "301656.SZ", "600536.SH", "6005

## ft_etf_description_all（ETF基础信息）

- 参数: {} | 行数: 50
- 字段(12): asset_class、custodian、float_shares、inception_date、management_company、marginable、name、supports_t0、symbol、tracking_index、tracking_index_id、tracking_index_symbol
- 样例: {"asset_class": "stock", "custodian": "交通银行", "float_shares": 39383993, "inception_date": "2025-07-07", "management_company": "易方达基金", "marginable": false, "name": "数字经济ETF易方达", "supports_t0": false, "symbol": "159311.XSHE", "tracking_index": "数字经济", "tracking_index_id": "931582.CSI", "tracking_index_symbol": "931582.C

## ft_etf_fund_export（指数ETF基金导出）

- 参数: {"request_id": ""} | 行数: 19
- 字段(29): accesn_date、annureturn_3y、annureturn_5y、annureturn_establ、aum、best_return、establmt_date、etf_code、exabbr、exchange、fund_manager、fund_managers、fund_type、is_inoffice、max_chargrt、nav_growth_rate、operat_mode、return_6m、return_d、return_w、return_y、risk_lvl、security_code、security_id、security_name、top10_holdings、tot_asset、total_fee_rate、total_return
- 样例: {"accesn_date": "20190712", "annureturn_3y": 11.3080068019, "annureturn_5y": 3.3665696717, "annureturn_establ": 6.676047516, "aum": 158001640.83, "best_return": 13.1762577533, "establmt_date": "20110916", "etf_code": "510290.场外交易市场", "exabbr": "", "exchange": "场外交易市场", "fund_manager": "孙伟", "fund_managers": [{"accesn_d

## ft_etf_pcf_list_handler（ETF-PCF清单列表）

- 状态: ❌ {"error":{"code":"INVALID_TYPE","field":"date","message":"参数类型错误，字段 `date`，请检查 i（参数变体已试: [{"date": "20260822"}, {"date": "2026-08-22"}]）

## ft_get_bse_mapping（北交所映射）

- 参数: {} | 行数: 248
- 字段(4): listing_date、new_code、old_code、stock_name
- 样例: {"listing_date": "2023-05-31", "new_code": "920017", "old_code": "430017", "stock_name": "星昊医药"}

## ft_get_bullion_price（贵金属价格）

- 状态: ❌ {"error":{"code":"INVALID_TYPE","field":"end_date","message":"参数类型错误，字段 `end_dat（参数变体已试: [{"symbol": "600519.XSHG", "start_date": "20260818", "end_date": "20260825", "page": "", "page_size": ""}, {"symbol": "600519.XSHG", "start_date": "20260818", "）

## ft_get_bullion_support_symbol（贵金属支持标的）

- 参数: {} | 行数: 2
- 字段(4): currency、symbol、symbol_name、unit
- 样例: {"currency": "美元", "symbol": "XAUUSD", "symbol_name": "现货黄金(伦敦)", "unit": "美元/盎司"}

## ft_get_cashflow_stock_code（现金流支持股票代码）

- 参数: {} | 行数: 200
- 字段(2): stock_code、stock_name
- 样例: {"stock_code": "000001.SZ", "stock_name": "平安银行"}

## ft_get_cb_base_data_handler（可转债基础数据）

- 状态: ❌ {"error":{"code":"UPSTREAM_REJECTED","message":"上游拒绝处理该请求","retryable":false}}（参数变体已试: [{"symbol_code": "600519.XSHG"}, {"symbol_code": "600519"}]）

## ft_get_cb_lists_handler（可转债列表）

- 参数: {} | 行数: 100
- 字段(4): cb_id、exchange、full_name、stock_id
- 样例: {"cb_id": 110001, "exchange": 3553, "full_name": "邯郸钢铁股份有限公司可转换公司债券", "stock_id": 600001}

## ft_get_china_futures_base_data_handler（中国期货基础数据）

- 参数: {} | 行数: 20
- 字段(28): de_list_tdate、delivery_date、delivery_mean、delivery_site、exchange、future_type、last_trade_date、last_trade_date_hour、list_date、margin_info、mean_cal_value、min_put_price_info、multiplier、position_limit_info、price_fluctuation_info、price_unit、product、put_price、spot_symbol、sub_type_code、symbol、symbol_cn_name、trade_date、trade_hours_info、trade_months_info、trade_unit、type_code、value_info
- 样例: {"de_list_tdate": 20260914, "delivery_date": "最后交易日后第3个交易日", "delivery_mean": "实物交割", "delivery_site": "大连商品交易所指定交割仓库", "exchange": "DCE", "future_type": 2, "last_trade_date": "合约月份的第10个交易日", "last_trade_date_hour": "", "list_date": 20250915, "margin_info": "最低交易保证金:合约价值的5%", "mean_cal_value": 1.0, "min_put_price_info"

## ft_get_china_futures_lists_handler（中国期货列表）

- 参数: {} | 行数: 100
- 字段(5): exchange、future_type、product、symbol、symbol_cn_name
- 样例: {"exchange": "DCE", "future_type": 2, "product": "A", "symbol": "A2609.DCE", "symbol_cn_name": "黄大豆1号"}

## ft_get_company_list（公司列表）

- 参数: {} | 行数: 35
- 字段(23): bk、business_products、business_scope、change_percent、circulation_capital、circulation_value、close、company_code、company_profile、crawl_date、created_at、id、listing_date、listing_type、main_business、pb、pe、source、stock_code、stock_name、total_capital、total_market_value、updated_at
- 样例: {"bk": "银行,银行Ⅱ,股份制银行Ⅲ,广东板块,低市净率,金融地产风格,大盘价值,大盘股,价值股,长期破净,破净股,标准普尔,富时罗素,深证100R,MSCI中国,深股通,融资融券,深成500,机构重仓,HS300_,跨境支付,区块链,互联网金融,深圳特区", "business_products": "主营产品：报告期：2026-06-30,其他业务收入64.87亿 ，占比9.19% ，利润57.4亿 ，占比11.31% ，毛利率88.48%；批发金融业务收入325.59亿 ，占比46.11% ，利润246.48亿 ，占比48.56% ，毛利率75.7%；零售金融业务收入315.71亿 ，占比44.71% ，利润203.73

## ft_get_eastmoney_dapan_flow（东方财富大盘资金流）

- 参数: {} | 行数: 50
- 字段(16): large_net、large_pct、main_net、main_pct、mid_net、mid_pct、name、sh_change_pct、sh_close、small_net、small_pct、sz_change_pct、sz_close、trade_date、xlarge_net、xlarge_pct
- 样例: {"large_net": "-323.2911", "large_pct": "-1.04", "main_net": "-346.2785", "main_pct": "-1.11", "mid_net": "-142.2252", "mid_pct": "-0.46", "name": "上证指数", "sh_change_pct": "0.92", "sh_close": "4120.43", "small_net": "488.5037", "small_pct": "1.56", "sz_change_pct": "1.15"}

## ft_get_eastmoney_futures_position（东方财富期货持仓）

- 参数: {} | 行数: 50
- 字段(28): contract_code、exchange、long_position、lp_avg_price、lp_change、lp_down_rank、lp_rank、lp_up_rank、member_name_abbr、net_long_position、net_short_position、nlp_change、nlp_rank、nsp_change、nsp_rank、org_code、settle_price、short_position、sp_avg_price、sp_change、sp_down_rank、sp_rank、sp_up_rank、trade_date、variety_code、volume、volume_change、volume_rank
- 样例: {"contract_code": "IC2609", "exchange": "cffex", "long_position": "23424", "lp_avg_price": "7929.2526", "lp_change": "-845", "lp_down_rank": "3", "lp_rank": "2", "lp_up_rank": "27", "member_name_abbr": "中信期货(代客)", "net_long_position": "", "net_short_position": "8844", "nlp_change": ""}

## ft_get_eastmoney_market_valuation（东方财富市场估值）

- 参数: {} | 行数: 50
- 字段(11): change_rate、close_price、free_market_cap、free_shares、listing_org_num、market_code、market_name、pe_ttm、total_shares、trade_date、trade_market_value
- 样例: {"change_rate": "0.1916", "close_price": "3889.4449", "free_market_cap": "4998834100", "free_shares": "463953200", "listing_org_num": "1702", "market_code": "000001", "market_name": "上证指数", "pe_ttm": "13.79", "total_shares": "485633300", "trade_date": "2026-08-25", "trade_market_value": "5195049000"}

## ft_get_eastmoney_sector_flow（东方财富板块资金流）

- 参数: {} | 行数: 50
- 字段(14): large_net、large_pct、main_net、main_pct、medium_net、medium_pct、sector_code、sector_name、sector_type、small_net、small_pct、super_large_net、super_large_pct、trade_date
- 样例: {"large_net": "2.9024", "large_pct": "0.21", "main_net": "4.5249", "main_pct": "0.33", "medium_net": "-2.0489", "medium_pct": "-0.15", "sector_code": "BK0145", "sector_name": "上海板块", "sector_type": "regional", "small_net": "-1.7833", "small_pct": "-0.13", "super_large_net": "1.6226"}

## ft_get_eastmoney_stock_flow（东方财富个股资金流）

- 参数: {} | 行数: 50
- 字段(16): change_pct、close_price、code、large_net、large_pct、main_net、main_pct、market、medium_net、medium_pct、name、small_net、small_pct、super_large_net、super_large_pct、trade_date
- 样例: {"change_pct": "0.26", "close_price": "11.59", "code": "000001", "large_net": "63987150", "large_pct": "5.55", "main_net": "9477703", "main_pct": "0.82", "market": "0", "medium_net": "24801536", "medium_pct": "2.15", "name": "平安银行", "small_net": "-34279259"}

## ft_get_eastmoney_stock_valuation（东方财富个股估值）

- 状态: ❌ {"error":{"code":"MISSING_PARAMETER","details":{"required_any_of":[["symbol"],["（参数变体已试: [{}]）

## ft_get_etf_components_handler（ETF成份股）

- 状态: ❌ {"error":{"code":"UPSTREAM_REJECTED","message":"上游拒绝处理该请求","retryable":false}}（参数变体已试: [{"symbol": "600519.XSHG"}, {"symbol": "600519"}]）

## ft_get_etf_pre（ETF盘前数据）

- 参数: {} | 行数: 50
- 字段(13): cash_component、creation_redemption_flag、creation_redemption_unit、estimate_cash_component、etf_market_id、etf_symbol_id、max_cash_ratio、member_market_type、nav、nav_per_cu、publish_ipov、record_num、trade_date
- 样例: {"cash_component": -249.64, "creation_redemption_flag": 3, "creation_redemption_unit": 1000000, "estimate_cash_component": -310.51, "etf_market_id": 3554, "etf_symbol_id": 158003, "max_cash_ratio": 1.0, "member_market_type": 6, "nav": 1.0172, "nav_per_cu": 1017161.01, "publish_ipov": 1, "record_num": 50}

## ft_get_etf_pre_single_handler（单只ETF盘前数据）

- 状态: ❌ {"error":{"code":"UPSTREAM_REJECTED","message":"上游拒绝处理该请求","retryable":false}}（参数变体已试: [{"symbol": "600519.XSHG"}, {"symbol": "600519"}]）

## ft_get_hk_basinfo（港股个股信息）

- 状态: ❌ {"error":{"code":"UPSTREAM_REJECTED","message":"上游拒绝处理该请求","retryable":false}}（参数变体已试: [{"hk_code": ""}]）

## ft_get_hk_candlesticks（港股K线）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","details":{"constraint":"enum:day/month/quar（参数变体已试: [{"trade_code": "", "interval_unit": "", "until_date": "20260825"}, {"trade_code": "", "interval_unit": "", "until_date": "2026-08-25"}]）

## ft_get_hk_valuatnanalyd（港股估值分析）

- 参数: {} | 行数: 20
- 字段(30): amount、ashare_num、bshare_num、dividrt_lyr_rpt、dividrt_ttm、forwd_pe、hshare_circ_mv、hshare_limit_num、hshare_mv、hshare_num、id、minprice_chg、nonhshare_num、op_mode、pb、pcf、pcf_ttm、pe_lyr、pe_ttm、price_close、ps、ps_ttm、security_id、security_name、trade_code、trade_date、turnover_rt、update_time、volatility_y、volume
- 样例: {"amount": "0", "ashare_num": "0", "bshare_num": "0", "dividrt_lyr_rpt": "0", "dividrt_ttm": "0", "forwd_pe": "5.1627", "hshare_circ_mv": "72006749.44", "hshare_limit_num": "0", "hshare_mv": "72006749.44", "hshare_num": "56255273", "id": 17137980, "minprice_chg": "0.01"}

## ft_get_market_cap_hk（港股市值）

- 状态: ❌ {"error":{"code":"UPSTREAM_REJECTED","message":"上游拒绝处理该请求","retryable":false}}（参数变体已试: [{"trade_code": ""}]）

## ft_get_namechange（股票曾用名）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","field":"trade_code","message":"参数值不满足约束，字段 （参数变体已试: [{"trade_code": ""}]）

## ft_get_nth_trade_date（第N个交易日）

- 状态: ❌ {"error":{"code":"INVALID_TYPE","field":"n","message":"参数类型错误，字段 `n`，请检查 inputSc（参数变体已试: [{"n": ""}]）

## ft_get_price_change（价格变动）

- 状态: ❌ {"error":{"code":"INVALID_TYPE","field":"n","message":"参数类型错误，字段 `n`，请检查 inputSc（参数变体已试: [{"stock_code": "600519.XSHG", "base_date": "20260822", "n": "", "direction": ""}, {"stock_code": "600519.XSHG", "base_date": "2026-08-22", "n": "", "direction"）

## ft_get_stk_ah_comparison（AH股对比）

- 状态: ❌ {"error":{"code":"UPSTREAM_UNAVAILABLE","message":"上游服务暂时不可用","retryable":true}}（参数变体已试: [{}]）

## ft_get_stk_code_change（A股代码变更）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","field":"trade_code","message":"参数值不满足约束，字段 （参数变体已试: [{"trade_code": ""}]）

## ft_get_stk_manager_hold（上市公司管理层持股）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","field":"trade_code","message":"参数值不满足约束，字段 （参数变体已试: [{"trade_code": ""}]）

## ft_get_stk_manager_pay（上市公司管理层薪酬）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","field":"trade_code","message":"参数值不满足约束，字段 （参数变体已试: [{"trade_code": ""}]）

## ft_get_stk_managers（上市公司管理层）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","field":"trade_code","message":"参数值不满足约束，字段 （参数变体已试: [{"trade_code": ""}]）

## ft_get_stk_status_change（A股状态变更）

- 参数: {} | 行数: 319
- 字段(5): change_date、change_details、change_type、name、trade_code
- 样例: {"change_date": "19910403", "change_details": "", "change_type": "上市", "name": "平安银行", "trade_code": "000001.SZ"}

## ft_get_stock_institution_holdings（机构持股）

- 状态: ❌ {"error":{"code":"INVALID_TYPE","field":"year","message":"参数类型错误，字段 `year`，请检查 i（参数变体已试: [{"year": "", "report_type": "", "inst_type": ""}]）

## ft_get_stock_institution_holdings_detail（机构持股明细）

- 状态: ❌ {"error":{"code":"INVALID_TYPE","field":"year","message":"参数类型错误，字段 `year`，请检查 i（参数变体已试: [{"stock_code": "600519.XSHG", "year": "", "report_type": "", "inst_type": ""}, {"stock_code": "600519", "year": "", "report_type": "", "inst_type": ""}]）

## ft_get_stock_institution_share_holdings（机构股本持股）

- 状态: ❌ {"error":{"code":"INVALID_TYPE","field":"year","message":"参数类型错误，字段 `year`，请检查 i（参数变体已试: [{"institution_id": "", "year": "", "report_type": "", "invest_type": ""}]）

## ft_get_stock_list（股票列表）

- 参数: {} | 行数: 200
- 字段(2): stock_code、stock_name
- 样例: {"stock_code": "000001.SZ", "stock_name": "平安银行"}

## ft_get_stock_share_handler（股本）

- 参数: {"stock_code": "600519.XSHG", "date": "20260822"} | 行数: 1
- 字段(12): ashare_circ_limit_num、ashare_circ_num、ashare_circ_unlimit_num、bshare_circ_num、bshare_num、bshare_uncirc_num、hshare_num、osshare_num、share_circ_num、stock_code、stock_name、totshare_num
- 样例: {"ashare_circ_limit_num": "0", "ashare_circ_num": "1250081601", "ashare_circ_unlimit_num": "1250081601", "bshare_circ_num": "0", "bshare_num": "0", "bshare_uncirc_num": "0", "hshare_num": "0", "osshare_num": "0", "share_circ_num": "1250081601", "stock_code": "600519.SH", "stock_name": "贵州茅台", "totshare_num": "125008160

## ft_get_yzxdr_detail（一致行动人明细）

- 状态: ❌ {"error":{"code":"INVALID_TYPE","field":"quarter","message":"参数类型错误，字段 `quarter`（参数变体已试: [{"year": "", "quarter": ""}]）

## ft_global_index_daily_kline（全球指数日K线）

- 状态: ❌ empty（参数变体已试: [{"secid": ""}]）

## ft_goodwill_industry（商誉行业）

- 参数: {"date": "20260822"} | 行数: 127
- 字段(6): company_count、goodwill_scale、goodwill_to_net_assets_ratio、industry_name、net_assets、net_profit_scale
- 样例: {"company_count": 65, "goodwill_scale": "32981879898.2200", "goodwill_to_net_assets_ratio": "0.12812935", "industry_name": "IT服务Ⅱ", "net_assets": "257410808979.2800", "net_profit_scale": "-339477573.0000"}

## ft_goodwill_market_overview（商誉市场总览）

- 参数: {} | 行数: 17
- 字段(8): goodwill_impairment、goodwill_scale、goodwill_to_net_assets_ratio、impairment_to_net_assets_ratio、impairment_to_net_profit_ratio、net_assets、net_profit_scale、report_date
- 样例: {"goodwill_impairment": null, "goodwill_scale": "1224218430250.2300", "goodwill_to_net_assets_ratio": "0.02175296", "impairment_to_net_assets_ratio": null, "impairment_to_net_profit_ratio": null, "net_assets": "56278253157394.5000", "net_profit_scale": "1133013378865.3600", "report_date": "2026-03-31 00:00:00"}

## ft_goodwill_predict（商誉预测）

- 状态: ❌ {"error":{"code":"UPSTREAM_REJECTED","message":"上游拒绝处理该请求","retryable":false}}（参数变体已试: [{"date": "20260822"}, {"date": "2026-08-22"}]）

## ft_goodwill_stock_detail（商誉个股明细）

- 参数: {"date": "20260822"} | 行数: 50
- 字段(10): goodwill_previous、goodwill_scale、goodwill_to_net_assets_ratio、net_profit_scale、net_profit_yoy_ratio、notice_date、security_code、security_name、seq、trade_board
- 样例: {"goodwill_previous": "17166195.0300", "goodwill_scale": "17166195.0300", "goodwill_to_net_assets_ratio": "0.01966767", "net_profit_scale": "2974951.1300", "net_profit_yoy_ratio": "-0.41227500", "notice_date": "2026-04-27 00:00:00", "security_code": "920964", "security_name": "润农节水", "seq": 0, "trade_board": "bjs"}

## ft_goodwill_stock_impairment（商誉减值）

- 参数: {"date": "20260822"} | 行数: 50
- 字段(10): goodwill_change、goodwill_impairment_to_net_profit、goodwill_scale、goodwill_to_net_assets_ratio、net_profit_scale、notice_date、security_code、security_name、seq、trade_board
- 样例: {"goodwill_change": null, "goodwill_impairment_to_net_profit": null, "goodwill_scale": "17166195.0300", "goodwill_to_net_assets_ratio": "0.01966767", "net_profit_scale": "2974951.1300", "notice_date": "2026-04-27 00:00:00", "security_code": "920964", "security_name": "润农节水", "seq": 0, "trade_board": "bjs"}

## ft_income（A股利润表）

- 状态: ❌ {"error":{"code":"MISSING_PARAMETER","details":{"required_any_of":[["stock_code"（参数变体已试: [{}]）

## ft_index_candlesticks（指数K线）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","details":{"constraint":"enum:Minute/Day/Wee（参数变体已试: [{"symbol": "600519.XSHG", "interval_unit": "", "until_ts_millis": ""}, {"symbol": "600519", "interval_unit": "", "until_ts_millis": ""}]）

## ft_index_candlesticks_batch（批量指数K线）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","details":{"constraint":"enum:Minute/Day/Wee（参数变体已试: [{"symbols": "600519.XSHG", "interval_unit": "", "until_ts_millis": ""}, {"symbols": "600519", "interval_unit": "", "until_ts_millis": ""}]）

## ft_index_description_all（指数基础信息）

- 参数: {} | 行数: 100
- 字段(6): full_name、name、pb、pe_ttm、ps_ttm、symbol
- 样例: {"full_name": "中证方正富邦保险主题指数", "name": "保险主题", "pb": 0.8227, "pe_ttm": 7.506, "ps_ttm": 2.2, "symbol": "399809.XSHE"}

## ft_index_description_list_handler（中证指数描述列表）

- 参数: {} | 行数: 20
- 字段(5): index_code、index_intro、index_name、index_orig、url_hash
- 样例: {"index_code": "000001", "index_intro": "上证综合指数由在上海证券交易所上市的符合条件的股票与存托凭证组成样本，反映上海证券交易所上市公司的整体表现。", "index_name": "上证综合指数", "index_orig": "中证指数", "url_hash": "f933ef8ddef930cda490af8e9f6219cc8f02259a99c8cd61f4c2fb095a1664c0"}

## ft_index_weight_list_handler（指数权重列表）

- 状态: ❌ {"error":{"code":"UPSTREAM_REJECTED","message":"上游拒绝处理该请求","retryable":false}}（参数变体已试: [{"index_code": ""}]）

## ft_index_weight_summary_handler（指数权重汇总）

- 状态: ❌ {"error":{"code":"UPSTREAM_REJECTED","message":"上游拒绝处理该请求","retryable":false}}（参数变体已试: [{"index_code": ""}]）

## ft_limit_down_pool（跌停池）

- 参数: {} | 行数: 9
- 字段(10): last_limit_down_time、limit_down_break、limit_down_break_count、limit_down_enter、limit_down_price、limit_down_seal_value、ready、status、symbol、trade_date
- 样例: {"last_limit_down_time": "09:30:57", "limit_down_break": ["09:31:33"], "limit_down_break_count": 1, "limit_down_enter": ["09:30:57"], "limit_down_price": "5.0400", "limit_down_seal_value": "0", "ready": true, "status": "normal", "symbol": "000931.XSHE", "trade_date": "20260825"}

## ft_limit_event_timeline_3s（涨跌停事件时间线）

- 参数: {} | 行数: 20
- 字段(15): first_limit_up_time、last_limit_down_time、limit_down_break、limit_down_break_count、limit_down_enter、limit_down_price、limit_down_seal_value、limit_up_break、limit_up_break_count、limit_up_enter、limit_up_price、ready、status、symbol、trade_date
- 样例: {"first_limit_up_time": null, "last_limit_down_time": null, "limit_down_break": [], "limit_down_break_count": 0, "limit_down_enter": [], "limit_down_price": "0.0000", "limit_down_seal_value": "0", "limit_up_break": [], "limit_up_break_count": 0, "limit_up_enter": [], "limit_up_price": "0.0000", "ready": true}

## ft_limit_up_break_pool（炸板池）

- 参数: {} | 行数: 24
- 字段(9): first_limit_up_time、limit_up_break、limit_up_break_count、limit_up_enter、limit_up_price、ready、status、symbol、trade_date
- 样例: {"first_limit_up_time": "09:31:21", "limit_up_break": ["10:37:09"], "limit_up_break_count": 1, "limit_up_enter": ["09:31:21"], "limit_up_price": "3.3800", "ready": true, "status": "normal", "symbol": "000523.XSHE", "trade_date": "20260825"}

## ft_limit_up_pool（涨停池）

- 参数: {} | 行数: 50
- 字段(9): first_limit_up_time、limit_up_break、limit_up_break_count、limit_up_enter、limit_up_price、ready、status、symbol、trade_date
- 样例: {"first_limit_up_time": "09:25:00", "limit_up_break": ["09:58:09", "14:57:00"], "limit_up_break_count": 2, "limit_up_enter": ["09:25:00", "09:58:12", "14:57:09"], "limit_up_price": "8.6000", "ready": true, "status": "limit_up", "symbol": "000017.XSHE", "trade_date": "20260825"}

## ft_limit_up_pool_yesterday（昨日涨停池）

- 参数: {} | 行数: 64
- 字段(9): first_limit_up_time、limit_up_break、limit_up_break_count、limit_up_enter、limit_up_price、ready、status、symbol、trade_date
- 样例: {"first_limit_up_time": "09:25:00", "limit_up_break": ["14:57:00"], "limit_up_break_count": 1, "limit_up_enter": ["09:25:00", "14:57:09"], "limit_up_price": "7.8200", "ready": true, "status": "limit_up", "symbol": "000017.XSHE", "trade_date": "20260824"}

## ft_lpr_monthly（LPR）

- 参数: {} | 行数: 200
- 字段(3): date、lpr_1y、lpr_5y
- 样例: {"date": "2026-07-20", "lpr_1y": "3.0000", "lpr_5y": "3.5000"}

## ft_major_contract（重大合同）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","message":"时间范围不能超过 3 天","retryable":false}}（参数变体已试: [{"start_date": "20260818", "end_date": "20260825"}, {"start_date": "20260818", "end_date": "2026-08-25"}]）

## ft_major_contract_by_symbol（重大合同按标的）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","message":"字段 `symbol` 必须是有效的 6 位 A 股股票代码，支持（参数变体已试: [{"symbol": "600519.XSHG"}, {"symbol": "600519"}]）

## ft_major_contract_summary（重大合同汇总）

- 参数: {} | 行数: 50
- 字段(9): contract_count、last_year_revenue、latest_revenue、prev_year_total、revenue_ratio、security_code、security_short_name、seq、total_amount
- 样例: {"contract_count": "41", "last_year_revenue": null, "latest_revenue": "496605714000.0000", "prev_year_total": "50215220000.0000", "revenue_ratio": null, "security_code": "601390", "security_short_name": "中国中铁", "seq": 0, "total_amount": "149550970000.0000"}

## ft_margin_trading_details（融资融券明细）

- 参数: {} | 行数: 50
- 字段(10): date、margin_trading_balance、margin_trading_buying_amount、margin_trading_repayment_amount、securities_lending_balance_volume、securities_lending_repayment_volume、securities_lending_selling_volume、symbol、symbol_name、total_balance
- 样例: {"date": "2026-08-24", "margin_trading_balance": 32800918181, "margin_trading_buying_amount": 4572901402, "margin_trading_repayment_amount": 3751292867, "securities_lending_balance_volume": 195533, "securities_lending_repayment_volume": "18100", "securities_lending_selling_volume": 27300, "symbol": "300308.SZ", "symbol

## ft_member_build_process（会员建仓过程）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","message":"字段 `exchange` 不能为空","retryable":f（参数变体已试: [{"exchange": "", "member_name": "", "instrument_id": ""}]）

## ft_member_position_ranking（会员持仓排名）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","message":"字段 `exchange` 不能为空","retryable":f（参数变体已试: [{"exchange": "", "instrument_id": "", "trade_date": "20260822", "direction": ""}, {"exchange": "", "instrument_id": "", "trade_date": "2026-08-22", "direction"）

## ft_northbound（北向资金交易）

- 参数: {"date": "20260822"} | 行数: 1
- 字段(4): channels、currency、date、total_amount
- 样例: {"channels": {"SH": {"amount": "0", "trade_count": 0}, "SZ": {"amount": "0", "trade_count": 0}}, "currency": "CNY", "date": "20260822", "total_amount": "0"}

## ft_performance_forecasts_paginated（业绩预告）

- 状态: ❌ {"error":{"code":"MISSING_PARAMETER","details":{"required_any_of":[["stock_code"（参数变体已试: [{}]）

## ft_reserve_ratio_monthly（存款准备金率）

- 参数: {} | 行数: 318
- 字段(3): date、reserve_ratio_large、reserve_ratio_small_medium
- 样例: {"date": "2026年06月", "reserve_ratio_large": "9.0000", "reserve_ratio_small_medium": "6.0000"}

## ft_risk_warning_stock_quotes（风险警示股行情）

- 参数: {"date": "20260822"} | 行数: 10
- 字段(44): amplitude、asks、avg、bid_ask_ratio、bids、buy_orders、buy_volume、canceled_buy_orders、canceled_sell_orders、change、change_rate、change_rate_day10、change_rate_day120、change_rate_day20、change_rate_day5、change_rate_day60、change_rate_ytd、close、cum_adjust_factor、down_limited、filled_buy_orders、filled_sell_orders、high、limit_down、limit_up、low、market_cap、non_tradable_a_shares、open、prev_close、risk_type、sell_orders、sell_volume、shares、stock_code、stock_name、tradable_a_market_cap、tradable_a_shares、trades、ts_nanos、turnover、turnover_rate、up_limited、volume
- 样例: {"amplitude": 0.026143790849673203, "asks": [{"price": "1.5400", "volume": 301800}, {"price": "1.5500", "volume": 1336400}, {"price": "1.5600", "volume": 671700}, {"price": "1.5700", "volume": 538100}, {"price": "1.5800", "volume": 779300}, {"price": "1.5900", "volume": 221000}, {"price": "1.6000", "volume": 499600}, {

## ft_risk_warning_stocks（风险警示股）

- 参数: {"date": "20260822"} | 行数: 203
- 字段(3): risk_type、stock_code、stock_name
- 样例: {"risk_type": "*ST", "stock_code": "000010", "stock_name": "*ST美丽"}

## ft_semantic_search_news_handler（新闻语义搜索）

- 状态: ❌ {"error":{"code":"UPSTREAM_REJECTED","message":"上游拒绝处理该请求","retryable":false}}（参数变体已试: [{"query": ""}]）

## ft_sh_hk_stock_connect_members（沪股通成份）

- 参数: {} | 行数: 200
- 字段(1): symbol
- 样例: {"symbol": "600004.SH"}

## ft_shareholders_meeting（股东大会）

- 参数: {} | 行数: 50
- 字段(12): decision_notice_date、equity_record_date、meeting_title、notice_date、onsite_record_date、proposal、security_code、security_name_abbr、serial_num、start_adjust_date、web_end_date、web_start_date
- 样例: {"decision_notice_date": null, "equity_record_date": "2026-09-03", "meeting_title": "2026年第2次临时股东大会", "notice_date": "2026-08-25", "onsite_record_date": null, "proposal": "1、《关于使用部分闲置募集资金进行现金管理的议案》\r\n2、《关于使用闲置自有资金进行委托理财的议案》", "security_code": "301565", "security_name_abbr": "中仑新材", "serial_num": "241753", "start_adjus

## ft_southbound（南向资金交易）

- 参数: {"date": "20260822"} | 行数: 1
- 字段(4): channels、currency、date、total
- 样例: {"channels": {"SH_HK": {"buy_amount": "0", "net_buy_amount": "0", "sell_amount": "0", "trade_count": 0}, "SZ_HK": {"buy_amount": "0", "net_buy_amount": "0", "sell_amount": "0", "trade_count": 0}}, "currency": "HKD", "date": "20260822", "total": {"buy_amount": "0", "net_buy_amount": "0", "sell_amount": "0", "trade_count

## ft_stk_limit（涨跌停价）

- 参数: {} | 行数: 50
- 字段(6): down_limit、instrument_type、pre_close、trade_date、ts_code、up_limit
- 样例: {"down_limit": "85.121", "instrument_type": "cb", "pre_close": "106.401", "trade_date": 20260825, "ts_code": "110075.SH", "up_limit": "127.681"}

## ft_stk_premarket（盘前数据）

- 参数: {} | 行数: 50
- 字段(10): ashare_circ_num、down_limit、float_mv、pre_close、price、total_mv、totshare_num、trade_date、ts_code、up_limit
- 样例: {"ashare_circ_num": "19405918198", "down_limit": "10.4", "float_mv": "224332414368.88", "pre_close": "11.56", "price": "11.56", "total_mv": "224332414368.88", "totshare_num": "19405918198", "trade_date": 20260825, "ts_code": "000001.SZ", "up_limit": "12.72"}

## ft_stock_adjust_factor（股票复权因子）

- 参数: {} | 行数: 50
- 字段(4): adj_factor、ex_adj_factor、symbol、trade_date
- 样例: {"adj_factor": 1.0, "ex_adj_factor": 150.726, "symbol": "000001.SZ", "trade_date": "20260825"}

## ft_stock_announcements（公告列表）

- 状态: ❌ {"error":{"code":"INVALID_TYPE","field":"page","message":"参数类型错误，字段 `page`，请检查 i（参数变体已试: [{"type": "", "page": "", "page_size": ""}]）

## ft_stock_candlesticks（股票K线）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","details":{"constraint":"enum:Minute/Day/Wee（参数变体已试: [{"symbol": "600519.XSHG", "interval_unit": "", "until_ts_millis": ""}, {"symbol": "600519", "interval_unit": "", "until_ts_millis": ""}]）

## ft_stock_candlesticks_batch（批量股票K线）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","details":{"constraint":"enum:Minute/Day/Wee（参数变体已试: [{"symbols": "600519.XSHG", "interval_unit": "", "until_ts_millis": ""}, {"symbols": "600519", "interval_unit": "", "until_ts_millis": ""}]）

## ft_stock_capital_flows_paginated（股票资金流向）

- 参数: {} | 行数: 50
- 字段(8): net_inflow_extra_large、net_inflow_large、net_inflow_main、net_inflow_medium、net_inflow_small、symbol、symbol_name、ts_nanos
- 样例: {"net_inflow_extra_large": "1505559951.17", "net_inflow_large": "731358838.97", "net_inflow_main": "2236918790.14", "net_inflow_medium": "-2146431496.46", "net_inflow_small": "-90487293.68", "symbol": "688835.SH", "symbol_name": "N高凯", "ts_nanos": 1787643000000000000}

## ft_stock_comment_desire_em（千股千评意愿度）

- 参数: {"symbol": "600519"} | 行数: 65
- 字段(6): participation_wish、participation_wish_5days、participation_wish_5days_change、participation_wish_change、security_code、trade_date
- 样例: {"participation_wish": "42.5700", "participation_wish_5days": "44.3300", "participation_wish_5days_change": "-1.5100", "participation_wish_change": "-9.0300", "security_code": "600519", "trade_date": "2026-05-26"}

## ft_stock_comment_em（千股千评）

- 参数: {} | 行数: 50
- 字段(13): change_rate、close_price、focus、org_participate、pe_dynamic、prime_cost、rank、security_code、security_name_abbr、seq、total_score、trade_date、turnover_rate
- 样例: {"change_rate": "0.25950000", "close_price": "11.5900", "focus": "91.60000000", "org_participate": "0.42594560", "pe_dynamic": "4.37645143", "prime_cost": "11.581709600891", "rank": "438", "security_code": "000001", "security_name_abbr": "平安银行", "seq": 0, "total_score": "74.87717295", "trade_date": "2026-08-25"}

## ft_stock_comment_focus_em（千股千评关注度）

- 参数: {"symbol": "600519"} | 行数: 65
- 字段(6): close_price、market_focus、market_focus_change、market_focus_rank、total_market、trade_date
- 样例: {"close_price": "1273.3800", "market_focus": "93.60000000", "market_focus_change": "1", "market_focus_rank": "58", "total_market": "5207", "trade_date": "2026-05-26"}

## ft_stock_comment_org_participate_em（机构参与度）

- 参数: {"symbol": "600519"} | 行数: 64
- 字段(2): org_participate、trade_date
- 样例: {"org_participate": "0.54720920", "trade_date": "2026-05-26"}

## ft_stock_comment_score_em（千股千评评分）

- 参数: {"symbol": "600519"} | 行数: 65
- 字段(2): diagnose_date、total_score
- 样例: {"diagnose_date": "2026-05-26", "total_score": "73.14689601"}

## ft_stock_filter（股票筛选）

- 参数: {} | 行数: 50
- 字段(21): amplitude、board、change、change_rate、change_rate_day10、change_rate_day20、change_rate_day5、change_rate_day60、change_rate_ytd、close、high、low、open、prev_close、symbol、symbol_id、symbol_name、ts_nanos、turnover、type、volume
- 样例: {"amplitude": 0.009515570934256055, "board": "sz", "change": "0.0300", "change_rate": 0.0025951557093425604, "change_rate_day10": 0.02930728241563055, "change_rate_day20": 0.03482142857142857, "change_rate_day5": 0.048868778280542986, "change_rate_day60": 0.090310442144873, "change_rate_ytd": 0.04039497307001795, "clos

## ft_stock_float_holders（十大流通股东）

- 状态: ❌ {"error":{"code":"MISSING_PARAMETER","details":{"required_any_of":[["stock_code"（参数变体已试: [{}]）

## ft_stock_ggcg_em_handler（东方财富股东增减持）

- 参数: {} | 行数: 50
- 字段(16): after_holder_num、change_free_ratio、change_num、change_num_symbol、change_total_ratio、end_date、free_shares、free_shares_ratio、hold_ratio、holder_name、latest_price、notice_date、price_change_rate、start_date、stock_code、stock_name
- 样例: {"after_holder_num": null, "change_free_ratio": "0.280000", "change_num": "72.140000", "change_num_symbol": "72.140000", "change_total_ratio": "0.210972", "end_date": "2026-08-24", "free_shares": null, "free_shares_ratio": null, "hold_ratio": null, "holder_name": "游景超", "latest_price": "9.0200", "notice_date": "2026-08

## ft_stock_ggmx_buy_ranking_handler（董监高增持排名）

- 参数: {} | 行数: 50
- 字段(9): latestChangeDate、latestPrice、priceChangeRate、startDate、stockCode、stockName、timeRange、totalAmountWan、totalShares
- 样例: {"latestChangeDate": "2026-07-29", "latestPrice": "33.0", "priceChangeRate": "-1.43", "startDate": "2026-07-25", "stockCode": "920065", "stockName": "千岸科技", "timeRange": "1m", "totalAmountWan": "18458.94", "totalShares": "7596270.0"}

## ft_stock_ggmx_handler（董监高持股变动）

- 参数: {} | 行数: 50
- 字段(26): avg_price、change_amount、change_date、change_direction、change_quantity、change_ratio、change_reason、change_shares、changer、close_price、crawl_batch_ts、crawl_date、data_time、executive_name、notice_date、position、price_change、quote_change、quote_price、register_date、relation、shares_after、source、stock_code、stock_name、total_share
- 样例: {"avg_price": "11.71", "change_amount": "9996827.0", "change_date": "2026-08-24", "change_direction": "增持", "change_quantity": "853700.0", "change_ratio": "0.46310543", "change_reason": "集中竞价", "change_shares": "853700.0", "changer": "蒲忠杰", "close_price": "11.71", "crawl_batch_ts": "2026-08-24 22:53:00", "crawl_date": 

## ft_stock_ggmx_sell_ranking_handler（董监高减持排名）

- 参数: {} | 行数: 50
- 字段(9): latestChangeDate、latestPrice、priceChangeRate、startDate、stockCode、stockName、timeRange、totalAmountWan、totalShares
- 样例: {"latestChangeDate": "2026-08-14", "latestPrice": "12.64", "priceChangeRate": "-2.02", "startDate": "2026-07-25", "stockCode": "688599", "stockName": "天合光能", "timeRange": "1m", "totalAmountWan": "45449.9", "totalShares": "36100000.0"}

## ft_stock_holders（十大股东）

- 状态: ❌ {"error":{"code":"MISSING_PARAMETER","details":{"required_any_of":[["stock_code"（参数变体已试: [{}]）

## ft_stock_holders_number（股东人数）

- 状态: ❌ {"error":{"code":"MISSING_PARAMETER","details":{"required_any_of":[["stock_code"（参数变体已试: [{}]）

## ft_stock_intraday_auction_volume（连续竞价成交量）

- 参数: {} | 行数: 50
- 字段(5): bjse、overall、ts_millis、xshe、xshg
- 样例: {"bjse": {"turnover": "79552903", "turnover_ratio": 0.0063820213126158055, "volume": 3385759, "volume_ratio": 0.00596370539497312}, "overall": {"turnover": "14618808172.73", "turnover_ratio": 0.007927376590729673, "volume": 851309650, "volume_ratio": 0.0081148939036598}, "ts_millis": 1787621400000, "xshe": {"turnover":

## ft_stock_intraday_auction_volume_symbol（单标的连续竞价成交量）

- 参数: {"symbol": "600519.XSHG"} | 行数: 50
- 字段(5): ts_millis、turnover、turnover_ratio、volume、volume_ratio
- 样例: {"ts_millis": 1787621400000, "turnover": "19809539", "turnover_ratio": 0.00718380569740912, "volume": 15100, "volume_ratio": 0.007152608238857326}

## ft_stock_ipos（股票IPO）

- 参数: {} | 行数: 50
- 字段(11): industry_pe、listing_date、max_subscription_shares、online_shares、pe、price、shares、subscription_date、subscription_symbol_id、symbol、symbol_name
- 样例: {"industry_pe": null, "listing_date": null, "max_subscription_shares": 6500, "online_shares": 6885500, "pe": null, "price": null, "shares": 43035173, "subscription_date": "2026-09-02", "subscription_symbol_id": "787801", "symbol": "688801.SH", "symbol_name": "燧原科技"}

## ft_stock_pledge_detail（股权质押明细）

- 状态: ❌ {"error":{"code":"UPSTREAM_REJECTED","message":"上游拒绝处理该请求","retryable":false}}（参数变体已试: [{}]）

## ft_stock_pledge_summary（股权质押汇总）

- 参数: {} | 行数: 50
- 字段(8): hs300_index、hs300_week_change_ratio、pledge_company_count、pledge_deal_count、pledge_total_market_value、pledge_total_ratio、pledge_total_shares、trade_date
- 样例: {"hs300_index": "4665.8812", "hs300_week_change_ratio": "-0.6082796092779186596729980300", "pledge_company_count": 2218, "pledge_deal_count": 13485, "pledge_total_market_value": "2704366966456.0000", "pledge_total_ratio": "0", "pledge_total_shares": "282643894500.00", "trade_date": "2026-08-14"}

## ft_stock_rating_top5（非凸股票评级Top5）

- 状态: ❌ {"error":{"code":"UPSTREAM_UNAVAILABLE","message":"上游服务暂时不可用","retryable":true}}（参数变体已试: [{"date": "20260822"}, {"date": "2026-08-22"}]）

## ft_stock_reports（研报列表）

- 状态: ❌ {"error":{"code":"INVALID_TYPE","field":"page","message":"参数类型错误，字段 `page`，请检查 i（参数变体已试: [{"type": "", "page": "", "page_size": ""}]）

## ft_stock_share_chg（股东增减持）

- 状态: ❌ {"error":{"code":"MISSING_PARAMETER","details":{"required_any_of":[["stock_code"（参数变体已试: [{}]）

## ft_stock_signal_latest_snapshot（信号最新快照）

- 参数: {} | 行数: 50
- 字段(8): close_price、code、latest_trade_date、signal_detail、signal_name、signal_type、symbol、volume
- 样例: {"close_price": "11.5900", "code": "000001", "latest_trade_date": "2026-08-25", "signal_detail": "连续上涨5天", "signal_name": "连续上涨", "signal_type": "consecutive_up", "symbol": "000001.XSHE", "volume": "99488115.00"}

## ft_stock_unlock_by_date_handler（限售解禁按日期）

- 参数: {"start_date": "20260818", "end_date": "20260825"} | 行数: 31
- 字段(17): a20Adjchrate、ableFreeShares、b20Adjchrate、crawlDate、currentFreeShares、freeRatio、freeSharesType、holderCount、holders、liftMarketCap、newPrice、nonFreeShares、source、stockCode、stockName、totalRatio、unlockDate
- 样例: {"a20Adjchrate": "2.28", "ableFreeShares": "603.99", "b20Adjchrate": "15.85903084", "crawlDate": "20260825", "currentFreeShares": "603.99", "freeRatio": "0.02046860308", "freeSharesType": "股权激励限售股份", "holderCount": "5", "holders": [{"actualListedShares": "3219900.0", "addListingCap": "17323062.0", "addListingShares": "

## ft_stock_unlock_handler（限售解禁）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","message":"字段 `stock_code` 必须是有效的 6 位 A 股股票代（参数变体已试: [{"stock_code": "600519.XSHG"}, {"stock_code": "600519"}]）

## ft_suspension_list（停牌列表）

- 参数: {} | 行数: 4
- 字段(4): resume_time、suspend_time、suspension_type、symbol
- 样例: {"resume_time": null, "suspend_time": null, "suspension_type": "full-day", "symbol": "000016.XSHE"}

## ft_sw_industry_constituent_history（申万行业成份股历史）

- 状态: ❌ empty（参数变体已试: [{"industry_code": ""}]）

## ft_sw_industry_daily_metrics（申万行业日度指标）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","field":"end_date","message":"参数值不满足约束，字段 `e（参数变体已试: [{"start_date": "20260818", "end_date": "20260825", "industry_code": ""}, {"start_date": "20260818", "end_date": "2026-08-25", "industry_code": ""}]）

## ft_sw_industry_overview（申万行业总览）

- 状态: ❌ {"error":{"code":"UPSTREAM_REJECTED","message":"上游拒绝处理该请求","retryable":false}}（参数变体已试: [{"date": "20260822"}, {"date": "2026-08-22"}]）

## ft_sz_hk_stock_connect_members（深股通成份）

- 参数: {} | 行数: 200
- 字段(1): symbol
- 样例: {"symbol": "000006.SZ"}

## ft_tax_revenue_monthly（税收）

- 参数: {} | 行数: 50
- 字段(6): cumulative_revenue、mom_growth、month、monthly_revenue、monthly_yoy_growth、yoy_growth
- 样例: {"cumulative_revenue": "97865.0000", "mom_growth": "5.0138", "month": "2026年06月", "monthly_revenue": "15248.0000", "monthly_yoy_growth": "10.8220", "yoy_growth": "5.3000"}

## ft_ths_all_board_kline（同花顺全板块K线）

- 参数: {} | 行数: 50
- 字段(9): board_code、board_name、close、date、high、low、module、open、volume
- 样例: {"board_code": "881101", "board_name": "种植业与林业", "close": "939.32", "date": "2007-08-01", "high": "1001.523", "low": "939.32", "module": "industry", "open": "1001.523", "volume": "195916030"}

## ft_ths_board_kline（同花顺板块K线）

- 状态: ❌ {"error":{"code":"UPSTREAM_UNAVAILABLE","message":"上游服务暂时不可用","retryable":true}}（参数变体已试: [{"board_code": ""}]）

## ft_ths_board_list（同花顺板块列表）

- 参数: {} | 行数: 493
- 字段(3): code、module、name
- 样例: {"code": "886056", "module": "concept", "name": "阿尔茨海默概念"}

## ft_type_reports（研报分类）

- 状态: ❌ {"error":{"code":"INVALID_TYPE","field":"page","message":"参数类型错误，字段 `page`，请检查 i（参数变体已试: [{"rept_type": "", "start_date": "20260818", "page": "", "page_size": ""}, {"rept_type": "", "start_date": "2026-08-18", "page": "", "page_size": ""}]）

## ft_wallstreetcn_financial_calendar（华尔街见闻财经日历）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","message":"时间范围不能超过 3 天","retryable":false}}（参数变体已试: [{"start_date": "20260818", "end_date": "20260825"}, {"start_date": "20260818", "end_date": "2026-08-25"}]）

## ft_xueqiu_rank（雪球股票排名）

- 参数: {} | 行数: 20
- 字段(6): latest_price、metric_value、normalized_symbol、rank_no、raw_symbol、stock_name
- 样例: {"latest_price": "602.800000", "metric_value": "42263.000000", "normalized_symbol": "688836", "rank_no": 1, "raw_symbol": "SH688836", "stock_name": "C宇树-W"}

## intraday_kline（分时与分钟 K 线）

- 状态: ❌ {"error":{"code":"MISSING_PARAMETER","field":"symbol","message":"缺少必填或条件必填参数，字段 （参数变体已试: [{}]）

## report_announcement_list（公告列表）

- 参数: {"date": "20260822"} | 行数: 50
- 字段(16): adjunct_size、adjunct_type、announcement_id、announcement_time、announcement_title、column_type、created_at、id、plate、processed_at、retry_count、sec_code、sec_name、status、updated_at、url_hash
- 样例: {"adjunct_size": 132, "adjunct_type": "PDF", "announcement_id": "1225493805", "announcement_time": "2026-08-22 08:00:00", "announcement_title": "2026年半年度报告摘要", "column_type": "stock", "created_at": "2026-08-22 16:34:54", "id": 1008572, "plate": "szmb", "processed_at": "2026-08-22 16:35:03", "retry_count": 0, "sec_code"

## report_announcement_summary（公告摘要）

- 状态: ❌ {"error":{"code":"INVALID_ARGUMENT","message":"announcement_id 必填且非空（取自 list 工具返（参数变体已试: [{"announcement_id": ""}]）
