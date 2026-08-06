# 项目结构与数据流图

本项目采用「**main.py 调度 → 子进程执行报告脚本 → 调用数据源层 → 上传 GD**」的层次化架构。
下文使用 Mermaid 描述核心模块之间的实际调用关系，便于开发者快速了解系统全景。

> 📌 **V12.4+ 重要更新**：所有 5 大报告脚本（ful 已删）统一继承 `BaseReportRunner` 基类（V12.4），消除样板代码；V12.5 进一步将 GD 上传逻辑真正落地到基类辅助方法。

## 1. 总体架构

```mermaid
graph TD
    User([用户 CLI]) --> Main[main.py<br/>统一入口]
    Main -- "asyncio.create_subprocess_exec" --> Sht[get_sht_report.py]
    Main -- "asyncio.create_subprocess_exec" --> Med[get_med_report.py]
    Main -- "asyncio.create_subprocess_exec" --> Lng[get_lng_report.py]
    Main -- "asyncio.create_subprocess_exec" --> (sht/med/lng/val/mak)
    Main -- "asyncio.create_subprocess_exec" --> Val[get_val_report.py]
    Main -- "asyncio.create_subprocess_exec" --> Mak[get_mak_report.py]

    Sht -. "继承" .-> Runner[BaseReportRunner<br/>stock_common/sc_report_runner.py]
    Med -. "继承" .-> Runner
    Lng -. "继承" .-> Runner
    Ful -. "继承" .-> Runner
    Val -. "继承" .-> Runner
    Mak -. "继承" .-> Runner

    Sht --> SC[stock_common/<br/>sc_datasource / sc_network / sc_utils / sc_scoring]
    Med --> SC
    Lng --> SC
    Ful --> SC
    Val --> SC
    Mak --> SC

    SC -- "sc_datasource 委托" --> Tdx[tdx_client.py<br/>通达信行情]
    SC -- "aiohttp + aiosqlite" --> Cache[(cache/stock_cache.db<br/>SQLite + L1)]
    SC -- "requests/aiohttp" --> EastMoney[东方财富 API]
    SC -- "requests/aiohttp" --> Sina[新浪财经 API]
    SC -- "requests/aiohttp" --> Ths[同花顺 API]

    Sht --> GD[gd_uploader.py<br/>Google Drive 上传]
    Med --> GD
    Lng --> GD
    Ful --> GD
    Val --> GD
    Mak --> GD
    Runner -- "upload_single_report / upload_multi_reports" --> GD
    Ful -- "save_snapshot" --> AH[stock_common/analyze_history.py]

    GD -- "google-api-python-client" --> Drive[(Google Drive API<br/>a-stock-data/)]
```

## 2. 模块职责

| 模块 | 职责 |
|------|------|
| **`main.py`** | 统一 CLI 入口；通过 `asyncio.create_subprocess_exec` 串行执行各报告脚本（进程级并发默认 1） |
| **`get_*.py`** (6 个) | 6 种报告类型的执行入口，**继承 `BaseReportRunner`**；只需实现 `execute_pipeline()` 和 `upload_reports()`，其余样板代码由基类提供 |
| ├ `get_val_report.py` | 18 策略全市场发现引擎 |
| ├ `get_sht_report.py` | 短线策略个股分析报告 |
| ├ `get_med_report.py` | 中线深度投研报告 |
| ├ `get_lng_report.py` | 长线价投专属深度体检报告 |
| ├ ~~`get_ful_report.py`~~ | V16.3 O19 已删除（能力并入 sht/med/lng）|
| └ `get_mak_report.py` | 异动及行业轮动扫描报告 |
| **`stock_common/sc_report_runner.py`** | V12.4+ **核心基类**：`BaseReportRunner`，统一 CLI 解析 / Banner / Summary / GD 上传模板（`upload_single_report` / `upload_multi_reports`）/ TDX 资源清理 |
| **`stock_common/`** 包 | 数据源层与公共工具的集合，由各报告脚本统一调用 |
| ├ `sc_datasource.py` | 数据源适配层（新浪/东财/同花顺），含 `aiohttp` 异步与 `requests` 同步两套实现 |
| ├ `sc_network.py` | 限流、代理、UA 池、`_debug_log` 日志等基础网络工具；全局异步 Session 单例（V12.2） |
| ├ `sc_utils.py` | CLI 参数解析、配置加载、字符串清洗等通用工具 |
| ├ `sc_scoring.py` | 短/中/长线评分权重与计算函数 |
| ├ `sc_fault_tolerance.py` | 网络容错层：令牌桶限流、熔断器、随机 UA 池（V11.5） |
| ├ `analyze_history.py` | 快照保存、跨日期评分对比、趋势背离检测 |
| ├ `stock_calendar.py` | A 股交易日历（含节假日、调休） |
| └ `f10_parser.py` | 通达信 F10 文本解析器 |
| **`tdx_client.py`** | 通达信行情接口（实时行情、K 线、F10、财务数据等）；V12.0 移除 easy_tdx 依赖，由 `sc_datasource` 委托调用 |
| **`stock_cache.py`** | SQLite + TTL + 交叉验证 + L1/L2 双级缓存（`@cached` / `@cached_async`）；V12.5 修复 `_l1_clear()` 拼写错误回归 |
| **`data_provider.py`** | V11.0+ 统一数据中心层（ZHB 优先 → TCP 直连 → HTTP fallback），防投毒熔断 |
| **`gd_uploader.py`** | Google Drive 上传业务；提供 `init_gd` / `upload_stock_report_by_code` / `upload_type_reports` |
| **`config.py`** | V12.2 全局配置集中管理（网络超时、限流参数、防投毒阈值等） |

