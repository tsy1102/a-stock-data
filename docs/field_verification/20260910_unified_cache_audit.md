# 统一层 × 缓存层 × 字典一致性审计报告（2026-09-10）

> 数据来源：腾讯行情 / 东方财富 push2·ulist / 同花顺 fuyao / 通达信 easy_tdx（运行时源）
> 审计对象：`field_dict.md`「统一层接线」列（§12.8.12e，最新破解 round12 2026-09-08 及 2026-09-09 专项复核）vs 代码实际接线
> 结论性质：技术诊断，不构成投资建议

---

## 一、结论摘要

**需要增加调整 —— 是，但范围收敛**。字典近期大量破解中，**绝大部分（资金流四档、f153/f154 常量、PE 动/静/TTM、涨停/跌停价源切换）已正确反映在统一层代码**；但 **round12（09-08）与 09-09 专项复核新定的 4 处字段，字典「统一层接线」列已写 `canonical`，代码却未同步**：

| # | 字段 | 字典最新定案 | 代码当前实际 | 判定 |
|---|------|--------------|--------------|------|
| 1 | 均价 avg_price | `canonical: 腾讯[51]+TDX快照`（[85] 已撤销） | `tdx_client.py:919` 映射 `avg_price→85`；`_quotes.py:95`、`sc_schema.py:472` 用 [85] | ❌ 用已撤销源 |
| 2 | 委差 bid_ask_net | `canonical: 腾讯[50]+push2 f192`（[86] 已撤销） | `tdx_client.py:923` 映射 `bid_ask_net→86`；`_quotes.py:98`、`sc_schema.py:510` 用 [86] | ❌ 用已撤销源 |
| 3 | 委比 entrust_ratio | `canonical: 腾讯[74]+push2 f191+TDX快照` | `CanonicalStockData` 无 `entrust_ratio` 字段；活跃代码零赋值 | ❌ 字段缺失（字典声称已接） |
| 4 | 买二/卖二价 bid2/ask2 | `canonical: 腾讯[12]+tdx bid2+sina[14]` / `腾讯[22]+tdx ask2+sina[24]` | `CanonicalStockData` 无 `bid2`/`ask2` 字段 | ❌ 字段缺失（字典声称已接） |

> 内盘/外盘（s_vol/b_vol）代码仅接 easy_tdx，未合成 腾讯[8]/[7]+push2 f161/f49，属**部分接线**（低优先级，见 §五）。

**缓存层：本次批次无需结构性调整**（详见 §四）；但建议补充「契约版本号 + 失效机制」作为加固（§六）。

---

## 二、核查范围与方法

- **字典侧**：`git log -- docs/field_dict.md` + 关键区段精读（§12.3.4 资金流重定案 1765–1827；§12.8.12e 统一层接线表 3072–3143）。
- **统一层（读路径）**：`core/data_provider.py::get_canonical_stock_data`（强类型 `CanonicalStockData` 合约，6 大报告唯一入口）→ `stock_common/sc_schema.py:444 CanonicalStockData` → 适配器 `stock_common/sc_datasource/_quotes.py`、`core/tdx_client.py` 索引映射。
- **缓存层**：`core/stock_cache.py`（统一 SQLite/L1）、`stock_common/sc_kline_cache.py`（K 线磁盘缓存）。

---

## 三、统一层逐字段核查结果

### 3.1 已正确反映（无需调整）

| 字段族 | 字典定案 | 代码现状 | 证据 |
|--------|----------|----------|------|
| 资金流四档（f135–f149） | §12.3.4 推翻 V17.0 旧「四档并列+主力=f137+f140」误案，重定 `f137=主力净(=f140+f143)`、`f142=大单卖出`、`f143=大单净`、`f146=中单净`、`f149=小单净` | `CanonicalStockData` 键名与字典一致；`data_provider.py:1418–1434` 用 `fund_main_today/fund_large_today/fund_large_sell/fund_mid_today/fund_small_today`；**未出现旧的 `f137+f140` 重复计** | `sc_schema.py:542–556`、`data_provider.py:1418–1434`、字典 1767–1782 |
| PE 动/静/TTM | `pe_dynamic=f162` / `pe_lyr(静态 LYR)=f163` / `pe_ttm=f164` | `data_provider.py` 透传三键；`get_lng_report.py:417–429` 分动/静展示 | 字典 3090–3092 |
| 涨停/跌停价 | `canonical: 腾讯[47]+push2ex ztp` / `腾讯[48]`（push2 f51 非涨停价、已自误注订正） | `_quotes.py:100–102` 取 腾讯[47]/[48]；`data_provider.py:512` 优先级 `腾讯[47/48] > TDX get_price_limits > push2 f51/f52` | 字典 3103–3104 |
| f153/f154 协议常量 | 恒为 3/4 的协议枚举常量，「downstream 不得按个股值消费」 | 活跃代码对 `f153`/`f154` **零引用**（grep 无匹配） | 字典 3141–3142 |
| 主力净 = f137（东财单值） | 已定案 | `rt_quote.fund_main_today` 单值透传；thsdk TCP 网关已于 V17.0.29 退役，回退 f137 | 字典 3125、`data_provider.py:1418` |

### 3.2 脱节项（需调整，详见 §五）

- **均价 avg_price**：代码 `_f["avg_price"]=85`（`tdx_client.py:919`），但字典 3109 明确「原腾讯[85]为误注，对均价锚仅 3/20，已撤销均价候选，回退 L3；canonical=腾讯[51]+TDX快照」。
- **委差 bid_ask_net**：代码 `_f["bid_ask_net"]=86`（`tdx_client.py:923`），但字典 3106 明确「腾讯[86] 非委差，等值 0/20、与 TDX 委比同号仅 55%，已撤销[86]候选；canonical=腾讯[50]+push2 f192」。
- **委比 / 买二·卖二价**：字典 §12.8.12e 标注 `canonical`，但 `CanonicalStockData` 无对应字段，活跃代码无赋值 → 字典「统一层接线」列**超前于代码**（见 §七根因）。

