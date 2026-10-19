# 碰撞候选人工定案与注册表同步

`collide.py` 只发现候选，不直接改变主字典。只有经过人工核对的决定，才能通过此流程写入逐源字段注册表。数值命中本身不是语义定案。

## 探索模式结果如何继承

`collide.py --exploratory` 会把报告中的 L1、L4 和方法候选按无序字段对登记到 `collision_research_state.json.gz`，并以 gzip 台账保留每次观察的完整 sections 证据、数据日和报告路径；仅从磁盘副本移除可由最新 observation 重建的重复 latest_evidence。后续碰撞报告会为再次出现的字段对附上 `research_history`，同时汇总累计候选数、历史复现数和本次新发现数。

同一数据日、报告路径、窗口和上下文范围的重跑视为同一次观察，会替换该次候选记录而不重复累计；不同上下文范围会使用独立报告目录并形成新的观察。该台账是探索研究记录，不会自动提升字段状态，也不会让 L4 或方法候选进入主字典。只有符合下方正式流程、人工确认语义并显式应用的决定才会更新注册表。

## 可以进入此流程的候选

- 报告必须是 `collision_mode: verified_anchor_only`，且 `exploratory_pair_count` 为 0。
- 仅接受报告 `actionable_L1` 中的 `L1` 或 `L1-U` 新候选；旧版报告没有该键时才回退读取 `L1`。已登记映射的当前窗口复验另列于 `mapped_pair_revalidations`，不是新候选；L4、方法候选和未知字段互撞结果不能直接晋级。
- `target` 与 `anchor` 必须各自精确对应报告中的一个端点，允许它们与报告 `left` / `right` 的顺序相反；运行时别名必须能唯一解析到注册表中的完整路径。若运行时别名映射到多个字典来源，决策文件必须明确指出正确的来源名。
- `action: verify` 只接受状态为 `unverified` 或 `candidate` 的目标字段，并将其升级为 `verified`。
- 当 `verify` 所选锚字段缺少规范名、含义或单位时，必须同时提供 `external_evidence` HTTPS 链接；碰撞证据只用于交叉确认数值对应，独立文档才用于确定字段语义。外部链接会写入定案记录和逐源 `reference_evidence`。
- `action: enrich_metadata` 用于主字典中已验证、但规范名/含义/单位有缺口的字段。决策必须提供 `previous` 元数据快照；当前值必须与该快照完全相同，且工具只允许补缺或替换占位规范名，不会覆盖已存在的有效语义。
- `action: link_verified` 用于两个已验证且元数据完整的字段。它只写入 `same_number_same_meaning` 映射和审计证据，不改动任一字段的状态或元数据。
- 可选 `anchor_metadata_correction` 用于证据确认锚字段的现有元数据有误时。必须提交精确的 `previous` / `updated` 快照、理由及 HTTPS 上游证据；工具会同时保留锚字段的旧值、新值与修正记录。
- `conflict` 与 `disproved` 字段不能由这条流程覆盖；`verify` 也不能覆盖完整的 `verified` 字段。已验证字段只能按上述受限的 `enrich_metadata` 或 `link_verified` 操作处理。

## 单源上游契约核验（不要求跨源数值碰撞）

有些字段只由一个来源提供，或没有独立来源可作锚。若上游的正式接口/协议定义能解释该来源字段，可走单源契约核验；这条路径与 L1 数值碰撞并列，但结论范围不同：

- 上游契约可以确认一个精确 `(source, 完整 code path)` 的规范名、含义和已知单位；它**不证明**另一个来源的字段等价，也不创建 `mappings`。
- 必须核实项目中的运行字段如何映射到上游接口响应字段。仓库 README、相似字段名、变量名或通用注释本身不足以证明映射；客户端/聚合框架的文档也不能直接代表底层数据提供方契约。
- 决策文件需记录权威提供方与接口/协议、固定提交/版本或有日期的文档版本、上游路径、精确定位、HTTPS 链接、核验理由，以及目标当前的 `status`、`status_resolution` 和元数据快照。
- 常规核验接受 `unverified` / `candidate`。`conflict` 只有在以下条件全部成立时才可由上游契约解除：`status_resolution` 为 `status_conflict`；逐源参考状态只有 `verified`；`registry_aggregate_status` 为 `unverified`；状态证据值只有 `verified` 与 `unverified`；`attribute_conflicts` 为空；非空 `reference_evidence.status` 全为 `verified`。这只修复聚合视图导致的状态差异，不覆盖真实含义冲突；`disproved` 仍不能走此路径。
- 已有有效元数据默认不能覆盖。确需纠正时，决策必须附 `metadata_correction`，精确重复 `previous` / `updated` 三项快照并写明理由；快照须与决策的字段值完全一致。核验通过后，逐源记录改为 `verified`，`status_resolution` 记为 `verified_by_source_contract`，完整保留契约与修正证据；这仍不创建跨源 `mappings`，来源锚资格由 `source_lineage.json` 独立决定。
- 工具只检查证据记录结构、版本定位和状态快照，不会替复核人访问链接或判断链接内容是否权威。必须先实际打开并核对契约，再填写决定。

