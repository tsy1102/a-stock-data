# `scripts/` 工具说明

> 当前项目版本：`VERSION` 文件中的 17.4.23。本文记录当前维护的脚本入口；具体参数以脚本 `--help` 和 `AGENTS.md` 为准。

## Python 与 PowerShell 入口

仓库以 Windows PowerShell 5.1 为默认 Shell。运行 Python 工具时使用 `run_with_system_python.ps1`，它优先读取 `SYSTEM_PYTHON_EXE`，随后检查项目 `.venv`、`py -3.12`、Windows Store Python 和 PATH 上的解释器，并校验 Python 版本。

```powershell
.\scripts\run_with_system_python.ps1 scripts\capture_field_probe.py --help
.\scripts\run_with_system_python.ps1 scripts\gen_field_matrix.py --check
```

测试统一通过 `run_tests.ps1`：

```powershell
.\scripts\run_tests.ps1 -Mode skip_real
.\scripts\run_tests.ps1 -Mode module -Path tests\core\test_core_routing.py
.\scripts\run_tests.ps1 -Mode expression -Expression "test_cache"
```

如执行策略阻止脚本，可对单次运行使用 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ...`；不需要修改当前用户或系统的永久执行策略。

仓库仍包含 `.bat` 兼容包装器，供旧式 cmd 环境使用。项目默认工作流和本仓库的脚本维护按 PowerShell 版本执行。

## 字段采集与破解

- `capture_field_probe.py`：采集字段实测数据并写入 `docs/field_verification/<日期>/`。`--help` 列出日期、刷新样本池和 dry-run 选项；原始采集 JSON 属于可重建数据，按 `.gitignore` 规则处理。
- `collide.py`：读取已保存的跨源采集数据，生成字段对撞报告；只发现候选，不直接改主字典。
- `collision_rules.py`：对撞阈值与规则的代码定义，可用 `--emit` 生成规则说明。
- `field_meta.py`：为采集数据写入字段来源和锚点元数据。

常用调用：

```powershell
.\scripts\run_with_system_python.ps1 scripts\capture_field_probe.py --help
.\scripts\run_with_system_python.ps1 scripts\collide.py --help
.\scripts\run_with_system_python.ps1 scripts\collision_rules.py --emit
```

## 字段登记与治理

- `extract_registry.py`：从主字典构建字段登记表候选。
- `registry_parity.py`：检查登记表与主字典投影的一致性。
- `gen_field_dict.py --check`、`gen_field_matrix.py --check`：只读检查生成内容是否漂移。
- `archive_field_preflight.py`：字段采集归档契约预检。
- `audit_field_completeness.py`：对照采集源与字段登记，检查来源覆盖。
- `verify_data_access.py`：检查生产代码是否越过数据访问公开层。
- `verify_sync_check.py`：检查字段文档与代码同步；此脚本会生成/更新审计报告。
- `lint_field_same_number.py`、`lint_field_names.py`：字段编号和命名检查。

只读检查可逐项运行：

```powershell
.\scripts\run_with_system_python.ps1 scripts\registry_parity.py
.\scripts\run_with_system_python.ps1 scripts\gen_field_dict.py --check
.\scripts\run_with_system_python.ps1 scripts\gen_field_matrix.py --check
.\scripts\run_with_system_python.ps1 scripts\archive_field_preflight.py
.\scripts\run_with_system_python.ps1 scripts\verify_data_access.py
```

`run_governance_gates.sh` 是 POSIX Shell 的本地编排脚本。当前仓库没有配置 GitHub Actions 工作流或 pre-commit 配置；不要把该脚本描述为 CI/pre-commit 的共享入口。Windows 原生 PowerShell 环境可用上面的 Python 入口分别运行闸门。

## 其他维护工具

- `backtest_topn.py`：基于历史数据运行 Top-N 回测；遇到无效 ZHB ZIP 会给出解析错误。
- `clean_cache.py`：缓存清理命令封装。
- `check_em_health.py`：低频探测东方财富服务可用性；遵守脚本给出的请求间隔。
- `fmt_preview.py`：离线预览报告 Markdown 渲染。
- `gen_field_matrix.py`：从字段登记表生成主字典中的字段×来源矩阵；不带 `--check` 时会写入生成结果。
- `sync_readme.py`：旧格式摘要同步工具。当前根 README 不含其目标标记，且当前 CHANGELOG 标题格式不匹配该脚本解析器；不要运行它覆盖 README，版本说明按需手动同步。
- `update_calendar.py`：更新本地交易日历数据。
- `upload_reports_to_gd.py`：补传尚未上传到 Google Drive 的报告；先用 `--dry-run` 检查待上传项。
- `perf_compare.py`：本地数据结构性能对比工具。

执行会改写字典、矩阵、README 或审计报告的脚本前，先确认其写入目标和当前工作区状态。对可重建缓存的清理只影响脚本明确支持的缓存目录，不应借此清理研究归档或用户采集文件。
