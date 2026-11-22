# 2026-11-22 日期、ELTDX 与 Eastmoney 剩余来源路径裁决

复核日期：2026-11-22。本文记录本轮日期继承边界、6 条 ELTDX `limit_ladder` 路径及 Eastmoney clist 两个名称/代码路径的裁决。结构化登记见 [`20261122_remaining_source_contracts.json`](20261122_remaining_source_contracts.json)。

## 同源日期继承边界

同一源的日期锚只有在目标字段与锚字段来自同一 `capture_folder`、同一证券和同一交易日键时才可继承。碰撞会逐字段择优，因此仅匹配来源名、证券代码和交易日不够；重复采集时两字段可能来自不同快照。来源日期缺失时，日期锚可补充 `as_of_date`；已有来源日期、行时间戳或交易日键冲突时保持不合格。财报期和事件有效日仍由字段自身日期证明。

Ulist239 的已验证 `f297` 与同一行 `f124` 时间戳、当前目录数据日，在审计的 120 个非空 f297 行中 120/120 一致；行时间戳覆盖 180/180。当前样本没有日期资格变化，因为既有 f124 已覆盖这些行。完整逐行审计见 [`同源行日期锚审计`](../research/20261122_ulist_row_date_anchor_audit.md)及[CSV](../research/20261122_ulist_row_date_anchor_audit.csv)。

## ELTDX v3.3.2 `limit_ladder`

固定依赖版本的[连板天梯 Helper 文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/helpers/%E8%BF%9E%E6%9D%BF%E5%A4%A9%E6%A2%AF.md)说明 `limit_ladder()` 返回当前交易日组合行、`exchange` 和日期对齐元数据；[短线指标文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/helpers/%E7%9F%AD%E7%BA%BF%E6%8C%87%E6%A0%87.md)给出统计资源字段及比率公式。项目 `capture_tcp_collectors.py` 直接调用 `client.helpers.limit_ladder(codes=ecodes)`，保留 `global_helpers.limit_ladder.rows[*]`，再按完整证券代码复制到 `stocks.<code>.limit_ladder`。

保留期路径审计覆盖 12 个来源数据日、16 条有效行；所有 6 条路径均与同一全局 Helper 返回行逐值相同。`seal_prev_ratio` 与另一次独立的 `shortline` Helper 输出有 1/16 差异，因此没有把两个 ELTDX Helper 路径登记成逐值等价。字段裁决为来源内适配器契约，不是原生 TDX 协议释义，也没有跨源映射。

| 完整路径 | 定义 / 单位 | 边界 |
|---|---|---|
| `limit_ladder.alignment_status` | 统计资源日期与目标交易日对齐状态；枚举 | 只接受上游返回值，不重算状态 |
| `limit_ladder.exchange` | 证券所属交易所前缀代码；市场代码 | 当前样本只有 `sh` / `sz`，不外推其他取值 |
| `limit_ladder.limit_up_streak_days` | 统计文件日期记录的连续涨停天数；天 | 原样保留统计日期值，不自动加计目标日 |
| `limit_ladder.open_prev_seal_ratio` | 09:25 竞价金额 / 上一实际交易日统计封单金额 × 100；% | 保留原始符号；不据负值推断资金方向 |
| `limit_ladder.prev_seal_amount` | 上一实际交易日统计资源的封单金额原值；元 | `sz002242` 的 2026-11-18 值为 `-177681300.0`；负号方向未由上游解释，不改符号或当正向毛额 |
| `limit_ladder.seal_prev_ratio` | 当前买一金额 / 上一实际交易日统计封单金额；倍 | 保留分母符号；只有当前 `limit_status="sealed"` 时才用于封单强度解读 |

逐行原值、两种 Helper 对照结果和原始文件摘要见 [`20261122_eltdx_limit_ladder_six_path_audit.csv`](../research/20261122_eltdx_limit_ladder_six_path_audit.csv)。

## Eastmoney clist `f257` / `f258` / `f259`

东方财富[板块资金流官方页面随页脚本](https://data.eastmoney.com/newstatic/js/bkzj/list.js)将 `f257` 映射到 `zdname`、`f258` 映射到 `zdcode`；3 日与 5 日统计视图均请求两字段，`zdname` formatter 用同一行的 `zdcode` 生成证券资金流详情链接。随页脚本只说明字段绑定，不公开关联证券的选择/排序规则。因此只把它们定为板块统计行中的证券简称和代码，不命名为领涨股或资金流代表股。

保留期审计包括 9 个来源数据日、2,079 行和 494 个不同代码，`f257` 均为名称文本且 `f258` 均为六位代码。采集器现同时请求 `f257,f258,f259`；修正了旧文档将 f257 误列为 5 日金额、旧请求缺少代码字段的问题。`f259` 未在官方脚本的字段映射中出现，虽然保留样本有 0/1 值，也不因与代码前缀相关就推断为市场号，继续保留未知。

官方脚本本地核验副本 SHA-256：`A380CDC8A93515CAB3B55FA79300C0F3EC1F116384EBB1F5203284F145DD74D7`。逐行样本见 [`20261122_clist_f257_f258_f259_audit.csv`](../research/20261122_clist_f257_f258_f259_audit.csv)。

本裁决不建立跨源字段映射、不声明 clist 与其他排行源等价，也不改变采集频率或来源优先级。
