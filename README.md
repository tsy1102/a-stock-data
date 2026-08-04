# A股个股分析报告生成系统

一套自动化生成A股个股分析报告的Python工具集，支持短线、中线、长线、完整、估值、市场热点等多种报告类型，数据来源于新浪财经、东方财富、同花顺等主流平台。

---

## 功能特性

- **5种报告类型**（V16.1: ful 下线）：短线(sht)、中线(med)、长线(lng)、估值选股(val)、市场状态(mak)
- **标准化数据合约对象**（V15.0-V15.2）：`CanonicalStockData` 不可变强类型合约，封装 50+ 核心数据字段及元数据溯源标签（`data_source`/`time_anchor`），彻底消除异构多源数据冲突
- **基于真实周期的 ZHB-First 离线优先路由**（V15.1 全局普及）：
  - 盘前（`<09:30`）与休市日：100% 走 ZHB 本地内存秒级提取，零网络开销（完美利用清晨生成的最新 ZHB 文件包）
  - 交易日 `09:30-24:00`（含盘中与盘后）：行情与资金流字段 100% 强制走网络 HTTP/TDX 接口，确保获取 T 日真实收盘价
- **并发策略 100% 线程池 Worker 隔离**（V15.1）：量化策略完全下沉至 Worker 线程池，解决假 async 协程阻塞主 asyncio 事件循环挂起问题
- **全局 5 大报告脚本 ZHB 旁路普及**（V15.1）：中线脚本财报数据与长线 52周/分红数据 100% 走 ZHB 静态层内存解析，单股分析耗时大幅提升 80%
- **ZHB 旁路剥离与 SQLite 缓存瘦身**（V15.0）：所有 ZHB 静态/估值/财务字段旁路绕走 ZHB 内存（`<0.001ms`），删除废弃磁盘 Key，数据库体积从 16.7MB 骤降至几十 KB，彻底消除 `.db-journal` 文件死锁
- **熔断静默降级（Graceful Fallback）**（V15.0）：断路器触发或网络异常时，数据中心静默回退至 ZHB T-1 内存快照，确保报告引擎 100% 不崩溃
- **6 大报告引擎全量重构**（V15.0）：所有报告脚本统一绑定 `CanonicalStockData` 强类型数据合约
- **zhb 全局配置总包**：一次 TCP 下载，全市场静态数据本地解析，零 HTTP 请求
  - **A级数据**：大板块成分、申万行业分类、节假日日历、证监会行业、券商名称表
  - **B级数据**：全市场统计快照（tdxstat）、资金流向快照（tdxstat2），含主力资金流向字段（tdxstat2[9/10/14/15]，双日 Delta 验证 10/10 + 公式验算误差<1%）
  - **辅助数据**：财报日历、新股申购、A+H股比价、中概股ADR、可转债、退市股对照表
