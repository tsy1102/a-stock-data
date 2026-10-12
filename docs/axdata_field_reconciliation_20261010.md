# AxData 与项目字段静态映射及受控实测报告（2026-10-10）

> 本报告先完成 257 个 AxData 接口、3,343 个字段出现项和 2,469 条项目 `source_fields` 的静态映射基线。静态名称/路径命中只属 E0 候选；之后的双交易日逐股实测为 KPH/KPL 六组路径提供 E3 证据。本报告末尾记录了本次获授权的采集器与字典增补；E3 只覆盖列明的字段，不推广到其他 KPH 接口或字段。

## 范围与校验

- AxData pinned revision：`f8ce3cee989717d79c7ad8f73b42f93c6dbd87e8`（以 crosswalk 的来源基线为准）。
- 接口覆盖：257/257；字段出现项：3343/3,343。
- 静态映射基线：主字典来源身份 26/26；运行源名称 35/35；反向字段索引 2469/2,469。后续实施后的计数见本报告末尾。
- 当前采集 wiring：`SOURCE_SCHEME` 32/32；另 3 个为 `ulist` 别名、已移除 `push2_full`、嵌在 `market_sources` 的 `kpl`。
- 2,469 条项目字段路径生成 6066 个名称/路径候选链接，覆盖 1544 个 AxData 字段出现项；666 项带历史附录候选标记，其中 636 项没有当前 registry 路径候选。
- 完整接口和字段数据见 [机器可读交叉表](axdata_interface_crosswalk.json)：`interfaces[].static_reconciliation` 为接口结论，`interfaces[].fields[].static_reconciliation` 为每个字段出现项，顶层 `project_dictionary_field_reverse_map` 覆盖项目所有字段路径。

## 接口关系状态

状态只描述当前源码中的调用关系。`same_endpoint_candidate` 仅指 endpoint/协议可对应，仍不代表字段值可互换。

| 状态 | 数量 |
|---|---:|
| 项目直接调用 AxData (`direct_call`) | 1 |
| 仅同族候选（E0） (`family_candidate_only`) | 88 |
| 当前无该接口路由 (`no_project_route`) | 141 |
| 同端点/协议候选 (`same_endpoint_candidate`) | 21 |
| 同一提供方、不同端点 (`same_provider_different_endpoint`) | 5 |
| 流接口；项目无订阅路径 (`stream_only`) | 1 |

静态接口证据等级计数：E0 88，E1 168，E2 1。E1 只确认源码路由关系；这组静态计数不包含本报告后文新增的受控样本，受控样本独立登记在交叉表的 `empirical_reconciliation` 中。

### 逐接口状态表

接口级 E1/E2 代表源码或既有样本的路径证据；仍须按报告备注区分参数范围、可选采集、同源差异和字段值验证。

