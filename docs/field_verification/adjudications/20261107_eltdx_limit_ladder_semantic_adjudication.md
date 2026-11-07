# ELTDX `limit_ladder` 五字段历史重破解定案

定案时间：2026-11-07 07:15（Asia/Shanghai）  
证据记录：[`公开资料与历史样本复核`](public_web/20261107_public_web_research.md)  
候选审阅：[`18 条候选处置`](20261107_eltdx_limit_ladder_candidate_reviews.json)

## 结论

上游 `eltdx` 文档与本项目 2026-10-16 至 2026-11-04 保留的原始样本一致支持以下逐源语义。注册身份使用完整路径，不能折叠到同名短路径或另一个 `shortline` 路径。

| 完整路径 | 定案含义 | 单位 | 时效分类 |
|---|---|---|---|
| `limit_ladder.float_shares` | 普通流通股本，财务快照口径；等于 TDX 财务批次原始万股值乘 10,000 | 股 | `slow_changing` |
| `limit_ladder.free_float_shares` | 自由流通股本，TDX 自由流通口径；不等同于普通流通股本 | 股 | `slow_changing` |
| `limit_ladder.float_market_value` | 普通流通市值，普通流通股本乘当前行情价 | 元 | `daily_market` |
| `limit_ladder.free_float_market_value` | 自由流通市值，自由流通股本乘当前行情价 | 元 | `daily_market` |
| `limit_ladder.seal_amount` | 当前买一价乘买一量；仅在 `limit_status=sealed` 时解释为封单额 | 元 | `intraday_sensitive` |

12 条历史行中，前四项的来源内公式均逐值复核；封单额 12/12 符合买一价、买一手数和每手 100 股的金额公式，残差仅为小于约 `1.9e-9` 元的二进制浮点表示误差。五项的 `limit_ladder` 值与对应 `shortline` 字段在抽中 12 行逐值一致，但两者仍是不同完整路径；官方 Helper 文档明确 `limit_ladder` 返回一张含 `trade_date` 和 `ShortlineIndicator` 行的表。

## 跨源候选决定

- 普通流通股本与 Tencent `[72]/[76]` 的语义相符，历史数值只在 2/12 组完全一致，最大相对差约 `1.57e-7`。11/12 差值在 0.57 个 TDX float32 换算 ULP 内，1/12 为 1.36 ULP；由于精度与财务更新日并未逐条对齐，本轮将语义定案与数值映射分开，保留 `[72]` 候选等待外部证据，并将 `[76]` 合并为其已登记别名。**不新增严格逐值跨源映射。**
- 自由流通股本与 Tencent `[72]/[76]` 的普通流通股本语义不同；不建立映射。
- 封单额与 Tencent 委差、Sina 买一量、区间收益、量比和振幅是不同业务量/单位；7 条直接数值配对均拒绝。
- `float_market_value`、`free_float_market_value` 在本轮历史样本中没有待审跨源候选，按上游定义和来源内公式登记，不虚构跨源映射。

候选审阅工具按最新历史碰撞报告 SHA 校验 18 条候选，已写入项目审阅台账。报告里 5,649 条方法候选是自动生成的全量清单；本次人工定案范围是上述五个完整字段路径，不将全清单标成已审。

## 日期边界

本次 12 行的 `target_trade_date` 均与采集目录 `meta.data_date` 相同；`stats_date` 有 8 行为前一交易日，符合上游定义的统计资源对齐行为。ELTDX 在这些旧 `meta.json` 中没有 `source_as_of_dates.eltdx`，所以不把 `stats_date`、文件夹日期或财务 `updated_date` 混成同一种字段日期：股本归为慢变字段，市值归为日频，买一金额归为盘中敏感字段。样本里没有 2026-11-06 ELTDX 原始采集，本次结论不声称覆盖该日。

## 写入范围

在 `field_registry.json.source_fields` 中新增五条 `TDX-eltdx(适配层)` 完整路径，并用 E3 证据附录指向公开资料和历史复核记录；同步时效分类和生成的字段字典。未修改代码、缓存键或运行时数据路由；未改动旧 `eltdx::float_shares` 映射，也未把它冒充新完整路径的证据。
