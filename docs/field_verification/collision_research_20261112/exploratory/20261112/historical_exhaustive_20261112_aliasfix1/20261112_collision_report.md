# 全源对撞报告（20261112）

> 交易数据窗口配置：全部历史日期（`--all`）
> 行情窗口：20261015 ~ 20261110（18 个不同交易日）｜字段 1309 个｜样本值 1288945 条
> 新闻/公告自然日窗口：20261015 ~ 20261112
> 主攻目标（unverified）=231｜可审定新候选=21｜首次发现新候选对=3｜已登记关系复验=0｜异号同义 21 / 同号镜像 0

> **规则**：L1 每日需≥18 组有效配对，并至少有5 组信息配对；双方同时为 0 或同时缺失不计命中率，一侧为 0、另一侧非 0 按失配计。信息配对命中率≥90%，且覆盖至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。JSON `daily_sample_counts` 与 `daily_informative_sample_counts`分别保留每日有效配对数和 L1 信息配对数。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 新候选 — 异号同义（跨编号，高价值）(21)

| 左字段(unverified) | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|
| `zhb.full.change_pct` | `tencent[32]` | L1 | 100.00% | 11 | 220 | 218 | - |  | — |
| `zhb.full.amount` | `fuyao.snapshot.turnover` | L1-U | 100.00% | 11 | 220 | — | 10000 |  | — |
| `zhb.full.low_52w` | `tencent[68]` | L1 | 100.00% | 11 | 220 | 220 | - |  | — |
| `zhb.full.pe_ttm` | `ulist239.f115` | L1 | 100.00% | 5 | 100 | 100 | - |  | — |
| `zhb.full.change_pct` | `push2.f170` | L1 | 100.00% | 5 | 100 | 100 | - |  | — |
| `zhb.full.change_pct` | `ulist239.f3` | L1 | 100.00% | 5 | 100 | 100 | - |  | — |
| `zhb.full.change_20d` | `ulist239.f110` | L1 | 100.00% | 5 | 100 | 100 | - |  | — |
| `zhb.full.change_30d` | `ulist239.f110` | L1 | 100.00% | 5 | 100 | 100 | - |  | — |
| `zhb.full.change_60d` | `push2.f121` | L1 | 100.00% | 5 | 100 | 100 | - |  | — |
| `zhb.full.change_5d` | `ulist239.f109` | L1 | 100.00% | 5 | 100 | 99 | - |  | — |
| `zhb.full.change_10d` | `ulist239.f160` | L1 | 100.00% | 5 | 100 | 100 | - |  | — |
| `zhb.full.amount` | `push2.f48` | L1-U | 100.00% | 5 | 100 | — | 10000 |  | — |
| `zhb.full.amount` | `ulist239.f6` | L1-U | 100.00% | 5 | 100 | — | 10000 |  | — |
| `zhb.full.change_5d` | `tencent[63]` | L1 | 98.62% | 11 | 220 | 218 | - |  | — |
| `zhb.full.change_20d` | `tencent[70]` | L1 | 97.73% | 11 | 220 | 220 | - |  | — |
| `zhb.full.change_30d` | `tencent[70]` | L1 | 97.73% | 11 | 220 | 220 | - |  | — |
| `zhb.full.change_10d` | `tencent[69]` | L1 | 97.73% | 11 | 220 | 220 | - |  | — |
| `zhb.full.pe_ttm` | `tencent[39]` | L1 | 95.00% | 11 | 220 | 220 | - |  | — |
| `zhb.full.high_52w` | `tencent[67]` | L1 | 95.00% | 11 | 220 | 220 | - |  | — |
| `zhb.full.change_60d` | `tencent[71]` | L1 | 92.27% | 11 | 220 | 220 | - |  | — |
| `zhb.full.change_ytd` | `push2.f122` | L1 | 90.00% | 5 | 100 | 100 | - |  | — |

## 二、L1 / L1-U 新候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、已登记映射的本窗口复验（0）

_这些关系已在主注册表登记，只用于观察当前样本是否仍支持既有映射；它们不是新的未知字段候选，也不能再次提交为新定案。_

_本轮没有已登记关系进入复验窗口。_


## 四、L4 存疑候选（53）

| 左字段 | 右字段 | 命中率 | 天数 | 样本 |
|:--|:--|--:|--:|--:|
| `zhb.full.pe_ttm` | `push2.f164` | 100.00% | 5 | 100 |
| `zhb.full.change_20d` | `push2.f120` | 100.00% | 5 | 100 |
| `zhb.full.change_30d` | `push2.f120` | 100.00% | 5 | 100 |
| `zhb.full.change_60d` | `ulist239.f24` | 100.00% | 5 | 100 |
| `zhb.full.change_5d` | `push2.f119` | 100.00% | 5 | 100 |
| `zhb.full.low_52w` | `push2.f175` | 96.00% | 5 | 100 |
| `sina[32]` | `ulist239.f190` | 95.00% | 7 | 140 |
| `sina[32]` | `ulist239.f231` | 95.00% | 7 | 140 |
| `ulist239.f190` | `tdx.finance_info.hgu` | 94.93% | 7 | 138 |
| `sina[32]` | `tdx.finance_info.hgu` | 94.67% | 17 | 338 |
| `push2ex.zt_continuous` | `kph.limit_count` | 93.00% | 11 | 457 |
| `sina[32]` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 91.76% | 17 | 340 |
| `kph.industry_limit_up_count` | `kpl.raw_columns.col_20` | 90.00% | 11 | 500 |
| `sina[32]` | `ulist239.f200` | 90.00% | 7 | 140 |
| `sina[32]` | `zhb.full.other_qy_jzc` | 90.00% | 11 | 220 |
| `sina[32]` | `zhb.stat.other_qy_jzc` | 90.00% | 11 | 220 |
| `ulist239.f190` | `zhb.full.other_qy_jzc` | 90.00% | 5 | 100 |
| `ulist239.f190` | `zhb.stat.other_qy_jzc` | 90.00% | 5 | 100 |
| `zhb.full.change_ytd` | `ulist239.f25` | 90.00% | 5 | 100 |
| `sina[32]` | `tdx.finance_info.bgu` | 89.64% | 17 | 338 |
| `ulist239.f190` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 87.14% | 7 | 140 |
| `push2ex.zt_days` | `kph.limit_count` | 86.65% | 11 | 457 |
| `push2ex.zt_days` | `kpl.raw_columns.col_15` | 86.61% | 16 | 1016 |
| `push2ex.zt_continuous` | `kpl.raw_columns.col_15` | 86.61% | 16 | 1016 |
| `zhb.full.high_52w` | `push2.f174` | 86.51% | 7 | 126 |
| `ulist239.f190` | `tdx.finance_info.bgu` | 84.78% | 7 | 138 |
| `zhb.full.dividend_yield` | `tencent[64]` | 75.91% | 11 | 220 |
| `tencent[7]` | `ulist239.f34` | 75.00% | 7 | 140 |
| `tencent[8]` | `ulist239.f35` | 75.00% | 7 | 140 |
| `push2.f49` | `tencent[7]` | 74.74% | 11 | 194 |
| `push2.f161` | `tencent[8]` | 74.74% | 11 | 194 |
| `zhb.full.change_ytd` | `tencent[62]` | 71.82% | 11 | 220 |
| `kpl.raw_columns.col_16` | `push2ex.broken_count` | 70.77% | 16 | 1016 |
| `ulist239.f11` | `tencent[80]` | 70.00% | 7 | 140 |
| `zhb.full.dividend_yield` | `ulist239.f133` | 70.00% | 5 | 100 |
| `zhb.full.change_250k_bar` | `tencent[79]` | 67.73% | 11 | 220 |
| `sina[32]` | `ulist239.f13` | 60.00% | 7 | 140 |
| `sina[32]` | `ulist239.f27` | 60.00% | 7 | 140 |
| `sina[32]` | `ulist239.f97` | 58.57% | 7 | 140 |
| `sina[32]` | `push2.f107` | 57.22% | 11 | 194 |
| `sina[32]` | `push2.f110` | 57.22% | 11 | 194 |
| `ulist239.f97` | `zhb.full.other_qy_jzc` | 57.00% | 5 | 100 |
| `ulist239.f97` | `zhb.stat.other_qy_jzc` | 57.00% | 5 | 100 |
| `ulist239.f97` | `tdx.finance_info.hgu` | 55.80% | 7 | 138 |
| `ulist239.f97` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 53.57% | 7 | 140 |
| `ulist239.f97` | `tdx.finance_info.bgu` | 50.72% | 7 | 138 |
| `sina[32]` | `ulist239.f147` | 49.29% | 7 | 140 |
| `kpl.raw_columns.col_02` | `kph.limit_count` | 46.00% | 11 | 500 |
| `kpl.raw_columns.col_16` | `kph.limit_count` | 45.40% | 11 | 500 |
| `kpl.raw_columns.col_02` | `push2ex.limit_count` | 43.60% | 16 | 1016 |
| `kpl.raw_columns.col_16` | `push2ex.limit_count` | 41.93% | 16 | 1016 |
| `kpl.raw_columns.col_02` | `push2ex.zt_days` | 40.16% | 16 | 1016 |
| `kpl.raw_columns.col_02` | `push2ex.zt_continuous` | 40.16% | 16 | 1016 |

