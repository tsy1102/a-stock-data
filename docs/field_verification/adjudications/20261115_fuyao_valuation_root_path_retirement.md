# Fuyao 估值字段裸根路径身份退役（2026-11-15）

## 决定

将两个缺少 `valuation` 分组的旧登记身份退役，并将 `canonical` 指向当前采集记录中的完整来源路径：

| 旧身份 | 当前完整身份 |
|---|---|
| `同花顺-fuyao::pe_ttm` | `同花顺-fuyao::valuation.pe_ttm` |
| `同花顺-fuyao::pe_mrq` | `同花顺-fuyao::valuation.pe_mrq` |

此次只裁定采集路径身份。官方端点 `data.item[]` 的字段叶名仍是 `pe_ttm`、`pe_mrq`；项目的原始采集对象将整条 item 保存在每只股票的 `valuation` 分组中，所以它们不构成 `stocks.<代码>.pe_ttm` 或 `stocks.<代码>.pe_mrq` 两个独立根路径。既有嵌套路径的含义、单位和状态不变，不建立跨源映射。

## 接口与实现路径

- [Fuyao 官方估值接口文档](https://fuyao.aicubes.cn/llms-full.txt) 将接口列为 `GET /api/a-share/valuations/snapshot`，响应字段位于 `data.item[].pe_ttm` 与 `data.item[].pe_mrq`。文档说明 TTM 为最近连续 12 个月口径，MRQ 使用最近一个已披露报告期。
- 官方文档同时说明 `data.timestamp` 是本次响应指标元数据的最大有效时间，不能保证所有指标同步更新。
- 项目 [`stock_common/sc_fuyao.py`](../../../stock_common/sc_fuyao.py) 的 `_items` 只提取 `data.item`；`get_fuyao_valuation` 返回这些 item。采集器 [`scripts/capture_verified_collectors.py`](../../../scripts/capture_verified_collectors.py) 再将按股票代码索引的 item 写入 `stocks.<代码>.valuation`。
- 当前适配器没有将 `data.timestamp` 保存在估值字段记录中。因此，本次只用历史原始文件核查 JSON 路径，不把采集目录日或来源级 `as_of_date` 当成 PE 指标各自的有效日期，也不将这批值用于跨源碰撞。

## 保留样本路径审计

只检查保留边界 `20261015` 起、带有 `raw_fuyao.json` 的 18 个日目录：

`20261015`、`20261016`、`20261019`、`20261020`、`20261021`、`20261023`、`20261026`、`20261028`、`20261029`、`20261030`、`20261102`、`20261103`、`20261104`、`20261105`、`20261106`、`20261109`、`20261110`、`20261112`。

- 每个目录的 Fuyao 来源状态均为 `ok`，来源级 `as_of_date` 均与目录数据日相符；18 个来源日期互不重复，共检查 360 条股票记录。
- 逐记录检查键是否存在（包含值为 `null` 的键）：`stocks.<代码>.pe_ttm` 和 `stocks.<代码>.pe_mrq` 均为 0 条。
- `stocks.<代码>.valuation.pe_ttm` 与 `.pe_mrq` 各有 320 条非空记录，分别覆盖 16 个采集日。`20261015` 和 `20261026` 的 40 条股票字段观察没有估值 item，作为缺值路径记录保留，不用于语义判断。
- 逐代码、逐字段的键存在状态、原始值以及对应 `raw_fuyao.json`、`meta.json` 的 SHA-256 见 [`20261115_fuyao_valuation_path_inventory.csv`](../research/20261115_fuyao_valuation_path_inventory.csv)。
- 没有读取保留边界之前的 raw、ZHB 压缩包或解析缓存。

## 注册表处置边界

两个旧根身份设为 `disproved` / `retired_legacy_path`，保留原 `unverified` 状态快照，并指向同一来源下已验证的完整路径。这里的 `disproved` 表示旧采集路径身份不存在，不表示估值字段语义被证伪。嵌套路径仍由既有官方契约裁决单独管理。
