# AGENTS.md — Agent 行为规约(本仓库)

> 适用于:Windows 桌面版 Agent(原生执行 PowerShell)
> 适用范围:本仓库根目录及其全部子目录
> **静态上下文(分层按需读取, 减少重复探索)**: docs/PROJECT_CONTEXT.md——含§0 指引目录(任务类型→热/温/冷区读取清单);
> 🔥热区=AGENTS.md+§5 约束(每次必读); 🌤️温区=任务相关章节; 🧊冷区=仅任务需要时读对应文件;
> 字段类动态细节查 field_dict/script_data_dict(冷区按需)
> 版本:v1.2(V16.4.1 重构:合并落盘规则、清理过时内容与已完成待办)

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
- Shell:**Windows PowerShell 5.1**(Desktop edition)
- 仓库路径:项目根目录(即本文件所在目录,用 `$PSScriptRoot` 获取;Windows 文件系统,统一使用 `C:\...`,**禁止** `/mnt/c/...`)
- 不需要 `pwsh`;若检测到 PowerShell 7,仍按 PowerShell 兼容语法编写

如果实际环境与上述不符,**先停手报差异**,不直接执行。

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

| 场景 | Shell | 路径 | 备注 |
|---|---|---|---|
| Windows/.NET / Python / 原生 Python 工具链 | **PowerShell** | `C:\...` | 本仓库默认 |
| Bash / Docker / Linux-only 工具链 | WSL2 | `/mnt/c/...` | 仅当项目确实需要才切,需先告知用户 |

只跑 Python 项目时,**不切 WSL**,保持原生 Agent。

### 2.1 测试(pytest 是 Python 库,不是 shell 命令)

pytest 作为 **Python 第三方库**(通过 `pip install pytest` 安装)的用法跟 shell 完全无关。
在写测试代码 / 在 IDE 里运行时,可以并且应该直接 import。下面把"测试代码"和"测试运行"分清楚。

#### 2.1.1 测试代码(写代码时,正常 import 即可)

✅ **应当且必须**使用 pytest 的 Python API:

```python
import pytest                       # 库 API,跟 shell 调用无关
from pytest import approx           # 用于浮点容差比较
import pytest_asyncio               # 异步测试

@pytest.fixture                     # 装饰器,Python 语言特性
def tmp_project(tmp_path): ...

@pytest.mark.real_network           # 自定义 marker,已在 conftest.py 注册
def test_em_endpoint(endpoint): ...

@pytest.mark.parametrize('a,b,exp', [(1,1,2),(2,3,5)])
def test_add(a, b, exp): ...

def test_raises():
    with pytest.raises(ValueError):
        int('not a number')

def test_skip():
    if not network_up():
        pytest.skip('no network')

def test_approx():
    assert 0.1 + 0.2 == approx(0.3)
```

使用范围(本仓库现状):

- 17 个测试文件已在 `tests/` 跑通(含 `@pytest.fixture`、`@pytest.mark.real_network`、`pytest.skip`、`pytest_asyncio` 等)
- `tests/conftest.py` 提供 `_no_real_network` autouse fixture 和 `endpoint` 参数化 fixture
- `pyproject.toml` `[tool.pytest.ini_options]` 集中管 `testpaths` / `addopts` / `markers` / `norecursedirs`

写测试时的硬性约束:

- 测试文件命名:`tests/test_*.py`(已被 `pyproject.toml` 收集规则限制)
- 自定义 marker 先在 `pyproject.toml` `markers` 注册,避免 `PytestUnknownMarkWarning`
- 真要触发外部网络的测试,**必须**加 `@pytest.mark.real_network`(否则会被 `conftest._no_real_network` 拦截)

#### 2.1.2 测试运行(Agent 调用 shell 时,强制走 `.ps1` 中转)

只有当 Agent / CI / 开发者本人**主动触发一次完整测试套件**时才进这一节。
此时 `.ps1` 中转解决的是 shell 转义 + 路径 + 退出码,不解决 pytest 用法。

**禁止**的直接调用:

