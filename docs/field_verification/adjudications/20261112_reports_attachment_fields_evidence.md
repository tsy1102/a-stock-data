# `reports::attachSize` / `reports::attachPages` 单源 E3 证据

核验日期：2026-11-12（Asia/Shanghai）。本次只裁决精确路径 `reports::attachSize` 和 `reports::attachPages`；不裁决相邻 `reports::attachType` 的枚举值。

## 来源路径与保留样本

- [`get_reports()`](../../../stock_common/sc_datasource/_financials.py) 请求东方财富研报列表接口并保留原始响应字段；[`collect_reports()`](../../../scripts/capture_context_collectors.py) 将结果保存为 `raw_reports.json`。注册表完整路径与原始键逐字一致。
- 按项目保留规则扫描 2026-10-15 起的全部研报归档：16 个 `raw_reports.json` 文件、6,051 条记录，按 `(stock_code, infoCode)` 去重后 443 条唯一研报记录。两字段在全部 6,051 条观察及 443 条唯一记录中都非空且为正整数；`attachPages` 观测范围为 2–62 页，`attachSize` 为 161–14,204 KiB。`attachType` 在这批样本中恒为 `0`，不能由单一观察值推出代码表。
- 全集扫描只用于覆盖、缺失和异常值核查。PDF 直接测量仅针对下表三个不同股票、不同报告日期的样本；这不是 443 份 PDF 的逐份核验。

## 东方财富详情页与 PDF 实测

2026-11-12 约 21:28–21:30（Asia/Shanghai）在 Chrome 打开下列东方财富官方研报详情页，点击“查看 PDF 原文”。PDF 阅读器显示总页数；对详情页链接的 `pdf.dfcfw.com` 文件各发出一次 HEAD 请求读取 `Content-Length`。每份记录均通过 `infoCode`、股票及发布日期与保留的 `raw_reports.json` 精确绑定。逐样本数据和完整链接见 [样本 CSV](20261112_reports_attachment_fields_samples.csv)。

| 股票 / `infoCode` | 原始 `attachSize` (KiB) | PDF `Content-Length` | `floor(字节数 / 1024)` (KiB) | 原始 `attachPages` | 阅读器页数 | 核对 |
|---|---:|---:|---:|---:|---:|---|
| 贵州茅台 / `AP202611081831533384` | 305 | 312,813 B | 305 | 4 | 4 | 大小、页数吻合 |
| 泸州老窖 / `AP202503041644025016` | 540 | 553,087 B | 540 | 3 | 3 | 大小、页数吻合 |
| 农业银行 / `AP202409101639809204` | 1,311 | 1,342,748 B | 1,311 | 32 | 32 | 大小、页数吻合 |

对应东方财富详情页：[贵州茅台](https://data.eastmoney.com/report/info/AP202611081831533384.html)、[泸州老窖](https://data.eastmoney.com/report/info/AP202503041644025016.html)、[农业银行](https://data.eastmoney.com/report/info/AP202409101639809204.html)。详情页的“查看 PDF 原文”实际打开了 CSV 中记录的 PDF 链接；HEAD 响应均为 HTTP 200，`Content-Type: application/pdf`。三个 PDF 的阅读器总页数分别为 4、3、32。

## 裁决范围

- `attachPages` 定为东方财富研报记录所链接 PDF 附件的页数，单位“页”。本次三个官方 PDF 样本均与原始字段逐值吻合（3/3）；保留全集另确认该字段覆盖完整且均为正整数。
- `attachSize` 定为东方财富研报记录所链接 PDF 附件的大小，单位 KiB（1 KiB = 1,024 B）；三个官方 PDF 样本的原始整数值均等于 `floor(Content-Length / 1024)`（3/3）。结论限定为所测东方财富当前 PDF 链接的服务端长度口径，不推断券商最初发布文件的大小，也不保证重新托管后数值不变。
- 逐源参考材料中的组合别名（如 `attachSize / attachPages`）造成了注册表属性冲突；路径级参考记录和 PDF 实测能区分页数与大小。本次按证据更正这两个精确路径的元数据，并在 E3 裁决记录中保留完整旧冲突快照。
- 本证据不解释 `attachType=0` 的枚举含义，不建立跨源映射，也不声称对全集 443 个 PDF 均逐个打开、下载或核验。
