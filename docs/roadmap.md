---

# A-Stock Data Project Roadmap

> ## ⚠️ 使用本路线图前的强制提醒（2026-09-04 加固）
> 1. **R1–R3 存在两套互相矛盾的编号**（详见下方「注记 A」）。`session_notes/20260813.md` 的 R1–R5 是 **V17.0 已实际完成的重构项**；本表 **V17-1 / V17-5 / V17-6** 的 R1/R2/R3 是 **V16.2.4 静态分析遗留的旧提案**，二者毫无关系、仅编号撞车。
> 2. **V17-5（with_fallbacks 装饰器）与 V17-6（字段分发 dispatch dict）前提已失效**：V17.0 已把 fallback 收敛进 `get_canonical_stock_data` 单体、字段路由改用 `REQUIRES_REALTIME_HTTP` / `ZHB_SUFFICIENT` frozenset 集合判定（仅作测试契约元数据，不参与运行时路由）。**切勿按本表字面实现 R2/R3**，否则会触碰 `get_canonical_stock_data` ~1000 行核心单体，收益为负、风险极高。
> 3. 任何重构必须以 `AGENTS.md` §12 活跃待办 + `DEBT_LEDGER.md` 现状为准，本表旧提案仅作历史 ADR 参考。

> **本文档定位**：历史版本规划 + ADR 决策记录（记录设计「为什么」）。已落地工作的逐条明细与字段破解实锤以 [CHANGELOG.md](../CHANGELOG.md) 为准，二者不重复。
> 旧版本（V11–V16.x）多已收官；V17 起进入字段破解收官与报告体系稳定期，活跃待办见 `AGENTS.md` §12。

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
| **V15.4.3** | **easy_tdx 字段探测（成果已并入 docs/field_dict.md §12.13）+ V15.5 移植 health/reconnect** | ✅ **已完成（字典与测试）+ ✅ V15.5 移植** |
| **V16.0** | **正确性修复 + 限流加固 + 统一数据层落地 + 缓存重构 + 性能优化 + 项目清理** | ✅ **已完成（2026-08-04）** |
| **V16.1** | **报告体系重构：sht/med/lng 三视图 + ful 下线 + mak/val 引擎化 + 新字段接入** | ✅ **已完成（2026-08-05）** |
| **V16.2** | **全项目审计整改：数据正确性 + 限流统一 + 缓存 v2 + 性能优化 + 防封机制治本** | ✅ **已完成（2026-08-12）** |
| **V16.3.0** | **全项目审查整改（74 文件核查）+ 文档/依赖清理** | ✅ **已完成（2026-08-05）** |
| **V16.3.1** | **F10 财务接入 + 字典全面破解 + 东财限流治本 + 统一层梳理** | ✅ **已完成（2026-08-06）** |
| **V16.3.2** | **新数据源适配器落地（THS SDK/KPL/板块轮动）+ 新机环境适配** | ✅ **已完成（2026-08-10）** |
| **V16.4.0** | **字典架构重构（主字典=决策层,附录=实证层）+ 三大客户端逆向 + 统一层加固** | ✅ **已完成（2026-08-11）** |
| **V16.4.1** | **字段实测验证流水线 + TdxQuant 官方破解 + 报告质量 19 项修复 + 编码治本 + 全项目代码审查整改** | ✅ **已完成（2026-08-12）** |

---

## 已收官版本摘要（V11–V16.4.1）

> 以下版本均已收官。逐阶段 Phase 表、补丁表与字段破解日志已归档至 [CHANGELOG.md](../CHANGELOG.md)；字段破解实锤见 [docs/field_dict.md](field_dict.md) 与 [docs/field_verification/](field_verification/)。本文档只保留「做了什么」的概览与「为什么这么做」的设计决策（ADR）。

