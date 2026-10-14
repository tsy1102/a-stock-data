# 全源对撞报告（20261012）

> 行情窗口：20260924 ~ 20261012（7 个不同交易日）｜字段 1197 个｜样本值 438599 条
> 新闻/公告自然日窗口：20261006 ~ 20261012
> 主攻目标（unverified）=370｜新增 L1/L1-U 定案=0｜异号同义 17 / 同号镜像 0

> **规则**：每个定案日有效样本≥18，命中率≥90%，至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 定案候选 — 异号同义（跨编号，高价值）(17)

| 左字段(unverified) | 右字段 | 等级 | 命中率 | 天数 | 样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|:--|:--|
| `tencent[10]` | `ulist239.f211` | L1 | 100.00% | 4 | 80 | - |  | ✅ |
| `zhb.full.change_pct` | `tencent[32]` | L1 | 100.00% | 3 | 60 | - |  | ✅ |
| `zhb.full.change_20d` | `tencent[70]` | L1 | 100.00% | 3 | 60 | - |  | ✅ |
| `zhb.full.change_30d` | `tencent[70]` | L1 | 100.00% | 3 | 60 | - |  | ✅ |
| `zhb.full.high_52w` | `tencent[67]` | L1 | 95.00% | 3 | 60 | - |  | ✅ |
| `tdx.finance_info.liutongguben` | `tencent[72]` | L1-U | 100.00% | 7 | 140 | 10000 |  | — |
| `tdx.finance_info.liutongguben` | `tencent[76]` | L1-U | 100.00% | 7 | 140 | 10000 |  | — |
| `tdx.finance_info.liutongguben` | `ulist239.f39` | L1-U | 100.00% | 4 | 80 | 10000 |  | — |
| `tdx.finance_info.zongzichan` | `ulist239.f50` | L1-U | 100.00% | 4 | 80 | 0.1 |  | — |
| `tdx.finance_info.liudongzichan` | `ulist239.f51` | L1-U | 100.00% | 4 | 76 | 0.1 |  | — |
| `tdx.finance_info.gudingzichan` | `ulist239.f52` | L1-U | 100.00% | 4 | 80 | 0.1 |  | — |
| `tdx.finance_info.liudongfuzhai` | `ulist239.f55` | L1-U | 100.00% | 4 | 76 | 0.1 |  | — |
| `tdx.finance_info.zibengongjijin` | `ulist239.f60` | L1-U | 100.00% | 4 | 80 | 0.1 |  | — |
| `tdx.finance_info.yingyelirun` | `ulist239.f42` | L1-U | 100.00% | 4 | 80 | 0.1 |  | — |
| `tdx.finance_info.lirunzonghe` | `ulist239.f44` | L1-U | 100.00% | 4 | 80 | 0.1 |  | — |
| `tdx.finance_info.weifenlirun` | `ulist239.f47` | L1-U | 100.00% | 4 | 80 | 0.1 |  | — |
| `zhb.full.pe_ttm` | `tencent[39]` | L1 | 98.33% | 3 | 60 | - |  | — |

## 二、L1 / L1-U 定案候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、L4 存疑候选（168）

