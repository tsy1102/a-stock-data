# 上游 simonlin1212/a-stock-data v3.10.0 同步核对报告

- 核对日期：2026-09-23
- 上游版本：v3.9.0（2026-09-20）→ **v3.10.0（2026-09-22 16:11，`2e0ae63`）**
- 本仓库 HEAD：V17.4.6（commit `07d538e`，本地未推送）
- 治理前提：本仓库是 fork 后演化的**字段对撞研究框架**，仅选择性继承上游数据来源代码，未整体纳入上游 skill 库。

---

## 一、本仓库与上游的代码重叠实况（先定位"能同步"的前提）

| 维度 | 上游 v3.10.0 | 本仓库（V17.4.6） |
|---|---|---|
| 形态 | 数据来源库/skill（数十个 `xxx()` 取数函数 + SKILL.md § 编号文档） | 字段对撞研究框架（`core/`、`stock_common/sc_datasource/`、`field_dict.md`、`scripts/collide.py`） |
| 共享函数 | `lpr_history()`（§11.5） | `stock_common/sc_datasource/_macro.py:71` `lpr_history()` ✅ 唯一重叠 |
| `tencent_ticks` / `futures_kline`(sina) / `futures_daily` / `tdx_client`(skill) | 存在 | **不存在**（grep 全仓 0 命中；上游未作为 pip 依赖或 vendored 模块引入） |
| `futures_kline_tdx` 等期货扩展 | 无 | 本仓库自有 TDX 期货扩展（与上游 sina 版无关） |
| 文档 § 编号 | SKILL.md Layer-1 §1.1–§1.7 | 本仓库 `field_dict.md` 用**自有** § 编号（§1.4=复权因子、§6.5=估值历史……），与上游 Layer-1 不重合 |

**结论**：上游 v3.10.0 绝大多数改动位于本仓库**未继承**的代码中，无对应落点。

---

## 二、v3.10.0 全部变更逐项映射

### Breaking Changes：Layer 1 重新编号
- 旧 1.2 腾讯财经→1.1、1.5 腾讯K线→1.2、1.6 通达信盘后包→1.3、（新）腾讯逐笔→1.4、1.3 百度→1.5、1.4 新浪复权因子→1.6、1.1 mootdx→1.7。
- **适用性：不适用。** 这是对上游 SKILL.md 内部 § 引用的重排，函数名/签名不变。本仓库 `field_dict.md` 的 § 编号是自有的（§1.4=复权因子等），与上游 Layer-1 §1.4=tencent_ticks 完全不同体系，无交叉引用会失效。
- grep 本仓库 README/AGENTS/field_dict/CHANGELOG 对 "mootdx/tencent_kline/tencent_ticks/futures_daily/Layer 1/§1.1 通达信" 的命中**全部是自有 TDX 基础设施（eltdx/easy_tdx/mootdx 兜底）**，非上游 § 编号引用。

### 新增 §1.4 `tencent_ticks(code)`（腾讯当日逐笔，替代失效 mootdx `transaction()`）
- **适用性：不直接适用，列为"可选采纳项 A"。**
- 本仓库 `get_sht_report.py` 已在 V17.4.5 **主动移除**"均价偏离/盘口委差"两块（源于盘中 L1 字段，盘后恒 N/A，你确认盘后扫描下无意义）。即本仓库当前不消费逐笔/盘口数据。
- 若未来要做**盘中**分析，tencent_ticks 是上游验证过的替代失效 mootdx 的逐笔源。但当前扫描在盘后，**采纳需新增取数层 + 新字段接入**，属架构决策，见第五节。

### 新增 §13.7 `futures_kline(symbol, start, end)`（新浪期货日K，补大商所历史日线）
- **适用性：不直接适用，列为"可选采纳项 B"。**
- 本仓库已有 `futures_kline_tdx`（TDX 期货扩展，line 4586），走自有 TDX 通道；上游此函数是**新浪**源，增量价值主要是"大商所历史日线补全"。
- 本仓库期货并非字段治理重点（对撞主战场是 A 股 ulist239/push2/ZHB）。是否需要对齐新浪源补全大商所，取决于期货字段需求。

### 修正①：INE 首个交易日之前发文件不再误判"格式改变"，改抛 `ValueError`
- 落点：`futures_daily()`/`futures_position_rank()`/`options_daily()`（上游函数）。
- **适用性：不适用**（本仓库无上述上游函数；自有 `futures_kline_tdx` 走 TDX 解析，不命中此边界）。

