# a-stock-data 全项目代码审计报告

- **审计日期**：2026-09-18
- **审计范围**：根目录报告脚本、core/、stock_common/(含 sc_datasource)、scripts/(排除 tests/、docs/、cache/)
- **代码规模**：约 135 个 .py、~7.8 万行(含 tests/docs)
- **工具链**：pyflakes 3.4.0(语法/未定义名/未用导入) + vulture 2.16(死代码)
- **数据来源标注**：通达信/同花顺/东方财富多源；以下结论均不构成投资建议

---

## 一、方法论与误报过滤

| 工具 | 原始告警 | 过滤后有效 |
|------|---------|-----------|
| pyflakes | 1273 行 | undefined 1098 → 筛除 exec 片段 1090，剩 **8 条真 bug 候选**；加未用导入 110、未用局部变量 23、重定义 12、f-string 24 |
| vulture | 162 条 | 筛除 exec 片段后 157 条死代码候选 |

**关键误报源**：`stock_common/sc_datasource/*` 8 个文件被 `sc_datasource/__init__.py` 用 `exec` 注入**包共享命名空间**(文件头 `# flake8: noqa: F821` 已声明)。pyflakes 在这些"片段"里报的 1090 个 `undefined name` 全部来自跨片段共享的 `globals()`,属**系统性误报**,非 bug。但此 `exec` 模式本身是**架构风险**(见第三节)。

---

## 二、🔴 确认的运行时崩溃 Bug(3 处,均已核实位于可达路径)

均为**未定义名被直接引用**且无 `from __future__ import annotations` 兜底,执行到该分支即抛 `NameError`。

### BUG-1【P1】`get_mak_report.py:313` — `_main_net_map` 未定义
- **位置**：`_get_zhb_market_data()`(async,定义于 218 行,被 169 行调用 → **可达**)
- **现象**：
  ```python
  "main_net_amount": (
      _main_net_map[code] if code in _main_net_map   # ← 未定义
      else (_safe_float(stat.get("main_net_buy_amount", 0)) or 0) * 1e4
  ),
  ```
- **根因**：同文件第 38 行定义全局 `_MAIN_NET_MAP_GLOBAL`、188 行填充、780/1353 行均正确引用。313 行用的是小写旧变量名 `_main_net_map`,疑似重构残留。
- **影响**：A 段个股循环每只要构造 `main_net_amount` 即 `NameError`。若被上游 try 吞掉,则 A 段主力净额字段静默缺失 → **数据质量退化**;若未捕获则 A 段整体失败。
- **修复(一行)**：`_main_net_map` → `_MAIN_NET_MAP_GLOBAL`(两处,313 行 `if code in` 与索引处)。

### BUG-2【P1】`get_sht_report.py:1697` — `is_fuyao_enabled` 未导入
- **位置**：个股短线报告 异动解读(fuyao AI)段(1693-1705),**每只股都走此路径 → 可达**
- **现象**：
  ```python
  from stock_common import get_fuyao_anomaly as _f_ano
  if is_fuyao_enabled():          # ← 未导入
  ```
- **根因**：顶部 `from stock_common import (... get_fuyao_anomaly ...)`(55-56 行)未含 `is_fuyao_enabled`;`stock_common/__init__.py` 已导出该函数(154/375 行),`get_mak_report.py` 亦用 `from stock_common import ... is_fuyao_enabled as _f_lad_on` 正确引用。
- **影响**:th 报告的 fuyao 异动解读块必抛 `NameError`。
- **修复(一行)**：`from stock_common import get_fuyao_anomaly as _f_ano` → `from stock_common import get_fuyao_anomaly as _f_ano, is_fuyao_enabled`

### BUG-3【P1】`stock_common/stock_calendar.py:905 / 915` — `date` 未定义
- **位置**：`_load_zhb_neednote_supplement()`(定义 886 行,被 946 行调用 → **可达**)
- **现象**：`supplement_holidays.add(date(year, month, day))`(905/915 行)
- **根因**：文件仅 `import datetime`(16 行),无 `from datetime import date`,裸 `date(...)` 未定义。
- **影响**:ZHB 休市补充日历加载必抛 `NameError`,补充节假日/交易日失效。
- **修复(一行,二选一)**：`date(` → `datetime.date(`;或在函数/模块顶部加 `from datetime import date`。

> 以上 3 处均为"变量/函数名写错或漏导入"类历史遗留缺陷,修复均为单行、零逻辑改动、低风险。

---

## 三、🟠 架构风险:`sc_datasource` 的 exec 命名空间注入

