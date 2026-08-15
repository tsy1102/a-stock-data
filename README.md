# A股个股分析报告生成系统

一套自动化生成A股个股分析报告的Python工具集，支持短线、中线、长线、估值、市场热点等多种报告类型，数据来源于通达信（TDX）、东方财富、腾讯、新浪等主流平台。

---

## 功能特性

- **字典架构重构（V16.4.0）**：主字典=决策层（field_dict 只留结论），附录=实证层（docs/verify/ 12 个文件）；三大客户端逆向（东财/通达信/同花顺）——tdxstat 35 列/tdxstat2 21 列官方破解（ipo_price/52周/PE 双口径铁证）、thsdk 市净率口径铁证、服务器全表（通达信 HQHOST 43/同花顺 123ths 域名族）；统一层加固（缓存 schema 版本化 + canonical 量级校验）；sht 批量预取优化（push2delay ulist 300/批）
- **字段实测验证流水线（V16.4.1）**：20 股固定股票池 + 19 源按天采集（`scripts/capture_field_probe.py` → `docs/field_verification/`）；TdxQuant 官方 88 字段交叉破解（Col[3]=StaticPE_TTM/Col[24]=CashZJ 万元/[26]=YearZTDay 等 18/18 实锤）；每日会话纪要锚点 `docs/session_notes/`
- **全盘重构与字段破解（V17.0）**：7 支撑模块包化 `core/`；批量骨架收敛基类 `execute_batch_pipeline`；main.py 固定超时改**输出活性检测**；主力净流入全链统一 f137、行业仅认 881 段、PE 动态=f162（字典实锤）；**命名规律破解**——Amo=Amount 金额族、"N日"涨跌幅全交易日口径、tdxstat2 21 列全映射（封单额三日滚动）、f137-146 资金流定位、通达信行业体系（881 行业/880 概念/X 码细分行业）；script_data_dict.md 全量重写
- **字段增强与全量 md 化（V17.0.1）**：mak 主力净额 ulist 批量 f62+f66 真主力（竞价额冒充修复）；sht 连板追踪 ZHB[31] 真连板数；val 21→23 策略（业绩预增 get_yjyg_all + 盈利预期本机 ProfitForecast）；lng 机构一致预期；三轮审查 50+ 项修复（单位 10000x/缓存失效/限流面/契约键）；**报告全量 md 化**（`md_render.py` 渲染层转换：标题/分隔线/F10 边框表/空格表数据驱动切分，输出 .md 纯文本兼容）；bypass 模式 .day 尾部补价（新版 .day 格式破解：OHLC=int32×0.01 元）
- **5种报告类型**（V16.1: ful 下线）：短线(sht)、中线(med)、长线(lng)、估值选股(val)、市场状态(mak)
- **标准化数据合约对象**（V15.0-V15.2）：`CanonicalStockData` 不可变强类型合约，封装 50+ 核心数据字段及元数据溯源标签（`field_sources`），彻底消除异构多源数据冲突
- **基于真实周期的 ZHB-First 离线优先路由**（V15.1 全局普及）：
  - 盘前（`<09:30`）与休市日：100% 走 ZHB 本地内存秒级提取，零网络开销（完美利用清晨生成的最新 ZHB 文件包）
  - 交易日 `09:30-24:00`（含盘中与盘后）：行情与资金流字段 100% 强制走网络 HTTP/TDX 接口，确保获取 T 日真实收盘价
- **行业统一申万二级**（V16.2.17 用户决策）：canonical/mak 板块聚合/同业对比/板块内排名全链路统一为东财 datacenter 申万二级（半导体/白酒Ⅱ/光学光电子…），全市场映射一次性分页拉取 + 7 天缓存（`em_industry_map_l2.json`），零逐股请求、零 push2 风控面
- **东财分域限流与风控体系**（V16.2.5-V16.2.13）：push2 系共享归一化令牌桶 **0.4rps/2.5s**、datacenter 1.0rps、腾讯 5.0rps；全局时间戳硬下限（`EM_MIN_INTERVAL=1.0`）+ 进程间文件锁 + 429 指数退避 + **连续 3 次断连 → 20 小时封禁冷却自动跳过**（参考仓库 PR#36 实战结论）；资金流多域轮换（push2his→push2→push2delay）
- **东财全局节奏（V16.3 O15 方案 A）**：所有东财请求统一跨进程 1.0-1.3s 全局节流（45000 请求/小时封禁阈值余量 30 倍）+ **强制直连**（除 GD 上传外全部忽略系统代理——防 FlClash 机房 IP 封禁）+ push2delay 域破解通道（≤10 字段/请求）
- **字典驱动多源路由（V16.3 N-O）**：field_dict 623 字段/723 字段×源记录 + §零·B 自动生成矩阵（gen_field_matrix.py）；数据源难易度按参考仓库 v3.2 + 实测（ZHB→TDX/腾讯→新浪/巨潮→同花顺→AxData→东财）；统一层多源 fallback 对齐（F10 财务九件套/0x0010 金额角→元/920 北交所路由/腾讯 52周股息率）
- **TDX 服务器白名单**（V16.2.9-V16.2.11）：54 台全量实测收敛为 **5 台 FULL 服务器**（K线/行情/财务三项完整），探测与轮换只遍历白名单；`_tdx_host_data_complete` 原生 API 数据完整性校验 + 北交所 8/4 段拦截 + 5 分钟标的级失败记忆
- **ZHB 字段深度破解**（V16.2.18-V16.3 D）：新股开板日/上市连板数（东财 f189 交叉验证）、涨跌停封单额、主板连板数、profile.dat 历史名称记录（64 字节结构）等字段确认；tdxstat2 Col[13] 重新定性为 **T 日特色板块归属**（非行业）；区间涨跌幅字典修正（不存在 30日/90日字段，injoyai 130 日日线核验）
- **缓存版本化防污染**（V16.2.16+ 铁律）：行业/口径变更必须升级 `@cached` category（如 `industry_peers_v2`），旧缓存不读取；`zhb_data` 等 5 分类旁路（ZHB RAM 字典 <1ms，SQLite 写路径负优化）
- **并发策略 100% 线程池 Worker 隔离**（V15.1）：量化策略完全下沉至 Worker 线程池，解决假 async 协程阻塞主 asyncio 事件循环挂起问题
- **ZHB 旁路剥离与 SQLite 缓存瘦身**（V15.0）：所有 ZHB 静态/估值/财务字段旁路绕走 ZHB 内存，数据库体积从 16.7MB 骤降至几十 KB，彻底消除 `.db-journal` 文件死锁
- **熔断静默降级（Graceful Fallback）**（V15.0）：断路器触发或网络异常时，数据中心静默回退至 ZHB T-1 内存快照，确保报告引擎 100% 不崩溃
- **zhb 全局配置总包**：一次 TCP 下载，全市场静态数据本地解析，零 HTTP 请求
  - **A级数据**：大板块成分、申万行业分类、节假日日历、证监会行业、券商名称表
  - **B级数据**：全市场统计快照（tdxstat 35 字段）、资金流向快照（tdxstat2 21 字段）、财报日历（tipinfo 22 字段），主力资金流向双日 Delta 验证 10/10
  - **辅助数据**：新股申购、A+H股比价、中概股ADR、可转债、退市股对照表、历史名称记录（profile.dat）
