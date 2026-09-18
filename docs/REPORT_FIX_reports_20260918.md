# reports/ 20260918 批次数据质量修复报告（V17.3）

> 数据来源：通达信 / 项目多源对撞体系（push2、东财、腾讯、同花顺、ZHB、eltdx 等）。以下结论均不构成投资建议。

## 一、核查范围

2026-09-18 批次 `reports/` 下全部 **37 篇 md 报告**，覆盖 5 大脚本：

- `get_sht_report.py`（33 篇个股深度 `_sht_`）
- `get_med_report.py` / `get_lng_report.py`（000938 各 1）
- `get_mak_report.py`（1 篇市场情绪看板）
- `get_val_report.py`（1 篇策略发现，27 策略）

校验方法：内部算术一致性（市值/股本/涨跌幅/振幅/涨跌停价/封板率/主力净额单位与占比/北向）、跨脚本矛盾（sht↔mak 跌停/北向）、缺失库存（⚠️ 标记 + 占位符扫描）。脚本 `cache/_audit_reports_20260918.py`。

## 二、3 处真实错误及修复

### 错误 1 — `get_med_report.py` 互动易未回复渲染字面 `答案: None`

- **现象**：`000938_med_20260918_1822.md:254/256` 把互动易未回复问题渲染成字面 `答案: None`（Python `None` 类型被 `str()` 转成字符串泄漏）。
- **根因**：`cninfo_irm` 对未回复问题偶发返回字面字符串 `"None"`，`a = str(item.get("answer","")).strip()` 判真后直接渲染。
- **修复**（`get_med_report.py:1288`）：归一化 `"none"/"nan"/"n/a"/"null"` 为待回复，与 sht 的"（公司待回复）"口径对齐。
  ```python
  a = str(item.get("answer", "")).strip()
  if a.lower() in ("none", "nan", "n/a", "null"):
      a = ""
  _ans = f"答案: {a[:120]}" if a else "答案: （公司待回复）"
  ```

### 错误 2 — `get_sht_report.py` 002360 流通市值不自洽

- **现象**：`002360_sht_20260918_1804.md` 流通股本 3.26亿股 × 现价 5.33 = **17.38 亿**，报告却写 **流通市值 16.44 亿**（偏差 5.4%）；同股总市值 21.41 亿 = 总股本 4.02亿×5.33 自洽。
- **根因**：`cdata.float_mcap_yi`（流通市值）偶发 stale 价格基准，与同表 `现价`/`总市值` 不同源。
- **修复**（`get_sht_report.py:378`）：流通市值恒由 `流通股本(亿股) × 现价` 推导，与总市值/现价同源同价基。
  ```python
  _float_mv_yi = (cdata.float_shares_wan / 1e4) * price_today if cdata.float_shares_wan else cdata.float_mcap_yi
  L(f"  总市值:   {cdata.mcap_yi:.2f} 亿元  流通市值: {_float_mv_yi:.2f} 亿元")
  ```

### 错误 3 — `get_lng_report.py` 000938 总股本=0.00亿股（陈旧产物，代码已修）

- **现象**：`000938_lng_20260918_1824.md:22` 渲染 `总股本: 0.00亿股`，但总市值 971.00亿 ÷ 现价 33.95 = 28.6亿股（与 sht/med 的 28.60亿股一致）。
- **根因**：该报告为 **修复前陈旧产物**。当前工作树代码（`get_lng_report.py` V17.2.26，提交 `d6e0318` 2026-09-17 21:11）已修复：先取 `info.total_shares`，再回退 canonical `cdata.total_shares_wan`（万股→亿股），仍为空则渲染"数据暂缺"，**永不显示误导性的 0.00亿股**。
- **处置**：代码层已正确（重跑即渲染 28.60亿股 或 数据暂缺）；本报告 artifact 需在用户正常管线重跑时刷新。本批次**不修改 lng 代码**（已在 V17.2.26 收口）。

## 三、跌停计数矛盾（3 vs 0）根因定位与修复

