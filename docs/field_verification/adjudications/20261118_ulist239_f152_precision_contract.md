# 东方财富 Ulist `f152` 行情缩放位数

核验日期：2026-11-18。目标身份为 `东财-ulist239(np/get)::f152`。

## 项目路径与官方格式器

项目 [`collect_ulist239`](../../../scripts/capture_http_collectors.py#L945) 请求 `api/qt/ulist.np/get`，直接保存 `data.diff` 中的响应键。东方财富行情中心官方前端脚本 [`index.js`](https://quote.eastmoney.com/center/static/build/index.js)（固定版本 UTF-8 SHA-256：`1224df21d3aa5cef8659acd9293b1f44047e0398080e6bce72fe881d755dc59b`）将：

- `涨跌幅_5分钟` 关联到 `f11` 和 `f152`，由 `f11` 提供数值、`f152` 传入格式器；
- `涨速_3分钟` 关联到 `f22` 和 `f152`，同样由 `f152` 传入格式器；
- 可转债对应正股涨跌幅关联字段列表虽包含 `f152`，格式器实际使用 `f230` 作为数值、`f152` 作为第二参数。

同一脚本的格式器在 `t > 0` 时以 `e / 10**t` 还原数值并显示 `t` 位小数；其 `getListQuoteNPList` 实际请求 `api/qt/ulist.np/get`，参数为 `fltt=1`。这说明 `f152` 在这些指标映射中是价格变动百分比/比例字段的十进制缩放位数，不是涨跌幅或涨速数值本身。项目也请求该端点，但使用 `fltt=2`。

## 留存样本和范围

2026-11-17 保留快照 [`raw_ulist239.json`](../20261117/raw_ulist239.json)（SHA-256：`d8f0cd0092412ab8f33fc0cbdccc9643e10367001c667857ec6a16ea73b033bf`）中 20/20 行含 `f152`，取值均为 `2`；同时 `f11`、`f22` 保存为已转换的小数形式。该恒定样本本身不证明含义；定义来自官方前端对 `f152` 的多处格式器调用。因为项目使用 `fltt=2`，不得再次对已转换的行情数值按 `f152` 缩放。

## 裁决

`f152` 定案为 **行情百分比/比例字段的十进制缩放位数**，单位留空。它只解释该 Ulist 路径的格式元数据角色；不创建 `mappings`，也不外推到其他接口中的同编号字段。精确的服务端 `fltt` 转换实现仍以各调用方参数为界。

## 来源

- 东方财富[行情中心官方前端脚本](https://quote.eastmoney.com/center/static/build/index.js)。
- 项目[Ulist 采集器](../../../scripts/capture_http_collectors.py#L945)与[保留样本](../20261117/raw_ulist239.json)。