- `pytest tests/` / `pytest tests/test_xxx.py`(bash 一行块、路径未走 `-LiteralPath`、无可重入)
- `python -m pytest ...`(同上,且 `python` 在 PS 里不可靠)
- `pwsh` / `powershell.exe -Command "pytest ..."`(嵌套 shell)

**统一入口**:[scripts/run_tests.ps1](scripts/run_tests.ps1),支持:

| Mode | 行为 | 对应 pytest 原生命令 |
|---|---|---|
| `all` (默认) | 跑全部测试(conftest 自动跳过 real_network) | `pytest tests/` |
| `module` + `-Path <file>` | 跑单个测试文件 | `pytest tests/test_xxx.py` |
| `real` | 仅 `@pytest.mark.real_network` | `pytest tests/ -m real_network` |
| `skip_real` | 全部但跳过 real_network | `pytest tests/ -m "not real_network"` |
| `expression` + `-Expression "<expr>"` | 用 `-k` 表达式筛选 | `pytest tests/ -k <expr>` |
| `-ExtraArgs <string[]>` | 透传额外 pytest 参数 | 直接追加 |

```powershell
.\scripts\run_tests.ps1                                                # 全部
.\scripts\run_tests.ps1 -Mode module -Path tests/test_calendar.py      # 单文件
.\scripts\run_tests.ps1 -Mode skip_real -ExtraArgs '--maxfail=1','-x' # 离线 + 失败即停
.\scripts\run_tests.ps1 -Mode expression -Expression "test_cache"      # 用 -k 表达式
```

底层 [run_with_system_python.ps1](scripts/run_with_system_python.ps1) 负责强制使用系统 Python 3.12,
`run_tests.ps1` 只负责装配参数 + 透传退出码。

#### 2.1.3 排错清单(测试跑不起来时,按顺序查)

| 现象 | 原因 | 验证命令 |
|---|---|---|
| `[ERROR] System Python 3.12 not found` | `run_with_system_python.ps1` 自动探测失败 | 设 `SYSTEM_PYTHON_EXE` 环境变量指向系统 Python 3.12，或安装 Python 3.12 后重试（探测顺序：env > py -3.12 > Windows Store 包 > PATH） |
| `ModuleNotFoundError: No module named 'pytest'` | dev 依赖没装 | `pip install -r requirements-dev.txt` |
| `no tests ran` / `collection error` | 工作目录不是仓库根 | `Test-Path -LiteralPath pyproject.toml`(应 True) |
| 默认 `Mode=all` 一上来就 import error | 某个真网络测试在 collection 阶段炸 | 改用 `.\scripts\run_tests.ps1 -Mode module -Path <单文件>` |
| Agent 拒绝写 `import pytest` | 这是旧措辞的副作用;按 2.1.1 节,**可以并且必须** import | 在 prompt 中显式重申"测试代码按 2.1.1 写;测试运行按 2.1.2 走" |

### 2.2 git / 其他外部命令

略,与本文档其他章节一致。

---

## 3. Codex / Agent 调用模板

> 复制下面这段贴在 Codex 对话开头,可强制上述规则生效:

```
先检测当前 Agent 是 Windows native 还是 WSL,并报告 PowerShell 版本。
原生环境只使用 PowerShell,不混用 Bash/cmd,不嵌套 powershell -Command。
复杂命令或含中文输出的命令改写为 .ps1(首四行含 UTF-8 强制);路径使用 -LiteralPath,外部程序检查 $LASTEXITCODE。
同一错误不要盲目重试。
```

---

## 4. 验收测试(规则生效判定)

三项全部通过,才算"Shell 规则已生效"。任意一项失败 → 立刻修复,不要往下走。

### 4.1 读取带空格和 `[]` 的路径

```powershell
# V17.0: v9.6/SKILL.md 已删除, 验收路径改为真实存在文件（要点是 -LiteralPath 防通配符）
$path = Join-Path $PSScriptRoot 'docs\domain_glossary.md'
if (Test-Path -LiteralPath $path) {
    Get-Content -Raw -LiteralPath $path | Select-Object -First 1
} else { Write-Warning "not found: $path" }
```

要点:`Test-Path -LiteralPath` + `Get-Content -LiteralPath`,**不能用** `-Path`。

### 4.2 读取一个环境变量

