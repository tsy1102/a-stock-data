# ELTDX 分类行情字段定案

## 定案范围

对 `TDX-eltdx(适配层)` 的 10 个分类行情字段做来源内契约核验：`bid1`、`ask1`、`bid_vol1`、`ask_vol1`、`change_pct`、`depth`、`min2_amount`、`rise_speed`、`short_turnover`、`vol_rise_speed`。不建立跨源映射。

ELTDX v3.3.2 文档说明 `client.helpers.realtime_rank()` 基于 7709 `0x054b` 分类行情接口，原始 `CategoryQuoteRecord` 行被保存在 `global_helpers.realtime_rank.rows[].raw`；`change_pct` 是包装行中的派生值。注册表字段按 `(source, code)` 定位，本批 10 个字段在今天采集的分类行情中各自只有这条对应路径，没有同名冲突对象。

## 依据

- [ELTDX v3.3.2：7709 分类行情（0x054b）](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-%E5%88%86%E7%B1%BB%E8%A1%8C%E6%83%85.md)：说明 `realtime_rank()` 与 `CategoryQuoteRecord` 的关系，列出买卖一档、盘口深度、近两分钟金额、涨速、短周期换手、量增速等字段，并给出 `change_pct` 的计算公式。
- 2026-11-09 保留采集的 80 条 `realtime_rank` 行：上述 9 个原始字段均为 80/80 可见；`change_pct` 80/80 与 `(last_price - pre_close_price) / pre_close_price × 100` 完全一致，最大绝对差为 0。

## 字段结论

| 字段 | 定案语义 | 单位 |
|---|---|---|
| `bid1` / `ask1` | 买一 / 卖一价格 | 上游未注明 |
| `bid_vol1` / `ask_vol1` | 买一 / 卖一委托量 | 上游未注明 |
| `change_pct` | 涨跌幅，按公开公式由现价和昨收派生 | % |
| `depth` | 盘口强弱 / 盘口深度口径指标 | 上游未注明，算法未公开 |
| `min2_amount` | 近 2 分钟金额口径指标 | 上游未注明 |
| `rise_speed` | 涨速指标 | 上游未注明，算法未公开 |
| `short_turnover` | 短周期换手口径指标 | 上游未注明，窗口未公开 |
| `vol_rise_speed` | 量增速指标 | 上游未注明，算法未公开 |

## 裁决

10 条字段标为 `verified_by_source_contract`。`min2_amount`、`rise_speed`、`short_turnover`、`vol_rise_speed` 的旧合并占位释义通过 `metadata_correction` 留存，改为各自完整源字段契约。未为未公开的公式、窗口或单位补造信息，也未新增跨源映射。决定文件为 [`20261109_eltdx_category_rank_fields.json`](20261109_eltdx_category_rank_fields.json)。
