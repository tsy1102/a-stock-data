# ELTDX `limit_ladder` 历史重破解第二轮

## 范围

本轮使用项目明确保留起点 `2026-10-15` 之后的样本。正式全历史报告为 [`user_recrack_post_alias_review`](../20261107/user_recrack_post_alias_review/20261107_collision_report.json)，SHA-256：`9ea823052928a1744a6ce73b9b746b99e6bd9f2f8ffa2ea2a93e0f04e2e5d5f8`。报告完整，扫描 21 个采集目录、16 个交易日窗口、1,303 个字段身份和 1,026,686 条样本值；输出 4,337 条方法候选、142 条前沿候选、50 条 L4。完整报告不代表所有自动方法候选都已人工审阅。

原始 ELTDX 数据最新到 `2026-11-05`；`2026-11-06` 目录只有历史报告，没有该日 `raw_eltdx.json`。因此本轮不能声称核验了 11 月 6 日的采集值。ELTDX `limit_ladder` 前沿样本为 6 只股票、9 个交易日、12 组配对；日期采用碰撞器现有快照加载规则，本轮没有新增 ELTDX 来源日期见证，也没有据此建立逐值映射。

## 上游契约与精确身份

本项目路径为 `raw_eltdx.json → global_helpers.limit_ladder.rows[*]`，注册时使用来源 `TDX-eltdx(适配层)` 和完整路径。锁定的上游版本为 [`electkismet/eltdx@af471f1adf38757f6aa0188968db8110eb23f6ad`](https://github.com/electkismet/eltdx/tree/af471f1adf38757f6aa0188968db8110eb23f6ad)。上游字段手册逐项定义了 `beta_60d`、`pe_ttm`、`ladder_level`、`open_price`、`pre_close`；连板天梯 Helper 说明它们属于当前交易日的组合结果，开盘数据在 09:25 成交数据可用后提供。

这些证据确认的是 **ELTDX 适配层输出字段契约**，不是东方财富原始接口签发的字段规范。登记范围限于这五条完整路径，不推导其他同名路径，也不把同类指标自动变成跨源映射。[上游字段手册](https://github.com/electkismet/eltdx/blob/af471f1adf38757f6aa0188968db8110eb23f6ad/docs/FIELD_REFERENCE.md#L560-L608)、[上游连板天梯 Helper](https://github.com/electkismet/eltdx/blob/af471f1adf38757f6aa0188968db8110eb23f6ad/docs/helpers/%E8%BF%9E%E6%9D%BF%E5%A4%A9%E6%A2%AF.md#L177-L262)。

| 完整路径 | 本项目登记含义 | 单位 | 边界 |
|---|---|---|---|
| `limit_ladder.open_price` | 当前交易日开盘价 | 元 | 上游说明开盘数据通常在 09:25 后可用 |
| `limit_ladder.pre_close` | 当前交易日涨跌幅基准价，通常为昨收 | 元 | 按交易日作为基准，不把除权日调整参考价强行解释为未调整昨收 |
| `limit_ladder.pe_ttm` | 滚动市盈率，按最近 12 个月利润口径 | 倍 | 同属 TTM 概念不等于不同源逐值一致 |
| `limit_ladder.beta_60d` | 近 60 日相对上游所用市场基准的 Beta | 无量纲 | 依赖上游统计资源和统计日期 |
| `limit_ladder.ladder_level` | 当前连续封板高度 | 板 | 仅 `limit_status=sealed` 时有值 |

五个身份均以 E3 上游文档和保留期原始样本登记为 `verified` 源内语义，并退出未知字段队列；本轮没有改写缓存、路由或 `temporal_policy.json`，也没有新增 `mappings`。

## 高相关候选的逐对裁定

项目碰撞快照加载器按股票和交易日复算 12 组样本。以下候选来自方法相似度层，相关系数只是研究线索；逐值计数由项目的 `to_num` / `is_close` 复核。它们不属于本轮 L1 精确映射。

| 候选 | 历史值复核 | 处置 |
|---|---|---|
| `open_price ↔ Tencent[9]` | 12 组仅 1 组精确相等；最大相对差约 17.08%。上游左侧为集合竞价开盘价，注册表右侧 `[9]` 属于买卖盘口价量序列 | `rejected`：拒绝该具体直接映射；高横截面相关不能覆盖字段时点和业务含义差异 |
| `pre_close ↔ Tencent[9]` | 0/12 精确相等；最大相对差约 16.67% | `rejected`：交易日基准价不等于盘口买一 |
| `beta_60d ↔ Tencent[76]`、`beta_60d ↔ Tencent[73]` | 各 0/12；左侧无量纲，右侧分别为流通股本和总股本 | `rejected`：单位和业务含义不符 |
| `ladder_level ↔ Tencent[70]` | 0/12；左侧单位为板，右侧是 20 日涨跌幅百分比 | `rejected`：不同度量 |
| `pe_ttm ↔ Tencent[53]` | 0/12；左侧是 TTM，右侧已登记为静态/年报 LYR 市盈率 | `rejected`：计算期间不同，不能登记为同一字段 |
| `pe_ttm ↔ Tencent[39]` | 4/12 精确相等；其余 8 组不同，最大相对差约 18.76% | `needs_external_evidence`：两端均标为 TTM 概念，但差异远超舍入；不认定为近似等值或逐值映射，需进一步确认计算口径、统计日期和刷新时点 |

“拒绝”仅针对表中具体字段对的直接等值/映射，不否定右侧字段本身，也不把 `pe_ttm` 与 Tencent `[39]` 的同类语义关系抹除。`pe_ttm ↔ Tencent[39]` 保留为待外证候选；本报告没有近似证据层新增项，因为 18.76% 的偏差不能归入单位换算或舍入误差。

候选审查事件见 [`第二轮候选审阅 JSON`](20261107_eltdx_limit_ladder_second_pass_candidate_reviews.json)。本轮判断不表示 4,337 条方法候选已被穷尽人工审阅；完整报告审阅摘要和未审数量以重跑后的正式报告为准。
