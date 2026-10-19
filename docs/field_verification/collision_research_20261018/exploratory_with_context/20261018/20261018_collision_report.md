# 全源对撞报告（20261018）

> 交易数据窗口配置：全部历史日期（`--all`）
> 行情窗口：20260812 ~ 20261016（39 个不同交易日）｜字段 1604 个｜样本值 1565190 条
> 新闻/公告自然日窗口：20260812 ~ 20261018
> 主攻目标（unverified）=573｜可审定新候选=40｜首次发现新候选对=0｜已登记关系复验=39｜异号同义 40 / 同号镜像 0

> **规则**：L1 每日需≥18 组有效配对，并至少有5 组信息配对；双方同时为 0 或同时缺失不计命中率，一侧为 0、另一侧非 0 按失配计。信息配对命中率≥90%，且覆盖至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。JSON `daily_sample_counts` 与 `daily_informative_sample_counts`分别保留每日有效配对数和 L1 信息配对数。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 新候选 — 异号同义（跨编号，高价值）(40)

| 左字段(unverified) | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|
| `push2_full.f60` | `tdx.quote_full.last_close` | L1 | 100.00% | 24 | 478 | 478 | - |  | — |
| `push2_full.f47` | `sina[8]` | L1-U | 100.00% | 23 | 459 | — | 100 |  | — |
| `push2_full.f119` | `zhb.stat.change_5d` | L1 | 100.00% | 20 | 398 | 426 | - |  | — |
| `push2_full.f120` | `zhb.stat.change_20d` | L1 | 100.00% | 20 | 398 | 427 | - |  | — |
| `push2_full.f175` | `zhb.stat2.low_52w` | L1 | 100.00% | 20 | 398 | 428 | - |  | — |
| `push2_full.f44` | `fuyao.snapshot.high_price` | L1 | 100.00% | 19 | 380 | 380 | - |  | — |
| `push2_full.f45` | `fuyao.snapshot.low_price` | L1 | 100.00% | 19 | 380 | 380 | - |  | — |
| `push2_full.f46` | `fuyao.snapshot.open_price` | L1 | 100.00% | 19 | 380 | 380 | - |  | — |
| `push2_full.f47` | `fuyao.snapshot.volume` | L1-U | 100.00% | 19 | 380 | — | 100 |  | — |
| `push2_full.f48` | `fuyao.snapshot.turnover` | L1 | 100.00% | 19 | 380 | 380 | - |  | — |
| `push2_full.f60` | `fuyao.snapshot.prev_price` | L1 | 100.00% | 19 | 380 | 380 | - |  | — |
| `push2_full.f169` | `fuyao.snapshot.price_change` | L1 | 100.00% | 19 | 380 | 374 | - |  | — |
| `tdx.quote_full.limit_down_price` | `tencent[48]` | L1 | 100.00% | 9 | 178 | 178 | - |  | — |
| `push2_full.f44` | `eltdx.quote_snapshot.high_price` | L1 | 100.00% | 4 | 72 | 72 | - |  | — |
| `push2_full.f45` | `eltdx.quote_snapshot.low_price` | L1 | 100.00% | 4 | 72 | 72 | - |  | — |
| `push2_full.f46` | `eltdx.quote_snapshot.open_price` | L1 | 100.00% | 4 | 72 | 72 | - |  | — |
| `push2_full.f48` | `eltdx.quote_snapshot.amount` | L1 | 100.00% | 4 | 72 | 72 | - |  | — |
| `push2_full.f60` | `eltdx.quote_snapshot.pre_close_price` | L1 | 100.00% | 4 | 72 | 72 | - |  | — |
| `tdx.quote_full.pe_static` | `tencent[53]` | L1 | 100.00% | 4 | 78 | 78 | - |  | — |
| `push2_full.f46` | `tdx.quote_full.open` | L1 | 99.79% | 24 | 477 | 477 | - |  | — |
| `push2_full.f170` | `zhb.stat.change_pct` | L1 | 99.74% | 20 | 398 | 422 | - |  | — |
| `push2_full.f44` | `tdx.quote_full.high` | L1 | 99.58% | 24 | 477 | 477 | - |  | — |
| `push2_full.f45` | `tdx.quote_full.low` | L1 | 99.16% | 24 | 477 | 477 | - |  | — |
| `tdx.quote_full.limit_up` | `tencent[47]` | L1 | 98.45% | 13 | 258 | 258 | - |  | — |
| `tdx.quote_full.amplitude_pct` | `tencent[43]` | L1 | 97.70% | 9 | 178 | 174 | - |  | — |
| `tdx.quote_full.limit_down` | `tencent[48]` | L1 | 97.50% | 6 | 120 | 120 | - |  | — |
| `tdx.quote_full.pe_static` | `ulist239.f114` | L1 | 97.50% | 4 | 80 | 80 | - |  | — |
| `zhb.full.pe_dynamic` | `push2.f164` | L1 | 97.50% | 4 | 80 | 95 | - |  | — |
| `tdx.quote_full.amplitude_pct` | `ulist239.f7` | L1 | 96.84% | 8 | 160 | 158 | - |  | — |
| `push2_full.f121` | `zhb.stat.change_60d` | L1 | 96.20% | 20 | 398 | 424 | - |  | — |
| `push2_full.f169` | `tdx.quote_full.change_amt` | L1 | 95.97% | 24 | 478 | 471 | - |  | — |
| `push2_full.f122` | `zhb.stat.change_ytd` | L1 | 94.96% | 20 | 398 | 427 | - |  | — |
| `zhb.full.pe_dynamic` | `tencent[39]` | L1 | 94.96% | 20 | 397 | 427 | - |  | — |
| `zhb.full.pe_dynamic` | `ulist239.f115` | L1 | 94.75% | 20 | 400 | 430 | - |  | — |
| `push2_full.f164` | `zhb.stat.pe_dynamic` | L1 | 94.72% | 20 | 398 | 428 | - |  | — |
| `tdx.quote_full.pb` | `tencent[46]` | L1 | 93.82% | 9 | 178 | 178 | - |  | — |
| `tdx.quote_full.vol_ratio` | `tencent[49]` | L1 | 90.96% | 9 | 178 | 177 | - |  | — |
| `push2_full.f174` | `tencent[67]` | L1 | 90.78% | 24 | 477 | 477 | - |  | — |
| `tdx.quote_full.float_mcap_yi` | `tencent[44]` | L1 | 90.45% | 9 | 178 | 178 | - |  | — |
| `tdx.quote_full.mcap_yi` | `tencent[45]` | L1 | 90.45% | 9 | 178 | 178 | - |  | — |

