# 字段字典 × 5 大脚本 数据结构审计报告

> 审计日期：2026-09-10　｜　审计视角：资深股票/金融数据工程师
> 审计对象：`docs/field_dict.md`（5531 行）× 5 大报告脚本（val/mak/sht/med/lng，合计 9494 行）
> 权威契约基准：`stock_common/sc_schema.py::CanonicalStockData`（104 字段）
> 数据来源：腾讯行情 / 东方财富 push2·ulist / 同花顺 fuyao / 通达信 easy_tdx / ZHB
> **本文为数据结构技术审计，不构成任何投资建议。**

---

## 0. 审计方法

不依赖人工抽样，采用程序化全量比对：

1. 从 `CanonicalStockData` 解析出 **104 个契约字段**作为权威基准；
2. 对 5 个脚本全文匹配 `\.field` 与 `"field"` 两种消费形式，生成 **字段 × 脚本消费矩阵**；
3. 对零消费字段二次扫描 `core/`、`stock_common/`、`main.py` 内部层，区分「真死字段」与「仅内部消费」；
4. 反向核算字典对契约字段的覆盖率，并检索外挂取数源的字典收录情况。

---

## 1. 总体结论与优先级排序

### 核心判断

**当前结构的最大问题不是"字段不够"，而是"采、存、用"三层严重脱节**：契约层采集了 104 个字段，5 大脚本仅消费 64 个（61.5%），**40 个字段（38.5%）零消费**；与此同时，各脚本又通过 12+ 个外挂接口自行取数，这些外挂数据既不进契约、也不进字典，形成"契约内浪费、契约外失控"的双向失衡。

### 优先级排序（按对分析结果影响从高到低）

| 优先级 | 问题 | 影响面 | 性质 |
|--------|------|--------|------|
| **P0-1** | 资金流维度「采而不用 + 用错别名」：15 个 `fund_*` 字段全采集零消费，脚本却走旧别名 `main_net_buy_wan`（= `fund_main_today`/1e4，且**字典未收录**） | 全局 | 口径风险 + 分析维度缺失 |
| **P0-2** | `change_30d` 实为 `change_20d` 的错误副本（tdxstat.cfg 无 30 日列） | 全局 | **数据正确性** |
| **P0-3** | `is_valid` / `data_source` / `quote_date` 三个质量门禁字段**全仓零引用** | 全局 | 数据质量不可观测 |
| **P1-1** | 契约为「单时点快照」，**无时间序列维度**，历史分析全部外挂且不可复用 | 全局 | 架构缺口 |
| **P1-2** | `get_reports_async` 在 med(3) 与 lng(4) 重复采集 | 2 脚本 | 冗余 |
| **P1-3** | 字典覆盖率仅 **81.7%**，19 个契约字段未收录（含高频 `main_net_buy_wan`、`roa`、`beta`、`sec_type`） | 全局 | 文档滞后 |
| **P1-4** | 6 个真死字段仍占契约 | 全局 | 维护负担 |
| **P2-1** | 可派生字段重复存储（市值/市净率/市销率/EPS 等 8 组） | 全局 | 冗余 |
| **P2-2** | 单位与命名不统一（元/万元/亿元/手/股混用；`industry_code` 双份） | 全局 | 易错 |
| **P2-3** | 维度缺失：偿债/成长/营运能力、完整五档盘口、PEG、行业估值分位 | 全局 | 广度不足 |

---

## 2. 跨脚本共性问题

### 2.1 覆盖度比对

#### (A) 字典中遗漏未采集的高价值字段

以下字段**已进契约、已被内部层采集，但字典未收录**（共 19 个，覆盖率 81.7%）：

