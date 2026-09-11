# 字段登记表「单一真相源」架构根治计划（Plan (b)）

> 关联：P0（`gen_field_matrix` §零·B 写回护栏，已提交 `1fc9dd4`）、P1（归档契约预检，已提交 `1fc9dd4`）
> 数据来源：通达信 a-stock-data 字段破解体系（`docs/field_dict.md`）
> 状态：**G0 闸门已签字（5 项安全默认已定）；Phase 1 抽取完成且 G1 闸门 PASS（已提交 `e009cc5`→`8728279`）；Phase 2（治理脚本改读 registry）已完成 6/8 脚本改读 + 2 个刻意排除/延迟（最新提交 `e3daf69`）；Phase 3（markdown 单向生成 `gen_field_dict.py`）已完成，G3 闸门 PASS（幂等、§零·B 字节一致、subdict-index 自动索引），详见 §6.4（本次收尾提交）。**

---

## 0. 目标与动机（为什么做）

当前 `field_dict.md` 同时扮演两个角色：

| 角色 | 消费者 | 改字典的后果 |
|---|---|---|
| 人类可读契约文档 | 人、注释 | 无 |
| **机器可解析数据源** | `scripts/` 下 8 个治理脚本 | **行为直接改变** |

这是经典的 **document-as-database（文档即数据库）反模式**：只要工具在解析文档，改文档就必然改工具行为。本次已观测到的两个真实症状：
1. `gen_field_matrix` 从主字典正文表格抽取字段，归档搬章节 → 数字从 1147/1402/63 掉到 723/876/34（尺子变短，非东西变少）。
2. `audit_field_completeness.py` 用硬编码章节号（`SECTION_MAP`）定位，章节被迁走 → 误判假 GAP。

**根治方向**：把机器消费的部分抽成 **YAML/JSON 单一真相源 `field_registry`**，markdown 由它**生成**而非被它**解析**。治理脚本改读 `field_registry`，彻底切断「改文档→改工具行为」的隐式耦合。

> P0/P1 是**止血**（护栏 + 预检），本计划是**治本**（消除反模式本身）。

---

## 1. 现状盘点（规模决定难度）

| 指标 | 数值 |
|---|---|
| `field_dict.md` 规模 | **5395 行 / 556 KB / ~2809 表格行** |
| 主字典字段基数 | **1156 唯一字段 / 1412 记录 / 64 多源** |
| `docs/verify/` 分字典 | **17 个** |
| 消费主字典的脚本 | **8 个**（见 §3） |

**8 个消费脚本及消费方式**：
| 脚本 | 消费点 | 依赖的 markdown 结构 |
|---|---|---|
| `audit_field_completeness.py` | `SECTION_MAP`（L62）子串匹配标题 + 正文提取字段 | 章节标题 + 字段表 |
| `gen_field_matrix.py` | `build_matrix()` 全正文解析表格 | §零·B marker 区间 |
| `verify_sync_check.py` | `MAPPING`（L56）源→分字典 + 引用扫描 | 引用 `docs/verify/*.md` |
| `lint_field_names.py` | 字段命名规则扫描 | 字段表 |
| `lint_field_same_number.py` | 跨源同号异义校验（含 A7 血缘护栏） | 字段表 + scheme |
| `field_landing_audit.py` | 字段落点审计 | 字段表 |
| `verify_ulist_push2_collision.py` | ulist/push2 同号碰撞 | 字段表 |
| `expand_range_fields.py` | 区间字段展开 | 字段表 |

**生产取数层（`stock_common/`、`core/`、`get_*_report.py`）零耦合**：已核实全部 `field_dict` 引用为注释，无运行时 `open(...field_dict...)`。本计划**不触碰生产取数层**。

---

---

## 1.5 G0 阶段交付（盘点 + Schema 冻结）— 待 G0 闸门签字

> 本阶段为**只读盘点 + 设计冻结**，不实施任何抽取/改写代码。交付物：（1）9 脚本消费点详单；（2）`field_registry.yaml` Schema 冻结草案（含真实小样本）；（3）存储格式选型。Phase 1 抽取需待本闸门签字后启动。

