# TDX 大写 `Date` 的接口路径范围核查

核查日期：2026-11-19
目标身份：`TDX(双命名源)::Date`

## 结论

该键显然承载日期值，但当前注册路径只到 `Date`，没有接口名或上级对象，不能据此断定它是股本记录日、市场统计日还是日线资金统计日。通达信官方文档在多个不同接口的响应中复用相同键名 `Date`，且每个接口对应不同数据域。`get_gb_info_by_date` 的 `Date` 是股本记录日期，只能作为本字段的一个候选解释；不能因它与 `Zgb`、`Ltgb` 同页出现，就把定义套到未绑定接口的注册项。

因此本次不把 `TDX(双命名源)::Date` 留作“无意义残留”，也不写入“股本日期”等猜测性释义；现有待核状态正确。定案所缺的是接口级来源路径，而不是日期格式识别或更多自然日样本。

## 官方接口对照

| 官方接口 | `Date` 的字段契约及样例 | 数据域 |
|---|---|---|
| [`get_gb_info_by_date`](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1hc4303vsv1fk.html) | 输出 `Date`（double，日期）；样例 `20260105` 等，并与 `Zgb`、`Ltgb` 同行返回 | 个股股本记录日 |
| [`get_scjy_value`](https://help.tdx.com.cn/quant/docs/markdown/TdxQuant.md/mindoc-1h10p8op6ia9g.html) | 市场统计序列按 `Date` 与 `Value` 组成记录；官方样例日期为 `20250102` | 市场级指标数据日 |
| [`get_bkjy_value`](https://help.tdx.com.cn/quant/docs/markdown/TdxQuant.md/mindoc-1h10p0ncmp5mc.html) | 板块统计序列同样按 `Date` 与 `Value` 返回 | 板块级指标数据日 |
| [`get_exday_data`](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1hh9gktmqsv5c.html) | 输出 `Date`（str，日期），与成交笔数、资金统计等字段同行返回 | 个股日线资金统计日 |

这些官方定义共同确认 `Date` 是数据记录日期，而不是采集运行日期；但接口之间的记录对象不同，足以说明裸路径 `Date` 不能唯一确定业务日期类型。官方样例仅用于对照接口契约，不视为本项目采集样本。

## 项目路径与样本核查

- 在当前仓库生产代码、测试和采集脚本中检索不到 `get_gb_info_by_date`、`get_scjy_value`、`get_bkjy_value` 或 `get_exday_data` 的调用点；现有代码没有建立 `TDX(双命名源)::Date` 到其中任一接口的映射。
- 按 `scripts/capture_retention.py` 的现行保留边界检查了保留期内 `raw_tdx*.json`：66 个文件中没有大写键 `"Date"`。它们不能用于当前逐值核验。
- `TDX::HqDate`、`TDX::updated_date`、`TDX::ipo_date` 和小写 `TDX::date` 各有各自的官方契约/路径；不得移植这些字段的含义到大写 `Date`。
- 注册表中 `TDX(双命名源)::Date` 与 `开盘啦(kpl)::Date` 是两个独立身份。相同拼写不代表同源，也不支持跨源映射。

## 后续可定案条件

只有在项目采集结果或权威来源记录能保存接口/父对象路径时，才按对应接口契约定案。例如，若真实完整路径为 `get_gb_info_by_date[].Date`，可定为股本记录日期；若为 `get_scjy_value.SCxx[].Date`，则是市场统计数据日。不能只凭字段名、YYYYMMDD 格式、相邻样本行或其他来源同名字段选定其中之一。
