# AGENTS.md — Agent 行为规约(本仓库)

> 适用于:Windows 桌面版 Agent(原生执行 PowerShell)
> 适用范围:本仓库根目录及其全部子目录
> **静态上下文（按任务读取）**：`docs/PROJECT_CONTEXT.md` §0 是任务路由索引；常规任务只读对应权威文档和相关代码，字段破解不默认加载大体积 JSON。
> 日常采集与碰撞流程见 `docs/field_verification/DAILY_RUNBOOK.md`。字段语义、运行阈值、架构原则和 Agent 执行规约各有单独真源，发生冲突时先核对代码、测试及用户当前要求。
> 字段身份以 `field_registry.json` 的 `(source, 完整 code path)` 为准；先用生成的 `field_dict.md` / `unknown_fields.md` 导航，历史协议原文按需查 `field_source_reference.md`。
> 字段样本保留起点为 20261015：此前 `raw_*.json`、日期化 ZHB 压缩包及解析缓存已清理，采集、碰撞与审计不得回补或读取更早日期；少数被裁决材料引用的报告与元数据保留。
> 版本:v1.6（收敛架构、审查和排障规则；调查状态移至字段验证索引）

---

## 0. 环境确认(首次进入仓库必做)

在第一次执行任何命令前,先报告:

```powershell
$PSVersionTable.PSEdition
$PSVersionTable.PSVersion
Get-Command pwsh -ErrorAction SilentlyContinue
```

本仓库的预期环境:

- OS:Windows(原生 Agent,不在 WSL/容器中)
- Shell:Windows 原生 PowerShell；默认按 5.1 兼容。当前工作区已获用户明确授权使用 PowerShell 7，仍须保持脚本可由 5.1 解析。
- 路径:以本文件目录/`$PSScriptRoot` 为根，使用 Windows 盘符路径；禁止 `/mnt/c/...`。

若环境不同于默认值，仅在本工作区已明确批准的 PowerShell 7 例外内继续；其他差异先报告，不直接执行。

---

## 1. Shell 规则(硬性)

### 1.1 只用一种 Shell

- **只用 PowerShell**。禁止生成 `bash` / `zsh` / `cmd` / `bash -c` / `sh -c` 等一行块。
- **禁止嵌套** `powershell.exe -Command "..."` / `powershell -Command` / `pwsh -Command`。
- 同一任务里,路径要么全是 `C:\...`,要么全是 `/mnt/c/...`,**不能混用**。

### 1.2 复杂命令/中文输出必须落盘为 `.ps1`

凡是满足下面**任一条**,**必须**写到临时或仓库下的 `.ps1` 文件,然后 `& .\.ps1` 或 `pwsh -File`:

- 多层引号(`"..."` 里套 `'...'` 里套 `"..."`)
- 包含 JSON / 正则 / Here-String
- 多步判断或循环
- 命令行 > 120 字符
- **输出含中文**(含调试模式 `Select-String 读文件→Out-File→Get-Content` 等)——PowerShell
  原生输出按系统代码页(GBK)写字节,opencode 按 UTF-8 解码必乱码(2026-08-12 实测),
  落盘后由四行头部强制 UTF-8;或改用 Python 探针(项目已统一 `ensure_utf8_stdio`,输出天然 UTF-8)

**V16.4.1 管道禁令(2026-08-12 二度实测根因)**: **禁止把 python 输出接 PowerShell 管道**
(`python.exe ... | Select-Object` / `| Out-File | Get-Content` 等)——PS 5.1 对原生进程
多字节 UTF-8 流的分块解码有缺陷,会破坏部分字符(行首「/行尾字变 �),**与 python 输出
本身无关**(无管道直跑 100% 正常)。需要截断/存文件时:
  - 截断:在 python 脚本内部控制(print 前切片),或直接无管道跑(opencode 超长自动落盘)
  - 存文件:python 脚本自己写文件(open(..., encoding="utf-8")),**不要用 Out-File 中转**

唯一例外——**无中文输出**的简单单行命令(`chcp`/`git status`/`Test-Path` 等)可直接执行。

`.ps1` 开头固定四行(V16.4.1:后两行为 UTF-8 强制——opencode/Codex 子进程
**不加载 Profile**,系统代码页 936(GBK) 时 PowerShell 原生输出乱码;实测
会话内设置编码后输出即恢复):

```powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding
```

> **V16.4.1 BOM 铁律(实测根因)**: `.ps1` 文件必须是 **UTF-8 with BOM**。
> Windows PowerShell 5.1 对无 BOM 文件按 ANSI(GBK) 解析 → 文件内中文字面量
> 在解析时即乱码(输出必然乱码,运行时设编码也救不回)。opencode/Codex 的
> edit/write 写的是无 BOM UTF-8 —— **凡工具修改过 .ps1,必须重写为带 BOM**:
>
> ```powershell
> $c = [System.IO.File]::ReadAllText($p, [System.Text.Encoding]::UTF8)
> [System.IO.File]::WriteAllText($p, $c, (New-Object System.Text.UTF8Encoding($true)))
> ```
>
> 校验:`Format-Hex` 头三字节应为 `EF BB BF`。`.py` 文件不受影响(Python 3 源
> 文件默认 UTF-8,不依赖 BOM)。

**禁止**为绕开脚本而全局放宽 `ExecutionPolicy`;如需执行,用
`powershell -ExecutionPolicy Bypass -File .\xxx.ps1` 单次放行。

> 校验:若临时脚本输出中文仍乱码,检查 .ps1 是否被 edit 工具重写丢 BOM
> (见上文 BOM 铁律)。

### 1.3 路径

- 一律 `Join-Path` 或 `-LiteralPath`,不用 `-Path`(避免 `[` `]` `&` `空格` 被通配)
- 测试路径:`Test-Path -LiteralPath $path`
- 读文件:`Get-Content -Raw -LiteralPath $path`
- 路径拼接示例:

  ```powershell
  $root = Join-Path $PSScriptRoot 'docs'
  $file = Join-Path $root 'backtest_v1432\backtest_summary.csv'
  ```

- 项目内临时目录统一为仓库根 `.tmp/`；临时探针、下载包、临时虚拟环境和测试基目录都放在此目录下，不使用系统 `%TEMP%`。
- `scripts/run_with_system_python.ps1` 会为 Python 进程及其子进程设置 `TEMP`、`TMP`、`TMPDIR` 到 `.tmp/`；测试通过 `scripts/run_tests.ps1` 进入该启动器。旧 `.bat` 兼容入口也使用 `.tmp/`。
- `.tmp/` 整个目录被 Git 忽略；启动器或项目代码会在运行时按需创建。清理时只删除本任务创建的明确路径。

### 1.4 环境变量

- 读取:`$env:NAME`,不用 `Getenv("NAME")` 这种伪语法
- 设置:`$env:NAME = 'value'`,作用域仅当前会话
- 写入永久值:**禁止**(改 `.env`/配置文件由用户/项目主管控)

### 1.5 外部程序(`git`、`npm`、`python`、`py`、`curl`、`docker` 等)

- **必须**写全名(`curl.exe`、`python.exe`、`git.exe`),避免撞 alias
- **必须**使用 splatting,不靠字符串拼:
  ```powershell
  $gitArgs = @('status','--short')
  & git @gitArgs
  ```
- **必须**检查 `$LASTEXITCODE`;非零立即停止并把 stderr 上报,不要吞错
- `$LASTEXITCODE` 仅在直接执行外部程序后读取；若经过 PowerShell 管道或需要捕获退出码，使用 `System.Diagnostics.Process.ExitCode`。
- PowerShell 5.1 **没有** `&&` / `||`;`$LASTEXITCODE` 是唯一可靠的依赖手段

### 1.6 错误处理

- **不要** 把 `try { } catch { }` 当"什么都不做"用(`catch {}` 是吞错黑洞)
- 抛出:`throw`
- 捕获后重抛:`throw $_`
- 真要降级:在 catch 体里写明原因并 `Write-Warning`,再走兜底逻辑

### 1.7 重复错误的处置

同一类错误重试 > 2 次仍然失败 → **停止重试**,按以下顺序汇报:

1. 报错命令原文(不含转义噪声)
2. `Get-Error` 的 Exception 名前两段
3. 一份最小复现(`xx.ps1` + 输入)
4. 已尝试的 2 种修法

**绝不**一边报错一边继续叠加 `2>&1 | Out-String` / `Start-Process -Wait` / `cmd /c` 之类的转义层。

---

## 2. 任务分类与执行路径

