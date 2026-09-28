# 源健康度分析 × 东财封禁策略对齐（2026-09-21）

> 数据底座：`docs/field_verification/20260812–20260921` 共 33 个采集日 `raw_*.json`
> 结论均不构成投资建议。

---

## 一、5 大脚本的东财调用顺序/规则——**无需调整**

### 结论
5 大报告脚本（`get_lng/mak/med/sht/val_report.py`）**不直接调用东财**，grep 零 `eastmoney`/`push2` 引用；
它们全部经 `core/data_provider.get_canonical_stock_data` → `stock_common.sc_datasource` 间接取数。
因此东财调用顺序/规则**只能、且已经集中在数据源层**实现，且**已与实证封禁规律一致**，无需在 5 大脚本层面改动。

### 证据链（从调用链自顶向下）
1. **`core/data_provider.py` 优先级顺序**：L418 注释 `tdx → tencent → eastmoney_push2delay → eastmoney_push2`；
   - L439：腾讯行情（不封 IP，优先于 push2）；
   - L457-458：push2delay 镜像域优先（风控独立、114 字段全量），push2 主域仅作最后兜底；
   - L462 `get_em_quote_full_delay`（push2delay）、L469 `get_em_quote_full`（push2 主域 fallback）。
   - L97-100：批量预取走 `push2delay ulist.np`（延时镜像域，独立风控面）。
2. **`stock_common/sc_datasource/_quotes.py` 固化**：
   - `get_em_quote_full_delay`（L285，push2delay 镜像域）注释："**统一层 L3 东财兜底应优先本函数**"；
   - `get_em_quote_full`（L275，push2 主域，`@requires_push2`）注释："**风控最严，最后手段**"。
3. **V17.3.2 仅补了唯一残留缺口**：`_eastmoney.eastmoney_stock_info_push2` 原直连 push2 主域、主域断路器 Open 被裸 `except` 吞成 `{}` → 已加 push2delay 镜像域回退（可用率 ~95%）。

### 推论
封禁规律（push2 主域受扰率 80%、push2delay 镜像域可用率 93–97%、两者同崩仅 8%）**已正确落地在数据源层**，
5 大脚本层面无可调、亦无需调。

---

## 二、tencent / tdx / zhb "长期 error" 独立分析——**前论撤回**

### 诚实订正
上一轮终述称"本脚本 tencent/tdx/zhb 长期 error 是未配置/未同步的独立问题"——
**该论断未经核实，实证核查后撤回。** 三源在 33 个采集日中 **`real=20 / empty=0 / err=0` 跨 30+ 日一致**，根本未 error。

### 逐源实证（20260812–20260921）
| 源 | 端点/机制 | 跨日状态 | 实时性 | 备注 |
|---|---|---|---|---|
| **tencent** | `qt.gtimg.cn` 单股全字段 | 20/20 每日成功（仅 0827 单股 err） | 实时 | 600519=88 字段，零异常 |
| **tdx** | `core.tdx_client`（easy_tdx TCP 适配层） | 20/20 每日成功 | 实时 | quote_full/s_vol/b_vol/finance_info 齐全 |
| **zhb** | `core.zhb_client`（本机 zhb.zip 镜像） | 20/20 每日成功 | **滞后 1–3 天** | 数据齐，但 `zhb_date` 系统性滞后采集日 |

### 三源唯一真问题：zhb 镜像滞后（属设计内，非缺陷）
- 采集日 `zhb_date` 滞后采集日 **1–3 天**：如 20260921 采集 → `zhb_date=20260918`（3 天滞后）；
  整个序列最小滞后 1 天、周末/停更期达 3 天。
- 这即是"未同步"的真实含义——**是 STALE DATA（数据滞后），不是 ERROR**。
- 脚本已正确记录 `zhb_date`，crack 脚本按 **ZHB-T1 铁律**对齐到该镜像日，属设计内行为（镜像由用户手动/周期同步，非代码缺陷）。
- 附带 `name=None`：`get_stock_name_from_zhb` 在离线字典+磁盘缓存均未命中时返回 None（cosmetic，不影响对撞；`full` 字典含名称字段）。

### 路径分歧（非缺陷，仅供知悉）
- **采集脚本的 `collect_tdx` 用 `core.tdx_client`（easy_tdx 1.20.4 适配层）**；
- **运行时 `get_canonical_stock_data` 用 `eltdx`（Rust 7709/7615 客户端）**。
- 两者是不同 TDX 客户端，当前都可用；但若要求"采集血缘 ≡ 运行时血缘"，应让 `collect_tdx` 也走 eltdx。当前非阻塞。

### 推论
原"总封禁兜底链缺 tencent/tdx/zhb、需另立项修复"的担忧**不成立**——
三源长期可用，data_provider 的 `tdx → tencent → push2delay → push2` 兜底链完整。
真正需要关注的只有"全东财总封禁日（如 0921）"——那一天的兜底必须靠非东财源（TDX/腾讯/zhb 均已验证可用）。

---

## 三、可选改进（非必须，待用户确认）
1. **tdx 路径统一**：`collect_tdx` 改走 `eltdx`，使采集血缘与运行时一致。当前 easy_tdx 可用，非阻塞。
2. **zhb `name` 补全**：`get_stock_name_from_zhb` 离线/缓存未命中时，从 `full` 字典回退取名称（cosmetic 修复）。
