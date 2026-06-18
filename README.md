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
├── main.py              # 主入口程序
├── stock_common.py      # 核心数据获取函数库
├── stock_calendar.py    # 交易日历模块
├── gd_uploader.py       # Google Drive上传模块
├── tdx_client.py        # 通达信数据客户端
├── get_sht_report.py    # 短线报告生成
├── get_med_report.py    # 中线报告生成
├── get_lng_report.py    # 长线报告生成
├── get_ful_report.py    # 完整报告生成
├── get_val_report.py    # 估值报告生成
├── get_mak_report.py    # 市场热点报告生成
├── requirements.txt     # 依赖列表
├── CHANGELOG.md         # 版本变更记录
└── reports/             # 报告输出目录
```

---

## 配置文件

### requirements.txt

```
requests>=2.28.0
aiohttp>=3.8.0
pandas>=1.5.0
numpy>=1.23.0
mootdx>=0.5.0
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

详见 [CHANGELOG.md](CHANGELOG.md)

### v8.1.0 (2026-06-18)

- 新增交易日历判断功能
- 新增市场状态判断（含午休时段）
- 新增股票代码清洗功能
- 修复银行股财报字段映射问题
- 添加财务分析除零保护
- 修复空字符串转换异常

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

# 运行测试
pytest tests/
```

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