- **TDX 双通道**（V12.0 + V15.5）：mootdx 统一 TCP 层；easy_tdx 1.20.4 适配层首选（服务器健康分引擎 + K线空数据故障转移 + 52 候选服务器 + MacClient 板块源）
- **ReportRunner 通用框架**（V12.4-V12.5）：6 大报告脚本共享 `BaseReportRunner` 基类（CLI 解析/Banner/Summary/GD 上传模板/TDX 资源清理），样板代码减少 ~700 行
- **sc_fault_tolerance 容错层**（V12.1）：`TokenBucket` / `CircuitBreaker` / `RandomUAPool` 三大防御机制
- **统一缓存层**（V8.4+）：SQLite + TTL 自动过期 + 交叉验证（`cross_verify`）+ L1 内存缓存 + 异步连接复用
- **Config 集中管理**（V12.2）：`config.py` 集中管理网络超时/限流参数/熔断器阈值
- **交易日历判断**（V14.0 修复）：本地 `holidays`/`workdays` 字典（621 条 2004-2026+）作为权威数据，ZHB 仅作为辅助校验
- **云端同步**：Google Drive 自动上传报告，快照文件自动云端备份
- **智能快照管理**：自动生成评分快照，支持跨日期趋势分析和背离检测
- **批量处理**：支持多股票、多报告类型并行生成
- **代码清洗**：自动处理股票代码格式问题（`600519` / `600519茅台` / `600519 茅台`）
- **异步并发**：30+ 异步函数支持高效并发请求
- **类型安全**：mypy 静态检查通过，类型注解完整覆盖
- **异常处理规范**：无裸 `except:`，所有静默异常均加日志，Ctrl+C 可正常终止
- **测试体系**（V15.0 精简规整）：11 个核心测试文件 / 245 项单元测试 100% 通过（默认离线运行）
- **P0 崩溃修复 + 缓存强化**（V15.2 2026-07-28）：
  - 修复 `get_canonical_stock_data` 中 `board` 变量 `UnboundLocalError`，恢复 39 只 sht/med/lng 股票数据生成
  - 统一 `valid_if` 工厂函数 `make_valid_if()`，8 个 F10 + 2 个 dragon_tiger + 12 个 zhb_data 函数补 valid_if
  - 恢复 V10.0/V12.6 期间简化的 ZHB 交叉验证 + 两次获取一致机制
  - val 1000s 性能优化：L1 缓存 5000→10000 + 22 策略去重循环
  - GD 上传 stdout 缓冲修复：`init_gd` 非交互模式自动跳过 + `main.py` 子进程 stdout=PIPE
  - `ths_hot_reason` HTTP 失败降级，避免依赖 hot_pool 的 9 个策略 0 命中
  - `stock_cache.py clear` CLI 增强：支持按 category 清理
- **0x0010 协议 key 修正**（V15.1）：`zongguben`/`liutongguben`/`gudongrenshu`/`jinglirun`/`jingyingxianjinliu`（V15.0 引入的下划线错配已修正）
- **tdxchain.cfg 重写**（V15.1）：实测 80 行，格式为 `板块代码|chain_id|产业链名称`，重写 `_parse_tdxchain` 为板块代码→名称映射
- **industry 字段改用 TDX boards**（V15.1）：ZHB dict 不含 industry 字段，统一改用 `tdx_get_belong_boards`

---

## 快速开始

### 环境要求

- Python 3.9+
- Windows / macOS / Linux

### 安装依赖

