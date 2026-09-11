# tests 目录说明

本目录包含项目的 pytest 单元测试与集成测试，运行 `.\scripts\run_tests.ps1` 时自动收集。

> **V17.0**: 核心模块已包化到 `core/`——测试中引用 config/data_provider/gd_uploader/
> stock_cache/tdx_client/zhb_client/zhb_sync 一律 `from core.X import ...`;
> `patch("core.tdx_client.xxx")`(mock 字符串同样带 core. 前缀, 否则假绿)。

## 目录结构（V16.3 F 按架构分层重构）

```
tests/
├── conftest.py                    # pytest 共享 fixtures（real_network 网络拦截）
├── data/                          # ① 数据源层（数据从哪来）— 5 文件 / 113 例
│   ├── test_data_zhb.py           # ZHB 包解析 / 字段破解 / 行业段过滤（45）
│   ├── test_data_tdx.py           # TDX TCP / 适配器 / 服务器白名单（40）
│   ├── test_data_eastmoney.py     # 东财接口 / 13 域健康矩阵（15，全 real_network）
│   ├── test_data_network.py       # 令牌桶限流 / 熔断器 / 20h 封禁冷却（10）
│   └── test_data_prefetch.py      # sht 批量预取映射/单位换算/缓存命中（3）
├── core/                          # ② 统一层 / 服务层 — 10 文件 / 179 例
│   ├── test_core_calendar.py      # 交易日历（权威日历 + ZHB 补班校验）（38）
│   ├── test_core_utils.py         # 公共工具（_safe_float/is_limit_up/_safe_cast 等）（33）
│   ├── test_core_schema.py        # CanonicalStockData / 归一化（31）
│   ├── test_core_scoring.py       # 评分系统（21）
│   ├── test_core_routing.py       # 字段路由矩阵 / 断路器降级（14）
│   ├── test_core_technical.py     # 技术指标 / 风险引擎（13）
│   ├── test_core_cache.py         # 统一缓存层（L1/L2/交叉验证/版本化）（11）
│   ├── test_core_tencent_volume_unit.py # 科创板 688 成交量单位换算（8，V17.0.12 新增）
│   ├── test_core_seat.py          # 龙虎榜席位三层匹配（6）
│   └── test_core_capital_cache.py # 股本缓存单位自愈/schema 版本失效（4）
├── infra/                         # ③ 基础设施（外部依赖）— 3 文件 / 14 例
│   ├── test_infra_gd.py           # Google Drive 上传（7）
│   ├── test_infra_api_stability.py # 外部 API 字段契约（5，real_network）
│   └── test_infra_f10.py          # F10 章节集成（2，real_network）
└── reports/                       # ④ 报告层（2026-08-30 新补）— 3 文件 / 64 例
    ├── test_reports_runner.py     # ReportRunner 基类 + execute_batch_pipeline 骨架（22）
    ├── test_reports_strategy.py   # val 23 策略注册表 / 空池安全 / 配置键（12）
    └── test_reports_pipeline.py   # 5 个 Runner 子类 execute_pipeline 装配（42）
```

> **2026-08-30 校正**：本目录结构按实际文件重写。
> - 原 `reports/` 层历史上一度规划过（`test_report_runner.py` / `test_report_strategy.py`）
>   但**从未落地**；2026-08-30 已按 `test_<层>_<主题>.py` 规约**重新补齐**为
>   `test_reports_runner.py` / `test_reports_strategy.py`。
> - 现为 **data / core / infra / reports 四层**（21 文件 / **370 个测试函数**；
>   pytest 收集 398 项，差值为参数化展开 + mixin 被 3 个子类复用）。
> - 回归基线 **353 passed / 45 deselected / 0 failed**（`skip_real`，2026-08-30 实测）；
>   演进 302 → 269 → 277 → 311 → **353**（+34 基类骨架与策略注册表，+42 五个 Runner 装配）。
>   判回归一律以 **353** 为准。
> - ✅ 命名不一致**已修**（2026-08-30）：`tests/core/test_tencent_volume_unit.py` 未按
>   `test_<层>_<主题>.py` 规约带 `core_` 前缀，已 `git mv` 为 `test_core_tencent_volume_unit.py`
>   （保留 git 重命名历史）。已核查全仓无外部引用（`scripts/` 零引用；文档引用已同步）。