- **TDX 双通道**（V12.0 + V15.5）：mootdx 统一 TCP 层 + easy_tdx 1.20.4 适配层首选（服务器健康分引擎 + K线空数据故障转移 + MacClient 板块源）
- **ReportRunner 通用框架**（V12.4-V12.5）：报告脚本共享 `BaseReportRunner` 基类（CLI 解析/Banner/Summary/GD 上传模板/TDX 资源清理）
- **sc_fault_tolerance 容错层**（V12.1）：`TokenBucket` / `CircuitBreaker` / `RandomUAPool` 三大防御机制
- **统一缓存层**（V8.4+）：SQLite + TTL 自动过期 + 交叉验证（`cross_verify`）+ L1 内存缓存 + per-key single-flight + 异步连接复用
- **Config 集中管理**（V12.2）：`config.py` 集中管理网络超时/限流参数/熔断器阈值
- **交易日历判断**（V14.0 修复）：本地 `holidays`/`workdays` 字典（621 条 2004-2026+）作为权威数据，ZHB 仅作为辅助校验
- **云端同步**：Google Drive 自动上传报告，快照文件自动云端备份
- **智能快照管理**：自动生成评分快照，支持跨日期趋势分析和背离检测
- **批量处理**：支持多股票、多报告类型并行生成
- **代码清洗**：自动处理股票代码格式问题（`600519` / `600519茅台` / `600519 茅台`）
- **异步并发**：30+ 异步函数支持高效并发请求
- **类型安全**：mypy 静态检查通过，类型注解完整覆盖
- **测试体系**（V16.3）：17 个测试文件 / **296 项单元测试 100% 通过**（默认离线运行，real_network 标记隔离）；`tests/test_eastmoney_health.py` 13 域健康度矩阵、`tests/test_tdx_health.py` 白名单/适配器覆盖

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
- **Google Drive 上传**：根目录放 `client_secrets.json`，首次运行浏览器 OAuth 生成 `credentials.json`；国内网络需本地代理（gd_uploader 自动探测 7890/10809/1080 等常见端口）
- **同花顺增强**：根目录放 `ths_credentials.json`（`{"username":..,"password":..,"mac":..}`）或设 `THS_USERNAME/THS_PASSWORD` 环境变量；无凭证时 SDK 游客兜底

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
│   ├── run_tests.ps1             # 测试统一入口（AGENTS.md 强制 shell 层中转）
│   ├── update_calendar.py        # 交易日历数据更新（含 V14+ 防覆盖保护）
│   ├── clean_cache.py            # 缓存清理快捷脚本（封装 python -m core.stock_cache）
│   ├── backtest_topn.py          # top_n 回测验证
│   ├── perf_compare.py           # dataclass vs dict 性能压测
│   ├── gen_field_matrix.py       # 字段×源矩阵自动生成
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
├── tests/                        # pytest 测试（按 data/core/reports/infra 分层，见 tests/README.md）
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

### requirements.txt

```
# ── HTTP & 网络 ─────────────────────────────────────────────
requests>=2.25,<3.0
urllib3>=1.26,<3.0

# ── 异步 HTTP ─────────────────────────────────────────────
aiohttp>=3.8,<4.0
aiosqlite>=0.20,<1.0

# ── 数据处理 ─────────────────────────────────────────────────
pandas>=1.0,<3.0
numpy>=1.20,<2.0

# ── 配置解析 ─────────────────────────────────────────────────
PyYAML>=5.4

# ── 行情数据源（核心依赖，必须安装）───────────────────────────
easy-tdx>=1.0,<2.0
mootdx>=0.11,<1.0
pytdx>=1.0  # mootdx 底层依赖；zhb_client 下载 zhb.zip

# ── V16.1.7 新数据源（可选，缺失时自动降级）──────────────────
levistock>=0.1    # 盘口异动/市场情绪/涨停池（字典 §12.10）
axdata>=0.1       # 短线指标/涨跌停规则/筹码分布（字典 §12.12）

# ── Google Drive（可选）────────────────────────────────────
google-auth>=2.0
google-auth-oauthlib>=1.0
google-api-python-client>=2.0
httplib2>=0.22,<0.31

# ── A股日历与交易日判断 ─────────────────────────────────────
chinese-calendar>=1.11

# 单元测试依赖见 requirements-dev.txt（V16.3 起运行时不再声明）
```

### config.py（V12.2 集中管理）

