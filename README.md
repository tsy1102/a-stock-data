# A股个股分析报告生成系统

一套自动化生成A股个股分析报告的Python工具集，支持短线、中线、长线、完整、估值、市场热点等多种报告类型，数据来源于新浪财经、东方财富、同花顺等主流平台。

> **V11.5**：Data Provider统一数据层正式启用 - 历时多版本规划，data_provider.py统一数据中心层全面激活，六大报告脚本全部完成迁移；核心架构为字段时效性三级分级模型（实时层/准实时层/静态层），自动按字段业务属性选择最优数据源；全函数支持缓存、交易状态感知、async异步版本；val脚本6个策略改为async+智能调度器，ful脚本9层架构async并发重构，sht/med/lng/mak四脚本统一数据入口

> **V11.4**：死代码清理与财联社/舆情互动层集成 - 删除6个报告脚本共47处data_provider.py死导入；修复TTL重复键（hsgt_flow→hsgt_macro_flow）；修复med报告3处静默异常；按硬约束在sht/med/lng/ful四报告中集成财联社快讯（sht=420min/med=3d/lng=2d/ful=3d）和互动易问答（sht=24h/med=7h/lng=30d/ful=15d）并实现时间阈值过滤；tests目录全面重写（删除21个废弃文件，更新3个测试文件，重写README.md）

> **V11.3**：缓存层T-1数据混入修复 - 通过7/15 vs 7/16报告对比发现4个缓存分类跨日携带T-1数据（industry_compare/industry_peers/ths_hot_reason/hsgt_flow），全部改为交易日模式（trading_day=True，交易日15:00自动过期）；北向资金批量缓存重构（移除预取共享，改为每只股票独立调用+缓存层保证仅1次API请求）；ZHB数据经用户手动交叉验证100%可信（贵州茅台7/14+7/15涨跌幅/成交额精确吻合）

> **V11.2**：ZHB混合分层架构 + 字段真实性验证 - val脚本全市场数据加载升级为混合分层模式（API实时层覆盖price/change_pct/amount/pe_ttm/turnover_pct，ZHB静态层保留52w/pb/dividend/ipo_price等慢变字段）；clean_codes增加命令行flag粘连检测警告；新增verify_zhb_fields.py字段验证脚本（跨日Delta验证14项全部PASS + 外部数据校验）

> **V11.1**：ZHB数据时效性修复 - val脚本全市场成交额实时覆盖（腾讯行情覆盖ZHB T-1数据），流动性池基于实时成交额排序；策略19标注T-1数据来源；策略20增加TDX实时资金流fallback，数据来源在reason中明确标注

> **V11.0**：架构重构完成 - val 脚本选股池扩大（策略19/20全市场扫描，每策略显示10只股票）；修复 sht 报告主力资金占比 bug、val 脚本 banner 错误、lng/ful 变量作用域等 9 个问题

> **V10.3**：阶段二+阶段三完整实施 - 六大报告脚本新增ZHB分析维度（主力资金流向、52周位置百分位、IPO破发度、EPS/员工数、全市场资金监控）；创建统一数据中心层（Data Provider），根据字段时效性自动路由数据源；缓存模块引入L1/L2双级架构，同脚本运行期内零I/O；新增zhb_sync.py自动化入库管道，支持定时检测/智能下载/数据校验/自动入库/清理策略

> **V10.2**：缓存命中率重大修复 - 修复cross_verify读写互斥BUG（14个分类缓存永久失效）、修复_has_zero_price递归误杀（龙虎榜/行业对比等有效缓存被跳过）、修复today_str污染缓存key（lockup_expiry/dragon_tiger TTL失效）；修复val脚本导入错误（get_data_date未定义）；修复"休市日"标签错误

