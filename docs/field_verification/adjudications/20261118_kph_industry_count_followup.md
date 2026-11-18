# KPH `industry_limit_up_count` 2026-11-17 数据复核

复核日期：2026-11-18。目标与 KPH 实际数据日：2026-11-17。字段路径：`开盘红::industry_limit_up_count`；跨源对照：`开盘啦(kpl_limit_up_detail)::raw_columns.col_20`。

## 采集与日期

- 北京时间 11:57 执行默认字段采集时，运行卡仍将目标数据日设为 2026-11-17；该目录已有完整盘后采集，默认流程幂等跳过，没有重请求其他来源。
- 随后备份原始 KPH raw 与 `meta.json`，执行 `capture_field_probe.py --date 20261117 --only kph`。KPH 于 12:02:17 成功返回；`as_of_date=2026-11-17`、市场阶段为 `closed`，分页 `1` 页、`34/34` 行、`complete=true`。这是按明确历史交易日请求的收盘数据，不是 11 月 18 日盘中行情。
- KPL 归档数据日同为 2026-11-17：37 行、无重复；来源采集于 2026-11-17 15:38。两源日期可直接对齐。

## 上游字段映射证据

项目适配器从 KPH 响应 row[26] 读取 `industry_id`，从 row[27] 读取 `industry_limit_up_count`。Levistock 0.1.8 在固定提交 `808d8187a6dd2a781dc51efeb1581f35d68e66c7` 中调用相同的 `apphis.kaipanhong.com` 历史接口及 `HisDaBanList / HisHomeDingPan / PidType=4 / Type=6` 参数，并将 row[26] 映射为 `industry_id`、row[27] 映射为 `industry_zt`，注释为“同行业涨停数”。这强力支持字段名和项目路径的对应关系；该仓库是第三方客户端，不是开盘红提供方的正式接口契约，因此不单独证明计数的完整统计范围。

## 2026-11-17 逐股对照

完整逐股证据见 [CSV 样本](../research/20261118_kph_industry_limit_up_count_samples.csv)：

- KPH 34 条记录全部能在同日 KPL 列表中找到；两源 `industry_id` / `col_19` 有 31/34 相同。
- KPH 计数与 KPL `col_20` 有 14/34 精确相同，不能建立两字段的逐值等价映射。
- KPH 计数与本次 KPH 返回列表按 `industry_id` 分组的行数有 29/34 相同。两个不相同的行业组为：`801346` 返回 1 行、字段值 2；`801807` 返回 4 行、字段值 5。
- KPL `col_20` 与本次 KPL 返回的 37 行按 `col_19` 分组的行数为 37/37 相同。这与已有 KPL 来源内定案一致，但不能用 KPL 的统计逻辑替代 KPH 口径。

返回列表内的 5 条差异没有证明 KPH 释义错误：字段可能使用比当前历史接口返回集合更宽的计数池；但现有证据无法判明是否如此，也未取得提供方说明。不得把 `industry_limit_up_count` 精确定义成“KPH 当前返回行数按行业分组”，也不得把 KPH 与 KPL 视为可互换来源。

## 结论与后续判别条件

Levistock 的精确接口/索引映射与本次样本共同支持候选释义“同行业涨停数”。目前仍无开盘红提供方的正式字段契约或可独立核对计数总体的官方页面；同日 KPH/KPL 的逐股计数亦有 20/34 不同。因此本字段继续保持 `unverified`，注册表和主字典不变，不创建 `mappings`。这不是等待更多随机样本：只有取得 KPH 提供方对该字段及计数集合的明确定义，或能在同一数据日独立核对所有可比行业计数的数据，才足以确认统计范围。

## 证据指纹

- KPH raw：[`20261117/raw_kph.json`](../20261117/raw_kph.json)，SHA-256 `23dd7a6e8c33aabb279bbabdef929cb051861167c04a517c2720bcd3fc76f1ca`。
- KPL raw：[`20261117/raw_kpl.json`](../20261117/raw_kpl.json)，SHA-256 `a3392ff2f352d345c97a0ad057fedcb0f5b47d59383cd41b5c467020f7d4ea8c`。
- 来源元数据：[`20261117/meta.json`](../20261117/meta.json)，SHA-256 `98c2c63822b6cd86c701d810eb952b631db24473af82d91cf6f7b121a4c4f25e`。
- Levistock 字段映射：[固定版本源码](https://github.com/fleetinglife/levistock/blob/808d8187a6dd2a781dc51efeb1581f35d68e66c7/levistock/stock/stock_daban_his_kph.py)；字段目录：[固定版本 README](https://github.com/fleetinglife/levistock/blob/808d8187a6dd2a781dc51efeb1581f35d68e66c7/README.md)。
- 前次 KPH/KPL 审查：[`20261117_kph_industry_count_followup.md`](20261117_kph_industry_count_followup.md) 与 [`20261117_kph_pagination_audit.md`](20261117_kph_pagination_audit.md)。
