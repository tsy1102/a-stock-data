# TDX 行情采集字段的派生值与回退来源审计

日期：2026-11-15。只核查保留期内已有 TDX 行情归档和代码调用链；未发起采集请求，也未将本次来源血缘检查当作跨源数值碰撞。

## 结论与精确身份

注册表身份是完整 `(source, code path)`。本次只纠正三个嵌套路径，并将一个嵌套路径标为项目派生输出；同名裸路径与它们是不同身份，不能共享结论。

| 完整身份 | 处置 | 证据结论 |
|---|---|---|
| `TDX(双命名源)::quote_full.change_pct` | `disproved` / `project_derived_capture_output` | 2026-10-16 至 2026-11-12 的 338 条可复算记录全部由 TDX raw `price`、`last_close` 经项目公式生成；2026-10-15 的 20 条旧值是 ZHB 回退例外。语义仍是涨跌幅，业务输出本身不表示错误，但该完整路径不是稳定的 TDX 上游原始字段。 |
| `TDX(双命名源)::quote_full.amount_1d` | `disproved` / `mixed_source_capture_passthrough` | 保留期内仅在 2026-10-15 出现 20 条；`quote_raw` 均为空，值与同记录 ZHB `full.amount_1d`、`stat2.amount_1d` 逐值相同。 |
| `TDX(双命名源)::quote_full.amount_2d` | `disproved` / `mixed_source_capture_passthrough` | 与上一条相同；逐值命中 ZHB `full.amount_2d`、`stat2.amount_2d`。 |
| `TDX(双命名源)::quote_full.pe_ttm` | `disproved` / `mixed_source_capture_passthrough` | 与上一条相同；逐值命中 ZHB `full.pe_ttm`、`stat.pe_ttm`。 |

裸身份 `TDX(双命名源)::change_pct`、`::amount_1d`、`::amount_2d`、`::pe_ttm` 保持原状态和待核队列。本次归档只为 `quote_full.*` 嵌套路径提供证据，不能用来改动无前缀身份。

## 证据范围与日期边界

按 `MIN_CAPTURE_DATE = 2026-10-15`，扫描 18 个日期目录、360 条股票记录，目标数据日为 2026-10-15 至 2026-11-12。完整逐行结果和目录级 raw/meta SHA-256 在 [`../research/20261115_tdx_quote_path_provenance.csv`](../research/20261115_tdx_quote_path_provenance.csv)，该 CSV 的规范 LF SHA-256 为 `abe7ef81516c1baec4efa027d530e73a27df3f77c53b02ea92577215f379714b`。

2026-10-15 的 20 条记录中，`quote_raw` 全为空；四个嵌套路径各出现 20 次，且分别与同记录 ZHB 路径 20/20 精确相同。该目录元数据为 `data_date=20261015`、`run_datetime=2026-10-15 16:24:54`，`sources.tdx.as_of_date` 缺失，`sources.zhb.as_of_date=20261014`。旧 `tdx_get_quote_full()` 是 ZHB→TDX→腾讯的复合回退 accessor；因此这些旧值只证明该次归档的回退血缘。ZHB 与 TDX 同属通达信来源族，且来源日期不同/缺失，故不构成独立来源等价或行情碰撞证据。

相关归档的 SHA-256：

- `raw_tdx.json`: `107c6d7bc2acdef7c880d1a349be7bd3eb2512a3420d667cddd9c114ef1cb2f9`
- `raw_zhb.json`: `38eb8bb6df0959f9ef2ab206881a680bced4f8ebe6e5053e0326a84782da6b90`
- `meta.json`: `329844a06aafa37023a2f23ce3437aa8561b2e6e60e4345cbd4666162b4f1618`

## `quote_full.change_pct` 复算

2026-10-16 至 2026-11-12 的 17 个保留目录中，有 338 条记录同时含 TDX raw `price`、`last_close` 与嵌套输出 `quote_full.change_pct`。按项目公式 `(price - last_close) / last_close * 100` 复算，338/338 完全相等，最大绝对误差为 0。2026-10-15 的 20 条不含 TDX raw 行且与 ZHB 对应路径一致，已排除在公式验证集外；两条缺少 `change_pct` 的稀疏记录也不参与比较。

此结果验证当前项目规范化步骤和输出语义，不代表 TDX 上游原始键，也不证明行情来源实际数据日。TDX 归档没有独立 `as_of_date`，故不据此开展跨源行情碰撞。

## 运行时路径

- [`scripts/capture_tcp_collectors.py::collect_tdx`](../../../scripts/capture_tcp_collectors.py) 保存 `tdx_get_quote_raw()` 的适配器响应为 `quote_raw`，然后用 [`scripts/capture_field_probe.py::_normalize_tdx_capture_quote`](../../../scripts/capture_field_probe.py) 构造 `quote_full`；这条采集路径不调用带 ZHB/Tencent 回退的 `tdx_get_quote_full()`。
- 规范化函数从 `price` 和 `last_close` 计算 `change_pct` 与 `change_amt`；不从 raw 响应生成 `amount_1d` 或 `amount_2d`。虽然代码会在 raw 键存在时透传 `pe_ttm`，当前 ELTDX 行情适配器和项目锁定的 easy-tdx `SecurityQuote` 契约均不提供该项；应以具体适配器返回结构为准。
- [`core/tdx_client.py::_get_verified_adapter`](../../../core/tdx_client.py) 配置 ELTDX 主用、easy-tdx 备用；[`core/eltdx_adapter.py::quotes`](../../../core/eltdx_adapter.py) 返回的行情键不含上述三个指标。easy-tdx 是客户端实现材料，不视为通达信官方字段定义：[项目锁定的 easy-tdx 仓库版本](https://github.com/yanwei99521/easy-tdx/tree/41e5637)。
- [`docs/field_verification/source_lineage.json`](../source_lineage.json) 记录这条客户端链。当前归档不记录单条调用实际命中哪个客户端，`tdx` 与 `eltdx` 属于同一 TDX 来源族，不计作两个独立来源。

注册表处置保留变更前的状态快照和历史 `reference_evidence`，并链接本审计与逐行 CSV；未创建跨源 `mappings`，未改动 ZHB 字段及四个同名裸路径。原始归档未被回写或重解释。
