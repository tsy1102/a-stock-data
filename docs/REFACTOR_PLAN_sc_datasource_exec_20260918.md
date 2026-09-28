# 架构重构方案：`sc_datasource` 去 exec 注入（单独核准稿）

> 关联审计：`docs/AUDIT_REPORT_20260918.md`（本报告为其"架构风险"专项落地方案）
> 数据来源：通达信/同花顺/东方财富；本方案为工程重构，不涉及任何投资建议。

---

## 0. 为什么这是"最核心"的问题

`stock_common/sc_datasource/__init__.py` 末尾（约 833–841 行）用一段 `exec` 把 9 个 `_*.py` 源片段**逐行注入包共享 `globals()`**：

```python
_PKG_ORDER = ('_holders', '_official_backup', '_eastmoney', '_quotes',
              '_industry', '_financials', '_pools', '_zhb', '_misc')
for _mod in _PKG_ORDER:
    _fp = _os.path.join(_PKG_HERE, _mod + '.py')
    with open(_fp, encoding='utf-8') as _fh:
        _src = _fh.read()
    exec(compile(_src, _fp, 'exec'), globals())
```

源片段本身不是可导入模块，只是"载入命名空间的源码"。这带来三类系统性隐患：

1. **静态分析全员失明**：pyflakes 在该子系统报出 **1090 个 `undefined` 误报**（上一轮审计已据此过滤）。真实 bug（如本次修复的 3 处 `NameError`）会被淹没；IDE/类型检查/重构工具完全失效。
2. **不可独立单测**：任一片段依赖全包共享 `globals`，无法单独 import、单独测试，必须拉起整个取数底座（连带网络层副作用）。
3. **脆弱的共享命名空间**：任何片段都能在共享 `globals` 里静默覆盖另一个片段的名字，无封装、无边界，删改一个片段是高危操作。

设计者当初选择 `exec` 是为了两个诉求（见文件 827–832 行注释）：
- **状态只有一份**：模块级缓存/锁在共享 `globals` 中单实例；
- **mock.patch 可穿透**：打在 `sc_datasource.X` 的补丁对包内跨函数调用同样生效。

**重构目标 = 消除 exec，同时保住这两个诉求。**

---

## 1. 依赖图谱量化（本次只读分析得出，作为方案依据）

用 AST 扫描 9 个片段的"本片段未定义却被使用"的符号，再把每个外部符号映射回来源。结论：

- **跨片段符号边约 50 条**：每片段依赖兄弟片段 1–22 个符号（如 `_eastmoney`→`_financials` 9 条、`_industry`→`_financials` 8 条、`_financials`→`_eastmoney` 7 条）。
- **存在真实循环依赖**（仅统计"确在兄弟片段定义"的名字，结构可靠、无假阳性）：
  - 最紧双向环：`_financials ↔ _official_backup`
  - 典型环：`_misc → _eastmoney → _industry → _misc`、`_eastmoney → _industry → _zhb → _eastmoney`
  - 长环：`_holders → _misc → _eastmoney → _industry → _zhb → _quotes → _financials → _holders`

**关键推论：不能按依赖拓扑序逐片段改造（有环）**。必须先用共享状态提取打断"状态环"，再用"调用点懒导入"打断"代码环"。

> 注：扫描报告的 `unknown` 列表含大量函数内局部变量（`c/i/k` 等循环变量、参数），属分析器未追踪 intra-function 局部导致的噪声，**不影响上面的边/环结论**；精确逐名映射在阶段 0 细化。

---

## 2. 目标与非目标

**目标（Go）**
- 移除 `__init__.py` 的 `exec` 注入块，使 9 个 `_*.py` 成为标准可导入子模块。
- 恢复 pyflakes/vulture/IDE 对该子系统的可见性（误报应从 ~1090 降到近 0，残余仅动态符号）。
- 保留"模块级状态单实例"与"mock 可穿透"两大原始诉求。
- 对外公开 API 面 `sc_datasource.<func>` **调用方零改动**。

