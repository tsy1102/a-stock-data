# 字段实测验证（Field Verification）

本目录保存固定股票池的多源原始采样、来源元数据、字段碰撞和人工复核证据，用于发现字段未知、错义、单位差异与来源映射问题。日常执行从 [`DAILY_RUNBOOK.md`](DAILY_RUNBOOK.md) 开始。

## 权威规则

- [`COLLISION_RULES.md`](COLLISION_RULES.md)：由 `scripts/collision_rules.py` 生成，镜像当前运行时碰撞阈值与状态机。
- [`CRACKING_METHODOLOGY.md`](CRACKING_METHODOLOGY.md)：候选生成、数据拆解和常见误判；按需读相关章节，不替代运行时阈值。
- [`EVIDENCE_COVERAGE.md`](EVIDENCE_COVERAGE.md)：字段覆盖、交易日/自然日、来源日期与证据边界。
- [`ADJUDICATION_WORKFLOW.md`](ADJUDICATION_WORKFLOW.md)：跨源关系、单源契约核验与注册表写回。
- [`PUBLIC_WEB_VERIFICATION.md`](PUBLIC_WEB_VERIFICATION.md)：每日采集和碰撞后优先核验登记来源的官方网站（通达信、同花顺、东方财富、新浪、开盘啦、开盘红等），以及第三方次级佐证的证据边界。
- [`review_templates/candidate_review_template.json`](review_templates/candidate_review_template.json)：人工候选审阅决定模板；审阅台账按需生成，默认不创建空状态文件。
- [`../../scripts/README.md`](../../scripts/README.md)：采集源顺序、限流、候选接口日轮和冗余退出/复验条件。

## 当前调查计划

