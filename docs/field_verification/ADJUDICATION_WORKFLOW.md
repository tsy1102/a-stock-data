# 碰撞候选人工定案与注册表同步

`collide.py` 只发现候选，不直接改变主字典。报告完整性与全量候选审阅按 [`COLLISION_REPORT_REVIEW.md`](COLLISION_REPORT_REVIEW.md) 执行。只有经过逐项证据复核的决定，才能通过此流程写入逐源字段注册表。数值命中本身不是语义定案。用户要求运行采集并碰撞时，授权包含对达到现行规则的候选完成本流程；执行者应自行完成预览、应用和验证，无需再次请求进入定案。未达到门槛的候选保持原状态，并记录证据缺口。

## 候选审阅状态（schema 5 起）

schema 5 碰撞报告为完整方法候选、L1/L1-C、L4 和公式候选生成稳定 `candidate_id`；身份包含完整来源路径、方法/结果、日期与样本资格及其报告记录的候选方法版本。当前新报告使用 `collision-candidate-v2`：收紧 L1 精确匹配精度，并将展示舍入差异移到独立研究层。历史 `collision-candidate-v1` 报告仍按报告内记录的版本校验和查询；其旧审阅不会附着到 v2 新身份。若候选算法、归一化、精度或样本资格语义发生变化，必须提升 `scripts/collision_candidate_reviews.py` 中的 `METHOD_VERSION`。`docs/field_verification/collision_candidate_reviews.json` 是独立追加式人工审阅台账；机器候选完整率、身份校验和人工审阅进度分别统计。`unreviewed` 是默认派生状态，不是人工处置。

复制 [`review_templates/candidate_review_template.json`](review_templates/candidate_review_template.json) 后填写决定，先预览，再显式应用：

```powershell
$decision = 'docs\field_verification\adjudications\YYYYMMDD_candidate_review.json'
.\scripts\run_with_system_python.ps1 scripts\review_collision_candidates.py --decision $decision
.\scripts\run_with_system_python.ps1 scripts\review_collision_candidates.py --decision $decision --apply
```

每项决定必须引用至少一份包含该候选的碰撞 JSON；工具保存引用路径与 SHA-256，并验证候选身份。批量决定可用 `{"schema_version":1,"decisions":[...]}`，重复成员必须逐项指向同一个代表候选，台账和报告会保留代表/成员双向索引。合法处置为 `duplicate_grouped`、`insufficient_evidence`、`needs_external_evidence`、`accepted_for_adjudication`、`rejected`；每条记录都带审阅人、带时区时间、理由、证据引用和历史事件。

审阅台账不会写字段注册表。对于 schema 5 的 L1 注册表裁决，必须先将该候选置为 `accepted_for_adjudication`，再用更新后的碰撞报告运行现有 `apply_collision_adjudications.py` 预览/应用。老 schema 3/4 报告维持兼容；schema 5 的候选身份和审阅状态则由完整性闸门复核。

## 探索模式结果如何继承

`collide.py --exploratory` 会把报告中的 L1、L4 和方法候选按无序字段对登记到 `collision_research_state.json.gz`，并以 gzip 台账保留每次观察的完整 sections 证据、数据日和报告路径；仅从磁盘副本移除可由最新 observation 重建的重复 latest_evidence。后续碰撞报告会为再次出现的字段对附上 `research_history`，同时汇总累计候选数、历史复现数和本次新发现数。FTShare REST 的 L1-C 契约锚候选不计作独立来源研究状态；它通过每天保存的 `raw_ftshare_rest.json` 在默认碰撞中重算，并在报告中单列。

同一数据日、报告路径、窗口和上下文范围的重跑视为同一次观察，会替换该次候选记录而不重复累计；不同上下文范围会使用独立报告目录并形成新的观察。该台账是探索研究记录，不会自动提升字段状态，也不会让 L4 或方法候选进入主字典。只有符合下方正式流程、人工确认语义并显式应用的决定才会更新注册表。

## 可以进入此流程的候选

