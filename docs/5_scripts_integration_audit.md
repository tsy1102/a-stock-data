# 5 大脚本字段接入与 fallback 治理 · 复核报告（v2 修正版）

> 生成日期：2026-09-21
> 范围：`get_mak / get_lng / get_med / get_val / get_sht` 五大报告脚本 + `core/data_provider.py` 的 `get_canonical_stock_data` 统一取数入口。报告形成时登记表有 26 个来源；2026-09-28 复核后为 28 个来源。
> 状态：**本文档已用代码实测核实，修正了初版 Explore 报告的若干误判**。所有论断均附 `file:line` 证据。
>
> **2026-09-28 复核说明**：下文 2026-09-21 关于“单一优先级配置”和 POSIX 治理脚本接入提交钩子的描述已过期，详见本次订正。运行时路由仍由 `core/data_provider.py` 的分支决定；`core/source_priority.py` 现在仅保存 quote fallback 的测试期望值。

---

## 0. 结论摘要（TL;DR）

1. **5 大脚本接入健康度：良好**。除 `get_mak` 走独立全市场扫描外，其余 4 个均经 `get_canonical_stock_data` 统一入口取数；跨源 fallback 链（L1 TDX → L2 腾讯 → L3 东财）结构清晰、注释充分。
2. **初版"孤儿源"论断多数不成立**——`em_fund_flow`、`clist`、`em_hot_concept`、`ZHB-tipinfo(涨停族)`、`AxData(eltdx 短线)` 在实测中均已接线。`slist` 有字段采集探针 producer，但仅服务采集，不是报告运行时的板块归属源；主字典规定运行时板块归属走 TDX。
3. **路由行为由代码分支实现**。字段字典记录字段与来源事实，`audit_field_completeness.py` 的 `SECTION_MAP` 用于审计归属；两者都不是运行时路由配置。`core/source_priority.py` 只用于测试断言，不是生产代码的单一配置源。
4. **"可直取却仍计算"的字段：仅 `mcap_yi/float_mcap_yi` 的兜底分支**（当 rt_quote/ZHB 均无市值时按 `股本×价` 推算）；主路径已"先取后算"，非真缺口。
5. **阻塞项**：`ulist239` 资金流细分 `f88-f95` 尚未破解，无法接线（保持候选态，待对撞四铁律升级 L1）。

---

## 1. 初版论断 × 实测核实对照表

| 初版论断 | 核实结果 | 证据 |
|---|---|---|
| `em_fund_flow` 是孤儿源（生产零调用） | **误判**。`get_em_fund_flow` 被 `tdx_client.py:1846` 调用；`get_em_fund_flow_multiday` 被 `data_provider.py:675` 调用 | `tdx_client.py:1846`, `core/data_provider.py:675` |
| `clist` 未接线板块资金流 | **误判**。`_industry.py:588/810/890` 用 clist 拉行业/概念/地域板块 | `stock_common/sc_datasource/_industry.py:588` |
| `slist` 是孤儿源，需补实现或删登记 | **误判**：`capture_field_probe.py:946` 实现 `collect_slist`，供字段采集探针使用；它不是报告运行时板块归属源，字典规定运行时走 TDX。保留采集来源与审计映射 | `scripts/capture_field_probe.py:946,1786`; `docs/field_dict.md:2384`; `scripts/audit_field_completeness.py:93` |
| `mcap_yi` 仍在计算而非直取（主缺口） | **过度声称**：主路径优先直取；只在值缺失时按 `股本×价` 推算，偏差检查仅写 debug 日志 | `core/data_provider.py:1270-1306` |
| tipinfo 涨停日/连板需纳入 sht/mak | **误判**：`get_zt_streak_info`（dp.py:1759）已零网络读取 ZHB tdxstat 连板/封单，sht 已用 | `core/data_provider.py:1759`, `get_sht_report.py` |
| AxData 短线指标未进生产 | **误判**：`get_eltdx_shortline_for_code`（dp.py:1370）已在 canonical 内消费 eltdx 短线 | `core/data_provider.py:1370`, `core/eltdx_adapter.py:285` |
| em_hot_concept 仅登记未用 | **误判**：`get_sht_report.py:2203` 与 `get_val_report.py:2283-2297` 均已接入；`med` 暂无调用 | `core/data_provider.py:1953-1966`; `get_sht_report.py:2203`; `get_val_report.py:2283-2297` |
| 优先级/fallback 无集中配置 | **订正**：运行时路由由 `data_provider.py` 的实际分支执行；测试合同不驱动生产路由 | `core/data_provider.py`, `core/source_priority.py`, `tests/core/test_quote_fallback_order.py` |

