# Eastmoney source-rating code observations

网页核验日期：2026-11-10（Asia/Shanghai）

## Evidence boundary

以下官网详情页正文给出机构原始评级文字，不显示 sRatingCode 数字本身。每条记录使用详情页 URL 中的 infoCode，并以标题、发布日期和原始采集行作唯一绑定。
600519 与 601288 是精确文字匹配；600309 的“买入”对原始“买入(Buy)”是近似匹配，单独标记，不计入精确匹配数。
同日完整归档有 398 组非空代码/名称，10 个代码与 12 种名称；机构+代码组合内名称唯一，但三个观测代码跨机构均存在多种名称。结论仅限字段角色，不给出跨机构码表。

## Official record pages

- 600519，页面访问时间：2026-11-10 06:31:22 Asia/Shanghai。
  URL：https://data.eastmoney.com/report/info/AP202611081831533384.html
  页面标识：infoCode=AP202611081831533384；标题：贵州茅台26Q3点评：市场化改革持续兑现；发布日期：2026-11-08 00:00:00.000。
  页面原文：维持“买入”评级；匹配类型：exact。
[observation] {"code":"sRatingCode","data_date":"20261109","display_text":"维持“买入”评级","match_type":"exact","observation_type":"report_source_rating_code","page_metric":"研报正文 > 投资建议/评级原文","page_source_rating":"买入","page_url":"https://data.eastmoney.com/report/info/AP202611081831533384.html","raw_organization":"华安证券","raw_value":"0101","record_identity":{"infoCode":"AP202611081831533384","publishDate":"2026-11-08 00:00:00.000","title":"贵州茅台26Q3点评：市场化改革持续兑现"},"source":"reports","source_file":"20261109/raw_reports.json","stock_code":"600519"}

- 601288，页面访问时间：2026-11-10 06:31:23 Asia/Shanghai。
  URL：https://data.eastmoney.com/report/info/AP202611011831293587.html
  页面标识：infoCode=AP202611011831293587；标题：2026年三季报点评：营收利润增速回升；发布日期：2026-11-01 00:00:00.000。
  页面原文：维持‘优于大市’评级；匹配类型：exact。
[observation] {"code":"sRatingCode","data_date":"20261109","display_text":"维持‘优于大市’评级","match_type":"exact","observation_type":"report_source_rating_code","page_metric":"研报正文 > 投资建议/评级原文","page_source_rating":"优于大市","page_url":"https://data.eastmoney.com/report/info/AP202611011831293587.html","raw_organization":"国信证券","raw_value":"0301","record_identity":{"infoCode":"AP202611011831293587","publishDate":"2026-11-01 00:00:00.000","title":"2026年三季报点评：营收利润增速回升"},"source":"reports","source_file":"20261109/raw_reports.json","stock_code":"601288"}

- 600309，页面访问时间：2026-11-10 06:31:18 Asia/Shanghai。
  URL：https://data.eastmoney.com/report/info/AP202610281831068169.html
  页面标识：infoCode=AP202610281831068169；标题：公司信息更新报告：Q3归母净利润超预期，新建磷酸铁锂产能加速打开成长空间；发布日期：2026-10-28 00:00:00.000。
  页面原文：维持‘买入’评级；匹配类型：approximate。
[observation] {"code":"sRatingCode","data_date":"20261109","display_text":"维持‘买入’评级","match_type":"approximate","observation_type":"report_source_rating_code","page_metric":"研报正文 > 投资建议/评级原文","page_source_rating":"买入","page_url":"https://data.eastmoney.com/report/info/AP202610281831068169.html","raw_organization":"开源证券","raw_value":"0201","record_identity":{"infoCode":"AP202610281831068169","publishDate":"2026-10-28 00:00:00.000","title":"公司信息更新报告：Q3归母净利润超预期，新建磷酸铁锂产能加速打开成长空间"},"source":"reports","source_file":"20261109/raw_reports.json","stock_code":"600309"}
