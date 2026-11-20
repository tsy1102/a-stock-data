# 深交所 ETF 当前规模数据日期裁决

## 裁决

`沪深交易所::etf_sz.date` 定义为深交所官方 ETF 列表中“当前规模（万份）”数值对应的统计日期。项目将 `metadata.cols.dqgm` 列标题括号内的日期写入 `date`，该日期与同一行的 `shares_10k` 对应；它不是列表响应日期、采集运行日或目录目标数据日。该裁决只适用于深交所 ETF 分支，不建立与上交所或其他来源的字段映射。

## 官方响应证据

2026-11-20 21:36:59–21:37:00（北京时间）以一次只读 GET 请求访问深交所基金业务专区 ETF 列表接口，HTTP 200。请求参数为 `SHOWTYPE=JSON`、`CATALOGID=1000_lf`、`TABKEY=tab1`、`selectJjlb=ETF`、`PAGENO=1`、`pagesize=2000`。接口返回 772 条记录，实际分页大小为 20。

| 响应字段 | 官方响应值 | 对日期释义的作用 |
|---|---|---|
| `metadata.name` | `基金列表` | 确认响应为官方基金列表 |
| `metadata.subname` | `2026-11-20` | 列表响应的页面日期 |
| `metadata.cols.dqgm` | `当前规模（万份）…该字段T日晚间更新的T日规模仅供参考，以T+1日早间更新的T日规模为准…（2026-11-19）` | 明确“当前规模”对应 2026-11-19；并说明 T+1 日早间更新值才是 T 日规模的准值 |

同一响应中的页面日期为 11 月 20 日，而当前规模列标题日期为 11 月 19 日。因此不能将 `metadata.subname` 当作 `shares_10k` 的数据日。页面栏目及数据由[深交所基金业务专区 ETF 列表](https://fund.szse.cn/marketdata/etf/)及其[官方列表接口](https://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1000_lf&TABKEY=tab1&selectJjlb=ETF&PAGENO=1&pagesize=2000)提供。

## 项目路径核对

`stock_common/sc_datasource/_etf.py::_etf_shares_szse_host()` 解析 `metadata.cols.dqgm` 的唯一日期，将其作为每条 ETF 行的 `date`；同一行 `dqgm` 数字仍解析为 `shares_10k`。分页时要求页面日期、规模列日期、页数和总数一致。缺失、含多个或日历上无效的列头日期均失败关闭，不能静默回退到页面日期。

采集器为新 SZ 行写入 `__source_meta__.date_basis=szse_current_scale_column_header`。碰撞与证据覆盖只接受带该标记的行。修复前生成的历史行没有保存列头日期口径，不能由当前接口响应倒推其历史列头；因此旧 SZ ETF 行继续排除于正式日期碰撞，保留原始归档且不改写。后续经授权的新采集会自然生成符合该来源日期契约的样本。

## 范围边界

本裁决解决日期语义和样本资格，不调整 ETF 其他字段的释义或采集频率。KPH（开盘红）与 KPL（开盘啦）仍是不同产品及来源族，本裁决不触及二者，也不建立 KPH/KPL 字段映射。
