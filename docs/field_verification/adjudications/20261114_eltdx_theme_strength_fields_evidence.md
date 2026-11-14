# ELTDX 题材强度 Helper 字段来源契约定案

日期：2026-11-14
范围：`TDX-eltdx(适配层)` 的题材强度 Helper；只确认适配层输出，不宣称这些是原生通达信协议字段。

## 裁决

依据项目固定的 ELTDX v3.3.2 上游字段手册与实现，确认以下 8 个字段的来源内含义：

| 完整来源身份 | 规范名 | 定案含义 | 单位 |
| --- | --- | --- | --- |
| `TDX-eltdx(适配层)::topic_id` | `topic_id` | 题材 ID；由参与聚合股票的 F10 题材关系提供，可为空；ID 缺失时 Helper 回退到题材名称作为分组键 | — |
| `TDX-eltdx(适配层)::topic_name` | `topic_name` | 参与聚合股票的 F10 题材关系所提供的题材名称 | — |
| `TDX-eltdx(适配层)::limit_up_count` | `limit_up_count` | Helper 返回的目标交易日内，本次请求股票池中已封涨停且关联该题材的股票数；不含仅触板股票，也不是全市场计数 | 只 |
| `TDX-eltdx(适配层)::highest_ladder_level` | `highest_ladder_level` | Helper 返回的目标交易日内，本次请求股票池中该题材封板成分股的最高当前连板高度 | 板 |
| `TDX-eltdx(适配层)::lianban_count` | `lianban_count` | Helper 返回的目标交易日内，本次请求股票池中该题材封板成分股里当前连板高度不低于 2 板的股票数 | 只 |
| `TDX-eltdx(适配层)::total_seal_amount` | `total_seal_amount` | Helper 返回的目标交易日内，本次请求股票池中该题材封板成分股当前买一金额之和；单股金额缺失按 0，聚合值保留 6 位小数。共享题材股票会计入各自题材 | 元 |
| `TDX-eltdx(适配层)::leader_code` | `leader_code` | Helper 在目标交易日选出的该题材最高连板成分股完整证券代码；同高度时遵循连板天梯的封单金额降序、完整代码升序顺序 | — |
| `TDX-eltdx(适配层)::leader_ladder_level` | `leader_ladder_level` | Helper 目标交易日所选 leader 对应股票的当前连板高度 | 板 |

本次 8 条裁决不新增跨源映射，也不把题材强度 Helper 当作独立来源或黄金锚。

## 上游实现与精确路径

`requirements.txt` 固定 `eltdx==3.3.2`。采集器 `scripts/capture_tcp_collectors.py::collect_eltdx` 将本次股票代码池显式传给 `client.helpers.theme_strength_rank(codes=ecodes)` 和 `client.helpers.stock_theme_strength_rank(codes=ecodes)`。两条序列化路径为：

- `global_helpers.theme_strength_rank.rows[*].<field>`
- `global_helpers.stock_theme_strength_rank.rows[*].<field>`

ELTDX v3.3.2 中 `ThemeStrengthRow` 定义了这 8 个属性；`stock_theme_strength_rank()` 直接委托 `theme_strength_rank()`，两份采集结果是同一个 Helper 结果的别名，不是两份独立观测。字段身份限定为该 `ThemeStrengthRow` 的属性，不扩展到 ELTDX 中其他对象的同名属性。

`theme_strength_rank()` 先调用 `limit_ladder(codes, count=None)`，再读取每个入选证券的 `stock_topics(...).topics`，按 `topic_id`（缺失时按 `topic_name`）聚合。`limit_ladder` 默认只保留 `sealed`（已封板）股票，不包括仅 `touched`（触板）股票；项目调用传入约 20 只股票的采集池，所以计数和金额均限于请求池。题材可以交叉，同一股票可能被多个题材分别统计。

- `limit_up_count`：目标交易日每个已封板、具备该题材关系的请求池股票增加 1。
- `highest_ladder_level`：目标交易日取组内 `ladder_level` 最大值。
- `lianban_count`：目标交易日只对 `ladder_level >= 2` 的成员计数。
- `total_seal_amount`：累加目标交易日成员的 `seal_amount`；缺失按 0，结果 `round(..., 6)`。`seal_amount` 是当前买一价乘买一量，单位元；只有股票已封板时才解释为封单额。
- `leader_code` 与 `leader_ladder_level`：目标交易日选取最高 `ladder_level` 的成员。连板天梯先按高度降序、封单额降序、完整代码升序排序；Helper 只在发现更高高度时更换 leader，因此同高度时保留天梯排序靠前者。

上游引用：

