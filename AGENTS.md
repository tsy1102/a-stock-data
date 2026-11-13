# AGENTS.md — 仓库执行规约

适用范围：仓库根目录及全部子目录。使用 Windows 原生 PowerShell 7；不要求 PowerShell 5.1 兼容。

## 1. 任务路由与权威来源

- 按 [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md) §1 选择任务文档；采集与碰撞按 [`docs/field_verification/DAILY_RUNBOOK.md`](docs/field_verification/DAILY_RUNBOOK.md) 执行。
- 只读取完成当前任务所需的权威文档、代码和测试。大体积 registry、raw 样本、报告及历史材料按需查询，不默认整份载入；最小化读取不得成为跳过本规约所要求的高影响改动检查的理由。
- 用户当前要求决定任务范围；字段语义、日期、架构和运行行为以对应真源及当前代码、配置、测试核实。先查明会影响当前任务结论或操作的冲突；无关冲突记录后继续独立工作，不从旧报告推断动态状态。
- 字段身份以 `field_registry.json` 中的 `(source, 完整 code path)` 为准；`field_dict.md`、`unknown_fields.md` 是导航视图，源协议材料按需查阅。
- 采集样本保留边界以 [`scripts/capture_retention.py`](scripts/capture_retention.py) 的 `MIN_CAPTURE_DATE` 为准。不得回补或将边界前的 `raw_*.json`、日期化 ZHB 压缩包或解析缓存用作当前样本；现行裁决材料引用的报告与元数据按其权威规则保留。日常操作见 [`DAILY_RUNBOOK.md`](docs/field_verification/DAILY_RUNBOOK.md)。
- 当前调查状态以 [`docs/field_verification/README.md`](docs/field_verification/README.md) 及专项记录为准，不在本规约复制候选状态或研究结论。

### 自主执行与任务收尾

- 在用户当前请求及仍有效的明确授权范围内，直接完成可逆的本地分析、修改和验证；不因可推断细节或非关键偏好缺失而额外要求确认。采用合理假设时说明依据；缺失信息会实质改变结果或涉及明确批准边界时，集中询问，同时继续独立可做事项。
- 用户要求先审阅或提交方案时，确认前保持只读；收到确认后按确认方案实施，不重复请求同一授权。失败、冲突或验收阻碍只暂停受影响步骤；完成其他已授权且可执行的工作。只有核心目标依赖缺失用户输入或外部状态且无可行替代路径时，才报告受阻，并列明已完成、未完成及阻塞原因。
- 本节不授权超出用户要求的操作，也不弱化永久配置、凭据、真实联网测试和样本保留边界等明确限制。

## 2. 日期与证据资格

- 分别识别运行自然日（`run_date` / `capture_date`）、A 股交易日、采集目录目标数据日（`data_date`）和来源实际数据日（`as_of_date` 或来源契约指定日期）；不得用运行日或目录名替代来源实际日期。
- 自然日与目标数据日或来源数据日相差一天，本身不表示采集错误或数据过期。先按交易日历、运行时点和来源日期规则确认日期，再判断样本在对应数据域中是否可用于碰撞或定案。
- 日频行情按交易日序列比较；新闻、公告、分红和财报按事件日、生效日或报告期判断。来源日期未确认的样本不得作为正式碰撞输入或定案证据；同一来源数据日的重复采集不算独立日期样本。稳定的非日频字段可作为标注待核的研究线索。
- 采集时点、来源日期与 ZHB 日期副本冲突时的核查流程见 [`DAILY_RUNBOOK.md`](docs/field_verification/DAILY_RUNBOOK.md)。

## 3. PowerShell、Python 与测试

