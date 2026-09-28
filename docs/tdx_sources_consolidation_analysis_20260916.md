# TDX 多源与多安装「精简 / 替代」核查分析

> 分析日期：2026-09-16｜范围：a-stock-data 项目内所有"通达信（TDX）"相关**数据源**与**安装依赖**
> 方法：静态代码核查 + 字段字典（field_dict §零·B / §13.5）+ 既有分析文档（eltdx_analysis / easy_tdx_repos_analysis）
> 结论性质：架构审计，不构成代码改动；所有建议均标"条件/风险"。数据来源：通达信协议 + 本项目代码。

---

## 一、全景盘点（10 项 TDX 相关实体）

| # | 名称 | 类型 | 项目中的角色 | 运行期 / 对撞 | 当前状态 |
|---|------|------|--------------|----------------|----------|
| 1 | **eltdx** | pip 包（Rust 内核） | TDX 7709/7615 TCP 主源：行情/日K线/0x0010 财务/F10/连板天梯/短线指标/zhb 下载(已验证) | 运行期主源 + 对撞净新增（§12.13.10） | ✅ 活跃上游 v3.2.2，2026-09 握手内置 |
| 2 | **easy_tdx** | pip 包（Python） | TCP 兜底 + **ZHB zip 下载（当前实际路径）** + MacClient 板块归属 + F10 兜底 | 运行期兜底（多依赖握手补丁） | ⚠️ 上游已 404，靠本地补丁续命 |
| 3 | **mootdx** | pip 包（Python） | TCP 末级兜底（仅当 easy_tdx 全部主机不可达触发） | 运行期末级保险 | ⚠️ 停更 2024-07，纯 pip 备胎 |
| 4 | **zhb_client**（项目模块） | 代码模块 | 下载+解析 zhb.zip（tdxstat/tdxstat2/spblock/tdxzs…）——项目核心快照源之一 | 运行期（ZHB 为字典"离线零网络"首选源） | ✅ 经 easy_tdx 或 eltdx 下载 |
| 5 | **_tdx_handshake_patch** | 项目模块 | easy_tdx 2026-09 主站握手补丁 | 仅 zhb_client import 时全局生效 | ⚠️ 仅为 easy_tdx 续命 |
| 6 | **tdx_connector MCP**（云连接器） | 连接器 | AI 字段对撞神谕（CwInfo/ExtInfo/HQInfo 官方命名真值） | **非运行期，仅对撞** | ✅ 云侧，不增加运行负担 |
| 7 | **CwInfo**（云 tdx_quotes 子块） | 云数据块 | 对撞命名真值（万元口径财务快照） | **非运行期，仅对撞** | ✅ 与 tdx_connector 同源 |
| 8 | **tdxrs**（外部仓库 jiangtaovan/tdxrs） | 外部参考 | 本会话已分析：K线能力在日频下无不可替代性 | 未安装 | ℹ️ 仅 docs 引用，非依赖 |
| 9 | **本地 TDX App**（C:\new_tdx64\vipdoc） | 外部安装 | val 历史日K线只读依赖（需用户手动同步） | 运行期只读（val 专用） | ⚠️ 非自包含外部依赖 |
| 10 | **axdata** | pip 包 | 消费项目 zhb.zip 派生短线指标/涨跌停规则/筹码分布 | 运行期可选（缺失即降级） | ✅ 派生消费，非源本身 |

> 字典权威源清单（field_dict §零·B）将 TDX 族归纳为 3 个对外源标签：**ZHB**、**TDX-0x0010/F10**、**TDX-eltdx**；云 CwInfo 单列于对撞流程，不计入运行期源。

---

## 二、依赖与冗余关系图

```
                 ┌─────────────────────────────────────────────┐
   行情/K线/财务 │  eltdx(Rust,主)  ──失败──▶  easy_tdx(兜底)  │
   取数链路      │                     └──失败──▶  mootdx(末级)│
                 └─────────────────────────────────────────────┘
                              │
   ZHB 快照源      zhb_client ──下载──▶ easy_tdx(当前) ／ eltdx(已验证可替)
                              │
   板块归属        tdx_get_belong_boards ──▶ easy_tdx MacClient(MAC协议)
                  （东财 sc_datasource 已有行业/板块替代路径，但口径不同）
                              │
   对撞命名真值    tdx_connector(云 CwInfo) ＋ eltdx 运行时净新增 ＋ 黄金锚(fuyao/东财)
```

