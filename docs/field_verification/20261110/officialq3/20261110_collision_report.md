# 全源对撞报告（20261110）

> 交易数据窗口配置：近 7 个交易日（`--window`）
> 行情窗口：20261102 ~ 20261110（7 个不同交易日）｜字段 1298 个｜样本值 654580 条
> 新闻/公告自然日窗口：20261104 ~ 20261110
> 主攻目标（unverified）=204｜可审定新候选=0｜首次发现新候选对=0｜已登记关系复验=0｜异号同义 0 / 同号镜像 0

> **规则**：L1 每日需≥18 组有效配对，并至少有5 组信息配对；双方同时为 0 或同时缺失不计命中率，一侧为 0、另一侧非 0 按失配计。信息配对命中率≥90%，且覆盖至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。JSON `daily_sample_counts` 与 `daily_informative_sample_counts`分别保留每日有效配对数和 L1 信息配对数。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 新候选 — 异号同义（跨编号，高价值）(0)

_本轮无异号同义候选。_


## 二、L1 / L1-U 新候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、已登记映射的本窗口复验（0）

_这些关系已在主注册表登记，只用于观察当前样本是否仍支持既有映射；它们不是新的未知字段候选，也不能再次提交为新定案。_

_本轮没有已登记关系进入复验窗口。_


## 四、L4 存疑候选（26）

| 左字段 | 右字段 | 命中率 | 天数 | 样本 |
|:--|:--|--:|--:|--:|
| `ulist239.f190` | `tdx.finance_info.hgu` | 94.93% | 7 | 138 |
| `push2ex.zt_continuous` | `kph.limit_count` | 90.45% | 5 | 178 |
| `ulist239.f190` | `zhb.stat.other_qy_jzc` | 90.00% | 5 | 100 |
| `zhb.full.other_qy_jzc` | `ulist239.f231` | 90.00% | 5 | 100 |
| `ulist239.f190` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 87.14% | 7 | 140 |
| `ulist239.f190` | `tdx.finance_info.bgu` | 84.78% | 7 | 138 |
| `push2ex.zt_days` | `kpl.raw_columns.col_15` | 83.56% | 7 | 511 |
| `push2ex.zt_continuous` | `kpl.raw_columns.col_15` | 83.56% | 7 | 511 |
| `push2ex.zt_days` | `kph.limit_count` | 83.15% | 5 | 178 |
| `zhb.full.other_qy_jzc` | `ulist239.f200` | 80.00% | 5 | 100 |
| `push2.f126` | `zhb.full.dividend_yield` | 70.00% | 5 | 100 |
| `push2.f126` | `zhb.stat.dividend_yield` | 70.00% | 5 | 100 |
| `ulist239.f11` | `tencent[80]` | 70.00% | 7 | 140 |
| `zhb.full.other_qy_jzc` | `push2.f107` | 60.00% | 5 | 100 |
| `zhb.full.other_qy_jzc` | `push2.f110` | 60.00% | 5 | 100 |
| `zhb.full.other_qy_jzc` | `ulist239.f13` | 60.00% | 5 | 100 |
| `zhb.full.other_qy_jzc` | `ulist239.f27` | 60.00% | 5 | 100 |
| `ulist239.f97` | `zhb.stat.other_qy_jzc` | 57.00% | 5 | 100 |
| `ulist239.f97` | `tdx.finance_info.hgu` | 55.80% | 7 | 138 |
| `push2.f126` | `tencent[64]` | 55.00% | 7 | 140 |
| `ulist239.f97` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 53.57% | 7 | 140 |
| `kpl.raw_columns.col_16` | `kph.limit_count` | 52.04% | 5 | 221 |
| `ulist239.f97` | `tdx.finance_info.bgu` | 50.72% | 7 | 138 |
| `kpl.raw_columns.col_02` | `kph.limit_count` | 45.70% | 5 | 221 |
| `kpl.raw_columns.col_02` | `push2ex.limit_count` | 43.64% | 7 | 511 |
| `kpl.raw_columns.col_16` | `push2ex.limit_count` | 42.27% | 7 | 511 |