| 字段 | 业务含义 | 未收录风险 |
|------|----------|-----------|
| `main_net_buy_wan` | 主力净买额（万元） | **最高**——sht 主力资金流唯一入口，无字典定义 |
| `roa` / `roe_deduct_ttm` | 总资产收益率 / 扣非加权 ROE | 基本面核心，口径无据可依 |
| `beta` | 贝塔系数 | 风险因子，无口径说明（腾讯[56] 估计值） |
| `sec_type` | 市场类型枚举（主板2/创业板5/科创板32/北交所80） | 板块判定依赖，字典无枚举定义 |
| `fund_main_5d` / `fund_main_5d_pct` / `fund_5d_array` | 近 5 日主力净及其数组 | 趋势资金流，无文档 |
| `net_assets` | 净资产 | 与 `bps` 关系未定义 |
| `bid_ask_net` / `industry_code_push2` / `trading_periods` / `quote_date` / `time_anchor` / `is_valid` / `data_source` / `open_amount_wan` / `bid_volume_hand` / `main_net_buy_wan_1d` | — | — |

#### (B) 已废弃或已更名的字段

| 字段 | 状态判定 | 依据 |
|------|----------|------|
| `change_30d` | **应废弃**（错误副本） | `data_provider.py:1170-1172` 实锤：读 Col[18]=20 日值，与 `change_20d` 同值；真实 30 日需 TdxQuant `ZAFPre30` |
| `open_amount_wan` / `bid_volume_hand` | **真废弃** | 竞价族，全仓零引用 |
| `name_core` / `quote_date` | **真废弃** | 全仓零引用 |
| `fund_*_5d/10d`（f141-f146 误读） | 已删除 | 字典 518 行记录，5 日主力改由 f178 数组聚合 |

> ⚠️ **字典治理缺口**：全文检索「废弃 / 已停用 / DEPRECATED / 不再使用」**命中 0 处**。字典缺少「字段生命周期状态」列（在用/废弃/更名/待删），这是死字段得以长期驻留的根本原因。

#### (C) 脚本中字典不存在、属无效采集的字段

各脚本在统一入口之外的外挂取数，其中 4 类**字典完全未覆盖**：

| 外挂源 | 使用脚本 | 字典命中 | 风险 |
|--------|----------|----------|------|
| `get_fund_flow_120d`（120 日资金流） | sht | **0** | 口径无文档，不可复用 |
| `get_roe_trend`（ROE 趋势） | lng | **0** | 长线核心指标，无口径定义 |
| `get_market_abnormal_data` / 异动类 | mak | **0** | 异动判定标准未字典化 |
| `get_turnover_pct_async` | val | **0** | 与契约 `turnover_pct` 关系不明 |

### 2.2 冗余识别

#### (A) 同义重复（应合并）

| 冗余对 | 关系 | 处置建议 |
|--------|------|----------|
| `main_net_buy_wan` ↔ `fund_main_today` | **同源**：`data_provider.py:957→962` 证实 `main_net_buy_wan = fund_main_today / 1e4`（元→万元） | 契约保留 `fund_main_today`（元），`main_net_buy_wan` 降级为展示层换算，**禁止双写** |
| `change_30d` ↔ `change_20d` | 完全同值 | 删除 `change_30d` |
| `industry_code` ↔ `industry_code_push2` | 双份行业代码 | 明确单一权威（建议 `industry_code_push2`=f198），另一份标记废弃 |

#### (B) 可派生字段（应改为指标层计算，不占契约存储）

依据字典实证恒等式：

| 字段 | 派生式 | 依据 |
|------|--------|------|
| `fund_main_today` | = `fund_super_today` + `fund_large_today` | f137 = f140 + f143（169/169 精确） |
| `fund_main_buy` | = `fund_super_buy` + `fund_large_buy` | f135 = f138 + f141 |
| `fund_main_sell` | = `fund_super_sell` + `fund_large_sell` | f136 = f139 + f142 |
| `mcap_yi` | = `total_shares_wan` × `price` / 1e4 | 定义式 |
| `float_mcap_yi` | = `float_shares_wan` × `price` / 1e4 | 定义式 |
| `pb` | = `price` / `bps` | 定义式 |
| `ps_ttm` | = 市值 / `revenue_ttm` | 定义式 |
| `pcf_ttm` | = 市值 / `ocf_ttm` | 定义式 |
| `eps_annual` | = `net_profit_annual` / 总股本 | 定义式 |
| `roe` | = `net_profit` / `net_assets` | 近似 |

