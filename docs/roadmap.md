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
| **V16.1** | **报告体系重构：sht/med/lng 三视图 + ful 下线 + mak/val 引擎化 + 新字段接入** | ✅ **已完成（2026-08-05）** |
| **V16.2** | **全项目审计整改：数据正确性 + 限流统一 + 缓存 v2 + 性能优化** | 🔵 **进行中（2026-08-05 启动）** |

---

## V16.2 全项目审计整改（进行中）

> **启动日期**：2026-08-05
> **背景**：三路只读审计（字典一致性/缓存与效率/限流逻辑）发现 10 项 HIGH 正确性 bug、跨进程限流非互斥、
> 缓存键无 schema/version、多个脚本重复取数与伪异步阻塞。
> **执行顺序**：Phase1(正确性) → Phase2(限流) → Phase3(缓存) → Phase4(性能)
> **硬性约束**：每阶段独立 commit + 验证循环；修复不得引入新 bug（回归 262+ 测试全过）；
> 盘中数据不得用 T-1 伪装实时；限流不得放松。

### V16.2 Phase 1：数据正确性修复（H1-H10）

| # | 问题 | 修复方案 | 状态 |
|:---:|:---|:---|:---:|
| 1.1 | 盘中实时字段被 ZHB T-1 覆盖（tdx_get_quote_full 先合并 ZHB，TDX 只补缺不覆盖）| 盘中/盘后 TDX 实时值**覆盖** ZHB；盘前才用 ZHB；来源标签与数据真实一致 | ✅ |
| 1.2 | ZHB 日期解析失效（YYYYMMDD 按 %Y-%m-%d 解析 + timedelta 未导入）| 统一日期解析 + 顶部导入 timedelta + 交易日偏移修复 | ✅ |
| 1.3 | 报告期/行情日期/上市日期混用（f221 未请求、data_date=本机日期、list_date 回退 data_date）| 请求 f221；data_date 用接口日期；list_date 失败置空不回退当天 | ✅ |
| 1.4 | easy_tdx adapter 与调用方接口不匹配（finance vs get_finance_info、updated_date 下划线丢失）| adapter 补 get_finance_info 别名 + 保留下划线；调用方统一走 adapter | ✅ |
| 1.5 | 解禁单位错配（FREE_SHARES=万股 被 /1e4；FREE_RATIO=小数 当 %）| 统一规范单位，报告按规范换算；risk 引擎对齐 | ✅ |
| 1.6 | 总股本单位不一致（万股 vs 股）| 统一 Canonical 输出万股；sc_capital_cache/报告对齐 | ✅ |
| 1.7 | 报告脚本北交所硬编码（mak/sht/val 自行判断阈值）| 全部改走 get_board_type/is_limit_up/is_limit_down | ✅ |
| 1.8 | 动态概念代码当行业用（tdxstat2 Col13 概念映射到行业聚合）| 区分 industry/concept/dynamic_theme 三来源 | ✅ |
| 1.9 | 资金流 HTTP 兜底字段/单位错（无 main_net_hands；金额当量）| 拆分明细字段，main_net_buy_hands 独立来源 | ✅ |
| 1.10 | Canonical 扩展字段未进主字段（push2 EPS/BPS/52周/PE 已解析未覆盖）| 明确 ZHB/实时覆盖规则，扩展字段完整进 Canonical | ✅ |
**验收**：盘中 600519 price/amount 为 T 日；报告期不混用；解禁/股本/资金流单位规范；262 测试全过

### V16.2 Phase 2：限流统一（跨进程互斥 + 旁路收敛）

| # | 问题 | 修复方案 | 状态 |
|:---:|:---|:---|:---:|
| 2.1 | 跨进程锁非互斥（每进程独立锁文件）+ mtime 无原子抢占 | 改为 SQLite 原子 reservation 或 Windows Named Mutex；进程间 token bucket | ✅ |
| 2.2 | em_get 熔断被自己吞 + 403 后 _on_success | CircuitBreakerError 冒泡；403 不重置熔断；429 读 Retry-After | ✅ |
| 2.3 | _quick_request 绕过令牌桶/熔断 | 统一接入 TokenBucket + CircuitBreaker + 域级预算 | ✅ |
| 2.4 | levistock/AxData 限流旁路 | provider 级缓存 + 错误分类（无数据 vs 被限流）+ timeout + 固定版本 | ✅ |
| 2.5 | 腾讯批量绕过统一限流 | 腾讯批量接入独立 token bucket + 跨进程协调 | ✅ |
| 2.6 | 异步限流与同步不一致（无 TokenBucket/域隔离/403 统计）| 异步层按域 token bucket + 熔断 + 403/429 统一 | ✅ |
| 2.7 | TDX 裸 client 调用未加锁/throttle（finance/F10/健康检查等）| 全部收敛到 _TDX_CALL_LOCK + _tdx_throttle | ✅ |
| 2.8 | TLS 校验默认关闭 | verify=True 默认；显式需要处单独注明 | ✅ |
**验收**：并发 3 进程东财 ≤1rps；levistock/AxData 受预算控制；无绕过入口

### V16.2 Phase 3：缓存 v2（schema envelope + L1 一致性）

| # | 问题 | 修复方案 | 状态 |
|:---:|:---|:---|:---:|
| 3.1 | 缓存键无 source/schema/version | 键+值含 schema_version/source/trade_date/report_period；schema 不符拒绝命中 | ✅ |
| 3.2 | trading_day=True 覆盖 TTL | 过期策略与 TTL 分离；实时短 TTL、日频 trade_date、静态数据日期 | ✅ |
| 3.3 | L1 绕过 verified/stale | L1 存 (value, expiry, verified, schema)；cross_verify 只返回 verified | ✅ |
| 3.4 | clear_all/clear_expired 不清 L1 | 所有失效路径清 L1 + generation/epoch | ✅ |
| 3.5 | 无 single-flight | per-key single-flight（同 key 并发 1 次上游）| ✅ |
| 3.6 | K线缓存无日期/复权/来源 + pickle 非原子 | 版本化键 + 原子写（temp+replace）+ 只缓存完整K线 | ✅ |
| 3.7 | 失败结果永久缓存 | 空值负缓存 ≤30s 或区分 无数据/请求失败 | ✅ |
| 3.8 | 移动窗口未进键（公告/解禁/涨停池/情绪）| 规范化 trade_date/end_date 进键 | ✅ |
**验收**：同 key 并发 5 次最多 1 次上游；clear_all 后 L1/L2 均不返回旧值；报告期变化财务缓存立即刷新

### V16.2 Phase 4：性能优化（安全前提下）

| # | 问题 | 修复方案 | 状态 |
|:---:|:---|:---|:---:|
| 4.1 | ZHB 纯本地字段仍走 SQLite | 纯 ZHB 函数绕过 SQLite 用 RAM generation | ✅ |
| 4.2 | SHT 重复（hsgt 预取丢弃/热榜 2 次/盘口异动 4 类逐股）| RunContext 复用市场级数据一次；盘口异动建立 code 索引；ths_hot_reason 按 date 一次拉取全市场缓存 | ✅ |
| 4.3 | MED/LNG 重复（composite+canonical 双链/EPS 研报重复）| 单次 canonical；研报一次拉取复用 | ✅ |
| 4.4 | VAL 休市仍全市场批量 + 多 K 线根数 | 先判市场状态（休市/盘前零腾讯批量）；单股一次最大 K 线集切片 | ✅ |
| 4.5 | MAK 腾讯批量重复 + 行业成员重复加载 | 运行级缓存；snapshot 一次 | ✅ |
| 4.6 | 伪异步阻塞（同步调用在协程中）| 统一 to_thread / 有界线程池 | ✅ |
**验收**：盘前/休市 VAL 全市场实时请求 0；MAK 腾讯批量 ≤1 次；单股每次 ≤1 份最大 K 线集；优化前后评分一致

### V16.2.1 补丁（2026-08-05，用户实跑日志暴露 3 个问题）

| # | 问题 | 修复 |
|:---:|:---|:---|
| P1 | get_mak_report `limit_pct_for` is not defined（模块级未导入，仅局部函数导入）| 加入 mak 顶部 `from stock_common import` 块 |
| P2 | get_sht_report `is_limit_up` is not defined（import 块缺函数）| 加入 sht 顶部 import 块（is_limit_up/is_limit_down/limit_pct_for）|
| P3 | easy_tdx K线空响应（ret_count 撒谎/服务器截断）被当"真无数据"写进程缓存，且每只失败股触发 easy_tdx 全服务器 ping 拖慢扫描 | tdx_get_security_bars：首轮空响应换台重试一次（直接置空全局客户端）；二轮仍空仅写进程缓存不写磁盘；连续 5 次空响应强制重建连接（_TDX_EMPTY_STREAK 计数）；成功清零 |
### V16.2.2 补丁（2026-08-05，二次实跑日志：sht 失败 + K 线空响应根因）

