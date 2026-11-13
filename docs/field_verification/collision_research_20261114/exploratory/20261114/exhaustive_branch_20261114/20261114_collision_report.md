# 全源对撞报告（20261114）

> 交易数据窗口配置：全部历史日期（`--all`）
> 行情窗口：20261015 ~ 20261112（19 个不同交易日）｜字段 1309 个｜样本值 1356938 条
> 新闻/公告自然日窗口：20261015 ~ 20261114
> 主攻目标（unverified）=206｜可审定新候选=5｜首次发现新候选对=0｜已登记关系复验=0｜异号同义 5 / 同号镜像 0

> **规则**：L1 每日需≥18 组有效配对，并至少有5 组信息配对；双方同时为 0 或同时缺失不计命中率，一侧为 0、另一侧非 0 按失配计。信息配对命中率≥90%，且覆盖至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。JSON `daily_sample_counts` 与 `daily_informative_sample_counts`分别保留每日有效配对数和 L1 信息配对数。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 新候选 — 异号同义（跨编号，高价值）(5)

| 左字段(unverified) | 右字段 | 兼容代码 | 关系类别 | 证据依据 | 处理进度 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |
|:--|:--|:--|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|
| `zhb.full.change_30d` | `ulist239.f110` | L1 | multi_day_exact_match | independent_cross_source_value_comparison | candidate_only | 100.00% | 5 | 100 | 100 | - |  | — |
| `ulist239.f297` | `sina[30]` | L1 | date_value_correspondence | independent_cross_source_value_comparison | candidate_only | 100.00% | 4 | 80 | 80 | - |  | — |
| `zhb.full.change_30d` | `tencent[70]` | L1 | multi_day_exact_match | independent_cross_source_value_comparison | candidate_only | 97.73% | 11 | 220 | 220 | - |  | — |
| `zhb.full.high_52w` | `tencent[67]` | L1 | multi_day_exact_match | independent_cross_source_value_comparison | candidate_only | 95.00% | 11 | 220 | 220 | - |  | — |
| `zhb.full.change_ytd` | `push2.f122` | L1 | multi_day_exact_match | independent_cross_source_value_comparison | candidate_only | 90.00% | 5 | 100 | 100 | - |  | — |

## 二、L1 / L1-U 新候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、已登记映射的本窗口复验（0）

_这些关系已在主注册表登记，只用于观察当前样本是否仍支持既有映射；它们不是新的未知字段候选，也不能再次提交为新定案。_

_本轮没有已登记关系进入复验窗口。_


## 四、L4 存疑候选（48）

| 左字段 | 右字段 | 关系类别 | 证据依据 | 处理进度 | 命中率 | 天数 | 样本 |
|:--|:--|:--|:--|:--|--:|--:|--:|
| `zhb.full.change_30d` | `push2.f120` | exploratory_non_anchor_match | independent_cross_source_value_comparison | diagnostic_only | 100.00% | 5 | 100 |
| `tencent[29]` | `zhb.tipinfo.forecast_type` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 100.00% | 1 | 20 |
| `tencent[55]` | `zhb.tipinfo.forecast_type` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 100.00% | 1 | 20 |
| `sina[32]` | `ulist239.f190` | exploratory_non_anchor_match | independent_cross_source_value_comparison | diagnostic_only | 95.00% | 7 | 140 |
| `sina[32]` | `ulist239.f231` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 95.00% | 7 | 140 |
| `ulist239.f190` | `tdx.finance_info.hgu` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 94.93% | 7 | 138 |
| `sina[32]` | `tdx.finance_info.hgu` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 94.69% | 18 | 358 |
| `push2ex.zt_continuous` | `kph.limit_count` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 93.00% | 11 | 457 |
| `sina[32]` | `eltdx.quote_snapshot.unknown_after_outer_raw` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 91.67% | 18 | 360 |
| `kph.industry_limit_up_count` | `kpl.raw_columns.col_20` | exploratory_non_anchor_match | independent_cross_source_value_comparison | diagnostic_only | 90.00% | 11 | 500 |
| `sina[32]` | `ulist239.f200` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 90.00% | 7 | 140 |
| `sina[32]` | `zhb.full.other_qy_jzc` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 90.00% | 11 | 220 |
| `sina[32]` | `zhb.stat.other_qy_jzc` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 90.00% | 11 | 220 |
| `ulist239.f190` | `zhb.full.other_qy_jzc` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 90.00% | 5 | 100 |
| `ulist239.f190` | `zhb.stat.other_qy_jzc` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 90.00% | 5 | 100 |
| `zhb.full.change_ytd` | `ulist239.f25` | exploratory_non_anchor_match | independent_cross_source_value_comparison | diagnostic_only | 90.00% | 5 | 100 |
| `sina[32]` | `tdx.finance_info.bgu` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 89.66% | 18 | 358 |
| `ulist239.f190` | `eltdx.quote_snapshot.unknown_after_outer_raw` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 87.14% | 7 | 140 |
| `push2ex.zt_days` | `kph.limit_count` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 86.65% | 11 | 457 |
| `zhb.full.high_52w` | `push2.f174` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 86.51% | 7 | 126 |
| `push2ex.zt_continuous` | `kpl.raw_columns.col_15` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 86.32% | 17 | 1053 |
| `push2ex.zt_days` | `kpl.raw_columns.col_15` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 86.32% | 17 | 1053 |
| `ulist239.f190` | `tdx.finance_info.bgu` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 84.78% | 7 | 138 |
| `zhb.full.dividend_yield` | `tencent[64]` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 75.91% | 11 | 220 |
| `tencent[7]` | `ulist239.f34` | exploratory_non_anchor_match | independent_cross_source_value_comparison | diagnostic_only | 75.00% | 7 | 140 |
| `tencent[8]` | `ulist239.f35` | exploratory_non_anchor_match | independent_cross_source_value_comparison | diagnostic_only | 75.00% | 7 | 140 |
| `push2.f161` | `tencent[8]` | exploratory_non_anchor_match | independent_cross_source_value_comparison | diagnostic_only | 74.74% | 11 | 194 |
| `push2.f49` | `tencent[7]` | exploratory_non_anchor_match | independent_cross_source_value_comparison | diagnostic_only | 74.74% | 11 | 194 |
| `zhb.full.change_ytd` | `tencent[62]` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 71.82% | 11 | 220 |
| `kpl.raw_columns.col_16` | `push2ex.broken_count` | exploratory_non_anchor_match | independent_cross_source_value_comparison | diagnostic_only | 70.28% | 17 | 1053 |
| `ulist239.f11` | `tencent[80]` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 70.00% | 7 | 140 |
| `zhb.full.dividend_yield` | `ulist239.f133` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 70.00% | 5 | 100 |
| `zhb.full.change_250k_bar` | `tencent[79]` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 67.73% | 11 | 220 |
| `sina[32]` | `ulist239.f13` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 60.00% | 7 | 140 |
| `sina[32]` | `ulist239.f27` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 60.00% | 7 | 140 |
| `sina[32]` | `ulist239.f97` | exploratory_non_anchor_match | independent_cross_source_value_comparison | diagnostic_only | 58.57% | 7 | 140 |
| `sina[32]` | `push2.f107` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 57.22% | 11 | 194 |
| `sina[32]` | `push2.f110` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 57.22% | 11 | 194 |
| `ulist239.f97` | `zhb.full.other_qy_jzc` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 57.00% | 5 | 100 |
| `ulist239.f97` | `zhb.stat.other_qy_jzc` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 57.00% | 5 | 100 |
| `ulist239.f97` | `tdx.finance_info.hgu` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 55.80% | 7 | 138 |
| `ulist239.f97` | `eltdx.quote_snapshot.unknown_after_outer_raw` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 53.57% | 7 | 140 |
| `ulist239.f97` | `tdx.finance_info.bgu` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 50.72% | 7 | 138 |
| `sina[32]` | `ulist239.f147` | exploratory_non_anchor_match | independent_cross_source_value_comparison | diagnostic_only | 49.29% | 7 | 140 |
| `kpl.raw_columns.col_02` | `kph.limit_count` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 46.00% | 11 | 500 |
| `kpl.raw_columns.col_16` | `kph.limit_count` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 45.40% | 11 | 500 |
| `kpl.raw_columns.col_02` | `push2ex.limit_count` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 43.02% | 17 | 1053 |
| `kpl.raw_columns.col_16` | `push2ex.limit_count` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 42.26% | 17 | 1053 |

