# 脚本应用接口与字段来源字典(Script Data Dictionary)

> **创建日期**: 2026-07-28
> **更新日期**: 2026-08-14(**V17.0 全盘重构版**——core/ 包化、execute_batch_pipeline 基类、composite 链删除、主力净流入 f137 统一、行业 881 段过滤、PE 动态源修正)
> **基于**: [field_dict.md](../docs/field_dict.md)(§12 多源字典 + §12.15 源优先级矩阵 O37 修订版 + **V17.0 拼音规律破解/口径实锤**)
> **目的**: 明确每个脚本的**每个字段**从哪个源/接口获取、走哪个中间层函数、**完整 fallback 链**、**跨脚本获取逻辑差异**——与 field_dict 形成"双字典"对照
> **使用原则**: 脚本调整前必查; 优先采用字典已确定的中间层函数
> **数据流总览**: 全市场脚本(mak/val)→ ZHB 快照 + 腾讯批量覆盖; 个股脚本(sht/med/lng)→ `get_canonical_stock_data` 强类型合约(TDX→腾讯→push2delay→ZHB + 补取) + 基类 `execute_batch_pipeline` 批量骨架
> **脚本清单(5 大, ful 已删除)**: mak 1737 行｜val 2151 行｜sht 1718 行｜med 1198 行｜lng 1108 行(2026-08-14 实测)

---

## 〇、公共数据源底座(所有 fallback 链的层级定义)

| 层级 | 实现位置 | 说明 |
|:---|:---|:---|
| **L1 ZHB 静态** | core/zhb_client `_parse_tdxstat`/`_parse_tdxstat2`/tipinfo; 入口 sc_datasource `get_zhb_single_stock_data` | T-1 快照; **tdxstat2 21 列全映射已定位(V17.0)**;[4]/[6]/[8]=涨停封单额三日滚动; [13]=881 行业板块/880 概念·风格双段 |
| **L1.5 THS SDK** | stock_common/sc_ths.py(同花顺官方 C 库 TCP——正式账号无限频) | 独有: PB/ROE TTM/主力净流入盘中/两融/户均持股/市值——候选级补全 |
| **L2 TDX TCP** | core/tdx_client(easy_tdx 适配) | 0x0010 金额**单位角**(O19 /10 得元); F10/boards/K线; **prefetch 命中时 canonical 跳过 TDX(V17.0)** |
| **L3 腾讯** | sc_datasource `get_tencent_quote` / tdx_client `_tencent_batch_fallback`(60/批) | O21 平盘 `is not None` 不回退; [67]/[68]=52周高低(V17.0 实证); **tx75 主力净流入口径存疑(V17.0 实锤反向)→ 仅兜底** |
| **L4 东财 push2delay** | sc_datasource `get_em_quote_full_delay`(push2delay 镜像域, 风控独立) | **V17.0 主力源**: f162 动态PE/f163 静态PE/f137-146 资金流/f174-175 52周; ulist(f2-f21 行情, **估值字段返回 "-" 勿用**); 1.0rps 限流 |
| **L5 东财 push2 主域** | sc_datasource `get_em_quote_full` | 风控最严最后手段; 当前 IP 封禁中自动跳过 |
| **L6 东财 datacenter** | 龙虎榜/股东/北向/解禁/大宗(日期单引号) | 独有数据 |
| **统一合约** | core/data_provider `get_canonical_stock_data` | sht/med/lng 主入口; **V17.0 补取**: push2delay 估值+资金流无条件补取(进程当天缓存 _PD_EXTRA_CACHE, 空结果不缓存) |

> **V17.0 关键修正**: ①canonical fallback 实际链 = prefetch(push2delay ulist)→ TDX → 腾讯 → push2delay 补取(pe/fund)→ push2 主域 → ZHB 兜底; ②**主力净流入 f137 无条件优先**(盘前/盘后均取最近交易日, 与 get_main_net_buy 同源); ③**行业仅认 881 段**(880 段=概念/风格, 防"股权转让"当行业); ④prefetch 命中跳过 TDX(35 只批量省 35 次 TCP)。

