# KPL `raw_columns.col_20` 来源内实证定案

复核日期：2026-11-16。字段身份为 `开盘啦(kpl_limit_up_detail)::raw_columns.col_20`。本结论只确认 KPL 该精确来源路径的字段含义，不认定它与开盘红/KPH 的行业涨停数等价，也不代表官方接口发布了该列定义。

## 路径与样本资格

- `stock_common/sc_kpl.py::get_kpl_limit_up_detail()` 请求 `DailyLimitPerformance`；`capture_raw=True` 时把上游响应中除代码、名称之外的原始位置保存为 `raw_columns.col_{index}`，因此 `col_20` 精确对应代码中的 `row[20]`。
- `scripts/capture_verified_collectors.py::collect_kpl_detail()` 请求 `PidType=1..5`，合并各梯队记录并按股票代码归档。对每个目录，脚本复核了原始 `trade_date` 与 `meta.source_as_of_dates.kpl` 一致；有效记录的原始行数、归档股票数和 PidType 分项计数相互对账，未发现重复行。
- 样本保留起点为 2026-10-15。2026-10-15 的 30 行旧格式归档没有 `raw_columns.col_20`，按字段路径缺失排除，不作为反例。其余 17 个有效来源交易日为 2026-10-16、10-19、10-20、10-21、10-23、10-26、10-28、10-29、10-30、11-02、11-03、11-04、11-05、11-06、11-09、11-10、11-12。
- 逐行证据 CSV：[`20261116_kpl_col20_sector_count_samples.csv`](../research/20261116_kpl_col20_sector_count_samples.csv)，规范文本 SHA-256：`003580544c431aef71110908ce9531b61d234ec923314c57e98cde2e5b6031f8`。

## 观测结果与裁决

| 核查项 | 结果 |
|---|---:|
| 有效来源交易日 | 17 |
| `col_20` 逐股票记录比较 | 1,096 |
| 与同日相同 `col_19` 分类码的 KPL 唯一返回行数完全一致 | 1,096/1,096 |
| 反例 | 0 |
| 不同股票代码 | 695 |
| 数据日 × `col_19` 分类码分组 | 344 |
| `col_20` 整数范围 | 1–40 |
| 因旧归档缺少该路径而排除 | 30 行（2026-10-15）|

**定案含义：**`col_20` 是同一来源交易日内，按 `raw_columns.col_19` 分类代码分组后，该代码对应的 KPL `DailyLimitPerformance` 涨停梯队返回记录数；记录来自采集器合并的 `PidType=1..5` 响应。单位为“家”。此定义仅覆盖该接口返回集合；不确认 `col_19` 的具体分类体系或层级，不将该数解释为其他来源、其他接口或更广市场范围的行业总数。

对照 KPH `industry_limit_up_count` 的 11 个来源日期、500 个共同股票日样本中，450 组相同、50 组不同，且差异集中在 2026-10-16 与 2026-11-02。故不建立 KPL↔KPH 映射；开盘红 `industry_limit_up_count` 也保持原有未验证状态。总体相同率不能抹掉逐日反例。

开盘啦官网页面没有公开 `DailyLimitPerformance` 原始列位置或 `col_20` 定义；官网访问结果记录在 [`20261116_kpl_col20_public_web.md`](public_web/20261116_kpl_col20_public_web.md)。因此本次是来源内样本结构与计数关系的实证定案，不是官方契约定案。未修改采集逻辑，也未新增跨源映射。
