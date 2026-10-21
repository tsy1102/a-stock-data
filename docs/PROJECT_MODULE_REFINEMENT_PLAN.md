# 大型模块后续拆分计划与执行档案

> 状态：分阶段实施中；每阶段通过验收后继续下一阶段。
> 基线日期：2026-10-21。基线版本：17.6.1（模块拆分前；已完成的 17.6 阶段历史记录见原计划）。
> 范围：核心采集、碰撞、网络与裁决模块。主字典、字段注册表和历史采集证据不属于拆分对象。

## 1. 目的与边界

17.6 已完成一轮架构整理，碰撞报告、候选审阅、采集目录、诊断和归档均有独立模块。核心入口仍然较大，职责和副作用交织；继续按行数切文件会增加跳转成本，也可能复制字段路由、限流状态或裁决规则。本计划要求先以调用关系和数据契约确定边界，再逐个模块族拆分。

本计划不改变字段语义、数据源身份、请求目标/顺序/数量、限流与重试策略、日期资格、碰撞阈值、裁决条件、缓存格式、报告内容或 CLI 行为。没有独立证据时，不改主字典、`field_registry.json`、生成视图和历史 raw。

## 2. 当前结构基线

行数以 2026-10-21 工作区的 `Get-Content | Measure-Object` 结果为准。行数用于定位审查重点，不作为拆分完成指标。

| 模块 | 当前行数 | 已有职责模块/边界 | 后续关注点 |
|---|---:|---|---|
| `scripts/capture_field_probe.py` | 3,925 | `capture_catalog.py`、`capture_diagnostics.py`、`capture_archive.py` | 多来源采集函数、日期/范围编排和运行状态仍集中在入口模块 |
| `scripts/collide.py` | 2,537 | `collision_dates.py`、`collision_snapshots.py`、`collision_math.py`、`collision_state.py`、`collision_candidate_ranking.py`、`collision_reporting.py`、`collision_candidate_reviews.py` 等 | 候选生成、资格/谱系加载与总流程仍交错 |
| `stock_common/sc_network.py` | 1,857 | `sc_network_limits.py`；限流桶、熔断与封禁状态由本模块持有 | 同步/异步传输流程和状态所有权耦合；必须避免复制全局状态 |
| `stock_common/sc_datasource/_eastmoney.py` | 2,022 | 同目录已有报价、持仓等专题适配器 | 东财端点函数仍集中；拆分时必须保持统一请求适配器和风控策略 |
| `scripts/apply_collision_adjudications.py` | 1,449 | 独立裁决 CLI | 输入校验、证据审定、注册表写入与原子保存需按契约拆开 |
| `scripts/collision_reporting.py` | 749 | 已独立 | 仅维护报告序列化；不再按大小继续机械拆分 |
| `scripts/collision_candidate_reviews.py` | 872 | 已独立 | 审阅台账状态、身份和处置流程已有模块边界 |

同一日完成的限流修复已把跨进程等待机制的通用部分留在 `sc_network_limits.py`。此文件继续保持无业务状态的辅助层；不得将令牌桶、域名配置、封禁状态再复制一份到采集器或适配器。

**尚未关闭的限流边界**：GEN 同步/异步等待目前按原设计读取/更新共享 mtime 文件，但没有文件互斥锁；本轮已让文件状态异常 fail closed，尚未证明多个独立进程并发时的总请求间隔。不要把本轮错误路径修复表述成“GEN 已有跨进程串行限流”。阶段 0/4 必须结合并发用例评估是否需要增加互斥锁；若增加，先量化来源请求总量与耗时，再保证单请求仍至少间隔 0.21–0.25 秒且无突发。

## 3. 先决基线与证据

每个代码阶段开始前，先生成并归档以下基线；基线缺项时只补调查，不开始拆分：

1. **导入图**：模块的直接/间接导入者、循环导入风险、脚本以模块或文件方式运行时的导入差异。
2. **调用图**：公开入口、私有调用者、动态注册/反射调用、CLI 子进程入口，以及测试中的 monkeypatch 路径。
3. **状态所有权表**：模块级状态、锁、限流/熔断状态、缓存、文件句柄、时间/随机数、网络 Session、写盘职责。
4. **数据契约**：函数签名和返回结构、错误/空值含义、来源身份键、日期和有效日期口径、文件路径/schema、报告章节和退出码。
5. **固定验证样本**：离线采集夹具、历史碰撞报告/候选摘要、裁决临时注册表、测试用的网络调用计数。保存可比较的摘要，不复制或改写真实历史证据。

