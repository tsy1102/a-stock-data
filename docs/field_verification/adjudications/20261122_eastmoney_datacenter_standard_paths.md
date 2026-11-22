# DataCenter 当前路径与旧别名批量核验

复核日期：2026-11-22。范围是 `东财-datacenter(英文键)` 中 44 个未限定短路径，以及当前两融、大宗交易、股东户数、解禁和分红适配器的实际输出。只核对保留期内的项目采集样本（`MIN_CAPTURE_DATE=2026-10-15`）、当前代码和官方页面定义；不回填边界前的归档数据。

## 裁决摘要

- 将 8 个两融基础输出、7 个大宗交易输出、3 个 Eastmoney 股东户数 helper 输出和 4 个 TDX 分红输出登记为完整路径。完整定义、接口到输出的映射及限制见结构化决定。
- `margin_trading`、`northbound_hold`、`lockup_expiry` 是 `raw_datacenter.json` 中的采集对象容器，不是字段。
- `lockup_expiry.*` 是统一适配器输出。`get_lockup_expiry()` 优先走 TDX F10，缺少有效记录时才回退 Eastmoney `RPT_LIFT_STAGE`；采集容器没有逐事件来源标记或来源实际数据日。现有一条保留期样本只证明序列化结构与回退分支，不作业务语义或日期碰撞证据。`free_shares`、`shares_is_actual` 是项目归一化/派生值。
- 旧 Eastmoney 分红表 `RPT_SHAREBONUS_DET` 不是当前 `get_dividend_history()` 的路由；当前实现只调用 TDX XDXR。保留旧接口原始字段记录，不把它们映射到 TDX 字段。
- TDX 兼容输出键 `bonus_ratio` 实际承载 `peigu`（配股数量），不是送股数量。登记含义为“每股配股数/配股比例”，保留旧代码键名以维持现有返回结构；`transfer_ratio` 来自 `songzhuangu`，含义按上游命名记作“每股送转股数”，不缩窄成单独转增。
- 原有未限定短名中，多义 `date`、`change_ratio` 只作为旧扁平别名退役；它们分别拆到各自完整路径，不形成一个统一字段或跨源映射。

## 可复核的来源定义与映射

### 两融基础路径

`get_margin_trading()` 在 TDX F10 无有效明细时，向东方财富 `RPTA_WEB_RZRQ_GGMX` 请求报告行，并将 `DATE`、`RZYE`、`RZMRE`、`RZCHE`、`RQYE`、`RQMCL`、`RQCHL`、`RZRQYE` 写入 `margin_trading.*`。本轮保留期逐行公式材料中，扩展键 `RZJME` 等与基础键同时出现；该扩展输出是此批 Eastmoney 分支的路由标记。样本来源日取原始 `DATE`，不是采集目录名。

