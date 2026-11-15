# 2026-11-15 新浪三表字段实证与包装路径核验

复核日期：2026-11-15（Asia/Shanghai）。这是新浪来源内字段语义实证，不是新浪未公开 API 的完整协议契约，也不创建跨源 `mappings`。

## 样本范围与日期口径

- 保留边界取 `scripts/capture_retention.py::MIN_CAPTURE_DATE`（2026-10-15）。本次实际找到 16 个含 `raw_sina_extended.json` 的数据目录，覆盖数据日期 `20261019` 至 `20261112`、20 只股票、每个股票日三类报表，共 960 个报表包装对象和 91,168 行科目数据。逐报表记录、来源元数据和 raw/meta SHA-256 见 [`20261115_sina_financial_report_inventory.csv`](../research/20261115_sina_financial_report_inventory.csv)。
- 目录 `data_date`、`meta.json` 中的 `capture_date` / `run_date`、报表 `report_period` 和 `publish_date` 分列保存；不得把运行日期当作财报日期。历史归档的报表期共有 `318` 个 2026-06-30、`642` 个 2026-09-30 记录。重复采集的是同一报告期，不计作新的独立财报期。
- 页面逐值样本来自 2026-11-12 目标数据目录、股票 600519 和 601288，报表期 2026-09-30、披露日 2026-10-31、合并口径、币种 CNY。2025 页面只用于对应科目的同比对照。页面值和采集值按报表期、报表类别、项目标题及主体绑定。

## `report_type`：项目包装字段，不是新浪原始报表字段

`stock_common/sc_datasource/_financials.py::get_sina_financial_report_raw` 将 `report_type` 放入请求参数 `source`，并返回 `{"report_type": report_type, "report_list": report_list}`；`scripts/capture_http_collectors.py::collect_sina_extended` 按 `fzb`、`lrb`、`llb` 请求后，以同一键写入 `financial_reports`。因此采集 JSON 中的 `report_type` 是项目回显的请求类别。

完整归档审计中，960/960 个包装值均与外层请求键相同；其内层 `report_list` 的 960 个对象均没有 `report_type` 键；科目行 `item_source` 与对应请求类别 91,168/91,168 相符。代码链与逐目录 SHA-256 清单在 inventory CSV 中。按完整身份将 `新浪(扩展API)::report_type` 标为 `disproved` / `project_derived_capture_output`，意思是“不是提供方原始字段”，不表示采集值错误。`fzb`/`lrb`/`llb` 仍作为项目财报包装类别有用。

## `item_value`：报表科目值，单位随科目

注册表原注“科目值（字符串）”过于简略。`item_value` 是某一报表类别、报告期和主体口径下，与同一行 `item_field` / `item_title` 绑定的项目值；它不是可脱离科目标签的单一股票指标。全量归档中，37,495 行为非空数值字符串、2,528 行为空字符串、51,145 行为 `null`，没有其他类型；全部非空字符串都可解析为十进制数。2,528 个空字符串全部位于空 `item_field` 分组行；`null` 与空字符串均不能当作 0。货币项目的例子以人民币元存档，EPS 项目为元/股，因此注册表单位保持空值，避免给整组异质项目强加一个单位。

新浪官网财报查询页以“万元”显示金额，raw 金额按 10,000 换算后与页面展示精度一致；EPS 页以元/股显示。金额页面显示两位小数，页面舍入容差为 0.005 万元，即 50 元；EPS 显示四位小数，容差为 0.00005 元/股。八个页面项目值样本全部落入各自显示精度范围，逐行差值和 SHA-256 见 [`20261115_sina_financial_item_page_comparisons.csv`](../research/20261115_sina_financial_item_page_comparisons.csv)。

## `item_tongbi`：同比变动率，以小数比例存储

注册表原注“同比（有才附 `_同比` 键）”没有说明数值尺度。七个可复算项目用同股、同报表类别、同一 2026-09-30 报告期的 2026 与 2025 新浪页值计算 `(本期 / 上年同期) - 1`，按五位小数四舍五入，七项均与采集值完全相同。例：贵州茅台营业收入 `0.01959` 表示增长 `1.959%`；农业银行基本每股收益 `0.10169` 表示增长 `10.169%`。因此单位记为“比率”，不是百分数值。全量数据中有 36,117 个数值、55,051 个空字符串、0 个 null；其中 757 个为数值 0。两个等值 EPS 例子中，页面同比复算为 0 且 raw `item_tongbi` 为 0；空字符串则表示没有可用的同比值。

本裁决确认观察样本中同比字段为小数比例。没有据此声称所有异常情况的服务端计算规则、上年基值为零的处理、重述政策或空值原因均已还原；上述情况未在这七个页面样本中出现。历史重复记录中有 `10` 个科目身份出现填充状态变化，但 `0` 个“两个不同非空值互相冲突”的情况；变化是空/null 与后续有值（含真实 0）之间的填充，不构成数值反例。

## Chrome 页面访问记录

访问时刻记录为系统时钟（UTC）在 Chrome 导航请求前读取的时刻，换算为 Asia/Shanghai；每次导航加载后核对 Chrome 返回的最终 URL 和页面标题。`item_value` 与 `item_tongbi` 的页面标签和值来自同日 Chrome 页面表格的实际观察；本轮为补齐审计时间再次打开并确认了各 URL / 页面标题。下表时刻精确表示本轮导航开始，不冒称每个表格单元在该秒单独读取。新浪页面的财务表头给出报表期与单位；本次没有把行情栏上的实时日期作为财报日期。

