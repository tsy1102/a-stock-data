# 近两周主字典同义路径审查（2026-11-24）

## 结论

检查到 6 组释义相同或高度重叠的完整路径。它们不应因文本相同而从 registry 删除：字段身份按 `(source, 完整 code path)` 区分。应说明是不同响应结构、原始/规范化两种表示，还是共享枚举定义；这些关系不自动成为跨源 `mappings`，也不自动构成独立来源或独立日期证据。

## 路径关系

| 路径组 | 关系与证据 | 处理 |
|---|---|---|
| `TDX-eltdx(适配层)::previous_trade_date` / `TDX-eltdx(适配层)::limit_ladder.previous_trade_date` | 同一“上一实际交易日”概念，但一个是历史登记的扁平完整路径，另一个是 ELTDX `limit_ladder` 返回行中的嵌套路径。registry 对嵌套路径有独立 v3.3.2 契约证据。现有证据没有建立两个路径在同一请求、每条记录上恒等。 | 保留完整路径并分开核验；不据同义名称断言逐值别名。 |
| `TDX-eltdx(适配层)::stats_date` / `TDX-eltdx(适配层)::limit_ladder.stats_date` | 同一“统计资源主导日期”概念，分别是扁平与嵌套路径；路径与来源契约按各自登记处理。 | 保留完整路径，不当作重复采集源或独立日期样本。 |
| `开盘啦(kpl_limit_up_detail)::amplitude` / `...::raw_columns.col_17` | 采集器将 `row[17]` 解析为规范化数值 `amplitude`，并在 `capture_raw` 下把原始位置存为 `col_17`。保留期审计中原列与规范值 1,165/1,165 一致；原始类型、缺失值表现与规范化数字仍有区别。 | 保留两种身份，标作同一 KPL 行的原始/规范化表示；不把它们算作两个来源或两个独立样本。 |
| `开盘啦(kpl_limit_up_detail)::main_buy` / `...::raw_columns.col_09` | 规范字段由同一行 `row[9]` 转成数值；原列保留原值。裁决记录的原始列与规范值 1,165/1,165 一致。 | 同上；不删除原始路径。 |
| `开盘啦(kpl_limit_up_detail)::main_sell` / `...::raw_columns.col_10` | 规范字段由同一行 `row[10]` 转成数值；原列保留原值。裁决记录的原始列与规范值 1,165/1,165 一致。 | 同上；保留负值表示流出的已核释义。 |
| `东财-event_dc(可转债列表)::convertible_bonds[].EXECUTE_REASON_HS` / `...EXECUTE_REASON_SH` | 东财第一方 `detail.js` 分别为两键实现相同的 1–5 展示枚举。它们是两个原始字段路径；共同代码表不证明两列每个债券的值相等，代码 6 仍未定。 | 保留两条逐源路径和相同的已证实代码表；不合并字段、不建映射、不把代码 6 外推。 |

## 可复核依据

- ELTDX 精确嵌套路径的官方契约记录位于 `field_registry.json` 的 `limit_ladder.*` 字段证据中；扁平字段保持各自原始登记。
- KPL 解析实现：[`stock_common/sc_kpl.py`](../../../stock_common/sc_kpl.py) 的 `get_kpl_limit_up_detail()`。身份更正、逐值样本数量和适用边界见[2026-11-18 裁决](../adjudications/20261118_kpl_source_identity_correction.md)及其 CSV。
- EventDC 两个枚举键的第一方脚本依据和 code 6 边界见[2026-11-22 穷尽批次](../adjudications/20261122_exhaustive_empirical_semantics.md)及相应的 `field_registry.json` 来源契约记录。

本审查仅澄清完整路径之间的关系，不新增或撤回字段语义裁决，不修改采集逻辑，也不建立跨源字段等价关系。
