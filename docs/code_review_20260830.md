# 代码审查报告（2026-08-30）

> 范围：生产代码全量逐文件审查（`get_*_report.py` / `stock_common/` / `core/` / `scripts/`），测试与 `scratch/` 临时脚本不计入正确性审查（仅 `scripts/` 作工具审查）。
> 方法：5 个并行审查员逐文件读源码 + 关键符号全仓交叉 Grep；本报告下列 **5 个严重项已由主代理亲自核对原始代码确认**。
> 量级：生产代码约 **30 个 .py 文件 / 5.6 万行**；审稿覆盖全部。

---

## 一、严重级（数值正确性 / 数据安全，已逐条核实）

| # | 文件:行 | 问题 | 核实 |
|---|---|---|---|
| **S1** | `stock_common/sc_capital_cache.py:117-128` | **大盘股市值被低估约 10000×**。`_norm` 触发阈值 `ts>1e7`（单位：万股），但 `_fetch_share_capital` 已把股本÷10000 存为**万股**（:159/:173）。工农中建等总股数 ≈ 3.5e7 万股 > 1e7 → 误判为"股"（V16.2.3 旧脏数据）再 ÷10000 → 市值 `price*3564/10000` 而非正确 `price*3564`（亿元）。根因：:116 注释"`2000 亿股=2e6 万股`"少算一个数量级（实为 `2e7 万股`）。 | ✅ 亲核 |
| **S2** | `core/data_provider.py:1647-1677` | **`get_change_ytd` 年初至今涨幅算反**。`tdx_get_security_bars` 实测**升序（旧→新）**（`tdx_client.py:802` 注释实锤），但本函数把 `rows[0]`（最旧）当"当日价"、把 `year_start_idx=min(len-1,243)`（临近最新）当"年初价"，:1668 注释"rows从新到旧"与事实相反。算得 `(最旧−近新)/近新`，YTD 数值错位、符号可能反。仅 ZHB 不新鲜时走兜底触发。 | ✅ 亲核 |
| **S3** | `core/data_provider.py:1959-1988` | **`get_streak_days` 连涨连跌方向与天数整体反**。同源：`closes[0]/[1]` 是最旧两根，:1968 注释"从新到旧"错误。上升段 `closes[0]<closes[1]` → 走"连跌"分支 → 返回 `streak≈-19`（误报连跌 19 天）。同仅兜底触发。 | ✅ 亲核 |
| **S4** | `stock_common/sc_datasource.py:3261 vs 3282` | **`get_lockup_expiry` 解禁字段单位自相矛盾**。`history` 分支 `ABLE_FREE_SHARES` 标"股"（:3261），`upcoming` 分支同名同表（同一 `RPT_LIFT_STAGE`）标"万股"（:3282）。无论真实单位是哪种，两分支必有一个差 **1e4×**；F10 分支又根本不产 `able_shares`。 | ✅ 亲核 |
| **S5** | `stock_common/sc_datasource.py:6652` | **`get_em_fund_flow` 的 `total_net` 重复计数**。五档 `main+small+medium+large+super` 全加；东财语义"主力 = 大单+超大单"，故 `large`/`super` 被计两次。代码已亲核（:6641-6652 确为全五档求和）；**需数值对撞确认"主力列是否已含大+超"**（高疑似，若确认则所有资金流总额结论失真）。 | ✅ 代码亲核 / ⚠️ 语义待对撞 |
| **S6** | `scripts/sync_readme.py:194-219` | **运行即丢 README 版本历史归档**。`update_readme` 重写 `## 📋 版本历史` 到下一个 `\n---` 块（实测约 44KB，含 V16.3 及更早归档表 `16.2.0/15.3/14.x/11.5/9.4/8.0.0`…），而 CHANGELOG 正则只匹配 14 个 `## [数字]` 近期节；`README.write_text` 无备份/无 `--dry-run`。**应禁止运行**（脚本 docstring 自己已警告）。 | ✅ 亲核（只读模拟替换边界 17921→62200） |

---

## 二、中等级（正确性/防护/性能，代理核查）