| AxData interface_id | 家族 | 关系 | 证据 | 项目 collector/候选 | 字段数 | 日期域 | 说明 |
|---|---|---|---|---|---:|---|---|
| cls_limit_up_pool | cls | no_project_route | E1 | collect_cls, collect_market_sources | 8 | trading_day_or_session_snapshot | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| cls_market_emotion | cls | same_endpoint_candidate | E1 | collect_market_sources | 14 | trading_day_market_snapshot | 端点和参数可静态对应；项目以 market_sources 聚合落盘，字段值/时间边界仍未实测。 |
| cls_market_mainline | cls | no_project_route | E1 | collect_cls, collect_market_sources | 4 | trading_day_or_session_snapshot | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| cls_market_wind | cls | no_project_route | E1 | collect_cls, collect_market_sources | 3 | trading_day_or_session_snapshot | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| cls_market_wind_stocks | cls | no_project_route | E1 | collect_cls, collect_market_sources | 8 | trading_day_or_session_snapshot | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| cls_news_telegraph | cls | same_provider_different_endpoint | E1 | collect_cls | 6 | calendar_day_news_event | 同一新闻服务族、不同主机；项目采集的电报内容不是 AxData 其他 CLS 行情接口的替代。 |
| cls_sector_heat | cls | no_project_route | E1 | collect_cls, collect_market_sources | 6 | trading_day_or_session_snapshot | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| cls_sector_industry | cls | no_project_route | E1 | collect_cls, collect_market_sources | 10 | trading_day_or_session_snapshot | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| cls_sector_popular_stocks | cls | no_project_route | E1 | collect_cls, collect_market_sources | 10 | trading_day_or_session_snapshot | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| cls_sector_rotation | cls | no_project_route | E1 | collect_cls, collect_market_sources | 5 | trading_day_or_session_snapshot | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| cls_stock_kline | cls | no_project_route | E1 | collect_cls, collect_market_sources | 14 | trading_date_series | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| cls_stock_timeline | cls | no_project_route | E1 | collect_cls, collect_market_sources | 13 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| bond_corporate_issue_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 17 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| bond_cov_issue_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 31 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| bond_cov_stock_issue_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 10 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| bond_local_government_issue_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 15 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| bond_treasure_issue_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 15 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| cninfo_announcement_detail | cninfo | no_project_route | E1 | collect_cninfo | 5 | calendar_day_event_or_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| cninfo_announcements | cninfo | no_project_route | E1 | collect_cninfo | 10 | calendar_day_event_or_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| fund_report_asset_allocation_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 6 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| fund_report_industry_allocation_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 6 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| fund_report_stock_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 9 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_allotment_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 59 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_cg_equity_mortgage_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 13 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_cg_guarantee_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 9 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_cg_lawsuit_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 7 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_dividend_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 14 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_hold_change_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 12 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_hold_control_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 10 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_hold_management_detail_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 19 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_hold_num_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 12 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_industry_category_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 8 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_industry_change_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 14 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_industry_pe_ratio_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 12 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_ipo_summary_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 17 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_irm_ans_cninfo | cninfo | same_provider_different_endpoint | E1 | collect_cninfo | 10 | calendar_day_qa_events | 项目答案来自问题列表中的 attachedContent；项目输出未保留 question_id，也没有按 question_id 查询的调用，不能视为该答案详情接口已接入。 |
| stock_irm_cninfo | cninfo | same_endpoint_candidate | E1 | collect_cninfo | 16 | calendar_day_qa_events | 同端点候选；AxData 支持日期/关键词/分页参数，项目固定每股 page_size=10；字段投影仍需逐项验证。 |
| stock_new_gh_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 6 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_new_ipo_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 15 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_profile_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 29 | reference_snapshot_or_validity_interval | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_rank_forecast_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 13 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_share_change_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 46 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_zh_a_disclosure_relation_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 10 | calendar_day_event_or_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_zh_a_disclosure_report_cninfo | cninfo | no_project_route | E1 | collect_cninfo | 10 | calendar_day_event_or_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| eastmoney_dragon_tiger_daily | eastmoney | same_endpoint_candidate | E1 | collect_market_sources | 14 | trading_day_report | 端点相同但 reportName 不同，且为可选上下文采集；不得按同接口或主字典字段重复定案。 |
| eastmoney_limit_down_pool | eastmoney | same_endpoint_candidate | E1 | collect_push2ex | 18 | trading_day_pool | 端点路径相同；返回字段归一化及指定交易日边界尚待受控样本。 |
| eastmoney_limit_up_pool | eastmoney | same_endpoint_candidate | E1 | collect_push2ex | 18 | trading_day_pool | 端点路径相同；返回字段归一化及指定交易日边界尚待受控样本。 |
| eastmoney_margin_trading | eastmoney | same_endpoint_candidate | E1 | collect_datacenter | 18 | trading_day_series | 端点候选只覆盖项目 fallback；多数情况下项目优先返回 TDX F10 数据，须在样本中记录实际命中来源。 |
| eastmoney_market_index_realtime | eastmoney | same_endpoint_candidate | E1 | collect_clist | 11 | trading_day_market_snapshot | 同一 clist endpoint；项目查询行业/概念/地域板块列表，不查询 AxData 默认指数范围，只有端点重合。 |
| eastmoney_research_reports | eastmoney | same_endpoint_candidate | E1 | collect_reports | 15 | calendar_day_report_publication | 端点相同；AxData 与项目分页/过滤范围和字段投影需要值样本核验。 |
| eastmoney_sector_constituents | eastmoney | same_endpoint_candidate | E1 | collect_clist | 20 | trading_day_sector_snapshot | 同一 endpoint 候选；项目按行业/概念/地域分页采集板块列表，不按单板块请求成分股，覆盖范围不同。 |
| eastmoney_sector_realtime | eastmoney | same_endpoint_candidate | E1 | collect_clist | 17 | trading_day_sector_snapshot | 同一 endpoint 候选；项目保留原始 f 字段，但参数范围仅覆盖行业/概念/地域板块。 |
| eastmoney_stock_change_detail | eastmoney | same_provider_different_endpoint | E1 | collect_market_sources | 12 | trading_day_intraday_event | 同一提供方和相邻数据域，不同 endpoint；项目只采 8201 火箭发射列表，未接入逐股异动详情请求。 |
| eastmoney_stock_changes | eastmoney | same_endpoint_candidate | E1 | collect_market_sources | 9 | trading_day_intraday_event | 端点相同，但项目只采一种异动类型；不能推断 AxData 的全部异动类型均已覆盖。 |
| eastmoney_stock_realtime_snapshot | eastmoney | same_endpoint_candidate | E1 | collect_ulist239 | 20 | trading_day_realtime_snapshot | 端点相同；项目按一批股票请求原始字段，值、字段选择和盘中时点尚未对照。 |
| eastmoney_stock_sector_belong | eastmoney | same_endpoint_candidate | E1 | collect_ulist239 | 5 | reference_membership_snapshot | AxData 与项目调用同一 ULIST endpoint；项目原始字段目前以行情字段为主，所属板块语义和字段需另行验证。 |
| eastmoney_yesterday_limit_up_pool | eastmoney | same_provider_different_endpoint | E1 | collect_push2ex | 22 | trading_day_prior_close_performance | 同一提供方、不同池接口；项目没有采集昨日涨停股的今日表现，不能认为已覆盖。 |
| stock_basic_info_exchange | exchange | no_project_route | E1 | collect_exchange | 27 | reference_snapshot_or_validity_interval | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_historical_list_exchange | exchange | no_project_route | E1 | collect_exchange | 9 | trading_date_series | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_trade_calendar_exchange | exchange | no_project_route | E1 | collect_exchange | 4 | calendar_date_or_session_calendar | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| kph_limit_down_history | kph | no_project_route | E1 | collect_market_sources | 19 | trading_date_series | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| kph_limit_ladder | kph | same_endpoint_candidate | E1 | collect_market_sources | 14 | trading_day_limit_ladder | KPH 天梯走 Levistock；项目 KPL 指标是另一独立上游，不能把 kpl_* 与 KPH 字段合并。 |
| kph_limit_resumption_history | kph | no_project_route | E1 | collect_market_sources | 12 | trading_date_series | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| kph_limit_up_history | kph | no_project_route | E1 | collect_market_sources | 19 | trading_date_series | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| kph_market_emotion | kph | no_project_route | E1 | collect_market_sources | 14 | trading_day_or_session_snapshot | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| kph_market_review_events | kph | no_project_route | E1 | collect_market_sources | 9 | trading_day_or_session_snapshot | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| kph_sector_constituents_history | kph | no_project_route | E1 | collect_market_sources | 16 | trading_date_series | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| kph_sector_ranking | kph | no_project_route | E1 | collect_market_sources | 11 | trading_day_or_session_snapshot | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| kph_wind_vane_history | kph | no_project_route | E1 | collect_market_sources | 19 | trading_date_series | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| bond_cb_profile_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 7 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| bond_cb_summary_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 7 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| bond_gb_us_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 10 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| bond_gb_zh_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 10 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| currency_boc_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 8 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| fund_etf_category_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 17 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| fund_etf_dividend_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 6 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| fund_etf_hist_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 11 | trading_date_series | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| fund_scale_close_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 10 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| fund_scale_open_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 10 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| fund_scale_structured_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 10 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| futures_display_main_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 22 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| futures_hold_pos_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 7 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| futures_main_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 9 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| futures_zh_daily_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 9 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| futures_zh_minute_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 11 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| index_global_hist_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 8 | trading_date_series | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| index_stock_cons_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 23 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| index_us_stock_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 9 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_cffex_hs300_daily_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 10 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_cffex_hs300_list_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 7 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_cffex_hs300_spot_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 21 | trading_day_or_session_snapshot | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_cffex_sz50_daily_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 10 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_cffex_sz50_list_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 7 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_cffex_sz50_spot_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 21 | trading_day_or_session_snapshot | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_cffex_zz1000_daily_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 10 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_cffex_zz1000_list_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 7 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_cffex_zz1000_spot_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 21 | trading_day_or_session_snapshot | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_commodity_contract_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 6 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_commodity_contract_table_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 8 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_commodity_hist_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 12 | trading_date_series | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_finance_minute_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 8 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_sse_codes_sina | sina | same_endpoint_candidate | E1 | collect_sina | 8 | trading_day_or_session_snapshot | base endpoint is shared, but project sends A-share stock codes while AxData interface targets HK index/SSE options; field and instrument coverage do not match. |
| option_sse_daily_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 8 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_sse_expire_day_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 10 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_sse_greeks_sina | sina | same_endpoint_candidate | E1 | collect_sina | 16 | trading_day_or_session_snapshot | base endpoint is shared, but project sends A-share stock codes while AxData interface targets HK index/SSE options; field and instrument coverage do not match. |
| option_sse_list_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 6 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_sse_minute_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 8 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| option_sse_spot_price_sina | sina | same_endpoint_candidate | E1 | collect_sina | 29 | trading_day_or_session_snapshot | base endpoint is shared, but project sends A-share stock codes while AxData interface targets HK index/SSE options; field and instrument coverage do not match. |
| option_sse_underlying_spot_price_sina | sina | same_endpoint_candidate | E1 | collect_sina | 21 | trading_day_or_session_snapshot | base endpoint is shared, but project sends A-share stock codes while AxData interface targets HK index/SSE options; field and instrument coverage do not match. |
| rv_from_futures_zh_minute_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 8 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_classify_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 21 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_esg_hz_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 12 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_esg_msci_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 11 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_esg_rate_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 6 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_esg_rft_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 13 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_esg_zd_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 6 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_financial_report_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 24 | reporting_period_or_calendar_publication | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_hk_index_daily_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 11 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_hk_index_spot_sina | sina | same_endpoint_candidate | E1 | collect_sina | 12 | trading_day_or_session_snapshot | base endpoint is shared, but project sends A-share stock codes while AxData interface targets HK index/SSE options; field and instrument coverage do not match. |
| stock_info_global_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 3 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_intraday_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 10 | trading_date_series | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_lhb_detail_daily_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 11 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_lhb_ggtj_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 13 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_lhb_jgmx_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 10 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_lhb_jgzz_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 12 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_lhb_yytj_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 10 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_restricted_release_queue_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 10 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_zh_index_spot_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 18 | trading_day_or_session_snapshot | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| tool_trade_date_hist_sina | sina | no_project_route | E1 | collect_research_sina, collect_sina | 4 | trading_date_series | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| concept_capital_flow_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 6 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| concept_constituent_comparison_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 16 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| concept_constituents_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 7 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| concept_control_ranking_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 8 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| concept_control_series_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 5 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| concept_related_boards_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 7 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| etf_auction_process_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 12 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| etf_auction_result_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 10 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| etf_codes_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 6 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| etf_intraday_history_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 10 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| etf_intraday_today_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 9 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| etf_kline_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 14 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| etf_realtime_rank_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 22 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| etf_realtime_snapshot_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 21 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| etf_trades_history_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 12 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| etf_trades_today_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 10 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| index_codes_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 7 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| index_intraday_history_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 10 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| index_intraday_today_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 9 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| index_kline_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 14 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| index_quote_refresh_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 21 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| index_realtime_rank_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 22 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| index_realtime_snapshot_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 21 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_adj_factor_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 7 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_analyst_rating_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 13 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_auction_process_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 12 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_auction_result_history_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 12 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_auction_result_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 10 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_balance_summary_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 15 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_business_composition_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 13 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_capital_changes_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 17 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_chip_distribution_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 8 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_codes_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 6 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_company_profile_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 21 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_daily_price_limit_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 15 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_daily_share_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 10 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_disclosure_feed_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 15 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_dividend_history_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 13 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_dividend_metrics_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 10 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_equity_financing_events_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 9 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_event_drivers_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 10 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_finance_profile_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 17 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_finance_summary_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 16 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_financial_diagnosis_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 11 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_financial_statement_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 20 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_forecast_consensus_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 14 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_governance_guarantees_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 12 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_index_constituent_changes_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 8 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_institution_holding_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 6 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_intraday_buy_sell_strength_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 8 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_intraday_history_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 10 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_intraday_recent_history_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 13 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_intraday_today_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 9 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_intraday_volume_comparison_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 10 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_ipo_listing_profile_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 15 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_kline_daily_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 12 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_kline_minute_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 12 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_kline_monthly_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 12 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_kline_nday_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 12 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_kline_nminute_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 12 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_kline_quarterly_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 12 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_kline_second_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 12 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_kline_weekly_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 12 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_kline_yearly_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 12 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_limit_ladder_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 19 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_margin_trading_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 6 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_market_rankings_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 8 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_northbound_holding_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 9 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_order_book_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 9 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_private_placement_allocations_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 11 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_profit_cashflow_summary_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 17 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_quote_refresh_tdx | tdx | stream_only | E1 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 9 | stream_event_time | One streaming catalog entry; it is distinct from the project’s request/response snapshots. |
| stock_realtime_rank_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 42 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_realtime_snapshot_tdx | tdx | same_endpoint_candidate | E2 | collect_tdx | 41 | intraday_trading_snapshot | 已有 2026-10-09 12:35 单股样本，但缺少当时 AxData 版本/as_of_date；只作 E2 观察候选，不作为 pinned 0.1.4 定案证据。 |
| stock_regulatory_actions_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 7 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_research_reports_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 8 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_return_calendar_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 16 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_score_summary_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 15 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_share_capital_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 13 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_shareholder_change_plans_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 13 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_shortline_indicators_tdx | tdx | direct_call | E1 | collect_axdata | 34 | trading_day_statistics_baseline_plus_live_quote | This is the only explicit production AxData call. Current latest project ZHB cache is 2026-09-30; it cannot establish a 2026-10-09 baseline. |
| stock_st_list_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 7 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_suspensions_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 6 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_theme_strength_rank_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 18 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_topic_exposure_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 10 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_trades_history_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 12 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_trades_today_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 10 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_valuation_band_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 9 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_valuation_metrics_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 14 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_valuation_series_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 6 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| stock_violation_cases_tdx | tdx | family_candidate_only | E0 | collect_axdata, collect_eltdx, collect_tdx, collect_tdx_f10, collect_tdx_f10_more, collect_zhb | 8 | not_verified_per_interface | Current collectors share TDX family/protocol only; interface-level command, output key, cache, and date behavior remain unresolved. |
| bond_codes_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 7 | reporting_period_or_calendar_publication | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| bond_kline_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 13 | reporting_period_or_calendar_publication | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| bond_realtime_snapshot_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 39 | reporting_period_or_calendar_publication | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| fund_codes_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 10 | reference_snapshot_or_validity_interval | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| fund_nav_series_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 13 | not_declared | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| fund_nav_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 7 | not_declared | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| futures_contracts_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 10 | not_declared | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| futures_intraday_history_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 9 | trading_date_series | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| futures_intraday_today_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 9 | trading_date_series | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| futures_kline_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 13 | trading_date_series | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| futures_realtime_snapshot_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 39 | trading_day_or_session_snapshot | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| futures_trades_history_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 10 | trading_date_series | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| futures_trades_today_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 10 | not_declared | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| fx_codes_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 8 | reference_snapshot_or_validity_interval | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| fx_intraday_history_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 9 | trading_date_series | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| fx_intraday_today_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 9 | trading_date_series | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| fx_kline_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 13 | trading_date_series | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| fx_realtime_snapshot_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 39 | trading_day_or_session_snapshot | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| fx_trades_history_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 10 | trading_date_series | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| fx_trades_today_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 10 | not_declared | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| macro_indicator_series_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 11 | not_declared | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| macro_indicator_snapshot_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 9 | trading_day_or_session_snapshot | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| macro_indicators_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 9 | not_declared | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| option_chain_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 55 | not_declared | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| option_contracts_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 11 | not_declared | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| option_intraday_history_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 9 | trading_date_series | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| option_intraday_today_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 9 | trading_date_series | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| option_kline_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 13 | trading_date_series | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| option_realtime_snapshot_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 39 | trading_day_or_session_snapshot | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| tdx_ext_instruments_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 17 | reference_snapshot_or_validity_interval | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| tdx_ext_markets_tdx | tdx_ext | no_project_route | E1 | collect_eltdx, collect_etf | 5 | trading_day_or_session_snapshot | Checked collect_etf (official SSE/SZSE ETF shares) and collect_eltdx; neither requests AxData TDX Ext bond/futures/FX/options/macro endpoints. No current TDX Ext route is wired. |
| get_tx_start_year | tencent | no_project_route | E1 | collect_tencent | 6 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_zh_a_hist_tx | tencent | no_project_route | E1 | collect_tencent | 12 | trading_date_series | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_zh_a_spot_tx | tencent | same_provider_different_endpoint | E1 | collect_tencent | 16 | trading_day_market_snapshot | 同一提供方，但 AxData 返回榜单，项目返回逐股快照；不是同一接口覆盖。 |
| stock_zh_a_tick_tx_js | tencent | no_project_route | E1 | collect_tencent | 10 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| stock_zh_index_daily_tx | tencent | no_project_route | E1 | collect_tencent | 12 | not_declared | The active project collector(s) for this family were inspected; their current request/adapter scope does not call this AxData interface. No same-interface project route is wired. |
| tencent_realtime_snapshot | tencent | same_endpoint_candidate | E1 | collect_tencent | 23 | trading_day_realtime_snapshot | 端点和逐股请求模式相同；原始字段为位置数组与 AxData 命名字段仍需样本对照。 |

