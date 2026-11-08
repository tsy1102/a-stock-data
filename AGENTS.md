# AGENTS.md — 仓库执行规约

适用范围：仓库根目录及全部子目录。当前环境只支持 **Windows 原生 PowerShell 7**；不要求 PowerShell 5.1 兼容。

## 1. 任务路由与权威来源

- 按 [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md) §0 选择任务文档；采集与碰撞按 [`docs/field_verification/DAILY_RUNBOOK.md`](docs/field_verification/DAILY_RUNBOOK.md) 执行。
- 只读取完成当前任务所需的权威文档、代码和测试。大体积 registry、raw 样本、报告及历史材料按需查询，不默认整份载入。
- 用户当前要求决定任务范围；字段语义、日期、架构和运行行为须以对应真源及当前代码、配置、测试核实。遇到冲突先查明来源，不从旧报告推断动态状态。
- 字段身份以 `field_registry.json` 中的 `(source, 完整 code path)` 为准；`field_dict.md`、`unknown_fields.md` 是导航视图，源协议材料按需查阅。
- 字段样本保留起点为 `20261015`。不得回补或读取更早的 `raw_*.json`、日期化 ZHB 压缩包和解析缓存；被现行裁决材料引用的报告与元数据按其权威规则保留。日常操作细节见 `DAILY_RUNBOOK.md`。
- 当前调查状态以 [`docs/field_verification/README.md`](docs/field_verification/README.md) 及其专项记录为准，不在本规约复制候选状态或研究结论。

## 2. PowerShell 与命令执行

- 在仓库任务中使用 PowerShell 7；不要切换到 Bash、WSL 或嵌套 `cmd` / `powershell -Command` 来拼装命令。
- 使用 Windows 路径。路径拼接用 `Join-Path`；涉及通配符字符、空格或用户输入的路径时用 `-LiteralPath`。
- 简单、单步命令可直接运行。多步逻辑、循环、复杂引号或需要稳定中文输出时，写入仓库根 `.tmp/` 下的 `.ps1` 再执行。需要参数的脚本先写 `param()`，再设置严格模式和错误策略；不要求 BOM。
- `.tmp/` 已被 Git 忽略，用于本任务的临时脚本、探针和下载文件。不要清理其他任务创建的临时文件，也不要把临时产物放入项目数据目录。
- 环境变量只在当前进程/会话设置；未经用户明确要求，不写入永久环境变量或凭据配置。
- 调用外部程序时写明可执行文件名（如 `git.exe`、`python.exe`），用参数数组和 splatting，紧接着检查 `$LASTEXITCODE`；非零时停止并保留错误信息。不要吞掉异常或用空 `catch` 继续执行。
- 不要全局放宽 `ExecutionPolicy`。相同故障经过两种有依据的尝试仍失败时，停止盲目重试，报告原命令、关键异常和已尝试的修复方向。

### Python 与测试

- 项目 Python 命令通过 [`scripts/run_with_system_python.ps1`](scripts/run_with_system_python.ps1) 执行；它会选择并校验 Python 3.12，并把临时目录设为仓库 `.tmp/`。
- 测试统一通过 [`scripts/run_tests.ps1`](scripts/run_tests.ps1)，不得直接调用 pytest。测试按 `tests/core/`、`tests/data/`、`tests/infra/`、`tests/reports/` 及 `tests/` 根目录组织；marker 先登记在 `pyproject.toml`。运行选项见 [`tests/README.md`](tests/README.md)。
- 默认离线测试排除 `real_network`。真实网络测试必须使用该 marker；仅在用户明确要求联网验证时运行。

## 3. 数据边界与高影响改动

- 生产采集和报告通过 Tier 1 / Tier 2 公开适配器取数；原始客户端限于其适配器边界。原则见 [`docs/ARCHITECTURE_THEORY.md`](docs/ARCHITECTURE_THEORY.md)，模块边界见 [`docs/architecture.md`](docs/architecture.md)。
- 修改公共函数签名、返回字段、来源身份/路由、缓存口径、日期策略或 SQLite 契约前，先核对定义、调用方、消费者、相关测试及受影响的缓存键/失效规则。普通文档或局部实现改动按其实际影响检查，不要求机械地提交五项调查清单。
- 高影响区域及必查重点：
  - `stock_common/sc_datasource/`、`core/data_provider.py`：来源映射、适配器契约、优先级、新鲜度、缓存及调用方测试。
  - `core/tdx_client.py`、`core/zhb_client.py`：协议/解析契约、日期和缓存边界及对应测试。
  - `stock_common/__init__.py`：公开导出、消费者和兼容性测试。
  - `docs/field_verification/field_registry.json`：逐源完整字段身份和状态；修改后按 registry 工具重生成视图并验证 parity，不直接编辑生成视图。
- 字段或 API 契约变化时同步更新实际权威文档、Schema、全部消费者和测试。只有缓存语义发生变化时才调整缓存版本或类别。
- 若发现架构原则本身已过时，先更新原则及依赖闸门；确认原则仍有效而实现偏离时，才登记到 [`docs/DEBT_LEDGER.md`](docs/DEBT_LEDGER.md)。

## 4. 审查与验证

### 改动审查

- 对照用户当前要求和对应权威文档检查实现意图；字段改动按完整来源路径核验，缓存改动检查 key、TTL、日期边界和失效策略。
- 检查凭据或密钥是否进入版本控制（整个 `credentials/` 目录不得提交）、SQL 是否使用参数绑定、异常是否被吞掉、共享状态是否需要锁，以及新增行为是否有测试覆盖。
- 阻塞问题：安全漏洞、数据丢失风险或明确功能缺陷。其余问题按影响说明，不为降低问题数量而隐去未解决项。

### 验证入口

```powershell
.\scripts\run_offline_checks.ps1
.\scripts\run_tests.ps1 -Mode module -Path tests\core\test_core_routing.py
.\scripts\run_with_system_python.ps1 scripts\verify_data_access.py
```

- `run_offline_checks.ps1` 是提交前完整离线验收入口，覆盖语法、类型、格式、架构/同步/registry 闸门及离线测试；真实网络测试不会启动。
- 定向回归可先用 `run_tests.ps1 -Mode module -Path <测试文件>`，但不能代替提交前完整验收。只改文档时不运行代码测试；核对链接、命令、规则一致性和 diff。
- 代码改动完成后、提交前运行完整离线验收。按改动范围检查密钥扫描和 `git.exe diff --check`；任一必需检查失败时，不报告为通过。
- 行为变更写入 `CHANGELOG.md`，避免在路线图、索引和多个历史说明重复记录同一事实。
- 汇报实际改动范围、执行过的验证及结果、重要证据和未解决限制；没有可靠基线时不编造指标。项目级完整审查可按以下格式汇总：

```text
VERIFICATION REPORT
==================
语法/类型/格式/测试/安全: [按适用项报告结果]
Diff: [文件数及范围]
Overall: [READY / NOT READY]
待修复: [问题，或无]
```