| 左字段 | 右字段 | 命中率 | 天数 | 样本 |
|:--|:--|--:|--:|--:|
| `fuyao.auction_final.auction_price` | `eltdx.shortline.open_price` | 100.00% | 3 | 54 |
| `fuyao.auction_final.auction_price` | `push2.f46` | 100.00% | 2 | 29 |
| `fuyao.auction_final.auction_price` | `sina[1]` | 100.00% | 4 | 78 |
| `fuyao.auction_final.auction_price` | `tdx.quote_full.open` | 100.00% | 4 | 78 |
| `fuyao.auction_final.auction_price` | `tencent[5]` | 100.00% | 4 | 78 |
| `fuyao.auction_final.auction_price` | `ulist239.f17` | 100.00% | 3 | 59 |
| `fuyao.auction_final.pre_close_price` | `eltdx.quote_snapshot.pre_close_price` | 100.00% | 4 | 72 |
| `fuyao.auction_final.pre_close_price` | `eltdx.shortline.pre_close` | 100.00% | 3 | 54 |
| `fuyao.auction_final.pre_close_price` | `push2.f60` | 100.00% | 2 | 30 |
| `fuyao.auction_final.pre_close_price` | `ulist239.f18` | 100.00% | 3 | 60 |
| `fuyao.auction_final.open_price` | `eltdx.quote_snapshot.open_price` | 100.00% | 3 | 54 |
| `fuyao.auction_final.open_price` | `eltdx.shortline.open_price` | 100.00% | 3 | 54 |
| `fuyao.auction_final.open_price` | `push2.f46` | 100.00% | 2 | 30 |
| `fuyao.auction_final.open_price` | `sina[1]` | 100.00% | 3 | 60 |
| `fuyao.auction_final.open_price` | `tdx.quote_full.open` | 100.00% | 3 | 60 |
| `fuyao.auction_final.open_price` | `tencent[5]` | 100.00% | 3 | 60 |
| `fuyao.auction_final.open_price` | `ulist239.f17` | 100.00% | 3 | 60 |
| `fuyao.auction_final.last_price` | `eltdx.quote_snapshot.last_price` | 100.00% | 3 | 54 |
| `fuyao.auction_final.last_price` | `push2.f43` | 100.00% | 2 | 30 |
| `fuyao.auction_final.last_price` | `push2.f179` | 100.00% | 2 | 30 |
| `fuyao.auction_final.last_price` | `sina[3]` | 100.00% | 3 | 60 |
| `fuyao.auction_final.last_price` | `tdx.quote_full.price` | 100.00% | 3 | 60 |
| `fuyao.auction_final.last_price` | `tencent[3]` | 100.00% | 3 | 60 |
| `fuyao.auction_final.last_price` | `ulist239.f2` | 100.00% | 3 | 60 |
| `fuyao.auction_final.last_price` | `ulist239.f144` | 100.00% | 3 | 60 |
| `sina[11]` | `tdx.quote_full.bid1` | 100.00% | 7 | 140 |
| `sina[11]` | `tencent[9]` | 100.00% | 7 | 140 |
| `sina[11]` | `ulist239.f31` | 100.00% | 4 | 80 |
| `sina[13]` | `tencent[11]` | 100.00% | 7 | 140 |
| `sina[13]` | `ulist239.f142` | 100.00% | 4 | 80 |
| `sina[15]` | `tencent[13]` | 100.00% | 7 | 140 |
| `sina[17]` | `tencent[15]` | 100.00% | 7 | 140 |
| `sina[19]` | `tencent[17]` | 100.00% | 7 | 140 |
| `sina[23]` | `tencent[21]` | 100.00% | 7 | 140 |
| `sina[25]` | `tencent[23]` | 100.00% | 7 | 140 |
| `sina[27]` | `tencent[25]` | 100.00% | 7 | 140 |
| `sina[29]` | `tencent[27]` | 100.00% | 7 | 140 |
| `tdx.finance_info.jinglirun` | `ulist239.f45` | 100.00% | 4 | 80 |
| `tdx.quote_full.turnover_pct` | `push2.f168` | 100.00% | 1 | 10 |
| `tdx.quote_full.turnover_pct` | `tencent[38]` | 100.00% | 1 | 20 |
| `tdx.quote_full.turnover_pct` | `ulist239.f8` | 100.00% | 1 | 20 |
| `tdx.quote_full.amplitude_pct` | `push2.f171` | 100.00% | 1 | 10 |
| `tdx.quote_full.amplitude_pct` | `tencent[43]` | 100.00% | 1 | 20 |
| `tdx.quote_full.amplitude_pct` | `ulist239.f7` | 100.00% | 1 | 20 |
| `tdx.quote_full.float_mcap_yi` | `tencent[44]` | 100.00% | 1 | 20 |
| `tdx.quote_full.mcap_yi` | `tencent[45]` | 100.00% | 1 | 20 |
| `tdx.quote_full.pb` | `tencent[46]` | 100.00% | 1 | 20 |
| `tdx.quote_full.limit_up` | `push2.f51` | 100.00% | 1 | 10 |
| `tdx.quote_full.limit_up` | `tencent[47]` | 100.00% | 1 | 20 |
| `tdx.quote_full.limit_down_price` | `push2.f52` | 100.00% | 1 | 10 |
| `tdx.quote_full.limit_down_price` | `tencent[48]` | 100.00% | 1 | 20 |
| `tdx.quote_full.vol_ratio` | `push2.f50` | 100.00% | 1 | 10 |
| `tdx.quote_full.vol_ratio` | `tencent[49]` | 100.00% | 1 | 20 |
| `tdx.quote_full.vol_ratio` | `ulist239.f10` | 100.00% | 1 | 20 |
| `tdx.quote_full.pe_lyr` | `push2.f163` | 100.00% | 1 | 10 |
| `tdx.quote_full.pe_lyr` | `tencent[53]` | 100.00% | 1 | 20 |
| `tdx.quote_full.pe_lyr` | `ulist239.f114` | 100.00% | 1 | 20 |
| `tencent[11]` | `ulist239.f142` | 100.00% | 4 | 80 |
| `ulist239.f144` | `eltdx.quote_snapshot.last_price` | 100.00% | 4 | 72 |
| `ulist239.f144` | `fuyao.snapshot.last_price` | 100.00% | 4 | 80 |

