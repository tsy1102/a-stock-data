# 统一层 × 缓存层 调整 A–E 实施报告（2026-09-10）

> 数据来源：腾讯行情 / 东方财富 push2·ulist / 同花顺 fuyao / 通达信 easy_tdx（运行时源）
> 依据：审计报告 `docs/field_verification/20260910_unified_cache_audit.md`（2026-09-10）
> 结论性质：技术诊断与代码实施，不构成投资建议

---

## 一、实施总览

按用户确认，落实审计报告五项调整 **A / B / C / D / E**，并在 `field_dict.md`「统一层接线」列对应行追加「✅2026-09-10 已接统一层」标注，闭环「字典超前、代码滞后」根因。

| 调整 | 内容 | 文件 |
|---|------|------|
| A | 均价源 `腾讯[85]→[51]` | `tdx_client.py` / `sc_schema.py` / `_quotes.py` / `data_provider.py` |
| B | 委差源 `腾讯[86]→[50]` + push2 `f192` 兜底 | 同上 + `_quotes.py`(`_em_quote_full_impl`) |
| C | 实装 `entrust_ratio`/`bid2`/`ask2` 三字段，使字典 canonical 成真 | `sc_schema.py` / `tdx_client.py` / `_quotes.py` / `data_provider.py` |
| D | 内盘/外盘合成：TDX 实时(权威) > push2 `f161`/`f49` > 腾讯[8]/[7] | `tdx_client.py` / `_quotes.py` / `data_provider.py` |
| E | 缓存契约版本号 `CACHE_CONTRACT_VERSION="v1"` 嵌入 key 前缀 | `core/stock_cache.py` |

---

## 二、调整 A：均价源 [85] → [51]

- `core/tdx_client.py` `_TENCENT_FIELD_INDEX`：`"avg_price": 85` → `51`。
- `stock_common/sc_datasource/_quotes.py` `get_tencent_quote`：注释更新（[85] 已撤销，[51] 为强锚）；取数走既有 `_tv("avg_price")`（越界安全），自动生效。
- `stock_common/sc_schema.py` `avg_price` 字段注释：`腾讯[51] + TDX快照 average_price`。
- `core/data_provider.py`：tencent-extras 注释 `tx85→tx51`；统一层构造段注释更新。
- TDX 快照 `tdx_get_quote_full` 增补防御性 `average_price→avg_price`（easy_tdx 未暴露则该列 `q.get` 返回 None 自动跳过）。

## 三、调整 B：委差源 [86] → [50] + push2 f192

- `core/tdx_client.py` `_TENCENT_FIELD_INDEX`：`"bid_ask_net": 86` → `50`。
- `stock_common/sc_datasource/_quotes.py` `_em_quote_full_impl`：
  - `params["fields"]` 增补 `f192`（同批并入 `f49,f161,f191`）。
  - 新增 `src→dst` 映射 `("f192", "bid_ask_net")`（委差，手）。
- 统一层构造：`bid_ask_net = rt_quote.get("bid_ask_net") or em_quote_raw.get("bid_ask_net")`（腾讯[50] 优先，push2 f192 兜底）。
- 注释与字段名保持 `bid_ask_net`（与字典「委差」行一致；字典未要求其正名）。

## 四、调整 C：实装 entrust_ratio / bid2 / ask2（canonical 成真）

- `stock_common/sc_schema.py` `CanonicalStockData` 新增三字段（均带默认值，不影响 frozen/slots 契约）：
  - `entrust_ratio: float = 0.0`（委比%，腾讯[74] + push2 f191 + TDX快照）
  - `bid2: float = 0.0`（买二价，元）
  - `ask2: float = 0.0`（卖二价，元）
- `core/tdx_client.py` `_TENCENT_FIELD_INDEX` 增补：`"entrust_ratio": 74`、`"bid2": 12`、`"ask2": 22`。
- `_quotes.py` `get_tencent_quote`：raw dict 与透传列表增补 `entrust_ratio`/`bid2`/`ask2`；`_em_quote_full_impl` 增补 `("f191", "entrust_ratio")`。
- `tdx_get_quote_full` 增补防御性 `entrust_ratio` 快照提取（TDX快照源）。
- `data_provider.py` tencent-extras 循环增补 `entrust_ratio`/`bid2`/`ask2`；统一层构造段增补三字段接线（`rt_quote.get(X) or em_quote_raw.get(X)`）。
- `to_dict()` 用 `dataclasses.asdict`，新字段自动进入导出 dict。

## 五、调整 D：内盘/外盘合成补全

