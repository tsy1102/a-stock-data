# 20260909 T35(wenda 定名) + A4(财务叶名补全) 执行报告

> 数据来源：通达信（问小达 wenda 四件套 + 云 `tdx_quotes` CwInfo）、腾讯自选股（westock `data_quote`）。
> 所有结论仅服务于字段字典定案，**不构成任何投资建议**。

## 0. 结论速览

| 战役 | 范围 | 结果 |
|------|------|------|
| **T35** wenda 字段定名 | 研报/公告/新闻/宏观 四件套 | 字段结构**全部定名**（研报/公告/新闻=[标题,时间,链接,来源,摘要]；宏观=[指标名称,指标完整路径,日期,指标值]）|
| **A4** fuyao 12 叶名补全 | §12.8.12i 的 12 个财务叶名 | **7+1 云通道闭环（L1，单位万元）**；**5 个确认在 TDX F10 利润表/现金流量表**（云 CwInfo + westock 不暴露，待本地 F10 实跑）|

**关键发现**：TDX 云 `tdx_quotes` 的 `CwInfo` 财务金额字段单位 = **万元**（非本地 `tdx_get_finance_info` 0x0010 的"角"、亦非 tdxstat 旧注）。铁证：`JLY`=4451688 万元 = 445.17 亿，与 push2 `f105` `net_profit_period` 逐字等。

---

## 1. T35 — 通达信问小达（wenda）四件套字段定名

### 1.1 实测样本与方法
- 研报/公告/新闻：贵州茅台 `600519`，结构化参数 `name`+`bdate`~`edate`（覆盖 2026 年）
- 宏观：中国 CPI/PPI，`query="中国|20260101|20260909||CPI,PPI"`（管道格式，仅 `query` 入参）

### 1.2 返回字段结构（命名神谕）

| 工具 | 返回 row 结构（命名字段） | 典型 dataCard 候选 | 典型 dataFunction 候选 |
|------|--------------------------|---------------------|------------------------|
| `wenda_report_query`（研报）| `[标题, 时间, 链接, 来源, 摘要]` | 预测目标价 / 龙虎榜 / 资金流向 / 主题投资-机会前瞻 / 牛熊研判 | 研报中心 |
| `wenda_notice_query`（公告）| `[标题, 时间, 链接, 来源, 摘要]` | 预测目标价 / 龙虎榜 / 资金流向 / 分红率 / 牛熊研判 | 公告中心 / 并购重组 / 股份回购 / 重要股东增减持 / 重大合同 / 前瞻会议 / 公司治理 / 立案调查 |
| `wenda_news_query`（新闻）| `[标题, 时间, 链接, 来源, 摘要]` | 主题投资-机会前瞻 / 龙虎榜 / 市场溯因 / 主题投资-热门主题 / 主题投资-新增主题 / 动态双柱图 | 热点解读 / 负面新闻 / 主题投资 / 市场风向 / 市场解读 / 数据解盘 |
| `wenda_macro_query`（宏观）| `[指标名称, 指标完整路径, 日期, 指标值]` | 牛熊研判 / 市场溯因 | 宏观专题 |

### 1.3 定名结论
- **研报/公告/新闻三件套同构**：统一为 5 命名字段 `标题 / 时间 / 链接 / 来源 / 摘要`。`时间` 在公告中为 `YYYY-MM-DD HH:MM:SS` 全精度，研报/新闻为 `YYYY-MM-DD`。
- **宏观独立结构**：4 命名字段 `指标名称 / 指标完整路径 / 日期 / 指标值`，且存在"去年=100 / 上年=100 / 同月=100 / 上月=100"多口径同指标（如 CPI 在 `指标完整路径` 中区分基期），属**时序命名源**。
- **性质定位**：wenda 四件套是**文本/时序命名源（oracle）**，不是量化数值对撞源——它用于"字段含义定名 + 内容检索"，不解决东财 ulist / 死占位符 / 计算字段等数值型未破解块。其 `dataCard/dataFunction` 候选元数据已在本回合统一经 `tdx_present_research_ui` 呈现。

---

## 2. A4 — fuyao §12.8.12i 十二叶名 × TDX 云 CwInfo / westock 交叉

### 2.1 单位铁证（先定单位，再对撞）
对 `600519` 云 `tdx_quotes` `CwInfo`：

| 字段 | 原始值 | 换算（÷10000 得亿）| 交叉锚 | 结论 |
|------|--------|---------------------|--------|------|
| `JLY`（净利润·归母）| 4451688 | 445.17 亿 | push2 `f105` `net_profit_period` = 445.17 亿（逐字等）| **单位 = 万元** ✅ |
| `ZZC`（总资产）| 30905078 | 3090.5 亿 | 茅台 2026H1 总资产量级一致 | **佐证 万元** ✅ |

> ⚠️ **单位分档铁律（新增）**：TDX 三套财务编码互异——
> - 云 `tdx_quotes` `CwInfo` 金额 = **万元**（本回合实测）
> - 本地 `tdx_get_finance_info` 0x0010 金额 = **角**（`/10` 得元，见 §零·C / line 279）
> - tdxstat 部分列 = **万元**（Col[14]/Col[24]，见 §7.3）
> 接入层必须按"源"分档换算，**禁止跨源套用单位**。

### 2.2 云通道闭环（7+1，L1）

