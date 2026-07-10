# TDX F10 功能扩展 Roadmap（V2 实施版）

> **文档用途**：作为 F10 全覆盖修改期间的对焦参照文档。每完成一个函数/阶段，对照本文档确认实现位置、替代关系、缓存策略是否符合计划，防止修改失焦。
>
> **生成时间**：2026-07-04
> **状态**：缓存方案已批准，待实施阶段一

---

## 一、背景与目标

### 1.1 背景

easy_tdx 库通过 `get_company_info_category` + `get_company_info_content` 可读取 TDX F10 公司资料的 **16 个分类**，全部为纯文本表格格式（GBK 编码，ASCII 制表符绘制表格）。V9.0 已修复「公司公告」分类的 bug（`tdx_get_latest_announcements`），其余 15 个分类尚未使用。

### 1.2 核心问题

当前项目数据源高度依赖 HTTP 接口（特别是东财），存在严重限流风险：
- **东财 8 个域名**：`datacenter-web` / `push2` / `push2his` / `reportapi` / `search-api-web` / `np-listapi` / `np-weblist` / `emappdata`
- **仅 3 个域名配置了限流**（`tdx_client.py:179` 对 datacenter/push2/reportapi 设置 `sleep_ms=100`）
- **9 个东财接口 + 3 个新浪接口** 完全无 TDX 替代，是限流风险核心来源

### 1.3 目标

用 F10 数据源替代/补充现有 HTTP 接口，分四阶段实施：
- **阶段一**：核心替代（降低东财限流风险）
- **阶段二**：纯新增内容（丰富报告维度）
- **阶段三**：对比核查（数据质量提升）
- **阶段四**：缓存优化（按交易日过期）

### 1.4 F10 数据源优势

- 纯 TDX 协议（7709 端口），不依赖 HTTP，不会被反爬/限流
- 数据来自深交所/上交所官方披露，权威可靠
- 响应速度快（单分类 30-300ms）
- 数据格式稳定（F10 格式多年未变）
- 16 个分类覆盖公司基本面方方面面

---

## 二、缓存集成方案（已批准，方案 B）

> 此方案是所有 F10 函数的基础设施，必须在阶段一实施前或同期完成。

### 2.1 核心策略：按交易日过期 + 分类差异化 TTL

**核心思路**：用「最近一个交易日」作为缓存日期标签，而不是用固定 24 小时时长。

```
写入缓存时：
  key = f10_{category}_{code}
  trade_date = 最近一个交易日（由 stock_calendar.is_workday 计算）
  在缓存元数据中记录 trade_date

读取缓存时：
  取出缓存，比较 trade_date
  如果 trade_date == 最近一个交易日 → 命中
  如果 trade_date <  最近一个交易日 → 失效
```

### 2.2 与现有缓存框架的关系

| 设计点 | 现有方案 | 新方案 | 结论 |
|--------|---------|--------|------|
| 分类差异化 TTL | `TTL` 字典，22 个分类 | F10 新增 16 个分类 | **不重复**，纯扩展 |
| SQLite 存储 | `cache_entries` 表 | 同 | **完全复用** |
| 装饰器模式 | `@cached` / `@cached_async` | 同 | **完全复用** |
| LRU 清理 | `_enforce_size_limit()` | 同 | **完全复用** |
| 空值/坏数据不缓存 | `_has_zero_price` 检查 | 同 | **完全复用** |

**关键原则**：不修改 `get_cache`/`set_cache` 现有逻辑，只在 `set_cache` 和 `@cached` 装饰器中**新增** `trading_day` 可选参数（默认 False），现有 22 个分类行为完全不变。

### 2.3 实现机制

过期判断最终都统一为 `expires_at` 时间戳，`get_cache` 中的 `WHERE expires_at > now` **不需要修改**：

- `trading_day=False`（默认，现有分类）：`expires_at = now + ttl_seconds`
- `trading_day=True`（F10 高频分类）：`expires_at = 下一个交易日的 15:00`

### 2.4 F10 分类的缓存策略