## 字段出现项关系与证据等级

项目侧反向索引：2469 条字段路径中，`unverified` 401 条有 AxData 名称/路径候选，`project_only` 2068 条当前无候选；此状态同样不代表语义上不存在。

| 字段关系状态 | 数量 | 解释 |
|---|---:|---|
| `axdata_only_candidate` — AxData-only 候选（无当前名称/路径命中） | 931 | 没有当前名称/路径/canonical 命中，不证明项目不存在同义字段。 |
| `not_applicable` — 证券/公司/交易所标识字段 | 609 | 用于识别记录对象，不作为业务指标字段对撞。 |
| `unverified` — 未验证候选 | 1803 | 可定位到当前字典路径或历史附录；语义、单位、日期和空值行为仍未确认。 |

| 字段证据等级 | 出现项数 | 可支持的结论 |
|---|---:|---|
| E0 | 3330 | 目录/名称/路径候选；不能确认字段含义或等价。 |
| E2 | 13 | 一次历史同代码样本的观测候选；版本、as_of_date 和跨样本稳定性未确认。 |

**没有字段被定为 `exact_same_field`、`same_semantics_alias` 或 `same_semantics_with_transform`。** 本节的旧午间样本没有记录 AxData 版本，且采集时间/来源日期不符合主字典确认要求；其 13 个字段观察仍标记为 `usable_for_dictionary_change=false`。本轮另用项目要求的 `axdata==0.1.4` 做了受控实测，证据和局限见下一节。