---

## 一、字段时效性分类(O37 修订 + V17.0)

| 类别 | 字段示例 | 主源 | 补源 |
|:---|:---|:---|:---|
| 行情(实时) | price/change_pct/amount/OHLC | 腾讯批量(全市场)/TDX(单股) | push2delay(补取)/ZHB(盘前) |
| 资金流 | main_net_buy_hands/amount | **push2delay f137(当日权威)** | ZHB tdxstat2(T-1)/THS(盘中)/TDX 0x0011(兜底) |
| 估值 | pe_ttm/**pe_dynamic**/pb/dividend_yield | push2delay **f163 静态/f162 动态**(V17.0)/ZHB | 腾讯(pe_ttm/pb)/THS(PB)/fuyao(pe_mrq) |
| 财务 | net_profit/revenue/roe/eps | TDX F10/0x0010 | THS ROE TTM/新浪三表 |
| 股本 | total_shares/float_shares/mcap | 腾讯实时合并 | **gb_info Zgb/Ltgb/FreeLtgb(V17.0 定位)**/sc_capital_cache |
| 历史涨跌幅 | change_5d-60d/ytd | ZHB(**全部交易日口径**, V17.0 实锤) | 腾讯 52周 |
| 情绪/轮动 | market_degree/strong/板块强度 | 财联社/开盘啦 | KPL/duanxianxia |

---

## 二、data_provider 统一接口(按字段归类, V17.0 更新)

### 2.1 行情/资金流
| 字段 | 中间层 | 优先级链(V17.0) |
|:---|:---|:---|
| price/change_pct/amount/turnover | get_canonical_stock_data | prefetch → TDX → 腾讯 → push2delay → push2 → ZHB |
| **main_net_buy** | **get_main_net_buy** | **push2delay f137(当日, 无条件) → ZHB T-1 → TDX 0x0011 → 腾讯 tx75(兜底)** |
| main_net_buy_wan(cdata) | get_canonical_stock_data | **f137/1e4(无条件) → ZHB → 腾讯 → TDX**——与 get_main_net_buy 同源一致 |
| main_net_buy_wan_1d | cdata | ZHB [15](T-1, OpenAmoPre1 实锤) |
| 四档资金流 | get_em_quote_full_delay | fund_main/super/large/mid_today(+5d/10d) = f137/f138/f139/f140/f141-146(V17.0 全定位) |

### 2.2 估值/财务
| 字段 | 中间层 | 优先级链(V17.0) |
|:---|:---|:---|
| **pe_dynamic** | cdata | **push2delay f162(动态, 无条件补取) → fuyao pe_mrq → ZHB Col[3](=静态, 名不符)**;**腾讯 [52] 实为静态 PE 已从来源剔除(V17.0 实锤)** |
| pe_ttm | cdata | push2delay f163(静态TTM)/ZHB Col[9](MorePE TTM)/腾讯[39]——TTM 口径一致 |
| pb | cdata | push2delay f167/腾讯[46]/ZHB 计算 |
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
| tdx_get_fund_flow(0x0011) | 主力资金流(口径与 f137 不同, 仅兜底) |
| _tencent_batch_fallback | 腾讯批量 60/批——mak/val 核心(进程内按交易日缓存) |
| get_history_fund_flow_120d | 60/120 日资金流(sht prefer=tdx / med prefer=em) |
| _TENCENT_FIELD_INDEX | [67]/[68]=52周高低(V17.0 实证); **pe_dynamic 索引已移除(静态勿用)** |

---

## 四、sc_datasource 函数(HTTP + 新源, V17.0 更新)

