# V14.3.x 对话上下文压缩（2026-07-25 ~ 2026-07-26）

> **目的**：将本对话上下文压缩为可回顾的关键决策与修改记录
> **范围**：缓存机制重构（V14.3 → V14.3.1） + Top-N 数据驱动差异化（V14.3.2）
> **状态**：V14.3.2 已完成；后续脚本（sht/med/lng/ful/mak）问题待修复

---

## 一、V14.3 → V14.3.1：缓存机制重构

### 1.1 用户两个质疑

| 质疑 | 用户原文 |
|:---|:---|
| **Q1** | "脚本开始清空缓存是每次都清空还是就第一次，意义在哪里" |
| **Q2** | "缓存 K 线对于缓存文件的大小是否会造成影响，缓存的失效机制又是什么" |

### 1.2 分析结论

**Q1 答**：是的，每次都清。**但冗余**——
- 进程级缓存 `_TDX_KLINE_CACHE` 本就只活在本进程内，新进程必空
- 同进程内 22 策略共享同一份 L1 是性能优化（22 次复用 vs 22 次从 L2 重读）
- 删除入口 `.clear()` 是正确决策

**Q2 答**：单只 K 线 ~200 KB（count=800），val 一次 ~60 MB（300 只）
- 长期累积 200-500 MB（取决于报告多样性）
- 失效机制：TTL 24h，仅访问时检查过期
- 缺陷：无启动清理、无总大小限制、无 LRU、无定期任务

### 1.3 已完成修改