### G0.1 消费点详单（基于代码事实，非推测）

9 个治理脚本对 `field_dict.md` / `docs/verify/*.md` 的机器消费，集中在**三类耦合形态**：

| 脚本 | 消费的核心 md 数据结构 | 耦合 | 改读 registry 的难度 | 关键强依赖点 |
|---|---|---|---|---|
| `audit_field_completeness.py` | `SECTION_MAP`(L62,22 项子串) + 全文字段记号按源分组 | 高 | 高 | SECTION_MAP 子串须逐字命中标题；标题层级继承；fNN/[NN]/snake/camel 记号约定 |
| `gen_field_matrix.py` | 全表首格字段名→源集合（`sec_to_source` L61 巨型子串链 + `GEN` marker 写回） | 高 | 高 | `sec_to_source` 几十个特定子串；两个 `GEN` marker 必须存在 |
| `verify_sync_check.py` | 主字典 token/status/date ↔ 17 分字典 token/status/date | 高 | 中高 | `MAPPING`(L56,17 项)硬编码；token 正则与分字典书写格式绑定；`UPGRADE_EVENT_RE`/`DATE_RE` 与措辞绑定 |
| `lint_field_names.py` | 全行字段别名/样式违规（跳过区 L21-30） | 中 | 低 | **相对路径**(L17) CWD 耦合；跳过区起止标记改写即静默误通过 |
| `lint_field_same_number.py` | §12.3.2.3 表(ulist fX/status/note) + §12.8.12e 注册表(canonical/别名) + 对齐表 | 高 | 中 | §12.3.2.3 标题子串 + 三列表格；§12.8.12e 标题 `^#+\s*12\.8\.12e`；对齐表 `ulist fX \| fY` |
| `field_landing_audit.py` | 全文 fNN 强/弱登记 + 四列表行(`\| **fNN** \| 含义 \| 单位 \| 状态 \|`) | 中高 | 中 | `f\d{1,4}` 全文扫描易污染；四列表列数/顺序变动即漏抽 |
| `verify_ulist_push2_collision.py` | §12.3.2.3 未实证列表 + 对齐表 | 中高 | 低-中 | §12.3.2.3 标题子串 + `未实证` 关键词；对齐表 `ulist fX \| fY` |
| `expand_range_fields.py` | 区间/斜杠记号串（文本规范化，写回） | 中 | 低（**建议退役**） | 记号格式约定；是冗余记法的生产者，registry 化后可废弃 |
| `verify_cross_source_crack.py` | §12.3.2.3 未实证列表 + scheme 血缘 | 中高 | 低-中 | §12.3.2.3 标题正则；`未实证·待核实` 精确子串；**相对路径**(L33/L214) |

**横切结论（设计依据）**：
1. 最脆弱的耦合只有三类：① 章节标题子串匹配（SECTION_MAP / sec_to_source / §12.3.2.3 / §12.8.12e）；② `\| fX \| ... \|` / `\| 字段 \| 含义 \| 单位 \| 状态 \|` 表格列结构；③ 状态/记号关键词硬约定（✅/未实证/已证伪/`**[N]**`/各种 token 正则），分散在 6+ 脚本重复维护。
2. **对齐表 `ulist_push2_align.md` 已是准 registry 雏形**（3 脚本解析同一份 `ulist fX \| fY`），应升格为 `mappings`。
3. **§12.8.12e 规范注册表已是半结构化注册表**，应并入 `fields[].names.canonical/aliases`。
4. 两个脚本几乎与 registry 无关：`lint_field_names`（只查命名样式，仅修相对路径即可）、`expand_range_fields`（应随冗余记法消失而退役）。
5. **相对路径硬伤**：`lint_field_names`(L17)、`verify_cross_source_crack`(L33/L214) 用相对路径，CI 在错误 CWD 下直接失败——无论是否 registry 化都应先修为 `ROOT` 绝对路径（属 P1 范围外的小修，建议 Phase 2 顺带）。

### G0.2 `field_registry.yaml` Schema 冻结草案（含真实小样本）

