# 归档：§三 与项目已知字段交叉印证（2026-08-09）
> 来源：docs/field_dict.md 原 §三（L4398–L5539），2026-09-11 经 L3 拆分归档移出。
> 本文件为一次性审计过程证据，字段权威状态以 field_dict.md §12.8.12e 为准。
> 数据来源：通达信。以上为字段破解过程记录，不构成投资建议。

## 三、与项目已知字段交叉印证（2026-08-09）

| AxData 接口 | 字段 | 印证结论 |
|:---|:---|:---|
| eastmoney_stock_realtime_snapshot（58 字段）| last_price/change_pct/change/volume/amount/amplitude/turnover_rate/pe_ttm/volume_ratio/OHLC/pre_close/总市值/流通市值/pb 等 | 与项目东财 push2（字典 12.3.1 实测 114 字段）**同源**——AxData 为规范化子集 |
| eastmoney_limit_up_pool（25 字段）| trade_date/market_code/last_price/limit_price/change_pct/amount/float_market_value/turnover_rate/first_limit_time/last_limit_time/seal_amount/continuous_count 等 | 与项目 get_limit_up_pool（12.8.1 push2ex）**同源**——连续数/封单/炸板字段一致口径 |
| stock_realtime_snapshot_tdx（41 字段）| 与 ZHB 同源（短线指标 stats_root 直接读 tdxstat.cfg）| §12.12.2 已详细录入 |
| cls_market_emotion | market_degree/shsz_balance/up_ratio 等 | 与项目 get_cls_market_emotion（12.10.2）**同接口同字段** |
| stock_daily_price_limit_tdx（15 字段）| 涨跌停价格官方规则枚举 | §12.12.3 已录——ZHB 涨停价规则验证 |
| stock_shortline_indicators_tdx（34 字段）| 与 ZHB tdxstat 同源 | §12.12.1 已录——O28 破解的 Col17-20 周期字段对照 |

**总结**：AxData 不新增独家数据源（全部封装已有公开源）——价值 = ① 256 接口完整目录（**能力地图**——避免漏接口）② TDX 系字段规范（instrument_id/symbol/tdx_code 命名对照）③ 巨潮/新浪期权/ETF 全系字段清单（项目未接的领域参考）。