## 五、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 六、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `kph.industry_limit_up_count` | `kpl.raw_columns.col_20` | robust_correlation, affine_formula, per_stock_time_series | 500 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028, T:20261030 | kph, kpl | Pearson=0.993, Spearman=0.9895, LOO稳号=True |
| `push2ex.turnover_rate` | `kph.turnover_rate` | robust_correlation, per_stock_time_series, semantic_label | 457 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028, T:20261030 | kph, push2ex | Pearson=0.8466, Spearman=0.8897, LOO稳号=True |
| `tencent[22]` | `sina[22]` | robust_correlation, affine_formula, per_stock_time_series | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[28]` | `tencent[28]` | robust_correlation, affine_formula, per_stock_time_series | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[26]` | `tencent[26]` | robust_correlation, affine_formula, per_stock_time_series | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[24]` | `tencent[24]` | robust_correlation, affine_formula, per_stock_time_series | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[18]` | `tencent[18]` | robust_correlation, affine_formula, per_stock_time_series | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[16]` | `tencent[16]` | robust_correlation, affine_formula, per_stock_time_series | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[14]` | `tencent[14]` | robust_correlation, affine_formula, per_stock_time_series | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.high_52w` | `tencent[68]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=0.9994, Spearman=0.9182, LOO稳号=True |
| `zhb.full.high_52w` | `tencent[67]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_ytd` | `tencent[75]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=0.9845, Spearman=0.9699, LOO稳号=True |
| `zhb.full.change_ytd` | `tencent[62]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_30d` | `tencent[70]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_250k_bar` | `tencent[79]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `push2.f49` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 194 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, sina | Pearson=0.9946, Spearman=0.9947, LOO稳号=True |
| `push2.f49` | `ftshare_rest.volume` | robust_correlation, affine_formula, per_stock_time_series | 194 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | ftshare_rest, push2 | Pearson=0.9946, Spearman=0.9947, LOO稳号=True |
| `push2.f49` | `eltdx.quote_snapshot.total_hand` | robust_correlation, affine_formula, per_stock_time_series | 194 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | eltdx, push2 | Pearson=0.9946, Spearman=0.9947, LOO稳号=True |
| `push2.f49` | `eltdx.quote_snapshot.outer_disc` | robust_correlation, affine_formula, per_stock_time_series | 194 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | eltdx, push2 | Pearson=0.9982, Spearman=0.9985, LOO稳号=True |
| `push2.f49` | `eltdx.quote_snapshot.inside_dish` | robust_correlation, affine_formula, per_stock_time_series | 194 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | eltdx, push2 | Pearson=0.9827, Spearman=0.9832, LOO稳号=True |
| `push2.f161` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 194 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, sina | Pearson=0.9945, Spearman=0.9945, LOO稳号=True |
| `push2.f161` | `ftshare_rest.volume` | robust_correlation, affine_formula, per_stock_time_series | 194 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | ftshare_rest, push2 | Pearson=0.9945, Spearman=0.9945, LOO稳号=True |
| `push2.f161` | `eltdx.quote_snapshot.total_hand` | robust_correlation, affine_formula, per_stock_time_series | 194 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | eltdx, push2 | Pearson=0.9945, Spearman=0.9945, LOO稳号=True |
| `push2.f161` | `eltdx.quote_snapshot.outer_disc` | robust_correlation, affine_formula, per_stock_time_series | 194 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | eltdx, push2 | Pearson=0.9826, Spearman=0.9823, LOO稳号=True |
| `push2.f161` | `eltdx.quote_snapshot.inside_dish` | robust_correlation, affine_formula, per_stock_time_series | 194 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | eltdx, push2 | Pearson=0.9981, Spearman=0.9986, LOO稳号=True |
| `push2.f49` | `tdx.s_vol` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9827, Spearman=0.9833, LOO稳号=True |
| `push2.f49` | `tdx.quote_raw.s_vol` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9827, Spearman=0.9833, LOO稳号=True |
| `push2.f49` | `tdx.quote_raw.b_vol` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9982, Spearman=0.9984, LOO稳号=True |
| `push2.f49` | `tdx.quote_full.s_vol` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9827, Spearman=0.9833, LOO稳号=True |
| `push2.f49` | `tdx.quote_full.b_vol` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9982, Spearman=0.9984, LOO稳号=True |
| `push2.f49` | `tdx.b_vol` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9982, Spearman=0.9984, LOO稳号=True |
| `push2.f161` | `tdx.s_vol` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9981, Spearman=0.9986, LOO稳号=True |
| `push2.f161` | `tdx.quote_raw.s_vol` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9981, Spearman=0.9986, LOO稳号=True |
| `push2.f161` | `tdx.quote_raw.b_vol` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9826, Spearman=0.9823, LOO稳号=True |
| `push2.f161` | `tdx.quote_full.s_vol` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9981, Spearman=0.9986, LOO稳号=True |
| `push2.f161` | `tdx.quote_full.b_vol` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9826, Spearman=0.9823, LOO稳号=True |
| `push2.f161` | `tdx.b_vol` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9826, Spearman=0.9823, LOO稳号=True |
| `zhb.full.change_ytd` | `ftshare_rest.change_rate_ytd` | robust_correlation, per_stock_time_series, semantic_label | 180 | T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103 | ftshare_rest, zhb | Pearson=0.9428, Spearman=0.9554, LOO稳号=True |
| `push2.f49` | `fuyao.snapshot.volume` | robust_correlation, affine_formula, per_stock_time_series | 180 | T:20261020, T:20261023, T:20261029, T:20261102, T:20261103, T:20261104 | fuyao, push2 | Pearson=0.9956, Spearman=0.9949, LOO稳号=True |
| `push2.f161` | `fuyao.snapshot.volume` | robust_correlation, affine_formula, per_stock_time_series | 180 | T:20261020, T:20261023, T:20261029, T:20261102, T:20261103, T:20261104 | fuyao, push2 | Pearson=0.9958, Spearman=0.9944, LOO稳号=True |
| `ulist239.f11` | `tencent[80]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | tencent, ulist239 | Pearson=0.987, Spearman=0.9721, LOO稳号=True |
| `zhb.full.high_52w` | `push2.f175` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=0.9994, Spearman=0.9228, LOO稳号=True |
| `zhb.full.high_52w` | `push2.f174` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=1.0, Spearman=0.9997, LOO稳号=True |
| `zhb.full.change_ytd` | `push2.f122` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_30d` | `push2.f120` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_ytd` | `ulist239.f25` | robust_correlation, affine_formula, per_stock_time_series | 100 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_30k_bar` | `ulist239.f24` | robust_correlation, affine_formula, per_stock_time_series | 100 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb | Pearson=0.9806, Spearman=0.798, LOO稳号=True |
| `zhb.full.change_30d` | `ulist239.f110` | robust_correlation, affine_formula, per_stock_time_series | 100 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.TOTAL_SHARES` | `ftshare_rest.shares` | robust_correlation, affine_formula, semantic_label | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.CHANGE_RATE` | `ftshare_rest.change_rate` | robust_correlation, affine_formula, semantic_label | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.CHANGE_RATE` | `ftshare_rest.change` | robust_correlation, affine_formula, semantic_label | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=0.9959, Spearman=0.9978, LOO稳号=True |
| `event_dc.CHANGE` | `ftshare_rest.change_rate` | robust_correlation, affine_formula, semantic_label | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=0.9959, Spearman=0.9978, LOO稳号=True |
| `event_dc.CHANGE` | `ftshare_rest.change` | robust_correlation, affine_formula, semantic_label | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `push2ex.turnover_rate` | `sina_extended.turnover` | robust_correlation, affine_formula, semantic_label | 13 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | push2ex, sina_extended | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `push2ex.turnover_rate` | `ftshare_rest.turnover_rate` | robust_correlation, affine_formula, semantic_label | 12 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | ftshare_rest, push2ex | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `push2ex.zt_days` | `kpl.raw_columns.col_15` | robust_correlation, per_stock_time_series | 1053 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, push2ex | Pearson=0.4457, Spearman=0.7188, LOO稳号=True |
| `push2ex.zt_continuous` | `kpl.raw_columns.col_15` | robust_correlation, per_stock_time_series | 1053 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, push2ex | Pearson=0.6205, Spearman=0.7698, LOO稳号=True |
| `push2ex.turnover_rate` | `kpl.turnover_real` | robust_correlation, per_stock_time_series | 1053 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, push2ex | Pearson=0.863, Spearman=0.9007, LOO稳号=True |
| `push2ex.turnover_rate` | `kpl.raw_columns.col_14` | robust_correlation, per_stock_time_series | 1053 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, push2ex | Pearson=0.863, Spearman=0.9007, LOO稳号=True |
| `push2ex.turnover_rate` | `kpl.raw_columns.col_11` | robust_correlation, per_stock_time_series | 1053 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, push2ex | Pearson=0.3518, Spearman=0.6448, LOO稳号=True |
| `push2ex.turnover_rate` | `kpl.amount` | robust_correlation, per_stock_time_series | 1053 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, push2ex | Pearson=0.3518, Spearman=0.6448, LOO稳号=True |
| `push2ex.total_value` | `kpl.raw_columns.col_13` | robust_correlation, per_stock_time_series | 1053 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, push2ex | Pearson=0.9005, Spearman=0.8135, LOO稳号=True |
| `push2ex.circulating_value` | `kpl.raw_columns.col_13` | robust_correlation, per_stock_time_series | 1053 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, push2ex | Pearson=0.9554, Spearman=0.8359, LOO稳号=True |
| `kpl.raw_columns.col_17` | `push2ex.first_limit_time` | robust_correlation, per_stock_time_series | 1053 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, push2ex | Pearson=0.4673, Spearman=0.6297, LOO稳号=True |
| `kpl.raw_columns.col_16` | `push2ex.broken_count` | robust_correlation, per_stock_time_series | 1053 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, push2ex | Pearson=0.535, Spearman=0.9242, LOO稳号=True |
| `kpl.raw_columns.col_10` | `push2ex.amount` | robust_correlation, per_stock_time_series | 1053 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, push2ex | Pearson=-0.9479, Spearman=-0.9435, LOO稳号=True |
| `kpl.raw_columns.col_09` | `push2ex.amount` | robust_correlation, per_stock_time_series | 1053 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, push2ex | Pearson=0.961, Spearman=0.9471, LOO稳号=True |
| `kpl.main_sell` | `push2ex.amount` | robust_correlation, per_stock_time_series | 1053 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, push2ex | Pearson=-0.9479, Spearman=-0.9435, LOO稳号=True |
| `kpl.main_buy` | `push2ex.amount` | robust_correlation, per_stock_time_series | 1053 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, push2ex | Pearson=0.961, Spearman=0.9471, LOO稳号=True |
| `kpl.amplitude` | `push2ex.first_limit_time` | robust_correlation, per_stock_time_series | 1053 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, push2ex | Pearson=0.4673, Spearman=0.6297, LOO稳号=True |
| `kpl.raw_columns.col_10` | `kph.turnover` | robust_correlation, per_stock_time_series | 500 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028, T:20261030 | kph, kpl | Pearson=-0.9472, Spearman=-0.94, LOO稳号=True |
| `kpl.raw_columns.col_09` | `kph.turnover` | robust_correlation, per_stock_time_series | 500 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028, T:20261030 | kph, kpl | Pearson=0.9642, Spearman=0.9357, LOO稳号=True |
| `kpl.main_sell` | `kph.turnover` | robust_correlation, per_stock_time_series | 500 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028, T:20261030 | kph, kpl | Pearson=-0.9472, Spearman=-0.94, LOO稳号=True |
| `kpl.main_buy` | `kph.turnover` | robust_correlation, per_stock_time_series | 500 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028, T:20261030 | kph, kpl | Pearson=0.9642, Spearman=0.9357, LOO稳号=True |
| `push2ex.zt_days` | `kph.limit_count` | robust_correlation, per_stock_time_series | 457 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028, T:20261030 | kph, push2ex | Pearson=0.7083, Spearman=0.8986, LOO稳号=True |
| `push2ex.zt_continuous` | `kph.limit_count` | robust_correlation, per_stock_time_series | 457 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028, T:20261030 | kph, push2ex | Pearson=0.783, Spearman=0.9144, LOO稳号=True |
| `push2ex.turnover_rate` | `kph.turnover` | per_stock_time_series, semantic_label | 457 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028, T:20261030 | kph, push2ex | 逐股相关=0.9891, 方向一致=1.0 |
| `tencent[8]` | `sina[8]` | robust_correlation, per_stock_time_series | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.0432, Spearman=0.6577, LOO稳号=True |
| `tencent[8]` | `eltdx.quote_snapshot.total_hand` | robust_correlation, per_stock_time_series | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.0432, Spearman=0.6577, LOO稳号=True |
| `tencent[8]` | `eltdx.quote_snapshot.outer_disc` | robust_correlation, per_stock_time_series | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.0434, Spearman=0.6467, LOO稳号=True |
| `tencent[8]` | `eltdx.quote_snapshot.inside_dish` | robust_correlation, per_stock_time_series | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.0425, Spearman=0.6641, LOO稳号=True |
| `tencent[7]` | `sina[8]` | robust_correlation, per_stock_time_series | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.0477, Spearman=0.6586, LOO稳号=True |
| `tencent[7]` | `eltdx.quote_snapshot.total_hand` | robust_correlation, per_stock_time_series | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.0477, Spearman=0.6586, LOO稳号=True |
| `tencent[7]` | `eltdx.quote_snapshot.outer_disc` | robust_correlation, per_stock_time_series | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.0526, Spearman=0.6643, LOO稳号=True |
| `tencent[7]` | `eltdx.quote_snapshot.inside_dish` | robust_correlation, per_stock_time_series | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.0421, Spearman=0.6501, LOO稳号=True |
| `tencent[8]` | `tdx.s_vol` | robust_correlation, per_stock_time_series | 338 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | tdx, tencent | Pearson=0.0412, Spearman=0.6628, LOO稳号=True |
| `tencent[8]` | `tdx.quote_raw.s_vol` | robust_correlation, per_stock_time_series | 338 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | tdx, tencent | Pearson=0.0412, Spearman=0.6628, LOO稳号=True |
| `tencent[8]` | `tdx.quote_raw.b_vol` | robust_correlation, per_stock_time_series | 338 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | tdx, tencent | Pearson=0.0419, Spearman=0.6462, LOO稳号=True |
| `tencent[8]` | `tdx.quote_full.s_vol` | robust_correlation, per_stock_time_series | 338 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | tdx, tencent | Pearson=0.0412, Spearman=0.6628, LOO稳号=True |
| `tencent[8]` | `tdx.quote_full.b_vol` | robust_correlation, per_stock_time_series | 338 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | tdx, tencent | Pearson=0.0419, Spearman=0.6462, LOO稳号=True |
| `tencent[8]` | `tdx.b_vol` | robust_correlation, per_stock_time_series | 338 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | tdx, tencent | Pearson=0.0419, Spearman=0.6462, LOO稳号=True |
| `tencent[7]` | `tdx.s_vol` | robust_correlation, per_stock_time_series | 338 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | tdx, tencent | Pearson=0.0383, Spearman=0.6478, LOO稳号=True |
| `tencent[7]` | `tdx.quote_raw.s_vol` | robust_correlation, per_stock_time_series | 338 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | tdx, tencent | Pearson=0.0383, Spearman=0.6478, LOO稳号=True |
| `tencent[7]` | `tdx.quote_raw.b_vol` | robust_correlation, per_stock_time_series | 338 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | tdx, tencent | Pearson=0.0489, Spearman=0.6637, LOO稳号=True |
| `tencent[7]` | `tdx.quote_full.s_vol` | robust_correlation, per_stock_time_series | 338 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | tdx, tencent | Pearson=0.0383, Spearman=0.6478, LOO稳号=True |
| `tencent[7]` | `tdx.quote_full.b_vol` | robust_correlation, per_stock_time_series | 338 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | tdx, tencent | Pearson=0.0489, Spearman=0.6637, LOO稳号=True |
| `tencent[7]` | `tdx.b_vol` | robust_correlation, per_stock_time_series | 338 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | tdx, tencent | Pearson=0.0489, Spearman=0.6637, LOO稳号=True |
| `tencent[8]` | `fuyao.snapshot.volume` | robust_correlation, per_stock_time_series | 320 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028 | fuyao, tencent | Pearson=0.0449, Spearman=0.6558, LOO稳号=True |
| `tencent[7]` | `fuyao.snapshot.volume` | robust_correlation, per_stock_time_series | 320 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028 | fuyao, tencent | Pearson=0.0441, Spearman=0.6553, LOO稳号=True |
| `tencent[8]` | `ftshare_rest.volume` | robust_correlation, per_stock_time_series | 300 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | ftshare_rest, tencent | Pearson=0.044, Spearman=0.6584, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 七、日期与数据质量告警（330）

- 20261017: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261018: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261031: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261101: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261107: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261113: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
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
- 20261015/zhb: 来源有效交易日 20261014 不在本轮行情交易日窗口，快照跳过
- 20261016/ftshare: 采集状态 failed
- 20261016/sse_e_interaction: 采集状态 partial
- 20261016/ftshare: 来源状态为 failed，快照跳过
- 20261016/sse_e_interaction: 来源状态为 partial，样本按部分快照参与
- 20261016/tdx_f10_more: 没有可用记录，快照跳过
- 20261019/zhb: 采集状态 partial
- 20261019/em_kline_f61: 采集状态 partial
- 20261019/em_fund_flow: 采集状态 partial
- 20261019/ulist239: 采集状态 failed
- 20261019/ftshare: 采集状态 failed
- 20261019/em_fund_flow: 来源状态为 partial，样本按部分快照参与
- 20261019/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20261019/em_kline_f61: 没有可用记录，快照跳过
- 20261019/ftshare: 来源状态为 failed，快照跳过
- 20261019/tdx_f10: 没有可用记录，快照跳过
- 20261019/tdx_f10_more: 没有可用记录，快照跳过
- 20261019/ulist239: 来源状态为 failed，快照跳过
- 20261019/zhb: 来源状态为 partial，样本按部分快照参与
- 20261020/zhb: 采集状态 partial
- 20261020/push2: 采集状态 partial
- 20261020/em_kline_f61: 采集状态 partial
- 20261020/em_fund_flow: 采集状态 partial
- 20261020/ulist239: 采集状态 failed
- 20261020/clist: 采集状态 partial
- 20261020/slist: 采集状态 failed
- 20261020/st_list: 采集状态 partial
- 20261020/clist: 来源状态为 partial，样本按部分快照参与
- 20261020/clist: 没有可用记录，快照跳过
- 20261020/em_fund_flow: 来源状态为 partial，样本按部分快照参与
- 20261020/em_fund_flow: 没有可用记录，快照跳过
- 20261020/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20261020/em_kline_f61: 没有可用记录，快照跳过
- 20261020/push2: 来源状态为 partial，样本按部分快照参与
- 20261020/slist: 来源状态为 failed，快照跳过
- 20261020/st_list: 来源状态为 partial，样本按部分快照参与
- 20261020/st_list: 没有可用记录，快照跳过
- 20261020/tdx_f10: 没有可用记录，快照跳过
- 20261020/tdx_f10_more: 没有可用记录，快照跳过
- 20261020/ulist239: 来源状态为 failed，快照跳过
- 20261020/zhb: 来源状态为 partial，样本按部分快照参与
- 20261021/zhb: 采集状态 partial
- 20261021/push2: 采集状态 failed
- 20261021/axdata: 采集状态 failed
- 20261021/em_kline_f61: 采集状态 partial
- 20261021/em_fund_flow: 采集状态 partial
- 20261021/ulist239: 采集状态 failed
- 20261021/clist: 采集状态 partial
- 20261021/slist: 采集状态 failed
- 20261021/st_list: 采集状态 partial
- 20261021/axdata: 来源状态为 failed，快照跳过
- 20261021/clist: 来源状态为 partial，样本按部分快照参与
- 20261021/clist: 没有可用记录，快照跳过
- 20261021/em_fund_flow: 来源状态为 partial，样本按部分快照参与
- 20261021/em_fund_flow: 没有可用记录，快照跳过
- 20261021/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20261021/em_kline_f61: 没有可用记录，快照跳过
- 20261021/push2: 来源状态为 failed，快照跳过
- 20261021/slist: 来源状态为 failed，快照跳过
- 20261021/st_list: 来源状态为 partial，样本按部分快照参与
- 20261021/st_list: 没有可用记录，快照跳过
- 20261021/tdx_f10: 没有可用记录，快照跳过
- 另有 230 条告警，详见同名 JSON 报告。

---

> 数据来源：通达信 / 项目字段对撞体系。以上为方法论梳理，不构成投资建议。

## 来源身份状态（不参与字段语义定案）

_FTShare 公共 REST 接口已进入日常采集；官方字段契约作为语义锚，底层数据提供方仍未确认。与其匹配的强候选列在 L1-C，不混入独立来源 L1。_
_旧私有托管 MCP 采集器已退役，历史样本仅供 `--all` / `--exploratory` 追溯。_

## 官方契约锚候选 L1-C（0）

_L1-C 使用逐字段审定的官方接口契约语义作锚，并满足多日数值匹配门槛；仅当该接口底层数据来源独立性未确认时才列入此处，不属于独立来源 L1，也不自动定案。_

_本轮无达到多日门槛的官方契约锚候选。_

## 字段时效与来源日期证据

_字段语义关系和来源日期可信度分开记录。`source_dates_confirmed` 表示两侧入选样本都有来源或记录级日期；`semantic_only_date_unconfirmed` 只支持缓变/静态字段的语义关系，不证明数据新鲜度或具体有效日期；`cross_source_dates_inferred` 表示日期通过独立、已确认日期的来源对同股同日精确值交叉推断，并不代表目标源自身提供了日期。未分类字段按来源日期严格门控。_

策略状态：`ok`；逐源分类字段 75，保守默认未分类字段 1234。L1/L1-C 日期证据：来源日期已确认 5 条，跨源值见证推断 0 条，仅语义证据且日期未确认 0 条，其他日期未确认 0 条。

| 日期见证关系 | 结果 | 交易日 | 精确样本 | 非零精确样本 | 不同非零值 | 证据 SHA-256 |
|:--|:--|--:|--:|--:|--:|:--|
| `tdx.quote_raw.ask1_vol <- tencent[20]` | thresholds_met | 17 | 338/338 | 325/325 | 228 | `9f488224d9a95673bf751451c47a3fd1ae05090b51cf090dc014d66818252d69` |
| `tdx.quote_raw.bid1_vol <- tencent[10]` | thresholds_met | 17 | 338/338 | 335/335 | 227 | `9f488224d9a95673bf751451c47a3fd1ae05090b51cf090dc014d66818252d69` |

_本轮 L1/L1-C 没有仅凭静态或缓变字段、且来源日期未确认的关系。_

## 来源字段覆盖与碰撞参与

_窗口字段值样本是经日期筛选、重复折叠和快照择优后载入的非空值；右侧比较次数另受字段类型及来源规则筛选。官方契约字段须有逐字段审定证据，契约语义本身不证明底层数据来源独立。_

| 来源 | 已确认字段 | 契约已确认 | 契约锚 | 独立锚 | L1-C 锚 | 窗口字段 / 字段值样本 / 交易日 |
|:--|--:|--:|--:|--:|--:|--:|
| axdata | 34 | 0 | 0 | 0 | 0 | 34 / 9043 / 17 |
| clist | 20 | 0 | 0 | 20 | 0 | 33 / 50169 / 7 |
| cls | 4 | 0 | 0 | 4 | 0 | 5 / 4250 / 0 |
| cninfo | 6 | 0 | 0 | 6 | 0 | 0 / 0 / 0 |
| datacenter | 42 | 1 | 1 | 42 | 0 | 0 / 0 / 0 |
| eltdx | 208 | 136 | 136 | 208 | 0 | 116 / 19738 / 18 |
| em_fund_flow | 15 | 0 | 0 | 15 | 0 | 15 / 2295 / 8 |
| em_hot | 39 | 0 | 0 | 39 | 0 | 0 / 0 / 0 |
| em_kline_f61 | 11 | 1 | 1 | 11 | 0 | 2 / 280 / 7 |
| etf | 0 | 0 | 0 | 0 | 0 | 9 / 198516 / 17 |
| event_dc | 0 | 0 | 0 | 0 | 0 | 148 / 493782 / 16 |
| exchange | 4 | 0 | 0 | 4 | 0 | 0 / 0 / 0 |
| ftshare | 6 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| ftshare_rest | 31 | 31 | 31 | 0 | 31 | 32 / 9525 / 15 |
| fuyao | 91 | 77 | 77 | 91 | 0 | 20 / 6420 / 17 |
| kph | 12 | 0 | 0 | 12 | 0 | 15 / 7965 / 12 |
| kpl | 11 | 0 | 0 | 11 | 0 | 28 / 37534 / 18 |
| market_sources | 14 | 0 | 0 | 0 | 0 | 74 / 139518 / 18 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 2 / 402 / 0 |
| push2 | 64 | 0 | 0 | 64 | 0 | 114 / 22116 / 11 |
| push2ex | 24 | 0 | 0 | 24 | 0 | 16 / 25392 / 17 |
| reports | 43 | 0 | 0 | 43 | 0 | 49 / 931 / 0 |
| research_sina | 0 | 0 | 0 | 0 | 0 | 6 / 6252 / 0 |
| sina | 27 | 0 | 0 | 27 | 0 | 39 / 12420 / 18 |
| sina_extended | 3 | 3 | 3 | 3 | 0 | 4 / 1280 / 16 |
| slist | 5 | 0 | 0 | 5 | 0 | 1 / 140 / 7 |
| sse_e_interaction | 0 | 0 | 0 | 0 | 0 | 8 / 1360 / 0 |
| st_list | 0 | 0 | 0 | 0 | 0 | 6 / 17106 / 9 |
| tdx | 232 | 103 | 103 | 232 | 0 | 63 / 22472 / 18 |
| tencent | 76 | 0 | 0 | 76 | 0 | 88 / 31644 / 18 |
| ulist239 | 57 | 0 | 0 | 57 | 0 | 240 / 33540 / 7 |
| zhb | 243 | 26 | 26 | 243 | 0 | 130 / 24235 / 11 |

| 来源 | 破解目标 | 比较字段 | 作目标比较 | 作右侧比较 | L1-C 锚比较 | L1 / L1-C / L4 关系 | 方法候选涉及 |
|:--|--:|--:|--:|--:|--:|--:|--:|
| axdata | 0 | 30 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| clist | 10 | 27 | 3782 | 1326 | 0 | 0 / 0 / 0 | 0 |
| cls | 2 | 2 | 770 | 10 | 0 | 0 / 0 / 0 | 0 |
| cninfo | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| datacenter | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| eltdx | 29 | 82 | 11945 | 3534 | 0 | 0 / 0 / 3 | 586 |
| em_fund_flow | 0 | 15 | 0 | 1170 | 0 | 0 / 0 / 0 | 111 |
| em_hot | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| em_kline_f61 | 1 | 1 | 391 | 26 | 0 | 0 / 0 / 0 | 12 |
| etf | 4 | 4 | 29 | 0 | 0 | 0 / 0 / 0 | 0 |
| event_dc | 62 | 62 | 1258 | 0 | 0 | 0 / 0 / 0 | 201 |
| exchange | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare_rest | 1 | 26 | 23 | 4127 | 4127 | 0 / 0 / 0 | 387 |
| fuyao | 0 | 14 | 0 | 1652 | 0 | 0 / 0 / 0 | 134 |
| kph | 1 | 10 | 670 | 988 | 0 | 0 / 0 / 5 | 33 |
| kpl | 11 | 22 | 5986 | 2198 | 0 | 0 / 0 / 8 | 426 |
| market_sources | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| push2 | 7 | 92 | 1231 | 6416 | 0 | 1 / 0 / 6 | 613 |
| push2ex | 7 | 12 | 2667 | 642 | 0 | 0 / 0 / 7 | 408 |
| reports | 3 | 19 | 1143 | 948 | 0 | 0 / 0 / 0 | 0 |
| research_sina | 2 | 2 | 673 | 71 | 0 | 0 / 0 / 0 | 0 |
| sina | 8 | 34 | 4968 | 3010 | 0 | 1 / 0 / 14 | 482 |
| sina_extended | 0 | 3 | 0 | 327 | 0 | 0 / 0 / 0 | 19 |
| slist | 1 | 1 | 372 | 45 | 0 | 0 / 0 / 0 | 7 |
| sse_e_interaction | 1 | 1 | 23 | 0 | 0 | 0 / 0 / 0 | 0 |
| st_list | 3 | 3 | 48 | 0 | 0 | 0 / 0 / 0 | 0 |
| tdx | 0 | 58 | 0 | 4288 | 0 | 0 / 0 / 6 | 254 |
| tencent | 9 | 83 | 4099 | 7947 | 0 | 2 / 0 / 10 | 1044 |
| ulist239 | 18 | 172 | 5861 | 11280 | 0 | 2 / 0 / 22 | 684 |
| zhb | 26 | 101 | 10712 | 6646 | 0 | 4 / 0 / 15 | 1633 |

## 来源/接口重叠审阅（不自动停采）

此处按**完整规范路径**和来源实际日期对齐比较已采值，单独呈现同家族、不同仓库或血缘未明来源的重叠。数值一致只说明观测范围内的路径等价候选，不证明底层提供方相同、字段语义相同或整条路由可删除。只有接口字段覆盖、唯一字段、备用关系和复验策略均核实后，才可调整采集路由。
来源对 24 组；保留详情 24 组；路径身份歧义 5 项；采集自动停用：否。

| 来源 A / 仓库 | 来源 B / 仓库 | 血缘关系 | 观测关系 | 共同路径 | 强匹配路径 | 失配路径/失配样本/近似样本/未对齐样本 | A/B 独有路径 | 强匹配完整路径样例 |
|:--|:--|:--|:--|--:|--:|--:|:--|:--|
| `sina` / https://github.com/shidenggui/easyquotation | `tencent` / https://github.com/shidenggui/easyquotation | different_confirmed_provider_families | observed_value_differences | 39 | 1 | 38/11869/3084/0 | 0/49 | `[3]` |
| `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | provider_relation_unconfirmed | insufficient_aligned_evidence | 17 | 0 | 0/0/0/1096 | 11/57 | — |
| `em_fund_flow` / https://github.com/fleetinglife/levistock | `ulist239` / https://github.com/fleetinglife/levistock | same_confirmed_provider_family | insufficient_aligned_evidence | 15 | 0 | 0/0/0/2100 | 0/225 | — |
| `em_fund_flow` / https://github.com/fleetinglife/levistock | `push2` / https://github.com/fleetinglife/levistock | same_confirmed_provider_family | insufficient_aligned_evidence | 15 | 0 | 0/0/0/2100 | 0/99 | — |
| `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `push2ex` / https://github.com/fleetinglife/levistock | provider_relation_unconfirmed | insufficient_aligned_evidence | 7 | 0 | 0/0/0/7732 | 67/9 | — |
| `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | provider_relation_unconfirmed | insufficient_aligned_evidence | 4 | 0 | 0/0/0/1486 | 11/70 | — |
| `push2ex` / https://github.com/fleetinglife/levistock | `tdx` / https://github.com/yanwei99521/easy-tdx | different_confirmed_provider_families | insufficient_aligned_evidence | 3 | 0 | 0/0/0/48 | 13/60 | — |
| `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `tdx` / https://github.com/yanwei99521/easy-tdx | provider_relation_unconfirmed | insufficient_aligned_evidence | 3 | 0 | 0/0/0/159 | 71/60 | — |
| `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `push2ex` / https://github.com/fleetinglife/levistock | different_confirmed_provider_families | insufficient_aligned_evidence | 3 | 0 | 0/0/0/2106 | 25/13 | — |
| `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | `push2ex` / https://github.com/fleetinglife/levistock | different_confirmed_provider_families | insufficient_aligned_evidence | 3 | 0 | 0/0/0/1371 | 12/13 | — |
| `ftshare_rest` / — | `tdx` / https://github.com/yanwei99521/easy-tdx | provider_relation_unconfirmed | insufficient_aligned_evidence | 3 | 0 | 0/0/0/894 | 29/60 | — |
| `ftshare_rest` / — | `push2ex` / https://github.com/fleetinglife/levistock | provider_relation_unconfirmed | insufficient_aligned_evidence | 2 | 0 | 0/0/0/24 | 30/14 | — |
| `ftshare_rest` / — | `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | provider_relation_unconfirmed | insufficient_aligned_evidence | 2 | 0 | 0/0/0/71 | 30/72 | — |
| `push2ex` / https://github.com/fleetinglife/levistock | `zhb` / https://github.com/yanwei99521/easy-tdx, https://github.com/yanwei99521/easy-tdx | different_confirmed_provider_families | insufficient_aligned_evidence | 1 | 0 | 0/0/0/8 | 15/129 | — |
| `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `zhb` / https://github.com/yanwei99521/easy-tdx, https://github.com/yanwei99521/easy-tdx | provider_relation_unconfirmed | insufficient_aligned_evidence | 1 | 0 | 0/0/0/41 | 73/129 | — |
| `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | `sina_extended` / https://github.com/mpquant/Ashare | different_confirmed_provider_families | insufficient_aligned_evidence | 1 | 0 | 0/0/0/3 | 14/3 | — |
| `ftshare_rest` / — | `sina_extended` / https://github.com/mpquant/Ashare | provider_relation_unconfirmed | insufficient_aligned_evidence | 1 | 0 | 0/0/0/300 | 31/3 | — |
| `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | different_confirmed_provider_families | observed_value_differences | 3 | 0 | 1/3/0/0 | 12/25 | — |
| `ftshare_rest` / — | `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | provider_relation_unconfirmed | observed_value_differences | 2 | 0 | 1/11/0/0 | 30/26 | — |
| `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `zhb` / https://github.com/yanwei99521/easy-tdx, https://github.com/yanwei99521/easy-tdx | different_confirmed_provider_families | observed_value_differences | 1 | 0 | 1/6/0/0 | 27/129 | — |
| `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | `zhb` / https://github.com/yanwei99521/easy-tdx, https://github.com/yanwei99521/easy-tdx | different_confirmed_provider_families | observed_value_differences | 1 | 0 | 1/1/0/0 | 14/129 | — |
| `ftshare_rest` / — | `zhb` / https://github.com/yanwei99521/easy-tdx, https://github.com/yanwei99521/easy-tdx | provider_relation_unconfirmed | observed_value_differences | 1 | 0 | 1/108/0/0 | 31/129 | — |
| `ftshare_rest` / — | `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | provider_relation_unconfirmed | observed_value_differences | 4 | 0 | 3/9/3/0 | 28/11 | — |
| `push2` / https://github.com/fleetinglife/levistock | `ulist239` / https://github.com/fleetinglife/levistock | same_confirmed_provider_family | observed_value_differences | 113 | 0 | 107/14789/3/280 | 1/127 | — |

强匹配路径不得有值失配、未对齐样本或低信息常量，并达到每条路径至少 5 个信息样本、3 个不同样本日期、3 只证券；宽松舍入窗口只列为独立近似样本数，不计强匹配；该筛选只产生路由复核候选，不取代现有接口专用退出和复验规则。

## AxData 每日接口核验

> 此处汇总采集目录已保存的本地证据，不发起网络请求、不改变注册表状态；AxData 是多源框架，不作为独立字段锚。

### AxData

窗口内有 19 个唯一数据日的轮验记录；重复目录合并 0 条。
静态接口队列：257 个接口，3343 个字段出现项，低于 E3 的字段出现项 3343；当前主动探针白名单 `tencent_realtime_snapshot`。
静态候选策略：static review only until route, parameters, date basis, and request safety are approved。

| 数据日 | 轮验状态 | 探针状态 / 请求数 | 来源身份状态 | 短线配对 | KPH/KPL 配对 | 证据文件 |
|:--|:--|:--|:--|--:|--:|:--|
| 20261015 | probe_skipped | skipped_project_counterpart_failed / 0 (字段相同/不同 0/0) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 0 | — | full |
| 20261016 | already_recorded | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | — | 50 | full |
| 20261019 | sampled | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261020 | already_recorded | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | — | — | full |
| 20261021 | sampled | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | — | 45 | full |
| 20261022 | not_eligible | not_run / 0 (字段相同/不同 0/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing | — | — | meta_summary |
| 20261023 | already_recorded | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261026 | already_recorded | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | — | — | full |
| 20261028 | sampled | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261029 | sampled | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261030 | already_recorded | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | 44 | full |
| 20261102 | sampled | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261103 | sampled | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261104 | sampled | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261105 | sampled | sampled / 1 (字段相同/不同 0/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261106 | already_recorded | sampled / 1 (字段相同/不同 0/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | 30 | full |
| 20261109 | already_recorded | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261110 | already_recorded | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261112 | already_recorded | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |

被动逐字段比较中的差异计数（跨本窗口唯一数据日累加，不含原始值）：

| 比较路径 | 相同 | 不同 | 缺失/双方空值 |
|:--|--:|--:|--:|
| `axdata_shortline_vs_eltdx:alignment_status` | 0 | 260 | 0 |
| `axdata_shortline_vs_eltdx:beta_60d` | 0 | 260 | 0 |
| `axdata_shortline_vs_eltdx:code` | 0 | 260 | 0 |
| `axdata_shortline_vs_eltdx:full_code` | 0 | 260 | 0 |
| `axdata_shortline_vs_eltdx:instrument_id` | 0 | 260 | 0 |
| `axdata_shortline_vs_eltdx:limit_status` | 0 | 260 | 0 |
| `axdata_shortline_vs_eltdx:market_id` | 0 | 260 | 0 |
| `axdata_shortline_vs_eltdx:opening_rush` | 0 | 260 | 0 |
| `axdata_shortline_vs_eltdx:pe_ttm` | 0 | 260 | 0 |
| `axdata_shortline_vs_eltdx:previous_trade_date` | 0 | 260 | 0 |
| `axdata_shortline_vs_eltdx:symbol` | 0 | 260 | 0 |
| `axdata_shortline_vs_eltdx:target_trade_date` | 0 | 260 | 0 |
| `axdata_shortline_vs_eltdx:tdx_code` | 0 | 260 | 0 |
| `axdata_shortline_vs_eltdx:open_amount` | 50 | 210 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_hand` | 50 | 210 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_ratio` | 50 | 210 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_amount_ratio` | 63 | 197 | 0 |
| `axdata_shortline_vs_eltdx:auction_prev_volume_ratio` | 72 | 185 | 3 |
| `axdata_shortline_vs_eltdx:open_turnover_z` | 137 | 123 | 0 |
| `kph_limit_up_history_vs_kpl_detail:seal_amount` | 74 | 95 | 0 |
| `kph_limit_up_history_vs_kpl_detail:seal_money` | 74 | 95 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_seal_ratio` | 4 | 10 | 246 |
| `axdata_shortline_vs_eltdx:ladder_level` | 0 | 8 | 252 |
| `axdata_shortline_vs_eltdx:limit_board_text` | 21 | 7 | 232 |

### FTShare 退役来源历史记录（显式历史研究）

窗口内保留 3 个唯一数据日的旧元数据；重复目录合并 0 条。

| 数据日 | 历史状态 | 旧接口状态计数 |
|:--|:--|:--|
| 20261015 | ok | pending: 6 |
| 20261016 | ok | pending: 6 |
| 20261019 | ok | pending: 6 |

## 字母字段名语义提示（仅候选）

窗口内观察到 121 条需审阅的字母字段路径：含词义线索 29 条，仅拆词 92 条。
完整逐条记录保存在碰撞 JSON；名称线索清单：`docs/field_verification/20261014/20261014_alphabetic_field_name_inventory.csv`。
> 拼音、英文、缩写和混合拆词只用于检索候选；必须结合原始值、接口定义和独立来源复核，不得据此定案或改写主字典。

| 逐源字段路径 | 状态/审阅范围 | 名称形式与拆词 | 词义线索（非释义） | 样本日期 |
|:--|:--|:--|:--|:--|
| `市场源(market_sources)::change_type` | unverified / unverified_semantics | snake_case_or_mixed: change type | 变化/涨跌 + 类型 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `市场源(market_sources)::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `东财-push2ex::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `东财-push2ex::first_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: first limit time | 首次/第一 + 涨跌停限制 + 时间 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `东财-push2ex::last_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: last limit time | 最近/上一期 + 涨跌停限制 + 时间 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `东财-push2ex::name` | unverified / unverified_semantics | recognized_english_word_candidate: name | 名称 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `东财-push2ex::total_value` | unverified / unverified_semantics | snake_case_or_mixed: total value | 总 + 值 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `市场源(market_sources)::limit_count` | verified / verified_metadata_gap | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `市场源(market_sources)::limit_time` | unverified / unverified_semantics | snake_case_or_mixed: limit time | 涨跌停限制 + 时间 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `市场源(market_sources)::plate_limit_up_count` | verified / verified_metadata_gap | snake_case_or_mixed: plate limit up count | 涨跌停限制 + 上/涨 + 数量/次数 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `财联社(cls)::time` | unverified / unverified_semantics | recognized_english_word_candidate: time | 时间 | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110, C:20261112 |
| `TDX(双命名源)::changqifuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: changqifuzhai | 长期负债 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `TDX(双命名源)::cunhuo` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: cunhuo | 存货 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `TDX(双命名源)::jingyingxianjinliu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingyingxianjinliu | 经营现金流 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `TDX(双命名源)::jingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingzichan | 净资产 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `TDX(双命名源)::liudongfuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: liudongfuzhai | 流动负债 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `TDX(双命名源)::meigujingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: meigujingzichan | 每股净资产 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `TDX(双命名源)::yingshouzhangkuan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: yingshouzhangkuan | 应收账款 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `TDX(双命名源)::zibengongjijin` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zibengongjijin | 资本公积金 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `TDX(双命名源)::zongzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongzichan | 总资产 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `同花顺-fuyao::snapshot.open_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot open price | 开盘 + 价格 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `reports::count` | verified / verified_metadata_gap | recognized_english_word_candidate: count | 数量/次数 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::lastEmRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Code | 最近/上一期 + 代码 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::lastEmRatingName` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Name | 最近/上一期 + 名称 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::lastEmRatingValue` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Value | 最近/上一期 + 值 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::predictLastYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Eps | 最近/上一期 + 每股收益 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::predictLastYearPe` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Pe | 最近/上一期 + 市盈率 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `TDX-eltdx(适配层)::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `东财-push2ex::broken_count` | unverified / unverified_semantics | snake_case_or_mixed: broken count | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `东财-push2ex::circulating_value` | unverified / unverified_semantics | snake_case_or_mixed: circulating value | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `东财-push2ex::sector` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: sector | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `东财-push2ex::turnover_rate` | unverified / unverified_semantics | snake_case_or_mixed: turnover rate | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `东财-push2ex::zt_continuous` | unverified / unverified_semantics | snake_case_or_mixed: zt continuous | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `东财-push2ex::zt_days` | unverified / unverified_semantics | snake_case_or_mixed: zt days | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `市场源(market_sources)::one_word` | unverified / unverified_semantics | snake_case_or_mixed: one word | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `市场源(market_sources)::plate_amount` | verified / verified_metadata_gap | snake_case_or_mixed: plate amount | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `市场源(market_sources)::plate_code` | verified / verified_metadata_gap | snake_case_or_mixed: plate code | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `市场源(market_sources)::plate_name` | verified / verified_metadata_gap | snake_case_or_mixed: plate name | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `市场源(market_sources)::popular` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: popular | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `开盘啦(kpl_limit_up_detail)::raw_columns.col_19` | verified / verified_metadata_gap | runtime_tokenization_only: col 19 | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `财联社(cls)::content` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: content | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110, C:20261112 |
| `财联社(cls)::level` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: level | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110, C:20261112 |
| `财联社(cls)::reading_num` | unverified / unverified_semantics | snake_case_or_mixed: reading num | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110, C:20261112 |
| `财联社(cls)::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110, C:20261112 |
| `开盘红::industry_limit_up_count` | unverified / unverified_semantics | runtime_tokenization_only: industry limit up count | — | T:20261016, T:20261019, T:20261021, T:20261022, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 |
| `同花顺-fuyao::fin_report` | unverified / unverified_semantics | snake_case_or_mixed: fin report | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `市场源(market_sources)::big_order_300w_net` | unverified / unverified_semantics | runtime_tokenization_only: big order 300 w net | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `市场源(market_sources)::institution_add` | unverified / unverified_semantics | runtime_tokenization_only: institution add | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `市场源(market_sources)::main_inflow` | unverified / unverified_semantics | snake_case_or_mixed: main inflow | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `市场源(market_sources)::pe_next` | unverified / unverified_semantics | runtime_tokenization_only: pe next | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `市场源(market_sources)::pe_now` | unverified / unverified_semantics | runtime_tokenization_only: pe now | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `市场源(market_sources)::strength` | unverified / unverified_semantics | runtime_tokenization_only: strength | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `市场源(market_sources)::total_value` | unverified / unverified_semantics | runtime_tokenization_only: total value | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `同花顺-fuyao::snapshot.prev_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot prev price | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `新浪(扩展API)::opendate` | conflict / unverified_semantics | unsegmented_latin_pinyin_or_word: opendate | — | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `FTShare REST::amplitude` | verified / verified_metadata_gap | runtime_tokenization_only: amplitude | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `FTShare REST::avg` | verified / verified_metadata_gap | runtime_tokenization_only: avg | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `FTShare REST::bid_ask_ratio` | verified / verified_metadata_gap | runtime_tokenization_only: bid ask ratio | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `FTShare REST::board` | verified / verified_metadata_gap | runtime_tokenization_only: board | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `FTShare REST::listing_date` | verified / verified_metadata_gap | runtime_tokenization_only: listing date | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `FTShare REST::name` | verified / verified_metadata_gap | runtime_tokenization_only: name | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `FTShare REST::st` | verified / verified_metadata_gap | runtime_tokenization_only: st | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `FTShare REST::status` | verified / verified_metadata_gap | runtime_tokenization_only: status | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `FTShare REST::symbol` | verified / verified_metadata_gap | runtime_tokenization_only: symbol | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `FTShare REST::symbol_id` | unverified / unverified_semantics | runtime_tokenization_only: symbol id | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `FTShare REST::turnover_rate` | verified / verified_metadata_gap | runtime_tokenization_only: turnover rate | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `FTShare REST::pe_ttm` | verified / verified_metadata_gap | runtime_tokenization_only: pe ttm | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `ZHB-tdxstat::stat.unknown_2` | verified / verified_metadata_gap | snake_case_or_mixed: stat unknown 2 | — | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 |
| `ZHB-tdxstat::stat.unknown_26` | verified / verified_metadata_gap | snake_case_or_mixed: stat unknown 26 | — | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 |
| `市场源(market_sources)::rank` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: rank | — | T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `TDX-eltdx(适配层)::trade_date` | unverified / unverified_semantics | snake_case_or_mixed: trade date | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112 |
| `reports::attachType` | verified / verified_metadata_gap | camel_case_or_mixed: attach Type | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::column` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: column | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::emIndustryCode` | unverified / unverified_semantics | camel_case_or_mixed: em Industry Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::emRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: em Rating Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::emRatingName` | verified / verified_metadata_gap | camel_case_or_mixed: em Rating Name | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::emRatingValue` | verified / verified_metadata_gap | camel_case_or_mixed: em Rating Value | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::encodeUrl` | conflict / unverified_semantics | camel_case_or_mixed: encode Url | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::industryCode` | verified / verified_metadata_gap | camel_case_or_mixed: industry Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::industryName` | verified / verified_metadata_gap | camel_case_or_mixed: industry Name | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::indvInduCode` | verified / verified_metadata_gap | camel_case_or_mixed: indv Indu Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::indvInduName` | verified / verified_metadata_gap | camel_case_or_mixed: indv Indu Name | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::indvIsNew` | verified / verified_metadata_gap | camel_case_or_mixed: indv Is New | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::infoCode` | verified / verified_metadata_gap | camel_case_or_mixed: info Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::newPurchaseDate` | verified / verified_metadata_gap | camel_case_or_mixed: new Purchase Date | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::orgCode` | verified / verified_metadata_gap | camel_case_or_mixed: org Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::orgName` | verified / verified_metadata_gap | camel_case_or_mixed: org Name | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::orgSName` | verified / verified_metadata_gap | camel_case_or_mixed: org S Name | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::orgType` | unverified / unverified_semantics | camel_case_or_mixed: org Type | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::predictNextTwoYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Next Two Year Eps | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::predictNextTwoYearPe` | conflict / unverified_semantics | camel_case_or_mixed: predict Next Two Year Pe | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::predictNextYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Next Year Eps | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::predictNextYearPe` | conflict / unverified_semantics | camel_case_or_mixed: predict Next Year Pe | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::predictThisYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict This Year Eps | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::predictThisYearPe` | conflict / unverified_semantics | camel_case_or_mixed: predict This Year Pe | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::publishDate` | verified / verified_metadata_gap | camel_case_or_mixed: publish Date | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |
| `reports::ratingChange` | verified / verified_metadata_gap | camel_case_or_mixed: rating Change | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111 |

Markdown 显示前 100 条；其余 21 条完整保留在 JSON。

## 探索候选持续跟踪

研究台账：`collision_research_state.json.gz`；累计历史跟踪候选对 3189，本报告候选对 620，历史复现 550，新发现 70。
台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，不会自动改变字段状态、碰撞锚或主字典。新报告只将 `actionable_L1`、L4 和主动方法候选写入待研究队列；已登记关系的复验单独展示，历史跟踪记录不会被删除。

## 候选覆盖、公式与下一步采样

本节用于定位证据缺口和安排后续取样。相关性、公式与样本优先级均为探索候选；不会改变 L1/L1-U 门槛、来源独立性或主字典。

- 未知目标 206 个；其中有方法候选 118 个、无候选 88 个；多候选目标 110 个；有官方契约锚强匹配 0 个、诊断命中 0 个，日期值候选 1 个。
- 方法候选生成 3517 条；全局详细项保留 500/500，另按目标字段保留 92 条；完整明细 3517 条在 JSON `method_candidate_inventory`；未归档明细 0 条。
- 字段覆盖详情：available；覆盖身份 1976，读取 19 份本地索引。

### 优先处理字段

| 未知字段 | 核验入口 | 当前诊断 | 官方锚强/诊断 | 独立对比/候选数 | 独立锚家族/本源日期 | 建议复核股票 | 最强候选线索 |
|:--|:--|:--|--:|--:|:--|:--|:--|
| `zhb.full.change_30k_bar_ref` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 122 | 6 家族 / 287 对 / 本源 11 日 | 600825 (1.644457) | tencent[75] (robust_correlation,per_stock_time_series); tencent[71] (robust_correlation,per_stock_time_series) |
| `zhb.full.dividend_yield` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 120 | 6 家族 / 287 对 / 本源 10 日 | 600519 (49.81127) | tencent[64] (robust_correlation,per_stock_time_series); ulist239.f133 (robust_correlation,per_stock_time_series) |
| `zhb.full.change_ytd` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 107 | 6 家族 / 287 对 / 本源 11 日 | 600825 (1.860585) | tencent[75] (robust_correlation,affine_formula,per_stock_time_series); tencent[62] (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.change_30d` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 102 | 6 家族 / 287 对 / 本源 0 日 | 002242 (3.571035) | tencent[70] (robust_correlation,affine_formula,per_stock_time_series); push2.f120 (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.change_250k_bar` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 101 | 6 家族 / 287 对 / 本源 11 日 | 002242 (1.961517) | tencent[79] (robust_correlation,affine_formula,per_stock_time_series); tencent[75] (robust_correlation,per_stock_time_series) |
| `zhb.full.change_30k_bar` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 100 | 6 家族 / 287 对 / 本源 11 日 | 600825 (3.536658) | ulist239.f24 (robust_correlation,affine_formula,per_stock_time_series); tencent[75] (robust_correlation,per_stock_time_series) |
| `zhb.full.high_52w` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 97 | 6 家族 / 287 对 / 本源 11 日 | 600519 (20.540023) | tencent[68] (robust_correlation,affine_formula,per_stock_time_series); tencent[67] (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f176` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 358 / 95 | 6 家族 / 316 对 / 本源 0 日 | 600519 (14.135462) | tencent[46] (robust_correlation,per_stock_time_series); fuyao.valuation.ps_ttm (robust_correlation,per_stock_time_series) |
| `push2ex.total_value` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 358 / 91 | 6 家族 / 316 对 / 本源 0 日 | no_shared_stock_holdout | kpl.raw_columns.col_13 (robust_correlation,per_stock_time_series); tencent[45] (robust_correlation,affine_formula) |
| `push2ex.circulating_value` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 358 / 87 | 6 家族 / 316 对 / 本源 0 日 | no_shared_stock_holdout | kpl.raw_columns.col_13 (robust_correlation,per_stock_time_series); tencent[45] (robust_correlation,affine_formula) |
| `ulist239.f63` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 342 / 87 | 6 家族 / 316 对 / 本源 0 日 | no_shared_stock_holdout | eltdx.shortline.open_volume_ratio (robust_correlation,per_stock_time_series); eltdx.shortline.open_volume_hand (robust_correlation,per_stock_time_series) |
| `tencent[7]` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 550 / 71 | 6 家族 / 406 对 / 本源 18 日 | no_shared_stock_holdout | sina[8] (robust_correlation,per_stock_time_series); eltdx.quote_snapshot.total_hand (robust_correlation,per_stock_time_series) |
| `zhb.full.employee_count` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 71 | 6 家族 / 287 对 / 本源 10 日 | 601288 (6.362856) | tencent[76] (robust_correlation,affine_formula); tencent[73] (robust_correlation,affine_formula) |
| `tencent[8]` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 550 / 65 | 6 家族 / 406 对 / 本源 18 日 | no_shared_stock_holdout | sina[8] (robust_correlation,per_stock_time_series); eltdx.quote_snapshot.total_hand (robust_correlation,per_stock_time_series) |
| `zhb.full.amount_1d` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 65 | 6 家族 / 287 对 / 本源 10 日 | 600519 (23.399812) | tencent[85] (robust_correlation); tencent[76] (robust_correlation) |
| `zhb.full.main_net_buy_amount` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 65 | 6 家族 / 287 对 / 本源 11 日 | 600519 (3.120821) | tencent[79] (robust_correlation); tencent[75] (robust_correlation) |
| `zhb.full.main_net_buy_amount_1d` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 64 | 6 家族 / 287 对 / 本源 11 日 | 601288 (2.787159) | tencent[79] (robust_correlation); tencent[75] (robust_correlation) |
| `zhb.full.amount_2d` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 61 | 6 家族 / 287 对 / 本源 10 日 | 600519 (23.777711) | tencent[85] (robust_correlation); tencent[75] (robust_correlation) |
| `zhb.full.main_net_buy_hands_1d` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 57 | 6 家族 / 287 对 / 本源 11 日 | 600519 (2.418048) | tencent[75] (robust_correlation); tencent[70] (robust_correlation) |
| `zhb.full.main_net_buy_hands` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 56 | 6 家族 / 287 对 / 本源 11 日 | 600519 (2.987993) | tencent[79] (robust_correlation); tencent[75] (robust_correlation) |
| `push2.f49` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 358 / 54 | 6 家族 / 316 对 / 本源 0 日 | candidates_converge_on_existing_samples | sina[8] (robust_correlation,affine_formula,per_stock_time_series); ftshare_rest.volume (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.board_count` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 53 | 6 家族 / 287 对 / 本源 10 日 | 688327 (10.511923) | tencent[6] (robust_correlation); tencent[68] (robust_correlation) |
| `zhb.full.change_10k_bar` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 53 | 6 家族 / 287 对 / 本源 10 日 | 600519 (12.726161) | tencent[69] (robust_correlation,per_stock_time_series); tencent[63] (robust_correlation,per_stock_time_series) |
| `push2.f161` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 358 / 51 | 6 家族 / 316 对 / 本源 0 日 | candidates_converge_on_existing_samples | sina[8] (robust_correlation,affine_formula,per_stock_time_series); ftshare_rest.volume (robust_correlation,affine_formula,per_stock_time_series) |
| `kpl.main_sell` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 629 / 50 | 6 家族 / 455 对 / 本源 0 日 | 300296 (2.046956) | push2ex.amount (robust_correlation,per_stock_time_series); kph.turnover (robust_correlation,per_stock_time_series) |
| `kpl.raw_columns.col_10` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 629 / 50 | 6 家族 / 455 对 / 本源 0 日 | 300296 (2.046956) | push2ex.amount (robust_correlation,per_stock_time_series); kph.turnover (robust_correlation,per_stock_time_series) |
| `kpl.main_buy` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 629 / 46 | 6 家族 / 455 对 / 本源 0 日 | 300296 (2.673385) | push2ex.amount (robust_correlation,per_stock_time_series); kph.turnover (robust_correlation,per_stock_time_series) |
| `kpl.raw_columns.col_09` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 629 / 46 | 6 家族 / 455 对 / 本源 0 日 | 300296 (2.673385) | push2ex.amount (robust_correlation,per_stock_time_series); kph.turnover (robust_correlation,per_stock_time_series) |
| `push2ex.turnover_rate` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 358 / 46 | 6 家族 / 316 对 / 本源 0 日 | no_shared_stock_holdout | kph.turnover_rate (robust_correlation,per_stock_time_series,semantic_label); sina_extended.turnover (robust_correlation,affine_formula,semantic_label) |
| `eltdx.limit_ladder.open_price` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 446 / 45 | 6 家族 / 287 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[85] (robust_correlation,affine_formula) |
| `eltdx.limit_ladder.pre_close` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 446 / 45 | 6 家族 / 287 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[85] (robust_correlation,affine_formula) |
| `kpl.raw_columns.col_02` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 629 / 45 | 6 家族 / 455 对 / 本源 0 日 | no_shared_stock_holdout | tencent[8] (robust_correlation); tencent[76] (robust_correlation) |
| `ulist239.f149` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 342 / 44 | 6 家族 / 316 对 / 本源 0 日 | 000678 (3.155604) | tencent[63] (robust_correlation,per_stock_time_series); ftshare_rest.change_rate_day5 (robust_correlation,per_stock_time_series) |
| `sina[26]` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 598 / 40 | 6 家族 / 446 对 / 本源 18 日 | 600519 (13.39842) | tencent[26] (robust_correlation,affine_formula,per_stock_time_series); tencent[68] (robust_correlation) |
| `sina[14]` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 598 / 36 | 6 家族 / 446 对 / 本源 18 日 | 600519 (18.424447) | tencent[14] (robust_correlation,affine_formula,per_stock_time_series); tencent[68] (robust_correlation) |
| `sina[16]` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 598 / 36 | 6 家族 / 446 对 / 本源 18 日 | 600519 (15.652799) | tencent[16] (robust_correlation,affine_formula,per_stock_time_series); tencent[68] (robust_correlation) |
| `sina[18]` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 598 / 36 | 6 家族 / 446 对 / 本源 18 日 | 601288 (11.898294) | tencent[18] (robust_correlation,affine_formula,per_stock_time_series); tencent[68] (robust_correlation) |
| `sina[24]` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 598 / 33 | 6 家族 / 446 对 / 本源 18 日 | 601288 (14.751885) | tencent[24] (robust_correlation,affine_formula,per_stock_time_series); tencent[67] (robust_correlation) |
| `sina[28]` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 598 / 30 | 6 家族 / 446 对 / 本源 18 日 | 601288 (14.690812) | tencent[28] (robust_correlation,affine_formula,per_stock_time_series); tencent[26] (robust_correlation) |
| `tencent[26]` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 550 / 29 | 6 家族 / 406 对 / 本源 18 日 | 600519 (12.699126) | sina[22] (robust_correlation); sina[20] (robust_correlation) |
| `eltdx.limit_ladder.prev_amount` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 446 / 28 | 6 家族 / 287 对 / 本源 0 日 | no_shared_stock_holdout | tencent[8] (robust_correlation); tencent[7] (robust_correlation) |
| `eltdx.limit_ladder.open_volume_hand` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 446 / 27 | 6 家族 / 287 对 / 本源 0 日 | no_shared_stock_holdout | tencent[8] (robust_correlation); tencent[86] (robust_correlation) |
| `kpl.amplitude` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 629 / 27 | 6 家族 / 455 对 / 本源 0 日 | no_shared_stock_holdout | push2ex.first_limit_time (robust_correlation,per_stock_time_series); tencent[43] (robust_correlation,affine_formula) |
| `kpl.raw_columns.col_17` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 629 / 27 | 6 家族 / 455 对 / 本源 0 日 | no_shared_stock_holdout | push2ex.first_limit_time (robust_correlation,per_stock_time_series); tencent[43] (robust_correlation,affine_formula) |
| `push2ex.zt_continuous` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 358 / 27 | 6 家族 / 316 对 / 本源 0 日 | no_shared_stock_holdout | kpl.raw_columns.col_15 (robust_correlation,per_stock_time_series); kph.limit_count (robust_correlation,per_stock_time_series) |
| `tencent[24]` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 550 / 27 | 6 家族 / 406 对 / 本源 18 日 | 600519 (11.756436) | sina[22] (robust_correlation); sina[20] (robust_correlation) |
| `tencent[28]` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 550 / 27 | 6 家族 / 406 对 / 本源 18 日 | 600519 (10.740867) | sina[22] (robust_correlation); sina[20] (robust_correlation) |
| `zhb.full.change_mtd` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 389 / 27 | 6 家族 / 287 对 / 本源 10 日 | 600519 (5.705826) | tencent[69] (robust_correlation,per_stock_time_series); tencent[63] (robust_correlation,per_stock_time_series) |
| `push2ex.zt_days` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 358 / 26 | 6 家族 / 316 对 / 本源 0 日 | no_shared_stock_holdout | kpl.raw_columns.col_15 (robust_correlation,per_stock_time_series); kph.limit_count (robust_correlation,per_stock_time_series) |
| `eltdx.limit_ladder.open_prev_amount_ratio` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 446 / 25 | 6 家族 / 287 对 / 本源 0 日 | no_shared_stock_holdout | tencent[86] (robust_correlation); tencent[67] (robust_correlation) |

_此表显示优先级最高的 50 / 共 206 个目标；完整清单见 JSON。_


### 舍入近似数值线索（仅研究，不算 L1/L1-U；2 组）

近似窗口只用于提示复核：需核对双方原始单位、展示精度和来源口径；不得把该命中率当作字段语义结论或注册表写回依据。完整明细在 JSON `candidate_triage.approximate_matches`。

| 左字段 | 右字段 | 近似命中率 | 精确/舍入命中 | 有效日期 | 最大误差（绝对/相对） |
|:--|:--|--:|:--|:--|:--|
| `zhb.full.high_52w` | `push2.f174` | 98.00% | 88/10 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | 0.030000000000001137 / 0.0017411491584446393 |
| `zhb.full.change_250k_bar` | `tencent[79]` | 92.69% | 148/55 | T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | 0.11999999999999744 / 0.004822446295484412 |

### 补足全局截断的字段候选（92）

| 未知字段 | 候选字段 | 方法 | 样本 | 日期 | 来源 |
|:--|:--|:--|--:|:--|:--|
| `eltdx.limit_ladder.auction_prev_volume_ratio` | `tencent[69]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.beta_60d` | `tencent[76]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.ladder_level` | `tencent[68]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_amount` | `tencent[8]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_change_pct` | `tencent[86]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_prev_amount_ratio` | `tencent[86]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_turnover_z` | `tencent[8]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_volume_hand` | `tencent[8]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_volume_ratio` | `tencent[86]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.pe_ttm` | `tencent[64]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.prev_amount` | `tencent[8]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.prev_open_amount` | `tencent[8]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.prev_open_volume_hand` | `tencent[86]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.seal_to_amount_ratio` | `tencent[86]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.seal_to_float_ratio` | `tencent[86]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.year_limit_up_days` | `tencent[86]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `em_kline_f61.dktotal` | `tencent[30]` | per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | em_kline_f61, tencent |
| `event_dc.AMPLITUDE` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.AVERAGE_PRICE` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.CHANGE_RATE` | `ftshare_rest.change_rate_ytd` | semantic_label | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.CLOSE_PRICE` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.EACHBALLOT_SHARES` | `ftshare_rest.shares` | semantic_label | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.IPO_YIELD` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.ISSUE_NUM` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.ISSUE_PRICE` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LATELY_PRICE` | `ftshare_rest.prev_close` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LD_AVERAGE_PRICE` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LD_CLOSE_CHANGE` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LD_HIGH_CHANG` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LD_OPEN_PREMIUM` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LIMIT_UP_PRICE` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.MZYQ_PAY_FUND` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.OD_HIGH_CHANGE` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.OPEN_AVERAGE_PRICE` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.OPEN_PRICE` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.PROFIT` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TCHANGE_RATE` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TNEW_PRICE` | `ftshare_rest.prev_close` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TOTAL_CHANGE` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TOTAL_ISSUE_NUM` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TOTAL_SHARES` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TURNOVERRATE` | `ftshare_rest.volume` | robust_correlation | 30 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `kpl.amplitude` | `tencent[86]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, tencent |
| `kpl.main_buy` | `tencent[8]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, tencent |
| `kpl.raw_columns.col_02` | `tencent[8]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, tencent |
| `kpl.raw_columns.col_09` | `tencent[8]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, tencent |
| `kpl.raw_columns.col_16` | `tencent[43]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, tencent |
| `kpl.raw_columns.col_17` | `tencent[86]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, tencent |
| `kpl.raw_columns.col_20` | `tencent[73]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, tencent |
| `push2.f176` | `tencent[9]` | per_stock_time_series | 194 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2ex.broken_count` | `tencent[8]` | robust_correlation | 16 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | push2ex, tencent |
| `push2ex.first_limit_time` | `tencent[43]` | robust_correlation | 16 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | push2ex, tencent |
| `push2ex.zt_continuous` | `tencent[79]` | robust_correlation | 16 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | push2ex, tencent |
| `push2ex.zt_days` | `tencent[79]` | robust_correlation | 16 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | push2ex, tencent |
| `sina[14]` | `tencent[68]` | robust_correlation | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[16]` | `tencent[68]` | robust_correlation | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[18]` | `tencent[68]` | robust_correlation | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[24]` | `tencent[67]` | robust_correlation | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[26]` | `tencent[68]` | robust_correlation | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[28]` | `tencent[26]` | robust_correlation | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[36]` | `push2.f62` | robust_correlation | 17 | T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, sina |
| `slist.n_boards` | `tencent[45]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | slist, tencent |
| `tencent[22]` | `sina[20]` | robust_correlation | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `tencent[24]` | `sina[22]` | robust_correlation | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `tencent[26]` | `sina[22]` | robust_correlation | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `tencent[28]` | `sina[22]` | robust_correlation | 360 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `tencent[86]` | `eltdx.shortline.prev2_seal_amount` | robust_correlation | 18 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261026 | eltdx, tencent |
| `ulist239.f111` | `zhb.tipinfo.hg_amount_yi` | robust_correlation | 30 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `ulist239.f127` | `tencent[63]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f139` | `tencent[76]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f148` | `tencent[71]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f190` | `tencent[76]` | affine_formula | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f192` | `tencent[76]` | affine_formula | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f22` | `tencent[80]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f59` | `tencent[39]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f98` | `zhb.stat.zt_streak_cycle` | robust_correlation | 17 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `ulist239.f99` | `eltdx.shortline.limit_up_count_in_stat_days` | robust_correlation | 22 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | eltdx, ulist239 |
| `zhb.full.amount_1d` | `tencent[85]` | robust_correlation | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028 | tencent, zhb |
| `zhb.full.amount_2d` | `tencent[85]` | robust_correlation | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028 | tencent, zhb |
| `zhb.full.board_count` | `tencent[6]` | robust_correlation | 55 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028 | tencent, zhb |
| `zhb.full.change_10k_bar` | `tencent[9]` | per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028 | tencent, zhb |
| `zhb.full.change_30k_bar` | `tencent[9]` | per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028 | tencent, zhb |
| `zhb.full.change_5k_bar` | `tencent[69]` | robust_correlation | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028 | tencent, zhb |
| `zhb.full.change_mtd` | `push2.f71` | per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104 | push2, zhb |
| `zhb.full.dividend_yield` | `tencent[9]` | per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028 | tencent, zhb |
| `zhb.full.main_net_buy_amount` | `tencent[79]` | robust_correlation | 217 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028 | tencent, zhb |
| `zhb.full.main_net_buy_amount_1d` | `tencent[79]` | robust_correlation | 218 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028 | tencent, zhb |
| `zhb.full.main_net_buy_hands` | `tencent[79]` | robust_correlation | 217 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028 | tencent, zhb |
| `zhb.full.main_net_buy_hands_1d` | `tencent[75]` | robust_correlation | 218 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028 | tencent, zhb |
| `zhb.full.zt_seal_amount_1d` | `tencent[69]` | robust_correlation | 12 | T:20261016, T:20261019, T:20261023, T:20261028, T:20261102 | tencent, zhb |
| `zhb.full.zt_seal_amount_2d` | `tencent[79]` | robust_correlation | 12 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028 | tencent, zhb |
| `zhb.tipinfo.unlock_shares_wan` | `tencent[76]` | affine_formula | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028 | tencent, zhb |

### 双输入公式候选
本轮未发现通过留出筛选的公式候选；测试组合 4139 个。


### 已知映射与已证伪关系的候选校准

- 已登记正向对照：当前窗口有 158 组独立数值关系可评估，155 组被方法候选识别；样本不足 0 组。此计数仅检查方法覆盖，不是准确率。
- 已证伪负向对照：数值关系 0 组，其中仍有方法信号 0 组；这些信号被隔离，不进入普通候选。

### 采集覆盖异常源

- axdata: 20261021, 20261026 ({'failed': 1, 'ok': 16, 'partial': 1})
- baidu: 20261109, 20261110, 20261112 ({'deprecated': 2, 'pending_validation': 15})
- clist: 20261029, 20261030, 20261112 ({'ok': 7, 'partial': 9})
- em_fund_flow: 20261029, 20261030, 20261112 ({'ok': 7, 'partial': 10})
- em_hot: 20261109, 20261110, 20261112 ({'context_only': 16})
- em_kline_f61: 20261029, 20261030, 20261112 ({'ok': 7, 'partial': 10})
- exchange: 20261109, 20261110, 20261112 ({'context_only': 16})
- ftshare: 20261109, 20261110, 20261112 ({'deprecated': 15, 'failed': 3})
- market_sources: 20261026 ({'ok': 17, 'partial': 1})
- news_wscn_cctv: 20261015 ({'ok': 17, 'partial': 1})
- push2: 20261029, 20261030, 20261112 ({'failed': 5, 'ok': 7, 'partial': 4})
- slist: 20261029, 20261030, 20261112 ({'failed': 9, 'ok': 7})
- sse_e_interaction: 20261016 ({'ok': 17, 'partial': 1})
- st_list: 20261028, 20261029, 20261030 ({'ok': 9, 'partial': 8})
- tdx: 20261104, 20261105 ({'ok': 16, 'partial': 2})
- ulist239: 20261029, 20261030, 20261112 ({'failed': 11, 'ok': 7})
- zhb: 20261109, 20261110, 20261112 ({'ok': 5, 'partial': 13})

## 低信息与日期语义专项队列

恒空、恒零或当前恒定字段不参与普通碰撞；状态表示当前样本没有区分力，新采样出现有效变化后重新纳入。日期形状只代表值可解析为日期，必须查清业务角色，不能拿字段值代替来源 `as_of_date`。
低信息未知路径 156 项，状态分布 `{'constant_zero': 32, 'all_missing_or_blank': 5, 'constant_value': 119}`。

### 等待新信息的字段

| 完整字段路径 | 状态 | 观测/非空/缺失或空白/不同值 | 样本日期数 | 示例值 |
|:--|:--|--:|--:|:--|
| `market_sources.request_params.offset` | constant_zero | 3/3/0/1 | 3 | `0` |
| `eltdx.adjust_mode_raw` | constant_zero | 18/18/0/1 | 18 | `0` |
| `eltdx.anchor_date_raw` | constant_zero | 18/18/0/1 | 18 | `0` |
| `eltdx.raw_payload` | all_missing_or_blank | 18/0/18/0 | 18 | `` |
| `eltdx.start` | constant_zero | 18/18/0/1 | 18 | `0` |
| `reports.emIndustryCode` | all_missing_or_blank | 19/0/19/0 | 13 | `` |
| `sina[34]` | constant_zero | 36/36/0/1 | 18 | `0.0000` |
| `sina[35]` | constant_zero | 36/36/0/1 | 18 | `0` |
| `event_dc.PREDICT_RAISE_FUNDS` | constant_zero | 115/115/0/1 | 16 | `0` |
| `ulist239.f120` | constant_zero | 140/140/0/1 | 7 | `0` |
| `ulist239.f125` | constant_zero | 140/140/0/1 | 7 | `0` |
| `ulist239.f126` | constant_zero | 140/140/0/1 | 7 | `0` |
| `ulist239.f137` | constant_zero | 140/140/0/1 | 7 | `0.0` |
| `ulist239.f138` | constant_zero | 140/140/0/1 | 7 | `0.0` |
| `ulist239.f194` | constant_zero | 140/140/0/1 | 7 | `0` |
| `ulist239.f216` | constant_zero | 140/140/0/1 | 7 | `0` |
| `ulist239.f223` | constant_zero | 140/140/0/1 | 7 | `0` |
| `push2.f123` | constant_zero | 194/194/0/1 | 11 | `0.0` |
| `push2.f124` | constant_zero | 194/194/0/1 | 11 | `0.0` |
| `push2.f125` | constant_zero | 194/194/0/1 | 11 | `0.0` |
| `push2.f134` | constant_zero | 194/194/0/1 | 11 | `0` |
| `event_dc.OPEN_CHANGERATE` | constant_zero | 317/317/0/1 | 16 | `0` |
| `event_dc.IS_1YEAR` | constant_zero | 320/320/0/1 | 16 | `0` |
| `event_dc.IS_1YEAR_APPLY` | constant_zero | 320/320/0/1 | 16 | `0` |
| `event_dc.IS_BALLOT_NUM` | constant_zero | 320/320/0/1 | 16 | `0` |
| `event_dc.IS_BEIJING` | constant_zero | 320/320/0/1 | 16 | `0` |
| `event_dc.IS_CALENDAR_DATA` | constant_zero | 320/320/0/1 | 16 | `0` |
| `event_dc.IS_PROFIT` | constant_zero | 320/320/0/1 | 16 | `0` |
| `event_dc.IS_REGISTRATION` | constant_zero | 320/320/0/1 | 16 | `0` |
| `event_dc.IS_REGISTRATION_NEW` | constant_zero | 320/320/0/1 | 16 | `0` |
| `event_dc.IS_UNOPEN` | constant_zero | 320/320/0/1 | 16 | `0` |
| `event_dc.PREDICT_ISSUE_PRICE` | constant_zero | 320/320/0/1 | 16 | `0` |
| `event_dc.PREDICT_ISSUE_PRICE2` | constant_zero | 320/320/0/1 | 16 | `0` |
| `tencent[29]` | all_missing_or_blank | 360/0/360/0 | 18 | `` |
| `tencent[55]` | all_missing_or_blank | 360/0/360/0 | 18 | `` |
| `kph.open_time` | constant_zero | 531/531/0/1 | 12 | `0` |
| `kpl.raw_columns.col_03` | all_missing_or_blank | 1096/0/1096/0 | 17 | `` |
| `market_sources.reason` | constant_value | 2/2/0/1 | 2 | `candidate_sample_already_exists_for_data_date` |
| `market_sources.request_params.days` | constant_value | 2/2/0/1 | 2 | `4` |
| `market_sources.request_params.fetch_all` | constant_value | 2/2/0/1 | 2 | `false` |
| `market_sources.request_params.zs_type` | constant_value | 2/2/0/1 | 2 | `7` |
| `market_sources.request_params.kline_type` | constant_value | 3/3/0/1 | 3 | `daily` |
| `market_sources.request_params.limit` | constant_value | 3/3/0/1 | 3 | `5` |
| `market_sources.request_params.stock_code` | constant_value | 6/6/0/1 | 6 | `000007` |
| `market_sources.stock_code` | constant_value | 6/6/0/1 | 6 | `000007` |
| `eltdx.limit_ladder.limit_status` | constant_value | 13/13/0/1 | 10 | `sealed` |
| `eltdx.adjust_mode` | constant_value | 18/18/0/1 | 18 | `none` |
| `eltdx.category` | constant_value | 18/18/0/1 | 18 | `沪深A股` |
| `eltdx.code` | constant_value | 18/18/0/1 | 18 | `880005` |
| `eltdx.exchange` | constant_value | 18/18/0/1 | 18 | `sh` |

_显示前 50 / 共 156 项；完整清单在 JSON。_

日期值候选 17 项；应先查官方定义和完整路径，再确定上市日、记录更新日、报告期、公告/事件日、生效日或来源数据日。

### 日期形状字段待核业务含义

| 完整字段路径 | 日期样本比例 | 编码 | 样本键日期数 | 日期值/来源日/样本日/股票样例 |
|:--|--:|:--|--:|:--|
| `etf.date` | 100.0% | YYYY-MM-DD | 17 | 2026-10-15(来源日=20261015;样本日=T:20261015;股票=158000), 2026-10-15(来源日=20261015;样本日=T:20261015;股票=158001), 2026-10-15(来源日=20261015;样本日=T:20261015;股票=158003), 2026-10-15(来源日=20261015;样本日=T:20261015;股票=158005), 2026-10-15(来源日=20261015;样本日=T:20261015;股票=158006) |
| `etf.listing_date` | 100.0% | YYYY-MM-DD | 17 | 2026-08-26(来源日=20261015;样本日=T:20261015;股票=158000), 2026-08-27(来源日=20261015;样本日=T:20261015;股票=158001), 2026-08-19(来源日=20261015;样本日=T:20261015;股票=158003), 2026-08-24(来源日=20261015;样本日=T:20261015;股票=158005), 2026-08-07(来源日=20261015;样本日=T:20261015;股票=158006) |
| `research_sina.date` | 100.0% | YYYY-MM-DD | 24 | 2026-10-16(来源日=20261016;样本日=C:20261016;股票=__0), 2026-10-16(来源日=20261016;样本日=C:20261016;股票=__1), 2026-10-16(来源日=20261016;样本日=C:20261016;股票=__10), 2026-10-16(来源日=20261016;样本日=C:20261016;股票=__11), 2026-10-16(来源日=20261016;样本日=C:20261016;股票=__12) |
| `sina_extended.opendate` | 100.0% | YYYY-MM-DD | 16 | 2026-10-19(来源日=20261019;样本日=T:20261019;股票=000007), 2026-10-19(来源日=20261019;样本日=T:20261019;股票=000011), 2026-10-19(来源日=20261019;样本日=T:20261019;股票=000037), 2026-10-19(来源日=20261019;样本日=T:20261019;股票=000568), 2026-10-19(来源日=20261019;样本日=T:20261019;股票=000678) |
| `zhb.full.date` | 100.0% | YYYYMMDD | 11 | 2026-10-16(来源日=20261016;样本日=T:20261016;股票=000007), 2026-10-16(来源日=20261016;样本日=T:20261016;股票=000011), 2026-10-16(来源日=20261016;样本日=T:20261016;股票=000037), 2026-10-16(来源日=20261016;样本日=T:20261016;股票=000568), 2026-10-16(来源日=20261016;样本日=T:20261016;股票=000678) |
| `zhb.tipinfo.unlock_date` | 100.0% | YYYYMMDD | 11 | 2024-11-21(来源日=20261016;样本日=T:20261016;股票=000007), 2020-04-30(来源日=20261016;样本日=T:20261016;股票=000011), 2009-05-27(来源日=20261016;样本日=T:20261016;股票=000037), 2026-09-28(来源日=20261016;样本日=T:20261016;股票=000568), 2019-07-25(来源日=20261016;样本日=T:20261016;股票=000678) |
| `news_wscn_cctv.date` | 100.0% | YYYY-MM-DD | 16 | 2026-10-15(来源日=20261015;样本日=C:20261015;股票=__0), 2026-10-15(来源日=20261015;样本日=C:20261015;股票=__1), 2026-10-15(来源日=20261015;样本日=C:20261015;股票=__10), 2026-10-15(来源日=20261015;样本日=C:20261015;股票=__11), 2026-10-15(来源日=20261015;样本日=C:20261015;股票=__12) |
| `zhb.tipinfo.dt_date_recent` | 100.0% | YYYYMMDD | 11 | 2026-05-12(来源日=20261016;样本日=T:20261016;股票=000007), 2025-04-07(来源日=20261016;样本日=T:20261016;股票=000011), 2026-07-24(来源日=20261016;样本日=T:20261016;股票=000037), 2024-10-09(来源日=20261016;样本日=T:20261016;股票=000568), 2026-10-12(来源日=20261016;样本日=T:20261016;股票=000678) |
| `ulist239.f297` | 100.0% | YYYYMMDD | 4 | 2026-11-05(来源日=20261105;样本日=T:20261105;股票=000007), 2026-11-05(来源日=20261105;样本日=T:20261105;股票=000011), 2026-11-05(来源日=20261105;样本日=T:20261105;股票=000037), 2026-11-05(来源日=20261105;样本日=T:20261105;股票=000568), 2026-11-05(来源日=20261105;样本日=T:20261105;股票=000678) |
| `zhb.full.unseal_date` | 100.0% | YYYYMMDD | 11 | 2019-07-15(来源日=20261016;样本日=T:20261016;股票=300788), 2021-12-24(来源日=20261016;样本日=T:20261016;股票=301190), 2022-05-27(来源日=20261016;样本日=T:20261016;股票=688327), 2021-10-26(来源日=20261016;样本日=T:20261016;股票=688553), 2020-07-22(来源日=20261016;样本日=T:20261016;股票=688589) |
| `eltdx.trade_date` | 100.0% | YYYY-MM-DD | 18 | 2026-10-15(来源日=20261015;样本日=T:20261015;股票=limit_ladder), 2026-10-15(来源日=20261015;样本日=T:20261015;股票=stock_theme_strength_rank), 2026-10-15(来源日=20261015;样本日=T:20261015;股票=theme_strength_rank), 2026-10-16(来源日=20261016;样本日=T:20261016;股票=limit_ladder), 2026-10-16(来源日=20261016;样本日=T:20261016;股票=stock_theme_strength_rank) |
| `market_sources.data_date` | 100.0% | YYYY-MM-DD | 18 | 2026-10-15(来源日=20261015;样本日=T:20261015;股票=levistock_daily_candidate), 2026-10-16(来源日=20261016;样本日=T:20261016;股票=levistock_daily_candidate), 2026-10-19(来源日=20261019;样本日=T:20261019;股票=000007), 2026-10-20(来源日=20261020;样本日=T:20261020;股票=000007), 2026-10-21(来源日=20261021;样本日=T:20261021;股票=levistock_daily_candidate) |
| `market_sources.requested_trade_date` | 100.0% | YYYY-MM-DD | 18 | 2026-10-15(来源日=20261015;样本日=T:20261015;股票=kph_limit_ladder), 2026-10-16(来源日=20261016;样本日=T:20261016;股票=kph_limit_ladder), 2026-10-19(来源日=20261019;样本日=T:20261019;股票=kph_limit_ladder), 2026-10-20(来源日=20261020;样本日=T:20261020;股票=kph_limit_ladder), 2026-10-21(来源日=20261021;样本日=T:20261021;股票=kph_limit_ladder) |
| `eltdx.limit_ladder.previous_trade_date` | 100.0% | YYYY-MM-DD | 10 | 2026-10-15(来源日=20261016;样本日=T:20261016;股票=000678), 2026-10-15(来源日=20261016;样本日=T:20261016;股票=600825), 2026-10-19(来源日=20261020;样本日=T:20261020;股票=002242), 2026-10-20(来源日=20261021;样本日=T:20261021;股票=002242), 2026-10-22(来源日=20261023;样本日=T:20261023;股票=000678) |
| `eltdx.limit_ladder.stats_date` | 100.0% | YYYY-MM-DD | 10 | 2026-10-16(来源日=20261016;样本日=T:20261016;股票=000678), 2026-10-16(来源日=20261016;样本日=T:20261016;股票=600825), 2026-10-19(来源日=20261020;样本日=T:20261020;股票=002242), 2026-10-21(来源日=20261021;样本日=T:20261021;股票=002242), 2026-10-22(来源日=20261023;样本日=T:20261023;股票=000678) |
| `eltdx.limit_ladder.target_trade_date` | 100.0% | YYYY-MM-DD | 10 | 2026-10-16(来源日=20261016;样本日=T:20261016;股票=000678), 2026-10-16(来源日=20261016;样本日=T:20261016;股票=600825), 2026-10-20(来源日=20261020;样本日=T:20261020;股票=002242), 2026-10-21(来源日=20261021;样本日=T:20261021;股票=002242), 2026-10-23(来源日=20261023;样本日=T:20261023;股票=000678) |
| `market_sources.request_params.date` | 100.0% | YYYY-MM-DD | 4 | 2026-10-15(来源日=20261015;样本日=T:20261015;股票=levistock_daily_candidate), 2026-10-23(来源日=20261023;样本日=T:20261023;股票=levistock_daily_candidate), 2026-10-28(来源日=20261028;样本日=T:20261028;股票=levistock_daily_candidate), 2026-11-04(来源日=20261104;样本日=T:20261104;股票=levistock_daily_candidate) |

## 候选身份与人工审阅状态

- 候选身份：生成 3570 条，唯一候选 3570 个，重复身份 0，无效身份 0。
- 审阅台账：可用；当前状态 `pending`；已审 0，待处理 3570，覆盖率 0.0%。
- 重复归并组：0；每个成员均保留到代表候选的反向追溯。
- 处置计数：`accepted_for_adjudication` 0；`duplicate_grouped` 0；`insufficient_evidence` 0；`needs_external_evidence` 0；`rejected` 0；`unreviewed` 3570。
- `accepted_for_adjudication` 只表示可进入现有证据裁决流程；审阅台账不会修改主字典或字段注册表。

## 报告完整性与审阅范围

- 机器可读完整性：`complete`；方法候选生成 3517 条，完整明细保存 3517 条，缺失 0 条，多余 0 条，重复 0 条，身份无效 0 条。
- 全量方法候选位于同名 JSON 的 `method_candidate_inventory`；Markdown 的 Top-N 表格是导航摘要，不能代替全量 JSON 审阅。
- 候选审阅数据对账：`complete`；唯一候选 3570 个，审阅 0 个，待处理 3570 个；人工审阅进度与机器清单完整性分别统计。
- Markdown 未逐行展示、但 JSON 保留的部分：
  - `method_candidates`：展示 100 / 500，摘要省略 400 条。
  - `method_candidate_inventory`：展示 0 / 3517，摘要省略 3517 条。
  - `candidate_triage.targets`：展示 50 / 206，摘要省略 156 条。
  - `candidate_triage.low_information_fields`：展示 50 / 156，摘要省略 106 条。
  - `diagnostics`：展示 100 / 330，摘要省略 230 条。
- 完整性对账通过；逐目标复核仍须覆盖 JSON 的全部明细，并为每项记录已检查、重复归并、证据不足或需外部核验的处置。