- 报告必须是 `collision_mode: verified_anchor_only`，且 `exploratory_pair_count` 为 0。
- 只接受碰撞报告 schema 3、4 或 5，且 `report_completeness.status` 必须为 `complete`；schema 4 起还包含来源覆盖章节，schema 5 另校验候选身份与审阅摘要。应用器会复核方法候选总数、全量 inventory、目标覆盖计数和可裁决章节计数。缺清单或任一数量不一致时不得定案。旧版报告需先从原始归档重建为完整新报告。
- 仅接受报告 `actionable_L1` 中的 `L1` 或 `L1-U` 新候选；旧版报告没有该键时才回退读取 `L1`。schema 5 还要求该候选的审阅处置是 `accepted_for_adjudication`。已登记映射的当前窗口复验另列于 `mapped_pair_revalidations`，不是新候选；L4、方法候选和未知字段互撞结果不能直接晋级。
- FTShare 官方契约字段确实参与默认碰撞，强匹配会显示在报告的 `L1-C` 中；`L1-C` 因底层来源独立性未确认而不进入 `actionable_L1`，也不会被普通 L1/L1-U 决策自动应用。它是有公开语义定义的碰撞锚候选，不是独立来源锚或跳过碰撞。
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
- 常规核验接受 `unverified` / `candidate`。`conflict` 可由上游契约解除的形态有两类：① `status_resolution` 为 `status_conflict`，逐源参考状态只有 `verified`，`registry_aggregate_status` 为 `unverified`，状态证据值只有 `verified` 与 `unverified`，`attribute_conflicts` / `attribute_ambiguities` 为空，且非空 `reference_evidence.status` 全为 `verified`；② 短代码被多个来源复用，`registry_aggregate_status` 为 `conflict`，状态证据值只有 `verified` 与 `candidate` 或只有 `verified` 与 `conflict`，目标来源属于至少两个且唯一的聚合来源，内嵌聚合来源和状态与状态证据一致，并满足同样的逐源参考及属性条件。第二类只验证精确 `(source, code)` 路径，不会解除或覆盖其他来源的状态冲突。两类都不覆盖真实语义/属性冲突；`disproved` 不能走此路径。
- 已有有效元数据默认不能覆盖。`action: correct_verified_metadata` 专用于已经 `verified` 且 `status_resolution: matched` 的字段，必须附 `metadata_correction`，精确记录 `previous` / `updated` 三项快照并写明理由；快照须与决策的字段值完全一致，目标不得有 `attribute_conflicts`，也不能在同一决定内附带别名。常规 `verify_source_contract` 仍只接受未验证、候选或满足前述条件的可收敛状态冲突字段。核验通过后，逐源记录保持 `verified`，`status_resolution` 记为 `verified_by_source_contract`，完整保留契约与修正证据；该流程不创建跨源 `mappings`，来源锚资格由 `source_lineage.json` 独立决定。
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

## 官方来源网站的标签与数值核验

先按 `source_lineage.json` 确认字段所属的实际数据提供方，再访问该提供方的官方接口/协议文档、字段字典和官网股票查询页面。比较前按字段时间语义对齐：日快照匹配来源日期和交易阶段，财报值匹配报告期及披露版本，已完成历史事件匹配同一事件身份/状态/日期/数量，不要求事件日期等于采集日。每日采集与碰撞完整审阅后执行此项核验；样本、留证和访问规则见 [`PUBLIC_WEB_VERIFICATION.md`](PUBLIC_WEB_VERIFICATION.md)。