> **来源**：https://electkismet.github.io/AxData/interfaces/（eltdx 作者新框架，256 个接口，Apache-2.0）
> **✅ 2026-08-10 仓库最新源码核对**（clone electkismet/AxData@main，import 各 sources/*/catalog.py 的 INTERFACES 逐一比对）：
> - 总数 **256**（原记 257）：tdx 90 + tdx_ext 31 + exchange 3 + eastmoney 13 + cninfo 32 + tencent 6 + sina 60 + cls 12 + kph 9
> - **tdx 90 个接口名全部在字典中**（0 缺失）；原"91"为口径差（实际 股票 67 + 指数 7 + ETF 10 + 概念题材 6）
> - **tdx_ext 补录 2 个**：`tdx_ext_instruments_tdx` / `tdx_ext_markets_tdx`（原漏列，31 总数未变）
> - **新浪 60 补齐展开**：期权 21 + 期货 6 + 龙虎榜 5 的具体接口名（原为缩写）
> - 除以上 34 处展开/补录外，仓库 256 接口与字典 12.12.0 分类清单**完全一致**
> **数据源**：通达信 90（2026-08-10 仓库核对，原记 91）/ 通达信扩展行情 31 / 交易所 3 / 东方财富 13 / 巨潮 32 / 腾讯 6 / 新浪 60 / 财联社 12 / 开盘红 9
> **核心价值**：① 短线指标与项目 **ZHB 数据同源**（stats_root 可直接传 tdxstat.cfg/zhb.zip）② 涨跌停官方规则枚举 ③ 筹码分布/ESG 等空白维度
> **注意**：接口为 AxData HTTP/SDK 封装（POST），非直连协议；字段名以 AxData 文档为准
> **✅ 2026-08-05 实测验证**（axdata 0.1.3 + axdata_core，stats_root=项目 cache/zhb/zhb_20260803.zip）：
> - `stock_shortline_indicators_tdx` 调用成功，**stats_date=20260803 与项目 zhb 包日期一致**（确认消费同源数据）
> - **free_float_shares 三源精确闭环**：
>   - 600519: AxData=540949000 股 = ZHB Col11=54094.90 万 × 10000 = 官方 TdxQuant FreeLtgb=54094.90 ✅
>   - 000001: AxData=8160481200 股 = ZHB Col11=816048.12 万 × 10000 = 官方 FreeLtgb=816048.12 ✅
> - 34 字段全返回（茅台 open_volume_ratio=1.01/prev_amount=48.99亿/昨开盘量=408手等）
> - 调用方式：`from axdata_core import request_interface; request_interface("stock_shortline_indicators_tdx", params={"code":"600519","stats_root":"<zhb.zip路径>"}, fields=None, persist=False, data_root=None)`

#### 12.12.1 短线指标 34 字段（stock_shortline_indicators_tdx）🆕 最重磅

> **关键**：`stats_root` 参数可传 tdxstat.cfg/tdxstat2.cfg 目录或 zhb.zip——与项目 ZHB 数据**完全同源**，
> 可直接用项目 cache/zhb/zhb_*.zip 喂给 AxData 计算（零额外下载）
> **V16.3 O 补齐**：2026-08-06 local 模式实测 `code='600519'` 返回 34 列全量（下表）。

| 字段 | 含义 | 公式/说明 |
|:---|:---|:---|
| instrument_id / symbol / tdx_code / exchange | 元数据 | 源端标识 |
| stats_date | 统计基准日 | - |
| open_price / pre_close | 开盘价 / 昨收盘 | - |
| open_change_pct | 开盘涨跌幅 | % |
| open_amount / open_volume_hand | 开盘金额 / 开盘量 | 手 |
| open_volume_ratio | 开盘量比 | 开盘量 / 近5日平均每分钟成交量 |
| open_turnover_z | 开盘换手Z | 开盘量 / 流通股本Z × 100 |
| open_prev_amount_ratio | 开盘昨比 | 开盘金额 / 昨成交额 × 100 |
| auction_prev_volume_ratio | 竞价昨比 | 今开盘量 / 昨开盘量 |
| opening_rush | 开盘抢筹 | 实时快照携带 |
| open_prev_seal_ratio | 开盘昨封比 | 开盘金额 / 昨封单额 × 100 |
| prev_amount / prev_seal_amount / prev2_seal_amount | 昨成交额 / 昨封单额 / 前封单额 | 负值=昨收盘跌停封单 |
| prev_open_volume_hand / prev_open_amount | 昨开盘量 / 昨开盘金额 | 手 / 元 |
| float_shares / float_market_value | 流通股本 / 流通市值 | 全部流通口径 |
| free_float_shares / free_float_market_value | 流通股本Z / 流通市值Z | 自由流通口径 |
| seal_amount | 封单额 | 元 |
| seal_to_amount_ratio | 封成比 | 封单额 / 当前成交额 |
| seal_to_float_ratio | 封流比 | 封单额 / 流通市值Z × 100 |
| seal_prev_ratio | 封昨比 | 当前封单额 / 昨封单额 |
| limit_stat_days / limit_up_count_in_stat_days | 几天几板统计 | - |
| limit_board_text | 几天几板文本 | 如 "7天5板" |
| limit_up_streak_days | 连板天数 | - |
| year_limit_up_days | 年涨停天数 | - |

> **与 ZHB 对照**：`free_float_shares`（流通股本Z）与 ZHB Col[11]=FreeLtgb（自由流通股本，2026-08-04 官方确认）**同语义**——可交叉校准

#### 12.12.2 实时快照 41 字段（stock_realtime_snapshot_tdx）🆕

> 通达信实时快照，含 push2 没有的**派生指标**：
> **V16.3 O 补齐**：2026-08-06 local 模式实测 `code='600519'` 返回 41 列全量（下表）。

| 字段 | 含义 |
|:---|:---|
| instrument_id / symbol / tdx_code / exchange | 元数据 |
| last_price / pre_close / open / high / low | 现价 / 昨收盘 / 开盘价 / 最高价 / 最低价 |
| change / change_pct | 涨跌额 / 涨跌幅 |
| open_change_pct | 开盘涨跌幅 |
| high_change_pct / low_change_pct | 最高涨跌幅 / 最低涨跌幅（相对昨收盘）|
| amplitude_pct | 振幅% |
| average_price / average_change_pct | 均价 / 均价涨跌幅 |
| drawdown_pct | 回头波（最高价-现价）/昨收盘 |
| attack_pct | 攻击波（现价-最低价）/昨收盘 |
| volume / current_volume | 总成交量 / 当前盘口量 |
| amount | 成交额 |
| inside_volume / outside_volume / inside_outside_ratio | 内盘 / 外盘 / 内外比 |
| open_amount / open_amount_ratio_pct | 开盘金额 / 开盘占比 |
| bid1_price / bid1_volume / ask1_price / ask1_volume | 买一价量 / 卖一价量 |
| locked_amount | 封单额（买一价×买一量×100）|
| bid1_ask1_volume_diff / bid1_ask1_balance_pct | 买一卖一量差 / 占比 |
| rise_speed | 涨速 |
| short_turnover | 短换手 |
| min2_amount | 近2分钟成交额 |
| opening_rush | 开盘抢筹 |
| vol_rise_speed | 量涨速 |
| entrust_ratio | 委比 |
| activity | 活跃度 |

#### 12.12.3 涨跌停价格 15 字段（stock_daily_price_limit_tdx）🆕 官方规则枚举

> **V16.3 O 补齐**：2026-08-06 local 模式实测 `code='600519'` 返回 15 列全量（下表）。

| 字段 | 含义 |
|:---|:---|
| trade_date | 交易日 |
| instrument_id / symbol / tdx_code / exchange | 元数据 |
| name | 股票名称 |
| name_flag | 名称标记（N/C/ST/*ST）|
| pre_close_trade_date | 昨收盘所在交易日 |
| pre_close | 昨收盘 |
| pre_close_source | tdx_realtime_snapshot 或 tdx_daily_kline |
| limit_up_price / limit_down_price | 涨停价 / 跌停价 |
| limit_ratio_pct | 涨跌停比例 |
| **limit_rule** | **计算规则枚举：`main_10pct` / `st_5pct` / `chinext_20pct` / `star_20pct` / `bse_30pct` / `ipo_first_day` / `ipo_first_5_days`** |
| limit_status | normal / no_price_limit / missing_pre_close |

> **⚠️ 2026-08-05 规则修正（V16.1.8）**：AxData 文档枚举 `st_5pct` 为**旧快照**——用户确认**最新规则 ST 涨跌幅已放宽至 10%**（与主板一致，判定阈值 9.5）。
> 项目 `is_limit_up/is_limit_down` 已按最新规则调整：ST 与主板同走 9.5/-9.5；北交所 30%（29.5 判定）、创业板·科创板 20%（19.5 判定）。
> **对项目价值**：limit_rule 枚举的 `bse_30pct`（北交所）与 `ipo_first_day`（IPO 首日）仍可参考；`st_5pct` 不再采用

#### 12.12.4 综合评分 15 字段（stock_score_summary_tdx）🆕

> **V16.3 O 补齐**：2026-08-06 local 模式实测 `code='600519'` 返回 15 列全量（下表）。

| 字段 | 含义 |
|:---|:---|
| instrument_id / symbol | 元数据 |
| date | 评分日期 |
| score | 源端综合评分 |
| industry_rank / industry_rank_total | 行业排名 / 总数 |
| market_rank / market_rank_total / market_win_pct | 市场排名 / 总数 / 打败A股百分比 |
| capital_score / fundamental_score / news_score / theme_score | 资金 / 基本面 / 消息 / 主题 四维评分 |
| industry_name / stock_name | 行业名 / 股票名 |

#### 12.12.5 筹码分布 8 字段（stock_chip_distribution_tdx）🆕

> **V16.3 O 补齐**：2026-08-06 local 模式实测 `code='600519'` 返回 8 列全量（下表）。

| 字段 | 含义 |
|:---|:---|
| instrument_id / symbol | 元数据 |
| date | 统计日期 |
| profit_ratio_pct | 获利比例（%）|
| cost90_concentration / cost90_range | 90% 成本集中度 / 区间 |
| cost70_concentration / cost70_range | 70% 成本集中度 / 区间 |

> 项目完全空白维度（lng/med 筹码分析可补）

#### 12.12.6 每日股本盘前 10 字段（stock_daily_share_tdx）🆕

> **V16.3 O 补齐**：2026-08-06 local 模式实测 `code='600519'` 返回 10 列全量（下表）。

| 字段 | 含义 |
|:---|:---|
| trade_date | 交易日 |
| instrument_id / symbol / tdx_code / exchange | 元数据 |
| total_share / float_share | 总股本 / 流通股本（财务快照，股）|
| **free_float_share_z** | **流通股本Z（自由流通口径）——与 ZHB Col[11] 同语义** |
| finance_updated_date | 财务快照更新日期 |
| share_source | 股本来源（财务快照/盘前）|

#### 12.12.7 其他高价值接口（字段密度排行）

| 接口 | 字段数 | 价值 |
|:---|:---:|:---|
| stock_allotment_cninfo（配股）| 59 | 巨潮配股全字段 |
| option_chain_tdx（期权T型）| 55 | 期权层（项目⏸️）|
| stock_share_change_cninfo（股本变动）| 46 | 巨潮股本 |
| stock_realtime_rank_tdx（实时榜单）| 42 | 全市场榜单 |
| concept_capital_flow_tdx（题材资金走势）| 6 | **题材级资金流**（项目只有板块级）|
| stock_theme_strength_rank_tdx（题材强度排行）| 18 | 题材强度 |
| stock_financial_diagnosis_tdx（财务诊断）| 11 | F10 诊断 |
| stock_forecast_consensus_tdx（盈利预测）| 14 | 一致预期 |
| 新浪 ESG ×5（MSCI/华证/秩鼎/路孚特）| 6-13 | **ESG 评分**（项目空白）|
| 新浪期权 ×21 | 6-29 | 期权层 |
| 开盘红复盘 ×3（天梯/事件流/涨停复盘）| 9-19 | 与 levistock §12.10.4 同源 |

---

### 12.20 FTShare MCP（✅ 已采纳——2026-08-25 实测+接入统一层与采集脚本）🆕

> **来源**：https://github.com/FTShare-Lab/FTShare-MCP （MIT；MCP Streamable HTTP 网关，
> 公共地址 `https://market.ft.tech/gateway/mcp`；另有 FTShare-python-sdk 编程通道）
> **规模**：207 工具 = 202 数据 + 5 便捷入口；服务版本 0.1.1；只读；统一 structuredContent 信封。
> **性质判定**：**上游聚合网关**——工具名与目录显示聚合了东财（board/flow/rank 族）、
> 同花顺（ths_board_*）、雪球（xueqiu_rank）、百度（财经日历）、华尔街见闻（日历）等上游。
> ⚠️ 接入形态为 MCP 协议(JSON-RPC)而非纯 REST；鉴权/配额/计费未在 README 声明
> （tools/list 含 _meta.securitySchemes → 部分工具需鉴权）；**接入前必须实测配额与稳定性**。

**对字典的增量盘点（2026-08-25 查重结论）**：

| 分级 | 能力 | 字典现状 |
|:---|:---|:---|
| 🆕 全新维度 | **千股千评族×5**（评分/意愿度/关注度/机构参与度） | 字典无 |
| 🆕 全新维度 | **涨跌停事件时间线(3s 级)** + **DAEC 日内涨跌停分布历史** | 字典无 |
| 🆕 全新维度 | **商誉族×5**（行业/市场总览/预测/个股明细/减值） | 字典无（lng 仅资产负债表商誉科目自算占比） |
| 🆕 全新维度 | **董监高族×4**（持股变动/增持排名/减持排名/东财增减持）+ 一致行动人明细 | 字典无（lng 减持走公告关键词弱口径） |
| 🆕 全新维度 | **股权质押明细/汇总**、业绩快报、停牌列表、非凸评级 Top5、语义新闻搜索 | 字典无 |
| 🔄 已知字段新源 | 股东人数(TDX/巨潮403→第三源)、限售解禁(datacenter→第二源)、十大流通股东/十大股东、业绩预告(get_yjyg_all→第二源)、两融明细、涨停池族(push2ex/fuyao→第三源)、集合竞价结果(fuyao auction→同源异构)、复权因子(fuyao→第二源) | 多源补强 |
| 🔌 push 替代候选 | **DAEC 全市场快照族×8**（沪/深/北分市 A 股行情快照+历史 OHLC+昨收盘）——若盘后 T 日可用，可作 push2delay ulist 的替代通道（呼应 V17.0.7 push 退化主题） | ⏳ 需实测 |
| 🔄 死源复活 | 雪球排名（已死清单"免登录需 token"——经 FTShare 代理恢复排名维度） | 部分 |
| ➖ 项目不需要 | 宏观 17 工具（V17.0.5 P1-4 结论：宏观层暂不需要）、港股/美股/期货/债券/ETF/现货/外汇/公募基金(fuyao fund/* 已覆盖核心)、南向资金 | 维持 |

**已知字段对照警示**：其"集合竞价结果"与 fuyao auction 同类（须做 ZHB[9]/[14] 互锁后再定口径）；
"东财板块成份/K线"与 push2 clist 同上游（无新增信息量，仅接入面变化）。

**接入前置条件**：①MCP client 或 python-sdk 二选一；②tools/list 核对各工具
inputSchema/outputSchema 与配额；③优先实测 DAEC 快照族（push 替代价值最高）与
千股千评/商誉/质押三个全新维度。

**🔬 最小实测结果（2026-08-25 盘中，公共网关 JSON-RPC 直调 ~15 次，无 SDK/无鉴权）**：

| 工具 | 结果 | 关键发现 |
|:---|:---|:---|
| `ft_stock_comment_score_em` | ✅ 可用 | symbol=**6位纯代码**（600519✓/SH600519 与 .XSHG ✗）；返回**日频评分序列**（diagnose_date+total_score，茅台 64 期≈3个月）——散户情绪趋势新维度 |
| `ft_stock_comment_em` | ✅ 可用 | 全市场分页 5195 只：close/change_rate/**pe_dynamic/prime_cost 主力成本/focus 关注度/org_participate 机构参与度**/rank/total_score |
| `ft_limit_up_pool_yesterday` | ✅ **可用且富于 push2ex** | 昨日涨停池 64 只：first_limit_up_time/**limit_up_break[] 炸板时间点数组/limit_up_enter[] 回封数组**/break_count/status(今日续封标记)——晋级率与断板分析直接可用 |
| `ft_daec_prev_closes` | ✅ 可用 | 昨收盘序列与本机 K线**逐字等**（600519 五日全中） |
| `ft_daec_market_snapshot` | ⚠️ 口径修正 | 非"全市场个股快照"，实为**市场级涨跌分布聚合**（down_limited 等 8 桶+两市额量）——mak 情绪看板素材 |
| `ft_daec_stocks_all` | ⚠️ 半可用 | 个股行情 **31 字段**（OHLC/pe_ttm/market_cap/st/listing_date/**change_rate_day5~120/ytd 区间涨跌幅族**）；但 **filter/order_by 服务端实测无效**（order_by market_cap desc 返回乱序）、分页上限 200（全市场需 28 页）→ **替代 ulist 批量不成立**，适合单股深查；待上游修复后重估 |
| `ft_limit_event_timeline_3s` | ⚠️ 样本不足 | 000657@20260806 返回全 null（该日非涨停日，样本选择不当），换真实涨停日复核 |

**🔬 全字段实弹采样（2026-08-25 第二轮，154 工具 → 85 可用）**：

> 工程发现：①**会话 TTL≈2小时**——过期后所有调用静默返回空，客户端必须自动 re-init
> （首轮采样全灭的根因）；②无鉴权确认；③失败分类：MISSING_PARAMETER(需专用参数)/
> INVALID_ARGUMENT(kline 族需 start_time+count)/UPSTREAM_UNAVAILABLE(瞬态可重试)。
> 全量字段镜像：**[docs/verify/ftshare_fields_mirror.md](verify/ftshare_fields_mirror.md)**（85 工具×实际响应首行字段表）

**高价值 A 股工具字段表摘录**（完整版见镜像）：

| 工具 | 字段数 | 字段 |
|:---|:-:|:---|
| ft_stock_comment_em | 13 | change_rate/close_price/**focus 关注度**/**org_participate 机构参与度**/pe_dynamic/**prime_cost 主力成本**/rank/name_abbr/seq/**total_score 综合评分**/trade_date/turnover_rate |
| ft_stock_comment_desire_em | 6 | participation_wish 参与意愿(+5days/+change 变体) |
| ft_stock_comment_focus_em | 6 | market_focus/market_focus_rank(全市场排名)/total_market |
| ft_limit_up_pool_yesterday | 9 | first_limit_up_time/**limit_up_break[] 炸板时间点数组/limit_up_enter[] 回封数组**/break_count/status(今日续封) |
| **ft_limit_event_timeline_3s** | 15 | 涨跌停双向事件时间线：up/down 各自 break[]/enter[]/price/**limit_down_seal_value 跌停封单额** |
| ft_stk_premarket | 10 | ts_code/up_limit/down_limit/pre_close/price/float_mv/total_mv/shares |
| ft_auction_results | 8 | OHLC/volume/amount/**vwap 竞价均价** |
| **ft_stock_ggmx_handler** | **26** | 董监高持股变动全维：changer/relation/position/change_direction/quantity/ratio/change_reason/avg_price/shares_after/notice_date/source… |
| **ft_stock_unlock_by_date_handler** | **17** | 解禁按日：unlockDate/freeSharesType/freeRatio/liftMarketCap/newPrice/a20/b20Adjchrate/holderCount/holders[] 持有人明细 |
| **ft_stock_filter** | **21** | 服务端筛选器：OHLC/change_rate/day5~ytd 区间涨跌幅族/board/type/volume/turnover |
| **ft_risk_warning_stock_quotes** | **44** | ST 股全行情：五档 bids/asks、委托计数、cum_adjust_factor、day5~ytd 族、risk_type |
| ft_get_eastmoney_dapan_flow | 16 | 大盘资金流：main/xlarge/large/mid/small 净额+占比 × 沪深指数对照 |
| ft_xueqiu_rank | 6 | normalized_symbol/raw_symbol(SH 前缀)/rank_no/metric_value/latest_price |
| ft_suspension_list | 4 | symbol/suspension_type(full-day)/suspend/resume_time |
| ft_goodwill_stock_detail | 10 | goodwill_scale/goodwill_to_net_assets_ratio/net_profit_scale/net_profit_yoy_ratio |
| ft_ths_board_list | 3 | code/module(concept)/name——同花顺板块目录 REST 化 |

**新维度定级建议**（脚本采纳评估）：千股千评五工具=散户情绪面全新维度（sht 十四章候选）；
ggmx 26 字段=lng 九之二减持的结构化升级；unlock_by_date 持有人明细+20 日涨跌率=
lng 解禁压力评估升级；stock_filter 表达式待上游修复后可承接 val 部分扫描。

**✅ 采纳落地（同日）**：统一封装 **stock_common/sc_ftshare.py**（会话 TTL 自动续期+
SSE 解析+代码双格式转换）；sc_network 注册 market.ft.tech @2rps；采集脚本新增
`collect_ftshare`（个股×6 族+市场级 7 项，~126 请求≈66s）；sht 十四章消费千股千评+
昨日涨停池晋级统计；lng 九之二消费董监高结构化+商誉交叉核验。
**实测结论**：①接入形态可行（无鉴权即可调用，SSE+UTF-8 解码注意点已记录）；②千股千评族/
昨日涨停池/事件时间线为字典外真新增维度，具备 sht/mak 消费价值；③DAEC 批量替代
push2delay ulist **不成立**（分页上限+filter 失效），维持 V17.0.7 层级结论；
④配额限制本次未触发（15 次调用），长期配额仍未知。

#### 12.20.1 FTShare 股吧/评论原始字段补录（V17.1.1 全量登记）

> `raw_ftshare.json` 真实返回 6 叶（`comment_*`/`ggmx`/`goodwill_detail`），源=FTShare 股吧评论/商誉明细工具。§12.20 主表以工具名（`ft_stock_comment_score_em`→`total_score` 等）登记，原始叶名未在此列出，补录如下：

| 原始叶 | 含义(最佳已知) | 对应 FTShare 工具 | 状态 |
| :--- | :--- | :--- | :---: |
| comment_score | 评论情绪总分 | ft_stock_comment_score_em | ✅ 已接入 |
| comment_desire | 评论看多欲望 | ft_stock_comment_desire_em | ✅ 已接入 |
| comment_focus | 评论关注度 | ft_stock_comment_focus_em | ✅ 已接入 |
| comment_org | 机构评论 | ft_stock_comment_org_em | ✅ 已接入 |
| ggmx | 高管增持明细 | ft_stock_ggmx_em | ✅ 已接入 |
| goodwill_detail | 商誉明细 | ft_goodwill_stock_detail | ✅ 已接入 |

> 注：原始叶名与 §12.20 工具输出键（total_score 等）为同一字段的不同命名层；统一层 `sc_ftshare.py` 已做映射，本表补全源原始字段登记。

### 12.21 开盘啦 App 数据解析工具（✅ 实测可接入——无 Token 可用，2026-08-26 盘中穷尽测试）🆕

> **来源**：https://github.com/Rainynitesky/kaipanla-data-parser （MIT，61⭐）
> **性质**：mitmproxy 流量拦截 + Android 模拟器(MuMu) 抓包开盘啦 App 私有 API。
> **与已有源的关系**：KPL 数据已通过 levistock §12.10 + 直接 API §12.17 覆盖核心功能；
> 本仓库的增量价值在于暴露了更多未在 HTTP API 中公开的字段定义和 Socket 协议细节。
> ⚠️ 接入门槛极高：需 Android 模拟器 + mitmproxy 抓包 + Token 管理(过期需重新抓包) +
> Dalvik UA 校验 + 多域名分工(apphwshhq/applhb/apphis)。不适合脚本自动化场景。

#### 12.21.1 ZhiShuStockList_W8 个股详情完整 63 字段定义表（最有价值的发现）

> 域名必须用 `apphis.longhuvip.com`；Type 参数需遍历 0~19 合并去重才是完整个股列表。
> 来源：kaipanla-data-parser README + crawler_batch.py 列名定义交叉确认。

| 索引 | 字段名 | 含义 | 单位 | 对应项目字段 | 独有 |
|:--:|:---|:---|:---:|:---|:---:|
| [0] | code | 股票代码 | — | code | |
| [1] | name | 股票名称 | — | name | |
| [4] | board_tag | 所属板块标签 | — | industry | |
| [5] | price | 现价 | 元 | price(f43/tx3) | |
| [6] | change_pct | 涨跌幅% | % | change_pct(f170/tx32) | |
| [7] | amount | 成交额 | 元 | amount_wan(f48/tx37) | |
| [8] | real_turnover_rate | ★实际换手率% | % | — | 🆕 |
| [9] | speed | 涨速 | — | speed(tx80) | |
| [10] | actual_float_mv | 实际流通市值 | 元 | circ_mv(f117) | |
| [11] | main_buy | 主力买入额 | 元 | fund_buy(f138) | |
| [12] | main_sell | 主力卖出额 | 元 | fund_sell(f139) | |
| [13] | main_net | 主力净额(≡主力净买入额) | 元 | fund_net(f137) | |
| [18] | sell_flow_ratio | 卖流占比 | % | — | |
| [19] | net_flow_ratio | 净流占比 | % | — | |
| [20] | period_change | 区间涨跌幅 | % | change_5d/20d | |
| [21] | vol_ratio | 量比 | — | vol_ratio(f50/tx49) | |
| [23] | limit_pattern_text | 几天几板(如"3天2板") | 文本 | Col[31]+Col[33] | 🆕 |
| [25] | turnover_pct | 换手率% | % | turnover_pct(f168) | |
| [28] | close_seal_amount | 收盘封单额 | 元 | zt_seal_amount(stat2[4]) | |
| [29] | max_seal_amount | 最大封单额 | 元 | max_seal_amount(fuyao seal_map) | |
| [33] | amplitude | 振幅% | % | amplitude(f171/tx43) | |
| [37] | total_mv | 总市值 | 元 | mcap_yi(f116) | |
| [38] | circ_mv | 流通市值 | 元 | float_mcap_yi(f117) | |
| [40] | lead_count | 领涨次数 | 次 | — | 🆕 |
| [42] | inst_increase_q1 | 机构增仓Q1金额 | 元 | — | 🆕 |
| [50] | big_order_net_3m | 300万以上大单净额 | 元 | — | 🆕 |
| [53] | pb | 市净率 | 倍 | pb(f167) | |
| [58] | popularity_value | 人气值 | — | em_hot 相关 | 🆕 |
| [59] | popularity_rank_chg | 人气排名变化 | — | em_hot 相关 | 🆕 |
| [60] | pe_dynamic | 动态PE（最新报告期年化） | 倍 | `pe_mrq`(**f162**) | 🔴2026-09-01 二次重裁定；✅ 已由开盘啦 W8 \*ST湘邮 600476 全字段实测 `[60]=市盈率（动）145.44` 终验（见 §12.21 尾部实测表），与 f162=动态 完美对应 |
| [61] | pe_ttm | PE(TTM) | 倍 | `pe_ttm`(**f164**) | ✅ 未变；✅ 开盘啦实测 `[61]=市盈率TTM` 对应 f164 |
| [62] | pe_static | 静态PE（上年度年报 LYR） | 倍 | `pe_lyr`(**f163**) | 🔴2026-09-01 二次重裁定；✅ 开盘啦实测 `[62]=市盈率（静）` 对应 f163 |

> 🔴 **2026-09-01 二次重裁定（推翻 2026-08-31 那次订正）**：
> - `f162` = `pe_mrq` = **动态**PE（现价÷最新报告期年化EPS）→ 对应开盘啦 **[60] `pe_dynamic`**
> - `f163` = `pe_lyr` = **静态**PE（现价÷f160 年报EPS）→ 对应开盘啦 **[62] `pe_static`**
> - `f164` = `pe_ttm` = **TTM** PE → 对应开盘啦 **[61] `pe_ttm`**
> - 即上表 **[60]/[61]/[62] 的语义名与 push2 编号对应关系，2026-08-31 订正为 `f163/f164/f162`，
>   现改回 `f162/f164/f163`**——与 2026-08-06 快照**旧约定的编号映射一致**（旧约定 `f162=动态/f163=…` 中
>   "f162=动态"这半句本来就是对的，2026-08-31 误改）。
> - 证据链：fuyao 120/120 + 闭式反推 120/120 + TTM 自洽(差0.0000) + 同花顺官方配置 `806289408`=市盈(动)`pe_mrq` + 披露日跳变实验；
>   死证 `f162==现价÷f160` 0/120、`f163==现价÷(f55×2)` 0/120。
> - **完整铁证见 §12.8.12e 后【PE 口径铁证】。**

**★独有维度汇总**（push2/fuyao/ZHB/TDX 均无法获取）：
- [8] 实际换手率%：区别于普通换手率——可能按自由流通股本计算
- [23] 几天几板文本描述（如"3天2板"，含非连续涨停信息）
- [40] 领涨次数：该股在板块内领涨的累计次数
- [42] 机构增仓Q1金额：基金季报披露的机构增持数据
- [50] 300万以上大单净额：大单阈值与东财不同
- [58]/[59] 人气值及排名变化：KPL 自有人气算法

#### 12.21.2 GetPanKou 板块盘口 12 字段

成交额/换手率/主力净额/上涨家数/下跌家数/强度。

#### 12.21.3 SonPlate_Info 子板块层级

父板块 → 子板块列表 [[代码, 名称, 强度], ...]

#### 12.21.4 Socket Protobuf 实时推送

volRatio=量比, institutionIncrease=机构增仓 仅在 Socket 推送中——HTTP API 无此字段。

#### 12.21.5 无 Token 穷尽实测（2026-08-26 盘中，jinhao2003 方法验证）✅

> **重大发现**：开盘啦 API 大部分端点无需 Token 即可调用——
> 直接 HTTP POST + Dalvik UA 即可。不需要 Android 模拟器/mitmproxy。
> 参考 jinhao2003/kaipanla-crawler (141⭐) 实现。

| Action | Controller | 域名 | 状态 | 说明 |
|:---|:---|:---|:---:|:---|
| GetInfo | Index | apphwhq | ✅ | 首页聚合 ErBanList/JJJYList/TKGKList |
| MarketStockZDNum | HomeDingPan | apphwhq | ✅ | 涨跌家数 |
| **ChangeStatistics** | HomeDingPan | apphwhq | ✅ | 市场情绪 ztjs=52涨停/df_num=7跌停/strong=55强度/lbgd=5连板高度 |
| RiseFallAnalysis | HomeDingPan | apphwhq | ✅ | 涨跌分析 |
| RealRankingInfo | ZhiShuRanking | apphis | ✅ | 板块排行30只/页 |
| **ZhiShuStockList_W8** | ZhiShuRanking | apphis | ✅ | **63字段个股详情** 无Token可用 |
| **GetYTFP_BKHX** | FuPanLa | apphis | ✅ | 复盘啦板块核心(涨停原因+题材) |
| **GetYTFP_SCTD** | FuPanLa | apphis | ✅ | 复盘啦市场题材(几天几板 Tips) |
| GetStockList | LongHuBang | applhb | ✅ | 龙虎榜58条 |
| SharpWithdrawal | HisHomeDingPan | apphwhq | ❌ | JSONDecodeError 需 Token |
| GetDayNewHigh_W28 | StockNewHigh | apphwhq | ❌ | 同上 |
| DailyLimitPerformance | HisHomeDingPan | apphwhq | ❌ | 同上 |
| GetPanKou | ZhiShuL2Data | apphwhq | ❌ errcode=1020 | 需 UserID/Token |

**结论**: 9/22 无 Token 可用，覆盖 sht/mak 核心数据需求。
采纳评估从⏸️升级为✅。

接入需 AES 解密+签名计算(libsockSign.so)，门槛极高。

> 📌 **重要提示**：本文件是项目的**关键字典**，所有数据接口与字段调整前必查。优先采用字典中已确定的内容，可大幅减少重复反向工程工作。


#### 12.12.8 跨源接口实测确认（2026-08-05，axdata 0.1.3 local 模式）

> **方法**：`request_interface(name, params=..., fields=None, persist=False, data_root=None)` 逐个实测（串行+2s 间隔）
> **原则**：测试确认真实有效即录入（无论项目是否使用）——为后期脚本升级提供现成接口
> **注意**：参数名以 AxData 实际校验为准（常见差异：symbol↔code、date↔trade_date）

**腾讯财经（5/6 ✅）**：

| 接口 | 实测 | 关键字段 |
|:---|:---:|:---|
| stock_zh_a_hist_tx（A股历史日线）| ✅ 120 根 | trade_date/open/close/high/low/volume/amount/adjust |
| stock_zh_index_daily_tx（指数日线）| ✅ 120 根 | 同上（指数）|
| stock_zh_a_tick_tx_js（逐笔）| ✅ 10 条 | trade_time/price/change/volume/amount/**trade_side** |
| get_tx_start_year（历史起始年）| ✅ | start_date/source_value |
| tencent_realtime_snapshot（实时快照）| ✅ | last_price/pre_close/open/high/low/change/quote_time |
| stock_zh_a_spot_tx（全市场列表）| ❌ 参数特殊 | sort_type/direction/offset（列表接口）|

**财联社（8/10 ✅）**：

| 接口 | 实测 | 关键字段 |
|:---|:---:|:---|
| cls_market_emotion（市场情绪）| ✅ | market_degree/shsz_balance/up_ratio/up_open_num/performance/rise_num/fall_num |
| cls_limit_up_pool（涨停池含原因）| ✅ 139 条 | secu_code/secu_name/last_price/change_pct/**up_reason** |
| cls_sector_heat（板块热度）| ✅ 20 条 | plate_code/rank/cur_heat/rank_change/is_new |
| cls_market_wind（风口板块）| ✅ 3 条 | plate_code/plate_name/**catalyst** |
| cls_sector_industry（行业实时）| ✅ 54 条 | change_pct/main_fund_diff/rise_count/fall_count/limit_up_count |
| cls_sector_rotation（板块轮动）| ✅ 40 条 | trade_date/plate_code/plate_name/change_pct/rank |
| cls_market_mainline（主线机会）| ✅ 3 条 | block_key/title/summary |
| cls_news_telegraph（电报）| ✅ 5 条 | news_id/title/content/publish_time/category |

**开盘红（4/4 ✅）**：

| 接口 | 实测 | 关键字段 |
|:---|:---:|:---|
| kph_market_emotion（情绪）| ✅ | limit_up_count/real_limit_up_count/**st_limit_up_count**/rise_count/fall_count/market_sign |
| kph_sector_ranking（板块排行）| ✅ 50 条 | plate_id/change_pct/amount/net_inflow/turnover_rate/market_cap/stock_count |
| kph_limit_up_history（历史涨停复盘）| ✅ 50 条 | limit_time/open_time/**seal_amount/seal_money**/limit_tag/limit_count/themes/reason |
| kph_limit_ladder（涨停天梯）| ✅ 137 条 | limit_count/limit_time/plate_name/**one_word/popular**/plate_limit_up_count/amount |

