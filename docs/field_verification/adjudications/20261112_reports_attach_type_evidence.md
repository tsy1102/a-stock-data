# `reports::attachType` 单源 E3 证据

核验日期：2026-11-12（Asia/Shanghai）。本次裁决只覆盖东方财富 `report/list` 的精确来源路径 `reports::attachType`，以及保留样本中实际观察到的代码 `0`；不定义未出现的枚举值，不建立跨来源映射。

## 来源与样本

- [`get_reports()`](../../../stock_common/sc_datasource/_financials.py) 请求东方财富研报列表并保留原始行；[`collect_reports()`](../../../scripts/capture_context_collectors.py) 将返回行写入日期归档的 `raw_reports.json`。注册表路径 `reports::attachType` 与原始键 `attachType` 完全一致。
- 按项目保留边界只读取 2026-10-15 起的 16 份研报归档：共 6,051 条观察、443 个唯一 `(stock_code, infoCode)` 研报记录。6,051 条观察的 `attachType` 均为非空数值 `0`；全量扫描只用于值域和覆盖率，不将重复记录计作独立官方核验。
- 详情页核验使用三只股票、三个不同 `infoCode`，且对应不同归档日期。每条 API 记录均以股票代码、`infoCode` 和发布日期与东方财富详情页绑定；详情页“查看 PDF 原文”链接实际打开 PDF，响应类型为 `application/pdf`。Chrome PDF 阅读器页数分别为 4、3、32 页。完整记录与链接见[样本 CSV](20261112_reports_attach_type_samples.csv)。

| 股票 / `infoCode` | 归档日 | API `attachType` | 官方详情页原文附件 | 核验结果 |
|---|---|---:|---|---|
| 贵州茅台 / `AP202611081831533384` | 2026-11-09 | 0 | PDF，4 页 | `application/pdf` |
| 泸州老窖 / `AP202503041644025016` | 2026-10-20 | 0 | PDF，3 页 | `application/pdf` |
| 农业银行 / `AP202409101639809204` | 2026-10-16 | 0 | PDF，32 页 | `application/pdf` |

## 裁决范围

- `attachType` 定为东方财富研报记录中的附件类型代码，单位不适用。保留期内可观察值只有 `0`；三个不同股票的详情页原文附件均为 PDF，因此本样本支持 `0` 对应 PDF 附件（3/3）。
- 结论不推断代码 `0` 在其他接口或其他字段中的含义；也不定义本样本未出现的 `attachType` 代码。详情页与 PDF 的核验是附件类型佐证，不是对 443 份研报逐份打开 PDF。
- 旧参考表“恒为 0”仅说明历史取值覆盖，不足以独立解释代码含义；本次通过精确记录与官方附件绑定补充语义，避免把恒值本身当作释义。