**非目标（No-Go）**
- 不重构 `sc_network` / `sc_utils` / `core.stock_cache`（它们已是正规模块）。
- 不改动 `get_*/core/data_provider` 等消费方的 import 路径。
- 不借机重写业务逻辑、不调整缓存/TTL 策略、不改动网络层。

---

## 3. 推荐方案：共享状态模块 + 显式导入 + 循环边懒导入

### 3.1 阶段 0 — 精确依赖映射（降低后续一切风险）
- 在现有 AST 扫描基础上，补追踪函数内局部名（参数、循环变量、`with`/`for` 目标），过滤噪声，产出**逐片段"需从兄弟片段导入的符号清单"**（精确到名）。
- 输出 `cache/sc_datasource_import_map.json`（片段→符号→来源模块），作为后续每步的"导入 checklist"。
- **验收门**：清单可人工逐条复核；与人工抽样一致。

### 3.2 阶段 1 — 提取 `_shared.py`（打断"状态环"）
- 新建 `stock_common/sc_datasource/_shared.py`，收纳当前散落在 `__init__.py` 顶层的**跨片段共享可变状态**：约 40+ 项，如 `_EM_BATCH_CACHE/_EM_BATCH_CACHE_DATE`、`_PROFIT_FORECAST_CACHE/_PROFIT_FORECAST_INDEX*`，`_HOLDER_CACHE_TTL/_HOLDER_CACHE_REFRESH`、`_DC_PREFETCH_FUTURES`、`_KPL_*`、`_FFLOW_HOSTS`、`_ULIST_BATCH_*`、`_EM_L2_*`、`_ZHB_*_FIELDS`、`_TDXHY_CACHE` 等。
- 各片段改为 `from ._shared import _EM_BATCH_CACHE, ...`，引用同一份对象 → **仍单实例**（保住诉求①）。
- **验收门**：`python -c "import stock_common.sc_datasource._shared"` 成功；该模块无业务逻辑、仅状态。

### 3.3 阶段 2 — 逐片段改显式导入（每片段一 commit）
- 对每个片段：
  - 顶部补 `from typing import Any, Dict, List, Optional, Tuple`、标准库 `from datetime import datetime, date, timedelta` 等**显式导入**（根除 `date(` 这类裸名隐患，见已修 BUG-3）。
  - 外部模块依赖改为显式：`from stock_common.sc_network import em_get, _quick_request, ...`、`from stock_common.sc_utils import _load_settings, _safe_float, ...`、`from core.stock_cache import TTL, cached, make_valid_if`。
  - 兄弟片段依赖按阶段 0 清单 `from ._eastmoney import get_xxx` 等。
  - **循环边用函数内懒导入**打断：`def f(): from ._official_backup import g; return g()`（行为等价于原 exec 命名空间——名字在函数*运行*时才解析，故调用点懒导入完全等价，且天然破环）。
  - 删除 `# flake8: noqa: F821`。
- 提交顺序：**先改低耦合/被依赖少的片段试水**（如 `_misc`、`_official_backup`），再改核心（`_eastmoney`、`_financials`、`_industry`）。
- **验收门（每片段）**：`python -c "import stock_common.sc_datasource"` 全包可导入；`pyflakes` 该片段 0 个 F821 真告警。

### 3.4 阶段 3 — `__init__.py` 去 exec、改 re-export
- 删除 833–841 行 `exec` 循环 + 相关 `_os/_PKG_ORDER` 清理。
- 改为确定性公开 API 再导出（维持 `sc_datasource.<func>` 不变）：
  ```python
  from ._eastmoney import get_em_batch_quotes, ...   # 显式列出公共函数
  # 或 from ._eastmoney import *（配 __all__）
  ```
- 保留 `from ._shared import *` 让共享状态仍可通过 `sc_datasource._X` 访问（兼容现有 `mock.patch('sc_datasource._X')` 旧测试，过渡期）。
- **验收门**：全包 import 成功；`dir(sc_datasource)` 含全部原公开函数。

