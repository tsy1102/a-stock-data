# L4 真存疑对 — 待累积清单（2026-09-24 对撞）

> 本清单为 L4 中**未达四铁律**的 324 条真存疑对，本轮**不晋级** durable 表，待后续交易日累积后自动升 L1。
> 其中 A类（overall≥0.9 仅缺天数）112 条，B类（命中率<0.9）212 条。

## A类：overall≥0.9 但 days_ge<3（再累积 1–2 个交易日即达 L1）— 112 条

| 左字段 | 右字段 | 命中率 | 已达天数(days_ge) | 还差天数 | 实际采集日数 |
|---|---|---|---|---|---|
| `push2_full.f46` | `eltdx.shortline.open_price` | 100.0% | 2 | 1 | 2 |
| `push2_full.f50` | `tdx.quote_full.vol_ratio` | 100.0% | 2 | 1 | 2 |
| `push2_full.f52` | `tdx.quote_full.limit_down_price` | 100.0% | 2 | 1 | 2 |
| `push2_full.f60` | `eltdx.shortline.pre_close` | 100.0% | 2 | 1 | 2 |
| `push2_full.f84` | `tdx.finance_info.zong_guben` | 100.0% | 2 | 1 | 2 |
| `push2_full.f84` | `tdx.finance_info.zongguben` | 100.0% | 2 | 1 | 2 |
| `push2_full.f85` | `tdx.finance_info.liutong_guben` | 100.0% | 2 | 1 | 2 |
| `push2_full.f85` | `eltdx.shortline.float_shares` | 100.0% | 2 | 1 | 2 |
| `push2_full.f163` | `tdx.quote_full.pe_lyr` | 100.0% | 2 | 1 | 2 |
| `push2_full.f168` | `tdx.quote_full.turnover_pct` | 100.0% | 2 | 1 | 2 |
| `push2_full.f171` | `tdx.quote_full.amplitude_pct` | 100.0% | 2 | 1 | 2 |
| `tdx.quote_full.rise_speed` | `tdx.rise_speed` | 100.0% | 2 | 1 | 2 |
| `tdx.rise_speed` | `tdx.quote_full.rise_speed` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.liutong_guben` | `push2_full.f85` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.liutong_guben` | `tdx.finance_info.liutongguben` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.liutong_guben` | `tencent[72]` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.liutong_guben` | `tencent[76]` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.liutong_guben` | `ulist239.f39` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.zong_guben` | `push2_full.f84` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.zong_guben` | `tdx.finance_info.zongguben` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.zong_guben` | `tencent[73]` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.zong_guben` | `ulist239.f38` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.guojia_gu` | `tdx.finance_info.guojiagu` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.faqiren_faren_gu` | `tdx.finance_info.faqirenfarengu` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.faren_gu` | `tdx.finance_info.farengu` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.b_gu` | `tdx.finance_info.bgu` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.h_gu` | `tdx.finance_info.hgu` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.zhigong_gu` | `tdx.finance_info.zhigonggu` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.gudong_renshu` | `tdx.finance_info.gudongrenshu` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.zong_zichan` | `tdx.finance_info.zongzichan` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.liudong_zichan` | `tdx.finance_info.liudongzichan` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.guding_zichan` | `tdx.finance_info.gudingzichan` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.wuxing_zichan` | `tdx.finance_info.wuxingzichan` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.liudong_fuzhai` | `tdx.finance_info.liudongfuzhai` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.changqi_fuzhai` | `tdx.finance_info.changqifuzhai` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.ziben_gongjijin` | `tdx.finance_info.zibengongjijin` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.jing_zichan` | `tdx.finance_info.jingzichan` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.zhuying_shouru` | `tdx.finance_info.zhuyingshouru` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.zhuying_lirun` | `tdx.finance_info.zhuyinglirun` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.yingshou_zhangkuan` | `tdx.finance_info.yingshouzhangkuan` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.yingye_lirun` | `tdx.finance_info.yingyelirun` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.touzi_shouyu` | `tdx.finance_info.touzishouyu` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.jingying_xianjinliu` | `tdx.finance_info.jingyingxianjinliu` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.zong_xianjinliu` | `tdx.finance_info.zongxianjinliu` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.lirun_zonghe` | `tdx.finance_info.lirunzonghe` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.shuihou_lirun` | `tdx.finance_info.shuihoulirun` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.jing_lirun` | `tdx.finance_info.jinglirun` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.weifen_lirun` | `tdx.finance_info.weifenlirun` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.meigujing_zichan` | `tdx.finance_info.meigujingzichan` | 100.0% | 2 | 1 | 2 |
| `tdx.finance_info.weifenlirun` | `tdx.finance_info.weifen_lirun` | 100.0% | 2 | 1 | 2 |
| `ulist239.f7` | `tdx.quote_full.amplitude_pct` | 100.0% | 2 | 1 | 2 |
| `ulist239.f8` | `tdx.quote_full.turnover_pct` | 100.0% | 2 | 1 | 2 |
| `ulist239.f10` | `tdx.quote_full.vol_ratio` | 100.0% | 2 | 1 | 2 |
| `ulist239.f38` | `tdx.finance_info.zong_guben` | 100.0% | 2 | 1 | 2 |
| `ulist239.f38` | `tdx.finance_info.zongguben` | 100.0% | 2 | 1 | 2 |
| `ulist239.f39` | `tdx.finance_info.liutong_guben` | 100.0% | 2 | 1 | 2 |
| `ulist239.f114` | `tdx.quote_full.pe_lyr` | 100.0% | 2 | 1 | 2 |
| `push2.f50` | `tdx.quote_full.vol_ratio` | 100.0% | 2 | 1 | 2 |
| `push2.f52` | `tdx.quote_full.limit_down_price` | 100.0% | 2 | 1 | 2 |
| `push2.f163` | `tdx.quote_full.pe_lyr` | 100.0% | 2 | 1 | 2 |
| `push2.f168` | `tdx.quote_full.turnover_pct` | 100.0% | 2 | 1 | 2 |
| `push2.f171` | `tdx.quote_full.amplitude_pct` | 100.0% | 2 | 1 | 2 |
| `tdx.quote_full.turnover_pct` | `push2_full.f168` | 100.0% | 2 | 1 | 2 |
| `tdx.quote_full.turnover_pct` | `ulist239.f8` | 100.0% | 2 | 1 | 2 |
| `tdx.quote_full.turnover_pct` | `push2.f168` | 100.0% | 2 | 1 | 2 |
| `tdx.quote_full.amplitude_pct` | `push2_full.f171` | 100.0% | 2 | 1 | 2 |
| `tdx.quote_full.amplitude_pct` | `ulist239.f7` | 100.0% | 2 | 1 | 2 |
| `tdx.quote_full.amplitude_pct` | `push2.f171` | 100.0% | 2 | 1 | 2 |
| `tdx.quote_full.limit_down_price` | `push2_full.f52` | 100.0% | 2 | 1 | 2 |
| `tdx.quote_full.limit_down_price` | `push2.f52` | 100.0% | 2 | 1 | 2 |
| `tdx.quote_full.vol_ratio` | `push2_full.f50` | 100.0% | 2 | 1 | 2 |
| `tdx.quote_full.vol_ratio` | `ulist239.f10` | 100.0% | 2 | 1 | 2 |
| `tdx.quote_full.vol_ratio` | `push2.f50` | 100.0% | 2 | 1 | 2 |
| `tdx.quote_full.pe_lyr` | `push2_full.f163` | 100.0% | 2 | 1 | 2 |
| `tdx.quote_full.pe_lyr` | `ulist239.f114` | 100.0% | 2 | 1 | 2 |
| `tdx.quote_full.pe_lyr` | `push2.f163` | 100.0% | 2 | 1 | 2 |
| `zhb.full.unknown_26` | `eltdx.shortline.year_limit_up_days` | 100.0% | 2 | 1 | 2 |
| `zhb.stat.unknown_26` | `eltdx.shortline.year_limit_up_days` | 100.0% | 2 | 1 | 2 |
| `push2_full.f52` | `tdx.quote_full.limit_down` | 97.5% | 2 | 1 | 2 |
| `tdx.quote_full.limit_up` | `push2.f51` | 97.5% | 2 | 1 | 2 |
| `tdx.quote_full.limit_down` | `push2_full.f52` | 97.5% | 2 | 1 | 2 |
| `tdx.quote_full.limit_down` | `tencent[48]` | 97.5% | 2 | 1 | 2 |
| `push2.f51` | `tdx.quote_full.limit_up` | 97.5% | 2 | 1 | 2 |
| `push2_full.f167` | `tdx.quote_full.pb` | 95.0% | 2 | 1 | 2 |
| `tdx.finance_info.b_gu` | `ulist239.f200` | 95.0% | 2 | 1 | 2 |
| `tdx.finance_info.h_gu` | `ulist239.f190` | 95.0% | 2 | 1 | 2 |
| `ulist239.f23` | `tdx.quote_full.pb` | 95.0% | 2 | 1 | 2 |
| `ulist239.f190` | `tdx.finance_info.h_gu` | 95.0% | 2 | 1 | 2 |
| `push2.f167` | `tdx.quote_full.pb` | 95.0% | 2 | 1 | 2 |
| `tdx.quote_full.pb` | `push2_full.f167` | 95.0% | 2 | 1 | 2 |
| `tdx.quote_full.pb` | `ulist239.f23` | 95.0% | 2 | 1 | 2 |
| `tdx.quote_full.pb` | `push2.f167` | 95.0% | 2 | 1 | 2 |
| `tdx.finance_info.b_gu` | `tdx.finance_info.h_gu` | 90.0% | 2 | 1 | 2 |
| `tdx.finance_info.b_gu` | `tdx.finance_info.hgu` | 90.0% | 2 | 1 | 2 |
| `tdx.finance_info.b_gu` | `ulist239.f190` | 90.0% | 2 | 1 | 2 |
| `tdx.finance_info.b_gu` | `ulist239.f231` | 90.0% | 2 | 1 | 2 |
| `tdx.finance_info.h_gu` | `tdx.finance_info.b_gu` | 90.0% | 2 | 1 | 2 |
| `tdx.finance_info.h_gu` | `tdx.finance_info.bgu` | 90.0% | 2 | 1 | 2 |
| `tdx.finance_info.h_gu` | `ulist239.f200` | 90.0% | 2 | 1 | 2 |
| `tdx.finance_info.h_gu` | `ulist239.f231` | 90.0% | 2 | 1 | 2 |
| `ulist239.f190` | `tdx.finance_info.b_gu` | 90.0% | 2 | 1 | 2 |
| `tdx.finance_info.liutong_guben` | `push2.f85` | 100.0% | 1 | 2 | 1 |
| `tdx.finance_info.zong_guben` | `push2.f84` | 100.0% | 1 | 2 | 1 |
| `push2.f84` | `tdx.finance_info.zong_guben` | 100.0% | 1 | 2 | 1 |
| `push2.f84` | `tdx.finance_info.zongguben` | 100.0% | 1 | 2 | 1 |
| `push2.f85` | `tdx.finance_info.liutong_guben` | 100.0% | 1 | 2 | 1 |
| `zhb.full.pe_lyr` | `zhb.stat.pe_lyr` | 100.0% | 1 | 2 | 1 |
| `zhb.stat.pe_lyr` | `zhb.full.pe_lyr` | 100.0% | 1 | 2 | 1 |
| `tdx.quote_full.limit_down` | `push2.f52` | 95.0% | 1 | 2 | 1 |
| `tdx.quote_full.limit_down` | `tdx.quote_full.limit_down_price` | 95.0% | 1 | 2 | 1 |
| `push2.f52` | `tdx.quote_full.limit_down` | 95.0% | 1 | 2 | 1 |
| `tdx.quote_full.limit_down_price` | `tdx.quote_full.limit_down` | 95.0% | 1 | 2 | 1 |

## B类：overall<0.9（命中率不足，需改进对齐窗口或确认字段语义）— 212 条

> B类多为低同步字段（如部分资金流细分、事件类），当前窗口命中率 40.0%–89.6%，
> 建议扩大对撞窗口（--window 更大）或单独核验字段定义后再审议。
