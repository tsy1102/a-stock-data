# 五大脚本数据充实分析（基于最新字典字段）

> 分析视角：专业股票分析员  
> 数据底座：统一层 `CanonicalStockData`（sc_schema.py，已归一化 **101 字段**）  
> 方法：静态扫描 5 个报告脚本的字段引用 + 章节结构 + 外部数据函数调用，与 canonical 契约做差集  
> 日期：2026-09-14

---

## 0. 数据底座现状（关键认知）

| 维度 | 事实 |
|---|---|
| canonical 字段总数 | 101（量价/估值/财务/资金流/区间涨跌/盘口/行业/元数据八大类） |
| 5 脚本平均覆盖 | med 39 / lng 40 / sht 43 / mak 16 / val 39（字段/101） |
| **完全零引用的字段** | **28 个**（见 §3） |
| 仅 1 个脚本引用的字段 | 26 个（见 §2 横向复用） |

**两个重要澄清（避免误判）**：

1. **"零引用"≠"数据没用上"**：`holder_count`/`net_assets`/`total_assets`/`roe_deduct_ttm`/`eps_deduct_ttm` 等被 med/lng/val 通过 helper 函数间接消费（`get_holder_structure`/`get_sina_balance_sheet`/`get_gross_margin_and_roe`）。它们的数据**已经在报告里**，只是没走 canonical 字段名 → 这是**轻量化机会**，不是新增数据。
2. **真正的"未开采富矿"**是那些连 helper 都没碰的字段：资金流**毛额**（主买/主卖额）、**盘口**（委比/买二卖二/内外盘/涨速）、**5日资金占比与数组**、**市场类型 sec_type**、**东财板块码 industry_code_push2**、**区间涨跌(60日/YTD)** 等。

---

## 1. 按脚本的充实建议

### 1.1 `get_med_report.py`（中线深度，17 章）— 当前 39/101

中线最该补的是**现金流质量**与**资金趋势**两个维度，胜率提升最明显。

| 优先级 | canonical 字段 | 充实到哪个章节 | 分析师逻辑 | 工作量 |
|---|---|---|---|---|
| **P0** | `ocf_ttm`（经营现金流 TTM） | 第四章「资产负债表财务健康度（排雷）」 | 净利润高但 OCF 长期为负 = 盈利质量差/赊销注水，是中线排雷核心指标。med 现只拉 Sina 资产负债表，canonical 已带 OCF，可零新增取数直接加"净利现金含量=ocf_ttm/net_profit" | 低（直接用 canonical） |
| **P0** | `eps_deduct_ttm`（扣非 EPS TTM） | 第三章「历史财务业绩兑现」 | 扣非 vs 归母差异大 = 非经常性损益撑业绩（卖资产/政府补贴），中线陷阱。canonical 已带 | 低 |
| **P1** | `roa`（资产回报率 TTM） | 第三章财务 | 与既有 ROE 互补：高 ROE 低 ROA = 高杠杆驱动，风险暴露不同 | 低 |
| **P1** | `fund_main_5d_pct`（近5日主力净占比%） | 第十一章「中线主力资金流向(60日基准)」 | 现有 60 日主力净额缺"占比"维度；净占比高且为正 = 资金真实介入，过滤对倒虚量 | 低 |
| **P1** | `ps_ttm` / `pcf_ttm` | 第二章「估值锚点」 | 与 PE/PB 构成跨估值体系，对亏损/重资产股更稳健的锚 | 低（val 已验证可用） |
| **P2** | `total_assets`/`net_assets`/`bps`（canonical） | 第四章排雷 | **轻量化**：现 med 用 `get_sina_balance_sheet` 重拉，canonical 已带这三个轻量字段，浅排雷可省一次 Sina 调用 | 低 |

### 1.2 `get_lng_report.py`（长线，13+ 章）— 当前 40/101

长线最该补**股东回报质量**与**资产结构**，强化"排雷"与"长效"。

| 优先级 | canonical 字段 | 充实到哪个章节 | 分析师逻辑 | 工作量 |
|---|---|---|---|---|
| **P0** | `undist_profit_ps`（每股未分配利润） | 第五章「长效股东回报」 | 高未分配利润+稳定分红 = 分红可持续性强；低未分配利润高分红 = 分光吃老本，长线隐患 | 低 |
| **P0** | `eps_deduct_ttm` | 第二章「跨期财务纵深」 | 长线看业绩连续性，扣非口径剔除噪音，比归母更干净 | 低 |
| **P1** | `ps_ttm` / `pcf_ttm` | 第一章「绝对估值锚点」 | 长线估值安全边际多元锚 | 低 |
| **P1** | `change_60d` / `change_ytd` | 第一章/仓位建议 | 现仅用 change_ytd；补 60 日回撤幅度辅助"长线回撤预算"仓位容忍度 | 低 |
| **P2** | `net_assets`/`total_assets`（canonical 轻量） | 第三章「现金流排雷」 | 替代部分 Sina 资产负债表调用，商誉/负债率浅排雷用 canonical 即可 | 低 |

