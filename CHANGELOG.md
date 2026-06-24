# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- 新增AI产业链卡位分析 `ai_chain_analyzer.py`：
  - 卡脖子环节：GPU/AI芯片、HBM存储、CoWoS封装、光模块、PCB、电源管理、交换机、液冷散热
  - `analyze_ai_chain_position()`判断个股是否在AI产业链、卡位等级、上游暴露度
  - `stock_common.py`新增`analyze_ai_chain_position()`便捷函数

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
