# 2026-11-20 上交所 ETF 与央视《新闻联播》日期字段核验

## 裁决结果

- 登记 `沪深交易所::etf_sh.date` 为上交所 ETF 规模统计记录的统计日期，规范名 `sse_etf_scale_statistics_date`。
- 将运行路径 `news_wscn_cctv.date` 按精确来源身份 `央视网(新闻联播)::date` 登记为《新闻联播》按日栏目页对应的节目期次日期，规范名 `cctv_news_broadcast_edition_date`。
- `沪深交易所::etf_sz.date` 暂不定案。现有样本显示它随深交所列表快照改变，但尚未找到可核实 `metadata.subname` 业务含义的深交所正式字段说明。
- 本批不创建跨源字段映射。KPH（开盘红）和 KPL（开盘啦）仍是不同产品、不同来源身份；本批与其来源登记无关。

## 日期口径与样本来源

样本表 [`research/20261120_exchange_cctv_date_samples.csv`](../research/20261120_exchange_cctv_date_samples.csv) 对每行分别记录目录数据日、来源级采集日和来源级开始时间。这里不使用 `meta.json` 的全局 `capture_date`：这些归档后来经过补采或元数据更新，全局日期可能晚于原始文件中 ETF/CCTV 适配器的实际运行时点。来源级日期与开始时间取自同一目录 `meta.json` 的 `sources.etf` 或 `sources.news_wscn_cctv`。

- CSV 规范 LF SHA-256：`5f38eec4270b13c63d44bd61c3cedcedffc99b6d928e7d56093bab6c4834d777`
- 样本覆盖 5 个目录数据日：2026-11-12、11-16、11-17、11-18、11-19；它们不是连续的 5 个交易日样本。
- 每行 `raw_archive_sha256` 校验对应原始 JSON。样本数按来源实际字段值及原始记录计，不将重复归档伪作独立日期。

## `沪深交易所::etf_sh.date`

### 官方与代码契约

上交所官方 [ETF 规模页面](https://www.sse.com.cn/market/funddata/volumn/etfvolumn/) 将该数据标为 ETF 规模，并注明“统计数据为当日清算后数据”。项目 `stock_common/sc_datasource/_etf.py::_etf_shares_sse(day)` 请求上交所 `query.sse.com.cn/commonQuery.do`，SQL ID 为 `COMMON_SSE_ZQPZ_ETFZL_XXPL_ETFGM_SEARCH_L`，参数 `STAT_DATE=day`；逐行校验上游 `STAT_DATE` 必须与请求日相等，随后将该值输出到 `date`。`scripts/capture_context_collectors.py::collect_etf` 按近期交易日尝试，使用首个非空响应。因此目录数据日、采集日和 ETF 记录日期不保证相同，字段值应按其上游 `STAT_DATE` 解释。

据此将精确路径 `沪深交易所::etf_sh.date` 定为上交所 ETF 规模记录的统计日期。它不是运行自然日或目录目标数据日。单位为 `YYYY-MM-DD`。

### 保留样本

5 个归档中 SH 分支各有 924 或 925 条，日期分别为 11-12、11-13、11-16、11-17、11-18；每个文件内日期单一，且已确认原始上游日期通过 `STAT_DATE` 校验后才会被输出。11-16 目录中的 SH 日期为 11-13，展示了来源回退后的实际数据日，不能用目录名覆盖它。

## `央视网(新闻联播)::date`

### 官方与代码契约

央视网 [《新闻联播》栏目页](https://tv.cctv.com/lm/xwlb/index.shtml) 按日期展示节目期次。抽核的官方页面包括 [2026-11-12 条目](https://tv.cctv.com/2026/11/12/VIDEmGNuJ8IaG638qS9sl51D261112.shtml)、[2026-11-16 完整节目](https://tv.cctv.com/2026/11/16/VIDEZ8Ck8e5IUIbA9cP3lAl8261116.shtml) 和 [2026-11-18 条目](https://tv.cctv.com/2026/11/18/VIDEBxzPhCzDOvbKcE9Y2PVV261118.shtml)。官方标题或页面更新时间标明相应期次日；例如 11-16 页面标题为“《新闻联播》20261116 21:00”，来源时间为 2026-11-16 21:39。

项目 `stock_common/sc_datasource/_news_wscn_cctv.py::cctv_news(date)` 将输入日期格式化为 `YYYYMMDD` 并请求 `https://tv.cctv.com/lm/xwlb/day/{ymd}.shtml`，输出记录的 `date` 由该栏目页请求日期生成。`scripts/capture_context_collectors.py::collect_news_wscn_cctv` 在近期自然日中选择首个有条目的栏目页。故该字段准确表示记录所属的栏目页/节目期次日期，不表示单条新闻事件发生日、单条报道的独立发布时间或本次采集日。

### 保留样本

5 次归档共 69 条记录，来源级采集日为 11-12、11-16、11-17、11-18、11-19，字段实际出现的期次日为 11-12、11-16、11-17、11-18。11-17 目录的 17 条记录与 11-16 目录具有相同原始归档 SHA-256，且都属于 11-16 期；该副本只用于确认“期次日不等于采集/目录日”，不算第二个独立期次样本。

据此将精确来源路径 `央视网(新闻联播)::date` 登记为节目期次日期，单位 `YYYY-MM-DD`。原运行别名 `news_wscn_cctv` 名称包含 WSCN，但当前代码只调用央视网；WSCN 宏观日历由独立采集路径提供，故已将 lineage 中这个运行别名归到 CCTV 来源族，不再标记为混合来源。

## 边界

本裁决只补齐来源内日期语义，不把 ETF 或 CCTV 字段与其他来源的同名日期建立映射。深交所 `etf_sz.date` 继续待核，直到取得能解释 `metadata.subname` 的官方契约或等效直接证据。