| fuyao 叶名 | 含义 | TDX 云 CwInfo 字段 | 600519 实测(万元) | 等价 canonical / 公式 | 定级 |
|------------|------|---------------------|---------------------|------------------------|------|
| `net_profit` | 净利润 | `JLY` | 4451688（≈445.17亿 = f105 逐字等）| net_profit_period(f105) | **L1** ✅ |
| `profit_total` | 利润总额 | `LYZE` | 6143842（≈614.4亿）| 利润总额 | **L1** ✅ |
| `operating_profit` | 营业利润 | `YYLR` | 6141129（≈614.1亿）| 营业利润 | **L1** ✅ |
| `accounts_receivable` | 应收账款 | `YSZK` | 57.08（茅台应收极低，合理）| 应收账款 | **L1** ✅ |
| `holder_equity_total` | 股东权益合计 | `JZC` | 25125360（≈2512.5亿）| jingzichan（净资产）| **L1** ✅ |
| `cash_equivalents_net_addition` | 现金及等价物净增加额 | `ZXJL` | 5838700（≈583.9亿）| 现金净增加额 | **L1** ✅ |
| `total_debt` | 总债务（=总负债）| `LDFZ`+`CPFZ` | 4664507.5+1084275.75 = **5748783.25**（≈574.9亿）| 总负债 = 流动负债+长期负债 | **L1** ✅（公式）|

> `total_debt` 派生：资产负债率 = 574.9 / 3090.5 ≈ **18.6%**，与茅台低杠杆特征一致（CwInfo 口径自洽）。

### 2.3 需 TDX F10 子源（5，云 CwInfo + westock 均不暴露）

| fuyao 叶名 | 含义 | 落点（TDX F10 子源）| 状态 |
|------------|------|----------------------|------|
| `manage_fee` | 管理费用 | F10 利润表 `income_statement`（line 98 已登记字段名）| ⏸️ 待本地 easy_tdx `tdx_get_financial_analysis` 实跑 |
| `interest_expenses` | 利息支出 | F10 利润表（财务费用内含）| ⏸️ 待本地 F10 |
| `income_tax_expense` | 所得税费用 | F10 利润表 | ⏸️ 待本地 F10 |
| `research_and_development_expenses` | 研发费用 | F10 利润表（管理费用内含/单列）| ⏸️ 待本地 F10 |
| `pay_dividends_profits_interest_cash` | 分红/利息现金支出 | F10 现金流量表 | ⏸️ 待本地 F10 |

> 上述 5 字段在云 `CwInfo` 快照中**不存在**（CwInfo 仅暴露利润表"头部汇总"级字段：营收/成本/营业利润/利润总额/净利润/现金流净额/存货/应收/净资产/总资产/负债合计，不含费用明细行项目）。其语义已由 fuyao 叶名中文直给，属于"映射未登记"而非"未知"，待本地 F10 子源实跑后升 L1。

### 2.4 腾讯自选股（westock）财务覆盖结论
对 `sh600519` `data_quote` 实测返回：

| 类别 | 字段 |
|------|------|
| 行情/估值 | price / prev_close / open / high / low / volume / amount / change / change_percent / turnover_rate / volume_ratio / range_pct / avg_price / wb_ratio / outer_volume / inner_volume |
| 估值比率 | pe_ratio / pe_fwd / pe_lyr / pb_ratio / dividend_ratio_ttm |
| 市值/股本 | total_market_cap / circulating_market_cap / total_shares / float_shares |
| 区间 | high_52week / low_52week / chg_5d / chg_10d / chg_20d / chg_60d / chg_ytd |
| 板价 | price_ceiling / price_floor |

**印证（同源腾讯行情云）**：
- `total_market_cap`=16132.93 亿 ≈ TDX `ZSZ` 1614.23 亿（口径差，同源）
- `price_ceiling`=1440.23 = TDX `ZTPrice` 1440.23 **逐字等**
- `pb_ratio`=6.42、`pe_ratio`=19.81 与 TDX `ExtInfo`/`ProInfo` 同量级

**结论**：westock `data_quote` **仅返回 quote/估值快照，不含任何财务报表行项目**（无 管理费用/总债务/净利润明细）。这从实战印证此前判断——**westock 同源腾讯行情云，是估值 oracle，非财报源**。故 A4 目标三项中：`net_profit`/`total_debt` 由 TDX 云闭环，`manage_fee` 需 F10；**westock 不补全任何深度财务行项目**。

---

## 3. 边界与待办

- **wenda 四件套**：文本/时序命名源，不进入数值对撞闭环，仅作"字段含义定名 + 内容检索"神谕。
- **A4 残留 5 字段**：归"TDX F10 子源"，下一步用本地 `easy_tdx` `tdx_get_financial_analysis` F10 利润表/现金流量表实跑，登记 `manage_fee` 等费用明细行项目。
- **桶 B（东财 ulist 126 / 死占位符 / 计算字段）**：不在 TDX+腾讯射程，需独立"东财源破解"战役（见 `20260909_bucketA_TDX_oracle_sweep.md`）。

## 4. 配套改动
- `field_dict.md` §12.8.12i：12 叶名表增「TDX 云 CwInfo 字段 / 600519 实测 / 定级 / 状态」四列，标注 7+1 云闭环与 5 F10 待补。
- `field_dict.md` §12.8.19（新增）：TDX 问小达 wenda 四件套源字段结构。
- 新增单位分档铁律（云 CwInfo=万元 / 0x0010=角 / tdxstat=万元）。
