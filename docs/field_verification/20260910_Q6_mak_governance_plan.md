# Q6 专项：`get_mak_report.py` 外挂数据源治理 —— 方案与评估

> 生成时间：2026-09-10 | 状态：**待你决策**（本文仅评估与方案，未实施）
> 依据：本次健康体检第三步 + 针对 mak 的程序化取数调用盘点
> 数据来源：通达信 / 腾讯行情 / 东方财富 push2·ulist / 同花顺 fuyao·THS 热榜 / ZHB / 百度K线。仅供技术评估，不构成投资建议。

---

## 一、问题重述与**关键判断修正**

体检报告原表述为「mak 外挂最重（12+ 源），契约消费最少」，并建议"建事件层纳管异动源并字典化"。**深入盘点后，我认为原表述的方向需要修正**，否则会导向错误的改造。

### 1.1 核心事实

| 指标 | 实测值 |
|:---|---:|
| 顶层取数函数（去重） | **25 个** |
| `get_canonical_stock_data` 实际调用 | **0 次**（此前记为 1 次，实为注释/导入，非调用） |
| `@cached` 缓存包装 | **0 处** |
| `asyncio.gather` / `as_completed` | **0 处**（仅 15 处 `asyncio.to_thread`） |
| 顶层函数 | 24 个 |

### 1.2 ⚠️ 关键判断：不能简单要求 mak "改用统一入口"

`get_canonical_stock_data` 的契约是 **`CanonicalStockData`（单只股票、101 字段快照）**——它是**个股维度**入口。

而 mak 的数据需求是**全市场/板块/指数/事件维度**：

| mak 取数类别 | 代表函数 | 维度 |
|:---|:---|:---|
| 全市场快照 | `get_market_snapshot_async`(3)、`get_zhb_full_market_snapshot`(3)、`get_market_status`(1) | 市场级 |
| 板块/行业 | `get_sector_stocks`(5)、`get_all_sectors`(2)、`tdx_get_board_list`(1)、`get_zhb_industry_map`(1)、`get_em_industry_l2_data`(1) | 板块级 |
| 指数 | `get_index_returns`(2)、`get_index_kline_closes`(2)、`get_stock_index`(2) | 指数级 |
| 异动/事件 | `get_market_abnormal_data`(2)、`get_abnormal_announcements`(2)、`get_strategic_announcements`(2) | 事件级 |
| 情绪/热榜 | `get_ths_hot_pool`(2)、`get_ths_hot_raw`(1)、`get_kpl_broken_ratio`(1)、`get_kpl_market_sentiment`(1) | 情绪级 |
| K线 | `get_baidu_kline`(3) | 标的级 |
| ZHB 基础 | `get_zhb`(1)、`get_stock_name_from_zhb`(2)、`get_zhb_data_date`(1) | 基础级 |

**结论**：`get_canonical_stock_data` 调用为 0 **并非缺陷，而是维度不匹配的必然结果**。若强求 mak 改走该入口，等于用个股接口去取全市场快照，会产生 N 次单股请求（N≈5000），**性能灾难且逻辑错误**。

> 因此，正确的治理方向不是"让 mak 用统一入口"，而是**为 mak 建立与之匹配的「市场层 / 事件层」抽象**，并让**标的级**部分（当前 `get_baidu_kline`）回归统一层。

---

## 二、现状问题（真实存在的部分）

虽然"外挂"有合理性，但仍有**三个真实问题**：

### 问题 1：25 个源零缓存包装（`@cached` = 0）
全市场快照/板块列表属**低频变化**数据，却每次运行重新拉取。对比 `core/stock_cache.py` 已有成熟的 SQLite+TTL+single-flight 机制，mak **完全未接入**。
- **影响**：每次运行重复网络请求，是全市场扫描耗时的主要来源之一。
- **严重度**：中（性能，非正确性）。

### 问题 2：无 `asyncio.gather` 并发（0 处，仅 15 处 `to_thread`）
25 类取数之间多数无依赖，却可能串行等待。
- **影响**：耗时叠加。
- **严重度**：中。
- **注意**：需先确认现有 `to_thread` 是否已被上层 `execute_pipeline` 并发调度——若是，则此问题不成立（**待核**）。

