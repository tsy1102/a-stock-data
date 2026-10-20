# A股个股分析报告生成系统

一套自动化生成A股个股分析报告的Python工具集，支持短线、中线、长线、估值、市场热点等多种报告类型，数据来源于通达信（TDX）、东方财富、腾讯、新浪等主流平台。

---

## 功能特性

- **已验证字段作为碰撞锚**：只有含义完整、无占位、含义/单位无冲突且路径对齐无歧义的逐源记录才可作为锚；仅有 `verified` 状态不足以成为锚。碰撞定案会写入逐源 registry 与跨源映射，后续运行可跳过已定案字段对，将其用于未知字段对撞。已登记但缺少语义的字段可在证据充分时只补元数据；完整验证字段可只登记映射，不重写原定义；锚定义有误时保留前后值和独立证据。2026-10-14 已据三日历史样本确认 9 个 Ulist239 财务字段、补齐 1 个 TDX 字段定义，并登记腾讯流通股本关系；不会因此增加每日请求或改动五大报告路由。详情见 [`定案同步流程`](docs/field_verification/ADJUDICATION_WORKFLOW.md) 与 [`字段证据记录`](docs/field_verification/20261014/20261014_finance_field_adjudication.md)。
- **缺少同字段锚时仍可验证**：有固定上游契约时可确认单源定义；没有直接契约但存在可复算公式时，可用独立来源、已验证输入和留档 CSV 样本审定目标字段。公式证据不创建字段映射，不停止采集；日期、单位、来源独立性和误差门槛见 [`定案同步流程`](docs/field_verification/ADJUDICATION_WORKFLOW.md)。
- **FTShare 日常语义锚**：旧私有托管 MCP/SDK 已退役，15 条旧字段和历史 raw 仅作归档。公开 REST 网关的 `A股行情列表` 已接入日常字段采集，输出 `raw_ftshare_rest.json`；官方文档列出的 31 个返回字段已登记为契约语义锚，并在默认碰撞中与项目字段比较。达到多日匹配门槛的结果单列为 `L1-C`，表示语义有官方契约支持、但底层来源独立性尚未确认；它不混入独立来源 `L1/L1-U`，也不自动定案。接口是实时报价快照，采集器会校验有效交易日，不把盘中值伪装成历史收盘值；`symbol_id` 是一次响应中观察到但官方字段表未定义的字段，仍为未确认且不作锚。套餐目录及字段定义见 [`FTShare REST 契约目录`](docs/ftshare_contract_catalog.json) 和 [`FTShare REST 采集与碰撞契约`](docs/verify/ftshare_rest_contract.md)。凭证从被 Git 忽略的 `credentials/ftshare_api_key.txt` 读取，也可用 `FTSHARE_API_KEY` 环境变量覆盖；限流和失败策略见 [`采集脚本说明`](scripts/README.md)。
- **5 种报告类型**：短线(sht) / 中线(med) / 长线(lng) / 估值选股(val) / 市场状态(mak)（ful 已于 V16.1 下线，能力并入前四类）。
- **字段聚合复核**：主字典按来源和完整路径保存定义；同一短 code 出现异义或定义缺口时单列到 [`field_aggregate_review.md`](docs/field_aggregate_review.md)，疑似复合文本只提示人工核实，不自动拆分或改变逐源状态。
- **每日证据覆盖**：采集脚本在新采集和幂等跳过时，都会只读现有归档，更新最近 7 个有效交易日的待确认字段覆盖摘要。精确来源日期、事件自然日、来源状态和身份歧义分开记录；不会联网补请求或自动升级字典状态。仅含日期与样本数的明细保存在被 Git 忽略的 `.tmp/field_evidence_coverage/`。规则见 [`字段证据覆盖`](docs/field_verification/EVIDENCE_COVERAGE.md)。
- **破解状态不关闭采集**：字段达到定案状态后，只从未知字段的重复破解目标中移出，并继续作为碰撞锚；每日采集器仍按来源路由持续采集这些字段，用于监测偏差和验证来源稳定性。只有来源身份被证实为运行上冗余、或接口明确暂停/待验证时，才按来源生命周期规则处理请求。
- **多源字段逆向破解**：ZHB / TDX 0x0010 / 东财 push2delay（单股失败时才回退主域 push2）/ 腾讯 / 新浪 / 同花顺 fuyao / 巨潮等来源交叉验证。字段状态按源与完整路径保存在机器权威 registry；[`field_dict.md`](docs/field_dict.md) 提供导航，[`unknown_fields.md`](docs/unknown_fields.md) 列出日常破解队列，[`field_metadata_gaps.md`](docs/field_metadata_gaps.md) 暴露已验证字段的描述缺口，[`field_matrix.md`](docs/field_matrix.md) 和 [`source_repository_map.md`](docs/source_repository_map.md) 分别展示来源矩阵与仓库谱系。碰撞报告只提供候选，显式记录全历史或近 N 个交易日的窗口配置；“首次发现候选对”表示状态台账首次记录，不代表字段语义已定案。人工复核后按 [`定案同步流程`](docs/field_verification/ADJUDICATION_WORKFLOW.md) 更新状态。
- **主字典来源质量审计**：2026-10-18 检查了 2,481 条逐源路径，其中 917 条登记为 `verified`；714 条通过元数据可用性检查，203 条因含义缺失/占位、冲突或对齐歧义暂不作为碰撞锚。该统计是元数据门禁，不代表对字段真实含义的最终裁定。完整逐源结果见 [`来源质量审计`](docs/field_verification/field_source_quality_audit_20261018.md)；可用 [`audit_field_source_quality.py`](scripts/audit_field_source_quality.py) 重跑只读审计。
- **探索候选持续继承**：碰撞脚本使用 `--exploratory` 时，将 L1、L4 和方法候选按字段对写入 `docs/field_verification/collision_research_state.json.gz`，保留每次观察的完整证据、日期与报告位置；台账以 gzip 存储，只从磁盘副本删除可重建的 latest_evidence。后续报告会标出历史复现，避免每次从零审阅；同一日期、报告路径、窗口和上下文范围的重跑会替换该次观察，不重复累计。带 `--include-context` 的探索报告单独存放。探索台账只保存研究历史，不自动确认字段；只有人工复核并显式应用的正式决定才会更新主字典。
- **日期感知的跨源对撞**：行情按有效交易日对齐，新闻/公告按自然日处理；保留历史休市目录，按实际数据日期择优快照，并让候选证据记录样本日期与来源。字段破解采集和碰撞默认排除龙虎榜、人气榜等市场上下文；其余数值字段照常采集，历史 raw 保留。AxData 的 KPH 接口（底层来源族为 KPH）作为 KPL 名单的补充接口，不替代 KPL；六组双交易日对撞确认字段已登记为锚。采集上下文可添加 `--include-context`；采集时单独指定 `--only exchange` 或 `--only em_hot` 也会自动启用对应上下文。采集启动行会显示实际源选择和上下文状态。碰撞时添加 `--include-context` 可将已归档的上下文数据纳入分析。方法与规则见 [`CRACKING_METHODOLOGY.md`](docs/field_verification/CRACKING_METHODOLOGY.md) 和 [`scripts/README.md`](scripts/README.md)。
- **AxData 日常验证与冗余退出**：以最近已完成交易日为数据日，在收盘后、盘前或非交易日运行时均可核验；盘中和集合竞价阶段不发起主动探测。允许完整采集，或 `--only` 明确选中 AxData 与 Tencent 两个必要源；项目 Tencent 对照失败时跳过请求。流程复用当次已成功采集的源数据，每个有效数据日最多增加一次已核准的 Tencent `tencent_realtime_snapshot` 请求，轮换一只项目已成功采集的股票；它不是对 AxData 257 个接口的每日轮询，其余路由仍在静态交叉表中按价值和风险待审。主动报价仅在双方报价日期及 `quote_time` 完全匹配时比较。被动短线对照按 AxData 与 ELTDX 记录的共同有效交易日配对，并选择不晚于最近已完成交易日的最新共同日期；KPH/KPL 只有两端实际 `trade_date` 相同且有效时才配对。部分采集只有在相应源对均被本次选中且采集成功时才累积路由证据。至少 3 个不同交易数据日、3 只不同股票、每份样本至少 5 个非空信息字段匹配且没有数值失配后，才将接口标记为运行上（部分）冗余并停止每日探测。语义冲突或尚未覆盖的字段继续列为未决项，不升级字典；每 20 个后续有效数据日启动一次复验，需积累 3 个新的有效样本。接口映射指纹、返回字段结构变化或复验发现差异会恢复日常探测。碰撞报告保留退出状态、证据日期、未决字段和复验倒计时，不将 AxData 视为独立字段锚。身份状态保存在本机 `.tmp/axdata_daily_validation_state.json`；该文件不可读时停止探测并要求人工检查，状态文件缺失或经审核删除时按未确认状态恢复限量采样。403/429/封禁会暂停对应源族，确认恢复后删除此状态文件才恢复。逐日证据写入 `docs/field_verification/<数据日>/axdata_validation.json`，不自动修改主字典。同一有效数据日重跑不会重复已发起的请求；之前因必要源缺失而零请求跳过时，必要源恢复后可重新评估。
- **AxData 实际采集路由退出**：每日实际调用的 TDX 短线 `stock_shortline_indicators_tdx` 与 KPH 涨停历史 `kph_limit_up_history` 分别和 ELTDX、KPL 对照。每条路由需至少 3 个不同的有效交易数据日、每日至少 18 只匹配股票；短线需至少 5 个字段全值相等，KPH 六个已知字段映射须全值相等且不能带未识别数值字段，才会停止该路由的日常请求。有效样本按双方记录的共同交易日核对，不要求来源日等于采集目录日；两端日期不同或数据不足时不计样本。确认后，默认碰撞也排除对应 AxData 路由；定期复验期间仍排除，发现失配或返回结构变化后立即重新采集并恢复碰撞。每 20 个后续有效数据日启动复验，须重新通过 3 个新数据日。未知字段继续让路由保持活跃。短线接口遇到 HTTP 403、429 或封禁信号会停止本轮剩余股票请求并持久标记人工复核；`--only` 采集同样记录封禁状态。人工复核封禁优先于契约变化，成功快照也不能自动解封；确认源已恢复后删除 `.tmp/axdata_daily_validation_state.json`，清除状态并从限量采样重新开始。AxData 身份状态与 Tencent 探针共用该文件。
- **Levistock 每日来源核验**：完整采集或 `--only market_sources` 会复用已采集的 CLS 情绪与 KPH 天梯，并从 7 个已筛选的数值接口中逐交易日轮换至多一个候选请求；仅在运行版本符合 `requirements.txt` 的 `0.1.8` 固定约束、目标为最近已完成交易日且数据阶段为 `closed` 时探测。周末和节假日默认以最近交易日作为数据日，盘前运行也可以核验该数据日；候选日期可比性仍依据请求日期或响应日期证据判定。调用前走 CLS/KPH 源族限流，403/429/封禁后停止该族并等待人工复核。候选 raw 独立存放，不直接作为碰撞锚；每日核验器本身只读 raw，新增请求数为 0。当前 7 项轮验不代表 Levistock 全部公开 API 均已验证。Eastmoney push2 未确认恢复前排除。完整快照同日重跑会复用 raw、补齐缺失的核验摘要，已保存的候选样本不会重请求；此前因对照源缺失而零请求跳过时，主源通过 `--overwrite` 恢复后可同日重新评估，实际候选请求一旦启动仍会被日级状态去重。详见 [`Levistock 来源核对`](docs/levistock_source_reconciliation_20261010.md)。
- **上游兼容性复核**：登记仓库、依赖版本差异、实际调用边界与采用结论见 [`UPSTREAM_COMPATIBILITY.md`](docs/UPSTREAM_COMPATIBILITY.md)；仓库对应关系见 [`source_repository_map.md`](docs/source_repository_map.md)。
- **百度源状态**：百度 K 线 MA 的 3 个登记字段目前为 `pending_validation`；默认不发请求，可显式使用 `--only baidu` 做限量验证。先前失效的 `getrelatedblock` 是概念接口，不能据此断定 K 线接口失效。AxData 当前接口表没有百度接口；FTShare 历史服务曾暴露的 `baidu_financial_calendar` 是财经日历方法，不是股票行情源。
- **统一数据合约**：唯一入口 `get_canonical_stock_data` 返回 `CanonicalStockData` 强类型合约（115 个 dataclass 属性，含 12 个可选 ELTDX 扩展；每只股票通过 `field_sources` 记录来源，并保留行情有效日期和采集时间元数据）。
- **按工作负载批量取源**：SHT/MED/LNG 先用 push2delay 批量行情，再用腾讯 60 只/批接口补齐估值、财务比率、盘口和涨跌停字段；VAL 保留全市场腾讯批量，MAK 保留 ZHB 快照、腾讯行情覆盖和东财资金字段批次。每字段记录实际来源，缺项仍保留单股 fallback。长线正文不消费 ELTDX 短线天梯，因此不再为长线请求该数据。
- **按时段与新鲜度选择行情**：盘前和休市日可复用满足逐字段新鲜度要求的 ZHB 快照；交易日 09:30 起，实时行情按当前路由获取当日数据。路由和来源标注见 [`架构说明`](docs/architecture.md)。
- **申万二级行业统一**：东财 datacenter 一次性分页拉取 + 90 天缓存，零逐股请求、零 push2 风控面。
- **东财分域限流与风控**：共享令牌桶 + 全局 1.0s 节流 + 强制直连；瞬时连接/超时及 408/5xx 有界退避，403/429 立即停止重试；连续 3 次断连触发跨进程 20h 冷却，字段采集在 403、429、已封禁或连续断连时暂停该源后续股票请求。
- **统一缓存层**：SQLite + L1 内存 + TTL + `cross_verify` + single-flight + 版本化防污染（口径变更升 category）。
- **TDX 服务器选择**：主源使用已验证主机列表并避免冷启动全量探测，故障时交由兼容适配器降级。ELTDX 北交所 `92xxxx` 使用 `bj` 市场码；采集与报告适配器按目标代码范围请求，避免误扫全市场。字段采集不再逐股请求未用于破解的 F10 新闻。
- **通用框架与工程化**：`BaseReportRunner` 共享骨架、并发下沉线程池、云端同步（GD 上传）、批量并行、mypy 类型安全。
- **测试体系（防退化守护）**：测试按 data/core/infra/reports 分层；当前模块数与用例数见 `tests/README.md`。
- **工程质量与验证记录**：本轮审计结论见 [`docs/PROJECT_AUDIT_20261015.md`](docs/PROJECT_AUDIT_20261015.md)；持续验证结果见 [`tests/README.md`](tests/README.md) 与 [`CHANGELOG.md`](CHANGELOG.md)。

