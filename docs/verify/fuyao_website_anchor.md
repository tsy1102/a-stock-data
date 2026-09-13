# fuyao 源「网站中文列名 ↔ 英文字段」黄金锚

> 状态：进行中（Phase 0–2 已落地，列表页排行表浏览器阻塞待补）
> 创建：2026-09-13 ｜ 关联计划：`docs/field_verification/20260913_fuyao_website_anchor_plan.md`
> 数据来源：通达信 / 同花顺 `q.10jqka.com.cn` 官方中文列名、`fuyao_api_full.md` 全量字段契约镜像（`docs/verify/`）。
> 说明：本表为字段治理的"中文名黄金锚"，仅登记/映射，不改动任何运行时取数路径。所有结论不构成投资建议。

---

## 〇、方法与环境约束（防失焦首读）

- **目标**：把 `q.10jqka.com.cn` 可见中文列名逐列映射到 fuyao 英文字段，建立"中文名 ↔ 英文键 ↔ 真实来源 ↔ 口径单位"三元锚，固化后供后期对撞/破解按中文名检索。
- **抽取通道实测**：
  - `WebFetch` 通道**可用**：板块详情页（`/gn/detail/code/XXX/`）的成分股表 + 板块汇总块已逐字抓取成功（样本 `886112.TI` MLCC 概念，2026-09-13 实测）。
  - `agent-browser`（Chrome 153）**本沙箱无法启动**：`open about:blank`（无网络）亦零输出挂起、`timeout` 杀不掉，Chrome 进程残留。→ **浏览器自动化在本环境被硬阻断**。
  - `curl` 直连 10jqka 沙箱受限（HTTP 200 但 body 写不下）。
- **因此**：
  - **Phase 2（板块详情成分股表）+ 板块汇总块**：WebFetch 全做，已逐字核验 → 本表核心、可信。
  - **Phase 3（数据中心子页）**：WebFetch 逐页可达即做，非 fuyao 列标真实源。
  - **Phase 1（概念/地域/行业列表页"可排序排行表"）**：该表为 JS 渲染，WebFetch 与 `data.10jqka.com.cn/conception/gn/`（404）均拿不到 → **浏览器阻塞**。其列名以"详情页汇总块镜像 + 标准同花顺概念板列"建锚（§三），**明确标注"待浏览器补全"**，不虚构。
- **红线（用户强调）**：网站列 ≠ 全为 fuyao。逐列确权真实源，fuyao 无对应者标 push2/东财/ZHB/TDX 等，喂 canonical registry，不假设全 fuyao。

---

## 一、板块汇总指标（详情页顶部"板块概况"）— 逐字核验 ✅

样本页 `https://q.10jqka.com.cn/gn/detail/code/309269/`（MLCC 概念 886112.TI），WebFetch 逐字抓取：

| # | 网站中文列名 | 量级/单位 | fuyao 对应字段 | 真实来源判定 | 备注 |
|---|------------|----------|---------------|------------|------|
| 1 | 板块涨幅 | % | 指数行情快照 `price_change_ratio_pct`（**契约镜像该响应表为空，网站即实证规范名**） | **fuyao 板块快照**（文档缺口，由网站补全） | fuyao_api_full.md §434 响应表未列字段 |
| 2 | 涨幅排名 | `2/390` | 板块快照衍生（排名） | fuyao 指数快照（未文档化） | 网站为唯一可见规范名 |
| 3 | 涨跌家数 | `19 18`（涨/跌） | 板块快照衍生 | fuyao 指数快照（未文档化） | 网站实证 |
| 4 | 资金净流入(亿) | 亿元，可为负 | **fuyao 无** | push2 `f137` / 东财资金流（主力净流入口径） | 前序实证：主力净流入=push2 f137；非 fuyao |
| 5 | 成交额(亿) | 亿元 | 指数快照 `turnover`（CNY，÷1e8 得亿） | fuyao 指数快照 | |
| 6 | 成交量(万手) | 万手 | 指数快照 `volume`（股，÷1e4÷100 得万手） | fuyao 指数快照 | 量纲换算 |

> **结论性洞察**：fuyao 指数行情快照（§434）在 `fuyao_api_full.md` 中**响应字段表为空**，而网站板块汇总块正是这些板块级字段的**官方中文规范名实证源**——印证"网站 = 板块级字段黄金锚"。

---

## 二、成分股列表（详情页"成分股涨跌排行榜"）— 逐字核验 ✅

列顺序（WebFetch 原样）：`序号 代码 名称 现价 涨跌幅(%) 涨跌 涨速(%) 换手(%) 量比 振幅(%) 成交额 流通股 流通市值 市盈率`