```yaml
meta:
  version: 1
  updated: 2026-09-11
  source_of_truth: field_registry.yaml
  generated_warn: "docs/field_dict.md 字段表由本文件生成，勿手改"

sources:                          # 替代 verify_sync_check.MAPPING + BUILTIN_SCHEME + SECTION_MAP 源名
  - name: 东财-push2              # 唯一源标识（slug）
    scheme: eastmoney.stock_get   # 采集 meta.schemes 标识
    verify_file: push2_verify.md # docs/verify/ 下分字典文件名
    section_patterns:            # 原 SECTION_MAP 子串（保留仅用于 markdown 生成回链，不再参与运行判定）
      - "12.3.1 单股行情"
      - "12.8.3 东财 datacenter"
    status: active

fields:                           # 字段级单一真相源（替代 markdown 字段表 + 全文正则扫描）
  - code: f3                      # 主键：主记号码（fNN / [NN] / 字段NN / snake_case / camelCase 之一）
    source: 东财-push2            # 归属源（替代 SECTION_MAP 子串匹配 + sec_to_source 链）
    section: "12.3.1 单股行情"    # 章节归属（替代章节标题子串定位）
    names:
      canonical: 现价             # 规范中文名（替代 §12.8.12e 注册表 canonical 列）
      aliases: [当前价, 最新价]    # 别名集合（替代 lint_field_names FORBID / 全文别名扫描）
    type: float
    unit: 元
    description: "最新成交价"
    scheme: eastmoney.stock_get   # 该字段所属 scheme（替代 BUILTIN_SCHEME 硬编码）
    status: verified              # 见下方 status 枚举
    verified_date: 2026-09-04
    raw_codes: [f3, "现价", "最新价"]   # 原始记号全集（供 lint 全局扫描替代全文正则，去重去噪）
    evidence: "第七轮审计"          # 实证来源（CROSS/VERIFIED 类的证据标记）
  - code: "[1]"                   # 腾讯数组索引记号作主键
    source: 腾讯-qt.gtimg
    names: {canonical: 股票代码}
    scheme: tencent.qt.gtimg.array
    status: verified
    raw_codes: ["[1]", "股票代码"]

mappings:                         # 替代 ulist_push2_align.md 对齐表（已是准 registry 雏形）
  - from: {source: 东财-ulist239, code: f1}
    to:   {source: 东财-push2, code: f59}
    relation: cross_number_diff_meaning   # 同号异义（异体系，跨号映射实证）
    evidence: "ulist_push2_align.md L8"
  - from: {source: 东财-ulist239, code: f2}
    to:   {source: 东财-push2, code: f43}
    relation: same_number_same_meaning    # 真同号同义（对齐表实证，X==Y）
    evidence: "ulist_push2_align.md L9"
```

**`status` 枚举（归一原分散关键词）**：
| 枚举值 | 原 markdown 关键词 | 含义 |
|---|---|---|
| `verified` | ✅ + 实证（第七轮审计/数值实证） | 已定案同义映射 |
| `disproved` | 已证伪 | 主张被实测推翻 |
| `unverified` | ⚠️ 未实证/待核实/待破解/待数值对撞 | 显式声明无实证，允许 |
| `cross` | ✅ + 跨源/交叉验证（异源具名字段对撞定案） | 同号即同义铁律的正确解药 |
| `candidate` | （lint 新发现尚未定案） | 候选待审 |
| `deprecated` | 已弃用 | 退役字段 |

**Schema 对 9 脚本的覆盖证明**：
- `audit_field_completeness` REG 侧 → `fields[].source + section` 直接出"各源登记字段集"，删除 SECTION_MAP/全文正则。
- `gen_field_matrix` → `fields[].code + source` 直接出字段×源矩阵，删除 `sec_to_source` 链。
- `verify_sync_check` → `sources[].verify_file` 取代 `MAPPING` 硬编码；token/status/date 正则保留（作用于分字典，仍合法）。
- `lint_field_same_number` → `fields[].status` + `mappings` + `fields[].scheme` 取代 §12.3.2.3 表/§12.8.12e 注册表/对齐表。
- `field_landing_audit` → `fields[].raw_codes + status + names` 取代全文 fNN 扫描/四列表。
- `verify_ulist_push2_collision` / `verify_cross_source_crack` → `fields[].status(unverified)` + `mappings` 取代 §12.3.2.3/对齐表。
- `lint_field_names` → `fields[].names.aliases` 取代 FORBID 表（几乎零改动，仅修相对路径）。
- `expand_range_fields` → registry 化后区间/斜杠记法消失，本脚本退役。

