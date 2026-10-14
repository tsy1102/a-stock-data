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

当 `capture_field_probe.py` 的数据日是最近已完成交易日且数据阶段为 `closed` 时，会调用 `axdata_daily_validation.py`：对 AxData 短线/ELTDX 和 KPH/KPL 现有 raw 做有日期门槛的离线逐字段统计；每个数据日最多再请求一次已核准的 Tencent `tencent_realtime_snapshot`，仅在双方 `quote_time` 相同且属于目标交易日时比较字段。周末和节假日默认把数据日设为最近交易日，因此盘前、周末或节假日运行均可核验上一完整交易日；实际采集时刻不设 15:30 门槛。它轮换的是样本股票，不是 AxData 的 257 个接口；其他接口仍按交叉表候选待审。至少 3 个不同交易数据日、3 只不同股票且每份样本至少 5 个非空信息字段匹配、没有数值失配后，接口标记为运行上（部分）冗余并停止每日探测；未决/语义冲突字段继续展示。每 20 个后续有效数据日启动复验，需 3 个新有效样本；映射指纹、返回字段结构变化或复验差异会恢复日常探测。状态保存在本机 `.tmp/axdata_daily_validation_state.json`，每日证据写入数据日目录的 `axdata_validation.json`；碰撞报告显示状态和未决字段，但不把 AxData 当独立锚或自动更新主字典。`--only`、非最近交易日、目标数据阶段未收盘或项目对照源失败时不发额外请求；零请求跳过后可同日重评，已发请求同日不会重复。Eastmoney push2 不在白名单中。403/429/封禁立即暂停 Tencent 探针，连续两次空响应也暂停。超过 30 分钟的残留日锁会原子回收。

实际生产路由另有独立退出状态：`stock_shortline_indicators_tdx` 与 `eltdx.stocks.*.shortline` 比较，`kph_limit_up_history` 与 KPL 比较。每条路由至少要求 3 个不同交易数据日、每日至少 18 只配对股票；短线至少 5 个信息字段逐值全匹配，KPH 的六个已知字段全部匹配且没有额外未识别数值字段，才会暂停该接口的日常采集。每累计 20 个后续有效数据日，接口恢复采集并收集 3 个新交易日的复验样本；在复验期间仍从默认碰撞中排除，直到失配或结构变化将状态重开。未识别字段使路由保持采集并在证据中列出。短线请求收到 403、429 或封禁信号时立即停止该轮剩余股票请求，并将该路由持久标记为 `blocked_until_manual_review`；即使通过 `--only axdata` 或 `--only kph` 运行也会记录。人工复核封禁优先于契约变化，不会自动重试；成功快照也不能解除封锁。确认源恢复后，删除 `.tmp/axdata_daily_validation_state.json` 可清除该文件中的路由决策并从限量采样重新开始。状态损坏时不会自动覆盖。AxData 身份结果进入碰撞辅助报告，但不是碰撞锚。

`capture_field_probe.py` 同时调用 `levistock_daily_probe.py` 与 `levistock_daily_validation.py`。完整采集或 `--only market_sources` 在目标数据日为最近已完成交易日且数据阶段为 `closed` 时，每个数据日最多从 7 个数值候选接口中轮换一个额外请求；盘前、周末和节假日运行可沿用最近完整交易日作为数据日。请求经 `stock_common.sc_datasource.get_levistock_candidate_sample` Tier 2 适配器执行，要求安装版本符合 `requirements.txt` 中的 `levistock==0.1.8`；候选可比性由明确的请求交易日或响应交易日证据判断。适配器按 CLS/KPH 源族限流，遇到 403/429/封禁即持久暂停对应源族。候选响应写入独立的 `levistock_candidate_raw.json`，不自动并入碰撞锚；离线核验器复用 `raw_market_sources.json` 并生成 `levistock_validation.json`。完整快照同日重跑会跳过主源请求、检查/补齐每日核验；候选 raw、AxData 证据和每日状态保留，同日不重复探测。若之前因对照源缺失而零请求跳过，使用 `--overwrite` 恢复主源后可在同日重新评估；实际候选请求一旦启动仍会由每日状态阻止重复。详见 `docs/levistock_source_reconciliation_20261010.md`。

FTShare 的 MCP 客户端按网关当前 `tools/list` 使用有效工具名，兼容 JSON 与 SSE；历史接口按最近已完成交易日请求。董监高变动、涨停池和全市场商誉详情会完整翻页，并核对页数与记录总数，发现截断时丢弃部分结果并写入 `__error__`。商誉结果按股票代码恢复原有个股返回结构，进程内复用成功的全市场快照。HTTP、JSON-RPC 和工具错误摘要写入采集 raw 的 `__error__`，避免空数据掩盖失败；可通过 `FTSHARE_API_KEY` 环境变量设置可选请求头，仓库不保存密钥。所有 POST 至少间隔 500ms；收到 403/429 后本进程立即停止该源请求，连续三次请求或工具错误也会熔断。FTShare 已确认冗余的接口会停止日常请求，默认碰撞只移除这些接口的逐字段路径；未确认接口继续采集和碰撞。每 20 个有效交易数据日复验，复验期间仍排除，失配/契约变化会重新开放。AxData TDX 短线接口对北交所代码显式传入 `.BJ` 后缀，避免上游转换器将 `92` 开头代码误路由到上海市场。

