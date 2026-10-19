# 统一层整改计划

> 状态：已完成（2026-10-19）
> 范围：Tier 1 `CanonicalStockData`、ZHB 新鲜度、字段级来源与日期、报告批量预热入口，以及对应验证和说明。
> 目标：修正统一层的日期与来源误报，确保 ZHB 字段按交易日和 ABCD 分类择用；减少跨层私有状态写入；让已核实的契约有自动化回归。

## 1. 已核实的调用与数据契约

| 项目 | 现状 | 整改约束 |
|---|---|---|
| Tier 1 调用方 | SHT、MED、LNG、VAL；`stock_common/enrich_helpers.py` 读取 `field_sources` | 保持 `get_canonical_stock_data()` 签名和 `field_sources: dict[str, str]` 类型 |
| 日期消费者 | SHT、MED 使用 `time_anchor == "t-1"` 显示上一交易日提示 | `time_anchor` 基于可核验的价格数据日期；无日期时显式为 `unknown` 并提示，不冒充 T 日 |
| Canonical 序列化 | `CanonicalStockData` 有 115 个 dataclass 属性；`to_dict()` 使用 `asdict()` | 新增日期元数据属于公开的增量字段，更新属性清单、`to_dict()` 和报告契约测试 |
| 采集日期 | EastMoney quote adapter 的 `data_date` 由本机 `datetime.now()` 生成 | 将其视为采集时间兼容字段，不再当作上游 `as_of_date` |
| ZHB 日期 | `ZhbData.date` 是缓存包数据日；现有年龄按股票交易日计算 | 所有直接 ZHB 字段通过同一包日期和 ABCD 阈值过滤；未来日期判为不新鲜 |
| 报告期事件锁 | Canonical `report_period` 可来自 ZHB `report_date` | `report_date` 是报告期标识，不参与快照日期过滤，保证事件锁输入不变 |
| 批量缓存 | 内存缓存按运行日隔离；L2 键为 `quote_batch_v2:prefetch_quote_batch:<code>` | 预热改用公开函数；保留缓存分类、键、TTL、来源元数据和避免重复请求的行为 |
| TDX quote 适配器 | `tdx_get_quote_full()` 将 ZHB、TDX TCP、腾讯 HTTP 合并；多个现有消费者依赖其原返回结构 | 旧接口结构不变；新增兼容的逐字段来源接口供 Tier 1 使用 |
| 主字典 / 注册表 | 主字典的 `(source, 完整 code path)` 是字段身份；当前任务未取得足以重写注册表的逐字段新证据 | 不改主字典或 `field_registry.json`；只增加统一层契约检查，不伪造来源映射 |

## 2. 整改原则

1. 行情日期一律按项目交易日历解释；周末、节假日与调休按有效交易日计算。
2. `collected_at` 表示本机采集时刻；`field_as_of_dates` 只记录上游或本地 ZHB 包能证明的字段有效日期。缺日期即未知，不用采集日期推断上游数据日期。
3. ZHB 字段按自身字段名应用 A/B/C/D 延迟阈值；不以“ZHB 字典非空”代表其中所有字段都新鲜。
4. 来源标记跟随实际填入该字段的来源；计算值单独标为计算来源，不能继承旁边字段的来源。
5. 先加离线回归，再改运行路径；不发真实网络请求，不改变采集限流。
6. 现有公开 API 尽量只作增量扩展；不改变 L2 缓存键，不改变财报 `report_period` 事件锁。

## 3. 分阶段计划

### 阶段 A：锁定回归基线

- 增加交易日边界与未来 ZHB 日期测试。
- 增加 ABCD 各类字段在不同快照年龄下的保留/拒绝测试，并覆盖 `turnover_pct` 的 A 类口径。
- 增加 Canonical 的陈旧字段排除、`report_date` 保留、未知日期标记、字段日期溯源和错误来源标签测试。
- 增加 TDX 混合适配器逐字段来源和旧接口返回兼容测试。
- 增加公开批量预热 API 的缓存命中、哨兵范围、L2 持久化和零重复请求测试。

### 阶段 B：统一 ZHB 有效性判定

- 让 `zhb_field_safe()` 支持已读取快照的明确 `data_date` 和统一 `as_of`，并保留现有无参调用语义。
- 集中 A/B/C/D 最大交易日延迟定义；修正遗漏的 `turnover_pct` 实时分类。
- 对未来日期、非法日期、无日期均安全拒绝；不得把负交易日年龄判为新鲜。
- Canonical 读取 ZHB 包日期后先过滤字段；保留 `report_date`。
- 当原始 ZHB 包含但已过期的 A 类行情字段时，触发对应行情 fallback，避免“快照字典仍有其他字段”挡住回退。
- TDX quote 适配器的 ZHB 分支改用相同字段级新鲜度；不再以统一的 1 日阈值给所有字段放行。
- TDX 行情缓存日期改由 `latest_market_data_date()` 计算；休市日和盘前沿用最近有效交易日，不以周末/假期自然日创建空日期缓存桶。

