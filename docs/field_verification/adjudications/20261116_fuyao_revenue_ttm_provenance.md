# Fuyao `revenue_ttm` 来源路径与回算口径裁决

复核日期：2026-11-16。没有运行采集。本次只检查 `同花顺-fuyao::revenue_ttm` 的精确来源身份、项目调用链、保留期报表输入和公开财报；不建立跨源映射，也不把报表期样本当作日频碰撞样本。

## 裁决

`同花顺-fuyao::revenue_ttm` 不是 Fuyao 利润表响应中的原始叶字段，而是项目在统一行情对象缺少 `revenue_ttm` 时，用 Fuyao `operating_income` 回算后写入的兜底输出。将此精确身份记为 `disproved` / `project_derived_capture_output`；这里的 `disproved` 只否定“这是 Fuyao 上游原始字段”的身份，不表示回算值错误。

该兜底值的业务口径是**营业收入 TTM**。东方财富 Push2 `f104` 对应的**营业总收入 TTM**是另一个来源路径；二者不可视作同义字段或精确等价，旧材料所记“约差 1.8%”不是舍入误差。本裁决不改动东方财富 `f104` 身份、字段路由或任何 `mappings`。

## 官方契约与项目调用链

- 项目保存的 [Fuyao 官方 API 契约镜像](../../verify/fuyao_api_full.md)将 `GET /api/a-share/financials/income-statements` 的 `operating_income` 定义为“营业收入（原币元）”。契约响应字段表没有 `revenue_ttm`。Fuyao 官方[单股财务体检示例](https://fuyao.aicubes.cn/best-practices/02-financial-health/example.html)也按季度序列调用利润表接口；精确字段表以仓库锁定的契约镜像为准。
- [`stock_common/sc_fuyao.py`](../../../stock_common/sc_fuyao.py) 的 `get_fuyao_financials("income", ..., limit=8)` 调用收入报表端点，默认 `period="quarterly"`，返回报表行；`operating_income` 来自对应的报表期记录。
- [`core/data_provider.py`](../../../core/data_provider.py) 先读取 `operating_income` 序列；用现金流序列选出最新报告期，再按“最近上一完整年度 Q4 累计值 + 本期累计值 − 上年同期累计值”计算 `revenue_ttm`。仅当 `rt_quote` 尚无 `revenue_ttm` 时才填入该值，并把 `field_sources["revenue_ttm"]` 标记为 `realtime:fuyao`。因此该路径是项目计算的 fallback，不是从 Fuyao 响应中透传的 `revenue_ttm`。
- [`scripts/capture_catalog.py`](../../../scripts/capture_catalog.py) 将 Fuyao 利润表输入登记为 `stocks.*.financials.income_q` / `income_a`；生产公式实际使用 `income_q` 中的 `operating_income`，没有登记或采集一个 Fuyao `revenue_ttm` 响应键。

## 保留样本和公式回放

按 [`capture_retention.py`](../../../scripts/capture_retention.py) 的 `MIN_CAPTURE_DATE=2026-10-15`，审计 2026-10-15 至 2026-11-12 的 18 个 Fuyao 归档目录、360 条股票记录。逐行输入、来源日期、生产公式回放结果及对应 `raw_fuyao.json` / `meta.json` SHA-256 见 [`20261116_fuyao_revenue_ttm_pipeline_samples.csv`](../research/20261116_fuyao_revenue_ttm_pipeline_samples.csv)。该 CSV 的规范 LF SHA-256：`71d217c54c4a0df4b031c369760a5a12ef725e53b420a646330f561cfdd57057`。

- 360/360 条记录的 `meta.sources.fuyao.as_of_date` 与其采集目录日期一致；每个目录均有 20 条股票记录，Fuyao 状态均为 `ok`。2026-10-19 的元数据没有 `n_expected` / `n_received` 字段，所以该日只确认归档中有 20 条记录，不据此声称来源报告的完整性计数为 20/20。
- 全部 18 个 `raw_fuyao.json` 中，精确键名 `revenue_ttm` 的递归路径数为 **0**。报表输入能直接对应的叶字段是 `financials.income_q[].operating_income`。
- 严格按当前生产代码重放后，338 条记录通过该回算分支的现金流期门槛，且营业收入年度、本期及上年同期三个输入均齐全；另外 22 条不能回算：2026-10-15 的 20 条没有所需财务序列，2026-10-26 的 2 条缺少所需收入输入。**338/338 个可计算样本均没有以 0 补齐缺失收入项；没有观察到缺输入却生成非零 TTM 的情况。**
- 这些日期化目录是重复采集的财报快照，不是 18 个独立报告期。`as_of_date` 用于描述 Fuyao 捕获元数据；`period_end_ms` / `report_date_ms` 才标识每条财报输入所属期间。本次回放只核验转换血缘和公式，不把重复快照用于跨源碰撞或日频等价判断。

## 发行人财报交叉核对

贵州茅台 2025 年年度报告与 2026 年第三季度报告把“营业总收入”和其组成中的“营业收入”分别列示；三季报还同时列出 2026 年和 2025 年前三季度比较数。它们与 Fuyao 保留样本中的 `operating_income` 数值相符：

| 口径与输入 | 2025 年全年 | 2026 年前三季度 | 2025 年前三季度 | 按 TTM 公式计算 |
|---|---:|---:|---:|---:|
| 营业收入（Fuyao `operating_income`） | 168,838,102,514.79 | 130,970,743,649.04 | 128,453,707,655.86 | **171,355,138,507.97** |
| 营业总收入 | 172,054,171,890.91 | 133,283,652,508.95 | 130,903,889,634.88 | **174,433,934,764.98** |

两种 TTM 相差 **3,078,796,257.01 元**，占营业总收入 TTM 的约 **1.765%**。2025 年年报将两者差额分列为利息收入 3,216,069,376.12 元；因此这是合并报表科目口径差异，不是四舍五入。来源为发行人正式披露：[贵州茅台 2025 年年度报告](https://static.cninfo.com.cn/finalpage/2026-04-17/1225114741.PDF)（利润表区分营业总收入与营业收入）及[贵州茅台 2026 年第三季度报告](https://static.cninfo.com.cn/finalpage/2026-10-31/1225649896.PDF)（前三季度及上年同期比较数）。公开报告在此用于事后验证科目及回算值；不据其披露时间倒推采集时点的信息可得性。

## 注册表范围

只将 `同花顺-fuyao::revenue_ttm` 标为 `disproved` / `project_derived_capture_output`，将说明改为项目根据 `operating_income` 计算的营业收入 TTM 近似兜底，并保存本次审计、逐行 CSV、代码链及变更前状态。保留旧 `reference_evidence` 作为历史记录；不新增 `mappings`，不修改原始采集文件、生产计算或来源路由。
