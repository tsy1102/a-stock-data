# A股个股分析报告生成系统

一套自动化生成A股个股分析报告的Python工具集，支持短线、中线、长线、估值、市场热点等多种报告类型，数据来源于通达信（TDX）、东方财富、腾讯、新浪等主流平台。

---

## 功能特性

- **5 种报告类型**：短线(sht) / 中线(med) / 长线(lng) / 估值选股(val) / 市场状态(mak)（ful 已于 V16.1 下线，能力并入前四类）。
- **多源字段逆向破解**：ZHB / TDX 0x0010 / 东财 push2 / 腾讯 / 新浪 / 同花顺 fuyao·thsdk / 巨潮 / FTShare 私有协议字段交叉验证，实锤与样本沉淀于 `docs/field_dict.md` 与 `docs/verify/`；主字典只留结论、附录存实证。
- **统一数据合约**：唯一入口 `get_canonical_stock_data` 返回 `CanonicalStockData` 强类型合约（50+ 字段，每字段带 `field_sources` 溯源），消除异构多源冲突。
- **ZHB-First 离线优先路由**：盘前 / 休市日 100% 走 ZHB 内存秒级提取；交易日盘中盘后强制网络取 T 日真实收盘价。
- **申万二级行业统一**：东财 datacenter 一次性分页拉取 + 7 天缓存，零逐股请求、零 push2 风控面。
- **东财分域限流与风控**：共享令牌桶 + 全局 1.0s 节流 + 强制直连 + 429 退避 + 连续 3 次断连 20h 冷却；熔断静默降级回退 ZHB T-1 快照。
- **统一缓存层**：SQLite + L1 内存 + TTL + `cross_verify` + single-flight + 版本化防污染（口径变更升 category）。
- **TDX 服务器白名单**：54 台实测收敛为 5 台 FULL 服务器，探测轮换只遍历白名单。
- **通用框架与工程化**：`BaseReportRunner` 共享骨架、并发下沉线程池、云端同步（GD 上传）、批量并行、mypy 类型安全。
- **测试体系（防退化守护）**：21 文件 / 370 函数（pytest 收集 398 项，分层 data/core/infra/reports），回归基线 **353 passed / 45 deselected / 0 failed**；演进 302 → 269 → 277 → 311 → 353。

---

## 快速开始

### 环境要求

- Python **3.12**（系统 Python，`scripts/run_tests.ps1` 强制；main.py 自动探测）
- Windows / macOS / Linux

### 新机器部署（复制项目后）

项目全部路径基于脚本自身位置动态定位（`__file__`），**无任何绝对路径硬编码**；复制到任意目录即可运行，首次运行自动创建 `cache/`、`logs/`、`reports/`、`snapshots/` 并下载 ZHB 数据包。

1. 安装 Python 3.12（任意发行版；Windows Store 版已验证可用）
2. `pip install -r requirements.txt`（运行时依赖 17+ 项；`levistock/axdata/thsdk` 为可选增强，缺失自动降级）
3. `pip install -r requirements-dev.txt`（仅开发需要：pytest/mypy/black）
4. 首次运行 `python main.py --sht 600519 --no-upload` 冒烟（首只约 5 分钟，含 ZHB 下载+缓存预热）

可选配置（缺失不影响运行）：
- **Google Drive 上传**：`credentials/client_secrets.json`（V17.0 凭据集中目录），首次运行浏览器 OAuth 生成 `credentials/credentials.json`；国内网络需本地代理（gd_uploader 自动探测 7890/10809/1080 等常见端口）
- **同花顺增强**：`credentials/ths_credentials.json`（`{"username":..,"password":..,"mac":..}`）或设 `THS_USERNAME/THS_PASSWORD` 环境变量；无凭证时 SDK 游客兜底

**新电脑 UTF-8 环境初始化（V16.4.0，一次性）**：

```powershell
# 1. Python 全局 UTF-8（解决 python 输出/参数中文乱码）
setx PYTHONUTF8 1

# 2. PowerShell UTF-8（解决控制台/管道中文乱码——Profile 内容见下）
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
New-Item -ItemType Directory -Force "$HOME\Documents\WindowsPowerShell" | Out-Null
@"
# UTF-8 environment init
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
`$OutputEncoding = [Console]::OutputEncoding
chcp 65001 > `$null
"@ | Set-Content -Path "$HOME\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1" -Encoding UTF8
```