## 五、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 六、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `zhb.full.pe_ttm` | `fuyao.valuation.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | fuyao, zhb | Pearson=0.9985, Spearman=0.9994, LOO稳号=True |
| `zhb.full.pe_ttm` | `ftshare_rest.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 135 | T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103 | ftshare_rest, zhb | Pearson=0.9895, Spearman=0.9967, LOO稳号=True |
| `kph.industry_limit_up_count` | `kpl.raw_columns.col_20` | robust_correlation, affine_formula, per_stock_time_series | 500 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028, T:20261030 | kph, kpl | Pearson=0.993, Spearman=0.9895, LOO稳号=True |
| `push2ex.turnover_rate` | `kph.turnover_rate` | robust_correlation, per_stock_time_series, semantic_label | 457 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028, T:20261030 | kph, push2ex | Pearson=0.8466, Spearman=0.8897, LOO稳号=True |
| `tencent[22]` | `sina[22]` | robust_correlation, affine_formula, per_stock_time_series | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[28]` | `tencent[28]` | robust_correlation, affine_formula, per_stock_time_series | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[26]` | `tencent[26]` | robust_correlation, affine_formula, per_stock_time_series | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[24]` | `tencent[24]` | robust_correlation, affine_formula, per_stock_time_series | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[18]` | `tencent[18]` | robust_correlation, affine_formula, per_stock_time_series | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[16]` | `tencent[16]` | robust_correlation, affine_formula, per_stock_time_series | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[14]` | `tencent[14]` | robust_correlation, affine_formula, per_stock_time_series | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.pe_ttm` | `tencent[39]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=0.9985, Spearman=0.9994, LOO稳号=True |
| `zhb.full.low_52w` | `tencent[68]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.low_52w` | `tencent[67]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=0.9994, Spearman=0.9182, LOO稳号=True |
| `zhb.full.high_52w` | `tencent[68]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=0.9994, Spearman=0.9182, LOO稳号=True |
| `zhb.full.high_52w` | `tencent[67]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_ytd` | `tencent[75]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=0.9845, Spearman=0.9699, LOO稳号=True |
| `zhb.full.change_ytd` | `tencent[62]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_pct` | `tencent[32]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_pct` | `fuyao.snapshot.price_change_ratio_pct` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | fuyao, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_60d` | `tencent[71]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_5d` | `tencent[63]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_30d` | `tencent[70]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_250k_bar` | `tencent[79]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_20d` | `tencent[70]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_10d` | `tencent[69]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.amount` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.amount` | `tencent[37]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.amount` | `sina[9]` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | sina, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.amount` | `fuyao.snapshot.turnover` | robust_correlation, affine_formula, per_stock_time_series | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | fuyao, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
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
| `tdx.finance_info.eps` | `push2.f92` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9865, Spearman=0.9308, LOO稳号=True |
| `tdx.finance_info.eps` | `push2.f55` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9999, Spearman=0.9991, LOO稳号=True |
| `tdx.finance_info.eps` | `push2.f190` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.985, Spearman=0.8829, LOO稳号=True |
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
| `push2.f135` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tencent | Pearson=0.982, Spearman=0.9908, LOO稳号=True |
| `push2.f135` | `tencent[37]` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tencent | Pearson=0.982, Spearman=0.9908, LOO稳号=True |
| `push2.f135` | `sina[9]` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, sina | Pearson=0.982, Spearman=0.9908, LOO稳号=True |
| `push2.f135` | `ftshare_rest.turnover` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | ftshare_rest, push2 | Pearson=0.982, Spearman=0.9908, LOO稳号=True |
| `push2.f135` | `eltdx.quote_snapshot.amount` | robust_correlation, affine_formula, per_stock_time_series | 192 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | eltdx, push2 | Pearson=0.982, Spearman=0.9908, LOO稳号=True |
| `push2.f135` | `tdx.quote_raw.amount` | robust_correlation, affine_formula, per_stock_time_series | 190 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9823, Spearman=0.9907, LOO稳号=True |
| `push2.f135` | `tdx.quote_full.amount_wan` | robust_correlation, affine_formula, per_stock_time_series | 190 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9823, Spearman=0.9907, LOO稳号=True |
| `push2.f136` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 188 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tencent | Pearson=0.9835, Spearman=0.9915, LOO稳号=True |
| `push2.f136` | `tencent[37]` | robust_correlation, affine_formula, per_stock_time_series | 188 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tencent | Pearson=0.9835, Spearman=0.9915, LOO稳号=True |
| `push2.f136` | `sina[9]` | robust_correlation, affine_formula, per_stock_time_series | 188 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, sina | Pearson=0.9835, Spearman=0.9915, LOO稳号=True |
| `push2.f136` | `ftshare_rest.turnover` | robust_correlation, affine_formula, per_stock_time_series | 188 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | ftshare_rest, push2 | Pearson=0.9835, Spearman=0.9915, LOO稳号=True |
| `push2.f136` | `eltdx.quote_snapshot.amount` | robust_correlation, affine_formula, per_stock_time_series | 188 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | eltdx, push2 | Pearson=0.9835, Spearman=0.9915, LOO稳号=True |
| `push2.f136` | `tdx.quote_raw.amount` | robust_correlation, affine_formula, per_stock_time_series | 186 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9838, Spearman=0.9914, LOO稳号=True |
| `push2.f136` | `tdx.quote_full.amount_wan` | robust_correlation, affine_formula, per_stock_time_series | 186 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tdx | Pearson=0.9838, Spearman=0.9914, LOO稳号=True |
| `zhb.full.change_ytd` | `ftshare_rest.change_rate_ytd` | robust_correlation, per_stock_time_series, semantic_label | 180 | T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103 | ftshare_rest, zhb | Pearson=0.9428, Spearman=0.9554, LOO稳号=True |
| `zhb.full.change_pct` | `ftshare_rest.change_rate` | robust_correlation, affine_formula, per_stock_time_series | 180 | T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103 | ftshare_rest, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.amount` | `ftshare_rest.turnover` | robust_correlation, affine_formula, per_stock_time_series | 180 | T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103 | ftshare_rest, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `push2.f49` | `fuyao.snapshot.volume` | robust_correlation, affine_formula, per_stock_time_series | 180 | T:20261020, T:20261023, T:20261029, T:20261102, T:20261103, T:20261104 | fuyao, push2 | Pearson=0.9956, Spearman=0.9949, LOO稳号=True |
| `push2.f161` | `fuyao.snapshot.volume` | robust_correlation, affine_formula, per_stock_time_series | 180 | T:20261020, T:20261023, T:20261029, T:20261102, T:20261103, T:20261104 | fuyao, push2 | Pearson=0.9958, Spearman=0.9944, LOO稳号=True |
| `push2.f135` | `fuyao.snapshot.turnover` | robust_correlation, affine_formula, per_stock_time_series | 178 | T:20261020, T:20261023, T:20261029, T:20261102, T:20261103, T:20261104 | fuyao, push2 | Pearson=0.9815, Spearman=0.9905, LOO稳号=True |
| `push2.f136` | `fuyao.snapshot.turnover` | robust_correlation, affine_formula, per_stock_time_series | 174 | T:20261020, T:20261023, T:20261029, T:20261102, T:20261103, T:20261104 | fuyao, push2 | Pearson=0.9836, Spearman=0.9913, LOO稳号=True |
| `em_fund_flow.f135` | `tdx.quote_raw.amount` | robust_correlation, affine_formula, per_stock_time_series | 149 | T:20261019, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | em_fund_flow, tdx | Pearson=0.9802, Spearman=0.9894, LOO稳号=True |
| `em_fund_flow.f135` | `tdx.quote_full.amount_wan` | robust_correlation, affine_formula, per_stock_time_series | 149 | T:20261019, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | em_fund_flow, tdx | Pearson=0.9802, Spearman=0.9894, LOO稳号=True |
| `em_fund_flow.f136` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 147 | T:20261019, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | em_fund_flow, tencent | Pearson=0.982, Spearman=0.9907, LOO稳号=True |
| `em_fund_flow.f136` | `tencent[37]` | robust_correlation, affine_formula, per_stock_time_series | 147 | T:20261019, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | em_fund_flow, tencent | Pearson=0.982, Spearman=0.9907, LOO稳号=True |
| `em_fund_flow.f136` | `sina[9]` | robust_correlation, affine_formula, per_stock_time_series | 147 | T:20261019, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | em_fund_flow, sina | Pearson=0.982, Spearman=0.9907, LOO稳号=True |
| `em_fund_flow.f136` | `fuyao.snapshot.turnover` | robust_correlation, affine_formula, per_stock_time_series | 147 | T:20261019, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | em_fund_flow, fuyao | Pearson=0.982, Spearman=0.9907, LOO稳号=True |
| `em_fund_flow.f136` | `eltdx.quote_snapshot.amount` | robust_correlation, affine_formula, per_stock_time_series | 147 | T:20261019, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | eltdx, em_fund_flow | Pearson=0.982, Spearman=0.9907, LOO稳号=True |
| `em_fund_flow.f136` | `tdx.quote_raw.amount` | robust_correlation, affine_formula, per_stock_time_series | 145 | T:20261019, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | em_fund_flow, tdx | Pearson=0.9823, Spearman=0.9905, LOO稳号=True |
| `em_fund_flow.f136` | `tdx.quote_full.amount_wan` | robust_correlation, affine_formula, per_stock_time_series | 145 | T:20261019, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | em_fund_flow, tdx | Pearson=0.9823, Spearman=0.9905, LOO稳号=True |
| `ulist239.f11` | `tencent[80]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | tencent, ulist239 | Pearson=0.987, Spearman=0.9721, LOO稳号=True |
| `em_fund_flow.f136` | `ftshare_rest.turnover` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | em_fund_flow, ftshare_rest | Pearson=0.9819, Spearman=0.9912, LOO稳号=True |
| `zhb.full.pe_ttm` | `push2.f164` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.low_52w` | `push2.f175` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `zhb.full.high_52w` | `push2.f175` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=0.9994, Spearman=0.9228, LOO稳号=True |
| `zhb.full.high_52w` | `push2.f174` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=1.0, Spearman=0.9997, LOO稳号=True |
| `zhb.full.change_ytd` | `push2.f122` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_pct` | `push2.f170` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_60d` | `push2.f121` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_5d` | `push2.f119` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_30d` | `push2.f120` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.change_20d` | `push2.f120` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.amount` | `push2.f48` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `zhb.full.amount` | `push2.f145` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=0.9871, Spearman=0.9958, LOO稳号=True |
| `zhb.full.amount` | `push2.f144` | robust_correlation, affine_formula, per_stock_time_series | 126 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104, T:20261106 | push2, zhb | Pearson=0.9866, Spearman=0.9933, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 七、日期与数据质量告警（305）

