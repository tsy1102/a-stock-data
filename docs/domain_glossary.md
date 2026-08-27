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
| tdxstat2.cfg | 全市场资金流向+板块归属(21 字段) | Col[13]=**T日特色板块**, 非行业(见 §4); Col[4]/[6]/[8]=**limit_up_down_seal 涨跌停封单额三日滚动**(万元, 涨停正/跌停负, V17.0.5 铁证); Col[11]=**change_mtd 本月至今涨跌幅**(基准=上月末收盘, V17.0.5 铁证) |
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

## 5.5 数据源接口与调用链（V16.3 L 补录：字典接口维度）

> 原则：**优先本地(ZHB) → TCP(TDX/MAC) → 腾讯 → push2(仅无替代时)**。
> 本表记录各接口可用性、码体系与 fallback 链——**字段字典之外的"接口可用性/调用链"维度**。

### 数据新鲜度分级（V16.3 M 用户原则固化）

> ZHB 数据 = 文件名日期的**前一个交易日（T-1）**；盘前（<09:30）/非交易日运行 T-1 满足目的，
> **9:30-24:00（含盘后——当日收盘后 ZHB 仍是 T-1，次日凌晨才更新）需实时**。
> 按字段精度分级决定 ZHB 使用策略：

### ZHB 全字段归类总表（V16.3 N：42 字段全集核对，无遗漏）

> 元数据（code/date/market）不参与分级。规则：**随当日变化→A；日内变化小但随交易日→B；
> 历史/季度/静态→C；参照系→D**。新增破解字段按下表规则归类（见"字段分级规则"）。

| 级 | 字段 | 说明 |
|---|---|---|
| **A 即时** | price① / change_pct / amount / volume① / open① / high① / low① / prev_close① / main_net_buy_amount / main_net_buy_hands / turnover_pct / streak_days | 价格/当日涨幅/当日成交/当日主力/换手/连涨（①为 TDX/腾讯实时字段，ZHB 无或仅兜底）|
| **B 中精度** | pe_ttm / pe_dynamic / pb① / dividend_yield / mcap① / change_ytd / **change_mtd** / change_5d / change_10d / change_20d / change_30d / change_60d / **change_5k_bar / change_10k_bar / change_20k_bar / change_60k_bar** | 估值/股息/市值/阶段涨幅（含近 N 根 K 线口径；change_mtd=本月至今, ZHB tdxstat2 Col[11]）|
| **C 静态** | high_52w / low_52w / total_shares① / float_shares① / employee_count / ipo_price / industry① / industry_code / board① / concept① / eps / roe① / net_profit① / revenue① / **net_profit_kcf / unknown_24(现金总额) / board_count / unseal_date / amount_1d / amount_2d / main_net_buy_amount_1d / main_net_buy_hands_1d / change_pct_1d / change_pct_2d / disclose_date / report_period / div_date / div_amount / ex_date** | 股本/52周/行业/财务/历史序列（昨日/前日值、T-1 主力、连板数、开板日、分红财报）|
| **D 参照系** | （派生，非 ZHB 字段）| 行业排名/板块聚合/指数对比 |

> ① = 非 ZHB 直接字段（REQUIRES_REALTIME_HTTP 或派生）；ZHB 直接字段见左侧全集。
> **V16.3 N 补全**：上表为 42 字段全集核对结果——B 类补近 N 根 K 线（change_*k_bar）；
> C 类补历史序列（amount_1d/2d、main_net_buy_*_1d、change_pct_1d/2d）、财务
> （net_profit_kcf/unknown_24）、次新（board_count/unseal_date）。

### 字段分级规则（新增破解字段的处理流程）

**field_dict.md 新增字段条目时**，除字段含义/来源/破解证据外，**必须标注新鲜度分级**（A/B/C/D），判定流程：

```
1. 该字段是否随当日交易变化（价格/涨幅/成交/资金流/换手/连涨）？ → A
2. 否——是否日内变化小但逐交易日更新（估值/股息/市值/阶段涨幅）？ → B
3. 否——是否历史值/季度财务/静态股本（昨日/前日序列、扣非净利、52周、行业）？ → C
4. 否——是否仅作参照系/聚合对比用途？ → D
5. 无法判断 → 先归 C（最保守，ZHB 无条件用），破解语义后再修正
```