---

## 碰撞分析与每日验证

采集脚本每日保存 AxData 的有限主动探针与短线/KPH 路由身份比较；已确认冗余的生产路由停止常规请求，仅在到期复核时恢复采集。FTShare 旧私有 MCP 的历史 raw 默认排除；公开 REST 的 `raw_ftshare_rest.json` 则进入默认碰撞，官方定义字段作为语义锚，强匹配单列 `L1-C`。采集完成后单独运行 `scripts/collide.py`，碰撞报告读取窗口内本地结果并按有效数据日去重。报告还展示 AxData 257 接口静态队列、字母字段拆词线索和候选覆盖区；候选完整明细、方法候选、双输入公式线索、预测分歧复核点及候选校准计数保存在碰撞 JSON。分析时必须遍历全量 JSON 明细并记录各候选处置；Markdown 仅作导航，完整性未通过或覆盖数未对账时不得宣告无成果或进入定案。探索候选不能替代独立来源 `L1/L1-U` 门槛或主字典裁决；`L1-C` 使用有官方定义的契约字段作语义锚，仍需独立复核底层来源和字段关系，不自动定案。**字段达到确认标准后只从待破解目标中移出，仍持续采集并保留为碰撞锚，用于监测来源漂移；字段状态不决定采集器是否运行。**确认冗余的接口源治理独立于字段破解定案。字母拆词按主字典逐源完整路径关联，只生成待审候选，不自动更新主字典。L1 精确匹配须满足每日 18 组有效配对、3 个独立日期及至少 5 组信息配对；双方同时为零或同时缺失不计入命中率。报告 JSON 保留候选和逐日诊断。

