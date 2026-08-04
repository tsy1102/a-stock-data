"""stock_common — 统一基础工具包

将原 stock_common.py (4300+行) 拆分为 5 个职责清晰的子模块：
  - sc_network:   网络层 / 限流 / Session 管理
  - sc_datasource: 数据源获取函数
  - sc_scoring:   评分系统（含统一多评委输出）
  - sc_utils:     工具函数 / 常量 / 配置
  - sc_schema:    V13.0 字段元数据层（FieldSpec + TimeAnchor/DataSource/Unit Enum + NormalizedQuote）

V13.0 新增 sc_schema.py 作为第 5 个子模块，提供：
  - 34 个核心字段的元数据表（FIELD_SPECS）
  - dataclass(slots=True, frozen=True) FieldSpec
  - 归一化边界函数 normalize_at_boundary() 骨架
  - test_sc_schema.py 23 个单元测试

向后兼容：所有原来通过 `from stock_common import xxx` 的接口
仍然可以正常工作，本包会自动 re-export 所有公共接口。

架构说明：
  当 stock_common/ 包目录存在时，Python 会优先导入包而不是
  同名的 stock_common.py 文件。因此本 __init__.py 必须重新
  导出原 stock_common.py 的所有公共接口。

  在完全迁移完成前，原 stock_common.py 的代码仍然作为数据源
  函数的 fallback 来源（通过 _legacy 模块加载）。
"""
from __future__ import annotations

import os

