# AGENTS.md — Agent 行为规约(本仓库)

> 适用于:Windows 桌面版 Agent(原生执行 PowerShell)
> 适用范围:本仓库根目录及其全部子目录
> **静态上下文（按任务分层读取）**：`docs/PROJECT_CONTEXT.md` §0 是任务路由索引；常规任务只读相关热区，字段破解不默认加载整份方法论文档或大体积 JSON。
> 🔥热区：本文件 §5；🌤️温区：任务所需章节；🧊冷区：只在遇到具体候选/问题时按路径取证。日常采集与碰撞流程见 `docs/field_verification/DAILY_RUNBOOK.md`。
> 字段身份以 `field_registry.json` 的 `(source, 完整 code path)` 为准；先用生成的 `field_dict.md` / `unknown_fields.md` 导航，历史协议原文按需查 `field_source_reference.md`。
> 版本:v1.3（压缩重复常驻规则，保留原有数据安全约束）

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

> 术语口径以 `docs/domain_glossary.md`(领域词汇表)为准,命名/注释不得引入新歧义。

| 文件 | 改前必查项 |
|---|---|
| `sc_datasource.py` | ZHB 列索引映射、35 个未知字段、缓存 Key |
| `tdx_client.py` | 0x0010 协议字段名、统一 TDX 适配器输出 key、限流间隔 |
| `zhb_client.py` | 各解析器列映射、GBK/分隔符约定 |
| `data_provider.py` | **字段路由与元数据真机制**（见下方注记）：交易时段/交易日历、`need_realtime_quote`、ZHB ABCD 字段新鲜度、逐字段来源与有效日期 |
| `stock_common/__init__.py` | 导出是否与实际定义一致(2026-08-10 审计:`__all__` 241 项全部可访问,0 缺失;少数公共函数如 `get_em_quote_full` 未在 `__all__` 重导出,但调用方均直连子模块,无破坏) |
| `docs/field_verification/field_registry.json` | 逐源状态以 `source_fields` 中 `(source, 完整 code path)` 为准；`docs/unknown_fields.md` 是生成队列，旧 ZHB/ulist 列索引见只读归档 `docs/field_source_reference.md` |

> **⚠️ 注记（2026-08-30 校正）：`REQUIRES_REALTIME_HTTP` / `ZHB_SUFFICIENT` 不控制运行时路由**
>
> 旧版本节曾把这两个集合列为 "改前必查项"，会误导——它们**不参与任何运行时分支决策**。现状：
> - **定义**：`data_provider.py:180-260` 从 `sc_schema.FIELD_SPECS.is_real_time` 动态生成（单一权威源在 sc_schema）。
> - **消费方**：仅 `tests/core/test_core_routing.py`（14 例）与 `test_core_schema.py` 通过
>   `is_realtime_http_field()` / `is_zhb_sufficient_field()` 查询——**业务代码零调用**（全仓 grep 证实）。
> - **因此它们是"测试契约元数据"而非死代码**：删除会破坏 14 个回归用例，**禁止删除**。
> - **真正决定走 ZHB 还是 HTTP 的机制**：
>   1. `_should_use_zhb_for_realtime()` 根据交易日历与 9:30 分界处理盘前、休市日、盘中和盘后。
>   2. `get_canonical_stock_data` 的 `need_realtime_quote` 综合强制实时、时段、ZHB 快照是否存在及 A 类行情字段是否过期。
>   3. `sc_datasource.zhb_field_safe(field)` 使用明确的 ZHB 包日期，按 A/B/C/D 交易日延迟过滤：A 实时 `=0`／B 准实时 `=1`／C 日频 `=3`／D 静态 `=90`。
>   4. `CanonicalStockData.quote_date` 与 `time_anchor` 依据价格字段的有效日期；日期未知则 `time_anchor="unknown"`。`collected_at` 是本机组装时间，不能作为上游有效日期。逐字段日期见 `field_as_of_dates`。
>   5. TDX 行情缓存日期使用 `latest_market_data_date()`，不能按自然日把周末/节假日当作有效行情日。
> - 改路由行为时检查以上路径；改字段的"是否实时"分类请动 `sc_schema.FIELD_SPECS`（会同步测试契约集合）。

### 8.3 字段/签名变更时的连带检查

若改动涉及 **dict key / 函数签名 / 返回结构** 变更,必须:
- 找到并更新**所有**调用点(不允许只改定义)
- 更新 `docs/field_verification/field_registry.json.source_fields` 中的逐源完整路径与证据；重跑 `gen_field_dict.py`、`gen_field_matrix.py` 并通过 parity。`docs/field_dict.md` 是生成入口，`field_source_reference.md` 是不可覆盖的历史归档。
- 检查是否有缓存反序列化依赖旧 key

