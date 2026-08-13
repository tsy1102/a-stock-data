# 客户端字段枚举全景（附录——东财/同花顺安装目录逆向，2026-08-11）

> **目的**：按字典设计理念穷尽客户端字段源——所有文本配置 + DLL 字符串 + 数据文件清单
> **方法**：全目录扫描（1000+ 配置文件）+ 二进制字符串提取（ASCII/UTF-16/GBK）
> **状态**：✅=已提取字段  📦=二进制待解码  🔄=运行时下载资源

## 一、东财客户端字段源

### 1.1 已提取（✅）

| 源 | 位置 | 字段数 | 说明 |
|:---|:---|:---|:---|
| 自选列表协议 | config\FavListUiFieldToServerField.xml | **118** | UI→DataCenter→HS 三层映射（见 em_client_dict.md）|
| 交易协议 | config\dict.ini | ~80 | 交易字段缩写+type 体系（见 network_servers.md §一.3）|
| 行情协议 DLL | DataCenter.dll | **725** | 盘口/封单/大单/涨跌/财务字段（节选见下）|
| 列表协议 DLL | ElementStockListFactory.dll | 110 | bkCode/conceptList/clientType 等 |
| 市场定义 | config\markets_define.xml | 8+ | 市场 ID（1=沪/0=深/90=板块/10=沪期权…）|

### 1.2 DataCenter.dll 核心字段节选（725 中精选）

- **盘口**：AskVol1/BidVol1（买一量/卖一量）、SumAskVol/SumBidVol、AfterSumAskVol/AfterSumBidVol（盘后）、AfterTradeNum/AfterVolume（盘后）
- **封单**：FengDanAmount/FengDanVolume（封单额/量）、FengDanAmountLastDay/FengDanVolumeLastDay（昨日）
- **大单**：BigTradeAmount/BigTradeVol、DTBidVolume/DTOffTimes/DTTimeFirst/DTTimeLast/DTTopAmount/DTTotalAmount（DT=大单系）
- **资金**：BuyAmount/BuyCost、BuyInRatio/BuyInRatio3Day/10Day/20Day、ABuyAmout/ABuyVol/ASellAmout/ASellVol（A股买卖）
- **涨跌序列**：Close2/Close4/Close5/Close9/Close19/Close59/Close119/Close249（与自选协议 CloseN 体系一致——N 日前收盘价）
- **财务**：Dividendtype/Diviratioa/Diviratiob（分红率A/B）、ExDate/ExDivType（除权日/类型）
- **本地库**：SQLite 表 `stock_pk` / `customlistheader_v2`（自选股本地存储结构）

### 1.3 数据文件（📦 二进制，待解码）

| 文件 | 大小 | 说明 |
|:---|:---|:---|
| fullfinnew_hs_V12.dat | 4MB | 沪深全市场财务（代码明码，字段压缩）|
| fullfinnew_gss_V12.dat | 13MB | 港美股财务 |
| fullfinnew_bjs_V12.dat | 4MB | 北交所财务 |
| ProfitForecast.dat | 2.5MB | 盈利预测 |
| StockAliasV1.dat | 2MB | 股票别名 |
| Stock_DetailTypeV2.dat | 453KB | 股票类型 |
| Stock_Flags.dat | 58KB | 股票标志 |
| Stock_Former_Name_V2.dat | 828KB | 曾用名 |
| optionalFieldDataV1.dat | 94KB | 可选字段（加密）|
| hs_bk_crc_data_new.dat | 880KB | 沪深板块数据 |
| ContentStock_v1.dat | 9MB | 内容股票 |
| BlockIndexHisLtg.dat | - | 板块指数历史换手（Data\fin\）|

### 1.4 文本数据（✅）

- **bjs_code_conversion.txt**：北交所代码转换表（833xxx→920xxx 全量映射，含 BSETransferDate/EffDate）
- DelistStock.ini：退市股清单（1.6MB）

