# 核心模块依赖与契约地图

> 阶段 0 基线与逐阶段更新档案。静态扫描日期：2026-10-21。本文记录入口、依赖、状态、契约和已验收的拆分边界；不定义新运行规则。后续拆分过程在 `PROJECT_MODULE_REFINEMENT_PLAN.md` 中逐阶段记录。

## 1. 调用与导入关系

| 模块 | 直接消费者 / 入口 | 重要测试与兼容入口 |
|---|---|---|
| `scripts/collide.py` | CLI；`apply_collision_adjudications.py`；历史研究脚本 `crack_push2_status_codes_20260921.py`、`crack_ulist_f88_95_20260921.py` | `test_collide.py`、`test_collision_math.py`、`test_axdata_collision_suppression.py`、`test_ftshare_collision_anchor.py`、`test_ftshare_rest.py`、`test_apply_collision_adjudications.py`。测试直接调用 `collide.*`，并 monkeypatch `ROOT`、`REG_PATH`、`SLA.load_source_lineage`、`are_independent_sources`。保留门面符号和 monkeypatch 的可见路径。 |
| `scripts/capture_field_probe.py` 与 `capture_{context,tcp,verified,http}_collectors.py` | 独立 CLI；`build_collectors()` 是单一运行源到 collector 的注册表；入口保留 CLI、日期/覆盖编排、源路由及 composite `market_sources` | `test_capture_field_probe.py` 通过 `spec_from_file_location` 导入入口；`test_capture_catalog.py`、`test_capture_source_coverage.py`、`test_axdata_capture_policy.py`、`test_dependency_adapter_compat.py` 直接调用兼容函数。可替换日期、限流、解析和策略助手由入口包装器显式传入。来源实现模块不导入入口，也不持有网络状态或磁盘写入。 |
| `stock_common/sc_network.py` | `stock_common/__init__.py` 重导出；`core/data_provider.py`、`core/tdx_client.py`、多个 `stock_common/sc_datasource/*` 和 Fuyao/utilities 直接消费传输函数或内部限流入口 | `test_data_network.py`、`test_levistock_rate_limit.py`、`test_capture_field_probe.py`、`test_check_em_health.py`、`test_dependency_adapter_compat.py`、`test_network_isolation.py` 等。很多消费者从模块导入函数对象；单一运行状态必须继续由此模块持有。 |
| `stock_common/sc_datasource/_eastmoney.py` | `stock_common/sc_datasource/__init__.py` 适配层及 `_convertible.py`、`_events.py`、`_financials.py`、`_holders.py`、`_industry.py`、`_macro.py` 等专题模块；保留数据中心同步/异步公开 façade 与 monkeypatch 注入点 | CYQ、龙虎榜、东财资金流、板块成员、缓存单位和报告契约测试。公开 adapter 名称、参数、返回形状及 cache key 必须兼容。 |
| `stock_common/sc_datasource/_datacenter.py` | 仅由 `_eastmoney.py` 的兼容 façade 调用 | 同步/异步数据中心请求参数、响应行筛选和错误降级契约测试；传入现有请求/日志依赖，不导入或持有网络状态、缓存和业务预取状态。 |
| `scripts/apply_collision_adjudications.py`、`collision_adjudication_validation.py`、`collision_adjudication_transformations.py` | 原文件继续负责裁决流程、CLI/参数与原子写入；校验模块负责纯 schema/身份/证据验证；变换模块仅改调用方传入的内存对象 | `test_apply_collision_adjudications.py` 对 registry、lineage、路径边界和报告完整性做临时副本测试；入口保留全部原函数名/签名，唯一正式写入路径仍为 CLI 的 `_atomic_write_batch()`。 |

### 已知动态边界

