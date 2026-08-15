# 三客户端本机数据资产与破解用途映射(2026-08-14 盘点)

> 用户: "3 个软件磁盘本地可以挖掘太多东西, 完全可以用来破解字典中的未知字段"
> 原则: 客户端打开与否不影响(文件在磁盘); 零网络、零风控、全字段、全市场

## 一、同花顺 C:\同花顺软件\同花顺

| 文件 | 大小 | 格式 | 内容/状态 | 破解用途 |
|---|---|---|---|---|
| realtime\shase\stocknow.dat | 14MB | 二进制(私有) | **沪市全字段行情快照**, 头部=字段ID表(`hd1.0` + `XX 70 00 04` 序列: ID 06,07,08,09,0a,11,0d,13,12,0c,0e,0f,18...), 600519 块含名称+数值 | 同花顺字段 ID 体系(与 thsdk 427 ID 联动破解) |
| realtime\sznse/stocknow.dat | 12.7MB | 同上 | 深市 | 同上 |
| realtime\quota/stb/bats/gfex/nyse/nsdq/cme/cffex/hz/stocknow.dat | 各 0.2-6MB | 同上 | 其他市场/品种 | 扩展市场 |
| realtime\swindx\indexnow.dat | 475KB | 二进制 | 申万指数行情 | 指数字段 |
| realtime\blockindex\indexnow.dat | 240KB | 二进制 | 板块指数 | 板块字段 |
| text\Base\text\sbt*.txt | 12 股×12 后缀 | **GBK 明文** | F10 全文(★行业分析☆ 600519 所属行业=食品饮料+行业地位表) | **零成本直读**(覆盖仅自选股 12 只) |
| industry.ini | 273KB | INI | 881xxx→成员股(600519→881273) | 行业成员(编码与 TDX 881 不通用) |
| StockBlock.ini | 2.9MB | INI | 个股→37 板块(600519) | 个股→板块全集 |
| BlockUpdate\block_*.ini | 30+ 个 | INI | 板块成员(块名加密) | 板块体系 |
| system\同花顺方案\StockLink.ini | 980KB | INI | 板块→块ID链接(881273=248:BC83) | 板块关联 |
| stockname\stockname_*.txt | 多文件 | 文本 | 股票名+附加字段(多语言/市场) | 名称/附加字段 |
| system\同花顺方案\Z同花顺深度分析level2方案说明.txt | 248KB | 文本 | L2 字段方案说明 | **字段定义线索**(L2 盘口) |

## 二、东方财富 C:\eastmoney\dfcf

| 文件 | 大小 | 格式 | 内容/状态 | 破解用途 |
|---|---|---|---|---|
| data\fullfinnew_gss_V12.dat | 13MB | 二进制(规整) | **深市全市场财务字段**(double 序列, 600519 块已定位) | **财务字段顺序破解**(对照 ZHB/tipinfo/网络 F10) |
| data\fullfinnew_hs_V12.dat | 4MB | 同上 | 沪市 | 同上 |
| data\fullfinnew_bjs_V12.dat | 4MB | 同上 | 北交所 | 同上 |
| data\DayData_SH_V43.dat / SZ / BK | 110/83/41MB | 二进制 | **全市场日线**(类似 TDX .day) | 历史行情口径验证(K 线破解) |
| data\fin\gss_cqcx.db | 7MB | **SQLite** | 全市场除权除息 | **SQL 直查**(除权字段对照) |
| data\fin\full_cqcx_hs_V3.dat | 7MB | 二进制 | 沪深除权除息 | 同上 |
| data\fin\full_HisLtg_V1.dat | 5.9MB | 二进制 | 历史换手 | 换手口径验证 |
| data\fin\IPO_Index_Data_V4.dat | 8.3MB | 二进制 | IPO 数据 | 新股字段 |
| data\StkQuoteList_V10_*.dat | 多版本 1-10MB | 二进制 | **东财客户端行情快照缓存** | 东财客户端字段集(与 push2 对照) |
| data\ContentStock_v1.dat | 8.9MB | 二进制 | 内容股票? | 待破 |
| data\Stock_JianPin.dat | 4.5MB | 二进制 | 股票简拼/附加 | 名称字段 |
| data\StockAliasV1.dat | 2MB | 二进制 | 股票别名 | 名称字段 |
| data\ProfitForecast.dat | 2.4MB | 二进制 | 盈利预测 | 预测字段(待破) |
| data\DelistStock.ini | 1.6MB | INI | 退市股 | 退市标记 |
| data\hs_bk_crc_data_new.dat | 879KB | 二进制 | 板块成分 CRC | 板块成员 |
| data\gss_bk_list_new.dat | 785KB | 文本(;) | 板块列表+成分(`日期;时间;ID;类型;创建;更新;?;名称;:市场.代码`) | **已解格式** |
| data\IndustryBlockRelation.dat | 14.5KB | 二进制 | 行业板块→子板块 BK 关系(BK0420→BK1479...) | 东财行业层级 |
| config\SubIndustry.dat | 8KB | **JSON** | 105 细分行业 D017 码(白酒=饮料 D017002002) | **已解** |

