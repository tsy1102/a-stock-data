# 2026-11-17 KPL `col_16` 与东财官方页面抽核

## 核验对象与范围

- 待研究路径：`开盘啦(kpl_limit_up_detail)::raw_columns.col_16`。此完整路径当前未登记在 `field_registry.json`，本记录不作为定案输入。
- 已验证参照：`东财-push2ex::broken_count`，注册表含义为“东财涨停股池个股当日炸板次数”，页面列名为“炸板次数”。
- 官方页面：<https://quote.eastmoney.com/ztb/detail>，页面日期选择为 `2026-11-16`。使用 Chrome 于北京时间 `2026-11-17 02:13` 读取；页面显示“涨停股池”表格及“炸板次数”列。
- 本地数据：`docs/field_verification/20261116/raw_kpl.json` 和 `docs/field_verification/20261116/raw_push2ex.json`。KPL raw 的 `trade_date` 为 `2026-11-16`；Push2EX 采集请求目标日为 `2026-11-16`，响应没有独立日期回显。

## 页面与归档逐值对照

| 股票代码 | KPL `col_16` | Push2EX `broken_count` | 东财页面“炸板次数” | 关系 |
|---|---:|---:|---:|---|
| 000819 | 1 | 10 | 10 次 | `col_16=1` 与次数大于零一致 |
| 002148 | 1 | 7 | 7 次 | `col_16=1` 与次数大于零一致 |
| 002419 | 1 | 2 | 2 次 | `col_16=1` 与次数大于零一致 |
| 002356 | 1 | 3 | 3 次 | `col_16=1` 与次数大于零一致 |
| 002905 | 0 | 0 | 0 次 | `col_16=0` 与次数为零一致 |
| 002548 | 0 | 0 | 0 次 | `col_16=0` 与次数为零一致 |

下列规范化 `[observation]` 行只记录东财官方页面和东财 raw 的字段观测；KPL 对照值见上表。它们不是 KPL 页面观测，也不单独证明 KPL 字段定义。

[observation] {"code":"broken_count","data_date":"20261116","display_increment":"1","display_text":"10 次","display_unit":"次","display_value":"10","missing_as_zero":false,"page_metric":"涨停股池 > 炸板次数","page_url":"https://quote.eastmoney.com/ztb/detail","raw_collection":"limit_up_pool","raw_value":10.0,"source":"东财-push2ex","source_file":"20261116/raw_push2ex.json","stock_code":"000819"}
[observation] {"code":"broken_count","data_date":"20261116","display_increment":"1","display_text":"7 次","display_unit":"次","display_value":"7","missing_as_zero":false,"page_metric":"涨停股池 > 炸板次数","page_url":"https://quote.eastmoney.com/ztb/detail","raw_collection":"limit_up_pool","raw_value":7.0,"source":"东财-push2ex","source_file":"20261116/raw_push2ex.json","stock_code":"002148"}
[observation] {"code":"broken_count","data_date":"20261116","display_increment":"1","display_text":"2 次","display_unit":"次","display_value":"2","missing_as_zero":false,"page_metric":"涨停股池 > 炸板次数","page_url":"https://quote.eastmoney.com/ztb/detail","raw_collection":"limit_up_pool","raw_value":2.0,"source":"东财-push2ex","source_file":"20261116/raw_push2ex.json","stock_code":"002419"}
[observation] {"code":"broken_count","data_date":"20261116","display_increment":"1","display_text":"3 次","display_unit":"次","display_value":"3","missing_as_zero":false,"page_metric":"涨停股池 > 炸板次数","page_url":"https://quote.eastmoney.com/ztb/detail","raw_collection":"limit_up_pool","raw_value":3.0,"source":"东财-push2ex","source_file":"20261116/raw_push2ex.json","stock_code":"002356"}
[observation] {"code":"broken_count","data_date":"20261116","display_increment":"1","display_text":"0 次","display_unit":"次","display_value":"0","missing_as_zero":false,"page_metric":"涨停股池 > 炸板次数","page_url":"https://quote.eastmoney.com/ztb/detail","raw_collection":"limit_up_pool","raw_value":0.0,"source":"东财-push2ex","source_file":"20261116/raw_push2ex.json","stock_code":"002905"}
[observation] {"code":"broken_count","data_date":"20261116","display_increment":"1","display_text":"0 次","display_unit":"次","display_value":"0","missing_as_zero":false,"page_metric":"涨停股池 > 炸板次数","page_url":"https://quote.eastmoney.com/ztb/detail","raw_collection":"limit_up_pool","raw_value":0.0,"source":"东财-push2ex","source_file":"20261116/raw_push2ex.json","stock_code":"002548"}

## 结论边界

东财官方页面在 6 个同日样本中逐值支持 `broken_count` 及其“炸板次数”标签；同时 KPL 的 `col_16` 在这 6 例中与次数是否大于零一致。结合日内完整本地对照（4 个合格来源交易日、216 组配对、`col_16 == (broken_count > 0)` 为 216/216），可以把“二值炸板状态指示”作为 KPL `col_16` 的高置信候选解释。

该证据没有显示 KPL 官方对第 16 列的标签，也没有直接绑定 KPL 产品页面中的字段。准确业务语义仍属推断；本文件不改注册表、不创建跨源映射。KPL 官方主页为产品介绍页，第三方接口说明只描述 `DailyLimitPerformance` / `PidType`，均未定义该列。