**东财（8/8 ✅）**：

| 接口 | 实测 | 关键字段 |
|:---|:---:|:---|
| eastmoney_stock_realtime_snapshot | ✅ | last_price/change_pct/volume/amount/amplitude/turnover_rate/pe_ttm/volume_ratio |
| eastmoney_limit_up_pool（涨停池）| ✅ 138 条 | last_price/**limit_price**/change_pct/float_market_value/first_limit_time/last_limit_time |
| eastmoney_yesterday_limit_up_pool（昨涨停）| ✅ 75 条 | 22 字段（含 limit_price/连续涨停）|
| eastmoney_stock_changes（盘口异动）| ✅ 2792 条 | change_time/change_pct/**change_type/change_type_name** |
| eastmoney_dragon_tiger_daily（龙虎榜）| ✅ 50 条 | reason/close_price/change_pct/buy_amount/sell_amount/**net_buy_amount** |
| eastmoney_margin_trading（两融）| ✅ 24 条 | margin_balance/margin_buy_amount/**margin_net_buy_amount**/short_balance/short_sell_volume |
| eastmoney_sector_realtime（板块）| ✅ 100 条 | sector_code/change_pct/amount/main_inflow/lead_stock_name |
| eastmoney_stock_sector_belong（所属板块）| ✅ | sector_name |

**巨潮（4/6 ✅）**：

| 接口 | 实测 | 关键字段 |
|:---|:---:|:---|
| stock_profile_cninfo（公司概况）| ✅ 29 字段 | company_name/english_name/former_short_name/a_share_code/h_share_code/selected_indexes |
| stock_dividend_cninfo（历史分红）| ✅ 31 条 | announcement_date/bonus_share_ratio/transfer_share_ratio/cash_dividend_ratio/record_date/ex_right_date |
| cninfo_announcements（公告）| ✅ 30 条 | announcement_id/title/publish_date/file_type/file_size_kb/**download_url** |
| stock_irm_cninfo（互动易）| ⚠️ 空返回 | 需参数核实 |
| stock_hold_num_cninfo（股东户数）| ❌ 403 | 源端风控 |
| cninfo_announcement_detail（PDF元信息）| ⚠️ 需 url 参数 | - |

**交易所（3/3 ✅）**：

| 接口 | 实测 | 关键字段 |
|:---|:---:|:---|
| stock_trade_calendar_exchange（交易日历）| ✅ 10 条 | cal_date/is_open/pretrade_date/next_trade_date |
| stock_basic_info_exchange（基础信息）| ✅ 27 字段 | name/security_full_name/market_code/industry/region/company_code |
| stock_historical_list_exchange（历史列表）| ✅ 119 万条 | trade_date/symbol/name/list_date/delist_date/listing_status |

**新浪（7/8 ✅）**：

| 接口 | 实测 | 关键字段 |
|:---|:---:|:---|
| stock_restricted_release_queue_sina（限售解禁）| ✅ 3 条 | release_date/**release_shares_10k/release_market_value_100m_yuan**/batch_no/announcement_date |
| stock_zh_index_spot_sina（A股指数实时）| ✅ 80 条 | latest_price/change_pct/bid/ask/open/high |
| stock_esg_rate_sina（ESG评级）| ✅ 10 条 | agency_name/**rating**/rating_period |
| stock_lhb_detail_daily_sina（龙虎榜）| ✅ 56 条 | rank/close/metric_value/volume_10k_shares/amount_10k_yuan/indicator |
| index_stock_cons_sina（指数成份）| ✅ 80 条 23 字段 | index_code/name/latest_price/change_pct/bid/ask |
| fund_etf_category_sina（ETF分类行情）| ✅ 100 条 17 字段 | fund_code/fund_type/latest_price/change_pct |
| stock_hk_index_spot_sina（港股指数）| ✅ 3 条 | index_code/latest_price/change_pct |
| stock_financial_report_sina（财务报表）| ⚠️ 参数待查 | - |

**实测总结**：腾讯 5/6 + 财联社 8/10 + 开盘红 4/4 + 东财 8/8 + 巨潮 4/6 + 交易所 3/3 + 新浪 7/8 = **39 个接口确认可用**。
**项目高价值补充**：东财盘口异动（change_type 中文名）、开盘红历史涨停复盘（seal_money/one_word）、新浪限售解禁（万股/百万元口径）、巨潮公告 download_url（PDF 直链）、财联社涨停池 up_reason（涨停原因）。


### 12.14 多源字段补齐矩阵（AxData 线索核对，2026-08-10）

> **666 个补录字段的完整矩阵见附录**：[docs/verify/axdata_verify.md](verify/axdata_verify.md)——按源组织（TDX 196/扩展 89/交易所 10/东财 12/巨潮 222/腾讯 2/新浪 115/财联社 8/开盘红 12）
> **方法**：clone electkismet/AxData@main 提取 256 接口/3334 字段定义，与字典按源比对；1235 字段同源同字段已印证（不重复录入）
> **高价值补录摘要**：TDX 估值分位（pb_percentile/pe_percentile/ps_ttm/peg）、一致预期（eps_year1-3）、分析师评级（target_price/buy_count）；
> 新浪 ESG 五源评分、龙虎榜聚合统计；巨潮配股 52 字段、股权质押；东财两融（margin_repay_amount/total_balance）、研报（rating_change）