__all__ = [
    # sc_network
    "_LOG_DIR", "_http_logger", "_biz_logger", "_DEBUG", "_debug_log",
    "UA", "DATACENTER_URL", "JP_URL",
    "EM_SESSION", "EM_MIN_INTERVAL", "_EM_LAST_CALL",
    "_DOMAIN_LIMITS", "_DOMAIN_LAST_TIME", "_DOMAIN_LAST_TIME_LOCK", "_RL_STATS",
    "_em_lock_dir", "_em_lock_file", "_gen_lock_file",
    "_file_lock_acquire", "_file_lock_release",
    "em_get", "_em_wait_process_interval", "_gen_wait_process_interval",
    "_request_with_retry", "_quick_request", "_do_request",
    "_log_rate_limit", "print_rate_limit_stats", "_market_code",
    "_em_async_lock", "_gen_async_lock", "_em_async_last_request",
    "_gen_async_last_request", "_HAS_ASYNCIO", "_HAS_AIOHTTP",
    "_ensure_async_locks", "_em_wait_process_interval_async",
    "_gen_wait_process_interval_async", "create_async_session",
    "_async_request_with_retry", "_async_quick_request",
    # sc_scoring
    "ScoreData", "ScoreResult",
    "_score_technical", "_score_fundamental", "_score_valuation",
    "_score_flow", "_score_holder", "_score_dividend",
    "calculate_score", "calculate_score_by_school",
    "calculate_multi_school_scores", "format_multi_school_report",
    "SCHOOL_CONFIGS",
    # sc_technical (V16.1: 技术指标引擎，从 ful Layer1 迁移)
    "calc_macd", "calc_rsi", "calc_bollinger", "calc_kdj",
    "calc_volume_analysis", "calc_ma", "analyze_technical",
    # sc_risk (V16.1: 风险扫描引擎，从 ful layer_risk 迁移)
    "scan_financial_risk", "scan_event_risk", "combine_risk",
    # sc_utils
    "get_version",
    "_safe_float",
    "ensure_output_dir", "get_script_dir",
    "get_board_type", "is_limit_up", "is_limit_down",
    "clean_codes", "parse_args",
    "_safe_cleanup_tdx",
    "_load_settings", "_load_strategy_config",
    "_settings_cache", "_strategy_config_cache",
    # sc_datasource
    "eastmoney_datacenter", "_em_filter",
    "eastmoney_datacenter_async", "_em_filter_async",
    "holder_change", "holder_change_async",
    "_holder_fetch_from_sqlite", "_holder_update_sqlite",
    "_holder_fetch_em", "_holder_fetch_tdx",
    "_holder_fetch_tdx_optimized",
    "_compute_holder_changes",
    "_HOLDER_CACHE_TTL", "_HOLDER_CACHE_REFRESH",
    "get_strategic_announcements", "get_strategic_announcements_async",
    "_cninfo_get_orgid", "_CNINFO_ORGID_CACHE",
    "_holder_structure_cache",
    "get_holder_structure", "get_holder_structure_async",
    "get_tencent_quote", "get_tencent_quote_async",
    "baidu_kline_full", "get_stock_info", "get_stock_info_async",
    "get_reports", "get_reports_async",
    "get_industry_reports", "get_eps_forecast", "get_eps_forecast_async",
    "get_northbound_hold", "get_northbound_hold_async",
    "_northbound_cache_path", "_load_northbound_cache",
    "get_margin_trading", "get_margin_trading_async",
    "get_block_trade", "get_block_trade_async",
    "get_dividend_history", "get_dividend_history_async",
    "get_concept_blocks", "get_concept_blocks_async",
    "get_ths_hot_reason", "get_ths_hot_reason_async",
    "get_industry_peers", "get_industry_peers_async",
    "get_stock_sector_rank", "get_stock_sector_rank_async",
    "get_industry_comparison", "get_industry_comparison_async",
    "_get_eastmoney_industry_sectors",
    "get_eastmoney_stock_news", "get_eastmoney_global_news",
    "get_sina_financial_report", "get_sina_financial_report_async",
    "get_sina_balance_sheet", "get_sina_balance_sheet_async",
    "get_em_batch_quotes",
    # V12.0: 东财HTTP替代接口（完全移除easy_tdx）
    "get_em_board_list", "get_em_board_members", "get_em_belong_boards",
    "get_em_fund_flow", "get_em_history_fund_flow",
    "get_eastmoney_cash_flow", "get_eastmoney_cash_flow_async",
    "get_hsgt_macro_flow", "get_hsgt_macro_flow_async",
    "get_lockup_expiry", "get_lockup_expiry_async",
    "get_gross_margin_and_roe", "get_gross_margin_and_roe_async",
    "_try_upgrade_calendar",
    "get_valuation_pe_center", "is_trading_day", "get_market_status",
    "print_batch_summary",
    "get_dragon_tiger_board", "get_dragon_tiger_board_async",
    "get_recent_dragon_tiger", "get_recent_dragon_tiger_async",
    "eastmoney_stock_info_push2",
    "ths_hot_list", "em_hot_rank", "em_hot_concept",
    "get_limit_up_pool", "get_limit_broken_pool", "get_limit_down_pool", "get_limit_pool_summary",
    "get_yesterday_limit_pool",  # V16.1: 昨日涨停池（晋级率）
    "extract_report_valuation",  # V16.1: 研报估值提取
    # V16.1.7: 新数据源封装（字典 §12.10/12.12）
    "get_cls_market_emotion", "get_kph_limit_ladder",
    "get_stock_changes", "get_shortline_indicators",
    "em_stock_monitor",  # V16.0: 重点监控池
    "get_board_fund_flow",  # V16.0: 板块资金流向
    "ths_limit_up_pool",
    "get_eastmoney_minute_fund_flow", "get_fund_flow_weighted",
    "cls_telegraph", "dragon_tiger_backup", "fund_flow_backup", "cninfo_irm",
    # zhb A级数据（V9.6）
    "get_zhb_sp_block", "get_zhb_sp_block_list", "get_zhb_sw_industries",
    "get_zhb_industry_map", "get_zhb_data_date",
    # zhb B级数据（V9.6 阶段二）
    "get_zhb_stock_stat", "get_zhb_stock_stat2", "get_zhb_market_snapshot",
    "get_zhb_52w_range", "get_zhb_industry_code", "is_zhb_data_fresh",
    "zhb_field_safe",
    # zhb 辅助数据（V9.6 阶段三）
    "get_zhb_tip_info", "get_zhb_ipo_list", "get_zhb_ah_stocks", "get_zhb_broker_name",
    # zhb V10.0 新增
    "get_zhb_holidays", "get_zhb_csrc_industries", "get_zhb_adr_stocks",
    "get_zhb_convertible_bonds", "get_zhb_delisted_stocks",
    # zhb V10.0 智能日期筛选
    "should_use_zhb_data", "is_zhb_date_matching",
    # zhb V10.1 新增：全量字段 + 衍生指标
    "get_zhb_full_market_snapshot", "get_zhb_market_stat2_snapshot",
    "get_zhb_dividend_yield", "get_zhb_streak_days", "get_zhb_change_ytd",
    "get_zhb_ipo_price", "get_zhb_amount_wan", "get_zhb_amount_1d",
    "get_zhb_net_profit_kcf",  # V16.0: 扣非净利润(万元, Col[14]联网确认)
    "get_zhb_single_stock_data",
    # zhb V10.3 新增：主力资金流向
    "get_zhb_main_net_buy", "get_zhb_main_net_buy_amount",
    "get_zhb_main_net_buy_amount_1d",
    # V10.1: 全局股本缓存 + 市值计算
    "get_share_capital", "calc_mcap_yi", "calc_float_mcap_yi",
    # V16: 连续 ZHB 回溯补充字段
    "sc_zhb",
    "backtrack_field", "backtrack_stats", "backtrack_with_extractor",
    "list_zhb_archives", "zhb_archive_summary",
    # V12.4: 策略报告通用运行框架
    "BaseReportRunner",
]

