# TDX 多日涨跌幅回退来源补查

日期：2026-11-15。仅检查保留期内已有原始归档及当前代码，不运行采集。

## 结论

以下两个**完整嵌套身份**此前被历史字典登记为 TDX 行情字段；保留样本证明它们在唯一一次观测中是旧复合 accessor 从 ZHB 回退写入的值，应退出 TDX 上游字段破解队列：

| 完整来源身份 | 新状态 | 证据 |
|---|---|---|
| `TDX(双命名源)::quote_full.change_pct_1d` | `disproved` / `mixed_source_capture_passthrough` | 2026-10-15 的 20 条值与同记录 ZHB `full.change_pct_1d`、`stat.change_pct_1d` 均 20/20 完全相同。 |
| `TDX(双命名源)::quote_full.change_pct_2d` | `disproved` / `mixed_source_capture_passthrough` | 2026-10-15 的 20 条值与同记录 ZHB `full.change_pct_2d`、`stat.change_pct_2d` 均 20/20 完全相同。 |

这里的 `disproved` 只撤销“这两个完整路径是 TDX 行情适配器原始字段”的归属，不否定涨跌幅含义，也不表示旧 JSON 值错误。裸路径 `TDX(双命名源)::change_pct_1d` 与 `::change_pct_2d` 是各自独立的注册身份；本次没有相同路径样本，状态保持 `unverified`。

## 日期与逐行证据

2026-10-15 归档的 `data_date=20261015`、运行时间 `2026-10-15 16:24:54`。20 条记录的 `quote_raw` 均为空，TDX `as_of_date` 未记录，ZHB `as_of_date=20261014`。两项 TDX `quote_full` 值分别与 ZHB `full`、`stat` 同名路径逐值相同。ZHB 与 TDX 属于同一通达信来源族；此结果用于判定这次复合采集的值来自哪个采集通道，不作为独立来源碰撞或同日行情等价证据。

逐股数值、布尔命中和文件摘要见 [`../research/20261115_tdx_rolling_change_provenance.csv`](../research/20261115_tdx_rolling_change_provenance.csv)。CSV 规范 LF SHA-256：`469eb94703e345ff360d9b42f152e9b4c40aee9894c073d7a0c289c5de92af34`。所用归档的 SHA-256：

- `raw_tdx.json`: `107c6d7bc2acdef7c880d1a349be7bd3eb2512a3420d667cddd9c114ef1cb2f9`
- `raw_zhb.json`: `38eb8bb6df0959f9ef2ab206881a680bced4f8ebe6e5053e0326a84782da6b90`
- `meta.json`: `329844a06aafa37023a2f23ce3437aa8561b2e6e60e4345cbd4666162b4f1618`

## 代码血缘核查

- 历史 [`core/tdx_client.py::tdx_get_quote_full`](../../../core/tdx_client.py) 是 ZHB→TDX→腾讯复合 accessor，代码直接从 ZHB 读取 `change_pct_1d`、`change_pct_2d` 并写入同名输出键；这符合该归档 `quote_raw` 为空且值逐项与 ZHB 相同的证据。
- 当前 [`scripts/capture_tcp_collectors.py::collect_tdx`](../../../scripts/capture_tcp_collectors.py) 使用 `tdx_get_quote_raw()`，再由 [`scripts/capture_field_probe.py::_normalize_tdx_capture_quote`](../../../scripts/capture_field_probe.py) 规范化。该规范化不生成 `_1d`、`_2d` 两项，当前行情适配器也不提供它们。
- 原始来源参考证据保存在 `superseded_status_evidence` 和 `reference_evidence` 中；注册表未新增 `mappings`，未更改 ZHB 字段、裸 TDX 路径或原始归档。