### 问题 3：跨脚本同类需求重复实现
- `get_index_returns` / `get_index_kline_closes`：指数收益与K线，其他脚本（val/lng）可能也有类似需求。
- `get_sector_stocks`（5 次调用）：板块成分股，与 `tdx_get_board_members`(1) 可能功能重叠。
- **影响**：口径漂移风险。
- **严重度**：中。

### 问题 4（低）：部分源未进字典
体检已指出 `研报`/`龙虎榜`/`异动`/`百度K线` 等在字典中覆盖不足。

---

## 三、改造方案（三阶段，可分批决策）

### 阶段 A：缓存纳入（推荐优先做）

**目标**：让 mak 的 25 类取数接入既有 `core/stock_cache.py`。

**做法**：
1. 在 `stock_common/sc_datasource/` 为每类源补 `@cached(category=..., ttl_seconds=...)` 装饰器，而非在 mak 脚本内加（保持分层）。
2. TTL 建议：
   | 类别 | 建议 TTL | 理由 |
   |:---|:---|:---|
   | 全市场快照 | 当日有效（盘中可 5~15 分钟） | 盘中变化快 |
   | 板块/行业列表 | 1 天 | 低频 |
   | 指数 K线 | 1 天 | 收盘后固定 |
   | 异动/公告 | 10~30 分钟 | 事件驱动 |
   | 情绪/热榜 | 15~30 分钟 | 中频 |
   | 百度K线 | 1 天 | 日频数据 |

**收益**：显著减少重复网络请求，降低触发东财 429/风控的概率（与 `sc_network._DOMAIN_LIMITS` 保护目标一致）。
**风险**：**低**。装饰器在 stock_common 层，mak 调用点不变；缓存 key 已含 `CACHE_CONTRACT_VERSION` 前缀（本次治理已加），语义变更可整体失效。
**回退**：移除装饰器即可，单文件回滚。
**工作量**：小（约 8~12 处装饰器）。

### 阶段 B：并发编排核验与优化

**目标**：确认/建立 mak 的并发取数编排。

**做法**：
1. **先做只读核验**：确认 `execute_pipeline` 是否已并发调度这些 `to_thread`。若已并发，**此阶段取消**（避免过度改造）。
2. 若确为串行：引入 `asyncio.gather` 对无依赖源并行拉取。

**风险**：中。并发改动可能触发限流（`_DOMAIN_LIMITS` push2 系仅 0.4rps），**必须与阶段 A 的缓存配合**，否则并发会放大风控风险。
**回退**：单文件回滚。
**工作量**：中（需先核验）。

### 阶段 C：建立「市场层 / 事件层」抽象（架构级）

**目标**：为全市场/板块/指数/事件维度建立与 `CanonicalStockData` 对等的契约层。

**做法**：
1. 在 `stock_common/sc_schema.py` 新增市场级契约（如 `MarketSnapshot`、`SectorSnapshot`、`MarketEvent`），类比 `CanonicalStockData` 的强类型 + `field_sources` 溯源。
2. 在 `stock_common/sc_datasource/` 建立对应统一入口（如 `get_market_snapshot_unified()`）。
3. mak 改为消费该层；同时让 val/lng 的同类需求复用。
4. 字典增补市场层字段条目。

**收益**：
- 消除跨脚本同类需求的重复实现（问题 3）
- 市场层字段进入字典与缓存，可审计、可复用
- 为后续其他全市场类功能提供基础设施

**风险**：**高**。
- 属架构级改造，需新建模块；
- 项目存在已知的 **core ↔ stock_common 循环依赖约束**（须沿用 lazy import 断环手法，切勿把 lazy import 提升级）；
- 改动面覆盖 schema / datasource / mak 三处，**回归风险显著高于本次已完成的治理项**。

**回退**：按模块回滚，但 mak 需同步回退，耦合度较高。
**工作量**：大（预估数个迭代）。

---

## 四、收益 / 风险 / 工作量 汇总

