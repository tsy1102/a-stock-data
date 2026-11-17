# 东方财富 `stock/get` `f126` 来源内释义核验

## 裁决

定案精确路径 `东财-push2(stock/get)::f126`：**股息率（%）**。东方财富官方分红融资页将该指标定义为按调整后最近四个季度分红总额相对最近一个交易日总市值计算的股息率。

此结论只覆盖 `stock/get` 的 `data.f126`。不建立与 Tencent `[64]`、Ulist239 `f133` 或 ZHB 字段的跨源映射，也不把其他接口里同名、同号字段视为同一字段。

## 端点与路径

项目 [`capture_http_collectors.py`](../../../scripts/capture_http_collectors.py) 的 `collect_push2` 调用东方财富官方 `/api/qt/stock/get`，并把响应 `data` 对象原样保存在 `raw_push2.json` 的 `stocks[code].data` 下。因此 `stocks[600519].data.f126` 是待核的完整来源路径，而不是根据其他字段名推断出来的编号。

本次在 **2026-11-17 08:24:40 +08:00** 通过 Chrome 直接读取东方财富官网接口、行情页和 F10 分红融资页。页面/接口日期均为 2026-11-16：

| 股票 | 官方接口值 `data.f126` | F10 标签与值 | 同日新采 ZHB `full.dividend_yield` |
|---|---:|---:|---:|
| 贵州茅台 600519 | 1.93 | 股息率 1.93% | 1.93 |
| 农业银行 601288 | 3.42 | 股息率 3.42% | 3.42 |

逐项值和可复核链接见 [`20261117_push2_f126_dividend_yield_samples.csv`](../research/20261117_push2_f126_dividend_yield_samples.csv)。官方页面：

- 贵州茅台行情页：<https://quote.eastmoney.com/sh600519.html>
- 贵州茅台 `stock/get`：<https://push2delay.eastmoney.com/api/qt/stock/get?secid=1.600519&fltt=2&invt=2&fields=f12%2Cf14%2Cf43%2Cf47%2Cf48%2Cf49%2Cf58%2Cf126%2Cf162%2Cf168>
- 贵州茅台 F10 分红融资：<https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code=SH600519&color=b#/fhrz>
- 农业银行行情页：<https://quote.eastmoney.com/sh601288.html>
- 农业银行 `stock/get`：<https://push2delay.eastmoney.com/api/qt/stock/get?secid=1.601288&fltt=2&invt=2&fields=f12%2Cf14%2Cf43%2Cf47%2Cf48%2Cf49%2Cf58%2Cf126%2Cf162%2Cf168>
- 农业银行 F10 分红融资：<https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code=SH601288&color=b#/fhrz>

两个 F10 页面显示相同的 2026-11-16 更新日和股息率值，并给出股息率计算口径。接口返回值与官方标签及值逐只精确一致；同日新 ZHB 值是附加旁证，不是这项来源内裁决的唯一依据。样本比较为 2/2 命中、0 个官网接口/F10 反例。

## 本轮采集边界

2026-11-17 08:14 的采集运行自然日为 2026-11-17，目标交易数据日为 2026-11-16。ZHB 本轮成功返回 20 只股票，`as_of_date=20261116`；归档 `zhb_20261116.zip` 与 raw 文件名一致。

Eastmoney Push2 本轮 20/20 请求在发出前被既有 `ip_banned` 熔断器拦截（`attempts=0`）。`meta.json` 明确记录 `previous_probe_snapshot_preserved=true`、旧快照采集时间为 2026-11-16 21:25:38、`as_of_date=null`。因此 `raw_push2.json` 不是本轮的新 Push2 采集，不能当作正式来源日样本。

作为诊断而非裁决样本，保留的 Push2 快照有 10 个数值型 `f126`，其中 9 个与本轮来源日已确认的 ZHB `full.dividend_yield` 相等，万华化学一条为 1.80 对 2.96；另有 3 个 `-` 占位值。由于旧 Push2 快照来源日期为空，这些比较不计入本次 2/2 官方页面样本，也不用于证实或否定跨源映射。最新碰撞报告中的 Tencent `[64]`、ZHB 股息率关系仍是探索关系，不是已登记映射。

## 适用边界

`f126` 的来源内语义和 `%` 单位已由精确的采集路径、东方财富官方 F10 标签/公式、两个同日官方接口值及同日新采 ZHB 旁证闭环。此结论不声称官网已公开 `f126` 的编号字段字典，也不推定其他端点的 `f126` 或其他来源的股息率字段与其等价。
