# ZHB tipinfo `[8]/[9]` 当前字段状态收敛

复核日期：2026-11-09<br>
数据保留起点：2026-10-15<br>
前序语义核验：[`20261108` 股东持股变动裁决](../zhb_tipinfo_shareholder_change_adjudication_20261108.md)

## 定案

将 `ZHB-tipinfo::[8]`、`ZHB-tipinfo::[9]` 的当前状态由 `disproved` 更正为 `verified`，保留原始列含义、单位和运行值：

| 完整来源路径 | 当前含义 | 单位 | 当前状态 |
|---|---|---|---|
| `ZHB-tipinfo::[8]` | 股东持股变动记录关联日期；可为交易日、区间截止日或权益变动协议签署日 | `YYYYMMDD` | `verified` |
| `ZHB-tipinfo::[9]` | 股东持股变动数量；正值为增持/转入，负值为减持/转出 | 万股 | `verified` |

此前的 `disproved` 表达的是已撤回的“业绩预告日/业绩预告金额”解释，不是原始列无效。注册表把这个解释状态应用到了来源字段本身，导致“含义已改正但列仍证伪”，也使已验证的新运行路径无法与列号形成闭环。现在将当前列定义设为已验证，并完整保留旧参考文本与旧裁决 ID 供历史追溯。旧输出键 `div_date`、`div_amount` 及 `tipinfo.div_*` 仍表示已废弃身份，维持 `disproved`；本次不复活这些键。

## 留存样本对照

对 2026-10-15 至 2026-11-06 的 15 个保留日期化 ZHB 包重新调用当前 `_parse_tipinfo()`：

- 84,815 条股票记录中，`[8]` 与 `shareholder_change_date`、`[9]` 与 `shareholder_change_shares_wan` 各有 84,815 组配对；不匹配数均为 0。
- `[8]` 日期和 `[9]` 数量各有 50,604 条非空值；股数有 8,864 个正值、41,740 个负值。
- 日期逐字比较（解析器仅去除首尾空格）；股数以 `Decimal(原始文本) == Decimal(str(解析浮点数))` 比较，空原值要求解析结果为 `None`，没有使用容差。
- 每包股票行数及压缩包 SHA-256：[`20261109_zhb_tipinfo_shareholder_alias_audit.csv`](20261109_zhb_tipinfo_shareholder_alias_audit.csv)。逐日三股代表样本：[`20261109_zhb_tipinfo_shareholder_alias_samples.csv`](20261109_zhb_tipinfo_shareholder_alias_samples.csv)。

前序三条公告核验覆盖高管增持、累计减持和国有股权无偿划转；公告展示的数量经万股换算、四舍五入后与 `[9]` 的正负方向和量级相符。它们支持股数语义，也显示 `[8]` 可能记录公告所涉交易日、区间截止日或协议签署日，不能一律解释为逐笔交易日期。公开网页的具体证据边界见[公开核验记录](public_web/20261109_zhb_tipinfo_shareholder_columns.md)。

## 变更范围

只更新两个原始列的逐源状态与裁决证据，不改变解析器、字段名、数据类型、单位、缓存、报告路由或数据日期逻辑。运行字段 `shareholder_change_date` 与 `shareholder_change_shares_wan` 原本已验证，本次只用 84,815 组精确同源对照加强原始列到运行字段的证据链；旧 `div_*` 标识继续退出破解和运行路径。

机器可读裁决：[`20261109_zhb_tipinfo_shareholder_columns.json`](20261109_zhb_tipinfo_shareholder_columns.json)，ID `zhb-tipinfo-shareholder-columns-20261109`。
