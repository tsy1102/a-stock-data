# tests 目录说明

本目录包含单元测试、组件集成测试与显式标记的真实网络测试。测试通过 `scripts/run_tests.ps1` 运行；默认模式拦截/排除 `real_network` 用例。

## 当前模块清单

| 区域 | 测试模块数 | 覆盖范围 | 详细清单 |
|:---|---:|:---|:---|
| `core/` | 16 | 核心门面、缓存、日历、类型契约、fallback、评分和技术指标 | [`core/README.md`](core/README.md) |
| `data/` | 10 | ZHB、TDX、Eastmoney、KPL、网络、解禁单位和回测快照 | [`data/README.md`](data/README.md) |
| `infra/` | 9 | 调度器、字段完整性/命名、依赖预检、dry-run 写入边界、F10、外部 API 与 GD | [`infra/README.md`](infra/README.md) |
| `reports/` | 5 | 报告 Runner、流水线、策略与章节契约 | [`reports/README.md`](reports/README.md) |
| 根目录 | 7 | 采集探针、降级契约、技术指标、席位、代码归一化、来源兼容和依赖适配 | 本文件下方列出 |
| **合计** | **52** | 参数化用例展开前的测试模块数 | — |

根目录测试：

- `test_capture_field_probe.py`：采集源请求参数与调用边界。
- `test_dependency_adapter_compat.py`：Levistock 实际方法契约与 AxData 本地 ZHB ZIP 读取。
- `test_degradation_contract.py`：多级数据源降级契约。
- `test_sc_ta_core.py`：技术指标基础运算。
- `test_seat_db_audit_fix.py`：龙虎榜席位评分降级。
- `test_symbol_norm.py`：股票代码归一化。
- `test_v310_sources.py`：数据源兼容性与回归。

> **最近离线验证（2026-10-08）**：共收集 747 项，699 passed、1 skipped、47 deselected（125.89 秒）；`real_network` 未运行。测试集合会随参数化和用例增减而变化，结果以当次运行输出为准。

## 按问题定位

| 问题 | 测试位置 |
|:---|:---|
| 字段路由、行情 fallback 顺序 | `core/test_core_routing.py`、`core/test_quote_fallback_order.py` |
| 类型边界与 schema | `core/test_core_type_contracts.py`、`core/test_core_schema.py` |
| 缓存、股本与解禁单位 | `core/test_core_cache.py`、`core/test_core_capital_cache.py`、`data/test_lockup_units.py` |
| ZHB 解析或回测快照 | `data/test_data_zhb.py`、`data/test_backtest_zhb_snapshot.py` |
| 东财 / KPL 数据源 | `data/test_data_eastmoney.py`、`data/test_data_kpl.py` |
| 字段登记与命名守护 | `infra/test_field_completeness_scopes.py`、`infra/test_lint_field_names.py`、`infra/test_ulist_subdict.py` |
| 子进程调度结果 | `infra/test_main_scheduler.py` |
| 报告流水线与缺章 | `reports/test_reports_pipeline.py`、`reports/test_reports_chapter_omission.py` |

报告正文渲染输出仍没有专门的端到端快照测试；修改正文时应检查对应渲染逻辑与现有章节契约用例。

## 运行方式

```powershell
.\scripts\run_tests.ps1                                      # 全部离线测试
.\scripts\run_tests.ps1 -Mode skip_real                      # 显式排除真实网络用例
.\scripts\run_tests.ps1 -Mode module -Path tests/core/test_core_routing.py
.\scripts\run_tests.ps1 -Mode expression -Expression "test_cache"
.\scripts\run_tests.ps1 -Mode real                           # 仅运行 @pytest.mark.real_network 用例
```

测试文件命名为 `test_<层>_<主题>.py`，按 `data/`、`core/`、`infra/`、`reports/` 归类；新增自定义 marker 前先在 `pyproject.toml` 注册。真实网络测试必须标记 `@pytest.mark.real_network`，并通过 `-Mode real` 显式运行。
