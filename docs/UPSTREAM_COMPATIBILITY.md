# 上游仓库与兼容性复核

> 复核日期：2026-10-08。仓库对应关系以生成文档 [`source_repository_map.md`](source_repository_map.md) 和逐源完整路径登记为准；本文件记录本轮确实影响依赖、采集路径或字段解释的更新结论。GitHub 项目是实现参考、客户端或传输工具时，不据此推断其拥有底层行情，也不把包装库当成独立碰撞来源。

## 本轮相关仓库与结论

| 仓库/项目 | 本项目中的实际边界 | 本次核对 | 采用结论 |
|---|---|---|---|
| [HiThink-Tech/Financial-API](https://github.com/HiThink-Tech/Financial-API) | 用户确认的 Fuyao 上游参考；本项目直接请求 Fuyao REST，不安装或调用该仓库 SDK。 | 仓库迁移到 monorepo 的说明及 2026-09-20 前后的更新记录；竞价能力近期有更新。`auction/snapshot` 返回响应信封，当前契约没有明确的源端数据日期，响应 `timestamp` 是响应时间。 | 不复制 SDK、不增加请求。采集保存关键响应元数据；只有上游明确给出数据日期、日期与目标交易日一致且状态明确就绪时，竞价子树才参与对撞。Benchmark 请求仍显式传入目标交易日。 |
| [yanwei99521/easy-tdx](https://github.com/yanwei99521/easy-tdx) | 用户确认的 TDX 客户端及 ZHB 三类缓存的传输/读取工具；不代表仓库托管 ZHB 数据本体，也不是独立行情提供方。 | requirements 固定到提交 `41e56376fafa3abae0f6538f271eafd6af26d27f`；本次复核未发现该固定提交之后有需要本项目吸收的代码变化。 | 保留固定提交和 vendored wheel，不升级；按既有 TDX 限流使用。 |
| [electkismet/eltdx](https://github.com/electkismet/eltdx) | 用户确认的 TDX 协议客户端适配层；与 TDX 属于同一来源族。 | 当前环境为 `eltdx 3.2.2`，上游复核版本为 `3.2.3`。新增退市日线/校验及更早可用的板块行情能力；本项目当前未调用这些入口。 | 本轮不升级、不增加来源锚。将新能力留作后续候选，接入前需补契约与离线/真实网络验证。 |
| [fleetinglife/levistock](https://github.com/fleetinglife/levistock) | 用户确认的多源客户端包装库；用于部分 Eastmoney/财联社相关实现参考，不代表独立底层数据源。 | 系统环境原为 `levistock 0.1.7`；隔离回归了 `0.1.8`。项目实际调用 `market_emotion_cls()`、顶层 `get_zttt(date=...)`，以及 `levistock.stock.stock_fupanla_kph.get_zttt()` / `get_pmsl()`；签名和返回结构与适配器一致。0.1.8 唯一 Python 源码差异是项目未调用的 Eastmoney 股票分页间随机延迟。 | requirements 精确固定 `levistock==0.1.8`。离线回归覆盖真实方法路径、日期参数和 11 列涨停行归一化；不把包装来源重复计为独立证据。 |
| [electkismet/AxData](https://github.com/electkismet/AxData) / [AxData on PyPI](https://pypi.org/project/axdata/) | `axdata` 发行包内含 `axdata_core` 与 TDX 源适配器。短线指标的 `tdxstat.cfg` / `tdxstat2.cfg` 统计资源来自项目本地 ZHB ZIP；其余实时快照、日 K 和财务输入仍可能访问 TDX 网络。 | 系统环境原为 `axdata 0.1.3`；隔离回归了 `0.1.4`。显式 `stats_root` 会直接加载 ZIP 并返回 `refreshed=False`，不刷新/下载统计包。0.1.4 的统计资源解析与该分支未变；另有 TDX 连接池/请求分发改动。单股票调用不触发其多代码并行快照条件。AxData 包及 GitHub 仓库标示 Apache-2.0；这与 `eltdx` 的许可声明分开记录，数据源自身条款仍需独立遵守。 | requirements 精确固定 `axdata==0.1.4`。离线回归通过真实 AxData ZIP 读取器与 `request_interface` 契约、注入无网络适配器；未验证真实 TDX 连接或行情返回，不声称 live transport 已回归。 |
| [simonlin1212/a-stock-data](https://github.com/simonlin1212/a-stock-data) | 用户确认的项目早期参考仓库；不是本项目的运行时依赖或自动同步源。 | 上游 [v3.10.1 CHANGELOG](https://github.com/simonlin1212/a-stock-data/blob/main/CHANGELOG.md)（2026-10-07）只更正文档：腾讯 K 线的科创板成交量单位、分钟字段位置等；未改变 K 线返回值。该版同时复审并修复腾讯逐笔：复用会话、对连接/握手/响应头超时及 429/5xx 退避重试（不重试 403 或响应体读取超时），新增基于快照盘后成交额的 `frame.attrs["complete"]` 三态完整性标记。 | 本轮将逐笔会话复用、限范围重试和完整性判定移植到本项目，并以离线测试覆盖。对上游文档中逐笔金额阈值、调用耗时和 live 实测不作本项目已验证声明；期货 K 线的重试调整未移植。腾讯 K 线文档更正与本项目当前路径无关，不改其字段契约。 |

## 其他更新的处理

- `easyquotation` 本次可见更新属于文档说明，没有发现会改变本项目现有请求或解析契约的代码变化。
- Ashare 类项目在本仓库中属于参考材料，不是采集器当前运行时调用的依赖；不因上游参考仓库有更新而自动同步代码。
- 其余源的仓库关系、关系类型与确认状态继续以生成的 [`source_repository_map.md`](source_repository_map.md) 为准。本轮不编辑生成文件，也不把未确认关系扩大为“代码来源确认”。

## 依赖与维护规则

1. 本项目对经过兼容回归的 `levistock` 与 `axdata` 使用 requirements 精确版本；升级需更新该文件并先核对本项目实际调用点、返回结构、缓存路径和来源限流。
2. 上游新增功能先核对其数据日期、来源独立性、单位、限流和缓存契约，再决定是否接入；不得仅凭 changelog 标题改变生产路径。
3. 采用上游变更前，先确认本项目实际调用点和现有测试，再增加最小离线回归。真实网络适配器与本地 ZHB 统计 ZIP 的读取是两段不同路径，不能用本地 ZIP 测试替代对 live TDX 传输的验证；需真实网络验证时应单独安排并遵守限流。
4. Fuyao 响应组装时间不是竞价数据日期；`probe_trading_day` 只表示采集任务期望的数据日，不能填充缺失的源端日期。
5. 信封适配器使用新的缓存函数名，旧 list-only 缓存不含信封元数据，无法安全复用；升级后的相同参数首次调用可能回源一次。之后采集器和旧列表接口统一以 `stage` 关键字调用并共用信封缓存，不增加每轮采集请求。
