# 东方财富可转债 `ISSUE_YEAR` 字段核验

## 裁决对象

- 来源：`东财-event_dc(可转债列表)`
- 完整路径：`convertible_bonds[].ISSUE_YEAR`
- 当前运行路径：`stock_common/sc_datasource/_convertible.py::convertible_bonds()` 的 `RPT_BOND_CB_LIST` 响应原键，经 `stock_common/sc_datasource/_datacenter.py::query_datacenter()` 返回 `result.data` 行对象，保存在 `raw_event_dc.convertible_bonds[]`。
- 历史目标数据日：2026-11-19；归档实际采集于 2026-11-20 06:57:34 +08:00。该来源无 `as_of_date`，本字段按稳定的债券年度元数据处理，不把目录日解释为字段有效日。

## 官方字段路径与标签

东方财富官网可转债详情页加载第一方脚本 [`detail.js`](https://data.eastmoney.com/newstatic/js/kzz/detail.js)。脚本的 `loadinfo()` 请求 `datacenter-web.eastmoney.com/api/data/v1/get`，指定 `reportName: 'RPT_BOND_CB_LIST'`、`columns: 'ALL'`；详情渲染语句为 `$(".zqnd").html(data.ISSUE_YEAR || "-"); //债券年度`。这把官网显示标签“债券年度”与官方响应键 `ISSUE_YEAR` 直接绑定。复核时该脚本 SHA-256 为 `ca2b2b77647eabdd03121487f6540c0918212c176c42cf6bed0ce0028e4c7dcc`（2026-11-21 19:20–19:23 +08:00 核验）。

项目适配器使用相同的官方 reportName 与 `columns=ALL`，统一客户端仅返回官方响应中的字典行，不重命名或计算 `ISSUE_YEAR`。因此从上游响应到项目完整采集路径可精确追溯，语义没有依赖字段拼写猜测。

## 样本与真实年度含义

保留的 [`raw_event_dc.json`](../20261119/raw_event_dc.json) SHA-256 为 `41fe019b29d038e1cf4726f69700af303aae0206a6fdb8d7399912290065b091`。500 条可转债记录中 `ISSUE_YEAR` 全部有值；其中恰有 5 条的字段年度与 `VALUE_DATE` / `PUBLIC_START_DATE` 的实际公开发行日期年份不同。对这 5 条逐一查阅东方财富当前同接口响应和发行人正式公告：字段值全部等于中国证监会核准批复文号中的年份，而不是实际发行年份。

| 债券代码与名称 | 项目归档及东方财富接口 `ISSUE_YEAR` | 实际公开发行日 | 发行人公告中的证监会批复 | 判断 |
|---|---:|---|---|---|
| 110032 三一转债 | 2015 | 2016-01-04 | 证监许可[2015]3090号 | 核准年份 |
| 110033 国贸转债 | 2015 | 2016-01-05 | 证监许可[2015]3117号 | 核准年份 |
| 111011 冠盛转债 | 2022 | 2023-01-03 | 证监许可[2022]2865号 | 核准年份 |
| 111012 福新转债 | 2022 | 2023-01-04 | 证监许可[2022]2891号 | 核准年份 |
| 113562 璞泰转债 | 2019 | 2020-01-02 | 证监许可[2019]2318号 | 核准年份 |

发行人正式材料：[三一转债发行上市公告书](https://static.cninfo.com.cn/finalpage/2016-01-14/1201910636.PDF)、[国贸转债发行与上市概况](https://static.cninfo.com.cn/finalpage/2016-06-29/1202431740.PDF)、[冠盛转债发行与上市概况](https://static.cninfo.com.cn/finalpage/2025-06-26/1223980055.PDF)、[福新转债开始转股公告](https://static.cninfo.com.cn/finalpage/2023-07-04/1217202455.PDF)、[璞泰转债上市公告书](https://static.cninfo.com.cn/finalpage/2020-01-23/1207282258.PDF)。五份公告分别明确了批复文号和发行日；这五条恰是完整 500 条本地样本中能区分“核准年度”与“发行年份”的全部记录，没有遗漏或抽掉反例。

2026-11-21 19:20–19:23 +08:00 直接核查东方财富官方详情脚本及 `RPT_BOND_CB_LIST` API；以上五个代码的官方响应值与本地归档逐项一致。详情页官方标签本身为“债券年度”，而五条跨年样本将该年度的业务角色进一步确定为“核准年度”。`ISSUE_YEAR` 的变量名不能按字面改释为发行日年份。

## 结论与范围

将规范名登记为 `convertible_bond_approval_year`，中文含义为“可转债核准年度（东方财富详情页标签：债券年度）”，单位为“年”。此结论由官方页面字段绑定、项目原键透传和全部五条区分性历史样本共同支持；它只定义该来源路径，不建立跨源字段映射。当前没有证据支持把该字段解释成申购年份、实际公开发行年份或上市年份。
