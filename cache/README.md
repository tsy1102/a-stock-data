# cache/ — 运行时缓存目录

> 本目录为**运行时缓存**，全部由程序自动生成，已被 `.gitignore:35` 的 `cache/*` 规则忽略，**不入库、可随时整体删除重建**。`cache/README.md` 例外受版本控制（与 `scratch/README.md` 同例，不被缓存清理删除）。

## 定位（与 scratch/、__pycache__ 的区别）

| 目录 | 定位 | 内容 | 入库 |
|:---|:---|:---|:---|
| `cache/` | 运行时业务缓存 | K线 / 行业映射 / ZHB 行情 / 统一缓存 DB | 否（除 README） |
| `scratch/` | 一次性调研沙盒 | 实验脚本（用完即弃） | 否（除 README） |
| `__pycache__/` / `.pytest_cache/` / `.mypy_cache/` | 解释器 / 测试 / 类型缓存 | 字节码 / 收集结果 | 否 |

## 目录结构与内容（2026-09-12 核查）

```
cache/
├── em_industry_map_l2.json         # 东财行业映射 L2（生成自 stock_common/sc_datasource/_industry.py）
├── em_industry_members_l2.json     # 东财行业成分 L2
├── stock_cache.db                  # 统一缓存层 SQLite 库（≈97MB，跨数据源共享缓存中枢）
├── kline/                          # K线 / 筹码分布缓存（pickle，sc_kline_cache.py 生成）
│   ├── D_<code>_<period>_v2.pkl    # 日线类 K线（883 个，含 5/30/60/240 等多周期）
│   ├── W_<code>_<period>_v2.pkl    # 周线 K线（282 个）
│   └── CYQ_<code>_<period>_v2.pkl  # 筹码分布 CYQ（35 个）
├── zhb/                            # ZHB 行情原始快照 + 同步状态
│   ├── zhb_YYYYMMDD.zip            # 日级 ZHB 行情快照（31 个，2026-07-31 ~ 2026-09-11）
│   ├── .last_download              # 上次下载日期标记（增量同步锚点）
│   ├── .sync_state.json            # 同步状态机状态（隐藏元数据）
│   └── sync.log                    # 同步日志
└── zhb_parsed/                     # ZHB 解析产物（二进制，供下游读取）
    ├── tdxstat_YYYYMMDD_v4.bin     # 每日 ZHB 统计（14 个，2026-08-25 ~ 2026-09-11）
    └── tdxstat2_YYYYMMDD_v4.bin    # 每日 ZHB 统计2（14 个，同期）
```

## 各缓存类型说明

| 缓存文件 / 目录 | 生成模块 | 用途 | 可删 |
|:---|:---|:---|:---|
| `em_industry_map_l2.json`<br>`em_industry_members_l2.json` | `stock_common/sc_datasource/_industry.py` | 东财行业映射与成分，减少重复抓取 | 可（下次运行重建） |
| `stock_cache.db` | 统一缓存层（`sc_kline_cache.py` / `data_provider` 等） | 跨源字段 / 单位换算 / 版本化缓存中枢 | 可（代价最大，重建耗时） |
| `kline/*.pkl` | `stock_common/sc_kline_cache.py` | 个股多周期 K线 + 筹码分布，离线回测 / 技术指标输入 | 可（按 code 惰性重建） |
| `zhb/zhb_YYYYMMDD.zip` | ZHB 行情同步模块 | 原始日级行情快照，支持断点续传与历史回溯 | 可（归档 / 可重下） |
| `zhb/.last_download`<br>`zhb/.sync_state.json`<br>`zhb/sync.log` | ZHB 行情同步模块 | 增量同步状态与日志 | 可（同步会重建） |
| `zhb_parsed/*.bin` | ZHB 解析模块 | 解析后的统计二进制，供报表 / 席位分析读取 | 可（由 zip 重解析） |

> 文件规模（2026-09-12）：共 **1265** 个文件 —— pkl 1200（D_ 883 / W_ 282 / CYQ_ 35）、zip 31、bin 28、json 3、db 1、log 1、隐藏同步状态 1。全部为合法缓存产物。

## 保留与清理策略

- **整体可删**：`cache/` 全部为可重建产物，可 `rm -rf cache/kline cache/zhb cache/zhb_parsed cache/*.json cache/stock_cache.db` 后由程序按需重建；无专用清理脚本，手工删除即可。
- **不要手工编辑**：pkl / zip / bin 为二进制序列化，手工改动会导致反序列化失败或数据污染。
- **保留 README**：`cache/README.md` 受 `!cache/README.md` 例外保护，缓存清理时不应删除本文件。
- **DB 优先原则**：`stock_cache.db` 是统一缓存中枢（≈97MB，体积最大）；局部回收空间时优先删 `kline/` 与 `zhb/`，`stock_cache.db` 留待最后。

## 历史核查记录

- **2026-09-12**：应"排查 cache 下有无非缓存无用文件"要求，全量核查 `cache/`（共 1265 个文件）。
  - 结论：**未发现任何非缓存类垃圾文件**。按扩展名：pkl 1200 / zip 31 / bin 28 / json 3 / db 1 / log 1 / 隐藏状态文件 1。
  - 专项排查：零字节文件 0、临时残留（`.tmp/.bak/.part/.swp`）0、脚本 / 文档残留（`.py/.md/.txt/.csv`）0。
  - 所有文件均为合法缓存产物（K线 / 行业映射 / ZHB 快照与解析 / 统一缓存 DB / 同步状态），来源可溯至 `stock_common/sc_kline_cache.py` 与 `sc_datasource/_industry.py` 等。
  - 同日补充本 `cache/README.md`（原目录缺失说明文档），并为 `.gitignore` 的 `cache/` 规则加 `!cache/README.md` 例外，使其与 `scratch/README.md` 同例受版本控制。

> 数据来源：通达信；本目录为工程性运行时产物，以上说明不构成投资建议。
