# stock_common/ — 公共业务与数据适配层

> 定位: 报告脚本与 core/ 之上的公共业务模块——网络传输、数据源适配、报告数据富化与渲染、评分/风险/技术指标、日历和工具函数。
> 报告脚本与 main.py 通过 `from stock_common import X` 引用；公共导出由包入口的 `__all__` 明确列出。

## 目录结构(按职责分组)

### 网络与容错
| 模块 | 职责 |
|:---|:---|
| sc_network.py | 统一传输层: 分域限流/令牌桶/封禁冷却/跨进程文件锁/UA/Referer |
| sc_fault_tolerance.py | 容错层: TokenBucket / CircuitBreaker / RandomUAPool |
| sc_fuyao.py | 同花顺官方金融数据 API(fuyao)适配器 |

### 数据源查询(子包 sc_datasource/)
> **V17.2 起 `sc_datasource.py` 单文件已拆分为 `sc_datasource/` 子包**。拆包前快照已从当前工作树清理，历史副本仍保存在 Git 提交 `e868de5` 中。`__init__.py` 统一再导出, 对外 `from stock_common.sc_datasource import X` 接口不变。

| 子模块 | 职责 |
|:---|:---|
| sc_datasource/__init__.py | 子包入口: 统一再导出全部数据源函数(对外兼容旧 `sc_datasource.py` 命名空间) |
| sc_datasource/_shared.py | 跨片段共享可变状态(单实例), 常量/字段段定义 |
| sc_datasource/_axdata.py | AxData 请求适配；由采集器按核验策略调用，不持有日常验证状态 |
| sc_datasource/_datacenter.py | 东财数据中心 sync/async 端点处理；由 `_eastmoney.py` 注入共享请求/重试函数，不持有网络状态 |
| sc_datasource/_eastmoney.py | 东财接口(接口映射/多域健康矩阵/资金流/板块/研报等) |
| sc_datasource/_financials.py | 财务数据(利润表/资产负债表/现金流量表/估值) |
| sc_datasource/_holders.py | 股东/股本/十大股东/限售解禁 |
| sc_datasource/_industry.py | 行业映射与成分(生成 cache/em_industry_*.json) |
| sc_datasource/_pools.py | 涨停池/炸板池/跌停池/重点监控(push2ex) |
| sc_datasource/_quotes.py | 实时行情/快照/竞价/概念(含 get_concept_from_zhb, V17.3 改引 core._accessors) |
| sc_datasource/_zhb.py | ZHB 行情衍生字段(成交额/年至今涨跌/股息率/主力净额/连板天数等, V17.3 改引 core._accessors) |
| sc_datasource/_misc.py | 其他零散数据源(互动易/新闻/公告等) |
| sc_datasource/_convertible.py | 可转债条款、转股价值与溢价率 |
| sc_datasource/_etf.py | ETF 份额数据 |
| sc_datasource/_events.py | 业绩预告、调研、增减持、质押、新股申购等事件 |
| sc_datasource/_futures_sina.py | 新浪期货日 K 数据 |
| sc_datasource/_macro.py | 宏观指标、利率与宏观日历 |
| sc_datasource/_news_wscn_cctv.py | 华尔街见闻与央视新闻数据 |
| sc_datasource/_research_sina.py | 新浪研报列表（第二来源） |
| sc_datasource/_sse_e_interaction.py | 上证 e 互动问答 |
| sc_datasource/_st_list.py | 全市场 ST / *ST 名单 |
| sc_datasource/_ticks.py | 腾讯逐笔成交 |
| sc_datasource/_v39_compat.py | 上游数据适配器共用的兼容 helper |
| sc_datasource/_official_backup.py | 官方数据兜底：沪深两融与北交所行情（由 `_financials.py` / `_quotes.py` 调用） |

### 其它数据源/缓存模块(顶层)
| 模块 | 职责 |
|:---|:---|
| sc_kpl.py | 涨停池/炸板池/跌停池/重点监控(push2ex) |
| sc_plate_rot.py | 板块轮动数据 |
| sc_capital_cache.py | 全局股本缓存(90 天 TTL, schema 版本校验) |
| md_render.py | 报告 Markdown 转换器：标题、分隔线、F10 边框表与空格表切分 |
| sc_render.py | 报告共享片段渲染器，集中复用多评委评分等报告输出 |
| sc_kline_cache.py | K 线与筹码分布跨进程文件缓存；按交易日历在下一数据交易日 09:30 失效，日历不可用时回退 24 小时 |
| stock_calendar.py | 交易日历(holidays/workdays 字典 + ZHB 补充, 含 CLI 更新入口) |
| seat_db.py / seats.json | 龙虎榜营业部席位数据库 |
| _temp.py | 配置仓库 `.tmp/` 为项目进程及子进程临时目录，支持 `ASTOCK_TEMP_DIR` 覆盖 |
| symbol_norm.py | 股票代码与市场标识归一化 |
| enrich_helpers.py | 报告数据补充与归一化辅助函数 |
| sc_market_signals.py | IPO、ETF、研报、新闻、互动问答和风险名单等市场级报告片段 |

### 分析与评分
| 模块 | 职责 |
|:---|:---|
| sc_schema.py | 字段元数据层(FieldSpec + Enum + normalize_at_boundary) |
| sc_scoring.py | 统一评分接口(ScoreData/ScoreResult) |
| sc_technical.py | 技术指标引擎(MACD/RSI/BOLL/KDJ) |
| sc_ta_core.py | 通达信/同花顺公式原语，如 REF、SUM、EMA、CROSS |
| sc_risk.py | 风险扫描引擎(9 项清单) |
| sc_snapshot.py | 评分快照(SnapshotProxy, 跨脚本共享) |
| analyze_history.py | 评分快照分析与趋势背离检测 |

### 报告运行
| 模块 | 职责 |
|:---|:---|
| sc_report_runner.py | BaseReportRunner 基类(批量流水线/上传/日志) |
| f10_parser.py | F10 数据解析 |
| sc_utils.py | 工具函数(_safe_float/is_limit_up/limit_pct_for/board_type 等) |
| env_setup.py | ensure_utf8_stdio(全局 UTF-8 输出强制) |

### 配置与数据
| 文件 | 用途 |
|:---|:---|
| strategy_config.yaml | 策略阈值配置(报告模块模块级加载) |
| keywords_config.yaml | 关键词配置 |
| cache/share_capital.json | 股本缓存(运行时生成, 不入库) |

## 关键约定

- **包入口 `__init__.py`** 是唯一对外门面: 所有公共函数经 `from stock_common import X` 导入;
  `__all__` 与 from-import 块必须保持同步(修改导出必查两份)。
- **sc_datasource ↔ core 依赖保持函数体内懒 import**，跨边界访问器集中在 `core/_accessors.py`，避免导入期循环。
- 历史模块 `sc_zhb.py` 已删除；原 `sc_datasource.py` 已按来源拆分为 `sc_datasource/` 子包。当前职责以目录中的实际模块和 [`sc_datasource/README.md`](sc_datasource/README.md) 为准。