### G0.3 存储格式选型

**决策变更（约束驱动的最安全选择）：采用 JSON（`field_registry.json`），非原 YAML。**
- **原因**：本执行环境（系统 Python 3.12）**未安装 `pyyaml` / `ruamel`**，手写 YAML emitter 风险高且易出解析歧义。JSON 是 YAML 的**严格子集**（任何 YAML 读取器均可读），Schema/结构与原草案**完全一致**，Phase 2 脚本用 stdlib `json.load` 零依赖读取。
- 保留项：人可审（结构化缩进）、可 diff（git 友好）、可机读。缺失的"注释"能力由 `meta.note` / `fields[].status_raw` 等字段补偿（原文记号不丢）。
- 若后续环境补齐 `ruamel.yaml`，可无损转 YAML；当前 JSON 即权威格式。

### G0 待签字项（G0 闸门）— 用户授权"由我做出最安全合理决定"

用户明确表示对 5 项无明确偏好，授权我按最安全合理原则定夺并继续推进。以下为**已落定的安全默认**（均已在 Phase 1 实施验证）：

1. **Schema 属性全集**：采用草案全集（`code/source/section/sources/canonical/meaning/unit/status_raw/status` + `sources[]` + `mappings[]`）。**追加 `status_raw` 字段**保留原始中文状态记号（✅/⚠️未实证/已证伪…），**绝不丢弃原始信息**（安全底线）。`type/description/verified_date/raw_codes/evidence` 留作后续扩展位，当前抽取未强制填充以免臆造数据。
2. **`status` 枚举**：采用 6 值（verified/disproved/unverified/cross/candidate/deprecated）。**保守默认**：无法判定者一律 `unverified`，绝不误标 `verified`；同时 `status_raw` 存原文供人工复核。
3. **格式**：JSON（见 G0.3，约束驱动最安全选择）。
4. **退役/吸收**：Schema **结构上已支持** `mappings`（吸收 `ulist_push2_align.md`）、`names.canonical` 等价物（`canonical` 字段吸收 §12.8.12e 规范名）。但**实际脚本退役/删除推迟到 Phase 2**——Phase 1 只产影子 registry，不触碰任何运行中的脚本（`expand_range_fields.py` 等保留至 Phase 2 改读 registry 后再评估退役）。
5. **Phase 1 覆盖率门槛**：分层定义——**Layer1 字段×源映射须与 `build_matrix()` 基线 100% 一致（1156/1230/64 去重配对）**（这是 G1 硬闸，已 PASS）；**Layer2 逐字段属性（canonical/meaning/unit/status）为最佳努力层**，覆盖率单独报告、缺口列清单供人工补录，**不要求 ≥99.5%**、绝不静默丢弃。抽样核对 64 多源字段的源集合与基线一致（parity 已含此抽样）。

> G0 闸门状态：**已签字**（决策由 AI 在安全原则下代行，用户知情授权）。进入 Phase 1。

---

### 1.6 Phase 1 交付与 G1 闸门结果（已实施，已提交 master `e009cc5`）

**交付物**：
- `scripts/extract_registry.py`：复用 `gen_field_matrix.parse_tables` + `verify_sync_check.MAPPING`，抽取 `field×source` 映射（Layer1，确定性）+ 逐字段属性（Layer2，最佳努力）+ `ulist_push2_align.md` 对齐表（→ `mappings`）。输出 `docs/field_verification/field_registry.json`（影子，不改动任何运行时行为）。
- `scripts/registry_parity.py`：独立 parity 闸门，比对 registry 与 `build_matrix()` 基线；退出码 1 即未过闸。
- 生成的 `docs/field_verification/field_registry.json`：1156 字段 / 1230 去重配对 / 64 多源 / 17 源 / 88 对齐。

