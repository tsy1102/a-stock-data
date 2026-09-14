# Ashare 仓库分析 × Tier1/Tier2 可行性评估（2026-09-14）

> 状态：分析评估（C 步骤延续），**纯分析、不动代码、不登记**。
> 触发：外部 AI 对 `mpquant/Ashare` 仓库的分析，要求评估其结论能否解决 Tier1（val 因子）与 Tier2（公式/指标层）问题，或能否借鉴优化。
> 数据来源标注：通达信 / 东方财富 / 同花顺官网黄金锚 + 各源 raw 采集（20260819–0907）+ 项目 live 代码核查。以下为方法结论，不构成投资建议。

---

## 0. TL;DR（先给结论）

1. **外部分析大部分是既有结论的复述**：仓库内 `docs/ashare_reference_review.md`（2026-09-12）早已覆盖 Ashare 评估，且 **A7 缺口已闭合（jsonp→纯 JSON host，2026-09-12 已切）、mkline 已决策不新增（P1-B）**。外部分析漏读了这份文档，重新推导了一遍。
2. **但它暴露了一个对 Tier1 真正关键的事实**：项目里 `_misc.py:16` 的 `get_historical_high_qfq` **已是「个股级 + 实时 HTTP + 腾讯 fqkline qfq 日线」**。这正是 Tier1 重分析（`20260914_val_tier1_reanalysis.md`）里"Route ② 需要的每日新鲜时序源 B1"——**它早已存在、已验证、A1 合规（有消费者）**。
3. **结论：Tier1 Route ② 未被"需新建时序基础设施"阻塞**——B1 轻量源已在项目内，只需一个薄封装返回完整序列即可。Tier1 现在就能做（路线①零改动 + 路线②薄封装）。
4. **Tier2：MyTT 低价值，xg 缺口未补**：MyTT 是 Python 指标库（MA/BOLL），val 已有 MACD/KDJ；它**不能**复活被放弃的"非开发者公式引擎"需求（MyTT 仍是 Python 代码，非公式 DSL）。

---

## 1. 外部分析 vs 项目真实现状（核查清单）

| 外部分析断言 | 项目真值（live 核查） | 判定 |
|---|---|---|
| A. 新浪纯 JSON host 闭合 A7，"应改 `_eastmoney.py:1678` jsonp→纯 JSON" | `_eastmoney.py:1678` **已用纯 JSON host**（`money.finance.sina.com.cn/.../json_v2.php`），注释"2026-09-12 由 jsonp 切换"；`ashare_reference_review.md:259` 已记"闭合一处 A7 缺口" | ⚠️ **过时断言**，缺口已闭合 |
| B. 腾讯 K 线端点 `fqkline/get`+`mkline` 作参考基准 | 已在项目内：`_eastmoney.py:1662`（指数，L2 兜底）+ `_misc.py:27`（个股 `get_historical_high_qfq`）均用 `web.ifzq.gtimg.cn/appstock/app/fqkline/get`，实时 HTTP、免费无鉴权 | ⚠️ **已存在**，非新发现 |
| P1-B. mkline 是否接入 | `ashare_reference_review.md:261` 已决策"**复用 fuyao，不新增 mkline**"（零消费者违反 A1）；本仓 `get_fuyao_kline` 零消费 | ✅ 已落定，无需重议 |
| C. 新浪 `scale` 1200/7200 + `ma=5` 多列 | `ashare_reference_review.md` P1-C/P0-A 已登记 scale 枚举、`ma=5` 取舍 | ✅ 已覆盖（确认性） |
| D. MyTT 指标库 | val 已有 MACD/KDJ（`sc_technical.py`）；MyTT = 增量指标实现 | 🟡 增量参考，非必需 |

> **同源陷阱复盘**：外部分析再次踩了"假设缺口即缺口"的坑（与 118 字段、K 线陷阱同源）——它没先查项目是否已有对应实现，就把"待落地"写进建议。仓库内 `docs/ashare_reference_review.md` 才是该仓库的权威评估结论。

---

## 2. 对 Tier1 的回答（核心：Route ② 已解锁）

### 2.1 关键证据：每日新鲜个股 qfq 日线已在项目内

`stock_common/sc_datasource/_misc.py:16`：
```python
def get_historical_high_qfq(code: str, count: int = 640) -> Optional[float]:
    """V17.0.5 P2: 历史最高价（腾讯前复权日线, ~640 根≈2.6 年窗口）。
    接口: web.ifzq.gtimg.cn fqkline(字典 §12.1 备胎——免费无鉴权, 与 TDX 实测一致)。"""
    mkt = "bj" if code.startswith(("92","8","4","43","83","87")) else (
          "sh" if code.startswith(("6","9","5")) else "sz")
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
    r = _quick_request(url, params={"param": f"{mkt}{code},day,,,{count},qfq"}, ...)
    node = (r.json().get("data") or {}).get(f"{mkt}{code}") or {}
    days = node.get("qfqday") or node.get("day") or []
    highs = [float(row[3]) for row in days if len(row) > 3 and float(row[3]) > 0]
    return max(highs) if highs else None
```

核查结论：
- **个股级**：按 code 前缀拼 `mkt`（sh/sz/bj），可拉任意 A 股/北交所个股。
- **每日新鲜**：每次 `_quick_request` 实时 HTTP（函数内**无缓存层**）→ 拉到的是当日最新 qfq 日线，非本地 `.day` 残留。
- **免费无鉴权**：`ifzq.gtimg.cn` 无需 Cookie/Key（Ashare 分析亦确认"全程无鉴权"）。
- **A1 合规**：有消费者 `get_lng_report.py:114` 调用 → 端点已 sanctioned，非孤儿源。