| 改动 | 文件 |
|:---|:---|
| 删除 P0 入口 `_TDX_KLINE_CACHE.clear()` / `_TDX_WKLINE_CACHE.clear()` 冗余代码 | [get_val_report.py](file:///d:/GitHub/test/get_val_report.py) L1525-1531 |
| 缓存失效机制增强（启动清理 + 500MB 上限 + LRU + 线程锁） | [stock_common/sc_kline_cache.py](file:///d:/GitHub/test/stock_common/sc_kline_cache.py) |
| V14.3.1 缓存测试（8 个新测试 + 24 个 V14.3 测试） | [tests/test_v143_perf.py](file:///d:/GitHub/test/tests/test_v143_perf.py) |
| CHANGELOG V14.3.1 章节 | [CHANGELOG.md](file:///d:/GitHub/test/CHANGELOG.md) L199-243 |

### 1.4 V14.3 vs V14.3.1 缓存机制对比

| 维度 | V14.3 | V14.3.1 |
|:---|:---|:---|
| 入口清空 L1 | 冗余 | ✅ 删除 |
| 启动清理过期文件 | 无 | ✅ 自动（导入时）|
| 总大小限制 | 无限增长 | ✅ 500 MB 上限 |
| LRU 淘汰 | 无 | ✅ 按 mtime 升序 |
| 线程安全 | 无锁 | ✅ `threading.Lock` |

---

## 二、V14.3.1 → V14.3.2：Top-N 数据驱动差异化

### 2.1 用户两个质疑

| 质疑 | 用户原文 |
|:---|:---|
| **Q1** | "你讲选股的范围从 1000 只减少到 300 只，我想问你选 300 只的逻辑是什么，不同的策略针对的股票类型是不一样的" |
| **Q2** | "是针对整个 val 还是针对每个策略都选不同的 300 只股票" |

### 2.2 分析结论

**Q1 答**：`300` 是 `_top_n_large`（仅用于 05/06 形态类）的全局常量，**不是针对 22 个策略的通用阈值**

**Q2 答**：**每个策略独立选股**——但有 4 个核心问题：
1. 300 没有理论依据
2. 不同策略应不同（实际几乎都按 mcap_yi 排序，忽略其他维度）
3. 排序键单一
4. 选股范围与策略目标错配

### 2.3 用户决策

**用户同意方案 A（差异化）**，但要求**先用 4 天 ZHB 数据回测验证**，再根据回测结果调整。

### 2.4 回测实施

**数据**：[cache/zhb/zhb_202607{21,22,23,24}.zip](file:///d:/GitHub/test/cache/zhb/) —— 4 个连续交易日

**脚本**：[scripts/backtest_topn.py](file:///d:/GitHub/test/scripts/backtest_topn.py)

**评估指标**：
- 选中数曲线（top_n 100/200/300/500/1000）
- 4 天 Jaccard 稳定性
- 推荐规则：能稳定选到 8+ 结果 + Jaccard ≥ 0.5 的最小 top_n

**输出**：
- [docs/backtest_v1432/README.md](file:///d:/GitHub/test/docs/backtest_v1432/README.md) —— 综合分析报告
- [docs/backtest_v1432/backtest_daily.csv](file:///d:/GitHub/test/docs/backtest_v1432/backtest_daily.csv) —— 每日明细
- [docs/backtest_v1432/backtest_summary.csv](file:///d:/GitHub/test/docs/backtest_v1432/backtest_summary.csv) —— 汇总
- [docs/backtest_v1432/backtest_recommendations.json](file:///d:/GitHub/test/docs/backtest_v1432/backtest_recommendations.json) —— 推荐表

### 2.5 V14.3.2 推荐配置（5 档差异化）

```python
_top_n_large = 300   # 形态类（05 W底/06 红三兵）— 回测推荐 300
_top_n_medium = 200  # 财务/筹码类（11/12/17）— 稳定性提升 26%
_top_n_small = 100   # 周线/核心（02/04）— 100 已饱和
_top_n_pure = 200    # 纯 ZHB 类（19/22）— 19 稳定性峰值
_top_n_fund = 1000   # 主力资金（20）— 条件严苛，需大池子
```

### 2.6 回测结果汇总

| 策略 | V14.3.1 | V14.3.2 | 选中数 | 稳定性 | 依据 |
|:---|:---:|:---:|:---:|:---:|:---|
| 02 周线多头 | 200 | **100** | 10/10 饱和 | 0.40 平稳 | 100 已饱和 |
| 04 核心打折 | 200 | **100** | 10/10 饱和 | 0.58 平稳 | 100 已饱和 |
| 05 W底形态 | 300 | 300 | 0.8→10 (300 饱和) | 0→0.28 | ✅ 验证一致 |
| 06 红三兵 | 300 | **100** | 10/10 饱和 | 0.13 | 100 已饱和 |
| 10 逆向白马 | 200 | 200 | - | - | 维持（无财务数据回测）|
| 11 筹码集中 | 200 | 200 | 10/10 饱和 | 0.63→0.79 | 稳定性提升 26% |
| 12 量价信号 | 200 | 200 | 10/10 饱和 | 0.63→0.79 | 稳定性提升 26% |
| 13 高股息 | 300 (内部) | **100** | 10/10 饱和 | 0.57→0.45 | 100 稳定性更高 |
| 17 北向Top | 150 | **200** | 10/10 饱和 | 0.63→0.79 | 稳定性提升 26% |
| 19 52周低位 | all_stocks | **200** | 10/10 饱和 | 0.37→0.77 | 200 稳定性峰值 |
| 20 主力资金 | all_stocks | **1000** | 0.5→9.5 | 0→0.15 | 条件严苛，需大池子 |
| 21 量能三连击 | all_stocks | **200** | 9.5→10 饱和 | 0.01→0.02 | 200 选满 10 |
| 22 资金动量 | all_stocks | **100** | 10/10 饱和 | 0.57 | 100 已饱和 |

### 2.7 已完成修改

| 改动 | 文件 |
|:---|:---|
| 5 档差异化 top_n 配置 | [get_val_report.py](file:///d:/GitHub/test/get_val_report.py) L1660-1703 |
| 策略 13 内部 top_n 300→100 | [get_val_report.py](file:///d:/GitHub/test/get_val_report.py) L973 |
| 更新 TestTopNConfig 验证 5 档配置 | [tests/test_v143_perf.py](file:///d:/GitHub/test/tests/test_v143_perf.py) L55-74 |
| VERSION 14.3 → 14.3.2 | [VERSION](file:///d:/GitHub/test/VERSION) |
| CHANGELOG V14.3.2 章节 | [CHANGELOG.md](file:///d:/GitHub/test/CHANGELOG.md) L246-313 |

---

## 三、用户实测发现的问题（待修复）

### 3.1 val 脚本问题（[get_val_report.py](file:///d:/GitHub/test/get_val_report.py)）

| # | 问题 | 根因 |
|:---:|:---|:---|
| 1 | 19/20/21 策略报错：`takes 1 positional argument but 2` | V14.3.2 错把 `top_n` 当作参数传给 `(stocks)` 单参数函数 |
| 2 | 命中股票数明显变少（02/04/05/06/07/08/12/13/15/16/22 都是 0）| top_n 缩到 100-200 + 网络/数据源问题 |
| 3 | val 报告未上传 GD | 用户 GD 凭据缺失，`init_gd` 静默跳过 |
| 4 | 多策略共振显示 `000039(000039): 2个策略`（无名称）| `get_em_batch_quotes` HTTP 失败，name fallback 到 code |

### 3.2 mak 脚本问题（[get_mak_report.py](file:///d:/GitHub/test/get_mak_report.py)）

| # | 问题 | 根因 |
|:---:|:---|:---|
| 5 | 3 日/10 日指数都是 N/A | `tdx_get_index_bars` 在 V14.3 P2 修复中**遗漏**，休市日卡死 |
| 6 | 全市场情绪监测看板很多数据为 0 | ZHB 字段缺失 / 旁路逻辑问题 |
| 7 | 封板时间格式错误（9 点多错误，10 点多正确）| 时间格式化 bug |
| 8 | 异动集聚板块 TOP5 / 行业轮动强度 / TOP10 板块深度分析 / 资金流验证 数据为空 | 数据抓取失败或逻辑空跑 |
| 9 | 近 3 日异动回溯中 3日/10日/20日偏离数据都为 0 | 偏离值计算逻辑问题 |

### 3.3 sht 脚本问题（[get_sht_report.py](file:///d:/GitHub/test/get_sht_report.py)）

| # | 问题 | 根因（待核查）|
|:---:|:---|:---|
| 10 | `unsupported format string passed to NoneType.__format__` 报错（002202/600143/600596）| format 字符串遇到 None 字段，未做保护 |

---

## 四、待解决的关键状态

| 状态 | 详情 |
|:---|:---|
| ✅ V14.3.1 已完成 | 缓存机制重构 + 237 测试全过 |
| ✅ V14.3.2 已完成 | 5 档差异化 top_n + 237 测试全过 |
| ⏳ V14.3.3 待实施 | 修复上述 10 个实测问题（但用户已要求"只分析不修改"）|

---

## 五、关键设计原则（用户已确认）

1. **数据驱动 > 经验拍脑袋**：top_n 必须有回测支撑
2. **进程级缓存不手动清空**：L1 跨函数复用是优化
3. **缓存有边界**：TTL + 大小限制 + LRU 清理
4. **休市日可走 ZHB 旁路**：T-1 数据已稳定，零网络请求

---

## 六、关键文件清单

### 已完成修改的文件
- [get_val_report.py](file:///d:/GitHub/test/get_val_report.py) —— V14.3 + V14.3.1 + V14.3.2
- [stock_common/sc_kline_cache.py](file:///d:/GitHub/test/stock_common/sc_kline_cache.py) —— V14.3.1 重构
- [tests/test_v143_perf.py](file:///d:/GitHub/test/tests/test_v143_perf.py) —— 32 个测试
- [scripts/backtest_topn.py](file:///d:/GitHub/test/scripts/backtest_topn.py) —— V14.3.2 回测脚本
- [VERSION](file:///d:/GitHub/test/VERSION) —— 14.3.2
- [CHANGELOG.md](file:///d:/GitHub/test/CHANGELOG.md) —— V14.3 + V14.3.1 + V14.3.2 完整章节
- [docs/backtest_v1432/README.md](file:///d:/GitHub/test/docs/backtest_v1432/README.md) —— 回测综合报告

### 已发现的待修复文件
- [get_val_report.py](file:///d:/GitHub/test/get_val_report.py) —— 19/20/21 参数 bug + name fallback bug
- [get_mak_report.py](file:///d:/GitHub/test/get_mak_report.py) —— 多个 N/A 和数据为空问题
- [get_sht_report.py](file:///d:/GitHub/test/get_sht_report.py) —— format None bug
