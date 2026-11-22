# 2026-11-22 穷尽破解批次：E3 语义裁决

复核日期：2026-11-22。此批把来源身份登记后的字段按可重放的公式、同记录关联、上市交易日 K 线和发行人正式材料批量定案。官方定义与样本一致的字段直接定案；单位或日期边界存在差异的保留原生口径，不把不完整证据外推。

## 批次结果与证据文件

- IPO 募资总额公式：420/500 按市场原生单位复算匹配；沪深记录以亿元、北交所记录以元保留。见 `research/20261122_eventdc_ipo_gross_funds_formula_audit.csv`。
- 可转债 ISSUE_TYPE/PARAM_NAME 与 PAYDAYNEW：500 个不同债券，三次归档快照共 1500 行；由全部组合唯一反推代码到中文类别的映射数 `1`，不同债券映射吻合 `500`，重复快照负日号公式 `1500` 行吻合。E3 样本计数按单次快照的不同债券，不把重复抓取算作独立日期样本。
- KPL col_18：保留期 1,259 条行记录中 115 条非空，其中 115 条符合可观察的 N天M板/N连板描述格式；覆盖 21 个 KPL 来源交易日。col_02 和 col_03 不作语义猜测。
- IPO AVERAGE_PRICE：6 只跨年份、跨沪深板块样本在上市后第 5 个交易日的 VWAP 误差不超过 0.0018 元；旧 20 行早期样本不能区分几个均价字段，故撤回“AVERAGE_PRICE 是 TOTAL_CHANGE 基准价”的旧解释并留存旧裁决历史。
- 其余 IPO 字段按各自公式/发行人文件核验；每条 E3 sample 记录比较数、排除数、股票数和正式文件数，研究 CSV 保留逐行输入及误差。

## 时间与市场边界

1. IPO 首日振幅以 LISTING_DATE 的交易日 K 线验证；不能用采集自然日替代上市交易日。
2. TNEW_PRICE、CHANGE、CHANGE_RATE 属于接口最新报价字段；若接口未提供行情来源日，采集目录目标日不能充当 as-of 日期。字段语义定案与日频碰撞资格分别处理。
3. AVERAGE_PRICE 的第 5 个交易日含义只应用于本批 6 个实测样本；未验证的历史发行制度保留其年代边界。它与 LD_AVERAGE_PRICE、OPEN_AVERAGE_PRICE、TOTAL_CHANGE 各自独立。
4. 可转债发行类型和付息日是稳定条款字段；三份重复采集用于重复性检查，不计算成三个独立来源日。PAYDAYNEW 是负日号编码，不是日期值。
5. 募资金额不同交易所的响应单位不一致；registry 保留原生单位，任何统一换算须由消费者显式执行。
6. 本批没有建立不同来源的等价映射或采集替代关系；KPL col_18 不与 KPH 字段合并。

## 仍保留的未知项

未在本次 E3 决策中硬定案的 `IS_CONVERT_STOCK`、IPO `IS_RISKWARNING`/`ORG_TYPE`/`PE_TTM`、KPL col_02/col_03、clist f257/f258/f259 和 ulist239.f63 仍见同目录《全目标处置与未决项》；原因是原始值缺乏变化、缺少精确官方映射、历史字段不具现代覆盖或多候选不可区分。未决表示明确保留调查边界，不表示停止后续批量破解。

## 官方页面依据

- [东方财富 IPO 新股详情页](https://data.eastmoney.com/xg/xg/detail/688827.html)：分别标示首日成交均价、开板日期/开板日均价等事件字段；为区分旧字段重名与现代样本语义提供官方页面锚点。
- [东方财富可转债字段渲染脚本](https://data.eastmoney.com/newstatic/js/kzz/detail.js)：EXECUTE_REASON_HS/SH 的官方页面枚举映射，以及 PAY_INTEREST_DAY 的“每年付息日”绑定。
- [上交所基金列表](https://www.sse.com.cn/assortment/fund/list/?type=5)和[ETF 分类规范](https://www.sse.com.cn/services/tradingtech/development/c/10760533/files/d5e67c2ce55d44098321a71f5e560751.pdf)：`ETF_TYPE` 的分类边界。
- [新浪财经研报列表](https://stock.finance.sina.com.cn/stock/go.php/vReport_List/kind/lastest/index.phtml)：列表字段“报告类型”、详情链接/报告标识。
- [上证 e 互动使用手册](https://sns.sseinfo.com/resources/files/help.pdf)：提问与上市公司回复是不同事件块。具体 id/time 的 DOM 绑定由项目 parser 逐行确认。

- `adjudications/20261121_eventdc_ipo_average_price.md` — canonical LF SHA-256 `37b0e7da7b486ec3faad5c85166d1ebd170fd630a62977c621f3c60e30bf9d33`。
- `research/20261120_eventdc_ipo_first_day_contract_samples.csv` — canonical LF SHA-256 `fdcd685ea570d06e84684381be5c548464608e4f3d9f7f160f5c56c308c1b9c9`。
- `research/20261120_eventdc_ipo_semantics_samples.csv` — canonical LF SHA-256 `2d80d9c9557da72c7fe0cce3bffa505b21ceae223cafde5620b5001df41970ac`。
- `research/20261122_eventdc_convertible_issue_type_payday_audit.csv` — canonical LF SHA-256 `519b00d7fea3ac583ffaef1ebdc5cca0d046a20c972e60dd944e09d3c0d6ad5e`。
- `research/20261122_eventdc_ipo_500_row_audit.csv` — canonical LF SHA-256 `ce55ff2a6dcf95a6a46ceac175e73f1278282cebb66a61d84be4ae461e399b55`。
- `research/20261122_eventdc_ipo_gross_funds_formula_audit.csv` — canonical LF SHA-256 `cf6944bccddd6c20dcaebdf2428a05f212d412fe6d6c161a8077245808ec0ec4`。
- `research/20261122_eventdc_ipo_issuer_anchor_pairs.csv` — canonical LF SHA-256 `45feb211c5ddfeb6f074a693e09eb5e49c7d26284c7c904115bb45b4c6cbfa5d`。
- `research/20261122_eventdc_ipo_kline_six_stock_audit.csv` — canonical LF SHA-256 `69291f9659359856a28e8e90a128e15fd91845f697c80ca68807b3d8f81654ce`。
- `research/20261122_eventdc_ipo_latest_quote_six_stock_audit.csv` — canonical LF SHA-256 `9b2396f6e348e04b7109944e63b2a2a31f76b7a881ad6b8a021ad220cf56ced3`。
- `research/20261122_kpl_raw_col18_samples.csv` — canonical LF SHA-256 `52e51d1201e7f0d8e66e08162c6ff920d4395be694ea6feafc14bebbc0256960`。
