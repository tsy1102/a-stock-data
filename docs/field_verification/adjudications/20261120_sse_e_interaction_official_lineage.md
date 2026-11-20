# 上证 e 互动官方来源血缘核验（2026-11-20）

## 结论

采集器访问的 `https://sns.sseinfo.com` 是上交所官方“上证 e 互动”平台，登记为 `exchange` 来源家族。该结论只确认运行时来源身份与运营归属，不确认任何字段的业务语义，也不把该平台的问答内容视为交易所行情数据。

## 证据

- 上交所官网的[上线说明](https://www.sse.com.cn/aboutus/mediacenter/hotandd/c/c_20150912_3988691.shtml)明确称“上证 e 互动网络平台”，并将平台地址列为 `sns.sseinfo.com`。
- [上证所信息网络有限公司投资者服务页](https://www.sseinfo.com/services/investor/)说明“上证 e 互动”是面向投资者与上市公司的互动平台，并列出投资者提问、上市公司反馈等功能。
- [平台首页](https://sns.sseinfo.com/)的使用声明说明平台知识产权归属于上海证券交易所或上证所信息网络有限公司。
- 项目适配器 [`stock_common/sc_datasource/_sse_e_interaction.py`](../../../stock_common/sc_datasource/_sse_e_interaction.py) 的 `SSE_E_BASE` 固定为 `https://sns.sseinfo.com`，列表及公司问答请求分别访问 `/ajax/feeds.do` 与 `/ajax/userfeeds.do`。

## 归属范围与边界

- 登记 `runtime_sources.sse_e_interaction.independence_family = "exchange"`，表示该官方平台归属上交所服务体系。与沪深交易所其他官方接口对撞时，不重复计为独立机构来源。
- KPH（开盘红）与 KPL（开盘啦）仍为不同来源；本次判断只涉及上证 e 互动。
- `id`、`question_time`、`answer_time` 的字段语义、时间精度和相对时间换算均未由本条来源血缘裁决。字段含义仍需结合页面标签、原始响应及样本单独核实。
- 用户和上市公司在平台提交的内容属于平台承载的互动信息；来源官方不意味着内容等同于交易所发布的行情或法定披露。
