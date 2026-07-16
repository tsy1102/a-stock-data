# tests 目录文件说明

本目录包含项目的 pytest 单元测试与集成测试，运行 `pytest tests/` 时会被自动收集。

## 目录结构

```
tests/
├── __init__.py                      # 包标识（让 tests/ 可被作为包导入）
├── conftest.py                      # pytest 共享 fixtures（网络 mock、临时目录等）
├── test_cache.py                    # 统一缓存层 stock_cache 单元测试
├── test_cache_verify.py             # 缓存交叉验证（cross_verify）机制测试
├── test_calendar.py                 # A股交易日历逻辑测试
├── test_external_apis.py            # 东方财富/同花顺等外部 HTTP 接口测试（需真实网络）
├── test_f10_chapters_integration.py # 短/中/长线报告 F10 章节集成测试（需真实网络）
├── test_gd_uploader.py              # Google Drive 上传模块单元测试
├── test_scoring.py                  # 评分系统（ScoreData / calculate_score）测试
├── test_stock_common.py             # 公共工具函数（_safe_float / get_board_type 等）测试
├── test_strategy.py                 # 策略配置与 get_val_report 策略函数测试
├── test_tdx_client.py               # 通达信客户端接口测试（需真实网络）
└── test_zhb_client.py               # zhb 配置文件下载/解析/缓存机制测试
```

## 测试分类

### 1. 核心模块单元测试（默认离线运行）

外部 HTTP 请求默认被 `conftest.py` 的 `_no_real_network` autouse fixture 全局拦截，不会触发真实网络调用。

- **test_stock_common.py**: 测试 `sc_utils` 中的工具函数（如 `_safe_float`、`get_board_type`、`is_limit_up`、`clean_codes`）。
- **test_scoring.py**: 测试评分系统逻辑（`ScoreData`、`_score_technical`、`_score_fundamental`、`_score_valuation`、`calculate_score` 等）。
- **test_cache.py**: 测试 `stock_cache` 的读写、TTL 过期、分类/前缀失效、`@cached` 装饰器、`STOCK_NOCACHE` 禁用等。
- **test_cache_verify.py**: 测试 `cross_verify` 交叉验证机制（首次未验证、二次一致验证通过、数据变化重置、已验证不被覆盖）。
- **test_calendar.py**: 测试 A 股交易日历（节假日、调休日、周末、边界与错误输入）。
- **test_gd_uploader.py**: 测试 Google Drive 上传模块的代理探测、环境变量清理、文件夹创建、文件上传等逻辑（通过 mock 拦截，不发真实请求）。
- **test_strategy.py**: 测试 `strategy_config.yaml` / `keywords_config.yaml` 配置加载，以及 `get_val_report` 中策略函数的可调用性与健壮性。

### 2. 外部接口与数据源测试（需真实网络）

带有 `@pytest.mark.real_network` 标记的测试会跳过网络 mock，发起真实请求。未带标记运行时这些测试会被 conftest 拦截并大概率失败/跳过。

- **test_tdx_client.py**: 测试通达信 TCP/Mac 接口（K 线、行情、资金流、分红、EPS、所属板块、板块成员等）。
- **test_zhb_client.py**: 测试 zhb 配置文件下载、解析与缓存机制（含 `sc_datasource` 中的 zhb 系列函数）。
- **test_external_apis.py**: 测试东方财富数据中心、研报、个股新闻、股东结构、北向资金、融资融券、大宗交易、限售解禁、行业对比、热度概念等外部接口。

### 3. 业务报告集成测试（需真实网络）

- **test_f10_chapters_integration.py**: 验证中线报告（med）、长线报告（lng）、全维度报告（ful）中 F10 章节与舆情互动章节的渲染集成。

## 日常使用指南

1. **运行所有测试（默认离线）**
   ```bash
   pytest tests/ -v
   ```

2. **运行特定模块测试**
   ```bash
   pytest tests/test_cache.py -v
   ```

3. **仅运行涉及真实网络请求的测试**
   ```bash
   pytest tests/ -m real_network -v
   ```

4. **跳过真实网络测试（默认行为，等价于不加 `-m real_network`）**
   ```bash
   pytest tests/ -v -m "not real_network"
   ```

## 网络隔离说明

`conftest.py` 通过 autouse fixture `_no_real_network` 拦截 `requests.get` / `requests.post` 与 `urllib.request.urlopen`，确保离线测试不会污染真实网络。需要真实网络的测试必须显式添加 `@pytest.mark.real_network` 标记，fixture 检测到该标记后会自动放行。

*最后更新时间：2026-07-16*
