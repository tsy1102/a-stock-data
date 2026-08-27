# fuyao 同花顺官方金融数据 API —— 全量字段契约镜像（附录）

> 来源: https://fuyao.aicubes.cn/llms-full.txt（官方机器可读契约, 2026-08-22 抓取）
> 仓库: https://github.com/HiThink-Tech/Financial-API （同花顺官方, MIT）
> 用途: 主字典 §12.8.12c 的实证层——**逐端点全量字段表**（请求参数+响应字段+口径注记），无删减。
> 维护: 由 scratch/build_fuyao_appendix.py 从上游契约自动提取；上游升级后重跑即可。
> 盘后可用性: 本服务为 HTTPS REST（非 thsdk TCP 行情网关），**财务/日历/复权/特色池/竞价终态等盘后可查**
> ——thsdk TCP 盘后关闭(-6)时的同花顺层替代通道。


---

## 通用约定（信封/错误码/鉴权）

## 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- 标准 `/api/**` 接口使用请求头 `X-api-key: <your-api-key>`；缺失或无效返回 `code=2001`，无权访问 capability 返回 `code=2003`。Market Dumps 的页面下载按钮使用 `/dump/**` 登录 Cookie 入口，API 客户端使用 `/api/dump/** + X-api-key`。
- 股票、指数和基金标的使用完整 `thscode`（如 `600519.SH`），不接受纯代码 `ticker`（如 `600519`）；基金经理、基金公司详情分别使用 `manager_id`、`company_id`，具体以端点参数表为准。
- 时间戳字段统一为毫秒级 Unix 时间戳（`long`），时区按 `Asia/Shanghai`。
## 响应信封
| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | integer | 业务结果码，`0` 表示成功，非 `0` 表示业务错误。 |
| `message` | string | 结果描述。 |
| `request_id` | string | 请求追踪 ID。 |
| `data` | object \| null | 业务数据容器，按接口而定；错误时固定保留，可能为 `null`。 |
| `data.timestamp` | long | 数据时间戳（毫秒）。 |
| `data.item` | array | 业务数据列表。 |
## 错误码
| code | 含义 | 典型场景 |
|---|---|---|
| `0` | 成功 | - |
| `1001` | 缺少必填参数 | `start` / `end` / `q` / `thscode` 漏传。 |
| `1002` | 参数格式错误 | `thscode` 含逗号，或日期格式错误。 |
| `1003` | 参数取值越界 | 枚举非法、`limit <= 0`，或历史查询窗口超过接口上限。 |
| `1004` | 参数冲突 | `financials` 同时传 `start`/`end` 与 `limit`；仅传 `start` 或仅传 `end`（半开区间）。 |
| `2001` | 未认证 | `X-api-key` 缺失或无效。 |
| `2003` | 权限不足 | API Key 无权调用该 capability。 |
| `3001` | 标的不存在 | 找不到目标标的。 |
| `3002` | 数据未就绪 | 标的存在，但暂无可用业务数据。 |
| `3004` | 标的类型不支持该能力 | 该标的类型不支持所请求的能力。 |
| `4001` | 频率超限 | 超过约定 QPS。 |
| `5001` | 服务内部错误 | 服务端未知错误。 |
| `5002` | 上游服务超时 | 数据源响应超时。 |
| `5003` | 数据源不可用 | 上游服务暂时不可用或返回非 0 状态。 |
## MCP 接入


---

## 价格数据（行情快照/历史K线/全市场导出）

## 价格数据
> A 股行情快照与历史 K 线接口
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- 时间戳字段统一为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
- 价格类字段为原始货币计价，A 股恒为 `CNY`。
:::
## 行情快照
```text
GET /api/a-share/prices/snapshot
**MCP Tool**：[`get_a_share_prices_snapshot`](/docs/mcp/tools/get_a_share_prices_snapshot)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `thscodes` | query | string | 否 | 逗号分隔的 thscode 列表，如 `600519.SH,000001.SZ`。给定时忽略分页参数。 | - |
| `limit` | query | integer | 否 | 分页大小，仅在 `thscodes` 省略时生效。 | `100` |
| `offset` | query | integer | 否 | 分页偏移，仅在 `thscodes` 省略时生效。 | `0` |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long \| null | 数据就绪时间（毫秒），为本次快照中最新的上游有效时间；无有效数据时为 `null`。 |
| `total` | int | 全市场代码表总数（用于分页模式估算页数）。 |
| `item` | array | 快照记录列表，单条记录也以数组返回。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 带交易所后缀的完整 thscode，如 `600519.SH`。 |
| `ticker` | string | 纯代码（无交易所后缀），如 `600519`。 |
| `last_price` | number | 最新成交价（原始货币）。 |
| `price_change` | number | 相对前收盘价的涨跌额（原始货币）。 |
| `price_change_ratio_pct` | number | 涨跌幅，单位为百分比数值（如 `1.74` 表示 +1.74%）。 |
| `open_price` | number | 当日开盘价。 |
| `high_price` | number | 当日最高价。 |
| `low_price` | number | 当日最低价。 |
| `prev_price` | number | 前收盘价。 |
| `volume` | number | 成交量（股）。 |
| `turnover` | number | 成交额（原始货币）。 |
:::note 中文名解析
快照响应不返回标的中文名 `name`。如需展示中文名，请配合 [`/api/meta/tickers/search`](./ticker-search.mdx) 或 [`/api/meta/tickers/list`](./ticker-list.mdx) 解析。
:::
## 历史 K 线
```text
GET /api/a-share/prices/historical
**MCP Tool**：[`get_a_share_prices_historical`](/docs/mcp/tools/get_a_share_prices_historical)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `thscode` | query | string | 是 | 单只标的 thscode，**不接受逗号**。多标的请分多次请求。 | - |
| `interval` | query | string | 是 | K 线周期，**当前仅支持** `1d`(日线)。 | `1d` |
| `start` | query | long | 是 | 起始时间，毫秒 Unix 时间戳。缺失返回 `code=1001`。 | - |
| `end` | query | long | 是 | 结束时间，毫秒 Unix 时间戳。`end - start` 超过 10 年返回 `code=1003`。 | - |
| `adjust` | query | string | 否 | 复权方式：`none` / `forward`(前复权) / `backward`(后复权)。 | `forward` |
| `offset` | query | integer | 否 | 分页偏移。 | `0` |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 数据就绪时间（毫秒），为序列中最新一根 K 线的上游有效时间。 |
| `item` | array | K 线列表。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `date_ms` | long | K 线日期（毫秒）。 |
| `open_price` | number | 开盘价。 |
| `high_price` | number | 最高价。 |
| `low_price` | number | 最低价。 |
| `close_price` | number | 收盘价。 |
| `volume` | number | 成交量（股）。 |
| `turnover` | number | 成交额（原始货币）。 |
## 全市场数据导出
> A 股全市场 10 年日 K、最近 10 交易日日 K 与复权因子 Parquet 文件下载
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- 本页下载按钮使用登录态 Cookie 调用接口；登录入口见 [API Key 管理](/admin)。
- 下载接口返回短时有效的 S3 预签名链接，不能将链接本身作为长期数据地址。
- Parquet 中的日期时间字段为毫秒级 Unix 时间戳，交易日期按 `Asia/Shanghai` 解释；A 股价格按原始货币计价，币种为 `CNY`。
:::
## 一键获取下载链接
:::caution 过期处理
预签名链接的有效期非常短（通常 5 分钟），不要持久化或缓存。需要长期使用时，应在每次下载前重新点击「获取下载链接」。
:::
## Parquet 文件结构
| dump 名 | dump_id | data_type | mode | 默认窗口 | 触发 profile overlay | 下载端点 |
|---|---|---|---|---|---|---|
| 10 年全量日 K | `a_share_daily_k_1d_none_10y` | `daily_k` | `FULL` | `years=10` | base profile 默认 | `GET /dump/market-dumps/daily-k/download-url` |
| 最近 10 交易日日 K | `a_share_daily_k_1d_none_10d` | `daily_k` | `RECENT_TRADING_DAYS` | `trading_days=10` | `dump-builder-daily-k-10d` | `GET /dump/market-dumps/daily-k-10d/download-url` |
| 复权因子全量 | `a_share_adjustment_factors_event_none_all` | `adjustment_factors` | `FULL` | 全量事件 | `dump-builder-adjustment-factors` | `GET /dump/market-dumps/adjustment-factors/download-url` |
| dump | dump_id | 主键 | 时间字段 |
|---|---|---|---|
| 10 年全量日 K | `a_share_daily_k_1d_none_10y` | `(thscode, date_ms)` | `date_ms` |
| 最近 10 交易日日 K | `a_share_daily_k_1d_none_10d` | `(thscode, date_ms)` | `date_ms` |
| 复权因子 | `a_share_adjustment_factors_event_none_all` | `(thscode, ex_date_ms)` | `ex_date_ms` |
### 日 K 列
| 列 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 带交易所后缀的完整代码。 |
| `currency` | string | 币种代码，A 股为 `CNY`。 |
| `interval` | string | 周期代码，固定为 `1d`。 |
| `adjusted` | string | 复权方式，固定为 `none`（未复权）。 |
| `date_ms` | long | K 线日期（毫秒，`Asia/Shanghai` 零点）。 |
| `open_price` / `high_price` / `low_price` / `close_price` | number | OHLC，原始货币计价。 |
| `volume` | number | 成交量（股）。 |
| `turnover` | number | 成交额（原始货币）。 |
### 复权因子列
| 列 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 带交易所后缀的完整代码。 |
| `ticker` | string | 展示用代码。 |
| `ex_date_ms` | long | 除权除息日（毫秒，`Asia/Shanghai` 零点）。 |
| `dividend_per_share` | number | 每股现金分红（税前）。 |
| `per_share_bonus` | number | 每股送股比例。 |
| `allotment_ratio` | number | 配股比例。 |
| `allotment_price` | number | 配股价格（原始货币）。 |
| `currency` | string | 币种代码，A 股为 `CNY`。 |
## 解读脚本示例


---

## 标的目录（检索/列表）