- [`20261111_finance_candidate_crosscheck.md`](20261111_finance_candidate_crosscheck.md) 与 [`20261111_finance_extended_candidate_crosscheck.md`](20261111_finance_extended_candidate_crosscheck.md)：按拼音/英文先生成候选，再用 ELTDX v3.3.2 来源契约、2026Q3 公开报告、单位和报告期独立核对；确认来源内财务语义，不建立跨源映射。发起人法人股、法人股和主营利润路径的冲突仍保留。
- [`20261111_eltdx_share_raw_crosscheck.md`](20261111_eltdx_share_raw_crosscheck.md)：先由名称提出 B 股、H 股和原始财务主体候选，再以 ELTDX v3.3.2 0x0010 契约、136/143 字节结构、保留样本及发行人股份数据核验；只确认 ELTDX 来源内定义，不新增跨源映射。
- `ZHB-tipinfo::[17]/[18]`：16 个保留期归档、90,471 行的全市场检查均为空，但没有 `tipinfo.dat` 的官方位置映射；保留未验证状态。细节见 [`20261110/zhb_tipinfo_17_18_followup.md`](20261110/zhb_tipinfo_17_18_followup.md) 及逐包哈希审计表。
- 东财 push2 多主机字段差异：仅在用户明确安排真实联网核验后，以低频逐主机小样本比字段、数值和来源日期。先核验备用域；首次出现 403、429、封禁或熔断迹象即停止该风险组，不运行 `--all`。历史健康探测只代表当时可达，不证明字段等价或当前健康。
- [`f118_ulist_source_semantics_plan.md`](f118_ulist_source_semantics_plan.md)：区分 push2 与 ulist239 的 `f107` / `f118` 逐源身份、含义和占位状态；计划未执行前不更新注册表。
- [`efinance_eastmoney_review_20261105.md`](../efinance_eastmoney_review_20261105.md)：对照 efinance 的 Ulist 字段映射与本项目端点；对 `600000` 的两个 Ulist 主机各做一次限流内实时请求，均 HTTP 200，五个字段一致，`f124` 两端 Unix 时间戳相差 30 秒，`f297` 均为 `20261105`。再核对 2026-11-02/03 的 Ulist 与 `stock/get::f86` 历史样本后，Ulist `f124` 已按完整来源路径纠正为“行情更新时间戳（Unix 秒）”，旧参考记录保留；`push2 stock/get::f124` 仍未验证。另一次 `push2delay` 请求返回 `None`，未重试，DNS/连接失败层尚不能区分。FlClash 主机 DNS 与 TUN 网络路径可用，但 Eastmoney 是否命中 `DIRECT` 规则未证实；未修改网络设置。`f297` 仅有单日单票证据，跨日口径仍待查，不接入报告日期或缓存键。
- [`adjudications/20261105_axdata_field_reverse.md`](adjudications/20261105_axdata_field_reverse.md)：逆向登记 AxData 257 个接口的 3,343 个输出字段并与当前逐源字典比对；对项目实际调用的 KPH 历史涨停接口按 8 个交易日、370 组同股样本逐项核验，更新 6 条字段定案并保留 2 条待核字段。TDX 短线接口按 0.1.4 运行时代码追到 TDX/ZHB 输入及派生公式。
- [`adjudications/20261105_collection_cracking_audit.md`](adjudications/20261105_collection_cracking_audit.md)：截至 2026-11-05 的采集、日期归属、碰撞完整性、历史候选审阅与注册表写回闭环审计；记录并修复交易日窗口缺日时回填更早样本的问题。其 KPL 列状态是当日结论，后由 2026-11-06 的历史实证复核更新。
- [`adjudications/20261106_kpl_raw_columns_semantics.md`](adjudications/20261106_kpl_raw_columns_semantics.md)：首次历史复核 KPL 原始列语义；将 `col_15` 定案为当前连续涨停板数、`col_21` 为现价、`col_22` 为当日涨跌幅，并拒绝 `col_15 ↔ KPH.limit_count` 映射。后续复核确认 `Push2EX limit_count ↔ KPL col_15`，同时拒绝将不同来源的 `Push2EX zt_continuous` 与 KPH 连板数字段精确映射。
- [`adjudications/20261106_historical_second_pass.md`](adjudications/20261106_historical_second_pass.md) 与 [`adjudications/20261106_historical_recrack_closeout.md`](adjudications/20261106_historical_recrack_closeout.md)：第二轮使用 2026-10-15 起的保留样本，对照多轮 KPL/AxData/东财历史报告和公开数据；定案 ZHB `change_pct` 及四条精确映射，撤回 Ulist `f190/f192` 旧语义，并将 Push2 `f174` 定义为 52 周滚动最高价；同时拒绝将近似命中误记为逐值等价。
- [`adjudications/20261106_push2ex_kpl_limit_count_mapping.json`](adjudications/20261106_push2ex_kpl_limit_count_mapping.json) 记录 `Push2EX limit_count ↔ KPL raw_columns.col_15` 的三日 271/271 精确映射；[`adjudications/public_web/20261106_em_zt_continuous_kph_probe.json`](adjudications/public_web/20261106_em_zt_continuous_kph_probe.json) 与 [`adjudications/20261106_historical_recrack_zt_continuous_candidate_review.json`](adjudications/20261106_historical_recrack_zt_continuous_candidate_review.json) 记录 `zt_continuous ↔ KPH limit_count` 的日期对照反例及拒绝裁决。
- [`adjudications/20261106_historical_recrack_semantic_adjudication.md`](adjudications/20261106_historical_recrack_semantic_adjudication.md)：在完整 16 日历史报告、往期候选与发行人公告核证基础上，新增 ZHB 静态 PE、YTD、250 日变动及 Ulist239 `f133` 的来源内语义定案；拒绝五条精确跨源映射并保留一个研究前沿项，不将近似值映射为同义字段。公开网页核证见 [`adjudications/public_web/20261106_public_web_research.md`](adjudications/public_web/20261106_public_web_research.md)。
- [`adjudications/20261106_historical_recrack_round2_supplement.md`](adjudications/20261106_historical_recrack_round2_supplement.md)：按 2026-10-15 数据保留起点复跑历史碰撞；新增 ZHB `full.high_52w` → `stat2.high_52w` 的同源别名定案（260/260），排除 2026-10-14 样本，维持 Push2/Tencent 精确映射拒绝结论，并记录 Eastmoney 网页回查的日期边界。
- [`adjudications/20261107_historical_recrack_final_closeout.md`](adjudications/20261107_historical_recrack_final_closeout.md)：再次按保留起点全量重破解，以东财官方网页/接口定案 Ulist `f142/f143` 与 Push2 `stock/get::f192` 的来源语义，复验既有盘口映射并记录未决候选和人工审阅余量。
- [`adjudications/20261107_historical_large_recrack_second_pass.md`](adjudications/20261107_historical_large_recrack_second_pass.md)：后续大规模历史再破解；补正 Ulist `f13/f27` 已验证语义回归，以 80 组保留期样本确认市场标志与同源别名，复核全部 48 条正式 L4 候选并重跑最终正式报告（29 条拒绝、19 条待外证）。
- [`adjudications/20261107_axdata_shortline_semantic_adjudication.md`](adjudications/20261107_axdata_shortline_semantic_adjudication.md)：以 AxData 实际调用的 TDX 短线接口契约和保留历史样本，登记 34 条来源内字段语义；8 条高价值候选中 3 条接受语义关系、5 条按口径或量纲反证拒绝。公开接口字段快照见 [`public_web/20261107_axdata_shortline_interface.md`](adjudications/public_web/20261107_axdata_shortline_interface.md)。
- [`adjudications/20261107_historical_recrack_third_pass.md`](adjudications/20261107_historical_recrack_third_pass.md)：在前几轮基础上再次全历史碰撞，以东财公开页面与腾讯接口核实五档买量，更新精确注册表语义并完成人工 L4 收敛；记录未同步样本日期、未决候选和运行时单位边界。
- [`adjudications/20261108_zhb_tipinfo_market_code.md`](adjudications/20261108_zhb_tipinfo_market_code.md)：以 2026-10-15 起保留的 15 个日期化 ZHB 压缩包和通达信官方市场枚举核实 `ZHB-tipinfo::[0]` 为市场代码（0=深、1=沪、2=京）；`[17]/[18]` 在保留样本中仍全空但用途未定。
- [`adjudications/20261108_zhb_tdxstat2_fields.md`](adjudications/20261108_zhb_tdxstat2_fields.md)：以 15 个保留期日期化 ZHB 包和通达信官方接口文档，定案 `tdxstat2` 开盘竞价、成交额、涨跌停封单字段；纠正主力流入误名、万元单位和回测历史日期回退。
- [`adjudications/20261109_zhb_tdxstat2_30bar_formula.md`](adjudications/20261109_zhb_tdxstat2_30bar_formula.md)：以 20 只股票、5 个数据日的 100 组日K对照，定案 `change_30k_bar` 的 lag-29 与 `change_30k_bar_ref` 的 lag-30 收盘价基准公式；保留 600825 的五组未解释异常，不创建跨源映射。
- [`adjudications/20261108_zhb_tdxstat2_metadata_followup.md`](adjudications/20261108_zhb_tdxstat2_metadata_followup.md)：区分旧字段解释证伪与运行路径状态；复核 14 个竞价/封单兼容路径、250/30 根日K周期、混合 TDX 板块代码，并同步统一层字段元数据。文中 `change_30k_bar_ref` 未定结论为当时状态，已由 2026-11-09 公式定案更新。
- [`research/20261108_zhb_tdxstat_contract_alignment.md`](research/20261108_zhb_tdxstat_contract_alignment.md) 与 [`adjudications/20261108_zhb_tdxstat_contract_alignment.json`](adjudications/20261108_zhb_tdxstat_contract_alignment.json)：按 ZHB 文件名数据日对齐 11 个保留期日期与 ELTDX `stats_date`，核实 `[2]/[26]/[31]/[32]` 并解决 `stat.unknown_26` 的同源别名状态冲突；不增加跨源映射。
- [`research/20261108_zhb_tdxstat_slow_fields.md`](research/20261108_zhb_tdxstat_slow_fields.md) 与 [`adjudications/20261108_zhb_tdxstat_slow_fields.json`](adjudications/20261108_zhb_tdxstat_slow_fields.json)：按文件名数据日复核 11 个保留期 ZHB 样本，定案 `dividend_yield`、`employee_count` 两条路径为同源已验证字段的精确别名；不推断员工人数报告期或股息率公式。
- [`research/20261108_zhb_tdxstat_metadata_aliases.md`](research/20261108_zhb_tdxstat_metadata_aliases.md) 与 [`adjudications/20261108_zhb_tdxstat_metadata_aliases.json`](adjudications/20261108_zhb_tdxstat_metadata_aliases.json)：按 2026-10-15 起保留的 11 个数据日期与 220 组去重股票日样本，确认 `tdxstat`/`tdxstat2` 代码、日期、市场别名及 `tdxstat2.change_mtd` 同源别名；不新增跨源映射。
- [`research/20261108_zhb_tdxstat_semantic_corrections.md`](research/20261108_zhb_tdxstat_semantic_corrections.md) 与 [`adjudications/20261108_zhb_tdxstat_semantic_corrections.json`](adjudications/20261108_zhb_tdxstat_semantic_corrections.json)：根据 ZHB 解析器位置契约和 11 个保留数据日，纠正七项 `tdxstat` 已验证字段的旧语义/单位，并确认八项 `tdxstat`/`tdxstat2` 同源别名；区分上市后首次开板日期与限售股解禁日期，不新增跨源映射。
- [`adjudications/20261109_zhb_tipinfo_financial_fields.md`](adjudications/20261109_zhb_tipinfo_financial_fields.md)：以 15 个保留期 ZHB 包的 84,815 行解析对应及三家发行人半年报、三季报和官方个股日历，定案 `report_period`、累计 `eps` 与预约 `disclose_date`；不推断 EPS 基本/稀释子口径，不将预约日当作实际公告时间，也不新增跨源映射。
- [`adjudications/20261109_zhb_tipinfo_runtime_aliases.md`](adjudications/20261109_zhb_tipinfo_runtime_aliases.md)：以 15 个保留期 ZHB 包的 84,815 条逐行审计定案 `code`、`zt_date_recent`、`hg_date`、`hg_amount_yi` 与原始列别名；补齐日期/金额单位，按通达信官方快照契约收窄涨停与回购日期说明，不声称 `RecentHGAmo` 是官方公开字段映射。
- [`adjudications/20261110_zhb_tipinfo_date_aliases.md`](adjudications/20261110_zhb_tipinfo_date_aliases.md)：以 15 个保留包、84,815 行解析器对照和通达信官方字段说明，定案 `forecast_date_recent` 与 `equity_incentive_date` 为原始列 `[11]`、`[21]` 的同源运行别名；官方股票页面和发行人公告作语义佐证，不新增跨源映射。
- [`adjudications/20261110_zhb_tipinfo_remaining_aliases.md`](adjudications/20261110_zhb_tipinfo_remaining_aliases.md)：补出 `forecast_type`、`suspend_major_event_date` 到原始列 `[12]`、`[7]` 的解析器直通别名，15 个保留包共 84,815 行、零差异；确认停牌起始日语义，业绩预告类型仅确认代码字段角色，不扩展未定案码表。
- [`adjudications/20261109_zhb_tipinfo_shareholder_columns.md`](adjudications/20261109_zhb_tipinfo_shareholder_columns.md)：以 15 个保留包、84,815 条逐行样本和三类公开权益变动公告，修正 `[8]/[9]` 被旧业绩预告解释遗留为 `disproved` 的状态错误；旧 `div_*` 别名仍保持证伪。
- [`adjudications/20261109_tdx_snapshot_dates.md`](adjudications/20261109_tdx_snapshot_dates.md)：更正 11 个日期字段的接口归属为 `get_more_info_batch`（旧报告误写为 `get_market_snapshot_batch`）；字段语义不变，官方未注明日期格式，不补造项目采集或跨源映射。
- [`adjudications/20261109_tdx_snapshot_quote_fields.md`](adjudications/20261109_tdx_snapshot_quote_fields.md)：依据通达信官方 `get_market_snapshot_batch` 字段表定案 21 个基础行情字段；保留文档未注明的单位和涨速窗口，不推断项目采集路径或跨源映射。
- [`adjudications/20261109_tdx_more_info_fields.md`](adjudications/20261109_tdx_more_info_fields.md)：依据通达信官方 `get_more_info_batch` 字段表定案 77 个已登记的来源内语义；逐项保留单位、编码、算法和口径边界，不把未登记的四个期货/期权字段补入项目，也不声称项目实际采集。
- [`adjudications/public_web/20261109_tdx_more_info_fields.md`](adjudications/public_web/20261109_tdx_more_info_fields.md)：记录 TDX 官方接口分节及万科、平安银行 2026 三季报对 ZHB `[25]`、`[34]` 账务字段名称与万元单位的交叉核验。
- [`adjudications/20261109_zhb_accounting_metadata_corrections.md`](adjudications/20261109_zhb_accounting_metadata_corrections.md)：以 2026-11-06 保留 ZHB 文件和两家发行人的官方三季报，纠正 `ZHB-tdxstat::[25]`、`[34]` 的字段名与单位；解析值和兼容键不变。
- [`adjudications/20261110_zhb_tipinfo_public_crosscheck.md`](adjudications/20261110_zhb_tipinfo_public_crosscheck.md) 与 [`adjudications/20261110_zhb_tipinfo_forecast_code_samples.csv`](adjudications/20261110_zhb_tipinfo_forecast_code_samples.csv)：补充 15 个保留 ZHB 包中的 230 条去重 `[12]` 取值事件及发行人公告核验；更正 `3=略增`、`10=略减`、`14=续亏` 旧推测，记录 `6=首亏`、`8=扭亏`、`9=减亏` 的强候选和码值重叠边界。没有公开的 ZHB 整数码表，故不改变注册表状态。
- [`adjudications/20261110_zhb_change_60d_alt_path_retirement.md`](adjudications/20261110_zhb_change_60d_alt_path_retirement.md)：按来源日期和日期化 ZHB 归档名筛选 15 个保留 raw 文件、去重为 11 个交易日；旧键 `change_60d_alt` 未在样本或当前解析器出现，退役该历史路径并保持当前 `change_60d` 定案不变。
- [`adjudications/20261109_tdx_order_book_price_levels.md`](adjudications/20261109_tdx_order_book_price_levels.md)：依据通达信官方五档盘口契约和项目适配路径，定案 TDX `bid2..bid5` / `ask2..ask5` 的来源内含义；300 条保留期 TDX 原始记录均无深档样本，故不登记跨源映射，并保留官方未注明的单位边界。

