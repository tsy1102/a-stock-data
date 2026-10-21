# `scripts/` 工具索引

当前版本见仓库根目录 `VERSION`。脚本参数以各自的 `--help` 和本仓库 `AGENTS.md` 为准。

## 运行入口

Windows 开发默认使用 PowerShell。`run_with_system_python.ps1` 校验并选择 Python 3.12，并将 Python 进程及其子进程的 `TEMP`、`TMP`、`TMPDIR` 指向仓库根 `.tmp/`；兼容入口 `run_with_system_python.bat` 也采用该目录。导入项目 `stock_common` 包时，项目自身的临时目录和进程间锁也会使用 `.tmp/`，直接 `python main.py` 不再依赖系统临时目录。可通过 `ASTOCK_TEMP_DIR` 指定临时目录。`SYSTEM_PYTHON_EXE` 可显式指定解释器。测试通过 `run_tests.ps1` 运行：

```powershell
.\scripts\run_tests.ps1 -Mode skip_real
.\scripts\run_tests.ps1 -Mode module -Path tests\core\test_core_routing.py
.\scripts\run_tests.ps1 -Mode expression -Expression "test_cache"
```

`run_with_system_python.bat` 和 `upload_reports_to_gd.bat` 是兼容包装器。`run_governance_gates.sh` 是供 POSIX shell 使用的本地门禁运行器；仓库没有版本化 CI 或 hook 安装配置，具体克隆是否在 `.git/hooks/pre-commit` 中调用它取决于本地设置。门禁只按暂存内容判断是否触发；相关路径若同时有未暂存或未跟踪文件，会拒绝检查，避免结果与提交快照不一致。

提交前的完整离线验收统一运行 `.\scripts\run_offline_checks.ps1`：语法、全项目 MyPy、Black API 格式、AxData 摘要一致性、数据访问、字典同步、Canonical contract、registry parity 和离线测试都在同一入口执行，真实网络测试不会被启动。Black 检查读取 Git 可见的 Python 文件，使用 `pyproject.toml` 配置的 Python API，以避免 Windows 下 CLI 无输出挂起。

## 字段采集与研究

当 `capture_field_probe.py` 的数据日为最近已完成交易日时，`closed`、`pre_open` 与 `non_trading_day` 阶段可调用 `axdata_daily_validation.py`；盘中和集合竞价阶段不主动探测。允许完整采集，或 `--only` 明确选中 AxData 与 Tencent 两个主动探测必要源；项目 Tencent 对照失败时不发请求。每个有效数据日最多请求一次已核准的 Tencent `tencent_realtime_snapshot`，仅在双方 `quote_time` 与日期完全相同时比较字段。周末和节假日默认把数据日设为最近交易日，因此可核验上一完整交易日；实际采集时刻不设 15:30 门槛。被动短线/ELTDX 与 KPH/KPL 对照按双方共同有效交易日配对，不以采集目录日替代来源数据日；只有相关源对本次均被选中且成功时才更新对应身份样本。该日轮换的是样本股票，不是 AxData 的 257 个接口；其他接口仍按交叉表候选待审。至少 3 个不同交易数据日、3 只不同股票且每份样本至少 5 个非空信息字段匹配、没有数值失配后，接口标记为运行上（部分）冗余并停止每日探测；未决/语义冲突字段继续展示。每 20 个后续有效数据日启动复验，需 3 个新有效样本；映射指纹、返回字段结构变化或复验差异会恢复日常探测。状态保存在本机 `.tmp/axdata_daily_validation_state.json`，每日证据写入数据日目录的 `axdata_validation.json`；碰撞报告显示状态和未决字段，但不把 AxData 当独立锚或自动更新主字典。非最近数据日、盘中或集合竞价阶段、必要源未选中或对照源失败时不发主动请求；零请求跳过后可同日重评，已发请求同日不会重复。Eastmoney push2 不在白名单中。403/429/封禁立即暂停 Tencent 探针，连续两次空响应也暂停。超过 30 分钟的残留日锁会原子回收。