```python
# 网络
HTTP_TIMEOUT_SECONDS = 15
HTTP_TIMEOUT_LONG = 30

# 限流（V16.2 分域体系：域表 _DOMAIN_LIMITS 在 sc_network.py）
TDX_MIN_INTERVAL = 0.1        # 100ms
EM_MIN_INTERVAL = 1.0         # 东财全局硬下限（push2 域 0.4rps 取严）

# 重试
MAX_RETRY_COUNT = 3
RETRY_DELAY_SECONDS = 0.5

# 缓存
CACHE_DB_SIZE_LIMIT_MB = 500

# 容错
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 10
CIRCUIT_BREAKER_RESET_TIMEOUT_SECONDS = 60
# 令牌桶 rps 由 sc_network._DOMAIN_LIMITS 分域管理（push2 系 0.4rps 最严）
```

### Google Drive 配置（可选）

如需启用云端上传功能：

1. 在 Google Cloud Console 创建项目并启用 Drive API
2. 下载 OAuth 2.0 凭证文件，保存为 `client_secrets.json`（项目根目录）
3. 首次运行时会弹出浏览器进行授权，授权后自动生成 `credentials.json`

> **注意**：
> - OAuth scope 为 `drive.file`，脚本只能看到由该脚本自身创建或打开过的文件/文件夹
> - 若 Google Drive 根目录无故出现个股文件夹，通常是桌面客户端同步冲突导致（详见 FAQ），脚本本身不会移动或删除已有文件夹

---

## 核心模块说明

### data_provider.py（V11.5+ 统一数据层）

所有报告 Runner 调用的数据入口，封装 `CanonicalStockData` 强类型合约 + 字段路由 + 4 级 fallback（L0 东财申万二级 → push2 → TDX → ZHB）：

```python
from data_provider import (
    get_canonical_stock_data,    # 强类型合约（每字段带 field_sources 溯源）
    get_stock_composite,         # dict 聚合入口
    get_pe_ttm, get_pb, get_turnover_pct,  # ZHB 字段
    get_market_snapshot,         # 全市场快照
    REQUIRES_REALTIME_HTTP,      # 字段分类常量
    ZHB_SUFFICIENT,              # 字段分类常量
)
```

### stock_common/（V12.0 包，17 个子模块）

**sc_network.py**：网络请求层——分域限流表 `_DOMAIN_LIMITS`（38 域）、push2 系共享归一化桶、`EM_MIN_INTERVAL` 硬下限、进程间文件锁（stale 回收 60s）、429 指数退避、连续 403/断连封禁 20h 冷却、熔断器接入

**sc_datasource.py**：100+ 数据源查询函数（财务/资金流/解禁/行业对比/股东/龙虎榜/互动易/公告/研报/东财申万二级行业映射）

**sc_schema.py**（V13.0）：字段元数据层——`FieldSpec` dataclass、3 个 Enum（`TimeAnchor`/`DataSource`/`Unit`）、`normalize_at_boundary` 单位归一化（股本统一万股/金额统一万元）

**sc_fault_tolerance.py**（V12.1）：容错层
- `TokenBucket` - 令牌桶限流
- `CircuitBreaker` - 熔断器
- `RandomUAPool` - 随机 User-Agent 池

**sc_technical.py / sc_risk.py**（V16.1）：技术指标引擎（MACD/RSI/BOLL/KDJ/MA 均线）与风险扫描引擎（9 项清单）

### stock_cache.py（V8.4+ 统一缓存层）

关键特性：

- **SQLite 持久化**：缓存写入 `cache/stock_cache.db`，支持程序重启
- **L1 内存缓存**：进程内 LRU 字典（上限 10000 条目）
- **TTL 分级策略**：财务 90 天 / 板块 7 天 / 日频 24h / 研报 3 天 等 50+ 分类
- **交易日过期**（V9.1）：F10 高频分类按交易日 15:00 自动过期
- **cross_verify**（V9.2）：多天 TTL 分类两次数据一致才标记已验证
- **per-key single-flight**（V16.2）：同 key 并发 miss 仅一次上游请求
- **版本化防污染**（V16.2.16+）：口径变更升级 category（`industry_peers_v2`）
- **dataclass 透明序列化**（V13.1）：`_serialize_for_cache` / `_deserialize_from_cache`
- **环境变量开关**：`STOCK_NOCACHE=1` 临时禁用
- **CLI 工具**：`python -m core.stock_cache stats` 查看命中率（V17.0 包化后）

```python
from core.stock_cache import cached, invalidate_category, print_cache_stats

@cached(category="dragon_tiger", ttl_seconds=24 * 3600)
def get_dragon_tiger_board(code, days=30, include_seats=True):
    ...

invalidate_category("dragon_tiger")  # 清除某分类
print_cache_stats()  # 查看缓存统计
```

### stock_calendar.py（V14.0 修复）

交易日历模块，支持：

- 中国 A 股交易日判断（含节假日、调休日）
- 本地 `holidays`/`workdays` 字典（621 条 2004-2026+）作为权威数据
- ZHB neednote 补充校验（`is_workday_with_zhb_supplement`）
- 最近/下一交易日查询（`get_last_trading_day`/`get_next_trading_day`）

```python
from stock_common.stock_calendar import is_workday
from stock_common.sc_datasource import get_market_status

# 判断某日是否交易日
if is_workday(date(2026, 1, 1)):
    print("2026-1-1 是交易日")
else:
    print("2026-1-1 是节假日")

# 获取市场状态
status, message = get_market_status()
# status: closed/pre_market/morning/lunch/afternoon/post_market
```

### get_*_report.py（5 大报告脚本 Runner，ful 已于 V16.3 O19 删除）

报告脚本全部继承 `BaseReportRunner`（[stock_common/sc_report_runner.py](stock_common/sc_report_runner.py)）：

