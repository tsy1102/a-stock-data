# easy-tdx 关联仓库分析报告（2026-09-15）

> 分析对象：GitHub 搜索 `easy-tdx` 返回 9 个仓库中、今年（2026）有更新的 7 个通达信相关仓库。
> 目的：与本项目所使用的 `easy-tdx`（本地安装 v1.32.6）做差异对比，找出可跟进改进项。
> 数据来源：GitHub API（repo/commits/README）、本机 `easy-tdx 1.32.6` 包元数据、PyPI 探测。
> 结论均不构成投资建议。

---

## 0. 结论速览（TL;DR）

1. **这 7 个仓库（除 obliviouslabs 为误命中）本质上都是同一个上游 `handsomejustin/awayings/easy_tdx`（PyPI 包名 `easy-tdx`）的分支 / 镜像 / 周边项目，并非互相独立的「不同实现」。** 它们的 README 徽章全部指向同一个上游。
2. **本项目使用的正是该上游包**（本机 `easy-tdx 1.32.6`，summary=「通达信 TCP 协议行情数据客户端」）。但**该上游的 GitHub 仓库与 PyPI 包当前均已不可公开访问（均 404）**——上游已被撤下。我们手上的 1.32.6 wheel 是目前能用的「事实最新版」。
3. 因此「跟进改进」**不能走「bump 上游版本」老路**（上游已死、公共 PyPI 装不到）。可行路径只有两条：
   - **P0**：从仍存活、且带协议修复的分支（主要是 `V0idk/easy_tdx_1` 的 2026-09 主站握手适配）补丁 / vendoring，修复我们 1.32.6 可能缺失的 TDX 握手兼容性；
   - **P1**：供应链韧性——把 1.32.6 wheel 固化，requirements 锁定精确版本（去掉 `>=` 浮动），避免未来环境不可装。
4. 多数分支差异是**应用层（终端看盘 / 回测 / Web UI / AI 复盘）功能**，对本项目（数据 + 字段字典层，且已在把行情 / 资金流 / 板块迁往东财）**直接可采纳度低**。

---

## 1. 上游溯源（关键事实）

| 探测项 | 结果 |
|---|---|
| GitHub `handsomejustin/easy_tdx` | **404**（不存在） |
| GitHub `awayings/easy_tdx`（README 徽章指向的另一 owner） | **404** |
| PyPI `easy-tdx` / `easy_tdx` / `easytdx` | **均 404** |
| 对照：PyPI `pandas` / `requests` → 200；GitHub `microsoft/vscode` → 200 | 正常（排除沙箱网络问题） |
| `handsomejustin` 现存仓库 | `mootdx` / `pytdx` / `gotdx` / `pytdx_backup`（正是 `injoyai/tdx` 引用的参考实现），**但无 `easy_tdx`** |
| 本机 `easy-tdx` 安装 | v1.32.6，`dist-info/direct_url.json` 为空（非 PyPI 直装，系本地 wheel），`Requires-Python >=3.10` |

**推论**：上游 `easy_tdx` 已被作者删除 / 私有化。公开互联网上已无官方源码与包。所有搜索命中的仓库都是社区分支 / 镜像，各自停留在不同快照。我们的 1.32.6 即是「最后可用版本」的本地副本。

---

## 2. 七仓逐库分析

> 用户所指「7 个今年更新的仓库」= 搜索 9 个结果中排除 2 个明显误命中（`voxnyx/tdx-easy-ticket-id` 浏览器插件、`Yuhala/tees-for-dummies` Intel TEE 指南）后剩下的 7 个。其中 `obliviouslabs/tdx_easy_https` 实为 Intel 机密计算误命中，已标注。

### 2.1 V0idk/easy_tdx_1 — ★1，2026-09-11
- **定位**：上游的重新托管（re-host）。README 与 `handsomejustin` 同源，commit `a9fa039 Change GitHub links to new repository owner` 印证。
- **今年核心改动**：
  - `f31790e fix: 适配 2026-09 主站新式握手，修复 K线/市场统计返回空数据` ← **针对 2026 年 9 月 TDX 主站握手协议变更的修复**。
  - `71c3865 fix: 个股/板块弹窗日K只取近 2 年，不再全历史分页`。
  - `5ea6914 perf: /watchlist/returns 取数 800→20 根`（取数优化）。
  - `04f7f1f fix: fetchBars 停页判断取末根恒假，带 startDate 的请求多翻一页`。
