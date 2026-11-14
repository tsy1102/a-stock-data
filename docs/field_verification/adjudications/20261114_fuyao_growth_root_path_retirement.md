# Fuyao 同比增长指标旧根路径退役（2026-11-14）

## 决定

退役两个把 `index_id` 叶名误登记为无分组来源根路径的旧身份，并指向已单独实证的完整响应路径：

| 旧路径身份 | 当前完整路径 |
|---|---|
| `同花顺-fuyao::calculate_operating_income_yoy_growth_ratio` | `同花顺-fuyao::growth.calculate_operating_income_yoy_growth_ratio` |
| `同花顺-fuyao::calculate_parent_holder_net_profit_yoy_growth_ratio` | `同花顺-fuyao::growth.calculate_parent_holder_net_profit_yoy_growth_ratio` |

退役只更正来源路径身份，不合并两个身份、不改变嵌套路径的既有语义裁决，也不建立跨源映射。

## 路径证据

- [Fuyao 财务指标接口文档](https://fuyao.aicubes.cn/docs/api-reference/financial-indicators/) 将指标响应组织为 `data.abilities[]`，能力项含 `ability` 与 `indicators[]`，指标项含 `index_id` 和 `value`。项目解析器 [`stock_common/sc_fuyao.py`](../../../stock_common/sc_fuyao.py) 按 `out[ability][index_id]` 保存；采集器 [`scripts/capture_verified_collectors.py`](../../../scripts/capture_verified_collectors.py) 将该对象写入股票记录的 `fin_indicators`。因此，原始响应的字段路径需包含能力分组。
- 保留边界 `20261015` 起，18 个含 Fuyao raw 的目录、360 条个股记录中，每个旧无分组根路径均出现 0 次；对应 `growth` 嵌套路径各有 340 条非空观察。首个保留目录的 20 条记录没有所选报告期指标，按缺值排除。
- 所有 18 个目录的 Fuyao `as_of_date` 与目录数据日一致。其余 17 个目录的 `fin_report` 均为 `2026-2`；重复快照只用于路径存在性核查，不算独立财报期或额外语义样本。
- 逐日、逐股的路径状态、原值、`raw_fuyao.json` 哈希和 `meta.json` 哈希见 [`research/20261114_fuyao_growth_alias_path_inventory.csv`](../research/20261114_fuyao_growth_alias_path_inventory.csv)。没有读取 `20261015` 之前的 raw、ZHB 压缩包或解析缓存。

## 与语义定案的边界

嵌套营业收入同比和归母净利润同比字段的来源内语义，已由 20 家发行人 2026H1 正式报告逐股核验，见 [`20261114_fuyao_growth_empirical_evidence.md`](20261114_fuyao_growth_empirical_evidence.md) 及其逐项比较表。该接口在线文档没有列出样本中的 `calculate_` 前缀 ID，因此这里仅裁定根路径不存在、响应保留分组这一身份问题；不声称文档定义了这两个精确叶名，也不外推其服务端公式。

注册表将旧根身份记为 `disproved` / `retired_legacy_path`，保存其原始状态快照，并把 `canonical` 指向对应嵌套路径。旧身份不再进入未知字段队列；两个嵌套字段维持各自独立的已验证记录。
