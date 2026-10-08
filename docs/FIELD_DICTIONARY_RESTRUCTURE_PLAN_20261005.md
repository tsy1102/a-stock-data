# 字段字典、来源谱系与碰撞锚点重整计划

> 状态：全部阶段完成。字段逐项审计、质量闸门、离线全量测试均已通过；两份临时备份已按验收条件删除，永久原文参考保留。
> 范围：字段注册与文档导航、来源仓库/数据谱系登记、碰撞器锚点选择及必要的同步工具。
> 当前工作区已有 `docs/field_verification/collision_state.json`、`pool.json` 和 `20261005/` 采集分析产物改动；这些属于本任务开始前的状态，必须原样保留。

## 目标与设计约定

1. 将字段定义、字段×源矩阵、待破解队列、碰撞规则和来源仓库关系分别放在职责明确的文件中，保留一个明确的主入口。
2. 以 `docs/field_verification/field_registry.json` 为机器真相源；保留兼容的按 token 聚合视图，新增逐源、完整路径的字段记录视图，主字典与队列、矩阵由生成器产生。
3. 已核实字段只在其**完整源内字段路径**匹配时成为锚点。默认破解队列为未验证/候选字段 × 独立来源的已验证锚点；同源不得定案。未验证×未验证保留为显式探索模式，不混入默认结果。
4. 来源谱系与 GitHub 仓库关系只登记有证据的对应关系；上游、fork、客户端库、聚合器与数据提供方分开标注。未知或混合来源明确标记待确认，不靠猜测补齐。
5. 所有旧字典内容在整理期间完整保留；生成物与旧字典逐项核对通过后，才删除临时备份。

## 已确认迁移前基线

| 项目 | 基线 |
|---|---:|
| 主字典 | `docs/field_dict.md`，6,279 行；顶层标题重复、编号回退，最近核实说明停留在 2026-09-01 |
| 注册源 | 28 |
| 注册字段 | 1,831（verified 668、unverified 1,160、candidate 2、disproved 1）|
| 字段映射 | 1,097 |
| 原字典抽取基线 | 1,852 个字段标识 / 2,469 条源字段记录 / 1,097 条映射 |
| Registry 对原文基线差异 | 43 条源字段关系缺失（2 条 push2ex、41 条 market_sources；0 条 registry 多出）；224 条共同记录元数据差异，其中 72 条状态不同（65 verified→unverified、6 unverified→verified、1 candidate→verified）|
| 现有 parity 闸门 | `registry_parity.py` 基线已失败：registry 1831/2426/342 vs 原文 1852/2469/363；字段矩阵 parity 仍通过 |
| 已确认的抽取器限制 | `extract_registry.py` 把 Layer1 记录按裸 token 合并，再用“首次非空”规则附加 status/meaning/unit；无法表达同一 token 的源间差异，也可能把重复叶名的状态套到错误路径 |
| 现有生成标记 | 主字典内 `GEN:field-matrix` 与 `GEN:subdict-index` 两块 |
| 已确认路径折叠风险 | 129 组源别名归一后同叶名冲突；字段路径被 `code_of()` 丢弃 |
| 碰撞器 | 默认 left=未验证，right=全部可用字段；2026-10-05 报告基线 left=714、right=1,053，上限组合约 751,842 |
| 现有碰撞测试 | `tests/test_collide.py` 14 项 |

## 分阶段执行

### 阶段 0：事实冻结与备份

- [x] 确认执行环境为 Windows PowerShell 5.1，并记录任务开始前工作区状态。
- [x] 查明字典、注册表、生成器、同步检查器、分字典生成器、清理工具、碰撞器和测试之间的读写关系。
- [x] 将当前 `docs/field_dict.md` 原样复制至 `docs/backups/field_dict_pre_restructure_20261005.md`。
- [x] 记录备份：636,821 字节、6,279 行（文本行）、SHA-256 `8F59FFFB22852422E506B409923DCB8E8EFE5059B73D1B0570C30DC57711520D`。
- [x] 从原字典生成临时注册表基线并核对字段/映射条目；已发现上述差异，**禁止据此直接覆盖现有 registry**。
- [x] 记录迁移前 `registry_parity.py` 状态：字段 token/源关系 parity 已失败，field_matrix parity 通过。
- [x] 用完整源路径与来源范围核对基线差异：43 条仅在原文出现的关系已补入，旧 registry 的 2,426 条源字段关系均保留；聚合状态与原文冲突不做单边覆盖，逐条保存来源、原值和冲突原因。详细分类见迁移审计报告。

