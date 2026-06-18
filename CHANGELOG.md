# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [8.1.0] - 2026-06-18

### Added

- 新增 `is_trading_day()` 函数判断A股交易日（含节假日+调休）
- 新增 `get_market_status()` 函数返回市场状态（盘前/上午/午休/下午/盘后/休市）
- 新增 `clean_codes()` 函数清洗股票代码（提取6位数字、去重、过滤无效项）
- 新增 `_try_upgrade_calendar()` 函数实现 chinese-calendar 库自动升级
- 新增 `_safe_float()` 函数处理空字符串转换问题

### Changed

- 统一 `get_lockup_expiry` 接口：`days=90` 作为默认值，支持 `include_history` 参数
- 银行股财报字段映射优化：支持多种字段名（归属于母公司股东权益合计/归属于母公司股东的权益/股东权益）
- 财务分析添加除零保护：资产总计为0时跳过占比计算，净资产为0时提示商誉风险
- `get_worth_analysis_async` 统一重命名为 `get_eps_forecast_async`
- 所有分散函数统一抽象到 `stock_common.py`

### Fixed

- 修复 `000981` 数据生成失败问题（空字符串转换异常）
- 修复股票代码格式问题（中文后缀、空格分裂、重复代码）
- 修复 `ImportError: cannot import name 'timegm' from 'calendar'`（改名为 `stock_calendar.py`）

### Security

- 支持静默自动升级 chinese-calendar 库
- 降级方案：当升级失败时自动使用 weekday < 5 简单判断

## [8.0.0] - 2026-06-17

### Added

- 初始版本，包含6个报告脚本（sht/med/lng/ful/val/mak）
- 支持A股个股分析报告生成
- 集成新浪财经、东方财富、同花顺等数据源
- 支持Google Drive云端上传