## 快速定位规则

| 遇到问题 | 找哪个测试 |
|:---|:---|
| ZHB 数据/字段不对 | `data/test_data_zhb.py` |
| TDX 行情/白名单 | `data/test_data_tdx.py` |
| 东财被封/接口变化 | `data/test_data_eastmoney.py` |
| 限流/熔断/封禁 | `data/test_data_network.py` |
| 缓存失效/污染 | `core/test_core_cache.py` |
| 股本单位/schema 版本 | `core/test_core_capital_cache.py` |
| 批量预取映射 | `data/test_data_prefetch.py` |
| 字段口径/归一化 | `core/test_core_schema.py` |
| 日历/节假日 | `core/test_core_calendar.py` |
| 评分/技术指标 | `core/test_core_scoring.py` / `core/test_core_technical.py` |
| 龙虎榜席位匹配 | `core/test_core_seat.py` |
| 科创板成交量单位 | `core/test_core_tencent_volume_unit.py` |
| GD 上传失败 | `infra/test_infra_gd.py` |
| 降级/fallback 顺序 | `core/test_core_routing.py` |
| **策略不工作（val 23 策略）** | `reports/test_reports_strategy.py` |
| **Runner/批量流水线骨架** | `reports/test_reports_runner.py` |
| **5 个 Runner 子类取数/装配** | `reports/test_reports_pipeline.py` |
| **报告正文渲染/章节内容** | ⚠️ **无专职测试** — 同下方缺口 |

> ✅ **reports/ 层已补齐（2026-08-30，共 64 例）**，分两批落地：
> - **① 骨架与注册表（22 + 12）**：`ReportRunner` 基类契约、`execute_batch_pipeline`
>   五大骨架能力（代码清洗 / 并发上限 3 / 单股失败隔离 / 两个预取钩子容错 / 快照落盘）、
>   GD 上传编排，以及 `val` 的 23 策略注册表一致性 + 空池安全 + 配置键存在性。
> - **② 五个 Runner 装配（42）**：`sht/med/lng/val/mak` 的 `execute_pipeline`
>   ——公共契约（返回类型 / `report_type` / 生成器绑定 / 快照代理透传 / 上游调用次数钉死）、
>   sht 四指数行情与 depth→席位开关、`val` 的 async→sync 回退与 V16.3 O39「文件不存在
>   不得假成功」守卫、`mak` 无 sync 回退必须抛错。
>
> 两批用例均经**变异测试**验证有效，共注入 7 处回归全部被捕获：
> 批次①「调度表漏登记策略25」「并发上限 3→99」「单股失败不再隔离」；
> 批次②「sht 少取一个指数」「val 删掉 sync 回退」「val 去掉 O39 文件存在性校验」
> 「mak 静默吞异常」。
>
> ⚠️ **剩余缺口（已收窄）**：仅剩**报告正文渲染结果**（生成的 md 章节内容/措辞/数据
> 呈现）无测试——需对数据层做大量打桩，成本高、易与业务改动耦合。
> 取数与章节**装配**逻辑现已有回归保护；修改报告**正文渲染**时仍**勿假设已有保护**。
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
  定位表、命名规约三处同时引用了已删除的 `reports/` 层）

## 日常使用

```powershell
.\scripts\run_tests.ps1                                       # 全部离线测试
.\scripts\run_tests.ps1 -Mode module -Path tests/data/test_data_zhb.py   # 单文件
.\scripts\run_tests.ps1 -Mode skip_real -ExtraArgs '--maxfail=1','-x'    # 失败即停
$env:REAL_NETWORK=1; .\scripts\run_tests.ps1 -Mode real        # 仅真网络测试
```
