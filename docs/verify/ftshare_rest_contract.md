# FTShare REST 官方字段契约

此文件记录 FTShare Gateway 公共 REST 接口的 A 股行情列表契约，供采集、字段登记和日常碰撞共同引用。

## 接口与证据边界

- 接口目录：[FTShare Gateway 接口表](https://market.ft.tech/gateway/doc/p/pb8eizu3)
- 行情接口文档：[A 股行情列表](https://market.ft.tech/gateway/doc/p/mdsj0xyo)
- 请求：`GET /api/v1/market/data/daec/stocks/all`，认证头为 `FTSHARE_API_KEY`。
- 按文档使用 `symkey IN ["600000.XSHG"]` 形式筛选，并按分页字段逐页读取；日常采集上限为 200 只，单页最多 40 只，页间至少间隔 2 秒。遇到 403、429 或其他请求错误不重试。
- 此接口只提供实时行情快照，不提供历史日期参数。采集器按返回项 `ts_millis` 的上海交易日期核验项目有效日期；日期不匹配的记录不混入当日样本。
- 下表语义来自接口文档的返回字段表，中文为项目译注；计量单位只在接口文档明确时登记。官方接口身份和字段定义已确认，底层数据提供方以及与其他公开源是否独立仍未确认。
- 文档定义字段可作为**语义契约锚**参与常规碰撞。达到统计门槛的结果标为 `L1-C`，与要求来源独立性的 `L1` / `L1-U` 分开报告，也不会自动写入定案状态。

## 官方返回字段

| 字段 | 接口文档含义 | 类型 | 单位 | 注册状态 |
|:--|:--|:--|:--|:--|
| `symbol` | 证券代码（含交易所后缀） | string | — | 官方契约锚 |
| `name` | 证券名称 | string | — | 官方契约锚 |
| `open` | 开盘价 | string | 元/股 | 官方契约锚 |
| `high` | 最高价 | string | 元/股 | 官方契约锚 |
| `low` | 最低价 | string | 元/股 | 官方契约锚 |
| `close` | 收盘价/最新价 | string | 元/股 | 官方契约锚 |
| `prev_close` | 前收盘价 | string | 元/股 | 官方契约锚 |
| `change` | 价格涨跌额 | string | 元/股 | 官方契约锚 |
| `change_rate` | 日涨跌幅；0.03 表示 3% | number | 比率 | 官方契约锚 |
| `volume` | 成交量 | integer | 股 | 官方契约锚 |
| `turnover` | 成交额 | string | 元 | 官方契约锚 |
| `amplitude` | 价格振幅 | number | — | 官方契约锚 |
| `avg` | 平均价格 | number | — | 官方契约锚 |
| `bid_ask_ratio` | 买卖盘比率 | number | — | 官方契约锚 |
| `turnover_rate` | 换手率 | number | — | 官方契约锚 |
| `market_cap` | 总市值 | string | 元 | 官方契约锚 |
| `tradable_a_market_cap` | A 股流通市值 | string | 元 | 官方契约锚 |
| `pe_ttm` | 滚动市盈率（TTM） | number | — | 官方契约锚 |
| `board` | 板块标识 | string | — | 官方契约锚 |
| `st` | 是否为 ST | boolean | — | 官方契约锚 |
| `status` | 证券状态 | string | — | 官方契约锚 |
| `shares` | 总股本 | integer | 股 | 官方契约锚 |
| `float_a_shares` | A 股流通股数 | integer | 股 | 官方契约锚 |
| `listing_date` | 上市日期 | string | — | 官方契约锚 |
| `change_rate_day5` | 5 日涨跌幅 | number | 比率 | 官方契约锚 |
| `change_rate_day10` | 10 日涨跌幅 | number | 比率 | 官方契约锚 |
| `change_rate_day20` | 20 日涨跌幅 | number | 比率 | 官方契约锚 |
| `change_rate_day60` | 60 日涨跌幅 | number | 比率 | 官方契约锚 |
| `change_rate_day120` | 120 日涨跌幅 | number | 比率 | 官方契约锚 |
| `change_rate_ytd` | 年初至今涨跌幅 | number | 比率 | 官方契约锚 |
| `ts_millis` | 交易所行情时间戳 | integer | 毫秒（Unix 时间戳） | 官方契约锚 |

## 观测但未列入返回字段表

| 字段 | 观察 | 状态 | 处理 |
|:--|:--|:--|:--|
| `symbol_id` | 一次成功响应中出现；接口文档将其列为可筛选字段，但没有在返回字段表中定义 | `unverified` | 保留为采集观察字段；不得作为语义锚或据此推断含义 |

## 采集与碰撞路径

- 日常采集器：`scripts/capture_field_probe.py` 的 `ftshare_rest` source，输出 `raw_ftshare_rest.json`。
- 适配器：`stock_common/sc_ftshare.py`；密钥从环境变量 `FTSHARE_API_KEY` 读取，缺省读取被 Git 忽略的 `credentials/ftshare_api_key.txt`。密钥值不得进入报告、日志或原始数据。
- 注册表身份：`FTShare REST`；字段完整路径为原始记录中的字段名，例如 `FTShare REST::close`，运行时字段为 `ftshare_rest.close`。
- 日常碰撞只使用逐字段状态为 `verified` 且 `evidence.basis=official_contract` 的字段作为右侧语义锚。它们不是已确认底层独立来源，不计入独立锚家族覆盖，也不生成普通 `L1` / `L1-U`。
- 旧私有 MCP 字段仍归属历史来源 `FTShare`，采集器已退役；历史身份、缓存和 REST 来源不得合并。