| F10 分类 | 缓存 key 前缀 | 模式 | TTL | 理由 |
|---------|--------------|------|-----|------|
| F2 最新提示 | `f10_reminders` | 交易日 | — | 每日更新，休市不变 |
| F13 公司报道 | `f10_news` | 交易日 | — | 交易日更新 |
| F16 研报评级 | `f10_reports` | 交易日 | — | 每日更新 |
| F9 资金动向 | `f10_fund_flow` | 交易日 | — | 每日更新 |
| F12 公司公告 | `f10_announcements` | 交易日 | — | 已实现，复用 |
| F5 股东研究 | `f10_shareholder` | 固定 | 7 天 | 季度更新 |
| F4 股本结构 | `f10_share_capital` | 固定 | 7 天 | 偶尔更新 |
| F10 资本运作 | `f10_capital_op` | 固定 | 7 天 | 不定期 |
| F15 行业分析 | `f10_industry` | 固定 | 7 天 | 每周更新 |
| F11 热点题材 | `f10_themes` | 固定 | 3 天 | 不定期 |
| F3 财务分析 | `f10_financial` | 固定 | 90 天 | 季报周期 |
| F2 公司概况 | `f10_overview` | 固定 | 30 天 | 几乎不变 |
| F10 经营分析 | `f10_operation` | 固定 | 90 天 | 季度更新 |
| F8 高管治理 | `f10_governance` | 固定 | 30 天 | 几乎不变 |
| F7 分红融资 | `f10_dividend` | 固定 | 30 天 | 偶尔更新 |
| F6 机构持股 | `f10_inst_hold` | 固定 | 30 天 | 季度更新 |

**统计**：5 个高频分类用交易日模式，11 个低频分类用固定 TTL。

### 2.5 场景验证

| 场景 | 写入时间 | `expires_at`（交易日模式） | 下次查询 | 结果 |
|------|---------|--------------------------|---------|------|
| 周五 15:00 运行 | 周五 15:00 | 下周一 15:00 | 周六 10:00 | 命中 ✅ |
| 周五 15:00 运行 | 周五 15:00 | 下周一 15:00 | 周一 9:00 | 命中 ✅（盘前数据不变） |
| 周五 15:00 运行 | 周五 15:00 | 下周一 15:00 | 周一 16:00 | **失效 → 重取** ✅ |
| 节前最后一天 15:00 | 6/30 15:00 | 7/7 15:00（节后第一天） | 7/3 10:00 | 命中 ✅（假期数据不变） |
| 节前最后一天 15:00 | 6/30 15:00 | 7/7 15:00 | 7/7 16:00 | **失效 → 重取** ✅ |

### 2.6 依赖与新增函数

- **复用**：`stock_common/stock_calendar.py` 的 `is_workday()` 和 `holidays`/`workdays` 字典
- **新增**：`get_last_trading_day(d=None)` — 返回给定日期之前最近的交易日（向前回溯直到找到交易日）
- **新增**：在 `@cached` / `@cached_async` 装饰器中新增 `trading_day: bool = False` 参数
- **新增**：在 `set_cache` 中新增 `trading_day` 参数分支

### 2.7 风险规避

| 风险 | 严重度 | 规避措施 |
|------|--------|---------|
| 修改 `get_cache`/`set_cache` 影响现有 22 个分类 | 🔴 高 | **不修改现有逻辑**，只新增 `trading_day` 参数分支 |
| `stock_calendar` 年份超出范围抛异常 | 🟡 中 | `trading_day` 模式失败时 fallback 到固定 24h TTL |
| `expires_at` 可能比 `now` 还小（极端情况） | 🟢 低 | 写入时校验 `expires_at > now`，否则用 `now + 24h` |
| F10 分类名与现有分类名冲突 | 🟢 低 | F10 统一用 `f10_` 前缀 |

### 2.8 预计工作量

约 150-200 行代码（含 `get_last_trading_day`、装饰器扩展、TTL 字典扩展）。

---

## 三、阶段一：核心替代（降低东财限流风险）

### 3.1 目标

用 F10 替代 **9 个东财 HTTP 接口 + 3 个新浪 HTTP 接口**，将东财 HTTP 调用减少 60%+。

### 3.2 可完全替代的接口清单

#### 3.2.1 东财接口（9 项，高优先级）

