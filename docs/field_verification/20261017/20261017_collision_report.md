# 全源对撞报告（20261017）

> 交易数据窗口配置：近 7 个交易日（`--window`）
> 行情窗口：20261008 ~ 20261016（7 个不同交易日）｜字段 1174 个｜样本值 354832 条
> 新闻/公告自然日窗口：20261011 ~ 20261017
> 主攻目标（unverified）=324｜首次发现 L1/L1-U 候选对=0｜异号同义 4 / 同号镜像 0

> **规则**：L1 每日需≥18 组有效配对，并至少有5 组信息配对；双方同时为 0 或同时缺失不计命中率，一侧为 0、另一侧非 0 按失配计。信息配对命中率≥90%，且覆盖至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。JSON `daily_sample_counts` 与 `daily_informative_sample_counts`分别保留每日有效配对数和 L1 信息配对数。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 定案候选 — 异号同义（跨编号，高价值）(4)

| 左字段(unverified) | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|
| `zhb.full.change_pct` | `tencent[32]` | L1 | 97.98% | 5 | 100 | 99 | - |  | ✅ |
| `zhb.full.high_52w` | `tencent[67]` | L1 | 95.00% | 5 | 100 | 100 | - |  | ✅ |
| `zhb.full.pe_ttm` | `tencent[39]` | L1 | 97.00% | 5 | 100 | 100 | - |  | — |
| `zhb.full.change_60d` | `tencent[71]` | L1 | 90.00% | 5 | 100 | 100 | - |  | — |

## 二、L1 / L1-U 定案候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、L4 存疑候选（61）

