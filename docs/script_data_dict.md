# 脚本应用接口与字段来源字典(Script Data Dictionary)

> **创建日期**: 2026-07-28
> **更新日期**: 2026-11-25（同步最新字段裁决、五大报告的数据消费边界与日期缓存口径）
> **基于**: [field_dict.md](../docs/field_dict.md)(§12 多源字典 + §12.15 源优先级矩阵 O37 修订版 + **V17.0 拼音规律破解/口径实锤**)
> **目的**: 明确每个脚本的**每个字段**从哪个源/接口获取、走哪个中间层函数、**完整 fallback 链**、**跨脚本获取逻辑差异**——与 field_dict 形成"双字典"对照
> **使用原则**: 脚本调整前必查; 优先采用字典已确定的中间层函数
> **数据流总览**: 全市场脚本(mak/val)按全市场负载使用 ZHB 快照与受限批量源；个股脚本(sht/med/lng)由 push2delay 批量取基础行情、腾讯批量补充腾讯字段，再由 `get_canonical_stock_data` 对残缺字段逐股降级。
> **脚本清单(5 大, ful 已删除)**: `mak` / `val` / `sht` / `med` / `lng`。行数不作为接口契约。

---

## 当前运行源路由（2026-10-12，优先于下方历史字段明细）

`field_matrix.md` 是逐字段来源证据矩阵，不是脚本运行时路由表。五大脚本按工作负载选择批量源；源矩阵中的候选关系不自动变成生产 fallback。

| 脚本 | 工作负载与主路径 | 补源与保留规则 |
|:---|:---|:---|
| `sht` | 用户指定的约 30 只；push2delay ulist 300/批提供基础行情，腾讯 qt 批量 60/批补估值、财务比率、盘口与涨跌停字段 | ELTDX 天梯/封单包仍保留；不覆盖已有 push2delay 基础值。缺价时仍走 TDX → 腾讯单股 → push2delay 单股 → push2 末级 fallback |
| `med` | 指定的少量股票；与 sht 共用基础行情 + 腾讯补充批次 | ELTDX 天梯状态在中线报告中实际显示，故保留；共享 L2 缓存命中时不重复打批量接口 |
| `lng` | 指定的少量股票；与 sht/med 共用基础行情 + 腾讯补充批次 | 长线报告未消费 ELTDX 短线天梯，已取消该无用预热；缺失字段仍由统一层 fallback |
| `val` | 全市场；腾讯按 60 只/批提供行情快照并预热 Canonical 与 SQLite L2 | 本批来源以 `realtime:tencent:batch` 逐字段标记；闭市/盘前旁路逻辑保持原状 |
| `mak` | 全市场异常扫描；ZHB 快照为覆盖底，腾讯批量更新行情；候选结果再批量补东财 ulist 资金字段 | 保持其独立全市场路径与现有分域限流；部分 ulist 缺项只对缺失代码增量补取 |

### 0.1 字段破解采集与报告路由的边界（2026-10-14）

字段破解采集器已持续保存 Ulist239 全量数值字段。基于三笔有效交易日的真实样本，本项目在主 registry 中补充 9 个 Ulist239 财务字段的规范名、含义、单位，并关联到 TDX 0x0010 锚；依据协议和通达信公式定义确认 TDX `weifenlirun` 为“未分配利润”；另将腾讯 `[72]`、`[76]` 两个流通股本路径分别关联到 TDX 锚，并为 `[76]` 补齐已定义的 `[72]` 规范名。详细证据见 [`20261014 财务字段定案`](field_verification/20261014/20261014_finance_field_adjudication.md)。

这些映射用于降低后续碰撞重复计算，并让已确认字段作为未知字段的锚点；它们不等于新增五大报告指标，也不构成新增采集请求。SHT/MED/LNG/VAL/MAK 当前没有因此调整字段路由、指标或展示项。只有未来报告确有业务需求、字段时效与单位契约经过验证后，才应把这些值接入报告计算。

个股批量路由只对缺失字段补值，不做随机轮询：push2delay 的基础行情优先保留；腾讯批次补足其已核实字段。腾讯批次按 60 只切分并经过 `_gen_wait_process_interval` 进程级节流；push2delay 仍由 `sc_network` 共享熔断/限流控制，未向 push2 主域增加批量请求。单股 fallback 链只在批量字段缺失时执行，字段来源标记区分 push2delay 与末级 push2 主域。带来源的 quote L2 与扩展个股 Tencent L2 使用新分类键；MAK/VAL 全市场原始腾讯缓存继续沿用原分类，避免单独运行 MAK 时触发整市场缓存失效。跨进程批量缓存为 60 分钟硬 TTL，适用于一轮串行报告；同一小时内单独重跑可能复用该轮快照。

本次估算的请求变化：30 只股票在五项腾讯补充字段都可用时，原本最多逐股请求约 30 次腾讯行情，改为最多 1 次腾讯批量请求（另保留 1 次 push2delay 基础批量请求）；实际请求数取决于缓存命中和接口缺项。此处是按批次上限计算，不代表当日联网压测结果。

---

## 〇、公共数据源底座(所有 fallback 链的层级定义)

