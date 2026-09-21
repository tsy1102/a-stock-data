# 5 大脚本字段接入与 fallback 治理 · 复核报告（v2 修正版）

> 生成日期：2026-09-21
> 范围：`get_mak / get_lng / get_med / get_val / get_sht` 五大报告脚本 + `core/data_provider.py` 的 `get_canonical_stock_data` 统一取数入口 + 26 源注册表（`docs/field_verification/field_registry.json`）。
> 状态：**本文档已用代码实测核实，修正了初版 Explore 报告的若干误判**。所有论断均附 `file:line` 证据。

---

## 0. 结论摘要（TL;DR）

1. **5 大脚本接入健康度：良好**。除 `get_mak` 走独立全市场扫描外，其余 4 个均经 `get_canonical_stock_data` 统一入口取数；跨源 fallback 链（L1 TDX → L2 腾讯 → L3 东财）结构清晰、注释充分。
2. **初版"孤儿源"论断多数不成立**——`em_fund_flow`、`clist`、`em_hot_concept`、`ZHB-tipinfo(涨停族)`、`AxData(eltdx 短线)` 在实测中均已接线。真正未接线/死条目的只有 `slist`（无实现函数，纯审计死标签）。
3. **唯一结构性缺口：源优先级散落于三处**（`dp.py` 内联分支 + `field_dict.md` §零·B/§一文档 + `audit_field_completeness.py` 的 `SECTION_MAP`）。运行时取数优先级只存在于 `dp.py` 内联，建议收敛为单一真相源。
4. **"可直取却仍计算"的字段：仅 `mcap_yi/float_mcap_yi` 的兜底分支**（当 rt_quote/ZHB 均无市值时按 `股本×价` 推算）；主路径已"先取后算"，非真缺口。
5. **阻塞项**：`ulist239` 资金流细分 `f88-f95` 尚未破解，无法接线（保持候选态，待对撞四铁律升级 L1）。

---

## 1. 初版论断 × 实测核实对照表

| 初版论断 | 核实结果 | 证据 |
|---|---|---|
| `em_fund_flow` 是孤儿源（生产零调用） | **误判**。`get_em_fund_flow` 被 `tdx_client.py:1846` 调用；`get_em_fund_flow_multiday` 被 `data_provider.py:675` 调用 | `tdx_client.py:1846`, `core/data_provider.py:675` |
| `clist` 未接线板块资金流 | **误判**。`_industry.py:588/810/890` 用 clist 拉行业/概念/地域板块 | `stock_common/sc_datasource/_industry.py:588` |
| `slist` 是孤儿源，需补实现或删登记 | **部分成立**：`slist` 既不在 `field_registry` 的 sources，也无任何实现函数；仅在 `audit SECTION_MAP:75` 作为死审计标签存在 | `grep` 全仓无 `def ...slist`；`scripts/audit_field_completeness.py:75` |
| `mcap_yi` 仍在计算而非直取（主缺口） | **过度声称**：主路径 `dp.py:1150-1179` 已"优先 `rt_quote.mcap_yi`/ZHB，缺失才按 `股本×价` 推算" | `core/data_provider.py:1150-1179` |
| tipinfo 涨停日/连板需纳入 sht/mak | **误判**：`get_zt_streak_info`（dp.py:1759）已零网络读取 ZHB tdxstat 连板/封单，sht 已用 | `core/data_provider.py:1759`, `get_sht_report.py` |
| AxData 短线指标未进生产 | **误判**：`get_eltdx_shortline_for_code`（dp.py:1370）已在 canonical 内消费 eltdx 短线 | `core/data_provider.py:1370`, `core/eltdx_adapter.py:285` |
| em_hot_concept 仅登记未用 | **部分误判**：`get_sht_report.py:2203` 已调用；val/med 确实未用（属可用增强，非修复） | `get_sht_report.py:2203` |
| 优先级/fallback 无集中配置 | **成立**：运行时顺序仅内联于 `dp.py:397-480`；文档与审计各有一份 | `core/data_provider.py:397-480`, `scripts/audit_field_completeness.py:67` |

---

## 2. 5 脚本字段消费现状（实测）

| 脚本 | 取数路径 | 主要 canonical 字段 | 直接 `data_provider.*` 调用 |
|---|---|---|---|
| `get_mak` | **不走** canonical；ZHB tdxstat 自聚合 + 腾讯板块 + ulist f62 + push2ex 涨停池 + ftshare + 财联社 | 全市场扫描类 | `tdx_get_board_members` 等（`tdx_client.py:3024`） |
| `get_lng` | `get_canonical_stock_data` | 行情/估值/资金流约 ~180 字段 | 少量注释引用 |
| `get_med` | `get_canonical_stock_data` | ~244 字段 | `get_change_pct_async`（`get_med_report.py:122`） |
| `get_val` | `get_canonical_stock_data` | ~756/1831 字段 | `get_volume_acceleration`(1535)、`get_capital_momentum`(1572) |
| `get_sht` | `get_canonical_stock_data` + 直接源 | ~306 字段 | `get_zt_streak_info`、`em_hot_concept`(2203) |

**已接线新源（dict 登记且运行时调用）**：ulist239(资金流 `dp.py:649/675`)、`em_hot_rank`(val:2255)、`reports`(med:640/lng:125)、`em_kline_f61`/CYQ(med:865)、ftshare(sht:1475/mak:1208)、baidu_kline(med:686)、datacenter 行业 L2(`dp.py:1242`)、财联社(med:1249)、push2ex(mak/sht)、`em_hot_concept`(sht:2203)、`get_zt_streak_info`/ZHB tipinfo(dp:1759)、AxData eltdx shortline(dp:1370)。

