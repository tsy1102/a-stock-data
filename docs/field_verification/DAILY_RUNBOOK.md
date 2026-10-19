# 每日采集与字段碰撞运行卡

本页是日常执行入口，不复制完整字段规则。碰撞阈值以 scripts/collision_rules.py 和生成的 COLLISION_RULES.md 为准；日期/样本选择以 collision_dates.py 为准；方法、覆盖与写回分别见下方权威文档。

## 日常顺序

1. **定数据日。** 行情目标日取项目交易日历与 ZHB 假期缓存确认的最近已完成交易日；盘前、周末、节假日都可采集最近收盘快照，不设“必须 15:30 后运行”的门槛。capture_date/run_date 是实际采集自然日，data_date 是目标数据日，来源 as_of_date/zhb_date 是源实际提供的数据日。公告新闻按事件自然日。不要用文件夹名替代来源日期，也不要为对齐而删除/改名历史目录。

2. **运行字段采集。**

       .\scripts\run_with_system_python.ps1 scripts\capture_field_probe.py

   需要刷新动态股票池时显式加 --refresh-pool；需要龙虎榜/人气榜等市场上下文时加 --include-context，或单独用 --only exchange / --only em_hot（会自动启用上下文）。这一步不等于运行五大报告脚本，也不会自动启动碰撞。

3. **核对采集归档。** 检查目标数据日目录的 meta.json：运行时间、数据日/日期域、市场阶段、各源状态、as_of_date、ZHB 实际日期、失败/deferred 和 raw 覆盖。盘前采集上一个交易日时，来源日期早于实际采集日可被碰撞器判为已收盘样本；以报告中的资格与告警为准，不因开盘时刻或旧目录名机械排除。

   同日已有完整收盘快照时默认幂等跳过；盘中快照可在收盘后更新。--overwrite 会重采所选数据，--only <source> 会实际重新请求该源；覆盖前先读现有 meta.json。同一来源、同一有效数据日的重复目录不会计成独立日期，快照择优按运行时日期规则执行。

4. **遵守限流。** 来源按采集器顺序和适配器限流运行；不为凑样本并发重试。出现 HTTP 403、429、明确封禁或源族熔断时，立即停止该源族本轮请求，记录原始诊断，不盲目换端重试。持久 blocked_until_manual_review 状态需人工确认源恢复后清除。不要把 main.py --all 当作字段采集命令；collide.py --all 只扩展历史分析窗口，不发网络请求。各源白名单、退役/复验条件见 [scripts/README.md](../../scripts/README.md)。

5. **单独运行碰撞。**

       .\scripts\run_with_system_python.ps1 scripts\collide.py

   默认分析最近 7 个不同有效交易日；新闻/公告另按自然日窗口处理。扩窗用 --window N；--all 只用于明确的全历史研究。碰撞是本地分析，不请求数据源。只有确需分析已归档的龙虎榜/人气榜上下文时才加 --include-context。

6. **读报告而非只看候选数。** 检查窗口中的具体样本日期、来源日期、采集阶段、每日样本量、信息配对、来源独立性和异常告警；把 actionable_L1 与已登记映射的 mapped_pair_revalidations 分开。名称拆词、相关性、公式/时间序列、AxData/FTShare/Levistock 汇总接口都只提供候选或来源身份辅助证据，不能绕过当前 L1/L1-U 门槛或独立性规则。

## 破解与主字典闭环

- 字段定义已确认后，应停止重复破解同一关系并让已确认字段作为未知字段的锚；**继续采集**字段，除非该具体源路由另行满足 scripts/README.md 中的冗余退出与复验条件。
- 只有达到跨源裁决条件并人工确认语义等价，或完成权威单源契约核验，才创建 adjudication。先按 [ADJUDICATION_WORKFLOW.md](ADJUDICATION_WORKFLOW.md) 预览，再明确应用；随后检查 registry parity、字典同步和对应回归。候选报告本身不自动改变主字典。
- 定义/单位冲突须先逐来源、逐完整路径处理；不能把某源的字段含义投射给同名短 code 的其他源，也不能把汇总/包装库当作新的独立底层来源。

## 按需读取与每次汇报

- 常规运行先读本页、当日 meta.json 和本轮碰撞报告；只有具体候选需要时，再读 [CRACKING_METHODOLOGY.md](CRACKING_METHODOLOGY.md) 对应方法、原始样本、registry 精确记录或上游源码。完整索引见 [EVIDENCE_COVERAGE.md](EVIDENCE_COVERAGE.md)。不要全文加载大体积 registry、unknown queue 或历史状态 JSON。
- 汇报：实际采集日与有效来源日、成功/失败/跳过、碰撞窗口、候选与证据等级、是否满足裁决条件、主字典/注册表是否变化、验证结果及下一步证据缺口。
