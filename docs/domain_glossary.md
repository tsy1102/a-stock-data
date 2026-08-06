# 领域词汇表 (Domain Glossary)

> 版本: v1.0 (2026-08-05)
> 来源: mattpocock/skills "shared language" 理念 (AGENTS.md v1.1 采纳)。
> 用途: 统一 Agent 与本仓库文档的术语口径,消除歧义(如 Col[13] 曾被误称"行业板块代码")。
> 更新: 发现新术语/口径变更时,先更新本表再改代码与文档。

---

## 1. 数据源

| 术语 | 定义 | 备注 |
|---|---|---|
| ZHB | zctt.cn 提供的通达信离线数据包(45+ cfg/dat 文件), T-1 数据 | 离线优先路由, 零网络风险 |
| TDX | 通达信 TCP 行情(经 mootdx/easy_tdx 适配层), 白名单 5 台 FULL 服务器 | 见 tdx_client.py `_EASY_TDX_PREFERRED_HOSTS` |
| 东财 | EastMoney HTTP 接口(push2/datacenter-web/reportapi 等域) | 各域风控独立, 见 sc_network |
| 腾讯 | qt.gtimg.cn 批量行情(60只/批, 进程内按交易日缓存) | `_tencent_batch_fallback` |

## 2. ZHB 数据文件

| 术语 | 定义 | 备注 |
|---|---|---|
| tdxstat.cfg | 全市场个股统计快照(35 字段: 涨跌幅/PE/5-60日涨跌/扣非净利润/员工数…) | Col[3]=pe_dynamic, Col[9]=pe_ttm; Col[12]=新股开板日/Col[13]=上市连板数(V16.2.18 破解); [17]=近20根K线/[18]=20日/[19]=近60根K线/[20]=60日 |
| tdxstat2.cfg | 全市场资金流向+板块归属(21 字段) | Col[13]=**T日特色板块**, 非行业(见 §4); Col[4]=疑涨跌停封单额 |
| profile.dat | 离线股票简称字典(代码→名称, 每日随 ZHB 更新) | `get_stock_name_from_zhb` |
| tdxzs3.cfg | 板块代码→名称映射(880xxx 通达信自建 604 个 + 881xxx 申万版 467 个) | `industry_map` |
| tipinfo.dat | 财报日历(EPS/披露日/除权除息/分红日) | |
| tdxchain.cfg | 概念板块成分股映射 | `get_concept_stocks` |
| spblock.dat | 大板块成分股(中证2000/沪深港通等) | |
| incon.dat | 证监会行业分类(门类 A-S, 仅字典无股票映射) | |

## 3. 行业分类体系

| 术语 | 定义 | 备注 |
|---|---|---|
| 申万二级 | **本项目行业统一口径**(V16.2.17 用户决策)。数据源=东财 datacenter `RPT_EM_BOARD_CONSTITUENT` type=2 排除一级名单后 code 最小的板块 | 例: 半导体/白酒Ⅱ/光学光电子/银行Ⅱ |
| 东财行业 | 东财自建行业(BK 板块), 一级 31 个(与申万一级同名)+二级 129 个+三级 | 非申万官方, 但二级与申万二级同源 |
| 通达信行业 | 8803xx/8804xx 段(880301 煤炭/880400 医药), TDX boards type=0/1/2 返回 | 自建体系, 非申万 |
| 881xxx | 通达信收录的申万版行业(467 个, 含一/二/三级混合) | 无现成一级映射, 无股票关联 |
| 特色板块 | tdxstat2 **Col[13]** 的 T 日条件筛选板块(微盘股/近已解禁/业绩预降…), 成员按当日条件归属、个股只取其一 → 每日变化/不全 | **非行业**, 不可用于行业聚合 |
| is_industry_code() | zhb_client 行业段判断: 仅 8803/8804/881 开头为行业 | Col[13] 过滤用 |
| get_em_industry_l2_data() | 东财申万二级映射 {code: 二级名} + {二级名: [成员]} | 缓存 `em_industry_map_l2.json`/`em_industry_members_l2.json`, 7 天 TTL |

## 4. 架构

| 术语 | 定义 | 备注 |
|---|---|---|
| canonical | CanonicalStockData 强类型数据合约, `get_canonical_stock_data()` 统一产出 | data_provider.py |
| field_sources | canonical 每字段的来源标签(如 realtime:em-datacenter / zhb) | |
| L0/L1/L2/L3 fallback | canonical 字段的多级兜底链(如 industry: L0 东财申万二级 → L1 push2 → L2 TDX → L3 ZHB) | |
| @cached | SQLite 缓存装饰器(category + 参数 key + TTL + trading_day) | stock_cache.py |
| 缓存版本号 | 口径/结构变更时必须升级 category(如 industry_peers → industry_peers_v2), 旧缓存不删除但不再读取 | **防污染铁律** |
| single-flight | 同 key 并发 miss 仅一次上游请求 | @cached 内置 |
| 限流桶 | TokenBucket + 全局时间戳协调; push2 系共享桶 0.4rps/2.5s, datacenter 1.0rps | sc_network |

## 5. 网络风控

| 术语 | 定义 | 备注 |
|---|---|---|
| push2 封禁 | push2 系域名连接级风控(RemoteDisconnected), 恢复需 **20h+** | 参考仓库 PR#36 实战结论 |
| _em_is_banned | 连续 3 次断连 → 标记封禁 → 自动跳过 20h 冷却 | |
| _FFLOW_HOSTS | 资金流多域轮换(push2his→push2→push2delay) | |
| 429 | 请求限频返回, 自动退避重试 | |

## 6. 报告

| 术语 | 定义 | 备注 |
|---|---|---|
| 六大报告 | mak(开盘前瞻)/val(价值)/sht(短线)/med(中长线)/lng(长线)/ful(全量) | main.py 编排 |
| 策略 01-20 | get_val_report 的 20 个选股策略(如 04=PE 估值回归) | 可配置 pool |
| real_network | pytest marker, 需真实网络的测试必须标注 | 离线默认跳过 |

## 7. 方法论

| 术语 | 定义 | 备注 |
|---|---|---|
| Fact-Forcing Gate | 改文件前必须调查导入者/调用方/数据契约/缓存影响/测试影响 5 项 | AGENTS.md §8 |
| 六阶段验证 | py_compile/mypy/black/测试/安全/diff | AGENTS.md §9 |
| 迭代度量 | 每次改动绑定可数机械指标, 报告填"度量"行 | AGENTS.md §11.1 |
| 假设驱动调试 | 症状→最小复现→侦察→假设→单次实验→判定→记录 | AGENTS.md §11.2 |
| roadmap ADR | docs/roadmap.md 的 V16.2.x 决策记录(结论+证据+修复) | 决策回溯依据 |