> **V10.1**：zhb字段映射重大修正（基于injoyai/tdx开源仓库源码验证）- tdxstat/tdxstat2字段全部确认，新增连涨天数/股息率/52周高低价/IPO发行价等关键字段；全局股本缓存层（share_capital.json，90天TTL），市值内存计算（收盘价×总股本），零网络请求；val脚本全策略切换zhb数据（7.7秒→<0.1秒），策略扫描范围扩大至500-1000只；mak脚本优先使用zhb全市场快照，失败自动回退TDX；缓存策略优化 - basic_info TTL从30天降至1天（修复市值过期问题），新增share_capital/basic_info_static分类

> **V10.0**：zhb全局配置总包全面升级 - 进程安全文件锁、磁盘空间保护、智能日期筛选、节假日/证监会行业/中概股ADR/可转债/退市股数据导出、行业分类统一为申万标准、删除百度K线fallback；缓存系统优化 - cross_verify多进程失效修复、TTL分级策略延长、命中率统计自动输出；val脚本优化 - zhb零成本全市场数据、策略扫描范围扩大、字段访问安全加固（全策略统一使用.get()安全访问）；main.py任务顺序优化；ST股票涨跌幅新规适配（5%→10%）；修复f-string docstring误伤导致的ful第一章节消失、MACD键名不匹配、异步公告配置键名错误等关键问题

---

## 功能特性

- **6种报告类型**：短线(sht)、中线(med)、长线(lng)、完整(ful)、估值(val)、市场热点(mak)
- **多数据源整合**：新浪财经、东方财富、同花顺、通达信等
- **zhb全局配置总包**（V10.0）：一次TCP下载，全市场静态数据本地解析，零HTTP请求
  - **A级数据**：大板块成分、申万行业分类、节假日日历、证监会行业、券商名称表
  - **B级数据**：全市场统计快照（tdxstat）、资金流向快照（tdxstat2）
  - **辅助数据**：财报日历、新股申购、A+H股比价、中概股ADR、可转债、退市股对照表
- **进程安全文件锁**（V10.0）：多进程并发下载时自动加锁，避免重复下载和文件损坏
- **磁盘空间保护**（V10.0）：空间不足时自动清理旧缓存，保留最新文件
- **行业分类统一**（V10.0）：以申万行业为主，通达信行业为辅，对标公募基金标准
- **智能日期筛选**（V10.0）：根据脚本运行时机（收盘后/开盘前/休市日/盘中）自动判断是否使用zhb数据，盘中强制实时获取，确保数据准确性
- **节假日数据整合**（V10.0）：优先使用zhb.needini.dat节假日数据（1991-2030），覆盖范围更广，本地数据仅作为fallback
- **缓存TTL优化**（V10.0）：日频数据（K线/资金流/打板/龙虎榜）从1天延长至7天，历史数据（北向/解禁/融资融券）从3-7天延长至14-90天，减少重复网络请求
- **缓存命中率统计**（V10.0）：进程退出时通过atexit自动打印总命中率和分类命中率，为缓存优化提供数据支撑
- **val脚本全市场扫描优化**（V10.0）：使用zhb.stock_stats替代tdx_get_all_stocks，全市场数据加载从7.7秒降至<0.1秒；策略扫描范围扩大（200-300→500-1000），发现更多优质标的
- **main.py任务顺序优化**（V10.0）：调整执行顺序为val→mak→sht→med→lng→ful，全市场扫描产生的缓存被后续单股分析脚本复用
- **zhb字段映射重大修正**（V10.1，基于injoyai/tdx开源仓库源码验证）：
  - tdxstat字段：change_pct[6]、streak_days[5]（连涨连跌天数）、dividend_yield[10]（股息率）、change_5d[28]、change_10d[30]、change_ytd[21]（年初至今）、employee_count[15]（员工人数）
  - tdxstat2字段：amount[3]（今日成交额，万元）、amount_1d[5]、amount_2d[7]、ipo_price[16]（IPO发行价）、high_52w[17]、low_52w[18]、industry_code[13]
  - 新增full_market_snapshot（tdxstat+tdxstat2合并），一次调用获取全市场完整数据
