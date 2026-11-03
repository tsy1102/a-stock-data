# 领域词汇表

本文件只统一稳定术语的含义，不定义运行策略。字段口径、数据路由、新鲜度、缓存、限流、重试、保留期和碰撞门槛均由各自真源决定；本表不复制这些易变规则。遇到冲突时，按 `docs/PROJECT_CONTEXT.md` 和 `docs/README.md` 的职责索引核对代码、测试、生成来源及用户当前要求。

## 真源导航

| 内容 | 当前依据 |
|---|---|
| Agent 操作、数据保护和验收规约 | [`../AGENTS.md`](../AGENTS.md) |
| 架构原则与当前已接受的偏离 | [`ARCHITECTURE_THEORY.md`](ARCHITECTURE_THEORY.md)、[`DEBT_LEDGER.md`](DEBT_LEDGER.md) |
| 字段身份与逐源状态 | [`field_verification/field_registry.json`](field_verification/field_registry.json)；[`field_dict.md`](field_dict.md) 是生成导航 |
| 采集来源、字段样本及证据 | [`field_verification/`](field_verification/README.md)、[`verify/`](verify/README.md) |
| 日期与碰撞样本资格 | [`field_verification/temporal_policy.json`](field_verification/temporal_policy.json)、[`../scripts/collision_dates.py`](../scripts/collision_dates.py) |
| 碰撞阈值与状态转换 | [`../scripts/collision_rules.py`](../scripts/collision_rules.py)；[`field_verification/COLLISION_RULES.md`](field_verification/COLLISION_RULES.md) 是生成镜像 |
| 实际数据路由、缓存、限流和重试 | 对应运行时代码及契约测试；从 [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) 按任务定位 |
| 日常采集与正式裁决 | [`field_verification/DAILY_RUNBOOK.md`](field_verification/DAILY_RUNBOOK.md)、[`field_verification/ADJUDICATION_WORKFLOW.md`](field_verification/ADJUDICATION_WORKFLOW.md) |

## 术语

| 术语 | 含义 |
|---|---|
| 自然日 | 日历上的日期。公告、新闻等事件的来源日期按其原始时间戳或来源定义记录。 |
| 交易日 | 交易所实际开市的日期；不能仅由星期几推断，具体资格由项目交易日历和日期规则判断。 |
| 采集时间（`collected_at`） | 本机获取或组装样本的时间，不代表上游数据日期。 |
| 数据日期（`data_date`） | 样本所代表的市场或业务日期，应由该来源可核实的日期证据确定。 |
| 字段有效日期（`as_of_date`） | 单个字段取值所对应的日期；可与采集时间、整份响应的数据日期不同。 |
| 字段身份 | 来源标识与完整字段路径的组合；端点、协议或命名空间不同，即使代码数字相同，也视为不同路径。 |
| canonical | `core/data_provider.py` 提供的统一字段合约。其成员和行为以运行时代码及契约测试为准。 |
| 碰撞（collision） | 对不同来源的候选字段进行样本比较，用于筛选和评估关系；候选结果本身不写入主字典。 |
| 裁决（adjudication） | 按正式流程审阅证据并明确决定是否写回字段注册表；流程见裁决工作流。 |
| 日期化 ZHB 缓存 | 对 `zhb_YYYYMMDD.zip`，文件名日期是数据日期；解析得到的 `zhb_date` 是下游元数据。日期冲突处理以解析器和 ZHB 回归测试为准。 |

## 维护边界

- 新术语只在含义稳定且跨文档复用时加入；接口字段清单和中英文映射维护在 registry、生成字典或来源证据中。
- 不在本文件记录易变的接口可用性、字段数量、版本、限流数字、缓存 TTL、测试计数或当前待办。
- 历史方法、规则和字段原文留在明确标注为历史的归档中，不作为现行执行依据。