实际生产路由另有独立退出状态：`stock_shortline_indicators_tdx` 与 `eltdx.stocks.*.shortline` 比较，`kph_limit_up_history` 与 KPL 比较。每条路由至少要求 3 个不同有效交易数据日、每日至少 18 只配对股票；短线至少 5 个信息字段逐值全匹配，KPH 的六个已知字段全部匹配且没有额外未识别数值字段，才会暂停该接口的日常采集。双方来源日期相同且不晚于最近已完成交易日即可成为样本；来源日不同、源未被本次选择或源采集失败时不累计。暂停后采集器不再请求冗余接口；仅当参考源成功且 `as_of_date` 与目标数据日一致时，每个不同有效数据日才计入 20 日复验倒计时，同日重复运行只计一次。复验到期后接口恢复请求并收集 3 个新交易日样本；复验期间仍从默认碰撞中排除，直到失配或结构变化重开状态。未识别字段使路由保持采集并在证据中列出。短线请求收到 403、429 或封禁信号时立即停止该轮剩余股票请求，并将该路由持久标记为 `blocked_until_manual_review`；即使通过 `--only axdata` 或 `--only kph` 运行也会记录。人工复核封禁优先于契约变化，不会自动重试；成功快照也不能解除封锁。确认源恢复后，删除 `.tmp/axdata_daily_validation_state.json` 可清除该文件中的路由决策并从限量采样重新开始。状态损坏时不会自动覆盖。AxData 身份结果进入碰撞辅助报告，但不是碰撞锚。

`capture_field_probe.py` 同时调用 `levistock_daily_probe.py` 与 `levistock_daily_validation.py`。完整采集或 `--only market_sources` 在目标数据日为最近已完成交易日且数据阶段为 `closed` 时，每个数据日最多从 7 个数值候选接口中轮换一个额外请求；盘前、周末和节假日运行可沿用最近完整交易日作为数据日。请求经 `stock_common.sc_datasource.get_levistock_candidate_sample` Tier 2 适配器执行，要求安装版本符合 `requirements.txt` 中的 `levistock==0.1.8`；候选可比性由明确的请求交易日或响应交易日证据判断。适配器按 CLS/KPH 源族限流，遇到 403/429/封禁即持久暂停对应源族。候选响应写入独立的 `levistock_candidate_raw.json`，不自动并入碰撞锚；离线核验器复用 `raw_market_sources.json` 并生成 `levistock_validation.json`。完整快照同日重跑会跳过主源请求、检查/补齐每日核验；候选 raw、AxData 证据和每日状态保留，同日不重复探测。若之前因对照源缺失而零请求跳过，使用 `--overwrite` 恢复主源后可在同日重新评估；实际候选请求一旦启动仍会由每日状态阻止重复。详见 `docs/levistock_source_reconciliation_20261010.md`。

FTShare 的旧私有托管 MCP/SDK 已退役；旧 `FTShare` 身份下的 15 条字段路径、镜像文档和历史 raw 只用于历史研究。公开 REST 网关则是独立的当前运行源：`capture_field_probe.py` 默认注册 `ftshare_rest` 采集器，通过 `stock_common.sc_ftshare` 调用 `A股行情列表`，写入数据日目录的 `raw_ftshare_rest.json`。官方接口表定义的 31 个返回字段已登记为语义契约锚，`collide.py` 默认读取这些字段并与未知字段对撞；达到统计门槛的强匹配单列 `L1-C`，不冒充独立来源 `L1/L1-U`，也不自动改主字典。实时报价须与目标有效交易日一致，不能作为历史收盘值。单次采集最多 200 个代码、每页最多 40 个，页间隔至少 2 秒；无自动重试，403/429 立即停止当前源，错误响应正文不落盘。认证从被 Git 忽略的 `credentials/ftshare_api_key.txt` 读取，也可用 `FTSHARE_API_KEY` 环境变量覆盖；程序不打印或写入密钥。`symbol_id` 目前只有单次响应观察证据，未列入官方返回字段契约，不参与语义锚。接口字段、日期边界及 L1-C 规则见 [`FTShare REST 采集与碰撞契约`](../docs/verify/ftshare_rest_contract.md)；全接口目录见 [`ftshare_contract_catalog.json`](../docs/ftshare_contract_catalog.json)。

