# tests/infra/ — 基础设施测试

> 本目录覆盖调度器、外部 API/Google Drive、字段工具、入口依赖预检与脚本写入边界等基础设施契约。
> 文件清单与逐文件定位见父目录 [`../README.md`](../README.md); 本文件仅作本层速查。

## 文件与职责(9)

| 文件 | 职责 |
|:---|:---|
| test_infra_gd.py | Google Drive 上传模块单元测试 |
| test_infra_api_stability.py | 多数据源接口稳定性 + 字段核实守护(real_network) |
| test_infra_f10.py | F10 章节在报告中的集成测试(阶段二验证) |
| test_field_completeness_scopes.py | 字段完整性审计范围契约 |
| test_lint_field_names.py | 字段命名检查器回归 |
| test_main_scheduler.py | 调度器子任务成功/失败状态传播 |
| test_main_dependencies.py | 必选 TDX 依赖与可选 Google Drive 依赖预检 |
| test_cleanse_dict_verif_narrative.py | dry-run 默认无写入、显式计划路径才生成文件 |
| test_ulist_subdict.py | ulist 子字典生成与占位索引回归 |

## 运行

```powershell
.\scripts\run_tests.ps1 -Mode module -Path tests/infra/test_infra_gd.py
.\scripts\run_tests.ps1 -Mode real   # 仅运行标记为 real_network 的用例
```
