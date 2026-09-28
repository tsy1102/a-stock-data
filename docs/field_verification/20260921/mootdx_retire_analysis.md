# mootdx 退役可行性分析（2026-09-21 续 · 回应"是否与 easy_tdx 一起退役"）

> **📌 最终结论（2026-09-21 20:10 实测订正后）**：**保留 eltdx + easy_tdx（pin 到 github.com/yanwei99521/easy-tdx 可维护上游），退役 mootdx。**
> 理由（已彻底订正）：经修正后的实测，easy_tdx（含可维护上游 1.20.8）与 mootdx（0.11.7）在 2026 主站上**表现完全相同——都能建连、但都返回空数据**；二者差别只在**维护性**：easy_tdx 有活跃上游（2026-09 提交、API 与项目代码完全匹配）可修复空数据问题，mootdx 自 2024-05 起废弃、同样取不到数且无维护路径。故 2nd 后备应选可维护的 easy_tdx，而非废弃的 mootdx。
> 详见文末 §8 订正（此前"留 mootdx、杀 easy_tdx"的结论源于测试 Bug，已作废）。

---

## 0. 一句话判断（已订正）

| | eltdx | easy_tdx | mootdx |
|---|---|---|---|
| 运行时存活 | ✅ 主源 | ❌ 全路径已死 | ✅ 活（第三级） |
| 是否依赖本地通达信安装 | **否**（直连包内 `tdx_server.json` 的公网主站，与 mootdx 同源） | （已死） | **否**（直连公共服务器，纯 Python） |
| 连接目标 | TDX 公网主站 7709（行情）/ 7615（F10） | （已死） | TDX 公网主站 7709/7615 |
| `tdx_client.py` 角色 | primary（Rust 引擎） | dead 兜底 | 第三级（L664/L712） |
| `zhb_client.py` 角色 | primary（V17.3.1，0x06B9） | 二级（L1701，无补丁实死） | 第三级（L1746） |
| 维护状态 | 活跃（Rust 内核 3.2.2，2026-09-12 发布） | dead：本地装 1.32.6、公开 PyPI 查无此包、`TdxClient().connect()`=False | 0.11.7 停更(2024-05-04)、能连但取数空 |

**关键订正**：eltdx 与 mootdx **都是"直连公网 TDX 主站"的客户端**，二者连接模型完全一致，**都不依赖本地通达信（TdxW.exe）安装或运行**。上一轮分析称"eltdx 强依赖本地 TDX Windows 客户端、mootdx 是唯一环境无关通道"是错误的——该判断源于误读了 `eltdx_adapter.py` 的 docstring（"本地 TDX"），实际 eltdx 的 `hosts.py` 仅对 `tdx_server.json` 的 **45 个公网 IP**:7709 做 TCP 探测与连接，代码内无任何指向 `127.0.0.1`、本地安装目录、`vipdoc`、`TdxW.exe`、注册表的引用。

---

## 1. 三源真实身份（代码实证，非凭记忆）

- **eltdx（Rust 7709/7615，公网主站）**：`core/eltdx_adapter.py` 的 `create_eltdx_adapter()` 调 `TdxClient(hosts=_ELTDX_HOSTS)`，而 `_ELTDX_HOSTS`（L34-41）是 6 个公网 IP；底层 `eltdx/hosts.py` 的 `tdx_server.json`（45 台公网主站）+ `FALLBACK_HOSTS` 是同一批公网 IP，`probe_host` 仅做 `socket.create_connection((address, 7709))`。**不依赖本地 TDX 安装**。失败模式是 `eltdx 包缺失 / 公网主站不可达 / 上游异常`，而非"无本地 TDX"。
- **easy_tdx（Python）**：V17.2.15 移除 `_tdx_handshake_patch` 后，`_create_easy_tdx_adapter()`（L540）对 2026-09 主站握手失败 → 返回 None；`zhb_client.py:1701` 直接 `from easy_tdx.client import TdxClient` **也未再 import 握手补丁**（L38-40 注释已说明移除），故 ZHB 下载二级路径在 2026-09 服务器上同样握手失败、静默走到 mootdx。→ **easy_tdx 在所有活路径上实际已死**，仅残留 import/适配层代码。
- **mootdx（Python）**：纯 Python TDX 协议，直连公共服务器。`_check_tdx`(L664)、`_get_tdx_client`(L712)、`zhb_client.py:1746` 三处均作为 eltdx 之后的第三级兜底 → **活**。它与 eltdx 的连接目标完全相同（公网主站），区别仅在于它是**独立的纯 Python 实现**，而非"唯一不依赖本地 App 的通道"。