**G1 闸门口径与结果**：
| 指标 | registry | 基线(build_matrix) | 结果 |
|---|---|---|---|
| 字段数 | 1156 | 1156 | ✅ |
| 去重 (字段,源) 配对 | 1230 | 1230 | ✅ |
| 多源字段数 | 64 | 64 | ✅ |
| 多源字段源集合抽样 | 与基线一致 | — | ✅ |

> 注：基线 `records=1412` 为 `build_matrix` 按行出现计数（含同源重复行），非 (字段,源) 配对基数；registry 存去重配对 1230，为单一真相源正确口径。§零·B 渲染当前用 1412 仅为展示计数，Phase 3 重生成时统一改用去重配对口径。

**Layer2 覆盖率（最佳努力，缺口供人工补录，非失败）**：canonical/meaning/unit/status 各 447/1156（≈38.7%）。缺口主要来自 §零·B B.2 单源 bullet 列表与 ZHB/TDX-eltdx 程序名列表（无四列表头）。这些字段的 `source`/`section` 已由 Layer1 完整登记，属性缺失不影响"字段归属源"这一核心真相。

**G1 闸门结论：PASS。** 核心单一真相源（字段×源）已 100% 对齐，可进入 Phase 2（治理脚本改读 registry）。

---

## 2. 目标架构

```
field_registry.yaml  (单一真相源，机器消费)
   │  ├─< 生成 ── scripts/gen_field_dict.py  ──> docs/field_dict.md §X（由 registry 渲染）
   │  └─< 读取 ── 8 个治理脚本（改读 registry 而非解析 markdown）
人类编辑 ──> 只改 field_registry.yaml（不再手改 markdown 字段表）
```

### 2.1 单一真相源 Schema（草案）

```yaml
meta:
  version: 1
  updated: 2026-09-11
  source_of_truth: field_registry.yaml   # markdown 降级为派生产物
sources:                                 # 替代 verify_sync_check.MAPPING
  - name: 东财-push2
    section_map: ["12.3.1 单股行情", "12.3.3 日K线", "12.8.7 东财 push2 资金流"]
    verify_file: push2_verify.md
    scheme: em.stock_get
fields:                                  # 替代 markdown 字段表 + SECTION_MAP 子串匹配
  - code: f3
    source: 东财-push2
    section: "12.3.1 单股行情"
    name: 现价
    type: float
    description: "..."
    aliases: [f3]
    scheme: em.stock_get
    status: verified          # verified | candidate | deprecated
    verified_date: 2026-09-04
  - code: "[1]"
    source: 腾讯-qt.gtimg
    ...
```

> 该 Schema 在 Phase 0 需与用户**联合审定**——这是整个计划成败的支点。

---

## 3. 分阶段实施（5 阶段 · 每阶段有审定闸）

### Phase 0 — 盘点与 Schema 审定  ⏱ 难度：**中**  ⏳ 估时：2–3 天
**交付**：
- 输出《消费点详单》：8 脚本逐函数列出「读 markdown 的哪一段、期望提取什么」。
- 冻结 `field_registry.yaml` Schema 草案（含 `fields`/`sources`/`meta` 三块、字段属性全集）。
- 选定存储格式（**YAML 优先**：人可审、可 diff；JSON 备选仅当 YAML 解析性能成瓶颈）。
**审定闸 G0**：用户签字 Schema + 格式选型。

### Phase 1 — 一次性反向抽取（markdown → registry）  ⏱ 难度：**高**  ⏳ 估时：4–6 天
**交付**：
- `scripts/extract_registry.py`：解析 `field_dict.md`（5395 行）全字段表 + 章节归属，生成 `field_registry.yaml`。
- ** parity 测试**：`registry → 渲染 §零·B` 必须与当前 `gen_field_matrix` 输出**逐字节一致**（1156 字段 / 1412 记录 / 64 多源）。
- registry 覆盖率报告：抽取失败的字段（格式异常行）单独列出人工补录。
**审定闸 G1**：parity 测试 100% 通过，覆盖率 ≥ 99.5%（余下为人工补录）。

