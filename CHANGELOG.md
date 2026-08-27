# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),


## [17.0.10] - 2026-08-27


**ZHB T-1 对撞规则固化 + Col[33] 连板数破解 + 批量报错修复**

### 📐 ZHB T-1 对撞规则固化 V17.0.10b（2026-08-27）

**规则写入（CRACKING_METHODOLOGY.md 〇节 + field_verification README 每日流程）**：
- ZHB 本地包数据日期**恒为 T-1**——对撞破解严禁"当日报告 ↔ 当日采集 ZHB"直接比
  (2026-08-27 初犯得 type 0/20 假阴性, 纠正后 20/20)
- 正确矩阵: 采集目录 YYYYMMDD 的 ZHB(T-1) 应对撞 **T-1 当日报告**; 对撞当日报告
  须先验证字段实时性(如涨停族 type/lianban/count 实测为当日盘中值)
- 操作规范: 每次对撞先打印 raw_zhb.json 的 zhb_date + 报告文件名; 结论标注双日期
- capture_field_probe.py: meta.json 增写 zhb_data_date 字段, 完成行打印 ZHB 日期
- 回归 269 passed ✓


### 🔬 字段破解 V17.0.10（2026-08-27 采集, 19 源 519s）

**新破解: tdxstat Col[33] = 连板数（原"涨停类型族 ztlx"证伪）**
- 方法: **日期对齐对撞**——今日采集 ZHB(8/26数据) 与 8/27 MAK 报告涨停天梯对撞
- 铁证: type(Col33) 与天梯连板 **20/20 完全匹配**(000017=5/003040=4/002084=3 全精确)
- 当日涨停时 Col[31]/[32]/[33] 三字段一致=连板数; 非涨停日 type=None/0,
  count=涨停累计次数(近N日), lianban=历史高位(近N日最高连板/异动周期计数)
- 同步: field_dict.md Col[31]/[32]/[33] 对撞补强(Col33 ⚠️→✅)
- 中报指标入库 17 只(tx65/tx66 终判条件达成)
- 字段矩阵: 977 字段 / 1175 记录 / 多源 48
- 回归 269 passed ✓


### 🐛 批量报告报错修复 V17.0.9b（2026-08-27）

**1. LNG 688802(沐曦) 亏损股 UnboundLocalError**
- 根因: `_pe_src` 只在 `_pe>0`(盈利)分支赋值, 亏损股(pe_ttm=0/pe_dynamic=-699)走 else
  分支未赋值 → 444 行访问报 UnboundLocalError。仅亏损股触发, 盈利股全部正常。
- 修复: else 分支补 `_pe_src = "亏损(无正PE)"`。实测 688802 报告正常输出
  "PE(TTM): 0.00x (亏损(无正PE)口径...)"。

**2. SHT 300475 批量 margin TypeError**
- 根因: `resolve_datacenter('margin')` 批量预取偶发返回非 list(dict), sht 1104 行
  `for d in margin` 遍历 dict keys → `d['date']` TypeError。
- 修复(双层防御): ① `get_margin_trading_async` to_thread 结果非 list 置 []
  (源头); ② sht 消费端 `if margin and isinstance(margin, list)` 防御;
  ③ `get_block_trade_async` 同步 data 非 list 防御。
- 回归 269 passed ✓



## [17.0.9] - 2026-08-26


**Col[24] 货币资金破解 + 报告核查修复**

### 🔬 字段破解 V17.0.9（2026-08-26 盘后采集, 19 源 461s）

**新破解: tdxstat Col[24] = 货币资金（万元）`cash_reserve_wan`**
- F10 资产负债表「货币资金」逐股对照终极锁定: 600519=535.188亿(unknown_24 100%一致),
  17 只有数据全部匹配(14 最新期精确 + 600675/688500 为报告期差异=2026Q1值)
- 跨日恒定根因=财报季度才更新(静态财务字段); 历史"成交量/总负债/股本"三假设证伪
- 同步: `zhb_client.py` Col[24] 正名 unknown_24→cash_reserve_wan; `data_provider`/`tdx_client`
  注释更新; `test_data_zhb.py` 断言更新(45 passed); `field_dict.md` 7.3 节破解结论 +
  P0-1 关闭 + 跨源对照表新增货币资金行; `field_verification/README` 破解里程碑
- 采集: 20260826 归档 19 源全 OK; push2 主域 20h 冷却(push2delay 正常); thsdk 盘后不可用
- 字段矩阵重生成: 977 字段 / 1175 记录 / 多源 48
- 全量回归 269 passed ✓



## [17.0.8] - 2026-08-26


**82 份报告全量核查修复(跌停数假数据/扣非ROE/展示口径)**

### 🔴 报告核查修复 V17.0.8（2026-08-26 晚, 82 份报告全量核查驱动）

**P0 跌停数假数据(22→0)根因修复**
- `get_limit_pool_summary` 跌停兜底重写: 旧逻辑直接读 ZHB 全市场快照算跌停,
  但快照盘中恒为 T-1(前一日)——8/26 盘中把 8/25 的 22 只跌停误报为今日
  (KPL/push2ex 双源证实今日真实跌停=0)。权威链: ① 东财 getTopicDTPool tc
  (新 `_query_dt_pool_tc`, pool 可空但 tc 权威) → ② KPL RiseFallAnalysis dt
  (独立匿名源, 校验日期) → ③ ZHB 仅当快照日期==目标日期
- 排查确认 22 与 8/25 炸板池 22 为巧合, `_parse_limit_pool` 无字段错位
- MAK B 段跌停数恢复 pool 优先(A 段涨跌幅口径兜底), 撤销 V17.0.4 强制覆盖

**P1 扣非ROE 全 N/A 修复**
- `get_roe_trend_series` F10 路径补扣非ROE: 加权ROE×(扣非EPS/基本EPS) 同源推算
  (F10 无直接扣非ROE 字段; 曾用 fuyao index_deduct_weighted_avg_roe 实测为
  TTM 滚动口径与单期加权不可混排, 弃用)。新浪兜底同步加同口径推算

**P2 展示/口径**
- MAK E 段涨停名单改真实涨停全量(limit_up_all, 原用梯队 _leaders 含替补致
  "声称3只实际1只"); 名称优先级腾讯实时名>ZHB(消除 霞客环保/哈高科/二纺机 旧名)
- MAK B 段涨停明细>30 只加截断注明(原 43 只只显 30 行易误解)
- MED "静态PE"→"动态PE" 标签修正(实为 pe_dynamic f162), 与 LNG 对齐;
  LNG PE(动态) 改 canonical pe_dynamic(原 ZHB 动态, 数值与 MED 不一致)
- LNG/MED 解禁明细保留一位小数(原 .0f 四舍五入致 1.4万股显示 1 → 明细≠总计)
- 回归 269 passed ✓



## [17.0.7] - 2026-08-25

**field_dict_gemini 对撞复核: f103/f104 终破 + f55/f105 语义纠错 + tx 区间涨幅族定案 + 散单第五档新破解**

### 🔬 Gemini 字典独立复核（9日×20股×19源 raw + 本机K线 + fuyao 官方报表终判, docs/field_verification/20260825_cross_analysis.md）
- **f103 = 经营活动现金流量净额(TTM)**: fuyao 官方季度现金流量表 5/5 精确
  (茅台 FY25 615.22+H1_26 706.91-H1_25 131.19=1190.94亿); 推翻 Gemini
  "营业利润/资产总计分行业"与 scratch 旧审计"利润总额存疑"两案并结;
  报告期切换 796→1190.94 亿动态吻合
- **f104 = 营业总收入(TTM)**(18/18 恒等式); **f105 = 归母净利润(最新报告期)**
  (fuyao 利润表逐字等; 切换日 Q1 272.43→H1 445.17)——证伪 Gemini"经营现金流"
- **f55 = 基本EPS(最新报告期)**=f105/f84(35.611): 恢复主字典旧注,
  证伪 Gemini"每股经营现金流"(F10 每股经营现金=56.55≠35.61);
  f109=归母净利(**最新年报**口径)/f160=年报EPS/f108=扣非EPS(**TTM**, 切换日跳变佐证)
- **tx 区间涨幅族定案(前复权)**: tx62=YTD / tx71=60交易日 / tx69=10交易日(L1,
  K线 w=10 平均偏差 0.101pp n=56) / tx75=180交易日 / tx79=250交易日(ZHB
  change_250k 中位差 1.24pp); **证伪 Gemini tx75="主力占比"/tx79="超大单占比"**
  (与东财占比族最大差 40pp 且符号翻转、值可超 ±100);
  **推翻 f121/f122 "资金流衍生指标"旧注**(实为 60日/YTD 涨幅)
- tx58/59 与"收盘竞价说"和解(9/9): 收盘后最新逐笔=竞价撮合单, 字段本义为最新逐笔
- tx56=Beta 维持 L4 未证实(池内回归不吻合, 农行 -0.19 反例)

### ✨ 新破解
- **f147/f148/f149 = 散单(第五档)买入/卖出/净额**(净=买-卖 715/715 自洽);
  **f197 = 散单净占比 ≡ f149/f48×100**(154/154 含北交所)——修正 Gemini
  "-(f194+f195+f196)"公式(仅沪深成立, 根因=沪深守恒律"大中小散四档净额和≡0"
  137/140 逐字零; 北交所退化: f140≡0、f137≡f143、守恒律失效)
- f111 板级枚举(2/6/23/80/81)、f177 位掩码{1,65,577,1025,1089}、f199≡90 全样本复核通过

### 📝 文档同步
- field_dict.md: 腾讯表 [56]/[58]/[59]/[62]/[69]/[71]/[75]/[79] 六行重写 +
  §12.9.1 V17.0.7 七条终破; verify/push2_verify.md、verify/tencent_verify.md
  加终判覆盖头注; §零·B 矩阵重生成(932 字段/1112 记录)
- 遗留: Col[31] vs 东财池同日对撞 32/46(ZHB 偏大 14 例)建议降回 ⚠️ 复核

### 🔧 统一层/缓存层同步(同日第二段)
- **修复真 bug**: data_provider 主力净流入兜底链删除"腾讯 tx75×10000"分支——
  tx75 实为近180交易日涨幅, 旧分支会注入假主力净额(603221 +13.45亿假流入);
  tdx_client._TENCENT_FIELD_INDEX 键 main_net_inflow_yi→change_180td_pct 正名,
  sc_datasource 腾讯映射/白名单与 data_provider 补取循环同步更名
- **统一层接入财务 TTM 族**: _em_quote_full_impl 字段包 +f103/f104/f105/f108/
  f109/f160/f190 → 规范键 ocf_ttm/revenue_ttm/net_profit_period/net_profit_annual/
  eps_annual/eps_deduct_ttm/undist_profit_ps; push2delay 补取块(_PD_EXTRA_CACHE)
  同步透传; CanonicalStockData 新增同名字段(带默认值, asdict 序列化旧缓存兼容);
  冒烟实测 600519 七字段全中(ocf_ttm=1190.94亿=fuyao 终判值逐字等)