## 快速开始

### 环境要求

- Python **3.11+**；推荐 **3.12**（AxData 0.1.4 要求 Python ≥3.11；测试启动器默认选择并校验 Python 3.12）
- 已验证环境：Windows + Python 3.12（PowerShell）；代码最低支持 Python 3.11。其他系统尚未按本仓库的标准启动器完整验证。
- 项目自身的锁文件和报告临时输出写入仓库根 `.tmp/`。Windows 下仍推荐使用 `scripts/run_with_system_python.ps1`（或兼容入口 `.bat`），使 Python 及其子进程的 `TEMP`/`TMP`/`TMPDIR` 均指向该目录；直接执行项目入口时，项目内部临时路径也会落入 `.tmp/`。可通过 `ASTOCK_TEMP_DIR` 显式指定项目临时目录。

### 新机器部署（复制项目后）

项目内数据目录按仓库位置解析；首次运行会按需创建 `cache/`、`logs/`、`reports/`、`snapshots/` 并同步 ZHB 数据。部分功能还会读取本机配置或外部行情文件，部署前请按对应功能说明配置。

1. 安装 Python 3.12（最低支持 Python 3.11；Windows Store 版已验证可用）
2. `pip install -r requirements.txt`（包含经离线兼容回归的 `eltdx==3.2.2`、`levistock==0.1.8`、`axdata==0.1.4`；如自行省略，相关功能会降级）
   > ⚠️ **`thsdk` 已于 V17.0.29(2026-09-07) 随 `stock_common/sc_ths.py` 一同移除**，不再是可选依赖。
