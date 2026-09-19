# ZHB 包深度重排查报告（2026-09-19）

> 数据来源：通达信 `zhb.zip` 离线包（`cache/zhb/zhb_20260918.zip`，数据日期 20260918，47 文件 / 4.39 MB）
> 动机：7 月对 ZHB 的分析定论一直未被复核，本次在 P0 eltdx 接入 + 17.3.1 节流验证后，按"核对已用真实性 / 落实未用内容 / 排查被忽略项"三线重做完整排查。
> 结论：ZHB 是**全市场 8055 只 A 股统计快照**的核心载体（非仅 1600 只名称表）；已用内容解析正确、数值真实，并有 `ihelp.dat` 黄金锚背书；存在可落实的未用内容（`hqrule.dat` 已落实）与需专项破解的加密二进制（`*comte*.dat`）。

---

## 一、全量文件清单（47 个）

按"项目是否已解析"分类：

### A. 已被项目解析（18 文件，已用内容）
| 文件 | 解析器 | 内容 | 实测记录数 |
|--|--|--|--|
| tdxstat.cfg | `_parse_tdxstat` | 全市场个股统计快照（PE/涨跌幅/连板/52周/K线周期等） | **8055** |
| tdxstat2.cfg | `_parse_tdxstat2` | 全市场资金流向+封单额+52周高低 | **8055** |
| tipinfo.dat | `_parse_tipinfo` | 财报日历（EPS/披露日/除权除息/分红） | 5644 |
| spblock.dat | `_parse_spblock` | 大板块成分股（融资融券/沪深港通等） | 35208 行 |
| profile.dat | `_parse_profile` | 名称表（沪市老股，**仅精选名单**） | 1651 |
| relation.dat | `_parse_relation` | A/B 股名称 | 1677 |
| tdxpkmore.cfg | `_parse_tdxpkmore` | 新股/特色股名称 | 1373 |
| pttab.dat | `_parse_pttab`/`_parse_special_tags`/`_parse_delisted` | 代码对照+特别标签+退市 | 1794 |
| tdxchain.cfg | `_parse_tdxchain` | 概念/产业链节点（80 行） | 80 |
| neednote.dat | `_parse_neednote` | 调休补班日 | 66 |
| brkseat.dat | `_parse_brkseat` | 龙虎榜席位 | 2761 |
| tdxzs3.cfg | `_parse_sw_industries`/`_parse_industry_map` | 申万行业分类 | 1071 |
| needini.dat | `_parse_holidays` | **节假日**（1991-2030） | 42 |
| xgsg.cfg | `_parse_xgsg` | 新股申购日历 | 24 |
| tdxahrate.cfg | `_parse_ahrate` | A+H 股比价 | 1 |
| brkcomp.dat | `_parse_brokers` | 券商名称表 | 844 |
| incon.dat | `_parse_csrc_industries` | 证监会行业分类 | 3703 |
| tdxadr.cfg | `_parse_adr` | 中概股 ADR 对应表 | 31 |
| othersg.cfg | `_parse_convertible_bonds` | 可转债信息 | 18 |

### B. 未被项目解析 — A 股相关（可落实）
| 文件 | 内容 | 规模 | 落实价值 |
|--|--|--|--|
| **hqrule.dat** | 交易规则（涨跌停阈值/股通限额） | 12 行 | **高** ✅已落实 |
| tdxbk.cfg | 板块简称↔全称（锂电池→锂电池概念） | 58 行 | 中（展示富化） |
| addedcode_bj.cfg | 北交所新增代码+状态 | 347 行/693 码 | 中（北交所覆盖） |
| tdxbjmore.cfg | 北交所代码 | 349 行/349 码 | 中（北交所覆盖） |
| ilong.dat | 指数名称表（含 A 股/港股通指数） | 907 行/531 码 | 中 |
| hspy.dat | 沪深港通标的 | 22 行 | 低 |
| tend_std.cfg | 热点数据分组名 | 1013 行 | 低 |
| ihelp.dat | **栏目说明（列语义字典）** | 2463 行 | **极高（黄金锚，见下）** |

### C. 未被项目解析 — 海外市场/其他（超出 A 股范围，建议忽略）
hkblock(恒指)/jjblock(基金)/mgblock(美股道琼斯)/ukblock(英股)/sgxblock(新加坡)/sbblock(三板拟转A)/csiblock(中证指数)/tdxdszs(港股分类)/tdxhkag(港股行业)/hkzsinfo(恒指信息)/importzs(美股中概)/tdxmgag(美股行业)/tdxsbzs(三板)。

### D. 加密/强压缩二进制（被忽略/未确定含义）
`nacomte.dat` `nbcomte.dat` `nvcomte.dat` `nzcomte.dat` `nscomte.dat` `nscomte_std.dat` —— 6 文件，熵 7.8-7.9/8.0，zlib/gzip/bz2/lzma 全失败，5 个共享 32 字节相同头（暗示 ECB 加密固定头或共享压缩字典）。

---

## 二、任务一：已使用内容的真实性核对

### 2.1 tdxstat.cfg（核心，8055 行）
- **结构**：8055 行**全部恰好 35 列**（零截断），日期 8004/8055 = `20260918`（22 只为 0917/空，属新股/停牌边缘情况）。
- **数值真实性**：
  - `change_pct`(Col6) 均值 +1.44%，超 ±11 仅 34 只（创业板/科创板/北交所 ±20%），超 ±21 仅 3 只 —— 合理。
  - `pe_ttm`(Col9) 5565 有效、1459 负值（亏损股）、零值 0、最大 8811.7 —— 合理。
  - `high_52w ≥ low_52w`：**8042/8042 零违反** —— 强一致性。
  - 代表股抽样（茅台/平安/宁德/浦发/平安/比亚迪）PE、涨跌幅、YTD 全部落在 2026 年真实区间。
