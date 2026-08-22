# scripts/ - 工具脚本目录

本目录提供项目本地化的工具脚本，避免 TRAE IDE 内置 Python 3.10 抢占调用。

## 背景

TRAE IDE 自带一个 Python 3.10 解释器并将其注入到系统 PATH 前面，导致：

- 直接运行 `python` 命令会调用 TRAE 的 3.10，而非系统的 3.12
- `pip install` 会安装到 TRAE 的 site-packages，污染 IDE 环境
- 项目测试环境与实际运行环境（系统 Python 3.12）不一致

## 解决方案

### `run_with_system_python.bat`（推荐 CMD 用户）

强制使用系统 Python 3.12：

```bat
:: 单元测试
.\scripts\run_with_system_python.bat -m unittest tests.test_cache

:: pytest 测试
.\scripts\run_with_system_python.bat -m pytest tests/test_cache.py

:: 直接运行报告脚本
.\scripts\run_with_system_python.bat get_sht_report.py 600519 --no-upload

:: 安装依赖到系统 Python
.\scripts\run_with_system_python.bat -m pip install some-package
```

### `run_with_system_python.ps1`（PowerShell 用户）

```powershell
.\scripts\run_with_system_python.ps1 -m pytest tests/
.\scripts\run_with_system_python.ps1 -m unittest tests.test_cache
```

> 注：`.bat` 版本已不再提供（V16.4.1 起仅保留 `.ps1`，Windows PowerShell 5.1 原生环境）。
>
> 如果遇到执行策略错误，先执行一次：
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

## 工作原理

两个脚本都做三件事：

1. **自检**：自动探测系统 Python 3.12（`SYSTEM_PYTHON_EXE` 环境变量 > `py -3.12` > Windows Store 包 > PATH 上 3.12）
2. **PATH 注入**：把系统 Python 3.12 目录放到 PATH 最前面
3. **透传参数**：所有命令行参数原样转发到系统 Python

## 配置自定义

如果系统 Python 路径变了，修改脚本顶部的 `PYTHON_EXE` 变量。

## 其他工具脚本

### V12.6-V14.0 新增脚本

- **`perf_compare.py`** — 【V13.2】dataclass vs dict 性能压测脚本。对比 `dataclass(slots=True, frozen=True)` 与普通 dict 的内存占用、字段访问速度、序列化开销。**不需要网络**，可直接本地运行：
  ```bat
  .\scripts\run_with_system_python.bat scripts\perf_compare.py
  ```
  输出示例（Python 3.12，5000 记录）：
  - 内存：dict 184 B/obj → dataclass 56 B/obj（**-70%**）
  - 字段访问：dict 0.066s → dataclass 0.054s（**+21% 速度**，1M reads）
  - 序列化：dict 0.005s → dataclass 0.012s（**+172%**，asdict 开销）
  - **结论**：dict 作为默认接口保留，dataclass 作为 opt-in 升级路径

- **`test_em_batch_quotes_limit.py`** — 【V12.6】东财 `push2.eastmoney.com` 批量接口单次请求上限实测脚本。渐进式测试 100/500/1000/2000/5000 只股票。**标记为 `@pytest.mark.real_network`**，需要真实网络，建议用户在网络空闲时段择机运行：
  ```bat
  .\scripts\run_with_system_python.bat scripts\test_em_batch_quotes_limit.py
  ```
  输出最大成功 N 值将用于 V13.x 阶段批量调用优化决策。

- **`check_em_health.py`** — 【V16.4.0】东财接口健康探测（6 域低频，间隔 5s 防封锁）。
  `--once` 单域验证恢复；退出码 0=全 OK/1=有 FAIL。换 IP 后/开机时使用：
  ```bat
  python scripts\check_em_health.py
  ```
- **`upload_reports_to_gd.py` / `.bat`** — 【V16.4.1】补传 `reports/` 未上传文件到 Google Drive。
  复用 `gd_uploader.py` 完整逻辑（文件夹规则/凭证/代理），**网盘已存在同名文件则跳过，只上传缺失**；
  个股报告 → 「代码-名」子文件夹，val/mak → 类型文件夹；名称缺失时按前缀匹配网盘已有文件夹。
  解决 GD 上传因超时/网络抖动漏传的问题：
  ```bat
  scripts\upload_reports_to_gd.bat            # 扫描+补传
  scripts\upload_reports_to_gd.bat --dry-run  # 只扫描不上传
  ```
- **`capture_field_probe.py`** — 【V16.4.1】**字段实测采集脚本**（用户每日采集入口）：固定 20 股 × 18 源全字段
  （ZHB/TDX/腾讯/push2+full/ulist239/新浪/AxData/财联社/KPL/板块轮动/thsdk/push2ex/人气榜/datacenter/巨潮/研报），
  输出 `docs/field_verification/YYYYMMDD/`。`--dry-run` 只检查源可用性：
  ```bat
  python scripts/capture_field_probe.py                 # 采今天
  python scripts/capture_field_probe.py --date 20260819 # 指定日期
  ```
- **`fmt_preview.py`** — 【V17.0.3】零网络格式预览：重转报告/喂模拟行，验证 md 渲染效果
- **`run_tests.ps1`** — 【V16.4.1】pytest 统一入口（Mode: all/module/real/skip_real/expression + ExtraArgs 透传）
- **`clean_cache.py`** — 缓存清理快捷脚本（封装 `python -m core.stock_cache`）
- **`gen_field_matrix.py`** — 【V16.3】从 field_dict 字段表自动生成 §零·B 字段×源矩阵（幂等重写）
- **`backtest_topn.py`** — top_n 回测验证
- **`run_with_system_python.ps1`** — 一键使用系统 Python 3.12，避免 TRAE IDE 内置 Python 3.10 抢占调用

### 历史脚本

- **`update_calendar.py`** — 从 chinese_calendar 库更新交易日历（[`stock_common/stock_calendar.py`](../stock_common/stock_calendar.py) 数据补充）
- **`sync_readme.py`** — 【V14.1】从 CHANGELOG.md 自动同步 README.md 顶部"历史版本摘要"块。设计目标：减少双重维护成本，CHANGELOG.md 作为单一权威源
  ```bat
  .\\scripts\\run_with_system_python.bat scripts\\sync_readme.py
  ```
  行为：解析 CHANGELOG.md 提取最近 8 个主要版本摘要，重写 README.md 摘要块（其他内容保持不变）。CI 集成：可在 git commit 前自动运行。