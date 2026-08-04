# 脚本应用接口与字段来源字典 (Script Data Dictionary)

> **创建日期**：2026-07-28
> **更新日期**：2026-08-05（V16.1：ful 下线 → 5 大脚本；新数据源接入）
> **基于**：[field_dict.md](file:///d:/GitHub/test/docs/field_dict.md)（V16.1 字段元数据，§12 多源字典）
> **目的**：明确每个脚本的每个字段从哪个接口获取、走哪个中间层函数、单位/含义如何、**优先级**，与 field_dict 形成"双字典"对照。
> **使用原则**：脚本调整前必查，避免重复反向工程；优先采用本字典已确定的中间层函数。
> **V16.1 变化**：① `get_ful_report.py` 已下线（技术/风险引擎迁移至 `sc_technical.py`/`sc_risk.py`）② push2 字段包 19→50（涨停/跌停价/EPS/BPS/52周/资金流 12 字段）③ 评分权重可配置（scoring_sht/med/lng）④ 新数据源（levistock/AxData）已录入 field_dict §12.10-12.14，脚本未接入但可扩展

---

## 一、 三层数据源架构

```
┌──────────────────────────────────────────────────────────┐
│ Layer 1: ZHB 本地数据包（TCP 7709，easy_tdx 首选下载）      │
│   - V16.1.1: zhb.zip 下载 easy_tdx get_report_file 首选    │
│     （实测 180.153.18.170 成功），mootdx 备胎               │
│   - 含 45 个文件（tdxstat/tdxstat2/tipinfo/profile.dat/…）│
│   - 数据日期 = 包内数据日期 = 上一交易日（T-1）             │
├──────────────────────────────────────────────────────────┤
│ Layer 2: TDX TCP 协议（easy_tdx 1.20.4 适配层首选）         │
│   - V15.5: _EasyTdxAdapter 包装 easy_tdx → mootdx 兼容     │
│   - 健康分引擎 + K线空数据故障转移 + 52 候选服务器           │
│   - 0x0010 GetFinanceInfo → 单只股票 36 字段               │
│   - mootdx/pytdx 为备胎（0.11.7 行情类接口实测失效）        │
├──────────────────────────────────────────────────────────┤
│ Layer 3: HTTP 网络（东财/腾讯/同花顺/新浪）                 │
│   - 走 aiohttp + 令牌桶 + 熔断器 + 分域名限流（18 域名）    │
│   - 数据日期 = T（实时）                                   │
│   - ZHB 缺失或需最新数据时调用                              │
└──────────────────────────────────────────────────────────┘
```

### 字段时效性分类（基于 field_dict.md 第 5.2 节）

| 类别 | 字段示例 | 数据延迟 | HTTP 必要性 |
|:---|:---|:---:|:---:|
| **行情类（实时）** | price/change_pct/amount/volume/open/high/low/prev_close | T | **必须** |
| **资金流类（准实时）** | main_net_buy_hands/amount | T-1 | 盘中必须 |
| **估值类（静态）** | pe_ttm/pe_dynamic/pb/dividend_yield/turnover_pct | T-1 | 不需要 |
| **财务类（静态）** | net_profit/revenue/roe/eps | 季度 | 不需要 |
| **股本类（静态）** | total_shares/float_shares/mcap | 长期 | 不需要 |
| **历史涨跌幅（静态）** | change_5d/10d/20d/30d/60d/ytd | T-1 | 不需要 |
| **52周/IPO/员工（静态）** | high_52w/low_52w/ipo_price/employee_count | 长期 | 不需要 |
| **板块/题材（静态）** | industry/concept/board | 长期 | 不需要 |

---

## 二、 data_provider 统一接口（按字段归类）

> **设计原则**：**所有脚本统一通过 `data_provider` 或 `CanonicalStockData` 获取数据**，不再直接调用 `tdx_client` 或 HTTP。

### 2.1 行情/资金流（实时类）

| 字段 | 推荐函数 | 优先级 | 备注 |
|:---|:---|:---:|:---|
| `price` | `get_stock_price(code)` | ZHB → TDX → 腾讯 HTTP | 盘前 ZHB，盘中 TDX |
| `change_pct` | `get_change_pct(code)` | ZHB → TDX → 腾讯 HTTP | 同上 |
| `change_pct_1d/2d` | `cdata.change_pct_1d/2d` | ZHB 字段 | `tdxstat.cfg Col[7/8]` |
| `amount_wan` | `get_amount_wan(code)` | 盘后 ZHB / 盘中腾讯 → TDX | 单位：万元 |
| `amount_1d/2d` | `cdata.amount_1d/2d` | ZHB 字段 | `tdxstat2.cfg Col[5/7]` |
| `volume` | `cdata.volume_hand` | ⚠️ ZHB 不可用（5 天不变） | 用 HTTP 实时 |
| `open/high/low/prev_close` | `cdata.open/high/low/prev_close` | ZHB → TDX → 腾讯 | |
| `main_net_buy` | `get_main_net_buy(code)` | ZHB → TDX(实 HTTP) | 返回 dict |
| `main_net_buy_hands` | `cdata.main_net_buy_hands` | ZHB → TDX | 手数 |
| `main_net_buy_amount` | `cdata.main_net_buy_wan` | ZHB → TDX | 万元 |

### 2.2 估值/财务（静态类）

| 字段 | 推荐函数 | 优先级 | 备注 |
|:---|:---|:---:|:---|
| `pe_ttm` | `get_pe_ttm(code)` | ZHB only | T-1 |
| `pe_dynamic` | `cdata.pe_dynamic` | ZHB | 静态 PE（最新年报） |
| `pb` | `get_pb(code)` | ZHB only | T-1 |
| `dividend_yield` | `get_dividend_yield(code)` | ZHB only | 单位：% |
| `turnover_pct` | `get_turnover_pct(code)` | ZHB only | 单位：% |
| `net_profit` | `cdata.net_profit` | ZHB | 万元（需/10000 转元） |
| `revenue` | `cdata.revenue` | ZHB | 万元 |
| `roe` | `cdata.roe` | ZHB → `tdx_get_finance_roe` | 单位：% |
| `eps` | `cdata.eps` | ZHB（`tipinfo.dat Col[3]`）| 元/股 |
| `gross_margin` | `cdata.gross_margin` | ZHB | 单位：% |

### 2.3 股本/市值（静态类）

| 字段 | 推荐函数 | 优先级 | 备注 |
|:---|:---|:---:|:---|
| `total_shares` | `get_totals(code)` | 本地缓存 → ZHB | 单位：万股 |
| `float_shares` | `get_share_capital(code)` | 本地缓存 | 单位：万股 |
| `mcap` | `calc_mcap_yi(code, price)` | 动态计算 | 单位：亿元 |
| `float_mcap` | `get_market_cap(code)` | ZHB → 动态 | 单位：亿元 |
| `mcap_yi` | `cdata.mcap_yi` | 动态 | 单位：亿元 |
| `float_mcap_yi` | `cdata.float_mcap_yi` | 动态 | 单位：亿元 |
| `holder_count` | `cdata.holder_count` | ZHB（`tdxstat2` 计算）| 单位：户 |

### 2.4 历史涨跌幅（静态类）

| 字段 | 推荐函数 | 优先级 | 备注 |
|:---|:---|:---:|:---|
| `change_5d/10d/20d/60d/ytd` | `cdata.change_5d/10d/20d/60d/ytd` | ZHB | `tdxstat.cfg Col[28/30/17/19/21]` |
| `change_30d` | **未通过 CanonicalStockData 暴露** | ZHB | `tdxstat.cfg Col[18]` |
| `streak_days` | `get_streak_days(code)` | ZHB | `tdxstat.cfg Col[5]` |

### 2.5 52周/IPO/员工（静态类）

| 字段 | 推荐函数 | 优先级 | 备注 |
|:---|:---|:---:|:---|
| `high_52w` | `get_52w_range(code)[0]` | ZHB → TDX K线 | `tdxstat2.cfg Col[17]` |
| `low_52w` | `get_52w_range(code)[1]` | ZHB → TDX K线 | `tdxstat2.cfg Col[18]` |
| `ipo_price` | `cdata.ipo_price` | ZHB | `tdxstat2.cfg Col[16]` |
| `employee_count` | `cdata.employee_count` | ZHB | `tdxstat.cfg Col[15]` |
| `ipo_date` | `cdata.list_date` | TDX 0x0010 → HTTP 兜底 | `tdx_finance_info Col[6]` |
| `updated_date` | （ZHB 财报事件锁） | ZHB | `tdx_finance_info Col[5]` |

### 2.6 板块/概念（静态类）

| 字段 | 推荐函数 | 优先级 | 备注 |
|:---|:---|:---:|:---|
| `industry` | `cdata.industry` | **TDX boards** | ⚠️ ZHB dict 无此 key |
| `industry_code` | `cdata.industry_code` | ZHB（动态概念板块代码）| ⚠️ **不是固定行业归属** |
| `board` | `cdata.board` | TDX boards | |
| `concept` | `cdata.concepts` | TDX boards | ⚠️ `get_concept_from_zhb` 当前返回空 |
| `concept_chain` | `get_concept_chain_from_zhb()` | ZHB | ⚠️ 当前仅 80 个节点 |

---

## 三、 tdx_client 函数（部分函数名误导）

> **警告**：tdx_client 中部分 `tdx_*` 函数实际委托给 HTTP，**不是 TDX 协议**！脚本中应按实际数据源评估。

| 函数名 | 实际数据源 | 推荐替代 | 备注 |
|:---|:---|:---|:---|
| `tdx_get_quote_full` | 腾讯 HTTP + TDX TCP 补强 | `data_provider.get_stock_price` | HTTP 在前！ |
| `tdx_get_index_quote` | TDX → 腾讯 HTTP | （无统一函数）| TDX 优先 ✅ |
| `tdx_get_fund_flow` | **HTTP 东财** | `data_provider.get_main_net_buy` | 改名 `em_get_fund_flow` |
| `tdx_get_history_fund_flow` | **HTTP 东财** | （脚本内自定义）| 改名 `em_get_history_fund_flow` |
| `tdx_get_finance_info` | TDX 0x0010 | `tdx_client.tdx_get_finance_info` | ✅ 36 字段 |
| `tdx_get_finance_roe` | TDX 0x0010 | `tdx_client.tdx_get_finance_roe` | ✅ jinglirun/jingzichan |
| `tdx_get_dividend_history` | TDX xdxr | `tdx_client.tdx_get_dividend_history` | ✅ |
| `tdx_get_eps_from_reports` | **HTTP 东财研报** | （保留）| 研报中心 |
| `tdx_get_latest_reminders` | TDX F10 | `tdx_client.tdx_get_latest_reminders` | 公告/融资融券 |
| `tdx_get_belong_boards` | TDX 板块 | `sc_datasource.get_concept_blocks` | ✅ 行业+概念+地域 |
| `tdx_get_board_list/members/by_name` | TDX 板块 | （直接调用）| ✅ |

### 3.5 V15.4.3 easy_tdx 兼容性（V15.5 移植前置）

> **2026-07-31 实跑 easy_tdx v1.17.10**（本地已装）+ GitHub v1.20.4 源码对照。
> **结论**：保留 V15 强类型 cdata 架构，**仅借鉴 easy_tdx 的 `_health.py` 服务器健康分引擎 + `_reconnect.py` K 线空数据故障转移**。
> **完整字段表**：[docs/tdx_field_dict.md](tdx_field_dict.md)

#### easy_tdx 关键 dataclass 与本项目函数对应

| easy_tdx dataclass | 本项目 V15 函数 | 字段对应 | V15.5 移植状态 |
|:---|:---|:---|:---:|
| `SecurityBar`（K 线 12 字段）| `tdx_get_security_bars` | `vol` 单位差异（手 vs 股）| ⏳ |
| `SecurityQuote`（五档 30+ 字段）| `tdx_get_quote_full`（7 字段）| s_vol/b_vol/bid1-5 缺失 | ⏳ |
| `FinanceInfo`（财务 32 字段）| `tdx_get_finance_info`（3 字段）| 缺 22 个资产负债+利润字段 | ⏳ |
| `XdxrRecord`（除权除息 18 字段）| ❌ 无（V9.6 删）| fenhong/每 10 股 | ⏳ V15.8 |
| `SecurityInfo`（证券 9 字段）| n/a | industry_tdx/sw 新增 | ⏳ |
| `FundFlow` / `HistoricalFundFlow` | `tdx_get_fund_flow` | 字段直接对应 | ⏳ |
| `MarketStat`（10 字段）| mak 报告"市场概况" | 字段直接对应 | ⏳ |
| Enum `Market` / `KlineCategory` | `Market` 未用；`frequency` 参数 | 100% 对应 | ✅ 已对齐 |

#### 关键结论

1. **`KlineCategory` 与 `frequency` 100% 对应**——`MIN_1=7`, `MIN_5=0`, `DAY=4`, `WEEK=5`, `MONTH=6`, `YEAR=9`（V3.2.5 已修复）
2. **本项目 V15 已用 `frequency` 参数**（不用 easy_tdx 旧的 `category`）
3. **V15.5 移植 health/reconnect 是顶层任务**（15.143-15.152 已在 roadmap）
4. **V15.7 移植 7 个新字段**：`industry_tdx`/`industry_sw`/`rise_speed`/`s_vol`/`b_vol`/`trading_status`/`open_amount`

详见 [roadmap.md V15.4.3/V15.5](roadmap.md) + [tdx_field_dict.md](tdx_field_dict.md)。

---

## 四、 sc_datasource 函数（HTTP 层）

| 函数 | 数据源 | 推荐替代 | 备注 |
|:---|:---|:---|:---|
| `get_tencent_quote` | HTTP 腾讯 | `data_provider.get_stock_price` | ⚠️ 优先用 data_provider |
| `get_em_batch_quotes` | HTTP 东财 | （保留）| 批量行情 |
| `get_stock_info` | HTTP 腾讯 + TDX | `data_provider.get_stock_composite` | ⚠️ **包含 5 处错配 key** |
| `get_reports` | HTTP 东财 | （保留）| 个股研报 |
| `get_eps_forecast` | HTTP 同花顺 → TDX 兜底 | （保留）| |
| `get_northbound_hold` | HTTP 东财 + CSV 缓存 | （保留）| |
| `get_margin_trading` | TDX F10 → HTTP 东财 | （保留）| |
| `get_block_trade` | HTTP 东财 | （保留）| |
| `get_dividend_history` | TDX xdxr | （保留）| |
| `get_concept_blocks` | TDX belong_boards | （保留）| |
| `get_ths_hot_reason` | HTTP 同花顺 | （保留）| |
| `get_industry_peers` | TDX boards | （保留）| |
| `get_industry_comparison` | TDX + HTTP 东财补充 | （保留）| |
| `get_eastmoney_stock_news` | HTTP 东财 | （保留）| |
| `get_sina_financial_report` | HTTP 新浪 | （保留）| 12 期历史 |
| `get_sina_balance_sheet` | HTTP 新浪 | （保留）| 5 期历史 |
| `get_eastmoney_cash_flow` | HTTP 东财 | （保留）| 现金流量表 |
| `get_hsgt_macro_flow` | HTTP 同花顺 | （保留）| 北向大盘 |
| `get_lockup_expiry` | TDX F10 | （保留）| 解禁 |
| `get_gross_margin_and_roe` | HTTP 新浪 | （保留）| |
| `get_valuation_pe_center` | HTTP 新浪 | （保留）| |
| `get_market_status` | TDX index_quote | （保留）| |
| `get_limit_up_pool/broken/down` | HTTP 同花顺 | （保留）| |
| `get_eastmoney_minute_fund_flow` | HTTP 东财 | （保留）| |
| `get_fund_flow_weighted` | TDX + HTTP 融合 | （保留）| |
| `get_zhb_*` | ZHB 本地 | （保留）| |
| `get_share_capital` | 本地缓存 | （保留）| |
| `get_dragon_tiger_board` | HTTP 东财 | （保留）| 龙虎榜 |
| `eastmoney_stock_info_push2` | HTTP 东财 | （保留）| list_date 兜底 |
| `get_em_board_*` | HTTP 东财 | （保留）| |
| `get_em_belong_boards` | HTTP 东财 | **改用 `get_concept_blocks`** | 仅 industry/area |
| `get_em_fund_flow` | HTTP 东财 | `data_provider.get_main_net_buy` | |
| `get_em_history_fund_flow` | HTTP 东财 | `tdx_get_history_fund_flow` | |

---

## 五、 6 大报告脚本字段调用矩阵

### 5.1 get_sht_report.py（短线 / Strategy A-E）

| 行号 | 字段访问 | 推荐中间层 | 数据源 |
|:---:|:---|:---|:---|
| 107 | `ff["main_net_wan"]` | `get_main_net_buy` | ZHB/TDX |
| 113 | `ff_120d["data"]` | `tdx_get_history_fund_flow` | HTTP 东财 |
| 336 | `cdata.industry or info.get('industry')` | `get_industry` | TDX boards |
| 422 | `q.get('open'/'price'/'change_pct')` | `get_quote_full` | HTTP+TDX |
| 441 | `ff.iloc[0].get('net_main')` | `tdx_get_fund_flow` | HTTP 东财 |
| 561 | `blocks["industry"]` | `get_concept_blocks` | TDX boards |
| 567 | `info.get('industry')` | `get_industry` | TDX boards |
| 571 | `blocks["industry"][0].get("name")` | `get_concept_blocks` | TDX boards |
| 684 | `q.get('pe_ttm'/'turnover_pct')` | `get_pe_ttm`/`get_turnover_pct` | ZHB |
| 708 | `q.get('amount_wan')` | `get_amount_wan` | ZHB/HTTP |
| 715 | `_composite["streak_days"]` | `get_streak_days` | ZHB |
| 732-748 | `ff["data"]` | `tdx_get_history_fund_flow` | HTTP 东财 |
| 772-782 | `d.get('market_cap'/'hold_ratio'/'hold_shares')` | `get_northbound_hold` | HTTP 东财 |
| 809-833 | `dtb["records"]/["seats"]` | `get_dragon_tiger_board` | HTTP 东财 |
| 960 | `lh["change_ratio"]` | `get_northbound_hold` | HTTP 东财 |
| 1020 | `block_trade` | `get_block_trade` | HTTP 东财 |
| 1053-1063 | `holders[i].get('change_ratio')` | `get_northbound_hold` | HTTP 东财 |
| 1171-1177 | `anns` | `tdx_get_latest_announcements` | TDX F10 |
| 1247 | `q.get("change_pct")` | `get_change_pct` | ZHB/TDX/HTTP |
| 1261-1278 | `nb/margin` | `get_northbound_hold`/`get_margin_trading` | HTTP/TDX F10 |

### 5.2 get_med_report.py（中线）

类似 sht，主要用 `cdata`/`info`/`q`/`ff`/`blocks` 中间层；HTTP 调用同 sc_datasource。

### 5.3 get_lng_report.py（长线）

| 行号 | 字段访问 | 备注 |
|:---:|:---|:---|
| 200-208 | `info.get('industry')` + `_zhb_data.get("industry_code")` | ⚠️ **P0 Bug**：industry 取值需修正 |
| 335 | `fi.iloc[0].get('zong_guben')` | ⚠️ **P0 Bug**：key 错配 |
| 469 | `fi.iloc[0].get('jing_lirun')` | ⚠️ **P0 Bug**：key 错配 |
| 642 | `_zhb_data.get("industry_code")` | ⚠️ ZHB dict 缺 industry 字段 |

### 5.4 get_mak_report.py（市场全景）

类似 sht；龙虎榜/板块/新闻用 HTTP。

### 5.5 get_val_report.py（估值筛选）

类似 sht；PE/PB 用 ZHB only ✅。

### 5.5 get_val_report.py（估值筛选）

类似 sht；PE/PB 用 ZHB only ✅。

### 5.6 ~~get_ful_report.py~~（V16.1 已下线）

> **V16.1 下线**：全维度报告不再生成（main.py `--ful` 仅提示）。其独有能力已迁移：
> - 技术指标引擎（MACD/RSI/BOLL/KDJ/量能）→ `stock_common/sc_technical.py`（sht/med 复用）
> - 风险扫描引擎（9 项清单）→ `stock_common/sc_risk.py`（med/lng 复用）

---

## 六、 5 大报告脚本公共中间层清单（V16.1：ful 下线后）

> **强制约定**：所有脚本统一通过以下中间层函数获取数据，**不再直接调用 `tdx_client` / `requests` / `_quick_request`**

### 6.1 行情快照（必用）

```python
from data_provider import get_canonical_stock_data  # 返回 CanonicalStockData
cdata = get_canonical_stock_data(code)
# cdata.price, cdata.change_pct, cdata.pe_ttm, cdata.pb, cdata.dividend_yield,
# cdata.industry, cdata.industry_code, cdata.total_shares_wan, cdata.mcap_yi,
# cdata.main_net_buy_wan, cdata.main_net_buy_hands, cdata.change_5d/10d/20d/60d/ytd,
# cdata.high_52w, cdata.low_52w, cdata.streak_days, cdata.ipo_price, cdata.employee_count
```

### 6.2 资金流（必用）

```python
from data_provider import get_main_net_buy, get_change_pct, get_amount_wan
# get_main_net_buy(code) → {"main_net_buy_hands": ..., "main_net_buy_amount": ...}
```

### 6.3 财务（必用）

```python
from data_provider import get_eps_forecast  # 机构预测
# 或直接 TDX 0x0010：
from tdx_client import tdx_get_finance_info
info = tdx_get_finance_info(code)  # 36 字段 dict
# info['jinglirun'] / info['zongguben'] / info['liutongguben'] / info['gudongrenshu']
```

### 6.4 行业/概念（必用）

```python
from stock_common.sc_datasource import get_concept_blocks, get_industry_peers
# get_concept_blocks(code) → {"industry": [...], "concept": [...], "area": [...]}
```

### 6.5 龙虎榜/北向/融资融券（HTTP 独有）

```python
from stock_common.sc_datasource import get_dragon_tiger_board, get_northbound_hold, get_margin_trading
# 这些字段 ZHB 无替代，必须 HTTP
```

### 6.6 财报历史（HTTP 独有）

```python
from stock_common.sc_datasource import get_sina_financial_report, get_sina_balance_sheet
# 12 期历史 / 5 期历史资产负债表，ZHB 仅有最新期
```

---

## 七、 CanonicalStockData 字段映射表（`cdata.*` 完整对照）

| `cdata` 字段 | 类型 | ZHB 来源 | 字典 key | 单位 |
|:---|:---:|:---|:---|:---:|
| `code` | str | — | — | — |
| `name` | str | ZHB | name | — |
| `price` | float | tdxstat/pe_dy/tdx 补 | — | 元 |
| `change_pct` | float | tdxstat Col[6] | change_pct | % |
| `open` | float | TDX/腾讯 | — | 元 |
| `high` | float | TDX/腾讯 | — | 元 |
| `low` | float | TDX/腾讯 | — | 元 |
| `prev_close` | float | TDX | — | 元 |
| `amount_wan` | float | tdxstat2 Col[3] | amount | 万元 |
| `volume_hand` | float | ⚠️ ZHB 不可靠 | — | 手 |
| `pe_ttm` | float | tdxstat Col[9] | pe_ttm | 倍 |
| `pe_dynamic` | float | tdxstat Col[3] | pe_dynamic | 倍 |
| `pb` | float | ZHB | pb | 倍 |
| `dividend_yield` | float | tdxstat Col[10] | dividend_yield | % |
| `turnover_pct` | float | ZHB | turnover_pct | % |
| `main_net_buy_wan` | float | tdxstat2 Col[14] | main_net_buy_amount | 万元 |
| `main_net_buy_hands` | float | tdxstat2 Col[9] | main_net_buy_hands | 手 |
| `main_net_buy_wan_1d` | float | tdxstat2 Col[15] | main_net_buy_amount_1d | 万元 |
| `roe` | float | tdx_get_finance_roe | — | % |
| `gross_margin` | float | sc_datasource 计算 | — | % |
| `net_profit_margin` | float | sc_datasource 计算 | — | % |
| `net_profit` | float | tdxstat/tipinfo | — | 万元 |
| `revenue` | float | ZHB | — | 万元 |
| `eps` | float | tipinfo Col[3] | eps | 元/股 |
| `total_shares_wan` | float | 本地缓存/total_capital | — | 万股 |
| `float_shares_wan` | float | 本地缓存 | — | 万股 |
| `mcap_yi` | float | 动态 = price × total | — | 亿元 |
| `float_mcap_yi` | float | 动态 / ZHB float_mcap | — | 亿元 |
| `holder_count` | int | tdxstat2 计算 | — | 户 |
| `change_5d` | float | tdxstat Col[28] | change_5d | % |
| `change_10d` | float | tdxstat Col[30] | change_10d | % |
| `change_20d` | float | tdxstat Col[17] | change_20d | % |
| `change_60d` | float | tdxstat Col[19] | change_60d | % |
| `change_ytd` | float | tdxstat Col[21] | change_ytd | % |
| `streak_days` | int | tdxstat Col[5] | streak_days | 天 |
| `high_52w` | float | tdxstat2 Col[17] | high_52w | 元 |
| `low_52w` | float | tdxstat2 Col[18] | low_52w | 元 |
| `ipo_price` | float | tdxstat2 Col[16] | ipo_price | 元 |
| `employee_count` | int | tdxstat Col[15] | employee_count | 人 |
| `industry` | str | **TDX boards** ⚠️ | — | — |
| `industry_code` | str | tdxstat2 Col[13] | industry_code | — |
| `board` | str | TDX boards | — | — |
| `concepts` | tuple | TDX boards / ⚠️ | — | — |

---

## 八、 P0 Bug 清单（必须修复）

| Bug | 文件:行 | 错误 | 修正 |
|:---|:---|:---|:---|
| **B-1** | sc_datasource.py:844 | `zong_guben` | `zongguben` |
| **B-2** | sc_datasource.py:845 | `liutong_guben` | `liutongguben` |
| **B-3** | sc_datasource.py:228 | `gudong_renshu` | `gudongrenshu` |
| **B-4** | get_lng_report.py:334 | `jing_lirun` | `jinglirun` |
| **B-5** | get_lng_report.py:335 | `zong_guben` | `zongguben` |
| **B-6** | get_lng_report.py:469 | `jing_lirun` | `jinglirun` |
| **B-7** | zhb_client.py:341-374 | `_parse_tdxchain` 解析格式错误 | 修正 tdxchain 解析 |
| **B-8** | data_provider.py:323-324 | ZHB dict 缺 `industry` | 改用 TDX boards |
| **B-9** | get_lng_report.py:200-208 | 行业归属误用 industry_code | 改用 TDX boards |

---

## 九、 字段路由决策矩阵（最终）

```
任意字段请求
  │
  ├── 是 0x0010 协议字段（zongguben/liutongguben/jingzichan/jinglirun/...）？
  │   └── ✅ → tdx_client.tdx_get_finance_info(code) 直接拿
  │
  ├── 是 ZHB 静态字段（PE/PB/dividend_yield/turnover_pct/change_*d/52w/ipo/employee）？
  │   ├── 盘前/盘后/周末？
  │   │   └── ✅ → data_provider.get_xxx(code)  ZHB only
  │   └── 盘中？
  │       └── ✅ → ZHB T-1 兜底（实时字段除外）
  │
  ├── 是 ZHB 实时字段（price/change_pct/amount/volume）？
  │   ├── 盘前/盘后/周末？
  │   │   └── ✅ → ZHB T-1
  │   └── 盘中？
  │       └── ✅ → ZHB T-1（容差 1 天）→ TDX TCP 实时
  │
  ├── 是 ZHB 准实时字段（main_net_buy_*/streak_days）？
  │   └── ✅ → ZHB T-1（与策略 T-1 对齐）
  │
  ├── 是 ZHB 无替代字段（12期历史财报/5期资产负债表/龙虎榜/北向/融资融券/大宗/同花顺热榜/研报）？
  │   └── ✅ → sc_datasource.get_xxx() HTTP（带 TDX 兜底则优先 TDX）
  │
  ├── 是行业/概念板块？
  │   ├── 行业归属？
  │   │   └── ✅ → tdx_get_belong_boards() TDX（非 HTTP）
  │   └── 概念板块？
  │       └── ✅ → tdx_get_belong_boards() TDX（concepts 字段）
  │
  └── ❌ 不存在 → 报错 / 兜底返回 None
```

---

## 十、 后续维护

- **新增字段**时：先更新 [field_dict.md](file:///d:/GitHub/test/docs/field_dict.md) 字段表，再更新本文件中间层映射
- **新增脚本**时：必须通过 `data_provider` 或 `sc_datasource` 中间层获取数据
- **Bug 修复后**：在本文档第 8 节 P0 Bug 清单中标记为 ✅ 已修复
- **HTTP 性能优化**：定期审查可优先 ZHB/TDX 的字段，更新第 2 节"推荐函数"

---

> 📌 **双字典约定**：
> - **field_dict.md** = 字段元数据（含义、单位、来源）——**测试确认真实有效即录入，无论是否使用**
> - **script_data_dict.md** = 脚本应用接口（中间层函数、调用模式、优先级）
> - 两者一一对应，缺一不可。

---

## V16.1 新接入字段与优先级总表（2026-08-05）

> **原则**：field_dict §12 已录入全部测试确认字段（push2 扩展/levistock/AxData/akshare 校准）。
> 下表标注**脚本当前是否已用**与**扩展优先级**——未用字段为后期脚本升级的现成素材，无需重新寻找。

### V16.1 已接入脚本（数据层+三报告）

| 字段 | 来源 | 脚本状态 | 优先级 |
|:---|:---|:---:|:---:|
| limit_up / limit_down（涨停跌停价）| push2 f51/f52 | sht 用（评分）| ✅ 已用 |
| eps / bps | push2 f55/f92 | Canonical 有值 | ✅ 已用 |
| dividend_yield | push2 f126 | Canonical 有值 | ✅ 已用 |
| pe_dynamic / pe_ttm / pe_more / pb | push2 f162-167 | Canonical 有值 | ✅ 已用 |
| high_52w / low_52w | push2 f174/f175 | Canonical 有值 | ✅ 已用 |
| fund_main_today / 5d / 10d | push2 f137-146 | Canonical 有值（sht/med 待用）| ⭐ 高 |
| report_period / quote_date | push2 f221 / data_date | Canonical 有值 | ✅ 已用 |
| 昨日涨停晋级率 | push2ex getYesterdayZTPool | sht 已用 | ✅ 已用 |
| 研报评级变化 | reportapi ratingChange | med 已用 | ✅ 已用 |
| 两融 RZJME/RQJMG/10D/5D/3D | datacenter | med 已用 | ✅ 已用 |

### 新数据源（field_dict §12.10-12.14 已录，脚本未接入——扩展素材）

| 字段 | 来源 | 接入成本 | 扩展优先级 |
|:---|:---|:---:|:---:|
| 短线指标 34 字段（开盘量比/竞价昨比/封成比/几天几板）| AxData `stock_shortline_indicators_tdx`（**直接消费项目 zhb.zip，已实测**）| 零下载 | ⭐⭐⭐ 最高 |
| 涨跌停 limit_rule 官方枚举（st_5pct/bse_30pct/ipo_first_day）| AxData `stock_daily_price_limit_tdx` | 一次测试 | ⭐⭐⭐ 最高 |
| 盘口异动（火箭发射/大笔买入/封涨停板）| levistock `stock_changes_em`（已实测 2782 条）| 零成本 | ⭐⭐⭐ |
| 市场情绪（热度/封板率/高开率/获利率/连板梯队）| levistock `market_emotion_cls`（已实测）| 零成本 | ⭐⭐ |
| 涨停池补充字段（circ_share/main_inflow/zt_days）| levistock `stock_zt_pool_em`（已实测）| 零成本 | ⭐⭐ |
| i问财自然语言选股 | levistock `stock_strategy_wencai`（免 Key，已实测）| 零成本 | ⭐⭐ |
| 筹码分布（获利比例/90%成本集中度）| AxData `stock_chip_distribution_tdx` | 一次测试 | ⭐⭐ |
| 题材资金走势 / 题材强度排行 | AxData concept_capital_flow / theme_strength_rank | 一次测试 | ⭐ |
| ESG 评分 ×5 | AxData 新浪 ESG | 一次测试 | ⭐ |
| 历史估值序列（校准 val PE 百分位）| akshare 乐咕 stock_a_indicator_lg | 一次测试 | ⭐⭐ |

### AxData 跨源接口实测确认（2026-08-05，39 个可用，field_dict §12.12.8 全字段）

| 数据源 | 实测接口 | 高价值字段（脚本可扩展）|
|:---|:---|:---|
| 东财（8/8）| 快照/涨停池/昨涨停/盘口异动/龙虎榜/两融/板块/所属板块 | **盘口异动 change_type_name（中文"火箭发射"）**、昨涨停 22 字段 |
| 财联社（8/10）| 市场情绪/涨停池/板块热度/风口/轮动/主线/电报 | **涨停池 up_reason（涨停原因）**、板块热度 rank_change |
| 开盘红（4/4）| 情绪/板块排行/历史涨停复盘/涨停天梯 | **历史复盘 seal_money/one_word（大单一字）**、ST 涨停统计 |
| 腾讯（5/6）| 历史日线/指数日线/逐笔/起始年/快照 | **逐笔 trade_side（买卖方向）** |
| 新浪（7/8）| 限售解禁/指数实时/ESG/龙虎榜/指数成份/ETF/港股指数 | **限售解禁 万股/百万元口径**、ESG 评级 |
| 巨潮（4/6）| 公司概况/分红/公告/互动易 | **公告 download_url（PDF 直链）**、分红全字段 |
| 交易所（3/3）| 交易日历/基础信息 27 字段/历史列表 | **股票基础信息 27 字段**（含退市股历史）|



---

## V15.4 PUSH2 字段名映射表（方案 C 关键）

> V15.4 核心修复：**V15 cdata 强类型架构胜利，但 push2 字段名（f43/f44/...）未映射到 cdata 字段名（price/high/...）**——push2 fallback 拿到 dict 但取不出字段，导致 med/lng/ful 三报告总市值/价格/PB 全 0。

### 1. push2 key → cdata field 完整映射（22 项）

`get_em_quote_full()` 返回的 push2 dict 用 `f43`/`f44`/... 命名，
`cdata` 用 `price`/`high`/... 命名——**两套字段名不兼容**。

V9.6 之前没维护这张映射表，cdata 在 push2 fallback 时**拿到 dict 但取不出字段**。

| push2 key | cdata field | 含义 | 单位 |
|:---|:---|:---|:---|
| f43 | price | 当前价 | 元 |
| f44 | high | 最高 | 元 |
| f45 | low | 最低 | 元 |
| f46 | open | 今开 | 元 |
| f60 | last_close | 昨收 | 元 |
| f170 | change_pct | 涨跌幅 | % |
| f168 | turnover_pct | 换手率 | % |
| f171 | amplitude_pct | 振幅 | % |
| f49 | vol_ratio | 量比 | 倍 |
| f6 | amount_wan | 成交额 | 万元 |
| f5 | volume_hand | 成交量 | 手 |
| f162 | pe_ttm | 动态市盈率 | 倍 |
| f167 | pb | 市净率 | 倍 |
| f163 | pe_dynamic | 动态市盈率 | 倍 |
| f84 | total_shares | 总股本 | 股 |
| f85 | float_shares | 流通股本 | 股 |
| f116 | mcap_yi | 总市值 | 亿元 |
| f117 | float_mcap_yi | 流通市值 | 亿元 |
| f57 | code | 股票代码 | — |
| f58 | name | 股票名称 | — |
| **f128** | **industry** | **行业归属** | **文本** |
| f100 | industry_code | 行业代码 | — |

### 2. 关键发现

**f128 industry** 是 push2 自身带的**真实行业归属**（如"光学光电"），
比 TDX boards（"光学光电子"，带"子"）和 ZHB（"光学光电"）都更准。
V15 没用上 f128，是 cdata 行业字段为"光学光电子"的根因。
**V15.4 修复**：industry 4 级 fallback 链首项就是 push2 f128。

### 3. PUSH2_FIELD_MAP 实现位置

V15.4 [data_provider.py:264-279](file:///d:/GitHub/test/data_provider.py#L264) 集中维护 PUSH2_FIELD_MAP 字典。

新增/修改字段时**只改这张表**——上层调用 `get_canonical_stock_data(code)` 拿到的 cdata 字段名始终是 cdata 风格的（price/high/mcap_yi/pb/industry），无需关心 push2 key。
