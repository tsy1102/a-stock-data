# ELTDX 快照成交字段定案

## 定案范围

对 `TDX-eltdx(适配层)` 的 `total_hand`、`current_hand`、`inside_dish`、`outer_disc`、`open_amount_yuan` 五个字段做来源内契约核验，不建立跨源映射。

项目的 `quote_snapshot` 由 `client.quotes.get_snapshots()` 返回 `QuoteSnapshot`；`realtime_rank` 由 `client.helpers.realtime_rank()` 基于 7709 `0x054b` 分类行情整理，原始行保留在 `CategoryQuoteRecord` 路径。注册表按 `(source, code)` 定位字段，不能区分跨对象同名叶字段。本批四个成交量字段在两个上游模型中语义一致；`current_hand` 的单位未在 0x054c 快照契约中注明，因此只确认语义并保留空单位。`open_amount_yuan` 只在本项目 `QuoteSnapshot` 路径出现。

## 依据

- [ELTDX v3.3.2：7709 批量快照（0x054c）](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-%E6%89%B9%E9%87%8F%E5%BF%AB%E7%85%A7.md)：`total_hand` 为总成交量（手）、`current_hand` 为现手、`inside_dish` / `outer_disc` 为内盘 / 外盘（手）、`open_amount_yuan` 为开盘金额（元）。
- [ELTDX v3.3.2：7709 分类行情（0x054b）](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-%E5%88%86%E7%B1%BB%E8%A1%8C%E6%83%85.md)：说明 `realtime_rank()` 基于 `list_by_category()`，并将 `CategoryQuoteRecord.total_hand/current_hand/inside_dish/outer_disc` 定义为总成交量、现量、内盘、外盘，单位均为手。
- 2026-11-09 保留采集：20/20 个 `QuoteSnapshot` 均包含上述五项；`total_hand` 与同日 ELTDX 日 K `volume_lots` 的绝对差均小于 1 手，仅作同源数值尺度旁证。内盘与外盘相加只在 10/20 个样本中等于总量，因此不将其当作定案条件。

## 裁决

五条字段的来源内语义标为 `verified_by_source_contract`。`total_hand`、`inside_dish`、`outer_disc` 的单位登记为手，`open_amount_yuan` 登记为元；`current_hand` 单位留空。未把同源对象关系登记为跨源映射。决定文件为 [`20261109_eltdx_quote_snapshot_fields.json`](20261109_eltdx_quote_snapshot_fields.json)。