**核心判断**：运行期 TDX 二进制协议取数已由 **eltdx 单点主导**；easy_tdx / mootdx 实质是"协议级保险冗余"。**easy_tdx 已无不可替代职责**（见 §六 用户确权）：① ZHB 下载 eltdx 经 0x06B9 已实证可接管；② MacClient 板块归属——项目行业分类统一为东财申万二级，`tdx_get_belong_boards/members` 的东财兜底（`get_em_belong_boards`）已存在，翻转优先级即弃 MacClient；③ TCP 兜底坍缩为 `eltdx→mootdx` 即可。当前仅"生产代码仍依赖"三处，非"语义不可互替"。

---

## 三、精简 / 替代可行性逐项评估

### 1. easy_tdx —— 可大幅瘦身 / 退役（条件）
- **剩余职责（均可替，非不可替代）**：`tdx_get_belong_boards` 的 MacClient 板块归属（MAC 协议，eltdx 无 stock→board 能力）——但东财兜底 `get_em_belong_boards` 已存在，翻转优先级即弃 MacClient（见 §六 确权）。
- **可迁移职责**：
  - ZHB 下载 → 切 eltdx（`zhb_client.py:41-43` 已实证 `eltdx.ResourceApi.download_file("zhb.zip")` 经 0x06B9 成功）。
  - TCP 兜底 → eltdx 主用已稳，mootdx 可兼末级。
- **建议动作**：
  1. zhb_client 下载路径迁 eltdx（P0，见下）；
  2. `tdx_get_belong_boards` 迁东财 `sc_datasource`（已有板块/行业，项目统一申万二级口径，无需保留 TDX 板块码）；
  3. 删 `_tdx_handshake_patch` + 卸载 `easy-tdx`。
- **风险（已消解）**：原 §13.5 Q10 曾裁定 `industry_code`（TDX 码）与 `industry_code_push2`（东财 BK1277）为两套分类体系、不可互替——但经用户确权，项目行业口径本就是东财申万二级（非 TDX 板块码），该约束不成立。迁东财后直接采用东财板块码即可，唯一风险是**回归口径一致性**（mcap/pe/主力净额返回字段须与原 MAC 对齐）。

### 2. mootdx —— 可降级为可选 / 移除（条件）
- 仅当 eltdx 主源不可达**且** easy_tdx 也失效时触发，实测触发概率极低。
- 若 easy_tdx 退役，mootdx 成为唯一 Python TCP 备胎；保留成本仅为纯 pip（零运行时依赖），收益是"协议级保险"。
- **建议**：eltdx 生产稳定观察 N 日（建议 ≥14 个交易日）后，评估移除；移除前须确认 eltdx 对北交所/边缘标的 K线覆盖与 easy_tdx 等价。

### 3. tdx_connector MCP + CwInfo —— 暂不可精简（对撞职责专属）
- 非运行期，不增加运行负担；提供**官方命名真值**（L1 定级锚）。
- 长期：eltdx 运行时净新增字段（§12.13.10）成熟后，可让 eltdx 同时承担"运行期 + 对撞命名"，云连接器降级为偶发复核；但**不应简单删除**——它与 eltdx 是"命名真值 vs 运行期"互补，非冗余。

### 4. tdxrs —— 可清理（无害）
- 未安装，仅 docs 参考；本会话已判定日频下无不可替代性。
- **动作**：保留 docs 引用作为灵感来源即可，不纳入任何依赖。

### 5. 本地 TDX App（vipdoc）—— 候选替代（需验证，不急）
- val 历史日K线只读依赖，须用户手动同步（非自包含，违反项目"每日收盘自动采集"原则）。
- **替代**：eltdx / mootdx `bars(0x052d)` 日K线；但存在**北交所边缘标的 gaps** + 前复权本地化差异。
- **建议**：列为技术债，待 eltdx 日K线全市场覆盖验证后迁移；当前保留。

### 6. axdata —— 保留（非源，派生消费）
- 消费项目自有 zhb.zip，可选降级，无冗余可删。

### 7. _tdx_handshake_patch —— 随 easy_tdx 退役一并删除（条件）
- 仅服务于 easy_tdx 2026-09 握手；eltdx 无需。

---

## 四、优先级行动建议

