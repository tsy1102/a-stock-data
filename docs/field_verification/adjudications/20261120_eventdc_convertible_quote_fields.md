# 东方财富可转债行情字段与旧映射更正

## 裁决结论

`东财-event_dc(可转债列表)` 的精确运行路径是 `convertible_bonds[].<FIELD>`。按东方财富官方详情页脚本的请求参数和页面标签，登记以下 10 个来源字段：初始转股价、当前转股价、转股价值、正股价、债券现价的两个响应键、转股溢价率、回售触发价、强赎触发价、正股市净率。只确认这些来源路径各自的含义，不建立跨来源 `mappings`。

撤回旧的 `INITIAL_TRANSFER_PRICE ↔ TRANSFER_VALUE` 同义映射。历史相等来自行情请求漏传 `quoteColumns`，不能证明两个字段同义。经更正的接口下，154 组可比记录中两个字段 0 组相等；`TRANSFER_VALUE` 与采集到的正股价、当前转股价按公式计算的结果 154/154 精确吻合。

KPH（开盘红）和 KPL（开盘啦）仍是两个独立来源。本裁决只涉及东财 `event_dc`，不改变两者的来源身份、采集或对照规则，详见[身份裁决](20261119_kph_kpl_source_identity.md)。

## 请求与运行路径

东方财富可转债详情页的前端脚本请求 `RPT_BOND_CB_LIST`，设置 `columns=ALL`，并通过 `quoteColumns` 请求以下行情键：

```text
f2~01~CONVERT_STOCK_CODE~CONVERT_STOCK_PRICE
f235~10~SECURITY_CODE~TRANSFER_PRICE
f236~10~SECURITY_CODE~TRANSFER_VALUE
f2~10~SECURITY_CODE~CURRENT_BOND_PRICE
f237~10~SECURITY_CODE~TRANSFER_PREMIUM_RATIO
f239~10~SECURITY_CODE~RESALE_TRIG_PRICE
f240~10~SECURITY_CODE~REDEEM_TRIG_PRICE
f23~01~CONVERT_STOCK_CODE~PBV_RATIO
```

脚本只在特定登录 Cookie 条件下令 `hsaDelay()` 返回真并发送 `quoteType=1`；项目请求不携带登录 Cookie，因此发送 `quoteType=0`。请求由 [`_convertible.py`](../../../stock_common/sc_datasource/_convertible.py) 经 [`_eastmoney.py`](../../../stock_common/sc_datasource/_eastmoney.py) 和 [`_datacenter.py`](../../../stock_common/sc_datasource/_datacenter.py) 发出，返回行由 `collect_event_dc()` 保存到 `raw_event_dc.convertible_bonds[]`。

