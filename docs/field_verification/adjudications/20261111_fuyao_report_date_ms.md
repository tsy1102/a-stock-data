# Fuyao `report_date_ms` 是披露日

## 定案

对字段身份 `(同花顺-fuyao, report_date_ms)` 定案为财务报表的**披露日**。它记录报表公开披露的日期，不是财务数据所属的报告期末。时间戳单位为毫秒，按 `Asia/Shanghai` 解释。

同一响应中的 `period_end_ms` 才表示报告期末。两者是不同的日期字段，不能互相替代。

## 项目取数路径

`get_financial_report_with_fallback()` 在新浪财务报表不可用时，调用 `get_fuyao_financials("income", ..., period="quarterly")`。采集对象中的字段位于 `stocks.<code>.financials.income_q[].report_date_ms`；同一记录也有 `period_end_ms`。

项目保存的 [Fuyao API 契约](../../verify/fuyao_api_full.md) 将 `report_date_ms` 定义为披露日，将 `period_end_ms` 定义为报告期末，并指定报告期末时间戳为 `Asia/Shanghai` 零点。

## 样本与公告核对

`docs/field_verification/20261110/meta.json` 将 Fuyao 来源标为成功，数据日为 2026-11-10，覆盖 20/20 只股票。该目录的原始样本中：

| 股票 | `report_date_ms`（上海日期） | `period_end_ms`（上海日期） | 公告核对 |
|---|---:|---:|---|
| 600519 贵州茅台 | 2026-10-31 | 2026-09-30 | [2026 年第三季度报告](https://static.cninfo.com.cn/finalpage/2026-10-31/1225649896.PDF) |
| 601288 农业银行 | 2026-10-31 | 2026-09-30 | [2026 年第三季度报告](https://static.cninfo.com.cn/finalpage/2026-10-31/1225649460.PDF) |
| 920508 殷图网联 | 2026-10-30 | 2026-09-30 | [2026 年第三季度报告](https://static.cninfo.com.cn/finalpage/2026-10-30/1225649649.PDF) |

公告日期与 `report_date_ms` 对应；公告中的报告期末与 `period_end_ms` 对应。样本的两个日期清楚地区分了“何时披露”与“数据属于哪个报告期”。

## 代码影响

财务回退原先把 `report_date_ms` 填入统一结果的“报告日”，会将报告期末错标成披露日。估值报告随后按“报告日”排序、分季度，并计算历史区间，因此会把报告期往后错移。本次修正改为按 `period_end_ms` 生成“报告日”，按 `Asia/Shanghai` 转换；若没有报告期末时间戳则留空，不再拿披露日伪装报告期末。披露日字段的定案本身不代表与其他来源建立映射。