3. `pip install -r requirements-dev.txt`（开发环境；自动包含运行时依赖及 pytest/mypy/black）
4. Windows 首次运行 `.\scripts\run_with_system_python.ps1 main.py --sht 600519 --no-upload` 冒烟（首只约 5 分钟，含 ZHB 下载+缓存预热）

可选配置（缺失不影响核心报告）：
- **Google Drive 上传**：配置 Google OAuth 凭据；缺失时本地报告仍可生成，但无法上传。
- **东方财富 Cookie**：需要时可通过 `EAST_MONEY_COOKIE` 或 `credentials/eastmoney_cookie.txt` 配置。

项目入口会将 Python 标准输出设为 UTF-8，启动器会把临时目录指向仓库 `.tmp/`。无需修改系统级环境变量、PowerShell Profile 或全局执行策略；测试和 Python 命令按下方入口运行。

### 安装依赖

```powershell
.\scripts\run_with_system_python.ps1 -m pip install -r requirements.txt
.\scripts\run_with_system_python.ps1 -m pip install -r requirements-dev.txt   # 开发环境
```

`requirements-dev.txt` 通过 `-r requirements.txt` 继承同一组运行时固定版本。AxData 的 `axdata_core` 模块由 `axdata` 包提供；短线指标使用仓库根目录 `cache/zhb/` 中最新的 `zhb_*.zip` 作为统计资源，同时仍会请求 TDX 行情/财务输入。适配器和 ZIP 路径的回归边界见 [`UPSTREAM_COMPATIBILITY.md`](docs/UPSTREAM_COMPATIBILITY.md)。