### 12.15 数据源优先级矩阵（V16.1.7 统一数据层重构，V16.3 O18 修正排序，O37 新源插入）

> **原则（V16.3 O18 修正——依据参考仓库 v3.2 + 实测）**：
> **ZHB 一次性获取优先（零网络）→ TDX TCP / 腾讯（不封 IP，首选）→ 新浪/巨潮（低风险）→ 同花顺（有 401 反爬史）→
> AxData（local 未充分验证）→ 东财 HTTP（最难：45000/h 封禁 20h + 观察期 + 共享风控，仅独有数据，最后手段）**
> **实测验证**（2026-08-05，600519）：price/industry/concepts = realtime:tdx/tdx:boards（TCP 优先），pe_ttm/main_net_buy = zhb（ZHB 优先）

> **V16.3 O18b 数据获取模式维度（用户提出——难易度不只"封禁"，还有"批量效率"）**：
> 各源的**获取模式**不同——排序时要同时看"封禁风险"与"单次请求产出"：
>
> | 模式 | 特征 | 代表源 | 适用场景 |
> |:---|:---|:---|:---|
> | **逐股多字段** | 单请求=单股票全部字段（快照/财务/五档）| **TDX TCP**（0x0010/F10/quotes）、新浪单股接口 | **sht/lng/med**（单股深度报告）|
> | **批量单字段** | 单请求=多股票列表（一行一字段）| **腾讯批量**（60只/请求）、东财 ulist/clist | **val/mak**（全市场扫描）|
>
> **模式匹配铁律**：
> 1. **全市场扫描（val/mak）→ 批量接口**——绝不可逐股 TCP（7957 次 × 单股 = 数小时）；腾讯批量 60/批最优
> 2. **单股深度（sht/lng/med）→ TCP 逐股**——一次拿全字段；绝不可逐字段 HTTP（多次请求浪费）
> 3. **混合**（如 mak 板块聚合）：ZHB 本地一次性（批量）→ TDX boards（批量列表）→ 东财 clist（批量）——均批量模式
> 4. **同一字段两模式皆可时**（如 52周最高价低：腾讯批量带 [67]/[68] vs TDX 单股 K 线计算）——**按当前场景选模式**（val 用批量、sht 用单股）
>
> **现状符合性核查**：val/mak 全市场走腾讯批量 ✓（V15.5.9 起）；sht/lng/med 单股走 TDX TCP ✓；mak 板块 ZHB 旁路 ✓——**两模式均正确匹配**，无需改造，仅固化原则防未来回归。

#### 12.15.1 逐股链路优先级

| 数据 | L1 | L2 | L3 | L4 | 说明 |
|:---|:---|:---|:---|:---|:---|
| **行情** | ZHB（盘前/静态）| TDX/easy_tdx（TCP 实时）| 腾讯 qt.gtimg.cn | 东财 push2（最后）| push2 风控最严仅兜底 |
| **资金流** | ZHB tdxstat2（T-1）| **THS 主力净流入（盘中，正式账号无限频）** | 东财 push2 f137/f138/f139/f140/f141/f142/f143/f144/f145/f146 | - | O37 新增 THS 位（盘中实时主力——ZHB T-1 之外）；东财最后 |
| **行业** | TDX boards（TCP）| ZHB profile.dat | 东财 push2 f127（免费副产品）| - | O18 修正：push2 最后（原 f127 第一）|
| **概念** | ZHB tdxchain（本地）| TDX boards（TCP）| 东财 push2 f129（免费副产品）| - | O18 修正：ZHB 本地优先 |
| **财务** | TDX F10 财务分析（roe/毛利率/eps——@cached gross_margin_roe）| TDX 0x0010（净利/营收/股东户数——单位角 /10）| **THS 财务组（ROE TTM/净利营收增长率——单股一次）** | 新浪财务报表 | O37 新增 THS 位（ROE TTM 茅台 31.26% 实测）；ZHB 无 roe/毛利率 |
| **估值** | ZHB（pe_ttm/dividend_yield）| **THS（PB 市净率——ZHB 无——茅台 6.05 实测）** | TDX/腾讯 rt_quote | 计算（price/bvps）| O37 修订：PB 首选 THS（直接值 vs 计算兜底）——ZHB 无 PB |
| **股本** | rt_quote（实时合并）| ZHB | **THS（总股本/流通股本/市值——单股）** | sc_capital_cache | O37 新增 THS 位 |
| **52周/涨跌幅** | ZHB | 腾讯 [67]/[68]（元）| TDX K线计算 | - | O18 新增腾讯位（已破解）|
| **两融/股东户数** | 东财 datacenter（独有）| **THS（融资余额/融券/户均持股——单股）** | - | - | O37 新增 THS 备胎 |

#### 12.15.2 批量链路优先级（mak/val）

| 数据 | L1 | L2 | L3 | 说明 |
|:---|:---|:---|:---|:---|
| **全市场快照** | ZHB 一次性 | 腾讯批量 `_tencent_batch_fallback`（60只/批）| 东财 push2 批量（仅 ZHB+腾讯全失败）| V15.5.9 后腾讯批量替代逐股 push2（防连接级风控）|
| **行业板块** | ZHB 聚合 | TDX boards | 东财 clist | - |
| **板块强度/资金** | **KPL RealRankingInfo（强度/主力净额/今明 PE——匿名）** | 东财 clist（申万二级）| - | O37 新增 KPL 位（板块资金流盘中——开盘啦板块 80x——需名称映射）|
| **市场情绪** | **财联社 market_emotion_cls** | **开盘红 market_emotion_kph** | **KPL ChangeStatistics（strong/连板高度）** | O37 新增 KPL 三源互校（8/7：KPL strong 63/连板 4 = 东财/财联社涨停 74 一致）|
| **板块轮动** | **duanxianxia getPlateRotatData（N×天矩阵——ths 涨跌幅/kaipan 强度双口径）** | 本地 ZHB 聚合计算 | - | O37 新增（mak D 段轮动对照——医药 20846 与 KPL 同值交叉 ✓）|
| **涨停池** | 东财 push2ex（4 池，独有数据）| **KPL DailyLimitPerformance（连板梯队+涨停原因——匿名）** | levistock/AxData 补充 | O37 新增 KPL 位（涨停原因/封单/主力——东财之外第二源）|
| **涨停原因** | **KPL GetPlateInfo_w38 / GetKLineZhangTing（开盘啦详细原因——独有）** | 财联社 stock_zt_pool_cls（up_reason）| 同花顺 getharden（reason）| O37 新增 KPL 首位（详细长文原因）|

#### 12.15.3 V16.1.7 代码变更

1. `tdx_get_quote_full` pe_ttm 守卫修正：缺 pe_ttm 不再整体置空（保 price/change_pct，防丢 TCP 实时价导致链跳到腾讯/东财）
2. 资金流标签 `realtime:tdx` → `realtime:eastmoney`（名实相符）
3. 行业链删腾讯虚位级（get_tencent_quote 无 industry 字段，死级）
4. 概念链新增 push2 f129 兜底（get_em_quote_full 请求包 + 解析）

#### 12.15.4 O37 统一层跟进后的完整优先级（2026-08-09）

> **全源难易度最终排序（O18 基线上 O30-O37 新增）**：
> **ZHB（本地零网络）→ TDX TCP / 腾讯（不封 IP）→ 财联社/开盘红（低风险匿名）→ 板块轮动 duanxianxia（Referer 注入）→ KPL 开盘啦（longhuvip 匿名+示例 token——私有 API 风险）→ 新浪/巨潮（低风险）→ 同花顺（401 反爬史）→ AxData（封装——无独家数据）→ 东财（最难：45000/h 封禁 20h——仅独有数据）**
>
> **脚本落地（O37）**：
> - **mak A 段情绪**：财联社 → 开盘红 → KPL 三源互校（一源失败自动兜底）
> - **mak D 段轮动**：duanxianxia 矩阵（ths/kaipan 双口径）对照本地 ZHB 聚合
> - **val 策略 04 PB**：候选级 THS 批量补全（get_ths_market_snapshot 50/批——20s/200 候选）——替代计算兜底（更准）
> - **统一层函数**：get_kpl_market_sentiment/get_kpl_plate_strength/get_plate_rotation_matrix/get_ths_market_snapshot/get_ths_pb（§12.8.12b/§12.17/§12.18）

### 12.13 eltdx 完整方法字典（2026-08-05 文档确认，未实测）

> **来源**：https://github.com/electkismet/eltdx（303⭐，Research-Only 许可，2026-08-04 活跃）+ docs/METHOD_REFERENCE.md
> **定位**：在线协议客户端，74 个方法入口 / 115+ 可调用名（含别名），底层覆盖 0x054c/0x0547/0x052d/0x0537/0x0fc5/0x0fc6/0x056a/0x000f/0x0010/0x0452/0x06b9 等 + F10 走 7615/TQLEX HTTP 网关
> **状态标注**：本文档字段来自官方文档（方法级参考），**未实测**；如需接入项目需先实测核实
> **与 AxData 关系**：eltdx 为底层协议库，AxData 为其迭代（256 接口，Apache-2.0）——字段价值已被 AxData 覆盖

#### 12.13.1 行情快照（get_quote / get_snapshots）文档确认

| 字段 | 含义 |
|:---|:---|
| last_price / pre_close_price | 现价 / 昨收盘 |
| open_price / high_price / low_price | 开盘价 / 最高价 / 最低价 |
| total_hand / current_hand | 总成交量（手）/ 现手 |
| amount | 成交额 |
| inside_dish / outer_disc | 内盘 / 外盘 |
| open_amount_yuan | 开盘金额（元）|
| buy_levels / sell_levels | get_quote 买一~买五 / 卖一~卖五；get_snapshots 仅一档 |
| change / change_pct | 派生：涨跌额 / 涨跌幅 |
| sum_buy_vol / sum_sell_vol | 派生：五档买卖量合计 |

#### 12.13.2 财务批量（get_finance_batch，0x0010）文档确认

| 字段 | 含义 | 单位 |
|:---|:---|:---|
| updated_date / ipo_date | 财务更新日期 / 上市日期 | - |
| eps_raw | 每股收益原始值 | - |
| liu_tong_gu_ben_raw_float | 流通股本原始值 | **万股** |
| zong_gu_ben_raw_float | 总股本原始值 | **万股** |
| zong_zi_chan_raw_float | 总资产原始值 | **千元** |
| jing_li_run_raw_float | 净利润原始值 | **千元** |
| circulating_shares / total_shares | 派生：流通/总股本 | 股 |
| total_assets_yuan / net_profit_yuan | 派生：总资产/净利润 | 元 |

#### 12.13.3 除权除息（get_gbbq / get_xdxr，0x000f）文档确认

| 字段 | 含义 |
|:---|:---|
| date / category_name | 事件日期 / 类别名称 |
| c1_value~c4_value | 按类别解码的四个业务值 |
| fenhong / peigujia | 分红 / 配股价（XdxrRecord）|
| songzhuangu / peigu | 送转股 / 配股（XdxrRecord）|

#### 12.13.4 涨跌停限制（limits.special / scan_special，0x0452）文档确认

> **注意**：eltdx **无 get_price_limits 方法**；涨跌停价来自特殊品种涨跌停限制表

| 字段 | 含义 |
|:---|:---|
| limit_up_price / limit_down_price | 涨停价 / 跌停价 |

#### 12.13.5 K线（bars.get，0x052d）文档确认

| 字段 | 含义 |
|:---|:---|
| time / open / high / low / close | 时间 / OHLC |
| volume_lots | 成交量（手）|
| amount | 成交额 |
| up_count / down_count | 指数类上涨/下跌家数 |
| adjust | none/qfq/hfq/fixed_qfq/fixed_hfq（定点复权需 anchor_date）|
| period | 1m/5m/15m/30m/60m/day/week/month/quarter/year + 10m/2d/5s 自定义 |

#### 12.13.6 行情列表（quotes.list_by_category，0x054b）文档确认

> 含**涨速/短换手/2分钟金额/开盘抢筹/量涨速**等短线字段（与 AxData 实时快照 §12.12.2 同源）

| 字段 | 含义 |
|:---|:---|
| rise_speed / short_turnover | 涨速 / 短换手 |
| min2_amount / opening_rush | 近2分钟金额 / 开盘抢筹 |
| vol_rise_speed / locked_amount | 量涨速 / 封单额（=bid1×bid_vol1×100）|

#### 12.13.7 服务器统计资源（resources.read_stats，zhb.zip）文档确认 ⚠️重要

> 📋 原始实证见附录：[docs/verify/network_servers.md](verify/network_servers.md)（三源服务器清单 + 移动线路实测）。本 § 为决策层，原始清单在该附录。

> **与项目 ZHB 直接对应**：eltdx 同样消费 tdxstat.cfg/tdxstat2.cfg（zhb.zip）！

| TdxStatRow 字段 | 含义 |
|:---|:---|
| 60日 Beta / PE TTM | 与 ZHB tdxstat Col[2]=BetaValue / Col[9]=pe_ttm 同语义 |
| 自由流通股本 | 与 ZHB Col[11]=FreeLtgb 同语义 |
| 年内涨停数 / 连板统计 | 与 ZHB tdxstat 涨停相关字段 |

| TdxStat2Row 字段 | 含义 |
|:---|:---|
| 当日/前一日/前两日成交额、封单额 | 与 ZHB tdxstat2 amount/amount_1d/amount_2d 同语义 |
| 当日/前一日开盘量额 | 与 AxData 短线指标 prev_open_* 同源 |

#### 12.13.8 F10 方法概览（7615/TQLEX HTTP 网关，文档确认）

