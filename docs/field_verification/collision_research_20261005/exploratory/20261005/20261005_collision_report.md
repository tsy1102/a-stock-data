# 全源对撞报告（20261005）

> 行情窗口：20260812 ~ 20260930（32 个不同交易日）｜字段 1558 个｜样本值 1203936 条
> 新闻/公告自然日窗口：20260812 ~ 20261005
> 主攻目标（unverified）=602｜新增 L1/L1-U 定案=36｜异号同义 95 / 同号镜像 0

> **规则**：每个定案日有效样本≥18，命中率≥90%，至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 定案候选 — 异号同义（跨编号，高价值）(95)

| 左字段(unverified) | 右字段 | 等级 | 命中率 | 天数 | 样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|:--|:--|
| `push2_full.f51` | `tencent[47]` | L1 | 100.00% | 24 | 477 | - |  | ✅ |
| `push2_full.f52` | `tencent[48]` | L1 | 100.00% | 24 | 477 | - |  | ✅ |
| `push2_full.f57` | `tencent[2]` | L1 | 100.00% | 24 | 477 | - |  | ✅ |
| `push2_full.f60` | `sina[2]` | L1 | 100.00% | 24 | 478 | - |  | ✅ |
| `push2_full.f60` | `tencent[4]` | L1 | 100.00% | 24 | 477 | - |  | ✅ |
| `push2_full.f168` | `tencent[38]` | L1 | 100.00% | 24 | 477 | - |  | ✅ |
| `push2_full.f175` | `tencent[68]` | L1 | 100.00% | 24 | 477 | - |  | ✅ |
| `push2_full.f44` | `sina[4]` | L1 | 99.58% | 24 | 478 | - |  | ✅ |
| `push2_full.f44` | `tencent[33]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `push2_full.f44` | `tencent[41]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `push2_full.f45` | `sina[5]` | L1 | 99.58% | 24 | 478 | - |  | ✅ |
| `push2_full.f45` | `tencent[34]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `push2_full.f45` | `tencent[42]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `push2_full.f46` | `sina[1]` | L1 | 99.58% | 24 | 478 | - |  | ✅ |
| `push2_full.f46` | `tencent[5]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `push2_full.f48` | `sina[9]` | L1 | 99.58% | 24 | 478 | - |  | ✅ |
| `push2_full.f50` | `tencent[49]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `push2_full.f71` | `tencent[51]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `push2_full.f162` | `tencent[52]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `push2_full.f169` | `tencent[31]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `push2_full.f170` | `tencent[32]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `push2_full.f171` | `tencent[43]` | L1 | 99.58% | 24 | 477 | - |  | ✅ |
| `push2_full.f119` | `tencent[63]` | L1 | 99.37% | 24 | 477 | - |  | ✅ |
| `push2_full.f163` | `tencent[53]` | L1 | 98.95% | 24 | 477 | - |  | ✅ |
| `push2_full.f164` | `tencent[39]` | L1 | 98.32% | 24 | 477 | - |  | ✅ |
| `push2_full.f120` | `tencent[70]` | L1 | 96.44% | 24 | 477 | - |  | ✅ |
| `tencent[10]` | `ulist239.f211` | L1 | 93.54% | 28 | 557 | - |  | ✅ |
| `push2_full.f167` | `tencent[46]` | L1 | 90.57% | 24 | 477 | - |  | ✅ |
| `push2_full.f60` | `tdx.quote_full.last_close` | L1 | 100.00% | 24 | 478 | - |  | — |
| `fuyao.valuation.pcf_ttm` | `ulist239.f131` | L1 | 100.00% | 23 | 460 | - |  | — |
| `push2_full.f47` | `sina[8]` | L1-U | 100.00% | 23 | 459 | 100 |  | — |
| `zhb.full.amount` | `sina[9]` | L1-U | 100.00% | 23 | 459 | 10000 |  | — |
| `zhb.full.low_52w` | `tencent[68]` | L1 | 100.00% | 23 | 457 | - |  | — |
| `zhb.full.change_20d` | `ulist239.f110` | L1 | 100.00% | 22 | 440 | - |  | — |
| `zhb.full.change_30d` | `ulist239.f110` | L1 | 100.00% | 22 | 440 | - |  | — |
| `zhb.full.change_5d` | `ulist239.f109` | L1 | 100.00% | 22 | 440 | - |  | — |
| `zhb.full.change_10d` | `ulist239.f160` | L1 | 100.00% | 22 | 440 | - |  | — |
| `push2_full.f119` | `zhb.stat.change_5d` | L1 | 100.00% | 20 | 398 | - |  | — |
| `push2_full.f120` | `zhb.stat.change_20d` | L1 | 100.00% | 20 | 398 | - |  | — |
| `push2_full.f120` | `zhb.stat.change_30d` | L1 | 100.00% | 20 | 398 | - |  | — |
| `push2_full.f175` | `zhb.stat2.low_52w` | L1 | 100.00% | 20 | 398 | - |  | — |
| `push2_full.f44` | `fuyao.snapshot.high_price` | L1 | 100.00% | 19 | 380 | - |  | — |
| `push2_full.f45` | `fuyao.snapshot.low_price` | L1 | 100.00% | 19 | 380 | - |  | — |
| `push2_full.f46` | `fuyao.snapshot.open_price` | L1 | 100.00% | 19 | 380 | - |  | — |
| `push2_full.f47` | `fuyao.snapshot.volume` | L1-U | 100.00% | 19 | 380 | 100 |  | — |
| `push2_full.f48` | `fuyao.snapshot.turnover` | L1 | 100.00% | 19 | 380 | - |  | — |
| `push2_full.f60` | `fuyao.snapshot.prev_price` | L1 | 100.00% | 19 | 380 | - |  | — |
| `push2_full.f169` | `fuyao.snapshot.price_change` | L1 | 100.00% | 19 | 380 | - |  | — |
| `zhb.full.amount` | `fuyao.snapshot.turnover` | L1-U | 100.00% | 19 | 380 | 10000 |  | — |
| `tdx.quote_full.limit_down_price` | `tencent[48]` | L1 | 100.00% | 9 | 178 | - |  | — |
| `push2_full.f44` | `eltdx.quote_snapshot.high_price` | L1 | 100.00% | 4 | 72 | - |  | — |
| `push2_full.f45` | `eltdx.quote_snapshot.low_price` | L1 | 100.00% | 4 | 72 | - |  | — |
| `push2_full.f46` | `eltdx.quote_snapshot.open_price` | L1 | 100.00% | 4 | 72 | - |  | — |
| `push2_full.f48` | `eltdx.quote_snapshot.amount` | L1 | 100.00% | 4 | 72 | - |  | — |
| `push2_full.f60` | `eltdx.quote_snapshot.pre_close_price` | L1 | 100.00% | 4 | 72 | - |  | — |
| `tdx.quote_full.pe_static` | `tencent[53]` | L1 | 100.00% | 4 | 78 | - |  | — |
| `zhb.full.change_pct` | `push2.f170` | L1 | 100.00% | 4 | 80 | - |  | — |
| `zhb.full.change_20d` | `push2.f120` | L1 | 100.00% | 4 | 80 | - |  | — |
| `zhb.full.change_30d` | `push2.f120` | L1 | 100.00% | 4 | 80 | - |  | — |
| `zhb.full.change_60d` | `push2.f121` | L1 | 100.00% | 4 | 80 | - |  | — |
| `zhb.full.change_5d` | `push2.f119` | L1 | 100.00% | 4 | 80 | - |  | — |
| `zhb.full.low_52w` | `push2.f175` | L1 | 100.00% | 4 | 80 | - |  | — |
| `push2_full.f46` | `tdx.quote_full.open` | L1 | 99.79% | 24 | 477 | - |  | — |
| `zhb.full.change_pct` | `tencent[32]` | L1 | 99.78% | 23 | 457 | - |  | — |
| `zhb.full.change_pct` | `ulist239.f3` | L1 | 99.77% | 22 | 440 | - |  | — |
| `push2_full.f170` | `zhb.stat.change_pct` | L1 | 99.75% | 20 | 398 | - |  | — |
| `push2_full.f44` | `tdx.quote_full.high` | L1 | 99.58% | 24 | 477 | - |  | — |
| `zhb.full.change_5d` | `tencent[63]` | L1 | 99.34% | 23 | 457 | - |  | — |
| `push2_full.f45` | `tdx.quote_full.low` | L1 | 99.16% | 24 | 477 | - |  | — |
| `zhb.full.change_10d` | `tencent[69]` | L1 | 98.91% | 23 | 457 | - |  | — |
| `tdx.quote_full.limit_up` | `tencent[47]` | L1 | 98.45% | 13 | 258 | - |  | — |
| `tdx.quote_full.amplitude_pct` | `tencent[43]` | L1 | 97.75% | 9 | 178 | - |  | — |
| `tdx.quote_full.limit_down` | `tencent[48]` | L1 | 97.50% | 6 | 120 | - |  | — |
| `tdx.quote_full.pe_static` | `ulist239.f114` | L1 | 97.50% | 4 | 80 | - |  | — |
| `zhb.full.pe_dynamic` | `push2.f164` | L1 | 97.50% | 4 | 80 | - |  | — |
| `tdx.quote_full.amplitude_pct` | `ulist239.f7` | L1 | 96.88% | 8 | 160 | - |  | — |
| `zhb.full.change_20d` | `tencent[70]` | L1 | 96.72% | 23 | 457 | - |  | — |
| `zhb.full.change_30d` | `tencent[70]` | L1 | 96.72% | 23 | 457 | - |  | — |
| `zhb.full.change_60d` | `ulist239.f24` | L1 | 96.36% | 22 | 440 | - |  | — |
| `push2_full.f121` | `zhb.stat.change_60d` | L1 | 96.23% | 20 | 398 | - |  | — |
| `push2_full.f169` | `tdx.quote_full.change_amt` | L1 | 96.03% | 24 | 478 | - |  | — |
| `zhb.full.change_ytd` | `push2.f122` | L1 | 95.00% | 4 | 80 | - |  | — |
| `zhb.full.high_52w` | `tencent[67]` | L1 | 94.97% | 23 | 457 | - |  | — |
| `push2_full.f122` | `zhb.stat.change_ytd` | L1 | 94.97% | 20 | 398 | - |  | — |
| `zhb.full.pe_dynamic` | `tencent[39]` | L1 | 94.96% | 20 | 397 | - |  | — |
| `zhb.full.pe_dynamic` | `ulist239.f115` | L1 | 94.75% | 20 | 400 | - |  | — |
| `push2_full.f164` | `zhb.stat.pe_dynamic` | L1 | 94.72% | 20 | 398 | - |  | — |
| `zhb.full.change_ytd` | `ulist239.f25` | L1 | 94.55% | 22 | 440 | - |  | — |
| `tdx.quote_full.pb` | `tencent[46]` | L1 | 93.82% | 9 | 178 | - |  | — |
| `tdx.quote_full.vol_ratio` | `tencent[49]` | L1 | 91.01% | 9 | 178 | - |  | — |
| `push2_full.f174` | `tencent[67]` | L1 | 90.78% | 24 | 477 | - |  | — |
| `tdx.quote_full.float_mcap_yi` | `tencent[44]` | L1 | 90.45% | 9 | 178 | - |  | — |
| `tdx.quote_full.mcap_yi` | `tencent[45]` | L1 | 90.45% | 9 | 178 | - |  | — |
| `zhb.full.other_qy_jzc` | `ulist239.f190` | L1 | 90.00% | 6 | 120 | - |  | — |
| `zhb.full.other_qy_jzc` | `ulist239.f231` | L1 | 90.00% | 6 | 120 | - |  | — |