| 源 | 代表函数 | 脚本 |
|:---|:---|:---|
| 东财 push2ex | get_limit_up_pool/get_limit_broken_pool/get_limit_down_pool/get_yesterday_limit_pool | mak B/B+ |
| 东财 datacenter | get_em_industry_l2_data/get_holder_structure/get_margin_trading/get_block_trade/get_dragon_tiger_board/get_lockup_expiry | sht/med/lng/mak |
| 东财 push2delay | **get_em_quote_full_delay**(f162/163/167/174/175/f137-146 全字段)/prefetch_quote_batch(ulist) | canonical/sht 批量预取 |
| 同花顺 | **get_ths_hot_raw(getharden 唯一入口, V17.0 三版合一)**/ths_hot_list/get_eps_forecast | val/mak/sht |
| 财联社 | get_cls_market_emotion/cls_telegraph | mak A(主)/val 08/全脚本 |
| 开盘啦 | get_kph_limit_ladder | mak B+ |
| 巨潮 | **get_strategic_announcements(新增 keywords 参数, V17.0 下沉 mak 异动公告)**/cninfo_irm | mak/sht/med/lng |
| 新浪 | get_sina_financial_report/get_sina_balance_sheet | val 04/med/lng |
| KPL | get_kpl_market_sentiment/get_kpl_broken_ratio/get_kpl_plate_strength/get_kpl_limit_up_detail | mak A |
| THS | get_ths_market_snapshot/get_ths_pb | val 04 PB(仅盘中核对——盘后跳过) |
| duanxianxia | get_plate_rotation_top/get_plate_rotation_matrix | mak D 对照 |
| ZHB 快照辅助 | get_zhb_full_market_snapshot/get_zhb_market_stat2_snapshot/zhb_field_safe | mak/val 全市场 |

---

## 五、5 大报告脚本**逐字段**调用矩阵(2026-08-14 V17.0 重定位)

> ⚠️ **V17.0 行号说明**: 全脚本经 core/ 包化 + 批量骨架收敛 + 死代码清理, 行号已大幅漂移——下表行号为当前代码定位, 以 `Select-String` 复核为准。

### 5.1 get_mak_report.py(市场全景, 1737 行)——A-G 段

#### 5.1.1 个股扫描字段(主入口 `get_market_abnormal_data`/`_get_zhb_market_data`)
| 字段 | 获取函数 | fallback 链 | 说明/口径 |
|:---|:---|:---|:---|
| 全市场快照 | get_market_abnormal_data | ZHB `zhb_field_safe` → TDX `tdx_get_market_abnormal_data` | 5124 只 A 股过滤 |
| price | — | 腾讯 → ZHB price_map | O21 盘中今日 |
| change_pct | — | 腾讯(`is not None` 且 ≠0) → ZHB Col[6] | O21 平盘不回退 |
| amount_yi | — | 腾讯 amount_wan/1e4 → ZHB amount/1e4 | O21 万→亿 |
| turnover | — | 腾讯 turnover_pct → ZHB | O21 |
| mcap_yi | `_calc_mcap_yi` | price×股本(sc_capital_cache) | 股本缓存未命中=0 |
| ret_3d/5d/10d/20d/60d | `_calc_3d_from_daily` | ZHB Col[28]/[30]/[18]/[20] 等(**交易日口径**) | O28 |
| main_net_amount | ZHB stat2 | stat `main_net_buy_amount`×1e4(万→元) | V17.0: 全市场 O(1) 读 |
| **industry_code** | ZHB [13] | `_is_industry_code` 过滤 | **V17.0: 仅认 881 段=行业; 880 段=概念/风格(股权转让/微盘股等)已过滤** |
| name | snapshot/profile/腾讯 | — | ST/退剔除 |
| A 股过滤 | `is_a_stock`(sc_utils 统一, V17.0) | 前缀 00/30/60/68/92 | 滤 ETF/LOF/可转债 |
| is_limit_up/down | `limit_pct_for` | change_pct vs 阈值-0.5 | 主板/ST 10、双创 20、北交所 30 |