| 方法 | 返回内容 | 项目对应 |
|:---|:---|:---|
| stock_score | 综合评分/排名/资金基本面主题面评分 | AxData §12.12.4 |
| finance_diagnosis | 营运/盈利/成长/现金流/资产质量诊断 | AxData F10 |
| profit_forecast | EPS/归母净利润/营业收入预测 | reportapi |
| hot_topics / topic_compare | 题材名称/关联度/入选日期/原因/题材内对比 | push2 f129 / MacClient |
| northbound_holding | 沪深股通持股比例/数量/变动 | get_northbound_hold |
| theme_market | 题材行情/相关板块/成分股 | MacClient |
| valuation | PE/PB/市销率/市现率/估值百分位/市值 | push2 f162/f163/f164/f165/f166/f167 |
| business_composition | 主营收入/成本/毛利/占比/毛利率 | 新浪三表 |
| dividend_financing | 分红方案/股权登记日/除权派息日/股息率 | get_dividend_history |
| shareholder_change_plans | 股东增减持计划 | 巨潮公告关键词 |

#### 12.13.9 集合竞价/分时/成交（文档确认）

| 方法 | 主要字段 |
|:---|:---|
| auctions.series（0x056a）| matched_volume 虚拟成交量 / unmatched_volume / price |
| get_auction_0925 | 09:25 竞价结果（price/volume/amount）|
| minutes.today/history/recent | 分时（price/avg_price 均价/volume）|
| minutes.aux（0x051b）| 买卖力道 buy_commission/sell_commission / 成交对比 |
| trades.today/history | 逐笔（price/volume/side buy-sell-neutral/trade_amount_yuan）|

---

#### 12.15.5 实测后最终矩阵（2026-08-10——24 股全字段 + 7 接口 + push2delay/fuyao/腾讯 ROA 验证）

> **本轮实测改变排序的关键结论**：
> 1. **push2 主域连接风控实锤**（RemoteDisconnected 服务器主动断开，20h 冷却触发条件）——**东财链路统一 push2delay 优先**（114 字段全量可用、延时 15min 非盘中无影响、风控面独立）
> 2. **腾讯地位跃升**：88 字段（含 ROA=tx66 已确认、主力净流入=tx75、盘口价=tx85）+ ifzq K线（免费零封禁）——**行情/估值/ROA/K线 四合一首选**
> 3. **fuyao 官方 REST**：pe_ttm 20.385=腾讯 20.39 印证 ✓ + **涨停梯队 boards 独有结构**
> 4. **涨停数三源互校实锤**：复盘啦 99=财联社 99=KPL 99（8/10）
> 5. **THS SDK 盘后空**（23:16 全 query_key 空）——仅盘中可用
> 6. **tx66=ROA** 新维度（银行股精确：招行 1.12/工行 0.67）

**逐股链路（盘中/盘前分层）**：

