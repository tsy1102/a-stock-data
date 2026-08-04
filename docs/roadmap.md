---

# A-Stock Data Project Roadmap

## 版本规划

| 版本 | 主题 | 状态 |
|:---:|:---|:---:|
| V11.0 | Data Provider 统一数据层正式启用 | ✅ 已完成 |
| V11.5 | 六大报告脚本全部迁移到 Data Provider | ✅ 已完成 |
| V12.0 | TCP 统一层重构：pytdx/easy_tdx → mootdx + 完全移除 easy_tdx | ✅ 已完成 |
| V12.1 | 代码质量修复：L1/L2 缓存同步 + 静默异常日志化 + 容错层下沉 + 死代码清理 | ✅ 已完成 |
| V12.2 | 工程化优化：数据库优雅关闭 + 全局异步 Session + config.py 集中配置 + 单元测试补齐 | ✅ 已完成 |
| V12.3 | 深入架构演进：DAL 强收口 + 异步 Session 优雅关闭 + Semaphore 并发限流 | ⏸️ 已挂起 (低ROI/过度设计) |
| V12.4 | 策略报告通用框架 (ReportRunner)：抽取 CLI/I/O/云端同步/日志样板代码 | ✅ 已完成 |
| V12.5 | ReportRunner 修复 + GD 上传模板真正落地 + L1 缓存回归修复 | ✅ 已完成 |
| V12.6 | 字段路由简化：HTTP 批量上限实测 + data_provider 字段决策树优化 | ✅ 已完成 |
| V13.0 | Schema 骨架：`stock_common/sc_schema.py` 定义 + 字段元数据 | ✅ 已完成 |
| V13.1 | 缓存层透明序列化 dataclass + opt-in dataclass 接口 | ✅ 已完成 |
| V13.2 | 性能压测 + 文档全面更新 | ✅ 已完成（dict 仍为默认）|
| V14.0 | Bug修复 + 文档全量同步：is_workday() 误判 + config 清理 + scratch 整理 + README/CHANGELOG 同步 | ✅ 已完成 |
| V14.1 | CHANGELOG + README 顶部版本历史同步脚本 sync_readme.py | ✅ 已完成 |
| V14.2 | ZHB 数据集深度集成：profile.dat + tdxchain.cfg + neednote.dat + xgsg.cfg + brkcomp.dat + pttab.dat | ✅ 已完成 |
| V15.0 | 标准化数据中心：CanonicalStockData 强类型数据合约 + ZHB 离线优先路由 + 熔断静默降级 | ✅ 已完成 |
| V15.1 | 全局 ZHB 旁路普及 + 0x0010 协议 key 修正 + tdxchain.cfg 重写 + 策略线程池隔离 | ✅ 已完成 |
| **V15.2** | **P0 board UnboundLocalError 修复 + 缓存 valid_if 强化 + 恢复 ZHB 交叉验证 + GD 上传缓冲修复 + val 1000s 性能优化** | ✅ **已完成** |
| **V15.3** | **全量健康修复（9 个 P0/P1） + CanonicalStockData 落地剩余 4 大报告 + CircuitBreaker TOCTOU + L1 LRU + scratch 文档** | ✅ **已完成** |
| **V15.4** | **cdata 分层多源 + per-field source label + PUSH2 字段映射 + industry 4 级 fallback + field_dict/script_data_dict 补扎实** | ✅ **已完成** |
| **V15.4.1** | **修复 med/lng/ful 报告异步化补全 + sht/med/lng/ful 同步调用包 to_thread (12 处)** | ✅ **已完成** |
| **V15.4.2** | **main.py KeyboardInterrupt kill 子进程 + 600s 超时保护 + 4 报告文件名统一为时分** | ✅ **已完成** |
| **V15.4.3** | **easy_tdx 字段探测 + docs/tdx_field_dict.md（v1.20.4 健康分引擎+V15.5 移植规划）** | ✅ **已完成（字典与测试）+ ✅ V15.5 移植 health/reconnect** |
| **V16.0** | **正确性修复 + 限流加固 + 统一数据层落地 + 缓存重构 + 性能优化 + 项目清理** | ✅ **已完成（2026-08-04）** |
| **V16.1** | **报告体系重构：sht/med/lng 三视图 + ful 下线 + mak/val 引擎化 + 新字段接入** | 🔵 **进行中（2026-08-04 启动）** |

---

## V16.0 全面整改（已完成）

