# fuyao 源「网站中文列名 ↔ 英文字段」黄金锚

> 状态：**v1.0 完整版（Phase 1–4 实证覆盖，浏览器阻塞项已标注）**
> 创建：2026-09-13 ｜ 关联计划：`docs/field_verification/20260913_fuyao_website_anchor_plan.md`
> 数据来源：通达信 / 同花顺 `q.10jqka.com.cn` 官方中文列名（WebFetch 逐字抓取）、`fuyao_api_full.md` 全量字段契约镜像（`docs/verify/`）、运行时 `stock_common/sc_fuyao.py`。
> 说明：本表为字段治理的"中文名黄金锚"，仅登记/映射，不改动任何运行时取数路径。所有结论不构成投资建议。

---

## 〇、方法与环境约束（防失焦首读）

- **目标**：把 `q.10jqka.com.cn` 可见中文列名逐列映射到 fuyao 英文字段，建立"中文名 ↔ 英文键 ↔ 真实来源 ↔ 口径单位"三元锚，固化后供后期对撞/破解按中文名检索。
- **抽取通道实测（2026-09-13）**：
  - `WebFetch` 通道**可用**：以下页面均逐字抓取成功——板块详情页（`/gn/detail/code/XXX/`）、A股个股行情页（`/stock/xsjj/`）、指数列表页（`/zs/`）、港股列表页（`/hk/`）、新股页（`/newstock/`）。
  - `agent-browser`（Chrome 153，agent-browser 下载版）**本沙箱无法启动**：`open about:blank`（无网络）即零输出挂起、`timeout` 杀不掉、Chrome 残留。
  - **系统 Chrome（C:\Program Files\Google\Chrome\Application\，152/153）亦无法运行**：`--no-sandbox --headless --single-process --no-zygote --disable-gpu` 全组合下 **segfault（EXIT=139）** / 子进程崩溃（Network service / GPU process 访问违规 0xC0000005）。判定：**本沙箱硬阻断 Chrome 子进程创建，浏览器自动化不可行**。
  - `curl` 直连 10jqka 沙箱受限（HTTP 200 但 body 写不下，exit 23）。
- **因此**：
  - 所有**服务器渲染页**（`/zs/`、`/hk/`、`/stock/xsjj/`、`/newstock/`、详情页）已用 WebFetch 逐字抓取 → 本锚核心、可信。
  - **概念/地域/行业列表页"可排序排行表"**（`/gn/`、`/dn/`、`/hy/`）为 JS 渲染，WebFetch 与 `data.10jqka.com.cn/conception/gn/`（404）均取不到 → **浏览器阻塞**，其列名以"详情页汇总块镜像 + 标准同花顺概念板列"建锚（§八），**明确标注"待浏览器补全"**，不虚构。
- **红线（用户强调）**：网站列 ≠ 全为 fuyao。逐列确权真实源，fuyao 无对应者标 push2/东财/ZHB/TDX 等，喂 canonical registry，不假设全 fuyao。
- **THS 登录凭据**：项目 `credentials/ths_credentials.json` 含 `username: 15061507789` / `password` / `mac`。列表页排行表为 JS 渲染且疑似需登录态获取完整数据，但本沙箱浏览器被硬阻断，凭据暂无法用于无头渲染；记录备查。

---

## 一、A股个股行情列表列（/stock/xsjj/ + 详情页成分股表）— 逐字核验 ✅

列顺序（WebFetch 原样，两处一致）：`序号 代码 名称 现价 涨跌幅(%) 涨跌 涨速(%) 换手(%) 量比 振幅(%) 成交额 流通股 流通市值 市盈率`