- **全局股本缓存层**（V10.1）：新增sc_capital_cache.py模块，全局JSON文件缓存（cache/share_capital.json，90天TTL），市值=收盘价×总股本纯内存计算，零网络请求
- **val/mak脚本深度zhb化**（V10.1）：
  - val脚本：使用full_market_snapshot替代tdx_get_all_stocks，全市场数据加载从~7.7秒降至<0.1秒，策略扫描范围扩大至500-1000只
  - mak脚本：优先使用zhb全市场快照，失败自动回退TDX，全市场数据加载时间显著缩短
- **sht/med/lng/ful脚本zhb优先改造**（V10.1）：zhb数据作为主数据源，原有HTTP/TDX路径降为fallback
  - sht脚本：行业归属、股息率优先用zhb，阶段涨幅/52周区间zhb独有直接展示
  - med脚本：PE估值、股息率、行业归属优先用zhb，腾讯行情/东财HTTP降为fallback
  - lng脚本：PE/PB估值、历史最高价、股息率、行业归属优先用zhb，YTD/员工人数zhb独有
  - ful脚本：PE/PB估值、52周高低、阶段涨跌幅、股息率优先用zhb，K线计算/TDX行情降为fallback
- **缓存策略优化**（V10.1）：basic_info TTL从30天降至1天（修复市值/价格等动态字段缓存过期问题），新增share_capital/basic_info_static分类（90天TTL）
- **F10 全覆盖**（V9.1）：12 个 F10 函数 + 11 个 HTTP 函数 F10 优先逻辑 + 6 种新章节 + 数据质量核查附录
- **缓存交叉验证**（V9.2/V10.0修复）：11 个多天 TTL 分类启用交叉验证；V10.0修复多进程并发下因数据源含实时字段导致验证永远无法通过的问题，改为首次写入通过 valid_if 校验即标记已验证
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
- **GD上传根目录文件夹定位加固**（V9.5）：删除 `init_gd` 中冗余的二次验证逻辑，`retry_get_folder_interactive` 严格限定父文件夹搜索，避免同名文件夹重复创建
- **打板层**（V9.6）：新增 `get_limit_up_pool`/`get_limit_broken_pool`/`get_limit_down_pool` 函数，获取涨停池、炸板池、跌停池数据；集成到 sht 和 mak 报告
- **资金流降权**（V9.6）：融合 TDX TCP 资金流（权重1.0）和东财分钟级资金流（权重0.6），实现加权融合资金流数据
- **财联社快讯复活**（V9.6）：使用 `cls.cn/v1/roll/get_roll_list` 接口，本地签名（`sign=md5(sha1(字典序拼接的query))`），零key实现，与东财7×24快讯互为独立备份
- **官方备胎池**（V9.6）：新增龙虎榜官方备用源（深交所+上交所官方接口）、新浪资金流备用源，东财被封时自动fallback
- **舆情互动层**（V9.6）：新增 `cninfo_irm` 互动易问答函数，两步调用获取orgId和问答列表，支持按时间筛选
- **东财新闻JSONP解析修复**（V9.6）：东财search-api-web HTTP接口已失效（返回passportWeb而非新闻），删除HTTP fallback代码，仅保留 TDX F10 公司报道数据
- **东财7×24全球资讯接口更新**（V9.6）：从旧版 `np-listapi.eastmoney.com/comm/ws/build/list` 切换到 SKILL.md V3.4 推荐的 `np-weblist.eastmoney.com/comm/web/getFastNewsList`，返回 `fastNewsList` 结构
- **同花顺涨停揭秘**（V9.6）：新增 `ths_limit_up_pool` 函数，作为东财涨停池的增强源，提供涨停原因题材、封板成功率、板型等东财没有的字段，与东财接口不冲突
- **解禁接口字段修复**（V9.6）：更新东财 `RPT_LIFT_STAGE` 报表字段映射（`FREE_SHARES_TYPE`/`FREE_SHARES`），新增 `ABLE_FREE_SHARES` 字段，提高解禁数据准确性
- **行业排名排序修复**（V9.6）：东财行业板块接口添加 `fid=f3` 参数，确保按涨跌幅排序，`top`/`bottom` 切片正确反映涨幅最高/最低行业
- **北向资金降级警告**（V9.6）：当 sgt/hgt 比例超过3.0时标记数据质量为 degraded，发出警告日志，帮助用户识别异常数据
- **东财现金流量表**（V9.6）：新浪现金流量表API（xjllb）已失效，新增东财数据中心 `RPT_CASHFLOW` 接口替代，支持经营/投资/筹资活动现金流和现金等价物净增加额
- **mootdx依赖集成**（V9.6）：新增 `mootdx>=0.11` 依赖，与 easy-tdx 形成互补关系（easy-tdx负责资金流/板块/MacClient，mootdx负责复权数据/F10/分笔成交）
- **easy-tdx与mootdx互补方案**（V9.6）：两库为互补关系，非替代关系；easy-tdx擅长资金流、板块（MacClient）、实时行情；mootdx擅长复权数据（xdxr）、F10、分笔成交、连接更稳定

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
├── scripts/                  # 辅助脚本
│   ├── update_calendar.py    # 交易日历数据更新（chinese-calendar 库同步）
│   └── clean_cache.py        # 缓存清理快捷脚本（封装 stock_cache.py CLI）
├── docs/                     # 技术文档
│   └── architecture.md       # 项目架构与数据流图（Mermaid）
├── pyproject.toml            # pytest / mypy / black 等工具配置中心
├── requirements.txt          # 运行时依赖列表
├── requirements-dev.txt      # 开发依赖列表（pytest / mypy / black）
├── CHANGELOG.md              # 版本变更记录
├── CONTRIBUTING.md           # 贡献指南
├── CODE_OF_CONDUCT.md        # 社区行为准则
├── LICENSE                   # MIT 许可证
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
2. 下载 OAuth 2.0 凭证文件，保存为 `client_secrets.json`（项目根目录）
3. 首次运行时会弹出浏览器进行授权，授权后自动生成 `credentials.json`

