# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [9.3.0] - 2026-07-07

### Added

- **盘前行情模式**（`tdx_client.py`）：9:30前自动使用上一交易日日K线数据，避免实时接口返回 0 导致涨跌幅计算为 -100%
  - 新增 `_is_before_market_open()` 判断函数
  - 新增 `_get_trading_date_for_quote()` 生成带交易日期的缓存 Key
  - 新增 `_pre_market_quote_from_kline()` 从日K线构建盘前行情
- **缓存 Key 交易日期隔离**：行情缓存 Key 格式改为 `Q:{code}:{trading_date}`，盘前/盘中数据独立保留，避免相互覆盖
- **报告盘前提示**：sht/med/lng 等报告在盘前模式时显示“⚠️ 盘前模式（9:30前），以下行情数据基于上一交易日收盘数据”

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
