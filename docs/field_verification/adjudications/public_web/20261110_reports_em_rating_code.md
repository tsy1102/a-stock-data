# Official Eastmoney rating-code observations

网页核验日期：2026-11-10（Asia/Shanghai）。采集目录日期为 2026-11-09；研报发布日期单独列示。
归档来源：`20261109/raw_reports.json`；SHA-256：`70dad23e2db4b70a8a9af41c39944da178fd3930da87763f34900220bb982b9f`。

证据边界：官网页面显示记录的东财评级名称，不直接显示 `emRatingCode`。以下结论将官网名称与归档中同一 `infoCode` 的代码字段绑定，并检查同日完整归档内代码到名称的唯一性，因此只支持类别代码的字段含义和已观测代码，不构成完整代码表或完整 API 契约。

同日归档全量配对：395 条非空 `emRatingCode`/`emRatingName`；3 个代码，均只对应一个名称：005=持有、006=增持、007=买入。

## reports::emRatingCode

- 600309：[https://data.eastmoney.com/report/600309.html](https://data.eastmoney.com/report/600309.html)，页面读取时间 2026-11-10 06:31:18 Asia/Shanghai。
  - 官网研报行的“东财评级”显示“买入”；报告发布日期 2026-10-28。
  - 标题“公司信息更新报告：Q3归母净利润超预期，新建磷酸铁锂产能加速打开成长空间”对应 infoCode=AP202610281831068169。
  - 同一条归档记录的原始字段：emRatingCode=007；emRatingName=买入。
- 600519：[https://data.eastmoney.com/report/600519.html](https://data.eastmoney.com/report/600519.html)，页面读取时间 2026-11-10 06:31:22 Asia/Shanghai。
  - 官网研报行的“东财评级”显示“买入”；报告发布日期 2026-11-08。
  - 标题“贵州茅台26Q3点评：市场化改革持续兑现”对应 infoCode=AP202611081831533384。
  - 同一条归档记录的原始字段：emRatingCode=007；emRatingName=买入。
- 601288：[https://data.eastmoney.com/report/601288.html](https://data.eastmoney.com/report/601288.html)，页面读取时间 2026-11-10 06:31:23 Asia/Shanghai。
  - 官网研报行的“东财评级”显示“增持”；报告发布日期 2026-11-01。
  - 标题“2026年三季报点评：营收利润增速回升”对应 infoCode=AP202611011831293587。
  - 同一条归档记录的原始字段：emRatingCode=006；emRatingName=增持。
[observation] {"code":"emRatingCode","data_date":"20261109","display_text":"买入","observation_type":"report_eastmoney_rating_code","page_current_rating":"买入","page_metric":"研报明细 > 东财评级","page_url":"https://data.eastmoney.com/report/600309.html","raw_value":"007","record_identity":{"infoCode":"AP202610281831068169","publishDate":"2026-10-28 00:00:00.000","title":"公司信息更新报告：Q3归母净利润超预期，新建磷酸铁锂产能加速打开成长空间"},"source":"reports","source_file":"20261109/raw_reports.json","stock_code":"600309"}
[observation] {"code":"emRatingCode","data_date":"20261109","display_text":"买入","observation_type":"report_eastmoney_rating_code","page_current_rating":"买入","page_metric":"研报明细 > 东财评级","page_url":"https://data.eastmoney.com/report/600519.html","raw_value":"007","record_identity":{"infoCode":"AP202611081831533384","publishDate":"2026-11-08 00:00:00.000","title":"贵州茅台26Q3点评：市场化改革持续兑现"},"source":"reports","source_file":"20261109/raw_reports.json","stock_code":"600519"}
[observation] {"code":"emRatingCode","data_date":"20261109","display_text":"增持","observation_type":"report_eastmoney_rating_code","page_current_rating":"增持","page_metric":"研报明细 > 东财评级","page_url":"https://data.eastmoney.com/report/601288.html","raw_value":"006","record_identity":{"infoCode":"AP202611011831293587","publishDate":"2026-11-01 00:00:00.000","title":"2026年三季报点评：营收利润增速回升"},"source":"reports","source_file":"20261109/raw_reports.json","stock_code":"601288"}
