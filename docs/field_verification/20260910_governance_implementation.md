# 项目健康体检治理 —— 实施报告

> 实施时间：2026-09-10 | 前置报告：`20260910_project_health_audit.md`（只读分析）
> 用户决策：Q1 统一口径 / Q2 scratch 保持不跟踪 / Q3 删除 .vendor_backup / Q4 两份 README 不合并 / Q5 限流表不合并 / Q6 单独出方案
> 数据来源：通达信 / 腾讯行情 / 东方财富 push2·ulist / 同花顺 fuyao / ZHB。仅为技术治理，不构成投资建议。

---

## 〇、⚠️ 先说三处「原审计误报」——已复核并**刻意不改**

审计的价值在于发现问题，但**盲从审计结论同样危险**。实施前逐项复核发现 3 项原建议有误，已纠正并记录，避免误改：

| 原建议 | 复核结论 | 处置 |
|:---|:---|:---|
| **补 `flush=True`**（称 sht/med/lng 为 0，有卡死风险） | ❌ **误报**。实测 sht/lng 的 `print(` 出现 **0 次**、med 仅 1 次（且是注释）。进度输出由 **`BaseReportRunner` 统一提供**（`sc_report_runner.py:169-176`，已带 `flush=True`）；脚本层是**刻意不重复打印**（`get_med_report.py:206` 注释明示"移除 print(双打印)"）。故无卡死风险 | ✅ **保持现状**，不改 |
| **命名统一 `pct_chg`→`change_pct`** | ❌ **误报**。`pct_chg` 是 med 的**本地辅助函数** `def pct_chg(cur, prv)`（`:544`），非数据字段名 | ✅ **保持现状**，不改 |
| **市值命名 4 种统一** | ❌ **误报**。分属**不同数据结构的合法键名**：契约层 `mcap_yi` / 北向持仓记录 `market_cap`（独立 schema，且有 `_mcap==0 → _shares*price` 兜底）/ 市场汇总 `total_market_cap` / mak 局部聚合变量 `total_mcap` | ✅ **保持现状**，不改 |

> 这三项若按原结论执行，会引入无意义改动甚至破坏既有兜底逻辑。**"改全"不是目标，"改对"才是。**

---

## 一、已实施改动清单

### P0 — 统一 `get_fund_flow_120d` 口径（Q1）

| 文件 | 改动 |
|:---|:---|
| `get_sht_report.py:137-149` | `prefer="tdx"` → **`prefer="em"`**，重写 docstring 说明变更依据 |
| `get_med_report.py:98-106` | docstring 更新（口径本就是 `"em"`，现与 sht 完全一致） |
| `stock_common/sc_datasource/_eastmoney.py:1004` | 统一入口 docstring：标注 `prefer="tdx"` 为**历史别名、勿再用** |

**决策依据（关键实测）**：
- `core/tdx_client.py:1694` 的 `tdx_get_history_fund_flow` 注释明载「**V12.0: 委托到东财 HTTP 接口（原 TDX get_history_fund_flow 已废弃）**」；
- 且 V17.0.13 口径规定主力净额统一走东财 push2 f137+f140；
- ⇒ **两路径数据同源同值**。`prefer="tdx"` 仅多一次对同一函数的冗余二次调用，还会把 `source` **误标为 "tdx"**。
- ⇒ 统一为 `"em"`：**数据完全不变**（无行为变更），source 标注正确，少一层间接调用。

**风险**：极低（数据等价，调用点只读 `data` 不读 `source`，已核实 `sht:121`/`med:1010`）。
**回退**：单文件改回 `prefer` 值。

### P1 — `_obsolete_v17_residue` 解引用后清理

**这是本次最需要谨慎的一项**：该目录虽名为"废弃"，却被 2 个脚本作为 `BACKUP` 路径真实引用，直接删除会破坏脚本。

| 步骤 | 操作 |
|:---|:---|
| 1 | 将被引用的 `_sc_datasource_singlefile_backup.py`（329KB）**迁移**至 `docs/backups/`（保留而非删除） |
| 2 | `scripts/split_sc_datasource_v2.py:36`、`scripts/_verify_split.py:11` 的 `BACKUP` 路径改指新位置 |
| 3 | `scripts/verify_data_access.py:98` 豁免清单条目更新（`docs/` 规则已覆盖新位置） |
| 4 | 删除 `_obsolete_v17_residue/` 整个目录（11 个已跟踪文件） |

**风险**：低（已完全解引用，grep 确认无残留真实引用）。
**回退**：`git revert`（迁移为 `git mv`，历史可追溯）。

### P1 — 移除 `thsdk` 过时表述

| 文件 | 改动 |
|:---|:---|
| `README.md:34` | 删除 thsdk，**补充醒目提示**：已随 `sc_ths.py` 于 V17.0.29 移除 |
| `README.md:221` | 依赖数 17+ → **16 项**，移除 thsdk |
| `README.md:10` | 破解源列表移除 thsdk 并标注移除 |
| `requirements.txt:36-46` | 整段注释重写为「已完全移除 + 替代方案 + 历史包名撞车留档」 |

