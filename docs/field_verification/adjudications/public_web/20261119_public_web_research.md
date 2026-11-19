# 财联社 `time` 字段官方页面核验

## 对象与样本范围

- 精确注册身份：`财联社(cls)::time`；来源谱系确认实际提供方为 CLS，路径状态原为 `unverified`。
- 本次盘前采集命令按交易日规则选中目标数据日 `20261118`。该日已有完整盘后归档，采集器幂等跳过重复请求；本轮没有新增 CLS 样本。归档中的 CLS 来源状态为 `ok`，实际采集开始时间为 `2026-11-18 17:00:17`（Asia/Shanghai），50 条记录。
- 破解报告：`docs/field_verification/20261119/retained_history_date_qualified_v7_20261119/20261119_collision_report.json`，schema 5，`report_completeness.status=complete`，SHA-256 `0b41e7e3c45774e974865af7a4cd380192b80a043a9fa4d78e2797d251c145f1`。候选清单将 `cls.time` 列为未验证语义，覆盖保留边界后的 20 个采集目录、1,000 条记录。
- 采集器映射：`stock_common/sc_datasource/_eastmoney.py:1183-1224` 调用 CLS `/v1/roll/get_roll_list`，读取 `data.roll_data[].ctime`，用 `datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")` 写入输出 `time`。当前 Windows 时区为 `China Standard Time`（UTC+08:00）；代码格式化采用进程本地时区。
- 对 `20261015` 起 20 个保留期 raw 目录逐条审计：`time` 共有 1,000/1,000 条符合 `YYYY-MM-DD HH:MM:SS`；350 条有来源级采集开始时间，其中没有一条晚于采集开始时间，另 650 条历史记录缺少来源级采集开始时间，不据全局目录日期推断精确采集时刻。
- 其中 150 条的时间文本日期与目标目录日期不同，均落在后一个自然日：`20261021→20261022` 50 条、`20261030→20261031` 50 条、`20261106→20261107` 25 条、`20261106→20261108` 25 条。这是字段值携带的自然日与采集目录目标数据日不同；旧归档缺少足够的逐源采集时刻，不能将其判为采集错误或数据过期，也不能把目录日期覆盖到 `time`。
- 本次选择 4 条记录逐条打开 CLS 官方详情页核对。4/4 标题和时间精确匹配；其中 2 条为带股票代码的个股电报，分别来自不同股票；另 2 条跨日期记录用于区分发布时间与正文事件时间。其余 996 条留存记录未逐条打开网页，排除在外部页面比较计数之外。

## 官方页面观察

以下 `[observation]` 行按项目约定保存结构化观察；网页均在用户授权的 Chrome 会话中直接打开，页面域名为 `api3.cls.cn`。

[observation] {"source":"财联社(cls)","code":"time","stock_code":"sh600276","data_date":"20261118","source_file":"docs/field_verification/20261118/raw_cls.json","raw_title":"恒瑞医药：获得药物临床试验批准通知书","raw_value":"2026-11-18 16:59:50","page_url":"https://api3.cls.cn/share/article/2537973?app=&os=ios&sv=839","page_title":"恒瑞医药：获得药物临床试验批准通知书","page_visible_time":"16:59:50","page_visible_datetime":"2026-11-18 16:59:50","accessed_at":"2026-11-19T03:11:23+08:00","result":"exact_match"}

[observation] {"source":"财联社(cls)","code":"time","stock_code":"sz000963","data_date":"20261118","source_file":"docs/field_verification/20261118/raw_cls.json","raw_title":"华东医药：全资子公司HDM4002注射液获临床试验批准","raw_value":"2026-11-18 16:47:05","page_url":"https://api3.cls.cn/share/article/2537948?app=&os=andr&sv=846","page_title":"华东医药：全资子公司HDM4002注射液获临床试验批准","page_visible_time":"16:47:05","page_visible_datetime":"2026-11-18 16:47:05","accessed_at":"2026-11-19T03:11:37+08:00","result":"exact_match"}

[observation] {"source":"财联社(cls)","code":"time","stock_code":"","data_date":"20261117","source_file":"docs/field_verification/20261117/raw_cls.json","raw_title":"11月17日连板股分析：连板股晋级率仅9% 九阳股份盘中上演“地天板”","raw_value":"2026-11-17 15:37:54","page_url":"https://api3.cls.cn/share/article/2536572?app=&os=andr&sv=846","page_title":"11月17日连板股分析：连板股晋级率仅9% 九阳股份盘中上演“地天板”","page_visible_time":"15:37:54","page_visible_datetime":"2026-11-17 15:37:54","accessed_at":"2026-11-19T03:11:50+08:00","result":"exact_match"}

[observation] {"source":"财联社(cls)","code":"time","stock_code":"","data_date":"20261116","source_file":"docs/field_verification/20261116/raw_cls.json","raw_title":"伊朗军队称24小时内第三艘油轮在霍尔木兹海峡触雷起火","raw_value":"2026-11-16 21:24:09","page_url":"https://api3.cls.cn/share/article/2535892?app=&os=web&sv=845","page_title":"伊朗军队称24小时内第三艘油轮在霍尔木兹海峡触雷起火","page_visible_time":"21:24:09","page_visible_datetime":"2026-11-16 21:24:09","accessed_at":"2026-11-19T03:11:59+08:00","result":"exact_match"}