| 层级 | 实现位置 | 说明 |
|:---|:---|:---|
| **L1 ZHB 静态** | core/zhb_client `_parse_tdxstat`/`_parse_tdxstat2`/tipinfo; 入口 sc_datasource `get_zhb_single_stock_data` | T-1 快照; **tdxstat2 21 列全映射(V17.0)**; [4]/[6]/[8] 分别为 T/T-1/T-2 日涨跌停封单额（万元；涨停为正、跌停为负）；短线报告仅在 ZHB 文件日与行情数据日一致时显示 [4]，不得把历史槽位当作当前封单；**[11]=change_mtd 本月至今涨跌幅(基准=上月末收盘, V17.0.5 铁证——键名已由 change_5k_bar 改名)**; [13]=881 行业/880 概念双段; **⚠️ [9]/[10]/[14]/[15]=竞价量/竞价额(今/昨, 键名 main_net_buy_hands/amount 历史遗留——非主力资金流)** |
| **L1.5 THS SDK** | stock_common/sc_ths.py(同花顺官方 C 库 TCP——正式账号无限频) | 独有: PB/ROE TTM/主力净流入盘中/两融/户均持股/市值——候选级补全 |
| **L2 TDX TCP** | core/tdx_client(easy_tdx 适配) | 0x0010 金额**单位角**(O19 /10 得元); F10/boards/K线; **prefetch 命中时 canonical 跳过 TDX(V17.0)** |
| **L3 腾讯** | sc_datasource `get_tencent_quote` / tdx_client `_tencent_batch_fallback`(60/批) | O21 平盘 `is not None` 不回退; [67]/[68]=52周高低(V17.0 实证); **tx75 正名=近180交易日涨跌幅(V17.0.7 证伪"主力净流入")→ 已改名 change_180td_pct 并删除主力兜底分支** |
| **L3.5 新浪日K** | quotes.sina.cn `CN_MarketDataService.getKLineData`(V17.0.4 新增, mak `get_index_returns` 指数多周期收益兜底) | 域级限流已配(sc_network 150ms/5rps); 前复权, 与腾讯 ifzq `qfq` 实测一致(<0.01); **能力全集**: scale=5/15/30/60(分钟)/240(日)/1200(周)/7200(月), 日K字段 `day/open/high/low/close/volume`, 分钟级追加 `amount`——当前仅用 close 算区间收益, 其余字段按需取用; 同类已有接口: 新浪财报 `CompanyFinanceService.getFinanceReport2022`(sc_datasource) |
| **L4 东财 push2delay** | sc_datasource `get_em_quote_full_delay`(push2delay 镜像域, 风控独立) | **V17.0 主力源**: f162 动态PE/f163 静态PE/f137(主力净)/f140/f141/f142/f143/f144/f145/f146(四档)/f149(小单净)/f174/f175 52周; ulist(f2/f3/f4/f5/f6/f7/f8/f9/f10/f11/f12/f13/f14/f15/f16/f17/f18/f19/f20/f21 行情, **估值字段返回 "-" 勿用**); 1.0rps 限流 |
| **L5 东财 push2 主域** | sc_datasource `get_em_quote_full` | 风控最严最后手段; 当前 IP 封禁中自动跳过 |
| **L6 东财 datacenter** | 龙虎榜/股东/北向/解禁/大宗(日期单引号) | 独有数据 |
| **统一合约** | core/data_provider `get_canonical_stock_data` | sht/med/lng 主入口; **V17.0 补取**: push2delay 估值+资金流无条件补取(进程当天缓存 _PD_EXTRA_CACHE, 空结果不缓存) |

> **当前行情路由补充(V17.4.45)**: ①个股批量阶段 = push2delay ulist 基础行情 → 腾讯批量补充缺失的腾讯字段；②批量不完整时逐股 fallback = TDX → 腾讯 → push2delay → push2；③各字段通过 `field_sources` 记录真实来源；④主力净流入仍按字典定义使用 push2delay f137，不与竞价字段混用。

---

## 一、字段时效性分类(O37 修订 + V17.0)

| 类别 | 字段示例 | 主源 | 补源 |
|:---|:---|:---|:---|
| 行情(实时) | price/change_pct/amount/OHLC | 个股脚本：push2delay 批量基础行情 + 腾讯批量补充；val/mak：全市场腾讯批量覆盖 | 缺失字段按统一层走 TDX/腾讯单股/东财单股 fallback；ZHB 依时段提供可用快照 |
| 资金流 | main_net_buy(主力净) | **push2delay f137(主力净=超大单+大单, V17.0.16 重定案)** | THS(盘中)/TDX 0x0011(净量兜底); **ZHB 资金流键=竞价族不可作主力** |
| 估值 | pe_ttm/**pe_dynamic**/pb/dividend_yield | push2delay **f163 静态/f162 动态**(V17.0)/ZHB | 腾讯(pe_ttm/pb)/THS(PB)/fuyao(pe_mrq) |
| 财务 | net_profit/revenue/roe/eps | TDX F10/0x0010 | THS ROE TTM/新浪三表 |
| 股本 | total_shares/float_shares/mcap | 腾讯实时合并 | **gb_info Zgb/Ltgb/FreeLtgb(V17.0 定位)**/sc_capital_cache |
| 历史涨跌幅 | change_5d-60d/ytd | ZHB(**全部交易日口径**, V17.0 实锤) | 腾讯 52周 |
| 情绪/轮动 | KPL `strong/ztjs/df_num/lbgd`、板块榜原始值 | MAK A 展示已核实 KPL 字段；CLS 聚合情绪字段不作报告结论 | `strong` 是 0–100 情绪分值，不是百分比/概率；KPL `day` 只是响应标签。板块强度单位/公式未知，只展示来源值；短线侠 `kaipan` 是独立接口，不与 KPL/KPH 合并 |

---

## 二、data_provider 统一接口(按字段归类, V17.0 更新)

