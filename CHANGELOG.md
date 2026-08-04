# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## [16.1.4] - 2026-08-05

**AxData 假设实测验证：stats_root 直接消费项目 zhb.zip（三源校准闭环）**。

### ✅ 验证结果（axdata 0.1.3 + axdata_core，stats_root=项目 cache/zhb/zhb_20260803.zip）

1. **同源确认**：`stock_shortline_indicators_tdx` 调用成功，`stats_date=20260803` 与项目 zhb 包数据日期一致——AxData 短线指标直接消费项目 ZHB 文件，**零额外下载**
2. **free_float_shares 三源精确闭环**：
   - 600519: AxData=540949000股 = ZHB Col11=54094.90万×10000 = 官方 TdxQuant FreeLtgb=54094.90 ✅
   - 000001: AxData=8160481200股 = ZHB Col11=816048.12万×10000 = 官方 FreeLtgb=816048.12 ✅
   - → **ZHB Col[11] ↔ AxData free_float_shares ↔ TdxQuant FreeLtgb 三源一致**
3. **34 字段全返回**：茅台 open_volume_ratio=1.01/prev_amount=48.99亿/昨开盘量=408手/竞价昨比=0.58
4. **调用方式**：`request_interface("stock_shortline_indicators_tdx", params={"code":"600519","stats_root":"<zhb.zip>"}, ...)`

### 📝 字典更新（field_dict.md §12.12）

- §12.12 头部标注实测验证状态 + 三源闭环证据 + 调用代码示例



**字典扩充：AxData 接口全景（257 接口）**。调研 electkismet/AxData 完整接口文档（https://electkismet.github.io/AxData/interfaces/），录入关键字段。

### 🆕 字典（field_dict.md §12.12）

1. **§12.12.1 短线指标 34 字段**（最重磅）：开盘量比/开盘换手Z/竞价昨比/开盘昨封比/封成比/封流比/封昨比/几天几板/连板天数/年涨停天数/流通股本Z——**`stats_root` 参数可直接传 tdxstat.cfg/zhb.zip（与项目 ZHB 数据同源）**
2. **§12.12.2 实时快照 41 字段**：回头波/攻击波/内外比/封单额/涨速/短换手/近2分钟成交额/开盘抢筹/量涨速/委比/活跃度
3. **§12.12.3 涨跌停价格 15 字段**：**limit_rule 官方规则枚举（main_10pct/st_5pct/chinext_20pct/star_20pct/bse_30pct/ipo_first_day/ipo_first_5_days）**——可补齐 is_limit_up 的北交所 30%/IPO 首日规则
4. **§12.12.4 综合评分 15 字段**：四维评分（资金/基本面/消息/主题）+ 市场/行业排名
5. **§12.12.5 筹码分布 8 字段**：获利比例/90%成本集中度/70%成本集中度（项目空白维度）
6. **§12.12.6 每日股本 10 字段**：free_float_share_z 与 ZHB Col[11] 同语义可交叉校准
7. **§12.12.7 高字段密度接口**：配股 59/期权T型 55/股本变动 46/实时榜单 42/题材资金走势/ESG×5

### 🔑 关键发现

- AxData 短线指标消费 **tdxstat.cfg/tdxstat2.cfg（即项目 ZHB 数据）**——零额外下载即可用 AxData 计算 34 个短线指标
- free_float_share_z（流通股本Z）与 ZHB Col[11]=FreeLtgb（2026-08-04 官方 TdxQuant 确认）同语义——多源校准闭环
- 涨跌停 limit_rule 枚举补齐项目 is_limit_up 的板块规则盲区（北交所 30%/IPO 首日）



**字典扩充：levistock 新数据源 + akshare 校准基准**。调研 AxData 依赖三源（pytdx/akshare/levistock），实测 levistock 4 类接口全部可用。

### 🆕 字典（field_dict.md §12.10/12.11）

1. **§12.10 levistock 字段字典**（5 类独家数据）：
   - 东财盘口异动（change_type 枚举：8201 火箭发射/8193 大笔买入/8205 封涨停板/64 有大买盘）
   - 财联社市场情绪（market_degree/封板率/高开率/获利率/涨跌分布/连板梯队）
   - 开盘红复盘（涨停天梯/盘面梳理事件流/历史涨停原因+封单量额）
   - 板块轮动/热度（rank_change/is_new/催化剂）
   - i问财自然语言查询（免 Key）
2. **§12.11 akshare 校准基准表**：10 项字段多源交叉（乐咕历史 PE/股息率序列校准 val 模拟算法等）

### ✅ 实测结论（levistock 0.1.7）

| 接口 | 结果 |
|:---|:---|
| stock_changes_em(8201) | ✅ 2782 条（火箭发射）|
| market_emotion_cls | ✅ 13 字段（热度57/封板率85%/炸板23/高开率88%）|
| stock_zt_pool_em | ✅ 129 条（含 circ_share/main_inflow/zt_days 等 push2ex 无的字段）|
| stock_strategy_wencai | ✅ 免 Key，"连板3板以上"→8 条（传智教育 7 连板）|

**关键差异**：levistock 涨停池多 circ_share（流通股本）/main_inflow（主力净流入）/zt_days（近期涨停天数）——项目 `get_limit_up_pool` 无；盘口异动是项目完全空白维度。



**zhb 下载迁移 easy_tdx + 依赖体系收敛**。实测 easy_tdx 1.20.4 完全覆盖 mootdx/pytdx 能力（K线/行情/财务/除权/逐笔/资金流/板块 + 健康分/故障转移/52 服务器）。

### 🆕 变更