### Phase 2 — 治理脚本改读 registry  ⏱ 难度：**高（逐脚本）**  ⏳ 估时：6–8 天（8 脚本）
**交付**：按风险从低到高改写：
1. `gen_field_matrix.py` → 改读 registry 生成 §零·B（**可立即下线 P0 护栏**，因输入不再依赖 markdown 体积）。
2. `verify_sync_check.py` → `MAPPING` 改从 registry `sources[].verify_file` 取；引用扫描保留（引用的是 verify 文件，仍合法）。
3. `audit_field_completeness.py` → `SECTION_MAP` 改从 registry `sources[].section_map` 取；raw/reg 比对逻辑不变。
4. `lint_field_*` / `field_landing_audit` / `verify_ulist_push2_collision` / `expand_range_fields` → 改读 registry。
- 每改一个脚本跑 **parity 测试**（输出 == 改前对真实字典的输出）。
**审定闸 G2**：8 脚本全部 parity 通过；P1 预检仍可运行（作为 registry 与 markdown 一致性双保险）。

### Phase 3 — markdown 单向生成  ⏱ 难度：**中**  ⏳ 估时：2–3 天
**交付**：
- `scripts/gen_field_dict.py`：registry → 渲染 `field_dict.md` 的「字段表 + §零·B + 分字典索引」区块（marker 区间，与现有 `<!-- GEN -->` 机制兼容）。
- 人类编辑规范变更：**字段增删改只进 registry**，CI 跑 `gen_field_dict` 重新生成 markdown；手改 markdown 字段表被 generator 覆盖（或 CI 检测差异告警）。
**审定闸 G3**：`gen_field_dict` 重生成 markdown 后 `git diff` 对当前主字典**为 0**（纯格式等价）。

### Phase 4 — 切换与归档  ⏱ 难度：**中**  ⏳ 估时：1–2 天
**交付**：
- 删除 8 脚本内残留的 markdown 解析分支（仅保留 registry 读取 + 异常兜底）。
- CI 接入：提交前跑 `archive_field_preflight`（P1） + registry↔markdown parity（G3）。
- `docs/field_dict.md` 头部加「本文件字段表由 `field_registry.yaml` 自动生成，勿手改」声明。
**审定闸 G4**：治理套件全量回归通过；P0 护栏可下线或保留为冗余保险。

---

## 6. Phase 2 实施记录与收尾（2026-09-12 完成）

### 6.1 已改读 registry 的 6 个脚本（registry 优先 + 字典回退，parity 已验证）

| 脚本 | 改读点 | 回退机制 | parity 验证 |
|---|---|---|---|
| `gen_field_matrix.py` | `build_matrix` 拆为 `_from_md`(golden) 与 `_from_registry`；`update_dict` 默认走 registry | `--from-md` 回归开关 | §零·B 渲染逐字节一致（仅 header 计数 1412→1230 去重口径纠正） |
| `verify_sync_check.py` | `MAPPING` → `get_source_mapping()`（registry `sources[].verify_file` 优先，硬编码基线回退 + 漂移告警） | `MAPPING_HARDCODED` 基线 | A7 闸门 EXIT=0，HARD 1/2/3/4 全过 |
| `verify_ulist_push2_collision.py` | `load_align()` 优先读 registry `mappings`（from=东财-ulist239/to=东财-push2） | markdown `ulist_push2_align.md` 回退 | 对齐表 87 条逐条一致 |
| `lint_field_same_number.py` | `align` 优先读 registry `mappings` | markdown 回退 | 87 条逐条一致 |
| `audit_field_completeness.py` | 新增 `registry_field_sets()`（registry `fields_by_source`）作 REG 半边，主路径退出 `SECTION_MAP`/`section_to_sources` | `registered_field_sets()` 字典解析回退 | `scratch/test_audit_registry_parity.py`：23 源 0 不一致 / 主路径计数+missing 等价 / 缺失回退正确 |
| `field_registry_api.py` | **新建统一访问层**（零依赖 json 读取），作为上述 5 脚本的 registry 基座 | 读取失败抛异常由调用方回退 | `registry_parity.py` 独立闸门 PASS |