### 2.1 行情/资金流
| 字段 | 中间层 | 优先级链(V17.0) |
|:---|:---|:---|
| price/change_pct/amount/turnover | get_canonical_stock_data | push2delay 基础批量 → 腾讯补充批量 → (缺价时) TDX → 腾讯单股 → push2delay 单股 → push2 → ZHB |
| **main_net_buy** | **get_main_net_buy** | **push2delay f137(主力净=超大单+大单, 无条件) → TDX 0x0011**——ZHB 分支已删(其资金流键=竞价额); ~~腾讯 tx75 兜底~~ V17.0.7 删(证伪=180日涨幅) |
| main_net_buy_wan(cdata) | get_canonical_stock_data | **f137 /1e4(无条件) → TDX rt_fund**——与 get_main_net_buy 同源; ZHB 兜底已删(竞价额不可作主力); tx75 分支 V17.0.7 删除 |
| main_net_buy_wan_1d | cdata | **0(缺失)**——ZHB [15]=昨日竞价额(非主力 T-1), 已停用 |
| 四档资金流 | get_em_quote_full_delay | **主力=f137(=超大单+大单); 超大单=f140/大单=f143/中单=f146/小单=f149(净); f178 为 5 条带各自数据日的主力净额记录，SHT/MED 按逐条日期展示；旧 fund_*_5d/10d 映射已删** |
| **vol_ratio(量比)** | cdata | **腾讯 [49](现用, val 策略07 依赖) → push2 f50(V17.0.4 破解, 20/20 与腾讯同值, 可作等价源)** |
| **market_type(市场类型)** | get_board_type(code 推算) | **push2 f182(V17.0.4 破解官方枚举: 主板2/创业5/科创32/北交80, 可交叉验证)** |
| **industry_code_push2(东财板块代码)** | get_em_quote_full | **push2 f198(BKxxxx, 已解析使用)** |
| **财务字段透传** | cdata ← _em_quote_full_impl +f103/f104/f105/f108/f109/f160/f190 | `ocf_ttm`、`revenue_ttm`、`net_profit_period`、`net_profit_annual`、`eps_annual`、`eps_ttm`、`undist_profit_ps`；其中 `f108 → eps_ttm` 是归母净利润 TTM ÷ 当前总股本，不是扣非 EPS。旧 `eps_deduct_ttm` 仅作为相同数值的兼容别名。证据：[2026-11-14 f108 实证](field_verification/adjudications/20261114_push2_f108_eps_ttm_evidence.md)。 |
| **财务字段回退链** | get_canonical_stock_data | Fuyao 三张报表仍为报告期财务值主源；Push2 `f103` 族仅补缺失值，`eps_ttm` 由 Push2 `f108` 提供。`eps_ttm` 与 Fuyao `basic_eps` 的统计期间和分母口径不同，不映射为同义字段；旧别名 `eps_deduct_ttm` 只为调用兼容保留。 |
| **FTShare 历史字段（已退役）** | 旧私有托管 MCP；运行时会话客户端已删除 | 15 条旧来源路径及 `raw_ftshare.json` 仅保留作审计和显式历史研究；默认不采集、不碰撞。其底层来源无法从公开材料核实。 |
| **FTShare REST 契约锚** | `capture_field_probe.py` → `stock_common.sc_ftshare.get_a_share_quote_snapshot` | `ftshare_rest` 每日采集 `A股行情列表` 并输出 `raw_ftshare_rest.json`。官方返回字段定义登记为语义锚并参与默认碰撞；强多日匹配标 `L1-C`，不表示底层来源独立，也不自动定案。 |
| **Fuyao 官方字段契约** | `capture_field_probe.py` → `stock_common.sc_fuyao` | 逐字段审定的 Fuyao 上游契约证据会列入来源覆盖报告；Fuyao 来源独立性已确认，合格字段按普通独立锚参与 L1/L1-U，不标为 L1-C。 |

### 2.1b 竞价族(V17.0 实锤: ZHB tdxstat2 资金流键=竞价数据)
| 字段 | 中间层 | 说明 |
|:---|:---|:---|
| 竞价金额(今/昨) | ZHB stat2 main_net_buy_amount/1d(键名遗留) | =开盘金额=集合竞价成交额(万); [14]×开盘≈[14] 铁证(15/17) |
| 竞价量(今/昨) | ZHB stat2 main_net_buy_hands/1d(键名遗留) | 早盘竞价量(手); 与竞价额构成今昨竞价对(同花顺"今昨早盘竞价量比值"可算) |
| 竞价涨幅 | tdxquant VOpenZAF=(开盘-昨收)/昨收 | 实锤 |

### 2.2 估值/财务
| 字段 | 中间层 | 优先级链(V17.0) |
|:---|:---|:---|
| **pe_dynamic** | cdata | **push2delay f162(动态, 无条件补取) → fuyao pe_mrq → ZHB Col[3](=静态, 名不符)**;**腾讯 [52] 实为静态 PE 已从来源剔除(V17.0 实锤)** |
| pe_ttm | cdata | push2delay f163(静态TTM)/ZHB Col[9](MorePE TTM)/腾讯[39]——TTM 口径一致 |
| pb | cdata | push2delay f167/腾讯[46]/ZHB 计算; **clist f23=PB(行业对比 get_em_board_members, V17.0.15/H3 订正: 原误当PE→实测 f23 恒正=PB, 见主字典 §12.3.2.1)** |
| roe/gross_margin | get_gross_margin_and_roe | F10 加权 → 新浪自算(O19 统一口径) |
| 历史涨跌幅 | cdata | ZHB 单源(**交易日口径**: 5d/10d/20d/60d/ytd; **change_30d 历史遗留=20日值勿用**) |

### 2.3 股本/市值
| 字段 | 中间层 | 优先级链 |
|:---|:---|:---|
| total_shares/float_shares | get_share_capital | rt_quote → ZHB → sc_capital_cache(**gb_info Zgb/Ltgb 股/FreeLtgb 自由流通万**) |
| mcap_yi | calc_mcap_yi | 腾讯批量注入 → price×股本 → push2 直给(4 级) |

---

## 三、tdx_client 关键函数(V17.0 包化后路径 core.tdx_client)

| 函数 | 说明 |
|:---|:---|
| tdx_get_quote_full | 内部 ZHB→TDX→腾讯; **canonical 在 prefetch 命中时不再调用(V17.0)** |
| tdx_get_finance_info(0x0010) | 财务——O19 单位角→元/10 |
| tdx_get_fund_flow(0x0011) | 主力资金流(唯一主力净量源, cdata.main_net_buy_hands 非实时=0 时用它) |
| _tencent_batch_fallback | 腾讯批量 60/批——mak/val 核心(进程内按交易日缓存) |
| get_history_fund_flow_120d | 60/120 日资金流(sht prefer=tdx / med prefer=em) |
| _TENCENT_FIELD_INDEX | [67]/[68]=52周高低(V17.0 实证); **pe_dynamic 索引已移除(静态勿用)** |

---

## 四、sc_datasource 函数(HTTP + 新源, V17.0 更新)