- 共享 CLI 解析 / Banner / Summary / GD 上传模板 / TDX 资源清理
- 通过 `from data_provider import get_stock_composite` 统一获取数据
- 各自维护差异化的章节渲染（sht/med/lng/val/mak）

---

## 输出示例

报告文件命名格式：`{股票代码}_{报告类型}_{日期}_{时间}.txt`

```
reports/
├── 600519_sht_20260618_1430.txt    # 茅台短线报告
├── 600519_med_20260618_1435.txt    # 茅台中线报告
├── 600519_lng_20260618_1440.txt    # 茅台长线报告
└── get_val_report_20260618_1445.txt # 估值汇总报告
```

---

## 📋 版本历史

完整版本历史详见 [CHANGELOG.md](CHANGELOG.md)。

> ✨ **V17.0.1**（2026-08-15）
> **补丁: 字段增强实施(P0-P4) + 三轮代码审查闭环 + 全量 md 化 + 运行修复**
>
> - **mak**: 主力净额 ulist 批量 f62+f66(=f137+f140 特大+大单, 20/20 实锤, push2delay 域, 元口径带符号)→
>   板块聚合/A 段看板同源; 北向宏观资金(to_thread+降级标记)
> - **sht**: 连板追踪 ZHB[31] 真连板数(双日铁证)+涨停类型[33]+官方封单额[4]; 3日涨幅估算降兜底
> - **val**: 21→23 策略——策略22 业绩预增(get_yjyg_all 全市场分页, ADD_AMP/IS_LATEST/日期缓存)+
>   策略23 盈利预期(本机 ProfitForecast O(1) 索引+股东户数 local_only)
> - **lng**: 机构一致预期(本机 ProfitForecast 优先)
> - **数据层**: zhb_client 暴露涨停族; get_em_batch_quotes +f62/f66(secids 参数修复);
>   get_eps_forecast 本机索引+local_only; get_yjyg_all; eastmoney_datacenter page_index
>
> - **CRITICAL 类**: mak 主力单位 1e4 倍; data_provider TDX 兜底 T-1 单位 10000x;
>   med 北向占比 100 倍; get_eps_forecast 缓存失效+5000 次扫描; ulist 参数 fs→secids(data:null);
>   **val bypass 模式 price 全缺 → 10 策略 0 命中**(.day 尾部快速读补价, 终审修正 ÷1000→÷100);
>   mak A 段 ZHB 兜底单位; GD 补传脚本 .md 适配
> - **限流**: get_em_batch_quotes push2 主域→push2delay 镜像域; get_yjyg_all 全市场一次分页;
>   strategy_23/holder_change local_only 禁网络; mak/val async 阻塞 to_thread 4 处
> - **缓存**: ProfitForecast O(1) 索引+锁; 业绩预告日期缓存; _KLINE_PRICE_CACHE
> - **契约**: holder_num/ADD_AMP/IS_LATEST/zt_type 0 值 等
>
> - 新增 stock_common/md_render.py 渲染层转换器(标题/分隔线/F10 边框表/空格表数据驱动切分/安全回退);
>   5 脚本写尾 render_md_report, 输出 .md(纯文本兼容); val [NN 名称] 标题支持
>
> - 269 passed / 45 deselected, 0 failed
>
> ---

> 📊 **V17.0**（2026-08-13）
> **里程碑：全盘重构(core/ 包化 + v9.6 清理) + 字段命名规律破解 + 运行核查修复。**
>
> - 7 支撑模块包化 `core/`(全仓 ~150 import 统一 `from core.X`, `__init__.py` 空防循环, CLI 改 `-m`)
> - v9.6 遗产清理(目录/SKILL/3 对比工具/孤儿 db); 凭据归位 `credentials/`; README 体系补全(45 条目→分层)
>
> - **S1 死代码 ~1000 行**: 21 zhb 转发+sc_zhb+12 dp 包装+composite 链 220 行(__all__ 255→230)
> - **S2 传输层统一**: _request_with_retry→_quick(别名+4 点迁移); _async_quick EM/GEN 分流(限流语义保留); 进程间隔 2 核心+4 薄包装
> - **S3 市场代码**: em_secid_prefix(修北交所 92 secid bug); is_a_stock 下沉; _market_code 补沪 B
> - **S4 数据源合并**: getharden 三版合一(get_ths_hot_raw 唯一入口); cninfo 公告下沉(keywords 参数)
> - **S5/S8 样板**: 写尾/ST 标注/多评委(sc_render)公共化; 缓存适配器删除
> - **批量骨架收敛**: 基类 `execute_batch_pipeline`(prefetch/快照/上传钩子); ts 基类统一
>
> - **双源实锤 20+ 组**: ConZAFDateNum=streak_days、ZAFYear/Pre20/Pre60=ytd/20d/60d、Yield/OpenAmo=主力净流入(双单位)、
>   gb_info Zgb/Ltgb 股本、f137-146 四档资金流全定位、f162=动态PE/f163=静态PE(TTM)(茅台 Q1 年化精确)、
>   f174/f175=52周(腾讯 [67]/[68] 三源一致)、f191=委比%(原"×100"修正)
> - **"N日"口径实锤**: change_5d-60d/ytd 全交易日(开盘日)口径(日K 精确匹配); change_30d=历史遗留 key(实为 20 日值)
> - **tdxstat2 [4]/[6]/[8]=涨停封单额三日滚动**(涨停池 92/92 全覆盖); 21 列全映射
> - **通达信行业体系**: 细分行业=X 码(名称≈申万三级); ZHB [13]=881 行业板块/880 概念·风格双段; 地区不在 ZHB
> - **vzangsu=量涨速%(TDX 表头同名实锤)**; ZAFPre 系列口径(PreN=交易日区间/D=当日/MyMonth=上月最后交易日)
>
> - 主力净流入**全链统一 f137**(腾讯 tx75 反向警示入字典); PE 动态=f162(腾讯静态剔除); 行业仅认 881 段(防 880 概念污染)
> - main.py 固定超时→**输出活性检测**(持续输出无限等待, 无输出 900s 判卡死); sht 上传与 med/lng 统一
> - 性能: prefetch 命中跳过 TDX; push2delay 补取进程缓存(同股二次 2.3x)
> - 测试隔离: conftest 补拦 Session.get/post
> - script_data_dict.md 全量重写; 全量回归 **302 passed / 45 deselected, 0 失败**
>
> > 详细执行轨迹: docs/V17.0_REFACTOR_PLAN.md / docs/field_verification/20260813/(analysis+映射表) / docs/session_notes/20260813.md

