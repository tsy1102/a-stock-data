# 贡献指南

本文件概述本项目的开发入口。仓库级约束与数据访问边界以 [`AGENTS.md`](AGENTS.md)、[`docs/ARCHITECTURE_THEORY.md`](docs/ARCHITECTURE_THEORY.md) 和 [`docs/DEBT_LEDGER.md`](docs/DEBT_LEDGER.md) 为准。

## 开发环境

- 最低 Python 版本为 3.11；项目验证环境为 Python 3.12。
- Windows 下使用 PowerShell，并通过 `scripts/run_with_system_python.ps1` 选择受支持的解释器。该入口会将临时文件放入仓库 `.tmp/`。
- 安装运行依赖：`.\scripts\run_with_system_python.ps1 -m pip install -r requirements.txt`。
- 安装开发依赖：`.\scripts\run_with_system_python.ps1 -m pip install -r requirements-dev.txt`。

## 修改与验证

- 新增或修改行为时，在 `tests/` 中补充对应回归用例；真实网络用例必须标记 `real_network`。
- Shell 层运行测试统一使用 `scripts/run_tests.ps1`：

  ```powershell
  .\scripts\run_tests.ps1 -Mode skip_real
  .\scripts\run_tests.ps1 -Mode module -Path tests\core\test_core_routing.py
  ```

- 修改生产数据访问时，检查并运行 A1/A7 闸门：

  ```powershell
  .\scripts\run_with_system_python.ps1 scripts\verify_data_access.py
  .\scripts\run_with_system_python.ps1 scripts\verify_sync_check.py
  ```

- 按改动范围运行 Black、MyPy 和语法检查；验证标准及报告格式见 [`AGENTS.md`](AGENTS.md) §9。
- 字段、来源身份、缓存键、单位或日期语义变更，必须先追踪所有调用方与序列化契约，再同步 registry 投影、相关测试和文档。
- 不要静默吞掉异常；降级分支应保留可诊断信息。改动涉及的缓存类别或 schema 若语义变化，按架构约定升级。

## 文档与版本

- 对用户可见的行为、修复和验证结果更新根目录 [`CHANGELOG.md`](CHANGELOG.md)。
- 版本号由根目录 [`VERSION`](VERSION) 管理；项目结构、运行参数或开发流程变化时同步更新对应 README。
- 详细架构、字段定义和上游关系分别见 [`docs/architecture.md`](docs/architecture.md)、[`docs/field_dict.md`](docs/field_dict.md) 与 [`docs/UPSTREAM_COMPATIBILITY.md`](docs/UPSTREAM_COMPATIBILITY.md)。
