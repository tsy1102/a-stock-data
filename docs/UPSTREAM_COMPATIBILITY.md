# 上游仓库与兼容性复核

> 复核日期：常规上游兼容性基线为 2026-10-08；项目级历史参考仓库增量复核于 2026-11-02。仓库对应关系以生成文档 [`source_repository_map.md`](source_repository_map.md) 和逐源完整路径登记为准；本文件记录本轮确实影响依赖、采集路径或字段解释的更新结论。GitHub 项目是实现参考、客户端或传输工具时，不据此推断其拥有底层行情，也不把包装库当成独立碰撞来源。

## 本轮相关仓库与结论

| 仓库/项目 | 本项目中的实际边界 | 本次核对 | 采用结论 |
|---|---|---|---|
| [HiThink-Tech/Financial-API](https://github.com/HiThink-Tech/Financial-API) | 用户确认的 Fuyao 上游参考；本项目直接请求 Fuyao REST，不安装或调用该仓库 SDK。 | 仓库迁移为 monorepo；截至 2026-09-10 增加期货/期权等服务能力。竞价 `auction/snapshot` 返回响应信封，响应 `timestamp` 是组装时间，未定义明确的源端数据日期。 | 不复制 SDK、不增加请求。只有上游明确给出数据日期、日期与目标交易日一致且状态就绪时，竞价子树才参与对撞；Benchmark 请求仍传入目标交易日。新增期货、期权和基金能力当前未被项目调用。 |
| [yanwei99521/easy-tdx](https://github.com/yanwei99521/easy-tdx) | 用户确认的 TDX 客户端及 ZHB 缓存传输/读取工具；不代表仓库托管 ZHB 数据本体或独立行情提供方。 | GitHub Releases 无正式发行版；上游 changelog 最新标注 1.20.8（2026-08-21）。requirements 使用提交 `41e56376fafa3abae0f6538f271eafd6af26d27f` 对应的 vendored wheel。 | 保留固定提交和 wheel，不追随无版本号的 main；仍需项目动态握手补丁，并按既有 TDX 限流使用。 |
| [electkismet/eltdx](https://github.com/electkismet/eltdx) | 用户确认的 TDX 协议客户端适配层；与 TDX 属于同一来源族。 | requirements 原锁定 3.2.2；上游最新为 3.3.2（2026-10-30）。3.2.3 新增退市日线接口和代码/分页参数校验，本项目未调用该接口；3.3.0 新增 EX/MAC/offline/financial 能力并说明从 3.2.3 升级保持原有 API 默认行为；3.3.1 调整子服务与客户端生命周期并移除可转债单位补偿；3.3.2 强化 `get_snapshots()` 与 `finance_batch()` 的缺项、记录长度、市场、代码及请求归属校验。缺项默认严格报错；显式 `on_missing="skip"` 返回有效部分并告警，但仍可能执行最多 32 次二分恢复请求。适配器持有客户端，并直接使用 `volume_lots`，不依赖旧生命周期或可转债补偿。本轮按 [0x000f 股本变迁接口契约](https://electkismet.github.io/eltdx/methods/7709-%E8%82%A1%E6%9C%AC%E5%8F%98%E8%BF%81GBBQ/) 补齐 `capital_changes()` 到 mootdx `xdxr` 的类别 1 字段映射（c1/c2/c3/c4 对应每十股现金分红/配股价格/送转数量/配股数量）。该接口不支持日期范围并返回整段历史。 | 保持 `eltdx==3.3.2` 与已有 `on_missing="skip"` 分批快照行为。分红历史改由按需报告接口读取并使用新的 `dividend_tdx_v2` 缓存分类；默认每日 `tdx_f10` 不再把无日期范围的整段历史写入原始样本。TDX 与 ELTDX 仍是同一来源族，不新增字段矩阵关系、来源锚或对撞路由。 |
| [fleetinglife/levistock](https://github.com/fleetinglife/levistock) | 用户确认的多源客户端包装库；用于部分 Eastmoney/财联社实现参考，不代表独立底层数据源。 | PyPI 最新为 0.1.8（2026-09-22），本项目 requirements 已固定 0.1.8。项目实际调用 `market_emotion_cls()`、顶层 `get_zttt(date=...)`，以及 `levistock.stock.stock_fupanla_kph.get_zttt()` / `get_pmsl()`；该版其余差异不触及这些适配调用。 | 保持 `levistock==0.1.8`。现有离线回归覆盖实际方法路径、日期参数和 11 列涨停行归一化；不把包装来源重复计为独立证据。 |
| [electkismet/AxData](https://github.com/electkismet/AxData) / [AxData on PyPI](https://pypi.org/project/axdata/) | AxData 是多提供方框架，本项目只调用 `stock_shortline_indicators_tdx` 这一条 TDX 适配接口。该接口读取项目本地 ZHB ZIP 的 `tdxstat.cfg` / `tdxstat2.cfg`，行情和财务输入仍可能访问 TDX；`stats_date` 只是统计基准日期。 | PyPI 最新为 0.1.4（2026-08-13），与 requirements 固定版本一致。0.1.4 改进 TDX 连接池和请求调度；显式 `stats_root` 分支仍直接读取本地 ZIP 并返回 `refreshed=False`。单股票调用不触发其多代码并行快照条件。 | 保持 `axdata==0.1.4`。现有回归覆盖 ZIP 读取器与 `request_interface` 契约；未验证真实 TDX 连接或行情返回，不将 AxData 视为独立字段锚。 |
| [FTShare-Lab/FTShare-MCP](https://github.com/FTShare-Lab/FTShare-MCP) | 仅为已退役集成的历史文档参考；项目已删除运行时客户端、MCP/SDK 调用与每日采集。该仓库没有公开 MCP 服务端实现，不能验证 `market.ft.tech` 的底层数据提供方或官方接口来源。 | 15 条历史字段路径及旧响应镜像保留在注册表/本地归档，FTShare 来源身份被标为历史；不再视为当前项目运行源。 | 不安装、不调用、不采集、不作为碰撞锚；历史样本仅通过显式 `--all` / `--exploratory` 研究。以后如需替代，应直接核验并接入可公开检查的官方源接口。 |
| [FTShare REST Gateway 接口文档](https://market.ft.tech/gateway/doc/p/pb8eizu3) | 公开 REST Gateway 的 `A股行情列表` 接口。其公开文档能支持返回字段含义与请求契约；该服务的底层数据提供方及与项目现有源的独立性仍未确认。 | 接口每日由 `ftshare_rest` 采集；官方定义的字段登记在 `field_registry.json` 并进入默认碰撞。强多日数值匹配标为 `L1-C`，与独立来源 L1/L1-U 分开，不自动定案。未文档化的观察字段不作为锚。 | 使用公开 REST 接口，不使用私有 MCP/SDK。按 `docs/verify/ftshare_rest_contract.md` 限量、限速；403/429 立即停止当前源，不重试。 |

| [simonlin1212/a-stock-data](https://github.com/simonlin1212/a-stock-data) | 用户确认的项目早期参考仓库；不是本项目的运行时依赖或自动同步源。 | 最新 release 为 [v3.10.3](https://github.com/simonlin1212/a-stock-data/releases/tag/v3.10.3)（2026-10-30），修复 §10.3 上证 e 互动时间解析：补齐 ISO 日期、月日、纯时分和多种相对写法，统一按北京时间换算，并将无效/越界输入作为未识别时间；v3.10.2 的 `full_valuation()` 修正未找到本项目运行时代码对应项。v3.10.1 的逐笔会话复用、限范围重试和完整性标记已在此前移植；其余 K 线更新仅是文档口径。 | 本地 `_sse_e_interaction.py` 已支持“昨天”等常见相对写法，但缺 ISO/月日/纯时分、明确北京时间和越界保护。本轮补齐这些解析边界并保留不识别时整页 `RuntimeError`；输出字段、调用签名、采集路由和缓存行为不变。增加离线回归覆盖各写法、时区、跨年及错误输入。其余 v3.10.2 不需同步。 |

本项目将 `axdata` 保留为客户端/接口采集键，不能将其视为独立数据提供方或独立碰撞锚。当前短线采集只代表 AxData 的 TDX 接口路径；其他 AxData 接口需逐项登记实际提供方、字段契约和限流后再接入。

## 其他更新的处理

- [LowellLee/kpl](https://github.com/LowellLee/kpl) 与 [Rainynitesky/kaipanla-data-parser](https://github.com/Rainynitesky/kaipanla-data-parser) 是并列的 KPL 接口参考，不是 requirements 依赖，也没有项目锁定的版本号；项目自有请求/解析适配器，不做代码自动同步。
- `easyquotation` PyPI 最新版为 0.7.7（2025-03-25）；[mpquant/Ashare](https://github.com/mpquant/Ashare) 仍是局部历史 K 线参考。两者均未作为项目运行时依赖或直接导入，不因上游文档/仓库更新而同步代码。
- [FTShare-Lab/FTShare-MCP](https://github.com/FTShare-Lab/FTShare-MCP) 对应的私有 MCP 集成已退役；不安装、不调用、不采集，也不作为碰撞锚。
- 项目早期参考仓库 [simonlin1212/a-stock-data](https://github.com/simonlin1212/a-stock-data) 当前最新仍为 v3.10.3；其 SSE 时间解析已在上一轮同步，v3.10.2 估值修复仍无本项目运行时代码对应项。
- 其余源的仓库关系、关系类型与确认状态继续以生成的 [`source_repository_map.md`](source_repository_map.md) 为准。本轮不编辑生成文件，也不把未确认关系扩大为“代码来源确认”。

## 依赖与维护规则

1. 本项目对经过兼容回归的 `levistock` 与 `axdata` 使用 requirements 精确版本；升级需更新该文件并先核对本项目实际调用点、返回结构、缓存路径和来源限流。
2. 上游新增功能先核对其数据日期、来源独立性、单位、限流和缓存契约，再决定是否接入；不得仅凭 changelog 标题改变生产路径。
3. 采用上游变更前，先确认本项目实际调用点和现有测试，再增加最小离线回归。真实网络适配器与本地 ZHB 统计 ZIP 的读取是两段不同路径，不能用本地 ZIP 测试替代对 live TDX 传输的验证；需真实网络验证时应单独安排并遵守限流。
4. Fuyao 响应组装时间不是竞价数据日期；`probe_trading_day` 只表示采集任务期望的数据日，不能填充缺失的源端日期。
5. 信封适配器使用新的缓存函数名，旧 list-only 缓存不含信封元数据，无法安全复用；升级后的相同参数首次调用可能回源一次。之后采集器和旧列表接口统一以 `stage` 关键字调用并共用信封缓存，不增加每轮采集请求。
