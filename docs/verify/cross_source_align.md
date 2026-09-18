# 跨源字段等价对齐表（通用存储，sanctioned 入库）

> 用途：承载非 ulist239↔push2 的跨源等价/同义关系（fuyao/tdx/eltdx/zhb/tencent/push2/push2_full/sina 任意源对）。
> 经 extract_registry.py 解析入 field_registry.json mappings，collide 据 load_registry_state 标 in_registry 后 durable 定案（不再每轮重新发现）。
> 来源：docs/field_verification/20260918/20260918_crack_report.md（collide 7 天窗口 L1 候选，hit≥0.92·5d，四铁律全过）。
> 格式：`| 源A.字段A | 源B.字段B | 关系 | 中文语义 | 证据 |`
> 源前缀短别名：fuyao / tdx / eltdx / zhb / tencent / push2 / push2_full / ulist239 / sina
> 注：fuyao/tdx/eltdx/zhb 适配层字段因 registered_field_sets 收录形态差异，verified 状态定案见 field_dict.md 附录；本表确保 collide in_registry 固化等价关系。

| 源A.字段A | 源B.字段B | 关系 | 中文语义 | 证据 |
|---|---|---|---|---|
| fuyao.snapshot.price_change | push2.f169 | 异号同义 | 涨跌额 | 20260918 对撞 L1·hit=1.0·5d |
| fuyao.snapshot.price_change_ratio_pct | tdx.quote_full.change_pct | 异号同义 | 涨跌幅 | 20260918 对撞 L1·hit=1.0·5d |
| fuyao.snapshot.turnover | push2.f48 | 异号同义 | 成交额 | 20260918 对撞 L1·hit=1.0·5d |
| push2.f162 | tencent[52] | 异号同义 | 市盈率(动态) | 20260918 对撞 L1·hit=1.0·5d |
| push2.f163 | tencent[53] | 异号同义 | 市盈率(静态/年报 LYR) | 20260918 对撞 L1·hit=1.0·5d |
| push2.f51 | tencent[47] | 异号同义 | 涨停价 | 20260918 对撞 L1·hit=1.0·5d |
| push2.f52 | tencent[48] | 异号同义 | 跌停价 | 20260918 对撞 L1·hit=1.0·5d |
| push2.f71 | tencent[51] | 异号同义 | 均价 | 20260918 对撞 L1·hit=1.0·5d |
| push2_full.f162 | tencent[52] | 异号同义 | 市盈率(动态) | 20260918 对撞 L1·hit=1.0·5d |
| push2_full.f163 | tencent[53] | 异号同义 | 市盈率(静态/年报 LYR) | 20260918 对撞 L1·hit=1.0·5d |
| push2_full.f51 | tencent[47] | 异号同义 | 涨停价 | 20260918 对撞 L1·hit=1.0·5d |
| push2_full.f52 | tencent[48] | 异号同义 | 跌停价 | 20260918 对撞 L1·hit=1.0·5d |
| push2_full.f71 | tencent[51] | 异号同义 | 均价 | 20260918 对撞 L1·hit=1.0·5d |
| sina[23] | tencent[21] | 异号同义 | 年初至今涨跌幅(YTD) | 20260918 对撞 L1·hit=1.0·5d |
| tdx.quote_full.ask1 | sina[7] | 异号同义 | 1日涨跌幅 | 20260918 对撞 L1·hit=1.0·5d |
| tdx.quote_full.bid1 | sina[6] | 异号同义 | 涨跌幅 | 20260918 对撞 L1·hit=1.0·5d |
| tdx.quote_full.change_amt | push2.f169 | 异号同义 | 涨跌额 | 20260918 对撞 L1·hit=1.0·5d |
| tencent[32] | push2.f170 | 异号同义 | 涨跌幅 | 20260918 对撞 L1·hit=1.0·5d |
| tencent[63] | push2.f119 | 异号同义 | 5日涨跌幅% | 20260918 对撞 L1·hit=1.0·5d |
| tencent[72] | push2.f85 | 异号同义 | 流通股本 | 20260918 对撞 L1·hit=1.0·5d |
| tencent[73] | push2.f84 | 异号同义 | 总股本 | 20260918 对撞 L1·hit=1.0·5d |
| tencent[76] | push2.f85 | 异号同义 | 流通股本 | 20260918 对撞 L1·hit=1.0·5d |
| ulist239.f10 | tencent[49] | 异号同义 | 量比 | 20260918 对撞 L1·hit=1.0·5d |
| ulist239.f114 | tencent[53] | 异号同义 | 市盈率(静态/年报 LYR) | 20260918 对撞 L1·hit=1.0·5d |
| ulist239.f7 | tencent[43] | 异号同义 | 振幅% | 20260918 对撞 L1·hit=1.0·5d |
| ulist239.f8 | tencent[38] | 异号同义 | 换手率% | 20260918 对撞 L1·hit=1.0·5d |
| eltdx.quote_snapshot.amount | push2.f48 | 异号同义 | 成交额 | 20260918 对撞 L1·hit=1.0·4d |
| tencent[70] | push2.f120 | 异号同义 | 20日涨跌幅% | 20260918 对撞 L1·hit=0.98·5d |
| ulist239.f142 | sina[13] | 异号同义 | 板级枚举计数 | 20260918 对撞 L1·hit=0.98·5d |
| ulist239.f211 | tencent[10] | 异号同义 | 股息率 | 20260918 对撞 L1·hit=0.98·5d |
| ulist239.f31 | sina[6] | 异号同义 | 涨跌幅 | 20260918 对撞 L1·hit=0.98·5d |
| push2.f164 | tencent[39] | 异号同义 | PE(TTM) | 20260918 对撞 L1·hit=0.97·5d |
| push2_full.f164 | tencent[39] | 异号同义 | PE(TTM) | 20260918 对撞 L1·hit=0.97·5d |
| ulist239.f115 | tencent[39] | 异号同义 | PE(TTM) | 20260918 对撞 L1·hit=0.97·5d |
| push2.f167 | tencent[46] | 异号同义 | PB | 20260918 对撞 L1·hit=0.95·5d |
| push2_full.f167 | tencent[46] | 异号同义 | PB | 20260918 对撞 L1·hit=0.95·5d |
| ulist239.f143 | tencent[21] | 异号同义 | 年初至今涨跌幅(YTD) | 20260918 对撞 L1·hit=0.94·5d |
| ulist239.f212 | tencent[20] | 异号同义 | 60日涨跌幅 | 20260918 对撞 L1·hit=0.94·5d |
| ulist239.f32 | sina[7] | 异号同义 | 1日涨跌幅 | 20260918 对撞 L1·hit=0.94·5d |
| tencent[71] | push2.f121 | 异号同义 | 60日涨跌幅% | 20260918 对撞 L1·hit=0.92·5d |