### 基本用法

```powershell
# 生成短线报告
.\scripts\run_with_system_python.ps1 main.py --sht 600519 000858

# 生成中线报告
.\scripts\run_with_system_python.ps1 main.py --med 600519 000858

# 生成多种报告
.\scripts\run_with_system_python.ps1 main.py --sht 600519 --med 600519 --lng 600519

# 批量处理
.\scripts\run_with_system_python.ps1 main.py --sht 600519 000858 03606 --med 600519 000858
```

项目当前的标准启动和测试流程以 Windows PowerShell 为准；跨平台支持尚未作为验证承诺。

---

## 报告类型说明

| 参数 | 报告类型 | 说明 |
|------|----------|------|
| `--sht` | 短线交易执行 | 涨跌停边界、当日资金流、昨日涨停晋级率、龙虎榜席位、封单强度、盘口异动检测 |
| `--med` | 中线业绩兑现 | 报告期绑定财务、研报评级变化、两融 3/5/10 日维度、技术面 MACD/RSI/BOLL/KDJ |
| `--lng` | 长线企业质量 | 多期财务纵深、分红连续性、风险扫描（解禁/减持/质押）、现金流验证 |
| `--val` | 全市场候选发现 | 多策略分层扫描（ZHB 初筛 → 扩展字段候选 → 深度确认），PE 估值回归含跨年 Q1 修复 |
| `--mak` | 市场状态引擎 | 市场宽度、四池、行业轮动（申万二级）、财联社市场情绪/涨停天梯/盘口异动 |
| `--ful` | ~~完整报告~~ | **V16.1 已下线**：能力并入 sht/med/lng（技术/风险引擎迁移至 sc_technical/sc_risk） |

> V16.1：`--ful` 参数保留但不再生成报告（报友好提示）。技术指标引擎（MACD/RSI/BOLL/KDJ）与风险扫描引擎已迁移至 `stock_common/sc_technical.py` / `sc_risk.py` 供 sht/med/lng 复用。

---

## 命令行参数

```
python main.py [选项] 股票代码...

选项:
  --sht    生成短线交易执行报告
  --med    生成中线业绩兑现报告
  --lng    生成长线企业质量报告
  --val    生成全市场选股报告
  --mak    生成市场状态报告
  --ful    V16.1 已下线（提示改用 --sht/--med/--lng）
  --all    生成所有报告类型
  --no-upload  禁用Google Drive上传
  --help   显示帮助信息

股票代码格式:
  支持6位数字代码，如: 600519
  支持带后缀格式，如: 600519茅台
  支持空格分隔，如: 600519 000858 03606
```

---

## 项目结构

