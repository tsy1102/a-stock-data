# 主字典命名一致性审计（Naming Consistency Audit）

> 触发：用户 2026-09-01 提问——「不同源相同字段因标注语言差异被理解为不同字段，已设命名规则，但主字典是否做过完整系统核查？是否还有其他类似情况？是否该按命名规则对整个主字典排查？」
> 方法：以 §12.8.12e **规范字段注册表**（canonical registry，跨源唯一语义名）为唯一裁决基准，逐语义族（PE / ROE / EPS / 市值 / 量额 / 换手率 / 资金流四档 / 营收 / BPS / 振幅 / 委比委差 / 封单 / 涨停价 / Beta / 52周 / 行业概念 / 上市日）扫描 `docs/field_dict.md` 全文，比对「源私有别名 vs 规范名」「旧标签 vs fuyao 2026-08-31 实锤」。
> 结论：**此前未做过完整系统核查。** 发现 5 类实质性问题（含 2 处与 fuyao 实锤直接矛盾的残留错误），已全部订正；注册表缺口（~25 个日常字段未入库）已补全，§12.4 规范名列已并入注册表。

---

## 一、结论摘要

| 项 | 结论 |
|:---|:---|
| 是否做过完整系统核查 | **否**。本次为首次按命名规则的全量排查 |
| 是否还有其他类似情况 | **是**，共 5 类（见下），其中 2 处是直接违背 fuyao 实锤的残留错误 |
| 已订正 | 5 处（E1–E5），均落盘 `field_dict.md` |
| 注册表缺口 | 已补 ~25 行，§12.8.12e 现为跨源唯一语义名总表 |
| 命名陷阱范式 | f184 口径分叉、snapshot.turnover=成交额 —— 本项目「同值异名/同名异义」的标准答案 |

---

## 二、已订正的实质性问题（E1–E5）

### E1 ❌ 残留过时 PE 标签（§12.3.1 汇总表，line 1572）
- **原文**：`动态PE | f162 | f9` —— 声称 f162=动态PE。
- **实锤**：2026-08-31 fuyao 三方验证 `f162=pe_mrq`（静态/MRQ），真动态PE 是 `f163`。
- **订正**：改为 `静态PE(MRQ) | f162 | f9`，并标注「f162=pe_mrq 非动态PE」。
- **性质**：与现行实锤直接矛盾，属 V17.0.16→V17.0.20 同类翻车的残留。

### E2 ❌ 开盘啦 W8 跨源 PE 映射颠倒（§12.21.1，lines 3806–3808）
- **原文**：`[60] 动态PE → pe_dynamic(f162)`、`[61] PE(TTM) → pe_ttm(f163)`、`[62] 静态PE → pe_static`。
- **问题**：沿用 2026-08-06 快照旧约定（f162=动态/f163=TTM），与注册表 f162=MRQ/f163=动态/f164=TTM 颠倒。
- **订正**：映射列改为 `f163 / f164 / f162`，并加 2026-08-31 订正说明。开盘啦自身语义标签（动态/TTM/静态）保留，仅修正跨源 fN 参照。

### E3 ❌ 注册表 tx[65]/tx[66] ROE/ROA 双重归属错误（§12.8.12e，rows 2525–2527）
- **原文**：
  - `roe_weighted_ttm`(TTM) ← 腾讯 `[65]`
  - `roe_deduct_weighted`(最新报告期) ← 腾讯 `[66]`
  - `roa`(最新报告期) ← 腾讯 `[66]`
- **问题**：tx[65] 在 §12.1 line 1326 与 fuyao 对撞（line 2555）均证实 = `roe_weighted`（最新报告期，披露日跳变天然实验），**非 TTM**；tx[66] 在 §12.1 line 1327 / V17.0.5 实锤 = **ROA**（招行 1.12 精确），被同时错误挂到「扣非加权ROE」与「ROA」两行（双重归属）。
- **订正**：
  - `roe_weighted`(最新报告期) 加腾讯 `[65]`；
  - `roe_weighted_ttm`(TTM) 腾讯列清空，注「腾讯无 TTM ROE 单槽，tx[65] 为最新报告期口径」；
  - `roe_deduct_weighted`(最新报告期) 腾讯列清空，注「腾讯无单槽，须由扣非净利/净资产推导」；
  - `roa`(最新报告期) 保留 `[66]`。

### E4 ⚠️ ZHB §七 PE 命名陈旧（lines 937、461）
- **原文**：Col[3] 纠正列写作 `pe_dynamic`（静态 PE / 最新年报）；line 461 断言「Col[3]=pe_dynamic（动态PE）」。
- **问题**：变量名 `pe_dynamic` 历史遗留，实为 `pe_mrq`（静态/MRQ）。Col[9]=`pe_ttm`(TTM) 正确无需改。
- **订正**：line 937 纠正列改 `pe_mrq`；line 461 断言改 `pe_mrq`，并补 fuyao 实锤指向。

