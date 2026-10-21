# 项目静态上下文（PROJECT_CONTEXT）

> 用途：提供稳定架构、关键约束与文档路由；任务开始时按 §0 读取相关文件，不重复加载全仓历史。
> 维护：结构、入口或稳定流程变化时更新。字段语义以 registry/裁决证据为准；运行结果以当次产物为准。
> 更新日期：2026-10-21（`VERSION`：17.5.11）

## 0. 任务路由

| 任务 | 先读 | 按需读取 |
|---|---|---|
| 日常采集与碰撞 | [`field_verification/DAILY_RUNBOOK.md`](field_verification/DAILY_RUNBOOK.md)、当日 `meta.json` | [`scripts/README.md`](../scripts/README.md)、`collision_dates.py` 诊断 |
| 字段破解/裁决 | [`field_dict.md`](field_dict.md)、[`COLLISION_RULES.md`](field_verification/COLLISION_RULES.md) | 方法论相关章节、raw 样本、[`ADJUDICATION_WORKFLOW.md`](field_verification/ADJUDICATION_WORKFLOW.md) |
| 字典/采集器改动 | `AGENTS.md` §8、§9；`field_registry.json` | `unknown_fields.md`、`script_data_dict.md`、对应适配器与测试 |
| 报告脚本改动 | `AGENTS.md` §8.4；对应报告入口 | `script_data_dict.md`、对应测试 |
| 测试/回归 | [`tests/README.md`](../tests/README.md)、`AGENTS.md` §2.1、§9 | 被改模块及相关测试 |
| 上游/依赖复核 | [`UPSTREAM_COMPATIBILITY.md`](UPSTREAM_COMPATIBILITY.md) | [`source_repository_map.md`](source_repository_map.md)、requirements |
| 架构边界/偏离 | [`ARCHITECTURE_THEORY.md`](ARCHITECTURE_THEORY.md) | [`DEBT_LEDGER.md`](DEBT_LEDGER.md)、对应调用方 |
| 临时目录/启动器 | `AGENTS.md` §1.3 | 仓库根 `.tmp/`、`scripts/run_with_system_python.ps1` |

**读取策略**：主字典导航与待审队列可按字段筛选；不要将 `field_registry.json`、`unknown_fields.md`、`collision_research_state.json.gz` 或 raw 全量灌入上下文。先定位具体 `(source, 完整 code path)`，再读相关样本和来源证据。

## 1. 项目与架构

- A 股分析项目有五个报告入口：`get_sht_report.py`、`get_med_report.py`、`get_lng_report.py`、`get_val_report.py`、`get_mak_report.py`；`main.py` 调度报告子进程。
- 字段采集/破解是独立流程：采集入口为 `scripts/capture_field_probe.py`，碰撞入口为 `scripts/collide.py`；运行步骤见每日运行卡。
- 报告写入 `reports/`；运行缓存使用 `cache/` 或模块配置目录；原始字段证据按数据日存入 `docs/field_verification/`。

| 层 | 入口 | 职责 |
|---|---|---|
| 调度 | `main.py` | 解析任务、执行报告子进程、汇总退出结果 |
| 报告 | 五个 `get_*_report.py`、`stock_common/sc_report_runner.py` | 分析流程、渲染和上传 |
| Tier 1 | `core/data_provider.get_canonical_stock_data()` | 规范字段、来源选择、fallback、单位与 `field_sources` |
| Tier 2 | `stock_common/sc_datasource`、`sc_fuyao`、`core/tdx_client.py` 公开函数 | CYQ/F10/涨停梯队/龙虎榜/行业等专项数据 |
| 原始客户端 | `stock_common/`、`core/tdx_client.py` 内部 | HTTP/TCP/SDK；生产报告脚本不得绕过公开适配器 |
| 缓存 | `core/stock_cache.py` 及适配器 | 分类 TTL；数据契约变化时核查失效策略 |

## 2. 关键运行约束

