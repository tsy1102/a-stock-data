# 字段实测验证流水线(Field Verification)

> V16.4.1 建立。目标: 用固定股票池的**每日实测数据**,定位 `field_dict.md` 中
> 错误/未知/推测字段,发现统一层未发现的格式与单位错误。

字段破解统一按 [`CRACKING_METHODOLOGY.md`](CRACKING_METHODOLOGY.md) 和 [`COLLISION_RULES.md`](COLLISION_RULES.md) 检查；碰撞候选经人工复核后，按 [`ADJUDICATION_WORKFLOW.md`](ADJUDICATION_WORKFLOW.md) 更新注册表。

## 原理

同一字段跨 20 只股票 × 多天的实测值呈规律分布(随状态/行业/日期变化);
字段解释错误时,实测值往往自相矛盾(单位差 10 倍/列错位/状态切换时突变)。
逐日记录 + 每日分析 = 让错误暴露。

## 目录结构

```
docs/field_verification/
├── pool.json          # 20 股股票池(固定 15 + 动态 5,动态层每日可换)
├── README.md          # 本文件
└── YYYYMMDD/          # 按天归档(自动生成: 由 capture_field_probe.py 每日创建, 按约定不单列 README; 内容见本文件"每日核查流程"与 collide.py 产物)
    ├── raw_<source>.json  # 每个有 producer 的来源各一份原始结果
    ├── meta.json          # 采集时段、来源状态、覆盖率、错误/deferred 与已知来源数据日
    ├── <date>_collision_report.md/.json  # 碰撞候选及其样本证据
    └── analysis.md        # 可选的人工综合分析
```

Fuyao raw 文件额外保留 `auction_snapshot_meta` 信封摘要；有竞价记录时，`auction_final.__source_meta__` 记录源端状态、响应时间、明确的数据日期和碰撞资格。响应 `timestamp` 与采集器的 `probe_trading_day` 都不能替代源端数据日期。只有源明确给出数据日期、与目标交易日相同且状态明确就绪的竞价子树才参与碰撞；其他 Fuyao 字段仍正常处理。历史 raw 没有这些标记时保留原行为。详情见 [`UPSTREAM_COMPATIBILITY.md`](../UPSTREAM_COMPATIBILITY.md)。

## 采集命令

```powershell
.\scripts\run_with_system_python.ps1 scripts\capture_field_probe.py                 # 采今天(用现有 ZHB 包)
.\scripts\run_with_system_python.ps1 scripts\capture_field_probe.py --date 20260812 # 指定日期目录
.\scripts\run_with_system_python.ps1 scripts\capture_field_probe.py --dry-run       # 连通性探测(会发请求,不生成每日 raw 样本)
.\scripts\run_with_system_python.ps1 scripts\capture_field_probe.py --refresh-pool  # 采集前刷新动态层(连板/新股/涨停)写回 pool.json
```

`--dry-run` 不是离线模式：它检查 ZHB/TDX，并对腾讯和 Eastmoney 发少量健康探测请求；它不生成每日 raw 样本。ZHB 客户端仍遵循自身缓存与刷新行为。

### 龙虎榜/人气榜上下文（按需）

默认字段采集和碰撞会排除龙虎榜、人气榜等市场上下文。需要采集这些数据时，可显式启用：

```powershell
.\scripts\run_with_system_python.ps1 scripts\capture_field_probe.py --include-context
```

采集时单独指定 `--only exchange` 或 `--only em_hot` 也会自动启用对应上下文：

```powershell
.\scripts\run_with_system_python.ps1 scripts\capture_field_probe.py --only exchange
.\scripts\run_with_system_python.ps1 scripts\capture_field_probe.py --only em_hot
```

碰撞不会请求网络；要将已归档的上下文数据纳入分析，运行时添加 `--include-context`：

```powershell
.\scripts\run_with_system_python.ps1 scripts\collide.py --include-context
```

## 采集请求与限流