采集与碰撞是两个独立步骤：采集器保存 AxData `axdata_validation.json` 和来源状态；FTShare REST 则保存常规 `raw_ftshare_rest.json`。`collide.py` 读取交易日窗口内的归档，并在 JSON/Markdown 报告中展示逐日状态、被动比较计数、AxData 静态接口队列及 FTShare 契约锚候选。相同有效数据日的重复采集目录只计一次。默认碰撞排除已确认冗余的 AxData 生产路由和旧 FTShare 私有 MCP 历史 raw，但包含 FTShare REST 文档定义字段；这些匹配以 `L1-C` 单列，不计独立来源家族、不自动定案。`--all` 与 `--exploratory` 可显式读取旧 FTShare 历史 raw。AxData 其余 257 项仍是静态候选，不因路由复验而自动联网采样。碰撞不会替代接口安全审定或额外发请求。

每次碰撞也会把观察到的字母字段与注册表 `(source, 完整 code path)` 精确关联，输出拼音、英文、缩写和混合拆词候选；同时标出注册状态、样本日期和候选来源文件。候选只是名称检索线索，不自动确认字段。候选覆盖区按未知目标逐字段汇总可比字段、来源血缘跳过、候选数及本地覆盖日期；全局明细上限之外另保留每个目标的一条前沿候选。多个候选时，报告会给出按股票留出的预测分歧复核点，并在有限输入候选上搜索受约束的双输入乘积、比值、和差公式。已登记映射和已证伪关系提供正/负向方法覆盖计数。以上新增线索保持候选状态，不修改定案规则。完整详情保存在碰撞 JSON，Markdown 显示优先目标和有限摘要。L1 精确匹配继续要求每日至少 18 组有效样本、3 个独立日期，并新增每日至少 5 组信息配对；双方同时为零或同时缺失不参与精确命中率，单侧零值仍按失配处理。

