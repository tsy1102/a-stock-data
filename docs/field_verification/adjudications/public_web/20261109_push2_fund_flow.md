# Eastmoney push2 小单资金流页面观测

- 审阅者：Codex。整理日期：2026-11-09（Asia/Shanghai）。
- 被比对的原始数据日：2026-11-06；原始文件：`20261106/raw_push2.json`。
- 页面值在 2026-11-06 收盘后的 Chrome 页面中观察；页面收盘统计显示更新时间 16:05。精确的浏览器导航分钟未保存在原始研究记录中，故不把更新时间冒充访问时间。
- 2026-11-09 的官方页面静态抓取可复核页面标题和指标标签，但 JS 动态数值为空；下列显示值保留自收盘当日 Chrome 页面观察。
- 页面：`data.eastmoney.com/zjlx/600519.html`（贵州茅台）与 `data.eastmoney.com/zjlx/601288.html`（农业银行）。
- 页面可见标签：`实时成交分布图` 的 `类型 / 流入 / 流出` 行含 `小单`；实时资金面板含 `今日小单净流入`；历史表含 `小单净流入`。
- 仅核定 Eastmoney 页面指标与 Eastmoney push2 原始路径的来源内含义，不声称其为 push2 API 契约，不推断真实投资者账户类别，不作为独立来源，也不新增跨源映射。
- 原始 `-` 仍是采集哨兵；只在茅台 2026-11-06 页面明确显示小单流入为 0 时，将该条页面观测按 0 比较。

## 同日页面值与原始值

页面金额统一以元记入 `display_value`；亿/万格式按页面最末位精度换算。允许误差为显示刻度的一半。

## 历史公式复核

9 个保留日期文件，共 154 条样本；数值样本 147/147 精确符合 f149=f147-f148；f147 为 `-` 的 7/7 条均符合 f149=-f148。覆盖 20 只股票。

| 数据日 | 文件 |
| --- | --- |
| 20261020 | `20261020/raw_push2.json` |
| 20261023 | `20261023/raw_push2.json` |
| 20261026 | `20261026/raw_push2.json` |
| 20261029 | `20261029/raw_push2.json` |
| 20261102 | `20261102/raw_push2.json` |
| 20261103 | `20261103/raw_push2.json` |
| 20261104 | `20261104/raw_push2.json` |
| 20261105 | `20261105/raw_push2.json` |
| 20261106 | `20261106/raw_push2.json` |

## 逐条规范化观测记录

### 东财-push2(stock/get)::f147
[observation] {"code":"f147","data_date":"20261106","display_increment":"1","display_text":"0","display_unit":"元","display_value":"0","missing_as_zero":true,"page_metric":"实时成交分布图｜类型=小单｜流入","page_url":"https://data.eastmoney.com/zjlx/600519.html","raw_value":"-","source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"600519"}
[observation] {"code":"f147","data_date":"20261106","display_increment":"10000","display_text":"4.9623亿","display_unit":"元","display_value":"496230000","missing_as_zero":false,"page_metric":"实时成交分布图｜类型=小单｜流入","page_url":"https://data.eastmoney.com/zjlx/601288.html","raw_value":496233072.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"601288"}

### 东财-push2(stock/get)::f148
[observation] {"code":"f148","data_date":"20261106","display_increment":"1","display_text":"10.8674万","display_unit":"元","display_value":"108674","missing_as_zero":false,"page_metric":"实时成交分布图｜类型=小单｜流出","page_url":"https://data.eastmoney.com/zjlx/600519.html","raw_value":108674.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"600519"}
[observation] {"code":"f148","data_date":"20261106","display_increment":"10000","display_text":"5.0535亿","display_unit":"元","display_value":"505350000","missing_as_zero":false,"page_metric":"实时成交分布图｜类型=小单｜流出","page_url":"https://data.eastmoney.com/zjlx/601288.html","raw_value":505345584.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"601288"}

### 东财-push2(stock/get)::f149
[observation] {"code":"f149","data_date":"20261106","display_increment":"1","display_text":"-10.8674万","display_unit":"元","display_value":"-108674","missing_as_zero":false,"page_metric":"实时资金流向图｜今日小单净流入","page_url":"https://data.eastmoney.com/zjlx/600519.html","raw_value":-108674.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"600519"}
[observation] {"code":"f149","data_date":"20261106","display_increment":"1","display_text":"-911.2512万","display_unit":"元","display_value":"-9112512","missing_as_zero":false,"page_metric":"实时资金流向图｜今日小单净流入","page_url":"https://data.eastmoney.com/zjlx/601288.html","raw_value":-9112512.0,"source":"东财-push2(stock/get)","source_file":"20261106/raw_push2.json","stock_code":"601288"}
