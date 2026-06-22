# A股个股分析报告生成系统

一套自动化生成A股个股分析报告的Python工具集，支持短线、中线、长线、完整、估值、市场热点等多种报告类型，数据来源于新浪财经、东方财富、同花顺等主流平台。

---

## 功能特性

- **6种报告类型**：短线(sht)、中线(med)、长线(lng)、完整(ful)、估值(val)、市场热点(mak)
- **多数据源整合**：新浪财经、东方财富、同花顺、通达信等
- **交易日历判断**：自动识别中国A股交易日、节假日、调休日、午休时段
- **云端同步**：支持Google Drive自动上传报告
- **批量处理**：支持多股票、多报告类型并行生成
- **代码清洗**：自动处理股票代码格式问题
- **统一缓存层**：SQLite + TTL 自动过期，降低 API 请求频率
- **异步并发**：30+ 异步函数支持高效并发请求
- **类型安全**：mypy 静态检查通过，类型注解完整覆盖

---

## 快速开始

### 环境要求

- Python 3.9+
- Windows / macOS / Linux

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本用法

```bash
# 生成短线报告
python main.py --sht 600519 000858

# 生成中线报告
python main.py --med 600519 000858

# 生成多种报告
python main.py --sht 600519 --med 600519 --lng 600519

# 批量处理
python main.py --sht 600519 000858 03606 --med 600519 000858
```

---

## 报告类型说明

| 参数 | 报告类型 | 说明 |
|------|----------|------|
| `--sht` | 短线报告 | 90日内解禁、近期资金流向、短线技术指标 |
| `--med` | 中线报告 | 180日内解禁、财务分析、行业对比、机构持仓 |
| `--lng` | 长线报告 | 730日内解禁、深度财务分析、股东变化、估值分析 |
| `--ful` | 完整报告 | 综合报告，包含所有分析维度 |
| `--val` | 估值报告 | PE/PB估值、行业估值对比、估值历史分位 |
| `--mak` | 市场热点 | 行业热点、概念题材、资金流向 |

---

## 命令行参数

```
python main.py [选项] 股票代码...

选项:
  --sht    生成短线报告
  --med    生成中线报告
  --lng    生成长线报告
  --ful    生成完整报告
  --val    生成估值报告
  --mak    生成市场热点报告
  --all    生成所有报告类型
  --no-gd  禁用Google Drive上传
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
├── main.py                   # 主入口程序（参数分发/多报告并行）
├── stock_common.py           # 核心数据获取函数库（网络请求/缓存/类型接口）
├── stock_cache.py            # 统一缓存层（SQLite + TTL 装饰器）
├── stock_calendar.py         # 交易日历模块（含节假日/调休日数据）
├── gd_uploader.py            # Google Drive上传模块（folderId 动态查找）
├── tdx_client.py             # 通达信数据客户端（easy-tdx 行情接口封装）
├── get_sht_report.py         # 短线报告生成（90日窗口）
├── get_med_report.py         # 中线报告生成（180日窗口）
├── get_lng_report.py         # 长线报告生成（730日窗口）
├── get_ful_report.py         # 完整报告生成（综合评分）
├── get_val_report.py         # 估值报告生成（策略选股）
├── get_mak_report.py         # 市场热点报告生成（异动扫描）
├── strategy_config.yaml      # 统一策略参数配置文件（评分/阈值/权重）
├── pyproject.toml            # pytest / mypy / black 等工具配置中心
├── requirements.txt          # 运行时依赖列表
├── CHANGELOG.md              # 版本变更记录
├── reports/                  # 报告输出目录（运行时自动创建）
├── snapshots/                # 评分快照（历史对比/背离检测）
└── tests/                    # pytest 单元测试用例
```

---

## 配置文件

### requirements.txt

```
requests>=2.28.0
aiohttp>=3.8.0
pandas>=1.5.0
numpy>=1.23.0
easy-tdx>=1.0,<2.0
chinese-calendar>=1.11.0
google-api-python-client>=2.0.0
google-auth-oauthlib>=1.0.0
pyyaml>=6.0
```

### Google Drive 配置（可选）

如需启用云端上传功能：

1. 在 Google Cloud Console 创建项目并启用 Drive API
2. 下载 OAuth 2.0 凭证文件，保存为 `credentials.json`
3. 首次运行时会弹出浏览器进行授权

---

## 核心模块说明

### stock_common.py

核心数据获取函数库，提供以下功能：

