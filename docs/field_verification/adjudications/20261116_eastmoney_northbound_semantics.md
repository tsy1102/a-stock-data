# 东方财富北向持仓字段复核（2026-11-16）

## 范围与日期资格

本次精确核对来源身份 `东财-datacenter(英文键)::northbound_hold.*`，代码入口为 `stock_common/sc_datasource/_eastmoney.py::get_northbound_hold` 与异步版本。没有运行生产采集；复核使用既有归档和公开网页/接口查询。

依照 [`capture_retention.py`](../../../scripts/capture_retention.py) 的 `MIN_CAPTURE_DATE = 2026-10-15`，样本表 [`20261116_eastmoney_northbound_capture_sample.csv`](../research/20261116_eastmoney_northbound_capture_sample.csv) 汇总了 17 个保留目录、238 条股票记录。按每条记录的 `TRADE_DATE` 去重后仅剩 `2026-06-30`、`2026-09-30` 两个来源日期；17 个采集目录不是 17 个独立来源日期。样本文件规范 LF SHA-256：`2b2f24315e885ab0812fc9d84a55a40f5caac484e124b2ccf165075c20828e65`。归档的 `raw_datacenter.json` 是项目适配后的记录，不能单独证明上游响应键是否存在。

## 上游接口与代码映射

两种适配器均请求东方财富数据中心 `RPT_MUTUAL_HOLDSTOCKNORTH_STA`，并将响应映射为 `northbound_hold[]`：

| 项目路径 | 上游字段 / 转换 | 复核结论 |
|:--|:--|:--|
| `northbound_hold.date` | `TRADE_DATE` 截取前 10 位 | 记录数据日期；2026-11-11 已按官方“持股日期”说明定案，本次不改。 |
| `northbound_hold.hold_shares` | `HOLD_SHARES` | 北向持股数量，单位股。 |
| `northbound_hold.market_cap` | `HOLD_MARKET_CAP`，回退 `MARKET_CAP` | 北向持股市值，单位元；同记录等于持股数量乘收盘价。 |
| `northbound_hold.hold_ratio` | 优先 `FREE_SHARES_RATIO`，再回退 `A_SHARES_RATIO`、`TOTAL_SHARES_RATIO`、`HOLD_RATIO` | 北向持股比例，百分数刻度。具体分母取决于实际命中的上游键；不能把数值不同的回退键合并成一个固定分母口径。 |
| `northbound_hold.change_ratio` | `CHANGE_RATE` | 持股记录日对应证券的当日涨跌幅（%），不是持股比例的期际变化。 |
| `northbound_hold.change_shares` | 旧代码读取 `CHANGE_SHARES`，缺失时填 0 | 直接核验的 600519、601288 两条 2026-09-30 响应均未返回该键；旧归档的零值为代码默认值，不能解释为真实“持股未变化”。标记为项目派生占位，不作为提供方未知字段继续破解。 |

官方入口：[东方财富沪深港通持股页面](https://data.eastmoney.com/hsgtV2/hsgtDetail/ggzj.html)、[东方财富个股统计页面](https://data.eastmoney.com/hsgtcg/StockStatistics.html)。东方财富个股持股详情页面的表格以“持股日期”“持股数量”“持股市值”“持股数量占 A 股百分比”“当日涨跌幅”等字段呈现持股记录。

直接核验的上游查询（`columns=ALL`，代码和日期按项目适配器参数）为：[600519](https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_MUTUAL_HOLDSTOCKNORTH_STA&columns=ALL&filter=%28SECURITY_CODE%3D%22600519%22%29&pageNumber=1&pageSize=20&sortColumns=TRADE_DATE&sortTypes=-1&source=WEB&client=WEB) 与 [601288](https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_MUTUAL_HOLDSTOCKNORTH_STA&columns=ALL&filter=%28SECURITY_CODE%3D%22601288%22%29&pageNumber=1&pageSize=20&sortColumns=TRADE_DATE&sortTypes=-1&source=WEB&client=WEB)。两条 2026-09-30 记录都有 `CHANGE_RATE`、`CLOSE_PRICE`、`HOLD_SHARES`、`HOLD_MARKET_CAP` 和比例字段，没有 `CHANGE_SHARES`。项目代码旧表达式 `float(row.get("CHANGE_SHARES") or 0)` 因此把缺失伪装为 0。

## 数值复核

| 股票 / 来源日 | 持股数量 | 持股比例键值 | 持股市值 | 当日涨跌幅接口值 | 同日收盘价计算 |
|:--|--:|--:|--:|--:|--:|
| 贵州茅台 600519 / 2026-09-30 | 55,263,682 股 | `FREE_SHARES_RATIO=4.4208` | 69,555,975,438.84 元 | 1.864711309668% | `(1258.62 / 1235.58 - 1) × 100 = 1.864711309668321%` |
| 中国农业银行 601288 / 2026-09-30 | 1,526,471,802 股 | `FREE_SHARES_RATIO=0.4782` | 10,639,508,459.94 元 | 0.432276657061% | `(6.97 / 6.94 - 1) × 100 = 0.4322766570605152%` |

两行的市值分别严格等于 `HOLD_SHARES × CLOSE_PRICE`。茅台 2026 年第三季度报告列示香港中央结算有限公司持股 55,263,682 股、持股比例 4.42%；数据中心 4.4208% 经页面显示精度四舍五入后为 4.42%。[公司三季报（巨潮资讯）](https://static.cninfo.com.cn/finalpage/2026-10-31/1225649896.PDF)

直接 K 线核对使用东方财富日 K 线端点 `push2his.eastmoney.com/api/qt/stock/kline/get`，周期 `klt=101`、不复权 `fqt=0`、截至 `2026-10-01`；两股 2026-09-29 / 2026-09-30 收盘价分别为 `1235.58 / 1258.62` 和 `6.94 / 6.97`。接口 `CHANGE_RATE` 与同日收盘变动按百分数公式吻合到接口返回精度。

## 定案边界

- `hold_shares` 定案为北向持股数量，单位 `股`。
- `hold_ratio` 定案为北向持股比例，单位 `%`；适配器当前优先使用 `FREE_SHARES_RATIO`。当该键缺失而命中回退键时，分母口径须随实际响应键保留，不据此宣称不同键定义完全相同。
- `market_cap` 定案为北向持股市值，单位 `元`。
- `change_ratio` 的旧释义“较上一期持股比例增减变动幅度”错误；现定案为持股记录日证券的当日涨跌幅，单位 `%`。
- `change_shares` 的历史 238 条输出全为 0，但来源日期仅两个，且直接查询没有 `CHANGE_SHARES` 键。代码修复后，缺失/NaN 作为 `None`，真实显式 0 仍为 0；报告中缺失显示为“—”。只证伪该完整来源路径在当前接口响应中的上游字段身份，不推断其他来源或其他接口，也不从相邻持仓快照擅自计算变动股数。
- 原始采集归档不改写。本地 CSV 回退仍保留；旧 CSV 没有“上游字段缺失”与“真实零值”的区分，故回退时将变动字段的零值作为未知 `None`，非零值保留。CSV 不用于推断上游字段定义。若未来接口开始提供 `CHANGE_SHARES`，应按新响应结构重新核验并更新注册表。
- 不建立任何跨来源 `mappings`。