## 五、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 六、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `push2ex.turnover_rate` | `kph.turnover_rate` | robust_correlation, per_stock_time_series, semantic_label | 178 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | kph, push2ex | Pearson=0.8599, Spearman=0.8957, LOO稳号=True |
| `ulist239.f11` | `tencent[80]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | tencent, ulist239 | Pearson=0.987, Spearman=0.9721, LOO稳号=True |
| `tencent[22]` | `sina[22]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[18]` | `tencent[18]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[16]` | `tencent[16]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[14]` | `tencent[14]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `push2.f49` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, sina | Pearson=0.9953, Spearman=0.9946, LOO稳号=True |
| `push2.f49` | `fuyao.snapshot.volume` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | fuyao, push2 | Pearson=0.9953, Spearman=0.9946, LOO稳号=True |
| `push2.f49` | `ftshare_rest.volume` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | ftshare_rest, push2 | Pearson=0.9953, Spearman=0.9946, LOO稳号=True |
| `push2.f49` | `eltdx.quote_snapshot.total_hand` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, push2 | Pearson=0.9953, Spearman=0.9946, LOO稳号=True |
| `push2.f49` | `eltdx.quote_snapshot.outer_disc` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, push2 | Pearson=0.9979, Spearman=0.9984, LOO稳号=True |
| `push2.f49` | `eltdx.quote_snapshot.inside_dish` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, push2 | Pearson=0.9873, Spearman=0.983, LOO稳号=True |
| `push2.f176` | `fuyao.valuation.ps_ttm` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | fuyao, push2 | Pearson=0.9867, Spearman=0.9684, LOO稳号=True |
| `push2.f161` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, sina | Pearson=0.9951, Spearman=0.994, LOO稳号=True |
| `push2.f161` | `fuyao.snapshot.volume` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | fuyao, push2 | Pearson=0.9951, Spearman=0.994, LOO稳号=True |
| `push2.f161` | `ftshare_rest.volume` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | ftshare_rest, push2 | Pearson=0.9951, Spearman=0.994, LOO稳号=True |
| `push2.f161` | `eltdx.quote_snapshot.total_hand` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, push2 | Pearson=0.9951, Spearman=0.994, LOO稳号=True |
| `push2.f161` | `eltdx.quote_snapshot.outer_disc` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, push2 | Pearson=0.9871, Spearman=0.9825, LOO稳号=True |
| `push2.f161` | `eltdx.quote_snapshot.inside_dish` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, push2 | Pearson=0.9978, Spearman=0.9987, LOO稳号=True |
| `push2.f49` | `tdx.s_vol` | robust_correlation, affine_formula, per_stock_time_series | 138 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, tdx | Pearson=0.9873, Spearman=0.9831, LOO稳号=True |
| `push2.f49` | `tdx.quote_raw.s_vol` | robust_correlation, affine_formula, per_stock_time_series | 138 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, tdx | Pearson=0.9873, Spearman=0.9831, LOO稳号=True |
| `push2.f49` | `tdx.quote_raw.b_vol` | robust_correlation, affine_formula, per_stock_time_series | 138 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, tdx | Pearson=0.9979, Spearman=0.9984, LOO稳号=True |
| `push2.f49` | `tdx.quote_full.s_vol` | robust_correlation, affine_formula, per_stock_time_series | 138 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, tdx | Pearson=0.9873, Spearman=0.9831, LOO稳号=True |
| `push2.f49` | `tdx.quote_full.b_vol` | robust_correlation, affine_formula, per_stock_time_series | 138 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, tdx | Pearson=0.9979, Spearman=0.9984, LOO稳号=True |
| `push2.f49` | `tdx.b_vol` | robust_correlation, affine_formula, per_stock_time_series | 138 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, tdx | Pearson=0.9979, Spearman=0.9984, LOO稳号=True |
| `push2.f161` | `tdx.s_vol` | robust_correlation, affine_formula, per_stock_time_series | 138 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, tdx | Pearson=0.9978, Spearman=0.9987, LOO稳号=True |
| `push2.f161` | `tdx.quote_raw.s_vol` | robust_correlation, affine_formula, per_stock_time_series | 138 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, tdx | Pearson=0.9978, Spearman=0.9987, LOO稳号=True |
| `push2.f161` | `tdx.quote_raw.b_vol` | robust_correlation, affine_formula, per_stock_time_series | 138 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, tdx | Pearson=0.9871, Spearman=0.9827, LOO稳号=True |
| `push2.f161` | `tdx.quote_full.s_vol` | robust_correlation, affine_formula, per_stock_time_series | 138 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, tdx | Pearson=0.9978, Spearman=0.9987, LOO稳号=True |
| `push2.f161` | `tdx.quote_full.b_vol` | robust_correlation, affine_formula, per_stock_time_series | 138 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, tdx | Pearson=0.9871, Spearman=0.9827, LOO稳号=True |
| `push2.f161` | `tdx.b_vol` | robust_correlation, affine_formula, per_stock_time_series | 138 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, tdx | Pearson=0.9871, Spearman=0.9827, LOO稳号=True |
| `push2.f136` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, tencent | Pearson=0.9819, Spearman=0.9912, LOO稳号=True |
| `push2.f136` | `tencent[37]` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, tencent | Pearson=0.9819, Spearman=0.9912, LOO稳号=True |
| `push2.f136` | `sina[9]` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, sina | Pearson=0.9819, Spearman=0.9912, LOO稳号=True |
| `push2.f136` | `fuyao.snapshot.turnover` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | fuyao, push2 | Pearson=0.9819, Spearman=0.9912, LOO稳号=True |
| `push2.f136` | `ftshare_rest.turnover` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | ftshare_rest, push2 | Pearson=0.9819, Spearman=0.9912, LOO稳号=True |
| `push2.f136` | `eltdx.quote_snapshot.amount` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, push2 | Pearson=0.9819, Spearman=0.9912, LOO稳号=True |
| `em_fund_flow.f136` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | em_fund_flow, tencent | Pearson=0.9819, Spearman=0.9912, LOO稳号=True |
| `em_fund_flow.f136` | `tencent[37]` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | em_fund_flow, tencent | Pearson=0.9819, Spearman=0.9912, LOO稳号=True |
| `em_fund_flow.f136` | `sina[9]` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | em_fund_flow, sina | Pearson=0.9819, Spearman=0.9912, LOO稳号=True |
| `em_fund_flow.f136` | `fuyao.snapshot.turnover` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | em_fund_flow, fuyao | Pearson=0.9819, Spearman=0.9912, LOO稳号=True |
| `em_fund_flow.f136` | `ftshare_rest.turnover` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | em_fund_flow, ftshare_rest | Pearson=0.9819, Spearman=0.9912, LOO稳号=True |
| `em_fund_flow.f136` | `eltdx.quote_snapshot.amount` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, em_fund_flow | Pearson=0.9819, Spearman=0.9912, LOO稳号=True |
| `push2.f136` | `tdx.quote_raw.amount` | robust_correlation, affine_formula, per_stock_time_series | 132 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, tdx | Pearson=0.9822, Spearman=0.9911, LOO稳号=True |
| `push2.f136` | `tdx.quote_full.amount_wan` | robust_correlation, affine_formula, per_stock_time_series | 132 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | push2, tdx | Pearson=0.9822, Spearman=0.9911, LOO稳号=True |
| `em_fund_flow.f136` | `tdx.quote_raw.amount` | robust_correlation, affine_formula, per_stock_time_series | 132 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | em_fund_flow, tdx | Pearson=0.9822, Spearman=0.9911, LOO稳号=True |
| `em_fund_flow.f136` | `tdx.quote_full.amount_wan` | robust_correlation, affine_formula, per_stock_time_series | 132 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | em_fund_flow, tdx | Pearson=0.9822, Spearman=0.9911, LOO稳号=True |
| `zhb.full.change_60k_bar` | `tencent[71]` | robust_correlation, affine_formula, per_stock_time_series | 100 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | tencent, zhb | Pearson=0.9982, Spearman=0.9853, LOO稳号=True |
| `zhb.full.change_60k_bar` | `push2.f121` | robust_correlation, affine_formula, per_stock_time_series | 100 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | push2, zhb | Pearson=0.9982, Spearman=0.9853, LOO稳号=True |
| `zhb.full.change_60k_bar` | `ftshare_rest.change_rate_day60` | robust_correlation, affine_formula, per_stock_time_series | 100 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ftshare_rest, zhb | Pearson=0.9975, Spearman=0.9853, LOO稳号=True |
| `push2.f135` | `zhb.stat2.amount` | robust_correlation, affine_formula, per_stock_time_series | 98 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | push2, zhb | Pearson=0.9803, Spearman=0.9894, LOO稳号=True |
| `push2.f135` | `zhb.full.amount` | robust_correlation, affine_formula, per_stock_time_series | 98 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | push2, zhb | Pearson=0.9803, Spearman=0.9894, LOO稳号=True |
| `em_fund_flow.f135` | `zhb.stat2.amount` | robust_correlation, affine_formula, per_stock_time_series | 98 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | em_fund_flow, zhb | Pearson=0.9803, Spearman=0.9894, LOO稳号=True |
| `em_fund_flow.f135` | `zhb.full.amount` | robust_correlation, affine_formula, per_stock_time_series | 98 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | em_fund_flow, zhb | Pearson=0.9803, Spearman=0.9894, LOO稳号=True |
| `push2.f136` | `zhb.stat2.amount` | robust_correlation, affine_formula, per_stock_time_series | 96 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | push2, zhb | Pearson=0.9835, Spearman=0.9913, LOO稳号=True |
| `push2.f136` | `zhb.full.amount` | robust_correlation, affine_formula, per_stock_time_series | 96 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | push2, zhb | Pearson=0.9835, Spearman=0.9913, LOO稳号=True |
| `em_fund_flow.f136` | `zhb.stat2.amount` | robust_correlation, affine_formula, per_stock_time_series | 96 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | em_fund_flow, zhb | Pearson=0.9835, Spearman=0.9913, LOO稳号=True |
| `em_fund_flow.f136` | `zhb.full.amount` | robust_correlation, affine_formula, per_stock_time_series | 96 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | em_fund_flow, zhb | Pearson=0.9835, Spearman=0.9913, LOO稳号=True |
| `ulist239.f297` | `tencent[30]` | robust_correlation, affine_formula, per_stock_time_series | 80 | T:20261105, T:20261106, T:20261109, T:20261110 | tencent, ulist239 | Pearson=1.0, Spearman=0.9686, LOO稳号=True |
| `ulist239.f297` | `ftshare_rest.ts_millis` | robust_correlation, affine_formula, per_stock_time_series | 80 | T:20261105, T:20261106, T:20261109, T:20261110 | ftshare_rest, ulist239 | Pearson=1.0, Spearman=0.9685, LOO稳号=True |
| `event_dc.TOTAL_SHARES` | `ftshare_rest.shares` | robust_correlation, affine_formula, semantic_label | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.CHANGE_RATE` | `ftshare_rest.change_rate` | robust_correlation, affine_formula, semantic_label | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.CHANGE_RATE` | `ftshare_rest.change` | robust_correlation, affine_formula, semantic_label | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | event_dc, ftshare_rest | Pearson=0.999, Spearman=0.9989, LOO稳号=True |
| `event_dc.CHANGE` | `ftshare_rest.change_rate` | robust_correlation, affine_formula, semantic_label | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | event_dc, ftshare_rest | Pearson=0.999, Spearman=0.9989, LOO稳号=True |
| `event_dc.CHANGE` | `ftshare_rest.change` | robust_correlation, affine_formula, semantic_label | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `push2ex.zt_continuous` | `kpl.raw_columns.col_15` | robust_correlation, per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | kpl, push2ex | Pearson=0.6193, Spearman=0.748, LOO稳号=True |
| `push2ex.turnover_rate` | `kpl.turnover_real` | robust_correlation, per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | kpl, push2ex | Pearson=0.8647, Spearman=0.9008, LOO稳号=True |
| `push2ex.turnover_rate` | `kpl.raw_columns.col_14` | robust_correlation, per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | kpl, push2ex | Pearson=0.8647, Spearman=0.9008, LOO稳号=True |
| `push2ex.turnover_rate` | `kpl.raw_columns.col_11` | robust_correlation, per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | kpl, push2ex | Pearson=0.2849, Spearman=0.613, LOO稳号=True |
| `push2ex.turnover_rate` | `kpl.amount` | robust_correlation, per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | kpl, push2ex | Pearson=0.2849, Spearman=0.613, LOO稳号=True |
| `push2ex.total_value` | `kpl.raw_columns.col_13` | robust_correlation, per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | kpl, push2ex | Pearson=0.9635, Spearman=0.8109, LOO稳号=True |
| `push2ex.circulating_value` | `kpl.raw_columns.col_13` | robust_correlation, per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | kpl, push2ex | Pearson=0.9635, Spearman=0.852, LOO稳号=True |
| `kpl.raw_columns.col_10` | `push2ex.amount` | robust_correlation, per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | kpl, push2ex | Pearson=-0.9461, Spearman=-0.946, LOO稳号=True |
| `kpl.raw_columns.col_09` | `push2ex.amount` | robust_correlation, per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | kpl, push2ex | Pearson=0.9623, Spearman=0.9514, LOO稳号=True |
| `kpl.main_sell` | `push2ex.amount` | robust_correlation, per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | kpl, push2ex | Pearson=-0.9461, Spearman=-0.946, LOO稳号=True |
| `kpl.main_buy` | `push2ex.amount` | robust_correlation, per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | kpl, push2ex | Pearson=0.9623, Spearman=0.9514, LOO稳号=True |
| `kpl.raw_columns.col_10` | `kph.turnover` | robust_correlation, per_stock_time_series | 221 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | kph, kpl | Pearson=-0.9369, Spearman=-0.94, LOO稳号=True |
| `kpl.raw_columns.col_09` | `kph.turnover` | robust_correlation, per_stock_time_series | 221 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | kph, kpl | Pearson=0.9624, Spearman=0.9371, LOO稳号=True |
| `kpl.main_sell` | `kph.turnover` | robust_correlation, per_stock_time_series | 221 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | kph, kpl | Pearson=-0.9369, Spearman=-0.94, LOO稳号=True |
| `kpl.main_buy` | `kph.turnover` | robust_correlation, per_stock_time_series | 221 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | kph, kpl | Pearson=0.9624, Spearman=0.9371, LOO稳号=True |
| `push2ex.turnover_rate` | `kph.turnover` | per_stock_time_series, semantic_label | 178 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | kph, push2ex | 逐股相关=0.9891, 方向一致=1.0 |
| `push2ex.first_limit_time` | `kph.limit_time` | per_stock_time_series, semantic_label | 178 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | kph, push2ex | 逐股相关=0.8664, 方向一致=1.0 |
| `ulist239.f63` | `eltdx.shortline.open_volume_ratio` | robust_correlation, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, ulist239 | Pearson=0.3527, Spearman=0.6817, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.open_volume_hand` | robust_correlation, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, ulist239 | Pearson=0.4204, Spearman=0.8185, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.open_prev_amount_ratio` | robust_correlation, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, ulist239 | Pearson=0.3666, Spearman=0.7024, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.open_amount` | robust_correlation, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, ulist239 | Pearson=0.909, Spearman=0.9736, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.open_amount_yuan` | robust_correlation, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, ulist239 | Pearson=0.909, Spearman=0.9736, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.open_amount_raw` | robust_correlation, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, ulist239 | Pearson=0.909, Spearman=0.9736, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.current_hand` | robust_correlation, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, ulist239 | Pearson=0.2661, Spearman=0.7037, LOO稳号=True |
| `ulist239.f149` | `tencent[63]` | robust_correlation, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | tencent, ulist239 | Pearson=0.8884, Spearman=0.8817, LOO稳号=True |
| `ulist239.f149` | `ftshare_rest.change_rate_day5` | robust_correlation, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | ftshare_rest, ulist239 | Pearson=0.8884, Spearman=0.8815, LOO稳号=True |
| `ulist239.f135` | `tencent[76]` | robust_correlation, affine_formula | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | tencent, ulist239 | Pearson=0.9964, Spearman=0.7519, LOO稳号=True |
| `ulist239.f135` | `tencent[73]` | robust_correlation, affine_formula | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | tencent, ulist239 | Pearson=0.9963, Spearman=0.7338, LOO稳号=True |
| `ulist239.f135` | `tencent[72]` | robust_correlation, affine_formula | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | tencent, ulist239 | Pearson=0.9964, Spearman=0.7519, LOO稳号=True |
| `ulist239.f135` | `ftshare_rest.shares` | robust_correlation, affine_formula | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | ftshare_rest, ulist239 | Pearson=0.9963, Spearman=0.7338, LOO稳号=True |
| `ulist239.f135` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | ftshare_rest, ulist239 | Pearson=0.9964, Spearman=0.7519, LOO稳号=True |
| `ulist239.f135` | `eltdx.shortline.free_float_shares` | robust_correlation, affine_formula | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, ulist239 | Pearson=0.9955, Spearman=0.6842, LOO稳号=True |
| `ulist239.f135` | `eltdx.shortline.float_shares` | robust_correlation, affine_formula | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, ulist239 | Pearson=0.9964, Spearman=0.7519, LOO稳号=True |
| `tencent[8]` | `ulist239.f5` | robust_correlation, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | tencent, ulist239 | Pearson=0.0344, Spearman=0.6529, LOO稳号=True |
| `tencent[8]` | `sina[8]` | robust_correlation, per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | sina, tencent | Pearson=0.0344, Spearman=0.6529, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 七、日期与数据质量告警（69）