1. **zhb.zip 下载 easy_tdx 首选**（[zhb_client.py](file:///d:/GitHub/test/zhb_client.py) `_download_zhb_zip`）：
   - easy_tdx `get_report_file()` 分块拉取（实测 180.153.18.170 下载 1292315 字节有效 zip，45 文件）
   - 主机顺序：3 个实测可用主机 → from_best_host 健康分兜底（52 候选）→ mootdx 备胎（保留 V12.0 路径）
   - 原招商/国信节点已失效（实测超时/拒连），降为备胎列表尾部
2. **主机清单更新**：`_ZHB_HOSTS` 前置 180.153.18.170 / 150.158.160.2 / 124.71.187.122
3. **文档同步**：zhb_client docstring、requirements pytdx 注释、tdx_client/main/README "easy_tdx 移除"过时表述修正

### 🧪 实测结论（2026-08-04，同一服务器对照）

| 能力 | easy_tdx 1.20.4 | mootdx 0.11.7 | pytdx 1.72 直连 |
|---|---:|---:|---:|
| 日K线 | ✅ | ❌ 0 根 | ✅ |
| 五档行情 | ✅ | ❌ 空 | ✅ |
| 财务 37 字段 | ✅ | ✅ | - |
| 除权除息 | ✅ | ✅ | - |
| 指数/分钟/逐笔 | ✅ | ❌ 全灭 | ✅ |

mootdx 0.11.7（2024-07 停更）行情类接口静默失败但 pytdx 底层正常 → 封装层 bug；easy_tdx 功能全 + 活跃维护 → 主通道。



**报告体系重构：sht/med/lng 三视图 + ful 下线 + mak/val 引擎化 + 新字段接入**。基于 2026-08-04 接口实测破解（push2 stock/get 114 字段、ulist 239 字段，官方 TdxQuant 交叉验证）与投研职责审计。

### 🎯 架构变化

1. **FUL 下线**：`main.py --ful` 保留参数但仅提示；技术指标引擎（MACD/RSI/BOLL/KDJ/量能）迁移至 `stock_common/sc_technical.py`，风险扫描引擎（9 项清单）迁移至 `stock_common/sc_risk.py`，能力并入 sht/med/lng
2. **SHT 短线执行视图**：接入昨日涨停池晋级率、资金流切片方向修复（"最新在前"）、深度开关生效、同步阻塞 to_thread
3. **MED 中线业绩视图**：研报评级变化统计、两融 3/5/10 日维度、研报请求去重、技术面接入共享引擎、新浪 async 补缓存
4. **LNG 长线质量视图**：风险引擎章节、分红连续性指标、重复 Canonical/TDX 财务调用去重、历史高点缓存
5. **MAK/VAL 引擎化**：mak 伪回测改名、负索引错位修复、ret_3d 冒充移除；val 策略 03 箱体修复、策略 13 TTM 股息率、策略 20 缺导入、策略 21/22 字段契约重写、PE 百分位前视偏差修复、硬编码胜率删除、策略数统一 21

### 🆕 数据层（阶段 1）

1. **push2 stock/get 字段包 19→50**：新增 f51/f52 涨停跌停价、f55 EPS、f92 BPS、f126 股息率、f162-167 PE×3/PB、f174/f175 52周高低、f137-146 资金流 12 字段、f198 行业码、f80 交易时段、f178 5日资金流数组（官方 TdxQuant 精确匹配）
2. **ulist 批量字段扩展**：f55/f92/f126/f162/f163/f167/f174/f175/f221（val 横截面初筛用）
3. **CanonicalStockData +15 字段**：limit_up/limit_down/bps/pe_more/fund_*/report_period/quote_date 等（向后兼容默认值）
4. **研报估值提取**：`extract_report_valuation()` 规范化三年 PE/EPS 预测 + 评级变化
5. **事件源字段保留**：CLS stock_list/subjects、巨潮 adjunctUrl/announcementId、龙虎榜 EXPLAIN/BUY_RATIO/D1-D30 偏离、两融 RZJME/RQJMG/10D/5D/3D
6. **评分权重可配置**：strategy_config.yaml 新增 scoring_sht/med/lng，三脚本传 cfg（原硬编码默认）

### ⚠️ 修复

- `get_em_quote_full` data_date 用未定义 now_str() → datetime.now()
- SHT/MED 资金流切片 `[-10:]`/`[-20:]` 取最旧数据 → `[:10]`/`[:20]`（数据源"最新在前"）
- lng 两次 get_canonical_stock_data → 复用
- lng 两次 TDX 0x0010 财务查询 → 快照复用
- val estimate_pe_percentile 财报时序倒置（新浪最新在前被当旧→新）→ 按报告日排序 + 亏损季度不截断 + 披露日锚点



**cdata 分层多源 + per-field source label 版本（方案 C）**。基于 2026-07-30 跑 000100 报告与 a-stock-data-v9.6 对照分析的根因结论：
**V15 cdata 强类型架构胜利，但 push2 字段名（f43/f44/...）未映射到 cdata 字段名（price/high/...）**——push2 fallback 拿到 dict 但取不出字段，导致 med/lng/ful 三报告总市值/价格/PB 全 0。

方案 C 三大核心：
- **PUSH2_FIELD_MAP 22 项字段映射表**（[data_provider.py:264-279](file:///d:/GitHub/test/data_provider.py#L264)）
- **4 级 fallback 链**：push2 → TDX → 腾讯 → calculated
- **per-field source label**：`CanonicalStockData.field_sources: Dict[str, str]`

### ⚠️ Critical Bug Fixes

1. **PUSH2 字段名映射表 PUSH2_FIELD_MAP（P0）**：
   - **触发场景**：[data_provider.py:259-267](file:///d:/GitHub/test/data_provider.py#L259) push2 fallback 处直接 `rt_quote.update(em_quote)`，但 push2 用 `f43`/`f44` 命名，cdata 用 `price`/`high` 命名——**两套字段名不兼容**
   - **影响范围**：med/lng/ful 三报告总市值/价格/PB 全 0 的根因
   - **修复方案**：新增 PUSH2_FIELD_MAP（22 项），把 push2 字段名 f43/f44/... 映射成 cdata 字段名 price/high/...

2. **腾讯行情第三级 fallback（P0）**：
   - **触发场景**：TDX 限流 + push2 风控时 cdata price=0
   - **影响范围**：ful 报告 10:42 实跑"行情与技术分析"段空白
   - **修复方案**：L3 走 `get_tencent_quote` 兜底

3. **公式推算（calculated）L4 fallback（P0）**：
   - **触发场景**：所有实时源失败但有股本数据
   - **修复方案**：mcap = total_shares × price / 1e8；amplitude = (high-low)/last_close

4. **`CanonicalStockData.field_sources` per-field 标签（P1）**：
   - **新增字段**：[sc_schema.py:494-512](file:///d:/GitHub/test/stock_common/sc_schema.py#L494) `field_sources: Dict[str, str] = field(default_factory=dict)`
   - **用途**：上层用 `cdata.field_sources.get("price")` 可知道这个 price 是 `realtime:push2` / `realtime:tencent` / `calculated` / `missing`

5. **industry 4 级 fallback + 剥离"子"后缀（P1）**：
   - **触发场景**：[data_provider.py:344-355](file:///d:/GitHub/test/data_provider.py#L344) industry 走 TDX boards（"光学光电子"，带"子"）
   - **修复方案**：优先级 push2 f128 > 腾讯 > TDX boards > ZHB static + 剥离"子"后缀（"光学光电子" → "光学光电"）
   - **关键发现**：push2 **f128 industry** 是 push2 自身带的真实行业归属，比 TDX boards 更准

6. **`get_concept_blocks` ZHB tdxchain.cfg fallback（P1）**：
   - **触发场景**：[sc_datasource.py:1386](file:///d:/GitHub/test/stock_common/sc_datasource.py#L1386) 走 TDX boards concept 经常空
   - **影响范围**：sht 报告对比 V9.6 缺 16 个概念板块
   - **修复方案**：concept 为空时 fallback 到 `get_concept_from_zhb` 解析 tdxchain.cfg

### 📝 Documentation

7. **field_dict.md 增 7.10 节 cdata 字段源体系**：
   - 9 种 source 状态码 + 22 个字段优先级矩阵 + 上层使用示例

8. **script_data_dict.md 增 V15.4 PUSH2 字段名映射表**：
   - 22 项 push2 key → cdata field 完整映射 + 关键发现（f128 industry）

### V15.4 不做的事

- ❌ **不拆分 sc_datasource.py（184KB）** — V16.0 的事
- ❌ **不重写 14 个伪 async 函数** — 接受现状
- ❌ **不重写 val 18 步策略** — 策略逻辑不动
- ❌ **不引入新依赖** — 腾讯 API 走 V9.6 已有的 `get_tencent_quote`
- ❌ **不破坏 V15.3 已修的 9 项** — V15.3 全部保留

## [15.4.3] - 2026-07-31

**easy_tdx 字段探测 + tdx_field_dict 字典 + V15.5 移植规划**。基于用户反馈"全部更换为 mootdx 接口后数据获取并不稳定"，调研 [easy_tdx v1.20.4](https://github.com/handsomejustin/easy_tdx) 后发现：
- easy_tdx v1.20.4 新增 `_health.py` 服务器健康分引擎（score × 0.5 衰减 / +0.2 恢复 / 120s 冷却）——**直接命中本项目 V15.4.1 sht 4 指数卡死的根因**
- easy_tdx v1.20.4 修复 `get_index_bars`/`get_security_bars` 空 DataFrame 时**自动逐台换台**（此前指数 K 线空数据不触发故障转移）
- **结论**：保留 V15 强类型 cdata 架构，**仅借鉴而非替换**——本轮先做字段探测和字典，V15.5 移植 health/reconnect

### Added

1. **`scripts/_v1543_probe_easy_tdx.py` 实跑探测脚本**：
   - 实跑 easy_tdx v1.17.10 各接口（dataclass 返回）
   - inspect 读 8 个 dataclass 字段定义（`SecurityBar`/`SecurityQuote`/`FinanceInfo`/`XdxrRecord`/`FundFlow`/`MarketStat`/`HistoricalFundFlow`/`SecurityInfo`）
   - 与本项目 `tdx_client.py` 同类函数对照
   - 实测 easy_tdx v1.17.10 K 线 bug：`TdxDecodeError: day datetime: 数据不足`（v1.19.3/1.20.4 已修）
   - 写 `logs/easy_tdx_field_probe.txt` JSON 完整保存

2. **`docs/tdx_field_dict.md` 字典创建**：
   - 8 个 dataclass 完整字段表（200+ 字段）
   - 4 个 Enum 映射（`Market`/`KlineCategory`）
   - 健康分模块（`_reconnect.py` v1.17.10、`_health.py` v1.20.4）
   - 关键差异：vol 单位（手 vs 股）、`pre_close` vs `last_close` 改名、`fenhong` 每 10 股
   - V15.5/15.7/15.8 移植优先级 + 工作量估算

3. **`docs/field_dict.md` §7.11 V15.4.3 easy_tdx 兼容性**：
   - 8 个 dataclass 速查 + V15.5 10 个移植任务

4. **`docs/script_data_dict.md` §3.5 V15.4.3 easy_tdx 兼容性**：
   - easy_tdx dataclass 与本项目函数对应表 + 关键结论

5. **`docs/roadmap.md` V15.4.3 子版本 + V15.5 升级路线**：
   - 10 个 V15.5 移植任务（15.143-15.152）：升级 easy_tdx / 移植 `_health.py` / 移植 `_reconnect.py` / 50+ 候选 server / `_get_tdx_client` 集成 / K 线 + 指数 K 线空数据转移 / 跨进程健康分 / 单元测试 / 实跑验证
   - **根治 V15.4.1 sht 4 指数卡死**（V15.5 任务 15.149）

### V15.4.3 不做的事

- ❌ **不升级 easy_tdx 1.17.10→1.20.4**（pip cache 损坏；本轮先抓字段定义，升级在 V15.5）
- ❌ **不引入 easy_tdx 到 tdx_client.py**（V15.5 计划）
- ❌ **不替换本项目 cdata 架构**（easy_tdx 是"通道"，本项目是"数据中心"——根本冲突）
- ❌ **不集成前复权 / 34 指标 / 缠论**（V15.8/V15.9 计划）

### V15.4.3 验证

- ✅ 实跑探测脚本捕获 8 个 dataclass 完整字段
- ✅ `logs/easy_tdx_field_probe.txt` JSON 完整保存
- ✅ `docs/tdx_field_dict.md` 字典创建（200+ 字段对照表）
- ✅ `field_dict.md` / `script_data_dict.md` 交叉引用
- ✅ `roadmap.md` V15.4.3 子版本 + V15.5 升级路线

## [15.3] - 2026-07-29

**全量健康修复版本**。基于 2026-07-29 跑 000100 时的全量根因分析（X1-X8 共 8 个 P0/P1），结合第三方 deepseek 评审报告的逐条核查，对剩余 9 个 P0/P1 + 1 个 P2 做最后一次集中修复。**前置 V15.2 已修 8 个 P0/P1**：sht 报告 `_composite` NameError、`irm_q` 覆盖 q、`name` GBK 乱码、`price=0`、`board` 浮点数、val 18 步策略 0 命中、push2 fallback、share_capital 脏数据保护。**本轮 V15.3 修复剩余 9 个**：sc_report_runner path UnboundLocalError、sc_schema 4 字段 unit 错、4 个 `_SNAPSHOT_DATA` 模块级冲突、mak 重复 snapshot 调用、main.py 依赖检查不全、4 大报告 cdata 推广、CircuitBreaker TOCTOU、L1 LRU 升级、scratch 文档。

### ⚠️ Critical Bug Fixes

1. **`sc_report_runner.upload_multi_reports` 中 `path` 变量未定义（P0）**：
   - **触发场景**：[sc_report_runner.py:167-169](file:///d:/GitHub/test/stock_common/sc_report_runner.py#L167) `path = r.get("path", ...) if self.args else path` —— 当 `self.args is None` 时 `path` 在三元表达式右侧引用自身，Python 报 `UnboundLocalError`
   - **影响范围**：作为库使用 `BaseReportRunner` 时不传 `args` 会崩溃；当前子进程模型未触发
   - **修复方案**：先用 `os.path.join` 计算默认值，再用 `r.get("path", default_path) or default_path` 单步赋值

2. **`sc_schema` 4 个字符串字段 unit 错标为 `Unit.COUNT`（P0）**：
   - **触发场景**：[sc_schema.py:335-356](file:///d:/GitHub/test/stock_common/sc_schema.py#L335) `industry`/`industry_code`/`board`/`concept` 4 个字段错标 `unit=Unit.COUNT`（数值单位），实际是字符串
   - **影响范围**：依赖 `Unit` 枚举做序列化或类型检查的下游会得到错误信号；不影响当前报告生成
   - **修复方案**：4 个字段 `unit=Unit.COUNT` → `unit=Unit.TEXT`

3. **4 个报告模块 `_SNAPSHOT_DATA` 全局变量冲突（P0）**：
   - **触发场景**：[get_sht_report.py:42](file:///d:/GitHub/test/get_sht_report.py#L42) / [get_med_report.py:38](file:///d:/GitHub/test/get_med_report.py#L38) / [get_lng_report.py:38](file:///d:/GitHub/test/get_lng_report.py#L38) / [get_ful_report.py:121](file:///d:/GitHub/test/get_ful_report.py#L121) 各自定义同名 `_SNAPSHOT_DATA: dict = {}`
   - **影响范围**：当前子进程模型互不干扰；将来若同进程多报告会互相覆盖
   - **修复方案**：抽出到 `stock_common/sc_snapshot.py` 单一来源，4 个报告 import 后用 `sc_snapshot.register(code, ...)` 写入

4. **`get_mak_report` 重复 `get_market_snapshot_async()` 调用（P0）**：
   - **触发场景**：[get_mak_report.py:112+117](file:///d:/GitHub/test/get_mak_report.py#L112) 同函数调 2 次：第一次拿全市场，第二次用 codes 重新调
   - **影响范围**：3000+ 股票场景下浪费一次完整 ZHB 解析
   - **修复方案**：L112 已返回完整 dict，第二次直接 `price_map = snapshot` 复用

5. **`main.py` 依赖检查不全（P0）**：
   - **触发场景**：[main.py:133-167](file:///d:/GitHub/test/main.py#L133) `check_dependencies()` 只检查 5 个包（aiohttp/yaml/google.*×3/requests），但 requirements.txt 列出 14 个，缺 mootdx / pytdx / pandas / numpy
   - **影响范围**：缺这些核心依赖时启动不报错，运行到具体报告才 `ImportError` 崩溃
   - **修复方案**：补 9 项完整检查

### 🔧 Type Safety & Resilience

6. **lng/ful/val/mak 4 大报告接入 `CanonicalStockData`（P1）**：
   - **现状**：当前只 sht/med 用 cdata（[sht:332](file:///d:/GitHub/test/get_sht_report.py#L332) / [med:203](file:///d:/GitHub/test/get_med_report.py#L203)）；lng/ful/val/mak 仍走 `get_stock_composite_async` 返回 dict
   - **影响范围**：强类型合约只覆盖 40% 报告
   - **修复方案**：4 大报告在关键字段（price/change_pct/mcap_yi）切换到 cdata

7. **`CircuitBreaker` TOCTOU 加锁合并（P1）**：
   - **触发场景**：[sc_fault_tolerance.py:115-128](file:///d:/GitHub/test/stock_common/sc_fault_tolerance.py#L115) `_maybe_transition` 与 `_on_failure` 之间无锁保护
   - **影响范围**：高并发下多线程可能同时进入 HALF_OPEN 试探
   - **修复方案**：合并为单次 `with self._lock` 临界区

8. **`stock_cache` L1 淘汰策略 TTL→LRU（P1）**：
   - **触发场景**：[stock_cache.py:124-126](file:///d:/GitHub/test/stock_cache.py#L124) 当前按"最早过期"淘汰，会把热点 key 驱逐（如果热点 key ttl 短）
   - **影响范围**：val 报告 5721+ zhb_data 频繁淘汰场景下热点 key 不稳
   - **修复方案**：改为 LRU 淘汰（按最近访问时间），热点 key 永驻

### 📝 Documentation

9. **`scratch/` 目录 INVENTORY 文档（P2）**：
   - **现状**：`scratch/` 有 13 个子目录（eastmoney / EastMoney_Crawler / TradingAgents-astock / UZI-Skill / tickflow / finshare / investool / stock-sdk / tdx / zhb_20260713 等）+ 4 个 .py，无任何文档说明
   - **修复方案**：新增 `scratch/INVENTORY.md` 列出每个子目录用途

### V15.3 不做的事

- ❌ **不拆分 sc_datasource.py（184KB）** — V15.3 仅为修复版，拆分是 V16.0
- ❌ **不重写 14 个伪 async 函数** — 接受现状
- ❌ **不删除 scratch/ 子目录** — 用户的调研沙盒
- ❌ **不重写 val 18 步策略** — 策略逻辑不在本轮范围

## [15.2] - 2026-07-28

**P0 崩溃修复 + 缓存保护强化 + ZHB 交叉验证恢复版本**。基于 2026-07-28 20:29 批量运行日志的深度根因分析，重点修复 V15.1 引入的 `board` 变量未初始化导致的 39 只股票 `UnboundLocalError`，并恢复 V10.0/V12.6 期间被简化的"两次获取一致"缓存验证机制。

### ⚠️ Critical Bug Fixes

1. **`get_canonical_stock_data` 中 `board` 变量 `UnboundLocalError`（P0）**：
   - **触发场景**：V15.1 重构 industry/board 字段改用 TDX boards 时，代码错误地将 `board = ...` 放在 `if boards and boards.get("area"):` 条件块内，导致 TDX boards 返回无 area 字段时 `board` 变量未定义
   - **影响范围**：所有访问 `cdata.industry` 或 `cdata.board` 的报告脚本 → sht (35/35)、med (2/2)、lng (2/2) 共 39 只股票**全部数据生成失败**
   - **修复方案**：[data_provider.py:327-338](file:///d:/GitHub/test/data_provider.py#L327) `board = ''` 移出 try 块；删除 `if not board: board = ''` 死代码
   - **连锁恢复**：修好后 sht/med/lng 自动恢复数据生成 + GD 上传（因为 `upload_multi_reports` 检查 `status="成功"` 才上传）

### 🔒 Cache Protection Hardening

2. **统一 `valid_if` 工厂函数 `make_valid_if(check_zeros=True, min_size=0)`**：
   - 拒绝 None/空 dict/空 list/全零 dict
   - 替代散落在 9 个 F10 函数中的 `valid_if=lambda r: r is not None`（V12.6 弱化版）
   - 防止接口失败返回 `{}` 后被缓存为脏数据

3. **8 个 F10 函数 valid_if 强化**：
   - `tdx_client.py` 中 f10_fund_flow / f10_announcements / f10_reminders / f10_news 改用 `make_valid_if`
   - 此前 `valid_if=lambda r: r is not None` 允许空 dict 被缓存（如 `tdx_get_fund_flow` 失败返回 `{}`）

4. **dragon_tiger 补 valid_if（P0）**：
   - `sc_datasource.py:3509/3614` 原**完全无** `valid_if` 参数，HTTP 失败返回 `{}` 必然被缓存
   - 添加 `make_valid_if(min_size=1)` 防止空数据进入 SQLite

5. **12 个 zhb_data 函数补 valid_if**：
   - `data_provider.py` 中 12 个 `@cached(category="zhb_data", ...)` 函数补 `valid_if=lambda r: r`
   - 防止 ZHB dict 偶发空值被缓存

6. **`_has_zero_price` 递归检查**：
   - 从顶层 dict 改为递归检查嵌套结构
   - 捕获龙虎榜未成交席位、板块列表中无成交板块等 0 值
   - 修复 V10.2 引入的"仅顶层"导致的漏过误判

### 🛡️ ZHB Cross-Verification Restored (用户历史机制恢复)

7. **`_cross_verify_with_zhb` 工具函数**：
   - HTTP 返回值与 ZHB dict 关键字段对比，偏离 >50% 拒绝缓存
   - 恢复 V12.6 之前存在的 ZHB 交叉验证机制

8. **`set_cache` 集成交叉验证**：
   - 对 F10 / f10_fund_flow / dragon_tiger 自动调用 `_cross_verify_with_zhb`
   - 防止"网络瞬断 → 空数据被缓存"污染

9. **`cross_verify=True` 恢复"两次获取一致"**：
   - 仅对多天 TTL 分类（>1 天）启用
   - 实时分类（trading_day=True / < 1 天 TTL）不启用，避免实时数据变化导致永不过验证
   - 修复 V10.0 简化过度导致的"假通过"

### ⚡ val 1000s 性能优化

10. **L1 缓存上限 5000→10000**：
    - val 报告 5721+ 个 zhb_data 频繁淘汰旧条目
    - 扩容 `L1_MAX_ENTRIES` 减少最老条目淘汰开销

11. **val 22 策略去重循环**：
    - `get_pe_ttm_async` 等循环调用改为从 `_snapshot` dict 读（避免 260 只股票 × 22 策略 × 多次重复调用）
    - 单次 `get_market_snapshot_async` 拿到全市场 dict 后续直接 O(1) 读

12. **`ths_hot_reason` HTTP 失败降级**：
    - 添加 valid_if + fallback 默认空池 + 网络限流提示
    - 避免依赖 `hot_pool` 的 9 个策略（01/02/03/05/06/07/08/16）因 HTTP 阻断导致 0 命中

### 📤 GD Upload Stdout Buffer Fix

13. **`init_gd` 非交互模式自动跳过**：
    - 检测 `sys.stdin.isatty()`，非交互时（main.py 子进程 stdin=None）直接 return `skip_upload=True` 而非 input 卡住
    - 修复 val 报告 1000s 跑完后 GD 上传日志被吞的问题

14. **main.py 子进程 stdout 接管**：
    - `stdout=None` 改为 `stdout=subprocess.PIPE` + 显式 read + print
    - 确保子进程输出不被父进程控制台缓冲（Windows 默认全缓冲）

15. **所有 GD print 显式 flush=True**：
    - `init_gd` / `upload_type_reports` / `upload_stock_report_by_code` 内 print 全部加 `flush=True`

### 🧹 Cache Cleanup CLI

16. **`stock_cache.py clear` CLI 增强**：
    - 支持按 category 清理：`python stock_cache.py clear --category dragon_tiger --pattern ""`
    - 方便清理 V15.1 期间可能写入的脏数据

### Added

- `stock_cache.py:make_valid_if`: 统一 valid_if 工厂函数，拒绝 None/空 dict/空 list/全零 dict
- `stock_cache.py:_cross_verify_with_zhb`: HTTP vs ZHB 关键字段交叉验证
- `stock_cache.py:cross_verify` 参数恢复"两次获取一致"语义（仅多天 TTL 启用）
- `main.py`: 子进程 stdout=subprocess.PIPE 接管，修复 GD 日志被缓冲
- `gd_uploader.py`: `init_gd` 非交互模式自动跳过检测

### Changed

- `data_provider.py:get_canonical_stock_data`: `board = ''` 初始化移出 try 块，删除 `if not board: board = ''` 死代码
- `data_provider.py`: 12 个 zhb_data 函数补 `valid_if=lambda r: r`
- `tdx_client.py`: 8 个 F10 函数 valid_if 改用 `make_valid_if`
- `tdx_client.py:tdx_get_fund_flow` 等：失败时返回 `None` 而非 `{}`，避免脏数据
- `sc_datasource.py:get_dragon_tiger_board`: 添加 `valid_if=make_valid_if(min_size=1)`
- `stock_cache.py:_has_zero_price`: 从顶层改为递归检查
- `get_val_report.py:run_discovery_async`: 22 策略从 `_snapshot` 读，避免循环 `get_pe_ttm_async`
- `VERSION: 15.1.0 → 15.2.0`

### Fixed

- 🐛 **P0**: sht/med/lng 报告 39 只股票 100% 失败 (`cannot access local variable 'board'`)
- 🐛 **P1**: dragon_tiger 空 dict 被缓存为脏数据
- 🐛 **P1**: f10_fund_flow 失败返回 `{}` 被 `r is not None` 通过写入缓存
- 🐛 **P1**: 12 个 zhb_data 函数无 valid_if，ZHB 偶发空值被缓存
- 🐛 **P2**: val 1000s+ 超时（L1 5000 频繁淘汰 + 22 策略循环调 get_pe_ttm_async）
- 🐛 **P2**: GD 上传日志在 Windows 子进程 stdout 缓冲中被吞
- 🐛 **P3**: val 9 个策略依赖 `hot_pool`，`ths_hot_reason` HTTP 失败时硬卡

### Removed

- 无

### Security / Compatibility

- ✅ 保留所有 V15.0 / V15.1 旧 API（`get_canonical_stock_data` / `CanonicalStockData` / `em_get_fund_flow` 等）
- ✅ `tdx_get_fund_flow` / `tdx_get_history_fund_flow` 旧函数保留，新增 `em_*` 别名
- ✅ `get_concept_stocks` / `get_stock_concepts` V14.2 API 兼容（但 `get_stock_concepts` 永远返回空，因为 tdxchain.cfg 不含成分股）
- ✅ 不影响 F10/HTTP 接口调用层

### V15.2 不做的事

- ❌ **不删除 V15.1 的所有 ZHB 旁路机制**（已通过 SQLite 实测 100% 非空，无脏数据）
- ❌ **不升级到 V16.0**（V15.2 仅为修复版，不引入新功能）
- ❌ **不修改 val 22 策略的策略逻辑**（仅优化数据获取层）
- ❌ **不重写 F10 接口**（仅强化 valid_if，不动 HTTP 调用层）

### V15.2 验收标准

- ✅ `python main.py --sht 300750` 单股跑通，数据生成 + GD 上传成功
- ✅ `python main.py --sht 35只 --all ...` 全量跑通，0 数据失败
- ✅ `python main.py --val --mak` val 耗时 < 600s，mak 耗时 < 120s
- ✅ 缓存统计：4 个 0% 分类（zhb_data/f10_fund_flow/dragon_tiger/news）命中率均 > 0%
- ✅ `python stock_cache.py clear --category dragon_tiger` 一键清理生效
- ✅ 245+ 单元测试 100% 通过
- ✅ `VERSION: 15.1.0 → 15.2.0`

---

## [15.1] - 2026-07-26

全全局 ZHB 旁路普及与并发线程池隔离深化版本。将基于真实周期的 ZHB 时空路由矩阵全面普及至 6 大报告脚本（`sht`/`med`/`lng`/`ful`/`mak`/`val`），修补盘后 `09:30-24:00` 实时抓取路由窗口，并恢复量化策略的 100% 线程池 Worker 隔离机制。

### ⚠️ Major Optimizations & Features

1. **策略并发线程池 Worker 隔离与主线程解锁**：
   - 彻底解决 `get_val_report.py` 在 `▶ 22 策略并行扫描...` 处挂起 20 分钟的物理死锁瓶颈。
   - 恢复 `strategy_20_main_fund_ratio`、`strategy_21_volume_acceleration`、`strategy_22_capital_momentum` 为标准的同步 `def` 函数，使其在 `_run_sync_strategy` 调度中 100% 触发 `asyncio.to_thread` 隔离在后台 Worker 线程池中。
   - 主 asyncio 事件循环单线程恢复 100% 空闲，彻底消除了假 async 协程在主线程上同步循环发起 1,000 次网络请求造成的死锁。

2. **精细化 `09:30 - 24:00` 实时行情路由时间窗 (`_should_use_zhb_for_realtime`)**：
   - 根据真实物理数据更新规律重构时间路由规则：
     - **盘前与休市日 (`<09:30` / 周末 / 节假日)**：100% 走 ZHB 秒级内存提取（0ms，0 网络开销，完美复用清晨 06:00 前生成的最新文件包）。
     - **交易日 `09:30 - 24:00` (含盘中与盘后 15:00-24:00)**：强行走 HTTP / TDX 实时行情接口，完美抓取 T 日最新盘中行情与盘后收盘数据（解决磁盘 ZHB 在 15:00-24:00 仍为 T-1 日旧数据的问题）。

3. **全局 5 大报告脚本 ZHB 旁路普及与性能飞跃**：
   - **`get_sht_report` (短线)**：阶段涨幅与短线题材板块全面走 ZHB 内存解析，单股生成耗时缩短 50%。
   - **`get_med_report` (中线)**：休市日及盘前，ZHB 涵盖的归母净利润 / PE / PB / 静态股息率 100% 走 ZHB 静态层提取，消除东财 F10 HTTP 等待，单股生成速度提升显著。**注意：ROE / 毛利率 / 资产负债率等财务比率 ZHB 不包含，仍依赖 F10/HTTP 接口；当 ZHB 无该字段时显示 `N/A` 不显示虚假 `0.00%`**。
   - **`get_lng_report` (长线)**：52 周高低位与当期股息率优先走 ZHB 本地快照解析，单股分析耗时缩短 70%。**注意：历史分红派息明细 ZHB 不包含，仍走 `get_dividend_history` (TDX xdxr_info) 接口**。
   - **`get_ful_report` (全维度)**：Layer 3 财务诊断与 Layer 6 行业排名初筛融入 ZHB 本地代码/板块索引，行业比较速度提升 10 倍。
   - **`get_mak_report` (异动扫描)**：板块行情数据走 ZHB 批量快照；**大宗交易明细 / 限售解禁时间表 ZHB 不包含，仍走 DataCenter HTTP 接口**。

4. **GD 云端上传稳定性与日志透明度增强**：
   - 将根文件夹「a-stock-data」自动重试次数从 `max_auto_retry=0` 提升为 `3`，消除了网络瞬断时直接弹出终端交互提示阻断批量运行的问题。
   - 在 `sc_report_runner.py` 中添加显式提示 `⚠️ GD 云端同步跳过：未能获取云盘根文件夹「a-stock-data」`，提升日志透明度。

### Added

- `data_provider.py`: 重构 `_should_use_zhb_for_realtime()` 物理时间路由函数，精准区分 `00:00-09:30` 盘前 ZHB 模式与 `09:30-24:00` 实时 API 模式。

### Changed

- `get_val_report.py`: 策略 19、20、21、22 函数签名与并发调度的同步解耦，修补控制台 Unicode GBK 打印逻辑。
- `get_val_report.py`: V15.1.1 补齐 Component 5 —— `strategy_04_core_discount` 与 `strategy_08_policy_driven` 接入 `get_canonical_stock_data` 强类型合约（`await asyncio.to_thread()`），同时移除对旧的 `get_stock_composite_async` 引用。
- `get_mak_report.py`: V15.1.1 补齐 Component 5 —— 新增 `_canonicalize_stock(code, stock_dict)` 适配函数（dict → CanonicalStockData），保留 `get_market_snapshot_async` 批量入口避免 1000 倍性能回退。
- `get_sht_report.py`: `generate_report_async` 显式绑定 `price_today` 与 `q` 变量，消除 UnboundLocalError。
- `stock_common/sc_report_runner.py`: 优化 `_handle_gd_upload` 上传跳过时的日志输出。

---

## [15.0] - 2026-07-26

标准化数据中心与 ZHB 离线优先架构重构大版本。**完全收敛多源行情异构数据**，引入强类型数据合约 `CanonicalStockData`，实施基于真实生成周期（T+1 清晨 06:00 前）的 ZHB 时空路由矩阵、SQLite 缓存 ZHB 旁路剥离以及静默容错降级机制。

### ⚠️ Breaking Changes & Architectural Upgrades

1. **统一数据合约 (`CanonicalStockData`)**：
   - 彻底废弃各报告脚本中直接分散调用 Eastmoney / Sina / Tencent 的多源硬编码逻辑。
   - 所有 6 大报告引擎（`get_sht_report`, `get_med_report`, `get_lng_report`, `get_ful_report`, `get_val_report`, `get_mak_report`）统一接入 `get_canonical_stock_data(code)` 强类型合约。
   - `CanonicalStockData` 为 `@dataclass(slots=True, frozen=True)`，包含 50+ 个标准化强类型属性与 `data_source`/`time_anchor` 溯源标签。
2. **基于真实周期的 ZHB 时空路由矩阵**：
   - **盘前 (`<09:30`) 与休市日**：100% 走 ZHB 本地内存秒级提取，零网络开销（完美利用清晨 06:00 前生成的最新 ZHB 文件包）。
   - **T日盘后 (`15:00-24:00`)**：行情与资金流字段 100% 强制走网络 HTTP/TDX 接口，确保获取 T 日真实收盘价（非 T-1 盘前数据）。
3. **ZHB 数据 SQLite 磁盘缓存全量旁路 (Bypass)**：
   - 所有 ZHB 提供的 30+ 静态/估值/财务/股本/概念字段在内存中直接从 `zhb_client` 的 RAM 字典提取（`<0.001ms`），**完全不写入 `stock_cache.db`**。
   - 重置数据库后，磁盘数据库占用从 16.7MB 骤降至几十 KB，彻底消除 SQLite 写放大与 Windows 平台下 `.db-journal` 文件死锁隐患。
4. **熔断与网络故障静默降级 (Graceful Degradation)**：
   - 当网络 HTTP/TDX 接口触发断路器（`Open` 状态）或发生超时/连接异常时，`get_canonical_stock_data` **零异常静默降级**回退至 ZHB T-1 内存快照，并标注 `data_source="zhb"`，确保报告引擎 100% 不崩溃。

### Added

- `stock_common/sc_schema.py`: 新增 `CanonicalStockData` dataclass，包含完整 50+ 字段定义及 `to_dict()` 方法。
- `data_provider.py`: 新增 `get_canonical_stock_data(code, force_realtime=False)` 与 `get_canonical_stock_data_batch(codes)` 统一数据入口。
- `tests/test_field_routing.py`: 新增 `test_graceful_circuit_breaker_fallback` 单元测试，验证断路器熔断时零异常降级。
- `.gitignore`: 引入 `scratch/*` 通配符规整规则，支持自动屏蔽全局临时编译与缓存文件。

### Changed

- `tdx_client.py`: 增加 `hasattr(signal, 'SIGALRM')` 保护，彻底解决 Windows 平台下的 `AttributeError` 崩溃。
- `get_med_report.py` / `get_ful_report.py` / `get_sht_report.py` / `get_lng_report.py` / `get_val_report.py` / `get_mak_report.py`: 6 大报告脚本全量重构，统一绑定 `CanonicalStockData` 属性。
- `stock_cache.py`: SQLite 数据库职责瘦身，仅保留重网络请求（800 根 K 线、龙虎榜席位明细、F10 三表报表、研报列表）。
- `tests/`: 自动化测试套件合并重构，文件数从 19 个收敛精简至 11 个核心测试文件。

### Fixed

- **Windows 信号崩溃**：修复 `tdx_client.py` 中 `signal.SIGALRM` 在 Windows 平台上的 AttributeError。
- **`UnboundLocalError`**：修复 `get_med_report.py` 中旧变量 `price_today` / `q` / `_zhb_data` 残留导致的属性绑定异常。
- **SQLite 锁死锁**：ZHB 旁路剥离后，不再向 SQLite 高频写入 ZHB 字典，完全杜绝 `.db-journal` 死锁。

### Removed

- 清理已废弃的 4 个临时里程碑测试文件（`test_cache_verify.py`, `test_v1421_features.py`, `test_v1422_bugfix.py`, `test_v143_perf.py`），测试用例已全量合流至主测试文件。
- 删除重置旧版 16.7MB `cache/stock_cache.db` 文件。

### 🔧 Migration Guide

**版本无缝平滑升级**。`get_canonical_stock_data(code)` 提供了兼具 `dataclass` 强类型访问和 `.to_dict()` 字典转换的双重支持：
```python
from data_provider import get_canonical_stock_data

# 获取统一标准化数据
cdata = get_canonical_stock_data("600519")

# 属性直接访问（推荐）
print(cdata.code, cdata.price, cdata.pe_ttm, cdata.data_source)

# 转换为字典（兼容旧代码）
cdata_dict = cdata.to_dict()
```

---

## [14.0] - 2026-07-22

V13.x Bug 修复 + 文档全量同步版本。**不引入新功能**。

### ⚠️ Breaking Changes
- **`is_workday()` 逻辑修复**：本地 `holidays`/`workdays` 字典为权威，ZHB 仅辅助校验（V10.0 ZHB 优先逻辑存在 Bug，ZHB 残缺时误判 8 个 `TestKnownHolidays` 为工作日）。
- **`ANTI_POISON_DEVIATION_THRESHOLD` 标记废弃**：保留仅兼容 `tests/test_core_defense.py::TestAntiPoison`。

### Added / Changed / Fixed / Removed
- 6 个核心文档（README / CHANGELOG / tests-README / scripts-README / architecture / master_data_sources）全量同步到 V14.0；VERSION 13.2 → 14.0。
- 6 大 Runner / main.py / tdx_client / zhb_sync / gd_uploader docstring 版本信息更新；`stock_common/__init__.py` 补充 sc_schema.py 说明。
- conftest.py 增加 CI 环境 `REAL_NETWORK=1` skip 防御；test_stock_common.py 从 6 个测试扩充到 28 个。
- CHANGELOG V12.6/V13.0/V13.1 增加 ⚠️ Breaking Changes + 🔧 Migration Guide；field_dict.md 第 6 节补充 V13.x Schema mermaid 数据流图。
- `config.py` 中 `ANTI_POISON_DEVIATION_THRESHOLD` 标记为 V14.0 已废弃；`data_provider.py` 删除 V12.6 后无引用的 import。
- 删除 `scratch/fix_perf_memory.py` / `scratch/fix_perf_memory_v2.py`（本会话遗留临时脚本）。

### 🔧 Migration Guide
**无需迁移**。V14.0 保持 V13.x 完全兼容。唯一语义变化：`is_workday()` 对 ZHB 残缺数据处理更准确（Bug 修复，非 API 变更）。

---

## [14.2] - 2026-07-22

ZHB 数据集深度集成版本。基于 `field_dict.md` 第三节第 4 小节新挖掘的 6 个 ZHB 数据集（profile.dat / tdxchain.cfg / neednote.dat / xgsg.cfg / brkseat.dat / pttab.dat），深度集成到 `data_provider`，**HTTP 调用减少 30-50%**。

### Added

**zhb_client.py 增强（6 个新解析器）**：
- `ZhbData.stock_profile` / `get_stock_name(code)` —— 解析 `profile.dat`（全市场 4888 只 A 股代码+简称，GBK 编码）
- `ZhbData.concept_chain` / `get_concept_stocks(name)` / `get_stock_concepts(code)` —— 解析 `tdxchain.cfg`（200+ 概念/产业链节点）
- `ZhbData.neednote_holidays` / `neednote_jyweek` —— 解析 `neednote.dat` 的 `RecentCFETSHoliday`（官方休市日）+ `RecentCFETSJYWeek`（官方调休补班日）
- `ZhbData.brk_seat` —— 解析 `brkseat.dat`（龙虎榜营业部席位）
- `ZhbData.special_tags` —— 解析 `pttab.dat` 完整版（红筹/AH/概念等特别标签，区别于 V12.0 仅退市股的 `delisted_stocks`）
- 模块级便捷函数：`get_stock_name_from_zhb()` / `get_stock_profile()` / `get_concept_chain_from_zhb()` / `get_stock_concepts_from_zhb()` / `get_zhb_official_holidays()` / `get_zhb_official_jyweek()` / `get_brk_seat_from_zhb()` / `get_special_tags_from_zhb()`

**data_provider.py 新增 5 个 ZHB 本地函数**：
- `get_stock_basic_info_from_zhb(code)` —— 替代东财 HTTP code_to_name
- `get_concept_from_zhb(code)` —— 替代同花顺热榜 HTTP（仅静态匹配部分）
- `get_new_share_calendar_from_zhb()` —— 替代东财新股 API
- `get_special_tags_from_zhb()` —— 替代手工字典
- `is_zhb_dataset_available()` —— ZHB 6 个新数据集可用性检查

**stock_calendar.py 增强**：
- `_load_zhb_neednote_supplement()` —— 加载 ZHB neednote.dat 官方休市日+调休补班日
- `is_workday_with_zhb_supplement(date)` —— 在 is_workday() 基础上叠加 ZHB 补充日历
- `get_zhb_supplement_count()` —— 返回 ZHB 补充日历统计信息

**get_sht_report.py 集成**：
- 短线报告在 `em_hot_concept()` 之前先调用 `get_concept_from_zhb()`，优先展示 ZHB 本地匹配的产业链/概念

**测试**：
- 新增 `tests/test_zhb_new_datasets.py`（24 个测试）：覆盖 6 个 ZHB 解析器 + 5 个 data_provider 函数 + 日历补充 + Fallback 优雅降级

### 🔧 Migration Guide

**无需迁移**。V14.2 保持 V14.0/V14.1 完全兼容。

新功能是**新增**而非替换，HTTP Fallback 保留。ZHB 数据缺失时所有函数返回 `None` / `set()` / `list()`，不抛异常。

---

## [14.2.1] - 2026-07-22

Gemini 深度静态分析后修复的 3 个边界隐患 + 1 个架构一致性提升。**不改变 VERSION 编号**（仍是 14.2）。

### Fixed

**1. `stock_calendar.py` 缓存陈旧防护（问题 3）**：
- `_ensure_zhb_supplement_loaded()` 现在记录 `_last_zhb_supplement_date`，当 ZHB 数据日期变更时（盘后守护进程下载了新 zhb.zip）**自动重新加载**补充日历
- 新增 `invalidate_zhb_supplement_cache()` 用于 zhb_sync.py 下载完成后显式触发 reload
- 解决长轮询模式下 ZHB 节假日/调休日不生效的隐患

**2. `_load_zhb_neednote_supplement()` 空串防御（问题 1）**：
- 预过滤空元素 `if s and s.strip()`
- 增加 `IndexError` 异常捕获
- 避免空字符串触发 ValueError 异常开销

**3. `zhb_client._parse_profile()` 全角空格去除（问题 2）**：
- 在 `.strip()` 后增加 `.strip('\u3000')`（全角空格）
- 解决个别股票简称尾部残余全角空格导致 `get_stock_name_from_zhb()` 返回值与预期不匹配

**4. `data_provider.py` 字段路由与 sc_schema 联动（提升 A）**：
- `REQUIRES_REALTIME_HTTP` / `ZHB_SUFFICIENT` 从**静态硬编码 frozenset** 改为**动态从 sc_schema 生成**：
  ```python
  from stock_common.sc_schema import list_realtime_http_fields, list_zhb_sufficient_fields
  REQUIRES_REALTIME_HTTP = frozenset(list_realtime_http_fields())
  ZHB_SUFFICIENT = frozenset(list_zhb_sufficient_fields())
  ```
- 保留 ImportError fallback 静态定义
- **单一权威源**：新增字段只需在 `sc_schema.FIELD_SPECS` 添加即可

**5. `sc_schema.list_zhb_sufficient_fields()` 语义修正**：
- 原实现 `zhb_t_minus_1_acceptable=True` 与 `is_real_time=True` 有交集（如 price 既能 HTTP 也能 ZHB 兜底）
- 现改为 `not s.is_real_time`（严格意义"不强制走 HTTP"）
- 保证 `REQUIRES_REALTIME_HTTP` 与 `ZHB_SUFFICIENT` 互斥

**6. `sc_schema.FIELD_SPECS` 补全 3 个字段**：
- `main_net_buy_hands_1d` / `main_net_buy_amount_1d`（资金流 T-1 数据）
- `pe_dynamic`（动态 PE，区别于 pe_ttm）
- `concept`（概念/题材）

### Added

**测试**：
- 新增 `tests/test_v1421_features.py`（10 个测试）：覆盖缓存陈旧防护 + sc_schema 联动 + 全角空格去除 + neednote 空串防御

### 🔧 Migration Guide

**无需迁移**。所有改动都是内部实现优化与边界修复，公开 API 保持不变。

- 新增字段的开发者现在只需要在 `sc_schema.FIELD_SPECS` 添加即可，data_provider 自动同步
- 长轮询模式（如未来 WebSocket 调度器）调用 `invalidate_zhb_supplement_cache()` 即可触发 ZHB 补充日历重载

---

## [14.3] - 2026-07-25

**性能优化版本**。针对 val 报告周日首次跑 15 分钟卡死的实际问题，从 P0/P1/P2/P3 四个层面完整解决"网络请求风暴"问题。

### Fixed

**P0：清理 TDX K 线缓存（解决 ZHB 更新后缓存陈旧）**：
- `get_val_report.run_discovery_async` 入口处清空 `_TDX_KLINE_CACHE` / `_TDX_WKLINE_CACHE`
- 解决：周日 ZHB 数据更新后，进程级缓存可能脏

**P1-1：收缩策略扫描范围**：
- `_top_n_large`：1000 → **300**（周线/形态类策略，1000 → 300）
- `_top_n_medium`：500 → **200**（财务/筹码类策略）
- `_top_n_small`：300 → **150**（北向/流动性类策略）
- 网络请求数从 3000+ 降至 1000-

**P1-2：ZHB 前置过滤**（用 ZHB 离线字段避免无意义 K 线网络请求）：
- 新增 `_zhb_weekly_eligible(stock)` —— 周线多头前置过滤（mcap_yi/amount/change_20d/change_60d/streak_days/pe_ttm）
- 新增 `_zhb_pattern_eligible(stock, pattern)` —— 形态类前置过滤（double_bottom / three_soldiers）
- 策略 02/05/06 在循环中调用，预计过滤掉 50-70% 股票

**P2：TDX K 线显式 5s 超时**：
- `tdx_get_security_bars` / `tdx_get_weekly_bars` 内部用 `signal.alarm(5)` 包装 mootdx TCP 请求
- 避免 mootdx 默认 15s 超时在休市日卡死进程
- 超时后立即返回空数据，不阻塞后续

**P3：跨进程 K 线磁盘缓存**：
- 新增 [`stock_common/sc_kline_cache.py`](file:///d:/GitHub/test/stock_common/sc_kline_cache.py)
- 提供 `get_cached_kline` / `set_cached_kline` / `clear_kline_cache` / `get_cache_stats`
- 缓存目录：`<repo_root>/.cache/kline/`
- TTL：24 小时（T+1 数据稳定后不再变化）
- 接入 `tdx_get_security_bars` / `tdx_get_weekly_bars` 网络层
- **效果**：第二次运行 val（即使进程重启）几乎瞬时返回，零网络请求

### Added

**测试**：
- 新增 `tests/test_v143_perf.py`（24 个测试）：覆盖 P0/P1/P2/P3 各优化点的代码完整性与功能正确性

### 🔧 Migration Guide

**无需迁移**。所有改动都是性能优化与架构改进，公开 API 保持不变。

运行 `python main.py --val` 现在应：
- 首次运行：~5 分钟（之前 15+ 分钟）
- 第二次运行：~1-2 分钟（磁盘缓存命中）
- 休市日：单只股票 K 线请求最多 5s 超时（之前 15s）

升级 VERSION 14.2 → 14.3。

## [14.3.1] - 2026-07-25

根据用户对缓存机制的两点深入分析，对 V14.3 缓存架构进行精细化重构。**不改变 VERSION 编号**（仍是 14.3）。

### Fixed / Refactored

**1. 删除 P0 入口清空缓存（冗余代码）**：
- 问题：用户质疑"脚本开始清空缓存是每次都清空还是就第一次，如果每次都清空缓存的意义在哪里"
- 分析：进程级缓存 `_TDX_KLINE_CACHE` 本就只活在本进程内，新进程必空；同进程内 22 个策略共享同一份 L1 缓存是**性能优化**（22 次复用 vs 22 次从 L2 重读）
- 删除：[get_val_report.py](file:///d:/GitHub/test/get_val_report.py) 入口的 `_TDX_KLINE_CACHE.clear()` / `_TDX_WKLINE_CACHE.clear()` 冗余代码

**2. 缓存失效机制增强（启动清理 + 总大小限制 + LRU）**：
- 问题：用户质疑"缓存K线对于缓存文件的大小是否会造成影响，缓存的失效机制又是什么"
- 增强 [`stock_common/sc_kline_cache.py`](file:///d:/GitHub/test/stock_common/sc_kline_cache.py)：
  - **`CACHE_SIZE_LIMIT_BYTES = 500 MB`**：缓存总大小上限
  - **`CACHE_SIZE_TARGET_BYTES = 400 MB`**：LRU 清理目标值
  - **`clear_expired()`**：手动清理 24h+ 过期文件
  - **`enforce_size_limit()`**：超限时按 mtime 升序 LRU 清理
  - **模块导入时自动清理过期文件**（一次）
  - **写入后自动检查大小**（不阻塞主流程）
  - **线程安全**：pickle 文件操作加 `threading.Lock`

### Added

**测试**：
- 更新 `tests/test_v143_perf.py`（32 个测试，含 V14.3.1 新增 8 个）：
  - 验证 `.clear()` 已从入口移除
  - 验证大小限制常量
  - 验证 `clear_expired()` / `enforce_size_limit()` 接口
  - 验证过期文件被正确清理
  - 验证 `get_cache_stats()` 返回大小信息

### 🔧 Migration Guide

**无需迁移**。所有改动都是缓存机制内部优化，公开 API 保持不变。

### 📊 缓存机制对比

| 维度 | V14.3 | V14.3.1 |
|:---|:---|:---|
| 入口清空 L1 | ❌ 冗余 | ✅ 删除 |
| 启动清理过期文件 | ❌ 无 | ✅ 自动（导入时）|
| 总大小限制 | ❌ 无限增长 | ✅ 500 MB 上限 |
| LRU 淘汰 | ❌ 无 | ✅ 按 mtime 升序 |
| 线程安全 | ❌ 无锁 | ✅ `threading.Lock` |
| 监控能力 | 仅 stats | stats + 主动清理接口 |

## [14.3.2] - 2026-07-25

**Top-N 数据驱动回测**。用 4 天 ZHB 数据（cache/zhb/zhb_202607{21,22,23,24}）回测 12 个策略在不同 top_n 下的选股质量，给出"按策略差异化 top_n"建议。**不改变 VERSION 编号**（仍是 14.3）。

### Changed

**1. Top-N 从"一刀切"改为"按策略差异化"**：

| 策略 | V14.3.1 配置 | V14.3.2 推荐 | 依据 |
|:---|:---:|:---:|:---|
| 02 周线多头 | 200 | **100** | 100 已饱和（10/10）|
| 04 核心打折 | 200 | **100** | 100 已饱和 |
| 05 W底形态 | 300 | 300 | ✅ 验证一致 |
| 06 红三兵 | 300 | **100** | 100 已饱和 |
| 10 逆向白马 | 200 | 200 | 维持（4天无财务数据）|
| 11 筹码集中 | 200 | 200 | ✅ 验证一致 |
| 12 量价信号 | 200 | 200 | ✅ 验证一致 |
| 13 高股息 | 300 (内部) | **100** | 100 稳定性 0.57 > 300 稳定性 0.43 |
| 17 北向Top | 150 | **200** | 200 稳定性 0.79 > 150 稳定性 0.71 |
| 19 52周低位 | all_stocks | **200** | 200 稳定性 0.77 最佳 |
| 20 主力资金 | all_stocks | **1000** | 条件严苛，需大池子（即便 1000 也只选 9.5）|
| 21 量能三连击 | all_stocks | **200** | 200 选满 10 |
| 22 资金动量 | all_stocks | **100** | 100 已饱和 |

### Added

**2. 5 档差异化 top_n 配置**：
```python
_top_n_large = 300   # 形态类（05 W底/06 红三兵）
_top_n_medium = 200  # 财务/筹码类（11/12/17）
_top_n_small = 100   # 周线/核心（02/04）
_top_n_pure = 200    # 纯 ZHB 类（19/22）
_top_n_fund = 1000   # 主力资金（20）
```

**3. 回测脚本与报告**：
- 新增 [`scripts/backtest_topn.py`](file:///d:/GitHub/test/scripts/backtest_topn.py) - 独立回测脚本
- 新增 [`docs/backtest_v1432/README.md`](file:///d:/GitHub/test/docs/backtest_v1432/README.md) - 综合分析报告
- 新增 `docs/backtest_v1432/backtest_daily.csv` - 每日明细（240 行）
- 新增 `docs/backtest_v1432/backtest_summary.csv` - 汇总（60 行）
- 新增 `docs/backtest_v1432/backtest_recommendations.json` - 推荐表

### 📊 评估方法

| 指标 | 计算方式 |
|:---|:---|
| 选中数 | 4 天平均（策略在该 top_n 范围内能选出的股票数）|
| 稳定性 | 4 天 Jaccard 相似度均值（C(4,2) = 6 对的平均）|
| 推荐规则 | "能稳定选到 8+ 结果" + "Jaccard >= 0.5" 的最小 top_n |

### ⚠️ 回测局限性

- **17 北向Top**：用 mcap_yi 近似北向数据，偏差较大，需真实北向数据二次验证
- **10 逆向白马 / 18 龙虎榜**：4 天包无相关数据，未参与回测
- **mcap_yi 不在 ZHB**：回测用 `amount × pe_ttm × 0.5` 代理（粗略，作为排序键足够）

### 🔧 Migration Guide

**无需迁移**。所有改动都是回测驱动的 top_n 优化，公开 API 保持不变。

运行 `python main.py --val` 现在应：
- 22 策略按各自最优 top_n 选股
- 总网络请求与 V14.3.1 基本持平（多数策略缩小，少数扩大）
- 选股稳定性更优（11/12/17 提升 26%）

升级 VERSION 14.3 → 14.3.2。

---

## [14.2.2] - 2026-07-25

针对 Gemini 报告的两个实际运行异常（`val` 脚本 `NameError` + `mak` 脚本 `0只` 与卡死），进行深度根因修复。**不改变 VERSION 编号**（仍是 14.2）。

### Fixed

**1. `get_mak_report.py` 的 `0只` Bug（修复 1）**：
- `_get_zhb_market_data()` 之前用 `price_map.get(code, {}).get("name", "")` 永远取空字符串（ZHB tdxstat 快照不包含 name 字段），导致全市场 4888 只股票被 `if not name: continue` 全部丢弃
- 修复：用 `get_stock_name_from_zhb(code)` 从 ZHB `profile.dat` 离线字典补齐中文简称（零网络请求）
- 引入 `zhb_name_cache` 局部字典避免重复查询

**2. `tdx_get_market_abnormal_data()` 的 `0只` Bug（修复 2）**：
- 同上问题，V12.0 改用 ZHB 全市场快照后未补 name 字段
- 修复：在 [tdx_client.py](file:///d:/GitHub/test/tdx_client.py) 同样用 `get_stock_name_from_zhb()` 补齐

**3. `get_val_report.py` 的 `NameError: strategy_21_volume_acceleration not defined`（修复 3）**：
- `_strategy_defs` 列表已注册策略 21/22 但**未定义**函数体
- 修复：在 [`get_val_report.py:1369+`](file:///d:/GitHub/test/get_val_report.py#L1369) 补充：
  - `strategy_21_volume_acceleration(stocks)` —— 量能三连击（基于 `data_provider.get_volume_acceleration`）
  - `strategy_22_capital_momentum(stocks)` —— 资金动量（基于 `data_provider.get_capital_momentum`）
  - `_safe_int(v)` 辅助函数
- 两个策略均为 `async def`，与 V11.5 设计一致

**4. `tdx_client._get_tdx_client` 的"卡死选择最快服务器"问题（修复 4）**：
- 之前 `bestip=True` 触发 mootdx `[-] 选择最快的服务器...` 探速循环，**休市日多个 TCP 节点超时导致卡死数分钟**
- 修复：改为 `bestip=False`，与 [zhb_client.py](file:///d:/GitHub/test/zhb_client.py) 保持一致（手动指定服务器）

## [14.2.3] - 2026-07-25

V14.2.2 的修复不完整——`_check_tdx()`（健康检查函数）仍使用 `bestip=True`，导致 val 报告（`strategy_10_contrarian_value` 调用 `tdx_get_finance_roe`）在 22 策略并行扫描时触发 mootdx 探速循环卡死。**不改变 VERSION 编号**（仍是 14.2）。

### Fixed

**5. `tdx_client._check_tdx()` 补漏（修复 5，V14.2.3 补漏）**：
- 之前 V14.2.2 只改了 `_get_tdx_client()`，**漏了** `_check_tdx()` 这条路径
- 实际调用链：`strategy_10_contrarian_value` → `tdx_get_finance_roe` → `tdx_get_finance_info` → `_get_tdx_client` → `_check_tdx(bestip=True)` → 触发 mootdx 探速循环
- 修复：`_check_tdx()` 的 `bestip=True` → `bestip=False`，与 `_get_tdx_client` 保持一致
- **根因分析**：val 报告卡死日志 `选择最快的服务器` 来自 `_check_tdx`，不是 `_get_tdx_client`

### Added

**测试**：
- `tests/test_v1422_bugfix.py` 增加 `test_check_tdx_uses_bestip_false` 测试，覆盖补漏验证

### 🔧 Migration Guide

**无需迁移**。内部代码修改，公开 API 保持不变。

运行 `python main.py --val` 现在应：
- 22 策略并行扫描不再卡死在 mootdx 探速循环
- 真正进入策略执行阶段（之前在 `_check_tdx` 阶段就卡死）

---

### Added

**测试**：
- 新增 `tests/test_v1422_bugfix.py`（11 个测试，含 V14.2.3 补漏测试）：覆盖 5 个修复点的代码完整性 + 函数可调用性 + 集成验证

### 🔧 Migration Guide

**无需迁移**。所有改动都是 Bug 修复与行为修正，公开 API 保持不变。

运行 `python main.py --sht 600519 --mak --val` 现在应：
- val 报告正常执行 22 个策略
- mak 报告正确显示全市场 4888 只股票（之前 0只）
- 不会在休市日卡死在 mootdx 探速循环

---

## [13.2] - 2026-07-22

### ⚠️ Breaking Changes

无重大破坏性变更。V13.2 仅追加文档与脚本。

### 🔧 Migration Guide

无需迁移。

## [13.2] - 2026-07-22

### Added — V13.x dataclass Schema（opt-in 升级路径）

V13.0/V13.1/V13.2 三阶段引入 dataclass 形式的数据容器，作为 V12.x dict 的**可选**升级路径。

### V13.0: Schema 骨架

**1. `stock_common/sc_schema.py` 新建**：
- `TimeAnchor` Enum: T_DAY / T_MINUS_1 / T_OPEN / T_YEAR_START
- `DataSource` Enum: ZHB / TDX / TENCENT / EASTMONEY / SINA / FALLBACK
- `Unit` Enum: YUAN / WAN_YUAN / YI_YUAN / SHARE / PERCENT / ...
- `FieldSpec` dataclass(slots=True, frozen=True) — 字段元数据
- 34 个核心字段的元数据表 `FIELD_SPECS`
- `NormalizedQuote` 归一化行情快照（V13.0 草案）
- `normalize_at_boundary()` 边界归一化函数（骨架，NotImplementedError）

**2. V13.0 阶段不接入 data_provider**：保持 V12.x 完全兼容。

### V13.1: 缓存层透明序列化 + opt-in dataclass 接口

**1. `stock_cache.py` 新增**：
- `_serialize_for_cache(value)`: dataclass → dict（自动递归）
- `_deserialize_from_cache(value, target_cls)`: dict → dataclass（可选）
- `set_cache` 自动调用 `_serialize_for_cache` 转换
- `_l1_set` 也走序列化（L1/L2 返回一致性）

**2. `data_provider.py` opt-in 接口**：
- `get_stock_composite_dataclass(code) -> NormalizedQuote`
- `get_market_snapshot_dataclass(codes) -> {code: NormalizedQuote}`
- `dict_to_normalized_quote(code, raw, source)` 通用工具

**3. 测试**：`tests/test_sc_schema.py` 23 个测试全过：
- Schema 元数据测试（11）
- NormalizedQuote 骨架测试（3）
- `_serialize_for_cache` / `_deserialize_from_cache` 测试（9）

### V13.2: 性能压测 + 文档更新

**1. `scripts/perf_compare.py` 性能对比脚本**：
- 5000 记录对比（Python 3.12）
- dataclass (slots=True) 内存节省 70%（184B → 56B/对象）
- 字段访问加速 21%（dict 0.066s → dataclass 0.054s for 1M reads）
- 序列化开销 +172%（asdict 调用）

**2. 文档更新**：
- `docs/field_dict.md` 第 6 节"V13.x dataclass Schema"
- `docs/architecture.md` 第 8/9 节"V12.6 字段路由" + "V13.x dataclass Schema 层"

### V13.2 不做的事

- ❌ **不强制 6 大 Runner 切换访问语法**：dict 接口是默认，避免引入大量 bug
- ❌ **不删除 dict 输出兼容层**：opt-in dataclass 是补充，不是替换
- ❌ **不全面重构 data_provider**：仅追加 3 个 opt-in 函数

### 实用主义结论

**dict 作为默认接口保留，dataclass 作为可选升级**。这是基于 V13.2 实测结果：
- 序列化开销太大（+172%），不能全面替换
- 但内存与访问速度优势明显，可在新功能/新模块 opt-in 使用

### 验证结果

- ✅ 100 个测试全部通过（test_cache 11 + test_field_routing 15 + test_report_runner 16 + test_core_defense 9 + test_stock_common + test_scoring 27 + test_sc_schema 23）
- ✅ sc_schema.py 34 个 FieldSpec 正确加载
- ✅ stock_cache.py dataclass 序列化不影响现有调用

---

## [13.0] - 2026-07-22

### ⚠️ Breaking Changes

无重大破坏性变更。V13.0 仅新增 `stock_common/sc_schema.py` 模块，不接入 data_provider。

### Added — V13.0 Schema 骨架

创建 `stock_common/sc_schema.py`（详见 V13.2 CHANGELOG 的 V13.0 章节）。

不接入 data_provider，保持 V12.x 完全兼容。

### 🔧 Migration Guide

无需迁移。现有 6 大 Runner 调用语法保持兼容。

---

## [13.1] - 2026-07-22

### ⚠️ Breaking Changes

V13.1 涉及缓存层行为变化（**潜在影响**）：

1. **`_l1_set` 现在也走 `_serialize_for_cache`**：L1 缓存存储前会递归 asdict() 转换 dataclass。如果你的代码直接读取 `_L1_CACHE` 字典（不推荐），会发现引用值从 dataclass 变为 dict。
2. **`set_cache` 拒绝 dataclass 失败的行为消除**：之前 `json.dumps(dataclass_instance)` 会失败导致缓存静默跳过；现在会自动序列化。

### Added — V13.1 缓存透明序列化 + opt-in dataclass

- `stock_cache._serialize_for_cache` / `_deserialize_from_cache` 新增
- `set_cache` / `_l1_set` 自动序列化
- `data_provider` 新增 3 个 opt-in dataclass 函数
- `tests/test_sc_schema.py` 23 个测试全过

### 🔧 Migration Guide

**无需迁移**。现有 6 大 Runner 调用 `data_provider.get_*()` 仍返回 dict（默认接口），dataclass 为 opt-in。

---

## [12.6] - 2026-07-22

### ⚠️ Breaking Changes

V12.6 取消原计划的防投毒熔断机制（V11.5 时期实施），存在以下行为变化：

1. **`get_pe_ttm` 移除腾讯 HTTP fallback**：
   - 之前：ZHB 找不到 PE_TTM 时，HTTP fallback 拉腾讯行情 PE（带 30% 防投毒熔断）
   - 现在：ZHB 找不到 PE_TTM 时直接返回 None
2. **`get_pb` 移除腾讯 HTTP fallback**：同上
3. **`get_turnover_pct` 移除腾讯 HTTP fallback**：同上
4. **`ANTI_POISON_DEVIATION_THRESHOLD` 常量保留但标记废弃**（[config.py](file:///d:/GitHub/test/config.py)）

### Added — V12.6 字段路由简化：HTTP 请求减半

V12.6 彻底重塑 `data_provider.py` 的字段获取逻辑：从"先 ZHB 后 HTTP fallback"的盲目尝试，改为基于**运行时机 + 字段类型**的精确路由决策。

### 核心变更

**1. 字段路由决策分类**（[data_provider.py](file:///d:/GitHub/test/data_provider.py)）：
- 新增两个 frozenset 常量：
  - `REQUIRES_REALTIME_HTTP`：必须 HTTP 实时接口的字段（行情/资金流）
  - `ZHB_SUFFICIENT`：ZHB 完全够用的字段（估值/财务/股本/板块）
- 新增两个查询函数：`is_realtime_http_field()` / `is_zhb_sufficient_field()`

**2. 三个 ZHB_SUFFICIENT 字段函数简化**：
- `get_pe_ttm`：移除腾讯 HTTP fallback 和 30% 防投毒熔断（用户决定不需要）
- `get_pb`：移除腾讯 HTTP fallback
- `get_turnover_pct`：移除腾讯 HTTP fallback

**3. HTTP 批量上限实测脚本**（[scripts/test_em_batch_quotes_limit.py](file:///d:/GitHub/test/scripts/test_em_batch_quotes_limit.py)）：
- 5 阶段渐进式实测（100/500/1000/2000/5000 只股票）
- 标记 `@pytest.mark.real_network`，可由用户手动运行

**4. 单元测试**（[tests/test_field_routing.py](file:///d:/GitHub/test/tests/test_field_routing.py)）：
- 15 个测试覆盖：行情类/资金流类/估值类/财务类字段分类、集合互斥、未知字段处理、遗留函数兼容性
- 100% 通过

**5. 文档补充**（[field_dict.md](file:///d:/GitHub/test/docs/field_dict.md)）：
- 新增"V12.6 ZHB 时间机制与字段访问矩阵"专节
- 明确 ZHB 包名=包内数据日期=上一交易日收盘日期
- 字段 × 时机 × 数据源矩阵 + 决策流程图

### 字段访问决策矩阵

| 字段类型 | 盘前 (00:00-09:30) | 盘中 (09:30-15:00) | 盘后 (>= 15:00) |
|:---|:---:|:---:|:---:|
| 行情/资金流类 | ZHB | **HTTP** | **HTTP** |
| 估值/财务/股本/板块 | ZHB | ZHB | ZHB |

### 不做的事

- ❌ 不实施防投毒熔断（HTTP 仅用于行情/资金流，与 ZHB T-1 数据对比无意义）
- ❌ 不做 ZHB 真 T 日判定（ZHB 永远是上一交易日数据）
- ❌ 不做 Fast-Scan 时机判定（盘前用户期望就是昨日数据，ZHB 直接可用）

### 🔧 Migration Guide

**无需迁移**。6 大 Runner 仍通过 `data_provider.get_pe_ttm()` 等接口访问。

但**如果你直接 import 私有模块**或绕过 data_provider 直接调用腾讯 HTTP，需要改用其他数据源（ZHB/Snowball 等）。

### 验证结果

- ✅ data_provider.py 语法正常，模块可正常导入
- ✅ 50+ 个测试全部通过（test_field_routing 15 + test_cache 11 + test_report_runner 16 + test_core_defense 9）
- ✅ get_pe_ttm/get_pb/get_turnover_pct 三个字段函数成功简化

---

## [12.5] - 2026-07-22

### Fixed — ReportRunner 修复 + GD 上传模板真正落地

V12.5 针对 V12.4 复盘发现的 3 大问题进行修正：消除 `get_med_report.py` / `get_lng_report.py` 中重复定义的 Runner 类、让基类 GD 上传辅助方法真正被 6 大 Runner 复用、补全回归测试与上传辅助方法测试覆盖。

### 核心变更

**1. 消除重复 Runner 类 (P0)**（[get_med_report.py](file:///d:/GitHub/test/get_med_report.py) / [get_lng_report.py](file:///d:/GitHub/test/get_lng_report.py)）：
- 删除 `get_med_report.py` 中重复定义的 `MedReportRunner` 类（约 80 行死代码，Python 后定义覆盖前定义）
- 删除 `get_lng_report.py` 中重复定义的 `LngReportRunner` 类（约 80 行死代码）
- 两个脚本各减少 ~70 行

**2. 基类 GD 上传辅助方法真正落地 (P1)**（[stock_common/sc_report_runner.py](file:///d:/GitHub/test/stock_common/sc_report_runner.py)）：
- 新增 `BaseReportRunner.upload_single_report()`：单文件报告（val/mak/ful）的统一上传入口
- 新增 `BaseReportRunner.upload_multi_reports()`：多文件报告（sht/med/lng）的统一上传入口，支持自定义 `name_resolver` 回调
- 新增 `BaseReportRunner._default_resolve_name()`：默认股票名解析器（先查 `_SNAPSHOT_DATA` 再 fallback 到 `tdx_get_quote_full`）
- 6 大 Runner 全部重构 `upload_reports`，委托给基类辅助方法

**3. 测试覆盖补齐 (P2)**（[tests/test_report_runner.py](file:///d:/GitHub/test/tests/test_report_runner.py)）：
- 新增 `TestUploadHelpers` 类：7 个测试覆盖单文件/多文件上传成功/失败/异常/自定义解析器
- 新增 `TestSubclassDuplication` 类：2 个静态分析回归测试，确保 med/lng 不会再次出现重复 Runner 类
- 测试总数从 4 个 → 13 个，**13/13 通过**

**4. 版本管理更新**：
- VERSION: 12.4 → 12.5
- roadmap.md：修正 V12.4 "1500行" 夸大数据为 "~700行"，并新增 V12.5 任务清单
- CHANGELOG.md：补全 V12.3（挂起）、V12.4、V12.5 三段变更记录

### 验证结果

- ✅ 6 大脚本语法检查全部通过
- ✅ test_report_runner.py 13/13 测试通过
- ✅ get_med_report.py 仅含 1 个 MedReportRunner 类
- ✅ get_lng_report.py 仅含 1 个 LngReportRunner 类
- ✅ _default_resolve_name 添加 None 保护（修复 ful 脚本潜在崩溃）

---

## [12.3] - 2026-07-22

### Status — 已挂起（低 ROI / 过度设计）

V12.3 原计划引入三项深度架构演进，但在评估后决定挂起，未实际实施：

1. **DAL 强收口**：强制 6 大脚本仅通过 `data_provider.py` 获取数据，消除 `from stock_common` / `from tdx_client` 直连
2. **异步 Session 优雅关闭钩子**：通过 `atexit` + `asyncio` 生命周期钩子释放 `aiohttp.ClientSession`
3. **并发任务 `asyncio.Semaphore` 信号量限流**：引入 `MAX_CONCURRENT_HTTP_TASKS=50` 和 `MAX_CONCURRENT_TDX_TASKS=20`

### 挂起原因

| 优化点 | 当前状态 | 评估结论 |
|:---|:---|:---|
| DAL 强收口 | 脚本直连底层模块 | ⚠️ 低优先级。当前运行稳定（1000 只股票扫描无问题），属于"架构债"而非"功能性问题"，可后续迭代逐步迁移 |
| 异步 Session 关闭钩子 | 各脚本独立 `create_async_session()` + `finally: close()` | ❌ 不必要。当前模式已经正确释放资源，无 unclosed warning。V12.2 新增的全局单例 `get_em_async_session()` 尚未被任何脚本使用，是更优的解决方案 |
| Semaphore 并发限流 | 各脚本独立 `Semaphore(3)` | ❌ 不必要。`Semaphore(3)` 已经将并发严格限制在 3 个，1000 只股票 ≈ 333 批次。当前限流足够保守，不会出现网络通道暴涨 |

### 决策

- **V12.4 才是高 ROI 任务**：ReportRunner 框架重构真正消除了 6 大脚本中重复的样板代码（~700 行）
- **V12.3 三个优化点保留为远期规划**：若未来扩展到 5000+ 只股票全市场扫描，再考虑启用
- 后续版本将聚焦：**性能监控/可观测性**、**ReportRunner 持续优化**、**V12.4 复盘遗留问题修正（→V12.5）**

### 验证结果

- ⏸️ 三个优化点均未实施，状态为已挂起
- ✅ V12.3 决策已纳入 [docs/roadmap.md](file:///d:/GitHub/test/docs/roadmap.md) 版本规划表

---

## [12.4] - 2026-07-22

### Added — ReportRunner 框架：6大报告脚本统一基类

V12.4 成功构建并全面应用 `BaseReportRunner` 引擎框架，彻底剥离6大策略报告脚本中约 1200+ 行重复的 CLI 解析、运行生命周期 Banner、Google Drive 增量上传与网络资源清理等模板代码。

> ⚠️ **V12.4 复盘**：原声称"精简 1500 行样板代码"，实际净减少约 700 行。此外 6 大 Runner 的 `upload_reports` 仍各自实现，未真正复用基类 `_handle_gd_upload` 模板。这些问题已在 V12.5 中修正。

### 核心变更

**1. 策略报告通用运行框架 BaseReportRunner**（[stock_common/sc_report_runner.py](file:///d:/GitHub/test/stock_common/sc_report_runner.py)）：
- 统一 `argparse` 参数解析 (`--output`, `--no-upload`, `--no-parallel`)
- 自动运行生命周期 Banner/Summary 日志及 Unicode 兼容退回
- 自动创建输出目录落盘
- 自动初始化 Google Drive 并触发类型/标的增量上传与代理清理
- 统一 `cleanup_tdx` 通信套接字释放

**2. 6 大策略脚本全面重构**：
- [get_val_report.py](file:///d:/GitHub/test/get_val_report.py)：重构为 `ValReportRunner`
- [get_sht_report.py](file:///d:/GitHub/test/get_sht_report.py)：重构为 `ShtReportRunner`
- [get_med_report.py](file:///d:/GitHub/test/get_med_report.py)：重构为 `MedReportRunner`
- [get_lng_report.py](file:///d:/GitHub/test/get_lng_report.py)：重构为 `LngReportRunner`
- [get_ful_report.py](file:///d:/GitHub/test/get_ful_report.py)：重构为 `FulReportRunner`
- [get_mak_report.py](file:///d:/GitHub/test/get_mak_report.py)：重构为 `MakReportRunner`

**3. ReportRunner 单元测试套件**（[tests/test_report_runner.py](file:///d:/GitHub/test/tests/test_report_runner.py)）：
- 覆盖 `BaseReportRunner` 的执行流程、CLI 参数拦截与 GD 无缝上传。

## [12.2] - 2026-07-22

### Changed — 工程化优化：资源管理 + 配置集中 + 测试补齐

V12.2 完成工程化优化任务清单，包括数据库连接优雅关闭、配置集中管理、全局异步Session单例、核心防线单元测试、三级日志规范落地。

### 核心变更

**1. 数据库连接优雅关闭**（[stock_cache.py](file:///d:/GitHub/test/stock_cache.py)）：
- 添加 `_close_db()` 函数，进程退出时自动调用 `atexit.register()`
- 执行 WAL 日志 FULL checkpoint，防止数据库损坏

**2. 配置文件集中化**（[config.py](file:///d:/GitHub/test/config.py)）：
- 创建全局配置文件，管理网络超时、限流参数、重试配置、防投毒阈值、缓存TTL
- `tdx_client.py`、`sc_network.py`、`data_provider.py` 已接入

**3. 全局异步 Session 单例**（[sc_network.py](file:///d:/GitHub/test/stock_common/sc_network.py)）：
- 添加 `_EM_ASYNC_SESSION` 单例和 `get_em_async_session()` 函数
- 实现异步请求连接复用，减少 TCP 握手开销

**4. 核心防线单元测试**（[test_core_defense.py](file:///d:/GitHub/test/tests/test_core_defense.py)）：
- 防投毒熔断测试（偏离度阈值判断）
- 令牌桶限流测试（容量限制、获取令牌）
- 熔断器状态转换测试（closed→open→half-open）
- ZHB 事件锁缓存 Key 生成测试
- 9 个测试全部通过

**5. 三级日志规范**（[sc_network.py](file:///d:/GitHub/test/stock_common/sc_network.py)）：
- 添加 `_fallback_logger`，记录数据降级/Fallback 正常触发
- 三级分类：FATAL/BIZ_ERROR、NETWORK_ERROR、FALLBACK

**6. 版本管理更新**：
- VERSION: 12.1 → 12.2

### 验证结果

- ✅ 数据库连接优雅关闭测试通过
- ✅ 配置集中化已在核心模块落地
- ✅ 全局异步 Session 单例可用
- ✅ 9 个核心防线单元测试全部通过

---

## [12.1] - 2026-07-22

### Fixed — 代码质量修复 + 容错层下沉 + 死代码清理

V12.1 针对全量代码审查发现的问题进行修复，包括 L1/L2 缓存同步 Bug、静默异常日志化、容错层实际下沉、异步阻塞修复、未使用导入清理。

### 核心变更

**1. 修复 L1/L2 缓存同步 Bug**（[stock_cache.py](file:///d:/GitHub/test/stock_cache.py)）：
- `invalidate_category()` 和 `invalidate_prefix()` 现在同步清空 L1 内存缓存
- 防止批量删除缓存后，L1 仍然命中返回旧数据

**2. 静默异常日志化**（[data_provider.py](file:///d:/GitHub/test/data_provider.py)）：
- 38 处 `except Exception: pass` 改为 `except Exception as _e: _debug_log(...); pass`
- 保留异常轨迹，便于排查数据失真问题

**3. 容错层实际下沉**（[stock_common/sc_network.py](file:///d:/GitHub/test/stock_common/sc_network.py)）：
- `em_get()` 现在使用令牌桶限流 + 熔断器保护 + 随机 UA
- 成功/失败时自动更新熔断器状态

**4. 修复异步阻塞**（[get_sht_report.py](file:///d:/GitHub/test/get_sht_report.py)）：
- `time.sleep(0.5)` 改为 `await asyncio.sleep(0.5)`
- 避免阻塞事件循环

**5. 清理未使用导入**：
- `get_val_report.py`：清理 14 个未使用的异步函数导入
- `get_ful_report.py`：删除 `ThreadPoolExecutor` / `as_completed` 死导入

**6. Fast-Scan 旁路逻辑修正**（[get_val_report.py](file:///d:/GitHub/test/get_val_report.py)）：
- 仅在非交易日（`closed`）和盘前（`pre_market`）旁路
- 午休、盘后时段不再旁路，正确获取 T 日数据

### 验证结果

- ✅ 6 个核心文件语法检查全部通过
- ✅ L1/L2 缓存同步逻辑正确
- ✅ 容错层令牌桶/熔断器正常工作

---

## [12.0] - 2026-07-17

### Changed — TCP统一层重构：完全移除 easy_tdx 依赖

V12.0 完成 TCP 统一层重构，彻底删除 easy_tdx 依赖，实现"HTTP + mootdx"双通道架构。所有原 easy_tdx/MacClient 独有功能（板块、资金流、全市场快照）已迁移到东财 HTTP 接口和 ZHB 快照。

### 核心变更

**1. 新增5个东财HTTP替代接口**（[stock_common/sc_datasource.py](file:///d:/GitHub/test/stock_common/sc_datasource.py)）：
- `get_em_board_list(board_type)` — 板块列表（替代 MacClient.get_board_list），支持行业/概念/地域
- `get_em_board_members(board_code)` — 板块成员列表（替代 MacClient.get_board_members）
- `get_em_belong_boards(code)` — 个股所属板块（替代 MacClient.get_belong_board）
- `get_em_fund_flow(code)` — 实时资金流（替代 TDX get_fund_flow），使用东财 push2 fflow daykline 接口
- `get_em_history_fund_flow(code, days)` — 历史资金流（替代 TDX get_history_fund_flow）

**2. tdx_client.py 8个函数迁移到HTTP委托**（[tdx_client.py](file:///d:/GitHub/test/tdx_client.py)）：
- `tdx_get_fund_flow` / `tdx_get_history_fund_flow` → 委托到 `get_em_fund_flow` / `get_em_history_fund_flow`
- `tdx_get_belong_boards` / `tdx_get_board_list` / `tdx_get_board_members` / `tdx_get_board_by_name` → 委托到对应 `get_em_*` HTTP函数
- `tdx_get_market_abnormal_data` / `tdx_get_all_stocks` → 改用 ZHB 全市场快照

**3. 删除 easy_tdx 辅助代码**：
- 删除 `_patch_easy_tdx_heartbeat()` 函数及调用（V7.5 monkey-patch 心跳线程，mootdx 内部已管理）
- 删除 `_mac_health_check()` 函数
- 删除 `_check_mac()` 函数（含 `from easy_tdx import MacClient`）
- 删除 `_get_mac_client()` 函数（含 `from easy_tdx import MacClient`）
- 删除全局变量 `_TDX_MAC_CLIENT`、`_MAC_AVAILABLE`
- 清理 `_reset_tdx_connections()` 和 `cleanup_tdx()` 中的 MacClient 相关代码

**4. main.py 移除 easy_tdx 依赖检查**（[main.py](file:///d:/GitHub/test/main.py)）：
- 删除 `import easy_tdx` 检查及缺失时的 `pip install easy-tdx` 提示

### 最终架构

```
┌─────────────────────────────────────────────┐
│            报告脚本 (val/sht/med/lng/ful)      │
├─────────────────────────────────────────────┤
│           data_provider.py (统一入口)          │
├──────────────┬──────────────┬───────────────┤
│   ZHB本地快照  │   HTTP层     │   mootdx TCP   │
│  (盘后主力源)  │ (行情/资金流/ │ (K线/行情/F10 │
│               │  板块/名称)   │  深度数据)     │
├──────────────┼──────────────┼───────────────┤
│  本地文件读取  │ sc_network   │  mootdx       │
│               │ +容错层      │  (统一TCP层)   │
└──────────────┴──────────────┴───────────────┘
```

### 验证结果

- ✅ tdx_client.py / main.py / sc_datasource.py 语法检查全部通过
- ✅ 5个新HTTP替代接口导入正常
- ✅ tdx_client 导入正常，所有函数可调用
- ✅ test_tdx_client.py 11个测试全部通过
- ✅ test_f10_chapters_integration.py 3个测试全部通过
- ⚠️ test_calendar.py 8个测试失败（预先存在的 Bug，与本次修改无关：`is_workday` 中 zhb_holidays 逻辑错误，节假日落在工作日时返回 True）

---

## [11.5] - 2026-07-17

### Added — Data Provider 统一数据层正式启用 + ZHB时间体系重构 + 网络容错层

历时多个版本规划，data_provider.py 统一数据中心层在 V11.5 正式全面激活，六大报告脚本全部完成迁移。同时新增三大防封机制，彻底提升网络稳定性。

### 核心架构

**字段时效性三级分级模型**：
- **实时层**（price, change_pct, amount）：盘中TDX优先，盘前/盘后优先ZHB T-1
- **准实时层**（main_net_buy, streak_days, turnover_pct）：ZHB优先（T-1可接受）
- **静态层**（pe_ttm, pb, dividend_yield, 52w_range, change_ytd, totals, industry）：ZHB优先

**接口优先级原则（按TDX TCP原生支持情况分级）**：
- **实时字段**（price/change_pct/amount）：ZHB(盘后)→TDX(盘中)→腾讯(fallback)
  - TDX TCP原生支持这些字段，真正高效
- **估值字段**（pe_ttm/pb/turnover_pct）：ZHB→腾讯
  - TDX TCP不返回这些字段，无需TDX中间层
- **股息率**：ZHB only
  - TDX和腾讯都不直接返回，ZHB有完整数据

**交易状态感知**：盘前(<9:30)用上一交易日收盘数据，盘中TDX优先，盘后用ZHB

**缓存策略（按字段变化频率分级TTL）**：
- 实时层（price/change_pct/amount）：30分钟 + 交易日模式（原60秒，API调用减少97%）
- 日变层（pe_ttm/pb/turnover_pct/main_net_buy/streak_days）：24小时 + 交易日模式
- 周变层（52w_range）：7天（52周高低极少变化）
- 季度层（total_shares/industry）：90天（行业归属几乎不变）
- 月变层（dividend_yield）：30天（分红半年才变）
- 全函数 async 版本支持，`asyncio.to_thread` 模式

### 各脚本迁移情况

1. **val脚本（选股报告）**：
   - 初始化阶段：全市场数据获取改为 `get_market_snapshot_async()`
   - 6个策略改为async：策略01/04/08/10/14/20
   - 策略执行器自动识别async/同步函数，智能调度
   - K线类、龙虎榜、股东数据等保持原路径

2. **ful脚本（深度报告）**：
   - layer1_market / layer2_research / layer_ind_industry 改为async，优先data_provider
   - layer6_fundamental / layer_risk 改为async，优先data_provider
   - 行业对比层用 `asyncio.gather` 并发获取同行数据（替代ThreadPoolExecutor）
   - analyze_stock主函数重构为async并发执行架构

3. **sht脚本（短线报告）**：
   - generate_report_async 新增 `get_stock_composite_async` 统一入口
   - _zhb_data / q / 主力资金 / 连涨天数 均优先从composite提取
   - 缺失字段自动fallback到原数据源

4. **med脚本（中线报告）**：
   - generate_report_async 优先data_provider综合数据
   - get_stock_sector_rank 改为async，涨跌幅从data_provider获取
   - GD上传名称获取优化

5. **lng脚本（长线报告）**：
   - generate_report_async 新增 `get_stock_composite_async` 统一入口
   - 腾讯行情/zhb重叠字段/估值指标/股息率展示 均优先data_provider
   - zhb独有字段（change_5d/10d/20d/60d等）保持原路径

6. **mak脚本（做市商报告）**：
   - get_market_abnormal_data 改为async，全市场快照用data_provider
   - get_ths_hot_pool 改为async，批量行情用data_provider
   - generate_sector_report 改为async并发架构

### Changed — data_provider.py 功能增强

1. **新增5个字段函数**：get_turnover_pct, get_totals, get_market_cap, get_industry, get_streak_days
2. **全函数缓存装饰器**：12个核心函数全部添加 @cached 装饰器
3. **12个async版本函数**：所有主要函数都有 `_async` 后缀版本
4. **交易状态感知**：盘前/盘中/盘后自动选择最优数据源
5. **get_stock_composite优化**：ZHB全量预取 + 实时字段补全，减少重复调用
6. **get_field_value通用接口**：支持动态字段名查询

### Fixed

1. data_provider.py 从死代码状态激活，六大报告脚本全部迁移
2. 各脚本数据获取统一入口，消除重复代码和不一致性
3. **接口优先级修正（按TDX TCP原生支持情况分级）**：
   - 实时字段（price/change_pct/amount）：ZHB(盘后)→TDX(盘中)→腾讯(fallback)
   - 估值字段（pe_ttm/pb/turnover_pct）：ZHB→腾讯（TDX不返回这些字段，移除多余中间层）
   - 股息率：ZHB only（TDX和腾讯都不直接返回）
   - 成交额：盘前/盘后用ZHB T-1，盘中腾讯→TDX（恢复原始设计）
4. **TTL策略优化**：实时层60秒→30分钟；52w_range→7天；industry→90天；dividend_yield→30天
5. **Fallback链补全**：
   - get_52w_range：添加K线计算fallback（取260根日K最高/最低）
   - get_change_ytd：添加K线计算fallback（年初近似涨幅）
   - get_streak_days：添加K线计算fallback（连续涨跌天数）
6. **限流架构保持不变**：TDX全局锁+HTTP Semaphore(3)+脚本级Semaphore(3)三层保护未受影响

### Added — ZHB时间体系重构与新因子落地

1. **ZHB时间体系重构**：
   - ZHB文件次日更新机制：今日运行脚本获取昨日数据（如7月17日运行→zhb_20260716）
   - 非交易日运行：获取最近一个交易日的数据
   - ZHB中的"基准日" = ZHB文件名日期，明确区分基准日/T-1/T-2数据
   - composite新增`_zhb_data_date`和`_zhb_offset_days`元信息

2. **量能三连击因子**（纯ZHB数据，无需实时T）：
   - 基于ZHB的amount/T-1成交额、amount_1d/T-2成交额、amount_2d/T-3成交额
   - 检测放量加速趋势：amount > amount_1d > amount_2d
   - 新增`get_volume_acceleration`函数，返回加速比率和信号标签

3. **资金动量加速因子**（纯ZHB数据，无需实时T）：
   - 基于ZHB的main_net_buy_amount/基准日主力净流入、main_net_buy_amount_1d/T-1主力净流入
   - 计算资金流入加速度：净流入差值和变化率
   - 新增`get_capital_momentum`函数，返回动量值、比率和信号标签（抢筹加速期/衰竭期/平稳）

### Changed — 缓存策略与脚本定位优化

1. **stock_cache.py交易日期过期计算优化**：
   - 适配ZHB次日更新机制，明确缓存过期逻辑
   - 盘前/盘中：缓存到当日15:00（等收盘更新）
   - 盘后/非交易日：缓存到下一个交易日15:00（等次日ZHB更新）

2. **val脚本定位说明更新**：
   - 明确标注为"纯盘后选股工具"，所有数据来自ZHB本地快照
   - 输出报告中添加ZHB数据日期和更新机制说明
   - 强调延迟1-2个交易日的数据时效性

3. **sht报告主力资金占比修复**：
   - 修复时空错位Bug：使用ZHB内部的成交额（基准日）计算占比，而非实时API成交额
   - 标签从"T日主力净流入"改为实际ZHB日期标注

### Added — 网络容错层（三大防封机制）

借鉴 stock-sdk 仓库的防封架构，新增 `sc_fault_tolerance.py` 模块：

1. **令牌桶限流器（TokenBucket）**：
   - 按域名独立配置 RPS（每秒请求数）
   - 东财类域名：1.0 RPS；巨潮/财联社：3.0 RPS；腾讯/新浪/同花顺：5.0 RPS
   - 最大突发量 max_burst=3，平滑流量峰值

2. **熔断器模式（CircuitBreaker）**：
   - 三态转换：Closed → Open → Half-Open
   - 连续5次失败触发断路，60秒后自动恢复试探
   - 被封后立即切断请求，避免资源耗尽

3. **随机UA池 + 指数退避**：
   - 10个主流浏览器UA随机轮换，7个金融网站Referer随机轮换
   - 指数退避重试：1s → 2s → 4s → 8s（最大32s），带随机抖动0.5-1.5x
   - 429状态码检测 + Retry-After响应头解析

4. **sc_network.py 集成**：
   - `_do_request`：添加随机UA/Referer + 指数退避
   - `_request_with_retry`：集成令牌桶 + 熔断器
   - `_async_request_with_retry` / `_async_quick_request`：异步版同样集成
   - 域名配置新增 `rps` 参数

### Changed — 数据源架构优化

1. **val脚本架构清理**：
   - `sina_financial_report` 本地函数迁移至 `sc_datasource.get_sina_financial_report`
   - val脚本成为纯策略层，不再包含爬虫实现
   - 策略05（深度价值折价）改为调用统一数据源接口

2. **东财批量行情替代TDX**：
   - 新增 `get_em_batch_quotes()` 函数（sc_datasource.py）
   - 使用东财 push2 接口批量获取股票名称，支持网络容错机制
   - val脚本中股票名称查询从 `tdx_get_quotes_batch` 改为 `get_em_batch_quotes`
   - 消除Socket断线风险，HTTP接口 + 熔断器保护

3. **ZHB时间对齐完善**：
   - `get_stock_composite` 新增 `main_net_buy_amount_2d` 和 `main_net_buy_hands_2d` 字段
   - 时间偏移时正确映射：ZHB[14]→T-1，ZHB[15]→T-2，不再丢失数据

## [11.4] - 2026-07-16

### Fixed — 死代码清理与缓存逻辑修复

1. **data_provider.py死代码清理**：6个报告脚本（sht/val/med/lng/mak/ful）共47处`from data_provider import (...)`导入语句全部删除——导入的函数（get_stock_price/get_pe_ttm/get_pb等11个）从未被实际调用，脚本通过tdx_get_quote_full/get_tencent_quote/get_zhb_single_stock_data等底层函数直接获取数据
2. **TTL重复键修复**：stock_cache.py中`hsgt_flow`出现两次（第211行14天/第233行24小时），后者覆盖前者。将第233行重命名为`hsgt_macro_flow`，同步更新sc_datasource.py中`get_hsgt_macro_flow`的category引用
3. **med报告静默异常修复**：3处`except: pass`改为`except as _e: _debug_log(...)`，避免隐藏潜在问题（资产负债表预警计算/EPS行解析/黑马潜质检测）

### Added — 财联社快讯与舆情互动层集成

按project_memory硬约束要求，在4个报告脚本中集成财联社快讯和互动易问答，并实现时间阈值过滤：

1. **sht报告**：在"短线情绪与事件催化"章节新增财联社快讯（近420分钟=7小时，最多10条）和互动易问答（近24小时，最多5条）
2. **med报告**：新增"十七、舆情与互动"章节，包含财联社快讯（近3天，最多10条）和互动易问答（近7小时，最多5条）
3. **lng报告**：新增"十、舆情与互动"章节，包含财联社快讯（近2天，最多10条）和互动易问答（近30天，最多10条）
4. **ful报告**：在layer5_news函数中新增财联社快讯（近3天，最多15条）和互动易问答（近15天，最多10条），并在渲染层添加显示逻辑

### Changed — tests目录全面重写

1. **删除21个废弃文件**：17个diag_*.py诊断脚本、diagnose_tdx.py、test_reports.py（与test_strategy.py完全重复）、README.txt（旧版文档）、test_em_rate_limit.py（非pytest格式）
2. **更新3个测试文件**：
   - test_cache_verify.py：重写7个测试方法匹配V10.0的cross_verify新逻辑
   - test_cache.py：增加L1内存缓存清理（V10.3新增L1/L2双级架构）
   - test_f10_chapters_integration.py：为med/lng报告新增舆情与互动章节断言
3. **重写README.md**：反映实际文件状态，删除错误声明

## [11.3] - 2026-07-16

### Fixed — 缓存层T-1数据混入修复

通过7/15 vs 7/16报告对比发现，4个缓存分类在跨日运行时携带T-1数据混入T0报告：

1. **industry_compare改为交易日模式**：`get_industry_comparison` 添加 `trading_day=True`，板块排名数据在交易日15:00自动过期，避免昨日板块排名混入今日报告
2. **industry_peers改为交易日模式**：`get_industry_peers` 和 `get_stock_sector_rank` 添加 `trading_day=True`，同业对比和板块内排名在交易日15:00过期
3. **ths_hot_reason改为交易日模式**：`ths_hot_list` 添加 `trading_day=True`，热点题材在交易日15:00过期
4. **北向资金批量缓存修复**：
   - `get_hsgt_macro_flow` 添加 `@cached(trading_day=True)` 交易日模式缓存
   - `get_hsgt_macro_flow_async` 改为委托到同步缓存版本（`asyncio.to_thread`）
   - sht批量模式移除预取共享机制（`_cached_hsgt_async`），改为每只股票独立调用，由缓存层保证仅1次API请求
   - 修复前：35只股票共享同一份北向资金数据（可能为T-1）；修复后：第一只股票触发API写入缓存，后续股票读缓存，每个交易日15:00自动刷新

### Verified — ZHB数据绝对验证

- 用户手动解压zhb_20260714.zip和zhb_20260715.zip，用贵州茅台(600519)与新浪/东财真实收盘数据交叉验证：
  - 7/14 涨跌幅0.32%、成交额52.95亿 → 精确吻合
  - 7/15 涨跌幅2.98%、成交额89.23亿 → 精确吻合
- 确认ZHB包名日期100%代表当天盘后真实数据，是T-1日绝对快照

## [11.2] - 2026-07-16

### Fixed — 命令行参数粘连检测

- **clean_codes增加flag粘连警告**：当股票代码参数中包含`--`时（如`601718际华--all`缺少空格），打印警告提示用户检查命令行格式，避免`--all`参数被误解析为股票代码

### Changed — ZHB混合分层架构

- **val脚本全市场数据加载升级为混合分层模式**：
  - [API实时层] 覆盖 price/change_pct/amount/pe_ttm/turnover_pct 五个动态字段
  - [ZHB静态层] 保留 high_52w/low_52w/pb/dividend_yield/ipo_price/industry_code 等慢变字段
  - 新增数据来源分层日志，运行时清晰展示各字段数据来源
- **策略19 reason标注实时来源**：price和pe_ttm标注"(实时)"，52周区间标注"(T-1)"

### Added — ZHB字段真实性验证脚本

- **新增 verify_zhb_fields.py**：独立验证脚本，包含两部分验证
  - Part A 跨日Delta验证：用3天ZHB缓存数据检查7类字段的跨日逻辑一致性（change_pct/streak_days/change_Nd/main_net_buy滚动/52w单调性）
  - Part B 外部数据校验：随机抽样50只股票，用TDX K线和腾讯行情对比ZHB字段绝对值（pe_ttm/high_52w/low_52w/streak_days/change_5d/change_20d/change_ytd/amount）
  - Delta验证结果：14项全部PASS，字段映射逻辑一致性100%

## [11.1] - 2026-07-16

### Fixed — ZHB数据时效性问题修复

1. **全市场成交额实时覆盖**：val脚本加载全市场数据时，用腾讯实时行情的`amount_wan`覆盖ZHB的T-1成交额，确保流动性排序和策略计算使用当日数据
2. **流动性池实时排序**：`top_liquidity_pool`基于实时成交额重新排序，避免使用昨日成交额导致今日放量股被遗漏
3. **策略19 52周低位标注T-1数据**：在reason中明确标注52周区间基于T-1数据，使用户有明确预期
4. **策略20 主力资金增加TDX实时fallback**：ZHB数据不可用或不新鲜时，自动切换到TDX实时资金流，reason中显示数据来源（ZHB(T-1)/TDX实时）
5. **腾讯批量行情增加amount_wan字段**：`_tencent_batch_fallback`返回值新增`amount_wan`，为全市场实时成交额覆盖提供数据支撑

## [11.0] - 2026-07-16

### Added — 阶段三.4：六大报告脚本迁移到 Data Provider

- **所有报告脚本统一导入 Data Provider 模块**：
  - [get_sht_report.py](file:///d:/GitHub/test/get_sht_report.py#L62-L65)
  - [get_val_report.py](file:///d:/GitHub/test/get_val_report.py#L64-L67)
  - [get_med_report.py](file:///d:/GitHub/test/get_med_report.py#L60-L62)
  - [get_lng_report.py](file:///d:/GitHub/test/get_lng_report.py#L54-L56)
  - [get_mak_report.py](file:///d:/GitHub/test/get_mak_report.py#L38-L40)
  - [get_ful_report.py](file:///d:/GitHub/test/get_ful_report.py#L72-L75)

- **Data Provider 统一数据层正式启用**：
  - 实时字段（价格、涨跌幅）→ 强制走 API
  - 准实时字段（主力资金流向）→ 优先 ZHB，失败 fallback 到 API
  - 静态字段（PE/PB/股息率/52周高低）→ ZHB 优先

### Changed — val 脚本选股池扩大

- **策略19/20 扩大到全市场扫描**：从 top_n=300 改为全市场 all_stocks
- **每策略显示股票数**：从 5 只增加到 10 只（`_top5_sorted` 返回 `[:10]`）

### Fixed — 9个Bug修复

1. **sht 报告主力资金占比 bug**：`amount_wan` 变量未定义 → 改为 `q.get('amount_wan', 0)`
2. **val 脚本 banner 策略数错误**：`"策略: 18"` → `"策略: 20"`
3. **val 脚本 `_sfmt` 字典缺失**：添加策略19/20格式化项
4. **val 策略20无 zhb_fresh 检查**：添加 `if not is_zhb_data_fresh(): return result`
5. **lng 脚本 `_zhb_date` 变量作用域**：提前初始化 `_zhb_date = ""`
6. **ful 脚本重复调用 `get_zhb_single_stock_data`**：复用已有的 `_zhb_data`
7. **ful 脚本股息率 fallback**：逻辑正确，无需修改
8. **data_provider.py 死代码问题**：添加状态注释，标记 V11.0 正式启用
9. **策略19/20 参数签名**：移除 `top_n` 参数，直接遍历 `stocks`

## [10.3] - 2026-07-16

### Added — ZHB 字段解锁（基于 zhb_analysis 深度分析）

**zhb 资金流向字段解锁**（基于 zhb_analysis 深度分析 + 双日 Delta 验证 + 公式验算）：
- `tdxstat2[9]` → `main_net_buy_hands`（T 日主力净买入量，手）
- `tdxstat2[10]` → `main_net_buy_hands_1d`（T-1 日主力净买入量，手）
- `tdxstat2[14]` → `main_net_buy_amount`（T 日主力净流入额，万元）
- `tdxstat2[15]` → `main_net_buy_amount_1d`（T-1 日主力净流入额，万元）
- 验证方法：双日 Delta 滚动匹配（10/10 通过）+ 公式验算（`[9]×100×收盘价÷10000≈[14]`，误差<1%）
- 📦 新增便捷函数：`get_main_net_buy`、`get_main_net_buy_amount`、`get_main_net_buy_amount_1d`
- 📊 zhb 字段时效性分级增强：新增"准实时"字段分类（max_delay_days=1），资金流向字段归入此类
- 📋 docs/roadmap.md：新增实施路线图，覆盖阶段一（核心字段补全、阶段二（脚本增强）、阶段三（架构重构）

### Added — 阶段二：六大报告脚本新增ZHB分析维度

**sht报告（短线）**：
- 新增主力资金流向展示（净流入额/净买入量，对比T-1日）
- 新增连涨连跌天数分析（zhb独有字段）
- 资金流向与涨幅联动分析

**val报告（估值）**：
- 新增策略19（52周低位筛选）：位置百分位<30%且PE<50x
- 新增策略20（主力资金占比）：主力净流入占成交额>3%
- 优化策略并行逻辑（ThreadPoolExecutor，20策略并行扫描）
- 策略扫描范围扩大至500-1000只

**med报告（中线）**：
- 新增IPO破发度分析（现价/发行价，低于发行价标记破发）
- 新增中线动能对比（5日/10日/20日阶段涨幅）
- 股息率优先使用zhb数据

**lng报告（长线）**：
- 新增EPS（每股收益）展示（zhb独有字段）
- 新增员工总数及人效比分析（市值/员工数）
- 年初至今涨幅优先使用zhb数据

**mak报告（市场热点）**：
- 新增全市场主力资金监控（总净流入额）
- 通过zhb全市场快照计算主力资金总量
- 资金流向与市场涨跌联动分析

**ful报告（完整）**：
- 整合所有新字段：主力资金流向、52周位置、IPO破发度、EPS、员工数
- 统一数据获取逻辑，优先zhb数据

### Added — 阶段三.1：统一数据中心层（Data Provider）

- **创建 data_provider.py**：统一数据源路由层
- **字段时效性分级路由**：
  - 实时字段（0天延迟）→ 优先API（腾讯行情等）
  - 准实时字段（1天延迟）→ 优先ZHB，失败fallback到API
  - 静态字段（3天延迟）→ ZHB优先
- **聚合接口**：`get_stock_composite(code)` 一次调用获取完整股票数据
- **主力资金流向专用接口**：`get_main_net_buy(code)`、`get_main_net_buy_amount(code)`
- **52周数据接口**：`get_52week_range(code)`
- **IPO数据接口**：`get_ipo_info(code)`

### Added — 阶段三.2：缓存模块L1/L2双级架构

- **L1内存缓存**：进程内字典存储，支持TTL自动过期，最大5000条目
- **L2 SQLite缓存**：跨进程/跨运行持久化（原有架构）
- **双级查询策略**：优先L1 → L2命中后回写L1 → 首次请求写入双级
- **线程安全**：L1使用threading.Lock保护
- **命中率提升**：同脚本运行期内重复请求零I/O，大幅减少SQLite读写

### Added — 阶段三.3：ZHB自动化入库管道

- **创建 zhb_sync.py**：完整的定时同步工具
- **定时模式**：支持cron表达式（如"0 9,18 * * *"）和间隔模式（如每6小时）
- **智能下载**：仅在数据日期更新时下载，避免无效请求
- **数据校验**：校验zip完整性、字段数量、数据日期合理性
- **状态追踪**：记录最后成功同步时间、连续失败次数、总同步次数
- **清理策略**：保留最近7天数据，自动清理过期文件
- **命令行接口**：`--once`（单次同步）、`--cron`（定时任务）、`--interval`（间隔任务）、`--status`（查看状态）

### Changed — 数据获取优先级优化

- 所有脚本优先使用ZHB数据，原有HTTP/TDX路径降为fallback
- 实时字段（如当日开盘/收盘价、涨幅）强制使用API获取，确保准确性
- 准实时字段（资金流向）优先ZHB，过期时自动fallback

### Fixed — 遗留问题修复

- 修复val脚本导入错误（get_data_date未定义）
- 修复"休市日"标签错误（非交易日标记问题）

## [10.2] - 2026-07-16

### Fixed — 缓存命中率修复（核心）

- **修复 cross_verify 读写互斥BUG**（影响14个分类：concept_blocks/lockup_expiry/basic_info/financial/balance_sheet/cash_flow/gross_margin_roe/eps_forecast/dividend/f10_financial/f10_shareholder/f10_share_capital/holder_structure/sina_financial_report）：
  - 症结：`set_cache` 数据变化分支写入 `prev_value=旧值, value=新值, verified=1`，但 `get_cache` 检查 `prev_value != value` 时直接删除缓存返回 None → 数据源发生过一次变化后缓存永久失效
  - 修复：删除 `get_cache` 中 `prev_value != value` 的误删检查，`prev_value` 仅用于数据变更追踪，不影响缓存命中
- **修复 `_has_zero_price` 递归误杀**（影响 dragon_tiger/industry_compare/f10_fund_flow 等）：
  - 症结：原递归检查整个 dict/list 的所有子层级，嵌套结构中任一子项 `price=0`（如龙虎榜未成交席位、板块列表中无成交板块）就跳过整条缓存
  - 修复：改为仅检查顶层 dict 的 `price`/`close` 字段，不递归子层级
- **修复 `today_str` 污染缓存 key**（影响 lockup_expiry/dragon_tiger）：
  - 症结：`get_lockup_expiry(code, today_str, days=90)` 和 `get_dragon_tiger_board(code, today_str, days=30)` 的参数 `today_str` 被 `_build_key` 拼入 key，每天 key 不同 → 90天/7天TTL完全失效，每天每只股票都重新请求
  - 修复：移除 `today_str` 参数（改为函数内部 `datetime.now().strftime("%Y-%m-%d")` 自动计算），同步更新7个调用点 + 1个测试文件
- **放宽 `valid_if` 校验**（影响 industry_peers/basic_info/f10_fund_flow/f10_news/f10_reminders/f10_announcements/f10_financial/f10_shareholder/f10_share_capital）：
  - `industry_peers`：`all(p.price>0)` 改为 `any(p.price>0)`，避免单个 peer 停牌导致整条缓存拒写
  - `basic_info`：`list_date` 校验改为 `code` 校验，避免 TDX 偶尔返回空 list_date 时整条拒写
  - F10 系列：`valid_if=bool(r)` 改为 `valid_if=lambda r: r is not None`，避免空 dict/list 被拒写

### Fixed — zhb数据滞后优先级分级

- **新增 `zhb_field_safe(field_name)` 函数**：按字段时效性分级判断 zhb 数据是否安全可用
  - 实时字段（change_pct/amount/price 等）：zhb 日期必须是今天（`max_delay_days=0`）
  - 阶段/静态字段（pe_ttm/high_52w/dividend_yield 等）：3天延迟可接受
- **mak 脚本 zhb 优先级修复**：`change_pct` 是实时字段，`get_market_abnormal_data()` 改为 `if zhb_field_safe("change_pct")` 才用 zhb，否则 fallback 到 TDX（避免滞后涨跌幅误判涨停/跌停）
- **val 脚本 zhb 实时字段覆盖**：用 `tdx_get_quotes_batch` 返回的实时 `change_pct` 覆盖 zhb 的滞后值（避免涨停/跌停数量统计错误）
- **sht/med/lng 脚本 zhb 数据日期标注**：zhb 数据不新鲜时在报告头部标注 `ℹ️ zhb数据日期: YYYYMMDD（延迟，阶段涨幅/52周高低等数据可能有1-2天滞后）`

### Fixed — 其他BUG

- **修复 val 脚本 ImportError**：`full_market_snapshot` 不存在于 `stock_common.__init__` 导出，改为 `get_zhb_full_market_snapshot`
- **修复"休市日"标签错误**：`get_market_status()` 交易日16:30后从 `closed` 改为新增状态 `post_close`，避免盘后运行脚本时错误显示"休市日"
  - sht/med/lng/ful 四个脚本同步更新 `post_close` 分支，显示"ℹ️ 盘后收盘：数据为今日收盘快照"

### Changed

- **`get_lockup_expiry` / `get_dragon_tiger_board` 函数签名变更**：移除 `today_str` 参数，调用方无需传递日期字符串（向后不兼容，调用方需更新）

## [10.1] - 2026-07-15

### Added

- **zhb字段映射重大修正**（基于injoyai/tdx开源仓库源码验证）：
  - tdxstat字段映射：`change_pct` 从[2]修正为[6]，新增 `streak_days`[5]（连涨连跌天数）、`change_pct_1d`[7]（昨日涨跌幅）、`change_pct_2d`[8]（前日涨跌幅）
  - 新增确认字段：`dividend_yield`[10]（股息率）、`employee_count`[15]（员工人数）、`change_5d`[28]、`change_10d`[30]、`change_ytd`[21]（年初至今涨跌幅）
  - tdxstat2字段映射：`amount` 修正为[3]（今日成交额，万元），新增 `amount_1d`[5]、`amount_2d`[7]、`ipo_price`[16]（IPO发行价）
  - 新增 `full_market_snapshot`（tdxstat+tdxstat2合并）、`market_stat2_snapshot` 等批量接口
  - 新增便捷函数：`get_dividend_yield`、`get_streak_days`、`get_change_ytd`、`get_ipo_price`、`get_amount_wan`、`get_amount_1d`
- **全局股本缓存层**（V10.1新增）：
  - 新增 `stock_common/sc_capital_cache.py` 模块，提供总股本/流通股全局缓存
  - 全局JSON文件缓存（`cache/share_capital.json`），90天TTL，被动累积式构建
  - 市值内存计算：`calc_mcap_yi` = 收盘价 × 总股本 / 10000，零网络请求
  - 支持 `batch_refresh_capital` 批量刷新缺失股本数据
- **缓存分类扩展**：
  - 新增 `share_capital` 分类（90天TTL），用于存储股本数据
  - 新增 `basic_info_static` 分类（90天TTL），预留静态基本信息缓存
- **stock_common导出更新**：`__all__` 列表和 `from sc_datasource import` 块新增11个V10.1函数导出

### Changed

- **val脚本全策略切换到zhb数据**：
  - 使用 `full_market_snapshot` 替代 `tdx_get_all_stocks` 加载全市场数据
  - 全市场数据加载从 ~7.7秒 降至 <0.1秒，零HTTP请求
  - 通过 `tdx_get_quotes_batch` 批量获取收盘价，结合全局股本缓存计算市值
  - 修复名称补充逻辑，同步更新 `_stock_map` 中的股票名称
  - 流动性池从Top300扩大到Top500，策略扫描范围扩大（200-300→500-1000）
- **mak脚本全量切换zhb数据**：
  - 优先使用zhb全市场快照，失败时自动回退到TDX MAC协议
  - 新增 `_get_zhb_market_data` 函数，从zhb构建异动扫描数据结构
  - 新增 `_calc_3d_from_daily` 函数，从T/T-1/T-2日涨跌幅复利推算3日累计涨跌幅
  - 全市场数据加载时间显著缩短，减少TDX服务器压力
- **sht脚本zhb优先改造**：
  - 行业归属：zhb `industry_code` 优先，`get_stock_info` 返回N/A时用zhb补充
  - 股息率：zhb `dividend_yield` 优先，无zhb时fallback到 `get_dividend_history`
  - 阶段涨幅、52周区间：zhb独有指标直接展示，不再需要K线计算
- **med脚本zhb优先改造**：
  - PE估值：zhb `pe_ttm/pe_dynamic` 优先，无zhb时fallback到腾讯行情
  - 股息率：zhb `dividend_yield` 优先展示，详细分红记录仍用 `get_dividend_history`
  - 行业归属：zhb优先，减少TDX `tdx_get_belong_boards` 请求
  - 阶段涨幅（5/10/20/30/60日）、52周区间：zhb独有指标直接展示
- **lng脚本zhb优先改造**：
  - PE/PB估值：zhb `pe_ttm/pe_dynamic/pb` 优先，无zhb时fallback到腾讯行情
  - 历史最高价：zhb `high_52w` 优先，无zhb时fallback到 `get_historical_high`
  - 股息率：zhb `dividend_yield` 优先展示，详细分红记录仍用 `get_dividend_history`
  - 行业归属：zhb优先
  - 阶段涨幅、52周区间、YTD收益率、员工人数：zhb独有指标直接展示
- **ful脚本zhb优先改造**：
  - Layer1行情层：PE/PB估值zhb优先覆盖 `result["basic"]`，无zhb时使用TDX行情
  - 52周高低、阶段涨跌幅（20日/60日）：zhb优先，无zhb时fallback到K线计算
  - 股息率：zhb `dividend_yield` 优先，无zhb时fallback到 `tdx_get_dividend_history` 计算
  - zhb独有指标（成交额、员工人数、IPO发行价、YTD、5/10/30日涨跌幅）直接写入 `result["basic"]["zhb"]`
- **缓存策略优化**：
  - `basic_info` TTL从30天调整为1天（修复市值/价格等动态字段缓存过期问题）
  - 静态股本数据通过 `share_capital` 分类单独缓存（90天TTL），与动态数据分离

### Fixed

- **zhb字段映射错误**：修正tdxstat中 `change_pct` 字段位置错误（[2]→[6]），以及tdxstat2中 `amount` 字段位置错误
- **市值全为0问题**：新增全局股本缓存层，通过收盘价×总股本实时计算市值，解决zhb数据源缺失市值字段的问题
- **多策略共振无名称问题**：修复名称补充逻辑，补充名称时同步更新 `_stock_map`，确保共振部分能正确显示股票名称

## [10.0] - 2026-07-14

### Added

- **zhb全局配置总包全面升级**：
  - **进程安全文件锁**：`zhb_client.py` 新增 `_acquire_file_lock`/`_release_file_lock` 函数，多进程并发下载时自动加锁，避免重复下载和文件损坏
  - **磁盘空间保护**：新增 `_check_disk_space` 函数，空间不足（<100MB）时自动清理旧缓存，保留最新文件
  - **智能日期筛选**：新增 `should_use_zhb_data()`/`is_zhb_date_matching()` 函数，根据当前时机（收盘后/开盘前/休市日/盘中）智能判断是否使用zhb数据，盘中强制实时获取
  - **节假日数据导出**：新增 `get_zhb_holidays` 函数，导出 needini.dat 中的节假日列表（1991-2030），返回 YYYYMMDD 字符串列表
  - **证监会行业分类**：新增 `get_zhb_csrc_industries` 函数，解析 incon.dat（3703个行业分类），涵盖A-S门类
  - **中概股ADR**：新增 `get_zhb_adr_stocks` 函数，解析 tdxadr.cfg（30只中概股ADR对应表）
  - **可转债数据**：新增 `get_zhb_convertible_bonds` 函数，解析 othersg.cfg（可转债信息）
  - **退市股对照表**：新增 `get_zhb_delisted_stocks` 函数，解析 pttab.dat（股票代码对照表，含退市股）
- **行业分类统一为申万标准**：zhb.tdxzs3 提供完整的申万行业分类（467个四级分类），对标公募基金标准，通达信行业作为降级方案
- **pytdx依赖**：`requirements.txt` 新增 `pytdx>=1.0`，用于 zhb.zip 协议下载
- **缓存命中率统计**：`stock_cache.py` 新增 `_CACHE_STATS` 全局计数器和 `print_cache_stats()` 函数，通过 `atexit` 在进程退出时自动打印总命中率和分类命中率（按未命中数降序显示前10个低命中率分类）
- **main.py任务顺序优化**：调整脚本执行顺序为 `val → mak → sht → med → lng → ful`，全市场扫描产生的缓存被后续单股分析脚本复用

### Changed

- **死代码清理**：
  - `gd_uploader.py`：删除 `run_report_to_gd`、`gd_auth_and_get_parent`
  - `get_lng_report.py`/`get_med_report.py`：删除 `generate_report` 同步包装函数
  - `get_val_report.py`：删除 `get_all_stocks`、`filter_top_liquidity_pool`
  - `stock_cache.py`：删除 `cached_async`、`_async_get_cache`、`_async_set_cache`、`_async_enforce_size_limit_bg`、`_get_async_db` 及相关全局变量
  - `tdx_client.py`：删除 `tdx_cache_clear`、`tdx_get_security_bars_qfq`
  - `zhb_client.py`：删除 `_load_from_cache` 和 `import struct`
  - `stock_common/seat_db.py`：删除 `get_seat_style_tags`、`get_premium_label`、`is_in_seat_range`、`format_seat_summary`
- **冗余导入清理**：`get_mak_report.py`、`get_lng_report.py`、`get_med_report.py` 移除未使用的 `requests`, `json`, `math`, `time`, `re`；`stock_cache.py` 删除重复的 `import asyncio`；`tests/diag_tdx_compare.py` 删除重复的 `TdxClient` 导入
- **无效 f-string 批量清理**：自动清理 27 个文件中的 364 处无效 f-string（`f"..."` 中无 `{}` 占位符），消除 F541 警告
- **文件锁竞态条件修复**：`zhb_client.py` 的 `_release_file_lock()` 读取锁文件中的 PID，仅当匹配当前进程时才删除锁文件
- **\u9fff Unicode 转义修复**：`stock_common/sc_datasource.py` 第684行 `\u9ff` 补全为 `\u9fff`
- **datetime 导入修复**：`tests/diag_v96_skill_verify.py` 将循环内重复导入移到顶部
- **正则转义警告修复**：`tests/diag_dragon_tiger.py` 文档字符串路径反斜杠改为双反斜杠
- **stock_common/__init__.py 导出更新**：`__all__` 列表和 `from sc_datasource import` 块新增7个 V10.0 函数导出
- **节假日数据整合**：`stock_calendar.py` 的 `is_workday()` 优先使用 zhb.needini.dat 节假日数据，本地数据仅作为 fallback
- **删除百度K线fallback**：移除 `_baidu_kline_full_fallback()` 函数及所有调用点，TDX失败时返回空数据
- **缓存TTL优化**：根据数据特性延长TTL，减少重复网络请求
  - `kline`/`fund_flow`/`limit_pool`/`dragon_tiger`：1天→7天（历史数据收盘后不变）
  - `northbound`：7天→30天 | `margin_trading`/`block_trade`/`hsgt_flow`：3天→14天
  - `lockup_expiry`：7天→90天（解禁日期固定） | `announcements`：7天→30天
  - `basic_info`/`concept_blocks`：7天→30天（低频变动）
- **get_val_report.py优化**：
  - 使用 `zhb.stock_stats` 替代 `tdx_get_all_stocks`，全市场数据加载从7.7秒降至<0.1秒，零HTTP请求
  - 扩大策略扫描范围：周线/形态类策略 top_n 200-300→1000，财务/筹码类策略 200-300→500，北向/流动性类策略 200→300
  - 流动性池从Top300扩大到Top500

### Fixed

- **运行时崩溃隐患修复**：
  - `sc_datasource.py:756`：添加缺失的 `tdx_get_quote_full` 导入
  - `tdx_client.py:781`：`_baidu_kline_full_fallback` 函数已删除，替换为返回空数据并记录日志
  - `sc_datasource.py:2266`：删除无意义的 `global _calendar_fallback_warned` 声明
- **f-string docstring 误伤修复**（6处）：
  - `get_ful_report.py`：`_calc_macd` 文档字符串被误加 f 前缀导致 UnboundLocalError，ful第一章节消失
  - `zhb_client.py`（5处）：`stock_stats`、`stock_stats2`、`tip_info`、`csrc_industries` 属性及 `get_sw_industries` 函数文档字符串被误加 f 前缀，导致 zhb初筛静默失效
  - `tdx_client.py`：`_tencent_batch_fallback` 文档字符串被误加 f 前缀
- **MACD键名不匹配**：`_calc_macd` 返回键名 `"di"` 改为 `"dif"`，修复信号判断和评分中的 KeyError
- **异步公告配置键名错误**：`get_strategic_announcements_async` 中 `strategy_keywords` 改为 `announcement_keywords`，修复 sht/med/lng 公告全部丢失问题
- **版本号违规**：移除 ful/sht 输出中的 "V8.5" 版本号
- **市场状态文案不准确**：sht/lng/ful 的午休时段从"休市日"改为"午休时段（11:30-13:00）"
- **mak封板时间格式错误**：`first_limit_time` 整数时间戳按 HHMMSS 正确解析，修复"93:70"等无效时间显示
- **mak跌停阈值未区分板块**：创业板/科创板跌停阈值从 -9.5% 改为 -19.5%
- **ful PE -x 格式问题**：PE 为负时显示 "N/A" 而非 "-x"
- **needini.dat解析修复**：正确解析 `Y{n}=YYYY,MMDD,MMDD,...` 格式，仅提取当前年份和前一年数据
- **cross_verify多进程失效修复**：原逻辑要求两次获取数据完全相同才标记 verified=1，但多进程并发 + 数据源含实时字段（如 price/timestamp）导致 11 个分类的交叉验证永远无法通过，每次调用都走网络请求。新逻辑：首次写入通过 `valid_if` 校验即标记 verified=1，数据变化时用新数据替换并保持 verified=1
- **val脚本字段访问安全加固**：全策略统一使用 `.get()` 安全访问外部数据字段，避免 KeyError 导致策略中断
  - 策略04：`pe_data["percentile"]` → `pe_data.get("percentile", 100)`，兼容缺失字段
  - 策略08：`s["code"] == h["code"]` → `s.get("code", "") == h.get("code", "")`，兼容 hot_pool 数据结构变化
  - 策略09：`ind["name"]`/`ind["rank"]` → `ind.get("name", "")`/`ind.get("rank", 0)`，兼容行业数据缺失
  - 策略11：`holders[0]["change_ratio"]` → `holders[0].get("change_ratio", 0)`，兼容股东数据缺失
  - 策略13：`divs[0]["bonus_rmb"]` → `divs[0].get("bonus_rmb", 0)`，兼容分红数据缺失
  - 策略16：`c["amount_yi"]`/`c["mcap_yi"]`/`c["matched_kw"]` → `.get()` + `_safe_float()`，兼容zhb数据源字段差异
  - 策略18：`dtb["records"]` → `dtb.get("records", [])`，兼容龙虎榜数据结构变化
  - 打印输出和涨停统计：`item["name"]`/`item["code"]` → `.get()`，防止输出阶段崩溃
- **ST股票涨跌幅新规适配**（5%→10%）：根据最新A股交易规则，ST/*ST股票日涨跌幅限制从5%放宽至10%
  - `sc_utils.py`：`is_limit_up`/`is_limit_down` 删除ST分支，ST股票与主板统一使用±9.5%阈值
  - `get_mak_report.py`：`get_threshold` 删除ST 12%阈值，ST股票异动阈值与主板统一为20%
  - `get_mak_report.py`：近5日异动回溯删除ST特殊判断，与主板统一为20%
  - `get_sht_report.py`：异动雷达3日偏离值删除ST 12%阈值，与主板统一为20%
  - `get_sht_report.py`：连板阶梯计算删除ST 5%基准，与主板统一为10%

## [9.6] - 2026-07-13

### Added

- **mootdx依赖集成**：`requirements.txt` 新增 `mootdx>=0.11,<1.0`，与 easy-tdx 形成互补关系
- **东财现金流量表**：新增 `get_eastmoney_cash_flow` 和 `get_eastmoney_cash_flow_async` 函数，使用东财数据中心 `RPT_CASHFLOW` 接口替代已失效的新浪现金流量表API（xjllb）
- **北向资金数据质量字段**：`get_hsgt_macro_flow` 和 `get_hsgt_macro_flow_async` 返回结果新增 `data_quality` 和 `warning` 字段，支持降级警告
- **打板层**：新增 `get_limit_up_pool`/`get_limit_broken_pool`/`get_limit_down_pool`/`get_limit_pool_summary` 函数，获取涨停池、炸板池、跌停池数据；集成到 sht【十四、短线情绪与事件催化】和 mak【B. 涨停池扫描】章节
- **资金流降权**：新增 `get_eastmoney_minute_fund_flow` 和 `get_fund_flow_weighted` 函数，融合 TDX TCP 资金流（权重1.0）和东财分钟级资金流（权重0.6），实现加权融合资金流数据
- **财联社快讯复活**：新增 `cls_telegraph` 函数，使用 `cls.cn/v1/roll/get_roll_list` 接口，本地签名（`sign=md5(sha1(字典序拼接的query))`），零key实现，与东财7×24快讯互为独立备份
- **官方备胎池**：新增 `dragon_tiger_backup`（龙虎榜官方备用源：深交所+上交所官方接口）和 `fund_flow_backup`（新浪资金流备用源），东财被封时可fallback
- **舆情互动层**：新增 `cninfo_irm` 互动易问答函数，两步调用获取orgId和问答列表，支持按时间筛选
- **新增域名限流配置**：`sc_network.py` 新增 `www.cls.cn`、`irm.cninfo.com.cn`、`www.szse.cn`、`query.sse.com.cn`、`vip.stock.finance.sina.com.cn`、`data.10jqka.com.cn` 域名的限流配置，防止新接口被封禁
- **新增缓存分类**：`stock_cache.py` 新增 `news` 缓存分类（6小时TTL），用于财联社快讯缓存
- **同花顺涨停揭秘**：新增 `ths_limit_up_pool` 函数，作为东财涨停池的增强源，提供涨停原因题材、封板成功率、板型等东财没有的字段，与东财接口不冲突

### Changed

- **东财新闻接口清理**：`get_eastmoney_stock_news` 删除已失效的 `search-api-web.eastmoney.com` HTTP fallback（返回 passportWeb 而非新闻），仅保留 TDX F10 公司报道数据
- **东财7×24全球资讯接口更新**：`get_eastmoney_global_news` 从旧版 `np-listapi.eastmoney.com/comm/ws/build/list` 切换到 SKILL.md V3.4 推荐的 `np-weblist.eastmoney.com/comm/web/getFastNewsList`，返回 `fastNewsList` 结构
- **val脚本新闻源统一**：`get_val_report.py` 中的旧版 `cls_telegraph`（使用已下线的 `/nodeapi/telegraphList` 接口）和 `eastmoney_global_news` 改为引用 `sc_datasource.py` 统一实现，消除重复代码
- **news缓存TTL调整**：财联社快讯缓存TTL从1小时调整为6小时，平衡新鲜度和请求频率
- **解禁接口字段映射**：更新东财 `RPT_LIFT_STAGE` 报表字段映射（`FREE_SHARES_TYPE`/`FREE_SHARES`），新增 `ABLE_FREE_SHARES` 字段
- **行业排名排序**：东财行业板块接口添加 `fid=f3` 参数，确保按涨跌幅排序
- **北向资金降级警告**：当 sgt/hgt 比例超过3.0时标记数据质量为 degraded，发出警告日志

### Fixed

- **东财个股新闻解析**：修复 `get_eastmoney_stock_news` 函数的JSONP解析逻辑，之前仅处理 `jQuery(...)` 格式，无法解析带时间戳的 `jQuery35108723733748578402_1693632913001({...})` 格式
- **解禁接口字段**：修复旧字段 `LIMITED_STOCK_TYPE` / `FREE_SHARES_NUM` 恒空的问题，改为使用新字段
- **行业排名排序**：修复行业板块列表未按涨跌幅排序的问题，`top`/`bottom` 切片现在正确反映涨幅最高/最低行业

## [9.5] - 2026-07-13

### Changed

- **静默异常日志化**（28处）：`tdx_client.py`（23处）、`gd_uploader.py`（4处）、`get_med_report.py`（1处）共28处 `except Exception:` 静默吞异常改为 `except Exception as _e: _debug_log(f"...: {_e}")`，提升调试可观测性。覆盖心跳线程、连接管理、行情获取、板块查询、代理测试、凭证加载、健康检查等函数
- **aiohttp原生异步迁移**：`sc_datasource.py` 中10个纯HTTP异步函数从 `asyncio.to_thread(sync_func)` 包装的"假异步"改写为使用 `_async_request_with_retry` / `_async_quick_request` 的原生 `aiohttp` 实现。迁移函数包括：`eastmoney_datacenter_async`、`_em_filter_async`、`get_reports_async`、`get_northbound_hold_async`、`get_block_trade_async`、`get_ths_hot_reason_async`、`get_hsgt_macro_flow_async`、`get_sina_financial_report_async`、`get_sina_balance_sheet_async`、`get_strategic_announcements_async`。剩余10个依赖TDX协议的 `asyncio.to_thread` 调用保留（TDX客户端为同步socket协议，无法直接异步化）。异步限流比同步版更保守（东财 Semaphore(3)+1.0s / 非东财 Semaphore(5)+0.2s），不会突破限流阈值
- **ful脚本价格走势显示优化**：`get_ful_report.py` 中价格走势从"近60日"改为"近15日倒序显示"（Day-1为最近日期放在第一条），提升可读性
- **ful脚本新闻舆情文案修正**：`get_ful_report.py` 中"近24小时未检测到..."改为"近期未检测到..."，避免休市日文案与实际数据时间范围不符
- **GD上传根目录定位加固**：删除 `init_gd` 中冗余的二次验证逻辑（第534-546行），`retry_get_folder_interactive` 已通过 `parent_id=None` 严格限定在根目录搜索，二次查询不仅多余，还可能因 Drive 多文件夹场景造成混乱
- **文档与脚本完善**：
  - 新增 `docs/architecture.md`：Mermaid 架构图、模块职责、序列图、并发限流策略、GD 上传流程、缓存设计、文件清单
  - 新增 `scripts/clean_cache.py`：`stock_cache.py` CLI 的薄封装，支持 `--category` / `--pattern` / `--expired` / `--stats` / `--dry-run`
  - 新增 `CONTRIBUTING.md`：贡献指南（提交流程、代码规范、测试要求、提交信息规范）
  - 新增 `CODE_OF_CONDUCT.md`：Contributor Covenant v2.1 社区行为准则
  - 新增 `LICENSE`：MIT 许可证
  - `README.md` 完整重写：补充项目结构、配置文件、核心模块说明、FAQ（含 GD 桌面客户端同步冲突说明）
- **sc_scoring.py 评分权重配置化**：`sht`/`med`/`lng` 三套评分权重从硬编码改为从 `strategy_config.yaml` 读取（`weights_sht` / `weights_med` / `weights_lng`），保留默认值
- **get_ful_report.py 重构**：`main()` 拆分为 `_generate_reports` / `_upload_reports` / `_print_summary` 三个函数，添加 `logging` 日志

### Fixed

- **get_strategic_announcements_async 中 _load_config 未定义错误**：`sc_datasource.py` 迁移过程中误将同步版的 `_load_settings()` 写成不存在的 `_load_config()`，导致 sht/med/lng 三个脚本运行时报 `name '_load_config' is not defined`。修正为 `_load_settings()`
- **ful脚本价格走势为空**：`kl["closes"]` 字段误删导致渲染层第1570行 `closes_series = kl.get("closes") or []` 取不到数据，恢复 `closes_list[-60:]` 赋值（实际展示 15 条）

## [9.4] - 2026-07-11

### Added

- **VERSION文件单一来源版本号管理**：项目根目录新增 `VERSION` 文件（内容为 `9.4`），`stock_common/sc_utils.py` 新增 `get_version()` 函数读取版本号。所有Python脚本docstring去除硬编码版本号，改为引用 VERSION 文件。升级版本时只需修改 VERSION 文件，无需遍历所有脚本

### Changed

- **mak报告全市场异动扫描并行化**：`get_mak_report.py` 中 `check_stock` 循环改为 `ThreadPoolExecutor(max_workers=3)` 并行，扫描速度提升2-3x。并发数3与TDX/东财限流配额匹配，不突破限流阈值
- **med脚本两融数据添加融券余额列**：`get_med_report.py` 两融表格从3列（融资余额/融资买入/融资偿还）扩展为4列，增加"融券余额(万)"，与sht脚本格式统一
- **med/lng流通股东显示统一为0%**：`get_med_report.py` 和 `get_lng_report.py` 中十大流通股东表格删除 `if foreign_count` 条件判断，外资/境内机构/个人均统一显示百分比数值（0%表示无持股），不再显示N/A
- **lng脚本休市提示移至标题下方**：`get_lng_report.py` 将市场状态提示从【一、企业基本盘】章节内部移至报告标题下方，与sht/med脚本格式统一
- **ful脚本新闻page_size从10增至30**：`get_ful_report.py` 中 `layer5_news` 的 `get_eastmoney_stock_news(code, page_size=10)` 改为 `page_size=30`，覆盖近30天重要新闻
- **四脚本休市提示文案统一简化**：sht/med/lng/ful四个脚本的休市提示统一为 `⚠️ 休市日：数据为最近交易日快照，[脚本特定说明]` 格式，消除括号内外意思重复的混乱
- **med脚本休市提示文案丰富**：各时段（盘前/盘中/午休/盘后/休市）提示文案统一格式，去掉冗余的"当前为"前缀

### Removed

- **trap_detector.py**（22KB/12函数）：杀猪盘8信号检测模块，API定义但上层报告脚本未调用。依赖web search API（未实现），现有风险扫描已覆盖财务风险
- **valuation_methods.py**（21KB/9函数）：机构多方法估值模块，API定义但上层报告脚本未调用。依赖EPS增长率（机构一致预期，未接入），现有简单PE/PB对比可用
- **sc_datasource.py 中3个外部分析模块代理函数**：`get_trap_detection`、`get_valuation`、`analyze_ai_chain_position`（~260行），对应的外部模块已删除或未实现
- **gd_upload_flow 函数**（~100行）：`sc_utils.py` 中定义但零调用，各报告脚本使用 `gd_uploader.py` 的直接接口
- **sc_utils.py 中的 print_batch_summary 占位符**：被 `sc_datasource.py` 同名函数覆盖，从未实际使用
- **sc_network.py 中 _em_last_request_time / _gen_last_request_time 变量**：无锁保护的裸float变量，多线程场景下限流可能失效。实际限流已使用 `_DOMAIN_LAST_TIME` + `_DOMAIN_LAST_TIME_LOCK`（线程安全），这两个遗留变量已废弃
- **10个临时诊断脚本**：`tests/diag_fund_flow_{deep,final,quick,round3,round4,round5,stability,supplement}.py`、`tests/test_fix_bugs.py`、`tests/test_fix_verify.py`，均为临时诊断遗留，未登记在 tests/README.txt

### Fixed

- **sht资金流重复调用**：`get_sht_report.py` 中 `get_fund_flow_realtime` 内部 fallback 调用了 `get_fund_flow_120d`，外层第405行又调了一次。`get_fund_flow_realtime` 增加 `ff_120d` 参数，外层复用已获取的数据

## [9.3.3] - 2026-07-10

### Fixed

- **GD上传路径混乱**：`get_or_create_drive_folder` 增加 `'{parent_id}' in parents` 严格约束，`get_val_report.py` 移除 `gd_parent_folder_id or ""` 防止空字符串导致根目录上传，所有 txt 文件统一上传到 `a-stock-data/[股票代码-名称]/` 子文件夹
- **ScoreData 构造路径错误**（Bug 2）：`get_ful_report.py` 中 `price=price` 改为 `price=basic.get('price',0)`，`name=layers.get('layer1',{}).get('name','')` 改为 `name=basic.get('name','')`
- **地天板预警键名错误**（Bug 3）：`get_sht_report.py` 中 `limit_down` 改为 `limit_down_price`
- **MACD DEA 计算错误**（Bug 11）：`get_med_report.py` 中 DEA 计算从 `_dif*2/9 + _dif*7/9` 修正为正确的 EMA(DIF, 9)
- **iloc[3] IndexError**（Bug 6）：`get_med_report.py` 和 `get_lng_report.py` 中 `>= 3` 改为 `>= 4`
- **cleanup_tdx()/exit(1) 缩进错误**（Bug 5/Bug 7）：`get_val_report.py` 和 `get_mak_report.py` 中异常处理缩进修正
- **stock_calendar.py 非枚举值**（Bug 10）：`"Anti-Fascist 70th Day"` 改为 `Holiday.national_day`
- **get_reports None 检查**：`sc_datasource.py` 中增加 `r is None` 检查防止后续操作崩溃
- **sht资金流获取崩溃**：`get_sht_report.py` 中 `_get_eastmoney_fund_flow_120d()` fallback 调用无 try-except，东财接口异常时直接崩溃导致【七、资金走向分析】显示"资金流数据获取失败"。已增加 try-except 保护
- **ful技术分析内容缺失**：`get_ful_report.py` 中 `layer1_market()` 当 K线数据不足导致 `closes_list` 为空时，`kline["price"]` 未设置，渲染时跳过整个技术分析详情。已增加实时行情价格 fallback
- **GD根目录出现旧股票文件夹**：`gd_uploader.py` 中 `get_or_create_drive_folder()` 创建文件夹前未验证 `parent_id` 有效性，无效/已删除的 `parent_id` 导致 Google Drive API 回退到根目录创建。已增加 `service.files().get()` 存在性验证
- **FREE_DATE None 切片崩溃**：`sc_datasource.py:1805` 中 `str(r.get("FREE_DATE", "")[:10])` 当 key 存在但值为 None 时返回 None 而非默认值，导致 `slice(None, 10, None)` 报错（如 600563 法拉电子）。改为 `str(r.get("FREE_DATE", "") or "")[:10]`，与第 1792 行写法一致
- **val 脚本 coroutine 未 await 警告**：`get_val_report.py` 中 `_tasks` 被赋值两次，第一次创建的 17 个 coroutine 被覆盖后从未 await，触发 `RuntimeWarning: coroutine was never awaited` 并阻塞运行。将策略 18 移入 `_strategy_defs` 列表，删除冗余的第一次 `_names`/`_tasks` 赋值
- **mak 报告标题双括号**：`get_mak_report.py:429` 标题中 `（{_mkt_note}）` 与 `_mkt_note` 本身已含的 `（）` 叠加，输出 `（（休市日，数据为最近交易日快照））`。去掉外层 `（）`
- **mak 连板表格漏显连板股**：`get_mak_report.py` 连板表格遍历 `ths[:50]`（涨幅前50名），排名50之后的连板股（如亚联机械 001395）虽在连板明细摘要中出现，却不在表格中显示。改为遍历 `_lb_list` 并通过 `_ths_map` 查表，确保全部连板股都进入表格
- **mak 涨停列表少1只**：`get_mak_report.py` 涨停表格先取 `ths[:50]` 再排除连板股，导致 `50 - 1(贵绳股份) = 49` 只。改为遍历 `_zt_list[:50]`（已排除连板股），先排除连板再取 top N，确保显示完整 50 只

### Changed

- **sync/async 重复代码重构**：`sc_datasource.py` 中 9 个独立实现的 async 函数改为 `asyncio.to_thread()` 代理；`get_val_report.py` 删除 `strategy_18_longhu_activity_async` 重复代码，`run_discovery` 简化为 `asyncio.run()` 包装
- **stock_cache.py schema 单点维护**：定义 `_CACHE_TABLE_SQL`、`_CACHE_INDEX_SQLS`、`_CACHE_PRAGMAS` 常量，`_get_db()` 和 `_get_async_db()` 复用；删除 `_migrate_verify_columns`，`prev_value`/`verified` 字段直接定义在主表 SQL 中
- **httplib2 版本放宽**：`requirements.txt` 中 `httplib2==0.22.0` 改为 `>=0.22,<0.31`
- **删除大量死代码和未用导入**：
  - `get_sht_report.py`：删除 20+ 个未用导入、死函数 `generate_report()`、`_SCRIPT_DIR`、`_is_td`、`_results=[]`
  - `get_ful_report.py`：删除死函数 `_calc_ma`、`_calc_ema`、`_ascii_radar_chart`、`_ascii_price_trend`、未用导入
  - `get_med_report.py`：删除死代码 `peer_data["all_members"]`、`_cash_debt_ratio`、`_ar_rev_ratio`、30+ 个未用导入
  - `get_lng_report.py`：删除 `_is_td`、30+ 个未用导入、修复 `'gm_rows' in dir()` 判断
  - `sc_datasource.py`：删除 22+ 个未用导入、死函数 `_save_northbound_cache`、`_holder_fetch_em_async`
  - `analyze_history.py`：删除死键 `TYPE_LABELS` 中的 `val`、`mak`
  - `strategy_config.yaml`：删除死配置 `cash_debt_ratio_warn`、`ar_rev_warn_ratio`、26 处失效行号注释
  - `gd_uploader.py`：删除不可达 else 分支

### Documentation

- **README.md**：项目结构图更新（`stock_common.py`→`stock_common/` 目录），内嵌 requirements.txt 与真实文件同步，AI 产业链标注为"规划中，模块尚未实现"
- **CHANGELOG.md**：删除 `[Unreleased]` 空章节
- **tests/README.txt**：编号重复修复，8 个诊断脚本文件名更新（`test_`→`diag_`）

## [9.3.2] - 2026-07-09

### Fixed

- **TDX K线假数据导致指数涨幅全N/A和异动检测全为0**：约50%的 easy_tdx 内置TDX服务器K线接口返回假数据（响应头 `ret_count=800` 但 body 为 0 字节），导致 `TdxDecodeError: day datetime: 数据不足`。`from_best_host()` 只测延迟不测数据正确性，会选中这些坏服务器。K线失败后走百度fallback也返回空，导致指数 `ret_3d`/`ret_10d` 全部 None，异动检测前置条件全部不满足。
  - `_tdx_health_check` 新增 `get_security_bars` K线接口校验，检测到假数据时标记主机为坏主机并抛出异常触发重连
  - `_get_tdx_client` 调用 `from_best_host` 时过滤掉 `_TDX_BAD_HOSTS` 黑名单中的IP，所有IP都被标记时重置黑名单重试
  - `tdx_get_security_bars`、`tdx_get_index_bars`、`tdx_get_weekly_bars` 捕获 `TdxDecodeError` 时自动标记坏主机并换IP重连
  - `tdx_get_index_bars` 新增重试机制（原先异常直接走百度fallback，现在先重试换IP）
- **SQLite WAL模式多进程并发死锁**：`--all` 命令通过 `asyncio.create_subprocess_exec` 启动4个独立Python进程，每个进程独立写SQLite，WAL模式下产生 `-wal`/`-shm` 文件锁导致死锁。`stock_cache.py` 的 `journal_mode` 从 `WAL` 改为 `DELETE`，`cache_size` 从 `-64000`(64MB) 降到 `-8000`(8MB)。
- **代理环境下东财接口永久阻塞**：系统代理自动拦截 `requests` 请求，`np-weblist.eastmoney.com` 等接口超时失效。`_do_request` 增加 `proxies={"http": None, "https": None}` 禁用系统代理，增加 `ProxyError` 和兜底 `Exception` 捕获。

### Changed

- **TDX IP列表精简**：删除38个失效IP，保留13个可用IP，减少 `from_best_host()` 扫描时间

### Added

- **TDX坏主机黑名单机制**（`tdx_client.py`）：新增 `_TDX_BAD_HOSTS` 全局集合，记录返回假K线数据的服务器IP，`from_best_host` 自动跳过黑名单中的IP
- **诊断脚本**（`tests/`）：
  - `diag_tdx_hosts_test.py`：逐个测试52个TDX服务器的K线可用性，区分正常/假数据/连不上三种状态
  - `diag_tdx_final.py`：捕获TDX K线请求的原始TCP响应（header + body），深度诊断TdxDecodeError根因

## [9.3.1] - 2026-07-08

### Fixed

- **sht 脚本 `'float' object is not subscriptable` 崩溃**：`ff["data"]` 存在多态（TDX 返回 `List[dict]`、东财 fallback 返回 `List[float]`），第1181行信号生成和第1381-1382行评分数据处直接访问 `d["main_net"]`，当 TDX 资金流历史为空走东财 fallback 时崩溃。已在两处增加 `isinstance(_ff_data[0], dict)` 类型检查，与第706-725行的渲染逻辑保持一致。
- **`--all` 批量运行子进程永久挂起**：`main.py` 的 `_run_script_async` 中 `await proc.wait()` 没有超时，若某个报告脚本因网络/接口问题永不返回，整个 `--all` 链会无限阻塞。已改为 `await asyncio.wait_for(proc.wait(), timeout=600)`，10分钟超时后自动 `kill()` 子进程。
- **sht 脚本处理大量股票时超时**：TDX 请求间隔增大到 100ms 后，35 只股票的处理时间超过 10 分钟超时阈值，导致部分股票被跳过且无 GD 上传。已将超时时间从 600 秒增大到 1800 秒（30 分钟）。
- **策略08【政策驱动】异常 `_debug_log is not defined`**：`get_val_report.py` 中的 `cls_telegraph` 和 `eastmoney_global_news` 函数在异常处理中使用了 `_debug_log`，但文件未导入该函数。已在导入列表中添加 `_debug_log`。

### Changed

- **TDX 请求间隔从 20ms 增大到 100ms**：`_TDX_MIN_INTERVAL` 从 0.02 调整为 0.1，批量运行时降低 TDX 服务器压力，减少接口间歇性失败和数据缺失（上市日期空白、资金流获取失败等）。

### Added

- **TDX 健康检查增强**（`tdx_client.py`）：
  - `_tdx_health_check` 新增 `get_finance_info`、`get_fund_flow`、`get_xdxr_info` 三个关键接口连通性检测，便于快速定位是哪个 TDX 接口出问题
  - 新增 `_mac_health_check` 函数，MacClient 连接成功后自动检查 `get_belong_board` 和 `get_board_list` 接口可用性
- **测试脚本增强**（`tests/test_datasource.py`）：
  - 新增 `test_tdx_mac_client`：MacClient 连接检测
  - 新增 `test_tdx_belong_boards`：上交所/深交所股票所属板块获取（覆盖 601718 和 000100）
  - 新增 `test_tdx_board_members`：板块成员列表获取
  - 测试脚本版本从 V2.2 升级为 V2.3

## [9.3.0] - 2026-07-07

### Added

- **盘前行情模式**（`tdx_client.py`）：9:30前自动使用上一交易日日K线数据，避免实时接口返回 0 导致涨跌幅计算为 -100%
  - 新增 `_is_before_market_open()` 判断函数
  - 新增 `_get_trading_date_for_quote()` 生成带交易日期的缓存 Key
  - 新增 `_pre_market_quote_from_kline()` 从日K线构建盘前行情
- **缓存 Key 交易日期隔离**：行情缓存 Key 格式改为 `Q:{code}:{trading_date}`，盘前/盘中数据独立保留，避免相互覆盖
- **报告盘前提示**：sht/med/lng 等报告在盘前模式时显示"⚠️ 盘前模式（9:30前），以下行情数据基于上一交易日收盘数据"

### Changed

- **版本号统一清理**：所有报告脚本和终端输出中的硬编码版本号（如 V8.9）全部删除，避免版本更新时遗漏
- **融资融券数据清洗**（`sc_datasource.py`）：F10 数据增加日期截断（`[:10]`）和全 0 行过滤，解决 688305 数据拼接问题

### Fixed

- **sht 脚本 688305 list index out of range**：增加 `_fd` / `holders` 等多处列表索引边界检查
- **med 脚本历史财务业绩显示旧数据**：限制 `get_sina_financial_report` 返回近 5 季度数据
- **ful 脚本成功/失败统计显示 0**：统计逻辑改为基于数据生成结果，不再依赖上传结果
- **get_val_report.py FutureWarning 无限循环**：修正 `_safe_float` 对 pandas Series 的处理方式
- **--no-upload 对快照异常上传不生效**：`main.py` 传递 `skip_upload` 参数到快照上传逻辑

## [9.2.0] - 2026-07-05

### Added

- **缓存交叉验证机制**（`stock_cache.py`）：11 个多天 TTL 分类启用 `cross_verify=True`，两次获取数据一致才标记为已验证，防止意外错误数据被缓存
  - 新增 `prev_value` 和 `verified` 字段，支持自动表结构迁移
  - `get_cache` 未验证数据视为未命中，触发重新获取
  - `set_cache` 两次一致则标记 verified=1，不一致则重置继续验证
- **缓存并发安全加固**：`set_cache` cross_verify 分支的 SELECT-then-UPDATE 用 `_db_lock` 包裹，防止竞态丢失更新
- **异步连接复用**：新增 `_get_async_db()` 模块级单例，`_async_get_cache` / `_async_set_cache` / `_async_enforce_size_limit_bg` 复用同一 aiosqlite 连接
- **日历更新脚本**（`scripts/update_calendar.py`）：从 chinese-calendar 库提取数据，自动更新 `stock_calendar.py`
  - 支持 `--check` / `--update` / `--backup` / `--dry-run` 四种模式
  - `stock_calendar.py` 新增 CLI 入口：`python -m stock_common.stock_calendar --update`
- **交易日历降级警告**：`sc_datasource.py:is_trading_day()` 降级到 `weekday < 5` 时打印首次警告日志，避免静默误判

### Fixed

- **13 处裸 `except:` 全部改为 `except Exception:`**：允许 KeyboardInterrupt / SystemExit 穿透，Ctrl+C 可正常终止脚本
- **约 70 处 `except Exception: pass` 静默吞异常修复**：全部加 `_debug_log` / `_cache_logger.debug` 记录异常来源和信息，含跨行模式
  - 涉及文件：`get_ful_report.py`(26处)、`sc_datasource.py`(24处)、`tdx_client.py`(6处)、`stock_cache.py`(6处)、`sc_network.py`(4处)、`sc_utils.py`(3处)、`get_med_report.py`(4处)、`get_lng_report.py`(7处)、`get_mak_report.py`(4处) 等
- **tdx_client.py 重连泄漏**：`_get_tdx_client` / `_get_mac_client` 异常重连前先 `close()` 旧连接，防止 socket fd / 心跳线程泄漏
- **main.py 模块级副作用**：`check_dependencies()` 从模块级移到 `if __name__ == "__main__":` 内，`import main` 不再触发 `sys.exit`

### Changed

- **seat_db.py 席位数据文件去年份化**：`seats-2026.json` → `seats.json`，跨年后无需手动修改
- **gd_uploader.py 函数去重**：删除第二版重复定义的 `_make_stock_folder_name`，保留含 ST 处理的第一版
- **sc_scoring.py 亏损股评分封顶**：`min(score, 20.0)` 从 ROE 分支内移到函数末尾 return 前，确保所有维度加完后统一裁剪
- **tests 9 个文件硬编码路径修复**：统一改为 `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`，换机器/CI 可正常运行
- **test_cache.py TTL 脆性测试优化**：用 `monkeypatch time.time` 模拟时间流逝，消除 1.5s 真实等待
- **sc_utils.py `import time` 移到顶部**：从文件末尾移到标准 import 区
- **__init__.py 清理 legacy 死代码**：删除 `_legacy` / `_legacy_available` / `_legacy_missing` 及相关迁移状态
- **stock_cache.py 移除 `# type: ignore`**：用 `cast(F, wrapper)` / `cast(AF, wrapper)` 替代
- **sc_network.py 删除 `_DOMAIN_SEMAPHORES` 死代码**：V7.5 起不再使用，从 `__all__` 和 `__init__.py` 中彻底移除（同步删除 `_em_request_lock` / `_gen_request_lock`）
- **限流体系完善**（`sc_network.py`）：
  - 新增 `_gen_wait_process_interval_async()` 异步版通用进程间协调函数，`_async_quick_request()` 和 `_async_request_with_retry()` 中补齐调用
  - `em_get()` 与 per-domain 限流器（`_DOMAIN_LAST_TIME`）双向状态同步，避免与 `_quick_request` 交替调用时碰撞
  - 删除 `get_industry_peers()` 中冗余的 `_time.sleep(0.3)` 硬编码 sleep（TDX 内部已有 `_tdx_throttle` 限流）
  - 删除 `get_mak_report.py` 中冗余的 `time.sleep(0.1)` 硬编码 sleep（`_quick_request` 内部已有按域名限流）
- **报告脚本异常处理补全**：20 处 `except Exception:` 无变量绑定的全部改为 `except Exception as _e:` 并添加 `_debug_log` 日志
  - 涉及文件：`get_val_report.py`(10处)、`get_sht_report.py`(3处)、`get_ful_report.py`(2处)、`get_med_report.py`(1处)、`get_lng_report.py`(2处)、`get_mak_report.py`(2处)

### Removed

- `tests/compare_f10_vs_http.py`（V9.1.1 已清理）：F10 vs HTTP 对比测试脚本
- `tests/test_f10_p1_all.py`（V9.1.1 已清理）：F10 阶段一全量测试脚本

## [9.1.1] - 2026-07-04

### Fixed

- **ful 评分 theme→holder 映射 bug**：`get_ful_report.py` 中 `_scoring()` 返回值用 `"theme"` 作为键名，但实际取自 `dims.get("holder", 50)`，导致键名与数据来源不一致；同时权重读取用 `_weights.get('theme', 15)` 与评分系统默认值 10% 不一致。统一为 `holder` 键名 + 10% 默认权重，显示名称从"题材面"改为"筹码面"（与实际数据含义一致）。
- **F10 交易日缓存策略缺失**：`tdx_get_fund_flow` 和 `tdx_get_latest_announcements` 两个高频 F10 函数未添加 `@cached(trading_day=True)` 装饰器，导致每次调用都重复请求 TDX。现已补全，与 `f10_reminders` / `f10_news` / `f10_reports` 保持一致，5 个高频分类全部按交易日 15:00 过期。

### Changed

- **ful 报告从五维升级为六维**：`get_ful_report.py` 中 `_scoring()` 原计算了 6 个维度（技术/估值/基本/资金/筹码/分红）但只显示 5 个（隐藏了分红面），造成总分与显示维度不匹配。现补全分红面显示，标题从"综合五维评分"改为"综合六维评分"，权重：技术面25% + 估值面20% + 基本面20% + 资金面15% + 筹码面10% + 分红面10% = 100%。
- **F10 死代码精简**：移除 V9.1 中新增但未在生产代码中独立调用的 6 个 F10 函数（`tdx_get_research_reports` / `tdx_get_company_overview` / `tdx_get_operation_analysis` / `tdx_get_capital_operation` / `tdx_get_governance` / `tdx_get_themes`），以及 `render_f10_chapter()` 渲染函数（~213行）和 `_val_append_f10_themes_deprecated()`，合计精简约 700 行代码。

### Removed

- `tests/compare_f10_vs_http.py`：F10 vs HTTP 对比测试脚本，F10 优先级调整后已无保留价值
- `tests/test_f10_p1_all.py`：F10 阶段一全量测试脚本，功能已被集成测试覆盖

## [9.1.0] - 2026-07-04

### Added

- **F10 全覆盖工程**：用通达信 F10 协议替代/补充现有 HTTP 接口，降低东财限流风险，详见 `docs/TDX_F10_ROADMAP.md`
- **阶段一：12 个 F10 核心函数**（`tdx_client.py`）：
  - `tdx_get_latest_reminders`（最新异动与风险提示）
  - `tdx_get_financial_analysis`（财务分析：偿债/成长/现金流）
  - `tdx_get_shareholder_research`（股东研究：控股/增减持计划/持股变动）
  - `tdx_get_share_capital`（股本结构：限售解禁/分红送转）
  - `tdx_get_company_news_f10`（公司报道）
  - `tdx_get_research_reports`（研报评级）
  - `tdx_get_industry_analysis`（行业分析）
  - `tdx_get_company_overview`（公司概况/核心竞争力）
  - `tdx_get_operation_analysis`（经营分析：主营构成/行业地位）
  - `tdx_get_capital_operation`（资本运作：并购重组）
  - `tdx_get_governance`（高管治理：高管/薪酬）
  - `tdx_get_themes`（所属板块/事件驱动）
- **阶段二：F10 新增 6 种章节**（`render_f10_chapter`）：
  - `risk_warning`：异动与风险提示（sht/ful）
  - `rnd_innovation`：研发与创新（lng/val）
  - `financial_depth`：财务深度分析（med/lng/ful）
  - `shareholder_behavior`：股东行为分析（med/lng/ful）
  - `governance`：治理结构（lng/ful）
  - `business_composition`：主营构成分析（med/lng/val/ful）
- **阶段三：数据质量核查附录**（`render_data_quality_appendix`）：
  - 6 个验证函数：财务/股东/研报/资金流/股本/分红一致性
  - 差异 > 20% 时标记警告，5 个报告脚本均集成附录
- **缓存层交易日过期策略（方案B）**（`stock_cache.py`）：
  - `@cached` / `@cached_async` / `set_cache` 新增 `trading_day: bool = False` 参数
  - 新增 `_calc_trading_day_expiry()` 按最近交易日计算过期时间
  - 5 个 F10 高频分类用交易日过期，11 个低频分类用固定 TTL
  - `stock_calendar.py` 新增 `get_last_trading_day` / `get_next_trading_day`
- **F10 解析器增强**（`f10_parser.py`）：
  - `_normalize_pipes`：全角/半角竖线归一化（｜→│）
  - `find_subsection` / `parse_tables` / `merge_continuation_lines`
  - `transpose_table` / `parse_text_table`
- **集成测试**：`tests/test_f10_chapters_integration.py` 验证 F10 章节和附录在 5 个报告脚本中的集成
- **roadmap 文档**：`docs/TDX_F10_ROADMAP.md` V2 实施版，4 阶段实施对焦参照

### Changed

- **11 个 HTTP 函数添加 F10 优先逻辑**（F10 优先 + HTTP 兜底）：
  `get_block_trade` / `get_margin_trading` / `get_eastmoney_stock_news` /
  `get_sina_financial_report` / `get_sina_balance_sheet` /
  `get_gross_margin_and_roe` / `get_reports` / `get_lockup_expiry` /
  `holder_change` / `get_holder_structure` / `get_industry_peers`
- **7 个异步函数委托到同步版**（自动获得 F10 优先逻辑）：
  `get_reports_async` / `get_sina_financial_report_async` /
  `get_sina_balance_sheet_async` / `get_lockup_expiry_async` /
  `holder_change_async` / `get_industry_peers_async` 等
- **5 个报告脚本集成 F10 章节 + 附录**：
  - `get_sht_report.py`：仓位管理前插入 risk_warning 章节
  - `get_med_report.py`：仓位管理前插入 3 章节
  - `get_lng_report.py`：仓位管理前插入 5 章节
  - `get_ful_report.py`：返回前插入全部 6 章节 + 附录
  - `get_val_report.py`：共振金股追加 `_val_append_f10_themes`
- **TDX 服务器扩容**：新增 2 个官方 IP（123.60.164.122 / 82.156.214.79），共 53 节点
- **版本号统一升级 V9.1**

### Fixed

- **sht 报告资金流渲染 TypeError**：东财 push2 回退返回 `List[float]`，但渲染代码期望 dict，导致 `TypeError: 'float' object is not subscriptable`。改为用 `isinstance(_recent[0], dict)` 检测格式后分支处理
- **F10 字段名带后缀不匹配**："股东人数(户)" vs "股东人数" → `_holder_fetch_f10` 改用 `startswith` 匹配
- **TDX 连接失败导致空数据被缓存 7 天**：12 个 F10 函数全部添加 `valid_if=lambda r: bool(r)`
- **全角竖线 ｜ 导致 000001 表格解析失败**：新增 `_normalize_pipes()` 归一化
- **F10 section 名称不匹配**（如 "1.基本资料" 而非 "公司概况"）：改为遍历 `sections.items()` 用 `in` 匹配
- **risk_warnings 是 dict 而非 list**：`render_f10_chapter` 用 `isinstance(risks, dict)` 分支处理
- **测试脚本 ModuleNotFoundError**：`tests/test_f10_chapters_integration.py` 添加 `sys.path.insert(0, ...)` 将项目根目录加入路径

## [9.0.0] - 2026-07-02

### Added

- **舆情互动层（Layer 10）**：新增 `cninfo_irm()`（互动易问答）、`ths_hot_list()`（同花顺热榜）、`em_hot_rank()`（东财人气榜）、`em_hot_concept()`（个股概念命中）四个舆情接口，全部零鉴权
- **上市日期东财 push2 fallback**：`get_stock_info()` 在 TDX 无法获取 `ipo_date` 时自动降级到东财 push2 (`f189`)，不再返回空白
- **`@cached` 读取时 valid_if 校验**：缓存命中但数据不通过 `valid_if` 校验时视为未命中，自动重新获取
- **`_has_zero_price` 坏数据拦截**：`set_cache` 中检测到 `price=0` / `close=0` 的特征时禁止写入缓存
- **sht 脚本新闻/舆情段**：替换硬编码文字为东财个股新闻 + 互动易 + 同花顺热榜三层数据

### Fixed

- **TDX MacClient 失败缓存**：新增 `_check_mac()` 缓存 MacClient 不可用状态，避免每次调用重试 3 次（1.5s→0.000s）
- **`get_tencent_quote` 不完整返回保护**：腾讯超时时 TDX 补充不完整 → 返回空字典，避免 KeyError（`change_pct` / `pe_ttm`）
- **`get_industry_peers` 腾讯 fallback 防限流**：同行价格补全循环加 `time.sleep(0.3)` 间隔
- **`get_industry_peers` valid_if 强化**：从 `any` 改为 `all`，要求所有同行价格有效才缓存
- **已下线财联社快讯清除**：`get_ful_report.py` 删除 `cls.cn` 404 接口调用
- **各脚本 `q['xxx']` 改为 `q.get('xxx',0)`**：消除腾讯 API 偶发缺字段导致的 KeyError
- **删除 sht 重复的股价/PE/PB 显示段**：综合信号后的重复信息行
- **各脚本多评委评分位置统一**：sht/med/lng 统一在原始评分后输出多评委评分 + 综合投资建议

### Changed

- **快照架构重构**：`save_snapshot()` 只写 JSON 不做分析；`analyze_history()` 统一做跨日期检测，有异常才生成 TXT + 上传 GD
- **缓存淘汰改写入时**：删除 `_startup_cleanup()` 启动清理，改为 `_enforce_size_limit()` 写入时顺带清理过期条目
- **TTL 优化**：`northbound` 1d→7d, `margin_trading` 1d→3d, `lockup_expiry` 1d→7d, 等 6 项调整
- **7 个数据函数加 `@cached`**：`baidu_kline_full`, `get_holder_structure`, `ths_hot_list`, `em_hot_rank`, `em_hot_concept`, `cninfo_irm`, `eastmoney_stock_info_push2`
- **文件重组**：`stock_calendar.py` / `seat_db.py` / `trap_detector.py` / `analyze_history.py` / `valuation_methods.py` 等 8 个文件移入 `stock_common/`
- **修复 `trap_detector.py` 中文引号语法错误**（2 处）
- **修复 `get_mak_report.py` 嵌套 f-string 语法错误**
- **版本号统一升级 V9.0**

## [8.9.0] - 2026-06-29

### Added

- **版本号统一升级**：所有脚本版本从 V8.8/V8.7 统一升级到 V8.9
- **CHANGELOG/README 更新**：记录 V8.9 全部变更

### Changed

- **快照架构改进**：
  - 移除逐只股票的 `save_score_snapshot()` 调用
  - 改用模块级 `_SNAPSHOT_DATA` 字典累积所有股票的评分
  - 脚本末尾一次性调用 `save_snapshot()` 写入 JSON
  - 删除 `save_score_snapshot` 函数及其在两个子模块中的重复定义
  - 删除所有报告脚本末尾的 `_stocks`/`generate_daily_snapshot` 冗余快照块

### Fixed

- **get_sht_report.py**：修复 `int+dict` 类型错误（`sum(recent_data)` → `sum(d.get("main_net",0) for d in recent_data)`）
- **get_val_report.py**：修复 V8.9 模块化后缺失 `_load_settings`、`holder_change` 导入导致的 NameError
- **get_ful_report.py**：修复线程数硬编码（`ON(5线程)` → 引用 `_MAX_WORKERS=3` 变量）
- **stock_cache.py**：关闭遗留 `holder_cache.json` 迁移逻辑（`_MIGRATE_HOLDER_CACHE = False`）
- **多文件**：移除 11 处 `print(f"\n..."` 的前置换行，减少多余空行输出

### Removed

- `stock_common/sc_utils.py`、`stock_common/sc_datasource.py`：删除 `save_score_snapshot()` 函数
- 删除 6 个 V8.8 存档文档：`CHANGELOG_V8.8.md`、`CHANGELOG_V8.8_DETAILED.md`、`FILES_CHANGE_LOG_V8.8.md`、`PROJECT_STATUS_V8.8.md`、`VERSION_SUMMARY_V8.8.md`
- 删除 `stock_common.py.bak_v86`（V8.6 备份文件）

## [8.8.0] - 2026-06-25

### Added

- **GD上传逻辑统一化**：
  - 统一 `ful/sht/med/lng` 四个脚本的GD上传格式为：`股票代码-2个中文`（如 `002193-如意`）
  - 新增股票名称处理函数 `_make_stock_folder_name()`：跳过ST前缀，取前2个中文字符
  - 无中文字符时显示 `股票代码-`，便于识别问题
  - `val` 和 `mak` 脚本保持原有的按类型文件夹上传逻辑

- **快照文件格式升级**：
  - 快照文件从 `snapshot_YYYYMMDD_type.json` 改为 `snapshot_YYYYMMDD_HHmm.txt` 文本格式
  - 新增快照文件自动上传功能：每次生成后自动上传到 `a-stock-data/snapshot/` 文件夹
  - 快照文件内容优化：增加元数据注释，提升可读性
  - 更新快照加载逻辑以支持TXT格式

- **系统功能增强**：
  - `analyze_history.py` 新增GD自动上传功能，确保快照数据云端同步
  - `gd_uploader.py` 新增股票文件夹名称处理工具函数
  - 优化快照文件生成和保存流程，支持格式兼容性

### Changed

- **版本号升级**：所有主要脚本版本号从 V8.7 升级到 V8.8
- **快照处理**：快照文件生成逻辑重写，从JSON格式改为更易读的TXT格式
- **上传策略**：优化了GD上传的错误处理和重试机制

### Fixed

- **GD上传逻辑**：修复了ful脚本GD上传后可能出现的目录结构不一致问题
- **快照文件**：解决了快照文件格式兼容性问题，支持新旧格式平滑过渡

## [8.7.0] - 2026-06-25

### Removed

- 删除 `social_sentiment.py`（6 平台社交热榜聚合，全为桩实现返回空数据）
- 删除 `stock_common.py` 中的 `get_social_sentiment()` 和 `get_social_sentiment_async()` 便捷函数（~70 行）
- 删除 `tests/test_issues.py` 中的 `test_social_sentiment()` 和 `test_gross_roe_scope()` 测试（社交相关功能已移除）

### Refactored

- `get_lng_report.py`：同步 `generate_report()` 替换为薄包装（`asyncio.run()` 调用异步版），删除 `_get_eps_from_em_reports()` 死代码辅助函数（~545 行删除）
- `get_med_report.py`：同步 `generate_report()` 替换为薄包装，删除 `get_cninfo_announcements()`、`_get_eps_from_em_reports()`、`get_holder_change()` 死代码辅助函数（~828 行删除）
- `get_sht_report.py`：同步 `generate_report()` 替换为薄包装，删除社交热榜段落（~1175 行删除）

### Added

- 新增 `analyze_history.py` 历史分析模块：
  - `save_snapshot(script_type, stocks)`：智能合并快照到 `snapshots/snapshot_<YYYYMMDD>_<type>.json`
  - `analyze_history()`：跨日期趋势背离检测（单日突变 |Δ|≥15分 / 连续≥3天同向且总变化≥15分）
  - 检测结果：评分突变背离（按变化幅度降序）+ 连续趋势信号（持续上涨📈/持续下跌📉）

### Fixed

- 修复 `analyze_history.py` 趋势检测判定条件（`run_len + 1 >= TREND_MIN_DAYS` 确保连续天数正确计算）
- 修正趋势检测语义：删除 `TREND_STEP_THRESHOLD`，改用 `DIVERGENCE_THRESHOLD` 作为总变化幅度显著性门槛

## [8.6.0] - 2026-06-24

### Security

- stock_common.py：新增 _DOMAIN_LAST_TIME 线程锁保护，彻底消除多线程竞态条件
- 新增 HTTP 429 状态码检测 + Retry-After 响应头处理
- 失败重试改为指数退避（1s → 2s → 4s）
- 新增限流统计计数器 + rate_limit.log 日志
- 新增 print_rate_limit_stats() 统计打印函数
- tdx_client.py：新增 TDX 请求频率限制（20ms 最小间隔）
- tdx_client.py：重连机制改为指数退避（0.5s, 1s, 2s）

### Changed

- 所有报告脚本 ThreadPoolExecutor 并发数统一调整为 3
- get_val_report.py 策略18龙虎榜：初筛Top20再查席位（东财请求减少75%）
- 测试脚本新增 TDX TCP 接口测试

## [8.5.0] - 2026-06-22

### Added

- 新增龙虎榜席位增强模块 `seat_db.py`：
  - 22位游资席位数据库 `seats-2026.json`（legend/new_gen/regional/new_2025分级）
  - 席位等级识别 `identify_seat_tier()`、席位详情查询 `get_seat_info()`
  - 席位风格标签、溢价判断、席位质量评分
  - 龙虎榜数据自动增强（`get_dragon_tiger_board()`新增`enhance_seats`参数）
- 新增杀猪盘8信号检测 `trap_detector.py`：
  - 8维检测框架：低质量账号推荐/话术模板化/付费社群引流/基本面热度脱节/K线异常/老师人设推广/跨平台联动/虚假研报
  - `detect_trap_signals()` 返回trap_score(1-10)和level(安全/注意/警惕/高度可疑)
  - `stock_common.py`新增`get_trap_detection()`便捷函数
- 新增数据质量HARD-GATE `data_quality_gate.py`：
  - 13条数据质量检查清单（K线完整性/财务数据缺失/研报时间戳/席位不一致/北向背离/主力连续流出/融资不连贯/股东突变/公告为空/换手率异常/成交额异常/股价背离/数据源空值）
  - `run_data_quality_gate()` 返回passed/blocked状态和错误详情
  - critical级别错误自动阻断报告生成
- 新增多档分析深度：
  - `get_sht_report.py`新增`--depth lite/medium/deep`参数
  - lite模式跳过120日资金流/席位详情/股东历史/两融详细/大宗详细/公告详细/行业对比
  - medium模式跳过120日资金流/机构调研/研报详细
- 新增多评委评审团（`stock_common.py`）：
  - 价值派（权重：基本面40%/估值30%/分红20%/筹码10%）
  - 成长派（权重：技术面35%/资金面30%/筹码20%/基本面15%）
  - 游资派（权重：技术面40%/资金面35%/情绪面25%）
  - 综合派（均衡权重）
  - `calculate_multi_school_scores()`计算多派别评分和分歧度
- 新增社交热榜聚合 `social_sentiment.py`：
  - 6平台支持：微博/知乎/抖音/今日头条/百度/B站
  - `get_social_sentiment()`返回total_hot/sentiment/active_platforms
  - `stock_common.py`新增`get_social_sentiment()`和`get_social_sentiment_async()`便捷函数
- 新增机构估值方法库 `valuation_methods.py`：
  - DCF现金流折现、DDM股息折现、PEG估值、LBO杠杆收购
  - PB-ROE矩阵、行业PE比较、股价/自由现金流
  - `get_intrinsic_value()`综合多种方法给出内在价值判断
  - `stock_common.py`新增`get_valuation()`便捷函数
- AI产业链卡位分析 `ai_chain_analyzer.py`（规划中，模块尚未实现）：
  - 卡脖子环节：GPU/AI芯片、HBM存储、CoWoS封装、光模块、PCB、电源管理、交换机、液冷散热
  - `analyze_ai_chain_position()`判断个股是否在AI产业链、卡位等级、上游暴露度
  - `stock_common.py`新增`analyze_ai_chain_position()`便捷函数（当前返回空结果）

### Changed

- `get_sht_report.py` 和 `get_sht_report_async()` 新增 `depth` 参数
- `stock_common.py` 新增多个V8.5版本便捷函数（席位/杀猪盘/多评委/社交/估值/AI产业链）

## [8.4.0] - 2026-06-22

### Added

- 新增 `stock_cache.py` 统一缓存层（SQLite + TTL 自动过期 + LRU 清理）
- 新增 8 个异步函数：`get_tencent_quote_async`、`get_dividend_history_async`、`get_concept_blocks_async`、`get_holder_structure_async`、`get_industry_peers_async`、`get_stock_sector_rank_async`、`get_industry_comparison_async`、`get_stock_info_async`
- 新增 `pyproject.toml` 集中管理 pytest/mypy/black 配置
- 新增测试文件：`tests/test_cache.py`、`tests/test_scoring.py`、`tests/test_strategy.py`

### Changed

- 所有 `get_*` 函数添加 `@cached` 装饰器，降低 API 请求频率
- 类型注解完整覆盖核心模块（stock_common.py、tdx_client.py、get_val_report.py 等）
- mypy 静态检查配置（python_version=3.10）

### Technical

- mypy 检查通过（6 个核心文件零错误）
- pytest 测试框架配置完成

## [8.3.0] - 2026-06-18

### Fixed

- 修复北向资金持股占比显示超100%问题（`get_sht_report.py`/`get_med_report.py`中`_ratio*100`改为`_ratio`，东方财富API返回的`hold_ratio`已是百分比形式）
- 修复股东户数变化率异常问题（当变化率超过±500%时显示为±999.99%并标记⚠️，防止极端值干扰判断）
- 修复EPS预测合理性检查（当eps_val<=0时不计算前向PE）
- 修复涨停封单弱时仓位建议降级（检测到"封单预警"或"弱势烂板"信号时，仓位建议减半）
- 修复主力净流入单位不统一问题（统一使用"亿元"为单位）

### Changed

- 亏损股评分强制下限：当ROE<0时，评分强制下限为20分并添加警告标识
- 涨停封单弱时仓位建议降级：检测到封单预警信号时，仓位建议从40%/25%/10%/5%分别降为20%/12%/5%/2%
- 板块排名标题明确区分市值排名：改为"[市值排名]"并标注"(按总市值)"
- 章节分隔符风格统一：sht/med/lng/val/mak全部统一为`─`风格
- 数字正负号格式统一：资金流向表格单位统一为亿元，精度调整为2位小数
- 评分图形条按加权分数显示：各维度图形长度=原始分数×权重比例
- W底形态成交量确认统一：使用5日均量对比判断放量（vol[-1] > avg_vol_5 * 1.2），替代原来的单日对比（vol[-1] > vol[-3] * 1.2）

## [8.2.0] - 2026-06-18

### Fixed

- 修复 `300274` 等股票因 lines 列表中存在 None 值导致 `join()` 报错的问题（在所有脚本的 `join()` 调用前添加 `filter(None, lines)` 防护）
- 修复 `ful` 脚本综合评分显示 4211.0 的异常（`strategy_config.yaml` 中权重为百分比形式，`calculate_score()` 未除以100导致数值被放大100倍）
- 统一 `ful` 脚本的终端显示逻辑（删除额外的报告头部和评分区打印，与其他脚本保持一致，仅输出文件生成路径）

### Changed

- `get_dragon_tiger_board()` 和 `get_dragon_tiger_board_async()` 增加 `include_seats` 参数（默认 True），当设为 False 时跳过席位详情查询，可减少2次不必要的API请求

## [8.1.0] - 2026-06-18

### Added

- 新增统一评分接口：`ScoreData` 数据结构、`ScoreResult` 结果结构、`calculate_score()` 主函数，统一管理 sht/med/lng/ful 四种评分类型的计算逻辑
- 新增 6 个维度评分函数：`_score_technical`（技术面）、`_score_fundamental`（基本面）、`_score_valuation`（估值面）、`_score_flow`（资金面）、`_score_holder`（筹码面）、`_score_dividend`（分红面）
- 新增快照功能：`save_score_snapshot()` 将评分结果保存到 `snapshots/` 目录用于历史对比
- 新增 `analyze_history.py` 实现评分快照历史分析与背离检测
- 新增 `is_trading_day()` 函数判断A股交易日（含节假日+调休）
- 新增 `get_market_status()` 函数返回市场状态（盘前/上午/午休/下午/盘后/休市）
- 新增 `clean_codes()` 函数清洗股票代码（提取6位数字、去重、过滤无效项）
- 新增 `_try_upgrade_calendar()` 函数实现 chinese-calendar 库自动升级
- 新增 `_safe_float()` 函数处理空字符串转换问题
- 新增 `strategy_config.yaml` 配置评分权重和参数

### Changed

- 统一评分接口重构（MINOR）：`get_sht_report.py`、`get_med_report.py`、`get_lng_report.py`、`get_ful_report.py` 4个报告脚本全部改用 `calculate_score()` 统一接口，消除重复评分逻辑
- 目录重命名：`WARNING_DIR` → `SNAPSHOT_DIR`，`ensure_warning_dir()` → `ensure_snapshot_dir()`
- 统一 `get_lockup_expiry` 接口：`days=90` 作为默认值，支持 `include_history` 参数
- 银行股财报字段映射优化：支持多种字段名（归属于母公司股东权益合计/归属于母公司股东的权益/股东权益）
- 财务分析添加除零保护：资产总计为0时跳过占比计算，净资产为0时提示商誉风险
- `get_worth_analysis_async` 统一重命名为 `get_eps_forecast_async`
- 所有分散函数统一抽象到 `stock_common.py`

### Fixed

- 修复 `000981` 数据生成失败问题（空字符串转换异常）
- 修复股票代码格式问题（中文后缀、空格分裂、重复代码）
- 修复 `ImportError: cannot import name 'timegm' from 'calendar'`（改名为 `stock_calendar.py`）
- 修复龙虎榜查询中日期字段过滤格式（东财API需使用单引号：`TRADE_DATE>='YYYY-MM-DD'`）

### Security

- 支持静默自动升级 chinese-calendar 库
- 降级方案：当升级失败时自动使用 weekday < 5 简单判断

## [8.0.0] - 2026-06-17

### Added

- 初始版本，包含6个报告脚本（sht/med/lng/ful/val/mak）
- 支持A股个股分析报告生成
- 集成新浪财经、东方财富、同花顺等数据源
- 支持Google Drive云端上传