## 三、破解路线图(优先级)

1. **P0 东财全市场财务字段顺序**(fullfinnew_*): 对照 ZHB tipinfo/tdxstat 财务字段 + 网络 F10 → 一次性破解东财财务全字段(可能 100+ 字段)
2. **P1 东财行情快照字段集**(StkQuoteList_V10): 与 push2 114 字段数值匹配 → 东财客户端字段全集
3. **P1 同花顺 stocknow 字段 ID 体系**: 与 thsdk 427 ID(_constants.py 已归档)+ 表头 170 对照 → 离线破解 thsdk ⏳ 160 盘中字段(不再等盘中!)
4. **P2 日线全集**(DayData_*): K 线/除权口径验证
5. **P2 gss_cqcx.db SQLite**: 除权除息直接查

## 四、已确认的交叉印证锚点(600519)

| 维度 | 通达信 | 同花顺 | 东财 |
|---|---|---|---|
| 行业 | X210205 白酒(hy_tree) | 食品饮料(F10 明文)/881273 | 饮料 D017002002(JSON) |
| 归属文件 | tdxhy.cfg | sbt600519G.txt/industry.ini | SubIndustry.dat |


## 五、通达信 C:\new_tdx64 完整资产(2026-08-14 用户完成数据下载后全量扫描, 11,441 文件)

