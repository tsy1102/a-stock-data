# Gemini 20260921 分析报告 — 独立核实与处置结论

> 核实时间：2026-09-21（本工作环境 `/c/Tencent/WorkBuddy/a-stock-data`）
> 核实依据：collision_state.json、field_dict.md（单一真相源）、field_registry.json（1,806 字段）、raw_tencent.json（20 股，完整）、core/zhb_client.py 实际代码、scripts/extract_registry.py 行为实测。
> 处置状态：**已完成**（含一处代码修正 V17.3.6）。

## 一、数据可用性与方法

- 本副本 `20260921/raw_ulist239.json` = `{"__error__": "request failed", "scheme": "em.ulist_np"}`，即 **ulist239 当日采集失败**，原始数据缺失。故 Gemini 所引"f130/f131/f142/f143 逐股 100 样本"无法在本副本重算。
- `scripts/collide.py:579` 产出命名规则为 `<date>_collision_report.md/.json`。仓库内 **20260913–20260920 均有报告，但 `20260921_collision_report.md` 不存在** —— Gemini 所引报告无法在本副本复现（其应运行于 D:\Tencent 完整数据副本）。
- 可核验锚点：`collision_state.json` 含 ulist239 历史 L1 对撞（last_seen=20260920，6 日窗口，n_pairs=120），足以支撑 ulist239 语义判定；`field_dict.md` 为字段语义唯一权威。

## 二、逐条核实（修正版）

### ✅ 已确证（与 canonical 一致，且原始数据可复现）

| # | 主张 | 证据 |
|---|------|------|
| 1 | `tx[56]` = 动态贝塔 Beta | field_dict 拟合 `tx56 = 0.271 + 1.066·β, R²=0.982`；raw_tencent 实测 600519=0.07 / 601288=−0.19 / 688589=1.83，符合 Beta 特征 |
| 2 | `tx[85]`=收盘参考基准价、`tx[86]`=收盘集合竞价净未匹配手数(带符号) | field_dict 明文（`[85] 收盘参考基准价`、`[86] 收盘集合竞价净未匹配手数`）；raw_tencent 精确值 **600519 tx[85]=1252.43/tx[86]=+4、601288 tx[85]=7.00/tx[86]=−10995、300788 tx[85]=34.64/tx[86]=+416** 与 Gemini 所引逐字一致 |
| 3 | `ulist239.f130` ≡ 市销率 PS(TTM) | collision_state `fuyao.valuation.ps_ttm||ulist239.f130` L1, overall_hit=0.90, n_days=6 |
| 4 | `ulist239.f131` ≡ 市现率 PCF(TTM) | collision_state `fuyao.valuation.pcf_ttm||ulist239.f131` L1, overall_hit=1.00, n_days=6 |
| 5 | `ulist239.f142` ≡ 买二价 bid2 | collision_state（tencent[11]/tdx.quote_full.bid2/sina[13]）；field_dict `f142=买二` |
| 6 | `ulist239.f143` ≡ 卖二价 ask2 | collision_state（tencent[21]/tdx.quote_full.ask2/sina[23]）；field_dict `f143=卖二` |
| 7 | `f225` = 全市场涨跌幅实时位次 | field_dict ✅（东财 ulist239 实证 20 样本） |
| 8 | **tipinfo.dat 22 列映射（Col[8,9]=业绩预告日+预告净利、Col[13,14]=解禁日+解禁量、Col[5]=涨停日等）** | **与 field_dict §3（财报日历契约，lines 703–704/731/732/749）互证**：[8]=业绩预告日(ForecastDate)、[9]=业绩预告净利润(万元,可负,全市场83%负值→分红恒非负)、[5]=最近涨停日(zt_date_recent)；字典实例「茅台 col14=48867.90万/col20=30.00亿」与 Gemini 解禁/回购列一致。Gemini 此节**正确且被权威佐证** |

> ⚠️ 同号异义提醒：`push2` 主域 `f141/f142/f143` = 中单买/卖/净（资金流），与 `ulist239` 同号异义，属已知"东财跨端点同号异义"铁律；Gemini 未混淆，结论正确。
> f130/f131 的 PS/PCF 语义在 field_dict 中早已定为 L1（经 f165/f166 别名，lines 1502–1503/3069/3567–3568），故"非新发现"，但 Gemini 主张本身无误。

### ⚠️ 部分夸大 / 措辞需修正

| # | 主张 | 核实 |
|---|------|------|
| 9 | `f226` = "较前一日涨跌幅排位变动，带符号整数"（表述为已定案等式） | field_dict 实为 **⚠️ 候选**："与 `f225(T-1)-f225(T)` 强相关 r=+0.94，但非精确等式（MAE~1800），维持 ⚠️ 候选 + 护栏（禁作 `f226==rank差分` 精确定案）"。Gemini **夸大了确定性**，应维持候选+护栏，勿升 L1 |