# ═══════════════════════════════════════════════════════════════
# 第一部分：从已拆分的子模块导入（sc_network / sc_scoring / sc_utils）
# ═══════════════════════════════════════════════════════════════

# --- 网络层 ---
from stock_common.sc_network import (
    # 日志
    _LOG_DIR, _http_logger, _biz_logger, _DEBUG, _debug_log,
    # 常量
    UA, DATACENTER_URL, JP_URL,
    # Session
    EM_SESSION, EM_MIN_INTERVAL, _EM_LAST_CALL,
    # 限流
    _DOMAIN_LIMITS, _DOMAIN_LAST_TIME, _DOMAIN_LAST_TIME_LOCK, _RL_STATS,
    # 进程间锁
    _em_lock_dir, _em_lock_file, _gen_lock_file,
    _file_lock_acquire, _file_lock_release,
    # 同步请求
    em_get, _em_wait_process_interval, _gen_wait_process_interval,
    _request_with_retry, _quick_request, _do_request,
    _log_rate_limit, print_rate_limit_stats, _market_code,
    # 异步请求
    _em_async_lock, _gen_async_lock, _em_async_last_request,
    _gen_async_last_request, _HAS_ASYNCIO, _HAS_AIOHTTP,
    _ensure_async_locks, _em_wait_process_interval_async,
    _gen_wait_process_interval_async, create_async_session,
    _async_request_with_retry, _async_quick_request,
)

# --- 评分系统 ---
from stock_common.sc_scoring import (
    ScoreData, ScoreResult,
    _score_technical, _score_fundamental, _score_valuation,
    _score_flow, _score_holder, _score_dividend,
    calculate_score, calculate_score_by_school,
    calculate_multi_school_scores, format_multi_school_report,
    SCHOOL_CONFIGS,
)

# --- 工具函数 ---
from stock_common.sc_utils import (
    get_version,
    _safe_float,
    ensure_output_dir, get_script_dir,
    get_board_type, is_limit_up, is_limit_down,
    clean_codes, parse_args,
    _safe_cleanup_tdx,
    _load_settings, _load_strategy_config,
    _settings_cache, _strategy_config_cache,
)

from stock_common.sc_technical import (  # V16.1: 技术指标引擎
    calc_macd,
    calc_rsi,
    calc_bollinger,
    calc_kdj,
    calc_volume_analysis,
    calc_ma,
    analyze_technical,
)

from stock_common.sc_risk import (  # V16.1: 风险扫描引擎
    scan_financial_risk,
    scan_event_risk,
    combine_risk,
)