## 历史 TDX 午间样本（不作为 pinned AxData 证据）

样本文件：`.tmp/axdata_project_live_sample_20261009.json`；代码 `000001`；AxData 12:35:28、项目 TDX 12:35:33。无接口返回的 `trade_date/as_of_date`，属于盘中快照。

| AxData 字段 | 项目输出键/路径候选 | 单次观测 | 样本结果 |
|---|---|---|---|
| last_price | price | 同值别名候选 | 11.69 ↔ 11.69 |
| pre_close | last_close | 同值别名候选 | 11.78 ↔ 11.78 |
| open | open | 值相同 | 11.78 ↔ 11.78 |
| high | high | 值相同 | 11.89 ↔ 11.89 |
| low | low | 值相同 | 11.65 ↔ 11.65 |
| change | change_amt | 同值别名候选；浮点容差 | -0.09 ↔ -0.08999999999999986 |
| change_pct | change_pct | AxData 保留 6 位小数候选 | -0.764007 ↔ -0.7640067911714759 |
| volume | s_vol + b_vol | project s_vol + b_vol = AxData volume | 546400 ↔ 546400 |
| amount | amount_wan | AxData amount / 10000 = project amount_wan | 640948416.0 ↔ 64094.8416 |
| inside_volume | s_vol | 值相同候选 | 282513 ↔ 282513 |
| outside_volume | b_vol | 值相同候选 | 263887 ↔ 263887 |
| bid1_price | bid1 | 同值别名候选 | 11.69 ↔ 11.69 |
| ask1_price | ask1 | 同值别名候选 | 11.71 ↔ 11.71 |

数值相等、别名或换算只在这一只股票、这个时点成立；样本版本和来源日期未完整记录。主字典中的 TDX 字段仍保持原状态。

## 2026-10-10 受控实测（目标交易日 2026-10-09）

本轮使用 Python 3.12 和 `axdata==0.1.4`（与 `requirements.txt` 已有约束一致），先将采集目录登记为 `20261009`，再按接口族限量取样。采集是选择性采集，不是全源 `--all`；`meta.json` 汇总的实际采集源为 ZHB、TDX、ELTDX、AxData。

| 数据组 | 实际结果 | 日期证据与限制 |
|---|---|---|
| ZHB | 20/20 股票；0 错误 | `as_of_date=20261009`。 |
| TDX | 20/20 股票；0 错误 | 响应没有明确 `as_of_date`；按目标目录保存，但不单独作为来源日期证据。 |
| ELTDX | 20 条记录；0 错误；4 个北交所快照子项跳过 | 短线记录 `stats_date=2026-10-09`；被跳过原因是 `BSE code: snapshot marker not available`。 |
| AxData 短线 | 18/20 条可用；2 条 `no_records`，代码为 `920118`、`920508` | 18 条可用记录的 `stats_date=20261009`；未重试，未观察到 403/429。 |

AxData 与 ELTDX 的短线对照限于 18 只双方均有记录的股票，共 31 个同名字段、558 个字段值比较：327 个非空完全相同、4 个浮点近似、115 对均为空、112 个不同。差异拆分为交易所值格式 18 项（`SSE`/`SZSE` 对 `sh`/`sz`）、日期格式 18 项（`20261009` 对 `2026-10-09`）、`opening_rush` 18 项（AxData 有数值、ELTDX 为 `null`），以及 6 个数值字段合计 58 项：`auction_prev_volume_ratio` 11、`open_amount` 11、`open_prev_amount_ratio` 9、`open_turnover_z` 5、`open_volume_hand` 11、`open_volume_ratio` 11。上述数值差异幅度均较小（最大相对差约 0.04%），但仍不能据单日样本认定公式相同。

| AxData 接口 | 限量样本结果 | 可得结论与限制 |
|---|---|---|
| `tencent_realtime_snapshot` | 600519 单只；19 个手工对照值中 18 个一致（含金额单位换算）；唯一数值映射差异是 PE；`quote_time=20261009161459`。 | AxData 将 `pe_dynamic` 解析自腾讯原始 `parts[39]`（19.39）；主字典当前把腾讯 `[39]` 登记为 PE(TTM)，而 `[52]` 为动态 PE（17.73）、`[53]` 为静态 PE（19.18）。与主字典当前动态 PE 路径相比，AxData 的 19.39 不同，但它恰与项目原始 `[39]` 相同；需跨证券核对上游字段定义后再判定 AxData 标签或字典映射是否有误。金额对照中 AxData 元与原始 `[57]` 万元换算后相等；项目 `[37]` 是取整金额。 |
| `cls_market_emotion` | 项目和 AxData 各一次；市场情绪顶层常用值一致，`up_down_dis` 与涨停表结构可对应。 | 响应没有明确交易日期；只作结构和值的 E2 观察，不宣称是 10 月 9 日收盘值。 |
| `kph_limit_ladder` | 显式指定 `20261009`；双方各返回 69 行，69 个代码均匹配，11 个映射值逐行一致。 | 日期明确；`one_word`、`popular` 为 int/bool 类型差异，金额为 int/float 差异，值归一后相同。一次样本不足以升级主字典。 |
| `stock_irm_cninfo` | 同一股票、同一页各取前 10 条；按问题文本空白归一和提问时间分钟粒度，10/10 事件匹配。 | 问题为自然日事件，样本未设日期筛选；原始问题文本 9/10 完全相同，空白归一后 10/10 一致。AxData 还输出项目没有保留的 ID、提问者及更新时间等字段。 |
| `stock_realtime_snapshot_tdx` | 600519 单次 AxData 快照，1 条记录。 | 返回没有 `quote_time/as_of_date/trade_date`，不用于 10 月 9 日日期定论。 |