**真正未接线/死条目**：
- `slist`：`audit SECTION_MAP:75` 死标签，无实现函数 → **清理**。
- `ulist239 f88-f95` 资金流细分：未破解 → **保持候选，待 L1**。

---

## 3. 内部计算字段：是否可直取

| 字段 | 当前实现 | 直取源（dict 已定案） | 结论 |
|---|---|---|---|
| `mcap_yi`/`float_mcap_yi` | 优先 `rt_quote.mcap_yi`/ZHB；缺失才 `股本×价` 推算（`dp.py:1150-1179`） | tx[45]/tx[44]（L1）、fuyao、ulist239 f20/f116 | **已先取后算**，兜底推算仅应急；建议加一道"双源一致性护栏"（见 §5-2） |
| `amplitude_pct` | 仅 quote 无值时算（`dp.py:950`） | tx[43]（L1） | 保持 |
| `prev_close` | `price/(1+chg%)` 反算（`dp.py:806`，带合理性校验） | tx[4]（L1） | 保持 |
| `pb` | `price/bvps`（`dp.py:907`，缺值时） | tx[46]/f167/fuyao | 保持 |
| `eps_annual`/`net_profit_margin`/`sec_type` | 真派生，无单一直取源 | — | 保留计算 |

→ **真正"可直取却仍计算"的仅市值兜底分支**，且非主路径。其余模式已健康。

---

## 4. 字段优先级与 fallback 现状

运行时链（硬编码内联，`dp.py:397-480`）：
1. 批量预取（push2delay/ulist）→ 注入 `rt_quote`（标记 `realtime:push2delay:batch`）。
2. **L1 TDX**（eltdx 本地 TCP）：批量命中且缺 OHLC 时补五档/open/high/low/last_close（`dp.py:406-424`）。
3. **L2 腾讯**：TDX 无价时补（`dp.py:427-441`）。
4. **L3 东财**：腾讯仍无价时 push2delay→push2 兜底（`dp.py:446-480`）。
5. 估值补取：腾讯独有 roa/pe_ttm/pb/股息率主动补 1 次（`dp.py:482+`）。
6. 财务 TTM：fuyao 升为主源（V17.0.7，`dp.py:551`）。
7. 资金流：push2 f137 → TDX（`dp.py:638-700`）+ `get_em_fund_flow_multiday`（push2，`dp.py:675`）。

**问题**：优先级逻辑散落于 ① `dp.py` 内联分支 ② `field_dict.md` §零·B/§一（文档）③ `audit_field_completeness.py` 的 `SECTION_MAP`（审计映射，与运行时顺序不是同一概念，但混在一起易歧义）。新增/调权任何源需改多处 → 建议抽离 `SOURCE_PRIORITY` 单一配置（见 §5-1）。

---

## 5. 修正后的建议与已执行改动

> 以下为本报告落地执行的改动清单（非纯建议）。逐项对应 commit。

### 5-1 源优先级收敛为单一真相源（结构性修复）
- 新增 `core/source_priority.py`：`QUOTE_FETCH_ORDER`、`FUND_FLOW_PRIORITY`、`VALUATION_PRIORITY` 常量 + docstring 引证内联位置；附 `check_quote_priority()` 一致性校验（供测试/启动期调用，非生产热路径）。
- `data_provider.py` 在 L1/L2/L3 分支处引用该常量（**行为不变**，仅把"顺序"从隐式注释提升为显式常量）。
- 价值：新增/调权源只改一处；消除三处文档与代码漂移。

### 5-2 mcap 双源一致性护栏（低风险增强）
- 在 `dp.py:1150-1179` 的 mcap 推算分支增加：当 rt_quote 直取市值与 `股本×价` 推算值偏离 > 2× 时，记录 `field_sources` 标记并优先采用直取值（不静默覆盖，仅日志/溯源）。保持既有"先取后算"语义。

### 5-3 em_hot_concept 富集接入 val（一致性增强）
- `data_provider.py` 新增 `get_hot_concepts(code)` 访问器（沿用 `get_zt_streak_info` 的 lazy + try/except 模式，**不进入 canonical 热路径**，避免新增网络延迟）。
- `get_val_report.py` 在既有热门板块段（`em_hot_rank` 调用处 ~2254）旁，按 `get_sht_report.py:2203` 同款模式接入，非破坏性（数据非空才记录）。med 暂无自然钩子，仅文档建议。

### 5-4 清理 slist 死审计条目
- `scripts/audit_field_completeness.py:75` 的 `'东财-slist'` 条目无对应实现函数，移除，避免"字典有源、运行时不用"误导。

### 5-5 不执行 / 阻塞项（透明说明）
- `ulist239 f88-f95` 资金流细分：未破解，保持候选态，待对撞四铁律（≥3 采集日 + 跨源精确相等 + hub 巧合排除）升级 L1 后再接线。
- `AxData 34 字段`（`_quotes.py:1058`）为 legacy HTTP 路径；生产已用 eltdx 适配层（`dp.py:1370`），不再重复接线。
- `em_fund_flow`/`clist`/`tipinfo`/`AxData eltdx` 经核实已接线，**不重复改动**。

---

## 6. 治理闸门

所有改动经：G1 `registry_parity.py`（native + §零·B 投影）、G3 `gen_field_dict.py --check`（幂等）、P1 `archive_field_preflight.py`（预检）验证；提交经 `PYTHON=py` 触发 G1 提交钩子。

> 数据来源以项目字典（东财/腾讯/同花顺/通达信等）登记源为准，本文不构成投资建议。
