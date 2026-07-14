================================================================
  tests 目录文件说明
================================================================
本目录包含两类文件：pytest 单元测试（运行 pytest 时会被自动收集）
和独立诊断脚本（手动运行，用于排查问题）。

重要提示：所有诊断脚本都必须在项目根目录运行（即 a-stock-data-v7\
目录下），否则无法 import stock_common 等模块。


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【第一类】pytest 单元测试  (运行:  pytest tests/)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

按模块分类：

├── sc_utils (工具函数)
│   └── test_stock_common.py
│       覆盖：
│       - _safe_float：各种输入类型（字符串、int、float、None、NaN、inf）
│       - get_board_type：板块判断（科创板/创业板/主板/ST）
│       - is_limit_up / is_limit_down：涨跌停判断（V10.0: ST涨跌幅放宽至10%）
│       - clean_codes：代码清洗与去重
│       何时需要：修改了 sc_utils.py 中的工具函数后

├── sc_scoring (评分系统)
│   └── test_scoring.py
│       覆盖：
│       - _score_technical：技术面 bullish/bearish、涨停加分、边界限制
│       - _score_fundamental：ROE 三档（高/中/亏损）、边界限制
│       - _score_valuation：PE 低估、PE 高估、PE 中性、PE 无数据
│       - _score_flow：净流入加分、无数据兜底
│       - _score_holder：筹码集中度三档
│       - _score_dividend：股息率高低档
│       - calculate_score：full/dict/med_lng 三种输出模式
│       - ScoreData / ScoreResult 数据结构
│       何时需要：修改了评分维度或权重配置后

├── stock_cache (缓存层)
│   ├── test_cache.py
│   │   覆盖：
│   │   - set_cache / get_cache：基本读写与 key 构建
│   │   - TTL 过期：不同 category 的过期行为
│   │   - invalidate_category / invalidate_prefix：按分类/前缀清理
│   │   - print_cache_stats：命中率与占用统计
│   │   - @cached 装饰器：同步函数缓存效果验证
│   │   - STOCK_NOCACHE=1 环境变量禁用缓存
│   │   - 空值写入：确保 {} / [] / "" 等空值不写入缓存
│   │   何时需要：修改了 stock_cache.py 或缓存策略后
│   │
│   └── test_cache_verify.py
│       覆盖：
│       - 首次写入未验证（verified=0），get_cache 返回 None
│       - 第二次写入相同数据，标记为已验证（verified=1），可正常读取
│       - 第二次写入不同数据，重置验证状态（verified=0，prev_value=NULL）
│       - 已验证数据不被覆盖，仅刷新过期时间
│       - 普通模式（cross_verify=False）不受影响
│       - @cached 装饰器集成测试：模拟连续两次调用验证通过
│       何时需要：修改了交叉验证逻辑或缓存表结构后

├── stock_calendar (交易日历)
│   └── test_calendar.py
│       覆盖：
│       - is_workday：已知节假日、调休日、周末交易日验证
│       - _wrap_date：datetime → date 转换
│       - _validate_date：日期范围验证与错误输入处理
│       何时需要：修改了交易日历逻辑或 chinese-calendar 更新后

├── strategy_config (策略配置)
│   └── test_strategy.py
│       覆盖：
│       - strategy_config.yaml / keywords_config.yaml 存在性
│       - _load_strategy_config / _load_settings 返回 dict
│       - get_valuation_pe_center：默认返回正浮点数
│       - get_val_report 策略函数可导入且处理空股票池
│       - top5 函数返回有序列表
│       - kline_indices 返回 dict 结构
│       - keywords_config 包含行业名清理或别名配置
│       何时需要：修改了策略参数或关键词配置后

├── gd_uploader (GD上传模块)
│   └── test_gd_uploader.py
│       覆盖：
│       - _find_working_proxy：代理发现函数在无网络时返回 None
│       - cleanup_gd_proxy：环境变量清理是否正常
│       - get_or_create_drive_folder(None, ...)：传入 None 时是否返回 None
│       - upload_or_update_to_drive(None, ...)：service 为 None 时返回 False
│       - upload_or_update_to_drive(... fake_service)：service 正常时走完整路径
│       何时需要：修改了 gd_uploader.py 或上传逻辑后

├── em_rate_limit (东财限流测试)
│   └── test_em_rate_limit.py
│       覆盖：
│       - 基准测试：单域名 push2，1秒间隔，验证安全基线
│       - 交叉测试：三域名轮询，总QPS≈3，验证是否触发限流
│       - 串行测试：三域名串行，总QPS≈1，作为对照组
│       何时需要：想验证东财限流阈值，调整限流参数前（谨慎使用）

├── f10_integration (F10集成测试)
│   └── test_f10_chapters_integration.py
│       覆盖：
│       - 验证 3 个报告脚本（med/lng/ful）中的 F10 新章节是否正确渲染
│       何时需要：修改了 F10 章节逻辑后（需联网，约 5-10 分钟）

