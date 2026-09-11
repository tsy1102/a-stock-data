# 桶 A 全扫 + 桶 B 标记：TDX 实时神谕表与未破解字段分类（2026-09-09）

> 数据来源：通达信 `tdx_quotes` 实时（600519 茅台 20260909 14:08 实测，HQDate=20260909）。
> 方法论：沿用 path A+B「通达信官方命名语义终止器」——TDX 命名字段即官方 L1 锚，与字典未破解列按名印证。
> 所有结论均不构成投资建议。

## 0. 结论速览

- TDX `tdx_quotes` 实时神谕表（HQInfo / ExtInfo / CwInfo / ProInfo / CalcInfo / BspInfo 六大块）可对撞字典 **tdxstat 0–36 全部财务/股本/资产/权益列**：**28/37 列**直接按通达信官方命名印证 → 升 **L1（TDX 官方命名）**；2 列 ⚠️ 候选；7 列 ❌（legacy 股本结构 / 保留字段，TDX 无对应命名）。
- **桶 A（TDX/腾讯可破解）=** tdxstat/ZHB 同源列 + tx[] 实时快照弱字段 + wenda + 财务。
- **桶 B（TDX/腾讯射程外）=** 东财 ulist 专属 126 字段 + 恒空/恒0 死占位符 + 需基准序列的计算字段（Beta tx[56] / CYQ / 52周高低）。

## 1. TDX tdx_quotes 实时神谕表（600519 实测）

| 块 | 命名字段（实时值节选） | 语义 |
|:---|:---|:---|
| HQInfo | Now=1291.12, Close=1309.3, Open=1305.01, MaxP/MinP, Volume=25871, Amount=3.35e9, Inside=15370, Outside=10502, Average=1294.07, HSL=0.207%, LB=1.301, CJBS=21334 | 实时盘口/成交量 |
| ExtInfo | ZTPrice=1440.23, DTPrice=1178.37, ZGB=125008.16(万), LTGB=125008.16(万), FreeLtgb=54094.9(万), MGSY=35.57, MGJZC=200.99, ZSZ=1.614e12(元), SYL=18.13, BelongHY="82102", BelongHS300/RZRQ/HGTAG=1 | 股本/市值/涨停跌停/行业/标签 |
| CwInfo | ZZC=30905078(万), LDZC=26072466, GDZC=2222089, WXZC=857874, GDRS=296404, LDFZ=4664507, CPFZ=1084275, ZBGJJ=157.7, JZC=25125360, YYSR=9070326, YYCB=947376, YSZK=57.08, YYLR=6141129, TZSY=101.38, JYXJL=7069075, ZXJL=5838700, CH=6131721, LYZE=6143842, SHLY=4603333, JLY=4451688, WFPLY=19968322, GXRQ=20260815, Start=20010827, IPOPrice=31.39 | 资产负债表/利润表/现金流（万元） |
| ProInfo | 资金净流入=-5.63e8, 主力资金净流入=-2.89e8, Wtb=-12, 20日涨幅=-3.86, 年初至今=-4.30, 静态市盈率=19.61, TTM市盈率=19.82, HisHigh=1539.98, HisLow=1151.01, 3/5/10/60日涨幅, OpenAmo=33408256 | 资金流/涨跌幅/估值/52周 |
| CalcInfo | CAZAF/CAZDJ/CAZF/CAKPHSZ/CALTZZ/CAHSZ/CALTZ/CAKP/CAZD/CAJJ/CAST/CAHTB/CAGJB/CAJZDBP/CAZDBP | 计算指标族 |
| BspInfo | BuyP=1291.12, SellP=1291.13, BuyV=2, SellV=1 | 买一/卖一盘口 |

> 注：CwInfo 数值单位为**万元**（茅台 YYSR=9070326 万≈907 亿，与 2025H1 营收吻合）；tdxstat 同名字段单位为角/元或股，印证时须做单位换算（万股×1e4=股、万元×1e4=元），但**官方命名语义一致即 L1 终止**。

## 2. 桶 A / 桶 B 分类（基于 field_dict.md 实测）

| 桶 | 范围 | 数量 | TDX/腾讯能否破解 | 依据 |
|:---|:---|:---:|:---|:---|
| **A1** | tdxstat 0–36 同源列 | 37 | ✅ 28/37 直接印证 | TDX CwInfo/ExtInfo 官方命名 |
| **A2** | tx[] 实时快照弱字段（tx[11]/[21]/[40]/[80]/[85] 等） | ~6 | ✅ 部分 | TDX BspInfo/HQMaskFlag + 腾讯 qt/westock |
| **A3** | wenda 研报/公告/新闻/宏观 | 多维 | ✅ 直出定名 | TDX `wenda_*` 工具 |
| **A4** | 财务字段（manage_fee/net_profit/total_debt…） | 13 | ✅ 部分 | TDX CwInfo + 腾讯自选股财务 |
| **B1** | 东财 ulist 专属 f 编号 | **126** | ❌ | 东方财富自有体系，TDX/腾讯不承载 |
| **B2** | 恒空/恒0 死占位符（tx[29]/[54-55]/[77-78]/[81]/[83]） | 5+ | ❌（无可破解内容） | 已确认无信息量 |
| **B3** | 计算字段（Beta tx[56]/CYQ/52周高低/TA-Lib） | 4+ | ❌ | 需基准序列/窗口计算，非实时快照对撞 |

## 3. tdxstat 0–36 → TDX 命名映射（桶 A1 第一轮对撞）

