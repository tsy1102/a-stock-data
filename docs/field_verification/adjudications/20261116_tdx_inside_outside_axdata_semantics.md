# TDX `inside_volume` / `outside_volume` 语义核验

复核日期：2026-11-16。没有运行采集。本记录只核定历史字段参考中 AxData `stock_realtime_snapshot_tdx` 模型路径的字段语义；不声称它是当前项目采集路径，不确认其单位、wire 槽位或与 `s_vol` / `b_vol` 的数值等价，不建立跨源映射。

## 裁决

| 注册身份 | 字段含义 | 单位 | 状态范围 |
|---|---|---|---|
| `TDX(双命名源)::inside_volume` | 内盘量（指数场景为跌停家数；AxData TDX 快照模型路径，官方概念为 `Inside`） | 未注明 | 仅确认字段语义；不是当前项目输出或别名裁决 |
| `TDX(双命名源)::outside_volume` | 外盘量（指数场景为涨停家数；AxData TDX 快照模型路径，官方概念为 `Outside`） | 未注明 | 仅确认字段语义；不是当前项目输出或别名裁决 |

## 证据链

- 项目历史字段参考将两键列在 AxData 的 `stock_realtime_snapshot_tdx` 快照输出中，并曾把它们写入内盘/外盘的跨源汇总。本次以 AxData 固定提交 `f8ce3cee989717d79c7ad8f73b42f93c6dbd87e8` 复核：`QUOTE_FIELDS` 将两个完整输出键声明为整数型，中文说明分别为“内盘量”“外盘量”；`_parse_quote_row()` 将解析出的两个值写入对应模型属性。该仓库用于追踪第三方模型路径，不能替代通达信官方定义。
- 通达信官方[批量行情快照字段表](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html)将 `Inside` 定义为内盘、板块指数时为跌停家数，将 `Outside` 定义为外盘、板块指数时为涨停家数；未给出这两个字段的单位。通达信官方[公式函数表](https://help.tdx.com.cn/gspt/docs/markdown/redword/functionlist.html)又将 `SELLVOL` / `DYNAINFO(22)` 定义为内盘，将 `BUYVOL` / `DYNAINFO(23)` 定义为外盘。官方定义与 AxData 输出键及中文描述一致，足以确认这两个字段所表达的内外盘语义；不据此推断具体 wire 位置或单位。
- 当前项目代码没有 `stock_realtime_snapshot_tdx` 调用，也没有输出 `inside_volume` / `outside_volume`。当前 ELTDX 适配链将 `inside_dish` 输出为 `s_vol`、`outer_disc` 输出为 `b_vol`；这两条当前路径已有独立的 TDX 官方语义核验，不能反向证明 AxData 路径是相同字节槽或值别名。

## 保留期路径审计

按 [`capture_retention.py`](../../../scripts/capture_retention.py) 的保留起点 2026-10-15，递归检查保留期 26 个日期目录中的全部 561 个 `raw_*.json` 文件，而不是只扫描 `stocks` 子对象。每个归档文件单独记录目录日、`meta.data_date`、运行日、来源状态、来源 `as_of_date`（若存在）以及 raw/meta SHA-256，见[路径审计 CSV](../research/20261116_tdx_inside_outside_capture_path_audit.csv)。审计结果：`meta.data_date` 与目录日无冲突，`inside_volume` 和 `outside_volume` 的精确键出现次数均为 0。该结构审计只证明当前保留归档没有这两个键，不作行情值或来源日期碰撞证据。

当前采集链 `core/eltdx_adapter.py` 将 `QuoteSnapshot.inside_dish` / `outer_disc` 分别映射到 `s_vol` / `b_vol`。保留样本对这两条路径的既有契约结论见 [`20261109_tdx_trade_volume_sides.md`](20261109_tdx_trade_volume_sides.md)。本次不把 AxData 字段映射到这些路径，也不沿用旧参考文档中“TDX 全按手”或三源值等同的结论。

## 注册表范围

主字典更新两个精确身份的字段语义，单位保持空白。未新增 `mappings`，未修改采集、限流、缓存或来源路由。`inside_volume` / `outside_volume` 在项目原始采集中仍不存在；若将来接入 AxData 对应接口，须再用同一来源日期样本确认其单位、模型路径和值关系。
