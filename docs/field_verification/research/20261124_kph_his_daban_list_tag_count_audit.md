# KPH `HisDaBanList` `limit_tag` / `limit_count` 样本补充（2026-11-24）

## 精确路径

本记录仅覆盖项目当前 [`_kph.py`](../../../stock_common/sc_datasource/_kph.py) 的 `get_kph_limit_up_history()` 路径：`HisHomeDingPan/HisDaBanList`。解析器把响应 `row[9]`、`row[10]` 写入项目 KPH 源 `开盘红::limit_tag`、`开盘红::limit_count`。这是对当前 KPH 适配路径的来源内样本补充；对应字段原已在 registry 中验证，本记录不改规范名、含义、单位或映射。

该端点不同于 Levistock `get_his_limit_resumption()` 的 `HisLimitResumption/GetPlateInfo_w38`。因此这些样本不用于定案 `开盘红(Levistock适配)` 下的同名路径。开盘红 KPH 与开盘啦 KPL 保持独立，本记录不以 KPL 值作为字段定义或同源证据。

## 日期与样本

- 检查 2026-10-15 起、碰撞报告 25 个保留交易日目录里的 KPH 归档。22 个目录含 `raw_kph.json`，其中 21 个非空批次、1 个空批次；空批次不进入样本比较。
- 21 个非空批次的请求日期等于响应顶层 `trade_date`；逐行 `__identity__.trade_date` 也与该响应日期相同。采集目录日期只用于定位样本，不替代来源日期。
- 885 条观测去重后为 723 个唯一 `(来源数据日, 证券代码)` 记录，覆盖 551 只证券和 17 个来源数据日。162 条重复观测逐项一致、无冲突，不作为独立比较。

## 关系复核

对每个唯一证券-来源日记录解析 `limit_tag` 的计数部分：`首板` 取 1，`N连板` 取 N，`N天M板` 取 M。723/723 个唯一记录均与 `limit_count` 一致，0 反例；重复观测均与对应的唯一记录一致。可复核逐行数据见[审计 CSV](20261124_kph_history_limit_count_audit.csv)，输入日期与文件哈希见[清单](20261124_kph_history_limit_count_manifest.csv)。

这批数据仅作为 `开盘红::limit_tag/limit_count` 既有来源内定义的补充证据；它不确认 `N天` 的统计窗口算法，不外推到另一个 KPH 端点，也不生成跨源映射。