| 源 | 代表函数 | 脚本 |
|:---|:---|:---|
| 东财 push2ex | `get_limit_broken_pool`/`get_limit_down_pool`/`get_yesterday_limit_pool` 仍保留适配器能力；当前 MAK/SHT 的 `get_limit_pool_summary` 调用均传 `allow_push2ex=False`，不会走该兜底 | 诊断/显式适配器调用 |
| 东财 datacenter | get_em_industry_l2_data/get_holder_structure/get_margin_trading/get_block_trade/get_dragon_tiger_board/get_lockup_expiry/**get_yjyg_all(业绩预告全市场分页, V17.0)**/**eastmoney_datacenter(+page_index 参数)** | sht/med/lng/mak/val 策略22 |
| 东财 push2delay | **get_em_quote_full_delay**(f162/f163/f167/f174/f175/f137/f138/f139/f140/f141/f142/f143/f144/f145/f146 全字段)/prefetch_quote_batch(ulist)/**get_em_batch_quotes(+f62 主力净, V17.0.16 重定案: f62 已含超大单+大单, 不再 +f66)** | canonical/sht 批量预取/mak 全市场主力 |
| 同花顺 | **get_ths_hot_raw(getharden 唯一入口, V17.0 三版合一)**/ths_hot_list/**get_eps_forecast(本机 ProfitForecast 优先, V17.0 |)**/**ths_limit_up_pool(涨停池优先源, V17.0.1g, 17 字段含涨停原因/板型/封板率/炸板/换手/流通市值; 缓存 `limit_pool_v3`)** | val/mak/sht/lng |
| 财联社 | `cls_telegraph`；`get_cls_market_emotion` 保留字段研究 | 电报关联：VAL 政策线索、SHT/MED/LNG 个股舆情；`get_cls_market_emotion` 不进入五大报告的解释性情绪输出 |
| KPH（开盘红） | get_kph_limit_ladder | mak B+ |
| 巨潮 | **get_strategic_announcements(新增 keywords 参数, V17.0 下沉 mak 异动公告)**/cninfo_irm | mak/sht/med/lng |
| 新浪 | get_sina_financial_report/get_sina_balance_sheet | val 04/med/lng |
| KPL（开盘啦） | `get_kpl_market_sentiment`、`get_kpl_plate_strength` | MAK A 展示情绪分值、涨停家数、大幅回撤个股数、连板高度及板块榜；KPL 响应日期只作标签，不能单独证明实际数据日；板块 `strength` 只显示源值。`get_kpl_broken_ratio` 与 `get_kpl_limit_up_detail` 保留研究/采集用途，不把未定案 RiseFallAnalysis 字段用于报告计数。MAK B 关闭 Push2，仅把 KPL 统计作为单源对照，不用它回填涨停池名单数 |
| THS | get_ths_market_snapshot/get_ths_pb | val 04 PB(仅盘中核对——盘后跳过) |
| duanxianxia（短线侠） | get_plate_rotation_top/get_plate_rotation_matrix | mak D 外部对照；显示接口返回日期和指标值，`kaipan` 参数不等同于直接调用 KPL |
| ZHB 快照辅助 | get_zhb_full_market_snapshot/get_zhb_market_stat2_snapshot/zhb_field_safe | mak/val 全市场 |

---

## 五、5 大报告脚本**逐字段**调用矩阵（历史字段消费信息，运行源路由以本节前置表为准）

> ⚠️ **V17.0 行号说明**: 全脚本经 core/ 包化 + 批量骨架收敛 + 死代码清理, 行号已大幅漂移——下表行号为当前代码定位, 以 `Select-String` 复核为准。

### 5.1 get_mak_report.py（市场全景）——8 段(A/B/B+/C/近3日异动回溯/D/E/F)

> ⚠️ **V17.0(2026-08-15 核查修正)**: 原注释"A-G 段"过时——脚本实际段为
> **A 全市场情绪 → B 涨停池 → B+ 涨停天梯/盘口异动 → C 板块-异动 → 近3日异动回溯 →
> D 行业轮动 → E TOP10 板块深度 → F 资金流验证**(无 G 段标题输出)

#### 5.1.1 个股扫描字段(主入口 `get_market_abnormal_data`/`_get_zhb_market_data`)
| 字段 | 获取函数 | fallback 链 | 说明/口径 |
|:---|:---|:---|:---|
| 全市场快照 | `get_market_abnormal_data` | ZHB 全市场快照；腾讯按批次覆盖有逐股 `[30]` 时间戳的字段；TDX 命名 fallback 实际也读取 ZHB 快照 | A 股过滤；ZHB 数据日来自压缩包文件名 |
| price | — | 日期与时间戳一致的腾讯字段 → ZHB `price_map` | 逐字段保留来源、数据日和观测时刻；腾讯时间戳无效时不借用 ZHB 日期 |
| change_pct | — | 日期与时间戳一致的腾讯字段（含有效平盘 `0`）→ ZHB Col[6] | 平盘是有效值；收盘判断需目标交易日且腾讯时间戳不早于 15:00，或同日 ZHB 快照在收盘后读取 |
| amount_yi | — | 有日期时间戳的腾讯 `amount_wan/1e4` → ZHB `amount/1e4` | 万元→亿元；来源日期随所用字段记录 |
| turnover | — | 有日期时间戳的腾讯 `turnover_pct` → ZHB | 收盘异动辅助条件也须与异动指标日期相同 |
| mcap_yi | `_calc_mcap_yi` | price×股本(sc_capital_cache) | 股本缓存未命中=0 |
| `ret_3d` | `_calc_3d_from_daily` | 连续三个交易日涨跌幅复合；以腾讯当日值拼接 ZHB 前序交易日值，或全用同一 ZHB 快照日值 | 不重复计入同日 ZHB 涨跌幅；日期链不连续、字段缺失或无法确认时为未评估，不伪作 0 |
| `ret_5d/10d/20d/60d` | `_get_zhb_market_data` | ZHB `change_5k_bar/10k_bar/20k_bar/60k_bar` | 按交易日 bar 窗口；字段安全状态及 ZHB 包日期合格后才使用，避免把自然日 `change_10d` 等同交易日收益 |
| 指数基准 | `get_index_returns` | 带日期指数日 K：TDX → 腾讯 ifzq → 新浪 JSON/JSONP → 腾讯实时缩减兜底 | 每个指标按个股指标的同一结束日和完整交易日窗口计算；缺少任一日期的收盘价即不评估，不按数组尾部直接对比 |
| 异动评估 | `_evaluate_stock` | 个股收益与对应指数同数据日、同交易日窗口逐项对齐 | 当前扫描只评估目标行情日；3/10/20 交易日异动均要求可确认收盘数据，旧数据日不冒充当前信号；报告分别列出各窗口可评估数及未评估原因 |
| 历史异动次数 | `count_history_deviations` | TDX 个股日 K + 指数日期 K 线 | 以日期连接最近 10 个先前三交易日窗口；必须 10 个窗口全部具备双方完整 K 线才报告次数，否则为未知，不以 `0` 表示缺数据 |
| main_net_amount | **ulist 批量 f62**（已验证为主力净额，含超大单+大单，不再加 f66） | `get_em_batch_quotes` 全市场批量；只汇总同一 Ulist 行 `f124` 与 `f297` 一致且匹配交易日历基准日的记录。日期锚缺失、不完整、冲突或不匹配的行不参与合计。 | f62 与 Push2 `stock/get::f137` 的已登记同义关系保留（历史对撞 96.6%）；单位为元（适配器 `main_net_inflow_wan` 万元值×1e4）；ZHB 竞价额不回填 f62，仅在无可用 f62 样本时单独展示 |
| **industry_code** | ZHB [13] | `_is_industry_code` 过滤 | **V17.0: 仅认 881 段=行业; 880 段=概念/风格(股权转让/微盘股等)已过滤** |
| name | snapshot/profile/腾讯 | — | ST/退剔除 |
| A 股过滤 | `is_a_stock`(sc_utils 统一, V17.0) | 前缀 00/30/60/68/92 | 滤 ETF/LOF/可转债 |
| is_limit_up/down | `limit_pct_for` | change_pct vs 阈值-0.5 | 主板/ST 10、双创 20、北交所 30 |

