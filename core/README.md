# core/ — 核心模块包(V17.3 目录整理)

> 定位: 项目核心支撑模块(数据层/传输层/缓存/日历同步/上传/跨边界访问器), 由根目录报告脚本(`get_*_report.py`)、`main.py`、`stock_common/`、`scripts/`、`tests/` 通过 `from core import X` 引用。

## 目录结构

```
core/
├── __init__.py        # 包入口——保持空(避免过早触发子模块导入副作用)
├── config.py          # 全局配置集中管理(超时/限流/熔断常量)
├── data_provider.py   # 统一数据层(canonical 强类型合约 + 字段路由 + 多级 fallback + 估值工具)
├── _accessors.py      # 【V17.3】跨边界访问器叶子模块(消除 data_provider↔stock_common 导入期循环依赖)
├── gd_uploader.py      # Google Drive 上传(google-auth + google-api-python-client)
├── stock_cache.py      # 统一缓存层(SQLite + L1 内存 + TTL + cross_verify + CLI)
├── tdx_client.py       # mootdx/easy_tdx 统一层(K线/F10/资金流/板块, 白名单主机)
├── zhb_client.py       # 通达信 zhb.zip 全局配置总包下载与解析(45 文件)
└── zhb_sync.py         # ZHB 自动化入库管道(定时/手动/状态, 命令行: python -m core.zhb_sync)
```

## 各模块职责

| 模块 | 职责 | 主要导出 |
|:---|:---|:---|
| config.py | 超时/限流/熔断阈值 | HTTP_TIMEOUT_* / TDX_MIN_INTERVAL / MAX_RETRY_COUNT 等常量 |
| data_provider.py | 报告层统一数据入口, get_canonical_stock_data 强类型合约, 缓存+多源 fallback | get_canonical_stock_data / get_market_snapshot_async 等 |
| _accessors.py | 【V17.3】跨边界访问器: 概念/股息率/年至今涨跌/成交额/主力净额/连板天数等。顶层仅依赖 `core.stock_cache`(真叶子) + `typing`, **零 `stock_common` 顶层依赖**, 跨引统一在函数体内懒 import | get_concept_from_zhb / get_dividend_yield / get_change_pct / get_change_ytd / get_amount_wan / get_main_net_buy / get_streak_days |
| gd_uploader.py | GD 上传(凭据在 仓库根/credentials/ 子目录) | init_gd / upload_stock_report_by_code |
| stock_cache.py | @cached 装饰器 + SQLite 持久化, 全仓 ~70 处使用 | cached / TTL / make_valid_if; CLI: `python -m core.stock_cache stats` |
| tdx_client.py | 通达信 TCP 客户端封装(MAC 协议板块/行情) | tdx_get_security_bars / tdx_get_quote_full 等 |
| zhb_client.py | zhb.zip 下载解析(缓存到 cache/zhb/) | get_zhb / get_zhb_data_date 等 |
| zhb_sync.py | 每日同步调度 | main(); `python -m core.zhb_sync --once` |

## 设计约束

- **导入期循环依赖已根治(V17.3)**: 原 `data_provider.py` 顶层 `from stock_common.sc_network import ...` 与 `stock_common/sc_datasource/_quotes.py`、`_zhb.py` 顶层 `from core.data_provider import ...` 构成导入期环, 生产靠入口先载 `stock_common` 规避, 直引 `import core.data_provider` 必崩 `ImportError`。V17.3 将 7 个跨边界访问器抽离到 **`core/_accessors.py` 叶子模块**(顶层零 `stock_common` 依赖), 并改 `data_provider.py` 的 `_debug_log` 为函数内懒引 `_fallback_logger` → **环已彻底消除, 现在 `import core.data_provider` 正反顺序均可直接成功**。
- **懒 import 仍是硬约定**: 模块间互相引用(尤其 ↔ `stock_common` 的数据源子模块)一律函数体内懒 import, 防止重新引入循环依赖(历史踩坑: zhb_client↔stock_calendar 递归爆栈, 见 AGENTS.md §12)。
- **`__file__` 路径**: 模块内基于 `__file__` 的仓库根推导已按包化上提一级
  (`dirname(dirname(abspath(__file__)))` = 仓库根); 新增路径推导遵循同一模式。
- **CLI 运行**: `python -m core.zhb_sync ...` / `python -m core.stock_cache <action>`
  (在仓库根目录运行; 包化后不支持 `python core/zhb_sync.py` 直跑)。
