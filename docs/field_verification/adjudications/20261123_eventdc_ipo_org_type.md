# 东方财富 IPO `ORG_TYPE` 来源契约定案（2026-11-23）

## 裁决

将 `东财-event_dc(IPO发行记录)::ipo_calendar[].ORG_TYPE` 定义为 IPO 发行记录的“银行股/非银行股分类文本”。单位为分类文本，当前观察到 `银行股` 与 `非银行股` 两个值。

这项裁决只定义接口返回的分类文字，不解释东方财富内部分类标准，不把它扩展成公司的法律组织形式或某套交易所行业代码，也不声称未来不会出现其他枚举。该字段与 `MARKET_TYPE` 等上市板块分类字段区分。本次不建立跨源映射，不将其用于行情观测日期推断。

## 来源路径与样本

项目 `stock_common/sc_datasource/_events.py::ipo_calendar()` 请求官方 Data Center `RPTA_APP_IPOAPPLY` 的 `columns="ALL"`；`stock_common/sc_datasource/_datacenter.py::query_datacenter()` 返回 `result.data[*]` 原始行，`scripts/capture_context_collectors.py::collect_event_dc()` 保留字段到 `raw_event_dc.ipo_calendar[]`。东方财富官方新股页的一方 [`xg/index.js`](https://data.eastmoney.com/newstatic/js/xg/index.js) 在 `loadtabledata()` 的请求列清单中明确包含 `ORG_TYPE`。同代码官方接口返回 `000001` 的 `ORG_TYPE="银行股"`。

保留边界 `2026-10-15` 后共审计 20 个非空归档批次、400 行和 21 个不同证券代码。400/400 行有值；`银行股` 有 20 行、对应 000001，`非银行股` 有 380 行、对应其他 20 个代码；同一证券在重复批次中的分类无变化。400 行是重复采集，不代表 400 个独立证券。逐行数据和原始文件哈希见[研究 CSV](../research/20261123_eventdc_ipo_org_type_audit.csv)、[审计清单](../research/20261123_eventdc_ipo_org_type_audit.json)及[研究说明](../research/20261123_eventdc_ipo_org_type_audit.md)。

东方财富未公开版本化字段 schema 或该分类的判定规则，因此裁决范围仅限接口返回分类文本和观察到的枚举。结构化来源契约决定见[JSON](20261123_eventdc_ipo_org_type.json)。本轮只进行公开网页/单行接口研究和本地历史文件审计，未运行项目采集器。
