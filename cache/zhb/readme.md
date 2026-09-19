# ZHB 数据包文件清单与用途说明（readme）

> 数据来源：通达信 ZHB 数据包 `zhb_20260918.zip`（解压后 47 个文件）。
> 数据日期：**20260918**（取自 `tdxstat.cfg` 首行）。
> 本文档用于记录包内每个文件的名称、大小、编码、结构与其在 `a-stock-data` 项目中的解析状态，以备后查。
> 维护：2026-09-19 ZHB 深度重排查时补全（V17.3.1）。

---

## 一、核心统计快照（项目主干，已解析）

| 文件 | 大小 | 编码 | 行数 | 结构 | 用途 / 解析状态 |
|---|---|---|---|---|---|
| `tdxstat.cfg` | 1.35 MB | UTF-8 | 8055 | 管道`\|`分隔，35 列（首列为市场标记位`0`/深，真实代码在第 2 列） | 全市场个股日线统计快照：涨跌幅/PE(动·TTM·LYR)/52周高低/封单额/连板天/股息率/YTD 等。**项目主干取数（val 全市场扫描 100% 本地覆盖）** |
| `tdxstat2.cfg` | 912 KB | UTF-8 | 8055 | 管道分隔，21 列 | 全市场个股扩展快照：封单额三日滚动（今/昨/前）、主力净流入等 |
| `tipinfo.dat` | 645 KB | UTF-8 | 5644 | 管道分隔 | 个股贴士信息：财报披露日/业绩/解禁等 |
| `profile.dat` | 314 KB | GBK(二进制结构) | 190 | 固定宽字段，`\x00` 填充 | 全市场股票标准中文简称表。**注意：注释称"全市场 4888 只"，实测仅 1651 只（名称缺口约 44%）**，已有腾讯兜底 |
| `spblock.dat` | 317 KB | GBK | 35208 | `#板块名` 分段 + 7位代码行 | 大板块成分股（融资融券/沪深300/中证2000 等）。`sp_blocks` 已解析 |
| `relation.dat` | 97 KB | 二进制 | 1 | 二进制 | 关系数据（代码关联）。已解析 |
| `tdxpkmore.cfg` | 50 KB | GBK | 1373 | 管道分隔 | 代码→名称补充（含新三板/老三板映射）。`unified_name_map` 已用 |
| `pttab.dat` | 34 KB | GBK | 1794 | 逗号分隔 | 板块/特别处理(ST)标记、退市标记。`special_tags`/`delisted_stocks` 已用 |
| `tdxchain.cfg` | 2 KB | GBK | 80 | 管道分隔 | 概念链：概念代码→成分股。`concept_chain` 已用 |
| `neednote.dat` | 4 KB | GBK | 66 | `[Data]` 段 | 节假日/交易周。**注意：文档注释写 `needini.dat`，实际读此文件** |
| `brkseat.dat` | 33 KB | UTF-8 | 2761 | 管道分隔 | 券商交易席位。`brk_seat` 已用 |
| `tdxzs3.cfg` | 33 KB | GBK | 1071 | 管道分隔 | 申万行业(code+type=12) + 所有板块 代码→名称。`sw_industries`/`industry_map` 已用 |
| `needini.dat` | 4 KB | UTF-8 | 42 | `[Holiday]` 段 | 节假日配置（备用，主用 neednote.dat） |
| `xgsg.cfg` | 3 KB | GBK | 24 | 管道分隔 | 新股申购(IPO)列表。`ipo_list` 已用 |
| `tdxahrate.cfg` | 23 B | GBK | 1 | 管道分隔 | AH 股比价（例：比亚迪\|002594\|01211\|1）。`ah_stocks` 已用 |
| `brkcomp.dat` | 30 KB | GBK | 844 | 管道分隔 | 券商公司信息（id\|名称）。`brokers` 已用 |
| `incon.dat` | 68 KB | GBK | 3703 | `#ZJHHY` 分段 | 证监会行业分类。`csrc_industries` 已用 |
| `tdxadr.cfg` | 726 B | GBK | 31 | 管道分隔 | ADR 美国存托凭证（中概股）。`adr_stocks` 已用 |
| `othersg.cfg` | 2 KB | GBK | 18 | 管道分隔 | 其他证券（可转债等）。`convertible_bonds` 已用 |
| `tdxzs.cfg` | 18 KB | GBK | 604 | 管道分隔 | 板块指数（旧版/备用，项目主用 `tdxzs3.cfg`） |

---

## 二、本次深度重排查落实的 A 股相关文件（V17.3.1 新增解析）

