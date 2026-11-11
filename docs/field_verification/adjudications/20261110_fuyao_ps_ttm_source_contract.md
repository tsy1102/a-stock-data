# Fuyao `valuation.ps_ttm` 来源契约定案

日期：2026-11-10<br>
来源身份：`同花顺-fuyao::valuation.ps_ttm`<br>
裁决类型：来源契约确认；不新增跨源映射

## 结论

该字段是 Fuyao 最新估值快照中的 **TTM 市销率**，数值单位为倍。官方接口将返回路径列为 `data.item[].ps_ttm`，并说明 TTM 通常按最近四个季度计算。

来源日期仍未确认。接口不提供历史估值；响应 `data.timestamp` 表示上游指标元数据的最大有效时间，官方说明它不代表所有指标完全同步。当前项目适配器仅向上层返回 `item`，统一层检查的 `as_of_date` 和 `source_as_of_date` 因而缺失。不得把采集文件夹日期当作 Fuyao 估值字段的数据日期。

## 证据

- [同花顺金融数据 API：估值数据](https://fuyao.aicubes.cn/docs/api-reference/valuations/) 将 `data.item[].ps_ttm` 定义为市销率 TTM，并说明该接口是最新估值快照、不提供历史估值；`data.timestamp` 是上游指标元数据的最大有效时间，不能代表各指标同步更新。
- 项目 `stock_common.sc_fuyao.get_fuyao_valuation` 原样返回估值响应的 `item`；`core.data_provider` 将条目中的 `ps_ttm` 投影为统一数据字段，没有单位换算。
- 2026-11-10 post-capture 对撞报告记录 Fuyao 字段与 `ulist239.f130` 的探索关系覆盖 20 只股票、6 个采集日期、120 个值；本轮来源日期未确认，结果没有通过 L1 日期门槛，因此不能据此宣告相同数值。

## 处置边界

注册表只把该 Fuyao 路径的含义和单位改为来源契约已确认。既有 Fuyao/Ulist 关系不由本记录升级或改写；`ulist239.f130` 的自身定义仍依据其独立记录。本决策也不改变运行路由、缓存或缓存键。