## 二、L1 / L1-U 定案候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、L4 存疑候选（337）

| 左字段 | 右字段 | 命中率 | 天数 | 样本 |
|:--|:--|--:|--:|--:|
| `fuyao.auction_final.auction_price` | `eltdx.shortline.open_price` | 100.00% | 6 | 108 |
| `fuyao.auction_final.pre_close_price` | `eltdx.quote_snapshot.pre_close_price` | 100.00% | 10 | 180 |
| `fuyao.auction_final.pre_close_price` | `eltdx.shortline.pre_close` | 100.00% | 6 | 108 |
| `fuyao.auction_final.pre_close_price` | `push2.f60` | 100.00% | 6 | 120 |
| `fuyao.auction_final.pre_close_price` | `push2_full.f60` | 100.00% | 19 | 380 |
| `fuyao.auction_final.pre_close_price` | `ulist239.f18` | 100.00% | 23 | 460 |
| `fuyao.auction_final.open_price` | `eltdx.quote_snapshot.open_price` | 100.00% | 9 | 162 |
| `fuyao.auction_final.open_price` | `eltdx.shortline.open_price` | 100.00% | 6 | 108 |
| `fuyao.auction_final.open_price` | `push2.f46` | 100.00% | 6 | 120 |
| `fuyao.auction_final.open_price` | `push2_full.f46` | 100.00% | 19 | 380 |
| `fuyao.auction_final.open_price` | `sina[1]` | 100.00% | 24 | 480 |
| `fuyao.auction_final.open_price` | `tdx.quote_full.open` | 100.00% | 24 | 480 |
| `fuyao.auction_final.open_price` | `tencent[5]` | 100.00% | 24 | 479 |
| `fuyao.auction_final.open_price` | `ulist239.f17` | 100.00% | 23 | 460 |
| `fuyao.auction_final.last_price` | `eltdx.quote_snapshot.last_price` | 100.00% | 9 | 162 |
| `fuyao.auction_final.last_price` | `push2.f43` | 100.00% | 6 | 120 |
| `fuyao.auction_final.last_price` | `push2.f179` | 100.00% | 6 | 120 |
| `fuyao.auction_final.last_price` | `push2_full.f43` | 100.00% | 19 | 380 |
| `fuyao.auction_final.last_price` | `push2_full.f179` | 100.00% | 19 | 380 |
| `fuyao.auction_final.last_price` | `sina[3]` | 100.00% | 24 | 480 |
| `fuyao.auction_final.last_price` | `tencent[3]` | 100.00% | 24 | 479 |
| `fuyao.auction_final.last_price` | `ulist239.f2` | 100.00% | 23 | 460 |
| `fuyao.auction_final.last_price` | `ulist239.f144` | 100.00% | 23 | 460 |
| `push2_full.f43` | `eltdx.quote_snapshot.last_price` | 100.00% | 4 | 72 |
| `push2_full.f43` | `fuyao.snapshot.last_price` | 100.00% | 19 | 380 |
| `push2_full.f46` | `eltdx.shortline.open_price` | 100.00% | 1 | 18 |
| `push2_full.f52` | `tdx.quote_full.limit_down_price` | 100.00% | 7 | 138 |
| `push2_full.f60` | `eltdx.shortline.pre_close` | 100.00% | 1 | 18 |
| `push2_full.f84` | `tdx.finance_info.zong_guben` | 100.00% | 20 | 398 |
| `push2_full.f84` | `tdx.finance_info.zongguben` | 100.00% | 20 | 398 |
| `push2_full.f84` | `tencent[73]` | 100.00% | 24 | 477 |
| `push2_full.f85` | `eltdx.shortline.float_shares` | 100.00% | 1 | 18 |
| `push2_full.f85` | `tencent[72]` | 100.00% | 24 | 477 |
| `push2_full.f85` | `tencent[76]` | 100.00% | 24 | 477 |
| `push2_full.f119` | `zhb.full.change_5d` | 100.00% | 20 | 398 |
| `push2_full.f120` | `zhb.full.change_20d` | 100.00% | 20 | 398 |
| `push2_full.f120` | `zhb.full.change_30d` | 100.00% | 20 | 398 |
| `push2_full.f175` | `zhb.full.low_52w` | 100.00% | 20 | 398 |
| `push2_full.f179` | `eltdx.quote_snapshot.last_price` | 100.00% | 4 | 72 |
| `push2_full.f179` | `fuyao.snapshot.last_price` | 100.00% | 19 | 380 |
| `tdx.quote_full.turnover_pct` | `push2.f168` | 100.00% | 3 | 50 |
| `tdx.quote_full.amplitude_pct` | `push2.f171` | 100.00% | 3 | 50 |
| `tdx.quote_full.limit_down_price` | `push2.f52` | 100.00% | 4 | 58 |
| `tdx.quote_full.vol_ratio` | `push2.f50` | 100.00% | 4 | 58 |
| `tdx.finance_info.liutong_guben` | `push2.f85` | 100.00% | 2 | 28 |
| `tdx.finance_info.zong_guben` | `push2.f84` | 100.00% | 2 | 28 |
| `tdx.finance_info.zong_guben` | `tencent[73]` | 100.00% | 20 | 397 |
| `tdx.finance_info.zong_guben` | `ulist239.f38` | 100.00% | 20 | 400 |
| `tdx.finance_info.zongguben` | `push2.f84` | 100.00% | 2 | 28 |
| `tdx.finance_info.zongguben` | `tencent[73]` | 100.00% | 20 | 397 |
| `tdx.finance_info.zongguben` | `ulist239.f38` | 100.00% | 20 | 400 |
| `tdx.quote_full.pe_lyr` | `push2.f163` | 100.00% | 3 | 50 |
| `ulist239.f144` | `eltdx.quote_snapshot.last_price` | 100.00% | 8 | 144 |
| `ulist239.f144` | `fuyao.snapshot.last_price` | 100.00% | 23 | 460 |
| `push2_full.f85` | `tdx.finance_info.liutong_guben` | 99.75% | 20 | 398 |
| `push2_full.f170` | `zhb.full.change_pct` | 99.75% | 20 | 398 |
| `tdx.finance_info.liutong_guben` | `tencent[72]` | 99.75% | 20 | 397 |
| `tdx.finance_info.liutong_guben` | `tencent[76]` | 99.75% | 20 | 397 |
| `tdx.finance_info.liutong_guben` | `ulist239.f39` | 99.75% | 20 | 400 |
| `sina[32]` | `ulist239.f125` | 99.64% | 28 | 560 |