| F10 分类/子栏目 | 替代的东财接口 | 现有函数 | 涉及脚本 |
|----------------|---------------|---------|---------|
| F2-1.4 最新报道 | search-api-web 个股新闻 | `get_eastmoney_stock_news` | sht/ful |
| F2-1.6 大宗交易 | datacenter RPT_DATA_BLOCKTRADE | `get_block_trade` | sht/med/lng |
| F2-1.7 融资融券 | datacenter RPTA_WEB_RZRQ_GGMX | `get_margin_trading` | sht/med/lng |
| F2-1.2 互动问答 | irm.cninfo.com.cn 互动易 | `cninfo_irm` | sht/ful |
| F4-4.3 限售解禁 | datacenter RPT_LIFT_STAGE | `get_lockup_expiry` | sht/med/lng/ful |
| F5-5.4 股东变化 | datacenter RPT_F10_EH_HOLDERS | `get_holder_structure` | med/lng/val/ful |
| F13 公司报道 | search-api-web 个股新闻 | `get_eastmoney_stock_news` | sht/ful |
| F16 研报评级 | reportapi 个股研报 | `get_reports` | sht/med/lng/ful |
| F15 行业分析 | push2 行业板块涨跌 | `_get_eastmoney_industry_sectors` | sht/med/ful |

#### 3.2.2 新浪接口（3 项，中优先级）

| F10 分类/子栏目 | 替代的新浪接口 | 现有函数 | 涉及脚本 |
|----------------|---------------|---------|---------|
| F3-3.7 资产负债表摘要 | 新浪 fzb | `get_sina_balance_sheet` | med/lng/val/ful |
| F3-3.8 利润表摘要 | 新浪 lrb | `get_sina_financial_report` | med/lng/val/ful |
| F3-3.4 盈利能力 | 新浪 lrb（毛利率+ROE） | `get_gross_margin_and_roe` | med/lng/val |

#### 3.2.3 无法用 F10 替代的接口（保留 HTTP）

以下数据 F10 **不包含**，必须保留 HTTP 接口：
- 龙虎榜（`get_dragon_tiger_board`）— F10 无席位明细
- 北向资金（`get_northbound_hold`）— F10 无沪股通/深股通数据
- 东财人气榜（`em_hot_rank`）— F10 无热度排名
- 同花顺强势股（`get_ths_hot_reason`）— F10 无当日热点归因
- 财联社电报（`cls_telegraph`）— F10 无实时快讯
- 7×24 快讯（`get_eastmoney_global_news`）— F10 无全市场快讯

### 3.3 新增函数（在 `tdx_client.py` 中）

| # | 函数名 | F10 分类 | 缓存 key | 缓存模式 | 替代接口数 |
|---|--------|---------|---------|---------|-----------|
| 1 | `tdx_get_latest_reminders(code)` | F2 最新提示（8 子栏目） | `f10_reminders` | 交易日 | 4（互动/报道/大宗/两融） |
| 2 | `tdx_get_company_news_f10(code)` | F13 公司报道 | `f10_news` | 交易日 | 1（东财新闻） |
| 3 | `tdx_get_financial_analysis(code)` | F3 财务分析（10 子栏目） | `f10_financial` | 固定 90 天 | 3（新浪三表） |
| 4 | `tdx_get_shareholder_research(code)` | F5 股东研究（7 子栏目） | `f10_shareholder` | 固定 7 天 | 2（东财股东） |
| 5 | `tdx_get_share_capital(code)` | F4 股本结构（含限售解禁） | `f10_share_capital` | 固定 7 天 | 1（东财限售） |
| 6 | `tdx_get_research_reports(code)` | F16 研报评级 | `f10_reports` | 交易日 | 1（东财研报） |
| 7 | `tdx_get_industry_analysis(code)` | F15 行业分析 | `f10_industry` | 固定 7 天 | 1（东财板块） |

**ROI 排序**（一次调用替代的接口数）：
1. `tdx_get_latest_reminders` — 一次调用替代 4 个 HTTP 接口（最高 ROI）
2. `tdx_get_financial_analysis` — 一次调用替代 3 个新浪接口
3. `tdx_get_shareholder_research` — 一次调用替代 2 个东财接口
4. 其余 4 个函数 — 各替代 1 个接口

### 3.4 实施位置

#### 3.4.1 数据获取层（`tdx_client.py`）
- 新增 7 个 F10 函数，复用 `_TDX_CALL_LOCK` / `_tdx_throttle` / `_get_tdx_client` 基础设施
- 每个函数返回结构化 dict，解析逻辑封装在函数内部