> **注意**：
> - OAuth scope 为 `drive.file`，脚本只能看到由该脚本自身创建或打开过的文件/文件夹
> - 若 Google Drive 根目录无故出现个股文件夹，通常是桌面客户端同步冲突导致（详见 FAQ），脚本本身不会移动或删除已有文件夹

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
def get_dragon_tiger_board(code, days=30, include_seats=True):
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

### V10.3 (2026-07-16)

- 🔧 **zhb资金流向字段解锁**（基于zhb_analysis深度分析 + 双日Delta验证 + 公式验算）：
  - tdxstat2[9] → `main_net_buy_hands`（T日主力净买入量，手）
  - tdxstat2[10] → `main_net_buy_hands_1d`（T-1日主力净买入量，手）
  - tdxstat2[14] → `main_net_buy_amount`（T日主力净流入额，万元）
  - tdxstat2[15] → `main_net_buy_amount_1d`（T-1日主力净流入额，万元）
  - 验证方法：双日Delta滚动匹配（10/10通过）+ 公式验算（[9]×100×收盘价÷10000≈[14]，误差<1%）
- 📦 **新增便捷函数**：`get_main_net_buy`、`get_main_net_buy_amount`、`get_main_net_buy_amount_1d`
- 📊 **zhb字段时效性分级增强**：新增"准实时"字段分类（max_delay_days=1），资金流向字段归入此类
- 📋 **docs/roadmap.md**：新增实施路线图，覆盖阶段一（核心字段补全、阶段二（脚本增强）、阶段三（架构重构）

### V10.2 (2026-07-16)

- 🐛 **缓存命中率核心修复**（3个症结导致14+个分类0%命中率）：
  - cross_verify 读写互斥BUG：`get_cache` 的 `prev_value != value` 误删检查与 `set_cache` 数据变化分支冲突 → 14个cross_verify分类永久失效，删除误删检查
  - `_has_zero_price` 递归误杀：嵌套结构中任一子项 price=0 就跳过整条缓存 → 改为仅检查顶层
  - `today_str` 污染 key：`lockup_expiry`/`dragon_tiger` 参数含 `today_str` 导致跨日key不同 → 移除参数改为内部自动计算
  - `valid_if` 过严：`industry_peers`/`basic_info`/F10系列校验放宽，避免空值拒写