```
a-stock-data/
├── main.py                       # 主入口程序（参数分发/子进程调度/超时分级）
├── .tmp/                         # 本机运行时临时目录（Git 忽略，按需创建）
├── VERSION                       # 项目版本号（见文件，单一来源）
│
├── core/                         # 核心模块包（9 个支撑模块，见 core/README.md）
│   ├── config.py                 # 全局配置集中管理（超时/限流/熔断）
│   ├── data_provider.py          # 统一数据层（canonical 合约 + 字段路由 + 多级 fallback）
│   ├── _accessors.py             # 跨边界访问器叶子模块（get_concept_from_zhb 等 7 个访问器，消除 data_provider↔stock_common 导入期循环依赖）
│   ├── _tdx_handshake_patch.py   # eltdx 握手兼容补丁
│   ├── zhb_client.py             # 通达信 zhb.zip 全局配置总包下载与解析（45 文件）
│   ├── zhb_sync.py               # ZHB 自动化入库管道（python -m core.zhb_sync）
│   ├── tdx_client.py             # eltdx/easy_tdx 统一层（运行时主源 eltdx；mootdx 已于 V17.3.4 退役）
│   ├── stock_cache.py            # 统一缓存层（SQLite + L1 内存 + TTL + cross_verify）
│   └── gd_uploader.py            # Google Drive 上传（凭据在 credentials/）
│
├── stock_common/                 # 核心公共包（传输/数据源/评分/报告基类，见 stock_common/README.md）
│   ├── __init__.py               # 包入口，统一导出显式公共接口
│   ├── sc_datasource/            # 数据源查询包（按数据源与业务职责拆分，见子包 README）
│   ├── sc_network.py             # 网络请求层（分域限流/令牌桶/封禁冷却/进程文件锁）
│   ├── sc_report_runner.py       # BaseReportRunner 基类
│   └── ...                       # 详见 stock_common/README.md
│
├── get_sht_report.py             # 短线报告生成（90 日窗口）——入口脚本
├── get_med_report.py             # 中线报告生成（180 日窗口）
├── get_lng_report.py             # 长线报告生成（730 日窗口）
├── get_val_report.py             # 估值报告生成（策略选股）
├── get_mak_report.py             # 市场热点报告生成（异动扫描）
│
├── credentials/                  # V17.0 凭据集中目录（.gitignore 排除，不入库）
│   ├── client_secrets.json       # GD OAuth 客户端凭据
│   ├── credentials.json          # GD OAuth token（自动刷新）
│   └── eastmoney_cookie.txt      # 可选东方财富 Cookie
│
├── scripts/                      # 辅助脚本（见 scripts/README.md）
│   ├── capture_field_probe.py    # 字段实测采集；KPL/KPH 涨停明细独立归档并按实测日对齐
│   ├── collide.py                # 日期归一化、快照择优、跨源独立性闸门与多方法候选；每日采集后运行
│   ├── collision_research_state.py  # 探索候选观察台账；按字段对保存证据历史
│   ├── context_policy.py         # 采集与碰撞共享的可选上下文路径策略
│   ├── run_tests.ps1             # 测试统一入口（AGENTS.md 强制 shell 层中转）
│   ├── run_with_system_python.ps1 # Python 3.12 选择与命令转发
│   ├── update_calendar.py        # 交易日历数据更新（含 V14+ 防覆盖保护）
│   ├── clean_cache.py            # 缓存清理快捷脚本（封装 python -m core.stock_cache）
│   ├── backtest_topn.py          # top_n 回测验证
│   ├── perf_compare.py           # dataclass vs dict 性能压测
│   ├── gen_field_matrix.py       # 字段×源矩阵自动生成
│   ├── fmt_preview.py            # 零网络格式预览工具（V17.0.3）
│   ├── check_em_health.py        # 东财接口健康探测（6 域低频）
│   ├── upload_reports_to_gd.py   # GD 补传（扫描未上传 md）
│   └── backup-opencode.ps1       # opencode 配置备份
│
├── docs/                         # 技术文档（见 docs/README.md）
│   ├── PROJECT_CONTEXT.md        # 架构导航、稳定约束与动态项目快照
│   ├── ARCHITECTURE_THEORY.md    # 统一数据访问架构公理
│   ├── DEBT_LEDGER.md            # 已知架构偏离与偿还状态
│   ├── PROJECT_AUDIT_REMEDIATION_20260928.md # 本轮整改计划与验收记录
│   ├── UPSTREAM_COMPATIBILITY.md # 上游仓库、依赖和适配边界复核
│   ├── architecture.md           # 项目架构与数据流图（Mermaid）
│   ├── roadmap.md                # 版本路线图 + ADR 决策记录
│   ├── field_dict.md             # 生成的字段治理入口与链接
│   ├── field_verification/field_registry.json # 逐源完整路径字段状态（机器权威）
│   ├── field_verification/collision_research_state.json.gz # 探索候选历史（不代表字段定案）
│   ├── unknown_fields.md         # 未知、候选、冲突与已证伪字段队列
│   ├── field_matrix.md           # 字段×源矩阵
│   ├── source_repository_map.md  # 数据源与 GitHub 仓库对应关系
│   ├── field_source_reference.md # 重整前完整字典原文归档
│   ├── verify/                   # 字典附录（实测值/样本/破解数据——实证层）
│   ├── script_data_dict.md       # 脚本应用接口与字段来源字典
│   └── domain_glossary.md        # 领域词汇表（术语口径统一）
│
├── tests/                        # pytest 测试（模块和用例数见 tests/README.md）
├── pyproject.toml                # pytest / mypy / black 等工具配置中心
├── requirements.txt              # 运行时依赖列表
├── requirements-dev.txt          # 开发依赖列表（测试/类型/格式）
├── CHANGELOG.md                  # 版本变更记录
├── AGENTS.md                     # Agent 行为规约（Shell 规则/验证循环/审查流程）
├── CONTRIBUTING.md               # 贡献指南
├── CODE_OF_CONDUCT.md            # 社区行为准则
├── LICENSE                       # MIT 许可证
├── README.md                     # 本文件
│
├── reports/                      # 报告输出目录（运行时，.gitignore）
├── snapshots/                    # 评分快照（历史对比/背离检测，.gitignore）
├── cache/                        # 缓存数据库 + ZHB 数据包 + 行业映射（.gitignore）
└── scratch/                      # 一次性调研沙盒（.gitignore，见 scratch/README.md）
```

