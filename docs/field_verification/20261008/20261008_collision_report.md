# 全源对撞报告（20261008）

> 行情窗口：20260922 ~ 20261008（7 个不同交易日）｜字段 1117 个｜样本值 457035 条
> 新闻/公告自然日窗口：20261002 ~ 20261008
> 主攻目标（unverified）=335｜新增 L1/L1-U 定案=19｜异号同义 21 / 同号镜像 0

> **规则**：每个定案日有效样本≥18，命中率≥90%，至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 定案候选 — 异号同义（跨编号，高价值）(21)

| 左字段(unverified) | 右字段 | 等级 | 命中率 | 天数 | 样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|:--|:--|
| `tencent[10]` | `ulist239.f211` | L1 | 99.00% | 5 | 100 | - |  | ✅ |
| `tdx.finance_info.liutongguben` | `tencent[72]` | L1-U | 100.00% | 6 | 120 | 10000 |  | — |
| `tdx.finance_info.liutongguben` | `tencent[76]` | L1-U | 100.00% | 6 | 120 | 10000 |  | — |
| `tdx.finance_info.liutongguben` | `ulist239.f39` | L1-U | 100.00% | 5 | 100 | 10000 |  | — |
| `tdx.finance_info.zongzichan` | `ulist239.f50` | L1-U | 100.00% | 5 | 100 | 0.1 |  | — |
| `tdx.finance_info.liudongzichan` | `ulist239.f51` | L1-U | 100.00% | 5 | 95 | 0.1 |  | — |
| `tdx.finance_info.gudingzichan` | `ulist239.f52` | L1-U | 100.00% | 5 | 100 | 0.1 |  | — |
| `tdx.finance_info.liudongfuzhai` | `ulist239.f55` | L1-U | 100.00% | 5 | 95 | 0.1 |  | — |
| `tdx.finance_info.zibengongjijin` | `ulist239.f60` | L1-U | 100.00% | 5 | 100 | 0.1 |  | — |
| `tdx.finance_info.yingyelirun` | `ulist239.f42` | L1-U | 100.00% | 5 | 100 | 0.1 |  | — |
| `tdx.finance_info.lirunzonghe` | `ulist239.f44` | L1-U | 100.00% | 5 | 100 | 0.1 |  | — |
| `tdx.finance_info.weifenlirun` | `ulist239.f47` | L1-U | 100.00% | 5 | 100 | 0.1 |  | — |
| `zhb.full.change_pct` | `tencent[32]` | L1 | 100.00% | 3 | 60 | - |  | — |
| `zhb.full.change_20d` | `tencent[70]` | L1 | 100.00% | 3 | 60 | - |  | — |
| `zhb.full.change_30d` | `tencent[70]` | L1 | 100.00% | 3 | 60 | - |  | — |
| `zhb.full.change_5d` | `tencent[63]` | L1 | 100.00% | 3 | 60 | - |  | — |
| `zhb.full.change_10d` | `tencent[69]` | L1 | 100.00% | 3 | 60 | - |  | — |
| `zhb.full.low_52w` | `tencent[68]` | L1 | 100.00% | 3 | 60 | - |  | — |
| `zhb.full.pe_ttm` | `tencent[39]` | L1 | 98.33% | 3 | 60 | - |  | — |
| `zhb.full.high_52w` | `tencent[67]` | L1 | 95.00% | 3 | 60 | - |  | — |
| `zhb.full.amount` | `tencent[57]` | L1 | 90.00% | 3 | 60 | - |  | — |

## 二、L1 / L1-U 定案候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、L4 存疑候选（167）

