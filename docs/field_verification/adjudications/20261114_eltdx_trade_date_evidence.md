# ELTDX Helper `trade_date` 来源契约证据

## 裁决范围

- 精确来源身份：`TDX-eltdx(适配层)::trade_date`
- 运行时字段路径：`global_helpers.limit_ladder.trade_date`、`global_helpers.theme_strength_rank.trade_date`、`global_helpers.stock_theme_strength_rank.trade_date`
- 结论：连板天梯及题材强度结果对应的目标交易日。该值由 `ShortlineIndicatorTable.target_trade_date` 派生；两个题材强度 Helper 继承天梯结果日期。
- 本结论只覆盖 ELTDX 适配层这条来源身份，不创建跨源映射，也不影响 `Levistock历史未归属::trade_date` 或 `财联社(cls)::trade_date`。

## 上游契约

项目固定使用 ELTDX v3.3.2。该版本的 [`FIELD_REFERENCE.md`](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md) 在 ShortlineIndicatorTable 字段表中将 `target_trade_date` 定义为“当前行情对应的目标交易日”。同版本 [`core.py`](https://github.com/electkismet/eltdx/blob/v3.3.2/src/eltdx/helpers/core.py) 给出完整返回链：

1. `LimitLadderTable.trade_date` 是 Helper 返回模型的日期字段。
2. `HelperApi.limit_ladder()` 用 `ShortlineIndicatorTable.target_trade_date` 构造该字段。
3. `HelperApi.theme_strength_rank()` 复制 `ladder.trade_date` 到题材强度表；`stock_theme_strength_rank()` 是该 Helper 的别名。

因此，字段名 `trade_date` 的具体含义由上游类型和赋值链明确限定为 Helper 结果对应的目标交易日，而不是采集运行日、财报日期或公告事件日。

## 项目采集路径

`scripts/capture_tcp_collectors.py::collect_eltdx` 分别调用 `limit_ladder(codes=ecodes)`、`theme_strength_rank(codes=ecodes)` 和 `stock_theme_strength_rank(codes=ecodes)`，并经 `_jfy` 序列化到 `global_helpers`。这与以上三个注册路径一一对应，没有把其他同名源路径并入本结论。

## 保留样本审计

审计仅使用 2026-10-15 起保留期内、同时有 `raw_eltdx.json` 和 `meta.json` 的采集目录；未读取保留边界之前的 raw、ZHB 压缩包或解析缓存。

- 18 个不同的采集目标数据日：2026-10-15、10-16、10-19、10-20、10-21、10-23、10-26、10-28、10-29、10-30、11-02、11-03、11-04、11-05、11-06、11-09、11-10、11-12。
- 每日 3 条 Helper 路径，共 54 条路径观察；独立日期样本数为 18，三个 Helper 对同日的重复输出不计为三个独立日期样本。
- 54/54 个非空日期均与目录 `meta.data_date` 一致，三个 Helper 同日互相一致；所有目录的 ELTDX 来源状态为 `ok`，市场阶段均为 `closed`。
- 每份 raw 中预期的三个 `trade_date` 路径无缺失、无额外路径。`limit_ladder` 在 10 个日期有榜单行，共 13 行；有行时，行级 `target_trade_date` 均与表级 `trade_date` 及目录数据日一致。没有榜单行的日期仍保留表级日期。
- 样本审计 CSV 包含每条记录对应的 raw/meta SHA-256、状态、阶段依据、日期匹配和路径完整性检查。CSV SHA-256：`1C8C7B005A6C7514B2DD4DE834CC0A0E2872892591E24D8D8F18F8F987B30E0E`。

## 日期边界与限制

这些采集元数据的 `source_as_of_dates` 未单独列出 `eltdx`。因此，上述样本证明 Helper 日期值与项目目标数据日相符，但不把 `meta.data_date` 伪称为 ELTDX 独立提供的来源级 `as_of_date`。日期语义来自固定版本上游字段定义和赋值链；样本对照作为项目运行一致性佐证。该决定不声称证明每个 Helper 底层请求的独立更新时间。

## 定案后碰撞回归

全历史本地碰撞报告为 [`20261114_collision_report.md`](../20261114/post-eltdx-trade-date-contract/20261114_collision_report.md)；报告完整性查询结果为 `complete`，对应 JSON SHA-256 为 `E30D89A8F4C0C152B35EB56DCF24BE53C202782BFEE85CC0768480EE7FBAFED1`。按完整运行路径查询 `global_helpers.limit_ladder.trade_date` 返回 0 条候选，确认该路径已退出主攻破解与候选 triage。该碰撞报告只作流程回归证据，不替代上游契约作为语义依据。
