# tests 目录说明

本目录包含项目的 pytest 单元测试与集成测试，运行 `.\scripts\run_tests.ps1` 时自动收集。

> **V17.0**: 核心模块已包化到 `core/`——测试中引用 config/data_provider/gd_uploader/
> stock_cache/tdx_client/zhb_client/zhb_sync 一律 `from core.X import ...`;
> `patch("core.tdx_client.xxx")`(mock 字符串同样带 core. 前缀, 否则假绿)。
>
> **V17.2**: 数据源真实包为 `stock_common.*`——测试中 `from stock_common.sc_datasource import ...`、
> `patch("stock_common.sc_datasource.xxx")` 为正确写法（与运行时包结构一致，原 README 所述 `core.X` 为笔误）。

## 目录结构（2026-09-12 同步）

```
tests/
├── conftest.py                       # pytest 共享 fixtures（real_network 网络拦截）
├── test_degradation_contract.py      # 三层数据源降级契约 L1/L2/L3/L4 + 降级等价性
├── test_sc_ta_core.py                # 技术指标核心：ref/sum_rolling/hhv/llv/sma/macd/rsi/boll/kdj 等
├── test_symbol_norm.py               # 股票代码归一化（市场段/前缀/后缀/矛盾检测）
├── test_seat_db_audit_fix.py         # 龙虎榜席位评分降级回归（审计 P1-6 修复守护）
├── data/                            # ① 数据源层（数据从哪来）— 7 文件
│   ├── test_data_zhb.py              # ZHB 包解析 / 字段破解 / 行业段过滤
│   ├── test_data_tdx.py              # TDX TCP / 适配器 / 服务器白名单
│   ├── test_data_eastmoney.py        # 东财接口 / 多域健康矩阵（全 real_network）
│   ├── test_data_network.py          # 令牌桶限流 / 熔断器 / 封禁冷却
│   ├── test_data_prefetch.py         # 批量预取映射 / 单位换算 / 缓存命中
│   ├── test_data_em_board_members.py # 东财董事会成员
│   └── test_data_em_fund_flow_tiers.py # 东财资金流分层
├── core/                            # ② 统一层 / 服务层 — 12 文件
│   ├── test_core_calendar.py         # 交易日历（权威日历 + ZHB 补班校验）
│   ├── test_core_utils.py            # 公共工具（_safe_float/is_limit_up/_safe_cast 等）
│   ├── test_core_schema.py           # CanonicalStockData / 归一化
│   ├── test_core_scoring.py          # 评分系统
│   ├── test_core_routing.py          # 字段路由矩阵 / 断路器降级
│   ├── test_core_technical.py        # 技术指标 / 风险引擎
│   ├── test_core_cache.py            # 统一缓存层（L1/L2/交叉验证/版本化）
│   ├── test_core_tencent_volume_unit.py # 科创板 688 成交量单位换算
│   ├── test_core_seat.py             # 龙虎榜席位三层匹配
│   ├── test_core_capital_cache.py    # 股本缓存单位自愈 / schema 版本失效
│   ├── test_core_blob_cache.py       # 统一层 blob 缓存
│   ├── test_core_cyq.py              # 筹码分布（CYQ）计算
│   └── test_sec_type_exposure.py     # 证券类型→板块标签（DEBT-016 锁固，位于 core/ 下）
├── infra/                           # ③ 基础设施（外部依赖）— 3 文件
│   ├── test_infra_gd.py              # Google Drive 上传
│   ├── test_infra_api_stability.py   # 外部 API 字段契约（real_network）
│   └── test_infra_f10.py             # F10 章节集成（real_network）
└── reports/                         # ④ 报告层 — 5 文件（已纳入版本控制）
    ├── test_reports_runner.py        # ReportRunner 基类 + execute_batch_pipeline 骨架
    ├── test_reports_strategy.py      # val 27 策略注册表 / 空池安全 / 配置键
    ├── test_reports_pipeline.py      # 5 个 Runner 子类 execute_pipeline 装配
    ├── test_reports_chapter_omission.py # 报告章节缺失检测
    └── test_reports_val_turnover.py  # val 换手率相关
```

> **2026-09-12 校正**：本目录结构按实际文件重写并核对。
> - 共 **33 个测试文件**（不含 `conftest.py` 共享 fixtures），分 data(7) / core(13) / infra(3) / reports(5)
>   四层 + 顶层 4 个专项测试（degradation_contract / sc_ta_core / symbol_norm / seat_db_audit_fix）。
> - pytest 实际收集约 **561 个测试项**（含参数化展开；具体以 `pytest tests/ --collect-only` 实时为准）。
> - **reports/ 曾因 `.gitignore:26` 的 `reports/` 规则被误忽略**（该规则本意忽略根级运行时输出目录），导致 5 个报告层
>   测试长期游离于版本控制之外；已加 `!tests/reports/` 例外并纳入版本库（commit 见版本历史）。
> - 已删除 `tests/_run_ta_tests.py`（手动桩运行器，注释前提"pytest 未装"已不成立，且 `_` 前缀不进 pytest 套件）。
> - 命名规约：`test_<层>_<主题>.py`，层名与所在目录名一致；更新本 README 须按实际文件核对，勿沿用旧结构。