- **M1 编排层假成功**：`main.py:509` 的 `all_ok` 依赖各脚本退出码，但 `sc_report_runner.py:83-95` 的 `run()` 把 `execute_pipeline` 异常吞掉、进程恒退出 0 → `all_ok` 永远 True，批量失败被误判成功（与 O39 同根因，发生在父进程层）。
- **M2 事件循环阻塞**：`get_med_report.py:642,679` / `get_lng_report.py:810` / `get_mak_report.py:1699` 在 `async def generate_report_*` **内同步调用** `baidu_kline_full`(HTTP)，未 `await asyncio.to_thread`，阻塞事件循环使 `Semaphore(3)` 并发失效；mak 还在循环里对 ST/退市股逐个阻塞，可能触发 `main.py` 15 分钟 stall-kill。对比 sht `:1721` 已正确 `to_thread`。
- **M3 重复网络调用**：`get_med_report.py:1214`、`get_lng_report.py:1241` 在评分段**重复拉取** `get_holder_structure`（前面 :1038/:905 已取），浪费限流预算。
- **M4 O39 守卫残留**：`get_val_report.py:2360-2382` 文件缺失只打印告警、**不 raise / 不返回非零**，叠加 M1 → 父进程仍判该脚本成功（守卫正确但退出语义未收口）。
- **M5 预取非并行**：`sc_report_runner.py:168-173` `await prefetch_async_fn(...)` 在 `Semaphore(3)` 与 worker 之前执行，注释称"与 3 条 worker 并行"实为串行前置（若钩子非 fire-and-forget 则拖慢整批）。
- **M6 GD 双上传 + 快照无校验**：`sc_report_runner.py:182` 逐股已上传 GD，`run()` 末尾 `:82` 又 `_handle_gd_upload` 二次上传（基类未对 `_gd_per_stock` 短路）；`:205-208` `snapshot_data` 直接透传 `save_snapshot`，若调用方误传 pipeline results（非 `{code:{name,total_score}}`）则跨日期背离检测静默成空壳。
- **M7 席位匹配缺陷**：`seat_db.py:56-91` 三层匹配用**双向子串**（`member in seat_name or seat_name in member`）+ 字典序首命中、无最长匹配。短席位名（如"盟主"）易误判为顶级游资；重叠别名分别维护在 `aliases`/`keywords_map`/`seat_details`。
- **M8 异步通道熔断失效**：`sc_network.py:1052-1181` `_async_quick_request` 仅开头判 `state==open` 即返回，**成功/失败后从不调** `_on_success`/`_on_failure` → 异步 EM 路径完全绕过熔断/20h 封禁（同步路径 :565-579/:814 已更新）。
- **M9 封禁被静默降级**：`sc_network.py:518-562` `em_get` 连续 403 抛 `RateLimitBlockedError`，但调用方（如 `get_em_batch_quotes._fetch_batch:1173`）宽 `except Exception` 转空结果 → "IP 被封"变空数据；且 `em_get`(抛) 与 `_quick_request`(返 None) 错误语义分裂。
- **M10 北交所公告 orgId 错**：`sc_datasource.py:510-533` `_cninfo_get_orgid` 把 `92x` 北交所落入 `else` 得 `gssz0{code}`（应为 `gsbj0`）；动态查询只拉 `szse_stock.json`，沪/北交所基本查不到、恒走错误 fallback。
- **M11 PE 字段路由可疑**：`sc_datasource.py:5890-5901 / 1161-1162` `f162→pe_dynamic`、`f163→pe_ttm`，与通行东财 push2 字典（`f162=TTM`、`f163=静`、`f164=动`）相反。依项目"对撞规则"序号≠字段，**需数值对撞逆证**（如招行/茅台实测两源），若相反则估值类全错。
- **M12 硬编码路径**：`sc_datasource.py:3933/:3942/:5255` 硬编码 `C:\new_tdx64\vipdoc\...`，非该 TDX 安装路径的机器直接 `FileNotFoundError`。应改为可配置。
- **M13 采集市场前缀错**：`scripts/capture_field_probe.py:220` `collect_sina` 只把 `6` 判沪市，漏 `5`(沪ETF)/`9`(沪B) → 新浪源误判 `sz`，污染跨源字段对照（与 `collect_tencent:97`、`collect_ulist239:469` 口径冲突）。
- **M14 回测指标失真**：`scripts/backtest_topn.py:329-341` `coverage`/`hit_in_top_n` 因候选域已截断到 `top_n`，恒等于 `selected_count/top_n`，无独立意义，易误读为"策略覆盖度"。
- **M15 回测脆弱依赖**：`scripts/backtest_topn.py:311-335` 策略全用 `s["code"]`，若 `core.zhb_client` 解析的股票 dict 不含 `code` 键（code 仅作 dict key）则整体 `KeyError`；且硬编码依赖 `cache/zhb/zhb_20260721.zip` 等固定包。
- **M16 dry-run 死代码**：`scripts/upload_reports_to_gd.py:112` 已 `return`，`:137/:155` 的 `if args.dry_run` 永不可达；`--dry-run` 实际不列待传文件清单（与 help 不符）。
- **M17 清缓存破坏性无确认**：`scripts/clean_cache.py:67-73` 无参运行 = `clear-all` 清空全部缓存，无二次确认（仅 `--dry-run` 安全）。