- 仓库命令使用 PowerShell 7；不要切换到 Bash、WSL 或嵌套 `cmd` / `powershell -Command` 拼装命令。使用 Windows 路径；路径拼接用 `Join-Path`，涉及通配符、空格或用户输入的路径时用 `-LiteralPath`。
- 简单单步命令可直接运行。多步逻辑、循环、复杂引号或需要稳定中文输出时，将脚本放在仓库根 `.tmp/` 下执行；不要清理其他任务创建的临时文件，也不要将临时产物放入项目数据目录。
- 生成需提交或参与 SHA-256 校验的文本文件时，PowerShell `Export-Csv` / `Set-Content` 的默认行尾可能与 Git 入库后的文件不同。证据哈希统一使用 `scripts/evidence_hash.py` 或 `canonical_text_file_sha256()` 计算规范 LF 摘要；现有证据校验继续容忍 LF/CRLF，避免行尾变化误判内容损坏。
- 环境变量只在当前进程或会话设置；未经用户明确要求，不写入永久环境变量或凭据配置。调用外部程序时写明可执行文件名，使用参数数组和 splatting，并立即检查 `$LASTEXITCODE`；非零时保留错误信息，不要吞掉异常。不要全局放宽 `ExecutionPolicy`；有依据的两种尝试后停止重复同一失败路径，继续替代诊断及其他独立工作；确无可行替代路径时报告原命令和关键异常。
- 项目 Python 命令经 [`scripts/run_with_system_python.ps1`](scripts/run_with_system_python.ps1) 执行；它校验 Python 3.12 并将临时目录设为仓库 `.tmp/`。`pyproject.toml` 的 mypy 3.11 是静态检查目标，不是运行时版本。
- 测试经 [`scripts/run_tests.ps1`](scripts/run_tests.ps1) 执行，不直接调用 pytest。测试分区、运行选项和 marker 见 [`tests/README.md`](tests/README.md)；新增 marker 前先登记在 `pyproject.toml`。默认离线测试排除 `real_network`；只有用户在当前请求或仍有效的明确授权中授权真实联网测试时才运行。此限制仅约束测试套件，不限制另行授权的公开网页核查。

## 4. 数据边界、改动审查与验收

- 生产采集和报告通过 Tier 1 / Tier 2 公开适配器取数；原始客户端限于适配器边界。架构原则见 [`docs/ARCHITECTURE_THEORY.md`](docs/ARCHITECTURE_THEORY.md)，模块边界见 [`docs/architecture.md`](docs/architecture.md)。
- 修改公共函数签名、返回字段、来源身份或路由、缓存口径、日期策略或 SQLite 契约前，按实际影响核对定义、调用方、消费者、相关测试及缓存键/失效规则；局部改动不要求固定格式的调查清单。
- 高影响区域：
  - `stock_common/sc_datasource/`、`core/data_provider.py`：来源映射、适配器契约、优先级、新鲜度、缓存及调用方测试。
  - `core/tdx_client.py`、`core/zhb_client.py`：协议/解析契约、日期、缓存边界及对应测试。
  - `stock_common/__init__.py`：公开导出、消费者和兼容性测试。
  - [`docs/field_verification/field_registry.json`](docs/field_verification/field_registry.json)：按完整来源路径维护字段身份和状态；使用 registry 工具重生成视图并验证 parity，不直接编辑生成视图。
- 字段或 API 契约变化时同步更新实际权威文档、Schema、消费者和测试。只有缓存语义变化时才调整缓存版本或类别。架构原则过时时先更新原则及依赖闸门；原则有效而实现偏离时登记至 [`docs/DEBT_LEDGER.md`](docs/DEBT_LEDGER.md)。
- 审查改动时核对用户要求和权威来源；检查凭据或密钥未进入版本控制（整个 `credentials/` 目录不得提交）、SQL 使用参数绑定、异常处理、共享状态并发安全及新增行为覆盖。安全漏洞、数据丢失风险或明确功能缺陷为阻塞问题；其余问题按影响说明。

### 验证

```powershell
.\scripts\run_offline_checks.ps1
```

- 该入口执行提交前完整离线验收，涵盖语法、类型、格式、架构/同步/registry 闸门和离线测试，不启动真实网络测试。定向回归选项见 [`tests/README.md`](tests/README.md)。
- 代码改动完成后、提交前运行完整离线验收；按改动范围检查密钥扫描和 `git.exe diff --check`，必需检查失败时不得报告为通过。失败时先修复项目问题并重跑；若环境阻碍无法排除，完成其他独立检查，报告失败命令、证据和 `NOT READY`，不得把受阻检查报告为通过或据此跳过必需闸门。只改文档时不运行代码测试，应核对链接、命令、规则一致性和 diff。
- 行为变更写入 [`CHANGELOG.md`](CHANGELOG.md)，避免在路线图、索引和多个历史说明重复记录同一事实。
- 汇报实际改动范围、执行过的验证及结果、重要证据和未解决限制；没有可靠基线时不编造指标。
