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
- [`adjudications/20261108_zhb_tdxstat2_metadata_followup.md`](adjudications/20261108_zhb_tdxstat2_metadata_followup.md)：区分旧字段解释证伪与运行路径状态；复核 14 个竞价/封单兼容路径、250/30 根日K周期、参考字段未定状态、混合 TDX 板块代码，并同步统一层字段元数据。
- [`research/20261108_zhb_tdxstat_contract_alignment.md`](research/20261108_zhb_tdxstat_contract_alignment.md) 与 [`adjudications/20261108_zhb_tdxstat_contract_alignment.json`](adjudications/20261108_zhb_tdxstat_contract_alignment.json)：按 ZHB 文件名数据日对齐 11 个保留期日期与 ELTDX `stats_date`，核实 `[2]/[26]/[31]/[32]` 并解决 `stat.unknown_26` 的同源别名状态冲突；不增加跨源映射。
- [`research/20261108_zhb_tdxstat_slow_fields.md`](research/20261108_zhb_tdxstat_slow_fields.md) 与 [`adjudications/20261108_zhb_tdxstat_slow_fields.json`](adjudications/20261108_zhb_tdxstat_slow_fields.json)：按文件名数据日复核 11 个保留期 ZHB 样本，定案 `dividend_yield`、`employee_count` 两条路径为同源已验证字段的精确别名；不推断员工人数报告期或股息率公式。

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