- 🐛 **zhb数据滞后优先级分级**：新增 `zhb_field_safe(field_name)` 函数，按字段时效性分级
  - 实时字段（change_pct/amount/price）：zhb日期必须是今天，否则fallback原接口
  - 阶段/静态字段（pe_ttm/high_52w/dividend_yield）：3天延迟可接受
  - mak脚本 `change_pct` 改为 `zhb_field_safe("change_pct")` 校验，val脚本用实时行情覆盖zhb的滞后change_pct
  - sht/med/lng 脚本 zhb 不新鲜时标注数据日期
- 🐛 **val脚本ImportError修复**：`full_market_snapshot` → `get_zhb_full_market_snapshot`
- 🐛 **"休市日"标签修复**：`get_market_status()` 交易日16:30后从 `closed` 改为 `post_close`，避免盘后运行脚本误显示"休市日"
- ⚠️ **函数签名变更**（向后不兼容）：`get_lockup_expiry` / `get_dragon_tiger_board` 移除 `today_str` 参数

### V10.1 (2026-07-15)

- 🔧 **zhb字段映射重大修正**（基于injoyai/tdx开源仓库源码验证）：
  - tdxstat：`change_pct` 从[2]修正为[6]，新增 `streak_days`[5]、`change_pct_1d`[7]、`change_pct_2d`[8]、`dividend_yield`[10]、`employee_count`[15]、`change_5d`[28]、`change_10d`[30]、`change_ytd`[21]
  - tdxstat2：`amount` 修正为[3]，新增 `amount_1d`[5]、`amount_2d`[7]、`ipo_price`[16]
  - 新增 `full_market_snapshot`（tdxstat+tdxstat2合并）、`market_stat2_snapshot` 等批量接口
- 📦 **全局股本缓存层**：新增 `stock_common/sc_capital_cache.py`，90天TTL，被动累积式构建，市值内存计算（收盘价×总股本/10000），零网络请求
- ⚡ **val脚本全策略切换zhb**：`full_market_snapshot` 替代 `tdx_get_all_stocks`，全市场加载从~7.7秒降至<0.1秒；结合全局股本缓存计算市值；流动性池从Top300扩大到Top500
- ⚡ **mak脚本全量切换zhb**：优先zhb全市场快照，失败时自动回退TDX MAC协议
- ⚡ **sht脚本zhb优先改造**：行业归属、股息率优先用zhb，阶段涨幅/52周区间zhb独有直接展示，原有HTTP/TDX路径降为fallback
- ⚡ **med脚本zhb优先改造**：PE估值、股息率、行业归属优先用zhb，阶段涨幅/52周区间zhb独有直接展示，腾讯行情/东财HTTP降为fallback
- ⚡ **lng脚本zhb优先改造**：PE/PB估值、历史最高价、股息率、行业归属优先用zhb，YTD/员工人数zhb独有直接展示，腾讯行情/`get_historical_high`降为fallback
- ⚡ **ful脚本zhb优先改造**：PE/PB估值zhb优先覆盖basic，52周高低/阶段涨跌幅zhb优先（K线计算降为fallback），股息率zhb优先（`tdx_get_dividend_history`降为fallback）
- 💾 **缓存策略优化**：`basic_info` TTL从30天调整为1天（修复动态字段缓存过期），新增 `share_capital` 分类（90天TTL）
- 🐛 **市值全为0修复**：新增全局股本缓存层，通过收盘价×总股本实时计算市值
- 🐛 **多策略共振无名称修复**：补充名称时同步更新 `_stock_map`

### V10.0 (2026-07-14)

