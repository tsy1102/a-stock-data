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

1. conftest.py
   作用：pytest 共享 fixtures 配置。
   - 全局拦截所有 HTTP 请求，阻止测试期间真实联网；
   - 提供临时项目目录（含模拟的 strategy_config.yaml）。
   何时需要：运行 pytest 时自动生效，不需手动调用。


2. test_stock_common.py
   作用：测试 stock_common.py 中的工具函数。
   覆盖：
   - _safe_float：各种输入类型（字符串、int、float、None、NaN、inf）；
   - holder_cache_flush：缓存刷新在缺省目录下是否抛异常。
   何时需要：修改了 stock_common.py 中的工具函数后，运行一次确保无回归。


3. test_gd_uploader.py
   作用：测试 gd_uploader.py（Google Drive 上传模块）。
   覆盖：
   - _find_working_proxy：代理发现函数在无网络时返回 None；
   - cleanup_gd_proxy：环境变量清理是否正常；
   - get_or_create_drive_folder(None, ...)：传入 None 时是否返回 None；
   - upload_or_update_to_drive(None, ...)：service 为 None 时返回 False；
   - upload_or_update_to_drive(... fake_service)：service 正常时走完整路径；
     包括 media body 构造，mock 成功场景。
   何时需要：修改了 gd_uploader.py 或上传逻辑后，运行一次确认无回归。


4. test_cache.py（V8.4 新增）
   作用：测试 stock_cache.py 缓存层核心功能。
   覆盖：
   - set_cache / get_cache：基本读写与 key 构建；
   - TTL 过期：不同 category 的过期行为；
   - invalidate_category / invalidate_prefix：按分类/前缀清理；
   - print_cache_stats：命中率与占用统计；
   - @cached 装饰器：同步函数缓存效果验证；
   - STOCK_NOCACHE=1 环境变量禁用缓存；
   - 空值写入：确保 {} / [] / "" 等空值不写入缓存。
   何时需要：修改了 stock_cache.py 或缓存策略后。


5. test_cache_verify.py（V9.2 新增）
   作用：测试 stock_cache.py 交叉验证（cross_verify）机制。
   覆盖：
   - 首次写入未验证（verified=0），get_cache 返回 None；
   - 第二次写入相同数据，标记为已验证（verified=1），可正常读取；
   - 第二次写入不同数据，重置验证状态（verified=0，prev_value=NULL）；
   - 已验证数据不被覆盖，仅刷新过期时间；
   - 普通模式（cross_verify=False）不受影响；
   - @cached 装饰器集成测试：模拟连续两次调用验证通过。
   何时需要：修改了交叉验证逻辑或缓存表结构后。


6. test_calendar.py（V8.4 新增）
   作用：测试 stock_common.py 交易日历判断函数。
   覆盖：
   - is_trading_day()：普通工作日（周一~五）、周末、节假日、调休日；
   - get_market_status()：盘前/上午/午休/下午/盘后/休市各状态；
   - 已知节假日验证：元旦、春节、劳动节、国庆节、端午、中秋；
   - 调休日验证：节假日前后补班日；
   - 边界情况：None / 超范围日期 / datetime 输入。
   何时需要：修改了交易日历逻辑或 chinese-calendar 更新后。


7. test_scoring.py（V8.4 新增）
   作用：测试统一评分接口 calculate_score() 及各维度评分函数。
   覆盖：
   - _score_technical：技术面 bullish/bearish、涨停加分、边界限制；
   - _score_fundamental：ROE 三档（高/中/亏损）、边界限制；
   - _score_valuation：PE 低估、PE 高估、PE 中性、PE 无数据；
   - _score_flow：净流入加分、无数据兜底；
   - _score_holder：筹码集中度三档；
   - _score_dividend：股息率高低档；
   - calculate_score：full/dict/med_lng 三种输出模式；
   - 空数据兜底：返回有效评分的边界处理。
   何时需要：修改了评分维度或权重配置后。


