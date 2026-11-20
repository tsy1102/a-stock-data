# Eastmoney IPO `TOTAL_ISSUE_NUM` 同源别名核验

复核日期：2026-11-21。

## 裁决

将 `东财-event_dc(IPO发行记录)::ipo_calendar[].TOTAL_ISSUE_NUM` 登记为 IPO 发行总股数，规范名 `ipo_total_issue_shares_wan`，单位“万股”。在本次留存的 20 条 `RPTA_APP_IPOAPPLY` 响应记录中，`TOTAL_ISSUE_NUM` 与已定案的 `ISSUE_NUM` 逐行完全相等；因此将它作为同一响应中的同值字段别名登记，不另建跨源映射。

证据边界：东方财富当前官方页面和前端明确把 `ISSUE_NUM` 绑定到发行总数；没有找到官方页面或脚本对 `TOTAL_ISSUE_NUM` 的独立字段标签。故本裁决说明它在本次完整留存响应样本中的同源别名关系，不声称东方财富公开了该键的独立 schema，也不外推接口未来版本。若未来同一来源的两个键出现差异，应重新核验别名关系。

## 官方定义与项目路径

- 东方财富[新股申购页](https://data.eastmoney.com/xg/xg/?mkt=zh)将列表列名标为“发行总数（万股）”。
- 东方财富官方前端脚本 [`xglist.js`](https://data.eastmoney.com/newstatic/js/xg/xglist.js) 对新股列表请求使用 `reportName: RPTA_APP_IPOAPPLY`，请求列包含 `ISSUE_NUM`，不包含 `TOTAL_ISSUE_NUM`。
- 官方详情页脚本 [`xgdetail.js`](https://data.eastmoney.com/newstatic/js/xg/xgdetail.js) 使用 `info.ISSUE_NUM` 渲染“总发行数量”，并将 `ONLINE_ISSUE_NUM` 单独渲染为“网上发行数量”。这与已定案的 `ISSUE_NUM` 释义及字段边界一致。
- 项目 [`_events.py`](../../../stock_common/sc_datasource/_events.py) 将 `ipo_calendar` 路由至 `RPTA_APP_IPOAPPLY`，默认由 [`_eastmoney.py`](../../../stock_common/sc_datasource/_eastmoney.py) 请求全部列；[`_datacenter.py`](../../../stock_common/sc_datasource/_datacenter.py) 将 `result.data[*]` 响应行原样返回。采集路径为：`RPTA_APP_IPOAPPLY response.data[*].TOTAL_ISSUE_NUM -> ipo_calendar() -> raw_event_dc.ipo_calendar[].TOTAL_ISSUE_NUM`，没有对该键重命名或换算。
- `ISSUE_NUM` 已按官方页面和发行人资料定案为发行总股数、单位万股，历史数值存在已记录的精度差异。参见[前次定案](20261120_eventdc_ipo_issue_fields.md)。

## 留存样本

原始归档 `docs/field_verification/20261119/raw_event_dc.json` 的数据目标日为 2026-11-19，采集自然日为 2026-11-20。对该响应中全部 20 条 IPO 记录逐行比较：两字段均有值 20/20，精确相等 20/20，反例 0，双方各有 19 个不同取值。股票与逐行原值见[完整样本表](../research/20261121_eventdc_total_issue_num_samples.csv)。

| 股票 | 申购日期 | `ISSUE_NUM` | `TOTAL_ISSUE_NUM` | 结果 |
|---|---|---:|---:|---|
| 平安银行（000001） | 1989-03-10 | 67.5 | 67.5 | 相等 |
| 万科A（000002） | 1988-12-28 | 2800 | 2800 | 相等 |
| 深振业A（000006） | 1991-12-01 | 69 | 69 | 相等 |
| 全新好（000007） | 1989-01-01 | 300 | 300 | 相等 |
| 其余 16 条 | 详见完整样本表 | 全部有值 | 全部有值 | 16/16 相等 |

文件摘要：

- 原始响应 SHA-256：`41fe019b29d038e1cf4726f69700af303aae0206a6fdb8d7399912290065b091`
- 完整逐行样本 CSV SHA-256：`6406b8e9c11c63cb568099d78b4df32ba5919f61c3cc5bb9fdb5e63f99d7da9f`
- 核查时官方 `xglist.js` SHA-256：`e4fec5ac510df518f434fb050319e46ad3598c77fb536f72dd82fdf18f8b0655`
- 核查时官方 `xgdetail.js` SHA-256：`e681def470ece2ae827fd9a870baf108e692f8020d48d316ef45d5108c9aeeef`

## 关系与适用范围

主注册表中已有旧式短路径 `event_dc.ISSUE_NUM -> event_dc.TOTAL_ISSUE_NUM` 的 `same_number_same_meaning` 关系。本次完整路径核验补足当前运行时身份；没有据旧关系单独推断语义，也没有把同源重复键误登记成独立提供方。

本次只定案 Eastmoney 的完整路径 `ipo_calendar[].TOTAL_ISSUE_NUM`。它继承官方 `ISSUE_NUM` 的业务语义和单位，观察到的同值关系限定于当前归档响应。该证据不证明其他接口、其他来源或未来 API 版本也使用相同字段。
