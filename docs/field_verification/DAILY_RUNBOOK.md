# 每日采集与字段碰撞运行卡

本页是日常执行入口，不复制完整字段规则。碰撞阈值以 scripts/collision_rules.py 和生成的 COLLISION_RULES.md 为准；日期/样本选择以 collision_dates.py 为准；方法、覆盖与写回分别见下方权威文档。

## 日常顺序

1. **定数据日。** 行情目标日取项目交易日历与 ZHB 假期缓存确认的最近已完成交易日；盘前、周末、节假日都可采集最近收盘快照，不设“必须 15:30 后运行”的门槛。capture_date/run_date 是实际采集自然日，data_date 是目标数据日，来源 as_of_date/zhb_date 是源实际提供的数据日。公告新闻按事件自然日。不要用文件夹名替代来源日期，也不要为对齐而删除/改名历史目录。

2. **运行字段采集。**

       .\scripts\run_with_system_python.ps1 scripts\capture_field_probe.py

   需要刷新动态股票池时显式加 --refresh-pool；需要龙虎榜/人气榜等市场上下文时加 --include-context，或单独用 --only exchange / --only em_hot（会自动启用上下文）。这一步不等于运行五大报告脚本，也不会自动启动碰撞。

3. **核对采集归档。** 检查目标数据日目录的 meta.json：运行时间、数据日/日期域、市场阶段、各源状态、as_of_date、ZHB 实际日期、失败/deferred 和 raw 覆盖。盘前采集上一个交易日时，来源日期早于实际采集日可被碰撞器判为已收盘样本；以报告中的资格与告警为准，不因开盘时刻或旧目录名机械排除。

   同日已有完整收盘快照时默认幂等跳过；盘中快照可在收盘后更新。--overwrite 会重采所选数据，--only <source> 会实际重新请求该源；覆盖前先读现有 meta.json。同一来源、同一有效数据日的重复目录不会计成独立日期，快照择优按运行时日期规则执行。

4. **遵守限流并处理瞬时失败。** 来源按采集器顺序运行，不并发重试。通用同步/异步请求层对传输超时、连接类异常和 HTTP 408/5xx 按调用方 `max_retries` 总尝试次数（含首次请求）做有界退避；Eastmoney 专用 `em_get` 最多额外请求一次，每次重试重新取得令牌并遵守跨进程节奏。HTTP 403/429 不在这些共享请求层重试，push2 显式设置 `max_retries=1` 时仍只发一次。单次超时、连接重置、临时 DNS 故障或 HTTP 408/5xx 不得直接当作该源永久失败；请求层重试结束后，采集器继续执行其他来源。首轮结束后，若 `meta.json` 仍将某源标为 `partial`/`failed`，且错误证据属于上述瞬时故障、该源策略允许重试，可对该源做**一次串行单源补采**：沿用同一 `--date`，使用 `--only <source>`，不要重跑全量采集或 `--all`。重试前把该源现有 `raw_<source>.json`（若存在）及 `meta.json` 复制到仓库 `.tmp/capture_retry/<data_date>/`；`--only` 会重新请求并覆盖该源文件。重试后比较来源日期、必需路径、成功样本覆盖与错误/缺股数；只有结果确实改善且没有丢失原有成功样本时才保留，否则恢复原文件。每源每天最多做一次这种采集器级补采。

   `meta.json` 中 `sources.<source>.error_diagnostics` 保留 `categories` 与 `request_attempt_states` 汇总，并给出至多 20 组明细：分类代码、阶段、风险族、尝试状态、可重试提示、主机、HTTP 状态、脱敏错误样例和路径样例。分类来自错误标记文本，不证明远端收到请求；`retryable_hint` 只用于排查、不会改变重试策略。明细超量时检查 `omitted_detail_groups`；最终以 raw 中的原始错误和逐请求记录为准。

   HTTP 403、429、明确封禁、`circuit_open` 或 `blocked_until_manual_review` 属于限流/封禁：共享请求层不重试 403/429，适配器内部其他明确限次处理也不叠加采集器级重跑；适配器最终返回受限状态后，立即停止该源族本轮剩余请求，不换同源端点继续试，但继续其他独立源。400/401/404、参数错误、稳定的解析/契约错误也不做采集器级补采，应定位接口或代码问题。若来源已有更严格的防封或禁止重试约束，遵守该约束。二次补采后仍失败就保留失败记录并报告证据缺口，不把一次失败静默当作已完成。不要把 main.py --all 当作字段采集命令；collide.py --all 只扩展历史分析窗口，不发网络请求。各源白名单、退役/复验条件见 [scripts/README.md](../../scripts/README.md)。

   手动核对东方财富时使用 `scripts/check_em_health.py`；默认每个端点单次请求并复用共享限流，JSON 输出到 `.tmp/eastmoney_health/`。它遇到封禁、403/429 或传输故障后停止同风险族探测；退出码 `2` 表示本地熔断跳过或空样本，不能当作接口实测失败。可用 `--probe push2his` 等只检查一个端点。该脚本不会改生产采集路由或重试策略。

5. **单独运行碰撞。**

       .\scripts\run_with_system_python.ps1 scripts\collide.py

   默认分析最近 7 个不同有效交易日；新闻/公告另按自然日窗口处理。扩窗用 --window N；--all 只用于明确的全历史研究。碰撞是本地分析，不请求数据源。只有确需分析已归档的龙虎榜/人气榜上下文时才加 --include-context。