---

## 四、缓存层核查结果

### 4.1 `sc_kline_cache.py`（K 线/CYQ 磁盘缓存）
- 已有 `_KLINE_CACHE_SCHEMA_VERSION = "v2"`（`sc_kline_cache.py:108`），**嵌入文件名** → 格式/列变更自动失效旧缓存，设计到位。
- K 线属标准 OHLCV，不受字典语义改动影响。**无需调整**。

### 4.2 `core/stock_cache.py`（统一 SQLite + L1 缓存）
- 缓存 key = `category:func_name:args`（`stock_cache.py:_build_key`），**无全局 schema 版本号**，亦无「字段契约变更触发失效」机制。
- 长 TTL 分类：`static_permanent=10年`、`basic_info_static=365天`、`share_capital`/`industry_classification=90天`。若某**静态字段语义**被重定义，旧值最长可静默服务 90天–10年。
- **对本批次的实际风险**：本轮改动均落在**实时/短 TTL** 字段（quote_full_delay=7天 trading_day、fuyao_valuation=1h、fund_flow=7天），且 von 均价/委差源切换不影响已被缓存的语义层（均价取腾讯实时、未走缓存；委差若新增则走 quote_full_delay 7天刷新）——**本次无需迫使缓存失效**。
- **结论**：缓存层**无需为本次批次做结构性调整**。

---

## 五、需要增加的调整（具体方案）

### 调整 A（必须）：均价源 [85] → [51]
- `core/tdx_client.py:919`：`"avg_price": 85` → `51`（并核对 [51] 在腾讯 qt.gtimg 实为均价/VWAP 强锚）。
- 同步更新注释 `stock_common/sc_schema.py:471–472`、`stock_common/sc_datasource/_quotes.py:94–95`、`core/data_provider.py:1413`。

### 调整 B（必须）：委差源 [86] → [50]+push2 f192
- `core/tdx_client.py:923`：`"bid_ask_net": 86` → `50`（且建议将字段语义从模糊的 `bid_ask_net`（盘口净量 L4）正名为 `entrust_diff`（委差），与字典对齐）。
- 委差还需 push2 `f192` 合成：在 `_quotes.py` 腾讯分支已取 [50] 基础上，于 `data_provider.py` 统一层以 `rt_quote.entrust_diff` 优先、`em_quote_raw.f192` 兜底（与 内盘/外盘 的「腾讯+push2+TDX」合成模式一致）。
- 同步更新 `sc_schema.py:510–511`、`_quotes.py:98`、`data_provider.py:1416` 注释。

### 调整 C（建议）：补齐委比 / 买二·卖二价 字段，使字典「canonical」断言成真
- `CanonicalStockData` 新增 `entrust_ratio`（委比=腾讯[74]+push2 f191+TDX快照）、`bid2` / `ask2`（买二/卖二价=腾讯[12]/[22]+tdx bid2/ask2+sina）。
- 在 `_quotes.py` / `tdx_client.py` 索引映射与 `data_provider.py` 统一层构造段补充取数与透传。
- **或**：若暂不实装，将字典 §12.8.12e 对应行的「canonical: …」改为「未接 canonical｜外部: …」（与 封单额/连板天数/涨速 的诚实标注保持一致），避免字典虚报接线状态。

### 调整 D（低优先级）：内盘/外盘合成补全
- 当前 `s_vol`/`b_vol` 仅接 easy_tdx；建议按字典 3107/3108 合成 腾讯[8]/[7]（⚠️科创板腾讯按股×100、其余按手）+ push2 f161/f49 + TDX，与委差合成模式统一。

### 调整 E（缓存加固，建议非必需）：增加契约版本号
- 在 `core/stock_cache.py` 增设 `CACHE_CONTRACT_VERSION`（如 `"v1"`），并入缓存 key 或作为 `cache_entries` 列；当统一层字段语义发生**静态字段**重定义时 +1，旧版本缓存整体失效。
- 目的：杜绝「长 TTL 静态分类在字段语义变更后静默服务陈旧数据」的潜在隐患（本轮未触发，但属架构级加固）。

---

## 六、缓存失效操作（若实施调整 A/B）
均价/委差属实时取数（腾讯未缓存、push2 走 quote_full_delay 7天），切换源后**无需全量清缓存**；若担心 7 天窗口内旧映射残留，可定向清理：
```
python core/stock_cache.py clear --category quote_full_delay
```

---

## 七、根因（系统性）
字典「统一层接线」列由 `scratch/inject_wiring_col.py` 在 **2026-09-03（V17.0.25）** 按当时代码状态自动注入。随后 round12（09-08）与 09-09 专项复核**更新了字典判定**（撤销 [85]/[86]、定案 [51]/[50]+f192、新增委比/买二卖二价 canonical），但**未回写代码**。

**建议引入「字典→代码回写」门禁**：任何将某字段「统一层接线」列从「未接」改为「canonical」的提交，必须附带对应代码接线改动（新增字段 + 适配器映射 + 透传），否则视为字典虚报。可挂 `scripts/lint_field_same_number.py` 同类校验或在每日流水线 `--strict-naming` 中加一项。

---

## 八、待确认
- 调整 A/B（源切换）是否立即实施？
- 调整 C 选「实装字段」还是「字典标注降级为未接」？
- 调整 E（缓存契约版本）是否纳入？

（本报告仅给出审计结论与方案，未改动任何代码。）