### 1.5 东财自选列表协议 118 字段（✅ em_client_dict 并入——UI→DataCenter→HS 三层映射）

> **来源**：config\FavListUiFieldToServerField.xml；与主字典 push2 f 字段破解表对照；datacenter-web API 字段名权威来源
> **注意**：HS=沪深，Gss=港美股/深股通

118 字段映射表（UI → DataCenter → HS 协议）

| UI 字段 | DataCenterField | HS 请求字段 |
|:---|:---|:---|
| 最新价 | LastSale | Price,Close,PreSettlementPrice,Open,High,Low |
| 涨跌幅 | Percent | Price,Close,PreSettlementPrice,Open,High,Low |
| 涨跌额 | NetChange | Price,Close,PreSettlementPrice,Open,High,Low |
| 买一价 | Ask1 | Ask1 |
| 卖一价 | Bid1 | Bid1 |
| 现量 | CurVol | CurVol,CurVolDirection |
| 成交量 | Volume | Volume |
| 金额 | Amount | Amount |
| 1分钟涨幅 | UpSpeed | Price,PrePrice |
| 换手率 | Turnover | Volume,LTG |
| 实际换手率 | ActualTurnover | Volume |
| 量比 | VolumeRatio | Liangbi |
| 昨收价 | Close | Close,PreSettlementPrice |
| 开盘价 | Open | Open,High,Low,Price |
| 最高价 | High | Open,High,Low,Price |
| 最低价 | Low | Open,High,Low,Price |
| 振幅 | Delta | Close,High,Low,PreSettlementPrice,Open |
| 内盘 | InnerVolume | Volume,Waipan |
| 外盘 | OuterVolume | Waipan |
| 内外比 | InnerOuterRatio | Volume,Waipan |
| 3日涨幅 | Percent3Day | Price,Close,Close2,PreSettlementPrice |
| 6日涨幅 | Percent6Day | Price,Close,Close5,PreSettlementPrice |
| 3日换手 | Turnover3Day | LTG,Prev2SumVolume,Volume |
| 6日换手 | Turnover6Day | LTG,Prev5SumVolume,Volume |
| 均价 | AvgPrice | AvgPrice,Amount,Volume |
| 涨停价 | UpperPrice | UpperPrice |
| 跌停价 | LowerPrice | LowerPrice |
| 委买总量 | SumAskVol | SumAskVol |
| 委卖总量 | SumBidVol | SumBidVol |
| 委比 | AskBidRatio | SumAskVol,SumBidVol |
| 委差 | AskBidChange | SumAskVol,SumBidVol |
| 买一量 | AskVol1 | AskVol1 |
| 卖一量 | BidVol1 | BidVol1 |
| 昨日涨幅 | PercentLastDay | N_ZDF |
| 昨日成交量 | VolumeLastDay | Volume19 |
| 昨日成交额 | AmountLastDay | Value19 |
| 开盘昨比 | KaiPanZuoBi | Close,Open,PreSettlementPrice |
| 现均差 | XianJunCha | AvgPrice,Price,Amount,Volume |
| 实体涨幅 | ShiTiZhangFu | Price,Open |
| 5日涨幅 | Percent5Day | Price,Close,Close4,PreSettlementPrice |
| 10日涨幅 | Percent10Day | Price,Close,Close9,PreSettlementPrice |
| 20日涨幅 | Percent20ay | Price,Close,Close19,PreSettlementPrice |
| 60日涨幅 | Percent60Day | Price,Close,Close59,PreSettlementPrice |
| 本月涨幅 | PercentThisMonth | Price,Close,LastMonthPrePrice,PreSettlementPrice |
| 今年涨幅 | PercentThisYear | Price,Close,LastYearPrePrice,PreSettlementPrice |
| 近一月涨幅 | PercentRecentMonth | Price,Close,Close19,PreSettlementPrice |
| 近半年涨幅 | PercentRecentHalfYear | Price,Close,Close119,PreSettlementPrice |
| 近一年涨幅 | PercentRecentYear | Price,Close,Close249,PreSettlementPrice |
| 5日换手率 | Turnover5Day | LTG,Prev4SumVolume,Volume |
| 10日换手率 | Turnover10Day | LTG,Prev9SumVolume,Volume |
| 20日换手率 | Turnover20Day | LTG,Prev19SumVolume,Volume |
| 5日跑赢大盘天数 | WinDays5 | Prev4WinDays,Price,Close,PreSettlementPrice |
| 10日跑赢大盘天数 | WinDays10 | Prev9WinDays,Price,Close,PreSettlementPrice |
| 20日跑赢大盘天数 | WinDays20 | Prev19WinDays,Price,Close,PreSettlementPrice |
| 历史最高价 | PriceHighHistory | Price,PriceHigh |
| 60日最高价 | PriceHigh60Day | Price,PriceHigh59days |
| 连涨天数 | ContinueUpDays | Price,Close,ContinueUpDownDays,PreSettlementPrice |
| 总股本 | ZGB | ZGB |
| 总市值 | ZSZ | Price,Close,TotalMarketCap,PreSettlementPrice |

