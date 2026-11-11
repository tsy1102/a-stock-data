# Eastmoney 个股研报列表：author / researcher 字段核验

核验时间：2026-11-10 06:31（Asia/Shanghai）。通过 Chrome 实际查看三只股票的东方财富个股研报页。
原始证据：`20261109/raw_reports.json`；SHA-256：`70dad23e2db4b70a8a9af41c39944da178fd3930da87763f34900220bb982b9f`。采集目录日与报告发布日期分开记录。

## 页面上看到的记录

- 600519：[https://data.eastmoney.com/report/600519.html](https://data.eastmoney.com/report/600519.html)，页面读取时间 2026-11-10 06:31:22 Asia/Shanghai。
  - “研报明细 > 作者”显示：邓欣、郑少轩；记录日期 2026-11-08。
  - 标题链接含 `infoCode=AP202611081831533384`；作者链接的 `authorid` 依次为：11000276538, 11000474034。
  - 同一 `infoCode`、标题和发布日期在归档中的精确记录：author=["11000276538.邓欣", "11000474034.郑少轩"]；researcher=邓欣,郑少轩。
- 601288：[https://data.eastmoney.com/report/601288.html](https://data.eastmoney.com/report/601288.html)，页面读取时间 2026-11-10 06:31:23 Asia/Shanghai。
  - “研报明细 > 作者”显示：陈俊良、王剑；记录日期 2026-11-01。
  - 标题链接含 `infoCode=AP202611011831293587`；作者链接的 `authorid` 依次为：11000257641, 11000209220。
  - 同一 `infoCode`、标题和发布日期在归档中的精确记录：author=["11000257641.陈俊良", "11000209220.王剑"]；researcher=陈俊良,王剑。
- 600309：[https://data.eastmoney.com/report/600309.html](https://data.eastmoney.com/report/600309.html)，页面读取时间 2026-11-10 06:31:18 Asia/Shanghai。
  - “研报明细 > 作者”显示：金益腾、张晓锋、李思佳；记录日期 2026-10-28。
  - 标题链接含 `infoCode=AP202610281831068169`；作者链接的 `authorid` 依次为：11000267432, 11000338335, 11000444537。
  - 同一 `infoCode`、标题和发布日期在归档中的精确记录：author=["11000267432.金益腾", "11000338335.张晓锋", "11000444537.李思佳"]；researcher=金益腾,张晓锋,李思佳。

## reports::author

[observation] {"code":"author","data_date":"20261109","display_text":"邓欣 郑少轩","observation_type":"report_author_list","page_authors":[{"author_id":"11000276538","name":"邓欣"},{"author_id":"11000474034","name":"郑少轩"}],"page_metric":"研报明细 > 作者","page_url":"https://data.eastmoney.com/report/600519.html","raw_value":["11000276538.邓欣","11000474034.郑少轩"],"record_identity":{"infoCode":"AP202611081831533384","publishDate":"2026-11-08 00:00:00.000","title":"贵州茅台26Q3点评：市场化改革持续兑现"},"source":"reports","source_file":"20261109/raw_reports.json","stock_code":"600519"}
[observation] {"code":"author","data_date":"20261109","display_text":"陈俊良 王剑","observation_type":"report_author_list","page_authors":[{"author_id":"11000257641","name":"陈俊良"},{"author_id":"11000209220","name":"王剑"}],"page_metric":"研报明细 > 作者","page_url":"https://data.eastmoney.com/report/601288.html","raw_value":["11000257641.陈俊良","11000209220.王剑"],"record_identity":{"infoCode":"AP202611011831293587","publishDate":"2026-11-01 00:00:00.000","title":"2026年三季报点评：营收利润增速回升"},"source":"reports","source_file":"20261109/raw_reports.json","stock_code":"601288"}
[observation] {"code":"author","data_date":"20261109","display_text":"金益腾 张晓锋 李思佳","observation_type":"report_author_list","page_authors":[{"author_id":"11000267432","name":"金益腾"},{"author_id":"11000338335","name":"张晓锋"},{"author_id":"11000444537","name":"李思佳"}],"page_metric":"研报明细 > 作者","page_url":"https://data.eastmoney.com/report/600309.html","raw_value":["11000267432.金益腾","11000338335.张晓锋","11000444537.李思佳"],"record_identity":{"infoCode":"AP202610281831068169","publishDate":"2026-10-28 00:00:00.000","title":"公司信息更新报告：Q3归母净利润超预期，新建磷酸铁锂产能加速打开成长空间"},"source":"reports","source_file":"20261109/raw_reports.json","stock_code":"600309"}

## reports::researcher

[observation] {"code":"researcher","data_date":"20261109","display_text":"邓欣 郑少轩","observation_type":"report_author_list","page_authors":[{"author_id":"11000276538","name":"邓欣"},{"author_id":"11000474034","name":"郑少轩"}],"page_metric":"研报明细 > 作者","page_url":"https://data.eastmoney.com/report/600519.html","raw_value":"邓欣,郑少轩","record_identity":{"infoCode":"AP202611081831533384","publishDate":"2026-11-08 00:00:00.000","title":"贵州茅台26Q3点评：市场化改革持续兑现"},"source":"reports","source_file":"20261109/raw_reports.json","stock_code":"600519"}
[observation] {"code":"researcher","data_date":"20261109","display_text":"陈俊良 王剑","observation_type":"report_author_list","page_authors":[{"author_id":"11000257641","name":"陈俊良"},{"author_id":"11000209220","name":"王剑"}],"page_metric":"研报明细 > 作者","page_url":"https://data.eastmoney.com/report/601288.html","raw_value":"陈俊良,王剑","record_identity":{"infoCode":"AP202611011831293587","publishDate":"2026-11-01 00:00:00.000","title":"2026年三季报点评：营收利润增速回升"},"source":"reports","source_file":"20261109/raw_reports.json","stock_code":"601288"}
[observation] {"code":"researcher","data_date":"20261109","display_text":"金益腾 张晓锋 李思佳","observation_type":"report_author_list","page_authors":[{"author_id":"11000267432","name":"金益腾"},{"author_id":"11000338335","name":"张晓锋"},{"author_id":"11000444537","name":"李思佳"}],"page_metric":"研报明细 > 作者","page_url":"https://data.eastmoney.com/report/600309.html","raw_value":"金益腾,张晓锋,李思佳","record_identity":{"infoCode":"AP202610281831068169","publishDate":"2026-10-28 00:00:00.000","title":"公司信息更新报告：Q3归母净利润超预期，新建磷酸铁锂产能加速打开成长空间"},"source":"reports","source_file":"20261109/raw_reports.json","stock_code":"600309"}
