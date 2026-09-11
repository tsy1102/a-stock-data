# 项目健康体检与治理报告（只读分析版）

> 生成时间：2026-09-10 | 项目版本：VERSION=17.2.9 | 活跃 Python 文件：137 个
> **本报告为只读分析，未修改任何文件、未删除任何内容。** 所有结论均附代码行级/命令级依据。
> 数据来源：通达信（easy_tdx）/ 腾讯行情 / 东方财富 push2·ulist / 同花顺 fuyao / ZHB。仅为技术诊断，不构成投资建议。

---

## 〇、执行摘要

项目经多轮迭代后，**架构主干健康，但外围治理滞后**。核心评级：

| 维度 | 评级 | 结论 |
|:---|:---|:---|
| 核心架构 | 🟢 良好 | 5 大脚本统一继承 `BaseReportRunner`，CLI/Banner/上传/清理已收敛；错误处理高度一致（无 bare except、无 `except:pass`） |
| 外围文件治理 | 🔴 差 | 未跟踪文件 230 个（scratch 3.7MB）+ 本地 530MB 备份；已跟踪的"废弃"目录却仍被脚本引用 |
| 文档同步 | 🟡 中 | 4 处可证伪数字失准 + 1 处已删除模块仍被描述为可选依赖 |
| 语义统一 | 🟡 中 | 存在 1 处 **P0 级同名不同口径**（影响分析结论可比性）+ 3 组重复实现 + 2 套并行限流表 |

**最需优先处理的 3 件事**：
1. `get_fund_flow_120d` 同名不同源（P0，直接污染分析结论）
2. `_obsolete_v17_residue` 删除前必须先解引用（否则破坏 2 个脚本）
3. README 中 `thsdk` 描述指向已删除模块（误导新环境部署）

---

## 一、问题分布总览与优先级

### 1.1 数量分布

| 类别 | 数量 | 影响面 |
|:---:|:---:|:---|
| 完全孤儿脚本（代码+文档均零引用） | 11 | 低（不参与运行） |
| 已跟踪的废弃目录 | 1 个（11 文件） | **中（被 2 脚本引用）** |
| 已跟踪的临时文件 | 4 个 | 低 |
| 未跟踪沙盒文件 | 230 个 / 3.7MB | 中（备份缺失风险） |
| 本地大体积备份（已忽略） | 530MB + 16MB | 低（仅磁盘） |
| 重复备份内容 | 2 组（含 2 个完全相同的 `tdx_client.py`） | 低 |
| 死函数（仅定义处出现） | 3 | 低 |
| 文档可证伪失准 | 4 处数字 + 1 处模块 | **中（误导部署）** |
| 跨脚本重复实现 | 4 组 | **中（维护成本）** |
| **同名不同口径** | **1 处（P0）** | **高（结论不可比）** |
| 并行限流表 | 2 套 | 中（风控不一致） |

### 1.2 优先级排序（按对分析结果影响从高到低）

| 优先级 | 问题 | 位置 | 为什么排这个位置 |
|:---:|:---|:---|:---|
| **P0** | `get_fund_flow_120d` 同名不同源 | `get_sht_report.py` vs `get_med_report.py` | 同名函数返回不同口径数据，短线/中线结论**不可横向比较**，属正确性缺陷 |
| **P1** | `_obsolete_v17_residue` 被引用 | `scripts/split_sc_datasource_v2.py:36`、`scripts/_verify_split.py:11` | 名字暗示可删，实际是备份路径；误删即破坏脚本 |
| **P1** | README 描述已删除模块 `thsdk` | `README.md:34/221`、`requirements.txt:37-48` | 新机器按文档部署会踩"同名不同库"的坑（requirements 注释已记录此坑，但 README 仍称可选） |
| **P2** | 两套并行 `_DOMAIN_LIMITS` | `sc_network.py:168`(37域) / `tdx_client.py:145`(6域) | TDX 侧限流**不受统一风控约束**，长期看是封禁风险点 |
| **P2** | `flush=True` 覆盖不全 | sht/med/lng 为 0，仅 val(11)/mak(8) | 子进程 stdout 静默 → 可能触发 `main.py` 900s 卡死保护（与 09-09 val 超时同源风险） |
| **P2** | 11 个孤儿脚本 + `scratch/` 230 文件 | `scripts/`、`scratch/` | 心智负担与误用风险，不影响运行 |
| **P3** | 重复实现去重、命名统一、README 数字订正 | 多处 | 维护性收益 |