```python
# 股票基本信息
get_stock_info(code)                    # 获取股票名称、行业等基本信息

# 财务数据
get_sina_financial_report(code)         # 新浪财报数据
get_sina_balance_sheet(code)            # 新浪资产负债表
get_gross_margin_and_roe(code)          # 毛利率和ROE数据

# 资金流向
get_hsgt_macro_flow()                   # 沪深港通资金流向
get_northbound_hold_async(code)         # 北向资金持股
get_margin_trading_async(code)          # 融资融券数据
get_block_trade_async(code)             # 大宗交易数据

# 解禁数据
get_lockup_expiry(code, days, include_history)  # 解禁到期数据

# 交易日历
is_trading_day(date)                    # 判断是否交易日
get_market_status()                     # 获取当前市场状态

# 工具函数
clean_codes(codes)                      # 清洗股票代码
```

### stock_cache.py

统一缓存层，用于降低 API 请求频率、避免重复网络请求。关键特性：

- **SQLite 持久化**：缓存写入项目根目录 `cache/stock_cache.db`，支持程序重启后读取
- **TTL 分级策略**：按数据类型配置不同过期时间（财务数据 90 天，龙虎榜/北向数据当日有效，概念板块 7 天，研报 3 天，通用兜底 1 小时）
- **装饰器模式**：通过 `@cached(category="xxx")` 一行启用函数级缓存，不需改写业务逻辑
- **手动失效**：提供 `invalidate_category("dragon_tiger")`、`clear_all()` 等手动清理接口
- **环境变量开关**：`STOCK_NOCACHE=1 python main.py ...` 临时禁用缓存（调试用）
- **CLI 工具**：`python stock_cache.py stats` 查看缓存命中率、条目数量、占用空间

```python
from stock_cache import cached, invalidate_category, print_cache_stats

# 例：给一个网络请求函数加缓存
@cached(category="dragon_tiger", ttl_seconds=24 * 3600)
def get_dragon_tiger_board(code, today_str, days=30, include_seats=True):
    ...

# 例：清除某分类缓存（重新拉取当日数据前）
invalidate_category("dragon_tiger")

# 例：查看缓存统计
print_cache_stats()
```

### stock_calendar.py

交易日历模块，支持：

- 中国A股交易日判断（含节假日、调休日）
- 市场状态判断（盘前/上午/午休/下午/盘后/休市）
- 自动升级节假日数据（依赖 chinese-calendar 库）

```python
from stock_common import is_trading_day, get_market_status

# 判断今天是否交易日
if is_trading_day():
    print("今天是交易日")

# 获取市场状态
status, message = get_market_status()
# status: closed/pre_market/morning/lunch/afternoon/post_market
# message: "已休市" / "盘前" / "上午交易中" / "午休时段" / "下午交易中" / "盘后结算"
```

---

## 输出示例

报告文件命名格式：`{股票代码}_{报告类型}_{日期}_{时间}.txt`

```
reports/
├── 600519_sht_20260618_1430.txt    # 茅台短线报告
├── 600519_med_20260618_1435.txt    # 茅台中线报告
├── 600519_lng_20260618_1440.txt    # 茅台长线报告
└── get_val_report_20260618_1445.txt # 估值汇总报告
```

---

## 版本历史

完整版本历史详见 [CHANGELOG.md](CHANGELOG.md)

### v8.4.0 (2026-06-22)

- ✅ **新增统一缓存层**：`stock_cache.py`（SQLite + TTL 装饰器），覆盖龙虎榜/北向/财务/概念板块等 25+ 个网络请求函数
- ✅ **新增异步函数族**：`get_northbound_hold_async`、`get_margin_trading_async`、`get_block_trade_async`、`get_dividend_history_async`、`get_concept_blocks_async`、`get_industry_peers_async` 等 22+ 个异步接口
- ✅ **类型注解补齐**：~25 个函数补上 PEP 484 类型注解（参数 + 返回值），mypy 静态检查通过
- ✅ **参数外置**：硬编码阈值（换手率/PE/PB/封单强度等）统一从 `strategy_config.yaml` 读取，便于策略调参
- ✅ **新增测试文件**：`tests/test_calendar.py`（交易日历）、`tests/test_cache.py`（缓存层）、`tests/test_strategy.py`（选股策略）
- ✅ **工具配置中心化**：`pyproject.toml` 集中管理 pytest/mypy/black
- ⚡ **性能提升**：缓存命中率可降至 50-80% 网络请求（视使用频率）；异步化让批量报告生成提速 3-5x

### v8.3.0 (2026-06-18)

