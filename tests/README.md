# tests 目录说明

本目录包含单元测试、组件集成测试与显式标记的真实网络测试。测试通过 `scripts/run_tests.ps1` 运行；默认模式拦截/排除 `real_network` 用例。

## 当前模块清单

| 区域 | 测试模块数 | 覆盖范围 | 详细清单 |
|:---|---:|:---|:---|
| `core/` | 16 | 核心门面、缓存、日历、类型契约、fallback、评分和技术指标 | [`core/README.md`](core/README.md) |
| `data/` | 11 | ZHB、TDX、Eastmoney、KPL、网络、解禁单位和回测快照 | [`data/README.md`](data/README.md) |
| `infra/` | 12 | 调度器、字段完整性/命名、依赖预检、dry-run 写入边界、F10、外部 API 与 GD | [`infra/README.md`](infra/README.md) |
| `reports/` | 6 | 报告 Runner、流水线、策略与章节契约 | `reports/` 测试目录 |
| 根目录 | 16 | 碰撞/字段登记、采集探针、依赖适配、临时目录与基础工具契约 | 本文件下方列出 |
| **合计** | **61** | 参数化用例展开前的测试模块数 | — |

根目录测试：

- `test_apply_collision_adjudications.py`、`test_collide.py`、`test_collision_dates.py`、`test_collision_topic_scripts.py`：碰撞候选、日期口径、专题脚本与人工定案。
- `test_field_registry_api.py`、`test_gen_field_dict.py`、`test_reconcile_field_registry.py`、`test_source_lineage_api.py`：字段登记、生成视图、状态同步与来源谱系。
- `test_capture_field_probe.py`：采集源请求参数、日期校验、状态和调用边界。
- `test_dependency_adapter_compat.py`：Levistock 实际方法契约与 AxData 本地 ZHB ZIP 读取。
- `test_degradation_contract.py`：多级数据源降级契约。
- `test_project_temp.py`：项目临时目录默认位置与显式覆盖。
- `test_sc_ta_core.py`、`test_seat_db_audit_fix.py`、`test_symbol_norm.py`：技术指标、龙虎榜席位与代码归一化。
- `test_v310_sources.py`：数据源兼容性、完整性与重试回归。

> **最近离线验证（2026-10-08）**：默认 `all` 模式共收集 768 项，720 passed、1 skipped、47 个 `real_network` 用例被排除（125.45 秒）。测试集合会随参数化和用例增减而变化，结果以当次运行输出为准。

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

测试文件命名为 `test_<层>_<主题>.py`，按 `data/`、`core/`、`infra/`、`reports/` 归类；新增自定义 marker 前先在 `pyproject.toml` 注册。真实网络测试必须标记 `@pytest.mark.real_network`。默认、单模块和表达式模式均不启用真实网络；`-Mode real` 会临时设置 `REAL_NETWORK=1`，只运行带标记的用例，结束后恢复调用环境。
