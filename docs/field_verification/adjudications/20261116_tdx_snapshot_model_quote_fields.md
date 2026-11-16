# TDX 实时快照模型行情字段语义核验

复核日期：2026-11-16。本记录处理 `TDX(双命名源)::last_price`、`pre_close`、`average_price`、`volume` 四个小写路径。它们在 AxData 的 `stock_realtime_snapshot_tdx` 字段清单中有同名模型输出；通达信官方快照文档提供相应行情概念的定义。

## 裁决范围

| 完整来源身份 | 字段语义 | 单位 | 裁决范围 |
|---|---|---|---|
| `TDX(双命名源)::last_price` | 最新价或最新值 | 未注明 | AxData TDX 实时快照模型字段语义 |
| `TDX(双命名源)::pre_close` | 前收盘价或上一期值 | 未注明 | AxData TDX 实时快照模型字段语义 |
| `TDX(双命名源)::average_price` | 均价；源端有值时返回 | 未注明 | AxData TDX 实时快照模型字段语义 |
| `TDX(双命名源)::volume` | 成交量，沿用源端行情单位 | 未注明 | AxData TDX 实时快照模型字段语义 |

字段语义标为已核实，但这不证明 AxData 的这条接口已由本项目调用，也不证明它的返回键对应通达信官方接口的 wire 字段。通达信官方字段名为 `Now`、`LastClose`、`Average`、`Volume`；AxData 模型名为小写路径。相同概念不构成代码路径映射或跨源数值等价。

## 证据

- 通达信官方[批量行情快照字段表](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html)将 `LastClose` 定义为前收盘价、`Now` 定义为现价、`Average` 定义为均价、`Volume` 定义为总手。除官方为 `Volume` 明确的总手口径外，该字段表没有给出价格字段单位。
- AxData 固定提交 `f8ce3cee989717d79c7ad8f73b42f93c6dbd87e8` 的[实时行情字段目录](https://github.com/electkismet/AxData/blob/f8ce3cee989717d79c7ad8f73b42f93c6dbd87e8/libs/axdata_core/axdata_core/sources/tdx_ext/catalog.py#L298-L320)将 `last_price`、`pre_close`、`average_price`、`volume` 列为报价模型输出，分别描述为最新价/值、前收/上期值、均价和按源端行情口径返回的成交量。[解析器](https://github.com/electkismet/AxData/blob/f8ce3cee989717d79c7ad8f73b42f93c6dbd87e8/libs/axdata_core/axdata_core/adapters/tdx_ext/client.py#L617-L681)将 TDX Ext 行情行中的 `close`、`pre_close`、`avg`、`vol` 解码到这些模型属性。
- 项目 AxData 字段逆向登记将这四个字段匹配到 `stock_realtime_snapshot_tdx`，但匹配类别仍是字段名候选。`source_lineage.json` 说明 AxData 是多提供方框架，项目当前只确认其短线接口走通达信；本次不把 AxData 的其他接口声明为当前采集来源或独立来源。

## 留存采集路径审计

按 `scripts/capture_retention.py` 的 2026-10-15 保留边界，复核了已有清单中的 561 个 `raw_*.json` 文件，并逐文件重算 SHA-256 与清单比对。审计表 [`20261116_tdx_quote_model_capture_path_audit.csv`](../research/20261116_tdx_quote_model_capture_path_audit.csv) 保留每个文件的归档目录、来源、状态、原始哈希及精确大小写键路径。

小写键没有出现在 18 个 `raw_tdx.json` 文件中。它们在其他来源中出现时属于不同的完整路径：`last_price` 在 ELTDX 报价快照/排行和 Fuyao 快照/榜单，`pre_close` 在 AxData 短线数据及 ELTDX 短线/梯队数据，`volume` 在 ELTDX 买卖档位、FTShare 和 Fuyao 快照；`average_price` 的小写精确键在保留期 raw 中没有出现。大小写不同的 `AVERAGE_PRICE` 不计作该字段。

因此，本记录不声称这四个字段是当前 TDX raw 输出，不把 `last_price` 映射到 `quote_snapshot.last_price`，不把 `pre_close` 映射到 `shortline.pre_close`，也不把 `volume` 映射到任何其他来源路径。没有来源日期值对照、单位证明或独立来源映射；上述单位均保持未注明。
