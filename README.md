# A股个股分析报告生成系统

一套自动化生成A股个股分析报告的Python工具集，支持短线、中线、长线、估值、市场热点等多种报告类型，数据来源于通达信（TDX）、东方财富、腾讯、新浪等主流平台。

---

## 功能特性

- 生成短线、中线、长线、估值选股和市场状态五类 A 股分析报告。
- 通过统一数据层和专项适配器读取行情、财务、行业及市场数据，集中处理来源路由、单位、缓存和来源标注。
- 独立运行多源字段采集与离线碰撞分析；候选不会自动写入主字典，正式变更走人工审阅与裁决流程。
- 可选上传报告至 Google Drive；本地报告与离线验收流程不依赖该功能。
- 文档入口见 [`docs/README.md`](docs/README.md)，当前采集与破解步骤见 [`每日运行卡`](docs/field_verification/DAILY_RUNBOOK.md)。

## 碰撞分析与每日验证

使用 `scripts/capture_field_probe.py` 采集来源样本，再单独运行 `scripts/collide.py` 分析本地证据；碰撞本身不联网，也不会直接修改主字典。运行阈值以 `scripts/collision_rules.py` 为准，字段身份以逐源 registry 为准，报告审阅和写回流程见每日运行卡及裁决工作流。

## 快速开始

### 环境要求

- Python **3.11+**；推荐 **3.12**（AxData 0.1.4 要求 Python ≥3.11；测试启动器默认选择并校验 Python 3.12）
- 已验证环境：Windows + Python 3.12（PowerShell）；代码最低支持 Python 3.11。其他系统尚未按本仓库的标准启动器完整验证。
- 项目自身的锁文件和报告临时输出写入仓库根 `.tmp/`。Windows 下仍推荐使用 `scripts/run_with_system_python.ps1`（或兼容入口 `.bat`），使 Python 及其子进程的 `TEMP`/`TMP`/`TMPDIR` 均指向该目录；直接执行项目入口时，项目内部临时路径也会落入 `.tmp/`。可通过 `ASTOCK_TEMP_DIR` 显式指定项目临时目录。

### 新机器部署（复制项目后）

项目内数据目录按仓库位置解析；首次运行会按需创建 `cache/`、`logs/`、`reports/`、`snapshots/` 并同步 ZHB 数据。部分功能还会读取本机配置或外部行情文件，部署前请按对应功能说明配置。

1. 安装 Python 3.12（最低支持 Python 3.11；Windows Store 版已验证可用）
2. `pip install -r requirements.txt`（依赖版本和可选功能以该文件为准）
3. `pip install -r requirements-dev.txt`（开发环境；依赖范围以该文件为准）
4. Windows 首次运行 `.\scripts\run_with_system_python.ps1 main.py --sht 600519 --no-upload` 冒烟（首只约 5 分钟，含 ZHB 下载+缓存预热）

可选配置（缺失不影响核心报告）：
- **Google Drive 上传**：配置 Google OAuth 凭据；缺失时本地报告仍可生成，但无法上传。
- **东方财富 Cookie**：需要时可通过 `EAST_MONEY_COOKIE` 或 `credentials/eastmoney_cookie.txt` 配置。

项目入口会将 Python 标准输出设为 UTF-8，启动器会把临时目录指向仓库 `.tmp/`。无需修改系统级环境变量、PowerShell Profile 或全局执行策略；测试和 Python 命令按下方入口运行。

### 安装依赖

```powershell
.\scripts\run_with_system_python.ps1 -m pip install -r requirements.txt
.\scripts\run_with_system_python.ps1 -m pip install -r requirements-dev.txt   # 开发环境
```

`requirements-dev.txt` 通过 `-r requirements.txt` 继承同一组运行时固定版本。AxData 的 `axdata_core` 模块由 `axdata` 包提供；短线指标使用仓库根目录 `cache/zhb/` 中最新的 `zhb_*.zip` 作为统计资源，同时仍会请求 TDX 行情/财务输入。适配器和 ZIP 路径的回归边界见 [`UPSTREAM_COMPATIBILITY.md`](docs/UPSTREAM_COMPATIBILITY.md)。

### 基本用法

```powershell
# 生成短线报告
.\scripts\run_with_system_python.ps1 main.py --sht 600519 000858

# 生成中线报告
.\scripts\run_with_system_python.ps1 main.py --med 600519 000858

# 生成多种报告
.\scripts\run_with_system_python.ps1 main.py --sht 600519 --med 600519 --lng 600519

# 批量处理
.\scripts\run_with_system_python.ps1 main.py --sht 600519 000858 03606 --med 600519 000858
```

