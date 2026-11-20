# 东方财富可转债申购字段来源契约裁决

复核日期：2026-11-20。范围为 `东财-event_dc(可转债列表)` 的七条完整来源路径；本次只登记官网页面直接绑定的字段，不建立跨来源映射。

## 官方接口与字段绑定

东方财富[可转债新股申购页](https://data.eastmoney.com/xg/xg/?mkt=kzz)的表头通过 `data-field` 直接绑定字段键。页面前端脚本 [`xglist.js`](https://data.eastmoney.com/newstatic/js/xg/xglist.js) 的 `loadKzzTable()` 对 `api/data/v1/get` 请求使用 `reportName=RPT_BOND_CB_LIST`、`columns=ALL`。页面 HTML 中可见的精确键与标签如下：

| 完整路径 | 官网字段标签 | 原始单位 | 500 条留存记录 |
|:--|:--|:--|:--|
| `convertible_bonds[].BOND_START_DATE` | 中签号发布日 | 日期 | 500/500 非空，441 个不同日期；例：2022-11-21 |
| `convertible_bonds[].SECURITY_START_DATE` | 股权登记日 | 日期 | 499/500 非空，440 个不同日期；例：2022-11-16 |
| `convertible_bonds[].RATING` | 信用评级 | — | 499/500 非空，18 个不同值；例：AA- |
| `convertible_bonds[].ONLINE_GENERAL_AAU` | 申购上限（万元） | 千元 | 500/500 非空，47 个不同值；范围：1,000–20,000,000 |
| `convertible_bonds[].ONLINE_GENERAL_LWR` | 中签率 | % | 499/500 非空，499 个不同值；范围：0.00033243–5.31177382 |
| `convertible_bonds[].FIRST_PROFIT` | 每中一签获利（元） | 元 | 497/500 非空，497 个不同值；范围：-217.804376763368–2,689.85048466796 |
| `convertible_bonds[].FIRST_PER_PREPLACING` | 每股配售额 | 元/股 | 499/500 非空，466 个不同值；例：2.055 |

页面同时把 `FIRST_PER_PREPLACING` 的字段说明为：股权登记日持有的原股东可按每股配售额优先配售可转债，单位为元/股。`xglist.js` 将 `ONLINE_GENERAL_AAU` 按 `zoom=-1` 显示，并在格式器注释中明确接口单位是千元、页面单位是万元；`ONLINE_GENERAL_LWR` 按四位小数加百分号显示；`FIRST_PROFIT` 按两位小数显示。这里只记录字段自身的官方显示口径，不推导未公开的收益或中签率公式。

项目的 [`_convertible.py`](../../../stock_common/sc_datasource/_convertible.py) 请求同一 `RPT_BOND_CB_LIST`，[`_datacenter.py`](../../../stock_common/sc_datasource/_datacenter.py) 保留响应行原键，[`capture_context_collectors.py`](../../../scripts/capture_context_collectors.py) 将其保存为 `raw_event_dc.convertible_bonds[]`。因此注册身份为 `东财-event_dc(可转债列表)::convertible_bonds[].<FIELD>`。`BOND_START_DATE`、`SECURITY_START_DATE` 等日期分别使用官网表头标签，不与申购日或上市时间混淆。

## 留存样本及时间边界

使用保留期内 `docs/field_verification/20261119/raw_event_dc.json` 的一次 `RPT_BOND_CB_LIST` 响应，共 500 条不同债券记录。原文件 SHA-256：`41fe019b29d038e1cf4726f69700af303aae0206a6fdb8d7399912290065b091`。逐行样本 CSV 仅抽出本次七个字段及证券代码/名称、项目采集接收时间，规范 LF SHA-256：`28ab37ec65cca48b35a28d652479e1b1b873118ce96f5f148b9abebe71b53308`。

该归档目录的数据日为 2026-11-19，采集日为 2026-11-20；可转债行的项目 `fetched_at` 接收时间约为 2026-11-20 06:59:11（北京时间）。响应没有可确认的来源实际数据日期。目录日期与项目接收时间不代表 `ONLINE_GENERAL_LWR`、`FIRST_PROFIT` 或 `RATING` 的来源 as-of 日期；本裁决只定字段含义和原始单位，不将这 500 条当成 500 个独立日期样本或目标数据日的行情证据。


`FIRST_PROFIT` 的样本包含正数和负数；本裁决仅采用官网“每中一签获利（元）”标签，不将负值视作采集错误，也不额外推导利润算法或估值时点。`ONLINE_GENERAL_AAU` 的单位按接口原始千元登记；官网表格为了展示换算为万元。缺值不推定为零。

## 裁决范围

七个字段均来自同一官方 `RPT_BOND_CB_LIST` 请求，但只按各自 `data-field` 和中文表头登记。页面字段相同或数值相似，不构成与 IPO、KPH、KPL、其他东财接口或其他仓库字段的映射依据。KPH（开盘红）与 KPL（开盘啦）仍按两个独立来源身份处理，本裁决不涉及两者的合并或采集关系。
