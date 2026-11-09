# TDX `b_vol` / `s_vol` 定案

日期：2026-11-09
范围：仅确认 `TDX(双命名源)::b_vol` 和 `TDX(双命名源)::s_vol` 的来源内含义及证券类型单位；不新增跨源映射。

## 裁定

| 完整来源路径 | 含义 | 单位 |
|---|---|---|
| `TDX(双命名源)::b_vol` | 外盘成交量（主动买入侧）；板块指数时表示涨停家数 | 股票为手；板块指数为家数 |
| `TDX(双命名源)::s_vol` | 内盘成交量（主动卖出侧）；板块指数时表示跌停家数 | 股票为手；板块指数为家数 |

## 字段路径证据

- `core/eltdx_adapter.py` 将 ELTDX `QuoteSnapshot.outer_disc` 原样赋给 `b_vol`，将 `inside_dish` 原样赋给 `s_vol`。
- `core/tdx_client.py` 的 EasyTDX 回退路径调用 `get_security_quotes()`，保留其 `b_vol` / `s_vol` 字段；项目 TDX 原始报价捕获也保留原始行。
- `scripts/capture_field_probe.py::_normalize_tdx_capture_quote()` 把原始 `b_vol` / `s_vol` 原样复制到规范化行情对象，没有重新计算这两个值。
- ELTDX 与 EasyTDX 的上游字段文档用于核对客户端字段到项目字段的路径；字段语义以通达信官方资料为准。

## 官方语义证据

- 通达信量化平台 `get_market_snapshot_batch` 字段表定义 `Volume` 为“总手”、`Inside` 为“内盘”、`Outside` 为“外盘”；并注明板块指数中的 `Inside` / `Outside` 分别表示跌停 / 涨停家数。
- 通达信官方公式函数表定义 `SELLVOL` 为内盘（`DYNAINFO(22)`），`BUYVOL` 为外盘（`DYNAINFO(23)`）。这与 ELTDX 快照模型的 `inside_dish` / `outer_disc` 及项目赋值方向一致。
- 官方快照表没有单独给 `Inside` / `Outside` 指定量纲。量纲由证券类型和留存样本关系共同确认，故未把所有证券类型统一写成手。

来源：

- [通达信量化平台：批量获取实时行情快照](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html)
- [通达信公式系统：函数列表](https://help.tdx.com.cn/gspt/docs/markdown/redword/functionlist.html)
- [ELTDX `QuoteSnapshot` 字段说明](https://github.com/electkismet/eltdx/blob/main/docs/METHOD_REFERENCE.md)
- [EasyTDX `SecurityQuote` 字段说明](https://github.com/clong365/easy_tdx/blob/main/docs/field_mapping.md)

核验时间：2026-11-09。通达信量化页面直接打开请求超时；官方站点搜索索引返回了该页面完整的快照字段表。通达信公式函数表与两个客户端字段说明均已打开核对。客户端文档仅用于路径追踪，不单独作为提供方字段语义依据。

## 保留样本核对

仅读取 2026-10-15 起保留的本地样本。2026-10-16 至 2026-11-06 有 14 个采集日期，共 278 组同日 TDX / Tencent 有效股票记录。对比 TDX `b_vol + s_vol` 与 Tencent 原始总成交量字段：

| 股票代码前缀 | 配对数 | 总量关系 |
|---|---:|---|
| `000` | 68 | 68/68 精确相等 |
| `002` | 28 | 28/28 精确相等 |
| `300` | 28 | 28/28 精确相等 |
| `301` | 14 | 14/14 精确相等 |
| `600` | 56 | 56/56 精确相等 |
| `601` | 14 | 14/14 精确相等 |
| `920` | 28 | 28/28 精确相等 |
| `688` | 42 | TDX 两侧之和乘 100 后与 Tencent 总量吻合；Tencent 该板块以股计，TDX 样本以手计 |

此外，`quote_full.b_vol` / `quote_full.s_vol` 与对应 raw 字段在这 278 组记录中分别 278/278 完全相同，证明它们是同一 TDX 快照的包装别名。

## 边界与未决项

- 总量关系验证了单位与两侧合计，但不能单独证明单侧分类语义；分类语义依据通达信官方字段定义与项目适配器赋值链。
- TDX 与 Tencent 的内盘 / 外盘单侧数值不是逐值完全相等。两个采集源没有可确认的同一快照时间，且成交分类边界也可能不同，因此本次**不登记** `b_vol` / `s_vol` 与 Tencent 或东财单侧字段的映射。
- 注册表中的 `inside_volume` / `outside_volume` 是不同的未验证路径；它们出现在历史字段参考与 AxData 研究中，但没有找到当前适配器把这两个路径作为运行字段输出的证据。本次不将其当成 `b_vol` / `s_vol` 的别名，也不据历史单样本定案；保留给后续路径溯源。
- `quote_full.b_vol` / `quote_full.s_vol` 只在碰撞字段身份归一时并回各自已验证的 raw identity；其他 `quote_full` 路径保持独立。