| 左字段 | 右字段 | 命中率 | 天数 | 样本 |
|:--|:--|--:|--:|--:|
| `push2ex.limit_fund` | `kpl.seal_amount` | 100.00% | 2 | 75 |
| `sina[11]` | `tdx.quote_full.bid1` | 100.00% | 4 | 80 |
| `sina[11]` | `tencent[9]` | 100.00% | 7 | 140 |
| `sina[11]` | `ulist239.f31` | 100.00% | 1 | 20 |
| `tencent[10]` | `ulist239.f211` | 100.00% | 1 | 20 |
| `ulist239.f144` | `eltdx.quote_snapshot.last_price` | 100.00% | 1 | 18 |
| `ulist239.f144` | `fuyao.snapshot.last_price` | 100.00% | 1 | 20 |
| `ulist239.f144` | `sina[3]` | 100.00% | 1 | 20 |
| `ulist239.f144` | `tdx.quote_full.price` | 100.00% | 1 | 20 |
| `ulist239.f144` | `tencent[3]` | 100.00% | 1 | 20 |
| `zhb.full.change_pct` | `push2.f170` | 100.00% | 1 | 12 |
| `zhb.full.change_60d` | `push2.f121` | 100.00% | 1 | 12 |
| `sina[32]` | `ulist239.f190` | 95.00% | 1 | 20 |
| `sina[32]` | `ulist239.f231` | 95.00% | 1 | 20 |
| `sina[32]` | `tdx.finance_info.hgu` | 93.00% | 5 | 100 |
| `zhb.full.pe_ttm` | `push2.f164` | 91.67% | 1 | 12 |
| `zhb.full.change_ytd` | `push2.f122` | 91.67% | 1 | 12 |
| `sina[32]` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 91.38% | 6 | 116 |
| `sina[32]` | `ulist239.f200` | 90.00% | 1 | 20 |
| `tencent[20]` | `ulist239.f212` | 90.00% | 1 | 20 |
| `sina[32]` | `tdx.finance_info.bgu` | 88.00% | 5 | 100 |
| `sina[32]` | `zhb.stat.other_qy_jzc` | 88.00% | 5 | 100 |
| `push2.f192` | `tencent[50]` | 87.50% | 2 | 24 |
| `fuyao.valuation.ps_ttm` | `ulist239.f130` | 85.00% | 1 | 20 |
| `push2.f174` | `tencent[67]` | 83.33% | 2 | 24 |
| `push2.f174` | `zhb.stat2.high_52w` | 83.33% | 1 | 12 |
| `push2.f126` | `zhb.stat.dividend_yield` | 75.00% | 1 | 12 |
| `tencent[8]` | `ulist239.f35` | 75.00% | 1 | 20 |
| `ulist239.f11` | `tencent[80]` | 75.00% | 1 | 20 |
| `zhb.full.dividend_yield` | `tencent[64]` | 75.00% | 5 | 100 |
| `zhb.full.change_ytd` | `tencent[62]` | 74.00% | 5 | 100 |
| `sina[11]` | `ulist239.f2` | 70.00% | 1 | 20 |
| `tencent[7]` | `ulist239.f34` | 70.00% | 1 | 20 |
| `ulist239.f144` | `sina[6]` | 70.00% | 1 | 20 |
| `ulist239.f144` | `tdx.quote_full.bid1` | 70.00% | 1 | 20 |
| `ulist239.f144` | `tencent[9]` | 70.00% | 1 | 20 |
| `zhb.full.change_250k_bar` | `tencent[79]` | 69.00% | 5 | 100 |
| `ulist239.f97` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 66.67% | 1 | 18 |
| `ulist239.f97` | `tdx.finance_info.bgu` | 65.00% | 1 | 20 |
| `ulist239.f97` | `tdx.finance_info.hgu` | 65.00% | 1 | 20 |
| `push2.f191` | `tencent[74]` | 62.50% | 2 | 24 |
| `ulist239.f13` | `tdx.finance_info.hgu` | 60.00% | 1 | 20 |
| `ulist239.f27` | `tdx.finance_info.hgu` | 60.00% | 1 | 20 |
| `push2.f126` | `tencent[64]` | 58.33% | 2 | 24 |
| `ulist239.f13` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 55.56% | 1 | 18 |
| `ulist239.f27` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 55.56% | 1 | 18 |
| `ulist239.f133` | `tencent[64]` | 55.00% | 1 | 20 |
| `sina[11]` | `tdx.quote_full.price` | 53.75% | 4 | 80 |
| `sina[11]` | `push2.f43` | 50.00% | 2 | 24 |
| `sina[11]` | `push2.f179` | 50.00% | 2 | 24 |
| `sina[32]` | `push2.f107` | 50.00% | 2 | 24 |
| `sina[32]` | `push2.f110` | 50.00% | 2 | 24 |
| `ulist239.f13` | `tdx.finance_info.bgu` | 50.00% | 1 | 20 |
| `ulist239.f27` | `tdx.finance_info.bgu` | 50.00% | 1 | 20 |
| `zhb.full.other_qy_jzc` | `push2.f107` | 50.00% | 1 | 12 |
| `zhb.full.other_qy_jzc` | `push2.f110` | 50.00% | 1 | 12 |
| `sina[11]` | `tencent[3]` | 47.86% | 7 | 140 |
| `sina[11]` | `fuyao.snapshot.last_price` | 47.50% | 4 | 80 |
| `sina[11]` | `eltdx.quote_snapshot.last_price` | 47.41% | 6 | 116 |
| `ulist239.f13` | `tencent[0]` | 40.00% | 1 | 20 |

_（仅显示前 60 / 共 61）_

