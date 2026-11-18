# ELTDX `ladder_level` 字段定案

## 结论

- `TDX-eltdx(适配层)::limit_ladder.ladder_level`：定案为**当前连续封住涨停的板数**，单位“板”；只有 `limit_status=sealed` 时有值。
- `TDX-eltdx(适配层)::shortline.ladder_level`：原登记“连板梯队等级”、单位“-”不准确，已按同一上游字段契约修正为上述计数语义。
- `limit_ladder.ladder_level` 与 `shortline.ladder_level` 是同一个 `ShortlineIndicator` 字段在两个 Helper 输出路径中的值。同日原始样本 14/14 相等；这属于同源路径核验，不计作独立来源证据。
- 已验证的 KPL `raw_columns.col_15` 在 13 个同日可配对样本中 13/13 相等，支持相同业务语义。`docs/verify/cross_source_align.md` 早已将 `push2ex.limit_count` 映射到完整路径 `eltdx.limit_ladder.ladder_level`；但 registry 投影错误地把目标压成 `eltdx::ladder_level`。本轮将 registry 映射校正为对齐表已有的完整路径，没有新建映射。最新样本对该历史关系提供 12/13 个可配对值相等的复核；唯一差异对应 ELTDX 上游误报封板，另有一个 ELTDX 行未出现在东财池，均作为数据质量/缺行限制保留。

## 上游定义与实现

项目固定依赖为 `eltdx==3.3.2`。上游[短线指标字段表](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/helpers/%E7%9F%AD%E7%BA%BF%E6%8C%87%E6%A0%87.md)将 `ladder_level` 定义为当前连续封住涨停的板数，单位为“板”，并限定仅封板时返回；[连板天梯文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/helpers/%E8%BF%9E%E6%9D%BF%E5%A4%A9%E6%A2%AF.md)说明 `limit_ladder()` 返回 `ShortlineIndicator` 行。固定版本源码的 `_ladder_level()` 先要求 `limit_status == "sealed"`，再依据统计文件日期、当前目标交易日和前一交易日调整连板数。

采集器将 `limit_ladder` 行写入 `stocks.<code>.limit_ladder`；短线指标写入 `stocks.<code>.shortline`。因此注册为两个不同的完整来源路径，不把叶字段名当成路径身份。

## 样本与日期核验

逐行证据见 [`research/20261119_eltdx_limit_ladder_level_samples.csv`](../research/20261119_eltdx_limit_ladder_level_samples.csv)。样本全部在 `MIN_CAPTURE_DATE=2026-10-15` 之后：14 条、6 只股票、11 个目标交易日（2026-10-16 至 2026-11-17）。所有 ELTDX `target_trade_date` 与采集目录 `meta.data_date` 相同；`stats_date` 只落在目标交易日或 Helper 标出的上一实际交易日，满足来源对齐规则。目录 `run_date` 与目标数据日不同的样本仍按目标交易日判定，没有把自然日差异误作过期。

KPL 原始响应显式提供 `trade_date`。13 个两源共同出现的股票日与目标交易日相同，`eltdx.limit_ladder.ladder_level` 和已验证的 `kpl.raw_columns.col_15` 均为 13/13 精确相等；1 个 ELTDX 行未出现在 KPL 当日涨停明细，不算相等或反例。两条 helper 输出路径 14/14 精确相等，但它们来自同一个 ELTDX 模型，不能重复计作独立证据。

## 单独的数据质量异常

2026-10-16，000678 的 ELTDX 行给出 `limit_status=sealed`、`ladder_level=1`。同条原始行情快照为：前收 9.94 元、最新价 10.93 元、买一 10.92 元/1092 手、卖一 10.93 元。东财同数据日把 000678 放在 `limit_broken_pool`，`limit_count=0`、`broken_count=2`；KPL 当日涨停明细也没有该代码。此记录不符合“当前封住涨停”的定义，不能用于跨源同义的正证据。

核对固定版本源码后找到原因：`_limit_status()` 在最新价达到涨停价时，接受“买一价达到涨停价 **或** 买一金额大于零”作为封板条件；`_locked_amount()` 对任何正买一价和正数量都会返回正金额。因此买一低于涨停价时仍可能被误标 `sealed`，随后 `_ladder_level()` 会返回至少 1。此问题在 ELTDX v3.3.2 上游 Helper 实现中，不是本项目采集器改写原始值造成的。本轮保留原始证据、不回写样本；把字段语义定案与这条输出质量问题分开处理。

另外，碰撞报告中的候选 `push2ex.limit_count` 有一条不一致及一条缺失：13 个可配对行中 12 个相等，000678 的上述误判对应东财 `limit_count=0`；另有一个 ELTDX 行未出现在东财已归档的池中。东财池文件没有逐行 `as_of_date`，故这些样本只用于定位 ELTDX 上游质量问题，不作为新的独立映射裁决。对齐表已登记的历史映射仍保留，但 registry 现已按对齐表和完整路径解析结果改正为 `eltdx.limit_ladder.ladder_level`。

## 定案文件

结构化决定见 [`20261119_eltdx_limit_ladder_level_source_contract.json`](20261119_eltdx_limit_ladder_level_source_contract.json)。它修正已有 `shortline.ladder_level` 的单位/释义，新增并确认 `limit_ladder.ladder_level` 完整路径，并记录两路径同源别名证据；跨源映射只校正 registry 中与既有对齐表不一致的路径，不新增映射关系。