| 左字段 | 右字段 | 命中率 | 天数 | 样本 |
|:--|:--|--:|--:|--:|
| `fuyao.auction_final.auction_price` | `eltdx.shortline.open_price` | 100.00% | 4 | 72 |
| `fuyao.auction_final.auction_price` | `push2.f46` | 100.00% | 2 | 29 |
| `fuyao.auction_final.auction_price` | `sina[1]` | 100.00% | 5 | 97 |
| `fuyao.auction_final.auction_price` | `tdx.quote_full.open` | 100.00% | 5 | 97 |
| `fuyao.auction_final.auction_price` | `tencent[5]` | 100.00% | 5 | 97 |
| `fuyao.auction_final.auction_price` | `ulist239.f17` | 100.00% | 4 | 78 |
| `fuyao.auction_final.pre_close_price` | `eltdx.quote_snapshot.pre_close_price` | 100.00% | 5 | 90 |
| `fuyao.auction_final.pre_close_price` | `eltdx.shortline.pre_close` | 100.00% | 4 | 72 |
| `fuyao.auction_final.pre_close_price` | `push2.f60` | 100.00% | 2 | 30 |
| `fuyao.auction_final.pre_close_price` | `ulist239.f18` | 100.00% | 4 | 80 |
| `fuyao.auction_final.open_price` | `eltdx.quote_snapshot.open_price` | 100.00% | 4 | 72 |
| `fuyao.auction_final.open_price` | `eltdx.shortline.open_price` | 100.00% | 4 | 72 |
| `fuyao.auction_final.open_price` | `push2.f46` | 100.00% | 2 | 30 |
| `fuyao.auction_final.open_price` | `sina[1]` | 100.00% | 4 | 80 |
| `fuyao.auction_final.open_price` | `tdx.quote_full.open` | 100.00% | 4 | 80 |
| `fuyao.auction_final.open_price` | `tencent[5]` | 100.00% | 4 | 80 |
| `fuyao.auction_final.open_price` | `ulist239.f17` | 100.00% | 4 | 80 |
| `fuyao.auction_final.last_price` | `eltdx.quote_snapshot.last_price` | 100.00% | 4 | 72 |
| `fuyao.auction_final.last_price` | `push2.f43` | 100.00% | 2 | 30 |
| `fuyao.auction_final.last_price` | `push2.f179` | 100.00% | 2 | 30 |
| `fuyao.auction_final.last_price` | `sina[3]` | 100.00% | 4 | 80 |
| `fuyao.auction_final.last_price` | `tdx.quote_full.price` | 100.00% | 4 | 80 |
| `fuyao.auction_final.last_price` | `tencent[3]` | 100.00% | 4 | 80 |
| `fuyao.auction_final.last_price` | `ulist239.f2` | 100.00% | 4 | 80 |
| `fuyao.auction_final.last_price` | `ulist239.f144` | 100.00% | 4 | 80 |
| `sina[11]` | `tdx.quote_full.bid1` | 100.00% | 6 | 120 |
| `sina[11]` | `tencent[9]` | 100.00% | 6 | 120 |
| `sina[13]` | `tencent[11]` | 100.00% | 6 | 120 |
| `sina[15]` | `tencent[13]` | 100.00% | 6 | 120 |
| `sina[17]` | `tencent[15]` | 100.00% | 6 | 120 |
| `sina[19]` | `tencent[17]` | 100.00% | 6 | 120 |
| `sina[23]` | `tencent[21]` | 100.00% | 6 | 120 |
| `sina[25]` | `tencent[23]` | 100.00% | 6 | 120 |
| `sina[27]` | `tencent[25]` | 100.00% | 6 | 120 |
| `sina[29]` | `tencent[27]` | 100.00% | 6 | 120 |
| `tdx.finance_info.jinglirun` | `ulist239.f45` | 100.00% | 5 | 100 |
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
| `ulist239.f144` | `eltdx.quote_snapshot.last_price` | 100.00% | 5 | 90 |
| `ulist239.f144` | `fuyao.snapshot.last_price` | 100.00% | 5 | 100 |
| `ulist239.f144` | `sina[3]` | 100.00% | 5 | 100 |
| `ulist239.f144` | `tdx.quote_full.price` | 100.00% | 5 | 100 |
| `ulist239.f144` | `tencent[3]` | 100.00% | 5 | 100 |