| 脚本 | 用途 |
|:---|:---|
| `capture_field_probe.py` | 按来源分别采集字段样本至 `docs/field_verification/<数据日>/`；串行调用各源，沿用适配器限流，记录逐源错误、缺股、deferred 与来源数据日。东财 `push2` 样本先请求 `push2delay`，只有某只股票的 delay 请求失败才逐股回退主域 `push2`；不会在 delay 成功后再重复请求主域，也不单独运行已退役的 `push2_full` 全量采集器。东财 HTTP 请求共享跨进程全局间隔，并按 push2 家族 0.25 RPS、push2ex 0.6 RPS、push2delay 1.0 RPS 分组限速；全局及分组时隙原子预留，403 连续计数和停止状态也按风险组隔离。KPL 市场接口保存原始响应字段，新增板块强度源；涨停明细按 `PidType=1…5` 分层采集，保存原始列与层级身份，复用 1 秒请求间隔。AxData `kph_limit_up_history` 单次批量写入 `raw_kph.json`，不缓存、不重试，并与 KPL 对撞；短线 TDX 路由与 ELTDX 逐股比较，原始快照保留 bid/ask 五档价格及对应 `_vol` 数值，不改写源单位。两条 AxData 实际路由各自满足三交易日、每日 18 只配对股票及全字段规则后停止日常采集，20 个后续有效数据日后用三个新数据日复验；确认路由也从默认碰撞排除，复验期间仍排除，失配/结构变化即重新纳入。未知数值字段保持路由活跃。403/429/封禁立即停止 AxData 短线剩余请求并持久暂停相应路由；单独 `--only` 也记录状态。可用 `--only kpl` 或 `--only kph` 单独补采。该补充不替代 KPL 完整名单，也不增加独立 Eastmoney push2 采集。默认仍跳过纯上下文的交易所龙虎榜、东财人气榜和市场源/Fuyao 中的龙虎榜与热股榜子路径；上下文可用 `--include-context` 恢复，或通过 `--only exchange` / `--only em_hot` 明确选择。 |
| `collide.py`、`collision_dates.py`、`collision_rules.py`、`collision_candidate_reviews.py` | 共用日期归一化与快照择优；行情窗口按有效交易日，`as_of_date` 不在所选交易日窗口内的行情快照会排除并记诊断；新闻/公告按自然日。L1 检查样本量、独立日期和来源族。默认排除交易所/东财人气榜源及市场源/Fuyao 中的上下文记录，也过滤历史 raw；需纳入研究时加 `--include-context`。其他带 `collision_eligible=false` 的子树仍按来源元数据排除并在报告诊断中说明。候选报告逐字段展示来源覆盖、候选缺口、按股票留出的区分点、受约束公式线索及正/负向校准统计；数值范围不重叠只作诊断，不过滤单位换算或仿射候选。完整方法候选保存在 JSON `method_candidate_inventory`，`report_completeness` 对账生成/保留数量和 Markdown Top-N 展示差额。schema 5 另为候选附稳定 ID 与人工处置状态；审阅状态写入 `collision_candidate_reviews.json`，候选审阅工具默认预览，只有 `--apply` 才追加记录。`accepted_for_adjudication` 是进入既有定案流程的前置条件，不会直接改主字典；重复成员保留到代表项的反向关系。机器完整性与人工审阅覆盖率分开统计。完整性不通过时不得据报告做无候选或定案结论。候选方法不改变 L1/L1-U 条件或主字典。盘中/未知阶段仅作候选，所有结果保留日期及来源证据。详见 `docs/field_verification/DAILY_RUNBOOK.md` 与 `docs/field_verification/CRACKING_METHODOLOGY.md`。 |
| `context_policy.py` | 采集与碰撞共用的上下文源及路径策略，避免默认过滤规则漂移。 |
| `field_meta.py` | 为采集样本补充来源与锚点元数据。 |
| `crack_push2_status_codes_20260921.py` | Push2 状态码研究脚本。 |
| `crack_ulist_f88_95_20260921.py` | Ulist 高位字段研究脚本。 |
| `crack_zhb_anchored_20260921.py` | 基于锚点样本的 ZHB 字段研究脚本。 |

采集启动行会显示 `--only` 中实际选择的源，未指定时显示“默认源集合”，并单独标明市场上下文是“启用”还是“跳过”。

### 字段采集覆盖与生命周期

主字典字段变为 `verified` 后，碰撞脚本只将它从“待破解目标”中移除，仍保留为独立锚点；采集器不读取字段状态，因此已定案字段会继续进入每日样本，用于复核和漂移监测。接口因来源身份重复而暂停请求是另一项独立的源级决定，不由字段定案触发。

采集覆盖回归遍历本轮注册表中的 2,550 条 `source_fields` 记录，逐条检查来源身份能解析到日常采集器，只有已退役重复源与历史未归属记录使用明确例外。该回归证明字段记录没有因 `verified`/`unverified` 状态而失去来源路由；它是静态源级路由检查，不代表每个接口字段在某次样本中都实际返回。实际 raw 与登记字段的双向差异由 `audit_field_completeness.py` 检查，并结合 `meta.json` 区分未选源、请求失败、稀疏字段和采集遗漏。新浪扩展 API 的 27 项拆为 7 项可采集字段、17 项因缺少期权合约池而暂停、3 项无可靠接口路径而待补证；三类状态都由采集 raw 的 `__source_meta__` 记录。百度 K 线 3 个 MA 字段默认保持 `pending_validation`，仅 `--only baidu` 时限量请求；首次请求或响应契约失败即停止本轮剩余代码，避免对不稳定接口批量施压。