### E5 ⚠️ §12.4 规范名列与注册表分裂
- **现象**：§12.4（跨数据源字段对照表）的「规范名」列使用一套与 §12.8.12e 注册表不一致的名字：`price` vs `last_price`、`pb` vs `pb_mrq`、`mcap_yi`/`float_mcap_yi` 在注册表无对应行（注册表缺口）。
- **订正**：
  - §12.4 内联改名：`price`→`last_price`、`pb`→`pb_mrq`、`mcap_yi`→`total_market_cap_yi`、`float_mcap_yi`→`float_market_cap_yi`；
  - §12.4 表末加「🔗 规范名治理」重定向说明，指向 §12.8.12e 为唯一语义名总表；
  - 注册表补全（见第三节），§12.4 全部规范名现已在注册表中有一一对应行。

---

## 三、注册表缺口补全（§12.8.12e，lines 2539–2565）

原注册表仅覆盖 PE/ROE/EPS/财务/量额/封单等「破解新字段」，缺失全部日常标量字段。本次新增 25 行，使注册表成为真正的总表：

`prev_close` / `open_price` / `high_price` / `low_price` / `change_pct` / `change_amt` / `volume_hand` / `amount_wan` / `turnover_pct` / `pb_mrq` / `total_market_cap_yi` / `float_market_cap_yi` / `total_shares_wan` / `float_shares_wan` / `bps` / `amplitude` / `entrust_ratio` / `entrust_diff` / `zt_price` / `high_52w` / `low_52w` / `beta` / `industry` / `concepts` / `list_date`

每行带「规范名(口径) | 语义 | push2 fN | 腾讯[idx] | ZHB Col[n] | fuyao 官方字段 | 状态」六列，与既有行同构。命名陷阱（fuyao `turnover`=成交额非换手率）在 `amount_wan` 行内联警示。

---

## 四、「同值异名 / 同名异义」范式案例（本项目标准答案）

用户核心关切 = 「标注语言差异 → 理解为不同字段」。本项目已实锤两类范式，供后续核查对照：

1. **口径 qualifier 差异（同值但字典看来不同）**——`f184` 口径分叉（§12.8.12f 铁证块）：
   - fuyao `calculate_operating_income_yoy_growth_ratio` = **营业收入**同比；
   - push2 `f184` = **营业总收入**同比（含利息收入）；
   - 19/20 精确等，仅茅台分叉（财务公司利息净收入）。差异**不在源标签，在口径 qualifier**。铁律：凡引用必须标注口径，不可混用/兜底。
2. **字段名 ≠ 语义（同名异义）**——`snapshot.turnover`：
   - 字面「换手率」，实测 = **成交额(元)**（÷f48 比值 1.000000，6日×20/20）；
   - 换手率应取 `auction_final.auction_turnover_pct` 或 push2 `f168`。凡把 `turnover` 当换手率用的代码即 bug。

> 推论：**真实语义漂移来自口径（MRQ/TTM/LYR/最新报告期/扣非/per-share/total），非源标签本身。** 这正是 §12.8.12e 强制「规范名+口径 qualifier」的底层逻辑。

---

## 五、仍建议用户确认 / 待办

1. **ZHB 变量名 `pe_dynamic`（Col[3]）**：§三 line 428/437 已注「变量名历史遗留,非动态PE」，但未重命名为 `pe_mrq`（ZHB 内部变量名，改名恐牵动代码，故保留+注记）。若后续统一层重构，建议 ZHB 侧 Col[3] 直接映射注册表 `pe_mrq`。
2. **开盘啦 [60] 是否确为动态PE**：本轮依开盘啦自身标签「动态PE」修正了跨源 fN 映射（→f163）。若要终验 [60] 真值，需开盘啦原始字段快照比对 f163（动态PE 介于静态与TTM间）。
3. **`roe_weighted_ttm` 概念**：腾讯/fuyao 均无 TTM ROE 单槽，注册表保留该行但标「待核」；如需 TTM ROE，须由 `roe_weighted` 推导或等 fuyao 开放。

---

## 六、固化铁律（已写入 §12.8.12e）

> 凡字典出现「PE 标签 / ROE 口径 / EPS 报告期」类描述，必须引用注册表规范名+口径，禁止再用 `f162=动态` 等源私有别名当语义名。§12.8.12e 为跨源唯一语义名总表；§12.4 规范名列已并入。

---

## 七、变更清单（落盘 `docs/field_dict.md`）

| 位置 | 变更 |
|:---|:---|
| line 1572 | 动态PE→静态PE(MRQ)（f162） |
| lines 3806–3808 + 3837 | 开盘啦 W8 PE 跨源映射 f162/f163→f163/f164/f162 + 订正注 |
| rows 2524–2527 | tx[65]→roe_weighted；tx[66] 去重（仅 ROA）；roe_weighted_ttm 腾讯列清空 |
| line 937 / 461 | ZHB Col[3] `pe_dynamic`→`pe_mrq` |
| lines 2539–2565 | 注册表新增 25 行日常字段 |
| lines 1729/1741/1742/1743 + 1751 | §12.4 规范名 price/pb/mcap_yi/float_mcap_yi 重定向 + 治理说明 |