- Windows/Python 任务使用原生 PowerShell；只有确需 Linux-only 工具时才考虑 WSL，并先说明原因。
- 任务文档按 `docs/PROJECT_CONTEXT.md` §0 路由；采集与碰撞按 `docs/field_verification/DAILY_RUNBOOK.md`。

### 2.1 测试

- 测试代码可以正常 `import pytest`；测试文件放在 `tests/test_*.py`，marker 先登记在 `pyproject.toml`。
- 真实网络测试必须标记 `real_network`；默认离线测试会拦截或排除它们。未经用户明确要求，不主动发真实网络测试请求。
- Agent/CI 运行测试统一使用 `scripts/run_tests.ps1`；禁止从 Shell 直接调用 `pytest` 或 `python -m pytest`。解释器由 `scripts/run_with_system_python.ps1` 选择，优先 Python 3.12。
- 模式、模块定位和排错方式见 [`tests/README.md`](tests/README.md)。

### 2.2 外部程序

使用完整可执行文件名和参数数组；依赖前一步结果的命令必须检查退出码。详细规则见 §1.5。

---

## 3. Agent 调用模板

不需每轮复制通用模板。先按 §0 确定相关上下文；运行采集/碰撞时按 `DAILY_RUNBOOK.md` 逐步核对日期、状态和结果。

---

## 4. Shell 规则验收

不在每项任务中重复运行环境验收样例；仅在 Shell、编码或执行环境变更后验证。日常操作遵从 §1 与 §5。

---

## 5. 速查

| 约束 | 执行方式 |
|---|---|
| 路径含通配符/空格 | `Join-Path`、`-LiteralPath` |
| 复杂命令或中文 PowerShell 输出 | 落盘 `.ps1`；固定 UTF-8 头部，UTF-8 BOM |
| Python 输出含中文 | 用 Python 探针并直接运行；禁止接 PowerShell 管道 |
| 外部程序 | 完整 `.exe` 名、参数数组/splatting；检查退出码 |
| 临时文件 | 仓库根 `.tmp/`；只清理本任务创建的明确路径 |
| pytest | `scripts/run_tests.ps1`；不从 Shell 直跑 pytest |
| 兼容性 | PowerShell 7 是当前工作区批准例外；仍写 PowerShell 5.1 兼容语法 |

---

## 6. 例外与豁免

当前工作区已由用户明确允许 PowerShell 7；该例外只放宽执行宿主，不放宽语法兼容、路径、编码或退出码规则。其他豁免须有当次明确授权，并在回复中说明原因。

---

## 7. 自检清单

- [ ] PowerShell 原生执行，路径使用 Windows 盘符与 `-LiteralPath`。
- [ ] 复杂命令按 §1.2 落盘；`.ps1` 为带 BOM 的 UTF-8；无 Python→PowerShell 管道。
- [ ] 临时产物位于 `.tmp/`；外部程序使用完整名称并检查退出码。
- [ ] 测试运行走 `scripts/run_tests.ps1`；真实网络仅在用户明确授权时运行。
- [ ] 代码改动完成后按 §9 验证；文档改动检查链接、规则一致性和 diff。

---

## 8. 修改前置事实门 (Fact-Forcing Gate / gateguard)

> 来源: ECC (github.com/affaan-m/ECC) 提炼。目的: 防止"未调查就改代码"导致的字段映射错误、死代码、漏改调用方。

### 8.1 强制规则

**首次 Edit/Write 某个文件前,必须先调查并在回复中列出:**

1. **导入者**: 谁 `import` 了这个文件/函数?(用 Python 探针或 `Select-String -Pattern "import X"` 全仓扫描)
2. **调用方**: 该函数被哪些脚本/模块调用?(同上扫描函数名)
3. **数据契约**: 返回 dict 的 key、dataclass 字段、ZHB 列索引、SQLite Key 格式
4. **缓存影响**: 是否影响 `report_date` 事件锁 / 缓存 Key 约定
5. **测试影响**: 改动是否会破坏 `tests/` 现有用例

**判定**: 这 5 项回答完毕后,才允许动手改文件。做不到 → 不写。

### 8.2 高风险文件清单(改前必查)

> 通用术语以 `docs/domain_glossary.md` 为准；字段语义、来源路由和新鲜度不得由术语表推定。

