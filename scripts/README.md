# `scripts/` 工具索引

当前版本见仓库根目录 `VERSION`。脚本参数以各自的 `--help` 和本仓库 `AGENTS.md` 为准。

## 运行入口

Windows 开发默认使用 PowerShell。`run_with_system_python.ps1` 校验并选择 Python 3.12；`SYSTEM_PYTHON_EXE` 可显式指定解释器。测试通过 `run_tests.ps1` 运行：

```powershell
.\scripts\run_tests.ps1 -Mode skip_real
.\scripts\run_tests.ps1 -Mode module -Path tests\core\test_core_routing.py
.\scripts\run_tests.ps1 -Mode expression -Expression "test_cache"
```

`run_with_system_python.bat` 和 `upload_reports_to_gd.bat` 是兼容包装器。`run_governance_gates.sh` 是供 POSIX shell 使用的本地脚本；当前仓库未配置 CI 或 pre-commit 自动调用它。

## 字段采集与研究

| 脚本 | 用途 |
|:---|:---|
| `capture_field_probe.py` | 采集字段样本至 `docs/field_verification/<日期>/`；会访问数据源并写入采集文件。 |
| `collide.py`、`collision_rules.py` | 跨源字段对撞与候选规则；对撞结果用于研究，不直接改主字典。 |
| `field_meta.py` | 为采集样本补充来源与锚点元数据。 |
| `crack_push2_status_codes_20260921.py` | Push2 状态码研究脚本。 |
| `crack_ulist_f88_95_20260921.py` | Ulist 高位字段研究脚本。 |
| `crack_zhb_anchored_20260921.py` | 基于锚点样本的 ZHB 字段研究脚本。 |

## 字段登记、生成与治理

| 脚本 | 用途与写入行为 |
|:---|:---|
| `extract_registry.py`、`field_registry_api.py` | 从主字典提取登记信息；后者是多个治理脚本共用的内部 API。 |
| `registry_parity.py` | 检查登记表、主字典投影和字段矩阵一致性。 |
| `gen_field_dict.py`、`gen_field_matrix.py` | 生成字典/矩阵片段；`--check` 只检查、不写入。 |
| `gen_ulist_subdict.py`、`gen_zhb_subdict.py` | 生成对应接口的字典子表及镜像。 |
| `audit_field_completeness.py`、`lint_field_names.py`、`lint_field_same_number.py` | 字段来源完整度、命名和编号检查。 |
| `archive_field_preflight.py` | 检查字段采集归档的 Markdown 契约。 |
| `verify_data_access.py`、`verify_sync_check.py` | 分别检查生产数据访问边界和字典/代码同步；同步检查会更新审计报告。 |
| `cleanse_dict_provenance.py` | 整理字段证据叙述；默认 dry-run，`--apply` 会改写字典并追加溯源记录。 |
| `cleanse_dict_verif_narrative.py` | 生成字段结论列清理建议；默认 dry-run 不写文件，需显式传 `--plan-output <路径>` 才保存计划；`--apply` 会改写字典并追加溯源记录。 |

## 报告、数据与维护

| 脚本 | 用途 |
|:---|:---|
| `backtest_topn.py` | 基于本地历史数据回测 Top-N 选股。 |
| `check_em_health.py` | 低频探测东方财富服务状态；按脚本限频执行。 |
| `clean_cache.py` | 调用统一缓存清理入口；清理范围以 `--help` 为准。 |
| `fmt_preview.py` | 离线预览报告 Markdown 渲染。 |
| `perf_compare.py` | 本地数据结构性能对比。 |
| `update_calendar.py` | 更新本地交易日历数据。 |
| `upload_reports_to_gd.py` | 补传 Google Drive 报告；支持先预览待上传项目。 |
| `backup-opencode.ps1` | 备份本机 OpenCode 配置。 |

会改写字典、矩阵、采集记录或审计报告的工具，先检查其写入目标和工作区状态。`cache/` 里的 SQLite、K 线和 ZHB 快照不是同一种缓存；不要通过删除整个目录来代替有范围的清理。