| col | 含义 | TDX 命名字段 | 判定 |
|:---:|:---|:---|:---:|
| 0 | market 市场 | BaseInfo.Setcode | ✅ L1 |
| 1 | code 代码 | BaseInfo.Code | ✅ L1 |
| 2 | 流通股本 | ExtInfo.LTGB(万×1e4=股) | ✅ L1 |
| 3 | province 省份 | ExtInfo.Addr(候选) | ⚠️ 候选 |
| 4 | 行业编码 | ExtInfo.BelongHY | ✅ L1 |
| 5 | 财报更新日 | CwInfo.GXRQ | ✅ L1 |
| 6 | 上市日期 | CwInfo.Start | ✅ L1 |
| 7 | 总股本 | ExtInfo.ZGB(万×1e4=股) | ✅ L1 |
| 8 | 国家股 | — | ❌ legacy |
| 9 | 发起人法人股 | — | ❌ legacy |
| 10 | 法人股 | — | ❌ legacy |
| 11 | B股 | — | ❌ legacy |
| 12 | H股 | —（BelongHGTAG=沪股通≠H股） | ❌ legacy |
| 13 | 职工股 | — | ❌ legacy |
| 14 | 总资产 | CwInfo.ZZC(万×1e4=元) | ✅ L1 |
| 15 | 流动资产 | CwInfo.LDZC | ✅ L1 |
| 16 | 固定资产 | CwInfo.GDZC | ✅ L1 |
| 17 | 无形资产 | CwInfo.WXZC | ✅ L1 |
| 18 | 股东户数 | CwInfo.GDRS | ✅ L1 |
| 19 | 流动负债 | CwInfo.LDFZ | ✅ L1 |
| 20 | 长期负债 | CwInfo.CPFZ | ✅ L1 |
| 21 | 资本公积金 | CwInfo.ZBGJJ | ✅ L1 |
| 22 | 净资产/股东权益 | CwInfo.JZC | ✅ L1 |
| 23 | 主营业务收入 | CwInfo.YYSR(营业收入) | ✅ L1 |
| 24 | 主营业务利润 | CwInfo.YYLR(营业利润 近似) | ⚠️ 候选 |
| 25 | 应收账款 | CwInfo.YSZK | ✅ L1 |
| 26 | 营业利润 | CwInfo.YYLR | ✅ L1 |
| 27 | 投资收益 | CwInfo.TZSY | ✅ L1 |
| 28 | 经营活动现金流 | CwInfo.JYXJL | ✅ L1 |
| 29 | 总现金流 | CwInfo.ZXJL | ✅ L1 |
| 30 | 存货 | CwInfo.CH | ✅ L1 |
| 31 | 利润总和 | CwInfo.LYZE | ✅ L1 |
| 32 | 税后利润 | CwInfo.SHLY | ✅ L1 |
| 33 | 净利润 | CwInfo.JLY | ✅ L1 |
| 34 | 未分配利润 | CwInfo.WFPLY | ✅ L1 |
| 35 | 每股净资产 BPS | ExtInfo.MGJZC | ✅ L1 |
| 36 | 保留字段2 | — | ❌ 保留 |

> 8–13 为 legacy 股本结构字段（国家股/法人股/B股/H股/职工股），现代公司已归零，TDX 实时接口不暴露命名字段 → 维持 ❌，归入桶 B（非 TDX/腾讯射程，需历史二进制解析）。

## 4. tx[] 弱字段印证（桶 A2）

| 字段 | 现状态 | TDX/腾讯印证 | 判定 |
|:---|:---|:---|:---:|
| tx[11] 买一价 | ⚠️ 疑似冗余 | TDX BspInfo.BuyP=1291.12 | ✅ 买一价（非冗余，确为买一） |
| tx[21] 卖一价 | ⚠️ 疑似冗余 | TDX BspInfo.SellP=1291.13 | ✅ 卖一价 |
| tx[40] 停牌标记 | ⚠️ L3 | TDX HQMaskFlag="7"（需停牌样本数值印证） | L3 维持 |
| tx[80] 涨速 | 候选 | TDX 未直接暴露（CalcInfo/ProInfo 无即时涨速） | 候选待定 |
| tx[85] 盘口参考价 | ⚠️ L3 | TDX Average=1294.07（均价，非盘口参考价） | L3 维持 |

> 买一/卖一由 BspInfo 实锤，建议字典将「疑似冗余」改为「✅ 买一价/卖一价（TDX BspInfo 印证）」。

## 5. 桶 B 标记（待源）

- **B1 东财 ulist 126 字段**（f1–f249 未破解段）：东方财富自有 f 编号体系，TDX/腾讯行情云均不承载，无法印证。破解须走东财 ulist 源本身（沙箱对 push2 主域拦截，已有采集 raw + 字段表可离线对撞）。**建议在 ulist 段表头标注「桶 B：待东财源」**。
- **B2 死占位符**（tx[29]/[54-55]/[77-78]/[81]/[83]）：已确认恒空/恒0，无信息量，非未破解语义。**标注「死字段·无内容」**。
- **B3 计算字段**（Beta tx[56] / CYQ 筹码 / 52周高低 / TA-Lib）：依赖宽基指数基准或窗口计算，非实时快照对撞。**标注「待基准/计算源」**。

## 6. 方法论与下一步

- **已落地**：TDX 官方命名语义终止器对 tdxstat 0–36 完成 28/37 L1 印证（与 tx[45]/[47] path A+B 同法）。
- **下一步（桶 A 续）**：① A3 wenda 字段用 `wenda_*` 直出定名；② A4 财务字段用 TDX CwInfo + 腾讯自选股财务补全；③ A2 余下 tx[] 弱字段（涨速/停牌）扩样印证。
- **桶 B**：东财 ulist 126 列为独立「东财源破解」战役，不在 TDX/腾讯射程。

> 本地提交：待本报告 + 字典小节落地后 git commit（PAT 失效仅本地）。