## 二、补齐候选（20260918 全量 49 条 · 含 6 条原排除项经黄金锚复核）

> 以下为 20260918 对撞 49 条 L1 候选中、首轮未入上表（§一）的补齐项；其中 #4/#22/#33/#34/#36 为原 6 条排除项，经**双黄金锚**（fuyao 官网锚 / 东财官网锚）复核后定案（#19=`tencent[23]` 复核为证伪/丢弃，见 §三）。
> 黄金锚复核依据：`docs/verify/eastmoney_website_anchor.md:265`（f175=52周最低、腾讯.idx68、zhb.low_52w）、`docs/verify/tencent_verify.md:20`（tx[69]≡ulist f160=区间累计涨幅类）、`docs/field_dict.md:1370/3527/3591`（sina[8]=成交量、snapshot.volume≡sina[8] 1:1）。
> 关键修正：报告 `20260918_crack_report.md` 对 #4 锚义误标为 `change_pct_2d`（实为成交量）、对 #22/#33/#34 锚义误标 `tx[69]`（实为 52周最低）、对 #36 锚义误标 EPS（实为 10日涨跌幅）——均经黄金锚回订正。

| 源A.字段A | 源B.字段B | 关系 | 中文语义 | 证据 |
|---|---|---|---|---|
| fuyao.snapshot.volume | sina[8] | 异号同义 | 成交量 | 20260918 对撞 L1·hit=1.0·5d（黄金锚 field_dict §12.2：sina[8]=成交量 ✅L1，snapshot.volume≡sina[8] 1:1） |
| tencent[68] | push2.f175 | 异号同义 | 52周最低 | 20260918 对撞 L1·hit=1.0·5d（黄金锚 eastmoney_website_anchor f175=52周最低） |
| zhb.full.low_52w | push2.f175 | 异号同义 | 52周最低 | 20260918 对撞 L1·hit=1.0·5d（黄金锚 eastmoney_website_anchor：zhb.low_52w=52周最低） |
| zhb.stat2.low_52w | push2.f175 | 异号同义 | 52周最低 | 20260918 对撞 L1·hit=1.0·5d（黄金锚 eastmoney_website_anchor：zhb.low_52w=52周最低） |
| tencent[69] | ulist239.f160 | 异号同义 | 10日涨跌幅 | 20260918 对撞 L1·hit=0.99·5d（黄金锚 tencent_verify tx[69]≡ulist f160=区间累计涨幅类/10日涨跌幅） |
| ulist239.f13 | push2.f110 | 异号同义 | 市场标记（布尔 0/1，北交=0） | 20260918 对撞 L1·hit=1.0·5d |
| ulist239.f19 | push2.f112 | 异号同义 | 板级枚举 | 20260918 对撞 L1·hit=1.0·5d |
| ulist239.f27 | push2.f110 | 异号同义 | 市场标记（布尔 0/1，北交=0） | 20260918 对撞 L1·hit=1.0·5d |

## 三、已排除候选（证伪/丢弃，不落字段，仅作回归护栏备案）

- `tencent[23]` → `sina[25]`：原对撞判为数值巧合/证伪（报告 `20260918_crack_report.md` §二 row19 标注"*(丢弃)*"），经双黄金锚复核维持**证伪**——不写入 mappings（遵循治理铁律：证伪固化成护栏、不落成字段）。