### 8.4 统一层与数据访问收口 (2026-09-03 新增)

> **理论层权威文档: `docs/ARCHITECTURE_THEORY.md`(架构公理 A1–A8)**
> **偏离台账: `docs/DEBT_LEDGER.md`**
> 本节是操作速查;完整论证与"为什么"见上述两个文件。

**统一层 = 两层网关**(不是一个大对象):

| 层 | 入口 | 职责 |
|---|---|---|
| **Tier1 门面** | `core/data_provider.get_canonical_stock_data()` | `CanonicalStockData` 115 个属性（含 12 个 ELTDX 扩展属性）、源选择、fallback、单位归一化、逐字段来源和有效日期溯源 |
| **Tier2 适配器** | `sc_datasource.get_*` / `sc_fuyao.get_fuyao_*` / `tdx_client.tdx_get_*` | 专精数据(CYQ / F10 / 涨停梯队 / 龙虎榜 / 行业L2 / 宏观流向 / 竞价),已含 @cached + 归一化 + 令牌桶限流 |
| **原始客户端** | `_get_tdx_client()` / `sc_network.em_get` / `sc_fuyao._fuyao_raw` / 裸 requests·httpx | **仅允许出现在 `stock_common/` 与 `core/tdx_client.py` 内部** |

**铁律(公理 A1)**:生产脚本(`main.py` / `get_*_report.py` / `sc_report_runner.py` / `core/*.py`)
取数必须先经过 Tier1 或 Tier2 的**公开函数**,禁止直连原始客户端。

> **⚠️ 不要把专精数据塞进 `CanonicalStockData`** —— 会造成 god-object,
> 且让 fallback 一致性更难做(而这正是统一层要解决的原始问题)。
> **Tier2 适配器本身就是统一层的"专精面"**,调用它不等于绕过统一层。

**自动化闸门**(提交前必跑):

```powershell
python.exe scripts\verify_data_access.py     # 公理 A1: 数据访问收口(禁止生产脚本直连原始客户端)
python.exe scripts\verify_sync_check.py      # 公理 A7: 字典 ↔ 代码 同步
python.exe scripts\verify_canonical_contract.py  # Tier 1: 属性、日期、来源与缓存边界
```

> 闸门已用 `tokenize` 剥离注释与字符串,故文档中引用违规符号的说明性注释不会误报。

**🔴 禁止静默迁就(公理 A8,元公理)**:
明知违反公理,却因"改动大 / 风险高"而不改、**也不记账** —— 这是最严重的违规,
也是本仓库历史上多轮修改累积混乱的唯一成因。必须二选一:

1. **按公理改**(哪怕改动面扩大);或
2. **在 `docs/DEBT_LEDGER.md` 登记偏离** —— 写明**真实技术原因**(要动哪些消费方/测试、
   缺什么验证手段)与偿还计划。禁止写"风险大""暂缓"这类无信息量的措辞。

> 判断标准:债务台账的 OPEN 条目数应**单调下降**。
> 显式债务是可偿还的,隐形债务是不可理解的。

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

### 9.2 验证报告格式

完成六阶段后,输出:

