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
    "get_board_type", "limit_pct_for", "is_limit_up", "is_limit_down",
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
    "get_limit_pool_multi_source",  # V16.3.3: 涨停池三源互校
    "get_fupan_zttt", "get_fupan_pmsl",  # V16.3.3: 复盘啦缓存包装
    "get_stock_permanent_info",  # V16.3.3: 永久字段 10 年缓存
    "get_yesterday_limit_pool",  # V16.1: 昨日涨停池（晋级率）
    "extract_report_valuation",  # V16.1: 研报估值提取
    # V16.1.7: 新数据源封装（字典 §12.10/12.12）
    "get_cls_market_emotion", "get_kph_limit_ladder",
    "get_stock_changes", "get_shortline_indicators",
    "em_stock_monitor",  # V16.0: 重点监控池
    "get_board_fund_flow",  # V16.0: 板块资金流向
    "ths_limit_up_pool",
    "get_eastmoney_minute_fund_flow", "get_fund_flow_weighted",
    "cls_telegraph", "news_matches_stock", "get_history_fund_flow_120d", "get_em_industry_l2_data", "get_em_industry_l2", "get_em_industry_members_l2", "dragon_tiger_backup", "fund_flow_backup", "cninfo_irm",
    # zhb A级数据（V9.6）—— V17.0 S1: 删 21 个零调用死转发, 保留有调用方项
    "get_zhb_industry_map", "get_zhb_data_date",
    # zhb B级数据（V9.6 阶段二）
    "get_zhb_market_snapshot", "is_zhb_data_fresh",
    "zhb_field_safe",
    # zhb 辅助数据（V9.6 阶段三）—— 仅保留存活项
    "get_zhb_tip_info",
    # zhb V10.1 新增：全量字段 + 衍生指标（仅保留存活项）
    "get_zhb_full_market_snapshot", "get_zhb_market_stat2_snapshot",
    "get_zhb_dividend_yield", "get_zhb_streak_days", "get_zhb_change_ytd",
    "get_zhb_amount_wan",
    "get_zhb_single_stock_data",
    # zhb V10.3 新增：主力资金流向（仅保留存活项）
    "get_zhb_main_net_buy",
    # V10.1: 全局股本缓存 + 市值计算
    "get_share_capital", "calc_mcap_yi", "calc_float_mcap_yi",
    # V16: 连续 ZHB 回溯补充字段（V17.0 S1: 函数本体随 sc_zhb 模块删除, 保留导出占位见 import 块注释）
    # V12.4: 策略报告通用运行框架
    "BaseReportRunner",
    # V16.3 O35: 新数据源适配器（字典 §12.8.12b/§12.17/§12.18）
    "get_ths_market_snapshot", "get_ths_pb", "get_ths_credentials",
    "get_kpl_market_sentiment", "get_kpl_up_down", "get_kpl_plate_strength",
    "get_kpl_limit_up_detail", "get_kpl_broken_ratio",
    "get_plate_rotation_matrix", "get_plate_rotation_top",
    # V16.3.3: fuyao 官方 REST
    "is_fuyao_enabled", "get_fuyao_key", "ensure_fuyao_key",
    "get_fuyao_snapshot", "get_fuyao_valuation", "get_fuyao_kline",
    "get_fuyao_limit_up_ladder", "get_fuyao_hot_list", "get_fuyao_dragon_tiger",
    "fuyao_to_thscode",
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
    get_board_type, limit_pct_for, is_limit_up, is_limit_down,
    clean_codes, parse_args,
    _safe_cleanup_tdx,
    _load_settings, _load_strategy_config,
    _settings_cache, _strategy_config_cache,
    # V17.0 新增公共工具（S3 市场代码 / S5 报告样板 / sc_render）
    em_secid_prefix, is_a_stock, name_mark, save_text_report,
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
    get_limit_pool_multi_source,
    get_fupan_zttt, get_fupan_pmsl,
    get_stock_permanent_info,
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
    cls_telegraph, news_matches_stock, get_history_fund_flow_120d, get_em_industry_l2_data, get_em_industry_l2, get_em_industry_members_l2, dragon_tiger_backup, fund_flow_backup, cninfo_irm,
    # zhb A级数据（V9.6）—— V17.0 S1: 删 21 个零调用死转发
    get_zhb_industry_map, get_zhb_data_date,
    # zhb B级数据（V9.6 阶段二）
    get_zhb_market_snapshot, is_zhb_data_fresh,
    zhb_field_safe,
    # zhb 辅助数据（V9.6 阶段三）—— 仅保留存活项
    get_zhb_tip_info,
    # zhb V10.1 新增：全量字段 + 衍生指标（仅保留存活项）
    get_zhb_full_market_snapshot, get_zhb_market_stat2_snapshot,
    get_zhb_dividend_yield, get_zhb_streak_days, get_zhb_change_ytd,
    get_zhb_amount_wan,
    get_zhb_single_stock_data,
    # zhb V10.3 新增：主力资金流向（仅保留存活项）
    get_zhb_main_net_buy,
    # V10.1: 全局股本缓存 + 市值计算
    get_share_capital, calc_mcap_yi, calc_float_mcap_yi,
)


# ═══════════════════════════════════════════════════════════════
# V16.3 O35: 新数据源适配器（字典 §12.8.12b THS / §12.17 KPL / §12.18 板块轮动）
# ═══════════════════════════════════════════════════════════════
from stock_common.sc_ths import (  # THS SDK（同花顺官方 C 库——正式账号无限频）
    get_ths_market_snapshot, get_ths_pb, get_ths_credentials,
)
from stock_common.sc_kpl import (  # 开盘啦 KPL（longhuvip 私有 API——匿名接口）
    get_kpl_market_sentiment, get_kpl_up_down, get_kpl_plate_strength,
    get_kpl_limit_up_detail, get_kpl_broken_ratio,
)
from stock_common.sc_plate_rot import (  # 板块轮动（duanxianxia 短线侠——N×天矩阵）
    get_plate_rotation_matrix, get_plate_rotation_top,
)

# V16.3.3: 同花顺官方金融数据 REST（fuyao.aicubes.cn，字典 §12.8.12c）——Key 交互引导 + 跳过禁用
from stock_common.sc_fuyao import (
    is_fuyao_enabled, get_fuyao_key, ensure_fuyao_key,
    get_fuyao_snapshot, get_fuyao_valuation, get_fuyao_kline,
    get_fuyao_limit_up_ladder, get_fuyao_hot_list, get_fuyao_dragon_tiger,
    fuyao_to_thscode,
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