## 二、L1 / L1-U 新候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、已登记映射的本窗口复验（39）

_这些关系已在主注册表登记，只用于观察当前样本是否仍支持既有映射；它们不是新的未知字段候选，也不能再次提交为新定案。_

| 左字段 | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|
| `push2_full.f51` | `tencent[47]` | L1 | 100.00% | 24 | 477 | 477 | - |  | ✅ |
| `push2_full.f52` | `tencent[48]` | L1 | 100.00% | 24 | 477 | 477 | - |  | ✅ |
| `push2_full.f57` | `tencent[2]` | L1 | 100.00% | 24 | 477 | 477 | - |  | ✅ |
| `push2_full.f60` | `sina[2]` | L1 | 100.00% | 24 | 478 | 478 | - |  | ✅ |
| `push2_full.f60` | `tencent[4]` | L1 | 100.00% | 24 | 477 | 477 | - |  | ✅ |
| `push2_full.f168` | `tencent[38]` | L1 | 100.00% | 24 | 477 | 475 | - |  | ✅ |
| `push2_full.f175` | `tencent[68]` | L1 | 100.00% | 24 | 477 | 477 | - |  | ✅ |
| `push2_full.f119` | `zhb.full.change_5d` | L1 | 100.00% | 20 | 398 | 426 | - |  | ✅ |
| `push2_full.f120` | `zhb.full.change_20d` | L1 | 100.00% | 20 | 398 | 427 | - |  | ✅ |
| `push2_full.f175` | `zhb.full.low_52w` | L1 | 100.00% | 20 | 398 | 428 | - |  | ✅ |
| `zhb.full.change_pct` | `push2.f170` | L1 | 100.00% | 4 | 80 | 121 | - |  | ✅ |
| `zhb.full.change_60d` | `push2.f121` | L1 | 100.00% | 4 | 80 | 123 | - |  | ✅ |
| `zhb.full.change_pct` | `ulist239.f3` | L1 | 99.77% | 22 | 440 | 477 | - |  | ✅ |
| `push2_full.f44` | `sina[4]` | L1 | 99.58% | 24 | 478 | 478 | - |  | ✅ |
| `push2_full.f44` | `tencent[33]` | L1 | 99.58% | 24 | 477 | 477 | - |  | ✅ |
| `push2_full.f44` | `tencent[41]` | L1 | 99.58% | 24 | 477 | 477 | - |  | ✅ |
| `push2_full.f45` | `sina[5]` | L1 | 99.58% | 24 | 478 | 478 | - |  | ✅ |
| `push2_full.f45` | `tencent[34]` | L1 | 99.58% | 24 | 477 | 477 | - |  | ✅ |
| `push2_full.f45` | `tencent[42]` | L1 | 99.58% | 24 | 477 | 477 | - |  | ✅ |
| `push2_full.f46` | `sina[1]` | L1 | 99.58% | 24 | 478 | 478 | - |  | ✅ |
| `push2_full.f46` | `tencent[5]` | L1 | 99.58% | 24 | 477 | 477 | - |  | ✅ |
| `push2_full.f48` | `sina[9]` | L1 | 99.58% | 24 | 478 | 478 | - |  | ✅ |
| `push2_full.f50` | `tencent[49]` | L1 | 99.58% | 24 | 477 | 477 | - |  | ✅ |
| `push2_full.f71` | `tencent[51]` | L1 | 99.58% | 24 | 477 | 477 | - |  | ✅ |
| `push2_full.f162` | `tencent[52]` | L1 | 99.58% | 24 | 477 | 477 | - |  | ✅ |
| `push2_full.f171` | `tencent[43]` | L1 | 99.58% | 24 | 477 | 476 | - |  | ✅ |
| `push2_full.f169` | `tencent[31]` | L1 | 99.57% | 24 | 477 | 470 | - |  | ✅ |
| `push2_full.f170` | `tencent[32]` | L1 | 99.57% | 24 | 477 | 470 | - |  | ✅ |
| `zhb.full.change_pct` | `tencent[32]` | L1 | 99.45% | 28 | 557 | 593 | - |  | ✅ |
| `push2_full.f119` | `tencent[63]` | L1 | 99.37% | 24 | 477 | 475 | - |  | ✅ |
| `push2_full.f163` | `tencent[53]` | L1 | 98.95% | 24 | 477 | 477 | - |  | ✅ |
| `push2_full.f164` | `tencent[39]` | L1 | 98.32% | 24 | 477 | 477 | - |  | ✅ |
| `push2_full.f120` | `tencent[70]` | L1 | 96.43% | 24 | 477 | 476 | - |  | ✅ |
| `zhb.full.change_60d` | `ulist239.f24` | L1 | 96.34% | 22 | 440 | 481 | - |  | ✅ |
| `zhb.full.high_52w` | `tencent[67]` | L1 | 94.97% | 28 | 557 | 602 | - |  | ✅ |
| `zhb.full.change_ytd` | `push2.f122` | L1 | 94.94% | 4 | 80 | 122 | - |  | ✅ |
| `zhb.full.change_ytd` | `ulist239.f25` | L1 | 94.53% | 22 | 440 | 484 | - |  | ✅ |
| `tencent[10]` | `ulist239.f211` | L1 | 93.76% | 29 | 577 | 577 | - |  | ✅ |
| `push2_full.f167` | `tencent[46]` | L1 | 90.57% | 24 | 477 | 477 | - |  | ✅ |