> 其余字段（流通股本/流通市值/市盈率/市净率/每股收益/每股净资产/股息率等财务估值类）见原文件（共 118 项）

## 二、市场 ID 定义（markets_define.xml）

| ID | 市场 | 备注 |
|:---|:---|:---|
| 0 | 深圳 | ems（东财自研行情）|
| 1 | 上海 | ems |
| 2 | 中证指数 | ems |
| 90 | 板块 | ems |
| 10 | 上海期权 | ems（isOptions）|
| 12 | 深圳期权 | ems |
| 13 | 国证指数 | ems |
| 47 | 东财指数 | ems |
| 100+ | QQZS 等港美股 | gss（深股通/港美股）|

> 项目 push2 secid 前缀（1.600519 / 0.000001）即此体系（1=上海/0=深圳）

## 三、同花顺指标系统键（IndicatorKeyHelper.json，低价值——公式引擎用）

TREND=109C8 / KLINE=C09C8 / MACD=3E8C93 / RSI=3009C8 / KDJ=1A09C8 / BOLL=3D09CB /
CCI=3189D4 / DMI=2609C8 / OBV=2D09C8 / ATR=2109CE / PSY=1489D5 / 筹码分布=20A9F 等 50+ 指标

> 项目不调用同花顺公式引擎（技术指标本地算），此表仅作 thsdk 未来指标调用参考

## 二、同花顺字段源

### 2.1 行情协议端点（✅ DataCenter.xml——thsdk 同源！）

| 协议 | 端点 | 端口 | 说明 |
|:---|:---|:---|:---|
| QuoteV1 | hevo-h.10jqka.com.cn | 8601 | 旧版行情 |
| QuoteV2 | hevo-h.10jqka.com.cn | 9601 | 行情 V2 |
| QuoteV3 | hevo.10jqka.com.cn | 8602 | 行情 V3（calc/stats/supercalc）+ udns/wdcs/otqs/realorder 各端点 |
| QuoteV4 | hxpns.hexin.cn | 9000 | 个性化推送 |
| QuoteVice | 172.19.80.115 | 8602 | 备用 |

> **与项目关联**：thsdk 连接的行情服务器即此协议族（项目 sc_ths.py 用其 SDK 封装）；
> "盘面" query_key 失效（2026-08-11 发现）= V3 协议字段集改版，估值字段迁至"扩展1"

### 2.2 字段定义 XML（🔄 运行时下载资源，未缓存）

Hevo.Core.DataModel.dll 引用 4 个字段定义资源（位置 440684-440818）：
- `Data.QuoteFieldData.xml`（行情字段定义）
- `Data.TradeFieldData.xml`（交易字段定义）
- `Data.MarketData.xml`（市场定义）——✅ **已从客户端日志提取**（128 市场前缀，见 §2.3）
- `Data.DataApiFieldData.xml`（Data API 字段定义）