```bash
pip install -r requirements.txt
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
| `--sht` | 短线交易执行 | 涨跌停边界、当日资金流、昨日涨停晋级率、龙虎榜席位、封单强度（V16.1: push2 官方字段） |
| `--med` | 中线业绩兑现 | 报告期绑定财务、研报评级变化、两融 3/5/10 日维度、技术面 MACD/RSI/BOLL/KDJ |
| `--lng` | 长线企业质量 | 多期财务纵深、分红连续性、风险扫描（解禁/减持/质押）、现金流验证 |
| `--val` | 全市场候选发现 | 21 策略分层扫描（ZHB 初筛 → 扩展字段候选 → 深度确认） |
| `--mak` | 市场状态引擎 | 市场宽度、四池、行业轮动、资金验证（V16.1: 移除伪回测表述） |
| `--ful` | ~~完整报告~~ | **V16.1 已下线**：能力并入 sht/med/lng（技术/风险引擎迁移至 sc_technical/sc_risk） |

> V16.1：`--ful` 参数保留但不再生成报告（报友好提示）。技术指标引擎（MACD/RSI/BOLL/KDJ）与风险扫描引擎（9 项清单）已迁移至 `stock_common/sc_technical.py` / `sc_risk.py` 供 sht/med/lng 复用。

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
├── main.py                       # 主入口程序（参数分发/多报告并行）
├── VERSION                       # 项目版本号（V15.2，单一来源）
├── config.py                     # V12.2 全局配置集中管理（超时/限流/熔断/防投毒）
├── data_provider.py              # V11.5 统一数据层（字段路由 + ZHB 优先 + 批量调用）
├── zhb_client.py                 # 通达信 zhb.zip 全局配置总包下载与解析
├── zhb_sync.py                   # V10.3 ZHB 自动化入库管道（定时/手动/状态）
├── tdx_client.py                 # V12.0 mootdx 统一层 + 自封装 TCP（K线/F10/资金流）
├── stock_cache.py                # V8.4 统一缓存层（SQLite + L1 内存 + TTL + cross_verify）
├── gd_uploader.py                # Google Drive 上传（google-auth + google-api-python-client）
│
├── stock_common/                 # V12.0 核心模块包（5 个子模块）
│   ├── __init__.py               # 包入口，统一导出接口
│   ├── sc_datasource.py          # 数据源查询模块（60+ 函数）
│   ├── sc_network.py             # 网络请求层（限流/重试/代理）
│   ├── sc_utils.py               # 工具函数（get_version/_safe_float/_load_settings 等）
│   ├── sc_scoring.py             # 统一评分接口（ScoreData/ScoreResult）
│   ├── sc_fault_tolerance.py     # V12.1 容错层（TokenBucket/CircuitBreaker/RandomUAPool）
│   ├── sc_schema.py              # V13.0 字段元数据层（FieldSpec + 3 个 Enum）
│   ├── sc_capital_cache.py       # V10.1 全局股本缓存（90 天 TTL）
│   ├── sc_report_runner.py       # V12.4 BaseReportRunner 基类
│   ├── stock_calendar.py         # 交易日历模块（含 holidays/workdays 字典）
│   ├── strategy_config.yaml      # 统一策略参数配置
│   ├── keywords_config.yaml      # 公告关键词配置
│   ├── analyze_history.py        # 评分快照分析与趋势背离检测
│   ├── f10_parser.py             # F10 数据解析模块
│   ├── seat_db.py                # 龙虎榜席位数据库
│   └── seats.json                # 席位数据文件
│
├── get_sht_report.py             # 短线报告生成（90 日窗口）
├── get_med_report.py             # 中线报告生成（180 日窗口）
├── get_lng_report.py             # 长线报告生成（730 日窗口）
├── get_ful_report.py             # 完整报告生成（综合评分）
├── get_val_report.py             # 估值报告生成（策略选股）
├── get_mak_report.py             # 市场热点报告生成（异动扫描）
│
├── scripts/                      # 辅助脚本
│   ├── update_calendar.py        # 交易日历数据更新（chinese-calendar 库同步）
│   ├── clean_cache.py            # 缓存清理快捷脚本
│   ├── perf_compare.py           # V13.2 dataclass vs dict 性能压测
│   ├── test_em_batch_quotes_limit.py  # V12.6 东财 push2 批量上限实测
│   ├── sync_readme.py            # V14.1 CHANGELOG → README 自动同步
│   ├── run_with_system_python.bat    # 系统 Python 3.12 启动包装
│   └── run_with_system_python.ps1    # PowerShell 版本
│
├── docs/                         # 技术文档
│   ├── architecture.md           # 项目架构与数据流图（Mermaid）
│   ├── roadmap.md                # V8.0-V14.0 实施路线图
│   └── field_dict.md  # 字段来源与时效性参考
│
├── pyproject.toml                # pytest / mypy / black 等工具配置中心
├── requirements.txt              # 运行时依赖列表
├── requirements-dev.txt          # 开发依赖列表
├── CHANGELOG.md                  # 版本变更记录
├── CONTRIBUTING.md               # 贡献指南
├── CODE_OF_CONDUCT.md            # 社区行为准则
├── LICENSE                       # MIT 许可证
├── README.md                     # 本文件
│
├── reports/                      # 报告输出目录（运行时自动创建，.gitignore）
├── snapshots/                    # 评分快照（历史对比/背离检测，.gitignore）
├── cache/                        # 缓存数据库（stock_cache.db，.gitignore）
└── tests/                        # pytest 测试用例（160+ 测试）
    ├── test_cache.py             # 缓存层基础
    ├── test_cache_verify.py      # cross_verify 子模块
    ├── test_calendar.py          # 交易日历（V14.0 修复 8 个）
    ├── test_core_defense.py      # 事件锁/防投毒/熔断器
    ├── test_external_apis.py     # 外部 HTTP（real_network）
    ├── test_f10_chapters_integration.py  # F10 集成（real_network）
    ├── test_field_routing.py     # V12.6 字段路由决策树
    ├── test_gd_uploader.py       # Google Drive 上传
    ├── test_report_runner.py     # V12.4-V12.5 ReportRunner
    ├── test_sc_schema.py         # V13.0 sc_schema dataclass
    ├── test_scoring.py           # 评分系统
    ├── test_stock_common.py      # V14.0 公共工具（6→28 测试）
    ├── test_strategy.py          # 策略配置
    ├── test_tdx_client.py        # TDX TCP（real_network）
    └── test_zhb_client.py        # ZHB 解析
```

