# Push2EX 昨日涨停池的采集缺口与日期边界

审计日期：2026-11-14<br>
范围：`东财-push2ex::yfbt`、`::ylbc`、`::y_first_seal`、`::y_limit_count`，以及对应昨日涨停池接口

## 保留期历史覆盖

按每个归档目录和 `meta.json.data_date` 一致且不早于 `20261015` 筛选后，检查了 18 个含 Push2EX raw 的不同数据日目录：`20261015`、`20261016`、`20261019`、`20261020`、`20261021`、`20261023`、`20261026`、`20261028`、`20261029`、`20261030`、`20261102`、`20261103`、`20261104`、`20261105`、`20261106`、`20261109`、`20261110`、`20261112`。没有读取保留起点前的 raw、ZHB 包或解析缓存。

18 个归档的 `source_as_of_dates.push2ex` 均缺失。其 `raw_push2ex.json` 根路径只有 `limit_up_pool`、`limit_down_pool`、`limit_broken_pool` 与 `scheme`；没有 `yesterday_limit_pool`，也没有 `y_first_seal` 或 `y_limit_count`。这是采集覆盖事实，不代表昨日池接口无数据或字段无效；历史归档也不能用于证明上游请求成功、缓存命中或来源实际日期。

## 现有适配器路径

项目适配器 [`stock_common/sc_datasource/_pools.py`](../../../stock_common/sc_datasource/_pools.py) 的 `get_yesterday_limit_pool(date_str)` 请求 `https://push2ex.eastmoney.com/getYesterdayZTPool`，读取 `data.pool`，并在 `_parse` 循环中将原始 `yfbt` 写入 `y_first_seal`、将 `ylbc` 写入 `y_limit_count`。同一返回对象的 `price`、`change_pct` 等字段描述请求交易日的表现，而 `y_first_seal` / `y_limit_count` 描述昨日状态，不能把整条列表简单标为一个未经核实的来源日期。

当前代码路径和名称可形成明确的待核映射：

| 上游键 | 项目适配器键 | 代码注释/目录线索 | 当前结论 |
|:---|:---|:---|:---|
| `yfbt` | `y_first_seal` | `get_yesterday_limit_pool` 注释为“昨封板时间” | 待日期对齐样本和官方页面值验证 |
| `ylbc` | `y_limit_count` | `get_yesterday_limit_pool` 注释为“昨连板数” | 待日期对齐样本和官方页面值验证 |

## 官方网页线索

[东方财富涨停板行情页](https://quote.eastmoney.com/ztb/)列出“昨日涨停股池”，其表格列名包括“昨日连板数”。该页面证明项目接口处于相同业务区域并给出展示字段名称，但页面没有展示原始键 `yfbt` / `ylbc` 或逐代码历史响应，因此这里只作为来源语义线索，不作为字段定案依据。访问时间：2026-11-14 23:16:05（Asia/Shanghai）；页面为当前动态页面，不提供 2026-11-12 历史快照。

## 采集调整与验证计划

日常 Push2EX collector 现调用已有适配器增加 `get_yesterday_limit_pool`，并将四个池接口拆为独立 `capture_units`。每个单元记录请求数据日、原始路径/结构和值指纹、状态和逻辑调用信息；适配器不提供来源日期回显时，`source_as_of_date` 保持空值。昨日池候选字段后续应按股票代码和交易日历，将目标日 T 的昨日字段与 T-1 的涨停池及官方页面逐条比较；只在确认该字段对应的实际数据日后，才纳入正式碰撞或定案。

该调整沿用项目 `get_yesterday_limit_pool` 适配器、全局限流和 `push2ex` 风险组限流，没有绕过采集器或另外发出网络请求。2026-11-14 为非交易日，本次没有运行采集脚本。首次新增样本只能由后续交易日的正常采集产生。

本记录不改变注册表，也不将 `yfbt`、`ylbc`、`y_first_seal`、`y_limit_count` 或 `HHMMSS` 定案。下次核验应先取得日期合格的原始路径和官方显示值；若只取得适配器输出，须保留原始键与解析键的映射证据，不能把项目注释当成独立官方定义。