> **获取实验（2026-08-11）**：用户操作客户端（行情页/F10/问财/迷你趋势）+ 文件系统监控 30 分钟——
> **QuoteFieldData/TradeFieldData/DataApiFieldData 确认仅在进程内存、不落盘**（仅 MarketData.xml 启动时同步+日志打印）。
> **结论**：需抓包 hevo 域（8601/9601/8602，BinaryPack 协议）才能获取；当前不折腾。
> **替代**：官方字段的运行时子集已通过 **thsdk** 获得（项目 thsdk_field_verify.md 395 ID 字典——thsdk 即同花顺官方 SDK，返回字段名为官方定义）

### 2.3 已提取（✅）

- **IndicatorKeyHelper.json**：50+ 指标系统键（见 §1.5 指标键）
- **Hevo.Api.Quotes.dll**：协议线索——`BinaryPack` 序列化 + JSON 请求格式（`"codelist":[...]` / `"kind":"CLIENT"` / `"ver":"1.1"` / `Rate limit exceeded`）
- **block_tree.xml**（1.6MB）：板块树全量（行业/概念/地域，另一体系）
- **DNSCache.json/Services.xml**：服务器清单（见 network_servers.md）
- **MarketData.xml**（✅ 2026-08-11 从客户端日志提取，128 个市场前缀）：

| 前缀 | 市场 | 前缀 | 市场 |
|:---|:---|:---|:---|
| USHA | 沪A | USZA | 深A |
| USHB | 沪B | USZB | 深B |
| USHI | 沪指 | USZI | 深指 |
| USHD/USHJ/USHP/USHT/USHC | 沪D/科创板?/盘/退/创 | USZD/USZJ/USZP/USZH/USZC | 深对应 |
| UHK* | 港股（HKW 窝轮/HKT 涡轮/HKD 指数…）| UUS* | 美股 |
| UNY* | 纽约（NYA 等）| UOO*/UCF* | 期权/期货 |
| UTII | 沪国债? | UMT* | 中证? |
| URFI/URFA | 瑞富? | UZOI/UZOO | 中欧? |
| UCM* | 商品 | UGT* | ? |

> **价值**：thsdk 的 USHA/USZA 前缀（sc_ths.py 用 `"USHA" if 6开头 else "USZA"`）的**官方市场代码定义表**——扩展其他市场（港股/美股/期权）时直接可用

## 三、通达信客户端（C:\new_tdx64，2026-08-11 新增）

### 3.1 服务器（connect.cfg——HQHOST 43 台官方来源）

见 network_servers.md §2.0 + docs/verify/data/tdx_connect_cfg.json（HQHOST 43/HFHost 2/INFOHOST2 9/DSHOST 16 全表）
移动线路实测：HFHost 2/2 ✅、DSHOST 16/16 ✅（7727）、INFOHOST2 9/9 ✅（7712）、云 3/3 ✅

### 3.2 大数据栏目指标代码（✅ bigdata_all.txt，404 个）

`T0002\bigdata_all.txt`——通达信"大数据"功能栏目 ID 字典（板块级/股票级指标栏目）：

| 系列 | 示例 | 说明 |
|:---|:---|:---|
| 可转债 | KZZ_DFKZZ/KZZ_GX/KZZ_KZZSY/ZZ_SHTK/ZZ_XZTK… | 转债栏目体系 |
| 基金 | JJ_ETFJJ/JJ_LOFJJ/JJ_ZQETF/JJ_CNHSJJ/JJ_FBJJ… | 基金栏目 |
| 美股 | US12_ETF/US9_ZGG/US10_ADR/US11_ZMMG/US13_TZPJ/US14_JGCC | 美股系列 |
| 指数 | HSZS1_ZSHQ_GZZS/HSZS1_ZSHQ_HSZS/HSZS1_ZSHQ_QQZS… | 指数栏目 |
| 通用 | 5G/AIWJJ/AIYX/AGPJ/BKLD/BKZS/CWZB/CXG/CYB/GDRS… | 概念/资金/筹码/涨跌停 |