- 来源按 `capture_field_probe.py` 的 producer 顺序串行执行，不通过并发扩大请求量。TDX TCP 与 HTTP 数据源分别沿用 `core/tdx_client.py` 和 `stock_common/sc_network.py` 的限流配置。
- Eastmoney HTTP 请求同时受域级限流和跨进程全局节奏约束。本轮调整的 push2、clist、slist、ulist239、K 线与资金流直连请求均为单次尝试；push2、clist、slist 遇 IP 封禁/HTTP 403/429 或同域连续失败时，本轮熔断该域，只在另一域仍可请求时使用既有备用路径。其他经统一适配器访问的来源继续使用适配器自己的限流和重试策略。
- 不为补齐样本并发或快速重试失败源。封禁、限流或连续传输失败会保留诊断并停止对受限域追加请求；应先检查 `meta.json`，来源恢复后使用 `--only <source>` 定向重采。`--only` 会实际重新调用所选来源，不会因已有快照跳过。
- 避免重复启动完整采集进程；不同数据源有各自的域级限流，重复运行会增加不必要的请求。

> **动态层每日刷新（V17.2.10）**：`pool.json` 的 `dynamic` 5 只此前静态冻结（自 20260812）。
> 现由采集脚本 `--refresh-pool` 在采集前自动从涨停池（同花顺 `ths_limit_up_pool`，东财兜底）挑选
> 5 只连板/新股/涨停写回 `dynamic`（`date=最近交易日`），固定层 15 只不动。
> 网络不可用时保留旧动态层。建议每日命令：`.\scripts\run_with_system_python.ps1 scripts\capture_field_probe.py --refresh-pool`。

## 每日核查流程(固定)

1. 跑采集脚本(耗时随股票池、来源响应和限流等待变化；会访问配置的来源)
   ```powershell
   .\scripts\run_with_system_python.ps1 scripts\capture_field_probe.py --refresh-pool   # 刷新动态层(连板/新股/涨停)再采集
   ```
2. **跑全源对撞(通用引擎)**——每次运行按当前字典状态选择待破解字段和 verified 独立锚:
   ```powershell
   .\scripts\run_with_system_python.ps1 scripts\collide.py                 # 默认近 7 天窗口，全源全字段完整对撞
   .\scripts\run_with_system_python.ps1 scripts\collide.py --window 14     # 近 14 天窗口
   .\scripts\run_with_system_python.ps1 scripts\collide.py --all           # 全部历史日期
   .\scripts\run_with_system_python.ps1 scripts\collide.py --date 20260913 # 指定报告日期戳（默认今天）
   ```
   产物：碰撞报告 `.md` + `.json`，只记录发现，不直接修改注册表或字典状态。
3. 检查报告使用的交易日/自然日、ZHB 实际数据日期、样本覆盖和来源独立性；日期必须从样本元数据和项目交易日历确认，不能机械地把 ZHB 日期当作运行日的前一自然日。规则见 `collision_dates.py` 与 `CRACKING_METHODOLOGY.md`。
4. 结合 `CRACKING_METHODOLOGY.md`、上游字段定义和原始样本逐项复核候选。L1/L1-U 只是可审查候选；L4、探索模式和缺少独立锚的结果不得晋级。
5. 将人工结论记录到 `field_verification/adjudications/`，先运行 `scripts/apply_collision_adjudications.py` 预览；检查字段来源、完整路径、语义、单位和证据后再加 `--apply`。该工具同步 registry 与生成文档，不手改 `field_dict.md`。
6. 应用后运行注册表 parity、字典同步闸门和对应测试。字段定义冲突须先单独解决，不能用碰撞结果覆盖 `conflict`。
7. **⚠️ 命名仲裁守卫（强制阻断, 2026-09-09 固化）**: 任何正式字段命名变更前后均须运行
   `.\scripts\run_with_system_python.ps1 scripts\lint_field_same_number.py --strict-naming`。
   该模式将 **R3 命名缺口升为阻断级（exit≠0）**；**若报 R3 缺口,禁止回写 field_dict.md**,
   须先补登 §12.8.12e 规范表或加数值二级复核标记,再重跑直到 exit 0。
   （默认不带 `--strict-naming` 为 warn 级、不阻断,用于日常检视。）

