# Push2 `f61` 来源边界复核

## 决定

不把 `东财-push2(stock/get)::f61` 定案为换手率，也不再把 `stock/get::f61/f63` 列为该接口的未知字段目标。此前两条身份由字段审计器把 `field_source_reference.md` §12.8.2 归到 `stock/get` 造成；§12.8.2 实际描述的是 `/api/qt/stock/fflow/daykline/get`，其中 `f57–f65` 只来自外部 SKILL 的请求参数，没有本项目对应的原始响应证据。原注册行状态分别为 `f61=unverified/reference_status_missing`、`f63=unverified/aggregate_status_scope_unresolved`；两行均无逐源参考字段证据、正式裁决或 mapping。

保留 `东财-em_kline_f61::f61=换手率%`。这是另一个 `/api/qt/stock/kline/get` 端点，项目解析器从 K 线逗号串第 11 列读取换手率。不同端点的相同编号不构成相同字段身份。此复核不裁决 Ulist239 的 `f61`，也不声称 Eastmoney `stock/get` 协议永远不会返回 `f61`；若保留期内的未来快照首次实际包含该字段，raw 覆盖审计应把它作为未登记响应字段重新审查。

## 证据

- `scripts/capture_catalog.py` 的 `EM_FULL_FIELDS` 为 `f1` 至 `f250`；`collect_push2()` 将此完整列表发送给 `stock/get`。保留期内 2026-11-02 至 2026-11-10 的 7 个收盘有效数据日、20 只股票，共 140 条成功响应，均无 `data.f61` 或 `data.f63`。同批 `f86` 时间戳 140/140 转换为对应 `meta.data_date`，且 140/140 均晚于北京时间 15:00。11 月 2–5 日 `meta` 缺少逐源采集时间/市场阶段，按 legacy 元数据处理；只用响应内 `f86` 判断来源数据日和收盘后时间，不推断采集启动时间。逐行数据日与文件哈希见 [`20261114_push2_f61_scope_samples.csv`](20261114_push2_f61_scope_samples.csv) 和 [`20261114_push2_f61_scope_manifest.json`](20261114_push2_f61_scope_manifest.json)。
- `stock_common/sc_datasource/_eastmoney.py::get_em_history_fund_flow()` 调用 `/api/qt/stock/fflow/daykline/get`，只请求 `f51–f56`，并把响应位置 0–5 解码为日期和资金流字段。该接口路径与快照 `stock/get` 不同。
- `scripts/capture_http_collectors.py::collect_em_kline_f61()` 调用 `/api/qt/stock/kline/get`，按 K 线字段串位置解析，并将位置 10 存为 `turnover`。这与 `东财-em_kline_f61::f61` 的已登记含义一致。
- 外部文档对 `/stock/kline/get` 的 `fields2=f51…f61` 和 f61 换手率说明，仅作为端点结构的次级佐证：[A 股数据 API 的 Eastmoney 迁移说明](https://ashareapi.com/docs/migrate-from-eastmoney/)、[East Money Data Skill](https://github.com/LangSensei/agentic-catalog/blob/main/skills/eastmoney-data/SKILL.md)。这些不是东方财富官方字段字典，不用于证明 `stock/get::f61` 的语义。

## 修复

- 从 `scripts/audit_field_completeness.py` 的 Push2 `stock/get` 章节映射中移除 §12.8.2，防止外部 SKILL 中的请求字段被误注册到快照字段空间。
- 在 `field_source_reference.md` 中明确 §12.8.2 的 endpoint、项目请求范围和外部候选边界；扩展字段没有原始样本前不登记为项目字段。
- 增加回归断言：§12.8.2 不映射到 Push2 `stock/get`，`f61/f63` 不再从该章节污染快照来源，且 K 线端点 `f61` 仍独立登记。

## 限制

本次没有重新请求 Eastmoney，也没有补采历史资金流扩展字段；当前结论是移除错误的来源归属，不是对任何未采集 endpoint 作“字段不存在”的绝对断言。