- 产品页面是外部佐证，不自动等同于数据提供方契约。只有上游正式接口/协议定义及项目适配器映射能精确解释来源路径时，才走“单源上游契约核验”；不能把网页展示名冒充为原始字段路径定义。
- 页面值吻合可以支持已有碰撞候选或公式假设，但不会提高碰撞等级、增加独立来源数或单独创建 `mappings`。来源谱系未知时，网页数据也不作为独立来源锚。
- `candidate_triage.approximate_matches` 仅用于独立研究线索排序；其宽容差近似命中不属于 L1/L1-U，也不会生成正式 `candidate_id` 或审阅台账项。只有另行满足现有碰撞、契约、公式或下方官方页面观测路径，并有可核对的单位、显示精度、日期及反例记录，才可进入注册表流程。
- 如果提供方官网无法提供历史值或字段标签，再用新浪、同花顺等第三方页面作次级佐证；若它们本身就是注册表登记来源，则按对应来源逐路径核验。需要记录回退原因，不能把第三方显示口径冒充该字段提供方的官方定义。
- 若来源谱系仍未确认，不得仅根据客户端仓库、SDK 名称或登录域名猜测实际数据提供方；将提供方身份缺口记为待核，并继续核实来源映射。
- 每条证据要保存精确 HTTPS 链接、访问时间、页面标签和值、单位、有效日期/报告期、股票代码、原始来源日期、阶段、换算依据和不匹配样本。搜索摘要、论坛转载或仅一只股票/一天的吻合只能作为线索。
- 日期比较按字段时间域处理：历史事件须核对同股、事件类型/状态、事件日期、数值/数量和单位，并确认其在原始样本截止时已发生或公开、未被更正/撤销；“最近/下一项”等选择语义还须匹配当时的选择范围。当前网页可佐证稳定事件的语义，但不能单独证明历史采集时的可用状态。
- 若网页证据仍未解决项目 raw 路径到展示指标的映射，候选保持 `needs_external_evidence`，在候选审阅记录中引用网页核验备忘录和相关链接。若没有可用于跨源定案的候选，但满足下方“官方页面精确观测裁决”的逐值门槛，可只登记来源内语义；否则继续保留未决状态。
- 公开网页研究备忘录只记录证据，不等于候选审阅或注册表裁决。对用于跨源映射且已有 `candidate_id` 的研究对象，仍须通过候选审阅流程记录正式处置并引用碰撞报告、研究备忘录和相关网页；来源内语义按下方单独路径裁决。已验证字段的补充佐证不要求重写注册表，也不自动创建映射。

## 官方页面精确观测裁决（不等同上游接口契约）

当官方产品页直接显示某个有标签的指标，而项目保留的原始响应没有字段说明时，可用页面的同日逐值对照登记**该来源内部**的字段含义。此路径记录实际观测，不声称页面是 API 契约，也不确认分类算法代表真实投资者身份。

- 必须逐字段核实精确 `(source, 完整 code path)`；页面须属于已确认的实际提供方，记录至少两个不同股票代码、同一个数据日的原始字段值、页面标签、显示值、单位和显示精度。应用器同时核验 `source_lineage.json` 中的提供方身份及代码维护的官方主机名白名单；目前 Eastmoney 白名单仅含 `data.eastmoney.com`。数值应在页面显示精度的半个最小刻度内。原始值单位与页面单位不同时，观测必须显式填写 `raw_to_display_factor`，按 `raw_value × raw_to_display_factor` 换算后再与页面值比较；该因子也会写入结构化证据和注册表审计记录。字段 `unit` 仍记录原始来源单位，`display_unit` 记录页面单位。
- 原始值为 `"-"` 时，只有同日官方页面明确显示零，才能在该观测中按零比较。原始采集值仍保留 `"-"`，不得据此把解析器的缺失值通用转成零。
- 若语义依赖公式，附带保留期原始文件列表并重算；至少 10 个数值样本、3 个数据日、3 只股票，且数值样本和明确标注的缺失值哨兵样本均无反例。每个目标字段可登记一条公式；同一决策文件可用 `formula_validations` 数组验证多个目标，目标码不得重复且各自必须对应唯一决定。旧版单项 `formula_validation` 继续兼容。公式只佐证字段语义，不代替页面标签到原始路径的逐值对应。
- 默认只允许填写空白或占位元数据。目标已有完整定义、但来源状态仍为 `unverified` / `candidate` 时，可显式设 `verification_mode: "confirm_existing"`；此模式要求 `canonical`、`meaning`、`unit` 与先前快照完全相同，且没有属性冲突，只确认状态并记录观测，不改写元数据。它不能覆盖已确立含义/单位，也不能解除属性冲突。其他 `conflict` 仍仅可在状态冲突确为 registry 聚合范围导致、含义与单位无冲突、`attribute_conflicts` 为空或仅含合法的 canonical 冲突，并完整保存原快照时处理。Eastmoney 研报作者字段有单独的窄范围记录裁决模式，见下文。
- 决策使用 [`public_web_observation_template.json`](adjudications/public_web_observation_template.json)，顶层为 `evidence_basis: "public_web_observation"`。证据备忘录须逐行保存决策中每条观测的规范化 `[observation]` JSON 记录；工具核验原始样本、日期、值、舍入刻度、提供方主机、决定快照和证据路径，parity 再逐项比较裁决快照与原决定。网页内容由复核人先实际访问核实。定案记录标记 `verified_by_public_web_observation`，不新增 `mappings`，也不把网页计为独立来源。

