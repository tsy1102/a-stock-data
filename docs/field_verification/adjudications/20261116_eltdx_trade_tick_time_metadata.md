# ELTDX `TradeTick` 时间与序号元数据裁决

复核日期：2026-11-16。依据项目锁定的 ELTDX v3.3.2 客户端模型契约。本裁决确认模型字段，不将它们表述为 TDX 原始 wire 字段。

## 结论

| 注册身份 | 定案含义 | 边界 |
|---|---|---|
| `TDX-eltdx(适配层)::index` | 当前返回页内的成交记录序号；与 `absolute_index` 的服务端全局序号区分。 | 不代表完整历史序号，也不等同集合竞价 `AuctionPoint.index`。 |
| `TDX-eltdx(适配层)::time_minutes` | `TradeTick` 的分钟数时间属性，与 `time_label` 一同描述逐笔记录时间。 | 文档未明确分钟起算基准或 wire 编码；不推断具体数值转换、交易日期或时区。单位为分钟。 |
| `TDX-eltdx(适配层)::time_label` | `TradeTick` 的时间文本字段；09:25 正式撮合接口将其固定为 `09:25`。 | 不含来源日期，不能单独表示来源数据日；不与 `AuctionPoint.time_label` 合并。 |

## 证据与路径核对

- 项目来源参考 [`field_source_reference.md` §12.13.10E](../../field_source_reference.md) 将 `index`、`time_minutes`、`time_label` 列在 `TradeTick` 字段表；§12.13.10F 中竞价点路径则明确写作 `AuctionPoint.index`、`AuctionPoint.time_label`。注册身份按 `(source, 完整 code path)` 区分，本裁决不改动这些竞价点路径。
- 项目 [`requirements.txt`](../../../requirements.txt) 固定 `eltdx==3.3.2`。锁定版 [方法参考](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/METHOD_REFERENCE.md) 将 `TradeTick.index / absolute_index` 定义为页内序号 / 全局序号，并将 `time_minutes / time_label` 定义为分钟数 / 时间文本；锁定版[历史 09:25 正式撮合文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-%E5%8E%86%E5%8F%B20925%E6%AD%A3%E5%BC%8F%E6%92%AE%E5%90%88.md)确认该接口的 `time_label` 固定为 `09:25`。
- 按 `MIN_CAPTURE_DATE=2026-10-15` 检查 18 份保留期 `raw_eltdx.json`，覆盖 360 条股票记录；未发现成交页、逐笔 `ticks` 或撮合对象。当前采集入口及 TCP collector 中没有 `client.trades` 或 `client.auctions` 调用。因此本裁决只确认 ELTDX v3.3.2 的客户端返回模型语义，不声称当前采集器输出这些字段，也不使用保留边界前样本。
- `time_minutes` 的起算基准和 wire 编码没有在锁定版文档中说明，故不以常识或字段名补造精确换算；该字段仍不得作为来源日期证据。项目没有对这些字段建立 ZHB 碰撞或跨源映射，因为未发现具有相同事件模型和已确认来源日期的对应字段。

## 裁决范围

主字典将以上三个精确注册路径标记为 `verified_by_source_contract`。结论只覆盖 ELTDX 客户端 `TradeTick` 模型字段，不扩展到竞价点、分时点或其他同名路径；不改变采集逻辑、来源优先级或报告路由。