- **缓存层评估**: get_tencent_quote/_em_quote_full 均不走 SQLite @cached
  (stock_cache.py:60 明示实时行情不缓存), 键名变更/字段扩展零失效面;
  _PD_EXTRA_CACHE 按日进程缓存自动覆盖; 新增字段为报告期驱动静态值,
  无需新增 TTL 分类, 口径铁律不触发
- 回归: scripts/run_tests.ps1 -Mode skip_real → **269 passed / 45 deselected 基线不变**

### 📊 5 大脚本核查与增强(同日第三段)
- **核查结论**: 五脚本代码零字段误用(sht 主力段自动受益 tx75 兜底删除;
  med 阶段涨幅全为 ZHB 实锤口径; lng tipinfo EPS 已有单季标注; val 仅取
  vol_ratio; mak 板块域编号不同构不冲突); get_main_net_buy 本体无 tx75 残留
- **实施 3 增强**(零额外网络请求——财务族随 push2delay 补取已入 canonical):
  ①lng 三章现金流双源对照: f103(TTM) vs 0x0010(报告期) + 经营现金流/收入比 +
    滚动现金含量(TTM OCF/上年归母, 跨两财年粗算标注);
    实测茅台 TTM 1190.94亿=fuyao 终判值逐字等、含量 144.7% ✅
  ②med 三章归母净利双源核验: f105 vs 新浪财报首行, 偏差>2pp 提示以财报为准;
    实测 445.17 vs 445.17 偏差 0.0% ✅
  ③lng 五章/med 三章: undist_profit_ps 每股未分配利润展示(分红能力池子,
    负值=弥补亏损期预警); 实测 159.74 元 ✅
- script_data_dict 补财务 TTM 族路由行; 矩阵重跑一致(932/1112)

### 🧾 reports 全量审计与渲染/脚本修复(同日第四段, 41 文件逐项核查)
- **审计发现(脚本 audit_reports*.py)**: 81 处问题——系统性 3 类+散点:
  ①股东户数表→"### 信号:"粘连 ~25 处; ②综合建议加粗粘连(**中性观望**各项) ~40 处;
  ③席位明细 5 行全标"买五"(硬编码); ④互动易"答案: None"(str(None) 未兜底);
  ⑤两融标签 15 行实显 10 行; ⑥lng ROE 表前后缺空行; ⑦北向"近N个交易日"
  措辞失实(季度频数据); ⑧60日资金流标题固定"最近10日"配 1 行数据
- **上游退化确认(非代码回归)**: push2his 连接级封锁(RemoteDisconnected)+
  push2delay fflow daykline 返回空 klines(行为再变)→历史资金流仅剩 TDX 单日
  (V17.0.4 prefer_his 修复被上游再次绕过); 已按诚实降级处理
- **md_render.py 中心修复**: ➊行内嵌 \n 展开(L("\n➤ X") 的空行意图不再被吞);
  ➋新增 _ensure_tbl_gap_after: ➤→### / 字段:值 / 树形列表三个提前 continue
  分支补齐"表后空行"规则; 合成用例 T1-T5 全过
