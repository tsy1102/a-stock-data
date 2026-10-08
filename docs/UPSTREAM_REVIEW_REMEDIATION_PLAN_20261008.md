# 上游更新复核整改计划（2026-10-08）

## 状态

**已完成（2026-10-08）。** 本计划承接上游仓库复核结论；实施范围保持在竞价日期证据、上游兼容记录和相关文档/验证。

## 目标

1. 消除 Fuyao 竞价快照没有源端数据日期、却随混合源 `probe_trading_day` 进入历史碰撞的误归日风险。
2. 保持现有报告接口、采集字段路径和历史快照兼容；只隔离日期证据不足的竞价子树。
3. 将登记的上游仓库、实际调用边界、已核发布/依赖版本、采用结论及许可注意事项集中记录，避免把 SDK 版本、底层数据源和协议参考混为一谈。
4. 不因上游新增能力而增加每轮采集请求、并发或限流压力；因新信封缓存键无法复用旧 list-only 缓存，相同参数的首次调用允许一次缓存冷读。本轮不发真实网络请求，不升级运行环境依赖。

## 事实与根因

- 上游 Fuyao `auction/snapshot` 契约不提供查询日期；信封包含响应组装时间、竞价阶段和数据状态。响应时间不能作为行情数据日期。
- `stock_common.sc_fuyao._items()` 当前只返回 `data.item`，采集结果因而丢失信封状态与时间。
- `scripts/capture_field_probe.collect_fuyao()` 将 `probe_trading_day` 作为混合 Fuyao 文件的源级日期；`_source_as_of_date()` 会将该日期登记为整个 `fuyao` 源的 `as_of_date`。
- `scripts/collide.py._flatten()` 会把 `stocks.<code>.auction_final` 的数值字段与同文件其他 Fuyao 字段一起按源级日期展开。2026-09-29 原始样本可见该结构已存在，但不含上游信封元数据，不能由现有样本确认该日快照实际对应的日期。
- `get_sht_report.py` 也调用 `get_fuyao_auction_snapshot(..., stage="live")`。它依赖列表返回契约，不能因采集器的取证需求改变其返回类型或字段。
- 当前环境中的 `eltdx`、`axdata`、`levistock` 版本低于复核时上游最新版本；现行 requirements 使用宽版本范围。项目未调用本次上游新增的退市日线/板块行情入口；AxData 项目适配器使用本地 ZHB ZIP。无证据支持本轮盲目升级或锁定依赖。

## 分阶段实施

### 阶段一：先固化现状和调用契约

- [x] 确认工作区干净，读取项目上下文、现有采集/碰撞日期规则与上游登记关系。
- [x] 追踪 Fuyao 集合竞价函数的生产调用者、返回形态、缓存分类和相关测试位置。
- [x] 修改前补齐缓存装饰器行为及 `_flatten()` 唯一调用点的最后一次定向核对；缓存键含函数名且区分位置/关键字参数，因此旧列表包装器与新信封适配器统一用 `stage=` 关键字调用；新缓存键首次请求会回源，后续同参数调用复用缓存。旧 raw 没有新元数据时保持原处理。

### 阶段二：保留 Fuyao 快照信封，保持旧接口

- [x] 在 `stock_common/sc_fuyao.py` 增加返回完整 Fuyao 竞价快照信封的公开适配器；保留原 `get_fuyao_auction_snapshot()` 的 list 返回语义，并让二者共用同一个 `fuyao_auction` 缓存/单次请求路径。
- [x] 在 `stock_common/__init__.py` 明确重导出新适配器，保持 `__all__` 与实际导出一致。
- [x] `collect_fuyao()` 仍按原路径写入 `stocks.<code>.auction_final` 字段，并在该子树附加请求阶段、`data_status`、`auction_phase`、响应时间、明确源端数据日期和碰撞资格；顶层另留信封摘要供无数据行时诊断。
- [x] 当前契约没有提供数据日期时，显式标记 `collision_eligible=false` 与原因；未将 `timestamp` 或 `probe_trading_day` 用作该竞价子树的源端数据日期。
- [x] 保持源级 `probe_trading_day` 的既有行为，未改变同一 Fuyao 文件中其他数据的日期处理。

### 阶段三：只在碰撞中隔离不具备日期证据的子树