基线工具优先使用项目已有测试、维护闸门和离线归档。禁止为了建立基线发送真实请求；如以后某阶段确实需要联网验证，须另行说明请求预算、源族、日期和停止条件。

## 4. 分阶段实施

### 阶段 0：依赖与契约地图

**范围**：五个重点模块及其直接依赖，不改运行代码。

- 输出 3 节所列导入图、调用图、状态所有权表和数据契约清单。
- 按纯逻辑、编排逻辑、外部副作用三类标注函数；记录动态调用与 monkeypatch 的稳定路径。
- 为每个候选提取边界列出“搬迁前后入口、返回结构、异常、缓存/文件副作用和测试夹具”。
- 发现已有文档与运行代码不一致时先核实权威来源，再更新计划档案；不能为了匹配文档改运行语义。

**验收**：上述材料完整；每个拟拆函数都有已知调用者和归属；无循环依赖设计；每阶段可独立回退。

### 阶段 1：碰撞引擎的纯候选逻辑

**范围**：`scripts/collide.py` 中的两两候选生成、时间序列/语义/公式候选与目标区分样本逻辑。已有 `collision_math.py` 和 `collision_candidate_ranking.py` 的职责先核清，不重复造层。

- 将纯输入输出、无 I/O 的候选方法按职责迁出；文件名和 API 由阶段 0 调用图最终确定。
- `collide.py` 保留 `run()`、参数解析、数据流程编排和兼容导入名；外部脚本和测试继续通过现有入口调用。
- 交易日筛选、来源独立性、verified 锚资格、候选审阅状态与 L1/L1-U/L1-C 判定不在搬迁中重写。
- 使用固定历史样本对比候选 ID、方法明细、样本日、证据引用、排序和规范化 JSON/Markdown 摘要。

**验收**：固定样本逐项一致；候选完整性计数、身份校验和人工审阅状态不变；碰撞报告 schema、路径和 CLI 退出码不变；离线碰撞测试全过。

### 阶段 2：碰撞资格、谱系与覆盖编排

**范围**：字段覆盖索引、注册表/来源谱系上下文、来源资格与候选 triage。

- 先拆只读注册表/谱系解析，再拆覆盖索引和 triage；每次只处理一个职责。
- 注册表仍是字段状态权威源；生成视图仍只读；审阅台账与 registry 写入流程互不越权。
- 来源别名、完整 code path、事件记录身份、交易日历及自然日事件窗口均继续由现有权威模块供给。
- 新模块不得自行读取另一份来源映射副本；公共数据由调用方显式传入或从既有 API 读取。

**验收**：对同一历史目录，日期合格样本、排除原因、来源配对和 triage 计数不变；parity、数据访问、字典同步、canonical contract 全通过；不改写注册表或历史文件。

### 阶段 3：采集器来源族拆分

**范围**：`scripts/capture_field_probe.py` 中的 producer 和源级采集实现。

- 保留 CLI、`main()`、采集计划、日期校验、`build_collectors()` 和兼容导入面；具体来源实现按阶段 0 的真实依赖分组。
- 分组候选：市场行情、财务/公司资料、官方交易所与公告、事件/上下文、AxData/FTShare/Levistock 核验源。最终组合以请求适配器、共享状态和测试夹具为准，不为均衡文件行数强拆。
- 每个 collector 继续用当前统一网络适配器；不复制 Session、Cookie、域名状态、重试、限流、封禁和熔断逻辑。
- `raw_{source}.json`、`meta.json`、`source_as_of_dates`、逐源状态、错误标记、源选择、`--include-context` 和增量合并行为必须保持兼容。

**验收**：离线 fixture 下源名与登记身份一一对应；请求计划/HTTP 调用数量与错误停止行为不变；相同 fixture 产生相同 raw/meta 结构；日期、盘前、休市日、重复采集覆盖规则全过；测试中真实网络请求数为 0。

### 阶段 4：网络状态与东财适配器边界

**范围**：`stock_common/sc_network.py` 与 `stock_common/sc_datasource/_eastmoney.py`。

- 保持 `sc_network.py` 为网络状态单一所有者：域名归一化、令牌桶配置、熔断器、封禁态和 Session 不复制到 endpoint 模块。
- 只迁出有明确消费者、稳定契约且能独立测试的端点组或纯诊断逻辑；`sc_datasource` 的公开适配器名称保持兼容。
- Eastmoney 端点仍统一经过 `em_get`、共享 `_quick_request` 或已登记的明确备用通道；严禁因拆分新增裸 HTTP 回退、并发探测或请求重试。
- 同步与异步的限流等待失败必须 fail closed；新增端点组测试需断言等待失败时网络调用为 0，并覆盖 403/429 停止行为。
- 明确验证 GEN 当前无锁 mtime 路径在多进程并发下的实际间隔；若需互斥，单独记录请求速率/耗时预算，不能在重构中悄悄更改。