_（仅显示前 60 / 共 337）_

## 四、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 五、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `fuyao.auction_final.auction_volume_ratio` | `eltdx.shortline.auction_prev_volume_ratio` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 108 | T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930 | eltdx, fuyao | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `push2ex.change_pct` | `zhb.stat.change_pct` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 35 | T:20260901, T:20260902, T:20260904, T:20260908, T:20260911, T:20260914 | push2ex, zhb | Pearson=1.0, Spearman=0.9982, LOO稳号=True |
| `push2ex.change_pct` | `zhb.full.change_pct` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 35 | T:20260901, T:20260902, T:20260904, T:20260908, T:20260911, T:20260914 | push2ex, zhb | Pearson=1.0, Spearman=0.9982, LOO稳号=True |
| `sina[29]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9803, Spearman=0.966, LOO稳号=True |
| `sina[27]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9803, Spearman=0.966, LOO稳号=True |
| `sina[25]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9803, Spearman=0.966, LOO稳号=True |
| `sina[23]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9803, Spearman=0.9661, LOO稳号=True |
| `sina[21]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.9934, LOO稳号=True |
| `sina[19]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9733, LOO稳号=True |
| `sina[17]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9733, LOO稳号=True |
| `sina[15]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9733, LOO稳号=True |
| `sina[13]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9733, LOO稳号=True |
| `sina[11]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9803, Spearman=0.947, LOO稳号=True |
| `sina[11]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 620 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.993, LOO稳号=True |
| `sina[11]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9805, Spearman=0.9554, LOO稳号=True |
| `sina[11]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 619 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9804, Spearman=0.9561, LOO稳号=True |
| `tencent[12]` | `sina[12]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9946, Spearman=0.9478, LOO稳号=True |
| `tencent[10]` | `sina[10]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=1.0, Spearman=0.9361, LOO稳号=True |
| `sina[28]` | `tencent[28]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9819, Spearman=0.9362, LOO稳号=True |
| `sina[24]` | `tencent[24]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9832, Spearman=0.9395, LOO稳号=True |
| `sina[16]` | `tencent[16]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9961, Spearman=0.941, LOO稳号=True |
| `sina[14]` | `tencent[14]` | robust_correlation, affine_formula, per_stock_time_series | 617 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9974, Spearman=0.9467, LOO稳号=True |
| `tdx.finance_info.zongzichan` | `ulist239.f50` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=1.0, Spearman=0.9998, LOO稳号=True |
| `tdx.finance_info.zibengongjijin` | `ulist239.f60` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tdx.finance_info.zhuyingshouru` | `ulist239.f40` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9941, Spearman=0.9975, LOO稳号=True |
| `tdx.finance_info.yingyelirun` | `ulist239.f45` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9909, Spearman=0.963, LOO稳号=True |
| `tdx.finance_info.yingyelirun` | `ulist239.f44` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9929, Spearman=0.9769, LOO稳号=True |
| `tdx.finance_info.yingyelirun` | `ulist239.f42` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9929, Spearman=0.9954, LOO稳号=True |
| `tdx.finance_info.wuxingzichan` | `ulist239.f53` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tdx.finance_info.weifenlirun` | `ulist239.f47` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=1.0, Spearman=0.9998, LOO稳号=True |
| `tdx.finance_info.weifenlirun` | `ulist239.f135` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9966, Spearman=0.9464, LOO稳号=True |
| `tdx.finance_info.touzishouyu` | `ulist239.f43` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9915, Spearman=0.9936, LOO稳号=True |
| `tdx.finance_info.shuihoulirun` | `ulist239.f45` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9947, Spearman=0.9971, LOO稳号=True |
| `tdx.finance_info.shuihoulirun` | `ulist239.f44` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.993, Spearman=0.9896, LOO稳号=True |
| `tdx.finance_info.shuihoulirun` | `ulist239.f42` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.993, Spearman=0.9684, LOO稳号=True |
| `tdx.finance_info.meigujingzichan` | `ulist239.f113` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=1.0, Spearman=0.9986, LOO稳号=True |
| `tdx.finance_info.liudongzichan` | `ulist239.f51` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=1.0, Spearman=0.9997, LOO稳号=True |
| `tdx.finance_info.liudongfuzhai` | `ulist239.f55` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9999, Spearman=0.9997, LOO稳号=True |
| `tdx.finance_info.lirunzonghe` | `ulist239.f45` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9909, Spearman=0.9849, LOO稳号=True |
| `tdx.finance_info.lirunzonghe` | `ulist239.f44` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9929, Spearman=0.9958, LOO稳号=True |
| `tdx.finance_info.lirunzonghe` | `ulist239.f42` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9929, Spearman=0.9774, LOO稳号=True |
| `tdx.finance_info.jingzichan` | `ulist239.f47` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9963, Spearman=0.9326, LOO稳号=True |
| `tdx.finance_info.jingzichan` | `ulist239.f135` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=1.0, Spearman=0.9964, LOO稳号=True |
| `tdx.finance_info.jinglirun` | `ulist239.f45` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9948, Spearman=0.9983, LOO稳号=True |
| `tdx.finance_info.jinglirun` | `ulist239.f44` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9927, Spearman=0.9873, LOO稳号=True |
| `tdx.finance_info.jinglirun` | `ulist239.f42` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9927, Spearman=0.966, LOO稳号=True |
| `tdx.finance_info.gudingzichan` | `ulist239.f52` | robust_correlation, affine_formula, per_stock_time_series | 580 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=1.0, Spearman=0.9998, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 578 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 578 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9999, Spearman=0.9976, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 578 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=1.0, Spearman=0.9986, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.last_close` | robust_correlation, affine_formula, per_stock_time_series | 578 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9999, Spearman=0.9971, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 578 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=1.0, Spearman=0.9991, LOO稳号=True |
| `ulist239.f144` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 578 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=0.9999, Spearman=0.9436, LOO稳号=True |
| `ulist239.f144` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 578 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=0.9999, Spearman=0.9811, LOO稳号=True |
| `ulist239.f144` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 578 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=1.0, Spearman=0.9986, LOO稳号=True |
| `ulist239.f144` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 578 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=1.0, Spearman=0.9991, LOO稳号=True |
| `ulist239.f144` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 578 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f144` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 578 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=0.9999, Spearman=0.9971, LOO稳号=True |
| `ulist239.f144` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 578 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=0.9999, Spearman=0.9976, LOO稳号=True |
| `ulist239.f144` | `tencent[5]` | robust_correlation, affine_formula, per_stock_time_series | 575 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tencent, ulist239 | Pearson=0.9999, Spearman=0.9975, LOO稳号=True |
| `ulist239.f144` | `tencent[51]` | robust_correlation, affine_formula, per_stock_time_series | 575 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tencent, ulist239 | Pearson=1.0, Spearman=0.9995, LOO稳号=True |
| `ulist239.f144` | `tencent[4]` | robust_correlation, affine_formula, per_stock_time_series | 575 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tencent, ulist239 | Pearson=0.9999, Spearman=0.9971, LOO稳号=True |
| `ulist239.f144` | `tencent[48]` | robust_correlation, affine_formula, per_stock_time_series | 575 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tencent, ulist239 | Pearson=0.9999, Spearman=0.9882, LOO稳号=True |
| `ulist239.f144` | `tencent[47]` | robust_correlation, affine_formula, per_stock_time_series | 575 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tencent, ulist239 | Pearson=0.9999, Spearman=0.9942, LOO稳号=True |
| `ulist239.f144` | `tencent[42]` | robust_correlation, affine_formula, per_stock_time_series | 575 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tencent, ulist239 | Pearson=1.0, Spearman=0.9986, LOO稳号=True |
| `ulist239.f144` | `tencent[41]` | robust_correlation, affine_formula, per_stock_time_series | 575 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tencent, ulist239 | Pearson=1.0, Spearman=0.9991, LOO稳号=True |
| `ulist239.f144` | `tencent[3]` | robust_correlation, affine_formula, per_stock_time_series | 575 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tencent, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f144` | `tencent[34]` | robust_correlation, affine_formula, per_stock_time_series | 575 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tencent, ulist239 | Pearson=1.0, Spearman=0.9986, LOO稳号=True |
| `ulist239.f144` | `tencent[33]` | robust_correlation, affine_formula, per_stock_time_series | 575 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tencent, ulist239 | Pearson=1.0, Spearman=0.9991, LOO稳号=True |
| `ulist239.f11` | `tencent[80]` | robust_correlation, affine_formula, per_stock_time_series | 575 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tencent, ulist239 | Pearson=0.9871, Spearman=0.9676, LOO稳号=True |
| `sina[11]` | `ulist239.f31` | robust_correlation, affine_formula, per_stock_time_series | 570 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=0.9999, Spearman=0.9786, LOO稳号=True |
| `tencent[10]` | `ulist239.f211` | robust_correlation, affine_formula, per_stock_time_series | 564 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tencent, ulist239 | Pearson=1.0, Spearman=0.9273, LOO稳号=True |
| `ulist239.f142` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f142` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9999, Spearman=0.9975, LOO稳号=True |
| `ulist239.f142` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=1.0, Spearman=0.9985, LOO稳号=True |
| `ulist239.f142` | `tdx.quote_full.last_close` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9999, Spearman=0.9969, LOO稳号=True |
| `ulist239.f142` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=1.0, Spearman=0.9991, LOO稳号=True |
| `ulist239.f142` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f142` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9999, Spearman=0.9414, LOO稳号=True |
| `ulist239.f142` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=0.9999, Spearman=0.9414, LOO稳号=True |
| `ulist239.f142` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f142` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=1.0, Spearman=0.9985, LOO稳号=True |
| `ulist239.f142` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=1.0, Spearman=0.9991, LOO稳号=True |
| `ulist239.f142` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f142` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=0.9999, Spearman=0.9969, LOO稳号=True |
| `ulist239.f142` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=0.9999, Spearman=0.9975, LOO稳号=True |
| `sina[29]` | `ulist239.f142` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=0.9999, Spearman=0.9413, LOO稳号=True |
| `sina[27]` | `ulist239.f142` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=0.9999, Spearman=0.9413, LOO稳号=True |
| `sina[25]` | `ulist239.f142` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=0.9999, Spearman=0.9414, LOO稳号=True |
| `sina[23]` | `ulist239.f142` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=0.9999, Spearman=0.9414, LOO稳号=True |
| `sina[21]` | `ulist239.f142` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=0.9999, Spearman=0.9414, LOO稳号=True |
| `sina[19]` | `ulist239.f142` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[17]` | `ulist239.f142` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[15]` | `ulist239.f142` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[13]` | `ulist239.f142` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[11]` | `ulist239.f142` | robust_correlation, affine_formula, per_stock_time_series | 556 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f142` | `tencent[5]` | robust_correlation, affine_formula, per_stock_time_series | 553 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tencent, ulist239 | Pearson=0.9999, Spearman=0.9975, LOO稳号=True |
| `ulist239.f142` | `tencent[51]` | robust_correlation, affine_formula, per_stock_time_series | 553 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tencent, ulist239 | Pearson=1.0, Spearman=0.9995, LOO稳号=True |
| `ulist239.f142` | `tencent[4]` | robust_correlation, affine_formula, per_stock_time_series | 553 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tencent, ulist239 | Pearson=0.9999, Spearman=0.9969, LOO稳号=True |
| `ulist239.f142` | `tencent[48]` | robust_correlation, affine_formula, per_stock_time_series | 553 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tencent, ulist239 | Pearson=0.9999, Spearman=0.9881, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 六、日期与数据质量告警（239）

