# 未知字段破解整合报告（20260920）

> 生成：2026-09-20 12:48 ｜ 数据源：通达信本地仓库 field_verification

> **方法**：registry 已验证字段（48 通用 EM f 字段 + 6 源特定 + 139 跨源映射）为**权威种子**；ZHB 语义锚与对撞等价图为**候选证据**。
> 沿等价图传播语义，仅输出**新赋义**；与外部锚冲突者单列**需复核**，不静默覆盖。

## 摘要

- 输入：碰撞 L1=753 / L4=1072；权威种子=585；跨源映射=139；ZHB 锚=6
- **新破解未验证字段：100 个**（置信降序）
- 各源破解分布：{'em_hot': 1, 'exchange': 1, 'fuyao': 1, 'push2': 5, 'push2_full': 4, 'push2ex': 2, 'sina': 19, 'tdx': 8, 'tencent': 30, 'ulist239': 29}
- **与 registry 冲突需复核：17 个**
- 仍残余无语义锚：306 个
- 引擎新增定案（in_registry 复用）：33

## 1、高置信破解（置信≥90%，根植 registry 已验证）


| 源.字段 | 破解含义 | 置信 | 证据链 |
|---|---|---|---|
| em_hot.pct | 涨跌幅 | 95% | direct←push2_full.f170 |
| exchange.zqjc | 股票名称 | 95% | direct←push2_full.f58 |
| fuyao.auction_price | 开盘价 | 95% | direct←push2.f46 |
| push2.f164 | 市盈率(TTM) | 95% | direct←eltdx.pe_ttm |
| push2.f174 | 52周最高价 | 95% | direct←zhb.high_52w |
| push2.f175 | 52周最低价 | 95% | direct←zhb.low_52w |
| push2_full.f164 | 市盈率(TTM) | 95% | direct←eltdx.pe_ttm |
| push2_full.f174 | 52周最高价 | 95% | direct←zhb.high_52w |
| push2_full.f175 | 52周最低价 | 95% | direct←zhb.low_52w |
| push2_full.f198 | 东财板块代码 | 95% | direct←push2.f198 |
| push2ex.amount | 成交额 | 95% | direct←fuyao.turnover |
| push2ex.zt_continuous | 涨停次数 | 95% | direct←zhb.zt_count |
| sina.[0] | 股票名称 | 95% | direct←push2.f58 |
| sina.[11] | 买一价 | 95% | direct←tdx.bid1 |
| sina.[13] | 买二价 | 95% | direct←tdx.bid2 |
| sina.[15] | 买三价 | 95% | direct←tdx.bid3 |
| sina.[17] | 买四价 | 95% | direct←tdx.bid4 |
| sina.[19] | 买五价 | 95% | direct←tdx.bid5 |
| sina.[1] | 开盘价 | 95% | direct←fuyao.open_price |
| sina.[21] | 卖一价 | 95% | direct←tdx.ask1 |
| sina.[23] | 卖二价 | 95% | direct←tdx.ask2 |
| sina.[25] | 卖三价 | 95% | direct←tdx.ask3 |
| sina.[27] | 卖四价 | 95% | direct←tdx.ask4 |
| sina.[29] | 卖五价 | 95% | direct←tdx.ask5 |
| sina.[3] | 现价(重复列) | 95% | direct←push2.f179 |
| sina.[4] | 最高价 | 95% | direct←push2_full.f44 |
| sina.[5] | 最低价 | 95% | direct←fuyao.low_price |
| sina.[6] | 买一价 | 95% | direct←tdx.bid1 |
| sina.[7] | 卖一价 | 95% | direct←tdx.ask1 |
| sina.[8] | 成交量 | 95% | direct←fuyao.volume |
| sina.[9] | 成交额 | 95% | direct←push2.f48 |
| tdx.amplitude_pct | 振幅% | 95% | direct←push2_full.f171 |
| tdx.h_gu | 其他权益净资产 | 95% | direct←zhb.other_qy_jzc |
| tdx.liutong_guben | 流通股本 | 95% | direct←push2_full.f85 |
| tdx.liutongguben | 流通股本 | 95% | direct←push2_full.f85 |
| tdx.turnover_pct | 换手率% | 95% | direct←push2_full.f168 |
| tdx.vol_ratio | 量比 | 95% | direct←push2.f50 |
| tdx.zong_guben | 总股本 | 95% | direct←push2_full.f84 |
| tdx.zongguben | 总股本 | 95% | direct←push2_full.f84 |
| tencent.[11] | 买二价 | 95% | direct←tdx.bid2 |
| tencent.[13] | 买三价 | 95% | direct←tdx.bid3 |
| tencent.[15] | 买四价 | 95% | direct←tdx.bid4 |
| tencent.[17] | 买五价 | 95% | direct←tdx.bid5 |
| tencent.[19] | 卖一价 | 95% | direct←tdx.ask1 |
| tencent.[1] | 股票名称 | 95% | direct←push2_full.f58 |
| tencent.[21] | 卖二价 | 95% | direct←tdx.ask2 |
| tencent.[23] | 卖三价 | 95% | direct←tdx.ask3 |
| tencent.[25] | 卖四价 | 95% | direct←tdx.ask4 |
| tencent.[27] | 卖五价 | 95% | direct←tdx.ask5 |
| tencent.[31] | 涨跌额 | 95% | direct←push2_full.f169 |
| tencent.[32] | 涨跌幅 | 95% | direct←push2_full.f170 |
| tencent.[33] | 最高价 | 95% | direct←eltdx.high_price |
| tencent.[34] | 最低价 | 95% | direct←push2_full.f45 |
| tencent.[38] | 换手率% | 95% | direct←push2_full.f168 |
| tencent.[39] | 市盈率(TTM) | 95% | direct←eltdx.pe_ttm |
| tencent.[3] | 现价(重复列) | 95% | direct←push2.f179 |
| tencent.[41] | 最高价 | 95% | direct←push2.f44 |
| tencent.[42] | 最低价 | 95% | direct←tdx.low |
| tencent.[43] | 振幅% | 95% | direct←push2_full.f171 |
| tencent.[49] | 量比 | 95% | direct←push2.f50 |
| tencent.[57] | 成交额 | 95% | direct←tdx.amount_wan |
| tencent.[5] | 开盘价 | 95% | direct←eltdx.open_price |
| tencent.[67] | 52周最高价 | 95% | direct←zhb.high_52w |
| tencent.[68] | 52周最低价 | 95% | direct←zhb.low_52w |
| tencent.[71] | 资金流衍生指标(≡60日涨跌幅, 见[71]/ulist f24) | 95% | direct←push2.f121 |
| tencent.[72] | 流通股本 | 95% | direct←push2_full.f85 |
| tencent.[73] | 总股本 | 95% | direct←push2_full.f84 |
| tencent.[76] | 流通股本 | 95% | direct←push2_full.f85 |
| tencent.[9] | 买一价 | 95% | direct←tdx.bid1 |
| ulist239.f10 | 量比 | 95% | direct←push2.f50 |
| ulist239.f100 | 行业名称 | 95% | direct←push2.f127 |
| ulist239.f102 | 地域板块名称 | 95% | direct←push2_full.f128 |
| ulist239.f107 | 市场/板块状态标记（≡ ulist:f107） | 95% | direct←push2.f118 |
| ulist239.f115 | 市盈率(TTM) | 95% | direct←eltdx.pe_ttm |
| ulist239.f124 | 当日收盘/最后行情时间戳 | 95% | direct←push2.f86 |
| ulist239.f13 | 市场标记（布尔 0/1，北交=0） | 95% | direct←push2.f107 |
| ulist239.f139 | 市场类型枚举 | 95% | direct←push2_full.f182 |
| ulist239.f14 | 股票名称 | 95% | direct←push2_full.f58 |
| ulist239.f142 | 买二价 | 95% | direct←tdx.bid2 |
| ulist239.f143 | 卖二价 | 95% | direct←tdx.ask2 |
| ulist239.f144 | 现价 | 95% | direct←push2_full.f43 |
| ulist239.f15 | 最高价 | 95% | direct←tdx.high |
| ulist239.f17 | 开盘价 | 95% | direct←push2.f46 |
| ulist239.f19 | 板级枚举 | 95% | direct←push2_full.f112 |
| ulist239.f2 | 现价(重复列) | 95% | direct←push2_full.f179 |
| ulist239.f24 | 资金流衍生指标(≡60日涨跌幅, 见[71]/ulist f24) | 95% | direct←push2_full.f121 |
| ulist239.f25 | 资金流衍生指标 | 95% | direct←push2_full.f122 |
| ulist239.f26 | 上市日期 | 95% | direct←push2_full.f189 |
| ulist239.f27 | 市场标记（布尔 0/1，北交=0） | 95% | direct←push2_full.f107 |
| ulist239.f3 | 涨跌幅 | 95% | direct←push2.f170 |
| ulist239.f31 | 买一价 | 95% | direct←tdx.bid1 |
| ulist239.f32 | 卖一价 | 95% | direct←tdx.ask1 |
| ulist239.f37 | 加权净资产收益率（最新报告期 %） | 95% | direct←push2.f173 |
| ulist239.f38 | 总股本 | 95% | direct←push2_full.f84 |
| ulist239.f39 | 流通股本 | 95% | direct←push2_full.f85 |
| ulist239.f4 | 涨跌额 | 95% | direct←push2.f169 |
| ulist239.f7 | 振幅% | 95% | direct←push2.f171 |
| ulist239.f8 | 换手率% | 95% | direct←push2_full.f168 |
| push2.f124 | 其他权益净资产(万元?) | 90% | ZHB语义锚 |
| push2.f134 | 其他权益净资产(万元?) | 90% | ZHB语义锚 |

