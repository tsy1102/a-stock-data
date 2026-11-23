# 东方财富 IPO `ORG_TYPE` 字段核验（2026-11-23）

## 范围与证据

- 精确路径：`东财-event_dc(IPO发行记录)::ipo_calendar[].ORG_TYPE`。项目 `stock_common/sc_datasource/_events.py::ipo_calendar()` 查询 `RPTA_APP_IPOAPPLY` 的 `columns="ALL"`；`_datacenter.py::query_datacenter()` 保留 `result.data[*]` 原始键，`collect_event_dc()` 将列表保存为 `raw_event_dc.ipo_calendar[]`。本轮没有运行项目采集器。
- 历史样本：按 `MIN_CAPTURE_DATE=2026-10-15`，纳入 2026-10-16 至 2026-11-19 的 20 个非空归档批次，共 400 行、21 个不同证券代码。`ORG_TYPE` 400/400 有值；20 个不同证券代码在重复批次中的分类没有变化。每条逐行值、目录数据日和原始文件 SHA-256 见[审计 CSV](20261123_eventdc_ipo_org_type_audit.csv)；[机器清单](20261123_eventdc_ipo_org_type_audit.json)汇总批次与分类覆盖。
- 观察到的枚举只有 `银行股`（20 行、1 个代码 `000001`）和 `非银行股`（380 行、20 个代码）。例：`000001 平安银行` 为 `银行股`，`000002 万科A` 为 `非银行股`。这里的 400 行是 20 个证券记录在 20 次响应中的重复观测，不视作 400 个独立证券。
- 东方财富官方[新股申购页](https://data.eastmoney.com/xg/)的一方脚本 [`xg/index.js`](https://data.eastmoney.com/newstatic/js/xg/index.js) 在 `loadtabledata()` 中调用 `RPTA_APP_IPOAPPLY`，请求列清单明确含 `ORG_TYPE`。该页未发布版本化字段 schema 或该键的分类规则，因此本裁决只确认其返回的分类文本和值，不推断法律主体类型、行业代码体系、判定标准或未观察到的枚举。
- 2026-11-23 对东方财富官方接口按 `SECURITY_CODE="000001"` 做一次公开页面核对，`ORG_TYPE` 返回 `银行股`。这是单条公开接口核查，不是项目采集。

## 结论边界

将该路径定为 IPO 发行记录的“银行股/非银行股分类文本”。值是分类文字，不是数值单位；它与同一响应中区分上市板块的 `MARKET_TYPE` 不应混为一项。注册表不创建跨来源映射，也不把该稳定分类值用作行情日期证据。

CSV 规范 LF SHA-256：`6f33c51a6e30b39198ef73602538d6310993287d8ac4f48f05a635c870c42dbe`。

官方接口核对链接：<https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPTA_APP_IPOAPPLY&columns=ALL&filter=%28SECURITY_CODE%3D%22000001%22%29&pageSize=5&pageNumber=1>。