- [ELTDX v3.3.2 `ThemeStrengthRow` 与 Helper 实现](https://github.com/electkismet/eltdx/blob/v3.3.2/src/eltdx/helpers/core.py)
- [ELTDX v3.3.2 字段手册：`StockTopics` / `StockTopic`](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md)
- [ELTDX v3.3.2 实时涨停梯队 Helper](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/helpers/%E8%BF%9E%E6%9D%BF%E5%A4%A9%E6%A2%AF.md)
- [ELTDX v3.3.2 短线指标：`ladder_level` / `seal_amount`](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/helpers/%E7%9F%AD%E7%BA%BF%E6%8C%87%E6%A0%87.md)

## 保留采集审计

审计脚本只读取 2026-10-15 起的 ELTDX `raw_*.json` 与对应 `meta.json`，未读取边界日前样本，也未联网补采。共有 18 组 raw/meta，目录范围 2026-10-15 至 2026-11-12；ELTDX 状态均为 `ok`，市场阶段均为 `closed`。题材强度返回 310 行，分布于 10 个非空目标数据日：

| 目标数据日 | 行数 | 目标数据日 | 行数 |
| --- | ---: | --- | ---: |
| 2026-10-16 | 40 | 2026-10-28 | 24 |
| 2026-10-20 | 28 | 2026-10-30 | 20 |
| 2026-10-21 | 28 | 2026-11-02 | 64 |
| 2026-10-23 | 26 | 2026-11-04 | 31 |
| 2026-10-26 | 27 | 2026-11-10 | 22 |

另有 8 个目标数据日返回空榜：2026-10-15、10-19、10-29、11-03、11-05、11-06、11-09、11-12。空榜不是字段缺失，也没有被计入 310 行字段覆盖率。

逐行核验结果：

- 8 个字段在 310/310 行均存在且非空。
- `limit_up_count` 为正且不超过每次请求的 20 只股票；`highest_ladder_level` 为正；`lianban_count` 在 0 与 `limit_up_count` 之间；`total_seal_amount` 非负；`leader_ladder_level == highest_ladder_level`；题材名称与 leader 代码非空。上述不变量均为 310/310 成立。
- 两个 Helper 路径的行和 `trade_date` 在 18/18 组 raw/meta 中一致；Helper `trade_date` 与目录 `meta.data_date` 一致。
- 运行自然日与目标数据日按交易日历区分。例如 2026-10-18 运行目录的数据日为 2026-10-16，这是非交易日运行时的正常归属。

**日期证据边界：**18/18 份 `meta.json` 均未记录 `source_as_of_dates.eltdx`。因此，上述样本只用于确认项目如何序列化该固定 Helper、目标日期接线、别名关系和输出不变量；不把它们算作 18 个独立来源日期，不用它们证明上游原始数据日期，也不把同一目标数据日重复采集计为独立样本。`raw_eltdx.json` 没有完整保存 Helper 内部逐股 F10 题材关系，故本审计未对聚合值做独立重算；计算语义以固定版本源码为准。

完整逐行记录（含每组 raw/meta SHA-256）见 [`research/20261114_eltdx_theme_strength_samples.csv`](../research/20261114_eltdx_theme_strength_samples.csv)，文件 SHA-256：`56d1574172ce7ebff6ed73fe61b6037c04aab5f09a3a71e83755a8835ce01253`。其中 2026-10-16 的首行样本为：题材 ID `2994`、名称“最近情绪指数”、请求池封板股数 2、最高 11 板、连板股数 1、总封单金额 909,464,448 元、领涨股 `sh600825`、领涨高度 11 板。

定案后按 `collide.py --all --date 20261114` 重建全历史本地报告，schema 5 完整性为 `complete`；窗口含 19 个有效交易日、1,309 个字段、1,356,938 条样本值，当前主攻未知目标 180 个。8 个已定案字段在 `candidate_triage.targets` 中均无匹配；碰撞得到 L1/L1-C 0 个、L4 32 个。Markdown 报告见 [`20261114_collision_report.md`](../20261114/post-eltdx-theme-strength-contract/20261114_collision_report.md)，完整 JSON SHA-256：`3708293083bc0b143c5a2f08044023dd451109a8f6112214efc0a293eaf7e91b`。L4 项仍是候选，未据此新增裁决。

## 本次未裁决的相邻字段

- `rank` 仍未定案：同一未限定注册身份还覆盖 `realtime_rank` 的排名序号；不同 Helper 的排名域不同，现有注册条目不能安全限定为题材排名。
- `trading_date` 仍未定案：在保留期 ELTDX raw 中没有该精确字段；不能从 `trade_date` 或运行日期代替推断。