- `stock_common/sc_datasource/_eastmoney.py` 等 8 文件**非独立模块**,由 `__init__.py` 用 `exec(open(...).read())` 注入包 `globals()`,跨文件共享状态。
- **后果**:
  1. 静态分析(pyflakes/vulture/IDE)对跨片段引用**完全失明** → 本次 1090 个 undefined 即此,未来真实 bug 也会被淹没。
  2. `exec` 片段无法独立单测、重构易踩坑、命名污染。
- **建议(中长期)**:逐步改为显式 `from ._eastmoney import eastmoney_datacenter` 等正常导入;至少给每个片段配 `# flake8: noqa: F821` 之外的类型桩,降低维护风险。

---

## 四、🟡 死代码(vulture,已排除 exec 片段)

157 条候选,按类型:未用函数 68、未用变量 67、未用属性 9、未用方法 6、未用导入 5、未用 property 1、未用类 1。

**重要提示**:本仓库大量使用**动态分发**(字符串公式 eval、getattr、注册表),vulture 对"被动态引用"的符号会**误判为死代码**。以下分组需人工二次确认,**不要无脑删**:

| 模块 | 候选死代码 | 误报风险 | 备注 |
|------|-----------|---------|------|
| `stock_common/sc_ta_core.py` | ~40 个 TA 函数(DIFF/SUM/STD/HHV/LLV/EMA/SMA/MACD…) | **高** | 典型技术指标库,大概率被公式引擎 `eval` 按名调用 |
| `stock_common/sc_schema.py` | ~30 个未用属性/变量(fund_main_today 等) | **高** | 字段 schema 默认值,可能经 `getattr`/动态键访问 |
| `core/zhb_client.py` | ~15 个未用方法(get_high_52w/get_ah_stocks…) | 中 | 部分属公开 API 面,可能被外部脚本调用 |
| `core/data_provider.py` | 5 个未用函数 | 中 | `is_zhb_*`/`get_zt_streak_info` 等疑似重构残留 |
| `core/tdx_client.py` | `set_cached_kline` 重定义 3 次、`_market_from_code` 未用 | 中 | 重定义需确认是否覆盖旧逻辑 |
| `core/tdx_client.py:1144` `signum`、`:3051` `sort_by_change` | 未用局部变量(**100% 置信**) | 低 | **高置信真死变量**,可直接删 |
| `stock_common/sc_fault_tolerance.py:71/139` | `try_acquire`/`call_async` 未用方法 | 低 | 疑似熔断器的废弃接口 |

> 死代码清理属 P2(体验/可维护性),建议在确认非动态引用后再删,且**不要**纳入本次紧急修复。

---

## 五、⚪ 良性告警(非 bug,勿改)

- **`Dict`/`Tuple` 等 typing 名 undefined(eltdx_adapter.py:427、backtest_topn.py:348 等)**:相关文件有 `from __future__ import annotations`,注解不求值 → **误报**。
- **f-string is missing placeholders(24 处)**:`f"xxx"` 无 `{}`,仅为多余 `f` 前缀,字符串本身正确,属**无害整洁问题**(如 `get_lng_report.py:282`)。
- **`print(...)` 985 处**:绝大多数是 `main.py`/报告脚本的进度/状态日志(`flush=True`),是项目既定日志风格,**非调试残留**。仅个别近似重复(如 `get_val_report.py` 同时存在中文 `▶` 与英文 `[TIMEOUT]` 两行),属轻微冗余,可后续顺手合并。

---

## 六、遗留标记统计(已知技术债)

| 标记 | 数量 | 说明 |
|------|------|------|
| `print` 残留 | 985 | 多为正当日志(见上) |
| `TODO` | 66 | 前瞻性计划,非皆 bug |
| `XXX` | 29 | 需关注 |
| `FIXME` | 19 | 已知待修 |
| `HACK` | 5 | 临时绕过 |
| `WORKAROUND`/`临时` | 5 | 临时方案 |

> 这些标记本身是"已知债"的清单,不在本次修复范围;建议未来专项清理。

---

## 七、结论与建议

1. **立即修复(3 处 P1 崩溃 bug)**:BUG-1/2/3 均为单行修复、零逻辑改动、低风险,且位于可达路径,建议本轮直接落地(可复用 `PYTHON=py git commit` 闸门)。
2. **架构债(sc_datasource exec)**:列为中长期重构项,短期至少在片段内补类型桩。
3. **死代码**:需人工确认动态引用后再清理,勿批量删除。
4. **本次审计产物**:`cache/audit_pyflakes.txt`、`cache/audit_vulture.txt`、`cache/audit_triage2.py`(分析脚本),可留作复跑基线。

数据来源:通达信/同花顺/东方财富;结论不构成投资建议。
