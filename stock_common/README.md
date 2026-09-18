# stock_common/ — 核心公共包(V17.3 演进)

> 定位: 报告脚本与 core/ 之上的公共业务模块——网络传输层、数据源查询、评分/风险/技术指标、报告运行基类、日历、工具函数。
> 报告脚本与 main.py 通过 `from stock_common import X` 引用(包入口统一导出, __all__ 250+ 项)。

## 目录结构(按职责分组)

### 网络与容错
| 模块 | 职责 |
|:---|:---|
| sc_network.py | 统一传输层: 分域限流/令牌桶/封禁冷却/跨进程文件锁/UA/Referer |
| sc_fault_tolerance.py | 容错层: TokenBucket / CircuitBreaker / RandomUAPool |
| sc_fuyao.py | 同花顺官方金融数据 API(fuyao)适配器 |
| sc_ftshare.py | FTShare MCP 工具封装(千股千评/董监高/商誉/质押等) |

### 数据源查询(子包 sc_datasource/)
> **V17.2 起 `sc_datasource.py` 单文件已拆分为 `sc_datasource/` 子包**(拆分前单文件备份见 `docs/backups/_sc_datasource_singlefile_backup.py`)。`__init__.py` 统一再导出, 对外 `from stock_common.sc_datasource import X` 接口不变。

| 子模块 | 职责 |
|:---|:---|
| sc_datasource/__init__.py | 子包入口: 统一再导出全部数据源函数(对外兼容旧 `sc_datasource.py` 命名空间) |
| sc_datasource/_shared.py | 跨片段共享可变状态(单实例), 常量/字段段定义 |
| sc_datasource/_eastmoney.py | 东财接口(接口映射/多域健康矩阵/资金流/板块/研报等) |
| sc_datasource/_financials.py | 财务数据(利润表/资产负债表/现金流量表/估值) |
| sc_datasource/_holders.py | 股东/股本/十大股东/限售解禁 |
| sc_datasource/_industry.py | 行业映射与成分(生成 cache/em_industry_*.json) |
| sc_datasource/_pools.py | 涨停池/炸板池/跌停池/重点监控(push2ex) |
| sc_datasource/_quotes.py | 实时行情/快照/竞价/概念(含 get_concept_from_zhb, V17.3 改引 core._accessors) |
| sc_datasource/_zhb.py | ZHB 行情衍生字段(成交额/年至今涨跌/股息率/主力净额/连板天数等, V17.3 改引 core._accessors) |
| sc_datasource/_misc.py | 其他零散数据源(互动易/新闻/公告等) |
| sc_datasource/_official_backup.py | 单文件时代的官方备份片段(参考用, 不主动调用) |

### 其它数据源/缓存模块(顶层)
| 模块 | 职责 |
|:---|:---|
| sc_kpl.py | 涨停池/炸板池/跌停池/重点监控(push2ex) |
| sc_plate_rot.py | 板块轮动数据 |
| sc_capital_cache.py | 全局股本缓存(90 天 TTL, schema 版本校验) |
| md_render.py | **报告 md 渲染转换器(V17.0.1)**——标题/分隔线/F10 边框表/空格表数据驱动切分→Markdown; 5 脚本写尾统一入口 |
| sc_kline_cache.py | K线缓存(进程内) |
| stock_calendar.py | 交易日历(holidays/workdays 字典 + ZHB 补充, 含 CLI 更新入口) |
| seat_db.py / seats.json | 龙虎榜营业部席位数据库 |

### 分析与评分
| 模块 | 职责 |
|:---|:---|
| sc_schema.py | 字段元数据层(FieldSpec + Enum + normalize_at_boundary) |
| sc_scoring.py | 统一评分接口(ScoreData/ScoreResult) |
| sc_technical.py | 技术指标引擎(MACD/RSI/BOLL/KDJ) |
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
- **sc_datasource ↔ core 依赖全部为函数体内懒 import**(防循环依赖; V17.3 进一步将跨边界访问器抽至 `core/_accessors.py` 叶子, 导入期循环已根治)。
- **V17.0 状态**: sc_zhb.py(连续 ZHB 回溯)已删除(V17.0 S1 死代码清理, 2026-08-13); **V17.2** 将 `sc_datasource.py` 拆分为 `sc_datasource/` 子包。
