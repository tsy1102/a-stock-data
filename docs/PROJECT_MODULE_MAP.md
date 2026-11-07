# 核心模块依赖与契约地图

> 本文是截至 2026-10-21 的模块拆分快照，不是运行规则或保证最新的依赖图。使用前须对照当前代码、调用方和测试核实。
## 1. 调用与导入关系

| 模块 | 直接消费者 / 入口 | 重要测试与兼容入口 |
|---|---|---|
| `scripts/collide.py` | CLI；`apply_collision_adjudications.py` | `test_collide.py`、`test_collision_math.py`、`test_axdata_collision_suppression.py`、`test_ftshare_collision_anchor.py`、`test_ftshare_rest.py`、`test_apply_collision_adjudications.py`。测试直接调用 `collide.*`，并 monkeypatch `ROOT`、`REG_PATH`、`SLA.load_source_lineage`、`are_independent_sources`。保留门面符号和 monkeypatch 的可见路径。 |
| `scripts/capture_field_probe.py` 与 `capture_{context,tcp,verified,http}_collectors.py` | 独立 CLI；`build_collectors()` 是单一运行源到 collector 的注册表；入口保留 CLI、日期/覆盖编排、源路由及 composite `market_sources` | `test_capture_field_probe.py` 通过 `spec_from_file_location` 导入入口；`test_capture_catalog.py`、`test_capture_source_coverage.py`、`test_axdata_capture_policy.py`、`test_dependency_adapter_compat.py` 直接调用兼容函数。可替换日期、限流、解析和策略助手由入口包装器显式传入。来源实现模块不导入入口，也不持有网络状态或磁盘写入。 |
| `stock_common/sc_network.py` | `stock_common/__init__.py` 重导出；`core/data_provider.py`、`core/tdx_client.py`、多个 `stock_common/sc_datasource/*` 和 Fuyao/utilities 直接消费传输函数或内部限流入口 | `test_data_network.py`、`test_levistock_rate_limit.py`、`test_capture_field_probe.py`、`test_check_em_health.py`、`test_dependency_adapter_compat.py`、`test_network_isolation.py` 等。很多消费者从模块导入函数对象；单一运行状态必须继续由此模块持有。 |
| `stock_common/sc_datasource/_eastmoney.py` | `stock_common/sc_datasource/__init__.py` 适配层及 `_convertible.py`、`_events.py`、`_financials.py`、`_holders.py`、`_industry.py`、`_macro.py` 等专题模块；保留数据中心同步/异步公开 façade 与 monkeypatch 注入点 | CYQ、龙虎榜、东财资金流、板块成员、缓存单位和报告契约测试。公开 adapter 名称、参数、返回形状及 cache key 必须兼容。 |
| `stock_common/sc_datasource/_datacenter.py` | 仅由 `_eastmoney.py` 的兼容 façade 调用 | 同步/异步数据中心请求参数、响应行筛选和错误降级契约测试；传入现有请求/日志依赖，不导入或持有网络状态、缓存和业务预取状态。 |
| `scripts/apply_collision_adjudications.py`、`collision_adjudication_validation.py`、`collision_adjudication_transformations.py` | 原文件继续负责裁决流程、CLI/参数与原子写入；校验模块负责纯 schema/身份/证据验证；变换模块仅改调用方传入的内存对象 | `test_apply_collision_adjudications.py` 对 registry、lineage、路径边界和报告完整性做临时副本测试；入口保留全部原函数名/签名，唯一正式写入路径仍为 CLI 的 `_atomic_write_batch()`。 |

### 使用限制

- 采集器清单以 `build_collectors()` 当前注册表为准；不在此复制来源数量或完整列表。
- `collide.py`、采集器和裁决入口均保留脚本/包导入兼容；修改时应检查当前消费者和 monkeypatch 测试。
- 来源适配器迁移不得复制网络、缓存、限流、日期或落盘状态；具体所有权以代码为准。
## 2. 状态与副作用所有权

| 状态 / 副作用 | 当前唯一所有者 | 拆分约束 |
|---|---|---|
| HTTP session、域名令牌桶配置、最后请求时刻、计数、熔断与 Eastmoney 封禁态/持久文件 | `stock_common/sc_network.py`；线程/进程文件互斥与时隙算法在 `sc_network_limits.py` | EM、GEN 的同步/异步入口及 Levistock 直连入口使用跨进程 OS 锁；限流状态与 `.mutex` 文件分离，损坏状态 fail closed，进程退出由 OS 释放互斥。新传输模块只能通过现有请求门面；不得各自持有 session、桶、封禁状态或重试循环。 |
| 东财专题业务缓存、预取任务、北向持仓缓存路径、非数据中心端点整形 | `_eastmoney.py` 与 `stock_common/sc_datasource/_shared.py`；通用 TTL cache 在 `core/stock_cache.py` | 缓存 key、TTL、缓存有效性判断、prefetch 生命周期和 `_shared` 状态不能复制或改名。 |
| 数据中心同步/异步请求及响应行筛选 | `_datacenter.py`（无共享状态）；请求限流、重试和熔断仍归 `sc_network.py` | `_eastmoney.py` 传入当前模块级请求/日志依赖，保留现有 monkeypatch 路径；无新 HTTP 客户端、重试、缓存或并发。 |
| 采集日目录、逐源 raw JSON、`meta.json`、采集计划、日期/时段、上下文保留及覆盖 | `capture_field_probe.py`；目录/诊断/字段目录策略在既有 `capture_archive.py`、`capture_diagnostics.py`、`capture_catalog.py` | 来源实现迁移不得负责落盘、重试计划或日期改判；每源 `raw_{source}.json` 与 metadata schema、source-as-of、错误状态、`--only`/`--include-context` 和同日覆盖行为保持原样。 |
| 碰撞 registry / 来源身份 | `collision_registry_context.py` 解析 registry、lineage、锚资格与运行来源身份；`collide.py` façade 持有当前 `_SOURCE_LINEAGE` 并提供稳定调用签名 | 新模块只读且不保存第二份 lineage 状态；`collide.py` 的 `REG_PATH`、lineage loader monkeypatch 和来源身份导出保持兼容。 |
| 碰撞覆盖、triage、报告汇总 | `collision_candidate_triage.py` 读取 ignored coverage cache 并构造 coverage/triage/source-coverage 结果；collision state、research state、review ledger、report serialization 分别由既有专属模块持有 | 覆盖读路径由 façade 显式传入；不写 coverage cache、不保存状态；交易/自然日筛选、来源独立性、verified/contract anchor 资格不在该模块重定义。 |
| registry/lineage 决策副本、派生文档准备与正式替换 | `apply_collision_adjudications.py` 持有裁决流程、路径与原子写入；`collision_adjudication_validation.py` 只验证；`collision_adjudication_transformations.py` 只变换内存对象 | apply 函数仅改调用方提供的内存对象；CLI 在受限目录读取输入，通过 `_atomic_write_batch()` 批量写 registry、lineage 和生成视图。测试只写 pytest 临时副本。 |

## 3. 结项状态

模块拆分阶段 0–6 于 2026-10-21 完成。原阶段日志、历史哈希和样本计数已移除，避免与变更记录重复并被误读为当前基线；后续改动见 `CHANGELOG.md`，模块行为以当前代码和测试为准。