> **价值**：通达信大数据指标栏目体系（东财 push2 栏目/THS 指标键的第三套体系）——
> 与项目"板块轮动/资金流/涨跌停"类功能对照；KZZ 转债系为扩展市场字典

### 3.3 数据结构（📦 待下载/待解码）

- `vipdoc\cw\`：gpcw 财务数据（二进制，F10 数据源——需客户端连接行情后下载）
- `T0002\blocknew\`：板块文件（blk 格式——未下载，仅自选 zxg.blk）
- `T0002\hq_cache\` 等缓存目录：空（客户端未连接）
- TDataParse.dll：gpcw 二进制解析器（字段为二进制 offset，非字符串——待协议分析）

### 3.4 数据文件字典（✅ 2026-08-11 客户端连接后下载，hq_cache 全量）

客户端连接行情后 hq_cache 下载 100+ 个官方数据文件——**与项目 ZHB 同源的原始文件**：

| 文件 | 大小 | 说明 | 状态 |
|:---|:---|:---|:---|
| **tdxstat.cfg** | 1.3MB | 全市场统计快照 **35 列 × 7976 只**（=项目 ZHB tdxstat）| ✅ 已解析 |
| **tdxstat2.cfg** | 908KB | 资金流+基本面 **21 列 × 7976 只**（=ZHB tdxstat2）| ✅ 已解析 |
| profile.dat | 313KB | 全市场名称 | 与项目同源 |
| tipinfo.dat | 657KB | 每股收益/提示（=ZHB tipinfo）| 同源 |
| spblock.dat | 314KB | 板块成分 | 同源 |
| tdxhy.cfg | 150KB | 行业分类 | 同源 |
| tdxzsbase.cfg | 233KB | 指数基础 | - |
| gbbq | 5.5MB | 股本变迁/除权 | - |
| code2name.ini | 13KB | 期货合约字典（IF/IC/IH/T/TF/TL 乘数保证金）| ✅ |
| ds_stk.dat | 10MB | 扩展市场 | - |
| mgcwdata.dat/hkcwdata.dat/sgpcwdata.dat | 1MB+ | 美股/港股/深沪财务 | - |
| neeqcode.txt | 646KB | 新三板代码 | - |
| specgpext.txt | 260KB | 扩展股 | - |
| base.dbf | 3.8MB | 数据库 | - |
| sh.tcu/th2、sz.tcu/th2 | 30MB | 行情缓存 | - |

### 3.5 tdxstat.cfg 35 列破解（✅ 官方原始文件 20260810 + 实时交叉验证）

| Col | 茅台 600519 | 定义 | 验证 |
|:---|:---|:---|:---|
| 0 | 1 | 市场（0=深/1=沪）| ✅ |
| 1 | 600519 | 代码 | ✅ |
| 2 | -0.1041 | 待确认（?）| - |
| 3 | 20.39 | **pe_dynamic 动态PE** | ✅ 今日实时 20.39 精确一致 |
| 4 | 20260810 | 日期 | ✅ |
| 5 | 3 | **streak_days 连涨跌** | ✅ 字典已确认 |
| 6 | 3.03 | **change_pct 涨跌幅** | ✅ 字典已确认 |
| 7 | 0.05 | 1日涨跌幅? | - |
| 8 | 0.16 | 2日涨跌幅? | - |
| 9 | 20.4833 | **pe_ttm** | ✅ push2delay f163=20.48 一致（Col[3]/[9] 口径已定）|
| 10 | 3.86 | **dividend_yield 股息率** | ✅ 腾讯 [64]=3.86 一致 |
| 11 | 54094.90 | 成交额?（万）| 待确认 |
| 12 | 空 | - | - |
| 13 | 空 | - | - |
| 14 | 2723998.52 | 大额资金? | 待确认 |
| 15 | 34992 | **employee 员工数** | ✅ 茅台 3.5万/平安 4.2万/招行 12万 合理 |
| 16 | 5931.07 | 待确认 | - |
| 17 | 11.03 | 待确认 | - |
| 18 | 11.38 | **change_20d 20日涨幅** | ✅✅ 四股全中（11.38/7.12/7.26/4.46 精确）|
| 19 | 4.16 | 待确认（非45/120/250日）| - |
| 20 | 6.21 | 待确认（茅台/平安同值疑点）| - |
| 21 | 2.17 | **ytd 年初至今** | ✅ 万科 -30.11 精确；茅台/平安同值疑点 |
| 22 | 140206 | 待确认（unknown2）| - |
| 23 | 0 | 待确认 | - |
| 24 | 38799600 | 待确认（总股本?万）| 茅台 12.56亿股=125600万≠3880万 待确认 |
| 25 | 空 | 待确认 | - |
| 26 | 0 | 待确认 | - |
| 27 | -1.31 | 待确认 | - |
| 28 | -2.84 | **change_5d 5日涨幅** | ✅ 平安/万科/招行三股全中；茅台除息暂态异常（8/6 分红30元）|
| 29 | 0.80 | 待确认 | - |
| 30 | 1.62 | **change_10d 10日涨幅** | ✅ 三股全中（1.62/3.83/-0.23 精确）|
| 31-33 | 空 | 待确认 | - |
| 34 | 8000000 | 待确认（股本?）| 000001=8000000 万? 待确认 |

### 3.6 tdxstat2.cfg 21 列破解（✅ 官方原始文件 + 实时交叉验证）

| Col | 茅台 600519 | 定义 | 验证 |
|:---|:---|:---|:---|
| 0 | 1 | 市场 | ✅ |
| 1 | 600519 | 代码 | ✅ |
| 2 | 20260810 | 日期 | ✅ |
| 3 | 842830.44 | **amount 成交额（万）**| ✅ 84.3亿（茅台日成交合理）|
| 4 | 空 | - | - |
| 5 | 326691.94 | 待确认 | - |
| 6 | 空 | - | - |
| 7 | 332623.08 | 待确认 | - |
| 8 | 空 | - | - |
| 9 | 984 | 待确认（手数?）| 字典标 main_net_buy_hands 待复核 |
| 10 | 173 | 待确认 | 字典标 main_net_buy_hands 待复核 |
| 11 | -0.13 | 待确认（资金占比%）| - |
| 12 | -1.47 | 待确认 | - |
| 13 | 881130 | **industry_code 行业码** | ✅ 8803/8804/881 段 |
| 14 | 13040.65 | **main_net_buy_amount（万）**| ✅ 1.3亿（茅台主力净买合理）|
| 15 | 2263.98 | 主力净买另一口径? | 待确认 |
| 16 | 31.390 | **ipo_price IPO发行价** | ✅✅ 茅台 31.39/平安 40/万科 1.0 精确 |
| 17 | 1539.980 | **52周最高** | ✅✅ 腾讯 [67]=1539.98 精确一致 |
| 18 | 1151.010 | **52周最低** | ✅✅ 腾讯 [68]=1151.01 精确一致 |
| 19 | 13.78 | 待确认（非45/120/250日）| - |
| 20 | 12.88 | **change_30d 30日涨幅** | ✅✅ 三股全中（12.88/10.25/6.91 精确）|

> **价值**：字典 §12.0 记录的"35 列未全破解"→ 本次拿到官方原始文件 + 多列铁证
> （ipo_price/52周/pe 双口径/股息率/员工数/行业码/成交额）
> **交叉验证（2026-08-11，TDX K线）**：tdxstat Col[18]=20日/Col[28]=5日/Col[30]=10日/
> Col[21]=ytd（万科精确）、tdxstat2 Col[20]=30日——多股精确全中
> **疑点记录**：茅台/平安 Col[20]/[21] 及 Col[22]-[34] 部分同值——疑似占位/
> 除息暂态（茅台 8/6 分红 30 元）；Col[22]=911 值行业/地区类、Col[24] 个股级
> （净资产/市值类待定）、Col[34] 大量 0（未启用）

## 四、同花顺普通版（C:\同花顺软件\同花顺，2026-08-11 新增）

### 4.1 行情服务器字典（✅ public\dns\dns_cache.json + domain_list_cache.ini）

**123ths 域名族 9 域 ~80 IP**（已存 docs/verify/data/ths_dns_cache_20260811.json）：

| 域名 | 用途 | IP 数 | 典型 IP |
|:---|:---|:---|:---|
| main.123ths.com | 主行情 | 4 | 123.60.76.34/8.132.233.145 |
| fu2/fu4/fu6.123ths.com | 行情分片 | 14 | 106.14.44.170/122.9.78.232 |
| realhk.123ths.com | 港股实时 | 19 | 119.3.36.20/8.145.213.49 |
| delayhk/delayus.123ths.com | 延时港/美 | 26 | 8.132.233.158/114.115.218.60 |
| euhq.123ths.com | 欧洲行情 | 4 | 124.70.145.157 |
| usotc.123ths.com | 美股 OTC | 5 | 121.37.238.70 |
| ifindhq.123ths.com | iFinD 行情 | 11 | 8.145.213.52 |
| slavedns.123ths.com | 备用 DNS | 6 | 114.115.216.10 |

> 与远航版 hevo 域名（hevozhuhq1 等）为同一服务器集群的不同域名映射；
> hqserver.ini（根目录/用户目录）为旧式直连 IP 列表

### 4.2 stockname 市场名称库（✅ 官方，30+ 文件）

`stockname\stockname_<市场>_<段>.txt/.base`——代码=名称官方库：

| 市场代码 | 内容 | 示例 |
|:---|:---|:---|
| 16 | 沪市全股票+指数 | 1A0001=上证指数|000001@s |
| 32 | 深市 | - |
| 104 | 申万行业指数 | 801001=申万50/801010=农林牧渔… |
| 112/120/128/144/168/176/184/200/216 | 各类市场（含港/美/期权?） | - |

> 格式：`代码=名称|映射代码@市场后缀`；ConfigVer=20260811 当日版

### 4.3 F10 文本库（✅ text\Base\text\sbt*.txt——五期财务指标）

用户查看个股 F10 时下载（如 002193：sbt002193A-O.txt），**同花顺 F10 文本版**：

| 指标 | 说明 |
|:---|:---|
| 每股收益(元) | 五期（最新~去年同期）|
| 每股净资产(元) | 五期 |
| 净资产收益率(%) | 五期 |
| 总股本(亿股)/实际流通A股/限售流通A股 | 股本结构 |
| 每股资本公积/每股未分配利润 | 最新期值 |
| 营业收入(万)同比/净利润(万)同比 | 最新期同比 |

### 4.4 thsdk 字段铁证（✅ 2026-08-11 交叉验证）

**THS "扩展1" 市净率 = 现价 / 最新报告期每股净资产**（静态口径权威确认）：
- 002193：市净率 4.6457 = 4.78（基础数据现价）/ 1.0289（F10 每股净资产 26-03-31）——**精确匹配**
- 呼应 PB 双口径研究（THS=静态 vs 腾讯=除息）：F10 文本级证据坐实 THS 静态口径

### 4.5 实时行情快照（📦 realtime\ 二进制）

- swindx/bats/nsdq/nyse 各市场 stocknow.dat（快照 1-3MB）+ indexnow.dat
- 用户查看美股/指数行情时下载——二进制待解码

### 4.6 12 股 F10 交叉验证（✅ 2026-08-11 用户采集 144 个 F10 文本）

**样本**：000001/000002/000725/000858/002193/002594/300750/600036/600519/600809/601318/688981
**数据**：同花顺 F10 文本（每股净资产/总股本/营收/净利五期）+ 腾讯实时（限频 1s）+ tdxstat/tdxstat2 全列

**tdxstat2 新确认（与 zhb_client 映射对照——zhb 已破解，本次 12 股数据印证）**：
- **Col[5] = amount_1d 昨日成交额（万）**：茅台 32.7 亿 = 8/7 成交额（zhb_client L843 已破解，本次印证）
- **Col[7] = amount_2d 前日成交额（万）**：茅台 33.3 亿 = 8/6 成交额（zhb_client L845）
- **Col[14] = main_net_buy_amount（万，T 日）**：茅台 1.30 亿（8/10）vs 腾讯今日 -5.07 亿（8/11）——跨日差异正常
- **Col[15] = main_net_buy_amount_1d（T-1）**：茅台 0.23 亿（zhb_client L853）
- **Col[19]/[20] = change_30k_bar/ref**：茅台 13.78/12.88 = 30日K线涨幅（zhb_client L857-858；本日 Col[20] 三股全中）

**tdxstat 新确认**：
- **Col[22] = 通达信内部代码（5-6 位）**：与 tdxhy T 码/X 码/880xxx 板块码均不对应
  （白酒 61111×2+31113、银行 140206/120501、保险 51101、半导体 41008…）
  ——**码表不在本地**（客户端运行时从服务器下载），标记待码表
- **Col[24] = 动态值（盘中更新）**：茅台 38799600→4878669.14（万）——口径未明
- **Col[34] = 大量 0 + 少数值**（比亚迪 180 亿/招行 1500 亿——疑似两融/解禁类）

**疑点澄清**：茅台/平安 Col[20]/[21]/[22-34] 之前同值——**tdxstat.cfg 已被通达信客户端盘中更新**（新数据），
茅台 Col[22] 140206→61111、Col[24] 38799600→4878669——旧文件为 20260810 收盘版、新文件为 20260811 盘中版；
同值疑点随之消失（是旧版数据生成时的占位，新版已修正）

**统一层对照结论（2026-08-11）**：zhb_client `_parse_tdxstat`（L712）/`_parse_tdxstat2`（L834）
映射与本次 12 股 F10 验证 **100% 吻合**（tdxstat Col[6]/[18]/[20]/[21]/[28]/[30]、
tdxstat2 Col[3]/[5]/[7]/[9]/[10]/[13]/[14]/[15]/[16]/[17]/[18]/[19]/[20]）——
**统一层无需代码修改**，本次验证闭环确认既有破解正确；Col[11]=自由流通股本（万股，
茅台 5.4 亿≈12.52×46% 大股东锁定）为本次新线索（zhb 未解析该列，待 TdxQuant 复核）

## 五、结论与建议

1. **已穷尽层**：文本配置（XML/JSON/INI）与 DLL 明文字符串——东财 118+80+725+110、通达信 404 指标码、同花顺市场前缀+名称库+F10 文本已归档
2. **待解码层**（📦）：东财 fullfinnew_v12 财务库/ProfitForecast——需抓包客户端行情请求或分析 dat 压缩格式才能枚举字段（**列为后续破解目标**）
3. **可获取层**（🔄）：同花顺 4 个字段 XML——客户端运行时从服务器下载，**建议下次运行客户端后重新搜索**（或抓包 hevo 域请求）
4. **印证价值**：DataCenter.dll 的 Close2-Close249 序列与自选协议 HS 字段（Close2/Close5/Close19…）完全同体系——两源互证
5. **通达信**：connect.cfg 全表已提取（HQHOST 43 来源补齐）+ 404 指标码；gpcw 财务/板块数据需客户端连接后下载
6. **同花顺普通版**：123ths 域名族 9 域 ~80 IP + stockname 名称库 + F10 文本库；thsdk 市净率口径铁证（现价/最新期 BPS）