- `collide.py` 和采集器都可直接作为脚本运行；包导入和文件路径导入均有使用，提取模块不能依赖仅在 CLI 执行时插入的相对路径。
- `build_collectors()` 当前注册 **36 个**运行源：`zhb`、`tdx`、`eltdx`、`tencent`、`push2`、`sina`、`sina_extended`、`axdata`、`market_sources`、`kpl`、`kph`、`tdx_f10`、`fuyao`、`em_kline_f61`、`em_fund_flow`、`ulist239`、`push2ex`、`em_hot`、`cls`、`datacenter`、`tdx_f10_more`、`cninfo`、`reports`、`ftshare`、`ftshare_rest`、`baidu`、`clist`、`slist`、`exchange`、`event_dc`、`macro_dc`、`research_sina`、`etf`、`news_wscn_cctv`、`sse_e_interaction`、`st_list`。阶段 0 原记录将 36 项误计为 37；阶段 3 通过入口前后路由键和字段覆盖回归核实后更正，未发现缺少运行源。
- `collide.py` 在导入时尝试读取来源谱系到 `_SOURCE_LINEAGE`，失败时使用空映射；任何新候选模块不能反向导入 `collide.py`，否则会形成循环导入并破坏脚本入口。
- Eastmoney 专题模块仍有消费者直接导入 `_eastmoney.py` 的函数。迁出实现时应让 façade 只重导出稳定函数；被测私有依赖的 monkeypatch 路径需逐项迁移并测试，不能靠复制函数或共享状态来“兼容”。

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

## 3. 拆分候选职责与边界

| 计划阶段 | 候选职责 | 必须留在原门面的内容 | 已识别耦合 / 风险 |
|---|---|---|---|
| 1 | 时间/语义/公式候选、区分样本等确定性候选计算，已迁至 `scripts/collision_candidate_methods.py` | `collide.py` 继续导出旧常量和 helper 名；`run()`、CLI、L1/L1-U/L1-C 判断及来源独立性仍留在原门面 | 新模块只依赖 `collision_rules` 与 `collision_math`，没有 registry、文件、网络、缓存或报告 I/O；不得重造排序或数值层。 |
| 2 | registry/source lineage 只读解析、coverage index、candidate triage、source coverage 汇总；已分别迁至 `collision_registry_context.py` 和 `collision_candidate_triage.py` | `collide.py` 保持 API façade 与执行编排；日期资格、写状态与完整报告序列化由原专属模块持有 | registry 仍是字段状态权威；身份状态按调用方传入，模块无第二份 lineage 状态或 registry 副本。 |
| 3 | 已迁至 `capture_context_collectors.py`、`capture_tcp_collectors.py`、`capture_verified_collectors.py`、`capture_http_collectors.py` 的来源族 producer | CLI、`main()`、日期/覆盖编排、`build_collectors()`、复合 `market_sources` 编排、磁盘写入 | 日期、来源资格、解析和限流诊断等原入口可替换依赖通过薄包装器/冻结依赖记录传入；网络 Session、限流/重试和 raw/meta 写入仍由原所有者管理。 |
| 4 | 东财数据中心同步/异步请求与行响应筛选，已迁至 `stock_common/sc_datasource/_datacenter.py` | `sc_network.py` 的网络状态所有权；`_eastmoney.py` 的兼容函数、专题缓存/预取和数据整形 | façade 通过参数注入原有 `_quick_request`、异步重试器和日志对象，故 `_eastmoney` 原 monkeypatch 入口保留；请求参数、过滤规则、空值降级与行结构不变。 |
| 5 | 已迁至 `collision_adjudication_validation.py` 的 schema/身份/报告证据校验，以及 `collision_adjudication_transformations.py` 的确定性内存变换 | `apply_collision_adjudications.py` 保留三类裁决编排、CLI、唯一路径和原子回滚 | façade 导入并重导出原 31 个函数名/签名；输入拒绝、幂等、临时副本 CLI 与原子写失败测试保留。两个新模块均不读写官方文件。 |

## 4. 固定离线样本与可观察契约

用于代码拆分对照的已存在离线样本（读取，不修改）：

