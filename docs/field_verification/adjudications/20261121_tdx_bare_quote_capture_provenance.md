# TDX 裸行情输出键的历史回退来源审计

日期：2026-11-21。只检查保留期内已有采集归档、Git 历史和当前调用链；未运行采集，也未发起联网请求。本次裁决的是字段来源归属，不是字段中文语义、单位或跨源等价关系。

## 结论

以下 registry 裸身份对应旧版 `tdx_get_quote_full()` 返回字典中的输出键。2026-10-15 的采集器把该字典原样放在 `stocks.<code>.quote_full` 下，因此留存 JSON 路径有包装层 `quote_full.` 前缀。这里不是把嵌套身份的裁决直接套到裸身份：本审计重新沿历史采集调用链把每个返回键映射到归档路径，并逐样本验证实际回退来源。

| registry 身份 | 历史归档路径 | 实测 ZHB 字段 | 来源结论 |
|---|---|---|---|
| `TDX(双命名源)::amount_1d` | `quote_full.amount_1d` | `stat2.amount_1d`（合并对象 `full.amount_1d`） | 20/20 同值；不是 TDX 原始响应字段 |
| `TDX(双命名源)::amount_2d` | `quote_full.amount_2d` | `stat2.amount_2d`（合并对象 `full.amount_2d`） | 20/20 同值；不是 TDX 原始响应字段 |
| `TDX(双命名源)::change_pct_1d` | `quote_full.change_pct_1d` | `stat.change_pct_1d`（合并对象 `full.change_pct_1d`） | 20/20 同值；不是 TDX 原始响应字段 |
| `TDX(双命名源)::change_pct_2d` | `quote_full.change_pct_2d` | `stat.change_pct_2d`（合并对象 `full.change_pct_2d`） | 20/20 同值；不是 TDX 原始响应字段 |
| `TDX(双命名源)::pe_ttm` | `quote_full.pe_ttm` | `stat.pe_ttm`（合并对象 `full.pe_ttm`） | 20/20 同值；不是 TDX 原始响应字段 |

五个字段各有 20 个样本，共 100 条字段观测；每项均为 20/20 精确匹配 ZHB 的合并对象和实际承载组件，且对应键在同股 `quote_raw` 中均不存在。逐行值、比较结果、路径和哈希见[结构化审计表](../research/20261121_tdx_bare_path_provenance.csv)，其规范 LF SHA-256 为 `227c47472177d9902e362dd56602410cf423e0d7206b360cda266d5427896c57`。

## 日期和证据边界

唯一出现这五个历史裸输出键的保留目录为 `20261015`。该目录的 `data_date=20261015`、`run_datetime=2026-10-15 16:24:54`；TDX `as_of_date` 未记录，ZHB `as_of_date=20261014`。因此本结果只用于确定这批历史输出的回退血缘，不能作为 10 月 15 日 TDX 行情、独立来源碰撞或 ZHB/TDX 同值映射证据。未读取保留起点之前的样本。

原始归档 SHA-256：

- `raw_tdx.json`: `107c6d7bc2acdef7c880d1a349be7bd3eb2512a3420d667cddd9c114ef1cb2f9`
- `raw_zhb.json`: `38eb8bb6df0959f9ef2ab206881a680bced4f8ebe6e5053e0326a84782da6b90`
- `meta.json`: `329844a06aafa37023a2f23ce3437aa8561b2e6e60e4345cbd4666162b4f1618`

## 调用链核对

- 2026-10-15 使用的旧采集器在 [提交 `b0f173b` 的父提交 `9daa054`](https://github.com/tsy1102/a-stock-data/tree/9daa054c5fea6e7b767395cea3aabbb6c89276b4)：`collect_tdx()` 调用 `tdx_get_quote_full(c)`，并将整个返回字典保存到 `quote_full`。10 月 19 日该采集器切换至来源专用采集；[当前 `collect_tdx()`](../../../scripts/capture_tcp_collectors.py) 调用 `tdx_get_quote_raw()`，避免将复合回退结果记作 TDX 原始响应。
- [`tdx_get_quote_full()`](../../../core/tdx_client.py) 先读取 `get_zhb_single_stock_data()`，再由 `_put_zhb(source_key, output_key)` 把 `change_pct_1d`、`change_pct_2d`、`amount_1d`、`amount_2d` 和 `pe_ttm` 放入返回字典；在进入后续 TDX/Tencent 回退前，这些同名返回键已可能由 ZHB 填入。
- [`get_zhb_single_stock_data()`](../../../stock_common/sc_datasource/_zhb.py) 将 `stat` 与 `stat2` 合并，后者覆盖同名键。归档中 `amount_1d/amount_2d` 的承载组件为 `stat2`，其余三项为 `stat`。
- 当前 TDX 专用采集保留原始响应与规范化结果分开；[`_EltdxAdapter.quotes()`](../../../core/eltdx_adapter.py) 明确组装的行情快照字段不含这五项。规范化器不会生成 `amount_1d`、`amount_2d`、`change_pct_1d` 或 `change_pct_2d`；它只会在原始响应实际含 `pe_ttm` 时透传该键，本次保留归档扫描未在任何 TDX `quote_raw` 中发现它。若未来 TDX 原始响应新增这些路径，应按新采集路径和新样本重新审查，不能把本审计当作永久接口约束。
- `tdx_get_quote_full()` 在 ZHB 缺值或不安全时仍可能继续使用后续 TDX/Tencent 回退；本次结论只归属 2026-10-15 这 20 条观察值，不声称该复合函数的所有时期或每次调用都由 ZHB 提供。

## 注册表处置

仅将上述五条精确身份从原 `unverified / aggregate_status_scope_unresolved` 改为 `disproved / mixed_source_capture_passthrough`，并在注册表保留原状态、原聚合范围及原参考证据快照。该 `disproved` 只表示这些历史复合 accessor 输出不能作为 TDX 上游原始字段证据；不否定字段本身的业务语义，不改变 ZHB 的字段身份，不建立或删除跨源映射。后续若 TDX 专用原始响应实际出现对应键，应按当时的精确接口路径和新证据重新登记审查。