**验收**：接口、参数、字段路径、返回类型、缓存 key、请求预算及风险族停止规则不变；所有调用方与限流状态唯一归属可静态检查；mock 测试证明异常路径不会越过限流。

### 阶段 5：裁决流程模块化

**范围**：`scripts/apply_collision_adjudications.py`。

- 先独立审计 schema 校验、来源/公式/派生关系裁决、字段注册表变更集合、原子写回和 CLI 交互边界。
- 只把纯 schema/验证和确定性转换拆到模块；唯一的 registry 写入路径与备份/原子替换流程仍清晰可追踪。
- 测试只对 `.tmp/` 临时注册表副本执行；禁止把测试结果写入正式 registry、生成字典或真实证据。
- 每种裁决类型需有输入验证、拒绝路径、幂等和“原文件未变”回归。

**验收**：历史决策样本的接受/拒绝与 patch 逐项一致；正式字典和 registry 哈希不变；原子写回失败时保留原文件；CLI 参数与退出码不变。

### 阶段 6：薄入口、文档与结项档案

**范围**：完成上述拆分后的入口、模块说明、测试索引和本档案。

- 清理只由搬迁产生且已证明无引用的私有死代码；先全仓查 import/字符串/动态注册/测试引用，再删。
- 每个新模块记录职责、调用者、公共契约、状态归属和禁止职责；README 只保留导航，不重复完整规则。
- 更新 `docs/PROJECT_CONTEXT.md`、`scripts/README.md`、相关测试 README 和 CHANGELOG；行数与覆盖指标以实际工具结果更新。
- 记录每阶段实际改动、指标、验收证据、遗留问题和回退点；不能把计划状态写成已完成。

**验收**：链接/命令有效；文档数字与实际结果一致；无孤立兼容层或只转发不增值的模块；完整离线验收通过。

## 5. 通用验收门与停止条件

每一阶段都须按 `AGENTS.md` §8 建立修改前事实，按 §9 验证并量化。阶段验收至少包括：

- `python.exe -m py_compile` 覆盖改动文件；Mypy 和 Black API 对改动文件通过。
- 相关模块回归通过；阶段完成时通过 `scripts/run_offline_checks.ps1`。
- `scripts/verify_data_access.py`、`scripts/verify_sync_check.py`、`scripts/verify_canonical_contract.py` 与 `scripts/registry_parity.py` 全通过。
- 比较固定输入的候选数、样本日、报告章节、raw/meta schema、缓存键、限流调用数和外部请求数；没有适用维度时说明原因。
- 真实网络请求默认 0；历史文件、`.gitignore` 数据、credentials、主字典和 registry 均无非授权写入。
- 改动文件清单与计划一致；新增模块必须消除可说明的耦合或重复，不能仅把代码搬到新文件。

出现任一数据契约差异、限流绕行、请求数量增加、候选/字段状态变化、缓存 key 变化、正式证据被改写、报告必需章节缺失或未定位循环依赖，立即停止当前阶段；只回退当前阶段，不将差异带入后续阶段。

## 6. 执行顺序与阶段档案

顺序：阶段 0 → 1 → 2 → 3 → 4 → 5 → 6。阶段 0 的调查材料须先通过审阅；后续阶段每阶段验收通过再进入下一阶段。拆分完成后再统一升版本、更新文档、全量验收并按当次授权决定提交/推送。

