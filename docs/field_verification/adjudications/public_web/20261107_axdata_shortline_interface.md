# AxData `stock_shortline_indicators_tdx` 接口文档核验

- 核验日期：2026-11-07
- 文档：[AxData 短线指标接口](https://electkismet.github.io/AxData/interfaces/stock_shortline_indicators_tdx.html)
- 接口：`stock_shortline_indicators_tdx`，`POST /v1/request/stock_shortline_indicators_tdx`
- 文档标注提供方：`axdata.source.tdx_external`；来源：通达信 / TDX
- 文档说明：临时请求实时快照、日 K、财务快照，并使用 AxData 缓存的历史统计资源作为分母；返回一条短线指标记录。

项目 `requirements.txt` 和当前 Python 环境均为 `axdata==0.1.4`。`scripts/capture_verified_collectors.py::collect_axdata` 通过 `stock_common.get_shortline_indicators_result` 调用该接口，并把接口返回原样保存在 `stocks[code].data`，未改写下面的输出字段名。

## 返回字段与文档语义

| 接口字段 | 文档定义摘要 | 单位 |
|:--|:--|:--|
| `instrument_id` | AxData 统一证券代码 | — |
| `symbol` | 交易所原始六位证券代码 | — |
| `tdx_code` | 带市场前缀的 TDX 证券代码 | — |
| `exchange` | AxData 交易所代码（SSE / SZSE / BSE） | — |
| `stats_date` | 历史统计分母日期，来自 `tdxstat` / `tdxstat2` | 日期 |
| `open_price` | 开盘价 | 元 |
| `pre_close` | 昨收价 | 元 |
| `open_change_pct` | 开盘涨幅，百分比数值 | % |
| `open_amount` | 开盘金额 | 元 |
| `open_volume_hand` | 按开盘金额 / 开盘价 / 100 估算的开盘成交量 | 手 |
| `open_volume_ratio` | 开盘成交量 / 近 5 个完整交易日平均每分钟成交量 | 倍 |
| `open_turnover_z` | 开盘成交量 / 流通股本 Z 口径 | % |
| `open_prev_amount_ratio` | 开盘金额 / 昨成交额 × 100 | % |
| `auction_prev_volume_ratio` | 今日开盘成交量 / 昨开盘成交量 | 倍 |
| `opening_rush` | TDX 实时快照携带的开盘抢筹百分比 | % |
| `open_prev_seal_ratio` | 开盘金额 / 昨封单额 × 100 | % |
| `prev_amount` | 昨成交额 | 元 |
| `prev_seal_amount` | 昨封单额；负值通常表示昨日收盘跌停封单 | 元 |
| `prev2_seal_amount` | 前封单额 | 元 |
| `prev_open_volume_hand` | 昨开盘成交量 | 手 |
| `prev_open_amount` | 昨开盘金额 | 元 |
| `float_shares` | 普通财务口径流通股 | 股 |
| `float_market_value` | 普通流通股 × 当前价 | 元 |
| `free_float_shares` | 流通股本 Z / 自由流通股本口径 | 股 |
| `free_float_market_value` | 流通股本 Z × 当前价 | 元 |
| `seal_amount` | 封单额 | 元 |
| `seal_to_amount_ratio` | 封单额 / 当前成交额 | 比率 |
| `seal_to_float_ratio` | 封单额 / 流通市值 Z × 100 | % |
| `seal_prev_ratio` | 当前封单额 / 昨封单额 | 比率 |
| `limit_stat_days` | 几天几板统计窗口天数 | 天 |
| `limit_up_count_in_stat_days` | 统计窗口内涨停数 | 次 |
| `limit_board_text` | 几天几板描述文本，例如“7天5板” | — |
| `limit_up_streak_days` | 连板天数 | 天 |
| `year_limit_up_days` | 年内涨停天数 | 天 |

本文只核验该接口自身公开的字段名称、定义和单位；AxData 文档同时明确该接口来源为 TDX。这不构成 AxData 与 TDX 独立的来源证明。
