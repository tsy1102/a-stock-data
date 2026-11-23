# IPO `CURRENT_ONEWORD_NUM` / `PE_TTM` 批次复核

审计日期：2026-11-24。范围：东方财富数据中心 `RPTA_APP_IPOAPPLY` 的两个未定完整路径。仅使用保留边界内本地 `raw_event_dc.json` 与东方财富公开页面脚本；未运行采集。本文记录排除的解释，不作为字段定案。

## 来源路径

项目 `stock_common/sc_datasource/_events.py::ipo_calendar()` 调用 `eastmoney_datacenter()`，未传 `columns` 参数；统一查询默认请求 `columns=ALL`。采集器将响应行保留在 `raw_event_dc.ipo_calendar[]`，因此本轮核查的完整路径为：

- `东财-event_dc(IPO发行记录)::ipo_calendar[].CURRENT_ONEWORD_NUM`
- `东财-event_dc(IPO发行记录)::ipo_calendar[].PE_TTM`

东方财富 IPO 首页脚本 [`newstatic/js/xg/index.js`](https://data.eastmoney.com/newstatic/js/xg/index.js) 于本轮读取。其 `RPTA_APP_IPOAPPLY` 首页字段清单包含 `AFTER_ISSUE_PE`、`CONTINUOUS_1WORD_NUM` 和 `PROFIT`，未包含 `CURRENT_ONEWORD_NUM` 或 `PE_TTM`。首页实际使用哪些字段，只能界定展示映射范围；未展示不能证明接口键的完整含义或无业务意义。

## `PE_TTM` 的时间口径核查

在 2026-10-16 至 2026-11-19 的 20 个保留采集批次中，证券 000012（南玻 A）的 `LATELY_PRICE` 从 3.57 元变到 3.21 元，而 `PE_TTM` 每批均为 44.2835129。这不支持“随同批最新价同步刷新的当日市盈率”解释；若仍作此解释，还需独立证明其收益分母在这些批次间按相同比例变化。现有证据不能认定它具体是发行期估值、历史快照、缓存值或其他口径。

同一 2026-11-19 原始行中，非空 `PE_TTM` 共 8 个不同值；000017 的 `PE_TTM=34.44757796`、`AFTER_ISSUE_PE=6.4`，000030 的 `PE_TTM=176.56565657`、`AFTER_ISSUE_PE=9.9`。因此 `PE_TTM` 不能简单映射为该接口明确用于“发行市盈率”的 `AFTER_ISSUE_PE`。页面脚本也未将 `PE_TTM` 加入首页表格字段。

当前结论：字段含义、计算基准及业务日期均未定。下一步应寻找该字段的东方财富字段级契约，或以原始发行公告/历史财务口径验证具体候选；不得把当前市盈率、发行市盈率或 `PE_TTM` 词面直接写入主字典。

## `CURRENT_ONEWORD_NUM` 的关系核查

东方财富首页脚本的字段表使用 `CONTINUOUS_1WORD_NUM` 与 `PROFIT` 展示连续一字板/中签获利相关内容，没有 `CURRENT_ONEWORD_NUM` 的展示映射。本地已有 [风险标记审计](20261122_eventdc_risk_flag_audit.md)：保留期内 `CURRENT_ONEWORD_NUM` 与 `IS_RISKWARNING` 有 23 条直接反例，不能把它释为风险标记；同批旧 `PREDICT_ISSUE_PRICE1` 对撞也有 23 条反例。000016 的 8210 值只出现于三个重复采集批次，尚无可验证的字段解释。

当前结论：保持未知。共同零值、同名片段以及单个 8210 异常值均不足以构成释义；需要取得该键对应的官方字段说明或找到能区分候选解释的新增历史/公开样本。

## 本轮处置

- 两个路径均未达到来源契约或来源内实证定案条件；不新增映射、不改主字典。
- 本轮访问的是公开静态脚本，不是项目数据采集；未请求东方财富数据接口，不改变本地样本。
- 其余 `st_list` 的三个来源/路径候选仍以 [`20261121_st_list_route_provenance_audit.md`](20261121_st_list_route_provenance_audit.md) 的历史路由缺口结论为准，本轮未重开。