本轮请求均为一次性、小样本查询；没有运行 `--all`，没有请求 Eastmoney push2，也没有观察到 403/429 或封禁。样本总量与来源日期限制都低于 E3 标准。首次 `--only zhb,tdx` 的控制台摘要横幅仍列出 Tencent/push2，但 `--only` 参数和 `meta.json` 的实际来源列表均确认未请求它们；这是容易误导的状态展示，需后续针对性修正采集脚本。原始采集数据受 `.gitignore` 排除；本报告和机器可读交叉表保留统计结果，原始数据当前仅在本地工作区。

## 来源身份和运行源核对

### 主字典当前 30 个 `source_fields` 来源身份（2026-10-11）

本表反映 2026-10-11 的当前注册表。下方原始 AxData 交叉表文件 [`axdata_interface_crosswalk.json`](axdata_interface_crosswalk.json) 保留 2026-10-10 分析快照，仍使用当时的来源身份名称；核对当前来源身份时，以主字典和 [`source_identity_reclassifications.json`](field_verification/source_identity_reclassifications.json) 为准。

AxData 在主字典中只有 `framework_reference` 元数据，没有逐字段记录；当前 `axdata` 采集器只通过 AxData 框架调用 TDX 短线接口，不能把 AxData 记为独立数据提供方。FTShare 的 6 条字段来自项目接入的 MCP 服务接口，底层提供方族尚未确认。Levistock 旧混合键已从活动字段注册表删除。

| 主字典来源身份 | 路径数 | 对应的运行源名候选 |
|---|---:|---|
| TDX(双命名源) | 305 | tdx, tdx_f10, tdx_f10_more |
| TDX-eltdx(适配层) | 294 | eltdx |
| ZHB-tdxstat | 97 | zhb |
| ZHB-tdxstat2 | 65 | zhb |
| ZHB-tipinfo | 49 | zhb |
| FTShare | 6 | ftshare（服务接口；底层来源族未确认） |
| Levistock历史未归属 | 136 | —（历史证据，无运行时别名） |
| reports | 101 | reports |
| 东财-clist | 26 | clist, st_list |
| 东财-datacenter(英文键) | 100 | datacenter, event_dc, macro_dc |
| 东财-em_kline_f61 | 14 | em_kline_f61 |
| 东财-push2(stock/get) | 166 | push2 |
| 东财-push2ex | 43 | push2ex |
| 东财-slist | 5 | slist |
| 东财-ulist239(np/get) | 240 | ulist, ulist239 |
| 东财-热榜(em_hot) | 42 | em_hot |
| 东财-资金流(em_fund_flow) | 30 | em_fund_flow |
| 同花顺-fuyao | 223 | fuyao |
| 巨潮(cninfo) | 10 | cninfo |
| 市场源(market_sources) | 140 | market_sources |
| 开盘啦(kpl) | 161 | kpl, market_sources |
| 开盘啦(kpl_limit_up_detail) | 6 | kpl |
| 开盘红 | 6 | kph |
| 开盘红(Levistock适配) | 33 | kph（与开盘红属于同一来源族） |
| 新浪(hq.sinajs) | 36 | sina |
| 新浪(扩展API) | 27 | research_sina |
| 沪深交易所 | 5 | exchange |
| 百度(baidu) | 3 | baidu |
| 腾讯(qt.gtimg) | 88 | tencent |
| 财联社(cls) | 24 | cls |

这 30 个字段来源身份共覆盖 2,481 条逐源记录；历史身份迁移只改来源键及对应聚合来源名，字段路径和确认状态保持不变。AxData 的框架元数据不计入这 30 个有字段身份的数量。

### 计划列出的 35 个运行源名

| 运行源名 | 当前状态 | scheme | collector | raw 文件/路径 | 字典身份候选 |
|---|---|---|---|---|---|
| push2 | active | em.stock_get | collect_push2 | docs/field_verification/{YYYYMMDD}/raw_push2.json | 东财-push2(stock/get) |
| em_fund_flow | active | em.stock_get | collect_em_fund_flow | docs/field_verification/{YYYYMMDD}/raw_em_fund_flow.json | 东财-资金流(em_fund_flow) |
| ulist239 | active | em.ulist_np | collect_ulist239 | docs/field_verification/{YYYYMMDD}/raw_ulist239.json | 东财-ulist239(np/get) |
| ulist | alias | — | — | docs/field_verification/{YYYYMMDD}/raw_ulist239.json | 东财-ulist239(np/get) |
| push2ex | active | em.push2ex | collect_push2ex | docs/field_verification/{YYYYMMDD}/raw_push2ex.json | 东财-push2ex |
| datacenter | active | em.datacenter | collect_datacenter | docs/field_verification/{YYYYMMDD}/raw_datacenter.json | 东财-datacenter(英文键) |
| slist | active | em.slist | collect_slist | docs/field_verification/{YYYYMMDD}/raw_slist.json | 东财-slist |
| clist | active | em.clist | collect_clist | docs/field_verification/{YYYYMMDD}/raw_clist.json | 东财-clist |
| push2_full | removed_historical | — | — | — | 东财-push2_full |
| reports | active | reports | collect_reports | docs/field_verification/{YYYYMMDD}/raw_reports.json | reports |
| em_kline_f61 | active | em.kline | collect_em_kline_f61 | docs/field_verification/{YYYYMMDD}/raw_em_kline_f61.json | 东财-em_kline_f61 |
| em_hot | active | em.hot | collect_em_hot | docs/field_verification/{YYYYMMDD}/raw_em_hot.json | 东财-热榜(em_hot) |
| tdx | active | tdx | collect_tdx | docs/field_verification/{YYYYMMDD}/raw_tdx.json | TDX(双命名源) |
| tdx_f10 | active | tdx.f10 | collect_tdx_f10 | docs/field_verification/{YYYYMMDD}/raw_tdx_f10.json | TDX(双命名源) |
| tdx_f10_more | active | tdx.f10 | collect_tdx_f10_more | docs/field_verification/{YYYYMMDD}/raw_tdx_f10_more.json | TDX(双命名源) |
| zhb | active | zhb | collect_zhb | docs/field_verification/{YYYYMMDD}/raw_zhb.json | ZHB-tdxstat, ZHB-tdxstat2, ZHB-tipinfo |
| eltdx | active | eltdx | collect_eltdx | docs/field_verification/{YYYYMMDD}/raw_eltdx.json | TDX-eltdx(适配层) |
| tencent | active | tencent.qt | collect_tencent | docs/field_verification/{YYYYMMDD}/raw_tencent.json | 腾讯(qt.gtimg) |
| sina | active | sina.hq | collect_sina | docs/field_verification/{YYYYMMDD}/raw_sina.json | 新浪(hq.sinajs) |
| fuyao | active | fuyao | collect_fuyao | docs/field_verification/{YYYYMMDD}/raw_fuyao.json | 同花顺-fuyao |
| cls | active | cls | collect_cls | docs/field_verification/{YYYYMMDD}/raw_cls.json | 财联社(cls) |
| baidu | deprecated | baidu.deprecated | collect_baidu | — | 百度(baidu) |
| exchange | active | exchange.official | collect_exchange | docs/field_verification/{YYYYMMDD}/raw_exchange.json | 沪深交易所 |
| cninfo | active | cninfo | collect_cninfo | docs/field_verification/{YYYYMMDD}/raw_cninfo.json | 巨潮(cninfo) |
| axdata | active | axdata.shortline | collect_axdata | docs/field_verification/{YYYYMMDD}/raw_axdata.json | AxData |
| ftshare | active | ftshare | collect_ftshare | docs/field_verification/{YYYYMMDD}/raw_ftshare.json | FTShare MCP (`market.ft.tech`); not Levistock |
| market_sources | active | market.mixed | collect_market_sources | docs/field_verification/{YYYYMMDD}/raw_market_sources.json | CLS/KPH via Levistock; KPL is a separate provider; other market sources |
| kpl | embedded_subsource | — | collect_market_sources | docs/field_verification/{YYYYMMDD}/raw_market_sources.json#/kpl_* | 开盘啦(kpl) |
| event_dc | active | em.datacenter | collect_event_dc | docs/field_verification/{YYYYMMDD}/raw_event_dc.json | 东财-datacenter(英文键) |
| macro_dc | active | em.datacenter | collect_macro_dc | docs/field_verification/{YYYYMMDD}/raw_macro_dc.json | 东财-datacenter(英文键) |
| research_sina | active | sina.research | collect_research_sina | docs/field_verification/{YYYYMMDD}/raw_research_sina.json | 新浪(扩展API) |
| news_wscn_cctv | active | cctv.news | collect_news_wscn_cctv | docs/field_verification/{YYYYMMDD}/raw_news_wscn_cctv.json | — |
| sse_e_interaction | active | sse.e_interaction | collect_sse_e_interaction | docs/field_verification/{YYYYMMDD}/raw_sse_e_interaction.json | — |
| etf | active | sse/szse.etf_shares | collect_etf | docs/field_verification/{YYYYMMDD}/raw_etf.json | — |
| st_list | active | em.clist | collect_st_list | docs/field_verification/{YYYYMMDD}/raw_st_list.json | 东财-clist |

