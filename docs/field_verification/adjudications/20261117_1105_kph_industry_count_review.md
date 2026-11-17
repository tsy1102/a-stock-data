# KPH 行业涨停数与 KPL `col_20` 候选复核

复核时间：2026-11-17 11:31 Asia/Shanghai。采集任务实际开始于 11:05，市场阶段为 `morning_session`，并非盘前；按最近已完成交易日规则，目标数据日仍是 2026-11-16。

## 最新完整碰撞证据

- 报告：[`preopen_20261117_1105/20261117_collision_report.json`](../20261117/preopen_20261117_1105/20261117_collision_report.json)，SHA-256：`9399bc82b19ffb96eac3cdec9d18795b3a7fc31072bf1b8fc68da046ecf7edcc`；完整性为 `complete`。
- 候选 ID：`cc1_8f9d96e4cee780a405d64109c74e908f91518d29784845466d97847325f72f48`。
- 11 月 16 日 KPH 来源日与 KPL 来源日均为 2026-11-16；KPH `pagination.complete=true`、31 条，KPL 32 条。共有 31 只股票，`industry_limit_up_count` 与 KPL `raw_columns.col_20` 为 31/31 相等；KPH `industry_id` 与 KPL `col_19` 有 30/31 相同。
- 这只是 1 个完整独立来源日，因此当前关系只列为 L4。报告 `research_history` 显示该候选关系自 2026-10-18 持续出现；历史研究记录称 11 个旧来源日的 500 组中有 50 组不等，集中在 2026-10-16 与 2026-11-02。旧 KPH 页缺少完整分页证明，不能当作正式反例或正式匹配；但也不能把剩余单日吻合外推为稳定等价。
- 11:05 的补采只尝试 6 个不完整/缺失的东财源，因本地 `ip_banned` 熔断均为 `attempts=0`。它没有刷新 KPH 或 KPL；本次对撞使用的是 01:12 KPH 与 11 月 16 日晚间 KPL 的留存样本。

## 裁决

当前 L4 关系标记为 `needs_external_evidence`，不建立 KPH↔KPL `mappings`，不改变字段注册表。KPL `col_20` 的已验证释义仅指 KPL 当日按 `col_19` 分组的接口返回记录数，不扩展为 KPH 口径。KPH 客户端将索引 27 命名为“同行业涨停数”，但开盘红官网未公布该 API 的字段契约或统计范围；客户端说明不能替代上游定义。

保留的后续问题是：KPH 指标的行业范围、未出现在 KPH 返回列表中的行业涨停股票如何计入、以及历史日期差异是否由分页截断或两端口径造成。需要官方契约或新的完整分页来源日才能判断来源关系；不得通过重复跑同一来源日增加独立样本数。

相关历史记录：[`KPH 新数据复核`](20261117_kph_industry_count_followup.md)、[`KPH 分页审计`](20261117_kph_pagination_audit.md)、[`KPL col_20 来源内定案`](20261116_kpl_col20_category_limit_up_count.md)。公开产品页：[开盘红官网](https://www.kaipanhong.com/)。