## 四、L4 存疑候选（327）

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
| `push2_full.f78` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 100.00% | 4 | 72 |
| `push2_full.f84` | `tdx.finance_info.zong_guben` | 100.00% | 20 | 398 |
| `push2_full.f84` | `tdx.finance_info.zongguben` | 100.00% | 20 | 398 |
| `push2_full.f84` | `tencent[73]` | 100.00% | 24 | 477 |
| `push2_full.f85` | `eltdx.shortline.float_shares` | 100.00% | 1 | 18 |
| `push2_full.f85` | `tencent[72]` | 100.00% | 24 | 477 |
| `push2_full.f85` | `tencent[76]` | 100.00% | 24 | 477 |
| `push2_full.f134` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 100.00% | 4 | 72 |
| `push2_full.f179` | `eltdx.quote_snapshot.last_price` | 100.00% | 4 | 72 |
| `push2_full.f179` | `fuyao.snapshot.last_price` | 100.00% | 19 | 380 |
| `push2ex.limit_fund` | `kph.seal_amount` | 100.00% | 1 | 50 |
| `push2ex.limit_fund` | `kpl.seal_amount` | 100.00% | 2 | 75 |
| `tdx.quote_full.turnover_pct` | `push2.f168` | 100.00% | 3 | 50 |
| `tdx.quote_full.amplitude_pct` | `push2.f171` | 100.00% | 3 | 50 |
| `tdx.quote_full.limit_down_price` | `push2.f52` | 100.00% | 4 | 58 |
| `tdx.quote_full.vol_ratio` | `push2.f50` | 100.00% | 4 | 58 |
| `tdx.finance_info.liutong_guben` | `push2.f85` | 100.00% | 2 | 28 |
| `tdx.finance_info.zong_guben` | `push2.f84` | 100.00% | 2 | 28 |
| `tdx.finance_info.zong_guben` | `tencent[73]` | 100.00% | 20 | 397 |
| `tdx.finance_info.zong_guben` | `ulist239.f38` | 100.00% | 20 | 400 |
| `tdx.quote_full.pe_lyr` | `push2.f163` | 100.00% | 3 | 50 |
| `ulist239.f125` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 100.00% | 9 | 162 |
| `ulist239.f144` | `eltdx.quote_snapshot.last_price` | 100.00% | 9 | 162 |
| `ulist239.f144` | `fuyao.snapshot.last_price` | 100.00% | 24 | 480 |
| `push2_full.f85` | `tdx.finance_info.liutong_guben` | 99.75% | 20 | 398 |
| `tdx.finance_info.liutong_guben` | `tencent[72]` | 99.75% | 20 | 397 |
| `tdx.finance_info.liutong_guben` | `tencent[76]` | 99.75% | 20 | 397 |
| `tdx.finance_info.liutong_guben` | `ulist239.f39` | 99.75% | 20 | 400 |
| `push2_full.f170` | `zhb.full.change_pct` | 99.74% | 20 | 398 |
| `sina[32]` | `ulist239.f125` | 99.67% | 30 | 600 |
| `ulist239.f144` | `sina[3]` | 99.66% | 29 | 580 |
| `ulist239.f144` | `tencent[3]` | 99.65% | 29 | 577 |

_（仅显示前 60 / 共 327）_

