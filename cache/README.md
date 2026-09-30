# `cache/` 运行时数据

本目录存放程序生成或同步的本地数据，默认由 `.gitignore` 排除；本说明文件纳入版本控制。目录内容并非都能从网络无损重建，尤其历史 ZHB 快照和本地行情文件，清理前应确认是否仍需要离线回溯。

## 内容

| 内容 | 主要用途 | 生成或维护位置 |
|:---|:---|:---|
| `stock_cache.db` | SQLite 统一缓存，包括跨源字段与版本化结果 | `core/stock_cache.py` |
| `kline/` | K 线和筹码分布文件，供报告、指标及回测使用 | `stock_common/sc_kline_cache.py` |
| `zhb/` | 原始 ZHB 压缩包与增量同步状态 | `core/zhb_client.py` |
| `zhb_parsed/` | ZHB 解析后的二进制快照 | ZHB 解析模块 |
| `em_industry_*.json` | 东财行业与成分映射缓存 | `stock_common/sc_datasource/_industry.py` |

## 清理

- `scripts/clean_cache.py` 管理统一 SQLite 缓存；使用前先查看 `--help`，确认清理类别和确认参数。
- K 线、ZHB 原始压缩包与解析产物分别存放。只清理明确的目标目录或文件，不要整体删除 `cache/`；历史 ZHB 包删除后不保证可重新下载。
- 不要手工编辑 `.db`、`.pkl`、`.zip` 或 `.bin` 文件。
- `README.md` 是唯一需要长期保留在版本控制中的目录说明。
