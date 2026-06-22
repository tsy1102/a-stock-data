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


5. test_calendar.py（V8.4 新增）
   作用：测试 stock_common.py 交易日历判断函数。
   覆盖：
   - is_trading_day()：普通工作日（周一~五）、周末、节假日、调休日；
   - get_market_status()：盘前/上午/午休/下午/盘后/休市各状态；
   - 已知节假日验证：元旦、春节、劳动节、国庆节、端午、中秋；
   - 调休日验证：节假日前后补班日；
   - 边界情况：None / 超范围日期 / datetime 输入。
   何时需要：修改了交易日历逻辑或 chinese-calendar 更新后。


6. test_scoring.py（V8.4 新增）
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


7. test_strategy.py（V8.4 新增）
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

8. diag_dragon_tiger.py
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


9. diagnose_tdx.py
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


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【已清理的文件】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

以下文件在本次整理中已被清理，仅供参考：

  - _probe_date_format.py：一次性调试，对比 TRADE_DATE 字段的引号
    写法（单引号 vs 双引号）。问题已在 stock_common.py 中统一为
    单引号后，此文件无需保留。

  - _probe_free_date.py：一次性调试，对比限售解禁 FREE_DATE 字段
    的引号写法。同上，问题已修复，删除。

  - test_dragon_tiger_diagnose.py：龙虎榜问题定位过程中的脚本，
    与 diag_dragon_tiger.py 功能重复，删除。

  - test_dragon_tiger_final.py：龙虎榜修复后的验证脚本，验证完成即
    无保留价值，删除。

  - test_asyncio.py：v7.5 开发期间评估 asyncio 可行性的 POC 脚本，
    不测试任何当前代码，删除。

  - diagnose_throttle_and_pools.py：开发期间测试东财 datacenter
    并发参数 / 同花顺强势股池大小的脚本。结论（并发上限、合理池
    大小）已经固化到各业务脚本的代码中，不再需要反复运行，删除。

  - test_report_formatters.py：测试已被重构掉的 report_formatters
    模块，运行会报 ImportError，删除。

  - _probe_dt.py：位于项目根目录的一次性调试脚本，反复对比龙虎榜
    接口中 TRADE_DATE 字段不同写法（带引号/不带/单引号/横杠格式）
    的响应。问题已解决，调试完成后无需保留，删除。


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【速查：日常使用指南】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  想跑单元测试，确认近期修改没有引入回归：
      cd 到项目根目录
      pytest tests/ -v

  想只跑缓存层测试（V8.4 新增）：
      pytest tests/test_cache.py -v

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

  想确认 GD 上传逻辑没被改坏：
      pytest tests\test_gd_uploader.py -v


更新时间：2026-06-22（V8.4）
