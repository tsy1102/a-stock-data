# ELTDX 短线指标统一层字段定案

## 定案范围

核验 `CanonicalStockData.eltdx_*` 中 11 个来源尚未定案的投影字段。它们由 `core.data_provider.get_canonical_stock_data()` 从 `core.eltdx_adapter.get_eltdx_shortline_for_code()` 的批量缓存记录逐项映射；适配器优先合并 `ShortlineIndicator` 行，并允许同模型 `limit_ladder` 行兜底/覆盖。16 个保留日期中，两类记录同时存在的 12 个配对行在本批覆盖的 10 个底层指标字段上逐项一致。

本次只补字段语义、单位和投影路径；不改变取数、缓存 TTL、缓存键或数据结构。缺失/转换失败时，统一层沿用 `0`、空文本或 `False` 默认值；这些默认值不是上游确认的零值。`eltdx_has_shortline` 只表示适配器返回了非空记录，不证明记录中每个指标都有效。

## 字段映射

| 统一层字段 | 来源字段 | 定案含义 | 单位 |
|---|---|---|---|
| `eltdx_auction_prev_volume_ratio` | `auction_prev_volume_ratio` | 竞价成交量昨比 | 倍 |
| `eltdx_has_shortline` | `bool(non_empty_record)` | ELTDX短线记录可用标记 | — |
| `eltdx_ladder_level` | `ladder_level` | 当前连板高度 | 板 |
| `eltdx_limit_board_text` | `limit_board_text` | 几天几板文本 | 文本 |
| `eltdx_limit_up_streak_days` | `limit_up_streak_days` | 统计文件记录的连续涨停天数 | 天 |
| `eltdx_open_change_pct` | `open_change_pct` | 开盘涨幅 | % |
| `eltdx_open_prev_amount_ratio` | `open_prev_amount_ratio` | 开盘成交额昨比 | % |
| `eltdx_open_turnover_z` | `open_turnover_z` | 自由流通口径开盘换手率 | % |
| `eltdx_open_volume_ratio` | `open_volume_ratio` | 开盘量比 | 倍 |
| `eltdx_seal_amount` | `seal_amount` | 当前买一金额；仅已封板时解释为涨停封单额 | 元 |
| `eltdx_seal_to_float_ratio` | `seal_to_float_ratio` | 当前买一金额占自由流通市值Z比；仅已封板时解释为封板强度 | % |

`eltdx_seal_amount` 的历史字段名保留；其值是当前买一金额。未封板时它只是盘口买一金额，只有 `limit_status=sealed` 时才可解释为涨停封单额。对应 schema 注释已同步纠正。

`eltdx_seal_to_float_ratio` 也是当前买一金额相对自由流通市值Z的比例。只有当前已封板时，该值才代表封板强度。ELTDX 对百分比字段已乘以100；`open_turnover_z` 的 Z 不是统计学 Z-score。

## 保留未知项

`eltdx_opening_rush` 本轮不定案。ELTDX 文档只说明它取自 0x054b 原生分类行情字段，未给算法、单位或正负方向；但 `get_val_report.py::strategy_27_shortline_fund_strength` 将其大于零当作抢筹信号并参与排序。现有证据不足以支撑该业务解释，本次保留字段未验证状态，不改策略逻辑。后续应先追溯 0x054b 解码/官方字段口径，再决定是否继续使用。

来源依据：

- [ELTDX v3.3.2 短线指标契约](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/helpers/%E7%9F%AD%E7%BA%BF%E6%8C%87%E6%A0%87.md)
- 本项目 `stock_common/sc_schema.py`、`core/data_provider.py` 与 `core/eltdx_adapter.py` 的映射路径。

## 注册表结果

11 个统一层投影由 `unverified` 更新为 `verified`，状态只代表来源字段映射与文档语义已确认。`eltdx_opening_rush` 仍在未知队列；没有新增跨源映射或运行时行为变化。

决定文件：[`20261109_eltdx_unified_shortline_fields.json`](20261109_eltdx_unified_shortline_fields.json)。

## 2026-11-10 补充契约核验

后续核对 ELTDX v3.3.2 `FIELD_REFERENCE.md` 后，来源字段 `opening_rush` 的单位确认是百分比，且 `0x054b` 将它与 `min2_amount` 分别定义；详见 [2026-11-10 来源契约裁决](20261110_eltdx_volume_rush_locked_fields.md)。这只修正来源字段的单位和身份，未公开算法及正负方向仍不能证明统一层策略“正值即抢筹”的解释，因此 `eltdx_opening_rush` 的业务方向风险和策略状态不变。