| # | 网站中文列名 | fuyao 对应字段 | 真实来源判定 | 口径/单位 | 备注 |
|---|------------|---------------|------------|----------|------|
| 1 | 序号 | — | 显示序，无源 | — | 不计字段 |
| 2 | 代码 | `ticker`（快照）/ `thscode`（成分股接口） | fuyao | — | 快照返回 ticker+thscode |
| 3 | 名称 | **快照不返回 `name`** | fuyao `catalog/constituents` 接口补全 | — | **重要**：快照缺 name，需 join `/api/a-share-index/constituents/ths-stock-list` 或 `/api/meta/tickers/search` |
| 4 | 现价 | `last_price` | **fuyao 行情快照** | CNY | §行情快照 L81 |
| 5 | 涨跌幅(%) | `price_change_ratio_pct` | **fuyao 行情快照** | % | L83 |
| 6 | 涨跌 | `price_change` | **fuyao 行情快照** | CNY | L82 |
| 7 | 涨速(%) | **fuyao 无** | push2 / 东财实时（价格变动速率） | % | 非 fuyao |
| 8 | 换手(%) | **fuyao 无**（仅 `auction.auction_turnover_pct` 竞价换手） | push2 / 东财换手率 | % | 全日换手非 fuyao |
| 9 | 量比 | **fuyao 无** | push2 / 东财 | 倍 | 非 fuyao |
| 10 | 振幅(%) | **fuyao 无** | push2 / 东财（`(high-low)/prev`） | % | 非 fuyao |
| 11 | 成交额 | `turnover` | **fuyao 行情快照** | CNY（网站显亿） | L89 |
| 12 | 流通股 | **fuyao 快照无** | fuyao 个股资料/基本面端点（待核验 `float_shares`） | 股 | 标"待 fuyao 资料端点确权" |
| 13 | 流通市值 | `float_market_cap` | **fuyao** | CNY | L587 / L1265 |
| 14 | 市盈率 | `pe_ttm`（TTM，常用）/ `pe_mrq`（MRQ 亦可） | **fuyao 估值快照** | 倍 | §估值快照 L1064-1065 |

> fuyao 直接覆盖：现价/涨跌幅/涨跌/成交额/流通市值/市盈率（6/14）。余 8 列（涨速/换手/量比/振幅/流通股 + 名称 join + 序号显示）需确权或补全——**严守"非全 fuyao"红线**。

---

## 三、板块列表页"可排序排行表"列（Phase 1，浏览器阻塞 ⚠️ 待补全）

该表 JS 渲染，WebFetch 与 `data.10jqka.com.cn/conception/gn/`（404）均取不到。**以下为依据"详情页汇总块镜像 + 标准同花顺概念板列 + 用户枚举"的最佳已知集，未经浏览器逐字核验，标 `⚠️待浏览器`**：

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
| 总市值 | fuyao 无独立总市值（仅 `float_market_cap`） | 派生/东财 | ⚠️待浏览器 |

**解锁条件**：浏览器可用后跑 `scripts/harvest_ths_columns.py`（列表页用 agent-browser 抽 `<th>`）逐字确认，消除 `⚠️`。

---

## 四、fuyao 端点 ↔ 网站中文列 覆盖矩阵

| fuyao 端点（fuyao_api_full.md） | 覆盖的网站中文列 | 缺失/需补 |
|-------------------------------|----------------|----------|
| `/api/a-share/prices/snapshot`（§行情快照 L61） | 现价/涨跌/涨跌幅/成交额/成交量 | 名称(需 join)、涨速/换手/量比/振幅（无） |
| `/api/a-share/valuations/snapshot`（§估值 L1032） | 市盈率(pe_ttm)/市净率(pb_mrq) | — |
| `float_market_cap`（L587/1265） | 流通市值 | — |
| `/api/a-share-index/catalog/ths-index-list`（§404） | 板块名称/代码 | — |
| `/api/a-share-index/constituents/ths-stock-list`（§419） | 成分股代码/名称/成分股数 | — |
| `/api/a-share-index/prices/snapshot`（§434） | 板块涨幅/成交额/成交量（**响应表空，待补文档**） | 涨幅排名/涨跌家数/领涨股（未文档化） |
| 资金流/换手/量比/振幅/涨速 | **无** | push2/东财/ZHB 确权 |

---

## 五、待办 / 下一步（按计划文档 §七 顺序）

1. **解锁 Phase 1**：浏览器可用后写 `scripts/harvest_ths_columns.py`，消除 §三 `⚠️`。
2. **补 fuyao 指数快照响应字段**：将 §一/§四 的板块级中文名回填 `fuyao_api_full.md` 与字典 §12.8.12c（修复文档缺口）。
3. **字典回填**：各 fuyao 字段补中文规范名（§12.8.12e canonical）；新增 §12.8.12k「fuyao 网站中文名黄金锚」指向本表。
4. **扩 `ths_tableheader_ids.md`**：从网站实测反推 tableheader 列 ID（当前仅 682 全表抽样）。
5. **治理闸门**：`extract_registry → gen_field_dict → registry_parity`（G1）+ 每日 collide 中文名锚交叉抽样。
6. **Phase 3**：数据中心子页（资金流向/龙虎榜/热度/新股/财报/业绩/分红/研报/港股/美股）逐页 WebFetch 抽取。

---
*反失焦：本表每条映射均注明"真实源判定"与"核验状态（✅逐字 / ⚠️待浏览器）"，禁止无来源归 fuyao。*