- 20261017: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261018: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261031: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261101: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261107: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
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
- 20261021/tdx_f10_more: 没有可用记录，快照跳过
- 另有 205 条告警，详见同名 JSON 报告。

---

> 数据来源：通达信 / 项目字段对撞体系。以上为方法论梳理，不构成投资建议。

## 来源身份状态（不参与字段语义定案）

_FTShare 公共 REST 接口已进入日常采集；官方字段契约作为语义锚，底层数据提供方仍未确认。与其匹配的强候选列在 L1-C，不混入独立来源 L1。_
_旧私有托管 MCP 采集器已退役，历史样本仅供 `--all` / `--exploratory` 追溯。_

## 官方契约锚候选 L1-C（1）

_L1-C 使用逐字段审定的官方接口契约语义作锚，并满足多日数值匹配门槛；仅当该接口底层数据来源独立性未确认时才列入此处，不属于独立来源 L1，也不自动定案。_

| 左字段（待确认） | 官方契约字段 | 等级 | 命中率 | 交易日数 | 样本 | 信息样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|
| `zhb.full.amount` | `ftshare_rest.turnover` | L1-C | 100.00% | 9 | 180 | — | 10000 |  | — |

## 字段时效与来源日期证据

_字段语义关系和来源日期可信度分开记录。`source_dates_confirmed` 表示两侧入选样本都有来源或记录级日期；`semantic_only_date_unconfirmed` 只支持缓变/静态字段的语义关系，不证明数据新鲜度或具体有效日期；`cross_source_dates_inferred` 表示日期通过独立、已确认日期的来源对同股同日精确值交叉推断，并不代表目标源自身提供了日期。未分类字段按来源日期严格门控。_

策略状态：`ok`；逐源分类字段 75，保守默认未分类字段 1234。L1/L1-C 日期证据：来源日期已确认 22 条，跨源值见证推断 0 条，仅语义证据且日期未确认 0 条，其他日期未确认 0 条。

| 日期见证关系 | 结果 | 交易日 | 精确样本 | 非零精确样本 | 不同非零值 | 证据 SHA-256 |
|:--|:--|--:|--:|--:|--:|:--|
| `tdx.quote_raw.ask1_vol <- tencent[20]` | thresholds_met | 16 | 318/318 | 305/305 | 216 | `9f488224d9a95673bf751451c47a3fd1ae05090b51cf090dc014d66818252d69` |
| `tdx.quote_raw.bid1_vol <- tencent[10]` | thresholds_met | 16 | 318/318 | 315/315 | 216 | `9f488224d9a95673bf751451c47a3fd1ae05090b51cf090dc014d66818252d69` |

_本轮 L1/L1-C 没有仅凭静态或缓变字段、且来源日期未确认的关系。_

## 来源字段覆盖与碰撞参与

_窗口字段值样本是经日期筛选、重复折叠和快照择优后载入的非空值；右侧比较次数另受字段类型及来源规则筛选。官方契约字段须有逐字段审定证据，契约语义本身不证明底层数据来源独立。_

| 来源 | 已确认字段 | 契约已确认 | 契约锚 | 独立锚 | L1-C 锚 | 窗口字段 / 字段值样本 / 交易日 |
|:--|--:|--:|--:|--:|--:|--:|
| axdata | 34 | 0 | 0 | 0 | 0 | 34 / 8512 / 16 |
| clist | 20 | 0 | 0 | 20 | 0 | 33 / 50169 / 7 |
| cls | 4 | 0 | 0 | 4 | 0 | 5 / 4000 / 0 |
| cninfo | 6 | 0 | 0 | 6 | 0 | 0 / 0 / 0 |
| datacenter | 42 | 1 | 1 | 42 | 0 | 0 / 0 / 0 |
| eltdx | 208 | 136 | 136 | 208 | 0 | 116 / 18670 / 17 |
| em_fund_flow | 0 | 0 | 0 | 0 | 0 | 15 / 2295 / 8 |
| em_hot | 39 | 0 | 0 | 39 | 0 | 0 / 0 / 0 |
| em_kline_f61 | 11 | 1 | 1 | 11 | 0 | 2 / 280 / 7 |
| etf | 0 | 0 | 0 | 0 | 0 | 9 / 186796 / 16 |
| event_dc | 0 | 0 | 0 | 0 | 0 | 148 / 462933 / 15 |
| exchange | 4 | 0 | 0 | 4 | 0 | 0 / 0 / 0 |
| ftshare | 6 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| ftshare_rest | 31 | 31 | 31 | 0 | 31 | 32 / 8890 / 14 |
| fuyao | 91 | 77 | 77 | 91 | 0 | 20 / 6020 / 16 |
| kph | 12 | 0 | 0 | 12 | 0 | 15 / 7965 / 12 |
| kpl | 11 | 0 | 0 | 11 | 0 | 28 / 36276 / 17 |
| market_sources | 14 | 0 | 0 | 0 | 0 | 74 / 133283 / 17 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 2 / 386 / 0 |
| push2 | 51 | 0 | 0 | 51 | 0 | 114 / 22116 / 11 |
| push2ex | 24 | 0 | 0 | 24 | 0 | 16 / 24240 / 16 |
| reports | 32 | 0 | 0 | 32 | 0 | 49 / 882 / 0 |
| research_sina | 0 | 0 | 0 | 0 | 0 | 6 / 5718 / 0 |
| sina | 27 | 0 | 0 | 27 | 0 | 39 / 11730 / 17 |
| sina_extended | 3 | 3 | 3 | 3 | 0 | 4 / 1200 / 15 |
| slist | 5 | 0 | 0 | 5 | 0 | 1 / 140 / 7 |
| sse_e_interaction | 0 | 0 | 0 | 0 | 0 | 8 / 1280 / 0 |
| st_list | 0 | 0 | 0 | 0 | 0 | 6 / 15854 / 8 |
| tdx | 224 | 103 | 103 | 224 | 0 | 63 / 21192 / 17 |
| tencent | 76 | 0 | 0 | 76 | 0 | 88 / 29886 / 17 |
| ulist239 | 52 | 0 | 0 | 52 | 0 | 240 / 33540 / 7 |
| zhb | 235 | 26 | 26 | 235 | 0 | 130 / 24235 / 11 |

