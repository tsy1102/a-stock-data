# 东方财富 IPO 首日表现与申购字段来源契约裁决

复核日期：2026-11-20

## 裁决范围

本次仅确认 `东财-event_dc(IPO发行记录)` 的 19 条完整来源路径。项目调用 `RPTA_APP_IPOAPPLY`，`ipo_calendar()` 将数据中心 `result.data[*]` 的字段原样保留到 `raw_event_dc.ipo_calendar[]`，仅附加追踪信息；没有把其它接口、详情页派生字段或同短码的其它接口路径并入。

| 完整来源路径 | 定案含义 | 单位 | 样本/边界 |
|---|---|---|---|
| `ipo_calendar[].OPEN_PRICE` | 上市首日开盘价 | 元/股 | 留存记录 20/20 有值 |
| `ipo_calendar[].LD_OPEN_PREMIUM` | 上市首日开盘溢价；留存样本符合 `(OPEN_PRICE / ISSUE_PRICE - 1) × 100` | % | 20/20 公式误差不超过 0.01 个百分点 |
| `ipo_calendar[].LD_CLOSE_CHANGE` | 上市首日收盘价相对发行价的涨幅；留存样本符合 `(CLOSE_PRICE / ISSUE_PRICE - 1) × 100` | % | 20/20 公式误差不超过 0.01 个百分点；与 `TOTAL_CHANGE` 区分 |
| `ipo_calendar[].TURNOVERRATE` | 上市首日换手率 | % | 留存记录 20/20 有值 |
| `ipo_calendar[].LD_HIGH_CHANG` | 上市首日最高涨幅 | % | 页面明确字段标签；本次不外推更细的基准价公式 |
| `ipo_calendar[].LD_AVERAGE_PRICE` | 上市首日成交均价 | 元/股 | 留存记录 20/20 有值 |
| `ipo_calendar[].OPEN_DATE` | 开板日期 | 日期 | 不等同于上市日期；早期样本恰好 20/20 与 `LISTING_DATE` 相同 |
| `ipo_calendar[].OPEN_AVERAGE_PRICE` | 开板日均价 | 元/股 | 不与 `LD_AVERAGE_PRICE` 合并；早期样本 20/20 相同是因开板日与上市日重合 |
| `ipo_calendar[].CONTINUOUS_1WORD_NUM` | 连续一字板数 | 板 | 注册制页面不统计该项；留存样本 20/20 均为 1，未用恒定值推断语义 |
| `ipo_calendar[].INFO_CODE` | 招股说明书/意向书 PDF 链接使用的文档代码 | — | 留存记录 13/20 有值；缺值不代表代码为零 |
| `ipo_calendar[].IS_REGISTRATION` | 东方财富页面用于区分注册制与审批制展示分支的标记；`1` 表示注册制，`0` 表示非注册制分支 | — | 留存早期记录全为 `0`；另以东方财富 001365 详情页 `1` 核对另一分支。未解释其它可能编码 |
| `ipo_calendar[].ONLINE_ISSUE_NUM` | 网上发行股数 | 股 | 留存 1988—1993 记录 0/20 有值；官方页面按万股展示，详情记录 300059 的原值为 28,000,000 股 |
| `ipo_calendar[].TOP_APPLY_MARKETCAP` | 网上顶格申购所需配售市值 | 万元 | 留存记录 0/20 有值；300059 详情页值 28，与“万元”标签一致 |
| `ipo_calendar[].ONLINE_APPLY_UPPER` | 网上申购数量上限 | 股 | 留存记录 0/20 有值；300059 详情页原值 28,000 股 |
| `ipo_calendar[].BALLOT_NUM_DATE` | 中签号码公布日期 | 日期 | 留存记录 0/20 有值；300059 详情页日期 2010-03-12，与深交所公告日期相符 |
| `ipo_calendar[].BALLOT_PAY_DATE` | 按该 IPO 发行安排缴纳申购/中签认购款的日期 | 日期 | 留存记录 0/20 有值；300059 详情页为 2010-03-09，与申购日相同。2009 年深交所资金申购办法要求 T 日缴足申购款；不能把此字段固定解释为 T+2 |
| `ipo_calendar[].ONLINE_ISSUE_LWR` | 网上发行中签率 | % | 留存记录 0/20 有值；300059 值 0.8387405891，与深交所公告的 0.8387405891% 一致 |
| `ipo_calendar[].INITIAL_MULTIPLE` | 初步询价累计报价倍数 | 倍 | 留存记录 0/20 有值；详情页以该字段直接填充此项 |
| `ipo_calendar[].OFFLINE_EP_OBJECT` | 网下配售对象报价家数 | 家 | 留存记录 0/20 有值；官方新股页字段列标题为“配售对象报价家数” |

“留存记录”是 2026-11-19 目标数据日归档中的一次 `RPTA_APP_IPOAPPLY` 响应，包含 20 条不同股票的历史发行记录；事件申购日期为 1988-12-28 至 1993-11-22。20 行不是 20 个独立采集日。缺少值的字段不据此推定为零或无效；官方页面键名、显示标签和渲染行为用于直接来源契约定案，未用这些空值做经验碰撞。

## 首日涨幅字段与原未决项

