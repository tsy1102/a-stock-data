# A股个股分析报告生成系统

一套自动化生成A股个股分析报告的Python工具集，支持短线、中线、长线、完整、估值、市场热点等多种报告类型，数据来源于新浪财经、东方财富、同花顺等主流平台。

> **V9.5**：静默异常日志化 + aiohttp原生异步迁移 + ful脚本显示修复

---

## 功能特性

- **6种报告类型**：短线(sht)、中线(med)、长线(lng)、完整(ful)、估值(val)、市场热点(mak)
- **多数据源整合**：新浪财经、东方财富、同花顺、通达信等
- **F10 全覆盖**（V9.1）：12 个 F10 函数 + 11 个 HTTP 函数 F10 优先逻辑 + 6 种新章节 + 数据质量核查附录
- **缓存交叉验证**（V9.2）：11 个多天 TTL 分类启用两次获取对比，一致才标记为已验证，防止错误数据被缓存
- **交易日历判断**：自动识别中国A股交易日、节假日、调休日、午休时段；支持脚本更新数据（`python -m stock_common.stock_calendar --update`）
- **云端同步**：支持Google Drive自动上传报告，快照文件自动云端备份
- **智能快照管理**：自动生成评分快照，支持跨日期趋势分析和背离检测
- **统一GD上传策略**：支持按股票代码和按类型的双模式上传，智能文件命名
- **批量处理**：支持多股票、多报告类型并行生成
- **代码清洗**：自动处理股票代码格式问题
- **统一缓存层**：SQLite + TTL 自动过期，支持交易日过期策略 + 交叉验证 + 异步连接复用
- **异步并发**：30+ 异步函数支持高效并发请求
- **类型安全**：mypy 静态检查通过，类型注解完整覆盖
- **限流安全加固**：线程锁保护、429智能重试、TDX请求节流、限流统计监控
- **盘前行情智能切换**（V9.3）：9:30前自动使用上一交易日日K线数据，避免实时接口返回 0 导致涨跌幅 -100%；行情缓存 Key 增加交易日期，盘前/盘中数据独立保留
- **报告盘前提示**（V9.3）：sht/med/lng 等报告在盘前模式时显示"⚠️ 盘前模式（9:30前），以下行情数据基于上一交易日收盘数据"
- **版本号统一清理**（V9.3）：删除所有报告脚本和终端输出中的硬编码版本号（如 V8.9），避免版本推进时遗漏修改
- **异常处理规范**（V9.2）：无裸 `except:`，所有静默异常均加日志，Ctrl+C 可正常终止
- **资金流多态修复**（V9.3.1）：sht 脚本两处资金流代码增加 `isinstance` 类型检查，TDX 失败走东财 fallback 返回 `List[float]` 时不再崩溃
- **子进程超时保护**（V9.3.1）：`--all` 批量运行时子进程设置 10 分钟超时，防止因网络/接口问题导致永久挂起
- **TDX 限流优化**（V9.3.1）：TDX 请求间隔从 20ms 增大到 100ms，批量运行更稳定，减少接口间歇性失败
- **TDX 健康检查增强**（V9.3.1）：TdxClient 和 MacClient 连接成功后自动检测关键接口可用性，便于快速定位问题
- **测试脚本增强**（V9.3.1）：数据源诊断测试新增 MacClient 三项测试（连接/所属板块/板块成员），覆盖上交所和深交所股票
- **TDX K线假数据防护**（V9.3.2）：健康检查增加 K线接口校验，检测到返回假数据（ret_count=800但body为空）的服务器时自动标记为坏主机并换IP重连，解决指数涨幅全N/A和异动检测全为0的问题
- **SQLite WAL死锁修复**（V9.3.2）：缓存数据库 journal_mode 从 WAL 改为 DELETE，避免多进程并发写时产生 `-wal`/`-shm` 文件锁导致 `--all` 命令卡死
- **代理环境兼容**（V9.3.2）：HTTP 请求显式禁用系统代理（`proxies=None`），增加 ProxyError 和兜底异常捕获，解决代理环境下东财接口永久阻塞

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
| `--sht` | 短线报告 | 90日内解禁、近期资金流向、短线技术指标 |
| `--med` | 中线报告 | 180日内解禁、财务分析、行业对比、机构持仓 |
| `--lng` | 长线报告 | 730日内解禁、深度财务分析、股东变化、估值分析 |
| `--ful` | 完整报告 | 综合报告，六维评分，包含所有分析维度 |
| `--val` | 估值报告 | PE/PB估值、行业估值对比、估值历史分位 |
| `--mak` | 市场热点 | 行业热点、概念题材、资金流向 |

