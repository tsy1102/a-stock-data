# tests 目录文件说明

本目录包含项目的 pytest 单元测试与集成测试，运行 `pytest tests/` 时会被自动收集。

## 目录结构 (V15.0 精简规整版)

```
tests/
├── __init__.py                      # 包标识（让 tests/ 可被作为包导入）
├── conftest.py                      # pytest 共享 fixtures（网络 mock、临时目录等）
├── test_cache.py                    # 统一缓存层 stock_cache（含 L1 内存 / L2 SQLite / 交叉验证）测试
├── test_calendar.py                 # A股交易日历逻辑（权威日历与 ZHB 补班校验）测试
├── test_core_defense.py             # 核心防线：令牌桶限流 + 熔断器 + ZHB 事件锁测试
├── test_external_apis.py            # 东方财富/同花顺等外部 HTTP 接口测试（需真实网络）
├── test_f10_chapters_integration.py # 短/中/长线报告 F10 章节与舆情集成测试（需真实网络）
├── test_field_routing.py            # 【V15.0】字段路由矩阵、CanonicalStockData 与断路器无缝降级测试
├── test_gd_uploader.py              # Google Drive 上传模块单元测试
├── test_report_runner.py            # ReportRunner 基类与 6 大子类 Runner 测试
├── test_sc_schema.py                # 【V15.0】CanonicalStockData（dataclass / to_dict / 序列化）测试
├── test_scoring.py                  # 评分系统（ScoreData / calculate_score）测试
├── test_stock_common.py             # 公共工具函数（_safe_float / get_board_type 等）测试
├── test_strategy.py                 # 策略配置与 get_val_report 策略函数测试
├── test_tdx_client.py               # 通达信 TCP 客户端接口测试（需真实网络）
└── test_zhb_client.py               # ZHB 配置文件解析、数据集集成与 fallback 机制测试
```

## 测试分类

### 1. 核心模块单元测试（默认离线运行）

外部 HTTP 请求默认被 `conftest.py` 的 `_no_real_network` autouse fixture 全局拦截，不会触发真实网络调用。

- **test_stock_common.py**: 测试 `sc_utils` 中的工具函数（如 `_safe_float`、`get_board_type`、`is_limit_up`、`clean_codes`）。
- **test_sc_schema.py**: 测试 `CanonicalStockData` 强类型数据合约、不可变约束、字典与序列化转换。
- **test_field_routing.py**: 测试 ZHB-First 盘前/盘中/盘后精确路由机制，以及网络断路器熔断时的静默无缝降级。
- **test_scoring.py**: 测试评分系统逻辑（`ScoreData`、`_score_technical`、`_score_fundamental`、`_score_valuation`、`calculate_score` 等）。
- **test_cache.py**: 测试 `stock_cache` 的读写、TTL 过期、分类/前缀失效、`cross_verify` 交叉验证、`STOCK_NOCACHE` 禁用等。
- **test_calendar.py**: 测试 A 股交易日历（节假日、调休日、周末、边界与错误输入）。
- **test_gd_uploader.py**: 测试 Google Drive 上传模块的代理探测、环境变量清理、文件夹创建、文件上传等逻辑。
- **test_strategy.py**: 测试 `strategy_config.yaml` / `keywords_config.yaml` 配置加载，以及策略函数的可调用性。

### 2. 外部接口与数据源测试（需真实网络）

带有 `@pytest.mark.real_network` 标记的测试会跳过网络 mock，发起真实请求。未带标记运行时这些测试会被 conftest 拦截并大概率跳过。

- **test_tdx_client.py**: 测试通达信 TCP/Mac 接口（K 线、行情、资金流、分红、EPS、所属板块、板块成员等）。
- **test_zhb_client.py**: 测试 zhb 配置文件下载、6 大新数据集解析与缓存机制。
- **test_external_apis.py**: 测试东方财富数据中心、研报、个股新闻、股东结构、北向资金、融资融券、大宗交易、限售解禁、行业对比等外部接口。

### 3. 业务报告集成测试（需真实网络）

- **test_f10_chapters_integration.py**: 验证中线报告（med）、长线报告（lng）、全维度报告（ful）中 F10 章节与舆情互动章节的渲染集成。

## 日常使用指南

> **AGENTS.md 强制规则**:仅在"主动发起一次测试套件"时,严禁直接调 `pytest ...` / `python -m pytest ...` / `powershell -Command "pytest ..."`。
> 写测试代码(`import pytest`、`@pytest.fixture`、`@pytest.mark.xxx`)完全 OK,pytest 是 Python 库,跟 shell 无关。
> 跑测试一律走 [scripts/run_tests.ps1](../../scripts/run_tests.ps1) 中转,详见 AGENTS.md 2.1.1 / 2.1.2。

1. **运行所有测试（默认离线，245 项测试 100% 通过）**
   ```powershell
   .\scripts\run_tests.ps1                       # Mode=all
   ```

2. **运行特定模块测试**
   ```powershell
   .\scripts\run_tests.ps1 -Mode module -Path tests/test_field_routing.py
   ```

3. **仅运行涉及真实网络请求的测试**
   ```powershell
   .\scripts\run_tests.ps1 -Mode real
   ```

4. **跳过真实网络测试（默认行为，等价于不加 `-m real_network`）**
   ```powershell
   .\scripts\run_tests.ps1 -Mode skip_real
   ```

5. **加额外参数（透传）**
   ```powershell
   .\scripts\run_tests.ps1 -Mode all -ExtraArgs '--maxfail=1','-x'
   ```

## 网络隔离说明

`conftest.py` 通过 autouse fixture `_no_real_network` 拦截 `requests.get` / `requests.post` 与 `urllib.request.urlopen`，确保离线测试不会污染真实网络。需要真实网络的测试必须显式添加 `@pytest.mark.real_network` 标记，fixture 检测到该标记后会自动放行。

*最后更新时间：2026-07-26 (V15.1 同步)*
