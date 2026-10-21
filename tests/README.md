# tests 目录说明

本目录包含单元测试、组件集成测试与显式标记的真实网络测试。测试通过 `scripts/run_tests.ps1` 运行；默认模式拦截外网并排除 `real_network` 用例。每个测试模块使用项目 `.tmp/` 下的独立 SQLite 缓存，避免测试清理或写入项目真实缓存。

## 当前模块清单

| 区域 | 测试模块数 | 覆盖范围 | 详细清单 |
|:---|---:|:---|:---|
| `core/` | 19 | 核心门面、缓存、日历、类型契约、fallback、评分和技术指标 | [`core/README.md`](core/README.md) |
| `data/` | 17 | ZHB、TDX/ELTDX、Eastmoney、KPL、网络、解禁单位、指数、EPS 预测缓存、财务日历和异步财报兜底 | [`data/README.md`](data/README.md) |
| `infra/` | 12 | 调度器、字段完整性/命名、依赖预检、dry-run 写入边界、F10、外部 API 与 GD | [`infra/README.md`](infra/README.md) |
| `reports/` | 14 | 报告 Runner、流水线、策略、章节契约、财务精度、Markdown 输出、正文辅助逻辑、指数映射和快照失败处理 | [`reports/README.md`](reports/README.md) |
| 根目录 | 47 | 碰撞/字段登记、采集探针、来源身份核验、来源语义质量、依赖适配、AxData 摘要与维护工具、网络和临时目录隔离 | 本文件下方列出 |
| **合计** | **108** | 参数化用例展开前的测试模块数 | — |

## 最近完整执行

2026-10-21（Python 3.12.10，`run_offline_checks.ps1`）：收集 1,250 项，离线执行 1,198 项，其中 1,197 通过、1 跳过；52 个 `real_network` 用例按默认策略排除，耗时 33.96 秒。真实网络测试未运行；语法 262 个文件、Mypy 232 个源文件、Black API 247 个文件且 0 格式差异；AxData 摘要、数据访问、字典同步、Canonical contract 与 registry parity 闸门均通过。

根目录测试：

- `test_apply_collision_adjudications.py`、`test_collide.py`、`test_collision_dates.py`、`test_collision_topic_scripts.py`：碰撞候选、日期口径、专题脚本与人工定案。
- `test_field_registry_api.py`、`test_registry_parity.py`、`test_gen_field_dict.py`、`test_reconcile_field_registry.py`、`test_reconcile_field_registry_quality.py`、`test_field_registry_semantic_quality.py`、`test_field_source_quality_audit.py`、`test_source_lineage_api.py`：字段登记、严格 parity、语义质量门、元数据审计、状态同步与来源谱系。
- `test_refresh_field_registry_projection.py`、`test_field_evidence_coverage.py`：生成视图 parity 与每日证据覆盖。
- `test_capture_field_probe.py`、`test_capture_catalog.py`、`test_capture_source_coverage.py`、`test_sina_raw_adapters.py`、`test_audit_field_completeness_inputs.py`：采集源路由与字段生命周期覆盖、采集目录契约、Sina 扩展适配、日期校验、状态/调用边界，以及全样本双向字段归档审计。
- `test_check_em_health.py`：东财单次低频探测的请求约束、风控族停止、响应结构摘要及跳过/失败分类。
- `test_extract_registry_alignment.py`：逐源字段解析中的分组对齐、组合单位和证据优先级。
- `test_dependency_adapter_compat.py`：Levistock 实际方法契约与 AxData 本地 ZHB ZIP 读取。
- `test_ftshare_rest.py`、`test_ftshare_collision_anchor.py`：FTShare REST 日常采集契约、凭证隔离、限流/403/429 熔断、报价日期校验、代码归一化及官方契约锚 L1-C 行为。
- `test_axdata_daily_validation.py`、`test_axdata_crosswalk_summary.py`、`test_levistock_daily_probe.py`、`test_levistock_daily_validation.py`、`test_levistock_rate_limit.py`：AxData 摘要完整性与候选源每日核验、日期/数据阶段、同步/异步跨进程限流与 OS 锁崩溃释放。
- `test_axdata_capture_identity.py`、`test_axdata_capture_policy.py`、`test_axdata_collision_suppression.py`：AxData 生产路由退出、三交易日复验、限流熔断与默认碰撞过滤。
- `test_collision_research_state.py`：探索候选跨轮保存、幂等和历史继承。
- `test_collision_candidate_reviews.py`、`test_collision_math.py`、`test_collision_state.py`：稳定候选身份、人工处置历史、批量重复归并、证据引用校验、数值方法和碰撞状态读写保护。
- `test_collision_auxiliary_evidence.py`：AxData 日轮验证摘要的交易日筛选、重复目录去重和无原始值输出；旧 FTShare 元数据只覆盖历史读取兼容性。
- `test_field_name_candidates.py`：字母字段名线索按逐源完整路径关联，歧义路径排除且不提升状态。
- `test_network_isolation.py`：离线网络边界与测试 SQLite 缓存隔离。
- `test_degradation_contract.py`：多级数据源降级契约。
- `test_project_temp.py`：项目临时目录默认位置与显式覆盖。
- `test_maintenance_checks.py`：语法与 Black 检查跳过已删除路径，并对无效语法/格式差异返回失败状态。
- `test_sc_ta_core.py`、`test_seat_db_audit_fix.py`、`test_symbol_norm.py`：技术指标、龙虎榜席位与代码归一化。
- `test_v310_sources.py`：数据源兼容性、完整性与重试回归。

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