### 1.3 `get_sht_report.py`（短线，17 章）— 当前 43/101（潜力最大）

短线**盘口与资金毛额**几乎全空白，而这是短线情绪最锋利的信号。

| 优先级 | canonical 字段 | 充实到哪个章节 | 分析师逻辑 | 工作量 |
|---|---|---|---|---|
| **P0** | `fund_main_buy`/`fund_main_sell`（主力买卖毛额） | 第七章「资金走向分析」 | **净额会被对倒掩盖**，主买占比 = fund_main_buy/(buy+sell) 才是真实做多力道；区分"真金白银买入"vs"对倒刷量" | 低（canonical 已带） |
| **P0** | `fund_super_buy`/`fund_super_sell`/`fund_large_buy`/`fund_large_sell` | 第七章 | 超大单/大单买卖毛额 → 机构 vs 游资行为拆解（游资做超大多对倒、机构主买占比高） | 低 |
| **P0** | `entrust_ratio`（委比%） | 第二章/十五章「短线情绪」 | 买卖盘挂单力量，盘前/盘中情绪前置指标 | 低 |
| **P1** | `b_vol`/`s_vol`（外盘/内盘，手） | 第七章/二章 | 内外盘比 = 主动买盘占比，与主力净额交叉验证；内盘持续>外盘=抛压重 | 低 |
| **P1** | `bid2`/`ask2`（买二/卖二价） | 二章盘口 | 盘口深度/支撑阻力位，配合现有 bid1_vol 封单分析 | 低 |
| **P1** | `rise_speed`（涨速 %/min） | 十五章「短线情绪与事件催化」 | 实时涨速突变 = 异动启动，比收盘涨跌幅早 N 分钟 | 低（实时路径已接） |
| **P2** | `fund_mid_buy`/`fund_mid_sell`（中单毛额） | 第七章 | 中单=散户/中户主力，与主力反向=散户接盘信号 | 低 |

> 注：sht 现用 `get_fund_flow_realtime`/`get_main_net_buy` 取净额，上述毛额 canonical 已归一化但 sht 未引用 → **直接改用 canonical 字段即可，无需新增采集**。

### 1.4 `get_mak_report.py`（异动及行业轮动扫描）— 当前 **16/101**（最欠充实）

mak 是**全市场扫描器**，但现在几乎只吃 ZHB 批量快照 + 涨停池/板块列表，**per-stock 的 canonical 衍生字段几乎没用**。这是充实空间最大的脚本。

| 优先级 | canonical 字段 | 充实到哪个章节 | 分析师逻辑 | 工作量 |
|---|---|---|---|---|
| **P0** | `change_60d` / `change_ytd` / `change_20d` | D「行业轮动强度扫描」/ E「TOP10 板块」 | 板块轮动强度 = 板块内个股区间涨幅中位数/离散度；现 mak 缺个股区间涨跌，只能用当日涨跌 → 用 60日/YTD 做"中期主线"识别，过滤一日游 | 中（需把 canonical per-stock 字段接入板块聚合） |
| **P0** | `sec_type`（市场类型枚举） | B「涨停池」/ 全扫描 | 主板/双创/北交所涨跌幅与流动性差异巨大，扫描应按 sec_type 分层，避免北交所 30% 干扰涨停统计 | 低 |
| **P0** | `turnover_pct` / `vol_ratio`（量比） | F「资金流验证：真金白银 vs 虚涨」 | 现 F 章只验资金流；加"放量纯度"= 高涨幅+高换手/高量比 = 真实资金推动，低量比虚涨剔除 | 低 |
| **P1** | `fund_main_5d_pct` + `fund_5d_array` | F 资金流验证 | 板块级 5 日主力净占比趋势，识别"资金持续流入的主线"而非单日脉冲 | 中 |
| **P1** | `industry_code_push2`（东财 BK 码） | C「板块-异动集中度」 | 现用 TDX 行业码聚合；加东财板块口径可对齐市场通用板块分类，提升板块归因可读性 | 低 |
| **P1** | `beta` | A「全市场情绪监测」 | 系统性风险暴露，高 beta 板块在情绪退潮时回撤更快，轮动择时加成 | 低 |
| **P2** | `holder_count`（经 helper） | C 板块筹码 | 板块内股东户数趋势 = 筹码沉淀/发散，长线主线确认 | 中 |

### 1.5 `get_val_report.py`（价值选股，25 策略）— 当前 39/101

val 字段利用已较充分（P1 刚补 #002/#009），仅指出可加的**质量/风险**维度。