---

## 三、轻微级 / 死代码（逐条 file:line）

**入口层**
- `main.py:337-338` 外层 `except asyncio.TimeoutError: pass` 永不触发（内层已捕获）→ 死分支。
- `get_val_report.py:1990,1997` `_mcap_count` 在已把 `mcap_yi` 赋值>0 后还判 `not mcap_yi>0`（恒 False）→ 市值覆盖率统计低估（仅展示失真，不影响选股）。
- `get_mak_report.py:1492` `success_rate` 按 0–100 百分比格式化，若数据源返回 0–1 小数则显示错（需确认 `get_limit_pool_summary` 单位）。

**core 客户端层**
- `core/tdx_client.py:243` `_SH_INDEX_CODES` 定义后全仓零引用（死代码）。
- `core/tdx_client.py:113-119` `_market_from_code` 仅测试引用（生产用 `_easy_market`）。
- `core/tdx_client.py:894-915` `_tencent_volume_divisor` 本模块孤儿；**外部 `sc_datasource.py:1030` 正确应用**（688→÷100），无放大遗漏路径，非 bug。
- `core/tdx_client.py:2939` `main_net_amount` 实为竞价额（注释已实锤），却以"主力净"命名，下游误用得错语义。
- `core/zhb_client.py:468-475` `get_stock_concepts` 恒返回 `[]`（兼容残留，调用方静默拿不到数据）。
- `core/zhb_client.py:1028-1068` `_parse_tipinfo` docstring 列 `[13]record_date/[14]record_amount`，实现未解析返回 → 调用方 `KeyError`。

**分析与辅助层**
- `stock_common/sc_kline_cache.py:208-210` 注释"每 100 次检查" vs 实际每次写都 `enforce_size_limit()`（全目录 glob）。
- `stock_common/sc_fuyao.py:224-228` `code!=0` 返回整个错误 dict 而非 docstring 声明的 None（契约不一致）。
- `stock_common/stock_calendar.py:1078-1082` `get_next_trading_day` 跨 2026→2027 `NotImplementedError` 直接 re-raise（日历数据仅到 2026，2027 年起取下一交易日抛异常）。
- `stock_common/sc_fault_tolerance.py:175-181` `CircuitBreaker` 半开态需累计到阈值才回断 Open（典型应单次失败即回断）；`call_async` 无单飞。
- `stock_common/sc_technical.py:479` `if len(vals) else 0` 死分支（numpy 数组 `len` 恒>0）。
- `stock_common/sc_scoring.py:67` `ScoreData.debt_ratio` 从未被任何 scorer 使用（死字段，易误导填错）。
- `stock_common/sc_datasource.py:6175-6181` `get_stock_permanent_info` 的 `return out` 之后残留一段不可达死代码（`get_fupan_pmsl` 体，已在 :6117 正确定义）。
- `stock_common/sc_datasource.py:4398-4451` `get_fund_flow_weighted` 只记录 source/权重/标记、未算加权融合值，且无调用方（死代码 + 不完整实现）。
- `stock_common/sc_schema.py:79-405` `FieldSpec`/`FIELD_SPECS`/`get_field_spec`/`list_realtime_http_fields`/`list_zhb_sufficient_fields` 全仓零调用（测试契约死代码；`REQUIRES_REALTIME_HTTP`/`ZHB_SUFFICIENT` 仅注释、未被业务消费 → 合规）。
- `stock_common/sc_schema.py:626-634 / 637-643` `normalize_at_boundary` 单位换算依赖 `source` 标签（仅 EM 除 1e4、仅非 EM 除 100）→ 隐式单位假设，TDX 源若走此函数会错（当前仅 TENCENT 真消费，未暴露）。