> **目录职责总表**

| 目录 | 目的 | 关键文件 |
|:---|:---|:---|
| `core/` | 核心支撑模块(数据层/传输/缓存/日历同步/上传) | data_provider / tdx_client / stock_cache |
| `stock_common/` | 公共业务模块(网络层/数据源/评分/报告基类) | sc_network / sc_datasource / sc_report_runner |
| `credentials/` | 可选本地凭据(不入库) | Google OAuth / Eastmoney Cookie |
| `scripts/` | 可复用运维命令 | run_tests.ps1 / update_calendar / clean_cache |
| `docs/` | 技术文档(架构/决策/字段治理) | roadmap / field_dict / registry / unknown_fields |
| `tests/` | pytest 测试(防退化守护) | data/ core/ reports/ infra/ |
| `reports/` | 报告输出(运行时) | 运行时生成（.gitignore，无专职 README） |
| `snapshots/` | 评分快照(运行时) | 运行时生成（.gitignore，无专职 README） |
| `cache/` | 缓存数据(运行时) | stock_cache.db / zhb/ / 行业映射 |
| `scratch/` | 一次性调研沙盒(用完即弃) | 见 scratch/README.md |
```

---

## 配置文件

### requirements.txt / config.py

运行时依赖见 [`requirements.txt`](requirements.txt)（16 项；`levistock`/`axdata` 可选，缺失自动降级），开发依赖见 [`requirements-dev.txt`](requirements-dev.txt)（pytest/mypy/black）。核心参数集中在 `core/config.py`：网络超时、限流（`EM_MIN_INTERVAL=1.0`）、重试、缓存（DB≤500MB）、熔断（阈值 10）；分域限流表在 `stock_common/sc_network.py::_DOMAIN_LIMITS`（push2 系最严 0.4rps）。完整定义以源文件为准。

### Google Drive 配置（可选）

如需启用云端上传功能：

1. 在 Google Cloud Console 创建项目并启用 Drive API
2. 下载 OAuth 2.0 凭证文件，保存为 `credentials/client_secrets.json`（V17.0 凭据集中目录）
3. 首次运行时会弹出浏览器进行授权，授权后自动生成 `credentials/credentials.json`

> **注意**：
> - OAuth scope 为 `drive.file`，脚本只能看到由该脚本自身创建或打开过的文件/文件夹
> - 若 Google Drive 根目录无故出现个股文件夹，通常是桌面客户端同步冲突导致（详见 FAQ），脚本本身不会移动或删除已有文件夹

---

## 核心模块说明

文档完整架构（模块职责 / 数据流 / 并发限流 / 缓存分层 / 字段路由）见 [`docs/architecture.md`](docs/architecture.md)（含 Mermaid 图）。要点速览：

- **`core/data_provider.py`**：个股数据统一入口，封装 `CanonicalStockData` 强类型合约（115 个 dataclass 属性，含 12 个可选 ELTDX 扩展；非扩展属性为 103 个；`sc_schema.FIELD_SPECS` 是 38 项精选源字段元数据，不是完整契约字段清单）。报告批量路由为 push2delay 基础行情 + 腾讯补充字段；批量缺价时单股 fallback 为 TDX → 腾讯 → push2delay → push2，并按时段使用 ZHB 快照。每只股票通过 `field_sources` 留存来源，并透传行情有效日期与采集时间；跨边界访问器已拆至 `core/_accessors.py`，消除与 `stock_common` 的导入期循环依赖。
- **`stock_common/sc_network.py`**：分域限流（37 域）、进程文件锁、408/5xx 与瞬时传输故障有界退避、403/429 立即停止、连续封禁 20h 冷却。
  > 注：`core/tdx_client.py::_DOMAIN_LIMITS` 另有 6 域**独立**限流表（TCP 长连接语义，与 HTTP 请求级节流不同，**有意不合并**）。
- **`stock_common/sc_datasource/`**：按数据源和业务职责组织的查询适配器，模块清单见 [`stock_common/sc_datasource/README.md`](stock_common/sc_datasource/README.md)。
- **`stock_common/sc_schema.py`**：字段元数据层（`FieldSpec` / `TimeAnchor` / `DataSource` / `Unit`），`normalize_at_boundary` 单位归一。
- **`core/stock_cache.py`**：SQLite + L1 内存 + TTL + `cross_verify` + single-flight + 版本化防污染。
- **`stock_common/sc_fault_tolerance.py`**：`TokenBucket` / `CircuitBreaker` / `RandomUAPool`。
- **`stock_common/sc_technical.py` / `sc_risk.py`**：技术指标（MACD/RSI/BOLL/KDJ）与风险扫描引擎。
- **`stock_common/stock_calendar.py`**：本地交易日历（621 条 2004-2026+）权威判定。
- **`get_*_report.py`**：5 大报告 Runner，继承 `BaseReportRunner`，共享 CLI/Banner/上传/清理模板，差异仅在章节渲染。

## 输出示例

报告文件命名格式：`{股票代码}_{报告类型}_{日期}_{时间}.md`（V17.0.1 起全量 md 化）

```
reports/
├── 600519_sht_20260618_1430.md    # 茅台短线报告
├── 600519_med_20260618_1435.md    # 茅台中线报告
├── 600519_lng_20260618_1440.md    # 茅台长线报告
└── get_val_report_20260618_1445.md # 估值汇总报告
```

---

## 版本历史

完整版本历史（含全部字段破解实锤与回归基线演进）见 [CHANGELOG.md](CHANGELOG.md)。本文档不再重复版本明细。

---
## 开发与验证

开发环境和临时目录约定见上方「快速开始」及 [`scripts/README.md`](scripts/README.md)。仓库级约束见 [`AGENTS.md`](AGENTS.md)。

### 离线测试

```powershell
.\scripts\run_tests.ps1 -Mode skip_real
.\scripts\run_tests.ps1 -Mode module -Path tests\core\test_core_routing.py
```

默认不触发真实网络；需要真实网络的测试必须标记 `real_network`，并显式使用 `-Mode real`。当前测试模块清单和最近完整结果见 [`tests/README.md`](tests/README.md)。

### 静态检查与架构闸门

```powershell
.\scripts\run_with_system_python.ps1 -m black --check core\_accessors.py
.\scripts\run_with_system_python.ps1 -m mypy core\_accessors.py
.\scripts\run_with_system_python.ps1 scripts\verify_data_access.py
.\scripts\run_with_system_python.ps1 scripts\verify_sync_check.py
```

按实际改动范围运行格式和类型检查；数据访问或字段同步相关修改还需通过 A1/A7 闸门。完整验收要求见 [`AGENTS.md`](AGENTS.md) §9。

### 文档与版本

改动行为后同步更新 [`CHANGELOG.md`](CHANGELOG.md)；版本号以根目录 [`VERSION`](VERSION) 为准。架构和数据口径分别见 [`docs/architecture.md`](docs/architecture.md) 与 [`docs/domain_glossary.md`](docs/domain_glossary.md)。

---

## 许可证

MIT License

---

## 免责声明

本项目仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。使用本工具产生的任何投资损失，作者不承担责任。

---

## 联系方式

如有问题或建议，欢迎提交 [Issue](https://github.com/tsy1102/a-stock-data/issues)。