> ⚠️ 注意：派生式成立**不等于应删除存储**。f137 等由上游直供，直供值与派生值一致时保留直供更稳（避免除零/缺参）；建议**保留直供、同时校验恒等式**，不一致时告警——而非改为纯派生。

#### (C) 跨脚本重复采集

- **`get_reports_async`**：med(3 次) + lng(4 次) 重复调用研报接口 → 应提至统一层，按 `code` 缓存复用。
- **行情/基本面底座**：5 脚本均经 `get_canonical_stock_data` 统一入口，**此处无重复**（已享受统一缓存），是现有架构的正确部分，不应改动。

### 2.3 维度与广度评估

| 维度 | 现状 | 判定 | 建议 |
|------|------|------|------|
| **行情** | 价/开高低/昨收/额/涨跌幅/换手/量比/均价/内外盘/涨速/涨跌停价/买一量/买二卖二价/委比 | **不足** | 缺完整五档（买一到买五量价），短线打板与盘口深度分析受限；`volume_hand`、`s_vol/b_vol`、`rise_speed`、`bid2/ask2/entrust_ratio` 已采集却零消费 |
| **资金流** | 15 字段（四档净额 + 四档买卖毛额 + 5 日） | **严重失衡**：采集最全、消费为零 | 见 P0-1，最高优先级 |
| **估值** | PE(TTM/动/静)、PB、PS、PCF、股息率、BPS、总/流通市值 | **过度与不足并存** | PS/PCF 仅 val 用且可派生；缺 PEG、EV/EBITDA、行业估值分位 |
| **基本面** | ROE/ROA/扣非ROE/毛利率/净利率/净利润/EPS/营收/OCF/TTM族/总净资产 | **偏窄** | 缺**偿债能力**（资产负债率、流动比率）、**成长性**（营收/净利同比增速）、**营运能力**（周转率）；`revenue`、`roa` 零脚本消费 |
| **行业/概念** | 行业名/行业码(双份)/地域/市场类型/概念 | **利用不足** | `concepts` 仅 sht 用 2 次——题材是 A 股核心维度；行业排名靠 med 外挂 |
| **时间粒度** | 契约=单时点快照；历史靠外挂（sht 120 日资金流、lng ROE 趋势/历史高点、mak 指数K线/百度K线） | **架构缺口** | 契约无时间序列维度，历史数据不可复用、不进缓存、不进字典 |

### 2.4 结构优化（分层）

当前 `CanonicalStockData` 将**原始层、清洗层、指标层、元数据层**混装于单一 dataclass，导致职责不清。建议三层分离：

| 层 | 职责 | 归入字段示例 |
|----|------|-------------|
| **原始层 raw** | 各源原样落盘，保留 f 编号与源标识 | `push2_raw`、`tx_raw`、`tdx_raw`、`fuyao_raw` |
| **清洗层 canonical** | 统一命名、单位、类型（= 现行契约） | `price`、`fund_main_today`、`pe_ttm`… |
| **指标层 derived** | 由清洗层计算，不重复采集 | `mcap_yi`、`pb`、`ps_ttm`、`peg`、`change_*` 派生校验 |

**单位规范建议**：基础单位统一为「元 / 股」，展示层再换算万元、亿元、手。当前 `amount_wan`(万元)、`volume_hand`(手)、`mcap_yi`(亿元)、`fund_*`(元)、`main_net_buy_wan`(万元) 混用，是资金流双写别名得以长期共存的技术温床。

---

## 3. 分脚本问题清单 + 修改建议 + 预期收益

### 3.1 `get_val_report.py`（2442 行｜全市场选股）

**画像**：估值维度最全（PE 三口径 + PB + PS + PCF + 股息率），但资金流、基本面几乎不消费。