## 五、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 六、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `fuyao.valuation.pe_ttm` | `eltdx.shortline.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 183 | T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930 | eltdx, fuyao | Pearson=0.9996, Spearman=0.9977, LOO稳号=True |
| `fuyao.auction_final.auction_volume_ratio` | `eltdx.shortline.auction_prev_volume_ratio` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 108 | T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930 | eltdx, fuyao | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_pct` | `em_hot.pct` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 40 | T:20260819, T:20260821, T:20260824, T:20260901, T:20260902, T:20260904 | em_hot, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `push2ex.change_pct` | `zhb.stat.change_pct` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 38 | T:20260901, T:20260902, T:20260904, T:20260908, T:20260911, T:20260914 | push2ex, zhb | Pearson=1.0, Spearman=0.9978, LOO稳号=True |
| `push2ex.change_pct` | `zhb.full.change_pct` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 38 | T:20260901, T:20260902, T:20260904, T:20260908, T:20260911, T:20260914 | push2ex, zhb | Pearson=1.0, Spearman=0.9978, LOO稳号=True |
| `tencent[20]` | `sina[20]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9804, Spearman=0.947, LOO稳号=True |
| `tencent[12]` | `sina[12]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9949, Spearman=0.9576, LOO稳号=True |
| `tencent[10]` | `sina[10]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=1.0, Spearman=0.9478, LOO稳号=True |
| `sina[29]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9831, Spearman=0.7393, LOO稳号=True |
| `sina[29]` | `tencent[27]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9481, LOO稳号=True |
| `sina[29]` | `tencent[25]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9481, LOO稳号=True |
| `sina[29]` | `tencent[23]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9481, LOO稳号=True |
| `sina[29]` | `tencent[21]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9481, LOO稳号=True |
| `sina[28]` | `tencent[28]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9838, Spearman=0.9478, LOO稳号=True |
| `sina[27]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9831, Spearman=0.7393, LOO稳号=True |
| `sina[27]` | `tencent[27]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9481, LOO稳号=True |
| `sina[27]` | `tencent[25]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9481, LOO稳号=True |
| `sina[27]` | `tencent[23]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9481, LOO稳号=True |
| `sina[27]` | `tencent[21]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9481, LOO稳号=True |
| `sina[25]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9831, Spearman=0.7395, LOO稳号=True |
| `sina[25]` | `tencent[27]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9481, LOO稳号=True |
| `sina[25]` | `tencent[25]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9481, LOO稳号=True |
| `sina[25]` | `tencent[23]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9481, LOO稳号=True |
| `sina[25]` | `tencent[21]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9481, LOO稳号=True |
| `sina[24]` | `tencent[24]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9862, Spearman=0.9501, LOO稳号=True |
| `sina[23]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9831, Spearman=0.7401, LOO稳号=True |
| `sina[23]` | `tencent[27]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9482, LOO稳号=True |
| `sina[23]` | `tencent[25]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9482, LOO稳号=True |
| `sina[23]` | `tencent[23]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9482, LOO稳号=True |
| `sina[23]` | `tencent[21]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9482, LOO稳号=True |
| `sina[19]` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9831, Spearman=0.9116, LOO稳号=True |
| `sina[19]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9832, Spearman=0.8006, LOO稳号=True |
| `sina[19]` | `tencent[17]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9463, LOO稳号=True |
| `sina[19]` | `tencent[15]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9462, LOO稳号=True |
| `sina[19]` | `tencent[13]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9462, LOO稳号=True |
| `sina[19]` | `tencent[11]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9462, LOO稳号=True |
| `sina[17]` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9831, Spearman=0.9116, LOO稳号=True |
| `sina[17]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9832, Spearman=0.8004, LOO稳号=True |
| `sina[17]` | `tencent[17]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9463, LOO稳号=True |
| `sina[17]` | `tencent[15]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9463, LOO稳号=True |
| `sina[17]` | `tencent[13]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9463, LOO稳号=True |
| `sina[17]` | `tencent[11]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9463, LOO稳号=True |
| `sina[16]` | `tencent[16]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9966, Spearman=0.9515, LOO稳号=True |
| `sina[15]` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9831, Spearman=0.9116, LOO稳号=True |
| `sina[15]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9832, Spearman=0.8002, LOO稳号=True |
| `sina[15]` | `tencent[17]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9462, LOO稳号=True |
| `sina[15]` | `tencent[15]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9462, LOO稳号=True |
| `sina[15]` | `tencent[13]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9463, LOO稳号=True |
| `sina[15]` | `tencent[11]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9462, LOO稳号=True |
| `sina[14]` | `tencent[14]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9977, Spearman=0.957, LOO稳号=True |
| `sina[13]` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9831, Spearman=0.9116, LOO稳号=True |
| `sina[13]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9832, Spearman=0.8001, LOO稳号=True |
| `sina[13]` | `tencent[17]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9463, LOO稳号=True |
| `sina[13]` | `tencent[15]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9463, LOO稳号=True |
| `sina[13]` | `tencent[13]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9463, LOO稳号=True |
| `sina[13]` | `tencent[11]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9833, Spearman=0.9463, LOO稳号=True |
| `sina[11]` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9831, Spearman=0.9295, LOO稳号=True |
| `sina[11]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9832, Spearman=0.7815, LOO稳号=True |
| `sina[11]` | `tencent[5]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9838, Spearman=0.9614, LOO稳号=True |
| `sina[11]` | `tencent[51]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9835, Spearman=0.9634, LOO稳号=True |
| `sina[11]` | `tencent[42]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9836, Spearman=0.9622, LOO稳号=True |
| `sina[11]` | `tencent[41]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9836, Spearman=0.963, LOO稳号=True |
| `sina[11]` | `tencent[3]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9835, Spearman=0.9522, LOO稳号=True |
| `sina[11]` | `tencent[34]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9836, Spearman=0.9622, LOO稳号=True |
| `sina[11]` | `tencent[33]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9836, Spearman=0.963, LOO稳号=True |
| `sina[11]` | `tencent[17]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9832, Spearman=0.9281, LOO稳号=True |
| `sina[11]` | `tencent[15]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9832, Spearman=0.9282, LOO稳号=True |
| `sina[11]` | `tencent[13]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9832, Spearman=0.9282, LOO稳号=True |
| `sina[11]` | `tencent[11]` | robust_correlation, affine_formula, per_stock_time_series | 757 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tencent | Pearson=0.9832, Spearman=0.9282, LOO稳号=True |
| `sina[29]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 700 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9825, Spearman=0.9699, LOO稳号=True |
| `sina[27]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 700 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9825, Spearman=0.9699, LOO稳号=True |
| `sina[25]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 700 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9825, Spearman=0.9699, LOO稳号=True |
| `sina[23]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 700 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9825, Spearman=0.9699, LOO稳号=True |
| `sina[19]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 700 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9759, LOO稳号=True |
| `sina[17]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 700 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9759, LOO稳号=True |
| `sina[15]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 700 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9759, LOO稳号=True |
| `sina[13]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 700 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9999, Spearman=0.9759, LOO稳号=True |
| `sina[11]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 700 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9825, Spearman=0.951, LOO稳号=True |
| `sina[11]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 700 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=1.0, Spearman=0.9938, LOO稳号=True |
| `sina[11]` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 698 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9829, Spearman=0.9583, LOO稳号=True |
| `sina[11]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 698 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9827, Spearman=0.9592, LOO稳号=True |
| `sina[11]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 698 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | sina, tdx | Pearson=0.9826, Spearman=0.96, LOO稳号=True |
| `tencent[17]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 697 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, tencent | Pearson=0.9816, Spearman=0.929, LOO稳号=True |
| `tencent[15]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 697 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, tencent | Pearson=0.9816, Spearman=0.929, LOO稳号=True |
| `tencent[13]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 697 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, tencent | Pearson=0.9816, Spearman=0.929, LOO稳号=True |
| `tencent[11]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 697 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, tencent | Pearson=0.9816, Spearman=0.929, LOO稳号=True |
| `zhb.full.high_52w` | `tencent[68]` | robust_correlation, affine_formula, per_stock_time_series | 622 | T:20260812, T:20260819, T:20260821, T:20260824, T:20260825, T:20260826 | tencent, zhb | Pearson=0.9992, Spearman=0.934, LOO稳号=True |
| `zhb.full.high_52w` | `tencent[67]` | robust_correlation, affine_formula, per_stock_time_series | 622 | T:20260812, T:20260819, T:20260821, T:20260824, T:20260825, T:20260826 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_ytd` | `tencent[75]` | robust_correlation, affine_formula, per_stock_time_series | 622 | T:20260812, T:20260819, T:20260821, T:20260824, T:20260825, T:20260826 | tencent, zhb | Pearson=0.9816, Spearman=0.952, LOO稳号=True |
| `zhb.full.change_ytd` | `tencent[62]` | robust_correlation, affine_formula, per_stock_time_series | 622 | T:20260812, T:20260819, T:20260821, T:20260824, T:20260825, T:20260826 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_pct` | `tencent[32]` | robust_correlation, affine_formula, per_stock_time_series | 622 | T:20260812, T:20260819, T:20260821, T:20260824, T:20260825, T:20260826 | tencent, zhb | Pearson=0.9823, Spearman=0.9944, LOO稳号=True |
| `zhb.full.change_60k_bar` | `tencent[71]` | robust_correlation, affine_formula, per_stock_time_series | 622 | T:20260812, T:20260819, T:20260821, T:20260824, T:20260825, T:20260826 | tencent, zhb | Pearson=0.9966, Spearman=0.977, LOO稳号=True |
| `zhb.full.change_60d` | `tencent[71]` | robust_correlation, affine_formula, per_stock_time_series | 622 | T:20260812, T:20260819, T:20260821, T:20260824, T:20260825, T:20260826 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_250k_bar` | `tencent[79]` | robust_correlation, affine_formula, per_stock_time_series | 622 | T:20260812, T:20260819, T:20260821, T:20260824, T:20260825, T:20260826 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_20k_bar` | `tencent[70]` | robust_correlation, affine_formula, per_stock_time_series | 622 | T:20260812, T:20260819, T:20260821, T:20260824, T:20260825, T:20260826 | tencent, zhb | Pearson=0.9917, Spearman=0.9649, LOO稳号=True |
| `zhb.full.change_10k_bar` | `tencent[69]` | robust_correlation, affine_formula, per_stock_time_series | 622 | T:20260812, T:20260819, T:20260821, T:20260824, T:20260825, T:20260826 | tencent, zhb | Pearson=0.9867, Spearman=0.9275, LOO稳号=True |
| `ulist239.f45` | `tdx.finance_info.yingyelirun` | robust_correlation, affine_formula, per_stock_time_series | 600 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9913, Spearman=0.9642, LOO稳号=True |
| `ulist239.f45` | `tdx.finance_info.shuihoulirun` | robust_correlation, affine_formula, per_stock_time_series | 600 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9949, Spearman=0.9972, LOO稳号=True |
| `ulist239.f45` | `tdx.finance_info.lirunzonghe` | robust_correlation, affine_formula, per_stock_time_series | 600 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.9913, Spearman=0.9854, LOO稳号=True |
| `ulist239.f45` | `tdx.finance_info.jinglirun` | robust_correlation, affine_formula, per_stock_time_series | 600 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824 | tdx, ulist239 | Pearson=0.995, Spearman=0.9984, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 七、日期与数据质量告警（360）

- 20260920: 旧式非交易日目录按前一交易日 20260918 归并；目录未改名
- 20261005: 旧式非交易日目录按前一交易日 20260930 归并；目录未改名
- 20261011: 旧式非交易日目录按前一交易日 20261009 归并；目录未改名
- 20261017: 旧式非交易日目录按前一交易日 20261016 归并；目录未改名
- 20261018: 旧式非交易日目录按前一交易日 20261016 归并；目录未改名
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
- 另有 260 条告警，详见同名 JSON 报告。

---

> 数据来源：通达信 / 项目字段对撞体系。以上为方法论梳理，不构成投资建议。

## 来源身份核验（不参与字段语义定案）

> 仅核验已登记的 FTShare 接口。需 3 个不同的已完成交易数据日、每日至少 18 只股票的完整记录逐项匹配；项目数据日和各来源 as_of_date 必须一致，盘前、周末或节假日采集也可计入；结果不会改变主字典或确认 FTShare 来源独立性。

运行上冗余的接口每累计 20 个后续有效交易数据日复核一次；字段或适配器契约变化会恢复采集，需重新积累完整证据。

| 字段接口 | 状态 | 对照来源 | 证据交易日 | 说明 |
|:--|:--|:--|:--|:--|
| comment_desire | pending | — | — | not enough matching completed trading-date samples |
| comment_focus | pending | — | — | not enough matching completed trading-date samples |
| comment_org | pending | — | — | not enough matching completed trading-date samples |
| comment_score | pending | — | — | not enough matching completed trading-date samples |
| ggmx | pending | — | — | not enough matching completed trading-date samples |
| goodwill_detail | pending | — | — | not enough matching completed trading-date samples |

## AxData / FTShare 每日轮验（不作为独立字段锚）

> 此处汇总采集目录已保存的本地证据，不发起网络请求、不改变注册表状态；AxData 是多源框架，FTShare 底层来源族仍须单独核实。

### AxData

窗口内有 6 个唯一数据日的轮验记录；重复目录合并 0 条。
静态接口队列：257 个接口，3343 个字段出现项，低于 E3 的字段出现项 3343；当前主动探针白名单 `tencent_realtime_snapshot`。
静态候选策略：static review only until route, parameters, date basis, and request safety are approved。

| 数据日 | 轮验状态 | 探针状态 / 请求数 | 来源身份状态 | 短线配对 | KPH/KPL 配对 | 证据文件 |
|:--|:--|:--|:--|--:|--:|:--|
| 20261009 | not_eligible | not_run / 0 (字段相同/不同 0/0) | 未记录 | — | — | meta_summary |
| 20261012 | not_eligible | not_run / 0 (字段相同/不同 0/0) | 未记录 | — | — | meta_summary |
| 20261013 | not_eligible | not_run / 0 (字段相同/不同 0/0) | 未记录 | — | — | meta_summary |
| 20261014 | sampled | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 0 | — | full |
| 20261015 | probe_skipped | skipped_project_counterpart_failed / 0 (字段相同/不同 0/0) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 0 | — | full |
| 20261016 | sampled | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | 47 | full |

被动逐字段比较中的差异计数（跨本窗口唯一数据日累加，不含原始值）：

| 比较路径 | 相同 | 不同 | 缺失/双方空值 |
|:--|--:|--:|--:|
| `kph_limit_up_history_vs_kpl_detail:seal_amount` | 0 | 47 | 0 |
| `kph_limit_up_history_vs_kpl_detail:seal_money` | 0 | 47 | 0 |
| `axdata_shortline_vs_eltdx:alignment_status` | 0 | 20 | 0 |
| `axdata_shortline_vs_eltdx:beta_60d` | 0 | 20 | 0 |
| `axdata_shortline_vs_eltdx:code` | 0 | 20 | 0 |
| `axdata_shortline_vs_eltdx:full_code` | 0 | 20 | 0 |
| `axdata_shortline_vs_eltdx:instrument_id` | 0 | 20 | 0 |
| `axdata_shortline_vs_eltdx:limit_status` | 0 | 20 | 0 |
| `axdata_shortline_vs_eltdx:market_id` | 0 | 20 | 0 |
| `axdata_shortline_vs_eltdx:opening_rush` | 0 | 20 | 0 |
| `axdata_shortline_vs_eltdx:pe_ttm` | 0 | 20 | 0 |
| `axdata_shortline_vs_eltdx:previous_trade_date` | 0 | 20 | 0 |
| `axdata_shortline_vs_eltdx:symbol` | 0 | 20 | 0 |
| `axdata_shortline_vs_eltdx:target_trade_date` | 0 | 20 | 0 |
| `axdata_shortline_vs_eltdx:tdx_code` | 0 | 20 | 0 |
| `axdata_shortline_vs_eltdx:open_amount` | 5 | 15 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_hand` | 5 | 15 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_ratio` | 5 | 15 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_amount_ratio` | 6 | 14 | 0 |
| `axdata_shortline_vs_eltdx:auction_prev_volume_ratio` | 7 | 13 | 0 |
| `axdata_shortline_vs_eltdx:open_turnover_z` | 12 | 8 | 0 |
| `axdata_shortline_vs_eltdx:ladder_level` | 0 | 2 | 18 |
| `axdata_shortline_vs_eltdx:open_prev_seal_ratio` | 0 | 1 | 19 |

