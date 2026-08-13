# AxData 666 字段补齐矩阵（附录——主字典 12.14 的详细实证层）

> 2026-08-10 从主字典迁移（字典架构重构：主字典=决策层，附录=实证层）
> 内容：AxData 256 接口揭示、字典未记录的 666 个字段，按源组织（通达信/扩展/东财/巨潮/腾讯/新浪/财联社/开盘红/交易所）
> 每字段含：来源接口 + 含义（axdata RequestField.description）
> 使用方法：查字段先看主字典（已录字段/结论），未找到再查本附录（补录字段）

### 12.14 多源字段补齐矩阵（AxData 线索核对，2026-08-10）🆕
> **目的**：AxData 256 接口揭示的字段全部来自已知公开源（TDX/东财/腾讯/新浪/巨潮/财联社/开盘红/交易所）——
> 不引入 axdata 本体，用已知源充实字典未知字段。
> **方法**：clone electkismet/AxData@main，提取各 sources/*/catalog.py 的 RequestField 定义（256 接口 / 3334 字段），
> 与字典全文逐字段比对（按源）。
> **规则**：① 同源同字段已在字典 → 印证（不补录，见下各源『印证数』）② 字典未记录且有业务价值的字段 → 补录备用
> **印证统计**（axdata 字段 vs 字典原有记录，同源同字段）：通达信 492 / 通达信扩展 120 / 交易所 18 / 东财 130 / 巨潮 104 / 腾讯 42 / 新浪 181 / 财联社 66 / 开盘红 82 —— 共 **1235 字段已由字典记录印证**（axdata 字段定义与项目已知字段口径一致）
> **补录统计**：本矩阵共补录 **666 字段**（过滤命名规范/元数据/低价值字段后）
> **过滤**：纯命名规范字段（instrument_id/symbol/tdx_code 等）、通用元数据（source_*/sequence/raw_* 等）不录入。
#### 12.14.1 通达信（TDX TCP/本地）（补录 196 字段）
| 字段 | 接口 | 含义 |
|:---|:---|:---|
| accounts_payable | stock_financial_statement_tdx | 应付账款。 |
| accounts_receivable | stock_balance_summary_tdx | Accounts receivable, unit: yuan. |
| action | stock_regulatory_actions_tdx | 监管措施。 |
| actual_date | stock_governance_guarantees_tdx | 实际发生日。 |
| after_tax_profit | stock_profit_cashflow_summary_tdx | After-tax profit, unit: yuan. |
| align_flag | stock_forecast_consensus_tdx | 年份对齐标记。 |
| allocated_amount | stock_private_placement_allocations_tdx | 获配金额，单位：元。 |
| allocated_volume | stock_private_placement_allocations_tdx | 获配数量，单位：股。 |
| allocator | stock_private_placement_allocations_tdx | 获配机构。 |
| analyst | stock_research_reports_tdx | 研究员。 |
| attachment | stock_research_reports_tdx | 研报附件标识。 |
| avg_main_amount | concept_capital_flow_tdx | 平均主力资金。 |
| avg_main_buy_amount | concept_capital_flow_tdx | 平均主买资金。 |
| band_value_1 | stock_valuation_band_tdx | 当前 PE 或 PB 指标值。 |
| band_value_2 | stock_valuation_band_tdx | 通道辅助值 2，源端用于绘制 Band。 |
| band_value_3 | stock_valuation_band_tdx | 通道辅助值 3，源端用于绘制 Band。 |
| benchmark_value | stock_dividend_metrics_tdx | 对照值。 |
| board_code | concept_control_series_tdx | 所属板块代码。 |
| board_date | stock_dividend_history_tdx | 董事会日期。 |
| board_market | concept_related_boards_tdx | 板块市场。 |
| board_name | concept_capital_flow_tdx | 题材或行业名。 |
| bps | stock_finance_summary_tdx | Book value per share, unit: yuan/share. |
| buy_count | stock_analyst_rating_tdx | 买入家数。 |
| c1 | stock_capital_changes_tdx | Event parameter slot 1; meaning depends on category_raw. |
| c2 | stock_capital_changes_tdx | Event parameter slot 2; meaning depends on category_raw. |
| c3 | stock_capital_changes_tdx | Event parameter slot 3; meaning depends on category_raw. |
| c4 | stock_capital_changes_tdx | Event parameter slot 4; meaning depends on category_raw. |
| capital_reserve | stock_balance_summary_tdx | Capital reserve, unit: yuan. |
| case_date | stock_violation_cases_tdx | 立案日期。 |
| case_type | stock_violation_cases_tdx | 立案类型。 |
| cash | stock_financial_statement_tdx | 货币资金。 |
| cash_dividend_total | stock_dividend_metrics_tdx | 累计现金分红。 |
| change_direction | stock_company_profile_tdx | 指数调入/调出方向。 |
| change_pct_20d | concept_constituent_comparison_tdx | 20 日涨幅，单位：%。 |
| change_pct_3d | concept_constituent_comparison_tdx | 3 日涨幅，单位：%。 |
| change_pct_5d | concept_constituent_comparison_tdx | 5 日涨幅，单位：%。 |
| change_pct_60d | concept_constituent_comparison_tdx | 60 日涨幅，单位：%。 |
| change_volume | stock_northbound_holding_tdx | 变动股数，单位：股。 |
| channel_type | stock_northbound_holding_tdx | 当前持股记录对应的交易通道；有记录的深市标为深股通，沪市标为沪股通。 |
| compare_group | stock_financial_diagnosis_tdx | 对比行业或板块。 |
| control_ratio_pct | concept_control_ranking_tdx | 控盘比例，单位：%。 |
| cost | stock_business_composition_tdx | 主营成本。 |
| cost_ratio_pct | stock_business_composition_tdx | 成本占比，单位：%。 |
| created_date | stock_topic_exposure_tdx | 创建日期。 |
| creation_change_pct | stock_event_drivers_tdx | 创建日涨跌幅，单位：%。 |
| currency | stock_governance_guarantees_tdx | 币种。 |
| current_liabilities | stock_balance_summary_tdx | Current liabilities, unit: yuan. |
| current_price | stock_analyst_rating_tdx | 当前价。 |
| decision | stock_violation_cases_tdx | 处罚决定，源端可能为空。 |
| detail_text | stock_event_drivers_tdx | 详情正文；include_detail=true 时补充。 |
| dimension | stock_business_composition_tdx | 分类方式。 |
| effective_date | stock_company_profile_tdx | 指数调整日期。 |
| effective_date_change_pct | stock_company_profile_tdx | 调整日涨跌幅，单位：%。 |
| end_time | stock_disclosure_feed_tdx | 路演结束时间；非路演为空。 |
| eps_year1 | stock_forecast_consensus_tdx | 未来第一年预测每股收益。 |
| eps_year2 | stock_forecast_consensus_tdx | 未来第二年预测每股收益。 |
| eps_year3 | stock_forecast_consensus_tdx | 未来第三年预测每股收益。 |
| event_name | stock_event_drivers_tdx | 事件名称，不等同于涨停原因。 |
| event_nature | stock_event_drivers_tdx | 事件性质。 |
| event_type | stock_equity_financing_events_tdx | 事件类型。 |
| ex_dividend_date | stock_dividend_history_tdx | 除权派息日。 |
| first_close | stock_company_profile_tdx | 首日收盘价，单位：元。 |
| first_open | stock_company_profile_tdx | 首日开盘价，单位：元。 |
| float_market_cap | concept_constituent_comparison_tdx | 流通市值。 |
| forecast_institution_count | stock_forecast_consensus_tdx | 预测机构数量。 |
| forecast_start_year | stock_forecast_consensus_tdx | 预测起始年份。 |
| gross_margin_pct | stock_business_composition_tdx | 毛利率，单位：%。 |
| gross_profit | stock_business_composition_tdx | 毛利。 |
| group_code | stock_topic_exposure_tdx | 源端分组类别码；主题题材可能为空。 |
| guarantee_type | stock_governance_guarantees_tdx | 担保类型。 |
| guaranteed_party | stock_governance_guarantees_tdx | 被担保方。 |
| guarantor | stock_governance_guarantees_tdx | 担保方。 |
| has_detail | stock_event_drivers_tdx | 是否有详情正文。 |
| holding_ratio_pct | stock_northbound_holding_tdx | 持股比例，单位：%。 |
| holding_volume | stock_northbound_holding_tdx | 持股数量，单位：股。 |
| industry_raw | stock_finance_profile_tdx | TDX raw industry code carried by the finance snapshot. |
| institution_holding_ratio_pct | stock_institution_holding_tdx | 机构持仓比例，单位：%。 |
| institution_type | stock_private_placement_allocations_tdx | 机构类型。 |
| inventory | stock_balance_summary_tdx | Inventory, unit: yuan. |
| investment_income | stock_profit_cashflow_summary_tdx | Investment income, unit: yuan. |
| is_completed | stock_governance_guarantees_tdx | 是否履行完毕。 |
| is_related_party | stock_governance_guarantees_tdx | 是否关联交易。 |
| issue_date | stock_disclosure_feed_tdx | 发布时间或公告日期；路演通常为空。 |
| issue_method | stock_company_profile_tdx | 发行方式。 |
| issue_price | stock_company_profile_tdx | 发行价格，单位：元。 |
| issue_system | stock_company_profile_tdx | 发行制度。 |
| issue_volume | stock_company_profile_tdx | 发行数量。 |
| item_name | stock_business_composition_tdx | 主营构成项目。 |
| item_order | stock_business_composition_tdx | 序号或层级。 |
| lead_underwriter | stock_company_profile_tdx | 主承销商。 |
| liabilities_and_equity | stock_financial_statement_tdx | 负债和股东权益合计。 |
| lock_months | stock_private_placement_allocations_tdx | 锁定期，单位：月。 |
| long_term_liabilities | stock_balance_summary_tdx | Long-term liabilities, unit: yuan. |
| main_amount | concept_capital_flow_tdx | 主力资金。 |
| main_business_profit | stock_profit_cashflow_summary_tdx | Main-business profit, unit: yuan. |
| main_buy_amount | concept_capital_flow_tdx | 主买资金。 |
| margin_net_buy | stock_margin_trading_tdx | 融资净买入。 |
| metric | stock_valuation_series_tdx | 指标。 |
| mid_value | stock_valuation_band_tdx | 当前统计区间中位值。 |
| min_value | stock_valuation_band_tdx | 当前统计区间最小值。 |
| month_10_pct | stock_return_calendar_tdx | 10 月涨跌幅，单位：%。 |
| month_11_pct | stock_return_calendar_tdx | 11 月涨跌幅，单位：%。 |
| month_12_pct | stock_return_calendar_tdx | 12 月涨跌幅，单位：%。 |
| month_1_pct | stock_return_calendar_tdx | 1 月涨跌幅，单位：%。 |
| month_2_pct | stock_return_calendar_tdx | 2 月涨跌幅，单位：%。 |
| month_3_pct | stock_return_calendar_tdx | 3 月涨跌幅，单位：%。 |
| month_4_pct | stock_return_calendar_tdx | 4 月涨跌幅，单位：%。 |
| month_5_pct | stock_return_calendar_tdx | 5 月涨跌幅，单位：%。 |
| month_6_pct | stock_return_calendar_tdx | 6 月涨跌幅，单位：%。 |
| month_7_pct | stock_return_calendar_tdx | 7 月涨跌幅，单位：%。 |
| month_8_pct | stock_return_calendar_tdx | 8 月涨跌幅，单位：%。 |
| month_9_pct | stock_return_calendar_tdx | 9 月涨跌幅，单位：%。 |
| net_assets | stock_balance_summary_tdx | Net assets, unit: yuan. |
| net_profit_year1 | stock_forecast_consensus_tdx | 未来第一年预测归母净利润。 |
| net_profit_year2 | stock_forecast_consensus_tdx | 未来第二年预测归母净利润。 |
| net_profit_year3 | stock_forecast_consensus_tdx | 未来第三年预测归母净利润。 |
| net_profit_yoy_pct | concept_constituent_comparison_tdx | 归母净利润同比，单位：%。 |
| net_raised_amount | stock_company_profile_tdx | 实际募资净额。 |
| neutral_count | stock_analyst_rating_tdx | 中性家数。 |
| notes_payable | stock_financial_statement_tdx | 应付票据。 |
| notes_receivable | stock_financial_statement_tdx | 应收票据。 |
| operating_cashflow | stock_finance_summary_tdx | Operating cash flow, unit: yuan. |
| operating_profit | stock_profit_cashflow_summary_tdx | Operating profit, unit: yuan. |
| overweight_count | stock_analyst_rating_tdx | 增持家数。 |
| par_value | stock_company_profile_tdx | 每股面值，单位：元。 |
| parent_equity | stock_financial_statement_tdx | 归母权益合计。 |
| payout_ratio_pct | stock_dividend_history_tdx | 股利支付率，单位：%。 |
| pb_mrq | stock_valuation_metrics_tdx | PB(MRQ)。 |
| pb_percentile | stock_valuation_metrics_tdx | PB 百分位。 |
| pcf_percentile | stock_valuation_metrics_tdx | 市现率百分位。 |
| pcf_ttm | stock_valuation_metrics_tdx | 市现率(TTM)。 |
| pe_percentile | stock_valuation_metrics_tdx | PE 百分位。 |
| peg | stock_valuation_metrics_tdx | PEG。 |
| percentile | stock_financial_diagnosis_tdx | 分位或打败比例。 |
| planned_amount_upper | stock_shareholder_change_plans_tdx | 拟变动资金上限，单位：元；源端未按金额披露时为空。 |
| planned_ratio_upper_pct | stock_shareholder_change_plans_tdx | 拟变动上限占总股本比例，单位：%。 |
| planned_volume_upper | stock_shareholder_change_plans_tdx | 拟变动数量上限，单位：股。 |
| progress | stock_dividend_history_tdx | 方案进度。 |
| progress_code | stock_dividend_history_tdx | 方案进度码。 |
| province_board_code | stock_finance_profile_tdx | TDX region board code mapped from province_raw by AxData TDX… |
| province_board_name | stock_finance_profile_tdx | TDX region board name mapped from province_raw by AxData TDX… |
| province_name | stock_finance_profile_tdx | Region/province name mapped from province_raw by AxData TDX … |
| province_raw | stock_finance_profile_tdx | TDX raw region/province code carried by the finance snapshot… |
| ps_percentile | stock_valuation_metrics_tdx | 市销率百分位。 |
| ps_ttm | stock_valuation_metrics_tdx | 市销率(TTM)。 |
| publish_date_change_pct | stock_company_profile_tdx | 公布日涨跌幅，单位：%。 |
| raised_amount | stock_company_profile_tdx | 实际募资总额。 |
| rating_code | stock_financial_diagnosis_tdx | 评价等级码。 |
| relevance | stock_topic_exposure_tdx | 关联度，源端评价分值。 |
| revenue_ratio_pct | stock_business_composition_tdx | 收入占比，单位：%。 |
| revenue_year1 | stock_forecast_consensus_tdx | 未来第一年预测营业收入。 |
| revenue_year2 | stock_forecast_consensus_tdx | 未来第二年预测营业收入。 |
| revenue_year3 | stock_forecast_consensus_tdx | 未来第三年预测营业收入。 |
| revenue_yoy_pct | concept_constituent_comparison_tdx | 营收同比，单位：%。 |
| roe_weighted_pct | stock_dividend_history_tdx | 加权净资产收益率，单位：%。 |
| selected_date | stock_topic_exposure_tdx | 入选或更新日期；源端可能为空。 |
| sell_count | stock_analyst_rating_tdx | 卖出家数。 |
| share_capital | stock_financial_statement_tdx | 实收资本或股本。 |
| shareholder_id | stock_private_placement_allocations_tdx | 股东 ID。 |
| shareholder_name | stock_shareholder_change_plans_tdx | 股东名称。 |
| shareholder_role | stock_shareholder_change_plans_tdx | 股东身份或职务。 |
| short_term_borrowing | stock_financial_statement_tdx | 短期借款。 |
| sponsor | stock_company_profile_tdx | 上市保荐人。 |
| st_type | stock_st_list_tdx | Detected ST name flag: ST or *ST. |
| start_time | stock_disclosure_feed_tdx | 路演开始时间；非路演为空。 |
| stock_type | stock_company_profile_tdx | 股票类别。 |
| subscribed_volume | stock_private_placement_allocations_tdx | 申购数量，单位：股。 |
| summary_total | stock_dividend_metrics_tdx | 汇总总额。 |
| target | stock_regulatory_actions_tdx | 处罚对象。 |
| target_holder | stock_dividend_history_tdx | 派发对象。 |
| target_price | stock_analyst_rating_tdx | 平均目标价。 |
| target_price_high | stock_analyst_rating_tdx | 目标价上限。 |
| target_price_low | stock_analyst_rating_tdx | 目标价下限。 |
| tdx_industry_code | stock_finance_profile_tdx | TDX industry board code mapped from the stock code by AxData… |
| tdx_industry_name | stock_finance_profile_tdx | TDX industry board name mapped from the stock code by AxData… |
| tdx_industry_path | stock_finance_profile_tdx | TDX industry board path mapped from the stock code by AxData… |
| tdx_research_industry_code | stock_finance_profile_tdx | TDX research industry code mapped from the stock code by AxD… |
| tdx_research_industry_name | stock_finance_profile_tdx | TDX research industry name mapped from the stock code by AxD… |
| tdx_research_industry_path | stock_finance_profile_tdx | TDX research industry path mapped from the stock code by AxD… |
| term | stock_governance_guarantees_tdx | 担保期限，源端原值，可能为数字或空。 |
| total_cashflow | stock_profit_cashflow_summary_tdx | Total cash flow, unit: yuan. |
| total_count | stock_valuation_band_tdx | 当前统计区间样本数。 |
| total_equity | stock_financial_statement_tdx | 所有者权益合计。 |
| total_liabilities | stock_financial_statement_tdx | 负债合计。 |
| total_market_cap | concept_constituent_comparison_tdx | 总市值。 |
| total_profit | stock_profit_cashflow_summary_tdx | Total profit, unit: yuan. |
| trading_financial_assets | stock_financial_statement_tdx | 交易性金融资产。 |
| type_code | stock_disclosure_feed_tdx | 公告类型码；非公告通常为空。 |
| type_name | stock_disclosure_feed_tdx | 公告类型名；非公告通常为空。 |
| underweight_count | stock_analyst_rating_tdx | 减持家数。 |
| undistributed_profit | stock_financial_statement_tdx | 未分配利润。 |
| unlock_date | stock_private_placement_allocations_tdx | 解禁日期。 |
| updated_time | stock_market_rankings_tdx | 更新时间。 |
| upside_pct | stock_analyst_rating_tdx | 上涨空间，单位：%。 |
| warning_value | stock_financial_diagnosis_tdx | Z 值或预警值。 |
| year_pct | stock_return_calendar_tdx | 年度涨跌幅，单位：%。 |
#### 12.14.2 通达信扩展行情（补录 89 字段）
| 字段 | 接口 | 含义 |
|:---|:---|:---|
| accumulated_nav | fund_codes_tdx | Accumulated NAV when available. |
| ask2_price | bond_realtime_snapshot_tdx | Ask level 2 price when available. |
| ask2_volume | bond_realtime_snapshot_tdx | Ask level 2 volume when available. |
| ask3_price | bond_realtime_snapshot_tdx | Ask level 3 price when available. |
| ask3_volume | bond_realtime_snapshot_tdx | Ask level 3 volume when available. |
| ask4_price | bond_realtime_snapshot_tdx | Ask level 4 price when available. |
| ask4_volume | bond_realtime_snapshot_tdx | Ask level 4 volume when available. |
| ask5_price | bond_realtime_snapshot_tdx | Ask level 5 price when available. |
| ask5_volume | bond_realtime_snapshot_tdx | Ask level 5 volume when available. |
| base_currency | fx_codes_tdx | Base currency. |
| bid2_price | bond_realtime_snapshot_tdx | Bid level 2 price when available. |
| bid2_volume | bond_realtime_snapshot_tdx | Bid level 2 volume when available. |
| bid3_price | bond_realtime_snapshot_tdx | Bid level 3 price when available. |
| bid3_volume | bond_realtime_snapshot_tdx | Bid level 3 volume when available. |
| bid4_price | bond_realtime_snapshot_tdx | Bid level 4 price when available. |
| bid4_volume | bond_realtime_snapshot_tdx | Bid level 4 volume when available. |
| bid5_price | bond_realtime_snapshot_tdx | Bid level 5 price when available. |
| bid5_volume | bond_realtime_snapshot_tdx | Bid level 5 volume when available. |
| bond_type | bond_codes_tdx | Bond market type. |
| call_ask1_price | option_chain_tdx | call ask level 1 price. |
| call_ask1_volume | option_chain_tdx | call ask level 1 volume. |
| call_ask2_price | option_chain_tdx | call ask level 2 price. |
| call_ask2_volume | option_chain_tdx | call ask level 2 volume. |
| call_ask3_price | option_chain_tdx | call ask level 3 price. |
| call_ask3_volume | option_chain_tdx | call ask level 3 volume. |
| call_ask4_price | option_chain_tdx | call ask level 4 price. |
| call_ask4_volume | option_chain_tdx | call ask level 4 volume. |
| call_ask5_price | option_chain_tdx | call ask level 5 price. |
| call_ask5_volume | option_chain_tdx | call ask level 5 volume. |
| call_bid1_price | option_chain_tdx | call bid level 1 price. |
| call_bid1_volume | option_chain_tdx | call bid level 1 volume. |
| call_bid2_price | option_chain_tdx | call bid level 2 price. |
| call_bid2_volume | option_chain_tdx | call bid level 2 volume. |
| call_bid3_price | option_chain_tdx | call bid level 3 price. |
| call_bid3_volume | option_chain_tdx | call bid level 3 volume. |
| call_bid4_price | option_chain_tdx | call bid level 4 price. |
| call_bid4_volume | option_chain_tdx | call bid level 4 volume. |
| call_bid5_price | option_chain_tdx | call bid level 5 price. |
| call_bid5_volume | option_chain_tdx | call bid level 5 volume. |
| call_instrument_id | option_chain_tdx | Call option instrument id. |
| call_last_price | option_chain_tdx | Call last price. |
| call_open_interest | option_chain_tdx | Call open interest. |
| call_symbol | option_chain_tdx | Call option source code. |
| call_volume | option_chain_tdx | Call volume. |
| contract_month | futures_contracts_tdx | Contract month, YYYYMM. |
| contract_type | futures_contracts_tdx | Contract type. |
| fund_id | fund_nav_tdx | AxData fund id. |
| indicator_category | macro_indicator_snapshot_tdx | Indicator category when known. |
| indicator_id | macro_indicator_series_tdx | AxData macro indicator id. |
| market_group | bond_codes_tdx | Asset group shown by the local extended-asset catalog. |
| market_name | bond_codes_tdx | Market name shown by the local extended-asset catalog. |
| nav | fund_codes_tdx | Fund NAV when available. |
| open_close_type | futures_trades_history_tdx | Open/close label inferred from verified trade fields when po… |
| open_interest_change | bond_realtime_snapshot_tdx | Open interest change when available. |
| period_date | macro_indicator_series_tdx | Value period date. |
| position_change | futures_trades_history_tdx | Open-interest change for the trade when available. |
| pre_settlement | bond_realtime_snapshot_tdx | Previous settlement when available. |
| pre_value | macro_indicator_snapshot_tdx | Previous value. |
| product_name | futures_contracts_tdx | Product name. |
| put_ask1_price | option_chain_tdx | put ask level 1 price. |
| put_ask1_volume | option_chain_tdx | put ask level 1 volume. |
| put_ask2_price | option_chain_tdx | put ask level 2 price. |
| put_ask2_volume | option_chain_tdx | put ask level 2 volume. |
| put_ask3_price | option_chain_tdx | put ask level 3 price. |
| put_ask3_volume | option_chain_tdx | put ask level 3 volume. |
| put_ask4_price | option_chain_tdx | put ask level 4 price. |
| put_ask4_volume | option_chain_tdx | put ask level 4 volume. |
| put_ask5_price | option_chain_tdx | put ask level 5 price. |
| put_ask5_volume | option_chain_tdx | put ask level 5 volume. |
| put_bid1_price | option_chain_tdx | put bid level 1 price. |
| put_bid1_volume | option_chain_tdx | put bid level 1 volume. |
| put_bid2_price | option_chain_tdx | put bid level 2 price. |
| put_bid2_volume | option_chain_tdx | put bid level 2 volume. |
| put_bid3_price | option_chain_tdx | put bid level 3 price. |
| put_bid3_volume | option_chain_tdx | put bid level 3 volume. |
| put_bid4_price | option_chain_tdx | put bid level 4 price. |
| put_bid4_volume | option_chain_tdx | put bid level 4 volume. |
| put_bid5_price | option_chain_tdx | put bid level 5 price. |
| put_bid5_volume | option_chain_tdx | put bid level 5 volume. |
| put_instrument_id | option_chain_tdx | Put option instrument id. |
| put_last_price | option_chain_tdx | Put last price. |
| put_open_interest | option_chain_tdx | Put open interest. |
| put_symbol | option_chain_tdx | Put option source code. |
| put_volume | option_chain_tdx | Put volume. |
| quote_currency | fx_codes_tdx | Quote currency. |
| settlement | bond_kline_tdx | Settlement when available. |
| short_name | tdx_ext_markets_tdx | Short market name. |
| strike_price | option_chain_tdx | Strike price. |
| update_date | fund_codes_tdx | Value update date when available. |
#### 12.14.3 交易所（补录 10 字段）
| 字段 | 接口 | 含义 |
|:---|:---|:---|
| company_full_name | stock_basic_info_exchange | Company full legal name when available. |
| company_full_name_en | stock_basic_info_exchange | Company English full name when available. |
| company_short_name | stock_basic_info_exchange | Company short name when available. |
| company_short_name_en | stock_basic_info_exchange | Company English short name when available. |
| has_weighted_voting_rights | stock_basic_info_exchange | Weighted voting rights marker when available. |
| is_profit | stock_basic_info_exchange | Profitability marker when available. |
| is_vie | stock_basic_info_exchange | VIE/control-structure marker when available. |
| region_code | stock_basic_info_exchange | Region code when available. |
| share_report_date | stock_basic_info_exchange | Share capital report date in YYYYMMDD format when available. |
| sponsor | stock_basic_info_exchange | Sponsoring broker or listing sponsor when available. |
#### 12.14.4 东方财富（补录 12 字段）
| 字段 | 接口 | 含义 |
|:---|:---|:---|
| eps_forecast_this_year | eastmoney_research_reports | This-year EPS forecast. |
| margin_repay_amount | eastmoney_margin_trading | Financing repay amount. |
| org_name | eastmoney_research_reports | Research organization. |
| pb | eastmoney_sector_constituents | PB ratio. |
| pe_forecast_this_year | eastmoney_research_reports | This-year PE forecast. |
| rating_change | eastmoney_research_reports | Rating change code from source. |
| report_id | eastmoney_research_reports | Report id. |
| short_net_sell_volume | eastmoney_margin_trading | Short net sell volume. |
| short_repay_volume | eastmoney_margin_trading | Short repay volume. |
| total_balance | eastmoney_margin_trading | Total margin balance. |
| yesterday_continuous_count | eastmoney_yesterday_limit_up_pool | Yesterday continuous board count. |
| yesterday_limit_time | eastmoney_yesterday_limit_up_pool | Yesterday limit-up time. |
#### 12.14.5 巨潮（补录 222 字段）
| 字段 | 接口 | 含义 |
|:---|:---|:---|
| a_share | stock_share_change_cninfo | 人民币普通股，单位/口径沿用巨潮源端。 |
| actual_allotment_shares | stock_allotment_cninfo | 实际配股数量，单位/口径沿用巨潮源端。 |
| actual_controller_name | stock_hold_control_cninfo | 实际控制人名称。 |
| actual_issue_amount | bond_corporate_issue_cninfo | 实际发行总量，单位/口径沿用巨潮源端。 |
| additional_issue_count | bond_local_government_issue_cninfo | 增发次数，源端数值口径。 |
| allocated_legal_person_share | stock_share_change_cninfo | 配售法人股，单位/口径沿用巨潮源端。 |
| allotment_listing_date | stock_allotment_cninfo | 配股上市日，格式 YYYYMMDD。 |
| allotment_price | bond_cov_issue_cninfo | 配售价格，单位：元。 |
| allotment_ratio | stock_allotment_cninfo | 配股比例，源端数值口径。 |
| allotment_target | stock_allotment_cninfo | 配售对象。 |
| analyst_name | stock_rank_forecast_cninfo | 研究员名称。 |
| announcement_period | stock_cg_guarantee_cninfo | 公告统计区间，沿用巨潮源端文本。 |
| answer_time | stock_irm_ans_cninfo | Reply timestamp. |
| avg_holding | stock_hold_num_cninfo | 本期人均持股数量，单位/口径沿用巨潮源端。 |
| avg_holding_change_pct | stock_hold_num_cninfo | 人均持股数量增幅，源端百分比数值口径。 |
| beginning_holding_shares | stock_hold_management_detail_cninfo | 期初持股数量，单位/口径沿用巨潮源端。 |
| bond_asset_pct | fund_report_asset_allocation_cninfo | 债券固定收益类占净资产比例，源端百分比数值口径。 |
| bond_code | bond_corporate_issue_cninfo | 债券代码。 |
| bond_name | bond_corporate_issue_cninfo | 债券名称。 |
| bond_short_name | bond_corporate_issue_cninfo | 债券简称。 |
| bondholder_record_date | bond_cov_issue_cninfo | 债权登记日，格式 YYYYMMDD。 |
| cash_asset_pct | fund_report_asset_allocation_cninfo | 现金货币类占净资产比例，源端百分比数值口径。 |
| category_code | stock_industry_category_cninfo | 类目编码。 |
| category_name_en | stock_industry_category_cninfo | 类目英文名称。 |
| change_date | stock_hold_change_cninfo | 变动日期，格式 YYYYMMDD。 |
| change_reason | stock_hold_change_cninfo | 变动原因。 |
| change_reason_code | stock_share_change_cninfo | 变动原因编码。 |
| change_shares | stock_hold_management_detail_cninfo | 变动数量，单位/口径沿用巨潮源端。 |
| changer_relation | stock_hold_management_detail_cninfo | 变动人与董监高关系。 |
| circulated_ratio | stock_hold_change_cninfo | 已流通比例，源端数值口径。 |
| circulated_share | stock_hold_change_cninfo | 已流通股份，单位/口径沿用巨潮源端。 |
| circulating_share | stock_share_change_cninfo | 已流通股份，单位/口径沿用巨潮源端。 |
| classification | stock_industry_pe_ratio_cninfo | 行业分类。 |
| classification_standard | stock_industry_change_cninfo | 分类标准名称。 |
| classification_standard_code | stock_industry_change_cninfo | 分类标准编码。 |
| company_count | stock_industry_pe_ratio_cninfo | 公司数量，单位：家。 |
| control_type | stock_hold_control_cninfo | 控制类型。 |
| controlling_shareholder_actual_controller_share | stock_share_change_cninfo | 控股股东、实际控制人持股，单位/口径沿用巨潮源端。 |
| conversion_code | bond_cov_issue_cninfo | 转股代码。 |
| conversion_end_date | bond_cov_issue_cninfo | 转股终止日期，格式 YYYYMMDD。 |
| conversion_price | bond_cov_stock_issue_cninfo | 转股价格，单位：元。 |
| conversion_short_name | bond_cov_stock_issue_cninfo | 转股简称。 |
| conversion_start_date | bond_cov_issue_cninfo | 转股开始日期，格式 YYYYMMDD。 |
| convertible_allotment_shares | stock_allotment_cninfo | 可转配股数量，单位/口径沿用巨潮源端。 |
| cumulative_pledge_total_share_pct | stock_cg_equity_mortgage_cninfo | 累计质押占总股本比例，源端百分比数值口径。 |
| diluted_pe | stock_ipo_summary_cninfo | 摊薄发行市盈率。 |
| direct_controller_name | stock_hold_control_cninfo | 直接控制人名称。 |
| director_supervisor_senior_name | stock_hold_management_detail_cninfo | 董监高姓名。 |
| director_supervisor_senior_position | stock_hold_management_detail_cninfo | 董监高职务。 |
| dividend_payment_date | stock_dividend_cninfo | 派息日，格式 YYYYMMDD。 |
| dividend_type | stock_dividend_cninfo | 分红类型。 |
| domestic_legal_person_restricted_share | stock_share_change_cninfo | 其中：境内法人持股，单位/口径沿用巨潮源端。 |
| domestic_legal_person_share | stock_share_change_cninfo | 境内法人持股，单位/口径沿用巨潮源端。 |
| domestic_natural_person_restricted_share | stock_share_change_cninfo | 其中：境内自然人持股，单位/口径沿用巨潮源端。 |
| employee_actual_shares | stock_allotment_cninfo | 职工股实配数量，单位/口径沿用巨潮源端。 |
| employee_share | stock_share_change_cninfo | 内部职工股，单位/口径沿用巨潮源端。 |
| ending_holding_shares | stock_hold_management_detail_cninfo | 期末持股数量，单位/口径沿用巨潮源端。 |
| ending_market_value | stock_hold_management_detail_cninfo | 期末市值，金额单位/口径沿用巨潮源端。 |
| entrusted_unit | stock_allotment_cninfo | 委托单位。 |
| equity_asset_pct | fund_report_asset_allocation_cninfo | 股票权益类占净资产比例，源端百分比数值口径。 |
| executive_name | stock_hold_management_detail_cninfo | 高管姓名。 |
| executive_share | stock_share_change_cninfo | 高管股，单位/口径沿用巨潮源端。 |
| expected_allotment_shares | stock_allotment_cninfo | 预计配股数量，单位/口径沿用巨潮源端。 |
| expected_issue_expense | stock_allotment_cninfo | 预计发行费用，金额单位/口径沿用巨潮源端。 |
| expected_raised_funds | stock_allotment_cninfo | 预计募集资金，金额单位/口径沿用巨潮源端。 |
| failed_refund_date | stock_allotment_cninfo | 配股失败退还申购款日期，格式 YYYYMMDD。 |
| fax | stock_profile_cninfo | Fax number. |
| foreign_legal_person_restricted_share | stock_share_change_cninfo | 其中：境外法人持股，单位/口径沿用巨潮源端。 |
| foreign_legal_person_share | stock_share_change_cninfo | 境外法人持股，单位/口径沿用巨潮源端。 |
| foreign_natural_person_restricted_share | stock_share_change_cninfo | 其中：境外自然人持股，单位/口径沿用巨潮源端。 |
| foreign_restricted_share | stock_share_change_cninfo | 外资持股-受限，单位/口径沿用巨潮源端。 |
| fund_arrival_date | stock_allotment_cninfo | 资金到账日，格式 YYYYMMDD。 |
| fund_count | fund_report_asset_allocation_cninfo | 基金覆盖家数，单位：只。 |
| fund_market_net_assets | fund_report_asset_allocation_cninfo | 基金市场净资产规模，金额单位/口径沿用巨潮源端。 |
| fundraising_use | bond_corporate_issue_cninfo | 募资用途说明。 |
| general_legal_person_share | stock_share_change_cninfo | 一般法人持股，单位/口径沿用巨潮源端。 |
| guarantee_amount | stock_cg_guarantee_cninfo | 担保金额，金额单位/口径沿用巨潮源端。 |
| guarantee_amount_net_asset_pct | stock_cg_guarantee_cninfo | 担保金额占净资产比例，源端百分比数值口径。 |
| guarantee_count | stock_cg_guarantee_cninfo | 担保笔数，单位：笔。 |
| holding_market_value | fund_report_stock_cninfo | 持股总市值，金额单位/口径沿用巨潮源端。 |
| holding_ratio | stock_hold_control_cninfo | 控股比例，源端数值口径。 |
| holding_shares | fund_report_stock_cninfo | 持股总数，单位/口径沿用巨潮源端。 |
| included_company_count | stock_industry_pe_ratio_cninfo | 纳入计算公司数量，单位：家。 |
| industry_level | stock_industry_pe_ratio_cninfo | 行业层级。 |
| industry_major | stock_industry_change_cninfo | 行业大类。 |
| industry_middle | stock_industry_change_cninfo | 行业中类。 |
| industry_scale | fund_report_industry_allocation_cninfo | 行业规模，金额单位/口径沿用巨潮源端。 |
| industry_sector | stock_industry_change_cninfo | 行业门类。 |
| industry_subcategory | stock_industry_change_cninfo | 行业次类。 |
| industry_type | stock_industry_category_cninfo | 行业类型。 |
| industry_type_code | stock_industry_category_cninfo | 行业类型编码。 |
| initial_conversion_price | bond_cov_issue_cninfo | 初始转股价格，单位：元。 |
| institution_short_name | stock_rank_forecast_cninfo | 研究机构简称。 |
| is_first_rating | stock_rank_forecast_cninfo | 是否首次评级，沿用巨潮源端文本。 |
| issue_end_date | bond_cov_issue_cninfo | 发行终止日，格式 YYYYMMDD。 |
| issue_expenses_total | stock_allotment_cninfo | 发行费用总额，金额单位/口径沿用巨潮源端。 |
| issue_method | bond_corporate_issue_cninfo | 发行方式。 |
| issue_method_code | stock_allotment_cninfo | 发行方式编码。 |
| issue_pe | stock_new_ipo_cninfo | 发行市盈率。 |
| issue_price | bond_corporate_issue_cninfo | 发行价格，单位：元。 |
| issue_result_announcement_date | stock_allotment_cninfo | 配股发行结果公告日，格式 YYYYMMDD。 |
| issue_scope | bond_corporate_issue_cninfo | 发行范围。 |
| issue_start_date | bond_cov_issue_cninfo | 发行起始日，格式 YYYYMMDD。 |
| issue_target | bond_corporate_issue_cninfo | 发行对象。 |
| latest_record_flag | stock_industry_change_cninfo | 最新记录标识，沿用巨潮源端。 |
| lawsuit_amount | stock_cg_lawsuit_cninfo | 诉讼金额，金额单位/口径沿用巨潮源端。 |
| lawsuit_count | stock_cg_lawsuit_cninfo | 诉讼次数，单位：次。 |
| lead_underwriter | stock_ipo_summary_cninfo | 主承销商。 |
| legal_person_actual_shares | stock_allotment_cninfo | 法人股实配数量，单位/口径沿用巨潮源端。 |
| legal_person_transfer_shares | stock_allotment_cninfo | 法人获转配数量，单位/口径沿用巨潮源端。 |
| listing_announcement_date | stock_allotment_cninfo | 上市公告日期，格式 YYYYMMDD。 |
| lottery_rate_announcement_date | stock_ipo_summary_cninfo | 中签率公告日，格式 YYYYMMDD。 |
| lottery_result_announcement_date | stock_new_ipo_cninfo | 摇号结果公告日，格式 YYYYMMDD。 |
| major_shareholder_subscribe_method | stock_allotment_cninfo | 大股东认购方式。 |
| major_shareholder_subscribe_shares | stock_allotment_cninfo | 大股东认购数量，单位/口径沿用巨潮源端。 |
| meeting_date | stock_new_gh_cninfo | 上会日期，格式 YYYYMMDD。 |
| min_subscription_amount | bond_corporate_issue_cninfo | 最低认购额，金额单位/口径沿用巨潮源端。 |
| min_subscription_unit | bond_corporate_issue_cninfo | 最小认购单位，单位/口径沿用巨潮源端。 |
| natural_person_share | stock_share_change_cninfo | 自然人持股，单位/口径沿用巨潮源端。 |
| nav_per_share_after_issue | stock_ipo_summary_cninfo | 发行后每股净资产，单位：元。 |
| nav_per_share_before_issue | stock_ipo_summary_cninfo | 发行前每股净资产，单位：元。 |
| net_asset_pct | fund_report_industry_allocation_cninfo | 占净资产比例，源端百分比数值口径。 |
| net_profit_static | stock_industry_pe_ratio_cninfo | 净利润-静态，金额单位/口径沿用巨潮源端。 |
| non_circulating_share | stock_share_change_cninfo | 未流通股份，单位/口径沿用巨潮源端。 |
| online_issue_date | stock_ipo_summary_cninfo | 上网发行日期，格式 YYYYMMDD。 |
| online_issue_end_date | bond_corporate_issue_cninfo | 交易所网上发行终止日，格式 YYYYMMDD。 |
| online_issue_shares | stock_new_ipo_cninfo | 上网发行数量，单位/口径沿用巨潮源端。 |
| online_issue_start_date | bond_corporate_issue_cninfo | 交易所网上发行起始日，格式 YYYYMMDD。 |
| online_lottery_rate | stock_ipo_summary_cninfo | 上网发行中签率，源端百分比数值口径。 |
| online_lottery_result_refund_date | bond_cov_issue_cninfo | 网上申购中签结果公告日及退款日，格式 YYYYMMDD。 |
| online_subscription_code | bond_cov_issue_cninfo | 网上申购代码。 |
| online_subscription_date | bond_cov_issue_cninfo | 网上申购日期，格式 YYYYMMDD。 |
| online_subscription_limit | stock_new_ipo_cninfo | 网上申购上限，单位/口径沿用巨潮源端。 |
| online_subscription_max | bond_cov_issue_cninfo | 网上申购数量上限，单位/口径沿用巨潮源端。 |
| online_subscription_min | bond_cov_issue_cninfo | 网上申购数量下限，单位/口径沿用巨潮源端。 |
| online_subscription_short_name | bond_cov_issue_cninfo | 网上申购简称。 |
| online_subscription_unit | bond_cov_issue_cninfo | 网上申购单位，单位/口径沿用巨潮源端。 |
| organization_name | stock_allotment_cninfo | 机构名称。 |
| other_actual_shares | stock_allotment_cninfo | 其他股份实配数量，单位/口径沿用巨潮源端。 |
| other_allotment_code | stock_allotment_cninfo | 其他配售代码。 |
| other_allotment_name | stock_allotment_cninfo | 其他配售简称。 |
| other_circulating_share | stock_share_change_cninfo | 其他流通股，单位/口径沿用巨潮源端。 |
| other_domestic_restricted_share | stock_share_change_cninfo | 其他内资持股-受限，单位/口径沿用巨潮源端。 |
| other_non_circulating_share | stock_share_change_cninfo | 其他未流通股，单位/口径沿用巨潮源端。 |
| other_restricted_share | stock_share_change_cninfo | 其他流通受限股份，单位/口径沿用巨潮源端。 |
| par_value | bond_corporate_issue_cninfo | 发行面值，单位：元。 |
| parent_code | stock_industry_category_cninfo | 父类编码。 |
| parent_equity | stock_cg_guarantee_cninfo | 归属于母公司所有者权益，金额单位/口径沿用巨潮源端。 |
| payment_date | bond_local_government_issue_cninfo | 缴款日，格式 YYYYMMDD。 |
| payment_end_date | stock_allotment_cninfo | 配股缴款截止日，格式 YYYYMMDD。 |
| payment_start_date | stock_allotment_cninfo | 配股缴款起始日，格式 YYYYMMDD。 |
| plan_description | stock_dividend_cninfo | 实施方案分红说明。 |
| planned_issue_amount | bond_corporate_issue_cninfo | 计划发行总量，单位/口径沿用巨潮源端。 |
| pledge_event | stock_cg_equity_mortgage_cninfo | 质押事项。 |
| pledged_shares | stock_cg_equity_mortgage_cninfo | 质押数量，单位/口径沿用巨潮源端。 |
| pledged_total_share_pct | stock_cg_equity_mortgage_cninfo | 占总股本比例，源端百分比数值口径。 |
| pledgee | stock_cg_equity_mortgage_cninfo | 质权人。 |
| pledgor | stock_cg_equity_mortgage_cninfo | 出质人。 |
| post_float_share | stock_allotment_cninfo | 配股后流通股本，单位/口径沿用巨潮源端。 |
| post_total_share | stock_allotment_cninfo | 配股后总股本，单位/口径沿用巨潮源端。 |
| pre_float_share | stock_allotment_cninfo | 配股前流通股本，单位/口径沿用巨潮源端。 |
| pre_total_share | stock_allotment_cninfo | 配股前总股本，单位/口径沿用巨潮源端。 |
| preferred_share | stock_share_change_cninfo | 优先股，单位/口径沿用巨潮源端。 |
| prev_avg_holding | stock_hold_num_cninfo | 上期人均持股数量，单位/口径沿用巨潮源端。 |
| prev_shareholder_count | stock_hold_num_cninfo | 上期股东人数，单位：户。 |
| previous_rating | stock_rank_forecast_cninfo | 前一次投资评级。 |
| priority_subscription_date | bond_cov_issue_cninfo | 优先申购日，格式 YYYYMMDD。 |
| priority_subscription_payment_date | bond_cov_issue_cninfo | 优先申购缴款日，格式 YYYYMMDD。 |
| promoter_share | stock_share_change_cninfo | 发起人股份，单位/口径沿用巨潮源端。 |
| prospectus_announcement_date | stock_ipo_summary_cninfo | 招股公告日期，格式 YYYYMMDD。 |
| public_actual_shares | stock_allotment_cninfo | 公众股实配数量，单位/口径沿用巨潮源端。 |
| public_allotment_code | stock_allotment_cninfo | 公众配售代码。 |
| public_allotment_name | stock_allotment_cninfo | 公众配售简称。 |
| public_transfer_shares | stock_allotment_cninfo | 公众获转配数量，单位/口径沿用巨潮源端。 |
| raised_funds_gross | stock_allotment_cninfo | 实际募资总额，金额单位/口径沿用巨潮源端。 |
| raised_funds_net | stock_allotment_cninfo | 实际募资净额，金额单位/口径沿用巨潮源端。 |
| raised_legal_person_share | stock_share_change_cninfo | 募集法人股，单位/口径沿用巨潮源端。 |
| rating_change | stock_rank_forecast_cninfo | 评级变化。 |
| released_pledge_shares | stock_cg_equity_mortgage_cninfo | 质押解除数量，单位/口径沿用巨潮源端。 |
| restricted_b_share | stock_share_change_cninfo | 其中：限售 B 股，单位/口径沿用巨潮源端。 |
| restricted_executive_share | stock_share_change_cninfo | 其中：限售高管股，单位/口径沿用巨潮源端。 |
| restricted_h_share | stock_share_change_cninfo | 其中：限售 H 股，单位/口径沿用巨潮源端。 |
| restricted_share | stock_hold_change_cninfo | 流通受限股份，单位/口径沿用巨潮源端。 |
| review_content | stock_new_gh_cninfo | 审议内容。 |
| review_result | stock_new_gh_cninfo | 审核结果。 |
| review_type | stock_new_gh_cninfo | 审核类型。 |
| securities_investment_fund_share | stock_share_change_cninfo | 证券投资基金持股，单位/口径沿用巨潮源端。 |
| share_arrival_date | stock_dividend_cninfo | 股份到账日，格式 YYYYMMDD。 |
| shareholder_count_change_pct | stock_hold_num_cninfo | 股东人数增幅，源端百分比数值口径。 |
| stat_date | stock_cg_equity_mortgage_cninfo | 请求统计日期，格式 YYYYMMDD。 |
| state_actual_shares | stock_allotment_cninfo | 国家股实配数量，单位/口径沿用巨潮源端。 |
| state_owned_legal_person_restricted_share | stock_share_change_cninfo | 国有法人持股-受限，单位/口径沿用巨潮源端。 |
| state_owned_legal_person_share | stock_share_change_cninfo | 国有法人持股，单位/口径沿用巨潮源端。 |
| state_restricted_share | stock_share_change_cninfo | 国家持股-受限，单位/口径沿用巨潮源端。 |
| static_pe_mean | stock_industry_pe_ratio_cninfo | 静态市盈率-算术平均。 |
| static_pe_median | stock_industry_pe_ratio_cninfo | 静态市盈率-中位数。 |
| static_pe_weighted | stock_industry_pe_ratio_cninfo | 静态市盈率-加权平均。 |
| stock_class | stock_allotment_cninfo | 股票类别。 |
| stock_class_code | stock_allotment_cninfo | 股票类别编码。 |
| strategic_investor_share | stock_share_change_cninfo | 战略投资者持股，单位/口径沿用巨潮源端。 |
| subscription_date | stock_new_ipo_cninfo | 申购日期，格式 YYYYMMDD。 |
| suspend_end_date | stock_allotment_cninfo | 停牌截止日，格式 YYYYMMDD。 |
| suspend_start_date | stock_allotment_cninfo | 停牌起始日，格式 YYYYMMDD。 |
| target_price_high | stock_rank_forecast_cninfo | 目标价格上限，单位：元。 |
| target_price_low | stock_rank_forecast_cninfo | 目标价格下限，单位：元。 |
| total_issue_shares | stock_ipo_summary_cninfo | 总发行数量，单位/口径沿用巨潮源端。 |
| total_market_value_static | stock_industry_pe_ratio_cninfo | 总市值-静态，金额单位/口径沿用巨潮源端。 |
| trade_market | stock_hold_change_cninfo | 交易市场。 |
| trading_market | bond_cov_issue_cninfo | 交易市场。 |
| transfer_actual_shares | stock_allotment_cninfo | 转配股实配数量，单位/口径沿用巨潮源端。 |
| transfer_fee_per_share | stock_allotment_cninfo | 每股配权转让费，单位：元。 |
| transferred_share | stock_share_change_cninfo | 转配股，单位/口径沿用巨潮源端。 |
| underlying_stock | bond_cov_stock_issue_cninfo | 标的股票。 |
| underwriting_balance | stock_allotment_cninfo | 承销余额，单位/口径沿用巨潮源端。 |
| underwriting_fee | stock_allotment_cninfo | 承销费用，金额单位/口径沿用巨潮源端。 |
| underwriting_method | bond_corporate_issue_cninfo | 承销方式。 |
| underwriting_method_code | stock_allotment_cninfo | 承销方式编码。 |
| voluntary_conversion_end_date | bond_cov_stock_issue_cninfo | 自愿转换期终止日，格式 YYYYMMDD。 |
| voluntary_conversion_start_date | bond_cov_stock_issue_cninfo | 自愿转换期起始日，格式 YYYYMMDD。 |
| warrant_trade_end_date | stock_allotment_cninfo | 配股权证交易截止日，格式 YYYYMMDD。 |
| warrant_trade_start_date | stock_allotment_cninfo | 配股权证交易起始日，格式 YYYYMMDD。 |
| winning_announcement_date | stock_new_ipo_cninfo | 中签公告日，格式 YYYYMMDD。 |
#### 12.14.6 腾讯（补录 2 字段）
| 字段 | 接口 | 含义 |
|:---|:---|:---|
| currency | tencent_realtime_snapshot | Currency. |
| pb | tencent_realtime_snapshot | PB ratio. |
#### 12.14.7 新浪（补录 115 字段）
| 字段 | 接口 | 含义 |
|:---|:---|:---|
| accumulated_dividend | fund_etf_dividend_sina | 累计分红，单位/口径沿用新浪源端。 |
| ask | fund_etf_category_sina | 卖出价，单位：元。 |
| ask_price_1 | futures_display_main_sina | 卖一价。 |
| ask_volume_1 | futures_display_main_sina | 卖一量。 |
| bid | fund_etf_category_sina | 买入价，单位：元。 |
| bid_price_1 | futures_display_main_sina | 买一价。 |
| bid_volume_1 | futures_display_main_sina | 买一量。 |
| boc_conversion_rate | currency_boc_sina | 中行折算价，单位：人民币元/100 外币。 |
| brokerage_name | stock_lhb_yytj_sina | 营业部名称。 |
| buy_amount_10k_yuan | stock_lhb_ggtj_sina | 累积购买额，单位：万元。 |
| buy_count | stock_lhb_jgzz_sina | 机构买入次数。 |
| buy_price | option_sse_spot_price_sina | 买价，单位/口径沿用新浪源端。 |
| buy_seat_count | stock_lhb_ggtj_sina | 买入席位数。 |
| buy_volume | option_sse_spot_price_sina | 买量，源端口径。 |
| call_ask_price | option_cffex_hs300_spot_sina | 看涨卖价，单位：点。 |
| call_ask_volume | option_cffex_hs300_spot_sina | 看涨卖量。 |
| call_bid_price | option_cffex_hs300_spot_sina | 看涨买价，单位：点。 |
| call_bid_volume | option_cffex_hs300_spot_sina | 看涨买量。 |
| call_change | option_cffex_hs300_spot_sina | 看涨涨跌，单位/口径沿用新浪源端。 |
| call_latest_price | option_cffex_hs300_spot_sina | 看涨最新价，单位：点。 |
| call_open_interest | option_cffex_hs300_spot_sina | 看涨持仓量。 |
| call_symbol | option_cffex_hs300_spot_sina | 看涨期权完整合约代码。 |
| cash_buy_rate | currency_boc_sina | 中行钞买价，单位：人民币元/100 外币。 |
| cash_sell_rate | currency_boc_sina | 中行钞卖价/汇卖价，单位：人民币元/100 外币。 |
| class_name | stock_classify_sina | 分类名称，例如 玻璃行业；由请求参数标注。 |
| close_yield | bond_gb_us_sina | 收盘收益率，单位：%。 |
| contract | futures_hold_pos_sina | 期货合约代码，例如 OI2501。 |
| controversy_score | stock_esg_rft_sina | 争议维度评分。 |
| controversy_score_date | stock_esg_rft_sina | 争议维度评分日期，格式 YYYYMMDD。 |
| country | bond_gb_us_sina | 国家/地区代码：US 或 CN。 |
| currency | stock_financial_report_sina | 币种，例如 CNY。 |
| currency_code | currency_boc_sina | 货币代码，例如 USD。 |
| currency_name | currency_boc_sina | 货币中文名称。 |
| dividend_date | fund_etf_dividend_sina | 分红日期，格式 YYYYMMDD。 |
| end_datetime | rv_from_futures_zh_minute_sina | 参与计算的末条分钟时间，格式 YYYYMMDDHHMMSS。 |
| env_grade | stock_esg_hz_sina | 环境维度等级。 |
| env_score | stock_esg_hz_sina | 环境维度评分。 |
| env_score_date | stock_esg_rft_sina | 环境维度评分日期，格式 YYYYMMDD。 |
| esg_grade | stock_esg_hz_sina | 华证 ESG 等级。 |
| esg_rating | stock_esg_msci_sina | MSCI ESG 等级/评分，源端文本口径。 |
| esg_score | stock_esg_hz_sina | 华证 ESG 综合评分。 |
| esg_score_date | stock_esg_rft_sina | ESG 综合评分日期，格式 YYYYMMDD。 |
| established_date | fund_scale_close_sina | 成立日期，格式 YYYYMMDD。 |
| expire_date | option_sse_expire_day_sina | 合约到期日，格式 YYYYMMDD。 |
| float_market_cap | index_stock_cons_sina | 流通市值，金额单位/口径沿用新浪源端。 |
| fund_category | fund_scale_close_sina | 基金规模分类，例如 封闭式基金。 |
| fund_manager | fund_scale_close_sina | 基金经理。 |
| fund_name | fund_scale_close_sina | 基金简称。 |
| fx_buy_rate | currency_boc_sina | 中行汇买价，单位：人民币元/100 外币。 |
| governance_grade | stock_esg_hz_sina | 公司治理维度等级。 |
| governance_score | stock_esg_hz_sina | 公司治理维度评分。 |
| governance_score_date | stock_esg_rft_sina | 公司治理维度评分日期，格式 YYYYMMDD。 |
| halt_status | option_sse_underlying_spot_price_sina | 停牌状态，源端编码。 |
| high_yield | bond_gb_us_sina | 最高收益率，单位：%。 |
| implied_volatility | option_sse_greeks_sina | 隐含波动率，源端数值口径。 |
| institution_buy_amount_10k_yuan | stock_lhb_jgmx_sina | 机构席位买入额，单位：万元。 |
| institution_sell_amount_10k_yuan | stock_lhb_jgmx_sina | 机构席位卖出额，单位：万元。 |
| item_name | bond_cb_profile_sina | 资料项名称。 |
| item_source | stock_financial_report_sina | 源端项目所属报表源编码。 |
| item_yoy | stock_financial_report_sina | 项目同比，源端数值口径。 |
| latest_total_share | fund_scale_close_sina | 最近总份额，单位/口径沿用新浪源端。 |
| list_count | stock_lhb_ggtj_sina | 上榜次数。 |
| low_yield | bond_gb_us_sina | 最低收益率，单位：%。 |
| member_name | futures_hold_pos_sina | 期货公司或会员简称。 |
| metric | futures_hold_pos_sina | 持仓成交指标：成交量、多单持仓或空单持仓。 |
| nav_date | fund_scale_close_sina | 净值更新日期，格式 YYYYMMDD。 |
| net_amount_10k_yuan | stock_lhb_ggtj_sina | 净额，单位：万元。 |
| open_yield | bond_gb_us_sina | 开盘收益率，单位：%。 |
| pb | index_stock_cons_sina | 市净率。 |
| pboc_mid_rate | currency_boc_sina | 央行中间价，单位：人民币元/100 外币。 |
| pe | index_stock_cons_sina | 市盈率。 |
| prev_price | stock_intraday_sina | 上一笔成交价，单位：元。 |
| prev_settlement | futures_display_main_sina | 昨结算价。 |
| put_ask_price | option_cffex_hs300_spot_sina | 看跌卖价，单位：点。 |
| put_ask_volume | option_cffex_hs300_spot_sina | 看跌卖量。 |
| put_bid_price | option_cffex_hs300_spot_sina | 看跌买价，单位：点。 |
| put_bid_volume | option_cffex_hs300_spot_sina | 看跌买量。 |
| put_change | option_cffex_hs300_spot_sina | 看跌涨跌，单位/口径沿用新浪源端。 |
| put_latest_price | option_cffex_hs300_spot_sina | 看跌最新价，单位：点。 |
| put_open_interest | option_cffex_hs300_spot_sina | 看跌持仓量。 |
| put_symbol | option_cffex_hs300_spot_sina | 看跌期权完整合约代码。 |
| quote_date | currency_boc_sina | 牌价日期，格式 YYYYMMDD。 |
| quote_status | option_sse_spot_price_sina | 源端行情状态。 |
| rating_date | stock_esg_msci_sina | 评级日期，格式 YYYYMMDD。 |
| realized_variance | rv_from_futures_zh_minute_sina | 实现方差，口径为相邻分钟收盘价对数收益平方和，未年化。 |
| realized_volatility | rv_from_futures_zh_minute_sina | 实现波动率，口径为实现方差平方根，未年化。 |
| recent_days | stock_lhb_ggtj_sina | 统计窗口天数：5、10、30、60。 |
| remainder_days | option_sse_expire_day_sina | 距离到期日的剩余自然日数，源端口径。 |
| remaining_days | option_sse_spot_price_sina | 剩余天数，源端口径。 |
| return_count | rv_from_futures_zh_minute_sina | 用于实现方差求和的相邻对数收益数量。 |
| sample_count | rv_from_futures_zh_minute_sina | 参与计算的有效收盘价样本数。 |
| sell_amount_10k_yuan | stock_lhb_ggtj_sina | 累积卖出额，单位：万元。 |
| sell_count | stock_lhb_jgzz_sina | 机构卖出次数。 |
| sell_price | option_sse_spot_price_sina | 卖价，单位/口径沿用新浪源端。 |
| sell_seat_count | stock_lhb_ggtj_sina | 卖出席位数。 |
| sell_volume | option_sse_spot_price_sina | 卖量，源端口径。 |
| settlement | futures_display_main_sina | 结算价。 |
| social_grade | stock_esg_hz_sina | 社会责任维度等级。 |
| social_score | stock_esg_hz_sina | 社会责任维度评分。 |
| social_score_date | stock_esg_rft_sina | 社会责任维度评分日期，格式 YYYYMMDD。 |
| start_datetime | rv_from_futures_zh_minute_sina | 参与计算的首条分钟时间，格式 YYYYMMDDHHMMSS。 |
| statement_name | stock_financial_report_sina | 报表中文名称。 |
| statement_type | stock_financial_report_sina | 报表类型：balance、income、cashflow。 |
| status_code | option_sse_spot_price_sina | 源端状态码。 |
| symbol_name | bond_gb_us_sina | 中文期限名称，例如 美国10年期国债。 |
| tenor | bond_gb_us_sina | 期限代码，例如 10Y、6M。 |
| theoretical_value | option_sse_greeks_sina | 理论价值，源端模型口径。 |
| top_buy_stocks | stock_lhb_yytj_sina | 买入前三股票，源端逗号分隔文本。 |
| total_raised_scale | fund_scale_close_sina | 总募集规模，单位/口径沿用新浪源端。 |
| trade_type | stock_intraday_sina | 成交方向/类型，源端文本口径。 |
| underlying_sina_symbol | option_sse_expire_day_sina | 源端标的行情代码，例如 s_sh510050。 |
| underlying_source_name | option_sse_expire_day_sina | 源端标的证券名称。 |
| underlying_type | option_sse_spot_price_sina | 标的证券类型，源端编码。 |
| unit_nav | fund_scale_close_sina | 单位净值，单位：元。 |
| updated_time | stock_esg_msci_sina | 源端更新时间。 |
#### 12.14.8 财联社（补录 8 字段）
| 字段 | 接口 | 含义 |
|:---|:---|:---|
| board_tag | cls_sector_popular_stocks | board_tag |
| change_px | cls_sector_popular_stocks | change_px |
| change_text | cls_sector_popular_stocks | change_text |
| down_num | cls_market_emotion | down_num |
| flat_num | cls_market_emotion | flat_num |
| head_rank | cls_sector_popular_stocks | head_rank |
| trade_status | cls_sector_industry | trade_status |
| up_num | cls_market_emotion | up_num |
#### 12.14.9 开盘红（补录 12 字段）
| 字段 | 接口 | 含义 |
|:---|:---|:---|
| event_time | kph_market_review_events | event_time |
| flat_count | kph_market_emotion | flat_count |
| industry_limit_up_count | kph_limit_down_history | industry_limit_up_count |
| plate_amount | kph_limit_ladder | plate_amount |
| rank_tag | kph_sector_constituents_history | rank_tag |
| real_limit_down_count | kph_market_emotion | real_limit_down_count |
| reason_detail | kph_limit_resumption_history | reason_detail |
| reason_short | kph_limit_resumption_history | reason_short |
| st_limit_down_count | kph_market_emotion | st_limit_down_count |
| tag_attribute | kph_market_review_events | tag_attribute |
| tag_id | kph_market_review_events | tag_id |
| tag_name | kph_market_review_events | tag_name |
---