| 来源 | 破解目标 | 比较字段 | 作目标比较 | 作右侧比较 | L1-C 锚比较 | L1 / L1-C / L4 关系 | 方法候选涉及 |
|:--|--:|--:|--:|--:|--:|--:|--:|
| axdata | 0 | 30 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| clist | 10 | 27 | 3785 | 1496 | 0 | 0 / 0 / 0 | 0 |
| cls | 2 | 2 | 767 | 10 | 0 | 0 / 0 / 0 | 0 |
| cninfo | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| datacenter | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| eltdx | 28 | 81 | 11950 | 4305 | 0 | 0 / 0 / 3 | 704 |
| em_fund_flow | 5 | 15 | 1960 | 1010 | 0 | 0 / 0 / 0 | 365 |
| em_hot | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| em_kline_f61 | 1 | 1 | 392 | 26 | 0 | 0 / 0 / 0 | 12 |
| etf | 4 | 4 | 29 | 0 | 0 | 0 / 0 / 0 | 0 |
| event_dc | 62 | 62 | 1258 | 0 | 0 | 0 / 0 / 0 | 201 |
| exchange | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare_rest | 1 | 26 | 23 | 4725 | 4725 | 0 / 1 / 0 | 450 |
| fuyao | 0 | 14 | 0 | 2016 | 0 | 1 / 0 / 0 | 198 |
| kph | 1 | 10 | 669 | 1201 | 0 | 0 / 0 / 5 | 33 |
| kpl | 10 | 21 | 5913 | 2678 | 0 | 0 / 0 / 10 | 437 |
| market_sources | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| push2 | 12 | 92 | 3128 | 7024 | 0 | 4 / 0 / 10 | 1111 |
| push2ex | 7 | 12 | 2674 | 692 | 0 | 0 / 0 / 9 | 390 |
| reports | 9 | 18 | 2346 | 861 | 0 | 0 / 0 / 0 | 0 |
| research_sina | 2 | 2 | 655 | 85 | 0 | 0 / 0 / 0 | 0 |
| sina | 8 | 34 | 4896 | 3726 | 0 | 0 / 0 / 14 | 598 |
| sina_extended | 0 | 3 | 0 | 405 | 0 | 0 / 0 / 0 | 34 |
| slist | 1 | 1 | 373 | 45 | 0 | 0 / 0 / 0 | 7 |
| sse_e_interaction | 1 | 1 | 23 | 0 | 0 | 0 / 0 / 0 | 0 |
| st_list | 3 | 3 | 48 | 0 | 0 | 0 / 0 / 0 | 0 |
| tdx | 2 | 58 | 850 | 5260 | 0 | 0 / 0 / 6 | 583 |
| tencent | 8 | 79 | 3974 | 9719 | 0 | 9 / 0 / 8 | 1336 |
| ulist239 | 20 | 172 | 6932 | 12627 | 0 | 7 / 0 / 23 | 933 |
| zhb | 34 | 100 | 13566 | 8300 | 0 | 21 / 1 / 18 | 2272 |

## AxData 每日接口核验

> 此处汇总采集目录已保存的本地证据，不发起网络请求、不改变注册表状态；AxData 是多源框架，不作为独立字段锚。

### AxData

窗口内有 18 个唯一数据日的轮验记录；重复目录合并 0 条。
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

被动逐字段比较中的差异计数（跨本窗口唯一数据日累加，不含原始值）：

| 比较路径 | 相同 | 不同 | 缺失/双方空值 |
|:--|--:|--:|--:|
| `axdata_shortline_vs_eltdx:alignment_status` | 0 | 240 | 0 |
| `axdata_shortline_vs_eltdx:beta_60d` | 0 | 240 | 0 |
| `axdata_shortline_vs_eltdx:code` | 0 | 240 | 0 |
| `axdata_shortline_vs_eltdx:full_code` | 0 | 240 | 0 |
| `axdata_shortline_vs_eltdx:instrument_id` | 0 | 240 | 0 |
| `axdata_shortline_vs_eltdx:limit_status` | 0 | 240 | 0 |
| `axdata_shortline_vs_eltdx:market_id` | 0 | 240 | 0 |
| `axdata_shortline_vs_eltdx:opening_rush` | 0 | 240 | 0 |
| `axdata_shortline_vs_eltdx:pe_ttm` | 0 | 240 | 0 |
| `axdata_shortline_vs_eltdx:previous_trade_date` | 0 | 240 | 0 |
| `axdata_shortline_vs_eltdx:symbol` | 0 | 240 | 0 |
| `axdata_shortline_vs_eltdx:target_trade_date` | 0 | 240 | 0 |
| `axdata_shortline_vs_eltdx:tdx_code` | 0 | 240 | 0 |
| `axdata_shortline_vs_eltdx:open_amount` | 47 | 193 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_hand` | 47 | 193 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_ratio` | 47 | 193 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_amount_ratio` | 59 | 181 | 0 |
| `axdata_shortline_vs_eltdx:auction_prev_volume_ratio` | 68 | 169 | 3 |
| `axdata_shortline_vs_eltdx:open_turnover_z` | 128 | 112 | 0 |
| `kph_limit_up_history_vs_kpl_detail:seal_amount` | 74 | 95 | 0 |
| `kph_limit_up_history_vs_kpl_detail:seal_money` | 74 | 95 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_seal_ratio` | 4 | 9 | 227 |
| `axdata_shortline_vs_eltdx:ladder_level` | 0 | 8 | 232 |
| `axdata_shortline_vs_eltdx:limit_board_text` | 20 | 7 | 213 |

### FTShare 退役来源历史记录（显式历史研究）

窗口内保留 3 个唯一数据日的旧元数据；重复目录合并 0 条。

| 数据日 | 历史状态 | 旧接口状态计数 |
|:--|:--|:--|
| 20261015 | ok | pending: 6 |
| 20261016 | ok | pending: 6 |
| 20261019 | ok | pending: 6 |

## 字母字段名语义提示（仅候选）

窗口内观察到 136 条需审阅的字母字段路径：含词义线索 35 条，仅拆词 101 条。
完整逐条记录保存在碰撞 JSON；名称线索清单：`docs/field_verification/20261014/20261014_alphabetic_field_name_inventory.csv`。
> 拼音、英文、缩写和混合拆词只用于检索候选；必须结合原始值、接口定义和独立来源复核，不得据此定案或改写主字典。