#### 5.1.2 其他段(V17.0 变化)
| 段 | 变化 |
|:---|:---|
| A 市场观测与个股异动 | ZHB 字段按包日期标记；腾讯报价仅在逐股时间戳与字段日期一致时覆盖。涨跌广度/涨跌停统计只纳入目标数据日且收盘时点已确认的涨跌幅；当前个股 3/10/20 交易日异动还要求数据日等于本次目标行情日，并与同日指数窗口对齐。报告列评估覆盖率和缺口原因；窗口不完整时不生成“无异动”结论。历史触发次数按日期连接 K 线，覆盖不足显示未评估。TDX 市场统计仍是独立响应且无可核验数据日，不称同日交叉校验。KPL `strong/ztjs/df_num/lbgd/tip` 使用已核实释义；`strong` 不转成百分比或项目情绪分档，`Day` 只是响应标签。KPL 板块榜只显示未定案接口原始列。连板梯队只统计 ELTDX 有效 `ladder_level`，不按近 3 日涨幅估算；CLS 聚合字段只留研究。 |
| A 段宏观资金(V17.0 2026-08-15) | get_hsgt_macro_flow(北向宏观, **asyncio.to_thread 包装防阻塞**, H2 审查修复) | 看板首行: 北向净流入+外资情绪 |
| B/B+ 涨停池 | `get_limit_pool_multi_source` 并列展示 KPL `ztjs` 与显式请求日期的东财名单计数；KPL `Day` 只是响应标签，东财请求日期也不是返回数据日证明，两数相同仅表示数值一致，不构成同日交叉确认；计数冲突或无法确定时不汇总、不取最大值。MAK 关闭 Push2，因此只显示 KPL 响应观测，不回填 THS 名单计数。CLS 未定案计数及 KPH 复盘榜不投票；空详情不伪造零炸板。KPH（开盘红）梯队保持独立来源。 |
| C 板块-异动 | ZHB 旁路优先 `_build_sectors_from_zhb`、TDX 兜底(防 push2 风控) |
| 异动公告 | **get_abnormal_announcements → get_strategic_announcements(keywords=["异常波动"], V17.0 下沉带缓存+TDX 兜底)** |

MAK/SHT 涨停池显式以 `latest_market_data_date` 查询 THS 并作为汇总缓存键；MAK/SHT 当前关闭 Push2。THS 名单接口未返回独立实际数据日，报告须标为目标日期请求的来源响应观察，不称为已确认的实际数据日。KPL 板块榜接收该请求日期，KPL 情绪接口仍以响应 `Day` 标签识别样本；请求日期或响应标签都不单独证明来源实际数据日。SHT 的前一交易日晋级观察也须保留 THS 名单实际日期未核实的说明。

### 5.2 get_val_report.py（当前 27 策略全市场）

- 策略扫描使用 asyncio 并发 3；ZHB 快照 O(1) 读取。动态行情字段由可用的腾讯报价覆盖，不以市值是否缺失决定是否更新。
- **策略07 政策驱动**：优先使用与个股代码关联的 THS 热度题材；快讯回退仅将代码、名称或正文可关联到目标股票的新闻作为候选依据，并在理由中引用标题/时间，不再把全市场政策关键词复制给无关低市值股票。
- **策略17 竞价额占比**：仅使用与最新有效行情日一致的 ZHB 数据日中的竞价成交额与成交额；ZHB 日期不是最新行情日、日期不可确认或任一分子/分母缺失时跳过；不调用东财主力净流入作回退。结果文案显示 ZHB 数据日和比值，不把竞价额描述成主力资金或资金关注度。
- **策略18/19 竞价加速与动量**：读取 ZHB `stat2` 竞价额字段，按竞价字段本义展示，不称为主力净流入。
- **策略20 业绩预增**：`get_yjyg_all` → Eastmoney `RPT_PUBLIC_OP_NEWPREDICT`；按预告类型与 `ADD_AMP_LOWER/UPPER` 评估，并以 `IS_LATEST=1` 去重。
- **策略21 盈利预期**：本机 `ProfitForecast` 索引（`local_only=True`）及股东户数变化；全市场扫描不触发逐股网络兜底。
- **策略22/23**：月内动量读取 ZHB 交易日口径涨幅；PS 估值使用 Fuyao 可得字段。
- **策略27 开盘动量·竞价活跃**：仅用已核实的 ELTDX 竞价量昨比、开盘成交额昨比、开盘涨幅与自由流通口径开盘换手率进行启发式排序；`opening_rush` 算法/正负方向未确认，不参与筛选或评分，策略分不解释为资金流向或买入信号。
- PB 批量盘中由 THS 核对，盘后跳过；`ths_hot_reason` 委托 `get_ths_hot_raw`；行业判断采用东财申万二级、TDX boards 与 ZHB 行业段过滤；报告通过 `render_md_report` 输出 Markdown。

