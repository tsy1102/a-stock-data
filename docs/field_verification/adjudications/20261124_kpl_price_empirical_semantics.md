# 开盘啦 W8 `price` 来源内语义核验

核验日期：2026-11-24。裁决目标仅为 `开盘啦(kpl)::price`，不创建跨源映射，也不据此认定开盘啦与东方财富接口可互相替代。

## 字段路径与现有状态

项目注册路径是 `开盘啦(kpl)::price`。适配器 `stock_common/sc_datasource/_pools.py::kpl_get_stock_list_w8()` 请求 `apphis.longhuvip.com` 的 `ZhiShuStockList_W8`，响应列表位于小写 `data.list`。固定提交版本的第三方解析记录把 `data.list[*][5]` 标为“价格”；它只用于定位数组位置，不作为开盘啦官方接口契约。开盘啦官网股票列表明确展示“现价”列。项目此前的注册表已填 `canonical=price`、`meaning=现价`、`unit=元`，但路径状态仍为 `unverified`，`status_resolution=aggregate_status_scope_unresolved`；属性冲突为空。

## 同日黄金锚核验

复核已留存的 [`20261122_kpl_pe_eastmoney_anchor_pairs.csv`](../research/20261122_kpl_pe_eastmoney_anchor_pairs.csv)，不请求接口、不运行采集器。该文件记录 KPL W8 响应 `Day=2026-11-20` 与东方财富官方 `stock/get` 行情价格的逐股配对。样本覆盖该次响应中的 23 个不同股票代码，数据日均为 `2026-11-20`；逐一以十进制定点数复算后，KPL `price` 与 Eastmoney `f43` 价格 **23/23 精确相等**，无缺失、重复代码或反例。完整代码、原值与差值见 CSV；其规范 LF SHA-256 为 `195fd09aa36aca910dc22da7c0b898e3ef62c5b79b5c39a078b886a35768cb8e`。

锚字段身份和单位已有项目证据：`东财-push2(stock/get)::f43` 已验证为现价、单位元；`stock_common/sc_datasource/_quotes.py` 将 `f43` 直接映射为 `price`，并注明 `fltt=2` 下以元计。东方财富价格因此是语义/单位锚；23 个同日精确配对同时验证了该 KPL 位置在本次样本中的解释。

## 裁决与边界

现有字段释义和单位都获得完整样本支持，本次只把精确路径 `开盘啦(kpl)::price` 定为“现价（元）”，元数据保持原值。一个数据日足以核验这批行情快照的价格角色；本裁决不据此推断其他数据日、盘中与盘后刷新边界，也不把页面标签当成接口公式契约。

证据链包含开盘啦官网的“现价”产品标签、固定版本第三方 W8 数组位置定位、项目实际请求适配器，以及 23 个同日样本与已验证 Eastmoney 黄金锚的精确核对。开盘啦未公开可查的 W8 键级 schema，因此其 API 内部字段定义仍以产品标签及完整样本实测建立来源内语义；第三方文档不是定案的唯一依据。

本决定只确认字段释义与元单位，不表示开盘啦和东方财富同源、具有替代关系或应删除任一采集源；也不推断当前项目每日采集器会请求该 W8 接口。

## 来源

- 项目请求入口：[`kpl_get_stock_list_w8()`](../../../stock_common/sc_datasource/_pools.py)；Eastmoney `f43` 到 `price` 的映射：[`_em_quote_full_impl()`](../../../stock_common/sc_datasource/_quotes.py)。
- 开盘啦官网首页股票列表的“股票名称 现价 涨幅”标签：[开盘啦首页](https://www.kaipanla.com/main/index.html)。
- W8 数组定位：[Rainynitesky/kaipanla-data-parser 固定提交 README](https://github.com/Rainynitesky/kaipanla-data-parser/blob/7bfae30ab420e10af816584b7aa77e21c25c9e14/README.md)，其中列出 `ZhiShuStockList_W8` 的 `[5]=价格`。该资料是第三方参考，不是官方 schema。
- 同日逐股值：[配对审计 CSV](../research/20261122_kpl_pe_eastmoney_anchor_pairs.csv)。
