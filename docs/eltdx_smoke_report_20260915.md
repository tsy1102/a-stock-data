# eltdx 沙箱 Smoke 报告（第一步验证）

> 日期：2026-09-15｜授权动作：`pip install eltdx` + `eltdx-smoke`
> 目的：① 验证 2026-09 主站新式握手是否内置；② **探查返回 schema，定出「全字段破解」丰富度天花板**。
> 范围：仅沙箱验证，未改动项目任何代码（`_tdx_handshake_patch.py` 仍保留）。
> 数据来源：通达信协议（eltdx 7709/7615 客户端）；以下为实证，不构成投资建议。

---

## 一、安装与导入

- `pip install eltdx` → **eltdx 3.2.2** 成功装入系统 Python **3.12.10**（cp310-abi3 wheel，零运行时依赖，含 3.12）。
- `import eltdx` 正常，`__version__ = 3.2.2`。

## 二、2026-09 握手门控：✅ 内置，开箱可用

`TdxClient` 直连 TDX 主站取到**真实当前数据**，证明 Rust 握手已含 2026-09 新式单条随机 msg_id 握手，无需本项目 `_tdx_handshake_patch.py` 补丁：

| 接口 | 实测返回（真实值） |
|---|---|
| `quotes.get_snapshots(sz000001)` | last_price=**11.84**, pre_close=11.85, 内外盘 292848/331738 |
| `bars.get(sz000001, day, qfq)` | 最新 K线 2026-**09-09**, OHLC 11.76/11.70/11.79/11.69 |
| `bars.get(sh880005, day)` | 市场统计指数返回真实 KlineSeries（close=1252…），**适配器 `get_market_stat`→`bars.get("sh880005")` 可行** |
| `corporate.finance_batch(sz000001)` | 0x0010 财务真实返回（updated_date_raw=2026081x） |
| `F10Client.news(sz000001)` | 财联社 2026-09-14 新闻真实返回 |
| `helpers.limit_ladder()` | 连板天梯真实返回（见下 ShortlineIndicator） |

> 注：cold `TdxClient` 首次连接偏慢（整轮 smoke 约 6 分钟，疑为默认主站发现/握手重试）。**生产集成须 `client.transport.pin()` 固定主站 + 连接复用/连接池**，否则延迟不可接受。eltdx 自带 Rust 连接池，pin 后预期快。

## 三、返回 schema：命名解析 + 原始字节（丰富度未被封顶）★关键发现

eltdx 返回**命名字段**，但每个模型都同时暴露**原始协议字节**——这正是「全字段破解」的余量：

| 模型 | 字段数 | 命名示例 | 原始字节暴露 |
|---|---|---|---|
| `QuoteSnapshot` | 23 | last_price/pre_close/inside_dish/outer_disc… | **`tail_raw`(bytes)** = 未解析帧尾；另 `time_raw/amount_raw/unknown_*` 等 raw 变体 |
| `KlineBar` | 22 | open/close/high/low(含 `_milli`)/volume_raw/amount_raw… | **`record_hex`** = 整条 K线记录原始 hex |
| `FinanceRecord` | 42 | liu_tong_gu_ben/zong_zi_chan/jing_li_run/mei_gu_jing_zi_chan… | **`finance_info_raw`(bytes)** = 0x0010 完整财务块；另 40 个命名解析字段 |
| `ShortlineIndicator` | 41 | 连板/竞价/封单/开盘量比等（见下） | 无 raw（已全解析） |

**含义**：`tail_raw` / `record_hex` / `finance_info_raw` 把协议帧的「未解析尾巴」原样交出。对撞引擎除碰撞 eltdx 已命名字段外，还可对**原始字节做二次解码**，引出 eltdx 自身未命名的更多 f 字段——故丰富度上限 = 7709 帧全字段，而非 eltdx 解析出的子集。

## 四、净新增字段类（当前任何源都未供给）