| 阶段 | 收益 | 风险 | 工作量 | 建议 |
|:---|:---|:---|:---|:---|
| **A 缓存纳入** | 中～高（降网络、降风控触发） | **低** | 小 | ✅ **建议立即做** |
| **B 并发核验/优化** | 中（若确为串行） | 中（风控） | 中 | 🟡 先做只读核验再决定 |
| **C 市场层抽象** | 高（长期可维护性） | **高**（架构级 + 循环依赖） | 大 | 🔴 建议单独立项，不并入日常治理 |

---

## 五、建议决策路径

**我的建议：先做 A，再做 B 的核验，C 暂缓。**

理由：
1. **A 的收益/风险比最优**——复用已有 `stock_cache` 机制，改动集中在 stock_common 层，mak 调用点零改动。
2. **B 必须先核验**——若 `execute_pipeline` 已并发，则无需改动；盲目加并发反而会放大东财风控风险（push2 仅 0.4rps）。
3. **C 虽长期价值最高，但风险显著**——本次治理已确立"不为改全而引入架构级回归风险"的原则；市场层抽象应作为独立专项，在 A 完成后、有充足回归窗口时推进。

**请你在以下选项中决策**：
- (1) 仅做 A
- (2) 做 A + B（先核验）
- (3) 做 A + B + C（全量，需接受架构级风险与较长周期）
- (4) 暂不改造，仅保留本文档作为技术债登记

---

## 六、附：mak 25 类外部取数源完整清单（供字典化与缓存归类使用）

| # | 函数 | 调用次数 | 类别 | 建议 TTL |
|:---:|:---|---:|:---|:---|
| 1 | `get_sector_stocks` | 5 | 板块 | 1 天 |
| 2 | `get_market_snapshot_async` | 3 | 全市场 | 盘中 5~15 分 |
| 3 | `get_baidu_kline` | 3 | 标的K线 | 1 天 |
| 4 | `get_zhb_full_market_snapshot` | 3 | 全市场 | 盘中 5~15 分 |
| 5 | `get_stock_index` | 2 | 指数 | 1 天 |
| 6 | `get_board_name` | 2 | 板块 | 1 天 |
| 7 | `get_market_abnormal_data` | 2 | 异动 | 10~30 分 |
| 8 | `get_stock_name_from_zhb` | 2 | 基础 | 1 天 |
| 9 | `get_index_returns` | 2 | 指数 | 1 天 |
| 10 | `get_index_kline_closes` | 2 | 指数 | 1 天 |
| 11 | `get_abnormal_announcements` | 2 | 事件 | 10~30 分 |
| 12 | `get_strategic_announcements` | 2 | 事件 | 10~30 分 |
| 13 | `get_all_sectors` | 2 | 板块 | 1 天 |
| 14 | `get_ths_hot_pool` | 2 | 情绪 | 15~30 分 |
| 15 | `get_zhb_industry_map` | 1 | 行业 | 1 天 |
| 16 | `tdx_get_board_list` | 1 | 板块 | 1 天 |
| 17 | `get_zhb` | 1 | 基础 | 1 天 |
| 18 | `get_em_industry_l2_data` | 1 | 行业 | 1 天 |
| 19 | `get_stock_name` | 1 | 基础 | 1 天 |
| 20 | `tdx_get_board_members` | 1 | 板块 | 1 天 |
| 21 | `get_ths_hot_raw` | 1 | 情绪 | 15~30 分 |
| 22 | `get_market_status` | 1 | 全市场 | 盘中 5 分 |
| 23 | `get_zhb_data_date` | 1 | 基础 | 1 天 |
| 24 | `get_kpl_broken_ratio` | 1 | 情绪 | 15~30 分 |
| 25 | `get_kpl_market_sentiment` | 1 | 情绪 | 15~30 分 |

> ⚠️ 上表 TTL 为**建议初值**，需结合各源的实际更新频率与你的使用时段（盘前/盘中/盘后）确认后定稿，不在本次臆测。

---

*本文档为评估与方案，未执行任何代码改动。*
