# eltdx 仓库接口核实与项目采纳可行性分析

> 分析日期：2026-09-15｜对象：`electkismet/eltdx`（GitHub Pages `electkismet.github.io/eltdx`）
> 指令：核实所有接口用法、与项目冲突、可否采纳；**仅分析，未改动任何项目代码**。
> 数据来源：通达信协议（eltdx 为 7709/7615 通达信协议客户端）；以下为架构评估，不构成投资建议。

---

## 一、仓库定位（先破误区）

`eltdx` 是 **Rust 驱动的通达信 A股行情协议 Python 客户端**，不是又一个 easy-tdx 的 Python 分叉：

| 维度 | 本项目现用 easy-tdx | eltdx |
|---|---|---|
| 实现语言 | Python（纯解释） | **Rust 内核 + Python 绑定**（预编译 wheel） |
| 安装 | `pip install easy-tdx`（上游已撤、装不到） | `pip install eltdx`（PyPI 在线，200 ✓） |
| 运行时依赖 | 依赖若干 PyPI 包 | **`dependencies = []`（零运行时依赖）** |
| Python 支持 | 依赖具体版本 | `>=3.10`，cp310-abi3 多平台 wheel（**含 3.12，无需 Rust**） |
| 维护状态 | 上游 `awayings/easy_tdx` 已 404 | **活跃**，最新 v3.2.2（2026-09-12），commit 至 2026-09-14 |
| 协议覆盖 | 7709 行情为主 | **7709 行情（22 命令）+ 7615 F10/资料（21+ Entry）+ Helpers + MCP + HTTP 网关** |
| 握手 | 本项目刚 patch 修复 2026-09 握手 | 活跃上游，**Rust 握手跟随主站演进**（天然含新式握手） |

**关键结论**：eltdx 与本项目同源（都是通达信协议客户端），标注数据源仍为「通达信」，与项目约定一致；且它是**当前唯一活的上游**。

---

## 二、全量接口清点与用法

### 2.1 7709 行情原生协议（22 条命令，全部 `已接入` 或 `核心`）

| 命令 | 能力 | eltdx API | 接入 |
|---|---|---|---|
| `0x000d` | 连接握手 | `client.session.handshake()` | 核心 |
| `0x0004` | 心跳保活 | `client.session.heartbeat()` | 核心 |
| `0x044e` | 代码数量 | `client.codes.count(market)` | 核心 |
| `0x044d` | 代码表分页 | `client.codes.list/all/a_shares/all_etfs/all_indices` | 核心 |
| `0x052d` | K线/周期线 | `client.bars.get(code, period="day", count=30, adjust="qfq")` | 核心 |
| `0x0537` | 当日分时 | `client.minutes.today(code)` | 核心 |
| `0x0fb4` | 指定日期历史分时 | `client.minutes.history(code, "2026-05-20")` | 核心 |
| `0x0feb` | 近期历史分时 | `client.minutes.recent(code)` | 已接入 |
| `0x051b` | 分时副图 | `client.minutes.aux(code)` | 已接入 |
| `0x0fd1` | 小走势图 | `client.minutes.sparkline(code)` | 已接入 |
| `0x054c` | 批量行情快照 | `client.quotes.get_snapshots(codes)` | 核心 |
| `0x053e` | 旧版批量行情 | `client.quotes.legacy(codes)` | 已接入 |
| `0x054b` | 分类行情列表 | `client.quotes.list_by_category(...)` | 核心 |
| `0x0547` | 增量刷新/推送 | `client.quotes.refresh()/poll_push()` | 单次刷新+推送队列已接入 |
| `0x0fc5` | 当日成交明细 | `client.trades.today(code)` / `all_today` | 核心 |
| `0x0fc6` | 历史成交明细增强 | `client.trades.history/all_history/history_batch` | 已接入 |
| `0x056a` | 集合竞价过程快照 | `client.auctions.series(code, date=None)` | 已接入 |
| `0x000f` | 股本变迁/GBBQ | `client.corporate.capital_changes(code)` | 已接入 |
| `0x0010` | 财务信息批量查询 | `client.corporate.finance_batch(code)` | 已接入 |
| `0x0452` | 特殊品种涨跌停限制 | `client.limits.special()` | 已接入 |
| `0x0ffc` | **资金流向日数据** | `client.money_flow.daily(code)` | 已接入 |
| `0x06b9` | 服务器文件读取/下载 | `client.resources.read/download_file/read_stats`（含 zhb.zip 解析） | 已接入 |