- 采集：`docs/field_verification/20261020/`，含 32 份 `raw_*.json`、`meta.json` 与验证状态文件。`raw_*.json` 的源名应与 `build_collectors()` 身份一致；采集测试将精确断言计划、请求调用次数、raw/meta key 和日期/错误状态。
- 碰撞：`docs/field_verification/20261020/20261020_collision_report.json`，报告 schema v4，20,452,490 bytes；`target_count=361`、`right_field_count=304`、`L1=20`、`L1-C=0`、`L4=109`、`method_candidate_count=5,673`、`method_candidate_frontier=190`、`formula_candidates=3`、`candidate_triage.targets=361`、完整性 `status=complete`。这是历史证据，不在拆分时重生成或覆盖。
- registry / lineage 拆分安全检查基线 SHA256：`field_registry.json`=`8cb1fb9842f6d7f715a4d1965810b7bd0b15bbe110262043bf987afddf7a2116`；`source_lineage.json`=`fe4c778266604de73c79e169be707c1e065d7c7c27f22b776744e1460bf433bf`。各代码文件原始哈希已在阶段 0 `.tmp` 探针输出中登记；正式核心资产的哈希须在每阶段前后重核。
- 网络：基线只使用 monkeypatch 的离线测试，预期请求数为 0；关注同步/异步限流失败前的 HTTP 调用计数、403/429 熔断行为以及共享状态引用身份。
- 裁决：`tests/test_apply_collision_adjudications.py` 使用临时 registry/lineage/report；覆盖输入拒绝、路径越界、重复 decision、派生关系、投影、原子批量写失败与回滚。拆分前后正式 registry/lineage hash 必须不变。

### 阶段 1 已验收记录（2026-10-21）

- 从 `collide.py` 拆出 11 个纯 helper / 候选函数及相关阈值常量；原入口重导出原名称，旧调用路径不变。`collide.py` 由 2,537 行降至 2,134 行，新模块 497 行。
- 原版（阶段开始时保存在 `.tmp/collide.py.phase1.backup`）与新门面对照：导出常量、公式候选及统计、区分样本结果相同；确定性样本公式候选 1 项、tested 5，区分样本仍选择 `600000`，`normalized_prediction_spread=1.825669`。
- 直接测试：`test_collide.py` 50/50，`test_collision_math.py` 4/4；完整离线维护套件：语法 251 文件、Mypy 221 文件、Black API 236 文件、维护闸门全通过，`1187 passed, 1 skipped, 52 deselected`，27.74 秒。`black.exe --check` 在 30 秒无输出后停止；验收改用仓库的 Black API 检查并通过。
- registry SHA256 仍为 `8cb1fb9842f6d7f715a4d1965810b7bd0b15bbe110262043bf987afddf7a2116`；lineage SHA256 仍为 `fe4c778266604de73c79e169be707c1e065d7c7c27f22b776744e1460bf433bf`；历史报告 SHA256 仍为 `a347e3e3154d4cc79c5a16cd28bfaf633153d18419c25f2ceb128c8e04c5f222`。网络请求 0，采集/缓存/正式证据无写入。

### 阶段 2 已验收记录（2026-10-21）

- 新增 `collision_registry_context.py`（447 行）和 `collision_candidate_triage.py`（437 行）；将 `collide.py` 从阶段 1 的 2,134 行降至 1,442 行。旧函数签名、返回结构、registry path 与 lineage 状态 setter 均由 façade 保留。
- 迁出的职责：registry/lineage 只读 context、来源身份和独立性查询、verified/disproved 目标资格、覆盖缓存读取和目标映射、候选 triage、来源覆盖汇总。coverage cache 只读 `.tmp/field_evidence_coverage`，未写入；日期资格及碰撞阈值仍在既有规则处。
- 原版与新版本确定性对照通过：来源别名、独立性、目标集合、来源覆盖报告一致（3 个源：ftshare_rest、fuyao、tdx）。定向测试 `test_collide.py` 50/50、FTShare 12/12、adjudication 39/39；最终全离线维护验收：语法 253 文件、Mypy 223 文件、Black API 238 文件、A1/sync/canonical/parity 全通过；`1187 passed, 1 skipped, 52 deselected`，28.10 秒。
- registry、lineage、20261020 历史碰撞报告哈希与阶段 1 完全一致。网络请求 0；registry、历史 raw/meta、缓存和正式报告未写入。