东方财富[新股申购页](https://data.eastmoney.com/xg/xg/?mkt=zh)当前前端请求 `RPTA_APP_IPOAPPLY`，请求列中包含本表字段。页面将首日表现字段分别绑定到“首日开盘价”“首日开盘溢价”“首日收盘价”“首日收盘涨幅”“首日换手率”“首日最高涨幅”“首日成交均价”，另将 `OPEN_DATE`、`CONTINUOUS_1WORD_NUM`、`OPEN_AVERAGE_PRICE` 分别绑定到“开板日期”“连续一字板数”“开板日均价”。官方前端脚本 [`xglist.js`](https://data.eastmoney.com/newstatic/js/xg/xglist.js) 明确请求这些原始键；详情页 [`300059`](https://data.eastmoney.com/xg/xg/detail/300059.html) 和 [`001365`](https://data.eastmoney.com/xg/xg/detail/001365.html) 提供记录级键值与详情标签。

留存样本中 `LD_OPEN_PREMIUM` 的公式误差最大为 `4.736842105263e-13` 个百分点；`LD_CLOSE_CHANGE` 的公式误差最大为 `0.0000680672269` 个百分点，均远低于 0.01 个百分点容差。另以留存 `AVERAGE_PRICE` 复算 `TOTAL_CHANGE`，20/20 误差不超过 0.02 个百分点，最大误差为 `0.004285714286` 个百分点；20 条中有 19 条的 `LD_CLOSE_CHANGE` 与 `TOTAL_CHANGE` 不同。东方财富 300059 详情记录同时显示 `CLOSE_PRICE=58.35`、`ISSUE_PRICE=40.58`、`LD_CLOSE_CHANGE=43.79` 与 `TOTAL_CHANGE=47.63`；前者按首日收盘价复算，后者按首日成交均价复算。由此，完整路径 `RPTA_APP_IPOAPPLY -> ipo_calendar[].LD_CLOSE_CHANGE` 可确认是首日收盘涨幅；它与 `TOTAL_CHANGE` 不是同一口径。北交所另一个接口即使复用短键 `LD_CLOSE_CHANGE`，也不会改变本路径的身份和含义。

`OPEN_DATE` 与 `OPEN_AVERAGE_PRICE` 在早期样本分别与 `LISTING_DATE`、`LD_AVERAGE_PRICE` 逐行相同，但官方详情页给出的事件名称不同，且早期记录均在上市首日开板；因此保留为独立字段，不建立别名关系。`CONTINUOUS_1WORD_NUM` 在 20 条记录中恒为 1，只作为覆盖事实记录；其释义来自页面字段标签和注册制不统计该指标的前端分支，不来自碰撞。

## 日期边界

东方财富详情页将 `BALLOT_NUM_DATE` 标为中签号公布日期，将 `BALLOT_PAY_DATE` 标为中签缴款日期。300059 的东方财富记录中，申购日与缴款日均为 2010-03-09，中签号公布日为 2010-03-12。深交所《资金申购上网公开发行股票实施办法（2009 年修订）》规定，投资者在申购日 T 日缴足申购款，摇号及后续处理另按 T+2/T+3 安排；深交所 2010-03-11 公告确认 300059 的中签结果于 2010-03-12 公布。因此，`BALLOT_PAY_DATE == APPLY_DATE` 是符合该历史发行制度的日期，不是采集日期错位。该字段只定为具体发行安排中的缴款日，不承诺固定为申购日或 T+2；`BALLOT_NUM_DATE` 与缴款日是不同事件日期。

## 项目调用链和证据

- 项目定义 [`_events.py`](../../../stock_common/sc_datasource/_events.py)：`ipo_calendar` 使用 `RPTA_APP_IPOAPPLY`，由 `ipo_calendar()` 调用东财数据中心并附加追踪元数据。
- [`_eastmoney.py`](../../../stock_common/sc_datasource/_eastmoney.py) 将请求交给 [`_datacenter.py`](../../../stock_common/sc_datasource/_datacenter.py)；后者返回 `result.data` 行字典，不重命名字段或改写数值。
- 东方财富[新股申购页](https://data.eastmoney.com/xg/xg/?mkt=zh)和[详情页](https://data.eastmoney.com/xg/xg/detail/300059.html)是字段键与页面标签的官方契约；页面脚本 [`xglist.js`](https://data.eastmoney.com/newstatic/js/xg/xglist.js) 请求 `RPTA_APP_IPOAPPLY`。注册制分支另核对[001365 详情页](https://data.eastmoney.com/xg/xg/detail/001365.html)。官网未提供版本化字段 schema，故页面和脚本按 2026-11-20 复核日期固定。
- 300059 发行事件核对：[深交所网上申购情况及中签率公告](https://disc.static.szse.cn/disc/disk01/finalpage/2010-03-11/3e5fdce2-a9c6-43ac-aecc-a564f527e765.PDF)、[深交所 2009 年资金申购实施办法](https://docs.static.szse.cn/www/lawrules/rule/stock/issue/W020220328389449415588.pdf)。
- 原始归档：`docs/field_verification/20261119/raw_event_dc.json`，SHA-256 `41fe019b29d038e1cf4726f69700af303aae0206a6fdb8d7399912290065b091`；元数据 `docs/field_verification/20261119/meta.json`，SHA-256 `c33dd40b7f340d0009987b4889f421c6bef8cf543f91b5caff0ce3501f07fe7f`。归档的 `data_date` 和目录名均为 2026-11-19，采集日期为 2026-11-20。
- 20 条记录的原值、字段覆盖、公式结果和精确误差见[逐条样本 CSV](../research/20261120_eventdc_ipo_first_day_contract_samples.csv)。CSV 规范 LF SHA-256：`fdcd685ea570d06e84684381be5c548464608e4f3d9f7f160f5c56c308c1b9c9`。

本裁决仅确认以上 19 个东方财富 IPO 完整字段路径，不建立跨来源映射，不将相同数值、空值、早期日期重合或相同短码作为字段等价依据；不更改采集逻辑。修复此前 `LD_CLOSE_CHANGE` 留待可比北交所样本的结论：本项目路径有精确 IPO 接口和页面字段绑定，先前把另一个接口的同短码语义混入该身份是不必要的范围扩大。