| 页面 | 精确 URL | Chrome 导航开始时刻（Asia/Shanghai） | 复核 |
|---|---|---|---|
| 贵州茅台(600519)利润表_新浪财经_新浪网 | [https://money.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/600519/ctrl/2026/displaytype/4.phtml](https://money.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/600519/ctrl/2026/displaytype/4.phtml) | 2026-11-15T19:28:58+08:00 | Chrome 导航开始时刻；加载后核对最终 URL 与标题 |
| 贵州茅台(600519)利润表_新浪财经_新浪网 | [https://money.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/600519/ctrl/2025/displaytype/4.phtml](https://money.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/600519/ctrl/2025/displaytype/4.phtml) | 2026-11-15T19:30:24+08:00 | Chrome 导航开始时刻；加载后核对最终 URL 与标题 |
| 贵州茅台(600519)现金流量表_新浪财经_新浪网 | [https://money.finance.sina.com.cn/corp/go.php/vFD_CashFlow/stockid/600519/ctrl/2026/displaytype/4.phtml](https://money.finance.sina.com.cn/corp/go.php/vFD_CashFlow/stockid/600519/ctrl/2026/displaytype/4.phtml) | 2026-11-15T19:32:05+08:00 | Chrome 导航开始时刻；加载后核对最终 URL 与标题 |
| 贵州茅台(600519)现金流量表_新浪财经_新浪网 | [https://money.finance.sina.com.cn/corp/go.php/vFD_CashFlow/stockid/600519/ctrl/2025/displaytype/4.phtml](https://money.finance.sina.com.cn/corp/go.php/vFD_CashFlow/stockid/600519/ctrl/2025/displaytype/4.phtml) | 2026-11-15T19:32:25+08:00 | Chrome 导航开始时刻；加载后核对最终 URL 与标题 |
| 贵州茅台(600519)资产负债表_新浪财经_新浪网 | [https://money.finance.sina.com.cn/corp/go.php/vFD_BalanceSheet/stockid/600519/ctrl/2026/displaytype/4.phtml](https://money.finance.sina.com.cn/corp/go.php/vFD_BalanceSheet/stockid/600519/ctrl/2026/displaytype/4.phtml) | 2026-11-15T19:32:38+08:00 | Chrome 导航开始时刻；加载后核对最终 URL 与标题 |
| 农业银行(601288)利润表_新浪财经_新浪网 | [https://money.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/601288/ctrl/2026/displaytype/4.phtml](https://money.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/601288/ctrl/2026/displaytype/4.phtml) | 2026-11-15T19:32:48+08:00 | Chrome 导航开始时刻；加载后核对最终 URL 与标题 |
| 农业银行(601288)利润表_新浪财经_新浪网 | [https://money.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/601288/ctrl/2025/displaytype/4.phtml](https://money.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/601288/ctrl/2025/displaytype/4.phtml) | 2026-11-15T19:32:59+08:00 | Chrome 导航开始时刻；加载后核对最终 URL 与标题 |

## 逐项页面比较

| 股票 | 报表 | 原始完整行 | `item_value` | 新浪当前页显示值 | raw 减换算显示值 | 值匹配 | `item_tongbi` | 页面复算到 5 位 | 比率匹配 |
|---|---|---|---:|---:|---:|---|---:|---:|---|
| 600519 | fzb | CURFDS / 货币资金 | 49926813769.810000 | 4992681.38 万元 | -30.190000 人民币元 | True | -0.03529 |  | not_checked |
| 600519 | lrb | BIZINCO / 营业收入 | 130970743649.040000 | 13097074.36 万元 | 49.040000 人民币元 | True | 0.01959 | 0.01959 | True |
| 600519 | lrb | PERPROFIT / 营业利润 | 88979846257.790000 | 8897984.63 万元 | -42.210000 人民币元 | True | -0.0057 | -0.00570 | True |
| 600519 | lrb | BASICEPS / 基本每股收益 | 51.530000 | 51.5300 元/股 | 0.000000 元/股 | True | 0 | 0.00000 | True |
| 600519 | llb | MANANETR / 经营活动产生的现金流量净额 | 84058979832.290000 | 8405897.98 万元 | 32.290000 人民币元 | True | 1.20068 | 1.20068 | True |
| 601288 | lrb | BIZINCO / 营业收入 | 618812000000.000000 | 61881200.00 万元 | 0.000000 人民币元 | True | 0.12332 | 0.12332 | True |
| 601288 | lrb | OPERPROFIT / 营业利润 | 288094000000.000000 | 28809400.00 万元 | 0.000000 人民币元 | True | 0.15204 | 0.15204 | True |
| 601288 | lrb | BASICEPS / 基本每股收益 | 0.650000 | 0.6500 元/股 | 0.000000 元/股 | True | 0.10169 | 0.10169 | True |

页面比较全集（含当前/上年页面、具体访问时刻、报表期、单位、换算因子、容差和 raw/meta 哈希）以 CSV 保存；六个金额项目和两个 EPS 项目均吻合。同比公式只计算有上年页面值的七项；资产负债表货币资金虽有页面值，但本次没有验证其同比公式。

## 裁决范围

- `新浪(扩展API)::item_value`：来源内实证定案为财务报表科目值；单位留空，因不同科目量纲不同。空、null、数值零分开解释。
- `新浪(扩展API)::item_tongbi`：来源内实证定案为同比变动率，单位“比率”，以小数比例表达；`0.01959` 为 1.959%。
- `新浪(扩展API)::report_type`：确认是项目包装层的请求类别回显，不是内层新浪 `report_list` 原始字段，按项目派生采集输出路径处置。
- 本轮没有新建任何跨源字段关系；同名字段仍按各自 `(source, 完整 code path)` 区分。官方页面访问路径只佐证新浪自身采集值，不作为另一独立数据源。