## 3. 单只股票的处理流程（以 `get_sht_report.py` 为例）

```mermaid
sequenceDiagram
    participant U as 用户
    participant M as main.py
    participant R as BaseReportRunner<br/>(基类)
    participant S as get_sht_report.py
    participant SC as stock_common
    participant TDX as tdx_client
    participant Cache as stock_cache.db
    participant GD as gd_uploader
    participant Drive as Google Drive

    U->>M: python main.py --sht 600519
    M->>S: subprocess 启动
    S->>R: ShtReportRunner().run()
    R->>R: parse_args() → Banner
    R->>S: execute_pipeline()
    S->>SC: 调用 sc_datasource 异步函数
    SC->>Cache: 查缓存 (L1 → L2)
    alt 缓存命中
        Cache-->>SC: 返回缓存值
    else 缓存未命中
        SC->>TDX: tdx_get_quote_full / tdx_get_security_bars ...
        SC->>新浪/东财/同花顺: aiohttp GET
        SC->>Cache: set_cache (TTL 到期)
    end
    SC-->>S: 返回数据 dict
    S->>S: 渲染报告 (60 多个章节)
    S-->>R: 返回 PipelineResult
    R->>R: _handle_gd_upload()
    R->>S: upload_reports()
    S->>R: 委托 upload_multi_reports()
    R->>GD: upload_stock_report_by_code(...)
    GD->>Drive: files.create / files.update
    Drive-->>GD: file_id
    GD-->>S: True / False
    R->>R: _print_summary() + cleanup_tdx()
    S-->>M: 退出码
    M-->>U: 完成提示
```

### 3.1 BaseReportRunner 生命周期（V12.4+）

```mermaid
graph LR
    A[Runner().run()] --> B[parse_args CLI 解析]
    B --> C[_print_banner 启动 Banner]
    C --> D[execute_pipeline 子类实现]
    D --> E{成功?}
    E -- "是" --> F[_handle_gd_upload]
    F --> G[upload_reports 子类委托]
    G --> H[upload_single_report 或 upload_multi_reports]
    E -- "否" --> I[异常捕获 + _debug_log]
    I --> J[finally: cleanup_tdx + _print_summary]
    F --> J
    H --> J
```

## 4. 并发与限流策略

```mermaid
graph LR
    A[main.py] -- "进程级串行 (concurrency=1)" --> B[get_sht_report.py]
    A -- "进程级串行" --> C[get_med_report.py]
    A -- "进程级串行" --> D[get_lng_report.py]

    B -- "Semaphore(3) + 1.0s" --> E[东财接口]
    B -- "Semaphore(5) + 0.2s" --> F[其他接口]
```

- **进程级串行**：`main.py` 通过子进程方式一次只跑一个报告脚本，避免东财接口请求叠加导致被封。
- **脚本级并发**：单个 `get_*.py` 内部用 `asyncio.Semaphore(3)` 并发 3 只股票，配合 1.0s 间隔。
- **跨进程文件锁**：`stock_cache.py` 使用文件锁协调多进程对 SQLite 缓存的并发写。

## 5. Google Drive 上传流程

```mermaid
graph TD
    A[脚本启动] --> B{是否 --no-upload?}
    B -- "是" --> C[跳过上传]
    B -- "否" --> D[init_gd]
    D --> E{OAuth 凭证有效?}
    E -- "否" --> F[弹窗 OAuth 授权]
    F --> G[保存 credentials.json]
    E -- "是" --> G
    G --> H[retry_get_folder_interactive<br/>查找/创建 a-stock-data]
    H --> I{成功获取 root_id?}
    I -- "否" --> J[用户选择跳过或重试]
    I -- "是" --> K[upload_stock_report_by_code]
    K --> L[retry_get_folder_interactive<br/>查找/创建 股票子文件夹]
    L --> M[upload_or_update_to_drive<br/>files.create / files.update]
    M --> N[txt 文件已同步至云端]
```

> **注意**：代码仅会查找/创建文件夹、上传/覆盖文件，**不会移动或删除已有文件夹**。
> 若根目录出现个股文件夹，根因通常是 Google Drive 桌面客户端的同步冲突，
> 而非脚本行为。详见 `README.md` FAQ 章节。

## 6. 缓存层设计

```mermaid
graph LR
    A[业务函数] -- "@cached('dragon_tiger', ttl=...)" --> B[stock_cache.py]
    A2[异步业务函数] -- "@cached_async('financial', ...)" --> B
    B --> C{SQLite cache_entries 表}
    C -- "命中 + 未过期" --> D[直接返回]
    C -- "未命中或过期" --> E[调用原始函数]
    E --> F[写入缓存 (TTL 计算)]
```

