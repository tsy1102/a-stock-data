# tests/reports/ — 报告层测试

> 本目录归并**5 大报告生成脚本**(`get_sht/med/lng/mak/val_report.py`)的 pytest 用例, 覆盖 `BaseReportRunner` 基类契约 / 批量流水线骨架 / val 策略注册表 / 章节缺失检测 / 换手率语义。
> 文件清单与逐文件定位见父目录 [`../README.md`](../README.md); 本文件仅作本层速查。

## 文件与职责(5)

| 文件 | 职责 |
|:---|:---|
| test_reports_runner.py | `ReportRunner` 基类与批量流水线骨架(execute_batch_pipeline) |
| test_reports_pipeline.py | 5 个 Runner 子类 `execute_pipeline` 装配契约(公共契约/生成器绑定/快照代理透传/上游调用次数钉死/sync 回退守卫) |
| test_reports_strategy.py | val 报告 **27 策略**注册表防线(空池安全 / 配置键存在性) |
| test_reports_chapter_omission.py | 回归锁固「源空→可见告警而非静默缺章」反模式 |
| test_reports_val_turnover.py | V17.0.15 换手率缺失值语义 |

> ⚠️ **剩余缺口**(见父 README): 仅剩**报告正文渲染结果**(生成 md 章节内容/措辞/数据呈现)无专职测试——修改报告正文渲染时仍勿假设已有保护。

## 运行

```powershell
.\scripts\run_tests.ps1 -Mode module -Path tests/reports/test_reports_strategy.py
```
