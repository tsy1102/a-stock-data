# Fuyao 财务指标分组容器与请求期标签核查

裁决日期：2026-11-15
范围：`同花顺-fuyao::growth`、`::profitability`、`::solvency`、`::operation`、`::fin_report`

## 结论

- 将 `growth`、`profitability`、`solvency`、`operation` 四个根路径标为 `disproved` / `collector_output_container`。它们是财务指标的分组容器，不是独立标量字段，不再进入默认破解目标；`unknown_fields.md` 仍在“已证伪”分组保留路径及处置记录供审计。该处置不更改任何分组内指标的语义或状态。
- 将 `fin_report` 标为 `disproved` / `project_derived_capture_output`。它记录项目实际选用的财务指标请求期标签，不是 Fuyao 指标响应中的独立原始字段，也不能单独证明指标实际所属报告期；它同样只保留在审计分组，不进入默认破解目标。
- 官方接口的第五个分组 `cash-flow` 没有单独的注册表根路径身份，本次不新增注册项。已有 `cash-flow.<index_id>` 叶路径不变。
- 不改采集行为、请求顺序、来源路由或跨源映射。

## 来源契约与项目代码

Fuyao 财务指标接口响应为 `data.abilities[]`，每项由 `ability` 分组名和 `indicators[]` 构成，指标项再以 `index_id`、`value` 表示。官方契约列出 `growth`、`profitability`、`solvency`、`operation`、`cash-flow` 五个能力分组，并将 `data.report` 说明为请求参数回显。

项目适配器 [`sc_fuyao.py`](../../../stock_common/sc_fuyao.py) 的 `get_fuyao_fin_indicators()` 遍历能力项，将值整理为 `{ability: {index_id: value}}`；因此四个已登记根路径承载的是子指标字典。采集器 [`capture_verified_collectors.py`](../../../scripts/capture_verified_collectors.py) 依次尝试当年 `-2`、`-1` 请求，遇到非空指标结果后将实际选中的请求标签写入 `fin_report`。适配器没有把响应的 `data.report` 当作字段返回。

官方冻结契约见 [`fuyao_api_full.md`](../../verify/fuyao_api_full.md) 的财务指标响应章节。另于 2026-11-15 20:16:53（Asia/Shanghai）核对了在线官方文档：[REST 财务指标接口](https://fuyao.aicubes.cn/docs/api-reference/financial-indicators/) 与 [MCP 财务指标工具](https://fuyao.aicubes.cn/docs/mcp/tools/get_a_share_financials_indicators/)。没有调用采集接口。

## 留存样本结构与日期核验

逐目录清单见 [`20261115_fuyao_fin_indicator_container_audit.csv`](../research/20261115_fuyao_fin_indicator_container_audit.csv)：

- 覆盖保留边界 `2026-10-15` 之后的 18 个 Fuyao 归档目录、360 条股票记录；每行包含 raw 与 meta 文件的 SHA-256。
- 18/18 行中目录日期与 `meta.data_date` 一致，`meta.source_as_of_dates.fuyao` 均有记录且与目标数据日相同。`capture_date` / `run_date` 在部分补采目录晚于目标数据日；这是自然日与目标数据日的区别，不据此判为过期。
- `2026-10-15` 的 20 条记录都没有 `fin_indicators` 对象，按缺失处理，不当作零值或空对象。
- `2026-10-16` 至 `2026-11-12` 的 17 个目录共 340 条记录均有 `fin_indicators` 对象。五个分组在各 340 条记录中均为对象且非空，没有把分组容器误当成标量。
- 上述 340 条记录的 `fin_report` 均为 `2026-2`。按官方请求参数约定，`-2` 是中报类别；但 `data.report` 是请求回显，故该标签只证明项目选择了该请求期，不能代替来源实际数据日，也不单独证明每个指标的实际报告期内容。

## 裁决边界

本次解决的是字段身份与采集输出结构，不是对子指标的再次定案。分组内每个 `index_id` 仍按自己的完整路径、来源契约和现有裁决维护；样本中出现的成长能力子键与在线契约列表若有覆盖差异，仍是独立的子字段核验事项。没有因容器形态或同一报告请求标签而新增字段含义、跨源等价关系或日期资格。