| 优先级 | canonical 字段 | 充实到哪个策略 | 分析师逻辑 | 工作量 |
|---|---|---|---|---|
| **P1** | `eps_deduct_ttm` / `ocf_ttm` | 新增「业绩质量」策略或并入「盈利预期」 | 扣非 EPS 连续为正 + OCF>净利 = 高质量，过滤"纸面盈利"伪价值股 | 中（需横截面 rank 范式） |
| **P1** | `sec_type` | 所有选股预筛 | 选股范围按市场类型分层，避免北交所/科创板特殊涨跌幅污染信号 | 低 |
| **P2** | `roe_deduct_ttm`（canonical，现经 helper） | 并入「逆向白马」 | 扣非 ROE 稳定性比 ROE 更干净 | 低 |

---

## 2. 横向可复用字段（1 脚本用 → 其他脚本照搬）

| 字段 | 现仅被使用 | 建议横向充实 |
|---|---|---|
| `ps_ttm` / `pcf_ttm` | val | med 估值锚、lng 长线估值 |
| `roa` | val | med/lng 财务章节 |
| `gross_margin` / `net_profit_margin` | med | lng 跨期财务纵深 |
| `bps` | lng | med 资产负债表排雷（轻量化替代 Sina） |
| `change_ytd` | lng | val 年度动量、mak 轮动 |
| `ocf_ttm` / `revenue_ttm` | lng | med 排雷（净利现金含量） |
| `bid1_vol` / `bid_ask_net` | sht | mak 盘口异动（若 mak 加个股盘口） |
| `concepts` | sht | val 题材共振、mak 概念板块轮动 |
| `data_source` / `is_valid` | val | **所有脚本顶部加数据质量门禁**（见 §4） |

---

## 3. 完全零引用的 28 字段（富矿清单，按类别）

| 类别 | 字段 | 最佳归宿脚本 |
|---|---|---|
| 资金流毛额 | `fund_main_buy/sell`, `fund_super_buy/sell`, `fund_large_buy/sell`, `fund_mid_buy/sell` | **sht**（P0）、mak F |
| 资金流趋势 | `fund_main_5d_pct`, `fund_5d_array` | mak F、med 十一章 |
| 盘口/量价 | `b_vol`, `s_vol`, `entrust_ratio`, `bid2`, `ask2`, `rise_speed`, `volume_hand` | **sht**（P0/P1） |
| 区间涨跌 | `change_60d`（med/lng/mak 可用）、`change_10d` | mak 轮动、lng 回撤 |
| 财务（canonical 轻量） | `net_assets`, `revenue`, `eps_annual`, `eps_deduct_ttm` | med/lng（替代部分 Sina 调用） |
| 行业/元数据 | `industry_code_push2`, `sec_type`, `trading_periods`, `quote_date` | mak（轮动/分层） |
| 质量门禁 | `is_valid`, `field_sources`, `name_core` | **所有脚本** |

> 注：`holder_count` 虽在零引用清单，但 med/lng/val 经 `get_holder_structure` 间接消费，故未列；其**对 mak/val 选股仍是新增维度**（见 1.4/1.5）。

---

## 4. 轻量优先铁律下的两条通用建议

1. **数据质量门禁（零成本、全脚本受益）**：`is_valid` 与 `field_sources` 当前仅 val 引用。建议每个脚本在取到 `CanonicalStockData` 后立即用 `is_valid` 过滤 + 用 `field_sources.get("price")` 标注实时/兜底来源，避免"假 PE""缺失≠0"类问题在 med/lng/sht/mak 复现（这些脚本目前靠各自散落的 `缺失≠0` 注释手工防御）。
2. **优先消费 canonical，不重拉重源**：med/lng 的 `net_assets`/`total_assets`/`bps`/`roe_deduct_ttm` 已可由 canonical 直接取（轻量、ZHB/TDX 路径），浅排雷场景应优先用 canonical，把 `get_sina_balance_sheet` 等重源留给深度下钻——契合项目"轻量优先、不接 heavyweight"铁律。

---

## 5. 优先级汇总（按 ROI 排序）

- **P0（高价值+低工作量，建议立即做）**：
  1. sht 接入 `fund_*_buy/sell` 毛额 + `entrust_ratio`（短线盘口/资金力道，零新增取数）
  2. mak 接入 `change_60d/ytd` + `sec_type` + `turnover_pct/vol_ratio`（行业轮动强度，覆盖从 16→实质提升）
  3. med/lng 接入 `ocf_ttm` + `eps_deduct_ttm`（盈利质量排雷）
- **P1（中价值）**：`ps_ttm/pcf_ttm/roa` 横向复用；`fund_main_5d_pct`+`fund_5d_array` 资金趋势；`industry_code_push2` 板块对齐；`beta` 系统性。
- **P2（长尾）**：val 业绩质量策略；`holder_count` 进 val/mak 选股；`bid2/ask2/rise_speed` 深度盘口。

> 全部建议字段均已由统一层 `CanonicalStockData` 归一化（数据已取、已清洗、已 QC），**绝大多数无需新增采集**，仅需在脚本内改用/补充 canonical 字段引用即可——符合项目轻量优先原则。

数据来源：通达信/ZHB 统一层契约（`stock_common/sc_schema.py`）+ 5 脚本静态扫描。以上为数据分析视角的充实建议，不构成投资建议。
