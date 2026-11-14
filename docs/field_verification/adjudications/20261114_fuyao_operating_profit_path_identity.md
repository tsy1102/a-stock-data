# Fuyao 营业利润同比字段完整路径与实证

复核日期：2026-11-14
范围：`同花顺-fuyao` 营业利润同比字段的完整响应路径；不创建跨源映射。

## 路径结论

| 状态 | 精确身份 | 解释 |
|---|---|---|
| 当前采集字段，来源内已验证 | `同花顺-fuyao::growth.calculate_operating_profit_yoy_growth_ratio` | 发行人报告中营业利润相较上年同期的同比增长率，按百分数值返回。2026H1 样本经验式为 `(本期营业利润 - 上年同期营业利润) / abs(上年同期营业利润) × 100`。 |
| 退役的旧无前缀身份 | `同花顺-fuyao::calculate_operating_profit_yoy_growth_ratio` | 旧登记把 `index_id` 叶名当成源对象根字段；当前响应/解析器没有这一根字段。此退役仅更正路径身份，不否定叶名或当前字段语义。 |

## 官方响应结构与项目序列化

- [Fuyao 财务指标接口文档](https://fuyao.aicubes.cn/docs/api-reference/financial-indicators/) 将响应定义为 `data.abilities[]`，每项含 `ability` 和 `indicators[]`，指标项再含 `index_id` 与 `value`；文档说明 `growth` 是能力分组，并把百分比增长率按百分数值表达。此结构中指标叶名必须与其 `ability` 父级一起定位。
- `stock_common/sc_fuyao.py::get_fuyao_fin_indicators` 按 `out[ability][index_id] = value` 组装返回值，不把指标提升为根级字段，也不改变叶名。`scripts/capture_verified_collectors.py` 将此返回对象保存到每只股票的 `fin_indicators`，所以项目中的精确路径是 `fin_indicators.growth.calculate_operating_profit_yoy_growth_ratio`；注册表的来源字段路径省略 `fin_indicators` 外层采集包装，记作 `growth.calculate_operating_profit_yoy_growth_ratio`。
- 当前在线文档表中列出的 ID 是无 `calculate_` 前缀的 `operating_profit_yoy_growth_ratio`；保留样本实际响应叶名有 `calculate_` 前缀。因此文档支持分组结构、报告期和百分数值惯例，但不被当作实测 ID 的精确契约。具体语义由下面的原始采集和发行人报告实证确认。

## 留存 raw 路径审计

只检查保留边界 `20261015` 及之后、Fuyao 来源日期与采集目录相符的样本。18 个目录共 360 条股票记录：

- `20261015` 有 20 条记录，但该报告期没有指标值；按缺失排除。
- 其余 17 个目录均为 `fin_report=2026-2`；共 340 条记录。每条在 `fin_indicators.growth.calculate_operating_profit_yoy_growth_ratio` 有值。
- 在全部 360 条记录中，`fin_indicators.calculate_operating_profit_yoy_growth_ratio` 根键出现 0 次；嵌套路径出现 340 次。

逐日期、逐股票、报告期、根键/嵌套键存在性与原始值见 [`20261114_fuyao_operating_profit_path_inventory.csv`](../research/20261114_fuyao_operating_profit_path_inventory.csv)。日期目录和来源 `as_of_date` 每条一致；`20261015` 缺值不拿来支持字段含义，也不计为有效指标观察。未读取保留起点之前的 raw、ZHB 压缩包或解析缓存。

## 财报语义与精度

目标数据日 `20261112` 的 20 个 `fin_report=2026-2` 值，逐股与巨潮资讯网对应发行人的 2026H1/2025H1 正式报告“营业利润”行复算，20/20 支持同一项目、0 个反例。最大绝对误差为 `4.647356636475838744e-7` 个百分点，最大相对误差为 `1.596344330672318576e-7`；全部金额、复算率、原始值、误差、报告页码、公告号、PDF URL 与 SHA-256 见 [`20261114_fuyao_growth_official_h1_comparisons.csv`](../research/20261114_fuyao_growth_official_h1_comparisons.csv) 中 `operating_profit` 的 20 行。

这些样本覆盖 20 家发行人和同一报告期；另有 17 次重复采集只作值稳定性核查，不作为 17 个独立报告期。绝对误差虽小但非零，差异原因未证实，不称为舍入。来源内结论不外推到其他字段或报告期，不建立跨源映射。

## 注册表处置

旧根路径按 `disproved` / `retired_legacy_path` 退役，`canonical` 指向当前完整嵌套路径；原无前缀历史说明保留，不改写历史档案。当前完整路径单独登记并以 E3 来源内实证确认为已验证，使用 `%` 单位。注册表 parity 通过 `source_field_addenda` 声明该基线外完整路径，并以 E3 决策中的 `matrix_projection_removals` 移除旧根路径矩阵投影。两个身份不合并为同一活动字段，也不创建 `mappings`。
