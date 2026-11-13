# `reports::actualLastYearEps` 单源 E3 证据

核验日期：2026-11-12（Asia/Shanghai）。本决定只确认东方财富 `report/list` 中 `actualLastYearEps` 的时期/角色与单位，不将其解释成发行人按加权平均股数计算的法定基本/稀释 EPS，也不裁决相邻字段 `actualLastTwoYearEps`。

## 来源路径

- 项目来源为东方财富 `https://reportapi.eastmoney.com/report/list`，由 [`_financials.py`](../../../stock_common/sc_datasource/_financials.py) 的 `get_reports()` 以 `qType=0` 请求并直接保留原始记录；[`capture_context_collectors.py`](../../../scripts/capture_context_collectors.py) 将其归档为 `reports` 原始样本。
- 注册表目标是精确身份 `(reports, actualLastYearEps)`，响应键与保留的 `raw_reports.json` 路径同名。公开页面只显示研报记录，不把该 EPS 列作为页面标签展示；因此本裁决基于上游响应键名和发行人报告期实证，不声称页面直接显示了该字段或完整服务端公式。
- 本轮对照的 Eastmoney 现行原始响应来自 2026-11-12；研报 `publishDate` 只用于确定该条研报对应的前一完整会计年度，不能冒充 EPS 值自身的历史计算日期。

## 全部可比留存样本

保留期内共审计 8 个非空 `infoCode`，覆盖 4 只股票，分布在 16 个 `raw_reports.json` 捕获文件。8 条中 `actualLastYearEps` 均非空，且按股票/上年财年去重后为以下 4 个独立比较；同股同年重复研报不重复计作独立年度样本。逐条 `infoCode`、研报日期、API 值和先前核验结果见 [live samples CSV](20261112_reports_actual_eps_live_samples.csv)（SHA-256 `D33484462714E315429A56967D4F310EE93B6CFF40691018E973510B85C7B3E3`）；去重财报与股本复算见 [comparison CSV](20261112_reports_actual_last_year_eps_samples.csv)（SHA-256 `9CC7883BE0D5501DF8B01D08B4135636726115E51C96E41F701B9D029770685E`）。

| 股票 | 研报发布日期 → 上年财年 | API 值 | 发行人实际数据核验 | 结论范围 |
|---|---|---:|---|---|
| 泸州老窖（000568） | 2025-09-02 → 2024 | 9.15345681398375 | 2024 归母净利润 13,472,986,476.01 元；除以总股本 1,471,901,463 股为 9.15345681398375。2024 年报法定基本/稀释 EPS 为 9.18。 | 指向 2024 年实际业绩；采用总股本分母时精确复现。 |
| 旺能环境（002034） | 2025-11-03 → 2024 | 1.08548201357681 | 2024 归母净利润 560,869,862.25 元；除以总股本 516,701,203 股为 1.08548201357681。2024 年报法定基本/稀释 EPS 为 1.31/1.21。 | 指向 2024 年实际业绩；采用总股本分母时精确复现。 |
| 力合微（688589） | 2023-10-30 → 2022 | 0.62220011276885 | 2022 归母净利润 75,135,596.29 元；API 值反推分母约 120,757,928 股。公开材料列出 2022 年末股本 100,194,770 股、2024 年权益分派后股本目标 120,566,916 股及 2024 年末股本 121,176,942 股；法定 2022 基本 EPS 为 0.75。 | 指向 2022 年实际业绩；分母显然不是 2022 年末股本，但仍未找到与反推数完全一致的股本日期，故不裁决计算公式，也不把残差称作舍入。 |
| 太湖远大（920118） | 2024-08/11 → 2023 | 1.52186849064760 | 2023 归母净利润 77,457,018.70 元；除以公开发行后总股本 50,896,000 股为 1.52186849064760。招股说明书的法定 2023 基本/稀释 EPS 为 1.7902。 | 指向 2023 年实际业绩；发行后股本口径精确复现。 |

发行人年报中的法定 EPS 按其披露的加权平均普通股口径计算；Eastmoney 响应值在泸州老窖、旺能环境和太湖远大中可由对应年度归母净利润与报告所列/调整后的总股本复现。力合微的上一年度归属仍明确，但反推股本日期未闭合。因此本决定仅确认字段“上年实际 EPS”的时期/角色和元/股单位；不登记统一分母算法、回溯日期或对法定基本/稀释 EPS 的等价关系。该具体残差是公式口径未决项，不是另一报告期的反例。

## `actualLastTwoYearEps` 的隔离

8 个 `infoCode` 的 `actualLastTwoYearEps` 均与 `actualLastYearEps` 相同。重复值只能证明当前两个响应键的样本值一致，不能证明 `actualLastTwoYearEps` 的值代表上年、前两年或 API 的预期行为。它不进入本次决定，仍保持 `unverified`；不得将两个路径合并或共用验证状态。

## 官方资料

- Eastmoney 个股原始行情接口（`stock/get`，`f84`）：[000568](https://push2.eastmoney.com/api/qt/stock/get?secid=0.000568&fields=f84)、[002034](https://push2.eastmoney.com/api/qt/stock/get?secid=0.002034&fields=f84)、[688589](https://push2.eastmoney.com/api/qt/stock/get?secid=1.688589&fields=f84)、[920118](https://push2.eastmoney.com/api/qt/stock/get?secid=0.920118&fields=f84)。`f84` 只按个股 `stock/get` 响应使用；列表端点 `ulist.np/get` 的同编号字段不可混用。
- [泸州老窖 2025 年年度报告（含 2024 EPS）](https://static.cninfo.com.cn/finalpage/2026-04-29/1225240660.PDF)；[2026 年半年度报告（总股本）](https://static.cninfo.com.cn/finalpage/2026-08-26/1225501255.PDF)。
- [旺能环境 2024 年第三季度报告](https://static.cninfo.com.cn/finalpage/2024-10-30/1221553426.PDF)；[2024 年年度报告](https://static.cninfo.com.cn/finalpage/2025-04-18/1223125438.PDF)；[2026 年半年度报告（总股本）](https://disc.static.szse.cn/disc/disk03/finalpage/2026-08-26/0304b54e-4b8c-467f-8bb1-2bdc6911ffa9.PDF)。
- [力合微 2022 年年度报告摘要](https://static.cninfo.com.cn/finalpage/2023-03-23/1216190920.PDF)；[2023 年年度报告](https://static.cninfo.com.cn/finalpage/2024-03-27/1219412051.PDF)；[2024 年年度报告（含股本变动）](https://static.cninfo.com.cn/finalpage/2025-03-27/1222911454.PDF)。
- [太湖远大 2024 年 IPO 招股说明书（含 2023 财务指标和发行后总股本）](https://dataclouds.cninfo.com.cn/sjother/documents/2024/20240809/46359bf83a7f40ecad03abb8eb1d7741.pdf)；[2024 年年度报告（北交所）](https://www.bse.cn/disclosure/2025/2025-04-25/b3a219672c30432c9cc318da787a77e1.pdf)；[2024 年第三季度报告](https://static.cninfo.com.cn/finalpage/2024-10-30/1221575208.PDF)。
