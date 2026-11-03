# tests 目录说明

本目录包含单元测试、组件集成测试与显式标记的真实网络测试。测试通过 `scripts/run_tests.ps1` 运行；默认模式拦截外网并排除 `real_network` 用例。每个测试模块使用项目 `.tmp/` 下的独立 SQLite 缓存，避免测试清理或写入项目真实缓存。

## 当前模块清单

| 区域 | 测试模块数 | 覆盖范围 | 详细清单 |
|:---|---:|:---|:---|
| `core/` | 20 | 核心门面、缓存、日历、类型契约、fallback、评分和技术指标 | [`core/README.md`](core/README.md) |
| `data/` | 23 | ZHB、TDX/ELTDX、Eastmoney、KPL、网络、解禁单位、指数、EPS 预测缓存、财务日历和异步财报兜底 | [`data/README.md`](data/README.md) |
| `infra/` | 13 | 调度器、字段完整性/命名、依赖预检、dry-run 写入边界、F10、外部 API 与 GD | [`infra/README.md`](infra/README.md) |
| `reports/` | 16 | 报告 Runner、流水线、策略、章节契约、财务精度、Markdown 输出、正文辅助逻辑、指数映射和快照失败处理 | [`reports/README.md`](reports/README.md) |
| 根目录 | 54 | 碰撞/字段登记、采集探针、来源身份核验、来源语义质量、依赖适配、AxData 摘要与维护工具、网络和临时目录隔离 | 本文件下方列出 |
| **合计** | **126** | 参数化用例展开前的测试模块数 | — |

## 验收入口

完整静态检查和离线回归使用 `scripts/run_offline_checks.ps1`；定向测试使用 `scripts/run_tests.ps1`。默认策略排除 `real_network` 用例。此文件不保存“最近一次”测试计数，避免数字与后续执行脱节；验收结果以当次命令输出为准。
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
| 报告数值与来源口径 | `reports/test_reports_financial_precision.py` |
| Markdown 输出边界 | `reports/test_report_markdown_output.py`（共享写入器）、`reports/test_architecture_output_contracts.py`（五大生成器实际离线输出）、`reports/test_reports_chapter_omission.py`（SHT 章节保护） |

共享 Markdown 写入器与五个 Runner 的输出路径已有契约测试；五个生成器各自的完整正文快照仍未覆盖。修改正文时应检查对应渲染逻辑与现有章节契约用例，完整正文快照纳入架构整改计划。

## 运行方式

```powershell
.\scripts\run_tests.ps1                                      # 全部离线测试
.\scripts\run_tests.ps1 -Mode skip_real                      # 显式排除真实网络用例
.\scripts\run_tests.ps1 -Mode module -Path tests/core/test_core_routing.py
.\scripts\run_tests.ps1 -Mode expression -Expression "test_cache"
.\scripts\run_tests.ps1 -Mode real                           # 仅运行 @pytest.mark.real_network 用例
```

测试文件命名为 `test_<层>_<主题>.py`，按 `data/`、`core/`、`infra/`、`reports/` 归类；新增自定义 marker 前先在 `pyproject.toml` 注册。真实网络测试必须标记 `@pytest.mark.real_network`。默认、单模块和表达式模式均不启用真实网络；`-Mode real` 会临时设置 `REAL_NETWORK=1`，只运行带标记的用例，结束后恢复调用环境。