#### 3.4.2 数据源适配层（`stock_common/sc_datasource.py`）
- 新增 7 个 F10 适配函数（如 `get_block_trade_f10`、`get_margin_trading_f10` 等）
- 作为现有 HTTP 函数的**优先源**：先调 F10，失败时 fallback 到原 HTTP 函数
- 保留原 HTTP 函数完整签名，确保稳定性

#### 3.4.3 报告脚本层（6 个脚本）
- 修改 6 个报告脚本的导入，优先调用 F10 版本
- 具体修改点：
  - `get_sht_report.py`：第十二章大宗交易、第十一章融资融券、第十四章新闻/互动
  - `get_med_report.py`：第三章财务（新浪→F10）、第八章筹码、第十二章两融、第十三章大宗、第十六章股东
  - `get_lng_report.py`：第二章财务（新浪→F10）、第六章股东、第七章限售
  - `get_val_report.py`：策略 11 筹码、策略 13 红利、策略 17 北向（保留 HTTP）
  - `get_ful_report.py`：Layer 2 研报、Layer 4 筹码/两融/大宗、Layer 5 新闻、Layer 6 财务
  - `get_mak_report.py`：B 节公告（已用 F10 兜底）

### 3.5 函数签名设计

```python
# 1. 最新提示（一次调用获 8 类数据）
def tdx_get_latest_reminders(code: str) -> dict:
    """返回: {
        "latest_indicators": {eps, net_asset, roe, share_capital, ...},
        "interaction_qa": [{question, answer, date}, ...],
        "latest_announcements": [{title, date}, ...],
        "latest_news": [{title, date}, ...],
        "abnormal_movements": [...],
        "block_trades": [...],
        "margin_trading": {...},
        "risk_warnings": [...]
    }"""

# 2. 公司报道（含正文摘要）
def tdx_get_company_news_f10(code: str, count: int = 10) -> list:
    """返回: [{title, date, summary, url}, ...]"""

# 3. 财务分析（10 子栏目）
def tdx_get_financial_analysis(code: str) -> dict:
    """返回: {
        "main_indicators": [...],      # 主要财务指标（多期）
        "solvency": {...},             # 偿债能力
        "operation": {...},            # 营运能力
        "profitability": {...},        # 盈利能力
        "growth": {...},               # 成长能力
        "indicator_changes": [...],    # 指标变动说明
        "balance_sheet": [...],        # 资产负债表摘要
        "income_statement": [...],     # 利润表摘要
        "cash_flow": [...],            # 现金流量表摘要
        "qoq_analysis": [...]          # 环比分析
    }"""

# 4. 股东研究（7 子栏目）
def tdx_get_shareholder_research(code: str) -> dict:
    """返回: {
        "controlling_shareholder": {...},   # 控股股东/实际控制人
        "planned_changes": [...],           # 股东增减持计划
        "major_holder_changes": [...],      # 重要股东持股变动
        "shareholder_changes": [...],       # 股东变化（十大流通）
        "holder_count": [...],              # 股东人数变化
        "same_controller_stocks": [...],    # 同大股东个股
        "fund_holdings": [...]              # 基金持股
    }"""

# 5. 股本结构（4 子栏目）
def tdx_get_share_capital(code: str) -> dict:
    """返回: {
        "structure": {...},          # 股本结构（A/B/H/限售）
        "changes": [...],            # 股本变化历史
        "lockup_expiry": [...],      # 限售解禁时间表
        "buyback": [...]             # 股票回购记录
    }"""

# 6. 研报评级
def tdx_get_research_reports(code: str, count: int = 10) -> list:
    """返回: [{institution, date, rating, target_price, title}, ...]"""

# 7. 行业分析
def tdx_get_industry_analysis(code: str) -> dict:
    """返回: {
        "industry_position": {...},   # 行业地位
        "industry_trend": [...],      # 行业趋势
        "industry_comparison": [...]  # 行业对比
    }"""
```

### 3.6 预计工作量

约 800-1000 行代码（含 7 个 F10 函数 + 7 个适配函数 + 6 个脚本导入修改）。

---

## 四、阶段二：纯新增内容（丰富报告维度）

### 4.1 目标

新增 **22 个项目当前完全缺失的数据维度**，报告维度扩展 30%+。

### 4.2 纯新增内容清单

