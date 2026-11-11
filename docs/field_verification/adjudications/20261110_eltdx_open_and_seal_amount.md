# ELTDX 开盘金额与买一档金额定案

日期：2026-11-10<br>
范围：`TDX-eltdx(适配层)::open_amount`、`TDX-eltdx(适配层)::seal_amount`。<br>
样本：`docs/field_verification/20261109/raw_eltdx.json`，来自最近已完成交易日 2026-11-09 的收盘采集。

## 结论

| 字段 | 固定版本契约 | 11 月 9 日样本 | 裁决边界 |
|---|---|---|---|
| `open_amount` | `0x054b CategoryQuoteRecord.open_amount` 为开盘金额，单位元。 | 80/80 行均非空，且 `raw.open_amount = raw.open_amount_raw × 100`。 | 确认该来源路径；不与其他模型的 `open_amount_yuan` 建立别名。 |
| `seal_amount` | `ShortlineIndicator.seal_amount` 为当前买一档金额，单位元。 | 80/80 行均非空，且与 `raw.bid1 × raw.bid_vol1 × 100` 一致。 | 仅表示买一档挂单金额；不推断涨停总封单或封板状态，不建立跨源映射。 |

## 来源依据

- [ELTDX v3.3.2 7709 分类行情文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-%E5%88%86%E7%B1%BB%E8%A1%8C%E6%83%85.md)：`CategoryQuoteRecord.open_amount_raw`、`open_amount` 及单位。
- [ELTDX v3.3.2 字段手册](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md)：`ShortlineIndicator.seal_amount` 的业务含义和元单位。

## 采集边界

2026-11-10 04:27 执行标准采集时处于开盘前，故项目数据日为 2026-11-09。完整来源复用既有归档；ZHB 补采返回 `zhb_20261106.zip`，来源日期落后目标数据日，标记为 partial 且未用于本次定案。没有覆盖 11 月 9 日 ELTDX 原样本。

决策文件：[`20261110_eltdx_open_and_seal_amount.json`](20261110_eltdx_open_and_seal_amount.json)。只更新来源字段语义和单位，不改运行代码、缓存行为或跨源映射。