## 四、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 五、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `fuyao.valuation.pe_ttm` | `eltdx.shortline.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 74 | T:20261008, T:20261009, T:20261014, T:20261016 | eltdx, fuyao | Pearson=0.9997, Spearman=0.999, LOO稳号=True |
| `fuyao.valuation.pe_ttm` | `zhb.stat.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 60 | T:20261009, T:20261014, T:20261016 | fuyao, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9952, LOO稳号=True |
| `tencent[27]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9235, LOO稳号=True |
| `tencent[27]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9296, LOO稳号=True |
| `tencent[27]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.935, LOO稳号=True |
| `tencent[27]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9028, LOO稳号=True |
| `tencent[27]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9191, LOO稳号=True |
| `tencent[27]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9952, LOO稳号=True |
| `tencent[27]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9303, LOO稳号=True |
| `tencent[25]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `tencent[25]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9235, LOO稳号=True |
| `tencent[25]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9296, LOO稳号=True |
| `tencent[25]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9351, LOO稳号=True |
| `tencent[25]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9028, LOO稳号=True |
| `tencent[25]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9191, LOO稳号=True |
| `tencent[25]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `tencent[25]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9303, LOO稳号=True |
| `tencent[23]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `tencent[23]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9235, LOO稳号=True |
| `tencent[23]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9296, LOO稳号=True |
| `tencent[23]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9351, LOO稳号=True |
| `tencent[23]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9028, LOO稳号=True |
| `tencent[23]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9191, LOO稳号=True |
| `tencent[23]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `tencent[23]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9303, LOO稳号=True |
| `tencent[22]` | `sina[22]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[21]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `tencent[21]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9235, LOO稳号=True |
| `tencent[21]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9296, LOO稳号=True |
| `tencent[21]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9351, LOO稳号=True |
| `tencent[21]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9028, LOO稳号=True |
| `tencent[21]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9191, LOO稳号=True |
| `tencent[21]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `tencent[21]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9302, LOO稳号=True |
| `tencent[20]` | `sina[20]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9998, LOO稳号=True |
| `tencent[17]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9271, LOO稳号=True |
| `tencent[17]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[17]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9911, LOO稳号=True |
| `tencent[17]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9929, LOO稳号=True |
| `tencent[17]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9686, LOO稳号=True |
| `tencent[17]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.96, LOO稳号=True |
| `tencent[17]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9271, LOO稳号=True |
| `tencent[17]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9914, LOO稳号=True |
| `tencent[15]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9271, LOO稳号=True |
| `tencent[15]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[15]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9912, LOO稳号=True |
| `tencent[15]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9929, LOO稳号=True |
| `tencent[15]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9686, LOO稳号=True |
| `tencent[15]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.96, LOO稳号=True |
| `tencent[15]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9271, LOO稳号=True |
| `tencent[15]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9915, LOO稳号=True |
| `tencent[13]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9271, LOO稳号=True |
| `tencent[13]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[13]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9912, LOO稳号=True |
| `tencent[13]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9929, LOO稳号=True |
| `tencent[13]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9687, LOO稳号=True |
| `tencent[13]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.96, LOO稳号=True |
| `tencent[13]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9271, LOO稳号=True |
| `tencent[13]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9915, LOO稳号=True |
| `tencent[12]` | `sina[12]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[11]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9271, LOO稳号=True |
| `tencent[11]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[11]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9912, LOO稳号=True |
| `tencent[11]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9929, LOO稳号=True |
| `tencent[11]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9687, LOO稳号=True |
| `tencent[11]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.96, LOO稳号=True |
| `tencent[11]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9271, LOO稳号=True |
| `tencent[11]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9915, LOO稳号=True |
| `tencent[10]` | `sina[10]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[29]` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9235, LOO稳号=True |
| `sina[29]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9997, Spearman=0.719, LOO稳号=True |
| `sina[29]` | `tencent[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9303, LOO稳号=True |
| `sina[29]` | `tencent[51]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9305, LOO稳号=True |
| `sina[29]` | `tencent[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9191, LOO稳号=True |
| `sina[29]` | `tencent[48]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9998, Spearman=0.8885, LOO稳号=True |
| `sina[29]` | `tencent[47]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9254, LOO稳号=True |
| `sina[29]` | `tencent[42]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9296, LOO稳号=True |
| `sina[29]` | `tencent[41]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.935, LOO稳号=True |
| `sina[29]` | `tencent[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9028, LOO稳号=True |
| `sina[29]` | `tencent[34]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9296, LOO稳号=True |
| `sina[29]` | `tencent[33]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.935, LOO稳号=True |
| `sina[29]` | `tencent[19]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9952, LOO稳号=True |
| `sina[27]` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9235, LOO稳号=True |
| `sina[27]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9997, Spearman=0.7192, LOO稳号=True |
| `sina[27]` | `tencent[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9303, LOO稳号=True |
| `sina[27]` | `tencent[51]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9305, LOO稳号=True |
| `sina[27]` | `tencent[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9191, LOO稳号=True |
| `sina[27]` | `tencent[48]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9998, Spearman=0.8884, LOO稳号=True |
| `sina[27]` | `tencent[47]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9254, LOO稳号=True |
| `sina[27]` | `tencent[42]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9296, LOO稳号=True |
| `sina[27]` | `tencent[41]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9351, LOO稳号=True |
| `sina[27]` | `tencent[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9028, LOO稳号=True |
| `sina[27]` | `tencent[34]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9296, LOO稳号=True |
| `sina[27]` | `tencent[33]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9351, LOO稳号=True |
| `sina[27]` | `tencent[19]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `sina[25]` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9235, LOO稳号=True |
| `sina[25]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9997, Spearman=0.7197, LOO稳号=True |
| `sina[25]` | `tencent[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9303, LOO稳号=True |
| `sina[25]` | `tencent[51]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261008, T:20261009, T:20261012, T:20261013, T:20261014, T:20261015 | sina, tencent | Pearson=0.9999, Spearman=0.9305, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 六、日期与数据质量告警（127）

- 20260920: 旧式非交易日目录按前一交易日 20260918 归并；目录未改名
- 20261005: 旧式非交易日目录按前一交易日 20260930 归并；目录未改名
- 20261011: 旧式非交易日目录按前一交易日 20261009 归并；目录未改名
- 20261017: 旧式非交易日目录按前一交易日 20261016 归并；目录未改名
- 20260814: 行情数据日 20260814 属于配置的异常日，行情快照排除
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
- 20261013/ftshare: 采集状态 failed
- 20261013/ftshare: 来源状态为 failed，快照跳过
- 20261014/push2: 采集状态 failed
- 20261014/em_kline_f61: 采集状态 partial
- 20261014/em_fund_flow: 采集状态 partial
- 20261014/ulist239: 采集状态 failed
- 20261014/ftshare: 采集状态 failed
- 20261014/clist: 采集状态 partial
- 20261014/slist: 采集状态 failed
- 20261014/sse_e_interaction: 采集状态 partial
- 20261014/st_list: 采集状态 partial
- 20261014/clist: 来源状态为 partial，样本按部分快照参与
- 20261014/clist: 没有可用记录，快照跳过
- 20261014/em_fund_flow: 来源状态为 partial，样本按部分快照参与
- 20261014/em_fund_flow: 没有可用记录，快照跳过
- 20261014/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20261014/em_kline_f61: 没有可用记录，快照跳过
- 20261014/ftshare: 来源状态为 failed，快照跳过
- 20261014/push2: 来源状态为 failed，快照跳过
- 20261014/slist: 来源状态为 failed，快照跳过
- 20261014/sse_e_interaction: 来源状态为 partial，样本按部分快照参与
- 20261014/st_list: 来源状态为 partial，样本按部分快照参与
- 20261014/st_list: 没有可用记录，快照跳过
- 20261014/tdx_f10: 没有可用记录，快照跳过
- 20261014/tdx_f10_more: 没有可用记录，快照跳过
- 20261014/ulist239: 来源状态为 failed，快照跳过
- 20261015/push2: 采集状态 failed
- 20261015/em_kline_f61: 采集状态 partial
- 20261015/em_fund_flow: 采集状态 partial
- 20261015/ulist239: 采集状态 failed
- 20261015/ftshare: 采集状态 failed
- 20261015/clist: 采集状态 partial
- 20261015/slist: 采集状态 failed
- 20261015/news_wscn_cctv: 采集状态 partial
- 20261015/st_list: 采集状态 partial
- 20261015/clist: 来源状态为 partial，样本按部分快照参与
- 20261015/clist: 没有可用记录，快照跳过
- 20261015/cls: 没有可用记录，快照跳过
- 20261015/cninfo: 没有可用记录，快照跳过
- 20261015/em_fund_flow: 来源状态为 partial，样本按部分快照参与
- 20261015/em_fund_flow: 没有可用记录，快照跳过
- 20261015/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20261015/em_kline_f61: 没有可用记录，快照跳过
- 20261015/event_dc: 没有可用记录，快照跳过
- 20261015/ftshare: 来源状态为 failed，快照跳过
- 20261015/kph: 没有可用记录，快照跳过
- 20261015/macro_dc: 没有可用记录，快照跳过
- 20261015/news_wscn_cctv: 来源状态为 partial，样本按部分快照参与
- 20261015/news_wscn_cctv: 没有可用记录，快照跳过
- 20261015/push2: 来源状态为 failed，快照跳过
- 20261015/push2ex: 没有可用记录，快照跳过
- 20261015/reports: 没有可用记录，快照跳过
- 20261015/research_sina: 没有可用记录，快照跳过
- 20261015/slist: 来源状态为 failed，快照跳过
- 20261015/st_list: 来源状态为 partial，样本按部分快照参与
- 20261015/st_list: 没有可用记录，快照跳过
- 20261015/tdx_f10_more: 没有可用记录，快照跳过
- 20261015/ulist239: 来源状态为 failed，快照跳过
- 20261016/ftshare: 采集状态 failed
- 20261016/sse_e_interaction: 采集状态 partial
- 20261016/ftshare: 来源状态为 failed，快照跳过
- 20261016/sse_e_interaction: 来源状态为 partial，样本按部分快照参与
- 20261016/tdx_f10_more: 没有可用记录，快照跳过
- 重复快照 kph/20261009: 选择 20261012，忽略 20261009
- 重复快照 cls/20261014: 选择 20261013，忽略 20261012
- 重复快照 cninfo/20261014: 选择 20261013，忽略 20261012
- 另有 27 条告警，详见同名 JSON 报告。

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
| 20261016 | not_eligible | not_run / 0 (字段相同/不同 0/0) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing | — | — | meta_summary |

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

窗口内观察到 119 条需审阅的字母字段路径：含词义线索 43 条，仅拆词 76 条。
完整逐条记录保存在碰撞 JSON；名称线索清单：`docs/field_verification/20261014/20261014_alphabetic_field_name_inventory.csv`。
> 拼音、英文、缩写和混合拆词只用于检索候选；必须结合原始值、接口定义和独立来源复核，不得据此定案或改写主字典。

| 逐源字段路径 | 状态/审阅范围 | 名称形式与拆词 | 词义线索（非释义） | 样本日期 |
|:--|:--|:--|:--|:--|
| `市场源(market_sources)::change_type` | unverified / unverified_semantics | snake_case_or_mixed: change type | 变化/涨跌 + 类型 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `市场源(market_sources)::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `市场源(market_sources)::limit_count` | verified / verified_metadata_gap | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `市场源(market_sources)::limit_time` | unverified / unverified_semantics | snake_case_or_mixed: limit time | 涨跌停限制 + 时间 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `市场源(market_sources)::plate_limit_up_count` | verified / verified_metadata_gap | snake_case_or_mixed: plate limit up count | 涨跌停限制 + 上/涨 + 数量/次数 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `东财-push2ex::change_pct` | unverified / unverified_semantics | recognized_english_word_candidate: change pct | 变化/涨跌 + 百分比 | T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::first_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: first limit time | 首次/第一 + 涨跌停限制 + 时间 | T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::last_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: last limit time | 最近/上一期 + 涨跌停限制 + 时间 | T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::limit_count` | unverified / unverified_semantics | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::name` | unverified / unverified_semantics | recognized_english_word_candidate: name | 名称 | T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::price` | unverified / unverified_semantics | recognized_english_word_candidate: price | 价格 | T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::total_value` | unverified / unverified_semantics | snake_case_or_mixed: total value | 总 + 值 | T:20261008, T:20261014, T:20261016 |
| `开盘红(Levistock适配)::limit_count` | unverified / unverified_semantics | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261009, T:20261013, T:20261015 |
| `开盘红(Levistock适配)::open_time` | unverified / unverified_semantics | snake_case_or_mixed: open time | 开盘 + 时间 | T:20261009, T:20261013, T:20261015 |
| `财联社(cls)::time` | unverified / unverified_semantics | recognized_english_word_candidate: time | 时间 | C:20261011, C:20261014, C:20261016 |
| `ZHB-tdxstat::change_pct` | unverified / unverified_semantics | recognized_english_word_candidate: change pct | 变化/涨跌 + 百分比 | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::change_pct_1d` | unverified / unverified_semantics | snake_case_or_mixed: change pct 1 d | 变化/涨跌 + 百分比 | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::change_pct_2d` | unverified / unverified_semantics | snake_case_or_mixed: change pct 2 d | 变化/涨跌 + 百分比 | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::pe_ttm` | unverified / unverified_semantics | snake_case_or_mixed: pe ttm | 市盈率 + 滚动十二个月 | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::main_net_buy_amount` | unverified / unverified_semantics | snake_case_or_mixed: main net buy amount | 净 + 金额/成交额（需看接口） | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::main_net_buy_amount_1d` | unverified / unverified_semantics | snake_case_or_mixed: main net buy amount 1 d | 净 + 金额/成交额（需看接口） | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `TDX(双命名源)::changqifuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: changqifuzhai | 长期负债 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::cunhuo` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: cunhuo | 存货 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::eps` | unverified / unverified_semantics | recognized_english_word_candidate: eps | 每股收益 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::fajirenfarengu` | unverified / unverified_semantics | recognized_pinyin_phrase_candidate: fajirenfarengu | 疑似 faqirenfarengu 的拼写变体；含义未证实 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::gudongrenshu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: gudongrenshu | 股东人数 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::ipodate` | unverified / unverified_semantics | recognized_english_phrase_candidate: ipodate | IPO/上市日期（字段语境候选） | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::jinglirun` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jinglirun | 净利润 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::jingyingxianjinliu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingyingxianjinliu | 经营现金流 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::jingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingzichan | 净资产 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::liudongfuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: liudongfuzhai | 流动负债 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::meigujingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: meigujingzichan | 每股净资产 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::yingshouzhangkuan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: yingshouzhangkuan | 应收账款 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::zhongguben` | unverified / unverified_semantics | recognized_pinyin_phrase_candidate: zhongguben | 疑似 zongguben 的拼写差异；含义未证实 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::zhuyingshouru` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zhuyingshouru | 主营收入 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::zibengongjijin` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zibengongjijin | 资本公积金 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::zongzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongzichan | 总资产 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `同花顺-fuyao::snapshot.open_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot open price | 开盘 + 价格 | T:20261008, T:20261009, T:20261014, T:20261016 |
| `同花顺-fuyao::valuation.pb_mrq` | conflict / unverified_semantics | snake_case_or_mixed: valuation pb mrq | 市净率 + 最近报告期 | T:20261008, T:20261009, T:20261014, T:20261016 |
| `同花顺-fuyao::valuation.pe_mrq` | conflict / unverified_semantics | snake_case_or_mixed: valuation pe mrq | 市盈率 + 最近报告期 | T:20261008, T:20261009, T:20261014, T:20261016 |
| `同花顺-fuyao::valuation.pe_ttm` | conflict / unverified_semantics | snake_case_or_mixed: valuation pe ttm | 市盈率 + 滚动十二个月 | T:20261008, T:20261009, T:20261014, T:20261016 |
| `TDX-eltdx(适配层)::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `市场源(market_sources)::one_word` | unverified / unverified_semantics | snake_case_or_mixed: one word | — | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `市场源(market_sources)::plate_amount` | verified / verified_metadata_gap | snake_case_or_mixed: plate amount | — | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `市场源(market_sources)::plate_code` | verified / verified_metadata_gap | snake_case_or_mixed: plate code | — | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `市场源(market_sources)::plate_name` | verified / verified_metadata_gap | snake_case_or_mixed: plate name | — | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `市场源(market_sources)::popular` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: popular | — | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015, T:20261016 |
| `开盘啦(kpl_limit_up_detail)::max_seal` | verified / verified_metadata_gap | snake_case_or_mixed: max seal | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 |
| `东财-push2ex::broken_count` | unverified / unverified_semantics | snake_case_or_mixed: broken count | — | T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::circulating_value` | unverified / unverified_semantics | snake_case_or_mixed: circulating value | — | T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::limit_fund` | unverified / unverified_semantics | snake_case_or_mixed: limit fund | — | T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::sector` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: sector | — | T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::turnover_rate` | unverified / unverified_semantics | snake_case_or_mixed: turnover rate | — | T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::zt_continuous` | unverified / unverified_semantics | snake_case_or_mixed: zt continuous | — | T:20261008, T:20261014, T:20261016 |
| `东财-push2ex::zt_days` | unverified / unverified_semantics | snake_case_or_mixed: zt days | — | T:20261008, T:20261014, T:20261016 |
| `财联社(cls)::content` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: content | — | C:20261011, C:20261014, C:20261016 |
| `财联社(cls)::level` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: level | — | C:20261011, C:20261014, C:20261016 |
| `财联社(cls)::reading_num` | unverified / unverified_semantics | snake_case_or_mixed: reading num | — | C:20261011, C:20261014, C:20261016 |
| `财联社(cls)::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20261011, C:20261014, C:20261016 |
| `ZHB-tdxstat::board_count` | unverified / unverified_semantics | snake_case_or_mixed: board count | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::change_10k_bar` | unverified / unverified_semantics | snake_case_or_mixed: change 10 k bar | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::change_5k_bar` | unverified / unverified_semantics | snake_case_or_mixed: change 5 k bar | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::change_60d` | unverified / unverified_semantics | snake_case_or_mixed: change 60 d | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::change_ytd` | unverified / unverified_semantics | snake_case_or_mixed: change ytd | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::dividend_yield` | unverified / unverified_semantics | snake_case_or_mixed: dividend yield | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::employee_count` | unverified / unverified_semantics | snake_case_or_mixed: employee count | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::pe_lyr` | unverified / unverified_semantics | snake_case_or_mixed: pe lyr | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::stat.unknown_2` | candidate / unverified_semantics | snake_case_or_mixed: stat unknown 2 | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::stat.unknown_26` | conflict / unverified_semantics | snake_case_or_mixed: stat unknown 26 | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::streak_days` | unverified / unverified_semantics | snake_case_or_mixed: streak days | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::unseal_date` | unverified / unverified_semantics | snake_case_or_mixed: unseal date | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::amount_1d` | unverified / unverified_semantics | snake_case_or_mixed: amount 1 d | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::amount_2d` | unverified / unverified_semantics | snake_case_or_mixed: amount 2 d | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::change_250k_bar` | unverified / unverified_semantics | snake_case_or_mixed: change 250 k bar | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::change_30k_bar` | unverified / unverified_semantics | snake_case_or_mixed: change 30 k bar | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::change_30k_bar_ref` | unverified / unverified_semantics | snake_case_or_mixed: change 30 k bar ref | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::change_mtd` | unverified / unverified_semantics | snake_case_or_mixed: change mtd | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::high_52w` | unverified / unverified_semantics | snake_case_or_mixed: high 52 w | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::industry_code` | unverified / unverified_semantics | snake_case_or_mixed: industry code | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::ipo_price` | unverified / unverified_semantics | snake_case_or_mixed: ipo price | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::main_net_buy_hands` | unverified / unverified_semantics | snake_case_or_mixed: main net buy hands | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::main_net_buy_hands_1d` | unverified / unverified_semantics | snake_case_or_mixed: main net buy hands 1 d | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::zt_seal_amount` | unverified / unverified_semantics | snake_case_or_mixed: zt seal amount | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::zt_seal_amount_1d` | unverified / unverified_semantics | snake_case_or_mixed: zt seal amount 1 d | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::zt_seal_amount_2d` | unverified / unverified_semantics | snake_case_or_mixed: zt seal amount 2 d | — | T:20260930, T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `TDX(双命名源)::baoliu2` | unverified / unverified_semantics | mixed_alphanumeric: baoliu 2 | — | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::ipo_date` | verified / verified_metadata_gap | snake_case_or_mixed: ipo date | — | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::updated_date` | verified / verified_metadata_gap | snake_case_or_mixed: updated date | — | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::updateddate` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: updateddate | — | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::zhuyinglyrun` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: zhuyinglyrun | — | T:20261008, T:20261009, T:20261012, T:20261014, T:20261015 |
| `TDX(双命名源)::b_vol` | unverified / unverified_semantics | snake_case_or_mixed: b vol | — | T:20261008, T:20261009, T:20261012, T:20261014 |
| `TDX(双命名源)::s_vol` | unverified / unverified_semantics | snake_case_or_mixed: s vol | — | T:20261008, T:20261009, T:20261012, T:20261014 |
| `同花顺-fuyao::fin_report` | unverified / unverified_semantics | snake_case_or_mixed: fin report | — | T:20261008, T:20261009, T:20261014, T:20261016 |
| `同花顺-fuyao::snapshot.prev_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot prev price | — | T:20261008, T:20261009, T:20261014, T:20261016 |
| `同花顺-fuyao::valuation.ps_ttm` | conflict / unverified_semantics | snake_case_or_mixed: valuation ps ttm | — | T:20261008, T:20261009, T:20261014, T:20261016 |
| `市场源(market_sources)::rank` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: rank | — | T:20261008, T:20261009, T:20261012, T:20261014 |
| `市场源(market_sources)::main_inflow` | unverified / unverified_semantics | snake_case_or_mixed: main inflow | — | T:20261008 |
| `市场源(market_sources)::max_seal` | unverified / unverified_semantics | snake_case_or_mixed: max seal | — | T:20261008 |
| `市场源(market_sources)::reason` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: reason | — | T:20261008 |

Markdown 显示前 100 条；其余 19 条完整保留在 JSON。

## 探索候选持续跟踪

研究台账：`collision_research_state.json`；累计候选对 1496，本报告候选对 555，历史复现 541，新发现 0。
台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，不会自动改变字段状态、碰撞锚或主字典。
