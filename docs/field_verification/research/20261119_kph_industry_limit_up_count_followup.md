# KPH `industry_limit_up_count`：2026-11-18 样本补充

复核时间：2026-11-19 05:04–05:16（北京时间）。精确字段身份：`开盘红::industry_limit_up_count`；对照字段：`开盘啦(kpl_limit_up_detail)::raw_columns.col_20`。

## 采集与日期资格

- 默认采集入口把目标数据日识别为 2026-11-18。已有完整收盘快照，因此幂等跳过主来源；当时未发起新增请求，ZHB 因早于 08:00 跳过。
- 为取得最新 KPH 来源日，先将原 `raw_kph.json` 和 `meta.json` 备份到 `.tmp/capture_retry/20261118/preopen_kph_20261119_0504/`，再运行 `capture_field_probe.py --date 20261118 --only kph`。KPH 请求于 2026-11-19 05:12:30 成功，返回 38 条，1 页且 `pagination.complete=true`，`as_of_date=2026-11-18`。
- 同日 KPL 样本来源日也是 2026-11-18，返回 41 条，`as_of_date=2026-11-18`。目标日、KPH 来源日和 KPL 来源日对齐；对比不使用目录日期替代来源日期。
- 这次只重采 KPH；没有刷新其他来源，也没有请求 ZHB。采集后以唯一标签 `preopen_kph_20261119` 运行了本地全局碰撞，报告完整生成并通过完整性核查，见下文。

## 三个来源日的逐股结果

| KPH 来源日 | KPH 行数 | KPL 行数 | 同股配对 | 行业码相同 | 计数相同 | KPH 值等于本次 KPH 返回集行业分组行数 |
|---|---:|---:|---:|---:|---:|---:|
| 2026-11-16 | 31 | 32 | 31 | 30/31 | 31/31 | 27/31 |
| 2026-11-17 | 34 | 37 | 34 | 31/34 | 14/34 | 29/34 |
| 2026-11-18 | 38 | 41 | 38 | 38/38 | 38/38 | 15/38 |
| **合计** | **103** | **110** | **103** | **99/103** | **83/103** | **71/103** |

KPL `col_20` 在这三日的完整返回集内均等于按 `col_19` 分组的记录数，共 110/110 条吻合。2026-11-18 的 38 条 KPH 股票均出现在同日 KPL 中，行业码和计数 38/38 完全一致；KPL 完整返回集的分组数为 41/41 条吻合。

最新日还有一个有区分力的现象：KPH 自己返回集中的 `801001` 只有 1 条记录，但字段值为 3；`801807` 返回 22 条，字段值为 23。KPL 对应行业组分别有 3 条和 23 条，且 KPH 字段值与 KPL `col_20` 相同。这支持“该计数使用的股票集合宽于当前 KPH 返回列表”的解释，但这仍是对样本的推断，不能替代 KPH 对计数范围的说明。

2026-11-17 的 20 个逐值不一致可分为两类：

- 17 组行业码相同但计数不同：`801001` 有 12 组为 KPH 12、KPL 13；`801218` 有 2 组为 2、3；`801807` 有 3 组为 5、4。
- 3 组行业码本身不同：一组 KPH `801807`/5 对 KPL `801218`/3；一组 KPH `801878`/2 对 KPL `801852`/1；一组 KPH `801878`/2 对 KPL `801001`/13。

因此 11 月 17 日不只是少数边界股票的舍入或缺失：多数反例是同一行业代码下的计数差异，另有 3 组行业归属差异。它们仍阻止把两字段认定为普遍逐值等价，但不推翻 KPH 字段可能表示“同行业涨停数”的来源内语义。

## 本轮碰撞报告

本轮碰撞使用最近 7 个交易日、行情截至 2026-11-18；读取 6 个采集目录、1,300 个字段和 384,092 个值。报告 [`20261119_collision_report.md`](../20261119/preopen_kph_20261119/20261119_collision_report.md) 完整生成；配套 JSON 的完整性核查通过，JSON SHA-256 为 `f32cc7f5c08472e1f61743146d1b2b57d58d72ded02d4778ee1e61b613ff3fc5`。

- `kph.industry_limit_up_count` 与 `kpl.raw_columns.col_20` 被列为 L4 存疑候选：103 组有效配对、3 个来源日，逐值命中率 80.58%，诊断用途；每日为 31/31、14/34、38/38。
- 该字段仍有方法候选（包括 KPL `col_20` 的相关/仿射关系和 `push2ex.limit_count` 的标签线索），但没有 L1 或 L1-C 定案候选。方法候选和相关性不能替代字段释义、范围及反例解释。
- 本轮没有更新 registry、主字典或映射；报告保留了最新 11 月 18 日一致性，也没有把它覆盖 11 月 17 日反例。