- **sht 脚本修复**: 席位排名 买一~买N/卖一~卖M 分别计数; 两融循环截断对齐标签;
  互动易 answer=None/"none" 兜底待回复; 北向标签如实化(期数+最新日期+距今天数);
  资金流段自适应标题(<10 日如实标注)+<5 日跳过误导性趋势统计;
  sht/med/lng 综合建议加粗后补空格; lng 评级行改"研报评级分布"(去 ### 内加粗)
- **验证**: 重生成 000657_sht 全部修复生效(买1~买5/两融15=15/表后空行/
  建议分隔/资金流诚实降级提示); 回归 269 passed 不变

### 🔄 THS 族替代 push 域盘点与 fuyao 兜底接入(同日第五段)
- **push 域退化实测确认**: push2his 连接级封锁(RemoteDisconnected)+push2delay
  fflow daykline 空 klines——历史资金流窗口断裂为上游行为变化, 非代码回归
- **thsdk 盘中实测(游客账号 13:01)**: 代码格式=USHA/USZA+6位10位定长(600519.SH 会报错);
  klines(count) 历史日K(8/24 总金额=ZHB stat2 amount 逐字等);
  **big_order_flow 盘中逐笔大单流**(茅台1520行: 时间/方向±1/量/金额/委托买卖)——
  push2 fflow 实时的盘中替代候选(需聚合, 非日级历史); 午休/盘后空 df 关闸复现
- **fuyao 三大报表 TTM 聚合对撞(600519)**: ocf_ttm=1190.94亿/net_profit_period=
  445.17亿/net_profit_annual=823.20亿 与 push2 f103/f105/f109 **逐字等**;
  revenue_ttm 差1.8%(营业收入 vs 营业总收入口径); **修复 get_fuyao_financials
  缺 period 必参的潜伏 bug(V17.0.5 引入, 恒返回空)**
- **data_provider 兜底链接入**: 财务 TTM 族 push2delay 缺失时 → fuyao 三大报表
  quarterly 聚合(_FY_TTM_CACHE 按 code+report_period 进程缓存); 
  eps_annual/eps_deduct_ttm/undist_profit_ps 无 fuyao 字段仍 push 独有
- **字典新增 §12.8.12d THS 族替代矩阵**: 七项 push 依赖逐一判定替代状态;
  script_data_dict 补兜底链路由行; 矩阵重跑(**950 字段/1134 记录/多源 45**)
- 回归 269 passed ✓

### 🔄 fuyao 升主源 + thsdk 层级后移(同日第六段, 用户决策)

- **层级定案**: 用户运行时段多为盘后 → thsdk(TCP 盘后/午休关闸)定位**盘中专属
  特殊层**, 不进通用 fallback 链; **fuyao(REST 盘后可查+独立风控域+官方口径)
  升为 push 替代主力**
- **data_provider 层级重构**: 财务 TTM 族 **fuyao 三大报表聚合升主源**
  (ocf_ttm/revenue_ttm/net_profit_period/net_profit_annual + eps_annual=
  净利年报÷股本缓存折算), push2delay 降为兜底仅补缺失(fuyao 已填键不覆盖);
  实测 canonical field_sources: 四键=realtime:fuyao、eps_annual=calc:fuyao
  (65.85=f160 精确)、eps_deduct_ttm/undist_profit_ps=push2delay(push 独有)
- **字典 §12.8.12d 扩充**: thsdk 实测表(USHA/USZA 定长格式/klines 历史日K/
  big_order_flow 盘中逐笔大单流/关闸复现)+fuyao TTM 对撞表+七项路由表
  (thsdk 后移注记/fuyao 主源/行情快照插槽候选暂缓); script_data_dict 同步;
  矩阵重跑(**951 字段/1135 记录/多源45**)
- 结论: 涨停池/龙虎榜/行业概念已有非 push 备胎 ✓; 批量行情 ulist 维持
  push2delay(fuyao 不支持批量); 仅历史资金流窗口无同口径替代(上游断裂待复核)
- 回归 269 passed ✓

### 📐 字典矩阵层级同步(同日第七段, 用户质询驱动)

- **核查发现矩阵未反映新规则**: 头部源排序仍是 2026-08-06 旧文(无 THS 族);
  财务 TTM 族七键只在 blockquote/路由表中, 解析器不收录;
  SOURCE_ORDER 无同花顺-fuyao/thsdk 定义; sec_to_source 的 "12.8" 子串
  会把 fuyao 节误判为东财源
- **gen_field_matrix 三处修正**: ①SOURCE_ORDER 插入 同花顺-fuyao(腾讯后)/
  同花顺-thsdk(fuyao 后); ②sec_to_source 前置 fuyao/thsdk 分支(防 "12.8"
  子串误判); ③生成头部源排序文案更新为 V17.0.7 层级定案+动态日期
- **字典补标准字段表**(解析器只认标准表格): §12.8.12c 加三大报表 TTM 聚合族表
  (fuyao 主源侧); §12.9.1 加财务 TTM 族字段表(东财兜底侧)——双表归并使七键
  进入 B.1 多源表
- **验证**: 矩阵 B.1 出现 `ocf_ttm(f103) | 2 | 同花顺-fuyao、东财` 等五行,
  fuyao 排前=主源语义 ✓; B.2 新增 同花顺-fuyao(70)/同花顺-thsdk(63) 分组;
  总量 951→**952 字段/1139 记录/多源48**; 回归 269 passed ✓

### ⚡ datacenter 五类批量预取流水线(同日第八段, 实施#1)

- **动机(实测)**: 昨晚 sht 34 只 15.5 分钟(均27s/只), 最大单项=
  datacenter-web 1.0rps × 每股5类(龙虎榜/两融/北向/解禁/大宗)≈5s/股纯限流等待;
  且跨域并行度=1, 宽松域(腾讯0.15s/巨潮0.2s/fuyao0.5s)全排队在 dc 后面
- **实现**: sc_datasource 新增 start_datacenter_prefetch(幂等调度,
  future 先注册后执行防消费竞态)+resolve_datacenter(kind, code, direct_fn)
  (预取命中 await/未调度回退直调); execute_batch_pipeline 新增通用
  prefetch_async_fn 钩子(session 建立后调度后台流水线); sht runner 接线
  (dragon_kwargs 按 depth 传席位开关), 5 个调用点切换 resolve
- **时序模型**: 预取生产 ~5s/只 vs 消费 ~9s/只÷3 worker——预取始终领先;
  dc 等待移出 worker 车道, 与 TCP F10/腾讯/巨潮/CPU渲染并行
- **实弹验证**: 3 只批量 83s 全成功, "15 项入队"日志 ✓, 五类章节全在 ✓;
  回归 269 passed ✓; med/lng(2-3 只)无需接入
- 附带审计结论: 网络层 5 脚本零裸调用(全部 sc_network 包装);
  mak 指数K线四源链下沉为 get_index_kline_closes(行为等价迁移)

### 📋 报告输出台账 + 两处修复(同日第九段, 用户"失去焦点"诉求)

- **新增 docs/report_output_inventory.md**: 以最新实际报告逐节核对(非 changelog
  描述)的输出台账——sht/med/lng 全章节×引入版本×数据源×验证状态;
  **⛔门控段清单**(自选基金重仓侧证需配置清单文件/封单衰减率仅涨停股/
  fuyao 指标交叉已启用/thsdk 盘中限定)
- **修复 lng 历史高点渲染回归**: V17.0.5 P2 只改了 qfq 函数, 渲染层仍
  high_52w 优先→前复权修复从未生效(茅台显示52周高1539.98/-15.25%,
  真 qfq 高1806.54/-27.83%); 且 🔔📉回调分级嵌套在旧口径注分支下,
  qfq 路径时两级信号全部静默丢失——恢复 qfq 主路径+分级拉平+口径注按源切换
- **修复 lng 九章研报瞬断空转**: 单次请求失败整段"暂无研报覆盖"(实测复测
  同函数返回200条)——加一轮轻量重试(5页失败→1s后3页重试)
- **sht 研报页数 5→3**(四章仅60天计数+前10篇展示, 3页足够); med/lng 维持
  (med 六章近3月统计已是3; lng 九章共识度样本需要5)
- 台账同步说明 reportapi 三处用途与降页影响; 回归 269 passed ✓

### 🔎 FTShare-MCP 仓库盘点 → 字典新增 §12.20 待实测源(同日第十段)

- 应用户要求核查 https://github.com/FTShare-Lab/FTShare-MCP (207 工具 MCP 网关)
- 查重结论: **FTShare 本身=字典未登记新源**(上游聚合网关: 东财/同花顺/雪球/百度/
  华尔街见闻); **6 组全新维度**: 千股千评族×5、涨跌停事件时间线(3s)+DAEC 日内
  涨跌停分布历史、商誉族×5、董监高族×4+一致行动人、质押明细/汇总、业绩快报/
  停牌列表/非凸评级/语义新闻搜索; 已知字段多源补强(股东人数第三源/解禁第二源等);
  **DAEC 全市场快照族×8 为 push2delay ulist 替代候选**(需实测盘后可用性);
  雪球排名经代理部分复活(已死清单注记)
- 字典新增 §12.20(⏸️ 待实测): 分级盘点表+接入前置条件(MCP 协议/鉴权未明/
  必须先 tools/list 核配额); 对照警示(集合竞价结果须 ZHB 互锁/东财板块同上游无增量);
  宏观/港股/美股等维持"项目不需要"
- 矩阵重跑 957 字段/1148 记录

### 🔬 FTShare 最小实测完成 → §12.20 升级(同日第十一段)

- 实测方式: 公共网关 MCP JSON-RPC 直调(无 SDK/无鉴权, SSE+UTF-8 解码), ~15 次调用
- ✅ 可用: 千股千评族(symbol=6位纯代码; score_em=日频评分序列64期;
  全市场表含 pe_dynamic/prime_cost 主力成本/focus/org_participate——字典外新维度);
  **昨日涨停池富于 push2ex**(炸板时间点数组/回封数组/续封标记——晋级率断板直接可用);
  daec_prev_closes 与本机K线逐字等
- ⚠️ 口径修正/半可用: daec_market_snapshot=市场级涨跌分布聚合(非个股快照);
  stocks_all 个股行情31字段(含 change_rate_day5~120/ytd 区间族)但
  **filter/order_by 服务端无效+分页上限200**→替代 ulist 批量不成立,
  维持 V17.0.7 层级结论; event_timeline_3s 样本选择不当待复核
- 字典 §12.20 升级为🔬最小实测完成(部分可用); 矩阵重跑 964 字段/1155 记录

### 📐 FTShare 全字段镜像落库(同日第十二段)

- 第二轮采样(会话 TTL 自动续期): 154 工具 → **85 可用**(首轮全灭根因=会话过期,
  已定位并记录); 失败分类: MISSING_PARAMETER/INVALID_ARGUMENT/UPSTREAM 瞬态
- 全量字段镜像入库: **docs/verify/ftshare_fields_mirror.md**(85 工具×实际响应字段表)
- 字典 §12.20 追加高价值字段表摘录: 千股千评族(focus/org_participate/prime_cost/
  total_score)、昨日涨停池(炸板/回封时间数组)、**limit_event_timeline_3s(15 字段含
  跌停封单额)**、**ggmx 董监高 26 字段**、**unlock_by_date 17 字段(含持有人明细)**、
  **stock_filter 21 字段服务端筛选器**、**risk_warning_stock_quotes 44 字段 ST全行情**
  等; 附新维度定级建议(脚本采纳评估)
- 工程发现: 会话 TTL≈2h 需自动 re-init; 无鉴权确认; kline 族需 start_time+count
- 回归 269 passed ✓

### ✅ FTShare 采纳落地: 统一封装+脚本消费+采集接入(同日第十三段)

- **新模块 stock_common/sc_ftshare.py**: MCP JSON-RPC 客户端(会话 TTL 90min
  自动续期+SSE/UTF-8 解析+空响应刷新重试)+代码双格式转换(纯6位/带后缀)+
  13 个业务函数(千股千评四族/昨日涨停池/事件时间线/董监高/商誉/质押/解禁按日/
  大盘资金流/市场分布/停牌列表); sc_network 注册 market.ft.tech @2rps;
  __init__ 导出 14 函数
- **sht 十四章**: 🧠千股千评行(综合评分+趋势/参与意愿+异动警示/机构参与度)+
  🎯昨日涨停池晋级统计(续封率/平均炸板/断板数)
- **lng 九之二**: 董监高变动结构化(近180日增持减持笔数+明细, 替代公告关键词弱口径)
  +商誉交叉核验(FTShare 商誉/净资产比 vs 三章自算)
- **采集脚本**: 新增 collect_ftshare(个股×6 族+市场级7项, ~126请求≈66s@2rps);
  实弹验证 raw_ftshare.json 落盘(20股全量, 评分序列含T日)
- 字典 §12.20 状态⏸️→✅; script_data_dict 路由行; 矩阵 964/1155; 回归 269 passed ✓

### 📐 Col[31] 口径降级 + tx65 终判条件澄清 + 千股千评对撞(同日第十四段)

- **Col[31] 降级**: 全历史17包×K线涨停日历穷尽破解发现仅11%匹配严格连续连板;
  14例 ZHB>池值(N天M板型)→新假说 H3"本轮行情口径(允许炸板)"待明日同日终判;
  字典注记降为⚠️
- **tx65/tx66 L1 终判未达成**: fuyao H1 指标为报告期累计(非TTM)——茅台 H1=16.74%
  vs TTM=32.41%(约减半); 终判需 quarterly 序列聚合 TTM 或年报数据
- **千股千评 pe_dynamic ≡ push2 f162 动态PE**(偏差0.00%); prime_cost 偏离收盘-0.7%
  (候选主力持仓成本, 待筹码分布交叉)
- **Beta 回归**: 方向相关但系统性偏移+农行反例 → 维持L4; 需沪深300标准回归

### 🔧 myhhub/stock 采纳: Cookie注入 + CYQ筹码分布 + TA-Lib形态识别 + 抢筹/选股器(同日第十五段)

来源: https://github.com/myhhub/stock (14.1k stars, Apache-2.0)——经分析后采纳以下五项:

#### P0-1: 东财 Cookie 注入 sc_network.em_get()
- 新增 `_get_eastmoney_cookie()`: 环境变量 EAST_MONEY_COOKIE > config/eastmoney_cookie.txt > 空
- em_get() 发请求前自动附加 Cookie 头——登录态请求大幅提高 push2 系封禁阈值
- 用户设置方式: `setx EAST_MONEY_COOKIE "从浏览器F12复制的Cookie值"` 后重启

#### P0-2: CYQ 筹码分布算法移植 sc_technical.py
- 新增 `calculate_cyq(dates,opens,closes,highs,lows,turnovers,...)` 函数
- 经典"三角形分布+换手率衰减"模型(与通达信一致, 来源 instock/core/kline/cyq.py)
- 输出: 获利盘比例/平均成本(50%分位)/90%·70%筹码区间与集中度
- 冒烟: 茅台获利盘0%/平均成本1443.40 符合近期走势

#### P1: TA-Lib 61 种 K 线形态识别
- 新增 `get_kline_patterns(opens,highs,lows,closes)` 函数(纯 CDL 函数族委托)
- 需安装 TA-Lib C 库; 未安装时返回 {}
- 消费场景: sht 十四章可加"今日出现形态"行

#### P2-1: 通达信早盘/尾盘抢筹数据
- 新增 `get_tdx_chip_race(period=0|1)` → excalc.icfqs.com POST JSON
- 字段: 抢筹幅度/委托金额/成交金额/连板天数/板数——字典无此源

#### P2-2: 东财选股器服务端筛选
- 新增 `get_em_xuangu(sty_fields,filter_expr,page,page_size)` → data.eastmoney.com/dataapi/xuangu/list
- 支持 200+ 字段组合筛选; val 部分本地扫描逻辑可下推到服务端执行

回归 269 passed ✓

### 🍪 东财 Cookie 过期自动检测(同日第十六段)

- **机制**: 已配置 Cookie 时连续 5 次 403/429 → 打印醒目警告+四步续期指南;
  成功请求或无 Cookie 时计数归零; 提醒后重置避免刷屏
- **配置方式**: `setx EAST_MONEY_COOKIE "值"` 或 `config/eastmoney_cookie.txt`(已 gitignore)
- **验证**: push2delay 实弹请求携带登录态返回茅台行情 ✓; 回归 269 passed ✓

### 🔧 lng 报告三处修复(同日第十七段, 用户报告审计驱动)

#### 修复1: ROE 表排序错乱
- 根因: get_roe_trend_series 返回数据先年报后季报(非纯时间降序)
- 修复: 渲染前按报告期日期降序排列
- 验证: 600519 ROE表 8期纯时间降序 ✓

#### 修复2: 近3年营收CAGR虚假负值(-11%)
- 根因: 混用H1半年收入922亿与FY全年收入1720亿直接比值→假CAGR -19%
- 修复: 仅用年度报告(12-31截止)数据计算CAGR; 年数由实际可得FY期数决定
- 验证: 600519 近1年营收CAGR -1.2%(真实微降, 非-11%假值) ✓

#### 修复3: fuyao 现金流官方指标口径缺失
- 问题: fuyao 净利现金含量98.8%(⚠️偏低)+现金营运指数0.71(🚨嫌疑)与
  双源对照滚动现金含量144.7%(✅充足)结论矛盾——实为H1单期vs TTM口径差异,
  茅台等下半年回款型企业 H1 现金含量天然偏低
- 修复: fuyao 行加"(报告期口径)"标注+ℹ️口径注指向下方 TTM 对照

验证: 重生成 600519_lng 三处全部生效; 回归 269 passed ✓

### 📋 levistock 全量审计: 7 函数补录 + 28 函数消费评估(同日第十八段)

- **三层对照审计**(38函数 × 字典登记 × 脚本消费):
  字典覆盖率 31/38(82%)→补录后 38/38 ✅; 脚本直接消费仅 3/38(get_pmsl/get_zttt/market_emotion_cls)
- **7 个字典未录函数实测**: 4/7 可用(market_index_all_em 43指数11字段/market_mainline_cls
  财联社主线机会🆕/market_wind_stocks_cls 风口龙头股/news_telegraph_cls 电报快讯);
  2/7 接口异常(errcode=1020); sector_stock_belong_em=em_industry_map_l2 实时校准源
- 字典新增 §12.10.10 补录表+消费建议分级(高价值5个/中价值6个/低优先17个)
- 矩阵重跑 **971 字段/1162 记录**; 回归 269 passed ✓

### 🐛 sc_ftshare _reinit UnboundLocalError 修复(同日第十九段)

- **根因**: `_reinit()` 内引用并赋值 `_LAST_POST` 但未声明 `global _LAST_POST`
  → Python 视为局部变量 → 首次读取抛 `UnboundLocalError` → 被
  `except Exception: pass` 吞掉 → `_SID` 永远为 None → ConnectionError
- 修复: 添加 `global _LAST_POST` 声明; 验证 mainline/comment_score 全通

### 📐 Col[31] 同日终判完成: 确认口径分歧(同日第二十段)

- **方法**: 强制同步 ZHB 获取 8/25 数据包(内部日期确认=20260825) →
  与 push2ex 涨停池(8/25 盘后采集)做**真正同日对撞**
- **结果**: 65 只池股中 Col[31]==zt_continuous 仅 50 只(77%);
  15 例不等且全部为 ZHB>pool(如 603095 ZHB=10 vs 连板=5)
- **K线涨停日历重建**: 多数不匹配样本近 20 日内无连续涨停模式,
  但 ZHB 值高达 7~10 → 排除 H1(严格连续)和 H2(近20日累计)
- **结论**: Col[31] 是 TDX 内部定义的"近期异动周期计数"，与东财的
  zt_continuous(严格连续天数)是不同概念。字典注记从 ✅ 降级为 ⚠️，
  消费侧不应单独依赖此字段做连板判定，建议结合 push2ex zt_continuous 使用
- 另发现: 上游 ZHB 包在盘后仅更新至前一交易日(8/25 包含的是 8/24 数据),
  当日包需次日盘前才能同步

### 📋 kaipanla-data-parser 盘点 → 字典新增 §12.21(同日第二十一段)

- 应用户要求分析 https://github.com/Rainynitesky/kaipanla-data-parser (61⭐, MIT)
- **性质**: mitmproxy 流量拦截 + Android 模拟器抓包开盘啦 App 私有 API——接入门槛极高
- **最有价值的发现**: ZhiShuStockList_W8 个股详情 63 字段，其中多个新维度
  (实际换手率/领涨次数/机构增仓Q1/300万大单净额/人气值/PE三口径)
  在 push2/fuyao/ZHB 中均无——但需模拟器+Token 管理+遍历 Type0~19
- 字典新增 §12.21(⏸️ 暂缓): 63字段定义表 + GetPanKou 板块盘口12字段 +
  SonPlate_Info 子板块层级 + Socket Protobuf 协议(volRatio/institutionIncrease 仅Socket推送)
- **与已有源的关系**: KPL 核心功能已由 levistock §12.10 + 直接API §12.17 覆盖；
  本仓库增量=63字段个股详情+板块盘口+子板块层级+Token自动刷新机制
- 矩阵重跑 971/1162; 回归 269 passed ✓

### 🔬 KPL 无 Token 穷尽实测 → §12.21 升级为✅(同日第二十二段)

- **重大发现**: 开盘啦 API 大部分端点无需 Token——直接 HTTP POST + Dalvik UA 即可
  (jinhao2003/kaipanla-crawler 141⭐ 方法验证)
- **穷尽测试**: 22 个 Action 逐一实弹(盘中时段) → 9/22 无 Token 可用:
  ChangeStatistics(市场情绪 ztjs/strong/lbgd)/RiseFallAnalysis/RealRankingInfo/
  ZhiShuStockList_W8(63字段无Token可用!)/GetYTFP_BKHX/YTFP_SCTD/
  GetInfo/GetStockList(LongHuBang)/MarketStockZDNum 全部 ✅
- ❌ 不可用(需Token或特定参数): SharpWithdrawal/GetDayNewHigh_W28/DailyLimitPerformance/
  GetPanKou/GetZhangTingGene/MorningBiddingList 等
- 字典 §12.21 从⏸️→✅升级; 矩阵重跑 971字段/1175记录; 回归 269 passed ✓

### 🔧 限流/导出补全(同日第二十三段, 审计驱动)

- sc_network._DOMAIN_LIMITS 补注册 longhuvip.com 四子域 @5rps
  (apphwhq/apphis/applhb/apparticle——KPL 无 Token API 统一层依赖)
- stock_common.__init__.py 导出 kpl_get_* 九函数
- 回归 269 passed ✓


## [17.0.6] - 2026-08-23

**md 报告格式治理: 键值表全面回退竖排 + 明细伪表转真表(用户审美驱动)**

### 🎨 渲染器(md_render)
- **删除"字段: 值"块→2 列表格自动转换**(V17.0.3 引入)——恢复 V17.0.2 用户原则:
  基本信息/行情快照/估值/评分等键值竖排不表格化。原转换使首行字段名成为
  加粗伪表头(股票名称/T日主力净流入额/价值派评分等喧宾夺主), 且综合投资
  建议长文本被塞进单元格。死函数 _fieldval_block_to_md 一并清除。
- 普通行冒号对齐清理(:\s{3,}→": ")使还原后竖排自然对齐。

### 📊 该用表格处直出真表格(脚本端)
- sht/med 龙虎榜上榜记录(日期/上榜原因/净买入/换手率): CJK 宽度对齐空格
  伪表依赖脆弱间隙推断、常态未转换 → 直出 md 表格(V17.0.2o 席位表先例)。
- med 评级统计行去标题化(➤/**嵌套——➤ 全局转 ### 使计数行变成章节标题)。

### 🗃 存量报告迁移(scratch/migrate_reports_md2.py)
- **165 个文件 / 623 个误转键值表**还原为竖排(保守判定: 2 列+字段名特征+
  值长≤60; 真 2 列数据表零误伤); med 存量评级标题滥用同步修正。

### ✅ 验证
- 探针四案例(键值块/一致预期空格表/龙虎榜 CJK 表/评分块)行为断言全过;
  回归 269 passed / 45 deselected 基线不变。

## [17.0.5] - 2026-08-22

**tdxstat2 Col[4]/Col[11] 终破 + 腾讯 ROE/ROA 对破解 + ulist/push2 字段编号不同构实锤**

### 🔬 字段终破(全市场 16 包 + 20 股×7 目录流水线, docs/field_verification/20260822/cross_analysis.md)
- **Col[11]=change_mtd 本月至今累积涨跌幅%**(基准=上月末最后交易日收盘):
  19/20 股×7 包全精确(误差≤±0.015pp); 月界重置实锤(Col11(8/3)≡chg(8/3) 差=0.000);
  **"WTD 本周至今"命名被证伪**(两周共享同一锚点排除每周重置; WTD 错觉=月初周 MTD≡WTD);
  旧解"近5根K线 r=1.0"亦证伪(中位差 6.1pp); **§7.3 周一相等悬案结案**
  (月初恰满 20 根 K 线时 MTD 与 Col[17] 窗口重合, 每月一次与星期无关)
- **Col[4]/[6]/[8]=limit_up_down_seal 用户修正完全证实**: 三日滚动 col4@T≡col6@T+1≡col8@T+2
  **1434/1434 全市场精确 0 失败**; 符号 100%(涨停正/跌停负, 8/19 千股跌停日中位数转负);
  ST ±5% 亦正确; 可接入打板/封单衰减策略
- **腾讯 tx[65]=ROE / tx[66]=ROA 盈利质量对**: 天然实验——各股随自己中报披露日跳变
  (600519 8/15 后 30.53→32.41、002827→15.13、688589/920118→8/21 披露后), 未披露股恒定;
  量级全符(工行 8.93/万科亏损负); 修订 08-10"tx65=roe 证伪"结论(系对照基准错误)
- **tx[69]≡ulist f160(86% 互锁)+推翻字典旧"振幅"解**(0/138 等 tx43 且 35% 负值);
  近10交易日窗口周六口径 37/38=97%(盘中口径待终破);
  **ul_f160 ≠ pf_f160(利润率类静态)——ulist239 与 push2 字段编号不同构再添一例**
- f190≡ul_f48 100%(138/138) 再实锤; tx62/tx71=f122/f121 资金流衍生再证

### ♻️ 统一层与缓存
- `core/zhb_client.py`: stat2 键改名 `change_5k_bar`→`change_mtd`(修复与 tdxstat Col[27]
  在 full_market_snapshot 合并时的静默同名覆盖); `_ZHB_PARSE_SCHEMA` 2→3(解析缓存强制失效)
- data_provider.get_zt_streak_info 补封单额符号语义注释

### 📚 文档固化链条
- field_dict.md: tdxstat2 Col[4]/[6]/[8]/[11] 四行重写(铁证入典); §7.3 周一悬案结案;
  腾讯表 [62]/[65]/[66]/[69]/[71] 更新; V16.3 O28 备注标记推翻项
- 附录: tencent_verify.md/samples_verify.md V17.0.5 增补节; domain_glossary.md 同步;
  script_data_dict.md L1 层字段说明更新; §零·B 矩阵重生成(920 字段/1103 记录)

### 🆕 fuyao 官方 REST 全量契约镜像 + 盘后通道扩展(HiThink-Tech/Financial-API 研究)
- **新附录 verify/fuyao_api_full.md**(80KB): 上游 llms-full.txt 全量字段契约——62 端点
  请求参数+响应字段+口径注记零删减(行情/财务五类指标/估值 PS·PCF/竞价/涨跌停炸板池/
  异动原因 AI 文本/热榜/龙虎榜/基金 ~24 端点/全市场 Parquet 导出); §12.15.9 索引登记
- field_dict §12.8.12c 重写: 31→62 端点全景; **盘后可用性定案**(HTTPS REST 无 thsdk TCP
  盘后关闸限制——财务/池/竞价终态盘后可查, thsdk 盘后失败的替代通道); ROE/扣非ROE/ROA
  官方口径(tx65/66 对撞终判源); PS/PCF 字典新维度; seal_money/max_seal_money 封单双口径;
  auction_unmatched/昨量比/开板次数/seal_nextday 等新维度入典
- sc_fuyao.py 扩展 7→**18 端点**(auction×2/pools×3/anomaly×2/fin_indicators/
  financials×3/trading_days/adjustment_factors/index×3); __init__ __all__ 同步;
  ⚠️ 本机 Key 未配置→通道自动禁用(配 THS_FUYAO_API_KEY 即启用)
- **Key 已配置并实测(fuyao_key.txt, gitignore)**: 首采 20/20 全通——对撞三线:
  竞价族 auction_volume/amount ≡ ZHB[9]/[14] **19/19**、涨停池 seal_money ≡ zt_seal_amount **54/54**
  (双双 L1 互锁); tx65=扣非加权ROE(TTM) 官方 Q1 32.52≈32.41 锁定语义;
  契约偏差入典(calculate_* 前缀/归母同比未列/中报入库滞后 5003)
- 工程修复: fuyao_to_thscode 北交所前缀顺序 bug(920→.SH 整批拒绝);
  @cached 第二位置参数误当 ttl 潜伏 bug; TTL 表 +fuyao_auction
- **待办①中报终判自动化**: capture_field_probe 内置哨兵探测(h1_indicators_ready)——
  fuyao 上游入库当日即自动拉取全池扣非加权ROE/ROA 完成 tx65 L1 对撞, 无需人工盯守;
  当前状态: 上游仍滞后(code=5003), 哨兵正确跳过省配额
- **待办②基金域接入 lng/med**: sc_fuyao 新增 get_fuyao_fund_holdings/fund_profile +
  get_fund_watch_evidence(自选清单门控); lng【六、筹码与机构持股】/med 新增
  【十六之二、自选基金重仓侧证】段——输出持仓占比/重仓排名/报告期增减/
  基金股票仓位/重仓行业/前十集中度; 实测 025480.OF 10 持仓全字段到手

### ⚡ P0 清单实施(五脚本字段升级——基于 V17.0.5 已互锁字段)
- **sht**: 封单官方口径优先(fuyao seal_money 替代 bid1×涨停价估算)+**封单衰减率**
  (max/current, <30% 烂板预警/>=90% 全日封死)+涨停原因文本; 竞价实时族(live)
  未匹配量/昨量比(<50% 缩量诱多警示)/竞价量比——与 ZHB T-1 同源互锁时效升级;
  十五章新增衰减率信号(仓位降级联动既有 _seal_warn 体系)
- **med**: [本月至今] 动量锚点展示(change_mtd, 持有期 1-3 月正交基准)
- **lng**: ROE 双口径对照(报告期加权 F10 vs 扣非 TTM tx65, 差>5pp 盈利水分预警);
  现金流官方指标交叉(fuyao 净利润现金含量<80%/现金营运指数<0.9 排雷)
- **mak**: fuyao 竞价风向标聚合(高开/放量/红盘占比——9:25 盘前量化情绪,
  时效领先叙事型情绪源; 高开>50%+放量>30% 共振进攻信号)
- **val**: 新增策略24【月内动量】——change_mtd∈[5,25]% (ZHB 本地零网络);
  注册表/_sfmt/计数文案同步; 实测全市场 8003 只→2598 候选(Top10 月内 20%+)
- 统一层: canonical +change_mtd/+roe_deduct_ttm; 腾讯映射表 roa→TTM 正名(键名兼容)+
  +roe_deduct_ttm:65; sc_datasource 白名单透传补 roe_deduct_ttm; 缓存 TTL 表
  +fuyao_seal_map(30min)/fuyao_fund_holdings/fuyao_indicators(trading_day)

### 🔧 P1 清单实施(五脚本增强第二批)
- **sht**: 官方风向标标签直采(高开/放量——免自建阈值)+**异动解读 AI 文本**
  (fuyao anomaly-analysis-stock, 补 V17.0.2 移除盘口异动后的语义层空白)
- **med**: 财务兑现双源核验(fuyao growth 族营收/净利/营业利润同比 vs F10,
  calculate_* 前缀+契约 id 双兼容; 偏差>2pp 以财报原文为准提示)
- **mak**: 跌停池明细正式解法(fuyao limit-down-pool first/last_limit_time——
  东财 getTopicDTPool 空缺闭环); fuyao 连板矩阵互校(boards 六档+
  seal_nextday 次日续封率——独有字段, 30 日窗口)
- **P1-4 核查结论**: change_30d 全仓零脚本引用(仅 canonical 透传+注释)——
  无需迁移, 语义陷阱已由注释覆盖

### 📐 P2 清单实施(用户批准)
- **val 策略25【PS低估值】**: fuyao valuation 批量(市值 top500 预筛控配额)——
  PS(TTM)≤全市场20分位 且 PCF>0; PE 失效标的(高毛利未盈利/轻资产)替代估值锚;
  注册表/_sfmt/计数文案 24→25 同步
- **lng 历史高点前复权切换**: 新增 sc_datasource.get_historical_high_qfq
  (腾讯 ifzq fqkline, ~640 根≈2.6年窗口, 字典 §12.1 备胎接口);
  get_historical_high wrapper 改 qfq 优先/TDX 不复权兜底, 渲染口径注同步。
  实测: 600519 qfq 高点 1806.54 → 真实回撤 -29.6%(旧不复权口径虚报 -52%
  误触"长线黄金坑"信号); TDX 周末 None 时 qfq 主路径天然韧性强于旧实现

### 🔗 统一层 fallback 链修复(盘后字段可用性)
- **roa/roe_deduct_ttm 盘后恒 0 修复**: 原 `need_realtime_quote` 门控导致休市日
  rt_quote={} → 盈利质量对(腾讯 tx65/tx66)盘后报告恒 missing。去门控后
  tencent extras 补取无条件执行——实测周六 600519: roa=27.3/roe_deduct_ttm=32.41 ✓
- **ps_ttm/pcf_ttm 入 canonical**: fuyao valuation 独有维度(ps_ttm/pcf_ttm)补入
  sc_schema CanonicalStockData + data_provider 构造; fuyao valuation 补取条件
  扩为 pe_ttm 或 ps_ttm 缺失即触发(原仅 pe_ttm); 实测 9.46/13.76 ✓
- **source_tag 判定修正**: 原 `and rt_quote` 在财务字段补取后恒真 → 熔断/盘后
  误标 http/tdx(测试 test_graceful_circuit_breaker_fallback 捕获); 改为只看
  `rt_quote.get("price")` 是否来自实时源

### 🧹 全仓 Bug/死代码审计(AST 扫描 66 文件/1269 函数)
- **死代码清理 4 处**: zhb_client.should_use_zhb_data(53 行, V15 遗留时机判断——
  ZHB-First 路由已由 data_provider REQUIRES_REALTIME_HTTP/ZHB_SUFFICIENT 取代)、
  f10_parser.extract_field(通用正则工具零调用)、sc_datasource.get_zhb_52w_range
  (V9.6 遗留——52 周已由 high_52w/low_52w 多源链取代)、conftest.tmp_project
  fixture(零测试引用)。删除后残留引用核查干净+py_compile 全过。
- **Bug 模式扫描零命中**: 裸 except/吞异常 0、可变默认参数 0、async 内
  time.sleep 0、requests 无 timeout 0; 本会话新增高危点作用域验证通过
  (sht _seal_info 跨段同函数/mak _dt_count A→B 段同函数)。
- **甄别说明**: 17 个"仅测试引用"生产函数(get_sw_industries/get_ah_stocks/
  日历族等)保留——属防退化测试覆盖的基础数据接口, 非死代码;
  print 输出集中于 GD 上传/批量 Runner/CLI 引导等用户可见交互层, 属设计选择。

### 📚 参考仓库同步核查(simonlin1212/a-stock-data v3.6.0→v3.7.1)
- P0 五项高危模式逐项核查: mootdx frequency 参数✓/解禁新列名✓/龙虎榜空窗口✓/
  EPS 均值列✓/历史高点不复权 ⚠️→lng 渲染加除权口径警示行(数据源切换待办)
- v3.7.0 新端点择要入典: 估值历史日频序列/复权因子 qfq·hfq/上市退市日/申万行业变迁史/
  CYQ 本地推演法; 宏观层暂不需要; 模式入典: 后缀静默错票(v3.7.1)/ETF 不覆盖个股资金流(#46);
  基线版本注释 V3.6.0→V3.7.1

## [17.0.4] - 2026-08-19

**历史报告深度核查修复 + 数据采集体系完善 + 新字段破解 + GD 补传**

### 🐛 数据修复(历史报告核查驱动, 8/17-8/19 63+39 份 md 全量对比)
- **mak 近3日异动回溯 3日偏离恒 0.00%**: TDX 路径 ret_3d 硬编码 0.0(V16.1 因 ZHB 未破解 1d/2d 移除, 现已破解)
  → `tdx_client._calc_ret_3d_snapshot` 恢复真实复利(实测 300862: 0.00→66.78%)
- **ZHB 路径腾讯覆盖分支 3 日窗口错位**(漏 T-1, 窗口 T/T-2/T-3): `_calc_3d_from_daily` 覆盖分支改取 Col[6]/[7]
- **北向资金冻结**(8/12-8/19 恒 -9.28/+379.75, 47 份报告全同): 同花顺接口 hgt(262 分时点) vs sgt(35 历史点)
  **序列错位** → `get_hsgt_macro_flow` 判 invalid 拒绝展示, sht/med/mak 三处消费点改"数据源异常, 净流入暂缺"
- **跌停 0 不可能**: 东财 `getTopicDTPool` 明细接口 tc>0 但 pool=[] 空(8/17/8/18 实测) →
  `get_limit_pool_summary` 用 ZHB 快照涨跌幅口径兜底(验证 0→2); mak B 段进一步无条件用 A 段当日 `_dt_count`
- **历史资金流仅 1 天**(8/18 全仓 35 份): `_FFLOW_HOSTS` push2delay 排第 1 截断历史请求 →
  `_em_fflow_request(prefer_his=True)` push2his 全窗口优先(实测 60 天)
- **指数多周期收益静默 None**(严重/卡异动判定失效): `get_index_returns` 加**新浪日K兜底**
  (quotes.sina.cn getKLineData, 与腾讯 ifzq 实测一致 <0.01; scale 支持分钟/日/周/月, OHLCV+amount)
- **sht/med 格式**: sht `➤ [板块共振监测]/[市值排名]` 括号拆分小节+内容; med 两融 4 处 ➤ 信息行去标题化;
  md_render 标题 `## **X**`(des2 全局替换误伤)→ 归一 `## X`
- **zhb_sync 校验误报**("tdxstat=0 条"假警告): 下载后惰性解析未触发 → `_validate_zhb_data` 强制访问 property

### 📤 GD 补传工具
- `reports/reupload.py`(gitignore 例外入库): 按日期核查未上传 md 批量上传; 已上传同名跳过;
  瞬时波动 30s 重试 2 轮; 名称从一章"股票名称/企业名称"提取(39 文件 0 缺失)

### 🔍 字段破解(采集 20260819/20260820, 20 股横截面)
- **push2 f50=量比**(20/20 与腾讯[49] 完全一致)、**f182=市场类型枚举**(主板2/创业5/科创32/北交80)、
  **f198=东财板块代码**(BKxxxx)、f121/f122=资金流衍生(与腾讯[71]/[62] 同源)
- 腾讯 [65]/[66] 静态排除项确认、f86 全局计数无信息量; ZHB tdxstat 全破解无新未知
- 字典登记: field_dict 12.3.1 正式表 + §零·B 矩阵重生成(914→920 字段) + script_data_dict 2.1

### 📦 采集与数据
- capture_field_probe 20260819(17 源 402s, thsdk 非交易时段 0KB 已知)/ 20260820(18 源 362s, ZHB=8/19)
- ZHB 8/18 包同步(zhb_sync, 7994 只); 8/19 报告核查: 章节全完整/数据逻辑 0 异常/000657 三报告交叉一致
- 回归 269 passed 持续通过

## [17.0.3] - 2026-08-17

**md 报告格式整体规划 + 数据修复 + 风控优化 + 离线预览工具**

### 🎨 md 排版整体规划(平面设计师视角, 摆脱 txt 遗留)
- 标题 ## 【X】/## [X] → ## X(去括号); ➤ 小节 → ### 三级标题; ├─/└─ 树形 → md 列表
- 表格渲染修复: 表格前+后双向空行(4 出口统一)——"标题被并表/表格未渲染"根因
- **#N** → **N.**(渲染器 # 高亮红色消除); 涨停板块分布竖排(避开表头加粗)
- 头部拆分(报告名/时间+时段分行)+ 报告名加粗; 时间 %H.%M.%S(分钟红色消除)
- 字段值对齐块 → 2 列表格(行内多字段拆分); 状态行(emoji)不转表; 独立分隔线去除
- 表格使用原则: 多列数据用表格(明细/天梯/轮动/资金/财务/席位/北向/两融/大宗/股东户数);
  枚举/状态/提示竖排文本; 单列行移出表格(rest 截断)

### 🐛 数据与逻辑修复
- 虚涨段恒空根因: 主力批量段仅在 ZHB 路径执行, 盘中 TDX 路径不跑 → 上移两路径统一
  (A 段 ulist f62+f66 真主力口径, 虚涨段恢复)
- 涨停天梯失败: 开盘红日期 今天-1(周一取周日空) → 最近交易日+向前找
- 同花顺独家/大宗交易/席位/股东户数/ROE 表 空格粘连 → 脚本直接 md 表格
- fflow 域顺序 push2delay 优先(策略20 逐股不再先打 push2 主域, 封禁风险源)
- val 策略展示 5→10 只; _top5_sorted → _top10_sorted 正名

### 🛠 工具与工程
- scripts/fmt_preview.py: 零网络格式预览(重转报告/喂模拟行)
- 删 20 死函数+8 未用 import(三轮全仓核查闭环)
- 回归 269 passed 持续通过

## [17.0.2] - 2026-08-16

**修复: 休市行情 OHLC 缺失 + 涨停池源切换 + 表格原则定稿 + 三轮全仓审查闭环**

### 🐛 数据修复(canonical)
- 休市/盘前 OHLC/成交额恒 0: _extract_with_source 去 need_realtime_quote 门控 +
  zhb_default 修复(amount 键名不匹配) + prev_close 反算(price/(1+chg), 加 0.5~2x sanity) +
  TDX 本机 .day 兜底(get_tdx_day_tail, 零网络) + 批量命中 TDX 补缺
- 盘口异动涨幅恒 0(levistock 字段 i 解析错误) → 修复后按用户原则**移除采集**(sht/mak 零 push2ex)

### 🔄 涨停池源切换(同花顺优先 + push2ex 兜底)
- ths_limit_up_pool 升格优先源: 空日期回退最近交易日; 17 字段(原因/板型/封板率/炸板次数/
  换手/流通市值/封单量/末封/回封/市场类型/新股, 一次请求零额外压力)
- 板块分布: TDX 本机 tdxhy 一级行业注入(零网络, 进程缓存); 炸板/跌停池保持东财
- 缓存 category 升 limit_pool_v2(字段变更强制失效); mak 封板时间双键兼容;
  休市日三池日期口径统一(封板率 100% 假象修复)

### 🎨 表格原则定稿(用户)
- "字段: 值"竖排(基本信息/行情/估值)不表格化; 仅横向数字列对齐章节(同业/资金/龙虎榜)用表格
- sht/lng 表格回退; 上市日期唯一来源 list_date

### 🔍 三轮审查闭环(2H+10M+11L, 20 死函数清零)
- med 板块内排名 NameError(永久静默失效)修复; mak 资金流验证段覆盖行删除
- 研报 None 崩溃/EPS 守卫 >=4/解禁单位统一(F10 万→股)/val 策略14 单位分键/
  to_thread 14 处/死 import 8 处/backtest 死函数
## [17.0.1] - 2026-08-15

**补丁: 字段增强实施(P0-P4) + 三轮代码审查闭环 + 全量 md 化 + 运行修复**

### 🆕 字段增强(P0-P4, 基于已破解字段池)
- **mak**: 主力净额 ulist 批量 f62+f66(=f137+f140 特大+大单, 20/20 实锤, push2delay 域, 元口径带符号)→
  板块聚合/A 段看板同源; 北向宏观资金(to_thread+降级标记)
- **sht**: 连板追踪 ZHB[31] 真连板数(双日铁证)+涨停类型[33]+官方封单额[4]; 3日涨幅估算降兜底
- **val**: 21→23 策略——策略22 业绩预增(get_yjyg_all 全市场分页, ADD_AMP/IS_LATEST/日期缓存)+
  策略23 盈利预期(本机 ProfitForecast O(1) 索引+股东户数 local_only)
- **lng**: 机构一致预期(本机 ProfitForecast 优先)
- **数据层**: zhb_client 暴露涨停族; get_em_batch_quotes +f62/f66(secids 参数修复);
  get_eps_forecast 本机索引+local_only; get_yjyg_all; eastmoney_datacenter page_index

### 🐛 三轮审查修复(2×python-reviewer + 运行复盘, 50+ 项)
- **CRITICAL 类**: mak 主力单位 1e4 倍; data_provider TDX 兜底 T-1 单位 10000x;
  med 北向占比 100 倍; get_eps_forecast 缓存失效+5000 次扫描; ulist 参数 fs→secids(data:null);
  **val bypass 模式 price 全缺 → 10 策略 0 命中**(.day 尾部快速读补价, 终审修正 ÷1000→÷100);
  mak A 段 ZHB 兜底单位; GD 补传脚本 .md 适配
- **限流**: get_em_batch_quotes push2 主域→push2delay 镜像域; get_yjyg_all 全市场一次分页;
  strategy_23/holder_change local_only 禁网络; mak/val async 阻塞 to_thread 4 处
- **缓存**: ProfitForecast O(1) 索引+锁; 业绩预告日期缓存; _KLINE_PRICE_CACHE
- **契约**: holder_num/ADD_AMP/IS_LATEST/zt_type 0 值 等

### 📝 全量 md 化(C 方案)
- 新增 stock_common/md_render.py 渲染层转换器(标题/分隔线/F10 边框表/空格表数据驱动切分/安全回退);
  5 脚本写尾 render_md_report, 输出 .md(纯文本兼容); val [NN 名称] 标题支持

### ✅ 回归
- 269 passed / 45 deselected, 0 failed

---

## [17.0] - 2026-08-13

**里程碑：全盘重构(core/ 包化 + v9.6 清理) + 字段命名规律破解 + 运行核查修复。**

### 🗂️ 目录整理
- 7 支撑模块包化 `core/`(全仓 ~150 import 统一 `from core.X`, `__init__.py` 空防循环, CLI 改 `-m`)
- v9.6 遗产清理(目录/SKILL/3 对比工具/孤儿 db); 凭据归位 `credentials/`; README 体系补全(45 条目→分层)

### ♻️ 代码重构(S1-S8)
- **S1 死代码 ~1000 行**: 21 zhb 转发+sc_zhb+12 dp 包装+composite 链 220 行(__all__ 255→230)
- **S2 传输层统一**: _request_with_retry→_quick(别名+4 点迁移); _async_quick EM/GEN 分流(限流语义保留); 进程间隔 2 核心+4 薄包装
- **S3 市场代码**: em_secid_prefix(修北交所 92 secid bug); is_a_stock 下沉; _market_code 补沪 B
- **S4 数据源合并**: getharden 三版合一(get_ths_hot_raw 唯一入口); cninfo 公告下沉(keywords 参数)
- **S5/S8 样板**: 写尾/ST 标注/多评委(sc_render)公共化; 缓存适配器删除
- **批量骨架收敛**: 基类 `execute_batch_pipeline`(prefetch/快照/上传钩子); ts 基类统一

### 🔬 字段字典破解(命名规律: 拼音/英文/中英混合)
- **双源实锤 20+ 组**: ConZAFDateNum=streak_days、ZAFYear/Pre20/Pre60=ytd/20d/60d、Yield/OpenAmo=主力净流入(双单位)、
  gb_info Zgb/Ltgb 股本、f137-146 四档资金流全定位、f162=动态PE/f163=静态PE(TTM)(茅台 Q1 年化精确)、
  f174/f175=52周(腾讯 [67]/[68] 三源一致)、f191=委比%(原"×100"修正)
- **"N日"口径实锤**: change_5d-60d/ytd 全交易日(开盘日)口径(日K 精确匹配); change_30d=历史遗留 key(实为 20 日值)
- **tdxstat2 [4]/[6]/[8]=涨停封单额三日滚动**(涨停池 92/92 全覆盖); 21 列全映射
- **通达信行业体系**: 细分行业=X 码(名称≈申万三级); ZHB [13]=881 行业板块/880 概念·风格双段; 地区不在 ZHB
- **vzangsu=量涨速%(TDX 表头同名实锤)**; ZAFPre 系列口径(PreN=交易日区间/D=当日/MyMonth=上月最后交易日)

### 🧪 统一层与运行修复
- 主力净流入**全链统一 f137**(腾讯 tx75 反向警示入字典); PE 动态=f162(腾讯静态剔除); 行业仅认 881 段(防 880 概念污染)
- main.py 固定超时→**输出活性检测**(持续输出无限等待, 无输出 900s 判卡死); sht 上传与 med/lng 统一
- 性能: prefetch 命中跳过 TDX; push2delay 补取进程缓存(同股二次 2.3x)
- 测试隔离: conftest 补拦 Session.get/post
- script_data_dict.md 全量重写; 全量回归 **302 passed / 45 deselected, 0 失败**

> 详细执行轨迹: docs/V17.0_REFACTOR_PLAN.md / docs/field_verification/20260813/(analysis+映射表) / docs/session_notes/20260813.md


## [16.4.1] - 2026-08-12

**里程碑：字段实测验证流水线落地 + TdxQuant 官方 88 字段交叉破解 + 报告数据质量 19 项修复 + 编码体系治本。**

### 🎯 字段验证流水线(每日记忆锚点体系的实证来源)

- **固定股票池** `docs/field_verification/pool.json`：20 股(固定 15 + 动态 5,沪深/创业/科创/北交所/ST/银行/连板全覆盖)
- **采集脚本** `scripts/capture_field_probe.py`：19 源全字段(本地 ZHB + TDX/F10 + 腾讯 88 + push2 114 + ulist 239 + 新浪 34 + AxData 34 + 财联社/KPL/板块轮动/涨停池/人气榜/datacenter/巨潮/研报/thsdk/TdxQuant)
- **首次采集** `docs/field_verification/20260812/`：19 raw 文件 + meta + analysis + field_analysis
- **防封**:push2 失败不重试 + 连续 3 只失败域级熔断切 push2delay(2026-08-12 二次封禁复盘根因:失败连接重试叠加 ~300 次)
- **sc_datasource.em_hot_rank** push2 → push2delay 镜像域(封禁期整体失败修复)

### 🔬 TdxQuant 官方对照破解(通达信客户端 PYPlugins tq 库,18 只全样本)

- **18/18 实锤**:Col[3]=StaticPE_TTM(pe_dynamic 历史遗留名)、Col[9]=MorePE、Col[10]=DYRatio、Col[14]=KfEarnMoney、Col[15]=StaffNum、Col[24]=CashZJ(**单位=万元,原"(元)"错误**)、tdxstat2[16]=IPO_Price、[17]/[18]=HisHigh/HisLow
- **破解**:tdxstat [26]=YearZTDay 年内涨停天数(18/18)、[32]=LastZTHzNum(2/2)、[31]≈LastStartZT、[23]=当日异动类型码、tdxstat2 [4]/[6]/[8]=同一资金字段三日滚动序列(T/T-1/T-2)、tipinfo [10]=DTDate_Recent
- **tipinfo 官方字段名实锤**(600519 单样本):Col[5]=ZTDate_Recent、[6]=TopDate_Recent、[13]=RecentReleaseDate、[19]=RecentHGDate
- **采集**:`C:\new_tdx64\PYPlugins\user\field_verify_tdxquant.py`(需通达信客户端运行)
- field_dict.md 全量回写 + 精简(多轮测试描述压缩为"含义+状态+一句证据")

### 🐛 核心 Bug 修复

- **ZHB 下载永不更新**:`_zhb_needs_download` 循环依赖(stock_calendar.is_workday 反向调 get_zhb → 递归爆栈)→ 改用本地包节假日表;+"每天最多下载一次"标记(成功才标记)
- **val 崩溃 KeyError('zhangfu')**:get_val_report L1880 复制粘贴残留(`_th["zhangfu"]` 在 elif 分支必崩)

### 📊 报告数据质量修复(19 项,基于 41 个报告文件逐份审查)

- **sht GD 丢失**:36 只批量超时被 kill 时批量上传未执行 → 改**逐只上传**(提前 init_gd,生成即传)+ main.py 单股超时 30s→45s
- 封板时间 "92:50" 格式错(5 位字符串切片)→ 统一 int 解析
- 新股首日无涨跌幅限制(+662%)→ mak 上市<3 日跳过偏离判定 + val 标注
- sht 主力资金占比 222%(abs 掩盖方向)→ 保留符号+超成交额异常标注+来源标签修正
- 北向 degraded 警告未展示(深股通 379 亿异常)→ sht/med 渲染 data_quality 警告
- med 资金流仅 1 天却下"吸筹"结论 → <5 天数据不下中线结论
- lng:人效比单位 元→万元、PE-TTM 来源口径标注、PEG 跨期标注、分红"距今 N 年"、互动易答案 None、净利率>100% 双源核验标注
- val 策略09 名称当代码(昀冢科技 (昀冢科技))→ 无 6 位代码 leader 走成分股路径
- med 同业本股 *ST 名称统一;同业亏损股 PE 显示"亏损"(原 0.0)

### 🛠 工具与规范

- **GD 补传工具** `scripts/upload_reports_to_gd.py/.bat`(reports/ 自包含副本):已存在跳过只传缺失,实测 39 上传/6 跳过/0 失败
- **编码体系治本**:
  - Python 入口全量 `ensure_utf8_stdio()`(env_setup.py 下沉,17 入口)
  - .ps1 四行 UTF-8 头部 + **BOM 铁律**(PS 5.1 无 BOM 按 GBK 解析)
  - **管道禁令**:禁止 python 输出接 PS 管道(PS 5.1 分块解码破坏多字节字符,实测根因)
  - bat 纯 ASCII+CRLF 铁律(cmd 按 ANSI 解析 UTF-8 中文注释致整文件错乱)
- **AGENTS.md v1.2 重构**:合并落盘规则、清理过时内容/已完成待办、修正 bash grep/废弃变量引用
- **每日会话纪要体系**:`docs/session_notes/YYYYMMDD.md`(详见 docs/session_notes/README.md)



**里程碑：字典架构重构 + 三大客户端逆向（东财/通达信/同花顺）+ 统一层加固 + 场景化批量优化。**

### 🔧 字典架构重构（主字典=决策层，附录=实证层）

- `docs/verify/` 附录目录：主字典只留结论，实测值/样本/破解数据迁入附录
  - push2_verify（12.9.1 全字段破解表）/ axdata_verify（666 字段矩阵）/
    samples_verify（24 股样本）/ tencent_verify（88 字段复核）
  - field_dict 358KB→284KB（-21%）；12.15.9 附录索引表
- **script_data_dict 全量重构**：5 脚本行号重定位（mak 1798/val 2131/sht 1740/med 1256/lng 1135）
  + 逐字段 fallback 链实测更新 + §七 12 项断点（8 项已修）
- **客户端逆向三附录**（统一 docs/verify/）：
  - `network_servers.md`：三源服务器清单（通达信 connect.cfg 全表 HQHOST 43/
    同花顺 123ths 域名族 9 域 ~80 IP/东财 SSO）+ 移动线路实测
  - `client_fields_enum.md`：客户端字段枚举全景（东财 950+/通达信 tdxstat
    35 列破 14/tdxstat2 21 列破 13/同花顺 F10 文本+thsdk 口径铁证）
  - 数据文件入库 `docs/verify/data/`（connect_cfg/dns_cache/复测结果）

### 🐛 脚本断点修复（8 项）

- mak：9.5 涨停分档×3 统一 limit_pct_for、板块 mcap_yi 腾讯注入+计算兜底、
  main_net_amount 取 ZHB、盘口异动死代码移除
- val：_sfmt 01-21 映射重建（14 号回归）、行业排名升级 O25（四脚本收敛唯一实现）
- sht：地天板预警 limit_down_price 修正、ff.iloc 死分支、**bid1_vol 入 canonical
  全链路**（封单资金/信号/预警复活）、_is_dict 死分支清理
- **PB 口径统一**：val 04 pb_ths 降级校验，全脚本收敛 canonical（腾讯/push2
  除息口径），THS 静态口径仅差异告警

### 🔍 客户端逆向发现（服务器 + 字段 + 铁证）

- **通达信 tdxstat/tdxstat2 官方原始文件 35/21 列破解**：ipo_price（茅台 31.39）、
  52周高低（=腾讯精确）、PE 双口径（Col[3]=动态/Col[9]=TTM 实时验证）、
  涨跌幅序列（5/10/20/30日 + ytd 多股全中）、amount_1d/2d（昨日/前日成交额）
- **同花顺**：123ths 域名族、stockname 名称库、F10 文本库（五期财务）、
  **thsdk 市净率=现价/最新期 BPS 铁证**（F10 文本 4 位小数精确）、
  get_ths_market_snapshot query_key 修复（汇总→扩展1）
- **TDX 服务器 74 台复测**：FULL 6 台（新增 120.76.152.87），白名单更新
- 东财 DataCenter.dll 725 协议字段 + 自选 118 字段三层映射

### 🛡️ 统一层加固（回应"规范管不住持久状态"）

- **share_capital 旧单位 bug**：6467 条"股"单位缓存（V16.2.3 修正前 8-03 批次）
  导致 canonical mcap 放大 1e4——清理 + **缓存 schema 版本化**（规范变更自动失效）
  + **canonical 量级校验**（股本>1e7 自动股→万、mcap>1e6 自动万→亿，与 pe 过滤对称）
- zhb_client tdxstat 映射与 12 股 F10 验证 100% 吻合（统一层无需改代码）
- 缓存同步：tdx_hosts_cache 6 台 FULL

### ⚡ 场景化批量优化（sht 30 只核心需求）

- **prefetch_quote_batch**（push2delay ulist 300/批）：sht 批量 1-2 次请求预取
  30 只核心行情，canonical 命中跳过 TDX 逐股；估值字段按需腾讯单股补齐
  （实测 ulist 不返回估值字段）
- 矩阵增加场景维度：单股深度（TDX 优先）/ 批量行情（ZHB+腾讯批量）
- UA 补全标准浏览器指纹（5 处）+ 东财 IP×子域封锁排查（push2 系与 delay/ex 独立）

### ✅ 验证

- 全量测试 339 passed, 2 skipped（多次基线一致）
- 东财接口健康探测脚本 `scripts/check_em_health.py`（低频防封锁）
- AGENTS.md §12 活跃待办（push2his 恢复复测提醒）


### 近期版本(V16.3-V16.2, 详细内容见 docs/session_notes/)

- **[16.3.8]** (2026-08-11): 东财 IP 封锁排查 + 新 IP 恢复核验（换光猫后）。
- **[16.3.7]** (2026-08-11): PB 口径统一：val 04 双通道收敛（回应统一层设计初衷）。
- **[16.3.6]** (2026-08-11): PB 多源实证归因 + THS 批量通道修复（盘中三股实测）。
- **[16.3.5]** (2026-08-11): 行业排名统一收敛 O25 + 资金流单位契约清理（回应字典 §七 剩余项）。
- **[16.3.4]** (2026-08-11): 脚本断点修复 8 项（script_data_dict §七 12 项中 8 项落地）+ bid1_vol 入 canonical 全链路。
- **[16.3.4]** (2026-08-11): script_data_dict 全量重构：5 大脚本按当前代码重定位（ful 删除确认）。
- **[16.3.3]** (2026-08-11): 字典架构重构：主字典=决策层，附录=实证层。
- **[16.3.1]** (2026-08-06): V16.3 O 系列：F10 财务接入 + 字典全面破解 + 东财限流治本 + 统一层梳理。
- **[16.3.0]** (2026-08-05): 全项目审查整改（74 文件核查，用户批准全改）+ 文档/依赖清理。
- **[16.2.0]** (2026-08-05): V16.2.1-V16.2.18 连续迭代：报告正确性 + 东财分域限流 + 缓存版本化 + 行业统一申万二级 + ZHB 字段破解。

### 历史版本归档(V16.1 及以前, 详细内容已归档)

| 版本 | 日期 | 里程碑 |
|:---|:---|:---|
| 16.1.9 | 2026-08-05 | ST 涨跌幅规则修正（5%→10%）。V16.1.7 曾误按 AxData 文档旧快照 `st_5pct` 将 ST 阈值改为 5%； |
| 15.4.3 | 2026-07-31 | easy_tdx 字段探测 + tdx_field_dict 字典 + V15.5 移植规划。基于用户反馈"全部更换为 mootdx 接口后数据获取并不稳定"，调研 [easy_tdx v1.20.4 |
| 15.3 | 2026-07-29 | 全量健康修复版本。基于 2026-07-29 跑 000100 时的全量根因分析（X1-X8 共 8 个 P0/P1），结合第三方 deepseek 评审报告的逐条核查，对剩余 9 个 P0/P1 + |
| 15.2 | 2026-07-28 | P0 崩溃修复 + 缓存保护强化 + ZHB 交叉验证恢复版本。基于 2026-07-28 20:29 批量运行日志的深度根因分析，重点修复 V15.1 引入的 `board` 变量未初始化导致的 3 |
| 15.1 | 2026-07-26 | 全全局 ZHB 旁路普及与并发线程池隔离深化版本。将基于真实周期的 ZHB 时空路由矩阵全面普及至 6 大报告脚本（`sht`/`med`/`lng`/`ful`/`mak`/`val`），修补盘后  |
| 15.0 | 2026-07-26 | 标准化数据中心与 ZHB 离线优先架构重构大版本。完全收敛多源行情异构数据，引入强类型数据合约 `CanonicalStockData`，实施基于真实生成周期（T+1 清晨 06:00 前）的 ZHB |
| 14.0 | 2026-07-22 | V13.x Bug 修复 + 文档全量同步版本。不引入新功能。 |
| 14.2 | 2026-07-22 | ZHB 数据集深度集成版本。基于 `field_dict.md` 第三节第 4 小节新挖掘的 6 个 ZHB 数据集（profile.dat / tdxchain.cfg / neednote.dat |
| 14.2.1 | 2026-07-22 | Gemini 深度静态分析后修复的 3 个边界隐患 + 1 个架构一致性提升。不改变 VERSION 编号（仍是 14.2）。 |
| 14.3 | 2026-07-25 | 性能优化版本。针对 val 报告周日首次跑 15 分钟卡死的实际问题，从 P0/P1/P2/P3 四个层面完整解决"网络请求风暴"问题。 |
| 14.3.1 | 2026-07-25 | 根据用户对缓存机制的两点深入分析，对 V14.3 缓存架构进行精细化重构。不改变 VERSION 编号（仍是 14.3）。 |
| 14.3.2 | 2026-07-25 | Top-N 数据驱动回测。用 4 天 ZHB 数据（cache/zhb/zhb_202607{21,22,23,24}）回测 12 个策略在不同 top_n 下的选股质量，给出"按策略差异化 top_ |
| 14.2.2 | 2026-07-25 | 针对 Gemini 报告的两个实际运行异常（`val` 脚本 `NameError` + `mak` 脚本 `0只` 与卡死），进行深度根因修复。不改变 VERSION 编号（仍是 14.2）。 |
| 14.2.3 | 2026-07-25 | V14.2.2 的修复不完整——`_check_tdx()`（健康检查函数）仍使用 `bestip=True`，导致 val 报告（`strategy_10_contrarian_value` 调用  |
| 13.2 | 2026-07-22 | 无重大破坏性变更。V13.2 仅追加文档与脚本。 |
| 13.2 | 2026-07-22 | V13.0/V13.1/V13.2 三阶段引入 dataclass 形式的数据容器，作为 V12.x dict 的可选升级路径。 |
| 13.0 | 2026-07-22 | 无重大破坏性变更。V13.0 仅新增 `stock_common/sc_schema.py` 模块，不接入 data_provider。 |
| 13.1 | 2026-07-22 | V13.1 涉及缓存层行为变化（潜在影响）： |
| 12.6 | 2026-07-22 | V12.6 取消原计划的防投毒熔断机制（V11.5 时期实施），存在以下行为变化： |
| 12.5 | 2026-07-22 | V12.5 针对 V12.4 复盘发现的 3 大问题进行修正：消除 `get_med_report.py` / `get_lng_report.py` 中重复定义的 Runner 类、让基类 GD 上 |
| 12.3 | 2026-07-22 | V12.3 原计划引入三项深度架构演进，但在评估后决定挂起，未实际实施： |
| 12.4 | 2026-07-22 | V12.4 成功构建并全面应用 `BaseReportRunner` 引擎框架，彻底剥离6大策略报告脚本中约 1200+ 行重复的 CLI 解析、运行生命周期 Banner、Google Drive  |
| 12.2 | 2026-07-22 | V12.2 完成工程化优化任务清单，包括数据库连接优雅关闭、配置集中管理、全局异步Session单例、核心防线单元测试、三级日志规范落地。 |
| 12.1 | 2026-07-22 | V12.1 针对全量代码审查发现的问题进行修复，包括 L1/L2 缓存同步 Bug、静默异常日志化、容错层实际下沉、异步阻塞修复、未使用导入清理。 |
| 12.0 | 2026-07-17 | V12.0 完成 TCP 统一层重构，彻底删除 easy_tdx 依赖，实现"HTTP + mootdx"双通道架构。所有原 easy_tdx/MacClient 独有功能（板块、资金流、全市场快照） |
| 11.5 | 2026-07-17 | 历时多个版本规划，data_provider.py 统一数据中心层在 V11.5 正式全面激活，六大报告脚本全部完成迁移。同时新增三大防封机制，彻底提升网络稳定性。 |
| 11.4 | 2026-07-16 | 1. data_provider.py死代码清理：6个报告脚本（sht/val/med/lng/mak/ful）共47处`from data_provider import (...)`导入语句全部删 |
| 11.3 | 2026-07-16 | 通过7/15 vs 7/16报告对比发现，4个缓存分类在跨日运行时携带T-1数据混入T0报告： |
| 11.2 | 2026-07-16 | - clean_codes增加flag粘连警告：当股票代码参数中包含`--`时（如`601718际华--all`缺少空格），打印警告提示用户检查命令行格式，避免`--all`参数被误解析为股票代码 |
| 11.1 | 2026-07-16 | 1. 全市场成交额实时覆盖：val脚本加载全市场数据时，用腾讯实时行情的`amount_wan`覆盖ZHB的T-1成交额，确保流动性排序和策略计算使用当日数据 |
| 11.0 | 2026-07-16 | - 所有报告脚本统一导入 Data Provider 模块： |
| 10.3 | 2026-07-16 | zhb 资金流向字段解锁（基于 zhb_analysis 深度分析 + 双日 Delta 验证 + 公式验算）： |
| 10.2 | 2026-07-16 | - 修复 cross_verify 读写互斥BUG（影响14个分类：concept_blocks/lockup_expiry/basic_info/financial/balance_sheet/ca |
| 10.1 | 2026-07-15 | - zhb字段映射重大修正（基于injoyai/tdx开源仓库源码验证）： |
| 10.0 | 2026-07-14 | - zhb全局配置总包全面升级： |
| 9.6 | 2026-07-13 | - mootdx依赖集成：`requirements.txt` 新增 `mootdx>=0.11,<1.0`，与 easy-tdx 形成互补关系 |
| 9.5 | 2026-07-13 | - 静默异常日志化（28处）：`tdx_client.py`（23处）、`gd_uploader.py`（4处）、`get_med_report.py`（1处）共28处 `except Excepti |
| 9.4 | 2026-07-11 | - VERSION文件单一来源版本号管理：项目根目录新增 `VERSION` 文件（内容为 `9.4`），`stock_common/sc_utils.py` 新增 `get_version()` 函 |
| 9.3.3 | 2026-07-10 | - GD上传路径混乱：`get_or_create_drive_folder` 增加 `'{parent_id}' in parents` 严格约束，`get_val_report.py` 移除 `g |
| 9.3.2 | 2026-07-09 | - TDX K线假数据导致指数涨幅全N/A和异动检测全为0：约50%的 easy_tdx 内置TDX服务器K线接口返回假数据（响应头 `ret_count=800` 但 body 为 0 字节），导致 |
| 9.3.1 | 2026-07-08 | - sht 脚本 `'float' object is not subscriptable` 崩溃：`ff["data"]` 存在多态（TDX 返回 `List[dict]`、东财 fallback  |
| 9.3.0 | 2026-07-07 | - 盘前行情模式（`tdx_client.py`）：9:30前自动使用上一交易日日K线数据，避免实时接口返回 0 导致涨跌幅计算为 -100% |
| 9.2.0 | 2026-07-05 | - 缓存交叉验证机制（`stock_cache.py`）：11 个多天 TTL 分类启用 `cross_verify=True`，两次获取数据一致才标记为已验证，防止意外错误数据被缓存 |
| 9.1.1 | 2026-07-04 | - ful 评分 theme→holder 映射 bug：`get_ful_report.py` 中 `_scoring()` 返回值用 `"theme"` 作为键名，但实际取自 `dims.get( |
| 9.1.0 | 2026-07-04 | - F10 全覆盖工程：用通达信 F10 协议替代/补充现有 HTTP 接口，降低东财限流风险，详见 `docs/TDX_F10_ROADMAP.md` |
| 9.0.0 | 2026-07-02 | - 舆情互动层（Layer 10）：新增 `cninfo_irm()`（互动易问答）、`ths_hot_list()`（同花顺热榜）、`em_hot_rank()`（东财人气榜）、`em_hot_co |
| 8.9.0 | 2026-06-29 | - 版本号统一升级：所有脚本版本从 V8.8/V8.7 统一升级到 V8.9 |
| 8.8.0 | 2026-06-25 | - GD上传逻辑统一化： |
| 8.7.0 | 2026-06-25 | - 删除 `social_sentiment.py`（6 平台社交热榜聚合，全为桩实现返回空数据） |
| 8.6.0 | 2026-06-24 | - stock_common.py：新增 _DOMAIN_LAST_TIME 线程锁保护，彻底消除多线程竞态条件 |
| 8.5.0 | 2026-06-22 | - 新增龙虎榜席位增强模块 `seat_db.py`： |
| 8.4.0 | 2026-06-22 | - 新增 `stock_cache.py` 统一缓存层（SQLite + TTL 自动过期 + LRU 清理） |
| 8.3.0 | 2026-06-18 | - 修复北向资金持股占比显示超100%问题（`get_sht_report.py`/`get_med_report.py`中`_ratio*100`改为`_ratio`，东方财富API返回的`hold |
| 8.2.0 | 2026-06-18 | - 修复 `300274` 等股票因 lines 列表中存在 None 值导致 `join()` 报错的问题（在所有脚本的 `join()` 调用前添加 `filter(None, lines)` 防 |
| 8.1.0 | 2026-06-18 | - 新增统一评分接口：`ScoreData` 数据结构、`ScoreResult` 结果结构、`calculate_score()` 主函数，统一管理 sht/med/lng/ful 四种评分类型的计 |
| 8.0.0 | 2026-06-17 | - 初始版本，包含6个报告脚本（sht/med/lng/ful/val/mak） |
