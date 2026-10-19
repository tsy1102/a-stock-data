# tests/reports/ — 报告层测试

> 本目录归并**5 大报告生成脚本**(`get_sht/med/lng/mak/val_report.py`)的 pytest 用例, 覆盖 `BaseReportRunner` 基类契约 / 批量流水线骨架 / val 策略注册表 / 章节缺失检测 / 换手率语义。
> 文件清单与逐文件定位见父目录 [`../README.md`](../README.md); 本文件仅作本层速查。

## 文件与职责(12)

| 文件 | 职责 |
|:---|:---|
| test_reports_runner.py | `ReportRunner` 基类与批量流水线骨架(execute_batch_pipeline) |
| test_reports_pipeline.py | 5 个 Runner 子类 `execute_pipeline` 装配契约(公共契约/生成器绑定/快照代理透传/上游调用次数钉死/sync 回退守卫) |
| test_reports_strategy.py | val 报告 **27 策略**注册表防线(空池安全 / 配置键存在性) |
| test_reports_chapter_omission.py | 回归锁固「源空→可见告警而非静默缺章」反模式 |
| test_reports_val_turnover.py | V17.0.15 换手率缺失值语义 |
| test_mak_industry_normalization.py | MAK 空值行业归类和名称归一化 |
| test_mak_index_mapping.py | MAK 指数代码映射回归 |
| test_report_enrichment.py | 财报期候选、现金含量和 TDX 快照期别标注 |
| test_val_snapshot_failure.py | VAL 快照失败时的报告降级与告警 |
| test_val_fast_kline.py | VAL TDX 快速 K 线样本不足与失败边界 |
| test_val_report_content.py | VAL 报告措辞与异步估值计算线程边界 |
| test_reports_financial_precision.py | 日期来源、52 周区间、PE 候选与 MAK 资金覆盖口径 |

> ⚠️ **剩余缺口**(见父 README): 当前新增用例覆盖报告辅助函数与关键候选/覆盖逻辑；完整生成的五类 Markdown 报告仍无端到端快照测试，修改章节组装时仍须检查真实渲染结果。

## 运行

```powershell
.\scripts\run_tests.ps1 -Mode module -Path tests/reports/test_reports_strategy.py
```