---

## 二、【第一步】无用文件排查清单

> 判定方法：程序化扫描 137 个活跃 `.py`，对每个模块/函数统计全仓引用次数；再对"零引用"项检索全部 `.md` 文档确认是否被文档提及。
> **风险分级**：低=可放心删；中=需先解引用或确认；高=勿删。

### 2.1 已跟踪的废弃/临时目录（风险：中～高）

| 文件路径 | 问题类型 | 判定依据 | 删除风险 | 建议动作 |
|:---|:---|:---|:---:|:---|
| `_obsolete_v17_residue/_ARCHIVED_sc_datasource_split_20260904/`（10 文件） | 已废弃模块存档 | 目录名自述 "obsolete"；活跃代码零 import | 🟡 **中** | **不要直接删**。其兄弟文件 `_sc_datasource_singlefile_backup.py` 被下方引用 |
| `_obsolete_v17_residue/_sc_datasource_singlefile_backup.py` | 单文件备份 | **被 `scripts/split_sc_datasource_v2.py:36` 与 `scripts/_verify_split.py:11` 作为 `BACKUP` 变量引用** | 🔴 **高** | **保留**，或先改这两个脚本的 BACKUP 路径再删 |
| `.tmp_audit/mutation_pipeline.py`（104行） | 临时文件却已入版本控制 | 目录名 `.tmp_*`；全仓零引用 | 🟡 中 | 确认无历史价值后 `git rm`；仅影响 VCS 清洁度 |
| `.tmp_audit/scan_sections.py`（36行） | 同上 | 同上 | 🟡 中 | 同上 |
| `.tmp_audit/sections.json` | 同上 | 临时产物 | 🟡 中 | 同上 |
| `.workbuddy-ai/tmp_audit_report.py` | AI 工具临时产物 | 零引用；位于工具目录 | 🟢 低 | 可删（未跟踪，仅本地） |
| `docs/field_verification/20260902/verify_existence_20260902.py` | 一次性验证脚本 | 零引用；日期戳命名 | 🟢 低 | 可删（未跟踪） |

### 2.2 完全孤儿脚本（代码零引用 + 文档零提及，11 个，风险：低）

| 文件路径 | 判定依据 | 建议动作 |
|:---|:---|:---|
| `scripts/_analyze_sc_ds.py` | 全仓 `.py` 零引用、全部 `.md` 零提及 | 删除或移入 `scratch/` |
| `scripts/_audit_probe3.py` | 同上 | 同上 |
| `scripts/_audit_raw_deep.py` | 同上 | 同上 |
| `scripts/_audit_raw_structure.py` | 同上 | 同上 |
| `scripts/_check_reports_sep4.py` | 同上 | 同上 |
| `scripts/_probe_kline_schema.py` | 同上 | 同上 |
| `scripts/_run_round10_cross_source_crack.py` | 同上 | 同上 |
| `scripts/_split_sc_datasource_BROKEN.py` | **文件名自述 BROKEN** + 零引用 | **优先删除**（明确废弃） |
| `scripts/_tx85_diagnose.py` | 零引用（[85] 均价候选已于 09-10 撤销，脚本使命完成） | 删除 |
| `scripts/_tx85_resid.py` | 同上 | 删除 |
| `scripts/_vwap_preview.py` | 零引用（VWAP 定案已完成） | 删除 |

> **说明**：另有 25 个脚本虽 `.py` 零引用但**文档中确有提及**（如 `sync_readme.py` 12 次、`verify_sync_check.py` 13 次、`check_em_health.py` 7 次），属"运维工具"而非死代码，**不建议删除**，应保留并在 README 补登工具清单。

### 2.3 备份与重复内容（风险：低）

| 文件路径 | 判定依据 | 建议动作 |
|:---|:---|:---|
| `docs/backups/unified_layer_20260901_2045/`（含 `tdx_client.py`、`data_provider.py`、`sc_schema.py`、`sc_datasource.py`） | 2026-09-01 拆包前备份，2.0MB，10 个已跟踪文件 | 保留 1 份，删除 `unified_layer_pe_lyr_20260901_2120/` |
| `docs/backups/unified_layer_pe_lyr_20260901_2120/` | **其 `tdx_client.py` 与上一目录的 `tdx_client.py` 内容完全相同**（同 MD5） | 删除（重复） |
| `docs/backups/field_dict_20260901_200657.md`、`field_dict_20260901_2036_pre_fix.md` | 字典历史快照 | 保留（字典体积 572KB，快照有价值） |

