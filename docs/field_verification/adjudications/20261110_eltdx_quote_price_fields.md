# ELTDX 快照价格字段来源契约核验（2026-11-10）

## 范围

核验 `TDX-eltdx(适配层)` 的 `last_price`、`pre_close_price`、`open_price`、`high_price`、`low_price` 五个完整字段路径。只确认该来源内的字段语义，不建立跨源映射，也不更改采集路由。

## 证据

- 固定版本 [ELTDX v3.3.2 字段手册](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md) 在 `QuoteSnapshot` 和 `CategoryQuoteRecord` 两个模型中分别列出这五项，并解释为最新价、昨收、今开、最高、最低。
- [ELTDX v3.3.2 7709 分类行情文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-%E5%88%86%E7%B1%BB%E8%A1%8C%E6%83%85.md) 说明 `client.helpers.realtime_rank()` 是 `client.quotes.list_by_category()` 的分页整理，原始 `CategoryQuoteRecord` 行保留在采集的 `global_helpers.realtime_rank.rows[].raw`。
- 通达信官方 [`get_market_snapshot_batch`](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html) 字段表将 `LastClose`、`Open`、`Max`、`Min`、`Now` 分别定义为前收盘价、开盘价、最高价、最低价、现价。该接口只作语义交叉核对；没有据此声称它与 7709 是同一条协议路径。
- 保留采集 [`20261109/raw_eltdx.json`](../20261109/raw_eltdx.json)，SHA-256 `b64be87ccbfd9afaa8d758553d86da8f4a02559a1c52f13c7ca9d801f02b3123`：`global_helpers.realtime_rank.rows` 的 80/80 行以及 `stocks.*.quote_snapshot` 的 20/20 行均包含五个非空数值字段。记录路径与版本化模型一致。

## 裁决

五个字段均由 `unverified` 更新为 `verified_by_source_contract`，含义按上游字段手册登记。上游快照字段表没有明确价格单位，本次单位保持空白。字段路径来自同一 TDX 谱系，不新增 `mappings`，也不将它们作为独立来源证据。

决定文件：[`20261110_eltdx_quote_price_fields.json`](20261110_eltdx_quote_price_fields.json)。
