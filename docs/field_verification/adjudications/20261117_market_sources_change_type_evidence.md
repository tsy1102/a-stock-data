# `market_sources::change_type` 查询参数回显核验

复核日期：2026-11-17

## 结论范围

本记录只解释注册表身份 `市场源(market_sources)::change_type` 在项目 `market_sources.stock_changes_8201` 采集单元中的含义。它不是对 `getAllStockChanges` 全部 `type` 代码表的裁决，也不证明采集记录的来源实际数据日。

结论：该字段是项目适配器把请求参数 `change_type` 逐条写回结果时生成的“异动类型请求代码”。当前采集单元固定请求字符串 `8201`；项目代码注释将 `8201` 对应为“火箭发射”。官方东方财富盘口异动页面也列出“火箭发射”类别，但页面没有公开该类别与数值代码 `8201` 的接口映射，因此本记录不把完整代码映射或其他代码值定案。

## 代码路径

- [`scripts/capture_catalog.py`](../../../scripts/capture_catalog.py) 将 `market_sources.stock_changes_8201` 登记为 `stock_common.get_stock_changes(8201)`，原始输出路径为 `stock_changes_8201`。
- [`stock_common/sc_datasource/_quotes.py`](../../../stock_common/sc_datasource/_quotes.py) 的 `get_stock_changes(change_type)` 将参数放入请求参数 `type`，随后创建记录时直接写入 `"change_type": change_type`。该输出值来自适配器参数回显，不是从上游 `allstock` 记录读取的独立字段。
- 同一函数注释把 `8201` 标为“火箭发射”。东方财富官方[盘口异动页面](https://quote.eastmoney.com/changes/?from=ztzt)的“当日盘口异动详情”类别中列有“火箭发射”。官方页面只支持类别名称存在，不作为 `8201` 数值代码的正式接口字典。

## 保留样本核验

样本文件：`docs/field_verification/20261116/raw_market_sources.json`，精确路径 `stock_changes_8201[].change_type`；元数据：`docs/field_verification/20261116/meta.json`。

- `meta.json` 的请求目标数据日为 `2026-11-16`，市场阶段为 `closed`，采集时段为 `2026-11-16T21:27:33+08:00` 至 `21:27:34+08:00`。
- 该采集单元没有来源实际日期（`source_as_of_date=null`）。原始记录中的 `date` 字段未用于推断来源数据日。
- 采集返回 567 条异动记录，涉及 275 个不同股票代码；567/567 条记录的 `change_type` 均为字符串 `"8201"`，没有反例。
- 原始文件 SHA-256：`9AEA7AB90EE8BD806B2F02A4F41E692F593E92B8950F5FDD1C5928A4AD83BD4A`。
- 元数据文件 SHA-256：`B8F155AD12D4E0785A2B5FF20205AC2E0AF472729CFB804ADCEF75B171FDB0FC`。

这些记录用于核实参数回显和适配器输出，不作为 567 个独立日期样本，也不作为跨源碰撞或新鲜度证据。重复股票行仍保留为不同异动记录；股票数只报告去重代码数量。

## 字段释义边界

- 规范名保持 `change_type`；含义限定为“盘口异动类型请求代码回显”。对当前采集单元，代码为字符串 `8201`，项目标注为“火箭发射”。
- 单位记为“字符串代码”，不是数量或涨幅。
- 该字段在此采集单元内为常量，后续不应作为待破解业务数值或跨源碰撞锚；若将来启用其他 `change_type`，须对各请求类型分别核对，不从 `8201` 外推整个代码表。
- 本次不确认 Eastmoney 记录的来源实际日期，不改变来源血缘，不建立跨源映射，也不声称官方公开了 `8201` 的接口枚举定义。