- **V11–V13**：统一数据层 Data Provider 启用 → Schema 强类型骨架 → 缓存透明序列化，奠定架构基础。
- **V14**：bug 修复 + 文档全量同步 + ZHB 数据集深度集成（profile.dat / tdxchain.cfg 等）。
- **V15**：CanonicalStockData 强类型合约 + ZHB 离线优先路由 + 熔断静默降级 + cdata 分层多源 / per-field source label。
- **V16.0**：正确性修复（成交额 10000 倍单位 bug 等 P0）+ 限流加固（借鉴参考仓库 em_get 统一入口）+ 统一数据层落地（`normalize_at_boundary`）+ 缓存重构（zhb_data 摘 @cached / L2 命中去 UPDATE）+ 性能 + 清理。
- **V16.1**：报告体系重构——sht/med/lng 三视图（不同持有周期），ful 下线（能力并入前三），mak/val 引擎化，push2 新字段（114 字段）接入统一层，`calculate_score` 权重修复。
- **V16.2**：全项目审计整改（数据正确性 / 限流统一 / 缓存 v2 / 性能）+ **防封机制治本**（东财封禁根因、TDX 服务器完整性、令牌桶真 bug）。
- **V16.3**：全项目审查整改 + 字典全面破解（F10 财务接入 / 0x0010 单位 / THS·KPL·levistock·板块轮动 新源调研）+ 数据新鲜度分级 + 缓存 TTL 交易日粒度。
- **V16.4**：字典架构重构（主字典=决策层，附录=实证层）+ 三大客户端逆向 + 字段实测验证流水线 + 报告质量 19 项修复 + 全项目代码审查整改。

---

## 关键设计决策与运营教训（ADR 精选）

> 以下内容是从 V16.x 海量实施日志中提取的「唯一/高价值」决策记录；纯字段破解明细见 field_dict，纯 bug 修复见 CHANGELOG。

### 防封与限流（高频踩坑，务必延续）
- 东财 **IP 级封禁可达 20+ 小时**（非 30-60 分钟）；连续 3 次 RemoteDisconnected → 自动标记封禁、20h 冷却、`em_get`/`_quick_request` 直接跳过（不浪费请求、不加重封禁）。
- push2 系**按域名共享风控面**（push2 / push2his / 83.push2 同面；datacenter-web 异面不受影响）；资金流多域轮换 `_FFLOW_HOSTS`（push2his→push2→push2delay）兜底。
- 限流铁律：东财任何窗口**全局 ≤1 req/s**（per-domain sleep 仅作下限，叠加全局令牌桶 + 跨进程锁）；东财是**隐性风控非配额型**，禁用令牌桶 burst 特性。
- 令牌桶真 bug 已修：`_quick_request` 须用 `acquire()`（原误调不存在的 `consume()` → 桶恒失效，只剩 1s 文件锁兜底）；push2 系 rps 0.6→0.4（2.5s）并共享。
- 运营商 NAT 污染：换 IP 后先 **1 次小请求验证**再放量（115.211 曾为脏 IP）。

### 数据源选型（终排，详见 field_dict §零 / 12.15）
ZHB（离线零网络）→ THS（TCP 非 HTTP，无限频）→ TDX / 腾讯 → 财联社 / 开盘红 → duanxianxia 板块轮动 → KPL 开盘啦（私有 API）→ 新浪 / 巨潮 → 同花顺 → AxData → **东财（最难，仅独有数据用）**。原则：主源优先 + 失败才降级；静态字段 `@cached` TTL 内零重复，性能影响≈0。

### 数据新鲜度分级（V16.3 M，写入 glossary §5.5）
- **A 即时**（价格/涨幅/成交额/资金流）：实时优先、ZHB 兜底 `max_delay=1`，盘中不接受 T-1。
- **B 中精度**（PE/PB/股息率/连涨/阶段涨幅）：ZHB 优先 `max_delay=3`。
- **C 静态**（股本/52周/行业/股东/分红/北向）：ZHB 无条件。
- **D 参照系**（行业排名/板块聚合）：ZHB 无条件（T-1 精度影响≈0）。

### 缓存 TTL 交易日粒度（V16.3 O24）
TTL 以「数据交易日」为界：**9:30 分界**（9:30 前=上一交易日，之后=新一天）；同一交易日内多次扫描共享缓存；**非交易日不过期**（周五缓存跨周末有效至周一 9:30）。`basic_info_static` 365 天 / `basic_info` 1 小时。K线/涨停池/板块资金流改为交易日粒度（盘中当日共享、次日 9:30 刷新）。

