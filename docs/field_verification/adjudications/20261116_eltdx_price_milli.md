# ELTDX `TradeTick.price_milli` 价格缩放语义裁决

复核日期：2026-11-16。依据项目锁定的 ELTDX v3.3.2 客户端模型契约。本裁决确认模型字段的价格缩放，不将其表述为通达信原始 wire 字段定义。

## 结论

`TDX-eltdx(适配层)::price_milli` 对应 `TradeTick.price_milli`，表示成交价格的千分值：字段数值除以 1000 还原模型中的价格，单位为千分之一元。ELTDX v3.3.2 历史 09:25 示例给出 `price=11.22`、`price_milli=11220`，与该转换一致。

## 证据与边界

- 项目来源参考 [`field_source_reference.md` §12.13.10E](../../field_source_reference.md) 将该注册路径列于 `TradeTick` 字段表，旧释义为“成交价(毫)”；身份按注册表中的精确 `(source, code)` 维护。
- 项目 [`requirements.txt`](../../../requirements.txt) 固定 `eltdx==3.3.2`。[该版本字段手册](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md) 的通用约定说明 `*_milli` 是毫厘价格，通常 `price = price_milli / 1000`；[方法参考](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/METHOD_REFERENCE.md) 将 `TradeTick.price / price_milli` 列为成交价 / 毫厘价。
- [历史 09:25 正式撮合文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-%E5%8E%86%E5%8F%B20925%E6%AD%A3%E5%BC%8F%E6%92%AE%E5%90%88.md) 的真实返回示例为 `price=11.22`、`price_milli=11220`，独立验证了 1000 倍缩放。
- 按保留边界 `2026-10-15` 只读检查 18 份 `raw_eltdx.json`，未发现 `price_milli` 键；当前 ELTDX 采集器也未调用 `client.trades` 或 `client.auctions`。本裁决不声称该路径由现行采集器输出，不引用边界前 raw/ZHB，不建立跨源映射。
- 来源参考另有完整路径 `AuctionPoint.price_milli`。它是竞价点路径，不在本次未限定的 `TradeTick` 注册身份范围内；本裁决不合并这两个身份。

本次只定案 ELTDX v3.3.2 `TradeTick` 客户端模型字段的语义与缩放单位；不改变采集调用、不确认来源数据日或事件日期，也不提供跨源等价结论。