_（仅显示前 60 / 共 168）_

## 四、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 五、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `fuyao.valuation.pe_ttm` | `eltdx.shortline.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 90 | T:20260924, T:20260928, T:20260930, T:20261008, T:20261009 | eltdx, fuyao | Pearson=0.9995, Spearman=0.9975, LOO稳号=True |
| `fuyao.valuation.pe_ttm` | `zhb.stat.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 75 | T:20260924, T:20260929, T:20260930, T:20261009 | fuyao, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `fuyao.valuation.pe_ttm` | `zhb.full.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 75 | T:20260924, T:20260929, T:20260930, T:20261009 | fuyao, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `fuyao.auction_final.auction_volume_ratio` | `eltdx.shortline.auction_prev_volume_ratio` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 54 | T:20260924, T:20260928, T:20260930 | eltdx, fuyao | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8221, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8254, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8312, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8175, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8175, LOO稳号=True |
| `tencent[27]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8254, LOO稳号=True |
| `tencent[27]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8312, LOO稳号=True |
| `tencent[27]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8221, LOO稳号=True |
| `tencent[27]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8221, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8253, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8311, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8175, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[25]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[25]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8175, LOO稳号=True |
| `tencent[25]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8253, LOO稳号=True |
| `tencent[25]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8311, LOO稳号=True |
| `tencent[25]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8221, LOO稳号=True |
| `tencent[25]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[23]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8221, LOO稳号=True |
| `tencent[23]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8253, LOO稳号=True |
| `tencent[23]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8311, LOO稳号=True |
| `tencent[23]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8175, LOO稳号=True |
| `tencent[23]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[23]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[23]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8175, LOO稳号=True |
| `tencent[23]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8253, LOO稳号=True |
| `tencent[23]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8311, LOO稳号=True |
| `tencent[23]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8221, LOO稳号=True |
| `tencent[23]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[22]` | `sina[22]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[21]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8221, LOO稳号=True |
| `tencent[21]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8253, LOO稳号=True |
| `tencent[21]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8311, LOO稳号=True |
| `tencent[21]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8176, LOO稳号=True |
| `tencent[21]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[21]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[21]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8176, LOO稳号=True |
| `tencent[21]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8253, LOO稳号=True |
| `tencent[21]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8311, LOO稳号=True |
| `tencent[21]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8221, LOO稳号=True |
| `tencent[21]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[20]` | `sina[20]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=0.9997, LOO稳号=True |
| `tencent[17]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=0.9957, LOO稳号=True |
| `tencent[17]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=0.9888, LOO稳号=True |
| `tencent[17]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=0.9917, LOO稳号=True |
| `tencent[17]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[17]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8171, LOO稳号=True |
| `tencent[17]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8171, LOO稳号=True |
| `tencent[17]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[17]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=0.9888, LOO稳号=True |
| `tencent[17]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=0.9917, LOO稳号=True |
| `tencent[17]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=0.9957, LOO稳号=True |
| `tencent[17]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8171, LOO稳号=True |
| `tencent[15]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=0.9959, LOO稳号=True |
| `tencent[15]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=0.9887, LOO稳号=True |
| `tencent[15]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=0.9918, LOO稳号=True |
| `tencent[15]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[15]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8172, LOO稳号=True |
| `tencent[15]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8172, LOO稳号=True |
| `tencent[15]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[15]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=0.9887, LOO稳号=True |
| `tencent[15]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=0.9918, LOO稳号=True |
| `tencent[15]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=0.9959, LOO稳号=True |
| `tencent[15]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8172, LOO稳号=True |
| `tencent[13]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=0.9959, LOO稳号=True |
| `tencent[13]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=0.9888, LOO稳号=True |
| `tencent[13]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=0.9918, LOO稳号=True |
| `tencent[13]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[13]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8171, LOO稳号=True |
| `tencent[13]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8171, LOO稳号=True |
| `tencent[13]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[13]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=0.9888, LOO稳号=True |
| `tencent[13]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=0.9918, LOO稳号=True |
| `tencent[13]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=0.9959, LOO稳号=True |
| `tencent[13]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8171, LOO稳号=True |
| `tencent[12]` | `sina[12]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[11]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=0.9959, LOO稳号=True |
| `tencent[11]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=0.9887, LOO稳号=True |
| `tencent[11]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=0.9918, LOO稳号=True |
| `tencent[11]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[11]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | tdx, tencent | Pearson=0.9998, Spearman=0.8176, LOO稳号=True |
| `tencent[11]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8176, LOO稳号=True |
| `tencent[11]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[11]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=0.9887, LOO稳号=True |
| `tencent[11]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=0.9918, LOO稳号=True |
| `tencent[11]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=0.9959, LOO稳号=True |
| `tencent[11]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=0.9998, Spearman=0.8176, LOO稳号=True |
| `tencent[10]` | `sina[10]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tdx.s_vol` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tdx | Pearson=0.9938, Spearman=0.9902, LOO稳号=True |
| `tdx.quote_full.s_vol` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tdx | Pearson=0.9938, Spearman=0.9902, LOO稳号=True |
| `tdx.quote_full.b_vol` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tdx | Pearson=0.9951, Spearman=0.9687, LOO稳号=True |
| `tdx.b_vol` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260924, T:20260928, T:20260929, T:20260930, T:20261008, T:20261009 | sina, tdx | Pearson=0.9951, Spearman=0.9687, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 六、日期与数据质量告警（128）

