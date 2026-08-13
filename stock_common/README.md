# stock_common/ — 核心公共包(V12.0+ 演进)

> 定位: 报告脚本与 core/ 之上的公共业务模块——网络传输层、数据源查询、评分/风险/技术指标、报告运行基类、日历、工具函数。
> 报告脚本与 main.py 通过 `from stock_common import X` 引用(包入口统一导出, __all__ 250+ 项)。

## 目录结构(按职责分组)

### 网络与容错
| 模块 | 职责 |
|:---|:---|
| sc_network.py | 统一传输层: 分域限流/令牌桶/封禁冷却/跨进程文件锁/UA/Referer |
| sc_fault_tolerance.py | 容错层: TokenBucket / CircuitBreaker / RandomUAPool |
| sc_fuyao.py | 同花顺官方金融数据 API(fuyao)适配器 |
| sc_ths.py | THS SDK 统一适配器(凭据 credentials/ths_credentials.json) |

### 数据源查询
| 模块 | 职责 |
|:---|:---|
| sc_datasource.py | 数据源查询模块(100+ 函数: 行业映射/同业对比/资金流/龙虎榜/解禁/研报等) |
| sc_kpl.py | 涨停池/炸板池/跌停池/重点监控(push2ex) |
| sc_plate_rot.py | 板块轮动数据 |
| sc_capital_cache.py | 全局股本缓存(90 天 TTL, schema 版本校验) |
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
- **sc_datasource ↔ core 依赖全部为函数体内懒 import**(防循环依赖)。
- **V17.0 状态**: sc_zhb.py(连续 ZHB 回溯)为 0 调用死代码, 计划在 V17.0 S1 删除(本表未列)。