字段语义定案与采集生命周期相互独立：已验证字段继续每日采集，只作为锚点退出未知字段的重复破解。TDX 字段采集保存原始 adapter 快照于 `quote_raw`，并从其直接计算 `quote_full` 行情路径；不会把 ZHB/Tencent 回退值标作 TDX。空行情或财务结果会留下逐股错误标记，防止空数据被统计为成功。`audit_field_completeness.py` 同时报告采到但未登记、登记但本次未观察到两类差异；后者还需结合采集范围、来源状态和字段稀疏性判断，不能直接等同于漏采。

每日采集遇到单次超时、连接重置、临时 DNS 故障或 HTTP 408/5xx 时，先使用请求层已有的有限重试：通用同步/异步请求按调用方 `max_retries` 的总尝试次数（含首次请求）对传输异常和 408/5xx 做有界退避；Eastmoney `em_get` 对连接/超时异常和 408/5xx 最多额外请求一次，并重新执行令牌桶与跨进程限流。Eastmoney 全局节流与 push2 家族、push2ex、push2delay 的风险组节流在同一锁内原子预约；分组速率上限分别为 0.25、0.6、1.0 RPS，另受全局最小间隔约束，属于保守本地策略而非上游限流承诺。共享请求层收到 403/429 不重试，push2 显式设置 `max_retries=1` 时保持单次尝试；连续 403 按风险组计数，push2 家族别名共享，push2ex 和 push2delay 单独计数。首轮仍不完整且来源策略允许时，可对失败源做一次串行 `--only <source>` 补采。补采会覆盖该源的 raw 文件，必须先备份原 raw 与 `meta.json`，再比较来源日期、必需路径、样本覆盖和错误数，只保留不丢失已有成功样本且确实改善的结果。403/429、封禁或熔断最终返回后不做采集器级补采；永久参数/契约错误也不重复请求。遵守适配器内部限次和各源更严格的防封限制。完整操作步骤见 [`DAILY_RUNBOOK.md`](../docs/field_verification/DAILY_RUNBOOK.md)。

`audit_field_completeness.py <采集目录日期> <报告日期>` 会把全部成功或部分成功的股票记录、列表响应中的全部行与登记字段做双向比较：`raw not registered` 是采到但字典未登记的候选，`registered not observed` 是本目录没有观察到的登记字段。另将 `levistock_candidate_raw.json` 中 `status=observed` 的 payload 按 candidate_id 和 provider_family 单列；探针元数据不当作字段，候选也不并入任何来源的独立碰撞锚。后者可能来自源未选择、请求失败、字段稀疏或明确暂停，不能单独判为采集器遗漏；需结合 `meta.json`、源状态和字段处置说明判断。报告 JSON 同时保留两类差异，不会把空目录误报为完整。

Fuyao REST 的 Key 读取顺序为官方变量 `HITHINK_FINANCE_API_KEY`、兼容变量 `THS_FUYAO_API_KEY`、被 Git 忽略的 `credentials/fuyao_key.txt`；程序不输出 Key。逐字段审定的 Fuyao 官方契约证据会列入碰撞报告来源统计，但 Fuyao 的来源独立性已确认，仍走普通 L1/L1-U 锚。只有底层数据来源未确认、且明确登记为官方契约锚的来源才走 L1-C。

`collide.py` 的 `source_coverage` 报告分列每个运行源的已确认字段、官方契约字段、窗口观察字段/字段值样本/交易日、目标/右侧比较次数及 L1/L1-C/L4 关系数；这些数量经过快照日期、择优和类型筛选，不能当作原始请求数。Fuyao 集合竞价的响应 `timestamp` 另存上海时区日期，但标记为响应组装时间；没有上游显式数据日时，仍排除该竞价子树，不用响应日期补造行情日期。

## 架构支持模块与维护验收