> 旁证：CHANGELOG V17.2.15:41 称"zhb_client 仍依赖握手补丁"，但实测 `core/_tdx_handshake_patch.py` 全仓**无任何 import 语句**（仅注释/CHANGELOG 文本提及），确为 orphaned 死文件。原 easy_tdx 退役方案 step 6（删该补丁文件）有效。

---

## 1.5 实证连通性测试（2026-09-21 19:50 补 · 用项目真实 API 实测，非推断）

为回应"按更新日期留 easy_tdx、退役 mootdx"的提议，本机对三库做了**真实调用**测试（同一台机器、同一批公网主站）：

| 引擎 | PyPI 最后发布 | API 可导入（项目真实路径） | 连 2026 主站 | 取数 |
|---|---|---|---|---|
| **eltdx** 3.2.2 | 2026-09-12 | ✅ | ✅（生产已证：采集 real=20/err=0） | ✅ |
| **easy_tdx** 1.32.6 | 公开 PyPI `easy-tdx` **404**（仅本地装，无公开上游可重装） | ✅ `from easy_tdx.client import TdxClient/Market`、`easy_tdx.KlineCategory`、`easy_tdx.mac.client.MacClient` 均在 | ❌ **`TdxClient().connect()` 返回 `False`**（连不上 2026 主站） | 取不到（根本连不上） |
| **mootdx** 0.11.7 | 2024-05-04（约 2.4 年未更新） | ✅ | ⚠️ 能建连（`Quotes.factory` 不报错），但 `quotes('600519')` 返回 **0 行空表**；`bestip=True` 选服扫描 **40s 挂起超时** | 当前取不到（连上空数据） |

**实测脚本要点：**
- easy_tdx 用项目真实 API `from easy_tdx.client import TdxClient; TdxClient().connect()` → **False**（早前误测 `from easy_tdx import EasyTdx` 报错是测错 API，已纠正；但结论"easy_tdx 已死"被本次正确测试**坐实**）。
- mootdx `Quotes.factory(market='std')` 建连成功但行情为空；`bestip=True` 触发全服扫描挂死 → 其内置选服/BESTIP 机制在当前网络已失效，属"连得上但算不出数"，与 easy_tdx 的"连不上"是不同性质的故障。

**关键推论：两个纯 Python 后备在 2026 当前环境其实都已失效**——easy_tdx 是"连不上"（connect=False），mootdx 是"连上空数据"。但二者失效性质不同：
- easy_tdx 在新主站握手即失败、且无公开上游可更新修复 → **结构性死**，不可恢复。
- mootdx 仍能建连，空数据源于选服/协议漂移（可尝试 `mootdx bestip` 重刷服务器表或显式指定主站修复） → **可恢复**，且至少有连接能力。

---

## 2. 调用链定位（逐文件证据）

**`tdx_client.py` 行情/财务主链：**
```
_get_verified_adapter()  →  eltdx (primary, L625-632)
                       →  easy_tdx 兜底 (L637, 已死→None)
_check_tdx()/_get_tdx_client()  →  仅当上面皆 None 才走 mootdx Quotes.factory (L664 / L712)
```
即 mootdx 是"eltdx 与 easy_tdx 双双失败"时才触发的**最后一道** TDX 通道。

**`zhb_client.py` ZHB 下载链：**
```
_download_zhb_zip()  →  eltdx (V17.3.1 primary, 0x06B9)
                   →  easy_tdx (L1701 二级, 无补丁实死)
                   →  mootdx (L1746 第三级)
```

---

## 3. 为什么不能一起删（硬理由 · 已订正）

1. **eltdx 与 mootdx 连接模型一致（都直连公网主站），但实现栈不同**：eltdx = Rust 原生引擎（`_native.pyd`，加载失败/平台不兼容时整段失效）；mootdx = 纯 Python。这是真正的**故障隔离点**——删 mootdx 后，一旦 `_native.pyd` 在某平台/版本无法加载、或 eltdx 某协议命令有 bug，TDX 层只剩 eltdx 一个引擎，**单点故障且无降级**。
2. **easy_tdx 删后，mootdx 成为唯一"非 Rust"端点**：原 easy_tdx 退役方案会把 tdx_client/zhb_client 的"非 eltdx 兜底"从"easy_tdx+mootdx"收敛为"仅 mootdx"。若连 mootdx 一并删，TDX 层彻底只剩 Rust 引擎，失去 Python 纯实现兜底。
3. **公网主站同时 down 时两者同归于尽，但实现级差异仍有价值**：当 TDX 公网主站整体不可达时，eltdx 与 mootdx 都会失败——此时真正兜底的是非 TDX 源（东财/腾讯/ZHB）。mootdx 的价值不在此场景，而在于**代码路径/协议实现/服务器探测排序与 eltdx 相互独立**，能覆盖"eltdx 能连但算错/某命令不支持"的局部失效。

