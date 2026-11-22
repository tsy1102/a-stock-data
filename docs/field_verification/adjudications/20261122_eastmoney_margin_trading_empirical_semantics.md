# 东方财富两融衍生字段：保留期实证复核

## 结论

对 `东财-datacenter(英文键)` 下 9 条 `margin_trading.*` 冲突路径重新核验后，全部达到来源内实证定案条件：每项纳入比较的样本均吻合，反例为 0。同步恢复逐源状态为 `verified`、补齐单位和公式释义；不新增跨源字段映射。

这 9 条记录原先的 `status_conflict` 来自注册表状态不一致：各字段的参考证据状态均为 `verified`，聚合兼容记录却为 `unverified`；活动 `attribute_conflicts` 均为空。此次裁决记录原状态、元数据与空冲突快照，按精确来源路径消解状态冲突。

## 来源路径与日期资格

`stock_common/sc_datasource/_financials.py::get_margin_trading` 请求东方财富 `RPTA_WEB_RZRQ_GGMX`，并将原始响应的 `DATE`、`RZYE`、`RZMRE`、`RZCHE`、`RQYE`、`RQMCL`、`RQCHL` 等键映射到采集结构；本批新增字段从同一原始响应精确映射：`RZJME`、`RQJMG`、`RZCHE5D`、`RZMRE5D`、`RZCHE10D`、`RZMRE10D`、`RCHANGE5DCP`、`RCHANGE10DCP`、`FIN_BALANCE_GR`。原始输入保存在逐行证据 CSV 的 `raw_datacenter_row_json` 列。

东方财富[融资融券交易明细页面](https://data.eastmoney.com/rzrq/detail/SH.html)列出 5 日、10 日排行，并将数据来源标为东方财富 Choice。该网页没有公开这组 JSON 键的逐键接口契约；因此精确释义由项目的原始键到运行路径映射和本次公式/行情实证共同确定，页面只作为业务范围佐证。

本次只使用保留边界 `2026-10-15` 之后的材料。21 个目录中的 `raw_datacenter.json` 形成 326 条去重后的“股票×来源日期”记录，涉及 16 只股票，原始来源日期为 `2026-10-15` 至 `2026-11-17`；目录名只用于定位文件，日期取自每条两融原始记录的 `DATE`。21 个快照中同一股票、同一来源日期有 2,321 条重复副本；全部重复副本的原始字段值一致，没有记录级漂移。16 只股票在各自留存范围内的来源日期没有工作日缺口。

行情验证使用 22 个已标记收盘且 Tencent `as_of_date` 合格的目录，共 440 个唯一“股票×来源日期”收盘报价。只接受报价时间戳在当日 15:00 之后的值；依据项目测试中记录的 Tencent 行情协议，`fields[3]` 为收盘/当前价，`fields[4]` 为前收盘。重复报价的收盘价及前收盘价没有冲突。对较早目标日没有单独收盘快照的个别样本，使用紧接的下一交易日 `fields[4]` 作为该目标日收盘价，并在 CSV 中标明目标日、观察日、时间戳及目录来源。数据日期窗口自 2026-10-15 起；上交所公告确认 2026 年国庆休市于 10 月 7 日结束、10 月 8 日恢复交易，本证据窗口没有落在该休市段内。

## 逐项公式复核

| 路径 | 定案含义 / 单位 | 比较 | 排除 | 反例 | 最大绝对差 |
|:---|:---|---:|---:|---:|---:|
| `margin_trading.rzjme` | 融资净买入额；`RZMRE - RZCHE`；元 | 326/326 | 0 | 0 | 0 元 |
| `margin_trading.rqjmg` | 融券净卖出量；`RQMCL - RQCHL`；股 | 326/326 | 0 | 0 | 0 股 |
| `margin_trading.rzche_5d` | 含来源日期当日的近 5 个交易日融资偿还额合计；元 | 262/262 | 64 | 0 | 0 元 |
| `margin_trading.rzmre_5d` | 含来源日期当日的近 5 个交易日融资买入额合计；元 | 262/262 | 64 | 0 | 0 元 |
| `margin_trading.rzche_10d` | 含来源日期当日的近 10 个交易日融资偿还额合计；元 | 182/182 | 144 | 0 | 0 元 |
| `margin_trading.rzmre_10d` | 含来源日期当日的近 10 个交易日融资买入额合计；元 | 182/182 | 144 | 0 | 0 元 |
| `margin_trading.balance_gr` | 融资余额较前一交易日的环比增长率；%；`(RZYE_T / RZYE_(T-1) - 1) × 100` | 310/310 | 16 | 0 | 0.000000000000499 个百分点 |
| `margin_trading.chg_5d` | 标的证券截至来源日期的 5 个交易间隔涨跌幅；%；`(close_T / close_(T-5) - 1) × 100` | 197/197 | 129 | 0 | 0.000050 个百分点 |
| `margin_trading.chg_10d` | 标的证券截至来源日期的 10 个交易间隔涨跌幅；%；`(close_T / close_(T-10) - 1) × 100` | 149/149 | 177 | 0 | 0.000049104 个百分点 |

金额、数量和增长率公式均以原始十进制值复算；两融余额增长率采用 `5×10⁻¹⁰` 个百分点的比较容差，最大残差低于 `5×10⁻¹³` 个百分点。`chg_5d` / `chg_10d` 以 Tencent 收盘值独立复算，容差为 `0.000051` 个百分点，覆盖原值 4 位小数的半单位舍入差；实测最大差分别为 `0.000050`、`0.000049104` 个百分点，均未超过容差。该近似只用于解释百分比字段精度，不把超过精度的反例视作舍入。

排除项都不计为命中：5 日与 10 日累计字段分别有 64、144 条记录尚无完整的前序窗口（留存起始处的历史边界）；`balance_gr` 每只股票的首条来源记录各排除 1 条；`chg_5d` 与 `chg_10d` 分别排除 80/160 条历史窗口不足及 49/17 条缺少可用当日 Tencent 收盘报价的样本。行情副本之间没有冲突。CSV 为所有 326 条唯一两融记录保存原始行、采集目录、完整公式输入日期、计算值、命中标记和报价凭据；空计算项均标注排除原因。

上述逐项 counts 是定案样本数，不要求 9 条字段拥有相同样本数。范围限于所列来源路径和公式；不推断东财未公开的内部计算实现，也不把 Tencent 行情验证转成跨源字段映射。

## 逐行证据与复现

- [逐股票、逐来源日期及公式输入的完整 CSV](../research/20261122_eastmoney_margin_trading_formula_audit.csv)
- CSV 规范 LF SHA-256：`519e98da79283fc071f2cc56d06f5f92346b1cc68e8e4940572f62dd8078499f`
- 原始字段到运行路径的映射：[stock_common/sc_datasource/_financials.py](../../../stock_common/sc_datasource/_financials.py)（`get_margin_trading`）
- Tencent 行情槽位回归：[tests/test_degradation_contract.py](../../../tests/test_degradation_contract.py)（Tencent `fields[3]` / `fields[4]`）
- 2026 年国庆休市安排：[上海证券交易所公告](https://big5.sse.com.cn/site/cht/www.sse.com.cn/disclosure/announcement/general/c/c_20260915_10832273.shtml)
