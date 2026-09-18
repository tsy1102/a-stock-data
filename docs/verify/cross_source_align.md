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