---

## 4. 若强行一起删的影响矩阵

| 操作 | 可行性 | 影响 |
|---|---|---|
| 删 easy_tdx | ✅ 安全（死代码） | tdx_client/zhb_client 移除死路径；ZHB 链变 eltdx→mootdx；无数据缺口 |
| 删 mootdx | ⚠️ 技术可行但破坏实现多样性 | 失去纯 Python 兜底，TDX 层退化为单一 Rust 引擎；Rust 引擎加载失败/局部命令失效时 TDX 整体不可用（但公网主站可连场景下仍由 eltdx 承担） |

---

## 5. 推荐方案（已订正理由）

- ✅ **退役 easy_tdx**：沿用 `easy_tdx_retire_analysis.md` 的 8 步方案（删 `_EasyTdxAdapter`/`_create_easy_tdx_adapter`/`MacClient`/`_tdx_handshake_patch`，ZHB 链改 eltdx→mootdx，板块改纯东财，更正 requirements 注释，同步 test_data_tdx.py）。属破坏性依赖变更，执行前需用户明确批准。
- ✅ **保留 mootdx**：作为与 eltdx 异构（Rust vs 纯 Python）的第三级兜底，提供实现级故障隔离。
- 📝 **更正 `requirements.txt` 注释**：原"easy_tdx 故障 fallback"已过时，应改为："mootdx = **eltdx Rust 引擎加载失败 / 跨平台兼容 / 协议命令局部失效时的纯 Python TDX 兜底**（第三级，直连公网主站）"。
- 📝 **更正 `eltdx_adapter.py` 误导性 docstring**（已执行）：L289/L406 的"本地 TDX 7709/7615"改为"TDX 公网主站 7709/7615"，失败模式改为"eltdx 包缺失 / 公网主站不可达"；L362/L371 的"无本地 TDX"注释同步订正。
- ⏸️ **mootdx 退役仅在未来确定"接受 TDX 单点（仅 Rust 引擎）且已另有纯 Python 兜底或不再需要 TDX 冗余"时再议**；届时须先确认 eltdx 已能独立覆盖全部命令且无加载兼容风险。

---

## 6. 风险与建议

- **mootdx 自身风险（中，可控）**：0.11.7 停更(2024-05-04) + BESTIP bug（实测 `bestip=True` 扫描挂起）+ 服务器静默空表（实测 `quotes()` 返回 0 行）。但仅在 eltdx 失败后才被触发，且代码已在 `_tdx_health_check`(L728) 做换 IP 处理；其空数据源于选服/协议漂移，属可修复项，风险可接受。
- **不建议擅自动**：依赖移除是破坏性变更，且 mootdx 应保留——故本次**不执行任何删除**，待用户确认"仅退役 easy_tdx"后再走治理闸门 + 单测回归。

> 订正说明（2026-09-21 19:40）：原分析误判 eltdx 依赖本地 TDX 安装，已通过实证 `eltdx/hosts.py` + `tdx_server.json` 推翻。eltdx 与 mootdx 均直连公网主站，保留 mootdx 的理由是**实现多样性**而非**环境无关**。

---

## 7. 直接回应"按更新日期留 easy_tdx、退役 mootdx"——该提议方向反了

**用户论点的前提错了**：判断"留谁做后备"的正确标准是**功能性（能否连上 2026 主站并取数）**，而非"是否最近更新过"。

- **"最近更新" ≠ "能连上"**：easy_tdx 即便"新鲜"（本地 1.32.6），实测 `connect()`=False——**连不上主站的后备等于没有后备**。它的"新鲜"是假象：公开 PyPI 上 `easy-tdx` 根本 404（无公开上游可重装），所谓"更新"只是本地一份无法连接旧主站的库。
- **"陈旧" ≠ "无用"**：mootdx 虽 2024-05 停更，但实测**仍能建连**，空数据是可修复的选服/协议漂移问题，且至少有连接能力；easy_tdx 则结构性死（握手失败、无上游修复）。