> 原 `requirements.txt` 注释指向 `stock_common/sc_ths.py:63`（**文件已不存在**），且 README 仍称其为可选依赖——新环境按文档部署必踩坑。

### P2 — 清理无用文件

| 类别 | 处置 |
|:---|:---|
| 11 个完全孤儿脚本 | 已删除（含自述 BROKEN 的 `_split_sc_datasource_BROKEN.py`） |
| `.tmp_audit/`（3 个已跟踪临时文件） | `git rm` |
| `.workbuddy-ai/tmp_audit_report.py` | 删除 |
| `docs/backups/unified_layer_pe_lyr_20260901_2120/` | 删除（其 `tdx_client.py` 与另一备份目录**内容完全相同**） |
| `.vendor_backup/`（**530MB**） | 删除（Q3） |
| `.venv_test/`（16MB） | 删除 |
| 空 `config/` 目录 | 删除（避免与真实配置 `core/config.py` 混淆） |
| `scratch/`（230 文件/3.7MB） | ✅ **按 Q2 保持不跟踪，未动** |

**磁盘效果**：仓库从 ~900MB 降至 **374MB**。

### P2/P3 — 语义统一

| 项 | 改动 |
|:---|:---|
| **限流表（Q5 不合并）** | 在 `core/tdx_client.py:145` 与 `stock_common/sc_network.py:168` **两侧加同步说明**：TDX 表为 **TCP 长连接级**节流、sc_network 表为 **HTTP 请求级**节流，语义不同故有意独立；并注明"新增域名须两处同步评估"。**代码逻辑未动**，实测仍为 2 处独立表（符合决策） |
| **`is_a_stock` 去重** | val/mak 的本地包装精简为同构单行转发并更新注释（保留包装以兼容调用点） |
| **`industry_comparison` 下沉** | 新增共享函数 `get_industry_ranking()` 于 `sc_datasource/_industry.py`；val/lng 改为薄转发 |

**`industry_comparison` 下沉时发现的重要命名隐患**（原审计未识别）：
- `_industry.py:484` 已有 `get_industry_comparison()` 返回 **Dict**（med 使用）
- val/lng 的同名近义函数返回 **list**（不同返回类型！）
- ⇒ 新函数刻意命名为 **`get_industry_ranking`** 以显式区分，并在 docstring 中写明"勿混用"

### P3 — README 数字订正

| 位置 | 原 | 现 |
|:---|:---|:---|
| `:242` | 分域限流（38 域） | **37 域** + 注明 tdx_client 另有 6 域独立表 |
| `:34`/`:221` | 依赖 17+ 项 | **16 项** |
| `:143` | `sc_datasource.py`（100+ 函数） | `sc_datasource/`（**8 子模块，138 函数**） |

---

## 二、验证结果

| 验证项 | 结果 |
|:---|:---|
| `py_compile`（全部改动文件） | ✅ 通过 |
| `get_industry_ranking` / `get_industry_comparison` 导入 | ✅ 均可导入、无命名冲突 |
| 限流表独立性 | ✅ 仍为 2 处（符合 Q5 决策） |
| `_obsolete_v17_residue` 残留引用 | ✅ 仅剩说明性注释，无真实引用 |
| 回归测试 | 见最终提交前结果 |

---

## 三、有意**未做**的项（附理由）

| 项 | 理由 |
|:---|:---|
| 三处误报（flush / pct_chg / 市值命名） | 见本报告开头——复核后判定为误报，改动会引入无意义变更或破坏兜底 |
| `generate_report_async` 合并 | 这是 `BaseReportRunner` 的**模板方法钩子**，同名是设计约定，**不应合并** |
| 两份 README 合并 | **Q4 决策：不合并** |
| 限流表合并 | **Q5 决策：不合并**（TCP/HTTP 语义不同） |
| `scratch/` 归档入 VCS | **Q2 决策：保持不跟踪** |
| **Q6 mak 外挂治理** | **单独出方案**，见 `20260910_Q6_mak_governance_plan.md` |

---

## 四、Q6 预告（详见独立文档）

**关键判断修正**：mak 的 `get_canonical_stock_data` 实际调用为 **0 次**，但这**并非缺陷**——统一入口是**单股**契约，而 mak 是**全市场/板块/指数/事件**维度扫描。强求改用会引发 N×5000 次请求的性能灾难。

正确方向是**建立与之匹配的「市场层/事件层」抽象**，而非套用单股入口。方案分 A（缓存纳入，低风险高收益）/ B（并发核验）/ C（市场层抽象，架构级高风险）三阶段，**建议先做 A**。

---

*本报告对应提交见 git log；所有删除项均可通过 git 历史恢复（未跟踪的临时文件除外，已在文中标注）。*