### 报告体系关键修复（避坑）
- **val 假成功根因**：`is_bypass`（休市）时 `_tencent_map` 未初始化 → `UnboundLocalError` 被外层 except 吞 → 提前 return 跳过写文件、却打印「已保存」。修复：失败前落盘失败报告 + 写文件前验证文件存在。
- **策略20 卡死**：净流出股 / stat2 缺字段股逐股 `get_main_net_buy`（触发东财限流 2.38s/只）→ 618s。修复：`use_zhb` 时直接跳过，纯内存 O(1) → 0.0s。
- **评分权重**：sht/med/lng 调用未传 `cfg` → 权重 `.get()` 默认 0 → 总分恒 0。修复：传 `strategy_config.yaml` 或内置默认。
- **TDX 服务器完整性**：仅 5 台 FULL（180.153.18.170 等），其余仅财务数据；`from_best_host` 按延迟选台会选中财务服务器致 K线空 → 收敛 5 台白名单 + 三项完整性验证；北交所老段(8/4)服务器无 K线 → 标的级失败记忆降级。

---

## V17 架构升级规划（v16.2.4 评估留待项；原 ANALYSIS_REPORT.md 已并入本文）

> **背景**：V16.2.4 对 minimax 静态分析逐项核对后，将"正确性相关"立即修复（B1/B5/D2 已完成）；
> 以下为**纯可维护性/重构**项，风险高、收益为"减重复/可读性"，统一留待 v17 集中做。
> **提醒**：后续任务若触及这些文件（sc_datasource/data_provider/report 脚本），可顺带按行号聚焦。

| # | 任务 | 来源 | 当前状态 | 风险 |
|:---:|:---|:---|:---|:---:|
| V17-1 | **R1: 三报告 execute_pipeline 模板抽取**（sht/med/lng ~250 行 → `BaseReportRunner._run_batch`）| ANALYSIS_REPORT R1 | ✅ **V17.0 R4 已吸收**（`execute_batch_pipeline` ~111 行抬基类，含 GD 早 init/prefetch 钩子/Semaphore(3)/快照/汇总；三脚本 execute_pipeline 现为 8–40 行薄包装）| —（已完成；✅ 测试层已补齐，剩余 5 个 Runner 装配见注记 B）|
| V17-2 | **R5: sc_datasource 拆包**（5734 行 → 子模块 package，__init__ re-export 保兼容）| R5 | 未做 | 中高 |
| V17-3 | **R6: data_provider 与 sc_datasource 职责合并**（~30 个 thin wrapper 去重，~1500 行）| R6 | 未做 | 中高（与 V17-2 一起）|
| V17-4 | **R7: lazy import 73 处 → 顶部 import**（需逐个核对循环依赖）| B7/R7 | 未做 | 中 |
| V17-5 | **R2: with_fallbacks 装饰器**（data_provider 15 个 fallback 函数 ~600 行 → 装饰器）| R2 | ❌ **前提已失效 / 不适用**（V17.0 已把 fallback 收敛进 `get_canonical_stock_data` 单体内联链，不再是 15 个独立函数）| 高（强行做需重构 ~1000 行单体，不建议）|
| V17-6 | **R3: data_provider 字段分发 if/elif → dispatch dict**（~80 行 → dict，易扩展）| R3 | ❌ **前提已失效 / 已近似达成**（无 if/elif 分发链，现为 `REQUIRES_REALTIME_HTTP`/`ZHB_SUFFICIENT` frozenset 集合判定；⚠️ 该集合仅作测试契约元数据，**不参与运行时路由**，见 AGENTS.md §8.2 注记）| 中高（转换改动面 ~200+ 行）|
| V17-7 | **A3: 配置集中**（`_BATCH=60`/`_KEEP_DAYS`/`max_delay_days` → config.py；`_top_n_large` 抽常量）| A3 | 未做 | 极低 |
| V17-8 | **A2: field_sources 标签文档**（docs/field_routing.md：realtime:tdx/tencent/push2、zhb:t-1/static、calculated、missing 语义表）| A2 | 未做 | 极低 |
| V17-9 | **D1: 14 个假异步函数处理** | D1 | 评估结论：**不改**——87 处调用方传 session，删参数改动面大；改注释提示"同步执行"可选 | 中 |
| V17-10 | **B3: data_provider field_sources 滥用 `_` 变量**（8+ 处绕写法）| B3 | 未做 | 低 |
| V17-11 | **B2: 多余三元判断**（`_safe_float(x) if x else 0`）| B2 | 未做 | 极低 |
| V17-12 | **R4: get_ful_report.py 下线清理**（2319 行，能力已并入 sht/med/lng）| R4 | ✅ V16.3 O19 已删除 | 高 — 完成 |
| V17-13 | **B6 文案: val 休市区分 closed/pre_market** | B6 | 逻辑已修（V16.2.3），仅文案未区分 | 极低 |
| V17-14 | **R8: a-stock-data-v9.6 目录** | R8 | ✅ **V17.0 已删除**（历史使命完成：对比/修复流水线均基于 v9.6 标杆，v16 系列已远超；连同 SKILL.md 与 3 个对比工具一并清理，见 V17.0 重构计划）| 高 — 完成 |
| V17-15 | **A4: 补 data_provider/main/BaseReportRunner 单测** | A4 | 未做（data_provider 仅间接覆盖）| 中 |
| V17-16 | **B4: val mcap 计数器合并 elif 链** | B4 | 评估结论：**非 bug**（前置 guard 互斥），仅可读性，可顺带 | 极低 |

