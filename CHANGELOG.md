# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### 文档与仓库清理

- `.tmp/` 运行时按需创建并整体忽略；移除 Git 占位文件，避免远端显示临时目录。
- 删除 7 份已完成的一次性计划，文档索引改指向最终审计、闭环和兼容性记录；未完成、待决策及原始字段证据继续保留。
- 从当前文档中清除本机账号/调试信息、用户目录路径和私网地址；凭据目录明确加入 Git 忽略规则。

## [V17.4.32] 2026-10-08 — AxData TDX 短线采集诊断

### 采集与来源说明

- 修正 AxData 统计 ZIP 搜索路径，改为读取仓库根目录 `cache/zhb`；之前错误地查找 `stock_common/cache/zhb`，因此即使本地存在缓存也会提前返回空结果。
- 新增带状态的短线接口结果：区分 ZHB 缓存缺失、接口无可用记录和请求异常；保留旧字段字典接口及交易日缓存契约，失败结果不缓存。
- 采集 raw 错误明确标注 AxData `stock_shortline_indicators_tdx` 的 TDX 路径；文档说明 AxData 是多提供方框架，当前项目只采集其中这一条接口，且实时输入可能访问 TDX 网络。
- 修正兼容测试中错误的模块相对缓存路径，并覆盖三类失败诊断与 `stats_date` 保留。
- 验证：离线套件 731 passed、1 skipped、47 deselected（98.34 秒），新增兼容测试 6 项（总通过数 725 → 731）；4 个改动 Python 文件语法、mypy 与 Black 通过，A1/A7 闸门 0 HARD FAIL / 0 WARN。9 条既有 `httplib2`/`pyparsing` 弃用警告。

## [V17.4.31] 2026-10-08 — 字段破解采集去噪

### 采集与碰撞

- 默认采集跳过沪深交易所龙虎榜与东财人气榜；市场指标和 Fuyao 个股、财务、竞价等字段继续采集，只跳过龙虎榜与热股榜子路径。显式 `--include-context` 可恢复上下文采集，单独 `--only exchange` / `--only em_hot` 也视为明确选择。
- 碰撞默认过滤上述来源和历史 raw 中的龙虎榜/热股榜子路径，并在诊断中记录排除情况；`--include-context` 可将已归档上下文样本加入研究性碰撞。
- 默认重采保留之前显式采集的上下文 raw 子路径；不删除历史原始文件，不改报告脚本、适配器、缓存键、日期规则或主字典状态。
- 验证：离线套件 725 passed、1 skipped、47 deselected（125.16 秒）；5 个改动 Python 文件通过语法与 Black 检查，3 个生产模块 MyPy 零错误；A1/A7 闸门均 0 HARD FAIL / 0 WARN，敏感信息扫描与 `git diff --check` 通过。9 条既有 `httplib2`/`pyparsing` 弃用警告。

## [V17.4.30] 2026-10-08 — 项目体检与兼容性修复

### 采集、网络与对撞

- 腾讯逐笔适配上游 v3.10.1 的会话复用、受限重试和完整性判定：连接/握手/响应头超时、429 与 5xx 最多请求 4 次；403 和响应体读取失败不重试；盘后逐笔金额与快照字段核对后写入 `frame.attrs["complete"]` 三态结果。
- 流式 HTTP 错误响应在重试前关闭，避免连接池资源滞留；通用 HTTP 调用的默认 timeout 改为使用 `HTTP_TIMEOUT_SECONDS`。
- `tdx_get_board_members(sort_by_change=...)` 现在对 TDX 与 Eastmoney fallback 都按涨跌幅降序，关闭选项时保留源顺序。
- 碰撞脚本统一使用 `scripts.*` 包导入，并在直接运行时补入仓库根路径；增加 `scripts` 包标记，避免 MyPy 将同一日期模块识别成两个模块。

### 运行环境、测试与文档

- 项目最低 Python 版本统一为 3.11，推荐使用 3.12；ELTDX 固定为已回归的 `3.2.2`，开发依赖增加 PyYAML 类型存根。
- 项目启动及直接导入时统一使用仓库 `.tmp/`，保留 `ASTOCK_TEMP_DIR` 覆盖；移走 `reports/_preview_out.md` 到临时目录，历史报告保留，并补充生成报告的日期与 Markdown 约定。
- 校准 113 个 CanonicalStockData 属性、12 个 ELTDX 扩展、101 个非扩展属性和 38 项精选 FieldSpec 元数据的文档口径；测试说明模块数更正为 61。
- 未显式设置真实网络环境变量时，默认、单模块和表达式测试路径均不访问真实网络；默认全量模式显式排除 `real_network`，`-Mode real` 会在子进程期间临时启用。
- 验证：默认离线套件 720 passed、1 skipped、47 deselected（共收集 768 项，125.45 秒）；9 条既有 `httplib2`/`pyparsing` 弃用警告。MyPy、Black、语法、A1/A7、字段生成检查和 registry parity 全部通过。最终全量回归未运行真实网络用例或采集；修复测试闸门前，早期定向回归曾意外触发 2 个 `real_network` 只读冒烟测试（腾讯逐笔、新浪期货），均通过，随后修正闸门并复跑全量离线套件。

## [V17.4.29] 2026-10-08 — 项目内临时目录

### 开发环境

- 新增仓库根 `.tmp/` 作为 Agent、测试和项目工具的临时目录；目录内容忽略，仅保留 `.gitkeep`。
- `run_with_system_python.ps1` 和兼容 `.bat` 入口将 Python 及其子进程的 `TEMP`、`TMP`、`TMPDIR` 设置到 `.tmp/`，解决系统临时目录无访问权限时测试/工具无法创建临时文件的问题。
- 更新 Agent 规约、部署说明和脚本说明，要求项目临时探针、测试基目录和临时安装产物落在 `.tmp/`。

## [V17.4.28] 2026-10-08 — Levistock/AxData 适配兼容性

### 依赖与适配

- 将 `levistock`、`axdata` 固定到经隔离环境离线回归的 `0.1.8`、`0.1.4`；`requirements-dev.txt` 通过 `-r requirements.txt` 自动继承。
- 明确并回归 Levistock 实际方法、日期参数和涨停梯队 11 列转换；新版本未改变项目使用的接口。
- 核实 AxData 的 `stats_root` 接收项目 `stock_common/cache/zhb/` 下的最新 ZHB ZIP；显式路径直接读取 CFG，不刷新/下载统计包。短线指标的行情输入仍可能请求 TDX。
- 新增离线适配器与本地 ZIP 回归；未调用真实行情源、未更改限流和报告/采集业务逻辑。
- 验证：适配器回归 3 passed；全量离线测试 699 passed、1 skipped、47 deselected（125.89s）；新增测试通过 py_compile、Black、mypy；A1/A7 闸门 0 HARD FAIL / 0 WARN，`git diff --check` 通过。

## [V17.4.27] 2026-10-08 — Fuyao 竞价日期证据与上游兼容性

### 采集与碰撞

- Fuyao 新增完整信封适配器；采集归档保存信封摘要和逐项 `__source_meta__`。旧 `get_fuyao_auction_snapshot()` 继续返回列表，仍走 `fuyao_auction` 缓存分类和同一请求路径。新缓存键不能复用旧 list-only 缓存，首次相同参数调用可能回源一次；此后两种接口共享缓存。
- 竞价子树只有在响应成功、状态明确就绪、上游显式提供的数据日期与目标交易日一致时才参与对撞。响应时间不再被误当作行情日期；混合 Fuyao 文件的顶层 `probe_trading_day` 保持原用途。
- 碰撞器仅跳过明确标记为 `collision_eligible=false` 的子树，并在报告诊断中列出原因和源端元数据；其他 Fuyao 字段及没有新标记的历史 raw 不变。日期窗口、缓存日期与五大报告逻辑均未改变。

### 上游复核与验证

- 新增 [`docs/UPSTREAM_COMPATIBILITY.md`](docs/UPSTREAM_COMPATIBILITY.md)，记录已确认上游关系、近期变化与本项目的采用边界；本轮不升级依赖、不增加请求。
- 相关模块定向测试 77 passed；全量离线套件 696 passed、1 skipped、47 deselected（124.18s）。9 条既有 `httplib2`/`pyparsing` 弃用警告，无测试失败。
- 8 个改动 Python 文件通过 `py_compile` 与 Black；5 个改动源码模块 mypy 零错误；A1/A7 数据访问与字典同步闸门均 0 HARD FAIL / 0 WARN，敏感信息扫描和 `git diff --check` 通过。

## [V17.4.26] 2026-10-06 — 字段定案与来源确认闭环

### 字段治理

- 新增碰撞候选人工定案工具：默认只预览，仅允许绑定正式 L1/L1-U 报告、精确字段路径与独立 verified 锚；显式应用后同步逐源状态、兼容聚合视图、等价映射和生成文档。
- 定案记录保留报告、交易日样本、复核人、理由与决定 ID；只有人工确认的语义等价才写回，单个错误配对不把整个字段标为 disproved；冲突状态不可被碰撞候选覆盖，探索结果不自动晋级。
- 主字典入口链接独立破解方法论和定案工作流；每日采集/破解说明改为检查实际数据日期，不再使用 ZHB 恒为自然日 T-1 的过时表述。
- 来源谱系区分项目证据与用户对话确认。用户确认 7 条关系（含 ZHB 的 3 类缓存传输关系）；另外 21 个来源保持待确认，不推断仓库。
- 生成 verified 字段描述缺口清单：239 条记录缺规范名或含义；其中 207 条缺含义、47 条缺规范名、15 条两者皆缺。只报告缺口，不自动改变字段状态。
- 未改变采集器、缓存键、交易日算法或公开报告数据契约。

### 验证

- 离线测试：688 passed、1 skipped、47 deselected；新增定案/谱系/生成器定向测试 16 passed。
- 本轮 6 个 Python 文件通过 `py_compile` 与 Black，3 个源码文件 mypy 零错误；生成器、field matrix、registry parity、A7 同步和 A1 数据访问闸门通过，HARD FAIL/WARN 均为 0。

## [V17.4.25] 2026-10-05 — 字段注册、来源谱系与碰撞锚点重整

### 字段字典与来源

- 将主字段字典收敛为权威入口；完整历史字段证据保存在 `docs/field_source_reference.md`，机器状态以逐源完整路径的 `field_registry.json` 为准。
- 新增独立生成的未知字段队列、字段×源矩阵和来源仓库图；明确 verified、unverified、candidate、conflict、disproved 的处理口径。
- 将原文解析得到的 2,469 条 `(source, full_code_path)` 身份逐项纳入登记表，保留聚合视图兼容现有工具；无法判定来源范围的历史状态保留为证据并隔离，不冒充逐源结论。
- 新增 28 个采集源的来源谱系登记。仓库对应关系仅在仓库或本地实现证据可支持时标为 confirmed，其余保持 unconfirmed。

### 碰撞锚点与治理

- 默认对撞跳过已验证字段，只以完整路径匹配、来源独立性已确认的 verified 字段作为锚；同源或未知谱系不能作为独立证据。
- 未知字段互撞仅在 `--exploratory` 模式产生候选，不进入默认定案状态；报告附带模式、锚点和跳过原因统计。
- 更新 registry 提取、parity、字段完整度、来源同步、归档预检、清理工具和子字典生成流程，避免历史参考文档被误当作可写机器真相源。
- 版本升至 `17.4.25`；未改变行情缓存键、交易日规则或公开数据合约。

### 验证与迁移记录

- 原文 2,469 条 `(source, full_code_path)` 身份逐项覆盖：缺失 0、额外 0、重复 0；旧注册表 2,426 条来源关系及聚合属性全部保留，原文补入 43 条关系。
- 离线测试 676 passed、1 skipped、47 deselected；25 个 Python 文件通过编译与 Black 检查，18 个源码文件 mypy 零错误；A1/A7 闸门均 0 HARD FAIL / 0 WARN。
- 同一 32 个交易日的只读碰撞对比将理论配对上界从 751,842 降至 271,502；字段完整度历史复核仍有 TDX 68 项、TDX-F10 103 项命名/覆盖缺口，旧 THSDK 原始采集记录含导入错误，详见字段字典迁移审计。
- 完成逐项审计后删除临时主字典和注册表备份；原字典逐字节参考档案继续保留。

## [V17.4.24] 2026-09-30 — 采集可靠性与交易日对撞证据治理

### 对撞与采集日期

- 新增共享日期/快照规则，分别保存采集日期、来源数据日期、实际采集时间和自然日事件日期；行情窗口按不同有效交易日计数，事件仍按自然日筛选。
- 历史周末或休市日目录不删除、不改名；无显式数据日期时，行情快照按项目交易日历归并到此前最近交易日并告警，显式日期无效的行情快照则跳过。重复快照按完整度、状态和采集时刻择优。
- 采集器默认选择最近已完成交易日；显式行情日期须为有效交易日，新闻/公告等事件源仍接受自然日。
- 通用对撞和专题脚本共用日期与来源规则。L1 要求每日最低样本量、至少三个独立交易日和独立来源族；盘中或阶段未知样本只进入候选。新增语义、公式、时间序列和稳健相关性候选，并保留样本日期与来源证据。
- 修正治理闸门路径匹配，归档的 `field_registry.json.bak_*` 不再误触发正式注册表 parity 检查。

### 采集器可靠性

- 逐源核验必需结果、应采股票覆盖、错误标记和 deferred 状态；`None` 返回或缺少必需结果不再被当作完整成功。幂等跳过要求上一轮元数据状态和 raw 文件均完整；`--only` 会重新采集指定来源。
- 市场级子源逐项隔离异常。本轮调整的 Eastmoney 直连请求使用单次尝试并保留传输诊断；push2、clist、slist 在 IP 封禁、403/429 或连续失败后熔断相应域。采集仍按来源串行执行并遵循 `sc_network`/TDX 既有域级与跨进程限流。
- 将 AxData 的来源 scheme 更正为独立的本地短线指标体系；元数据新增实际采集时段和可确认的来源数据日。
- 专项回归：`tests/test_capture_field_probe.py` 35 项通过；本次未发起真实数据源请求。

### 验证

- 离线测试：649 passed、1 skipped、47 deselected；数据访问闸门通过；本轮相关 Python 文件 `py_compile`、Black 与 mypy 检查通过。

### 既有未发布修复

- FTShare 董监高变动的 `change_date` 现在按 180 个交易日筛选，独立的 `notice_date` 仍表示公告日期。

### 修复

- 调度器现在会把缺失报告脚本、子进程异常/非零退出和不完整结果正确报告为失败，避免误报成功。
- 统一限售解禁数量的股数换算，并升级对应缓存类别，防止旧单位缓存继续被当作股数读取。
- 修复工作日/交易时段边界与 ZHB fallback 处理，并为报告入口增加缺失数据和参数保护。
- 修正字段采集探针的 Eastmoney 龙虎榜请求参数；恢复该采集器要求的进程间等待，避免请求绕过限速。
- 修正若干字段登记、生成器、报告和类型边界问题，补充对应回归测试。
- 统一 ZHB 数据新鲜度、行情年龄、龙虎榜与近期交易数据查询窗口的交易日口径；日历生成器和行情回退也不再把周末补班日当成 A 股开市日。
- 修复交易日历生成器未插入节假日/工作日数据表的问题；更新时只替换日期数据，保留项目自定义日历逻辑。
- val 无法取得全市场快照时仍保留诊断文件，但现在以失败退出且不将空数据报告当成成功上传。
- 收紧主字段字典的来源继承与章节映射，清理重复来源记录；字段登记从 1,820 条增至 1,831 条，字典/矩阵 parity 检查通过。

### 维护

- 按项目 Black 配置统一 154 个源码及测试 Python 文件；修复类型问题后，mypy 对配置范围内的 140 个源码文件零错误。
- 更新项目上下文、文档索引和测试目录清单，使 Python 目标版本、测试模块数和验证入口与当前仓库状态一致。
- 未更改公开字段契约、ZHB 列索引或缓存键语义（限售解禁缓存类别升级除外）；项目版本升至 `17.4.24`。

### 验证

- 离线测试：564 passed、1 skipped、47 deselected；真实网络测试：41 passed、6 skipped、565 deselected。
- Black：154 个文件通过；mypy：140 个配置范围源码文件、0 errors；`py_compile`：154 个源码/测试文件通过。
- A1/A7 闸门均为 0 HARD FAIL / 0 WARN；`git diff --check` 通过。

### 全仓文件精简复核

- 清理失效的拆分、README 同步与本地临时工具脚本；保留原始采集、缓存、备份和字段研究证据。
- 修正文档中的过期依赖、TDX/ZHB 下载顺序、缓存清理范围和测试目录清单；为字典清理工具补上无副作用的默认 dry-run。
- 对 5 个报告入口核实依赖与死代码，移除已确认的未使用导入、局部变量和不可达分支；补齐 SZSE 官方 XLSX 回退所需的 `openpyxl` 运行依赖。
- 验证：离线测试 621 collected，573 passed、1 skipped、47 deselected；Black/`py_compile` 检查本轮 16 个 Python 文件通过，mypy 137 个配置范围文件 0 errors，A1 为 0 HARD FAIL / 0 WARN。

## [V17.4.23] 2026-09-24 — 报告数据质量修复：ST名单None渲染 + med/lng一致预期源统一

- **问题1 ST名单表 None 字面渲染修复（`stock_common/sc_market_signals.py` `render_st_list_section`）**：val 报告 `【L. 风险警示（ST/*ST）名单】` 节在源可达但个别字段（现价/涨跌幅）为 `None` 时，原代码直接 `r.get('price')`/`r.get('pct_change')` 拼入表格，致渲染出字面 `None`（如 `| 873841 | sz | ST祥盛 | ST | None | None |`），与该节"待源恢复"标题自相矛盾。现新增 `_cell(v)` 辅助：对 `None`/空串统一转义为 `—`；章节标题改为按真实状态动态生成（源异常→`· 待源恢复`+暂缓接入提示；空列表→`· 无数据`；正常→无后缀），消除误导。功能冒烟测试三分支全过。
- **问题2 med/lng 跨报告一致预期 EPS 矛盾修复（统一数据源）**：001330 中线 vs 长线报告对 `2026E` 一致预期 EPS 给出 `0.070`（3家机构）/ `0.120`（4家机构）矛盾值，致前向 PE `82.57x`/`48.17x`、PEG `0.44`/`0.89` 并存。根因：med 走 `get_eps_forecast_async`（纯网络实时），lng 走 `get_eps_forecast`（本地 ProfitForecast 快照优先），命中不同机构快照。新增共享解析器 `resolve_eps_forecast(session, code)`（`stock_common/sc_datasource/_financials.py`）：以网络实时一致预期为主源、本地快照为兜底，med/lng 共用同一函数，确保解析链路与数据快照完全一致。两报告 import 已注入、取数行已切换。
- 治理：纯运行时代码修复（不影响 field_dict/registry/verify 契约）；PYTHON=py 提交；未推送。

## [V17.4.22] 2026-09-24 — P0: tdxstat PE 列标反修复 + unknown_2/26 晋级 L2 候选

- **P0 PE 列标反修复（`core/zhb_client.py` `_parse_tdxstat`）**：tdxstat.cfg `[3]`/`[9]` 原误标 `[3]=pe_dynamic`、`[9]=pe_ttm`。经独立实证（000858 五粮液：ZHB `[3]=20.87`≈TDX 实时 TTM `20.67`、`[9]=30.49`≈TDX 实时静态 `30.20`；与 fuyao `pe_ttm` 20/20 吻合）确认实为 **`[3]=TTM`、`[9]=静态LYR`**。现修正解析器字段名：`pe_ttm←col[3]`、`pe_lyr←col[9]`，并移除错误 `pe_dynamic` 键（ZHB tdxstat.cfg 无动态 PE 列，动态 PE 来自 push2 f162，下游 `zhb_dict.get('pe_dynamic')` 自然回落实时源，未崩溃）。顺带修复下游 `data_provider` 取 ZHB 兜底 `pe_ttm` 原误喂 LYR 值的隐性 bug。
- **`stat.unknown_2`/`stat.unknown_26` 晋级 L2 候选（sanctioned 管线）**：经 `extract_registry → gen_field_dict → parity` 三闸门（`G1`/`G3`/`P1` 全过），`stat.unknown_2` 落定为**贝塔系数(60日)**、`stat.unknown_26` 落定为**年内涨停天数 YearZTDay**。`field_dict.md` §12.1 列 `[2]`/`[26]` 早已定 `BetaValue`/`YearZTDay`（✅），本次在 `stat.*` 汇总表补齐语义并标 **L2 候选**（ihelp.dat L63/L64 官方定义逐字命中 + 慢变特征/事件级Δ实证）。**四铁律**：deepseek 自报命中 82.81% <90%，按本方治理仅定 L2、未越级 L1；待真实指数基准复现 / ≥90% 命中升 L1。
- **§三 PE 命名旧警告（已于本回合善后订正）**：原 `field_dict.md` §三 关于 Col[3]/[9] 命名的旧警告（"Col[3]=pe_mrq, Col[9]=pe_ttm"）与本次代码实证相反，系早期由误标代码循环推导所致；本回合已 sanctioned 修订推翻（见下方「PE 命名全文档订正」条）。
- **L2 晋级善后（prose 一致性）**：将 §12.1 `tdxstat.cfg` 节内两条旧"候选研判（⚠️，未定案）"块（原假设 `stat.unknown_2`=量比−1/`stat.unknown_26`=概念板块数）标注为"历史假设·已被 2026-09-24 L2 晋级 supersede"，并指向新定案块，消除与 L2 定案的直接矛盾（保留历史假设留痕，不改 registry，G1/G3/P1 全过）。
- **§三 PE 命名旧警告 + 全文档 PE 列语义订正（sanctioned 管线，本回合收尾）**：推翻 `field_dict.md` §三 旧「命名颠倒」论断（原称 Col[3]=pe_mrq/动态、Col[9]=pe_ttm），并同步订正 §12.1 权威列定义表（[3]`pe_dynamic`→`pe_ttm`、[9]`pe_ttm`→`pe_lyr`）、§12.1 引言（行 65）、tdxstat.cfg 字段列举（行 1192）、PE 源优先级矩阵（行 4183/4186：pe_ttm→ZHB Col[3]、pe_mrq 移除 ZHB Col[3]）、行 5330（Col[9]=pe_lyr），以及 4 处「ZHB 提供 pe_dynamic」陈旧断言（行 234/3116/5679/5697——ZHB 自 V17.4.22 不再产出 pe_dynamic，动态 PE 仍由 push2 f162/腾讯[52] 提供）。§三 重写为 V17.4.22 实证订正块，指认原论断为「由误标代码循环推导」、外部金标准（ZHB vs TDX 实时行情 MCP）才是正确仲裁。重跑 `extract_registry → gen_field_dict → parity`，G1/G3/P1 全过；未 bump VERSION（仍 17.4.22）。
- **zhb_verify.md 镜像补全（HARD5 闸门修复）**：`docs/verify/zhb_verify.md` 镜像缺失主字典 §三 tipinfo 6 个标准契约 token（`equity_incentive_date`/`forecast_date_recent`/`forecast_type`/`hg_amount_yi`/`hg_date`/`suspend_major_event_date`），致 `verify_sync_check.py` HARD5 失败。重跑 `gen_zhb_subdict.py`（自带 parity 自检，tdxstat 35/tdxstat2 21/tipinfo 22 全 OK）重生成镜像；重跑同步闸门 **HARD FAIL 0 / WARN 0** 全绿。该断裂源自 V17.3.9/V17.4.8 历史提交、非本轮引入，纯文档镜像、不进运行时。
- 治理：含 field_dict/registry/verify 改动，G1/G3/P1 闸门全过；`PYTHON=py` 提交；未推送。

## [V17.4.21] 2026-09-24 — 历史非交易日目录清理 + 盘中→盘后刷新逻辑

- **历史非交易日目录清理（治标）**：扫描 `docs/field_verification/` 下所有 `YYYYMMDD` 目录，将「周末/法定节假日（运行日）命名」的目录修正为真实数据日（`get_last_trading_day(目录名)`）。真实数据日目录已存在者判为冗余→删除；唯一者→改名至真实数据日并修正 `meta.data_date`/`date`。共处理 8 个目录（7 删 1 改：20260822→20260821），清理后**零周末/节假日命名目录**，对撞数据污染根除。被删目录内的原始采集数据（raw_*.json）均已在对应交易日目录保全，仅删除了可在交易日目录重现的派生分析产物。
- **盘中→盘后刷新逻辑（治本补全）**：`scripts/capture_field_probe.py` 新增 `market_phase` 判定（运行时刻 vs 数据日 15:00 收盘）。幂等跳过逻辑改为：①盘后已有=完整→幂等跳过；②盘中已有且本次仍盘中→跳过；③**盘中已有快照但本次盘后运行→自动刷新为收盘数据（覆盖重采目标源）**。直接回答「盘后采集发现盘中已采过」的场景：当前会**错误跳过**保留不完整快照，修复后改为**覆盖刷新为收盘数据**。`meta.json` 新增 `run_datetime`/`market_phase` 记录。`--overwrite` 仍强制重采。
- **collide.py 排除项收敛**：`EXCLUDE_DIRS` 由 `{20260814,20260815}` 收敛为 `{20260814}`（仅留盘中 10:49 那次快照，周末目录已随清理删除）。
- 治理：含 field_dict/registry/verify 无关改动（仅清历史数据目录 + 脚本逻辑），G1/G3/P1 闸门全过；PYTHON=py 提交，未推送。

- **字段治理（sanctioned 管线晋级）**：`docs/field_dict.md` §12.1 腾讯 88 字段表中，一段 PE 口径二次重裁定的 blockquote 误插在 `[53]` 与 `[54]` 表行之间，打断了 markdown 表格，导致 `[54]–[88]` 整段（含 `[63]/[67]/[68]/[69]/[70]` 五个已 ✅ 字段）从未被 `extract_registry` 解析。现将该 blockquote 移至表尾（`[87]` 行之后、`---` 分隔之前），使全表连续可解析；重跑 `extract_registry → gen_field_dict → parity` 三闸门全过，5 条正式入 `field_registry.json` 为 `verified`，`collide.py` 不再将其当 `unverified` 反复重对撞。
- **采集数据日命名铁律（根因修复 #449）**：`scripts/capture_field_probe.py` 原以「运行日」(`datetime.now()`) 命名采集目录，周末/法定节假日运行时目录名是假日、但数据实为上一交易日收盘，造成「目录名=假日 / 数据=上一交易日」的错位。`--date` 默认值改为 `_last_trading_day_str()`（基于 `stock_common.stock_calendar.get_last_trading_day()`，自动跳过周末+法定节假日），使目录名恒为「实际数据日」。`meta.json` 新增 `data_date`(数据日)/`run_date`(运行日) 双记录。
- **幂等/覆盖（#449）**：新增 `--overwrite` 开关——默认对「已完整采集的数据日」幂等跳过（避免假日重复采集的重复网络负载与同名覆盖）；`--overwrite` 仅清空本次目标源的 raw 与 meta 记录后重采，保留其他源采集物。增量 `--only` 补采不触发跳过。
- **collide.py 数据日键加固（#450）**：`load_date` 现优先采用 `meta.json` 的 `data_date`（采集时落盘的权威数据日）作非 ZHB 源碰撞键，缺省回落 `date_dir`（现已=数据日），使即便旧版「运行日命名」目录也能对齐到真实数据日；ZHB 仍单独用 `zhb_date`（P0-① 修复持续有效）。
- 治理：含 field_dict/registry/verify 改动，G1/G3/P1 闸门全过；本地提交未推送。

## [V17.4.19] 2026-09-24 — 修复 collide.py ZHB 日期键错位 + 剔除异常采集日

- **P0-① 修复**：`collide.py` 原以「采集目录名」作所有源的碰撞日期键，但 ZHB 包内真实数据日 `zhb_date` 恒为目录名的上一交易日（实测跨周末跳过），导致 ZHB 与任何外源恒差 1 个交易日、日频字段对撞系统性失效。现对 `src=="zhb"` 改用 `doc.zhb_date` 作键（`load_date` 内 `_date_key`）。
- **P0-② 修复**：剔除异常采集日 `20260814`（盘中快照，10:49:53 采集，其余日均为收盘后）→ 当日 change_pct 在 19/20 股同时失配，属采集时点缺陷非字段问题；并同列 `20260815`（周六、12:55 采集）入 `EXCLUDE_DIRS`。
- 修复后跑 sanctioned 四铁律对撞，5 个腾讯高位下标候选全部升 L1（命中率 0.949–1.000、22 独立日）：`[63]=5日涨跌幅`、`[67]=52周最高价`、`[68]=52周最低价`、`[69]=10日涨跌幅`、`[70]=20日涨跌幅`（ZHB 语料中 change_20d≡change_30d 退化，锚点不冲突）。
- 治理：纯代码修复，不含 field_dict/registry/verify，pre-commit 闸门自动跳过；本地提交未推送。

## [V17.4.18] 2026-09-24 — 文档漂移修复（9 处，命中 A7「文档代码同真」公理）+ 记忆体系收敛

- **README.md**：① 目录树 VERSION `17.3.1`→`17.4.17`；② `CanonicalStockData` 字段数 `86`→`113`（经代码核验 `sc_schema.CanonicalStockData` 实测 113 字段，原 86 为 `FIELD_SPECS` 子集误标）；③ 测试体系描述由过时的「21 文件/370 函数/398 项/353 passed」更新为「33 文件/545 函数（参数化展开约 561 项）」；④ `tdx_client.py` 标注由「mootdx/easy_tdx 统一层」更正为「eltdx/easy_tdx 统一层（运行时主源 eltdx；mootdx 已于 V17.3.4 退役）」；⑤ 目录职责表移除对不存在的 `reports/README.md`/`snapshots/README.md` 的断链引用。
- **core/README.md**：`tdx_client.py` 同④更正。
- **scripts/README.md**：版本 `V17.3`→`V17.4.17`；移除已废弃的 `.bat` 推荐小节（与文内「`.bat` 已不再提供」自相矛盾），统一为 `.ps1`。
- **docs/roadmap.md**：① R5「sc_datasource 拆包」状态由「未做」更正为「✅ 已完成（V17.1.0 拆包完成，零回归）」；② ADR「字段破解阶段收官(2026-08-15)」补「更新」注记：V17.4.x 已重启字段破解（吸收上游 + 治理大轮），「收官」结论不再适用。
- **docs/ARCHITECTURE_THEORY.md**：项目记忆引用由 `.workbuddy-ai/memory/MEMORY.md` 改为 `.workbuddy/memory/MEMORY.md`（与记忆体系收敛一致）。
- **tests/README.md**：测试文件数 `32`→`33`（不含 conftest）。
- **记忆体系收敛**：废弃 `.workbuddy-ai/memory/`（停在 V17.1.0 的陈旧记忆 + field-cracking 旧 skill），已删除整个 `.workbuddy-ai/` 目录，后续统一采用 `.workbuddy/memory/`。
- 治理：纯文档修订，不含 field_dict/registry/verify，不触发 G1/G3/P1 闸门；本地 commit、未推送。

## [V17.4.17] 2026-09-23 — 五大报告脚本数据质量修复：互动易跨公司错连 + eltdx 缺章占位 + val 极端值护栏

- **互动易跨公司错连根因修复（#440/#441）**：`cninfo_irm` 键盘查询为模糊搜索，原取 `d1[0].secid` 在沪市曾错连他司（如 601360 误连合金投资等内容）；新增按 `stockCode`/`code` 精确匹配，无匹配则空返回。新增 `get_irm_qa` 统一路由：沪市(60/68/900)改走 `sse_e_interaction`（上证 e 互动，自带强校验）、深市/北交所走 `cninfo_irm`；`get_sht/lng/med_report.py` 三处调用点由 `cninfo_irm` 改为 `get_irm_qa`，从调用层根绝跨公司错连。
- **eltdx 缺章显式占位（#442）**：连板天梯/封单强度为 eltdx 专属 helper API（easy-tdx/mootdx 无等价接口，且前者在 2026 主站已结构性失活），源不可用时原为静默缺章；现 `get_mak_report.py`（B++ 连板天梯）、`get_sht_report.py`（二·附 连板梯队）显式渲染 `⚠️ 数据源不可用…无等价后备通道…本节暂缺`，并修正数据来源标注为中性表述。
- **资金流失效标注（#443）**：`get_mak_report.py` F 段全市场行业主力净流入均为 0 时，原仍渲染含 0 表格误以为「无资金驱动」；新增 `_has_flow` 判定，失效时渲染 `⚠️ 资金流验证失效…本节无法判断真金白银 vs 虚涨，表格暂缺`。
- **涨跌停多源互校标签（#444）**：`get_mak_report.py` 涨停/跌停/封板率行补 `ℹ️ 上述为涨停池口径，与【B++. 连板天梯(eltdx)】/【开盘啦情绪】独立源交叉验证，多源并存时以本节为全市场基准` 标注（A 段连板高度已含三源互校说明）。
- **val 三处极端值护栏（#445）**：`get_val_report.py` §08 日历效应/成分股空名（`or leader_code` / `or c`），§09 逆向白马高 PE 误判（`pe_ttm <= 0 or > pe_ceiling` 跳过，避免 121–172x 标「错杀/低估」），§21 盈利预期近零基数（`abs(eps_a) < 0.05` 跳过，避免 0.01→2.25 EPS 算成 22400% 增速）。
- **历史报告数据质量中和（#446）**：601360 三份历史报告（lng/med/sht）原互动易小节因路由错误显示他司内容，已替换为 `⚠️ 数据质量告警` 占位（不臆造历史问答）；reports/ 为生成物已 gitignore，不入库。
- 治理：本次改动不含 field_dict.md/field_registry.json/docs/verify，不触发 G1/G3/P1 闸门（pre-commit 自动跳过）；全程本地 commit、未推送。

## [V17.4.16] 2026-09-23 — zhb unknown_26 再研判：概念计数证伪（护栏 R10）+ 主板专属指数/名单计数假设

- **`stat.unknown_26` 再研判（板块分层实证）**：tdxstat Col[26] 为有界分类码(0–62, 42类, 中位1)。全市场 8058 股解析/5576 非空，按板块 unknown_26 均值 **中小板6.14 > 深主板5.72 > 沪主板4.95**，而 **创业板0.88 / 科创板0.86（中位0）**。
- **概念成分计数假设被证伪**：科创板概念最密集却 unknown_26≈0，故"概念计数"不成立（规模代理 corr=−0.17 非单调、与股息率−0.37/年初至今+0.39 无单一驱动）。
- **护栏 R10**（`scripts/collision_rules.py` `REFUTED_CONCLUSIONS`）：固化"unknown_26=概念板块成分计数"为已证伪结论（`settled=[]` 不锁字段）。
- **最一致假设修正为 主板专属 指数/名单 成分计数**（沪深300/中证100/上证50·180/深证成指·100/红利等，天然排除双创）；前轮 csiblock 仅覆盖中证指数家族、未含上证/深证家族，指数假设从未被充分检验。解锁所需数据由"概念板块成员表"修正为"主板指数成分股名单"。unknown_26 维持 ⚠️ 候选。
- 治理：field_dict.md 仅改候选注释与 🆕 注记（字段名/状态不变）→ extract_registry 重写 registry(1 行随注释更新)、gen_field_dict --check 幂等一致 ✅；提交触发 G1/G3/P1 闸门；全程本地 commit、未推送。