（共 100 个）

## 2、ZHB 语义锚直击（候选，按命中率）


| 目标字段 | ZHB 锚语义 | 命中率 | 备注 |
|---|---|---|---|
| push2.f122 | 年初至今涨跌幅% | 95% | 高 |
| push2.f124 | 其他权益净资产(万元?) | 90% | 高 |
| push2.f134 | 其他权益净资产(万元?) | 90% | 高 |
| push2.f107 | 其他权益净资产(万元?) | 60% | 弱 |
| ulist239.f13 | 其他权益净资产(万元?) | 60% | 弱 |
| ulist239.f97 | 其他权益净资产(万元?) | 50% | 弱 |
## 3、与 registry 冲突 — 需人工复核（不自动定案）


> 含术语/字形变体（如 收盘/收价、总/流通市值，以及跨源同义字形如 市场标记/市场标记、股票代码/股票代码、昨收盘/昨收盘——后者为不同 codepoint 的同概念 artefact），均为需人工归一项；Jaccard>0.7 的近似对已过滤。

| 源.字段 | registry 已验证义 | 挑战语义 | 来源 | 置信 |
|---|---|---|---|---|
| push2.f122 | 资金流衍生指标 | 年初至今涨跌幅% | ZHB语义锚 | 95% |
| push2ex.total_value | 总市值 | 流通市值 | multi-edge:push2.f116|push2_full.f117 | 80% |
| ulist239.f12 | 股票代码 | 代码 / 简称（深市） | multi-edge:push2.f57|exchange.zqdm | 80% |
| push2ex.limit_fund | 市场标记（布尔 0/1，北交=0） | 买二价 | multi-edge:push2.f107|tdx.bid2 | 80% |
| push2ex.limit_count | 市场标记（布尔 0/1，北交=0） | 买三价 | multi-edge:push2.f107|tdx.bid3 | 80% |
| ulist239.f200 | 买二价 | 买五价 | multi-edge:tdx.bid2|tdx.bid5 | 80% |
| tdx.hgu | 买二价 | 卖三价 | multi-edge:tdx.bid2|tdx.ask3 | 80% |
| tdx.bgu | 买二价 | 买五价 | multi-edge:tdx.bid2|tdx.bid5 | 80% |
| ulist239.f231 | 卖三价 | 买三价 | multi-edge:tdx.ask3|tdx.bid3 | 80% |
| ulist239.f190 | 卖三价 | 买三价 | multi-edge:tdx.ask3|tdx.bid3 | 80% |
## 4、残余未破解字段（需新源/人工）