| 文件 | 大小 | 格式 | 内容/状态 | 破解用途 |
|---|---|---|---|---|
| **T0002\hq_cache\base.dbf** | 3.7MB | **标准 DBF** | **★ 40 字段全解(7880 只全市场)**: SC/GPDM/GXRQ + 股本 10(ZGB总/GJG国家/FQRFRG发起人/FRG法人/BG/HG/LTAG流通A/ZGG职工/ZPG增配) + 资产 8(ZZC总/LDZC流动/GDZC固定/WXZC无形/CQTZ长期投资/LDFZ流动负债/CQFZ长期负债/ZBGJJ资本公积/JZC净资产) + 利润 9(ZYSY主营/ZYLY主营利润/QTLY/YYLY营业利润/TZSY投资收益/BTSY补贴/YYWSZ营业外收支/SNSYTZ上年净利调整/LYZE利润总额/SHLY税后/JLY净利/WFPLY未分配/TZMGJZ调整每股净资产) + **DY=地域编号(8802xx-200: 7=北京/18=深圳/23=四川/29=贵州) + HY=行业编号(52 类, 1=银行/5=石油/16=电力/20=煤炭/37=白酒 37 只全白酒实锤) + ZBNB=报告期(3=Q1/6=H1/9=Q3/12=年报) + SSDATE上市日 + GDRS股东数** | **⭐ 基础资料金矿: 全市场财务+行业+地域+上市日, 标准 DBF 直接读** |
| T0002\hq_cache\sh.th2 / sz.th2 | 14/12MB | 二进制 | 沪/深行情快照缓存 | 待破(行情字段) |
| T0002\hq_cache\shs.tnf / szs.tnf | 9.7/8.4MB | 二进制 | 行情 | 待破 |
| T0002\hq_cache\ds_stk.dat | 9.6MB | 二进制 | ? | 待破 |
| T0002\hq_cache\gbbq | 5.4MB | 二进制(乱码) | 股本变迁(疑似加密) | 待破 |
| T0002\hq_cache\sbcwdata.dat / mgcwdata.dat / hkcwdata.dat | 1.4/1/0.4MB | 二进制(乱码) | 沪深/美股/港股财务数据(疑似加密) | 待破 |
| T0002\hq_cache\mgqxinfo2.dat / hkqxinfo.dat / hkqxinfo2.dat | 5.7/1.1/0.9MB | 二进制 | 美股/港股行情信息 | 待破 |
| T0002\hq_cache\sh.tcu / sz.tcu | 4.2/3.6MB | 二进制 | 涨跌速? | 待破 |
| T0002\hq_cache\zhb.zip | 1.25MB | zip | ZHB 包(本机直下载) | 已破(与 cache/zhb 同) |
| T0002\hq_cache\tdxstat.cfg / tdxstat2.cfg / tipinfo.dat / infoharbor_block.dat | 已破 | | 见 field_dict | |
| T0002\PriCS.dat + gs_bak\ 三日备份 | 787KB | 二进制 | 私有数据(每日备份) | 待破 |
| **vipdoc\** (9,330 文件) | - | .day/.lc1 等 | **全市场日线/分钟线/分时**(sh/sz/bj 目录) | K 线口径/历史验证 |
| T0002\hq_cache\neeqcode.txt | 630KB | 文本 | 新三板代码 | 名称 |


## 六、三客户端全文件台账(2026-08-14 完整扫描 16,917 文件)与新增破解

| 文件 | 格式 | 破解状态(本轮) |
|---|---|---|
| EM data\ProfitForecast.dat | **JSON** | ✅ **盈利预测全市场 5,607 只**: RATING_ORG_NUM/BUY/ADD/NEUTRAL/REDUCE/SALE 评级数 + YEAR1-5 EPS/PE(A=实际/E=预测, 600519: 2025A=65.85 ✓/2026E=68.97/2027E=72.76) |
| EM data\Stock_JianPin.dat | 明文 | ✅ 股票拼音缩写表(20260814,91340 + 市场,代码,拼音如 KCCYRGZNE,日期,日期,ID,ID) |
| EM data\ContentStock_v1.dat | 明文 | ✅ 板块成分+权重(0.158003,日期,时间,日期,2; 权重-代码: 0.640000-116.00241...) |
| EM data\StockAliasV1.dat / fin\fund_cqcx.db | SQLite | ✅ 别名表/基金除权除息(直查) |
| TDX T0002\hq_cache\ds_stk.dat | 二进制(标识 TDX_DS) | ✅ 商品/期货板块快照(IMCI=上期有色/T001=通达信商品/T002=农产品/T003=工业品...) |
| TDX T0002\hq_cache\shs.tnf / szs.tnf | 二进制(ASCII 头) | ✅ 服务器行情快照缓存(122.51.120.217 + 00999999 上证指数 + 数值区) |
| EM data\fullfinnew_hs_V12.dat | 二进制 | 🔶 **结构已确认**: 28B 头 + double 流(600519: 每股资本公积 21.34 ✓/每股未分配 220.64/总股本 12.5008 亿 ✓ 已定位)——50 字段顺序待逐字段对照(下一轮) |
| EM data\DayData_SH/SZ/BK_V43.dat | 二进制 | 🔶 日线全集(01000000 03000000 头)待解 |
| TDX sh.th2/sz.th2、sbcwdata.dat、gbbq、mgqxinfo*.dat、PriCS.dat | 二进制 | ⏳ 待破 |
| THS realtime\shase\stocknow.dat | 二进制(hd1.0) | 🔶 字段 ID 表在头(与 thsdk 427 联动待解) |
| THS system\同花顺方案\function.sav | 二进制(fh1.0) | ⏳ 同花顺函数库快照待破 |