| # | F10 分类/子栏目 | 新增数据维度 | 主要受益脚本 | 价值评级 |
|---|----------------|-------------|-------------|---------|
| 1 | F2-1.5 最新异动 | 异动信息 | sht/ful | 🔴 高 |
| 2 | F2-1.8 风险提示 | 风险警示 | sht/ful（强化杀猪盘检测） | 🔴 高 |
| 3 | F2-2.2 发行交易 | IPO 数据/发行价 | lng/val | 🟡 中 |
| 4 | F2-2.4 研发投入 | 研发费用/人员占比 | lng/val（科技股估值核心） | 🔴 高 |
| 5 | F2-2.5 参股控股 | 参股控股公司 | lng/ful（隐藏价值发现） | 🟡 中 |
| 6 | F3-3.2 偿债能力 | 资产负债率/流动比率 | med/lng/ful（财务排雷） | 🔴 高 |
| 7 | F3-3.3 营运能力 | 存货周转/应收周转 | med/lng/ful | 🟡 中 |
| 8 | F3-3.5 成长能力 | 营收/利润增长率 | med/lng/val | 🔴 高 |
| 9 | F3-3.9 现金流量表 | 现金流三表之一 | med/lng/ful（现金流健康度） | 🔴 高 |
| 10 | F3-3.10 环比分析 | QoQ 财报对比 | med/lng（拐点发现） | 🟡 中 |
| 11 | F4-4.4 股票回购 | 回购记录 | sht/med/lng（正面信号） | 🟡 中 |
| 12 | F5-5.1 控股股东 | 控股关系链 | med/lng/ful | 🟡 中 |
| 13 | F5-5.2 股东增减持计划 | 增减持公告 | sht/med/lng | 🔴 高 |
| 14 | F5-5.3 重要股东变动 | 前十大股东变动 | med/lng/ful | 🟡 中 |
| 15 | F5-5.6 同大股东个股 | 同控股股东其他公司 | lng（联动分析） | 🟢 低 |
| 16 | F5-5.7 基金持股 | 基金持股明细 | med/lng（机构认可度） | 🟡 中 |
| 17 | F7-7.2 融资 | IPO/增发/配股历史 | lng/val | 🟢 低 |
| 18 | F8 高管治理 | 高管/薪酬/持股 | lng/ful | 🟢 低 |
| 19 | F9 资本运作 | 并购重组结构化数据 | sht/med/lng（重大事件） | 🟡 中 |
| 20 | F10 经营分析 | 主营构成/分项毛利率 | med/lng/val（业务结构） | 🔴 高 |
| 21 | F2-2.3 员工效益 | 员工数/人均薪酬 | lng（人效分析） | 🟢 低 |
| 22 | F3-3.6 指标变动说明 | 财报变动归因 | med/lng | 🟢 低 |

### 4.3 新增函数（在 `tdx_client.py` 中）

| # | 函数名 | F10 分类 | 缓存 key | 缓存模式 |
|---|--------|---------|---------|---------|
| 1 | `tdx_get_company_overview(code)` | F2 公司概况（含研发投入/参股控股） | `f10_overview` | 固定 30 天 |
| 2 | `tdx_get_operation_analysis(code)` | F10 经营分析（主营构成） | `f10_operation` | 固定 90 天 |
| 3 | `tdx_get_capital_operation(code)` | F9 资本运作（并购重组） | `f10_capital_op` | 固定 7 天 |
| 4 | `tdx_get_governance(code)` | F8 高管治理 | `f10_governance` | 固定 30 天 |
| 5 | `tdx_get_hot_themes(code)` | F11 热点题材（含关联理由） | `f10_themes` | 固定 3 天 |

### 4.4 实施位置

#### 4.4.1 丰富原章节（13 项，融入现有结构）