| 数据 | 盘前(T-1) | L1(盘中) | L2 | L3 | L4 | 说明 |
|:---|:---|:---|:---|:---|:---|:---|
| **行情** | ZHB | TDX TCP | 腾讯 qt.gtimg | **push2delay** | push2(仅独有) | 4 源 24 股交叉 100% 一致；push2 最后 |
| **K线** | ZHB | TDX | **腾讯 ifzq**（免费零封禁）| 新浪 CN_MarketData | - | ifzq 实测=TDX 完全一致（12.1 补录）|
| **估值 pe/pb/股息** | ZHB(T-1 口径) | 腾讯(88 字段, **[53]=静态PE f163 L1**) | fuyao(官方印证) | push2delay(仅动态PE f162 兜底) | 计算 | 实时 pe_ttm 20.39=fuyao 20.385；🔴**静态PE(f163)=腾讯[53] L1(§12.8.12e 实锤, V17.0.23 批量接入, 逐股 get_tencent_quote 同步)——彻底脱离 push2**；push2delay 20.48 为延时口径 |
| **ROA** | - | **腾讯 tx66**（已确认）| - | - | - | 招行 1.12=年化 ROA 精确——新维度 |
| **PB** | - | THS(盘中) | 腾讯 [46] | push2delay f167 | 计算 price/bvps | 腾讯 7.24 vs push2delay 7.15（bps 时点差）|
| **资金流(主力净)** | ⚠️ ZHB tdxstat2 **已移出**(其资金流键=竞价额/量, 非主力) | 腾讯 tx75(仅兜底, 口径存疑) | THS(盘中) | **push2delay f137(主力净=超大单+大单, V17.0.16 重定案)** | push2 | 四档: f140=超大单/f143=大单/f146=中单/**f149=小单**; **f137=主力合计**; 5日=f178 聚合; 净量=TDX 0x0011。详见 §12.3.4 |
| **主力净(全市场批量)** | ulist.np/get 批量 **f62**(↔ push2 f137, 跨接口对撞 96.6%) | ZHB 竞价额(仅兜底标注语义) | - | - | - | **V17.0.16 重定案**: `f62` 已是主力净(实证 f62==f66+f72, 236/236)，**不再 +f66**；get_em_batch_quotes 只请求 f62; 失败回退 ZHB main_net_buy_amount×1e4(标注竞价额) |

> **⚠️ V17.0 腾讯 tx75 口径警示（2026-08-13 实测）**：tx75(主力净流入,亿)与东财 f137 **方向相反**——600519 同日 8/13: tx75=**-4.49 亿** vs f137=**+3.59 亿**(f135/f136=3.59 亿算术自洽)。**tx75 不可作主力净流入首选源**（统一层已降级为兜底, 主用 f137）; 若未来要用腾讯口径需先破解 tx75 真实语义（疑为"超大单净"或主动/被动口径差异）。
> **⚠️ V17.0 竞价族实锤（2026-08-14）**：ZHB tdxstat2 main_net_buy_amount/1d、main_net_buy_hands/1d 四键实为**竞价金额/竞价量**(今/昨)——[14] 恒正+占比<5% + [9]×开盘≈[14](15/17 铁证); 同花顺"早盘竞价量/金额"对应; 不可作主力资金流。
> **⚠️ V17.0.13 资金流口径外部核对（easy_tdx #55，2026-08-30）**：上游 easy_tdx 的 `get_fund_flow`/`get_history_fund_flow` 基于 `0x0fb5` **逐笔聚合、按成交额分档**，与东财/同花顺「主力净流入」**不可比（重合度 ~14%）**。本项目 **V12.0 起主力净额统一走 push2 f137 / thsdk，弃用 easy_tdx 原生资金流**（V17.0.16 订正：旧写 f137+f140 重复计数），经 #55 外部核对**架构正确**。⚠️ 未来禁止把 `tdx_get_fund_flow` 等原生 easy_tdx 资金流当主力净额源（其 wrapper 已委托东财 HTTP，但底层口径勿与主力净额混用）；只用 push2 f137/f138/f139/f140/f141/f142/f143/f144/f145/f146 / thsdk 口径的主力净。
| **财务** | ZHB(扣非/eps/bps) | **fuyao financials（V17.0.7 升主源：ocf_ttm/revenue_ttm/net_profit_period/annual/eps_annual，官方三表口径）** | TDX F10/0x0010（净利/营收/股东户数，角→元已验） | 新浪三表 | 巨潮 | 0x0010 角→元已验（净利 272.43 亿）；⚠️ V17.0.7 覆盖原 L3 印证位（见下方跟进修订）|
| **股本** | ZHB | 腾讯 [72]/[73] | push2delay f84/f85 | THS | sc_capital_cache | TDX=push2delay 差 39 股=时点 |
| **行业/概念** | ZHB tdxchain | TDX boards | push2delay f127/f129 | - | - | - |
| **两融/股东** | - | 东财 datacenter | THS(盘中) | - | - | 股东户数 243159=TDX 0x0010 精确 ✓ |
| **涨停梯队** | - | **fuyao boards**（独有档位结构）| 复盘啦 get_zttt | KPL | push2ex | 三源交叉 ✓ |

**批量链路（mak/val）**：

| 数据 | L1 | L2 | L3 | L4 | 说明 |
|:---|:---|:---|:---|:---|:---|
| **全市场快照** | ZHB 一次性 | 腾讯批量(60/批) | **push2delay ulist**（短字段列表——f2-f250(请求域通配) 超长会超时）| push2 | push2delay 风控独立优于 push2 |
| **市场情绪** | 财联社 | 开盘红 | KPL | - | 三源互校 |
| **涨停池** | 财联社(99) | KPL(ztjs 99) | 复盘啦(99) | push2ex(兜底) | 8/10 三源 99 一致 ✓ |
| **板块强度** | KPL RealRankingInfo | duanxianxia 矩阵 | ZHB 聚合 | push2delay clist | - |
| **板块轮动** | duanxianxia(ths/kaipan 双口径) | KPL | ZHB 聚合 | - | cells 5 字段已全展开 |

**fallback 总原则（实测修订版）**：
> **ZHB（盘前零网络）→ TDX TCP（实时主源）→ 腾讯（不封 IP 四合一）→ push2delay（东财首选域）→ fuyao（官方印证）→ 财联社/开盘红/KPL（情绪涨停三源）→ 新浪/巨潮（低风险）→ push2（东财最后手段——仅独有数据，风控最严）**

> **⚠️ V17.0.7 跟进修订（2026-08-25，与 §零·B / 代码对齐）**：上述 §12.15.5 实测表为 **2026-08-10 快照**，当时 fuyao 仅作 L2/L3「官方印证」位。**V17.0.7 已据脚本实际接入把 fuyao 提权，本表财务行未同步**——现据实修订如下：
> - **财务 TTM 族升主源**：`core/data_provider.py` L538-613 将 `ocf_ttm / revenue_ttm / net_profit_period / net_profit_annual / eps_annual` 改由 `get_fuyao_financials` 主取（同花顺官方三大报表 5/5 终判口径，报告期驱动静态值无需实时性），push2delay 降为兜底（仅补 fuyao 未填键，不覆盖主源值）。**§12.15.5 财务行 fuyao 应从 L4「fuyao financials」印证位 → 报告期驱动主源位**（位于 TDX F10/新浪之前——fuyao 官方报表口径最权威 + 盘后可查）。
> - **估值 fuyao 仍腾讯之后印证兜底**（`data_provider.py` L518-536）：腾讯 88 字段四合一已含 PE/PB/ROA，fuyao 估值仅双保险，定位合理，**不提权**。
> - **涨停梯队 fuyao boards L1 已接产**（`sc_datasource.py` `hot_list` fuyao），独有档位结构维持首位；炸板/竞价/异动由 `get_sht_report.py` 直接消费（L274/1452/1477/1492）。
> - **提权结论（用户问询）**：fuyao 在同花顺两通道中已排 **thsdk 之前**（§零·B 层级定案：同花顺-fuyao → 同花顺-thsdk（2026-09-07 已退役））——根因 **thsdk 盘后关闸(-6) 仅盘中可用**，fuyao REST 盘后可查 + 独立风控域（4001 退避，无 push 封禁史）；**财务/盘后场景 fuyao 实质优于 thsdk**。与 tdx 比**无需提权**：tdx TCP 仍是行情/静态字段零网络主源，fuyao REST 有网络依赖，二者场景互补（tdx 实时全字段 / fuyao 财务静态+盘后+独占领涨/炸板/竞价/异动）。**综上 fuyao 提权已在 V17.0.7 完成且落地代码，无需进一步调整**；与 §零·B 对齐后的现行主源位见该节「同花顺-fuyao（…V17.0.7 升为财务 TTM 族主源）」。

#### 12.15.6 统一层 ABCD 四层路由矩阵（2026-08-10 正式化——代码 `_should_use_zhb_for_realtime` 已实现）

> **核心原则：ZHB 全局第一优先（零网络）**——只有"盘中/盘后"的"实时字段"才走 HTTP 链。
> ABCD = 运行时机四层，每层字段策略不同：

| 层 | 时机 | 实时字段(行情/资金流) | 静态/估值/财务字段 | 代码实现 |
|:---:|:---|:---|:---|:---|
| **A** | 休市/假日 | **100% ZHB**（T-1 收盘）| 100% ZHB | `is_workday=False → ZHB` |
| **B** | 盘前 00:00-09:30 | **100% ZHB**（T-1，昨夜 zhb 包）| 100% ZHB | `t < 930 → ZHB` |
| **C** | 盘中 09:30-15:00 | **HTTP 链 TDX→腾讯→push2delay→push2** | ZHB（T-1 静态）| `930≤t<1500 → 实时链` |
| **D** | 盘后 15:00-24:00 | **HTTP 链**（T 日真实收盘价——ZHB 深夜才生成）| ZHB | `t≥1500 → 实时链` |

**字段类别判断**（`data_provider` 两集合）：
- `REQUIRES_REALTIME_HTTP`（A 实时）：price/change_pct/OHLC/volume/amount/prev_close/资金流——**C/D 层必走 HTTP**，A/B 层用 ZHB T-1
- `ZHB_SUFFICIENT`（B 静态）：pe_ttm/pe_dynamic/dividend_yield/total_shares/float_shares/change_5d-60d/ytd/streak/52周/ipo_price/employee/industry/concept——**四层均 ZHB 优先**，HTTP 仅兜底

**盘中实时字段 HTTP 链的 ZHB 位置**：
> TDX（实时主源）→ 腾讯（不封 IP 四合一）→ push2delay（东财首选域）→ **ZHB T-1（最后兜底——非盘中/盘后场景实时源全失败时用旧值）** → push2（风控最严仅独有）

> **"TDX→腾讯→push2delay→ZHB"是 C/D 层实时字段链的简写**——ZHB 位于链尾兜底；
> **全局视角 ZHB 是第一优先**（A/B 层 100% ZHB；C/D 层静态字段 ZHB）。两者不矛盾。

#### 12.15.7 ZHB 缓存 ABCD 四级分级（2026-08-10 正式化——`zhb_field_safe` 实现）

> **与 12.15.6 统一层路由矩阵区分**：12.15.6 管"各源优先级"（何时用哪个源）；
> 本矩阵管"zhb 缓存数据能否使用"（字段时效容忍度）。两个维度独立。
> 代码：`_ZHB_REALTIME_FIELDS` / `_ZHB_NEAR_REALTIME_FIELDS` / `_ZHB_STATIC_FIELDS` + `zhb_field_safe`

| 级 | 字段 | max_delay_days | 依据 | 实测（delay=4 天）|
|:---:|:---|:---:|:---|:---:|
| **A 实时** | 行情 11（change_pct/OHLC/amount/1d/2d/price）| 0 | 盘中必须 fallback 原接口 | False ✓ |
| **B 准实时** | 竞价族 4(main_net_buy_amount/1d/hands/1d **=竞价额/量**, V17.0 实锤) + **streak_days 连板** + **涨停族 [33]连板数/[31]异动周期计数/封单额[4][6][8]三日滚动** | 1 | 竞价/连板 1 交易日即变（8/7 涨停→8/8 断板）；streak 原误归静态 3 天→上移；⚠️ 真主力资金（东财 **f137**，V17.0.16 订正）走 A 实时链；[33] 连板数 2026-08-27 天梯 20/20 定案 | False → |
| **C 日频** | 区间涨跌幅 6/52周/pe_ttm/pe_dynamic/股息率/eps/bps | 3 | 滚动但慢变（pe 随价 ±2.5%/日），周末容忍 | False ✓（4>3）|
| **D 静态** | ipo_price/employee/股本/行业/概念/上市日期/名称 | 90 | 恒定数据（茅台 ipo_price=31.39 上市至今不变），长假/停更容忍 | True ✓ |

> **V16.3.3 调整内容**：① `streak_days` 从 C 级上移 B 级（1 天——连板数 1 日失真）② 新增 `_ZHB_STATIC_FIELDS` D 级（90 天——原全部静态字段 3 天过严，长假后无谓 fallback）
> **设计意图**：A/B 级保守（宁可 fallback 更优源）；C 级周末容忍；D 级长假容忍——平衡数据新鲜度与无谓请求

#### 12.15.8 永久字段缓存分类 + 股票名称结构化设计（2026-08-10——12.19 矩阵 + 12.14 字段库核实）

> **设计原则**：永久不变字段走 `static_permanent` 缓存（10 年 TTL，永不过期）；
> 名称结构化——临时前缀忽略、ST 风险信号保留。代码：`parse_stock_name`（sc_utils）+ `TTL["static_permanent"]`

**A. 字段永久性分级（字典全字段核实）**：

| 级 | 字段 | 缓存 | 依据 |
|:---:|:---|:---:|:---|
| **永久**（10 年）| code/exchange/market、list_date(上市日期)、ipo_price(发行价)、name_core(核心名称)、ts_code/instrument_id/thscoce | `static_permanent` | 上市 25 年不变（茅台 ipo_price=31.39 验证）|
| **年/季度**（90-365 天）| total_shares/float_shares（送转/增发才变）、employee_count（年报）、industry/board（重组）、company_full_name、registered_capital、legal_representative | `share_capital`/`basic_info_static` | 低频事件驱动 |
| **季度**（24h-7天）| bps/eps/net_profit/revenue（财报期）、limit_rule（ST 状态驱动）| `financial`/`f10_*` | 财报发布才变 |
| **每日**（交易日）| pe/股息率/区间涨跌幅/52周（C 级 zhb）、is_st（ST 标记）| `basic_info`/缓存 ABCD C 级 | 随价滚动 |

**B. 股票名称结构化（parse_stock_name）**：

| 输入名称 | name_core | is_st | is_new | 处理 |
|:---|:---|:---:|:---:|:---|
| 贵州茅台 | 贵州茅台 | False | False | 正常 |
| N百花医药 | 百花医药 | False | **True** | 上市首日——临时前缀忽略，次新标记保留 |
| C中芯 | 中芯 | False | **True** | 上市次日至第5日 |
| XD/XR/DR 茅台 | 贵州茅台 | False | False | 除权除息——**应忽略**（名称主体不变）|
| ST百花医药 | 百花医药 | **True** | False | **不可忽略**（退市风险信号）|
| *ST湘邮 | 湘邮 | **True** | False | 同上（退市风险更高）|

> **ST 判定修正**：原 `get_board_type` 用 `"ST" in name` 全包含——改为 `parse_stock_name` 前缀精确判定（避免名称中部含 ST 的误判）+ 不依赖调用方传 name（name_core 缓存后可独立判断）
> **设计价值**：① name_core 永久缓存（10 年 TTL 零开销）② ST 标记独立（报告/策略可快捷风险过滤——sht 短线/涨停判定等）③ 次新标记（is_new）供次新股策略

#### 12.15.9 附录索引（实证层——主字典只留结论，详细实证在附录）

> **字典架构**：主字典=决策层（字段定义/结论/优先级），附录=实证层（实测值/样本/破解数据）。
> 主字典引用附录处使用"详见 [verify/push2_verify.md](verify/push2_verify.md)"格式。

| 附录 | 内容 | 对应主字典章节 |
|:---|:---|:---|
| [verify/push2_verify.md](verify/push2_verify.md) | push2 114 字段全量破解表 + 24 股样本 + 未知字段数据（f103/f108/f160/f190/f199）| §12.9.1 |
| [verify/axdata_verify.md](verify/axdata_verify.md) | AxData 666 字段按源补齐矩阵（TDX 196/巨潮 222/新浪 115…）| §12.14 |
| [verify/samples_verify.md](verify/samples_verify.md) | 24 股样本核实矩阵（26 字段×6 源）+ f190/tx65 等破解数据 | §12.19 |
| [verify/tencent_verify.md](verify/tencent_verify.md) | 腾讯 88 字段全复核 + 未知位多股矩阵 + ROA 验证 | §12.1 |
| [../field_verification/20260902/report_existence_20260902.md](../field_verification/20260902/report_existence_20260902.md) | **2026-09-02 存在性+量级一致性复核**（不复盘精确对撞，只核验常规字段跨源存在+量级自洽；f109 独立复证；[86]证伪恒0）| §验证20260902 |
| [verify/levistock_field_verify.md](verify/levistock_field_verify.md) | levistock 26/38 接口实测字段 | §12.10.9 |
| [verify/thsdk_field_verify.md](verify/thsdk_field_verify.md) | THS SDK 395 ID 字段核实 | §12.8.12b |
| [verify/fuyao_api_full.md](verify/fuyao_api_full.md) | **fuyao 官方 REST 全量字段契约镜像**（62 端点：请求参数+响应字段+口径注记，零删减——行情/财务五类指标/估值 PS·PCF/竞价/涨跌停炸板池/异动/热榜/龙虎榜/基金 24 端点/全市场导出）。**在线官方文档站**：`fuyao.aicubes.cn/docs/`（introduction / api-reference / mcp/tools），财务指标语义页 `api-reference/financial-indicators/` | §12.8.12c |
| [verify/client_fields_enum.md](verify/client_fields_enum.md) | 客户端字段枚举全景（东财 950+/通达信 35/21 列破解/同花顺 F10 文本+thsdk 口径铁证）| 客户端逆向 |
| [verify/network_servers.md](verify/network_servers.md) | 三源服务器清单+移动线路实测（通达信 connect.cfg 全表/同花顺 123ths 域名族/东财 SSO）| 客户端逆向 |
| [verify/em_indicators.md](verify/em_indicators.md) | 东财 939 指标代码全表（100000000xxx→名称，财务/估值指标族）| §零·C（东财指标, line 207）|
| [verify/em_tableheader_ids.md](verify/em_tableheader_ids.md) | 东财客户端表头字段 ID 全表（A/B/C/D/E/F/G 系：行情/盘口/连板/竞价/区间/财务/主力）| §零·C（东财表头, line 207）|
| [verify/tdx_func_fields.md](verify/tdx_func_fields.md) | 通达信官方字段总表 1924 个（func_*.cfg code→中文名，含类型）| §零·C（通达信, line 220）|
| [verify/tdx_headers_definition.md](verify/tdx_headers_definition.md) | 通达信表头字段官方定义（用户提供：行情/财务类，与 tdxquant/ZHB 实锤对应）| §零·C（TDX 表头定义）|
| [verify/tdxhy_x_names.md](verify/tdxhy_x_names.md) | 通达信细分行业 X 码→名称全表 470 个（T=一级行业 / X=三级细分行业）| §（TDX 行业映射, line 579）|
| [verify/ftshare_fields_mirror.md](verify/ftshare_fields_mirror.md) | FTShare MCP 85 工具×实际响应首行字段全镜像（capital_flow/quote…）| §（FTShare MCP, line 3477）|
| [verify/ulist_push2_align.md](verify/ulist_push2_align.md) | ulist↔push2 162 字段同值对齐权威映射（两接口索引不同源，严禁混用）| §12.9.1（line 2659）|
| [verify/ths_tableheader_ids.md](verify/ths_tableheader_ids.md) | 同花顺 tableheader 列 ID 摘录汇编（682 抽样 + iwc 56 + Fy 81 + marketstatic；原始 682 全表未入库）| §零·C（同花顺段, line 217）|

> **📌 官方文档可行性结论（2026-09-01 网络调研）**：用户长期靠对撞破解，反思"有无官方文档直接解释字段"。结论：
> - **唯一有官方字段文档的源 = 同花顺 fuyao**（在线站 `fuyao.aicubes.cn/docs/`，含财务指标语义页；全量契约镜像见 `verify/fuyao_api_full.md`）。其官方文档覆盖 fuyao **自有字段**（财务五类指标 ROE/ROA/成长/偿债/营运/现金流、三大报表、复权因子、行情快照、涨跌停池、龙虎榜等）——已支撑 `tx65`/`tx66`(ROE/ROA) 与财务 TTM 族升 L1。
> - **腾讯 qt.gtimg.cn / 东财 push2 / 新浪 hq.sinajs / 通达信 TDX：均无官方字段文档**，仅社区逆向（今日头条/知乎/CSDN/cnblogs；腾讯接口社区文明确称"没有官方发布的正式文档和承诺"）。→ **[56][85][86]（腾讯实时行情占位位）无官方捷径**；对撞（跨源数值相等）对三者恒 0 命中（源覆盖盲区）→ 仅能判"暂无对撞证据"、不得直接收口为未知。**2026-09-03 经非对撞主动法（K线自算 Beta / VWAP 折算 / 符号-盘口比对）升级定案方向**：[56]=Beta族高置信、[85]=均价/VWAP类价格派生候选强、[86]=手级带符号量(候选=委差)——印证"对撞是终判、主动法为前置"（详见 §12.8.12e 状态表与 CRACKING_METHODOLOGY.md）。
> - **Tushare Pro**（`tushare.pro/document/`）、**AKShare**（`akshare.akfamily.xyz/`）有官方文档，但**非本项目主采集源**（仅 §12.11 调研录入）。
> - ⚠️ 关键边界：fuyao 官方文档解释的是 fuyao **自有命名字段**，≠"解释腾讯 [56][85][86]"。即使 fuyao 有同名语义字段，仍需数值对撞确认与腾讯槽位的映射——**官方文档不替代对撞**。

#### 12.15.10 破解新字段→同步分字典（强制规则，V17.0.16 建立）

> **原则**：主字典=决策层（★唯一权威），`verify/` 分字典=实证层（按源组织的原始证据）。**每破解/登记一个新字段，必须同步更新其对应源的 verify 分字典**——否则主字典与实证层割裂，后续对撞/复核无从溯源。

**源→分字典映射（破解新字段时的同步落点；标 ⚠️ 无分字典=主字典自身即权威）**：

| 源 | 分字典（verify/） | 同步落点 | 备注 |
|:---|:---|:---|:---|
| 东财指标代码 | em_indicators.md | 全表追加 code→名 | 939 全表 |
| 东财表头 | em_tableheader_ids.md | 全表追加 ID→列 | A/B/C/D/E/F/G 系 |
| 通达信官方字段 | tdx_func_fields.md | 全表追加 func_* | 1924 全表 |
| 通达信表头 | tdx_headers_definition.md | 全表追加定义行 | 用户提供 |
| 通达信行业 | tdxhy_x_names.md | 全表追加 X 码 | 470 全表 |
| 腾讯 | tencent_verify.md | 88 字段复核表 + 未知位矩阵 | §12.1 |
| push2 | push2_verify.md | stock/get 全字段破解表 | §12.3/§12.9.1 |
| ulist↔push2 对齐 | ulist_push2_align.md | 162 字段对齐映射 | §12.9.1 |
| 同花顺 SDK | thsdk_field_verify.md | 395 ID 核实表 | §12.8.12b |
| 同花顺 tableheader | ths_tableheader_ids.md | 列 ID 摘录汇编 | §零·C |
| 样本矩阵 | samples_verify.md | 24 股核实矩阵 | §12.19 |
| AxData | axdata_verify.md | 666 字段按源矩阵 | §12.14 |
| FTShare | ftshare_fields_mirror.md | 85 工具镜像 | §12.20 |
| fuyao | fuyao_api_full.md | 62 端点全量契约 | §12.8.12c |
| 客户端枚举 | client_fields_enum.md | 枚举全景 | 客户端逆向 |
| 服务器 | network_servers.md | 三源服务器清单 | §12.13.7 |
| levistock | levistock_field_verify.md | 26/38 接口实测 | §12.10.9 |
| ⚠️ ZHB (tdxstat/tdxstat2/tipinfo) | —（无分字典） | 主字典 §1/§2/§3 自身 | 主字典已含全字段表，破解直接登记本表 |
| ⚠️ 新浪/akshare/其他文档确认源 | —（无分字典） | 主字典对应章 | 仅文档确认，无原始采集附录 |

**强制流程（破解新字段后）**：
1. 在主字典对应章登记字段（含 `核实状态`/`验证依据`/`铁证等级`）。
2. 查上表确定该源的 verify 分字典；若有，将原始证据（字段契约/样本值/对撞数据）同步追加进分字典对应表。
3. 若源 ⚠️ 无分字典（如 ZHB），则主字典章节自身即权威，无需追加分字典。
4. 跑一致性闸门：`python scripts/verify_sync_check.py`（离线，检查 断链/孤儿附录/主字典字段未同步进分字典/**主字典已升级但分字典结论陈旧**），须零失败。

> **闸门脚本**：`scripts/verify_sync_check.py` 是「破解后一致性核查」的 CI/commit 前闸门——任何 `docs/verify/*.md` 引用断链、任何分字典孤儿、任何主字典已破解字段未进对应分字典，均会报错，确保本规则不被绕过。
> **HARD 4 陈旧结论检查（2026-09-03 新增）**：除存在性/映射一致性外，闸门现对 **腾讯 `[NN]`** 与 **push2 `fNN`** 两类分字典做**结论新鲜度**比对——扫描主字典含升级事件信号（如 `主动升级`/`非对撞升级`/`升级定案方向`/`→Beta族高置信`/`→均价/VWAP类价格派生候选强`/`候选=委差`）的字段行取最新日期，若 > 分字典同字段最新日期（或分字典无该字段日期戳行），即判 HARD FAIL。即：**主字典升级字段时，分字典须在同行补写日期戳**，否则闸门会拦下"陈旧结论"漏更。

### 12.16 akshare 接口分类全景（2026-08-05 文档确认，O39 编号修正：原 12.14——12.15 矩阵在其前导致编号乱序）

> **来源**：https://github.com/akfamily/akshare（21774⭐，MIT，1.18.81 高频周更）
> **定位**：A股数据接口大全（数千接口，封装几十个源）——**字典准确性校准基准**，详见 §12.11
> **状态标注**：接口分类来自官方文档，字段级需按接口调用实测

| 分类 | 代表接口（_em=东财/_sina=新浪/_tx=腾讯/_lg=乐咕）| 项目对应 |
|:---|:---|:---|
| 行情 | stock_zh_a_spot_em（全市场）/ stock_zh_a_hist（历史K线）/ stock_zh_a_tick_tx_js（逐笔）| push2/腾讯 |
| 财务 | stock_financial_abstract（F10摘要）/ stock_financial_analysis_indicator（指标）| 新浪三表 |
| 估值 | stock_a_indicator_lg（乐咕 PE/PB/股息率**历史序列**）/ stock_zh_valuation_baidu | push2 f162/f163/f164/f165/f166/f167 |
| 资金流 | stock_individual_fund_flow / stock_sector_fund_flow_rank | push2 f137/f138/f139/f140/f141/f142/f143/f144/f145/f146 |
| 龙虎榜 | stock_lhb_detail_em / stock_lhb_stock_statistic_em | datacenter |
| 两融 | stock_margin_detail_szse/sse | datacenter |
| 股东 | stock_zh_a_gdhs_detail_em（股东户数）| RPT_HOLDERNUMLATEST |
| 分红 | stock_fhps_detail_em | get_dividend_history |
| 板块 | stock_board_industry_name_em / stock_board_concept_name_em | clist/slist |
| 涨停池 | stock_zt_pool_em / stock_zt_pool_strong_em / stock_zt_pool_previous_em | push2ex |
| 异动 | stock_changes_em（盘口异动，同 levistock §12.10.1）| 项目空白 |
| 北向 | stock_hsgt_hist_em（历史）/ stock_hsgt_fund_flow_summary_em | get_northbound_hold |
| 可转债 | bond_zh_hs_cov_info / bond_zh_hs_cov_daily | ZHB 可转债 |
| 期权 | option_finance_board / option_sse_daily_sina | 项目⏸️ |
| ESG | 无专门模块（akshare 部分覆盖）| AxData §12.12.7 |

**价值重申**：akshare 不新增独家数据（项目已直连多数源），核心价值是**多源交叉校准**（乐咕历史估值序列 → 替换 val 模拟 PE 百分位）。

---

### 12.17 KPL 开盘啦（longhuvip.com 私有 API，2026-08-09 实测 30 接口）🆕

> **来源**：https://github.com/LowellLee/kpl（KPL接口.md 文档，开盘啦 App 私有接口）
> **协议**：Android UA（`Dalvik/2.1.0`）POST/GET `*/w1/api/index.php?a=<Action>&c=<Class>&...`
> **鉴权**：大部分接口**匿名可用**（仅 DeviceID/VerSion）；部分需 UserID/Token（**文档示例 token 实测有效**——`238db8818a81aac93eb79327e1bcff4a`/UserID 2675923/DeviceID d66474b3-fd78-3a95-a56d-76e29e765ea3）
> **域名**：apphq（实时）/ apphis（历史）/ apphwhq（行情）/ apphwshhq（情绪）/ applhb（龙虎榜）；xuangubao.com.cn（选股宝，公共无鉴权）；fupanwang.com（复盘网直播）
> **⚠️ 私有 API 风险**：非官方公开——接口/字段可能变更；token 属文档作者——生产勿依赖

**实测接口与字段（30 个全部成功，2026-08-09）**：

| 接口 | 域名 | 关键字段 | 价值 |
|:---|:---|:---|:---|
| RiseFallAnalysis | apphwshhq | info=[涨停/跌停/自然涨停/曾跌停/破板率/炸板/日期] | 市场情绪（历史 st=250）|
| MoodNumCount | apphwshhq | SZJS/XDJS/ZTJS/DTJS/qscln/q_zrcs/bl/color | 涨跌家数+全市场量能 |
| ChangeStatistics | apphq | ztjs/df_num/**strong 情绪指标**/lbgd 连板高度 + tip 提示 | 情绪值（历史 st=100）|
| GetPlate_Info_QJ | apphwshhq | PlateID=801900 昨涨停今表现 / 801902 昨连板 / 801903 昨破板——List=[--/家数/成交额/净额/涨跌幅] | 昨日梯队表现 |
| GetPlateInfo_w38 | apphwshhq | nums(SZJS/XDJS/ZT/DT/ZBL/yestRase) + list(板块/股票/涨停时间/封单/首板/连板/个股属性/实际换手/实际流通/原因) | **涨停复盘** |
| DailyLimitPerformance | apphwhq | PidType=1-5（一板~更高）info=[代码/名称/涨停时间/**涨停原因**/封单/最大封单/主力净额/主力买/主力卖/成交额/板块/实际流通/实际换手/振幅%/板块代码/涨停数量] | **连板梯队分板**（历史 Day=）|
| DailyLimitPerformance2 | apphwhq | 未涨停（价格/涨跌幅/板块/主力净额/买卖/成交额/实际流通/换手/振幅%）| 未涨停高板 |
| MorningBiddingList | apphwhq | info=[代码/名称/价格/实时涨跌幅/**涨停委买额**/竞价涨跌幅/**竞价净额**/竞价换手/竞价成交额/20分后委买/板块/实际流通/.../连扳] | **竞价强度**（历史 Date=，Index 分页 60）|
| GetStockBid | apphwhq | bid=[时间/价格/标志/成交量] 竞价分时 | 个股竞价 |
| GetStockPanKou | apphwhq | real 全字段（last_px/px_change/px_change_rate/OHLC/avg_px/turnover_ratio/total_amount/total_turnover/vol_ratio/up_px/down_px/amplitude/entrust_rate/amount_in/out/dyn_pb_rate/pe_rate/TTMPeRate/jtPeRate/circulation_amount/value/total_shares/market_value/phcj_volume/turnover/actualcirculation_value）+ weituo 十档 | **盘口全字段（含动态PB/多PE）** |
| GetKLineZhangTing | apphq | List=[Date/ZSCode 板块/Reason 开盘啦原因/SCLT 日内龙一/GNSM 概念/Boom_ZS] | 涨停原因（历史 GetDayZhangTing）|
| RealRankingInfo | apphq | list=[板块代码/名称/强度/涨跌幅/涨速/成交额/主力净额/主买/主卖/量比/流通值/300万大单净额/总市值/**机构增仓**/今PE/明PE/强度2/涨跌幅2] | **板块强度+今明PE** |
| ZhiShuStockList_W8 | apphwshhq | list 40+ 字段（恒瑞医药：代码/名称/基金/属性/概念/价格/涨跌幅/成交额/换手/流通/主力买/卖/净额/...）| 板块成分全字段 |
| GetMainMonitor_w30 | apphq | Money=0-4（30万/50万/100万/300万/1000万）List=[方向(1被动卖2主动买3被动买4主动卖)/时间戳/量/金额/均价/时间] | **L2 大单** |
| GetWeiTuo_W14 | apphq | Vol=500-10000 手/Tur=30-1000 万 List=[时间/委托序号/价格/手数/成交额/买卖/涨停标记/撤单标记] | 大单委托 |
| GroupCount_w28 | apphwshhq | List=[板块名/"新高数,涨停数"/板块代码] | **百日新高** |
| Radar | apphq | list=[time/status(封涨大减等)/stock_name/plate_type/status_color/content/content2/stockid/LBstatus] | **短线精灵** |
| GetHotPHB | apphq | Day/List=[代码/名称/涨跌幅/排名/...] | 人气热榜 |
| GlobalCommon | apphq | CYWWZS 全球指数（DJI 道琼斯 54036.93...）| 全球指数 |
| GetKLineDay_W14 | apphis | x 日期/y OHLC/vol/bal/turnover/CQ/state/state1/stateZT | K线（**StockID 是内部编码非 6 位**）|
| GetStockTrendIncremental | apphwhq | trend=[时间/价/均价/量/方向] + preclose/hprice/lprice/px_change_rate/total_turnover | 分时+竞价额 |
| GetStockList（龙虎榜）| applhb | list=[ID/Name/IncreaseAmount/D3/BuyIn/JoinNum/Turnover...] | 龙虎榜 |
| 涨停/炸板/跌停池 | flash-api.xuangubao | data=[break_limit_up_times/buy_lock_volume_ratio/change_percent/...]（date 历史）| **选股宝池** |
| market_indicator/line | flash-api.xuangubao | fields=rise_count/fall_count/limit_up_count/limit_down_count/limit_up_broken_count/yesterday_limit_up_avg_pcp/**market_temperature** | **分钟级情绪曲线** |
| surge_stock/stocks+plates | flash-api.xuangubao | 热点解读（code/prod_name/cur_price/px_change_rate/circulation_value/description）| 热点题材 |
| fupanwang /kpl/zhibo | api.fupanwang | data.info.List 直播消息 | 大盘直播 |

**交叉验证（2026-08-07，三家完全一致）**：
- **涨停 74 只**：KPL RiseFallAnalysis（74）= 东财涨停池（74）= 财联社涨停池（74）——**三源一致** ✓
- **跌停 4 只**：KPL（4）= 东财（4）✓
- 破板率 26% / 炸板 26 只（KPL）与东财口径可对照
- 情绪指标 strong 63 / 连板高度 4（8/7）

**独有数据（他源无）**：竞价涨停委买额、开盘啦详细涨停原因（Reason 长文）、连板梯队分板（PidType）、短线精灵状态流、板块今/明 PE、百日新高、市场温度曲线、龙虎榜营业部（GetNewOneStockInfo）

**⚠️ 未确定**：K线接口 StockID 内部编码映射（302132≠6位代码）；板块成分 40+ 字段中后段（PE/财务类）精确含义；GetHotPHB 第 4-7 个字段含义。

#### 12.17.1 kaipanla-data-parser 补充（2026-08-09 实测 10 接口 + 63 字段映射验证）🆕

> **来源**：https://github.com/Rainynitesky/kaipanla-data-parser（开盘啦 App 抓包解析——mitmproxy + 脱壳 + protobuf 逆向）
> **⚠️ 必须 Dalvik UA**（非 Dalvik 返回 errcode=0 但 List=[]）；非交易时间需 `Date=YYYY-MM-DD`；token 会过期（示例 token 2026-08-09 仍有效）

**实测验证的接口与字段**：

| 接口 | 控制器/域名 | 实测字段（已验证）| 说明 |
|:---|:---|:---|:---|
| GetPlate_Info_QJ | c=ZhiShuRanking | **概念板块** List[0]=涨跌家数差 [1]=强度 [2]=成交额(元) [3]=主力净额(元) [4]=未知(0.86) [5]=涨停数 [6]=涨停封单(元) [7]=大单封单(元)；**行业板块**（8019/803/880 开头）List[0]=强度 [1]=涨跌幅×100 [2]=成交额 [3]=主力净额 [4]=量比 | 实测 801159 机器人概念：[8, 2524, 6501.64亿, 44.32亿, 0.86, 3, 8994万, 4843万]——**涨跌幅不在此接口**（在 Index/GetInfo BaceFaceList）|
| GetPanKou | **c=ZhiShuL2Data**（非 ZhiShuRanking）参数 StockID | pankou[0]=成交额 [1]=换手率% [2]=未知(196) [3]=未知(2550亿) [4]=未知(-2505亿) [5]=主力净额 [6]=上涨家数 [7]=下跌家数 [8]=未知(23) [9]=未知(18.61万亿) [10]=未知(23.79万亿) [11]=强度 | 实测 801159：[6501.64亿, 3.494, 196, 2550亿, -2505亿, 44.32亿, 706, 522, 23, 18.61万亿, 23.79万亿, 2524.99]——[9]/[10] 疑板块流通/总市值 |
| GetBaseFaceListZDEvnArtNew | c=ZhiShuL2Data | ID/Title/BoomReason/IsBoom/Date/ZTNum/QD/LZInfo | 当日爆发原因（8/7 机器人概念 ZTNum=3）|
| BKFenShiZhiBo | c=ConceptionPoint | list/date | 板块分时直播事件 |
| SonPlate_Info | c=ZhiShuRanking | List=[[代码,名称,强度]] | 实测 801159 子板块：众擎机器人 261.7/滚珠丝杠 131.1/灵巧手 125.4/宇树机器人 120.8/外骨骼 85.3/智元 61.3/小米 47.x |
| GetGPCPHBTS_Tag | c=ZhiShuRanking | List（标签配置——排序选项）| Type 参数来源 |
| ZhiShuStockList_W8 | **c=ZhiShuRanking + 域名 apphis** | **63 字段**（详见下表）| **⚠️ 响应 key 小写 `list`**；**Type 需有效标签值**（实测 0/1 空——2/7/20 各 9 只——遍历合并去重）|
| Theme/InfoBKR | c=Theme + applhb | List_Special/Special/List | 子概念列表 |
| Index/GetInfo | c=Index | Day/Time/**BaceFaceList**（活跃板块涨跌幅——**非交易时间返回空**）| 涨跌幅唯一来源 |
| Index/NewGetList | c=Index + applhb | List/Ad_x/DongXiang/Topic/Theme | 首页聚合（热门板块）|
| GetDayBaseFaceListZDEvnArt | c=ZhiShuKLine | 实测 FAIL（参数需进一步探索）| 爆发原因历史 |

**ZhiShuStockList_W8 个股 63 字段映射（实测 *ST湘邮 600476 全字段验证 ✓）**：

| 索引 | 字段 | 实测值 | 索引 | 字段 | 实测值 |
|:--:|:---|:--:|:--:|:---|:--:|
| 0 | 代码 | 600476 | 25 | 换手率% | 0.92 |
| 1 | 名称 | *ST湘邮 | 28 | 收盘封单(元) | 0 |
| 4 | 板块标签 | 无人物流、蚂蚁概念 | 29 | 最大封单(元) | 0 |
| 5 | 价格 | 9.49 | 33 | 振幅% | 5.05 |
| 6 | 涨跌幅% | 2.04 | 37 | 总市值(元) | 15.29亿 |
| 7 | 成交额(元) | 1362万 | 38 | 流通市值(元) | 15.29亿 |
| 8 | 实际换手% | 1.52 | 40 | 领涨次数 | 0 |
| 9 | 涨速 | 2.04 | 42 | 机构增仓Q1(元) | 0 |
| 10 | 实际流通(元) | 9.27亿 | 50 | 300万大单净额(元) | 0 |
| 11 | 主力买(元) | 115.9万 | 53 | 市净率 | -3.45 |
| 12 | 主力卖(元) | -79.2万 | 58 | 人气值 | 646 |
| 13 | 主力净额(元) | 36.8万 | 59 | 人气排名变化 | -64 |
| 18 | 卖流占比 | 0.09 | 60 | 市盈率（动） | 145.44 |
| 19 | 净流占比 | 0.04 | 61 | 市盈率TTM | -3.29 |
| 20 | 区间涨跌幅 | 0 | 62 | 市盈率（静） | -3.23 |
| 21 | 量比 | 0.955 | 23 | 几天几板 | "" |

> 其余索引（2/3/14-17/22/24/26/27/30-32/34-36/39/41/43-49/51/52/54-57/63+）未命名（bind 数组无映射）——如需可对照 PaiHangBangOption/GetUserOptionB

**Socket 协议（README 逆向结论——HTTP 不可得的字段）**：PlateTypeQuotasListResp.Item = plateId/plateName/**strength 强度**/**incRate 涨跌幅**/**tur 成交额**/**mainNetAmount 主力净额**/**volRatio 量比**/**institutionIncrease 机构增仓**/circularCaptital/**yearPE 今PE**/**nextYearPE 明PE**——**volRatio/institutionIncrease 仅 Socket 推送有**（HTTP RealRankingInfo 有机构增仓但量比需对照）；267 板块列表走 Socket（protobuf）——RealRankingInfo 分页可替代

**坑清单（README 15 条已确认）**：Dalvik UA 必须 / 概念 vs 行业字段映射不同 / List[4] 非涨跌幅 / List[6]=涨停封单 List[7]=大单封单 / GetPanKou 控制器 ZhiShuL2Data / BKFenShiZhiBo 控制器 ConceptionPoint / ZhiShuStockList_W8 域名 apphis + 小写 list + Type 遍历 / 非交易时间 BaceFaceList 空 / [11] 主力买非流通市值 / [28][29][50] 封单/大单净额

#### 12.17.2 KPL-post 66 接口抓包文档核对（2026-08-10，未实测）🆕

> **来源**：https://github.com/zensu357/KPL-post（开盘啦 App 抓包 Postman 集合解析文档，2026-07-21，66 接口，敏感字段已遮蔽）
> **与 12.17（30 实测）/ 12.17.1（10 实测）关系**：66 接口中 **8 个 Action 已实测记录**（MoodNumCount/ChangeStatistics/GetPlateInfo_w38/GetTrendIncremental/GetVolTurIncremental/GroupCount_w28/GetStockList/GlobalCommon/GetDayZhangTing）——**互相印证 ✓**；其余 **约 45 个新接口**（多组同 Action 不同参数，如 MarketSCLNKLine×6 市场、GetList×4 快讯分类）
> **⚠️ 本小节为抓包级记录（未实测）**——参数/URL 来自抓包文档；实测口径以 12.17/12.17.1 为准

**🔑 复盘啦（FuPanLa）= 字典 12.10.3/12.10.4『开盘红』的抓包确认**：levistock 封装的 get_pmsl/get_zttt/get_his_limit_resumption 实为开盘啦 FuPanLa 控制器（apphwhq.longhuvip.com，apiv=w47）——
『开盘红』即复盘啦（fupanwang）系列，同一批接口：

| 复盘啦接口 | Action | 对应字典 12.10 记录 | 参数 |
|:---|:---|:---|:---|
| 盘面亮点 | FuPanLa/GetPMSL_PMLD | 12.10.4 get_pmsl 盘面梳理 | st=30/Index 分页/Red |
| 看强势（大幅回撤） | FuPanLa/GetPMSL_KQXY | 12.10.4 get_pmsl 盘面梳理 | Red |
| 涨停天梯 | FuPanLa/GetZhangTingTianTi_W47 | 12.10.4 get_zttt 涨停天梯 | Red |
| 龙虎榜动向 | FuPanLa/GetYTFP_LHBDX | 12.10.4（龙虎榜） | Red |

**新增接口清单（按 App 功能模块）**：

**最强风口/题材**：

| 接口 | Controller/Action | 参数 |
|:---|:---|:---|
| 最强风口 | StockFengKData/GetFengKListBest | Time |
| 明天炒什么 | Topic/InfoList | st/Index/Red |
| 明天炒什么搜索 | Topic/SearchTopic | KeyWord |
| 题材库搜索 | Theme/InfoSearch | key |
| 题材库详情 | Theme/InfoGet | ID |

**快讯**：

| 接口 | Controller/Action | 参数 |
|:---|:---|:---|
| 快讯头条 | PCNewsFlash/GetTopList | st/Index |
| 快讯重要/全部/AI解读 | PCNewsFlash/GetList | Type 区分+Date |

**大盘直播**：

| 接口 | Controller/Action | 参数 |
|:---|:---|:---|
| 直播内容 | ConceptionPoint/ZhiBoContent | index |
| 直播图标注 | ConceptionPoint/GetPoint | Red |

**量能趋势（历史）**：

| 接口 | Controller/Action | 参数 |
|:---|:---|:---|
| 北证/沪深京/沪深/上证/创业板/科创板 | HisHomeDingPan/MarketSCLNKLine | Type 区分市场 |

**市场情绪**：

| 接口 | Controller/Action | 参数 |
|:---|:---|:---|
| 权重表现 | HomeDingPan/WeightPerformanceList | Order/st/Index/Type |
| 大幅回撤 | HomeDingPan/SharpWithdrawalList | Order/st/Index/Type |
| 今日涨停破板率 | HomeDingPan/ZhangTingPoBan | Red |
| 历史涨停破板率 | HisHomeDingPan/ZhangTingPoBan | Red |
| 赚钱效应 | Emotion/GetMoneyDate | st/index |
| 赚钱效应展开 | Emotion/GetMoneyDetail | Day |
| 昨日涨停/连板/破板表现分时 | ZhiShuL2Data/GetTrendIncremental | StockID(板块代码)+Day |
| 同上成交量 | ZhiShuL2Data/GetVolTurIncremental | StockID+Day |

**机构/资金**：

| 接口 | Controller/Action | 参数 |
|:---|:---|:---|
| 机构增仓（未过滤/过滤北向保险） | ZhuLiChiCang/GGList_JGCC | Type/Order/Index/Date/IsBX |

**百日新高**：

| 接口 | Controller/Action | 参数 |
|:---|:---|:---|
| 按板块 | StockNewHigh/GroupStock_W28 | Type |
| 按个股 | StockNewHigh/GroupStock_W28 | Order/OrderType/IsAll |
| 新高趋势 | StockNewHigh/GetDayNewHigh_W28 | GroupID |

**互动易**：

| 接口 | Controller/Action | 参数 |
|:---|:---|:---|
| 热搜排行 | InteractData/GetHotSearch | Type |
| 搜索 | InteractData/GetSearchData | KeyWord |

**商品现货**：

| 接口 | Controller/Action | 参数 |
|:---|:---|:---|
| 涨价榜 | XianHuoData/XianHuo_Group | Order/Type/DStart/DEnd |
| 精选 | XianHuoData/AllXianHuo | IsJX |

**龙虎榜**：

| 接口 | Controller/Action | 参数 |
|:---|:---|:---|
| 股票 | LongHuBang/GetStockList | （12.17 已实测） |
| 订阅 | UserBusiness/GetDay | Day |

**新闻/公告/研报**：

| 接口 | Controller/Action | 参数 |
|:---|:---|:---|
| 列表 | CompanyNotice/GetList | StockID/Type |
| 内容详情 | CompanyNotice/GetContentNew | iid |
| 公告详情 | AnnouncementList/GGDetail | iid |

**全球行情**：

| 接口 | Controller/Action | 参数 |
|:---|:---|:---|
| 全球指数 | GlobalIndex/AllGlobaIndex | Red |

**个股**：

| 接口 | Controller/Action | 参数 |
|:---|:---|:---|
| 盘口精简（溢价基因） | StockL2Data/GetStockPanKou_Narrow | StockID/State |
| 消息速递 | StockMessageBar/MessageBarInfo | StockID |
| 盯盘实时 | StockYiDongKanPan/StockDPRealData | StockID |
| 涨停原因（个股） | HisLimitResumption/GetDayZhangTing | （12.17 已实测） |

**个股 F10（开盘啦版）**：

| 接口 | Controller/Action | 参数 |
|:---|:---|:---|
| 概念题材 | StockF10Basic/GetConceptJXBKw23 | StockID |
| 公司资料 | StockF10Basic/GetCompanyInfo | StockID |
| 股本股东 | YiDianCangWei/GetGuDong | StockID/Type |
| 估值（市盈率 TTM） | StockF10Basic/GetValuation | StockID/year/key |
| 主要指标 | StockF10Basic/GetMainIndicators | StockID/Type |

> **App 功能全景**：开盘啦 App 数据源模块 = 最强风口/明天炒什么/快讯/大盘直播/量能趋势/市场情绪(权重·回撤·破板率·赚钱效应·昨日梯队分时)/复盘啦(盘面·涨停天梯·龙虎榜)/涨停原因/题材库/商品现货/机构增仓/百日新高/互动易/龙虎榜/新闻公告研报/全球行情/个股盯盘/个股 F10 —— 用户已安装 App 可直接对照
> **⚠️ 未实测**：以上接口均来自抓包文档；实测价值排序建议：复盘啦 4 接口（与 12.10 印证）> 市场情绪 8 接口（GetMoneyDate 赚钱效应为独有）> 个股 F10 5 接口（估值/主要指标对照项目 F10）> 百日新高 3 接口


---

### 12.18 plate-rotation（duanxianxia 短线侠，2026-08-09 实测 4 接口）🆕

> **来源**：https://github.com/hssqz/plate-rotation-skill（板块轮动 Claude Skill——双源对照）
> **域名**：duanxianxia.com / ds.duanxianxia.com / x.duanxianxia.cn（POST form）
> **鉴权**：**无 API key——仅 Referer 注入**（`https://duanxianxia.com/web/main` + Origin + X-Requested-With）——Safari UA
> **⚠️ 返回格式**：**HTML 片段嵌在 JSON 的 `html` 字段**（前端 innerHTML 渲染）——需正则解析（仓库 parsers.py 已沉淀 5 个解析函数）
> **板块代码体系**：88x = 同花顺概念（886084 F5G/885998 光纤/886033 共封装光学）；80x/803x = 开盘啦（801807 算力/801660 通信/803023 AI 应用）——**与 KPL §12.17 同代码体系可互查**