registry.sources 中非 `source_fields` 身份的目录条目：

| registry.sources 条目 | 说明 |
|---|---|
| AxData | registry.sources catalog entry is not an item in source_fields; retain as registry metadata, not as a field identity. |
| 东财-push2_full | registry.sources catalog entry is not an item in source_fields; retain as registry metadata, not as a field identity. |

## 日期门槛与实测状态

- 选择性正式目录 `docs/field_verification/20261009/` 已创建；它不是全项目全源采集目录。ZHB、ELTDX、AxData 短线记录分别提供 `20261009`、`2026-10-09`、`20261009` 来源日期证据；腾讯报价时间及 KPH 指定日期也指向 2026-10-09。
- TDX 行情快照、CLS 市场情绪、TDX 实时快照缺少可用的响应日期；这些样本不能用于同日交易数据定案。CNINFO 互动易按自然日事件分析，不套用股票交易日窗口。
- 当前环境已安装 `axdata==0.1.4`，与 `requirements.txt` 一致。AxData 短线 2/20 北交所记录为空；本次只报告部分成功，没有追加请求。
- 项目短线接口使用项目 ZHB 缓存；本次 AxData/ELTDX 成功样本均报告 2026-10-09 统计日。原报告关于最新缓存仅到 2026-09-30 的说法已被本次实际日期输出取代。

## 2026-10-10 后续受控验证

以下验证继续使用项目已归档的收盘样本；只有为完成明确的同源对照才追加了少量 AxData 查询。所有交易日都显式带入接口参数或用响应日期核验。测试期间未运行 `--all`，未请求 Eastmoney push2，也未遇到 403、429 或源端封禁。一次默认沙盒网络连接先返回 Windows `10013`，在已授权的升级执行环境中完成了同一项只读请求；该错误是本机沙盒套接字权限，不是 KPH 源端拒绝。

### 静态全表与实测范围

静态映射仍覆盖 257/257 个目录接口、3,343/3,343 个字段出现项、26 个主字典来源身份、35 个运行源名和 2,469 条主字典字段路径。257 个接口状态为：1 个直接调用、88 个同源族候选、141 个当前项目无对应路线、21 个同端点候选、5 个同提供方不同端点、1 个流接口。字段出现项中有 931 个 AxData-only 名称/路径候选、609 个不适用于本项目当前 A 股数值范围的字段、1,803 个仍待核实字段；931 不是“931 个已证实新增字段”。其中按类型初筛有 180 个数值型 AxData-only 候选，仍混有期权、债券、期货、ESG 等业务，不能直接当作项目待纳入清单。

实测按“已有项目同源数据可直接比较”或“静态表显示有 A 股数值补充可能”筛选，不对 257 个接口一律发网路请求。下表区分字段语义已形成跨日证据、只是一次或单期候选、以及接口返回质量不足；未实测接口仍保留在逐接口静态表中，不会被整体判成重复。

### 已形成跨样本关系的内容