- 📦 **zhb全局配置总包全面升级**：通过通达信 0x06B9 协议 TCP 下载 zhb.zip，一次下载全市场静态数据本地解析，零 HTTP 请求
  - A级数据：大板块成分（spblock.dat，突破400只限制）、申万行业分类（tdxzs3.cfg，467个四级分类）、节假日日历（needini.dat）、证监会行业（incon.dat，3703个）、券商名称表（brkcomp.dat，842家）
  - B级数据：全市场统计快照（tdxstat.cfg，7938只，35字段）、资金流向快照（tdxstat2.cfg，21字段）
  - 辅助数据：财报日历（tipinfo.dat，5609只）、新股申购（xgsg.cfg）、A+H股比价（tdxahrate.cfg）、中概股ADR（tdxadr.cfg，30只）、可转债（othersg.cfg）、退市股对照表（pttab.dat）
- 🔒 **进程安全文件锁**：多进程并发下载时自动加锁，防止重复下载和文件损坏；锁文件写入 PID，释放时验证归属，避免误删其他进程锁
- 💾 **磁盘空间保护**：空间不足时自动清理旧缓存，保留最新文件；下载使用临时文件+原子重命名，防止多进程冲突导致文件损坏
- 📅 **智能日期筛选**：根据脚本运行时机（收盘后/开盘前/休市日/盘中）自动判断是否使用 zhb 数据，盘中强制实时获取，确保数据准确性
- 🗓️ **节假日数据整合**：优先使用 zhb.needini.dat 节假日数据，但仅提取当年和前一年的可信数据，未来年份硬编码数据丢弃
- 🏷️ **行业分类统一**：以申万行业为主，通达信行业为辅，对标公募基金标准
- 🗑️ **删除百度K线fallback**：百度 K线接口已不稳定，全部删除，TDX 失败时走腾讯行情兜底
- ⚡ **缓存TTL优化**：根据数据特性延长TTL，减少重复网络请求
  - 日频数据（K线/资金流/打板/龙虎榜）：1天→7天（历史数据收盘后不变）
  - 历史数据：北向7天→30天、融资融券/大宗交易3天→14天、解禁7天→90天、公告7天→30天
  - 静态数据：basic_info/concept_blocks 7天→30天
- ⚡ **cross_verify多进程失效修复**：原逻辑要求两次获取数据完全相同才标记 verified=1，但多进程并发 + 数据源含实时字段（如 price/timestamp）导致 11 个分类交叉验证永远无法通过。新逻辑：首次写入通过 valid_if 校验即标记 verified=1，数据变化时用新数据替换并保持 verified=1
- 📊 **缓存命中率统计**：进程退出时通过 atexit 自动打印总命中率和分类命中率（按未命中数降序显示前10个低命中率分类），为后续优化提供数据支撑
- ⚡ **val脚本全市场扫描优化**：使用 zhb.stock_stats 替代 tdx_get_all_stocks，全市场数据加载从7.7秒降至<0.1秒；策略扫描范围扩大（周线/形态类200-300→1000，财务/筹码类200-300→500）；流动性池从Top300扩大到Top500
- 🔄 **main.py任务顺序优化**：调整执行顺序为 val→mak→sht→med→lng→ful，全市场扫描产生的缓存被后续单股分析脚本复用
- 🧹 **死代码清理**：删除 zhb_client.py 未使用的 `_load_from_cache` 和 `import struct`；删除 tdx_client.py 未使用的 `tdx_cache_clear`、`tdx_get_security_bars_qfq` 和三个缓存预热函数；删除 gd_uploader.py 未使用的 `run_report_to_gd`；删除 get_lng_report.py/get_med_report.py 未使用的 `generate_report` 同步包装；删除 get_val_report.py 未使用的 `get_all_stocks`；删除 stock_cache.py 未使用的 `cached_async` 装饰器
- 🧹 **冗余导入清理**：get_mak_report.py 移除 `requests`/`json`/`math`；get_lng_report.py 移除 `requests`/`time`/`re`；get_med_report.py 移除 `requests`/`time`
- 🐛 **运行时崩溃隐患修复**：修复 sc_datasource.py 缺失的 `tdx_get_quote_full` 导入、tdx_client.py 已删除的 `_baidu_kline_full_fallback` 调用点、sc_datasource.py 无意义的 global 声明
- 🧹 **无效 f-string 批量清理**：自动清理 27 个文件中的 364 处无效 f-string，消除 F541 警告（后通过 AST 验证恢复 19 个文件的 181 处有效 f-string）
- 🐛 **f-string docstring误伤修复**（6处）：_calc_macd/zhb_client 5处属性/tdx_client _tencent_batch_fallback 文档字符串被误加 f 前缀
- 🐛 **MACD键名不匹配**：`_calc_macd` 返回键名 `"di"` 改为 `"dif"`，修复信号判断和评分中的 KeyError
- 🐛 **异步公告配置键名错误**：`get_strategic_announcements_async` 中 `strategy_keywords` 改为 `announcement_keywords`，修复 sht/med/lng 公告全部丢失问题
- 🐛 **版本号/文案/格式修复**：移除 ful/sht 输出中的 "V8.5" 版本号；午休时段从"休市日"改为"午休时段"；mak 封板时间按 HHMMSS 正确解析；mak 跌停阈值区分板块；ful PE 为负时显示 "N/A"
- 🐛 **语法错误修复**：修复 sc_datasource.py 第684行 `\u9ff` 补全为 `\u9fff`，修复 SyntaxError 启动崩溃
- 🧹 **重复导入清理**：修复 stock_cache.py 重复导入 asyncio、tests/diag_tdx_compare.py 重复导入 TdxClient
- 🐛 **datetime 导入修复**：diag_v96_skill_verify.py 将循环内重复导入的 datetime 移到文件顶部