| # | 问题 | 修复 |
|:---:|:---|:---|
| P4 | get_sht_report `name 'name' is not defined`：limit_pct_for/is_limit_up 引用不存在的 `name` 变量 | 改为 `stock_name`（generate_report_async 内 L353 定义，AST 验证 4 处作用域正确）|
| P5 | **K 线空响应根因**：`_easy_market` 把北交所（8/4/92 开头）映射到深圳(0)/上海(1)，easy_tdx Market.BJ=2 从未被使用 → 服务器对错误 market 返回空响应（"声称 800 条但首条即解析失败"）| 三处统一修复：`_easy_market`/`_market_from_code`/`_market_prefix` 均识别 8/4/92 → 北京(2/bj)；新增 test_bse 测试用例 |
| P6 | mak/sht/val 顶部 import 已补 limit_pct_for/is_limit_up（P1/P2 复验）| verify：三脚本 import + 阈值语义全过 |
**验证**：263/263 测试全过（+1 北交所映射测试）；AST 作用域验证 4 处 stock_name 引用；mak/sht import 冒烟通过

### V16.2.3 补丁（2026-08-05，报告对比 v9.6 核查 + 限流全面审计）

**A. 数据正确性（对比 a-stock-data-v9.6 报告）**

| # | 问题 | 修复 |
|:---:|:---|:---|
| A1 | lng 总股本 2080086.25 亿股（放大 1e4）：easy_tdx zong_guben 实为**股**（源码注释"万股"错误，_SCALE=10000 乘出）| lng 显示回 /1e8；get_stock_info 反推去 /1e4；**sc_capital_cache TDX 路径 +/1e4 转万股**（真正与 push2/canonical 对齐）|
| A2 | sht 解禁 2011833万股（应 201万）：F10/RPT_LIFT_STAGE 的 shares 单位=**股** | shares 统一股口径；sht/med/lng 显示 /1e4 万；lng 解禁市值 股×价/1e8 |
| A3 | med 融资余额环比 -92.53%（balance_gr 已是百分数，×100 多余）| 去掉 *100 |
| A4 | lng/med 分红"暂无记录"误报（TDX xdxr 失败返回 [] 与真无分红混淆）| tdx_get_dividend_history 失败返回 None；lng/med 显示区分"接口失败/真无分红"；val len(None) 崩溃修复 |
| A5 | sht/med/lng 舆情章节混入全市场财联社快讯（无个股过滤）| 新增 news_matches_stock（代码/全名/简称）；三脚本过滤 |
| A6 | sht 换手率恒 0.00%（TDX 0x010C 无换手率 + ZHB 无此字段）| canonical turnover 补腾讯兜底（@cached 无额外开销）|
| A7 | sht 二章缺振幅/涨停价/跌停价（V16.1 重构丢失）| 恢复（振幅自算、涨停价 cdata.limit_up/down）|
| A8 | sht 五章缺"最近分红"行（zhb 股息率有值时不再查询分红）| 改为无条件查询并补显示 |

**B. 限流全面审计（用户反馈仍频繁被限流）**