---

## 命令行参数

```
python main.py [选项] 股票代码...

选项:
  --sht    生成短线报告
  --med    生成中线报告
  --lng    生成长线报告
  --ful    生成完整报告
  --val    生成估值报告
  --mak    生成市场热点报告
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
├── main.py                   # 主入口程序（参数分发/多报告并行）
├── VERSION                   # 项目版本号（单一来源，脚本通过 get_version() 读取）
├── stock_common/             # 核心模块包
│   ├── __init__.py           # 包入口，统一导出接口
│   ├── sc_datasource.py      # 数据源查询模块（68+ 函数）
│   ├── sc_network.py         # 网络请求层（限流/重试/代理）
│   ├── sc_utils.py           # 工具函数（get_version/_safe_float/_load_settings 等）
│   ├── sc_scoring.py         # 统一评分接口（ScoreData/ScoreResult）
│   ├── stock_calendar.py     # 交易日历模块（含节假日/调休日数据）
│   ├── strategy_config.yaml  # 统一策略参数配置文件
│   ├── analyze_history.py    # 评分快照分析与趋势背离检测
│   ├── f10_parser.py         # F10 数据解析模块
│   ├── seat_db.py            # 龙虎榜席位数据库
│   ├── seats.json            # 席位数据文件
│   └── keywords_config.yaml  # 公告关键词配置
├── tdx_client.py             # 通达信数据客户端（easy-tdx 行情接口封装）
├── stock_cache.py            # 统一缓存层（SQLite + TTL 装饰器）
├── gd_uploader.py            # Google Drive上传模块
├── get_sht_report.py         # 短线报告生成（90日窗口）
├── get_med_report.py         # 中线报告生成（180日窗口）
├── get_lng_report.py         # 长线报告生成（730日窗口）
├── get_ful_report.py         # 完整报告生成（综合评分）
├── get_val_report.py         # 估值报告生成（策略选股）
├── get_mak_report.py         # 市场热点报告生成（异动扫描）
├── pyproject.toml            # pytest / mypy / black 等工具配置中心
├── requirements.txt          # 运行时依赖列表
├── CHANGELOG.md              # 版本变更记录
├── reports/                  # 报告输出目录（运行时自动创建）
├── snapshots/                # 评分快照（历史对比/背离检测）
└── tests/                    # 诊断脚本和 pytest 测试用例
```

---

## 配置文件

### requirements.txt

```
# ── HTTP & 网络 ─────────────────────────────────────────────
requests>=2.25,<3.0
urllib3>=1.26,<3.0

# ── 异步 HTTP（V7.5 新增）────────────────────────────────────
aiohttp>=3.8,<4.0
aiosqlite>=0.20,<1.0

# ── 数据处理 ─────────────────────────────────────────────────
pandas>=1.0,<3.0
numpy>=1.20,<2.0

# ── 配置解析 ─────────────────────────────────────────────────
PyYAML>=5.4

# ── 行情数据源（核心依赖，必须安装）─────────────────────────────
easy-tdx>=1.0,<2.0

# ── Google Drive（V7 已切换至 google-auth + google-api-python-client）
google-auth>=2.0
google-auth-oauthlib>=1.0
google-api-python-client>=2.0
httplib2==0.22.0       # ← 固定版本，0.32.0 有代理解析 bug

# ── A股日历与交易日判断（V8 新增）────────────────────────────────
chinese-calendar>=1.11

# ── 单元测试（可选，仅开发环境使用）─────────────────────────────
pytest>=7.0
```

### Google Drive 配置（可选）

如需启用云端上传功能：

1. 在 Google Cloud Console 创建项目并启用 Drive API
2. 下载 OAuth 2.0 凭证文件，保存为 `credentials.json`
3. 首次运行时会弹出浏览器进行授权

---

## 核心模块说明

### stock_common.py

核心数据获取函数库，提供以下功能：