**因此：**
- ❌ 若"退役 mootdx、留 easy_tdx 做后备" → 你将得到一个 **连不上的后备**（easy_tdx），同时砍掉**唯一还能建连的纯 Python TDX 通道**（mootdx）。这是三种组合里**韧性最差**的一种——比现状更糟。
- ✅ 正确组合是反过来的：**退役 easy_tdx（结构性死、不可恢复），保留 mootdx（可恢复、至少能连）**作为 eltdx 的异构兜底。这正是 §5 的推荐。
- 🔁 若进一步想"连 mootdx 也清掉"，则应是**两个纯 Python 后备一起清**，完全依赖 eltdx（Rust）+ 非 TDX 源（东财/腾讯/ZHB）兜底——这能彻底精简依赖，但代价是**放弃 TDX 层实现多样性**，且前提是先确认 eltdx 已能独立覆盖全部命令、无加载兼容风险。该路线见 §5 末尾"mootdx 退役再议"条件。

> 一句话：**mootdx 的"陈旧"是可修的小毛病；easy_tdx 的"新鲜"是连不上的死库。留新鲜死库、杀陈旧活库，是本末倒置。**

---

---

## 8. 订正（2026-09-21 20:10 · 用户给真实上游后重测，结论翻转）

**此前 §5/§7「留 mootdx、退役 easy_tdx」的结论作废——它建立在错误的实测上。**

- **测试 Bug 复盘**：上游 `TdxClient.connect()` 成功时返回 `None`（失败时抛 `TdxConnectionError`）。前两轮测试用 `if not c.connect():` 判定，而 `not None` 恒为 `True`，导致所有 "connect=False / 已死" 都是**误报**，从未真正走到取数。
- **修正后实测（强制 `sys.path` 优先加载 `src/easy_tdx` 上游源码）**：
  - 上游 **1.20.8** `TdxClient(host=<eltdx 已知可达主站>).connect()` **成功**（不抛异常）；`from_best_host()` 也成功；但 `get_security_quotes([(0,'600519')])` 返回 **0 行空数据**。
  - 本地 **1.32.6**（异源旧构建）表现**完全一致**：connect 成功、取数 0 行。
  - mootdx 0.11.7（早前实测）：`Quotes.factory` 建连成功、`quotes()` 返回 0 行空表、`bestip` 扫描挂起。
  - → **easy_tdx（含可维护上游）与 mootdx 在 2026 主站上表现完全相同：皆能建连、皆取不到数。只有 eltdx(Rust) 真正取到数（生产 real=20）。**
- **维护性差异才是唯一区分点**：
  - easy_tdx → 上游 `yanwei99521/easy-tdx` 创建于 2026-08-31、最近 push 2026-09-01、更新 2026-09-20，**活跃可维护**；其 `TdxClient`/`Market`/`KlineCategory`/`MacClient` 正是项目代码 `from easy_tdx.xxx import ...` 用到的接口 → 空数据问题**有望被上游修复**，且与现有代码零改对接。
  - mootdx → 0.11.7 最后发布 2024-05-04，**已废弃无上游**，同样取不到数且**无修复路径** → 是更差的 2nd 后备。
- **最终推荐（保留 2 个）**：**eltdx（工作主源） + easy_tdx（pin 到 yanwei99521 上游，可维护兜底），退役 mootdx（废弃且同样空数据）。**
- **诚实披露**：截至今日，easy_tdx 与 mootdx 在 2026 主站上**都"连上空数据"**，故纯 Python 后备目前均降级；真实可用兜底 = eltdx(Rust) + 非 TDX 源（东财/腾讯/ZHB）。保留 easy_tdx 是**面向未来的可维护选择**，并非当前即生效的可用 2nd 通道。若希望纯 Python 后备"立刻可用"，需先让上游修复空数据，或项目自写握手/解析补丁（原 `_tdx_handshake_patch` 思路）。
- **下一步（待用户批准）**：退役 mootdx = 删 `tdx_client.py:664/712` 与 `zhb_client.py:1746` 的 mootdx 第三级兜底 + 依赖声明；easy_tdx 则改为从 yanwei99521 上游安装/锁定版本（替换本地异源 1.32.6）。属破坏性依赖变更，走治理闸门前需用户明确批准。

> 以上为依赖架构与韧性分析，所有结论不构成投资建议。