- 20260920: 旧式非交易日目录按前一交易日 20260918 归并；目录未改名
- 20261005: 旧式非交易日目录按前一交易日 20260930 归并；目录未改名
- 20261011: 旧式非交易日目录按前一交易日 20261009 归并；目录未改名
- 20260814: 行情数据日 20260814 属于配置的异常日，行情快照排除
- 20260924/eltdx: 采集状态 partial
- 20260924/st_list: 采集状态 partial
- 20260924/eltdx: 来源状态为 partial，样本按部分快照参与
- 20260924/st_list: 来源状态为 partial，样本按部分快照参与
- 20260924/st_list: 没有可用记录，快照跳过
- 20260924/tdx_f10: 没有可用记录，快照跳过
- 20260924/tdx_f10_more: 没有可用记录，快照跳过
- 20260928/eltdx: 采集状态 partial
- 20260928/push2: 采集状态 partial
- 20260928/em_kline_f61: 采集状态 partial
- 20260928/em_fund_flow: 采集状态 partial
- 20260928/clist: 采集状态 partial
- 20260928/etf: 采集状态 partial
- 20260928/st_list: 采集状态 partial
- 20260928/clist: 来源状态为 partial，样本按部分快照参与
- 20260928/clist: 没有可用记录，快照跳过
- 20260928/eltdx: 来源状态为 partial，样本按部分快照参与
- 20260928/em_fund_flow: 来源状态为 partial，样本按部分快照参与
- 20260928/em_hot: 没有可用记录，快照跳过
- 20260928/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20260928/etf: 来源状态为 partial，样本按部分快照参与
- 20260928/push2: 来源状态为 partial，样本按部分快照参与
- 20260928/st_list: 来源状态为 partial，样本按部分快照参与
- 20260928/st_list: 没有可用记录，快照跳过
- 20260928/tdx_f10_more: 没有可用记录，快照跳过
- 20260929/eltdx: 采集状态 partial
- 20260929/push2: 采集状态 failed
- 20260929/em_kline_f61: 采集状态 failed
- 20260929/em_fund_flow: 采集状态 failed
- 20260929/ulist239: 采集状态 failed
- 20260929/clist: 采集状态 partial
- 20260929/slist: 采集状态 failed
- 20260929/st_list: 采集状态 partial
- 20260929/clist: 来源状态为 partial，样本按部分快照参与
- 20260929/clist: 没有可用记录，快照跳过
- 20260929/eltdx: 来源状态为 partial，样本按部分快照参与
- 20260929/em_fund_flow: 来源状态为 failed，快照跳过
- 20260929/em_hot: 没有可用记录，快照跳过
- 20260929/em_kline_f61: 来源状态为 failed，快照跳过
- 20260929/push2: 来源状态为 failed，快照跳过
- 20260929/push2ex: 没有可用记录，快照跳过
- 20260929/slist: 来源状态为 failed，快照跳过
- 20260929/st_list: 来源状态为 partial，样本按部分快照参与
- 20260929/st_list: 没有可用记录，快照跳过
- 20260929/tdx_f10: 没有可用记录，快照跳过
- 20260929/tdx_f10_more: 没有可用记录，快照跳过
- 20260929/ulist239: 来源状态为 failed，快照跳过
- 20260930/push2: 采集状态 failed
- 20260930/axdata: 采集状态 failed
- 20260930/em_kline_f61: 采集状态 partial
- 20260930/em_fund_flow: 采集状态 failed
- 20260930/axdata: 来源状态为 failed，快照跳过
- 20260930/em_fund_flow: 来源状态为 failed，快照跳过
- 20260930/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20260930/push2: 来源状态为 failed，快照跳过
- 20260930/tdx_f10: 没有可用记录，快照跳过
- 20260930/tdx_f10_more: 没有可用记录，快照跳过
- 20261008/push2: 采集状态 partial
- 20261008/axdata: 采集状态 failed
- 20261008/em_kline_f61: 采集状态 partial
- 20261008/em_fund_flow: 采集状态 partial
- 20261008/axdata: 来源状态为 failed，快照跳过
- 20261008/em_fund_flow: 来源状态为 partial，样本按部分快照参与
- 20261008/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20261008/push2: 来源状态为 partial，样本按部分快照参与
- 20261008/tdx_f10: 没有可用记录，快照跳过
- 20261008/tdx_f10_more: 没有可用记录，快照跳过
- 20261009/tdx_f10: 没有可用记录，快照跳过
- 20261009/tdx_f10_more: 没有可用记录，快照跳过
- 20261012/sse_e_interaction: 采集状态 partial
- 20261012/st_list: 采集状态 partial
- 20261012/em_fund_flow: 采集状态 partial
- 20261012/em_kline_f61: 采集状态 partial
- 20261012/push2: 采集状态 partial
- 20261012/ulist239: 采集状态 failed
- 20261012/em_fund_flow: 来源状态为 partial，样本按部分快照参与
- 20261012/em_fund_flow: 没有可用记录，快照跳过
- 20261012/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20261012/em_kline_f61: 没有可用记录，快照跳过
- 20261012/push2: 来源状态为 partial，样本按部分快照参与
- 20261012/sse_e_interaction: 来源状态为 partial，样本按部分快照参与
- 20261012/st_list: 来源状态为 partial，样本按部分快照参与
- 20261012/st_list: 没有可用记录，快照跳过
- 20261012/tdx_f10: 没有可用记录，快照跳过
- 20261012/tdx_f10_more: 没有可用记录，快照跳过
- 20261012/ulist239: 来源状态为 failed，快照跳过
- 重复快照 zhb/20260930: 选择 20261008，忽略 20260930
- 重复快照 kph/20261009: 选择 20261012，忽略 20261009
- 重复快照 zhb/20261009: 选择 20261012，忽略 20261009
- 20260924/em_hot: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260930/em_hot: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260924/exchange: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260928/exchange: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260929/exchange: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260930/exchange: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260924/fuyao/market.dragon_tiger: 默认碰撞已排除上下文记录（0 条）
- 另有 28 条告警，详见同名 JSON 报告。

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

## 探索候选持续跟踪

研究台账：`collision_research_state.json`；累计候选对 1216，本报告候选对 663，历史复现 317，新发现 346。
台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，不会自动改变字段状态、碰撞锚或主字典。