**4 接口（全部实测成功，2026-08-09）**：

| 接口 | 参数 | 返回字段 | 价值 |
|:---|:---|:---|:---|
| `/api/getPlateRotatData` | from=ths/kaipan, days=10/20/30/50 | `first` + `html`（表头日期 newest→oldest + 排名/板块代码/名称/当日值/color red-green——**N×天 矩阵**：ths=涨跌幅% / kaipan=**强度分**（综合上榜次数+涨速+龙头数多因子））| **板块轮动历史矩阵**（60KB HTML/20 天）|
| `/api/getPlateRotatChart` | from, days | ECharts：`date`/`legend`/`name` {1:'板块名(上榜次数)'..5}/`1-5` 系列（value=排名，未上榜=符号标记）| **Top5 板块 N 日排名曲线**（实测 8/7：并购重组 18 次上榜/芯片 12/机器人概念 11/算力 11/AI应用 10）|
| `/api/getLongByPlate` | platecode, days | `html`（每天一个 td：领涨/当日无领涨 + div.kline code/rank(龙一..)/name）| **板块龙头跨天追踪**（妖王榜——持续性统计）|
| `/api/getPlateDayChart` | platecode, days | `legend`（null=近 N 天未活跃）+ `date` + 强度/量能系列 | 单板块强度量能时序 |