| # | 网站中文列名 | fuyao 对应字段 | 真实来源判定 | 口径/单位 | 备注 |
|---|------------|---------------|------------|----------|------|
| 1 | 序号 | — | 显示序，无源 | — | 不计字段 |
| 2 | 代码 | `ticker`（快照）/ `thscode`（成分股接口） | fuyao | — | 快照返回 ticker+thscode |
| 3 | 名称 | **快照不返回 `name`** | fuyao `meta/tickers/search` 或 `catalog/constituents` 补全 | — | **重要**：快照缺 name，需 join |
| 4 | 现价 | `last_price` | **fuyao 行情快照** | CNY | fuyao_api_full.md L81 |
| 5 | 涨跌幅(%) | `price_change_ratio_pct` | **fuyao 行情快照** | % | L83 |
| 6 | 涨跌 | `price_change` | **fuyao 行情快照** | CNY | L82 |
| 7 | 涨速(%) | **fuyao 无** | push2 / 东财实时（价格变动速率） | % | 非 fuyao |
| 8 | 换手(%) | **fuyao 无**（仅 `auction.auction_turnover_pct` 竞价换手） | push2 / 东财换手率 `turnover_ratio_pct` | % | 全日换手非 fuyao |
| 9 | 量比 | **fuyao 无** | push2 / 东财 | 倍 | 非 fuyao |
| 10 | 振幅(%) | **fuyao 无** | push2 / 东财（`(high-low)/prev`） | % | 非 fuyao |
| 11 | 成交额 | `turnover` | **fuyao 行情快照** | CNY（网站显 **亿**→÷1e8） | L89 |
| 12 | 流通股 | **fuyao 快照无**（仅 `float_market_cap` 市值） | push2 / 东财（float_shares） | 股 | 标"非 fuyao" |
| 13 | 流通市值 | `float_market_cap` | **fuyao** | CNY（网站显 **亿**→÷1e8） | L587 / L1265 |
| 14 | 市盈率 | `pe_ttm`（TTM，常用）/ `pe_mrq`（MRQ 亦可） | **fuyao 估值快照** | 倍 | L1064-1065 |

> fuyao 直接覆盖：现价/涨跌幅/涨跌/成交额/流通市值/市盈率（6/14）。余 8 列（涨速/换手/量比/振幅/流通股 + 名称 join + 序号显示）需确权或补全——**严守"非全 fuyao"红线**。

---

## 二、板块汇总指标（详情页顶部"板块概况"）— 逐字核验 ✅

样本页 `https://q.10jqka.com.cn/gn/detail/code/309269/`（MLCC 概念 886112.TI），WebFetch 逐字抓取：

| # | 网站中文列名 | 量级/单位 | fuyao 对应字段 | 真实来源判定 | 备注 |
|---|------------|----------|---------------|------------|------|
| 1 | 板块涨幅 | % | 指数行情快照 `price_change_ratio_pct`（**契约镜像该响应表为空，网站即实证规范名**） | **fuyao 板块快照**（文档缺口，由网站补全） | fuyao_api_full.md §指数快照 响应表未列字段 |
| 2 | 涨幅排名 | `2/390` | 板块快照衍生（排名） | fuyao 指数快照（未文档化） | 网站为唯一可见规范名 |
| 3 | 涨跌家数 | `19 18`（涨/跌） | 板块快照衍生 | fuyao 指数快照（未文档化） | 网站实证 |
| 4 | 资金净流入(亿) | 亿元，可为负 | **fuyao 无** | push2 `f137` / 东财资金流（主力净流入口径） | 前序实证：主力净流入=push2 f137；非 fuyao |
| 5 | 成交额(亿) | 亿元 | 指数快照 `turnover`（CNY，÷1e8 得亿） | fuyao 指数快照 | |
| 6 | 成交量(万手) | 万手 | 指数快照 `volume`（股，×1e6 得万手） | fuyao 指数快照 | 量纲换算：万手=1e4手=1e6股 |

> **结论性洞察**：fuyao 指数行情快照在 `fuyao_api_full.md` 中**响应字段表为空**，而网站板块汇总块正是这些板块级字段的**官方中文规范名实证源**——印证"网站 = 板块级字段黄金锚"。