| 模块 | 职责 |
|:---|:---|
| `capture_catalog.py` | 采集器源配置、字段族和来源契约目录。 |
| `capture_diagnostics.py` | 响应、错误、数据日和 ZHB 新鲜度诊断；保留原采集入口兼容名称。 |
| `capture_archive.py` | ZHB 快照保护、上下文保留及归档完整性/覆盖刷新。 |
| `capture_context_collectors.py`、`capture_tcp_collectors.py`、`capture_verified_collectors.py`、`capture_http_collectors.py` | 按来源族实现采集 producer；`capture_field_probe.py` 继续持有 CLI、日期/覆盖编排、注册表和落盘。 |
| `stock_common/sc_network_limits.py` | 纯跨进程间隔等待与锁文件机制；所有限流、熔断状态仍由 `sc_network.py` 单一持有。 |
| `collision_snapshots.py`、`collision_math.py` | 碰撞快照身份/筛选，与纯数值、公式候选方法。 |
| `collision_candidate_methods.py`、`collision_registry_context.py`、`collision_candidate_triage.py` | 碰撞候选计算、只读来源/registry 上下文与覆盖 triage；`collide.py` 保留运行编排和兼容名称。 |
| `collision_candidate_ranking.py`、`collision_state.py`、`collision_reporting.py` | 候选排序、碰撞状态读写及报告序列化。 |
| `collision_candidate_reviews.py` | 独立候选审阅台账；`review_collision_candidates.py` 默认预览，显式 `--apply` 才记录处置。 |
| `collision_adjudication_validation.py`、`collision_adjudication_transformations.py` | 裁决输入验证与内存对象变换；裁决 CLI 和唯一原子写入仍在 `apply_collision_adjudications.py`。 |
| `stock_common/md_render.py` | 五大报告共用的 Markdown 表格与文本转换。 |
| `axdata_crosswalk_summary.py` | 从规范交叉表生成并校验轻量运行时队列摘要。 |
| `verify_python_syntax.py`、`verify_black_api.py`、`run_offline_checks.ps1` | 语法、Black Python API 和完整离线验收入口。 |

交叉表摘要只作派生计数视图；完整接口/字段证据仍保存在 `docs/axdata_interface_crosswalk.json`。更新源文件后执行 `run_with_system_python.ps1 scripts\build_axdata_crosswalk_summary.py`，不可手工修改派生摘要。

## 字段登记、生成与治理

| 脚本 | 用途与写入行为 |
|:---|:---|
| `extract_registry.py`、`field_registry_api.py` | 从主字典提取登记信息；后者是多个治理脚本共用的内部 API。 |
| `registry_parity.py` | 校验登记表、主字典投影和字段矩阵；历史 TDX 五档 token 与当前 bid/ask 原始路径、以及仍采集的 Fuyao 上下文标签通过 `registry_parity_scope.json` 逐项注明证据和采集范围。未列入清单的新差异仍会失败；治理运行器的接受差异清单只用于另行审定的 parity debt。 |
| `apply_collision_adjudications.py` | 默认预览，显式 `--apply` 后才写 registry 和生成视图；支持 L1 碰撞、固定版本的单源上游契约，以及有来源独立性检查和 CSV 复算的公式关系定案。校验与内存变换委托给相邻模块；公式样本留档于 `docs/field_verification/derived_evidence/`，不自动联网、不建立输入字段映射。 |
| `derived_relation_evidence.py` | 定案器调用的公式证据校验模块；限制算术语法与本地样本范围，核验来源族、已验证输入、有效日期和样本误差。 |
| `gen_field_dict.py`、`gen_field_matrix.py` | 生成字典/矩阵片段；`--check` 只检查、不写入。 |
| `gen_ulist_subdict.py`、`gen_zhb_subdict.py` | 生成对应接口的字典子表及镜像。 |
| `audit_field_completeness.py`、`audit_field_source_quality.py`、`lint_field_names.py`、`lint_field_same_number.py` | 分别审查归档样本字段覆盖、已验证登记的语义元数据质量，以及命名和编号；质量审计只读 registry，不会自动改状态。 |
| `archive_field_preflight.py` | 检查字段采集归档的 Markdown 契约。 |
| `verify_data_access.py`、`verify_sync_check.py` | 分别检查生产数据访问边界和字典/代码同步；同步检查会更新审计报告。 |
| `cleanse_dict_provenance.py` | 整理字段证据叙述；默认 dry-run，`--apply` 会改写字典并追加溯源记录。 |
| `cleanse_dict_verif_narrative.py` | 生成字段结论列清理建议；默认 dry-run 不写文件，需显式传 `--plan-output <路径>` 才保存计划；`--apply` 会改写字典并追加溯源记录。 |