## [V17.4.15] 2026-09-23 — zhb unknown_2 量比−1 假设证伪（护栏 R9）+ unknown_26 定案阻塞记录

- **`stat.unknown_2`：证伪「量比−1」候选**：取 `cache/kline` 全市场日K线(20260922) volume 计算 `量比=vtoday/mean(v_prev5)`，与 `tdxstat.Col[2]` 同码比对 **1000 股**，corr(unknown_2, 量比)=**−0.08**（几乎零相关）、回归残差中位 0.70 → 量比−1 假设证伪；unknown_2 真义仍待定，维持 ⚠️ 候选。
- **护栏 R9**（`scripts/collision_rules.py` `REFUTED_CONCLUSIONS`）：固化"unknown_2=量比−1"为已证伪结论（documentary，`settled=[]` 不锁字段），防止后续自动对撞再次提案。
- **`stat.unknown_26` 定案阻塞记录**：候选义=概念/指数成分计数；实证阻塞——zhb 缓存无 block_gn.dat、em_industry 缓存为空、tdxstat2 无解释列(最大相关0.22)、csiblock/jjblock/hkblock/mgblock 指数/基金/港股/美股块与 unknown_26 相关≈0、东财/腾讯板块 API 本沙箱不可达；待用户提供文本化板块成员表后闭环。
- 治理：field_dict.md 仅改候选注释（字段名/状态不变）→ extract_registry 重写 registry(2 行随注释更新)、gen_field_dict --check 幂等一致 ✅；提交触发 G1/G3/P1 闸门；全程本地 commit、未推送。

## [V17.4.14] 2026-09-23 — 补全 V17.4.13 闭合：提交遗漏的 zhb_client.py docstring + 再生 collision_state.json

- **实际提交 V17.4.13 时遗漏的 `zhb_client.py` 改动**：V17.4.13 的 CHANGELOG 已声明"同步更新 `zhb_client.py` 中 `zt_type_code` 字段 docstring 与新语义一致"，但该文件当时未纳入提交（4e8f9da 仅含 CHANGELOG/VERSION/field_dict.md/field_registry.json）。本次补齐 `[23] zt_type_code` docstring 修订（2026-08-14 临时解读 → 2026-09-22 全市场 26 码定案），使代码侧注释与已提交的字典 `stat.zt_type_code` ✅ 语义完全一致。
- **再生并提交 `docs/field_verification/collision_state.json`**：该文件为 `collide.py` 增量对撞状态；V17.4.13 之后的 20260923 采集轮次将其窗口刷新为 3 日（n_days 6→3、n_pairs 120→60、last_seen 20260920→20260923），仍保留 zhb.full↔zhb.stat 的 `unknown_2`/`unknown_26` 内部配对；本次一并入库使引擎状态与最新探针一致。
- 治理：本次改动不含 field_dict.md/field_registry.json/docs/verify，不触发 G1 闸门；全程本地 commit、未推送。

## [V17.4.13] 2026-09-23 — zhb 残留未知位研判：zt_type_code 全量定案 + unknown_2/unknown_26 候选

- **`stat.zt_type_code` 语义升级为 ✅**：由"涨停类型码"修订为"行情状态/涨跌强度分档码"，并补全 **7938 股全市场经验映射表**（26 码：高位 20/31/70/95→大涨涨停、低位 21/51/61/71/2/6→偏空大跌、码0=中性基准占53%）。数值闭环来源 `cache/zhb/zhb_20260922.zip` 全市场 `tdxstat.cfg`。
- **`stat.unknown_2` 降级为 ⚠️ 候选**：连续浮点(7668 股·5119 unique)，与全市场各列零/弱相关(R²=0.50, max\|r\|=0.365)系独立指标；候选义=量比−1 或 动量/回撤复合因子，因探针源日期错位(zhb=20260922 vs tencent=20260923)无法同日闭环验证，待同日量比源佐证后方可晋级 L1。
- **`stat.unknown_26` 降级为 ⚠️ 候选**：整数计数(0~62·42值·频次单调递减)，跨3周同值率 80.6%(近似恒定)；按上市板均值 深主板5.99/沪主板4.95/创业板0.91/科创板0.86/北交所0.39，主板大盘股显著高于双创，指向计数型属性(概念板块数/指数成分数/机构覆盖数)；板块 .dat 二进制格式且概念板块文件不在 zhb 缓存，未直接闭环，列为 ⚠️ 候选。
- 同步更新 `zhb_client.py` 中 `zt_type_code` 字段 docstring 与新语义一致。
- 治理：经 sanctioned 管线(extract_registry→gen_field_dict) + G1/G3/P1 闸门全 PASS；本地提交、未推送。


## [V17.4.12] 2026-09-23 — 字段治理：订正 field_dict.md f190 语义（AH上市标识→每股未分配利润）+ 同步 §零·B 至 registry

- **订正 f190 字典行自相矛盾（任务 #433）**：`field_dict.md` line 1946 原标 `f190 | ✅ | AH上市标识`，但 line 1948 已明确 f192 = A+H 双上市标识（20 样本实证）；且全文 line 1531（`f190↔ulist:f48` 338/338）/3038/3480/3495 与对撞引擎（push2.f190↔ulist239.f48 100%、61 样本）一致表明 f190 = 每股未分配利润（元/股）。line 1946 为笔误（与 f192 语义重复且违背其余全文），订正为 `每股未分配利润（元/股）`。
- **§零·B 同步至 registry**：运行 sanctioned 管线（extract_registry → gen_field_dict → G1/G3/P1 闸门），§零·B 投影由 registry 幂等重写，ZHB 单源字段计数 80→84（registry 较旧 §零·B 多 4 个 ZHB 字段的既有漂移补齐，非本次引入）。
- **治理铁律遵守**：G1 registry 双重 parity（原生 token + §零·B 投影）PASS、G3 gen_field_dict 幂等 PASS、P1 归档契约预检 PASS；全程本地 commit、未推送。

## [V17.4.11] 2026-09-23 — 修复采集脚本两处 import 回归（zhb/push2 整源失败）

- **Bug A `collect_push2`（line ~666）**：`from stock_common import _em_is_banned` → `_em_is_banned` 实际定义在 `stock_common.sc_network`，未由包 `__init__` 重导出，导致整源 `ImportError`、未生成 `raw_push2.json`。修复：`from stock_common.sc_network import _em_is_banned`（与 `check_em_health.py:33` 一致）。
- **Bug B `collect_zhb` → `_resolve_zhb_name`**：`get_stock_name_from_zhb`/`_lookup_name_persist` 仅在该函数内局部 import，模块级 `_resolve_zhb_name` 调用时 `NameError`，整源失败、未生成 `raw_zhb.json`。修复：提至模块级 import（line ~109）。
- **验证**：`py_compile` + 模块加载冒烟通过；补采 `--only zhb,push2` 确认 `raw_zhb.json`(71KB, OK)、`raw_push2.json` 已生成（19/20 因本日东财 push2 家族封禁 `request failed`，属网络非代码，由 ulist239 覆盖）。
- **范围**：纯 import 作用域修复，未触碰 field_dict/registry/verify，不触发 G1 闸门。

## [V17.4.10] 2026-09-23 — 第三轮核验订正：reportapi 非缺失、yfbt/ylbc 端点定位

- **订正第三轮(commit 71e179e, V17.4.9) §5 误判**：原称"reportapi 本仓 raw 完全缺失"系漏检。`docs/field_verification/20260812~20260921` **连续 31 天** `raw_reports.json` 早含 `sRatingCode`/`ratingChange`/`indvAimPrice`/`emRatingCode`/`sRatingName`。跨 31 天重算：`ratingChange` 分布 `{3:8275, 2:1014, 1:56, 0:54, '':799}` 与"3维持/2首覆/1调低/0调高"吻合 → 已 ✅ L1；`indvAimPriceT/L` 非空目标价数值正常 → 已 ✅ L1；`sRatingCode` 同码多 `sRatingName`（如 `0201`↔买入2486/推荐470/强烈推荐56/买入(Buy)505/谨慎增持78；`0101`↔买入/增持/强烈推荐/推荐）证其为**机构私有评级代码、非跨机构通用语义** → 维持 ⚠️，理由由"缺失"订正为"非通用语义、须配合 sRatingName 解读"。
- **yfbt/ylbc 端点定位**：源 = `stock_common/sc_datasource/_pools.py` `get_yesterday_limit_pool()` → `push2ex.eastmoney.com/getYesterdayZTPool`；响应 `data.pool[]` 带 `yfbt`(昨封板时间)/`ylbc`(昨连板数)，与同表 `fbt/lbc` 为昨日对应项。本仓无含此二字段的 raw 快照（Round-3 仅看了当日涨停池子端点，未见 `getYesterdayZTPool`）。
- **实时补采受阻**：2026-09-23 实测端点可达(HTTP 200, `data.tc` 非空 78/47/54)，但 `data.pool` 对全部 2026 日期恒空(`qdate` 恒回显 20260923) → 本环境对 2026 时间线不返回池数据，缺 raw 数值闭环。
- **处置**：reportapi 三项**无需新采集**（多数已 ✅）；yfbt/ylbc 含义已由代码级 L0 确证，`field_dict.md` §12.8.1 由"待破解 ⏸️"订正为"⚠️ 含义已确认(代码级L0)，缺 raw 数值闭环升 L1"；二者均不写护栏、不晋级 L1。
- **治理铁律遵守**：全程基于本仓既有 raw 数值重算，未改动业务代码与字典生产管线；本地提交、未推送。

## [V17.4.9] 2026-09-23 — 第三方复核反驳·第三轮独立对撞：撤防 R6、重构 R7/R8、PE 三梯队闭环升级

- **第三轮独立核验（对撞 Gemini 反驳）**：基于 `docs/field_verification/20260920/raw_ulist239.json`（20 股）数值重算，产出 `20260923_round3_reverify.md`。核心发现：000568/600309 的 `f48`/`f58`/`f113` 存在**源端报告期刷新异步**，上一轮(Round-2) R6/R7 将瞬时异步偏差误读为语义口径差异，本轮订正。
- **撤防 R6**：`f47/f38=f48` 在 18/20 股精确闭合（000568 `f47/f38=25.3279`=公司 2026 中报每股未分配利润官方值），证 `f47`=**未分配利润总额**而非留存收益；`f48`=每股未分配利润（含异步告警）。`field_dict.md` §12.3 f47 由"留存收益"订正为"未分配利润总额"。
- **重构 R7**：`f113`=每股净资产(BPS) 无疑义；但 `f113×f38` 在 18/20 股精确=f58(归母)，高少数股东股(000568)≈f135(合并)——母/合口径随快照刷新漂移，既非"恒=f58"也非"恒=f135"。R7 改写为 `R7_f113xb38_not_rigid_identity` 护栏（保留"禁刚性恒等式"，删除错误方向断言）。
- **R8 保留核心+补分母**：`f129≠f45/f132`(TTM, 周期错配) 全样本证实；归位为同报告期销售净利率 ≈`f45/f40`（20 股误差<2.5pp）。`f129` 由 ⚠️ 升 ✅。
- **PE 三梯队闭环升级**：`f9`=动态PE、`f114`=静态PE(年报)、`f115`=TTM PE 经 `price÷fX` 20 股复算闭合（茅台 71.2/65.85/65.14），与基础表既有 L1 语义一致。ulist §12.3 `f9` 标签订正、`f114/f115` 由 ⚠️ 升 ✅；footer 144→147、待破解 30→27。
- **push2ex(yfbt/ylbc) / reportapi(sRatingCode 等)**：本仓 raw 缺失对应端点数据，无法本地闭环，**维持候选不晋级**（疑似不同子端点/命名，待另行采集）。
- **治理铁律遵守**：`collision_rules.py --emit` 重生成 `COLLISION_RULES.md`；`extract_registry.py` 重生成 `field_registry.json`；G1/G3/P1 闸门全过；全程本地 commit、未推送。

## [V17.4.8] 2026-09-23 — 字段治理：ZHB tipinfo 4 字段 L1 定案 + ulist 21 字段晋升/订正 + 对撞护栏 R5–R8

- **B 项·ZHB tipinfo.dat 4 字段 L1 定案（主数据闭环）**：基于 `docs/field_verification/20260923_tipinfo_verify.md`（37 期 ZHB `tipinfo.dat` 逐字节核验），Col[7]→重大事项停牌起始日、Col[11]→最新业绩预告发布日（跨期跳变实证 002475 20260429→20260825 / 300497 20260618→20260918 / 000100 H1 后转空，推翻旧"ipo_date/配股比例"误标）、Col[12]→业绩预告类型代码（完整枚举 1/2/3/4/6/8/9/10/13，比外部报告子集更宽）、Col[21]→股权激励预案/草案公告日（000045=20260819 / 688130=20240920 / 000338=20231025 逐字吻合）。4 token 同步入驻 §3.1 标准契约表（✅ L1），§3 填充率摘要表与核验注记口径订正。
- **B 项·ulist239 21 字段晋升/订正（本轮 ✅ 计数 123→144）**：f103=所属概念题材标签串、f124=行情更新时间戳(Unix秒,推翻旧"股东户数"误标)、f130=市销率PS_TTM、f131=市现率PCF_TTM、f132=营业总收入(TTM,元)、f135=所有者权益合计(合并,元)(R4 口径)、f139=板块分类枚举、f231/f233=有转债标志、f185-189=H股行情块(现价/涨跌幅/溢价率/比价)、f195-197/f199/f202=B股行情块(现价/涨跌幅/行情值/存在标志)、f48=每股未分配利润、f58=归属于母公司所有者权益合计(元)(R4 母公司口径)。f47 由"未分配利润"订正为"留存收益(盈余公积+未分配利润)"（f48≠f47/f38 因 f47 含盈余公积）。
- **C 项·对撞护栏 R5–R8 固化（collision_rules.py + COLLISION_RULES.md `--emit` 重生成）**：R5 tipinfo Col[11]≠ipo/自由流通股本（跨期跳变实证，tdxstat Col[11]=free_ltgb 为另一文件）；R6 f48≠f47/f38（000568 误差21.1%/600309 2.51%，f47=留存收益非未分配利润）；R7 f58≠f113×f38（000568 f113×f38≈f135 合并权益而非 f58 归母，600309 误差16.57%）；R8 f129≠f45/f132（f45=单报告期净利/f132=TTM营收 周期错配误差35~77%，正确净利率须 TTM 派生）。
- **治理铁律遵守**：外部 LLM(Gemini)结论一律降格为候选，经本项目主数据独立闭环（37 期 ZHB 离线快照逐字节比对 + round-2 数值重算）后方可晋级 L1；f45/f46/f49/f127 因缺年报/中报交叉印证**维持 ⚠️ 候选**（round-2 治理决议）；field_registry.json 经 `extract_registry.py` 重生成、G1/G3/P1 闸门全过；全程本地 commit、未推送。

## [V17.4.7] 2026-09-23 — 吸收上游 3.10.0 两个新取数能力（腾讯逐笔 / 新浪期货日K）

- **采纳上游 v3.10.0 新增能力 A：腾讯逐笔成交 `tencent_ticks(code)`（§1.4, 替代失效 mootdx transaction）**：新增 `stock_common/sc_datasource/_ticks.py`。沪深个股/ETF 当日分笔（约 3 秒一笔，非 Level-2），覆盖连续竞价+盘后定价；北交所/指数/代码不存在/当日无成交抛 `ValueError`，源格式变/收盘后连续竞价段成交额与行情快照核对不符（差>0.1%）抛 `RuntimeError`，盘后定价段缺号记入 `frame.attrs["missing_seq"]`。
- **采纳上游 v3.10.0 新增能力 B：新浪期货日K `futures_kline_sina(symbol, start, end)`（§13.7, 补大商所历史日线）**：新增 `stock_common/sc_datasource/_futures_sina.py`。覆盖全部六家交易所（含大商所），代码不存在/太老/区间内无K 抛 `ValueError`，结算价新浪给 0 统一为 `None`。
- **上游 `_v39_*` helper 语义忠实复刻**：抽 `stock_common/sc_datasource/_v39_compat.py` 集中实现上游 `_v39_num/_req_num/_fut_price/_parse_date/_src_date/_rows/_frame/_contract` 契约（必填数值缺/非有限→`RuntimeError`，格式变→`RuntimeError`，与 `sc_utils._safe_float` 的"缺值返回 default"刻意区分），两新模块显式 import，避免各模块重复定义与包级命名空间冲突（`__all__` 仅导出公开 API）。
- **错误契约对齐上游**: 参数错/确实无数据→`ValueError`, 源格式变→`RuntimeError`, 不改变已有字段字典(取数层新增, 不涉 f-code 治理)。
- **测试**: 新增 `tests/test_v310_sources.py`（21 项, 全部离线可跑）：纯解析函数（快照/逐笔页/期货JSONP）、错误契约（`ValueError`/`RuntimeError` 边界）、端到端（mock `_quick_request` 复现网络返回 + 收盘后完整性核对分支）、联网冒烟（`@pytest.mark.real_network` 受控, 需 `REAL_NETWORK=1`）。
- **治理铁律遵守**: 上游 v3.10.0 的 Layer-1 重编号/INE 修正/doc 修正不涉本仓（自有 § 体系/未继承区）；唯一重叠 `lpr_history()` 已由 V17.4.4 覆盖；本次仅取数层新增, 经对撞校正, 未晋升字段字典; 全程本地提交、未推送。

## [V17.4.6] 2026-09-23 — 字段治理：f148 重对撞定案 + ZHB 跌停日 L1 + 注册表旧误标清理

- **① f148 主数据重对撞（解决硬冲突）**：Gemini 主张 ulist239 `f148`=市场/板块二进制掩码，与本项目旧 L1(=10日超大单净占比%)冲突。独立重对撞 `docs/field_verification/20260911/raw_ulist239.json` 全样本：**577/1089/1/65 = 1+64+512/1024 位分解**，与交易所前缀/两融标志系统吻合 → **Gemini 正确，ulist f148=复合二进制掩码（L1 定案）**。旧"10日超大单净占比%"实为 **ulist f177**（百分比字段，与 push2 f177 对齐），对齐表 `f177|ulist:f148` 系**转置错误**，已修为 `ulist:f177`。注意 push2 `stock/get` 的 `f148`=散单(第五档)卖出额(元)（§12.3.4）仍有效——此为**同号异义**陷阱（`docs/field_dict.md` 已加注）。
- **② ZHB tipinfo.dat Col[10] 实列核验（涨停/跌停日）**：解析 `cache/zhb/zhb_20260921.zip` 实测 6 股——茅台 20181029 / 平安·平安保险·农行 20150119 / 万科 20241009 / 五粮液 20200716 全部命中真实历史跌停事件日，宁德(创业板时代从未 20% 跌停)=空；与 Gemini 候选值一致，由**项目自有数据独立闭环**。`Col[5]`(=zt_date_recent 涨停日) 与项目既有结论吻合。`core/zhb_client.py._parse_tipinfo` 已接入 `dt_date_recent=parts[10]`（编译通过，6/6 抽取验证）；`field_dict.md` §3 col[10] 由"待官方文档"**升级为 L1 定案**。
- **③ 注册表旧误标同步 field_dict.md 既有 L1（治理缺口清理）**：`field_registry.json` 中 `f130/f131/f132/f133/f124` 的旧误标（毛利率/总资产/股东户数?/空）同步为既有 L1——`f132=revenue_ttm`、`f130=ps_ttm`、`f131=pcf_ttm`、`f133=股息率`、`f124=收盘Unix时间戳(秒)`，status 置 verified；`f148/f177` 含义与状态同步订正。经 `gen_field_dict.py` 回灌 + `registry_parity.py` 双重 parity 通过。
- **治理铁律遵守**：外部 LLM(Gemini)分析=非授权候选，结论经本项目主数据独立闭环（非仅文本采信）；注册表为单一真相源、经 sanctioned 管线回灌；全程本地提交、未推送。

## [V17.4.5] 2026-09-22 — 去除 sht 报告盘后恒 N/A 的「均价偏离 / 盘口委差」接入块

- **背景**：用户**只在盘后扫描**；`get_sht_report.py` 渲染的「均价偏离」(`cdata.avg_price`/腾讯[85]) 与「盘口委差」(`cdata.bid_ask_net`/腾讯[86]) 均为**盘中 L1 字段，盘后快照恒为 0/None**，故盘后产物永远落 `N/A`——接入无意义。
- **动作**：整体删除 `get_sht_report.py` 第 389–423 行（均价偏离、盘口委差两块渲染 + 其 DEBT-007/DEBT-014 注释文档）。语法校验通过（`py_compile` exit 0），字段残留计数 0。
- **范围**：仅移除 sht 报告渲染层；`avg_price` 在 `get_lng_report.py:1281` 另有独立消费（不同 dict、不依赖盘后快照），不受影响，未改动。
- **来源**：对应 `reports/audit_findings_20260922.md` 第 3 项（系统性缺口），用户授权"可以去除"。
- **未推送**：按治理铁律本地 commit，不推送远端。

## [V17.4.4] 2026-09-22 — 修复 LPR「最新」取值 bug（取数分页错取历史旧值）+ None 渲染为 N/A

- **LPR 最新值取数 bug 根因修复（真实 bug，非源过期）**：`stock_common/sc_datasource/_macro.py` 的 `lpr_history()` 调 `eastmoney_datacenter` 时 `sort_types="1"`（升序）且该函数默认只取第 1 页（单页、不自动翻页），致首屏返回最旧 200 行（1991 年起）；`get_macro_context()` 再取 `_lpr[-1]` = 第 200 行 ≈ 早期旧贷款基准利率 **5.76%**，且旧行 `LPR5Y` 为 null → 渲染成字面 `None`。修复：`lpr_history()` 改 `sort_types="-1"`（降序，首屏即最新 200 行）；`get_macro_context()` 取数改为 `max(_lpr, key=lambda r: r.get("date",""))`（取 TRADE_DATE 最大者=最新，防御性）。运行时验证返回 `lpr_1y=3.0 / lpr_5y=3.5`（与央行/邮储官网 2026-09-20 公布 1年 3.00% / 5年 3.50% 一致）。
- **LPR 缺失值渲染修复**：`get_med_report.py:244` / `get_lng_report.py:177` 的 `LPR(最新)` 行，`lpr_1y/lpr_5y` 为 `None` 时由字面字符串 `None` 改为 `N/A`（与项目"缺失诚实标注"约定对齐）。
- **审计回溯**：本报告系对 `reports/audit_findings_20260922.md` 第 2 项严重问题的根因修复；同审计第 1 项（中塑股份 301686 +683.3%）经复核为误报（该股 2026-09-22 当日创业板上市、首日无涨跌幅限制，+683.29% 为真实首板涨幅），不修复；第 3 项（sht 均价偏离/盘口委差 N/A）判定为非 bug 的设计性降级，不改代码。
- **未推送**：按治理铁律本地 commit，不推送远端。

## [V17.4.3] 2026-09-22 — 补回 A1 闸门脚本 + 宏观字段 _VERIFIED 溯源 + 11 项测试失败针对性修正