1. **`ShortlineIndicator`（41 字段，连板天梯/短线指标）** — 真正的增量：
   `limit_status / limit_stat_days / limit_up_count_in_stat_days / limit_up_streak_days / year_limit_up_days / beta_60d / pe_ttm / free_float_shares / prev_amount / prev_seal_amount / prev2_seal_amount / prev_open_volume_hand / prev_open_amount / open_turnover_z / open_prev_amount_ratio / auction_prev_volume_ratio / open_prev_seal_ratio / seal_to_float_ratio / seal_prev_ratio / ladder_level / open_change_pct / open_volume_ratio / opening_rush / float_market_value / seal_amount / seal_to_amount_ratio / limit_board_text …`
   → 对应连板天梯、集合竞价过程、封单比、开盘量比、几天几板——**东财/同花顺当前源均无**。

2. **`FinanceRecord`（42 字段）** — 比项目现有 0x0010「37 财务字段」更全（多出 mei_gu_jing_zi_chan、bao_liu_2、更多日期解码等），可补登字典。

3. **`HelperApi` 净新增方法**（非 board/资金流/F10 等东财重叠类）：
   `auction_data`(竞价) / `volume_comparison`(成交对比) / `buy_sell_strength`(买卖力道) / `realtime_rank`(实时排名) / `theme_strength_rank` + `stock_theme_strength_rank`(题材强度排行) / `stock_topics` / `topic_stocks` / `shortline_indicators` / `stock_limit_ladder` / `daily_price_limits` / `daily_share_capital` / `daily_shares` …

## 五、文档订正（eltdx_analysis_20260915.md 有误）

原报告 §2.3/§3.2 写 `helpers.theme_strength()`，实测 **`HelperApi` 无此属性**。正确名为 **`theme_strength_rank` / `stock_theme_strength_rank`**（题材强度**排行**）。其余接口描述经 smoke 复核无误。待用户授权后订正该报告。

## 六、对「全字段破解 + 主源替换」可行性的最终判定

- **(1) 全字段记入主字典 + 采集脚本**：✅ 可行且丰富度充足。机制=加 `collect_eltdx` producer + `SOURCE_SCHEME["eltdx"]="eltdx"` + `field_registry.json` 第 24 源（level-4 粘滞继承放簇尾）；不动东财主路径。
- **(2) 全字段破解**：✅ 可行且余量超预期。命名类直接进 `collide.py` 值级对撞；`tail_raw/record_hex/finance_info_raw` 原始字节可二次解码引出更多 f 字段，中文命名回锚黄金锚。
- **(3) 主源替换**：⚠️ 仍审慎。实时行情维度 7709 帧字段数结构性 < 东财 push2(f1–f250)，且受主站握手/限流拖累；但**原始字节二次解码可能在某些字段类超过东财 push2 覆盖**——此点须实证。建议：eltdx 在「连板/竞价/封单/题材强度/成交对比/买卖力道」等独有类天然即该类主源；全量实时行情主源切换仍不建议，除非三维打分（字段重叠/对撞命中率/多日稳定性）实证占优。

## 七、下一步选项（待用户拍板，均未执行）

- A. 订正 `eltdx_analysis_20260915.md` 的 `theme_strength` 错误命名。
- B. 写 `collect_eltdx` producer（覆盖快照/K线/市场统计/财务/F10/Helpers+原始字节），登记第 24 源，跑一次真实采集 + `collide.py` 对撞，量化 eltdx 字段重叠与净新增。
- C. P0 替换 `core/tdx_client.py` 为 eltdx 适配器 + 移除 `_tdx_handshake_patch.py` + requirements 加 `eltdx>=3.2.2`（pin 主站/连接池解决延迟）。
- D. 原始字节二次解码 PoC（`tail_raw`/`record_hex` → 引出的未命名 f 字段）。

数据来源：通达信协议；以上为沙箱实证，不构成投资建议。
