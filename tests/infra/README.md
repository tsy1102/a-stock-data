# tests/infra/ — 基础设施测试

> 本目录归并**外部依赖基础设施**的 pytest 用例(Google Drive 上传 / 外部 API 字段契约 / F10 集成), 对应 `core/gd_uploader.py` 与 `stock_common/f10_parser.py` 等。
> 文件清单与逐文件定位见父目录 [`../README.md`](../README.md); 本文件仅作本层速查。

## 文件与职责(3)

| 文件 | 职责 |
|:---|:---|
| test_infra_gd.py | Google Drive 上传模块单元测试 |
| test_infra_api_stability.py | 多数据源接口稳定性 + 字段核实守护(real_network) |
| test_infra_f10.py | F10 章节在报告中的集成测试(阶段二验证) |

## 运行

```powershell
.\scripts\run_tests.ps1 -Mode module -Path tests/infra/test_infra_gd.py
.\scripts\run_tests.ps1 -Mode real   # 仅真网络测试(需 REAL_NETWORK=1)
```
