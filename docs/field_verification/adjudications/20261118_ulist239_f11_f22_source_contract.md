# 东方财富 Ulist `f11` / `f22` 官方字段契约核验

核验时间：2026-11-18 00:38 +08:00。目标身份分别为 `东财-ulist239(np/get)::f11` 与 `东财-ulist239(np/get)::f22`。

## 项目采集路径

[`scripts/capture_http_collectors.py`](../../../scripts/capture_http_collectors.py) 的 `collect_ulist239` 请求 `https://push2delay.eastmoney.com/api/qt/ulist.np/get`，显式请求字段集合；随后遍历响应 `data.diff`，直接把每条返回记录放入 `stocks[代码].data`。`f11`、`f22` 没有在采集器中重命名或重新计算，因此注册路径与上游响应键一致。

## 东方财富官方定义和路径对应

东方财富行情中心官方前端脚本 [`index.js`](https://quote.eastmoney.com/center/static/build/index.js) 于上述时间返回 HTTP 200。核验的 UTF-8 响应内容长度为 647,073 字符，SHA-256 为 `1224df21d3aa5cef8659acd9293b1f44047e0398080e6bce72fe881d755dc59b`，作为本次所核版本的固定标识。

该脚本中 `QuoteItem` 的字段映射为：

```text
QuoteItem.涨跌幅_5分钟 -> fid ["f11", "f152"], sort "f11"，格式后缀 "%"
QuoteItem.涨速_3分钟   -> fid ["f22", "f152"], sort "f22"，格式后缀 "%"
```

同一脚本的行情中心配置把 `AB5MinChangePercent` 的排序键设为 `f11`，表格列引用 `QuoteItem.涨跌幅_5分钟`；`ABSpeed` 的排序键设为 `f22`，表格列引用 `QuoteItem.涨速_3分钟`。脚本中的 `getListQuoteNPList` 方法实际请求 `api/qt/ulist.np/get`，并以 `fields:E(t)` 传入同一行情字段目录。由此，官方前端把精确 Ulist 响应键连接到上述字段标签，而非依据第三方 SDK 的同名字段推断。

东方财富金融终端官方[常见问题第 21 问](https://emdesk.eastmoney.com/pc_activity/Pages/VIPTrade/pages/answer.html)另外说明，行情列表默认“涨速”为 3 分钟涨速，并可选择 1 至 5 分钟设置。这与脚本中的 `涨速_3分钟` 对应。

## 留存样本核对

2026-11-17 的保留期 `raw_ulist239.json`（SHA-256：`d8f0cd0092412ab8f33fc0cbdccc9643e10367001c667857ec6a16ea73b033bf`）包含 20 只股票；20/20 行均含 `f11` 与 `f22`，`f297` 均为 `20261117`，两字段在该横截面中分别有 15、12 个非零值。样本检查只确认项目实际保存了官方脚本定义的原始键及其正常变化，不单独充当释义证据。

## 裁决范围

- `f11` 定案为 **5 分钟涨跌幅**，单位 `%`。
- `f22` 定案为 **3 分钟涨速**，单位 `%`。
- 此裁决仅确认上述两个 Ulist 精确路径的来源内字段名和已知单位；不声称已还原服务端的精确计算公式、采样边界或所有盘中刷新细节，不据此创建跨源 `mappings`。
- 历史候选 `ulist239.f11 ↔ Tencent[80]` 仍是独立的跨源问题：Ulist 侧现已释义，但 Tencent `[80]` 的正式语义和时点口径仍未核实。此前高相关/部分逐值命中不自动证明等价，因此不把该候选升级为映射。

## 来源

- 东方财富[行情中心](https://quote.eastmoney.com/center/)及其官方前端字段/接口映射：[固定版本脚本](https://quote.eastmoney.com/center/static/build/index.js)。
- 东方财富金融终端[常见问题第 21 问](https://emdesk.eastmoney.com/pc_activity/Pages/VIPTrade/pages/answer.html)。
- 项目实际映射：[Ulist 采集器](../../../scripts/capture_http_collectors.py#L945)；样本：[2026-11-17 原始 Ulist 记录](../20261117/raw_ulist239.json)。