---

## 2. 5 脚本字段消费现状（实测）

| 脚本 | 取数路径 | 主要 canonical 字段 | 直接 `data_provider.*` 调用 |
|---|---|---|---|
| `get_mak` | **不走** canonical；ZHB tdxstat 自聚合 + 腾讯板块 + ulist f62 + push2ex 涨停池 + ftshare + 财联社 | 全市场扫描类 | `tdx_get_board_members` 等（`tdx_client.py:3024`） |
| `get_lng` | `get_canonical_stock_data` | 行情/估值/资金流约 ~180 字段 | 少量注释引用 |
| `get_med` | `get_canonical_stock_data` | ~244 字段 | `get_change_pct_async`（`get_med_report.py:122`） |
| `get_val` | `get_canonical_stock_data` | ~756/1831 字段 | `get_volume_acceleration`(1535)、`get_capital_momentum`(1572) |
| `get_sht` | `get_canonical_stock_data` + 直接源 | ~306 字段 | `get_zt_streak_info`、`em_hot_concept`(2203) |

**已接线新源（dict 登记且运行时调用）**：ulist239(资金流 `dp.py:649/675`)、`em_hot_rank`(val:2255)、`reports`(med:640/lng:125)、`em_kline_f61`/CYQ(med:865)、ftshare(sht:1475/mak:1208)、baidu_kline(med:686)、datacenter 行业 L2(`dp.py:1242`)、财联社(med:1249)、push2ex(mak/sht)、`em_hot_concept`(sht:2203、val:2283)、`get_zt_streak_info`/ZHB tipinfo(dp:1759)、AxData eltdx shortline(dp:1370)。`slist` 是独立的采集探针来源，不属于报告运行时接线。

**接入边界与未破解项**：
- `slist`：`capture_field_probe.py:946` 有实际采集实现，仅供字段探针；运行时板块归属按字典使用 TDX。保留来源与 `SECTION_MAP` 映射（`audit_field_completeness.py:93`），不删除或标为死代码。
- `ulist239 f88-f95` 资金流细分：未破解 → **保持候选，待 L1**。

---

## 3. 内部计算字段：是否可直取

| 字段 | 当前实现 | 直取源（dict 已定案） | 结论 |
|---|---|---|---|
| `mcap_yi`/`float_mcap_yi` | 优先直取；缺失才按 `股本×价` 推算（`core/data_provider.py:1270-1284`） | tx[45]/tx[44]（L1）、fuyao、ulist239 f20/f116 | **已先取后算**；另有 >2× 偏差 debug 观测护栏（`core/data_provider.py:1289-1306`），不改值或来源 |
| `amplitude_pct` | 仅 quote 无值时算（`dp.py:950`） | tx[43]（L1） | 保持 |
| `prev_close` | `price/(1+chg%)` 反算（`dp.py:806`，带合理性校验） | tx[4]（L1） | 保持 |
| `pb` | `price/bvps`（`dp.py:907`，缺值时） | tx[46]/f167/fuyao | 保持 |
| `eps_annual`/`net_profit_margin`/`sec_type` | 真派生，无单一直取源 | — | 保留计算 |

→ **市值公式只用于缺失值兜底**；双源偏差检查只记 debug 日志，不改变字段值或来源。其余模式已健康。