> ### ⚠️ 注记 A：R1–R3 存在**两套互相矛盾**的编号（2026-08-30 标注）
>
> 本文档历史上出现过两组都叫 "R1–R3" 的编号，极易混淆：
>
> | 编号来源 | R1 | R2 | R3 | 状态 |
> |:---|:---|:---|:---|:---|
> | **本表 V17-1 / V17-5 / V17-6**<br>（源自 V16.2.4 静态分析，原 ANALYSIS_REPORT.md） | execute_pipeline 模板抽取 | with_fallbacks 装饰器 | 字段分发 dispatch dict | 见上表（1 已完成被吸收 / 5·6 前提失效） |
> | **`session_notes/20260813.md` 第二轮 R1–R5**<br>（V17.0 实际执行的重构项） | ts 口径统一（5 脚本→基类 report_ts） | 进程间隔 2 核心 + 4 薄包装 | S7 composite 链 220 行删除 | **全部已完成** |
>
> 二者**毫无关系**，仅编号撞车。引用 "R1/R2/R3" 时必须写明来源，否则会得出相反结论
> （例如误以为本表 R1 未完成 → 去重构已被 V17.0 R4 吸收的代码）。
> 核查依据见 [`verification_R1_R3_20260828.md`](verification_R1_R3_20260828.md)（2026-08-28 专文，
> 结论：**不要按本表字面实现 R2/R3**，会触碰 `get_canonical_stock_data` ~1000 行核心单体）。
>
> ### ✅ 注记 B（2026-08-30 更新：`reports/` 测试层已补齐，V17-15 部分完成）
>
> - 历史：`tests/reports/` 一度规划过（`test_report_runner.py` / `test_report_strategy.py`）但从未落地。
> - **现已补齐** `tests/reports/` 三个文件（按 `test_<层>_<主题>.py` 规约命名）：
>   - `test_reports_runner.py`（22 例）— `BaseReportRunner` 契约、`execute_batch_pipeline` 五大骨架能力
>     （代码清洗 / **并发上限 3** / **单股失败隔离** / prefetch 双钩子容错 / 快照落盘）、GD 上传编排。
>   - `test_reports_strategy.py`（12 例）— val **23 策略注册表与调度表双向一致**（防漏登记 / 防引用不存在函数）、
>     **空股票池不崩**、**策略读取的配置键真实存在**（防键名笔误静默走默认值）。
>   - `test_reports_pipeline.py`（42 例）— **5 个 Runner 子类各自的 `execute_pipeline` 装配**：
>     sht/med/lng 的共享缓存**只拉一次**并注入 `gen_kwargs`、sht 的 `depth`→席位开关、
>     prefetch 双钩子委托正确；val 的**「异步失败→同步回退」**与 **O39 假成功守卫**
>     （asyncio 成功但文件不存在时须报「未生成」而非「已保存」）、mak 无回退必须 raise。
> - 有效性经**变异测试**验证（两批共 7 处注入回归，全部被捕获）：
>   「调度表漏登记策略23」「并发上限 3→99」「单股失败不再隔离」；
>   「sht 缓存未注入 gen_kwargs」「sht depth 席位开关失效」「val 去掉同步回退」「val 去掉 O39 守卫」。
> - 现状：21 个测试文件 / 370 个测试函数（pytest 收集 398 项），**353 passed / 45 deselected / 0 failed**，
>   data / core / infra / reports 四层（reports 层 3 文件 64 例）。
> - ⚠️ **仍剩余**：**报告正文渲染结果**（章节文本/表格实际产出）仍无覆盖——需对数据层大量打桩，
>   成本高、收益低（渲染由 `md_render` 统一负责，已在其他层间接覆盖）。**V17-15（A4）视为基本完成。**

