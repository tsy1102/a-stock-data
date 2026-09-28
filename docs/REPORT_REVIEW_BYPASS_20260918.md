# 统一层同义字段遗漏 / 口径一致性 严格审查报告

> 批次：2026-09-18（V17.3 续作）｜范围：`get_canonical_stock_data` 统一层契约 × 5 大报告脚本 × 主字典
> 数据来源：通达信 / 多源对撞体系｜结论不构成投资建议

## 一、你的根因疑问：sht/med 正常、lng 错误，是哪一种？

**结论：选项 1（脚本绕过统一层、采用不同源/函数导致口径不一致）成立；选项 2（统一层遗漏字段）不成立。**

实证依据：
- 统一层契约 `CanonicalStockData`（`stock_common/sc_schema.py:440+`）**已包含** `total_shares_wan`（总股本·万股，line 63）、`float_shares_wan`、`mcap_yi`、`float_mcap_yi`。字段存在且正确。
- `get_lng_report.py` 之前**没有使用**统一层字段，而是直接调用 `get_stock_info(code)['total_shares']`（原始源函数）。实测 `info.total_shares == cdata.total_shares_wan`（如 000938 均 = 286008 万股），即两者**同源同值**，但 `info.total_shares` 的单位语义在历史注释中被误标为"股"。
- `get_sht_report.py:331` 用 `cdata.total_shares_wan/1e4`（万股→亿股）正确；`get_med_report.py` 对股本仅作兜底展示（主路径 `cdata`）。所以 sht/med 显示正常、lng 错误——**不是统一层缺字段，而是 lng 绕过统一层直取源并错用单位**。

> 一句话：统一层"有这个字段且对"，是消费方"没走统一层、自己取源还用错单位"。

## 二、严格审查方法

1. 提取 `CanonicalStockData` 全部字段（统一层契约面）。
2. 全仓扫描报告脚本对 `get_stock_info` 的 `info.*` 直取点（绕过统一层的最典型模式）。
3. 对 `total_shares` 类做单位实证（探针 `cache/_probe_lng_ts.py` / `cache/_probe_cap_units.py` 已证实 `info.total_shares`=万股）。
4. 交叉核对北向 `hold_shares`（东财 `HOLD_SHARES`，原始单位=股，显示 `/1e4` 标"万股"印证）与 `info.total_shares`（万股）的同义字段混算。
5. 扫描资金流/PE 类原始 `fXXX` 直取（确认主路径已走 `cdata`）。

## 三、审查发现清单

### 🔴 已修复（V17.3 本批次）——本会话新增 2 处

| # | 位置 | 现象 | 根因 | 修复 |
|---|------|------|------|------|
| F1 | `get_lng_report.py:531` `get_roe_trend_series` | 新浪兜底 `eps=profit/total_shares` 期望**股**，传入 `info.total_shares`（万股）→ EPS/BPS 错 **1e4 倍**（仅 F10 缺失时触发） | 绕过统一层 + 单位误标 | 改用 `cdata.total_shares_wan*1e4`（股） |
| F2 | `get_sht_report.py:983` / `get_med_report.py:947` 北向占比兜底 | `_shares`(股) ÷ `info.total_shares`(万股) 单位错配（差 1e4）；且 **sht 无 ×100、med 有 ×100 → 两脚本口径互不一致（差 100 倍）** | 同上 + 两脚本口径未对齐 | 统一 `cdata.total_shares_wan*1e4`，均 ×100 百分数 |

### 🟡 已修复（前续 V17.3）——复盘更正

- `get_lng_report.py:401` 总股本显示：`info.total_shares/1e8`（误按股）→ `/1e4`（万股→亿股），数值已正确；并保留 `cdata.total_shares_wan` 兜底（line 402-403）。

### 🟢 架构建议（未改代码，非 bug）

- `get_lng_report.py:401` 仍**首选** `info.get('total_shares')`（已 `/1e4` 数值正确 + 有 cdata 兜底），建议正式改为首选 `cdata.total_shares_wan` 以彻底消除"绕过统一层"隐患。
- **统一层增强建议**：`CanonicalStockData` 当前仅暴露 `total_shares_wan`（万股）。建议在统一层**新增便捷字段 `total_shares`（股）**，使所有消费方只用单一单位，从根上消灭"股/万股"陷阱（这是本次 3 处 bug 的共同温床）。属增强，不改动现有字段。

### ✅ 一致性通过项（审查确认无绕过）

- 资金流：`cdata.fund_main_today` / `cdata.pe_ttm` 等主路径均走统一层；报告脚本无原始 `f137/f62/...` 直取。
- PE/PB/涨跌/换手：`cdata` 同源，无口径分歧。
- `name/industry/list_date`：`info.get` 仅作 `cdata.xxx or info.get` 兜底，属防御性用法，非口径分歧。

## 四、关于"主字典同义字段未统一"的判定

- **未遗漏**：股本/市值类主字典字段在统一层均有对应（`total_shares_wan`/`float_shares_wan`/`mcap_yi`/`float_mcap_yi`），无"同义多源却无统一字段"的遗漏。
- **存在不一致采纳**：问题不在"统一层缺字段"，而在"消费方未一致采纳统一层、自行绕过 `get_stock_info` 直取"，且 `info.total_shares` 单位语义长期误标诱发错算。本次 F1/F2 即该类遗漏采纳的确证 bug。
- 审查未发现资金流/PE 等其他类的同类绕过；若需，可对 `field_dict.md` 全字段 × `CanonicalStockData` 做机器交叉比对（下一轮可自动化）。

## 五、提交

- `fix(reports)`: V17.3 审查补刀——lng:531 EPS/BPS 单位 + sht/med 北向占比单位与口径对齐（均改 `cdata.total_shares_wan*1e4`）。
- 治理闸门正确跳过（无 field_dict/registry 改动）。