先预览，再检查每只股票、页面标签和显示刻度后显式应用：

```powershell
.\scripts\run_with_system_python.ps1 scripts\apply_collision_adjudications.py --decisions docs\field_verification\adjudications\public_web\YYYYMMDD_decisions.json
.\scripts\run_with_system_python.ps1 scripts\apply_collision_adjudications.py --decisions docs\field_verification\adjudications\public_web\YYYYMMDD_decisions.json --apply
```

跨源候选审阅仍使用现有候选审阅台账和 adjudication 文件保存证据引用；官方页面精确观测使用上方已实现并纳入 parity 的 `public_web_observation` 专用路径。研究、候选人工处置、注册表应用是不同步骤；只有达到相应路径的完整门槛且字段状态/元数据/映射确需变化时才应用。应用工具不会打开网页核验内容，执行者必须先实际访问链接、比较样本并保存书面结果。

### Eastmoney 研报记录字段的记录级冲突裁决

`resolve_report_record_conflict` 仅用于 `reports::author`、`reports::researcher`、`reports::lastEmRatingName` 与 `reports::emRatingCode`。每个目标至少核对三只不同股票，所有观测使用同一个保留期采集日；每条网页记录都要通过 `infoCode`、标题和发布日期与 `raw_reports.json` 中唯一记录绑定。`author` 逐项比较页面作者链接的 ID/姓名与原始 `ID.姓名` 数组，并核对 `authorID`；`researcher` 比较页面作者顺序与原始逗号分隔姓名串。`lastEmRatingName` 只允许用“评级变动”为“维持”的记录：原始 `ratingChange` 必须为已验证的 `3`，网页当前“东财评级”须与原始 `emRatingName`、`lastEmRatingName` 全部相等。`emRatingCode` 的代码本身不在官网列表页显示：按同一记录核对网页“东财评级”与原始 `emRatingName`，并检查该采集日完整归档中每个已观测代码是否只对应一个名称；这只能支持已观察到的分类代码含义，不是完整代码表。此模式不覆盖未观察代码，不将网页观察升级为 API 契约，不建立字段映射，单位保持空值。其他 `reports` 字段不得使用此模式。

`reports::sRatingCode` 使用独立裁决模式 `verify_report_source_rating_code`，只接受当前为 `unverified`、无元数据冲突的字段。每个裁决至少绑定三只不同股票的研报详情页，详情 URL 必须包含记录 `infoCode`；页面标题、发布日期和原始归档行也须一致。网页正文中的原始评级文字与同记录 `sRatingName` 至少两条精确匹配；允许登记特定近似命中（当前只支持 `买入` 对 `买入(Buy)`），但近似项单独计数且不得充作精确命中。完整同日归档须满足每个 `orgSName + sRatingCode` 只对应一种 `sRatingName`，并显示相同代码跨机构有多种名称。结论只确认“机构原始评级类别代码”这一字段角色，不发布代码表、不建立跨源映射，单位为空。作者/研究员模板见 [`public_web_report_record_template.json`](adjudications/public_web_report_record_template.json)，前次评级模板见 [`public_web_report_last_rating_template.json`](adjudications/public_web_report_last_rating_template.json)，东财评级码模板见 [`public_web_report_em_rating_code_template.json`](adjudications/public_web_report_em_rating_code_template.json)，机构原始评级码模板见 [`public_web_report_s_rating_code_template.json`](adjudications/public_web_report_s_rating_code_template.json)，逐条证据和记录识别要求见 [`PUBLIC_WEB_VERIFICATION.md`](PUBLIC_WEB_VERIFICATION.md)。