### v9.6 (2026-07-13)

- 🔌 **mootdx依赖集成**：`requirements.txt` 新增 `mootdx>=0.11`，与 easy-tdx 形成互补关系（easy-tdx负责资金流/板块/MacClient，mootdx负责复权数据/F10/分笔成交）
- 🚀 **打板层**：新增 `get_limit_up_pool`/`get_limit_broken_pool`/`get_limit_down_pool`/`get_limit_pool_summary` 函数，获取涨停池、炸板池、跌停池数据；集成到 sht 和 mak 报告
- 💰 **资金流降权**：新增 `get_fund_flow_weighted` 函数，融合 TDX TCP 资金流（权重1.0）和东财分钟级资金流（权重0.6），实现加权融合资金流数据
- 📰 **财联社快讯复活**：新增 `cls_telegraph` 函数，使用 `cls.cn/v1/roll/get_roll_list` 接口，本地签名（`sign=md5(sha1(字典序拼接的query))`），零key实现，与东财7×24快讯互为独立备份
- 🛡️ **官方备胎池**：新增龙虎榜官方备用源（深交所+上交所官方接口）、新浪资金流备用源，东财被封时自动fallback
- 💬 **舆情互动层**：新增 `cninfo_irm` 互动易问答函数，两步调用获取orgId和问答列表，支持按时间筛选
- 📊 **东财现金流量表**：新浪现金流量表API（xjllb）已失效，新增东财数据中心 `RPT_CASHFLOW` 接口替代，支持经营/投资/筹资活动现金流和现金等价物净增加额
- 🔝 **同花顺涨停揭秘**：新增 `ths_limit_up_pool` 函数，作为东财涨停池的增强源，提供涨停原因题材、封板成功率、板型等东财没有的字段
- ⚠️ **北向资金降级警告**：当 sgt/hgt 比例超过3.0时标记数据质量为 degraded，发出警告日志，帮助用户识别异常数据
- 🔧 **东财新闻JSONP解析修复**：删除已失效的 `search-api-web.eastmoney.com` HTTP fallback，仅保留 TDX F10 公司报道数据
- 🔧 **东财7×24全球资讯接口更新**：切换到 `np-weblist.eastmoney.com/comm/web/getFastNewsList`，返回 `fastNewsList` 结构
- 🔧 **解禁接口字段修复**：更新东财 `RPT_LIFT_STAGE` 报表字段映射（`FREE_SHARES_TYPE`/`FREE_SHARES`），新增 `ABLE_FREE_SHARES` 字段
- 🔧 **行业排名排序修复**：东财行业板块接口添加 `fid=f3` 参数，确保按涨跌幅排序

