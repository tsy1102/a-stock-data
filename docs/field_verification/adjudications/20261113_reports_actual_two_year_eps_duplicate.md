# `reports::actualLastTwoYearEps` 当前响应重复输出裁定

- **核验日期：** 2026-11-13（Asia/Shanghai）
- **精确身份：** `(reports, actualLastTwoYearEps)`
- **裁定范围：** 证伪“前年实际 EPS”这一旧候选释义；确认保留期非空样本中的响应行为与 `actualLastYearEps` 重复。本文不推断东方财富服务端的原始设计意图。

## 裁定

- 自 2026-10-15 保留起点以来，全部 8 个非空 `infoCode`、覆盖 4 只股票的复核记录中，`actualLastTwoYearEps` 均与同条 `actualLastYearEps` 完全相等，差异为 0/8。逐条证据在 [2026-11-12 样本表](20261112_reports_actual_eps_live_samples.csv)，SHA-256：`D33484462714E315429A56967D4F310EE93B6CFF40691018E973510B85C7B3E3`。
- 2026-11-13 通过东方财富官方 `report/list` 端点复核泸州老窖 2025-09-02 的 4 条研报记录：唯一一条非空记录 `AP202509021738064069` 的两字段仍都为 `9.15345681398375`；另外 3 条两字段均为空。逐条记录见[当日接口复核表](20261113_reports_actual_two_year_eps_api_recheck.csv)。空值不作为期间反例。
- 同一 `infoCode` 的发布日期为 2025-09-02，因此上一完整会计年度为 2024、此前年度为 2023。泸州老窖官方 2024 年年报列出 2024/2023 归母净利润分别为 13,472,986,476.01 / 13,246,394,700.59 元，基本 EPS 分别为 9.18 / 9.02 元/股。按上一轮已核的现行总股本 1,471,901,463 股，将同一分母分别用于两个年度以隔离年度差异，得到 2024 年 `9.15345681398375`、2023 年 `8.999511878730974` 元/股。API 两字段相等值精确复现 2024 年结果，不是独立的 2023 年结果。计算明细见[年度对照表](20261113_reports_actual_two_year_eps_annual_comparison.csv)。
- 官方年报本身同时显示两年度的法定基本 EPS 不同；由于东方财富 `actualLastYearEps` 已证实使用的并非法定加权平均股数口径，本裁定另以同一分母复算作期间区分，不把法定 EPS 与接口值的口径差异当成反例。

因此，旧的“前年实际 EPS”候选释义不能用于当前字段。注册表将该精确路径标为 `disproved` / `empirical_duplicate_alias`，规范指向同条 `actualLastYearEps`，含义限定为“当前保留样本中与上年实际 EPS 响应重复，不能作为独立的前两年 EPS 字段”。这是对当前响应行为的经验裁定；东方财富没有公开该键的正式定义，本结论不推断重复的成因、不宣称服务端有意设计成别名，也不保证未来响应不变。该路径不建立跨来源映射。

## 来源与日期边界

- 项目 `get_reports()` 将东方财富 `https://reportapi.eastmoney.com/report/list` 的原始记录保留为 `reports`；路径就是响应键 `actualLastTwoYearEps`。本次直接网页查询参数为 `code=000568`、`qType=0`、`beginTime=endTime=2025-09-02`，完整 URL：<https://reportapi.eastmoney.com/report/list?pageSize=50&industry=%2A&rating=%2A&beginTime=2025-09-02&endTime=2025-09-02&pageNo=1&code=000568&qType=0>。
- 本次查询自然日为 2026-11-13；`publishDate=2025-09-02` 是研报发布日期；财报对照的业务期间为 2024 与 2023 财年。不得把查询日或研报发布日期当作 EPS 值的历史快照日期。
- [泸州老窖 2024 年年度报告（巨潮资讯）](https://static.cninfo.com.cn/finalpage/2025-04-28/1223350383.pdf)，第二节“主要会计数据和财务指标”，列有 2024/2023 年度净利润及基本 EPS。报告解析页未显示东方财富的 `actualLastTwoYearEps` 字段标签；因此没有把报告正文页面当作该 API 键的正式定义。
- 与上一年度接口释义有关的股本和公式证据见 [`20261112_reports_actual_last_year_eps_evidence.md`](20261112_reports_actual_last_year_eps_evidence.md) 与 [`20261112_reports_actual_last_year_eps_samples.csv`](20261112_reports_actual_last_year_eps_samples.csv)。

## 保留的未决边界

1. 东方财富对 `actualLastTwoYearEps` 的正式语义、计算公式、回溯时点和重复输出原因仍未公开，未在字典中另造定义。
2. 经验别名裁定只覆盖保留期内全部已观测的非空响应；后续若出现该字段与 `actualLastYearEps` 不同的非空值，应按明确财年和发行人报告重新核验并重开该身份。
3. `actualLastYearEps` 的统一分母算法与历史回填规则仍按其既有证据单独保留，不由本裁定扩展。
