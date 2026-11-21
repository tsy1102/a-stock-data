# TDX 29 条未知路径穷尽复核（2026-11-22）

## 结论

本轮逐项复核注册表中 29 条 `TDX(双命名源)` 未知路径。29 条均已完成处置：`ErrorId` 按官方样例确认是返回键；`Date` 裸路径因缺接口/父对象而不能唯一解释，已作为旧的未限定路径退役，并新增 8 个有官方定义的接口级日期路径；其余 27 条按真实路径属性分为项目派生输出、混合来源包装输出、接口/类型 token 和旧伪路径，退出 TDX 原始字段破解队列。

退出未知队列只否定这些**精确 TDX 来源路径身份**，不否定包装输出或其它来源中同名字段的业务价值。没有根据字段名相似就登记映射；下表中的官方同义概念只作接口级检索线索，只有精确响应路径和项目值级证据闭环后才可建立别名或跨源关系。

本轮没有运行采集。只读保留期内采集文件的 JSON 结构，不把采集目录日期当作来源实际日期，也不将结构计数当作语义/数值对撞证据。官方接口日期条目只证明对应 TQ API 的字段契约，不代表本项目当前 7709/TCP 采集器调用这些接口。

## 实际采集路径检查

按 [`capture_retention.py`](../../../scripts/capture_retention.py) 的保留起点 `2026-10-15`，扫描 `docs/field_verification/` 下 22 个日期目录中的 88 份 TDX/ELTDX 文件：每个日期目录的 `raw_tdx.json`、`raw_tdx_f10.json`、`raw_tdx_f10_more.json` 和 `raw_eltdx.json`。逐文件 SHA-256、目标叶键计数和路径样例见[结构审计 CSV](../research/20261122_tdx_remaining_unknown_path_audit.csv)。

- 28 个未知键在四类 TDX/ELTDX 文件中没有同名叶键；`name` 有 1,760 次，但全部位于 `raw_eltdx.json` 的 `global_helpers.realtime_rank.rows[].name`，并非 `raw_tdx.json` 的逐股 `quote_raw` 或 `quote_full` 路径。它属于 ELTDX 辅助实时榜单上下文，不能倒灌为 `TDX(双命名源)::name`。
- `pe_lyr` 的同名命中只在 `raw_zhb.json`；`vol_ratio` 的同名命中只在 `raw_market_sources.json` 的 KPL 板块强度记录；`market_snapshot` 的同名命中只在 FTShare 的 `market.market_snapshot`。这些是其他来源的具体路径，不是 TDX 原始字段。
- 五个 2026-11-21 裸行情别名的既有专项审计另有结论，仍以[`TDX 裸行情回退来源审计`](20261121_tdx_bare_quote_capture_provenance.md)为准；本轮不重复扩展其单日数值判断。
- 当前采集依赖固定为 [`easy_tdx-1.20.8`](../../../requirements.txt) 的本地 wheel。其 `SecurityQuote` 模型及 `GetSecurityQuotesCmd` 响应解析定义了当前快照适配器可输出的字段；其中没有 `pb`、`entrust_ratio`、`turnover_pct`、市值、PE/量比等扩展键。故这些在统一行情函数中的名称是 ZHB/Tencent 回退或包装值，不能当作本项目 TDX 原始响应字段；可见 [`easy_tdx` wheel](../../../vendor/easy_tdx-1.20.8-py3-none-any.whl)、[`core/tdx_client.py`](../../../core/tdx_client.py) 与 [`capture_tcp_collectors.py`](../../../scripts/capture_tcp_collectors.py)。

## 官方 TDX Quant 字段与接口边界

通达信量化平台公开文档覆盖多个接口，不能将接口名、返回字段名、项目 helper 键和 7709/TCP 采集器输出混为一体：