| # | 问题清单 | 具体修改建议 | 预期收益 |
|---|----------|--------------|----------|
| V1 | `ps_ttm`(4)、`pcf_ttm`(1) 为 fuyao 独有且可派生 | 改由 `mcap_yi`/`revenue_ttm`、`ocf_ttm` 派生，fuyao 仅作校验兜底 | 降低 fuyao 依赖（此前 fuyao 曾致 val 超时），提升稳定性 |
| V2 | 资金流全零消费，选股缺资金面确认 | 接入 `fund_main_5d` / `fund_main_5d_pct`（近 5 日主力净及占比）作趋势确认 | 选股信号从"纯估值"升级为"估值+资金"，降低价值陷阱 |
| V3 | `roa`、`revenue`、`ocf_ttm` 零消费 | 价值策略补 `roa` + `ocf_ttm`（盈利质量） | 识别"高 PE 但现金流差"的伪成长 |
| V4 | `code`(93)/`name`(80) 高频字符串操作 | 统一走 `name_core`（当前零消费），去除 ST/N/C 前缀噪声 | 选股池去重与展示一致性提升 |
| V5 | 外挂 `get_turnover_pct_async` 字典 0 命中 | 明确其与契约 `turnover_pct` 的关系：若同义则删除外挂 | 消除口径歧义 |

### 3.2 `get_mak_report.py`（1956 行｜异动扫描）

**画像**：**外挂最重**——12+ 独立取数源，契约字段消费最少（基本只有 code/name/change_pct/mcap_yi/industry_code）。

| # | 问题清单 | 具体修改建议 | 预期收益 |
|---|----------|--------------|----------|
| M1 | 严重外挂化：`market_abnormal_data`、`abnormal_announcements`、`strategic_announcements`、`baidu_kline`、`index_returns`、`index_kline_closes` 等均不在契约 | 新建**事件/异动层**（EventLayer），统一纳管并字典化，与 canonical 层解耦但共享缓存 | 异动口径可复用、可审计；新脚本不再重复造轮子 |
| M2 | 「异动」字典命中 0 | 在字典新增 §异动判定标准（涨跌幅/换手/量比/资金阈值） | 消除"异动"黑盒 |
| M3 | 几乎不消费基本面/资金流/估值 | 异动信号叠加 `fund_main_today`（主力异动）+ `concepts`（题材异动） | 异动从"价格异动"升级为"量价+资金+题材"多维异动 |
| M4 | 与 val/med 行业快照可能重复取数 | 复用统一层行业快照 | 减少重复网络请求 |

### 3.3 `get_sht_report.py`（2267 行｜短线）

**画像**：打板/盘口依赖最重，独有 `limit_up`(7)、`bid1_vol`(2)、`main_net_buy_hands`(5)、`prev_close`(6)。

| # | 问题清单 | 具体修改建议 | 预期收益 |
|---|----------|--------------|----------|
| S1 | **调整 C 刚实装的 `entrust_ratio`/`bid2`/`ask2` 零消费**（本轮字典 canonical 成真但脚本未用） | 接入委比 `entrust_ratio` 与买二/卖二价 `bid2/ask2`，强化封单与盘口深度判断 | 兑现 09-10 调整 C 的预期收益，否则该实装形同虚设 |
| S2 | 资金流走旧别名 `main_net_buy_wan`/`main_net_buy_hands`，未用四档 | 切换至 `fund_super_today`(超大单)/`fund_large_today`(大单) 分档，识别"游资 vs 机构" | 打板成功率与资金性质识别显著提升 |
| S3 | `get_fund_flow_120d` 外挂，字典 0 命中，不可复用 | 纳入时间序列层 + 字典化 | 120 日资金流可被其他脚本复用 |
| S4 | `concepts` 仅用 2 次——题材是短线核心 | 强化概念维度：概念热度、概念内排名 | 题材联动与板块效应识别 |
| S5 | `volume_hand` 零消费（用 `amount_wan` 近似） | 补量能维度：`volume_hand` + `vol_ratio` + `s_vol/b_vol`（内外盘） | 量价配合分析更准确 |

### 3.4 `get_med_report.py`（1424 行｜中线）

**画像**：基本面最聚焦（`gross_margin`(3)、`net_profit_margin`(1)、`ipo_price`(4)、`report_period`(2)），但成长性与偿债维度缺失。