### 5.3 get_sht_report.py（短线）
| 变化点 | V17.0 |
|:---|:---|
| 批量骨架 | **基类 execute_batch_pipeline**；prefetch_fn 经统一层使用 push2delay 基础行情 + 腾讯批量补充；仍保留 ELTDX 短线章节与 SHT 异步 datacenter 预热 |
| 主力净流入 | 二章/七章**统一 f137(主力=超大单+大单, V17.0.16 重定案)**; T日主力净买入量=TDX 0x0011(非实时 0 时跳过显示) |
| PE(动) | cdata.pe_dynamic=push2delay f162(真动态 15.55, 腾讯静态不再覆盖) |
| 封单 | 盘中优先用 Fuyao 当前封单信息；ZHB tdxstat2 `[4]` 是 T 日封单额，仅在文件日与行情日一致时显示，不把 `[6]/[8]` 历史值混作当前封单 |
| 打板(涨停池, V17.0.1g/h) | **get_limit_pool_summary → 同花顺优先**(ths_limit_up_pool 17 字段: 原因/板型/封板率/炸板次数/首末封/回封/换手/流通市值/市场类型/新股, 缓存 `limit_pool_v3`); MAK/SHT 显式传交易日历目标数据日并关闭 Push2 回退; 板块分布=TDX tdxhy 一级行业注入(零网络); KPL 单源统计只作对照、不回填名单数; SHT 的 TDX 全市场计数单独展示为本次响应，接口未提供可核验数据日 |
| SHT 涨停/连板 | 只在价格与涨跌幅日期均匹配交易日历基准日时判涨停；ZHB 连板数及 T 日封单额只在快照文件日与报价日一致时显示，不再按近 3 日累计涨幅估算连板 |
| SHT 日内信号 | 涨停、逼近涨停、天地板及模型单日涨幅因子均要求目标行情日日期确认；板块成分涨幅日期未确认时不输出领涨/随涨结论。涨停阈值复用统一板块规则，逼近涨停使用板块阈值的 70% |
| CLS 快讯 | 先按 `stock_list[].code` 精确关联目标证券，再用标题与正文文本兜底；只显示已关联快讯的主题标签，并为最多 3 条附短摘要；不使用未定案的 `stock_list[].pct` |
| 巨潮公告 | 只显示已定案的标题/日期；PDF 链接仅从 `adjunct_url` 构造，`announcement_id` 不当 URL，未定案 `type` 不展示 |
| Push2 f178 | 在资金流章节展示 5 条各自带日期的主力净额；日期采用数组元素日期，不用报告日替代，也不把数据并成一个没有明确期间的总额 |
| 多评委 | **sc_render.render_multi_school_scores(V17.0)** |
| 行业 | 东财申万二级 → TDX → **881 段过滤** |

### 5.4 get_med_report.py（中线）
| 变化点 | V17.0 |
|:---|:---|
| 批量骨架 | 基类 execute_batch_pipeline；基础行情/腾讯补充共用批量路由；ELTDX 连板状态在报告中消费，继续预热 |
| 资金流 60 日 | get_history_fund_flow_120d(60 日窗口) |
| 阶段涨幅 | cdata change_5d/10d/20d/60d(**交易日口径确认**) |
| 重大公告/CLS 快讯 | 公告从已验证 `adjunct_url` 加可点击 PDF 原文；CLS 先精确匹配关联证券代码，回退标题/正文，报告显示主题及最多 3 条正文摘要 |
| 5 日资金细节 | Push2 f178 按每条自身日期和元单位换算显示，不把五日数组日期继承成行情响应日 |
| 多评委 | sc_render(V17.0) |

### 5.5 get_lng_report.py（长线）
| 变化点 | V17.0 |
|:---|:---|
| 批量骨架 | 基类 execute_batch_pipeline；基础行情/腾讯补充共用批量路由；长线正文不消费 ELTDX 短线天梯，故不预热该包 |
| **综合数据** | **get_stock_composite_async 链已删除(V17.0 R3, 220 行)——统一 get_canonical_stock_data(_dp_composite 由 cdata 构建, 二次获取同步重建)** |
| 行业 | TDX boards → **ZHB 881 段过滤(V17.0, 防 880 概念污染)** |
| PE 静态 | `_pe_static = _zhb_pe_dynamic`(ZHB Col[3]=静态 TTM, 口径已知) |
| **机构一致预期(V17.0 2026-08-15)** | **本机 ProfitForecast JSON(零网络, O(1) 索引缓存 H4)**(get_eps_forecast 默认 local_only=False=允许网络兜底——单股路径安全) → 同花顺网络兜底 | 一章展示: 2025A/2026E-2029E EPS + 机构家数; M6 修复: ths 兜底字符串列 _safe_float |
| 重大公告/CLS 快讯 | 巨潮公告链接只使用 `adjunct_url`；CLS 以关联证券代码优先、标题/正文兜底，并显示主题及最多 3 条摘要 |
| 多评委 | sc_render(V17.0) |

---

## 六、本机验证数据源(2026-08-14 新增——不参与运行时链路, 破解/核验专用)

> 三客户端安装目录本机文件, 零网络、零风控; 用于字段破解与多源核验(与运行时源独立)

| 本机文件 | 用途 | 对应运行时源 |
|---|---|---|
| 通达信 base.dbf(标准 DBF) | 全市场财务/股本/行业HY/地域DY/上市日基准 | ZHB/tipinfo 财务核验 |
| 通达信 tdxhy.cfg+hy_tree.xml | 行业/细分行业(T/X 码) | get_industry 核验 |
| 通达信 bigdata_1.zip func_*.cfg | 官方字段名 1,924 个 | 字段语义佐证 |
| 同花顺 tableheader/iwcDataTable/Fy映射 | 官方列 ID 682+指标 81+IWC 56 | 涨停/封单/竞价/主力字段核验 |
| 同花顺 industry.ini/StockBlock.ini | 板块成员(881 段) | 行业归属核验 |
| 东财 ProfitForecast.dat | EPS 预测/评级(JSON) | ⚠️ **V17.0 已升格运行时源**(get_eps_forecast 主源, O(1) 索引缓存)——val 策略23/lng 机构预期直用 |
| 东财 gss_cqcx.db | 除权除息(SQLite) | 分红/除权核验 |
| 东财 fullfinnew_*.dat | 财务 double 流(15/50 字段已定位) | 财务字段核验 |
| 东财 SubIndustry.dat | 105 细分行业(JSON) | 行业核验 |
| 东财 Stock_Former_Name/StockAliasV1 | 曾用名/别名 | 名称核验 |