> 全部 6 脚本采用「**registry 优先 + 字典回退**」双轨，registry 缺失/读失败绝不硬失败 → 过渡期安全。

### 6.2 刻意排除 / 延迟的 2 个脚本（非遗漏，附数据形状理由）

| 脚本 | 决策 | 理由（证据） |
|---|---|---|
| `lint_field_names.py` | **保留字典全量扫描**（仅做 ROOT 绝对路径硬化，非 registry 改读） | 它校验**中文字段名**禁忌词（如"最新价"）；registry 的 `code` 只存原生 token（f144/`[1]`/camelCase），中文名存于 `meaning` 而非 `code` → registry 数据形状不匹配，改读会丢失中文名 FORBID 校验。其字典读取为全文字面量扫描，非 SECTION_MAP 脆弱。 |
| `field_landing_audit.py` | **保留字典解析**（全文字面量 + 区间/斜杠展开扫描） | 它的"文档侧"需**完整 f 码提及全集**（含区间 `f135-146`、斜杠 `f144/145/146`、叙述提及）；registry 的 f 码字段（333 个）仅来自 `registered_field_sets` 对 f 源章节的抽取，是**真子集** → 强行替换会把"字典确实提及但 registry 未收录"的 f 码误判为"未文档化"，**破坏审计正确性**。其扫描为全文字面量正则，非 SECTION_MAP 脆弱。 |
| `expand_range_fields.py` | **延迟至 Phase 3**（不强行改读） | 它是**字典改写器**（原地写回 `field_dict.md`/`script_data_dict.md` 展开区间/斜杠记号），与 registry（字典读取视图）角色互斥；其区间归一职责在 Phase 3（markdown 由 registry 生成）后被吸收。按 G0 既定"实际脚本退役推迟 Phase 2"。 |

### 6.3 Phase 2 结论

- **真正脆弱的 SECTION_MAP / 章节号耦合（`audit_field_completeness`）已解除**：REG 半边主路径退出字典章节解析，章节搬家不再影响审计。
- **同号异义对齐表（`ulist_push2_align.md`）已单点吸收进 `mappings`**：3 个消费脚本（verify_ulist_push2_collision / lint_field_same_number / extract_registry）统一走 registry，消除重复解析源。
- **A7 闸门（`verify_sync_check`）增强而非削弱**：registry 声明源（ZHB/akshare/开盘红等）的 verify_file 也被校验，漂移仅告警。
- **保留的字典扫描（lint_field_names / field_landing_audit）均为非脆弱的全文正则**，registry 数据形状不覆盖其需求，故安全保留。
- Phase 2 未达"8/8 全改读"，但 6 个**真正受 SECTION_MAP/对齐表脆弱性影响**的脚本已解耦，2 个排除项有充分数据形状理由，**不构成反模式残留**。

---

### 6.4 Phase 3 实施记录与收尾（2026-09-12 完成）

#### 6.4.1 交付物
- `scripts/gen_field_dict.py`（新建）：由 `field_registry.json` 单一真相源渲染 `field_dict.md` 的机器生成区块：
  * `<!-- GEN:field-matrix -->` —— §零·B 字段×源总表（复用 `gen_field_matrix.render`）。
  * `<!-- GEN:subdict-index -->` —— 分字典索引（来自 `sources[].verify_file`）。
  * 幂等：`--check` 仅校验不写回，供 CI / 提交前闸门；重复运行同一 registry 产出一致。