### 2.4 未纳入版本控制的构建产物 / 大文件（风险：低，但影响磁盘与备份）

| 路径 | 体积 | 版本控制状态 | 说明与建议 |
|:---|---:|:---|:---|
| `.vendor_backup/` | **530MB** | 已 gitignore（`.gitignore:82`） | venv site-packages 本地保险备份；建议确认无需求后删除 |
| `.venv_test/` | 16MB | 未显式忽略（`venv/`/`.venv/` 规则不覆盖） | 建议加入 `.gitignore` 或删除；`.venv_test/Include` 为空目录 |
| `.mypy_cache/` | 16MB | 已忽略 | 可清 |
| `.pytest_cache/` | 59KB | 已忽略 | 可清 |
| `__pycache__/` | 1.1MB | 已忽略 | 可清 |
| `scratch/` | 3.7MB（230 py / 13 txt / 6 pyc / 6 md / 3 json / 1 log） | **gitignore 仅放行 `scratch/README.md`** | 沙盒定位清晰（README 已说明"用完即弃"），**但全部未跟踪 = 无备份**。建议评估后选择性归档高价值破解脚本 |

### 2.5 死代码（函数级，风险：低）

| 位置 | 函数 | 判定 | 建议 |
|:---|:---|:---|:---|
| `stock_common/sc_ftshare.py` | `get_ft_mainline_cls` | 全仓仅定义处出现 | 确认后删除 |
| `scripts/crack_push2_status_codes.py` | `build_field_index` | 同上（脚本本身为一次性破解工具） | 随脚本处置 |
| `tests/infra/test_infra_f10.py` | `_f10_env` | pytest fixture，仅本文件用 | 保留（fixture 非死代码） |

### 2.6 结构性问题

| 路径 | 问题 | 建议 |
|:---|:---|:---|
| `config/`（根目录空目录） | 与真实配置 `core/config.py` 易混淆 | 删除空目录，避免误以为配置在此 |
| `.venv_test/Include/` | 空目录 | 随 venv 处置 |

---

## 三、【第二步】文档同步核对

### 3.1 已过时 / 错误内容（需订正）

| 文档位置 | 现有表述 | 代码真实状态 | 影响 | 建议动作 |
|:---|:---|:---|:---|:---|
| `README.md:34` 与 `:221` | "`levistock`/`axdata`/**thsdk** 为可选增强，缺失自动降级" | **`thsdk` 已于 V17.0.29(2026-09-07) 完全移除**：`stock_common/sc_ths.py` 文件已不存在，`data_provider.py:555` 与 `sc_fuyao.py:322` 的注释均明确记录"thsdk TCP 网关于 2026-09-07 已移除" | 🔴 高：新环境按 README 部署会去找已不存在的依赖 | **删除 README 中所有 `thsdk` 表述**；同时 `requirements.txt:37-48` 的注释仍指向 `stock_common/sc_ths.py:63`（文件已删），应一并更新 |
| `README.md:242` | "分域限流（**38 域**）" | `sc_network._DOMAIN_LIMITS` 实为 **37 域** | 🟡 中：数字失准 | 改为 37 域，或改为"详见 `_DOMAIN_LIMITS`"避免数字漂移 |
| `README.md:34` / `:221` | "运行时依赖 **17+ 项**" | `requirements.txt` 实际 **16 条**（`grep -cE "^[a-zA-Z]"`） | 🟡 中 | 改为 16 项，或去掉具体数字 |
| `README.md:143` | `├── sc_datasource.py  # 数据源查询模块（100+ 函数）` | **已拆为包** `stock_common/sc_datasource/`（`__init__.py` + 8 个子模块），函数合计 **138 个** | 🟡 中：路径误导 | 改为 `sc_datasource/（8 子模块，138 函数）` |
| `README.md:125-216` 项目结构 | 未包含 `scratch/`、`_obsolete_v17_residue/`、`docs/backups/`、`.workbuddy/` 等 | 实际存在 | 🟡 中：新人困惑 | 补充目录说明表格（含"是否跟踪/是否参与运行"列） |

### 3.2 经核验**正确**的表述（无需修改，避免误伤）

