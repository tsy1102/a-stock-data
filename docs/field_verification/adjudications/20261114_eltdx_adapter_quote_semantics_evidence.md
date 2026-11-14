# ELTDX 适配层实时行情 `price` / `amount` 来源内实证定案

- 复核日期：2026-11-14
- 目标身份：`TDX-eltdx(适配层)::price`、`TDX-eltdx(适配层)::amount`
- 证据类型：来源路径审计 + 固定版本模型契约 + 保留期同日交叉核验

## 裁决

- `price`：实时行情快照最新价；收盘阶段与该数据日收盘价一致，单位元。
- `amount`：实时行情快照累计成交额，单位元。

结论只确认这两个精确来源字段的语义，不登记 TDX 与腾讯之间的字段映射，也不把 ELTDX 视为独立于通达信的数据源。

## 项目路径与上游字段

`core/eltdx_adapter.py` 的 `_EltdxAdapter.quotes()` 调用固定版本 ELTDX 的 `client.quotes.get_snapshots([symbol])`。对返回的 `QuoteSnapshot`，适配器直接写入 `row["price"] = s.last_price` 和 `row["amount"] = s.amount`，没有单位换算、公式或中间重命名。路径分别为：

- `TDX-eltdx(适配层)::price` ← `QuoteSnapshot.last_price`
- `TDX-eltdx(适配层)::amount` ← `QuoteSnapshot.amount`

项目固定 ELTDX v3.3.2。该版本的 [`FIELD_REFERENCE.md §QuoteSnapshot`](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md#quotesnapshot) 将 `last_price` 释为“最新价”，`amount` 释为“成交额”。[`7709-批量快照`](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-%E6%89%B9%E9%87%8F%E5%BF%AB%E7%85%A7.md) 明确该模型来自当前 `0x054c` 快照，并将 `amount_raw` 说明为成交额 compact-float 原始值。ELTDX 是通达信协议客户端，不是数据提供方官方文档；本裁决将其用于确认项目运行路径和返回模型，再以腾讯独立样本验证实际字段意义与单位。

项目的 [`test_data_eltdx_adapter.py`](../../../tests/data/test_data_eltdx_adapter.py) 构造 `QuoteSnapshot` 并检查适配器的盘口价格/数量直传。待裁决的两个基本键在适配器中同样是直接属性赋值，见 [`core/eltdx_adapter.py`](../../../core/eltdx_adapter.py) `_EltdxAdapter.quotes()`。

## 来源日期与样本资格

只使用 2026-10-15 起保留期内同时存在 `raw_eltdx.json`、`raw_tencent.json`、`meta.json` 的样本，不读更早 raw、ZHB 包或解析缓存。逐日核验 `meta.data_date` 与目录一致，Tencent `as_of_date` 等于目标数据日；原始 Tencent 行字段 `[30]` 的时间戳日期也逐样本等于目标数据日。TDX `quote_snapshot` 本身没有单独 `as_of_date`，因此不把目录日期直接当作它的来源日期：每个样本另检查了同一 TDX 记录的 `kline_day` 是否含目标数据日 K 线，并将报价与该 K 线收盘/成交额及带明确来源日期的 Tencent 行核对。18 个目标数据日均处于收盘行情阶段，覆盖 2026-10-15 至 2026-11-12 的 18 个交易日；共 20 只股票、360 组逐股同日记录。

## 对照结果

| 检查 | 结果 | 解释 |
|:--|--:|:--|
| Tencent 原始时间戳日期 = `data_date` | 360 / 360 | 每个腾讯行情观测的实际日期均明确 |
| TDX 同一股票存在目标日 K 线 | 360 / 360 | 用来源记录自身的交易日字段辅助确认目标日期 |
| `quote_snapshot.last_price` = Tencent 字段 `[3]` 最新价 | 360 / 360 | 所有股票、数据日精确相等 |
| `quote_snapshot.last_price` = 同日 TDX K 线 `close` | 360 / 360 | 收盘样本与目标日收盘字段精确相等 |
| `quote_snapshot.amount` = 同日 TDX K 线 `amount` | 360 / 360 | 同源快照成交额与同日累计成交额精确相等 |
| 正成交额样本与 Tencent `[57]` 对照 | 359 / 359 | `[57]` 的已验证口径为万元、保留 4 位；乘 10,000 转为元后，量级一致，最大相对差为 `1.6216e-7` |
| 可比值反例 | 0 | 未发现语义或单位反例 |

360 组中有 1 组（`20261015 / 600825`）双方成交额均为 0。依照恒 0 低信息量规则，该组不计入成交额语义比较；它仍计入价格检查。359 组正成交额的最大绝对差为 487 元，最大相对差为 `1.6216e-7`。本结论不假定或推导 compact-float 的具体舍入算法；单位判断主要依赖同日 TDX K 线 360/360 精确相等，并以独立 Tencent 字段的万元换算值验证元级量纲。Tencent 对照只报告实际观测误差，不将其包装成预先证明的协议精度阈值。

逐样本表：[20261114_eltdx_adapter_quote_samples.csv](../research/20261114_eltdx_adapter_quote_samples.csv)
CSV SHA-256：`942B736FAA87B00AAA3B99D9A30CD79995A2DC68318DB004BE0A23071AE1D3DE`

## 边界

- 本证据确认适配器输出 `price` / `amount` 的来源内语义和单位，不确认或修改其他字段。
- 腾讯只作为已登记的独立来源对照锚；不新增 `mappings`，不声明 TDX 与 Tencent 对所有行情字段的等价性。
- 上游把 `amount_raw` 标为 compact-float 原始值，但本次未审定该编码的具体量化/舍入算法；Tencent `[57]` 的展示精度也限制逐元比较。此证据不用于精确跨源等价映射。
- 来源独立性按 `source_lineage.json`：ELTDX 归入 Tongdaxin，Tencent 归入 Tencent，两者是不同来源族；只在本次逐字段数值核验中使用该独立性。