| 阶段 | 状态 | 档案记录 |
|---|---|---|
| 基线登记 | 完成 | 2026-10-21：记录 5 个重点模块与 2 个已拆分模块的行数；本文件建立，不改模块边界。 |
| 0 依赖与契约地图 | 完成 | 2026-10-21：完成静态导入/调用与测试注入点扫描、状态所有权和 API/磁盘契约登记；阶段 3 对照后更正：运行时有 36 个采集器身份（原手工清单误计为 37），并确认 20261020 固定采集/碰撞样本。详细证据见 [`PROJECT_MODULE_MAP.md`](PROJECT_MODULE_MAP.md)。registry 与 lineage SHA256 基线已登记；未修改生产代码或历史证据。 |
| 1 碰撞纯候选逻辑 | 完成 | 2026-10-21：新增 `scripts/collision_candidate_methods.py`；拆出 11 个无 I/O helper/候选函数并由 `collide.py` 重导出。核心候选、公式统计和区分样本原版对照一致；碰撞 50/50、数值层 4/4、完整离线 1,187 passed/1 skipped。详见 [`PROJECT_MODULE_MAP.md`](PROJECT_MODULE_MAP.md) 阶段 1 记录。 |
| 2 碰撞资格与覆盖 | 完成 | 2026-10-21：新增 `collision_registry_context.py` 与 `collision_candidate_triage.py`，迁出只读 registry/lineage、来源身份、字段资格、coverage cache 与 triage/source coverage；原 façade 签名保持兼容。固定样本对照一致；完整离线 1,187 passed/1 skipped，registry/lineage/历史报告哈希未变。详见 [`PROJECT_MODULE_MAP.md`](PROJECT_MODULE_MAP.md) 阶段 2 记录。 |
| 3 采集器来源族 | 完成 | 2026-10-21：35 个来源实现按上下文、ZHB/TDX、本项目核验源、共享 HTTP/Eastmoney 迁入 4 个模块；`market_sources` 复合编排、CLI/计划/日期/覆盖/落盘仍在入口。拆分前后 36 个运行源注册键与 36 个公开入口签名相同。定向采集测试 84+17+4 全过；最终完整离线验收 1,187 passed、1 skipped、52 deselected，28.95 秒。未产生网络请求，registry/lineage/历史报告哈希不变。阶段中发现的 `lite` 参数、Fuyao 导入和可空类型问题均已修复并复验。详见 [`PROJECT_MODULE_MAP.md`](PROJECT_MODULE_MAP.md) 阶段 3 记录。 |
| 4 网络与东财适配器 | 完成 | 2026-10-21：`sc_network.py` 保持网络状态/限流/重试唯一所有权；数据中心 sync/async 端点实现迁至 `_datacenter.py`，`_eastmoney.py` façade、函数签名、注入点、请求参数和缓存状态均保持。新增 2 项离线契约测试；完整离线验收语法 259、Mypy 229、Black 244，`1189 passed/1 skipped/52 deselected`，28.57 秒，所有维护闸门通过。记录见 [`PROJECT_MODULE_MAP.md`](PROJECT_MODULE_MAP.md) 阶段 4。 |
| 5 裁决流程 | 完成 | 2026-10-21：18 个 schema/身份/证据校验迁至 `collision_adjudication_validation.py`，5 个内存变换迁至 `collision_adjudication_transformations.py`；入口保留原 31 个函数名/签名、CLI 和唯一原子写入路径。裁决测试 39/39；完整离线验收 `1189 passed/1 skipped/52 deselected`，语法 261、Mypy 231、Black API 246，28.95 秒。核心资产哈希不变。详见 [`PROJECT_MODULE_MAP.md`](PROJECT_MODULE_MAP.md) 阶段 5。 |
| 6 文档与结项 | 完成 | 2026-10-21：项目上下文、根/子目录 README、CHANGELOG、模块地图与本计划已同步；108 个测试模块（数据层 16）及本轮文档本地链接核对一致，裁决 CLI `--help` 可直接运行。最终 `run_offline_checks.ps1`：语法 261、Mypy 231、Black API 246（0 差异），维护闸门全过，`1189 passed/1 skipped/52 deselected`，28.21 秒。核心资产 SHA256 与基线一致，真实网络请求 0；不再有可证明为死代码且可安全删除的拆分产物，现存 façade 均服务于兼容 API 或测试注入。 |

每次推进时仅追加/更新对应行的日期、提交或工作区变更标识、实际指标、验证命令和决定。不得删除失败实验或用新数字覆盖历史结果；更正时保留原记录与更正理由。

## 7. 关联资料

- 当前总体架构约束：[`ARCHITECTURE_THEORY.md`](ARCHITECTURE_THEORY.md)
- 已完成的 17.6 阶段整改及其历史验收：[`PROJECT_ARCHITECTURE_REFINEMENT_PLAN.md`](PROJECT_ARCHITECTURE_REFINEMENT_PLAN.md)
- 允许偏离及偿还状态：[`DEBT_LEDGER.md`](DEBT_LEDGER.md)
- 采集入口和源路由：[`../scripts/README.md`](../scripts/README.md)
- 日采集与碰撞操作：[`field_verification/DAILY_RUNBOOK.md`](field_verification/DAILY_RUNBOOK.md)
- 阶段 0 调用图、状态与数据契约地图：[`PROJECT_MODULE_MAP.md`](PROJECT_MODULE_MAP.md)
