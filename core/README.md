# core/ — 核心模块包

> 定位: 项目核心支撑模块(数据层/传输层/缓存/日历同步/上传/跨边界访问器), 由根目录报告脚本(`get_*_report.py`)、`main.py`、`stock_common/`、`scripts/`、`tests/` 通过 `from core import X` 引用。

## 目录结构

```
core/
├── __init__.py        # 包入口——保持空(避免过早触发子模块导入副作用)
├── config.py          # 全局配置集中管理(超时/限流/熔断常量)
├── data_provider.py   # 统一数据层(canonical 强类型合约 + 字段路由 + 多级 fallback + 估值工具)
├── _accessors.py      # 跨边界访问器叶子模块
├── _tdx_handshake_patch.py # eltdx 握手补丁(通过动态模块适配兼容外部实现)
├── eltdx_adapter.py   # 将 eltdx 适配为项目所需接口，并提供 ZHB/短线数据入口
├── source_priority.py # 批量预取后的逐股行情回退优先级契约
├── gd_uploader.py      # Google Drive 上传(google-auth + google-api-python-client)
├── stock_cache.py      # 统一缓存层(SQLite + L1 内存 + TTL + cross_verify + CLI)
├── tdx_client.py       # 通达信 TCP 统一层(运行时使用 eltdx；保留兼容适配边界)
├── zhb_client.py       # 通达信 ZHB 压缩包下载、解析与本地缓存
└── zhb_sync.py         # ZHB 自动化入库管道(定时/手动/状态, 命令行: python -m core.zhb_sync)
```

## 各模块职责

| 模块 | 职责 | 主要导出 |
|:---|:---|:---|
| config.py | 超时/限流/熔断阈值 | HTTP_TIMEOUT_* / TDX_MIN_INTERVAL / MAX_RETRY_COUNT 等常量 |
| data_provider.py | 报告层统一数据入口, get_canonical_stock_data 强类型合约, 缓存+多源 fallback | get_canonical_stock_data / get_market_snapshot_async 等 |
| _accessors.py | 【V17.3】跨边界访问器: 概念/股息率/年至今涨跌/成交额/主力净额/连板天数等。顶层仅依赖 `core.stock_cache`(真叶子) + `typing`, **零 `stock_common` 顶层依赖**, 跨引统一在函数体内懒 import | get_concept_from_zhb / get_dividend_yield / get_change_pct / get_change_ytd / get_amount_wan / get_main_net_buy / get_streak_days |
| eltdx_adapter.py | eltdx 客户端兼容层；提供行情/F10/ZHB 文件下载和批量短线数据能力 | `create_eltdx_adapter` / `download_eltdx_report_file` / `get_eltdx_shortline_bundle` |
| source_priority.py | 定义批量预取后逐股行情的回退顺序契约，供统一层和回归测试核对 | 行情来源优先级常量 |
| _tdx_handshake_patch.py | eltdx/TDX 握手兼容补丁；隔离对外部模块动态 API 的访问 | 由 `tdx_client.py` 内部加载 |
| gd_uploader.py | GD 上传(凭据在 仓库根/credentials/ 子目录) | init_gd / upload_stock_report_by_code |
| stock_cache.py | `@cached` 装饰器 + SQLite 持久化缓存；按 TTL 和缓存键管理跨调用结果 | cached / TTL / make_valid_if; CLI: `python -m core.stock_cache stats` |
| tdx_client.py | 通达信 TCP 客户端统一入口，封装板块、行情与连接管理 | tdx_get_security_bars / tdx_get_quote_full 等 |
| zhb_client.py | ZHB 压缩包下载、解析与缓存（原包位于 `cache/zhb/`） | get_zhb / get_zhb_data_date 等 |
| zhb_sync.py | 每日同步调度 | main(); `python -m core.zhb_sync --once` |

## 设计约束

- **跨层访问器集中在 `_accessors.py`**：该模块避免 `core` 与 `stock_common.sc_datasource` 的导入期循环；新增跨层取数逻辑时，保持函数体内懒导入，并通过现有导入顺序测试验证。
- **懒 import 仍是硬约定**: 模块间互相引用(尤其 ↔ `stock_common` 的数据源子模块)一律函数体内懒 import, 防止重新引入循环依赖(历史踩坑: zhb_client↔stock_calendar 递归爆栈, 见 AGENTS.md §12)。
- **`__file__` 路径**: 模块内基于 `__file__` 的仓库根推导已按包化上提一级
  (`dirname(dirname(abspath(__file__)))` = 仓库根); 新增路径推导遵循同一模式。
- **CLI 运行**: `python -m core.zhb_sync ...` / `python -m core.stock_cache <action>`
  (在仓库根目录运行; 包化后不支持 `python core/zhb_sync.py` 直跑)。