## 源内语义与跨源映射分开裁决

高命中率但存在少量反例时，不要把整个字段对压成“全部定案”或“全部不定案”两种结论。分别判断并记录：

- **来源内语义**：官方字段契约、项目解析器的位置映射，以及多数据日的独立来源对照，可以支持某来源字段的较宽语义类别；分类体系、层级或口径未证实的部分必须明确保留未知。可通过 `source_contract` 或 `source_field_addenda` 登记来源自身语义。
- **跨源关系**：只有双方语义、单位、来源日期和精度对齐后，才能登记逐值同义映射。少数反例若超出已证实的舍入/精度边界，应保留或拒绝这条映射；它本身不自动推翻字段来源内较宽的语义结论。
- **近似证据**：近似命中率只用于定位线索，不能代替字段定义或直接生成映射。必须逐项核对反例、单位、展示精度和有效日期；不得为了达到命中率而放宽整数或精确匹配阈值。

因此，注册表可先确认来源内语义，同时把跨源等价关系留在待补证状态；只有关系本身得到证实时，才写入 `mappings`。

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

## 排除类型/格式占位符路径

若注册表的 `code path` 是 `float`、`int`、`YYYYMMDD` 等类型或日期格式记号，不能仅凭词面判断它不是字段。须确认该记号在对应来源文档中只出现在类型/格式位置、当前解析器与测试没有以它作为输出键；使用历史样本时，先按来源实际数据日和权威日期标识筛选，再检查保留期 raw 的对象键。重复采集按实际来源数据日去重，保留起点前样本不得读取。

满足上述条件后，留存逐来源的日期化审计记录，仅将对应精确身份标为 `disproved`、`status_resolution: not_field_schema_token`，并说明它是类型/格式占位符而非数据路径；不创建字段映射，不把相同短 token 批量套到其他来源。若该字符串确实是接口响应键，则继续按普通来源字段核验。

## 退出当前解析器中的历史来源路径

当注册表仍列出一个旧来源路径，但当前解析器和测试均不再输出该路径时，先按完整 `(source, code path)` 检查它是否只是同一来源中已由新路径承接的历史键。必须有旧协议/说明明确旧键指向的来源列、当前解析器把同一列映射到新键、测试覆盖当前映射，并检查保留期内按来源实际数据日去重后的样本未出现旧键；不得把目录自然日当成来源日期，也不得读取保留起点之前的 raw、ZHB 包或解析缓存。

确认旧路径已退出且与当前路径为同源同列别名后，留存带日期的路径退役审计记录，仅将旧身份标为 `disproved`、`status_resolution: retired_legacy_path`，并在 `canonical` 和 `meaning` 中指向当前同源路径、说明它不是独立输出字段。保留原 `reference_evidence` 与旧状态快照；不改当前路径状态，不新增跨源 `mappings`，也不修改只读历史档案。若无法证明同源同列，继续保持待核，不以字段名相似为依据退役。

此操作表示“该精确代码路径不再由当前解析器生产”，不表示当前承接路径的语义被证伪。手工更新 `source_fields` 后，重建聚合视图和字典，运行 parity、同步校验及相应回归。

## 撤销错误的历史定义

