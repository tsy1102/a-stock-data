# R1–R3 核查报告（2026-08-28）

> 背景：用户要求「修 R1–R3（含回归验证）」。经核查，roadmap.md（V17 架构升级规划，行 434/438/439）
> 对 R1–R3 的描述是基于 **V16.2.4 静态分析、V17.0 大重构之前** 的代码形态写的，而 V17.0（2026-08-13）
> 已实质性吸收了这三项。本文档为「先核查再定」的结论，未改动任何核心文件。
>
> 注意：文档里存在**两套互相矛盾的 R1–R3 编号**：
> - `session_notes/20260813.md` 的 R1–R3（ts 统一 / 进程间隔 / S7 composite）= **已完成** 的 V17.0 第二轮项；
> - `roadmap.md` 的 R1–R3（execute_pipeline 抽取 / with_fallbacks 装饰器 / 字段 dispatch dict）= 本文核查对象，标「未做」但已过时。

## 结论速览

| 项 | roadmap 原描述 | 当前实际状态 | 结论 |
|:---:|:---|:---|:---|
| **R1** | 三报告 execute_pipeline 模板抽取（sht/med/lng ~250 行 → `BaseReportRunner._run_batch`） | 已被 V17.0 R4 `execute_batch_pipeline` 吸收；三脚本 execute_pipeline 现为 8–40 行薄包装 | **已完成（被吸收）** |
| **R2** | with_fallbacks 装饰器（data_provider 15 个 fallback 函数 ~600 行 → 装饰器） | 原「15 个独立 fallback 函数」形态已不存在；fallback 在 V17.0 收敛进 `get_canonical_stock_data` 单体内联链 | **前提已失效 / 不适用原写法** |
| **R3** | data_provider 字段分发 if/elif（~80 行）→ dispatch dict | 无 if/elif 字段分发链；已是集合成员判定（`REQUIRES_REALTIME_HTTP` / `ZHB_SUFFICIENT` frozenset） | **前提已失效 / 已近似 dict** |

## R1 核查

- `stock_common/sc_report_runner.py:107-217` — `BaseReportRunner.execute_batch_pipeline(...)`，约 111 行，提供完整批量骨架：
  GD 早 init、`clean_codes`、批量 prefetch 钩子、`asyncio.Semaphore(3)` worker 循环、逐只 GD 上传、异常捕获、快照保存、汇总打印。
- 三脚本现状（薄包装，无重复批量逻辑）：
  - `get_sht_report.py:1961` — 构建 ind_comp / 指数行情 / HSGT 缓存 + `_prefetch` + `_prefetch_async` 钩子，调用 `execute_batch_pipeline`（~40 行含钩子装配）。
  - `get_med_report.py:1286` — ~9 行，缓存 ind_comp + 快照，调用 `execute_batch_pipeline`。
  - `get_lng_report.py:1306` — ~8 行，同形。
- **R1 = 已完成**。原 ~250 行重复已被 `execute_batch_pipeline` 吸收，原 110 行本地实现已删除（见各脚本注释 V17.0 R4）。

## R2 核查

- `grep with_fallbacks / def with_ / decorator / @` 于 `core/data_provider.py` → **零命中**，无 fallback 装饰器。
- 原「15 个 fallback 函数 / ~600 行」已不反映现实。`get_canonical_stock_data`（`data_provider.py:351-1363`，约 1012 行）是**单体内联分层 fallback 链**，而非 15 个函数：
  - 行情块 `:396-520`：批量预取(push2delay) → L1 TDX → L2 腾讯 → L3 push2delay → L3 push2。
  - 腾讯 extras 补 `pe_ttm/roa/roe_deduct_ttm`（`:491-505`）；fuyao 估值兜底（`:510+`）。
  - 后续逐字段兜底（`:1012/1014/1183` eps/industry 等）。
  - 实际数据源：zhb / push2delay / tdx / tencent / push2 / fuyao（无 sina）。
- 小型公共 getter（`get_stock_price` / `get_change_pct` … `:1516-2044`）仅调用 `get_canonical_stock_data` + 取字段，fallback 已集中。
- **判定**：`with_fallbacks` 装饰器**不安全 / 不适用**——fallback 链存在跨字段依赖（批量命中短路 TDX；腾讯/fuyao 补 TDX 缺失的估值），强行装饰需重构整个 ~1000 行单体。若硬做，改动面 ~1000 行，**高风险**。

## R3 核查

- 无字段名 if/elif 分发链。分发机制为**集合成员判定**：
  `REQUIRES_REALTIME_HTTP` / `ZHB_SUFFICIENT` frozenset（`data_provider.py:183-260`）+ `is_realtime_http_field` / `is_zhb_sufficient_field`（`:252 / :257`）。