### FTShare 每日身份核验记录

窗口内保留 5 个唯一数据日的采集时记录；重复目录合并 0 条。

| 数据日 | 核验状态 | 接口状态计数 |
|:--|:--|:--|
| 20261012 | ok | pending: 6 |
| 20261013 | ok | pending: 6 |
| 20261014 | ok | pending: 6 |
| 20261015 | ok | pending: 6 |
| 20261016 | ok | pending: 6 |

## 字母字段名语义提示（仅候选）

窗口内观察到 247 条需审阅的字母字段路径：含词义线索 80 条，仅拆词 167 条。
完整逐条记录保存在碰撞 JSON；名称线索清单：`docs/field_verification/20261014/20261014_alphabetic_field_name_inventory.csv`。
> 拼音、英文、缩写和混合拆词只用于检索候选；必须结合原始值、接口定义和独立来源复核，不得据此定案或改写主字典。

| 逐源字段路径 | 状态/审阅范围 | 名称形式与拆词 | 词义线索（非释义） | 样本日期 |
|:--|:--|:--|:--|:--|
| `市场源(market_sources)::change_type` | unverified / unverified_semantics | snake_case_or_mixed: change type | 变化/涨跌 + 类型 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `市场源(market_sources)::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `东财-push2ex::change_pct` | unverified / unverified_semantics | recognized_english_word_candidate: change pct | 变化/涨跌 + 百分比 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::first_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: first limit time | 首次/第一 + 涨跌停限制 + 时间 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::last_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: last limit time | 最近/上一期 + 涨跌停限制 + 时间 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::limit_count` | unverified / unverified_semantics | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::name` | unverified / unverified_semantics | recognized_english_word_candidate: name | 名称 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::price` | unverified / unverified_semantics | recognized_english_word_candidate: price | 价格 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::total_value` | unverified / unverified_semantics | snake_case_or_mixed: total value | 总 + 值 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261014, T:20261016 |
| `市场源(market_sources)::limit_count` | verified / verified_metadata_gap | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `市场源(market_sources)::limit_time` | unverified / unverified_semantics | snake_case_or_mixed: limit time | 涨跌停限制 + 时间 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `市场源(market_sources)::plate_limit_up_count` | verified / verified_metadata_gap | snake_case_or_mixed: plate limit up count | 涨跌停限制 + 上/涨 + 数量/次数 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `财联社(cls)::time` | unverified / unverified_semantics | recognized_english_word_candidate: time | 时间 | C:20260812, C:20260813, C:20260814, C:20260819, C:20260820, C:20260822, C:20260824, C:20260825, C:20260826, C:20260827, C:20260828, C:20260831, C:20260901, C:20260902, C:20260903, C:20260904, C:20260907, C:20260908, C:20260909, C:20260910, C:20260911, C:20260914, C:20260915, C:20260916, C:20260917, C:20260918, C:20260920, C:20260921, C:20260923, C:20260924, C:20260928, C:20260930, C:20261005, C:20261008, C:20261010, C:20261011, C:20261014, C:20261016 |
| `东财-热榜(em_hot)::code` | verified / verified_metadata_gap | recognized_english_word_candidate: code | 代码 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260923, T:20260924, T:20260930 |
| `东财-热榜(em_hot)::name` | verified / verified_metadata_gap | recognized_english_word_candidate: name | 名称 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260923, T:20260924, T:20260930 |
| `同花顺-fuyao::name` | unverified / unverified_semantics | recognized_english_word_candidate: name | 名称 | T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930 |
| `TDX(双命名源)::changqifuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: changqifuzhai | 长期负债 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::cunhuo` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: cunhuo | 存货 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::gudongrenshu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: gudongrenshu | 股东人数 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::ipodate` | unverified / unverified_semantics | recognized_english_phrase_candidate: ipodate | IPO/上市日期（字段语境候选） | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::jinglirun` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jinglirun | 净利润 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::jingyingxianjinliu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingyingxianjinliu | 经营现金流 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::jingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingzichan | 净资产 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::liudongfuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: liudongfuzhai | 流动负债 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::meigujingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: meigujingzichan | 每股净资产 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::yingshouzhangkuan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: yingshouzhangkuan | 应收账款 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::zhuyingshouru` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zhuyingshouru | 主营收入 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::zibengongjijin` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zibengongjijin | 资本公积金 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::zongzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongzichan | 总资产 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `ZHB-tdxstat::change_pct` | unverified / unverified_semantics | recognized_english_word_candidate: change pct | 变化/涨跌 + 百分比 | T:20260811, T:20260812, T:20260817, T:20260819, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260922, T:20260923, T:20260924, T:20260929, T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::change_pct_1d` | unverified / unverified_semantics | snake_case_or_mixed: change pct 1 d | 变化/涨跌 + 百分比 | T:20260811, T:20260812, T:20260817, T:20260819, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260922, T:20260923, T:20260924, T:20260929, T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::change_pct_2d` | unverified / unverified_semantics | snake_case_or_mixed: change pct 2 d | 变化/涨跌 + 百分比 | T:20260811, T:20260812, T:20260817, T:20260819, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260922, T:20260923, T:20260924, T:20260929, T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::main_net_buy_amount` | unverified / unverified_semantics | snake_case_or_mixed: main net buy amount | 净 + 金额/成交额（需看接口） | T:20260811, T:20260812, T:20260817, T:20260819, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260922, T:20260923, T:20260924, T:20260929, T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::main_net_buy_amount_1d` | unverified / unverified_semantics | snake_case_or_mixed: main net buy amount 1 d | 净 + 金额/成交额（需看接口） | T:20260811, T:20260812, T:20260817, T:20260819, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260922, T:20260923, T:20260924, T:20260929, T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `同花顺-fuyao::snapshot.open_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot open price | 开盘 + 价格 | T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261014, T:20261016 |
| `同花顺-fuyao::valuation.pb_mrq` | conflict / unverified_semantics | snake_case_or_mixed: valuation pb mrq | 市净率 + 最近报告期 | T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261014, T:20261016 |
| `同花顺-fuyao::valuation.pe_mrq` | conflict / unverified_semantics | snake_case_or_mixed: valuation pe mrq | 市盈率 + 最近报告期 | T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261014, T:20261016 |
| `同花顺-fuyao::valuation.pe_ttm` | conflict / unverified_semantics | snake_case_or_mixed: valuation pe ttm | 市盈率 + 滚动十二个月 | T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261014, T:20261016 |
| `TDX(双命名源)::b_gu` | unverified / unverified_semantics | snake_case_or_mixed: b gu | B股 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::faren_gu` | unverified / unverified_semantics | snake_case_or_mixed: faren gu | 法人股 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::guding_zichan` | unverified / unverified_semantics | snake_case_or_mixed: guding zichan | 固定资产 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::h_gu` | unverified / unverified_semantics | snake_case_or_mixed: h gu | H股 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::jing_lirun` | unverified / unverified_semantics | snake_case_or_mixed: jing lirun | 净利润 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::jing_zichan` | unverified / unverified_semantics | snake_case_or_mixed: jing zichan | 净资产 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::jingying_xianjinliu` | unverified / unverified_semantics | snake_case_or_mixed: jingying xianjinliu | 经营现金流（不确定净额/总额口径） | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::liudong_fuzhai` | unverified / unverified_semantics | snake_case_or_mixed: liudong fuzhai | 流动负债 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::liudong_zichan` | unverified / unverified_semantics | snake_case_or_mixed: liudong zichan | 流动资产 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::liutong_guben` | unverified / unverified_semantics | snake_case_or_mixed: liutong guben | 流通股本 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::meigujing_zichan` | unverified / unverified_semantics | snake_case_or_mixed: meigujing zichan | 每股净资产 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::yingye_lirun` | unverified / unverified_semantics | snake_case_or_mixed: yingye lirun | 营业利润 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::zhuying_lirun` | unverified / unverified_semantics | snake_case_or_mixed: zhuying lirun | 主营利润（候选） | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::zhuying_shouru` | unverified / unverified_semantics | snake_case_or_mixed: zhuying shouru | 主营收入 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::zong_guben` | unverified / unverified_semantics | snake_case_or_mixed: zong guben | 总股本 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::zong_xianjinliu` | unverified / unverified_semantics | snake_case_or_mixed: zong xianjinliu | 总现金流（接口口径待核） | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::zong_zichan` | unverified / unverified_semantics | snake_case_or_mixed: zong zichan | 总资产 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::zongguben` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongguben | 总股本 | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::eps` | unverified / unverified_semantics | recognized_english_word_candidate: eps | 每股收益 | T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::fajirenfarengu` | unverified / unverified_semantics | recognized_pinyin_phrase_candidate: fajirenfarengu | 疑似 faqirenfarengu 的拼写变体；含义未证实 | T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::zhongguben` | unverified / unverified_semantics | recognized_pinyin_phrase_candidate: zhongguben | 疑似 zongguben 的拼写差异；含义未证实 | T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `开盘红(Levistock适配)::limit_count` | unverified / unverified_semantics | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261009, T:20261013, T:20261016 |
| `开盘红(Levistock适配)::open_time` | unverified / unverified_semantics | snake_case_or_mixed: open time | 开盘 + 时间 | T:20261009, T:20261013, T:20261016 |
| `市场源(market_sources)::CHANGE_TYPE` | unverified / unverified_semantics | uppercase_code_or_acronym: CHANGE TYPE | 变化/涨跌 + 类型 | T:20260928, T:20260929, T:20260930 |
| `市场源(market_sources)::CLOSE_PRICE` | unverified / unverified_semantics | uppercase_code_or_acronym: CLOSE PRICE | 收盘 + 价格 | T:20260928, T:20260929, T:20260930 |
| `市场源(market_sources)::DEAL_AMOUNT_RATIO` | unverified / unverified_semantics | uppercase_code_or_acronym: DEAL AMOUNT RATIO | 金额/成交额（需看接口） + 比率 | T:20260928, T:20260929, T:20260930 |
| `市场源(market_sources)::DEAL_NET_RATIO` | unverified / unverified_semantics | uppercase_code_or_acronym: DEAL NET RATIO | 净 + 比率 | T:20260928, T:20260929, T:20260930 |
| `市场源(market_sources)::MARKET` | unverified / unverified_semantics | recognized_english_word_candidate: MARKET | 市场 | T:20260928, T:20260929, T:20260930 |
| `市场源(market_sources)::SECURITY_TYPE_CODE` | unverified / unverified_semantics | uppercase_code_or_acronym: SECURITY TYPE CODE | 类型 + 代码 | T:20260928, T:20260929, T:20260930 |
| `市场源(market_sources)::TRADE_MARKET_CODE` | unverified / unverified_semantics | uppercase_code_or_acronym: TRADE MARKET CODE | 市场 + 代码 | T:20260928, T:20260929, T:20260930 |
| `市场源(market_sources)::FREE_MARKET_CAP` | unverified / unverified_semantics | uppercase_code_or_acronym: FREE MARKET CAP | 自由 + 市场 + 市值/资本（需看接口） | T:20260928, T:20260929, T:20260930 |
| `reports::actualLastTwoYearEps` | unverified / unverified_semantics | camel_case_or_mixed: actual Last Two Year Eps | 最近/上一期 + 每股收益 | C:20260816, C:20260817, C:20260818, C:20260819, C:20260821, C:20260824, C:20260825, C:20260826, C:20260827, C:20260828, C:20260829, C:20260830, C:20260831, C:20260902, C:20260903, C:20260907, C:20260909, C:20260921 |
| `reports::actualLastYearEps` | unverified / unverified_semantics | camel_case_or_mixed: actual Last Year Eps | 最近/上一期 + 每股收益 | C:20260816, C:20260817, C:20260818, C:20260819, C:20260821, C:20260824, C:20260825, C:20260826, C:20260827, C:20260828, C:20260829, C:20260830, C:20260831, C:20260902, C:20260903, C:20260907, C:20260909, C:20260921 |
| `reports::count` | verified / verified_metadata_gap | recognized_english_word_candidate: count | 数量/次数 | C:20260816, C:20260817, C:20260818, C:20260819, C:20260821, C:20260824, C:20260825, C:20260826, C:20260827, C:20260828, C:20260829, C:20260830, C:20260831, C:20260902, C:20260903, C:20260907, C:20260909, C:20260921 |
| `reports::lastEmRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Code | 最近/上一期 + 代码 | C:20260816, C:20260817, C:20260818, C:20260819, C:20260821, C:20260824, C:20260825, C:20260826, C:20260827, C:20260828, C:20260829, C:20260830, C:20260831, C:20260902, C:20260903, C:20260907, C:20260909, C:20260921 |
| `reports::lastEmRatingName` | conflict / unverified_semantics | camel_case_or_mixed: last Em Rating Name | 最近/上一期 + 名称 | C:20260816, C:20260817, C:20260818, C:20260819, C:20260821, C:20260824, C:20260825, C:20260826, C:20260827, C:20260828, C:20260829, C:20260830, C:20260831, C:20260902, C:20260903, C:20260907, C:20260909, C:20260921 |
| `reports::lastEmRatingValue` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Value | 最近/上一期 + 值 | C:20260816, C:20260817, C:20260818, C:20260819, C:20260821, C:20260824, C:20260825, C:20260826, C:20260827, C:20260828, C:20260829, C:20260830, C:20260831, C:20260902, C:20260903, C:20260907, C:20260909, C:20260921 |
| `reports::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | C:20260816, C:20260817, C:20260818, C:20260819, C:20260821, C:20260824, C:20260825, C:20260826, C:20260827, C:20260828, C:20260829, C:20260830, C:20260831, C:20260902, C:20260903, C:20260907, C:20260909, C:20260921 |
| `reports::predictLastYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Eps | 最近/上一期 + 每股收益 | C:20260816, C:20260817, C:20260818, C:20260819, C:20260821, C:20260824, C:20260825, C:20260826, C:20260827, C:20260828, C:20260829, C:20260830, C:20260831, C:20260902, C:20260903, C:20260907, C:20260909, C:20260921 |
| `reports::predictLastYearPe` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Pe | 最近/上一期 + 市盈率 | C:20260816, C:20260817, C:20260818, C:20260819, C:20260821, C:20260824, C:20260825, C:20260826, C:20260827, C:20260828, C:20260829, C:20260830, C:20260831, C:20260902, C:20260903, C:20260907, C:20260909, C:20260921 |
| `TDX-eltdx(适配层)::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `东财-push2ex::broken_count` | unverified / unverified_semantics | snake_case_or_mixed: broken count | — | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::circulating_value` | unverified / unverified_semantics | snake_case_or_mixed: circulating value | — | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::limit_fund` | unverified / unverified_semantics | snake_case_or_mixed: limit fund | — | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::sector` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: sector | — | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::turnover_rate` | unverified / unverified_semantics | snake_case_or_mixed: turnover rate | — | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::zt_continuous` | unverified / unverified_semantics | snake_case_or_mixed: zt continuous | — | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::zt_days` | unverified / unverified_semantics | snake_case_or_mixed: zt days | — | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260930, T:20261008, T:20261014, T:20261016 |
| `市场源(market_sources)::one_word` | unverified / unverified_semantics | snake_case_or_mixed: one word | — | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `市场源(market_sources)::plate_amount` | verified / verified_metadata_gap | snake_case_or_mixed: plate amount | — | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `市场源(market_sources)::plate_code` | verified / verified_metadata_gap | snake_case_or_mixed: plate code | — | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `市场源(market_sources)::plate_name` | verified / verified_metadata_gap | snake_case_or_mixed: plate name | — | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `市场源(market_sources)::popular` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: popular | — | T:20260812, T:20260813, T:20260819, T:20260820, T:20260821, T:20260824, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `财联社(cls)::content` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: content | — | C:20260812, C:20260813, C:20260814, C:20260819, C:20260820, C:20260822, C:20260824, C:20260825, C:20260826, C:20260827, C:20260828, C:20260831, C:20260901, C:20260902, C:20260903, C:20260904, C:20260907, C:20260908, C:20260909, C:20260910, C:20260911, C:20260914, C:20260915, C:20260916, C:20260917, C:20260918, C:20260920, C:20260921, C:20260923, C:20260924, C:20260928, C:20260930, C:20261005, C:20261008, C:20261010, C:20261011, C:20261014, C:20261016 |
| `财联社(cls)::level` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: level | — | C:20260812, C:20260813, C:20260814, C:20260819, C:20260820, C:20260822, C:20260824, C:20260825, C:20260826, C:20260827, C:20260828, C:20260831, C:20260901, C:20260902, C:20260903, C:20260904, C:20260907, C:20260908, C:20260909, C:20260910, C:20260911, C:20260914, C:20260915, C:20260916, C:20260917, C:20260918, C:20260920, C:20260921, C:20260923, C:20260924, C:20260928, C:20260930, C:20261005, C:20261008, C:20261010, C:20261011, C:20261014, C:20261016 |
| `财联社(cls)::reading_num` | unverified / unverified_semantics | snake_case_or_mixed: reading num | — | C:20260812, C:20260813, C:20260814, C:20260819, C:20260820, C:20260822, C:20260824, C:20260825, C:20260826, C:20260827, C:20260828, C:20260831, C:20260901, C:20260902, C:20260903, C:20260904, C:20260907, C:20260908, C:20260909, C:20260910, C:20260911, C:20260914, C:20260915, C:20260916, C:20260917, C:20260918, C:20260920, C:20260921, C:20260923, C:20260924, C:20260928, C:20260930, C:20261005, C:20261008, C:20261010, C:20261011, C:20261014, C:20261016 |
| `财联社(cls)::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20260812, C:20260813, C:20260814, C:20260819, C:20260820, C:20260822, C:20260824, C:20260825, C:20260826, C:20260827, C:20260828, C:20260831, C:20260901, C:20260902, C:20260903, C:20260904, C:20260907, C:20260908, C:20260909, C:20260910, C:20260911, C:20260914, C:20260915, C:20260916, C:20260917, C:20260918, C:20260920, C:20260921, C:20260923, C:20260924, C:20260928, C:20260930, C:20261005, C:20261008, C:20261010, C:20261011, C:20261014, C:20261016 |
| `同花顺-fuyao::heat` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: heat | — | T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930 |
| `同花顺-fuyao::rank` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: rank | — | T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930 |
| `同花顺-fuyao::rank_change` | unverified / unverified_semantics | snake_case_or_mixed: rank change | — | T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930 |
| `同花顺-fuyao::rank_trend` | unverified / unverified_semantics | snake_case_or_mixed: rank trend | — | T:20260824, T:20260825, T:20260826, T:20260827, T:20260828, T:20260831, T:20260901, T:20260902, T:20260903, T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914, T:20260915, T:20260916, T:20260917, T:20260918, T:20260921, T:20260923, T:20260924, T:20260928, T:20260929, T:20260930 |

Markdown 显示前 100 条；其余 147 条完整保留在 JSON。

## 探索候选持续跟踪

研究台账：`collision_research_state.json.gz`；累计历史跟踪候选对 1542，本报告候选对 824，历史复现 783，新发现 41。
台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，不会自动改变字段状态、碰撞锚或主字典。新报告只将 `actionable_L1`、L4 和主动方法候选写入待研究队列；已登记关系的复验单独展示，历史跟踪记录不会被删除。