> 完成后**注销重登**（setx 环境变量对新进程生效）。项目内文件统一 UTF-8；脚本文件避免在命令行内嵌中文（用脚本文件方式）。

### 安装依赖

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt   # 开发环境（测试/类型/格式）
```

### 基本用法

```bash
# 生成短线报告
python main.py --sht 600519 000858

# 生成中线报告
python main.py --med 600519 000858

# 生成多种报告
python main.py --sht 600519 --med 600519 --lng 600519

# 批量处理
python main.py --sht 600519 000858 03606 --med 600519 000858
```

---

## 报告类型说明

| 参数 | 报告类型 | 说明 |
|------|----------|------|
| `--sht` | 短线交易执行 | 涨跌停边界、当日资金流、昨日涨停晋级率、龙虎榜席位、封单强度、盘口异动检测 |
| `--med` | 中线业绩兑现 | 报告期绑定财务、研报评级变化、两融 3/5/10 日维度、技术面 MACD/RSI/BOLL/KDJ |
| `--lng` | 长线企业质量 | 多期财务纵深、分红连续性、风险扫描（解禁/减持/质押）、现金流验证 |
| `--val` | 全市场候选发现 | 多策略分层扫描（ZHB 初筛 → 扩展字段候选 → 深度确认），PE 估值回归含跨年 Q1 修复 |
| `--mak` | 市场状态引擎 | 市场宽度、四池、行业轮动（申万二级）、财联社市场情绪/涨停天梯/盘口异动 |
| `--ful` | ~~完整报告~~ | **V16.1 已下线**：能力并入 sht/med/lng（技术/风险引擎迁移至 sc_technical/sc_risk） |

> V16.1：`--ful` 参数保留但不再生成报告（报友好提示）。技术指标引擎（MACD/RSI/BOLL/KDJ）与风险扫描引擎已迁移至 `stock_common/sc_technical.py` / `sc_risk.py` 供 sht/med/lng 复用。

---

## 命令行参数

```
python main.py [选项] 股票代码...

选项:
  --sht    生成短线交易执行报告
  --med    生成中线业绩兑现报告
  --lng    生成长线企业质量报告
  --val    生成全市场选股报告
  --mak    生成市场状态报告
  --ful    V16.1 已下线（提示改用 --sht/--med/--lng）
  --all    生成所有报告类型
  --no-upload  禁用Google Drive上传
  --help   显示帮助信息

股票代码格式:
  支持6位数字代码，如: 600519
  支持带后缀格式，如: 600519茅台
  支持空格分隔，如: 600519 000858 03606