## 六、V17.0 数据流变更总览(2026-08-14)

| 变更 | 前(V16.x) | 后(V17.0) |
|:---|:---|:---|
| 主力净流入 | ZHB 优先/腾讯 tx75 优先(口径分裂) | **f137(当日权威)无条件优先, 全链同源**; V17.0.7 tx75 兜底分支删除(tx75=180日涨幅非资金流) |
| PE 动态 | 腾讯 [52] 冒充动态 | **push2delay f162 真动态; 腾讯静态剔除** |
| 行业 | ZHB [13] 880/881 混合(概念污染) | **仅认 881 段; 880=概念/风格** |
| 批量骨架 | 3 脚本各自 90-110 行 | **基类 execute_batch_pipeline(钩子参数化)** |
| composite | get_stock_composite_async 220 行 | **删除, cdata 统一** |
| 同花顺热点 | 3 版独立实现 | **get_ths_hot_raw 唯一入口** |
| 写尾/ST/多评委 | 各脚本重复 | **save_text_report/name_mark/sc_render 公共函数** |
| 上传 | sht 逐只/med lng 统一 | **全部统一(无固定超时后逐只上传场景消失)** |
| 超时 | 固定时间(3 度误杀) | **输出活性检测(900s 无输出判卡死)** |
| 腾讯 52周 | 未定位 | **[67]/[68] 实证** |
| 交易日口径 | 5d/10d 标"日历日" | **全系列交易日口径实锤** |

| **ZHB 资金流键语义** | main_net_buy_amount/hands 当主力 | **实锤=竞价金额/竞价量**(恒正+占比<5% + [9]×开盘≈[14] 铁证) |
| **主力净额口径** | f137 单独 | **f137(主力净=超大单+大单, V17.0.16 重定案; 旧 f137+f140 重复计数约 40% 已订正)** |
| **四档资金流** | f137 误当特大单净 + 主力=f137+f140 重复计数 | **f137=主力净(=f140+f143); f140=超大单净/f143=大单净/f146=中单净/f149=小单净**(加性+跨接口对撞, 见主字典 §12.3.4) |
| **ulist239** | 未知字段表缺失 | **跨源数值匹配定位 20+ 字段**(f9=动态PE/f37=ROE/f112=EPS 等, 13 项 20 股 100% 实锤) |

## 七、2026-08-15 字段增强实施轮(五大脚本 P0-P4 + 代码审查闭环)

| 变更 | 前 | 后 |
|:---|:---|:---|
| mak 主力净额 | ZHB main_net_buy_amount(实为竞价额, 名实不符) | **ulist 批量 f62(=f137 主力净, 跨接口对撞 96.6%; 旧 +f66 重复计数, V17.0.16 订正), 元口径, to_thread 防阻塞** |
| sht 连板追踪 | 3 日涨幅估算连板 | **ZHB[31] 真连板数优先**(双日铁证)+涨停类型[33]+官方封单额[4] |
| val 策略数 | 21 个 | **23 个**: 策略22 业绩预增(get_yjyg_all)+策略23 盈利预期(get_eps_forecast 本机+股东户数) |
| lng 机构预期 | 无 | 一章展示 2025A/2026E-2029E EPS+机构家数(本机零网络) |
| mak A 段 | 无北向 | **北向宏观资金(to_thread)** |
| get_eps_forecast | 同花顺网络抓取 | **本机 ProfitForecast O(1) 索引优先 + local_only 开关(全市场禁网络)** |
| 业绩预告 | 无 | **get_yjyg_all**(ADD_AMP 幅度/IS_LATEST 去重/5 页/日期缓存) |

**代码审查闭环(2026-08-15, 18 项)**: H1 单位 1e4 倍/H2 async 阻塞/H3 holder_num 契约/H4 缓存失效+5000 次扫描/
H5 裸 except/H6 zt_type 吞 0 全部修复; M1 分页/M2 filter 语法/M3 删死代码/M4 ADD_AMP 实测定案/M5 0 值回退/
M6 字符串格式化/M7 with open/M8 日期缓存/L1-L4 小项——详见 session_notes/20260815.md §8.15-8.16

---

## 八、2026-09-10 索引层滞后回填（real_dict_xcheck 代码实测）

> **依据**：`docs/field_verification/20260910/field_dict_xcheck_report.md` §三 + `xcheck.log`。
> **口径**：真实字典提及 54 字段 / 生产代码消费 88 字段；一致 44、反向缺口 44、真实滞后 4。
> **f1/f7/f10/f11/f13/f19 共 6 个为「区间/列举展开」（如 `f1,f2,…,f250`）写法引起的 xcheck 误报，不回填。**
> 本节回填 **44 反向缺口**（代码 `sc_datasource` 实测消费、字典原零提及）+ **4 真实滞后**（字典已载于 §二/§六，xcheck 因仅扫描 5 脚本未计入一致）。
> 语义取自 `field_dict.md`（章节见各注）；消费模块/方式取自 `xcheck.log`。数据来源：通达信；以下均不构成投资建议。

### 8.1 反向缺口（代码 sc_datasource 实测消费，字典原零提及）

