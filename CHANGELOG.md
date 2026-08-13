# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

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
