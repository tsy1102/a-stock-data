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