## 源与限流(依据 sc_network._DOMAIN_LIMITS)

| 源 | 限流 | 备注 |
|---|---|---|
| ZHB | 本地解析 | tdxstat 35 字段/tdxstat2 21 字段/tipinfo 22 字段 |
| TDX TCP | 100ms | 5 台 FULL 白名单 |
| TDX F10 | 100ms | 财务分析/股本/分红(V16.4.1 起) |
| 腾讯 qt.gtimg | 5rps | 批量 60 只/请求,单股 88 字段 |
| 东财 push2/push2delay | 0.4/1.0rps | 全字段 114 字段(f1-f250 显式,push2delay 兜底) |
| 新浪 hq.sinajs | 5rps | 34 字段,需 Referer |
| AxData | 零网络 | 短线指标 34 字段,直读项目 zhb.zip |
| 财联社/KPL/板块轮动 | 3/5rps | 市场级:情绪/涨停天梯/涨停明细/盘口异动 |
| thsdk | 正式账号 | 仅盘中可用(收盘后服务器拒绝) |

## 源覆盖状态(历史快照: 2026-08-26, 19 raw 文件)

> 本节记录的是 2026-08-26 的历史采集状态，不代表当前 producer 清单或当前可用性。当前运行结果以对应数据日的 `meta.json` 和 raw 文件为准；逐源状态、错误、deferred、覆盖率与可确认的来源数据日均以 `meta.json` 为准。

- ✅ 已采(19 源): ZHB / TDX(TCP+F10×6) / 腾讯 88 / push2_full(114) / ulist239(239 批量) / 新浪 34 / AxData 34 / 财联社(情绪+快讯) / KPL / 板块轮动 / thsdk(仅盘中) / push2ex 涨停炸板池 / 东财人气榜 / datacenter(两融/北向/解禁) / 巨潮互动易 / 研报 reportapi / 龙虎榜 / fuyao(竞价/池/财务指标/估值) / FTShare(千股千评/董监高/商誉/质押)
  - 已归档日期: 20260812~20260826(工作日连续, 8/16-18 缺采)
- ⏳ 待采 / 已知限制:
  - **TdxQuant(官方)**: 需**启动通达信客户端登录**(C:\new_tdx64\TdxW.exe)后在 PYPlugins 环境运行 `user\field_verify_tdxquant.py`(模板已就绪)——8/4 字典 Col[11]/[24]/[25]/[34] 官方确认即此通道
  - **thsdk**: 仅盘中 9:30-15:00 可用(非交易时段行情网关关闭, 服务器策略)
  - **push2 主域**: 偶发 20h 封禁冷却(2026-08-26 实测全 __error__), push2delay 镜像域正常
  - **ZHB 盘后**: 数据日期恒为 T-1(20260826 采集时=20260825), 需盘后强制同步才刷新

## 破解里程碑

