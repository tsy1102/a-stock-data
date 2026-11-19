# 东财 datacenter 解禁输出字段来源审计

审计日期：2026-11-19。这里只审计采集 JSON 中两个精确路径的生成方式和 registry 归属，不把它们当作行情碰撞或上游接口字段释义证据。

## 裁决

将以下完整身份标为 `disproved` / `project_derived_capture_output`：

- `东财-datacenter(英文键)::free_shares`
- `东财-datacenter(英文键)::shares_is_actual`

这里的 `disproved` 只否定“这是 Eastmoney 上游原始字段”的身份，不表示项目输出值错误。两项输出继续保留供业务和审计使用；不创建跨源映射，不改变采集频率、来源路由或适配器行为。

## 生成链路

`capture_field_probe.py` 将 `datacenter` 采集单元写入 `raw_datacenter.json`；`scripts/capture_context_collectors.py::collect_datacenter()` 对每只股票调用统一层 `get_lockup_expiry()`，输出位于 `stocks.<code>.lockup_expiry[]`。因此 `raw_datacenter.json` 不是单一上游响应的原样副本。

`stock_common/sc_datasource/_financials.py::get_lockup_expiry()` 有两条输入路径：

1. 优先读 TDX F10 股本结构。适配器把 F10 的解禁数量按万股换算为股，同时写入 `free_shares`；该路径固定写入 `shares_is_actual: false`。
2. F10 没有可用解禁记录时回退到 Eastmoney `RPT_LIFT_STAGE`。适配器将 `FREE_SHARES` 和 `ABLE_FREE_SHARES` 换算为股并生成 `free_shares`、`shares_is_actual`；后者是项目根据 `ABLE_FREE_SHARES` 是否为有限非负数计算的布尔标记。

所以 `free_shares` 是规范化后的项目输出；`shares_is_actual` 是项目计算的质量/口径标志。两者都不是可直接归为 Eastmoney 响应键的原始字段。`shares_is_actual: true` 可由当前实现识别为 Eastmoney 回退路径；`false` 不能区分 TDX 路径与缺少有效 `ABLE_FREE_SHARES` 的 Eastmoney 路径。

## 保留期结构审计

结构审计只读取 `scripts/capture_retention.py` 保留边界（`MIN_CAPTURE_DATE=2026-10-15`）之后的目录。对有 `raw_datacenter.json` 的 21 个日期目录逐一核验目录名与 `meta.data_date`，全部一致；扫描到 1 条含上述输出键的解禁事件记录。逐样本目录、事件键和值、raw/meta SHA-256 见 [结构化审计 CSV](../research/20261119_datacenter_lockup_derived_output_audit.csv)，CSV SHA-256：`657e722f685a228d6741a4a0dda8b4837e324520bd259789fb41c4e3edffbc4f`。

该采集容器没有为每条解禁事件提供可证明其上游数据日的 `as_of_date`。因此目录和 `meta.data_date` 在此仅用于保留边界、归档完整性及结构检查；本审计不把自然日当作来源数据日，也不将样本用于数值碰撞或真实语义定案。原始 raw/meta 未修改。

## Registry 处理

两条配对属于 parity 的历史字段基线，但之前未登记在 `field_registry.json.source_fields`。现将其作为项目派生输出补登记，保留原始基线配对计数，同时令它们退出上游未知字段破解队列。裁决前 registry 中不存在这两个精确 `source_fields` 身份；原状态快照记录在 registry 对应条目的 `superseded_status_evidence`。不影响同一采集容器里的其他叶字段。

代码证据 SHA-256：

| 文件 | SHA-256 |
|:--|:--|
| `stock_common/sc_datasource/_financials.py` | `d657a13a5ce47f07065a825f86bd47712a8698f8256af0e76d95634801dea363` |
| `scripts/capture_context_collectors.py` | `b8d954b8d32f2e90450b1d25f249dd9532ce08e8a5a0e541e781ebabeca9d6d3` |
| `scripts/capture_field_probe.py` | `72fa825b44f1682351681ef4e7d157aa77ded80ba8c789dc7fee7264d1f503e6` |
| `scripts/audit_field_completeness.py` | `13450694ea8e0f6800fbc3b80861f2debccec07b88e82bbb95b360a61123db16` |