```

---

## 项目结构

```
a-stock-data/
├── main.py                       # 主入口程序（参数分发/子进程调度/超时分级）
├── VERSION                       # 项目版本号（17.0，单一来源）
│
├── core/                         # V17.0 核心模块包（7 个支撑模块，见 core/README.md）
│   ├── config.py                 # 全局配置集中管理（超时/限流/熔断）
│   ├── data_provider.py          # 统一数据层（canonical 合约 + 字段路由 + 多级 fallback）
│   ├── zhb_client.py             # 通达信 zhb.zip 全局配置总包下载与解析（45 文件）
│   ├── zhb_sync.py               # ZHB 自动化入库管道（python -m core.zhb_sync）
│   ├── tdx_client.py             # mootdx/easy_tdx 统一层（K线/F10/资金流/板块）
│   ├── stock_cache.py            # 统一缓存层（SQLite + L1 内存 + TTL + cross_verify）
│   └── gd_uploader.py            # Google Drive 上传（凭据在 credentials/）
│
├── stock_common/                 # 核心公共包（传输/数据源/评分/报告基类，见 stock_common/README.md）
│   ├── __init__.py               # 包入口，统一导出接口（__all__ 250+ 项）
│   ├── sc_datasource.py          # 数据源查询模块（100+ 函数）
│   ├── sc_network.py             # 网络请求层（分域限流/令牌桶/封禁冷却/进程文件锁）
│   ├── sc_report_runner.py       # BaseReportRunner 基类
│   └── ...                       # 详见 stock_common/README.md
│
├── get_sht_report.py             # 短线报告生成（90 日窗口）——入口脚本
├── get_med_report.py             # 中线报告生成（180 日窗口）
├── get_lng_report.py             # 长线报告生成（730 日窗口）
├── get_val_report.py             # 估值报告生成（策略选股）
├── get_mak_report.py             # 市场热点报告生成（异动扫描）
│
├── credentials/                  # V17.0 凭据集中目录（.gitignore 排除，不入库）
│   ├── client_secrets.json       # GD OAuth 客户端凭据
│   ├── credentials.json          # GD OAuth token（自动刷新）
│   └── ths_credentials.json      # 同花顺 THS SDK 账号
│
├── scripts/                      # 辅助脚本（见 scripts/README.md）
│   ├── capture_field_probe.py    # 字段实测采集（20 股 × 18 源 → docs/field_verification/YYYYMMDD/）
│   ├── run_tests.ps1             # 测试统一入口（AGENTS.md 强制 shell 层中转）
│   ├── update_calendar.py        # 交易日历数据更新（含 V14+ 防覆盖保护）
│   ├── clean_cache.py            # 缓存清理快捷脚本（封装 python -m core.stock_cache）
│   ├── backtest_topn.py          # top_n 回测验证
│   ├── perf_compare.py           # dataclass vs dict 性能压测
│   ├── gen_field_matrix.py       # 字段×源矩阵自动生成
│   ├── fmt_preview.py            # 零网络格式预览工具（V17.0.3）
│   ├── check_em_health.py        # 东财接口健康探测（6 域低频）
│   ├── upload_reports_to_gd.py   # GD 补传（扫描未上传 md）
│   ├── sync_readme.py            # CHANGELOG → README 自动同步
│   └── backup-opencode.ps1       # opencode 配置备份
│
├── docs/                         # 技术文档（见 docs/README.md）
│   ├── architecture.md           # 项目架构与数据流图（Mermaid）
│   ├── roadmap.md                # 版本路线图 + ADR 决策记录
│   ├── field_dict.md             # 主字段字典（ZHB 字段索引/破解结论）
│   ├── V17.0_REFACTOR_PLAN.md    # V17.0 重构计划（执行基准）
│   ├── verify/                   # 字典附录（实测值/样本/破解数据——实证层）
│   ├── script_data_dict.md       # 脚本应用接口与字段来源字典
│   └── domain_glossary.md        # 领域词汇表（术语口径统一）
│
├── tests/                        # pytest 测试（21 文件 / 370 用例，按 data/core/infra/reports 分层，见 tests/README.md）
├── pyproject.toml                # pytest / mypy / black 等工具配置中心
├── requirements.txt              # 运行时依赖列表
├── requirements-dev.txt          # 开发依赖列表（测试/类型/格式）
├── CHANGELOG.md                  # 版本变更记录
├── AGENTS.md                     # Agent 行为规约（Shell 规则/验证循环/审查流程）
├── CONTRIBUTING.md               # 贡献指南
├── CODE_OF_CONDUCT.md            # 社区行为准则
├── LICENSE                       # MIT 许可证
├── README.md                     # 本文件
│
├── reports/                      # 报告输出目录（运行时，.gitignore）
├── snapshots/                    # 评分快照（历史对比/背离检测，.gitignore）
├── cache/                        # 缓存数据库 + ZHB 数据包 + 行业映射（.gitignore）
└── scratch/                      # 一次性调研沙盒（.gitignore，见 scratch/README.md）
```

> **目录职责总表**

| 目录 | 目的 | 关键文件 |
|:---|:---|:---|
| `core/` | 核心支撑模块(数据层/传输/缓存/日历同步/上传) | data_provider / tdx_client / stock_cache |
| `stock_common/` | 公共业务模块(网络层/数据源/评分/报告基类) | sc_network / sc_datasource / sc_report_runner |
| `credentials/` | 凭据集中目录(不入库) | client_secrets / credentials / ths_credentials |
| `scripts/` | 可复用运维命令 | run_tests.ps1 / update_calendar / clean_cache |
| `docs/` | 技术文档(架构/决策/字段字典) | roadmap / field_dict / architecture |
| `tests/` | pytest 测试(防退化守护) | data/ core/ reports/ infra/ |
| `reports/` | 报告输出(运行时) | 见 reports/README.md |
| `snapshots/` | 评分快照(运行时) | 见 snapshots/README.md |
| `cache/` | 缓存数据(运行时) | stock_cache.db / zhb/ / 行业映射 |
| `scratch/` | 一次性调研沙盒(用完即弃) | 见 scratch/README.md |
```