### v9.5 (2026-07-13)

- 🔧 **静默异常日志化**（28处）：`tdx_client.py`（23处）、`gd_uploader.py`（4处）、`get_med_report.py`（1处）中 `except Exception:` 静默吞异常全部添加 `_debug_log` 日志，提升调试可观测性
- ⚡ **aiohttp原生异步迁移**：`sc_datasource.py` 中10个HTTP异步函数从 `asyncio.to_thread` "假异步"包装改为原生 `aiohttp` 实现（`_async_request_with_retry` / `_async_quick_request`），剩余10个TDX依赖函数保留
- 🐛 **修复 _load_config 未定义错误**：`sc_datasource.py` 异步迁移过程中误写的不存在函数名，导致 sht/med/lng 脚本运行崩溃
- 🐛 **ful脚本显示修复**：价格走势改为近15日倒序显示（Day-1为最近日期）；新闻舆情文案从"近24小时"改为"近期"
- 🔧 **GD上传加固**：删除 `init_gd` 中冗余的二次验证逻辑，避免重复查询和潜在的根目录误匹配
- 📄 **文档与脚本完善**：补充 `docs/architecture.md` 架构文档、`scripts/clean_cache.py` 缓存清理脚本、`CONTRIBUTING.md` / `CODE_OF_CONDUCT.md` / `LICENSE` 等开源规范文件

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
- ⚠️ **报告盘前提示**：sht/med/lng 等报告在盘前模式时显示"⚠️ 盘前模式（9:30前），以下行情数据基于上一交易日收盘数据"
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
- 🧹 **死代码清理**：同步 `generate_report()` 替换为薄包装（`asyncio.run()` 调用异步版），删除 `get_lng_report.py`、`get_med_report.py`、`get_sht_report.py` 中的死代码辅助函数
- ✅ **新增历史分析模块**：`analyze_history.py` 实现 `save_snapshot()` 智能合并快照和 `analyze_history()` 跨日期趋势背离检测（单日突变 |Δ|≥15分 / 连续≥3天同向且总变化≥15分）
- 🐛 **修复趋势检测逻辑**：修正连续趋势判定条件（`run_len + 1 >= TREND_MIN_DAYS`），删除 `TREND_STEP_THRESHOLD` 避免小步累加噪音

### v8.5.0 (2026-06-22)

- ✅ **新增龙虎榜席位增强**：22位游资席位数据库（legend/new_gen/regional/new_2025分级），席位风格标签、溢价判断、席位质量评分
- ✅ **新增杀猪盘8信号检测**：`trap_detector.py`实现8维检测框架 *(V9.4已删除：API未接入上层报告)*
- ✅ **新增数据质量HARD-GATE**：13条数据质量检查清单，critical级别错误自动阻断报告生成
- ✅ **新增多档分析深度**：支持`--depth lite/medium/deep`三档（快速30秒/标准5分钟/深度15分钟）
- ✅ **新增多评委评审团**：价值派/成长派/游资派/综合派四套评分体系，支持分歧度检测
- ✅ **新增社交热榜聚合**：`social_sentiment.py`支持6平台情绪聚合（需API认证） *(V9.4已删除)*
- ✅ **新增机构估值方法库**：`valuation_methods.py`实现DCF/DDM/PEG等多种估值方法 *(V9.4已删除：API未接入上层报告)*
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

## 许可证

MIT License

---

## 免责声明

本项目仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。使用本工具产生的任何投资损失，作者不承担责任。

---

## 联系方式

如有问题或建议，欢迎提交 [Issue](https://github.com/tsy1102/a-stock-data/issues)。