东方财富[融资融券交易明细](https://data.eastmoney.com/rzrq/detail/SH.html)把相关列分别展示为融资余额、融券余额、融资买入额、融资偿还额、融资净买额、融券余量、融券卖出量、融券偿还量及融资融券余额。接口响应到运行路径的精确映射由项目代码确定；官方页面只用于核实业务标签。

### 大宗交易路径

`get_block_trade()` 请求 `RPT_DATA_BLOCKTRADE`，逐字段映射 `TRADE_DATE`、`DEAL_PRICE`、`CLOSE_PRICE`、`DEAL_VOLUME`、`DEAL_AMT`、`BUYER_NAME`、`SELLER_NAME`。当前官方[大宗交易页面](https://data.eastmoney.com/dzjy/)列有交易日期、收盘价、成交价、成交量、成交额、买方营业部及卖方营业部；页面展示成交量为万股、成交额为万元，而项目接口输出不缩放，单位分别按股、元记。

一次经项目 DataCenter 适配器的低频核查返回 920885 星辰科技 2026-11-20 记录：成交价 7.80 元、收盘价 10.39 元、成交量 100,000 股、成交额 780,000 元，买卖营业部均为招商证券股份有限公司桂林中山北路证券营业部。`7.80 × 100,000 = 780,000`；项目计算的折溢率为 `round((7.80 / 10.39 - 1) × 100, 2) = -24.93%`。该行用于确认接口映射和单位换算，不是采集归档或跨源字段映射。`premium_pct` 是项目计算值，不是上游键。

### 股东户数路径

当前 Eastmoney helper `_holder_fetch_em()` 调用 `RPT_F10_EH_HOLDERNUM`，将 `END_DATE`、`HOLDER_TOTAL_NUM`、`AVG_FREE_SHARES` 映射到 `holder_fetch_em.date`、`holder_fetch_em.holder_num`、`holder_fetch_em.avg_shares`。日期是股东户数统计截止日；股东数单位为户；户均字段是可流通股均值，单位为股。东方财富[股东户数页面](https://data.eastmoney.com/gdhs)展示股东户数、统计截止日和户均持股数量。

统一函数 `holder_change()` 可以优先使用 TDX F10，并在回退时使用该 helper；`_compute_holder_changes()` 按相邻报告期股东户数派生变化户数和变化率。故这些派生值不登记成 Eastmoney 上游字段，也不把旧 `RPT_HOLDERNUMLATEST` 字段表当作当前 helper 契约。在线返回的早期报告期只用于核对页面/字段路线，没有并入保留期碰撞样本。

当前原始响应键 `HOLDER_TOTAL_NUM` 已单独登记为 `(东财-datacenter(英文键), HOLDER_TOTAL_NUM)`；`holder_fetch_em.holder_num` 是同一路由经项目 helper 归一后的输出。历史 `RPT_HOLDERNUMLATEST` 的 `HOLDER_NUM`、`HOLDER_NUM_CHANGE`、`HOLDER_NUM_RATIO` 仍保留旧定义及证据，但其扁平身份不对应当前接口响应路径，现归档为 `retired_legacy_path`。不将这些历史路径与 `HOLDER_TOTAL_NUM` 或项目派生变化值声明为字段映射。

### TDX 分红路径

当前 `get_dividend_history()` 只转调 `tdx_get_dividend_history()`，筛选 XDXR 类别 1，并输出 `dividend_history.date`、`bonus_rmb`、`bonus_ratio`、`transfer_ratio`。固定 ELTDX v3.3.2 的 [`CapitalChangeRecord` 字段契约](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md)和项目适配器映射为：`fenhong → bonus_rmb`（元/股）、`peigu → bonus_ratio`（配股股数/股）、`songzhuangu → transfer_ratio`（送转股数/股）。项目的每 10 股值已在适配器中归一为每股值，细节见[2026-11-10 TDX 单位裁决](20261110_tdx_xdxr_source_contract.md)。XDXR `date` 是权息/股本变迁事件日期；目前证据没有进一步限定为公告日、登记日或除权除息日，见[2026-11-15 日期裁决](../research/20261115_tdx_xdxr_date_semantics.md)。

旧 Eastmoney `RPT_SHAREBONUS_DET` 与当前 TDX XDXR 是不同路径；没有建立字段等价关系。历史 Eastmoney 原始键仍保留其原注册身份。

## 保留期路径结构审计

读取 `MIN_CAPTURE_DATE` 之后的 21 个 `raw_datacenter.json`，逐股票检查三类完整对象路径及其后代。两融和北向路径已有精确子路径；解禁对象仅找到 1 条事件记录，且容器不带逐行 `as_of_date`。解禁路径的结构结果和样本边界沿用[2026-11-19 解禁来源审计](20261119_datacenter_lockup_derived_outputs.md)及其逐样本 CSV。不会因数据在某目录出现就将目录日期当作来源日期。

本次新增的完整字段定义见[结构化决定](20261122_eastmoney_datacenter_standard_paths.json)；短名、容器、派生字段和旧路径的逐项归类见[路径范围审计 CSV](../research/20261122_eastmoney_datacenter_path_scope_audit.csv)，两融及大宗交易样本见[接口映射样本 CSV](../research/20261122_eastmoney_datacenter_standard_path_samples.csv)。

## 范围限制

- 不建立跨源 `mappings`，不因同值或相同字段名认定来源等价。
- 不声称 Eastmoney DataCenter 公开了未公开的逐键 Schema；字段定义以官方页面标签、项目实际请求/映射和保留期或即时接口响应的组合证据为限。
- 未登记为当前抓取路径的旧 Eastmoney 分红/股东别名，不会重新进入每日碰撞目标。