---

## V17.0 全盘重构（已完成，2026-08-13，详见 [V17.0_REFACTOR_PLAN.md](V17.0_REFACTOR_PLAN.md)）

- **目录整理**：7 支撑模块包化 `core/`（全仓 ~150 import 统一 `from core.X`，`__init__.py` 空防循环）；`credentials/` 凭据归位；v9.6 遗产全清（目录/SKILL.md/3 工具/孤儿 db）；README 体系（core/stock_common/tests/运行时+根树）。
- **代码重构**：S1 死代码 ~1000 行（21 zhb 转发+sc_zhb+12 dp 包装，__all__ 255→230）；S2 传输层统一（retry→quick 别名+async EM/GEN 分流）；S3 em_secid_prefix 新增（**修 92 北交所 secid bug**）+is_a_stock 下沉；S4 getharden 三版合一（探针实测）+cninfo 下沉（keywords 参数）；S5 写尾/ST 标注样板收敛；S8 缓存适配器删除。
- **第二轮（2026-08-13，降级项清零）**：R1 ts 基类统一；R2 进程间隔 2 核心+4 薄包装；R3 S7 composite 链 220 行删除（cdata 覆盖核对）；R4 execute_batch_pipeline 抬基类（3 脚本批量骨架收敛+钩子）；R5 sc_render 部分抽取（多评委块 3 处收敛，其余渲染章节实测异构保留）。
- **度量**：根目录 45→~20 条目；全量回归 302 passed/45 deselected 0 失败（两轮验证）。

---

## 🏁 ADR: 字段破解阶段收官(2026-08-15)

> **决策**: 停止主动字段破解, 转入维护模式
> **依据**: ①项目盘后分析实际调用 63 个统一层字段 100% 已破解+多源验证; ②剩余未知项均为历史事件/行业口径/
> DDX 短线/协议私有/重复数据, 项目零依赖; ③对撞法六源(push2/ulist/腾讯/ZHB/base.dbf/F10)互锚完毕, 边际效应严重递减
> **遗留记录**(全部入档, 不删除): Col[26]/tipinfo[7][21]/f103/f193-197/fullfinnew 8 位置/stocknow 值区/
> tdxzsbase 样本集/加密文件族/DayData 数据区——待未来策略需求定向攻破
> **维护机制**: 季度性用新财报核验已解字段(2026-08-15 中报核验修正 4 处误判为范例)
> **度量**: 破解产出 8/12 破 20+/8/13 破 15+/8/14 破 10+/8/15 破 0(新项目字段, 全为验证修正)→ 递减趋势坐实收官决策

> **说明**: 本 Roadmap 为动态文档，将根据实施进度和实际情况持续更新。
