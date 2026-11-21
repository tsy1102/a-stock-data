# Eastmoney IPO `PREDICT_RAISE_FUNDS` 定案

复核日期：2026-11-21。

## 定案

将 `东财-event_dc(IPO发行记录)::ipo_calendar[].PREDICT_RAISE_FUNDS` 登记为 `ipo_planned_fundraising_target_yi_cny`，含义为东方财富 IPO 发行记录中的募资计划预测目标，单位为亿元。七个不同 IPO 事件的 API 值均与发行人招股文件中列出的拟投入募集资金/募资需求总额按 `万元 ÷ 10,000 = 亿元` 精确相等。

这确认的是该来源字段的计划/预测角色和单位。它不等同于发行价乘发行股数得出的发行募集总额，不等同于扣除发行费用后的实际净额，也不保证代表发行完成后最新调整的募投预算。本决定不建立跨来源 `mappings`。

## 项目接口路径与官方说明

- 项目 [`_events.py`](../../../stock_common/sc_datasource/_events.py) 将 `ipo_calendar` 路由到东方财富数据中心 `RPTA_APP_IPOAPPLY`，默认请求 `columns=ALL`；`ipo_calendar()` 原样保留响应行，并由 [`capture_context_collectors.py`](../../../scripts/capture_context_collectors.py) 写入 `raw_event_dc.ipo_calendar[]`。目标值没有项目侧重命名或单位换算。
- 2026-11-21 14:26（北京时间）查询[东方财富官方数据中心接口](https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPTA_APP_IPOAPPLY&columns=ALL&pageNumber=1&pageSize=50&sortColumns=APPLY_DATE&sortTypes=-1&source=WEB&client=WEB)，按 `APPLY_DATE` 倒序取 50 条。逐行样本和发行人文件链接见[样本 CSV](../research/20261121_eventdc_ipo_predict_raise_funds_samples.csv)。
- [东方财富官方新股申购页](https://data.eastmoney.com/xg/xg/default.html)说明斜体预估值可能因募集资金、发行数量和发行费用变化，仅供参考，实际数据公布后会更新。网页说明界定预估数据的时变性质，但没有发布 `PREDICT_RAISE_FUNDS` 的版本化字段 schema 或专属中文列名；因此不把页面说明单独当作完整字段契约。

## 发行人正式文件对照

| 代码 | 申购日 | API 预测值（亿元） | 文件计划额（万元） | 换算（亿元） | API 实际募集总额（亿元） |
|---|---|---:|---:|---:|---:|
| 001381 皇冠新材 | 2026-10-19 | 9.186813 | 91,868.13 | 9.186813 | 9.560550 |
| 301718 通则康威 | 2026-10-09 | 13.811148 | 138,111.48 | 13.811148 | 9.797760 |
| 301569 联亚药业 | 2026-09-28 | 9.500000 | 95,000.00 | 9.500000 | 9.361769 |
| 301660 粤芯半导体 | 2026-09-24 | 75.000000 | 750,000.00 | 75.000000 | 61.568785 |
| 001246 力勤资源 | 2026-09-18 | 40.468225 | 404,682.25 | 40.468225 | 36.704547 |
| 301716 鸿富诚 | 2026-09-16 | 12.203918 | 122,039.18 | 12.203918 | 14.396344 |
| 601091 沈鼓集团 | 2026-09-08 | 21.344695 | 213,446.95 | 21.344695 | 13.652911 |

七个发行人文件金额与 API 值均精确相等，未使用舍入容差；七条 `TOTAL_RAISE_FUNDS` 实际募集总额均与预测值不同，正负方向都有，能区分“发行计划目标”和“实际发行募集总额”。逐行差额与原始链接留存在样本 CSV。通则康威的官方风险公告同时列出 138,111.48 万元资金需求与 97,977.60 万元发行募集总额，是两种金额角色的直接区分样本。

力勤资源说明该字段具有方案版本边界：`PREDICT_RAISE_FUNDS=40.468225` 对应招股文件原计划 404,682.25 万元；实际募集后发行人又将拟投入募集资金调整为 340,418.85 万元。API 样本仍保留原计划值。因此本释义限定为东方财富记录中的发行计划预测目标，不将其称为实际金额或发行完成后最新募投预算。

## 历史归档边界

2026-11-19 目标数据日归档于自然日 2026-11-20 06:57:34 采集，`event_dc.as_of_date` 为空。`raw_event_dc.ipo_calendar` 有 20 条记录，`APPLY_DATE` 从 1989-03-10 至 1993-06-28；仅 7 条 `PREDICT_RAISE_FUNDS` 非空，且 7 条均为零。代码 [`ipo_calendar()`](../../../stock_common/sc_datasource/_events.py) 没有指定排序，数据中心默认按 `APPLY_DATE` 升序；采集因此保留最早 20 条，不能用这组恒零记录否定字段语义。报告渲染使用的 `ipo_calendar_recent()` 则明确按 `APPLY_DATE` 倒序。

本次网络查询是一次只读 API 核验，不是项目采集归档。响应记录带 IPO 事件日期 `APPLY_DATE`，不以本次查询时刻、目录目标数据日或采集自然日替代发行方案版本日期。

## 使用影响和未决范围

- [`sc_market_signals.py`](../../../stock_common/sc_market_signals.py) 的资金压力估值此前在 `TOTAL_RAISE_FUNDS` 缺失时用 `PREDICT_RAISE_FUNDS` 回退，混合了实际/估算发行总额与计划募资目标。本次改为优先使用实际募集总额；缺失时只用发行数量乘发行价估算总额。计划目标不再进入发行总额栏目。
- 官方网页没有发布该响应键的版本化 schema、精确更新时间或历史修订记录；本裁决不解释计划版本切换时点，也不承诺其他时期或所有历史记录都与发行人文件逐项一致。
- 不把 `PREDICT_RAISE_FUNDS` 与 `TOTAL_RAISE_FUNDS` 建立映射；两者含义和金额口径不同。

结构化决定见 [`20261121_eventdc_ipo_predict_raise_funds.json`](20261121_eventdc_ipo_predict_raise_funds.json)。