- [`adjudications/20261109_eltdx_chang_qi_fu_zhai.md`](adjudications/20261109_eltdx_chang_qi_fu_zhai.md)：基于 TDX 官方 FINANCE(16) 定义、ELTDX v3.3.2 FinanceRecord 路径和三只股票 H1/Q3 报表，定案该适配层路径为千元口径少数股东权益；记录上游文档误标、浮点/来源精度差及原生 TDX 注册冲突边界。
- [`adjudications/20261110_tdx_finance_source_contract.md`](adjudications/20261110_tdx_finance_source_contract.md)：按 ELTDX v3.3.2 TDX `0x0010 FinanceRecord` 契约定案 `TDX(双命名源)` 的 9 条财务原始/派生路径；16 组同日采集、320 条股票日记录对照五组原始值，派生字段仅依据上游明确公式定案，不新增跨源映射。
- [`adjudications/20261110_tdx_xdxr_source_contract.md`](adjudications/20261110_tdx_xdxr_source_contract.md) 与 [`adjudications/20261110_tdx_xdxr_unit_audit.csv`](adjudications/20261110_tdx_xdxr_unit_audit.csv)：按 ELTDX v3.3.2 `0x000f` category 1 契约定案四条 TDX 权息字段；两条交易所公告核对现金分红样本，并修正适配器把每10股金额当每股金额的十倍单位错误；不新增跨源映射。
- [`adjudications/20261109_eltdx_kline_ohlc.md`](adjudications/20261109_eltdx_kline_ohlc.md)：依据 ELTDX v3.3.2 `0x052d` KlineBar 路径、通达信官方 OHLC 定义/元单位和 2026-10-15 起三批 300 条留存日 K 样本，分别定案适配层 `open/high/low/close`；纠正旧合并释义及空单位，不建立跨源映射。
- [`adjudications/20261109_eltdx_kline_followup.md`](adjudications/20261109_eltdx_kline_followup.md)：依据 ELTDX v3.3.2 KlineBar 契约和四个日期共 400 条保留日 K 的毫厘价/成交量/差分实证，定案 14 条来源内字段；`amount`、`amount_raw`、`volume_raw` 因同名字段跨对象且注册表键无法隔离路径而继续留在未知队列，不建立跨源映射。
- [`adjudications/20261109_eltdx_quote_snapshot_fields.md`](adjudications/20261109_eltdx_quote_snapshot_fields.md)：依据 ELTDX v3.3.2 `0x054c/0x054b` 快照与分类行情契约、20 只股票当日样本，定案 `total_hand`、`current_hand`、`inside_dish`、`outer_disc`、`open_amount_yuan`；`current_hand` 单位仍未证实。
- [`adjudications/20261109_eltdx_category_rank_fields.md`](adjudications/20261109_eltdx_category_rank_fields.md)：依据 ELTDX v3.3.2 `0x054b` 分类行情契约和当日 80 条记录，定案 10 个排名字段，复算 `change_pct` 公开公式 80/80 完全一致；未补造未知单位或算法。
- [`adjudications/20261109_eltdx_shortline_fields.md`](adjudications/20261109_eltdx_shortline_fields.md)：依据 ELTDX v3.3.2 ShortlineIndicator 契约和 16 个日期、320 个股票日样本，定案 32 个来源内字段；保留两项单日 ZHB 数值差异及 `open_volume_ratio` 的独立日 K 窗口限制，不建立跨源映射。
- [`adjudications/20261109_eltdx_unified_shortline_fields.md`](adjudications/20261109_eltdx_unified_shortline_fields.md)：核实 11 个统一层 `eltdx_*` 字段到 ShortlineIndicator 缓存字段的映射与默认值边界，纠正当前买一金额注释；因 `opening_rush` 算法、单位和正负方向未公开，保留未知状态并登记报告策略风险。
- [`adjudications/20261110_eltdx_quote_price_fields.md`](adjudications/20261110_eltdx_quote_price_fields.md)：依据 ELTDX v3.3.2 快照/分类行情字段契约、通达信官方快照定义及 2026-11-09 的 100 条历史观测，定案 `last_price`、`pre_close_price`、`open_price`、`high_price`、`low_price`；单位未公开，保持空白，不新增跨源映射。
- [`adjudications/20261110_eltdx_volume_rush_locked_fields.md`](adjudications/20261110_eltdx_volume_rush_locked_fields.md)：依据 ELTDX v3.3.2 字段/7709 契约及 2026-11-09 的 80 条榜单样本，定案 `volume_hand`、`opening_rush`、`locked_amount` 的来源内语义和已公开单位；拆分 `min2_amount`、`opening_rush` 与 `vol_rise_speed` 的旧混合解释，不新增跨源映射，保留 `opening_rush` 算法和信号方向未知。
- [`adjudications/20261110_eltdx_open_and_seal_amount.md`](adjudications/20261110_eltdx_open_and_seal_amount.md)：按 ELTDX v3.3.2 7709/ShortlineIndicator 契约和 2026-11-09 的 80 条榜单样本，定案 `open_amount`、`seal_amount` 均为元口径；明确买一金额与涨停总封单不同，不新增别名或跨源映射。

