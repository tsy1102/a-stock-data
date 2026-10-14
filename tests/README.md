# tests 目录说明

本目录包含单元测试、组件集成测试与显式标记的真实网络测试。测试通过 `scripts/run_tests.ps1` 运行；默认模式拦截外网并排除 `real_network` 用例。每个测试模块使用项目 `.tmp/` 下的独立 SQLite 缓存，避免测试清理或写入项目真实缓存。

## 当前模块清单

| 区域 | 测试模块数 | 覆盖范围 | 详细清单 |
|:---|---:|:---|:---|
| `core/` | 16 | 核心门面、缓存、日历、类型契约、fallback、评分和技术指标 | [`core/README.md`](core/README.md) |
| `data/` | 11 | ZHB、TDX、Eastmoney、KPL、网络、解禁单位和回测快照 | [`data/README.md`](data/README.md) |
| `infra/` | 12 | 调度器、字段完整性/命名、依赖预检、dry-run 写入边界、F10、外部 API 与 GD | [`infra/README.md`](infra/README.md) |
| `reports/` | 6 | 报告 Runner、流水线、策略与章节契约 | `reports/` 测试目录 |
| 根目录 | 31 | 碰撞/字段登记、采集探针、来源身份核验、依赖适配、网络与临时目录隔离 | 本文件下方列出 |
| **合计** | **76** | 参数化用例展开前的测试模块数 | — |

根目录测试：

- 来源身份核验回归：test_source_identity_reconciliation.py，覆盖匹配阈值、逐接口跳过、日期资格与契约变化重验。
- `test_apply_collision_adjudications.py`、`test_collide.py`、`test_collision_dates.py`、`test_collision_topic_scripts.py`：碰撞候选、日期口径、专题脚本与人工定案。
- `test_field_registry_api.py`、`test_gen_field_dict.py`、`test_reconcile_field_registry.py`、`test_source_lineage_api.py`：字段登记、生成视图、状态同步与来源谱系。
- `test_capture_field_probe.py`：采集源请求参数、日期校验、状态和调用边界。
- `test_dependency_adapter_compat.py`：Levistock 实际方法契约与 AxData 本地 ZHB ZIP 读取。
- `test_axdata_daily_validation.py`、`test_levistock_daily_probe.py`、`test_levistock_daily_validation.py`、`test_levistock_rate_limit.py`：候选源每日核验、日期/数据阶段、熔断与限流。
- `test_axdata_capture_identity.py`、`test_axdata_capture_policy.py`、`test_axdata_collision_suppression.py`：AxData 生产路由退出、三交易日复验、限流熔断与默认碰撞过滤。
- `test_ftshare_client.py`：FTShare 客户端分页、响应解析和传输诊断。
- `test_collision_research_state.py`：探索候选跨轮保存、幂等和历史继承。
- `test_collision_auxiliary_evidence.py`：AxData/FTShare 日轮核验摘要的交易日筛选、重复目录去重、无原始值输出。
- `test_field_name_candidates.py`：字母字段名线索按逐源完整路径关联，歧义路径排除且不提升状态。
- `test_network_isolation.py`：离线网络边界与测试 SQLite 缓存隔离。
- `test_degradation_contract.py`：多级数据源降级契约。
- `test_project_temp.py`：项目临时目录默认位置与显式覆盖。
- `test_sc_ta_core.py`、`test_seat_db_audit_fix.py`、`test_symbol_norm.py`：技术指标、龙虎榜席位与代码归一化。
- `test_v310_sources.py`：数据源兼容性、完整性与重试回归。

> **历史离线验证（2026-10-08）**：默认 `all` 模式共收集 768 项，720 passed、1 skipped、47 个 `real_network` 用例被排除（125.45 秒）。测试集合会随参数化和用例增减而变化，结果以当次运行输出为准。