_（仅显示前 60 / 共 167）_

## 四、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 五、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `fuyao.valuation.pe_ttm` | `eltdx.shortline.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 90 | T:20260923, T:20260924, T:20260928, T:20260930, T:20261008 | eltdx, fuyao | Pearson=0.9995, Spearman=0.9961, LOO稳号=True |
| `fuyao.valuation.pe_ttm` | `zhb.stat.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 75 | T:20260923, T:20260924, T:20260929, T:20260930 | fuyao, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `fuyao.valuation.pe_ttm` | `zhb.full.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 75 | T:20260923, T:20260924, T:20260929, T:20260930 | fuyao, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `fuyao.auction_final.auction_volume_ratio` | `eltdx.shortline.auction_prev_volume_ratio` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 72 | T:20260923, T:20260924, T:20260928, T:20260930 | eltdx, fuyao | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8391, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.844, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8467, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8375, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8375, LOO稳号=True |
| `tencent[27]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.844, LOO稳号=True |
| `tencent[27]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8467, LOO稳号=True |
| `tencent[27]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8391, LOO稳号=True |
| `tencent[27]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8391, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8439, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8466, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8376, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[25]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[25]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8376, LOO稳号=True |
| `tencent[25]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8439, LOO稳号=True |
| `tencent[25]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8466, LOO稳号=True |
| `tencent[25]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8391, LOO稳号=True |
| `tencent[25]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[23]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8391, LOO稳号=True |
| `tencent[23]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8439, LOO稳号=True |
| `tencent[23]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8466, LOO稳号=True |
| `tencent[23]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8375, LOO稳号=True |
| `tencent[23]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[23]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[23]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8375, LOO稳号=True |
| `tencent[23]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8439, LOO稳号=True |
| `tencent[23]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8466, LOO稳号=True |
| `tencent[23]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8391, LOO稳号=True |
| `tencent[23]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[22]` | `sina[22]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[21]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8391, LOO稳号=True |
| `tencent[21]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8439, LOO稳号=True |
| `tencent[21]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8466, LOO稳号=True |
| `tencent[21]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8376, LOO稳号=True |
| `tencent[21]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[21]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[21]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8376, LOO稳号=True |
| `tencent[21]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8439, LOO稳号=True |
| `tencent[21]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8466, LOO稳号=True |
| `tencent[21]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8391, LOO稳号=True |
| `tencent[21]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[20]` | `sina[20]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=0.9997, LOO稳号=True |
| `tencent[17]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=0.9987, LOO稳号=True |
| `tencent[17]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=0.9955, LOO稳号=True |
| `tencent[17]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=0.9961, LOO稳号=True |
| `tencent[17]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[17]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.837, LOO稳号=True |
| `tencent[17]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.837, LOO稳号=True |
| `tencent[17]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[17]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=0.9955, LOO稳号=True |
| `tencent[17]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=0.9961, LOO稳号=True |
| `tencent[17]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=0.9987, LOO稳号=True |
| `tencent[17]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.837, LOO稳号=True |
| `tencent[17]` | `fuyao.snapshot.prev_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | fuyao, tencent | Pearson=0.9999, Spearman=0.9926, LOO稳号=True |
| `tencent[15]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=0.9989, LOO稳号=True |
| `tencent[15]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=0.9954, LOO稳号=True |
| `tencent[15]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=0.996, LOO稳号=True |
| `tencent[15]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[15]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8371, LOO稳号=True |
| `tencent[15]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8371, LOO稳号=True |
| `tencent[15]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[15]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=0.9954, LOO稳号=True |
| `tencent[15]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=0.996, LOO稳号=True |
| `tencent[15]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=0.9989, LOO稳号=True |
| `tencent[15]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8371, LOO稳号=True |
| `tencent[15]` | `fuyao.snapshot.prev_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | fuyao, tencent | Pearson=0.9999, Spearman=0.9926, LOO稳号=True |
| `tencent[13]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=0.9989, LOO稳号=True |
| `tencent[13]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=0.9954, LOO稳号=True |
| `tencent[13]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=0.9961, LOO稳号=True |
| `tencent[13]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[13]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.837, LOO稳号=True |
| `tencent[13]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.837, LOO稳号=True |
| `tencent[13]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[13]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=0.9954, LOO稳号=True |
| `tencent[13]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=0.9961, LOO稳号=True |
| `tencent[13]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=0.9989, LOO稳号=True |
| `tencent[13]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.837, LOO稳号=True |
| `tencent[12]` | `sina[12]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[11]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=0.999, LOO稳号=True |
| `tencent[11]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=0.9954, LOO稳号=True |
| `tencent[11]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=0.9961, LOO稳号=True |
| `tencent[11]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[11]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | tdx, tencent | Pearson=0.9998, Spearman=0.8376, LOO稳号=True |
| `tencent[11]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8376, LOO稳号=True |
| `tencent[11]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[11]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=0.9954, LOO稳号=True |
| `tencent[11]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=0.9961, LOO稳号=True |
| `tencent[11]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=0.999, LOO稳号=True |
| `tencent[11]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=0.9998, Spearman=0.8376, LOO稳号=True |
| `tencent[10]` | `sina[10]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tdx.s_vol` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tdx | Pearson=0.9958, Spearman=0.9919, LOO稳号=True |
| `tdx.quote_full.s_vol` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20260923, T:20260924, T:20260928, T:20260929, T:20260930, T:20261008 | sina, tdx | Pearson=0.9958, Spearman=0.9919, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 六、日期与数据质量告警（123）