| 官方接口 | 精确字段 | 官方定义 | 项目内边界 |
|:---|:---|:---|:---|
| `get_stock_info` | `Name` | 证券名称 | PascalCase 官方路径；不等于小写包装键 `name` |
| `get_stock_info` | `ActiveCapital`、`J_zgb` | 流通股本、总股本（万股） | 与项目 0x0010、ELTDX 及 F10 提示解析输出分开登记 |
| `get_stock_info` | `J_mgjzc`、`J_mggjj`、`J_mgwfp` | 每股净资产、每股公积金、每股未分配 | 与 0x0010 总额字段不是精确路径别名 |
| `get_stock_info` 样例 | `ErrorId` | 样例中出现，值为 `0`；完整错误码表未公开 | 只确认该 API 样例有此键，不解释 `0` 的成功/失败语义 |
| `get_more_info_batch` | `Wtb`、`Ltsz`、`Zsz`、`PB_MRQ`、`MorePE`、`ZTPrice`、`DTPrice`、`fHSL`、`fLianB`、`CashZJ` | 委比、流通/总市值、市净率、扩展市盈率、涨跌停价、换手率、量比、货币资金 | 这些精确契约路径已在注册表按原代码登记；不自动映射到小写包装键 |
| `get_financial_data` | `FN4`、`FN8`、`FN202`、`FN281` | 每股净资产、货币资金、销售毛利率、加权净资产收益率 | 新增为官方精确路径；`FN202`“销售毛利率”与项目 F10 标签“营业毛利率”不直接等同 |