### 阶段 3 已验收记录（2026-10-21）

- 将 35 个来源实现按依赖族迁入 4 个模块：上下文/公告事件 253 行、ZHB/TDX 本地适配器 393 行、AxData/Fuyao/FTShare/KPL/KPH 核验源 490 行、共享 HTTP/Eastmoney producer 1,068 行。入口保留复合 `market_sources`、CLI、采集计划、日期与覆盖编排、`build_collectors()` 和所有原函数签名；入口由 3,925 行降至 2,040 行。4 个 producer 模块合计 2,204 行，拆分增加 319 行（依赖记录与兼容边界）；此处优先降低入口耦合，不以总行数减少作为验收目标。
- 对照拆分前快照，36 个运行源的注册键完全相同；36 个 `collect_*` 公开入口的 `inspect.signature` 完全相同。未更改请求适配器、请求数/顺序、熔断/限流状态、日期资格、源身份、缓存、raw/meta schema 或写入路径。`test_capture_field_probe.py` 84/84、`test_capture_source_coverage.py` 17/17、`test_axdata_capture_policy.py` 4/4 均通过；完整离线维护验收：语法 257 文件、Mypy 227 文件、Black API 242 文件、维护闸门全通过，`1187 passed, 1 skipped, 52 deselected`，28.95 秒；真实网络请求 0。
- 验收中曾捕获并修复三个迁移问题：入口漏保留 ELTDX `lite` 参数、Fuyao 实现遗漏 `datetime` 导入、ZHB 名称解析器的可空类型声明不准确。修复后重跑相应测试及最终全离线套件通过。首次格式检查报告 5 个改动文件需 Black 格式化，按仓库 Black API 格式化后复验 0 差异。
- registry SHA256 仍为 `8cb1fb9842f6d7f715a4d1965810b7bd0b15bbe110262043bf987afddf7a2116`；lineage SHA256 仍为 `fe4c778266604de73c79e169be707c1e065d7c7c27f22b776744e1460bf433bf`；历史碰撞报告 SHA256 仍为 `a347e3e3154d4cc79c5a16cd28bfaf633153d18419c25f2ceb128c8e04c5f222`。采集目录与正式证据无写入。

### 阶段 4 已验收记录（2026-10-21）

- `sc_network.py` 保持唯一的 HTTP/异步请求、限流、重试和熔断状态所有者；仅把东财数据中心同步/异步端点的参数组装、响应行筛选与错误降级迁至 `_datacenter.py`。`_eastmoney.py` 保留原公开函数与精确签名，并将模块级请求函数、URL、UA 和日志器传入实现，保持既有 monkeypatch 注入路径。预取 Future、业务缓存、TTL、key、其他专题端点均未迁移或改动。
- 当前 `_eastmoney.py` 为 1,972 行（HEAD 基线 2,028 行），新 `_datacenter.py` 为 130 行；拆分使适配器入口减少 56 行，合计代码增加 74 行，用于显式依赖注入和单独边界。同步/异步请求均只走原请求函数一次；请求参数、15 秒 timeout、过滤规则（包括空 code 市场报表）、返回 `list[dict]` 和错误回退保持原样。
- 新增离线契约测试 2 项，覆盖同步分页与空过滤、异步重试器委托及两者行筛选；定向回归 `test_lockup_units.py` 4/4、`test_lhb_trading_day_window.py` 2/2、`test_sina_raw_adapters.py` 5/5、`test_degradation_contract.py` 8/8 通过。`test_data_eastmoney.py` 的 27 项都因真实网络/源健康探测标记而跳过，未发出网络请求。
- 初版 async pytest 用例需要创建 Windows asyncio 事件循环，在测试执行体前卡于 loop/socketpair 初始化；已停止该进程，测试改为用立即完成的 fake coroutine 无 I/O 直驱，不改变生产实现。完整离线维护验收通过：语法 259 文件、Mypy 229 文件、Black API 244 文件、所有数据访问/字典同步/Canonical/registry parity 闸门通过；`1189 passed, 1 skipped, 52 deselected`，28.57 秒。真实网络请求 0。
- registry、lineage 与 20261020 历史碰撞报告 SHA256 分别仍为 `8cb1fb9842f6d7f715a4d1965810b7bd0b15bbe110262043bf987afddf7a2116`、`fe4c778266604de73c79e169be707c1e065d7c7c27f22b776744e1460bf433bf`、`a347e3e3154d4cc79c5a16cd28bfaf633153d18419c25f2ceb128c8e04c5f222`。