**本地复权系数**：`client.corporate.adjustment_factors(code, anchor_date=...)` 基于 `0x000f` 返回 `scale+offset` 仿射系数（审计用，与服务端 `0x052d` 复权相差约 0.01~0.02 元）。

### 2.2 7615 F10 / TQLEX 资料接口（HTTP POST+JSON，21+ Entry）

入口：`from eltdx import F10Client; f10 = F10Client(timeout=3)` 或 `client.f10.*`。**不需要 7709 握手**。

常用方法（底层 Entry）：
- `stock_info(code)`、`company_profile(code)`、`business_composition(code)`、`shareholder_change_plans(code)`
- `dividend_financing(code)`、`allotment_dates/details(code,date)`
- `finance_report(code, report_type="zcfzb")`、`finance_diagnosis(code)`、`stock_score(code)`、`profit_forecast(code)`
- `theme_market(code)`、`valuation(code)`、`ranking_detail(code)`、`governance(code)`
- `hot_topics(code)`、`topic_compare(code, topic_id)`、`northbound_holding(code)`
- `announcements(code)`、`news(code)`、`roadshows(code)`、`company_news(code)`、`detail(detail_type, record_id)`
- `limit_up_down_list(start_date, end_date)`（逐股涨停/炸板/跌停列表）
- 高级：`f10.call("CWServ.tdxf10_gg_gsgk", params=[...])` 手动指定任意 Entry

返回 `F10Response`，含 `tables/rows/raw`；重复列名自动加 `__2` 后缀。

### 2.3 Helpers 组合封装（A股常用，业务层）

`client.helpers.*`：`latest_stock_list` / `latest_st_list` / `latest_suspended_list` / `full_quotes(codes)` / `stock_profile_table(codes)` / `board_quotes(category=...)` / `board_member_quotes(board_code)` / `shortline_indicators(codes)`（开盘量比、流通股本、封单、几天几板）/ `auction_data(code, date)` / `stock_topics(code)` / `topic_stocks(code, topic_name)` / `realtime_rank()` / `limit_ladder()`（连板天梯）/ `theme_strength_rank` / `stock_theme_strength_rank`（题材强度排行）/ `buy_sell_power` / `volume_compare`。

### 2.4 服务层

- **MCP**：`pip install "eltdx[mcp]"` → `eltdx-mcp`（stdio 工具服务，面向 Agent）。
- **HTTP 网关**：`pip install "eltdx[http]"` → `eltdx-http`（FastAPI，JSON / WebSocket RPC / 实时订阅，供 Java/Go/Node 等跨语言调用）。

### 2.5 连接与并发（用法要点）

```python
from eltdx import TdxClient
with TdxClient(timeout=3) as client:        # 构造即测速：43 普通 + 35 专用(竞价/资金流) 主站去重排名
    bars   = client.bars.get("sz000001", period="day", count=30, adjust="qfq")
    minute = client.minutes.today("sz000001")
    ticks  = client.trades.all_history("sz000001", "2026-05-20")   # 自动分页合并
    snap   = client.quotes.get_snapshots(["sz000001","sh600000"])
```
- Rust 连接池（`connections_per_server=4`、FIFO 准入）、心跳、`pin()`、推送队列；`probe_hosts=False` 可跳过测速；`client.transport.pin()` 可固定主站。
- 复权交给主站 `0x052d` 计算（`adjust="qfq/hfq/fixed_qfq"`）；本地审计用 `adjustment_factors()`。

