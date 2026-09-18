# 统一层 & 缓存层同步核查报告（2026-09-18 / V17.3）

> 背景：在最新主字典破解批次（#257 版本升级 / #258 英文→中文统一 / #259 入库 raw json / #260 扩展 registered_field_sets / #261 全量 49 候选经黄金锚复核定案）与 V17.3 脚本修改（med None 泄漏 / sht 流通市值+跌停 / lng 总股本单位 / val eltdx 口径）之后，核查统一层（`core/data_provider.py` `get_canonical_stock_data`，86 字段 frozen 契约）与缓存层（`cache/`：kline / zhb / capital_cache）是否需要同步更新，并排查 bug 与死代码。

## 一、统一层（core/data_provider.py）核查

### 1.1 字段契约与字典破解同步性 —— 无需新增暴露 ✅
- 字典破解 #257-#261 破解/verified 的是**原始 f 编号 ↔ 中文语义**映射，由源适配器 `sc_datasource` / `zhb_client` / `tdx_client` 消费；统一层合约经适配器自动继承订正，**无需在统一层新增字段暴露**。
- V17.3 脚本修改所用的字段（`total_shares_wan` / `float_shares_wan` / `float_mcap_yi` / `mcap_yi` / `price`）**均在既有 86 字段 frozen 契约内**，统一层契约字段集无需变更。

### 1.2 单位换算 Bug（严重，已修复）🔴→🟢
**现象**：大盘股（总股本 > 1000 亿股）经 `get_canonical_stock_data` 得到的总股本/市值静默错算 10000 倍。

**根因**：`core/data_provider.py` 内联的 `total_shares_wan` 单位归一守卫阈值误用**旧值 `>1e7`**，与已订正的兄弟模块 `stock_common/sc_capital_cache.py`（`_CAPITAL_SCHEMA_VERSION=2`，阈值 `1e9 万股`）**直接矛盾**。`sc_capital_cache` 注释已实锤：旧 `1e7` 阈值少算一个数量级，"曾把正确大盘股万股值误当'股'再÷10000"。

数据流：`total_shares_wan` 经 `sc_capital_cache` 兜底后已是**正确万股值**（如 601398=35640624 万股），但 `>1e7` 守卫误判为"股"单位再 `/1e4` → 3564 万股，市值随之错 10000 倍。

**实证（修复前/后实盘 `get_canonical_stock_data('601398')`）**：
| 字段 | 修复前 | 修复后（正确） |
|---|---|---|
| total_shares_wan | 3564.06 万股 | 35640624.00 万股（=3564 亿股） |
| mcap_yi | 2.87 亿 | 28761.98 亿（=2.88 万亿） |

> ⚠️ **历史影响**：20260918 批次审计因被测股 000938 为中盘（286008 万股 < 1e7）漏检此 bug；此前生成的**大盘股（>1000亿股，如工农中建/中石油）sht/med/lng 报告中总股本与总市值曾被静默误算**。如需精确历史数据须重跑大盘股报告。

**修复（提交见末尾）**：
- `total_shares_wan` 守卫阈值 `>1e7` → `>1e9`（与 `sc_capital_cache` v2 对齐）。
- 对 `float_shares_wan` 补对称守卫 `>1e9`（万股→万股防御，防未来 `rt_quote` 加流通股本字段时"股"单位误入）。
- 对 `float_mcap_yi` 补对称守卫 `>1e6`（万元→亿，与既有 `mcap_yi` 守卫一致）。

### 1.3 跨层一致性核验 ✅
实盘复现多标的全部正确：
- `601398` 35640624 万股 / 28761.98 亿；`601939` 26160038 万股 / 28279 亿；`601857` 18302098 万股 / 19327 亿；`000938` 286008 万股 / 971 亿。
- 与 lng 修复后 `28.60亿股` 完全一致，统一层 ↔ 报告层股本口径现已自洽。

## 二、缓存层（cache/）核查 —— 无需同步更新 ✅

| 缓存组件 | 失效策略 | 结论 |
|---|---|---|
| `sc_kline_cache.py` | 24h TTL（`CACHE_TTL_SECONDS=86400`）+ >500MB 按 mtime LRU 清理，init 自动 `clear_expired()` | 设计良好，无需改 |
| `sc_capital_cache.py` | schema 版本号（`_CAPITAL_SCHEMA_VERSION=2`），版本不符自动失效重建 | 阈值已正确（`1e9`），本次统一层守卫已对齐 |
| `cache/zhb`、`cache/zhb_parsed` | ZHB 快照 T-1（设计预期，用户同步刷新） | 陈旧为预期，非 bug |

- 字典破解批次为语义映射，不改动缓存 schema；缓存存储原始/归一值，版本化已兜住单位变更。**缓存层无需因字典破解或脚本修改做结构/失效策略更新**。

## 三、死代码与脆弱性发现（未修，建议）

1. **`cache/` 临时调试文件堆积（103 个未跟踪）**：`_dbg_*` / `_fix_*` / `_f821` / `_verify_*` / `audit_*` / `_phase*` / `_probe_*` 等，为历史死代码清理批次（提交 `0721b3c`/`1bac5df`）与本会话核查遗留的脚手架。已被 `.gitignore` 覆盖，不污染提交，但属杂物，建议清理。
2. **`core/data_provider.py:64` ↔ `sc_datasource/_quotes.py:20` 循环导入**：二者均为**顶层 import**，构成循环依赖。生产靠入口先载 `stock_common` 规避；直引 `from core.data_provider import ...` 即触发 `ImportError`。属预存在的导入顺序脆弱性，本次不修（高风险重构，超出核查范围）。

## 四、提交说明
- 修复落地 `core/data_provider.py`（3 处守卫），`py_compile` 通过，实盘复现验证。
- `CHANGELOG.md` [V17.3] 增补统一层跨层同步修复、缓存层核查结论、死代码发现三段。
- 治理闸门（`field_dict`/`field_registry`/`docs/verify` 未改动）正确跳过。

（数据来源：通达信 / 多源对撞体系；以上为数据质量与架构治理结论，不构成投资建议。）