- 20260920: 旧式非交易日目录按前一交易日 20260918 归并；目录未改名
- 20261005: 旧式非交易日目录按前一交易日 20260930 归并；目录未改名
- 20260814: 行情数据日 20260814 属于配置的异常日，行情快照排除
- 20260922/st_list: 没有可用记录，快照跳过
- 20260923/eltdx: 采集状态 partial
- 20260923/push2: 采集状态 partial
- 20260923/em_kline_f61: 采集状态 partial
- 20260923/em_fund_flow: 采集状态 failed
- 20260923/clist: 采集状态 partial
- 20260923/st_list: 采集状态 partial
- 20260923/clist: 来源状态为 partial，样本按部分快照参与
- 20260923/clist: 没有可用记录，快照跳过
- 20260923/eltdx: 来源状态为 partial，样本按部分快照参与
- 20260923/em_fund_flow: 来源状态为 failed，快照跳过
- 20260923/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20260923/push2: 来源状态为 partial，样本按部分快照参与
- 20260923/st_list: 来源状态为 partial，样本按部分快照参与
- 20260923/st_list: 没有可用记录，快照跳过
- 20260923/tdx_f10: 没有可用记录，快照跳过
- 20260923/tdx_f10_more: 没有可用记录，快照跳过
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
- 重复快照 zhb/20260930: 选择 20261008，忽略 20260930
- 20260923/em_hot: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260924/em_hot: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260930/em_hot: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260923/exchange: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260924/exchange: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260928/exchange: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260929/exchange: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260930/exchange: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260923/fuyao/market.dragon_tiger: 默认碰撞已排除上下文记录（0 条）
- 20260923/fuyao/market.hot_list_hour: 默认碰撞已排除上下文记录（30 条）
- 20260924/fuyao/market.dragon_tiger: 默认碰撞已排除上下文记录（0 条）
- 20260924/fuyao/market.hot_list_hour: 默认碰撞已排除上下文记录（30 条）
- 另有 23 条告警，详见同名 JSON 报告。

---

> 数据来源：通达信 / 项目字段对撞体系。以上为方法论梳理，不构成投资建议。