#### 5.1.2 其他段(V17.0 变化)
| 段 | 变化 |
|:---|:---|
| A 全市场情绪 | get_cls_market_emotion + KPL 系(不变) |
| B/B+ 涨停池 | get_limit_pool_multi_source + get_kph_limit_ladder(不变); **get_ths_hot_pool 请求已统一到 get_ths_hot_raw(V17.0)** |
| C 板块-异动 | ZHB 旁路优先 `_build_sectors_from_zhb`、TDX 兜底(防 push2 风控) |
| 异动公告 | **get_abnormal_announcements → get_strategic_announcements(keywords=["异常波动"], V17.0 下沉带缓存+TDX 兜底)** |

### 5.2 get_val_report.py(21 策略全市场, 2151 行)
| 变化点 | V17.0 |
|:---|:---|
| 策略扫描 | asyncio 并发 3; ZHB 快照 O(1) 读(main_net_buy_amount 等) |
| 主力资金策略 | ZHB tdxstat2 全市场快照(V15.5.14 预加载) |
| PB 批量 | THS 盘中核对/盘后跳过 |
| ths_hot_reason | **委托 get_ths_hot_raw(V17.0)** |
| 行业判断 | 东财申万二级 L2 → TDX boards → **ZHB 881 段过滤(V17.0)** |
| 写尾 | **save_text_report(V17.0 公共样板)**; _fail_out 收敛+UnboundLocalError 修复 |

### 5.3 get_sht_report.py(短线, 1718 行)
| 变化点 | V17.0 |
|:---|:---|
| 批量骨架 | **基类 execute_batch_pipeline**(prefetch_fn=push2delay ulist 预取, snapshot_data, **pre_gd_init 已去除→统一上传与 med/lng 一致**) |
| 主力净流入 | 二章/七章**统一 f137(get_main_net_buy 与 canonical 同源)** |
| PE(动) | cdata.pe_dynamic=push2delay f162(真动态 15.55, 腾讯静态不再覆盖) |
| 封单 | 盘中实时估算=买一量×涨停价(合理); ZHB 封单额三日滚动为增强候选 |
| 多评委 | **sc_render.render_multi_school_scores(V17.0)** |
| 行业 | 东财申万二级 → TDX → **881 段过滤** |

### 5.4 get_med_report.py(中线, 1198 行)
| 变化点 | V17.0 |
|:---|:---|
| 批量骨架 | 基类 execute_batch_pipeline(gen_kwargs=ind_comp; hsgt=None 误导参数已删) |
| 资金流 60 日 | get_history_fund_flow_120d(60 日窗口) |
| 阶段涨幅 | cdata change_5d/10d/20d/60d(**交易日口径确认**) |
| 多评委 | sc_render(V17.0) |

### 5.5 get_lng_report.py(长线, 1108 行)
| 变化点 | V17.0 |
|:---|:---|
| 批量骨架 | 基类 execute_batch_pipeline(gen_kwargs=ind_comp) |
| **综合数据** | **get_stock_composite_async 链已删除(V17.0 R3, 220 行)——统一 get_canonical_stock_data(_dp_composite 由 cdata 构建, 二次获取同步重建)** |
| 行业 | TDX boards → **ZHB 881 段过滤(V17.0, 防 880 概念污染)** |
| PE 静态 | `_pe_static = _zhb_pe_dynamic`(ZHB Col[3]=静态 TTM, 口径已知) |
| 多评委 | sc_render(V17.0) |

---

## 六、V17.0 数据流变更总览(2026-08-14)

| 变更 | 前(V16.x) | 后(V17.0) |
|:---|:---|:---|
| 主力净流入 | ZHB 优先/腾讯 tx75 优先(口径分裂) | **f137(当日权威)无条件优先, 全链同源** |
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