| F10 分类 | 融入章节 | 涉及脚本 | 实施方式 |
|---------|---------|---------|---------|
| F2-1.1 最新主要指标 | 「基本面」/「财务健康」 | sht/med/lng/ful | 替代分散的 ROE/EPS 获取 |
| F2-1.2 互动问答 | 「情绪与事件催化」 | sht/ful | 替代 `cninfo_irm` HTTP |
| F2-1.3 最新公告 | 「公告」 | sht/med/lng/ful | 巨潮失败时 F10 兜底（已实现） |
| F2-1.4 最新报道 | 「新闻舆情」 | sht/ful | 替代东财 search-api |
| F2-1.6 大宗交易 | 「大宗交易」 | sht/med/lng | 替代东财 datacenter |
| F2-1.7 融资融券 | 「融资融券」 | sht/med/lng | 替代东财 datacenter |
| F3 财务分析（部分） | 「基本面」/「财务健康」 | med/lng/ful | 替代新浪三表 |
| F4-4.3 限售解禁 | 「限售解禁」 | sht/med/lng/ful | 替代东财 datacenter |
| F5-5.4 股东变化 | 「筹码/股东」 | med/lng/ful | 替代东财 datacenter |
| F5-5.5 股东人数 | 「筹码/股东」 | sht/med/lng | 已有 TDX 兜底，F10 作为对比 |
| F7 热点题材 | 「题材概念」 | sht/med/ful | 补充关联理由字段 |
| F13 公司报道 | 「新闻舆情」 | sht/ful | 替代东财 search-api |
| F16 研报评级 | 「机构研报」 | sht/med/lng/ful | 替代东财 reportapi |

#### 4.4.2 新建章节（6 项，F10 提供全新维度）

| F10 分类 | 新建章节名 | 涉及脚本 | 价值 |
|---------|-----------|---------|------|
| F2-1.5/1.8 异动与风险 | 「异动与风险提示」 | sht/ful | 强化短线信号 + 杀猪盘检测 |
| F2-2.4 研发投入 | 「研发与创新」 | lng/val | 科技股估值核心 |
| F3-3.2/3.3/3.5 财务扩展 | 「财务深度分析」 | med/lng/ful | 偿债/营运/成长能力 |
| F4-5.1/5.2/5.3 股东扩展 | 「股东行为分析」 | med/lng/ful | 增减持/控股关系 |
| F8 高管治理 | 「治理结构」 | lng/ful | 长线投资参考 |
| F10 经营分析 | 「主营构成分析」 | med/lng/val | 业务结构诊断 |

### 4.5 预计工作量

约 600-800 行代码（含 5 个 F10 函数 + 章节融入 + 新建章节）。

---

## 五、阶段三：对比核查（数据质量提升）

### 5.1 目标

用 F10 数据核查现有 TDX/HTTP 数据准确性，提升报告数据可信度。

### 5.2 新增函数

| # | 函数名 | 对比目标 | 核查价值 |
|---|--------|---------|---------|
| 1 | `tdx_verify_fund_flow(code)` | F9 资金动向 vs TDX `tdx_get_fund_flow` | 校验 TDX 实时资金流准确性 |
| 2 | `tdx_verify_financials(code)` | F3 财务分析 vs 新浪三表 | 校验新浪财报数据完整性 |
| 3 | `tdx_verify_shareholder(code)` | F5 股东人数 vs 东财 `holder_change` | 校验股东户数变化趋势 |

### 5.3 实施位置

- 在报告末尾新增「数据质量核查」附录
- 差异 > 20% 时在报告中标记警告
- 不影响主流程，仅作为数据质量提示

### 5.4 对比核查矩阵（完整版）

| F10 分类 | 对比目标 | 核查价值 | 实施方式 |
|---------|---------|---------|---------|
| F9 资金动向 | TDX `tdx_get_fund_flow` | 校验 TDX 实时资金流准确性 | 双源对比，差异>20% 时标记 |
| F3 财务分析 | 新浪三表 | 校验新浪财报数据完整性 | F10 为主源，新浪兜底 |
| F4 股本结构 | TDX `tdx_get_dividend_history` | 校验除权除息记录 | 双源对比，发现送转差异 |
| F7 分红融资 | TDX `tdx_get_dividend_history` | 校验分红记录 | F10 含预案/实施进度，TDX 仅有历史 |
| F5-5.5 股东人数 | 东财 `holder_change` | 校验股东户数变化趋势 | F10 提供季度数据，东财提供 10 期历史 |

### 5.5 预计工作量

约 300-400 行代码。

---

## 六、阶段四：缓存优化（已批准方案 B）

### 6.1 目标

F10 数据更新频率低（每日 1 次），通过按交易日过期的缓存策略，避免休市期间不必要的重复请求。

### 6.2 实施方式

