# Official Eastmoney previous-rating observations

网页核验日期：2026-11-10（Asia/Shanghai）。采集目录日期为 2026-11-09；研报发布日期单独列示。
归档来源：`20261109/raw_reports.json`；SHA-256：`70dad23e2db4b70a8a9af41c39944da178fd3930da87763f34900220bb982b9f`。

本次只核对官网明确标为“维持”的行。官网“东财评级”与原始 `emRatingName`、`lastEmRatingName` 相同，且归档 `ratingChange=3`。该证据不覆盖评级发生变化的记录，也不说明完整接口契约。

## reports::lastEmRatingName

- 600309：[https://data.eastmoney.com/report/600309.html](https://data.eastmoney.com/report/600309.html)，页面读取时间 2026-11-10 06:31:18 Asia/Shanghai。
  - 官网研报行显示东财评级“买入”、评级变动“维持”；记录日期 2026-10-28。
  - 标题“公司信息更新报告：Q3归母净利润超预期，新建磷酸铁锂产能加速打开成长空间”对应 infoCode=AP202610281831068169。
  - 同一 infoCode、标题和发布日期在归档中的精确记录：emRatingName=买入；lastEmRatingName=买入；ratingChange=3。
- 600519：[https://data.eastmoney.com/report/600519.html](https://data.eastmoney.com/report/600519.html)，页面读取时间 2026-11-10 06:31:22 Asia/Shanghai。
  - 官网研报行显示东财评级“买入”、评级变动“维持”；记录日期 2026-11-08。
  - 标题“贵州茅台26Q3点评：市场化改革持续兑现”对应 infoCode=AP202611081831533384。
  - 同一 infoCode、标题和发布日期在归档中的精确记录：emRatingName=买入；lastEmRatingName=买入；ratingChange=3。
- 601288：[https://data.eastmoney.com/report/601288.html](https://data.eastmoney.com/report/601288.html)，页面读取时间 2026-11-10 06:31:23 Asia/Shanghai。
  - 官网研报行显示东财评级“增持”、评级变动“维持”；记录日期 2026-11-01。
  - 标题“2026年三季报点评：营收利润增速回升”对应 infoCode=AP202611011831293587。
  - 同一 infoCode、标题和发布日期在归档中的精确记录：emRatingName=增持；lastEmRatingName=增持；ratingChange=3。
[observation] {"code":"lastEmRatingName","data_date":"20261109","display_text":"买入 / 维持","observation_type":"report_previous_rating_name","page_current_rating":"买入","page_metric":"研报明细 > 东财评级 / 评级变动","page_rating_change":"维持","page_url":"https://data.eastmoney.com/report/600309.html","raw_value":"买入","record_identity":{"infoCode":"AP202610281831068169","publishDate":"2026-10-28 00:00:00.000","title":"公司信息更新报告：Q3归母净利润超预期，新建磷酸铁锂产能加速打开成长空间"},"source":"reports","source_file":"20261109/raw_reports.json","stock_code":"600309"}
[observation] {"code":"lastEmRatingName","data_date":"20261109","display_text":"买入 / 维持","observation_type":"report_previous_rating_name","page_current_rating":"买入","page_metric":"研报明细 > 东财评级 / 评级变动","page_rating_change":"维持","page_url":"https://data.eastmoney.com/report/600519.html","raw_value":"买入","record_identity":{"infoCode":"AP202611081831533384","publishDate":"2026-11-08 00:00:00.000","title":"贵州茅台26Q3点评：市场化改革持续兑现"},"source":"reports","source_file":"20261109/raw_reports.json","stock_code":"600519"}
[observation] {"code":"lastEmRatingName","data_date":"20261109","display_text":"增持 / 维持","observation_type":"report_previous_rating_name","page_current_rating":"增持","page_metric":"研报明细 > 东财评级 / 评级变动","page_rating_change":"维持","page_url":"https://data.eastmoney.com/report/601288.html","raw_value":"增持","record_identity":{"infoCode":"AP202611011831293587","publishDate":"2026-11-01 00:00:00.000","title":"2026年三季报点评：营收利润增速回升"},"source":"reports","source_file":"20261109/raw_reports.json","stock_code":"601288"}