复制 [`source_contract_template.json`](adjudications/source_contract_template.json) 到同目录，完成逐字段核验后先预览：

```powershell
.\scripts\run_with_system_python.ps1 scripts\apply_collision_adjudications.py --decisions docs\field_verification\adjudications\YYYYMMDD_source_contract.json
```

检查输出和证据内容后，才显式应用：

```powershell
.\scripts\run_with_system_python.ps1 scripts\apply_collision_adjudications.py --decisions docs\field_verification\adjudications\YYYYMMDD_source_contract.json --apply
```

该决策文件使用顶层 `evidence_basis: "source_contract"`，不填写碰撞报告；不可把它与 L1 候选决定混在同一文件。应用仍以事务方式更新注册表并重生成字段治理文档。

## 公式/恒等关系实证定案（没有同字段锚时）

没有已验证的同义字段作为锚，并不意味着目标字段永远无法确认。若一个未确认字段能由已有已验证字段和独立来源数据通过公开定义的公式复算，可使用 `derived_relation` 路径确认目标字段本身。它与跨源碰撞、上游契约各自解决不同问题：碰撞确认两个字段是否同义；上游契约解释一个来源路径；公式证据验证目标值是否符合一个可复现关系。

- 每个输入必须是注册表中状态为 `verified`、元数据完整且无属性冲突的精确 `(source, 完整 code path)`；声明单位必须与注册表逐字一致。目标来源族必须已在 `source_lineage.json` 确认为独立，且不能与任何输入的来源族相同。
- 决策需提供目标当前的 `status`、`status_resolution` 和完整元数据快照，以及新的规范名、含义、单位和解释。只接受 `unverified` / `candidate`；已定义元数据不会被静默覆盖；`conflict`、`disproved` 和已验证字段须走其他处置路径。
- 公式只允许变量、数字常量、括号、`+`、`-`、`*`、`/` 和一元正负号；程序用 Decimal 逐行复算 CSV，不执行任意代码。单位量纲无法由程序通用推断，复核人必须在公式中写明换算常数，并用权威引用证明输入单位、输出单位与换算关系。
- CSV 必须保存在 `docs/field_verification/derived_evidence/`，不超过 10 MB / 50,000 行。每行需有股票代码、目标值、目标日期和各输入值/日期；日期列可以共用，目标与所有输入日期必须完全相同。`trading_day` 按项目交易日历校验，`report_period` 要求至少两个不同报告期，其他日期域按自然日处理。公式样本不得晚于复核日。
- 最低覆盖为 10 行、5 行非全零信息样本、3 只股票；行情/自然日样本至少 3 个不同日期，财报样本至少 2 个报告期。至少 95% 的信息样本须在容差内；相对容差不得高于 1%，绝对容差不得高于信息样本典型值的 1%，避免用过宽绝对误差掩盖不匹配。阈值只判断数值关系，不替代对字段含义和来源独立性的人工判断。
- `references` 必须包含带固定版本/日期、定位和具体主张的 HTTPS `formula_definition`，并至少包含 `target_source_path` 或 `official_data`。工具不联网打开链接；复核人需先实际核对引用内容。数据日相同不保证盘中时点相同：若字段可能盘中变化，只有能确认相同阶段/时点时才能使用；否则限制为收盘或同一报告期样本。
- 公式证据只确认目标路径的定义，不意味着它与输入字段含义相同，因此不会创建 `mappings`。应用后记录 `status_resolution: verified_by_derived_relation`、输入身份、公式、引用、样本覆盖和误差摘要；目标在来源质量和谱系规则允许时可成为后续碰撞锚。字段状态变化只影响破解队列，不会停止采集。

例如，若总市值单位为“亿元”、股价为“元”、目标总股本单位为“万股”，关系可写为 `market_value * 10000 / price`。这只有在目标总股本、总市值和股价来自足够独立的来源、使用同一有效日期/阶段且不存在循环复用时，才是有效交叉验证。**股价加流通股本不能单独推出总股本**；还需要总市值、总股本比例等额外独立信息。公式结果与目标数值吻合，只证明关系和观测值相容；上游路径、单位和来源独立性仍须由引用与样本证据支持。