- **建议① 补回 A1 数据访问收口闸门** `scripts/verify_data_access.py`（AGENTS.md §8.4 要求、此前缺失）：
  用 `tokenize` 剥离注释/字符串，扫描生产脚本(main.py / get_*_report.py / core/*.py 除 tdx_client.py)是否直连原始客户端(`_get_tdx_client` / `sc_network.em_get` / `sc_fuyao._fuyao_raw` / 裸 `requests`·`httpx`·`aiohttp`·`urllib`)。
  实测真实仓库 **0 硬失败 0 警告**（exit 0）；`core/gd_uploader.py`(Google Drive 上传器, urllib 仅用于探测本地代理可达 OAuth)已按「非行情取数」语义文件级豁免, 但其 RAW_FUNC 类违规仍会被捕获(豁免不削弱检查)。
- **建议② 宏观 LPR/回购定盘补 _VERIFIED 溯源注记** `_macro.py`：新增 `_VERIFIED_FIELD_SOURCES`，将 `lpr_1y/lpr_5y`(央行LPR/东财RPTA_WEB_RATE) 与 `FR001/007/014`、`FDR001/007/014`(中国货币网官方CSV) 显式订正为 VERIFIED(官方公布利率, 非 a-stock f-code 破解字段, 无需经本仓 collide 终检)，满足「每个展示数值字段须有溯源」治理要求。
- **11 项测试失败针对性修正(不再仅归为历史遗留, 均定位真根因并修复)**:
  - `test_data_network::TestEmBanCooldown`(2)：V17.3.17 给 `_em_is_banned` 加了**跨进程封禁文件**检查, 测试只清内存没清它 → 磁盘残留让「应未封禁」误判为已封禁。测试 setUp 用 `unittest.mock` 隔离 `_load_banned_file`/`_save_banned_file`, 4 例全过。
  - `test_data_prefetch`(8)：V17.3.12 给 `prefetch_quote_batch` 加了 **SQLite L2 跨进程缓存**读写, 先于 `_quick_request` 注入、绕过 mock 并污染用例。测试 fixture 隔离 `read_quote_batch_l2`(→{}) / `persist_quote_batch_l2`(→noop), 9 例全过(`_ULIST_BATCH_FIELDS` 实测与断言完全一致)。
  - `test_reports_pipeline::test_no_prefetch_hooks`(1)：V17.3.10 给 Lng 注册了 `prefetch_fn`(与 med/sht 对齐), 该「无 prefetch」断言是过期断言。改为断言 Lng 注册同步 `prefetch_fn` 且不注册 `prefetch_async_fn`, 1 例全过。

## [V17.4.2] 2026-09-22 — 闭环上轮 3 项「遗留」：深交所ETF接口修复 + IPO募资额单位对撞订正 + ST名单 baostock 兜底接入
- **① 深交所 ETF 接口恢复(修复真问题, 非"未知")**: 原 `_etf.py` 用 `fund.szse.cn`(本环境被封, 长期显"深市 ETF 数据暂不可用")。仓内 `_eastmoney.py:1195` 早已用 `www.szse.cn` 同名端点(龙虎榜)且本环境可用 → 切主站 `www.szse.cn/api/report/ShowReport/data` + 兜底回退 `fund.szse.cn`。实测 `www.szse.cn/...CATALOGID=1000_lf&selectJjlb=ETF` → HTTP 200、740 只、快照日 2026-09-22。另加 `pagesize=2000` 一页取全 + `sleep(0.05)`(原 0.3), 消除 37 页循环最坏 555s 挂死; 快照日与请求日不符时以快照日为准(不再抛错)。
- **② IPO 募资额单位对撞订正(修复真 bug, 非"未知")**: 原渲染把 `TOTAL_RAISE_FUNDS` 当"元" `÷1e8` 显示 0.00。对撞确认单位=亿元: `TOTAL_ISSUE_NUM(万股)*ISSUE_PRICE(元)/1e4 == TOTAL_RAISE_FUNDS(亿元)`, 28 点误差 0。修复后直接按亿元展示, 恢复"募资(亿)"列与合计。验证: 未来 21 日 3 只新股申购, 预计募资约 84.5 亿元(粤芯半导体 75.00 / 联亚 9.50 / 莫森泰克 待定)。
- **③ ST 北交所名单 baostock 兜底接入(闭环上游 §6.8, 非"未知")**: 原 `_st_list.py` 注释"baostock 兜底未接入"。上游权威仓库 §6.8 `st_stock_list()` 即东财 + baostock 兜底 → 已接入 `_st_list_baostock()`: 东财主源(沪深风险警示板)不可达时走 baostock(仅沪深, 上游 §6.8 明记 baostock 不支持北交所); 用守护线程 + `join(timeout=20)` 包裹(本沙箱同样封 baostock TCP, 原会挂起 150s → 现 ~11s 优雅抛错)。BJ 始终只能来自东财(上游已知限制, 非 bug)。验证: push2+baostock 双封下 `st_stock_list()` 诚实抛 `RuntimeError: ST名单(沪深)主源与 baostock 兜底均不可用`, 渲染段显"⚠️ ST名单源当前不可达", 不伪装空名单。
- **性能修复(ETF 段 103s→10.2s)**: 原 `_fetch_etf` 对 SZ 也跑 10 天回退×2 主机, 撞 15s 超时×多次爆炸。改为 SZ 不回退历史日、单次尝试 + 25s 守护线程超时 → ETF 段耗时 103s→10.2s; 深市被封时优雅显"深市 ETF 数据暂不可用(待恢复)", 沪市 912 只(20197.8 亿份)正常。
- **核证方式**: 拉取上游权威 SKILL.md(simonlin1212/a-stock-data)校对 §4.7 ETF 深交所当前快照 / §6.8 ST 名单 baostock 兜底 / 行 2183 IPO"单位: 亿元", 确认 3 项均属仓库已明确改进内容; 数值对撞为本项目 field 治理铁律终检(单位已定案, 非候选)。
- **未推送**: 按用户指令本地 commit, 不推送远端。

## [V17.4.1] 2026-09-22 — 吸收层全量接入：申购日历/ETF份额/新浪研报/央视联播/上证e互动/ST名单 + 市场级报表 filter 根因修复
- **市场级报表 filter 根因修复(核心)**: `sc_datasource/_eastmoney.py` 的 `eastmoney_datacenter` 在 `code=""` 且无显式 filter 时自动补 `(SECURITY_CODE="")` 把全市场报表(ipo_calendar/convertible_bonds/lpr_history)过滤成空——此为 V17.4.0 市场级报表恒空根因。修复为 `filter_str if filter_str else (f'(SECURITY_CODE="{code}")' if code else "")`；同步将 `_events.ipo_calendar`/`_convertible.convertible_bonds` 调用点 `filter_str=" "` 改 `""`。复采验证：ipo_calendar 20 / convertible_bonds 500 / lpr_history 166 条全部生效。
- **申购日历接入 val/mak(抽水压力指标, #396)**: 新增 `ipo_calendar_recent()`(按 APPLY_DATE 倒序取未来申购)；`sc_market_signals.render_market_signals_section` 市场级附录新增【G. 近期新股申购日历·资金抽水压力监测】——以申购只数表征抽水压力(募资额字段 TOTAL_RAISE_FUNDS/PREDICT_RAISE_FUNDS 单位待对撞核实, 不展示未核数值)。
- **吸收层 5 新源 + ST 名单(全守卫渲染, #397/#400)**: 新增 `sc_market_signals.py` 渲染器, 6 源独立 try/except(单源失败仅该章节显"暂不可用", 不连累整份报告)。5 新数据采集器接入 `capture_field_probe.py`(`--only` 可单采), 今日采集 5 源 raw 已落盘(受 .gitignore 约束不外发)。
  - 新浪研报(第二源)/ 央视《新闻联播》/ 上证e互动(市场级+个股级) 已验证可用并接入 val/mak/med/lng。
  - ETF 份额: 沪市(SSE)可用; 深市(SZSE fund.szse.cn)当前接口暂不可用 → 显式"深市 ETF 数据暂不可用"而非伪装 0。
  - ST/*ST 名单: 源(东财 push2 clist)今日曾全封禁 → 硬化 `st_stock_list`(源失败抛错交采集器记 `__error__`, 不再伪装空名单); 源恢复后实测 208 只(sh83/sz122/bj3), 章节显式"暂缓接入→自动显示"。
- **对撞终检(#399)**: 今日 `collide.py --date 20260922 --window 3` 跑通(3 日 / 1216 字段 / 120,973 样本), 0 新 L1、8 guardrail 拦截——字段登记稳定, 确认 V17.4.0 的 reportName 候选常量大量错误, 已在 V17.4.1 经上游权威(黄金锚)+ 实采计数校正。
- **治理铁律遵守**: 未对撞字段(募资额单位/ST 北交所细则)仅展示记录条数+数据溯源, 不把未验证数值当权威结论; 所有新增源均带 `_VERIFIED` 标记(取自上游权威仓库 2026-09-22 对撞校正), 待本项目 collide 终检。
- **未推送**: 按用户指令本地 commit, 不推送远端。

## [V17.4.0] 2026-09-22 — 吸收上游 3.9.0：限流收口 + 宏观/事件/可转债层 + tdx 取数级验活
- **限流收口(用户指令①)**: `scripts/capture_field_probe.py` 的 `collect_push2` 显式"全走 push2delay、仅当其被跨进程标记封禁再回退 push2"——`_em_is_banned("push2delay.eastmoney.com")` 命中即跳过镜像域省一次请求走兜底(用户: push2delay 更安全)。push2 与 push2delay 为独立 ban key(V17.3.17 已确认), 回退链路成立。
- **tdx 取数级验活(用户指令③·#52 思路移植)**: `core/eltdx_adapter.py` 的 `create_eltdx_adapter()` 增加**取数级验活**——连通后必须真实拉一根日 K 线非空才算通过; 连通但取数损坏(静默空表)明确返回 None 交上层 tencent/zhb/easy_tdx fallback, 不再静默空表(上游 mootdx #52 根因: TCP 握手通过≠能取数)。验活结果缓存 300s。
- **宏观利率层(§11, 用户指令②)**: 新增 `stock_common/sc_datasource/_macro.py`(中债收益率曲线/LPR/回购定盘/宏观日历 + `get_macro_context()` 聚合); 接入 **med【宏观资金面背景】** 与 **lng【零、宏观利率与政策环境】** 两处章节(全守卫, 有数据才渲染, 空数据给"待对撞验证接入"提示)。
- **事件驱动层(§14)**: 新增 `stock_common/sc_datasource/_events.py`(业绩预告/机构调研/股东增减持/股权质押/新股申购; 回购已在 V17.3.9 独立成章不复刻)。
- **可转债层(§15)**: 新增 `stock_common/sc_datasource/_convertible.py`(`convertible_bonds()` 条款/转股价值/溢价率/状态)。
- **优化同步(§优化, 用户指令③)**: 三新模块统一带 `source`/`source_url`/`fetched_at` 溯源; 结构错抛 `RuntimeError`(非 KeyError); 取值异常优雅降级返回 [](不伪造数据)。reportName 常量集中登记并标注 `verified=False`, 待本项目 collide/field 对撞验证后方可视为权威(治理铁律: 推断走候选、不越级定案)。
- **未变更**: push2 0.4rps 硬上限、源优先级 QUOTE_FETCH_ORDER、缓存四原则、核心 86 字段契约均不动。
- **待办(用户指令③其余层面)**: 研报新浪第二源/ETF份额/华尔街见闻+央视新闻/上证e互动舆情/ST名单baostock退路/通达信官网盘后包/腾讯K线全谱——见分析报告(吸收/跳过/待定结论); 期货大宗用户明确不需要。新层 reportName 常量须对撞验证后入 field_dict。
- **报告接线(用户指令②续·事件驱动/可转债)**: med 新增【七之二、事件驱动与股东动作 (业绩预告/机构调研/股东增减持/股权质押)】+ 可转债可选小节(仅当标的含可转债时渲染); lng 新增【零之二、事件驱动与基本面催化 (业绩预告/机构调研)】+ 可转债可选小节, 并交叉引用【九之二、风险扫描】(增减持/质押已在彼覆盖)。渲染器集中为 `sc_datasource.render_event_driven_section`(公共函数, 经 `__init__` 导出), 全守卫, 仅展示记录条数+数据溯源(治理铁律: reportName 待对撞验证, 不呈现未验证字段数值, 避免把未对撞字段当权威结论)。
- **T393 待评估两项评估结论(用户指令③续)**: ① 通达信官网盘后包(§1.6)——项目已读本机 `vipdoc/*.day` + eltdx 公网主站 TCP + B1 腾讯 ifzq qfkline qfq 时序, 盘后包属已覆盖能力, 新增独立下载器价值有限且脆弱 → **不接入**; ② 腾讯K线全谱(§1.5 日周月+1~60分三端点轮换)——qfq 日/周/月时序已由 B1 覆盖, 分钟K与三端点轮换当前 5 大报告(日/周因子)无用例 → **不接入**(待后续短周期特征需求再评估)。其余"待吸收"层面(研报新浪/ETF份额/华尔街+央视/上证e互动/ST名单baostock)维持用户已同意的"待吸收"结论, 暂不接入。

## [V17.3.17] 2026-09-22 — 修复 push2 封禁态不跨进程共享（真正的遗漏限流一环）
- 根因：原 `_EM_BANNED_UNTIL` 仅模块级内存态；5 大脚本 + 采集脚本以独立进程运行，限流器已跨进程文件锁协调，但**封禁态未共享** → 任一进程检测到 push2 族封禁仅自身停火，其余进程毫不知情继续狂轰 → 持续/反复触发东财 IP 级(20h+)封禁。9/21 全 push2 族 20/20 失败即此模式。
- 修复：新增 `_EM_BANNED_FILE`（与限流锁同目录）持久化封禁态；`_mark_em_banned` 统一收口连接级断连 + 连续 403 两条路径，写共享文件；`_em_is_banned` 先查内存再查文件（5s 进程内缓存），跨进程互相感知停火。
- 附带：scripts/check_em_health.py 裸 `requests.get` 直打 push2 全族（无节流/无封禁感知）改为走 `_quick_request`（分域限流 + 跨进程封禁跳过 + 全局 1.0–1.3s 节奏），已封禁域返回 `SKIP(banned)` 不加重封禁。
- 验证：py_compile OK；跨进程封禁态共享 / 过期自动清除 / 3 次断连触发共享 全 PASS；tests/data/test_data_network.py 10 项无回归。
- 未变更：push2 0.4rps=2.5s 硬上限、源优先级 QUOTE_FETCH_ORDER、缓存四条原则均保持不变。
- 遗留（待用户拍板）：采集脚本 `capture_field_probe.py` 全市场≈5000 只逐股 push2 的**量级**问题（即使 0.4rps，也是 20+ 分钟持续占用主域风控面，与 5 大脚本 push2delay 用量叠加偶发触发总封禁）尚未改动。

## [V17.3.16] 2026-09-22 — 订正裸 V17.4 (2026-09-21) 注释引用 → V17.3.4
- 全量订正：core/source_priority.py:3、core/data_provider.py:81/1216/1850、get_val_report.py:2274 共 5 处裸 `V17.4 (2026-09-21)` 注释引用回订为 `V17.3.4`。
- 溯源定位：该批注释源自未打版本标签的提交 `f0c468a`（"5脚本接入与fallback治理：源优先级单一真相源+市值护栏+概念富集"）；git 确认其为 `6aa4376`(V17.3.4) 的祖先 → 其代码首现于 V17.3.4 并被子嗣版本继承，故映射为 V17.3.4（修正此前记忆笔记误判的 17.3.5~17.3.9 谱系）。
- 排除 `sc_fault_tolerance.py` 的 `Version/17.4 Safari` 浏览器 UA（非版本引用）。

## [V17.3.15] 2026-09-22 — 订正误标的 V17.4.x 版本引用
- 全量订正：将代码注释与提交信息中误标的 V17.4.0~17.4.4 版本引用统一回订为真实谱系 V17.3.10~17.3.14（各提交实际编号）。根因为提交标签擅自越级跳 minor 到 17.4，而项目 VERSION 单一来源自 V17.3.4 起未变。
- 同步订正 get_mak_report.py 异动扫描注释（MAK_SCAN_WORKERS 命名常量随 V17.3.12 引入，非 17.4.2）。

## [V17.3.14] 2026-09-22 — 修复评分快照链路断裂（评分突变背离报告消失根因）
- 根因：sc_report_runner.execute_batch_pipeline 保存分支用 isinstance(snapshot_data, dict) 校验（M6，V17.1.0 引入）；但 sht/med/lng 传入的 _SNAPSHOT_DATA 实为 SnapshotProxy（V15.3.1，非 dict 子类）→ 校验恒 False → save_snapshot 自 V17.1.0 起从未被调用 → snapshots/ 无 snapshot_*.json → analyze_history 读空 → 评分突变背离（≥15 分）报告永久消失。
- 修复：保存分支先对 SnapshotProxy/含 items() 的映射规整为真实 dict 再走结构校验与 save_snapshot；检测逻辑本身完好（构造 2 日快照 Δ=16 正确检出，Δ=10 对照不触发）。
- 影响：sht/med/lng 评分快照恢复落盘；需连续运行 ≥2 个交易日方能重新产出异动报告（历史残留快照已耗尽，无法回溯补算）。

## [V17.3.13] 2026-09-22 — 跨进程共享 TTL 15→60min + mak 复用 val 预热
- _QUOTE_BATCH_CACHE_TTL 15→60min：覆盖整轮 30~40min 运行，避免后段脚本 val 快照过期后退回逐股网络补取；仍为严格硬过期（不在软过期窗口），不读跨日陈旧。
- 复活 V16.0 "val→mak 跨脚本复用"意图：新增 TENCENT_BATCH_CACHE_CATEGORY + persist/read_tencent_batch_l2（原始腾讯批量形状，IN 子句分批 500）；_tencent_batch_fallback 增 use_l2_cache，val 写盘、mak 默认读盘零改动受益。
- 限流（push2 0.4rps 硬上限）/源优先级/网络请求数均未变；仅增 L2 落盘（复用已发生的同批腾讯拉取）。

## [V17.3.12] 2026-09-22 — val 预热跨进程惠及 sht/med/lng + mak K线去重
- #1 mak K线 count 归一去重：_MAK_KLINE_MEMO + _mak_kline_raw(count=60) 进程内 memo，每 code 仅 1 次 baidu_kline_full（原 15/25/30 三处各取 → 1 次）。
- #3 val 预热跨进程：read/persist_quote_batch_l2 对称 L2（15→60min TTL）；prefetch_quote_batch 入口读/出口写 L2；val 预热后落盘（刻意不含 _PD_EXTRA_CACHE 哨兵 0，避免他脚本主力资金段空白）。
- #2 线程池 3→6 实测后保持 3：纯 CPU 负载下 workers=6 反比 3 慢（GIL 限制），CPU+I/O 混合仅快 ~3%（噪声内）；提速主源为 #1 与 #3。

## [V17.3.11] 2026-09-22 — mak 异动扫描剔除重复全市场腾讯批量请求
- 去重 mak 异动扫描中对全市场腾讯批量的重复拉取（双拉→单拉），降低重复网络请求。

## [V17.3.10] 2026-09-22 — 批量行情预取延伸到中线/长线报告
- 批量行情预取能力从短线延伸到中线/长线报告（与短线对齐），缩小三类报告的数据新鲜度差。

> 注：17.3.5–17.3.9 各提交未在本文档登记（历史遗留），本段自 17.3.10 起补记。

## [V17.3.4] 2026-09-22 — 退役 mootdx + 重激活握手补丁修复 TDX 空数据

- **根因（"连接成功却返回空数据"）**：V17.2.15 将 TDX 主源切到 eltdx(Rust) 时，误判"eltdx 握手已含 2026-09 修复 → easy_tdx 补丁不再需要"，于是从 `tdx_client.py`/`zhb_client.py` 移除了 `core._tdx_handshake_patch` 的 import。但 easy_tdx 的真实上游(github.com/yanwei99521/easy-tdx)至今仍发布**静态三握手**，对 2026-09 行情主站"握手有响应、但所有数据请求静默返回空包(0x0320)"。故此前 easy_tdx 兜底路径连接成功却取不到任何 K 线/行情（mootdx 同源同症状）。eltdx 不受影响（Rust 内核自带修复）。
- **修复（重激活动态握手补丁）**：在 `core/tdx_client.py` 与 `core/zhb_client.py` 顶部恢复 `import core._tdx_handshake_patch`（须在任意 `from easy_tdx ... import` 之前）。补丁在 import 时把 `setup.SETUP_COMMANDS` 与已绑定的 `transport.sync`/`transport.async_` 的 `SETUP_COMMANDS` 一并重写为新式单条动态握手（随机 msg_id + 0x000d + payload 0x01），并对齐 eltdx 行为。实证：`import tdx_client` 后 `easy_tdx.transport.sync.SETUP_COMMANDS len=1`、dynamic flag=True；实拉 `get_security_bars('600519', DAY)` 返回 5 行真实 OHLCV（open 1281.0 / close 1272.75 / vol 1,376,172）。
- **退役 mootdx**：删除 `tdx_client.py` 的 `_check_tdx`/`_get_tdx_client` 中 `from mootdx.quotes import Quotes` 备胎分支与 `zhb_client.py` 的 mootdx 下载备胎循环；`main.py` 依赖自检移除 `("mootdx","mootdx")`；`requirements.txt` 删除 `mootdx` 依赖。仅留 eltdx(主) + easy_tdx(兜底) 双引擎。
- **锁定 easy_tdx 上游**：`requirements.txt` 将 `easy-tdx>=1.32.6` 改为锁定真实可维护上游 `github.com/yanwei99521/easy-tdx @ 1.20.8 (commit 41e5637)`（PyPI 同名包已停更/404，非同一库）。已删除本机曾装入的非同源异构建 1.32.6，安装上游 1.20.8；注：其 pyproject 含未发布的 `web-ui/dist` artifacts，全新 `pip install .` 需先删除 `[tool.hatch.build]` 段（运行时不需要前端）。
- **版本**：`VERSION` 17.3.1 → 17.3.4（单一来源）。

## [V17.3.1] 2026-09-19 — ZHB 下载节流缺陷修复

- **ZHB 下载节流逻辑修复（`core/zhb_client.py`）**：令牌文件 `.last_download` 由记录"日历日"改为记录"服务端返回的包数据日期"（YYYYMMDD）。`_zhb_needs_download` 抑制重下的判定由 blanket "今日是否已尝试"（每日一次闸门，会把同日 T+1 清晨发布的新包锁死到次日）改为——仅当"今日已成功拉取 且 服务端返回包日期 == 本地包日期（服务端确未前进）"才抑制；当本地落后于最近交易日时引入 3 小时重探冷却，使当日新包（如 `zhb_20260918`）可被拾取，而非滞留旧包直到次日。修复了"最新 ZHB 包停留在上一交易日"的缺陷（数据来源：通达信）。单元验证 6 项断言全过（不联网，monkeypatch 日期/时间）。

## [V17.3] 2026-09-18 — 架构重构落地 + 字段治理闭环

- **运行时去 exec 重构（核心架构调整）**：`stock_common/sc_datasource/__init__.py` 由 `exec()` 动态注入改为显式模块导入 + 共享状态对象（`_shared.py`）传递，消除隐式命名空间、可静态分析、可 mock。逐片段提交（阶段1 抽取 _shared / 阶段2 显式导入 / 阶段3 re-export / 阶段4 mock 契约迁移 + 全量回归），全源对撞引擎复跑零回归。
- **死代码清理**：vulture + pyflakes 分级扫描，Grep 二次确认无动态引用后分批删除（含 `stock_common/__init__.py` 死 re-export）；每批跑全量测试并独立提交。
- **适配层字段治理**：补 `meaning` 元数据并标 `verified`（fuyao 带点字段 6/6 命中 `12.8.12c-z` 标准契约表）；`cell_token` 修复——camel 源 token 含 `.` 时取完整带点 token（如 `snapshot.price_change`）。
- **通用跨源 mapping 存储**：新增 `docs/verify/cross_source_align.md`，集中记录 `fuyao.snapshot.*` / `tdx.quote_full.*` / `eltdx.quote_snapshot.*` / `zhb.full.*` / `tencent[*]` / `push2.f*` / `ulist239.f*` 的等价/互证关系（中文语义 + 证据），统一此前散落的附录术语。
- **对撞流水线**：`20260918` 全量采集 → L1 候选 sanctioned 定案 → 治理闸门（G1 基线比对 / G3 幂等 / parity）全绿分批提交；`collide.py` 证伪回归护栏固化。
- **版本**：`VERSION` 文件由 `17.2.9` 升 `17.3`（单一来源，代码经 `get_version()` 读取，无硬编码）。
- **registered_field_sets 扩展至 tdx/eltdx/zhb 带点 token（#260 字段治理收口）**：`audit_field_completeness.py` 的 `registered_field_sets()` 原先只覆盖 fc/fuyao/东财等主源，TDX 行情快照、eltdx 适配层、ZHB 三族的带点 token（`quote_full.*` / `quote_snapshot.*` / `shortline.*` / `stat.*` / `stat2.*` / `tipinfo.*`）无法被标 `verified`。本轮在 `field_dict.md` 新增 5 张标准契约表（12.8.12j2 TDX tdx_quotes、12.13.10c eltdx 适配层、1.1 tdxstat、2.1 tdxstat2、3.1 tipinfo），经黄金锚对撞定案后逐字段标 `✅ L1`；同步修复 `extract_registry.py` 的 `cell_token` 带点 token 优先级 Bug（ZHB 在 `_INDEX_SRC` 时 `[N]` 分支吞掉带点 token → 提前带点分支，使 `stat.*`/`stat2.*`/`tipinfo.*` 完整保留形态并挂上 meaning/status）。重生 `field_registry.json`：字段 **1484→1807**、源 **24→26**（新增 TDX-eltdx 适配层）、记录 2440、对齐 131；G1 基线比对 / G3 幂等 / P1 预检全绿，11 抽样 token 全部 `status=verified` 且 meaning 正确。
- **cross_source_align.md 全量 49 候选定案（#261 黄金锚复核收口）**：将 `20260918_crack_candidates.json` 的 49 条 L1 候选（含原 6 条排除项 #4/#19/#22/#33/#34/#36）经双黄金锚（fuyao/东财官网锚）复核后补齐入 `docs/verify/cross_source_align.md`。复核结论：5 条有效（#4 `fuyao.snapshot.volume`=成交量、#22 `tencent[68]`=52周最低、#33/#34 `zhb.*.low_52w`=52周最低、#36 `tencent[69]`=10日涨跌幅），其中报告 §二 对 #4/#22/#33/#34 锚义误标（change_pct_2d/tx[69]/EPS）均经黄金锚回订正；1 条证伪（#19 `tencent[23]`→`sina[25]` 标注"丢弃"，维持证伪、不落字段、仅作护栏备案，见 §三）；另补入首轮遗漏的 `ulist239.f13/f19/f27`。重生 `field_registry.json` 对齐 **131→139**（+8 等价映射 durable 定案），字段数/记录数/源数不变（1807/2440/26），G1/G3/P1 全绿。
- **采集原始数据入库（#259 20260918 批次归档）**：将 `docs/field_verification/20260918/` 本轮全量采集的 **25 个 `raw_*.json`**（axdata/clist/cls/cninfo/datacenter/eltdx/em_fund_flow/em_hot/em_kline_f61/exchange/ftshare/fuyao/market_sources/push2/push2_full/push2ex/reports/sina/slist/tdx/tdx_f10/tdx_f10_more/tencent/ulist239/zhb）+ **4 份报告**（20260918_collision_report.md/.json、20260918_crack_report.md/.json）经 `git add -f` 强制入库（`.gitignore` 默认忽略 `*/raw_*.json`/`*/meta.json`，本批次为一次性归档；`meta.json` 与 `cache/*` 仍按策略排除）。
- **reports/ 数据质量修复（V17.3 报告生成器治标）**：核查 20260918 批次 37 篇报告，修复 3 处真实错误 + 定位跌停计数矛盾根因 + 厘清 val 0 数量策略成因：
  - `get_med_report.py` 互动易未回复渲染字面 `答案: None`（cninfo_irm 偶发返回字面字符串 "None"）→ 归一为"（公司待回复）"，与 sht 口径对齐（V17.3）。
  - `get_sht_report.py` 流通市值不自洽（002360：流通股本 3.26亿×现价 5.33 = 17.38亿 ≠ 报 16.44亿，偏差 5.4%）→ 流通市值改由 `流通股本×现价` 推导，与总市值/现价同源同价基（V17.3）。
  - `get_sht_report.py` 跌停计数矛盾根因：sht 原信任 `get_limit_pool_summary().limit_down_count`（跌停池接口 stale，实测 33 篇报 3 只），而 `get_mak_report` 用全市场 ZHB 快照 `is_limit_down` 口径得 0 只；修复为 sht 优先采用与 mak 同源的实时涨跌幅口径（仅在快照源不可用时回退 pool），消除 3 vs 0 矛盾（V17.3）。
  - `core/eltdx_adapter.py` 新增 `is_eltdx_available()` 轻量探测；`get_val_report.py` 策略 26/27（连板梯队/短线资金强度，依赖 eltdx 本地 TDX）空产出时区分"数据源缺失"与"真实无符合"——实测 0 为 eltdx 未连接导致的降级（非真实无连板/抢筹标的，当日 77 只涨停必有连板），报告显式标注"⚠️ 数据源不可用"（V17.3）。策略 02 周线多头 0 为严格 MA 多头排列条件导致的真实无符合（无误）。
  - `get_lng_report.py` 总股本=0 **单位 Bug（活体，非陈旧产物）**：`info.total_shares` 实测单位为**万股**（== `cdata.total_shares_wan`，如 000938=286008 万股），原 `get_lng_report.py:398` 误按 股 `/1e8` → 0.00286亿股，界面显示 `0.00亿股`，且正数值绕过 V17.2.26 的 `<=0` 守卫与"数据暂缺"分支。更正为 `/1e4` 与 canonical 兜底同源同单位（V17.3）。复盘：前期审计将其误判为"V17.2.26 已修复的陈旧产物"，实为活体单位 Bug——本次对 000938 重跑（后修复）先复现 `0.00亿股`、修复后得 `28.60亿股`，已实证修正。
  - **统一层跨层同步修复（V17.3，大盘股市值静默错 10000 倍）**：`core/data_provider.py` 内联的 `total_shares_wan` 单位归一守卫阈值误用旧值 `>1e7`（与已订正的 `sc_capital_cache` v2 阈值 `1e9 万股` 直接矛盾——后者注释已实锤 `1e7` 曾把正确大盘股万股值误当"股"再÷10000）。修复：阈值对齐为 `>1e9`；并对 `float_shares_wan`、`float_mcap_yi` 补对称守卫（`float_shares_wan >1e9` 万股→万股、 `float_mcap_yi >1e6` 万元→亿），与既有 `mcap_yi` 守卫一致。实盘复现：修复前 `601398 工商银行` 总股本被误算为 3564 万股（实为 35640624 万股=3564亿股）、总市值 2.87 亿（实为 2.88 万亿）；修复后正确。此前 20260918 批次审计因被测股 000938 为中盘（286008万股<1e7）漏检，**历史大盘股（>1000亿股）sht/med/lng 报告市值曾被静默误算**。
  - **缓存层核查结论（V17.3）**：无需同步更新。`sc_kline_cache.py` 已有 24h TTL + 500MB LRU 自动失效；`sc_capital_cache.py` 已有 schema 版本号（v2）自动失效重建；ZHB 快照 T-1 陈旧为设计预期（用户同步刷新）。字典破解（#257-#261，49 候选）映射的是原始 f 编号语义，由源适配器（sc_datasource/zhb/tdx）消费，统一层合约经适配器自动继承订正，无需新增合约字段暴露（V17.3 脚本修改所用字段 total_shares_wan/float_shares_wan/float_mcap_yi/mcap_yi/price 均在既有 86 字段 frozen 契约内）。
  - **死代码清理（V17.3 续作已执行）**：① `cache/` 目录下 103 个未跟踪临时调试文件（`_dbg_*`/`_fix_*`/`_f821`/`_verify_*`/`audit_*`/`_phase*`/`_probe_*` 等）已清理完毕——保留 `README.md`/`_gitrun.py`(git闸门助手)/`stock_cache.db`(真实缓存库)/`em_industry_*.json`(数据桩)/`zhb`/`zhb_parsed`/`kline`(运行时数据缓存目录)，并清除误留的 `audit_venv/` 虚拟环境（数千文件）。
  - **循环导入架构级修复（V17.3 续作已执行·修正版 C）**：`core/data_provider.py:64` 顶层 `from stock_common.sc_network import _fallback_logger` 与 `sc_datasource/_quotes.py:20`/`_zhb.py:13` 顶层 `from core.data_provider import (get_concept_from_zhb + 5 ZHB 派生函数)` 构成导入期循环依赖，生产靠入口先载 stock_common 规避、直引 data_provider 即崩。修复：① 新建真叶子模块 `core/_accessors.py`（顶层仅依赖 `core.stock_cache` 叶子 + `typing`，6 个访问器函数体内懒引 `stock_common`/`core.tdx_client`/`core.zhb_client`，**顶层零 `stock_common` 依赖**）；② 将 `get_concept_from_zhb`/`get_dividend_yield`/`get_change_pct`/`get_change_ytd`/`get_amount_wan`/`get_main_net_buy`/`get_streak_days` 从 `core.data_provider` 迁出至 `_accessors`，`data_provider` 经 `from core._accessors import (...)` 保留 API 与 re-export 链；③ `_quotes.py:20`/`_zhb.py:13` 改引 `core._accessors`；④ `data_provider.py:64` 的 `_fallback_logger` 改为 `_debug_log` 函数内懒引（方案 A 同款）。**修复后实盘复现**：正/反向 `import core.data_provider` 与 `import stock_common` 均成功，导入期环彻底消除、import 顺序无关；`get_canonical_stock_data` 与 6 函数行为不变（`get_dividend_yield('000938')=0.2` 等正常返回）。**关键复盘**：原方案 B（改引 `core.zhb_client`）经证伪无效——`zhb_client` 顶层亦引 `stock_common`，仍成环；原"70 处 lazy 断环"系红鲱鱼（函数内调用期导入不构成环，真实环仅 3 条顶层边）。
  - **统一层同义字段"绕过"审查（V17.3 续作）**：回应"sht/med 正常而 lng 错"疑问——**非统一层遗漏字段**（`total_shares_wan` 等已在 `CanonicalStockData` 契约内且正确），根因是脚本绕过统一层直取 `get_stock_info()['total_shares']`（万股）却多处按"股"假设。审查又确证 2 处同类单位 Bug 并修复：`get_lng_report.py:531` 传 `info.total_shares`(万股) 给 `get_roe_trend_series` 新浪兜底 `eps=profit/total_shares`(期望股) → EPS/BPS 错 1e4 倍；`get_sht_report.py:983`/`get_med_report.py:947` 北向占比兜底 `_shares`(股)÷`info.total_shares`(万股) 单位错配(差1e4) 且 sht 无 ×100、med 有 ×100 两脚本口径互不一致(差100倍)。三处统一改为 `cdata.total_shares_wan*1e4`(股) 并 ×100 百分数对齐。建议增强：统一层新增 `total_shares`(股) 便捷字段从源头消灭股/万股陷阱（详见 `docs/REPORT_REVIEW_BYPASS_20260918.md`）。

## [V17.2.15] 2026-09-15 — TDX 主源切换 eltdx（Rust 客户端接管行情/财务）

- **背景**：V17.2.12 的 easy_tdx 握手补丁是 dead-upstream 的临时续命（上游 `awayings/easy_tdx` 已 404，PyPI 不可装）。`eltdx`（Rust 内核 7709/7615 客户端，零依赖，Research-Only 许可）握手已含 2026-09 新式单条随机 msg_id，且协议层更完整（含 limit_ladder/题材强度/短线指标/集合竞价/逐笔等 net-new 能力）。
- **新增 `core/eltdx_adapter.py`**：`_EltdxAdapter` 把 eltdx 包装成 mootdx 兼容接口（DataFrame 列名/单位对齐），供 `tdx_client.py` 零改动消费。覆盖 quotes / bars(index_bars) / finance(0x0010) / xdxr(stub) / F10C·F10(返回空→走东财) / price_limits·market_stat(尽力而为)。
- **单位换算关键修复**：eltdx `FinanceRecord.*_raw_float` 聚合字段为**千元**口径（非万元），映射 mootdx 角口径须 ×10000（data_provider 对 zongzichan/jingzichan/jinglirun 按角 `/10` 得元）。实测反推：平安银行 `zong_zi_chan_raw_float=6.029e9` 千元 → 元=6.03万亿（与实际吻合）；首版误用 ×100000(万元→角) 会算出 60万亿，已订正。
- **主站固定**：`TdxClient(hosts=[...:7709], probe_hosts=True)` pin 6 台 FULL 白名单（V16.2.11/16.3.9 复测），冷连接 6 分钟全量探测 → 4 秒，消除延迟痛点。
- **握手补丁处理**：`tdx_client.py` 移除 `core._tdx_handshake_patch` import（eltdx 不需要）；**保留** `zhb_client.py` 的补丁 import——ZHB 报告 ZIP 下载走 easy_tdx 文件传输（eltdx 无此能力），仍需补丁修复 2026-09 握手。补丁文件 `core/_tdx_handshake_patch.py` **未删除**（zhb_client 仍依赖）。
- **依赖**：`requirements.txt` 新增 `eltdx>=3.2.2,<4.0`（TDX TCP 主源），easy_tdx 注释收窄为"仅 ZHB 下载保留"。
- **实测**：`tdx_get_finance_info('sz000001')`→ 元 6.03万亿 / BVPS 24.13；`tdx_get_security_bars`→ 3 行真实日K；quotes 快照 price/last_close/amount/s_vol/b_vol/五档齐全。北交所(83/87/92)快照 eltdx 偶发解析失败（"snapshot record marker not found"），已优雅降级到上层 HTTP fallback。
- **配套（Step B/A）**：`scripts/capture_field_probe.py` 新增 `collect_eltdx` 采集源（命名+原始字节双轨），`field_registry.json` 登记第 24 源（簇尾 level-4 粘滞继承，不动东财主路径）；见 `docs/eltdx_smoke_report_20260915.md`。

## [V17.2.12] 2026-09-15 — TDX 新式握手修复（A 路线：最小侵入 + 固化）

- **问题**：2026-09 起通达信行情主站强制拒绝旧版三条固定握手（0x1893/0x1894/0x1899），握手有响应但连接上所有 K 线请求静默返回 2 字节空包（0x0320）、市场统计/板块指数快照返回空、`/market/stat` 500——服务器不报错只是不给数据。项目依赖的 `easy-tdx 1.32.6`（上游 `awayings/easy_tdx` 已撤、PyPI 不可装）静态握手全面失效（P0 实证：4 台可达主机 K线全 0 行、market_stat 全报错）。
- **修复（直接 patch 在用包）**：`easy_tdx/commands/setup.py`（site-packages）的 `SETUP_COMMANDS` 由静态三元组改为单条动态握手 `build_handshake_command()`（`<HIHHH` = 0x010C + 随机 msg_id + 0x0003 + 0x0003 + 0x000D，payload 0x01）。transport 层遍历/ping/心跳下标访问均兼容，业务请求格式零改动。保留 `SETUP_CMD1/2/3` 常量供 `commands/__init__.py` 导入兼容。本机临时备份未纳入仓库。
- **固化守卫（防重装回退）**：新增 `core/_tdx_handshake_patch.py`，`import` 即把 easy_tdx 握手续命为新式动态单条握手，并回写 `transport.sync` / `transport.async_` 的模块级 `SETUP_COMMANDS` 引用以抗乱序 import；幂等（`_v17212_dynamic_handshake_patched` 标记）。在 `core/tdx_client.py` 与 `core/zhb_client.py` 顶部 `import core._tdx_handshake_patch`（须在 easy_tdx 绑定前；因 easy_tdx 引用均为函数内懒加载，模块顶部即满足）。**不**挂 `core/__init__.py`（其须保持空，防 core↔stock_common 循环依赖）。
- **实证**：patch 后在用包直连主站成功取到个股/指数日K（各 10 行真实 OHLC）、市场统计（上涨1404/下跌4073/总市值11.26万亿）；守卫模块 E2E 连接取 K线 5 行、transport 引用同步无陈旧、重复 apply 幂等。
- **影响面**：TDX 备用链（K线/市场统计/板块指数实时）由失效恢复为可用；东财主路径（quote/资金流/板块）不受影响。

## [V17.2.11] 2026-09-15 — 路由加固 + 官方备胎源(v3.8.0 同步)

- **文档同步债（A）**：`docs/field_dict.md` §12.6 追加 **V17.2.11 同步核查（v3.7.1→v3.8.0 delta）**——上游 V3.8.0(2026-09-05) 纯增量零 breaking，本 fork 不 import 上游函数仅按能力对齐；v3.8.0 新增 6 入口（指数成分/权重/估值、交易日历、沪深官方两融、北交所行情）中，项目已有等价能力者标记为 ⏸️ 按需启用。
- **路由加固（B）**：`stock_common/sc_utils.py` 的 `em_secid_prefix` 加 `.SH/.SZ/.BJ` 后缀识别（修复 v3.7.1 潜伏 bug——`000016.SH` 此前静默错票为深市 secid，因输入层归一化拦截未触发）；新增 `em_exchange_prefix(code, upper=False)` 统一产出交易所 mnemonic（sh/sz/bj 或 SH/SZ/BJ）。收敛散点 `code.startswith("6")` 路由（_eastmoney/_financials×3/_quotes×2/_holders×2/sc_utils 共 9 处）到 `em_exchange_prefix`；`_quotes.py:23` 的腾讯前缀同时补齐 43/83/87 北交所老号段（此前仅 8/4/92）。
- **沪深官方两融降级源（C）**：新增 `stock_common/sc_datasource/_official_backup.py`（移植上游 V3.8.0 `margin_trading_backup` + Layer12 官方源辅助函数），提供 `get_margin_trading_backup(code)`——按代码自动判交易所(SH/SZ)、遍历最近交易日取已发布快照，归一化为与 `get_margin_trading` 一致的 dict 形状。归并进 `get_margin_trading`：东财 datacenter 空结果/封禁时自动降级，不依赖东财。
- **北交所官方行情降级源（D）**：同模块提供 `bse_quote_backup` + `get_bse_quote_backup(code)`（北交所官方行情+五档，须核对交易日）。归并进 `get_em_quote_full` / `get_em_quote_full_delay`：北交所代码东财 push2 空结果/封禁时自动降级到北交所官方源，扩面并提升鲁棒性。
- **导出**：`stock_common/__init__.py` 的 `__all__` 与 `sc_datasource` 导入块补充 `get_margin_trading_backup` / `get_bse_quote_backup`。
- 注：官方备胎源为独立官方域名（sse.com.cn / szse.cn / bse.cn），不走东财限流，东财封禁时仍可用；实测 600519(茅台) 上交所两融、920021(流金科技) 北交所行情均成功取数。

## [V17.2.10] 2026-09-13 — 动态层每日刷新(涨停池选连板/新股/涨停)

- **`scripts/capture_field_probe.py`（新增）— `refresh_dynamic_layer()` 动态层每日刷新**：实现 `pool_rules.dynamic_refresh` 长期缺失的能力。`pool.json` 的 `dynamic` 5 只此前静态冻结（自 20260812）。现支持：
  - 从同花顺涨停揭秘 `ths_limit_up_pool`（东财 `get_limit_up_pool` 兜底）取涨停池，按「连板数 → 新股 → 涨停」优先级选 5 只写回 `pool.json` 的 `dynamic`（`date=最近交易日`），固定层 15 只不动，剔除与固定层重复代码。
  - **连板数独立解析**：上游 `ths_limit_up_pool` 的 `limit_count` 对 `"N天M板"` 格式解析恒为 1（上游 bug），改由新增 `_parse_consecutive_boards(high_days)` 从 `"M板"` 末位解析真实连板数。
  - 网络/接口空时**保留原动态层、不破坏采集**；周末/非交易日自动回退最近交易日快照。
  - 新增 CLI：`--refresh-pool`（采集前刷新）、`--refresh-pool-only`（仅刷新不采集）。
- **文档**：`scripts/README.md` 与 `docs/field_verification/README.md` 补记每日工作流 `capture_field_probe.py --refresh-pool`；采集脚本 docstring 同步新增用法。

## [V17.2.9] 2026-09-13 — 通用全源对撞引擎 collide.py 取代定向脚本

- **`scripts/collide.py`（新增）— 全源全字段通用对撞引擎**：覆盖 `docs/field_verification/<date>/raw_*.json` 的全部采集数据，按 `collision_rules` 四铁律（精度对齐 + 每日命中率≥0.9 + ≥3 独立采集日 + hub 巧合排除）做跨源对撞；增量状态 `collision_state.json` 跨日累积，日常只冒"新增"、已定案标 `✅` 再确认；报告拆分"异号同义（高价值）"与"同号镜像（低优先）"。取代上一轮把定向脚本简单拼合的 `crack_fields.py`。
- **`scripts/collision_rules.py`（新增，V17.2.8 规则真相源）— 对撞四铁律 + 定案状态机**：常量固化为代码真相源，对撞入口自动 `print_active_rules()`；`--emit` 派生人读文档 `docs/field_verification/COLLISION_RULES.md`，与代码常量一致防双源漂移。
- **清理**：删除上一轮两个定向脚本 `crack_ulist_residuals_20260912.py` / `crack_zhb_col22_20260912.py`（功能已被 collide.py 全量覆盖）。
- **文档**：README 三处（根 / scripts / field_verification）补记每日「采集 → 全量对撞」流水线；新增 `docs/field_verification/20260913/` 本轮全量对撞报告（.md + .json）。

## [V17.2.7] 2026-09-07 — 修复 mak/val 报告数据矛盾与章节口径

- **`get_val_report.py` 广度口径修复（根因：ZHB T-1 污染）**：
  - 原仅用腾讯 T 日 `price` 覆盖 ZHB，但 `change_pct` 仍为 ZHB T-1 → 风控仪表盘涨停/跌停按 9/4 快照计算，与 mak 同日(9/7)广度(87/92/95)不可比。现**同步覆盖腾讯 T 日 `change_pct`**（盘前/休市旁路时 `_price_map` 为空则不覆盖，保留 ZHB T-1）。
  - **数据基准标签修复**：原 `数据日期` 恒为 ZHB 日期 + `✅新鲜`(仅看 ZHB 3 日容忍)，具误导性。现按实际取数路径标注——盘后/盘中=`✅T日收盘`/`✅T日实时`+今日日期(与 mak 同基准)；盘前/休市=`⚠️T-1快照(最新交易日)`+ZHB 日期。
- **`get_mak_report.py` 连板梯队首板修复**：原 ret_3d 阈值误杀导致 `首板≈1`（涨停总数 92 却首板仅 1）。现**首板 = 样本涨停总数 − 连板合计**反推，保证 首板+连板 恒等于本段涨停总数。
- **`get_mak_report.py` 涨停/跌停多源口径标注**：明确 A 段「短线情绪(样本内·剔除ST/退)」87/3 与「全市场(通达信·含ST/退/北交所)」95/2 的口径差异（涨停含 ST/退/北交所故多于样本；跌停按主板10%口径故少于样本），与 B 段涨停池(财联社/KPL/复盘啦互校)92/2 三者不再看似矛盾。

## [V17.2.6] 2026-09-07 — lint 接上 scheme 血缘护栏

- **`scripts/lint_field_same_number.py` 升级**：新增 `check_scheme_grounded()` 血缘护栏——字典主张 `ulist.fX = push2.fY` 同义时，强制校验采集 meta 的 scheme 标识（`docs/field_verification/*/meta.json` 的 `schemes` 字段，回退 `BUILTIN_SCHEME`）。
  - 确认 `ulist239=em.ulist.np` ↔ `push2=em.stock_get` 属不同字段体系，故任何 `ulist↔push2` 同义主张**必须以权威对齐表 `ulist_push2_align.md` 的跨号映射条目为实证**；即便 X==Y（同号）也只是"同号"而非"同义"。
  - 违规消息精确到 scheme 标识与缺失的跨号编号；scheme 未加载时降级为告警不阻断，保证 CI 健壮性。
  - 仍保留全文件回归扫描（裸「同号即同义」断言零复发）。与 `verify_cross_source_crack.py` 的 `BUILTIN_SCHEME` 对齐。

## [V17.2.5] 2026-09-07 — 采集脚本字段体系(scheme)血缘标注(A 方案落地)

- **采集脚本 `scripts/capture_field_probe.py`**: 新增 `SOURCE_SCHEME` 映射, 为每个源标注字段体系(scheme)
  (东财两套 f 编号族 `em.stock_get` vs `em.ulist_np` 同号≠同义; 其余源为独立命名/数组体系)。
  - `main()` 写入每个 `raw_{source}.json` 顶层 `scheme` 键 + `meta.json` 的 `schemes` 映射与各源 `scheme` 项。
  - 目的: 从数据血缘层面固化「同号即同义」陷阱的硬提示, 供对撞工具/lint 校验。
- **对撞工具 `scripts/verify_cross_source_crack.py`**: 新增 `source_scheme()`(raw 无 scheme 键时回退 `BUILTIN_SCHEME`,
  兼容 19 个历史目录) + 每条候选标注 `target_scheme/anchor_scheme`, 并捕获
  **跨端点同号风险**(ulist.np 与 stock/get 以同一 f 编号精确命中)在报告 §五 单列复核。
- 样本池不变(维持 A 股 20 股, 用户确认无需 AH/ETF/可转债); 本次仅补字段血缘元数据, 不改动任何字段取值或采集逻辑。

## [V17.2.4] 2026-09-07 — 第九轮跨源对撞破解 3 字段 + lint CROSS 类 + 字典纠错

- **跨源对撞破解（78 待核实 → 3 L1 定案 / 3 L4 / 72 未解）**：基于 `CRACKING_METHODOLOGY.md` 四铁律，
  以 `push2_full/em_fund_flow/zhb/tencent/fuyao/sina/tdx` 多源锚对 78 个 ulist239 待核实字段做精度对齐数值对撞。
  - `f142`=买二价(bid2)（tdx/sina[14]/腾讯[12]，16日 rate 1.0，spot-check 茅台 1297.40 逐字等）
  - `f143`=卖二价(ask2)（tdx/sina[24]/腾讯[22]，16日 rate 1.0，spot-check 茅台 1297.55 逐字等）→ 纠正先前「资金流」误判路径
  - `f160`=20日涨跌幅%(腾讯[70]口径)（16日 rate 1.0）→ **≠push2 f120/ulist f110**（同名异义，茅台 -0.79 vs -0.69）
- **关键纠错（铁律兜住两个伪命中）**：
  - `f190=tdx hgu` 为「退化锚伪命中」（纯A样本 95% 为 0）→ 补 `anchor_degenerate` 护栏后剔除，f190 维持待核实（实测 95% 为 0、非0恒=3.0）
  - 字典 line 1363「`腾讯[70]=push2 f120×100`」为错误断言 → 订正为「`腾讯[70]=ulist f160`，与 push2 f120 非同一口径」
- **lint 加固**：`scripts/lint_field_same_number.py` 新增 `CROSS` 证据类（✅ + 跨源/第九轮审计标记 + 具名外部源），将「跨源对撞定案」列为「同号即同义」铁律的合规解药。
- 工具：`scripts/verify_cross_source_crack.py`（永久跨源对撞引擎，含锚退化护栏）；报告：`docs/field_verification/20260907_round9_cross_source_crack.md`

## [V17.2.3] 2026-09-07 — 同号即同义 lint 守卫 + 78 条待核实扩展采样对撞

> 类型：工具链/文档（无运行时字段取数变更；纯校验与解释性产出）。

### ① 字典 lint 规则：同号即同义守卫（task 2）
- 新增 `scripts/lint_field_same_number.py`（对标既有 `lint_field_names.py`）：扫描 `docs/field_dict.md`
  §12.3.2.3 ulist239 登记表 + 全文件 f 编号行，**禁止「仅凭字段编号相同就认定语义相同」**的裸断言，
  并要求任何声明 ulist↔push2 映射的登记必须在权威对齐表 `docs/verify/ulist_push2_align.md`
  （ulist fN → push2 fM）登记实证；违规退出码 1（可接入 CI/提交前检查）。
- 字典 §12.3.2.3 表头新增「**新增字段登记公约**」：声明 push2 映射须先在对齐表登记跨源对撞证据，
  无实证者必须标 `⚠️ 同号同义·未实证·待核实`。
- 现状：当前字典 113 行订正后 lint 通过（exit 0）；含负向用例验证（注入裸断言即报错）。

### ② 78 条待核实字段扩展采样数值对撞（task 1）
- 将第七轮临时 `remap`/`xref` 固化为永久工具 `scripts/verify_ulist_push2_collision.py`：
  跨 `raw_ulist239.json × raw_push2_full.json` 配对目录做精确数值相等对撞 + Pearson 相关，
  含**常量护栏**与**空标记护栏**（'-'/空不计入匹配，避免「都空↔都空」伪匹配）。
- **扩展采样**：当日（2026-09-07）实采新增 1 个配对目录，语料 360 → **380 样本股**（19 交易日 × 20 股）。
- 结论（380 样本，与 360 一致）：**52 NO_MATCH + 24 CONSTANT_DEGEN + 2 WEAK_HINT**，0 确证。
  即 78 条绝大多数为 **ulist 专属字段**（退化恒值或无 push2 对应），仅 f147→f107@0.53、f190→f78@0.94 两条弱候选
  （相关性近零，未认定，维持待核实）。数值对撞已触平台期——瓶颈在「ulist/push2 本就不同字段体系」，
  后续建议转语义交叉引用（fuyao/ZHB/TDX 字段枚举）而非继续扩量。
- 报告：`docs/field_verification/20260907_round8_collision_unverified.md`。

## [V17.2.2] 2026-09-07 — 字典「同号即同义」断言审计与订正

> 类型：纯字典/文档审计（无代码变更，运行时行为不变）。

### ① 排查：字典同字段「凭编号相同就认定语义相同」的系统性错误
- 对象：`docs/field_dict.md` §12.3.2.3 `ulist239 全字段清单` 表中 113 条
  `| fN | ✅ 同 push2 fN（语义见 §12.9.1） | ulist/push2 同号，跨源引用 |` 断言。
- 方法：取 `docs/field_verification/20260812~20260906` 共 **18 交易日 × ~20 股 = 360 配对样本**，
  对 ulist 每 `fN` 与 push2 全字段做精确数值相等对撞（相对误差 ≤1e-6），并以权威对齐表
  `docs/verify/ulist_push2_align.md`（ulist fN → push2 fM 跨号映射）为基准分类。
- 结论：**仅 2/113（f153、f154）真同义**；**33 条为异号映射**（原「同 push2 fN」错误，实为 `ulist fN = push2 fM (M≠N)`）；
  **78 条无实证**（对齐表无条目，同号同义未经验证）。
  即「凭字段编号相同就认定语义相同」是系统性错误（与字典自身 L1827「ulist239 索引 ≠ push2 索引」警告直接印证）。

### ② 更正：逐行订正 §12.3.2.3 表（113 行）
- 2 条同号真同义：保留 `✅`，补「已数值实证，第七轮审计」注记。
- 33 条已证伪：改为 `⚠️ 同号同义·已证伪 → 实测 ulist fN = push2 fM（异号映射，见对齐表）`，并标注正确跨号映射
  （例：f62=f137 主力净、f115=f164 PE-TTM、f144=f43 现价、f114=f163 静态PE）。
- 78 条无实证：降标 `⚠️ 同号同义·未实证·待核实`，留待更多采样数值对撞补全。
- 表头 blockquote 加 ⚠️ 阻断性警告：同号≠同义，语义须按对齐表跨号映射，严禁凭同号认定同义。

### ③ 固化铁律
- 凡跨接口引用东财字段，**必须查 `docs/verify/ulist_push2_align.md` 跨号映射，严禁凭同号认定同义**（已写入工作记忆「东财跨端点同号异义铁律」）。

## [V17.2.1] 2026-09-07 — 五档资金流补全 + 多日聚合(f164/f165)进 canonical

### ① 五档资金流「买/卖毛额」补全（8 字段）
- `sc_schema.py` 新增 `fund_main_buy/sell`(f135/f136)、`fund_super_buy/sell`(f138/f139)、
  `fund_large_buy/sell`(f141/f142)、`fund_mid_buy/sell`(f144/f145)。
- 此前 `_quotes.py:606-618` 已映射全 13 个资金流字段，但 `data_provider` 补取块与构造函数
  **只透传 6 个净额**，8 个毛额被丢弃 → 现已补齐（毛额用于多空力道判断）。
- 实跑自洽校验（茅台 2026-09-07 盘中）：主力买 f135 = 超大单买 f138 + 大单买 f141
  (231726069 + 752484240 = 984210309 ✓)；主力净 f137 = 超大单净 f140 + 大单净 f143
  (-135603835 + 64083504 = -71520331 ✓)。

### ② 多日主力净聚合（ulist.np f164/f165）
- 新增 `get_em_fund_flow_multiday(code)`（`_quotes.py`），走 **ulist.np 端点**取
  f164(近5日主力净, 元) / f165(占比 %)。
- **⚠️ 跨端点同号异义铁律**：push2delay **主域 stock/get 的 f164 = pe_ttm**（估值字段），
  与 **ulist.np 端点的 f164 = 多日主力净** 同号不同义（东财跨端点复用 f 编号）。
  新函数固定走 ulist.np，绝不从主域读 f164，避免污染 pe_ttm。
- `data_provider`：f178 数组聚合仍为 `fund_main_5d` **主路径**；缺失时由 f164 兜底；
  新增 `fund_main_5d_pct`(f165)。
- 实跑（2026-09-07 盘中）：茅台 565,785,777 元 / 3.3%；农行 101,161,008 / 0.95%；
  宁德 -287,783,168 / -0.73%。

### ③ 第五轮破译结论落地
- `docs/field_verification/20260907_round5_multiday_check.md` 证实 ulist f164 = 最近 5 个
  **交易日**主力净(f62)滚动和，命中 10/11（按交易日序，非自然日）→ 本轮据此落地。

**验证**：3 文件 `py_compile` 通过；系统 Python 3.12 全量回归 **524 passed / 6 skipped / 0 failed**。


## [V17.2.0] 2026-09-07 — 移除 thsdk TCP 网关 + 源降级与缓存优化

> **状态：已完成。** 本轮主线："降低对东财/push2 的依赖、剔除仅盘中可用的 thsdk 网关"（用户场景为盘后/盘前运行脚本，thsdk 仅盘中可用，不符合）。

### ① 移除 thsdk TCP 网关
- 删除 `stock_common/sc_ths.py`（thsdk 唯一载体，`from thsdk import THS`）。
- `stock_common/__init__.py`：移除模块级导入与 `__all__` 中 3 个 THS 导出名。
- `core/data_provider.py`：删除 `_THS_FUND_CACHE` 全局缓存变量、T2 主力净流入 THS 快照兜底块（回退为仅东财 `push2delay f137`）、THS PB 兜底块（PB 改由 TDX `price/bvps` 兜底）。
- `get_val_report.py`：删除 val04 的 `pb_ths` THS 抓取与跨源校验（纯调试，不影响 canonical 取值）。
- `docs/field_dict.md`：市净率 canonical 去 `THS(pb)`；主力净 canonical 去 THS；源排序链/可用性表去 thsdk 节点；§12.8.12b 加"已退役 2026-09-07"横幅；余 2 处能力清单/提权叙述标注退役。
- **保留**：同花顺 HTTP 网页接口（`get_ths_hot_raw` 强势股热榜 / `ths_limit_up_pool` 涨停揭秘，走 `zx/data.10jqka.com.cn` REST，盘后仍可用，报告在用）。

### ② 涨停/跌停价脱离 push2（腾讯[47]/[48]）
- `stock_common/sc_datasource/_quotes.py`：`get_tencent_quote` 的 `raw` 字典与透传白名单增补 `limit_up`(tx47) / `limit_down`(tx48)。
- `core/data_provider.py`：腾讯 extras 补取块（不受 price 门控）增补 `limit_up`/`limit_down` 取数——push2(f51/f52) 不再是涨跌停价唯一来源。

### ③ 行业/板块分类季度缓存（降频东财，不换源）
- `core/stock_cache.py`：TTL 字典新增 `"industry_classification": 90*86400`。
- `stock_common/sc_datasource/__init__.py`：`_EM_L2_TTL` 由 7 天提升至 90 天（申万二级全市场映射内存+磁盘双级）。
- `stock_common/sc_datasource/_industry.py`：`get_em_belong_boards`（f127 行业 / f128 地域）加 `@cached(季度)`，命中后不再打 push2 主域。

### ④ 字典正确性订正
- `docs/field_dict.md` §12.8.12e：ZHB `main_net_buy_amount` 实锤=竞价额（非主力净流入），从"主力净买入额"canonical 移除（2026-08-14 实锤回填）。

### ⑤ easy-tdx 升级到 v1.32.6 + TDX 协议直解字段落地
- `requirements.txt`：easy-tdx 下限 `>=1.20.4` → `>=1.32.6`（仓库已到 v1.32.6/2026-09-06；本机 venv 实测已装 1.32.6，升级=提锁下界，无需新依赖）。
- **高优·内盘/外盘/涨速**：`easy_tdx` 的 `SecurityQuote` 已协议直解 `s_vol`(内盘/主动卖)/`b_vol`(外盘/主动买)/`rise_speed`(涨速)，此前 `tdx_get_quote_full` 只抽了 OHLC 五档而漏掉这 3 个。现于 `tdx_client.py` 的 TDX 补取块提取 → `sc_schema.py` 新增 `s_vol`/`b_vol`/`rise_speed`（默认 0）→ `data_provider.py` 合并链（批量预取路径下 TDX 未被咨询，主动补 1 次 TCP）+ 构造函数透传。零新源、零派生。
- **中优·涨跌停价 TDX 计算兜底**：新增 `tdx_get_price_limits(code, pre_close)` 调 `easy_tdx.get_price_limits`（按昨收规则，ST/创业板/无涨跌幅窗口等自动处理）。在 `data_provider` 合并链作为腾讯[47/48] 之后的兜底层（优先级：腾讯 > TDX计算 > push2 f51/f52）。源无关，盘前/盘后稳。
- **低优·市场广度**：新增 `tdx_get_market_stat()`（easy_tdx `get_market_stat`，通达信 880005/880001/880006 统计指数，60s 进程内缓存），接入 `get_mak_report.py` 与 `get_sht_report.py` 的广度/打板章，交叉校验样本涨跌家数与涨停/跌停家数。

### ⑥ 申万口径核验（用户问：TDX 申万能否替代不稳定的东财？结论：不能翻转）
- 经离线解析 `tdxhy.cfg`（库自带格式 `市场|代码|T一级(T码)|空|空|X细分码(X码)`）：**TDX 无任何申万列**；easy_tdx `parse_tdxhy_cfg` 把 `parts[5]` 标为 `sw_industry` 是误读，实测值 `X500102`/`X210205` 等为通达信 X码（非申万名）。
- 故 **TDX 无申万源可挖**，东财 `em_industry_map_l2`（申万二级）仍是唯一申万来源，不可作 primary/fallback 翻转。
- 项目安全目标已由 **③ 季度缓存**达成：东财封禁最严时也仅 ~4 次/年回源。`docs/field_dict.md` §12.8.12e 新增核验结论 blockquote；内盘/外盘/涨速 canonical 行由"未接"订正为 TDX `s_vol/b_vol/rise_speed`；`SecurityQuote` 字段表 stale 的"rise_speed 缺失"注记订正。

**验证**：`py_compile` 全 5 文件通过；系统 Python 3.12 全量回归 **524 passed / 6 skipped / 0 failed**（含内盘/外盘/涨速/涨跌停/广度新接线）；活跃代码零 thsdk 残留。

### ⑦ 补丁：V17.2.0 中优/低优 静默失效修复（2026-09-07 实跑发现）
- **根因**：`_EasyTdxAdapter` 仅暴露 `bars/quotes/finance/xdxr/F10` 等方法，**无 `get_price_limits`/`get_market_stat`**；而 `tdx_get_price_limits`/`tdx_get_market_stat` 直接调 `client.get_price_limits(...)`/`client.get_market_stat()` → `AttributeError` 被 `except` 吞掉。两功能自 V17.2.0 上线起从未生效（离线测试 mock 未覆盖调用点，未捕获）。第二层根因：`easy_tdx.get_price_limits` 要 `Market` 枚举，而本项目 `_easy_market` 返回 int。
- **修复**：适配器新增 `price_limits(symbol, pre_close)`（内部 int→`Market` 枚举转换）与 `market_stat()`；对应调用点改调 `client.price_limits(...)` / `client.market_stat()`。
- **实测（真实 TDX 客户端）**：涨跌停价 茅台 1428.77/1168.99(×1.10)、宁德 419.4/279.6(×1.20)、中芯 148.64/99.1(×1.20) 全对；市场广度 涨停 41/跌停 9/上涨 2444/下跌 2914/总市值 11.4 万亿 正常返回。
- **采集器增强**：`scripts/capture_field_probe.py` 的 `collect_tdx` 显式暴露 TDX 协议直解字段 `s_vol`(内盘)/`b_vol`(外盘)/`rise_speed`(涨速) 为顶层键，便于 `field_verification/` 纵向碰撞序列串联（源=本地 easy_tdx，非云连接器）。

**验证（⑦）**：`py_compile` 全通过；真实 TDX 客户端实测两函数输出正确；系统 Python 3.12 全量回归 **524 passed / 6 skipped / 0 failed**（适配器改动无回归）。


## [V17.1.0] 2026-09-04 — V17-2 重构：`sc_datasource.py` 拆包（完成，零回归）

> **状态：已成功完成。** god-module `stock_common/sc_datasource.py`（7617 行 / 162 顶层函数）按域拆为包 `stock_common/sc_datasource/`，对外 `from stock_common.sc_datasource import X` 零破坏。Python 3.12 全量回归 **518 passed / 2 failed / 4 skipped**，与拆包前基线完全一致（2 失败为 f10 实时数据既有断言，与本次无关），拆包引入回归数为 **0**。

**架构（共享命名空间法，规避首次尝试的「Facade 命名空间注入」缺陷）：**
- `sc_datasource/__init__.py` = 原文件「剔除函数体后的残体」：逐字保留 docstring、全部 import 块、全部模块级可变状态（缓存 dict / 字段索引 / 降级标志 / 常量）与其上方注释；末尾 loader 将各域子模块源码 `exec` 进本包（模块）的 `globals()`。
- 域子模块 `_holders`(15) / `_eastmoney`(36) / `_quotes`(21) / `_industry`(16) / `_financials`(30) / `_pools`(20) / `_zhb`(14) / `_misc`(10) 仅含函数定义（共 162）。
- **为什么无 bug**：① 全部函数/状态共处同一命名空间 → 模块级可变状态只有一份（根治首次尝试的 `KeyError: 'fund_super_today'`/缓存串号）；② 包内跨函数调用按名解析到包命名空间 → `mock.patch('stock_common.sc_datasource.X')` 对内部调用同样生效（根治 `m.call_args is None`）；③ 零 import 站点改动。

**等价性已验证**：运行时逐函数 `inspect.getsource` 比对，新包与原单文件备份的 173 个函数对象（162 顶层 + 导入辅助函数）源码字节级一致，无遗漏 / 无重复 / 无多余；且全包无重复定义。

**历史拆包脚本（已于 2026-09-28 清理）**：`scripts/split_sc_datasource_v2.py`；当时的等价性自检为 `scripts/_verify_split.py`。首次尝试产出的缺陷版归档 `stock_common/_ARCHIVED_sc_datasource_split_20260904/` 已被本版取代。该脚本不再是当前工具。

**V17-3 / V17-4 仍否决**（理由见 `docs/V17.1_REFACTOR_PLAN.md` §2/§3）。


## [V17.0.25] 2026-09-04 — 债务台账清零（DEBT-003/004/015 偿还 + DEBT-014 WONT_FIX）+ 文档滞后修复

**债务偿还（用户授权"4 项 OPEN 债务均可相应更改"）：**

### ① DEBT-003 — 删除 `pe_more` 冗余别名（A2）
- `sc_schema.py` 删除 `pe_more` 字段定义 + f164 映射元组；`data_provider.py` 删除组装赋值；`get_lng_report.py` / `get_med_report.py` 删除残留的 `pe_more` 假交叉验证 debug 自检（删除字段后仍引用 `cdata.pe_more` 会 `AttributeError`）；`tests/core/test_core_schema.py` 删除两处断言。
- 依据：`pe_more` 键已无任何源产出（f164 统一映射 `pe_ttm`），恒为 0 的死字段。消费方统一用 `pe_ttm`。

### ② DEBT-004 — 删除 `pe_static` 冗余数据键（A2）
- `core/tdx_client.py` `get_tencent_quote` 与 `_pre_market_quote_from_kline` 删除冗余 `pe_static` 数据键（与 `pe_lyr` 同源同值）。字段索引 `_TENCENT_FIELD_INDEX["pe_static"]=53`（槽位名）保留，被 `pe_lyr` 输出与 `sc_datasource` 引用。
- grep 确认无生产消费方读取 `pe_static` 数据键。

### ③ DEBT-015 — val「外资机构家数」标签澄清（A2）
- `get_val_report.py:1392` 文案「外资机构家数 N 家」→「外资机构家数（不含北向） N 家」。数值 `foreign_count` 语义无误（前十大流通股东中纯英文名外资机构家数，香港中央结算归北向不计），仅消除"同一句自相矛盾"的幻觉。

### ④ DEBT-014 — `bid_ask_net`（腾讯[86]）转 WONT_FIX（A8 论证）
- 完整语义定案需独立 L1 盘口快照对撞源（买一~五−卖一~五量）+ 同板块同时刻对齐 + 跨 4 类板块验证单位/符号，是独立 research 子项目，超出债务偿还范围。
- 当前 DEBT-007 降级展示（标注未定案、不参与信号）即永久正确行为，满足 A5 且不制造幻觉（不重蹈 DEBT-008）。定案研究单列 track。

**文档滞后修复（A7）：**
- `VERSION` 17.0.12 → **17.0.25**（对齐 CHANGELOG；注：工作树尚有 V17.0.26–31 代码注释未入 CHANGELOG，属历史滞后，详见下条"已知残留"）。
- `docs/ARCHITECTURE_THEORY.md` A2/A7「已知偏离」清零（DEBT-003/004/008 均已偿还）。
- `docs/roadmap.md` 顶部新增强制提醒：R1–R3 两套撞车编号 + V17-5/V17-6 前提失效，禁止按字面实现 R2/R3。

**回归：**
- 全仓 grep 消费方确认零遗漏；`py_compile` 通过；`CanonicalStockData` 实例化验证 `pe_more` 已移除、`pe_lyr`  intact。

> **已知残留（待后续 reconciliation，非本次范围）**：代码中存在 `V17.0.26`–`V17.0.31` 注释（含本版 17.0.27/17.0.31），但 CHANGELOG 此前仅至 17.0.24、VERSION 曾为 17.0.12、git HEAD 为 17.0.13（未提交工作树）。本版以 CHANGELOG 为单一权威，VERSION 对齐至 17.0.25；25–31 注释与 CHANGELOG 的完全对齐建议单列一次文档 reconciliation。

---

## [V17.0.24] 2026-09-01 — 源矩阵战略重估：静态 PE(f163) 逐股路径脱离 push2 + 主字典对齐 + 东财遗留函数标注

**用户指令落地（源矩阵战略重估，核心原则"尽量避免 push 源以免封 IP"）：**

### ① 关 f163 逐股路径缺口（静态 PE 完全脱离 push2）
- `stock_common/sc_datasource.py` `get_tencent_quote`（单股，供 sht/lng/med）补返回 `pe_lyr = vals[_f["pe_static"]]`（腾讯[53]=f163=静态LYR，主字典§12.8.12e L1）；并加入 normalize 透传白名单。
- `core/data_provider.py` 腾讯补取循环（L510）加 `"pe_lyr"`，使逐股路径静态 PE 来自腾讯而非 push2 `get_em_quote_full`。
- 修正 `get_tencent_quote` 过时注释"腾讯无独立静态PE字段"（实为 2026-09-01 订正前的滞后认知；腾讯[53]=f163 已 L1）。
- 批量路径此前已由 `tdx_client.py` `_tencent_batch_fallback`(V17.0.23) 接入 → **现 val/mak/sht/lng/med 全路径静态 PE 均走腾讯[53]，零 push2 主域依赖**。
- 仍走 push2delay（东财安全域）的独有数据仅剩：资金流 f137(主力净, 无同口径 TCP/HTTP 替代) + CYQ 换手率 f61(TDX/腾讯K线均无换手率)。

### ② 主字典对齐
- `docs/field_dict.md` §12.15.5 估值行补"静态PE(f163)=腾讯[53] L1（V17.0.23 批量接入, 逐股 get_tencent_quote 同步）——彻底脱离 push2"，与 §12.8.12e 一致（消除"push2delay 是 f163 来源"旧表述）。

### ③ 东财遗留函数标注（dead-code, 未接入 5 脚本活跃路径）
- `get_board_fund_flow` / `get_eastmoney_minute_fund_flow` / `get_fund_flow_weighted` 三函数经全仓 grep 确认**仅 def/export、无活跃调用**（mak 板块分析走 KPL+ZHB, 主力净额走 push2delay f137/thsdk）→ 加 ⚠️ 遗留注记，提示勿在批量管线新增调用以免触发东财连接级风控。逻辑未改。

### ④ 采集脚本更新（scripts/capture_field_probe.py）+ 20260901 全源采集
- **新增 3 个采集器**：`em_kline_f61`（东财日K f61 换手率——CYQ 唯一源，🔴实测 push2his 域才有全窗口，push2delay/push2 kline 均 dktotal=0）、`em_fund_flow`（资金流四档 f135-f149，push2delay 域）、`collect_fuyao` 补三大报表采集（income/balance/cashflow×8期 + annual——f163 闭环/TTM 重建原始锚）。
- **防封加固**：`collect_push2` 补域级熔断（首败即停）；`em_kline_f61` 3 连败熔断。
- **采集结果（20260901，19/22 源成功）**：腾讯/TDX/ZHB/fuyao(含三大报表)/sina/axdata/datacenter/cninfo/reports/ulist239 全 20/20；push2 主域 1/20（熔断记录）；em_kline_f61 因 push2 家族连接级风控期 0/20（熔断保护生效，20h 冷却后补采）；ftshare 会话失败；thsdk 盘后关闸（正常）。
- **闭环实锤**：腾讯[53] vs push2delay f163 **20/20 精确命中**——静态PE 双源一致，f163→腾讯[53] 替代完全成立；f137=f140+f143 加性成立；fuyao 中报指标 20/20 入库。

### 验证
- py_compile 通过；定向回归 routing+reports 通过；全量回归 457 passed / 45 deselected / 0 failed（EXIT=0）零回归。

**用户指令落地（稳扎稳打）：核查统一层 → 同步缓存层 → 据主字典用分析师视角判断 5 大脚本字段增补 → 迭代修订脚本逻辑。**

### ① 统一层 pe_lyr 透传闭环（静态 PE / f163 / LYR）
- `sc_schema.py` `CanonicalStockData` 估值类加 `pe_lyr: float = 0.0`（f163 静态 LYR）。
- `core/data_provider.py` 组装加 `pe_lyr = _safe_float(rt_quote.get('pe_lyr') or em_quote_raw.get('pe_lyr') or 0)` + `field_sources` 标注（缺失→`missing` 不伪造）。
- 背景：前轮统一层 PE 映射订正（f162=动态/f163=静态/f164=TTM）后，f163 只进统一层内部 dict 未透传到 `CanonicalStockData` → 静态 PE 不被下游消费。本次闭合。
- `core/tdx_client.py` `_tencent_batch_fallback` 补 `pe_lyr` 映射（腾讯 `[53]=pe_static`→`pe_lyr`，与主字典定案一致）。

### ② 三口径 PE 露出（5 大脚本，分析师基本功）
- **SHT**：`PE(TTM) | PE(动) | PE(静/LYR) | PB` 四口径齐全。
- **MED**：原标签"动态市盈率 PE(TTM)"（TTM 误标动态）拆正为 `PE(TTM) | 动态PE | 静态PE(LYR) | PB`；新增静态 PE 露出。
- **LNG**：修严重旧错——原 `_pe_static` 变量赋 `pe_dynamic`(动态)**当静态展示**，且从不使用真正 f163；静态改用 `cdata.pe_lyr`，动态/静态分开展示。
- VAL/MAK 不动（VAL 用 pe_ttm 过滤正确；MAK 板块扫描不需要 PE）。

### ③ 同业对比表静态 PE 列（横向比较口径闭合）
- `get_industry_peers` 三路径全透传 `pe_lyr`：东财 L2 主路径（`_q.get("pe_lyr")`）、腾讯兜底（`_q.get("pe_lyr")`）、F10 fallback（`pe_lyr=0` 无静态口径）。
- SHT 同业表加 `PE(静)` 列（本股 `cdata.pe_lyr` 与同业 `pe_lyr` 同源）；LNG 板块横向对比加本股 `PE(静)`。
- ZHB 无静态 PE 字段（[3]=动态/[9]=TTM），故盘后/休市仅 ZHB 兜底时 pe_lyr=0 → 展示 N/A（缺失不伪造）。

### ④ PE(MorePE) 交叉验证（分析师视角增补）
- MED/LNG 估值块加 `PE(MorePE, 东财官方滚动 f164)` 一行，与 `PE(TTM)` 交叉验证（同源 f164 但计算口径略有差异，偏差大→提示核查）。
- SHT/VAL/MAK 不加（避免信息过载）。`pe_more` 已在 `CanonicalStockData`（f164 MorePE 口径）透传，此前未消费。

### 缓存层
- `sc_kline_cache.py` / `sc_capital_cache.py` 经核查与 PE 无关，**零改动**（正确结论，不为改而改）。

### 回归
- `py_compile` 全过；定向回归 schema+routing 45 passed / reports 89 passed；**全量 457 passed / 45 deselected / 0 failed（EXIT=0）**，零回归。
- 备份：`docs/backups/unified_layer_pe_lyr_20260901_2120/`（统一层 sc_schema+data_provider）。

---

## [V17.0.22] 2026-09-01 — fuyao 黄金锚 × 5 源 × 多日对撞（主字典实证化）

> 用户要求："现在有了 fuyao 源的黄金锚，重新按历来采集数据和 zhb 连续数据，用 fuyao 字段对撞核实及破解其他未知字段。主字典是本项目最核心的部分，不容有差错。"
> 引擎：`scratch/collide_fuyao_anchor_v2.py` / `collide_ratio_unit.py` / `crack_tx_slots.py`
> 数据：6 采集日（0824/0825/0826/0827/0828/0831）× 20 股 × 5 源（push2_full / tencent / sina / tdx / zhb）

### ★ 两处方法论级修正（已回写 `CRACKING_METHODOLOGY.md`）
1. **精度对齐对撞**（原 1e-9 导致 24 个财务锚仅命中 1 个，假阴性 96%）：push2 财务字段是 10~12 位全精度（`f186=89.5552128279`），fuyao 锚仅 4~6 位小数（`89.5552`）。字典长期把 f186 记作 `89.56`（显示值）。改用 `|a−b| ≤ max(5e-5, |a|·5e-6)` 后命中 6/24。
2. **命中率分层**：≥18/20 且 miss 可解释 → L1 定案；8~17/20 → 存疑不定案。修正前把 tx[9] 买一价（16/20）、tx[19] 卖一价（11/20）误判为"现价"（盘后自然巧合），分层后正确剔除。
3. **新增工具：比值族（单位换算定案 L1-U）** —— CV<1e-4 且比值∈{100,1e3,1e4…} 且 ≥18/20 且 ≥3 日。
4. **新增规则：财务锚独立性来自报告期切换**（非采集日数），要求 ≥3 日且跨 ≥2 报告期。

### 新增 L1 定案（fuyao 官方锚实锤，6 日 × 20/20）
- **腾讯位置槽**：`tx[6]`/`tx[36]`=成交量（688 段=股、其余=手，5/5 科创板逐股点名）；`tx[37]`=成交额（万元·取整）；`tx[44]`=流通市值（亿元）；`tx[45]`=总市值（亿元）；`tx[46]`=PB（价÷f92 BPS）；`tx[47]`=**涨停价**（按板块幅度 主板10%/创业板·科创板20%/北交所30%）；`tx[57]`=成交额（万元·4 位小数）。
- **push2**：`f47`=成交量(手)（比值 100.0000）、`f48`=成交额(元)（比值 1.000000）、`f117`=流通市值、`f116`=总市值（全流通股 8/20 结构性重合，非巧合）。
- **财务**：`f173`=加权ROE、`f184`=营业总收入同比、**`f185`=归母净利润同比（新破解）**、`f186`=毛利率、`f187`=净利率、`f188`=资产负债率（均跨 2 报告期）。
- **新浪/通达信**：`sina[8]`=成交量(股)、`sina[9]`=成交额(元)、`tdx.quote_full.*` 七字段。

### 🔴 关键订正与发现
- **`tx[37]` 单位订正**：旧注"元"**有误**，实为**万元且取整**（茅台 477921 应读作 477921 万元 ≈ 47.79 亿元）。
- **`f184` 口径分叉（铁证块）**：fuyao `calculate_operating_income_yoy_growth_ratio`=**营业收入**同比（1.469869%，由官方利润表反算 6 位小数验证），push2 `f184`=**营业总收入**同比（1.3001%）。19/20 逐股精确相等，唯一 miss=600519（含财务公司利息收入）。旁证：f104 营业总收入 TTM 1732.38亿 vs 营业收入 1701.52亿（差 1.8%）同源互锁。**二者不可混用、不可互相兜底。**
- **命名陷阱**：fuyao `snapshot.turnover` 字面"换手率"，**实测=成交额(元)**。任何按字面理解的代码均为 bug。
- **字典键名订正（§12.8.12f）**：4 个键名实测不存在（`net_profit_yoy_growth_ratio` 等）、3 个实测键遗漏（`calculate_operating_income_yoy_growth_ratio` / `calculate_operating_profit_yoy_growth_ratio` / `fixed_asset_invest_expansion_ratio`）。**实测总数=24**（旧记 19、他处 25 均误）。
- **负面证据**：24 个 fuyao 财务指标中 **18 个对 push2 精确命中 0/20** → 判定 push2 无对应维度、无法兜底，接入优先级 偿债(5) > 营运(4) > 现金流质量(4) > 成长补充(4)。

### 文档
- 新增 `docs/field_dict.md` §12.8.12g「fuyao 黄金锚 × 5 源 × 多日 对撞总表」。
- 生成 `docs/field_verification/20260831/fuyao_anchor_multiday_collide.md`（256 行）。
- 残留未知维持原判：腾讯 `[56]`(L4) / `[85]`(L3弱) / `[86]`(❓)，push2 `f103/f108/f160/f190/f193~f197/f199`。

## [V17.0.21] 2026-09-01 — 规范字段注册表 + fuyao 字段完整度收口（回应"同值异名"风险）

**用户策略落地：统一跨源语义命名、消除以源私有别名当语义名导致的字典分裂（PE 标签翻车即前车之鉴）。**

### (a) f190↔fuyao 锚点补全 + L2528/L2543 误导标注修正
- `f190`=每股未分配利润(per-share) 非 push 独有：`push2 f190 ≡ fuyao balance_sheets.undistributed_profit(未分配利润总额) ÷ 总股本(f84)` 可推导，fuyao 有 total 版。
- 修正 L2528 / L2543「eps_deduct_ttm/undist_profit_ps 仍 push 独有」：**仅 `f108`(扣非EPS TTM) 真 push2 独有**（fuyao 仅 `basic_eps` 无扣非EPS）；`f190` 可推导。
- 财务 TTM 族表（L2504）补 `eps_deduct_ttm(f108)` / `undist_profit_ps(f190)` 两行。

### (b) 新增 §12.8.12e 规范字段注册表（canonical registry）
- 一行一概念，列 = 规范名(带口径 qualifier MRQ/TTM/LYR/最新报告期/扣非/per-share/total) | 语义 | push2 fN | 腾讯[idx] | ZHB Col[n] | fuyao 官方字段 | 状态/置信。
- 覆盖估值五指标 / ROE·扣非ROE·ROA / 财务TTM族 / eps_basic_period·eps_deduct_ttm·undist_profit_ps / 竞价量 / 涨停封单 / 行情。
- 铁律：PE 标签/ROE 口径/EPS 报告期类描述必须引用本表规范名+口径，禁用 `f162=动态` 等源私有别名。

### (c) 新增 §12.8.12f fuyao 财务指标 index_id 完整度与接入分类
- 枚举 fin_indicators 全 ~24–25 个 index_id（成长4/盈利5/偿债5/营运5/现金流5 + 契约未列 `calculate_parent_holder_net_profit_yoy_growth_ratio`）；**无"未知空白"**（全在 fuyao_api_full.md 可溯，适配器 0 丢弃）。
- 分类：3 个已接入（ROE/扣非ROE/ROA 锚）+ 5 个与 push2 f183–f188 同义可作跨源验证锚（毛利率f186/净利率f187/营收增速f184/净利增速f185/资产负债率f188）+ ~16–17 个为 push2 无对应新维度（偿债/营运/现金流质量，优先级最高）。
- 注记字典 L2441 旧写"19 个"为过时数，待统一。

---

## [V17.0.20] 2026-08-31 — fuyao 官方字段 × 东财 push2 财务/估值 fN 三方对撞 + 36/38 映射表复核

**同花顺 fuyao 官方 REST 契约（pe_mrq/pe_ttm/pb_mrq/ps_ttm/pcf_ttm/index_weighted_avg_roe + 三大报表 act_cash_flow_net/basic_eps）作第三方独立锚，对撞东财 push2 残留/已定案 fN，并三方复核 36/38 映射表。**

### 对撞实锤（20 股横截面，rel_tol≤1e-4 视作精确实锤）
- **估值五指标**：f162=市盈率(静态/MRQ) ↔ fuyao `pe_mrq`（比值 1.0000±2e-4）；f164=PE(TTM) ↔ fuyao `pe_ttm`（1.0000±2e-4）；f165=市销率(TTM)、f166=市现率(TTM)、f167=PB 同值定案。
- **f173=最新报告期加权 ROE** ↔ fuyao `index_weighted_avg_roe`（19/20 精确相等，比值恒 1.0）。
- **f103=经营活动现金流量净额(TTM)** ↔ fuyao `act_cash_flow_net` 季度表 TTM 重建（20/20 比值 1.0000，含茅台 1190.94 亿），强化 V17.0.7 原定案（本次初稿曾因 TTM 重建公式 bug 误判"反驳"，已纠正）。
- **f160=基本每股收益(年报/LYR)** ↔ fuyao `basic_eps`(年度)（17/20 落 [0.9,1.1]，原未破解→升级）。
- **f108**（EPS 变体/扣非 TTM）、**f190**（每股未分配利润）、**f199**（恒=90 常量）维持 V17.0.7 语义；fuyao 仅暴露 `basic_eps` 无扣非字段 → 不可第三方区分 f108 子口径（源覆盖限制，非破解失败）。

### ⚠️ PE 标签重大订正（fuyao 第三方推翻旧标注）
- **旧错**：字典曾标 `f162=动态PE`、`f163=静态PE`、`[52]=动`、`[53]=静`、`fuyao 原误判 f163=TTM`。
- **正解**（fuyao 精确实锤）：**f162=静态/MRQ**、**f163=动态PE（剩余类，fuyao 无官方对应字段，由腾讯[53]反推）**、**f164=TTM**；腾讯 `[39]=f164(TTM)`、`[52]=f162(静态)`、`[53]=f163(动态)`。
- 根因：同花顺 `DynaPE`/TDX `f9/f114` "动态/静态" 命名系**已知命名坑**（与 L461 TDX PE 命名颠倒同源）；其数值=f162，但"动态"标签误导。旧"f162=动态PE=15.55（价/Q1年化EPS=87.16）"推算基数有误（茅台 Q1 年化≈71），15.55 非动态真值。

### 字典一致性清理（本次落盘）
- 订正 L1503/L1534（ulist f114=动态、f9=静态/MRQ，推翻 V17.0.15 误订"f114=静态"）、L2683/L2689（V17.0 中报终核 PE 标签）、L428/L462（ZHB Col[3] 注记"f162=DynaPE=真动态PE"→ 实为静态/MRQ，真动态PE=f163）、L1546/L1547/L1548/L1736/L2847/L2849（碰撞表/映射表 fN 对应）、L1312/L1313（腾讯[52]/[53]）。
- 36/38 映射表（push2/ulist239 ↔ 腾讯[0]–[87]）跨三源（东财↔腾讯↔fuyao）复核通过。

### 产物
- 报告 `docs/field_verification/20260831/fuyao_push2_collide.md`（六节：估值/ROE/三源对齐/残留fN/字典订正/结论）。
- 脚本 `scratch/collide_fuyao_push2.py` / `scratch/probe_pe_labels.py` / `scratch/validate_f103.py`（TTM 重建已修）。

---

## [V17.0.19] 2026-08-31（深夜）— 字段采集脚本修复 + 主字典跨源对撞复测

**运行今日采集脚本并按最新数据对主字典做跨源数值对撞（CRACKING_METHODOLOGY.md）。**

### 采集脚本修复（前置必须）
`scripts/capture_field_probe.py` 工作树两处**未提交回归**致首次采集崩溃：
1. `from datetime import datetime, time` 遮蔽内置 `time` 模块 → `main()` 的 `time.time()` 抛
   `AttributeError`。修正：`from datetime import datetime, time as dt_time`。
2. `datetime.combine(td, datetime.time())` 误调 `datetime.datetime.time` 未绑定方法 → fuyao 采集
   崩 `unbound method datetime.time() needs an argument`。修正：`datetime.combine(td, dt_time())`。
修复后全 **21 源采集成功**（含 fuyao），产出 `docs/field_verification/20260831/`。

### 对撞结果（引擎 scratch/collide_20260831.py，改编自 collide_0829.py）
- **腾讯未知 `[56][85][86]` 跨源精确对撞 0 命中(≥8/20)**：复现 H12（12 日）结论，无新定案亦无误判翻案；
  `[86]` 的 Pearson r=+0.995 经留一法证实为单点伪相关（剔除后→+0.335），守 H12 铁律。
- **push2/ulist239 已知 fN × 腾讯锚点跨源映射表（36/38 字段）回归校验通过**（东财↔腾讯一致性成立）。
- **正向进展**：fuyao 中报(2026-2)全 20 只入库 → `tx65/tx66` 终判 L1 条件达成；跨源对撞
  `tx65≈2×fuyao中报H1扣非ROE`（600519 32.41 vs 16.74），期间差即 TTM vs 中报(H1)，印证 `tx65=TTM 滚动口径`。
- 残留 push2 未知 fN（f103/f108/f160/f190/f199）今日仍无跨源锚点/干净比值 → 维持未破解（f199 恒=90 常量占位）。

### 字典更新
- `[65]` 扣非加权 ROE：**⚠️→✅(L1-) → ✅ L1（2026-08-31 终判）**，附 fuyao 中报跨源对撞注记。
- H12 证据块新增「2026-08-31 复测（独立第 13 个采集日）」段落。

---

## [V17.0.18] 2026-08-31（晚）— 根因续查：CYQ/K线形态章节源空的真因（代码 bug，非纯源故障）

**用户授权运行 `scratch/probe_kline_sources.py` 后定位：CYQ 与 K线形态"全月恒空"是代码层 bug，非环境源故障。**

### 根因（实测，非推测）
1. **CYQ 空：`get_cyq_distribution` 缺 `fqt` 参数**（sc_datasource.py:1255）。东财 `kline/get`
   缺省 `fqt` 时返回 `rc:102, data:null`（对 600519/000001/300750/601318/000858 五只 +
   push2/push2his 双域**全部复现**）。加 `fqt=0`（不复权，成本分布用实际成交价）即恢复
   `rc:0, klines=240`。`get_cyq_distribution('600519')` 现返回真实 `benefit_pct/avg_cost/
   concentration_90/70/source=eastmoney_kline_f61`。**CYQ 此前全月 0 出现的唯一根因。**
2. **K线形态空：`baidu_kline_full` 形参 footgun**（sc_datasource.py:1218）。签名原为
   `(code, is_index=False, count=800)`；调用点 `baidu_kline_full(code, 60)` 把 **60 绑定到
   `is_index`（真值）** 去取**指数**K线，个股返回 `([],[])`（`is_index=False, count=60` 才是取
   个股日K 的意图）。这同时解释了报告里反复出现的"指数K线响应截断"告警——它正来自被误触的
   指数分支。修复前 `baidu_kline_full(code,60)=0 行 / (code,count=60)=60 行` 已实测对照定案。
3. **指数对照信号空：`_index_to_market_code` 误拆原始指数代码**（tdx_client.py:122）。无脑取
   前 2 字符当前缀 → 原始 `000001` 被拆成 `('00','0001')` 返回 `(0,'0001')` 坏码，`index_bars`
   取不到；`get_sht_report.py:1793` 又主动剥离 `sh/sz` 前缀后传入，致异动雷达"指数 3 日偏离"
   信号恒不触发。修复后 `000001/000300/399006/sh000001/sz399006` 均 → 250 行。

### 修复
- **CYQ**：`get_cyq_distribution` params 增 `"fqt": "0"`（不缓存空结果，源恢复即自愈）。
- **K线形态**：`baidu_kline_full` 形参重排为 `(code, count=800, is_index=False)`——位置第 2 参
  即 `count`，与所有调用点"count 位置传参"意图一致；仅 `get_sht` 指数分支用关键字 `is_index=True`。
- **缓存防冻结（防御）**：`@cached(category="kline")` 的 `valid_if` 由 `make_valid_if()` 改为
  `lambda r: isinstance(r,(tuple,list)) and len(r)==2 and len(r[1] or [])>0`——拒绝空 tuple，
  避免瞬断 `([],[])` 被 `trading_day` TTL 冻结整天（原 `make_valid_if()` 只拒空 dict/list/None，
  不拒空 tuple，是"全月恒空"的放大器）。已存在的 stale `[[],[]]` 在读取时 valid_if 失败自动 miss 重拉。
- **TDX 黑盒（防御）**：`tdx_get_security_bars` 的 5 分钟 `_TDX_KLINE_EMPTY_UNTIL` 失败记忆 +
  进程内 `_TDX_KLINE_CACHE` 空写入，**仅限确无 K 线的号段**（北交所 92/老三板 8/4/43/83/87），
  健康股(6/0/3)瞬断不拉黑、不写进程缓存，下次调用重拉（与 V16.2 连接失败路径一致）。
- **指数代码**：`_index_to_market_code` 兼容原始 6 位指数代码（0/9 开头→沪 market=1，3 开头→深 market=0）。

### 测试
- 回归：**457 passed / 45 deselected / 0 failed**（与 V17.0.17 基线一致，无回归）。

---

## [V17.0.17] 2026-08-31 — 修复「CYQ / K线形态」章节源空时静默消失（重演假空白章节反模式）

**🔧 sht 报告 `get_sht_report.py`：源抓取失败不再整章静默跳过，改为渲染可见告警占位。**

### 问题（2026-08-31 QA 核查发现）
- 8 月全量 360 份 sht 报告中，`十三·五 筹码分布（CYQ）` 与 `十六·五 K线形态识别（TA-Lib）`
  **0 出现** —— 自 V17.0.14/15 接入以来从未成功渲染。
- 根因两层：① 数据源失败——CYQ 走东财 push2his `kline/get`（返回 `{}`），K线走远程 TDX
  `client.bars`（返回 `([],[])`，日志「指数K线响应截断/数据不足」）；② **代码缺陷**——门控
  `if _cyq_dict:`（L1231）/ `if len(_sr)>=3`（L1870）在无数据时**整章静默跳过**，无占位无告警，
  重演 V17.0 已治理的 M1/M4「假空白章节 / 假成功」反模式。
- 附带发现更深 bug：`_sk/_sr` 仅在涨停块（L1836）内赋值，非涨停股触发 `NameError` 被
  `except` 吞掉 → K线形态章节对非涨停股恒不渲染（与源健康无关）。

### 修复
- **CYQ 章**（L1230）：标题恒渲染；源空时输出 `⚠️ 东财 K线/CYQ 数据源暂不可用…本章成本集中度数据暂缺`。
- **K线形态章**（L1861）：① 预初始化 `_sk,_sr=[]`（L1811 前）供本章复用，修非涨停股 NameError；
  ② 标题恒渲染；源空/数据不足时输出 `⚠️ K线数据源暂不可用…本章形态识别数据暂缺`；
  ③ 有数据但无形态时显式标注「无显著看涨/看跌形态信号」，章节稳定存在。
- 空结果不写缓存（原行为）→ 源恢复后下次抓取即得，无需清缓存。

### 测试
- 新增 `tests/reports/test_reports_chapter_omission.py`（2 例）：源故障配置下断言两章标题 + 告警
  占位仍出现（不再静默消失）；源正常时断言 CYQ 输出真实获利盘比例、不出现告警。
- 回归：**457 passed / 45 deselected / 0 failed**（基线 455，+2 新测试）。

### 附带
- `scratch/probe_kline_sources.py`：真实环境连通性探测脚本，定位 TDX 远端 / 东财 push2his
  端点不可达根因（区分源故障 vs 临时限流）。

## [H12] 2026-08-31 — 字典治理·未知字段跨源跨日期对撞破解（无功能变更，仅字典/实证层）

**🔓 腾讯 qt 未知字段 + ZHB tipinfo 列 跨源×跨日期对撞破解，结论落盘 `docs/field_dict.md` §12.1 / §3 与 `docs/verify/tencent_verify.md`**

### ✅ 腾讯 qt 字段定案（12 采集日 × 20 股 + 0812 38 股，共 237 股·日；全部脚本已重跑实证）
- `[0]` ⬆️ **L1 市场标识定案**（1=沪/51=深/62=京）：分组一致性 237/237=100%，规避编码巧合陷阱
- `[40]` ⬆️ **L3 停牌标记（`'S'`）**：233/233 零误报（603221 停牌期 0814-0815 现 'S'）
- `[76]` ⬆️ **L1 A股流通股本**（订正旧错标"总股本冗余"）：`[76]==push2 f85` 237/237=100%，歧义样本 142/142 跟流通股本
- `[87]` ⬆️ **L3 科创板/两融标记**（688段值='100'）：非空仅 5 代码且全 688（688327/426/500/553/589），值恒='100'
- `[29][54][55][77][78][81]` ⬇️ **占位符·恒空（无信息量）**：237/237 全空
- `[83]` ⬇️ **占位符·恒 '0'**：唯一值=1、237/237 恒 '0'
- `[56]` ⚠️ **L4 维持**（Beta 族同口径未定）：相关性达标但对撞 0/215、恒定正偏移 +0.34~+0.38
- `[85]` ⚠️ **L3 弱·价格类字段**：落本日[低,高]区间仅 76.6%，与[51]均价/MA/VWAP/昨收全部证伪（非当日价/均价/MA/参考价）
- `[86]` ❓ **维持·手级带符号量语义未破解**：517 候选全锚定精确命中 0、无 >0.6 Spearman

### ⚠️ ZHB tipinfo 列（H12 重测撤回一处过度定案）
- `Col[7]`：原 2026-08-29「价格异动标记日」与 H12 初判「停牌起始日」**两假设均未达 L1**；全量重测停牌起始日**正向仅 13/153=8.5%**（137 只停牌股 Col[7]空）→ **撤回"停牌起始日 定案"**，统一记为「最近一次重大事件/异动日（未定案）」
- `Col[21]` ⬆️ **L3 候选·持股变动类最近事件日**：1473/5630=26.2% 非空，板块倍率 688=2.06×/创业板=1.50×（解禁·增减持富集），维持 ⚠️

### 🐞 踩坑沉淀（H12）
- 同优先级假设须用**双向+全量**验证，勿用选择偏差（仅数非空命中）得"全中"——Col[7] 初判"15/15 全中"即仅统计非空子集
- 价格族混杂（跨股票价格量级差 13~1500 让价格字段互相关≈1.0）→ 改个股内比值判定
- 编码巧合（[0] 沪市"1"伪装对撞）→ 分组一致性验证；簇合并传递性错误（f84/f85 并查集合并）→ 歧义消除样本逐股验证

## [Unreleased] - 2026-08-30

**🧹 文档与测试规范校正 + 🧪 补齐报告层测试空白（无功能变更；回归 277 → 311 → 353 passed / 45 deselected / 0 failed）**

### 🧪 新增 `tests/reports/` 报告层（**76 例** — 填补长期空白）

> 分两批同日落地：① 骨架与注册表 34 例；② 五个 Runner 装配 42 例。合计覆盖
> `ReportRunner` 基类、批量流水线、25 策略注册表，以及 5 个报告脚本的取数装配。

- **背景**：`tests/reports/` 历史上一度规划（`test_report_runner.py` / `test_report_strategy.py`）但**从未落地**，
  `ReportRunner` 基类与 val 的 25 个策略长期零专属测试（`docs/roadmap.md` V17-1 / V17-15 均记录此缺口）
- **`test_reports_runner.py`（22 例）**：`BaseReportRunner` 契约 + `execute_batch_pipeline` 五大骨架能力——
  代码清洗（含中文粘连）、**并发上限 3**（`asyncio.Semaphore(3)`）、**单股失败隔离**、prefetch 双钩子异常容错、
  快照落盘；外加 GD 上传编排（跳过失败项 / name_resolver / 失败状态标记 / `args=None` 路径兜底）
- **`test_reports_strategy.py`（12 例）**：val **25 策略 ↔ 调度表 `_strategy_defs` 双向一致**
  （漏登记或引用不存在函数都会静默出问题，此处拦住）、**空股票池不崩**（休市日真实场景）、
  **策略读取的配置键必须真实存在**（键名笔误会静默走默认值，悄悄改掉回测口径）
- **有效性验证**：变异测试注入「调度表漏登记策略25」「并发上限 3→99」「单股失败不再隔离」三处回归，
  均被对应用例捕获（脚本 `.tmp_audit/mutation_check.py`，已清理）

### 🧪 `tests/reports/test_reports_pipeline.py`（新增 42 例 — 五个 Runner 装配）

- **背景**：上一批只覆盖了基类骨架，`sht/med/lng/val/mak` 各自 `execute_pipeline`
  **如何取数、如何组装章节**长期零测试——改报告脚本的取数逻辑无任何回归保护
- **`_BatchMixin`（sht / med / lng，34 例）**：
  - 公共契约：返回 `PipelineResult` / `report_type` 与脚本一致 / 生成器绑定到本模块的
    `generate_report_async` / 快照代理透传
  - **上游调用次数钉死**（`CACHE_PATCHES` 四元组）：sht = `get_industry_comparison` 1 次、
    `_get_index_quote` **4 次**（四个指数各一次，早期曾误写成 1 次而假红）、
    `get_hsgt_macro_flow` 1 次；med / lng 各 1 次
  - 行业对比结果必须注入 `gen_kwargs`
  - sht 专项：四指数行情（`sh000001 / sz399106 / sz399102 / sh000688`）全收集、
    单指数失败跳过不中断、prefetch 双钩子（同步→行情批量 / 异步→数据中心）委派正确、
    `depth` 三态（`deep` 开席位 / `lite` 关席位 / 未指定默认 `deep`）
- **`_SingleFileMixin`（val / mak，8 例）**：输出路径与 `report_ts` 注入、
  async→sync 回退、**V16.3 O39 守卫**（异步"成功"但产物文件不存在 → 必须判失败，
  防假成功）、`mak` 无 sync 回退必须抛错（`asyncio.run` 恰好调一次）
- **踩坑**：mock `asyncio.run` 永不执行协程 → `RuntimeWarning: coroutine was never awaited`；
  统一用 `_closing_run()` 替身先 `coro.close()` 再返回/抛错（见 §6 踩坑）
- **有效性验证**：变异测试注入「sht 少取一个指数」「val 删掉 sync 回退」
  「val 去掉 O39 文件存在性校验」「mak 静默吞异常」四处回归，**4/4 全被捕获**
- **回归**：311 → **353 passed** / 45 deselected / 0 failed（42 新增，零回归）
- ⚠️ **仍剩余**：**报告正文渲染结果**（生成的 md 章节内容/措辞/数据呈现）仍无覆盖（需大量数据层打桩）

### 测试命名归位

- `tests/core/test_tencent_volume_unit.py` → **`tests/core/test_core_tencent_volume_unit.py`**
  （补 `core_` 层前缀，符合 `test_<层>_<主题>.py` 规约；`git mv` 保留重命名历史）
- 同步更新引用：README、docs/PROJECT_CONTEXT.md、docs/V17.0_REFACTOR_PLAN.md、docs/field_dict.md、
  docs/field_verification/20260829/analysis.md、docs/field_verification/CRACKING_METHODOLOGY.md、tests/README.md
- ⚠️ 下方 `[17.0.12]` 条目中的**旧文件名系当时真实记录，按项目惯例保留不回改**；查最新路径见本条

### 字段字典唯一化

- **删除** `docs/field_dict_gemini.md`（3740 行，本字典的归档分支副本：2026-08-25 前快照、缺 §12.20/§12.21、
  无任何代码引用）——用户确认属 Gemini 会话遗留，**以 `docs/field_dict.md` 为唯一权威**

### 过时/误导性文档修正

- `AGENTS.md` §8.2：`REQUIRES_REALTIME_HTTP` / `ZHB_SUFFICIENT` 标注为**测试契约元数据**（业务代码零调用，
  删除会破坏 `tests/core/test_core_routing.py` 14 例），并列出**真正生效的三处路由机制**
- `core/data_provider.py` V12.6 决策注释：标注为**设计意图而非当前行为**
- 破解思路数：PROJECT_CONTEXT / field_dict「六大·七大思路」→ **八大思路**（与 CRACKING_METHODOLOGY 现文对齐）
- 回归基线：统一以 **277** 为准，并在 PROJECT_CONTEXT / V17.0_REFACTOR_PLAN 补 `302 → 269 → 277` 演进说明
  （历史数值保留，防止误判"丢了 25 个测试"）
  —— **同日后续**：再 +42 报告层装配 → **353**，`302 → 269 → 277 → 311 → 353`；
  现判回归一律以 **353** 为准
- `docs/roadmap.md`：V17-1 ✅已吸收（同日补齐装配测试）/ V17-5·V17-6 ❌前提失效；
  新增注记 A（两套 R1-R3 编号对照）、注记 B（`reports/` 测试层落地记录与剩余缺口，V17-15 视为基本完成）

### 🔧 `docs/` 目录误删与回收站整体恢复（事故记录）

- **事故**：清理 `field_dict_gemini.md` 时误删整个 `docs/` 目录（09:47），281 个文件入回收站
- **误判**：首版恢复脚本只处理**文件级**回收站记录（262 条），漏掉**目录级**记录（10 条），
  据此错误得出"16 个文件被永久删除"，并用 `git checkout` 从 HEAD 恢复——
  **导致未提交编辑丢失**
- **根因**：Windows 删除目录树时回收站**不会只建一条记录**，而是**按子目录拆分成多条**
  （`docs\` 记录本身只含其直属的 11 个文件）
- **恢复（用户方案，4 步）**：`docs` → 改名 `docs_OLD_20260830`（同分区瞬时）→
  从回收站**整体**恢复 `docs` → 逐文件校验完全 → 删除备份。
  结果 **281 → 300 文件，0 丢失**
- 🔑 **事后核查**：`docs/` 磁盘 300 文件中 **git 仅跟踪 58 个**——
  `.gitignore:43` 忽略 `docs/field_verification/*/raw_*.json` 与 `meta.json`，
  13 个采集日共 **240 个** `raw_*.json`/`meta.json` + `verification_reports_20260828.md`
  **从未入库**。**回收站一旦清空，这 242 个文件（80%）git 一个都救不回来**
  → 教训：本项目 `.gitignore` 排除面很大，**回收站/备份就是唯一的原始数据保险**
- **合并策略**：回收站版本 = 09:47 真实快照（含本日全部文档修正），以它为底；
  删除后的增量（353 基线、reports 层说明、归档注记、测试文件名同步）再补回。
  残留 5 处措辞差异均属"回收站版更详尽"，保留回收站版

### 🛠️ 代码审查问题整改（源自 `docs/code_review_20260830.md`：**S1–S6 / M1–M17 / 死代码 M18 全量落地**）

> 依据 `docs/code_review_20260830.md` 逐条对照修复；**回归基线 350 → 353 passed / 45 deselected / 0 failed 已恢复**（353 即修复后基线）。
> 整改全程未删任何被测试引用的符号（`_market_from_code` / `get_stock_concepts` / `sc_schema` 测试契约函数等）；`get_fund_flow_weighted` 因被 `__init__.py` 再导出，改为 deprecated stub 而非删除。

#### 严重级（数值正确性 / 数据安全）
- **S1 大盘股市值低估 ~10000×**：`sc_capital_cache._norm` 阈值 `1e7 → 1e9` 万股（同步修正 :116 注释 `2e6→2e7`）；正确大盘股万股值不再被误当"股"再 ÷10000。
- **S2 YTD 年初至今涨幅算反**：`data_provider.get_change_ytd` 改用升序 K 线 `rows[-1]`(当日) / `rows[0]`(约年初)，修正"rows 从新到旧"的错误注释（:1668）。
- **S3 连涨连跌方向整体反**：`data_provider.get_streak_days` 改从 `closes[-1]`(最新) 向前遍历，上升段记正、下降段记负（:1968 注释更正）。
- **S4 解禁字段单位自相矛盾**：`get_lockup_expiry` history/upcoming 两分支 `ABLE_FREE_SHARES` 统一按"股"处理（均不除法），删去 upcoming 分支误标的"万股"注释；新增 TODO 标注真实单位待实盘采样一次确认。
- **S5 资金流总额重复计数**：`get_em_fund_flow` 的 `total_net = main_net + small_net + medium_net`（东财"主力 = 大单 + 超大单"，原五档全加把大/超重复计）；更正原"漏大单"误解注释。
- **S6 历史工具 `sync_readme.py`（已于 2026-09-28 清理）误丢版本归档**：当时的 `update_readme` 新增 `dry_run` 参数、写前自动 `.bak` 备份；`main()` 新增 `--force`/`--dry-run`，**默认拒绝运行**（须显式 `--force` 或先 `--dry-run` 预览）——CI 已禁用。该脚本不再是当前工具。

#### 中等级（防护 / 性能 / 接口）
- **M1 编排层假成功**：`sc_report_runner.run()` 的 `execute_pipeline` 异常不再吞掉，记录后 `raise`，使 `main.py` 的 `all_ok` 真实反映失败。
- **M2 事件循环阻塞**：`get_med:642,679` / `get_lng:810` / `get_mak:1699` 四处同步 `baidu_kline_full`(HTTP) 改 `await asyncio.to_thread`（与 sht `:1721` 对齐），`Semaphore(3)` 并发恢复。
- **M3 重复网络调用**：`get_med:1214` / `get_lng:1241` 评分段复用前面已取的 `get_holder_structure`（`:1038`/`:905`），不再重复拉取。
- **M4 O39 守卫收口**：`get_val_report.execute_pipeline` 把文件存在性判定移到 async try/except 之外——文件存在才打印"✅ 已保存"，缺失则打印"⚠️ 报告未生成"且**不误触发同步回退**；仅"异步与同步双路均抛异常"时才 `raise`（守住 `test_async_discovery_is_invoked` / `test_no_false_success_when_file_missing` 锁定契约）。
- **M5 预取非并行**：`execute_batch_pipeline` 的 `prefetch_async_fn` 改 `asyncio.create_task(...)` 与 3 条 worker 真正并行（原 `await` 为串行前置）。
- **M6 快照无校验**：`execute_batch_pipeline` 对 `snapshot_data` 做 `{code:{name,total_score}}` 结构校验，缺 `total_score`/`score` 的坏项跳过保存，非 dict 直接跳过。
- **M7 席位匹配缺陷**：`seat_db.identify_seat_tier` 保留双向子串（反向子句不可删——"拉萨"→"拉萨天团" 锁定回归依赖），新增**最长子串优先**（最具体者胜），等长再按 tiers>aliases>keywords 排序。
- **M8 异步通道熔断失效**：`_async_quick_request` 成功/失败分别调 `_on_success`/`_on_failure`，403 计 `_EM_BAN_STREAK`（达阈值触发 20h 跳过），与同步路径对齐。
- **M9 封禁被静默降级**：`get_em_batch_quotes._fetch_batch` 在宽 `except` 前 `re-raise RateLimitBlockedError`，"IP 被封"不再变空数据。
- **M10 北交所 orgId 错**：`_cninfo_get_orgid` 把 `92x` 北交所落入 `gsbj0`（原 `gssz0` 错主体）；动态查询同时拉 `szse_stock.json` 与 `shse_stock.json`。
- **M11 PE 字段路由**：经项目自有 `field_dict.md` 实证（f162→pe_dynamic=动态PE、f163→pe_ttm=静态PE(TTM)）确认**代码路由本就正确**；仅修正 `field_dict.md:2538/2540` 文档表（原 pe_ttm↔f162 / pe_dynamic↔f163 写反）——属文档误记，非代码 bug。
- **M12 硬编码路径**：`sc_datasource` 三处 `C:\new_tdx64\...`（hy_tree.xml / tdxhy.cfg / vipdoc）改经 `_tdx_root()`，优先读 `TDX_HOME`/`TDX_ROOT` 环境变量，缺省回退 `C:\new_tdx64`。
- **M13 采集市场前缀错**：`capture_field_probe.collect_sina` 市场前缀对齐 `collect_tencent`（`92/8/4/43/83/87` → bj，补 `5`(沪ETF)/`9`(沪B)），消除跨源字段对照污染。
- **M14 回测指标失真**：`backtest_topn.coverage = len(selected_set) / total_universe`（原 `in_topn/top_n` 因候选域已截断恒等于 `selected_count/top_n`）。
- **M15 回测脆弱依赖**：`load_zhb_snapshot` 注入 `stk["code"] = code`（ZHB code 仅作 dict key，原 `s["code"]` KeyError）；新增 `discover_days()` 动态发现 `zhb_*.zip`，去掉硬编码日期依赖。
- **M16 dry-run 死代码**：`upload_reports_to_gd` `--dry-run` 现打印完整待传文件清单后返回，删除两处永不可达的 `if args.dry_run` 分支。
- **M17 清缓存破坏性无确认**：`clean_cache` 新增 `--yes`/`-y`；`clear-all`/`clear-expired` 非交互环境必须 `--yes`，交互环境显式询问确认，否则中止。

#### 死代码 / 轻微级（M18）
- `main.py:337-338` 外层 `except asyncio.TimeoutError: pass` 死分支删除。
- `get_val_report._mcap_count` 市值覆盖率统计**低估**修复：仅当旧值缺/≤0 时才计一次覆盖（`mcap_yi` 已被正确赋值>0 后不再误判恒 False）。
- `core/tdx_client.py:243` `_SH_INDEX_CODES` 零引用常量删除。
- `stock_common/sc_technical.py:479` `if len(vals) else 0` 死分支（numpy 数组 len 恒>0）删除。
- `scripts/fmt_preview.py:49` `... if False else m.group(2)` 死分支删除。
- `stock_common/sc_datasource.get_fund_flow_weighted`（无调用方 + 未算加权融合）改为 deprecated stub 返回 `{"primary_source":"none","sources":{},"deprecated":True}`（保留 `__init__.py` 再导出兼容）。
- `docs/code_review_20260830.md` §三 中**保留项**：`_market_from_code` / `get_stock_concepts` / `sc_schema.FieldSpec` 系列（测试契约死代码，审查意见标注"合规"）；`_tencent_volume_divid` 本模块孤儿但外部应用正确（非 bug）；`_parse_tipinfo` / `normalize_at_boundary` / `sc_fault_tolerance` 半开态等属**需判定或下游耦合**，维持现状不盲改。

### ⚠️ V17.0.13 资金流口径外部核对（2026-08-30，纯文档/注释，无逻辑变更）

- 经上游 easy_tdx issue #55 核实：`get_fund_flow` / `get_history_fund_flow` 基于 `0x0fb5` **逐笔聚合、按成交额分档**，
  与东财/同花顺「主力净流入」**不可比（重合度约 14%）**。
- 本项目 **V12.0 起主力净额已统一走 push2 `f137+f140` / thsdk**，原生 easy_tdx 资金流**未被使用**（`tdx_get_fund_flow` /
  `tdx_get_history_fund_flow` 两个 wrapper 本就转调东财）——本次仅把该口径限制**显式写入文档**，防止日后误接。
- 落点：`docs/field_dict.md` §12.15.5 新增警示块；`sc_datasource.get_history_fund_flow_120d` /
  `get_em_fund_flow` / `get_em_history_fund_flow` 三处 docstring；`core/tdx_client.py` 两个 wrapper docstring。

### 🔗 H9：verify 断链修复 + 附录吸收核查 + 主字典简化方案评估（2026-08-31）

#### 1. 全量断链核查与恢复（零活动断链）

- **唯一真实断链**：主字典 §零·C（line 217）引用 `verify/ths_tableheader_ids.md`，但该文件**从未入库**（git HEAD 无记录、无删除历史；`local_assets.md` 标注的「全量存档」未实际落盘，疑毁于 2026-08-30 docs 误删恢复）。
- **修复**：重建 `docs/verify/ths_tableheader_ids.md` —— 同花顺 tableheader 列 ID **摘录汇编**（汇自主字典 §零·C / local_assets.md / session_notes，收录 682 抽样 + iwc 56 + Fy 81 + marketstatic；头部明确标注「原始 682 全表未入库，此为可用摘录」，不伪造数据）；主字典引用措辞由「全表」改为「列 ID 摘录汇编(部分存档)」。
- **ulist_verify.md 非断链**：仅出现在日期归档 `field_verification/20260813/analysis.md:258`（标注「候选」），实际内容已落地为 `ulist_push2_align.md`（存在、主字典 §12.9.1 引用）。属历史候选注记，非活动导航断链。
- **复验**：活动文档（主字典/README/script_data_dict/verify）共引用 17 个 verify 文件，**全部存在，零断链**。

#### 2. 各附录是否被主字典吸收（量化核查）

- 16→17 个附录，逐一按头部自述 + 量化内联吸收率评估。**结论：无一被主字典完全吸收/冗余**，均为设计的两层互补「实证层」。
- **全表型（绝不应内联）**：`em_indicators` 939 指标代码主字典内联 **0.1%**、`tdx_func_fields` 1924 官方字段 **0.0%**、`tdxhy_x_names` 470 X 码 **6.7%** —— 主字典仅指向附录，不内联批量原始数据。
- **字段语义型**：`tencent_verify`/`push2_verify`/`ulist_push2_align` 主字典引用其关键字段 ~100%，但**原始 24 股样本矩阵、逐字段证据 dump 仍只在附录**（主字典只留结论 + V17.0.16 订正叙事）。

#### 3. 主字典简化方案评估（采纳导航强化变体，否决字面搬迁）

- **否决**「主字典只留未知字段 + 已验证字段下沉 verify 并标引用」的字面方案：主字典是**决策层★唯一权威**，script_data_dict 索引其章节、5 大脚本据此定位；剥离已验证字段会破坏决策层 + 跨脚本索引 + V17.0.16 四档订正叙事，且迫使 AI 每次在 17 个附录里翻找已知字段，更慢更易错。
- **采纳**用户底层目标（"让 AI 学会找 verify 分字典"）的正确机制——**导航强化（零风险）**：
  ① 补全主字典 §12.15.9 附录索引 **9→17**（补 em_indicators/em_tableheader_ids/tdx_func_fields/tdx_headers_definition/tdxhy_x_names/ftshare_fields_mirror/ulist_push2_align/ths_tableheader_ids）；
  ② 主字典顶部新增「🔎 AI 破解字段导航」约定（按源→分字典映射）；
  ③ README 目录树补齐 17 个附录 + 使用原则表加「破解未知字段→查 §12.15.9 分字典」行。

### 🔎 H10：主字典逐章冗余段落筛查（2026-08-31，零编辑）

承接 H9「简化方案评估」用户提议的"继续主字典逐章冗余段落筛查"。

#### 筛查口径
主字典某段落把某 verify 附录的**原始全表/样本数据原样重述**且**未新增**独立结论/V17.0.16 订正/铁证等级/优先级/跨源对撞 → 才判为"纯双重列举"可瘦身为链接；含决策价值者一律保留。

#### 方法
脚本提取主字典全部 ##/### 章节，统计每章表格规模 + verify 链接关联，定位 7 个"正文详列且恰有附录覆盖"的候选章节，逐章读取比对附录。

#### 候选章节性质判定（全部为权威决策层，非冗余）
| 章节 | 表格行 | 对应附录 | 判定 |
|---|---|---|---|
| §12.1 腾讯 88 字段 | 77 | tencent_verify | **保留**：每行含核实状态/验证依据/V17.0.7 订正/跨源对撞(≡push2 f122)/688 单位陷阱——决策层字段字典，脚本经 script_data_dict 依赖 |
| §12.3 东财 push2 字段 | 133 | push2_verify | **保留**：含核实状态/多日复核定案/L1 铁证/歧义消除/V17.0.11 破解——决策层 |
| §12.9 push2 实测新字段 | 67 | push2_verify | **保留**：破解结论+订正——决策层 |
| §12.10 levistock | 115 | levistock_field_verify | **保留**：来源/价值/实测结论/参数含义——决策层 |
| §12.20 FTShare | 38 | ftshare_fields_mirror | **保留**：来源/规模/性质判定/增量盘点/查重结论——决策层 |
| §零·C 三客户端官方 ID 体系 | 抽样 | em/ths/tdx 附录×5 | **保留（边界）**：仅列 ID 系统结构抽样(A=行情/B=盘口…)，展示分类法有决策价值；全表在附录(H9 量化内联率 0-7%) |
| §12.14/§12.19 | 0 表 | axdata_verify/samples_verify | **保留**：本身即"一句话+链接"指针，无内联 |

#### 结论
- **主字典无"纯双重列举"冗余段落**。5 个匹配附录的大表章节均为权威决策层字段字典(核实状态/验证依据/订正/铁证/跨源对撞)，与附录原始样本 dump 是互补双层(H8/H9 架构已最优)。
- 唯一边界项 §零·C 仅列 ID 分类抽样(非全表)，且承载"ID 系统结构"决策价值，**建议保留**。
- **本轮零编辑**：未做任何瘦身删改（避免破坏决策层★唯一权威 + script_data_dict 索引 + V17.0.16 四档订正叙事，印证 H9 否决字面搬迁的判断）。
- 活动文档 17 个 verify 链接复验全部有效。

### 🔗 H11：verify 指针全覆盖 + 破解新字段→同步分字典 强制机制（2026-08-31）

承接 H9/H10：H9 已证 17 个附录无一被主字典完全吸收且零断链；H10 证主字典无冗余可删。
本轮落实用户指令「补全覆盖，并且建立机制，每当主字典破解了新字段，需要同步更新分字典」。

#### 动作 1 — 补全覆盖指针（主字典各"大字段表"章头显式指向实证层）
原指针分布不均匀：§12.3(push2 主字典)与 §12.13.7(服务器)章头**缺**指向其附录的指针（push2_verify/network_servers 仅在其后子节被引）；ZHB §1/§2/§3 无分字典须显式声明。本轮补齐：
- `### 12.3 东财 push2 字段字典` 章头新增 `> 📋 原始实证见附录：docs/verify/push2_verify.md`。
- `#### 12.13.7 服务器统计资源` 章头新增 `> 📋 原始实证见附录：docs/verify/network_servers.md`。
- `### 1/2/3` (tdxstat/tdxstat2/tipinfo) 章头新增 `> 📋 ZHB 无专属 verify 分字典——本 § 即全字段权威表…` 声明（原始在 zhb_*.zip + docs/field_verification/20260812/field_analysis.md；破解直接登记本表，无需同步分字典）。
- 其余 15 个章头指针此前已就位（§12.1/§12.8.12b/§12.8.12c/§12.9.1/§12.10/§12.19/§12.20/§12.14/§零·C 等），本轮未动。

#### 动作 2 — 建立强制同步机制（文档规则 + 映射 + 闸门脚本）
- **新增 `#### 12.15.10 破解新字段→同步分字典（强制规则）`**：固化「源→分字典映射表」(17 源→17 附录，并显式标注 ZHB/新浪/akshare 等 ⚠️ 无分字典=主字典自身即权威)，及「破解后 4 步强制流程」（登记主字典→查表定位分字典→追加原始证据→跑闸门须零失败）。
- **新增 `scripts/verify_sync_check.py`（离线闸门，零网络，纯标准库）**：
  - HARD FAIL（CI/commit 前闸门，退出码 1）：①断链(主字典引用的 verify/*.md 须存在) ②孤儿(verify/*.md 须被引用) ③映射一致性(内嵌 MAPPING 每个分字典须存在且被引用)。
  - ADVISORY WARN（best-effort，默认关闭，仅 `--sync` 执行，避免跨源字段码误报噪声）：④字段级同步抽检(主字典字段 token ⊂ 对应分字典)。
  - 用法：`python scripts/verify_sync_check.py [--strict] [--sync] [--repo DIR]`。
- 复验：默认闸门 **0 断链 / 0 孤儿 / 映射全一致 / 0 warn**（17 引用 ↔ 17 附录）；`--sync` 深审为 advisory，不阻提交。

#### 结论
- 主字典 ↔ 17 分字典 双层架构闭环：决策层有覆盖指针、实证层有原始契约、机制有强制同步规则 + 离线闸门防割裂回潮。
- 闸门脚本可直接挂 pre-commit / CI，确保「破解新字段必同步分字典」不被绕过（H9 断链问题不再复发）。

### 🐛 V17.0.15 技术面数据缺陷修复 + K线形态识别接入（2026-08-31）

承接 V17.0.14「死代码复活」排查，本轮修掉两处**实质失真**并接入形态识别。

#### P0 修复：med 报告技术面用 close 近似 high/low + volumes 传空（真 bug）

- **现象**：`get_med_report.py` 原为 `_hi_m = _cls_m[:]` / `_lo_m = _cls_m[:]` /
  `analyze_technical(_cls_m, _hi_m, _lo_m, [])`——注释写"若无则用 close 近似"，
  但 `tdx_get_security_bars` 的 keys **本就是 `['time','open','close','high','low','volume','amount']`**，
  真实 high/low/volume 一直都在，是调用方没取。
- **后果一（KDJ 失真）**：RSV=(C−L9)/(H9−L9) 的分母退化成「9 日**收盘价**极差」，
  系统性小于真实 9 日振幅 → **RSV 被放大 → 金叉/超买信号过度敏感**；一字板/停牌时
  H9==L9 还会被钉成 RSV=50。
- **后果二（量能全程缺失）**：`analyze_technical` 在 `volumes` 为空时**根本不产出 `volume` 键**
  （`if volumes:` 门控），med 报告的量价配合判断此前从未生效。
- **修复**：按列名（`high`/`low`/`volume`）取真实值，列缺失才回退 close 近似；
  **统一行过滤条件**保证 closes/highs/lows/volumes 四序列严格等长对齐。
  新增 `[KDJ]`（含金叉/死叉判定与超买超卖区）与 `[量能]`（今日量/5日均/量比/近5日量能趋势）输出。

#### P1 接入：K线形态识别（TA-Lib 61 形态，sht 报告【十六·五】章）

- **前提核查**：`get_kline_patterns` 依赖 TA-Lib，而**环境未装** → 该函数恒返回 `{}`（`except ImportError: pass`）。
  **未先装就直接接入会产出"永远空白的假章节"**（V17.0 已修过的 M1/M4 假成功类型），故先解决依赖。
- **安装**：`pip install TA-Lib` 成功装到 **0.7.1**（Windows cp313 有预编译 wheel，**无需 VS 编译环境**）。
  实测 61 形态全部返回，构造的长下影被正确识别为 `dragonfly_doji`/`takuri`（均 +100 看涨）。
- **零额外请求设计**：sht 两处 `baidu_kline_full(code, 5)` 统一改为 `count=60`
  → 共用同一 cache_key `D:{code}:60`，第二次命中进程内/磁盘缓存，**净增网络请求为 0**；
  60 根同时满足 TA-Lib CDL 族的 lookback 要求（已在测试核实两处调用参数均未被测试钉死）。
- **输出**：看涨/看跌信号分组 + 中文形态名（模块级 `_CDL_CN` 表，61 键全覆盖，未命中回退英文原名）
  + 一致性研判；并附"须结合位置与量能、不可单独作为买卖依据"的风控提示。
- **降级契约**：未装 TA-Lib 时静默返回 `{}` → 整章自动跳过，报告不中断。

#### 依赖与测试

- `requirements.txt`：更新 TA-Lib 说明（实测可装、仍保持可选——无编译环境平台装失败会破坏整体安装）。
- 新增单测 **9 例**（`tests/core/test_core_technical.py`，13 → 22）：
  - `TestKlinePattern`：短序列 → `{}`；**mock 掉 talib 验证静默降级**（不抛异常）；
    有 TA-Lib 时返回 61 形态且长下影识别为 `dragonfly_doji`/`takuri`。
  - `TestAnalyzeTechnicalInputs`（P0 回归保护）：真实 high/low 与 close 近似**必须**算出不同 KDJ
    （若相同即说明又退化成近似）；close 近似导致 K 值失真；`H9==L9` 钉 50 的已知降级行为固化；
    volumes 为空不产出 `volume` 键 / 非空则产出且字段正确 / 短量序列不崩。

### 🔍 V17.0.15 统一层 / 缓存层复核 + 5 大脚本消费核对（2026-08-31，Request H）

按「最近新增的字典字段」反向复核架构层，结论：**统一层 1 项须改、缓存层 1 项须补、
val 1 处静默假信号须修；CYQ / K线形态**不进**冻结规范字段集**。

#### ① 缓存层（最高风险，已修）：`em_get` 无数据缓存 → CYQ 会打爆东财

- **发现**：`sc_network.em_get` 只有**令牌桶限流 + 熔断**，**没有任何数据缓存**。
  V17.0.14 把 CYQ 接到东财 push2 kline 后，全仓扫描时 sht/med/lng 各调一次
  `get_cyq_distribution` → **3N 次东财请求**。而东财 push2 系是**连接级风控**
  （`RemoteDisconnected`，字典 §12.3 实测恢复 20+ 小时），一旦触发会**连带打挂资金流与行情**。
- **修复**：`sc_kline_cache` 新增一对类型无关的 `get_cached_blob` / `set_cached_blob`
  （复用既有 TTL 24h / LRU 500MB→400MB / 原子写 / 锁），`get_cyq_distribution` 走 `CYQ` 命名空间。
  3N → **N**。CYQ 依赖的 240 根日K+换手率属 T+1 稳定数据，与 K 线同性质，故同 TTL。
- **关键约定：只缓存非空结果**。把失败/空数据写进缓存 = 把一次瞬时故障固化 24h。
  缓存读写异常一律静默，CYQ 仍走网络。

#### ② 统一层（已修）：`turnover_pct` 的 FieldSpec 与代码/字典漂移

- `sc_schema.FIELD_SPECS` 里 `turnover_pct` 写的是 `source_preference=(ZHB,)` /
  `time_anchor=T_MINUS_1` / `is_real_time=False`，但实证主源是**腾讯 T 日实时**：
  - `get_turnover_pct` docstring（V16.3 M）自述「换手率归 A 类当日即时指标——9:30-24:00 不接受 ZHB T-1」；
  - `get_canonical_stock_data`（:785-801）实为 rt_quote → ZHB → **腾讯**兜底，
    并写 `field_sources["turnover_pct"] = "realtime:tencent"`（V16.2.3）；
  - 同花顺 getharden `huanshou` 亦为当日值（**2026-08-28 探针实测 81 行**：`000712 huanshou=1.69`）。
- **修正为** `source_preference=(TENCENT, ZHB)` / `T_DAY` / `is_real_time=True`。
  已验证两集合仍**互斥**、无测试钉住其归属。

#### ③ 5 大脚本核对

| 脚本 | CYQ / 形态 | 换手率 | 结论 |
|:---|:---|:---|:---|
| val | 不消费（短线池+龙虎榜口径，无筹码/形态章） | **有缺陷，已修** | 见 ④ |
| mak | 不消费（大盘/板块面） | 已正确（腾讯 T 日优先，:276-280） | 无需改 |
| sht | V17.0.14 接入 CYQ；V17.0.15 接入形态 | — | 已完成 |
| med | V17.0.14 接入 CYQ | — | 已完成（P0 技术面已修） |
| lng | V17.0.14 接入 CYQ | — | 已完成 |

- **CYQ 四字段 / K线形态 / f61 序列不进冻结规范字段集**，理由：
  ① 规范集是**单股当日标量快照**，CYQ 与形态是 **210~240 天窗口的派生计算结果**，粒度不同；
  ② 规范集每字段都要求**多源可降级**，而 CYQ 依赖**独占源东财 f61**、形态依赖**可选依赖 TA-Lib**，
  纳入会破坏「字段可降级」不变式；③ 规范层面向全市场 5000+ 只扫描，承受不起 O(240×150) 计算。
  现状（各脚本早取一次 `_cyq_dict` 复用，V17.0.14）已是正确分层。

#### ④ val 两处「缺失值被当成有效值」缺陷（已修）

- **策略 01 龙回头（核心）**：原 `turnover = await get_turnover_pct_async(code) or 0`。
  `get_turnover_pct` 只查 ZHB 且无实时兜底，交易日 **09:30-24:00**（最常运行时段）
  `_should_use_zhb_for_realtime()` 恒 False → None → `or 0` 变成 0，三重叠加成**系统性结论虚高**：
  ① 文本「换手率仅 0.0%，缩量企稳，筹码沉淀充分」是**由数据缺失伪造的利好**；
  ② 0 ≤ cap(8.0) 故不过滤；③ `(8-0)*0.1 = 0.8` 反而是**理论最高加分**。
  即缺失被当成「极度缩量」这一**极值**。
  **修复**：取值次序 = 池内实时字段（腾讯批量预加载 V15.5.9）> ZHB 查询；取不到则**判据不参与**
  （加分 0.0 + 文本明说「换手率数据缺失(未参与缩量判据)」），既不伪造利好也不误剔除标的。
- **龙虎榜初筛/评分**：`avg_turnover` 原在缺失时无条件拼进 reason → 输出伪造的「平均换手率 0.0%」。
  改为按**有效值**求均值，缺失则整句省略（`_to_txt`）。该值只影响加分不影响过滤，方向不会反。

#### ⑤ 实证纠错：getharden **确实**返回 `zhangfu` / `huanshou`

- 代码注释 V16.4.0 写「getharden 不返回涨幅」——**与实证矛盾，是错的**。
  2026-08-28 探针实测 81 行，字段齐全：
  `['id','name','code','reason','date','close','zhangdie','zhangfu','huanshou','chengjiaoe','chengjiaoliang','ddejingliang','market']`，
  样本 `000712 锦龙股份 {"close":11.8,"zhangfu":9.972,"huanshou":1.69}`。字典 §12.8.12 才是对的。
- 修正 val 注释；`huanshou` 覆盖改为**仅当为正**（东财人气榜兜底路径无此键，此时保留腾讯预加载值）。

#### 测试（33 例新增，回归 390 → **423 passed**）

- `tests/core/test_core_blob_cache.py`（**新增 14 例**）：往返一致性（dict/list/标量）、
  命名空间隔离（CYQ/D/PAT 不串 + 不污染 K 线槽位）、TTL 过期**主动删除**、
  损坏文件 → None、不可 pickle 对象静默失败、**原子写无 .tmp 残留**、按命名空间清理、`__all__` 导出。
- `tests/core/test_core_cyq.py` 新增 `TestCyqDiskCache`（**8 例**）：二次调用**零网络请求**、
  三脚本 3N→1、**空结果不落盘**、**异常结果不毒化缓存**、按 code / days 分键、
  缓存层不可用仍返回结果。
  - ⚠️ 同时修了**测试自污染**：缓存写入真实 `cache/kline/` 会留下 `CYQ_*.pkl`，
    导致次日跑测试命中缓存 → `m.call_args is None` 假失败。现统一走 `_TmpCacheDir` 基类隔离。
- `tests/reports/test_reports_val_turnover.py`（**新增 11 例**）：
  已做**变异检验**——回退到 V17.0.15 前实现时 7 例转红（含两条核心断言：
  不输出「缩量企稳」、加分不为 0.8），确认测试真能拦住回归。

### 🔬 二次复核：字典最新字段 ↔ 统一层 / 缓存层 / 5 大脚本（2026-08-31）

承接上一节复核，再按「近几天新登记的字典字段」逐条回扫一遍，
**结论：统一层与缓存层无需结构性调整，5 大脚本无需再改；但查出 2 处文档 gap 并已修复。**

#### ✅ 核验通过（无需改动）

| 项 | 核验结果 |
|:---|:---|
| 统一层 `turnover_pct` 规格 | 上一节订正的 `(TENCENT, ZHB)` / `T_DAY` / `is_real_time=True` 已落地，与实证主源一致 |
| 688 成交量单位（V17.0.12） | `_tencent_volume_divisor` 只需覆盖 `sc_datasource.get_tencent_quote`（**唯一**输出 `volume_hand` 的腾讯通路）；`tdx_client` 单只/批量路径的 `_vol_v` 仅用于 `==0` 僵尸判据、不输出 `volume_hand`，故无需换算——**字典该注记正确** |
| 统一层 `roe` 口径 | 走 TDX F10「加权净资产收益率」（报告期制，带 `roe_type` 标注），**不经 push2 f173 / 腾讯[65]**，故不落入字典所记的「最新报告期 vs TTM」口径陷阱 |
| 缓存层——财务类 | `get_gross_margin_and_roe` / `get_roe_trend_series` 主路径为 **TDX F10 本地文件、零网络**，仅兜底走新浪 HTTP；财务数据季度级变更 → **无需缓存** |
| 缓存层——K线形态 | `get_kline_patterns` 是**纯本地 CPU 计算**（TA-Lib，输入为已缓存的 60 根日K），无网络请求 → **无需缓存** |
| 5 大脚本 | val 换手率已修、mak 本就正确（腾讯 T 日优先）、sht/med/lng 的 CYQ 与形态已接入；新字段无遗漏消费点 |

#### 🐛 修复 1：`push2 f86` 破解结果**漏登记**进字典（文档声称已同步、实际未同步）

- **问题**：V17.0.11（2026-08-28）CHANGELOG 写「同步: field_dict §12.3.1 新增 f86 行」，
  但全字典 grep `f86` 仅有 §12.3.1 注记里 V17.0.4 的**旧结论**——新行从未添加。
  这是继 `calculate_cyq`"注释称已单测、实际零测试"之后的**第二处同类文档失真**。
- **更严重的是字典内部自相矛盾**：旧结论把 f86 归为「**待定候选（常量/标记类）**」，
  记 `f86=178712/178713（恒,差1）`；而 V17.0.11 已判其为 **Unix 时间戳**。
- **已补证据块**（`docs/field_dict.md` §12.3.1），用**原始采集文件**而非摘要确证：
  `20260819/raw_push2_full.json` f86 = 1787124843/1787124870/1787127101/1787127119
  → 换算 **2026-08-19 15:34~16:11**（当日收盘后各股最后行情时刻，非采集时刻 22:48）；
  `20260812/raw_push2.json` f86 = 1786518339 → **2026-08-12 15:05:39**；
  跨 7 日差 606531 秒 = **7.02 天**，与日历差吻合。
- **旧观察的定性**：`178712` 实为 10 位时间戳**取前 6 位**的记录值（178712xxxx 覆盖 9999 秒 ≈ 2.78 小时，
  故单批采集内看似"恒定差 1"）。观察本身没错，**是截断记录销毁了可判别性**。
  → 已订正旧结论，并记入教训：**时间戳 / 大整数 ID 一类字段必须记全量原始值**。
- **接入决策：不纳入统一层规范集**（留档用途：数据新鲜度校验 / 停牌股识别）。
  理由是规范集要求每字段**多源可降级**，而 f86 为 push2 **独占**，纳入即破坏该不变式；
  且 `field_sources` 已隐含时间语义（ZHB=T-1 / push2=当日），现有僵尸检测靠 `volume==0` 成本更低。

#### 🐛 修复 2：`sc_kline_cache` 的 `"PAT"` 命名空间注释误导

- docstring 把 `"PAT"（K线形态）` 与 `"CYQ"` 并列为命名空间示例，但**形态从未走该缓存**
  （本地 CPU 计算，无网络请求）→ 易让维护者误判"形态已缓存"而漏掉真正的网络热点。
- 已改为明确说明：`PAT` **仅**作为 `tests/core/test_core_blob_cache.py` 中「与 CYQ 不同的第二个命名空间」
  的**测试夹具**存在（用于验证隔离性），**勿删、也勿把生产代码指向它**。

### 🐛 落地核查：东财 clist **f23 被误当 PE 使用**（2026-08-31，真实静默 bug）

用户要求「继续核实，落实字典中的字段已经实际落地」→ 写脚本对字典字段 × 生产代码消费点做全量比对
（`scripts/field_landing_audit.py`，已固化为常驻工具），再对报出的缺口逐条甄别，
查出并修掉一个**长期静默失效**的字段映射错误。

#### 根因

`sc_datasource.get_em_board_members`（东财 `clist/get` 板块成分股）原写
`"pe": item["f23"]` 且注释标 **"PE(动)"**——**错的，f23 实为市净率 PB**。

#### 三条独立铁证

1. **跨接口对撞**（12 个采集日同一股票，`ulist` ↔ `stock/get`，2% 容差 **100% 命中**）：
   f9=f162 动态PE（150/150）、f114=f163 静态PE（190/190）、f115=f164 PE-TTM（166/166）、
   **f23=f167 市净率 PB（238/238）**
2. **量级**：f9 中位 **20.84** vs f23 中位 **2.22**，相差 **9.4×**，分属 PE 族与 PB 族。
3. **符号判别（决定性）**：**PE 可为负（亏损），PB 恒为正**。实时探针 `clist/get` 实测
   爱克股份 300889 **f9 = −92.73（亏损）而 f23 = +3.66** → f23 不可能是 PE。
   另两样：晨丰科技 603685 f9=162.85/f23=3.35；腾景科技 688195 f9=355.98/f23=34.22。

   > 附带修正字典 §12.3.2：原记「f114 = 市盈率(动)」有误，实为**静态 PE**。

#### 后果链（静默，不报错、不产生 NaN）

`get_em_board_members["pe"]`（实为 PB）→ `get_industry_peers.peers[]["pe"]`
→ `get_med_report.py:1269` `score_data.industry_pe`（行业平均 PE 变成**行业平均 PB**）
→ `sc_scoring.py:237` 判据 `if data.pe_ttm < data.industry_pe:`
—— 拿 **PE(≈20) 去比 PB(≈2)**，**几乎恒为 False**
→ 「PE低于行业均值」**+15 分永不触发**、该结论永不出现。

> 📌 影响范围：**仅东财 clist 兜底路径**。TDX MAC 主路径用 `pe_dynamic`（真 PE），
> 修复后两条路径口径一致。

#### 修复

- `fields` 请求串补 **f9**；`"pe"` 改取 **f9**（与 TDX 的 `pe_dynamic` 口径一致）；
  新增 `"pb"` 取 **f23**（正确标注为市净率）。
- 新增 `tests/data/test_data_em_board_members.py`（**12 例**）：钉死 pe←f9 / pb←f23、
  两者数值不得相同、请求串必须含 f9 与 f23、市值单位换算、异常降级。
  **已做变异检验**：把 `pe` 改回 f23 → **3 例转红**（含核心断言），确认测试真能拦住。
- 字典新增 §12.3.2.1（ulist/clist 行情字段表，补 f16/f17/f18/f20/f21/f23 等**此前零登记**的字段）、
  §12.3.2.2（落地核查结论：7 项「字典已核实但代码不直接消费」经甄别**均非缺口**，
  已由腾讯/ZHB/TDX/本地判断等替代源落地，属多源可降级生效）。

### 🚨 V17.0.16：资金流四档**层级重定案**——「主力净 = f137 + f140」是重复计数

承接落地核查（上一节）的最后一个缺口 `f145`（只在区间简写 `f135-146` 里带过、查无专属说明），
在补逐号表时发现**四档的层级关系与代码/字典的既有结论都不符**，深挖后推翻 V17.0（2026-08-14）旧定案。

#### 旧结论错在哪

旧版把 f135–f146 当作**并列四档**（特大/大单/中单/小单），并据此算
「主力净额 = f137 + f140」。实为**两层错误**：
1. **层级错位**：f137 不是"特大单净"，它是**合计档**。
2. **重复计数**：f137 已含 f140，再 +f140 → 主力净额虚高。

#### 三条独立铁证（2026-08-31，12 个采集日原始数据）

1. **结构自洽 + 全组合盲搜**（169 样本，相对差 **0.00**，100% 命中）：
   `f135 = f138 + f141`、`f136 = f139 + f142`、**`f137 = f140 + f143`**
   → f137 是合计档。**反证**：旧命名下应推出 `f137 = f138 − f139 = f140`，
   实测 **0/169 相等**、96.4% 显著分离（|f137−f140|/max 中位 0.707）。
2. **ulist239 同名号段**（236 样本）：**`f62 == f66 + f72` 命中 236/236 = 100%**
   → 东财标准：f62=主力净、f66=超大单净、f72=大单净、f78=中单净、f84=小单净。
3. **跨接口对撞**（234 样本，2% 容差）：
   `f62==f137` 96.6%、`f66==f140` 98.3%、`f72==f143` 96.2%、
   `f78==f146` 95.7%、`f84==f149` 96.2%；**对照组 `f84==f146` 仅 0.9%**（排除）。
   （2026-08-14 命中率偏低系**采集时点差**：同日大盘股 600519/601288 偏差 <1%，
   小盘股 5–21%，符号一致——非字段错位。）

#### 正确层级

| 字段 | 语义 | 输出键 |
|:---|:---|:---|
| f138/139/140 | 超大单 买/卖/净 | `fund_super_*` |
| f141/142/143 | 大单 买/卖/净 | `fund_large_*` |
| **f135/136/137** | **主力 买/卖/净（= 超大单 + 大单）** | `fund_main_*` |
| f144/145/146 | 中单 买/卖/净 | `fund_mid_*` |
| **f149** | **小单净（段内无买/卖明细）** | `fund_small_today` |

#### 后果

实测 `(f137+f140)/f137` 中位 **1.196** → **主力净额虚高约 40%**，
沿 `data_provider.main_net_buy_amount`（元→万）流入各报告章节；**静默、不报错**。
ulist 批量侧 `main_net_inflow_wan = (f62+f66)/1e4` 是**同一个 bug**。

#### 改动

- `sc_datasource._em_quote_full_impl`：`flow_map` **整体重映射**（f137→`fund_main_today`、
  f140→`fund_super_today`、f143→`fund_large_today`、f146→`fund_mid_today`）；
  新增 f135/f136→`fund_main_buy/sell`、**f149→`fund_small_today`**；
  **删除** `fund_main_today = f137 + f140` 的相加逻辑。
- 请求串补 **f149**（旧版未请求 → 小单净恒缺）。
- `get_em_batch_quotes`（ulist 侧）：`main_net_inflow_wan` 改为 **f62/1e4**，请求字段去掉 f66。
- 注释订正：`core/data_provider.py:905`、`stock_common/sc_schema.py`（四档 FieldSpec 说明）。
- 新增 `tests/data/test_data_em_fund_flow_tiers.py`（**20 例**）：钉死四档映射、买/卖映射、
  结构不变量 `主力净 == 超大单净 + 大单净`、四档互不相同、请求串含 f149、缺失字段不得填 0。
  **已做变异检验**：还原旧映射 → **11 例转红**（含核心断言）。
- 字典新增 **§12.3.4**（资金流四档层级专章，逐号表 + 三铁证 + 数值样例 + 接口间编号差异）；
  订正 §12.3.1 主线块、§12.3.2.1 对照表、`stock_individual_fund_flow` 行、§12.15 主力净两行、
  腾讯 [86] 段、§12.19 实时链等 **6 处** `f137+f140` 旧述。
- `docs/PROJECT_CONTEXT.md`「口径铁律」同步改为 **主力净 = f137**。
- **真实字典 `docs/script_data_dict.md` 同步 13 处**（用户澄清其为「5 大脚本实际消费字段速查/
  改主字典发现错误后快速定位脚本改动点」的索引，此前滞后于 V17.0.16 代码）：主力净行改 `f137(不+f140)`、
  四档层级行订正为「主力=f137(=超大单+大单)；超大单=f140/大单=f143/中单=f146/小单=f149」、
  ulist 批量主力净改 `f62(不+f66)`、对照表 233/234 与七章/mak 轮同步；更新日期标
  `2026-08-31(V17.0.16 资金流四档重定案)`。带匹配校验的批量替换 **13/13 全命中、无漏网**。
- **非资金流字段离线全量比对**（2026-08-31 13:13，用户要求「用现成采集+zhb、零网络」）：新写
  `scripts/real_dict_xcheck.py`，对真实字典全部 `fNN` 断言 × 5 大脚本+sc_datasource 代码消费做交叉核查，
  并用 `docs/field_verification/2026*/raw_push2_full.json`/`raw_ulist239.json` 离线采样背书关键语义。
  结果：**非资金流字段零真滞后**——f162/f163/f167/f182/f198/f50/f178/财务TTM族(f103-f190)、
  ulist f9/f114/f115/f23 采样值全部印证字典断言（f167 PB 恒正、f182=2 主板、f198=BKxxxx）；
  10 个「疑似滞后」经甄别均为误报（区间串 f2-f21、ulist239 语义注记 f37/f112、等价源 f50、
  market_type 走响应键名而非 f182 字面量）。唯一索引缺口 `clist f23=PB` 已补入 pb 行。

#### 工具改进

`scripts/field_landing_audit.py` 升级 **v3**：登记判定新增**区间简写**（`f135-146`）与
**斜杠列举**（`f144/145/146`）展开，并区分两种登记强度——`mentioned`（有独立 `fNN` 字面量）
与 `range_only`（**只在区间简写里带过，查无专属说明**）。后者单列为 **②b 类**警示，
比"零提及"更隐蔽（阅读者会以为字典里有，但全文检索定位不到任何一行）。
升级后：②类（真·零提及）**归零**，②b 类 = 1（f145，已由本次 §12.3.4 补表关闭）。
- 字典补记**接口间编号不一致**：`stock/get` 的 f135-f146 是资金流四档（四组自洽校验全通过），
  而 `ulist` 的同号段是**价格/成交量**——跨接口不可照抄编号。

### 🧩 V17.0.14 CYQ 筹码分布接入管线（2026-08-31，死代码复活）

- **背景**：`sc_technical.calculate_cyq`（V17.0.7 实现，经典「三角形分布 + 换手率衰减」模型，与通达信 CYQ 一致）
  实现后**从未被任何管线调用**——报告此前只用「股东户数变化」代理筹码面评分；且该函数**从未有单测**
  （`sc_datasource` 旧注释称"已单测"属误记，已订正）。契因 `chengzuopeng/stock-sdk` 仓库能力对比分析。
- **关键阻塞与结论**：CYQ 必需 OHLC+**换手率**，而 TDX `0x0010` 日K（mootdx bars，仅回
  open/close/high/low/vol/amount）与腾讯 ifzq `fqkline` **均无换手率字段**；东财 `stock/get` 的 `f168` 只有当日快照。
  → **唯一可用源是东财 push2 kline 的 `f61`=换手率(%)**（历史全窗口）。
- **新增** `sc_datasource.get_cyq_distribution(code, days=240)`：走 `/api/qt/stock/kline/get`，
  复用既有 `_em_fflow_request(..., prefer_his=True)` 多域轮换（**push2his 全窗口优先**，`prefer_his=False` 会被
  push2delay 截成当日窗口——V17.0.4 同类根因）；`@requires_push2` 门控，任一步失败一律返回 `{}`，报告章节自动跳过。
- **评分接入** `sc_scoring._score_holder`：新增 `ScoreData` 四字段
  `cyq_benefit_pct` / `cyq_avg_cost` / `cyq_concentration_90` / `cyq_concentration_70`；
  集中度 <0.12 **+12**「筹码高度集中」/ <0.2 **+7**「筹码较集中」/ >0.35 **−6**「筹码分散」；
  获利盘 >0.85 **+4**「获利盘丰厚」/ <0.25 **−4**「套牢盘较重」。阈值经 `hc.get(key, 默认)` 回落，
  **无需改 `strategy_config.yaml`**（holder 子段本不存在）。
- **报告接入** sht（新增「十三·五、筹码分布（成本集中度）」章）/ med（「八、筹码稳定性」章内新增小节）/
  lng（「六、长线筹码沉淀」章内新增小节）；三处均**提前一次性拉取、章节与评分共用**，无重复网络调用。
- **新增单测** `tests/core/test_core_cyq.py`（**28 例**，算法/数据入口/评分三层）：
  含 f61 解析、`secid` 多市场前缀（沪 1. / 深创 0. / 北交所 0.）、None 响应/空 klines/坏行/坏 JSON/异常 → `{}`、
  `prefer_his=True` 与 `klt=101` 请求参数钉死、零换手率无筹码、深度套牢/全面浮盈的 `benefit_pct` 方向性、
  `concentration_70 ≤ concentration_90`、评分加减分与无数据不误判。
- 文档：`docs/field_dict.md` 新增 §12.3.3「日K线 `stock/kline/get`」，记录 f51–f61 列序与 f61 换手率的**独占性**
  （并说明与 §12.8「东财无公开筹码接口」条目不矛盾——前者说没有现成筹码接口，V17.0.14 解决的是推演所需的换手率来源）。

## [17.0.12] - 2026-08-29

**🐛 腾讯科创板(688)成交量单位修复 + 🔬 三字段旧结论全样本复核 + 📐 对撞规则表述校正**

### 🐛 腾讯科创板 688 成交量单位 BUG（V17.0.12）

- **现象**: 腾讯 `qt.gtimg.cn` 对**科创板 688 段**的 `[6]成交量 / [7]外盘 / [8]内盘`
  返回的是「**股**」，其余板块（主板 / 创业板 / 北交所 92x）返回的是「**手**」
- **根因**: 解析层未区分板块，688 段成交量被放大 100 倍
- **实测证据**（20 股横截面反推每手股数）: 主板/创业板/北交所 = 99.3~100.9；
  **688 段 = 1.01~1.02**（即腾讯给的是股，÷100 才是手）
- **边界**: `[10]买一量 / [12]卖一量` 全板块均为「手」不受影响；`[37]成交额(万)` 与量纲无关
- **修复**:
  - `core/tdx_client.py` 新增 `_tencent_volume_divisor(code)`（688 → 100.0，其余 → 1.0）
  - `stock_common/sc_datasource.py::get_tencent_quote` 对 `volume_hand` 施加除数归一
- **覆盖度核验**: `get_tencent_quote` 是唯一输出 `volume_hand` 的腾讯通路；
  两处僵尸数据校验（:753/:971）用的是 normalize 前的原始值（0÷100=0，不受影响）；
  `scripts/capture_field_probe.py` 刻意保留原始值（归一会污染字段破解数据）
- **测试**: 新增 `tests/core/test_tencent_volume_unit.py`（8 项，覆盖板块判定 + 端到端解析）
- **回归**: 277 passed / 45 deselected / 0 failed（基线 269 + 新增 8，零回归）

### 🔬 三字段旧结论全样本复核（20 股）

| 字段 | 旧结论 | 终核结论 | 关键证据 |
|---|---|---|---|
| push2 **f85** | 流通股本(股) | ✅ **升 L1** | 17/18 对撞 + 10 只"总股本≠流通"歧义消除 + 688500 个位双精确 + 17/20 结构自洽 + 0/18 排除"自由流通股本" |
| push2 **f173** | 加权ROE | ✅ **升 L1**（附**口径硬限定**） | 18/20 精确命中；17 只跟加权、0 只跟扣非 → 确为**加权**非扣非；⚠️ 口径=**最新报告期，非年化 / 非 TTM** |
| 腾讯 **[86]** | 候选"净主动买入量" | ❌ **证伪，退回 ❓未知** | 见下 |

**⚠️ [86]=委差 是一次严重假阳性**（已撤回）：
- 初判依据仅 Pearson r=+0.965 → 升级 L2
- 稳健复核打脸：Spearman **−0.012**、留一法 Pearson **−0.863（符号翻转）**、
  同号率 12/20、对撞精确命中 **0/20**、1% 容差 **0/20**
- 全 88 字段扫描最大 |Spearman| 仅 **0.540**（即无任何字段能通过门槛）
- 真因：相关完全由离群点 **601288**（量级大 2 个数量级）绑架

### 📐 对撞规则表述校正（重要）

- **用户定义的唯一对撞规则**（已固化进 `CRACKING_METHODOLOGY.md` 〇·二节）：
  扫描**同一日期不同源返回的相同数值**的字段；若其中之一已破解，则可反推同值的
  未知字段即该已破解字段。**唯一证据 = 逐股数值相等 ≥8/20**；1% 容差只能证明
  "同族"；**相关性 ≠ 对撞**
- **撤回**: 此前写在文档里的"**同序号 ≠ 同字段**"被误记为用户设定的规则，已撤回。
  正解：序号只是字段的一种表现形式，**不能**单独因序号一致/不一致就默认不同源的
  序号代表同一/不同字段；"同序号=同字段"只能是对撞成立后的**结果**，不能是**前提**
- **新增强制流程**: 相关性分析必须 Pearson + Spearman（抗离群）+ 留一法三者同号
  且 |Spearman|>0.6 才可作候选证据

### 🐛 工具脚本修复

- `scratch/verify3_0829.py`: None 值格式化 `TypeError` → 新增 `fx()` 占位
- `scratch/verify3b_0829.py`: `NoneType - float` → 增加 `num(v) is not None` 守卫
- `tests/core/test_tencent_volume_unit.py`: patch 目标由 `sc_datasource._quick_request`
  改为 `stock_common._quick_request`（运行时动态 import），并加守卫断言防止静默走网络

## [17.0.11] - 2026-08-28

**🔬 push2 f86 = 当日收盘/最后行情时间戳破解**

- 采集 20260828（19 源 487s，push2 主域冷却解除 166.8s，ZHB=20260827 T-1）
- **多日序列铁证**（600519）: f86 = 1787645498 → 1787904720，逐日递增约 **86400**（=1 天秒数）
  → 判定为 **Unix 时间戳**
- 全 20 股换算均为 8/28 当日 **15:34~16:12**（收盘后各股最后行情时刻），
  非采集时刻（22:48 采集）→ 确认是**当日收盘数据时间**
- 字典 8/19 旧观察"f86=178712/178713 恒差1"实为同一时间戳字段的旧日期值，互相印证
- 复核: f85=流通股本(股)、f173=加权ROE（fuyao H1 三样本精确）
- 中报指标入库 **18 只**（tx65/tx66 L1 终判条件达成，ded_weighted_roe / weighted_roe / roa 三键）
- 同步: field_dict §12.3.1 新增 f86 行 + 腾讯[86]新观测；矩阵 977/1175/48
- 回归 269 passed ✓

## [17.0.10] - 2026-08-27


**ZHB T-1 对撞规则固化 + Col[33] 连板数破解 + 批量报错修复**

### 📐 ZHB T-1 对撞规则固化 V17.0.10b（2026-08-27）

**规则写入（CRACKING_METHODOLOGY.md 〇节 + field_verification README 每日流程）**：
- ZHB 本地包数据日期=**最近交易日快照**(交易日运行落后 T-1; 休市日=报告数据日, 对撞有效)——严禁"当日报告 ↔ 当日采集 ZHB"直接比
  (2026-08-27 初犯得 type 0/20 假阴性, 纠正后 20/20)
- 正确矩阵: 采集目录 YYYYMMDD 的 ZHB(T-1) 应对撞 **T-1 当日报告**; 对撞当日报告
  须先验证字段实时性(如涨停族 type/lianban/count 实测为当日盘中值)
- 操作规范: 每次对撞先打印 raw_zhb.json 的 zhb_date + 报告文件名; 结论标注双日期
- capture_field_probe.py: meta.json 增写 zhb_data_date 字段, 完成行打印 ZHB 日期
- 回归 269 passed ✓


### 🔬 字段破解 V17.0.10（2026-08-27 采集, 19 源 519s）

**新破解: tdxstat Col[33] = 连板数（原"涨停类型族 ztlx"证伪）**
- 方法: **日期对齐对撞**——今日采集 ZHB(8/26数据) 与 8/27 MAK 报告涨停天梯对撞
- 铁证: type(Col33) 与天梯连板 **20/20 完全匹配**(000017=5/003040=4/002084=3 全精确)
- 当日涨停时 Col[31]/[32]/[33] 三字段一致=连板数; 非涨停日 type=None/0,
  count=涨停累计次数(近N日), lianban=历史高位(近N日最高连板/异动周期计数)
- 同步: field_dict.md Col[31]/[32]/[33] 对撞补强(Col33 ⚠️→✅)
- 中报指标入库 17 只(tx65/tx66 终判条件达成)
- 字段矩阵: 977 字段 / 1175 记录 / 多源 48
- 回归 269 passed ✓


### 🐛 批量报告报错修复 V17.0.9b（2026-08-27）

**1. LNG 688802(沐曦) 亏损股 UnboundLocalError**
- 根因: `_pe_src` 只在 `_pe>0`(盈利)分支赋值, 亏损股(pe_ttm=0/pe_dynamic=-699)走 else
  分支未赋值 → 444 行访问报 UnboundLocalError。仅亏损股触发, 盈利股全部正常。
- 修复: else 分支补 `_pe_src = "亏损(无正PE)"`。实测 688802 报告正常输出
  "PE(TTM): 0.00x (亏损(无正PE)口径...)"。

**2. SHT 300475 批量 margin TypeError**
- 根因: `resolve_datacenter('margin')` 批量预取偶发返回非 list(dict), sht 1104 行
  `for d in margin` 遍历 dict keys → `d['date']` TypeError。
- 修复(双层防御): ① `get_margin_trading_async` to_thread 结果非 list 置 []
  (源头); ② sht 消费端 `if margin and isinstance(margin, list)` 防御;
  ③ `get_block_trade_async` 同步 data 非 list 防御。
- 回归 269 passed ✓



## [17.0.9] - 2026-08-26


**Col[24] 货币资金破解 + 报告核查修复**

### 🔬 字段破解 V17.0.9（2026-08-26 盘后采集, 19 源 461s）

**新破解: tdxstat Col[24] = 货币资金（万元）`cash_reserve_wan`**
- F10 资产负债表「货币资金」逐股对照终极锁定: 600519=535.188亿(unknown_24 100%一致),
  17 只有数据全部匹配(14 最新期精确 + 600675/688500 为报告期差异=2026Q1值)
- 跨日恒定根因=财报季度才更新(静态财务字段); 历史"成交量/总负债/股本"三假设证伪
- 同步: `zhb_client.py` Col[24] 正名 unknown_24→cash_reserve_wan; `data_provider`/`tdx_client`
  注释更新; `test_data_zhb.py` 断言更新(45 passed); `field_dict.md` 7.3 节破解结论 +
  P0-1 关闭 + 跨源对照表新增货币资金行; `field_verification/README` 破解里程碑
- 采集: 20260826 归档 19 源全 OK; push2 主域 20h 冷却(push2delay 正常); thsdk 盘后不可用
- 字段矩阵重生成: 977 字段 / 1175 记录 / 多源 48
- 全量回归 269 passed ✓



## [17.0.8] - 2026-08-26


**82 份报告全量核查修复(跌停数假数据/扣非ROE/展示口径)**

### 🔴 报告核查修复 V17.0.8（2026-08-26 晚, 82 份报告全量核查驱动）

**P0 跌停数假数据(22→0)根因修复**
- `get_limit_pool_summary` 跌停兜底重写: 旧逻辑直接读 ZHB 全市场快照算跌停,
  但快照盘中恒为 T-1(前一日)——8/26 盘中把 8/25 的 22 只跌停误报为今日
  (KPL/push2ex 双源证实今日真实跌停=0)。权威链: ① 东财 getTopicDTPool tc
  (新 `_query_dt_pool_tc`, pool 可空但 tc 权威) → ② KPL RiseFallAnalysis dt
  (独立匿名源, 校验日期) → ③ ZHB 仅当快照日期==目标日期
- 排查确认 22 与 8/25 炸板池 22 为巧合, `_parse_limit_pool` 无字段错位
- MAK B 段跌停数恢复 pool 优先(A 段涨跌幅口径兜底), 撤销 V17.0.4 强制覆盖

**P1 扣非ROE 全 N/A 修复**
- `get_roe_trend_series` F10 路径补扣非ROE: 加权ROE×(扣非EPS/基本EPS) 同源推算
  (F10 无直接扣非ROE 字段; 曾用 fuyao index_deduct_weighted_avg_roe 实测为
  TTM 滚动口径与单期加权不可混排, 弃用)。新浪兜底同步加同口径推算

**P2 展示/口径**
- MAK E 段涨停名单改真实涨停全量(limit_up_all, 原用梯队 _leaders 含替补致
  "声称3只实际1只"); 名称优先级腾讯实时名>ZHB(消除 霞客环保/哈高科/二纺机 旧名)
- MAK B 段涨停明细>30 只加截断注明(原 43 只只显 30 行易误解)
- MED "静态PE"→"动态PE" 标签修正(实为 pe_dynamic f162), 与 LNG 对齐;
  LNG PE(动态) 改 canonical pe_dynamic(原 ZHB 动态, 数值与 MED 不一致)
- LNG/MED 解禁明细保留一位小数(原 .0f 四舍五入致 1.4万股显示 1 → 明细≠总计)
- 回归 269 passed ✓



## [17.0.7] - 2026-08-25

**field_dict_gemini 对撞复核 + FTShare / KPL / 千股千评多源接入（当日 23 段工作合并，结论已固化 field_dict.md）**

### 字段破解（对撞复核）
- **f103=经营活动现金流量净额(TTM)**（fuyao 官方季度现金流量表 5/5 精确）、**f104=营业总收入(TTM)**（18/18 恒等式）、**f105=归母净利润(最新报告期)**（fuyao 利润表逐字等）；证伪 Gemini「经营现金流/营业利润」旧注
- **f55=基本EPS(最新报告期)**=f105/f84；f109=归母净利(最新年报)、f160=年报EPS、f108=扣非EPS(TTM)
- **tx 区间涨幅族定案(前复权)**：tx62=YTD / tx71=60日 / tx69=10日 / tx75=180日 / tx79=250日；证伪 Gemini「主力占比/超大单占比」，推翻 f121/f122「资金流衍生」旧注
- **f147/f148/f149=散单(第五档)买入/卖出/净额**（净=买-卖 自洽）；f197=散单净占比=f149/f48*100（沪深守恒律，北交所退化）
- **Col[24]=货币资金(万元)**（F10 资产负债表 17 只全匹配，跨日恒定=财报季度更新）
- **Col[33]=连板数**（原「涨停类型族」证伪，与 MAK 涨停天梯 20/20 匹配）；**Col[31] 降级 (TDX 内部「近期异动周期计数」，与东财 zt_continuous 不同概念，消费侧勿单独依赖连板判定)**
- **腾讯 [86] 候选「净主动买入量」证伪**（Pearson r=+0.965 假阳性：Spearman -0.012、留一法 -0.863、同号率 12/20、对撞 0/20，真因离群点 601288 绑架）→ 退回 未知

### 架构 / 数据源接入
- 统一层接入财务 TTM 族（f103/f104/f105/f108/f109/f160/f190→ocf_ttm 等规范键）；删除 tx75 误作主力净额的假数据分支（603221 +13.45亿假流入）
- fuyao 升财务 TTM 主源 + thsdk 盘中专属层后移（盘后/午休关闸）；push2delay 降兜底；修复 get_fuyao_financials 缺 period 潜伏 bug
- **FTShare-MCP 采纳**：新增 sc_ftshare.py（13 函数，会话 TTL 自动续期），sht 千股千评+昨日涨停池晋级、lng 董监高+商誉交叉；字典 12.20 升级（85 工具全字段镜像见 verify/ftshare_fields_mirror.md）
- **KPL 无 Token 实测**：开盘啦 API 9/22 无 Token 可用（情绪/涨跌停/龙虎榜等），字典 12.21 升级
- levistock 全量审计：补录 7 函数，字典覆盖率 31/38→38/38
- 限流：longhuvip.com 四子域 @5rps 注册；导出 kpl_get_* 九函数

### 脚本 / 渲染修复
- md_render 中心修复：行内换行展开 + 表后空行规则（股东户数/综合建议/席位明细等粘连修复）
- lng 历史高点 qfq 渲染回归修复 + 九章研报瞬断重试；sht 研报 5→3 页
- lng 三处修复：ROE 表排序、营收 CAGR 混用 H1/FY 假负值、fuyao 现金流口径标注
- 东财 Cookie 注入（_get_eastmoney_cookie，提高封禁阈值）+ Cookie 过期自动检测
- CYQ 筹码分布（calculate_cyq）+ TA-Lib 61 形态（get_kline_patterns）+ 通达信抢筹/东财选股器接入
- 新增 docs/report_output_inventory.md 输出台账；datacenter 五类批量预取流水线（sht 提速）

回归：269 passed / 45 deselected（基线不变）

## [17.0.6] - 2026-08-23

**md 报告格式治理: 键值表全面回退竖排 + 明细伪表转真表(用户审美驱动)**

### 🎨 渲染器(md_render)
- **删除"字段: 值"块→2 列表格自动转换**(V17.0.3 引入)——恢复 V17.0.2 用户原则:
  基本信息/行情快照/估值/评分等键值竖排不表格化。原转换使首行字段名成为
  加粗伪表头(股票名称/T日主力净流入额/价值派评分等喧宾夺主), 且综合投资
  建议长文本被塞进单元格。死函数 _fieldval_block_to_md 一并清除。
- 普通行冒号对齐清理(:\s{3,}→": ")使还原后竖排自然对齐。

### 📊 该用表格处直出真表格(脚本端)
- sht/med 龙虎榜上榜记录(日期/上榜原因/净买入/换手率): CJK 宽度对齐空格
  伪表依赖脆弱间隙推断、常态未转换 → 直出 md 表格(V17.0.2o 席位表先例)。
- med 评级统计行去标题化(➤/**嵌套——➤ 全局转 ### 使计数行变成章节标题)。

### 🗃 存量报告迁移(scratch/migrate_reports_md2.py)
- **165 个文件 / 623 个误转键值表**还原为竖排(保守判定: 2 列+字段名特征+
  值长≤60; 真 2 列数据表零误伤); med 存量评级标题滥用同步修正。

### ✅ 验证
- 探针四案例(键值块/一致预期空格表/龙虎榜 CJK 表/评分块)行为断言全过;
  回归 269 passed / 45 deselected 基线不变。

## [17.0.5] - 2026-08-22

**tdxstat2 Col[4]/Col[11] 终破 + 腾讯 ROE/ROA 对破解 + ulist/push2 字段编号不同构实锤**

### 🔬 字段终破(全市场 16 包 + 20 股×7 目录流水线, docs/field_verification/20260822/cross_analysis.md)
- **Col[11]=change_mtd 本月至今累积涨跌幅%**(基准=上月末最后交易日收盘):
  19/20 股×7 包全精确(误差≤±0.015pp); 月界重置实锤(Col11(8/3)≡chg(8/3) 差=0.000);
  **"WTD 本周至今"命名被证伪**(两周共享同一锚点排除每周重置; WTD 错觉=月初周 MTD≡WTD);
  旧解"近5根K线 r=1.0"亦证伪(中位差 6.1pp); **§7.3 周一相等悬案结案**
  (月初恰满 20 根 K 线时 MTD 与 Col[17] 窗口重合, 每月一次与星期无关)
- **Col[4]/[6]/[8]=limit_up_down_seal 用户修正完全证实**: 三日滚动 col4@T≡col6@T+1≡col8@T+2
  **1434/1434 全市场精确 0 失败**; 符号 100%(涨停正/跌停负, 8/19 千股跌停日中位数转负);
  ST ±5% 亦正确; 可接入打板/封单衰减策略
- **腾讯 tx[65]=ROE / tx[66]=ROA 盈利质量对**: 天然实验——各股随自己中报披露日跳变
  (600519 8/15 后 30.53→32.41、002827→15.13、688589/920118→8/21 披露后), 未披露股恒定;
  量级全符(工行 8.93/万科亏损负); 修订 08-10"tx65=roe 证伪"结论(系对照基准错误)
- **tx[69]≡ulist f160(86% 互锁)+推翻字典旧"振幅"解**(0/138 等 tx43 且 35% 负值);
  近10交易日窗口周六口径 37/38=97%(盘中口径待终破);
  **ul_f160 ≠ pf_f160(利润率类静态)——ulist239 与 push2 字段编号不同构再添一例**
- f190≡ul_f48 100%(138/138) 再实锤; tx62/tx71=f122/f121 资金流衍生再证

### ♻️ 统一层与缓存
- `core/zhb_client.py`: stat2 键改名 `change_5k_bar`→`change_mtd`(修复与 tdxstat Col[27]
  在 full_market_snapshot 合并时的静默同名覆盖); `_ZHB_PARSE_SCHEMA` 2→3(解析缓存强制失效)
- data_provider.get_zt_streak_info 补封单额符号语义注释

### 📚 文档固化链条
- field_dict.md: tdxstat2 Col[4]/[6]/[8]/[11] 四行重写(铁证入典); §7.3 周一悬案结案;
  腾讯表 [62]/[65]/[66]/[69]/[71] 更新; V16.3 O28 备注标记推翻项
- 附录: tencent_verify.md/samples_verify.md V17.0.5 增补节; domain_glossary.md 同步;
  script_data_dict.md L1 层字段说明更新; §零·B 矩阵重生成(920 字段/1103 记录)

### 🆕 fuyao 官方 REST 全量契约镜像 + 盘后通道扩展(HiThink-Tech/Financial-API 研究)
- **新附录 verify/fuyao_api_full.md**(80KB): 上游 llms-full.txt 全量字段契约——62 端点
  请求参数+响应字段+口径注记零删减(行情/财务五类指标/估值 PS·PCF/竞价/涨跌停炸板池/
  异动原因 AI 文本/热榜/龙虎榜/基金 ~24 端点/全市场 Parquet 导出); §12.15.9 索引登记
- field_dict §12.8.12c 重写: 31→62 端点全景; **盘后可用性定案**(HTTPS REST 无 thsdk TCP
  盘后关闸限制——财务/池/竞价终态盘后可查, thsdk 盘后失败的替代通道); ROE/扣非ROE/ROA
  官方口径(tx65/66 对撞终判源); PS/PCF 字典新维度; seal_money/max_seal_money 封单双口径;
  auction_unmatched/昨量比/开板次数/seal_nextday 等新维度入典
- sc_fuyao.py 扩展 7→**18 端点**(auction×2/pools×3/anomaly×2/fin_indicators/
  financials×3/trading_days/adjustment_factors/index×3); __init__ __all__ 同步;
  ⚠️ 本机 Key 未配置→通道自动禁用(配 THS_FUYAO_API_KEY 即启用)
- **Key 已配置并实测(fuyao_key.txt, gitignore)**: 首采 20/20 全通——对撞三线:
  竞价族 auction_volume/amount ≡ ZHB[9]/[14] **19/19**、涨停池 seal_money ≡ zt_seal_amount **54/54**
  (双双 L1 互锁); tx65=扣非加权ROE(TTM) 官方 Q1 32.52≈32.41 锁定语义;
  契约偏差入典(calculate_* 前缀/归母同比未列/中报入库滞后 5003)
- 工程修复: fuyao_to_thscode 北交所前缀顺序 bug(920→.SH 整批拒绝);
  @cached 第二位置参数误当 ttl 潜伏 bug; TTL 表 +fuyao_auction
- **待办①中报终判自动化**: capture_field_probe 内置哨兵探测(h1_indicators_ready)——
  fuyao 上游入库当日即自动拉取全池扣非加权ROE/ROA 完成 tx65 L1 对撞, 无需人工盯守;
  当前状态: 上游仍滞后(code=5003), 哨兵正确跳过省配额
- **待办②基金域接入 lng/med**: sc_fuyao 新增 get_fuyao_fund_holdings/fund_profile +
  get_fund_watch_evidence(自选清单门控); lng【六、筹码与机构持股】/med 新增
  【十六之二、自选基金重仓侧证】段——输出持仓占比/重仓排名/报告期增减/
  基金股票仓位/重仓行业/前十集中度; 实测 025480.OF 10 持仓全字段到手

### ⚡ P0 清单实施(五脚本字段升级——基于 V17.0.5 已互锁字段)
- **sht**: 封单官方口径优先(fuyao seal_money 替代 bid1×涨停价估算)+**封单衰减率**
  (max/current, <30% 烂板预警/>=90% 全日封死)+涨停原因文本; 竞价实时族(live)
  未匹配量/昨量比(<50% 缩量诱多警示)/竞价量比——与 ZHB T-1 同源互锁时效升级;
  十五章新增衰减率信号(仓位降级联动既有 _seal_warn 体系)
- **med**: [本月至今] 动量锚点展示(change_mtd, 持有期 1-3 月正交基准)
- **lng**: ROE 双口径对照(报告期加权 F10 vs 扣非 TTM tx65, 差>5pp 盈利水分预警);
  现金流官方指标交叉(fuyao 净利润现金含量<80%/现金营运指数<0.9 排雷)
- **mak**: fuyao 竞价风向标聚合(高开/放量/红盘占比——9:25 盘前量化情绪,
  时效领先叙事型情绪源; 高开>50%+放量>30% 共振进攻信号)
- **val**: 新增策略24【月内动量】——change_mtd∈[5,25]% (ZHB 本地零网络);
  注册表/_sfmt/计数文案同步; 实测全市场 8003 只→2598 候选(Top10 月内 20%+)
- 统一层: canonical +change_mtd/+roe_deduct_ttm; 腾讯映射表 roa→TTM 正名(键名兼容)+
  +roe_deduct_ttm:65; sc_datasource 白名单透传补 roe_deduct_ttm; 缓存 TTL 表
  +fuyao_seal_map(30min)/fuyao_fund_holdings/fuyao_indicators(trading_day)

### 🔧 P1 清单实施(五脚本增强第二批)
- **sht**: 官方风向标标签直采(高开/放量——免自建阈值)+**异动解读 AI 文本**
  (fuyao anomaly-analysis-stock, 补 V17.0.2 移除盘口异动后的语义层空白)
- **med**: 财务兑现双源核验(fuyao growth 族营收/净利/营业利润同比 vs F10,
  calculate_* 前缀+契约 id 双兼容; 偏差>2pp 以财报原文为准提示)
- **mak**: 跌停池明细正式解法(fuyao limit-down-pool first/last_limit_time——
  东财 getTopicDTPool 空缺闭环); fuyao 连板矩阵互校(boards 六档+
  seal_nextday 次日续封率——独有字段, 30 日窗口)
- **P1-4 核查结论**: change_30d 全仓零脚本引用(仅 canonical 透传+注释)——
  无需迁移, 语义陷阱已由注释覆盖

### 📐 P2 清单实施(用户批准)
- **val 策略25【PS低估值】**: fuyao valuation 批量(市值 top500 预筛控配额)——
  PS(TTM)≤全市场20分位 且 PCF>0; PE 失效标的(高毛利未盈利/轻资产)替代估值锚;
  注册表/_sfmt/计数文案 24→25 同步
- **lng 历史高点前复权切换**: 新增 sc_datasource.get_historical_high_qfq
  (腾讯 ifzq fqkline, ~640 根≈2.6年窗口, 字典 §12.1 备胎接口);
  get_historical_high wrapper 改 qfq 优先/TDX 不复权兜底, 渲染口径注同步。
  实测: 600519 qfq 高点 1806.54 → 真实回撤 -29.6%(旧不复权口径虚报 -52%
  误触"长线黄金坑"信号); TDX 周末 None 时 qfq 主路径天然韧性强于旧实现

### 🔗 统一层 fallback 链修复(盘后字段可用性)
- **roa/roe_deduct_ttm 盘后恒 0 修复**: 原 `need_realtime_quote` 门控导致休市日
  rt_quote={} → 盈利质量对(腾讯 tx65/tx66)盘后报告恒 missing。去门控后
  tencent extras 补取无条件执行——实测周六 600519: roa=27.3/roe_deduct_ttm=32.41 ✓
- **ps_ttm/pcf_ttm 入 canonical**: fuyao valuation 独有维度(ps_ttm/pcf_ttm)补入
  sc_schema CanonicalStockData + data_provider 构造; fuyao valuation 补取条件
  扩为 pe_ttm 或 ps_ttm 缺失即触发(原仅 pe_ttm); 实测 9.46/13.76 ✓
- **source_tag 判定修正**: 原 `and rt_quote` 在财务字段补取后恒真 → 熔断/盘后
  误标 http/tdx(测试 test_graceful_circuit_breaker_fallback 捕获); 改为只看
  `rt_quote.get("price")` 是否来自实时源

### 🧹 全仓 Bug/死代码审计(AST 扫描 66 文件/1269 函数)
- **死代码清理 4 处**: zhb_client.should_use_zhb_data(53 行, V15 遗留时机判断——
  ZHB-First 路由已由 data_provider REQUIRES_REALTIME_HTTP/ZHB_SUFFICIENT 取代)、
  f10_parser.extract_field(通用正则工具零调用)、sc_datasource.get_zhb_52w_range
  (V9.6 遗留——52 周已由 high_52w/low_52w 多源链取代)、conftest.tmp_project
  fixture(零测试引用)。删除后残留引用核查干净+py_compile 全过。
- **Bug 模式扫描零命中**: 裸 except/吞异常 0、可变默认参数 0、async 内
  time.sleep 0、requests 无 timeout 0; 本会话新增高危点作用域验证通过
  (sht _seal_info 跨段同函数/mak _dt_count A→B 段同函数)。
- **甄别说明**: 17 个"仅测试引用"生产函数(get_sw_industries/get_ah_stocks/
  日历族等)保留——属防退化测试覆盖的基础数据接口, 非死代码;
  print 输出集中于 GD 上传/批量 Runner/CLI 引导等用户可见交互层, 属设计选择。

### 📚 参考仓库同步核查(simonlin1212/a-stock-data v3.6.0→v3.7.1)
- P0 五项高危模式逐项核查: mootdx frequency 参数✓/解禁新列名✓/龙虎榜空窗口✓/
  EPS 均值列✓/历史高点不复权 ⚠️→lng 渲染加除权口径警示行(数据源切换待办)
- v3.7.0 新端点择要入典: 估值历史日频序列/复权因子 qfq·hfq/上市退市日/申万行业变迁史/
  CYQ 本地推演法; 宏观层暂不需要; 模式入典: 后缀静默错票(v3.7.1)/ETF 不覆盖个股资金流(#46);
  基线版本注释 V3.6.0→V3.7.1

## [17.0.4] - 2026-08-19

**历史报告深度核查修复 + 数据采集体系完善 + 新字段破解 + GD 补传**

### 🐛 数据修复(历史报告核查驱动, 8/17-8/19 63+39 份 md 全量对比)
- **mak 近3日异动回溯 3日偏离恒 0.00%**: TDX 路径 ret_3d 硬编码 0.0(V16.1 因 ZHB 未破解 1d/2d 移除, 现已破解)
  → `tdx_client._calc_ret_3d_snapshot` 恢复真实复利(实测 300862: 0.00→66.78%)
- **ZHB 路径腾讯覆盖分支 3 日窗口错位**(漏 T-1, 窗口 T/T-2/T-3): `_calc_3d_from_daily` 覆盖分支改取 Col[6]/[7]
- **北向资金冻结**(8/12-8/19 恒 -9.28/+379.75, 47 份报告全同): 同花顺接口 hgt(262 分时点) vs sgt(35 历史点)
  **序列错位** → `get_hsgt_macro_flow` 判 invalid 拒绝展示, sht/med/mak 三处消费点改"数据源异常, 净流入暂缺"
- **跌停 0 不可能**: 东财 `getTopicDTPool` 明细接口 tc>0 但 pool=[] 空(8/17/8/18 实测) →
  `get_limit_pool_summary` 用 ZHB 快照涨跌幅口径兜底(验证 0→2); mak B 段进一步无条件用 A 段当日 `_dt_count`
- **历史资金流仅 1 天**(8/18 全仓 35 份): `_FFLOW_HOSTS` push2delay 排第 1 截断历史请求 →
  `_em_fflow_request(prefer_his=True)` push2his 全窗口优先(实测 60 天)
- **指数多周期收益静默 None**(严重/卡异动判定失效): `get_index_returns` 加**新浪日K兜底**
  (quotes.sina.cn getKLineData, 与腾讯 ifzq 实测一致 <0.01; scale 支持分钟/日/周/月, OHLCV+amount)
- **sht/med 格式**: sht `➤ [板块共振监测]/[市值排名]` 括号拆分小节+内容; med 两融 4 处 ➤ 信息行去标题化;
  md_render 标题 `## **X**`(des2 全局替换误伤)→ 归一 `## X`
- **zhb_sync 校验误报**("tdxstat=0 条"假警告): 下载后惰性解析未触发 → `_validate_zhb_data` 强制访问 property

### 📤 GD 补传工具
- `reports/reupload.py`(gitignore 例外入库): 按日期核查未上传 md 批量上传; 已上传同名跳过;
  瞬时波动 30s 重试 2 轮; 名称从一章"股票名称/企业名称"提取(39 文件 0 缺失)

### 🔍 字段破解(采集 20260819/20260820, 20 股横截面)
- **push2 f50=量比**(20/20 与腾讯[49] 完全一致)、**f182=市场类型枚举**(主板2/创业5/科创32/北交80)、
  **f198=东财板块代码**(BKxxxx)、f121/f122=资金流衍生(与腾讯[71]/[62] 同源)
- 腾讯 [65]/[66] 静态排除项确认、f86 全局计数无信息量; ZHB tdxstat 全破解无新未知
- 字典登记: field_dict 12.3.1 正式表 + §零·B 矩阵重生成(914→920 字段) + script_data_dict 2.1

### 📦 采集与数据
- capture_field_probe 20260819(17 源 402s, thsdk 非交易时段 0KB 已知)/ 20260820(18 源 362s, ZHB=8/19)
- ZHB 8/18 包同步(zhb_sync, 7994 只); 8/19 报告核查: 章节全完整/数据逻辑 0 异常/000657 三报告交叉一致
- 回归 269 passed 持续通过

## [17.0.3] - 2026-08-17

**md 报告格式整体规划 + 数据修复 + 风控优化 + 离线预览工具**

### 🎨 md 排版整体规划(平面设计师视角, 摆脱 txt 遗留)
- 标题 ## 【X】/## [X] → ## X(去括号); ➤ 小节 → ### 三级标题; ├─/└─ 树形 → md 列表
- 表格渲染修复: 表格前+后双向空行(4 出口统一)——"标题被并表/表格未渲染"根因
- **#N** → **N.**(渲染器 # 高亮红色消除); 涨停板块分布竖排(避开表头加粗)
- 头部拆分(报告名/时间+时段分行)+ 报告名加粗; 时间 %H.%M.%S(分钟红色消除)
- 字段值对齐块 → 2 列表格(行内多字段拆分); 状态行(emoji)不转表; 独立分隔线去除
- 表格使用原则: 多列数据用表格(明细/天梯/轮动/资金/财务/席位/北向/两融/大宗/股东户数);
  枚举/状态/提示竖排文本; 单列行移出表格(rest 截断)

### 🐛 数据与逻辑修复
- 虚涨段恒空根因: 主力批量段仅在 ZHB 路径执行, 盘中 TDX 路径不跑 → 上移两路径统一
  (A 段 ulist f62+f66 真主力口径, 虚涨段恢复)
- 涨停天梯失败: 开盘红日期 今天-1(周一取周日空) → 最近交易日+向前找
- 同花顺独家/大宗交易/席位/股东户数/ROE 表 空格粘连 → 脚本直接 md 表格
- fflow 域顺序 push2delay 优先(策略20 逐股不再先打 push2 主域, 封禁风险源)
- val 策略展示 5→10 只; _top5_sorted → _top10_sorted 正名

### 🛠 工具与工程
- scripts/fmt_preview.py: 零网络格式预览(重转报告/喂模拟行)
- 删 20 死函数+8 未用 import(三轮全仓核查闭环)
- 回归 269 passed 持续通过

## [17.0.2] - 2026-08-16

**修复: 休市行情 OHLC 缺失 + 涨停池源切换 + 表格原则定稿 + 三轮全仓审查闭环**

### 🐛 数据修复(canonical)
- 休市/盘前 OHLC/成交额恒 0: _extract_with_source 去 need_realtime_quote 门控 +
  zhb_default 修复(amount 键名不匹配) + prev_close 反算(price/(1+chg), 加 0.5~2x sanity) +
  TDX 本机 .day 兜底(get_tdx_day_tail, 零网络) + 批量命中 TDX 补缺
- 盘口异动涨幅恒 0(levistock 字段 i 解析错误) → 修复后按用户原则**移除采集**(sht/mak 零 push2ex)

### 🔄 涨停池源切换(同花顺优先 + push2ex 兜底)
- ths_limit_up_pool 升格优先源: 空日期回退最近交易日; 17 字段(原因/板型/封板率/炸板次数/
  换手/流通市值/封单量/末封/回封/市场类型/新股, 一次请求零额外压力)
- 板块分布: TDX 本机 tdxhy 一级行业注入(零网络, 进程缓存); 炸板/跌停池保持东财
- 缓存 category 升 limit_pool_v2(字段变更强制失效); mak 封板时间双键兼容;
  休市日三池日期口径统一(封板率 100% 假象修复)

### 🎨 表格原则定稿(用户)
- "字段: 值"竖排(基本信息/行情/估值)不表格化; 仅横向数字列对齐章节(同业/资金/龙虎榜)用表格
- sht/lng 表格回退; 上市日期唯一来源 list_date

### 🔍 三轮审查闭环(2H+10M+11L, 20 死函数清零)
- med 板块内排名 NameError(永久静默失效)修复; mak 资金流验证段覆盖行删除
- 研报 None 崩溃/EPS 守卫 >=4/解禁单位统一(F10 万→股)/val 策略14 单位分键/
  to_thread 14 处/死 import 8 处/backtest 死函数
## [17.0.1] - 2026-08-15

**补丁: 字段增强实施(P0-P4) + 三轮代码审查闭环 + 全量 md 化 + 运行修复**

### 🆕 字段增强(P0-P4, 基于已破解字段池)
- **mak**: 主力净额 ulist 批量 f62+f66(=f137+f140 特大+大单, 20/20 实锤, push2delay 域, 元口径带符号)→
  板块聚合/A 段看板同源; 北向宏观资金(to_thread+降级标记)
- **sht**: 连板追踪 ZHB[31] 真连板数(双日铁证)+涨停类型[33]+官方封单额[4]; 3日涨幅估算降兜底
- **val**: 21→23 策略——策略22 业绩预增(get_yjyg_all 全市场分页, ADD_AMP/IS_LATEST/日期缓存)+
  策略23 盈利预期(本机 ProfitForecast O(1) 索引+股东户数 local_only)
- **lng**: 机构一致预期(本机 ProfitForecast 优先)
- **数据层**: zhb_client 暴露涨停族; get_em_batch_quotes +f62/f66(secids 参数修复);
  get_eps_forecast 本机索引+local_only; get_yjyg_all; eastmoney_datacenter page_index

### 🐛 三轮审查修复(2×python-reviewer + 运行复盘, 50+ 项)
- **CRITICAL 类**: mak 主力单位 1e4 倍; data_provider TDX 兜底 T-1 单位 10000x;
  med 北向占比 100 倍; get_eps_forecast 缓存失效+5000 次扫描; ulist 参数 fs→secids(data:null);
  **val bypass 模式 price 全缺 → 10 策略 0 命中**(.day 尾部快速读补价, 终审修正 ÷1000→÷100);
  mak A 段 ZHB 兜底单位; GD 补传脚本 .md 适配
- **限流**: get_em_batch_quotes push2 主域→push2delay 镜像域; get_yjyg_all 全市场一次分页;
  strategy_23/holder_change local_only 禁网络; mak/val async 阻塞 to_thread 4 处
- **缓存**: ProfitForecast O(1) 索引+锁; 业绩预告日期缓存; _KLINE_PRICE_CACHE
- **契约**: holder_num/ADD_AMP/IS_LATEST/zt_type 0 值 等

### 📝 全量 md 化(C 方案)
- 新增 stock_common/md_render.py 渲染层转换器(标题/分隔线/F10 边框表/空格表数据驱动切分/安全回退);
  5 脚本写尾 render_md_report, 输出 .md(纯文本兼容); val [NN 名称] 标题支持

### ✅ 回归
- 269 passed / 45 deselected, 0 failed

---

## [17.0] - 2026-08-13

**里程碑：全盘重构(core/ 包化 + v9.6 清理) + 字段命名规律破解 + 运行核查修复。**

### 🗂️ 目录整理
- 7 支撑模块包化 `core/`(全仓 ~150 import 统一 `from core.X`, `__init__.py` 空防循环, CLI 改 `-m`)
- v9.6 遗产清理(目录/SKILL/3 对比工具/孤儿 db); 凭据归位 `credentials/`; README 体系补全(45 条目→分层)

### ♻️ 代码重构(S1-S8)
- **S1 死代码 ~1000 行**: 21 zhb 转发+sc_zhb+12 dp 包装+composite 链 220 行(__all__ 255→230)
- **S2 传输层统一**: _request_with_retry→_quick(别名+4 点迁移); _async_quick EM/GEN 分流(限流语义保留); 进程间隔 2 核心+4 薄包装
- **S3 市场代码**: em_secid_prefix(修北交所 92 secid bug); is_a_stock 下沉; _market_code 补沪 B
- **S4 数据源合并**: getharden 三版合一(get_ths_hot_raw 唯一入口); cninfo 公告下沉(keywords 参数)
- **S5/S8 样板**: 写尾/ST 标注/多评委(sc_render)公共化; 缓存适配器删除
- **批量骨架收敛**: 基类 `execute_batch_pipeline`(prefetch/快照/上传钩子); ts 基类统一

### 🔬 字段字典破解(命名规律: 拼音/英文/中英混合)
- **双源实锤 20+ 组**: ConZAFDateNum=streak_days、ZAFYear/Pre20/Pre60=ytd/20d/60d、Yield/OpenAmo=主力净流入(双单位)、
  gb_info Zgb/Ltgb 股本、f137-146 四档资金流全定位、f162=动态PE/f163=静态PE(TTM)(茅台 Q1 年化精确)、
  f174/f175=52周(腾讯 [67]/[68] 三源一致)、f191=委比%(原"×100"修正)
- **"N日"口径实锤**: change_5d-60d/ytd 全交易日(开盘日)口径(日K 精确匹配); change_30d=历史遗留 key(实为 20 日值)
- **tdxstat2 [4]/[6]/[8]=涨停封单额三日滚动**(涨停池 92/92 全覆盖); 21 列全映射
- **通达信行业体系**: 细分行业=X 码(名称≈申万三级); ZHB [13]=881 行业板块/880 概念·风格双段; 地区不在 ZHB
- **vzangsu=量涨速%(TDX 表头同名实锤)**; ZAFPre 系列口径(PreN=交易日区间/D=当日/MyMonth=上月最后交易日)

### 🧪 统一层与运行修复
- 主力净流入**全链统一 f137**(腾讯 tx75 反向警示入字典); PE 动态=f162(腾讯静态剔除); 行业仅认 881 段(防 880 概念污染)
- main.py 固定超时→**输出活性检测**(持续输出无限等待, 无输出 900s 判卡死); sht 上传与 med/lng 统一
- 性能: prefetch 命中跳过 TDX; push2delay 补取进程缓存(同股二次 2.3x)
- 测试隔离: conftest 补拦 Session.get/post
- script_data_dict.md 全量重写; 全量回归 **302 passed / 45 deselected, 0 失败**

> 详细执行轨迹: docs/V17.0_REFACTOR_PLAN.md / docs/field_verification/20260813/(analysis+映射表) / docs/session_notes/20260813.md


## [16.4.1] - 2026-08-12

**里程碑：字段实测验证流水线落地 + TdxQuant 官方 88 字段交叉破解 + 报告数据质量 19 项修复 + 编码体系治本。**

### 🎯 字段验证流水线(每日记忆锚点体系的实证来源)

- **固定股票池** `docs/field_verification/pool.json`：20 股(固定 15 + 动态 5,沪深/创业/科创/北交所/ST/银行/连板全覆盖)
- **采集脚本** `scripts/capture_field_probe.py`：19 源全字段(本地 ZHB + TDX/F10 + 腾讯 88 + push2 114 + ulist 239 + 新浪 34 + AxData 34 + 财联社/KPL/板块轮动/涨停池/人气榜/datacenter/巨潮/研报/thsdk/TdxQuant)
- **首次采集** `docs/field_verification/20260812/`：19 raw 文件 + meta + analysis + field_analysis
- **防封**:push2 失败不重试 + 连续 3 只失败域级熔断切 push2delay(2026-08-12 二次封禁复盘根因:失败连接重试叠加 ~300 次)
- **sc_datasource.em_hot_rank** push2 → push2delay 镜像域(封禁期整体失败修复)

### 🔬 TdxQuant 官方对照破解(通达信客户端 PYPlugins tq 库,18 只全样本)

- **18/18 实锤**:Col[3]=StaticPE_TTM(pe_dynamic 历史遗留名)、Col[9]=MorePE、Col[10]=DYRatio、Col[14]=KfEarnMoney、Col[15]=StaffNum、Col[24]=CashZJ(**单位=万元,原"(元)"错误**)、tdxstat2[16]=IPO_Price、[17]/[18]=HisHigh/HisLow
- **破解**:tdxstat [26]=YearZTDay 年内涨停天数(18/18)、[32]=LastZTHzNum(2/2)、[31]≈LastStartZT、[23]=当日异动类型码、tdxstat2 [4]/[6]/[8]=同一资金字段三日滚动序列(T/T-1/T-2)、tipinfo [10]=DTDate_Recent
- **tipinfo 官方字段名实锤**(600519 单样本):Col[5]=ZTDate_Recent、[6]=TopDate_Recent、[13]=RecentReleaseDate、[19]=RecentHGDate
- **采集**:`C:\new_tdx64\PYPlugins\user\field_verify_tdxquant.py`(需通达信客户端运行)
- field_dict.md 全量回写 + 精简(多轮测试描述压缩为"含义+状态+一句证据")

### 🐛 核心 Bug 修复

- **ZHB 下载永不更新**:`_zhb_needs_download` 循环依赖(stock_calendar.is_workday 反向调 get_zhb → 递归爆栈)→ 改用本地包节假日表;+"每天最多下载一次"标记(成功才标记)
- **val 崩溃 KeyError('zhangfu')**:get_val_report L1880 复制粘贴残留(`_th["zhangfu"]` 在 elif 分支必崩)

### 📊 报告数据质量修复(19 项,基于 41 个报告文件逐份审查)

- **sht GD 丢失**:36 只批量超时被 kill 时批量上传未执行 → 改**逐只上传**(提前 init_gd,生成即传)+ main.py 单股超时 30s→45s
- 封板时间 "92:50" 格式错(5 位字符串切片)→ 统一 int 解析
- 新股首日无涨跌幅限制(+662%)→ mak 上市<3 日跳过偏离判定 + val 标注
- sht 主力资金占比 222%(abs 掩盖方向)→ 保留符号+超成交额异常标注+来源标签修正
- 北向 degraded 警告未展示(深股通 379 亿异常)→ sht/med 渲染 data_quality 警告
- med 资金流仅 1 天却下"吸筹"结论 → <5 天数据不下中线结论
- lng:人效比单位 元→万元、PE-TTM 来源口径标注、PEG 跨期标注、分红"距今 N 年"、互动易答案 None、净利率>100% 双源核验标注
- val 策略09 名称当代码(昀冢科技 (昀冢科技))→ 无 6 位代码 leader 走成分股路径
- med 同业本股 *ST 名称统一;同业亏损股 PE 显示"亏损"(原 0.0)

### 🛠 工具与规范

- **GD 补传工具** `scripts/upload_reports_to_gd.py/.bat`(reports/ 自包含副本):已存在跳过只传缺失,实测 39 上传/6 跳过/0 失败
- **编码体系治本**:
  - Python 入口全量 `ensure_utf8_stdio()`(env_setup.py 下沉,17 入口)
  - .ps1 四行 UTF-8 头部 + **BOM 铁律**(PS 5.1 无 BOM 按 GBK 解析)
  - **管道禁令**:禁止 python 输出接 PS 管道(PS 5.1 分块解码破坏多字节字符,实测根因)
  - bat 纯 ASCII+CRLF 铁律(cmd 按 ANSI 解析 UTF-8 中文注释致整文件错乱)
- **AGENTS.md v1.2 重构**:合并落盘规则、清理过时内容/已完成待办、修正 bash grep/废弃变量引用
- **每日会话纪要体系**:`docs/session_notes/YYYYMMDD.md`(详见 docs/session_notes/README.md)



**里程碑：字典架构重构 + 三大客户端逆向（东财/通达信/同花顺）+ 统一层加固 + 场景化批量优化。**

### 🔧 字典架构重构（主字典=决策层，附录=实证层）

- `docs/verify/` 附录目录：主字典只留结论，实测值/样本/破解数据迁入附录
  - push2_verify（12.9.1 全字段破解表）/ axdata_verify（666 字段矩阵）/
    samples_verify（24 股样本）/ tencent_verify（88 字段复核）
  - field_dict 358KB→284KB（-21%）；12.15.9 附录索引表
- **script_data_dict 全量重构**：5 脚本行号重定位（mak 1798/val 2131/sht 1740/med 1256/lng 1135）
  + 逐字段 fallback 链实测更新 + §七 12 项断点（8 项已修）
- **客户端逆向三附录**（统一 docs/verify/）：
  - `network_servers.md`：三源服务器清单（通达信 connect.cfg 全表 HQHOST 43/
    同花顺 123ths 域名族 9 域 ~80 IP/东财 SSO）+ 移动线路实测
  - `client_fields_enum.md`：客户端字段枚举全景（东财 950+/通达信 tdxstat
    35 列破 14/tdxstat2 21 列破 13/同花顺 F10 文本+thsdk 口径铁证）
  - 数据文件入库 `docs/verify/data/`（connect_cfg/dns_cache/复测结果）

### 🐛 脚本断点修复（8 项）

- mak：9.5 涨停分档×3 统一 limit_pct_for、板块 mcap_yi 腾讯注入+计算兜底、
  main_net_amount 取 ZHB、盘口异动死代码移除
- val：_sfmt 01-21 映射重建（14 号回归）、行业排名升级 O25（四脚本收敛唯一实现）
- sht：地天板预警 limit_down_price 修正、ff.iloc 死分支、**bid1_vol 入 canonical
  全链路**（封单资金/信号/预警复活）、_is_dict 死分支清理
- **PB 口径统一**：val 04 pb_ths 降级校验，全脚本收敛 canonical（腾讯/push2
  除息口径），THS 静态口径仅差异告警

### 🔍 客户端逆向发现（服务器 + 字段 + 铁证）

- **通达信 tdxstat/tdxstat2 官方原始文件 35/21 列破解**：ipo_price（茅台 31.39）、
  52周高低（=腾讯精确）、PE 双口径（Col[3]=动态/Col[9]=TTM 实时验证）、
  涨跌幅序列（5/10/20/30日 + ytd 多股全中）、amount_1d/2d（昨日/前日成交额）
- **同花顺**：123ths 域名族、stockname 名称库、F10 文本库（五期财务）、
  **thsdk 市净率=现价/最新期 BPS 铁证**（F10 文本 4 位小数精确）、
  get_ths_market_snapshot query_key 修复（汇总→扩展1）
- **TDX 服务器 74 台复测**：FULL 6 台（新增 120.76.152.87），白名单更新
- 东财 DataCenter.dll 725 协议字段 + 自选 118 字段三层映射

### 🛡️ 统一层加固（回应"规范管不住持久状态"）

- **share_capital 旧单位 bug**：6467 条"股"单位缓存（V16.2.3 修正前 8-03 批次）
  导致 canonical mcap 放大 1e4——清理 + **缓存 schema 版本化**（规范变更自动失效）
  + **canonical 量级校验**（股本>1e7 自动股→万、mcap>1e6 自动万→亿，与 pe 过滤对称）
- zhb_client tdxstat 映射与 12 股 F10 验证 100% 吻合（统一层无需改代码）
- 缓存同步：tdx_hosts_cache 6 台 FULL

### ⚡ 场景化批量优化（sht 30 只核心需求）

- **prefetch_quote_batch**（push2delay ulist 300/批）：sht 批量 1-2 次请求预取
  30 只核心行情，canonical 命中跳过 TDX 逐股；估值字段按需腾讯单股补齐
  （实测 ulist 不返回估值字段）
- 矩阵增加场景维度：单股深度（TDX 优先）/ 批量行情（ZHB+腾讯批量）
- UA 补全标准浏览器指纹（5 处）+ 东财 IP×子域封锁排查（push2 系与 delay/ex 独立）

### ✅ 验证

- 全量测试 339 passed, 2 skipped（多次基线一致）
- 东财接口健康探测脚本 `scripts/check_em_health.py`（低频防封锁）
- AGENTS.md §12 活跃待办（push2his 恢复复测提醒）


### 近期版本(V16.3-V16.2, 详细内容见 docs/session_notes/)

- **[16.3.8]** (2026-08-11): 东财 IP 封锁排查 + 新 IP 恢复核验（换光猫后）。
- **[16.3.7]** (2026-08-11): PB 口径统一：val 04 双通道收敛（回应统一层设计初衷）。
- **[16.3.6]** (2026-08-11): PB 多源实证归因 + THS 批量通道修复（盘中三股实测）。
- **[16.3.5]** (2026-08-11): 行业排名统一收敛 O25 + 资金流单位契约清理（回应字典 §七 剩余项）。
- **[16.3.4]** (2026-08-11): 脚本断点修复 8 项（script_data_dict §七 12 项中 8 项落地）+ bid1_vol 入 canonical 全链路。
- **[16.3.4]** (2026-08-11): script_data_dict 全量重构：5 大脚本按当前代码重定位（ful 删除确认）。
- **[16.3.3]** (2026-08-11): 字典架构重构：主字典=决策层，附录=实证层。
- **[16.3.1]** (2026-08-06): V16.3 O 系列：F10 财务接入 + 字典全面破解 + 东财限流治本 + 统一层梳理。
- **[16.3.0]** (2026-08-05): 全项目审查整改（74 文件核查，用户批准全改）+ 文档/依赖清理。
- **[16.2.0]** (2026-08-05): V16.2.1-V16.2.18 连续迭代：报告正确性 + 东财分域限流 + 缓存版本化 + 行业统一申万二级 + ZHB 字段破解。

### 历史版本归档(V16.1 及以前, 详细内容已归档)

| 版本 | 日期 | 里程碑 |
|:---|:---|:---|
| 16.1.9 | 2026-08-05 | ST 涨跌幅规则修正（5%→10%）。V16.1.7 曾误按 AxData 文档旧快照 `st_5pct` 将 ST 阈值改为 5%； |
| 15.4.3 | 2026-07-31 | easy_tdx 字段探测 + tdx_field_dict 字典 + V15.5 移植规划。基于用户反馈"全部更换为 mootdx 接口后数据获取并不稳定"，调研 [easy_tdx v1.20.4 |
| 15.3 | 2026-07-29 | 全量健康修复版本。基于 2026-07-29 跑 000100 时的全量根因分析（X1-X8 共 8 个 P0/P1），结合第三方 deepseek 评审报告的逐条核查，对剩余 9 个 P0/P1 + |
| 15.2 | 2026-07-28 | P0 崩溃修复 + 缓存保护强化 + ZHB 交叉验证恢复版本。基于 2026-07-28 20:29 批量运行日志的深度根因分析，重点修复 V15.1 引入的 `board` 变量未初始化导致的 3 |
| 15.1 | 2026-07-26 | 全全局 ZHB 旁路普及与并发线程池隔离深化版本。将基于真实周期的 ZHB 时空路由矩阵全面普及至 6 大报告脚本（`sht`/`med`/`lng`/`ful`/`mak`/`val`），修补盘后  |
| 15.0 | 2026-07-26 | 标准化数据中心与 ZHB 离线优先架构重构大版本。完全收敛多源行情异构数据，引入强类型数据合约 `CanonicalStockData`，实施基于真实生成周期（T+1 清晨 06:00 前）的 ZHB |
| 14.0 | 2026-07-22 | V13.x Bug 修复 + 文档全量同步版本。不引入新功能。 |
| 14.2 | 2026-07-22 | ZHB 数据集深度集成版本。基于 `field_dict.md` 第三节第 4 小节新挖掘的 6 个 ZHB 数据集（profile.dat / tdxchain.cfg / neednote.dat |
| 14.2.1 | 2026-07-22 | Gemini 深度静态分析后修复的 3 个边界隐患 + 1 个架构一致性提升。不改变 VERSION 编号（仍是 14.2）。 |
| 14.3 | 2026-07-25 | 性能优化版本。针对 val 报告周日首次跑 15 分钟卡死的实际问题，从 P0/P1/P2/P3 四个层面完整解决"网络请求风暴"问题。 |
| 14.3.1 | 2026-07-25 | 根据用户对缓存机制的两点深入分析，对 V14.3 缓存架构进行精细化重构。不改变 VERSION 编号（仍是 14.3）。 |
| 14.3.2 | 2026-07-25 | Top-N 数据驱动回测。用 4 天 ZHB 数据（cache/zhb/zhb_202607{21,22,23,24}）回测 12 个策略在不同 top_n 下的选股质量，给出"按策略差异化 top_ |
| 14.2.2 | 2026-07-25 | 针对 Gemini 报告的两个实际运行异常（`val` 脚本 `NameError` + `mak` 脚本 `0只` 与卡死），进行深度根因修复。不改变 VERSION 编号（仍是 14.2）。 |
| 14.2.3 | 2026-07-25 | V14.2.2 的修复不完整——`_check_tdx()`（健康检查函数）仍使用 `bestip=True`，导致 val 报告（`strategy_10_contrarian_value` 调用  |
| 13.2 | 2026-07-22 | 无重大破坏性变更。V13.2 仅追加文档与脚本。 |
| 13.2 | 2026-07-22 | V13.0/V13.1/V13.2 三阶段引入 dataclass 形式的数据容器，作为 V12.x dict 的可选升级路径。 |
| 13.0 | 2026-07-22 | 无重大破坏性变更。V13.0 仅新增 `stock_common/sc_schema.py` 模块，不接入 data_provider。 |
| 13.1 | 2026-07-22 | V13.1 涉及缓存层行为变化（潜在影响）： |
| 12.6 | 2026-07-22 | V12.6 取消原计划的防投毒熔断机制（V11.5 时期实施），存在以下行为变化： |
| 12.5 | 2026-07-22 | V12.5 针对 V12.4 复盘发现的 3 大问题进行修正：消除 `get_med_report.py` / `get_lng_report.py` 中重复定义的 Runner 类、让基类 GD 上 |
| 12.3 | 2026-07-22 | V12.3 原计划引入三项深度架构演进，但在评估后决定挂起，未实际实施： |
| 12.4 | 2026-07-22 | V12.4 成功构建并全面应用 `BaseReportRunner` 引擎框架，彻底剥离6大策略报告脚本中约 1200+ 行重复的 CLI 解析、运行生命周期 Banner、Google Drive  |
| 12.2 | 2026-07-22 | V12.2 完成工程化优化任务清单，包括数据库连接优雅关闭、配置集中管理、全局异步Session单例、核心防线单元测试、三级日志规范落地。 |
| 12.1 | 2026-07-22 | V12.1 针对全量代码审查发现的问题进行修复，包括 L1/L2 缓存同步 Bug、静默异常日志化、容错层实际下沉、异步阻塞修复、未使用导入清理。 |
| 12.0 | 2026-07-17 | V12.0 完成 TCP 统一层重构，彻底删除 easy_tdx 依赖，实现"HTTP + mootdx"双通道架构。所有原 easy_tdx/MacClient 独有功能（板块、资金流、全市场快照） |
| 11.5 | 2026-07-17 | 历时多个版本规划，data_provider.py 统一数据中心层在 V11.5 正式全面激活，六大报告脚本全部完成迁移。同时新增三大防封机制，彻底提升网络稳定性。 |
| 11.4 | 2026-07-16 | 1. data_provider.py死代码清理：6个报告脚本（sht/val/med/lng/mak/ful）共47处`from data_provider import (...)`导入语句全部删 |
| 11.3 | 2026-07-16 | 通过7/15 vs 7/16报告对比发现，4个缓存分类在跨日运行时携带T-1数据混入T0报告： |
| 11.2 | 2026-07-16 | - clean_codes增加flag粘连警告：当股票代码参数中包含`--`时（如`601718际华--all`缺少空格），打印警告提示用户检查命令行格式，避免`--all`参数被误解析为股票代码 |
| 11.1 | 2026-07-16 | 1. 全市场成交额实时覆盖：val脚本加载全市场数据时，用腾讯实时行情的`amount_wan`覆盖ZHB的T-1成交额，确保流动性排序和策略计算使用当日数据 |
| 11.0 | 2026-07-16 | - 所有报告脚本统一导入 Data Provider 模块： |
| 10.3 | 2026-07-16 | zhb 资金流向字段解锁（基于 zhb_analysis 深度分析 + 双日 Delta 验证 + 公式验算）： |
| 10.2 | 2026-07-16 | - 修复 cross_verify 读写互斥BUG（影响14个分类：concept_blocks/lockup_expiry/basic_info/financial/balance_sheet/ca |
| 10.1 | 2026-07-15 | - zhb字段映射重大修正（基于injoyai/tdx开源仓库源码验证）： |
| 10.0 | 2026-07-14 | - zhb全局配置总包全面升级： |
| 9.6 | 2026-07-13 | - mootdx依赖集成：`requirements.txt` 新增 `mootdx>=0.11,<1.0`，与 easy-tdx 形成互补关系 |
| 9.5 | 2026-07-13 | - 静默异常日志化（28处）：`tdx_client.py`（23处）、`gd_uploader.py`（4处）、`get_med_report.py`（1处）共28处 `except Excepti |
| 9.4 | 2026-07-11 | - VERSION文件单一来源版本号管理：项目根目录新增 `VERSION` 文件（内容为 `9.4`），`stock_common/sc_utils.py` 新增 `get_version()` 函 |
| 9.3.3 | 2026-07-10 | - GD上传路径混乱：`get_or_create_drive_folder` 增加 `'{parent_id}' in parents` 严格约束，`get_val_report.py` 移除 `g |
| 9.3.2 | 2026-07-09 | - TDX K线假数据导致指数涨幅全N/A和异动检测全为0：约50%的 easy_tdx 内置TDX服务器K线接口返回假数据（响应头 `ret_count=800` 但 body 为 0 字节），导致 |
| 9.3.1 | 2026-07-08 | - sht 脚本 `'float' object is not subscriptable` 崩溃：`ff["data"]` 存在多态（TDX 返回 `List[dict]`、东财 fallback  |
| 9.3.0 | 2026-07-07 | - 盘前行情模式（`tdx_client.py`）：9:30前自动使用上一交易日日K线数据，避免实时接口返回 0 导致涨跌幅计算为 -100% |
| 9.2.0 | 2026-07-05 | - 缓存交叉验证机制（`stock_cache.py`）：11 个多天 TTL 分类启用 `cross_verify=True`，两次获取数据一致才标记为已验证，防止意外错误数据被缓存 |
| 9.1.1 | 2026-07-04 | - ful 评分 theme→holder 映射 bug：`get_ful_report.py` 中 `_scoring()` 返回值用 `"theme"` 作为键名，但实际取自 `dims.get( |
| 9.1.0 | 2026-07-04 | - F10 全覆盖工程：用通达信 F10 协议替代/补充现有 HTTP 接口，降低东财限流风险，详见 `docs/TDX_F10_ROADMAP.md` |
| 9.0.0 | 2026-07-02 | - 舆情互动层（Layer 10）：新增 `cninfo_irm()`（互动易问答）、`ths_hot_list()`（同花顺热榜）、`em_hot_rank()`（东财人气榜）、`em_hot_co |
| 8.9.0 | 2026-06-29 | - 版本号统一升级：所有脚本版本从 V8.8/V8.7 统一升级到 V8.9 |
| 8.8.0 | 2026-06-25 | - GD上传逻辑统一化： |
| 8.7.0 | 2026-06-25 | - 删除 `social_sentiment.py`（6 平台社交热榜聚合，全为桩实现返回空数据） |
| 8.6.0 | 2026-06-24 | - stock_common.py：新增 _DOMAIN_LAST_TIME 线程锁保护，彻底消除多线程竞态条件 |
| 8.5.0 | 2026-06-22 | - 新增龙虎榜席位增强模块 `seat_db.py`： |
| 8.4.0 | 2026-06-22 | - 新增 `stock_cache.py` 统一缓存层（SQLite + TTL 自动过期 + LRU 清理） |
| 8.3.0 | 2026-06-18 | - 修复北向资金持股占比显示超100%问题（`get_sht_report.py`/`get_med_report.py`中`_ratio*100`改为`_ratio`，东方财富API返回的`hold |
| 8.2.0 | 2026-06-18 | - 修复 `300274` 等股票因 lines 列表中存在 None 值导致 `join()` 报错的问题（在所有脚本的 `join()` 调用前添加 `filter(None, lines)` 防 |
| 8.1.0 | 2026-06-18 | - 新增统一评分接口：`ScoreData` 数据结构、`ScoreResult` 结果结构、`calculate_score()` 主函数，统一管理 sht/med/lng/ful 四种评分类型的计 |
| 8.0.0 | 2026-06-17 | - 初始版本，包含6个报告脚本（sht/med/lng/ful/val/mak） |
