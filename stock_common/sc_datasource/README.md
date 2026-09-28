# stock_common/sc_datasource/ — 数据源查询子包

> **来源**: V17.2 将原单文件 `sc_datasource.py`（100+ 函数）按数据源拆分为本子包; 拆分前单文件备份见 `docs/backups/_sc_datasource_singlefile_backup.py`。
> 对外接口**保持兼容**: `from stock_common.sc_datasource import <fn>` 与旧 `sc_datasource.py` 命名空间一致（`__init__.py` 统一再导出）。
> 报告脚本与 main.py 经 `stock_common/__init__.py` 门面转引: `from stock_common import <data_source_fn>`。

## 设计约束

- **零导入期环**: 本子包所有跨边界引用（`core.data_provider` / `stock_common.*`）一律**函数体内懒 import**, 不触发 `core↔stock_common` 导入期循环(V17.3 后该循环已在 `core/_accessors.py` 叶子层根治, 但本包仍保持懒引约定)。
- **依赖方向**: 子模块单向依赖 `_shared`(共享状态/常量) 与上层 `core` / `stock_common`; `_official_backup.py` 为历史片段, **不参与运行时**, 仅供回溯。

## 各子模块职责

| 子模块 | 职责 | 关键导出(示例) |
|:---|:---|:---|
| `__init__.py` | 子包入口, 统一再导出全部数据源函数, 对外兼容旧命名空间 | 见下方各模块 |
| `_shared.py` | 跨片段**共享可变状态**(单实例) + 公共常量 / 字段段定义 | `_ZHB_*_FIELDS` / `_EM_*` / `_get_shared_state()` |
| `_convertible.py` | 可转债条款、转股价值与溢价率 | `convertible_bonds` |
| `_eastmoney.py` | 东方财富接口层: 接口映射 / 多域健康矩阵 / 资金流 / 板块 / 研报 / 个股全景 | `get_em_*` / `check_em_health` |
| `_etf.py` | 上交所/深交所 ETF 份额数据 | `etf_shares` |
| `_events.py` | 业绩预告、机构调研、股东变动、质押与新股申购 | 事件查询函数 |
| `_financials.py` | 财务数据: 利润表 / 资产负债表 / 现金流量表 / 估值指标 | `get_financials` / `get_roe_trend` |
| `_futures_sina.py` | 新浪期货日 K 数据 | `futures_kline_sina` |
| `_holders.py` | 股东与股本: 十大股东 / 限售解禁 / 股本变动 | `get_holders` / `get_restricted_relief` |
| `_industry.py` | 行业映射与成分(生成 `cache/em_industry_*.json` 缓存) | `get_industry_map` / `get_industry_members` |
| `_macro.py` | 宏观指标、利率与宏观日历 | 宏观查询函数 |
| `_news_wscn_cctv.py` | 华尔街见闻与央视新闻 | `cctv_news` / 新闻查询函数 |
| `_pools.py` | 涨停池 / 炸板池 / 跌停池 / 重点监控(push2ex) | `get_limit_pool_summary` |
| `_quotes.py` | 实时行情 / 快照 / 竞价 / 概念; `get_concept_from_zhb`(V17.3 改引 `core._accessors`) | `get_realtime_quote` / `get_concept_from_zhb` |
| `_research_sina.py` | 新浪研报列表（第二来源） | `sina_research_reports` |
| `_sse_e_interaction.py` | 上证 e 互动问答 | `sse_e_interaction` |
| `_st_list.py` | 全市场 ST / *ST 风险警示名单 | `st_stock_list` |
| `_ticks.py` | 腾讯逐笔成交 | `tencent_ticks` |
| `_v39_compat.py` | 上游适配器共用 helper 的本地兼容实现 | `_v39_*` helpers |
| `_zhb.py` | ZHB 行情衍生字段: 成交额 / 年至今涨跌 / 股息率 / 主力净额 / 连板天数等(V17.3 改引 `core._accessors`) | `get_amount_wan` / `get_dividend_yield` / `get_streak_days` |
| `_misc.py` | 其他零散数据源: 互动易 / 新闻 / 公告 / 情绪 | `get_cninfo_irm` / `get_news` |
| `_official_backup.py` | 单文件时代的官方备份片段(**参考用, 不主动调用**) | — |

## 调用约定

```python
# 推荐: 经 stock_common 门面
from stock_common import get_realtime_quote, get_limit_pool_summary

# 或直接经子包(接口一致)
from stock_common.sc_datasource import get_financials
```

> 修改导出: 在对应子模块定义函数后, 若需经 `stock_common` 顶层暴露, 同步更新 `stock_common/__init__.py` 的 `__all__` 与 from-import 块(见 `stock_common/README.md` 关键约定)。
