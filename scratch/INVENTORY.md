# scratch/ 调研沙盒目录清单

> V15.3 文档化: 此目录是用户的 A股数据调研沙盒，**不参与生产代码运行**。
> `.gitignore` 已 ignore `scratch/*`（除本 INVENTORY.md），不会污染主仓库。

## 13 个子目录

| 目录 | 用途 | 是否保留 | 备注 |
|:---|:---|:---:|:---|
| `eastmoney/` | 东财 HTTP API 探索代码 | ✅ | 早期调研，参考用 |
| `eastmoney-monthly/` | 东财月度数据接口 | ⚠️ | 内容少，可能过时 |
| `EastMoney_Crawler/` | 东财爬虫（参考实现） | ✅ | 第三方爬虫参考 |
| `eastmoney_spider/` | 东财 spider 工具 | ⚠️ | 与 EastMoney_Crawler 类似，可合并 |
| `finshare/` | 财务分享脚本 | ⚠️ | 偶尔用 |
| `investool/` | 投资工具集合 | ⚠️ | 偶尔用 |
| `stock-sdk/` | stock-sdk 参考实现 | ✅ | 容错层/限流设计参考 |
| `tdx/` | TDX 协议探索 | ✅ | 协议实现参考 |
| `tickflow/` | 量化交易平台参考 | ✅ | UI 参考 |
| `TradingAgents-astock/` | AI 交易代理（含前端） | ✅ | 决策框架参考 |
| `UZI-Skill/` | 投资分析 skill | ✅ | 提示词参考 |
| `zhb_20260713/` | ZHB 数据集快照 | ✅ | 调试用 |
| `__pycache__/` | Python 缓存 | 🗑️ | 可安全删除 |

## 4 个独立 .py

| 文件 | 用途 |
|:---|:---|
| `get_real_data.py` | 拉真实数据调试 |
| `parse_zhb.py` | 解析 ZHB 数据集 |
| `query_tipinfo.py` | 查询个股提示信息 |
| `sample_all.py` | 全市场采样 |
| `search_mcap.py` | 按市值搜索 |

## 决策建议

- **🟢 保留**：stock-sdk / tdx / tickflow / TradingAgents-astock / UZI-Skill / EastMoney_Crawler / zhb_20260713 / eastmoney（重要的参考实现）
- **🟡 可合并/裁剪**：eastmoney-monthly / eastmoney_spider（与 eastmoney 重复）/ finshare / investool（偶尔用）
- **🗑️ 可删除**：__pycache__/（git ignore 已排除，磁盘上可清理）

## 何时可以删除整个 scratch/

如果未来所有调研代码都已迁移到主仓库对应模块，scratch/ 可整体删除。
目前保留作为快速参考。
