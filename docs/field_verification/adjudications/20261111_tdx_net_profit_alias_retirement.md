# TDX `net_profit` 伪来源路径退役（2026-11-11）

## 身份与决定

退役 `TDX(双命名源)::net_profit`：该身份不是 TDX 当前采集响应中的独立原始字段，而是旧的统一字段名/归一化别名。当前 TDX 原始路径是 `finance_info.jinglirun`；数据提供层读取该键后把结果写到统一模型的 `net_profit`。保留统一模型字段 `net_profit`，只将错误的 TDX 原始路径身份移出默认破解队列。

## 路径证据

- 旧项目字段参考记录明确写有 `net_profit → jing_lirun`，位置见 [`field_source_reference.md`](../../field_source_reference.md) §0.C（TDX 本地 easy_tdx F10 0x0010 字段闭环）。
- 当前 `core/tdx_client.py` 仅把 TDX 财务列名下划线去除（`jing_lirun → jinglirun`），没有生成 `net_profit` 源列；`core/data_provider.py` 读取 `finance_info.jinglirun`、除以 10 后才写入统一输出键 `net_profit`。
- 解析器回归在 `tests/data/test_data_tdx.py::TestAdapterFinance.test_columns_underscore_removed` 覆盖当前输出键；新增断言确保适配器不伪造原始源列 `net_profit`。

## 保留样本审计

仅读取保留起点 2026-10-15 起、根目录日期化目录内的 17 个 `raw_tdx.json`，共 340 条股票记录。每个目录均为 20 条记录：

`20261015`、`20261016`、`20261019`、`20261020`、`20261021`、`20261023`、`20261026`、`20261028`、`20261029`、`20261030`、`20261102`、`20261103`、`20261104`、`20261105`、`20261106`、`20261109`、`20261110`。

审计结果：原始 TDX 响应中 `finance_info.net_profit` 命中 0 次，所有位置的 `net_profit` 叶字段命中 0 次；340/340 条记录都有 `finance_info.jinglirun`。这支持“旧别名不再作为独立采集路径存在”，不证明 TDX 不会在其他接口或未来版本新增同名字段。

## 对 `jinglirun` 的区分

`finance_info.jinglirun` 的语义已另按 2026Q3 财报和 20 家同报告期样本定案为归母净利润，见 [`20261111_tdx_jinglirun_empirical_semantics.md`](20261111_tdx_jinglirun_empirical_semantics.md)。本退役决定不把旧 `net_profit` 与当前 `jinglirun` 声明为字段映射，也不把 TDX `jinglirun` 与 Fuyao `net_profit` 合并为同一语义。
