# `scripts/` 工具索引

当前版本见仓库根目录 `VERSION`。脚本参数以各自的 `--help` 和本仓库 `AGENTS.md` 为准。

## 运行入口

Windows 开发默认使用 PowerShell。`run_with_system_python.ps1` 校验并选择 Python 3.12，并将 Python 进程及其子进程的 `TEMP`、`TMP`、`TMPDIR` 指向仓库根 `.tmp/`；兼容入口 `run_with_system_python.bat` 也采用该目录。导入项目 `stock_common` 包时，项目自身的临时目录和进程间锁也会使用 `.tmp/`，直接 `python main.py` 不再依赖系统临时目录。可通过 `ASTOCK_TEMP_DIR` 指定临时目录。`SYSTEM_PYTHON_EXE` 可显式指定解释器。测试通过 `run_tests.ps1` 运行：

```powershell
.\scripts\run_tests.ps1 -Mode skip_real
.\scripts\run_tests.ps1 -Mode module -Path tests\core\test_core_routing.py
.\scripts\run_tests.ps1 -Mode expression -Expression "test_cache"
```

`run_with_system_python.bat` 和 `upload_reports_to_gd.bat` 是兼容包装器。`run_governance_gates.sh` 是供 POSIX shell 使用的本地脚本；当前仓库未配置 CI 或 pre-commit 自动调用它。

## 字段采集与研究

| 脚本 | 用途 |
|:---|:---|
| `capture_field_probe.py` | 按来源分别采集字段样本至 `docs/field_verification/<数据日>/`；串行调用各源，沿用适配器限流，记录逐源错误、缺股、deferred 与来源数据日。默认跳过纯上下文的交易所龙虎榜、东财人气榜，并跳过市场源/Fuyao 中的龙虎榜与热股榜子路径；其他字段和 Fuyao 竞价元数据照常采集。历史上下文 raw 在默认重采时保留；需要采集时加 `--include-context`，或通过 `--only exchange` / `--only em_hot` 明确选择。Eastmoney 失败不做盲目重试；完整快照才幂等跳过。 |
| `collide.py`、`collision_dates.py`、`collision_rules.py` | 共用日期归一化与快照择优；行情窗口按有效交易日、新闻/公告按自然日；L1 检查样本量、独立日期和来源族。默认排除交易所/东财人气榜源及市场源/Fuyao 中的上下文记录，也过滤历史 raw；需纳入研究时加 `--include-context`。其他带 `collision_eligible=false` 的子树仍按来源元数据排除并在报告诊断中说明。盘中/未知阶段仅作候选，语义、公式、时间序列与稳健相关性结果保留日期及来源证据；不直接改主字典。详见 `docs/field_verification/CRACKING_METHODOLOGY.md`。 |
| `context_policy.py` | 采集与碰撞共用的上下文源及路径策略，避免默认过滤规则漂移。 |
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
## 报告 Markdown 约定

- 报告目录保存可追溯的历史快照；不要批量重排或改写历史报告。
- 每份新报告在开头保留报告类型、股票/范围和生成时间；有可靠来源时另列数据日期或快照日期。生成时间、任务目标日期和来源数据日期是不同概念，不得互相推算或替代。
- 来源不可用、字段缺失、降级来源和单位口径应在对应章节明确呈现，不以空白内容伪装成功。
- 使用 Markdown 标题和标准表格，表头标注单位；行尾空格只在确实需要 Markdown 强制换行时保留。
- 预览、渲染和临时对比文件放在仓库 `.tmp/`，不写入 `reports/` 正式快照目录。