- 20261017: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261018: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261031: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261101: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261107: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261102/zhb: 采集状态 partial
- 20261102/kph: 来源有效交易日 20261030 不在本轮行情交易日窗口，快照跳过
- 20261102/tdx_f10: 没有可用记录，快照跳过
- 20261102/tdx_f10_more: 没有可用记录，快照跳过
- 20261102/zhb: 来源状态为 partial，样本按部分快照参与
- 20261102/zhb: 来源有效交易日 20261030 不在本轮行情交易日窗口，快照跳过
- 20261103/zhb: 采集状态 partial
- 20261103/tdx_f10: 没有可用记录，快照跳过
- 20261103/tdx_f10_more: 没有可用记录，快照跳过
- 20261103/zhb: 来源状态为 partial，样本按部分快照参与
- 20261104/zhb: 采集状态 partial
- 20261104/tdx: 采集状态 partial
- 20261104/tdx: 来源状态为 partial，样本按部分快照参与
- 20261104/tdx_f10: 没有可用记录，快照跳过
- 20261104/tdx_f10_more: 没有可用记录，快照跳过
- 20261104/zhb: 来源状态为 partial，样本按部分快照参与
- 20261105/zhb: 采集状态 partial
- 20261105/tdx: 采集状态 partial
- 20261105/tdx: 来源状态为 partial，样本按部分快照参与
- 20261105/tdx_f10: 没有可用记录，快照跳过
- 20261105/tdx_f10_more: 没有可用记录，快照跳过
- 20261105/zhb: 来源状态为 partial，样本按部分快照参与
- 20261106/tdx_f10: 没有可用记录，快照跳过
- 20261106/tdx_f10_more: 没有可用记录，快照跳过
- 20261109/zhb: 采集状态 partial
- 20261109/tdx_f10: 没有可用记录，快照跳过
- 20261109/tdx_f10_more: 没有可用记录，快照跳过
- 20261109/zhb: 来源状态为 partial，样本按部分快照参与
- 20261110/zhb: 采集状态 partial
- 20261110/tdx_f10: 没有可用记录，快照跳过
- 20261110/tdx_f10_more: 没有可用记录，快照跳过
- 20261110/zhb: 来源状态为 partial，样本按部分快照参与
- 重复快照 kph/20261106: 选择 20261109，忽略 20261106
- 重复快照 zhb/20261106: 保留 20261106，忽略 20261109
- 日常碰撞排除来源: ftshare=FTShare private hosted MCP
- 20261102/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1793607830671，response_timestamp_date='2026-11-02'（仅响应组装时间，不作为数据日期），记录数=20
- 20261103/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1793713187132，response_timestamp_date='2026-11-03'（仅响应组装时间，不作为数据日期），记录数=20
- 20261104/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1793787977258，response_timestamp_date='2026-11-04'（仅响应组装时间，不作为数据日期），记录数=20
- 20261105/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1793880669692，response_timestamp_date='2026-11-05'（仅响应组装时间，不作为数据日期），记录数=20
- 20261106/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1794104720802，response_timestamp_date='2026-11-08'（仅响应组装时间，不作为数据日期），记录数=20
- 20261109/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1794225380839，response_timestamp_date='2026-11-09'（仅响应组装时间，不作为数据日期），记录数=20
- 20261110/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1794315883118，response_timestamp_date='2026-11-10'（仅响应组装时间，不作为数据日期），记录数=20
- 折叠 85130 条重复字段样本，按快照质量择优；示例: market_sources.code/002029/T:20261102, market_sources.name/002029/T:20261102, market_sources.code/300992/T:20261102, market_sources.name/300992/T:20261102, market_sources.market/300992/T:20261102, market_sources.time/300992/T:20261102, market_sources.change_pct/300992/T:20261102, market_sources.price/300992/T:20261102, market_sources.change_type/300992/T:20261102, market_sources.date/300992/T:20261102
- 20261102/cninfo: 77 条事件记录缺少可解析的自然日，已跳过
- 20261103/cninfo: 75 条事件记录缺少可解析的自然日，已跳过
- 20261104/cninfo: 75 条事件记录缺少可解析的自然日，已跳过
- 20261105/cninfo: 75 条事件记录缺少可解析的自然日，已跳过
- 20261106/cninfo: 76 条事件记录缺少可解析的自然日，已跳过
- 20261109/cninfo: 77 条事件记录缺少可解析的自然日，已跳过
- 20261110/cninfo: 77 条事件记录缺少可解析的自然日，已跳过
- 61 条 verified 源字段来源未确认独立性，作为已知字段跳过重解但不作锚
- 31 条官方契约语义锚可参与对撞；底层来源独立性未确认，强候选标为 L1-C
- 70 条 verified 源字段映射到重复运行时身份；相关运行时路径已退出破解目标，但身份消歧前不作锚
- 190 条 verified 源字段元数据未达锚点条件（含义冲突 12 条、缺义/占位 189 条、单位冲突 4 条）；已退出破解目标，但保留在元数据补全队列且不作碰撞锚
- 东财-push2(stock/get) 行时间戳日期见证：确认 140 行，日期冲突 0 行，无效时间戳 0 行
- 东财-ulist239(np/get) 行时间戳日期见证：确认 140 行，日期冲突 0 行，无效时间戳 0 行
- 跨源值日期见证 tdx.quote_raw.bid1_vol <- tencent[10]: 138/138 精确，137/137 非零精确，7 个交易日满足日阈值；未达到门槛
- 跨源值日期见证 tdx.quote_raw.ask1_vol <- tencent[20]: 138/138 精确，133/133 非零精确，7 个交易日满足日阈值；未达到门槛
- 字段时效分类: daily_market=37, intraday_sensitive=23, periodic_or_event=3, slow_changing=5, static_reference=7, unclassified=1223；未分类字段按来源日期严格门控
- 对撞模式：verified_anchor_only；待破解字段=204，verified 锚资格字段=1183，verified 目标排除身份=1381，可用独立锚=1098，官方契约字段=339，L1-C 契约锚=31，right 字段=483
- 主动方法候选共 2291 条；全局保留 500 条，另按目标字段补充 84 条字段前沿候选；完整方法明细保存在 JSON `method_candidate_inventory`
- 跳过同一来源家族字段对：16766
- 跳过来源独立性未确认的字段对：32518
- 官方契约锚参与字段对撞 4167 对；底层来源独立性未确认，强匹配单列 L1-C

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