### 阶段 5 已验收记录（2026-10-21）

- 将 18 个纯 schema、来源身份、元数据与碰撞报告完整性验证函数迁入 `scripts/collision_adjudication_validation.py`（394 行）；将 5 个 mapping/evidence/aggregate/derived-relation 内存变换迁入 `scripts/collision_adjudication_transformations.py`（210 行）。`apply_collision_adjudications.py` 从阶段基线 1,449 行降至 905 行，保留三类裁决工作流、decision/report/registry 路径、CLI 与唯一 `_atomic_write_batch()`。
- 原入口仍提供原 31 个函数名和参数签名，既有测试直接导入 `_runtime_identity` 等私有 helper 也继续有效。新增导入用 `scripts.*` 包路径明确解析，并给直接脚本模式补入仓库根路径；入口仍可从包导入和脚本方式使用。`tests/test_apply_collision_adjudications.py` 39/39 通过，覆盖决策拒绝、幂等、derived/source-contract 验证与只对临时路径执行 CLI。
- 完整离线维护验收：语法 261 文件、Mypy 231 文件、Black API 246 文件、AxData 摘要/A1/字典同步/Canonical/registry parity 全通过；`1189 passed, 1 skipped, 52 deselected`，28.95 秒；网络请求 0。验收中首次 Mypy 提示 `_require_object` 导入被降为 `Any`，已将辅助模块改用解析明确的包导入，复验通过；首次 Black 发现 3 个新/改动文件需要格式化，使用 Black API 格式化后复验 0 差异。
- registry、lineage 与 20261020 历史碰撞报告 SHA256 与阶段 0 基线一致；没有正式字典、registry、lineage、采集数据或历史报告写入。

### 阶段 6 已验收记录（2026-10-21）

- 项目上下文、根目录/子目录 README、CHANGELOG、模块地图和拆分计划已同步；文档列出的测试模块为 108 个、`tests/data` 为 16 个，抽查的本地 Markdown 链接全部有效。版本为 `17.6.2`。
- `scripts/apply_collision_adjudications.py --help` 通过直接脚本入口冒烟；原 31 个裁决函数签名在阶段 5 已由独立探针核实，阶段 6 未改变代码契约。新模块均已登记调用者和职责，没有无消费者的拆分产物；兼容 façade 保留是为了维持既有调用与 monkeypatch 注入路径。
- 最终 `scripts/run_offline_checks.ps1` 完整通过：语法 261 文件、Mypy 231 文件、Black API 246 文件且 0 格式差异；AxData 摘要、数据访问、字典同步、Canonical contract、registry parity 和其他维护闸门全通过；测试 `1189 passed, 1 skipped, 52 deselected`，28.21 秒。真实网络请求为 0。
- `field_registry.json`、`source_lineage.json` 与 `20261020_collision_report.json` 的 SHA256 与阶段 0 基线一致；未改写字段字典、registry、lineage、历史采集数据或正式碰撞证据。阶段产物仍为工作区改动，本次未提交或推送。

## 5. 阶段 0 判定

阶段 0 的依赖图显示：可先迁出无 I/O 的候选计算；只读 registry/谱系和覆盖逻辑次之；采集 producer 必须先解决测试注入与兼容 façade；网络/Eastmoney 只迁出有明确稳定消费者的边界；裁决模块先抽纯校验/转换，原子写路径最后保持单一。任何提取模块不得导入其原 façade。日期、字段来源、请求顺序/数量、限流/重试、缓存、报告 schema、裁决条件都不是本轮拆分自由度。