8. test_strategy.py（V8.4 新增）
   作用：测试选股策略配置加载与策略函数基本行为。
   覆盖：
   - strategy_config.yaml / keywords_config.yaml 存在性；
   - _load_strategy_config / _load_settings 返回 dict；
   - get_valuation_pe_center：默认返回正浮点数；
   - get_val_report 策略函数可导入且处理空股票池；
   - top5 函数返回有序列表；
   - kline_indices 返回 dict 结构；
   - get_val_report 接受 parse_args；
   - keywords_config 包含行业名清理或别名配置。
   何时需要：修改了策略参数或关键词配置后。


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【第二类】独立诊断脚本  (手动运行:  python tests\xxx.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


9. diag_dragon_tiger.py
   作用：龙虎榜数据接口连通性与可用性诊断。
   运行：python tests\diag_dragon_tiger.py [股票代码1] [股票代码2] ...
          （不传参数默认跑 600519 / 000001 / 300750）
   输出包含 4 个部分：
     ① 直接调用东财 datacenter 3 个龙虎榜接口（上榜明细/买入席位/
        卖出席位），返回 HTTP 状态码、响应结构、数据条数；
     ② 全市场龙虎榜接口（最近 10 日所有上榜股票）；
     ③ 通过 stock_common.get_dragon_tiger_board() 调用（与短线/中线
        脚本实际使用的代码路径完全一致）；
     ④ 通过 stock_common.get_recent_dragon_tiger(3) 调用（与全市场
        选股/异动扫描脚本实际使用的代码路径一致）；
     ⑤ 自动判断时段（周末/盘中/盘后/稳定时段）并给出解释。
   何时需要：
     - 短线/中线脚本跑出来龙虎榜字段全是 0 或空，想判断是接口问题
       还是脚本逻辑问题；
     - 换电脑 / 换网络环境后，首次验证数据接口连通性；
     - 怀疑东财接口变化时，作为基准测试。


10. diagnose_tdx.py
   作用：通达信（TDX）数据接口连通性与稳定性诊断。
   运行：python tests\diagnose_tdx.py
   输出包含 5 个部分：
     ① easy_tdx 模块是否已安装；
     ② TdxClient 首次连接测试（TCP 连接 + 行情查询）；
     ③ MacClient 全市场列表查询测试；
     ④ 调用 tdx_client.py 中封装的公共函数（_check_tdx、
        _get_tdx_client、tdx_get_security_bars、tdx_get_all_stocks 等）；
     ⑤ 连续 20 次请求的压力测试，看是否被服务器限流或 IP 被拉黑。
   何时需要：
     - 脚本运行时报 TdxClient 连接失败 / Connection refused /
       timeout 等网络错误；
     - K 线数据返回空列表，想确认是 TDX 服务端问题还是业务脚本问题；
     - 怀疑本地 IP 被通达信服务器临时封禁。


11. diag_tdx_hosts_test.py（V9.3.2 新增）
    作用：测试 easy_tdx 内置的全部 TDX 服务器K线可用性。
    运行：python tests\diag_tdx_hosts_test.py
    输出：逐个测试 52 个内置 TDX 服务器的 get_security_bars 接口，
      区分三种状态：
      ✅正常 — K线返回正确数据；
      ❌假数据 — ret_count=800 但 body 为 0 字节（TdxDecodeError）；
      ❌连不上 — TCP 连接超时或被拒绝。
    何时需要：
      - K线数据全部 N/A 或返回空，怀疑选到了假数据服务器；
      - from_best_host() 选的 IP K线接口不可用；
      - 验证 V9.3.2 坏主机黑名单机制是否生效。


12. diag_tdx_final.py（V9.3.2 新增）
    作用：捕获 TDX K线请求的原始 TCP 响应（header + body），深度诊断
      TdxDecodeError 根因。
    运行：python tests\diag_tdx_final.py
    输出：monkey-patch TdxConnection.execute，打印每次 K线请求的：
      - FrameHeader（magic/seq_id/method/zipsize/unzipsize）
      - raw_body 长度和 hex 内容
      - 解压后 body 长度和 hex 内容
      - ret_count 与实际数据字节数的对比
    何时需要：
      - 需要确认 TDX 服务器是否返回假数据（ret_count > 0 但 body 为空）；
      - 怀疑 TDX 协议变更或 easy_tdx 解码逻辑有 bug；
      - diagnose_tdx.py 显示 K线失败但需要更详细的原始数据分析。


13. diag_datasource.py（V8.5 新增，V9.3.1 更新为 V2.3）
    作用：多数据源接口连通性诊断，一次性测试所有主要数据接口。
    运行：python tests\diag_datasource.py
    输出包含：
      ① 腾讯行情接口（qt.gtimg.cn）；
      ② 东财数据中心（datacenter-web.eastmoney.com）；
      ③ 东财 push2 接口（push2.eastmoney.com）；
      ④ 东财研报接口（reportapi.eastmoney.com）；
      ⑤ 同花顺强势股接口（zx.10jqka.com.cn）；
      ⑥ 新浪财报接口（quotes.sina.cn）；
      ⑦ 百度股市通接口（finance.pae.baidu.com，已标记deprecated）；
      ⑧ 巨潮资讯接口（www.cninfo.com.cn）；
      ⑨ 通达信TCP行情接口（tdx_client）；
      ⑩ TDX 财务信息接口（get_finance_info，V9.3.1 新增）；
      ⑪ TDX 资金流接口（get_fund_flow，V9.3.1 新增）；
      ⑫ TDX 分红除权接口（get_xdxr_info，V9.3.1 新增）；
      ⑬ TDX MacClient 连接检测（V9.3.1 新增）；
      ⑭ TDX 所属板块获取（上交所+深交所，V9.3.1 新增）；
      ⑮ TDX 板块成员列表（V9.3.1 新增）。
    何时需要：
      - 多个脚本同时报告数据为空，想快速判断是哪个接口出问题；
      - 怀疑 IP 被限流或封禁时，一次性验证所有数据源；
      - 换网络环境后，首次验证数据接口连通性。


14. diag_tdx_basic.py（V9.3.1 新增，按数据源重组）
    作用：TDX基础接口诊断，测试通达信行情/K线/资金流/财务基础接口。
    运行：python tests\diag_tdx_basic.py
    覆盖接口（共8个）：
      - tdx_get_security_bars（K线行情）
      - tdx_get_quote_full（实时行情）
      - tdx_get_index_quote（指数行情）
      - tdx_get_fund_flow（资金流）
      - tdx_get_history_fund_flow（历史资金流）
      - tdx_get_finance_info（财务信息）
      - tdx_get_dividend_history（分红历史）
      - tdx_get_eps_from_reports（研报EPS）
    何时需要：
      - TDX行情/K线返回空时定位问题；
      - 验证TDX基础数据接口连通性。


15. diag_tdx_f10.py（V9.3.1 新增，按数据源重组）
    作用：TDX F10接口诊断，测试通达信F10各分类接口。
    运行：python tests\diag_tdx_f10.py
    覆盖接口（共6个）：
      - tdx_get_financial_analysis（财务分析）
      - tdx_get_shareholder_research（股东研究）
      - tdx_get_share_capital（股本结构）
      - tdx_get_latest_reminders（最新提示）
      - tdx_get_company_news_f10（公司新闻）
      - tdx_get_latest_announcements（最新公告）
    何时需要：
      - F10章节数据异常时定位具体哪个分类出问题；
      - 验证TDX F10各分类接口连通性。


16. diag_tdx_board.py（V9.3.1 新增，按数据源重组）
    作用：TDX板块接口诊断，测试通达信板块/全市场接口。
    运行：python tests\diag_tdx_board.py
    覆盖接口（共4个）：
      - tdx_get_belong_boards（所属板块）
      - tdx_get_board_list（板块列表）
      - tdx_get_board_members（板块成员）
      - tdx_get_all_stocks（全市场股票）
    何时需要：
      - 概念板块/行业板块数据异常时定位问题；
      - 验证TDX MacClient板块接口连通性（同时测试上交所和深交所）。


17. diag_eastmoney.py（V9.3.1 新增，按数据源重组）
    作用：东财接口诊断，测试东方财富HTTP接口。
    运行：python tests\diag_eastmoney.py
    覆盖接口（共14个）：
      - eastmoney_datacenter（数据中心）
      - get_reports（研报列表）
      - get_eastmoney_stock_news（个股新闻）
      - get_holder_structure（股东结构）
      - get_northbound_hold（北向持仓）
      - get_margin_trading（融资融券）
      - get_block_trade（大宗交易）
      - get_lockup_expiry（限售解禁）
      - get_industry_comparison（行业对比）
      - get_industry_peers（行业同行）
      - get_stock_sector_rank（板块排名）
      - get_gross_margin_and_roe（毛利率/ROE）
      - em_hot_concept（概念命中）
      - eastmoney_stock_info_push2（push2基本面）
    何时需要：
      - 东财数据源异常时统一定位问题；
      - 验证资金面/基本面/行业对比等东财接口连通性。


18. diag_ths.py（V9.3.1 新增，按数据源重组）
    作用：同花顺接口诊断，测试同花顺HTTP接口。
    运行：python tests\diag_ths.py
    覆盖接口（共2个）：
      - get_ths_hot_reason（热点原因）
      - ths_hot_list（热榜）
    何时需要：
      - 同花顺热榜/热点原因数据异常时定位问题。


19. diag_other.py（V9.3.1 新增，按数据源重组）
    作用：其他接口诊断，测试腾讯/新浪/百度/巨潮等接口。
    运行：python tests\diag_other.py
    覆盖接口（共5个）：
      - get_tencent_quote（腾讯行情）
      - get_sina_financial_report（新浪财报）
      - baidu_kline_full（百度K线，deprecated）
      - get_strategic_announcements（巨潮公告）
      - get_hsgt_macro_flow（沪深港通宏观资金流）
    何时需要：
      - 验证腾讯/新浪/百度/巨潮等第三方数据源连通性。


20. test_em_rate_limit.py（V8.6 新增）
    作用：东财限流阈值压力测试，验证东财风控是按域名独立限流还是按IP总请求限流。
    运行：python tests\test_em_rate_limit.py
    测试三组对照实验：
      ① 基准测试：单域名 push2，1秒间隔，验证安全基线；
      ② 交叉测试：三域名轮询，总QPS≈3，验证是否触发限流；
      ③ 串行测试：三域名串行，总QPS≈1，作为对照组。
    安全机制：
      - 渐进式启动（从低频率到目标频率）；
      - 熔断机制（检测到429立即停止）；
      - 每组测试后5分钟冷却。
    何时需要：
      - 想验证东财限流阈值，调整限流参数前；
      - 怀疑风控策略变化时；
      - 评估性能优化空间时。


21. diag_issues.py（V8.5 新增，V8.7 更新）
   作用：专项问题验证脚本，用于复现和验证特定 bug 修复。
   运行：python tests\diag_issues.py
   覆盖：
     - 指数涨跌幅数据验证（上证指数、深证成指、创业板指、科创50）；
     - 板块排名验证（get_stock_sector_rank 返回数据结构）；
     - 行业对标验证（get_industry_peers 同行股票列表）；
     - 龙虎榜数据验证（席位分析、机构资金）；
     - 多评委评分验证（calculate_multi_school_scores 返回数据结构）。
   何时需要：
     - 开发期间验证特定 bug 修复是否生效；
     - 回归测试时确认已知问题没有复发。


22. test_f10_chapters_integration.py（V9.1 新增）
   作用：F10 章节集成测试，验证 3 个报告脚本（med/lng/ful）中的 F10 新章节是否正确渲染。
   运行：python tests\test_f10_chapters_integration.py
        （必须在项目根目录运行，脚本会自动将根目录加入 sys.path）
   覆盖：
     - med 报告：财务深度/股东行为/主营构成 3 章节；
     - lng 报告：财务深度/股东行为/治理结构/研发创新/主营构成 5 章节；
     - ful 报告：全部 6 个 F10 章节（含异动/治理）。
   测试机制：
     - 实际生成 3 份报告（med/lng/ful，使用 600519 茅台）；
     - 断言报告中包含章节标题关键字（如「财务深度分析」）。
   何时需要：
     - 修改 render_f10_chapter 后；
     - 修改报告脚本的 F10 章节集成位置后；
     - 升级 tdx_client.py 中 F10 函数后做回归验证。
   注意：
     - 测试需要联网（TDX + HTTP），单次运行约 5-10 分钟；
     - 测试期间会写入临时 .txt 报告文件（tempfile 自动生成）；
     - 若 TDX 服务器不可达，章节会渲染为「(数据获取失败)」但不会断言失败。
   V9.1 变更：已移除数据质量核查附录的断言（数据质量稳定，附录功能已下线）；
              已移除 sht 报告测试（sht 移除了 risk_warning 章节）。


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【速查：日常使用指南】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  想跑单元测试，确认近期修改没有引入回归：
      cd 到项目根目录
      pytest tests/ -v

  想只跑缓存层测试（V8.4 新增）：
      pytest tests/test_cache.py -v

  想只跑缓存交叉验证测试（V9.2 新增）：
      pytest tests/test_cache_verify.py -v

  想只跑交易日历测试（V8.4 新增）：
      pytest tests/test_calendar.py -v

  想只跑评分逻辑测试（V8.4 新增）：
      pytest tests/test_scoring.py -v

  想只跑策略配置测试（V8.4 新增）：
      pytest tests/test_strategy.py -v

  短线脚本龙虎榜全是 0 / 想判断数据接口是否正常：
      python tests\diag_dragon_tiger.py
      python tests\diag_dragon_tiger.py 301217 600036

  脚本报 TdxClient 连接失败 / K 线返回空：
      python tests\diagnose_tdx.py

  K线全部N/A或返回空，怀疑选到了假数据服务器（V9.3.2 新增）：
      python tests\diag_tdx_hosts_test.py
      # 逐个测试52个TDX服务器的K线可用性

  需要查看TDX原始TCP响应，确认服务器是否返回假数据（V9.3.2 新增）：
      python tests\diag_tdx_final.py
      # 捕获 header + body，对比 ret_count 与实际数据量

  想确认 GD 上传逻辑没被改坏：
      pytest tests\test_gd_uploader.py -v

  想一次性验证所有数据源接口：
      python tests\diag_datasource.py

  想按数据源分类测试（V9.3.1 新增）：
      # TDX基础接口（行情/K线/资金流/财务）
      python tests\diag_tdx_basic.py
      # TDX F10接口（财务分析/股东研究/股本结构等）
      python tests\diag_tdx_f10.py
      # TDX板块接口（所属板块/板块列表/板块成员）
      python tests\diag_tdx_board.py
      # 东财接口（研报/新闻/股东/北向/融资融券等14个）
      python tests\diag_eastmoney.py
      # 同花顺接口（热点原因/热榜）
      python tests\diag_ths.py
      # 其他接口（腾讯/新浪/百度/巨潮）
      python tests\diag_other.py

  想只跑 TDX 财务/资金流/分红接口测试（在 diag_datasource.py 中包含）：
      python tests\diag_datasource.py
      （测试TDX财务信息、TDX资金流、TDX分红除权三项）

  想只跑 TDX MacClient 测试（在 diag_tdx_board.py 中包含）：
      python tests\diag_tdx_board.py
      （测试MacClient连接、所属板块、板块成员三项）

  想验证东财限流阈值（谨慎使用，有封禁风险）：
      python tests\test_em_rate_limit.py

  想验证特定 bug 修复是否生效：
      python tests\diag_issues.py

  想验证 F10 章节和附录在报告中的集成（V9.1 新增，需联网，约 5-10 分钟）：
      python tests\test_f10_chapters_integration.py


更新时间：2026-07-09（V9.3.2 TDX K线假数据防护）