| 逐源字段路径 | 状态/审阅范围 | 名称形式与拆词 | 词义线索（非释义） | 样本日期 |
|:--|:--|:--|:--|:--|
| `市场源(market_sources)::change_type` | unverified / unverified_semantics | snake_case_or_mixed: change type | 变化/涨跌 + 类型 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::first_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: first limit time | 首次/第一 + 涨跌停限制 + 时间 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::last_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: last limit time | 最近/上一期 + 涨跌停限制 + 时间 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::name` | unverified / unverified_semantics | recognized_english_word_candidate: name | 名称 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::total_value` | unverified / unverified_semantics | snake_case_or_mixed: total value | 总 + 值 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::limit_count` | verified / verified_metadata_gap | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::limit_time` | unverified / unverified_semantics | snake_case_or_mixed: limit time | 涨跌停限制 + 时间 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::plate_limit_up_count` | verified / verified_metadata_gap | snake_case_or_mixed: plate limit up count | 涨跌停限制 + 上/涨 + 数量/次数 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `财联社(cls)::time` | unverified / unverified_semantics | recognized_english_word_candidate: time | 时间 | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110 |
| `TDX(双命名源)::changqifuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: changqifuzhai | 长期负债 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::cunhuo` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: cunhuo | 存货 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::eps` | unverified / unverified_semantics | recognized_english_word_candidate: eps | 每股收益 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::gudongrenshu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: gudongrenshu | 股东人数 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::ipodate` | unverified / unverified_semantics | recognized_english_phrase_candidate: ipodate | IPO/上市日期（字段语境候选） | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::jingyingxianjinliu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingyingxianjinliu | 经营现金流 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::jingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingzichan | 净资产 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::liudongfuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: liudongfuzhai | 流动负债 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::meigujingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: meigujingzichan | 每股净资产 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::yingshouzhangkuan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: yingshouzhangkuan | 应收账款 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::zhuyingshouru` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zhuyingshouru | 主营收入 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::zibengongjijin` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zibengongjijin | 资本公积金 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::zongzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongzichan | 总资产 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `同花顺-fuyao::snapshot.open_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot open price | 开盘 + 价格 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `reports::actualLastTwoYearEps` | unverified / unverified_semantics | camel_case_or_mixed: actual Last Two Year Eps | 最近/上一期 + 每股收益 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::actualLastYearEps` | unverified / unverified_semantics | camel_case_or_mixed: actual Last Year Eps | 最近/上一期 + 每股收益 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::count` | verified / verified_metadata_gap | recognized_english_word_candidate: count | 数量/次数 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::lastEmRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Code | 最近/上一期 + 代码 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::lastEmRatingName` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Name | 最近/上一期 + 名称 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::lastEmRatingValue` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Value | 最近/上一期 + 值 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::predictLastYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Eps | 最近/上一期 + 每股收益 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::predictLastYearPe` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Pe | 最近/上一期 + 市盈率 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `TDX-eltdx(适配层)::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::broken_count` | unverified / unverified_semantics | snake_case_or_mixed: broken count | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::circulating_value` | unverified / unverified_semantics | snake_case_or_mixed: circulating value | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::sector` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: sector | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::turnover_rate` | unverified / unverified_semantics | snake_case_or_mixed: turnover rate | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::zt_continuous` | unverified / unverified_semantics | snake_case_or_mixed: zt continuous | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::zt_days` | unverified / unverified_semantics | snake_case_or_mixed: zt days | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::one_word` | unverified / unverified_semantics | snake_case_or_mixed: one word | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::plate_amount` | verified / verified_metadata_gap | snake_case_or_mixed: plate amount | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::plate_code` | verified / verified_metadata_gap | snake_case_or_mixed: plate code | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::plate_name` | verified / verified_metadata_gap | snake_case_or_mixed: plate name | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::popular` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: popular | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `开盘啦(kpl_limit_up_detail)::raw_columns.col_19` | verified / verified_metadata_gap | runtime_tokenization_only: col 19 | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `财联社(cls)::content` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: content | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110 |
| `财联社(cls)::level` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: level | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110 |
| `财联社(cls)::reading_num` | unverified / unverified_semantics | snake_case_or_mixed: reading num | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110 |
| `财联社(cls)::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110 |
| `开盘红::industry_limit_up_count` | unverified / unverified_semantics | runtime_tokenization_only: industry limit up count | — | T:20261016, T:20261019, T:20261021, T:20261022, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 |
| `TDX(双命名源)::updateddate` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: updateddate | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::zhuyinglyrun` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: zhuyinglyrun | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `同花顺-fuyao::fin_report` | unverified / unverified_semantics | snake_case_or_mixed: fin report | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::big_order_300w_net` | unverified / unverified_semantics | runtime_tokenization_only: big order 300 w net | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::institution_add` | unverified / unverified_semantics | runtime_tokenization_only: institution add | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::main_inflow` | unverified / unverified_semantics | snake_case_or_mixed: main inflow | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::pe_next` | unverified / unverified_semantics | runtime_tokenization_only: pe next | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::pe_now` | unverified / unverified_semantics | runtime_tokenization_only: pe now | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::strength` | unverified / unverified_semantics | runtime_tokenization_only: strength | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::total_value` | unverified / unverified_semantics | runtime_tokenization_only: total value | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `同花顺-fuyao::snapshot.prev_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot prev price | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `新浪(扩展API)::opendate` | conflict / unverified_semantics | unsegmented_latin_pinyin_or_word: opendate | — | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::amplitude` | verified / verified_metadata_gap | runtime_tokenization_only: amplitude | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::avg` | verified / verified_metadata_gap | runtime_tokenization_only: avg | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::bid_ask_ratio` | verified / verified_metadata_gap | runtime_tokenization_only: bid ask ratio | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::board` | verified / verified_metadata_gap | runtime_tokenization_only: board | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::listing_date` | verified / verified_metadata_gap | runtime_tokenization_only: listing date | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::name` | verified / verified_metadata_gap | runtime_tokenization_only: name | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::st` | verified / verified_metadata_gap | runtime_tokenization_only: st | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::status` | verified / verified_metadata_gap | runtime_tokenization_only: status | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::symbol` | verified / verified_metadata_gap | runtime_tokenization_only: symbol | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::symbol_id` | unverified / unverified_semantics | runtime_tokenization_only: symbol id | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::turnover_rate` | verified / verified_metadata_gap | runtime_tokenization_only: turnover rate | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `ZHB-tdxstat::stat.unknown_2` | verified / verified_metadata_gap | snake_case_or_mixed: stat unknown 2 | — | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 |
| `ZHB-tdxstat::stat.unknown_26` | verified / verified_metadata_gap | snake_case_or_mixed: stat unknown 26 | — | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 |
| `FTShare REST::pe_ttm` | verified / verified_metadata_gap | runtime_tokenization_only: pe ttm | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::rank` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: rank | — | T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX-eltdx(适配层)::trade_date` | unverified / unverified_semantics | snake_case_or_mixed: trade date | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `reports::attachPages` | conflict / unverified_semantics | camel_case_or_mixed: attach Pages | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::attachSize` | conflict / unverified_semantics | camel_case_or_mixed: attach Size | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::attachType` | unverified / unverified_semantics | camel_case_or_mixed: attach Type | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::column` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: column | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::emIndustryCode` | unverified / unverified_semantics | camel_case_or_mixed: em Industry Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::emRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: em Rating Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::emRatingName` | verified / verified_metadata_gap | camel_case_or_mixed: em Rating Name | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::emRatingValue` | verified / verified_metadata_gap | camel_case_or_mixed: em Rating Value | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::encodeUrl` | conflict / unverified_semantics | camel_case_or_mixed: encode Url | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::industryCode` | verified / verified_metadata_gap | camel_case_or_mixed: industry Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::industryName` | verified / verified_metadata_gap | camel_case_or_mixed: industry Name | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::indvAimPriceL` | unverified / unverified_semantics | camel_case_or_mixed: indv Aim Price L | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::indvAimPriceT` | unverified / unverified_semantics | camel_case_or_mixed: indv Aim Price T | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::indvInduCode` | verified / verified_metadata_gap | camel_case_or_mixed: indv Indu Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::indvInduName` | verified / verified_metadata_gap | camel_case_or_mixed: indv Indu Name | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::indvIsNew` | unverified / unverified_semantics | camel_case_or_mixed: indv Is New | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::infoCode` | verified / verified_metadata_gap | camel_case_or_mixed: info Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::newIssuePrice` | conflict / unverified_semantics | camel_case_or_mixed: new Issue Price | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110 |

Markdown 显示前 100 条；其余 36 条完整保留在 JSON。

## 探索候选持续跟踪

研究台账：`collision_research_state.json.gz`；累计历史跟踪候选对 2947，本报告候选对 655，历史复现 559，新发现 96。
台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，不会自动改变字段状态、碰撞锚或主字典。新报告只将 `actionable_L1`、L4 和主动方法候选写入待研究队列；已登记关系的复验单独展示，历史跟踪记录不会被删除。

## 候选覆盖、公式与下一步采样

本节用于定位证据缺口和安排后续取样。相关性、公式与样本优先级均为探索候选；不会改变 L1/L1-U 门槛、来源独立性或主字典。

- 未知目标 231 个；其中有方法候选 141 个、无候选 90 个；多候选目标 133 个。
- 方法候选生成 4832 条；全局详细项保留 500/500，另按目标字段保留 124 条；完整明细 4832 条在 JSON `method_candidate_inventory`；未归档明细 0 条。
- 字段覆盖详情：available；覆盖身份 1974，读取 18 份本地索引。

### 优先处理字段