页面显示：标题前有对应时分秒，详情页同时显示完整日期和时间。11 月 16 日电报正文描述事件发生在“当天早些时候”，而页面电报时间为 21:24:09，说明该字段指向电报记录的发布时间，不能当成正文事件发生时间。11 月 17 日盘面复盘电报也在收盘后显示 15:37:54；11 月 18 日两条不同股票的电报分别显示 16:59:50 与 16:47:05，与采集值逐秒一致。

## 结论与边界

将 `财联社(cls)::time` 定义为**财联社电报记录的发布时间**：采集器读取 CLS 电报响应的 Unix 秒 `ctime`，并格式化为 `YYYY-MM-DD HH:MM:SS`；在本机当前 `Asia/Shanghai`（UTC+08:00）环境下，结果与官方详情页精确一致。该值不是正文事件时间、采集开始时间、A 股交易日或采集目录目标数据日。

本裁决确认的是精确来源路径的页面时间语义，不宣称掌握 CLS 未公开的 `ctime` 字段协议文档、后续编辑是否改写时间的规则，或其他主机时区下的输出文本；不建立跨源映射，也不把其他来源的同名 `time` 推广为相同含义。

## 复核文件摘要

| 文件 | SHA-256 |
|---|---|
| `docs/field_verification/20261118/raw_cls.json` | `beff13b6902860a0f8074e6538f10a22f62bcc7bfb690aae80be8720d3c71cfd` |
| `docs/field_verification/20261117/raw_cls.json` | `7055835025cdf8b542355ac0e644a336863d5d1693678514db2a8ccc66b95db1` |
| `docs/field_verification/20261116/raw_cls.json` | `a99a12f0e4534cfe0fb4edb121b2e2789735b731ec1281280fdff7fd17753227d` |

## Ulist `f63` 候选排除：ZHB 开盘金额与东财资金流

- 候选报告：`20261119/intraday_all_history_20261119_1030/20261119_collision_report.json`，SHA-256 `0c5ce52272da1318edf2630ef59bf73225545e8d3244acc4b21e41c0a03c69cb`；candidate_id `cc1_7c11bd5bf48747534c52e86e40d49bb535a1a098d2d109c7014889feaaf94c98`。
- 精确目标为 `东财-ulist239(np/get)::f63`。碰撞候选端 `zhb.stat2.main_net_buy_amount` 是项目兼容名；ZHB 既有裁决已确认其对应 `ZHB-tdxstat2::[14]`，含义为当日开盘集合竞价成交额，单位万元。通达信官方接口表定义 `OpenAmo` 为开盘金额（万元），见[官方接口文档](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html)。
- 历史样本按 Ulist `f124`/`f297` 与 ZHB 文件名日期对齐：139 组、20 只股票、7 个交易日，日期问题与重复值冲突均为零。f63 与 ZHB 原值精确相等 `0/139`，换算成人民币元后精确相等 `0/139`；按 ZHB `0.01 万元` 精度的半单位 `±50 元` 只命中 `2/139`。两例 11 月 18 日原始值和完整逐行结果见[专门研究记录](../../research/20261119_ulist239_f63_zhb_open_auction_candidate_review.md)。
- 同日 Chrome 页面检查时间为 2026-11-19 11:34 与 11:36（Asia/Shanghai）。两个官方页面均显示历史日期、五类净流入列及其净额；页面动态值以 Chrome 实际打开时记录为准。

[observation] {"source":"东财-ulist239(np/get)","code":"f63","stock_code":"600519","data_date":"20261118","source_file":"20261118/raw_ulist239.json","raw_value":334160976,"raw_unit":"unknown","page_url":"https://data.eastmoney.com/zjlx/600519.html","page_metric":"历史资金流向：主力净流入、超大单净流入、大单净流入、中单净流入、小单净流入","page_values":[{"label":"主力净流入","value":"-2.52","unit":"亿元"},{"label":"超大单净流入","value":"-2.08","unit":"亿元"},{"label":"大单净流入","value":"-4367.83","unit":"万元"},{"label":"中单净流入","value":"+2.52","unit":"亿元"},{"label":"小单净流入","value":"-34.27","unit":"万元"}],"accessed_at":"2026-11-19T11:34+08:00","result":"contradicted"}

[observation] {"source":"东财-ulist239(np/get)","code":"f63","stock_code":"000007","data_date":"20261118","source_file":"20261118/raw_ulist239.json","raw_value":410590,"raw_unit":"unknown","page_url":"https://data.eastmoney.com/zjlx/000007.html","page_metric":"历史资金流向：主力净流入、超大单净流入、大单净流入、中单净流入、小单净流入","page_values":[{"label":"主力净流入","value":"-1302.23","unit":"万元"},{"label":"超大单净流入","value":"-367.13","unit":"万元"},{"label":"大单净流入","value":"-935.10","unit":"万元"},{"label":"中单净流入","value":"+489.77","unit":"万元"},{"label":"小单净流入","value":"+812.47","unit":"万元"}],"accessed_at":"2026-11-19T11:36+08:00","result":"contradicted"}

`contradicted` 仅指同日页面五种净流入指标都不与 f63 原值直接相等；这些网页观察不定义 `f63`，也不建立其与任何资金流指标的跨源映射。ZHB 候选被排除的完整依据与字段状态边界见[裁决说明](../../research/20261119_ulist239_f63_zhb_open_auction_candidate_review.md)。
