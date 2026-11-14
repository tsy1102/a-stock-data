# Eastmoney 行情精度旧关系撤回记录

复核日期：2026-11-14。依据 [`报价精度来源内实证`](20261114_eastmoney_price_precision_evidence.md) 与其哈希锁定样本，修正当前字段状态和活动关系。历史碰撞报告保持只读。

## Push2 f152 状态修正

完整身份：`东财-push2(stock/get)::f152`。

| 属性 | 修正前 | 修正后 |
|---|---|---|
| `status` | `verified` | `candidate` |
| `status_resolution` | `matched` | `null` |
| `canonical` | `f152` | `f152` |
| `meaning` / `unit` | 空 / 空 | 空 / 空 |

旧 `verified` 仅由历史 `f152 ↔ ulist f1` 对撞状态支持；官方同日 B 股样本中 Push2 f152=2、Ulist f1=3，足以撤回该相等关系，但不能解释 Push2 f152 的业务含义。字段路径确实存在，故不将其标为 `disproved`。原 `reference_evidence` 和历史裁决文本均保留；当前状态通过本记录及来源内 `reference_evidence` 追溯。

Ulist `np/get::f152` 保持 `unverified`，语义仍为空。它在 140 条保留期 A 股样本和本次两个官方接口记录中均为 2；当前样本没有区分其候选含义。其旧 `status_resolution=aggregate_status_scope_unresolved` 来自 Push2 同码字段的旧已验证状态；该状态撤回后，Ulist f152 的 `status_resolution` 清为空值，表示普通待核，不再表示聚合范围冲突。

## 活动映射撤回

仅从当前 `field_registry.json.mappings` 及活动对齐表移除以下两项；原因是它们不能再代表有效的字段等价关系：

| 来源路径对 | 旧关系 | 证据 |
|---|---|---|
| `东财-ulist239::f1` → `东财-push2::f59` | `cross_number_diff_meaning` | 两字段已分别来源内定案为报价小数位数；旧 A 股全常量命中不足以证明跨源映射。当前不新增 `same_number_same_meaning` 映射。 |
| `东财-ulist239::f152` → `东财-push2::f59` | `cross_number_diff_meaning` | 同日 B 股样本 `ulist f152=2`、`stock/get f59=3`，旧关系失配；Ulist f152 语义仍未知。 |

历史矩阵记录中 `stock/get::f152 ↔ ulist::f1` 的 338/338 A 股命中也已在当前字典标记为撤回；该关系不是以上两条 `mappings` 中的一条。

## 保留内容

- `stock/get::f59` 与 `ulist.np/get::f1` 的来源内实证定案及其 E3 证据保留。
- 不把 `f152` 解释为价格精度、股本或其他项目；不把字段存在性错误标为语义证伪。
- 不改写历史碰撞报告，也不回读 2026-10-15 之前的 raw、ZHB 包或解析缓存。