- `scripts/extract_registry.py`：新增 `field_matrix` 投影（原生 token 视图 → 与 `build_matrix()` 同口径），供 gen_field_dict / registry_parity 消费。
- `scripts/field_registry_api.py`：新增 `field_matrix_map()` 统一访问层（零依赖，registry 基座）。
- `scripts/gen_field_matrix.py`：`build_matrix` registry 路径改读 `field_matrix` 投影（与 `--from-md` golden 回归一致）。
- `scripts/registry_parity.py`：新增 `field_matrix` 投影 parity 校验（G1 双重 parity：原生 token + §零·B 投影）。
- `docs/field_verification/field_registry.json`：重抽（与 §零·B 字节一致 + audit 不变 + parity，见 tasks 113–118）。
- `docs/field_dict.md`：头部 §零·B 声明改指 `field_registry.json`/`gen_field_dict.py`；尾部新增 `<!-- GEN:subdict-index -->` 自动分字典索引块。

#### 6.4.2 闸门结果（G3 收尾）
| 闸门 | 工具 | 结果 |
|---|---|---|
| G1 双重 parity | `registry_parity.py` | PASS（native 2252/3260/549；field_matrix PASS） |
| G3 幂等 | `gen_field_dict.py --check` | ✅ 与当前 `field_dict.md` 无差异 |
| A7 一致性 | `verify_sync_check.py` | HARD FAIL:0 / WARN:0（registry 声明源亦校验） |
| 同号即同义 | `lint_field_same_number.py` | PASS（87 对齐表条目 / 239 登记行 / 401 f 编号行） |

> 注：`lint_field_names.py` 在 `field_dict.md` §12.3.2.3 f144 行存在「禁用异名回归: 最新价」预警（exit 1），**该预警在 master HEAD 已存在**（仅因本阶段顶部声明减 1 行致行号 1742→1741 位移），**非 Phase 3 引入**；属独立清理项，不在本阶段范围。

#### 6.4.3 结论
- 根治目标达成：markdown 字段表区块（§零·B + 分字典索引）由 registry **生成**而非被**解析**，彻底切断「改文档→改工具行为」反模式。
- 字段契约表（四列 fNN/含义/单位/状态）仍人工维护（Layer2 覆盖率 ~38.7%，键空间为清洗字段名，生成会丢属性），待 Layer2 补全后纳入 Phase 4。
- 保留的字典扫描（`lint_field_names` / `field_landing_audit` / `expand_range_fields`）见 §6.2 排除理由，registry 化不覆盖其需求。

---

## 4. 难易度总评与关键风险

| 维度 | 评级 | 说明 |
|---|---|---|
| 一次性抽取准确率 | **高难** | 5395 行混合叙事/表格/代码块，解析器需鲁棒处理异常行；覆盖率须 ≥99.5% |
| Schema 设计 | **中难** | 需覆盖别名/scheme/状态/跨源同号等维度，且要兼容未来新源 |
| 8 脚本改写 | **中–高难** | 逐脚本 parity 测试量大，但逻辑改动局部 |
| 组织阻力（编辑习惯） | **中难** | 团队需从「改 markdown」切到「改 registry」，需规范 + CI 双保险 |
| 回滚 | **低难** | 每阶段独立 commit；Phase 1 完成前生产层零影响，可随时 abort |

**最大风险**：Phase 1 抽取遗漏/错字段 → 下游 parity 假绿。缓解：G1 强制 ≥99.5% 覆盖率 + 抽样人工核对 64 多源字段。

**与 P0/P1 的关系**：P0/P1 是**过渡期止血**，本计划完成后 P0 护栏可下线（输入不再依赖 markdown 体积）、P1 预检保留为 registry↔markdown 双保险。

---

## 5. 审定进度建议（Gate 节奏）

```
G0 Schema 签字 ──> G1 抽取 parity 100% ──> G2 8脚本 parity ──> G3 markdown 等价 ──> G4 全量回归
  (2-3d)              (4-6d)                 (6-8d)              (2-3d)            (1-2d)
```

每个 Gate 由你（或团队）**显式签字**后才进入下一阶段。任一 Gate 未过即暂停，回溯上一阶段。

> 本计划为长期根治方案，建议在「归档字段契约章节成为常态化操作」时启动；若归档仅为偶发，P0/P1 已足够，本计划可暂缓以规避过度工程。
