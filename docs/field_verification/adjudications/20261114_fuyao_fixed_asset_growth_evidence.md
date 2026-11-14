# Fuyao 固定资产投资扩张率完整路径与实证（2026-11-14）

## 结论

将 **同花顺-fuyao::growth.fixed_asset_invest_expansion_ratio** 按 E3 来源内实证定为“固定资产账面价值同比变动率，按百分数值返回”。2026H1 的 20 家发行人中，全部与合并资产负债表“固定资产”同向且量级接近；15/20 按同期间金额复算与原值之差不超过 **0.0000005** 个百分点。另 5 项存在未解释残差，最大 **0.2538839372** 个百分点。残差原因和上游精确公式、基期修订策略未获接口契约确认，因此不声称逐值相等，也不把误差归因于舍入。

这是基于正式报告对来源字段业务含义的实证定案，不是 Fuyao 官方字段契约定案，也不建立跨源映射。

## 字段身份与映射

- [Fuyao 财务指标接口文档](https://fuyao.aicubes.cn/docs/api-reference/financial-indicators/) 说明响应以 ability 分组，列举了 growth 指标 ID，并规定百分数值的解释；当前表中没有 fixed_asset_invest_expansion_ratio，所以不能把精确 ID 说成文档明确定义的官方字段。
- [项目解析器](../../../stock_common/sc_fuyao.py#L452) 依据响应的 ability 与 index_id 生成嵌套对象；[采集器](../../../scripts/capture_verified_collectors.py#L580) 将其放入每只股票的 fin_indicators。因此原始记录路径为 fin_indicators.growth.fixed_asset_invest_expansion_ratio，注册表按既有约定省略包装层，记录为 growth.fixed_asset_invest_expansion_ratio。
- 公开的[第三方财务指标整理](https://v6.bigquant.com/data/datasources/cn_stock_financial_growth)把“固定资产投资扩张率”与固定资产数值变化公式关联，仅作候选线索；它不替代 Fuyao 契约或发行人报告证据。

## 留存样本与日期资格

只检查样本保留起点 20261015 及之后。18 个含 Fuyao raw 的目录共 360 条个股记录，18/18 目录的 Fuyao as_of_date 与目录数据日一致：

- 旧的无分组根路径 fin_indicators.fixed_asset_invest_expansion_ratio 出现 0 次。
- 实际嵌套路径出现 340 次；首个保留目录 20261015 的 20 条记录未返回该指标，已作为缺值排除。
- 后续 17 个目录均覆盖相同 20 只股票，fin_report=2026-2，每只股票的字段值在 17 次请求中完全不变。它们是同一报告期的重复观察，只证明值稳定，不计为 17 个独立财报样本。
- 逐日逐股的来源日期、fin_report、根/嵌套键、原值及 raw_fuyao.json / meta.json 哈希见[路径审计 CSV](../research/20261114_fuyao_fixed_asset_path_inventory.csv)。

因此，旧注册身份 同花顺-fuyao::fixed_asset_invest_expansion_ratio 仅作为错误的无分组根路径退役；这不表示该业务字段无效或被证伪。

## 2026H1 官方报告核验

fin_report=2026-2 对应中报。以 2026-11-12 采集样本为唯一语义比较快照，逐股票读取 2026H1 与 2025H1 正式报告合并资产负债表中 6 月 30 日的“固定资产”金额，计算：

(2026-06-30 固定资产 - 2025-06-30 固定资产) / abs(2025-06-30 固定资产) × 100

农业银行两份报告将本集团与本行列并展示，已使用“本集团”首组金额；该处理由[农行 2025H1 报告](https://www.abchina.com/cn/AboutABC/investor_relations/report/mm/202508/P020250829704069640960.pdf)和[农行 2026H1 报告](https://static.cninfo.com.cn/finalpage/2026-08-29/1225527334.PDF)中的报表表头及行值复核。金额单位在同一发行人两期报告内一致，单位换算在比率中抵消。全部 20 家发行人的报告页码、原始报表行、金额、Fuyao 值、误差、公告号、URL 和 PDF SHA-256 见[逐股对照 CSV](../research/20261114_fuyao_fixed_asset_growth_official_h1_comparisons.csv)。

| 股票 | 官方复算（%） | Fuyao 原值（%） | 绝对差（百分点） |
|---|---:|---:|---:|
| 深南电A（000037） | -5.4042079372 | -5.150324 | 0.2538839372 |
| 泸州老窖（000568） | -6.6509440956 | -6.638409 | 0.0125350956 |
| 善水科技（301190） | 12.7133592710 | 12.624828 | 0.0885312710 |
| 新华传媒（600825） | -9.5107839173 | -9.501337 | 0.0094469173 |
| 太湖远大（920118） | -1.6094763408 | -1.613541 | 0.0040646592 |

这五项的误差超过原值六位小数对应的舍入范围，根因目前未确认；不将其归因于舍入或报表更正。五个样本与官方固定资产同比计算方向一致。另对这五家尝试母公司固定资产值，均不能解释 Fuyao 原值。其余 15 家与上述合并报表计算在六位小数精度内吻合。固定资产投资现金流等替代项目没有获得同等强度的样本支持。

## 定案边界与后续线索

- 定案的是完整嵌套来源路径的业务含义及 % 单位，不是 Fuyao 服务端的精确输入字段、计算代码或历史基期修订政策。
- 5 个残差保留在对照表，后续若取得 Fuyao 原始能力/指标解释、同一股票其他报告期的字段切换样本或公开更正对照，可继续定位差异；在此之前不把误差写成容差规则。
- 同一财报期的 17 次重复采集不扩大独立样本数；结论只覆盖本次 20 家发行人和 2026H1 报告期。
- 不添加 mappings，不据此调整采集优先级、接口频率或碰撞路由。

## 注册表处置

- 当前完整路径登记为 verified，status_resolution=verified_by_empirical_addendum，证据等级 E3，单位 %。
- 无分组旧身份登记为 disproved / retired_legacy_path，并指向当前完整路径。该处置只修正路径身份。
- 定案 JSON：[20261114_fuyao_fixed_asset_growth_semantics.json](20261114_fuyao_fixed_asset_growth_semantics.json)。