---

## 配置文件

### requirements.txt

```
# ── HTTP & 网络 ─────────────────────────────────────────────
requests>=2.25,<3.0
urllib3>=1.26,<3.0

# ── 异步 HTTP（V7.5+）──────────────────────────────────────
aiohttp>=3.8,<4.0
aiosqlite>=0.20,<1.0

# ── 数据处理 ─────────────────────────────────────────────────
pandas>=1.0,<3.0
numpy>=1.20,<2.0

# ── 配置解析 ─────────────────────────────────────────────────
PyYAML>=5.4

# ── 行情数据源（V12.0：完全移除 easy_tdx，统一用 mootdx）─────────
mootdx>=0.11,<1.0
pytdx>=1.0  # zhb_client.py 依赖：通达信协议下载 zhb.zip

# ── Google Drive（google-auth + google-api-python-client）────
google-auth>=2.0
google-auth-oauthlib>=1.0
google-api-python-client>=2.0
httplib2>=0.22,<0.31   # 避开 0.32.0 代理解析 bug

# ── A股日历与交易日判断 ─────────────────────────────────────
chinese-calendar>=1.11

# ── 单元测试（可选，仅开发环境使用）─────────────────────────────
pytest>=7.0
pytest-asyncio>=0.20
```

### config.py（V12.2 集中管理）

```python
# 网络
HTTP_TIMEOUT_SECONDS = 15
HTTP_TIMEOUT_LONG = 30

# 限流
TDX_MIN_INTERVAL = 0.1        # 100ms
EM_MIN_INTERVAL = 1.0

# 重试
MAX_RETRY_COUNT = 3
RETRY_DELAY_SECONDS = 0.5

# 缓存
CACHE_DEFAULT_TTL_DAYS = 365
CACHE_SHORT_TTL_DAYS = 7
CACHE_FINANCIAL_TTL_DAYS = 365
CACHE_DB_SIZE_LIMIT_MB = 500

# 并发
MAX_CONCURRENT_HTTP_TASKS = 50
MAX_CONCURRENT_TDX_TASKS = 20

# 市场时间
MARKET_OPEN_TIME = "09:30"
MARKET_CLOSE_TIME = "15:00"
PRE_MARKET_CUTOFF = "09:15"

# 容错
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 10
CIRCUIT_BREAKER_RESET_TIMEOUT_SECONDS = 60
TOKEN_BUCKET_RPS_EASTMONEY = 1.0
TOKEN_BUCKET_RPS_TENCENT = 5.0
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

所有 6 大 Runner 调用的数据入口，封装字段路由 + ZHB 优先 + 批量调用逻辑：

```python
from data_provider import (
    get_stock_composite,         # dict 默认（V11.5+）
    get_stock_composite_dataclass,  # V13.1 opt-in dataclass
    get_pe_ttm, get_pb, get_turnover_pct,  # ZHB 字段（V12.6 移除 HTTP fallback）
    get_market_snapshot,         # 全市场 push2 批量接口
    REQUIRES_REALTIME_HTTP,      # 字段分类常量
    ZHB_SUFFICIENT,              # 字段分类常量
    is_realtime_http_field,      # 查询函数
    is_zhb_sufficient_field,     # 查询函数
)
```

### stock_common/（V12.0 包，5 个子模块）

**sc_datasource.py**：60+ 数据源查询函数（财务/资金流/解禁/行业对比/股东等）

**sc_network.py**：HTTP 请求层（限流/重试/代理/UA 池）

**sc_scoring.py**：统一评分接口（ScoreData/ScoreResult）+ 多评委输出

**sc_fault_tolerance.py**（V12.1）：容错层
- `TokenBucket` - 令牌桶限流
- `CircuitBreaker` - 熔断器
- `RandomUAPool` - 随机 User-Agent 池

**sc_schema.py**（V13.0）：字段元数据层
- 3 个 Enum：`TimeAnchor` / `DataSource` / `Unit`
- `FieldSpec` dataclass(slots=True, frozen=True)
- 34 个核心字段元数据表（FIELD_SPECS）
- `NormalizedQuote` 归一化行情快照草案

### stock_cache.py（V8.4+ 统一缓存层）

关键特性：

- **SQLite 持久化**：缓存写入 `cache/stock_cache.db`，支持程序重启
- **L1 内存缓存**（V8.4）：进程内字典存储，最大 5000 条目
- **TTL 分级策略**：财务 90 天 / 板块 7 天 / 日频 7 天 / 历史 14-90 天 / 研报 3 天
- **交易日过期**（V9.1）：F10 高频分类按交易日 15:00 自动过期
- **cross_verify**（V9.2）：多天 TTL 分类两次数据一致才标记已验证
- **dataclass 透明序列化**（V13.1）：`_serialize_for_cache` / `_deserialize_from_cache`
- **装饰器模式**：`@cached(category="xxx")` 一行启用
- **环境变量开关**：`STOCK_NOCACHE=1` 临时禁用
- **CLI 工具**：`python stock_cache.py stats` 查看命中率

```python
from stock_cache import cached, invalidate_category, print_cache_stats