官方 [可转债详情页前端脚本](https://data.eastmoney.com/newstatic/js/kzz/detail.js)在 `loadinfo()` 中给出上述接口参数，并将响应键直接用于页面字段；[寿22转债详情页](https://data.eastmoney.com/kzz/detail/113660.html)和[鹤21转债详情页](https://data.eastmoney.com/kzz/detail/113632.html)列出这些行情标签。寿22页明确列出正股价、正股市净率、债券现价、转股价、转股价值、转股溢价率、回售触发价和强赎触发价。前端对债券现价使用 `CURRENT_BOND_PRICENEW`（非空时）或 `CURRENT_BOND_PRICE`（否则）的回退显示。

## 采集样本与旧相等来源

2026-11-20 盘前单源补采将结果写入目标数据日目录 `20261119`。接口返回 500 条债券记录；项目采集时刻是 2026-11-20 06:57:34–06:59:11。目录目标日不是这些行情值的来源数据日：响应未提供可确认的 `as_of_date`，`fetched_at` 只表示项目收到响应的时间。最终采集代码采用 `quoteType=0`；单债券在线探测和此全量补采均返回寿22相同的行情值。

在保留起点 `2026-10-15` 及之后、且本次覆盖前仍保留的 20 个旧快照中，10 月 15 日快照为 0 行，其余 19 个快照各 500 行。9,500 行中有 9,452 组 `INITIAL_TRANSFER_PRICE` 与 `TRANSFER_VALUE` 都为数值的配对，9,452 组完全相等；旧快照的 `TRANSFER_PRICE`、`CONVERT_STOCK_PRICE`、债券现价和三个触发价均没有数值。逐日文件摘要见[保留期覆盖审计](../research/20261120_eventdc_quote_coverage_history.csv)。这组证据说明旧碰撞只观察到不完整请求产生的同值字段，无法判别接口将行情键返回为有效值的行为。

更正请求后的 500 行快照中，非空数值覆盖为：`INITIAL_TRANSFER_PRICE` 499 行，`TRANSFER_PRICE` 154 行，`TRANSFER_VALUE` 154 行，`CONVERT_STOCK_PRICE` 493 行，`CURRENT_BOND_PRICE` 152 行，`CURRENT_BOND_PRICENEW` 2 行，`TRANSFER_PREMIUM_RATIO` 154 行，`RESALE_TRIG_PRICE` 149 行，`REDEEM_TRIG_PRICE` 154 行，`PBV_RATIO` 497 行。仅将当前响应中同时具备转股价、转股价值和正股价的 154 行用于公式复核；逐行值和计算差见[样本 CSV](../research/20261120_eventdc_quote_fields_samples.csv)。

| 完整路径 | 定案含义 | 单位 | 本次证据边界 |
|---|---|---:|---|
| `convertible_bonds[].INITIAL_TRANSFER_PRICE` | 初始转股价格 | 元/股 | 寿22初始价 38.08、鹤21初始价 39.09 均与发行人公告及原始响应一致；不代表当前转股价。 |
| `convertible_bonds[].TRANSFER_PRICE` | 当前生效转股价格 | 元/股 | 寿22原始响应 36.84，与发行人公告列出的调整后现行价一致。 |
| `convertible_bonds[].TRANSFER_VALUE` | 东方财富页面显示的转股价值 | 元 | 154/154 与 `100 × CONVERT_STOCK_PRICE / TRANSFER_PRICE` 四舍五入到 4 位小数的结果一致。公式是样本观察，不宣称官网公开了统一计算规则。 |
| `convertible_bonds[].CONVERT_STOCK_PRICE` | 正股价 | 元 | 官方请求按 `CONVERT_STOCK_CODE` 取行情，详情页标签为“正股价(元)”。 |
| `convertible_bonds[].CURRENT_BOND_PRICE` | 债券现价 | 元 | 官方行情请求键；详情页 `CURRENT_BOND_PRICENEW` 为空时显示该键。 |
| `convertible_bonds[].CURRENT_BOND_PRICENEW` | 债券现价的页面回退键 | 元 | 官方页面在该键非空时优先显示；本次只有 2 行非空。未据此建立数值等价映射。 |
| `convertible_bonds[].TRANSFER_PREMIUM_RATIO` | 转股溢价率 | % | 详情页前端按百分比展示；按 `100 × (债券现价 / 转股价值 − 1)` 复算，153/154 匹配到 2 位小数。113655 相差 0.01 个百分点，保留差值，不推断为舍入误差。 |
| `convertible_bonds[].RESALE_TRIG_PRICE` | 回售触发价 | 元 | 与官方详情页“回售触发价(元)”一一对应。 |
| `convertible_bonds[].REDEEM_TRIG_PRICE` | 强赎触发价 | 元 | 与官方详情页“强赎触发价(元)”一一对应。 |
| `convertible_bonds[].PBV_RATIO` | 正股市净率 | — | 与官方页面“正股市净率”一一对应；页面未标注单位，故不补造单位，也不解释为百分数。 |

寿22发行人公告明确记载初始转股价 38.08 元/股及 2025 年调整至 36.84 元/股；鹤21公告明确记载初始转股价 39.09 元/股。对应归档响应中的初始价分别为 38.08 和 39.09；寿22当前转股价为 36.84。[寿22公告](https://static.cninfo.com.cn/finalpage/2026-10-09/1225596301.PDF)；[鹤21公告](https://static.cninfo.com.cn/finalpage/2026-06-25/1225385842.PDF)。

## 日期资格与注册表变更

本次来源捕获日期是 2026-11-20，采集目录目标日是 2026-11-19，但行情响应没有来源实际日期。字段含义可依据官方键—页面标签映射以及发行人公告定案；这些动态行情值不作为 2026-11-19 的正式同日碰撞证据，也不把 `fetched_at` 当作 `as_of_date`。

结构化来源契约决定见 [`20261120_eventdc_convertible_quote_fields.json`](20261120_eventdc_convertible_quote_fields.json)。本次删除注册表里唯一的旧活动映射：

```text
event_dc.INITIAL_TRANSFER_PRICE ↔ event_dc.TRANSFER_VALUE
```

该映射原引用 2026-09-24 的 L1，但该日期早于当前样本保留边界；保留期内旧相等样本由缺少 `quoteColumns` 的请求形状解释。对应活动行也已从 [`docs/verify/cross_source_align.md`](../../verify/cross_source_align.md) 移除，以防 `extract_registry.py` 重新导入。`collision_state.json.legacy_findings_v1` 中的旧条目和 2026-09-24 报告只作为历史记录，不再代表当前语义结论。

按这批字段更新注册表后的本地碰撞报告见 [`20261119/eventdc_quote_fields_reviewed_20261120/20261119_collision_report.md`](../20261119/eventdc_quote_fields_reviewed_20261120/20261119_collision_report.md)；该报告完整且无 L1/L1-C 新候选，动态可转债报价因无 `as_of_date` 不计入日期合格样本。KPH/KPL 交叉弱候选的逐项审阅见 [`20261120_kph_kpl_l4_candidate_reviews.json`](20261120_kph_kpl_l4_candidate_reviews.json)。

复核摘要：全量 raw SHA-256 `41FE019B29D038E1CF4726F69700AF303AAE0206A6FDB8D7399912290065B091`；样本 CSV SHA-256 `A95619F2B51A20B83F601426FD1E774C0124C1A8CA1FF253B54AC9018E68F274`；覆盖审计 CSV SHA-256 `F369A953A675A3CD36619DEEB3AA4CAEF332CF1F38506768258FB162A6C2A56A`。