| AxData 接口/字段组 | 对照数据与结果 | 关系结论 |
|---|---|---|
| `kph_market_emotion` 汇总值 | 2026-09-28、09-29、09-30 三个交易日：涨/跌家数分别与 KPL 精确相同；总涨停/跌停数与 CLS 精确相同；非 ST 涨停/跌停与 KPL 精确相同；ST 数等于 CLS 总数减 KPL 非 ST 数；`flat_count + CLS suspend_num = CLS flat_num` 三日精确成立；成交额与 KPL `total_amount_wan` 三日精确相同。 | 核心汇总字段重复或可由项目字段计算。AxData `total_amount` 实际单位是万元，不能按接口文字描述的原始元使用。 |
| `kph_market_emotion` 的 1% 涨跌分布 | 同三日将 AxData 相邻两个 1% 桶合并后，与 CLS 2% 桶的差值落在 -4 至 +3；最高档用未落入前八个桶的计数补齐后，差值落在 -1 至 0。 | 在该市场情绪接口内，1% 桶是唯一明确的数值粒度增量，值得保留为候选；边界、极端涨跌和剩余项定义仍需上游契约确认，暂不晋升主字典。 |
| `kph_limit_up_history` | 09-29 AxData 50 行，项目 KPL 明细 47 行，45 只重叠证券的 6 个数值字段全部 45/45 精确匹配；09-30 AxData 47 行、项目 40 行，40 只重叠证券的 6 个字段全部 40/40 精确匹配。两日并集分别比项目明细多 5 行和 7 行；09-29 项目另有 2 行未被 AxData 返回。 | 这是一项有跨证券、跨交易日证据的补充明细，最适合后续作为 KPL 明细的增量补充来源；两日返回均少于全市场涨停数 57、52，不能取代原源或称为完整全集。 |
| `kph_limit_down_history` | 09-29 返回 10 个唯一代码、KPL `dt_num=10`；09-30 返回 9 个唯一代码、`dt_num=9`。 | 两日的名单条数与市场汇总数一致；项目没有现成的逐股票跌停明细，因此属于补充候选，但各行数值字段尚无独立逐股票锚。 |
| KPH 涨停/跌停证券身份 | 09-29 涨停样本 `920779` 返回 `920779.SH`/`SSE`；09-30 跌停样本 `920202` 返回 `920202.SH`/`SSE`，且其主题含“北交所”。 | 交易所标识存在内部矛盾。KPH 逐股数据纳入任何生产路线前，必须先按证券代码表纠正并验证交易所；不能拿错误的 `.SH` 标识建立字段身份。 |
| `stock_valuation_metrics_tdx.pe_ttm` 与 `stock_valuation_series_tdx.value`；`pe_percentile` 与 `series.percentile` | 3 只股票 × 3 个交易日（09-29、09-30、10-09），两组值均 9/9 精确相同。 | `pe_percentile` 与同源 PE 序列的 percentile 字段一致，是可继续验证的新数值候选；其回看区间/基准仍未由响应字段说明。PB/PCF/PS percentile 和 PEG 没有得到同级别验证。 |
| `stock_margin_trading_tdx` | 3 只股票 × 2 个交易日，共 6 行；`margin_net_buy` 与项目 `rzjme`、`margin_balance` 与 `rzye` 均 6/6 精确相同。AxData `short_balance` 却 6/6 等于项目 `rqjmg`（融券卖出量差），不等于 `rqye`（融券余额金额）。 | 前两个字段是重复校验值。AxData 的 `short_balance` 名称与实际映射不符，不能按融券余额纳入；该映射应向 AxData 上游反馈。 |
| `stock_auction_result_history_tdx` | 09-30、10-09 各 3 只股票，与同日项目 ELTDX 开盘数据对照：价格 6/6 精确相同，成交量差不超过 0.003 手，成交额差不超过 5 元；9 个 AxData 行的 `amount = price × volume × 100` 均成立。 | 价格、成交量、成交额都是项目已采字段的重复值。`order_count` 是现有路径未覆盖的数值候选，但意义/计数对象尚无锚，只建议进入短期碰撞样本，不直接进主字典。 |

### 有补充价值但不适合每日采集的内容

| AxData 接口/字段组 | 实测证据 | 建议 |
|---|---|---|
| `stock_financial_statement_tdx` / `stock_financial_report_sina` | TDX 财报接口一次样本覆盖 3 只股票、290 个报告期记录；Sina 资产负债表每只返回 141 条项目记录。对 600519、000568、300031 同一 2026-06-30 报告期的 9 个共同数值项目，Sina 与 TDX 共 27/27 精确相同。Sina 每股记录约有 50–52 个数值叶项目。 | 共享项目可判为重复；更多报表明细和同比项可用于财报字段扩展与语义锚定。值得做季报发布后的按需/季度采集，不应每天重复抓 141 条/股，也不建议长期同时保留两个完全重叠的整表源。 |
| `stock_hold_num_cninfo` | 单次请求返回 5,253 条全市场记录；与项目 20 股样本有 18 只匹配，当前股东人数 15/18 精确相同，3 个差异代码在项目 09-29、09-30、10-08、10-09 的 TDX 快照中保持不变。CNINFO 的 `report_date=20260630` 明确，而项目 TDX 字段本身无报告期标记。18/18 的 `avg_holding` 与“总股本 × 10,000 / 股东人数”差异小于 0.1%。 | 当前人数不是完全同值的替代源；时间戳差异仍未解释。平均持股数是总股本和人数的派生值。前期人数等字段有季度历史用途，但接口返回全市场大表，不适合每日重复采集。 |
| `stock_share_change_cninfo` | 对 600519、000568 各查 2026 年单股事件范围，分别返回 2、4 条。600519 的 `total_share/circulating_share` 与项目 09-30 捕获的 TDX 股本字段只差 38.5 股；000568 09-28“激励股份解禁”后，CNINFO `circulating_share=147116.1037` 万股，与项目 09-30 TDX `liutongguben=147116.109375` 万股只差 57.75 股。若错拿 06-30 报表流通股 147106.0137 万股与 09-30 TDX 比，会产生 100,956.75 股差异；接口明确记录的 09-28 解禁事件解释了这项变化。 | 这是值得纳入的低频历史股本事件来源，能还原变动原因、公告日、有效日和限售/流通拆分，并为 TDX 总股本/流通股字段提供日期对齐锚。应按事件/报告期采集，不要每日抓取；当前仅两只股票，字段分类仍需扩样。 |
| `stock_chip_distribution_tdx` | 3 只股票 × 2 个交易日共 6 行，字段包括获利比例、70/90 成本集中度和成本区间；项目字典没有对应的直接路径。 | 有数值研究价值但没有项目锚，暂列候选；若继续，应先验证接口时间参数、边界值和跨日重复性。 |

### 暂不纳入或需先修正的问题

- **短线 AxData 接口可靠性不足。** 2026-10-08 项目采集记录为 20/20 股票无可用 AxData 短线字段；10-09 为 18/20 可用、2 只北交所代码无记录。10-09 的 18 股对 ELTDX 有大量重复值，`opening_rush` 只有 AxData 有值，但目前仅有一个可用交易日，不能据此认为字段更全或已解释。它现在不满足稳定的每日源要求。
- **`cls_stock_kline` 当前返回不可用。** 600519 的 50 个交易日记录里，`open/high/low/close/volume/amount/change_pct/secu_name` 50/50 为空；仅 `change` 有值。修正 AxData 适配映射并复测前不纳入。
- **腾讯 `tencent_realtime_snapshot.pe_dynamic` 疑似 AxData 标签错配。** 600519、000568、300031 三只证券的 AxData 与项目原始腾讯 `quote_time` 逐只完全相同；三只的 AxData `pe_dynamic` 都等于腾讯原始 `[39]`，且也等于同日项目 TDX `pe_ttm`（3/3）。它们都不等于原始 `[52]` 动态 PE 或 `[53]` 静态 PE。主字典 `[39]=PE(TTM)`、`[52]=动态 PE`、`[53]=静态 PE` 的分配获得了跨证券支持；应将疑点记在 AxData 输出名称，不要把其 `pe_dynamic` 误加为另一个动态 PE 字段。此验证是同日 3 股，仍非跨日 E3。
- **`kph_wind_vane_history`** 只有单日 26 行，当前项目没有逐股票对应路线；其若干涨停相关时间/封单字段为零，其他资金/成交字段尚无独立锚，不建议纳入日常采集。
- **Eastmoney push2 未验证**：保持冻结。静态端点相似不代表已经恢复或等价；未确认恢复前不请求，也不由其他东财接口的状态推断它的状态。

## 更新后的去重/补缺结论

