# 2026-11-18 KPL `main_buy` / `main_sell` 来源内语义核验

## 裁决范围

本次核验精确限定为项目 KPL 涨停明细 `DailyLimitPerformance` 的归一化字段 `main_buy`、`main_sell`，即注册表身份 `开盘啦(kpl)::main_buy` 与 `开盘啦(kpl)::main_sell`。适配器 [`stock_common/sc_kpl.py`](../../../stock_common/sc_kpl.py) 的 `get_kpl_limit_up_detail()` 请求 `a=DailyLimitPerformance`，将响应 `row[9]`、`row[10]` 分别写入这两个字段，并在保留 raw 时分别保存为 `raw_columns.col_09`、`raw_columns.col_10`；同一行 `row[8]` 写为 `main_inflow`。

本裁决不把 `main_inflow` 扩展成另一个接口的 `main_net`，也不验证 KPL 的资金分类阈值、主力识别算法或跨来源等价关系。

## 官方产品标签和接口路径证据

开盘啦官网行情页 [https://www.kaipanla.com/page](https://www.kaipanla.com/page) 在“市场风口”个股表中并列展示“主力净额”“主力买入”“主力卖出”。官网前端 [`mp.js`](https://www.kaipanla.com/js/part/mp.js) 的 `mp2_.getLiDet_scfk()` 将官方行情对象 `ZLJE`、`ZLBuy`、`ZLSell` 分别渲染到这三列；请求由该页面发送至 `StockFengKData::GetIndexFengKList`。官网 [`com.js`](https://www.kaipanla.com/js/com.js) 的 `changeStand()` 将大额数值按 10,000 显示为“万”、按 100,000,000 显示为“亿”，支持原始资金金额单位为元。

官网页面这个“市场风口”请求与项目使用的 `DailyLimitPerformance` 是不同接口，因此官网前端只作为开盘啦自身字段标签和金额显示口径的证据，不冒充 `DailyLimitPerformance` 的原始列契约。未登录直查官网行情接口返回 `errcode=1016, errmsg=未登录`；没有重试，也没有把它当作任何历史值匹配证据。

项目字段索引与第三方公开逆向资料互相对应：[LowellLee/kpl 的 `KPL接口.md`](https://github.com/LowellLee/kpl/blob/master/KPL%E6%8E%A5%E5%8F%A3.md) 对同名 `DailyLimitPerformance` 响应样例将数组第 9、10 项（零基 `row[8]`、`row[9]`、`row[10]`）标为主力净额、主力买入、主力卖出。该资料不是开盘啦官方接口合同，本次仅用它定位候选数组项；最终限定由项目当前适配器的精确索引、原始数组留档、官网同产品字段标签和下列完整样本关系共同支持。

## 保留期样本核验

样本来自 2026-10-15（`scripts/capture_retention.py::MIN_CAPTURE_DATE`）至 2026-11-17 的 20 个 KPL 来源交易日归档。每份 `meta.json.sources.kpl.as_of_date` 都存在、状态均为 `ok`，并与 `raw_kpl.json.trade_date` 和目录目标交易日一致；日期通过格式归一比较。历史 `DailyLimitPerformance` 请求显式携带 `Day` 参数。自然日 `capture_date` 在这 20 份文件中也与来源数据日一致，但不作为来源日期依据。样本完整明细和复算列见 [`20261118_kpl_money_field_sample_audit.csv`](../research/20261118_kpl_money_field_sample_audit.csv)，规范 LF SHA-256：`114255e6858802d9a44e0bbd9afb386ac1afd4865268ae30c0c0f7de291ad014`。

- 20 日合计 1,195 条股票记录，覆盖 747 只不同股票；所有记录均满足 `main_inflow = main_buy + main_sell`，无反例。
- 其中 1,165 条保留了完整原始列；覆盖 730 只不同股票。`col_08/09/10/11` 与适配器归一字段逐值完全一致，索引比对 1,165/1,165 命中，无错位。
- 30 条旧归档没有 `raw_columns`，不计入原始索引核验，但其归一字段仍纳入 1,195 行算术关系复核；其余信息不用于填补 raw 列证据。
- 1,195/1,195 条 `main_buy >= 0`，且 `main_sell <= 0`。这支持 `main_sell` 是以负值表示卖出流出的金额分量。
- 最新来源日 2026-11-17 的 002451（摩恩电气）为：净额 31,676,471 元、买入 36,371,569 元、卖出 -4,695,098 元，等式精确成立。

## 定案

`开盘啦(kpl)::main_buy` 定义为 KPL 涨停明细中的主力买入金额，单位元；`开盘啦(kpl)::main_sell` 定义为主力卖出金额，单位元，原值以负号表示流出。该结论确认业务字段角色、符号和单位；不声称掌握开盘啦内部主力分类阈值或资金算法，不将它们映射到其他数据源。虽然官网未公开 `DailyLimitPerformance` 的数组下标契约，本次结合官方产品字段、项目实际路径和完整留存样本已足以确定字段释义；因此不再因缺少正式 API 列号文档而搁置。

官网核验时间：2026-11-18 02:04 Asia/Shanghai。页面和脚本读取链接列于上文；官网值接口的登录限制如实记录，不把失败请求重复为采集或重试。
