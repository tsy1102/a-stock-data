# 2026-11-03 公开网页候选核验

- 碰撞报告：`20261103/20261103_collision_report.json`
- 报告 SHA-256：`cfce542384db3d804438a5105c06ec37eb2cf2786ba73de699d6c22a5657ff3d`
- 目标数据日：2026-11-03；碰撞窗口：7 个有效交易日（2026-10-23 至 2026-11-03）。
- 核验时间：2026-11-04 11:08–11:33（Asia/Shanghai），通过 Chrome 阅读公开页面。
- 网页结果：已访问 FTShare、同花顺、新浪、东方财富的公开页面；本轮没有运行真实采集。
- 路由：按用户明确授权直接使用 Chrome 查询公开网页，不以 TUN/直连状态作为访问门槛。
- 日期边界：目标样本是 2026-11-03；页面实时行情在 2026-11-04。未把 11-04 实时值回填为 11-03 历史值；可见页面未提供足够的 11-03 对齐数值，因此网页研究不能单独完成定案。

## 网页证据

| 官方页面 | 页面中可见的信息 | 对本次样本的限制 |
|---|---|---|
| [FTShare 行情列表接口文档](https://market.ft.tech/gateway/doc/p/mdsj0xyo) | 行情列表是快照接口，无历史日期维度；`change` 为涨跌额（元），`change_rate` 为涨跌幅，`turnover` 为成交额（元），`turnover_rate` 为换手率，`pe_ttm` 为 TTM 市盈率，`float_a_shares` 为流通 A 股股数（整数）。 | 可用于判别 FTShare 字段名和接口日期能力；不能提供 2026-11-03 的 FTShare 历史值，也不能确认 FTShare 底层数据提供方。 |
| [同花顺贵州茅台 F10](https://basic.10jqka.com.cn/600519/)、[泸州老窖 F10](https://basic.10jqka.com.cn/000568/)、[旺能环境 F10](https://basic.10jqka.com.cn/002034/) | 页面标注“市盈率(动态)”/“市盈率(静态)”而非 PE_TTM；分别显示流通 A 股约 12.50 亿、14.71 亿、5.15 亿股。页面财务口径为三季报，资料更新时间分别在 2026-10-30、2026-10-30、2026-10-27 附近。 | PE 页面没有给出可与采集值直接比对的 TTM 历史值；股数为季度资料且有舍入，不能证明 11-03 的精确股数或来源独立性。 |
| [新浪贵州茅台行情页](https://finance.sina.com.cn/realstock/company/sh600519/nc.shtml) | 页面在 2026-11-04 约 11:08 显示贵州茅台实时行情，含换手率约 0.22%、PE TTM 约 22.29、流通股约 12.50 亿股等。 | 是 11-04 实时页面，且页面标签不能确认采集 JSON 中 `money_flow[0].turnover` 的具体单位或语义。 |
| [东方财富全新好行情页](https://quote.eastmoney.com/sz000007.html#fullScreenChart)、[全新好个股数据页](https://data.eastmoney.com/stockdata/000007.html) | 行情页在 2026-11-04 11:23 显示实时“涨跌”约 -0.43 元、换手率约 1.83%；11:33 页面显示“昨收”9.33 元，即 11-03 收盘价。个股页列出 11-03 的公告/资讯。日 K 图交互提示落在 2026-09-29，未显示 11-03。 | 11-03 的昨收可与原始记录 `LATELY_PRICE=9.33` 对齐，但没有取得 11-02 收盘价或 11-03 历史 `CHANGE` 页面值；不能仅凭这一只股票确认该字段映射。 |

## 本轮候选（按优先顺序，最多 5 条）

### 1. `cc1_cb00a9dc597ac474a419a91ccfc60f7176bac666114a589edd3d6a990a08edbc`
- 精确候选路径：`sina_extended.turnover` ↔ `ftshare_rest.turnover_rate`
- 来源提供方记录：`sina_extended` = Sina；`ftshare_rest` = FTShare public REST Gateway; the underlying data provider is unconfirmed。
- 本地窗口样本：140 配对；数据日：T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103。
- 对撞方法摘要：Pearson=0.9997, Spearman=0.9969, 留一法同号=True；公式线索 `right ≈ 0.00010020917 × left + 0.00040315949`，R²=0.999332；逐股时序中位|Pearson|=0.9999，方向一致=1.0；名称词元=['turnover']，Jaccard=0.5。
- 区分条件：核对对应提供方官方字段定义、单位和有效日期；至少 3 只不同股票，时变字段至少 2 个有效日期，并逐样本对齐候选 raw 的来源日期/阶段。
- 本地原始路径：新浪值来自 `stocks[code].money_flow[0].turnover`，另有股票级 `turnover` 副本；例如 600519 在 11-03 为 56.8191。FTShare 11-03 的 `turnover_rate` 为 0.0059292577。两者与报告中的跨日仿射关系一致，但数值尺度不同。
- 网页结论：`inconclusive`。FTShare 官方文档把成交额 `turnover` 和换手率 `turnover_rate` 明确分开；新浪实时页 11-04 的换手率值不能验证新浪原始资金流路径在 11-03 的单位/定义。高相关和缩放公式仍只是候选线索。
- 处理：保留为 `needs_external_evidence`；需要新浪对应原始字段的官方口径或与原始来源、有效日期对齐的可比材料。

### 2. `cc1_a9615e737990e7455925d9513f6180cf2da1e22f7cd971bde21ecec11dc2dbf4`
- 精确候选路径：`fuyao.valuation.pe_ttm` ↔ `zhb.stat.pe_ttm`
- 来源提供方记录：`fuyao` = Tonghuashun；`zhb` = Tongdaxin。
- 本地窗口样本：80 配对；数据日：T:20261023, T:20261028, T:20261030, T:20261102。
- 对撞方法摘要：Pearson=0.9956, Spearman=0.9981, 留一法同号=True；公式线索 `right ≈ 0.98078168 × left + -1.4457777`，R²=0.991283；逐股时序中位|Pearson|=1.0，方向一致=1.0；名称词元=['pe', 'ttm']，Jaccard=0.5。
- 区分条件：核对对应提供方官方字段定义、单位和有效日期；至少 3 只不同股票，时变字段至少 2 个有效日期，并逐样本对齐候选 raw 的来源日期/阶段。
- 网页结论：`inconclusive`。同花顺官方 F10 对茅台、泸州老窖、旺能环境显示动态/静态市盈率标签，没有显示 PE_TTM 的可比历史值；页面值也没有与 11-03 样本日期对齐。字段名称和高相关不足以证明与 TDX `stat.pe_ttm` 同义。
- 处理：保留为 `needs_external_evidence`；需要同花顺该字段的 TTM 定义及至少两个有效日期的日期对齐证据。

### 3. `cc1_b3c02927febdca47d9938c53deed42d74be9111531318017d6f5d4b5238af09b`
- 精确候选路径：`fuyao.valuation.pe_ttm` ↔ `zhb.full.pe_ttm`
- 来源提供方记录：`fuyao` = Tonghuashun；`zhb` = Tongdaxin。
- 本地窗口样本：80 配对；数据日：T:20261023, T:20261028, T:20261030, T:20261102。
- 对撞方法摘要：Pearson=0.9956, Spearman=0.9981, 留一法同号=True；公式线索 `right ≈ 0.98078168 × left + -1.4457777`，R²=0.991283；逐股时序中位|Pearson|=1.0，方向一致=1.0；名称词元=['pe', 'ttm']，Jaccard=0.6667。
- 区分条件：核对对应提供方官方字段定义、单位和有效日期；至少 3 只不同股票，时变字段至少 2 个有效日期，并逐样本对齐候选 raw 的来源日期/阶段。
- 网页结论：`inconclusive`，原因与上一候选相同。同一批本地 ZHB 样本中 `stat.pe_ttm` 与 `full.pe_ttm` 数值相同，说明本地碰撞证据不能区分两个 ZHB 路径；同花顺网页也没有给出可比的 PE_TTM 历史值。
- 处理：保留为 `needs_external_evidence`，暂不把它与上一候选合并或单独定案；需先核实两个 ZHB 路径的结构关系和提供方 TTM 口径。

### 4. `cc1_ba48361b86358fee1de618818b4f901e51b9cb4318d6b93f31d6b67337c09bb5`
- 精确候选路径：`axdata.data.float_shares` ↔ `ftshare_rest.float_a_shares`
- 来源提供方记录：`axdata` = AxData multi-provider framework; current shortline interface uses Tongdaxin；`ftshare_rest` = FTShare public REST Gateway; the underlying data provider is unconfirmed。
- 本地窗口样本：139 配对；数据日：T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103。
- 对撞方法摘要：Pearson=1.0, Spearman=1.0, 留一法同号=True；公式线索 `right ≈ 0.99999997 × left + 25.450531`，R²=1.0；名称词元=['float', 'shares']，Jaccard=0.5。
- 区分条件：核对对应提供方官方字段定义、单位和有效日期；至少 3 只不同股票，时变字段至少 2 个有效日期，并逐样本对齐候选 raw 的来源日期/阶段。
- 本地 11-03 样本示例：600519 AxData 为 1,250,081,562.5 股、FTShare 为 1,250,081,601 股；000568 分别为 1,471,161,093.75 与 1,471,161,037 股；002034 分别为 514,547,382.8125 与 514,547,414 股。对应同花顺三季报页面显示约 12.50 亿、14.71 亿、5.15 亿流通 A 股。
- 网页结论：`inconclusive`（仅有标签层面的语义支持）。三只股票的同花顺页面支持“流通 A 股股数”这一宽泛解释，但页面股数经舍入且是季度资料，不能验证 11-03 精确值。FTShare 文档定义为整数股数，而 AxData 样本含小数股；FTShare 底层提供方和 AxData 该字段的来源独立性仍未确认。
- 处理：保留为 `needs_external_evidence`；需要字段级来源/日期说明，并解释 AxData 小数股数的编码或换算方式。

### 5. `cc1_c17cd377ca373e188be326e1e736696b1ced2672d9633c641732b4e6839d863f`
- 候选登记路径：`event_dc.CHANGE` ↔ `ftshare_rest.change`
- 实际原始上下文：Eastmoney 采集记录位于 `ipo_calendar[*].CHANGE`，对应同一行的 `SECURITY_CODE`；采集器将该列表保存在 `raw_event_dc.json` 的 `ipo_calendar`。不能把它泛化为没有容器上下文的全局 `event_dc.CHANGE`。
- 来源血缘：`scripts/capture_context_collectors.py` 的 `collect_event_dc()` 调用 `ipo_calendar()`；`stock_common/sc_datasource/_events.py` 将它请求到 Eastmoney Data Center (`reportName=RPTA_APP_IPOAPPLY`)。`source_lineage.json` 已有“东财-datacenter(英文键)”来源项，但缺少 `event_dc` 到 `datacenter` 的别名；这是一处来源别名记录缺口，不代表底层提供方未知。`ftshare_rest` 底层数据提供方仍未确认。
- 本地窗口样本：14 配对；数据日：T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103。
- 对撞方法摘要：Pearson=1.0, Spearman=1.0, 留一法同号=True；公式线索 `right ≈ 1 × left + 0`，R²=1.0；名称词元=['change']，Jaccard=1.0。
- 区分条件：核对对应提供方官方字段定义、单位和有效日期；至少 3 只不同股票，时变字段至少 2 个有效日期，并逐样本对齐候选 raw 的来源日期/阶段。
- 本地 11-03 原始值：`ipo_calendar` 行中 000007 的 `CHANGE` 为 0.21 元，000011 为 -0.40 元；FTShare 对应 000007 `change` 为 0.21 元。跨 7 个日期共 14 对仅来自这两个代码。
- 网页结论：`inconclusive`，有一项部分值佐证。东方财富 11-04 行情页的“昨收”9.33 元与 11-03 原始记录的 `LATELY_PRICE=9.33` 对齐；但网页未给出 11-02 收盘或 11-03 `CHANGE` 值，日 K 图也未显示目标日。页面标签支持“涨跌额”的宽泛含义；本地 7 日样本仅覆盖两个股票代码，仍低于区分条件。
- 处理：保留为 `needs_external_evidence`；补齐 `event_dc` 来源别名和实际数组路径后，再用至少 3 个代码的日期对齐证据审阅。此项不能据当前的 2 代码局部吻合写入主字典。

## 定案结论

本轮报告没有新 `actionable_L1`、`L1-C` 或公式候选；L1 仅为已登记关系复验。5 个候选的网页结论均为 `inconclusive`：官网提供了字段定义、标签和少量日期对齐值，但证据仍不足以确认完整来源路径、单位及跨源独立性。故 5 条仍保持 `needs_external_evidence`，不修改 `field_registry.json` 或主字典；候选审阅理由更新为本轮实际网页核验结果，不再沿用此前未访问网页的路由原因。