```python
# 股票基本信息
get_stock_info(code)                    # 获取股票名称、行业等基本信息

# 财务数据
get_sina_financial_report(code)         # 新浪财报数据
get_sina_balance_sheet(code)            # 新浪资产负债表
get_gross_margin_and_roe(code)          # 毛利率和ROE数据

# 资金流向
get_hsgt_macro_flow()                   # 沪深港通资金流向
get_northbound_hold_async(code)         # 北向资金持股
get_margin_trading_async(code)          # 融资融券数据
get_block_trade_async(code)             # 大宗交易数据

# 解禁数据
get_lockup_expiry(code, days, include_history)  # 解禁到期数据

# 交易日历
is_trading_day(date)                    # 判断是否交易日
get_market_status()                     # 获取当前市场状态

# 工具函数
clean_codes(codes)                      # 清洗股票代码
```

### stock_cache.py

统一缓存层，用于降低 API 请求频率、避免重复网络请求。关键特性：

- **SQLite 持久化**：缓存写入项目根目录 `cache/stock_cache.db`，支持程序重启后读取
- **TTL 分级策略**：按数据类型配置不同过期时间（财务数据 90 天，龙虎榜/北向数据当日有效，概念板块 7 天，研报 3 天，通用兜底 1 小时）
- **装饰器模式**：通过 `@cached(category="xxx")` 一行启用函数级缓存，不需改写业务逻辑
- **手动失效**：提供 `invalidate_category("dragon_tiger")`、`clear_all()` 等手动清理接口
- **环境变量开关**：`STOCK_NOCACHE=1 python main.py ...` 临时禁用缓存（调试用）
- **CLI 工具**：`python stock_cache.py stats` 查看缓存命中率、条目数量、占用空间

```python
from stock_cache import cached, invalidate_category, print_cache_stats

# 例：给一个网络请求函数加缓存
@cached(category="dragon_tiger", ttl_seconds=24 * 3600)
def get_dragon_tiger_board(code, today_str, days=30, include_seats=True):
    ...

# 例：清除某分类缓存（重新拉取当日数据前）
invalidate_category("dragon_tiger")

# 例：查看缓存统计
print_cache_stats()
```

### stock_calendar.py

交易日历模块，支持：

- 中国A股交易日判断（含节假日、调休日）
- 市场状态判断（盘前/上午/午休/下午/盘后/休市）
- 自动升级节假日数据（依赖 chinese-calendar 库）

```python
from stock_common import is_trading_day, get_market_status

# 判断今天是否交易日
if is_trading_day():
    print("今天是交易日")

# 获取市场状态
status, message = get_market_status()
# status: closed/pre_market/morning/lunch/afternoon/post_market
# message: "已休市" / "盘前" / "上午交易中" / "午休时段" / "下午交易中" / "盘后结算"
```

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

### v9.5 (2026-07-11)

- 🔧 **静默异常日志化**（28处）：`tdx_client.py`（23处）、`gd_uploader.py`（4处）、`get_med_report.py`（1处）中 `except Exception:` 静默吞异常全部添加 `_debug_log` 日志，提升调试可观测性
- ⚡ **aiohttp原生异步迁移**：`sc_datasource.py` 中10个HTTP异步函数从 `asyncio.to_thread` "假异步"包装改为原生 `aiohttp` 实现（`_async_request_with_retry` / `_async_quick_request`），剩余10个TDX依赖函数保留
- 🐛 **修复 _load_config 未定义错误**：`sc_datasource.py` 异步迁移过程中误写的不存在函数名，导致 sht/med/lng 脚本运行崩溃
- 🐛 **ful脚本显示修复**：价格走势改为近15日倒序显示（Day-1为最近日期）；新闻舆情文案从"近24小时"改为"近期"

### v9.4 (2026-07-11)

- 📦 **VERSION文件单一来源版本号管理**：项目根目录新增 `VERSION` 文件，所有脚本通过 `get_version()` 函数读取版本号，告别"升级版本需遍历所有文件"的旧模式
- 🧹 **大规模死代码清理**（~70KB）：删除 `trap_detector.py`（杀猪盘检测，22KB/12函数）、`valuation_methods.py`（机构估值，21KB/9函数）、`gd_upload_flow` 函数、`sc_utils.py` 中被覆盖的 `print_batch_summary`、10个临时诊断脚本
- ⚡ **mak报告并行化**：全市场异动扫描引入 `ThreadPoolExecutor(max_workers=3)`，扫描速度提升2-3x
- 🔧 **线程安全修复**：删除 `sc_network.py` 中无锁保护的 `_em_last_request_time` / `_gen_last_request_time` 变量，统一使用 `_DOMAIN_LAST_TIME_LOCK` 保护
- 🔧 **sht资金流重复调用修复**：`get_fund_flow_realtime` 增加 `ff_120d` 参数，外层调用复用已获取的历史数据
- 🐛 **报告格式统一**：
  - med脚本两融数据添加"融券余额"列（与sht一致）
  - med/lng流通股东显示统一为0%（删除N/A判断）
  - lng脚本休市提示移至标题下方（与sht/med一致）
  - ful脚本新闻 page_size 从10增至30（覆盖近30天）
  - sht/med/lng/ful四个脚本休市提示文案统一简化

