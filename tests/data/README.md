# tests/data/ — 数据源层测试

> 本目录归并**数据从哪来**的 pytest 用例, 覆盖 ZHB / TDX / 东财 / 网络传输 / 预取等底层数据源, 对应 `stock_common/sc_datasource/` 与 `core/tdx_client.py` / `core/zhb_client.py` / `stock_common/sc_network.py`。
> 文件清单与逐文件定位见父目录 [`../README.md`](../README.md); 本文件仅作本层速查。

## 文件与职责(7)

| 文件 | 职责 |
|:---|:---|
| test_data_zhb.py | ZHB 包解析 / 字段破解 / 行业段过滤 |
| test_data_tdx.py | TDX TCP / 适配器 / 服务器白名单(None=接口失败 vs []=真无分红) |
| test_data_eastmoney.py | 东财接口按域名健康度矩阵(全 real_network) |
| test_data_em_board_members.py | 东财 clist 板块成分股字段映射回归 |
| test_data_em_fund_flow_tiers.py | 东财资金流四档层级回归(V17.0.16) |
| test_data_network.py | 令牌桶限流 / 熔断器 / 封禁冷却(核心防线) |
| test_data_prefetch.py | sht 批量行情预取映射 / 单位换算 / 缓存命中(V16.4.0) |

## 运行

```powershell
.\scripts\run_tests.ps1 -Mode module -Path tests/data/test_data_zhb.py
.\scripts\run_tests.ps1 -Mode real   # 仅真网络测试(需 REAL_NETWORK=1)
```