---

## 配置文件

### requirements.txt / config.py

运行时依赖见 [`requirements.txt`](requirements.txt)（17+ 项；`levistock`/`axdata`/`thsdk` 可选，缺失自动降级），开发依赖见 [`requirements-dev.txt`](requirements-dev.txt)（pytest/mypy/black）。核心参数集中在 `core/config.py`：网络超时、限流（`EM_MIN_INTERVAL=1.0`）、重试、缓存（DB≤500MB）、熔断（阈值 10）；分域限流表在 `stock_common/sc_network.py::_DOMAIN_LIMITS`（push2 系最严 0.4rps）。完整定义以源文件为准。

### Google Drive 配置（可选）

如需启用云端上传功能：

1. 在 Google Cloud Console 创建项目并启用 Drive API
2. 下载 OAuth 2.0 凭证文件，保存为 `credentials/client_secrets.json`（V17.0 凭据集中目录）
3. 首次运行时会弹出浏览器进行授权，授权后自动生成 `credentials/credentials.json`

> **注意**：
> - OAuth scope 为 `drive.file`，脚本只能看到由该脚本自身创建或打开过的文件/文件夹
> - 若 Google Drive 根目录无故出现个股文件夹，通常是桌面客户端同步冲突导致（详见 FAQ），脚本本身不会移动或删除已有文件夹

---

## 核心模块说明

文档完整架构（模块职责 / 数据流 / 并发限流 / 缓存分层 / 字段路由）见 [`docs/architecture.md`](docs/architecture.md)（含 Mermaid 图）。要点速览：

- **`core/data_provider.py`**：唯一数据入口，封装 `CanonicalStockData` 强类型合约 + 字段路由 + 4 级 fallback（L0 东财申万二级 → push2 → TDX → ZHB），每字段带 `field_sources` 溯源。
- **`stock_common/sc_network.py`**：分域限流（38 域）、进程文件锁、429 退避、连续封禁 20h 冷却。
- **`stock_common/sc_datasource.py`**：100+ 数据源查询函数。
- **`stock_common/sc_schema.py`**：字段元数据层（`FieldSpec` / `TimeAnchor` / `DataSource` / `Unit`），`normalize_at_boundary` 单位归一。
- **`core/stock_cache.py`**：SQLite + L1 内存 + TTL + `cross_verify` + single-flight + 版本化防污染。
- **`stock_common/sc_fault_tolerance.py`**：`TokenBucket` / `CircuitBreaker` / `RandomUAPool`。
- **`stock_common/sc_technical.py` / `sc_risk.py`**：技术指标（MACD/RSI/BOLL/KDJ）与风险扫描引擎。
- **`stock_common/stock_calendar.py`**：本地交易日历（621 条 2004-2026+）权威判定。
- **`get_*_report.py`**：5 大报告 Runner，继承 `BaseReportRunner`，共享 CLI/Banner/上传/清理模板，差异仅在章节渲染。

## 输出示例

报告文件命名格式：`{股票代码}_{报告类型}_{日期}_{时间}.md`（V17.0.1 起全量 md 化）

```
reports/
├── 600519_sht_20260618_1430.md    # 茅台短线报告
├── 600519_med_20260618_1435.md    # 茅台中线报告
├── 600519_lng_20260618_1440.md    # 茅台长线报告
└── get_val_report_20260618_1445.md # 估值汇总报告
```

---

## 版本历史