| 文件 | 改前必查项 |
|---|---|
| `stock_common/sc_datasource/` | 专项字段映射、缓存键和公开适配器；检查调用方与相关测试 |
| `core/tdx_client.py` | 0x0010 协议字段名、统一 TDX 适配器输出 key、限流边界 |
| `core/zhb_client.py` | 日期化缓存文件 `zhb_YYYYMMDD.zip` 的文件名是数据日期；检查包内日期冲突和解析器测试 |
| `core/data_provider.py` | 字段路由、交易日历、新鲜度、来源优先级和逐字段有效日期；以实际调用路径为准 |
| `stock_common/__init__.py` | 对外导出及调用兼容性；检查实际定义、消费者和测试 |
| `docs/field_verification/field_registry.json` | 逐源状态以 `source_fields` 中 `(source, 完整 code path)` 为准；`docs/unknown_fields.md` 是生成队列，旧 ZHB/ulist 列索引见只读归档 `docs/field_source_reference.md` |

> `REQUIRES_REALTIME_HTTP` / `ZHB_SUFFICIENT` 从 `sc_schema.FIELD_SPECS` 派生，是测试契约元数据；不能将其误当作运行时路由开关或未使用死代码。修改路由时，沿 `get_canonical_stock_data()` 的实际调用链和测试核查，并将当前路由细节留在代码及架构说明中，不在本规约复制行号和易变阈值。
>
> 日期化 ZHB 缓存的文件名日期优先于包内 `tdxstat.cfg` 日期；采集 JSON 的 `zhb_date` 是解析结果副本。通用无日期下载包的解析回退见 `core/zhb_client.py` 和 `tests/data/test_data_zhb.py`。

### 8.3 字段/签名变更时的连带检查

若改动涉及外部可见的 dict key、函数签名或返回结构，必须：
- 找到并更新该契约的所有调用点、消费者和测试。
- 若变更的是字段来源身份/完整路径，更新 `field_registry.json.source_fields`，重跑字段视图生成器并通过 parity；其他契约变更更新其实际权威文档/Schema。
- 检查缓存序列化、缓存键和事件锁是否受影响；仅在语义或缓存口径变化时升级相应版本。

### 8.4 统一数据访问

架构原则以 [`docs/ARCHITECTURE_THEORY.md`](docs/ARCHITECTURE_THEORY.md) 为准；模块与调用边界见 [`docs/architecture.md`](docs/architecture.md)。生产报告和采集脚本必须通过 Tier 1 或 Tier 2 公开适配器取数。原始客户端只允许在 `stock_common/` 与 `core/tdx_client.py` 内部使用。

适用的自动闸门：

```powershell
python.exe scripts/verify_data_access.py
python.exe scripts/verify_sync_check.py
python.exe scripts/verify_canonical_contract.py
```

若当前设计原则不再适用，先修订原则及依赖闸门；只有确认仍适用而实现选择偏离时，才登记到 `docs/DEBT_LEDGER.md`。OPEN 条数是当前状态快照，新发现的问题不得为追求下降而隐去。

---
## 9. 验证循环 (Verification Loop)

> 来源: ECC `verification-loop` skill 提炼,适配本仓库(纯 Python + PowerShell)。每次代码修改完成后、提交前运行。

### 9.1 验证入口与局部回归

| 检查 | 命令(全部 PowerShell 语法) | 通过标准 |
|---|---|---|
| 完整验收 | `.\scripts\run_offline_checks.ps1` | 语法、全项目 Mypy、Black API、AxData 摘要、架构闸门及离线测试全部通过 |
| 局部回归 | `.\scripts\run_tests.ps1 -Mode module -Path <测试文件>` | 相关用例通过；真实网络仍排除 |
| 安全 | 对改动代码执行密钥模式扫描并检查配置读写 | 无硬编码密钥或意外敏感数据 |
| Diff | `git.exe diff --stat` | 改动与任务范围一致 |

> 提交前必须运行完整离线验收。该入口通过 Black Python API 按 `pyproject.toml` 配置检查 Git 可见 Python 文件，避免 Windows 下 `black --check` 曾出现的长时间无输出；真实网络测试不会启动。局部回归可先运行单模块，但不能替代提交前完整验收。

### 9.2 验证结果记录

按改动范围说明实际执行的检查与结果；有可靠基线且与改动相关时报告前后指标，不造指标。纯文档改动说明检查的链接/规则范围及行数变化。跨模块代码改动或用户要求完整审查时，使用以下结构：