项目当前的标准启动和测试流程以 Windows PowerShell 为准；跨平台支持尚未作为验证承诺。

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
├── .tmp/                         # 本机运行时临时目录（Git 忽略，按需创建）
├── VERSION                       # 项目版本号（见文件，单一来源）
│
├── core/                         # 核心模块包（9 个支撑模块，见 core/README.md）
│   ├── config.py                 # 全局配置集中管理（超时/限流/熔断）
│   ├── data_provider.py          # 统一数据层（canonical 合约 + 字段路由 + 多级 fallback）
│   ├── _accessors.py             # 跨边界访问器叶子模块（get_concept_from_zhb 等 7 个访问器，消除 data_provider↔stock_common 导入期循环依赖）
│   ├── _tdx_handshake_patch.py   # eltdx 握手兼容补丁
│   ├── zhb_client.py             # 通达信 zhb.zip 全局配置总包下载与解析（45 文件）
│   ├── zhb_sync.py               # ZHB 自动化入库管道（python -m core.zhb_sync）
│   ├── tdx_client.py             # eltdx/easy_tdx 统一层（运行时主源 eltdx；mootdx 已于 V17.3.4 退役）
│   ├── stock_cache.py            # 统一缓存层（SQLite + L1 内存 + TTL + cross_verify）
│   └── gd_uploader.py            # Google Drive 上传（凭据在 credentials/）
│
├── stock_common/                 # 核心公共包（传输/数据源/评分/报告基类，见 stock_common/README.md）
│   ├── __init__.py               # 包入口，统一导出显式公共接口
│   ├── sc_datasource/            # 数据源查询包（按数据源与业务职责拆分，见子包 README）
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
│   └── eastmoney_cookie.txt      # 可选东方财富 Cookie
│
├── scripts/                      # 辅助脚本（见 scripts/README.md）
│   ├── capture_field_probe.py    # 字段实测采集；KPL/KPH 涨停明细独立归档并按实测日对齐
│   ├── collide.py                # 日期归一化、快照择优、跨源独立性闸门与多方法候选；每日采集后运行
│   ├── collision_research_state.py  # 探索候选观察台账；按字段对保存证据历史
│   ├── context_policy.py         # 采集与碰撞共享的可选上下文路径策略
│   ├── run_tests.ps1             # 测试统一入口（AGENTS.md 强制 shell 层中转）
│   ├── run_with_system_python.ps1 # Python 3.12 选择与命令转发
│   ├── update_calendar.py        # 交易日历数据更新（含 V14+ 防覆盖保护）
│   ├── clean_cache.py            # 缓存清理快捷脚本（封装 python -m core.stock_cache）
│   ├── backtest_topn.py          # top_n 回测验证
│   ├── perf_compare.py           # dataclass vs dict 性能压测
│   ├── gen_field_matrix.py       # 字段×源矩阵自动生成
│   ├── fmt_preview.py            # 零网络格式预览工具（V17.0.3）
│   ├── check_em_health.py        # 东财接口健康探测（6 域低频）
│   ├── upload_reports_to_gd.py   # GD 补传（扫描未上传 md）
│   └── backup-opencode.ps1       # opencode 配置备份
│
├── docs/                         # 技术文档（见 docs/README.md）
│   ├── PROJECT_CONTEXT.md        # 架构导航、稳定约束与动态项目快照
│   ├── ARCHITECTURE_THEORY.md    # 统一数据访问架构公理
│   ├── DEBT_LEDGER.md            # 已知架构偏离与偿还状态
│   ├── PROJECT_AUDIT_REMEDIATION_20260928.md # 本轮整改计划与验收记录
│   ├── UPSTREAM_COMPATIBILITY.md # 上游仓库、依赖和适配边界复核
│   ├── architecture.md           # 项目架构与数据流图（Mermaid）
│   ├── roadmap.md                # 版本路线图 + ADR 决策记录
│   ├── field_dict.md             # 生成的字段治理入口与链接
│   ├── field_verification/field_registry.json # 逐源完整路径字段状态（机器权威）
│   ├── field_verification/collision_research_state.json.gz # 探索候选历史（不代表字段定案）
│   ├── unknown_fields.md         # 未知、候选、冲突与已证伪字段队列
│   ├── field_matrix.md           # 字段×源矩阵
│   ├── source_repository_map.md  # 数据源与 GitHub 仓库对应关系
│   ├── field_source_reference.md # 重整前完整字典原文归档
│   ├── verify/                   # 字典附录（实测值/样本/破解数据——实证层）
│   ├── script_data_dict.md       # 脚本应用接口与字段来源字典
│   └── domain_glossary.md        # 领域词汇表（术语口径统一）
│
├── tests/                        # pytest 测试（模块和用例数见 tests/README.md）
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
| `credentials/` | 可选本地凭据(不入库) | Google OAuth / Eastmoney Cookie |
| `scripts/` | 可复用运维命令 | run_tests.ps1 / update_calendar / clean_cache |
| `docs/` | 技术文档(架构/决策/字段治理) | roadmap / field_dict / registry / unknown_fields |
| `tests/` | pytest 测试(防退化守护) | data/ core/ reports/ infra/ |
| `reports/` | 报告输出(运行时) | 运行时生成（.gitignore，无专职 README） |
| `snapshots/` | 评分快照(运行时) | 运行时生成（.gitignore，无专职 README） |
| `cache/` | 缓存数据(运行时) | stock_cache.db / zhb/ / 行业映射 |
| `scratch/` | 一次性调研沙盒(用完即弃) | 见 scratch/README.md |
```

---

## 配置文件

### requirements.txt / config.py

运行时依赖见 [`requirements.txt`](requirements.txt)（16 项；`levistock`/`axdata` 可选，缺失自动降级），开发依赖见 [`requirements-dev.txt`](requirements-dev.txt)（pytest/mypy/black）。核心参数集中在 `core/config.py`：网络超时、限流（`EM_MIN_INTERVAL=1.0`）、重试、缓存（DB≤500MB）、熔断（阈值 10）；分域限流表在 `stock_common/sc_network.py::_DOMAIN_LIMITS`，push2 家族上限为 0.25 RPS。Eastmoney 全局门槛和风险组门槛由共享跨进程调度共同执行。完整定义以源文件为准。

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

- **`core/data_provider.py`**：个股数据统一入口，封装 `CanonicalStockData` 强类型合约（113 个 dataclass 属性，含 12 个可选 ELTDX 扩展；非扩展属性为 101 个；`sc_schema.FIELD_SPECS` 是 38 项精选源字段元数据，不是完整契约字段清单）。报告批量路由为 push2delay 基础行情 + 腾讯补充字段；批量缺价时单股 fallback 为 TDX → 腾讯 → push2delay → push2，并按时段使用 ZHB 快照。每只股票通过 `field_sources` 留存来源，并透传行情有效日期与采集时间；跨边界访问器已拆至 `core/_accessors.py`，消除与 `stock_common` 的导入期循环依赖。
- **`stock_common/sc_network.py`**：分域与风险组限流（push2 家族、push2ex、push2delay 各自设限，仍共享 Eastmoney 全局间隔）、跨进程原子时隙、408/5xx 与瞬时传输故障有界退避、403/429 立即停止、按组连续封禁 20h 冷却。
  > 注：`core/tdx_client.py::_DOMAIN_LIMITS` 另有 6 域**独立**限流表（TCP 长连接语义，与 HTTP 请求级节流不同，**有意不合并**）。
- **`stock_common/sc_datasource/`**：按数据源和业务职责组织的查询适配器，模块清单见 [`stock_common/sc_datasource/README.md`](stock_common/sc_datasource/README.md)。
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
## 开发与验证

开发环境和临时目录约定见上方「快速开始」及 [`scripts/README.md`](scripts/README.md)。仓库级约束见 [`AGENTS.md`](AGENTS.md)。

### 离线测试

```powershell
.\scripts\run_tests.ps1 -Mode skip_real
.\scripts\run_tests.ps1 -Mode module -Path tests\core\test_core_routing.py
```

默认不触发真实网络；需要真实网络的测试必须标记 `real_network`，并显式使用 `-Mode real`。当前测试模块清单和最近完整结果见 [`tests/README.md`](tests/README.md)。

### 静态检查与架构闸门

```powershell
.\scripts\run_offline_checks.ps1
```

该入口依次检查 Git 可见 Python 文件的语法、全项目 MyPy、Black Python API 格式、AxData 摘要新鲜度、数据访问、字典同步、Canonical contract、registry parity 和完整离线测试；真实网络用例仍默认排除。Windows 下的格式检查使用与 `pyproject.toml` 一致的 Black Python API，不调用曾出现长时间无输出的 Black CLI。局部回归仍可用 [`scripts/run_tests.ps1`](scripts/run_tests.ps1) 选择单个测试文件。完整约束见 [`AGENTS.md`](AGENTS.md) §9。

### 文档与版本

改动行为后同步更新 [`CHANGELOG.md`](CHANGELOG.md)；版本号以根目录 [`VERSION`](VERSION) 为准。架构说明见 [`docs/architecture.md`](docs/architecture.md)，稳定术语见 [`docs/domain_glossary.md`](docs/domain_glossary.md)，字段口径以逐源注册表和生成字典为准。

---

## 许可证

MIT License

---

## 免责声明

本项目仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。使用本工具产生的任何投资损失，作者不承担责任。

---

## 联系方式

如有问题或建议，欢迎提交 [Issue](https://github.com/tsy1102/a-stock-data/issues)。