### 同花顺官方配置已全解(本机):
- **tableheader\*.ini: 682 个列 ID**(8197=代码/20490=现价/526792=振幅/3426=连续涨停天数/3419=昨日涨停时间/
  3420=昨日涨停原因/133970=封单量/133971=封单额/330327-330328=最高封单量额/330323=首次涨停时间_new/
  330325=涨停类型/68762=集合竞价撮合涨幅/330347=竞价换手/920371=开盘涨幅/920372=实体涨幅/
  331068=FREE净流入金额/331136=FREE板块净流入/20549=涨停价/20550=跌停价/134222=涨停开板次数)
  → 全量存档: docs/verify/ths_tableheader_ids.md
- **iwcDataTable.ini: 56 项 ID→名称**(陆股通 15 项/涨停族: 连续涨停天数/今日涨停原因/封单量/封单额/周月年涨停次数/昨日换手/昨日成交量/上市天数/高频均笔量)
- **FyTableHeaderIdToConfigMapping.ini: 81 项指标**(id→index_id: 807731200=几天几板 up_down_stock_boards_up_for_days/
  807862272=主力金额 main_net_inflow/806092800=总市值/806223872=市盈pe_lyr/806289408=市盈(动)pe_mrq/806354944=市净率pb_mrq/
  805371904=60日涨幅/805437440=120日涨幅/805502976=250日涨幅/807796736=自由流通市值 free_flow_market_value)
- **marketstatic.json: 涨停池字段 ID**(199245=price/199246=gains/199224=turnoverRate/920213=reason/199205=continuous/199206=firstLimitUp/199207=lastLimitUp/199197=openTimes)

### 与字典交叉印证(本轮新锚点):
- 同花顺"涨停封单额 133971/连续涨停天数 3426/涨停原因 920213" ↔ tdxstat2[4]/YearZTDay/tdxstat[31-33] 候选族
- 同花顺"竞价换手 330347/集合竞价撮合涨幅 68762/开盘涨幅 920371" ↔ ZHB 竞价族(VOpenZAF/open_amount)✓ 三方一致
- 同花顺"FREE净流入 331068/主力金额 main_net_inflow" ↔ f137+f140 主力净 ✓
- 东财 ProfitForecast EPS 预测 ↔ 字典 EPS(f112)未来值补充


## 七、fullfinnew 财务字段顺序破解(2026-08-14 多股对照实锤, 对齐=代码+33)

记录结构: [文件头][块: 前16B + 代码8B + 33B 偏移 + double 流(~56 字段)]; 单位=元(股本=股)

| 位置 | 字段 | 600519 茅台 | 000001 平安 | 600036 招行 | 601288 农行 | 601857 中石油 |
> ⚠️ **2026-08-15 修正(中报 20 股实锤)**: 本表原标注 [0]=每股资本公积/[4]=每股盈余公积/[6]=每股现金净额/[13]=每股经营现金流 均误——
> 实为 [0]=基本EPS(Q1 21.77 巧合)/[4]=ROE加权/[6]=营收增长率/[13]=每股未分配利润; 正确全表见 field_dict §四 fullfinnew 条目(21 字段)
|---|---|---|---|---|---|---|
| [0]/[1] | **每股资本公积** | 21.79 | 0.75 | 1.50 | 0.21 | 0.26 |
| [2]/[3] | **每股净资产 BPS** | 216.32 | 23.91 | 44.90 | 8.08 | 8.88 |
| [4]/[34] | **每股盈余公积** | 10.57 | 2.83 | 3.37 | 2.65 | 3.0 |
| [6] | **每股现金流量净额** | 6.34 | 4.65 | 3.81 | 10.49 | -2.21 |
| [13] | **每股经营现金流** | 147.3 | 14.26 | 27.43 | 3.71 | 5.68 |
| [15] | **总资产(元)** | 3.20e11 | 6.03e12 | 1.35e13 | 5.10e13 | 3.04e12 |
| [16] | **净资产(含少数, 元)** | 2.72e11 | - | - | - | 7.51e11 |
| [22] | **资产负债率%** | 12.12 | 90.98 | 90.43 | 93.53 | 39.58 |
| [24] | 疑销售毛利率%(茅台 84.7 待核) | 84.68 | 9.02 | 9.51 | 6.46 | 53.46 |
| [27] | **总股本(股)** | 1.25e9 | 1.94e10 | 2.06e10 | 3.19e11 | 1.62e11 |
| [31] | **EPS 基本(报告期)** | 66.05 | 2.22 | 5.98 | 0.83 | 0.86 |
| [32] | 疑 EPS 摊薄/同比(茅台 52.2) | 52.22 | 41.17 | 43.76 | 36.64 | 7.26 |
| [53] | 每股资本公积(重复) | 21.79 | 0.75 | 1.50 | 0.21 | 0.26 |
| [55] | **归母净资产(元)** | 2.71e11 | 5.44e11 | 1.28e12 | 3.30e12 | 1.63e12 |