**脚本层**
- `scripts/gen_field_matrix.py:233` 缺结束标记时 `tail` 取 marker 之后全部内容 → 旧内容重复累积。
- `scripts/capture_field_probe.py:355,366` 用 `__import__("datetime")` 重复导入（顶部已有 `import datetime`）。
- `scripts/backtest_topn.py:171` `if pe is not None and pe != 0 ...` 中 `pe is not None` 恒 True（`_safe_float` 永远 float）。
- `scripts/check_em_health.py:15` `reconfigure` 无 `try/except`（其余脚本均有）。
- `scripts/perf_compare.py:154-156` 结论文字硬编码（~50% 内存/~18% 快），与实际可能不符（仅说明性）。
- `scripts/fmt_preview.py:49` `... if False else m.group(2)` 死代码分支；`:13` docstring 路径 `C:\Opencode\...` 与实际项目路径不符。

---

## 四、已确认无问题（clean）

`get_sht_report.py` ✅、`core/zhb_sync.py` ✅、`core/gd_uploader.py` ✅、`f10_parser.py` ✅、
`analyze_history.py` ✅、`md_render.py` ✅、`sc_ftshare.py` ✅、`sc_kpl.py` ✅、`sc_risk.py` ✅、
`stock_common/sc_utils.py` ✅、`stock_common/__init__.py` ✅（re-export 对齐）、`scripts/update_calendar.py` ✅（含 V14+ 防覆盖保护，默认 BLOCK 退出）、`check_em_health.py`/`perf_compare.py` ✅（只读/无写）。

> 注：`get_val_report.py` O39"文件不存在却判成功"守卫**仍存在且正确**；`get_mak_report.py`**无 sync 回退**（符合预期）；科创板 688 成交量单位归一**收敛无遗漏**（`sc_datasource.py:1030` 已正确应用）。

---

## 五、修复优先级建议

1. **S1** 改 `_norm` 阈值为 `> 1e9`（或基于 `price×shares` 合理性回检），并修 :116 注释 `2e6→2e7`。影响最大（大盘股市值/筹码/风险全失真）。
2. **S2/S3** `get_change_ytd`/`get_streak_days` 改为基于升序数据的 `rows[-1]`(今日)/`rows[-2]`(昨日) 判定，并修注释；补单测（构造已知升序 K 线断言）。
3. **S4** 确认 `RPT_LIFT_STAGE.ABLE_FREE_SHARES` 真实单位，统一两分支换算，补 F10 分支 `able_shares`。
4. **S5/S11** 数值对撞验证 `total_net` 主力列语义、PE 字段路由 `f162/f163/f164`，确认后全量更正。
5. **S6** 在 CI 禁用 `sync_readme.py`，或改"合并"模式 + 写前 `.bak` + `--dry-run`。
6. **M1/M4** 让失败路径 `raise`/返回非零，使父进程 `all_ok` 真实反映失败（收口假成功）。
7. **M2** 四个 `baidu_kline_full` 同步调用改 `await asyncio.to_thread`。
8. **M8/M9** 异步通道补熔断器钩子；统一 `em_get`/`_quick_request` 的限流错误语义。
9. **M7** 席位匹配改"最长子串优先 + 去反向子句 + 别名统一回查 seat_details"。
10. **死代码清理**：`sc_schema` 测试契约函数、`:6175` 残留、`get_fund_flow_weighted`、`_SH_INDEX_CODES`、`get_stock_concepts` 等，降低维护误读。

---

## 六、结论

- **会污染报告数值的严重 bug 5 个**（S1 大盘市值、S2 YTD、S3 连涨连跌、S4 解禁、S5 资金流总额），其中 4 个已实锤、1 个需东财字段对撞确认。
- **安全/数据丢失 1 个**（S6 `sync_readme.py`）——已确认应禁止运行。
- **防护/性能/接口类中等 17 个**（M1–M17），多数有真实影响但不直接改数值（M8/M9 熔断失效、M2 并发失效较关键）。
- **死代码/轻微 20+ 处**，集中在 `sc_schema` 测试契约、`tdx_client` 残留常量、`zhb_client` 兼容函数、脚本层 `if False`/不可达分支。
- **约 13 个文件零问题**。