- ZHB/实时路由由 `data_provider.py` 和 `sc_datasource.zhb_field_safe()` 决定：非交易日或交易日盘前可使用最近已完成交易日快照；交易日开盘后及盘后使用实时路径，不能假定磁盘 ZHB 已更新到当日。
- 报告批量路由和单股 fallback 不是同一层。SHT/MED/LNG 常规批量行情以 push2delay + 腾讯补充为主；单股 fallback 顺序由代码维护为 TDX → 腾讯 → push2delay → push2。delay 成功时不额外请求 push2 主域；push2 是失败回退，不是重复全量锚。
- `CanonicalStockData` 当前有 115 个 dataclass 属性（含 12 个 ELTDX 扩展）；`FIELD_SPECS` 的 38 项是精选字段元数据，不代表全部契约字段。
- 注册表身份始终是 `(source, 完整 code path)`。语义已确认只停止对同一关系的重复破解，不停止采集；只有逐路由冗余证据达到 `scripts/README.md` 的退出与复验条件后，才可暂停该路由的常规采集。
- AxData 和 Levistock 候选样本只作来源或接口核验辅助证据；除非来源谱系明确独立，否则不作为跨源定案锚。AxData 已确认冗余的生产路由会退出日常请求，并在 20 个有效交易数据日后复验。FTShare 私有托管 MCP 已退役，旧字段与 raw 仅供显式历史研究；公开 REST 的 `A股行情列表` 已进入每日采集和默认碰撞。官方契约字段须有逐字段审定证据：Fuyao 属已确认独立来源，使用普通 L1/L1-U；底层来源独立性未确认的契约锚才列入 L1-C。碰撞报告按来源分列契约定义数、窗口观察、比较参与和等级结果；契约定义不等于来源独立，也不自动定案。白名单、限流、封禁和复验状态以 `scripts/README.md` 与本机 `.tmp/` 状态为准。
- 碰撞报告的 Markdown 是摘要；字段结论前必须核对 JSON `report_completeness` 并覆盖所有候选明细。完整性失败、缺失或数量不平时，结论保持未完成，优先从原始归档重建。
- 行情字段按不同有效交易日计窗口，并核对交易日历、来源 `as_of_date`、数据阶段和重复日期；公告/新闻按自然日事件时间。盘前、周末或节假日采样可用于已完成的上一交易日，只要归档和来源日期通过运行时筛选；详情见方法论与每日运行卡。
- 日采集源状态会附带 `error_diagnostics` 分类，区分请求前封禁/熔断跳过、客户端尝试错误与未分类标记；分类仅辅助诊断，不代替 raw 错误。`scripts/check_em_health.py` 通过共享限流做单次端点探测，报告主机、路径、HTTP、响应结构与日期依据，诊断 JSON 留在 `.tmp/`。
- 字段的实时属性、新鲜度与来源优先级分别由 `sc_schema.FIELD_SPECS`、`sc_datasource.zhb_field_safe()` 和实际路由函数决定，不要以名称推断。

架构公理见 [`ARCHITECTURE_THEORY.md`](ARCHITECTURE_THEORY.md)，明确偏离见 [`DEBT_LEDGER.md`](DEBT_LEDGER.md)。

## 3. 工程与验证

- Python 最低版本 3.11；开发/测试推荐 Python 3.12。解释器由 `scripts/run_with_system_python.ps1` 选择。
- 测试通过 `scripts/run_tests.ps1` 运行；真实网络测试只有显式选择时才运行。模块索引与最近全量结果见 [`tests/README.md`](../tests/README.md)。
- 最近完成的全量离线套件（2026-10-21）：收集 1,186 项，1,133 通过、1 跳过、52 个真实网络用例排除，27.95 秒。真实网络用例未运行；后续运行结果以当次命令输出为准。
- 2026-10-20 registry parity 仍有此前保留项：实际 1,878 字段、2,518 个来源配对，基线调整后预期 1,894/2,534，差 16 条新浪扩展 API 路径；投影、field matrix 与范围校验通过。按用户此前决定，留待 AxData 交叉核对后处理。本次定案未新增来源字段路径，仍为 2,518 条。
- 代码改动按 `AGENTS.md` §8 调查数据契约影响，再按 §9 验证。静态规则有专用闸门：`scripts/verify_data_access.py`（A1）和 `scripts/verify_sync_check.py`（A7）；字段视图用对应生成器与 `scripts/registry_parity.py` 检查。
- 清理缓存或采集归档前，先确认是否仍需离线复核；`.gitignore` 按路径规则忽略本机运行数据。

## 4. 权威文档索引

| 文档 | 权威范围 |
|---|---|
| [`field_dict.md`](field_dict.md) | 生成的字段治理导航与权威顺序 |
| [`field_verification/field_registry.json`](field_verification/field_registry.json) | 按来源与完整路径登记的机器权威字段状态 |
| [`unknown_fields.md`](unknown_fields.md) | 未验证/候选/冲突/证伪字段的生成队列 |
| [`field_verification/COLLISION_RULES.md`](field_verification/COLLISION_RULES.md) | 由运行时代码生成的碰撞阈值与状态机镜像；代码常量为执行真源 |
| [`field_verification/CRACKING_METHODOLOGY.md`](field_verification/CRACKING_METHODOLOGY.md) | 候选生成、数据分析与常见误判；按需读相关章节 |
| [`field_verification/ADJUDICATION_WORKFLOW.md`](field_verification/ADJUDICATION_WORKFLOW.md) | 跨源碰撞、单源上游契约与公式实证裁决、注册表写回 |
| [`field_verification/EVIDENCE_COVERAGE.md`](field_verification/EVIDENCE_COVERAGE.md) | 每日证据覆盖、日期资格和来源身份口径 |
| [`source_repository_map.md`](source_repository_map.md) | 上游仓库、包装关系和独立来源族证据 |
| [`script_data_dict.md`](script_data_dict.md) | 报告脚本实际消费的字段与来源 |
| [`field_source_reference.md`](field_source_reference.md) | 重整前字典与协议文字的只读历史归档 |

## 5. 动态信息

Git 状态、采集日期、源健康、碰撞候选、测试结果与 registry parity 都会变化。核实时读取当次状态和产物；不要把本文件、Changelog 或旧报告里的历史数字当成当前状态。