| 表述 | 核验结果 |
|:---|:---|
| "核心参数集中在 `core/config.py`" | ✅ 文件真实存在；`EM_MIN_INTERVAL = 1.0` 位于 `core/config.py:22` |
| "push2 系最严 0.4rps" | ✅ `sc_network.py:175` `rps: 0.4`（`sleep_ms: 2500`） |
| "缓存 DB≤500MB" | ✅ `core/stock_cache.py:199` `_MAX_CACHE_SIZE_MB = 500` |
| "本地交易日历 621 条 2004-2026+" | ✅ `stock_common/stock_calendar.py:840` 注释一致 |
| "4 级 fallback（L0 东财申万二级 → push2 → TDX → ZHB）" | ✅ 与 `data_provider.py` 结构一致 |
| README 提及的 5 个脚本 + `main.py` | ✅ 全部存在 |
| `docs/backups`、`scratch` 的定位说明 | ✅ `scratch/README.md` 已清晰定义"一次性调研沙盒"定位 |

### 3.3 缺失内容（建议补充）

| 缺失项 | 说明 | 建议 |
|:---|:---|:---|
| **双 README 分歧** | 根目录 `README.md` 376 行，`docs/README.md` 64 行，内容不同 | 明确二者关系（建议 `docs/README.md` 加指向根 README 的链接，或合并） |
| **`scratch/` 未跟踪的风险** | 230 个文件 3.7MB 全部未入 VCS，无备份 | 在 README 明确"scratch 不承诺备份"，或建立归档机制 |
| **运维工具清单** | 25 个文档提及的脚本散落在 CHANGELOG/各报告中 | 在 README 增设「运维工具」章节，列出 `sync_readme.py`、`verify_sync_check.py`、`check_em_health.py`、`clean_cache.py`、`field_landing_audit.py` 等及用途 |
| **Python 版本约束** | `README.md:26` / `AGENTS.md:226` 规定强制系统 Python 3.12 | 建议在 README「环境要求」顶部以醒目方式重申（当前散落在文档各处） |
| **`.vendor_backup` 530MB** | 未在任何文档说明 | 补充说明或加入清理指引 |

---

## 四、【第三步】语义与逻辑统一

### 4.1 🔴 P0：同名不同口径（正确性缺陷）

| 项目 | 内容 |
|:---|:---|
| **函数** | `get_fund_flow_120d(code)` |
| **位置 A** | `get_sht_report.py` → `get_history_fund_flow_120d(code, 60, prefer="tdx")`（TDX 优先→东财兜底） |
| **位置 B** | `get_med_report.py` → `get_history_fund_flow_120d(code, 60, prefer="em")`（**仅东财**口径） |
| **影响** | 函数名完全相同，但**数据源优先级相反**。短线与中线报告的"120 日资金流"实质来自不同源，两报告结论**不可横向比较**；且读者会误以为同源 |
| **建议** | ① 保留语义差异，但**重命名以显式化口径**：`get_fund_flow_120d_tdx_pref()` / `get_fund_flow_120d_em_only()`；<br>② 或统一为单一 `prefer`，将口径差异改为参数显式传入（推荐：`get_fund_flow_120d(code, prefer=...)` 在两处显式声明，并在文档注明两报告口径不同的**业务原因**） |
| **风险** | 重命名需同步调用点；**保持对外行为不变**的前提下，建议仅改函数名+更新调用点 |
| **回退** | 单文件改名，git 回滚即可 |

### 4.2 🟡 P1：跨脚本重复实现（3 组）

| 函数 | 出现位置 | 重复性质 | 建议 | 风险/回退 |
|:---|:---|:---|:---|:---|
| `_is_a_stock` | `get_val_report.py`、`get_mak_report.py` | **核心逻辑完全一致**（均 `from stock_common.sc_utils import is_a_stock`） | 下沉为 `sc_utils` 直接调用，或由 `BaseReportRunner` 提供 `self.is_a_stock()` | 低：纯代理函数，删除后改调用点即可 |
| `industry_comparison` | `get_val_report.py`、`get_lng_report.py` | 逻辑近乎一致，仅 docstring 与 `_debug_log` 前缀（`val`/`lng`）不同 | 抽至 `stock_common/sc_datasource/_industry.py`，脚本侧薄封装 | 中：需验证两处返回值键兼容（`leader_name`/`leader` 兼容处理已在 val 注释中提及，勿破坏） |
| `generate_report_async` | `lng`、`med`、`sht` | **Runner 钩子方法**（同名是设计约定，非重复） | ✅ **不建议合并**——这是 `BaseReportRunner` 的模板方法模式 | — |

### 4.3 🟡 P1：两套并行的限流表

