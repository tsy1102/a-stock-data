# ELTDX 日 K OHLC 字段定案

## 定案范围

定案 `TDX-eltdx(适配层)` 的四个精确路径 `open`、`high`、`low`、`close`：分别是日 K 开盘价、最高价、最低价和收盘价，单位均为元。四条原始记录此前共用“时间 / OHLC”释义且未登记单位；该描述把不同字段混在一起，也把 `time` 错并到价格字段。

本裁决只确认 ELTDX 适配层自身的字段含义，不建立任何跨源映射，也不据此确认其他数据源同名路径。项目采集调用没有显式传入复权参数；本结论不扩大到复权模式、复权因子或跨源数值等价。

## 路径与权威依据

项目调用链核实如下：

- `scripts/capture_field_probe.py::collect_eltdx` 委托 `scripts/capture_tcp_collectors.py::collect_eltdx`。
- 采集器调用 `client.bars.get(code, period="day", count=5, include_raw=True)`，将 `KlineSeries.bars` 中每条 `KlineBar` 交给 `_jfy` 序列化，保存到 `stocks.<code>.kline_day[]`。
- 项目安装并固定的 ELTDX v3.3.2 文档将 `client.bars.get()` 对应到通达信 7709 `0x052d`，把 `KlineBar.open/high/low/close` 列为开高低收；另列出的 `*_price_milli` 才是毫厘价，并说明展示价按毫厘值除以 1000 还原。
- 通达信官方公式文档分别将 `OPEN`、`HIGH`、`LOW`、`CLOSE` 定义为本周期开盘价、最高价、最低价、收盘价；官方 K 线行情字段表明确开高低收单位为元。

来源：

- [ELTDX v3.3.2：7709 K 线周期线接口](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-K%E7%BA%BF%E5%91%A8%E6%9C%9F%E7%BA%BF.md)，§作用、§解析字段、§解码口径。
- [ELTDX v3.3.2：字段手册](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md)，KlineSeries / KlineBar。
- [通达信公式系统函数列表](https://help.tdx.com.cn/gspt/docs/markdown/redword/functionlist.html)，`OPEN`、`HIGH`、`LOW`、`CLOSE`。
- [通达信量化平台获取 K 线行情](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1h10g60jt68sc.html)，开高低收字段单位。

## 保留样本核验

只读取根目录规则允许的 2026-10-15 起保留样本：

| 数据日 | 日 K 条数 | OHLC 缺项 | 高低价关系异常 |
|---|---:|---:|---:|
| 2026-10-15 | 100 | 0 | 0 |
| 2026-11-02 | 100 | 0 | 0 |
| 2026-11-06 | 100 | 0 | 0 |
| **合计** | **300** | **0** | **0** |

检查条件为 `low <= min(open, close)` 且 `max(open, close) <= high`。这一步验证采集路径确实产生日 K OHLC 结构且样本关系合理；字段语义和元单位以接口/官方文档为依据，样本检查不单独充当语义证据。

## 注册表结果

四个字段分别登记为 `日K开盘价`、`日K最高价`、`日K最低价`、`日K收盘价`，单位 `元`，状态由 `unverified` 变为 `verified`，解析为 `verified_by_source_contract`。原有合并释义及单位空缺通过显式 `metadata_correction` 留存前后快照。决定文件为 [`20261109_eltdx_kline_ohlc.json`](20261109_eltdx_kline_ohlc.json)。

未写入 `mappings`：其他来源的 OHLC 路径仍需按各自的完整来源身份和契约分别核验。