- [`adjudications/20261110_zhb_schema_tokens_not_fields.md`](adjudications/20261110_zhb_schema_tokens_not_fields.md) 与其逐目录审计 CSV：排除 ZHB 的 6 个精确类型/格式占位符身份；仅检查 2026-10-15 起、来源日期经交易日历确认且有同名归档的 15 个 raw，保留真实未知列 `[17]`、`[18]` 不变。
- [`adjudications/20261110_tdx_type_tokens_not_fields.md`](adjudications/20261110_tdx_type_tokens_not_fields.md)：仅按 TDX 自身字段类型/日期格式文档和解析器键路径排除 5 个完整类型 token 身份（`YYYYMMDD`、`float`、`str`、`byte`、`uint`）；未使用来源 `as_of_date` 未确认的采集 raw，不扩展到 ELTDX 或其他同名来源。
- [`adjudications/20261110_eltdx_type_tokens_not_fields.md`](adjudications/20261110_eltdx_type_tokens_not_fields.md)：按项目固定的 ELTDX 3.3.2 返回模型与 dataclass 序列化路径，排除 4 个精确 Python 类型 token 身份（`bool`、`float`、`int`、`str`）；未读取采集 raw，不扩展到其他来源的同名路径。
- [`adjudications/20261110_eltdx_finance_raw_dates.md`](adjudications/20261110_eltdx_finance_raw_dates.md)：依据 ELTDX 3.3.2 `FinanceRecord` 模型和 0x0010 日期编码契约，确认 `updated_date_raw`、`ipo_date_raw` 为 YYYYMMDD 整数；明确它们是财务记录业务日期，不是采集数据日或来源 `as_of_date`，未读取 raw 样本。
- [`adjudications/20261110_eltdx_special_limit_prices.md`](adjudications/20261110_eltdx_special_limit_prices.md)：按 ELTDX 3.3.2 `SpecialLimitRecord` 和 0x0452 契约拆分并确认 `limit_up_price`、`limit_down_price`；单位未公开，留空；不使用未确认来源数据日的样本或建立跨源映射。
- [`adjudications/20261110_eltdx_trade_tick_contract.md`](adjudications/20261110_eltdx_trade_tick_contract.md)：按 ELTDX 3.3.2 `TradeTick` 契约确认七个上游模型字段；两个竞价量字段固定为 `None`，真实竞价数据来自 `auctions.series`。当前项目采集器未调用成交接口；不读取未核日期样本、不恢复路由或建立碰撞锚。