策略状态：`ok`；逐源分类字段 75，保守默认未分类字段 1223。L1/L1-C 日期证据：来源日期已确认 0 条，跨源值见证推断 0 条，仅语义证据且日期未确认 0 条，其他日期未确认 0 条。

| 日期见证关系 | 结果 | 交易日 | 精确样本 | 非零精确样本 | 不同非零值 | 证据 SHA-256 |
|:--|:--|--:|--:|--:|--:|:--|
| `tdx.quote_raw.ask1_vol <- tencent[20]` | thresholds_not_met | 7 | 138/138 | 133/133 | 110 | `9f488224d9a95673bf751451c47a3fd1ae05090b51cf090dc014d66818252d69` |
| `tdx.quote_raw.bid1_vol <- tencent[10]` | thresholds_not_met | 7 | 138/138 | 137/137 | 113 | `9f488224d9a95673bf751451c47a3fd1ae05090b51cf090dc014d66818252d69` |

_本轮 L1/L1-C 没有仅凭静态或缓变字段、且来源日期未确认的关系。_

## 来源字段覆盖与碰撞参与

_窗口字段值样本是经日期筛选、重复折叠和快照择优后载入的非空值；右侧比较次数另受字段类型及来源规则筛选。官方契约字段须有逐字段审定证据，契约语义本身不证明底层数据来源独立。_

| 来源 | 已确认字段 | 契约已确认 | 契约锚 | 独立锚 | L1-C 锚 | 窗口字段 / 字段值样本 / 交易日 |
|:--|--:|--:|--:|--:|--:|--:|
| axdata | 34 | 0 | 0 | 0 | 0 | 34 / 3740 / 7 |
| clist | 20 | 0 | 0 | 20 | 0 | 33 / 50169 / 7 |
| cls | 4 | 0 | 0 | 4 | 0 | 5 / 1250 / 0 |
| datacenter | 41 | 0 | 0 | 41 | 0 | 0 / 0 / 0 |
| eltdx | 177 | 108 | 108 | 177 | 0 | 112 / 7678 / 7 |
| em_fund_flow | 0 | 0 | 0 | 0 | 0 | 15 / 2100 / 7 |
| em_hot | 39 | 0 | 0 | 39 | 0 | 0 / 0 / 0 |
| em_kline_f61 | 10 | 0 | 0 | 10 | 0 | 2 / 280 / 7 |
| etf | 0 | 0 | 0 | 0 | 0 | 9 / 81942 / 7 |
| event_dc | 0 | 0 | 0 | 0 | 0 | 148 / 216031 / 7 |
| exchange | 4 | 0 | 0 | 4 | 0 | 0 / 0 / 0 |
| ftshare | 6 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| ftshare_rest | 31 | 31 | 31 | 0 | 31 | 32 / 4445 / 7 |
| fuyao | 89 | 75 | 75 | 89 | 0 | 20 / 2800 / 7 |
| kph | 12 | 0 | 0 | 12 | 0 | 15 / 3315 / 5 |
| kpl | 11 | 0 | 0 | 11 | 0 | 28 / 18836 / 7 |
| market_sources | 14 | 0 | 0 | 0 | 0 | 72 / 62684 / 7 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 2 / 104 / 0 |
| push2 | 51 | 0 | 0 | 51 | 0 | 114 / 15960 / 7 |
| push2ex | 24 | 0 | 0 | 24 | 0 | 16 / 11696 / 7 |
| reports | 31 | 0 | 0 | 31 | 0 | 49 / 343 / 0 |
| research_sina | 0 | 0 | 0 | 0 | 0 | 6 / 1404 / 0 |
| sina | 27 | 0 | 0 | 27 | 0 | 39 / 4830 / 7 |
| sina_extended | 3 | 3 | 3 | 3 | 0 | 4 / 560 / 7 |
| slist | 5 | 0 | 0 | 5 | 0 | 1 / 140 / 7 |
| sse_e_interaction | 0 | 0 | 0 | 0 | 0 | 8 / 400 / 0 |
| st_list | 0 | 0 | 0 | 0 | 0 | 6 / 13808 / 7 |
| tdx | 217 | 100 | 100 | 217 | 0 | 58 / 8832 / 7 |
| tencent | 76 | 0 | 0 | 76 | 0 | 88 / 12306 / 7 |
| ulist239 | 52 | 0 | 0 | 52 | 0 | 240 / 33540 / 7 |
| zhb | 205 | 22 | 22 | 205 | 0 | 130 / 11065 / 5 |

| 来源 | 破解目标 | 比较字段 | 作目标比较 | 作右侧比较 | L1-C 锚比较 | L1 / L1-C / L4 关系 | 方法候选涉及 |
|:--|--:|--:|--:|--:|--:|--:|--:|
| axdata | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| clist | 10 | 17 | 3066 | 1071 | 0 | 0 / 0 / 0 | 0 |
| cls | 2 | 0 | 483 | 0 | 0 | 0 / 0 / 0 | 0 |
| datacenter | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| eltdx | 21 | 52 | 5480 | 3956 | 0 | 0 / 0 / 2 | 200 |
| em_fund_flow | 5 | 0 | 1695 | 0 | 0 | 0 / 0 / 0 | 263 |
| em_hot | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| em_kline_f61 | 1 | 0 | 339 | 0 | 0 | 0 / 0 / 0 | 12 |
| etf | 4 | 0 | 29 | 0 | 0 | 0 / 0 / 0 | 0 |
| event_dc | 61 | 0 | 1235 | 0 | 0 | 0 / 0 / 0 | 243 |
| exchange | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare_rest | 1 | 25 | 23 | 4167 | 4167 | 0 / 0 / 0 | 399 |
| fuyao | 0 | 14 | 0 | 1694 | 0 | 0 / 0 / 0 | 72 |
| kph | 1 | 9 | 450 | 972 | 0 | 0 / 0 / 4 | 39 |
| kpl | 10 | 11 | 3994 | 1904 | 0 | 0 / 0 / 6 | 51 |
| market_sources | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| push2 | 13 | 49 | 3111 | 2855 | 0 | 0 / 0 / 5 | 840 |
| push2ex | 7 | 5 | 2373 | 315 | 0 | 0 / 0 / 6 | 48 |
| reports | 8 | 7 | 2388 | 325 | 0 | 0 / 0 / 0 | 0 |
| research_sina | 2 | 0 | 454 | 0 | 0 | 0 / 0 / 0 | 0 |
| sina | 6 | 26 | 2592 | 2655 | 0 | 0 / 0 / 0 | 268 |
| sina_extended | 0 | 3 | 0 | 342 | 0 | 0 / 0 / 0 | 18 |
| slist | 1 | 0 | 339 | 0 | 0 | 0 / 0 / 0 | 6 |
| sse_e_interaction | 2 | 0 | 25 | 0 | 0 | 0 / 0 / 0 | 0 |
| st_list | 3 | 0 | 48 | 0 | 0 | 0 / 0 / 0 | 0 |
| tdx | 3 | 49 | 819 | 4565 | 0 | 0 / 0 / 4 | 385 |
| tencent | 8 | 70 | 2765 | 7568 | 0 | 0 / 0 / 2 | 527 |
| ulist239 | 20 | 51 | 6456 | 2981 | 0 | 0 / 0 / 13 | 449 |
| zhb | 15 | 83 | 4095 | 6889 | 0 | 0 / 0 / 10 | 762 |

## AxData 每日接口核验

> 此处汇总采集目录已保存的本地证据，不发起网络请求、不改变注册表状态；AxData 是多源框架，不作为独立字段锚。

### AxData

窗口内有 7 个唯一数据日的轮验记录；重复目录合并 0 条。
静态接口队列：257 个接口，3343 个字段出现项，低于 E3 的字段出现项 3343；当前主动探针白名单 `tencent_realtime_snapshot`。
静态候选策略：static review only until route, parameters, date basis, and request safety are approved。