| # | 根因 | 修复 |
|:---:|:---|:---|
| B1 | **同步/异步双通道各自限流**：lng/med 混合调用（get_stock_composite_async 异步 + get_canonical to_thread 同步）→ 同进程合计 2rps，超东财 push2 0.6rps 风控阈值 → 403/429 | 异步层与同步 `_EM_LAST_CALL` 共享全局时间戳，双通道合计 ≤1rps |
| B2 | em_get 429 直接返回 None（瞬时风控误报接口失败）| 429 退避（Retry-After 优先）后重试一次；403 仍直接失败（防加速封禁）|
| B3 | cninfo_irm（巨潮互动易）直连无节流，每次 2 请求逐股调用 | 加 _gen_wait_process_interval 进程级礼貌限速 |
| B4 | 交易所龙虎榜直连（szse/sse）无节流 | 低频（每日一次）可接受，已评估保留 |
| B5 | levistock 3 处已节流（V16.2）复验 ✓ | — |
**验证**：263/263 全过（test_tdx_dividend_history 断言更新为 (list, None)）；语法全过

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
| 6.3 | **文档合并** | field_dict/script_data_dict/tdx_field_dict/zhb_field_dict → 统一字段参考 | [docs/](file:///d:/GitHub/test/docs) | P2 | ✅ |
| 6.4 | **死代码清理** | print_cache_stats 双定义、MAX_CONCURRENT_* 死配置、PUSH2_FIELD_MAP 残留 | 多处 | P2 | ✅ |
| 6.5 | **超长函数拆分（暂缓：纯重构，先验证数据正确性）** | `run_discovery_async` 347行、`generate_sector_report` 446行 | [get_ful_report.py](file:///d:/GitHub/test/get_ful_report.py), [get_mak_report.py](file:///d:/GitHub/test/get_mak_report.py) | P2 | ✅ |
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
| 2.1 | **StockContext 建立** | 单股一次加载 canonical + quote_extended + technical + fundamental + fund_flow + ownership + events + quality，sht/med/lng 共用 | [stock_common/sc_context.py](file:///d:/GitHub/test/stock_common/) | P0 | ✅ |
| 2.2 | **MarketContext 建立** | 全市场快照 + 批量行情 + 四池 + 行业资金流 + 情绪指标，mak/val 共用 | [stock_common/sc_context.py](file:///d:/GitHub/test/stock_common/) | P1 | ✅ |
| 2.3 | **main.py 合并模式** | `--sht/--med/--lng 同一股票列表` 改为单进程内共享 StockContext 渲染三份，去掉子进程重复取数 | [main.py](file:///d:/GitHub/test/main.py) | P1 | ✅ |
| 2.4 | **修复 calculate_score 权重** | sht/med/lng 调用时未传 cfg → 权重 .get() 默认 0 → 传 strategy_config.yaml scoring 或内置默认权重 | [get_sht_report.py:1512](file:///d:/GitHub/test/get_sht_report.py), [get_med_report.py:1068](file:///d:/GitHub/test/get_med_report.py), [get_lng_report.py:912](file:///d:/GitHub/test/get_lng_report.py), [sc_scoring.py](file:///d:/GitHub/test/stock_common/sc_scoring.py) | P0 | ✅ |
| 2.5 | **缓存键分层** | 行情/财报/研报/公告/新闻/资金流分键（code+trade_date / code+report_period / code+infoCode / announcementId） | [stock_cache.py](file:///d:/GitHub/test/stock_cache.py) | P1 | ✅ |
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
| 8.1 | 字段单位/报告期/溯源测试 | 新字段 3 股交叉；f221 报告期绑定；field_sources 完整性 | ✅ |
| 8.2 | 缓存分键去重测试 | 行情/财报/研报/公告分键，无串键 | ✅ |
| 8.3 | 同股三报告一次取数测试 | sht+med+lng 网络请求数 ≈ 单份 1.3x | ✅ |
| 8.4 | 评分非 0 测试 | sht/med/lng total_score 随数据变化且非恒 0（实测 56.4/58.75/57.5）| ✅ |
| 8.5 | 全量回归 | `.\scripts
un_tests.ps1 -Mode skip_real` 全过 + py_compile + mypy + black | ✅ |
**验收**：242+ 测试全过；无硬编码胜率/伪回测；文档（roadmap/README/field_dict）与代码一致

---

## V17 架构升级规划（v16.2.4 评估留待项，来源 docs/ANALYSIS_REPORT.md）

> **背景**：V16.2.4 对 minimax 静态分析逐项核对后，将"正确性相关"立即修复（B1/B5/D2 已完成）；
> 以下为**纯可维护性/重构**项，风险高、收益为"减重复/可读性"，统一留待 v17 集中做。
> **提醒**：后续任务若触及这些文件（sc_datasource/data_provider/report 脚本），可顺带按行号聚焦。

| # | 任务 | 来源 | 当前状态 | 风险 |
|:---:|:---|:---|:---|:---:|
| V17-1 | **R1: 三报告 execute_pipeline 模板抽取**（sht/med/lng ~250 行 → `BaseReportRunner._run_batch`）| ANALYSIS_REPORT R1 | 未做（sc_report_runner.py:98 仅 execute_pipeline）| 中 — 需 test_report_runner 扩充 |
| V17-2 | **R5: sc_datasource 拆包**（5734 行 → 子模块 package，__init__ re-export 保兼容）| R5 | 未做 | 中高 |
| V17-3 | **R6: data_provider 与 sc_datasource 职责合并**（~30 个 thin wrapper 去重，~1500 行）| R6 | 未做 | 中高（与 V17-2 一起）|
| V17-4 | **R7: lazy import 73 处 → 顶部 import**（需逐个核对循环依赖）| B7/R7 | 未做 | 中 |
| V17-5 | **R2: with_fallbacks 装饰器**（data_provider 15 个 fallback 函数 ~600 行 → 装饰器）| R2 | 未做 | 中 |
| V17-6 | **R3: data_provider 字段分发 if/elif → dispatch dict**（~80 行 → dict，易扩展）| R3 | 未做 | 极低 |
| V17-7 | **A3: 配置集中**（`_BATCH=60`/`_KEEP_DAYS`/`max_delay_days` → config.py；`_top_n_large` 抽常量）| A3 | 未做 | 极低 |
| V17-8 | **A2: field_sources 标签文档**（docs/field_routing.md：realtime:tdx/tencent/push2、zhb:t-1/static、calculated、missing 语义表）| A2 | 未做 | 极低 |
| V17-9 | **D1: 14 个假异步函数处理** | D1 | 评估结论：**不改**——87 处调用方传 session，删参数改动面大；改注释提示"同步执行"可选 | 中 |
| V17-10 | **B3: data_provider field_sources 滥用 `_` 变量**（8+ 处绕写法）| B3 | 未做 | 低 |
| V17-11 | **B2: 多余三元判断**（`_safe_float(x) if x else 0`）| B2 | 未做 | 极低 |
| V17-12 | **R4: get_ful_report.py 下线清理**（2319 行，能力已并入 sht/med/lng）| R4 | ✅ V16.3 O19 已删除 | 高 — 完成 |ep 全调用含测试 |
| V17-13 | **B6 文案: val 休市区分 closed/pre_market** | B6 | 逻辑已修（V16.2.3），仅文案未区分 | 极低 |
| V17-14 | **R8: a-stock-data-v9.6 目录** | R8 | **明确不做**（AGENTS.md 硬性"只读参考标杆"，禁止删除）| — |
| V17-15 | **A4: 补 data_provider/main/BaseReportRunner 单测** | A4 | 未做（data_provider 仅间接覆盖）| 中 |
| V17-16 | **B4: val mcap 计数器合并 elif 链** | B4 | 评估结论：**非 bug**（前置 guard 互斥），仅可读性，可顺带 | 极低 |

> **V16.2.4 已完成项**：B1（main.py proc 初始化）、B5（腾讯字段索引 `_TENCENT_FIELD_INDEX` 三处统一 + 长度告警）、D2（`get_history_fund_flow_120d` 统一 sht/med 资金流入口，删除 sht 死代码 `_get_eastmoney_fund_flow_120d`）。
> **V16.2.5 报告核查（2026-08-04 晚间实跑，用户反馈仍失败）**：
> - **根因**：`push2/push2his.eastmoney.com` 对该 IP **连接级风控**（RemoteDisconnected，非 403/429）→ 资金流接口连续失败（sht 七章/med 十一章），而 datacenter-web 域正常（两融/北向/大宗成功）
> - **修复**：fflow 接口**多域轮换** `_FFLOW_HOSTS`（push2his 全窗口 → push2 → push2delay 延时镜像单日保底，`_em_fflow_request`），`_DOMAIN_LIMITS` 补 push2delay 配置；风控恢复后自动回全窗口
> - **附修**：sht/med 资金流统计按实有数据条数标注（防"1 天/20 天"误导）；lng `[ZHB EPS] 对应PE 68.9x` 误导（单季 EPS 当 TTM 用）→ 改标"单季口径"；解禁占比 4.90% 经 datacenter RPT_LIFT_STAGE 权威核对一致（FREE_SHARES=2011832 股/FREE_RATIO=0.0490，v9.6 的 0.05% 才是错的）
> **V16.2.6 东财接口健康度矩阵（tests/test_eastmoney_health.py，新增）**：
> - 按域名分组 13 项探测（push2/push2his/83.push2/push2delay/push2ex/datacenter-web/datacenter/reportapi/np-weblist/emappdata/mobappconfig/search-api-web/quote）
> - 判定三态：PASS / SKIP(403·429·RemoteDisconnected·超时=风控可恢复，非代码回归) / FAIL(200 但数据校验失败=协议变更)
> - 遵守限流纪律：域间 ≥1.8s 间隔；`REAL_NETWORK=1` 才运行（离线套件自动排除）
> - **首次实测矩阵（2026-08-04 夜）**：push2/push2his/83.push2 🔴 连接级风控（RemoteDisconnected）；push2delay/push2ex/datacenter×2/reportapi/np-weblist/emappdata/mobappconfig/search/quote ✅ 正常 → 印证"东财按域名分风控面"，资金流多域轮换（V16.2.5）方向正确
> - 运行：`$env:REAL_NETWORK=1; .\scripts\run_tests.ps1 -Mode module -Path tests/test_eastmoney_health.py -ExtraArgs '-v'`
> **V16.2.7 防封机制失效根因核实（2026-08-05）**：
> - **根因 A（限流遗漏·真 bug）**：`_quick_request` 的令牌桶调用 `consume()` —— **TokenBucket 无此方法**（只有 acquire/try_acquire），每次抛 AttributeError 被 except 吞掉 → **桶从未生效**（只剩 1s 文件锁兜底）
> - **根因 B（时间设置）**：push2 系 3 域**独立桶**（push2/push2his/83.push2 各 0.6rps）= 同风控面合计 1.8rps 叠加；且实测 0.6rps 连续探测 5 分钟即触发连接级风控（恢复后少量请求又触发）→ **阈值极低**，已降到 **0.4rps（2.5s）** 并共享
> - **根因 C（链路放大）**：TDX 断连时所有 TDX 接口（belong_boards/board_members/board_list/K线/分红）fallback 到 push2 → 请求量暴涨
> - **修复**：① `_quick_request` consume→acquire + 补 `_EM_LAST_CALL` 全局时间戳（与 em_get 同强度）② `_normalize_em_domain()`：push2/push2his/83.push2/1.push2/2.push2 桶+熔断器归一化共享（em_get/_quick_request/异步层 8 处）③ push2 系 rps 0.6→0.4、sleep 1500→2500 ④ 指数 K 线（index_quote/index_bars）空响应换台重试（与个股一致）⑤ **mak A 股过滤**（ZHB 7948 只含 ETF/基金 → 前缀白名单 00/30/60/68/92，与 val 同口径）⑥ 健康度测试 push2delay 兼容 rc=100（早盘无当日数据）+ 运行间隔提示
> - **实测**：push2 系 12h 后自动恢复（多域轮换自动回 push2his 全窗口 60 行）；矩阵 11 PASS/2 SKIP（连续探测又触发，印证阈值极低）
> **V16.2.8 对齐参考仓库 PR#36 防封铁律（2026-08-05）**：
> - **PR#36 核心结论**（luodada99 实战）：push2 全系列 IP 级封禁 **20+ 小时**（非 30-60 分钟）；触发根因=无间隔/高并发/超大量；datacenter-web 不同 WAF 不受影响；**连续 3 次 RemoteDisconnected → 标记封禁 → 跳过东财**（参考 v3.3.2 em_get 防封核心）；腾讯 K 线 5000+ 次是限流非封 IP
> - **修复**：① 新增封禁自动检测 `_record_em_disconnect`/`_em_is_banned`（连续 3 次断连 → 20h 冷却，em_get/_quick_request 直接跳过，不浪费请求不加重封禁）② 403 文案"30-60 分钟"→"20+ 小时"（2 处）③ 健康度测试文案同步 ④ **TDX 断联根因**：项目硬编码 3 台服务器 vs easy_tdx 内置 40+ 台 → `from_best_host` 改用 `get_known_hosts()` 全量列表（扩大可用面，降断联概率）
> - **腾讯 44/45 核对**：`_TENCENT_FIELD_INDEX` 44=流通/45=总 **与 PR#36 实测一致 ✓**（无需改）
> **V16.2.9 TDX 服务器数据完整性（2026-08-05 全量探测证实用户质疑）**：
> - **实测结论**：部分 TDX 服务器**只提供财务数据**——150.158.160.2 / 124.71.187.122 / 111.229.247.189（均在项目 preferred / easy_tdx fallback 前列）bars/quotes 恒空仅 finance OK；全量服务器为 180.153.18.170（primary）/ 115.238.56.198 / 115.238.90.165 / 218.75.126.9；另有 6 台连接超时不可达
> - **根因**：`from_best_host` 按**延迟**选台（0.2s 最快的 150.158.160.2 是财务服务器）→ 连接成功但 K线/报价全空（"声称 800 条"警告来源）；且我 V16.2.9 首版 `_tdx_host_data_complete` 误用 `client.bars()`（TdxClient 原生为 `get_security_bars`）→ AttributeError 被吞 → 验证恒 False → 全部走不验证的 from_best_host fallback
> - **修复**：① `_tdx_host_data_complete` 改原生 API（get_security_bars/get_security_quotes/get_finance_info 三项验证）② primary 先验证，失败后逐台探测（前 10 台）③ **from_best_host fallback 结果也强制验证**，不全则放弃 easy_tdx（宁缺毋滥，避免静默数据不全）
> - **实测验证**：create 0.8s 选中 180.153.18.170（bars=5/quotes=1/finance=1 全通过）
> **V16.2.10 换 IP 前遗留排查（2026-08-05）**：全仓扫描确认 push2 系 12 处 URL 入口全部走统一限流——
> 发现并修复 2 处遗漏：① `get_val_report.py:922`（策略09 日历效应 JP_URL=83.push2 clist）原走 `_request_with_retry`（无桶/熔断/封禁跳过/跨进程锁）→ 改 `_quick_request` ② `get_ful_report.py:1512`（np-weblist 快讯）同改；其余 NO-ENTRY 均为合法（备胎 URL 列表/常量/调用在 URL 行前）
> **V16.2.11 换 IP 后全量核查（2026-08-05）**：
> - **东财 13 域**：换 IP 后健康度矩阵 **13/13 全部 PASS**（push2/push2his/83.push2 封禁解除，IP 风控突破成功）
> - **TDX 54 台全量核查**（easy_tdx known hosts + 通达信 HQHOST 43 + HFHost 2 去重，逐台 bars/quotes/finance 三项）：
>   - **FULL 仅 5 台**：180.153.18.170、115.238.56.198、115.238.90.165、218.75.126.9、**159.75.55.232**（通达信 HFHost 深圳备用站，新发现）
>   - 39 台 INCOMPLETE（bars/quotes 恒空仅 finance OK）——通达信"双线主站"实为**接入/财务服务器**，不提供 0x010C 行情 K 线；6 台连接失败
>   - 通达信 DSHOST（16 台，Port 7727）为扩展市场协议（基金/港股），项目 std 行情(7709)不适用，未纳入
> - **修复**：`_EASY_TDX_PREFERRED_HOSTS` 收敛为 **5 台 FULL 白名单**；`_create_easy_tdx_adapter` 探测只遍历白名单（不再遍历 45 台浪费时间）；运行时仍强制三项完整性验证（防白名单服务器状态变化）
> - **实测验证**：create 0.8s 选中 primary（180.153.18.170 FULL），bars/finance 全链路正常
> **V16.2.12 mak K 线空响应根因定位（2026-08-05）**：
> - **实测定位**：空响应标的为**北交所老段（8/4 开头，如 832000/430047）**——白名单 5 台服务器全部无其 K 线（easy_tdx 库内换台 5 台仍空，每次浪费 6-12s）；920 新段正常（rows=30 ✓），沪/深/双创全正常
> - **修复**：① `tdx_get_security_bars`：北交所老段空响应**跳过换台重试**（服务器确认无此标的）+ **标的级失败记忆**（`_TDX_KLINE_EMPTY_UNTIL`，5 分钟内直接返回空，防重复 6-12s）② mak `count_history_deviations` 对 8/4 开头直接 hist_cnt=0（正确降级，省 7s/只）
> - **实测验证**：832000 首次 6.9s（原 12.3s）→ 同标的后续 **0.00s**；不同 count 也命中记忆 ✓
> **V16.2.13 K 线警告彻底消除（2026-08-05）**：
> - **进一步定位**：92 新段也有个别股票服务器无 K 线（920013 实测空，20 只中 1 只）——mak 空响应的真实标的为 92 个别新股（8/4 老段不在 A 股池）
> - **修复**：① `_EasyTdxAdapter.bars` 对 8/4 老段直接返回空（**不调用 easy_tdx → 零警告零耗时**，实测 0.000s）② 去掉项目层冗余重建换台（easy_tdx 已内部换台白名单 5 台，空 df=标的确无）→ 92 个别首次 12.3s→6.0s ③ **logging 过滤器精确抑制 easy_tdx "声称/首条即解析失败" 警告**（标的无数据的正常降级提示，不影响其他协议错误日志）④ **修复潜在死锁**：except 分支原 `_reset_tdx_connections()` 在 `_TDX_CALL_LOCK` 内重入锁（threading.Lock 不可重入）→ 改直接置空全局
> - **实测验证**：920013 首次 6.9s **零警告输出**；832000/430047 0.000s 零警告；600519 正常
> **V16.2.14 报告细节整改（2026-08-05，v15 vs v9.6 对比定位）**：
> - **分红失败根因（非 TDX 不可用）**：`_EasyTdxAdapter` **缺 `xdxr` 方法**——`tdx_get_dividend_history` 调 `client.xdxr()` 抛 AttributeError 被误报"TDX 接口暂不可用"（v9.6 mootdx 有 xdxr 所以正常）→ 补适配器 xdxr（easy_tdx get_xdxr_info）+ date 列双格式兼容（easy_tdx 'date' vs mootdx year/month/day）→ 实测 19 条含日期，与 v9.6 一致
> - **val 策略04 PE 荒谬（18337420x）根因**：新浪财报累计值**跨年边界拆解错误**——每年 Q1 累计 < 去年 Q4 累计，相减得大负数 → TTM/PE 错乱 → 每年 Q1 直接用累计值 → 招商银行 18337420x→**5.82x** ✓
> - **mak**：① 名称缺失根因=腾讯覆盖循环只补 price/change_pct 未补 name → 补全 ② G 同花顺强势股与 B/B+ 涨停池重复 → 改为**交叉验证**（重叠计数 + 只展示同花顺独家）
> - **sht**：涨停价 push2 f51 盘中为 0 → 按板块阈值推算兜底；快讯 7h→48h；问答加标题/48h/答案（空标"待回复"）/10 条标注
> - **med/lng**：问答 48h+标题+答案；lng 30 天窗口标注"最新 10 条"
> - **资金流口径说明**：v15 用东财 fflow（业界标准），v9.6 用 TDX 0x0011（通达信口径）——两源数值不同属口径差异，v15 更标准
> **V16.2.15 行业名称差异分析（v15"元器件" vs v9.6"光学光电"）**：
> - **根因**：通达信行业板块**层级服务器相关**——白名单 4 台实测全部返回 type=2（行业二级"元器件"，000100 唯一行业板块）；v9.6 运行时连的服务器返回 type=0/1（行业一级"光学光电"）；v9.6 type_map 不含 type=2 所以当时显示一级
> - **结论**：一级行业（"光学光电"）更贴近东财 f127"光学光电子"/申万口径、对 TCL 描述更准（108 家聚焦）；二级"元器件"粒度粗（312 家泛）；v15 稳定性更优（白名单全一致）
> - **修复**：`tdx_get_belong_boards` industry 排序**一级(0/1/12)优先、二级(2)兜底**——遇多层级返回时优先通用口径；当前白名单仅二级 → 仍显示"元器件"（合理兜底）
>
> **V16.2.16 行业分类标准核查 + 全链路统一（2026-08-05）**：
> - **核查结论**：TDX(880xxx 通达信自建)/东财 f127(东财自建)/ZHB Col[13](特色板块) **均非申万官方**；ZHB 881xxx 为通达信收录申万版（无一级映射、无股票关联）；申万官方 801xxx 项目内无现成来源
> - **东财一级=申万同源**：datacenter `RPT_EM_BOARD_CONSTITUENT` type=2 一级行业与申万一级同名（电子/食品饮料/家用电器/银行…31 个），且 **datacenter-web 域与 push2 风控无关（f127 会加封禁风险）**
> - **实施**：`get_em_industry_map()` 全市场 5625 只一次分页拉取（52s）+ 内存/磁盘双缓存 7 天；canonical L0 东财一级优先；mak 板块聚合改用东财一级 + `is_industry_code` 过滤（Col[13] 只接受 8803/8804/881 段）
>
> **V16.2.17 统一申万二级 + Col[13] 重新定性 + 缓存版本化（2026-08-05，用户决策：二级更细更优）**：
> - **申万二级统一**：`get_em_industry_l2_data()` → {code: 二级名} + {二级名: [成员]} 双映射；二级识别=排除一级名单后 code 最小（000100→光学光电子/600519→白酒Ⅱ/000651→白色家电/300750→电池/银行系→银行Ⅱ，129 板块零三级误判）；缓存文件 `em_industry_map_l2.json`/`em_industry_members_l2.json`（版本隔离防污染）
> - **全链路接入**：canonical industry L0（东财申万二级）→ mak 板块聚合 → `get_industry_peers` 同业对比（东财二级成员 + 腾讯批量市值排行 + A 股过滤，京东方Ａ≠京东方Ｂ）→ `get_stock_sector_rank` 板块内排名
> - **缓存防污染**：`get_industry_peers`/`get_stock_sector_rank` category 升级 `industry_peers_v2`（旧 v1 缓存含 TDX 路径 B 股数据，11 条已 invalidate）——**口径变更必须换缓存版本号**
> - **Col[13] 重新定性（写入字段字典）**：实测证据链——值域 31%空+57%特色板块+12%申万行业；880823"微盘股"197 只成交额全部≤2.93 亿（中位 0.35 亿，无一>5 亿）→ **T 日条件筛选板块（非热度排行），个股只取其一 → 每日变化/不全**；官方注释"行业板块代码"为误标（用户猜想方向正确：T 日动态板块）；同步 zhb_client docstring + field_dict.md + get_industry_code 注释
> - **股票名称缓存评估（用户问题）**：**结论=现状已合理，不新增持久化名称字典**——腾讯批量按交易日缓存（当日名称准确，ST/更名次日自动失效）；ZHB profile.dat 天然离线当日字典；持久化跨天字典会引入旧名称污染（与用户"防污染"原则冲突）
>
> **V16.2.18 ZHB 未知字段破解（2026-08-05，3 天 Delta + injoyai 官方源码 + 东财 f189 交叉）**：
> - **tdxstat [12] = 新股开板日**（破解）：2016+ 新股上市后首次不再涨停日期；东财 f189 上市日交叉验证 24 样本 18/24 精确（001203 大中矿业 10 日历日=8 交易日✓、300750 宁德 8 交易日✓），余差 1 天为节假日近似
> - **tdxstat [13] = 上市连板数（交易日）**（破解）：开板日-上市日间交易日数（300750=8 连板✓、001223 首日开板=0✓）；Col[12]/[13] 构成次新股开板数据对
> - **区间涨跌幅字典修正**（injoyai/tdx model_stat.go 130 日日线核验 MAE）：[17]=近20根K线、[18]=20日、[19]=近60根K线、[20]=60日、[21]=YTD——**不存在 30日/90日字段**（原 [18]"30d"、[20]"90d?" 误标）；zhb_client 新增 change_20k_bar/change_60k_bar 精确名，历史 key 保留兼容
> - **tdxstat2 [4] = 疑涨跌停封单额(万元)**（部分破解）：有值 144 只中 143 只涨跌停（600530 跌停也有值），122 只涨停无值（未封住）；[6]/[8] 疑资金分档（大单/特大单）
> - **未破解**：tdxstat [23]（0-95 离散枚举 24 类，7 月末 31/32 峰值 8 月初重置，疑月度累计计数）、[26]（0-48 恒定分类）、[31-33]（稀疏）、tdxstat2 [19]/[20]（涨跌幅类非标准周期，疑主力成本偏离）——injoyai 均未命名，待官方文档
> - **实现**：zhb_client 新增 unseal_date/board_count/change_20k_bar/change_60k_bar 映射（纯增量零破坏）；docstring + field_dict.md 同步；263/263 回归通过

> **V16.3 全项目审查整改（2026-08-05，74 文件全量核查后用户批准全改）**：
> - **A 级（立即修）**：
>   - A1 opencode.jsonc 重复 `permission` key（L14 被 L86 覆盖→run_tests.ps1/py_compile 权限静默失效）→ 合并两块
>   - A2 `zongguben` 单位口径三处不一致（sc_capital_cache:130 除 10000 / sc_schema:645 声称万股 / sc_datasource:1133 当股）→ 统一为**股**（V16.2.3 已确认 easy_tdx 口径）
>   - A3 tdx_client 独立限流表含 push2=100ms（比 sc_network 2500ms 差 10 倍，实测仅腾讯域调用无旁路，但为隐藏陷阱）→ 清理东财域条目
>   - A4 get_val_report:1861-1866 ascii encode 兜底重打中文可二次抛异常 → 修复
> - **B 级（清理）**：
>   - B1 skills/ 4 个 SKILL.md 孤儿（全仓库零引用）→ 删除
>   - B2 verify_shell_rules.ps1 零引用与 AGENTS.md §4 重复 → 删除
>   - B3 main.py 死代码：L331-332 不可达 gbk 兜底、L362 恒真死条件 → 清理
>   - B4 stock_common/__init__.py:153 死别名导出（list_zhb_archives/zhb_archive_summary）+ `"sc_zhb"` 模块名混入 `__all__` 笔误 → 修正
>   - B5 清理：`.cursor/` 空目录、`cache/gen_rate_limit` 遗留、scratch/INVENTORY.md 过时更新
> - **C 级（记录/低风险修）**：
>   - C1 cninfo 互动易/龙虎榜官方备胎裸请求补节流
>   - C2 `zhb_data` 等 5 分类缓存旁路 → 注释明确化（避免 15+ @cached 误导）
>   - C3 stock_cache:476 f-string SQL → 参数化
>   - C4 AGENTS.md §4.1 引用已删除路径 → 改真实路径
>   - C5 except→pass 容错点补注释（不改逻辑防回归）
> - **不处理（记录）**：get_ful_report.py 保留（测试引用 analyze_stock）；--ful 参数保留友好提示
> - **执行结果（2026-08-05 完成，263/263 回归通过）**：A1 合并 permission ✓ / A2 实测数据链路正确（canonical 万股✓、mcap✓），sc_schema TDX 分支统一 /1e4 防御修正 + data_provider 注释 / A3 移除 push2 条目 ✓ / A4 兜底 ascii 修复 ✓ / B1 删除 skills/ 4 孤儿 + verify_shell_rules.ps1 ✓ / B3 main.py 清理不可达分支与死条件 ✓ / B4 __all__ 移除死别名与模块名条目 ✓ / B5 清理 .cursor/、gen_rate_limit、INVENTORY 更新 ✓ / C1 龙虎榜备胎补节流 ✓ / C2 旁路注释 ✓ / C3 SQL 参数化 ✓ / C4 AGENTS.md §4.1 路径 ✓ / C5 关键容错点注释 ✓
> - **遗留（长期治理）**：except→pass 约 60 处容错点（已注释关键 3 处，其余为有意降级）；eastmoney_stock_info_push2 行业 TTL 1 天窗口；ful 资金流口径未与 sht 同步

> **V16.3 D ZHB 字段复核破解（2026-08-05，docs/ZHB_FIELD_VERIFICATION.md Part 3）**：
> - **Part 2 复核结论**：Mavis 的 Part 2 存在 **16 处错误**（tdxstat [5]/[12]/[13]/[14]/[15]/[16]/[24]/[25]/[34] 与 tdxstat2 [14]/[15] 列定义编造、tdxstat2 [12]/[20] 从 tipinfo 张冠李戴）——**不可作为字典依据**；已追加 Part 3 复核报告逐条标注
> - **🐛 真 bug 修复：zhb_client profile.dat 解析恒空**——记录结构实为 market(1)+code(6)+**null(1)**+name(8)+ts(4)+pad(44)，原 `record[7:15]` 取名称（首字节 null 分隔符）→ 0 条 → **离线名称字典从未生效**（"名称靠腾讯"根因之一）；修复为 `record[8:16]` → 实测 1644 条（000001=深发展A/600006=东风汽车✓）；测试构造记录同步修正
> - **tdxstat2 [11]/[12]/[19]/[20] 复核**：全为**涨跌幅类变体**（11≈5k ±0.5 内 21%、12≈ytd 精确 408/7953、19≈20d 9%、20≈20d/60k）——非 tdxstat 复制，疑基准/复权差异，保持"未破解"；Part 2"配股/配股价"结论作废（配股数据在 tipinfo [12]/[20]）
> - **tipinfo 破解确认**：Col[5]/[6]=除权日/除息日分开记录（同日=分红送转同日）；Col[11]-[14]=配股事件（日期/比例 每10股X股/登记日/登记金额）；Col[15]/[16]=(老)增发日期/金额；Col[19]/[20]=(新)增发日期/价格
> - **Col[33]=主板(10%)连板数 ✅**（143/143 全涨停、20% 板不计数）；Col[31] 下跌日也+1 → 非涨停次数（疑滚动窗口计数，待 30 日历史）；**Col[23]"距下次除权月数"证伪**（0804 当天除权 184 只全部非 0）；Col[22]=私有动态编码 887 值未破解；Col[26]=Col22 组内子分类（弱）
> - field_dict.md tipinfo/tdxstat2 表已同步修正；263/263 回归通过

> **V16.3 E CODE_AUDIT_REPORT 整改（2026-08-06，Mavis 审计 20+ 项用户批准全修）**：
> - **C1**：get_ful_report.py 19 个死 import 清理（AST 精确核实：9 data_provider _async + 12 stock_common + tdx_get_latest_announcements + sys）
> - **H1**：zhb_client 4 处重复 `_f` 嵌套 → 模块级 `_safe_cast(parts, idx, cast)`（41 处调用，消除 31,856 个一次性函数对象）
> - **H2**：get_val_report 3 处 SMA 重复（sma/_sma）→ 模块级 `_sma`（12 处调用）；补 Optional typing import
> - **M1/M5/M11**：data_provider 3 个死函数删除（get_net_profit_kcf/get_field_value 16 分支 if-elif/get_stock_composite_dataclass）+ README 同步
> - **M3/M10**：zhb_client `_cleanup_old_files` 死代码删除（_KEEP_DAYS=36500 恒不删）+ zhb_sync 调用/import 清理
> - **M6**：FulReportRunner 死类删除（V16.1 下线残骸，106 行）；测试同步为 5 大 Runner
> - **M8**：main.py drain_task None 检查（KeyboardInterrupt 理论竞态）
> - **M9**：get_lng_report 24 个死 import 清理（AST 核实）
> - **M12**：main.py 9 个 try/except ImportError → importlib.util.find_spec 批量（52 行→14 行）
> - **L4**：zhb_client get_zhb download 未预期异常降级到缓存路径
> - **跳过（记录）**：L5 显式 pass 35 处（风格级，批量改动风险>收益）；L1/L2/L3 注释类；M7 perf_compare 样板（scripts 工具保留）
> - **验证**：263/263 回归通过（含 test_report_runner 防退化守护同步）

> **V16.3 F tests 目录按架构分层重构（2026-08-06，用户诉求：测试快速定位）**：
> - **问题**：测试文件随版本更迭不断添加（test_v163_features 等补丁式命名），功能分散无法快速定位
> - **新分类（4 层）**：`data/`（数据源：zhb/tdx/eastmoney/network）+ `core/`（统一层：cache/schema/routing/calendar/technical/scoring/utils）+ `reports/`（应用层：runner/strategy）+ `infra/`（基础设施：gd/f10/api_stability）——命名规约 `test_<层>_<主题>.py`，**禁止版本号命名**
> - **迁移**：19 文件 → 17 文件（合并 zhb×2/tdx×2/eastmoney×2、拆分 v163_features 至各层）；删除空文件 test_sc_zhb_backtrack.py、tests/__init__.py
> - **踩坑修复**：① 合并后缺 `import unittest`/`from __future__` 位置/`import time` ② **`norecursedirs` 的 "reports" basename 匹配排除了 tests/reports/**（改为 `./reports` 根级限定）③ 子目录深度变化导致 `parent.parent` 路径失效（改 `parents[N]`）
> - **验证**：**281 passed + 46 deselected = 327 项，与重构前完全一致（无丢失无重复）**

> **V16.3 G CODE_AUDIT_REPORT_R2 处理（2026-08-06，Mavis R2 审计：上轮 8/9 修复验证全通过）**：
> - **M13（MEDIUM）seat_db keywords_map 精简**：50 个 keyword 按**匹配语义**验证（非字符串集合）——44 个被 tiers/aliases 层语义覆盖（任何命中必先走前两层，属死条目）安全删除；保留 6 个真独有（光大佛山/中信杭州延安路/宁波彩虹北路/银河绍兴/中金财富南京/广发上海东方路——券商+营业部全称变体）；新增 `tests/core/test_core_seat.py` 锁定三层识别行为（含已删 keyword 场景回归验证）
> - **M14（LOW）注释修正**：data_provider timedelta import 注释改指实际使用者 `_get_trading_date_offset`
> - **M15（LOW）核实保留**：date 在 type hint/调用仍使用（L274/930/947 等），保留
> - **R2 修复验证 4 项**：list_date 错误回退删除 ✓ / turnover 腾讯兜底 ✓ / _parse_zhb_date 统一解析 ✓ / _get_zhb_date_offset 日历日减法（业务正确，语义微调已记录）
> - **验证**：287/287 回归通过（281 + 新增 seat 6）

> **V16.3 H CODE_AUDIT_REPORT_R3 处理（2026-08-06，Mavis R3：E/F/G 验证全 PASS + 新发现）**：
> - **R3-H1（HIGH）测试假通过修复**：test_strategies_handle_empty_pool 同步调用 async 策略（strategy_01/08）→ coroutine 对象 + isinstance 断言失败被 except 吞 → **假通过**（2 个 coroutine never awaited 警告佐证）；修复：`inspect.iscoroutine` + `asyncio.run` 显式 await + 新增 `test_async_strategies_actually_return_list`（强制 async 策略真正执行）；**警告 11→9 验证修复生效**
> - **M4/M5 死函数删除**：ful `_section`（1 行）、mak `_canonicalize_stock`（38 行，已被 get_canonical_stock_data 取代）
> - **M1-M3/M6 核实保留（R3 误报）**：`_is_realtime/_is_near_realtime/_is_static` 被 test_core_routing 引用、`_market_from_code` 被 test_data_tdx 引用（北交所映射验证）——与 M2 同类"测试专用 API"
> - **L1（conftest monkeypatch 静默）跳过**：warn 已提示，改 fail 影响面未知（LOW）
> - **L2（sc_datasource 6028 行拆分）挂起**：沿用 V16.0 6.5 决策（数据正确性验证优先，重构后置）
> - **验证**：288/288 回归通过（287 + async 策略测试 1）

> **V16.3 I R4 复查处理（2026-08-06）**：
> - **R4-L1 修复**：data_provider.py `import asyncio` 死 import 删除（14 个 async def 全为假 async 显式设计、0 await、0 代码使用；残留仅 docstring 提及）
> - **M1-M3/M6 保留确认（R4 误报澄清）**：4 个函数**均被测试引用**（_is_realtime/_is_near_realtime/_is_static → test_core_routing:134-136；_market_from_code → test_data_tdx:141 北交所映射）——与 M2 同类"测试专用 API"，删除需同步改测试
> - **项目健康度**：0 CRITICAL / 0 HIGH / 0 MEDIUM（R1-R4 四轮闭环）；288/288 通过、9 warnings

> **V16.3 K 实跑报告问题修复（2026-08-06，用户 5 脚本实跑 13 项问题逐项核实）**：
> - **行业名 3 处不一致根因**：data_provider L680"剥离'子'后缀"逻辑（"光学光电子"→"光学光电"）——V16.2.17 统一申万二级后此逻辑错误（官方名带"子"）→ **删除**；sht/med/lng 文件头统一"光学光电子"（canonical L0 东财申万二级；sht 五章"元器件"为 TDX boards 直连属设计内差异，同业对比已用 L2"光学光电子"）
> - **val 显示修复**：_sfmt 表补 21/22（原只到 20→21/22 显示注册名格式不一致）、删已移除的 14、修正 15（头部风向标→流动性王）、汇总"20个策略"改动态、横幅"18 策略"→21（4 处）
> - **sht 游资标记修复**：trader_tags 是分类标签（机构/北向/量化/游资/散户）但显示逻辑全部当"著名游资"→ 仅 [游资] 类显示"著名游资买入/卖出"，机构/北向等归"其他席位分类×N"；龙虎榜"机构专用"多是真实数据（该股席位如此），seat_db 游资识别正常
> - **mak 板块成员失败降级**：TDX board_list 有值但 board_members 全空（2026-08-06 实测）→ C 段集中度/D 段成交额/E 段成分/F 段资金流全空白；新增"成员覆盖率 < 1/3 自动降级 _build_sectors_from_zhb"（129 板块全成员零网络）
> - **mak E 段名称补全**：_zhb_member_stocks 名称兜底加腾讯批量（profile 仅 1644 只，002842 等缺失显示 code(code)）
> - **资金流失败根因（网络状态非 bug）**：push2/push2his 被风控（连 None）→ fallback push2delay 但 fflow daykline 返回 rc=100 无数据 → sht/med"资金流数据获取失败"、mak F"0.00 亿"；20h 冷却自愈；**待办**：新浪个股资金流备用源（fund_flow_backup 实为板块接口不可复用）
> - **3 日偏离 0 待复现**：snapshot 三值有值（603221 复利 33%）但报告显示 0——需下次运行时日志确认（_calc_3d_from_daily 输入差异）
> - **验证**：288/288 回归通过

> **V16.3 L push2 风控治本（2026-08-06，用户关切：换 IP 次日又被 ban）**：
> - **根因链（对比 v9.6）**：
>   1. v9.6 的 `tdx_get_board_list/members/belong_boards` **全走 MAC TCP 零东财**；v15 的 `tdx_get_board_list` 委托**东财 clist**（BK 码）→ `tdx_get_board_members(BK码)` MAC 查不到（MAC 用 880xxx 码体系）→ **fallback push2 clist 每板块 1 次**（mak 100 板块 = 100 次 push2）
>   2. 实测：MAC 板块协议当前完全可用（board_list 56 / members 32 / belong_board ✓）——**BK↔880 码不匹配才是 fallback 触发点**（非 MAC 故障）
>   3. 叠加 V16.2.17 行业统一后 mak 深度依赖东财 → push2 请求量比 v9.6 大 10 倍 → 换 IP 次日即 ban
> - **修复（mak 优先级反转）**：`get_all_sectors` **ZHB 旁路优先**（`_build_sectors_from_zhb` 129 申万二级板块全成员、成交额/主力资金流齐全、零网络零 push2）；TDX board_list 仅当 ZHB 失败时兜底；E 段 code=行业名时不再显示 "(煤炭开采)" 重复
> - **验证**：D 段 TOP10 成交额/主力净流完整（通信设备 2504 亿/+68 亿）、E 段成分/龙头齐全；**mak 板块路径零 push2 请求**；288/288 回归通过
> - **遗留待办**：① 新浪个股资金流备用源（push2 封禁时 sht/med 资金流仍空；fund_flow_backup 实为板块接口需重写）② 3 日偏离 0 需运行加日志复现 ③ `_get_mac_client` 白名单 host 的 MAC 板块协议已实测可用（56 板块）

> **V16.3 M 数据新鲜度分级（2026-08-06，用户 6 点原则固化）**：
> - **用户原则**：① ZHB 成本最低优先 ② ZHB=T-1 ③ 盘前/非交易日 T-1 满足目的 ④ 盘中/盘后需实时 ⑤ 即时字段（价格/涨幅）不接受 T-1，静态字段（股本/股东/分红/北向）T-1 无影响无需缓存 ⑥ 参照系（行业排名）T-1 精度影响≈0 直接用
> - **分级模型（写入 glossary §5.5）**：A 即时（价格/涨幅/成交额/资金流）→ 实时优先 ZHB 兜底 max_delay=1；B 中精度（PE/PB/股息率/连涨/阶段涨幅）→ ZHB 优先 max_delay=3；C 静态（股本/52周/行业/股东/分红/北向）→ **ZHB 无条件**；D 参照系（行业排名/板块聚合）→ ZHB 无条件
> - **"太严格"实证与修复**：get_stock_composite 原 max_delay=1 打包 C 类字段（股本/52周/行业）——周一盘前 ZHB=上周五（延迟>1 天）→ C 类被拒绝走网络（白白请求+可能 push2）→ **拆分级**（C 无条件、B=3、A 兜底=1）；lng 同步拆分（阶段涨幅挂 fresh，估值/52周无条件）
> - **审查结论**：无"A 类用 T-1"突破（canonical A 类有 TDX/腾讯实时覆盖，ZHB 仅兜底；mak A 段腾讯覆盖；val 价格腾讯批量）；mak/val 的 fresh 仅标注用途 ✓；val 资金流 max_delay=3 为防卡死的合理放宽 ✓
> - **验证**：288/288 回归通过

---

> **V16.3 N 字典多源映射 + ZHB 碰撞（2026-08-06）**：
> - field_dict §零"字段多源接口映射"：7 财务字段 + 4 补充字段全部多源（易→难排序），附 AxData 257 接口目录
> - ZHB 碰撞（4 天连续包 0731~0805 + 新浪 000100 实测）：**eps 有（tipinfo）；roe/毛利率/净利率/net_profit/revenue/holder_count ZHB 无**（tdxstat 35 列全破解无财务深度字段，茅台/招行复核确认）——结论写入字典，避免未来重复破解

---

> **V16.3 O canonical 财务字段 TDX 接入（2026-08-06）**：
> - **根因发现**：`_EasyTdxAdapter` 缺 F10C/F10 代理 → `tdx_get_financial_analysis` 自 V12 起静默失败（med 一直走新浪 fallback）
> - **修复**：适配器补 F10C/F10（easy_tdx get_company_info_category/content，0x02CF/0x02D0 TCP）+ NaN start/length 防护；**F10 财务分析实测生效**（000100：10 子栏目全解析）
> - **canonical 接入**（ZHB 碰撞确认无这些字段后）：roe/毛利率/eps → F10（@cached gross_margin_roe，eps 键新增——**升级需 invalidate_category('gross_margin_roe')**）；net_profit/revenue/holder_count → 0x0010（@cached financial）
> - **单位破解**：**0x0010 金额字段单位=角（/10 得元）**（000100：jinglirun 15564526250 角=15.56 亿=F10 一致；zhuyingshouru 4345 亿角=434.5 亿）——每股类字段已是元
> - **交叉验证**：F10 基本每股收益 0.0692 = ZHB tipinfo ✓；F10 扣非净利 11.5485 亿 = ZHB net_profit_kcf 115484.79 万 ✓；0x0010 净利 = F10 净利 ✓（三源同值）
> - **净利率口径**：canonical 自算 net_profit/revenue×100（3.58%），仅当两字段同源 0x0010 时（防混合源单位错）——F10"营业净利率"是营业利润口径（1.43%）差税费，不混用
> - **字典**：field_dict §零 表更新 + 新增 §零·A TDX F10 财务分析字段结构（10 子栏目全字段 + 解析规则）
> - **sc_schema**：net_profit/revenue/roe/eps source_preference ZHB→(TDX, ZHB)（§8.3 契约同步）
> - **测试**：+7（F10C/F10 适配器 6 + eps 契约 1，fake client）；mypy 新增 0 错误；**295/295 全过**
> - **度量**：canonical 财务字段从"roe 恒 None/净利恒 None"→ **000100 全部 7 字段有值**（roe 2.47/毛利率 12.50/净利率 3.58/净利 15.56 亿/营收 434.5 亿/eps 0.0692/股东 61.4 万）

---

> **V16.3 O14 强制直连防护 + 字典破解收尾（2026-08-06）**：
> - **东财封禁事故复盘**：19:12 密集请求（get_em_fund_flow 等）触发真实 IP 封禁（20+ 小时恢复）——
>   项目主通道本就直连（V9.3.2 trust_env=False + _no_proxy），**被封的是真实 IP**（非 VPN IP）；
>   重启光猫换 IP 后 115.211 仍是"脏 IP"（运营商 NAT 共享池污染），113.221 正常——**换 IP 后先 1 次小请求验证**
> - **强制直连补齐**（用户决策：除 GD 上传外全部直连）：补 4 处裸调用遗漏——
>   SZSE/SSE 龙虎榜备胎源（urllib→ProxyHandler({})）+ 巨潮互动易（requests.post→proxies=None）；
>   gd_uploader 的显式代理逻辑保留（GD 专用）；带代理环境变量实测直连生效 ✓
> - **东财接口实测规律（写入字典 12.7）**：push2 主域新 IP 观察期严；**push2delay 可作破解通道**
>   （≤10 字段/请求、间隔 ≥5s）；超长 fields URL 被拒；空 data≠断连（先诊断）
> - **字典破解 13 轮成果**：腾讯 33 位 → **12 确认 + 4 部分定性**；push2 财务/衍生字段 → **13 确认/定性 + 3 误标修正**；
>   新浪 [33] 逐笔串确认；F10 接口修复（适配器 F10C/F10）；未破解项均有多股实测值 + 排除项（field_dict §零 O14 状态）
> - **验证**：295/295 全过；`度量`：东财 HTTP 请求从"每会话数百次（含代理风险）"→ 全部显式直连

---

> **V16.3 O15 东财限流方案 A（2026-08-06，用户决策）**：
> - **背景**：两代限流对比（v9.6 vs 当前）——老版东财全局 1.0-1.3s 串行（em_get 单一入口 + 100-500ms 大抖动 + 进程间文件锁）从未封禁；当前 per-domain 限流（push2 0.4/datacenter 1.0/reportapi 1.0 各自独立）多域名并行叠加 → 东财总速率 3-5 req/s → 触发共享风控（仓库实测 **45000 请求/小时封禁 20+ 小时**；datacenter-web 不同 WAF 不受 push2 封禁影响）
> - **修改**：`_do_request` 东财分支统一调用 `_em_wait_process_interval()`（跨进程原子 1.0-1.3s + 100-300ms 抖动）——per-domain sleep 保留为下限——**东财任何时间窗口总速率 ≤1 req/s**
> - **令牌桶结论**：东财是隐性风控（无明确配额）非配额型 API——令牌桶 burst 特性制造短窗峰值，与风控模型冲突——不用于东财域
> - **验证**：3 次连续请求间隔 2.3-2.5s（全局+per-domain 叠加）全部 200；速率 ≤1500/h vs 阈值 45000/h **余量 30 倍**；network 测试 10/10 通过
> - **代价**：东财请求变慢（~0.5/s）——东财本就最后手段（ZHB/TDX/腾讯优先），实际影响小；若后续实证 datacenter-web WAF 独立，可单独放开提速

---

> **V16.3 O16 参考仓库 releases 对照修复（2026-08-06）**：
> - **核查**：simonlin1212/a-stock-data 全部 16 个 releases（v2.1.0-v3.6.0）逐条对照——24 项中 13 项已采纳、3 项部分、4 项遗漏
> - **本次修复 5 项**：
>   1. **920 号段市场路由**（v3.5.1 同款）：_market_code 补北交所分支（920/8/4/43/83/87→2，此前 920 落深圳）；新浪财报/资金流前缀补 bj（3 处）
>   2. **腾讯僵尸数据检测**（v3.6.0 同款）：43/83/87 老号段 + 成交量 0 + 有价格 → 丢弃（3 路径：get_tencent_quote/_tencent_quote_full_fallback/_tencent_batch_fallback）
>   3. **板块资金流翻页**（v3.5.1 同款）：clist 先取首页拿 total，top_n>200 才翻页（每页 200），total 缺失按末页收敛，提前返空防死循环
>   4. **clean_codes 强化**（v3.6.0 norm_ticker 同款）：7 位数字不再截断（6005190 风险）、显式前缀与号段一致性（sh000001 指数拒绝）、前后缀矛盾拒绝（SH000001.SZ）
>   5. **残留清理**：baidu_kline_full 误导 docstring 修正（纯 TDX）；mak 巨潮 orgId 改动态查询（920 号段可用）
> - **决策记录**：ETF 期权层不实现（用户不关心 ETF）；K 线复权独立排期（中等难度，需逐步验证）
> - **验证**：295/295 全过；clean_codes/_market_code 8 用例手工验证 ✓

---

> **V16.3 O17 统一层格式梳理（2026-08-06）**：
> - **盘点**：canonical 全字段 × 源路径 × 单位——rt_quote 三层（TDX 链/腾讯 [45] 亿 [37] 万/get_em_quote_full fltt=2）单位已统一 ✓；canonical 消费层（mcap 公式/0x0010 角→元/净利率同源守卫）✓
> - **实测确认**（push2delay fltt=2）：f162/f163/f167/f174/f175 **返回浮点**（PE 19.87/PB 6.94/52周 1539.98 元）——**无需 /100**（此前疑为 bug 实为 fltt 差异）
> - **修复 2 个真实 bug**：
>   1. **批量路径 mcap 错 1e8 倍**：ulist f20/f21 实测单位=元（茅台 1635794278989）——`_fetch_batch` 直接赋值未 /1e8——已修（消费方 val 目前只用 name，未来安全）
>   2. **get_gross_margin_and_roe 新浪 fallback 永远失败**：旧结构 `result.data` 列表 vs 实际 `result.data.report_list`（按报告期 dict）——已修（参考仓库 v3.2.1 同款）
> - **记录**：ulist 的 f162/f163/f167 不可靠（返回 '-'/错值）——批量路径 PE/PB 需走单股路径；get_em_quote_full docstring 误导注释已修正
> - **验证**：295/295 全过；fltt=2 实测字段单位对照茅台参照全一致

---

> **V16.3 O18 数据源难易度排序修正 + 脚本源审核（2026-08-06）**：
> - **修正**：此前"易→难"排序（ZHB→TDX→AxData→腾讯→东财→新浪→巨潮）为**想当然**——AxData 未验证排前、新浪/巨潮（参考仓库"其次/低"）排后均错
> - **新排序（依据参考仓库 v3.2 官方优先级 + 实测）**：**ZHB（离线零网络）→ TDX TCP / 腾讯（不封 IP 首选）→ 新浪/巨潮（低风险）→ 同花顺（401 反爬史）→ AxData（local 未验证）→ 东财（最难：45000/h 封禁 20h + 观察期 + 共享风控，仅独有数据）**
> - **同步修正**：field_dict §零 原则 + 11 字段多源表重排（eps/net_profit/52周/list_date/概念/股息率 等源顺序）+ 12.15 优先级矩阵（财务行 F10/0x0010 主源、行业/概念 push2 最后）+ glossary §5.5 核查表（免费副产品规则加限定：仅当行情已走 push2 时零成本）+ gen_field_matrix SOURCE_ORDER（附录重生成）
> - **5+1 脚本源审核结论**：push2 使用全部合规（涨停池/龙虎榜/分红/两融/研报/解禁等独有数据 + 批量行情最后兜底）；val 行业已 TDX 替代、mak 板块已 ZHB 旁路、sht 涨停价已腾讯兜底——**无"非独有数据用东财"违规**
> - **优化 1 项**：lng `get_roe_trend` 新浪自算（第 4 档）→ **F10 财务分析多期加权 ROE/EPS/BPS（TDX 第 2 档）优先，新浪兜底**——实测 000100 4 期有值 ✓
> - **O18b 用户三问落地**：① 统一层理念确认——get_roe_trend 是统一层函数，F10/新浪日期均为 ISO 格式天然归一（无需改），原则固化"脚本层不得直接消费原始多源值" ② fallback 排序难易度已 O18 修正 ✓ ③ **新增"数据获取模式维度"**（用户关键洞察）：逐股多字段（TDX TCP）vs 批量单字段（腾讯批量/东财 ulist）——val/mak 全市场必须批量、sht/lng/med 单股必须 TCP——现状核查两模式均正确匹配，原则写入 12.15 + glossary
> - **验证**：295/295 全过

---

> **V16.3 O19 统一层覆盖修复（2026-08-06，双路审计 P0-P3 全修）**：
> - **P0 数值正确性**：① lng 0x0010 现金流/净利补 /10（角→元——此前偏大 10 倍）② get_roe_trend 下沉 sc_datasource 统一层（F10 加权优先 + 新浪摊薄兜底 + `roe_type` 口径标注）③ val strategy_10 改统一层 F10 加权 ROE（原 0x0010 摊薄口径与报告不可比）④ ful 年化 ROE 自算 → 统一层 F10 加权 ROE（字段改名 roe）
> - **P1 架构**：ful 新浪 lrb/fzb 脚本内嵌解析 → 统一层 get_sina_financial_report/get_sina_balance_sheet（缓存+归一）；**P1-6/7/8 重审修正**：ful 资金流（四档需求）与分红（TDX xdxr）用 tdx_client 封装**更合规**（TDX 比东财易——审计基于旧排序）、val strategy_09 已走统一网络层——均不改
> - **P2**：mak 指数腾讯兜底 2 值 bug → ifzq.gtimg.cn 前复权日 K 序列（ret_3d/10d/20d/60d 恢复）；K 线直调 8 处统一 baidu_kline_full（加 count 参数，跨脚本共享缓存）
> - **P3 统一层内部**：get_history_fund_flow_120d 强制归一（float 万 → dict 元）；get_gross_margin_and_roe 新浪 fallback 补 eps 键；**field_dict 0x0010 单位标注全修正**（旧表"×10000 万元"全错 → 金额=角 /10 得元、股本=股——28 行 + 2 处说明）
> - **验证**：295/295 全过；roe_trend 统一层 2 期 weighted ✓、baidu_kline_full count=120 ✓

---

> **V16.3 O20 字典反推统一层补齐（2026-08-06，用户思路：字典多源→统一层必须体现）**：
> - **方法论**：字典 §零·B 30 个多源字段 = 统一层审计基准——逐字段对照 canonical 接入现状，找"字典多源但统一层单源"缺口
> - **补齐 4 项**：① 腾讯 [67]/[68]/[64]（52周高低/股息率——O 破解源）接入 get_tencent_quote（_TENCENT_FIELD_INDEX 扩展）→ canonical rt_quote 自动生效 ② canonical net_profit/revenue 0x0010 失败时新浪财报兜底（@cached）③ 净利率自算守卫扩展（新浪同源也可自算）④ high_52w 标签修正（realtime 非误导的 push2）
> - **已多源无需改**：list_date（0x0010→push2 f189 ✓）、holder_count（0x0010 ✓ + 巨潮 403 实测不可用/AXD 未验证合理不接）、eps/roe（F10→新浪 ✓）、行业/概念/估值/股本（✓）
> - **性能结论（用户担忧回应）**：fallback 全部"主源优先 + 失败才降级"——实测 canonical 000100 主源（ZHB/0x0010）成功时零额外请求；静态字段 @cached TTL 内零重复——**性能影响≈0**
> - **验证**：腾讯新字段实测与参照全一致（1539.98/1151.01/3.98）；295/295 全过

---

> **V16.3 O21 val/mak 数据新鲜度审计修复（2026-08-06，用户原则：盘前/休市 ZHB 优先、盘中/盘后避免 ZHB、T-1 慢变量除外）**：
> - **审计发现 6 项盘中 T-1 渗入**（explore 双路核实代码）
> - **修复 5 项**：
>   1. **mak E 段成分股 change_pct/price/amount = T-1**（最高影响）——腾讯批量已拉却只用 name → 改 T 日优先覆盖（`is not None` 判定）
>   2. **mak ret_3d = T-1（或 0）**——3 日偏离检测盘中失真 → r0 用腾讯 T 日涨跌幅重算（_calc_3d_from_daily 加 today_change_pct 参数）
>   3. **val 策略20 资金占比时间基准错位**（T-1 资金流 ÷ T 日成交额）→ 分子分母同基准（use_zhb 时分母也用 stat2 T-1 amount，标注"同基准"——资金控盘属慢变量）
>   4. **mak A 段 amount/turnover = T-1**（"今日成交额"实为昨日）→ 腾讯 T 日优先（amount_wan/turnover_pct）；全市场主力净流入标注"ZHB T-1 口径"
>   5. **平盘股 change_pct=0 静默回退 T-1**（val 快照 + mak 板块——`if _real_chg`/`_cp != 0` 条件）→ `is not None` 判定（0 也是今日事实）
> - **记录（用户例外条款——T-1 慢变量不修）**：val 策略 02/05/06 前置过滤的 change_5d/20d/60d/streak_days（区间趋势慢变量，形态确认用实时 K 线）；单股 getter 双门已合规 ✓
> - **验证**：295/295 全过

---

> **V16.3 O22 双路审查修复（2026-08-06，全面回归发现的 7 个新 bug 全修）**：
> - **CRITICAL**：① 深交所备胎源 opener context TypeError（OpenerDirector.open 不接受 context——HTTPSHandler 注入修复，实测 10 条正常）② val 4 处裸名 baidu_kline_full NameError（只导入了 common_baidu_kline_full——改全名，strategy_01/03 恢复）
> - **HIGH**：③ 新浪 fallback 结构（report_list[period] 是 {"data":[...]}——item_map 构建修复 + 缺失返 None 防假 ROE=0.0 被缓存标 tdx:f10——实测 000100 ROE=2.44 ✓）④ _quick_request 双重全局等待（删内层——速率恢复 ≤1 rps）⑤ mak E 段 _tm 未初始化（try 前 {}）⑥ 腾讯批量僵尸检测 float 移入 per-code try（单只坏字段不丢整批）
> - **MEDIUM**：⑦ med ROE 缺失 0.0 伪装（消费端 >0 判定）⑧ get_roe_trend_series 双层 @cached（删外层冗余）⑨ 新浪直连前缀 bj（2 处）⑩ _TENCENT_MIN_FIELDS 53→69（覆盖 64/67/68 索引）⑪ val/sht 死 import 清理
> - **验证**：295/295 全过；dragon_tiger_backup 实测（深交所 10 条/上交所 35KB）；新浪 fallback 实测（真实 ROE）

---

> **说明**: 本 Roadmap 为动态文档，将根据实施进度和实际情况持续更新。
