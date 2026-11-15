# Fuyao 行情、估值与竞价裸路径复核（2026-11-15）

## 裁决

以下八个 Fuyao 登记项是旧的无分组叶路径。将其标记为 `disproved` / `retired_legacy_path`，并把 `canonical` 指向当前采集记录中的完整路径：

| 旧完整身份 | 当前完整身份 | 已登记含义与单位 |
|---|---|---|
| `同花顺-fuyao::auction_pct` | `同花顺-fuyao::auction_final.auction_pct` | 集合竞价涨跌幅，百分数原值（%） |
| `同花顺-fuyao::pb_mrq` | `同花顺-fuyao::valuation.pb_mrq` | 市净率 MRQ（倍） |
| `同花顺-fuyao::pcf_ttm` | `同花顺-fuyao::valuation.pcf_ttm` | 市现率 TTM（倍） |
| `同花顺-fuyao::price_change` | `同花顺-fuyao::snapshot.price_change` | 涨跌额（元） |
| `同花顺-fuyao::price_change_ratio_pct` | `同花顺-fuyao::snapshot.price_change_ratio_pct` | 涨跌幅（%） |
| `同花顺-fuyao::ps_ttm` | `同花顺-fuyao::valuation.ps_ttm` | 市销率 TTM（倍） |
| `同花顺-fuyao::turnover` | `同花顺-fuyao::snapshot.turnover` | 成交额（元） |
| `同花顺-fuyao::volume` | `同花顺-fuyao::snapshot.volume` | 成交量（股） |

`turnover` 和 `volume` 的旧登记项有跨来源聚合歧义；本裁决只处置 Fuyao 的精确来源路径，不更改其他来源的同名记录。除竞价字段外，当前完整路径的既有语义裁决和单位不变。裸路径退役只表示这些无分组路径不是当前 Fuyao 采集输出，不否定对应的嵌套字段。

## 官方契约与项目路径

Fuyao 官方接口文档（2026-11-15 在线核验）分别在行情快照 `GET /api/a-share/prices/snapshot`、估值快照 `GET /api/a-share/valuations/snapshot` 和集合竞价快照 `GET /api/a-share/auction/snapshot` 的 `data.item[]` 中列出上述字段。行情文档说明 `price_change` 是相对前收盘价的涨跌额、`price_change_ratio_pct` 是百分数值、`volume` 的单位为股、`turnover` 为货币金额；估值文档分别定义 `pb_mrq`、`ps_ttm`、`pcf_ttm` 为市净率 MRQ、市销率 TTM、市现率 TTM。竞价文档将 `auction_pct` 定义为竞价涨跌幅百分数值。

项目路径可以直接追到该响应结构：[`stock_common/sc_fuyao.py`](../../../stock_common/sc_fuyao.py) 的估值/行情适配器提取 `data.item`；竞价采集调用 `get_fuyao_auction_snapshot_envelope` 并由 `fuyao_auction_items` 提取项目。随后 [`scripts/capture_verified_collectors.py`](../../../scripts/capture_verified_collectors.py) 分别把项目记录保存在 `stocks.<代码>.snapshot`、`stocks.<代码>.valuation`、`stocks.<代码>.auction_final`。所以 registry 中的完整 code path 含对象分组前缀；不能把接口表的叶字段名单误当作股票记录根路径。

官方来源：

- [Fuyao 行情快照接口](https://fuyao.aicubes.cn/docs/api-reference/prices/)，字段表及响应示例也见[完整 API 文档](https://fuyao.aicubes.cn/llms-full.txt)。
- [Fuyao 估值接口](https://fuyao.aicubes.cn/docs/api-reference/valuations/)。
- [Fuyao 集合竞价接口](https://fuyao.aicubes.cn/docs/api-reference/auction/)。

## 保留样本路径审计

只读取保留边界 `20261015` 起的 Fuyao 采集目录：18 个目录、18 个不同的来源级 `as_of_date`，每个目录 20 条股票记录，共 360 条。逐记录检查根键和完整嵌套键是否存在（包括值为 `null` 的键），并保存原始值与 `raw_fuyao.json`、`meta.json` 的规范 LF SHA-256（由 `scripts/evidence_hash.py` 的 `canonical_text_file_sha256()` 计算，避免 LF/CRLF 转换造成摘要变化）：

- 八个旧裸根键在 360 条股票记录中均为 **0**。
- 七个已有语义裁决的完整 `snapshot.*` / `valuation.*` 路径各有 **320 条非空观察**。其余记录保留在逐行清单中，不据缺键推断字段语义。
- `auction_final.auction_pct` 有 **314 条非空观察**，分布在 18 个采集目录中的 16 个目录。314 条均可按四位小数复算为 `(auction_price / pre_close_price - 1) × 100`；这是同一竞价记录内的量纲/路径一致性检查，不是独立来源或独立日期证据。目录级 `as_of_date` 不作为竞价字段的来源日期。
- 竞价接口契约中的 `data.timestamp` 是响应组装时间，上游竞价行情时间只用于新鲜度判断。项目捕获元数据对竞价项记录 `source_data_date: null`、`collision_eligible: false`；因此这些竞价样本不用于跨源碰撞或日期敏感字段定案。当前定案仅确认官方含义、百分数单位和项目采集路径。

逐目录、逐股票、逐路径值、日期资格、竞价日期元数据及文件哈希见 [`research/20261115_fuyao_leaf_path_inventory.csv`](../research/20261115_fuyao_leaf_path_inventory.csv)。没有读取 `20261015` 之前的 raw、ZHB 压缩包或解析缓存。

## 注册表变更范围

- 旧无分组路径保留各自原 `status`、`status_resolution`、状态证据和参考证据快照，再改为 `disproved` / `retired_legacy_path`。每条记录都指向对应完整路径，不创建 `mappings`。
- 新增精确来源身份 `同花顺-fuyao::auction_final.auction_pct`，按 Fuyao 官方契约登记为“集合竞价涨跌幅，百分数原值”、单位 `%`、`verified_by_source_contract`。决定文件为 [`20261115_fuyao_auction_pct_source_contract.json`](20261115_fuyao_auction_pct_source_contract.json)。
- 竞价字段不作为已确认来源日期的日频样本，也不进入行情碰撞锚。若后续接口暴露可验证的上游竞价数据日期，再按来源日期规则评估其碰撞资格。