### v9.3.3 (2026-07-10)

- 🐛 **修复 GD上传路径混乱**：所有 txt 文件统一上传到 `a-stock-data/[股票代码-名称]/` 子文件夹，禁止根目录上传
- 🐛 **修复 ScoreData 构造路径错误**：`get_ful_report.py` 中 `price` 和 `name` 参数修正
- 🐛 **修复地天板预警键名错误**：`get_sht_report.py` 中 `limit_down` 改为 `limit_down_price`
- 🐛 **修复 MACD DEA 计算错误**：`get_med_report.py` 中修正为正确的 EMA(DIF, 9)
- 🐛 **修复 iloc[3] IndexError**：`get_med_report.py` 和 `get_lng_report.py` 中 `>= 3` 改为 `>= 4`
- 🐛 **修复 cleanup_tdx()/exit(1) 缩进错误**：`get_val_report.py` 和 `get_mak_report.py` 异常处理修正
- 🐛 **修复 sht资金流获取崩溃**：东财 fallback 调用无 try-except 导致【七、资金走向分析】显示失败
- 🐛 **修复 ful技术分析内容缺失**：K线数据不足时 `closes_list` 为空，增加实时行情价格 fallback
- 🐛 **修复 GD根目录出现旧股票文件夹**：`get_or_create_drive_folder()` 增加 `parent_id` 存在性验证，防止无效 ID 回退到根目录
- 🐛 **修复 FREE_DATE None 切片崩溃**：`sc_datasource.py:1805` 中 `r.get("FREE_DATE", "")` 当值存在但为 None 时返回 None，改为 `r.get("FREE_DATE", "") or ""`（如 600563 法拉电子）
- 🐛 **修复 val 脚本 coroutine 未 await 警告**：`get_val_report.py` 中 `_tasks` 被赋值两次，第一次创建的 17 个 coroutine 从未 await 导致阻塞。将策略 18 移入 `_strategy_defs` 列表
- 🐛 **修复 mak 报告标题双括号**：`get_mak_report.py:429` 标题 `（{_mkt_note}）` 与 note 本身已含的 `（）` 叠加，去掉外层括号
- 🐛 **修复 mak 连板表格漏显连板股**：连板表格遍历 `ths[:50]` 导致排名50之后的连板股（如亚联机械 001395）不在表格中。改为遍历 `_lb_list` + 查表
- 🐛 **修复 mak 涨停列表少1只**：先取 `ths[:50]` 再排除连板导致 `50-1=49` 只。改为遍历 `_zt_list[:50]`（先排除连板再取 top N）
- 🔧 **sync/async 重复代码重构**：`sc_datasource.py` 中 9 个 async 函数改为 `asyncio.to_thread()` 代理，消除重复逻辑
- 🔧 **stock_cache.py schema 单点维护**：提取公共 SQL 常量，删除迁移逻辑
- 🧹 **大量死代码清理**：删除各脚本中未用导入、死函数、死配置等冗余代码
- 📄 **README/CHANGELOG 更新**：项目结构图更新，内嵌 requirements.txt 同步，AI产业链标注为"规划中"

### v9.3.2 (2026-07-09)

- 🐛 **修复 TDX K线假数据导致指数涨幅全N/A和异动检测全为0**：约50%的 easy_tdx 内置TDX服务器K线接口返回假数据（响应头 `ret_count=800` 但 body 为 0 字节），导致 `TdxDecodeError`。`from_best_host()` 只测延迟不测数据正确性，会选中这些坏服务器。
  - `_tdx_health_check` 新增 `get_security_bars` K线接口校验，检测到假数据时标记主机为坏主机并抛出异常触发重连
  - `_get_tdx_client` 调用 `from_best_host` 时过滤掉 `_TDX_BAD_HOSTS` 黑名单中的IP，所有IP都被标记时重置黑名单重试
  - `tdx_get_security_bars`、`tdx_get_index_bars`、`tdx_get_weekly_bars` 捕获 `TdxDecodeError` 时自动标记坏主机并换IP重连
