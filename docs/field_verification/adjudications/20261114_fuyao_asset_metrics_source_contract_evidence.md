# Fuyao 总资产指标字段核验（2026-11-14）

## 裁决范围

确认 `同花顺-fuyao` 的三个来源内完整路径：`growth.total_assets_growth_ratio`、`profitability.total_assets_net_ratio`、`profitability.index_deduct_weighted_avg_roe`。本次只确认接口字段身份、中文释义及官方可确定的单位；不建立跨源映射，也不把样本公式外推为所有报告期的统一算法。

## 官方契约与项目路径

[Fuyao 官方财务指标文档](https://fuyao.aicubes.cn/docs/api-reference/financial-indicators/) 定义 `GET /api/a-share/financials/indicators`，指标项包含 `index_id` 和 `value`，并按 `data.abilities[]` 的 `ability` 分组。文档逐项列出：`growth.total_assets_growth_ratio` 为“总资产增长率”，`profitability.total_assets_net_ratio` 为“总资产收益率”，`profitability.index_deduct_weighted_avg_roe` 为“扣非加权净资产收益率”。响应约定明确百分比类指标的值按百分数表达。仓库保存的契约镜像见 [`docs/verify/fuyao_api_full.md`](../../verify/fuyao_api_full.md) §财务指标数据。

项目适配器 [`stock_common/sc_fuyao.py`](../../../stock_common/sc_fuyao.py) 的 `get_fuyao_fin_indicators` 按 `out[ability][index_id] = value` 保留分组和 ID；[`scripts/capture_verified_collectors.py`](../../../scripts/capture_verified_collectors.py) 将该对象放入每只股票的 `fin_indicators`。所以注册表完整路径是上述分组加 ID。没有证据表明裸叶名是 `fin_indicators` 下的独立字段。

## 日期与路径样本

- 路径审计只读取保留起点 `20261015` 及之后含 `raw_fuyao.json` 的目录：18 个目录、360 条股票记录。另有 8 个保留期目录没有 Fuyao raw 文件，不计入来源路径样本；没有读取保留起点之前的 raw、ZHB 文件或解析缓存。
- 18 个来源 `as_of_date` 均与各自采集目录的数据日一致。首个目录 `20261015` 的 20 条记录没有所选财报期指标；其余 17 个来源数据日均为 `fin_report=2026-2`，共 340 条有值观察。
- 三个完整嵌套路径各出现 340 次；对应的无分组路径 `fin_indicators.<leaf>` 在全部 360 条记录中各出现 0 次。逐目录、逐股票和值见 [`20261114_fuyao_asset_metrics_path_inventory.csv`](../research/20261114_fuyao_asset_metrics_path_inventory.csv)。这些重复快照只用于路径和稳定性核验，不当成 340 份独立财报。

## 2026H1 财报复算

使用 20 家发行人 2026 年半年度报告的合并报表，与 `20261112` Fuyao 样本的 `fin_report=2026-2` 对照。公告号、PDF 地址、PDF SHA-256、报表页码、输入金额、公式和误差逐项记录在 [`20261114_fuyao_official_asset_metrics_h1_comparisons.csv`](../research/20261114_fuyao_official_asset_metrics_h1_comparisons.csv)。金额均取自同一份合并报表，按原报表共同单位计算。

| 完整路径 | 官方释义 | 复算结果 | 限定 |
|---|---|---|---|
| `growth.total_assets_growth_ratio` | 总资产增长率，`%` | 当前期末合并总资产相对上期末未调整合并总资产的增长率，20/20 与 Fuyao 四位小数值相差不超过 `0.00005` 个百分点；最大误差约 `0.000041154` 个百分点。19 家报告直接披露该项，其中 18 家与 Fuyao 显示值吻合。 | 中华企业（600675）是一个比较基数差异：Fuyao `-8.1301%` 与上期末未调整资产 `55,006,636,710.01` 元复算相符；发行人摘要使用调整后资产 `55,021,685,328.71` 元并披露 `-8.16%`。差异约 `0.0299` 个百分点，不是舍入。保留为已知数据口径差异，不据此否定官方字段标签，也不宣称 Fuyao 与发行人重述后的展示值完全一致。 |
| `profitability.total_assets_net_ratio` | 总资产收益率，`%` | 当期合并净利润 ÷ 当前期末与上期末未调整合并总资产均值 × 100，20/20 命中四位小数舍入范围；最大误差约 `0.000049977` 个百分点。 | 这是 2026H1 样本中支持的复算关系，不声明为所有期间、行业和报告类型的普遍算法。 |
| `profitability.index_deduct_weighted_avg_roe` | 扣非加权净资产收益率，`%` | 依据官方接口对精确 `index_id` 的中文标签及百分数值约定定案。保留期 340 条有值观察全部落在该官方分组路径。 | 本次不声称已独立复算加权平均净资产收益率，也不推断年化规则或具体计算公式。 |

## 裁决结论

三个完整路径的官方 `index_id`、分组、中文释义及百分数单位明确，项目解析器和 raw 样本保留相同路径，因此按来源契约定案。财报复算用于检验 `total_assets_growth_ratio` 与 `total_assets_net_ratio` 的样本数值，并保留中华企业的比较基数差异；不把复算公式升级为上游的全局算法承诺。`index_deduct_weighted_avg_roe` 本次仅按精确官方字段契约确认名称和单位。三个裁决均不新增跨源 `mappings`。