### 3.5 阶段 4 — mock 契约迁移 + 全量回归
- 全局搜索 `mock.patch('stock_common.sc_datasource.`（旧补丁目标），改为 patch **定义所在真实模块**（`sc_datasource._eastmoney.foo` / `sc_network._quick_request` 等）——标准 Python 实践，且因阶段 2 用调用点懒导入，**定义点 patch 对所有调用方穿透**（保住诉求②）。
- 跑现有 `tests/` 全量；新增冒烟测试：`import sc_datasource` 后断言关键函数存在且 callable、无 `exec` 残留（grep 断言）。
- 跑一次真实报告产物（mak/val/sht 各一）与改造前 commit 字节级/语义 diff，确认**关键数值字段不因重构变化**（缓存键、主力净额、涨停池等）。
- 重跑 pyflakes/vulture 全项目，确认 `sc_datasource` 误报归零。
- **验收门**：tests 全绿；报告产物 diff 仅含非数值的无关差异（或无差异）；pyflakes sc_datasource 无 F821。

---

## 4. 关键技术决策（待您确认/补充）

| 决策点 | 推荐 | 备选 | 影响 |
|---|---|---|---|
| 循环依赖处理 | 调用点函数内懒导入 | 抽"公共helper"模块彻底去环 | 懒导入改动最小、行为等价；抽公共模块更彻底但改动大 |
| 共享状态位置 | 集中 `_shared.py` | 各状态归其主片段模块 | `_shared.py` 最贴合"单实例"语义、改动集中 |
| mock 穿透 | 改测试 patch 到定义点 | 保留 `__init__` 薄包装委托 | 定义点 patch 是 Python 标准，长期更优 |
| 公开 API | `__init__` 显式 re-export | `import *` + `__all__` | 显式更安全（避免误暴露私有符号） |

---

## 5. 风险与回滚

- **改动面极大**：该包 68+ 函数，被 `get_*/core/data_provider` 等广泛 import，是全局取数底座 → 任何回归都是全局性的。
- **循环依赖隐蔽**：若阶段 0 映射有漏，阶段 2 会出现 `ImportError` 环，需回退该片段 commit 重做。
- **回滚机制**：每阶段独立 commit（非 squash），任一步炸裂可 `git revert` 单步；exec 版始终留在 git 历史可对照。阶段 2/3 之间**不允许保留"半 exec 半 import"中间态**——每个 commit 必须 `import sc_datasource` 通过。
- **不删任何业务逻辑**：仅改导入形态与状态归属，函数体原则上逐字保留。

---

## 6. 验收标准（全部满足方可视为完成）

1. `git grep -n "exec(compile" stock_common/sc_datasource/` 无结果。
2. `python -c "import stock_common.sc_datasource"` 成功，且 `pyflakes sc_datasource` 在该子系统 **0 个 F821 真告警**（残余仅动态符号如公式 `eval` 目标）。
3. 现有 `tests/` 全绿；新增冒烟测试通过。
4. 改造前后各跑一份 mak/val/sht 报告，关键数值字段（主力净额、涨停池、缓存命中）**语义一致**。
5. 外部消费方 import 路径零改动（grep 确认无 `sc_datasource` 调用点需改）。

---

## 7. 待您核准的事项

1. **是否采用推荐方案（阶段 0–4）**？还是倾向更保守的"最小改动"（保留 exec 仅加 noqa + 文档化，不消除根因）？
2. **阶段 2 的循环处理**采用"调用点懒导入"（推荐）还是"抽公共 helper 模块"？
3. **执行节奏**：是否按阶段 0→4 顺序逐 commit 推进（每阶段我完成即提交、不停下来等您），还是每阶段完成后都停下等您复核再进下一阶段？
4. **工作量预期**：约 50 条跨片段导入 + 40+ 共享状态迁移 + 9 片段改造 + 测试迁移，预计多 commit、需一阵子；是否接受分批提交（推荐，降低单次爆炸半径）？

> 核准后我即从阶段 0 开始执行；未核准前本方案不落地任何代码改动。
