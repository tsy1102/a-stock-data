# ZHB tipinfo 运行字段别名与单位定案

日期：2026-11-09<br>
数据保留起点：2026-10-15<br>
范围：`ZHB-tipinfo` 的 `_parse_tipinfo` 活跃输出字段

## 结论

15 个保留日期包共解析 84,815 条股票记录。逐行比较后，运行字段 `code`、`zt_date_recent`、`hg_date`、`hg_amount_yi` 分别与原始列 `[1]`、`[5]`、`[19]`、`[20]` 完全一致，四项各有 84,815 组配对且不匹配数均为 0。字符串按解析器的去首尾空格行为比较；金额以 `Decimal` 比较原始文本和解析后浮点数的十进制文本，不设容差。

| 运行字段 | 原始列 | 定案含义 | 单位 | 证据边界 |
|---|---:|---|---|---|
| `code` | `[1]` | 股票代码 | 6位字符串 | 不补市场后缀 |
| `zt_date_recent` | `[5]` | 近2年最近涨停板日期 | `YYYYMMDD` | 与通达信官方 `ZTDate_Recent` 描述一致 |
| `hg_date` | `[19]` | 最近回购预案日 | `YYYYMMDD` | 对齐 `RecentHGDate` 官方字段描述；不代表实际公告时间 |
| `hg_amount_yi` | `[20]` | 回购预案金额上限 | 亿元 | 语义来自既有 TdxW 二进制提示字符串；官方快照字段表未列出 `RecentHGAmo`，不声称公开代码映射 |

`[19]` 的旧标签“回购预案公告日”收窄为“最近回购预案日”，避免把日期误读为实际公告时间。`[20]` 的字段说明明确引用本地二进制提示 `回购预案:上限%.2f亿元`；不能据此推导未经公开字段表确认的 `RecentHGAmo` 代码对应关系。

## 原始样本与审计

- 日期化 ZHB 包：2026-10-15 至 2026-11-06，共 15 包；未读取保留起点之前的数据。
- 股票记录：84,815。
- `[19]` 非空记录：35,142；`[20]` 非零记录：35,007。
- 每包文件 SHA-256、记录数及四个别名的配对/不匹配计数：[`20261109_zhb_tipinfo_runtime_alias_audit.csv`](20261109_zhb_tipinfo_runtime_alias_audit.csv)。
- 逐日代表样本：[`20261109_zhb_tipinfo_runtime_alias_samples.csv`](20261109_zhb_tipinfo_runtime_alias_samples.csv)，覆盖每包的 `000001`、`300750`、`600519`。
- 机器可读决定及注册表前后快照：[`20261109_zhb_tipinfo_runtime_aliases.json`](20261109_zhb_tipinfo_runtime_aliases.json)。
- 哈希：审计汇总 `2dea1c0d12c1cb93d445078fc5d5715d1202231f232916dfb1cbac0929940983`；代表样本 `3a96290d67124824873ee993485ffec88251a77af0ec17f73095ada767c50b20`。
- 官方接口字段描述与 `RecentHGAmo` 限制见[公开网页核验记录](public_web/20261109_zhb_tipinfo_runtime_aliases.md)。

## 注册表与运行影响

逐源注册表将四个活跃运行字段标为已验证，并为 `[1]`、`[5]`、`[19]`、`[20]` 补齐明确单位；同步修正 `[5]` 的两年范围和 `[19]` 的日期标签。此次不改解析器、返回值、缓存键、`report_date` 或跨源映射。生成的字段视图会重新计算汇总状态；其他来源同名字段仍按各自 `(source, 完整 code path)` 独立判定。

裁决记录：[`20261109_zhb_tipinfo_runtime_aliases.json`](20261109_zhb_tipinfo_runtime_aliases.json)，ID `zhb-tipinfo-runtime-aliases-20261109`。
