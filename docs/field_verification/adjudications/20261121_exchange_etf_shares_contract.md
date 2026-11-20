# 2026-11-21 沪深交易所 ETF `shares_10k` 来源契约核验

## 裁决

分别登记以下来源内路径：

- `沪深交易所::etf_sh.shares_10k`：上交所 ETF 规模接口中的基金总份额，单位“万份”。
- `沪深交易所::etf_sz.shares_10k`：深交所 ETF 列表“当前规模（万份）”列中的基金份额数值，单位“万份”；统计日期按已定案的 `etf_sz.date` 解释。

两条路径分别对应上交所和深交所各自的官方接口与列语义。本裁决只登记来源内含义，不创建沪深字段映射，也不据此认定两个接口同源或数据可互换。字段不表示以人民币计价的资产净值或市值。

## 上交所 `etf_sh.shares_10k`

上交所官方 [ETF 规模页面](https://www.sse.com.cn/market/funddata/volumn/etfvolumn/) 将 ETF 规模列标为“总份额（万份）”，并注明统计数据为当日清算后数据。项目 [`_etf.py`](../../../stock_common/sc_datasource/_etf.py) 的 `_etf_shares_sse(day)` 请求上交所官方 `query.sse.com.cn/commonQuery.do` 接口，使用 `sqlId=COMMON_SSE_ZQPZ_ETFZL_XXPL_ETFGM_SEARCH_L` 和 `STAT_DATE=day`；逐行检查响应 `STAT_DATE` 与请求日期一致后，将响应 `TOT_VOL` 映射为 `etf_sh[].shares_10k`。

保留样本 [`20261119/raw_etf.json`](../20261119/raw_etf.json) 的 SHA-256 为 `4A4C54D843BB406734A481387A2FBF9B911CEF38DC219AA592D4D88C9B2FECB1`。该文件的 `etf_sh` 分支含 925 行，`shares_10k` 均非空。对官方 ETF 详情页可核验的两个同日样本逐值比较如下：

| 代码 | 来源日期 | 项目 `shares_10k` | 上交所页面“总份额（万份）” | 结果 |
|---|---|---:|---:|---|
| 561160 | 2026-11-18 | 236933.50 | 236933.50 | 相等 |
| 589150 | 2026-11-18 | 99343.72 | 99343.72 | 相等 |

对应的上交所官方详情页：[561160 电池ETF富国](https://www.sse.com.cn/assortment/fund/list/etfinfo/basic/index.shtml?FUNDID=561160)、[589150 科创50ETF平安](https://www.sse.com.cn/assortment/fund/list/etfinfo/basic/index.shtml?FUNDID=589150)。两页的历史“基金规模”表都明确显示日期、基金代码、扩位简称和“总份额（万份）”；项目保留值与 2026-11-18 官方值一致。这将官方列语义与项目对不透明响应键 `TOT_VOL` 的映射连接起来。

## 深交所 `etf_sz.shares_10k`

2026-11-20 21:36:59–21:37:00（北京时间）读取深交所基金业务专区官方 ETF 列表接口，HTTP 200，响应含 772 条记录。官方响应 `metadata.cols.dqgm` 将列标为“当前规模（万份）”，并说明 T 日晚间更新的 T 日规模仅供参考，以 T+1 日早间更新的 T 日规模为准；同一列标题的括号日期为 2026-11-19。响应页面日期 `metadata.subname` 为 2026-11-20，与列数据日期不同。

项目 `_etf_shares_szse_host()` 从每条记录 `dqgm` 的 HTML 数字中解析数值并写入 `etf_sz[].shares_10k`；同时从同一响应 `metadata.cols.dqgm` 列标题解析唯一日期并写入 `etf_sz[].date`。分页校验要求各页列日期一致。对应的日期语义、响应观察和日期资格边界已在[深交所 ETF 当前规模数据日期裁决](20261120_szse_etf_scale_data_date.md)记录；本次依据同一官方列定义补齐数值字段，不把列表页面日期当作规模数据日期。

官方入口：[深交所基金业务专区 ETF 列表](https://fund.szse.cn/marketdata/etf/)；[官方列表接口](https://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1000_lf&TABKEY=tab1&selectJjlb=ETF&PAGENO=1&pagesize=2000)。

## 结论边界

- 已确认两条完整路径的官方列含义、单位及项目响应到输出字段的映射。
- 上交所样本核验是 2/2 精确匹配；不外推为对所有 925 条记录的逐条网页复核。
- 深交所 `shares_10k` 依官方 `dqgm` 列定义登记；T 日晚间值与 T+1 日早间最终值的更新时间差异仍按官方提示处理。
- 不因两边单位同为“万份”而创建跨所 `mappings` 或合并来源身份。
