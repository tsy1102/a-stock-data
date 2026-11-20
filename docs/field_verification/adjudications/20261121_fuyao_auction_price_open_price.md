# Fuyao 竞价价与开盘价身份更正（2026-11-21）

## 裁决

同花顺 Fuyao 官方集合竞价接口将 `data.item[].auction_price` 定义为“竞价价格”，另将 `data.item[].open_price` 定义为“开盘价”。两者是同一响应中的不同字段，不能因多数样本数值相同而认定同义。

- 定案 `同花顺-fuyao::auction_final.auction_price` 为竞价价格，单位留空（官方字段表未注明单位）。
- 定案 `同花顺-fuyao::auction_final.open_price` 为开盘价，单位留空。
- 退役错误的旧路径 `同花顺-fuyao::auction.auction_price`，指向当前运行路径 `auction_final.auction_price`。旧记录的“开盘价”释义及其与 `snapshot.open_price` 的错误等价关系不再生效；保留旧状态、元数据、参考证据和属性冲突快照供审计。
- 从注册表和活动跨源表撤回 5 组把 Fuyao 竞价价登记为开盘价同义项的映射。只撤回精确关系，不改动这些来源各自的开盘价释义，也不撤回其他行情字段关系。
- `同花顺-fuyao::auction_price` 仍保留为官方接口叶字段契约身份；它只表示竞价价格，不据此恢复已撤映射。`同花顺-fuyao::snapshot.open_price` 仍表示开盘价。
- 本裁决不涉及 KPH（开盘红）与 KPL（开盘啦）的来源归并；两者继续保持独立来源族。

结构化裁决见 [`20261121_fuyao_auction_price_open_price_source_contract.json`](20261121_fuyao_auction_price_open_price_source_contract.json)；精确映射撤回清单见 [`20261121_fuyao_auction_price_open_price_mapping_withdrawal.json`](20261121_fuyao_auction_price_open_price_mapping_withdrawal.json)。

## 官方字段定义与项目映射

Fuyao 官方 [A 股集合竞价快照接口](https://fuyao.aicubes.cn/docs/api-reference/auction/) 的响应示例在同一个 `data.item[]` 中返回 `auction_price` 和 `open_price`；返回字段表分别说明前者为“竞价价格”、后者为“开盘价”。该接口的 `data.timestamp` 是响应组装时间，不是竞价行情日期。

项目 [`stock_common/sc_fuyao.py`](../../../stock_common/sc_fuyao.py) 请求 `/api/a-share/auction/snapshot` 并返回原始响应信封；[`scripts/capture_verified_collectors.py`](../../../scripts/capture_verified_collectors.py) 从 `data.item` 复制记录，不重算这两个字段，并保存到 `stocks.<代码>.auction_final`。因此注册身份必须包含完整运行路径 `auction_final.auction_price` / `auction_final.open_price`，不能把竞价叶键当成 `snapshot.open_price`。

## 保留期路径与值审计

按 [`scripts/capture_retention.py`](../../../scripts/capture_retention.py) 的 `MIN_CAPTURE_DATE=2026-10-15`，仅检查 2026-10-15 至 2026-11-19 的 22 个目录，不读取边界前 raw、ZHB 压缩包或解析缓存。每个目录均核对目录名与 `meta.data_date` 一致；440 条 Fuyao 股票记录中：

- 旧 `stocks.<代码>.auction` 容器为 0 条；
- 当前 `stocks.<代码>.auction_final` 容器有 400 条；
- 所有 22 份竞价元数据均没有 `source_data_date`，且 `collision_eligible=false`。

唯一同时存在数值且 `auction_price != open_price` 的同项记录为 2026-10-20 的 `920508`：`auction_price=13.62`、`open_price=13.68`、`pre_close_price=13.62`、`auction_volume=0`。该响应没有来源数据日；此例只用于区分同一接口中的两个字段，不能作为日期合格的跨源碰撞样本，也不据此推断 Fuyao 的缺省/回退公式。逐股路径、原值、目录/元数据日期核对、来源日期资格及规范 LF 文件哈希见 [`20261121_fuyao_auction_price_open_price_path_audit.csv`](../research/20261121_fuyao_auction_price_open_price_path_audit.csv)。

## 撤回的活动映射

旧映射将下列端点与 Fuyao `auction_price` 记为 `same_number_same_meaning`，活动跨源表使用的目标路径为 `fuyao.auction_final.auction_price`。原登记证据和命中摘要原样存入结构化撤回清单；这里只删除活动关系，历史报告保持不变。

| 外部来源路径 | 旧 Fuyao 目标路径 | 旧关系 | 原命中摘要 |
|---|---|---|---|
| `sina[1]` | `auction_price` / `auction_final.auction_price` | `same_number_same_meaning` / 同义 | `20260924 对撞 L1等价(hub误伤复议)·hit=0.98·10d` |
| `tencent[5]` | `auction_price` / `auction_final.auction_price` | `same_number_same_meaning` / 同义 | `20260924 对撞 L1等价(hub误伤复议)·hit=0.98·10d` |
| `ulist239.f17` | `auction_price` / `auction_final.auction_price` | `same_number_same_meaning` / 同义 | `20260924 对撞 L1等价(hub误伤复议)·hit=0.98·9d` |
| `push2_full.f46` | `auction_price` / `auction_final.auction_price` | `same_number_same_meaning` / 同义 | `20260924 对撞 L1等价(hub误伤复议)·hit=0.98·7d` |
| `push2.f46` | `auction_price` / `auction_final.auction_price` | `same_number_same_meaning` / 同义 | `20260924 对撞 L1等价(hub误伤复议)·hit=0.98·8d` |

其中 `sina[1]`、`tencent[5]`、`ulist239.f17` 和 `push2.f46` 在逐源字典中均为开盘价；`push2_full.f46` 是旧跨源表所用别名。五条对应的注册表 shorthand 投影（目标 `fuyao::auction_price`）和跨源活动表行（目标 `fuyao.auction_final.auction_price`）均已精确移除。未更改外部字段自身释义，也未把同一提供方的两个接口登记为跨源映射。

后续碰撞仍可将 Fuyao `auction_final.auction_price` 作为“竞价价格”研究，但不得把它作为开盘价锚；新候选须按各来源实际日期、竞价阶段和字段语义重新建立证据。旧碰撞报告只作为当时报告保留，不再代表当前活动映射。