| # | 问题清单 | 具体修改建议 | 预期收益 |
|---|----------|--------------|----------|
| D1 | `revenue`(营收)、`roa`、`ocf_ttm`、`revenue_ttm` 零消费 | 启用 `revenue` + `revenue_ttm` + `ocf_ttm`，构建**成长性 + 盈利质量**维度 | 中线选股从"静态盈利"升级为"成长+质量" |
| D2 | 缺成长性（营收/净利同比增速）与偿债能力 | 契约新增 `revenue_yoy`、`net_profit_yoy`、`debt_ratio`（需确认数据源） | 补齐基本面三大能力中的两项 |
| D3 | `get_reports_async`(3) 与 lng(4) 重复 | 提至统一层，按 code 缓存共享 | 消除重复网络请求与配额消耗 |
| D4 | `get_holder_change_async` 独有（股东变化） | 字典化并考虑纳入契约（筹码集中度是中线重要信号） | 股东户数/机构持仓变化可复用 |

### 3.5 `get_lng_report.py`（1405 行｜长线）

**画像**：长线维度最丰富（`eps`(5)、`dividend_yield`(10)、`float_mcap_yi`(8)、`change_ytd`(6)、`board`(4)、`roe_deduct_ttm`、`bps`(2)）。

| # | 问题清单 | 具体修改建议 | 预期收益 |
|---|----------|--------------|----------|
| L1 | `get_roe_trend` 外挂且字典 0 命中——长线核心（ROE 稳定性） | ROE 趋势纳入时间序列层 + 字典化 | 从"单点 ROE"升级为"ROE 连续性与稳定性"判断 |
| L2 | `get_historical_high`、`get_finance_info`(8) 外挂 | 同上，纳入时间序列/基本面层 | 历史估值分位可计算（长线择时关键） |
| L3 | `get_reports_async`(4) 与 med 重复 | 统一至共享层 | 同上 |
| L4 | 缺**股息连续性/分红历史**（长线核心） | 新增分红历史序列（需确认数据源） | 识别"高股息陷阱"（一次性分红） |
| L5 | `holder_count`、`total_assets`/`net_assets` 零消费 | 启用 `net_assets` 计算资产负债率（偿债能力） | 补齐基本面偿债维度 |

---

## 4. 待确认项（不臆测，需业务/数据源确认）

| # | 待确认问题 | 为何需要确认 |
|---|-----------|-------------|
| Q1 | `main_net_buy_wan` 与 `fund_main_today` 是否**应当合并**？`main_net_buy_hands`(手) 是 f137 换算还是独立接口？`main_net_buy_wan_1d`(T-1) 是否仍需保留？ | 三者字典均未收录，口径源头未文档化，贸然合并可能破坏 sht 既有信号 |
| Q2 | `change_30d` 是**直接删除**，还是改接 TdxQuant `ZAFPre30` 取真实 30 日？ | 取决于项目是否具备 TdxQuant 依赖；当前该字段是错误副本，若被启用将产生错误结论 |
| Q3 | 8 个外挂源（百度K线/研报/ROE趋势/历史高点/股东变化/行业排名/异动/120日资金流）是否为**长期依赖**？是否需纳入字典？ | 决定"补字典"还是"下线外挂"两条相反路径 |
| Q4 | `sec_type` 枚举（主板2/创业板5/科创板32/北交所80）是否覆盖 B股、ST、退市整理板？ | 字典未收录，板块判定边界不明 |
| Q5 | `bid_volume_hand` / `open_amount_wan`（竞价族）是否**彻底废弃**？有无历史报告依赖？ | 全仓零引用，但删除前需确认无离线报告回溯需求 |
| Q6 | `is_valid` 的**校验规则是否定义**？是否应启用为质量门禁？ | 全仓零引用，若启用需先定义规则，否则是空壳字段 |
| Q7 | `volume_hand`(手) 与 `amount_wan`(万元) 是否需统一到「股/元」基础单位？ | 涉及全契约单位改造，成本较高，需评估收益 |
| Q8 | fuyao 源 `ps_ttm`/`pcf_ttm` 是否可**稳定获取**？ | 此前 fuyao 曾出现 DNS 抖动致 val 超时，若不稳定则必须改派生 |
| Q9 | `concepts` 的**数据来源与更新频率**？是否值得强化为题材维度？ | 仅 sht 用 2 次，投入前需确认数据质量 |
| Q10 | `industry_code` 与 `industry_code_push2` **哪个是权威**？ | 双份并存，取舍需业务确认 |