### 阶段 C：统一字段来源与日期元数据

- 新增小型 `core/canonical_metadata.py`，仅负责日期规范化、ZHB 字段过滤、来源有效日期映射和 `time_anchor` 判定；Canonical 主流程继续作为编排入口。
- `CanonicalStockData` 增加 `collected_at` 与 `field_as_of_dates`；`quote_date` 仅表示价格字段已核实的有效日期。
- `time_anchor` 通过价格的有效日期与本地交易日比较得到 `t_day`、`t-1` 或 `unknown`；SHT/MED 对 `unknown` 明示日期未核实。
- 给 TDX 混合 quote 增加带字段来源的新增接口；保留 `tdx_get_quote_full()` 原有 dict 返回结构。来源日期只从明确的 `as_of_date` 或 ZHB 包日期取值。
- 修正字段溯源：OHLC/昨收/成交量采用提取函数的实际返回来源；TDX 资金流不标为东财；`industry_code` 不继承 `industry` 来源；保留批量缓存中的完整来源标签，修复 `realtime:tencent:batch` 被截断成 `realtime:batch` 的情况。
- 修正 `sc_schema.py` 中 `push2` 上游描述和来源标签说明。

### 阶段 D：收口批量行情预热

- 在 `core.data_provider` 增加公开的 `prewarm_canonical_quote_cache()`，封装 Canonical 批量行情缓存、来源标签、VAL 专用“跳过本报告不消费的实时补充”哨兵和 L2 写入。
- 将 `get_val_report.py` 对 `_BATCH_QUOTE_CACHE`、`_PD_EXTRA_CACHE`、`_PD_EXTRA_CACHE_DATE` 的直接读写改为调用该 API。
- 让日期轮换逻辑由统一层内部函数处理，外部报告不再负责修改缓存状态。
- 保持哨兵只存在于当前进程内存；不把“跳过资金流请求”的哨兵写入 L2。

### 阶段 E：契约闸门、结构边界与文档

- 新增离线 `scripts/verify_canonical_contract.py`：检查 Canonical 属性清单、精选 `FIELD_SPECS` 名称唯一、日期来源只接受明确日期、Canonical 组装接线、TDX 交易日历使用、报告脚本不直接改私有缓存且能提示未知日期。
- 提取日期、新鲜度和字段来源处理到独立模块，减少 `data_provider.py` 中横切逻辑；不对整段 1,300 行编排函数做无测试保护的大规模搬迁。
- 更新架构说明、`CHANGELOG.md`、`VERSION` 和相关模块注释；版本从 `17.4.63` 升至补丁版 `17.4.64`。
- 保持 `field_registry.json` 与主字典不变；若新发现需要字段身份或语义裁决，另开有实证支持的字典变更。

## 4. 文件范围

- 新增：`docs/unified_layer_remediation_plan.md`、`core/canonical_metadata.py`、`scripts/verify_canonical_contract.py` 与相应测试。
- 修改：`AGENTS.md`、`core/data_provider.py`、`core/tdx_client.py`、`core/zhb_client.py`、`stock_common/sc_datasource/_zhb.py`、`stock_common/sc_datasource/_shared.py`、`stock_common/sc_schema.py`、`get_val_report.py`、`get_sht_report.py`、`get_med_report.py`、`tests/core/`、`tests/data/`、`tests/reports/`、`docs/architecture.md`、`docs/ARCHITECTURE_THEORY.md`、`CHANGELOG.md`、`VERSION`。
- 不修改：主字典、`field_registry.json`、日常采集限流、L2 缓存键和 TTL、其他业务报告字段定义。

## 5. 验收标准

- 陈旧 A/B/C/D 字段按交易日阈值分别处理；未来或非法 ZHB 日期不会被放行。
- SHT/MED 不再把没有有效日期的行情报告为已确认 T 日；来源日期与采集时间分开。
- 每个被纠正的字段来源标记对应实际填值路径；`field_sources` 继续是字符串字典。
- TDX 旧 API、Canonical 原 API、批量预热 L2 键与缓存 TTL 均保持兼容。
- 报告期事件锁输入不变；主字典和字段注册表无本轮改动。
- 新增契约闸门及原有离线套件通过；不运行真实网络测试。
- `git diff` 只包含本整改范围，工作区原有改动得到完整保留。

## 6. 实施状态

- [x] 现状调用、序列化、来源日期、缓存键和测试影响的事实核查。
- [x] 阶段 A：新增交易日、字段新鲜度、日期/来源元数据、TDX 兼容、公开预热与报告未知日期回归用例。
- [x] 阶段 B：ZHB 字段级交易日新鲜度、未来日期拒绝及休市日 TDX 缓存日期。
- [x] 阶段 C：字段级来源与日期元数据。
- [x] 阶段 D：公开批量预热 API。
- [x] 阶段 E：契约闸门、文档与离线验证。