**落库位置**：field_dict.md 字段表加"分级"列（新增字段必填）；本总表为汇总索引。
**时段保护范围**：A 类字段的 ZHB 分支加 `_should_use_zhb_for_realtime()`（9:30-24:00 拒绝 T-1）；
B/C/D 类不做时段保护（T-1 可接受或无条件）。
**用户决策记录**：换手率/连涨天数归 A；市值归 B；财务/行业/静态股本归 C；
ZHB_SUFFICIENT 路由集为"ZHB 有无此字段"的静态声明不做移出（移出会导致盘前也不允许 ZHB），
正确机制是运行期时段保护。

> **教训（"太严格"实证）**：data_provider get_stock_composite 原 max_delay=1 打包 C 类字段——
> 周一盘前 ZHB=上周五（延迟>1 天）→ C 类字段（股本/52周/行业）被拒绝走网络（白白请求 + 可能 push2）。
> V16.3 M 已拆分级：C 类无条件 ZHB，B 类 max_delay=3，A 类兜底 max_delay=1；lng 同步拆分。

### 多源 fallback 顺序核查结论（V16.3 N 核查 → V16.3 O18 修正）

> 原则（O18 修正，依据参考仓库 v3.2 + 实测）：**同字段多源时按"易→难"**——
> ZHB(本地零网络) → TDX TCP / 腾讯(不封 IP 首选) → 新浪/巨潮(低风险) → 同花顺(有 401 反爬史) →
> AxData(local 未充分验证) → 东财(最难：45000/h 封禁 20h + 观察期 + 共享风控，仅独有数据)。

> **V16.3 O18b 补充——"易→难"是双维度**：
> ① **封禁风险**（上表）② **获取模式匹配**（批量单字段 vs 逐股多字段）——
> 全市场扫描（val/mak）优先批量接口（腾讯批量 60/批），单股深度（sht/lng/med）优先 TCP 逐股
> （一次全字段）——排序时两维度同时看，详见 field_dict 12.15「数据获取模式维度」。

| 字段/功能 | 实际顺序 | 判定 |
|---|---|---|
| 行情（price/涨幅/成交/换手）| TDX → 腾讯 → push2（canonical L1/L2/L3）| ✅ 易→难 |
| 估值/股息/股本/52周/阶段涨幅 | ZHB 优先 → 实时兜底 | ✅ ZHB 易 |
| 行业 | TDX boards(TCP) → ZHB profile.dat → 东财 f127/push2（**仅当行情已走 push2 时零成本**）| ✅ O18 修正（原 datacenter 第一）|
| 概念 | ZHB tdxchain(本地) → TDX boards(TCP) → 东财 push2 f129（免费副产品）| ✅ O18 修正（原 push2 在 ZHB 前）|
| 板块地域 board | TDX boards → 东财 push2 f128（仅当行情已走 push2 时零成本）| ✅ O18 修正 |
| 资金流 120 日 | TDX → 东财（get_history_fund_flow_120d prefer=auto）| ✅ |
| 股本/上市日(get_stock_info) | TDX finance → capital_cache(TDX→push2) → push2 | ✅ TDX 优先 |
| 龙虎榜/北向 | datacenter(东财独有数据) → 备胎(szse/sse urlopen) | ✅ 独有数据用东财 |
| 名称 | 腾讯批量 → ZHB profile → 东财批量 | ✅ |
| 同业对比 | 东财 L2 成员(datacenter 缓存) + 腾讯批量行情 → TDX → F10 | ✅ |
| 板块成员 | MAC TCP → push2（条件触发，mak 已 ZHB 旁路）| ✅ |

**"免费副产品优先"规则（O18 限定）**：rt_quote/em_quote_raw 是行情请求已返回的字段（零额外请求）——
**仅当行情本身已走 push2（说明前面 ZHB/TDX/腾讯全失败）时才适用**——f127 行业/f128 地域/f129 概念/f44/f45 52周
随行情响应免费附带；**行情正常走 TDX 时，行业/概念必须回 TDX/ZHB 主链，不得因"免费"主动发起 push2**。
这是"从易到难"的扩展定义（成本维度），与 O18 源排序不冲突。