复制 [`derived_relation_template.json`](adjudications/derived_relation_template.json) 填写决定，并将 CSV 样本放在 `derived_evidence/` 下。先预览，再检查输出和引用：

```powershell
.\scripts\run_with_system_python.ps1 scripts\apply_collision_adjudications.py --decisions docs\field_verification\adjudications\YYYYMMDD_derived_relation.json
```

检查无误后显式应用：

```powershell
.\scripts\run_with_system_python.ps1 scripts\apply_collision_adjudications.py --decisions docs\field_verification\adjudications\YYYYMMDD_derived_relation.json --apply
```

顶层使用 `evidence_basis: "derived_relation"`，不填写碰撞报告，也不能与其他证据路径混在一个决策文件中。每日采集与碰撞不会自动访问网络或运行这些公式；它们读取人工核验后留档的定义和 CSV，避免将临时网页、未核验语义或重复请求自动升级为主字典结论。

## 准备决策文件

对于跨源碰撞决定，复制 `docs/field_verification/adjudications/template.json` 到同目录的新文件。填写碰撞报告路径、复核人、复核日期和决定。报告路径相对于 `docs/field_verification/`；`target` / `anchor` 的 `code` 使用注册表中的完整路径。单源上游契约核验使用上节的独立模板和证据路径。

`verify` / `enrich_metadata` 必须填写稳定的 `canonical`、明确的 `meaning` 和复核理由；`unit` 可为空，但不能猜测。`enrich_metadata` 还必须填写定案前的 `previous` 快照。`link_verified` 不需要新的字段定义，但理由必须解释数值比例、单位换算以及为什么已有语义确实等价。只有确认目标与锚字段语义等价后才提交决定。无法证明等价时，不提交定案；目标字段保持原状态。单个碰撞对不等价不代表目标字段本身已被证伪。

## 撤销错误的历史定义

当解析器列映射、原始响应或跨日样本证明一个历史 `verified` 定义错误时，不能把它当作普通碰撞晋级，也不能让旧的 `reference_evidence` 静默覆盖新结论。当前碰撞决策工具没有通用的 `disprove` 动作；此类源级纠错需单独留存带日期的审计记录，并在 `field_registry.json.source_fields` 中按完整 `(source, code)` 身份将状态改为 `disproved`、注明正确的对应字段和证据路径，保留旧 `reference_evidence` 作为历史记录；同时移除所有指向已证伪身份的活动 `mappings`。随后重建 `fields` 聚合视图与 `meta.source_field_stats`，运行字典生成器和同步校验。不要修改只读历史档案来掩盖旧定义，也不要按短字段名批量证伪其他来源。示例见 [`change_30d_adjudication_20261017.md`](change_30d_adjudication_20261017.md)。

## 预览和应用

在仓库根目录运行：

```powershell
python.exe scripts\apply_collision_adjudications.py --decisions docs\field_verification\adjudications\YYYYMMDD_review.json
```

预览会验证报告、完整字段身份、来源谱系和决定内容，不写文件。检查预览无误后，显式应用：

```powershell
python.exe scripts\apply_collision_adjudications.py --decisions docs\field_verification\adjudications\YYYYMMDD_review.json --apply
```

应用会以事务式写入更新 `field_registry.json`、兼容聚合字段状态和 `meta.source_field_stats`，并重生成 `field_dict.md`、`unknown_fields.md`、`source_repository_map.md`、`field_metadata_gaps.md`。验证记录会保留报告路径、样本日期、命中情况、复核人、决定理由、外部证据、变更前后值和唯一决定 ID。确认等价的字段对还会写入 `mappings`，供后续碰撞跳过已定案关系；使用现有关系值 `same_number_same_meaning`。兼容聚合视图仅在所有逐源记录对某元数据项均为相同非空值时才展示该项；数值代码相同但来源定义不同或任一来源缺少定义时，聚合语义留空，避免把某源的 `fNN` 含义误投射到另一源。

`field_matrix.md` 表达字段和来源的覆盖关系，状态/语义变更不改变该投影。应用后仍应运行 `registry_parity.py`、`verify_sync_check.py` 和对应测试。

## GitHub 仓库确认状态

`source_lineage.json` 将本地项目证据状态 `repository_mapping_status` 与用户对话确认 `dialog_confirmation.status` 分开记录。用户确认某仓库是客户端、传输层或包装库，不会自动把它标成底层数据提供方，也不会改变独立来源族。来源映射页分别显示这两种状态；未确认条目保持 pending，取得候选仓库证据后再逐项与用户确认。