- **与本项目差异**：它是完整 easy_tdx（含 Web UI / 回测 / 缠论 / AI 解读）。我们是下游数据消费者。
- **可跟进（P0）**：**最高优先级**。若我们的 1.32.6 未含「2026-09 主站新式握手」适配，用 easy_tdx 拉 K 线 / 市场统计可能返回空。建议实测 1.32.6 的 TDX 取数；若空数据，cherry-pick 该修复或 vendor 此分支。

### 2.2 SharsDela/easy_tdx — ★0，2026-09-08
- **定位**：`41ed808 Initial import of easy_tdx package`，纯备份镜像，无独立开发。
- **可跟进**：无（仅存档副本）。

### 2.3 Evolution627/hard_tdx-0909 — ★0，2026-09-09
- **定位**：实为 easy_tdx 的**活跃分支**（描述写「hard one」是误称；commit 出现 `release: v1.32.4 / v1.32.5`、`mypy 严格模式`、`ex_reconnect`）。版本 v1.32.5 ≈ 我们的 1.32.6（同代）。
- **今年核心改动（应用层）**：盘面洞察（六栏目）、AI 盘面复盘、板块主力资金日历、涨停生态 vipdoc 路径可配置、热点相关性矩阵、ex_reconnect 密闭化、mypy strict 通过。
- **可跟进（P2 参考级）**：均为**终端 / 可视化 / AI 复盘**特性。本项目是数据 + 字段字典层，且行情 / 资金流 / 板块已迁东财，不直接需要；若未来做盘面洞察类展示可作参考，但**非字段 / 数据层改进**。

### 2.4 yanwei99521/easy-tdx — ★13，2026-09-01
- **定位**：上游分支，README 同源。commit 停留在 `v1.20.8` 时代（**比我们的 1.32.6 旧**）。
- **今年核心改动（Web API）**：同花顺股票关联 API、行业 API、信号雷达（扫描已保存策略买卖信号）。
- **可跟进**：版本落后于我们（1.20.8 < 1.32.6），采用即降级；其 Web API 特性（同花顺关联 / 行业）我们已由东财 / 同花顺其他通道覆盖。**无直接采纳价值**。

### 2.5 mvpbaggio/backtest-system — ★1，2026-08-29
- **定位**：**非分支**，是基于 `easy-tdx>=1.20` 的**独立回测框架**（companion / 用法范例）。
- **方法论亮点**：自研前复权（消除 -15%~-20% 除权跳空）、严格 7 窗样本外 Walk-Forward、真实费率（佣金银边 + 印花税卖 + 滑点）、ATR 吊灯止损用真实 high/low 触发、多标的等权组合、引擎自我迭代系统。
- **可跟进（P2 参考级）**：**回测方法论参考**（尤其前复权 / 防过拟合 / WF），若未来做因子 / 策略验证有价值；本项目当前定位是数据 / 字段字典，不做回测，故为「参考级」而非「代码级」改进。其 `requirements.txt` 仅 `easy-tdx>=1.20`，与我们兼容。

### 2.6 obliviouslabs/tdx_easy_https — ★1，2026-07-11 — ⚠️ 误命中
- **定位**：**与通达信无关**。内容是 Intel **T**rust **D**omain e**X**tensions（机密计算 / 可信执行环境）的 HTTPS 部署：attestation 服务、Let's Encrypt DNS-01、TLS 证书钉扎、GCP Confidential Space、dstack/Phala。
- **可跟进**：无（主题错配，搜索仅因含 `tdx`+`easy`+`https` 字样命中）。

### 2.7 clong365/easy_tdx — ★31 / 363 forks，2026-05-22
- **定位**：上游热门镜像（从 `xmtdx` 改名而来），**已陈旧（4 个月前停滞）**，v1.1.0 时代。
- **特性**：CLI、扩展市场、离线读取、专业财务（calc server）。
- **可跟进**：版本（1.1.0）远旧于我们（1.32.6）且停滞；作为「流行镜像」可作存档，但**不提供新改进**。

---

## 3. 差异矩阵

