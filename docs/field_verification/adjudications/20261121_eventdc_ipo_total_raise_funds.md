# Eastmoney IPO `TOTAL_RAISE_FUNDS` 定案

复核日期：2026-11-21。

## 定案

将 `东财-event_dc(IPO发行记录)::ipo_calendar[].TOTAL_RAISE_FUNDS` 登记为 `ipo_actual_fundraising_total_yi_cny`，含义为“东方财富 IPO 发行记录中标注的实际募集资金总额”，单位为亿元。

本结论确认平台字段角色和展示单位。它不承诺每条历史值都与发行人原始公告的精确金额相同；万科历史样本存在约 0.3062% 的差异，具体见数据质量边界。本决定不建立跨来源 `mappings`，也不裁定 `PREDICT_RAISE_FUNDS` 或 `DEC_SUMFINA` 的语义。

## 官方定义与项目运行路径

- 东方财富官方[新股详情前端脚本 `xgdetail.js`](https://data.eastmoney.com/newstatic/js/xg/xgdetail.js) 请求 `RPT_IPO_OTHERDETAILS`，请求列包含 `TOTAL_RAISE_FUNDS`。前端以 `zoom: -8` 格式化该值，并将页面标签写为“实际募集资金总额(亿元)”；这明确给出字段角色和展示单位。
- 项目 [`_events.py`](../../../stock_common/sc_datasource/_events.py) 将 `ipo_calendar` 配置到 `RPTA_APP_IPOAPPLY`，请求 `columns=ALL`；[`_datacenter.py`](../../../stock_common/sc_datasource/_datacenter.py) 原样返回 `result.data[*]`，目标值经 `ipo_calendar()` 透传到 `raw_event_dc.ipo_calendar[].TOTAL_RAISE_FUNDS`，没有重命名或换算。
- `RPT_IPO_OTHERDETAILS` 与项目使用的 `RPTA_APP_IPOAPPLY` 是不同报表端点；本裁决不推断两个端点的完整 schema 相同。两条官方详情响应只用于同证券代码、同名字段的代表值核对。

## 日期口径与留存样本

目标归档目录为 `20261119`，其自然采集日为 `20261120`；`event_dc` 于 `2026-11-20 06:57:34` 开始采集，来源 `as_of_date` 为空。该归档的 IPO 行以 `APPLY_DATE`、`LISTING_DATE` 标识历史发行事件，因此不把采集自然日或目录目标数据日当作发行事件日期。

保留期内有 20 个非空 `event_dc` 采集归档，每个归档含 20 条 IPO 记录，共 400 行；其中 `TOTAL_RAISE_FUNDS` 有 280 个非空观察，覆盖 15 个不同证券。重复归档是同一业务记录的重复观察，不按独立股票或独立 IPO 事件计数。最新 `20261119` 归档中有值的代码为 14 个；`000016` 只出现在最早的三个非空归档。逐行输入、计算值、API 对照及事件日期见[样本核算 CSV](../research/20261121_eventdc_total_raise_funds_samples.csv)。

在 280 个非空观察中，`ISSUE_NUM × ISSUE_PRICE / 10000` 与 `TOTAL_RAISE_FUNDS` 逐值相等 280/280；`TOTAL_ISSUE_NUM × ISSUE_PRICE / 10000` 也相等 280/280。`DEC_SUMFINA` 同样在 280/280 个观测中数值相等。后两项是样本内数值事实，不单独证明 `DEC_SUMFINA` 与目标字段语义相同；本裁决不扩展旧的短路径映射。

## 官方详情接口交叉核对

详情端点以元返回目标字段。下列 2026-11-21 官方响应与项目 `RPTA_APP_IPOAPPLY` 留存值按 `1 元 = 1e-8 亿元` 换算后完全一致：

| 代码 | 留存列表值（亿元） | 官方详情 API（元） | 换算值（亿元） |
|---|---:|---:|---:|
| 000002 万科A | 0.28 | 28,000,000 | 0.28 |
| 000021 深科技 | 1.1938875 | 119,388,750 | 1.1938875 |

官方响应：[000002](https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_IPO_OTHERDETAILS&columns=SECURITY_CODE%2CTOTAL_RAISE_FUNDS&filter=%28SECURITY_CODE%3D%22000002%22%29&pageNumber=1&pageSize=1&source=WEB&client=WEB)、[000021](https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_IPO_OTHERDETAILS&columns=SECURITY_CODE%2CTOTAL_RAISE_FUNDS&filter=%28SECURITY_CODE%3D%22000021%22%29&pageNumber=1&pageSize=1&source=WEB&client=WEB)。

## 数据质量边界

巨潮披露的[万科 2005 年股权分置改革说明书](https://static.cninfo.com.cn/finalpage/2005-10-10/15997383.PDF)记载，公司首次公开发行 A 股 28,086,000 股，发行价每股 1 元，募集资金 28,086,000 元；东方财富对应历史 IPO 记录和当前详情接口均为 28,000,000 元，差额 86,000 元，约为发行人披露金额的 0.3062%。现有证据没有解释差值来源，不把它归因为舍入。

因此，字典记录的是“东方财富所报告的实际募集资金总额”这一字段定义，不将其描述为已逐条由发行人原始公告验证的精确金额。遇到需要发行人级精确值的用途，应另行核对发行公告。

## 适用范围与限制

- 定案只适用于来源 `东财-event_dc(IPO发行记录)` 的完整路径 `ipo_calendar[].TOTAL_RAISE_FUNDS`，不自动扩展到其他端点、短路径或同值字段。
- `PREDICT_RAISE_FUNDS` 是独立的预测候选字段，语义和单位不由本裁决确认；报告代码注释已改为明确区分它与本次定案字段，运行行为保持不变。
- `DEC_SUMFINA` 的数值相等是样本事实，不用来证明语义等价；现有短路径历史映射未在本决定中修改。
- `RPT_IPO_OTHERDETAILS` 和 `RPTA_APP_IPOAPPLY` 是不同报表；若后续同证券、同名字段出现分歧，应重新核对端点和精确路径。

## 证据完整性

- 原始归档 SHA-256：`41fe019b29d038e1cf4726f69700af303aae0206a6fdb8d7399912290065b091`
- 官方 `xgdetail.js` SHA-256：`e681def470ece2ae827fd9a870baf108e692f8020d48d316ef45d5108c9aeeef`
- 样本 CSV 规范 LF SHA-256：`4fc97958c2b2483b03929957ac8f89fde564f993102500e09d5d5ea7ab5e7ca3`

结构化决定见 [`20261121_eventdc_ipo_total_raise_funds.json`](20261121_eventdc_ipo_total_raise_funds.json)。