> **启动日期**：2026-08-03
> **背景**：全盘代码审计（对照 `a-stock-data-v9.6` 标杆 + [a-stock-data 参考仓库](https://github.com/simonlin1212/a-stock-data)限流方案）发现 P0 正确性问题、缓存"未带来飞跃"根因、限流接线不完整、val/mak 性能瓶颈、大量实验文件堆积。
> **硬性约束**：
> - 股票级并发**保持 3**（不提高，防封）
> - `a-stock-data-v9.6/` 为**只读参考标杆**，永不修改，且当前版**不能比它差**（数据更优或速度更快）
> - 参考仓库**仅借鉴限流方案**（em_get 统一入口 + EM_MIN_INTERVAL 可调 + 无突发）
> - 每阶段独立 commit + 验证循环（AGENTS.md §9）

### 执行顺序：阶段1(正确性) → 阶段4(限流) → 阶段2(统一层) → 阶段3(缓存) → 阶段5(性能) → 阶段6(清理)

---

## 阶段 1：正确性修复（P0，数据不能错）

| # | 任务分类 | 详细内容 | 关联文件 | 优先级 | 状态 |
|:---:|:---|:---|:---|:---:|:---:|
| 1.1 | **成交额 10000 倍单位 bug ×3** | ZHB tdxstat2 `amount` 已是万元，却再次 `/10000` → 去掉二次除法 | [tdx_client.py:749](file:///d:/GitHub/test/tdx_client.py), [data_provider.py:1336/1550/1569](file:///d:/GitHub/test/data_provider.py) | P0 | ✅ |
| 1.2 | **push2 兜底死代码** | `PUSH2_FIELD_MAP` 用 f43/f44 去 `.get()`，但 `get_em_quote_full` 已返回规范名 → 直接遍历映射 | [data_provider.py:314-322](file:///d:/GitHub/test/data_provider.py) | P0 | ✅ |
| 1.3 | **`cdata.net_profit_yi` AttributeError** | `CanonicalStockData` 无此字段 → 改为 `cdata.net_profit` | [get_med_report.py:324/326](file:///d:/GitHub/test/get_med_report.py) | P0 | ✅ |
| 1.4 | **ZHB 事件锁失效** | `sc_datasource.py:1880` 读不存在的 `report_date` → 从 tipinfo `report_period` 合并 | [sc_datasource.py:1880](file:///d:/GitHub/test/stock_common/sc_datasource.py), [zhb_client.py](file:///d:/GitHub/test/zhb_client.py) | P0 | ✅ |
| 1.5 | **f127/f128 语义冲突** | `data_provider.py:272` 误标 f128=industry（实为地域 board）→ 统一为 f127=industry | [data_provider.py:259-273](file:///d:/GitHub/test/data_provider.py), [sc_datasource.py:3752-3753](file:///d:/GitHub/test/stock_common/sc_datasource.py) | P1 | ✅ |
| 1.6 | **mak 板块涨幅口径错位** | ZHB 旁路板块涨幅是 T-1，个股是今日 → 腾讯实时覆盖 | [get_mak_report.py:513](file:///d:/GitHub/test/get_mak_report.py) | P1 | ✅ |
| 1.7 | **mak main_inflow 单位混用** | ZHB 路径万元被 `/1e8` → 应 `/1e4` | [get_mak_report.py:516/554/1023/1065/1071](file:///d:/GitHub/test/get_mak_report.py) | P1 | ✅ |
| 1.8 | **mak ret_3d 拼凑/fudge** | 混窗口 + 全 0 时 `change_5d*0.6` 捏造 → 纯 ZHB 3 日真实窗口 | [get_mak_report.py:241-254](file:///d:/GitHub/test/get_mak_report.py) | P1 | ✅ |
| 1.9 | **mak 行业错配映射** | "医药制造→化学制药"等以偏概全 → 删除错误映射 | [get_mak_report.py:416-439](file:///d:/GitHub/test/get_mak_report.py) | P1 | ✅ |
| 1.10 | **mak 板块代码体系不兼容** | ZHB 旁路申万代码 vs TDX BK 代码 → 统一 BK 前缀 | [get_mak_report.py:547](file:///d:/GitHub/test/get_mak_report.py), [sc_datasource.py:4129-4135](file:///d:/GitHub/test/stock_common/sc_datasource.py) | P1 | ✅ |
| 1.11 | **mak 10/30 日偏离口径混乱** | 简单减法/60日差减半冒充 → 统一复利口径 | [get_mak_report.py:387/405](file:///d:/GitHub/test/get_mak_report.py) | P2 | ✅ |
| 1.12 | **mak ST 涨停阈值漏判** | 9.5%/19.5% 无法识别 ST 5% → 按 ST 判定 | [get_mak_report.py:751-753](file:///d:/GitHub/test/get_mak_report.py) | P2 | ✅ |
**验收**：py_compile + mypy + black --check + skip_real 测试 + 600519 成交额 ZHB/TDX 一致

---

## 阶段 4：限流加固（防封，借鉴 a-stock-data）

| # | 任务分类 | 详细内容 | 关联文件 | 优先级 | 状态 |
|:---:|:---|:---|:---|:---:|:---:|
| 4.1 | **push2ex 补限流** | `_DOMAIN_LIMITS` 加 `push2ex.eastmoney.com: {sleep_ms:1500, rps:0.6}`（当前 100ms=10rps 高危） | [sc_network.py:167-184](file:///d:/GitHub/test/stock_common/sc_network.py) | P0 | ✅ |
| 4.2 | **池函数补 @requires_push2** | 涨停/炸板/跌停池函数 + 请求间间隔 | [sc_datasource.py:2502/2537/2572/2659](file:///d:/GitHub/test/stock_common/sc_datasource.py) | P0 | ✅ |
| 4.3 | **em_get rps 从 _DOMAIN_LIMITS 读** | 硬编码 1.0 → push2 应为 0.6 | [sc_network.py:281](file:///d:/GitHub/test/stock_common/sc_network.py) | P1 | ✅ |
| 4.4 | **修复 EM_MIN_INTERVAL 可调性** | 令牌桶异常才生效 → 作为硬性全局下限（与桶取严） | [sc_network.py:286-288](file:///d:/GitHub/test/stock_common/sc_network.py) | P1 | ✅ |
| 4.5 | **消除令牌桶突发** | `max_burst` 3→1（参考仓库无突发模式） | [sc_fault_tolerance.py:232](file:///d:/GitHub/test/stock_common/sc_fault_tolerance.py) | P1 | ✅ |
| 4.6 | **接通同步进程间文件锁** | `_em_wait_process_interval()` 定义无调用 → em_get 等接入 | [sc_network.py:329-351](file:///d:/GitHub/test/stock_common/sc_network.py) | P1 | ✅ |
| 4.7 | **em_get 补 403 处理** | 403 计数/长退避/熔断（对齐 _do_request） | [sc_network.py:303-313](file:///d:/GitHub/test/stock_common/sc_network.py) | P1 | ✅ |
| 4.8 | **熔断阈值对齐 + 429 修复** | 5 vs 10 统一 + `float(retry_after)` try/except | [sc_fault_tolerance.py:241](file:///d:/GitHub/test/stock_common/sc_fault_tolerance.py), [sc_network.py:540](file:///d:/GitHub/test/stock_common/sc_network.py) | P2 | ✅ |
| 4.9 | **腾讯批量批间间隔** | `_tencent_batch_fallback` 批间加 100-200ms | [tdx_client.py:556-582](file:///d:/GitHub/test/tdx_client.py) | P2 | ✅ |
**验收**：verify_tdx_host + 观察 `logs/rate_limit.log` push2 间隔 ≥1.5s

---

## 阶段 2：统一数据层落地（核心架构）

| # | 任务分类 | 详细内容 | 关联文件 | 优先级 | 状态 |
|:---:|:---|:---|:---|:---:|:---:|
| 2.1 | **实现 normalize_at_boundary()** | `sc_schema.py:524-541` 是 NotImplementedError → 各源 dict 进入统一层前归一化字段名+单位 | [sc_schema.py](file:///d:/GitHub/test/stock_common/sc_schema.py) | P0 | ✅ |
| 2.2 | **收敛 6 脚本旁路直连** | 逐脚本 grep 确认 `tdx_get_security_bars`/`get_sina_financial_report`/`baidu_kline_full` 直连点 → 走 data_provider 原子函数 | 6 大报告脚本 | P1 | ✅ |
| 2.3 | **修正 get_tencent_quote 名不副实** | `sc_datasource.py:746-749` 直接 return tdx_get_quote_full → 改真腾讯或改名 | [sc_datasource.py](file:///d:/GitHub/test/stock_common/sc_datasource.py) | P1 | ✅ |
| 2.4 | **补齐 list_date/ipo_date** | 从 push2 f189 / 0x0010 ipo_date / tipinfo 归一化到 cdata | [sc_schema.py](file:///d:/GitHub/test/stock_common/sc_schema.py), [data_provider.py](file:///d:/GitHub/test/data_provider.py) | P2 | ✅ |
**验收**：test_field_routing + test_sc_schema 全过；600519 各源值一致

---

## 阶段 3：缓存重构（针对"未带来飞跃"）

| # | 任务分类 | 详细内容 | 关联文件 | 优先级 | 状态 |
|:---:|:---|:---|:---|:---:|:---:|
| 3.1 | **zhb_data 摘除 @cached** | 17 个 RAM 读函数走完整 SQLite 写路径 → 进程内 lru_cache | [data_provider.py:861-1426](file:///d:/GitHub/test/data_provider.py) | P0 | ✅ |
| 3.2 | **L2 命中去 UPDATE+commit** | `stock_cache.py:537-541` 每次命中写库 → 批量落盘 | [stock_cache.py](file:///d:/GitHub/test/stock_cache.py) | P1 | ✅ |
| 3.3 | **写入端去全表清理** | `_enforce_size_limit` 每写执行 → 每 N 次或超阈值 | [stock_cache.py:810→436](file:///d:/GitHub/test/stock_cache.py) | P1 | ✅ |
| 3.4 | **cross_verify 软验证** | 首写 verified=0 直接 miss → 首写 verified=1 或软验证 | [stock_cache.py:785-790](file:///d:/GitHub/test/stock_cache.py) | P1 | ✅ |
| 3.5 | **统一参数分 key** | dragon_tiger days 7/30 分 key → 归一化 | [get_val_report.py:1242](file:///d:/GitHub/test/get_val_report.py), [get_mak_report.py:917](file:///d:/GitHub/test/get_mak_report.py) | P2 | ✅ |
| 3.6 | **缓存腾讯批量** | `_tencent_batch_fallback` 不落缓存 → trading_day TTL | [tdx_client.py:548-582](file:///d:/GitHub/test/tdx_client.py) | P1 | ✅ |
| 3.7 | **holder 查询批量化** | holder_change/get_holder_structure datacenter 逐股 → 批量 | [sc_datasource.py:249/651](file:///d:/GitHub/test/stock_common/sc_datasource.py) | P2 | ✅ |
**验收**：连续跑两次 val 第二次明显加快；test_cache 全过；perf_compare.py 对比

---

## 阶段 5：性能优化（对标"只能更快"）

| # | 任务分类 | 详细内容 | 关联文件 | 优先级 | 状态 |
|:---:|:---|:---|:---|:---:|:---:|
| 5.1 | **val 策略内股票级并发** | 参照 sht `Semaphore(3)+gather`，S20 最坏 15-25min → 5-8min | [get_val_report.py:1723-1724](file:///d:/GitHub/test/get_val_report.py) | P1 | ✅ |
| 5.2 | **mak 去双重腾讯批量** | 删 `get_mak_report.py:108` 冗余拉取，复用 L147 | [get_mak_report.py:105-119/147](file:///d:/GitHub/test/get_mak_report.py) | P1 | ✅ |
| 5.3 | **mak 板块成员缓存** | `get_sector_stocks` 跨 C/E 段复用 | [get_mak_report.py:475/658/928](file:///d:/GitHub/test/get_mak_report.py) | P2 | ✅ |
| 5.4 | **tdx_get_dividend_history 补 @cached** | S13 100 次逐股 xdxr 无缓存 | [tdx_client.py:1045](file:///d:/GitHub/test/tdx_client.py) | P2 | ✅ |
**验收**：val 冷跑 <8min（当前最坏 35min），mak <2min

---

## 阶段 6：项目清理合并

| # | 任务分类 | 详细内容 | 关联文件 | 优先级 | 状态 |
|:---:|:---|:---|:---|:---:|:---:|
| 6.1 | **删除 scratch/ 12 个第三方项目** | eastmoney/tdx/investool/TradingAgents/UZI-Skill 等 2696 文件（保留本项目相关脚本） | [scratch/](file:///d:/GitHub/test/scratch) | P1 | ✅ |
| 6.2 | **skill 归档** | `skills/a-stock-data/SKILL.md`（158KB 参考副本）→ docs/references/ | [skills/](file:///d:/GitHub/test/skills) | P2 | ✅ |
| 6.3 | **文档合并** | field_dict/script_data_dict/tdx_field_dict/zhb_field_dict → 统一字段参考 | [docs/](file:///d:/GitHub/test/docs) | P2 | ⏳ |
| 6.4 | **死代码清理** | print_cache_stats 双定义、MAX_CONCURRENT_* 死配置、PUSH2_FIELD_MAP 残留 | 多处 | P2 | ✅ |
| 6.5 | **超长函数拆分（暂缓：纯重构，先验证数据正确性）** | `run_discovery_async` 347行、`generate_sector_report` 446行 | [get_ful_report.py](file:///d:/GitHub/test/get_ful_report.py), [get_mak_report.py](file:///d:/GitHub/test/get_mak_report.py) | P2 | ⏳ |
| 6.6 | **补 scripts/run_tests.ps1** | AGENTS.md 引用但缺失，基于 run_with_system_python.ps1 | [scripts/](file:///d:/GitHub/test/scripts) | P0 | ✅ |
| 6.7 | **v9.6 移出仓库根目录** | 加入 .gitignore 或移出，防止误改/误提交 | 仓库根 | P1 | ✅ |
**验收**：AGENTS.md 引用的 run_tests.ps1 可用；git status 干净；文档无重复

---

## V16.1 报告体系重构（进行中）

> **启动日期**：2026-08-04
> **背景**：V16.0 完成后对 6 大脚本做投研职责审计（对照 [a-stock-data 参考仓库](https://github.com/simonlin1212/a-stock-data)十层架构 + 2026-08-04 接口实测破解的 push2 全字段 114 个/ulist 239 个）：
> - `sht/med/lng` 三报告是不同持有周期的单股视图，但 `calculate_score()` 未传 cfg → 权重为 0，总分恒为 0
> - `ful` 是前三者的重复汇总器（无独立数据能力），且 Layer2 引用作用域外 `cdata`、Layer6 引用未定义 `_zhb_data`（两处静默失败）→ **下线**
> - `mak` 是市场状态看板（保留，改引擎化）；`val` 是候选发现框架（保留，修字段契约）
> - push2 `stock/get` 实测可返回 114 字段（项目仅用 19），大量高价值字段（涨停/跌停价、52周高低、股息率、EPS/BPS、资金流 f135-f146、报告期 f221）被丢弃 → 接入统一层
> - **硬性约束**：
>   - 股票级并发保持 3（不提高，防封）
>   - 东财全字段探测仅限离线（生产用固定字段包，防风控）
>   - 每阶段独立 commit + 验证循环（AGENTS.md §9）
>   - `get_ful_report.py` 下线前必须先迁移技术引擎/风险引擎，禁止裸删

### 执行顺序：阶段1(字段合同) → 阶段2(共享上下文) → 阶段3(sht) → 阶段4(med) → 阶段5(lng) → 阶段6(ful下线) → 阶段7(mak/val) → 阶段8(验收)

---

## V16.1 阶段 1：数据合同扩展（push2 新字段接入）

| # | 任务分类 | 详细内容 | 关联文件 | 优先级 | 状态 |
|:---:|:---|:---|:---|:---:|:---:|
| 1.1 | **push2 stock/get 扩展字段包** | `get_em_quote_full` 请求字段从 19 个扩到已验证字段包（f51/f52 涨停跌停价、f55 EPS、f92 BPS、f126 股息率、f162-f167 PE/PB、f174/f175 52周高低、f137-f146 资金流、f198 行业码、f80 交易时段、f178 5日资金流数组） | [sc_datasource.py:4602-4647](file:///d:/GitHub/test/stock_common/sc_datasource.py) | P0 | ✅ |
| 1.2 | **CanonicalStockData 扩展字段** | 新增 limit_up/limit_down/high_52w/low_52w 实时来源、eps/bps 已有、fund_flow_by_period、report_period、quote_time 等字段（dataclass 向后兼容：默认值） | [sc_schema.py](file:///d:/GitHub/test/stock_common/sc_schema.py) | P0 | ✅ |
| 1.3 | **ulist 批量字段扩展** | `get_em_batch_quotes` 从 f12,f14,f2,f3,f20,f21 扩到含 f55/f92/f126/f162-f167/f174/f175/f221 | [sc_datasource.py:993-1059](file:///d:/GitHub/test/stock_common/sc_datasource.py) | P1 | ✅ |
| 1.4 | **修复现有映射问题** | f57 被请求未解析、`data_date` 用未定义 `now_str()` 返回空、f84/f85 单位注释错误、`eastmoney_stock_info_push2` 单位与 `get_em_quote_full` 不一致 | [sc_datasource.py](file:///d:/GitHub/test/stock_common/sc_datasource.py) | P1 | ✅ |
| 1.5 | **reportapi 预测字段接入** | 新增 `extract_report_valuation()` 提取 predictThisYearPe/predictNextYearPe/predictNextTwoYearPe/emRatingValue/lastEmRatingName/ratingChange（med/lng 用） | [sc_datasource.py](file:///d:/GitHub/test/stock_common/sc_datasource.py) | P1 | ✅ |
| 1.6 | **事件源字段保留** | CLS 保留 stock_list/subjects/level、巨潮保留 adjunctUrl/announcementId、龙虎榜保留 EXPLAIN/BUY_RATIO/D1-D30 偏离、两融保留 RZJME/RQJMG/10D/5D/3D | [sc_datasource.py](file:///d:/GitHub/test/stock_common/sc_datasource.py) | P1 | ✅ |
| 1.7 | **未验证字段隔离** | f103/f108/f109/f183-f199 放入 unverified 集，需多股/财报期交叉验证后才可进评分（字段包未请求即天然隔离）| [sc_datasource.py](file:///d:/GitHub/test/stock_common/sc_datasource.py) | P2 | ✅ |
**验收**：新字段 3 股（600519/000001/601398）与官方 TdxQuant 交叉一致；test_sc_schema 全过；生产字段包不含 f1-f250 全量

---

## V16.1 阶段 2：共享上下文（一次取数三报告复用）

| # | 任务分类 | 详细内容 | 关联文件 | 优先级 | 状态 |
|:---:|:---|:---|:---|:---:|:---:|
| 2.1 | **StockContext 建立** | 单股一次加载 canonical + quote_extended + technical + fundamental + fund_flow + ownership + events + quality，sht/med/lng 共用 | [stock_common/sc_context.py](file:///d:/GitHub/test/stock_common/) | P0 | ⏳ |
| 2.2 | **MarketContext 建立** | 全市场快照 + 批量行情 + 四池 + 行业资金流 + 情绪指标，mak/val 共用 | [stock_common/sc_context.py](file:///d:/GitHub/test/stock_common/) | P1 | ⏳ |
| 2.3 | **main.py 合并模式** | `--sht/--med/--lng 同一股票列表` 改为单进程内共享 StockContext 渲染三份，去掉子进程重复取数 | [main.py](file:///d:/GitHub/test/main.py) | P1 | ⏳ |
| 2.4 | **修复 calculate_score 权重** | sht/med/lng 调用时未传 cfg → 权重 .get() 默认 0 → 传 strategy_config.yaml scoring 或内置默认权重 | [get_sht_report.py:1512](file:///d:/GitHub/test/get_sht_report.py), [get_med_report.py:1068](file:///d:/GitHub/test/get_med_report.py), [get_lng_report.py:912](file:///d:/GitHub/test/get_lng_report.py), [sc_scoring.py](file:///d:/GitHub/test/stock_common/sc_scoring.py) | P0 | ✅ |
| 2.5 | **缓存键分层** | 行情/财报/研报/公告/新闻/资金流分键（code+trade_date / code+report_period / code+infoCode / announcementId） | [stock_cache.py](file:///d:/GitHub/test/stock_cache.py) | P1 | ⏳ |
**验收**：同股 sht+med+lng 三份报告，网络请求数 ≈ 单份的 1.3x；评分总分非 0 且随数据变化

---

## V16.1 阶段 3：SHT 重构（短线交易执行视图）

| # | 任务分类 | 详细内容 | 关联文件 | 优先级 | 状态 |
|:---:|:---|:---|:---|:---:|:---:|
| 3.1 | **接入涨跌停边界** | f51/f52 涨停/跌停价替代 prev_close×1.1 估算（ST/20cm 正确识别） | [get_sht_report.py:537-555](file:///d:/GitHub/test/get_sht_report.py) | P0 | ✅ |
| 3.2 | **资金流 5/10/20 日复用** | f137-f146 + f178 替代重复取 120d 再切片；修复"最新在前"切片方向 | [get_sht_report.py:122-136/759-787](file:///d:/GitHub/test/get_sht_report.py) | P0 | ✅ |
| 3.3 | **昨日涨停池晋级率** | push2ex getYesterdayZTPool 接入（§12.8.1 已记录字段），算晋级率/赚钱效应 | [sc_datasource.py](file:///d:/GitHub/test/stock_common/sc_datasource.py), [get_sht_report.py](file:///d:/GitHub/test/get_sht_report.py) | P1 | ✅ |
| 3.4 | **文本因子接入** | THS analyse/analyse_title、CLS stock_list/subjects/level、龙虎榜 EXPLAIN、公告 PDF 链接 | [get_sht_report.py:1106-1242](file:///d:/GitHub/test/get_sht_report.py) | P1 | ✅ |
| 3.5 | **修复深度开关** | lite 模式 skip_fund_flow_120d/skip_industry_peers/skip_lhb_detail 实际生效 | [get_sht_report.py:257-289](file:///d:/GitHub/test/get_sht_report.py) | P1 | ✅ |
| 3.6 | **同步阻塞调用 to_thread** | get_stock_sector_rank/get_dividend_history/cls_telegraph/ths_hot_list/cninfo_irm/get_limit_pool_summary/time.sleep 包 to_thread | [get_sht_report.py:621-666](file:///d:/GitHub/test/get_sht_report.py) | P2 | ✅ |
**验收**：涨停价与官方 TdxQuant 一致；SHT 不含长周期财务噪音；lite 模式请求数减半

---

## V16.1 阶段 4：MED 重构（中线业绩兑现视图）

| # | 任务分类 | 详细内容 | 关联文件 | 优先级 | 状态 |
|:---:|:---|:---|:---|:---:|:---:|
| 4.1 | **报告期绑定** | f221 报告期 + 新浪财报 report_date 事件锁对齐，EPS/BPS/营收/净利带报告期展示 | [get_med_report.py:349-633](file:///d:/GitHub/test/get_med_report.py) | P0 | ✅ |
| 4.2 | **两融 3/5/10 日维度** | RZJME/RQJMG/RZCHE10D/5D/3D/RZMRE10D/5D/3D 接入中线资金确认 | [get_med_report.py](file:///d:/GitHub/test/get_med_report.py) | P1 | ✅ |
| 4.3 | **研报评级变化** | lastEmRatingName/ratingChange → 评级升降风向；predictNextYearPe 前向 PE | [get_med_report.py](file:///d:/GitHub/test/get_med_report.py) | P1 | ✅ |
| 4.4 | **去除重复请求** | EPS 无数据时 get_reports_async(1) 后无条件 get_reports_async(3) 去重；baidu_kline_full 两次调用复用 | [get_med_report.py](file:///d:/GitHub/test/get_med_report.py) | P1 | ✅ |
| 4.5 | **async 直连补缓存** | get_sina_financial_report_async/get_sina_balance_sheet_async 直连不走同步缓存 → 复用同步路径或独立缓存 | [sc_datasource.py:2357-2497](file:///d:/GitHub/test/stock_common/sc_datasource.py) | P1 | ✅ |
| 4.6 | **技术面补强（迁移 technical_engine）** | MACD/RSI/BOLL/KDJ 从 ful Layer1 迁移，替换仅 MA20/MA60 | [get_med_report.py](file:///d:/GitHub/test/get_med_report.py), [stock_common/sc_technical.py](file:///d:/GitHub/test/stock_common/) | P2 | ✅ |
**验收**：med 报告财务数据带报告期锚点；无重复研报请求；评分总分非 0

---

## V16.1 阶段 5：LNG 重构（长线企业质量视图）

| # | 任务分类 | 详细内容 | 关联文件 | 优先级 | 状态 |
|:---:|:---|:---|:---|:---:|:---:|
| 5.1 | **删除短线噪音** | 移除龙虎榜席位/当日热榜/涨停池/盘中资金噪音章节 | [get_lng_report.py](file:///d:/GitHub/test/get_lng_report.py) | P0 | ✅ |
| 5.2 | **风险引擎迁移（risk_engine）** | 资产负债/商誉/应收/存货/现金短债/解禁/减持/质押/业绩下滑 9 项风险清单（从 ful layer_risk 迁移） | [stock_common/sc_risk.py](file:///d:/GitHub/test/stock_common/) | P1 | ✅ |
| 5.3 | **修复重复 Canonical 调用** | get_stock_composite_async + 两次 get_canonical_stock_data → 单次 StockContext | [get_lng_report.py:167-222](file:///d:/GitHub/test/get_lng_report.py) | P0 | ✅ |
| 5.4 | **TDX 财务读取去重** | jingyingxianjinliu/jinglirun 两次读取 → 一次 | [get_lng_report.py:498-512/576-587](file:///d:/GitHub/test/get_lng_report.py) | P1 | ✅ |
| 5.5 | **历史高点缓存** | tdx_get_historical_high 8000 根 K 线不走磁盘缓存 → 复用 sc_kline_cache | [tdx_client.py:966-983](file:///d:/GitHub/test/tdx_client.py) | P2 | ✅ |
| 5.6 | **分红连续性指标** | consecutive_dividend_years 真实计算（从分红历史推导，非硬编码） | [get_lng_report.py](file:///d:/GitHub/test/get_lng_report.py) | P2 | ✅ |
**验收**：lng 报告无短线章节；风险清单 9 项全可用；同股网络请求数 ≈ med 的 1.2x

---

## V16.1 阶段 6：FUL 下线（引擎迁移 + 归档）

| # | 任务分类 | 详细内容 | 关联文件 | 优先级 | 状态 |
|:---:|:---|:---|:---|:---:|:---:|
| 6.1 | **技术引擎迁移确认** | MACD/RSI/BOLL/KDJ/量能 → stock_common/sc_technical.py，sht/med 复用 | [get_ful_report.py:357-555](file:///d:/GitHub/test/get_ful_report.py) | P0 | ✅ |
| 6.2 | **风险引擎迁移确认** | layer_risk → stock_common/sc_risk.py，med/lng 复用 | [get_ful_report.py:1421-1595](file:///d:/GitHub/test/get_ful_report.py) | P0 | ✅ |
| 6.3 | **移除 main.py --ful 入口** | README/版本表/CHANGELOG 同步；get_ful_report.py 移入 docs/archive/ 或保留只读归档 | [main.py](file:///d:/GitHub/test/main.py), [README.md](file:///d:/GitHub/test/README.md) | P1 | ✅ |
| 6.4 | **删除 ful 评分快照逻辑** | report_source="ful" 快照停写；test_report_runner 中 ful 相关用例更新 | [get_ful_report.py](file:///d:/GitHub/test/get_ful_report.py), [tests/](file:///d:/GitHub/test/tests) | P1 | ✅ |
**验收**：`python main.py --ful` 报友好提示；sht/med/lng 全部技术+风险能力不缺失；测试全过

---

## V16.1 阶段 7：MAK/VAL 引擎化（市场状态 + 候选发现）

| # | 任务分类 | 详细内容 | 关联文件 | 优先级 | 状态 |
|:---:|:---|:---|:---|:---:|:---:|
| 7.1 | **mak 接入 MarketContext** | 复用全市场快照/四池/行业资金流，删双重腾讯批量（阶段5.2遗留回归检查） | [get_mak_report.py:105-215](file:///d:/GitHub/test/get_mak_report.py) | P1 | ✅ |
| 7.2 | **mak 修正口径** | 指数/个股统一交易日窗口；删除"异动后5日胜率"伪回测（改真实前瞻或改名）；ret_3d=change_pct_2d fallback 修正；count_history_deviations 负索引修正 | [get_mak_report.py:121-128/241-254/451-485](file:///d:/GitHub/test/get_mak_report.py) | P0 | ✅ |
| 7.3 | **val 三阶段扫描** | ZHB+批量(初筛) → push2扩展+K线(候选) → 财报/研报/股东(深度确认) | [get_val_report.py:1572-1780](file:///d:/GitHub/test/get_val_report.py) | P1 | ✅ |
| 7.4 | **val 修复 P0 策略缺陷** | 策略01 热点字段契约、策略03 箱体含当前价、策略07 vol_ratio 缺失、策略16 reason 缺失、策略20 缺导入、策略21/22 字段不匹配、策略13 单次分红 | [get_val_report.py:499-1531](file:///d:/GitHub/test/get_val_report.py) | P0 | ✅ |
| 7.5 | **val 修复 PE 百分位前视偏差** | 按披露日排序 + 累计利润不截断亏损 + 用披露日非报告期 | [get_val_report.py:236-316](file:///d:/GitHub/test/get_val_report.py) | P1 | ✅ |
| 7.6 | **val 删除硬编码胜率 + 统一策略数** | "55-65%"硬编码文案删除；18/20/22 三种说法统一为实际 21 | [get_val_report.py:1851-1895](file:///d:/GitHub/test/get_val_report.py) | P1 | ✅ |
**验收**：mak 无伪回测表述；val 策略数统一；val 冷跑 <8min（回归检查）

---

## V16.1 阶段 8：验收（验证循环 AGENTS.md §9）

| # | 任务分类 | 详细内容 | 状态 |
|:---:|:---|:---|:---:|
| 8.1 | 字段单位/报告期/溯源测试 | 新字段 3 股交叉；f221 报告期绑定；field_sources 完整性 | ⏳ |
| 8.2 | 缓存分键去重测试 | 行情/财报/研报/公告分键，无串键 | ⏳ |
| 8.3 | 同股三报告一次取数测试 | sht+med+lng 网络请求数 ≈ 单份 1.3x | ⏳ |
| 8.4 | 评分非 0 测试 | sht/med/lng total_score 随数据变化且非恒 0（实测 56.4/58.75/57.5）| ✅ |
| 8.5 | 全量回归 | `.\scripts
un_tests.ps1 -Mode skip_real` 全过 + py_compile + mypy + black | ⏳ |
**验收**：242+ 测试全过；无硬编码胜率/伪回测；文档（roadmap/README/field_dict）与代码一致

---

> **说明**: 本 Roadmap 为动态文档，将根据实施进度和实际情况持续更新。