- ✅ **bug 修复**: 北向资金持股占比显示超100%（`_ratio*100`改为`_ratio`）
- ✅ **bug 修复**: 股东户数变化率异常（变化率超过±500%时显示为±999.99%并标记⚠️）
- ✅ **bug 修复**: EPS预测合理性检查（eps_val<=0时不计算前向PE）
- ✅ **bug 修复**: 涨停封单弱时仓位建议降级（检测到封单预警信号时仓位减半）
- ✅ **优化**: 主力净流入单位统一使用"亿元"
- ✅ **优化**: 亏损股评分强制下限（ROE<0时评分下限为20分）
- ✅ **优化**: 板块排名标题明确区分市值排名
- ✅ **优化**: 章节分隔符风格统一为`─`
- ✅ **优化**: 数字正负号格式统一
- ✅ **优化**: 评分图形条按加权分数显示
- ✅ **优化**: W底形态成交量确认统一为5日均量对比

### v8.2.0 (2026-06-18)

- ✅ **bug 修复**: 股票代码 300274 等因 lines 列表中存在 None 值导致 `join()` 报错
- ✅ **bug 修复**: `ful` 脚本综合评分显示 4211.0（百分比权重未除以100）
- ✅ **统一显示**: 删除 `ful` 脚本的额外打印逻辑，与其他脚本保持一致
- ⚡ **优化**: `get_dragon_tiger_board()` 增加 `include_seats` 参数，减少不必要的 API 请求

### v8.1.0 (2026-06-18)

- **新增统一评分接口**: `ScoreData` / `ScoreResult` / `calculate_score()`，统一管理 4 种报告类型的评分逻辑
- **新增快照功能**: `save_score_snapshot()` 保存评分结果，支持 `analyze_history.py` 进行历史对比与背离检测
- **新增配置文件**: `strategy_config.yaml` 统一配置评分权重和参数
- **新增交易日历**: `is_trading_day()` / `get_market_status()` 判断 A 股交易日和市场状态
- **新增代码清洗**: `clean_codes()` 处理股票代码格式
- **目录重命名**: `WARNING_DIR` → `SNAPSHOT_DIR`
- **bug 修复**: 银行股财报字段映射 / 财务分析除零保护 / 空字符串转换异常 / 龙虎榜日期字段过滤格式

---

## 常见问题

### Q: 提示 "could not convert string to float" 错误？

A: 某些股票的财务数据可能为空，v8.1.0 已修复此问题，请更新到最新版本。

### Q: 如何判断今天是否交易日？

A: 使用 `is_trading_day()` 函数，系统会自动识别中国节假日和调休日。

### Q: Google Drive 上传失败？

A: 检查 `credentials.json` 文件是否存在，首次使用需要浏览器授权。

### Q: 股票代码格式不正确？

A: 系统会自动清洗代码格式，支持多种输入方式：
- `600519`
- `600519茅台`
- `600519 茅台`

---

## 开发指南

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/tsy1102/a-stock-data.git
cd a-stock-data

# 安装依赖
pip install -r requirements.txt

# 安装开发工具（可选，用于静态类型检查与代码格式化）
pip install mypy black

# 运行测试
pytest tests/

# 类型检查
python -m mypy stock_common.py get_val_report.py tdx_client.py analyze_history.py gd_uploader.py --ignore-missing-imports

# 临时禁用缓存调试
STOCK_NOCACHE=1 python main.py --sht 600519
```

### 类型注解与静态检查

项目核心模块已完成类型注解（PEP 484），在 `pyproject.toml` 中集中管理 mypy 配置：

- `[tool.mypy]`：Python 3.10 目标版本，启用 `no_implicit_optional`、`warn_redundant_casts`
- `[tool.mypy.overrides]`：stock_cache / stock_common 启用更严格规则
- `[tool.black]`：代码格式化工具配置

### 常见调试问题

- **报告数据与最新行情不一致？**：可能是缓存命中了过期数据，执行 `STOCK_NOCACHE=1 python main.py ...` 临时禁用缓存再测一次；或调用 `python stock_cache.py clear --category dragon_tiger` 清理对应分类。
- **类型检查 mypy 报错？**：`third-party library stub missing` 类警告可忽略（已在 `pyproject.toml` 配置 `ignore_missing_imports=true`）。如果是自定义函数参数/返回值类型问题，请直接提交 issue。
- **Google Drive 上传失败？**：检查根目录是否有 `credentials.json`（首次使用需浏览器授权），查看 `gd_uploader.py` 的 `upload_folder_name` 是否与目标文件夹名一致。

### 提交代码

```bash
git add .
git commit -m "feat: 新功能描述"
git push origin master
```

提交信息规范：
- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `refactor:` 代码重构
- `chore:` 杂项修改

---

## 许可证

MIT License

---

## 免责声明

本项目仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。使用本工具产生的任何投资损失，作者不承担责任。

---

## 联系方式

如有问题或建议，欢迎提交 [Issue](https://github.com/tsy1102/a-stock-data/issues)。
