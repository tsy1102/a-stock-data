# 开盘红 Levistock `industry_id` 字段别名来源内核验

复核日期：2026-11-20。精确字段身份：`开盘红(Levistock适配)::industry_id`。本裁决定义该适配器对开盘红 KPH 分类键的别名，不涉及开盘啦 KPL，也不建立跨源映射。

## 裁决

将该字段登记为规范项 `industry_id`，含义为：**开盘红接口返回的行业分类 ID，作为 KPH 自身记录的分类键**。具体分类体系和层级未公开；本定义不意味着该 ID 与 KPL `sector_code` 等价，也不推断它对应任何特定行业标准。单位不适用。

## 路径证据

本项目 [`_kph.py`](../../../stock_common/sc_datasource/_kph.py) 对开盘红 `HisDaBanList` 响应将 `row[26]` 映射为 `industry_id`。固定版本的独立 Levistock 客户端调用同一开盘红历史主机和动作，将同一 `row[26]` 映射为 `industry_id`，并注释为“行业ID”。因此 `开盘红(Levistock适配)::industry_id` 是同一 KPH 响应位置的客户端别名。[固定版本源码](https://github.com/fleetinglife/levistock/blob/808d8187a6dd2a781dc51efeb1581f35d68e66c7/levistock/stock/stock_daban_his_kph.py)

开盘红官网[盘后复盘教程](https://www.kaipanhong.com/article/42661) 使用板块分类观察当日涨停股数量，为接口中的分类键提供产品语境；页面没有公开 `industry_id` 的编号体系或层级，故本裁决仅确认它是 KPH 自身的行业分类 ID，不进一步命名标准。

## KPH 样本

2026-11-16、17、18 三个不同来源交易日的 KPH 完整分页样本共 103 条记录、43 个来源日与 `industry_id` 分组。逐组样本均有对应分类码，同组记录重复携带该分类码；这些值用于确认该字段在本接口中作为记录分类键。样本没有与 KPL `sector_code` 做语义推断，分类代码体系及层级仍未知。捕获于 11 月 19 日而来源日仍为 11 月 18 日的重复样本未计作新来源日。逐组样本见[样本 CSV](../research/20261120_kph_industry_limit_up_count_group_samples.csv)。

## 与 KPL 的边界

KPH（开盘红）和 KPL（开盘啦）是不同产品、官网、接口主机和来源族。本裁决仅依据 KPH 接口行映射、KPH 样本和开盘红官网材料，不使用 KPL 值确认 `industry_id`，不新增 `mappings`，不改变采集路由。

## 证据边界

- 已确认：`开盘红(Levistock适配)::industry_id` 是 KPH `HisDaBanList` 的 `row[26]` 分类 ID 别名。
- 仍未知：分类体系、行业层级、编号规则以及与其他来源编码的等价关系。
- 不据此裁定 KPL `sector_code` 与 KPH `industry_id` 同源或普遍逐值等价。