| 优先级 | 动作 | 收益 | 风险/条件 |
|--------|------|------|-----------|
| **P0** | zhb_client 下载迁 eltdx（去掉 easy_tdx 最大职责 + 握手补丁） | 切断 easy_tdx 主用路径，移除补丁模块 | 需回归 zhb.zip 解析（eltdx 0x06B9 已实证） |
| **P1** | `tdx_get_belong_boards`/`members`/`by_name` 翻转东财（弃 MacClient）＋ `_get_verified_adapter` 坍缩 `eltdx→mootdx` | easy_tdx 可完全退役，卸载 easy-tdx | 须 eltdx 稳定 + 东财 clist 回归 |
| **P2** | eltdx 生产稳定 ≥14 交易日后，评估移除 mootdx | 减少一个停更 pip 依赖 | 需北交所覆盖等价验证 |
| **P3（长期）** | eltdx 净新增字段成熟后，云连接器降级为复核锚 | 对撞流程更自包含 | 命名真值仍建议保留云侧复核 |
| 清理 | tdxrs 文档引用降级为"灵感"；vipdoc 列为技术债 | 降低认知负担 | 不动代码 |

---

## 五、结论

1. **运行期"多源"实为单点主导**：eltdx 已接管 TDX 二进制协议主取数，easy_tdx / mootdx 为保险冗余；精简核心目标是 **easy_tdx**。
2. **"多安装"中可替代性最高的是 easy_tdx**：ZHB 下载与 TCP 兜底均可迁；MacClient 板块归属此前被标为"唯一硬约束（TDX 板块码 vs 东财板块码不可互替）"，但经用户确权已不成立——项目行业分类统一为**东财申万二级**，`tdx_get_belong_boards/members` 的东财兜底已存在，翻转即弃 MacClient。故 easy_tdx **已无不可替代职责**，仅"当前生产代码仍依赖"三处（ZHB 下载 / 板块 MacClient / 行情二级兜底）。
3. **云连接器 / CwInfo 与 eltdx 是互补而非冗余**：前者提供官方命名真值（L1 锚），后者提供运行期数据；应长期共存、互补印证，不应删除。
4. **tdxrs 与本地 TDX App** 属外部 / 参考依赖：前者无害可留文档，后者为技术债待迁移。
5. **能力边界澄清（避免"eltdx 功能全覆盖 easy_tdx"误读）**：eltdx 在 **A股 TCP 行情核心取数**（Rust 性能 / 握手稳定性 / 零依赖）上优于 easy_tdx（Python，2026-09 主站握手需补丁），且**在项目的 A股数据治理职责范围内可逐步替代** easy_tdx；但二者并非"功能全覆盖"关系——(a) 项目当前生产代码里 **ZHB 下载仍走 easy_tdx**（eltdx 0x06B9 仅"已实证可替"、待实施），**板块归属 MacClient 仍走 easy_tdx**（东财兜底未翻转），故"全覆盖"是三步退役计划完成后的**目标态**而非现状；(b) easy_tdx 的**全量能力**（期货 / 港股 / 美股扩展市场、缠论、回测引擎、因子、Web UI、34 技术指标）eltdx 完全不覆盖——但这些超出项目 A股轻量治理定位，属无损益缺口。准确表述：**eltdx 在 A股行情核心取数上更优且可替代 easy_tdx 的项目相关职责，但功能上不全覆盖**。

> 一句话：**P0 先把 ZHB 下载从 easy_tdx 切到 eltdx（顺带删握手补丁），P1 再翻转板块查询至东财兜底（弃 MacClient）后让 easy_tdx 退役；mootdx 观察后评估；云连接器保留；tdxrs/vipdoc 留作参考与技术债。**

---

## 六、决策状态（2026-09-16，用户拍板）

- **暂缓执行删除**：eltdx 于 V17.2.15 刚接入，运行仅数日，**删除 easy_tdx 为时尚早**。须先连续运行数个交易日确认 eltdx 生产稳定性（尤其北交所等边缘标的连接/握手/数据完整性），再决定是否删除。
- **板块语义约束已推翻**：用户确认"项目板块定义采用东财申万分类，与通达信无关" → 原 §13.5 Q10 双体系不可互替的 P1 硬约束不成立，easy_tdx 已无不可替代职责（见"核心判断"订正）。
- **下周回顾**：已设自动提醒，于 2026-09-21（下周一）回顾本计划——核查 eltdx 稳定性证据后，再决策是否启动 P0→P1 三步删除。
- 当前动作：**仅分析、未改动任何 easy_tdx 相关代码**（除本分析文档与记忆外）。
