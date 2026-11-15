# ELTDX `TradeTick.trade_datetime` 日期时间语义裁决

复核日期：2026-11-16。依据项目锁定的 ELTDX v3.3.2 模型/方法契约；本裁决只确认客户端模型层字段语义，不将其写成通达信原始 wire 协议定义。

## 结论

`TDX-eltdx(适配层)::trade_datetime` 是 `TradeTick` 中混合成交事件的事件时间字段。历史 `0x0fc6` 记录按指定交易日返回成交时间；固定版本的历史 09:25 正式撮合文档给出 `2026-08-14T09:25:00` 样例。该值包含事件日期与时刻，表达历史成交/撮合事件发生时间，不是采集运行时间。

当日 `0x0fc5` 原始响应不带交易日期；`TradePage.trading_date` 因此为空，`trade_datetime` 在当日接口通常为 `None`。因此它不能单独用于确认当日来源数据日。文档也未说明时区，字典不补造时区口径。

## 证据与路径核对

- 项目历史来源参考 [`field_source_reference.md` §12.13.10E](../../field_source_reference.md) 将此叶字段列在 `TradeTick` 的 19 字段表中；注册表旧身份据此对应 `TradeTick.trade_datetime`。
- 锁定版本 [ELTDX v3.3.2 历史 09:25 正式撮合文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-%E5%8E%86%E5%8F%B20925%E6%AD%A3%E5%BC%8F%E6%92%AE%E5%90%88.md)将 `trade_datetime` 明确定义为“指定交易日的成交时间”，并展示 `2026-08-14T09:25:00`。
- 锁定版本 [ELTDX v3.3.2 当日 09:25 正式撮合文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-%E5%BD%93%E6%97%A50925%E6%AD%A3%E5%BC%8F%E6%92%AE%E5%90%88.md)说明当日接口该字段通常为 `None`。
- [ELTDX v3.3.2 方法参考](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/METHOD_REFERENCE.md)区分 `TradePage.trading_date` 与 `TradeTick.trade_datetime`，并明确当日 `0x0fc5` 原始响应不带日期，所以 `TradePage.trading_date` 保持为空。
- 项目保留边界 `2026-10-15` 起的 18 个 `raw_eltdx.json` 均未出现 `trade_datetime` 键；当前采集代码也没有调用 `client.trades` 或 `client.auctions`。本结论不声称该路径由当前采集器输出，没有用边界前 raw 或 ZHB 补样，也没有做逐值碰撞。

## 裁决范围

主字典现记录该 ELTDX 模型字段的成交事件时间语义，状态为 `verified_by_source_contract`。这不确认当前项目有该字段的日常采集，不把它作为 `as_of_date` 或跨源碰撞输入，不新增任何 `mappings`。`trading_date` 仍需按其具体模型路径区分：`TradePage` 的历史查询日、`AuctionSeries` 的历史请求日期等同名属性不可合并成一个无上下文日期字段。