1. **扩展 TTL 字典**：新增 16 个 `f10_` 前缀分类
2. **新增 `get_last_trading_day(d=None)` 函数**：在 `stock_common/stock_calendar.py` 中
3. **扩展 `@cached` / `@cached_async` 装饰器**：新增 `trading_day: bool = False` 参数
4. **扩展 `set_cache`**：新增 `trading_day` 参数分支，计算 `expires_at = 下一个交易日的 15:00`
5. **`get_cache` 不修改**：复用现有 `WHERE expires_at > now` 逻辑

### 6.3 代码改动清单

| 文件 | 改动内容 | 改动性质 |
|------|---------|---------|
| `stock_cache.py` | TTL 字典新增 16 个 F10 分类 | 纯新增 |
| `stock_cache.py` | `@cached` / `@cached_async` 新增 `trading_day` 参数 | 纯新增（默认 False） |
| `stock_cache.py` | `set_cache` 新增 `trading_day` 参数分支 | 纯新增（默认 False） |
| `stock_common/stock_calendar.py` | 新增 `get_last_trading_day(d=None)` | 纯新增 |
| `tdx_client.py` | 7 个 F10 函数加 `@cached` 装饰器 | 纯新增 |

**重要**：不修改 `get_cache`、不修改现有 22 个分类的 TTL、不修改现有函数签名。

### 6.4 预计工作量

约 150-200 行代码。

---

## 七、实施优先级与里程碑

### 7.1 优先级矩阵

| 优先级 | 阶段 | 收益 | 风险 | 建议时机 |
|--------|------|------|------|---------|
| 🔴 P0 | 阶段四（缓存优化） | 所有 F10 函数的基础设施 | 低 | 最先实施 |
| 🔴 P0 | 阶段一（核心替代） | 东财 HTTP 调用减少 60%+，限流风险大幅降低 | 低（保留 HTTP fallback） | 紧随阶段四 |
| 🟡 P1 | 阶段二（纯新增） | 报告维度扩展 30%+，基本面分析更全面 | 中（需设计新章节） | 阶段一完成后 |
| 🟢 P2 | 阶段三（对比核查） | 数据质量提升 | 低（仅追加附录） | 阶段二完成后 |

### 7.2 实施顺序（推荐）

```
阶段四（缓存基础） → 阶段一函数1（最新提示） → 验证 → 阶段一函数2-7 → 阶段二 → 阶段三
```

**关键原则**：每完成一个 F10 函数就立即验证并接入报告脚本，避免大批量修改带来的风险。

### 7.3 阶段一函数实施顺序（按 ROI 排序）

| 顺序 | 函数 | 替代接口数 | 缓存模式 | 验证点 |
|------|------|-----------|---------|--------|
| 1 | `tdx_get_latest_reminders` | 4 | 交易日 | 8 子栏目解析正确 |
| 2 | `tdx_get_financial_analysis` | 3 | 固定 90 天 | 10 子栏目解析正确 |
| 3 | `tdx_get_shareholder_research` | 2 | 固定 7 天 | 7 子栏目解析正确 |
| 4 | `tdx_get_share_capital` | 1 | 固定 7 天 | 限售解禁数据准确 |
| 5 | `tdx_get_company_news_f10` | 1 | 交易日 | 含正文摘要 |
| 6 | `tdx_get_research_reports` | 1 | 交易日 | 评级/目标价完整 |
| 7 | `tdx_get_industry_analysis` | 1 | 固定 7 天 | 行业地位字段 |

---

## 八、文件结构规划

### 8.1 新增文件

```
stock_common/
├── f10_parser.py        # F10 文本解析工具（通用表格解析器，处理 ┌┬┐├┼┤└┴┘─│ 格式）
└── sc_f10.py            # F10 数据获取 + 解析封装（16 个分类的高层 API）
```

### 8.2 修改文件

| 文件 | 修改内容 | 阶段 |
|------|---------|------|
| `stock_cache.py` | TTL 字典扩展 + 装饰器 `trading_day` 参数 | 阶段四 |
| `stock_common/stock_calendar.py` | 新增 `get_last_trading_day` | 阶段四 |
| `tdx_client.py` | 新增 7+5+3=15 个 F10 函数 | 阶段一/二/三 |
| `stock_common/sc_datasource.py` | 新增 7 个 F10 适配函数 | 阶段一 |
| `get_sht_report.py` | 导入修改 + 章节融入 | 阶段一/二 |
| `get_med_report.py` | 导入修改 + 章节融入 + 新建章节 | 阶段一/二 |
| `get_lng_report.py` | 导入修改 + 章节融入 + 新建章节 | 阶段一/二 |
| `get_val_report.py` | 导入修改 + 策略融入 | 阶段一/二 |
| `get_ful_report.py` | 导入修改 + Layer 融入 + 新建章节 | 阶段一/二 |
| `get_mak_report.py` | 公告兜底（已实现） | — |

