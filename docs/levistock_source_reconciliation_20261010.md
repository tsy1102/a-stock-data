# Levistock 来源与每日采集核对

核对日期：2026-10-10
依赖版本：`levistock==0.1.8`
范围：上游仓库定位、项目实际调用路径、逐日样本记录策略及来源身份校正。本文不修改字段含义或定案状态。

## 结论

`fleetinglife/levistock` 是多源客户端包装库，不是一个独立行情提供方。把 `levistock(ftshare)` 当作 FTShare 运行源会把不同来源混在一起：项目的 FTShare 数据由 `stock_common.sc_ftshare` 直接访问 `market.ft.tech`；Levistock 当前接入的两个采集方法分别属于财联社和开盘红（KPH）。

迁移前的结构化字段注册表有 175 条历史记录使用 `levistock(ftshare)` 混合键：116 条没有可直接定位的字典章节，16 条属于 KPH 市场情绪章节，12 条属于 KPH 复盘章节，5 条属于 KPH 板块排行章节，20 条属于旧版 Levistock 全接口核验，6 条实际是 FTShare 字段。2026-10-11 已按证据完成重分类：其中 136 条保留为未归属历史记录，33 条归到 KPH 组件身份，6 条归到 FTShare 服务接口身份。所有记录的字段路径和原状态均保留；两类明确身份仍分别映射到来源谱系中的 KPH 来源族和未确认的 FTShare 服务族。

本次审查解释器实际安装 `levistock==0.1.7`，而仓库依赖约束为 `levistock==0.1.8`；每日核验会记录运行时版本，不能把当前环境的样本误记为已在约束版本下回归。

## 已核实的项目调用

| 项目方法 | Levistock 方法 / 上游 | 项目归档位置 | 日期与采集口径 |
|:---|:---|:---|:---|
| `get_cls_market_emotion()` | `levistock.market_emotion_cls()`；财联社 `x-quote.cls.cn` 市场情绪接口 | `raw_market_sources.json` → `cls_market_emotion` | 方法不传交易日参数；逐日记录显式响应日期（若响应没有日期则记为未提供），不把采集目录日期伪装成来源日期。 |
| `get_kph_limit_ladder(date)` | `levistock.get_zttt(date=...)`；开盘红 KPH 天梯 | `raw_market_sources.json` → `kph_limit_ladder` | 只请求一个明确的已完成交易日；不再回退并静默返回更早日期。空响应计为可见失败。 |
| 项目 FTShare 采集器 | 不使用 Levistock；调用 `stock_common.sc_ftshare` 的 FTShare MCP 方法 | `raw_ftshare.json` | 是单独运行源；空字段不能再仅凭 `probe_trading_day` 被记为有效采集。 |

