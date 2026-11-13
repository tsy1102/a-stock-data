# 每日采集与字段核验运行卡

本页规定日常执行顺序；不重复维护阈值、接口限速、报告审阅细则或裁决门槛。对应真源：采集器和来源策略见 [`scripts/README.md`](../../scripts/README.md)，碰撞日期/时效见 `scripts/collision_dates.py`、`scripts/temporal_policy.py` 与 [`temporal_policy.json`](temporal_policy.json)，报告审阅见 [`COLLISION_REPORT_REVIEW.md`](COLLISION_REPORT_REVIEW.md)，网页核验见 [`PUBLIC_WEB_VERIFICATION.md`](PUBLIC_WEB_VERIFICATION.md)，注册表写回见 [`ADJUDICATION_WORKFLOW.md`](ADJUDICATION_WORKFLOW.md)。

## 日常顺序

1. **确定数据日。** 默认 `data_date` 为最近已完成的 A 股交易日：交易日 15:00 起包含当天，15:00 前取上一个交易日；休市日取最近已完成的交易日。采集目录使用 `docs/field_verification/<data_date>/`，同一数据日复用目录。`capture_date/run_date` 表示运行自然日，逐源 `source_capture_date/source_capture_started_at` 表示实际采集时间，`as_of_date` 表示来源数据日期。日期化 ZHB 包以 `zhb_YYYYMMDD.zip` 文件名作为 ZHB 数据日；它可以不同于项目采集目录日期。保留起点由 [`scripts/capture_retention.py`](../../scripts/capture_retention.py) 的 `MIN_CAPTURE_DATE` 定义；遵守根目录 [`AGENTS.md`](../../AGENTS.md) 的禁止绕过规则，不得回补或读取保留起点之前的 raw、ZHB 压缩包或解析缓存。

2. **运行字段采集。**

       .\scripts\run_with_system_python.ps1 scripts\capture_field_probe.py

   需要刷新动态股票池时加 `--refresh-pool`；需要龙虎榜/人气榜等市场上下文时加 `--include-context`，也可用 `--only exchange` 或 `--only em_hot` 单独选择。此命令只采集字段样本，不运行五大报告，也不启动碰撞。采集的日期参数、同日重跑行为和来源清单见 `scripts/README.md`。

   复合来源 `market_sources` 与 `fuyao` 可用 `--only-unit '<unit-id,unit-id>'` 精确补采子接口；成功且质量未退化时只更新所选 raw 路径并保留同源其他路径，失败/空结果或质量退化时保留旧 raw 并记录本次证据，不支持与 `--overwrite` 同用。Fuyao 财务报表按 income/balance/cashflow API 分开，涨停/跌停/炸板池也分别记录；财务指标与 H1 摘要因共用同一接口而合并为一个单元。例：`--date 20261113 --only-unit 'fuyao.income_statements,fuyao.limit_up_pool'`。此入口不运行额外的 AxData 或 Levistock 辅助核验；每日默认采集范围与频率保持不变。

3. **核对采集归档。** 检查 `docs/field_verification/<data_date>/meta.json` 中的 `data_date`、运行时间、市场阶段、逐源采集时间、`as_of_date`、ZHB 日期、来源状态、失败/deferred 和 raw 覆盖。目录名与 `meta.data_date` 不一致的行情快照会被碰撞器拒绝。盘前采集上一交易日时，来源日期早于采集自然日仍可能是已收盘样本；以来源级资格和报告诊断为准。

   同一数据日重跑默认跳过完整来源，只补采缺失或不完整来源并保留既有成功样本。`--only <source>` 会重新请求指定来源，`--overwrite` 会强制刷新所选范围；重采前备份该来源 raw 和 `meta.json`。旧 `meta.json` 缺少逐源时间时，按 `legacy_global_metadata` 处理，不推断精确请求时刻。需要检查历史来源日期对应关系时运行：

       .\scripts\run_with_system_python.ps1 scripts\audit_source_date_mapping.py

   复合接口子单元的覆盖和长期变化证据记在 `meta.json.capture_units`，包括路径/结构和值指纹、响应日期候选、采集器调用时间、逻辑适配器调用数和状态；指纹不复制原始值。此层不观测缓存命中、合并或底层重试，因此逻辑调用数不是实际 HTTP 请求数；适配器也可能把传输失败归一为空结果，`empty` 不证明上游正常返回空数据。用下列只读审计命令汇总保留起点之后的数据日记录：

       .\scripts\run_with_system_python.ps1 scripts\audit_capture_unit_history.py

   审计把请求数据日与来源实际数据日分开；如来源日期未由接口契约或响应字段明确确认，会标作未确认，不将重复请求或同一来源数据日算作独立日期。审计的 catalog 路径出现情况不等于注册表字段全集覆盖；审计结果仅积累证据，不自动降频、停采或退役。后续作此决定前还需核实完整字段覆盖、同日替代关系、独有路径、更新策略、备用源和失败回退行为；判断网络压力或上游空数据时还需要底层 HTTP 请求和状态计数。

   该接口级元数据从修改后的后续采集开始累积。既有归档缺少子接口调用、缓存和错误记录；可另行从保留期 raw 做历史值比较，但不得把推导结果写成真实请求或上游状态。

   ZHB 通常在北京时间 08:00 后才更新到最近交易日。08:00 前的默认采集会跳过 ZHB；显式 `--only zhb` 会在发出请求前拒绝执行。08:00 后可用同一数据日单独补采并归并进原目录，例如：

       .\scripts\run_with_system_python.ps1 scripts\capture_field_probe.py --date 20261109 --only zhb

   将示例日期替换为目标 `data_date`，不要换成运行自然日。日期化归档 `zhb_YYYYMMDD.zip` 的文件名是 ZHB 数据日依据；`raw_zhb.json` 的 `zhb_date` 和 `meta.json` 中该来源的 `as_of_date` 是解析后的副本，应与归档文件名核对。若归档文件名、解析副本或上游日期互相冲突，先查明并记录日期来源，不得静默选取一个日期定案。若上游仍返回旧日期，保留并标记为过期，碰撞按来源实际日期归位，不当作目标数据日的新样本。