---

## 三、与项目现有能力冲突/重叠矩阵

### 3.1 项目当前 TDX（easy-tdx）依赖面（仅 `core/tdx_client.py`，被 `core/data_provider.py` 调用）
- `tdx_get_security_bars`（K线）→ eltdx `client.bars.get` ✅ 完全对应
- `tdx_get_market_stat`（880005/880001/880006 统计指数）→ eltdx **无同名方法**，但 `client.bars.get("sh880005", period="day")` 等价可达成（**小缺口，需适配器封装**）
- `GetFinanceInfo 0x0010`（37 财务字段：净利/营收/股东户数/总资产）→ eltdx `client.corporate.finance_batch` ✅ 完全对应
- `get_company_news_f10` → eltdx `client.f10.news/announcements` ✅ 对应（且更全）

### 3.2 冲突/重叠分类

| eltdx 能力 | 项目现状 | 关系 | 采纳建议 |
|---|---|---|---|
| K线 `bars.get` | TDX 备用（主用东财 push2his f61） | **替代 easy-tdx** | ✅ P0 替换 |
| 0x0010 财务 `finance_batch` | TDX 0x0010 主源 | **替代 easy-tdx** | ✅ P0 替换 |
| 880xxx 市场统计 | TDX get_market_stat | **替代**（需封装 index bars） | ✅ P0 替换 |
| F10 news/announcements | TDX F10 + 部分东财 | **替代 easy-tdx 部分** | ✅ P0 替换 |
| 集合竞价 `auctions.series` | **项目无** | 净新增 | ✅ P1 新增 |
| 逐笔成交 `trades.history/all_history` | **项目无** | 净新增 | ✅ P1 新增 |
| 当日/历史分时 `minutes.*` | 东财分时为主 | 净新增（备用/补全） | ◐ P1 可选 |
| 连板天梯 `limit_ladder` | **项目无** | 净新增（短线因子） | ✅ P1 新增 |
| 题材强度 `theme_strength` | **项目无** | 净新增（短线因子） | ✅ P1 新增 |
| 短线指标 `shortline_indicators` | **项目无** | 净新增（开盘量比/封单/几天几板） | ✅ P1 新增 |
| 本地复权系数 `adjustment_factors` | 腾讯 ifzq qfq | 替代外部依赖（更自包含） | ◐ P1 可选 |
| 板块行情 `board_quotes` | **东财主路径**（sc_datasource 已迁东财） | **重复东财主源** | ⛔ 避免（不替换东财） |
| 资金流向日 `money_flow.daily` | **东财 push2/ulist 主路径** | **重复东财主源** | ⛔ 避免 |
| F10 全套（概况/财报/题材/估值…） | **东财主路径** | **重复东财主源** | ⛔ 避免（除非东财失效兜底） |
| zhb.zip 下载 `resources` | 本地 ZHB 快照（用户手动同步） | **净新增**（可自动刷新） | ✅ P1 新增 |

---

## 四、采纳可行性分级

### ✅ P0（强烈建议）：eltdx 替换 easy-tdx，作为「通达信二进制协议源」
- **价值**：① 消除 dead-upstream 风险（easy-tdx 上游已 404，不可 pip 重装，我们靠 site-packages patch 续命，脆弱）；② eltdx 活跃上游，**Rust 握手天然跟随 2026-09 主站**，可**移除我们刚写的 `_tdx_handshake_patch.py` 补丁**；③ Rust+连接池，**速度/并发/稳健性显著优于纯 Python easy-tdx**；④ 零运行时依赖，安装干净。
- **冲突**：无。它替换的是「TDX 二进制源」这一独立源（与东财 HTTP 主路径并列），不改变东财主路径。
- **代价**：重写 `core/tdx_client.py` 适配器（eltdx API 与 easy-tdx 不同：`client.bars.get` vs `get_security_bars(Market.SH,...)`），工作局部可控；`get_market_stat` 需封装为 `bars.get("sh880005")` 适配器。
- **治理**：eltdx 与 easy-tdx 同属「tdx」逻辑源，替换字段**无需新增 field_dict 注册**；G1 闸门照常。