> 🐛 **V16.4.1**（2026-08-12）
> **里程碑：字段实测验证流水线落地 + TdxQuant 官方 88 字段交叉破解 + 报告数据质量 19 项修复 + 编码体系治本。**
>
>
> - **固定股票池** `docs/field_verification/pool.json`：20 股(固定 15 + 动态 5,沪深/创业/科创/北交所/ST/银行/连板全覆盖)
> - **采集脚本** `scripts/capture_field_probe.py`：19 源全字段(本地 ZHB + TDX/F10 + 腾讯 88 + push2 114 + ulist 239 + 新浪 34 + AxData 34 + 财联社/KPL/板块轮动/涨停池/人气榜/datacenter/巨潮/研报/thsdk/TdxQuant)
> - **首次采集** `docs/field_verification/20260812/`：19 raw 文件 + meta + analysis + field_analysis
> - **防封**:push2 失败不重试 + 连续 3 只失败域级熔断切 push2delay(2026-08-12 二次封禁复盘根因:失败连接重试叠加 ~300 次)
> - **sc_datasource.em_hot_rank** push2 → push2delay 镜像域(封禁期整体失败修复)
>
>
> - **18/18 实锤**:Col[3]=StaticPE_TTM(pe_dynamic 历史遗留名)、Col[9]=MorePE、Col[10]=DYRatio、Col[14]=KfEarnMoney、Col[15]=StaffNum、Col[24]=CashZJ(**单位=万元,原"(元)"错误**)、tdxstat2[16]=IPO_Price、[17]/[18]=HisHigh/HisLow
> - **破解**:tdxstat [26]=YearZTDay 年内涨停天数(18/18)、[32]=LastZTHzNum(2/2)、[31]≈LastStartZT、[23]=当日异动类型码、tdxstat2 [4]/[6]/[8]=同一资金字段三日滚动序列(T/T-1/T-2)、tipinfo [10]=DTDate_Recent
> - **tipinfo 官方字段名实锤**(600519 单样本):Col[5]=ZTDate_Recent、[6]=TopDate_Recent、[13]=RecentReleaseDate、[19]=RecentHGDate
> - **采集**:`C:\new_tdx64\PYPlugins\user\field_verify_tdxquant.py`(需通达信客户端运行)
> - field_dict.md 全量回写 + 精简(多轮测试描述压缩为"含义+状态+一句证据")
>
>
> - **ZHB 下载永不更新**:`_zhb_needs_download` 循环依赖(stock_calendar.is_workday 反向调 get_zhb → 递归爆栈)→ 改用本地包节假日表;+"每天最多下载一次"标记(成功才标记)
> - **val 崩溃 KeyError('zhangfu')**:get_val_report L1880 复制粘贴残留(`_th["zhangfu"]` 在 elif 分支必崩)
>
>
> - **sht GD 丢失**:36 只批量超时被 kill 时批量上传未执行 → 改**逐只上传**(提前 init_gd,生成即传)+ main.py 单股超时 30s→45s
> - 封板时间 "92:50" 格式错(5 位字符串切片)→ 统一 int 解析
> - 新股首日无涨跌幅限制(+662%)→ mak 上市<3 日跳过偏离判定 + val 标注
> - sht 主力资金占比 222%(abs 掩盖方向)→ 保留符号+超成交额异常标注+来源标签修正
> - 北向 degraded 警告未展示(深股通 379 亿异常)→ sht/med 渲染 data_quality 警告
> - med 资金流仅 1 天却下"吸筹"结论 → <5 天数据不下中线结论
> - lng:人效比单位 元→万元、PE-TTM 来源口径标注、PEG 跨期标注、分红"距今 N 年"、互动易答案 None、净利率>100% 双源核验标注
> - val 策略09 名称当代码(昀冢科技 (昀冢科技))→ 无 6 位代码 leader 走成分股路径
> - med 同业本股 *ST 名称统一;同业亏损股 PE 显示"亏损"(原 0.0)
>
>
> - **GD 补传工具** `scripts/upload_reports_to_gd.py/.bat`(reports/ 自包含副本):已存在跳过只传缺失,实测 39 上传/6 跳过/0 失败
> - **编码体系治本**:
>   - Python 入口全量 `ensure_utf8_stdio()`(env_setup.py 下沉,17 入口)
>   - .ps1 四行 UTF-8 头部 + **BOM 铁律**(PS 5.1 无 BOM 按 GBK 解析)
>   - **管道禁令**:禁止 python 输出接 PS 管道(PS 5.1 分块解码破坏多字节字符,实测根因)
>   - bat 纯 ASCII+CRLF 铁律(cmd 按 ANSI 解析 UTF-8 中文注释致整文件错乱)
> - **AGENTS.md v1.2 重构**:合并落盘规则、清理过时内容/已完成待办、修正 bash grep/废弃变量引用
> - **每日会话纪要体系**:`docs/session_notes/YYYYMMDD.md`(详见 docs/session_notes/README.md)
>
>
>
> **里程碑：字典架构重构 + 三大客户端逆向（东财/通达信/同花顺）+ 统一层加固 + 场景化批量优化。**
>
>
> - `docs/verify/` 附录目录：主字典只留结论，实测值/样本/破解数据迁入附录
>   - push2_verify（12.9.1 全字段破解表）/ axdata_verify（666 字段矩阵）/
>     samples_verify（24 股样本）/ tencent_verify（88 字段复核）
>   - field_dict 358KB→284KB（-21%）；12.15.9 附录索引表
> - **script_data_dict 全量重构**：5 脚本行号重定位（mak 1798/val 2131/sht 1740/med 1256/lng 1135）
>   + 逐字段 fallback 链实测更新 + §七 12 项断点（8 项已修）
> - **客户端逆向三附录**（统一 docs/verify/）：
>   - `network_servers.md`：三源服务器清单（通达信 connect.cfg 全表 HQHOST 43/
>     同花顺 123ths 域名族 9 域 ~80 IP/东财 SSO）+ 移动线路实测
>   - `client_fields_enum.md`：客户端字段枚举全景（东财 950+/通达信 tdxstat
>     35 列破 14/tdxstat2 21 列破 13/同花顺 F10 文本+thsdk 口径铁证）
>   - 数据文件入库 `docs/verify/data/`（connect_cfg/dns_cache/复测结果）
>
>
> - mak：9.5 涨停分档×3 统一 limit_pct_for、板块 mcap_yi 腾讯注入+计算兜底、
>   main_net_amount 取 ZHB、盘口异动死代码移除
> - val：_sfmt 01-21 映射重建（14 号回归）、行业排名升级 O25（四脚本收敛唯一实现）
> - sht：地天板预警 limit_down_price 修正、ff.iloc 死分支、**bid1_vol 入 canonical
>   全链路**（封单资金/信号/预警复活）、_is_dict 死分支清理
> - **PB 口径统一**：val 04 pb_ths 降级校验，全脚本收敛 canonical（腾讯/push2
>   除息口径），THS 静态口径仅差异告警
>
>
> - **通达信 tdxstat/tdxstat2 官方原始文件 35/21 列破解**：ipo_price（茅台 31.39）、
>   52周高低（=腾讯精确）、PE 双口径（Col[3]=动态/Col[9]=TTM 实时验证）、
>   涨跌幅序列（5/10/20/30日 + ytd 多股全中）、amount_1d/2d（昨日/前日成交额）
> - **同花顺**：123ths 域名族、stockname 名称库、F10 文本库（五期财务）、
>   **thsdk 市净率=现价/最新期 BPS 铁证**（F10 文本 4 位小数精确）、
>   get_ths_market_snapshot query_key 修复（汇总→扩展1）
> - **TDX 服务器 74 台复测**：FULL 6 台（新增 120.76.152.87），白名单更新
> - 东财 DataCenter.dll 725 协议字段 + 自选 118 字段三层映射
>
>
> - **share_capital 旧单位 bug**：6467 条"股"单位缓存（V16.2.3 修正前 8-03 批次）
>   导致 canonical mcap 放大 1e4——清理 + **缓存 schema 版本化**（规范变更自动失效）
>   + **canonical 量级校验**（股本>1e7 自动股→万、mcap>1e6 自动万→亿，与 pe 过滤对称）
> - zhb_client tdxstat 映射与 12 股 F10 验证 100% 吻合（统一层无需改代码）
> - 缓存同步：tdx_hosts_cache 6 台 FULL
>
>
> - **prefetch_quote_batch**（push2delay ulist 300/批）：sht 批量 1-2 次请求预取
>   30 只核心行情，canonical 命中跳过 TDX 逐股；估值字段按需腾讯单股补齐
>   （实测 ulist 不返回估值字段）
> - 矩阵增加场景维度：单股深度（TDX 优先）/ 批量行情（ZHB+腾讯批量）
> - UA 补全标准浏览器指纹（5 处）+ 东财 IP×子域封锁排查（push2 系与 delay/ex 独立）
>
>
> - 全量测试 339 passed, 2 skipped（多次基线一致）
> - 东财接口健康探测脚本 `scripts/check_em_health.py`（低频防封锁）
> - AGENTS.md §12 活跃待办（push2his 恢复复测提醒）
>
>
>
> - **[16.3.8]** (2026-08-11): 东财 IP 封锁排查 + 新 IP 恢复核验（换光猫后）。
> - **[16.3.7]** (2026-08-11): PB 口径统一：val 04 双通道收敛（回应统一层设计初衷）。
> - **[16.3.6]** (2026-08-11): PB 多源实证归因 + THS 批量通道修复（盘中三股实测）。
> - **[16.3.5]** (2026-08-11): 行业排名统一收敛 O25 + 资金流单位契约清理（回应字典 §七 剩余项）。
> - **[16.3.4]** (2026-08-11): 脚本断点修复 8 项（script_data_dict §七 12 项中 8 项落地）+ bid1_vol 入 canonical 全链路。
> - **[16.3.4]** (2026-08-11): script_data_dict 全量重构：5 大脚本按当前代码重定位（ful 删除确认）。
> - **[16.3.3]** (2026-08-11): 字典架构重构：主字典=决策层，附录=实证层。
> - **[16.3.1]** (2026-08-06): V16.3 O 系列：F10 财务接入 + 字典全面破解 + 东财限流治本 + 统一层梳理。
> - **[16.3.0]** (2026-08-05): 全项目审查整改（74 文件核查，用户批准全改）+ 文档/依赖清理。
> - **[16.2.0]** (2026-08-05): V16.2.1-V16.2.18 连续迭代：报告正确性 + 东财分域限流 + 缓存版本化 + 行业统一申万二级 + ZHB 字段破解。
>
>
> | 版本 | 日期 | 里程碑 |
> |:---|:---|:---|
> | 16.1.9 | 2026-08-05 | ST 涨跌幅规则修正（5%→10%）。V16.1.7 曾误按 AxData 文档旧快照 `st_5pct` 将 ST 阈值改为 5%； |
> | 15.4.3 | 2026-07-31 | easy_tdx 字段探测 + tdx_field_dict 字典 + V15.5 移植规划。基于用户反馈"全部更换为 mootdx 接口后数据获取并不稳定"，调研 [easy_tdx v1.20.4 |
> | 15.3 | 2026-07-29 | 全量健康修复版本。基于 2026-07-29 跑 000100 时的全量根因分析（X1-X8 共 8 个 P0/P1），结合第三方 deepseek 评审报告的逐条核查，对剩余 9 个 P0/P1 + |
> | 15.2 | 2026-07-28 | P0 崩溃修复 + 缓存保护强化 + ZHB 交叉验证恢复版本。基于 2026-07-28 20:29 批量运行日志的深度根因分析，重点修复 V15.1 引入的 `board` 变量未初始化导致的 3 |
> | 15.1 | 2026-07-26 | 全全局 ZHB 旁路普及与并发线程池隔离深化版本。将基于真实周期的 ZHB 时空路由矩阵全面普及至 6 大报告脚本（`sht`/`med`/`lng`/`ful`/`mak`/`val`），修补盘后  |
> | 15.0 | 2026-07-26 | 标准化数据中心与 ZHB 离线优先架构重构大版本。完全收敛多源行情异构数据，引入强类型数据合约 `CanonicalStockData`，实施基于真实生成周期（T+1 清晨 06:00 前）的 ZHB |
> | 14.0 | 2026-07-22 | V13.x Bug 修复 + 文档全量同步版本。不引入新功能。 |
> | 14.2 | 2026-07-22 | ZHB 数据集深度集成版本。基于 `field_dict.md` 第三节第 4 小节新挖掘的 6 个 ZHB 数据集（profile.dat / tdxchain.cfg / neednote.dat |
> | 14.2.1 | 2026-07-22 | Gemini 深度静态分析后修复的 3 个边界隐患 + 1 个架构一致性提升。不改变 VERSION 编号（仍是 14.2）。 |
> | 14.3 | 2026-07-25 | 性能优化版本。针对 val 报告周日首次跑 15 分钟卡死的实际问题，从 P0/P1/P2/P3 四个层面完整解决"网络请求风暴"问题。 |
> | 14.3.1 | 2026-07-25 | 根据用户对缓存机制的两点深入分析，对 V14.3 缓存架构进行精细化重构。不改变 VERSION 编号（仍是 14.3）。 |
> | 14.3.2 | 2026-07-25 | Top-N 数据驱动回测。用 4 天 ZHB 数据（cache/zhb/zhb_202607{21,22,23,24}）回测 12 个策略在不同 top_n 下的选股质量，给出"按策略差异化 top_ |
> | 14.2.2 | 2026-07-25 | 针对 Gemini 报告的两个实际运行异常（`val` 脚本 `NameError` + `mak` 脚本 `0只` 与卡死），进行深度根因修复。不改变 VERSION 编号（仍是 14.2）。 |
> | 14.2.3 | 2026-07-25 | V14.2.2 的修复不完整——`_check_tdx()`（健康检查函数）仍使用 `bestip=True`，导致 val 报告（`strategy_10_contrarian_value` 调用  |
> | 13.2 | 2026-07-22 | 无重大破坏性变更。V13.2 仅追加文档与脚本。 |
> | 13.2 | 2026-07-22 | V13.0/V13.1/V13.2 三阶段引入 dataclass 形式的数据容器，作为 V12.x dict 的可选升级路径。 |
> | 13.0 | 2026-07-22 | 无重大破坏性变更。V13.0 仅新增 `stock_common/sc_schema.py` 模块，不接入 data_provider。 |
> | 13.1 | 2026-07-22 | V13.1 涉及缓存层行为变化（潜在影响）： |
> | 12.6 | 2026-07-22 | V12.6 取消原计划的防投毒熔断机制（V11.5 时期实施），存在以下行为变化： |
> | 12.5 | 2026-07-22 | V12.5 针对 V12.4 复盘发现的 3 大问题进行修正：消除 `get_med_report.py` / `get_lng_report.py` 中重复定义的 Runner 类、让基类 GD 上 |
> | 12.3 | 2026-07-22 | V12.3 原计划引入三项深度架构演进，但在评估后决定挂起，未实际实施： |
> | 12.4 | 2026-07-22 | V12.4 成功构建并全面应用 `BaseReportRunner` 引擎框架，彻底剥离6大策略报告脚本中约 1200+ 行重复的 CLI 解析、运行生命周期 Banner、Google Drive  |
> | 12.2 | 2026-07-22 | V12.2 完成工程化优化任务清单，包括数据库连接优雅关闭、配置集中管理、全局异步Session单例、核心防线单元测试、三级日志规范落地。 |
> | 12.1 | 2026-07-22 | V12.1 针对全量代码审查发现的问题进行修复，包括 L1/L2 缓存同步 Bug、静默异常日志化、容错层实际下沉、异步阻塞修复、未使用导入清理。 |
> | 12.0 | 2026-07-17 | V12.0 完成 TCP 统一层重构，彻底删除 easy_tdx 依赖，实现"HTTP + mootdx"双通道架构。所有原 easy_tdx/MacClient 独有功能（板块、资金流、全市场快照） |
> | 11.5 | 2026-07-17 | 历时多个版本规划，data_provider.py 统一数据中心层在 V11.5 正式全面激活，六大报告脚本全部完成迁移。同时新增三大防封机制，彻底提升网络稳定性。 |
> | 11.4 | 2026-07-16 | 1. data_provider.py死代码清理：6个报告脚本（sht/val/med/lng/mak/ful）共47处`from data_provider import (...)`导入语句全部删 |
> | 11.3 | 2026-07-16 | 通过7/15 vs 7/16报告对比发现，4个缓存分类在跨日运行时携带T-1数据混入T0报告： |
> | 11.2 | 2026-07-16 | - clean_codes增加flag粘连警告：当股票代码参数中包含`--`时（如`601718际华--all`缺少空格），打印警告提示用户检查命令行格式，避免`--all`参数被误解析为股票代码 |
> | 11.1 | 2026-07-16 | 1. 全市场成交额实时覆盖：val脚本加载全市场数据时，用腾讯实时行情的`amount_wan`覆盖ZHB的T-1成交额，确保流动性排序和策略计算使用当日数据 |
> | 11.0 | 2026-07-16 | - 所有报告脚本统一导入 Data Provider 模块： |
> | 10.3 | 2026-07-16 | zhb 资金流向字段解锁（基于 zhb_analysis 深度分析 + 双日 Delta 验证 + 公式验算）： |
> | 10.2 | 2026-07-16 | - 修复 cross_verify 读写互斥BUG（影响14个分类：concept_blocks/lockup_expiry/basic_info/financial/balance_sheet/ca |
> | 10.1 | 2026-07-15 | - zhb字段映射重大修正（基于injoyai/tdx开源仓库源码验证）： |
> | 10.0 | 2026-07-14 | - zhb全局配置总包全面升级： |
> | 9.6 | 2026-07-13 | - mootdx依赖集成：`requirements.txt` 新增 `mootdx>=0.11,<1.0`，与 easy-tdx 形成互补关系 |
> | 9.5 | 2026-07-13 | - 静默异常日志化（28处）：`tdx_client.py`（23处）、`gd_uploader.py`（4处）、`get_med_report.py`（1处）共28处 `except Excepti |
> | 9.4 | 2026-07-11 | - VERSION文件单一来源版本号管理：项目根目录新增 `VERSION` 文件（内容为 `9.4`），`stock_common/sc_utils.py` 新增 `get_version()` 函 |
> | 9.3.3 | 2026-07-10 | - GD上传路径混乱：`get_or_create_drive_folder` 增加 `'{parent_id}' in parents` 严格约束，`get_val_report.py` 移除 `g |
> | 9.3.2 | 2026-07-09 | - TDX K线假数据导致指数涨幅全N/A和异动检测全为0：约50%的 easy_tdx 内置TDX服务器K线接口返回假数据（响应头 `ret_count=800` 但 body 为 0 字节），导致 |
> | 9.3.1 | 2026-07-08 | - sht 脚本 `'float' object is not subscriptable` 崩溃：`ff["data"]` 存在多态（TDX 返回 `List[dict]`、东财 fallback  |
> | 9.3.0 | 2026-07-07 | - 盘前行情模式（`tdx_client.py`）：9:30前自动使用上一交易日日K线数据，避免实时接口返回 0 导致涨跌幅计算为 -100% |
> | 9.2.0 | 2026-07-05 | - 缓存交叉验证机制（`stock_cache.py`）：11 个多天 TTL 分类启用 `cross_verify=True`，两次获取数据一致才标记为已验证，防止意外错误数据被缓存 |
> | 9.1.1 | 2026-07-04 | - ful 评分 theme→holder 映射 bug：`get_ful_report.py` 中 `_scoring()` 返回值用 `"theme"` 作为键名，但实际取自 `dims.get( |
> | 9.1.0 | 2026-07-04 | - F10 全覆盖工程：用通达信 F10 协议替代/补充现有 HTTP 接口，降低东财限流风险，详见 `docs/TDX_F10_ROADMAP.md` |
> | 9.0.0 | 2026-07-02 | - 舆情互动层（Layer 10）：新增 `cninfo_irm()`（互动易问答）、`ths_hot_list()`（同花顺热榜）、`em_hot_rank()`（东财人气榜）、`em_hot_co |
> | 8.9.0 | 2026-06-29 | - 版本号统一升级：所有脚本版本从 V8.8/V8.7 统一升级到 V8.9 |
> | 8.8.0 | 2026-06-25 | - GD上传逻辑统一化： |
> | 8.7.0 | 2026-06-25 | - 删除 `social_sentiment.py`（6 平台社交热榜聚合，全为桩实现返回空数据） |
> | 8.6.0 | 2026-06-24 | - stock_common.py：新增 _DOMAIN_LAST_TIME 线程锁保护，彻底消除多线程竞态条件 |
> | 8.5.0 | 2026-06-22 | - 新增龙虎榜席位增强模块 `seat_db.py`： |
> | 8.4.0 | 2026-06-22 | - 新增 `stock_cache.py` 统一缓存层（SQLite + TTL 自动过期 + LRU 清理） |
> | 8.3.0 | 2026-06-18 | - 修复北向资金持股占比显示超100%问题（`get_sht_report.py`/`get_med_report.py`中`_ratio*100`改为`_ratio`，东方财富API返回的`hold |
> | 8.2.0 | 2026-06-18 | - 修复 `300274` 等股票因 lines 列表中存在 None 值导致 `join()` 报错的问题（在所有脚本的 `join()` 调用前添加 `filter(None, lines)` 防 |
> | 8.1.0 | 2026-06-18 | - 新增统一评分接口：`ScoreData` 数据结构、`ScoreResult` 结果结构、`calculate_score()` 主函数，统一管理 sht/med/lng/ful 四种评分类型的计 |
> | 8.0.0 | 2026-06-17 | - 初始版本，包含6个报告脚本（sht/med/lng/ful/val/mak） |

---

## 开发指南

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/tsy1102/a-stock-data.git
cd a-stock-data

# 安装依赖
pip install -r requirements.txt

# 安装开发工具（可选，用于静态类型检查与代码格式化）
pip install -r requirements-dev.txt

# 运行测试（shell 层强制走 run_tests.ps1）
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

- **报告数据与最新行情不一致？**：可能是缓存命中了过期数据，执行 `STOCK_NOCACHE=1 python main.py ...` 临时禁用缓存再测一次；或调用 `python stock_cache.py clear --category dragon_tiger` 清理对应分类。
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