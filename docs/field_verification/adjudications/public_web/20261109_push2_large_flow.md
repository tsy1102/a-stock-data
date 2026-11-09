# Eastmoney push2 funds flow public-page observations

审阅日：2026-11-09（Asia/Shanghai）。三个个股页面在 2026-11-09 开盘前访问，页面的最近历史行及盘后更新时间均指向 2026-11-06；同日 raw 样本以目录日期 `20261106` 对齐。实时资金流向图显示净流入指标，实时成交分布图显示分类流入/流出。金额显示单位按“万/亿”还原为元；“亿”保留四位小数的显示步长为 10,000 元，“万”保留四位小数的步长为 1 元。

本批只审阅五条来源路径。页面标签与三只股票同日原始值逐一对照；显示舍入误差须不超过半个末位刻度。资金流订单分类是页面统计口径，不据此推断投资者账户身份或未披露的订单阈值。

## 页面
- 600519: https://data.eastmoney.com/zjlx/600519.html
- 601288: https://data.eastmoney.com/zjlx/601288.html
- 600309: https://data.eastmoney.com/zjlx/600309.html

## 东财-push2(stock/get)::f137
页面指标：实时资金流向图｜今日主力净流入
[observation] {"code":"f137","data_date":"20261106","display_increment":"10000","display_text":"-3.1889亿","display_unit":"元","display_value":"-318890000","missing_as_zero":false,"page_metric":"实时资金流向图｜今日主力净流入","page_url":"https://data.eastmoney.com/zjlx/600519.html","raw_value":-318894480.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"600519"}
[observation] {"code":"f137","data_date":"20261106","display_increment":"1","display_text":"1374.5088万","display_unit":"元","display_value":"13745088","missing_as_zero":false,"page_metric":"实时资金流向图｜今日主力净流入","page_url":"https://data.eastmoney.com/zjlx/601288.html","raw_value":13745088.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"601288"}
[observation] {"code":"f137","data_date":"20261106","display_increment":"1","display_text":"-9715.4178万","display_unit":"元","display_value":"-97154178","missing_as_zero":false,"page_metric":"实时资金流向图｜今日主力净流入","page_url":"https://data.eastmoney.com/zjlx/600309.html","raw_value":-97154178.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"600309"}

## 东财-push2(stock/get)::f138
页面指标：实时成交分布图｜类型=超大单｜流入
[observation] {"code":"f138","data_date":"20261106","display_increment":"10000","display_text":"17.0149亿","display_unit":"元","display_value":"1701490000","missing_as_zero":false,"page_metric":"实时成交分布图｜类型=超大单｜流入","page_url":"https://data.eastmoney.com/zjlx/600519.html","raw_value":1701492944.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"600519"}
[observation] {"code":"f138","data_date":"20261106","display_increment":"10000","display_text":"7.1034亿","display_unit":"元","display_value":"710340000","missing_as_zero":false,"page_metric":"实时成交分布图｜类型=超大单｜流入","page_url":"https://data.eastmoney.com/zjlx/601288.html","raw_value":710343056.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"601288"}
[observation] {"code":"f138","data_date":"20261106","display_increment":"10000","display_text":"2.0060亿","display_unit":"元","display_value":"200600000","missing_as_zero":false,"page_metric":"实时成交分布图｜类型=超大单｜流入","page_url":"https://data.eastmoney.com/zjlx/600309.html","raw_value":200596980.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"600309"}

## 东财-push2(stock/get)::f139
页面指标：实时成交分布图｜类型=超大单｜流出
[observation] {"code":"f139","data_date":"20261106","display_increment":"10000","display_text":"18.8710亿","display_unit":"元","display_value":"1887100000","missing_as_zero":false,"page_metric":"实时成交分布图｜类型=超大单｜流出","page_url":"https://data.eastmoney.com/zjlx/600519.html","raw_value":1887100528.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"600519"}
[observation] {"code":"f139","data_date":"20261106","display_increment":"10000","display_text":"7.4585亿","display_unit":"元","display_value":"745850000","missing_as_zero":false,"page_metric":"实时成交分布图｜类型=超大单｜流出","page_url":"https://data.eastmoney.com/zjlx/601288.html","raw_value":745850848.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"601288"}
[observation] {"code":"f139","data_date":"20261106","display_increment":"10000","display_text":"2.5278亿","display_unit":"元","display_value":"252780000","missing_as_zero":false,"page_metric":"实时成交分布图｜类型=超大单｜流出","page_url":"https://data.eastmoney.com/zjlx/600309.html","raw_value":252778870.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"600309"}

## 东财-push2(stock/get)::f140
页面指标：实时资金流向图｜今日超大单净流入
[observation] {"code":"f140","data_date":"20261106","display_increment":"10000","display_text":"-1.8561亿","display_unit":"元","display_value":"-185610000","missing_as_zero":false,"page_metric":"实时资金流向图｜今日超大单净流入","page_url":"https://data.eastmoney.com/zjlx/600519.html","raw_value":-185607584.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"600519"}
[observation] {"code":"f140","data_date":"20261106","display_increment":"1","display_text":"-3550.7792万","display_unit":"元","display_value":"-35507792","missing_as_zero":false,"page_metric":"实时资金流向图｜今日超大单净流入","page_url":"https://data.eastmoney.com/zjlx/601288.html","raw_value":-35507792.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"601288"}
[observation] {"code":"f140","data_date":"20261106","display_increment":"1","display_text":"-5218.1890万","display_unit":"元","display_value":"-52181890","missing_as_zero":false,"page_metric":"实时资金流向图｜今日超大单净流入","page_url":"https://data.eastmoney.com/zjlx/600309.html","raw_value":-52181890.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"600309"}

## 东财-push2(stock/get)::f141
页面指标：实时成交分布图｜类型=大单｜流入
[observation] {"code":"f141","data_date":"20261106","display_increment":"10000","display_text":"19.4546亿","display_unit":"元","display_value":"1945460000","missing_as_zero":false,"page_metric":"实时成交分布图｜类型=大单｜流入","page_url":"https://data.eastmoney.com/zjlx/600519.html","raw_value":1945464384.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"600519"}
[observation] {"code":"f141","data_date":"20261106","display_increment":"10000","display_text":"6.9612亿","display_unit":"元","display_value":"696120000","missing_as_zero":false,"page_metric":"实时成交分布图｜类型=大单｜流入","page_url":"https://data.eastmoney.com/zjlx/601288.html","raw_value":696121328.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"601288"}
[observation] {"code":"f141","data_date":"20261106","display_increment":"10000","display_text":"3.5491亿","display_unit":"元","display_value":"354910000","missing_as_zero":false,"page_metric":"实时成交分布图｜类型=大单｜流入","page_url":"https://data.eastmoney.com/zjlx/600309.html","raw_value":354909984.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"600309"}
