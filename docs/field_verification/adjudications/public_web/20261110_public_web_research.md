# 2026-11-10 官方页面研究：东财 Ulist f45

## 核验对象与边界

- 精确身份：`东财-ulist239(np/get)::f45`；source_lineage 将运行来源 `ulist239` 确认为 Eastmoney，来源族为 eastmoney。
- 保留样本：`20261109/raw_ulist239.json`，`data_date=20261109`；采集运行日为 2026-11-10，来源响应时间 2026-11-09 19:58:58（Asia/Shanghai）。
- 页面于 2026-11-10 00:39–00:41（Asia/Shanghai）在用户授权的 Chrome 会话中逐页查看；该区间是本次观察窗口，不代表各页精确到秒的访问时间。
- Eastmoney 股票日历页面显示对应股票的“2026年三季报归属净利润”及亿元展示值。公开页面用于东财来源内路径语义核对；上市公司三季报用于确认金额、会计口径与报告期。

## 同日逐值观测

原字段值单位为元，页面展示单位为亿元；每条观测显式使用 `raw_to_display_factor=0.00000001`（原值 × 因子）。接受边界为显示刻度的一半。

| 股票 | 原始值 | 换算后 | 页面值 | 最小显示刻度 | 绝对差 | 半刻度上限 |
|---|---:|---:|---:|---:|---:|---:|
| 600519 | 64467425981.95 元 | 644.6742598195 亿元 | 644.7 亿元 | 0.1 亿元 | 0.0257401805 亿元 | 0.05 亿元 |
| 601288 | 236546000000.0 元 | 2365.460000000 亿元 | 2365 亿元 | 1 亿元 | 0.460000000 亿元 | 0.5 亿元 |
| 000568 | 5671059241.53 元 | 56.7105924153 亿元 | 56.71 亿元 | 0.01 亿元 | 0.0005924153 亿元 | 0.005 亿元 |

[observation] {"code":"f45","data_date":"20261109","display_increment":"0.1","display_text":"2026年三季报归属净利润644.7亿元","display_unit":"亿元","display_value":"644.7","missing_as_zero":false,"page_metric":"2026年三季报归属净利润","page_url":"https://data.eastmoney.com/stockcalendar/600519.html","raw_to_display_factor":"0.00000001","raw_value":64467425981.95,"source":"东财-ulist239(np/get)","source_file":"20261109/raw_ulist239.json","stock_code":"600519"}
[observation] {"code":"f45","data_date":"20261109","display_increment":"1","display_text":"2026年三季报归属净利润2365亿元","display_unit":"亿元","display_value":"2365","missing_as_zero":false,"page_metric":"2026年三季报归属净利润","page_url":"https://data.eastmoney.com/stockcalendar/601288.html","raw_to_display_factor":"0.00000001","raw_value":236546000000.0,"source":"东财-ulist239(np/get)","source_file":"20261109/raw_ulist239.json","stock_code":"601288"}
[observation] {"code":"f45","data_date":"20261109","display_increment":"0.01","display_text":"2026年三季报归属净利润56.71亿元","display_unit":"亿元","display_value":"56.71","missing_as_zero":false,"page_metric":"2026年三季报归属净利润","page_url":"https://data.eastmoney.com/stockcalendar/000568.html","raw_to_display_factor":"0.00000001","raw_value":5671059241.53,"source":"东财-ulist239(np/get)","source_file":"20261109/raw_ulist239.json","stock_code":"000568"}

三只股票的逐值差异均小于页面最小显示刻度的一半。Ulist f45 在保留的 2026-11-02、11-03、11-04、11-05、11-06、11-09 样本中均保持同值；这些重复采集覆盖同一个 2026Q3 报告期，只表示该已披露数据在多个采集日未变化，不按六个独立报告期计数。

同一数据日 Eastmoney Push2 `f105` 对三只股票也与 Ulist `f45` 原值一致；两者同属 Eastmoney，故仅作为同提供方内部一致性线索，不计为独立来源证据，也不据此登记映射。

## 正式财报核对与替代解释

- 贵州茅台 2026 年第三季度报告使用人民币元，列示年初至报告期末归属于上市公司股东的净利润 64,467,425,981.95 元；Ulist 原值精确相等。Q3 单季值为 19,950,545,560.09 元，排除“仅第三季度单季净利润”。[正式报告](https://static.cninfo.com.cn/finalpage/2026-10-31/1225649896.PDF)
- 农业银行 2026 年第三季度报告以人民币百万元列示，年初至报告期末归属于母公司股东的净利润为 236,546 百万元，即 236,546,000,000 元；Ulist 原值精确相等。Q3 单季值为 90,165 百万元，排除单季口径。[正式报告](https://static.cninfo.com.cn/finalpage/2026-10-31/1225649460.PDF)
- 泸州老窖 2026 年第三季度报告使用人民币元，列示年初至报告期末归属于上市公司股东的净利润 5,671,059,241.53 元；Ulist 原值精确相等。Q3 单季值为 1,331,795,155.20 元，排除单季口径。[正式报告](https://disc.static.szse.cn/download/disc/disk03/finalpage/2026-10-30/477d3881-379b-47af-ac0c-1f0197daf522.PDF)

东方财富页面观测：[贵州茅台](https://data.eastmoney.com/stockcalendar/600519.html)、[农业银行](https://data.eastmoney.com/stockcalendar/601288.html)、[泸州老窖](https://data.eastmoney.com/stockcalendar/000568.html)。三页分别显示 644.7 亿元、2365 亿元、56.71 亿元，并标记为 2026 年三季报归属净利润。

## 结论与限制

按项目官方页面精确观测流程，确认该精确来源路径在 2026-11-09 数据样本中的含义为“最新已披露定期报告中归属于上市公司股东的净利润，按年初至报告期末累计”，原始单位为元。它是稳定财报值，不是每日单季增量。此结论只覆盖该来源路径及本次可核的 2026Q3 报告值；没有据此声称观察到了多个独立报告期，也没有建立任何跨源/跨端点映射。

## 后续未决线索：Ulist f97-f99

复查 2026-11-02、11-03、11-04、11-05、11-06、11-09 的 Ulist 原始样本后，f97-f99 均存在非空、非零观测；因此 [`docs/verify/ulist_verify.md`](../../../verify/ulist_verify.md) 中早期“恒空/恒0”概述不能再当作当前样本事实。f98 与同源已知 DDX 字段 f88 的近五个交易日正值计数在既有碰撞复核中出现 40/40 相符，属于待核公式线索；f97、f99 也尚无可区分解释的公开标签。东方财富平台文章解释了 DDX/DDY/DDZ 指标，但未给 f97-f99 的接口代码映射，不能据此定案：[自选列表字段说明](https://caifuhao.eastmoney.com/news/20240729172343916411560)。这三个字段继续保持未知，后续应核对完整滚动窗口、缺失日处理和官方页面标签。