| fNN | 语义（field_dict.md） | 消费方式 | 消费模块 |
|:---|:---|:---:|:---|
| f43 | 现价 | 字面量 | sc_datasource/_eastmoney.py、_quotes.py |
| f44 | 最高价 | 字面量 | sc_datasource/_quotes.py、_schema.py |
| f45 | 最低价 | 字面量 | sc_datasource/_quotes.py、_schema.py |
| f46 | 开盘价 | 字面量 | sc_datasource/_quotes.py、_schema.py |
| f47 | 成交量（手） | 字面量 | sc_datasource/_quotes.py、_schema.py |
| f48 | 成交额（元） | 字面量 | sc_datasource/_quotes.py、_schema.py |
| f49 | 同号同义对齐表载 ulist f49 ≡ push2 f186（异号映射；push2 f49 本字段 §12.8 未单列语义） | 字面量 | sc_datasource/_quotes.py |
| f51 | ≡ 腾讯[48] | 字面量 | sc_datasource/_eastmoney.py、_quotes.py |
| f52 | ≡ 腾讯[49] | 字面量 | sc_datasource/_eastmoney.py、_quotes.py |
| f53 | ulist 专属·待破解 | 批量 | sc_datasource/_eastmoney.py |
| f54 | ulist 专属·待破解 | 批量 | sc_datasource/_eastmoney.py |
| f55 | ≡ ulist:f112 | 字面量 | sc_datasource/_eastmoney.py、_quotes.py |
| f56 | ulist 专属·待破解 | 批量 | sc_datasource/_eastmoney.py |
| f57 | 股票代码 | 字面量 | sc_datasource/_eastmoney.py、_schema.py |
| f58 | 股票名称 | 字面量 | sc_datasource/_eastmoney.py、_quotes.py |
| f59 | ≡ ulist:f1 | 批量 | sc_datasource/_eastmoney.py |
| f60 | 昨收盘 | 字面量 | sc_datasource/_eastmoney.py、_quotes.py |
| f61 | ulist 专属·待破解 | 批量 | sc_datasource/_eastmoney.py |
| f69 | ulist 专属·待破解 | 字面量 | sc_datasource/_eastmoney.py |
| f75 | ulist 专属·待破解 | 字面量 | sc_datasource/_eastmoney.py |
| f80 | 同号同义·未实证·待核实（§12.9 对齐表） | 字面量 | sc_datasource/_quotes.py |
| f84 | 总股本（股→万股） | 字面量 | sc_datasource/_eastmoney.py、_quotes.py |
| f85 | 流通股本（股→万股） | 字面量 | sc_datasource/_eastmoney.py、_quotes.py |
| f92 | ≡ ulist:f113 | 字面量 | sc_datasource/_eastmoney.py、_quotes.py |
| f116 | 总市值（元） | 字面量 | sc_datasource/_eastmoney.py、_quotes.py |
| f117 | 流通市值（元） | 字面量 | sc_datasource/_eastmoney.py、_quotes.py |
| f126 | 同号同义·未实证·待核实（§12.9 对齐表） | 字面量 | sc_datasource/_eastmoney.py、_quotes.py |
| f127 | 行业名称 | 字面量 | sc_datasource/_eastmoney.py、_industry.py |
| f128 | 地域板块名称 | 字面量 | sc_datasource/_industry.py、_quotes.py |
| f129 | 净利率 | 字面量 | sc_datasource/_quotes.py |
| f135 | 净资产（元） | 字面量 | sc_datasource/_quotes.py |
| f136 | 主力卖出额（= f139 + f142） | 字面量 | sc_datasource/_industry.py、_quotes.py |
| f161 | 同号同义·未实证·待核实（§12.9 对齐表） | 字面量 | sc_datasource/_quotes.py |
| f164 | ≡ ulist:f115 | 字面量 | sc_datasource/_eastmoney.py、_quotes.py |
| f165 | ≡ ulist:f130 | 字面量 | sc_datasource/_quotes.py |
| f168 | 换手率% | 字面量 | sc_datasource/_quotes.py、_schema.py |
| f169 | 涨跌额 | 字面量 | sc_datasource/_quotes.py |
| f170 | 涨跌幅 | 字面量 | sc_datasource/_quotes.py、_schema.py |
| f171 | 振幅% | 字面量 | sc_datasource/_quotes.py |
| f184 | ≡ ulist:f41 | 字面量 | sc_datasource/_eastmoney.py、_industry.py |
| f189 | 上市日期（YYYY-MM-DD） | 字面量 | sc_datasource/_eastmoney.py、_quotes.py |
| f191 | 同号同义·未实证·待核实（§12.9 对齐表） | 字面量 | sc_datasource/_quotes.py |
| f192 | 同号同义·未实证·待核实（§12.9 对齐表） | 字面量 | sc_datasource/_quotes.py |
| f221 | ulist 专属·待破解 | 字面量 | sc_datasource/_eastmoney.py、_quotes.py |

### 8.2 真实滞后（字典已载于 §二/§六，xcheck 因仅扫描 5 脚本未计入一致——显式锚定关闭缺口）

| fNN | 字典已有记载 | 等效源 / 消费点 | 说明 |
|:---|:---|:---|:---|
| f37 | ulist239 `f37=ROE`（§六 变更总览；§12.3.2.3 全字段清单标「ulist 专属·待破解」） | ulist.np/get `f37` | 字典 §六 已载；xcheck 扫描 5 脚本未命中 ulist 直接消费，故计「滞后」——属工具扫描口径 artifact，非字典错误 |
| f50 | 量比（§二 2.1 `vol_ratio`：腾讯[49] 现用 → push2 f50 等价源；§12.3.1 `f50 ✅`） | 腾讯[49]（现用） / push2 f50（等价） | 代码主用腾讯[49]，push2 f50 作等价源；非 push2 字面索引，xcheck 未计一致 |
| f112 | ulist239 `f112=EPS`（§六 变更总览；§12.3.1.1 `f112 ✅ L1 板级枚举`） | ulist.np/get `f112` | 字典 §六/§12.3.1.1 已载；xcheck 扫描口径 artifact |
| f182 | 市场类型枚举（§二 2.1 `market_type`：`push2 f182` 已由 get_board_type 本地推算；§12.3.1 `f182 ✅`） | `sc_utils.get_board_type()` 纯本地（零网络） | 代码**不**字面消费 push2 f182（本地按代码前缀推算）；字典 §二 已正名「纯本地」，xcheck 计「滞后」系将「push2 f182」误读为消费断言 |

> **回填结论**：44 反向缺口现已在 §8.1 显式登记（字段/语义/消费模块），与 §12.8 主字典形成索引闭环；4 真实滞后在 §8.2 锚定原记载并说明为 xcheck 扫描口径 artifact。后续 `real_dict_xcheck.py` 复跑时，44 缺口将转为「一致」、4 滞后维持「字典已载」——索引维护层滞后关闭，字段语义正确性不受影响。

