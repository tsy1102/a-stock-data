# TDX 活体碰撞报告（2026-09-07）

> ⚠️ **定位说明**：本报告是 **AI 字段碰撞/破解的验证工件**，所用 `mcp__tdx-connector` 为 WorkBuddy MCP 工具，**非 `a-stock-data` 项目依赖**；项目平时 `py` 运行不具备此能力，本报告的字段映射**不进入项目运行时取数路径**。项目真正的 TDX 运行时源是 `easy_tdx`（本地 TCP，已列 `requirements.txt`）。
>
> 目的：用 **TDX 云/TQLEX 实时真值** 作为字节级锚点，与项目既有历史采集序列（东财 push2 / 腾讯 / ZHB）对撞；并据活体值确认 TDX 源字段映射，补入字典。
> 采集基线：`docs/field_verification/20260812~20260906`（18 日，含 茅台 600519 全序列）。
> 工具：`mcp__tdx-connector__tdx_quotes`、`mcp__tdx-connector__tdx_api_data`（通达信云数据服务，只读、无账户/无交易权限）。

## 一、TDX 活体锚点（3 代表股，覆盖不同涨跌幅规则）

| 股票 | 板 | Inside(内盘) | Outside(外盘) | ZTPrice | DTPrice | 主力净流入(元) | Wtb(委比) | BelongHY |
|---|---|---|---|---|---|---|---|---|
| 茅台 600519 | 沪主板 | 17650 | 27766 | 1428.77 | 1168.99 | 444,347,136 | -55.38 | 82102 |
| 宁德 300750 | 创业板 | 102293 | 125088 | 419.40 | 279.60 | 869,887,000 | 82.34 | 83002 |
| 中芯 688981 | 科创板 | 169166 | 143552 | 148.64 | 99.10 | -264,739,840 | -46.19 | 84001 |

## 二、涨停/跌停价规则校验（中优项 TDX 计算兜底的正确性实证）

| 股票 | 昨收(Close) | 规则 | 期望 | TDX ZTPrice | 结论 |
|---|---|---|---|---|---|
| 茅台 | 1298.88 | ×1.10(主板) | 1428.768→1428.77 | 1428.77 | ✅ |
| 宁德 | 349.50 | ×1.20(创业板) | 419.40 | 419.40 | ✅ |
| 中芯 | 123.87 | ×1.20(科创板) | 148.644→148.64 | 148.64 | ✅ |

→ TDX `ExtInfo.ZTPrice/DTPrice` 与 `get_price_limits()` 计算口径一致，且**自动区分 10%/20% 板**，可作腾讯[47/48] 之后、push2 f51/f52 之前的源无关兜底层。

## 三、茅台纵向锚点一致性（TDX 活体 vs 历史采集 vs 腾讯）

| 字段 | TDX 活体(09-07) | TDX 历史 raw(09-06) | 腾讯(09-06) | 结论 |
|---|---|---|---|---|
| 涨停价 | 1428.77 | 1428.77 | 1428.77([47]) | 三方一致 ✅ |
| 跌停价 | 1168.99 | 1168.99 | 1168.99([48]) | 三方一致 ✅ |
| 量比 | 2.0626 | 2.06 | 2.06([49]) | 一致 ✅ |
| 内盘 | 17650 | —(采集未抽 s_vol) | 18005([8]) | **总量同(45416手)，分拆差 355 手** |
| 外盘 | 27766 | — | 27411([7]) | 同上（TDX 比腾讯多计 355 手于外盘） |
| 主力净流入(元) | 444,347,136 | — | — | TDX 独立锚；见四 |
| 总资产 | 30905078万(CwInfo.ZZC) | 3090507840000元 | — | 同值(单位不同) ✅ |

**发现 #1（内盘/外盘口径差）**：TDX 与腾讯的 `内盘+外盘` 均等于总成交量 45416 手，但内/外拆分在两者间差恰好 355 手（约 0.8%）。属**主动买卖归类边界差异**，非数据错误。→ canonical `s_vol/b_vol` 取 TDX 值时内部自洽（与成交量闭合），但与腾讯不完全逐手相等，报告中若并列两源需标注"口径差 ~0.8%"。

## 四、主力净流入：TDX 独立锚 + ZHB 竞价额再证伪

| 源 | 茅台值 | 性质 |
|---|---|---|
| TDX 活体 `ProInfo.主力资金净流入（元）` | 444,347,136 | 主力净流入（TDX 盘口口径） |
| ZHB `main_net_buy_amount` | 2325.2（万元级，≈2.3e7 元） | **竞价额**（2026-08-14 实锤，非主力净流入） |
| push2(东财 f137) | 09-06 全股票 "circuit-broken" | 当日不可用 |