6. **完整审阅报告，先过完整性闸门。** 检查窗口中的样本日期、来源日期、采集阶段、每日样本量、信息配对、来源独立性和告警；把 `actionable_L1` 与 `mapped_pair_revalidations` 分开。候选覆盖区逐个未知目标给出比较、覆盖、候选、来源失败、公式线索和复核股票。

    先核对 JSON 的 `report_completeness`：状态必须为 `complete`，方法候选生成数、全量明细数、重复数和缺失数必须对平。`candidate_review` 单独列出机器候选完整性、身份校验、人工审阅覆盖率与待处理量；`report_completeness.status=complete` 不代表人工已审完。再逐章节检查 Markdown，并结构化遍历 JSON 中所有明细集合，尤其是完整的 `method_candidate_inventory`、L1/L4、目标诊断、公式候选、来源状态和告警。Markdown 的 Top-N 仅是导航摘要；不得只分析开头、前 N 条或摘要后就称“无候选/无成果”。

    人工处置写入独立台账，不直接改注册表：从 [候选审阅模板](review_templates/candidate_review_template.json) 复制出一份决定 JSON，填入候选的 `candidate_id`、处置、审阅人、带时区的 `reviewed_at`、理由和证据引用。至少引用一份包含该候选的碰撞 JSON；工具会记录该文件的 SHA-256。先预览，再显式写入：

        python.exe scripts/review_collision_candidates.py --decision docs/field_verification/adjudications/candidate_review.json
        python.exe scripts/review_collision_candidates.py --decision docs/field_verification/adjudications/candidate_review.json --apply

    批量决定可用根对象 `{"schema_version":1,"decisions":[...]}`，每个成员采用模板中的决定字段。重复归并时，每个成员都填写 `duplicate_grouped` 和同一个代表候选 `duplicate_of`；报告会保留代表到成员的反向索引。状态含义：`insufficient_evidence` 表示当前证据不够，`needs_external_evidence` 表示须补权威外部材料，`rejected` 表示拒绝该关系候选，`accepted_for_adjudication` 表示可进入既有裁决流程。写入审阅台账后重新运行本地碰撞，使新报告反映状态；schema 5 的 L1 注册表裁决要求对应候选先达到 `accepted_for_adjudication`。审阅记录不会单独升级字段或修改主字典。

    若完整性状态异常、候选身份/处置数对不上、集合缺失或数量不一致，暂停语义结论与主字典裁决；从原始采集归档重建缺失明细。无法重建时，明确记录未审条数、字段范围和缺失原因，不得把未展示内容视为无结果。`candidate_review.human_review.status=pending` 表示审阅尚未完成，不等同于机器清单不完整；台账不可用或身份校验不通过时，不得宣称候选已审。旧版报告若没有 `report_completeness` 或全量方法候选清单，按可能截断处理；缺失索引 `.tmp/field_evidence_coverage/` 时则按报告给出的不可用状态记录证据缺口。

   名称拆词、相关性、公式/时间序列、AxData/Levistock 汇总接口都只提供候选或来源身份辅助证据，不能绕过当前 L1/L1-U 门槛或独立性规则。FTShare 旧私有 MCP 已退役；公开 REST `ftshare_rest` 是日常采集源，官方文档定义的字段参与默认碰撞并作为语义契约锚，强多日匹配单列 `L1-C`，不代表底层来源独立或自动定案。旧 `FTShare` raw 默认排除，仅显式 `--all` / `--exploratory` 可研究。

每次碰撞报告的 `source_coverage` 必须同时阅读 JSON 全量统计与 Markdown 汇总，按来源核对契约定义、窗口观察样本、实际参与比较次数及 L1/L1-C/L4 结果。契约字段数不是实测覆盖数；已确认独立来源（如 Fuyao）的契约字段仍按普通独立锚处理。Fuyao 竞价响应时间只作采集时间诊断，不替代来源数据日期。

## 破解与主字典闭环

- 字段定义已确认后，应停止重复破解同一关系并让已确认字段作为未知字段的锚；**继续采集**字段，除非该具体源路由另行满足 scripts/README.md 中的冗余退出与复验条件。
- 用户要求运行采集并碰撞时，授权包含对证据充分候选完成 adjudication、预览、应用、生成视图和验证；无需再次询问是否进入定案。执行者必须自行逐项核对语义、单位、来源独立性和完整性门槛；未达到条件的候选继续保留并报告缺少的证据。按 [ADJUDICATION_WORKFLOW.md](ADJUDICATION_WORKFLOW.md) 执行后检查 registry parity、字典同步和对应回归。候选报告本身不会自动改变主字典。
- 定义/单位冲突须先逐来源、逐完整路径处理；不能把某源的字段含义投射给同名短 code 的其他源，也不能把汇总/包装库当作新的独立底层来源。

## 按需读取与每次汇报

- 常规运行先读本页、当日 meta.json 和本轮碰撞报告；只有具体候选需要时，再读 [CRACKING_METHODOLOGY.md](CRACKING_METHODOLOGY.md) 对应方法、原始样本、registry 精确记录或上游源码。完整索引见 [EVIDENCE_COVERAGE.md](EVIDENCE_COVERAGE.md)。不要全文加载大体积 registry、unknown queue 或历史状态 JSON。
- 汇报：实际采集日与有效来源日、成功/失败/跳过、碰撞窗口、候选与证据等级、是否满足裁决条件、主字典/注册表是否变化、验证结果及下一步证据缺口。
