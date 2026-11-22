# 东方财富 IPO 风险警示字段复核与旧映射撤回

复核日期：2026-11-22。目标为精确来源身份 `东财-event_dc(IPO发行记录)::ipo_calendar[].IS_RISKWARNING`；旧碰撞表中的 `event_dc.IS_RISKWARNING` 是缺少数组上下文的展平别名，不能替代当前路径。

## 路径与官方依据

项目入口 `scripts/capture_context_collectors.py::collect_event_dc()` 调用 `stock_common/sc_datasource/_events.py::ipo_calendar()`；该函数把 `_EM_REPORTS['ipo_calendar']` 指向东方财富数据中心 `RPTA_APP_IPOAPPLY`，响应行透传到 `raw_event_dc.json::ipo_calendar[]`。字段身份据此固定为 `ipo_calendar[].IS_RISKWARNING`，没有建立与其他来源的映射。

深交所《股票上市规则（2026 年修订）》第 9.1.2 条将风险警示分为退市风险警示和其他风险警示，并规定简称分别冠以 `*ST`、`ST`。这是对“风险警示”这一官方业务概念及简称标识的权威说明；[东方财富新股数据页](https://data.eastmoney.com/xg/xg/?mkt=zh)是本项目所用 IPO 数据入口。该规则没有单独公开东方财富 JSON 键 `IS_RISKWARNING` 的 schema，因此本裁决同时核对同记录证券简称和响应中的 `MARKET` 行业板块标签，不把字段名本身当作唯一证据。

## 保留样本

- 按 [`capture_retention.py`](../../../scripts/capture_retention.py) 的 2026-10-15 保留边界筛选，并逐份核对采集目录名与 `meta.data_date`。有 `ipo_calendar[]` 数据的 20 份原始响应覆盖 2026-10-16 至 2026-11-19，共 400 行、21 个不同证券代码；2026-10-15 文件该数组为空，不计入样本。
- `IS_RISKWARNING` 为 `1` 的 23 行全部对应两个 `*ST` 代码：000010 *ST美丽 20 行、000016 *ST康佳A 3 行。其余 377 行为 `0`，没有简称以 `ST` 或 `*ST` 开头的反例。当前保留样本支持该键是来源行的风险警示标记；样本未包含纯 `ST`（其他风险警示）记录，因此不外推其对该子类的覆盖行为。
- 同一 `RPTA_APP_IPOAPPLY` 响应中的 `MARKET` 列 400/400 与标记一致：23 个 `1` 均为“深交所风险警示板”，377 个 `0` 均为“深交所主板”，无反例。这是同一响应内的交叉核对，不计作独立来源或第二份官方 schema。
- 同记录的 `CURRENT_ONEWORD_NUM` 在 23 个风险标记为 `1` 的行中分别为 `0`（000010）和 `8210`（000016）；与风险标记共 23/400 个直接不等。`PREDICT_ISSUE_PRICE1` 对 `CURRENT_ONEWORD_NUM` 也有 23/400 个直接不等：20 行为 `0.14` 对 `0`，3 行为 `0` 对 `8210`。其余 377 组共同零值不构成字段等价证据。
- 逐行值、同记录 `MARKET` 标签、采集目录、校验后的数据日、每个原始响应 SHA-256 及比较标志见[400 行审计 CSV](../research/20261122_eventdc_ipo_risk_flag_mapping_audit.csv)，规范 LF SHA-256：`a47f2203ca90cde13329391d234ab38383c2996fad90d7eb650177751cefbc3a`。此前[风险标记审计](../research/20261122_eventdc_risk_flag_audit.md)提供同批 400 行的旧候选反例。

## 结论与边界

将精确路径定案为东方财富 IPO 记录的**风险警示标记（0/1）**。观察到的 `1` 与深交所定义的 `*ST` 退市风险警示一致；纯 `ST` 样本未覆盖，保留此枚举覆盖限制。字段表示响应中的状态值，没有独立来源日期；本裁决不把 `UP_DATE` 或采集目录日期当作状态生效日，也不因此扩大行情日期覆盖。

从 `docs/field_verification/field_registry.json.mappings` 和 [`cross_source_align.md`](../../../verify/cross_source_align.md) 撤回下列两个基于旧展平路径的活动映射：

1. `event_dc.PREDICT_ISSUE_PRICE1 ↔ event_dc.CURRENT_ONEWORD_NUM`，关系 `same_number_same_meaning`，旧证据 `20260924 对撞 L1·hit=0.90·3d`。
2. `event_dc.CURRENT_ONEWORD_NUM ↔ event_dc.IS_RISKWARNING`，关系 `same_number_same_meaning`，旧证据 `20260924 对撞 L1·hit=0.90·3d`。

撤回只影响这两个旧展平身份，不改写已验证的完整路径 `ipo_calendar[].PREDICT_ISSUE_PRICE1`，不解释 `ipo_calendar[].CURRENT_ONEWORD_NUM`，不新建映射。历史报告原样保留。`IS_RISKWARNING` 的新定案不会给同记录其他字段自动赋予相同的业务有效日期。

## 官方参考

- [深交所《股票上市规则（2026 年修订）》第 9.1.2 条](https://docs.static.szse.cn/www/lawrules/rule/stock/W020260424747613955674.pdf)
- [东方财富新股数据页](https://data.eastmoney.com/xg/xg/?mkt=zh)