- 🐛 **修复 SQLite WAL模式多进程并发死锁**：`--all` 命令启动4个独立Python进程并发写SQLite，WAL模式下产生 `-wal`/`-shm` 文件锁导致死锁。`stock_cache.py` 的 `journal_mode` 从 `WAL` 改为 `DELETE`，`cache_size` 从 `-64000`(64MB) 降到 `-8000`(8MB)
- 🐛 **修复代理环境下东财接口永久阻塞**：系统代理自动拦截 `requests` 请求，`np-weblist.eastmoney.com` 等接口超时失效。`_do_request` 增加 `proxies={"http": None, "https": None}` 禁用系统代理，增加 `ProxyError` 和兜底 `Exception` 捕获
- ⚡ **TDX IP列表精简**：删除38个失效IP，保留13个可用IP，减少 `from_best_host()` 扫描时间
- 🔒 **新增 TDX坏主机黑名单机制**（`tdx_client.py`）：新增 `_TDX_BAD_HOSTS` 全局集合，记录返回假K线数据的服务器IP，`from_best_host` 自动跳过黑名单中的IP
- 🧪 **新增诊断脚本**（`tests/`）：
  - `diag_tdx_hosts_test.py`：逐个测试52个TDX服务器的K线可用性，区分正常/假数据/连不上三种状态
  - `diag_tdx_final.py`：捕获TDX K线请求的原始TCP响应（header + body），深度诊断TdxDecodeError根因

### v9.3.1 (2026-07-08)

- 🐛 **修复 sht 脚本 `'float' object is not subscriptable` 崩溃**：`ff["data"]` 多态（TDX=List[dict]、东财fallback=List[float]），第1181行信号生成和第1381-1382行评分数据处缺少类型检查，TDX 资金流历史为空时崩溃
- 🐛 **修复 `--all` 批量运行子进程永久挂起**：`main.py` 的 `proc.wait()` 无超时，接口异常永不返回时整个链路阻塞；改为 10 分钟超时后自动 kill
- ⚡ **TDX 请求间隔从 20ms 增大到 100ms**：降低批量运行时 TDX 服务器压力，减少接口间歇性失败和数据缺失
- 🔍 **TDX 健康检查增强**：TdxClient 新增财务/资金流/分红除权三项检测，MacClient 新增所属板块/板块列表两项检测，便于快速定位问题
- 🧪 **测试脚本增强**：数据源诊断测试新增 MacClient 三项测试，覆盖上交所和深交所股票

### v9.3.0 (2026-07-07)

- 📈 **盘前行情智能切换**（`tdx_client.py`）：9:30前自动使用上一交易日日K线数据，避免实时接口返回 0 导致涨跌幅计算为 -100%
- 🔑 **缓存 Key 交易日期隔离**：行情缓存 Key 格式改为 `Q:{code}:{trading_date}`，盘前/盘中数据独立保留，避免相互覆盖
- ⚠️ **报告盘前提示**：sht/med/lng 等报告在盘前模式时显示“⚠️ 盘前模式（9:30前），以下行情数据基于上一交易日收盘数据”
- 🧹 **版本号统一清理**：删除所有报告脚本和终端输出中的硬编码版本号（如 V8.9），避免版本推进时频繁修改
- 🐛 **修复 sht 脚本 688305 list index out of range**：增加多处列表索引边界检查
- 🐛 **修复 med 脚本历史财务业绩显示旧数据**：限制财务数据显示为近 5 季度
- 🐛 **修复 ful 脚本成功/失败统计显示 0**：统计逻辑改为基于数据生成结果
- 🐛 **修复 get_val_report.py FutureWarning 无限循环**：修正 `_safe_float` 对 pandas Series 的处理方式
- 🐛 **修复 --no-upload 对快照异常上传不生效**：传递 `skip_upload` 参数
- 🐛 **修复融资融券数据显示异常**（`sc_datasource.py`）：日期截断到 10 位并过滤金额全为 0 的无效行

### v9.2.0 (2026-07-05)

