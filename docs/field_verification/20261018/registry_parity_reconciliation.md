# Registry parity 差异复核（2026-10-18）

> 本记录闭合历史来源基线与 `field_registry.json.source_fields` 之间的 35 条缺失配对。
> 原始快照只证明字段键在采集结果中出现；所有新增记录均保持 `unverified`，不据此猜测含义、单位或跨源等价。

## 计数

- 修复前：source_fields 2483 条；基线（5 项已审查范围排除 + 12 项 E3 补录）预期 2518 条；缺失 35，多余 0。
- 修复后候选：source_fields 2518 条；唯一字段 code 数 1878（修复前 1854）；缺失 0，多余 0。
- 投影字段数：修复后 `1878`；字段矩阵未改写。
- 原有 5 项范围处置、12 项 E3 补录和只读历史来源档案保持不变。

## 逐项原始采集证据

| 来源身份 | code | 捕获文件 | 原始路径 | 注册状态 |
|:--|:--|:--|:--|:--|
| TDX(双命名源) | `ask1_vol` | `docs/field_verification/20261016/raw_tdx.json` | `stocks.[*].quote_raw.ask1_vol` | `unverified` |
| 市场源(market_sources) | `DTJS` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_up_down.__raw_response__.list.DTJS` | `unverified` |
| 市场源(market_sources) | `Day` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_sentiment.__raw_response__.info.[*].Day` | `unverified` |
| 市场源(market_sources) | `SZJS` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_up_down.__raw_response__.list.SZJS` | `unverified` |
| 市场源(market_sources) | `XDJS` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_up_down.__raw_response__.list.XDJS` | `unverified` |
| 市场源(market_sources) | `ZTJS` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_up_down.__raw_response__.list.ZTJS` | `unverified` |
| 市场源(market_sources) | `big_order_300w_net` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].big_order_300w_net` | `unverified` |
| 市场源(market_sources) | `bl` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_up_down.__raw_response__.list.bl` | `unverified` |
| 市场源(market_sources) | `circulation_value` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].circulation_value` | `unverified` |
| 市场源(market_sources) | `col_02` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_02` | `unverified` |
| 市场源(market_sources) | `col_03` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_03` | `unverified` |
| 市场源(market_sources) | `col_04` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_04` | `unverified` |
| 市场源(market_sources) | `col_05` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_05` | `unverified` |
| 市场源(market_sources) | `col_06` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_06` | `unverified` |
| 市场源(market_sources) | `col_07` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_07` | `unverified` |
| 市场源(market_sources) | `col_08` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_08` | `unverified` |
| 市场源(market_sources) | `col_09` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_09` | `unverified` |
| 市场源(market_sources) | `col_10` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_10` | `unverified` |
| 市场源(market_sources) | `col_11` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_11` | `unverified` |
| 市场源(market_sources) | `col_12` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_12` | `unverified` |
| 市场源(market_sources) | `col_13` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_13` | `unverified` |
| 市场源(market_sources) | `col_14` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_14` | `unverified` |
| 市场源(market_sources) | `col_15` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_15` | `unverified` |
| 市场源(market_sources) | `col_16` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_16` | `unverified` |
| 市场源(market_sources) | `col_17` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_17` | `unverified` |
| 市场源(market_sources) | `col_18` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].raw_columns.col_18` | `unverified` |
| 市场源(market_sources) | `errcode` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_broken_ratio.__raw_response__.errcode` | `unverified` |
| 市场源(market_sources) | `errcode` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_sentiment.__raw_response__.errcode` | `unverified` |
| 市场源(market_sources) | `errcode` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_up_down.__raw_response__.errcode` | `unverified` |
| 市场源(market_sources) | `institution_add` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].institution_add` | `unverified` |
| 市场源(market_sources) | `pe_next` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].pe_next` | `unverified` |
| 市场源(market_sources) | `pe_now` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].pe_now` | `unverified` |
| 市场源(market_sources) | `speed` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].speed` | `unverified` |
| 市场源(market_sources) | `strength` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].strength` | `unverified` |
| 市场源(market_sources) | `total_value` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].total_value` | `unverified` |
| 市场源(market_sources) | `ttag` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_broken_ratio.__raw_response__.ttag` | `unverified` |
| 市场源(market_sources) | `ttag` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_sentiment.__raw_response__.ttag` | `unverified` |
| 市场源(market_sources) | `ttag` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_up_down.__raw_response__.ttag` | `unverified` |
| 市场源(market_sources) | `vol_ratio` | `docs/field_verification/20261016/raw_market_sources.json` | `kpl_plate_strength.[*].vol_ratio` | `unverified` |

## 修复边界

- TDX `ask1_vol` 从 `quote_raw` 原始行情键登记；同时存在的 `quote_full` 是归一化副本，不另算来源字段。
- `市场源(market_sources)` 的 34 个键均来自同一采集容器中的 KPL 数据集路径；容器仍按来源谱系标为聚合且不可作独立碰撞锚。
- `col_02` 至 `col_18` 只确认字段键和原始列路径，含义继续留空。
- `errcode`、`ttag` 在多个 KPL 响应中出现，证据逐路径保留；同一来源身份按一个 code 登记。
- `registry_parity.py` 的严格模式现在用完整预期集合比较计数；只有显式接受的差异清单才会在计数时按债务项调整。