| 仓库 | 类型 | 版本基线 | 今年核心改动 | 对本项目可采纳度 |
|---|---|---|---|---|
| V0idk/easy_tdx_1 | 上游 re-host | ≈1.32.6 | **2026-09 主站握手适配**（修复 K线/市场统计空数据）+ 分页/取数优化 | **P0 高**（协议兼容性） |
| SharsDela/easy_tdx | 纯备份 | 不明 | 仅 initial import | 无 |
| Evolution627/hard_tdx-0909 | 活跃分支 | v1.32.5 | 盘面洞察 / AI 复盘 / 资金日历 / vipdoc 配置 | P2 参考（应用层） |
| yanwei99521/easy-tdx | 分支 | v1.20.8（旧） | Web API：同花顺关联 / 行业 / 信号雷达 | 无（版本旧+功能已覆盖） |
| mvpbaggio/backtest-system | 周边框架 | 依赖 easy-tdx>=1.20 | 回测方法论（前复权/WF/真实成本） | P2 参考（方法论） |
| obliviouslabs/tdx_easy_https | 误命中 | — | Intel TEE HTTPS 部署 | 无（主题错配） |
| clong365/easy_tdx | 陈旧镜像 | v1.1.0（旧） | CLI/扩展市场/离线读取 | 无（陈旧） |

---

## 4. 可跟进改进项（按优先级）

- **P0 — TDX 握手兼容性验证 + 修复（唯一实质代码级动作）**
  - 动作：实测本机 `easy-tdx 1.32.6` 在当前 TDX 主站下能否拉到 K 线 / 市场统计（对照 V0idk 的 `f31790e 适配 2026-09 主站新式握手`）。
  - 若返回空：从 `V0idk/easy_tdx_1` cherry-pick 握手修复，或将该项目 vendoring 进仓库（因上游已不可达，分支是仅存来源）。
  - 不改动主路径；仅影响 TDX 备用取数层。

- **P1 — 供应链韧性（配置级，非逻辑改动）**
  - 上游 GitHub + PyPI 均已撤下，`easy-tdx>=1.32.6,<2.0` 的浮动约束未来在干净环境**无法从公共源安装**。
  - 动作：将 1.32.6 wheel 固化进仓库内部索引 / `vendor/`；requirements 锁定精确版本 `easy-tdx==1.32.6`（去掉 `>=` 浮动）。

- **P2 — 参考级（仅未来需求触发）**
  - `Evolution627` 的盘面洞察 / 资金日历 / 涨停生态 vipdoc 配置：若未来做盘面展示类需求可借鉴。
  - `mvpbaggio` 的前复权 + 严格 7 窗 WF + 真实成本：若做因子 / 策略验证可借鉴（注意本项目 K 线取自 TDX 自带前复权 vipdoc，通常不自行重算）。

- **N/A — 不采纳**
  - `yanwei99521`（版本旧、功能已覆盖）、`clong365`（陈旧镜像）、`SharsDela`（纯备份）、`obliviouslabs`（误命中）。

---

## 5. 给决策者的建议

- **不建议**为「跟进这 7 个仓库」而切换 / 升级 `easy-tdx`：上游已死，分支多为镜像或应用层分叉，且无任何分支在「数据 / 字段字典」层面领先于我们的 1.32.6。
- **唯一值得做的实质动作** = P0（握手兼容性验证 + 必要时补丁）+ P1（wheel 固化）。
- 本项目的既定方向（行情 / 资金流 / 板块 迁东财、TDX 退居备用）与「丰富 easy_tdx 应用层」背道而驰，故多数差异**不值得跟进**。
- 与上一轮 `injoyai/tdx`（Go 协议库）结论一致：我们的 TDX 运行时是 Python `easy-tdx`，该上游现已不可达，后续应以「存活分支（V0idk）+ 东财降级层」双保险保障可用性。

---

## 6. 附：2 个被排除的搜索误命中（非通达信）

- `voxnyx/tdx-easy-ticket-id`（2025-10，JavaScript 浏览器插件，复制 TDX ticketID 为富文本）—— 非数据 SDK。
- `Yuhala/tees-for-dummies`（2026-04，Shell，Intel SGX / TrustZone / **TDX** / AMD SEV-SNP 指南）—— 此处「TDX」= Intel 机密计算，非通达信。