4. **按故障类型处置网络错误。** 项目采集 HTTP 请求遵守直连策略；不要为排障改动 TUN、VPN 或系统代理设置。Google Drive 上传按其独立配置处理。网络限速数值、风险组和请求层重试次数以 `scripts/README.md` 与适配器实现为准，本页不复制易变参数。

   | 证据/状态 | 处理方式 |
   |---|---|
   | DNS `dns_resolution_failure` / `not_attempted` | 请求未到达上游，不按东财封禁计数；先保留诊断并继续其他来源。需要单独探测时使用下方健康检查命令。 |
   | 超时、连接错误、HTTP 408/5xx | 先让请求层按适配器策略完成有限重试；采集结束后仅在来源策略允许时考虑单源补采。 |
   | HTTP 403/429、封禁、`circuit_open`、`blocked_until_manual_review` | 不叠加采集器级重试，停止受限风险组本轮请求；继续未受限的独立来源。 |
   | HTTP 400/401/404、参数或稳定契约错误 | 不补采，定位请求参数、接口或代码问题。 |

   `error_diagnostics` 和 `retryable_hint` 用于诊断，不替代来源重试策略。人工单源补采每来源、每数据日最多一次是**操作规约**，采集器不强制计数；仅对允许重试的瞬时故障使用同一 `--date` 和 `--only <source>`。先把 raw 与 `meta.json` 备份到 `.tmp/capture_retry/<data_date>/`，补采后比较来源日期、必需路径、成功样本覆盖和错误数；无改善或丢失既有成功样本时恢复备份。403/429、封禁、熔断和稳定契约错误不进行此补采。

   东方财富健康检查默认每个选中端点单次请求，受本地熔断或空样本影响的退出码 `2` 不代表接口实测失败：

       .\scripts\run_with_system_python.ps1 scripts\check_em_health.py
       .\scripts\run_with_system_python.ps1 scripts\check_em_health.py --probe push2his

   该工具只诊断端点，不改变采集路由或重试策略。采集器实际限流、风险组停止和来源复验条件见 [`scripts/README.md`](../../scripts/README.md)。

5. **运行本地碰撞。**

       .\scripts\run_with_system_python.ps1 scripts\collide.py

   默认使用最近 7 个已确认交易日；新闻/公告按自然日窗口处理。碰撞不请求网络，按来源 `as_of_date` 和有效期筛选样本，且不读取保留起点之前的数据。`collide.py --all` 只扩大本地历史窗口；不要把 `main.py --all` 当作字段采集命令。仅需分析龙虎榜/人气榜上下文时才加 `--include-context`。同一报告日期已有报告或审阅材料时，用 `--run-tag <标签>` 写入独立目录；标签和目标目录规则见 `scripts/collide.py`。

6. **审阅碰撞报告。** 按 [`COLLISION_REPORT_REVIEW.md`](COLLISION_REPORT_REVIEW.md) 核对报告完整性、交易窗口、来源覆盖和全部候选明细。报告未通过完整性或日期资格检查时，暂停语义结论和主字典裁决；重建材料只能使用保留起点之后允许读取的归档。

7. **核验公开网页。** 报告审阅通过后，按 [`PUBLIC_WEB_VERIFICATION.md`](PUBLIC_WEB_VERIFICATION.md) 选择官方页面并留证。Chrome 网页核验依该文档执行，不以 TUN/直连状态预检作为启动条件；不要改变系统网络设置或绕过网站访问控制。

8. **完成候选审阅与正式裁决。** 候选审阅台账和注册表写回是分开的步骤。符合条件的候选按 [`ADJUDICATION_WORKFLOW.md`](ADJUDICATION_WORKFLOW.md) 预览、显式应用并检查 registry parity、字典同步和相关回归；未达到门槛的候选保留证据缺口，不直接改主字典。

9. **汇报结果。** 说明实际采集日和来源有效日、成功/失败/跳过、碰撞窗口、候选和证据状态、是否更新注册表/主字典、验证结果及未解决的证据缺口。