| 项目 | `sc_network.py:168` | `tdx_client.py:145` |
|:---|:---|:---|
| 域数量 | **37** | **6** |
| 覆盖 | 全数据源（东财/腾讯/同花顺/新浪/szse/sse 等） | 仅 6 个（`qt.gtimg.cn`、`datacenter-web.eastmoney.com` 等，全部为 sc_network 的**子集**） |
| 是否复用 | — | ❌ 未 import sc_network，独立维护（仅 `from core.config import TDX_MIN_INTERVAL...`） |

**影响**：TDX 侧请求不走统一风控面，长期存在封禁风险；且两表数值若漂移会产生不一致节流。
**建议**：`tdx_client` 改为 import `sc_network._DOMAIN_LIMITS`（需评估 core↔stock_common 循环依赖约束——已知该项目存在此约束且用 lazy import 断环，此处应沿用同样手法）。
**风险**：中。限流改动影响所有 TDX 请求；**必须先在离线环境验证 import 不产生循环依赖**，再灰度。
**回退**：单文件改动，git 回滚。

### 4.4 🟡 P2：stdout `flush=True` 覆盖不全（与 09-09 val 超时同源）

| 脚本 | `print(..., flush=True)` 次数 |
|:---|---:|
| `get_val_report.py` | 11 |
| `get_mak_report.py` | 8 |
| `get_sht_report.py` | **0** |
| `get_med_report.py` | **0** |
| `get_lng_report.py` | **0** |

**影响**：`main.py:321-332` 的卡死保护以"子进程 stdout 连续静默 900s"为判据。sht/med/lng 的长耗时循环若无 flush，输出可能滞留缓冲区 → 主进程误判静默 → 提前 kill（这正是 09-09 val 超时事件的机制）。val 已修复，其余三个**仍是同一隐患**。
**建议**：为 sht/med/lng 的进度打印统一补 `flush=True`。
**风险**：低（仅增加输出刷新）。
**回退**：逐文件回滚。

### 4.5 🟡 P2：命名与术语不统一

| 概念 | 现存用词（脚本分布） | 建议 |
|:---|:---|:---|
| **市值** | `mcap_yi`（全 5 脚本）、`total_mcap`（mak）、`market_cap`（mak/sht/med） | 统一 `mcap_yi`（亿元）为契约名；`total_mcap`/`market_cap` 若为局部变量可保留，若为展示字段应统一 |
| **涨跌幅** | `change_pct`（全 5）、`pct_chg`（**仅 med**） | 统一 `change_pct` |
| **主力净** | `main_net_buy_wan`（sht）、`fund_main_today`（契约层，09-10 已明确主从关系） | 已由 09-10 整改显式化（`main_net_buy_wan ≡ fund_main_today/1e4`），**建议脚本侧统一走 `fund_main_today` 并在展示层换算**，消除双写分叉可能 |
| **换手率** | `turnover`（全 4） | ✅ 已统一 |

### 4.6 🟢 P3：错误处理与日志（整体健康，仅轻微不一致）

**积极结论**：5 大脚本错误处理高度一致——
- 无 `bare except`（全仓 0 处）
- 无 `except Exception: pass`（全仓 0 处）
- 主导模式为 `except Exception → _debug_log`（val 23 / mak 30 / sht 27 / med 11 / lng 23）

**轻微不一致**：
| 项目 | 现状 | 建议 |
|:---|:---|:---|
| `_debug_log` 导入方式 | `sht`/`lng` 显式 `from stock_common import ... _debug_log ...`；`val`/`mak`/`med` 依赖包级隐式导出 | 统一为显式导入（可读性 + 避免包 `__init__` 变更时的隐性失效） |
| 日志框架 | 5 大脚本全部使用 `print`，**零 `logging`**；而 `sc_network` 有 `_fallback_logger` | 建议报告脚本的关键事件（超时降级、源降级）也接入统一 logger，便于审计 |

### 4.7 🟢 P3：数据流转（整体受控）

- 统一入口 `get_canonical_stock_data` 调用次数：lng 9 / val 6 / sht 4 / med 3 / mak 1 —— **mak 仅 1 次，外挂最重**（与 09-10 审计结论一致）
- 绕过统一层的直连 `tdx_get_*` 调用：val 13 / mak 12 / lng 12 / sht 10 / med 8 —— 属行情/板块类取数的合理直连，但建议登记纳管
- 无 `requests.get/post` 直连（全部走 `sc_network`）✅ 良好

---