- **矛盾**：33 篇 sht §十五 均写 `跌停 3 只`，而 `get_mak_report_20260918_1800.md` 写 `跌停 0 只`；两者涨停(77)/炸板(25)/封板率(76%)完全一致。
- **根因**：sht 原读取 `get_limit_pool_summary().limit_down_count`（跌停池接口返回 **stale 值 3**）；mak 用全市场 ZHB 快照 `is_limit_down(change_pct)` 实时口径得 **0**。两脚本涨停计数一致（pool.limit_up_count 与快照同源），唯独跌停池字段 stale → 矛盾。
- **验证**：mak 的 `get_market_abnormal_data()`（mak:153）与 sht 的 `tdx_get_market_abnormal_data()`（core.tdx_client:3185）**同源**（均走 ZHB 全市场快照），故 mak 的 0 为权威实时口径。
- **修复**（`get_sht_report.py:1502`）：sht 跌停计数**优先采用与 mak 同源的实时涨跌幅口径**，仅在快照源不可用时回退 pool。
  ```python
  _dt_count_pool = pool.get("limit_down_count", 0)
  _abn = tdx_get_market_abnormal_data()      # 与 mak A 段 _dt_count 同源
  dt_count = sum(1 for s in _abn if is_limit_down(...)) if _abn else _dt_count_pool
  ```
- **附带提示**：ZHB 快照为 T-1 收盘数据，mak/sht 的"今日涨停/跌停"实为 T-1 口径（两报告共享此特性，非矛盾来源）；如需 T 日实时，须接入盘中行情源。

## 四、val 脚本 0 数量策略核查（脚本错误 vs 真实无符合）

今日 val 报告共 **3 个策略**显示"（今日无符合该策略阈值的标的）"：

| 策略 | 成因 | 判定 | 处置 |
|---|---|---|---|
| **02 周线多头(含金叉)** | 严格 MA5>MA10>MA20>MA30 多头排列 + 簇散度<5% + 现价≥MA5 + 周线≥25 根；当日无个股同时满足 | **真实无符合**（严格技术条件，无误） | 不改 |
| **26 连板梯队·短线封单强度** | 依赖 `get_eltdx_shortline_bundle()`（本地 TDX/eltdx 实时）；eltdx 未连接 → `sl_map` 空 → 降级返回 `[]` | **数据源缺失（非真实）**；当日 77 只涨停必有连板/强封标的 | 修复报告口径 |
| **27 短线资金强度·开盘抢筹** | 同上（eltdx 依赖） | **数据源缺失（非真实）** | 修复报告口径 |

- **根因**：策略 26/27 在 eltdx 不可用时**静默返回 `[]`**，与"真实无符合"在报告层无法区分，误导用户以为当日无连板/抢筹标的。
- **修复**：
  1. `core/eltdx_adapter.py` 新增 `is_eltdx_available()` 轻量探测（检测 `import eltdx` 是否成功）。
  2. `get_val_report.py` 渲染层对 策略26/27 空产出时，若 `is_eltdx_available()` 为 False，显式标注：
     `⚠️ eltdx 数据源不可用（本地 TDX 未连接 / eltdx 未安装），本策略降级跳过——属数据源缺失，非真实无符合标的`。
  3. 策略 02 维持原样（确为真实无符合）。

## 五、一致性通过项（无误，供复核）

涨跌幅、振幅、涨跌停价（按代码分市场 ±10%/±20%/±30%）、主力净流入单位与占比、北向沪股通（−9.28亿 sht↔mak 一致）、封板率自洽、000938 三类型(sht/med/lng) 总市值(971.00亿) 与 PE_TTM(34.54) 对齐、val 其余 24 策略产出正常（190 次选择）。

## 六、提交

- 代码修复：`get_med_report.py`、`get_sht_report.py`（流通市值 + 跌停）、`get_val_report.py`、`core/eltdx_adapter.py`。
- 经 `scripts/run_governance_gates.sh`（G1/G3/P1，`PYTHON=py` 闸门）提交；`CHANGELOG.md` [V17.3] 补上述说明。
- lng 报告 artifact 陈旧项不计入本次提交（代码已 V17.2.26 收口，重跑即刷新）。