## 标的检索
> 按 thscode / ticker / 名称检索 A 股、指数与基金标的
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- 时间戳字段统一为毫秒级 Unix 时间戳。
:::
```text
GET /api/meta/tickers/search
**MCP Tool**：[`get_meta_tickers_search`](/docs/mcp/tools/get_meta_tickers_search)
## 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `q` | query | string | 是 | 搜索关键词：完整 thscode、ticker 代码或中英文名称（支持子串匹配）。 | - |
| `exchange` | query | string | 否 | 交易所过滤：`SH` / `SZ` / `BJ`；场外基金不参与该过滤。 | - |
| `asset_type` | query | string | 否 | 规范化资产类型，支持单值或逗号分隔多值；完整枚举见下方。 | - |
| `limit` | query | integer | 否 | 返回上限，最大 `50`。 | `10` |
| `asset_type` | 含义 |
|---|---|
| `a-share` | A 股股票 |
| `a-share-index` | A 股指数、同花顺指数或板块 |
| `fund-otc` | 场外公募基金 |
| `fund-etf` | ETF 基金 |
| `fund-lof` | LOF 基金 |
## 请求示例
## 响应示例
## 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 数据就绪时间（毫秒），为当前代码表快照的上游加载时间。 |
| `item` | array | 标的列表。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 完整 thscode，如 `600519.SH`。 |
| `ticker` | string | 纯代码，如 `600519`。 |
| `name` | string | 展示名称。 |
| `exchange` | string \| null | 交易所后缀（`SH` / `SZ` / `BJ`）；场外基金为 `null`，`.OF` 不是交易所。 |
| `asset_type` | string | 规范化资产类型；每条记录仅返回一个叶子类型，含义同请求参数枚举表。 |
| `currency` | string | 币种代码；当前基金统一为 `CNY`。 |


---

## 除复权（公司行动/复权因子）

## 除复权
> A 股复权因子事件流（分红 / 送股 / 配股）
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- 请求参数 `from` / `to` 使用 `YYYY-MM-DD` 字符串；响应中的事件日期为毫秒 Unix 时间戳 `ex_date_ms`。
:::
## 复权因子事件流
```text
GET /api/a-share/corporate-actions/adjustment-factors
**MCP Tool**：[`get_a_share_corporate_actions_adjustment_factors`](/docs/mcp/tools/get_a_share_corporate_actions_adjustment_factors)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `thscode` | query | string | 是 | 单只标的 thscode，**不接受逗号**。 | - |
| `from` | query | string | 否 | 事件起始日，格式 `YYYY-MM-DD`。 | - |
| `to` | query | string | 否 | 事件截止日，格式 `YYYY-MM-DD`。 | - |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 带交易所后缀的完整 thscode（与 `item` 同级，标识本次返回所属标的）。 |
| `ticker` | string | 纯代码（无交易所后缀）。 |
| `item` | array | 事件列表，按 `ex_date_ms` 降序排列（最新在前）。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `ticker` | string | 纯代码（无交易所后缀），如 `600519`。 |
| `ex_date_ms` | long | 除权除息日，Asia/Shanghai 00:00:00 毫秒 Unix 时间戳。 |
| `dividend_per_share` | number | 每股现金分红（税前，原始货币）。非现金事件为 `0`。 |
| `per_share_bonus` | number | 每股送股比例（如 `0.1` 表示 10 送 1）。纯现金分红事件为 `0`。 |
:::note 字段约定差异
- 响应中**不返回** `event_type` / `record_date` / `adjust_factor`，事件类型由 `dividend_per_share` 与 `per_share_bonus` 两个数值字段隐式区分。
- 复权因子需调用方按 `dividend_per_share` + `per_share_bonus` 自行推导；若仅需复权后价格，直接调用 [`/api/a-share/prices/historical`](./prices.mdx#历史-k-线) 并传 `adjust=forward|backward`。
:::


---

## 财务报表（利润表/资产负债表/现金流量表）

## 财务报表
> A 股整体合并利润表 / 资产负债表 / 现金流量表多期序列
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- 时间戳字段统一为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
- 所有金额字段单位为**原币元**，`basic_eps` 单位为**元/股**（量级远小于金额字段，不可做单位换算）；A 股币种恒为 `CNY`。
- 字段为 `null` 表示「该期未披露」，透传不补零。
:::
## 取数模式
| 模式 | 触发条件 | 行为 |
|---|---|---|
| 最近 N 期 | 不传 `start` / `end` | 返回最近 `limit` 期，按 `period_end` 降序。 |
| 时间区间 | 同时传 `start` + `end`（毫秒戳） | 返回 `[start, end]` 闭区间内全部报告期，按 `period_end` 降序。 |
## 共有请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `thscode` | query | string | 是 | 单只标的 thscode，**不接受逗号**；含交易所后缀（如 `600519.SH` / `000858.SZ` / `430047.BJ`）。 | - |
| `period` | query | enum | 是 | 报告期类型：`annual`(仅 Q4 报告期) / `quarterly`(每个季度末)。 | `annual` |
| `limit` | query | integer | 否 | 最近 N 期模式：默认 4，范围 `[1, 20]`。**与 `start`/`end` 互斥**。 | `4` |
| `start` | query | long | 否 | 时间区间模式：起始毫秒戳，需与 `end` 同传；窗口跨度不超过 10 年。 | - |
| `end` | query | long | 否 | 时间区间模式：结束毫秒戳，`end >= start`。 | - |
## 共有响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 带交易所后缀的完整 thscode。 |
| `ticker` | string | 纯代码（不含后缀）。 |
| `period` | enum | 入参 `period` 回显。 |
| `fiscal_year` | int | 财年（自然年）。 |
| `fiscal_period` | string | `FY` / `Q1` / `Q2` / `Q3` / `Q4`。 |
| `report_date_ms` | long | 披露日（毫秒）。 |
| `period_end_ms` | long | 报告期末（Asia/Shanghai 零点毫秒戳）。 |
| `currency` | string | 币种，A 股恒为 `CNY`。 |
## 利润表
```text
GET /api/a-share/financials/income-statements
**MCP Tool**：[`get_a_share_financials_income_statements`](/docs/mcp/tools/get_a_share_financials_income_statements)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `thscode` | string | 是 | — | 单只标的 thscode，不接受逗号；含交易所后缀。 |
| `period` | enum | 是 | `annual` | `annual`（仅 Q4 报告期）/ `quarterly`（每个季度末）。 |
| `limit` | integer | 否 | `4` | 最近 N 期模式，范围 `[1, 20]`；与 `start` / `end` 互斥。 |
| `start` | long | 否 | — | 时间区间模式起始毫秒戳，需与 `end` 同传。 |
| `end` | long | 否 | — | 时间区间模式结束毫秒戳，需满足 `end >= start`。 |
### 返回字段 {#income-statements-return-fields}
| 字段 | 类型 | 说明 |
|---|---|---|
| `operating_income` | number | 营业收入（原币元）。 |
| `operating_costs` | number | 营业成本（原币元）。 |
| `operating_expenses` | number | 营业总成本（原币元）。 |
| `sales_fee` | number | 销售费用（原币元）。 |
| `manage_fee` | number | 管理费用（原币元）。 |
| `research_and_development_expenses` | number | 研发费用（原币元）。 |
| `operating_profit` | number | 营业利润（原币元）。 |
| `interest_expenses` | number | 利息费用（原币元）。 |
| `profit_total` | number | 利润总额（原币元）。 |
| `income_tax_expense` | number | 所得税费用（原币元）。 |
| `net_profit` | number | 净利润（原币元）。 |
| `parent_holder_net_profit` | number | 归属于母公司股东的净利润（原币元）。 |
| `basic_eps` | number | 基本每股收益（元/股）。 |
## 资产负债表
```text
GET /api/a-share/financials/balance-sheets
**MCP Tool**：[`get_a_share_financials_balance_sheets`](/docs/mcp/tools/get_a_share_financials_balance_sheets)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `thscode` | string | 是 | — | 单只标的 thscode，不接受逗号；含交易所后缀。 |
| `period` | enum | 是 | `annual` | `annual`（仅 Q4 报告期）/ `quarterly`（每个季度末）。 |
| `limit` | integer | 否 | `4` | 最近 N 期模式，范围 `[1, 20]`；与 `start` / `end` 互斥。 |
| `start` | long | 否 | — | 时间区间模式起始毫秒戳，需与 `end` 同传。 |
| `end` | long | 否 | — | 时间区间模式结束毫秒戳，需满足 `end >= start`。 |
### 返回字段 {#balance-sheets-return-fields}
| 字段 | 类型 | 说明 |
|---|---|---|
| `assets_total` | number | 资产总计（原币元）。 |
| `total_current_assets` | number | 流动资产合计（原币元）。 |
| `non_current_nets_total` | number | 非流动资产合计（原币元）。 |
| `cash` | number | 货币资金（原币元）。 |
| `accounts_receivable` | number | 应收账款（原币元）。 |
| `total_debt` | number | 负债合计（原币元）。 |
| `holder_equity_total` | number | 所有者权益（股东权益）合计（原币元）。 |
## 现金流量表
```text
GET /api/a-share/financials/cash-flow-statements
**MCP Tool**：[`get_a_share_financials_cash_flow_statements`](/docs/mcp/tools/get_a_share_financials_cash_flow_statements)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `thscode` | string | 是 | — | 单只标的 thscode，不接受逗号；含交易所后缀。 |
| `period` | enum | 是 | `annual` | `annual`（仅 Q4 报告期）/ `quarterly`（每个季度末）。 |
| `limit` | integer | 否 | `4` | 最近 N 期模式，范围 `[1, 20]`；与 `start` / `end` 互斥。 |
| `start` | long | 否 | — | 时间区间模式起始毫秒戳，需与 `end` 同传。 |
| `end` | long | 否 | — | 时间区间模式结束毫秒戳，需满足 `end >= start`。 |
### 返回字段 {#cash-flow-statements-return-fields}
| 字段 | 类型 | 说明 |
|---|---|---|
| `act_cash_flow_net` | number | 经营活动产生的现金流量净额（原币元）。 |
| `invest_cash_flow_net` | number | 投资活动产生的现金流量净额（原币元）。 |
| `financing_cash_flow_net` | number | 筹资活动产生的现金流量净额（原币元）。 |
| `pay_fixed_assets_etc_cash` | number | 购建固定资产、无形资产和其他长期资产支付的现金（原币元）。 |
| `pay_dividends_profits_interest_cash` | number | 分配股利、利润或偿付利息支付的现金（原币元）。 |
| `cash_equivalents_net_addition` | number | 现金及现金等价物净增加额（原币元）。 |


---

## 交易日历

## 交易日历
> A 股近一年交易日序列
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- 信封 `data.timestamp` 为毫秒级 Unix 时间戳；`item` 内同时返回毫秒戳 `date_ms` 与可读日期 `date`（`yyyyMMdd`），时区按 `Asia/Shanghai`。
:::
## 交易日序列
```text
GET /api/a-share/calendar/trading-days
**MCP Tool**：[`get_a_share_calendar_trading_days`](/docs/mcp/tools/get_a_share_calendar_trading_days)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| - | - | - | - | 无入参。 | - |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 数据就绪时间（毫秒）。 |
| `item` | array | 交易日列表，按时间升序。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `date_ms` | long | 单个交易日的 Asia/Shanghai 00:00:00 毫秒戳。 |
| `date` | string | 同一交易日的 `yyyyMMdd` 格式（Asia/Shanghai），方便直接展示 / 对账。 |


---

## 指数与板块（同花顺指数体系）

## 指数数据
> 同花顺指数 / 板块的列表、成分股、行情快照与历史 K 线
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- `thscode` 入参均会被 `trim().toUpperCase()` 标准化，**不接受逗号**，单次仅支持一个指数。
- 指数行情覆盖上证交易所指数（如 `000001.SH`）、深证交易所指数（如 `399001.SZ`）、同花顺板块（如 `886042.TI`）与同花顺行业指数（如 `881101.TI`）。
:::
## 同花顺指数列表
```text
GET /api/a-share-index/catalog/ths-index-list
**MCP Tool**：[`get_a_share_index_catalog_ths_index_list`](/docs/mcp/tools/get_a_share_index_catalog_ths_index_list)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `tag` | query | string | 否 | 标签白名单：`cn_concept`(A 股概念) / `region`(区域指数) / `tszs`(特色指数) / `industry`(行业指数)。大小写不敏感。 | `cn_concept` |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 数据时间戳（毫秒）。 |
| `item[].thscode` | string | 同花顺指数的完整 thscode，如 `886042.TI`。 |
| `item[].name` | string | 同花顺指数展示名称。 |
> 指数维度不暴露纯代码 `ticker`。
## 同花顺指数成分股
```text
GET /api/a-share-index/constituents/ths-stock-list
**MCP Tool**：[`get_a_share_index_constituents_ths_stock_list`](/docs/mcp/tools/get_a_share_index_constituents_ths_stock_list)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `thscode` | query | string | 是 | 指数 thscode，形如 `{ticker}.{suffix}`。入参会被 `trim().toUpperCase()` 标准化；**不接受逗号**，单次仅支持一个指数。 | - |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 数据时间戳（毫秒）。 |
| `item[].thscode` | string | 成分股完整 thscode。 |
| `item[].ticker` | string | 成分股纯代码。 |
| `item[].name` | string | 成分股展示名称。 |
## 指数行情快照
```text
GET /api/a-share-index/prices/snapshot
**MCP Tool**：[`get_a_share_index_prices_snapshot`](/docs/mcp/tools/get_a_share_index_prices_snapshot)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `thscodes` | query | string | 是 | 逗号分隔的指数 thscode 列表，如 `000001.SH,399001.SZ,886042.TI,881101.TI`。 | - |
| `limit` | query | integer | 否 | 与 A 股行情快照签名对齐，对本接口无效。 | - |
| `offset` | query | integer | 否 | 与 A 股行情快照签名对齐，对本接口无效。 | - |
### 响应字段
## 指数历史 K 线
```text
GET /api/a-share-index/prices/historical
**MCP Tool**：[`get_a_share_index_prices_historical`](/docs/mcp/tools/get_a_share_index_prices_historical)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `thscode` | query | string | 是 | 单只指数 thscode，**不接受逗号**。 | - |
| `interval` | query | string | 是 | K 线周期，当前仅支持 `1d`（日线）。 | `1d` |
| `start` | query | long | 是 | 起始时间，毫秒 Unix 时间戳。 | - |
| `end` | query | long | 是 | 结束时间，毫秒 Unix 时间戳。`end - start` 超过 10 年返回 `code=1003`。 | - |
### 响应字段


---

## 个股异动原因

## 特色数据
> A 股特色数据：涨跌停与炸板数据、同花顺热榜、个股异动原因与龙虎榜
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- 时间戳字段为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
:::
## 文档分组
| 分组 | 覆盖接口 | 说明 |
|---|---|---|
| [涨跌停与炸板数据](./limit-up-data.mdx) | `limit-up-pool` / `limit-down-pool` / `limit-break-pool` / `limit-up-ladder` | 涨停、跌停、炸板股票池与连板天梯。 |
| [同花顺热榜](./hot-list-data.mdx) | `skyrocket-list` / `hot-stock-list` / `hot-stock-list-history` / `hot-stock-rank-trend` | 热度榜单、历史热股排行与个股排名走势。 |
| [个股异动原因](./anomaly-analysis.mdx) | `anomaly-analysis-list` / `anomaly-analysis-stock` | 当日个股异动原因列表与按股票批量查询。 |
| [龙虎榜数据](./dragon-tiger-data.mdx) | `dragon-tiger-list` | 按交易日返回全部、机构榜或游资榜。 |
## 接口列表
| API | 方法与路径 | 说明 | MCP |
|---|---|---|---|
| [涨停股票池](./limit-up-data.mdx#涨停股票池) | `GET /api/a-share/special-data/limit-up-pool` | 按交易日返回 A 股涨停 / 连板股票池。 | [`get_a_share_special_data_limit_up_pool`](/docs/mcp/tools/get_a_share_special_data_limit_up_pool) |
| [跌停股票池](./limit-up-data.mdx#跌停股票池) | `GET /api/a-share/special-data/limit-down-pool` | 按交易日返回 A 股跌停股票池。 | [`get_a_share_special_data_limit_down_pool`](/docs/mcp/tools/get_a_share_special_data_limit_down_pool) |
| [炸板股票池](./limit-up-data.mdx#炸板股票池) | `GET /api/a-share/special-data/limit-break-pool` | 按交易日返回 A 股涨停炸板股票池。 | [`get_a_share_special_data_limit_break_pool`](/docs/mcp/tools/get_a_share_special_data_limit_break_pool) |
| [连板天梯](./limit-up-data.mdx#连板天梯) | `GET /api/a-share/special-data/limit-up-ladder` | 返回近 30 个交易日的连板梯队矩阵。 | [`get_a_share_special_data_limit_up_ladder`](/docs/mcp/tools/get_a_share_special_data_limit_up_ladder) |
| [飙升榜](./hot-list-data.mdx#飙升榜) | `GET /api/a-share/special-data/skyrocket-list` | 查询 A 股热度排名飙升榜 Top30，支持日榜与小时榜。 | [`get_a_share_special_data_skyrocket_list`](/docs/mcp/tools/get_a_share_special_data_skyrocket_list) |
| [A股热股榜单](./hot-list-data.mdx#a股热股榜单) | `GET /api/a-share/special-data/hot-stock-list` | 查询 A 股热股榜单 Top30，支持 24 小时级别与小时级别。 | [`get_a_share_special_data_hot_stock_list`](/docs/mcp/tools/get_a_share_special_data_hot_stock_list) |
| [历史热股排行](./hot-list-data.mdx#历史热股排行) | `GET /api/a-share/special-data/hot-stock-list-history` | 按自然日返回历史热股榜排行。 | [`get_a_share_special_data_hot_stock_list_history`](/docs/mcp/tools/get_a_share_special_data_hot_stock_list_history) |
| [个股排名走势](./hot-list-data.mdx#个股排名走势) | `GET /api/a-share/special-data/hot-stock-rank-trend` | 查询单只 A 股一段时间内的热榜排名走势。 | [`get_a_share_special_data_hot_stock_rank_trend`](/docs/mcp/tools/get_a_share_special_data_hot_stock_rank_trend) |
| [个股异动原因列表](./anomaly-analysis.mdx#个股异动原因列表) | `GET /api/a-share/special-data/anomaly-analysis-list` | 查询当日个股异动原因，可选按异动标签过滤。 | 不提供 MCP |
| [按股票查询个股异动原因](./anomaly-analysis.mdx#按股票查询个股异动原因) | `GET /api/a-share/special-data/anomaly-analysis-stock` | 按同花顺代码批量查询当日个股异动原因。 | [`get_a_share_special_data_anomaly_analysis_stock`](/docs/mcp/tools/get_a_share_special_data_anomaly_analysis_stock) |
| [龙虎榜榜单](./dragon-tiger-data.mdx#龙虎榜榜单) | `GET /api/a-share/special-data/dragon-tiger-list` | 按交易日返回全部、机构榜或游资榜。 | [`get_a_share_special_data_dragon_tiger_list`](/docs/mcp/tools/get_a_share_special_data_dragon_tiger_list) |
## 个股异动原因
> A 股个股异动原因列表与按股票查询能力
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- 时间戳字段为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
:::
## 接口列表
| API | 方法与路径 | 说明 | MCP |
|---|---|---|---|
| 个股异动原因列表 | `GET /api/a-share/special-data/anomaly-analysis-list` | 查询当日个股异动原因，可选按异动标签过滤。 | 不提供 MCP |
| 按股票查询个股异动原因 | `GET /api/a-share/special-data/anomaly-analysis-stock` | 按同花顺代码批量查询当日个股异动原因。 | [`get_a_share_special_data_anomaly_analysis_stock`](/docs/mcp/tools/get_a_share_special_data_anomaly_analysis_stock) |
## 个股异动原因列表
```text
GET /api/a-share/special-data/anomaly-analysis-list
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `tag_codes` | query | string | 否 | 异动标签，逗号分隔，多个值为 OR 关系；大小写不敏感，重复值自动去重。合法值见下方标签表。 | - |
| 值 | 含义 |
|---|---|
| `LIMIT_UP` | 涨停 |
| `LIMIT_DOWN` | 跌停 |
| `SHARP_RISE` | 大涨 |
| `SHARP_FALL` | 大跌 |
| `RAPID_RALLY` | 快速拉升 |
| `RAPID_DECLINE` | 快速下挫 |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 数据时间戳，毫秒级 Unix 时间戳。 |
| `item` | array | 个股异动原因列表。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `stock_name` | string | 股票名称。 |
| `analysis_content` | string | 异动解读内容。 |
| `keyword_list` | string[] | 关键词列表；无关键词时返回空数组。 |
| `thscode` | string | 带交易所后缀的同花顺代码，例如 `600519.SH`。 |
| `tag_name` | string | 异动标签展示名。 |
### 约束与错误
- `tag_codes` 中出现未知值、连续逗号或尾逗号导致的空 token 时返回 `code=1002`。
- 当日数据暂不可用时返回 `code=3002`。
- 有快照但查询无匹配时返回 `code=0`，且 `item=[]`。
## 按股票查询个股异动原因
```text
GET /api/a-share/special-data/anomaly-analysis-stock
**MCP Tool**：[`get_a_share_special_data_anomaly_analysis_stock`](/docs/mcp/tools/get_a_share_special_data_anomaly_analysis_stock)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `thscodes` | query | string | 是 | 逗号分隔的同花顺代码列表，支持 `SH` / `SZ` / `BJ` 后缀，大小写不敏感；去重前最多 50 个 token。 | - |
### 响应字段
### 约束与错误
- 缺失或空白 `thscodes` 返回 `code=1001`。
- `thscodes` 出现空 token 或不符合 `000001.SZ` / `600519.SH` / `430001.BJ` 这类格式时返回 `code=1002`。
- 去重前 token 数超过 50 时返回 `code=1003`。
- 当日数据暂不可用时返回 `code=3002`。
- 有快照但查询无匹配时返回 `code=0`，且 `item=[]`。


---

## 集合竞价数据（竞价快照/短线风向标基准）

## 集合竞价数据
> 查询 A 股集合竞价快照与短线风向标竞价基准
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`；认证与权限错误通过业务 `code` 表达。
- 所有接口返回统一 `ApiResponse` 信封，业务结果通过 `code` 表达。
- A 股标的使用带交易所后缀的完整 `thscode`；时间戳均为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
:::
## A股集合竞价快照
```text
GET /api/a-share/auction/snapshot
**MCP Tool**：[`get_a_share_auction_snapshot`](/docs/mcp/tools/get_a_share_auction_snapshot)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `thscodes` | string | 是 | — | 一个或多个 A 股 thscode，使用英文逗号分隔；服务端按请求顺序去重返回。 |
| `stage` | enum | 否 | `final` | `live`（实时阶段）或 `final`（终态）。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `data.timestamp` | long | 接口响应组装时间，毫秒 Unix 时间戳；实时、终态、停牌及 `not_ready` 场景均会返回。上游竞价行情时间仅用于判断数据新鲜度。 |
| `data.auction_phase` | string | 集合竞价阶段。 |
| `data.data_status` | string | 数据状态。 |
| `data.total` | integer | 返回标的数量。 |
| `data.item` | array | 集合竞价明细列表。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` / `ticker` / `name` | string | 标准代码、纯代码与股票简称。 |
| `auction_price` / `auction_pct` | number | 竞价价格与竞价涨跌幅百分数原值。 |
| `auction_volume` / `auction_amount` / `auction_unmatched` | number | 竞价成交量、成交额与未匹配量。 |
| `auction_turnover_pct` / `auction_yesterday_ratio_pct` / `auction_volume_ratio` | number | 竞价换手率、相对昨日成交量比例与竞价量比。 |
| `pre_close_price` / `open_price` / `last_price` | number | 前收盘价、开盘价与最新价。 |
| `float_market_cap` | number | 流通市值。 |
## 短线风向标竞价基准
```text
GET /api/a-share/auction/short-term-benchmark
**MCP Tool**：[`get_a_share_auction_short_term_benchmark`](/docs/mcp/tools/get_a_share_auction_short_term_benchmark)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `date` | string | 否 | 上海时区当日 | 查询日期，格式 `yyyy-MM-dd`；缺失或传入空字符串时使用 `Asia/Shanghai` 当日，显式指定非交易日时不自动回退。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 接口响应组装时间，毫秒 Unix 时间戳。 |
| `date` | string | 最终查询日期，格式 `yyyy-MM-dd`。 |
| `date_ms` | long | 最终查询日期在 `Asia/Shanghai` 当日零点的毫秒 Unix 时间戳。 |
| `item` | array | 短线风向标竞价基准明细。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 完整 A 股 thscode。 |
| `ticker` | string | 纯股票代码。 |
| `name` | string | 股票简称。 |
| `auction_pct` | number | 集合竞价涨跌幅，百分数原值。 |
| `tags` | array | 短线风向标标签。 |


---

## 龙虎榜

## 龙虎榜数据
> A 股龙虎榜榜单，覆盖全部、机构榜与游资榜
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- 时间戳字段为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
:::
## 接口列表
| API | 方法与路径 | 说明 | MCP |
|---|---|---|---|
| 龙虎榜榜单 | `GET /api/a-share/special-data/dragon-tiger-list` | 按交易日返回全部、机构榜或游资榜。 | [`get_a_share_special_data_dragon_tiger_list`](/docs/mcp/tools/get_a_share_special_data_dragon_tiger_list) |
## 龙虎榜榜单
```text
GET /api/a-share/special-data/dragon-tiger-list
**MCP Tool**：[`get_a_share_special_data_dragon_tiger_list`](/docs/mcp/tools/get_a_share_special_data_dragon_tiger_list)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `board_type` | query | enum | 否 | 榜单类型：`all` 全部 / `org` 机构榜 / `hot_money` 游资榜。 | `all` |
| `date` | query | string | 否 | 目标交易日，格式 `yyyy-MM-dd`；只支持一年内数据。显式传入非交易日返回 `code=1002`。 | 最近可用交易日 |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 目标交易日 `Asia/Shanghai` 00:00 毫秒时间戳。 |
| `board_type` | string | 实际榜单类型：`all` / `org` / `hot_money`。 |
| `trade_date` | string | 实际查询交易日，格式 `yyyy-MM-dd`。 |
| `count` | integer | 上游记录数；同一股票可能同时出现当日榜和 3 日榜。 |
| `stock_count` | integer | 股票去重数量。 |
| `stock_items` | array | 股票维度榜单；`board_type=all/org` 时填充，`hot_money` 时为空数组。 |
| `hot_money_items` | array | 游资维度聚合榜单；`board_type=hot_money` 时填充，普通榜单时为空数组。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 带交易所后缀的标准代码，例如 `002407.SZ`。 |
| `ticker` | string | 6 位股票代码。 |
| `name` | string | 股票简称。 |
| `concept_list` | array | 所属概念列表，元素包含 `name`。 |
| `change` | number | 当日涨跌幅，小数形式。 |
| `net_value` | number | 龙虎榜净买入金额，单位元。 |
| `net_rate` | number | 龙虎榜净买入占比，小数形式。 |
| `hot_rank` | integer | 同花顺人气排名，数值越小越靠前。 |
| `buy_value` | number | 买方金额，单位元。 |
| `sell_value` | number | 卖方金额，单位元。 |
| `limit_reason` | string | 涨跌停原因。 |
| `range_days` | integer | 上榜区间天数，`1` 为当日榜，`3` 为 3 日榜。 |
| `org_net_value` | number | 机构净买入金额，单位元。 |
| `org_net_rate` | number | 机构净买入占比，小数形式。 |
| `org_buy_num` | integer | 买入机构数。 |
| `org_sell_num` | integer | 卖出机构数。 |
| `amount` | number | 成交金额，单位元。 |
| `hot_money_net_value` | number | 股票维度游资合计净买入金额，单位元。 |
| `hot_money_net_rate` | number | 股票维度游资合计净买入占比，小数形式。 |
| `hot_money_item_net_value` | number | 该游资在该股上的净买入金额，单位元。 |
| `hot_money_item_net_rate` | number | 该游资在该股上的净买入占比，小数形式。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | string | 游资名称。 |
| `buying` | number | 聚合净买入金额，单位元。 |
| `rows` | array | 该游资关联股票列表，字段同 `stock_items[]`。 |
### 约束与错误
- `board_type` 仅接受 `all` / `org` / `hot_money`，否则返回 `code=1002`。
- `date` 必须为 `yyyy-MM-dd`，否则返回 `code=1002`。
- 显式传入的 `date` 必须是 A 股交易日，否则返回 `code=1002`。
- `date` 不在一年内，或日期晚于今天时返回 `code=1003`。


---

## 财务指标（五类能力）

## 财务指标数据
> A 股财务指标数据，一次返回成长、盈利、偿债、营运、现金流五类指标
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- `report` 格式为 `yyyy-1`、`yyyy-2`、`yyyy-3`、`yyyy-4`，其中 `1` 一季报、`2` 中报、`3` 三季报、`4` 年报。
- 指标项包含 `index_id` / `value`。`index_id` 使用下方表格列出的接口契约字段名，`value` 为数据源原始数值字符串；上游缺失时返回 `null`。
:::
## 接口
| REST 端点 | MCP Tool | 说明 |
|---|---|---|
| `GET /api/a-share/financials/indicators` | [`get_a_share_financials_indicators`](/docs/mcp/tools/get_a_share_financials_indicators) | 财务指标数据 |
## 财务指标数据
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `thscode` | string | 是 | — | 单只标的 thscode，含交易所后缀，如 `300033.SZ`。 |
| `report` | string | 是 | — | 报告期，示例 `2025-1`；格式见上方通用约定。 |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | integer | 业务状态码，`0` 表示成功。 |
| `message` | string | 业务状态说明。 |
| `request_id` | string | 请求追踪 ID。 |
| `data.thscode` | string | 入参 thscode 回显。 |
| `data.report` | string | 入参 report 回显。 |
| `data.abilities[]` | array | 五类能力块，固定顺序为 `growth`、`profitability`、`solvency`、`operation`、`cash-flow`。 |
| `data.abilities[].ability` | string | 能力标识。 |
| `data.abilities[].indicators[]` | array | 当前能力下的指标列表。 |
| `data.abilities[].indicators[].index_id` | string | 指标 ID，取值见下方表格。 |
| `data.abilities[].indicators[].value` | string \| null | 本期指标值。服务端保留数据源原始数值字符串，不承诺固定小数位；上游空值或缺失值标准化为 `null`。百分比类指标按百分数值表达，例如 `89.12000000` 表示 `89.12%`；周转率、比率、倍数类指标按指标名称对应单位解释。 |
:::note 数值口径
`value` 暂不转为 JSON number，是为了保留数据源精度和尾随小数位。调用方展示时应按 `index_id` 识别单位：名称含“增长率”“毛利率”“净利率”“收益率”“资产负债率”“现金比率”等的指标按百分比展示；“周转率”通常按次展示；“已获利息倍数”按倍展示；缺失值展示为 `--` 或空值。
:::
### 指标字段
#### 成长能力 `growth`
| `index_id` | 指标名称 |
|---|---|
| `total_assets_growth_ratio` | 总资产增长率 |
| `net_profit_yoy_growth_ratio` | 净利润同比增长率 |
| `operating_income_yoy_growth_ratio` | 营业收入同比增长率 |
| `operating_profit_yoy_growth_ratio` | 营业利润同比增长率 |
#### 盈利能力 `profitability`
| `index_id` | 指标名称 |
|---|---|
| `sale_gross_margin` | 销售毛利率 |
| `sale_net_interest_ratio` | 销售净利率 |
| `total_assets_net_ratio` | 总资产收益率 |
| `index_deduct_weighted_avg_roe` | 扣非加权净资产收益率 |
| `index_weighted_avg_roe` | 净资产收益率 |
#### 偿债能力 `solvency`
| `index_id` | 指标名称 |
|---|---|
| `current_ratio` | 流动比率 |
| `quick_ratio` | 速动比率 |
| `assets_debt_ratio` | 资产负债率 |
| `cash_ratio` | 现金比率 |
| `earned_interest_multiple` | 已获利息倍数 |
#### 营运能力 `operation`
| `index_id` | 指标名称 |
|---|---|
| `long_term_debt_equity_ratio` | 长期负债权益比率 |
| `total_assets_turnover_ratio` | 总资产周转率 |
| `inventory_turnover_ratio` | 存货周转率 |
| `current_assets_turnover_ratio` | 流动资产周转率 |
| `receive_account_turnover_ratio` | 应收账款周转率 |
#### 现金流 `cash-flow`
| `index_id` | 指标名称 |
|---|---|
| `cash_operating_index` | 现金营运指数 |
| `operating_cash_flow_net_divide_income` | 销售现金比率 |
| `net_profit_cash_content` | 净利润现金含量 |
| `operating_cash_net_yoy_growth_ratio` | 现金流量净额增长率 |
| `cash_meet_invest_ratio` | 现金满足投资比率 |
### 错误与约束
| 场景 | `code` | 说明 |
|---|---|---|
| 缺少 `thscode` 或 `report` | `1001` | 必填参数缺失。 |
| `report` 格式非法 | `1002` | 必须匹配 `yyyy-1`、`yyyy-2`、`yyyy-3`、`yyyy-4`。 |
| 上游服务超时 | `5002` | Arsenal 财务指标数据源超时。 |
| 上游服务不可用 | `5003` | Arsenal 财务指标数据源返回异常或非 0 状态码。 |


---

## 同花顺热榜（飙升/热股/历史/排名走势）

## 同花顺热榜
> A 股热度榜单、历史热股排行与个股排名走势
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- 时间戳字段为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
:::
## 接口列表
| API | 方法与路径 | 说明 | MCP |
|---|---|---|---|
| 飙升榜 | `GET /api/a-share/special-data/skyrocket-list` | 查询 A 股热度排名飙升榜 Top30，支持日榜与小时榜。 | [`get_a_share_special_data_skyrocket_list`](/docs/mcp/tools/get_a_share_special_data_skyrocket_list) |
| A股热股榜单 | `GET /api/a-share/special-data/hot-stock-list` | 查询 A 股热股榜单 Top30，支持 24 小时级别与小时级别。 | [`get_a_share_special_data_hot_stock_list`](/docs/mcp/tools/get_a_share_special_data_hot_stock_list) |
| 历史热股排行 | `GET /api/a-share/special-data/hot-stock-list-history` | 按自然日返回历史热股榜排行。 | [`get_a_share_special_data_hot_stock_list_history`](/docs/mcp/tools/get_a_share_special_data_hot_stock_list_history) |
| 个股排名走势 | `GET /api/a-share/special-data/hot-stock-rank-trend` | 查询单只 A 股一段时间内的热榜排名走势。 | [`get_a_share_special_data_hot_stock_rank_trend`](/docs/mcp/tools/get_a_share_special_data_hot_stock_rank_trend) |
## 飙升榜
```text
GET /api/a-share/special-data/skyrocket-list
**MCP Tool**：[`get_a_share_special_data_skyrocket_list`](/docs/mcp/tools/get_a_share_special_data_skyrocket_list)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `period` | query | enum | 否 | 榜单周期：`day` 日榜 / `hour` 小时榜。 | `day` |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 榜单时间戳，毫秒级 Unix 时间戳。 |
| `item` | array | 榜单股票条目，最多 30 条。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 带交易所后缀的标准代码，例如 `603822.SH`。 |
| `ticker` | string | 6 位股票代码。 |
| `name` | string | 股票简称。 |
| `rank` | integer | 当前排名。 |
| `heat` | string | 热度值，保留上游原始字符串。 |
| `rank_change` | integer \| null | 排名变化，正数表示上升，负数表示下降；上游缺失时为 `null`。 |
| `rank_trend` | string | 排名趋势：`up` / `down` / `flat` / `unknown`。 |
### 约束与错误
- `period` 仅接受 `day` / `hour`，否则返回 `code=1002`。
## A股热股榜单
```text
GET /api/a-share/special-data/hot-stock-list
**MCP Tool**：[`get_a_share_special_data_hot_stock_list`](/docs/mcp/tools/get_a_share_special_data_hot_stock_list)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `period` | query | enum | 否 | 榜单周期：`day` 24 小时级别 / `hour` 小时级别。 | `day` |
### 响应字段
### 约束与错误
- `period` 仅接受 `day` / `hour`，否则返回 `code=1002`。
## 历史热股排行
```text
GET /api/a-share/special-data/hot-stock-list-history
**MCP Tool**：[`get_a_share_special_data_hot_stock_list_history`](/docs/mcp/tools/get_a_share_special_data_hot_stock_list_history)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `date` | query | string | 是 | 目标自然日，格式 `yyyy-MM-dd`；只支持一年内数据。 | - |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `date` | string | 查询自然日，格式 `yyyy-MM-dd`。 |
| `date_ms` | long | 查询自然日 `Asia/Shanghai` 00:00 毫秒时间戳。 |
| `item` | array | 历史热股榜股票条目，最多 30 条。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 带交易所后缀的标准代码，例如 `000725.SZ`。 |
| `ticker` | string | 6 位股票代码。 |
| `name` | string | 股票简称。 |
| `rank` | integer | 当日热榜排名。 |
### 约束与错误
- `date` 必须为 `yyyy-MM-dd`，否则返回 `code=1002`。
- `date` 不在一年内时返回 `code=1003`。
## 个股排名走势
```text
GET /api/a-share/special-data/hot-stock-rank-trend
**MCP Tool**：[`get_a_share_special_data_hot_stock_rank_trend`](/docs/mcp/tools/get_a_share_special_data_hot_stock_rank_trend)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `thscode` | query | string | 是 | 单只 A 股标的，含交易所后缀，例如 `300034.SZ`。 | - |
| `start_date` | query | string | 是 | 起始自然日，格式 `yyyy-MM-dd`。 | - |
| `end_date` | query | string | 是 | 结束自然日，格式 `yyyy-MM-dd`；需大于等于 `start_date`。 | - |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 起始自然日 `Asia/Shanghai` 00:00 毫秒时间戳。 |
| `item` | array | 日线排名走势点位。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 入参标准代码。 |
| `ticker` | string | 6 位股票代码。 |
| `date` | string | 自然日，格式 `yyyy-MM-dd`。 |
| `date_ms` | long | 该自然日 `Asia/Shanghai` 00:00 毫秒时间戳。 |
| `rank` | integer | 当日热榜排名。 |
### 约束与错误
- `start_date` / `end_date` 必须为 `yyyy-MM-dd`，否则返回 `code=1002`。
- 日期不在一年内，或查询窗口超过一年时返回 `code=1003`。
- `start_date > end_date` 时返回 `code=1004`。
- `thscode` 无法映射到上游代码时返回业务错误。


---

## 涨跌停与炸板（涨停池/跌停池/炸板池/连板天梯）

## 涨跌停与炸板数据
> A 股涨停、跌停、炸板股票池与连板天梯
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- 时间戳字段为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
:::
## 接口列表
| API | 方法与路径 | 说明 | MCP |
|---|---|---|---|
| 涨停股票池 | `GET /api/a-share/special-data/limit-up-pool` | 按交易日返回 A 股涨停 / 连板股票池。 | [`get_a_share_special_data_limit_up_pool`](/docs/mcp/tools/get_a_share_special_data_limit_up_pool) |
| 跌停股票池 | `GET /api/a-share/special-data/limit-down-pool` | 按交易日返回 A 股跌停股票池。 | [`get_a_share_special_data_limit_down_pool`](/docs/mcp/tools/get_a_share_special_data_limit_down_pool) |
| 炸板股票池 | `GET /api/a-share/special-data/limit-break-pool` | 按交易日返回 A 股涨停炸板股票池。 | [`get_a_share_special_data_limit_break_pool`](/docs/mcp/tools/get_a_share_special_data_limit_break_pool) |
| 连板天梯 | `GET /api/a-share/special-data/limit-up-ladder` | 返回近 30 个交易日的连板梯队矩阵。 | [`get_a_share_special_data_limit_up_ladder`](/docs/mcp/tools/get_a_share_special_data_limit_up_ladder) |
## 涨停股票池
```text
GET /api/a-share/special-data/limit-up-pool
**MCP Tool**：[`get_a_share_special_data_limit_up_pool`](/docs/mcp/tools/get_a_share_special_data_limit_up_pool)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `date_ms` | query | long | 否 | 查询交易日 Unix 毫秒戳（Asia/Shanghai 00:00:00）；省略时回退到服务端当前自然日。 | - |
| `page` | query | integer | 否 | 页码，必须 `>= 1`。 | `1` |
| `size` | query | integer | 否 | 分页大小，取值范围 `1` 到 `200`。 | `50` |
| `sort_field` | query | enum | 否 | 排序字段：`last_price` / `continue_day_cnt` / `seal_money` / `limit_up_time`。 | `last_price` |
| `sort_dir` | query | enum | 否 | 排序方向：`asc` / `desc`。 | `desc` |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 数据就绪时间（毫秒）。 |
| `pagination` | object | 分页信息。 |
| `item` | array | 涨停股票列表。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `total` | integer | 总条数。 |
| `pages` | integer | 总页数。 |
| `size` | integer | 当前分页大小，回显请求参数。 |
| `page` | integer | 当前页码，回显请求参数。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 带交易所后缀的标准代码，例如 `603986.SH`。 |
| `ticker` | string | 6 位股票代码。 |
| `name` | string | 股票简称。 |
| `is_st` | boolean | 是否 ST，仅展示，不作为筛选入参。 |
| `is_new` | boolean | 是否未开板新股，仅展示。 |
| `last_price` | decimal | 当前价格，单位元。 |
| `price_change_ratio_pct` | decimal | 涨跌幅百分比，已乘以 100。 |
| `limit_up_time` | string | 涨停时间，格式 `HH:MM`。 |
| `limit_up_reason` | string \| null | 涨停原因；上游空字符串会标准化为 `null`。 |
| `continue_day_text` | string | 连板文本，例如 `首板`、`5天4板`。 |
| `continue_day_cnt` | integer | 连板计数。 |
| `seal_money` | decimal | 当前封单额，单位元。 |
| `max_seal_money` | decimal | 峰值封单额，单位元。 |
### 约束与错误
- `sort_field` 仅接受白名单值，否则返回 `code=1002`。
- `sort_dir` 仅接受 `asc` / `desc`。
- `page < 1` 或 `size` 不在 `1..200` 时返回 `code=1003`。
## 跌停股票池
```text
GET /api/a-share/special-data/limit-down-pool
**MCP Tool**：[`get_a_share_special_data_limit_down_pool`](/docs/mcp/tools/get_a_share_special_data_limit_down_pool)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `date_ms` | query | long | 否 | 交易日的上海时区零点毫秒时间戳。 | 当前自然日 |
| `page` | query | integer | 否 | 页码，从 1 开始。 | `1` |
| `size` | query | integer | 否 | 单页条数，范围 `1..200`。 | `50` |
| `sort_field` | query | enum | 否 | `last_limit_time` / `first_limit_time` / `last_price` / `price_change_ratio_pct` / `turnover_ratio_pct`。 | `last_limit_time` |
| `sort_dir` | query | enum | 否 | `asc` / `desc`。 | `desc` |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` / `ticker` / `name` | string | 标准代码、纯代码与股票简称。 |
| `last_price` | decimal | 最新价。 |
| `price_change_ratio_pct` | decimal | 涨跌幅，百分数原值。 |
| `first_limit_time` / `last_limit_time` | string | 首次与最后跌停时间，上海时区 `HH:mm`。 |
| `turnover_ratio_pct` | decimal | 换手率，百分数原值。 |
### 约束与错误
- `sort_field` 仅接受本接口列出的白名单值，否则返回 `code=1002`。
- `sort_dir` 仅接受 `asc` / `desc`。
- `page < 1` 或 `size` 不在 `1..200` 时返回 `code=1003`。
## 炸板股票池
```text
GET /api/a-share/special-data/limit-break-pool
**MCP Tool**：[`get_a_share_special_data_limit_break_pool`](/docs/mcp/tools/get_a_share_special_data_limit_break_pool)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `date_ms` | query | long | 否 | 交易日的上海时区零点毫秒时间戳。 | 当前自然日 |
| `page` | query | integer | 否 | 页码，从 1 开始。 | `1` |
| `size` | query | integer | 否 | 单页条数，范围 `1..200`。 | `50` |
| `sort_field` | query | enum | 否 | `price_change_ratio_pct` / `open_times` / `last_price` / `turnover_ratio_pct` / `turnover`。 | `price_change_ratio_pct` |
| `sort_dir` | query | enum | 否 | `asc` / `desc`。 | `desc` |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` / `ticker` / `name` | string | 标准代码、纯代码与股票简称。 |
| `last_price` | decimal | 最新价。 |
| `price_change_ratio_pct` | decimal | 涨跌幅，百分数原值。 |
| `open_times` | integer | 开板次数。 |
| `turnover_ratio_pct` | decimal | 换手率，百分数原值。 |
| `turnover` | decimal | 成交额。 |
### 约束与错误
- `sort_field` 仅接受本接口列出的白名单值，否则返回 `code=1002`。
- `sort_dir` 仅接受 `asc` / `desc`。
- `page < 1` 或 `size` 不在 `1..200` 时返回 `code=1003`。
## 连板天梯
```text
GET /api/a-share/special-data/limit-up-ladder
**MCP Tool**：[`get_a_share_special_data_limit_up_ladder`](/docs/mcp/tools/get_a_share_special_data_limit_up_ladder)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| - | - | - | - | 无入参。 | - |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 数据就绪时间（毫秒）。 |
| `window` | object | 窗口元信息。 |
| `item` | array | 按交易日组织的连板矩阵。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `length` | integer | 交易日窗口长度。 |
| `date_list` | string[] | 窗口内交易日列表，按后端返回顺序排列。 |
| `board_caps` | object | 每个板位的最大列表长度。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 带交易所后缀的标准代码。 |
| `ticker` | string | 6 位股票代码。 |
| `name` | string | 股票简称。 |
| `board_num` | integer | 连板数。 |
| `seal_nextday` | boolean \| null | 次一交易日是否继续封板；最近交易日没有次日参考，固定为 `null`。 |
| `sign_level` | integer | 上游标记等级。 |


---

## 股票基础信息（所属同花顺指数）

## 股票基础信息
> A 股标的基础信息接口（敬请期待）
:::info 敬请期待
**股票基础信息** 接口正在规划中。
将提供 A 股标的基本资料、上市状态、行业归属、市值等核心字段查询。
:::
## 股票所属同花顺指数查询
> 按个股反查所属同花顺行业/概念指数（敬请期待）
:::info 敬请期待
**股票所属同花顺指数查询** 接口正在规划中。
将按个股 thscode 反查其所属的同花顺行业、概念等指数集合。
:::


---

## 估值数据（PE/PB/PS/PCF 四类口径）

## 估值数据
> A 股多股票最新估值快照，固定返回市盈率 TTM/MRQ、市净率 MRQ、市销率 TTM 和市现率 TTM 五个估值指标
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- `thscodes` 使用英文逗号分隔，大小写不敏感；服务端会 trim、转为大写、去重并保留首次出现顺序。
- 一次请求默认最多接受 100 个原始 token；该上限由服务端配置，调用方不能覆盖。
- 接口固定返回市盈率 TTM/MRQ、市净率 MRQ、市销率 TTM 和市现率 TTM 五个估值指标，不提供历史估值、分页、指标选择或高低估结论。
:::
## 接口
| REST 端点 | MCP Tool | 说明 |
|---|---|---|
| `GET /api/a-share/valuations/snapshot` | [`get_a_share_valuations_snapshot`](/docs/mcp/tools/get_a_share_valuations_snapshot) | 批量查询 A 股最新估值快照 |
## A股估值快照
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `thscodes` | string | 是 | — | 英文逗号分隔的 A 股 thscode 列表，如 `600519.SH,000001.SZ`；每项必须为六位数字加 `.SH`、`.SZ` 或 `.BJ`。 |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | integer | 业务状态码，`0` 表示成功。 |
| `message` | string | 业务状态说明。 |
| `request_id` | string | 请求追踪 ID。 |
| `data.timestamp` | long \| null | 本次响应所用上游指标元数据中的最大有效时间，单位为毫秒；无有效时间时为 `null`。 |
| `data.total` | integer | 实际返回的股票条数。 |
| `data.item` | array | 估值快照列表，按去重后的请求顺序返回。 |
| `data.item[].thscode` | string | 带交易所后缀的完整 thscode。 |
| `data.item[].ticker` | string | 六位股票代码，不含交易所后缀。 |
| `data.item[].name` | string \| null | 本地 A 股代码表中的股票名称。 |
| `data.item[].pe_ttm` | number \| null | 市盈率 TTM。 |
| `data.item[].pe_mrq` | number \| null | 市盈率 MRQ。 |
| `data.item[].pb_mrq` | number \| null | 市净率 MRQ。 |
| `data.item[].ps_ttm` | number \| null | 市销率 TTM。 |
| `data.item[].pcf_ttm` | number \| null | 市现率 TTM。 |
:::note 数据语义
- 每个返回项固定包含 5 个指标字段；上游空值返回 `null`，不会补零。
- 负值和高精度十进制值原样返回，服务端不做估值计算、聚合、取绝对值或四舍五入。
- 上游未返回的股票不会生成占位项；无匹配记录时返回 `code=0`、`total=0`、`item=[]`。
:::
### 指标说明
| 指标分类 | 数据项 | 字段名 |
|---|---|---|
| 市盈率（PE） | 市盈率（TTM） | `pe_ttm` |
| 市盈率（PE） | 市盈率（MRQ） | `pe_mrq` |
| 市净率（PB） | 市净率（MRQ） | `pb_mrq` |
| 市销率（PS） | 市销率（TTM） | `ps_ttm` |
| 市现率（PCF） | 市现率（TTM） | `pcf_ttm` |
#### 市盈率（PE）
#### 市净率（PB）
#### 市销率（PS）
#### 市现率（PCF）
### 计算口径
| 口径 | 英文全称 | 说明 |
|---|---|---|
| TTM | Trailing Twelve Months | 使用最近连续 12 个月的数据，通常由最近四个季度数据计算。 |
| MRQ | Most Recent Quarter | 使用最近一个已披露报告期的数据。 |
:::tip 使用说明
1. 估值指标衡量股票价格与公司财务数据之间的相对关系，不代表股票的绝对投资价值。
2. 不同行业的盈利模式、资产结构和现金流特征不同，跨行业直接比较可能产生偏差。
3. 当净利润、净资产或经营现金流为负时，部分指标可能返回负值或 `null`。
4. TTM 与 MRQ 使用的财务数据周期不同，同一股票的两个口径可能存在明显差异。
5. 实际结果应以接口返回的数据值、`data.timestamp` 和字段说明为准。
:::
### 错误与约束
| 场景 | `code` | 说明 |
|---|---|---|
| 缺少 `thscodes` | `1001` | 必填参数缺失。 |
| 存在空 token 或 thscode 格式非法 | `1002` | 每项必须为六位数字加 `.SH`、`.SZ` 或 `.BJ`。 |
| 原始 token 数超过服务端上限 | `1003` | 默认最多 100 个。 |
| 格式正确但代码表不存在 | `3001` | 目标不在 A 股代码表中。 |
| 数据源超时 | `5002` | DataAPI 请求超时。 |
| 数据源不可用 | `5003` | DataAPI 返回异常、空响应或非成功状态。 |


---

## 公募基金（资料/经理/持仓/业绩/行情/资讯）

## 基金
> 基金资料、持仓、业绩、经理、财务、资讯与行情数据 API 总览
## 功能分类
| 分类 | 路径前缀 | 说明 |
|---|---|---|
| [基金基本资料](./fund-profile.mdx) | `/api/fund/profile` | 查询基金名称、成立日期、管理人与基金经理等基本资料。 |
| [基金重仓持仓](./fund-holdings.mdx) | `/api/fund/portfolio/holdings` | 查询基金定期披露的股票、债券和基金持仓。 |
| [基金持仓与资产配置](./fund-portfolio.mdx) | `/api/fund/portfolio` | 查询历史股票/债券持仓、报告期、资产与行业配置。 |
| [基金业绩与回撤](./fund-performance.mdx) | `/api/fund/performance` | 查询基金净值、收益、历史指标与最大回撤。 |
| [基金持有人数据](./fund-holders.mdx) | `/api/fund/holders` | 查询持有人结构与前十大持有人。 |
| [基金分红记录](./fund-corporate-actions.mdx) | `/api/fund/corporate-actions` | 查询基金历史分红。 |
| [基金经理数据](./fund-managers.mdx) | `/api/fund/managers` | 查询经理投资风格、业绩、经历与详情。 |
| [基金公司详情](./fund-company.mdx) | `/api/fund/companies` | 查询基金公司基本信息、基金数量与规模。 |
| [基金诊断详情](./fund-diagnostics.mdx) | `/api/fund/diagnostics` | 查询诊断维度、同类对比与韧性指标。 |
| [基金募集列表](./fund-offerings.mdx) | `/api/fund/offerings` | 查询当前募集或即将募集的新发基金。 |
| [基金资讯列表](./fund-news.mdx) | `/api/fund/news` | 游标分页查询基金资讯文章。 |
| [基金财务数据](./fund-financials.mdx) | `/api/fund/financials` | 查询财务指标、利润表与资产负债表。 |
| [基金行情数据](./fund-market.mdx) | `/api/fund/market` | 查询场内基金行情快照与场内基金历史日线行情。 |
## 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失、无效或无权访问时返回认证/权限错误码。
- `fund_type`：`otc`（场外基金）/ `exchange`（ETF、LOF）/ `reits`；仅非行情接口需要传入。
- `thscode`：完整同花顺代码，例如 `025480.OF`、`510300.SH`、`161725.SZ`。
- 时间戳均为毫秒级 Unix 时间戳；有可信上游数据时间时 `data.timestamp` 保留该时间，否则使用服务端响应组装时间。收益率、占比与涨跌幅均为百分数原值，例如 `8.88` 表示 `8.88%`。
## 错误与约束
| code | 含义 | 基金场景 |
|---|---|---|
| `1001` | 缺少必填参数 | 非行情接口缺少 `fund_type`，或缺少 `thscode`、`start`、`end`。 |
| `1002` | 参数格式错误 | 历史行情 `thscode` 含逗号。 |
| `1003` | 参数值越界 | 枚举非法、`start > end` 或查询窗口超过 5 年。 |
| `1004` | 参数冲突 | `fund_type` 多选，或基金类型与 `thscode` 所在分区不一致。 |
| `3001` | 标的不存在 | 找不到该基金。 |
| `3002` | 数据未就绪 | 标的存在，但暂无可用业务数据。 |
| `3004` | 标的类型不支持该能力 | 该基金类型不支持所请求的能力。 |
## 特色数据
> A 股特色数据：涨跌停与炸板数据、同花顺热榜、个股异动原因与龙虎榜
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- 时间戳字段为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
:::
## 文档分组
| 分组 | 覆盖接口 | 说明 |
|---|---|---|
| [涨跌停与炸板数据](./limit-up-data.mdx) | `limit-up-pool` / `limit-down-pool` / `limit-break-pool` / `limit-up-ladder` | 涨停、跌停、炸板股票池与连板天梯。 |
| [同花顺热榜](./hot-list-data.mdx) | `skyrocket-list` / `hot-stock-list` / `hot-stock-list-history` / `hot-stock-rank-trend` | 热度榜单、历史热股排行与个股排名走势。 |
| [个股异动原因](./anomaly-analysis.mdx) | `anomaly-analysis-list` / `anomaly-analysis-stock` | 当日个股异动原因列表与按股票批量查询。 |
| [龙虎榜数据](./dragon-tiger-data.mdx) | `dragon-tiger-list` | 按交易日返回全部、机构榜或游资榜。 |
## 接口列表
| API | 方法与路径 | 说明 | MCP |
|---|---|---|---|
| [涨停股票池](./limit-up-data.mdx#涨停股票池) | `GET /api/a-share/special-data/limit-up-pool` | 按交易日返回 A 股涨停 / 连板股票池。 | [`get_a_share_special_data_limit_up_pool`](/docs/mcp/tools/get_a_share_special_data_limit_up_pool) |
| [跌停股票池](./limit-up-data.mdx#跌停股票池) | `GET /api/a-share/special-data/limit-down-pool` | 按交易日返回 A 股跌停股票池。 | [`get_a_share_special_data_limit_down_pool`](/docs/mcp/tools/get_a_share_special_data_limit_down_pool) |
| [炸板股票池](./limit-up-data.mdx#炸板股票池) | `GET /api/a-share/special-data/limit-break-pool` | 按交易日返回 A 股涨停炸板股票池。 | [`get_a_share_special_data_limit_break_pool`](/docs/mcp/tools/get_a_share_special_data_limit_break_pool) |
| [连板天梯](./limit-up-data.mdx#连板天梯) | `GET /api/a-share/special-data/limit-up-ladder` | 返回近 30 个交易日的连板梯队矩阵。 | [`get_a_share_special_data_limit_up_ladder`](/docs/mcp/tools/get_a_share_special_data_limit_up_ladder) |
| [飙升榜](./hot-list-data.mdx#飙升榜) | `GET /api/a-share/special-data/skyrocket-list` | 查询 A 股热度排名飙升榜 Top30，支持日榜与小时榜。 | [`get_a_share_special_data_skyrocket_list`](/docs/mcp/tools/get_a_share_special_data_skyrocket_list) |
| [A股热股榜单](./hot-list-data.mdx#a股热股榜单) | `GET /api/a-share/special-data/hot-stock-list` | 查询 A 股热股榜单 Top30，支持 24 小时级别与小时级别。 | [`get_a_share_special_data_hot_stock_list`](/docs/mcp/tools/get_a_share_special_data_hot_stock_list) |
| [历史热股排行](./hot-list-data.mdx#历史热股排行) | `GET /api/a-share/special-data/hot-stock-list-history` | 按自然日返回历史热股榜排行。 | [`get_a_share_special_data_hot_stock_list_history`](/docs/mcp/tools/get_a_share_special_data_hot_stock_list_history) |
| [个股排名走势](./hot-list-data.mdx#个股排名走势) | `GET /api/a-share/special-data/hot-stock-rank-trend` | 查询单只 A 股一段时间内的热榜排名走势。 | [`get_a_share_special_data_hot_stock_rank_trend`](/docs/mcp/tools/get_a_share_special_data_hot_stock_rank_trend) |
| [个股异动原因列表](./anomaly-analysis.mdx#个股异动原因列表) | `GET /api/a-share/special-data/anomaly-analysis-list` | 查询当日个股异动原因，可选按异动标签过滤。 | 不提供 MCP |
| [按股票查询个股异动原因](./anomaly-analysis.mdx#按股票查询个股异动原因) | `GET /api/a-share/special-data/anomaly-analysis-stock` | 按同花顺代码批量查询当日个股异动原因。 | [`get_a_share_special_data_anomaly_analysis_stock`](/docs/mcp/tools/get_a_share_special_data_anomaly_analysis_stock) |
| [龙虎榜榜单](./dragon-tiger-data.mdx#龙虎榜榜单) | `GET /api/a-share/special-data/dragon-tiger-list` | 按交易日返回全部、机构榜或游资榜。 | [`get_a_share_special_data_dragon_tiger_list`](/docs/mcp/tools/get_a_share_special_data_dragon_tiger_list) |
## 个股异动原因
> A 股个股异动原因列表与按股票查询能力
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- 时间戳字段为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
:::
## 接口列表
| API | 方法与路径 | 说明 | MCP |
|---|---|---|---|
| 个股异动原因列表 | `GET /api/a-share/special-data/anomaly-analysis-list` | 查询当日个股异动原因，可选按异动标签过滤。 | 不提供 MCP |
| 按股票查询个股异动原因 | `GET /api/a-share/special-data/anomaly-analysis-stock` | 按同花顺代码批量查询当日个股异动原因。 | [`get_a_share_special_data_anomaly_analysis_stock`](/docs/mcp/tools/get_a_share_special_data_anomaly_analysis_stock) |
## 个股异动原因列表
```text
GET /api/a-share/special-data/anomaly-analysis-list
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `tag_codes` | query | string | 否 | 异动标签，逗号分隔，多个值为 OR 关系；大小写不敏感，重复值自动去重。合法值见下方标签表。 | - |
| 值 | 含义 |
|---|---|
| `LIMIT_UP` | 涨停 |
| `LIMIT_DOWN` | 跌停 |
| `SHARP_RISE` | 大涨 |
| `SHARP_FALL` | 大跌 |
| `RAPID_RALLY` | 快速拉升 |
| `RAPID_DECLINE` | 快速下挫 |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 数据时间戳，毫秒级 Unix 时间戳。 |
| `item` | array | 个股异动原因列表。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `stock_name` | string | 股票名称。 |
| `analysis_content` | string | 异动解读内容。 |
| `keyword_list` | string[] | 关键词列表；无关键词时返回空数组。 |
| `thscode` | string | 带交易所后缀的同花顺代码，例如 `600519.SH`。 |
| `tag_name` | string | 异动标签展示名。 |
### 约束与错误
- `tag_codes` 中出现未知值、连续逗号或尾逗号导致的空 token 时返回 `code=1002`。
- 当日数据暂不可用时返回 `code=3002`。
- 有快照但查询无匹配时返回 `code=0`，且 `item=[]`。
## 按股票查询个股异动原因
```text
GET /api/a-share/special-data/anomaly-analysis-stock
**MCP Tool**：[`get_a_share_special_data_anomaly_analysis_stock`](/docs/mcp/tools/get_a_share_special_data_anomaly_analysis_stock)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `thscodes` | query | string | 是 | 逗号分隔的同花顺代码列表，支持 `SH` / `SZ` / `BJ` 后缀，大小写不敏感；去重前最多 50 个 token。 | - |
### 响应字段
### 约束与错误
- 缺失或空白 `thscodes` 返回 `code=1001`。
- `thscodes` 出现空 token 或不符合 `000001.SZ` / `600519.SH` / `430001.BJ` 这类格式时返回 `code=1002`。
- 去重前 token 数超过 50 时返回 `code=1003`。
- 当日数据暂不可用时返回 `code=3002`。
- 有快照但查询无匹配时返回 `code=0`，且 `item=[]`。
## 集合竞价数据
> 查询 A 股集合竞价快照与短线风向标竞价基准
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`；认证与权限错误通过业务 `code` 表达。
- 所有接口返回统一 `ApiResponse` 信封，业务结果通过 `code` 表达。
- A 股标的使用带交易所后缀的完整 `thscode`；时间戳均为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
:::
## A股集合竞价快照
```text
GET /api/a-share/auction/snapshot
**MCP Tool**：[`get_a_share_auction_snapshot`](/docs/mcp/tools/get_a_share_auction_snapshot)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `thscodes` | string | 是 | — | 一个或多个 A 股 thscode，使用英文逗号分隔；服务端按请求顺序去重返回。 |
| `stage` | enum | 否 | `final` | `live`（实时阶段）或 `final`（终态）。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `data.timestamp` | long | 接口响应组装时间，毫秒 Unix 时间戳；实时、终态、停牌及 `not_ready` 场景均会返回。上游竞价行情时间仅用于判断数据新鲜度。 |
| `data.auction_phase` | string | 集合竞价阶段。 |
| `data.data_status` | string | 数据状态。 |
| `data.total` | integer | 返回标的数量。 |
| `data.item` | array | 集合竞价明细列表。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` / `ticker` / `name` | string | 标准代码、纯代码与股票简称。 |
| `auction_price` / `auction_pct` | number | 竞价价格与竞价涨跌幅百分数原值。 |
| `auction_volume` / `auction_amount` / `auction_unmatched` | number | 竞价成交量、成交额与未匹配量。 |
| `auction_turnover_pct` / `auction_yesterday_ratio_pct` / `auction_volume_ratio` | number | 竞价换手率、相对昨日成交量比例与竞价量比。 |
| `pre_close_price` / `open_price` / `last_price` | number | 前收盘价、开盘价与最新价。 |
| `float_market_cap` | number | 流通市值。 |
## 短线风向标竞价基准
```text
GET /api/a-share/auction/short-term-benchmark
**MCP Tool**：[`get_a_share_auction_short_term_benchmark`](/docs/mcp/tools/get_a_share_auction_short_term_benchmark)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `date` | string | 否 | 上海时区当日 | 查询日期，格式 `yyyy-MM-dd`；缺失或传入空字符串时使用 `Asia/Shanghai` 当日，显式指定非交易日时不自动回退。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 接口响应组装时间，毫秒 Unix 时间戳。 |
| `date` | string | 最终查询日期，格式 `yyyy-MM-dd`。 |
| `date_ms` | long | 最终查询日期在 `Asia/Shanghai` 当日零点的毫秒 Unix 时间戳。 |
| `item` | array | 短线风向标竞价基准明细。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 完整 A 股 thscode。 |
| `ticker` | string | 纯股票代码。 |
| `name` | string | 股票简称。 |
| `auction_pct` | number | 集合竞价涨跌幅，百分数原值。 |
| `tags` | array | 短线风向标标签。 |
## 龙虎榜数据
> A 股龙虎榜榜单，覆盖全部、机构榜与游资榜
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- 时间戳字段为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
:::
## 接口列表
| API | 方法与路径 | 说明 | MCP |
|---|---|---|---|
| 龙虎榜榜单 | `GET /api/a-share/special-data/dragon-tiger-list` | 按交易日返回全部、机构榜或游资榜。 | [`get_a_share_special_data_dragon_tiger_list`](/docs/mcp/tools/get_a_share_special_data_dragon_tiger_list) |
## 龙虎榜榜单
```text
GET /api/a-share/special-data/dragon-tiger-list
**MCP Tool**：[`get_a_share_special_data_dragon_tiger_list`](/docs/mcp/tools/get_a_share_special_data_dragon_tiger_list)
### 请求参数
| 参数 | 位置 | 类型 | 必需 | 说明 | 默认值 |
|---|---|---|---|---|---|
| `board_type` | query | enum | 否 | 榜单类型：`all` 全部 / `org` 机构榜 / `hot_money` 游资榜。 | `all` |
| `date` | query | string | 否 | 目标交易日，格式 `yyyy-MM-dd`；只支持一年内数据。显式传入非交易日返回 `code=1002`。 | 最近可用交易日 |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 目标交易日 `Asia/Shanghai` 00:00 毫秒时间戳。 |
| `board_type` | string | 实际榜单类型：`all` / `org` / `hot_money`。 |
| `trade_date` | string | 实际查询交易日，格式 `yyyy-MM-dd`。 |
| `count` | integer | 上游记录数；同一股票可能同时出现当日榜和 3 日榜。 |
| `stock_count` | integer | 股票去重数量。 |
| `stock_items` | array | 股票维度榜单；`board_type=all/org` 时填充，`hot_money` 时为空数组。 |
| `hot_money_items` | array | 游资维度聚合榜单；`board_type=hot_money` 时填充，普通榜单时为空数组。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 带交易所后缀的标准代码，例如 `002407.SZ`。 |
| `ticker` | string | 6 位股票代码。 |
| `name` | string | 股票简称。 |
| `concept_list` | array | 所属概念列表，元素包含 `name`。 |
| `change` | number | 当日涨跌幅，小数形式。 |
| `net_value` | number | 龙虎榜净买入金额，单位元。 |
| `net_rate` | number | 龙虎榜净买入占比，小数形式。 |
| `hot_rank` | integer | 同花顺人气排名，数值越小越靠前。 |
| `buy_value` | number | 买方金额，单位元。 |
| `sell_value` | number | 卖方金额，单位元。 |
| `limit_reason` | string | 涨跌停原因。 |
| `range_days` | integer | 上榜区间天数，`1` 为当日榜，`3` 为 3 日榜。 |
| `org_net_value` | number | 机构净买入金额，单位元。 |
| `org_net_rate` | number | 机构净买入占比，小数形式。 |
| `org_buy_num` | integer | 买入机构数。 |
| `org_sell_num` | integer | 卖出机构数。 |
| `amount` | number | 成交金额，单位元。 |
| `hot_money_net_value` | number | 股票维度游资合计净买入金额，单位元。 |
| `hot_money_net_rate` | number | 股票维度游资合计净买入占比，小数形式。 |
| `hot_money_item_net_value` | number | 该游资在该股上的净买入金额，单位元。 |
| `hot_money_item_net_rate` | number | 该游资在该股上的净买入占比，小数形式。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | string | 游资名称。 |
| `buying` | number | 聚合净买入金额，单位元。 |
| `rows` | array | 该游资关联股票列表，字段同 `stock_items[]`。 |
### 约束与错误
- `board_type` 仅接受 `all` / `org` / `hot_money`，否则返回 `code=1002`。
- `date` 必须为 `yyyy-MM-dd`，否则返回 `code=1002`。
- 显式传入的 `date` 必须是 A 股交易日，否则返回 `code=1002`。
- `date` 不在一年内，或日期晚于今天时返回 `code=1003`。
## 财务指标数据
> A 股财务指标数据，一次返回成长、盈利、偿债、营运、现金流五类指标
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`，缺失或无效返回 `code=2001`。
- `report` 格式为 `yyyy-1`、`yyyy-2`、`yyyy-3`、`yyyy-4`，其中 `1` 一季报、`2` 中报、`3` 三季报、`4` 年报。
- 指标项包含 `index_id` / `value`。`index_id` 使用下方表格列出的接口契约字段名，`value` 为数据源原始数值字符串；上游缺失时返回 `null`。
:::
## 接口
| REST 端点 | MCP Tool | 说明 |
|---|---|---|
| `GET /api/a-share/financials/indicators` | [`get_a_share_financials_indicators`](/docs/mcp/tools/get_a_share_financials_indicators) | 财务指标数据 |
## 财务指标数据
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `thscode` | string | 是 | — | 单只标的 thscode，含交易所后缀，如 `300033.SZ`。 |
| `report` | string | 是 | — | 报告期，示例 `2025-1`；格式见上方通用约定。 |
### 响应字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | integer | 业务状态码，`0` 表示成功。 |
| `message` | string | 业务状态说明。 |
| `request_id` | string | 请求追踪 ID。 |
| `data.thscode` | string | 入参 thscode 回显。 |
| `data.report` | string | 入参 report 回显。 |
| `data.abilities[]` | array | 五类能力块，固定顺序为 `growth`、`profitability`、`solvency`、`operation`、`cash-flow`。 |
| `data.abilities[].ability` | string | 能力标识。 |
| `data.abilities[].indicators[]` | array | 当前能力下的指标列表。 |
| `data.abilities[].indicators[].index_id` | string | 指标 ID，取值见下方表格。 |
| `data.abilities[].indicators[].value` | string \| null | 本期指标值。服务端保留数据源原始数值字符串，不承诺固定小数位；上游空值或缺失值标准化为 `null`。百分比类指标按百分数值表达，例如 `89.12000000` 表示 `89.12%`；周转率、比率、倍数类指标按指标名称对应单位解释。 |
:::note 数值口径
`value` 暂不转为 JSON number，是为了保留数据源精度和尾随小数位。调用方展示时应按 `index_id` 识别单位：名称含“增长率”“毛利率”“净利率”“收益率”“资产负债率”“现金比率”等的指标按百分比展示；“周转率”通常按次展示；“已获利息倍数”按倍展示；缺失值展示为 `--` 或空值。
:::
### 指标字段
#### 成长能力 `growth`
| `index_id` | 指标名称 |
|---|---|
| `total_assets_growth_ratio` | 总资产增长率 |
| `net_profit_yoy_growth_ratio` | 净利润同比增长率 |
| `operating_income_yoy_growth_ratio` | 营业收入同比增长率 |
| `operating_profit_yoy_growth_ratio` | 营业利润同比增长率 |
#### 盈利能力 `profitability`
| `index_id` | 指标名称 |
|---|---|
| `sale_gross_margin` | 销售毛利率 |
| `sale_net_interest_ratio` | 销售净利率 |
| `total_assets_net_ratio` | 总资产收益率 |
| `index_deduct_weighted_avg_roe` | 扣非加权净资产收益率 |
| `index_weighted_avg_roe` | 净资产收益率 |
#### 偿债能力 `solvency`
| `index_id` | 指标名称 |
|---|---|
| `current_ratio` | 流动比率 |
| `quick_ratio` | 速动比率 |
| `assets_debt_ratio` | 资产负债率 |
| `cash_ratio` | 现金比率 |
| `earned_interest_multiple` | 已获利息倍数 |
#### 营运能力 `operation`
| `index_id` | 指标名称 |
|---|---|
| `long_term_debt_equity_ratio` | 长期负债权益比率 |
| `total_assets_turnover_ratio` | 总资产周转率 |
| `inventory_turnover_ratio` | 存货周转率 |
| `current_assets_turnover_ratio` | 流动资产周转率 |
| `receive_account_turnover_ratio` | 应收账款周转率 |
#### 现金流 `cash-flow`
| `index_id` | 指标名称 |
|---|---|
| `cash_operating_index` | 现金营运指数 |
| `operating_cash_flow_net_divide_income` | 销售现金比率 |
| `net_profit_cash_content` | 净利润现金含量 |
| `operating_cash_net_yoy_growth_ratio` | 现金流量净额增长率 |
| `cash_meet_invest_ratio` | 现金满足投资比率 |
### 错误与约束
| 场景 | `code` | 说明 |
|---|---|---|
| 缺少 `thscode` 或 `report` | `1001` | 必填参数缺失。 |
| `report` 格式非法 | `1002` | 必须匹配 `yyyy-1`、`yyyy-2`、`yyyy-3`、`yyyy-4`。 |
| 上游服务超时 | `5002` | Arsenal 财务指标数据源超时。 |
| 上游服务不可用 | `5003` | Arsenal 财务指标数据源返回异常或非 0 状态码。 |
## 基金公司详情
> 按基金公司 ID 查询公司名称、类型、成立日期、基金数量与规模
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`；认证与权限错误通过业务 `code` 表达。
- 接口返回统一 `ApiResponse` 信封；时间戳均为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
- `company_id` 是基金公司 ID，可从基金基本资料返回值获取，不使用公司名称代替。
:::
```text
GET /api/fund/companies/detail
**MCP Tool**：[`get_fund_companies_detail`](/docs/mcp/tools/get_fund_companies_detail)
## 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `company_id` | string | 是 | — | 基金公司 ID，可从基金基本资料的 `company_id` 获取。 |
## 响应示例
## 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `company_id` | string | 基金公司 ID。 |
| `company_name` | string | 基金公司名称。 |
| `company_type` | string | 基金公司类型。 |
| `established_date_ms` | long | 成立日期，毫秒 Unix 时间戳。 |
| `fund_count` | integer | 公司旗下基金数量。 |
| `scale` | number | 公司管理规模。 |
## 基金分红记录
> 查询单只基金的历史分红与权益登记日期
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`；认证与权限错误通过业务 `code` 表达。
- 接口返回统一 `ApiResponse` 信封；时间戳均为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
- `fund_type` 取 `otc`、`exchange` 或 `reits`；`thscode` 必须保留市场后缀并与基金类型匹配。
:::
```text
GET /api/fund/corporate-actions/dividends
**MCP Tool**：[`get_fund_corporate_actions_dividends`](/docs/mcp/tools/get_fund_corporate_actions_dividends)
## 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc` / `exchange` / `reits`。 |
| `thscode` | string | 是 | — | 完整基金 thscode。 |
## 响应示例
## 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 接口响应时间戳，毫秒 Unix 时间戳。 |
| `dividend_count` | integer | 返回的分红记录总数。 |
| `dividend_total` | number | 服务端返回的累计分红汇总值；不要与每 10 份现金分红混用。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `per_ten_cash_before_tax` / `per_ten_cash_after_tax` | number | 每 10 份税前/税后现金分红。 |
| `progress` | string | 分红进度。 |
| `publish_date_ms` / `registration_date_ms` / `ex_dividend_date_ms` | long | 公告日、权益登记日与除息日。 |
| `payment_date_ms` / `reinvestment_date_ms` | long | 派息日与红利再投资日。 |
| `profit_base_date_ms` / `in_dividend_date_ms` | long | 收益基准日及分红相关日期。 |
## 基金诊断详情
> 查询基金诊断维度、同类对比、概率区间与韧性指标
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`；认证与权限错误通过业务 `code` 表达。
- 接口返回统一 `ApiResponse` 信封；时间戳均为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
- `fund_type` 取 `otc`、`exchange` 或 `reits`；`thscode` 必须保留市场后缀并与基金类型匹配。
:::
```text
GET /api/fund/diagnostics/detail
**MCP Tool**：[`get_fund_diagnostics_detail`](/docs/mcp/tools/get_fund_diagnostics_detail)
## 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc` / `exchange` / `reits`。 |
| `thscode` | string | 是 | — | 完整基金 thscode。 |
## 响应示例
## 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 完整基金 thscode。 |
| `ticker` | string | 纯基金代码。 |
| `fund_type` | string | 基金类型。 |
| `peer_code` | string | 同类比较分组代码。 |
| `dimensions` / `peer_dimensions` | object | 基金诊断维度及同类对比数据，保留上游结构。 |
| `probabilities` / `ranges` | object | 概率与区间数据，保留上游结构。 |
| `resilience` / `peer_resilience` | object | 基金韧性及同类韧性数据，保留上游结构。 |
## 基金财务数据
> 查询基金财务指标、利润表与资产负债表
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`；认证与权限错误通过业务 `code` 表达。
- 本页接口返回统一 `ApiResponse` 信封；时间戳均为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
- `fund_type` 取 `otc`、`exchange` 或 `reits`；`thscode` 必须保留市场后缀并与基金类型匹配。未披露字段保持 `null`，不补零。
:::
## 通用请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc`（场外基金）/ `exchange`（ETF、LOF）/ `reits`（公募 REITs）。 |
| `thscode` | string | 是 | — | 完整基金 thscode，必须保留市场后缀。 |
## 基金财务指标
```text
GET /api/fund/financials/indicators
**MCP Tool**：[`get_fund_financials_indicators`](/docs/mcp/tools/get_fund_financials_indicators)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc`（场外基金）/ `exchange`（ETF、LOF）/ `reits`（公募 REITs）。 |
| `thscode` | string | 是 | — | 完整基金 thscode，必须保留市场后缀。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `start_date_ms` / `end_date_ms` / `publish_date_ms` | long | 报告期起止时间与发布日期。 |
| `distribution_profit` / `current_profit` / `current_income` | number | 可分配利润、本期利润与本期收入。 |
| `distribution_share_profit` | number | 每份可分配利润。 |
| `average_nav_profit_margin` / `average_share_current_profit` | number | 平均净值利润率与平均每份本期利润。 |
| `share_nav` / `sum_share_nav` | number | 单位净值与累计单位净值。 |
| `asset_nav` | number | 基金资产净值。 |
| `sum_nav_rate` / `nav_rate` | number | 累计净值增长率与净值增长率。 |
## 基金利润表
```text
GET /api/fund/financials/income-statements
**MCP Tool**：[`get_fund_financials_income_statements`](/docs/mcp/tools/get_fund_financials_income_statements)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc`（场外基金）/ `exchange`（ETF、LOF）/ `reits`（公募 REITs）。 |
| `thscode` | string | 是 | — | 完整基金 thscode，必须保留市场后缀。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `start_date_ms` / `end_date_ms` / `publish_date_ms` | long | 报告期起止时间与发布日期。 |
| `income` / `total_income` | number | 收入与收入合计。 |
| `investment_income` | number | 投资收益。 |
| `stock_investment_income` / `bond_investment_income` / `fund_investment_income` | number | 股票、债券与基金投资收益。 |
| `dividend_income` / `interest_income` | number | 股利与利息收入。 |
| `fair_value_income` / `exchange_income` / `other_income` | number | 公允价值、汇兑及其他收入。 |
| `fee` / `total_fee` | number | 费用与费用合计。 |
| `manager_reward` / `custodian_fee` / `transaction_cost` / `tax_surcharge` | number | 管理人报酬、托管费、交易成本与税费。 |
| `total_profit` / `net_profit` | number | 利润总额与净利润。 |
## 基金资产负债表
```text
GET /api/fund/financials/balance-sheets
**MCP Tool**：[`get_fund_financials_balance_sheets`](/docs/mcp/tools/get_fund_financials_balance_sheets)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc`（场外基金）/ `exchange`（ETF、LOF）/ `reits`（公募 REITs）。 |
| `thscode` | string | 是 | — | 完整基金 thscode，必须保留市场后缀。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `start_date_ms` / `end_date_ms` / `publish_date_ms` | long | 报告期起止时间与发布日期。 |
| `total_assets` | number | 资产总计。 |
| `bank_deposit` | number | 银行存款。 |
| `fund_investment` / `stock_investment` / `bond_investment` | number | 基金、股票与债券投资。 |
| `transactional_financial_assets` / `other_assets` | number | 交易性金融资产与其他资产。 |
| `total_liability` / `other_liability` | number | 负债合计与其他负债。 |
| `owner_total_equity` / `undistributed_profit` | number | 所有者权益与未分配利润。 |
| `liability_and_owner_equity` | number | 负债和所有者权益总计。 |
## 基金持有人数据
> 查询基金持有人结构与前十大持有人
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`；认证与权限错误通过业务 `code` 表达。
- 本页接口返回统一 `ApiResponse` 信封；时间戳均为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
- `fund_type` 取 `otc`、`exchange` 或 `reits`；`thscode` 必须保留市场后缀并与基金类型匹配。占比字段为百分数原值，例如 `8.88` 表示 `8.88%`。
:::
## 基金持有人结构
```text
GET /api/fund/holders/detail
**MCP Tool**：[`get_fund_holders_detail`](/docs/mcp/tools/get_fund_holders_detail)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc`（场外基金）/ `exchange`（ETF、LOF）/ `reits`（公募 REITs）。 |
| `thscode` | string | 是 | — | 完整基金 thscode，必须保留市场后缀。 |
| `merge_scope` | enum | 否 | `all` | `all`（分别返回合并/独立份额的最新记录）/ `merged`（A/C 等份额合并披露）/ `separate`（当前份额独立披露）。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `merge_scope` | string | 该条记录的实际披露口径：`merged` 或 `separate`。 |
| `report_date_ms` | integer | 该条记录的披露报告日，毫秒 Unix 时间戳。 |
| `ins_position` | number | 机构投资者占比，百分数原值。 |
| `holder_amount` | integer | 基金份额持有人户数。 |
| `avg_holder_share` | number | 平均每户持有基金份额。 |
| `psnl_rate` | number | 个人投资者占比，百分数原值。 |
| `mgmt_staff_hold_rate` | number | 管理人员工持有比例，百分数原值。 |
## 基金前十大持有人
```text
GET /api/fund/holders/top
**MCP Tool**：[`get_fund_holders_top`](/docs/mcp/tools/get_fund_holders_top)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc` / `exchange` / `reits`。 |
| `thscode` | string | 是 | — | 完整基金 thscode。 |
| `limit` | integer | 否 | 服务端默认 | 返回条数，最大为 `10`。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 接口响应时间戳，毫秒 Unix 时间戳。 |
| `limit` | integer | 服务端实际采用的返回条数上限。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `holder_id` / `holder_code` | string | 持有人 ID 与代码。 |
| `holder_name` | string | 持有人名称。 |
| `holder_type` | string | 持有人类型。 |
| `rank` | integer | 持有排名。 |
| `hold_share` | number | 持有份额。 |
| `hold_rate_pct` | number | 持有比例，百分数原值。 |
| `report_date_ms` / `publish_date_ms` | long | 报告日与发布日期，毫秒 Unix 时间戳。 |
## 基金重仓持仓
> 查询基金定期披露的股票、债券与基金持仓及汇总指标
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`；认证与权限错误通过业务 `code` 表达。
- 接口返回统一 `ApiResponse` 信封；时间戳均为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
- `fund_type` 取 `otc`、`exchange` 或 `reits`；`thscode` 必须保留市场后缀并与基金类型匹配。持仓来自定期披露，不代表实时持仓。
:::
```text
GET /api/fund/portfolio/holdings
**MCP Tool**：[`get_fund_portfolio_holdings`](/docs/mcp/tools/get_fund_portfolio_holdings)
## 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | 基金类型，只允许单个值：`otc`（场外基金）、`exchange`（ETF、LOF）或 `reits`（公募 REITs）。 |
| `thscode` | string | 是 | — | 完整基金 thscode，必须保留市场后缀，并与 `fund_type` 对应，如 `025480.OF`。 |
## 响应示例
## 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 持仓股票的完整 thscode。 |
| `ticker` | string | 持仓股票的纯代码。 |
| `stock_name` | string | 资产名称；字段名为兼容既有契约而保留。 |
| `hold_ratio` | number | 占基金净值比例的百分数原值。 |
| `asset_type` | string | 资产类型，如 `stock` / `bond` / `fund`。 |
| `position_capital` / `position_count` | number | 持仓市值与持仓数量。 |
| `security_market_value_rate_pct` / `period_increase_rate_pct` | number | 证券市值占比与报告期增减比例。 |
| `investment_rank` | integer | 持仓排名。 |
| `start_date_ms` / `end_date_ms` / `publish_date_ms` / `modify_time_ms` | long | 报告期、发布日期与修改时间。 |
## 基金经理数据
> 查询基金经理投资风格、业绩、从业经历与详情
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`；认证与权限错误通过业务 `code` 表达。
- 本页接口返回统一 `ApiResponse` 信封；时间戳均为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
- `manager_id` 是基金经理 ID，可从基金基本资料返回值获取；收益率和占比字段为百分数原值。
:::
## 投资风格
```text
GET /api/fund/managers/investment-style
**MCP Tool**：[`get_fund_managers_investment_style`](/docs/mcp/tools/get_fund_managers_investment_style)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `manager_id` | string | 是 | — | 基金经理 ID。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `representative_fund_thscode` / `representative_fund_ticker` | string \| null | 代表基金完整代码与纯代码。 |
| `representative_fund_name` | string \| null | 代表基金名称。 |
| `investment_idea` | string \| null | 投资理念。 |
| `total_fund_scale` | number \| null | 管理基金总规模。 |
| `industry_preferences` | object \| null | 行业偏好，保留上游结构。 |
## 基金经理业绩
```text
GET /api/fund/managers/performance
**MCP Tool**：[`get_fund_managers_performance`](/docs/mcp/tools/get_fund_managers_performance)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `manager_id` | string | 是 | — | 基金经理 ID。 |
| `range` | enum | 是 | — | `month` / `tmonth` / `year` / `nowyear` / `now`。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `date_ms` | long | 数据日期，毫秒 Unix 时间戳。 |
| `manager_return_pct` | number | 基金经理收益率，百分数原值。 |
| `peer_return_pct` | number | 同类收益率，百分数原值。 |
| `benchmark_return_pct` | number | 基准收益率，百分数原值。 |
## 从业经历
```text
GET /api/fund/managers/experience
**MCP Tool**：[`get_fund_managers_experience`](/docs/mcp/tools/get_fund_managers_experience)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `manager_id` | string | 是 | — | 基金经理 ID。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `awards` | object | 获奖经历，保留上游结构。 |
| `heavy_assets` | object | 代表性重仓资产，保留上游结构。 |
| `investment_history` | object | 投资与从业经历，保留上游结构。 |
## 基金经理详情
```text
GET /api/fund/managers/detail
**MCP Tool**：[`get_fund_managers_detail`](/docs/mcp/tools/get_fund_managers_detail)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `manager_id` | string | 是 | — | 基金经理 ID。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `manager_id` / `manager_name` | string | 基金经理 ID 与姓名。 |
| `sex` / `degree` | string \| null | 性别与学历。 |
| `company_id` / `company_name` | string \| null | 所属基金公司 ID 与名称。 |
| `resume` / `photo_url` | string \| null | 履历与头像链接。 |
| `annual_return_pct` / `maximum_return_pct` | number \| null | 年化收益率与最大收益率。 |
| `radar_comparison` | array | 雷达图对比数据。 |
## 基金行情数据
> 查询场内基金行情快照与场内基金历史日线行情
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`；认证与权限错误通过业务 `code` 表达。
- 本页接口返回统一 `ApiResponse` 信封；时间戳均为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
- 行情接口仅接收带市场后缀的单只 ETF `thscode`，不接收 `fund_type`；价格字段按原始货币计价。
:::
## 场内基金行情快照
```text
GET /api/fund/market/snapshot
**MCP Tool**：[`get_fund_market_snapshot`](/docs/mcp/tools/get_fund_market_snapshot)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `thscode` | string | 是 | — | 单只 ETF 的完整 thscode，必须保留市场后缀，如 `510300.SH`；不接受逗号分隔的多个值。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | ETF 的完整 thscode。 |
| `ticker` | string | ETF 的纯基金代码，仅用于展示。 |
| `last_price` | number | 最新价。 |
| `open_price` | number | 开盘价。 |
| `high_price` | number | 最高价。 |
| `low_price` | number | 最低价。 |
| `prev_price` | number | 昨收价。 |
| `price_change_ratio_pct` | number | 涨跌幅，百分数原值。 |
| `price_change` | number | 涨跌额。 |
| `price_amplitude_ratio_pct` | number | 振幅，百分数原值。 |
| `volume` | number | 成交量。 |
| `turnover` | number | 成交额。 |
| `turnover_ratio_pct` | number | 换手率，百分数原值。 |
## 场内基金历史日线行情
```text
GET /api/fund/market/historical
**MCP Tool**：[`get_fund_market_historical`](/docs/mcp/tools/get_fund_market_historical)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `thscode` | string | 是 | — | 单只 ETF 的完整 thscode，必须保留市场后缀；不接受逗号分隔的多个值。 |
| `interval` | string | 否 | `1d` | K 线周期，当前仅支持 `1d`（日线）。 |
| `start` | long | 是 | — | 起始时间，毫秒级 Unix 时间戳。 |
| `end` | long | 是 | — | 结束时间，毫秒级 Unix 时间戳；必须不早于 `start`，且窗口最长 5 个自然年。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 数据就绪时间，取序列中最新一根 K 线的有效时间。 |
| `thscode` | string | 请求中的 ETF thscode。 |
| `interval` | string | K 线周期，固定为 `1d`。 |
| `adjust` | null | 复权方式，当前固定为 `null`。 |
| `item` | array | 历史日线数据列表。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `date_ms` | long | 交易日期，毫秒级 Unix 时间戳。 |
| `open_price` | number | 开盘价。 |
| `high_price` | number | 最高价。 |
| `low_price` | number | 最低价。 |
| `close_price` | number | 收盘价。 |
| `volume` | number | 成交量。 |
| `turnover` | number | 成交额。 |
## 基金资讯列表
> 查询单只基金的资讯文章并使用游标分页
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`；认证与权限错误通过业务 `code` 表达。
- 接口返回统一 `ApiResponse` 信封；时间戳均为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
- `fund_type` 取 `otc`、`exchange` 或 `reits`；`thscode` 必须保留市场后缀。`offset` 是不透明游标，翻页时必须原样回传。
:::
```text
GET /api/fund/news/article-list
**MCP Tool**：[`get_fund_news_article_list`](/docs/mcp/tools/get_fund_news_article_list)
## 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc` / `exchange` / `reits`。 |
| `thscode` | string | 是 | — | 完整基金 thscode。 |
| `limit` | integer | 否 | 服务端默认 | 返回条数。 |
| `offset` | string | 否 | — | 不透明翻页游标；下一页应原样回传上一页的 `data.offset`。 |
## 响应示例
## 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | long | 接口响应时间戳。 |
| `limit` | integer | 本页返回条数上限。 |
| `offset` | string \| null | 下一页游标；继续翻页时原样回传。 |
| `has_more` | boolean | 是否还有下一页；分页结束统一以该字段为准。 |
| `item` | array | 资讯明细列表。 |
| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string | 资讯 ID。 |
| `content_type` | string | 内容类型。 |
| `title` / `summary` | string | 标题与摘要。 |
| `source` / `author` | string | 来源与作者。 |
| `url` / `image_url` | string \| null | 正文链接与图片链接。 |
| `publish_time_ms` | long | 发布时间，毫秒 Unix 时间戳。 |
| `top` | boolean | 是否置顶。 |
## 基金募集列表
> 查询当前募集或即将募集的新发基金
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`；认证与权限错误通过业务 `code` 表达。
- 接口返回统一 `ApiResponse` 信封；日期时间字段统一使用文档标注的格式，毫秒时间戳按 `Asia/Shanghai` 解释。
- `subscribe` 只接受 `active`（当前募集）或 `upcoming`（即将募集）。
:::
```text
GET /api/fund/offerings/list
**MCP Tool**：[`get_fund_offerings_list`](/docs/mcp/tools/get_fund_offerings_list)
## 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `subscribe` | enum | 是 | — | `active`（当前募集）或 `upcoming`（即将募集）。 |
## 响应示例
## 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 完整基金 thscode。 |
| `ticker` | string | 纯基金代码。 |
| `subscription_start_ms` | long | 募集开始时间，毫秒 Unix 时间戳。 |
| `subscription_end_ms` | long | 募集结束时间，毫秒 Unix 时间戳。 |
## 基金业绩与回撤
> 查询基金净值、区间收益、历史业绩指标与最大回撤
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`；认证与权限错误通过业务 `code` 表达。
- 本页接口返回统一 `ApiResponse` 信封；时间戳均为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
- `fund_type` 取 `otc`、`exchange` 或 `reits`；`thscode` 必须保留市场后缀。收益率、占比和回撤字段为百分数原值。
:::
## 基金净值
```text
GET /api/fund/performance/nav
**MCP Tool**：[`get_fund_performance_nav`](/docs/mcp/tools/get_fund_performance_nav)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc`（场外基金）/ `exchange`（ETF、LOF）/ `reits`（公募 REITs）。 |
| `thscode` | string | 是 | — | 完整基金 thscode，必须保留市场后缀。 |
| `range` | string | 否 | 最新一条 | `week` / `month` / `tmonth` / `hyear` / `year` / `twoyear` / `tyear` / `fyear`。 |
| `nav_type` | string | 否 | `unit,adj` | `unit`（单位净值）/ `adj`（复权净值）/ `unit,adj`（同时返回）。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `nav_date` | long | 净值日期，毫秒级 Unix 时间戳。 |
| `unit_nav` | number | 单位净值；未通过 `nav_type` 请求时不输出。 |
| `adj_nav` | number | 复权净值；未通过 `nav_type` 请求时不输出，不等同于累计净值。 |
## 基金区间收益
```text
GET /api/fund/performance/returns
**MCP Tool**：[`get_fund_performance_returns`](/docs/mcp/tools/get_fund_performance_returns)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc`（场外基金）/ `exchange`（ETF、LOF）/ `reits`（公募 REITs）。 |
| `thscode` | string | 是 | — | 完整基金 thscode，必须保留市场后缀。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `return_month` | number | 近一月收益率，百分数原值。 |
| `return_week` | number | 近一周收益率，百分数原值。 |
| `return_tmonth` | number | 近三月收益率，百分数原值。 |
| `return_hyear` | number | 近半年收益率，百分数原值。 |
| `return_year` | number | 近一年收益率，百分数原值。 |
| `return_twoyear` | number | 近两年收益率，百分数原值。 |
| `return_tyear` | number | 近三年收益率，百分数原值。 |
| `return_fyear` | number | 近五年收益率，百分数原值。 |
| `return_nowyear` | number | 今年以来收益率，百分数原值。 |
| `return_now` | number | 成立以来收益率，百分数原值。 |
| `peer_average_*` | number | 对应周期的同类平均收益率；周期后缀覆盖 `week`、`month`、`tmonth`、`hyear`、`year`、`twoyear`、`tyear`、`fyear`。 |
| `rank_*` / `rank_total_*` | integer | 对应周期的同类排名与参与排名总数。 |
## 基金历史业绩指标
```text
GET /api/fund/performance/indicators-historical
**MCP Tool**：[`get_fund_performance_indicators_historical`](/docs/mcp/tools/get_fund_performance_indicators_historical)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc` / `exchange` / `reits`。 |
| `thscode` | string | 是 | — | 完整基金 thscode。 |
| `start` | long | 是 | — | 起始时间，毫秒 Unix 时间戳。 |
| `end` | long | 是 | — | 结束时间，毫秒 Unix 时间戳。 |
:::caution 参数必填
`start` 和 `end` 均为必填参数。此前未传这两个参数的客户端需要补充起止时间后再调用。
:::
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `date_ms` | long | 指标日期，毫秒 Unix 时间戳。 |
| `rsi_pct` | number | RSI 指标值。 |
| `donchian_channel` | number | 唐奇安通道指标值。 |
| `track_index_pe_ttm_five_year_percentile` | number | 跟踪指数 PE TTM 五年分位。 |
## 基金最大回撤
```text
GET /api/fund/performance/drawdowns
**MCP Tool**：[`get_fund_performance_drawdowns`](/docs/mcp/tools/get_fund_performance_drawdowns)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc` / `exchange` / `reits`。 |
| `thscode` | string | 是 | — | 完整基金 thscode。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` / `ticker` | string | 完整基金代码与纯代码。 |
| `week` / `month` / `tmonth` | number | 近一周、近一月、近三月最大回撤。 |
| `hyear` / `year` / `twoyear` | number | 近半年、近一年、近两年最大回撤。 |
| `tyear` / `fyear` | number | 近三年、近五年最大回撤。 |
| `nowyear` / `now` | number | 今年以来、成立以来最大回撤。 |
## 基金持仓与资产配置
> 查询基金历史股票债券持仓、报告期、资产配置与行业配置
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`；认证与权限错误通过业务 `code` 表达。
- 本页接口返回统一 `ApiResponse` 信封；时间戳均为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
- `fund_type` 取 `otc`、`exchange` 或 `reits`；`thscode` 必须保留市场后缀。持仓来自定期披露，不代表实时持仓。
:::
## 基金历史股票持仓
```text
GET /api/fund/portfolio/stock-history
**MCP Tool**：[`get_fund_portfolio_stock_history`](/docs/mcp/tools/get_fund_portfolio_stock_history)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc` / `exchange` / `reits`。 |
| `thscode` | string | 是 | — | 完整基金 thscode。 |
| `report_type` | string | 是 | — | 报告类型。 |
| `end_date` | string | 是 | — | 报告截止日期，格式 `yyyy-MM-dd`。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` / `ticker` / `name` | string | 持仓标的完整代码、纯代码与名称。 |
| `asset_type` | string | 资产类型，股票持仓为 `stock`。 |
| `hold_ratio` | number | 持仓占比，百分数原值。 |
| `market_value` | number | 持仓市值。 |
| `period_increase_pct` | number | 报告期增减比例，百分数原值。 |
| `rank` | integer | 持仓排名。 |
| `report_type` | string | 报告类型。 |
| `end_date_ms` | long | 报告截止日期，毫秒 Unix 时间戳。 |
## 基金历史债券持仓
```text
GET /api/fund/portfolio/bond-history
**MCP Tool**：[`get_fund_portfolio_bond_history`](/docs/mcp/tools/get_fund_portfolio_bond_history)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc` / `exchange` / `reits`。 |
| `thscode` | string | 是 | — | 完整基金 thscode。 |
| `report_type` | string | 是 | — | 报告类型。 |
| `end_date` | string | 是 | — | 报告截止日期，格式 `yyyy-MM-dd`。 |
### 返回字段
## 基金股票持仓报告日期
```text
GET /api/fund/portfolio/stock-report-dates
**MCP Tool**：[`get_fund_portfolio_stock_report_dates`](/docs/mcp/tools/get_fund_portfolio_stock_report_dates)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc` / `exchange` / `reits`。 |
| `thscode` | string | 是 | — | 完整基金 thscode。 |
| `report_type` | string | 否 | — | 报告类型。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `report_type` | string | 报告类型。 |
| `report_type_name` | string | 报告类型中文名称。 |
| `start_date_ms` / `end_date_ms` | long | 报告期起止日期，毫秒 Unix 时间戳。 |
## 基金债券持仓报告日期
```text
GET /api/fund/portfolio/bond-report-dates
**MCP Tool**：[`get_fund_portfolio_bond_report_dates`](/docs/mcp/tools/get_fund_portfolio_bond_report_dates)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc` / `exchange` / `reits`。 |
| `thscode` | string | 是 | — | 完整基金 thscode。 |
| `report_type` | string | 否 | — | 报告类型。 |
### 返回字段
## 基金资产配置
```text
GET /api/fund/portfolio/asset-allocation
**MCP Tool**：[`get_fund_portfolio_asset_allocation`](/docs/mcp/tools/get_fund_portfolio_asset_allocation)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc` / `exchange` / `reits`。 |
| `thscode` | string | 是 | — | 完整基金 thscode。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `report_date_ms` | long | 报告日期，毫秒 Unix 时间戳。 |
| `stock_ratio_pct` | number | 股票资产占比，百分数原值。 |
| `bond_ratio_pct` | number | 债券资产占比，百分数原值。 |
| `deposit_ratio_pct` | number | 存款占比，百分数原值。 |
| `other_ratio_pct` | number | 其他资产占比，百分数原值。 |
## 基金行业配置
```text
GET /api/fund/portfolio/industry-allocation
**MCP Tool**：[`get_fund_portfolio_industry_allocation`](/docs/mcp/tools/get_fund_portfolio_industry_allocation)
### 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc` / `exchange` / `reits`。 |
| `thscode` | string | 是 | — | 完整基金 thscode。 |
### 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `report_period` | string | 报告期。 |
| `industry_name` | string | 行业名称。 |
| `ratio_pct` | number | 行业配置比例，百分数原值。 |
## 基金基本资料
> 查询基金名称、规模、净值、管理人与基金经理等基本资料
:::info 通用约定
- **Base URL**：`https://fuyao.aicubes.cn`。
- **必需请求头**：`X-api-key`；认证与权限错误通过业务 `code` 表达。
- 接口返回统一 `ApiResponse` 信封；时间戳均为毫秒级 Unix 时间戳，时区按 `Asia/Shanghai`。
- `fund_type` 取 `otc`、`exchange` 或 `reits`；`thscode` 必须保留市场后缀并与基金类型匹配。
:::
```text
GET /api/fund/profile/detail
**MCP Tool**：[`get_fund_profile_detail`](/docs/mcp/tools/get_fund_profile_detail)
## 请求参数
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|---|---|---|---|---|
| `fund_type` | string | 是 | — | `otc`（场外基金）/ `exchange`（ETF、LOF）/ `reits`（公募 REITs）。 |
| `thscode` | string | 是 | — | 完整基金 thscode，必须保留市场后缀，如 `025480.OF` / `510300.SH`。 |
## 响应示例
## 返回字段
| 字段 | 类型 | 说明 |
|---|---|---|
| `thscode` | string | 带市场后缀的同花顺代码。 |
| `ticker` | string | 纯基金代码，仅用于展示。 |
| `fund_name` | string \| null | 基金名称。 |
| `estab_date` | long \| null | 成立日期，毫秒时间戳。 |
| `company_id` | string \| null | 基金公司 ID，可用于查询基金公司详情。 |
| `mgmt_name` | string \| null | 基金管理人名称。 |
| `manager_name` | string \| null | 基金经理姓名。 |
| `fund_scale` | number \| null | 基金规模。 |
| `unit_nav` | number \| null | 单位净值。 |
| `manager_info` | array | 基金经理引用，包含经理 ID、姓名、任职收益、任职天数与起止时间。 |
| `trade_rule` | array | 交易规则，包含标题、展示时间与毫秒时间戳。 |
| `rate_info` | array | 费率信息，包含费率类型、收费模式、条件、标准费率与优惠费率。 |
