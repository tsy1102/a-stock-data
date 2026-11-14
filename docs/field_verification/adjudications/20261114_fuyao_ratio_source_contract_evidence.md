# Fuyao 盈利与偿债比率字段核验（2026-11-14）

## 裁决范围

核验 `同花顺-fuyao` 的四个精确字段路径：`profitability.index_weighted_avg_roe`、`profitability.sale_gross_margin`、`profitability.sale_net_interest_ratio`、`solvency.assets_debt_ratio`。本裁决确认这些来源内字段的名称、含义和百分数单位；不建立跨来源映射，不声称样本数据质量绝对无误。

## 官方接口定义与项目路径

[Fuyao 官方财务指标接口文档](https://fuyao.aicubes.cn/docs/api-reference/financial-indicators/)把响应定义为 `data.abilities[]`，其中每个能力块有 `ability`，指标项有 `index_id` 与 `value`；`profitability`、`solvency` 是明确的能力分组，百分比类 `value` 按百分数值表达。文档的指标表直接列出本裁决四个 ID 及其中文标签。仓库留存的契约镜像为 [`docs/verify/fuyao_api_full.md`](../../verify/fuyao_api_full.md) §财务指标数据。

`stock_common/sc_fuyao.py::get_fuyao_fin_indicators` 以 `out[ability][index_id] = value` 组装对象；`scripts/capture_verified_collectors.py` 把对象存入每只股票的 `fin_indicators`。因此注册表路径准确写作上述分组加 `index_id`，不能把裸叶名当作另一个根字段。

## 日期与样本资格

- 项目样本：`docs/field_verification/20261112/raw_fuyao.json`，来源 `as_of_date=2026-11-12`；20 只股票均为 `fin_report=2026-2`，即 2026 年中报。
- 官方样本：对应发行人在巨潮资讯网发布的 20 份 2026H1 正式报告。每行报告公告号、下载 URL、PDF SHA-256 与页码均记录在 [`20261114_fuyao_official_ratio_h1_comparisons.csv`](../research/20261114_fuyao_official_ratio_h1_comparisons.csv)。金额使用同一合并报表的相同单位后再计算比率；不把披露日期或自然日当成报告期。
- 路径审计只读保留起点 `20261015` 及之后的 18 个采集目录：每日期 20 条股票记录，共 360 条。每个完整嵌套路径在已就绪的 17 个 `2026-2` 日期中出现 340 次；`20261015` 的 20 条记录无该报告期指标。四个裸根路径在全部 360 条记录中均为 0 次。逐日期、逐股票和值见 [`20261114_fuyao_ratio_path_inventory.csv`](../research/20261114_fuyao_ratio_path_inventory.csv)。同一报告期的 17 次重复抓取仅作路径及稳定性核查，不计为 17 个独立财报样本。

## 逐字段官方报告对照

| 完整路径 | 可比命中 | 反例 | 不可比 | 最大绝对误差（百分点） |
|---|---:|---:|---:|---:|
| `profitability.index_weighted_avg_roe` | 19/20 | 1 | 0 | 0.1300 |
| `profitability.sale_gross_margin` | 19/20 | 0 | 1 | 0.00004941737003535763093043 |
| `profitability.sale_net_interest_ratio` | 20/20 | 0 | 0 | 0.00004996693563930244673002 |
| `solvency.assets_debt_ratio` | 20/20 | 0 | 0 | 0.00004971964992626301794111 |

毛利率、净利率和资产负债率的采集数值均按四位小数输出；全精度报表金额复算后，误差上限不超过 0.00005 个百分点，符合四位小数展示的舍入界限。公式与逐股金额、报告页码和误差详见对照 CSV。

### ROE 的日期/年化口径与单一异常

农业银行 2026H1 报告的财务指标表把加权平均净资产收益率披露为 10.14%，并以星号注明“年化后数据”；其详细财务附注（PDF 第 283 页）也标为“年化”。Fuyao 对应值为 5.0700%，折算半年期间后与报告吻合。其余 18 家中有 18 家直接吻合，但太湖远大一例仍不吻合：发行人报告（PDF 第 8 页）披露 7.64%，Fuyao 为 7.7700%，差 0.13 个百分点。没有证据证明这是舍入、报告期差异或其他合法换算，因此保留为一个未解释的数据口径/取值异常。该反例不改变官方接口对字段 ID 的明确释义，但本裁决不会把它描述成 20/20 数据一致。

## 旧根路径身份退役

以下历史裸叶身份都不是当前响应中的根级输出：

| 退役身份 | 当前完整路径 |
|---|---|
| `同花顺-fuyao::index_weighted_avg_roe` | `同花顺-fuyao::profitability.index_weighted_avg_roe` |
| `同花顺-fuyao::sale_gross_margin` | `同花顺-fuyao::profitability.sale_gross_margin` |
| `同花顺-fuyao::sale_net_interest_ratio` | `同花顺-fuyao::profitability.sale_net_interest_ratio` |
| `同花顺-fuyao::assets_debt_ratio` | `同花顺-fuyao::solvency.assets_debt_ratio` |

官方响应结构、项目解析器和全部保留样本共同证明当前字段位于分组对象下。退役只清除未限定分组的重复身份；不否定或合并任一嵌套字段，也不改写历史来源文档。

## 裁决结论

四个嵌套字段依官方接口契约确认来源内名称与 `%` 单位，字段状态可由历史 `status_conflict` 收敛为 `verified_by_source_contract`。三项比率的报告复算完整命中；ROE 的名称/单位由精确 API 契约确认，另外保留 920118 的 0.13 个百分点数据异常。对来源独立性与跨源等价性没有作出结论，也不新增 `mappings`。