| 数据日 | 轮验状态 | 探针状态 / 请求数 | 来源身份状态 | 短线配对 | KPH/KPL 配对 | 证据文件 |
|:--|:--|:--|:--|--:|--:|:--|
| 20261102 | sampled | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261103 | sampled | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261104 | sampled | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261105 | sampled | sampled / 1 (字段相同/不同 0/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261106 | already_recorded | sampled / 1 (字段相同/不同 0/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | 30 | full |
| 20261109 | already_recorded | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261110 | sampled | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |

被动逐字段比较中的差异计数（跨本窗口唯一数据日累加，不含原始值）：

| 比较路径 | 相同 | 不同 | 缺失/双方空值 |
|:--|--:|--:|--:|
| `axdata_shortline_vs_eltdx:alignment_status` | 0 | 140 | 0 |
| `axdata_shortline_vs_eltdx:beta_60d` | 0 | 140 | 0 |
| `axdata_shortline_vs_eltdx:code` | 0 | 140 | 0 |
| `axdata_shortline_vs_eltdx:full_code` | 0 | 140 | 0 |
| `axdata_shortline_vs_eltdx:instrument_id` | 0 | 140 | 0 |
| `axdata_shortline_vs_eltdx:limit_status` | 0 | 140 | 0 |
| `axdata_shortline_vs_eltdx:market_id` | 0 | 140 | 0 |
| `axdata_shortline_vs_eltdx:opening_rush` | 0 | 140 | 0 |
| `axdata_shortline_vs_eltdx:pe_ttm` | 0 | 140 | 0 |
| `axdata_shortline_vs_eltdx:previous_trade_date` | 0 | 140 | 0 |
| `axdata_shortline_vs_eltdx:symbol` | 0 | 140 | 0 |
| `axdata_shortline_vs_eltdx:target_trade_date` | 0 | 140 | 0 |
| `axdata_shortline_vs_eltdx:tdx_code` | 0 | 140 | 0 |
| `axdata_shortline_vs_eltdx:open_amount` | 26 | 114 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_hand` | 26 | 114 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_ratio` | 27 | 113 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_amount_ratio` | 35 | 105 | 0 |
| `axdata_shortline_vs_eltdx:auction_prev_volume_ratio` | 39 | 100 | 1 |
| `axdata_shortline_vs_eltdx:open_turnover_z` | 75 | 65 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_seal_ratio` | 1 | 6 | 133 |
| `axdata_shortline_vs_eltdx:ladder_level` | 0 | 5 | 135 |
| `axdata_shortline_vs_eltdx:limit_board_text` | 15 | 5 | 120 |

## 字母字段名语义提示（仅候选）

窗口内观察到 141 条需审阅的字母字段路径：含词义线索 37 条，仅拆词 104 条。
完整逐条记录保存在碰撞 JSON；名称线索清单：`docs/field_verification/20261014/20261014_alphabetic_field_name_inventory.csv`。
> 拼音、英文、缩写和混合拆词只用于检索候选；必须结合原始值、接口定义和独立来源复核，不得据此定案或改写主字典。

| 逐源字段路径 | 状态/审阅范围 | 名称形式与拆词 | 词义线索（非释义） | 样本日期 |
|:--|:--|:--|:--|:--|
| `市场源(market_sources)::change_type` | unverified / unverified_semantics | snake_case_or_mixed: change type | 变化/涨跌 + 类型 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::first_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: first limit time | 首次/第一 + 涨跌停限制 + 时间 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::last_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: last limit time | 最近/上一期 + 涨跌停限制 + 时间 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::name` | unverified / unverified_semantics | recognized_english_word_candidate: name | 名称 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::total_value` | unverified / unverified_semantics | snake_case_or_mixed: total value | 总 + 值 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::limit_count` | verified / verified_metadata_gap | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::limit_time` | unverified / unverified_semantics | snake_case_or_mixed: limit time | 涨跌停限制 + 时间 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::plate_limit_up_count` | verified / verified_metadata_gap | snake_case_or_mixed: plate limit up count | 涨跌停限制 + 上/涨 + 数量/次数 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `财联社(cls)::time` | unverified / unverified_semantics | recognized_english_word_candidate: time | 时间 | C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110 |
| `同花顺-fuyao::snapshot.open_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot open price | 开盘 + 价格 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::changqifuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: changqifuzhai | 长期负债 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::cunhuo` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: cunhuo | 存货 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::eps` | unverified / unverified_semantics | recognized_english_word_candidate: eps | 每股收益 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::fajirenfarengu` | unverified / unverified_semantics | recognized_pinyin_phrase_candidate: fajirenfarengu | 疑似 faqirenfarengu 的拼写变体；含义未证实 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::gudongrenshu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: gudongrenshu | 股东人数 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::ipodate` | unverified / unverified_semantics | recognized_english_phrase_candidate: ipodate | IPO/上市日期（字段语境候选） | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::jinglirun` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jinglirun | 净利润 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::jingyingxianjinliu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingyingxianjinliu | 经营现金流 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::jingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingzichan | 净资产 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::liudongfuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: liudongfuzhai | 流动负债 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::meigujingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: meigujingzichan | 每股净资产 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::yingshouzhangkuan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: yingshouzhangkuan | 应收账款 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::zhuyingshouru` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zhuyingshouru | 主营收入 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::zibengongjijin` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zibengongjijin | 资本公积金 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::zongzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongzichan | 总资产 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX-eltdx(适配层)::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `reports::actualLastTwoYearEps` | unverified / unverified_semantics | camel_case_or_mixed: actual Last Two Year Eps | 最近/上一期 + 每股收益 | C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::actualLastYearEps` | unverified / unverified_semantics | camel_case_or_mixed: actual Last Year Eps | 最近/上一期 + 每股收益 | C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::count` | verified / verified_metadata_gap | recognized_english_word_candidate: count | 数量/次数 | C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::lastEmRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Code | 最近/上一期 + 代码 | C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::lastEmRatingName` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Name | 最近/上一期 + 名称 | C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::lastEmRatingValue` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Value | 最近/上一期 + 值 | C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::predictLastYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Eps | 最近/上一期 + 每股收益 | C:20261104, C:20261105, C:20261108, C:20261110 |
| `reports::predictLastYearPe` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Pe | 最近/上一期 + 市盈率 | C:20261104, C:20261105, C:20261108, C:20261110 |
| `东财-push2ex::broken_count` | unverified / unverified_semantics | snake_case_or_mixed: broken count | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::circulating_value` | unverified / unverified_semantics | snake_case_or_mixed: circulating value | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::sector` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: sector | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::turnover_rate` | unverified / unverified_semantics | snake_case_or_mixed: turnover rate | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::zt_continuous` | unverified / unverified_semantics | snake_case_or_mixed: zt continuous | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `东财-push2ex::zt_days` | unverified / unverified_semantics | snake_case_or_mixed: zt days | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `开盘啦(kpl_limit_up_detail)::raw_columns.col_19` | verified / verified_metadata_gap | runtime_tokenization_only: col 19 | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::one_word` | unverified / unverified_semantics | snake_case_or_mixed: one word | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::plate_amount` | verified / verified_metadata_gap | snake_case_or_mixed: plate amount | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::plate_code` | verified / verified_metadata_gap | snake_case_or_mixed: plate code | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::plate_name` | verified / verified_metadata_gap | snake_case_or_mixed: plate name | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::popular` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: popular | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `财联社(cls)::content` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: content | — | C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110 |
| `财联社(cls)::level` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: level | — | C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110 |
| `财联社(cls)::reading_num` | unverified / unverified_semantics | snake_case_or_mixed: reading num | — | C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110 |
| `财联社(cls)::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110 |
| `开盘红::industry_limit_up_count` | unverified / unverified_semantics | runtime_tokenization_only: industry limit up count | — | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 |
| `FTShare REST::amplitude` | verified / verified_metadata_gap | runtime_tokenization_only: amplitude | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::avg` | verified / verified_metadata_gap | runtime_tokenization_only: avg | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::bid_ask_ratio` | verified / verified_metadata_gap | runtime_tokenization_only: bid ask ratio | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::board` | verified / verified_metadata_gap | runtime_tokenization_only: board | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::listing_date` | verified / verified_metadata_gap | runtime_tokenization_only: listing date | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::name` | verified / verified_metadata_gap | runtime_tokenization_only: name | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::st` | verified / verified_metadata_gap | runtime_tokenization_only: st | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::status` | verified / verified_metadata_gap | runtime_tokenization_only: status | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::symbol` | verified / verified_metadata_gap | runtime_tokenization_only: symbol | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::symbol_id` | unverified / unverified_semantics | runtime_tokenization_only: symbol id | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::turnover_rate` | verified / verified_metadata_gap | runtime_tokenization_only: turnover rate | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `同花顺-fuyao::fin_report` | unverified / unverified_semantics | snake_case_or_mixed: fin report | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `同花顺-fuyao::snapshot.prev_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot prev price | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::big_order_300w_net` | unverified / unverified_semantics | runtime_tokenization_only: big order 300 w net | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::institution_add` | unverified / unverified_semantics | runtime_tokenization_only: institution add | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::main_inflow` | unverified / unverified_semantics | snake_case_or_mixed: main inflow | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::pe_next` | unverified / unverified_semantics | runtime_tokenization_only: pe next | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::pe_now` | unverified / unverified_semantics | runtime_tokenization_only: pe now | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::strength` | unverified / unverified_semantics | runtime_tokenization_only: strength | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `市场源(market_sources)::total_value` | unverified / unverified_semantics | runtime_tokenization_only: total value | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `新浪(扩展API)::opendate` | conflict / unverified_semantics | unsegmented_latin_pinyin_or_word: opendate | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::baoliu2` | unverified / unverified_semantics | mixed_alphanumeric: baoliu 2 | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::ipo_date` | verified / verified_metadata_gap | snake_case_or_mixed: ipo date | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::updated_date` | verified / verified_metadata_gap | snake_case_or_mixed: updated date | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::updateddate` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: updateddate | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX(双命名源)::zhuyinglyrun` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: zhuyinglyrun | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `FTShare REST::pe_ttm` | verified / verified_metadata_gap | runtime_tokenization_only: pe ttm | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `ZHB-tdxstat::stat.unknown_2` | verified / verified_metadata_gap | snake_case_or_mixed: stat unknown 2 | — | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 |
| `ZHB-tdxstat::stat.unknown_26` | verified / verified_metadata_gap | snake_case_or_mixed: stat unknown 26 | — | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 |
| `市场源(market_sources)::rank` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: rank | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX-eltdx(适配层)::trade_date` | unverified / unverified_semantics | snake_case_or_mixed: trade date | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX-eltdx(适配层)::adjust_mode` | unverified / unverified_semantics | snake_case_or_mixed: adjust mode | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX-eltdx(适配层)::adjust_mode_raw` | unverified / unverified_semantics | snake_case_or_mixed: adjust mode raw | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX-eltdx(适配层)::anchor_date_raw` | unverified / unverified_semantics | snake_case_or_mixed: anchor date raw | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX-eltdx(适配层)::category` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: category | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX-eltdx(适配层)::exchange` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: exchange | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX-eltdx(适配层)::market_id` | unverified / unverified_semantics | snake_case_or_mixed: market id | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX-eltdx(适配层)::period_name` | unverified / unverified_semantics | snake_case_or_mixed: period name | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX-eltdx(适配层)::period_param_raw` | unverified / unverified_semantics | snake_case_or_mixed: period param raw | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX-eltdx(适配层)::period_raw` | unverified / unverified_semantics | snake_case_or_mixed: period raw | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX-eltdx(适配层)::raw_payload` | unverified / unverified_semantics | snake_case_or_mixed: raw payload | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX-eltdx(适配层)::request_count` | unverified / unverified_semantics | snake_case_or_mixed: request count | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX-eltdx(适配层)::sort_by` | unverified / unverified_semantics | snake_case_or_mixed: sort by | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |
| `TDX-eltdx(适配层)::start` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: start | — | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110 |

Markdown 显示前 100 条；其余 41 条完整保留在 JSON。

## 探索候选持续跟踪

研究台账：`collision_research_state.json.gz`；累计历史跟踪候选对 2736，本报告候选对 603，历史复现 408，新发现 0。
台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，不会自动改变字段状态、碰撞锚或主字典。新报告只将 `actionable_L1`、L4 和主动方法候选写入待研究队列；已登记关系的复验单独展示，历史跟踪记录不会被删除。

## 候选覆盖、公式与下一步采样

本节用于定位证据缺口和安排后续取样。相关性、公式与样本优先级均为探索候选；不会改变 L1/L1-U 门槛、来源独立性或主字典。

- 未知目标 204 个；其中有方法候选 103 个、无候选 101 个；多候选目标 97 个。
- 方法候选生成 2291 条；全局详细项保留 500/500，另按目标字段保留 84 条；完整明细 2291 条在 JSON `method_candidate_inventory`；未归档明细 0 条。
- 字段覆盖详情：available；覆盖身份 1971，读取 7 份本地索引。

### 优先处理字段

| 未知字段 | 当前诊断 | 独立对比/候选数 | 独立锚家族/本源日期 | 建议复核股票 | 最强候选线索 |
|:--|:--|--:|:--|:--|:--|
| `push2.f126` | 存在多个候选，需区分 | 316 / 103 | 6 家族 / 316 对 / 本源 0 日 | 600519 (38.769539) | tencent[64] (robust_correlation,per_stock_time_series); tencent[53] (robust_correlation,per_stock_time_series) |
| `push2.f160` | 存在多个候选，需区分 | 316 / 97 | 6 家族 / 316 对 / 本源 0 日 | 600519 (48.955078) | tencent[68] (robust_correlation,affine_formula); tdx.finance_info.meigujingzichan (robust_correlation,affine_formula) |
| `push2.f108` | 存在多个候选，需区分 | 316 / 94 | 6 家族 / 316 对 / 本源 0 日 | 600519 (23.771902) | tencent[9] (robust_correlation,affine_formula); tencent[68] (robust_correlation,affine_formula) |
| `push2.f176` | 存在多个候选，需区分 | 316 / 89 | 6 家族 / 316 对 / 本源 0 日 | 600519 (13.975004) | fuyao.valuation.ps_ttm (robust_correlation,affine_formula,per_stock_time_series); tencent[46] (robust_correlation,per_stock_time_series) |
| `em_fund_flow.f135` | 存在多个候选，需区分 | 316 / 87 | 6 家族 / 316 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat2.amount (robust_correlation,affine_formula,per_stock_time_series); zhb.full.amount (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f135` | 存在多个候选，需区分 | 316 / 87 | 6 家族 / 316 对 / 本源 0 日 | 600519 (6.413513) | zhb.stat2.amount (robust_correlation,affine_formula,per_stock_time_series); zhb.full.amount (robust_correlation,affine_formula,per_stock_time_series) |
| `tdx.finance_info.eps` | 存在多个候选，需区分 | 250 / 84 | 6 家族 / 250 对 / 本源 0 日 | no_shared_stock_holdout | ulist239.f2 (robust_correlation,affine_formula); ulist239.f18 (robust_correlation,affine_formula) |
| `ulist239.f63` | 存在多个候选，需区分 | 316 / 81 | 6 家族 / 316 对 / 本源 0 日 | no_shared_stock_holdout | eltdx.shortline.open_volume_ratio (robust_correlation,per_stock_time_series); eltdx.shortline.open_volume_hand (robust_correlation,per_stock_time_series) |
| `em_fund_flow.f136` | 存在多个候选，需区分 | 316 / 74 | 6 家族 / 316 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f136` | 存在多个候选，需区分 | 316 / 74 | 6 家族 / 316 对 / 本源 0 日 | candidates_converge_on_existing_samples | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[16]` | 存在多个候选，需区分 | 409 / 64 | 6 家族 / 409 对 / 本源 7 日 | 600519 (14.184271) | tencent[16] (robust_correlation,affine_formula,per_stock_time_series); ulist239.f2 (robust_correlation) |
| `push2.f49` | 存在多个候选，需区分 | 316 / 60 | 6 家族 / 316 对 / 本源 0 日 | candidates_converge_on_existing_samples | sina[8] (robust_correlation,affine_formula,per_stock_time_series); fuyao.snapshot.volume (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.change_20k_bar` | 存在多个候选，需区分 | 250 / 60 | 6 家族 / 250 对 / 本源 0 日 | 002242 (4.118631) | ulist239.f21 (robust_correlation,per_stock_time_series); ulist239.f20 (robust_correlation,per_stock_time_series) |
| `push2.f161` | 存在多个候选，需区分 | 316 / 59 | 6 家族 / 316 对 / 本源 0 日 | candidates_converge_on_existing_samples | sina[8] (robust_correlation,affine_formula,per_stock_time_series); fuyao.snapshot.volume (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.change_60k_bar` | 存在多个候选，需区分 | 250 / 53 | 6 家族 / 250 对 / 本源 0 日 | 600519 (5.354133) | tencent[71] (robust_correlation,affine_formula,per_stock_time_series); push2.f121 (robust_correlation,affine_formula,per_stock_time_series) |
| `em_fund_flow.f138` | 存在多个候选，需区分 | 316 / 52 | 6 家族 / 316 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat2.amount (robust_correlation,per_stock_time_series); zhb.full.amount (robust_correlation,per_stock_time_series) |
| `em_fund_flow.f139` | 存在多个候选，需区分 | 316 / 50 | 6 家族 / 316 对 / 本源 0 日 | no_shared_stock_holdout | tencent[70] (robust_correlation); tencent[58] (robust_correlation) |
| `ulist239.f149` | 存在多个候选，需区分 | 316 / 42 | 6 家族 / 316 对 / 本源 0 日 | 000678 (3.155604) | tencent[63] (robust_correlation,per_stock_time_series); ftshare_rest.change_rate_day5 (robust_correlation,per_stock_time_series) |
| `ulist239.f297` | 存在多个候选，需区分 | 316 / 41 | 6 家族 / 316 对 / 本源 0 日 | candidates_converge_on_existing_samples | tencent[30] (robust_correlation,affine_formula,per_stock_time_series); ftshare_rest.ts_millis (robust_correlation,affine_formula,per_stock_time_series) |
| `ulist239.f135` | 存在多个候选，需区分 | 316 / 40 | 6 家族 / 316 对 / 本源 0 日 | 601288 (4.099191) | tencent[76] (robust_correlation,affine_formula); tencent[73] (robust_correlation,affine_formula) |
| `tencent[7]` | 存在多个候选，需区分 | 369 / 37 | 6 家族 / 369 对 / 本源 7 日 | candidates_converge_on_existing_samples | ulist239.f5 (robust_correlation,per_stock_time_series); sina[8] (robust_correlation,per_stock_time_series) |
| `tencent[8]` | 存在多个候选，需区分 | 369 / 34 | 6 家族 / 369 对 / 本源 7 日 | candidates_converge_on_existing_samples | ulist239.f5 (robust_correlation,per_stock_time_series); sina[8] (robust_correlation,per_stock_time_series) |
| `push2.f103` | 存在多个候选，需区分 | 316 / 33 | 6 家族 / 316 对 / 本源 0 日 | no_shared_stock_holdout | tdx.finance_info.zongzichan (robust_correlation,affine_formula); tdx.finance_info.yingyelirun (robust_correlation,affine_formula) |
| `zhb.full.cash_reserve_wan` | 存在多个候选，需区分 | 250 / 32 | 6 家族 / 250 对 / 本源 0 日 | 601288 (475.955223) | ulist239.f50 (robust_correlation,affine_formula); ulist239.f47 (robust_correlation,affine_formula) |
| `zhb.full.pre_receive_zj` | 存在多个候选，需区分 | 250 / 32 | 6 家族 / 250 对 / 本源 0 日 | 600519 (30.874813) | ulist239.f6 (robust_correlation); ulist239.f55 (robust_correlation) |
| `tdx.finance_info.zhuyinglyrun` | 存在多个候选，需区分 | 250 / 25 | 6 家族 / 250 对 / 本源 0 日 | no_shared_stock_holdout | ulist239.f55 (robust_correlation); ulist239.f52 (robust_correlation) |
| `zhb.full.free_ltgb` | 存在多个候选，需区分 | 250 / 25 | 6 家族 / 250 对 / 本源 0 日 | 601288 (260.901208) | ulist239.f60 (robust_correlation,affine_formula); ulist239.f50 (robust_correlation,affine_formula) |
| `sina[18]` | 存在多个候选，需区分 | 409 / 24 | 6 家族 / 409 对 / 本源 7 日 | 600519 (12.810012) | tencent[18] (robust_correlation,affine_formula,per_stock_time_series); ulist239.f2 (robust_correlation) |
| `zhb.full.unknown_2` | 存在多个候选，需区分 | 250 / 22 | 6 家族 / 250 对 / 本源 0 日 | 600519 (4.866276) | ulist239.f6 (robust_correlation); ulist239.f21 (robust_correlation) |
| `tdx.finance_info.fajirenfarengu` | 存在多个候选，需区分 | 250 / 21 | 6 家族 / 250 对 / 本源 0 日 | no_shared_stock_holdout | ulist239.f47 (robust_correlation,affine_formula); ulist239.f45 (robust_correlation,affine_formula) |
| `ulist239.f190` | 存在多个候选，需区分 | 316 / 21 | 6 家族 / 316 对 / 本源 0 日 | 600675 (0.075587) | tdx.finance_info.hgu (robust_correlation,affine_formula); zhb.stat.other_qy_jzc (robust_correlation,affine_formula) |
| `ulist239.f192` | 存在多个候选，需区分 | 316 / 21 | 6 家族 / 316 对 / 本源 0 日 | 600675 (0.075587) | tdx.finance_info.hgu (robust_correlation,affine_formula); zhb.stat.other_qy_jzc (robust_correlation,affine_formula) |
| `zhb.full.rd_input_fee` | 存在多个候选，需区分 | 250 / 21 | 6 家族 / 250 对 / 本源 0 日 | 600519 (26.432849) | ulist239.f52 (robust_correlation,affine_formula); ulist239.f55 (robust_correlation) |
| `ulist239.f139` | 存在多个候选，需区分 | 316 / 18 | 6 家族 / 316 对 / 本源 0 日 | 601288 (75.334687) | tencent[76] (robust_correlation); tencent[73] (robust_correlation) |
| `zhb.full.net_profit_kcf` | 存在多个候选，需区分 | 250 / 17 | 6 家族 / 250 对 / 本源 0 日 | 601288 (24.023299) | ulist239.f47 (robust_correlation,affine_formula); ulist239.f45 (robust_correlation,affine_formula) |
| `zhb.tipinfo.unlock_shares_wan` | 存在多个候选，需区分 | 250 / 16 | 6 家族 / 250 对 / 本源 0 日 | 601288 (428.777126) | ulist239.f60 (affine_formula); ulist239.f50 (affine_formula) |
| `sina[28]` | 存在多个候选，需区分 | 409 / 15 | 6 家族 / 409 对 / 本源 7 日 | 600519 (14.149385) | tencent[68] (robust_correlation); tencent[67] (robust_correlation) |
| `ulist239.f127` | 存在多个候选，需区分 | 316 / 15 | 6 家族 / 316 对 / 本源 0 日 | 300788 (2.694413) | zhb.stat2.change_mtd (robust_correlation,per_stock_time_series); zhb.stat.change_pct_2d (robust_correlation,per_stock_time_series) |
| `tencent[22]` | 存在多个候选，需区分 | 369 / 13 | 6 家族 / 369 对 / 本源 7 日 | 600519 (10.124568) | sina[22] (robust_correlation,affine_formula,per_stock_time_series); sina[20] (robust_correlation) |
| `em_kline_f61.dktotal` | 存在多个候选，需区分 | 316 / 12 | 6 家族 / 316 对 / 本源 0 日 | no_shared_stock_holdout | tencent[30] (per_stock_time_series); tencent[2] (robust_correlation) |
| `sina[24]` | 存在多个候选，需区分 | 409 / 12 | 6 家族 / 409 对 / 本源 7 日 | 600519 (13.193527) | tencent[68] (robust_correlation); tencent[67] (robust_correlation) |
| `ulist239.f148` | 存在多个候选，需区分 | 316 / 12 | 6 家族 / 316 对 / 本源 0 日 | 600825 (1.210028) | tencent[71] (robust_correlation); ftshare_rest.change_rate_day60 (robust_correlation) |
| `sina[14]` | 存在多个候选，需区分 | 409 / 11 | 6 家族 / 409 对 / 本源 7 日 | 600519 (16.259662) | tencent[14] (robust_correlation,affine_formula,per_stock_time_series); tencent[68] (robust_correlation) |
| `tencent[28]` | 存在多个候选，需区分 | 369 / 11 | 6 家族 / 369 对 / 本源 7 日 | 600519 (14.570431) | sina[22] (robust_correlation); sina[20] (robust_correlation) |
| `zhb.full.other_qy_jzc` | 存在多个候选，需区分 | 250 / 11 | 6 家族 / 250 对 / 本源 0 日 | 601288 (49.121634) | ulist239.f60 (affine_formula); ulist239.f50 (affine_formula) |
| `event_dc.AMPLITUDE` | 存在多个候选，需区分 | 0 / 11 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.CLOSE_PRICE` | 存在多个候选，需区分 | 0 / 11 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.OPEN_PRICE` | 存在多个候选，需区分 | 0 / 11 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.TOTAL_CHANGE` | 存在多个候选，需区分 | 0 / 11 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `sina[26]` | 存在多个候选，需区分 | 409 / 10 | 6 家族 / 409 对 / 本源 7 日 | 600519 (12.267045) | zhb.stat2.low_52w (robust_correlation,per_stock_time_series); zhb.full.low_52w (robust_correlation,per_stock_time_series) |

_此表显示优先级最高的 50 / 共 204 个目标；完整清单见 JSON。_


### 舍入近似数值线索（仅研究，不算 L1/L1-U；0 组）

近似窗口只用于提示复核：需核对双方原始单位、展示精度和来源口径；不得把该命中率当作字段语义结论或注册表写回依据。完整明细在 JSON `candidate_triage.approximate_matches`。

_本轮没有达到近似筛查门槛的关系。_


### 补足全局截断的字段候选（84）

| 未知字段 | 候选字段 | 方法 | 样本 | 日期 | 来源 |
|:--|:--|:--|--:|:--|:--|
| `em_fund_flow.f138` | `tencent[70]` | robust_correlation | 113 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | em_fund_flow, tencent |
| `em_fund_flow.f139` | `tencent[70]` | robust_correlation | 118 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | em_fund_flow, tencent |
| `em_kline_f61.dktotal` | `tencent[30]` | per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | em_kline_f61, tencent |
| `event_dc.AMPLITUDE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.CHANGE` | `ftshare_rest.prev_close` | robust_correlation | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.CHANGE_RATE` | `ftshare_rest.prev_close` | robust_correlation | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.CLOSE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.EACHBALLOT_SHARES` | `ftshare_rest.shares` | semantic_label | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.INDUSTRY_PE` | `ftshare_rest.ts_millis` | robust_correlation | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.INDUSTRY_PE_NEW` | `ftshare_rest.ts_millis` | robust_correlation | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.IPO_YIELD` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.ISSUE_NUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.ISSUE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.LATELY_PRICE` | `ftshare_rest.close` | robust_correlation, affine_formula | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.LD_AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.LD_CLOSE_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.LD_HIGH_CHANG` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.LD_OPEN_PREMIUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.LIMIT_UP_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.MZYQ_PAY_FUND` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.OD_HIGH_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.OPEN_AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.OPEN_PRICE` | `ftshare_rest.volume` | robust_correlation | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.PROFIT` | `ftshare_rest.volume` | robust_correlation | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.TCHANGE_RATE` | `ftshare_rest.volume` | robust_correlation | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.TNEW_PRICE` | `ftshare_rest.low` | robust_correlation | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.TOTAL_CHANGE` | `ftshare_rest.volume` | robust_correlation | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.TOTAL_ISSUE_NUM` | `ftshare_rest.volume` | robust_correlation | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.TOTAL_SHARES` | `ftshare_rest.volume` | robust_correlation | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.TURNOVERRATE` | `ftshare_rest.volume` | robust_correlation | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `event_dc.fetched_at` | `ftshare_rest.amplitude` | robust_correlation | 14 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | event_dc, ftshare_rest |
| `kph.industry_limit_up_count` | `kpl.turnover_real` | per_stock_time_series | 221 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | kph, kpl |
| `kpl.amplitude` | `push2ex.limit_fund` | per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | kpl, push2ex |
| `kpl.main_buy` | `kph.turnover_rate` | per_stock_time_series | 221 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | kph, kpl |
| `kpl.main_sell` | `kph.turnover_rate` | per_stock_time_series | 221 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | kph, kpl |
| `kpl.raw_columns.col_09` | `kph.turnover_rate` | per_stock_time_series | 221 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | kph, kpl |
| `kpl.raw_columns.col_10` | `kph.turnover_rate` | per_stock_time_series | 221 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | kph, kpl |
| `kpl.raw_columns.col_17` | `push2ex.limit_fund` | per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | kpl, push2ex |
| `kpl.raw_columns.col_20` | `kph.turnover_rate` | per_stock_time_series | 221 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | kph, kpl |
| `push2.f126` | `tencent[9]` | per_stock_time_series | 112 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | push2, tencent |
| `push2.f160` | `tencent[9]` | affine_formula | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | push2, tencent |
| `push2.f176` | `tencent[9]` | per_stock_time_series | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | push2, tencent |
| `push2ex.broken_count` | `kph.turnover_rate` | per_stock_time_series | 178 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | kph, push2ex |
| `push2ex.circulating_value` | `kpl.zt_time` | per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | kpl, push2ex |
| `push2ex.first_limit_time` | `kph.seal_amount` | per_stock_time_series | 178 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | kph, push2ex |
| `push2ex.total_value` | `kpl.zt_time` | per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | kpl, push2ex |
| `push2ex.zt_continuous` | `kpl.zt_time` | per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | kpl, push2ex |
| `push2ex.zt_days` | `kpl.zt_time` | per_stock_time_series | 511 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | kpl, push2ex |
| `sina[14]` | `tencent[68]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | sina, tencent |
| `sina[16]` | `ulist239.f2` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | sina, ulist239 |
| `sina[18]` | `ulist239.f2` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | sina, ulist239 |
| `sina[24]` | `tencent[68]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | sina, tencent |
| `sina[26]` | `tencent[68]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | sina, tencent |
| `sina[28]` | `tencent[68]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | sina, tencent |
| `slist.n_boards` | `tencent[45]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | slist, tencent |
| `tdx.finance_info.fajirenfarengu` | `ulist239.f52` | robust_correlation | 138 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tdx, ulist239 |
| `tdx.finance_info.zhuyinglyrun` | `ulist239.f55` | robust_correlation | 138 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tdx, ulist239 |
| `tencent[22]` | `sina[20]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | sina, tencent |
| `tencent[24]` | `sina[22]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | sina, tencent |
| `tencent[26]` | `sina[22]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | sina, tencent |
| `tencent[28]` | `sina[22]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | sina, tencent |
| `ulist239.f111` | `zhb.tipinfo.hg_amount_yi` | robust_correlation | 30 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `ulist239.f127` | `tencent[63]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f139` | `tencent[76]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f148` | `tencent[71]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f190` | `tencent[76]` | affine_formula | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f192` | `tencent[76]` | affine_formula | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f22` | `tencent[80]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f297` | `tencent[6]` | per_stock_time_series | 80 | T:20261105, T:20261106, T:20261109, T:20261110 | tencent, ulist239 |
| `ulist239.f46` | `zhb.stat.board_count` | robust_correlation | 25 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `ulist239.f59` | `tencent[39]` | robust_correlation | 140 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f98` | `zhb.stat.zt_streak_cycle` | robust_correlation | 17 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `ulist239.f99` | `eltdx.shortline.limit_up_count_in_stat_days` | robust_correlation | 22 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | eltdx, ulist239 |
| `zhb.full.change_60k_bar` | `ulist239.f6` | robust_correlation | 100 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `zhb.full.net_profit_kcf` | `ulist239.f52` | robust_correlation | 100 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `zhb.full.other_qy_jzc` | `ulist239.f60` | affine_formula | 100 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `zhb.full.pre_receive_zj` | `ulist239.f6` | robust_correlation | 90 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `zhb.full.rd_input_fee` | `ulist239.f55` | robust_correlation | 80 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `zhb.full.unknown_2` | `ulist239.f6` | robust_correlation | 100 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `zhb.full.unknown_26` | `ulist239.f12` | robust_correlation | 100 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `zhb.full.zt_count` | `ulist239.f160` | robust_correlation | 17 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `zhb.full.zt_streak_cycle` | `ulist239.f160` | robust_correlation | 17 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |
| `zhb.tipinfo.unlock_shares_wan` | `ulist239.f60` | affine_formula | 100 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb |

### 双输入公式候选
本轮未发现通过留出筛选的公式候选；测试组合 3860 个。


### 已知映射与已证伪关系的候选校准

- 已登记正向对照：当前窗口有 166 组独立数值关系可评估，165 组被方法候选识别；样本不足 1 组。此计数仅检查方法覆盖，不是准确率。
- 已证伪负向对照：数值关系 0 组，其中仍有方法信号 0 组；这些信号被隔离，不进入普通候选。

### 采集覆盖异常源

- baidu: 20261106, 20261109, 20261110 ({'pending_validation': 7})
- em_hot: 20261106, 20261109, 20261110 ({'context_only': 7})
- exchange: 20261106, 20261109, 20261110 ({'context_only': 7})
- ftshare: 20261106, 20261109, 20261110 ({'deprecated': 7})
- tdx: 20261104, 20261105 ({'ok': 5, 'partial': 2})
- zhb: 20261105, 20261109, 20261110 ({'ok': 1, 'partial': 6})

## 候选身份与人工审阅状态

- 候选身份：生成 2317 条，唯一候选 2317 个，重复身份 0，无效身份 0。
- 审阅台账：可用；当前状态 `pending`；已审 0，待处理 2317，覆盖率 0.0%。
- 重复归并组：0；每个成员均保留到代表候选的反向追溯。
- 处置计数：`accepted_for_adjudication` 0；`duplicate_grouped` 0；`insufficient_evidence` 0；`needs_external_evidence` 0；`rejected` 0；`unreviewed` 2317。
- `accepted_for_adjudication` 只表示可进入现有证据裁决流程；审阅台账不会修改主字典或字段注册表。

## 报告完整性与审阅范围

- 机器可读完整性：`complete`；方法候选生成 2291 条，完整明细保存 2291 条，缺失 0 条，多余 0 条，重复 0 条，身份无效 0 条。
- 全量方法候选位于同名 JSON 的 `method_candidate_inventory`；Markdown 的 Top-N 表格是导航摘要，不能代替全量 JSON 审阅。
- 候选审阅数据对账：`complete`；唯一候选 2317 个，审阅 0 个，待处理 2317 个；人工审阅进度与机器清单完整性分别统计。
- Markdown 未逐行展示、但 JSON 保留的部分：
  - `method_candidates`：展示 100 / 500，摘要省略 400 条。
  - `method_candidate_inventory`：展示 0 / 2291，摘要省略 2291 条。
  - `candidate_triage.targets`：展示 50 / 204，摘要省略 154 条。
- 完整性对账通过；逐目标复核仍须覆盖 JSON 的全部明细，并为每项记录已检查、重复归并、证据不足或需外部核验的处置。