- 🔒 **缓存交叉验证机制**：11 个多天 TTL 分类（financial/balance_sheet/gross_margin_roe/basic_info/concept_blocks/lockup_expiry/eps_forecast/dividend/f10_financial/f10_shareholder/f10_share_capital）启用 `cross_verify=True`，两次获取数据一致才标记为已验证，防止错误数据被缓存
- 🔒 **缓存并发安全加固**：`set_cache` 交叉验证分支的 SELECT-then-UPDATE 用 `_db_lock` 包裹，防止竞态丢失更新
- ⚡ **异步连接复用**：新增 `_get_async_db()` 模块级单例，复用同一 aiosqlite 连接提升异步缓存性能
- 📅 **日历更新脚本**：`scripts/update_calendar.py` 从 chinese-calendar 库提取数据自动更新 `stock_calendar.py`；支持 `python -m stock_common.stock_calendar --update` CLI 入口
- 🐛 **异常处理规范化**：13 处裸 `except:` 全部改为 `except Exception:`（Ctrl+C 可正常终止）；约 70 处 `except Exception: pass` 静默吞异常全部加 `_debug_log` 日志
- 🐛 **TDX 重连泄漏修复**：`_get_tdx_client` / `_get_mac_client` 异常重连前先 `close()` 旧连接，防止 socket fd 泄漏
- 🐛 **main.py 模块级副作用修复**：`check_dependencies()` 从模块级移到 `if __name__ == "__main__":` 内
- 🧹 **限流体系完善**：删除 `_em_request_lock`/`_gen_request_lock`/`_DOMAIN_SEMAPHORES` 死代码；异步请求补齐进程间协调 `_gen_wait_process_interval_async()`；`em_get()` 与 per-domain 限流器双向状态同步；删除 `get_industry_peers` / `get_mak_report` 中冗余硬编码 sleep
- 🧹 **席位数据去年份化**：`seats-2026.json` → `seats.json`，跨年后无需手动修改
- 🧹 **tests 9 个文件硬编码路径修复**：统一改为相对路径，换机器/CI 可正常运行

### v9.1.1 (2026-07-04)

- 🐛 **修复 ful 评分 theme→holder 映射 bug**：评分维度键名与数据来源不一致，统一为 `holder`（筹码面），权重默认值修正为 10%
- 🐛 **补全 F10 交易日缓存策略**：`tdx_get_fund_flow` 和 `tdx_get_latest_announcements` 添加 `trading_day=True`，5 个高频分类全部按交易日过期
- ✨ **ful 报告从五维升级为六维**：补全分红面显示，总分与显示维度一致（技术25%+估值20%+基本20%+资金15%+筹码10%+分红10%）
- 🧹 **F10 死代码精简**：移除 6 个未使用的 F10 函数 + `render_f10_chapter` 渲染函数 + 2 个测试文件，精简约 700 行

### v9.1.0 (2026-07-04)

- 🔧 **F10 全覆盖工程**：用通达信 F10 协议替代/补充现有 HTTP 接口，降低东财限流风险，详见 `docs/TDX_F10_ROADMAP.md`
- ➕ **12 个 F10 核心函数**（`tdx_client.py`）：异动/财务/股东/股本/新闻/研报/行业/经营/治理/资本运作/主题/概况
- ➕ **6 种 F10 新章节**：异动风险/研发创新/财务深度/股东行为/治理结构/主营构成，按报告类型差异化集成
- ➕ **数据质量核查附录**：6 项一致性验证（财务/股东/研报/资金流/股本/分红），差异 > 20% 标记警告
- 🔁 **11 个 HTTP 函数 F10 优先逻辑**：F10 优先 + HTTP 兜底，7 个异步函数委托到同步版
- 📅 **缓存层交易日过期策略**：`@cached(trading_day=True)` 按最近交易日过期，休市期间自动复用缓存
- 🐛 **修复 sht 资金流渲染 TypeError**：东财回退返回 `List[float]`，原渲染代码期望 dict 导致崩溃
- 📦 **版本号统一升级 V9.1**

### v9.0.0 (2026-07-02)

- 🌐 **舆情互动层（Layer 10）**：新增互动易问答、同花顺热榜、东财人气榜、个股概念命中，新闻板块不再为空
- 🗓️ **上市日期永不空白**：TDX 失败时自动从东财 push2 获取，缓存读取时校验防坏数据
- ⚡ **脚本速度恢复到 2 只/分钟**：修复 `_check_mac()` 缓存，消除 TDX 连接重试退避（1.5s→0.000s）
- 🛡️ **接口异常不崩溃**：`q['xxx']` 改为 `q.get('xxx')`，腾讯偶发超时不再导致 KeyError
- 🗑️ **清理冗余逻辑**：删除已下线财联社快讯、删除 sht 重复股价显示、sht 手动投机派评分删除
- 📦 **版本统一升级 V9.0**