## 五、改动风险与回退方式总表

| # | 改动项 | 优先级 | 风险 | 回退方式 | 前置依赖 |
|:---:|:---|:---:|:---:|:---|:---|
| 1 | `get_fund_flow_120d` 口径显式化（改名或参数化） | P0 | 中 | 单文件 git 回滚 | 需确认 sht/med 口径差异是**有意设计**还是历史遗留 |
| 2 | 解引用后再删 `_obsolete_v17_residue` | P1 | 高 | 删除前先改 `split_sc_datasource_v2.py:36` 与 `_verify_split.py:11` 的 `BACKUP` 路径 | **必须先解引用** |
| 3 | 删除 README/requirements 中 `thsdk` 表述 | P1 | 低 | git 回滚 | 无 |
| 4 | `tdx_client` 复用统一限流表 | P2 | 中 | 单文件回滚 | 验证 core↔stock_common 无循环依赖 |
| 5 | sht/med/lng 补 `flush=True` | P2 | 低 | 逐文件回滚 | 无 |
| 6 | 删除 11 个孤儿脚本 + `_split_sc_datasource_BROKEN.py` | P2 | 低 | git 回滚（未跟踪的 scratch 类需先备份） | 无 |
| 7 | 清理 `.tmp_audit`（已跟踪） | P2 | 低 | git 回滚 | 无 |
| 8 | 合并重复备份目录 | P3 | 低 | git 回滚 | 无 |
| 9 | `_is_a_stock` / `industry_comparison` 下沉 | P3 | 中 | 单文件回滚 | 验证 `leader_name`/`leader` 键兼容 |
| 10 | 命名统一（`pct_chg`→`change_pct` 等） | P3 | 中 | 全局搜索替换 + 单测 | 需确认无外部依赖这些键名 |
| 11 | README 数字订正（38→37 域、17+→16 项、sc_datasource 包化） | P3 | 低 | git 回滚 | 无 |
| 12 | 清理 `.vendor_backup`(530MB) / `.venv_test` | P3 | 低 | 删除前确认无回滚需求 | 确认不需要回滚到旧 site-packages |

---

## 六、待确认项（不臆测，需你决策）

| # | 事项 | 为什么必须问 |
|:---:|:---|:---|
| **Q1** | `get_fund_flow_120d` 在 sht(tdx优先) 与 med(仅东财) 的口径差异，是**有意设计**（短线要 TDX 实时、中线要东财历史一致性）还是**历史遗留**？ | 决定 P0 改法是"改名显式化"还是"统一口径"；若是有意设计，改名即可，不改行为 |
| **Q2** | `scratch/` 230 个未跟踪文件中，是否有**高价值破解脚本需要归档入 VCS**？ | 决定是"整体保持不跟踪"还是"选择性归档"；误删会丢失数月破解成果 |
| **Q3** | `.vendor_backup/` 530MB 是否仍有回滚价值？ | 决定可否释放磁盘 |
| **Q4** | `docs/README.md`（64 行）与根 `README.md`（376 行）**谁是权威**？ | 决定是合并还是加交叉引用 |
| **Q5** | `tdx_client` 独立限流表(6域)是否有**特殊业务原因**（如 TDX TCP 长连接与 HTTP 节流语义不同）？ | 若确有特殊原因，则不应合并，改为在两表间加同步注释 |
| **Q6** | `mak` 外挂 12+ 数据源且统一入口仅调用 1 次，是否计划专项治理？ | 这属架构级改造，本次仅登记不实施 |

---

## 七、结论

**架构主干无需大改**——`BaseReportRunner` 抽象、统一数据入口、分域限流、错误处理规范均已建立且执行良好。真正需要治理的是**外围**：11 个孤儿脚本、230 个未跟踪沙盒文件、530MB 本地备份、以及 4 处失真的文档数字。

**唯一影响分析正确性的缺陷是 P0 的 `get_fund_flow_120d` 同名不同口径**，建议优先处理。

**最危险的"看似可删"项是 `_obsolete_v17_residue`**——它被 2 个脚本作为备份路径引用，直接删除会造成真实破坏。这印证了本次"先只读分析、后确认落地"的必要性。

---

*本报告基于 137 个活跃 Python 文件、9 个文档目录的程序化全量扫描生成，所有结论均附行级依据。*
*数据来源：通达信 / 腾讯行情 / 东方财富 push2·ulist / 同花顺 fuyao / ZHB。仅供技术治理参考，不构成投资建议。*
