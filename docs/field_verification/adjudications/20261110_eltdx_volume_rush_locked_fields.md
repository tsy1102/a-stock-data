# ELTDX 成交量、开盘抢筹与买一金额字段定案

日期：2026-11-10<br>
范围：`TDX-eltdx(适配层)` 的 `volume_hand`、`opening_rush`、`locked_amount` 3 个完整来源路径。<br>
依据：固定版本 ELTDX v3.3.2 字段手册和 2026-11-09 留存的 `raw_eltdx.json`。本轮采集运行于 2026-11-10 04:27（开盘前），按 runbook 数据日规则复用 2026-11-09 目录；ZHB 包文件名日期为 2026-11-06，因此未用于以下裁决。

## 契约与样本结果

| 完整来源路径 | 官方/客户端契约结论 | 2026-11-09 样本核对 | 定案边界 |
|---|---|---|---|
| `TDX-eltdx(适配层)::volume_hand` | ELTDX `StockProfile.volume_hand` 为成交量，单位手；0x054b `CategoryQuoteRecord.total_hand` 为总成交量。 | `global_helpers.realtime_rank.rows` 80/80 行的 `volume_hand` 与同一行 `raw.total_hand` 完全相等。 | 确认来源内含义和单位；不映射到其他来源。 |
| `TDX-eltdx(适配层)::opening_rush` | 0x054b 将 `opening_rush` 与 `min2_amount` 分列；`ShortlineIndicator.opening_rush` 是分类行情的开盘抢筹值，单位 `%`。 | 80/80 行非空；均等于 `raw.opening_rush_raw / 100`。例如 `sz301718` 为 `-0.39`，而 `min2_amount` 为 `672512`。 | 更正旧的合并含义；算法及正负方向的业务解释仍未知，不据此判定买入/卖出信号。 |
| `TDX-eltdx(适配层)::locked_amount` | `CategoryQuoteRecord.locked_amount` 是派生字段 `bid1 × bid_vol1 × 100`；“量涨速”是另一字段 `vol_rise_speed`。 | 原始行没有直接名为 `locked_amount` 的键。项目 `seal_amount` 80/80 行与同记录 `raw.bid1 × raw.bid_vol1 × 100` 相等，仅作为公式一致性核对。 | 更正旧的混合规范名；定义为买一档挂单金额，单位元。不能把它解释为涨停总封单金额，也不声称捕获到独立原始键。 |

## 上游文档

- [ELTDX v3.3.2 字段手册](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md)：`StockProfileTable/StockProfile`、`CategoryQuoteRecord`、`ShortlineIndicator` 各节。
- [ELTDX v3.3.2 7709 分类行情文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-%E5%88%86%E7%B1%BB%E8%A1%8C%E6%83%85.md)：0x054b 排序键、解析字段及派生字段。

## 今日采集状态

标准采集命令于 2026-11-10 04:27 执行。当前为开盘前，默认数据日为最近完成交易日 2026-11-09。该日期下完整来源按 runbook 复用，ZHB 缺失/不完整项进行了补采；返回包名 `zhb_20261106.zip`，晚于目标交易日 1 个交易日，已保留并标为 partial，不用于本次字段裁决。此次没有覆盖既有 ELTDX 样本。

## 注册表写回

决策文件为 [`20261110_eltdx_volume_rush_locked_fields.json`](20261110_eltdx_volume_rush_locked_fields.json)。三项均只确认 `TDX-eltdx(适配层)` 来源内语义及已公开单位；没有新增跨源 `mappings`，没有改动采集、策略、缓存或运行路由。

`opening_rush` 的来源字段单位现已确认，但统一层 `eltdx_opening_rush` 在策略中用正值解释为抢筹信号的方向性仍未由上游公式证明，原策略风险记录继续有效。