└── conftest.py
    作用：pytest 共享 fixtures 配置
    - 全局拦截所有 HTTP 请求，阻止测试期间真实联网
    - 提供临时项目目录（含模拟的 strategy_config.yaml）
    - 使用 @pytest.mark.real_network 标记的测试不会被网络 mock 拦截


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【第二类】独立诊断脚本  (手动运行:  python tests\xxx.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

按数据源分类：

├── TDX 数据源
│   ├── diagnose_tdx.py
│   │   作用：通达信（TDX）数据接口连通性与稳定性诊断
│   │   覆盖：easy_tdx 安装检查、TdxClient连接、MacClient全市场列表、
│   │         tdx_client.py封装函数、连续20次请求压力测试
│   │   何时需要：脚本报TdxClient连接失败/K线返回空/怀疑IP被封禁
│   │
│   ├── diag_tdx_basic.py
│   │   作用：TDX基础接口诊断（行情/K线/资金流/财务）
│   │   覆盖：tdx_get_security_bars、tdx_get_quote_full、tdx_get_index_quote、
│   │         tdx_get_fund_flow、tdx_get_history_fund_flow、tdx_get_finance_info、
│   │         tdx_get_dividend_history、tdx_get_eps_from_reports
│   │   何时需要：TDX行情/K线返回空时定位问题
│   │
│   ├── diag_tdx_f10.py
│   │   作用：TDX F10接口诊断（财务分析/股东研究/股本结构等）
│   │   覆盖：tdx_get_financial_analysis、tdx_get_shareholder_research、
│   │         tdx_get_share_capital、tdx_get_latest_reminders、
│   │         tdx_get_company_news_f10、tdx_get_latest_announcements
│   │   何时需要：F10章节数据异常时定位具体哪个分类出问题
│   │
│   ├── diag_tdx_board.py
│   │   作用：TDX板块接口诊断（所属板块/板块列表/板块成员/全市场）
│   │   覆盖：tdx_get_belong_boards、tdx_get_board_list、tdx_get_board_members、
│   │         tdx_get_all_stocks
│   │   何时需要：概念板块/行业板块数据异常时定位问题
│   │
│   ├── diag_tdx_hosts_test.py
│   │   作用：测试 easy_tdx 内置的全部 TDX 服务器 K线可用性
│   │   覆盖：逐个测试52个内置TDX服务器的get_security_bars接口
│   │   何时需要：K线数据全部N/A或返回空，怀疑选到了假数据服务器
│   │
│   ├── diag_tdx_final.py
│   │   作用：捕获 TDX K线请求的原始 TCP 响应（header + body）
│   │   覆盖：monkey-patch TdxConnection.execute，打印FrameHeader、raw_body、
│   │         解压后body、ret_count与实际数据对比
│   │   何时需要：需要确认TDX服务器是否返回假数据、怀疑协议变更或解码bug
│   │
│   ├── diag_tdx_compare.py
│   │   作用：easy-tdx 与 mootdx 接口对比测试
│   │   覆盖：K线数据、实时行情、资金流、板块数据、复权数据、连接稳定性
│   │   何时需要：确认两库的功能差异、决定是否引入mootdx作为补充库
│   │
│   ├── diag_mootdx.py
│   │   作用：mootdx 库单独测试，验证 K线参数和复权数据
│   │   覆盖：mootdx版本信息、Quotes类方法签名、bars方法frequency参数映射、
│   │         xdxr复权数据获取、实际K线数据获取测试
│   │   何时需要：验证mootdx安装和基本功能
│   │
│   └── diag_qfq_debug.py
│       作用：前复权算法调试，手动检查除权除息数据处理逻辑
│       何时需要：复权数据异常时进行深度调试

├── 东财数据源
│   ├── diag_eastmoney.py
│   │   作用：东财接口诊断，测试东方财富HTTP接口
│   │   覆盖：eastmoney_datacenter、get_reports、get_eastmoney_stock_news、
│   │         get_holder_structure、get_northbound_hold、get_margin_trading、
│   │         get_block_trade、get_lockup_expiry、get_industry_comparison、
│   │         get_industry_peers、get_stock_sector_rank、get_gross_margin_and_roe、
│   │         em_hot_concept、eastmoney_stock_info_push2
│   │   何时需要：东财数据源异常时统一定位问题
│   │
│   └── diag_dragon_tiger.py
│       作用：龙虎榜数据接口连通性与可用性诊断
│       覆盖：东财datacenter 3个龙虎榜接口、全市场龙虎榜接口、
│             stock_common.get_dragon_tiger_board()、
│             stock_common.get_recent_dragon_tiger()、时段自动判断
│       何时需要：短线/中线脚本龙虎榜字段全是0或空、怀疑接口变化

├── 同花顺数据源
│   └── diag_ths.py
│       作用：同花顺接口诊断，测试同花顺HTTP接口
│       覆盖：get_ths_hot_reason、ths_hot_list
│       何时需要：同花顺热榜/热点原因数据异常时定位问题

├── 其他数据源
│   ├── diag_other.py
│   │   作用：其他接口诊断（腾讯/新浪/百度/巨潮）
│   │   覆盖：get_tencent_quote、get_sina_financial_report、
│             baidu_kline_full(deprecated)、get_strategic_announcements、
│             get_hsgt_macro_flow
│   │   何时需要：验证腾讯/新浪/百度/巨潮等第三方数据源连通性
│   │
│   ├── diag_datasource.py
│   │   作用：多数据源接口连通性诊断，一次性测试所有主要数据接口
│   │   覆盖：腾讯行情、东财数据中心、东财push2、东财研报、同花顺强势股、
│             新浪财报、百度股市通(deprecated)、巨潮资讯、通达信TCP行情、
│             TDX财务信息/资金流/分红除权/MacClient/所属板块/板块成员
│   │   何时需要：多个脚本同时报告数据为空、怀疑IP被限流或封禁
│   │
│   └── diag_news_and_finance.py
│       作用：东财新闻和新浪财报接口测试，验证接口修复效果
│       覆盖：东财新闻API、新浪现金流量表API、利润表和资产负债表验证
│       何时需要：验证东财新闻解析修复是否生效

├── zhb全局配置总包
│   └── diag_zhb.py
│       作用：zhb全局配置总包功能验证，测试所有zhb解析功能
│       覆盖（共16个测试用例）：
│       ① zhb_client下载与解析 ② spblock大板块成分 ③ 申万行业分类
│       ④ 行业代码映射 ⑤ 缓存机制 ⑥ sc_datasource集成接口
│       ⑦ tdxstat全市场统计快照 ⑧ tdxstat2资金流向+板块归属
│       ⑨ 数据新鲜度检查 ⑩ tipinfo财报日历 ⑪ 新股申购日历
│       ⑫ A+H股+券商名称表 ⑬ 节假日数据(V10.0) ⑭ 证监会行业分类(V10.0)
│       ⑮ 中概股ADR/可转债/退市股(V10.0) ⑯ V10.0 sc_datasource导出接口验证
│       何时需要：验证zhb下载和解析功能、确认全市场统计快照/行业分类等数据

└── 专项验证
    ├── diag_issues.py
    │   作用：专项问题验证脚本，用于复现和验证特定bug修复
    │   覆盖：指数涨跌幅数据验证、板块排名验证、行业对标验证、
    │         龙虎榜数据验证、多评委评分验证
    │   何时需要：开发期间验证特定bug修复是否生效、回归测试
    │
    ├── diag_v34_verify.py
    │   作用：源仓库V3.4.0关键接口验证
    │   覆盖：解禁接口字段验证、行业排名排序验证、北向资金数据可靠性验证、
    │         东财新闻解析验证、新浪财报三表解析验证
    │   何时需要：验证V9.6修复的接口问题是否已解决
    │
    └── diag_v96_skill_verify.py
        作用：SKILL.md V3.4复活版接口验证
        覆盖：财联社快讯、互动易问答、龙虎榜官方备胎、新浪资金流备胎
        何时需要：验证V9.6新增的备用数据源接口是否正常


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【速查：日常使用指南】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

想跑全部单元测试，确认近期修改没有引入回归：
    cd 到项目根目录
    pytest tests/ -v

想只跑特定模块的单元测试：
    pytest tests/test_stock_common.py -v   # sc_utils 工具函数
    pytest tests/test_scoring.py -v        # 评分系统
    pytest tests/test_cache.py -v          # 缓存层
    pytest tests/test_cache_verify.py -v   # 缓存交叉验证
    pytest tests/test_calendar.py -v       # 交易日历
    pytest tests/test_strategy.py -v       # 策略配置

短线脚本龙虎榜全是0 / 想判断数据接口是否正常：
    python tests\diag_dragon_tiger.py
    python tests\diag_dragon_tiger.py 301217 600036

脚本报TdxClient连接失败 / K线返回空：
    python tests\diagnose_tdx.py

K线全部N/A或返回空，怀疑选到了假数据服务器：
    python tests\diag_tdx_hosts_test.py

需要查看TDX原始TCP响应，确认服务器是否返回假数据：
    python tests\diag_tdx_final.py

想一次性验证所有数据源接口：
    python tests\diag_datasource.py

想按数据源分类测试：
    # TDX基础接口（行情/K线/资金流/财务）
    python tests\diag_tdx_basic.py
    # TDX F10接口（财务分析/股东研究/股本结构等）
    python tests\diag_tdx_f10.py
    # TDX板块接口（所属板块/板块列表/板块成员）
    python tests\diag_tdx_board.py
    # 东财接口（研报/新闻/股东/北向/融资融券等）
    python tests\diag_eastmoney.py
    # 同花顺接口（热点原因/热榜）
    python tests\diag_ths.py
    # 其他接口（腾讯/新浪/百度/巨潮）
    python tests\diag_other.py

想验证zhb全局配置总包功能：
    python tests\diag_zhb.py

想验证特定bug修复是否生效：
    python tests\diag_issues.py

更新时间：2026-07-14（V10.0 按模块/数据源分类重新组织测试文档）