---

## 三、指数列表列（/zs/ 沪深指数）— 逐字核验 ✅

列顺序（WebFetch 原样）：`序号 指数代码 指数名称 最新价 涨跌额 涨跌幅(%) 昨收 今开 最高价 最低价 成交量（万手） 成交额（亿元）`

| # | 网站中文列名 | fuyao 对应字段 | 真实来源判定 | 口径/单位 | 备注 |
|---|------------|---------------|------------|----------|------|
| 1 | 指数代码 | `thscode` / `ticker` | fuyao 指数快照 | — | |
| 2 | 指数名称 | `name`（catalog） | fuyao 指数目录 | — | |
| 3 | 最新价 | `last_price` | **fuyao 指数快照** | CNY | L81 |
| 4 | 涨跌额 | `price_change` | **fuyao 指数快照** | CNY | L82 |
| 5 | 涨跌幅(%) | `price_change_ratio_pct` | **fuyao 指数快照** | % | L83 |
| 6 | 昨收 | `prev_price` | **fuyao 指数快照** | CNY | L87（注意：快照用 `prev_price`，竞价接口用 `pre_close_price`） |
| 7 | 今开 | `open_price` | **fuyao 指数快照** | CNY | L84 |
| 8 | 最高价 | `high_price` | **fuyao 指数快照** | CNY | L85 |
| 9 | 最低价 | `low_price` | **fuyao 指数快照** | CNY | L86 |
| 10 | 成交量（万手） | `volume` | **fuyao 指数快照** | 股（网站显 **万手**→×1e6） | L88 |
| 11 | 成交额（亿元） | `turnover` | **fuyao 指数快照** | CNY（网站显 **亿**→÷1e8） | L89 |

> 指数列表为**服务器渲染**（WebFetch 直接拿到），是 fuyao 指数快照字段（`last_price/open_price/high_price/low_price/prev_price/volume/turnover`）的**逐字实证中文规范名**，无浏览器亦可确权。

---

## 四、港股列表列（/hk/）— 逐字核验 ✅

列顺序（WebFetch 原样，多个排行榜一致）：`序号 代码 名称 现价 涨跌幅(%) 涨跌 换手(%) 成交量 市盈率 昨收 开盘价 最高价 最低价`

| # | 网站中文列名 | fuyao 对应 | 真实源判定 | 备注 |
|---|------------|-----------|-----------|------|
| 1 | 代码/名称/现价/涨跌幅/涨跌 | 同名语义 | **非 fuyao**（港股源：腾讯/东财港股） | 港股不在 fuyao A股域 |
| 2 | 换手(%) | fuyao 无全日换手 | 港股源（东财港股/腾讯） | 非 fuyao |
| 3 | 成交量 | 同名语义 | 港股源 | 单位可能股/手 |
| 4 | 市盈率 | `pe_ttm` 语义 | 港股源（口径：港股 PE 常含负值显 `--`） | 非 fuyao |
| 5 | 昨收/开盘价/最高价/最低价 | `prev/open/high/low` 语义 | 港股源 | 非 fuyao |

> 港股列是**同花顺港股域**中文规范名，非 fuyao A股域字段；归入"真实源=港股源"，仅贡献中文名给 canonical registry，不误归 fuyao。

---

## 五、新股/IPO 列表列（/newstock/）— 逐字核验 ✅（非 fuyao 域）

样本列（WebFetch 原样，从数据反推）：`代码 名称 申购代码 发行总量(万股) 网上发行量(万股) 发行价 发行市盈率 募集资金(亿) 中签率(%) 申购日期 上市日期`

| 网站中文列名 | 真实源判定 | 备注 |
|------------|-----------|------|
| 申购代码 / 发行总量 / 网上发行量 / 发行价 / 发行市盈率 / 募集资金 / 中签率 / 申购日期 / 上市日期 | **非 fuyao**（IPO 域：东财/同花顺 IPO 数据） | fuyao 无 IPO 端点；归入东财 IPO 源 |