**发现 #2**：2026-09-06 采集日，东财 push2 对**全部股票熔断**——印证用户"push2 封禁厉害"的判断。此日 TDX 活体是唯一可得的主力净流入锚点。
**发现 #3（ZHB 再证伪）**：ZHB `main_net_buy_amount=2325.2` 量级与 TDX `444,347,136` 元差两个数量级，确为竞价额，绝不可并入主力净买入额（字典行 3104 已订正）。

> 注意：TDX 主力净流入与东财 f137 为**不同计算口径**（TDX 盘口逐单 vs 东财 L2 大单），绝对额会有差异。二者严格等价性需在 push2 可用日做 1 日多点对撞确认，本环境当日 push2 熔断故未能完成。

## 五、TDX 源字段目录（"表头/各种信息"能力边界）

`tdx_quotes` 返回**应用层（星云/通达信云 API）命名字段**，非 TCP 字节偏移——即"字段目录发现"，非字节级逆向（字节级已由 easy_tdx 净室实现完成）。完整 sections：

- **HQInfo**：HQDate/HQTime/Close/Open/MaxP/MinP/Now/Volume/Amount/**Inside**/**Outside**/InOutFlag/Yield/Jjjz/CJBS/**LB**(量比)/HSL/Average/PHVolume/RestVol
- **ExtInfo**：**ZTPrice**/**DTPrice**/ZGB/LTGB/MGSY/MGJZC/股息率/ZSZ/SYL/Addr/**BelongHY**(通达信行业码)/HYZAF/BelongHS300/BelongRZRQ/BelongHGTAG/FreeLtgb
- **CwInfo**（财报快照，约 30 字段）：LTGB/ZGB/Addr/BelongHY/GXRQ/Start/MGSY2/**ZZC**(总资产,万)/**LDZC**/**GDZC**/**WXZC**/GDRS/**LDFZ**/**CPFZ**/ZBGJJ/**JZC**(净资产)/YYSR/YYCB/YSZK/YYLR/TZSY/JYXJL/ZXJL/CH/LYZE/SHLY/JLY/WFPLY/MGJZC2/CagePriceUp/CagePriceDown/ZTStatus1/ZTStatus2/MoreHy/SafeValue/IPOPrice/ShinePoint/IPOTQPrice
- **ProInfo**：UnderlyMarket/UnderlyCode/NowVol/zangsu/HQMaskFlag/**资金净流入（元）**/**主力资金净流入（元）**/**Wtb**(委比)/20日涨幅/年初至今/静态市盈率/TTM市盈率/HisHigh/HisLow/ch/Implied/昨日涨幅/3日涨幅/60日涨幅/5日涨幅/10日涨幅/LLPrice/OpenAmo/ConZAFDateNum
- **CalcInfo**：CAZAF/CAZDJ/CAZF/CAKPHSZ/CALTZZ/CAHSZ/CALTZ/CAKP/CAZG/CAZD/CAJJ/CAST/CAHTB/CAGJB/CAJZDBP/CAZDBP（约 15 个衍生计算指标）
- **BspInfo**：5 档买卖盘（BuyP/SellP/BuyV/SellV）

F10（`tdx_api_data`）另返回**带显式 headers 的结构化 ResultSet**（如资金流向表 9 列：日期/主力净额金额(元)/主力净额占比(%)/超大单净买入金额(元)/大单净买入金额(元)/主买净额金额(元)/收盘价），可直接枚举 TDX 有哪些数据表。

## 六、对字典工程的输入

1. §12.8.12e 新增 **§12.8.12f TDX(云/TQLEX) 源字段映射**——上表即"TDX 云字段名 → canonical 字段名"的权威映射，补入字典源维度。
2. **BelongHY=82102（茅台）是通达信行业码，非申万**（通达信白酒码 82102，申万白酒为不同编码）。再次确认：TDX 无可挖申万列，东财 `em_industry_map_l2` 仍唯一申万源，不可翻转 primary/fallback。
3. 内盘/外盘口径差（~0.8%）记入字典"源差异"注记，避免后续误判为数据错误。

## 七、结论

- TDX 云真值**可作字节级锚点**：涨停/跌停价、量比、财报总额三方一致，可信。
- 主力净流入维度上，TDX 是 push2 熔断时的**唯一活体锚**，但需择 push2 可用日做口径等价性对撞。
- 历史 茅台连续序列 + ZHB 历史序列，为本碰撞提供了纵向基准：TDX 锚点经"活体 vs 历史"双重确认，再叠加东财/腾讯/ZHB 多源，形成"时间×源"二维验证网格。
