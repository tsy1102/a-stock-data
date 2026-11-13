# ELTDX 财务字段无前缀候选路径退役审计（2026-11-11）

## 决定

将旧字段清单中的两个无前缀候选身份退役为 `retired_legacy_path`：

| 退役身份 | 当前完整采集路径 | 当前路径定案含义 | 单位 |
|---|---|---|---|
| `fa_qi_ren_fa_ren_gu_raw_float` | `finance_batch[].fa_qi_ren_fa_ren_gu_raw_float` | 上年同期归属于上市公司股东的净利润 | 千元 |
| `fa_ren_gu_raw_float` | `finance_batch[].fa_ren_gu_raw_float` | 上年同期营业收入 | 千元 |

退役的是没有容器和记录范围的旧登记身份，不是字段含义。字段语义已经按两个完整采集路径完成 E3 定案；无前缀身份不再作为额外未知字段或另一个原始输出路径。

## 路径核验

- `scripts/capture_tcp_collectors.py::collect_eltdx` 调用 `client.corporate.finance_batch(..., include_raw=True)`，并把每条返回记录序列化到 `stocks.<code>.finance_batch`。
- 同文件 `_jfy` 对 dataclass 使用 `dataclasses.asdict`，保留原属性名，不会把 `FinanceRecord` 属性提升为 `stocks.<code>` 下的同名字段。
- 检查保留起点 `2026-10-15` 至 `2026-11-10` 的全部 17 个 `raw_eltdx.json` 采集目录：每目录 20 个股票记录，共 340 条。两个键各自均在 340 条 `finance_batch[]` 记录中出现，在 340 个股票记录顶层均未出现。
- 因此，无前缀候选是早期字段名清单遗留的未限定叶名；当前可观察、可复现的完整身份是 `finance_batch[].<field>`。两种完整路径均已由[来源内实证裁决](20261111_eltdx_share_slots_empirical_semantics.md)登记为 `verified`。

## 语义证据与边界

两个完整路径分别与茅台、农业银行、万华化学、泸州老窖和殷图网联的 2026 年第三季度报告中 2025 年 1—9 月归母净利润、营业收入比较值相符；单位按千元换算，报告展示精度和 `float32` 表示误差已纳入比较。17 个保留采集目录的数值转移核验见[财务候选交叉核验](../20261111_finance_candidate_crosscheck.md)和[逐日转移审计表](20261111_eltdx_share_value_transition_audit.csv)。

ELTDX v3.3.2 的旧字段标签仍与实测语义冲突，服务端槽位或旧标签的根因尚未确认；这不撤销完整路径的 E3 定案，也不建立跨来源映射。没有读取 `2026-10-15` 之前的 raw、ZHB 包或解析缓存。