@cached(category="dragon_tiger", ttl_seconds=24 * 3600)
def get_dragon_tiger_board(code, days=30, include_seats=True):
    ...

invalidate_category("dragon_tiger")  # 清除某分类
print_cache_stats()  # 查看缓存统计
```

### stock_calendar.py（V14.0 修复）

交易日历模块，支持：

- 中国 A 股交易日判断（含节假日、调休日）
- 市场状态判断（盘前/上午/午休/下午/盘后/休市）
- 本地 `holidays`/`workdays` 字典（621 条 2004-2026+）作为权威数据
- ZHB 数据仅作为辅助校验（V14.0 修复 Bug）

```python
from stock_common import is_workday, get_market_status

# 判断某日是否交易日（V14.0 修复名）
if is_workday(date(2026, 1, 1)):
    print("2026-1-1 是交易日")
else:
    print("2026-1-1 是节假日")  # V14.0 修复后正确返回

# 获取市场状态
status, message = get_market_status()
# status: closed/pre_market/morning/lunch/afternoon/post_market
# message: "已休市" / "盘前" / "上午交易中" / "午休时段" / "下午交易中" / "盘后结算"
```

### get_*_report.py（6 大 Runner）

6 大报告脚本全部继承 `BaseReportRunner`（[stock_common/sc_report_runner.py](stock_common/sc_report_runner.py)）：

- 共享 CLI 解析 / Banner / Summary / GD 上传模板 / TDX 资源清理
- 通过 `from data_provider import get_stock_composite` 统一获取数据
- 各自维护差异化的章节渲染（sht/med/lng/ful/val/mak）

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

## 版本历史

完整版本历史详见 [CHANGELOG.md](CHANGELOG.md)

---

## 常见问题

### Q: 提示 "could not convert string to float" 错误？

A: 某些股票的财务数据可能为空，v8.1.0 已修复此问题，请更新到最新版本。

### Q: 如何判断今天是否交易日？

A: 使用 `is_trading_day()` 函数，系统会自动识别中国节假日和调休日。

### Q: Google Drive 上传失败？

A: 检查 `client_secrets.json` 文件是否存在，首次使用需要浏览器授权。授权成功后自动生成 `credentials.json`。

### Q: 股票代码格式不正确？

A: 系统会自动清洗代码格式，支持多种输入方式：
- `600519`
- `600519茅台`
- `600519 茅台`

### Q: GD根目录为什么会出现个股文件夹？

A: 这是 Google Drive **桌面客户端的同步冲突**导致的，不是脚本本身的 bug。

**原因**：
- 当 `a-stock-data` 文件夹被共享后，协作者的操作会触发 Drive 的 changes feed
- 桌面客户端在解决云端与本地缓存的冲突时，可能将**长时间未被脚本操作的旧文件夹**从 `a-stock-data` 移动到根目录
- 脚本代码只会查找/创建文件夹、上传/覆盖文件，**绝不会移动或删除已有文件夹**

**解决办法**：
1. 在 Drive **网页版**中把这些文件夹手动移回 `a-stock-data`（不要用桌面客户端操作）
2. **退出 Google Drive 桌面客户端**后再运行脚本
3. 脚本运行完成后再启动桌面客户端

**预防**：定期运行脚本更新所有关注的股票，保持本地缓存与云端同步，可减少冲突概率。

### Q: 缓存怎么清理？

A: 两种方式：
- 快捷脚本：`python scripts/clean_cache.py`（清空全部）/ `python scripts/clean_cache.py --category dragon_tiger`（按分类）
- 原生 CLI：`python stock_cache.py clear-all` / `python stock_cache.py clear --category dragon_tiger`
- 临时禁用：`STOCK_NOCACHE=1 python main.py --sht 600519`

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

# 运行测试
pytest tests/

# 类型检查
python -m mypy stock_common/sc_datasource.py get_val_report.py tdx_client.py stock_common/analyze_history.py gd_uploader.py --ignore-missing-imports

# 临时禁用缓存调试
STOCK_NOCACHE=1 python main.py --sht 600519
```