待定: [5][7][8][9][10][11][12][14][17][18][19][20][21][23][25][26][32][33][35][54] 等(需基准财务全量对照)


## 八、补漏轮破解(2026-08-14 二轮穷尽)

| 文件 | 格式 | 成果 |
|---|---|---|
| **TDX T0002\bigdata_1.zip** | zip | ✅ **641 个 func_*.cfg 功能配置 XML → 官方字段总表 1,924 字段**(code→中文名)存档 docs/verify/tdx_func_fields.md——覆盖股东人数/财务/沪深港通/可转债/基金/融资融券/增发配股/评级等; 样例: func_gdrs101(股东人数 date1/date/date3)、func_cwzb101(财务 BGQ报告期/SZ市值/PE)、func_hsgt101(沪深港通 drzjlr流入/drye余额/cje1净买入=calc mrcje-mccje) |
| **TDX T0002\bigdata_0.zip** | zip | ✅ **cloud_dax/*.sp 选股方案数百个**(GDRS股东人数/HYGDRS行业股东人数/HSGT/ZTXX涨停信息/JGCC机构持仓/KZZ可转债...), 含 GPSetCode 股票清单+UnitNum |
| **EM at_conv_dat.dat** | JSON | ✅ 可转债转股数据(SECUCODE/CORRECODE转股代码/TRANSFER_PRICE转股价/ISSUE_SCALE发行规模) |
| **EM hs_bk_crc_data_new.dat** | 明文 | ✅ 板块成分+权重(`板块ID;市场.BK码;CRC;1;类型;名称;权重列表`) |
| **EM Stock_Former_Name_V2.dat** | 明文 | ✅ **股票曾用名全表 3,521 条**(市场:代码-日期,拼音,名称,标志,ID——含历史更名链) |
| **EM StockAliasV1.dat** | SQLite | ✅ StockAlias 表 14,668 条(Code/AliasName/AlialJP 拼音/UpdateDate)——GBK text_factory |
| **EM fin\fund_cqcx.db** | SQLite | ✅ fund_cqcx 表(基金除权: ExDivType/NvcvtDate/Diviratioa/Diviratiob) |
| **THS realtime\market.txt** | INI | ✅ 31 市场配置(交易时间 MarketTime) |
| **TDX tmp\Cache\f_*** | gzip | ✅ 网页 JS 缓存(无字段价值) |
| TDX neeqcode.txt | 明文 | 新三板代码表(630KB, 待批量) |
| EM HK_Warrant_Info / stk_option / Stock_DetailType | hex 文本 | 待解码(ASCII hex 头) |

### 本轮对照价值
- 通达信官方字段名词体系(1,924 个 code): 如 gb_info/股东人数/PE 计算口径——与字典命名规律互证
- func_hsgt101 净买入=买入-卖出(calc 公式=字典 f135-146 买卖差结构的官方佐证)
- .sp 选股方案=通达信"大数据"字段入口(GDRS/HYGDRS 等, 与 func_* 界面联动)