**修改前事实门**

- `scripts/gen_field_dict.py` 从 registry 生成主字典的矩阵与分字典索引；`scripts/gen_field_matrix.py` 默认读 registry，但当前仍将矩阵写回主字典。
- `scripts/extract_registry.py`、`audit_field_completeness.py`、`registry_parity.py`、`archive_field_preflight.py`、`verify_sync_check.py`、`gen_ulist_subdict.py`、`gen_zhb_subdict.py`、`lint_field_names.py`、`lint_field_same_number.py` 会读取主字典或其章节；迁移时逐个改为正确读取新主字典或旧内容参考文档。
- `scripts/collide.py` 是 CLI 与碰撞实现；`scripts/crack_push2_status_codes_20260921.py`、`scripts/crack_ulist_f88_95_20260921.py` 直接导入其中的 `EXCLUDE_DIRS` / `collide_pair`；`tests/test_collide.py` 通过文件路径导入模块。`load_registry_state()` 的返回契约为 `(verified_set, known_mapping_pairs)`；扁平字段 ID 使用 `source.path.to.field`，候选结果和历史状态以这些原始 ID 记录。
- 此次碰撞状态变更不触及行情缓存、缓存 key 或 `report_date` 事件锁；`collision_state.json` 中已有原始字段 ID 和 findings 必须保留，不做破坏性迁移。
- `docs/field_verification/field_registry.json` 字段记录契约为 `source/code/sources/section/canonical/meaning/unit/status_raw/status`；矩阵由 `field_matrix` 与 `mappings` 派生。
- `extract_registry.py --check-baseline` 只验证原生 token 覆盖数，当前可通过，但不验证逐源记录和字段状态；它不能单独作为无遗漏证明。
- 比较口径：原文抽取只用于产生覆盖身份集合和历史属性候选；逐源状态冲突不自动选新旧，也不允许在冲突未解时进入锚点集合。

### 阶段 1：拆分职责并建立新的主入口

- [x] 将备份内容复制为 `docs/field_source_reference.md`，保留所有旧章节、字段表、证据描述和引用；该文件标注为历史/来源细节参考，不再作为字段状态权威。
- [x] 将 `docs/field_dict.md` 重建为短而明确的主入口：状态定义、权威顺序、生成命令、未知字段队列/矩阵/来源图链接和按任务阅读路径。
- [x] 新建生成式 `docs/unknown_fields.md`：完整列出 unverified、candidate、conflict 和 disproved；conflict 可作为进一步核查目标但不能作锚，disproved 不进入默认目标。
- [x] 在 registry 增加逐源 `source_fields` 记录：每条记录以 `(source, full_code_path)` 唯一标识，覆盖原文 2,469 条源字段关系；保留原 `fields` 聚合视图供现有 parity/coverage API 使用。
- [x] 对 43 条 registry 缺失关系补齐逐源记录；对状态与属性差异保存双方证据值，冲突显式待复核，不擅自晋级或降级。
- [x] 将字段×源矩阵从主字典迁至独立生成文件 `docs/field_matrix.md`；保留 registry→生成物单向关系。
- [x] 用 `docs/PROJECT_CONTEXT.md` 与主入口说明各文档权威性，明确规则以 `collision_rules.py`/`COLLISION_RULES.md`、`CRACKING_METHODOLOGY.md` 为准，历史参考文档不能覆盖 registry 状态。
- [x] 保持 ZHB、ulist239 等分字典生成仍能从历史来源参考文档取得原始字段章节。

### 阶段 2：来源谱系与仓库映射

- [x] 新建结构化 `docs/field_verification/source_lineage.json`，覆盖注册表全部 28 个源，记录规范源别名、提供方/底层数据家族、独立性状态、仓库关系、证据文件及未确认项。
- [x] 新建由结构化谱系生成或与其逐项校验的 `docs/source_repository_map.md`，区分直接数据提供方、客户端实现、官方 SDK、fork/镜像、聚合器与纯协议参考仓库。
- [x] 只把本地文档/实现能证明的关系标为 confirmed；缺证据项标 `unconfirmed`，保留后续通过对话确认的入口。
- [x] 碰撞器以谱系中确认的 evidence family 判断独立性；混合/无法确认具体底层数据的源不得作为独立锚。报告显示被跳过来源和配对原因。