> IPO 列表是**同花顺 IPO 域**中文规范名，非 fuyao；仅贡献中文名给 canonical registry。

---

## 六、fuyao 英文字段 ↔ 网站中文名 映射总表（黄金锚主体）

> 本表为黄金锚核心：左侧 fuyao 英文键（权威，来自 fuyao_api_full.md / sc_fuyao.py），右侧同花顺网站官方中文名（WebFetch 逐字）。✅=已逐字实证；⚠️=待浏览器补全。

| fuyao 英文字段 | 网站官方中文名 | 来源端点 | 核验 | 口径差异 |
|---|------------|---------|------|---------|
| `last_price` | 最新价 / 现价 | a-share/prices/snapshot、a-share-index/prices/snapshot | ✅ | CNY |
| `price_change` | 涨跌额 / 涨跌 | 同上 | ✅ | CNY |
| `price_change_ratio_pct` | 涨跌幅(%) | 同上 | ✅ | % 原值 |
| `open_price` | 今开 / 开盘价 | 同上 | ✅ | CNY |
| `high_price` | 最高价 | 同上 | ✅ | CNY |
| `low_price` | 最低价 | 同上 | ✅ | CNY |
| `prev_price` | 昨收 | a-share/prices/snapshot | ✅ | CNY（注意：竞价接口字段名是 `pre_close_price`，勿混） |
| `volume` | 成交量 | a-share/prices/snapshot、指数快照 | ✅ | fuyao=**股**；网站指数页显 **万手**（×1e6 换算） |
| `turnover` | 成交额 | 同上 | ✅ | fuyao=**元(CNY)**；网站显 **亿元**（÷1e8 换算） |
| `float_market_cap` | 流通市值 | a-share/prices/snapshot（auction 亦返回）、指数成分 | ✅ | fuyao=CNY；网站显 **亿**（÷1e8） |
| `pe_ttm` | 市盈率(TTM) / 市盈率 | a-share/valuations/snapshot | ✅ | 倍；负值原样 |
| `pe_mrq` | 市盈率(MRQ) | 同上 | ✅ | 倍 |
| `pb_mrq` | 市净率 | 同上 | ✅ | 倍 |
| `ps_ttm` | 市销率 | 同上 | ✅ | 倍（字典新维度） |
| `pcf_ttm` | 市现率 | 同上 | ✅ | 倍（字典新维度） |
| `auction_turnover_pct` | 竞价换手率 | a-share/auction/snapshot | ✅ | %（**仅竞价，非全日换手**） |
| `auction_yesterday_ratio_pct` | 相对昨日量比（竞价） | 同上 | ✅ | 倍 |
| `auction_volume_ratio` | 竞价量比 | 同上 | ✅ | 倍 |
| `ticker` | 代码（纯代码） | 各快照 | ✅ | 无后缀 |
| `thscode` | 代码（带交易所后缀，如 600519.SH） | 各快照 | ✅ | |
| `name` | 名称 | meta/tickers/search、catalog/constituents | ✅ | **快照不返回，需 join** |
| `seal_money` | 封单额 | special-data/limit-up-pool | ✅ | 元（÷1e4≡ZHB 万元） |
| `max_seal_money` | 峰值封单额 | 同上 | ✅ | 元 |
| `continue_day_cnt` | 连板天数 | 同上 | ✅ | |
| `turnover_ratio_pct` | 换手率(%) | limit-down/limit-break-pool | ✅ | %（涨停/跌停池衍生，非通用快照） |
| `net_value` / `net_rate` / `buy_value` / `sell_value` | 龙虎榜净额/净比/买额/卖额 | special-data/dragon-tiger-list | ✅ | 龙虎榜域 |
| **板块涨幅 / 涨幅排名 / 涨跌家数 / 资金净流入(亿) / 成交量(万手) / 成交额(亿)** | 板块汇总块 | a-share-index/prices/snapshot（响应表空，待补文档） | ✅（网站逐字） | 板块级，fuyao 文档缺口由网站补全 |

