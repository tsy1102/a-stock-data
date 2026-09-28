# eltdx 字段重叠量化(B) 与 原始字节二次解码 PoC(D) — V17.2.15

> 配套：`core/eltdx_adapter.py`(TDX 主源切换)、`scripts/capture_field_probe.py::collect_eltdx`(第24源)、
> `docs/eltdx_smoke_report_20260915.md`(握手/返回 schema 实证)。
> 数据来源：通达信协议(eltdx 7709/7615 客户端)；以下为沙箱实证，不构成投资建议。

## B. eltdx 字段重叠与净新增量化

采集产物 `docs/field_verification/20260915/raw_eltdx.json`（20 只，4 个含 `__error__` 为北交所 920118/920508 快照解析失败）。

### 股票侧端点（20/20 成功覆盖）
`quote_snapshot` / `kline_day` / `finance_batch` / `f10_news` 各 20 只。

### 字段清单
- **股票侧命名字段：87 个**（含 eltdx snake_case 命名 + `*_raw` 原始字节字段）。
- 与 mootdx/easy_tdx 概念重叠（如 `last_price≈price`、`pre_close_price≈last_close`、`liu_tong_gu_ben_raw_float≈liutongguben`）占多数；纯命名层差异，值级可对撞归一。
- **净新增命名（样例）**：`buy_levels`/`sell_levels`(五档结构)、`close_delta_raw`/`open_price_milli` 等 milli 精度字段、`*_raw_float` 全套 0x0010 原始浮点、`finance_info_raw`/`record_hex`/`tail_raw` 原始字节。

### global_helpers（★全部为净新增，项目其他源均无）
| 端点 | 含义 | 项目现状 |
|---|---|---|
| `limit_ladder` | 连板天梯(几天几板) | 无 |
| `theme_strength_rank` | 题材强度排行 | 无 |
| `stock_theme_strength_rank` | 个股题材强度排行 | 无 |
| `realtime_rank` | 实时排行 | 无 |
| `volume_comparison` | 量比(成交量对比) | 部分(腾讯/东财有但口径不同) |
| `buy_sell_strength` | 买卖力道 | 无 |
| `market_stat_880005` | 880005 市场统计 | 东财有但 eltdx 直连主站 |

### 结论
- eltdx 作为**行情/财务 TDX 源**：与现有 tdx/zhb/tencent/sina 高度重叠（概念层），值级对撞后多为「已 verified，增量有限」。
- eltdx 的**独特价值**集中在 `global_helpers`（7 端点净新增）+ **原始字节二次解码**（D 节）——这两块才是「主源替换」真正值得投入的方向，且不替代东财主路径。

> 注：完整 cross-source `collide.py` 量化需先采集全部 24 源（本次仅采集 eltdx）。eltdx 侧字段清单已就绪，待全源采集后跑 `collide.py` 即得精确重叠率/净新增率。

## D. 原始字节二次解码 PoC

eltdx 每个模型都把**协议帧未解析部分原样交出**，可直接二次解码引出未命名字段。

### finance_info_raw（0x0010 财务块）
- 平安银行 `finance_info_raw` hex 长度 272 → **136 字节 → 34 个 4 字节小端 float 槽位，全部有效**。
- 标准 0x0010 块即 float 数组；eltdx 仅命名 42 个财务字段，原始块含完整 ~34+ 浮点槽位 + 日期/字符串区
  → 二次解码可引出 eltdx **未命名**的更多 0x0010 字段（如各类比率、细分科目）。

### kline `record_hex`
- 每条 K线 `record_hex` = 24 字节原始帧（去除头部）。`KlineBar` 已命名 22 字段，尾部字节可继续解析
  （如更细的买卖盘/持仓量子字段）。

### quote_snapshot `tail_raw` 等
- 快照原始字节字段：`time_raw` / `unknown_after_time_raw` / `amount_raw` / `unknown_after_outer_raw` /
  `open_amount_raw` / `tail_raw` —— 末段 `tail_raw` 为帧尾未解析区，可二次解码更多快照子字段。

### PoC 价值
对撞引擎除碰撞 eltdx 已命名字段外，还能对 `tail_raw`/`record_hex`/`finance_info_raw` 做**结构化二次解码**，
将「丰富度天花板」从「eltdx 解析出的命名子集」抬升到「7709 全帧字段」。这正是黄金锚范式（值级互证 + 中文命名回锚）可规模化的新战场。

## 待办（用户拍板后）
1. 全源采集 + `collide.py` 跑精确重叠/净新增率。
2. 对 `finance_info_raw` 落地 0x0010 全字段解码器（复用项目既有 0x0010 布局知识）。
3. 将 `global_helpers` 7 端点接入 `collect_eltdx` 并注册字段（净新增能力落地）。
