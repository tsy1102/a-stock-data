# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