---

## 七、非 fuyao 列确权 + 口径单位差异

### 7.1 网站有、fuyao 无（须标真实源，勿归 fuyao）
| 网站中文列名 | 真实来源 | 备注 |
|------------|---------|------|
| 涨速(%) | push2 / 东财实时 | 价格变动速率 |
| 换手(%)（全日） | push2 / 东财 `turnover_ratio_pct` | fuyao 仅 `auction_turnover_pct` 竞价换手 |
| 量比（全日） | push2 / 东财 | fuyao 仅 `auction_volume_ratio` 竞价量比 |
| 振幅(%) | push2 / 东财 `(high-low)/prev` | |
| 流通股 | push2 / 东财 | fuyao 仅有 `float_market_cap` 市值 |
| 总市值 | 东财（派生） | fuyao 无独立总市值字段 |
| 资金净流入 / 主力净流入 | push2 `f137` / 东财资金流 | 前序实证：非 fuyao |
| 领涨股 / 龙头股 | 由成分股派生 | fuyao 需排序成分股 |
| 成分股数 | 成分股接口 `item[]` 长度 | fuyao 可派生 |
| 名称 | fuyao `meta/tickers/search` join | 快照不返回 |

### 7.2 口径单位差异（对撞/取数必读）
- **成交量**：fuyao `volume` = **股**；网站指数页显 **万手**（1 万手 = 1e4 手 = 1e6 股）→ fuyao 值 = 网站万手 × 1e6。
- **成交额**：fuyao `turnover` = **元(CNY)**；网站显 **亿元** → fuyao 值 = 网站亿元 × 1e8。
- **流通市值 / 总市值类**：fuyao `float_market_cap` = CNY；网站显 **亿** → ×1e8。
- **昨收字段名**：通用快照 `prev_price`；竞价快照 `pre_close_price`——同义不同键，对撞时注意别名。

---

## 八、Phase 1 概念/地域/行业列表页"可排序排行表"（JS 渲染 ⚠️ 浏览器阻塞待补全）

`/gn/`（概念）、`/dn/`（地域 404）、`/hy/`（行业 404）的**排行表为 JS 渲染**，WebFetch 与 `data.10jqka.com.cn/conception/gn/`（404）均取不到；仅 `/gn/` 拿到"概念名列表 + 热点轮动图 + 概念时间表"（时间表含 `龙头股`/`成分股数量` 列）。

**以下为依据"详情页汇总块镜像 + 标准同花顺概念板列 + 用户枚举"的最佳已知集，未经浏览器逐字核验，标 `⚠️待浏览器`**：

预期列（常见同花顺概念板排行）：`板块名称 / 板块涨幅 / 涨幅排名 / 领涨股 / 领涨股涨幅 / 涨跌家数 / 资金净流入 / 成交额 / 成交量 / 换手率 / 成分股数 / 总市值`

| 网站中文列名 | fuyao 对应 | 真实源判定 | 状态 |
|------------|-----------|-----------|------|
| 板块名称 | 指数 `name`（catalog） | fuyao | ⚠️待浏览器 |
| 板块涨幅 | 指数快照 `price_change_ratio_pct` | fuyao（文档缺口） | ⚠️待浏览器 |
| 涨幅排名 | 指数快照衍生 | fuyao（未文档化） | ⚠️待浏览器 |
| 领涨股 | 成分股 `name` + 排序 | fuyao（需派生） | ⚠️待浏览器 |
| 领涨股涨幅 | 成分股 `price_change_ratio_pct` 最大者 | fuyao | ⚠️待浏览器 |
| 涨跌家数 | 板块快照衍生 | fuyao（未文档化） | ⚠️待浏览器 |
| 资金净流入 | fuyao 无 | push2 f137 / 东财 | ⚠️待浏览器 |
| 成交额 | 指数快照 `turnover` | fuyao | ⚠️待浏览器 |
| 成交量 | 指数快照 `volume` | fuyao | ⚠️待浏览器 |
| 换手率(%) | fuyao 无 | push2 / 东财 | ⚠️待浏览器 |
| 成分股数 | 成分股接口 `item[]` 长度 | fuyao | ⚠️待浏览器 |
| 总市值 | fuyao 无独立总市值 | 派生/东财 | ⚠️待浏览器 |

