# TDX 行情快照 `amount_wan` / `change_amt` 来源内语义定案证据

核验日：2026-11-13。裁决范围仅为 `(TDX(双命名源), amount_wan)` 与 `(TDX(双命名源), change_amt)` 两个完整路径；不扩展到同名字段的其他来源或其他嵌套路径。

## 项目路径

- 探针调用 [`capture_tcp_collectors.py`](../../../scripts/capture_tcp_collectors.py) 的 `collect_tdx()`：通过 `tdx_get_quote_raw()` 取得 TDX adapter 原始字段，再由 [`capture_field_probe.py`](../../../scripts/capture_field_probe.py) 的 `_normalize_tdx_capture_quote()` 生成标准行情记录。归档时标准化结果被放在 `stocks.<代码>.quote_full` 下，因此归档位置为 `stocks.<代码>.quote_full.amount_wan` 和 `stocks.<代码>.quote_full.change_amt`；函数返回对象中的完整键路径分别是 `amount_wan` 和 `change_amt`。
- `_normalize_tdx_capture_quote()` 明确以原始 `amount / 10000` 生成 `amount_wan`；以 `price - last_close` 生成 `change_amt`。若昨收缺失，则使用 `pre_close`。这说明裁决的两个平铺路径是项目的 TDX 标准化输出字段，不是从字段拼写猜测出的名称。
- 对照样本：[TDX 原始采集](../20261112/raw_tdx.json)、[Fuyao 同日快照](../20261112/raw_fuyao.json)、[采集元数据](../20261112/meta.json)及[20 只股票逐行比较 CSV](20261113_tdx_quote_semantics_samples.csv)。

## 数据日资格

TDX 与 Fuyao 均在 2026-11-12 收盘后采集，元数据的来源采集日期都是 `2026-11-12`；Fuyao 明确提供 `as_of_date=2026-11-12`。TDX 没有单独暴露 `as_of_date`，故用同一股票的现价和涨跌额对齐日期：20 只重叠股票的 TDX `quote_full.price` 与 Fuyao `snapshot.last_price` 全部相等，TDX `quote_full.change_amt` 与 Fuyao `snapshot.price_change` 也全部相等。两字段样本因此对应同一目标交易日；这不是 20 个独立交易日样本。

## 官方网页锚点对照

同花顺官方[上证50行情表](https://q.10jqka.com.cn/zs/detail/code/1B0016/)和[白酒行业行情表](https://q.10jqka.com.cn/thshy/detail/code/881273/)在 2026-11-12 页面快照中显示“现价、涨跌、成交额”等列。页面不展示明确的数据日期，故先用上节已由 Fuyao 日期锚定的价格/涨跌额识别对应行情日，再核验单位和标签。页面值及抓取限制也记录在[黄金锚研究笔记](../research/20261112_ths_valuation_anchor_research.md)。

| 股票 | TDX 现价 / 昨收 / `change_amt` | 官方表“现价 / 涨跌” | TDX `amount_wan` | 官方表“成交额” | 单位换算结果 |
|---|---|---|---:|---:|---|
| 600519 贵州茅台 | 1410.27 / 1402.30 / 7.97 | 1410.27 / 7.97 | 453681.4592 | 45.37 亿 | `453681.4592 万元 = 45.36814592 亿元`，按页面两位小数显示为 45.37 亿 |
| 000568 泸州老窖 | 76.74 / 76.99 / -0.25 | 76.74 / -0.25 | 95331.9808 | 9.53 亿 | `95331.9808 万元 = 9.53319808 亿元`，按页面两位小数显示为 9.53 亿 |

两只股票的页面标签和精度均支持：`amount_wan` 是成交金额，输出单位万元；`change_amt` 是价格涨跌额，单位元/股，值为最新价减昨收。页面没有显示字段级 API 协议或精确来源时间；本结论限定为已核验的项目路径和 2026-11-12 样本。

## 全量留存样本交叉检查

当日 20 只重叠股票全部满足：`quote_full.amount_wan × 10000` 与 TDX 原始 `quote_raw.amount` 完全相等；`quote_full.price` 和 `quote_full.change_amt` 分别与 Fuyao 同日 `snapshot.last_price`、`snapshot.price_change` 完全相等。TDX 标准化成交额换算为 CNY 后与 Fuyao `snapshot.turnover` 的最大差为 100 元，最大相对差为 0.142 ppm；该极小差异保留为提供方间精度差异，未擅自归因于舍入。逐股票的原始值、换算值和误差见 CSV。

## 裁决范围

1. `(TDX(双命名源), amount_wan)`：成交额，原始 CNY 金额除以 10,000，输出单位万元。
2. `(TDX(双命名源), change_amt)`：最新价减昨收价的涨跌额，输出单位元/股。
3. 两条路径均为单源语义确认，不创建跨来源 `mappings`，不更改同源 `quote_full.amount_wan` / `quote_full.change_amt` 的既有状态，也不将结论扩展到其他来源的同名键。