### v8.9.0 (2026-06-29)

- 🔧 **快照架构改进**：移除逐只股票写入，改用模块级累积器，脚本末尾一次性 `save_snapshot()`
- 🐛 **修复 int+dict 类型错误**：`get_sht_report.py` 中 `sum(recent_data)` 现改为 `sum(d.get("main_net",0) for d in recent_data)`
- 🐛 **修复 val 脚本导入缺失**：添加 `_load_settings`、`holder_change` 修复模块化后 NameError
- 🐛 **修复线程硬编码**：`get_ful_report.py` 显示正确的 `_MAX_WORKERS=3`
- 🗑️ **关闭旧 JSON 迁移**：`_MIGRATE_HOLDER_CACHE = False`，不再依赖 `holder_cache.json`
- 📄 **版本统一升级**：所有脚本版本号统一为 V8.9

### v8.8.0 (2026-06-25)

- 🚀 **GD上传逻辑统一化**：统一 `ful/sht/med/lng` 四个脚本的GD上传格式为「股票代码-2个中文」（如 `002193-如意`），跳过ST前缀，无中文时显示「股票代码-」便于识别问题
- 📄 **快照文件格式升级**：从 `snapshot_YYYYMMDD_type.json` 改为 `snapshot_YYYYMMDD_HHmm.txt` 文本格式，提升可读性并支持自动GD上传
- ☁️ **快照自动云端同步**：快照文件生成后自动上传到 `a-stock-data/snapshot/` 文件夹，确保数据安全和历史记录完整
- 🔧 **系统功能增强**：优化快照加载逻辑以支持TXT格式，完善GD上传错误处理和重试机制

### v8.7.0 (2026-06-25)

- 🗑️ **删除社交热榜聚合**：移除 `social_sentiment.py`（6 平台桩实现返回空数据）及 `stock_common.py` 中的便捷封装
- 🧹 **死代码清理**：同步 `generate_report()` 替换为薄包装（`asyncio.run()` 调用异步版），删除 `get_lng_report.py`（~545行）、`get_med_report.py`（~828行）、`get_sht_report.py`（~1175行）中的死代码辅助函数
- ✅ **新增历史分析模块**：`analyze_history.py` 实现 `save_snapshot()` 智能合并快照和 `analyze_history()` 跨日期趋势背离检测（单日突变 |Δ|≥15分 / 连续≥3天同向且总变化≥15分）
- 🐛 **修复趋势检测逻辑**：修正连续趋势判定条件（`run_len + 1 >= TREND_MIN_DAYS`），删除 `TREND_STEP_THRESHOLD` 避免小步累加噪音

### v8.5.0 (2026-06-22)

- ✅ **新增龙虎榜席位增强**：22位游资席位数据库（legend/new_gen/regional/new_2025分级），席位风格标签、溢价判断、席位质量评分
- ✅ **新增杀猪盘8信号检测**：`trap_detector.py`实现8维检测框架（低质量账号/话术模板/付费引流/基本面脱节/K线异常/老师营销/跨平台联动/虚假研报） *(V9.4已删除：API未接入上层报告)*
- ✅ **新增数据质量HARD-GATE**：13条数据质量检查清单，critical级别错误自动阻断报告生成
- ✅ **新增多档分析深度**：支持`--depth lite/medium/deep`三档（快速30秒/标准5分钟/深度15分钟）
- ✅ **新增多评委评审团**：价值派/成长派/游资派/综合派四套评分体系，支持分歧度检测
- ✅ **新增社交热榜聚合**：`social_sentiment.py`支持微博/知乎/抖音/头条/百度/B站6平台情绪聚合（需API认证）
- ✅ **新增机构估值方法库**：`valuation_methods.py`实现DCF/DDM/PEG/LBO/PB-ROE/行业PE比较等多种估值方法 *(V9.4已删除：API未接入上层报告)*
- ⏳ **AI产业链卡位分析（规划中）**：`ai_chain_analyzer.py` 模块尚未实现，功能暂不可用 *(V9.4已删除代理函数)*

### v8.4.0 (2026-06-22)

