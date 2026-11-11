# ZHB tipinfo 剩余运行字段别名核验（2026-11-10）

## 范围

本次核对两个主字典待破解路径：`ZHB-tipinfo::forecast_type` 与 `ZHB-tipinfo::suspend_major_event_date`。它们对应 `tipinfo.dat` 原始列 `[12]`、`[7]`，解析器此前没有输出这两个运行键。本次将其作为未变换的字符串值接入 `ZhbData.tip_info`，并分别与注册表中已有的同源已验证路径 `tipinfo.forecast_type`、`tipinfo.suspend_major_event_date` 对照。

本次不解释 `[12]` 的完整整数码表，也不新增跨源映射。

## 保留归档审计

- 只读取 2026-10-15 起的 15 个日期化 ZHB ZIP，覆盖 2026-10-15 至 2026-11-06；ZIP 文件名作为数据日期。
- 解析 84,815 条股票行。每个股票代码唯一，逐包解析行数与原始行数一致。
- `forecast_type` 与原始 `[12]`：84,815 组精确配对，1,454 个非空值，0 个差异；非空值均为十进制数字字符串。
- `suspend_major_event_date` 与原始 `[7]`：84,815 组精确配对，7,288 个非空值，0 个差异；所有非空值均为有效 `YYYYMMDD` 日期。
- 逐包行数、ZIP SHA-256、配对数、非空数及差异数见 [`20261110_zhb_tipinfo_remaining_alias_audit.csv`](20261110_zhb_tipinfo_remaining_alias_audit.csv)。审计文件 SHA-256：`514c6c30e27460134161c828a2aebc16883871ab0fc4e7e22fdec4fb4835e6af`。

## 字段结论

| 运行路径 | 原始列 | 已验证同源锚 | 结论与范围 |
|---|---:|---|---|
| `forecast_type` | `[12]` | `tipinfo.forecast_type` | 定义为业绩预告类型代码，按字符串原样保留，单位沿用枚举类别。只确认字段角色和路径别名；已观察到哪些代码及其公告样本见 [`20261110_zhb_tipinfo_public_crosscheck.md`](20261110_zhb_tipinfo_public_crosscheck.md)，但没有找到官方完整整数码表，不能把候选代码解释升级为确定映射。 |
| `suspend_major_event_date` | `[7]` | `tipinfo.suspend_major_event_date` | 定义为重大事项停牌起始日，按 `YYYYMMDD` 字符串原样保留。2026-11-06 包中的 002129、000831、002623 样本分别与深交所/巨潮资讯公告中的停牌日期相符；这不代表字段覆盖所有停牌原因、盘中临停或短时停牌，详见 [`20261110_zhb_tipinfo_public_crosscheck.md`](20261110_zhb_tipinfo_public_crosscheck.md)。 |

## 运行影响与边界

`get_tip_info()` 返回字典新增两个来源原值；`scripts/capture_tcp_collectors.py` 会将其保存在每只股票的 `tipinfo` 节点。现有业务合并仍只读取 `report_period`，不改变数据路由、缓存键、缓存期限、来源日期规则或报告事件锁。下次采集会在原始 JSON 中包含这两个键。

2026-11-10 当天采集的目标数据日为 2026-11-09，但最新 ZHB 包日期仍为 2026-11-06；本次全历史审计使用的是明确标记的留存包，不将它们描述为 11 月 9 日新鲜样本。

正式决定：[`20261110_zhb_tipinfo_remaining_aliases.json`](20261110_zhb_tipinfo_remaining_aliases.json)。