当解析器列映射、原始响应或跨日样本证明一个历史 `verified` 定义错误时，不能把它当作普通碰撞晋级，也不能让旧的 `reference_evidence` 静默覆盖新结论。当前碰撞决策工具没有通用的 `disprove` 动作；此类源级纠错需单独留存带日期的审计记录，并在 `field_registry.json.source_fields` 中按完整 `(source, code)` 身份将状态改为 `disproved`、注明正确的对应字段和证据路径，保留旧 `reference_evidence` 作为历史记录；同时移除所有指向已证伪身份的活动 `mappings`。随后重建 `fields` 聚合视图与 `meta.source_field_stats`，运行字典生成器和同步校验。不要修改只读历史档案来掩盖旧定义，也不要按短字段名批量证伪其他来源。示例见 [`change_30d_adjudication_20261017.md`](change_30d_adjudication_20261017.md)。

## 预览和应用

在仓库根目录运行：

```powershell
$decisions = 'docs\field_verification\adjudications\YYYYMMDD_review.json'
.\scripts\run_with_system_python.ps1 scripts\apply_collision_adjudications.py --decisions $decisions
```

预览会验证报告、完整字段身份、来源谱系和决定内容，不写文件。检查预览无误后，显式应用：

```powershell
$decisions = 'docs\field_verification\adjudications\YYYYMMDD_review.json'
.\scripts\run_with_system_python.ps1 scripts\apply_collision_adjudications.py --decisions $decisions --apply
```

应用会以事务式写入更新 `field_registry.json`、兼容聚合字段状态和 `meta.source_field_stats`，并重生成 `field_dict.md`、`unknown_fields.md`、`source_repository_map.md`、`field_metadata_gaps.md`、`field_aggregate_review.md`。验证记录会保留报告路径、样本日期、命中情况、复核人、决定理由、外部证据、变更前后值和唯一决定 ID。确认等价的字段对还会写入 `mappings`，供后续碰撞跳过已定案关系；使用现有关系值 `same_number_same_meaning`。兼容聚合视图仅在所有逐源记录对某元数据项均为相同非空值时才展示该项；数值代码相同但来源定义不同或任一来源缺少定义时，聚合语义留空，避免把某源的 `fNN` 含义误投射到另一源。

`field_matrix.md` 表达字段和来源的覆盖关系，状态/语义变更不改变该投影。应用后仍应运行 `registry_parity.py`、`verify_sync_check.py` 和对应测试。

### 同源别名导致的历史状态冲突

少量历史字段可能因“本字段仍留有候选标记、同源注册表聚合已验证”而显示 `status_conflict`。只有当裁决显式提供 `same_source_alias`，并满足以下全部条件时，来源契约流程才允许收敛：别名身份与目标来源相同且路径不同；锚字段已验证、无属性冲突；裁决后的含义和单位与锚字段完全一致；证据文件位于 `docs/field_verification/` 内并存在；证据记录至少一个同日样本配对且差异数为零。决策会保存别名身份、证据路径与样本计数，不会创建跨源映射。

此例外仅针对上述候选/已验证同源别名形态。语义冲突、属性冲突、跨源别名、未验证锚字段、元数据不一致或缺失证据仍会被拒绝。常规 `verify_source_contract` 冲突限制保持不变。

### 短代码跨接口复用导致的聚合状态冲突

一个短代码可能在不同接口中分别代表不同字段。来源契约仅证明目标 `(source, code)` 时，可以按上面的第二类条件核验该精确路径；其余接口的状态仍保留在聚合视图中，除非各自取得独立证据并分别裁决。例：`东财-em_kline_f61::f59` 与实时行情接口中的 `f59` 属于不同字段命名空间，不得因聚合 `f59` 状态为 `conflict` 而阻止日 K `f59` 的来源内核验，也不得借此将其他接口 `f59` 一并标为已验证。

## GitHub 仓库确认状态

`source_lineage.json` 将本地项目证据状态 `repository_mapping_status` 与用户对话确认 `dialog_confirmation.status` 分开记录。用户确认某仓库是客户端、传输层或包装库，不会自动把它标成底层数据提供方，也不会改变独立来源族。来源映射页分别显示这两种状态；未确认条目保持 pending，取得候选仓库证据后再逐项与用户确认。
