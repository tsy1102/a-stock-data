# tests/core/ — 统一层 / 服务层测试

> 本目录归并**核心统一层与公共服务**的 pytest 用例, 对应 `core/` 包(`data_provider` / `stock_cache` / `config` / `zhb_*` 等) 与 `stock_common` 的 schema / scoring / technical / risk / utils。
> 文件清单与逐文件定位见父目录 [`../README.md`](../README.md); 本文件仅作本层速查。

## 文件与职责(20)

| 文件 | 职责 |
|:---|:---|
| test_core_schema.py | `CanonicalStockData` 强类型合约 / 字段归一化(V13.0/13.1) |
| test_core_cache.py | 统一缓存层 `stock_cache`(@cached / SQLite / TTL / cross_verify) |
| test_core_blob_cache.py | V17.0.15 通用对象磁盘缓存 |
| test_core_capital_cache.py | 股本缓存单位防御 + schema 版本失效(V16.4.0) |
| test_core_calendar.py | A股交易日历(权威日历 + ZHB 补班) |
| test_core_routing.py | 字段路由矩阵 / 断路器降级分类(V12.6) |
| test_core_scoring.py | 评分系统 `ScoreData` / `calculate_score` |
| test_core_technical.py | 技术指标 / 风险引擎(V16.1) |
| test_core_cyq.py | 筹码分布 CYQ 计算(V17.0.14) |
| test_core_seat.py | 龙虎榜席位三层匹配(V16.3 E M13) |
| test_core_tencent_volume_unit.py | 腾讯行情成交量单位(科创板 688 = 股) |
| test_core_utils.py | 公共工具(`_safe_float` / `is_limit_up` 等) |
| test_core_type_contracts.py | 公共类型边界与类型契约回归 |
| test_quote_fallback_order.py | 行情来源 fallback 顺序契约 |
| test_canonical_consumer_coverage.py | 统一层属性消费覆盖与别名解析 |
| test_canonical_metadata.py | 字段级来源日期、时间锚与元数据归一化 |
| test_unified_metadata_and_tdx_calendar.py | 行情来源旁路元数据及 TDX 交易日归属 |
| test_zhb_field_freshness.py | ZHB A/B/C/D 字段新鲜度与交易日延迟 |
| test_sec_type_exposure.py | 证券类型→板块标签(DEBT-016 锁固) |
| test_eltdx_adapter.py | eltdx 报告包下载返回值类型与空载荷边界 |

## 运行

```powershell
.\scripts\run_tests.ps1 -Mode module -Path tests/core/test_core_schema.py
.\scripts\run_tests.ps1 -Mode skip_real   # 全部离线
```