> **最近验证（2026-10-10，日期资格调整后）**：AxData 定向测试 17 passed、Levistock 定向测试 10 passed；全量离线套件 793 passed、1 skipped、47 个 `real_network` 用例排除（841 收集，59.31 秒）。此前在受限执行沙箱中的停滞发生于 Windows Python 3.12 初始化 asyncio loopback socketpair 时，未进入业务协程；在获准的提升执行环境中最小探针与完整套件均通过。真实网络用例与实时采集未运行。此前完整运行记录见 `CHANGELOG.md`。
>
> **2026-10-11 来源身份重分类后补充验证**：启动提示/采集器模块 54 passed，字段范围与来源身份回归 6 passed，字典生成回归 3 passed；registry parity、field matrix、A1/A7、语法检查与 MyPy 通过。全量离线套件收集 865 项；首次运行在 `test_missing_report_script_is_failure` 长时间无输出，排除此项后再次运行在 `test_cyq_and_kline_chapters_survive_source_failure` 长时间无输出，均未计为全量通过。`real_network` 用例未运行，Black 检查未能返回结果。此次具体结果见 `CHANGELOG.md`。

> **2026-10-11 FTShare 接口身份核验改造**：来源核验、采集器逐接口停采、碰撞报告共 13 个定向用例全部通过；3 个生产脚本 MyPy、A1、A7、语法检查通过。完整离线套件本次收集 876 项、选取 829 项，运行到 34% 后在 test_data_em_board_members::test_mcap_yi_converted_from_yuan 连续 60 秒无输出；中断时该用例随后显示通过，但没有全套总结，故不计为全量通过。Black --check 两次均超过 60 秒未返回输出，未记为通过。

> **2026-10-14 碰撞与每日证据报告更新**：碰撞/字段名候选表达式选择 36 项通过（包含 1 项额外的缓存命名测试），采集、AxData 轮验、字段覆盖与 FTShare 来源身份选择 100 项通过；4 个碰撞模块语法、Black、MyPy、A1/A7 均通过。全量离线套件 938 项收集，890 passed、1 skipped、47 个真实网络用例排除（44.13 秒）。受限沙盒首轮在调度器用例停滞；本机执行环境完整重跑通过，未运行真实网络测试。

> **2026-10-14 AxData/FTShare 路由退出闭环补充**：AxData 身份状态单模块 9 passed；AxData/FTShare 身份、采集、碰撞与辅助证据联合表达式共 194 passed、764 deselected。新增验证确保已人工封锁的 AxData 路由不会因接口契约变化或传入成功快照而自动解封，同时覆盖冗余接口退出和复验。全量离线套件本次未完成；静态检查与停滞位置见 `CHANGELOG.md`。

> **2026-10-11 长时间无响应排查后的全量离线验证**：894 collected，846 passed、1 项因未安装可选 TA-Lib 而跳过、47 个 `real_network` 用例排除，35.48 秒；无 faulthandler 超时。已查明此前卡点分别来自测试写入真实 SQLite 缓存、DNS/限流等待、报告测试漏 mock 数据源，以及沙箱阻止 Windows asyncio 创建本地 socketpair；测试缓存和调用边界已隔离，使用获准提升执行环境完成回归。SHT 的 ELTDX 预热异常现在保留诊断并继续行情预取。语法编译、diff 检查和 `get_sht_report.py` MyPy 通过。Black 两种 worker 配置均无响应，格式状态未确认；MyPy 在报告流水线测试的其他未改行报告 8 个类属性赋值错误。真实网络用例未运行；单次 `real_network` 用例仍需单独按源确认服务状态与限流风险。

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

> **2026-10-12 东财/ELTDX 修复后全量离线验证**：908 collected，860 passed、1 skipped、47 个 `real_network` 用例排除，35.53 秒。Python 3.12 语法编译、7 个改动文件 Black、4 个生产文件 MyPy、A1/A7 闸门与 `git diff --check` 均通过。受限沙箱阻止 Windows asyncio 和 Black 创建本机 socketpair，故验证在获准的本机回环环境中完成；未运行真实网络用例。详见 `CHANGELOG.md`。
