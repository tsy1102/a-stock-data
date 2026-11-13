# TDX 0x0010 Easy-TDX 兜底别名财务语义补证（2026-11-13）

## 裁决目标与范围

本补证核对三个精确注册路径：`TDX(双命名源)::faqiren_faren_gu`、`TDX(双命名源)::faqirenfarengu` 和 `TDX(双命名源)::faren_gu`。不合并注册身份、不创建跨来源 `mappings`，也不把结论推广到其他拼写或其他来源。

它补足截图字段 `fa_qi_ren_fa_ren_gu_raw_float`、`fa_ren_gu_raw_float` 的 Easy-TDX 兜底路径。此前对 ELTDX 当前主路径 `fajirenfarengu` / `farengu` 的 E3 结论来自同一批 20 只股票及五份发行人 2026 年第三季度报告，见[前序对照表](20261112_tdx_finance_current_sample_comparison.csv)和[原始定案记录](20261112_tdx_finance_slots_semantic_alignment.md)。

## 日期与样本资格

- 只读取保留期内的 `20261110/raw_eltdx.json`、`20261110/raw_tdx.json`；未读取 2026-10-15 以前的 raw、ZHB 包或解析缓存。
- 采集目录目标数据日为 2026-11-10；每条财务记录另有来源 `updated_date`（样本为 2026-10-28 至 2026-10-31），与发行人 2025-09-30 比较期对齐。采集目录日期不替代财务报告期或来源更新日期。
- 20 只保留股票各有一个同次请求的 0x0010 `record_hex`；另有同一来源族的历史适配器输出快照。ELTDX 与 Easy-TDX 解码的是同一份原始槽位，不能计为独立来源样本。

## 解析路径与别名关系

1. `core/eltdx_adapter.py::_FIN_MAP` 将 `fa_qi_ren_fa_ren_gu_raw_float` 映射到主路径 `fajirenfarengu`，将 `fa_ren_gu_raw_float` 映射到 `farengu`；当前金额兼容输出按“千元 × 10,000 = 角”归一。
2. 已安装的 Easy-TDX 1.20.8 `GetFinanceInfoCmd.parse_response` 可直接解码保存的 `record_hex`。它先输出 `FinanceInfo.faqiren_faren_gu`、`FinanceInfo.faren_gu`；解码值均为原始浮点值 × 10,000。`core/tdx_client.py::_EasyTdxAdapter.finance` 会为原字段再生成删除下划线的别名，因此分别得到 `faqirenfarengu`、`farengu`。
3. 对 20 条保留 `record_hex` 离线重解码：`faqiren_faren_gu` 与 `faqirenfarengu` 的值，逐条精确等于该原始槽位 × 10,000；`faren_gu` 与 `farengu` 同理。两组值又分别与 ELTDX 当前主适配器归一后的 `fajirenfarengu`、`farengu` 逐条精确相等。逐股原值、更新日期、别名值、快照比较和 record hash 见[逐样本 CSV](20261113_tdx_finance_fallback_alias_semantics_samples.csv)。

Easy-TDX 自身的模型/文档把这些旧名称按股本类别命名；这只证明客户端层保留的标签。它与同一协议槽位的全样本实际数值及发行人财报相冲突，不能作为底层服务端该批返回值的语义定案。

## 发行人报告语义核对

20 只股票的两个原始值分别按 `raw × 1,000 = 元` 与同一 2025Q3 报告比较期核对；20/20 均落在前序证据记录的精度范围内，零反例。五只股票再按正式发行人 2026 年第三季度报告逐值复核：

- `faqiren_faren_gu` / `faqirenfarengu`：对应上年同期归属于上市公司股东的净利润，金额输出角口径。
- `faren_gu`：对应上年同期营业收入，金额输出角口径。

五份发行人报告：[泸州老窖](https://static.cninfo.com.cn/finalpage/2026-10-30/1225639079.PDF)、[万华化学](https://static.cninfo.com.cn/finalpage/2026-10-27/1225622843.PDF)、[贵州茅台](https://static.cninfo.com.cn/finalpage/2026-10-31/1225649896.PDF)、[农业银行](https://static.cninfo.com.cn/finalpage/2026-10-31/1225649460.PDF)、[殷图网联](https://static.cninfo.com.cn/finalpage/2026-10-30/1225649649.PDF)。逐样本差值、相对误差及发行人报告覆盖标志在 CSV 与[前序定案记录](20261112_tdx_finance_slots_semantic_alignment.md)中保存。

## 定案边界

按 exact `(source, code path)` 分别登记：`faqiren_faren_gu`、`faqirenfarengu` 均为上年同期归母净利润，`faren_gu` 为上年同期营业收入；三个输出单位均为角。它们是同一 TDX 0x0010 原始槽位通过不同客户端字段名暴露出来的路径别名，不是相互独立的采集源。旧模型标签及原 registry 快照保留为历史参考；不改只读历史报告，不新增跨源映射，也不改主路径 `fajirenfarengu` / `farengu` 已有结论。

输入 SHA-256：
- `raw_eltdx.json`: `6952797ab5f73c4915989ed2c1a5a4abf49336b8064f488b182d6fea947cddf6`
- `raw_tdx.json`: `99a8668ef019883a99c9800956630c0c04931ef416e5cf30a8afd9de9e98fd99`
- 前序 20 股对照 CSV: `40074c88c2596666b8db1c6750594f6d7b5de6c247f44535c1848fed3434fcfe`
- 本补充逐样本 CSV: `245fd5ff612151d6d28da2d324656a3c0cb27296282aa1f909ee2f3cde568c4d`
