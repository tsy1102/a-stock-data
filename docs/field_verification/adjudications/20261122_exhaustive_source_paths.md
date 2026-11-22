# 2026-11-22 穷尽破解批次：来源路径与官方契约

复核日期：2026-11-22。此批将碰撞报告里的来源路径缺口按官方页面/脚本、项目实际解析链和留存原始值逐批补齐。精确路径才是登记单位；不同接口的同号字段不合并。

## 批量登记范围

- 东方财富 clist：板块当前值、涨跌额、领涨/领跌股票代码与市场号；官方脚本目前仅确认 f128/f140/f141 和 f207/f208/f209 组。f257/f258/f259 的组别未被官方脚本绑定，且保留样本 f257 是名称文本，旧文档将 f257 归作 5 日资金流的说法错误，故不在本批误定案。
- 上交所 ETF：SSE `ETF_TYPE` 原值映射到 `etf_sh.etf_type`；仅适用于上交所路径。
- 新浪研报：官方表头“报告类型”映射 `type`；URL 的 `/rptid/{id}/` 映射 `report_id`。
- 上证 e 互动：按 `id=item-{id}` 解析条目 ID；只从回答块解析 `answer_time`，不与提问时间混淆。
- 可转债：第一方 detail.js 显示了两个执行原因路径的 1–5 含义；样本观察到 code 6 但脚本没有分支，故 code 6 未决。`ISSUE_TYPE`、`PAYDAYNEW` 先只确立精确原始路径，完整代码语义见 E3 批次。
- IPO 与开盘啦：登记原始响应路径，随后由 E3 的公式、逐日 K 线、发行人正式文件和原始列样本定案；与本文件对应的 E3 文件明确限定样本日期/市场，不外推未观测时期。

## 原始证据与边界

- IPO 发行记录逐行审计：`docs/field_verification/research/20261122_eventdc_ipo_500_row_audit.csv`。
- IPO 成交均价六股逐日核验：`docs/field_verification/research/20261122_eventdc_ipo_kline_six_stock_audit.csv`。
- IPO 最新价六股和报价日期核验：`docs/field_verification/research/20261122_eventdc_ipo_latest_quote_six_stock_audit.csv`。
- IPO 招股书锚点：`docs/field_verification/research/20261122_eventdc_ipo_issuer_anchor_pairs.csv`。
- 可转债 3 次保留响应的路径审计：`docs/field_verification/research/20261122_eventdc_convertible_issue_type_payday_audit.csv`；500 个不同债券，重复抓取只作稳定性复核。
- KPL 非空 col_18 行：`docs/field_verification/research/20261122_kpl_raw_col18_samples.csv`；所有原始值保持，不与 KPH 字段做同义推断。
- 募资总额原生单位复算：`docs/field_verification/research/20261122_eventdc_ipo_gross_funds_formula_audit.csv`；按代码对应交易所分别保留亿元/元原生单位。
- 未在此批替未知字段造义：`IS_CONVERT_STOCK`、KPL col_02/col_03、clist f257/f258/f259、IPO `IS_RISKWARNING`/`ORG_TYPE`/`PE_TTM` 继续按证据缺口或无信息量登记在综合处置表。

## 第一方公开来源

- 东方财富板块排行及随页 JS：`https://quote.eastmoney.com/center/boardlist.html`。
- 东方财富可转债详情字段渲染脚本：`https://data.eastmoney.com/newstatic/js/kzz/detail.js`。
- 东方财富 IPO 页面及详情页：`https://data.eastmoney.com/xg/xg/?mkt=zh`；`https://data.eastmoney.com/xg/xg/detail/688827.html`。
- 上交所 ETF 官方细分类型列表：`https://www.sse.com.cn/assortment/fund/list/?type=5`；交易所产品分类文件链接见项目裁决记录。
- 新浪官方研报列表：`https://stock.finance.sina.com.cn/stock/go.php/vReport_List/kind/lastest/index.phtml`。
- 上证 e 互动使用手册：`https://sns.sseinfo.com/resources/files/help.pdf`。

以上映射只针对表中完整来源路径。状态 `verified_by_source_contract` 证明来源身份/官方渲染路径，不代表项目已经建立跨源等价或自动统一层映射。
