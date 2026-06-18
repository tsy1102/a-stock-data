# A股全栈数据工具包 (a-stock-data) V3.0 — Code Wiki

> 项目主页：[https://github.com/simonlin1212/a-stock-data](https://github.com/simonlin1212/a-stock-data)
> 作者：Simon 林 · 抖音「Simon林」· 公众号「硅基世纪」

---

## 目录

1. [项目概述](#1-项目概述)
2. [项目架构总览](#2-项目架构总览)
3. [七层数据架构详解](#3-七层数据架构详解)
   - [Layer 1：行情层](#31-layer-1-行情层)
   - [Layer 2：研报层](#32-layer-2-研报层)
   - [Layer 3：信号层](#33-layer-3-信号层)
   - [Layer 4：资金面/筹码层](#34-layer-4-资金面筹码层)
   - [Layer 5：新闻层](#35-layer-5-新闻层)
   - [Layer 6：基础数据层](#36-layer-6-基础数据层)
   - [Layer 7：公告层](#37-layer-7-公告层)
4. [关键工具函数](#4-关键工具函数)
5. [估值计算框架](#5-估值计算框架)
6. [内置调研流程](#6-内置调研流程)
7. [依赖关系](#7-依赖关系)
8. [项目运行方式](#8-项目运行方式)
9. [版本历史](#9-版本历史)
10. [数据源与鉴权汇总](#10-数据源与鉴权汇总)
11. [常见问题](#11-常见问题)

---

## 1. 项目概述

**a-stock-data** 是一个自包含的 A 股全栈数据工具包，以单个 `SKILL.md` 文件形式发布，专为 AI 编程助手（Claude Code、Codex、OpenClaw）设计。

### 核心价值

- **零第三方数据封装依赖**：V3.0 彻底移除 akshare，所有数据源直连 HTTP API（仅 mootdx 保留 TCP 协议）
- **28 个数据端点**：覆盖行情、研报、信号、资金面、新闻、基础数据、公告七层
- **13 个数据源**：mootdx、腾讯财经、百度股市通、东财(datacenter/push2/reportapi/search-api/np-weblist)、同花顺(热点/hsgtApi/basic)、iwencai、新浪财经、财联社、巨潮 cninfo
- **免费为主**：仅 iwencai 需要 API Key，其余 12 个数据源完全免费
- **内嵌全部调用代码**：每个端点的 Python 调用代码直接写在 SKILL.md 中，无需查阅外部文档

### 工作方式

SKILL.md 本质是结构化 Markdown + 内嵌 Python 代码。放在 `~/.claude/skills/a-stock-data/SKILL.md` 后，Claude Code 会在 A 股相关对话中自动激活。用户通过自然语言描述需求，AI 助手读取 SKILL.md 中的代码端点直接执行。

---

## 2. 项目架构总览

```text
A股全栈数据 · 七层架构 (V3.0)
│
├── Layer 1: 行情层
│   ├── mootdx (TCP 7709)      → K线 + 五档盘口 + 逐笔成交
│   ├── 腾讯财经 (HTTP GBK)     → PE/PB/市值/换手率/涨跌停/指数/ETF
│   └── 百度股市通 (HTTP)       → K线带MA5/10/20 (V3.0新增)
│
├── Layer 2: 研报层
│   ├── 东财 reportapi (HTTP)  → 研报列表 + PDF下载 + 评级 + 三年EPS
│   ├── 同花顺 basic (HTTP)    → 机构一致预期EPS
│   └── iwencai OpenAPI (需Key) → NL语义搜索研报 (唯一能力)
│
├── Layer 3: 信号层
│   ├── 同花顺热点 (HTTP)      → 当日强势股 + 题材归因 reason tags
│   ├── 同花顺北向 (HTTP)      → hgt/sgt 分钟资金流向 + 自缓存历史
│   ├── 百度股市通概念 (HTTP)   → 概念板块归属 (行业/概念/地域)
│   ├── 百度股市通资金流 (HTTP) → 个股资金流向 (分钟级 + 20日历史)
│   ├── 龙虎榜席位 (东财DC)    → 上榜记录 + 买卖席位TOP5 + 机构动向
│   ├── 全市场龙虎榜 (东财DC)  → 每日全市场龙虎榜汇总
│   ├── 限售解禁日历 (东财DC)  → 历史解禁 + 未来90天待解禁
│   └── 行业板块排名 (东财push2) → 全行业涨跌幅排名
│
├── Layer 4: 资金面/筹码层 (V3.0新增)
│   ├── 融资融券明细 (东财DC)  → 日级融资余额/买入/偿还
│   ├── 大宗交易 (东财DC)      → 成交价/量 + 买卖方营业部
│   ├── 股东户数变化 (东财DC)  → 季度股东户数 + 环比变化
│   ├── 分红送转历史 (东财DC)  → 每股派息/送股/转增
│   └── 个股资金流120日 (东财push2his) → 主力/大单/中单/小单历史
│
├── Layer 5: 新闻层
│   ├── 东财个股新闻 (HTTP)    → 个股相关新闻 (JSONP)
│   ├── 财联社快讯 (HTTP)      → 全市场实时电报
│   └── 东财全球资讯 (HTTP)    → 7×24 财经快讯
│
├── Layer 6: 基础数据层
│   ├── mootdx finance (TCP)   → 37字段季报快照 (EPS/ROE/净利)
│   ├── mootdx F10 (TCP)       → 9大类公司文本资料
│   ├── 东财个股信息 (HTTP)    → 行业/股本/市值/上市日期
│   └── 新浪财报三表 (HTTP)    → 资产负债表/利润表/现金流量表
│
└── Layer 7: 公告层
    ├── 巨潮 cninfo (HTTP)     → 公告全文检索+下载
    └── mootdx F10 (TCP)       → 最新公告摘要
```

---

## 3. 七层数据架构详解

### 3.1 Layer 1: 行情层

提供实时市场数据，三个互补的数据源，均不封 IP。

#### 3.1.1 mootdx — K线 + 五档盘口 + 逐笔成交

| 属性 | 说明 |
|------|------|
| **协议** | TCP 二进制 (通达信服务器 7709 端口) |
| **鉴权** | 无，无需注册 |
| **Python 依赖** | `mootdx >= 0.10` |
| **市场代码** | 0=深圳, 1=上海 |

**关键功能：**

**`Quotes.bars(symbol, category, offset)`** — 获取 K 线数据

| 参数 | 说明 |
|------|------|
| `symbol` | 6 位股票代码 |
| `category` | 4=日线, 5=周线, 6=月线, 7=1分钟, 8=5分钟, 9=15分钟, 10=30分钟, 11=60分钟 |
| `offset` | 返回的 K 线根数 |

返回字段：`open, close, high, low, vol, amount, datetime`

**`Quotes.quotes(symbol=[...])`** — 实时报价（46 个字段）

返回字段：`price, open, high, low, last_close, bid1~bid5, ask1~ask5, bid_vol1~bid_vol5, ask_vol1~ask_vol5, vol, amount, servertime`

**`Quotes.transaction(symbol, date)`** — 逐笔成交（非交易时间返回空）

返回字段：`time, price, vol, num, buyorsell(0买/1卖/2中性)`

> 注意：mootdx 不提供 PE/PB/市值/换手率/涨跌停价，这些需要走腾讯财经 API。

#### 3.1.2 腾讯财经 API — PE/PB/市值/换手率/涨跌停/指数/ETF

| 属性 | 说明 |
|------|------|
| **协议** | HTTP GET |
| **编码** | GBK |
| **分隔符** | `~` 分隔 88 个字段 |
| **支持范围** | 个股、指数(`sh000001`/`sh000300`/`sz399006`)、ETF(`sh510050`/`sh510300`) |

**关键函数：**

**`tencent_quote(codes)`** — 批量拉取腾讯财经实时行情

| 参数 | 类型 | 说明 |
|------|------|------|
| `codes` | `list[str]` | 6 位代码列表，自动加市场前缀 |

返回字段关键索引（实测校准）：

| 索引 | 含义 | 说明 |
|------|------|------|
| 1 | 名称 | 股票简称 |
| 3 | 当前价 | 实时价格 |
| 4 | 昨收 | 昨日收盘价 |
| 31 | 涨跌额 | 元 |
| 32 | 涨跌幅% | 百分比 |
| 33 | 最高 | 日内最高价 |
| 34 | 最低 | 日内最低价 |
| 37 | 成交额(万) | 万元 |
| 38 | 换手率% | 换手率 |
| **39** | **PE(TTM)** | 滚动市盈率 |
| 43 | 振幅% | 非PB |
| **44** | **总市值(亿)** | 总市值 |
| **45** | **流通市值(亿)** | 流通市值 |
| **46** | **PB(市净率)** | 市净率 |
| **47** | **涨停价** | 当日涨停价 |
| **48** | **跌停价** | 当日跌停价 |
| 49 | 量比 | 量比 |
| **52** | **PE(静)** | 静态市盈率 |

> **踩坑提醒：** 网上很多教程把索引 43 写成 PB，实测是振幅%。PB 在索引 46。

#### 3.1.3 百度股市通 K线 — 带MA5/MA10/MA20 (V3.0 新增)

**核心价值：** 返回时自带均线数据，无需本地计算。

**关键函数：**

**`baidu_kline_with_ma(code, start_time)`** — 获取带均线的 K 线数据

| 参数 | 类型 | 说明 |
|------|------|------|
| `code` | `str` | 6 位股票代码 |
| `start_time` | `str` | 起始时间，默认空 |

返回数据中 `keys` 包含：`time, open, close, high, low, volume, amount, ma5avgprice, ma10avgprice, ma20avgprice` 等字段。

---

### 3.2 Layer 2: 研报层

提供机构研报数据，三个数据源互补使用。

#### 3.2.1 东财研报 API — 研报列表 + PDF下载

| 属性 | 说明 |
|------|------|
| **接口** | `reportapi.eastmoney.com/report/list` (A 级公开 JSON API) |
| **鉴权** | 免费无 key |
| **PDF 模板** | `https://pdf.dfcfw.com/pdf/H3_{infoCode}_1.pdf` |

**关键函数：**

**`eastmoney_reports(code, max_pages=5)`** — 拉取指定股票的研报列表

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `code` | `str` | — | 6 位股票代码 |
| `max_pages` | `int` | 5 | 最大翻页数 |

返回每条记录的关键字段：

| 字段 | 含义 |
|------|------|
| `title` | 研报标题 |
| `publishDate` | 发布日期 |
| `orgSName` | 机构简称 |
| `infoCode` | 用于拼接 PDF URL |
| `predictThisYearEps` | 今年 EPS 预测 |
| `predictNextYearEps` | 明年 EPS 预测 |
| `predictNextTwoYearEps` | 后年 EPS 预测 |
| `emRatingName` | 评级（买入/增持等） |
| `indvInduName` | 行业分类 |

**`download_pdf(record, target_dir)`** — 下载研报 PDF

| 参数 | 类型 | 说明 |
|------|------|------|
| `record` | `dict` | 研报记录（需含 infoCode） |
| `target_dir` | `str` | 保存目录，默认 `./reports` |

#### 3.2.2 同花顺一致预期EPS

**关键函数：**

**`ths_eps_forecast(code)`** — 获取机构一致预期 EPS

| 参数 | 说明 |
|------|------|
| `code` | 6 位股票代码 |

返回 DataFrame，列含：年度, 预测机构数, 最小值, 均值, 最大值。**"均值" = 机构一致预期EPS**。

> 当"预测机构数" < 3 时，一致预期参考价值有限。

#### 3.2.3 iwencai NL 语义搜索

**唯一能力：** 自然语言跨主题研报检索（如"人形机器人 行星滚柱丝杠"），其他接口无法替代。

| 属性 | 说明 |
|------|------|
| **协议** | OpenAPI |
| **鉴权** | 需要 API Key + X-Claw Headers (SkillHub 2.0) |
| **环境变量** | `IWENCAI_API_KEY`, `IWENCAI_BASE_URL` |

**关键函数：**

**`iwencai_search(query, channel, size)`** — 语义搜索

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `query` | `str` | — | 搜索关键词 |
| `channel` | `str` | `"report"` | 频道：report/announcement/news |
| `size` | `int` | 50 | 返回条数（隐藏参数，默认 10） |

**`iwencai_query(query, page, limit)`** — NL 数据查询（结构化字段）

**`dedup_articles(articles)`** — 同一 uid 仅保留 score 最高的段落

---

### 3.3 Layer 3: 信号层

提供市场信号数据，是 V3.0 中功能最丰富的层级。

#### 3.3.1 同花顺热点 — 当日强势股 + 题材归因

**核心价值：** 不仅提供"哪些走强"，还提供**"为什么走强"**——同花顺编辑部人工运营的题材标签。

**关键函数：**

**`ths_hot_reason(date)`** — 获取当日强势股归因

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `date` | `str` | `None`(今天) | 格式 `YYYY-MM-DD` |

返回 DataFrame 字段：

| 原字段 | 中文 | 说明 |
|--------|------|------|
| `code` | 代码 | 6 位股票代码 |
| `name` | 名称 | 简称 |
| **`reason`** | **题材归因** | **核心字段，人工运营 tags，如"算力租赁+Token工厂+AI政务"** |
| `zhangfu` | 涨幅% | 当日涨幅 |
| `huanshou` | 换手率% | 当日换手 |
| `chengjiaoe` | 成交额 | 元 |
| `ddejingliang` | 大单净量 | 主力净流入指标 |
| `close` | 收盘价 | 元 |

> 实测：73ms 拿到 ~125 只 + 完整字段。盘后数据 15:30 之后更新。

#### 3.3.2 同花顺北向资金 — 实时分钟流向 + 自缓存历史

| 属性 | 说明 |
|------|------|
| **接口** | `data.hexin.cn/market/hsgtApi/method/dayChart/` |
| **鉴权** | 零鉴权（仅需 User-Agent + Referer） |

**关键函数：**

**`hsgt_realtime()`** — 沪深股通当日实时分钟流向（含集合竞价 09:10–15:00，262 个时间点）

返回字段：`time, hgt(yi), sgt(yi)`，单位：亿元

**辅助函数（自缓存机制）：**

| 函数 | 说明 |
|------|------|
| `_northbound_cache_path()` | 获取本地 CSV 缓存路径：`~/.tradingagents/cache/northbound_daily.csv` |
| `_save_northbound_snapshot(date, hgt, sgt)` | 写入/更新当天北向收盘数据到 CSV |
| `_load_northbound_history(n)` | 读取最近 N 天北向历史 |

> **注意：** eastmoney 全系北向数据自 2024-08 后净买额字段返回 NaN/0，已改为本地 CSV 自缓存模式。

#### 3.3.3 百度股市通 — 概念板块归属

**核心价值：** 一次调用拿到个股所属的行业（申万一级/二级）、概念（多个）、地域三维分类，含当日涨跌幅。

**关键函数：**

**`baidu_concept_blocks(code)`** — 获取个股概念板块归属

返回结构：
```python
{
    "industry": [{"name", "change_pct", "desc"}, ...],
    "concept": [{"name", "change_pct", "desc"}, ...],
    "region": [{"name", "change_pct", "desc"}, ...],
    "concept_tags": ["AI芯片", "半导体", ...]
}
```

> **踩坑：** `ResultCode` 返回类型不稳定——有时 int `0`，有时 string `"0"`。必须用 `str()` 统一比较。

#### 3.3.4 百度股市通 — 个股资金流向（分钟级）

**关键函数：**

**`baidu_fund_flow_realtime(code, date)`** — 分钟级实时资金流向

| 参数 | 格式 | 说明 |
|------|------|------|
| `code` | `000858` | 6 位代码 |
| `date` | `YYYYMMDD` | 紧凑格式（注意不是 `YYYY-MM-DD`） |

返回字段：`time, mainForce(主力), retail(散户), super(超大单), large(大单), price`

**`baidu_fund_flow_history(code, days=20)`** — 日级历史资金流向

返回字段：`date, close, change_pct, superNetIn, largeNetIn, mediumNetIn, littleNetIn, mainIn`

> **踩坑：** 实时数据格式是分号分隔的字符串（非 JSON 数组），`date` 参数用紧凑格式 `20260517`。

#### 3.3.5 龙虎榜席位 — 个股上榜记录 + 买卖席位 TOP5 + 机构动向

**关键函数：**

**`dragon_tiger_board(code, trade_date, look_back=30)`** — 龙虎榜数据聚合

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `code` | `str` | — | 6 位代码 |
| `trade_date` | `str` | — | 格式 `YYYY-MM-DD` |
| `look_back` | `int` | 30 | 回看天数 |

返回结构：
```python
{
    "records": [{"date", "reason", "net_buy", "turnover"}, ...],
    "seats": {
        "buy": [{"name", "buy_amt", "sell_amt", "net"}, ...],
        "sell": [{"name", "buy_amt", "sell_amt", "net"}, ...]
    },
    "institution": {"buy_count", "sell_count", "net_amount"}
}
```

> **ST 股注意：** 5% 涨跌停更容易触发龙虎榜，科创板 20% 涨跌停较少触发。

#### 3.3.6 限售解禁日历

**关键函数：**

**`lockup_expiry(code, trade_date, forward_days=90)`** — 解禁日历

返回：
```python
{
    "history": [{"date", "type", "shares", "ratio"}, ...],
    "upcoming": [{"date", "type", "shares", "ratio"}, ...]
}
```

**限售股类型参考：**
- 首发原股东限售股份（IPO 后 1-3 年）
- 首发机构配售股份（IPO 战略配售）
- 定向增发机构配售股份（6-18 个月）
- 股权激励限售股份

#### 3.3.7 行业板块排名 — 全行业涨跌幅排名

**关键函数：**

**`industry_comparison(top_n=20)`** — 全行业涨跌幅排名

东财行业板块数据（~100 个行业），通过 `push2.eastmoney.com` 接口获取。

返回：
```python
{
    "top": [{"rank", "name", "change_pct", "code", "up_count", "down_count", "leader", "leader_change"}, ...],
    "bottom": [...],
    "total": 100
}
```

#### 3.3.8 全市场龙虎榜

**关键函数：**

**`daily_dragon_tiger(trade_date, min_net_buy)`** — 全市场龙虎榜汇总

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `trade_date` | `str` | `None`(当日) | `YYYY-MM-DD` |
| `min_net_buy` | `float` | `None` | 净买入下限(万元)，不过滤 |

返回：
```python
{
    "date": "2026-05-16",
    "total_records": 50,
    "stocks": [{"code", "name", "reason", "close", "change_pct", "net_buy_wan", ...}]
}
```

---

### 3.4 Layer 4: 资金面/筹码层 (V3.0 新增)

V3.0 新增的完整层级，5 个端点全部基于东财数据中心 API。

#### 3.4.1 融资融券明细

**`margin_trading(code, page_size=30)`** — 日级融资融券数据

返回字段：`date, rzye(融资余额), rzmre(融资买入), rzche(融资偿还), rqye(融券余额), rqmcl(融券卖出), rqchl(融券偿还), rzrqye(两融合计)`

#### 3.4.2 大宗交易

**`block_trade(code, page_size=20)`** — 大宗交易记录

返回字段：`date, price, close, premium_pct(溢价率), vol, amount, buyer, seller`

#### 3.4.3 股东户数变化

**`holder_num_change(code, page_size=10)`** — 季度股东户数

返回字段：`date, holder_num, change_num, change_ratio(环比%), avg_shares(户均持股)`

> 股东户数持续减少 = 筹码集中 = 主力吸筹信号

#### 3.4.4 分红送转历史

**`dividend_history(code, page_size=20)`** — 分红送转历史

返回字段：`date, bonus_rmb(每股派息税前), transfer_ratio(每10股转增), bonus_ratio(每10股送股), plan`

#### 3.4.5 个股资金流120日

**`stock_fund_flow_120d(code)`** — 日级个股资金流（最近 120 个交易日）

通过 `push2his.eastmoney.com` 接口获取。

返回字段：`date, main_net(主力净流入), small_net, mid_net, large_net, super_net`，单位：元

---

### 3.5 Layer 5: 新闻层

#### 3.5.1 东财个股新闻

**`eastmoney_stock_news(code, page_size=20)`** — 个股相关新闻

通过 `search-api-web.eastmoney.com` JSONP 接口获取。

返回字段：`title, content(前200字), time, source, url`

#### 3.5.2 财联社快讯

**`cls_telegraph(page_size=50)`** — 全市场实时电报

通过 `cls.cn/nodeapi/telegraphList` 接口获取。

返回字段：`title, content, time`

#### 3.5.3 东财全球资讯

**`eastmoney_global_news(page_size=50)`** — 全球财经资讯（7×24 滚动）

通过 `np-weblist.eastmoney.com` 接口获取。

返回字段：`title, summary, time`

---

### 3.6 Layer 6: 基础数据层

#### 3.6.1 mootdx 财务快照

通过 `Quotes.factory(market='std').finance(symbol=code)` 获取 37 个季报财务字段：

`liutongguben, zongguben, eps, bvps, roe, profit, income, meigujingzichan, meigugongjijin, meiguweifeipeili` 等。

#### 3.6.2 mootdx F10

通过 `Quotes.factory(market='std').F10(symbol=code, name=category)` 获取 9 大类文本数据：

| 类别 | 说明 |
|------|------|
| 最新提示 | 最新公告/分红/股东大会等摘要 |
| 公司概况 | 公司基本信息 |
| 财务分析 | 财务数据 |
| 股东研究 | 十大股东等 |
| 股本结构 | 股本构成 |
| 资本运作 | 资本运作记录 |
| 业内点评 | 行业评价 |
| 行业分析 | 行业分析 |
| 公司大事 | 重大事项 |

> **优化提示：** "股东研究"中的【4.股东变化】含大量历史数据（实测 16000+ chars），建议只保留最新一期。

#### 3.6.3 东财个股基本面

**`eastmoney_stock_info(code)`** — 通过 push2 API 获取个股基本面

返回字段：`code, name, industry, total_shares, float_shares, mcap, float_mcap, list_date, price`

#### 3.6.4 新浪财报三表

**`sina_financial_report(code, report_type)`** — 三大财务报表

| 参数 | 值 | 说明 |
|------|-----|------|
| `report_type` | `"fzb"` | 资产负债表 |
| | `"lrb"` | 利润表 |
| | `"llb"` | 现金流量表 |

返回最近 20 期的财务数据列表。

---

### 3.7 Layer 7: 公告层

#### 3.7.1 巨潮公告

**`cninfo_announcements(code, page_size=30)`** — 沪深北全量公告检索

通过 `cninfo.com.cn/new/hisAnnouncement/query` POST 接口获取。

返回字段：`title, type, date, url`

#### 3.7.2 mootdx F10 公告摘要

通过 `client.F10(symbol=code, name='最新提示')` 获取最近公告摘要。

---

## 4. 关键工具函数

### 4.1 市场前缀规则

**`get_prefix(code)`** — 6 位代码转市场前缀

| 代码前缀 | 市场 | 前缀 |
|----------|------|------|
| 6, 9 | 上海 | `sh` |
| 8 | 北京 | `bj` |
| 其他 | 深圳 | `sz` |

### 4.2 东财数据中心统一查询

**`eastmoney_datacenter(report_name, columns, filter_str, page_size, sort_columns, sort_types)`** — 东财数据中心统一查询

龙虎榜、解禁、融资融券、大宗交易、股东户数、分红共用的底层 helper。

| 参数 | 默认 | 说明 |
|------|------|------|
| `report_name` | — | 报表名称（如 `RPT_DAILYBILLBOARD_DETAILSNEW`） |
| `columns` | `"ALL"` | 查询列 |
| `filter_str` | `""` | 过滤条件 |
| `page_size` | 50 | 每页条数 |
| `sort_columns` | `""` | 排序列 |
| `sort_types` | `"-1"` | 排序方向 |

请求地址：`https://datacenter-web.eastmoney.com/api/data/v1/get`

### 4.3 Ticker 格式归一化

所有接口统一支持多种输入格式，内部归一化为纯 6 位数字：

| 输入 | 归一化结果 |
|------|-----------|
| `688017` | `688017` |
| `SH688017` / `sh688017` | `688017` |
| `688017.SH` | `688017` |
| `SZ000001` | `000001` |
| `BJ832000` | `832000` |

### 4.4 iwencai X-Claw 鉴权

**`_claw_headers(call_type)`** — 生成 SkillHub 2.0 强制要求的 X-Claw Headers

| Header | 值 |
|--------|-----|
| `X-Claw-Call-Type` | `normal` |
| `X-Claw-Skill-Id` | `report-search` |
| `X-Claw-Skill-Version` | `2.0.0` |
| `X-Claw-Plugin-Id` | `none` |
| `X-Claw-Plugin-Version` | `none` |
| `X-Claw-Trace-Id` | 随机 32 字节 hex |

---

## 5. 估值计算框架

### 5.1 前向 PE

```python
forward_pe(price, eps_forecast) → price / eps_forecast
```

当前股价 / 未来年度一致预期 EPS

### 5.2 PE 消化时间

```python
pe_digestion(current_pe, cagr, target_pe=30)
```

当前 PE 消化到目标 PE（A 股成长股合理估值锚点 30x）需要多少年。

### 5.3 PEG

```python
calc_peg(pe, cagr) → pe / (cagr * 100)
```

| PEG 范围 | 评估 |
|----------|------|
| < 1 | 便宜 |
| 1-1.5 | 合理 |
| \> 1.5 | 贵 |

### 5.4 投资框架

```text
壁垒 → 增速 → PE消化 → PEG校验
1. 有壁垒吗？(tech_moat / capacity_moat) → 没有则排除
2. 增速多少？(CAGR > 30% 才有意义)
3. PE多久消化到30x？(< 2年合理, > 4年太贵)
4. PEG多少？(< 1 便宜, 1-1.5 合理, > 1.5 贵)
```

---

## 6. 内置调研流程

### 流程 A: 单票完整估值（30 秒）

**`full_valuation(code)`** — 单票完整估值分析

串联步骤：
1. 腾讯实时行情 → 价格/PE/PB/市值
2. 同花顺一致预期 → EPS 预测
3. 计算前向 PE / CAGR / PEG / PE 消化年数

### 流程 B: 批量估值对比

对多只股票循环调用 `full_valuation()`，横向输出 PE_fwd / PEG / 消化年数 / 机构覆盖数。

### 流程 C: 主题研报批量检索

1. iwencai 多 query 语义搜索 + 去重
2. 东财补充同标的研报 + PDF 下载

### 流程 D: 新标的快速调研（V3.0 增强版）

10 步快速调研流程：
1. 机构覆盖检查（同花顺一致预期）
2. 实时估值（腾讯财经）
3. PE 消化计算
4. PEG 校验
5. 概念板块归属（百度股市通）
6. 分钟级资金流向（百度）
7. 120 日资金流（东财 push2his）
8. 龙虎榜记录
9. 解禁预警
10. 融资融券 + 股东户数

---

## 7. 依赖关系

### Python 依赖

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| `mootdx` | >= 0.10 | TCP 行情 + 财务 + F10（唯一非 HTTP 依赖） |
| `requests` | any | 所有 HTTP API 直连 |
| `pandas` | any | 数据处理 + HTML 表格解析 |
| `stockstats` | any | 技术指标计算（RSI/MACD/BOLL 等） |

### 安装命令

```bash
pip install mootdx requests pandas stockstats
```

### 可选配置

```bash
# iwencai API Key（仅语义搜索需要）
export IWENCAI_API_KEY="your_key_here"
export IWENCAI_BASE_URL="https://openapi.iwencai.com"
```

### 外部数据源列表

| # | 数据源 | 协议 | 是否需要 Key | 封 IP 风险 |
|---|--------|------|-------------|-----------|
| 1 | mootdx | TCP 7709 | 否 | 极低 |
| 2 | 腾讯财经 | HTTP GBK | 否 | 低 |
| 3 | 东财 datacenter | HTTP | 否 | 低 |
| 4 | 东财 push2/push2his | HTTP | 否 | 低 |
| 5 | 东财 reportapi/PDF | HTTP | 否 | 低 |
| 6 | 东财 search-api-web | HTTP JSONP | 否 | 低 |
| 7 | 东财 np-weblist | HTTP | 否 | 低 |
| 8 | 同花顺热点 | HTTP | 否 | 极低 |
| 9 | 同花顺 hsgtApi | HTTP | 否 | 极低 |
| 10 | 同花顺 basic | HTTP | 否 | 低 |
| 11 | 百度股市通 (PAE) | HTTP | 否 | 极低 |
| 12 | 新浪财经 | HTTP | 否 | 低 |
| 13 | 财联社 | HTTP | 否 | 低 |
| 14 | 巨潮 cninfo | HTTP | 否 | 低 |
| 15 | iwencai | OpenAPI | **是** | 低 |

---

## 8. 项目运行方式

### 作为 Claude Code Skill 使用

```bash
# 1. 创建 skill 目录
mkdir -p ~/.claude/skills/a-stock-data

# 2. 将 SKILL.md 复制到目录
cp SKILL.md ~/.claude/skills/a-stock-data/SKILL.md

# 3. 安装依赖
pip install mootdx requests pandas stockstats

# 4. (可选) 配置 iwencai API Key
export IWENCAI_API_KEY="your_key_here"

# 5. 启动 Claude Code，说"查一下688017的估值"
```

激活后，Claude Code 会自动识别并在 A 股相关对话中激活技能。

### 独立 Python 脚本使用

SKILL.md 中的每个 Python 代码段都可以独立复制出来运行。直接执行代码需要先安装依赖：

```python
# 复制单段代码独立使用
from your_script import tencent_quote
result = tencent_quote(["688017"])
print(result)
```

### 兼容平台

- Claude Code
- Codex
- OpenClaw
- 任何支持上下文注入的 AI 编程助手

### 注意事项

1. **国内 IP 要求**：mootdx 走 TCP 直连通达信服务器，海外环境不稳定，建议走代理
2. **GBK 编码**：腾讯财经 API 返回 GBK 编码，必须 `decode("gbk")`
3. **Referer Header**：东财 PDF 下载必须带 `Referer: https://data.eastmoney.com/`
4. **X-Claw Headers**：iwencai 接口必须携带 X-Claw 鉴权头
5. **响应速度**：大部分 HTTP 接口返回时间在 73ms-3s 之间

---

## 9. 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|---------|
| **V3.0** | 2026-05-17 | **Breaking Change**: 彻底移除 akshare 依赖，所有数据源直连 HTTP API；新增资金面/筹码层（5 个端点）；新增百度 K 线(带 MA)；架构从六层升级为七层，端点从 20 个增至 28 个，数据源从 8 个增至 13 个 |
| **V2.1** | 2026-05-12 | 新增龙虎榜席位、全市场龙虎榜、限售解禁、行业对比、概念板块、资金流向 6 个端点；北向资金改为本地自缓存；F10 股东研究截断(-70% token) |
| **V2.0** | 2026-05-11 | 首次开源发布；新增信号层（同花顺热点 + 北向资金）；架构从五层升级为六层 |
| **V1.0** | 2026-04 | 内部版本（未开源）；五层架构 · 13 端点 |

---

## 10. 数据源与鉴权汇总

### 免费无 Key（13 个数据源）

| 数据源 | 接口类型 | 主要用途 | 鉴权方式 |
|--------|---------|---------|---------|
| mootdx | TCP 二进制 | K线、盘口、财务、F10 | 无 |
| 腾讯财经 | HTTP | 实时行情、PE/PB/市值 | 无 |
| 东财 datacenter | HTTP | 龙虎榜、解禁、两融、大宗、股东、分红 | 无 |
| 东财 push2 | HTTP | 行业板块、个股信息 | 无 |
| 东财 push2his | HTTP | 120日资金流 K线 | 无 |
| 东财 reportapi | HTTP | 研报列表 | 无 |
| 东财 PDF | HTTP | 研报下载 | Referer |
| 同花顺热点 | HTTP | 强势股、题材归因 | 无 |
| 同花顺 hsgtApi | HTTP | 北向资金 | 无 |
| 同花顺 basic | HTTP | 一致预期 | User-Agent |
| 百度 PAE | HTTP | 概念板块、资金流向、K线带MA | User-Agent |
| 新浪财经 | HTTP | 三大报表 | User-Agent |
| 财联社 | HTTP | 电报快讯 | 无 |
| 巨潮 cninfo | HTTP | 公告全文 | 无 |

### 需要 Key（1 个）

| 数据源 | 接口类型 | 用途 | 申请地址 |
|--------|---------|------|---------|
| iwencai | OpenAPI | NL语义搜索 | https://www.iwencai.com/skillhub |

---

## 11. 常见问题

### Q: mootdx 和腾讯有什么区别？
互补关系。mootdx = 交易层（价格+盘口+K线），腾讯 = 估值层（PE/PB/市值/换手率/涨跌停价）。两者都不封 IP。

### Q: V3.0 为什么移除 akshare？
akshare 本质是对东财/同花顺/新浪等公开 API 的封装，中间层增加了故障点（版本兼容 bug、pandas 3.0 ArrowInvalid 等）。V3.0 直连底层 HTTP API，零中间依赖，更稳定可控。

### Q: 腾讯 API 字段 43 是 PB 吗？
**不是！** 43=振幅%，46=PB。网上大量教程写错了，这里是实测校准结果。

### Q: 哪些数据源需要 API Key？
只有 iwencai 需要。mootdx / 腾讯 / 东财 / 同花顺 / 百度股市通 / 新浪 / 巨潮 / 财联社全部免费无 key。

### Q: 北向资金历史数据为什么只有最近几天？
本地自缓存模式。eastmoney 全系北向数据自 2024-08 起断供（净买额字段返回 NaN/0）。每次调用实时 API 后自动写入本地 CSV，历史越跑越丰富。

### Q: 行业板块为什么从同花顺换成东财？
同花顺 `stock_board_industry_summary_ths` 接口 2026 年初加了反爬 401（需要登录态）。东财 push2 行业板块数据（`m:90+t:2`）是完美替代，零鉴权且字段更丰富。

### Q: 在海外服务器跑，mootdx 接口超时？
mootdx 走 TCP 直连通达信行情服务器，需国内 IP 才稳定。海外环境建议走代理。腾讯财经和百度股市通不受影响。

### Q: 同花顺热点接口需要 cookie 吗？
**不需要。** 仅 User-Agent 即可，零鉴权 73ms 拿到 ~125 只当日强势股。