## 归档格式

```text
docs/field_verification/<目标数据日>/
├── raw_<source>.json
├── meta.json
├── <报告日>_collision_report.md/.json
└── analysis.md（可选人工分析）
```

目录名表示目标数据日，不一定是运行自然日。`meta.json` 保存实际运行时间、`capture_date/run_date`、`data_date`/日期域、市场阶段、来源状态和各自 `as_of_date`。保留期内目录按原名维护，不通过重命名目录来“修正”来源日期；可读数据范围以根目录 `AGENTS.md` 为准，ZHB 日期归属按每日运行卡和解析器契约核实。

schema 5 碰撞 JSON 为候选保存稳定 `candidate_id`；人工处置单独进入 `collision_candidate_reviews.json`，不会自动写入主字典。每条决定须引用包含该候选的碰撞报告并保留 SHA-256；审阅覆盖率、未审数量和重复组关系见当次报告的 `candidate_review`。状态文件不存在时代表本轮均为 `unreviewed`，不是人工审阅完成。

Fuyao raw 还保留 `auction_snapshot_meta` 信封摘要；竞价字段仅在源响应成功、来源日期明确且与目标交易日相同、状态确认就绪时参与碰撞。响应时间戳或采集器探测日不能代替来源数据日期；详情见 [`UPSTREAM_COMPATIBILITY.md`](../UPSTREAM_COMPATIBILITY.md)。

## 数据与历史

采集 raw 保留来源原始字段，不做面向报告的单位归一化。重复采集、增量 `--only`、`--overwrite` 与上下文采集的行为见日常运行卡和采集脚本说明。历史日期目录及分析报告用于追溯；当前字段定义以 `../field_dict.md`、逐源 registry 和后续裁决记录为准，旧的静态覆盖/里程碑摘要不代表当前源健康或字段状态。