```text
VERIFICATION REPORT
==================
语法:     [PASS/FAIL]
类型:     [PASS/FAIL] (X errors)
格式:     [PASS/FAIL]
测试:     [PASS/FAIL] (X/Y passed)
安全:     [PASS/FAIL] (X issues)
Diff:     [X files changed]
度量:     [相关指标: 改前 → 改后；无可靠基线时说明原因]

Overall:  [READY/NOT READY] for commit
待修复:
1. ...
```

### 9.3 触发时机

- 每个功能/修复完成后
- 重构后
- 提交前(强制)
- 任何一次跨多个文件的改动后

---

## 10. 审查流程 (Code Review)

> 来源: ECC `code-review` / `python-reviewer` 提炼。代码改动后、提交前,用 `/review` 命令或手动执行。

### 10.1 严重级别

| 级别 | 含义 | 处理 |
|---|---|---|
| **CRITICAL** | 安全漏洞 / 数据丢失风险 | **阻塞** — 必须修复 |
| **HIGH** | Bug / 重大质量问题 | **警告** — 应修复 |
| **MEDIUM** | 可维护性问题 | **提示** — 考虑修复 |
| **LOW** | 风格/小建议 | **可选** |

### 10.2 必查清单

> V1.1 双轴审查(mattpocock/skills `code-review` 提炼): **Standards 轴**(代码质量) + **Spec 轴**(实现意图)。
> 两轴分开核查,避免"代码写得漂亮但做错了需求"。

**Standards 轴(代码质量)**:

- [ ] 无硬编码密钥/凭据(重点: `credentials.json` 不得进 git)
- [ ] 无 SQL 注入(f-string 拼查询)
- [ ] 无裸 `except` / 吞异常
- [ ] 关注函数复杂度；按可读性与复用边界决定是否拆分，不设硬性行数门槛
- [ ] 公开函数有类型注解
- [ ] 无可变默认参数 `def f(x=[])`
- [ ] 共享状态有锁(参考 `sc_network._EM_LAST_CALL` / `_DOMAIN_LAST_TIME`)
- [ ] 库代码用项目日志；命令行面向用户的输出允许使用 `print()`
- [ ] 新增功能有对应测试

**Spec 轴(实现意图)**:

- [ ] 对照原始需求/用户指令,确认改动**确实实现了要求**(而非自创方案)
- [ ] 对照 `docs/ARCHITECTURE_THEORY.md`、`docs/domain_glossary.md` 与用户当前要求确认口径；历史版本计划不作为当前规格。
- [ ] 涉及字段契约的改动,对照 `field_registry.json.source_fields`、生成的 `unknown_fields.md`、相关来源证据和 `script_data_dict.md`；`field_source_reference.md` 仅作历史协议参考
- [ ] 涉及缓存,确认 key、TTL、日期边界与失效策略符合当前契约；只有缓存语义变化时才调整版本或类别

### 10.3 审批标准

- **Approve**: 无 CRITICAL / HIGH
- **Warning**: 仅 MEDIUM(谨慎合入)
- **Block**: 有 CRITICAL / HIGH

---

## 11. 排障与结果记录

### 11.1 证据与度量

- 排查问题时先核对症状、数据流和相关契约；对不确定原因提出可证伪解释，并尽量一次只改变一个变量。
- 实验不支持假设时，记录结论并检查下一个可能原因；无需机械地为每个问题创建最小复现。
- 对性能、正确性或可靠性有明确基线的改动，报告相关改前/改后指标；不要为了满足格式制造指标。纯文档改动报告受影响范围及实际检查。
- 已完成的行为变更写入 `CHANGELOG.md`，不在路线图或多个索引重复记录。

### 11.2 修复验证

- 根据改动范围执行 `AGENTS.md` §9 中适用的检查，并在回复中说明证据、结果和未解决的限制。
- 修复未解决问题时，回到症状和证据重新判断；遵守 §1.7 的同类错误重试限制，不因固定计时门槛提前放弃尚可推进的工作。

---

## 12. 活跃调查

当前字段调查和待核来源以 [`docs/field_verification/README.md`](docs/field_verification/README.md) 的调查计划及其专项记录为准；不要在执行规约重复维护字段状态或证据摘要。