---

## 九、风险控制

### 9.1 技术风险

| 风险 | 等级 | 说明 | 缓解措施 |
|------|------|------|----------|
| 解析格式不稳定 | 中 | F10 文本格式可能随版本变化 | 加 try/except，解析失败返回空，不影响主流程 |
| 数据时效性 | 低 | F10 数据每日更新，T+1 延迟 | 对时效性要求高的数据（如实时行情）不用 F10 |
| TDX 连接不稳定 | 低 | 已修复连接问题，有兜底机制 | HTTP 数据源作为主源，TDX F10 作为补充 |
| 解析性能 | 低 | 单股全量解析约 1-2 秒 | 按需解析，只解析需要的分类 |
| 缓存集成影响现有分类 | 高 | 修改缓存逻辑可能影响 22 个现有分类 | **不修改现有逻辑**，只新增 `trading_day` 参数 |

### 9.2 业务风险

| 风险 | 等级 | 说明 | 缓解措施 |
|------|------|------|----------|
| F10 数据与 HTTP 数据不一致 | 中 | 两个数据源可能有细微差异 | 阶段三的对比核查机制 |
| 报告章节膨胀 | 中 | 新增章节过多导致报告过长 | 按报告类型（sht/med/lng）选择性展示 |
| fallback 逻辑复杂 | 中 | F10 失败时回退到 HTTP，逻辑链长 | 封装在 sc_datasource 适配函数中，对报告脚本透明 |

---

## 十、对焦检查清单

> 每完成一个函数/阶段，对照以下清单确认：

### 10.1 缓存对焦检查

- [ ] F10 分类是否使用 `f10_` 前缀？
- [ ] 高频分类（5 个）是否用 `trading_day=True`？
- [ ] 低频分类（11 个）是否用固定 TTL？
- [ ] 现有 22 个分类的 TTL 是否未修改？
- [ ] `get_cache` 是否未修改？
- [ ] `set_cache` 是否只新增了 `trading_day` 分支？

### 10.2 函数对焦检查

- [ ] 函数是否在 `tdx_client.py` 中？
- [ ] 是否复用 `_TDX_CALL_LOCK` / `_tdx_throttle` / `_get_tdx_client`？
- [ ] 返回值是否为结构化 dict/list？
- [ ] 是否加了 `@cached` 装饰器？
- [ ] 是否有 try/except 保护？

### 10.3 适配层对焦检查

- [ ] 是否在 `sc_datasource.py` 中新增了适配函数？
- [ ] 是否作为现有 HTTP 函数的优先源？
- [ ] HTTP fallback 是否保留？
- [ ] 报告脚本是否优先调用 F10 版本？

### 10.4 报告脚本对焦检查

- [ ] 修改是否限于导入和函数调用？
- [ ] 现有章节是否未被破坏？
- [ ] 新建章节是否符合脚本定位（sht/med/lng）？
- [ ] fallback 失败时是否不影响主流程？

---

## 十一、总结

TDX F10 是一个被严重低估的高质量数据源。16 个分类覆盖了公司基本面的方方面面，且数据权威、稳定、不被反爬。本 Roadmap 规划了四阶段实施路径：

1. **阶段四（缓存基础）**：建立按交易日过期的缓存机制，是所有 F10 函数的基础设施
2. **阶段一（核心替代）**：用 F10 替代 12 个 HTTP 接口，大幅降低限流风险
3. **阶段二（纯新增）**：新增 22 个数据维度，丰富报告内容
4. **阶段三（对比核查）**：用 F10 核查现有数据，提升数据质量

**核心原则**：
- 增量扩展，不重构现有代码
- 保留 HTTP fallback，确保稳定性
- 每完成一个函数立即验证，避免大批量修改风险
- 缓存方案不影响现有 22 个分类