**解析要点（仓库 parsers.py 沉淀）**：板块轮动表 `re.split("<span class='rank'...>(\d+)</span>")` 分行；每日单元格 `<td class='plate plate{code}' code='..' name='..'>`；龙头 td 区分 `text-align:left`（有领涨）vs `text-align:center;color:#bbb`（"当日无领涨"——**服务端 </div> 闭合错位，须 lookahead `(?=<td|$)` 兜底**）；日期表头 `line-height:160%;'>YYYY-MM-DD` 正则抽。

**交叉验证**：板块代码（801807/801660/886084）与 KPL §12.17 同体系 ✓；"并购重组"板块 18 次上榜与 8/7 涨停池题材（KPL 首板宏昌科技并购重组）方向一致 ✓

**独有价值**：**板块轮动 N×天矩阵**（他源无——mak 板块轮动可直接引用）；**双源口径框架**（ths 当日爆发 vs kaipan 持续性——"真主线 vs 妖板"判别：双源都上榜=真主线/仅 ths=妖板候选/仅 kaipan=退潮中）；龙头跨天持续性（妖王识别）

**⚠️ 未确定**：强度分（kaipan）的精确因子构成；getPlateDayChart 未活跃板块（legend=null）的系列结构；历史日期参数（days 是否支持指定日期回溯）

---

> 📌 **重要提示**：本文件是项目的**关键字典**，所有数据接口与字段调整前必查。优先采用字典中已确定的内容，可大幅减少重复反向工程工作。
> 📌 **重要提示**：本文件是项目的**关键字典**，所有数据接口与字段调整前必查。优先采用字典中已确定的内容，可大幅减少重复反向工程工作。


---
