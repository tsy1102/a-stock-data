# 东方财富 IPO AVERAGE_PRICE 来源内释义与旧映射撤回

复核日期：2026-11-21

## 裁决

将 `东财-event_dc(IPO发行记录)::ipo_calendar[].AVERAGE_PRICE` 登记为 IPO 涨幅计算所用的基准成交均价，单位为元/股。东方财富 `TOTAL_CHANGE` 按发行规则选择成交均价对应的交易日；当前留存样本不能证明该日始终是上市日或开板日，因此释义不固定到某一交易日。

本裁决不将该字段与 `LD_AVERAGE_PRICE`（上市首日成交均价）或 `OPEN_AVERAGE_PRICE`（开板日成交均价）建立同义映射。撤回以下三个 2026-09-24 旧映射：

| 原关系 | 旧证据 | 撤回原因 |
|---|---|---|
| `event_dc.OPEN_AVERAGE_PRICE` ↔ `event_dc.AVERAGE_PRICE` | `L1·hit=1.00·3d` | 三个数值相等的日期不足以证明“开板日均价”和涨幅计算基准均价为同一语义；现有 20 条样本的开板日均价虽相同，但 `OPEN_DATE` 均与 `LISTING_DATE` 重合。 |
| `event_dc.OPEN_AVERAGE_PRICE` ↔ `event_dc.LD_AVERAGE_PRICE` | `L1·hit=1.00·3d` | 官方字段分别标为开板日均价、上市首日成交均价；当前样本日期重合导致数值相等，不能证明事件语义相同。 |
| `event_dc.AVERAGE_PRICE` ↔ `event_dc.LD_AVERAGE_PRICE` | `L1·hit=1.00·3d` | `AVERAGE_PRICE` 是 `TOTAL_CHANGE` 计算所用的基准均价；官方规则依发行制度选择参考日。`LD_AVERAGE_PRICE` 则固定指上市首日，当前样本的数值相同不足以证明普遍等价。 |

撤回表示这些活动映射缺乏当前规则要求的语义证据，不表示三个字段在每条记录中都必然数值不同，也不改写原始样本或停止采集。

## 精确采集路径

项目 [`_events.py`](../../../stock_common/sc_datasource/_events.py) 将 `ipo_calendar` 路由到东方财富 `RPTA_APP_IPOAPPLY`。[`_eastmoney.py`](../../../stock_common/sc_datasource/_eastmoney.py) 将请求交给 [`_datacenter.py`](../../../stock_common/sc_datasource/_datacenter.py)；后者返回官方响应 `result.data[*]` 中的原始行对象。`ipo_calendar()` 仅附加 `source`、`source_url`、`fetched_at`，故响应键 `AVERAGE_PRICE` 直通至 `raw_event_dc.ipo_calendar[].AVERAGE_PRICE`。

## 官方定义与留存样本

东方财富[新股申购页面](https://data.eastmoney.com/xg/xg/?mkt=zh)将 `TOTAL_CHANGE` 显示为 IPO“涨幅”，并说明注册制与审批制按各自规则选择成交均价参考日；详情页和前端字段模板也将 `LD_AVERAGE_PRICE` 标为“首日成交均价”、`OPEN_AVERAGE_PRICE` 标为“开板日均价”。相关页面与原始路径核验见[首日表现字段裁决](20261120_eventdc_ipo_first_day_contracts.md)及[IPO 涨幅公式裁决](20261120_eventdc_ipo_semantics.md)。

按留存原始响应 `docs/field_verification/20261119/raw_event_dc.json` 与逐股审计表 `research/20261120_eventdc_ipo_semantics_samples.csv` 复核：

- 20 条记录覆盖 20 只股票，申购事件日期为 1988-12-28 至 1993-11-22；这是一次接口响应中的 20 条历史发行记录，不是 20 个独立采集日。
- `AVERAGE_PRICE`、`ISSUE_PRICE`、`TOTAL_CHANGE` 均为 20/20 非空；按 `(AVERAGE_PRICE / ISSUE_PRICE - 1) × 100` 复算 `TOTAL_CHANGE`，20/20 均在 0.02 个百分点内，最大绝对误差为 `0.004285714286` 个百分点。
- `AVERAGE_PRICE` 与 `LD_AVERAGE_PRICE` 在这 20 条记录中 20/20 数值相同；同时 `OPEN_DATE` 与 `LISTING_DATE` 20/20 相同。因此，该批样本不能区分基准均价日、上市首日和开板日三种解释。官方规则与公式支持“涨幅计算基准成交均价”这一受限释义，但不支持将三条路径合并。
- 本批样本只覆盖早期深市 IPO。对其他发行制度、市场和基准交易日的具体选择，按官方规则保留其适用范围，不从本批样本外推。

原始归档规范 LF SHA-256：`ba857795a52dfe5802e2f5eea2e04d8bd792247dffbbd1b0c6c9082ff82ac957`。此前字节摘要与该值不同；通过 `scripts/evidence_hash.py` 计算的规范 LF 摘要与本记录完全一致，确认为行尾规范化差异，原始证据无需恢复或改写。样本 CSV 规范 LF SHA-256：`2d80d9c9557da72c7fe0cce3bffa505b21ceae223cafde5620b5001df41970ac`。

## 主字典边界

本裁决只更新精确来源路径的来源内释义，并从 `docs/verify/cross_source_align.md` 和 registry 移除上表三条旧活动映射。没有创建跨来源映射；其他 IPO 字段关系、采集路由、来源日期与价格刷新时点均不由本裁决推断。