- [x] 更新 `scripts/collide.py._flatten()`：只对带显式 `collision_eligible=false` 元数据的子树停止展开；不改变其他 Fuyao 字段、其他源或历史 raw 文件的处理。
- [x] 对跳过的源路径输出可审计诊断；诊断及信封元数据不会成为候选字段，并显示在 Markdown/JSON 报告的诊断列表。
- [x] 旧采集文件没有该元数据时维持旧解析逻辑，未追溯性删除旧证据。
- [x] `scripts/collision_dates.py` 仅把元数据键排除在快照质量计数之外；交易日历、快照择优和源级 as-of 回退规则未改。

### 阶段四：上游兼容记录和文档闭环

- [x] 新增 `docs/UPSTREAM_COMPATIBILITY.md`，记录截至 2026-10-08 的已确认仓库、实际调用边界、当前/最新版本差异、近期变更是否适用、许可证注意事项与不直接采用的原因。
- [x] 明确 eltdx 新板块/退市入口是同一 TDX 来源族的后续候选；AxData/levistock 本轮不升级；腾讯 K 线单位/下标更正仅作为未来接入契约；Fuyao SDK 迁移不影响本项目 REST 调用。
- [x] 更新 `README.md`、`docs/PROJECT_CONTEXT.md` 文档索引及 `scripts/README.md`、`docs/field_verification/README.md` 的采集/碰撞日期说明；未手工编辑 lineage 生成的 `docs/source_repository_map.md`。
- [x] 更新 `CHANGELOG.md` 并将唯一版本源 `VERSION` 升一个最小补丁号（17.4.26 → 17.4.27）；`pyproject.toml` 使用动态版本，未重复写入版本号。

### 阶段五：测试与验收

- [x] 在现有 `tests/` 模块补离线 mock 回归：信封元数据、明确数据日期和状态判断、旧 list API、目标子树排除、其他 Fuyao 字段保留、历史无标记兼容、碰撞报告诊断、记录数不受元数据干扰。
- [x] 采集/碰撞/日期专项测试通过（77 passed）；仓库离线全量测试通过（696 passed、1 skipped、47 deselected）。
- [x] 改动 Python 文件通过编译、Black、mypy；A1/A7 闸门、敏感信息检查与 `git diff --check` 通过。
- [x] 未调用真实行情 API，未改变限流间隔，未升级或卸载本机依赖。
- [x] 回填本计划完成状态、实际验证数字；README/CHANGELOG/VERSION 与实现一致。A7 按项目约定刷新了 `docs/field_verification/20260911_verify_sync_report.md` 的最近检查日期。

## 不在本轮实施

- 不升级或固定 `eltdx`、`axdata`、`levistock`：已审查的新增 API 不是当前采集路径所必需，当前机器版本也不是上游最新版本；升级需单独做依赖安装与接口兼容验证。
- 不复制上游项目实现，也不把同一 TDX 来源族的多个包装器当作独立碰撞锚。
- 不将 2026-09-29 等旧采集目录改名或重写；历史快照元数据缺失时保留原始证据。
- 不在本轮引入 Fuyao 板块行情、退市股票日线或新的 Tencent K 线采集。
- 不改变五大报告脚本的计算和展示逻辑；本次兼容性通过共享适配器保持。

## 验收标准

1. 竞价快照保留原始字段与上游状态；当前契约无明确数据日期时，不进入交易日碰撞样本。
2. 其余 Fuyao 子数据和五大报告现有调用行为保持不变。
3. 碰撞报告说明被排除的 Fuyao 竞价字段路径及原因；历史无元数据 raw 文件不受影响。
4. 所有离线回归与仓库闸门结果明确记录；全流程真实数据源请求数为 0。

## 实施结果与度量

- Fuyao 竞价字段的日期判定从“跟随混合文件源级 `probe_trading_day`”改为“只接受源端显式日期 + 就绪状态 + 与目标交易日一致”；当前上游没有显式日期时，竞价字段进入碰撞的数量为 0，报告保留排除原因。
- 离线通过数：V17.4.26 记录的 688 → 本轮 696；新增 7 个定向回归用例。当前另有 1 skipped、47 deselected，最终全量耗时 124.18 秒。
- A1/A7：HARD FAIL 0、WARN 0；`py_compile`、Black、5 个源码模块 mypy、敏感信息扫描和 `git diff --check` 均通过。pytest 有 9 条既有 httplib2/pyparsing 弃用警告。
- 真实数据源请求：0；依赖升级/卸载：0；限流参数改动：0。
