# 统一层 / 缓存层 同步审计（中文名统一后）

> **审计日期**: 2026-09-06（晚） · **审计对象**: 主字典 §12.8.12e 中文名统一五轮（c632be4 / a7b1889 / 8f51a26 / 9a07f48 / 2d2b672）
> **关联前次审计**: `unified_cache_sync_audit.md`（2026-09-06 早，针对 sec_type/f118 新增字段）
> **核心问题**: 主字典中文字段名大规模统一后，统一层（CanonicalStockData / 86 字段契约）与缓存层（stock_cache.py）是否需要因之重新大调整？

## 0. 结论（一句话）

**不需要任何大调整，零功能影响。** 统一层契约与缓存层全部依赖**英文键 / 英文字段名**工作，本次中文名统一**只动了字典文档里的显示用中文名**，未改任何一个英文键、字段编号或"源A字段 ≡ 源B字段"的等价映射。

## 1. 证据

### 1.1 统一层契约：字段全英文 `name`，中文仅作 `description` 注释

`stock_common/sc_schema.py`（86 字段契约）抽样——所有字段的机器标识都是英文 snake_case，运行时按 `name` 键取值；中文只在 `description` 里作人类可读注释，**不参与取值**：

```
name="price",       description="当前价格（昨收参考）"   # 键=price(英文)，中文是注释
name="open",        description="开盘价（元）"
name="high",        description="最高价（元）"
name="low",         description="最低价（元）"
name="prev_close",  description="昨收价（元）"
name="pe_ttm",      description="PE-TTM（倍）"
name="pe_dynamic",  description="动态 PE（倍）"
name="turnover_pct",description="换手率（百分点，当日即时指标）"
name="sec_type",    description="市场类型枚举（f182，主板=2/创业板=5/科创板=32/北交所=80）"
```

→ 本次字典改名未触碰 `sc_schema.py` 的任何 `name`（唯一相关改动是更早的 cea4c99 新增 `sec_type` 字段，那是对 f182 抽取、非重命名）。

### 1.2 缓存层：SQLite blob 缓存，按 `category:code:trading_date` 存整包响应，不解析字段

`core/stock_cache.py` 头部与机制确认：
- 装饰器 `@cached` 模式，key 形如 `Q:{code}:{trading_date}`（V9.3 行情缓存加交易日期隔离），**value 是整个响应体 JSON blob**。
- 全程按 category/code/date 维度做 TTL 过期 + LRU，V15.0 起 ZHB 静态字段走 RAM 字典旁路提取。
- **全仓 grep 中文字段名（当前价/最新价/封板资金/52周高/振幅%/换手率% 等）在 stock_cache.py 零命中** → 缓存层不依赖、也不解析任何中文字段名。

### 1.3 5 大脚本：全部消费英文键，命中项均为注释文本

对 `get_*_report.py` 扫描，所有命中的"当前价/最新价"等均为**段落注释里的描述性中文**，无一处是字段键引用。脚本取值走：
- 东财 push2 数字键 `f43/f162/f137/f174/f175`
- fuyao 英文键 `last_price/open_price/high_price`
- ZHB 代码变量名 `zt_seal_amount/amount/high_52w`
- 腾讯协议 `sht bid1_vol` 等

→ 与中文显示名完全正交。

### 1.4 全仓不 import 字典 md

- 全仓**不存在** `field_dict.py` 模块被 import。
- `field_dict` 仅在 `core/data_provider.py:262`、`core/tdx_client.py` 作为**注释引用**（`# 数据源：field_dict.md 第三节第 4 小节`），非代码依赖。

## 2. 等价关系与对撞结论不受影响

中文名统一只改文档层显示名：
- 未改任何英文键 / 字段编号（f43 仍是 f43、f162 仍是 f162、zt_seal_amount 仍是 zt_seal_amount）。
- 未改任何跨源等价映射（f43≡f2、f118≡ulist:f107、f162≡pe_dynamic 等全保留）。
- 今日对撞 `d49ff95`（18 采集日，方案 A）**全按英文键 / 按值互验**，结论（15 条 L1 + f118 双确认）完整保留，零受命名改动影响。

## 3. 可选小收尾（非必须，不影响运行）

代码注释 / `description` 里残留少量**旧中文称**，与新规范名不统一。它们是**注释性文字（字段释义 / docstring）**，不是字典字段名、不影响对撞（对撞按英文键）、也不影响运行时：

| 位置 | 残留旧称 | 新规范名 | 性质 |
|---|---|---|---|
| `sc_schema.py:112` `price.description` | 当前价格 | 现价 | 字段释义注释 |
| `sc_schema.py:154` `prev_close.description` | 昨收价 | 昨收盘 | 字段释义注释 |
| `sc_capital_cache.py:194,213` docstring | 当前价格（元） | 现价 | docstring |
| `strategy_config.yaml:18` 注释 | 封单资金 | 封单额 | yaml 注释 |
| `core/tdx_client.py:795` 注释 | 当前价 | 现价 | 函数注释 |
| `get_*_report.py` 注释 | 最新价/当前价 | 现价 | 段落注释 |

> **区分说明**：字典里统一的是"作为字段标识的中文名"（如 f43 的名义从"当前价"→"现价"）；代码里的"当前价格（昨收参考）"是字段释义，是不同层面。用户原始诉求（"消除同义不同名、避免对撞偏差"）针对的是前者。
> **建议**：**否**——保持最小改动。除非明确要求"全项目中文名彻底一致"，否则不碰这些注释（改了也无功能收益，反而引入 diff 噪声）。

## 4. 与历史审计对照

- 2026-09-06 早 `unified_cache_sync_audit.md`：针对 sec_type/f118 **新增字段**，结论——统一层已单独加 `sec_type`（cea4c99），缓存层不需要动。
- 本次：针对**中文名统一**（fact-layer 文档改动），结论——统一层 / 缓存层 / 5 大脚本均零功能影响，不需要调整。
- 两次结论一致：**字典的纯中文名改动永远不会传导到代码层**，因为代码层契约是英文键。

## 5. 验证

- `scripts/lint_field_names.py`：✅ 无禁用异名回归、无 PE 半角（本次编辑未引入命名回归）。
- 全仓 grep 中文字段名：统一层/缓存层/5 脚本**仅注释性命中，零字段键命中**。