| 文件 | 大小 | 编码 | 行数 | 结构 | 用途 / 解析状态 |
|---|---|---|---|---|---|
| `hqrule.dat` | 217 B | UTF-8 | 18 | `[RULE]` 段 + `KEY=VALUE` | 交易规则：`CYBZDRatio=0.20`(创业板±20%)、`SH/SZGTDayMax=520`、`KCBOpenDate` 等。**已落实 → `ZhbData.trading_rules`**（替代硬编码涨跌停阈值） |
| `ilong.dat` | 24 KB | GBK | 907 | 管道分隔 `市场\|指数代码\|?\|名称[|说明]` | 跨市场指数代码→名称（含 A 股/港股/美股/板块指数），907 条中 566 条含名称。**已落实 → `ZhbData.index_names`**（项目此前无离线指数字典，补充） |
| `tdxbk.cfg` | 1.5 KB | GBK | 58 | 管道 `id\|简称\|全称\|flag` | 板块简称↔全称（如 锂电池→锂电池概念）。**已落实 → `ZhbData.block_short_names`**（富化 spblock 展示，零风险） |
| `addedcode_bj.cfg` | 15 KB | GBK | 347 | 首行汇总头(逗号) + `44\|老代码\|920代码\|名称(已切换/已转板)\|上市日` | 老三板/新三板→北交所(920)映射、切换状态、上市日。**已落实 → `ZhbData.bj_stock_metadata`（合并）** |
| `tdxbjmore.cfg` | 9 KB | GBK | 349 | 管道 `44\|920代码\|分类\|名称\|flag\|` | 北交所代码+名称+精选层分类/状态。**已落实 → `ZhbData.bj_stock_metadata`（合并）**（tdxstat 已有 920 代码，本文件为元数据补充） |
| `tend_std.cfg` | 16 KB | GBK | 1013 | `[GROUPxx]` 段 + `Num=N` + `Name01..NameN` + `ParentName=` | 题材概念分类树：100 组、201 个概念，99 组归属"主题投资"父类（注：`Name(N+1)..` 为 TDX 冗余重复，已按 `Num` 截断）。**已落实 → `ZhbData.concept_tree`** |
| `hspy.dat` | 325 B | UTF-8 | 22 | 管道 `市场\|代码\|拼音助记码` | **通达信拼音助记码字典**（如 `ZJGH→002839 张家港行`、`DSL→603233 大参林`）。**已落实 → `ZhbData.pinyin_codes`**（纠正旧判：非沪深港通标的，项目此前无拼音检索字典，为补充；现有 `hsgt_flow` 仅含资金流非标的基础清单） |
| `ihelp.dat` | 119 KB | GBK | 2463 | `#FUNC_ABCol` 栏目字典 | 通达信客户端栏目定义（涨幅/市盈/封单/连板/股息/换手/量比/委比/内外盘/股本 等权威释义）。**作为验证 tdxstat 列语义的"黄金锚"，已沉淀至 `docs/field_verification/ihelp_column_defs.md`**（不接入运行取数） |

> 新增解析器均遵循 `ZhbData` 的 lazy 属性 + `_parse_xxx()` 三件套模式，并提供模块级访问函数：
> `get_index_names_from_zhb()` / `get_block_short_names_from_zhb()` / `get_bj_stock_metadata_from_zhb()`
> / `get_concept_tree_from_zhb()` / `get_pinyin_codes_from_zhb()`。

---

## 三、海外市场文件（明确不解析，超出 A 股范围）

| 文件 | 大小 | 编码 | 行数 | 用途 |
|---|---|---|---|---|
| `hkblock.dat` | 72 KB | GBK | 10036 | 港股板块成分 |
| `hkzsinfo.cfg` | 3 KB | UTF-8 | 181 | 港股指数信息 `[HSI_QZ]` |
| `tdxdszs.cfg` | 15 KB | GBK | 382 | 港股指数列表 |
| `tdxhkag.cfg` | 7 KB | GBK | 137 | 港股↔A股映射 |
| `mgblock.dat` | 46 KB | GBK | 8099 | 美股板块成分（道琼斯等） |
| `tdxmgag.cfg` | 14 KB | GBK | 328 | 美股↔A股映射 |
| `ukblock.dat` | 2 KB | GBK | 290 | 英股板块 |
| `sgxblock.dat` | 623 B | GBK | 117 | 新加坡中国股 |
| `jjblock.dat` | 56 KB | GBK | 5101 | 基金板块 |
| `sbblock.dat` | 28 KB | GBK | 3533 | 三板拟转A股 |
| `csiblock.dat` | 14 KB | GBK | 1217 | 中证指数板块 |
| `importzs.cfg` | 554 B | UTF-8 | 12 | 导入指数（含数值快照） |
| `tdxsbzs.cfg` | 186 B | GBK | 10 | 三板成指成份 |

---

## 四、加密 / 压缩二进制（待专项破解）

| 文件 | 大小 | 编码 | 行数 | 特征 |
|---|---|---|---|---|
| `nacomte.dat` | 9.6 KB | GBK(乱码) | 335 | 熵 7.8–8.0；zlib/gzip/bz2/lzma 解压均失败；与 nbcomte/nscomte/nzcomte 共享 32 字节相同文件头（疑似 ECB 加密固定头或共享压缩字典） |
| `nbcomte.dat` | 9.6 KB | GBK(乱码) | 335 | 同上，与 nacomte 内容近同 |
| `nscomte.dat` | 1.4 KB | GBK(乱码) | 39 | 同上头部特征 |
| `nscomte_std.dat` | 1.5 KB | GBK(乱码) | 37 | 同上头部特征 |
| `nvcomte.dat` | 6.9 KB | GBK(乱码) | 184 | 同上头部特征（内容略异） |
| `nzcomte.dat` | 2.5 KB | GBK(乱码) | 70 | 同上头部特征 |

> 判定：TDX 私有加密/压缩格式，未被任何项目代码读取，列为"被忽略/含义未定"，需专项破解（截至 2026-09-19 未破）。

---

## 五、关键结论备忘

1. **ZHB 包不应删除**：核心载荷 `tdxstat.cfg`/`tdxstat2.cfg` 是全市场 8055 只统计快照，val 全市场扫描 100% 本地命中、零兜底。
2. **旧注释不可全信**（7 月定论复核）：`profile.dat` 注释"4888 只"实=1651；`tdxstat` docstring"7938 只"实=8055；`needini.dat` 注释与实际读 `neednote.dat` 不一致。
3. **`tdxstat.cfg` 首列为市场标记位**，真实代码在第 2 列；项目 `code=parts[1]` 解析正确。
4. **北交所代码已全覆盖于 tdxstat**（92 前缀 349 只），故 `addedcode_bj`/`tdxbjmore` 为元数据补充而非代码补全。
5. **`hspy.dat` 实为拼音助记码**，非沪深港通标的清单。