---

## 4. 字段优先级与 fallback 现状

当前路由分两步判断：

1. `_should_use_zhb_for_realtime()` 根据交易日和时段判断是否走 ZHB；非交易日/节假日及交易日 09:30 前可用 ZHB，交易日 09:30 起（包括盘后）走实时行情路径。
2. 需要实时行情时，`get_canonical_stock_data()` 的 quote fallback 分支按 TDX → 腾讯 → push2delay → push2 尝试。
3. 估值、财务和资金流由各自字段路径选择来源，不应把它们压成一个通用行情优先级列表。

字段字典登记字段语义和来源，`SECTION_MAP` 用于审计归属，`core/source_priority.py` 仅为 quote 顺序回归测试提供预期值。它们承担不同职责，不能互相当作生产路由真相源。

---

## 5. 修正后的建议与已执行改动

> 以下记录建议项与当前实现状态；“已实现”均以代码位置为准。本文不记录 Git 提交状态。

### 5-1 对优先级声明的 2026-09-28 订正
- 复核发现旧版 `core/source_priority.py` 中多组 quote/valuation/fund-flow 常量没有被生产分支消费，自检也只是在比较声明本身，容易制造“运行时已集中配置”的错觉。
- 移除了未消费的优先级列表和无效自检；保留 `QUOTE_FALLBACK_EXPECTED_ORDER` 作为测试契约。生产顺序仍在 `data_provider.py` 的业务分支中实现，测试 mock 实际调用来验证顺序。
- 增加交易日、节假日、09:30、15:00 等边界测试。修改路由时须同步修改实现和行为测试，不应只改测试常量。

### 5-2 mcap 双源一致性护栏（已实现，纯观测）
- `core/data_provider.py:1289-1306` 在直取市值与 `股本×价` 估算偏离 > 2× 时写 debug 日志。该检查不改变市值、不修改 `field_sources`，也不改变现有直取优先和缺失值推算行为。

### 5-3 em_hot_concept 富集接入 val（已实现）
- `core/data_provider.py:1953-1966` 提供 lazy `get_hot_concepts(code)` 访问器，不进入 canonical 热路径。
- `get_val_report.py:2283-2297` 为热门股按需附加最多 3 个概念标签；`get_sht_report.py:2203` 也已接入。`med` 暂无调用点。

### 5-4 保留 slist 采集来源映射（撤回死代码建议）
- `scripts/capture_field_probe.py:946` 实现 `collect_slist`，并在 `:1786` 注册到采集探针；字段字典 `docs/field_dict.md:2384` 标明它是采集探针源，运行时板块归属走 TDX。
- 因此保留 `scripts/audit_field_completeness.py:93` 的来源分类。`slist` 没有报告运行时适配器，不等于没有 producer，也不应从采集审计中删除。

### 5-5 不执行 / 阻塞项（透明说明）
- `ulist239 f88-f95` 资金流细分：未破解，保持候选态，待对撞四铁律（≥3 采集日 + 跨源精确相等 + hub 巧合排除）升级 L1 后再接线。
- `AxData 34 字段`（`_quotes.py:1058`）为 legacy HTTP 路径；生产已用 eltdx 适配层（`dp.py:1370`），不再重复接线。
- `em_fund_flow`/`clist`/`tipinfo`/`AxData eltdx` 经核实已接线，**不重复改动**。

---

## 6. 治理闸门

登记表变更可通过 G1 `registry_parity.py`（native + §零·B 投影）、G3 `gen_field_dict.py --check`、P1 `archive_field_preflight.py` 验证。仓库当前没有 `.github/workflows/` 或 `.pre-commit-config.yaml`；不要把本地 `run_governance_gates.sh` 描述成已接入 CI 或提交钩子的自动闸门。

> 数据来源以项目字典（东财/腾讯/同花顺/通达信等）登记源为准，本文不构成投资建议。