采集代码证据：`stock_common/sc_datasource/_misc.py`、`stock_common/sc_datasource/_pools.py`、`stock_common/sc_datasource/_quotes.py` 与 `scripts/capture_field_probe.py`。上游实现证据：[Levistock README](https://github.com/fleetinglife/levistock/blob/main/README.md)、[CLS 市场情绪实现](https://github.com/fleetinglife/levistock/blob/main/levistock/market/market_emotion_cls.py)、[KPH 天梯实现](https://github.com/fleetinglife/levistock/blob/main/levistock/stock/stock_fupanla_kph.py)。

## 每日核验策略

完整收盘采集或 `--only market_sources` 会先采项目现有的 CLS 情绪和 KPH 天梯，再从以下 7 个候选方法中按持久化游标选择一个，每个有效交易日最多增加一次请求：

| 候选 ID | 上游方法 | 提供方族 | 日期依据 |
|:---|:---|:---|:---|
| `cls_sector_industry` | `sector_industry_cls` | CLS | 实时快照，响应日期可能缺失 |
| `kph_market_emotion` | `market_emotion_kph(date=...)` | KPH | 请求交易日 |
| `cls_sector_heat` | `get_sector_heat` | CLS | 实时快照，响应日期可能缺失 |
| `kph_sector_ranking` | `sector_ranking_kph(date=..., zs_type="7", fetch_all=False)` | KPH | 请求交易日 |
| `cls_sector_rotation` | `get_sector_rotation(days=4)` | CLS | 响应日期序列 |
| `cls_stock_kline` | `stock_kline_cls(..., kline_type="daily", limit=5)` | CLS | 响应交易日序列 |
| `cls_stock_timeline` | `stock_timeline_cls` | CLS | 响应日期 |

探针只在市场阶段为 `closed`、数据日等于最近完整交易日、项目对应 CLS/KPH 采集成功且运行时版本精确等于 `requirements.txt` 固定的 `0.1.8` 时执行。运行时不设 15:30 门槛；周末、节假日和盘前运行时，采集器默认以最近已完成交易日作为数据日。版本或数据日门槛不满足时记录跳过原因，不消耗当日探针名额。候选样本的日期可比性仍由按日请求参数或响应实际交易日期判断，只有日期证据匹配的样本可用于日期对照。上游请求通过 `stock_common.sc_datasource.get_levistock_candidate_sample` Tier 2 适配器，适配器负责 CLS/KPH 跨进程限流和上游方法路由。403、429、封禁会持久熔断对应提供方族，需人工确认恢复后清理 `.tmp/a_stock_data_v7/levistock_provider_blocks.json`。当前检查环境的已安装版本是 `0.1.7`，因此这里的 7 项候选轮验会被版本门跳过；安装仓库固定依赖后才会开始轮验。原始候选响应和请求信息保存在 `levistock_candidate_raw.json`，与主碰撞 raw 分开，不能直接作为独立源或碰撞锚；`levistock_validation.json` 的 `network_requests_added=0` 只表示离线核验器自身不发请求，额外探针数量单列在 `capture_probe_request_count`。

完整快照当天再次运行时，主源采集保持幂等跳过，但会从已保存 raw 补齐或刷新验证摘要；`levistock_candidate_raw.json` 和 `.tmp` 每日状态防止同日重复请求。使用 `--overwrite` 会重采本次所选主源，仍保留候选文件和 AxData 每日证据，因此已启动的候选请求不会重复。若先前因 CLS/KPH 对照样本缺失而零请求跳过，重采恢复对照源后可同日重新评估；零请求评估只记录 `last_evaluated_data_date`，不会占用 `last_attempted_data_date`。

这只是一个经过筛选的 7 项日轮验队列，不是 Levistock 全部公开 API 的逐项实测。其余方法仍按底层提供方、项目覆盖、返回契约、数据日期和请求成本逐项评估；文本/热点接口不进入字段破解队列，Eastmoney push2 未确认恢复前继续排除。AxData 的每日主动探针也只固定核验 Tencent 快照接口并轮换样本股票，不是 AxData 257 个接口的每日轮询；全接口静态映射与真实样本验证范围见 [AxData 对撞报告](axdata_field_reconciliation_20261010.md)。

## 碰撞与登记影响

- 旧身份 `levistock(ftshare)` 已从当前字段注册表和 `source_lineage.json` 移除；其历史证据按接口归属拆分，未归属部分没有运行时别名，也不具备锚资格。
- 财联社与 KPH 样本通过 `market_sources` 的组件级 `__source_meta__` 标注适配方法和上游族。组件名称保留原状，数值字段路径不变。
- FTShare 的 6 条记录已归入 FTShare 服务接口身份；底层来源族仍未确认，因此不作为独立碰撞锚。
- Levistock 与 AxData、KPL 的关系按接口和数据日分别比较。相同底层提供方的包装调用不算独立源；KPH 与 KPL 是不同提供方，字段是否同义仍按同日实测值判断。

## 后续主字典来源身份校正（2026-10-11）

随后逐条核对了章节、规范路径和现有来源身份，并与迁移前的结构化注册表对照：

- **AxData**：主字典来源登记标注为“多源框架参考”，不是独立提供方。主注册表没有 `source="AxData"` 的逐字段记录，因此没有 AxData 字段需要迁移；采集器仍保留 `axdata` 客户端键，当前短线接口映射到 TDX 来源族，AxData 的其他接口不因仓库关系自动计作项目来源。
- **KPH**：12.10.3、12.10.4、12.10.7 明确属于开盘红 KPH，共 33 条字段记录迁到 `开盘红(Levistock适配)`；该身份映射到现有 `kph` 运行时和来源族，不形成第二个独立来源。5 个与现有 KPH 行重名的路径（`limit_time`、`net_inflow`、`seal_amount`、`seal_money`、`turnover`）保留在不同适配接口身份下，未合并相互冲突的规范映射。
- **FTShare**：12.20.1 的 6 条字段记录迁到 `FTShare` 服务接口身份。项目通过自有 MCP 客户端访问托管服务；GitHub 仓库是文档/集成参考。`ftshare` 的底层来源族仍为 `unconfirmed`，该身份不作为独立碰撞锚。
- **历史未归属**：136 条结构化记录保留原字段路径、状态、含义和证据。旧 Markdown 解析器另能识别 56 个 token，但这些 token 在迁移前的结构化注册表中没有对应记录，现仍只留在不可改写的 `field_source_reference.md` 原文中，不提升为当前字段记录、不推断含义或底层源。

逐项映射清单见 [`source_identity_reclassifications.json`](field_verification/source_identity_reclassifications.json)。重分类后注册表仍有 2,481 条 `source_fields`、1,852 个兼容聚合字段；verified 842、unverified 1,548、candidate 1、conflict 90。迁移只改 175 条记录的来源身份键及对应聚合来源名，不变更字段状态、含义、单位、路径或证据。历史逐字节归档 `field_source_reference.md` 保持不变。
