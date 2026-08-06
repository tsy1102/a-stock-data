# tests 目录说明

本目录包含项目的 pytest 单元测试与集成测试，运行 `.\scripts\run_tests.ps1` 时自动收集。

## 目录结构（V16.3 F 按架构分层重构）

```
tests/
├── conftest.py                    # pytest 共享 fixtures（real_network 网络拦截）
├── data/                          # ① 数据源层（数据从哪来）
│   ├── test_data_zhb.py           # ZHB 包解析 / 字段破解 / 行业段过滤
│   ├── test_data_tdx.py           # TDX TCP / 适配器 / 服务器白名单
│   ├── test_data_eastmoney.py     # 东财接口 / 13 域健康矩阵（real_network）
│   └── test_data_network.py       # 令牌桶限流 / 熔断器 / 20h 封禁冷却
├── core/                          # ② 统一层 / 服务层
│   ├── test_core_cache.py         # 统一缓存层（L1/L2/交叉验证/版本化）
│   ├── test_core_schema.py        # CanonicalStockData / 归一化
│   ├── test_core_routing.py       # 字段路由矩阵 / 断路器降级
│   ├── test_core_calendar.py      # 交易日历（权威日历 + ZHB 补班校验）
│   ├── test_core_technical.py     # 技术指标 / 风险引擎
│   ├── test_core_scoring.py       # 评分系统
│   └── test_core_utils.py         # 公共工具（_safe_float/is_limit_up/_safe_cast 等）
├── reports/                       # ③ 报告应用层
│   ├── test_report_runner.py      # ReportRunner 基类 / 5 大 Runner 防退化
│   └── test_report_strategy.py    # 策略配置 / 策略函数 / SMA
└── infra/                         # ④ 基础设施（外部依赖）
    ├── test_infra_gd.py           # Google Drive 上传
    ├── test_infra_f10.py          # F10 章节集成（real_network）
    └── test_infra_api_stability.py # 外部 API 字段契约（real_network）
```

## 快速定位规则

| 遇到问题 | 找哪个测试 |
|:---|:---|
| ZHB 数据/字段不对 | `data/test_data_zhb.py` |
| TDX 行情/白名单 | `data/test_data_tdx.py` |
| 东财被封/接口变化 | `data/test_data_eastmoney.py` |
| 限流/熔断/封禁 | `data/test_data_network.py` |
| 缓存失效/污染 | `core/test_core_cache.py` |
| 字段口径/归一化 | `core/test_core_schema.py` |
| 日历/节假日 | `core/test_core_calendar.py` |
| 评分/技术指标 | `core/test_core_scoring.py` / `core/test_core_technical.py` |
| 策略不工作 | `reports/test_report_strategy.py` |
| Runner/报告框架 | `reports/test_report_runner.py` |

## 测试分类

### 1. 离线单元测试（默认运行）

外部 HTTP 请求默认被 `conftest.py` 的 `_no_real_network` autouse fixture 全局拦截。

### 2. 外部接口测试（需真实网络）

带 `@pytest.mark.real_network` 标记（已在 `pyproject.toml` markers 注册）。离线运行时被拦截并跳过（deselected）。

### 3. 命名规约

- 文件命名：`test_<层>_<主题>.py`（层 = data/core/reports/infra）
- **禁止版本号命名**（如 `test_v163_features`）——新功能测试按主题归入对应层文件
- 新增功能必须带测试（防退化守护同层更新）

## 日常使用

```powershell
.\scripts\run_tests.ps1                                       # 全部离线测试
.\scripts\run_tests.ps1 -Mode module -Path tests/data/test_data_zhb.py   # 单文件
.\scripts\run_tests.ps1 -Mode skip_real -ExtraArgs '--maxfail=1','-x'    # 失败即停
$env:REAL_NETWORK=1; .\scripts\run_tests.ps1 -Mode real        # 仅真网络测试
```