- ✅ **新增统一缓存层**：`stock_cache.py`（SQLite + TTL 装饰器），覆盖龙虎榜/北向/财务/概念板块等 25+ 个网络请求函数
- ✅ **新增异步函数族**：`get_northbound_hold_async`、`get_margin_trading_async`、`get_block_trade_async`、`get_dividend_history_async`、`get_concept_blocks_async`、`get_industry_peers_async` 等 22+ 个异步接口
- ✅ **类型注解补齐**：~25 个函数补上 PEP 484 类型注解（参数 + 返回值），mypy 静态检查通过
- ✅ **参数外置**：硬编码阈值（换手率/PE/PB/封单强度等）统一从 `strategy_config.yaml` 读取，便于策略调参
- ✅ **新增测试文件**：`tests/test_calendar.py`（交易日历）、`tests/test_cache.py`（缓存层）、`tests/test_strategy.py`（选股策略）
- ✅ **工具配置中心化**：`pyproject.toml` 集中管理 pytest/mypy/black
- ⚡ **性能提升**：缓存命中率可降至 50-80% 网络请求（视使用频率）；异步化让批量报告生成提速 3-5x

### v8.3.0 (2026-06-18)

- ✅ **bug 修复**: 北向资金持股占比显示超100%（`_ratio*100`改为`_ratio`）
- ✅ **bug 修复**: 股东户数变化率异常（变化率超过±500%时显示为±999.99%并标记⚠️）
- ✅ **bug 修复**: EPS预测合理性检查（eps_val<=0时不计算前向PE）
- ✅ **bug 修复**: 涨停封单弱时仓位建议降级（检测到封单预警信号时仓位减半）
- ✅ **优化**: 主力净流入单位统一使用"亿元"
- ✅ **优化**: 亏损股评分强制下限（ROE<0时评分下限为20分）
- ✅ **优化**: 板块排名标题明确区分市值排名
- ✅ **优化**: 章节分隔符风格统一为`─`
- ✅ **优化**: 数字正负号格式统一
- ✅ **优化**: 评分图形条按加权分数显示
- ✅ **优化**: W底形态成交量确认统一为5日均量对比

### v8.2.0 (2026-06-18)

- ✅ **bug 修复**: 股票代码 300274 等因 lines 列表中存在 None 值导致 `join()` 报错
- ✅ **bug 修复**: `ful` 脚本综合评分显示 4211.0（百分比权重未除以100）
- ✅ **统一显示**: 删除 `ful` 脚本的额外打印逻辑，与其他脚本保持一致
- ⚡ **优化**: `get_dragon_tiger_board()` 增加 `include_seats` 参数，减少不必要的 API 请求

### v8.1.0 (2026-06-18)

- **新增统一评分接口**: `ScoreData` / `ScoreResult` / `calculate_score()`，统一管理 4 种报告类型的评分逻辑
- **新增快照功能**: `save_score_snapshot()` 保存评分结果，支持 `analyze_history.py` 进行历史对比与背离检测
- **新增配置文件**: `strategy_config.yaml` 统一配置评分权重和参数
- **新增交易日历**: `is_trading_day()` / `get_market_status()` 判断 A 股交易日和市场状态
- **新增代码清洗**: `clean_codes()` 处理股票代码格式
- **目录重命名**: `WARNING_DIR` → `SNAPSHOT_DIR`
- **bug 修复**: 银行股财报字段映射 / 财务分析除零保护 / 空字符串转换异常 / 龙虎榜日期字段过滤格式

---

## 常见问题

### Q: 提示 "could not convert string to float" 错误？

A: 某些股票的财务数据可能为空，v8.1.0 已修复此问题，请更新到最新版本。

### Q: 如何判断今天是否交易日？

A: 使用 `is_trading_day()` 函数，系统会自动识别中国节假日和调休日。

### Q: Google Drive 上传失败？

A: 检查 `credentials.json` 文件是否存在，首次使用需要浏览器授权。

### Q: 股票代码格式不正确？

A: 系统会自动清洗代码格式，支持多种输入方式：
- `600519`
- `600519茅台`
- `600519 茅台`

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
pip install mypy black

# 运行测试
pytest tests/

# 类型检查
python -m mypy stock_common/sc_datasource.py get_val_report.py tdx_client.py analyze_history.py gd_uploader.py --ignore-missing-imports

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
- **Google Drive 上传失败？**：检查根目录是否有 `credentials.json`（首次使用需浏览器授权），查看 `gd_uploader.py` 的 `upload_folder_name` 是否与目标文件夹名一致。

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

## 许可证

MIT License

---

## 免责声明

本项目仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。使用本工具产生的任何投资损失，作者不承担责任。

---

## 联系方式

如有问题或建议，欢迎提交 [Issue](https://github.com/tsy1102/a-stock-data/issues)。