- 20260920: 旧式非交易日目录按前一交易日 20260918 归并；目录未改名
- 20261005: 旧式非交易日目录按前一交易日 20260930 归并；目录未改名
- 20260814: 行情数据日 20260814 属于配置的异常日，行情快照排除
- 20260812/thsdk: 没有可用记录，快照跳过
- 20260813/push2: 没有可用记录，快照跳过
- 20260813/thsdk: 没有可用记录，快照跳过
- 20260819/thsdk: 没有可用记录，快照跳过
- 20260820/thsdk: 没有可用记录，快照跳过
- 20260821/push2: 没有可用记录，快照跳过
- 20260821/thsdk: 没有可用记录，快照跳过
- 20260824/thsdk: 没有可用记录，快照跳过
- 20260825/push2: 没有可用记录，快照跳过
- 20260825/thsdk: 没有可用记录，快照跳过
- 20260826/push2: 没有可用记录，快照跳过
- 20260826/thsdk: 没有可用记录，快照跳过
- 20260827/thsdk: 没有可用记录，快照跳过
- 20260828/cninfo: 没有可用记录，快照跳过
- 20260828/push2: 没有可用记录，快照跳过
- 20260828/thsdk: 没有可用记录，快照跳过
- 20260901/axdata: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/datacenter: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/em_fund_flow: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/em_hot: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/em_kline_f61: 没有可用记录，快照跳过
- 20260901/fuyao: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/market_sources: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/push2: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/push2_full: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/push2ex: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/sina: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/tdx: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/tdx_f10: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/tdx_f10_more: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/tencent: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/thsdk: 采集时段未知，保留为候选样本但不计入 L1
- 20260901/ulist239: 采集时段未知，保留为候选样本但不计入 L1
- 20260902/push2: 没有可用记录，快照跳过
- 20260903/em_kline_f61: 没有可用记录，快照跳过
- 20260903/push2: 没有可用记录，快照跳过
- 20260903/thsdk: 没有可用记录，快照跳过
- 20260904/em_kline_f61: 没有可用记录，快照跳过
- 20260904/push2: 没有可用记录，快照跳过
- 20260907/em_kline_f61: 没有可用记录，快照跳过
- 20260907/push2: 没有可用记录，快照跳过
- 20260908/push2: 没有可用记录，快照跳过
- 20260909/em_kline_f61: 没有可用记录，快照跳过
- 20260909/push2: 没有可用记录，快照跳过
- 20260910/push2: 没有可用记录，快照跳过
- 20260910/tdx_f10_more: 没有可用记录，快照跳过
- 20260911/em_kline_f61: 采集状态 failed
- 20260911/em_kline_f61: 来源状态为 failed，快照跳过
- 20260911/push2: 没有可用记录，快照跳过
- 20260911/tdx_f10_more: 没有可用记录，快照跳过
- 20260914/em_kline_f61: 采集状态 partial
- 20260914/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20260914/em_kline_f61: 没有可用记录，快照跳过
- 20260914/tdx_f10_more: 没有可用记录，快照跳过
- 20260915/eltdx: 采集状态 partial
- 20260915/em_kline_f61: 采集状态 partial
- 20260915/eltdx: 来源状态为 partial，样本按部分快照参与
- 20260915/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20260915/tdx_f10: 没有可用记录，快照跳过
- 20260915/tdx_f10_more: 没有可用记录，快照跳过
- 20260916/eltdx: 采集状态 partial
- 20260916/em_kline_f61: 采集状态 partial
- 20260916/eltdx: 来源状态为 partial，样本按部分快照参与
- 20260916/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20260916/tdx_f10_more: 没有可用记录，快照跳过
- 20260917/eltdx: 采集状态 partial
- 20260917/em_kline_f61: 采集状态 partial
- 20260917/eltdx: 来源状态为 partial，样本按部分快照参与
- 20260917/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20260917/tdx_f10: 没有可用记录，快照跳过
- 20260917/tdx_f10_more: 没有可用记录，快照跳过
- 20260918/eltdx: 采集状态 partial
- 20260918/em_kline_f61: 采集状态 failed
- 20260918/eltdx: 来源状态为 partial，样本按部分快照参与
- 20260918/em_kline_f61: 来源状态为 failed，快照跳过
- 20260918/tdx_f10: 没有可用记录，快照跳过
- 20260918/tdx_f10_more: 没有可用记录，快照跳过
- 20260920/eltdx: 采集状态 partial
- 20260920/em_kline_f61: 采集状态 partial
- 20260920/eltdx: 来源状态为 partial，样本按部分快照参与
- 20260920/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20260920/tdx_f10: 没有可用记录，快照跳过
- 20260920/tdx_f10_more: 没有可用记录，快照跳过
- 20260921/eltdx: 采集状态 partial
- 20260921/push2: 采集状态 failed
- 20260921/push2_full: 采集状态 failed
- 20260921/em_kline_f61: 采集状态 failed
- 20260921/em_fund_flow: 采集状态 failed
- 20260921/ulist239: 采集状态 failed
- 20260921/clist: 采集状态 partial
- 20260921/clist: 来源状态为 partial，样本按部分快照参与
- 20260921/clist: 没有可用记录，快照跳过
- 20260921/eltdx: 来源状态为 partial，样本按部分快照参与
- 20260921/em_fund_flow: 来源状态为 failed，快照跳过
- 20260921/em_hot: 没有可用记录，快照跳过
- 20260921/em_kline_f61: 来源状态为 failed，快照跳过
- 20260921/push2: 来源状态为 failed，快照跳过
- 另有 139 条告警，详见同名 JSON 报告。

---

> 数据来源：通达信 / 项目字段对撞体系。以上为方法论梳理，不构成投资建议。