### 2.2 因此 Tier1 重分析的"悲观前提"需修订

`20260914_val_tier1_reanalysis.md` 把 Route ② 列为"需先建 B1/B2 时序基础设施"。**修正**：B1（按需腾讯 qfqday HTTP）**项目已实现**（即 `get_historical_high_qfq` 的同端点同解析），无需从零搭建；仅差一个"返回完整序列而非 max-high"的薄封装。

| Tier1 因子 | 所需数据 | 落地方式 | 架构增量 |
|---|---|---|---|
| #002 短期反转 | 快照 `change_5d` | 路线① 直接用 | **零** |
| #009 规模 | 快照 `mcap_yi` | 路线① 直接用 | **零** |
| #006 变体 MTD 截面动量 | 快照 `change_mtd` | 路线① 直接用 | **零** |
| #006 截面动量(5日) | 5日 qfq 收盘 | 路线② 薄封装 `get_stock_qfq_kline` | **薄封装** |
| #054/#055 低波动 | 20日回报 std | 路线② 薄封装 | **薄封装** |
| #028/#044 质量 | 5日/财报季 | 路线② + 财报快照 | **薄封装** |

→ **Tier1 现在即可推进**：路线①零改动先落地（最快 win），路线②只需新增一个约 15 行的薄封装（复用 `get_historical_high_qfq` 的 mkt 前缀 + qfqday 解析 + `_quick_request`），**无重型 DB、无 TDX App 依赖**。

### 2.3 性能前提（须落实，非阻塞）

- 因子策略对**候选集/流动性前 N 只**算（非全市场 5000 只）才划算；
- 建议封装层接 `sc_kline_cache.set_cached_kline`（24h-TTL，机制已存在）→ 同日重算/多因子共享零网络；TTL 24h 与"每日新鲜"一致（因子只需当日历史快照）。

---

## 3. 对 Tier2 的回答（MyTT 低价值，xg 缺口仍在）

- **原 Tier2 = tdxquant `xg` 公式引擎**（让非开发者用通达信语法写策略）→ **已放弃**（需装 TDX App，与轻量优先冲突，见 `0933f6a`）。
- **MyTT.py = Python 指标库（MA/BOLL/通达信公式实现）**：val 已有 MACD/KDJ（`sc_technical.py`），MyTT 只是**增量指标实现**，且仍是 Python 代码——它**不能**填补"非开发者公式层"缺口（那是 DSL 需求，MyTT 不是 DSL）。
- **诚实判定**：MyTT 对 Tier2 **低价值**。若 val 后续确有某具体指标缺口（如 BOLL 带宽、BIAS），可 cherry-pick 单函数；**不应整体引入**，否则违反 A2 单一事实源 + 制造维护负担。
- **Tier2 真实方向**：若仍想要"非开发者可扩策略"，应评估**独立的轻量公式解析器**（非 TDX App 依赖），或接受"val 策略保持代码定义"。Ashare/MyTT 都不提供该解。

---

## 4. 借鉴/优化方案（可落地步骤，待拍板后执行）

**P0（最高价值·零风险）— Tier1 路线② 薄封装：**
1. 在 `_misc.py` 加 `get_stock_qfq_kline(code, count=60, fields=('close',))`：复用 `get_historical_high_qfq` 的 mkt 前缀 + qfqday 解析 + `_quick_request`，返回完整序列（默认 close，可选 OHLCV）。
2. 接 `sc_kline_cache.set_cached_kline`（24h-TTL）。
3. val 新增 `strategy_24~` 系列（#054/#055/#006/#028），向 `_strategy_defs` 追加元组，现有 23 零改动。

**P1（最快 win）— Tier1 路线①：**
- 直接用快照 `change_5d/change_mtd/mcap_yi` 落 #002/#009/#006 变体，零代码路径改动。

**P2（谨慎）— MyTT 单函数 cherry-pick：**
- 仅当 val 确有指标缺口时，移植单个指标函数到 `sc_technical.py`，不整体引入库。

**明确不做：**
- 不重新落地 A7（已闭合）、不新增 mkline（P1-B 已决策）。
- 不整体引入 MyTT / Ashare `get_price`（与统一层 `get_canonical_stock_data` 冲突，违反 A1 收口）。

---

## 5. 待拍板

- (a) 直接进 P0 薄封装实现（需你确认因子清单与候选集范围）；
- (b) 先只做 P1 路线①（最快 win）；
- (c) 仅评估、暂不动；
- (d) 评 MyTT 是否真有 val 指标缺口（P2 前置）。

---

## 6. 引用证据

- `stock_common/sc_datasource/_misc.py:16` — `get_historical_high_qfq`（个股级腾讯 fqkline qfq 日线，实时 HTTP）
- `stock_common/sc_datasource/_eastmoney.py:1662` — 指数 K 线 L2 兜底（同端点）
- `get_lng_report.py:114` — `get_historical_high_qfq` 消费者（A1 合规）
- `docs/ashare_reference_review.md:259/261/274/302` — 既有 Ashare 评估（A7 闭合 / mkline 不新增 / scale 枚举 / 周月线 qfq 契约）
- `docs/field_verification/20260914_val_tier1_reanalysis.md` — Tier1 重分析（本评论文档修正其"Route ② 需建基础设施"的偏悲观前提）
- `C:/Tencent/WorkBuddy/.workbuddy/memory/MEMORY.md` — K 线非每日新鲜（line 35）+ Tier1 路线（line 40-41）