| 未知字段 | 当前诊断 | 独立对比/候选数 | 独立锚家族/本源日期 | 建议复核股票 | 最强候选线索 |
|:--|:--|--:|:--|:--|:--|
| `zhb.full.dividend_yield` | 存在多个候选，需区分 | 376 / 118 | 6 家族 / 252 对 / 本源 10 日 | 600519 (49.81127) | tencent[64] (robust_correlation,per_stock_time_series); ulist239.f133 (robust_correlation,per_stock_time_series) |
| `zhb.full.change_30k_bar_ref` | 存在多个候选，需区分 | 376 / 117 | 6 家族 / 252 对 / 本源 11 日 | 600825 (1.644457) | tencent[75] (robust_correlation,per_stock_time_series); tencent[71] (robust_correlation,per_stock_time_series) |
| `push2.f160` | 存在多个候选，需区分 | 359 / 108 | 6 家族 / 307 对 / 本源 0 日 | 600519 (21.368591) | tencent[9] (robust_correlation,affine_formula); tencent[68] (robust_correlation,affine_formula) |
| `push2.f108` | 存在多个候选，需区分 | 359 / 106 | 6 家族 / 307 对 / 本源 0 日 | 600519 (60.057176) | tencent[9] (robust_correlation,affine_formula); tencent[68] (robust_correlation,affine_formula) |
| `zhb.full.change_ytd` | 存在多个候选，需区分 | 376 / 106 | 6 家族 / 252 对 / 本源 11 日 | 600825 (1.860585) | tencent[75] (robust_correlation,affine_formula,per_stock_time_series); tencent[62] (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.low_52w` | 存在多个候选，需区分 | 376 / 102 | 6 家族 / 252 对 / 本源 0 日 | 600519 (21.321269) | tencent[68] (robust_correlation,affine_formula,per_stock_time_series); tencent[67] (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.change_250k_bar` | 存在多个候选，需区分 | 376 / 101 | 6 家族 / 252 对 / 本源 11 日 | 002242 (1.961517) | tencent[79] (robust_correlation,affine_formula,per_stock_time_series); tencent[75] (robust_correlation,per_stock_time_series) |
| `tdx.finance_info.eps` | 存在多个候选，需区分 | 402 / 98 | 6 家族 / 252 对 / 本源 0 日 | no_shared_stock_holdout | push2.f92 (robust_correlation,affine_formula,per_stock_time_series); push2.f55 (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.change_20d` | 存在多个候选，需区分 | 376 / 96 | 6 家族 / 252 对 / 本源 0 日 | 002242 (3.571035) | tencent[70] (robust_correlation,affine_formula,per_stock_time_series); push2.f120 (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.change_30d` | 存在多个候选，需区分 | 376 / 96 | 6 家族 / 252 对 / 本源 0 日 | 002242 (3.571035) | tencent[70] (robust_correlation,affine_formula,per_stock_time_series); push2.f120 (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f176` | 存在多个候选，需区分 | 359 / 95 | 6 家族 / 307 对 / 本源 0 日 | 600519 (14.135462) | tencent[46] (robust_correlation,per_stock_time_series); fuyao.valuation.ps_ttm (robust_correlation,per_stock_time_series) |
| `zhb.full.change_30k_bar` | 存在多个候选，需区分 | 376 / 95 | 6 家族 / 252 对 / 本源 11 日 | 600825 (3.536658) | ulist239.f24 (robust_correlation,affine_formula,per_stock_time_series); tencent[75] (robust_correlation,per_stock_time_series) |
| `zhb.full.high_52w` | 存在多个候选，需区分 | 376 / 95 | 6 家族 / 252 对 / 本源 11 日 | 600519 (20.540023) | tencent[68] (robust_correlation,affine_formula,per_stock_time_series); tencent[67] (robust_correlation,affine_formula,per_stock_time_series) |
| `em_fund_flow.f135` | 存在多个候选，需区分 | 369 / 90 | 6 家族 / 307 对 / 本源 0 日 | no_shared_stock_holdout | tdx.quote_raw.amount (robust_correlation,affine_formula,per_stock_time_series); tdx.quote_full.amount_wan (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.change_60d` | 存在多个候选，需区分 | 376 / 90 | 6 家族 / 252 对 / 本源 0 日 | 600825 (1.272012) | tencent[71] (robust_correlation,affine_formula,per_stock_time_series); push2.f121 (robust_correlation,affine_formula,per_stock_time_series) |
| `push2ex.circulating_value` | 存在多个候选，需区分 | 359 / 88 | 6 家族 / 307 对 / 本源 0 日 | no_shared_stock_holdout | kpl.raw_columns.col_13 (robust_correlation,per_stock_time_series); tencent[45] (robust_correlation,affine_formula) |
| `push2ex.total_value` | 存在多个候选，需区分 | 359 / 88 | 6 家族 / 307 对 / 本源 0 日 | no_shared_stock_holdout | kpl.raw_columns.col_13 (robust_correlation,per_stock_time_series); tencent[45] (robust_correlation,affine_formula) |
| `ulist239.f63` | 存在多个候选，需区分 | 341 / 87 | 6 家族 / 307 对 / 本源 0 日 | no_shared_stock_holdout | eltdx.shortline.open_volume_ratio (robust_correlation,per_stock_time_series); eltdx.shortline.open_volume_hand (robust_correlation,per_stock_time_series) |
| `push2.f135` | 存在多个候选，需区分 | 359 / 86 | 6 家族 / 307 对 / 本源 0 日 | 600519 (0.06223) | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f136` | 存在多个候选，需区分 | 359 / 84 | 6 家族 / 307 对 / 本源 0 日 | candidates_converge_on_existing_samples | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `em_fund_flow.f136` | 存在多个候选，需区分 | 369 / 81 | 6 家族 / 307 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.amount` | 存在多个候选，需区分 | 376 / 76 | 6 家族 / 252 对 / 本源 0 日 | 600519 (2.070212) | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[7]` | 存在多个候选，需区分 | 539 / 67 | 6 家族 / 362 对 / 本源 17 日 | no_shared_stock_holdout | sina[8] (robust_correlation,per_stock_time_series); eltdx.quote_snapshot.total_hand (robust_correlation,per_stock_time_series) |
| `zhb.full.employee_count` | 存在多个候选，需区分 | 376 / 63 | 6 家族 / 252 对 / 本源 10 日 | 601288 (6.362856) | tencent[76] (robust_correlation,affine_formula); tencent[73] (robust_correlation,affine_formula) |
| `tencent[8]` | 存在多个候选，需区分 | 539 / 62 | 6 家族 / 362 对 / 本源 17 日 | no_shared_stock_holdout | sina[8] (robust_correlation,per_stock_time_series); eltdx.quote_snapshot.total_hand (robust_correlation,per_stock_time_series) |
| `zhb.full.amount_1d` | 存在多个候选，需区分 | 376 / 59 | 6 家族 / 252 对 / 本源 10 日 | 600519 (23.399812) | tencent[85] (robust_correlation); tencent[76] (robust_correlation) |
| `zhb.full.main_net_buy_amount` | 存在多个候选，需区分 | 376 / 59 | 6 家族 / 252 对 / 本源 11 日 | 600519 (3.120821) | tencent[79] (robust_correlation); tencent[75] (robust_correlation) |
| `zhb.full.change_10d` | 存在多个候选，需区分 | 376 / 58 | 6 家族 / 252 对 / 本源 0 日 | 600519 (12.779401) | tencent[69] (robust_correlation,affine_formula,per_stock_time_series); ulist239.f160 (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.main_net_buy_amount_1d` | 存在多个候选，需区分 | 376 / 58 | 6 家族 / 252 对 / 本源 11 日 | 601288 (2.787159) | tencent[79] (robust_correlation); tencent[75] (robust_correlation) |
| `zhb.full.amount_2d` | 存在多个候选，需区分 | 376 / 55 | 6 家族 / 252 对 / 本源 10 日 | 600519 (23.777711) | tencent[85] (robust_correlation); tencent[75] (robust_correlation) |
| `em_fund_flow.f138` | 存在多个候选，需区分 | 369 / 54 | 6 家族 / 307 对 / 本源 0 日 | no_shared_stock_holdout | eltdx.quote_snapshot.amount_raw (robust_correlation,per_stock_time_series); zhb.stat2.amount (robust_correlation,per_stock_time_series) |
| `em_fund_flow.f139` | 存在多个候选，需区分 | 369 / 54 | 6 家族 / 307 对 / 本源 0 日 | no_shared_stock_holdout | tencent[70] (robust_correlation); tencent[58] (robust_correlation) |
| `push2.f49` | 存在多个候选，需区分 | 359 / 54 | 6 家族 / 307 对 / 本源 0 日 | candidates_converge_on_existing_samples | sina[8] (robust_correlation,affine_formula,per_stock_time_series); ftshare_rest.volume (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.change_10k_bar` | 存在多个候选，需区分 | 376 / 53 | 6 家族 / 252 对 / 本源 10 日 | 600519 (12.726161) | tencent[69] (robust_correlation,per_stock_time_series); tencent[63] (robust_correlation,per_stock_time_series) |
| `zhb.full.main_net_buy_hands` | 存在多个候选，需区分 | 376 / 52 | 6 家族 / 252 对 / 本源 11 日 | 600519 (2.987993) | tencent[79] (robust_correlation); tencent[75] (robust_correlation) |
| `zhb.full.main_net_buy_hands_1d` | 存在多个候选，需区分 | 376 / 52 | 6 家族 / 252 对 / 本源 11 日 | 600519 (2.418048) | tencent[75] (robust_correlation); tencent[70] (robust_correlation) |
| `push2.f161` | 存在多个候选，需区分 | 359 / 51 | 6 家族 / 307 对 / 本源 0 日 | candidates_converge_on_existing_samples | sina[8] (robust_correlation,affine_formula,per_stock_time_series); ftshare_rest.volume (robust_correlation,affine_formula,per_stock_time_series) |
| `tdx.finance_info.zhuyinglyrun` | 存在多个候选，需区分 | 402 / 51 | 6 家族 / 252 对 / 本源 0 日 | no_shared_stock_holdout | push2.f183 (robust_correlation,per_stock_time_series); tencent[76] (robust_correlation) |
| `kpl.main_sell` | 存在多个候选，需区分 | 628 / 50 | 6 家族 / 411 对 / 本源 0 日 | 300296 (2.046956) | push2ex.amount (robust_correlation,per_stock_time_series); kph.turnover (robust_correlation,per_stock_time_series) |
| `kpl.raw_columns.col_10` | 存在多个候选，需区分 | 628 / 50 | 6 家族 / 411 对 / 本源 0 日 | 300296 (2.046956) | push2ex.amount (robust_correlation,per_stock_time_series); kph.turnover (robust_correlation,per_stock_time_series) |
| `zhb.full.board_count` | 存在多个候选，需区分 | 376 / 50 | 6 家族 / 252 对 / 本源 10 日 | 688327 (10.511923) | tencent[6] (robust_correlation); tencent[68] (robust_correlation) |
| `ulist239.f135` | 存在多个候选，需区分 | 341 / 48 | 6 家族 / 307 对 / 本源 0 日 | 601288 (4.099191) | tencent[76] (robust_correlation,affine_formula); tencent[73] (robust_correlation,affine_formula) |
| `eltdx.limit_ladder.open_price` | 存在多个候选，需区分 | 449 / 45 | 6 家族 / 252 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[85] (robust_correlation,affine_formula) |
| `eltdx.limit_ladder.pre_close` | 存在多个候选，需区分 | 449 / 45 | 6 家族 / 252 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[85] (robust_correlation,affine_formula) |
| `kpl.main_buy` | 存在多个候选，需区分 | 628 / 45 | 6 家族 / 411 对 / 本源 0 日 | 300296 (2.673385) | push2ex.amount (robust_correlation,per_stock_time_series); kph.turnover (robust_correlation,per_stock_time_series) |
| `kpl.raw_columns.col_02` | 存在多个候选，需区分 | 628 / 45 | 6 家族 / 411 对 / 本源 0 日 | no_shared_stock_holdout | tencent[8] (robust_correlation); tencent[76] (robust_correlation) |
| `kpl.raw_columns.col_09` | 存在多个候选，需区分 | 628 / 45 | 6 家族 / 411 对 / 本源 0 日 | 300296 (2.673385) | push2ex.amount (robust_correlation,per_stock_time_series); kph.turnover (robust_correlation,per_stock_time_series) |
| `sina[26]` | 存在多个候选，需区分 | 589 / 45 | 6 家族 / 402 对 / 本源 17 日 | 601288 (13.583939) | tencent[26] (robust_correlation,affine_formula,per_stock_time_series); tencent[68] (robust_correlation) |
| `ulist239.f149` | 存在多个候选，需区分 | 341 / 44 | 6 家族 / 307 对 / 本源 0 日 | 000678 (3.155604) | tencent[63] (robust_correlation,per_stock_time_series); ftshare_rest.change_rate_day5 (robust_correlation,per_stock_time_series) |
| `ulist239.f297` | 存在多个候选，需区分 | 341 / 41 | 6 家族 / 307 对 / 本源 0 日 | candidates_converge_on_existing_samples | tencent[30] (robust_correlation,affine_formula,per_stock_time_series); ftshare_rest.ts_millis (robust_correlation,affine_formula,per_stock_time_series) |

_此表显示优先级最高的 50 / 共 231 个目标；完整清单见 JSON。_


### 舍入近似数值线索（仅研究，不算 L1/L1-U；6 组）

近似窗口只用于提示复核：需核对双方原始单位、展示精度和来源口径；不得把该命中率当作字段语义结论或注册表写回依据。完整明细在 JSON `candidate_triage.approximate_matches`。

| 左字段 | 右字段 | 近似命中率 | 精确/舍入命中 | 有效日期 | 最大误差（绝对/相对） |
|:--|:--|--:|:--|:--|:--|
| `zhb.full.amount` | `tencent[57]` | 100.00% | 2/218 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | 0.04749999998603016 / 6.473569341022521e-06 |
| `zhb.full.change_pct` | `fuyao.snapshot.price_change_ratio_pct` | 100.00% | 2/216 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | 0.0049859999999999904 / 0.0904956798544793 |
| `zhb.full.amount` | `tencent[37]` | 100.00% | 23/197 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | 0.5100000000093132 / 0.00014484356894553882 |
| `zhb.full.high_52w` | `push2.f174` | 98.00% | 88/10 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | 0.030000000000001137 / 0.0017411491584446393 |
| `zhb.full.pe_ttm` | `fuyao.valuation.pe_ttm` | 96.36% | 0/212 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | 0.005046000000000106 / 0.0005546498277842869 |
| `zhb.full.change_250k_bar` | `tencent[79]` | 92.69% | 148/55 | T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | 0.11999999999999744 / 0.004822446295484412 |

### 补足全局截断的字段候选（124）

| 未知字段 | 候选字段 | 方法 | 样本 | 日期 | 来源 |
|:--|:--|:--|--:|:--|:--|
| `eltdx.limit_ladder.auction_prev_volume_ratio` | `tencent[69]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.beta_60d` | `tencent[76]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.ladder_level` | `push2ex.limit_count` | robust_correlation, affine_formula | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, push2ex |
| `eltdx.limit_ladder.open_amount` | `tencent[8]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_change_pct` | `tencent[86]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_prev_amount_ratio` | `tencent[86]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_price` | `tencent[9]` | robust_correlation, affine_formula | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_turnover_z` | `tencent[8]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_volume_hand` | `tencent[8]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_volume_ratio` | `tencent[86]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.pe_ttm` | `tencent[53]` | robust_correlation, affine_formula | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.pre_close` | `tencent[9]` | robust_correlation, affine_formula | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.prev_amount` | `tencent[8]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.prev_open_amount` | `tencent[8]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.prev_open_volume_hand` | `tencent[86]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.seal_to_amount_ratio` | `tencent[86]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.seal_to_float_ratio` | `tencent[86]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.year_limit_up_days` | `tencent[86]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `em_fund_flow.f135` | `tencent[57]` | robust_correlation, per_stock_time_series | 151 | T:20261019, T:20261102, T:20261103, T:20261104, T:20261105 | em_fund_flow, tencent |
| `em_fund_flow.f138` | `eltdx.quote_snapshot.amount_raw` | robust_correlation, per_stock_time_series | 123 | T:20261019, T:20261102, T:20261103, T:20261104, T:20261105 | eltdx, em_fund_flow |
| `em_fund_flow.f139` | `tencent[70]` | robust_correlation | 129 | T:20261019, T:20261102, T:20261103, T:20261104, T:20261105 | em_fund_flow, tencent |
| `em_kline_f61.dktotal` | `tencent[30]` | per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | em_kline_f61, tencent |
| `event_dc.AMPLITUDE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.CHANGE_RATE` | `ftshare_rest.change_rate_ytd` | semantic_label | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.CLOSE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.EACHBALLOT_SHARES` | `ftshare_rest.shares` | semantic_label | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.INDUSTRY_PE` | `ftshare_rest.ts_millis` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.INDUSTRY_PE_NEW` | `ftshare_rest.ts_millis` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.IPO_YIELD` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.ISSUE_NUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.ISSUE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LATELY_PRICE` | `ftshare_rest.close` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LD_AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LD_CLOSE_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LD_HIGH_CHANG` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LD_OPEN_PREMIUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LIMIT_UP_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.MZYQ_PAY_FUND` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.OD_HIGH_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.OPEN_AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.OPEN_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.PROFIT` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TCHANGE_RATE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TNEW_PRICE` | `ftshare_rest.close` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TOTAL_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TOTAL_ISSUE_NUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TOTAL_SHARES` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TURNOVERRATE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.fetched_at` | `ftshare_rest.ts_millis` | robust_correlation, affine_formula | 28 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `kph.industry_limit_up_count` | `push2ex.limit_count` | semantic_label | 457 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028 | kph, push2ex |
| `kpl.amplitude` | `tencent[43]` | robust_correlation, affine_formula | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, tencent |
| `kpl.main_buy` | `push2ex.turnover_rate` | per_stock_time_series | 1016 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.main_sell` | `push2ex.turnover_rate` | per_stock_time_series | 1016 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.raw_columns.col_02` | `tencent[8]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, tencent |
| `kpl.raw_columns.col_09` | `push2ex.turnover_rate` | per_stock_time_series | 1016 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.raw_columns.col_10` | `push2ex.turnover_rate` | per_stock_time_series | 1016 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.raw_columns.col_16` | `push2ex.turnover_rate` | per_stock_time_series | 1016 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.raw_columns.col_17` | `tencent[43]` | robust_correlation, affine_formula | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, tencent |
| `kpl.raw_columns.col_20` | `tencent[73]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, tencent |
| `push2.f103` | `zhb.tipinfo.hg_amount_yi` | robust_correlation, affine_formula | 40 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104 | push2, zhb |
| `push2.f176` | `fuyao.valuation.ps_ttm` | robust_correlation, per_stock_time_series | 180 | T:20261020, T:20261023, T:20261029, T:20261102, T:20261103 | fuyao, push2 |
| `push2ex.broken_count` | `kpl.turnover_real` | per_stock_time_series | 1016 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `push2ex.circulating_value` | `tencent[45]` | robust_correlation, affine_formula | 15 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | push2ex, tencent |
| `push2ex.first_limit_time` | `kph.turnover_rate` | per_stock_time_series | 457 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028 | kph, push2ex |
| `push2ex.total_value` | `tencent[45]` | robust_correlation, affine_formula | 15 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | push2ex, tencent |
| `push2ex.turnover_rate` | `tencent[38]` | robust_correlation, affine_formula | 15 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | push2ex, tencent |
| `push2ex.zt_continuous` | `kpl.zt_time` | per_stock_time_series | 1016 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `push2ex.zt_days` | `kpl.zt_time` | per_stock_time_series | 1016 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `sina[14]` | `tencent[68]` | robust_correlation | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[16]` | `tencent[68]` | robust_correlation | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[18]` | `tencent[68]` | robust_correlation | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[24]` | `tencent[67]` | robust_correlation | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[26]` | `tencent[68]` | robust_correlation | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[28]` | `tencent[26]` | robust_correlation | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[36]` | `push2.f62` | robust_correlation | 17 | T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, sina |
| `slist.n_boards` | `tencent[45]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | slist, tencent |
| `tdx.finance_info.zhuyinglyrun` | `tencent[76]` | robust_correlation | 338 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | tdx, tencent |
| `tencent[22]` | `sina[20]` | robust_correlation | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `tencent[24]` | `sina[22]` | robust_correlation | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `tencent[26]` | `sina[22]` | robust_correlation | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `tencent[28]` | `sina[22]` | robust_correlation | 340 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `tencent[86]` | `eltdx.shortline.prev2_seal_amount` | robust_correlation | 17 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261026 | eltdx, tencent |
| `ulist239.f111` | `zhb.tipinfo.hg_amount_yi` | robust_correlation | 30 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `ulist239.f127` | `zhb.stat2.change_mtd` | robust_correlation, per_stock_time_series | 100 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `ulist239.f135` | `tencent[76]` | robust_correlation, affine_formula | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f139` | `tencent[76]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f148` | `tencent[71]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f149` | `tencent[63]` | robust_correlation, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f190` | `tdx.finance_info.hgu` | robust_correlation, affine_formula | 138 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tdx, ulist239 |
| `ulist239.f192` | `tdx.finance_info.hgu` | robust_correlation, affine_formula | 138 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tdx, ulist239 |
| `ulist239.f22` | `tencent[80]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f297` | `tencent[6]` | per_stock_time_series | 80 | T:20261105, T:20261106, T:20261109, T:20261110 | tencent, ulist239 |
| `ulist239.f46` | `zhb.stat.board_count` | robust_correlation | 25 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `ulist239.f59` | `tencent[39]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f63` | `eltdx.shortline.open_volume_ratio` | robust_correlation, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | eltdx, ulist239 |
| `ulist239.f98` | `zhb.stat.zt_streak_cycle` | robust_correlation | 17 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `ulist239.f99` | `eltdx.shortline.limit_up_count_in_stat_days` | robust_correlation | 22 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | eltdx, ulist239 |
| `zhb.full.amount_1d` | `tencent[85]` | robust_correlation | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028 | tencent, zhb |
| `zhb.full.amount_2d` | `tencent[85]` | robust_correlation | 220 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028 | tencent, zhb |

_仅显示前 100 / 共 124 条字段前沿候选。_


### 双输入公式候选
本轮未发现通过留出筛选的公式候选；测试组合 5583 个。


### 已知映射与已证伪关系的候选校准

- 已登记正向对照：当前窗口有 148 组独立数值关系可评估，148 组被方法候选识别；样本不足 0 组。此计数仅检查方法覆盖，不是准确率。
- 已证伪负向对照：数值关系 0 组，其中仍有方法信号 0 组；这些信号被隔离，不进入普通候选。

### 采集覆盖异常源

- axdata: 20261021, 20261026 ({'failed': 1, 'ok': 15, 'partial': 1})
- baidu: 20261106, 20261109, 20261110 ({'deprecated': 2, 'pending_validation': 14})
- clist: 20261028, 20261029, 20261030 ({'ok': 7, 'partial': 8})
- em_fund_flow: 20261028, 20261029, 20261030 ({'ok': 7, 'partial': 9})
- em_hot: 20261106, 20261109, 20261110 ({'context_only': 15})
- em_kline_f61: 20261028, 20261029, 20261030 ({'ok': 7, 'partial': 9})
- exchange: 20261106, 20261109, 20261110 ({'context_only': 15})
- ftshare: 20261106, 20261109, 20261110 ({'deprecated': 14, 'failed': 3})
- market_sources: 20261026 ({'ok': 16, 'partial': 1})
- news_wscn_cctv: 20261015 ({'ok': 16, 'partial': 1})
- push2: 20261028, 20261029, 20261030 ({'failed': 4, 'ok': 7, 'partial': 4})
- slist: 20261028, 20261029, 20261030 ({'failed': 8, 'ok': 7})
- sse_e_interaction: 20261016 ({'ok': 16, 'partial': 1})
- st_list: 20261028, 20261029, 20261030 ({'ok': 8, 'partial': 8})
- tdx: 20261104, 20261105 ({'ok': 15, 'partial': 2})
- ulist239: 20261028, 20261029, 20261030 ({'failed': 10, 'ok': 7})
- zhb: 20261105, 20261109, 20261110 ({'ok': 5, 'partial': 12})

## 候选身份与人工审阅状态

- 候选身份：生成 4907 条，唯一候选 4907 个，重复身份 0，无效身份 0。
- 审阅台账：可用；当前状态 `pending`；已审 0，待处理 4907，覆盖率 0.0%。
- 重复归并组：0；每个成员均保留到代表候选的反向追溯。
- 处置计数：`accepted_for_adjudication` 0；`duplicate_grouped` 0；`insufficient_evidence` 0；`needs_external_evidence` 0；`rejected` 0；`unreviewed` 4907。
- `accepted_for_adjudication` 只表示可进入现有证据裁决流程；审阅台账不会修改主字典或字段注册表。

## 报告完整性与审阅范围

- 机器可读完整性：`complete`；方法候选生成 4832 条，完整明细保存 4832 条，缺失 0 条，多余 0 条，重复 0 条，身份无效 0 条。
- 全量方法候选位于同名 JSON 的 `method_candidate_inventory`；Markdown 的 Top-N 表格是导航摘要，不能代替全量 JSON 审阅。
- 候选审阅数据对账：`complete`；唯一候选 4907 个，审阅 0 个，待处理 4907 个；人工审阅进度与机器清单完整性分别统计。
- Markdown 未逐行展示、但 JSON 保留的部分：
  - `method_candidates`：展示 100 / 500，摘要省略 400 条。
  - `method_candidate_inventory`：展示 0 / 4832，摘要省略 4832 条。
  - `method_candidate_frontier`：展示 100 / 124，摘要省略 24 条。
  - `candidate_triage.targets`：展示 50 / 231，摘要省略 181 条。
  - `diagnostics`：展示 100 / 305，摘要省略 205 条。
- 完整性对账通过；逐目标复核仍须覆盖 JSON 的全部明细，并为每项记录已检查、重复归并、证据不足或需外部核验的处置。
