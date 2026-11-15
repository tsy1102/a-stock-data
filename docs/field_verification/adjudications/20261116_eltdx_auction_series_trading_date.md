# ELTDX `AuctionSeries.trading_date` 日期角色裁决

复核日期：2026-11-16。依据项目锁定的 ELTDX v3.3.2 客户端返回模型契约。本裁决确认日期字段的请求元数据角色，不将它用作来源实际数据日。

## 结论

`TDX-eltdx(适配层)::trading_date` 对应 ELTDX v3.3.2 `AuctionSeries.trading_date`：历史集合竞价查询时表示请求的历史日期；当日请求时为 `None`。它是请求日期标记，不单独证明服务器实际返回值对应的来源数据日，也不表示采集运行日期或事件日期。日期字符串格式未由字段手册明确规定。

## 证据与路径核对

- 项目来源参考 [`field_source_reference.md` §12.13.10F](../../field_source_reference.md) 在“集合竞价（AuctionSeries / AuctionPoint）”字段表中将未限定的 `trading_date` 列为 `AuctionSeries` 顶层字段；竞价点的其他字段按 `AuctionPoint.*` 明确加前缀。本裁决将该精确注册身份限定为 `AuctionSeries.trading_date`，不与成交页模型同名属性合并。
- 项目 [`requirements.txt`](../../../requirements.txt) 固定 `eltdx==3.3.2`。锁定版[字段手册](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md)说明 `AuctionSeries.trading_date` 是请求的历史日期、当日请求为 `None`；[方法参考](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/METHOD_REFERENCE.md)将该模型对应到 `client.auctions.series(code, date=None)`，并说明 `date` 用于请求指定历史日期。
- 按样本保留边界 `2026-10-15` 检查 18 份 `raw_eltdx.json`，覆盖 360 条股票记录；归档记录没有集合竞价 `AuctionSeries` 对象。当前采集器也没有调用 `client.auctions.series()`。因此本裁决只确认锁定版本客户端模型的字段角色，不声称现行采集器输出该字段，不用目录日期代替来源日期。
- 该字段是请求参数对应的日期元数据，不是已证明的来源级 `as_of_date`。本次不以 ZHB 或其他来源建立同义关系，不创建跨源映射，也不调整采集路由。

## 裁决范围

主字典将该精确来源路径标记为 `verified_by_source_contract`，含义限定为历史请求日期回显；日期格式、当前请求的 `None` 处理之外的接口行为及服务器实际数据日期仍不作推断。