### 修正②：`futures_daily()` 文档起始日期更正（上期所 2002-01-07、中金所 2010-04-16）
- **适用性：不适用**（纯上游 docstring 修正，本仓库无 `futures_daily`）。

### 修正③：大商所报错提示改指向 `futures_kline()`/`futures_realtime()`；`tdx_client()` 报错提示加"逐笔改用 §1.4"
- **适用性：不适用**（上游 doc/报错字符串；本仓库 `core/tdx_client.py` 为自有实现，且无 `tencent_ticks` 可指向）。

### 修正④：筹码分布一节原写"OHLC 用 §1.1 通达信"与下方 baostock 示例不符，改为 §6.5 baostock 一次取齐
- **适用性：不适用**（上游 SKILL.md 章节修正；本仓库无对应章节）。

### 测试：新增 `tests/test_v310_sources.py` 26 条
- **适用性：不适用**（上游针对自有函数的测试；本仓库测试套件独立）。

---

## 三、唯一重叠函数 `lpr_history()` 复核（无待办）

- 上游 v3.9.0 对 `lpr_history` 的修正："LPR 报表混着旧贷款基准利率行（38 行、最晚 2015-10-24），照旧剔除"。
- **本仓库 `stock_common/sc_datasource/_macro.py:71` 在 V17.4.4 已双管齐下修复**：
  1. `sort_types="-1"` 降序 → 首屏即最新 200 行（原函数升序只取最旧首屏，`_lpr[-1]` 误取历史旧值 5.76）；
  2. 第 83–85 行 `_1y is None: continue` 跳过**无 LPR 字段的旧基准利率行**。
- 即本仓库的修法**覆盖且强于**上游 v3.9.0 的"仅过滤"方案；v3.10.0 未再动 `lpr_history`。
- 运行验证（`py -3.12`）：`get_macro_context()` 返回 `lpr_1y=3.0 / lpr_5y=3.5`（2026-09-20 央行公布值），正确。
- **结论：无需动作。**

---

## 四、总体结论

| 项 | 是否需本仓库同步 |
|---|---|
| Layer 1 重编号 | ❌ 不适用（自有 § 体系） |
| §1.4 tencent_ticks | ✅ **已采纳（用户授权）— V17.4.7 落地 `_ticks.py`** |
| §13.7 futures_kline(sina) | ✅ **已采纳（用户授权）— V17.4.7 落地 `_futures_sina.py`** |
| 修正①②③④（INE/futures_daily/doc/筹码分布） | ❌ 不适用（上游库内） |
| test_v310_sources | ❌ 不适用（上游针对自有函数；本仓另写 `tests/test_v310_sources.py` 21 项离线测试） |
| lpr_history 重叠 | ✅ 已覆盖（V17.4.4），无待办 |

**无必须落地的"更正"项**（v3.10.0 的修复恰好落在未继承区，本仓无对应 bug 需修）。**新增能力 A/B 经用户 2026-09-23 明确授权采纳**，已在 V17.4.7 作为取数层新增落地（不涉字段字典晋升、符合治理铁律），故 bump 至 V17.4.7 并提交（本地，不推送）。

---

## 五、两个可选采纳项（需你授权才动手）

**A. 采纳 `tencent_ticks` 作为盘中逐笔源**
- 价值：替代已失效的 mootdx `transaction()`，提供沪深个股/ETF 当日分笔（约 3 秒一笔）。
- 代价：需新增 `stock_common/sc_datasource/_ticks.py` 取数层 + 解析（收盘后核对连续竞价成交额、缺序号记 `missing_seq`）+ 接入点。
- 与你"盘后扫描"习惯冲突：盘中逐笔只在交易时段有数据，盘后调用会走快照校验分支。
- **建议**：当前不采纳；若后续要做盘中/超短实时分析再引入。

**B. 采纳 `futures_kline(sina)` 补全大商所历史日线**
- 价值：新浪源覆盖大商所历史日 K（自有 TDX 期货路径可能不全会所历史）。
- 代价：新增 sina 期货取数层 + 与现有 `futures_kline_tdx` 的源优先级协调。
- **建议**：仅当期货字段对撞需要大商所历史日线时采纳；当前 A 股字段治理主战场下优先级低。

> 两条均**非 v3.10.0 强制同步项**。
> **更新（2026-09-23 续）：用户已明确授权「采纳 tencent_ticks + 采纳 sina futures_kline」**，两项均已在 V17.4.7 落地（新增 `_ticks.py` / `_futures_sina.py` + 共享 `_v39_compat.py` + 注册 `__init__.py` + 21 项离线测试），按本仓库治理铁律执行（取数层新增、不晋升字段字典、本地提交不推送）。