## 报告、数据与维护

| 脚本 | 用途 |
|:---|:---|
| `backtest_topn.py` | 基于本地历史数据回测 Top-N 选股。 |
| `check_em_health.py` | 低频按主机/接口诊断东方财富；共享限流、单次请求、封禁后停止同族探测，JSON 仅写入 `.tmp/eastmoney_health/`。 |
| `clean_cache.py` | 调用统一缓存清理入口；清理范围以 `--help` 为准。 |
| `fmt_preview.py` | 离线预览报告 Markdown 渲染。 |
| `perf_compare.py` | 本地数据结构性能对比。 |
| `update_calendar.py` | 更新本地交易日历数据。 |
| `upload_reports_to_gd.py` | 补传 Google Drive 报告；支持先预览待上传项目。 |
| `backup-opencode.ps1` | 备份本机 OpenCode 配置。 |

会改写字典、矩阵、采集记录或审计报告的工具，先检查其写入目标和工作区状态。`cache/` 里的 SQLite、K 线和 ZHB 快照不是同一种缓存；不要通过删除整个目录来代替有范围的清理。

### 东方财富端点诊断

使用 `check_em_health.py` 对照主机和接口的 HTTP 状态、响应大小、JSON 结构、返回日期线索及耗时。默认每个选中端点只请求一次，调用共享 `_quick_request` 限流；本地封禁/熔断记为 `suppressed`，不发请求。遇到封禁、403/429 或传输故障后停止该 push2 风控族剩余探测，但继续独立主机族；不自动重试、不轮换 IP，也不把 `push2delay` 的成功推断成实时数据。

```powershell
.\scripts\run_with_system_python.ps1 scripts\check_em_health.py
.\scripts\run_with_system_python.ps1 scripts\check_em_health.py --probe push2his
```

JSON 默认写入仓库 `.tmp/eastmoney_health/`。退出码 `0` 表示所选端点返回预期结构，`1` 表示实际请求或结构失败，`2` 表示被本地保护跳过或返回空样本、结论不确定。涨停池接口按 `data.pool` 校验，`rc=205` 表示请求日期无记录。`calendar_reference_date` 只是交易日历基准；`requested_data_date` 与 `returned_data_dates` 分开记录，快照端点没有显式数据日期时不推断来源日期。

日采集 `meta.json` 的 `sources.<source>.error_diagnostics` 保留分类计数，并包含最多 20 组结构化错误明细（`code`、`phase`、`request_attempt_state`、`retryable_hint`、`risk_family`、`host`、`http_status`、脱敏 `raw_error` 与路径样例）。明细由错误标记文本推导，`retryable_hint` 不参与重试或熔断决策；它不证明上游服务器实际收到请求。原始错误仍保留在 raw 归档中，调查时以 raw 和逐请求记录为准；超出的分组数记在 `omitted_detail_groups`。

## 报告 Markdown 约定

- 报告目录保存可追溯的历史快照；不要批量重排或改写历史报告。
- 每份新报告在开头保留报告类型、股票/范围和生成时间；有可靠来源时另列数据日期或快照日期。生成时间、任务目标日期和来源数据日期是不同概念，不得互相推算或替代。
- 来源不可用、字段缺失、降级来源和单位口径应在对应章节明确呈现，不以空白内容伪装成功。
- 使用 Markdown 标题和标准表格，表头标注单位；行尾空格只在确实需要 Markdown 强制换行时保留。
- 预览、渲染和临时对比文件放在仓库 `.tmp/`，不写入 `reports/` 正式快照目录。
