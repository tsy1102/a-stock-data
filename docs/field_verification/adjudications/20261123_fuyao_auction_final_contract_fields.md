# Fuyao `auction_final` 官方字段契约定案（2026-11-23）

## 裁决

依据同花顺金融数据 API 当前官方文档和项目的实际采集路径，为 `同花顺-fuyao` 新登记并验证 9 个完整来源路径：`last_price`、`pre_close_price`、`auction_amount`、`auction_volume`、`auction_unmatched`、`auction_turnover_pct`、`auction_yesterday_ratio_pct`、`auction_volume_ratio` 和 `float_market_cap`。这些是 `stocks.<ticker>.auction_final` 下的字段；不把旧根路径或 `snapshot` 子接口的字段身份借给它们。

官方[集合竞价快照契约](https://fuyao.aicubes.cn/docs/api-reference/auction/)逐项列出 `data.item[]` 键及中文定义。项目 [`sc_fuyao.py`](../../../stock_common/sc_fuyao.py) 请求该端点；[`capture_verified_collectors.py`](../../../scripts/capture_verified_collectors.py) 从响应 `data.item[]` 取出记录，仅附加 `__source_meta__`，再将原字段保存在 `stocks.<代码>.auction_final`。因此上游键到完整运行路径可直接追溯，没有重命名或数值重算。

## 保留样本审计

审计仅使用保留边界 `2026-10-15` 之后、日期见证清单中 19 个完整 `final` 批次，共 380 条证券记录。逐字段的精确原值、键是否存在、raw 路径及 SHA-256 见[逐股审计 CSV](../research/20261123_fuyao_auction_contract_field_audit.csv)和[审计清单](../research/20261123_fuyao_auction_contract_field_audit.json)。CSV 规范 LF SHA-256：`0e0aa9c5d99b957691cbe803f1bf7959ca3e0569bb7e3f6e6696657d8b43a0f3`。

| 完整来源路径 | 官方定义 | 有数值 / 380 | 单位或未决边界 |
|---|---|---:|---|
| `auction_final.last_price` | 最新价 | 380 | 不将“最新价”改写为收盘价；接口未列单位 |
| `auction_final.pre_close_price` | 前收盘价 | 380 | 接口未列单位 |
| `auction_final.auction_amount` | 竞价成交额 | 373 | 7 条记录未返回该键；接口未列单位 |
| `auction_final.auction_volume` | 竞价成交量 | 379 | 1 条记录未返回该键；接口未列单位 |
| `auction_final.auction_unmatched` | 竞价未匹配量 | 372 | 8 条记录未返回该键；样本含负数和小数，接口未说明数值单位及正负方向口径 |
| `auction_final.auction_turnover_pct` | 集合竞价换手率，百分数原值 | 379 | 1 条记录未返回该键；单位 `%` |
| `auction_final.auction_yesterday_ratio_pct` | 竞价成交量相对昨日成交量的比例，百分数原值 | 378 | 2 条记录未返回该键；单位 `%` |
| `auction_final.auction_volume_ratio` | 竞价量比 | 380 | 官方未说明分母、统计窗口和计算公式；不补猜单位 |
| `auction_final.float_market_cap` | 流通市值 | 380 | 接口字段表未列单位 |

所有已返回值均为数值；表内缺失仅表示原始项未包含该键，不据此推断原因或补造数值。对 `auction_unmatched` 和 `auction_volume_ratio` 只确认官方字段标签，不将未说明的方向、尺度或计算公式写成事实。

批次日期另按[受哈希约束的日期见证](../research/20261123_fuyao_auction_batch_date_witness.md)确认；该日期证据证明这些字段的观测日，不替代字段语义，也不把响应组装时间戳当来源日期。此裁决不新增跨源 `mappings`；已有 ELTDX、ZHB 等数值相关候选仍须单独审阅关系与口径。

结构化决定见[来源契约裁决 JSON](20261123_fuyao_auction_final_contract_fields.json)。