```text
VERIFICATION REPORT
==================
语法:     [PASS/FAIL]
类型:     [PASS/FAIL] (X errors)
格式:     [PASS/FAIL]
测试:     [PASS/FAIL] (X/Y passed)
安全:     [PASS/FAIL] (X issues)
Diff:     [X files changed]
度量:     [Metric] (改动前后对比,见 11.1)

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
- [ ] 函数 < 50 行,嵌套 < 4 层
- [ ] 公开函数有类型注解
- [ ] 无可变默认参数 `def f(x=[])`
- [ ] 共享状态有锁(参考 `sc_network._EM_LAST_CALL` / `_DOMAIN_LAST_TIME`)
- [ ] 无 `print()`(应 `_debug_log` / `logging`)
- [ ] 新增功能有对应测试

**Spec 轴(实现意图)**:

- [ ] 对照原始需求/用户指令,确认改动**确实实现了要求**(而非自创方案)
- [ ] 对照 `docs/roadmap.md` 最近决策记录(ADR),确认口径/约定一致(如行业统一申万二级)
- [ ] 对照 `docs/domain_glossary.md` 术语,确认命名/注释未引入新歧义
- [ ] 涉及数据契约的改动,对照 `field_registry.json.source_fields`、`unknown_fields.md`、`field_source_reference.md` / `script_data_dict.md`
- [ ] 涉及缓存,确认缓存版本号(§4)已按口径变更升级

### 10.3 审批标准

- **Approve**: 无 CRITICAL / HIGH
- **Warning**: 仅 MEDIUM(谨慎合入)
- **Block**: 有 CRITICAL / HIGH

---

## 11. 迭代度量与假设驱动调试 (Autoresearch 纪律)

> 来源: uditgoenka/autoresearch v2.2 (github.com/uditgoenka/autoresearch, MIT) 提炼,源自 Karpathy's autoresearch。
> 采纳范围:**仅方法论**(方案 A),不引入其命令/钩子/脚本——安装脚本为 bash 且与 1.1 节 Shell 规则冲突,
> 其"commit before verify"与"未经用户要求不 commit"的仓库政策冲突,故不采纳。

### 11.1 迭代度量 (Iteration Metric) — 每次改动必须量化

**原则**: 一次改动必须绑定至少一个**可数的机械指标**,改动前后对比,不能只说"看起来更好"。

| 场景 | 可选度量(取最容易量化的 1-2 个) |
|---|---|
| 代码修复 | 测试通过数 X/Y、耗时(如 78s)、失败数变化 |
| 网络/限流 | 封禁次数、429 次数、平均响应延迟、成功率 |
| 数据正确性 | 字段匹配条数(如分红 19 条)、错误报告数、偏差值(如 PE 18337420x→5.82x) |
| 性能 | 总耗时(如 1000s→620s)、请求数、缓存命中率 |

**执行要求**:

- 改动完成后的验证报告(9.2)必须填 `度量` 行,格式 `指标: 改前 → 改后`
- 无法量化时,写明理由(如"纯文档改动"),不得省略
- roadmap 每次版本条目建议带度量(如"V16.2.12: 警告 17 条 → 0 条")

### 11.2 假设驱动调试流程 (Hypothesis-Driven Debug)

排查疑难 bug 时按以下顺序,**每个假设只做一次实验**,禁止盲目堆叠修法:

1. **收集症状**: 报错原文、复现命令、现象(如"K线空但无报错")
2. **最小化复现**: 缩小到最小输入/最小脚本(mattpocock `diagnosing-bugs` 提炼)——
   去掉无关股票/字段/分支,确认在最小集上仍可复现;不可复现 → 说明症状与疑似面无关,先排查最小集差异
3. **侦察**: 读相关代码路径 + 检查数据(如实测返回的原始值),先找"数据在哪一层失真"
4. **提出假设**: 必须具体、可检验(如"push2 封禁是连接级而非请求级"),写成"若 X 则 Y"
5. **单次实验**: 一次只验证一个假设(最小复现脚本/加日志/抓包),禁止同时改多处
6. **判定**: 证实 → 修复;证伪 → 记录并排除,换下一个假设
7. **记录**: 在回复中列出 假设/实验/结论 三行,证伪的同样记录(防重复踩坑)

**硬约束**:

- 假设未证实前**不得改业务代码**(可写临时复现脚本)
- 每个假设耗时 > 15 分钟仍无结论 → 停止,汇报当前证据 + 剩余候选,不闷头继续
- 与 1.7 节(同一错误重试 > 2 次停止)联动:修复失败回到"提出新假设"而非"再试一次"

---

## 12. 活跃待办(每次会话先检查)

> 完成一项即删除对应条目;新会话开始时必须先看本节。

### 12.1 ⏳ 东财 push2 多主机字段差异复核

- 2026-08-12 的历史健康探测曾记录 6/6 主机或接口可用；之后确认“失败不重试 + 域级熔断”已修复重复请求导致二次封禁的问题。该历史结果不代表当前主机健康。
- **待办**：在用户明确安排真实网络核验后，用低频、逐主机样本比较字段集合、数值、来源日期和响应状态；先验证备用域，再决定是否触达敏感 push2 主域。首个 403、429、封禁或熔断迹象即停止该风险族；不运行 `--all`。健康探测只证明端点可达，不代替字段等价性核验。

### 12.2 ⏳ ulist239 `f107` / `f118` 来源路径语义待核

- **逐路径现状**：`push2(stock/get)::f107` 与 `::f118` 已在主注册表标为 verified；`ulist239(np/get)::f107` 与 `::f118` 的含义、单位为空，状态为 `unverified` / `aggregate_status_scope_unresolved`。全局聚合状态来自 push2 证据，不能直接复制为 ulist239 的字段语义。
- 生成队列仍列出两条 ulist239 待核记录；本轮未改注册表、主字典或采集路由。
- **待办**：按 [`docs/field_verification/f118_ulist_source_semantics_plan.md`](docs/field_verification/f118_ulist_source_semantics_plan.md) 对照每个接口的原始样本、有效日期和公开契约；区分“字段身份映射”“字段语义”和“接口占位/空值”。只有证据满足裁决流程后，才更新逐源记录及生成视图。