- `core/tdx_client.py` `_TENCENT_FIELD_INDEX` 增补：`"s_vol": 8`、`"b_vol": 7`（腾讯[8]=内盘 / [7]=外盘）。
- `_quotes.py` `get_tencent_quote`：raw dict 增补 `s_vol`/`b_vol`，并复用 `_tencent_volume_divisor` 对**科创板(688)按股**做 `÷100` 归一手（与 TDX、push2 单位对齐；主板/创业板/北交所除数为 1.0 不变）。
- `_em_quote_full_impl` 增补 `("f161", "s_vol")` / `("f49", "b_vol")`（⚠️ 跨端点同号异义铁律：仅 stock/get 主域/镜像域读取，不混入 ulist.np）。
- `data_provider.py` 统一层构造：`s_vol/b_vol = rt_quote.get(X) or em_quote_raw.get(X) or 0`。
- **优先级约定（与既有 TDX 实时权威一致，未回归）**：TDX 实时五档为内盘/外盘权威源（不覆盖）；腾讯[8]/[7] 经 `get_tencent_quote` 在 TDX 缺失路径进入 `rt_quote`；push2 `f161/f49` 经 `em_quote_raw` 兜底。故未将 s_vol/b_vol 加入 tencent-extras **覆盖**循环，避免静默覆盖 TDX 实时值。

## 六、调整 E：缓存契约版本号

- `core/stock_cache.py` 新增模块常量 `CACHE_CONTRACT_VERSION = "v1"`。
- `_build_key`：`parts = [CACHE_CONTRACT_VERSION, category, func_name]` → key 形如 `v1:quote_full_delay:get_em_quote_full_delay:600519`。
- `invalidate_category` / `invalidate_prefix`：LIKE 前缀同步嵌入 `v1:`，保证按分类/前缀清理仍生效。
- 机制：未来统一层**静态字段**语义重定义时，+1 版本号即令全部旧 key 脱离引用而失效（TTL 自然回收 / 下次写入覆盖），无需手动清缓存。
- 副作用：本次部署后旧（无版本前缀）缓存 key 自动脱离引用，首次运行冷启动后重新写入——属预期的一次性安全网。
- 测试影响：57 项 cache/schema 单元测试全部通过（`invalidate_category`/`invalidate_prefix` 前缀匹配语义保持）。

---

## 七、验证结果

- `py_compile`：5 个改动文件均通过。
- 离线功能校验（系统 Python 3.12）：
  - `CanonicalStockData` 新字段 `entrust_ratio`/`bid2`/`ask2` 存在且默认 0.0，`to_dict()` 含之。
  - 腾讯索引：`avg_price=51`、`bid_ask_net=50`、`entrust_ratio=74`、`bid2=12`、`ask2=22`、`s_vol=8`、`b_vol=7`。
  - `get_tencent_quote` 解析：7 个新字段从正确索引提取；科创板 688 段 `s_vol/b_vol` 经 `÷100` 正确归手（8880000 股→88800 手）。
  - `get_em_quote_full` 映射：`f191→entrust_ratio`、`f192→bid_ask_net`、`f161→s_vol`、`f49→b_vol` 均命中。
  - 缓存 key 前缀：`v1:...` 生成正确。
- 单元测试：`tests/core/test_core_cache.py`(26) + `tests/core/test_core_schema.py`(31) = **57 passed**；统一层相关 `data_provider`/`canonical` 选中测试 **6 passed**。

---

## 八、与审计报告「八、待确认」的对应

| 审计待确认项 | 本次处置 |
|---|---|
| 调整 A/B 源切换是否实施 | ✅ 已实施（A/B） |
| 调整 C 选「实装字段」还是「字典降级」 | ✅ 用户选定「实装字段使 canonical 成真」，已实装 |
| 调整 E 是否纳入 | ✅ 已实施（E） |
| 调整 D（低优） | ✅ 已实施（D），TDX 权威优先级不变 |

---

## 九、未改变项（保持与前述修改一致的约束）

- 资金流四档、PE 动/静/TTM、涨停/跌停价源、f153/f154 常量：维持原正确接线，未改动。
- `sc_kline_cache.py` 已有 `_KLINE_CACHE_SCHEMA_VERSION="v2"`，无需调整。
- `_run_sync_strategy` 720s 硬超时墙 / `sc_network` DNS 护栏（前序 val 超时修复）：未触碰。
- 网络取数仍走既有 `asyncio`/`_quick_request`/`em_get` 收口，无新增外部依赖。