FTShare 六个已登记数值接口分别参与来源身份核验：仅比较同一有效交易数据日且项目数据日与各源 as_of_date 一致的完整记录（盘前、周末或节假日采集也可计入）；至少三个不同的已完成交易数据日、每日至少 18 只股票且每条候选记录的非空字段全部匹配到一个已验证独立来源后，才暂停该接口的日常请求。其他 FTShare 接口继续采集。核验不确认 FTShare 的底层来源族、不修改主字典，也不把 FTShare 提升为碰撞锚。每 20 个后续有效交易数据日复核；适配器或字段契约变化后重新积累三天证据。状态保存在仓库 .tmp/source_identity_state.json；核验失败或状态损坏时继续采集。--overwrite 强制重采此前跳过的接口。collide.py 的独立报告段展示核验状态和证据日期，不混入 L1/L1-U 字段结论。

采集与碰撞是两个独立步骤：采集器每天保存 AxData `axdata_validation.json` 与 FTShare `meta.json` 核验结果；随后运行 `collide.py` 会读取所选交易日窗口中的归档，并在 JSON/Markdown 报告中展示逐日状态、被动比较计数、静态 AxData 接口队列及 FTShare 身份核验记录。相同有效数据日的重复采集目录只计一次。默认碰撞排除已确认冗余的 AxData 生产路由及 FTShare 逐字段路径，仍保留所有未确认字段；`--all` 与 `--exploratory` 可恢复这些历史数据以供研究。AxData 其余 257 项仍是静态候选，不因路由复验而自动联网采样。碰撞不会替代接口安全审定或增加请求，AxData/FTShare 结果不作为独立字段锚。

每次碰撞也会把观察到的字母字段与注册表 `(source, 完整 code path)` 精确关联，输出拼音、英文、缩写和混合拆词候选；同时标出注册状态、样本日期和候选来源文件。候选只是名称检索线索，不自动确认字段。完整列表保存在碰撞 JSON，Markdown 显示前 100 条。L1 精确匹配继续要求每日至少 18 组有效样本、3 个独立日期，并新增每日至少 5 组信息配对；双方同时为零或同时缺失不参与精确命中率，单侧零值仍按失配处理。

| 脚本 | 用途 |
|:---|:---|
| `capture_field_probe.py` | 按来源分别采集字段样本至 `docs/field_verification/<数据日>/`；串行调用各源，沿用适配器限流，记录逐源错误、缺股、deferred 与来源数据日。KPL 既有涨停明细独立写入 `raw_kpl.json`，新增 AxData `kph_limit_up_history` 单次批量写入 `raw_kph.json`，不缓存、不重试，并与 KPL 对撞；短线 TDX 路由与 ELTDX 逐股比较。两条 AxData 实际路由各自满足三交易日、每日 18 只配对股票及全字段规则后停止日常采集，20 个后续有效数据日后用三个新数据日复验；确认路由也从默认碰撞排除，复验期间仍排除，失配/结构变化即重新纳入。未知数值字段保持路由活跃。403/429/封禁立即停止 AxData 短线剩余请求并持久暂停相应路由；单独 `--only` 也记录状态。可用 `--only kpl` 或 `--only kph` 单独补采。该补充不替代 KPL 完整名单，也不调用 Eastmoney push2。默认仍跳过纯上下文的交易所龙虎榜、东财人气榜和市场源/Fuyao 中的龙虎榜与热股榜子路径；上下文可用 `--include-context` 恢复，或通过 `--only exchange` / `--only em_hot` 明确选择。 |
| `collide.py`、`collision_dates.py`、`collision_rules.py` | 共用日期归一化与快照择优；行情窗口按有效交易日、新闻/公告按自然日；L1 检查样本量、独立日期和来源族。默认排除交易所/东财人气榜源及市场源/Fuyao 中的上下文记录，也过滤历史 raw；需纳入研究时加 `--include-context`。其他带 `collision_eligible=false` 的子树仍按来源元数据排除并在报告诊断中说明。盘中/未知阶段仅作候选，语义、公式、时间序列与稳健相关性结果保留日期及来源证据；不直接改主字典。详见 `docs/field_verification/CRACKING_METHODOLOGY.md`。 |
| `context_policy.py` | 采集与碰撞共用的上下文源及路径策略，避免默认过滤规则漂移。 |
| `field_meta.py` | 为采集样本补充来源与锚点元数据。 |
| `crack_push2_status_codes_20260921.py` | Push2 状态码研究脚本。 |
| `crack_ulist_f88_95_20260921.py` | Ulist 高位字段研究脚本。 |
| `crack_zhb_anchored_20260921.py` | 基于锚点样本的 ZHB 字段研究脚本。 |

采集启动行会显示 `--only` 中实际选择的源，未指定时显示“默认源集合”，并单独标明市场上下文是“启用”还是“跳过”。

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