---

## 5. 附：字段消费矩阵（节选关键结论）

- 契约字段总数：**104**
- 5 脚本零消费：**40（38.5%）**
  - 真死字段（脚本+内部层均零引用）：**6** → `name_core`、`open_amount_wan`、`bid_volume_hand`、`quote_date`、`data_source`、`is_valid`
  - 仅内部层消费：**34** → 含**全部 15 个 `fund_*` 资金流字段**
- 全脚本通用字段（5/5 消费）：`code`、`name`、`price`、`change_pct`、`change_5d`、`change_20d`、`mcap_yi`
- 字典对契约字段覆盖率：**81.7%**（19 个未收录）

---

*本报告基于程序化全量比对生成，所有结论均标注代码行级依据，未依赖抽样推测。*
*数据来源：腾讯行情 / 东方财富 push2·ulist / 同花顺 fuyao / 通达信 easy_tdx / ZHB。仅供技术审计参考，不构成投资建议。*

---

## 附录：实施记录（2026-09-10 落地）

### 审计方法修正（重要）

初版审计判定"6 个真死字段"时，采用 `\.field` 与 `"field"` 两种匹配模式，**漏掉了构造块中的裸关键字实参（`field=`）**。
复核后发现 `name_core`（31 处引用，由 `parse_stock_name()` 产出）、`quote_date`（有单测断言）、`data_source`（有单测断言）、`is_valid`（硬编码 True）**均为已填充而非未接入**。
据此修正删除范围，避免误删。（`name_core` 实为"已供未用"，已在契约注释中建议脚本启用。）

### 已实施改动

| 文件 | 改动 |
|------|------|
| `stock_common/sc_schema.py` | 删除 `change_30d` 字段定义 + FieldSpec 注册项 + 别名映射；删除 `open_amount_wan`/`bid_volume_hand` 误名别名；`is_valid` 升级为真实质量门禁（补规则说明）；补 `main_net_buy_wan` 派生关系（Q1）、行业码双体系澄清（Q10）、`name_core`/`quote_date` 说明 |
| `core/data_provider.py` | 删除 `change_30d` 采集列表项/计算/构造项；删除 2 个误名别名赋值；`is_valid` 由恒 `True` 改为 `bool(code_str) and (price>0 or prev_close>0)`；补 `main_net_buy_wan` 主从关系注释；**新增资金流四档恒等式运行时校验**（f137≈f140+f143，非阻断告警） |
| `docs/field_dict.md` | 新增 §13：字段生命周期状态规范（ACTIVE/AVAILABLE/DERIVED/DEPRECATED/REMOVED）+ 补齐 19 个未收录契约字段 + `sec_type` 枚举 + 已删除字段说明 + 8 类外挂源 + **Q1–Q10 决策记录** + 资金流恒等式依据 |

### 验证

- `py_compile`：2 个文件通过。
- 契约字段数：104 → **101**（删除 3 个），三字段确认不存在。
- 单元测试：**71 项**核心（schema/routing/cache）+ **131 项**定向回归（provider/schema/canonical/quote/field/fund/change/valid）**全部通过**，含资金流四档专项 `test_data_em_fund_flow_tiers.py`。
- 残留检查：`change_30d`/`open_amount_wan`/`bid_volume_hand` 仅存说明性注释，无真实代码引用。

### 未改动项（及理由）

- **时间序列层 / 事件层**（P1-1）：属架构级改造，需新建模块并处理 core↔stock_common 循环依赖约束，风险高于本次容错范围 → 已在 §13.4 给出纳管清单，列为专项。
- **`get_reports_async` 统一**（P1-2）：需引入共享缓存层，同上，列为专项；§13.4 已标注。
- **全局单位统一**（Q7）：改造面过大、与收益不匹配，暂以注释标注单位。
- **PEG / 偿债 / 成长性等新维度**：需先确认数据源，避免臆造，列为待确认后续项。