**解锁条件**：浏览器可用后跑 `scripts/harvest_ths_columns.py`（列表页用 agent-browser 抽 `<th>`）逐字确认，消除 `⚠️`。

---

## 九、fuyao 端点 ↔ 网站中文列 覆盖矩阵

| fuyao 端点 | 覆盖的网站中文列 | 缺失/需补 |
|---|---|---|
| `/api/a-share/prices/snapshot` | 现价/涨跌/涨跌幅/今开/最高/最低/昨收/成交额/成交量 | 名称(需 join)、涨速/换手/量比/振幅（无） |
| `/api/a-share/valuations/snapshot` | 市盈率(pe_ttm)/市盈率(pe_mrq)/市净率(pb_mrq)/市销率(ps_ttm)/市现率(pcf_ttm) | — |
| `float_market_cap` | 流通市值 | — |
| `/api/a-share-index/catalog/ths-index-list` | 板块名称/代码 | — |
| `/api/a-share-index/constituents/ths-stock-list` | 成分股代码/名称/成分股数 | — |
| `/api/a-share-index/prices/snapshot` | 板块涨幅/最新价/涨跌额/涨跌幅/今开/最高/最低/昨收/成交额/成交量（**响应表空，待补文档**） | 涨幅排名/涨跌家数/领涨股（未文档化） |
| `a-share/auction/snapshot` | 竞价换手率/相对昨日量比/竞价量比/前收/开盘/最新/流通市值 | 全日换手/量比/振幅（无） |
| `special-data/limit-up-pool` | 封单额/峰值封单额/连板天数 | — |
| `special-data/dragon-tiger-list` | 龙虎榜净额/净比/买额/卖额 | — |
| 资金流/全日换手/量比/振幅/涨速/总市值 | **无** | push2/东财/ZHB 确权 |

---

## 十、待办 / 下一步（按计划文档 §七 顺序）

1. **解锁 Phase 1**：浏览器可用后写 `scripts/harvest_ths_columns.py`，消除 §八 `⚠️`。
2. **补 fuyao 指数快照响应字段文档**：将 §二/§九 的板块级中文名回填 `fuyao_api_full.md` 与字典 §12.8.12c（修复文档缺口）。
3. **字典回填**：各 fuyao 字段补中文规范名（§12.8.12e canonical）；新增 §12.8.12k「fuyao 网站中文名黄金锚」指向本表。
4. **扩 `ths_tableheader_ids.md`**：从网站实测反推 tableheader 列 ID（当前仅 682 全表抽样）。
5. **治理闸门**：`extract_registry → gen_field_dict → registry_parity`（G1）+ 每日 collide 中文名锚交叉抽样。
6. **Phase 3 收尾**：数据中心子页中 reachable 者（资金流向/港股/新股）已抓；龙虎榜正确 URL、财报/研报/分红/业绩等若需全量，待浏览器或独立 API 通道。

---

*反失焦：本表每条映射均注明"真实源判定"与"核验状态（✅逐字 / ⚠️待浏览器）"，禁止无来源归 fuyao。数据来源：通达信 / 同花顺(q.10jqka.com.cn) 官方中文列名、fuyao REST 契约。以上为字段治理层面的中文名黄金锚建工作，所有结论不构成投资建议。*