- **TTL 分级**（详见 `stock_cache.py` 顶部说明）：
  - 静态数据（股票基本信息、概念板块）：7 天
  - 财务数据（财报、资产负债表）：90 天
  - 日频数据（龙虎榜、北向、融资融券）：当日有效
  - 研报：3 天
  - 行业/概念热度：24 小时
- **交叉验证**：11 个多天 TTL 分类启用两次获取对比，写入 `prev_value` / `verified` 字段。
- **CLI**：`python stock_cache.py stats/clear-all/clear --category <name>`。

## 7. 文件清单

| 类别 | 文件 |
|------|------|
| 入口 | `main.py` |
| 报告脚本 | `get_sht_report.py` / `get_med_report.py` / `get_lng_report.py` / `get_val_report.py` / `get_mak_report.py`（ful 已删）|
| **Runner 框架**（V12.4+） | `stock_common/sc_report_runner.py` |
| 数据源层 | `tdx_client.py` / `stock_common/sc_datasource.py` / `stock_common/sc_network.py` |
| 数据中心 | `data_provider.py`（V11.0+ 统一入口） |
| 容错层 | `stock_common/sc_fault_tolerance.py` |
| 缓存 | `stock_cache.py` |
| 上传 | `gd_uploader.py` |
| 全局配置 | `config.py`（V12.2+） |
| 工具脚本 | `scripts/update_calendar.py` |
| 公共模块 | `stock_common/sc_utils.py` / `stock_common/sc_scoring.py` / `stock_common/analyze_history.py` / `stock_common/stock_calendar.py` / `stock_common/f10_parser.py` |
| 测试 | `tests/test_*.py` / `tests/diag_*.py` / `tests/conftest.py` |
| 文档 | `README.md` / `CHANGELOG.md` / `CONTRIBUTING.md` / `CODE_OF_CONDUCT.md` / `LICENSE` / `docs/architecture.md` / `docs/roadmap.md` / `docs/field_dict.md` |
## 8. V12.6 字段路由决策层（基于运行时机 + 字段类型）

V12.6 重塑 `data_provider.py` 的字段获取逻辑，引入两个核心常量：

```python
REQUIRES_REALTIME_HTTP = frozenset({
    # 行情类
    "price", "change_pct", "amount", "volume",
    "open", "high", "low", "prev_close",
    # 资金流类
    "main_net_buy_hands", "main_net_buy_amount",
})

ZHB_SUFFICIENT = frozenset({
    # 估值类
    "pe_ttm", "pb", "dividend_yield", "turnover_pct",
    # 财务/股本/历史/板块
    "net_profit", "revenue", "total_shares", "industry",
    ...
})
```

**简化决策规则**：
```
if 运行时机 == 盘前:
    → 所有字段都用 ZHB
elif 字段 in REQUIRES_REALTIME_HTTP:
    → HTTP（行情/资金流）
else:
    → ZHB（估值/财务/股本/板块）
```

详见 `docs/field_dict.md` 第 5 节。

## 9. V13.x dataclass Schema 层（opt-in 升级路径）

V13.0 创建 `stock_common/sc_schema.py`，定义：

- 3 个 Enum：`TimeAnchor` / `DataSource` / `Unit`
- `FieldSpec` dataclass（slots=True, frozen=True）
- 34 个核心字段的元数据表 `FIELD_SPECS`
- `NormalizedQuote` 归一化行情快照

V13.1 缓存层透明序列化：
- `_serialize_for_cache(value)`: dataclass → dict
- `_deserialize_from_cache(value, target_cls)`: dict → dataclass
- L1/L2 缓存统一返回 dict（不破坏现有调用）

V13.1 data_provider opt-in 接口：
- `get_stock_composite_dataclass(code)` → `NormalizedQuote`
- `get_market_snapshot_dataclass(codes)` → `{code: NormalizedQuote}`
- `dict_to_normalized_quote(code, raw, source)` 通用工具

V13.2 性能压测（5000 记录，Python 3.12）：

| 指标 | dict | dataclass (slots=True) | 改进 |
|:---|:---:|:---:|:---:|
| 内存/对象 | 184 B | 56 B | **-70%** |
| 字段访问 (1M reads) | 0.066s | 0.054s | **+21% 速度** |
| json.dumps | 0.005s | 0.012s | -172% |

**结论**：dict 作为默认接口保留，dataclass 作为可选升级（opt-in）。

## 10. 工具脚本（scripts/）

| 脚本 | 用途 |
|:---|:---|
| `scripts/run_with_system_python.bat` | 一键使用系统 Python 3.12 运行命令（避免 TRAE 内置 Python 抢占） |
| `scripts/run_with_system_python.ps1` | PowerShell 版本 |
| `scripts/test_em_batch_quotes_limit.py` | V12.6 HTTP 批量上限实测（5 阶段 100/500/1000/2000/5000 只股票） |
| `scripts/perf_compare.py` | V13.2 dataclass vs dict 性能压测 |
| `scripts/update_calendar.py` | 从 chinese_calendar 库更新交易日历 |

