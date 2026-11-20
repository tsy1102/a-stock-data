# 开盘红 Levistock `industry_zt` 字段别名来源内核验

复核日期：2026-11-20。精确字段身份：`开盘红(Levistock适配)::industry_zt`。本裁决只定义该适配器对开盘红 KPH 字段的别名，不涉及开盘啦 KPL，也不建立跨源映射。

## 裁决

将该路径登记为开盘红自身字段 `kph_industry_limit_up_count`：**按开盘红接口自身 `industry_id` 分类关联的当日涨停股票家数**，单位“家”。接口未公开确切统计全集与行业分类体系；部分计数大于该接口当前完整分页响应中该分类的返回行数，因此不把它解释成当前响应分组长度，也不外推为全市场完整行业总数。

## 路径和语义证据

本项目 [`_kph.py`](../../../stock_common/sc_datasource/_kph.py) 对开盘红 `HisDaBanList` 响应将 `row[26]` 映射为 `industry_id`、`row[27]` 映射为 `industry_limit_up_count`。固定版本的独立 Levistock 客户端调用同一开盘红历史接口（主机 `apphis.kaipanhong.com`，动作 `HisDaBanList`），把相同的 `row[26]` 和 `row[27]` 分别映射为 `industry_id` 与 `industry_zt`，并注释为“同行业涨停数”。这证明该注册路径是同一 KPH 响应位置的客户端别名；第三方命名本身不冒充官方 API 契约。[固定版本源码](https://github.com/fleetinglife/levistock/blob/808d8187a6dd2a781dc51efeb1581f35d68e66c7/levistock/stock/stock_daban_his_kph.py)

开盘红官网[盘后复盘教程](https://www.kaipanhong.com/article/42661) 解释同一板块内的涨停家数，并举例一个板块有 5 只涨停股。这确认产品级业务语义类别和单位，与 KPH `industry_id` 分类下的计数相符；教程没有给出 API 原始列到页面指标的正式映射，因此统计全集仍列为未知。

## KPH 样本核对

使用开盘红 KPH `HisDaBanList` 在 2026-11-16、17、18 三个不同来源交易日的完整分页快照。项目适配器的 `row[27]` 即 `industry_limit_up_count`，与 Levistock `industry_zt` 指向相同响应位置；样本不是另行调用 Levistock 取得。103 条记录分属 43 个“来源日 × `industry_id`”组，43/43 组内计数一致。38/43 组的值等于当前 KPH 返回列表中该组行数，另 5 组计数较大，证明其统计全集不能简单等同本次接口返回行数。捕获于 11 月 19 日、来源日仍为 11 月 18 日的重复快照不作为新来源日样本。逐组记录见[样本 CSV](../research/20261120_kph_industry_limit_up_count_group_samples.csv)。

## 与 KPL 的边界

KPH（开盘红）和 KPL（开盘啦）是不同产品、官网、接口主机和来源族。本裁决的接口路径、官网语义及样本都来自 KPH；没有使用 KPL 的 `col_20` 或其他数值解释 `industry_zt`，不新增任何 `mappings`，也不改变采集路由。`industry_id` 的正式分类体系和层级继续未知。

## 证据边界

- 已确认：`开盘红(Levistock适配)::industry_zt` 是 KPH 历史接口 `row[27]` 的客户端别名；其来源内业务角色为按 KPH 自身 `industry_id` 分类关联的当日涨停股票家数，单位“家”。
- 仍未知：KPH 计数全集、行业分类体系及层级；不能由该字段推断当前返回列表外每只股票的归属。
- 未确认：与 KPL `col_20` 或其他来源字段逐值同义；本次未建立跨源映射。