```powershell
$env:TEST_AGENT_VAR = 'hello-agent'
Write-Output "TEST_AGENT_VAR=$($env:TEST_AGENT_VAR)"
Remove-Item Env:\TEST_AGENT_VAR
```

要点:用 `$env:NAME`,**不能用** `$NAME` 或 `GetEnvironmentVariable('NAME')` 的伪语法。

### 4.3 运行会返回非零退出码的命令,确认立即停止并报告 stderr

```powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$exe = 'git.exe'
$args = @('--bogus-flag-for-test-12345')

# 任何 `| Out-String` / `| Out-Null` 都会把 $LASTEXITCODE 重写成管道末端的 0,
# 因此对外部命令统一用 System.Diagnostics.Process 直接取 ExitCode,不要靠 $LASTEXITCODE。
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $exe
$psi.Arguments = [string]::Join(' ', $args)
$psi.RedirectStandardError = $true
$psi.RedirectStandardOutput = $true
$psi.UseShellExecute = $false
$p = [System.Diagnostics.Process]::Start($psi)
$combined = $p.StandardOutput.ReadToEnd() + $p.StandardError.ReadToEnd()
$p.WaitForExit()
$code = $p.ExitCode

if ($code -eq 0) { throw 'expected non-zero, got 0' }
if ([string]::IsNullOrWhiteSpace($combined)) { throw 'no stderr/stdout captured' }
Write-Output 'unreachable'
```

要点:
- `Set-StrictMode -Version Latest` + `$ErrorActionPreference = 'Stop'` 让 cmdlet 错停
- 外部程序用 `System.Diagnostics.ProcessStartInfo`,从 `Process.ExitCode` 取退出码
- 期望 `throw` 被触发,**不**是 `unreachable`

> **PowerShell 5.1 gotcha:`$LASTEXITCODE` 在管道末尾必被改写,不要靠它判外部命令**。
> 只有在**完全没有** `| ...` 的纯 `&` 调用紧接读,才可信——但组合复杂命令时极易踩坑,
> 因此统一推荐 `System.Diagnostics.Process`。

---

## 5. 速查(踩过的坑)