### 类型注解与静态检查

项目核心模块已完成类型注解（PEP 484），在 `pyproject.toml` 中集中管理 mypy 配置：

- `[tool.mypy]`：Python 3.10 目标版本，启用 `no_implicit_optional`、`warn_redundant_casts`
- `[tool.mypy.overrides]`：stock_cache / stock_common 启用更严格规则
- `[tool.black]`：代码格式化工具配置

### 常见调试问题

- **报告数据与最新行情不一致？**：可能是缓存命中了过期数据，执行 `STOCK_NOCACHE=1 python main.py ...` 临时禁用缓存再测一次；或调用 `python stock_cache.py clear --category dragon_tiger` 清理对应分类。
- **类型检查 mypy 报错？**：`third-party library stub missing` 类警告可忽略（已在 `pyproject.toml` 配置 `ignore_missing_imports=true`）。如果是自定义函数参数/返回值类型问题，请直接提交 issue。
- **Google Drive 上传失败？**：检查根目录是否有 `client_secrets.json`（首次使用需浏览器授权），确认授权账号有 `a-stock_data` 文件夹的访问权限。
- **架构不熟悉？**：详见 [`docs/architecture.md`](docs/architecture.md)，包含 Mermaid 架构图、序列图、GD 上传流程图、缓存设计等。

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

> 详见 [AGENTS.md](AGENTS.md) 与 [tests/README.md](tests/README.md)。这里只列最常用的入口。

### 测试入口(强制 PowerShell 中转)

**不要**在 shell 里直接敲 `pytest ...` / `python -m pytest ...`。一律走：

```powershell
.\scripts\run_tests.ps1                                       # 全部离线测试
.\scripts\run_tests.ps1 -Mode module -Path tests/test_calendar.py     # 单个文件
.\scripts\run_tests.ps1 -Mode skip_real -ExtraArgs '--maxfail=1','-x' # 跳过 real_network + 失败即停
```

入口脚本在 [scripts/run_tests.ps1](scripts/run_tests.ps1),底层强制走系统 Python 3.12（见 [scripts/run_with_system_python.ps1](scripts/run_with_system_python.ps1)）。

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

新增自定义 marker 先在 `pyproject.toml` `[tool.pytest.ini_options] markers` 注册,避免 `PytestUnknownMarkWarning`。
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