- 不存在「字段 → 数据源/优先级」单一映射函数；路由在 `get_canonical_stock_data` 内联决定（ZHB 优先、4 行情字段走实时链、估值走腾讯/fuyao）。最接近的是 `_extract_with_source`（`:688`）。
- **判定**：dispatch dict *可* 把字段→源优先级集中化，但当前已是 set + 逐字段内联，转换改动面 ~200+ 行，**中高风险**（跨字段耦合）。

## 回归测试现状（R1–R3 影响面）

现有相关测试：

- `tests/core/test_core_routing.py` — 覆盖 `get_canonical_stock_data`（dataclass 返回、`force_realtime`、TDX/腾讯/东财全抛 → 降级 ZHB）。**这是 R2/R3 的关键守卫。**
- `tests/data/test_data_prefetch.py` — `prefetch_quote_batch`（R1 prefetch 钩子）。
- `tests/data/test_data_zhb.py` — 5 个 ZHB 本地函数。

**缺口（真问题）**：`tests/README.md:30 / :53` 引用 `reports/test_report_runner.py`（ReportRunner 基类 / 5 大 Runner 防退化），但**该文件不存在**（find 无结果）。R1 无专职测试，仅 README 意图。roadmap 风险列已注明「需 test_report_runner 扩充」——至今未补。

## 回归验证（含回归验证）

环境：文档化入口 `scripts/run_tests.ps1` 硬依赖系统 Python 3.12（本环境缺失），故用受管 Python 3.13.12
建 venv（`numpy` 放开到 `>=2.0` 以拿到 cp313 轮子；`pandas 2.3.3` / `pytest 9.1.1` / `aiohttp` / `easy-tdx` 等已装），
跑 `skip_real`（跳过 real_network 标记）模式。

**R1–R3 影响面（3 个文件，62 用例）—— 已跑，全过：**
```
tests/core/test_core_routing.py   14 passed   (get_canonical_stock_data — R2/R3 关键守卫)
tests/data/test_data_prefetch.py   3 passed   (prefetch_quote_batch — R1 prefetch 钩子)
tests/data/test_data_zhb.py       45 passed   (5 个 ZHB 本地函数)
─────────────────────────────────────────────
62 passed in 37.51s
```

**全量回归（tests/，skip_real）—— 已跑，全过：**
```
269 passed, 45 deselected (real_network 标记，离线跳过), 0 failed in 60.63s
```
（45 个 deselected = real_network 集成测试，离线模式按设计跳过；末尾 `safe-delete` 警告是 pytest
临时目录清理的网络路径提示，无害；1 个 SyntaxWarning 是测试文件 docstring 里的转义字符，无害。）

> 说明：当前工作树改动仅为文档 + `core/data_provider.py` 一处 docstring 修正（V17.0.10 字段破解），
> 未触碰任何运行时逻辑；全量 269 用例 0 失败即确认「无回归」基线。

## 最终结论（待用户决策）

- R1 已被 V17.0 R4 吸收（完成）；R2/R3 前提已过时（不适用原写法）。
- 回归基线：269 passed / 0 failed（skip_real），R1–R3 影响面 62 passed 包含在内。
- **建议走 B 路径**：更正 roadmap 行 434/438/439 的「未做」标注（实际已被吸收/前提失效）+ 补 R1 专职测试
  `reports/test_report_runner.py`（roadmap 早已指出、至今缺失的真缺口），不写/少写新代码。
- 若坚持字面做 R2+R3（路径 A），会触碰 `get_canonical_stock_data` ~1000 行核心单体，高风险，建议单独立项评估。

## 总体风险

按 roadmap 字面实现三项重构 **低收益 / 高风险**：
- R1 已完成；
- R2/R3 前提已过时（V17.0 改写了原结构）；
- 任何「字面」重写都会破坏 V17.0.x 精心调校的 fallback 顺序与跨字段补值逻辑（如 `:496-498` pe_dynamic 修复、`:491` 盘后 fuyao 兜底均依赖当前内联结构）。

## 建议

1. **更正文档**：把 roadmap 行 434/438/439 标「未做」改为「已被 V17.0 R4 / 单体收敛吸收（前提失效）」，消除误导。
2. **补 R1 专职测试**：新增 `tests/report_runner/test_report_runner.py`（或 `reports/test_report_runner.py`），覆盖 `execute_batch_pipeline` 骨架与三脚本 execute_pipeline 装配——这是 roadmap 早已指出、至今未补的真缺口。
3. **若仍要字面重构**：R2/R3 需先把 `get_canonical_stock_data` 的 fallback 链拆成「字段→源优先级」数据结构 + 薄执行器，改动面大、建议单独立项评估，不要顺带做。

## 待用户决策

- A. 按 roadmap 字面做 R2+R3（R1 视为已完成，仅补文档标注）——会触碰核心 ~1000 行函数，高风险。
- B. 仅核查 + 更正文档（不写/少写新代码），并补 R1 专职测试；跑回归确认无回归。← 当前已选路径。
- C. R1–R3 是别处定义的（非 roadmap 这套），请贴出具体定义。