1. **主字典没有可删除来源或字段的证据。** 多个 AxData 接口与现有值相同，说明分析/碰撞冗余，不代表主字典中不同来源身份可合并；继续保留完整来源和路径。
2. **KPH 涨停明细已作为 KPL 的补充采集接入。** 两个交易日、85 只重叠股票的六字段逐值一致，KPH 分别补充 5、7 行；它不是完整涨停名单，不能替代 KPL。北交所代码被报为沪市的问题仍未由上游修正，采集器只按六位证券代码对齐、单独保留异常标识并告警；应继续观察后续交易日覆盖。1% 分布仍待解释相邻桶映射误差与边界，未接入日常采集。
3. **跌停逐股列表值得作为影子数据验证，不宜立即替换项目字段。** 两日数量与 KPL 汇总精确相符，但股票级字段尚无独立对照，且存在北交所标识异常。
4. **可继续用于数值破解的候选**：PE percentile（同源序列对照 9/9，但窗口未明）、拍卖 `order_count`（重复 3 股×3 日，但意义未定）、TDX 筹码分布（3 股×2 日，无项目路径）。三者目前只进入候选采集/碰撞队列，不写入主字典。
5. **低频扩展优先项是 `stock_share_change_cninfo`。** 该接口按单股、日期范围返回股本事件；两股样本显示 2026-09-28 限售股解禁与项目 09-30 TDX 流通股本仅差约 58 股，能解释把 06-30 报表值直接对比 09-30 快照时产生的约 10.1 万股差异。建议按事件日期或报告期纳入低频研究采集。整表财报可按季报节点抽样；`stock_hold_num_cninfo` 的人数差异尚未解释，平均持股数又可由现有股本/人数推得，两者都不应成为每日主源。
6. **不纳入**：KPH 汇总中已重复的总数、成交额、ST/非 ST 数；可由股本和现价推得的市值；价格涨跌停公式值；平均持股数；融资融券已重复的余额和净买入。AxData `short_balance` 的错误命名、CLS K 线空列、短线接口间歇无数据均需先解决。
7. **剩余接口的结论边界**：257 个接口和全部字段出现项已静态逐项映射，但没有对 257 个接口进行网络实测。对债券、期权、基金、期货、ESG、指数、新闻及项目目标外的其他接口，静态表保留路线与字段证据；除非后续目标明确扩展到这些资产/业务，不为“凑满实测数量”发请求。其余 A 股数值接口按静态候选、数据日期、项目同源路径和请求成本排序，逐组补证。

## 证据等级口径

- E0：目录、名称或路径命中，只是候选。
- E1：上游和项目源码均能追到具体调用/端点/协议/参数/返回路径，可判断静态路线关系，不证明值等价。
- E2：受控样本支持结构或字段关系，但缺少跨交易日/报告期重复验证，或关键定义尚未定案。
- E3：跨证券、跨交易日/报告期的值关系与具体接口/字段路径相符；只对该已核实关系成立，不自动证明其他同名字段或其他日期。

本补充验证将 KPH 市场汇总的重复/派生关系、KPH 涨停明细 6 个字段的逐行匹配、TDX PE percentile 与序列 percentile 的一致性、以及两日融资融券现有映射列为 E3 关系；字段窗口、缺行原因和错误交易所标识仍保持未解决。

## 本轮落实（2026-10-10）

- 采集器新增 `kpl` 与 `kph` 独立来源输出。原有 KPL 明细请求从 `market_sources` 拆出写入 `raw_kpl.json`，调用次数仍为一次；AxData `kph_limit_up_history` 通过项目公开适配器单次请求、`persist=False`、不重试，并写入 `raw_kph.json`。KPH 天梯返回 403、429、封禁或限流信息时跳过 KPH 历史请求；此路径不访问 Eastmoney push2，也不运行 `--all`。
- KPH 查询日按 ZHB 补充交易日历选择，且严格早于自然日“今天”；KPL 的数据日由逐股 `zt_time` 推导。两源均把实际交易日写入 raw 和逐源 `as_of_date`，不以采集目录日期代替来源日期。北交所 `.SH`/`SSE` 异常单独留在 `identity_observations`，不进入碰撞数值。
- KPH raw 保留所有有限数值字段，未定案字段仅作为后续研究候选；本次只将有双交易日证据的 6 组对应关系登记为 verified，共 12 条来源字段路径。新增路径已进入主字典生成投影、字段矩阵和独立性锚；统计状态为 28 个来源身份、36 个运行源名、2,481 条来源字段路径。`field_source_reference.md` 历史协议原文保持不变。
- 本轮版本升至 `17.4.33`；README、采集脚本说明、AxData 交叉表和 Changelog 同步更新。此处的实现状态不改变上文静态映射候选等级，其他 AxData 接口和未确认字段仍留待后续验证。
- 验证：采集探针 52/52、碰撞 26/26 定向用例通过；7 个修改 Python 文件 `py_compile` 与 Black 检查通过；5 个修改源码文件 MyPy 零错误；registry parity、字段字典/矩阵生成检查、A1 数据访问闸门和 A7 字典同步闸门通过（0 HARD FAIL / 0 WARN）。
- 全量离线套件收集 788 项、排除 47 个真实网络用例后有 741 项待执行，但运行停在 `tests/infra/test_main_scheduler.py::test_missing_report_script_is_failure`，无后续输出。隔离测试及不导入项目的最小 `asyncio.run()` 探针也未进入协程，因此全量套件结果记为未完成，不报告为通过。

## 执行边界

- 初始静态审查阶段未改代码；之后用户另行授权了 KPH/KPL 采集器和主字典增补。本次不更改碰撞算法、依赖约束或 AxData 其余接口的采集状态。
- 未运行真实网络采集；未运行 `--all` 或 Eastmoney push2。未提交 Git。开始时已有的 `docs/field_verification/collision_state.json` 和 `docs/field_verification/20261008/` 继续保留。
- 全量离线验证因 Windows Python 启动器下 `asyncio.run()` 探针停滞而未完成；采集与碰撞相关定向回归、静态治理闸门均已完成。
- `.tmp/axdata_field_reconciliation_20261010_baseline/` 基线快照保留，未清理；工作区现有其他改动未重置或覆盖。
- 已按此前授权使用 PowerShell 7.6.5 兼容例外；仓库默认 Windows PowerShell 5.1 规则仍适用。

## 每日验证覆盖边界与重跑行为

- 全表 257 个接口、3,343 个字段出现项的静态映射已完成；真实值验证仅对报告列明的路径和样本成立。每日主动探针仍固定为 `tencent_realtime_snapshot`，逐个数据日轮换一只已成功采集的项目股票；它不会自动遍历其余 AxData-only 候选接口。其余接口需先确认参数、日期字段、底层提供方和请求成本，再加入明确白名单。
- 当天第二次默认完整收盘采集会跳过主源重采，并从现有 raw 刷新/补齐 AxData 与 Levistock 验证摘要。已有 `axdata_validation.json` 和 `.tmp` 数据日状态会保持原样，保证每个交易日最多一次主动探针；`--overwrite` 只重采选定的主源，也不会清除这些每日验证证据。
- AxData 每日锁在正常退出时移除；若进程异常终止，超过 30 分钟的锁会在后续调用时通过原子改名回收。锁恢复不清除“当天已尝试”的状态，因此不会因此重发请求。


## 每日轮验覆盖与同日重跑

- 静态映射覆盖 257/257 个接口与 3,343/3,343 个字段出现项；每日网络探针固定为 `tencent_realtime_snapshot`，逐交易日轮换样本股，并不轮询全部 257 个接口。其余候选仍须根据静态路由和价值安排分类实测。
- 当日重跑会跳过主采集并使用已保存 raw。如果前一轮已经发起请求，证据或全局日状态会阻止重复；如果前一轮仅因对照源暂缺等原因跳过且没有发请求，恢复后可同日重新评估。