## 字段含义与跨源关系分开判断

Levistock 固定提交 `808d8187a6dd2a781dc51efeb1581f35d68e66c7` 将相同 KPH 接口的原始 `row[27]` 映射为 `industry_zt`，并释为“同行业涨停数”；项目适配器将相同位置映射为 `industry_limit_up_count`。[固定版本源码](https://github.com/fleetinglife/levistock/blob/808d8187a6dd2a781dc51efeb1581f35d68e66c7/levistock/stock/stock_daban_his_kph.py)、[固定版本字段表](https://github.com/fleetinglife/levistock/blob/808d8187a6dd2a781dc51efeb1581f35d68e66c7/README.md)。这是独立客户端的公开解析和命名线索，不是 KPH 官方接口契约。KPH [官方网站](https://www.kaipanhong.com/)确认了产品和提供方身份；本轮检索没有找到将官方页面字段标签精确对应到原始 `row[27]` 的定义。

因此目前有两项不同结论：

1. “同行业涨停数”是得到客户端映射及三日样本支持的**来源内候选语义**。但官方字段标签到原始路径的对应和计数集合仍缺提供方证据，`industry_limit_up_count` 继续保持 `unverified`；不把未解释的统计范围写成已验证定义。
2. `KPH industry_limit_up_count` 与 `KPL col_20` 不是已证实的普遍逐值等价关系：三日 103 组仅 83 组相同，20 个反例全部在 2026-11-17。11 月 18 日的 38/38 命中不能抹掉该反例，也不能建立跨源映射。

主注册表、主字典和 `mappings` 均未修改。后续若取得 KPH 提供方对原始字段及计数集合的正式定义，或能从官方页面独立核对同日完整行业计数，即可确认来源内语义及其适用范围；不需要再等待无目标的随机采集。若只审查跨源映射，则必须先解释 2026-11-17 的 20 个计数差异。

## 可复核材料

- 最新日逐股对照 CSV：[`20261119_kph_industry_limit_up_count_20261118.csv`](20261119_kph_industry_limit_up_count_20261118.csv)。包含全部 38 个同股配对、双方行业码/计数、各自返回集分组数及逐行比较标记；规范 LF SHA-256 `7844a3597296652d5c2c2b11c14c1a0b8d0464043511c65cd2bf7c1cfa414cf0`。
- 本地归档 KPH raw：`docs/field_verification/20261118/raw_kph.json`，SHA-256 `1384ce33f2c2e20758890fb88520aaccce9ca5b3b981821f346de7d9865294d7`。
- 本地归档 KPL raw：`docs/field_verification/20261118/raw_kpl.json`，SHA-256 `9e72fa239bda12f857fb7e1fc36a17732ee9aec77abf44d3f667b6b96a467d6b`。
- 来源元数据：`docs/field_verification/20261118/meta.json`，SHA-256 `50f007e09c124758cb08ce3aa3e902d3f835c91edcf59dec3a7b9e8b5218fed6`。
- 前两日核验：[`20261117_kph_industry_count_followup.md`](../adjudications/20261117_kph_industry_count_followup.md)、[`20261118_kph_industry_count_followup.md`](../adjudications/20261118_kph_industry_count_followup.md) 及 [`20261118_kph_industry_limit_up_count_samples.csv`](20261118_kph_industry_limit_up_count_samples.csv)。

## 后续候选复核（2026-11-19 16:25）

- 将 KPH `industry_limit_up_count` 与 KPL `raw_columns.col_20` 的直接等价候选审阅为 `rejected`。三日的 103 组日期合格配对中 20 组失配；11 月 17 日仅 14/34 相同，其中多数反例在行业码相同的情况下计数仍不同。更早的 11 个来源日、500 组样本也有 50 组差异。高相关和两日全匹配不足以抹去可重复的逐值反例。
- 将 KPH `industry_limit_up_count` 与东财 `push2ex.limit_count` 的标签候选审阅为 `rejected`：后者已验证为当前连续涨停板数（单位“板”），前者候选是同行业涨停数量（单位“家”）；共有 `limit/count` 词元不代表语义相同。
- 这两项只拒绝具体跨源关系，不判定 KPH 提供方身份，也不否认 KPH 字段的“同行业涨停数”候选释义。KPH 字段仍 `unverified`，各源分别保留采集，无跨源映射或停采决定。审阅事件见[候选决定文件](../adjudications/20261119_kph_candidate_review_decisions.json)。
