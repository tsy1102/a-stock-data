# ELTDX 日 K 后续字段定案

## 定案范围

对 `TDX-eltdx(适配层)` 的 14 个 KlineBar 字段做来源内契约核验：`time`、四个 `*_price_milli`、`last_close_price_milli`、`volume_lots`、`volume_wire_value`、`up_count/down_count` 和四个 `*_delta_raw`。本次不建立跨源映射。

ELTDX v3.3.2 将 `client.bars.get(code, period="day")` 映射到通达信 7709 `0x052d`，返回 `KlineSeries.bars[].KlineBar`。本项目在个股数据下将该模型写入 `stocks.<code>.kline_day[]`，指数辅助行情写入 `global_helpers.market_stat_880005.bars[]`。注册表当前按 `(source, code)` 定位字段，不能区分同名叶字段的多个对象路径；因此本次只裁决 KlineBar 契约明确、在这两个容器语义一致的 14 项。

`amount`、`amount_raw`、`volume_raw` 暂不裁决：这些叶字段也出现在快照或实时排名对象，现有注册表键无法仅更新 KlineBar 路径。`amount` 的跨源数值接近度作为独立证据保留，但不能替代路径身份。

## 依据

- [ELTDX v3.3.2：7709 K 线周期线接口](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-K%E7%BA%BF%E5%91%A8%E6%9C%9F%E7%BA%BF.md)：`client.bars.get`、`0x052d`、返回类型和 KlineBar 解码口径。
- [ELTDX v3.3.2：字段手册](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md)：KlineBar 字段语义、指数宽度字段以及 A 股/指定可转债成交量单位。
- 2026-10-15、2026-11-02、2026-11-06、2026-11-09 四份保留采集：20 只股票各 5 根日 K，共 400 根；2026-11-09 同时包含 `880005` 指数辅助 KlineBar。
- 同日东财 `em_kline_f61` 对照：2026-11-02、11-06、11-09 各有 20 个同股同日行，共 60 行。OHLC 三项日期逐行完全一致；成交量差异不超过 0.5 手，符合东财整数手数舍入。
- 项目注册表将东财 `f57` 登记为成交额（元）；60 行 ELTDX K 线 `amount` 与东财 `f57` 的最大相对差为 `0.00000524%`。该结果支持“数值同尺度”的进一步调查，但因注册表无法隔离 ELTDX 的 KlineBar `amount` 路径，本次不将其提升为单位定案或映射。

## 样本核对

- `time`：400/400 均为带 `+08:00` 的上海时区 15:00 时间戳。
- 四个 `*_price_milli`：每项 400/400 满足对应展示价乘以 1000。
- `last_close_price_milli`：320 条有前一根 K 线的样本与上一根 `close_price_milli` 完全一致；80 条序列首根为空。
- `volume_lots` 与 `volume_wire_value`：400/400 普通 A 股样本满足 `volume_lots × 100 = volume_wire_value`，浮点误差小于 `1e-6`。
- `open_delta_raw`：320 条有前收盘的样本等于开盘毫厘价减上一根收盘毫厘价；80 条序列首根等于开盘毫厘价。
- `high_delta_raw`、`low_delta_raw`、`close_delta_raw`：每项 400/400 等于对应价格毫厘值减本根开盘毫厘值。
- `up_count/down_count`：400 条个股 K 线为空；2026-11-09 的 `880005` 指数辅助 K 线返回上涨 1768 家、下跌 2966 家，与固定版本“指数类解析、股票通常为空”的定义一致。

## 裁决

14 条记录标为 `verified_by_source_contract`。其中 `time`、`up_count`、`down_count` 的旧合并释义通过显式 `metadata_correction` 留存前后值；没有新增跨源映射。`amount`、`amount_raw`、`volume_raw` 保留未知状态，待注册表可表达完整对象路径后再分别处理。决定文件为 [`20261109_eltdx_kline_followup.json`](20261109_eltdx_kline_followup.json)。
