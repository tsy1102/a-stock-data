# 东方财富 push2 `f80` / `f129` 来源内语义核验

核验日期：2026-11-22。两项均按 `东财-push2(stock/get)` 的完整源键分别处理，未套用相同短码的 `东财-ulist239(np/get)` 语义。

## `f80`：个股交易时段区间

项目请求路由为 `push2 stock/get -> data.f80 -> raw_push2.stocks[code].data.f80`；`stock_common/sc_datasource/_quotes.py` 将其 JSON 字符串解析为 `trading_periods`。保留样本为 2026-11-17、18 两个收盘来源日、20 只股票、40 条记录；40/40 都是两个区间：09:30–11:30 与 13:00–15:00。

交易所规则将连续竞价分为 09:30–11:30 与 13:00–14:57，并将 14:57–15:00 单列为收盘集合竞价；因此 `f80` 记录的是宽泛的日内交易时段区间，下午区间包含收盘集合竞价，不表示全部时间都是连续竞价。覆盖上交所、深交所和北交所样本，分别对照其现行官方规则。该结论确认区间含义，不据此推断停牌个股实际可成交。

## `f129`：个股概念 / 题材标签列表

同一批 20 只股票、两个收盘来源日共 40 条记录中，`push2 stock/get::f129` 与同一提供方另一接口 `ulist239(np/get)::f103` 的完整逗号分隔字符串 40/40 相同；两接口属于同一提供方，不当作独立数据源计数。项目 `_quotes.py` 将 `f129` 拆为概念标签数组。

2026-11-22 08:26（北京时间）在 Chrome 核对东方财富贵州茅台 F10“核心题材”官方页面。页面“概念题材”列表明确列出“味蕾经济、白酒、乡村振兴、超级品牌、央国企改革、电商概念、西部大开发”；“题材详情”还列出“酿酒概念”。与 2026-11-17 保存的 600519 `f129` 全部 8 项逐项对上。网页当前内容只用于确认标签类别，不据此倒推历史网页在 11-17 的状态或字段值更新时点。

## 样本和实现

逐行原值、接口间比较、市场和收盘阶段见 `research/20261122_eastmoney_push2_f80_f129_audit.csv`。来源日期来自 `meta.json.sources.{push2,ulist239}.source_capture_date`，两个来源均标记 `data_market_phase=closed`；目录日期与来源数据日一致。

- 项目请求/解析：`stock_common/sc_datasource/_quotes.py` 中 `f129` 概念列表解析和 `f80` 交易时段解析；采集快照接口为 `em.stock_get`。
- [上交所《上海证券交易所交易规则（2026年修订）》](https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml)。
- [深交所《深圳证券交易所交易规则（2026年修订）》](https://docs.static.szse.cn/www/lawrules/rule/trade/current/W020260424690713155663.pdf)。
- [北交所《北京证券交易所交易规则》](https://www.bse.cn/jygl_list/200028217.html)。
- [东方财富贵州茅台 F10 核心题材页面](https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code=SH600519&color=b#/hxtc)。