| 反面 | 正确 |
|---|---|
| `Test-Path -Path $path` | `Test-Path -LiteralPath $path` |
| `Get-Content $path` | `Get-Content -Raw -LiteralPath $path` |
| `git status --short` (字符串拼) | `$a=@('status','--short'); & git @a` |
| `cmd && echo ok` | 检查 `$LASTEXITCODE -eq 0` |
| `curl https://...`(PowerShell 里) | `curl.exe https://...` |
| `powershell -Command "..."` 嵌一层 | 写成 `.ps1`,`powershell -File .\x.ps1` |
| 失败重试 N 次碰运气 | 第 2 次仍失败就停手、报差异 |
| 全局 `Set-ExecutionPolicy Bypass` | 用 `-ExecutionPolicy Bypass -File` 单次放行 |
| `$LASTEXITCODE = 0` 写在 `&` 之前 | `& <cmd>; if ($LASTEXITCODE -ne 0) { ... }` (或更稳:`System.Diagnostics.Process` 取 `ExitCode`) |
| 复杂命令或管道后用 `$LASTEXITCODE` 判外部命令 | `System.Diagnostics.ProcessStartInfo` 拿 `Process.ExitCode` |
| `try { } catch { }`(空 catch) | `catch { Write-Warning "..."; throw }` |
| `$psi.ArgumentList.Add(...)` (.NET Framework 4.x 不存在) | 用 `$psi.Arguments = [string]::Join(' ', $args)` |
| 双引号字符串里直接放 `` `r `n `` | 用 `[char]10` / `[char]13` 字面量,或单引号 here-string |
| `function Foo($a) { param([string]$a) ... }` | `function Foo { param([string]$a) ... }` |
| `New-Object Foo` 后立刻 `$f.X = ...` 在某些宿主下"变量未定义" | `[Foo]::new()` 然后赋值 |
| `$a = 'x'; Write-Output "$a"` 单引号字符串里 `$a` 想被插值 | 用双引号 `$("a:" + $a)`,或字符串拼接 `+` |
| 嵌套 `try { try {} catch {} } catch {}` 在 PS 5.1 解析器里有时报 Unexpected '}' | 把失败分支抬到上一层用 `if (-not …)`,避免嵌套 try |
| `pytest tests/ -v`(shell 层 bash 一行) / `python -m pytest ...` | `.\scripts\run_tests.ps1`(本仓库 shell 层强制入口);`import pytest` 写测试代码完全 OK |
| 顶层就 `Set-StrictMode -Version Latest` + 紧跟 `param(...)` 段 | 解析顺序错了会让参数"未初始化";要么砍 param,要么先抓 $args 手解,再 Set-StrictMode |
| `param([string[]]$ExtraArgs)` 数组类型标记 | 偶发兼容错,简写为 `param($ExtraArgs)` 即可,内部 if 兜底 |
| opencode 单行命令中文乱码(子进程不加载 Profile,系统代码页 936) | **落盘 .ps1(四行头部)或 Python 探针**;单行仅限无中文输出(2026-08-12 实测"加前缀"约定易漏) |
| **python 输出接 PowerShell 管道后乱码**(`\| Select-Object` / `\| Out-File \| Get-Content`) | **禁止管道接 python**——PS 5.1 分块解码破坏多字节字符,与 python 输出无关;无管道直跑 100% 正常(2026-08-12 二度实测) |
| 项目 Python 脚本输出乱码(GBK 字节被 UTF-8 解码) | 入口脚本顶部统一强制 UTF-8(`ensure_utf8_stdio` / 内联 reconfigure 块,V16.4.1 已全量接入) |
| `.ps1` 被工具 edit/write 后中文乱码(无 BOM 被 PS 5.1 按 GBK 解析) | 必须重写为 UTF-8 with BOM(`[System.IO.File]` 读 UTF-8 + `UTF8Encoding($true)` 写回) |
| 在 `zhb_client.get_zhb` 下载判定里 import `stock_calendar` | ❌ 循环依赖: `stock_calendar.is_workday` 反向调 `get_holidays`→`get_zhb` → 递归爆栈,下载永不执行(2026-08-12 实测) |

---

## 6. 例外与豁免

以下情况经用户明确确认后可放宽,默认不豁免:

1. 调用某个只接受 Bash 的外部 SDK 时 → 改用 `wsl --exec ...` 而不是写 bash 一行
2. PowerShell 7 已安装且用户明确选用 → 用 `pwsh -File`,本规则同样适用
3. CI / Dockerfile 等已定义 Shell 的场景 → 沿用其声明,不强制

任何豁免必须在当次回复里写明"已豁免:原因"。

---

## 7. 自检清单(Copy 到任何 PR / 任务前)

- [ ] 当前 Shell 是 Windows PowerShell,不是 Bash
- [ ] 没有 `powershell.exe -Command` 嵌套
- [ ] 复杂命令都在 `.ps1` 文件里,文件首四行是 `Set-StrictMode` + `$ErrorActionPreference` + `[Console]::OutputEncoding=UTF8` + `$OutputEncoding=UTF8`
- [ ] **凡输出含中文的命令(含调试模式 Select-String→Out-File→Get-Content)已落盘 .ps1 或改 Python 探针**——未落盘的单行命令只用于无中文输出场景
- [ ] **没有 `python ... |` 管道接 PS**(禁止模式;python 输出直跑或脚本内自截断)
- [ ] `.ps1` 文件是 UTF-8 with BOM(`Format-Hex` 头三字节 `EF BB BF`;工具修改后必须重写带 BOM)
- [ ] 新建/修改的 Python 入口脚本顶部有 UTF-8 强制(`ensure_utf8_stdio` 或内联 reconfigure 块)
- [ ] 所有路径走 `-LiteralPath`
- [ ] 外部程序走 splatting + `$LASTEXITCODE` 检查
- [ ] 同一错误没有重试第 3 次
- [ ] 主动跑测试(shell 层)走 `.\scripts\run_tests.ps1`,不是直接 `pytest ...`;写测试代码时 `import pytest` 是 OK 的
- [ ] 验证报告(9.2)填了 `度量` 行(改动前后可数对比,见 11.1)