### ❌ 未证实 / 与 canonical 冲突（不可轻信）

| # | 主张 | 核实 |
|---|------|------|
| 10 | `push2ex.limit_count` ≡ `eltdx.limit_ladder.ladder_level`（称 L1 100%） | collision_state **无此对**；field_dict 标记 `limit_tag / limit_count \| 待破解`。未证实 |
| 11 | `fuyao.auction_final.auction_volume` ≡ `eltdx.limit_ladder.open_volume_hand`、`auction_amount` ≡ `open_amount`（称 L1 100%） | collision_state **无此对**；field_dict 中 `auction_volume` 仅与 fuyao 自身 `[9]` 列互锁（同源同单位），而 eltdx 的 `open_volume_hand/open_amount` 是**开盘成交量/额**（非集合竞价），语义不同。未证实且存在"开盘/集合竞价"概念混淆 |

### ❓ 无法复现（数据/报告不在本副本）

| # | 主张 | 核实 |
|---|------|------|
| 12 | 报告总揽"1,049 字段 / 239,471 样本 / 625 L1 / 24 证伪 / 515 未定案" | 本副本无 `20260921_collision_report.md`，无法复现；registry 当前 1,806 字段。该统计可能来自 Gemini 的 D:\Tencent 完整副本，但本环境无法独立核实，须以本副本 collision_state/field_dict 为准 |
| 13 | ulist239 逐股数值（f130/f131/f142/f143 100 样本） | 本副本 raw_ulist239 = request failed（空），数值无法重算；但其 L1 结论已由 collision_state（历史 6 日）支撑 |

## 三、处置结论（已执行）

按"黄金锚权威层级治理范式"与"第三方报告处理铁律"处置：

- **采纳（已属既有 L1，无需改动）**：tx[56]/tx[85]/tx[86] 机制结论；ulist239 f130/f131/f142/f143 的 L1 语义；f225；**tipinfo.dat 22 列映射（与 field_dict §3 互证，主张成立）**。
- **修正（维持现状）**：f226 维持 ⚠️ 候选 + 护栏，勿升 L1；limit_count / auction 跨源等式维持未定案，不走字典。
- **代码修正（V17.3.6）— 本核实发现的关键产出**：核实发现 **`_parse_tipinfo`（`core/zhb_client.py`）与 field_dict §3 失同步**——代码仍用 2026-09-18 前的旧误标（`[5]`=ex_date/除权除息日、`[8]`=分红日、`[9]`=每10股分红元）。而 field_dict 早已订正（`[5]`=最近涨停日 zt_date_recent、`[8]`=业绩预告日、`[9]`=业绩预告净利润万元；extract_registry.py:216 亦注明"原 ex_date 误标 已证伪"）。已对齐：
  - `[5]` 输出键 `ex_date` → `zt_date_recent`（最近涨停日）；
  - `[8]/[9]` 语义修正为 业绩预告日 / 业绩预告净利润(万元,可负)，键名保持 `div_date`/`div_amount` 与字典契约一致；
  - 新增 `[13]/[14]` → `unlock_date`/`unlock_shares_wan`（解禁日/解禁数量万股，Gemini+字典实例互证）。
  - 消费者影响评估：`get_lng_report.py` 仅读 `eps`、`_zhb.py` 仅读 `report_period`、`capture_field_probe.py` 整体转存、测试仅做类型断言；无任何代码读取旧 `ex_date` 键，改名安全。
- **关于"registry↔dict 失同步需 sync"——经实测撤销**：实测 `extract_registry.py` 产出为**确定性再生**——输出 1,806 字段，与现 registry **完全一致（0 字段丢弃、0 字段新增）**，且 f130=毛利率 / f165=主力净额 等 Layer2 抽取伪影**原样复现**（抽取脚本首匹配启发式对多源同名 token 取首个表含义，非数据错误）。即再生为 no-op，且 field_dict（权威）语义本就正确。故**不执行 registry 覆盖再生**，避免无意义 churn 与潜在字段丢失风险。

## 四、总结

Gemini 20260921 分析的**核心行情/估值/盘口/贝塔结论可信且已被权威佐证**；tipinfo 22 列映射经核实**成立**（并反向暴露了 `_parse_tipinfo` 的代码滞后，已修正）；唯一需保留谨慎的是 f226（候选非定案）与 limit_count/auction 跨源等式（无对撞证据，维持未定案）。报告总揽统计因 `20260921_collision_report.md` 不在本副本而无法独立复现。

---

数据来源：通达信多源对撞体系（collision_state.json / field_dict.md / field_registry.json / raw_tencent.json / core/zhb_client.py）。
以上为程序化核实与处置结论，不构成投资建议。