# ═══════════════════════════════════════════════════════════════
# 第二部分：数据源函数 - 从新模块导入
# ═══════════════════════════════════════════════════════════════
from stock_common.sc_datasource import (
    # 东财数据中心
    eastmoney_datacenter, _em_filter,
    eastmoney_datacenter_async, _em_filter_async,
    # 股东数据
    holder_change, holder_change_async,
    _holder_fetch_from_sqlite, _holder_update_sqlite,
    _holder_fetch_em, _holder_fetch_tdx,
    _holder_fetch_tdx_optimized,
    _compute_holder_changes,
    _HOLDER_CACHE_TTL, _HOLDER_CACHE_REFRESH,
    # 公告和股东结构
    get_strategic_announcements, get_strategic_announcements_async,
    _cninfo_get_orgid, _CNINFO_ORGID_CACHE,
    _holder_structure_cache,
    get_holder_structure, get_holder_structure_async,
    # 行情和K线
    get_tencent_quote, get_tencent_quote_async,
    baidu_kline_full, get_stock_info, get_stock_info_async,
    # 研报
    get_reports, get_reports_async,
    get_industry_reports, get_eps_forecast, get_eps_forecast_async,
    # 北向资金
    get_northbound_hold, get_northbound_hold_async,
    _northbound_cache_path, _load_northbound_cache,
    # 融资融券
    get_margin_trading, get_margin_trading_async,
    # 大宗交易
    get_block_trade, get_block_trade_async,
    # 分红
    get_dividend_history, get_dividend_history_async,
    # 概念板块
    get_concept_blocks, get_concept_blocks_async,
    # 同花顺热点题材
    get_ths_hot_reason, get_ths_hot_reason_async,
    # 行业对比
    get_industry_peers, get_industry_peers_async,
    get_stock_sector_rank, get_stock_sector_rank_async,
    get_industry_comparison, get_industry_comparison_async,
    _get_eastmoney_industry_sectors,
    # 新闻
    get_eastmoney_stock_news, get_eastmoney_global_news,
    # 新浪财报
    get_sina_financial_report, get_sina_financial_report_async,
    get_sina_balance_sheet, get_sina_balance_sheet_async,
    # 东财批量行情（V11.5新增，替代TDX）
    get_em_batch_quotes,
    # V12.0: 东财HTTP替代接口（完全移除easy_tdx）
    get_em_board_list, get_em_board_members, get_em_belong_boards,
    get_em_fund_flow, get_em_history_fund_flow,
    # 东财现金流量表（V9.6新增）
    get_eastmoney_cash_flow, get_eastmoney_cash_flow_async,
    # 北向资金大盘
    get_hsgt_macro_flow, get_hsgt_macro_flow_async,
    # 限售解禁
    get_lockup_expiry, get_lockup_expiry_async,
    # 毛利率和ROE
    get_gross_margin_and_roe, get_gross_margin_and_roe_async,
    # 交易日历
    _try_upgrade_calendar,
    get_valuation_pe_center, is_trading_day, get_market_status,
    # 辅助函数
    print_batch_summary,
    # 龙虎榜
    get_dragon_tiger_board, get_dragon_tiger_board_async,
    get_recent_dragon_tiger, get_recent_dragon_tiger_async,
    # 舆情互动层（V8.9）
    eastmoney_stock_info_push2,
    ths_hot_list, em_hot_rank, em_hot_concept,
    # 打板层（V9.6）
    get_limit_up_pool, get_limit_broken_pool, get_limit_down_pool, get_limit_pool_summary,
    get_yesterday_limit_pool,  # V16.1: 昨日涨停池（晋级率）
    extract_report_valuation,  # V16.1: 研报估值提取
    # V16.1.7: 新数据源封装（字典 §12.10/12.12）
    get_cls_market_emotion, get_kph_limit_ladder,
    get_stock_changes, get_shortline_indicators,
    em_stock_monitor,  # V16.0: 重点监控池
    get_board_fund_flow,  # V16.0: 板块资金流向
    ths_limit_up_pool,
    # 东财分钟级资金流（V9.6）
    get_eastmoney_minute_fund_flow, get_fund_flow_weighted,
    # 财联社快讯/官方备胎池/舆情互动层（V9.6）
    cls_telegraph, dragon_tiger_backup, fund_flow_backup, cninfo_irm,
    # zhb A级数据（V9.6）
    get_zhb_sp_block, get_zhb_sp_block_list, get_zhb_sw_industries,
    get_zhb_industry_map, get_zhb_data_date,
    # zhb B级数据（V9.6 阶段二）
    get_zhb_stock_stat, get_zhb_stock_stat2, get_zhb_market_snapshot,
    get_zhb_52w_range, get_zhb_industry_code, is_zhb_data_fresh,
    zhb_field_safe,
    # zhb 辅助数据（V9.6 阶段三）
    get_zhb_tip_info, get_zhb_ipo_list, get_zhb_ah_stocks, get_zhb_broker_name,
    # zhb V10.0 新增
    get_zhb_holidays, get_zhb_csrc_industries, get_zhb_adr_stocks,
    get_zhb_convertible_bonds, get_zhb_delisted_stocks,
    # zhb V10.0 智能日期筛选
    should_use_zhb_data, is_zhb_date_matching,
    # zhb V10.1 新增：全量字段 + 衍生指标
    get_zhb_full_market_snapshot, get_zhb_market_stat2_snapshot,
    get_zhb_dividend_yield, get_zhb_streak_days, get_zhb_change_ytd,
    get_zhb_ipo_price, get_zhb_amount_wan, get_zhb_amount_1d,
    get_zhb_net_profit_kcf,  # V16.0: 扣非净利润(万元)
    get_zhb_single_stock_data,
    # zhb V10.3 新增：主力资金流向
    get_zhb_main_net_buy, get_zhb_main_net_buy_amount,
    get_zhb_main_net_buy_amount_1d,
    # V10.1: 全局股本缓存 + 市值计算
    get_share_capital, calc_mcap_yi, calc_float_mcap_yi,
)


# ═══════════════════════════════════════════════════════════════
# V16: 连续 ZHB 回溯补充字段（sc_zhb）
# ═══════════════════════════════════════════════════════════════
from stock_common.sc_zhb import (
    backtrack_field, backtrack_stats, backtrack_with_extractor,
    list_archives as list_zhb_archives,
    archive_summary as zhb_archive_summary,
)


# ═══════════════════════════════════════════════════════════════
# V12.4: 策略报告通用运行框架
# ═══════════════════════════════════════════════════════════════
from stock_common.sc_report_runner import BaseReportRunner


# ═══════════════════════════════════════════════════════════════
# 注册 atexit（TDX 清理）
# ═══════════════════════════════════════════════════════════════
import atexit
atexit.register(_safe_cleanup_tdx)


# ═══════════════════════════════════════════════════════════════
# 模块状态信息（用于调试）
# ═══════════════════════════════════════════════════════════════
_MIGRATION_STATUS = {
    "sc_network": "migrated",
    "sc_scoring": "migrated",
    "sc_utils": "migrated",
    "sc_datasource": "migrated",
}