不满足,先补再执行。

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
| `tdx_client.py` | 0x0010 协议字段名(mootdx dict key)、限流间隔 |
| `zhb_client.py` | 各解析器列映射、GBK/分隔符约定 |
| `data_provider.py` | REQUIRES_REALTIME_HTTP / ZHB_SUFFICIENT 字段集 |
| `stock_common/__init__.py` | 导出是否与实际定义一致(2026-08-10 审计:`__all__` 241 项全部可访问,0 缺失;少数公共函数如 `get_em_quote_full` 未在 `__all__` 重导出,但调用方均直连子模块,无破坏) |
| `docs/field_dict.md` | 字段索引以最新破解为准:Col[3]=StaticPE_TTM(pe_dynamic 为历史遗留名)、Col[9]=MorePE(2026-08-12 TdxQuant 18/18 实锤);ZHB 列索引变化见文档 §三 头部核实日期 |

### 8.3 字段/签名变更时的连带检查

若改动涉及 **dict key / 函数签名 / 返回结构** 变更,必须:
- 找到并更新**所有**调用点(不允许只改定义)
- 同步更新 `docs/field_dict.md`(主字段字典,含字段索引)
- 检查是否有缓存反序列化依赖旧 key

---

## 9. 验证循环 (Verification Loop)

> 来源: ECC `verification-loop` skill 提炼,适配本仓库(纯 Python + PowerShell)。每次代码修改完成后、提交前运行。

### 9.1 六阶段验证

| 阶段 | 命令(全部 PowerShell 语法) | 通过标准 |
|---|---|---|
| 1. 语法 | `python.exe -m py_compile <file>` | 无错误 |
| 2. 类型 | `mypy <file>` | 无新增错误 |
| 3. 格式 | `black --check <file>`(line-length=100) | 无格式差异 |
| 4. 测试 | `.\scripts\run_tests.ps1 -Mode skip_real` | 全部通过 |
| 5. 安全 | `Select-String -Pattern "sk-|api_key|password|token" <改动文件>`(或 Python 探针) | 无硬编码密钥 |
| 6. Diff | `git.exe diff --stat` | 改动符合预期 |

> 注意: 阶段 4 全量跑较慢,改动局部时可先 `-Mode module -Path <单文件>`,提交前再全量。

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
- [ ] 涉及数据契约的改动,对照 `docs/field_dict.md` / `docs/script_data_dict.md` 字段索引
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

### 12.1 ⏳ thsdk 盘中字段核对（2026-08-11 记录）

- **背景**：thsdk 官方 _constants.py 427 个 ID→名称已归档（thsdk_field_verify.md 附录）；
  其中 160 个 ⏳ 待盘中核对（盘口 6-10 档/港美字段/综合衍生）
- **盘后结论**：同花顺行情网关非交易时段关闭实时查询（-6 非交易时间）——
  thsdk 通道仅盘中 9:30-15:00 可用（服务器策略，与客户端版本/账号无关）
- **待办**：**下次盘中（9:30-15:00）跑一次核对**：
  1. market_data_cn query_key="汇率" 实测 30 字段全量返回
  2. 自定义 data_type 拼接（如基础+402/407 股本）是否被 hq.dll 接受
  3. 盘口 6-10 档字段（买6-10/卖6-10）是否存在
- **追加**：核对完更新 thsdk_field_verify.md 的 ⏳ 状态为 ✅，删除本条

### 12.2 ✅ 东财 push2 系已恢复（2026-08-12 确认）

- 2026-08-12 健康探测 6/6 OK（push2/83.push2/push2delay/push2his/push2ex/datacenter-web）
- `tests/data/test_data_eastmoney.py` 27/27 通过，无 skip → 原 §12.1 待办删除
- 恢复后验证（原对照假设）：保持完整 UA + 观察是否再触发封禁（若低量复封 → 坐实 UA 嫌疑）
- **2026-08-12 晚更新**：采集脚本触发二次封禁(失败连接重试叠加 ~300 次)——
  已修复"失败不重试 + 域级熔断";push2 恢复期 5 主机字段差异对比待办保留
