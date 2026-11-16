# TDX `latest_indicators` 输出路径核查

复核日期：2026-11-16。没有运行采集。本次只核查 `TDX(双命名源)::latest_indicators` 的完整来源身份、当前解析器与采集器调用链及保留期归档；不定义其子项业务语义，不建立跨源映射。

## 裁决

将精确身份 `TDX(双命名源)::latest_indicators` 记为 `disproved` / `project_derived_capture_output`。`latest_indicators` 不是通达信上游响应中的独立字段，而是项目从 F10「最新提示」文本提取后组装的字典容器。当前采集 JSON 中的完整位置为 `stocks.<code>.reminders.latest_indicators`；注册表的 `code` 是该 F10 解析器返回对象中的键。

这里的 `disproved` 只否定“它是提供方原始字段”的身份，不表示解析器输出错误，也不确认 `eps`、`net_asset`、`roe`、股东人数或财务同比等子项的业务口径、报告期及单位。每个子项仍须按其精确路径单独核验。

## 代码链

- [`core/tdx_client.py` 的 `_f10_get_content()`](../../../core/tdx_client.py#L2259) 返回指定 F10 分类的原始文本。[`tdx_get_latest_reminders()`](../../../core/tdx_client.py#L2295) 读取「最新提示」，用 `split_sections()` 拆分文本，再以标签和正则解析数值；只有分类文本非空时，才创建 `indicators` 并将其放入 `result['latest_indicators']`。这一步是项目解析结果，不是从上游 JSON 透传同名键。
- [`scripts/capture_tcp_collectors.py` 的 `collect_tdx_f10_more()`](../../../scripts/capture_tcp_collectors.py#L371) 将 `tdx_get_latest_reminders()` 的返回值写入每只股票记录的 `reminders` 键，因此在归档中的候选完整位置是 `stocks.<code>.reminders.latest_indicators`。
- [`stock_common/sc_capital_cache.py`](../../../stock_common/sc_capital_cache.py#L211) 当前从 `tdx_get_finance_info()` 读取 `zongguben` 和 `liutongguben`。注释说明旧实现曾错误地从 0x0010 财务对象读取 `latest_indicators`，现已修复；不应把该历史错配当作当前接口字段契约。

## 保留期归档复核

按 [`capture_retention.py`](../../../scripts/capture_retention.py) 的 `MIN_CAPTURE_DATE=2026-10-15`，只读取 2026-10-15 至 2026-11-12 的 18 个目录，没有读取边界前的 raw 或备份样本。逐条路径、采集目录日期、`meta.data_date`、来源状态、`as_of_date` 及 raw/meta SHA-256 见 [结构审计 CSV](../research/20261116_tdx_latest_indicators_path_inventory.csv)。CSV 的规范 LF SHA-256：`7b247ef51915bcf9f5117573804e8c4ab67cd0e06a631028c82d2a2b8e2b888a`。

- `raw_tdx.json` 共 18 个日期归档、360 条股票记录。完整对象递归扫描中，`latest_indicators` 路径为 0/360；其中 2026-11-04 与 2026-11-05 的 TDX 来源状态为 `partial`，其余日期状态为 `ok`。所有日期的 TDX `as_of_date` 均未登记。
- `raw_tdx_f10_more.json` 共 18 个日期归档、360 条股票记录，来源状态均为 `ok`；每条记录都有 `reminders` 空字典，`latest_indicators` 路径为 0/360。18 个文件的 SHA-256 相同（`5561a3fa495894a2c0ee8fb51749c0ed6807a759854d347af155193ebd290961`）。这说明归档没有该解析输出的实际子项值，不据此推断 F10 来源端无数据或请求失败。
- 两类 raw 对应的 `meta.data_date` 均与目录名一致，但都没有来源 `as_of_date`。因此这些归档只用于结构与路径核验，不作数值碰撞或日期语义证据。

## 注册表范围

只处置 `TDX(双命名源)::latest_indicators` 这一个容器身份，保留变更前状态快照和既有来源证据；不新增业务字段、映射或来源路由调整，不修改原始归档。`docs/field_source_reference.md` 中曾将它简称为“F10 接口字段”的行已更正为项目解析容器，并保留旧股本缓存错配已修复的历史说明。