### 阶段 3：碰撞器锚点与字段身份

- [x] 将 registry 状态键从 `(source, 最末字段名)` 改为 `(规范源, 完整字段路径)`；映射状态同样保留完整字段路径。
- [x] `load_registry_state()` 读取逐源记录而非依赖聚合记录中的单一 `source` 字段；完整路径按第一个源分隔符之后的全部路径匹配。
- [x] 加入路径回归覆盖：TDX 顶层字段 vs `quote_full.*`、ZHB 原始字段 vs `stat.*`/`stat2.*`/`tipinfo.*`，不得交叉继承 verified 状态。
- [x] 默认 right 仅取具有 verified 状态、精确路径且来源谱系可用的锚点；verified 字段不再进入 left。unverified/candidate 和 conflict 记录可作为核查目标，conflict 始终不得作锚；disproved 不进入默认目标。
- [x] 增加显式探索模式允许未验证字段互撞；探索结果不冒充独立来源 L1 定案，报告标注运行模式、锚点数、未知对撞数、源独立性跳过数。
- [x] 维持交易日窗口、日期去重、样本质量、L1 门槛和报告/state 既有契约；本次未更改日期模型。

### 阶段 4：同步工具和文档治理

- [x] 更新生成器、提取器、parity、完整度审计、同步检查、归档预检、ZHB/ulist 子字典生成器和字段名 lint 的文档路径/marker 契约。
- [x] `extract_registry.py` 要求显式输出路径，并保护历史参考、备份及当前真相文件免遭误覆盖。
- [x] 更新 README、CHANGELOG、项目上下文及活跃维护说明；移除与新流程冲突的维护口径。
- [x] 最终验收后清理本轮临时检查脚本；保留仍有明确调用/维护职责的工具。

### 阶段 5：全量核对与回归

- [x] 备份文件与 `field_source_reference.md` SHA-256、字节数一致；注册表字段与映射集合已从原始文档逐项对照。
- [x] 新主字典、unknown 队列、字段矩阵由当前 registry 生成且 `--check` 无差异；2,469 条逐源身份唯一，旧 registry 的 2,426 条源关系零遗漏，新增原文关系 43 条。
- [x] 核对状态数量与冲突台账；旧聚合状态/属性对 2,426 条关系逐条原样保存在 `registry_aggregate`，91 条源状态冲突保持 conflict 且不作锚；无证据项不补造定义。
- [x] 28 个注册源均出现在来源映射；confirmed 仓库关系具有本地证据路径，其余显式 unconfirmed；运行时别名校验通过。
- [x] 完成生成器 `--check`、parity、来源同步/归档预检、编译、类型、格式和离线完整测试；676 passed、1 skipped、47 deselected，25 个 Python 文件编译/Black 通过，18 个源码文件 mypy 零错误；A1/A7 均 0 HARD FAIL / 0 WARN。历史字段完整度遗留见迁移审计报告。
- [x] 对原 2026-10-05 报告同一 32 个交易日窗口做只读碰撞对比；旧报告与新计算日期集相同，没有写回报告或 `collision_state.json`。
- [x] 最终回归及逐项审计报告完成后，删除两份字典/注册表临时备份；`field_source_reference.md` 继续保留且 SHA-256 不变。

## 验收目标与度量

- 字段身份遗漏：0（旧 registry 关系 2,426/2,426；43 条原文关系补入）；字段重复身份：0。
- 状态计数不要求跨粒度相等；要求旧状态证据逐条保留、冲突显式化且冲突不得作锚。
- 同一历史窗口默认组合上界：751,842 → 271,502；同一字段类型/数值区间/来源独立性过滤后实际评估 80,254 对。
- 已 verified 精确路径不进入 left；每条 confirmed L1 均具有独立来源谱系和可追溯样本日期。
- 原始历史内容：主字典备份与 `field_source_reference.md` 在备份清理前逐字节一致。