## 快速定位规则

| 遇到问题 | 找哪个测试 |
|:---|:---|
| ZHB 数据/字段不对 | `data/test_data_zhb.py` |
| TDX 行情/白名单 | `data/test_data_tdx.py` |
| 东财被封/接口变化 | `data/test_data_eastmoney.py` |
| 限流/熔断/封禁 | `data/test_data_network.py` |
| 批量预取映射 | `data/test_data_prefetch.py` |
| 东财董事会成员 | `data/test_data_em_board_members.py` |
| 东财资金流分层 | `data/test_data_em_fund_flow_tiers.py` |
| 缓存失效/污染 | `core/test_core_cache.py` |
| 股本单位/schema 版本 | `core/test_core_capital_cache.py` |
| blob 缓存 | `core/test_core_blob_cache.py` |
| 筹码分布 CYQ | `core/test_core_cyq.py` |
| 字段口径/归一化 | `core/test_core_schema.py` |
| 日历/节假日 | `core/test_core_calendar.py` |
| 评分/技术指标 | `core/test_core_scoring.py` / `core/test_core_technical.py` |
| 数据源降级契约 | `test_degradation_contract.py` |
| 技术指标核心(ref/sma/macd...) | `test_sc_ta_core.py` |
| 代码归一化 | `test_symbol_norm.py` |
| 龙虎榜席位匹配/评分降级 | `core/test_core_seat.py` / `test_seat_db_audit_fix.py` |
| 科创板成交量单位 | `core/test_core_tencent_volume_unit.py` |
| 板块标签/涨跌幅限制 | `core/test_sec_type_exposure.py` |
| GD 上传失败 | `infra/test_infra_gd.py` |
| 降级/fallback 顺序 | `core/test_core_routing.py` |
| 策略不工作（val 27 策略） | `reports/test_reports_strategy.py` |
| Runner/批量流水线骨架 | `reports/test_reports_runner.py` |
| 5 个 Runner 子类取数/装配 | `reports/test_reports_pipeline.py` |
| 报告章节缺失检测 | `reports/test_reports_chapter_omission.py` |
| val 换手率 | `reports/test_reports_val_turnover.py` |
| 报告正文渲染/章节内容 | ⚠️ 无专职测试（见下） |

> **reports/ 层（5 文件，已纳入版本控制）**：覆盖 ReportRunner 基类契约、`execute_batch_pipeline`
> 五大骨架能力、val 27 策略注册表一致性 + 空池安全 + 配置键存在性，以及 5 个 Runner 子类
> `execute_pipeline` 装配（公共契约 / 生成器绑定 / 快照代理透传 / 上游调用次数钉死 / sync 回退守卫等）。
> 两批用例均经变异测试验证有效。
>
> ⚠️ **剩余缺口**：仅剩**报告正文渲染结果**（生成的 md 章节内容/措辞/数据呈现）无测试——
> 需对数据层做大量打桩，成本高、易与业务改动耦合。修改报告正文渲染时仍**勿假设已有保护**。
> 相关进度见 `docs/roadmap.md` V17-1 / V17-15。

## 测试分类

### 1. 离线单元测试（默认运行）

外部 HTTP 请求默认被 `conftest.py` 的 `_no_real_network` autouse fixture 全局拦截。

### 2. 外部接口测试（需真实网络）

带 `@pytest.mark.real_network` 标记（已在 `pyproject.toml` markers 注册）。离线运行时被拦截并跳过（deselected）。

### 3. 命名规约

- 文件命名：`test_<层>_<主题>.py`（层 = **data / core / infra / reports**，层名与所在目录名一致）
- **禁止版本号命名**（如 `test_v163_features`）——新功能测试按主题归入对应层文件
- 新增功能必须带测试（防退化守护同层更新）
- 更新本 README 时**必须按实际文件核对**，勿沿用旧结构（2026-08-30 曾发现目录树、
  定位表、命名规约三处同时引用了已删除的 `reports/` 层；2026-09-12 又发现 `reports/` 被
  `.gitignore` 误忽略导致长期未受控）

## 日常使用

```powershell
.\scripts\run_tests.ps1                                       # 全部离线测试
.\scripts\run_tests.ps1 -Mode module -Path tests/data/test_data_zhb.py   # 单文件
.\scripts\run_tests.ps1 -Mode skip_real -ExtraArgs '--maxfail=1','-x'    # 失败即停
$env:REAL_NETWORK=1; .\scripts\run_tests.ps1 -Mode real        # 仅真网络测试
```