字段表及单位边界见[官方契约批量决定](20261122_tdx_official_field_contracts.json)：[证券基本信息 `get_stock_info`](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1h10jj7r7jol4.html)、[扩展行情 `get_more_info_batch`](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html)、[专业财务数据 `get_financial_data`](https://help.tdx.com.cn/quant/docs/markdown/TdxQuant.md/mindoc-1h10m001ic888.html)。这三类 TQ API 与项目当前 7709/TCP 适配器是不同接口族；官方定义用于建立精确契约锚，不证明本项目已调用或采集它们。

## 29 条路径逐项处理

| 当前路径 | 结论 | 依据 / 限制 |
|:---|:---|:---|
| `Date` | 裸路径退役；按完整接口路径登记 | 官方文档在行情、股本、个股日线资金、个股/板块/市场指标和公式结果等接口中分别使用 `Date`，定义为各自记录或计算结果的日期。裸 `TDX::Date` 没有接口/父对象，不能选定其中一个含义；8 个精确路径与官方出处见下节及[接口级日期裁决](20261122_tdx_scoped_date_contracts.json)。这不否定日期字段，也不把多个日期域合并。 |
| `ErrorId` | 官方契约确认 | `get_stock_info` 样例有精确键；错误码表和 0 的语义未说明，也未在当前 raw 采集中出现。 |
| `bvps` | 退役旧别名路径 | 当前项目实际 0x0010 字段为 `meigujingzichan`；官方 TQ 的 `FN4`/`J_mgjzc` 是不同精确接口路径，未据名称相似建立别名。 |
| `entrust_ratio` | 混合来源包装值 | 当前 `easy_tdx` 行情模型没有委比字段；统一行情函数可由 Tencent 回退填入同名值。保留包装值的业务含义，不保留其为 TDX 原始键的身份。 |
| `float_capital` | 项目派生输出 | `tdx_get_latest_reminders()` 从 F10“实际流通A股(万股)”文本解析后组装该键，归档位置应在 `reminders.latest_indicators.float_capital`；近 22 日提醒对象无实际值。官方 `ActiveCapital` 是另一接口的精确字段。 |
| `float_mcap_yi` | 混合来源包装键 | 只由 `tdx_get_quote_full()` 的复合回退值提供，可能来自腾讯；当前 TDX raw quote 无该键。官方 TQ `Ltsz` 仅为相近业务概念，不等同于该包装路径。 |
| `gross_margin` | 项目派生输出 | 财务 helper 从 TDX F10 “营业毛利率”标签取值，并可走计算/备用源分支；采集归档 `financial_analysis` 为空，故无实测输出值。官方 `FN202` 定义为“销售毛利率”，不据此合并。 |
| `huobi_zijin` | 退役文档伪路径 | 项目 0x0010 的 37 个字段中无此键；官方扩展接口真实代码是 `CashZJ`，单位万元。两代码不建映射。 |
| `limit_down` | 项目派生输出 | `tdx_get_quote_full()` 可调用 `tdx_get_price_limits()` 按昨收和证券规则计算，不是上游返回字段；官方 `DTPrice` 是另一路精确字段。 |
| `limit_down_price` | 混合来源包装键 | 复合行情的 Tencent 槽位 48 输出键；当前 `quote_raw` 不含该键。官方 `DTPrice` 只提供同名业务概念锚。 |
| `limit_up` | 项目派生输出 | TDX 快照函数按昨收及证券规则计算涨停价，缺值时复合包装还可由 Tencent 回退；输出键不是 TDX wire 字段。官方 `ZTPrice` 属于另一 TQ 接口路径。 |
| `locked_amount` | 退役错误来源身份 | 现有已验证路径属于 `TDX-eltdx(适配层)` 并有独立定义；本 `TDX(双命名源)` 路径在保留期 raw 中不存在，不移植另一来源语义。 |
| `long_term_debt` | 退役文档伪路径 | 项目文档旧别名不在 0x0010 原始字段中；`changqifuzhai` 是负债字段，不据此称为长期借款/债务。 |
| `market_snapshot` | 非字段 token | 在 TQ 文档中是接口名；在 FTShare 的 raw 另有自己的容器路径。不是 TDX 返回字段。 |
| `mcap_yi` | 混合来源包装键 | 复合行情从腾讯回退键取得；当前原始 TDX 行情不输出此路径。官方 TQ `Zsz` 是总市值契约路径，不自动映射。 |
| `meigugongji` | 退役文档伪路径 | 不是 0x0010 原始键；该记录包含“每股”提示，而 `zibengongjijin` 是总额字段。官方 `J_mggjj` 是另一接口精确路径。 |
| `meiguweifenpei` | 退役文档伪路径 | 不是 0x0010 原始键；`weifenpeilirun` 是总额字段。官方 `J_mgwfp` 是另一接口精确路径。 |
| `more_info` | 非字段 token | TQ 文档中的 `get_more_info_batch` 是接口名，不是名为 `more_info` 的返回字段。 |
| `name` | 混合来源包装键 | TDX 复合 quote 的小写键不是 raw TDX 输出；官方 API 使用精确 `Name`。ELTDX raw 中的 1,760 个同名叶键均位于 realtime rank helper，属于另一来源身份和嵌套路径。 |
| `pb` | 混合来源包装值 | 当前 `easy_tdx` 行情模型没有 PB；统一行情函数可由 ZHB/Tencent 回退填入。官方 `PB_MRQ` 是另一个接口中的不同完整路径。 |
| `pe_lyr` | 混合来源包装键 | 复合 quote 的该键从 Tencent 字段回退取得；保留 raw TDX 中无此键。官方 `MorePE` 的文档口径还按证券类型变化，不可仅凭命名合并。 |
| `pe_static` | 退役代码遗留键 | 当前代码已删除重复 `pe_static` 输出，只保留 Tencent `pe_lyr`；raw TDX 与保留样本中均无此键。 |
| `roe` | 项目派生输出 | TDX F10 helper 按“加权净资产收益率”标签取值，并可从公式或备用源补全；本批无实际归档值。官方 `FN281` 与 `J_jyl` 是各自接口中的不同路径，未作映射。 |
| `shiyebianma` | 退役文档伪路径 | 0x0010/当前代码使用 `industry`，没有 `shiyebianma` 返回键；不将历史错字登记为字段。 |
| `short_term_debt` | 退役文档伪路径 | 项目没有此原始键；`liudongfuzhai` 指流动负债，不等同于短期借款或短期债务。 |
| `total_capital` | 项目派生输出 | F10“总股本(万股)”文本解析器可组装该键，完整逻辑路径为 `reminders.latest_indicators.total_capital`；保留期提醒输出为空。官方 `J_zgb` 是另一接口精确代码。 |
| `turnover_pct` | 混合来源包装值 | 当前 `easy_tdx` 行情模型没有换手率字段；统一行情函数可由 ZHB/Tencent 回退填入。官方 TQ `fHSL` 是不同接口路径，不与包装键建立别名。 |
| `ushort` | 非字段 token | 这是协议类型 token，不是 JSON/适配器返回键；当前代码和保留期 TDX raw 均无该键。 |
| `vol_ratio` | 混合来源包装值 | 当前 `easy_tdx` 行情模型没有量比字段；统一行情函数可由 Tencent 回退填入。其它原始同名命中属于 ZHB/KPL 的独立路径；官方 TQ `fLianB` 不自动映射。 |

## 日期路径穷尽定位

官方 TQ 文档中的大写 `Date` 至少对应以下互不等价的完整路径。项目注册表已按接口和父对象登记；这些是官方契约字段，**不是**当前 7709/TCP 采集器的运行路径：

| 完整路径 | 已确认含义 | 官方契约 |
|:---|:---|:---|
| `get_market_data.Date` | 所请求周期的 K 线记录日期 | [K 线行情](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1h10g60jt68sc.html) |
| `get_gb_info_by_date[].Date` | 个股总股本/流通股本历史记录日期 | [时间段股本数据](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1hc4303vsv1fk.html) |
| `get_exday_data[].Date` | 个股日线资金统计记录日期 | [日线统计数据](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1hh9gktmqsv5c.html) |
| `get_gpjy_value.<GPxx>[].Date` | 个股交易/事件指标序列记录日期 | [股票交易数据](https://help.tdx.com.cn/quant/docs/markdown/TdxQuant.md/mindoc-1h10muc82r55k.html) |
| `get_bkjy_value.<BKxx>[].Date` | 板块指标序列记录日期 | [板块交易数据](https://help.tdx.com.cn/quant/docs/markdown/TdxQuant.md/mindoc-1h10p0ncmp5mc.html) |
| `get_scjy_value.<SCxx>[].Date` | 市场指标序列记录日期 | [市场交易数据](https://help.tdx.com.cn/quant/docs/markdown/TdxQuant.md/mindoc-1h10p8op6ia9g.html) |
| `formula_by_file.<stock>.<output>[].Date` | `return_date=True` 时公式输出值对应日期 | [公式文件计算结果](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1h3hrvkp4sc0g/mindoc-1hnil4jq8t5f4.html) |
| `formula_process_mul.<stock>.<output>[].Date` | `return_date=True` 时批量公式输出值对应日期 | [批量公式计算](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1h3hrvkp4sc0g/mindoc-1h4ad5lisvdfg.html) |

这些结论分别来自上游接口字段表或样例。股票、板块、市场序列中的日期只确定记录所属日期；事件型指标是否滞后披露，仍须按该指标的官方说明判断。`YYYYMMDD` 是值格式，不足以把来源记录日改称采集日、报告期或公告日。

## 注册表与保留边界

- 新增精确官方路径 `Name`、`ActiveCapital`、`J_zgb`、`J_mgjzc`、`J_mggjj`、`J_mgwfp`、`FN4`、`FN8`、`FN202`、`FN281`，并新增上述 8 个完整日期路径；将 `ErrorId` 登记为官方样例键。它们只确认官方接口契约，不表示本项目当前采集这些 TQ API，也未新增别名或跨源映射。
- 对原 29 项中的 27 条非 `Date`/`ErrorId` 路径添加完整原状态快照和退出理由；另将无接口限定的裸 `Date` 以同样证据流程退役。已有的 `TDX-eltdx(适配层)::locked_amount`、0x0010 财务字段及其它来源同名路径身份不变。
- 本轮原 TDX 未知路径队列已闭环；日期字段没有被当作残留删除，而是拆到已核实的接口级业务域。没有将目录日期冒充来源日期，没有执行真实采集或改变路由。
- 各源文件仅用结构扫描计算键路径。无来源 `as_of_date` 的日期目录未用于行情新鲜度或数值比较；没有执行真实采集或改变路由。