### ✅ P1（选择性采纳）：eltdx 独有、项目缺的能力
- 集合竞价、逐笔成交历史、连板天梯、题材强度、短线指标、zhb.zip 自动下载——这些**当前任何源都未供给**，是真实增量。
- **代价**：需为新增字段在 `field_dict.md` 注册（G1 闸门），并写适配/缓存层。中等工作量。
- **谨慎点**：逐笔/分时高频数据量大，需加限流与 TTL，避免冲击现有分域限流架构。

### ⛔ 避免：不要用 eltdx 替换东财主路径
- `board_quotes` / `money_flow.daily` / F10 全套与东财主路径**功能重叠**。项目已确立「东财 HTTP 为主、TDX 为备用/补全」的单一数据源纪律；重复引入会造成双源冲突、违背字段治理原则。除非东财失效时作兜底，否则不主动替换。

---

## 五、风险与约束

1. **许可证（最高优先级）**：`ELTDX Research-Only License`——**仅限个人学习、协议研究、非商业研究**；明确禁止商业行为、付费/生产服务、转售、行情贩卖、自动化交易服务。本项目为个人研究用途**兼容**，但须明确：**一旦有任何商业化意图，eltdx 立即不可用**。easy-tdx 原许可与东财使用亦需各自合规。
2. **原生依赖**：Rust 编译的 `.pyd/.so`，绑定 CPython 3.10–3.14（**支持本机 3.12**）；不支持 free-threaded CPython、PyPy、musllinux。项目由纯 Python+东财栈变为「含一个原生扩展」，治理上建议保持 TDX 为**可选项**（无 eltdx 时东财主路径仍可跑）。
3. **集成成本**：`core/tdx_client.py` 适配器重写（约 1 个文件），局部但非平凡；`get_market_stat` 无直接方法需封装。
4. **治理闸门**：新增 P1 字段须走 G1 registry_parity / G3 gen_field_dict --check；P0 替换同逻辑源字段免注册。
5. **外部负载**：eltdx 默认探测 78 台 TDX 主站（与 easy-tdx 同量级），不新增额外外部负载；但 P1 高频（逐笔/分时）需自加限流。

---

## 六、建议路线（决策用）

1. **第一步（验证，不动项目）**：沙箱 `pip install eltdx` + 跑 `eltdx-smoke`，确认其对当前 TDX 主站可取 K线/财务/880xxx 统计（验证 2026-09 握手已内置）。
2. **第二步（P0 替换）**：将 `core/tdx_client.py` 的 easy-tdx 适配层改写为 eltdx API；封装 `get_market_stat` 为 `bars.get("sh880005")`；**移除 `_tdx_handshake_patch.py` 补丁**；requirements 加 `eltdx>=3.2.2`、去掉 easy-tdx 浮动约束。经 G1/G3 闸门提交。
3. **第三步（P1 增量，按需）**：评估连板天梯/题材强度/集合竞价/逐笔 对 val 策略的增益，挑 1–2 个先落地并注册字段；zhb.zip 自动下载作为 ZHB 快照刷新增强。
4. **始终避免**：用 eltdx 的 board/fund-flow/F10 替换东财主路径。

> 注：本报告为纯分析，未执行任何 `pip install`、未改动项目文件。是否进入第一步验证，请用户拍板。

数据来源：GitHub API（electkismet/eltdx 元数据/README/docs）、PyPI 探测、本机 `a-stock-data` 源码扫描；以上为架构评估，不构成投资建议。