按源：ulist239:83，push2:62，tdx:62，push2_full:54，tencent:19，em_fund_flow:14，push2ex:5，fuyao:3，sina:2，em_hot:1，exchange:1

### 完整残余（前 80）

- em_fund_flow.f135
- em_fund_flow.f136
- em_fund_flow.f137
- em_fund_flow.f139
- em_fund_flow.f140
- em_fund_flow.f141
- em_fund_flow.f142
- em_fund_flow.f143
- em_fund_flow.f144
- em_fund_flow.f145
- em_fund_flow.f146
- em_fund_flow.f147
- em_fund_flow.f148
- em_fund_flow.f149
- em_hot.price
- exchange.dqrq
- fuyao.pcf_ttm
- fuyao.pre_close_price
- fuyao.ps_ttm
- push2.f104
- push2.f105
- push2.f108
- push2.f109
- push2.f119
- push2.f120
- push2.f123
- push2.f126
- push2.f129
- push2.f131
- push2.f135
- push2.f136
- push2.f137
- push2.f138
- push2.f139
- push2.f140
- push2.f141
- push2.f142
- push2.f143
- push2.f144
- push2.f145
- push2.f146
- push2.f147
- push2.f148
- push2.f149
- push2.f153
- push2.f154
- push2.f160
- push2.f161
- push2.f162
- push2.f163
- push2.f165
- push2.f166
- push2.f167
- push2.f176
- push2.f177
- push2.f180
- push2.f181
- push2.f183
- push2.f184
- push2.f185
- push2.f186
- push2.f187
- push2.f188
- push2.f190
- push2.f191
- push2.f192
- push2.f193
- push2.f194
- push2.f195
- push2.f196
- push2.f197
- push2.f250
- push2.f49
- push2.f51
- push2.f52
- push2.f55
- push2.f59
- push2.f71
- push2.f78
- push2.f80
- …（其余 226 略）
## 5、方法学与风险


- **权威优先**：registry `verified` 字段为种子，外部锚仅作候选；冲突显式列出，不静默覆盖（符合项目「第三方报告处理铁律」）。
- **同号异义防护**：ulist239 与 push2 跨编号同义（如 ulist.f1↔push2.f59）经 registry `mappings` 显式桥接；code-agnostic 兜底仅限 EM push2 系源，避免污染 ulist。
- **置信度**：specific=100% / code=95% / 直接赋义=95% / ZHB=实测命中率；多跳传播已禁用（避免 price-like 字段污染）。
- **未回写字典**：本报告为发现性输出，定案须经 field_dict.md 订正 → sanctioned 管线 ingest（G1 闸门）。
- **残余**：多为 microstructure / 资金流细分比率块（f44-f49、f88-f95、f97-f99、f103/f107 部分、f111-f115、f122/f124/f127/f129-f134、tencent[56]/[85]/[86]），需行情中心板页或新源方可突破。
