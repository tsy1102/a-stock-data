# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