完整版本历史（含全部字段破解实锤与回归基线演进）见 [CHANGELOG.md](CHANGELOG.md)。本文档不再重复版本明细。

---
## 开发指南

### 本地开发

环境部署（克隆 / 安装依赖 / UTF-8 初始化）见上方「快速开始」。开发常用命令：

```bash
# 运行测试（shell 层强制走 run_tests.ps1，禁止直接 pytest）
.\scripts\run_tests.ps1

# 类型检查
python -m mypy stock_common/sc_datasource.py get_val_report.py tdx_client.py --ignore-missing-imports

# 临时禁用缓存调试
STOCK_NOCACHE=1 python main.py --sht 600519
```

### 类型注解与静态检查

项目核心模块已完成类型注解（PEP 484），在 `pyproject.toml` 中集中管理 mypy 配置：

- `[tool.mypy]`：Python 3.10 目标版本，启用 `no_implicit_optional`、`warn_redundant_casts`
- `[tool.black]`：代码格式化工具配置（line-length=100）

### 常见调试问题

- **报告数据与最新行情不一致？**：可能是缓存命中了过期数据，执行 `STOCK_NOCACHE=1 python main.py ...` 临时禁用缓存再测一次；或调用 `python -m core.stock_cache clear --category dragon_tiger` 清理对应分类。
- **类型检查 mypy 报错？**：`third-party library stub missing` 类警告可忽略（已在 `pyproject.toml` 配置 `ignore_missing_imports=true`）。如果是自定义函数参数/返回值类型问题，请直接提交 issue。
- **Google Drive 上传失败？**：检查根目录是否有 `client_secrets.json`（首次使用需浏览器授权），确认授权账号有 `a-stock_data` 文件夹的访问权限。
- **架构不熟悉？**：详见 [`docs/architecture.md`](docs/architecture.md)，包含 Mermaid 架构图；字段口径见 [`docs/domain_glossary.md`](docs/domain_glossary.md) 领域词汇表。

### 提交代码

```bash
git add .
git commit -m "feat: 新功能描述"
git push origin master
```

提交信息规范：
- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `refactor:` 代码重构
- `chore:` 杂项修改

---

## 开发与测试

> 详见 [AGENTS.md](AGENTS.md)。这里只列最常用的入口。

### 测试入口(强制 PowerShell 中转)

**不要**在 shell 里直接敲 `pytest ...` / `python -m pytest ...`。一律走：

```powershell
.\scripts\run_tests.ps1                                       # 全部离线测试
.\scripts\run_tests.ps1 -Mode module -Path tests/test_calendar.py     # 单个文件
.\scripts\run_tests.ps1 -Mode skip_real -ExtraArgs '--maxfail=1','-x' # 跳过 real_network + 失败即停
.\scripts\run_tests.ps1 -Mode real                             # 仅真网络测试（需 REAL_NETWORK=1）
```

入口脚本在 [scripts/run_tests.ps1](scripts/run_tests.ps1)，底层强制走系统 Python 3.12（见 [scripts/run_with_system_python.ps1](scripts/run_with_system_python.ps1)）。

### 写测试代码（pytest 是 Python 库,正常用）

```python
import pytest
from pytest import approx

@pytest.fixture
def tmp_project(tmp_path): ...

@pytest.mark.real_network   # 触发外部网络前必须加这个 marker
def test_em(endpoint): ...

@pytest.mark.parametrize('a,b,exp', [(1,1,2),(2,3,5)])
def test_add(a, b, exp): ...

def test_raises():
    with pytest.raises(ValueError):
        int('not a number')

def test_approx():
    assert 0.1 + 0.2 == approx(0.3)
```

新增自定义 marker 先在 `pyproject.toml` `[tool.pytest.ini_options] markers` 注册，避免 `PytestUnknownMarkWarning`。
详见 [tests/conftest.py](tests/conftest.py) 顶部的 compliance note 与 [AGENTS.md 2.1](AGENTS.md) 节。

---

## 许可证

MIT License

---

## 免责声明

本项目仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。使用本工具产生的任何投资损失，作者不承担责任。

---

## 联系方式

如有问题或建议，欢迎提交 [Issue](https://github.com/tsy1102/a-stock-data/issues)。