### 接口可用性实测（2026-08-06）

| 接口 | 协议 | 可用性 | 粒度/覆盖 | 备注 |
|---|---|---|---|---|
| ZHB tdxstat/tdxstat2/tipinfo | 本地文件 | ✅ 全量 7964 只 | 35/21/22 字段 | 零网络 |
| ZHB 申万二级聚合（_build_sectors_from_zhb）| 本地 | ✅ 129 板块全成员 | 申万二级 | mak 板块聚合主源（V16.3 L）|
| easy_tdx StdQuotes（行情/K线/财务）| TCP 0x010C | ✅ 白名单 5 台 | 全市场 | 行情主源 |
| easy_tdx MacClient（板块）| TCP MAC | ✅ 白名单 host 可用 | **56 个通达信行业** | 板块归属/成员（880xxx 码）|
| 腾讯 qt.gtimg.cn | HTTP | ✅ 全市场批量 | 60只/批 | 名称/行情/补名 |
| 东财 datacenter-web | HTTP | ✅ | 行业映射/龙虎榜等 | 低风控域 1.0rps |
| 东财 push2 系 | HTTP | ⚠️ 风控敏感 | 13 个入口 | **最后手段** 0.4rps/20h 冷却 |

### 码体系（BK↔880 不匹配是风控放大根因）

| 码 | 来源 | 示例 |
|---|---|---|
| **880xxx** | 通达信板块（MAC board_list/board_members/belong_board 同体系）| 880301 煤炭/880492 元器件 |
| **BKxxxx** | 东财板块（clist/stock/get）| BK1625 钨 |
| 881xxx | 通达信收录申万版（ZHB tdxzs3）| 881001 煤炭 |
| 申万二级名 | 东财 datacenter L2 映射（本项目统一口径）| 光学光电子/白酒Ⅱ |

⚠️ **tdx_get_board_members(BK码) 会失败**（MAC 只认 880xxx）→ fallback push2 clist 每板块 1 次
→ mak 100 板块 = 100 次 push2 = 风控放大。**教训：跨体系码不可直接互查**。

### push2 入口清单（13 个，2026-08-06 审计）

| 入口 | 接口 | 调用场景 | 替代性 |
|---|---|---|---|
| get_em_quote_full | stock/get | canonical L3 行情兜底（TDX/腾讯失败才用）| 条件触发 ✅ |
| eastmoney_stock_info_push2 | stock/get | 股本/上市日兜底（TDX 失败才用）| 条件触发 ✅ |
| get_em_belong_boards | stock/get | tdx_get_belong_boards 兜底（MAC 失败才用）| 条件触发 ✅ |
| get_em_batch_quotes | ulist 批量 | 补名/批量行情 | 腾讯批量可替代（评估中）|
| _get_eastmoney_industry_sectors | clist | 行业排名 | ZHB 旁路可替代 |
| get_board_fund_flow | clist | 板块资金流 | ZHB 旁路已替代（mak 主流程）|
| get_em_board_list | clist | tdx_get_board_list 委托（低频 1 次）| 保留（低频）|
| get_em_board_members | clist | tdx_get_board_members 兜底 | 条件触发 ✅（mak 已走 ZHB）|
| 涨停/炸板/跌停/昨日涨停池 | push2ex | mak/sht 涨停池 | **无替代，保留** |
| em_hot_rank | ulist | 人气榜 | **无替代，保留** |

### 报告脚本板块链路（V16.3 L 后）

| 脚本 | 板块聚合 | push2 依赖 |
|---|---|---|
| mak | **ZHB 旁路优先**（129 申万二级，腾讯实时涨跌幅）→ TDX 兜底 | **零**（板块路径）|
| sht/med/lng | TDX MAC belong_board（880xxx 同体系 ✓）→ 东财兜底 | 仅 MAC 失败时 |
| lng/val 行业排名 | tdx_get_board_list（东财 clist 低频 1 次）| 1 次/脚本 |

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