- **关键确认**：600000/601318/300750 **均在 tdxstat 中且数据完整** —— 再次证明"缺码只在 profile.dat 名称表，不在统计快照"。

### 2.2 黄金锚 ihelp.dat 强力背书解析语义
`ihelp.dat` 是通达信客户端栏目字典，逐条印证项目 tdxstat/tdxstat2 字段映射：
- `涨幅：(现价-昨收)/昨收*100` → Col[6]=change_pct ✓
- `市盈(动)：现价/折算成全年的每股收益` → Col[3]=pe_dynamic ✓
- `市盈(TTM)：最近12个月的每股收益` → Col[9]=pe_ttm ✓
- `封单额：涨停或跌停时买一/卖一的金额` + `昨封单额/前封单额` → **强力印证 tdxstat2 Col[4]/[6]/[8] 三日滚动封单额**（docstring 核心主张）✓
- `连板天：连续涨停板的天数` → Col[33]=zt_lianban ✓
- `股息率(TTM)...` → Col[10]=dividend_yield ✓

### 2.3 文档失实（真实性问题，非解析错误）
- tdxstat/tdxstat2 docstring 标"**7938 只**" → 实测 **8055**（差 117，+1.5%）；列数 35/21 主张**准确**。
- `profile.dat` 注释"全市场 4888 只" → 实测 **1651**（精选名单，不含部分大盘股）—— 7 月定论遗留的描述性错误。
- `needini.dat` 注释称节假日数据来源，但解析代码实际读 `neednote.dat`（`_parse_neednote` 行 512），docstring 与实现**不一致**（需统一）。

### 2.4 名称表陈旧（真实性隐患）
`profile.dat` 将 000001 映射为"**深发展A**"（其 2012 年前旧名，现应为"平安银行"）——属**数据陈旧**而非解析错误；项目名称解析走腾讯兜底，故不影响生产，但 ZHB 名称表本身时效性差。

---

## 三、任务二：未使用但存在的文件 — 落实尝试

### 3.1 ✅ 已落实：hqrule.dat（交易规则）
新增 `ZhbData.trading_rules` 属性 + `_parse_hqrule()` 方法，实测返回：
```
SHGTDayMax=520, SZGTDayMax=520, MainAG_Cage=1, CYBZDRatio=0.20,
CYBZCDate=20200822, SHGZ_XS3=1, SHKZZ_XS3=1, KCBOpenDate=20250922,
KCCZStartDate=20250713, SZST10Date=99991231, SHST10Date=99991231
```
价值：`CYBZDRatio=0.20` 即创业板 ±20% 涨跌停，**可使项目从硬编码阈值改为动态读取**；`SH/SZGTDayMax=520` 为沪深股通每日限额。已通过 `py_compile` + 真实 zip 解析验证，暂未接下游（仅暴露数据）。

### 3.2 待落实候选（已验证可解析，给出方案）
| 文件 | 落实方案 | 价值 |
|--|--|--|
| tdxbk.cfg | 新增 `block_short_names` 属性，spblock/概念展示时用全称替代简称 | 低-中 |
| addedcode_bj.cfg + tdxbjmore.cfg | 新增 `bse_stocks` 属性，扩展北交所覆盖 | 中 |
| ilong.dat | 新增 `index_name_map`，补全指数名称 | 中 |
| hspy.dat | 标记沪深港通标的 | 低 |

### 3.3 海外市场文件
建议**明确忽略**（超出 A 股核心范围），仅作文档记录。

---

## 四、任务三：被忽略/含义未确定的内容

### 4.1 ihelp.dat（隐藏金矿）
原本未被项目读取，实则是**验证 tdxstat/tdxstat2 列语义的权威黄金锚**（见 2.2）。建议：将其关键栏目定义沉淀为 `docs/field_verification/` 下的"列语义基准"，替代口头 docstring 主张。

### 4.2 `*comte*.dat`（加密/强压缩二进制，需专项破解）
- 6 文件，熵 7.8-7.9/8.0（高熵=强加密或强压缩）。
- `na/nb/nz/ns/nscomte_std` 共享 32 字节相同头 `7a99696405d414671ba17a0587d9b86e...`；`nv` 自第 16 字节起偏离（6881 处不同）。
- zlib/gzip/bz2/lzma 在 offset 0-7 全部失败。
- **判断**：大概率 TDX 私有加密（ECB 模式固定头）或私有压缩字典；命名 `na/nb/nv/nz/ns` 疑为不同数据序列。**需专项破解**（非本次范围），列为待办。

### 4.3 名称表时效性
profile.dat 名称陈旧（见 2.4），建议报告层优先依赖腾讯兜底，ZHB 名称表仅作离线降级。

---

## 五、结论与推荐
1. **ZHB 价值主体是全市场 8055 只统计快照**（tdxstat/tdxstat2），"本地优先"对 val 全市场扫描 100% 命中、零兜底 —— **不应删除 ZHB**。
2. **已用内容解析正确、数值真实**，并有 `ihelp.dat` 黄金锚背书；仅 docstring 计数（7938 vs 8055）与 profile 描述（4888 vs 1651）需订正。
3. **落实首步已完成**（hqrule.dat → trading_rules）；其余 A 股相关未用文件给出方案，待择机接线。
4. **加密 `*comte*.dat` 列为专项破解待办**；海外 block 文件明确忽略。
5. 建议将 `ihelp.dat` 栏目定义沉淀为字段语义基准文档。

> 以上为 ZHB 离线包深度重排查，不构成投资建议。
