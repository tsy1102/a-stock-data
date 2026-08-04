# TDX Field Dictionary — easy_tdx 与本项目 tdx_client.py 字段对照表

> **版本**：V15.4.3 · 2026-07-31
> **来源**：[easy_tdx v1.17.10](https://github.com/handsomejustin/easy_tdx) 本地已装 + GitHub v1.20.4 README/CHANGELOG + 本项目 [tdx_client.py](../tdx_client.py) 实跑探测
> **目的**：本项目 V15 强类型 cdata 架构基础上，参考 easy_tdx 健康分引擎 + K 线空数据转移，但不替换 cdata。本文档为 V15.5 移植 health/reconnect 提供精确字段表。

---

## 0. 探测脚本与产物

| 产物 | 路径 | 说明 |
|:---|:---|:---|
| 实跑探测脚本 | [scripts/_v1543_probe_easy_tdx.py](../scripts/_v1543_probe_easy_tdx.py) | 实跑 easy_tdx 7 类接口 + inspect 读 8 个 dataclass 字段 + 写 JSON |
| 探测原始输出 | [logs/easy_tdx_field_probe.txt](../logs/easy_tdx_field_probe.txt) | JSON 完整保存所有字段定义 |

### 0.1 版本对照

| 项 | easy_tdx v1.17.10（本地已装）| easy_tdx v1.20.4（GitHub 最新）| 本项目 tdx_client.py（V15.4.2）|
|:---|:---|:---|:---|
| 发布时间 | 2026-06-XX | 2026-07-13 | 2026-07-31 |
| 服务器健康分 `_health.py` | ❌ 无 | ✅ 新增 | ❌ 无 |
| K 线空数据转移 | ❌ **已知 bug** | ✅ 新增 | ❌ 无 |
| 跨主机故障转移 `_reconnect.py` | ✅ 部分 | ✅ 完整 | ⚠️ 部分 |
| 50+ 候选 server | ✅ `get_known_hosts()` | ✅ | ⚠️ 10 个内置 |
| dataclass 强类型 | ✅ 7 个 | ✅ | ❌ dict 返回 |
| 前复权 K 线 `--adjust QFQ` | ❌（v1.17.10 无）| ✅ | ❌（V15 删 V9.6 qfq）|
| 34 个技术指标 | ❌ | ✅ MACD/KDJ/RSI/BOLL/DMI/ATR/... | ❌ |
| 缠论分析（笔/中枢/买卖点/背驰）| ❌ | ✅ | ❌ |

---

## 1. Enum 映射表

### 1.1 `Market` 枚举

| easy_tdx Market | 数值 | 本项目代码 | 说明 |
|:---|:---:|:---|:---|
| `SZ` | 0 | `1 if code.startswith("6") else 0`（tdx_get_quote_full 等）| 深圳 |
| `SH` | 1 | 同上 | 上海 |
| `BJ` | 2 | —（主项目 V15 未直接用 BJ；V3.6.0 #15 提示 43/83/87 老号段已迁 920）| 北京 |

**注意**：本项目 V15 主要用 `get_prefix()` 字符串前缀（`sh/sz/bj`），不用 Market 整数。

### 1.2 `KlineCategory` 枚举

| easy_tdx 枚举 | 数值 | 本项目 `frequency` | V3.2.5 修复后 | 说明 |
|:---|:---:|:---:|:---:|:---|
| `MIN_5` | 0 | 0 | ✅ 5 分钟 | 5 分钟 K 线 |
| `MIN_15` | 1 | 1 | ✅ 15 分钟 | 15 分钟 K 线 |
| `MIN_30` | 2 | 2 | ✅ 30 分钟 | 30 分钟 K 线 |
| `MIN_60` | 3 | 3 | ✅ 60 分钟 | 60 分钟 K 线 |
| `DAY` | 4 | 4 | ✅ 日线 | 日 K 线 |
| `WEEK` | 5 | 5 | ✅ 周线 | 周 K 线 |
| `MONTH` | 6 | 6 | ✅ 月线 | 月 K 线 |
| `MIN_1` | 7 | 8 | ✅ 1 分钟 | 1 分钟 K 线（V3.2.5 修复 category→frequency）|
| `MIN_3` | 8 | — | — | 通达信内部用，实际同 MIN_1 |
| `YEAR` | 9 | 9 | ✅ 日线（默认）| 年 K 线 / 默认 |
| `SEASON` | 10 | — | — | 季 K 线 |
| `YEAR_ALT` | 11 | — | — | 年 K 线（备用）|

**关键警示**：本项目 V15.4.2 已用 `frequency` 参数（V3.2.5 修复），对应映射见上表。

---

## 2. 核心 dataclass 字段定义

### 2.1 `SecurityBar`（K 线）

**模块**：`easy_tdx.models.bar`
**文档**：单根 K 线（适用于 1m/5m/15m/30m/60m/日/周/月/季/年）

| 字段 | 类型 | 默认 | 本项目 `tdx_get_security_bars` 字段 | 说明 |
|:---|:---|:---|:---|:---|
| `open` | `float` | 必填 | `row[col]` 数组 | 今开 |
| `close` | `float` | 必填 | `row[col]` | 今收 |
| `high` | `float` | 必填 | `row[col]` | 最高 |
| `low` | `float` | 必填 | `row[col]` | 最低 |
| `vol` | `float` | 必填 | `row[col]` | 成交量（**股**，易与本项目"手"混淆！）|
| `amount` | `float` | 必填 | `row[col]` | 成交额（元）|
| `year` | `int` | 必填 | `row[col]` | 年 |
| `month` | `int` | 必填 | `row[col]` | 月 |
| `day` | `int` | 必填 | `row[col]` | 日 |
| `hour` | `int` | 必填 | `row[col]` | 时 |
| `minute` | `int` | 必填 | `row[col]` | 分 |
| `_raw` | `bytes` | `b""` | n/a | 原始字节（field 逆向用）|
| **property** `datetime_str` | `str` | — | n/a | `"YYYY-MM-DD HH:MM"` 格式化 |

**关键差异**：
- easy_tdx `vol` 是**股**（已乘 100），本项目 `tdx_get_security_bars` 是**手**（× 100 才到股）
- easy_tdx datetime 是 5 个 int 字段，本项目是 `YYYYMMDD` 字符串

### 2.2 `SecurityQuote`（实时五档）

**模块**：`easy_tdx.models.quote`
**文档**：单只股票实时五档行情

| 字段 | 类型 | 默认 | 本项目字段 | 说明 |
|:---|:---|:---|:---|:---|
| `market` | `Market` | 必填 | n/a | 市场枚举 |
| `code` | `str` | 必填 | n/a | 6 位代码 |
| `price` | `float` | 必填 | `price` | 现价 |
| `pre_close` | `float` | 必填 | `last_close`（V15.1 改名）| 昨收 |
| `open` | `float` | 必填 | `open` | 今开 |
| `high` | `float` | 必填 | `high` | 最高 |
| `low` | `float` | 必填 | `low` | 最低 |
| `vol` | `float` | 必填 | `volume_hand`（**手**！）| 总成交量 |
| `cur_vol` | `float` | 必填 | — | 当前成交量（易主时新增）|
| `amount` | `float` | 必填 | `amount_wan`（**万元**）| 成交额 |
| `s_vol` | `float` | 必填 | — | 内盘（主动卖）|
| `b_vol` | `float` | 必填 | — | 外盘（主动买）|
| `active1` | `int` | 必填 | — | 活跃度（含义来自逆向）|
| `active2` | `int` | 必填 | — | 活跃度 |
| `bid1` ~ `bid5` | `float` × 5 | 必填 | — | 买价 1-5 档 |
| `bid_vol1` ~ `bid_vol5` | `float` × 5 | 必填 | — | 买量 1-5 档 |
| `ask1` ~ `ask5` | `float` × 5 | 必填 | — | 卖价 1-5 档 |
| `ask_vol1` ~ `ask_vol5` | `float` × 5 | 必填 | — | 卖量 1-5 档 |
| `rise_speed` | `float` | 必填 | — | 涨速（原 reversed_bytes9 / 100）|
| `limit_up` | `float \| None` | 必填 | `limit_up` | 涨停价 |
| `limit_down` | `float \| None` | 必填 | `limit_down` | 跌停价 |
| `decimal_point` | `int` | `2` | n/a | 价格小数位（2=股票，3=指数/ETF）|
| `unknown_2` | `int` | `0` | — | 指数→集合竞价成交金额/100；个股→舍入残差 |
| `unknown_3` | `int` | `0` | — | 个股→集合竞价成交金额/100；指数→负值 |
| `unknown_5` ~ `unknown_8` | `int` × 4 | `0` | — | 保留字段，恒为 0 |
| `server_time` | `str` | `""` | — | 服务器时间 `HH:MM:SS.mmm` |
| `trading_status` | `int` | `0` | — | 交易状态（`0x8020`=停牌）|
| `open_amount` | `float` | `0.0` | — | 集合竞价成交金额（元）|
| `_raw` | `bytes` | `b""` | n/a | 原始字节 |

**关键差异**：
- 本项目 `volume_hand` vs easy_tdx `vol`：**单位都是手**，名称差异
- 本项目 `amount_wan`（万元）vs easy_tdx `amount`（元）：**差 10000 倍**
- 本项目**无** `s_vol`（内盘）/ `b_vol`（外盘）/ `bid1-5`（五档）—— V15.5 移植时可考虑加
- 本项目**无** `rise_speed`（涨速）—— sht 短线报告很有用

### 2.3 `FinanceInfo`（财务信息）

**模块**：`easy_tdx.models.finance`

| 字段 | 类型 | 本项目 `tdx_get_finance_info` 字段 | 说明 |
|:---|:---|:---|:---|
| `market` | `Market` | n/a | 市场 |
| `code` | `str` | n/a | 代码 |
| `liutong_guben` | `float` | `liutong_guben`（注意拼写！）| 流通股本（**万股**）|
| `zong_guben` | `float` | `zongguben`（V15.1 修复拼写）| 总股本（万股）|
| `guojia_gu` | `float` | — | 国家股（万股）|
| `faqiren_faren_gu` | `float` | — | 发起人法人股（万股）|
| `faren_gu` | `float` | — | 法人股（万股）|
| `b_gu` | `float` | — | B 股（万股）|
| `h_gu` | `float` | — | H 股（万股）|
| `zhigong_gu` | `float` | — | 职工股（万股）|
| `province` | `int` | — | 所属省份代码 |
| `industry` | `int` | — | 所属行业代码 |
| `updated_date` | `int` | — | 财务更新日期 `YYYYMMDD` |
| `ipo_date` | `int` | — | 上市日期 `YYYYMMDD` |
| `gudong_renshu` | `float` | `gudongrenshu`（V15.1 修复拼写）| 股东人数 |
| `zong_zichan` | `float` | — | 总资产（元）|
| `liudong_zichan` | `float` | — | 流动资产（元）|
| `guding_zichan` | `float` | — | 固定资产（元）|
| `wuxing_zichan` | `float` | — | 无形资产（元）|
| `liudong_fuzhai` | `float` | — | 流动负债（元）|
| `changqi_fuzhai` | `float` | — | 长期负债（元）|
| `ziben_gongjijin` | `float` | — | 资本公积金（元）|
| `jing_zichan` | `float` | — | 净资产（元）|
| `zhuying_shouru` | `float` | — | 主营收入（元）|
| `zhuying_lirun` | `float` | — | 主营利润（元）|
| `yingshou_zhangkuan` | `float` | — | 应收账款（元）|
| `yingye_lirun` | `float` | — | 营业利润（元）|
| `touzi_shouyu` | `float` | — | 投资收益（元）|
| `jingying_xianjinliu` | `float` | — | 经营现金流（元）|
| `zong_xianjinliu` | `float` | — | 总现金流（元）|
| `cunhuo` | `float` | — | 存货（元）|
| `lirun_zonghe` | `float` | — | 利润总额（元）|
| `shuihou_lirun` | `float` | — | 税后利润（元）|
| `jing_lirun` | `float` | — | 净利润（元）|
| `weifen_lirun` | `float` | — | 未分配利润（元）|
| `meigujing_zichan` | `float` | — | 每股净资产（元，原 baoliu1）|
| `reserve2` | `float` | — | 保留字段（原 baoliu2）|
| `_raw` | `bytes` | n/a | 原始字节 |

**关键发现**：
- easy_tdx 有 **22 个资产负债表 + 利润表字段**——本项目 V15 **只用了股本类 3 个**（`zongguben` / `liutongguben` / `gudongrenshu`）
- **V15.5/15.7 移植时**可补：`zong_zichan` / `jing_zichan` / `zhuying_shouru` / `jing_lirun` 等
- 拼写差异：easy_tdx `liutong_guben` vs 本项目 `liutongguben`（无下划线，V15.1 修复）

### 2.4 `XdxrRecord`（除权除息）

**模块**：`easy_tdx.models.finance`

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `market` | `Market` | 市场 |
| `code` | `str` | 代码 |
| `year` / `month` / `day` | `int` | 日期 |
| `category` | `int` | 事件类型（见 `XDXR_CATEGORY_NAMES`）|
| `name` | `str` | 事件类型名称 |
| `fenhong` | `float \| None` | 每股分红（**协议原值按每 10 股**）|
| `peigujia` | `float \| None` | 配股价（元/股）|
| `songzhuangu` | `float \| None` | 每股送转股比例（每 10 股）|
| `peigu` | `float \| None` | 每股配股比例（每 10 股）|
| `suogu` | `float \| None` | 缩股比例（category 11/12）|
| `xingquanjia` | `float \| None` | 行权价（category 13/14）|
| `fenshu` | `float \| None` | 分数（category 13/14）|
| `panqian_liutong` | `float \| None` | 盘前流通股本（**万股**）|
| `panhou_liutong` | `float \| None` | 盘后流通股本（万股）|
| `qian_zongguben` | `float \| None` | 前总股本（万股）|
| `hou_zongguben` | `float \| None` | 后总股本（万股）|
| `_raw` | `bytes` | 原始字节 |

**XDXR_CATEGORY_NAMES**：

| category | 含义 |
|:---:|:---|
| 1 | 除权除息 |
| 2 | 送配股上市 |
| 3 | 非流通股上市 |
| 4 | 未知股本变动 |
| 5 | 股本变化 |
| 6 | 增发新股 |
| 7 | 股份回购 |
| 8 | 增发新股上市 |
| 9 | 转配股上市 |
| 10 | 可转债上市 |
| 11 | 扩缩股 |
| 12 | 非流通股缩股 |
| 13 | 送认购权证 |
| 14 | 送认沽权证 |

**关键发现**：
- 本项目 V9.6 第 828 行有 `tdx_get_qfq()` 复权函数（V15 删了）—— **V15.8 移植此函数可与 `XdxrRecord` 对接**
- `fenhong` 是**每 10 股**——除 10 后才是"每股"
- 本项目 V15 **无此 dataclass**——V15.8 复权集成需要从 XdxrRecord 拿每条除权除息事件

### 2.5 `SecurityInfo`（证券基本信息）

**模块**：`easy_tdx.models.security`

| 字段 | 类型 | 默认 | 本项目字段 | 说明 |
|:---|:---|:---|:---|:---|
| `market` | `Market` | 必填 | n/a | 市场 |
| `code` | `str` | 必填 | n/a | 6 位代码 |
| `name` | `str` | 必填 | `cdata.name` | 股票名称（**GBK 解码**）|
| `volunit` | `int` | 必填 | n/a | 成交量单位（手 = volunit 股）|
| `decimal_point` | `int` | 必填 | n/a | 价格小数位数 |
| `pre_close` | `float` | 必填 | n/a | 昨收价（通达信自定义浮点）|
| `industry_tdx` | `str` | `""` | — | **通达信行业代码**（如 `T1001`）|
| `industry_sw` | `str` | `""` | — | **申万行业代码**（如 `X500102`）|
| `_raw` | `bytes` | `b""` | n/a | 原始字节 |

**关键发现**：
- easy_tdx **额外提供 `industry_tdx` / `industry_sw` 行业码**——通过 `get_security_list_all()` 关联 `tdxhy.cfg`
- 本项目 V15.4 行业 4 级 fallback 中 push2 f128 字段用 — **没有** tdxhy.cfg 行业码字段
- **V15.5 移植时可加**：`cdata.industry_tdx` / `cdata.industry_sw` 字段

### 2.6 `FundFlow`（资金流——分类汇总）

**模块**：`easy_tdx.models.stats`

| 字段 | 类型 | 默认 | 本项目字段 | 说明 |
|:---|:---|:---|:---|:---|
| `super_in` | `float` | 必填 | — | 超大单流入（**>100 万**）|
| `large_in` | `float` | 必填 | — | 大单流入（**>20 万** 且 ≤100 万）|
| `medium_in` | `float` | 必填 | — | 中单流入（**>4 万** 且 ≤20 万）|
| `small_in` | `float` | 必填 | — | 小单流入（≤4 万）|
| `super_out` | `float` | 必填 | — | 超大单流出 |
| `large_out` | `float` | 必填 | — | 大单流出 |
| `medium_out` | `float` | 必填 | — | 中单流出 |
| `small_out` | `float` | 必填 | — | 小单流出 |
| **property** `main_net_inflow` | `float` | n/a | `main_net`（cdata 字段）| **(超大 + 大) - (超大 + 大)流出** |
| **property** `total_net_inflow` | `float` | n/a | `total_net` | 全单净流入 |

**关键发现**：
- easy_tdx 资金流**分类阈值与本项目可能不同**——本项目从 `push2his.eastmoney.com` 拿，可能阈值不一样
- `main_net_inflow` property 计算：**超大单 + 大单 = 主力**——与本项目主力定义一致

### 2.7 `MarketStat`（市场涨跌概况）

**模块**：`easy_tdx.models.stats`

| 字段 | 类型 | 默认 | 本项目 mak 报告 | 说明 |
|:---|:---|:---|:---|:---|
| `up_count` | `int` | 必填 | — | 上涨家数 |
| `down_count` | `int` | 必填 | — | 下跌家数 |
| `neutral_count` | `int` | 必填 | — | 平盘家数 |
| `suspended_count` | `int` | 必填 | — | 停牌/未参与家数（推算）|
| `total_count` | `int` | 必填 | — | 总计 |
| `total_amount` | `float` | 必填 | — | 总成交额 |
| `total_volume` | `float` | 必填 | — | 总成交量 |
| `total_market_cap` | `float` | 必填 | — | 总市值（亿元，来自 880001 收盘价 ÷ 100 = 万亿）|
| `limit_up_count` | `int` | 必填 | — | 涨停家数（来自 880006 close）|
| `limit_down_count` | `int` | 必填 | — | 跌停家数（来自 880006 open）|

**关键发现**：
- 字段名与本项目 mak 报告**完全对应**——mak 报告"市场概况"段直接可用
- **V15.5/15.7 移植**：从东财 push2 880005/880001/880006 拿这些数据
- ⚠️ `total_market_cap` 单位"亿元 ÷ 100 = 万亿"——**易错**

### 2.8 `HistoricalFundFlow`（历史日线资金流）

**模块**：`easy_tdx.models.stats`

| 字段 | 类型 | 默认 | 本项目 `tdx_get_history_fund_flow` | 说明 |
|:---|:---|:---|:---|:---|
| `year` / `month` / `day` | `int` | 必填 | `date` (YYYYMMDD) | 日期 |
| `super_in` / `super_out` | `float` | 必填 | `super_net` (单位：元) | 超大单流入/流出 |
| `large_in` / `large_out` | `float` | 必填 | `large_net` | 大单 |
| `medium_in` / `medium_out` | `float` | 必填 | `mid_net` | 中单 |
| `small_in` / `small_out` | `float` | 必填 | `small_net` | 小单 |
| **property** `main_net_inflow` | `float` | n/a | `main_net` | 主力净流入 |

**关键发现**：
- 本项目 V15 `tdx_get_history_fund_flow` 与 easy_tdx `HistoricalFundFlow` **字段对应完全一致**
- V15.5 移植 easy_tdx 是**字段直接对应**——无需复杂 adapter

---

## 3. 健康分 + 故障转移模块（V15.5 移植重点）

### 3.1 `easy_tdx._health`（v1.20.4 新增 · 本项目 V15.4.3 实测不存在）

**实跑结果**（v1.17.10）：
```
error: v1.17.10 无 _health.py（v1.20.4 新增）: cannot import name '_health'
```

**v1.20.4 字段与常量**（从 GitHub 源码抓取）：

```python
# 模块级常量
_FAILURE_DECAY: float = 0.5        # 失败乘性衰减
_SUCCESS_RECOVER: float = 0.2      # 成功加性恢复（上限 1.0）
_COOLDOWN_FAIL_THRESHOLD: int = 3 # 进入冷却的连续失败次数
_COOLDOWN_SEC: float = 120.0      # 冷却时长（秒）
_SCORE_FLOOR: float = 1e-3         # score 下限

# 函数
def record_failure(host: str) -> float  # 失败降权
def record_success(host: str) -> None    # 成功恢复
def reset_health() -> None               # 清空记录（测试用）
def is_in_cooldown(host: str) -> bool    # 是否冷却中
def get_score(host: str) -> float        # 当前 score
def rank_by_health(ranked_hosts) -> list # 按 score/latency 重排
```

**数据结构**：
```python
@dataclass
class _HostHealth:
    score: float = 1.0
    consecutive_failures: int = 0
    cooldown_until: float = 0.0  # monotonic 时间戳
```

**v1.20.4 新增 8 个 client 统一健康分联动**：A股/MAC/EX/MAC-EX × sync/async。

### 3.2 `easy_tdx._reconnect`（v1.17.10 实测存在）

**实跑结果**（v1.17.10）：`_reconnect_constants = {}`（v1.17.10 可能未导出大写常量）。

**v1.20.4 常量**（从 GitHub 源码抓取）：

```python
_RETRY_DELAYS: tuple[float, ...] = (0.1, 0.5, 1.0, 2.0)  # 4 次指数退避
_FAILOVER_PING_THROTTLE_SEC: float = 30.0  # 跨主机测速节流
_WORKING_HOST_MAX_ATTEMPTS = 5             # 空数据转移最多试探几台
```

**关键函数**：
```python
def select_best_host_sync(hosts, ping_fn, save_fn, port, timeout, current_host) -> str | None
async def select_best_host_async(...) -> str | None
def find_working_host_sync(ranked_hosts, try_fn, save_fn, current_host, max_attempts=5) -> str | None
async def find_working_host_async(...) -> str | None
class AsyncHeartbeatMixin: ...
```

**v1.20.4 主要修复**：
- `get_index_bars` / `get_security_bars`（sync+async）空结果时**自动逐台换台**——本项目 V15.4.1 sht 4 指数卡死的根治方案
- 此前空 DataFrame 直接返回，是"指数 K 线响应被截断"的根因

### 3.3 V15.5 移植计划

| 项 | 来源 | V15.5 任务 |
|:---|:---|:---:|
| `_health.py` 核心 | v1.20.4 `_health.py` | 15.144 |
| `_reconnect.py` 核心（去 easy_tdx 特有的 4 个 client 心跳 Mixin）| v1.20.4 `_reconnect.py` | 15.145 |
| 50+ 候选 server | `easy_tdx.config.get_known_hosts()` | 15.146 |
| 与本项目 `_get_tdx_client()` 集成 | tdx_client.py L194 | 15.147 |
| K 线 / 指数 K 线 空数据转移 | tdx_client.py L419 + L639 | 15.148 + 15.149 |
| 跨进程健康分（file_lock）| sc_network.py 的 file_lock | 15.150 |

---

## 4. 接口字段对照总表

### 4.1 行情层

| 接口 | easy_tdx v1.20.4 | 本项目 V15.4.2 | V15.5 移植 |
|:---|:---|:---|:---:|
| **实时五档** | `get_security_quotes(markets, codes) -> List[SecurityQuote]` | `tdx_get_quote_full(code)` (部分字段) | ⏳ |
| **K 线（日/周/月）** | `get_security_bars(market, code, kline, start, count, adjust=None)` | `tdx_get_security_bars(code, count, frequency=9)` | ⏳ V15.8 |
| **K 线（1/5/15/30/60 分）** | `get_security_bars(..., kline=MIN_5)` | `tdx_get_security_bars(code, count, frequency=0/2/8)` | ⏳ V15.8 |
| **指数 K 线** | `get_index_bars(market, code, kline, start, count)` | `tdx_get_index_quote(idx_code)` | ✅ 15.149 |
| **证券列表** | `get_security_list(market, start)` | n/a | ⏳ V15.7 |
| **市场统计** | `get_market_stat()` | n/a（V15 mak 报告间接拿）| ⏳ V15.7 |

### 4.2 财务/股本层

| 接口 | easy_tdx | 本项目 | V15.5/15.8 移植 |
|:---|:---|:---|:---:|
| **财务信息（最新）** | `get_finance_info(market, code) -> FinanceInfo` | `tdx_get_finance_info(code)`（3 字段）| ⏳ V15.7 |
| **除权除息** | `get_xdxr_info(market, code) -> List[XdxrRecord]` | ❌ 无（V9.6 删了）| ⏳ V15.8 |
| **前复权 K 线** | `get_security_bars(..., adjust="QFQ")` | ❌ 无（V15 删 V9.6）| ⏳ V15.8 |
| **公司信息** | `get_company_info_category/content` | ✅ mootdx F10（V14.2 已集成）| n/a |

### 4.3 板块/资金层

| 接口 | easy_tdx | 本项目 | V15.5/15.7 移植 |
|:---|:---|:---|:---:|
| **板块列表** | `get_block_list()` | `tdx_get_board_list(board_type)` | ✅ 字段对齐 |
| **板块成员** | `get_block_members(name)` | `tdx_get_board_members(board_code)` | ✅ 字段对齐 |
| **个股资金流（分钟）** | n/a（用 `get_transaction_data` 计算）| `tdx_get_fund_flow(code)` | ⏳ V15.7 |
| **历史资金流（120 日）** | n/a | `tdx_get_history_fund_flow(code, days=120)` | ⏳ V15.7 |
| **分笔成交** | `get_history_transaction_data(market, code, date)` | n/a | ⏳ V15.7 |

### 4.4 增强层（V15.7+ 可选）

| 接口 | easy_tdx v1.20.4 | 本项目 V15.4.2 | V15.x 移植 |
|:---|:---|:---|:---:|
| **打板涨停池** | ❌ 无（V3.3.0 起才有，**v1.20.4 仍未引入**）| ❌ 无 | ⏳ V15.6 |
| **34 技术指标** | ✅ `indicator MACD/RSI/BOLL...` | ❌ 无 | ⏳ V15.9 |
| **缠论分析** | ✅ `chanlun` | ❌ 无 | ⏳ V15.9 |
| **ETF 期权** | ❌ 无 | ❌ 无 | 不做 |

---

## 5. V15.5/15.7/15.8 移植优先级与工作量

### 5.1 P0（V15.5 — 必做）

| 任务 | 字段对应 | 工作量 |
|:---|:---|:---:|
| 升级 easy_tdx 1.17.10→1.20.4+ | n/a | 1h |
| 移植 `_health.py` | §3.1 完整字段表 | 2h |
| 移植 `_reconnect.py`（去 easy_tdx 特性）| §3.2 + §3.3 | 2h |
| 50+ 候选 server 注入 | `_TDX_SERVERS` 扩 | 1h |
| `_get_tdx_client()` 集成 health | 集成 record_success/failure | 1h |
| `tdx_get_security_bars` 空数据转移 | 集成 find_working_host | 1h |
| `tdx_get_index_quote` 空数据转移 | **根治 sht 4 指数卡死** | 1h |
| 跨进程健康分 | file_lock 持久化 | 2h |
| 单元测试 | 15-26 测试 | 2h |
| 实跑验证 | `python main.py --all 000100` | 1h |

**P0 总计**：14h（2 个工作日）。

### 5.2 P1（V15.7 — 推荐）

| 任务 | 字段对应 | 工作量 |
|:---|:---|:---:|
| `tdx_get_finance_info` 扩展字段 | 补 22 个资产负债表字段 | 2h |
| `MarketStat` 集成 | mak 报告"市场概况"段直接对接 | 2h |
| `FundFlow` 字段统一 | 4 档分类（超大/大/中/小）| 2h |
| `SecurityInfo.industry_tdx`/`industry_sw` 接入 | cdata 增字段 | 2h |

**P1 总计**：8h（1 个工作日）。

### 5.3 P2（V15.8 — 推荐）

| 任务 | 字段对应 | 工作量 |
|:---|:---|:---:|
| `tdx_get_qfq` 前复权 K 线 | 用 `XdxrRecord` 算 | 3h |
| K 线换手率 / 量价分布 | 用 `SecurityBar` + 计算 | 2h |

**P2 总计**：5h。

### 5.4 P3（V15.9 — 可选）

| 任务 | 字段对应 | 工作量 |
|:---|:---|:---:|
| 34 个技术指标（MACD/KDJ/RSI/BOLL/DMI/ATR/...）| 用 `SecurityBar` 计算 | 6h |
| 缠论分析（笔/中枢/买卖点/背驰）| 复用 SecurityBar | 4h |

**P3 总计**：10h（不推荐）。

---

## 6. 关键差异与注意事项

### 6.1 单位差异

| 项 | easy_tdx | 本项目 V15 | 差异 |
|:---|:---|:---|:---|
| **成交量** | `vol`（股）| `volume_hand`（手）| **× 100** |
| **成交额** | `amount`（元）| `amount_wan`（万元）| **÷ 10000** |
| **股本** | `liutong_guben`（万股）| `liutongguben`（万股）| 一致 |
| **分红** | `fenhong`（每 10 股）| — | **÷ 10** |

### 6.2 字段命名差异

| easy_tdx | 本项目 V15 |
|:---|:---|
| `pre_close` | `last_close`（V15.1 改名）|
| `decimal_point` | n/a（V15 用 4 级 fallback 处理）|
| `industry_tdx` / `industry_sw` | `industry`（V15.4 push2 f128 优先）|
| `rise_speed` | n/a |
| `s_vol` / `b_vol`（内盘/外盘）| n/a |
| `bid1-5` / `ask1-5`（五档）| n/a |
| `cur_vol` / `trading_status` / `open_amount` | n/a |
| `category`（XdxrRecord）| n/a（V15 删 V9.6 qfq）|

### 6.3 时间格式差异

| 项 | easy_tdx | 本项目 V15 |
|:---|:---|:---|
| K 线日期 | `year`/`month`/`day` 三个 int | `YYYYMMDD` 字符串 |
| 服务器时间 | `server_time`（HH:MM:SS.mmm）| n/a |

### 6.4 编码差异

| 项 | easy_tdx | 本项目 V15 |
|:---|:---|:---|
| 股票名称 | `name`（**GBK 解码**）| `name`（UTF-8）|
| 异常处理 | `TdxConnectionError` / `TdxDecodeError` | `Exception` 通用 |

---

## 7. 已知 easy_tdx v1.17.10 Bug（V15.5 升级后解决）

### 7.1 实测 Bug

| Bug | 错误信息 | 影响 | v1.20.4 状态 |
|:---|:---|:---|:---:|
| **K 线空 body 抛异常** | `TdxDecodeError: day datetime: 数据不足，需要 4 字节，偏移 2，实际剩余 0 字节` | SH600519 等正常股票偶发 K 线空 body 仍 500 | ✅ v1.19.3 修复 |
| **K 线分钟空 body** | `TdxDecodeError: minute datetime: 数据不足，需要 4 字节，偏移 2，实际剩余 0 字节` | 同上 | ✅ v1.19.3 修复 |
| **指数 K 线空 body** | `TdxDecodeError: day datetime: 数据不足` | 指数 K 线空数据 | ✅ v1.20.4 修复（空数据转移）|

### 7.2 API 签名差异（v1.17.10 → v1.20.4）

| 接口 | v1.17.10 签名 | v1.20.4 签名 |
|:---|:---|:---|
| `get_security_quotes` | `(markets, codes)` | `(markets, codes)` 兼容 |
| `get_history_transaction_data` | `(market, code, date)` | `(market, code, date, start)` 新增 start |
| `get_security_list` | 返回 DataFrame | 返回 DataFrame 兼容 |
| `get_block_list` | 在 `TdxClient` 上 | 在 `MacClient` 子模块 |

### 7.3 升级建议

```
# 修复 pip cache 后升级
python -m pip cache purge
python -m pip install --upgrade easy-tdx==1.20.4

# 验证
python -c "import easy_tdx; print(easy_tdx.__file__)"
```

---

## 8. 总结：本字典与 cdata 强类型的关系

### 8.1 本项目 V15 cdata 已有字段 vs easy_tdx 字段覆盖

| cdata 字段 | easy_tdx 来源 | 备注 |
|:---|:---|:---|
| `price` | `SecurityQuote.price` | ✅ |
| `open` / `high` / `low` | `SecurityQuote.{open,high,low}` | ✅ |
| `last_close` | `SecurityQuote.pre_close` | V15 改名 |
| `change_pct` | 计算 (`price / pre_close - 1`) | ❌ easy_tdx 无 |
| `amount_wan` | `SecurityQuote.amount / 10000` | 单位转换 |
| `volume_hand` | `SecurityQuote.vol` | 一致（都是手）|
| `mcap_yi` | `price * liutong_guben / 10000` | ❌ easy_tdx 无 |
| `industry` | `SecurityInfo.industry_tdx`（待 V15.5 移植）| 🟠 |
| `pe_ttm` / `pb` | ❌ easy_tdx 无 | 走腾讯/东财 |
| `industry_code` | ❌ easy_tdx 无 | 走 ZHB |

### 8.2 移植后能补的 cdata 字段

| cdata 新增字段 | easy_tdx 来源 | 优先级 |
|:---|:---|:---:|
| `rise_speed` | `SecurityQuote.rise_speed` | 🟠 P1 |
| `s_vol` / `b_vol` | `SecurityQuote.{s_vol,b_vol}` | 🟡 P2 |
| `trading_status` | `SecurityQuote.trading_status` | 🟡 P2 |
| `industry_tdx` | `SecurityInfo.industry_tdx` | 🟠 P1 |
| `industry_sw` | `SecurityInfo.industry_sw` | 🟡 P2 |
| `pre_close` | `SecurityQuote.pre_close` | ❌ V15.1 已用 `last_close` |

---

## 9. 附录：测试用例

### 9.1 单元测试模板（V15.5 用）

```python
# tests/test_tdx_health.py
import time
from stock_common.tdx_health import (
    record_failure, record_success, reset_health,
    is_in_cooldown, get_score, rank_by_health,
    _FAILURE_DECAY, _SUCCESS_RECOVER,
    _COOLDOWN_FAIL_THRESHOLD, _COOLDOWN_SEC,
)

def test_record_failure_decay():
    reset_health()
    s0 = get_score("test1")
    assert s0 == 1.0
    s1 = record_failure("test1")
    assert s1 == _FAILURE_DECAY  # 0.5
    s2 = record_failure("test1")
    assert s2 == _FAILURE_DECAY ** 2  # 0.25

def test_record_success_recover():
    reset_health()
    record_failure("test2")
    record_failure("test2")
    record_success("test2")
    s = get_score("test2")
    assert abs(s - (0.25 + _SUCCESS_RECOVER)) < 0.001  # 0.45

def test_cooldown_after_3_failures():
    reset_health()
    for _ in range(_COOLDOWN_FAIL_THRESHOLD):
        record_failure("test3")
    assert is_in_cooldown("test3") == True

def test_cooldown_expires():
    reset_health()
    for _ in range(_COOLDOWN_FAIL_THRESHOLD):
        record_failure("test4")
    assert is_in_cooldown("test4") == True
    time.sleep(_COOLDOWN_SEC + 1)
    assert is_in_cooldown("test4") == False

def test_rank_by_health():
    reset_health()
    ranked = [("a", 0.1), ("b", 0.2), ("c", 0.3)]
    # 全健康 → 保持原序
    out = rank_by_health(ranked)
    assert [h for h, _ in out] == ["a", "b", "c"]
    # a 失败 3 次进冷却 → 剔除 a
    for _ in range(3):
        record_failure("a")
    out = rank_by_health(ranked)
    assert "a" not in [h for h, _ in out]
```

### 9.2 集成测试

```python
# tests/test_tdx_reconnect.py
def test_security_bars_empty_data_failover(monkeypatch):
    """K 线返空 DataFrame 应触发换台"""
    # mock 当前 server 返空，下一台返真实数据
    # 验证 report host 被切换 + 新 host 被持久化
    ...

def test_index_quote_empty_data_failover(monkeypatch):
    """指数 K 线返空 DataFrame 应触发换台（V15.4.1 sht 卡死场景）"""
    ...
```

---

## 10. 参考资料

| 资料 | URL | 备注 |
|:---|:---|:---|
| easy_tdx 主页 | https://github.com/handsomejustin/easy_tdx | v1.20.4 |
| easy_tdx CHANGELOG | https://github.com/handsomejustin/easy_tdx/blob/main/CHANGELOG.md | V3.6.0 8 月最新 |
| easy_tdx SKILL.md | [skills/a-stock-data/SKILL.md](../skills/a-stock-data/SKILL.md) | 简化版 SKILL |
| a-stock-data V3.6.0 借鉴 | [a-stock-data v3.6.0 SKILL.md](file:///D:/GitHub/test/skills/a-stock-data/SKILL.md) | 哲学借鉴 |
| 本项目 tdx_client.py | [tdx_client.py](../tdx_client.py) | V15.4.2 |
| V15.4.3 实跑日志 | [logs/easy_tdx_field_probe.txt](../logs/easy_tdx_field_probe.txt) | JSON |
| V15.5 路线图 | [docs/roadmap.md](roadmap.md) V15.5 章节 | 10 个移植任务 |
| a-stock-data V3.2.4 `tdx_client()` helper | https://github.com/simonlin1212/a-stock-data/blob/main/SKILL.md#mootdx-客户端必读规避-011x-bestip-bug | 互补哲学 |
| a-stock-data V3.2.5 HTTPAdapter Retry | 同上 SKILL.md §1.1 | Retry 配置 |
