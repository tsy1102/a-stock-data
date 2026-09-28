# easy_tdx 退役可行性分析（2026-09-21）

> ⚠️ **结论已订正（2026-09-21 20:10）**：本文件原结论"easy_tdx 已死、建议退役"**作废**。
> 经修正后的实测（修正 `connect()` 返回 `None` 被误判为 False 的测试 Bug），easy_tdx（含用户提供的可维护上游
> `github.com/yanwei99521/easy-tdx` 1.20.8）**能成功建连 2026 主站**（仅取数返回空，与 mootdx 表现相同），
> 且上游**活跃可维护**、API 与项目代码完全匹配。最终方案改为：**保留 eltdx + easy_tdx（pin 可维护上游），退役 mootdx**。
> 详见 `mootdx_retire_analysis.md` §8 订正节。本文件仅保留作为"曾考虑退役"的历史分析。

---

> ~~原结论（已作废）：easy_tdx 可以退役，且当前运行时它已基本是"死代码"。V17.2.15 已将
> 运行时 TDX 主源切到 eltdx，并移除了 easy_tdx 的 2026-09 握手补丁（`_tdx_handshake_patch`），
> 导致其适配器对当前行情主站握手失败、返回 None。所有 easy_tdx 仍"活着"的代码路径都已有
> 东财 HTTP 或 mootdx 兜底，删掉它不会引入新的数据缺口。~~

---

## 1. 运行时 easy_tdx 的真实存活状态

| 时间/位置 | 事实 |
|---|---|
| `core/tdx_client.py:614-641` `_get_verified_adapter()` | V17.2.15 改为 **eltdx 优先 → easy_tdx 兜底 → mootdx** |
| `core/zhb_client.py:39-40` | "2026-09 修复, 不再需要下方面向 easy_tdx 的 TDX 新式握手补丁, 故移除其 import" |
| `core/tdx_client.py:636` 注释 | "兜底 easy_tdx（2026-09 主站无补丁 → 通常返回 None）" |
| `core/eltdx_adapter.py:259` `download_eltdx_report_file` | V17.3.1 P0: **eltdx 已接管 ZHB 报告 ZIP 下载**（0x06B9 协议） |

**结论**：运行时 TDX 行情/财务主源 = eltdx（Rust 7709/7615）。easy_tdx 因缺握手补丁，其适配器
`_create_easy_tdx_adapter()` 对 2026-09 主站返回 None，是**死路径**。

---

## 2. 代码库中 easy_tdx 现存调用点（逐一定位）

| # | 位置 | 用途 | 是否活跃 | 删后替代 |
|---|---|---|---|---|
| A | `tdx_client.py:540` `_create_easy_tdx_adapter` | 兜底行情适配器 | ❌ 死（返回 None） | eltdx + mootdx |
| B | `tdx_client.py:2893-2945` `MacClient` | `tdx_get_belong_boards` 板块归属 | ⚠️ 活跃，但有东财兜底 | 东财 `get_em_belong_boards` |
| C | `tdx_client.py:441/466` `_EasyTdxAdapter.F10C/F10`（0x02CF/0x02D0） | F10 公司公告 | ⚠️ 活跃，但 eltdx 返回空→走东财 | mootdx「公司大事」+ 东财 |
| D | `zhb_client.py:1699-1744` | ZHB 下载二级兜底 | ⚠️ 活跃（eltdx 主源之后） | eltdx → mootdx |
| E | `tdx_client.py:379/394` `get_price_limits`/`market_stat` | 涨跌停价/市场统计 | ❌ 随适配器死（返回 None） | 上层 ±10% 计算 / eltdx limits |

---

## 3. 退役影响矩阵（逐项核验）

| 能力 | eltdx | mootdx | easy_tdx(将删) | 删后是否有替代 |
|---|---|---|---|---|
| 行情快照 / 财务 0x0010 | ✅ 主 | 指数K线 / xdxr 备 | 死 | ✅ eltdx + mootdx |
| 板块归属 | ✗ | ✗（委托东财） | MacClient | ✅ 东财 HTTP |
| F10 公告 | ✗（stub 空） | ✅ 公司大事 | 公司报道（死） | ✅ mootdx + 东财 |
| ZHB 报告下载 | ✅ 主（V17.3.1） | ✅ 三级 | 二级兜底 | ✅ eltdx + mootdx |
| xdxr 分红除权 | ✗（stub 空） | ✅ 有 | 死 | ✅ mootdx（已覆盖） |
| 涨跌停价 | ✗（返回 None） | n/a | 死 | ✅ 上层 ±10% 计算 |

**关键判断**：所有 easy_tdx "活跃"路径（B/C/D）都已有**独立的东财或 mootdx 兜底**，且 easy_tdx
自身的适配器已经死去。因此删除 easy_tdx **不会新增任何数据缺口**——那些缺口在 easy_tdx 返回
None 时就已经存在，现由 eltdx/mootdx/东财 实际承担。

唯一需落地确认的项：`tdx_get_belong_boards` 删 MacClient 后，板块归属**完全由东财 HTTP 承担**。
这其实符合项目历史决策——`stock_common/sc_datasource/_shared.py:696` 与 `__init__.py:623` 早已
写明"V12.0: 东财 HTTP 替代接口（完全移除 easy_tdx 依赖）"，板块/资金流本就走东财 push2/datacenter。
`get_em_belong_boards`（`sc_datasource/_industry.py:952`）是完整实现，东财为主源，可靠。

---

## 4. 推荐退役方案（待批准执行）

1. **`tdx_client.py`**：删除 `_create_easy_tdx_adapter` + 整个 `_EasyTdxAdapter` 类（所有方法）。
2. **`tdx_get_belong_boards`**：移除 MacClient 分支，仅保留东财 `get_em_belong_boards` 兜底；
   删除 `_get_mac_client` 及其 `easy_tdx.mac` 依赖。
3. **F10**：`_f10_get_content` 移除 easy_tdx「公司报道」分支（mootdx 公司大事 + 东财已覆盖）。
4. **`get_price_limits` / `market_stat`**：easy_tdx 实现改为直接委托 `eltdx_adapter` / 上层计算
   （与现状等价，无行为变化）。
5. **`zhb_client._download_zhb_zip`**：移除 easy_tdx 二级兜底，改为 eltdx → mootdx。
6. **删除 `core/_tdx_handshake_patch.py`**（已 orphaned，无任何 import 引用）。
7. **`requirements.txt:28-29`**：更正过时注释（eltdx 已接管 ZHB 下载，而非"easy_tdx 保留用于 ZHB 下载"）。
8. **`tests/data/test_data_tdx.py`**：移除 easy_tdx mock 专属用例（如仅测 easy_tdx 适配层者）。

---

## 5. 风险与建议

- **低风险**：运行时 easy_tdx 已死，删的是死代码 + 备胎死路径；活跃路径（行情/财务）由 eltdx + mootdx 覆盖。
- **中风险点**：板块归属删 MacClient 后将完全依赖东财 HTTP。需确认**东财全封禁日**（如 0921 实测）
  板块归属的降级策略——但这是东财可用性话题，与 easy_tdx 无关；且 V12.0 起板块本就走东财。
- **建议节奏**：本次先合 (a)/(b) 改进；easy_tdx 退役作为**独立提交**，走治理闸门 + 单测回归
  （现有 `test_data_tdx.py` 的 easy_tdx mock 需同步改）。
- **不擅自执行**：属依赖移除的破坏性变更，需用户明确批准后再动 `tdx_client.py` / `zhb_client.py` /
  `requirements.txt`。

> 以上为字段治理与依赖架构分析，所有结论不构成投资建议。