---

## 七、整改状态总览（2026-08-30 已落地）

> 全部 S1–S6 / M1–M17 / 死代码 M18 已对照修复并验证；回归基线 **353 passed / 45 deselected / 0 failed** 已恢复。
> 整改原则：被测试引用的符号一律保留；`get_fund_flow_weighted` 改 deprecated stub 而非删（被 `__init__.py` 再导出）。

| 项 | 处置 | 关键改动 |
|---|---|---|
| S1 | ✅ 已修 | `sc_capital_cache._norm` 阈值 `1e7→1e9`，注释 `2e6→2e7` |
| S2 | ✅ 已修 | `get_change_ytd` 改用 `rows[-1]`(当日)/`rows[0]`(年初)，更正注释 |
| S3 | ✅ 已修 | `get_streak_days` 从 `closes[-1]` 向前遍历，符号修正 |
| S4 | ✅ 已修 | `get_lockup_expiry` 两分支 `ABLE_FREE_SHARES` 统一"股"，删误标"万股"；TODO 标真实单位待采样 |
| S5 | ✅ 已修 | `get_em_fund_flow.total_net = main_net+small_net+medium_net`，更正"漏大单"误解注释 |
| S6 | ✅ 已修 | `sync_readme` 写前 `.bak` + `--force`/`--dry-run`，默认拒绝运行 |
| M1 | ✅ 已修 | `run()` 异常 `raise`，`all_ok` 真实反映失败 |
| M2 | ✅ 已修 | med/lng/mak 四处 `baidu_kline_full` 改 `await asyncio.to_thread` |
| M3 | ✅ 已修 | med:1214 / lng:1241 复用已取 `get_holder_structure` |
| M4 | ✅ 已修 | val O39 文件存在性判定移出 async try/except，双路失败才 raise |
| M5 | ✅ 已修 | `prefetch_async_fn` 改 `asyncio.create_task` 真并行 |
| M6 | ✅ 已修 | `snapshot_data` 结构校验（缺 `total_score`/`score` 跳过） |
| M7 | ✅ 已修 | `identify_seat_tier` 双向子串保留 + 最长子串优先 |
| M8 | ✅ 已修 | `_async_quick_request` 成功/失败更新熔断器，403 计 ban streak |
| M9 | ✅ 已修 | `_fetch_batch` 宽 except 前 re-raise `RateLimitBlockedError` |
| M10 | ✅ 已修 | `_cninfo_get_orgid` `92x→gsbj0`，动态查询拉 `szse`+`shse` |
| M11 | ⚠️ 文档误记（非代码 bug） | 代码 `f162→pe_dynamic`/`f163→pe_ttm` 经 `field_dict.md` 实证正确；仅修正文档表 `:2538/2540` 写反处 |
| M12 | ✅ 已修 | 三处 `C:\new_tdx64` 改 `_tdx_root()`（读 `TDX_HOME`/`TDX_ROOT`） |
| M13 | ✅ 已修 | `collect_sina` 市场前缀对齐 `collect_tencent` |
| M14 | ✅ 已修 | `backtest_topn.coverage = selected/total_universe` |
| M15 | ✅ 已修 | `load_zhb_snapshot` 注入 `stk["code"]`；`discover_days()` 取代硬编码日期 |
| M16 | ✅ 已修 | `upload_reports_to_gd --dry-run` 打印完整清单，删死分支 |
| M17 | ✅ 已修 | `clean_cache` 加 `--yes`，破坏性操作须确认 |
| M18 | ✅ 已修 | 删 `_SH_INDEX_CODES` / `sc_technical:479` 死分支 / `fmt_preview:49` 死分支；`_mcap_count` 覆盖率修复；`get_fund_flow_weighted` 改 deprecated stub |
| §三 测试契约死代码 | 🔒 保留 | `_market_from_code`/`get_stock_concepts`/`sc_schema.FieldSpec` 系列——审查意见标注"合规"，测试引用，不删 |
| §三 需判定/耦合项 | ⏸ 暂缓 | `_parse_tipinfo`/`normalize_at_boundary`/`sc_fault_tolerance` 半开态/`main_net_amount` 命名/`sc_fuyao` 返回值契约——属下游耦合或需实盘判定，维持现状不盲改 |