- **2026-08-29 (完整复破解轮)**: 2 项旧假设证伪 + 1 项新结论 + 1 项**自我撤回**（数据 `zhb_20260828` + `20260828/` 19 源）
  - ❌ **腾讯[86]: 恢复 ❓未知**——"主力净买/大单净量(手)"**证伪**(符号∝涨跌仅 40%; \|[86]\|/总手 0.0011);
    **第一版误判的"委差"已撤回**(Pearson +0.965 系 601288 单点绑架: Spearman **−0.012**、留一 Pearson **−0.863 翻号**、对撞精确/1% 均 **0/20**)
  - ❌ **tdxstat[2]: 资金净流入强度证伪**，"量比/换手率"降为 **L4 极弱候选**(Pearson +0.082 / Spearman **−0.371** 异号, 不达标)
  - ✅ **tipinfo[7] = 价格异动标记日 L3**(涨停15.1%/放量33.7% vs 基线1.3%/8%; 除权除息·解禁·财报披露日全 0%)
  - ⚠️ **腾讯[85]: 收紧为"价格类字段" L3 弱**(精确对撞 0/20; 1% 容差 16/20 命中卖一/卖二价族 → 仅证明价格族, 不等于参考价/结算价)
  - ✅ 清理陈旧条目: P1-3([20]/[22]/[23])·P1-4([26]) 实为**已破解**字段, 非未知
  - 🔧 **规则校正**: 对撞规则(用户定义, 唯一一条) = **扫描同日不同源返回的相同数字的字段, 其一已破解则反推同值未知字段即该字段**; 即**同日跨源逐股精确数值相等**(≥8/20), 非"相关性"; 相关性须 Pearson+Spearman 同号且 \|ρ\|>0.6 且留一不翻号
  - 🔧 **表述撤回**: 曾把"**同序号 ≠ 同字段**"写成用户设定的规则 —— **已撤回**。用户未设此规则; 序号只是字段的一种表现形式, "不能单独因序号/字段名一致就默认不同源同序号代表同一字段"属于对对撞规则的**边界澄清**, 不是独立规则
  - 详情: `20260829/analysis.md` | 主程序: `scratch/crack_0829_v3.py` | 对撞扫描器: `scratch/collide_0829.py`
- **2026-08-28 (V17.0.11)**: push2 f86 **破解 = 当日收盘/最后行情时间戳**（Unix 秒）
  - 多日序列逐日+86400(600519: 1787645498→1787904720); 全 20 股换算=当日收盘时刻
  - 复核: f85=流通股本(股)(F10 实际流通A股 1.0000 精确)、f173=加权ROE(fuyao H1 三样本精确)
  - 中报指标入库 18 只(tx65/tx66 终判条件达成)
  - 详情: `20260828/analysis.md`
- **2026-08-27 (V17.0.10b)**: tdxstat Col[33] **破解 = 连板数**（原"涨停类型族 ztlx"证伪）
  - 日期对齐对撞法（用户指引）: 今日采集 ZHB(8/26) 与 8/27 报告天梯对撞, type **20/20 完全匹配**
  - 当日涨停时 Col[31]/[32]/[33] 三字段一致=连板数; 非涨停日 type=None/0, count=累计次数, lianban=历史高位
  - 同步: field_dict Col[31]/[32]/[33] 对撞补强
  - 详情: `20260827/analysis.md`
- **2026-08-26 (V17.0.9)**: tdxstat Col[24] **终极破解 = 货币资金(万元) cash_reserve_wan**
  - F10 资产负债表「货币资金」逐股对照: 600519=535.188亿(100%一致), 17 只有数据全匹配(14 最新期精确+2 报告期差)
  - 跨日恒定根因: 财报季度才更新(静态财务字段); 历史"成交量/总负债/股本"三假设全部证伪
  - 同步: zhb_client 正名 / data_provider·tdx_client 注释 / test_data_zhb 断言 / field_dict 7.3 节+P0-1 关闭
  - 详情: `20260826/analysis.md`

## 已确认待办

- [x] 2026-08-12 首次采集(20 股,4 源;push2 半恢复 8/20,见当日 analysis.md)
- [x] 2026-08-12 源补强(10 源: +push2_full 114 字段/新浪/AxData/财联社/KPL/板块轮动/TDX-F10)
- [x] 2026-08-26 tdxstat Col[24] 破解=货币资金 cash_reserve_wan(V17.0.9)
- [ ] 中报(2026H1)全面披露后复查 600675/688500 cash_reserve_wan 翻期
- [ ] thsdk 盘中补采(9:30-15:00)
- [ ] push2 主域封禁解除后补采对照 f162/f167 估值字段
