# 全源对撞报告（20261106）

> 交易数据窗口配置：全部历史日期（`--all`）
> 行情窗口：20261015 ~ 20261106（16 个不同交易日）｜字段 1303 个｜样本值 1026686 条
> 新闻/公告自然日窗口：20261015 ~ 20261106
> 主攻目标（unverified）=328｜可审定新候选=3｜首次发现新候选对=0｜已登记关系复验=0｜异号同义 3 / 同号镜像 0

> **规则**：L1 每日需≥18 组有效配对，并至少有5 组信息配对；双方同时为 0 或同时缺失不计命中率，一侧为 0、另一侧非 0 按失配计。信息配对命中率≥90%，且覆盖至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。JSON `daily_sample_counts` 与 `daily_informative_sample_counts`分别保留每日有效配对数和 L1 信息配对数。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 新候选 — 异号同义（跨编号，高价值）(3)

| 左字段(unverified) | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|
| `zhb.full.high_52w` | `tencent[67]` | L1 | 95.00% | 9 | 180 | 180 | - |  | — |
| `zhb.full.change_ytd` | `push2.f122` | L1 | 90.00% | 3 | 60 | 60 | - |  | — |
| `zhb.full.high_52w` | `push2.f174` | L1 | 90.00% | 3 | 60 | 60 | - |  | — |

## 二、L1 / L1-U 新候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、已登记映射的本窗口复验（0）

_这些关系已在主注册表登记，只用于观察当前样本是否仍支持既有映射；它们不是新的未知字段候选，也不能再次提交为新定案。_

_本轮没有已登记关系进入复验窗口。_


## 四、L4 存疑候选（62）

| 左字段 | 右字段 | 命中率 | 天数 | 样本 |
|:--|:--|--:|--:|--:|
| `axdata.data.instrument_id` | `ftshare_rest.symbol` | 100.00% | 10 | 199 |
| `axdata.data.open_price` | `ftshare_rest.open` | 100.00% | 10 | 199 |
| `axdata.data.pre_close` | `ftshare_rest.prev_close` | 100.00% | 10 | 199 |
| `sina[32]` | `ulist239.f231` | 95.00% | 4 | 80 |
| `ulist239.f190` | `tdx.finance_info.hgu` | 94.87% | 4 | 78 |
| `sina[32]` | `tdx.finance_info.hgu` | 94.60% | 14 | 278 |
| `push2ex.zt_continuous` | `kph.limit_count` | 94.43% | 9 | 377 |
| `sina[32]` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 91.43% | 14 | 280 |
| `sina[32]` | `ulist239.f200` | 90.00% | 4 | 80 |
| `sina[32]` | `zhb.stat.other_qy_jzc` | 90.00% | 9 | 180 |
| `ulist239.f190` | `zhb.stat.other_qy_jzc` | 90.00% | 3 | 60 |
| `zhb.full.other_qy_jzc` | `ulist239.f231` | 90.00% | 3 | 60 |
| `sina[32]` | `tdx.finance_info.bgu` | 89.57% | 14 | 278 |
| `push2ex.zt_days` | `kph.limit_count` | 88.86% | 9 | 377 |
| `push2ex.zt_days` | `kpl.raw_columns.col_15` | 88.65% | 13 | 837 |
| `push2ex.zt_continuous` | `kpl.raw_columns.col_15` | 88.65% | 13 | 837 |
| `ulist239.f190` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 86.25% | 4 | 80 |
| `push2.f192` | `tencent[50]` | 85.07% | 8 | 134 |
| `ulist239.f190` | `tdx.finance_info.bgu` | 84.62% | 4 | 78 |
| `zhb.full.other_qy_jzc` | `ulist239.f200` | 80.00% | 3 | 60 |
| `sina_extended.trade` | `fuyao.snapshot.last_price` | 76.36% | 11 | 220 |
| `zhb.full.dividend_yield` | `tencent[64]` | 76.11% | 9 | 180 |
| `sina_extended.trade` | `eltdx.quote_snapshot.last_price` | 75.83% | 12 | 240 |
| `sina_extended.trade` | `tencent[3]` | 75.83% | 12 | 240 |
| `sina_extended.trade` | `tdx.quote_raw.price` | 75.63% | 12 | 238 |
| `sina_extended.trade` | `tdx.quote_full.price` | 75.63% | 12 | 238 |
| `sina_extended.trade` | `ftshare_rest.close` | 74.55% | 11 | 220 |
| `zhb.full.change_ytd` | `tencent[62]` | 72.78% | 9 | 180 |
| `ulist239.f11` | `tencent[80]` | 71.25% | 4 | 80 |
| `sina_extended.trade` | `push2.f43` | 70.90% | 8 | 134 |
| `sina_extended.trade` | `push2.f179` | 70.90% | 8 | 134 |
| `ulist239.f133` | `zhb.stat.dividend_yield` | 70.00% | 3 | 60 |
| `zhb.full.change_250k_bar` | `tencent[79]` | 68.33% | 9 | 180 |
| `sina_extended.trade` | `ulist239.f2` | 67.50% | 4 | 80 |
| `sina_extended.trade` | `ulist239.f144` | 67.50% | 4 | 80 |
| `ulist239.f13` | `zhb.stat.other_qy_jzc` | 60.00% | 3 | 60 |
| `ulist239.f27` | `zhb.stat.other_qy_jzc` | 60.00% | 3 | 60 |
| `ulist239.f13` | `tdx.finance_info.hgu` | 58.97% | 4 | 78 |
| `ulist239.f27` | `tdx.finance_info.hgu` | 58.97% | 4 | 78 |
| `zhb.full.other_qy_jzc` | `push2.f107` | 56.98% | 5 | 86 |
| `zhb.full.other_qy_jzc` | `push2.f110` | 56.98% | 5 | 86 |
| `push2.f191` | `tencent[74]` | 56.72% | 8 | 134 |
| `sina[32]` | `push2.f107` | 55.97% | 8 | 134 |
| `sina[32]` | `push2.f110` | 55.97% | 8 | 134 |
| `ulist239.f97` | `zhb.stat.other_qy_jzc` | 55.00% | 3 | 60 |
| `ulist239.f133` | `tencent[64]` | 55.00% | 4 | 80 |
| `ulist239.f97` | `tdx.finance_info.hgu` | 51.28% | 4 | 78 |
| `ulist239.f13` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 51.25% | 4 | 80 |
| `ulist239.f27` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 51.25% | 4 | 80 |
| `ulist239.f97` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 50.00% | 4 | 80 |
| `kpl.raw_columns.col_02` | `kph.limit_count` | 49.29% | 9 | 420 |
| `ulist239.f13` | `tdx.finance_info.bgu` | 48.72% | 4 | 78 |
| `ulist239.f27` | `tdx.finance_info.bgu` | 48.72% | 4 | 78 |
| `ulist239.f97` | `tdx.finance_info.bgu` | 48.72% | 4 | 78 |
| `kpl.raw_columns.col_02` | `push2ex.limit_count` | 45.76% | 13 | 837 |
| `kpl.raw_columns.col_16` | `kph.limit_count` | 45.71% | 9 | 420 |
| `kpl.raw_columns.col_16` | `push2ex.limit_count` | 42.89% | 13 | 837 |
| `sina_extended.trade` | `tencent[9]` | 42.50% | 12 | 240 |
| `sina_extended.trade` | `tdx.quote_raw.bid1` | 42.44% | 12 | 238 |
| `sina_extended.trade` | `tdx.quote_full.bid1` | 42.44% | 12 | 238 |

_（仅显示前 60 / 共 62）_

## 五、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 六、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `sina_extended.turnover` | `ftshare_rest.turnover_rate` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 220 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | ftshare_rest, sina_extended | Pearson=0.9998, Spearman=0.9982, LOO稳号=True |
| `push2ex.turnover_rate` | `kph.turnover_rate` | robust_correlation, per_stock_time_series, semantic_label | 377 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028, T:20261030 | kph, push2ex | Pearson=0.8443, Spearman=0.8873, LOO稳号=True |
| `tencent[27]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=0.9975, LOO稳号=True |
| `tencent[27]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.8997, LOO稳号=True |
| `tencent[27]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9072, LOO稳号=True |
| `tencent[27]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9052, LOO稳号=True |
| `tencent[27]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.8987, LOO稳号=True |
| `tencent[27]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=0.9975, LOO稳号=True |
| `tencent[27]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9997, Spearman=0.9081, LOO稳号=True |
| `tencent[27]` | `sina[11]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.8997, LOO稳号=True |
| `tencent[27]` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9997, Spearman=0.9081, LOO稳号=True |
| `tencent[27]` | `eltdx.quote_snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9997, Spearman=0.9081, LOO稳号=True |
| `tencent[27]` | `eltdx.quote_snapshot.low_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.9072, LOO稳号=True |
| `tencent[27]` | `eltdx.quote_snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.8987, LOO稳号=True |
| `tencent[27]` | `eltdx.quote_snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.9052, LOO稳号=True |
| `tencent[25]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=0.9975, LOO稳号=True |
| `tencent[25]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.8997, LOO稳号=True |
| `tencent[25]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9072, LOO稳号=True |
| `tencent[25]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9052, LOO稳号=True |
| `tencent[25]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.8987, LOO稳号=True |
| `tencent[25]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=0.9975, LOO稳号=True |
| `tencent[25]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9997, Spearman=0.9081, LOO稳号=True |
| `tencent[25]` | `sina[11]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.8997, LOO稳号=True |
| `tencent[25]` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9997, Spearman=0.9081, LOO稳号=True |
| `tencent[25]` | `eltdx.quote_snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9997, Spearman=0.9081, LOO稳号=True |
| `tencent[25]` | `eltdx.quote_snapshot.low_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.9072, LOO稳号=True |
| `tencent[25]` | `eltdx.quote_snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.8987, LOO稳号=True |
| `tencent[25]` | `eltdx.quote_snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.9052, LOO稳号=True |
| `tencent[23]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=0.9975, LOO稳号=True |
| `tencent[23]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.8997, LOO稳号=True |
| `tencent[23]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9072, LOO稳号=True |
| `tencent[23]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9052, LOO稳号=True |
| `tencent[23]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.8987, LOO稳号=True |
| `tencent[23]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=0.9975, LOO稳号=True |
| `tencent[23]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9997, Spearman=0.9081, LOO稳号=True |
| `tencent[23]` | `sina[11]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.8997, LOO稳号=True |
| `tencent[23]` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9997, Spearman=0.9081, LOO稳号=True |
| `tencent[23]` | `eltdx.quote_snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9997, Spearman=0.9081, LOO稳号=True |
| `tencent[23]` | `eltdx.quote_snapshot.low_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.9072, LOO稳号=True |
| `tencent[23]` | `eltdx.quote_snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.8987, LOO稳号=True |
| `tencent[23]` | `eltdx.quote_snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.9052, LOO稳号=True |
| `tencent[22]` | `sina[22]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[21]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=0.9975, LOO稳号=True |
| `tencent[21]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.8997, LOO稳号=True |
| `tencent[21]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9072, LOO稳号=True |
| `tencent[21]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9052, LOO稳号=True |
| `tencent[21]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.8987, LOO稳号=True |
| `tencent[21]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=0.9975, LOO稳号=True |
| `tencent[21]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9997, Spearman=0.9081, LOO稳号=True |
| `tencent[21]` | `sina[11]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.8997, LOO稳号=True |
| `tencent[21]` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9997, Spearman=0.9081, LOO稳号=True |
| `tencent[21]` | `eltdx.quote_snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9997, Spearman=0.9081, LOO稳号=True |
| `tencent[21]` | `eltdx.quote_snapshot.low_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.9072, LOO稳号=True |
| `tencent[21]` | `eltdx.quote_snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.8987, LOO稳号=True |
| `tencent[21]` | `eltdx.quote_snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.9052, LOO稳号=True |
| `tencent[20]` | `sina[20]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[17]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9015, LOO稳号=True |
| `tencent[17]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[17]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9999, Spearman=0.9939, LOO稳号=True |
| `tencent[17]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=0.9955, LOO稳号=True |
| `tencent[17]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=0.9921, LOO稳号=True |
| `tencent[17]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9868, LOO稳号=True |
| `tencent[17]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9015, LOO稳号=True |
| `tencent[17]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9999, Spearman=0.9934, LOO稳号=True |
| `tencent[17]` | `sina[11]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[17]` | `eltdx.shortline.pre_close` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.9868, LOO稳号=True |
| `tencent[17]` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9999, Spearman=0.9934, LOO稳号=True |
| `tencent[17]` | `eltdx.quote_snapshot.pre_close_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.9868, LOO稳号=True |
| `tencent[17]` | `eltdx.quote_snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9999, Spearman=0.9934, LOO稳号=True |
| `tencent[17]` | `eltdx.quote_snapshot.low_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9999, Spearman=0.9939, LOO稳号=True |
| `tencent[17]` | `eltdx.quote_snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=1.0, Spearman=0.9921, LOO稳号=True |
| `tencent[17]` | `eltdx.quote_snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=1.0, Spearman=0.9955, LOO稳号=True |
| `tencent[15]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9015, LOO稳号=True |
| `tencent[15]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[15]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9999, Spearman=0.994, LOO稳号=True |
| `tencent[15]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=0.9955, LOO稳号=True |
| `tencent[15]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=0.9921, LOO稳号=True |
| `tencent[15]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9868, LOO稳号=True |
| `tencent[15]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9015, LOO稳号=True |
| `tencent[15]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9999, Spearman=0.9935, LOO稳号=True |
| `tencent[15]` | `sina[11]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[15]` | `eltdx.shortline.pre_close` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.9868, LOO稳号=True |
| `tencent[15]` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9999, Spearman=0.9935, LOO稳号=True |
| `tencent[15]` | `eltdx.quote_snapshot.pre_close_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.9868, LOO稳号=True |
| `tencent[15]` | `eltdx.quote_snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9999, Spearman=0.9935, LOO稳号=True |
| `tencent[15]` | `eltdx.quote_snapshot.low_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9999, Spearman=0.994, LOO稳号=True |
| `tencent[15]` | `eltdx.quote_snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=1.0, Spearman=0.9921, LOO稳号=True |
| `tencent[15]` | `eltdx.quote_snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=1.0, Spearman=0.9955, LOO稳号=True |
| `tencent[13]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9016, LOO稳号=True |
| `tencent[13]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[13]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9999, Spearman=0.994, LOO稳号=True |
| `tencent[13]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=0.9955, LOO稳号=True |
| `tencent[13]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=0.9922, LOO稳号=True |
| `tencent[13]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9868, LOO稳号=True |
| `tencent[13]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9998, Spearman=0.9016, LOO稳号=True |
| `tencent[13]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=0.9999, Spearman=0.9935, LOO稳号=True |
| `tencent[13]` | `sina[11]` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[13]` | `eltdx.shortline.pre_close` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.9868, LOO稳号=True |
| `tencent[13]` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9999, Spearman=0.9935, LOO稳号=True |
| `tencent[13]` | `eltdx.quote_snapshot.pre_close_price` | robust_correlation, affine_formula, per_stock_time_series | 280 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | eltdx, tencent | Pearson=0.9998, Spearman=0.9868, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 七、日期与数据质量告警（281）

- 20261017: 旧式非交易日目录按前一交易日 20261016 归并；目录未改名
- 20261018: 旧式非交易日目录按前一交易日 20261016 归并；目录未改名
- 20261031: 旧式非交易日目录按前一交易日 20261030 归并；目录未改名
- 20261101: 旧式非交易日目录按前一交易日 20261030 归并；目录未改名
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
- 20261021/ulist239: 来源状态为 failed，快照跳过
- 另有 181 条告警，详见同名 JSON 报告。

---

> 数据来源：通达信 / 项目字段对撞体系。以上为方法论梳理，不构成投资建议。

## 来源身份状态（不参与字段语义定案）

_FTShare 公共 REST 接口已进入日常采集；官方字段契约作为语义锚，底层数据提供方仍未确认。与其匹配的强候选列在 L1-C，不混入独立来源 L1。_
_旧私有托管 MCP 采集器已退役，历史样本仅供 `--all` / `--exploratory` 追溯。_

## 官方契约锚候选 L1-C（0）

_L1-C 使用逐字段审定的官方接口契约语义作锚，并满足多日数值匹配门槛；仅当该接口底层数据来源独立性未确认时才列入此处，不属于独立来源 L1，也不自动定案。_

_本轮无达到多日门槛的官方契约锚候选。_

## 字段时效与来源日期证据

_字段语义关系和来源日期可信度分开记录。`source_dates_confirmed` 表示两侧入选样本都有来源或记录级日期；`semantic_only_date_unconfirmed` 只支持缓变/静态字段的语义关系，不证明数据新鲜度或具体有效日期。未分类字段按来源日期严格门控。_

策略状态：`ok`；逐源分类字段 13，保守默认未分类字段 1290。L1/L1-C 日期证据：来源日期已确认 3 条，仅语义证据且日期未确认 0 条，其他日期未确认 0 条。

_本轮 L1/L1-C 没有仅凭静态或缓变字段、且来源日期未确认的关系。_

## 来源字段覆盖与碰撞参与

_窗口字段值样本是经日期筛选、重复折叠和快照择优后载入的非空值；右侧比较次数另受字段类型及来源规则筛选。官方契约字段须有逐字段审定证据，契约语义本身不证明底层数据来源独立。_

| 来源 | 已确认字段 | 契约已确认 | 契约锚 | 独立锚 | L1-C 锚 | 窗口字段 / 字段值样本 / 交易日 |
|:--|--:|--:|--:|--:|--:|--:|
| axdata | 0 | 0 | 0 | 0 | 0 | 34 / 6932 / 13 |
| clist | 18 | 0 | 0 | 18 | 0 | 33 / 28668 / 4 |
| cls | 4 | 0 | 0 | 4 | 0 | 5 / 3250 / 0 |
| datacenter | 41 | 0 | 0 | 41 | 0 | 0 / 0 / 0 |
| eltdx | 64 | 0 | 0 | 64 | 0 | 116 / 15443 / 14 |
| em_fund_flow | 0 | 0 | 0 | 0 | 0 | 15 / 1395 / 5 |
| em_hot | 39 | 0 | 0 | 39 | 0 | 0 / 0 / 0 |
| em_kline_f61 | 10 | 0 | 0 | 10 | 0 | 2 / 160 / 4 |
| etf | 0 | 0 | 0 | 0 | 0 | 9 / 151654 / 13 |
| event_dc | 0 | 0 | 0 | 0 | 0 | 148 / 370350 / 12 |
| exchange | 4 | 0 | 0 | 4 | 0 | 0 / 0 / 0 |
| ftshare | 6 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| ftshare_rest | 31 | 31 | 31 | 0 | 31 | 32 / 6985 / 11 |
| fuyao | 88 | 74 | 74 | 88 | 0 | 20 / 4820 / 13 |
| kph | 12 | 0 | 0 | 12 | 0 | 15 / 6765 / 10 |
| kpl | 10 | 0 | 0 | 10 | 0 | 28 / 30190 / 14 |
| market_sources | 14 | 0 | 0 | 0 | 0 | 74 / 110864 / 14 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 2 / 308 / 0 |
| push2 | 40 | 0 | 0 | 40 | 0 | 114 / 15276 / 8 |
| push2ex | 24 | 0 | 0 | 24 | 0 | 16 / 20144 / 13 |
| reports | 26 | 0 | 0 | 26 | 0 | 49 / 784 / 0 |
| research_sina | 0 | 0 | 0 | 0 | 0 | 6 / 4290 / 0 |
| sina | 19 | 0 | 0 | 19 | 0 | 39 / 9660 / 14 |
| sina_extended | 0 | 0 | 0 | 0 | 0 | 4 / 960 / 12 |
| slist | 5 | 0 | 0 | 5 | 0 | 1 / 80 / 4 |
| sse_e_interaction | 0 | 0 | 0 | 0 | 0 | 8 / 1040 / 0 |
| st_list | 0 | 0 | 0 | 0 | 0 | 6 / 9968 / 5 |
| tdx | 83 | 0 | 0 | 83 | 0 | 67 / 17352 / 14 |
| tencent | 62 | 0 | 0 | 62 | 0 | 88 / 24612 / 14 |
| ulist239 | 44 | 0 | 0 | 44 | 0 | 240 / 19140 / 4 |
| zhb | 86 | 0 | 0 | 86 | 0 | 124 / 19789 / 9 |

| 来源 | 破解目标 | 比较字段 | 作目标比较 | 作右侧比较 | L1-C 锚比较 | L1 / L1-C / L4 关系 | 方法候选涉及 |
|:--|--:|--:|--:|--:|--:|--:|--:|
| axdata | 30 | 0 | 627 | 0 | 0 | 0 / 0 / 3 | 101 |
| clist | 11 | 16 | 2795 | 2224 | 0 | 0 / 0 / 0 | 0 |
| cls | 2 | 0 | 399 | 0 | 0 | 0 / 0 / 0 | 0 |
| datacenter | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| eltdx | 31 | 50 | 6354 | 5650 | 0 | 0 / 0 / 6 | 666 |
| em_fund_flow | 4 | 0 | 1112 | 0 | 0 | 0 / 0 / 0 | 182 |
| em_hot | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| em_kline_f61 | 1 | 0 | 278 | 0 | 0 | 0 / 0 / 0 | 23 |
| etf | 4 | 0 | 29 | 0 | 0 | 0 / 0 / 0 | 0 |
| event_dc | 62 | 0 | 1258 | 0 | 0 | 0 / 0 / 0 | 314 |
| exchange | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare_rest | 1 | 25 | 23 | 6851 | 6851 | 0 / 0 / 4 | 980 |
| fuyao | 1 | 13 | 363 | 2704 | 0 | 0 / 0 / 1 | 435 |
| kph | 1 | 9 | 368 | 1681 | 0 | 0 / 0 / 4 | 47 |
| kpl | 11 | 10 | 3623 | 3184 | 0 | 0 / 0 / 6 | 57 |
| market_sources | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| push2 | 19 | 35 | 4230 | 4469 | 0 | 2 / 0 / 8 | 1264 |
| push2ex | 7 | 5 | 1946 | 695 | 0 | 0 / 0 / 6 | 351 |
| reports | 11 | 6 | 2006 | 702 | 0 | 0 / 0 / 0 | 0 |
| research_sina | 2 | 0 | 381 | 0 | 0 | 0 / 0 / 0 | 0 |
| sina | 16 | 18 | 5776 | 2883 | 0 | 0 / 0 / 8 | 1440 |
| sina_extended | 3 | 0 | 1083 | 0 | 0 | 0 / 0 / 13 | 177 |
| slist | 1 | 0 | 278 | 0 | 0 | 0 / 0 / 0 | 6 |
| sse_e_interaction | 2 | 0 | 25 | 0 | 0 | 0 / 0 / 0 | 0 |
| st_list | 3 | 0 | 48 | 0 | 0 | 0 / 0 / 0 | 0 |
| tdx | 12 | 50 | 3150 | 6200 | 0 | 0 / 0 / 14 | 982 |
| tencent | 22 | 56 | 6823 | 9840 | 0 | 1 / 0 / 11 | 2374 |
| ulist239 | 26 | 44 | 6965 | 5588 | 0 | 0 / 0 / 27 | 1331 |
| zhb | 43 | 56 | 9675 | 6944 | 0 | 3 / 0 / 13 | 2196 |

## AxData 每日接口核验

> 此处汇总采集目录已保存的本地证据，不发起网络请求、不改变注册表状态；AxData 是多源框架，不作为独立字段锚。

### AxData

窗口内有 15 个唯一数据日的轮验记录；重复目录合并 0 条。
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

被动逐字段比较中的差异计数（跨本窗口唯一数据日累加，不含原始值）：

| 比较路径 | 相同 | 不同 | 缺失/双方空值 |
|:--|--:|--:|--:|
| `axdata_shortline_vs_eltdx:alignment_status` | 0 | 180 | 0 |
| `axdata_shortline_vs_eltdx:beta_60d` | 0 | 180 | 0 |
| `axdata_shortline_vs_eltdx:code` | 0 | 180 | 0 |
| `axdata_shortline_vs_eltdx:full_code` | 0 | 180 | 0 |
| `axdata_shortline_vs_eltdx:instrument_id` | 0 | 180 | 0 |
| `axdata_shortline_vs_eltdx:limit_status` | 0 | 180 | 0 |
| `axdata_shortline_vs_eltdx:market_id` | 0 | 180 | 0 |
| `axdata_shortline_vs_eltdx:opening_rush` | 0 | 180 | 0 |
| `axdata_shortline_vs_eltdx:pe_ttm` | 0 | 180 | 0 |
| `axdata_shortline_vs_eltdx:previous_trade_date` | 0 | 180 | 0 |
| `axdata_shortline_vs_eltdx:symbol` | 0 | 180 | 0 |
| `axdata_shortline_vs_eltdx:target_trade_date` | 0 | 180 | 0 |
| `axdata_shortline_vs_eltdx:tdx_code` | 0 | 180 | 0 |
| `axdata_shortline_vs_eltdx:open_amount` | 38 | 142 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_hand` | 38 | 142 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_ratio` | 38 | 142 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_amount_ratio` | 45 | 135 | 0 |
| `axdata_shortline_vs_eltdx:auction_prev_volume_ratio` | 53 | 124 | 3 |
| `kph_limit_up_history_vs_kpl_detail:seal_amount` | 44 | 95 | 0 |
| `kph_limit_up_history_vs_kpl_detail:seal_money` | 44 | 95 | 0 |
| `axdata_shortline_vs_eltdx:open_turnover_z` | 96 | 84 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_seal_ratio` | 4 | 8 | 168 |
| `axdata_shortline_vs_eltdx:ladder_level` | 0 | 7 | 173 |
| `axdata_shortline_vs_eltdx:limit_board_text` | 17 | 6 | 157 |

### FTShare 退役来源历史记录（显式历史研究）

窗口内保留 3 个唯一数据日的旧元数据；重复目录合并 0 条。

| 数据日 | 历史状态 | 旧接口状态计数 |
|:--|:--|:--|
| 20261015 | ok | pending: 6 |
| 20261016 | ok | pending: 6 |
| 20261019 | ok | pending: 6 |

## 字母字段名语义提示（仅候选）

窗口内观察到 178 条需审阅的字母字段路径：含词义线索 42 条，仅拆词 136 条。
完整逐条记录保存在碰撞 JSON；名称线索清单：`docs/field_verification/20261014/20261014_alphabetic_field_name_inventory.csv`。
> 拼音、英文、缩写和混合拆词只用于检索候选；必须结合原始值、接口定义和独立来源复核，不得据此定案或改写主字典。

| 逐源字段路径 | 状态/审阅范围 | 名称形式与拆词 | 词义线索（非释义） | 样本日期 |
|:--|:--|:--|:--|:--|
| `市场源(market_sources)::change_type` | unverified / unverified_semantics | snake_case_or_mixed: change type | 变化/涨跌 + 类型 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `市场源(market_sources)::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `东财-push2ex::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `东财-push2ex::first_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: first limit time | 首次/第一 + 涨跌停限制 + 时间 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `东财-push2ex::last_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: last limit time | 最近/上一期 + 涨跌停限制 + 时间 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `东财-push2ex::name` | unverified / unverified_semantics | recognized_english_word_candidate: name | 名称 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `东财-push2ex::total_value` | unverified / unverified_semantics | snake_case_or_mixed: total value | 总 + 值 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `市场源(market_sources)::limit_count` | verified / verified_metadata_gap | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `市场源(market_sources)::limit_time` | unverified / unverified_semantics | snake_case_or_mixed: limit time | 涨跌停限制 + 时间 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `市场源(market_sources)::plate_limit_up_count` | verified / verified_metadata_gap | snake_case_or_mixed: plate limit up count | 涨跌停限制 + 上/涨 + 数量/次数 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `财联社(cls)::time` | unverified / unverified_semantics | recognized_english_word_candidate: time | 时间 | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105 |
| `TDX(双命名源)::changqifuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: changqifuzhai | 长期负债 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::cunhuo` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: cunhuo | 存货 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::eps` | unverified / unverified_semantics | recognized_english_word_candidate: eps | 每股收益 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::fajirenfarengu` | unverified / unverified_semantics | recognized_pinyin_phrase_candidate: fajirenfarengu | 疑似 faqirenfarengu 的拼写变体；含义未证实 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::gudongrenshu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: gudongrenshu | 股东人数 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::ipodate` | unverified / unverified_semantics | recognized_english_phrase_candidate: ipodate | IPO/上市日期（字段语境候选） | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::jinglirun` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jinglirun | 净利润 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::jingyingxianjinliu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingyingxianjinliu | 经营现金流 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::jingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingzichan | 净资产 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::liudongfuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: liudongfuzhai | 流动负债 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::meigujingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: meigujingzichan | 每股净资产 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::yingshouzhangkuan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: yingshouzhangkuan | 应收账款 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::zhuyingshouru` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zhuyingshouru | 主营收入 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::zibengongjijin` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zibengongjijin | 资本公积金 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::zongzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongzichan | 总资产 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `同花顺-fuyao::snapshot.open_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot open price | 开盘 + 价格 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `新浪(扩展API)::turnover` | conflict / unverified_semantics | recognized_english_word_candidate: turnover | 换手/成交额（需看接口） | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `ZHB-tdxstat::change_pct_1d` | unverified / unverified_semantics | snake_case_or_mixed: change pct 1 d | 变化/涨跌 + 百分比 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104 |
| `ZHB-tdxstat::change_pct_2d` | unverified / unverified_semantics | snake_case_or_mixed: change pct 2 d | 变化/涨跌 + 百分比 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104 |
| `ZHB-tdxstat2::main_net_buy_amount_1d` | unverified / unverified_semantics | snake_case_or_mixed: main net buy amount 1 d | 净 + 金额/成交额（需看接口） | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104 |
| `ZHB-tdxstat2::main_net_buy_amount` | unverified / unverified_semantics | snake_case_or_mixed: main net buy amount | 净 + 金额/成交额（需看接口） | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104 |
| `reports::actualLastTwoYearEps` | unverified / unverified_semantics | camel_case_or_mixed: actual Last Two Year Eps | 最近/上一期 + 每股收益 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::actualLastYearEps` | unverified / unverified_semantics | camel_case_or_mixed: actual Last Year Eps | 最近/上一期 + 每股收益 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::count` | verified / verified_metadata_gap | recognized_english_word_candidate: count | 数量/次数 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::lastEmRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Code | 最近/上一期 + 代码 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::lastEmRatingName` | conflict / unverified_semantics | camel_case_or_mixed: last Em Rating Name | 最近/上一期 + 名称 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::lastEmRatingValue` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Value | 最近/上一期 + 值 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::predictLastYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Eps | 最近/上一期 + 每股收益 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::predictLastYearPe` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Pe | 最近/上一期 + 市盈率 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `TDX-eltdx(适配层)::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `东财-push2ex::broken_count` | unverified / unverified_semantics | snake_case_or_mixed: broken count | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `东财-push2ex::circulating_value` | unverified / unverified_semantics | snake_case_or_mixed: circulating value | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `东财-push2ex::sector` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: sector | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `东财-push2ex::turnover_rate` | unverified / unverified_semantics | snake_case_or_mixed: turnover rate | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `东财-push2ex::zt_continuous` | unverified / unverified_semantics | snake_case_or_mixed: zt continuous | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `东财-push2ex::zt_days` | unverified / unverified_semantics | snake_case_or_mixed: zt days | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `市场源(market_sources)::one_word` | unverified / unverified_semantics | snake_case_or_mixed: one word | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `市场源(market_sources)::plate_amount` | verified / verified_metadata_gap | snake_case_or_mixed: plate amount | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `市场源(market_sources)::plate_code` | verified / verified_metadata_gap | snake_case_or_mixed: plate code | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `市场源(market_sources)::plate_name` | verified / verified_metadata_gap | snake_case_or_mixed: plate name | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `市场源(market_sources)::popular` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: popular | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `开盘啦(kpl_limit_up_detail)::raw_columns.col_19` | verified / verified_metadata_gap | runtime_tokenization_only: col 19 | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `财联社(cls)::content` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: content | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105 |
| `财联社(cls)::level` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: level | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105 |
| `财联社(cls)::reading_num` | unverified / unverified_semantics | snake_case_or_mixed: reading num | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105 |
| `财联社(cls)::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105 |
| `开盘红::industry_limit_up_count` | unverified / unverified_semantics | runtime_tokenization_only: industry limit up count | — | T:20261016, T:20261019, T:20261021, T:20261022, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::baoliu2` | unverified / unverified_semantics | mixed_alphanumeric: baoliu 2 | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::ipo_date` | verified / verified_metadata_gap | snake_case_or_mixed: ipo date | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::updated_date` | verified / verified_metadata_gap | snake_case_or_mixed: updated date | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::updateddate` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: updateddate | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::zhuyinglyrun` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: zhuyinglyrun | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `同花顺-fuyao::fin_report` | unverified / unverified_semantics | snake_case_or_mixed: fin report | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `市场源(market_sources)::big_order_300w_net` | unverified / unverified_semantics | runtime_tokenization_only: big order 300 w net | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `市场源(market_sources)::institution_add` | unverified / unverified_semantics | runtime_tokenization_only: institution add | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `市场源(market_sources)::main_inflow` | unverified / unverified_semantics | snake_case_or_mixed: main inflow | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `市场源(market_sources)::pe_next` | unverified / unverified_semantics | runtime_tokenization_only: pe next | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `市场源(market_sources)::pe_now` | unverified / unverified_semantics | runtime_tokenization_only: pe now | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `市场源(market_sources)::strength` | unverified / unverified_semantics | runtime_tokenization_only: strength | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `市场源(market_sources)::total_value` | unverified / unverified_semantics | runtime_tokenization_only: total value | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::ask1_vol` | unverified / unverified_semantics | runtime_tokenization_only: ask 1 vol | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::b_vol` | unverified / unverified_semantics | snake_case_or_mixed: b vol | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::b_vol` | unverified / unverified_semantics | snake_case_or_mixed: b vol | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::bid1_vol` | unverified / unverified_semantics | snake_case_or_mixed: bid 1 vol | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::s_vol` | unverified / unverified_semantics | snake_case_or_mixed: s vol | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `TDX(双命名源)::s_vol` | unverified / unverified_semantics | snake_case_or_mixed: s vol | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `同花顺-fuyao::snapshot.prev_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot prev price | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `同花顺-fuyao::valuation.ps_ttm` | conflict / unverified_semantics | snake_case_or_mixed: valuation ps ttm | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `新浪(扩展API)::netamount` | conflict / unverified_semantics | unsegmented_latin_pinyin_or_word: netamount | — | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `新浪(扩展API)::opendate` | conflict / unverified_semantics | unsegmented_latin_pinyin_or_word: opendate | — | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `新浪(扩展API)::trade` | conflict / unverified_semantics | unsegmented_latin_pinyin_or_word: trade | — | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `FTShare REST::amplitude` | verified / verified_metadata_gap | runtime_tokenization_only: amplitude | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `FTShare REST::avg` | verified / verified_metadata_gap | runtime_tokenization_only: avg | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `FTShare REST::bid_ask_ratio` | verified / verified_metadata_gap | runtime_tokenization_only: bid ask ratio | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `FTShare REST::board` | verified / verified_metadata_gap | runtime_tokenization_only: board | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `FTShare REST::listing_date` | verified / verified_metadata_gap | runtime_tokenization_only: listing date | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `FTShare REST::name` | verified / verified_metadata_gap | runtime_tokenization_only: name | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `FTShare REST::st` | verified / verified_metadata_gap | runtime_tokenization_only: st | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `FTShare REST::status` | verified / verified_metadata_gap | runtime_tokenization_only: status | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `FTShare REST::symbol` | verified / verified_metadata_gap | runtime_tokenization_only: symbol | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `FTShare REST::symbol_id` | unverified / unverified_semantics | runtime_tokenization_only: symbol id | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `FTShare REST::turnover_rate` | verified / verified_metadata_gap | runtime_tokenization_only: turnover rate | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 |
| `ZHB-tdxstat::change_10k_bar` | unverified / unverified_semantics | snake_case_or_mixed: change 10 k bar | — | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104 |
| `ZHB-tdxstat::change_5k_bar` | unverified / unverified_semantics | snake_case_or_mixed: change 5 k bar | — | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104 |
| `ZHB-tdxstat::change_ytd` | unverified / unverified_semantics | snake_case_or_mixed: change ytd | — | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104 |
| `ZHB-tdxstat::dividend_yield` | unverified / unverified_semantics | snake_case_or_mixed: dividend yield | — | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104 |

Markdown 显示前 100 条；其余 78 条完整保留在 JSON。

## 探索候选持续跟踪

研究台账：`collision_research_state.json.gz`；累计历史跟踪候选对 2200，本报告候选对 757，历史复现 706，新发现 0。
台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，不会自动改变字段状态、碰撞锚或主字典。新报告只将 `actionable_L1`、L4 和主动方法候选写入待研究队列；已登记关系的复验单独展示，历史跟踪记录不会被删除。

## 候选覆盖、公式与下一步采样

本节用于定位证据缺口和安排后续取样。相关性、公式与样本优先级均为探索候选；不会改变 L1/L1-U 门槛、来源独立性或主字典。

- 未知目标 328 个；其中有方法候选 222 个、无候选 106 个；多候选目标 203 个。
- 方法候选生成 6463 条；全局详细项保留 500/500，另按目标字段保留 206 条；完整明细 6463 条在 JSON `method_candidate_inventory`；未归档明细 0 条。
- 字段覆盖详情：available；覆盖身份 1932，读取 15 份本地索引。

### 优先处理字段

| 未知字段 | 当前诊断 | 独立对比/候选数 | 独立锚家族/本源日期 | 建议复核股票 | 最强候选线索 |
|:--|:--|--:|:--|:--|:--|
| `sina_extended.trade` | 存在多个候选，需区分 | 338 / 124 | 6 家族 / 338 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[15]` | 存在多个候选，需区分 | 338 / 123 | 6 家族 / 338 对 / 本源 14 日 | 600519 (5.953439) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[17]` | 存在多个候选，需区分 | 338 / 123 | 6 家族 / 338 对 / 本源 14 日 | 600519 (5.948278) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[19]` | 存在多个候选，需区分 | 338 / 123 | 6 家族 / 338 对 / 本源 14 日 | 600519 (5.94243) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[13]` | 存在多个候选，需区分 | 338 / 122 | 6 家族 / 338 对 / 本源 14 日 | 600519 (5.959151) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `ulist239.f142` | 存在多个候选，需区分 | 255 / 110 | 6 家族 / 255 对 / 本源 0 日 | 600519 (5.031537) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `ulist239.f143` | 存在多个候选，需区分 | 255 / 110 | 6 家族 / 255 对 / 本源 0 日 | 600519 (4.978594) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[13]` | 存在多个候选，需区分 | 301 / 106 | 6 家族 / 301 对 / 本源 14 日 | 600519 (4.337345) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[15]` | 存在多个候选，需区分 | 301 / 106 | 6 家族 / 301 对 / 本源 14 日 | 600519 (4.336909) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[17]` | 存在多个候选，需区分 | 301 / 106 | 6 家族 / 301 对 / 本源 14 日 | 600519 (4.336236) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[11]` | 存在多个候选，需区分 | 301 / 105 | 6 家族 / 301 对 / 本源 14 日 | 600519 (4.338508) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `fuyao.valuation.ps_ttm` | 存在多个候选，需区分 | 340 / 104 | 6 家族 / 340 对 / 本源 12 日 | 600519 (10.658117) | ulist239.f130 (robust_correlation,affine_formula,per_stock_time_series); tencent[46] (robust_correlation,per_stock_time_series) |
| `sina[23]` | 存在多个候选，需区分 | 338 / 103 | 6 家族 / 338 对 / 本源 14 日 | 600519 (6.356284) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[25]` | 存在多个候选，需区分 | 338 / 103 | 6 家族 / 338 对 / 本源 14 日 | 600519 (6.358085) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[27]` | 存在多个候选，需区分 | 338 / 103 | 6 家族 / 338 对 / 本源 14 日 | 600519 (6.36181) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[29]` | 存在多个候选，需区分 | 338 / 103 | 6 家族 / 338 对 / 本源 14 日 | 600519 (6.3638) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[21]` | 存在多个候选，需区分 | 301 / 90 | 6 家族 / 301 对 / 本源 14 日 | 600519 (3.777115) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[23]` | 存在多个候选，需区分 | 301 / 90 | 6 家族 / 301 对 / 本源 14 日 | 600519 (3.779141) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[25]` | 存在多个候选，需区分 | 301 / 90 | 6 家族 / 301 对 / 本源 14 日 | 600519 (3.781396) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[27]` | 存在多个候选，需区分 | 301 / 90 | 6 家族 / 301 对 / 本源 14 日 | 600519 (3.78357) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `ulist239.f133` | 存在多个候选，需区分 | 255 / 90 | 6 家族 / 255 对 / 本源 0 日 | 600519 (39.249922) | tencent[64] (robust_correlation,per_stock_time_series); tencent[53] (robust_correlation,per_stock_time_series) |
| `push2.f108` | 存在多个候选，需区分 | 255 / 83 | 6 家族 / 255 对 / 本源 0 日 | 600519 (58.069117) | tencent[9] (robust_correlation,affine_formula); tencent[68] (robust_correlation,affine_formula) |
| `push2.f160` | 存在多个候选，需区分 | 255 / 83 | 6 家族 / 255 对 / 本源 0 日 | 600519 (18.961757) | tencent[9] (robust_correlation,affine_formula); tencent[68] (robust_correlation,affine_formula) |
| `zhb.full.dividend_yield` | 存在多个候选，需区分 | 202 / 83 | 6 家族 / 202 对 / 本源 9 日 | 600519 (47.982297) | tencent[64] (robust_correlation,per_stock_time_series); tencent[9] (per_stock_time_series) |
| `zhb.full.change_20k_bar` | 存在多个候选，需区分 | 202 / 78 | 6 家族 / 202 对 / 本源 0 日 | 600825 (3.240401) | tencent[70] (robust_correlation,affine_formula,per_stock_time_series); ulist239.f110 (robust_correlation,affine_formula,per_stock_time_series) |
| `push2ex.circulating_value` | 存在多个候选，需区分 | 255 / 77 | 6 家族 / 255 对 / 本源 0 日 | no_shared_stock_holdout | kph.turnover (robust_correlation,per_stock_time_series); tencent[45] (robust_correlation,affine_formula) |
| `push2ex.total_value` | 存在多个候选，需区分 | 255 / 77 | 6 家族 / 255 对 / 本源 0 日 | no_shared_stock_holdout | kph.turnover (robust_correlation,per_stock_time_series); tencent[45] (robust_correlation,affine_formula) |
| `zhb.full.change_ytd` | 存在多个候选，需区分 | 202 / 77 | 6 家族 / 202 对 / 本源 9 日 | 600825 (1.745608) | tencent[75] (robust_correlation,affine_formula,per_stock_time_series); tencent[62] (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.change_250k_bar` | 存在多个候选，需区分 | 202 / 73 | 6 家族 / 202 对 / 本源 9 日 | 002242 (1.912653) | tencent[79] (robust_correlation,affine_formula,per_stock_time_series); tencent[75] (robust_correlation,per_stock_time_series) |
| `push2.f135` | 存在多个候选，需区分 | 255 / 71 | 6 家族 / 255 对 / 本源 0 日 | 600519 (0.080354) | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.change_30k_bar_ref` | 存在多个候选，需区分 | 202 / 70 | 6 家族 / 202 对 / 本源 9 日 | 600519 (6.006441) | tencent[75] (robust_correlation,per_stock_time_series); tencent[70] (robust_correlation,per_stock_time_series) |
| `em_fund_flow.f136` | 存在多个候选，需区分 | 255 / 68 | 6 家族 / 255 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.unknown_26` | 存在多个候选，需区分 | 202 / 67 | 6 家族 / 202 对 / 本源 0 日 | 600519 (13.220347) | tencent[38] (robust_correlation,per_stock_time_series); tencent[9] (per_stock_time_series) |
| `zhb.stat.unknown_26` | 存在多个候选，需区分 | 202 / 67 | 6 家族 / 202 对 / 本源 0 日 | 600519 (13.220347) | tencent[38] (robust_correlation,per_stock_time_series); tencent[9] (per_stock_time_series) |
| `em_fund_flow.f135` | 存在多个候选，需区分 | 255 / 66 | 6 家族 / 255 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.change_60k_bar` | 存在多个候选，需区分 | 202 / 64 | 6 家族 / 202 对 / 本源 0 日 | 600825 (4.196431) | tencent[71] (robust_correlation,affine_formula,per_stock_time_series); push2.f121 (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.zt_streak_cycle` | 存在多个候选，需区分 | 202 / 64 | 6 家族 / 202 对 / 本源 0 日 | 301190 (2.061683) | ftshare_rest.change_rate_day5 (robust_correlation,per_stock_time_series); ftshare_rest.change_rate_day10 (robust_correlation,per_stock_time_series) |
| `zhb.full.pe_lyr` | 存在多个候选，需区分 | 202 / 63 | 6 家族 / 202 对 / 本源 9 日 | 600519 (11.358646) | tencent[53] (robust_correlation,affine_formula,per_stock_time_series); ulist239.f114 (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.stat.pe_lyr` | 存在多个候选，需区分 | 202 / 63 | 6 家族 / 202 对 / 本源 9 日 | 600519 (11.358646) | tencent[53] (robust_correlation,affine_formula,per_stock_time_series); ulist239.f114 (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f136` | 存在多个候选，需区分 | 255 / 62 | 6 家族 / 255 对 / 本源 0 日 | candidates_converge_on_existing_samples | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f176` | 存在多个候选，需区分 | 255 / 61 | 6 家族 / 255 对 / 本源 0 日 | 600519 (13.617211) | tencent[46] (robust_correlation,per_stock_time_series); fuyao.valuation.pb_mrq (robust_correlation,per_stock_time_series) |
| `tdx.finance_info.eps` | 存在多个候选，需区分 | 202 / 61 | 6 家族 / 202 对 / 本源 0 日 | no_shared_stock_holdout | push2.f55 (robust_correlation,affine_formula,per_stock_time_series); tencent[9] (robust_correlation,affine_formula) |
| `ulist239.f63` | 存在多个候选，需区分 | 255 / 59 | 6 家族 / 255 对 / 本源 0 日 | candidates_converge_on_existing_samples | tencent[57] (robust_correlation,per_stock_time_series); tencent[37] (robust_correlation,per_stock_time_series) |
| `zhb.full.change_30k_bar` | 存在多个候选，需区分 | 202 / 59 | 6 家族 / 202 对 / 本源 9 日 | 600825 (3.699484) | tencent[75] (robust_correlation,per_stock_time_series); tencent[71] (robust_correlation,per_stock_time_series) |
| `zhb.full.high_52w` | 存在多个候选，需区分 | 202 / 57 | 6 家族 / 202 对 / 本源 9 日 | 600519 (20.610561) | tencent[67] (robust_correlation,affine_formula,per_stock_time_series); ftshare_rest.high (robust_correlation,affine_formula,semantic_label) |
| `push2.f139` | 存在多个候选，需区分 | 255 / 52 | 6 家族 / 255 对 / 本源 0 日 | candidates_converge_on_existing_samples | tencent[57] (robust_correlation,per_stock_time_series); tencent[37] (robust_correlation,per_stock_time_series) |
| `push2.f138` | 存在多个候选，需区分 | 255 / 51 | 6 家族 / 255 对 / 本源 0 日 | 600519 (5.184828) | zhb.stat2.amount (robust_correlation,per_stock_time_series); zhb.full.amount (robust_correlation,per_stock_time_series) |
| `ulist239.f149` | 存在多个候选，需区分 | 255 / 50 | 6 家族 / 255 对 / 本源 0 日 | 600519 (23.225983) | tencent[69] (robust_correlation,per_stock_time_series); tencent[63] (robust_correlation,per_stock_time_series) |
| `em_fund_flow.f139` | 存在多个候选，需区分 | 255 / 47 | 6 家族 / 255 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,per_stock_time_series); tencent[37] (robust_correlation,per_stock_time_series) |
| `push2.f49` | 存在多个候选，需区分 | 255 / 47 | 6 家族 / 255 对 / 本源 0 日 | 601288 (9.989006) | sina[8] (robust_correlation,affine_formula,per_stock_time_series); ftshare_rest.volume (robust_correlation,affine_formula,per_stock_time_series) |

_此表显示优先级最高的 50 / 共 328 个目标；完整清单见 JSON。_


### 舍入近似数值线索（仅研究，不算 L1/L1-U；74 组）

近似窗口只用于提示复核：需核对双方原始单位、展示精度和来源口径；不得把该命中率当作字段语义结论或注册表写回依据。完整明细在 JSON `candidate_triage.approximate_matches`。

| 左字段 | 右字段 | 近似命中率 | 精确/舍入命中 | 有效日期 | 最大误差（绝对/相对） |
|:--|:--|--:|:--|:--|:--|
| `zhb.full.pe_lyr` | `tencent[53]` | 100.00% | 1/179 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104 | 0.0060000000000854925 / 0.0005447531378891637 |
| `zhb.stat.pe_lyr` | `tencent[53]` | 100.00% | 1/179 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104 | 0.0060000000000854925 / 0.0005447531378891637 |
| `ulist239.f142` | `sina[11]` | 100.00% | 0/80 | T:20261102, T:20261103, T:20261104, T:20261105 | 0.5 / 0.00467289719626179 |
| `ulist239.f142` | `sina[6]` | 100.00% | 0/80 | T:20261102, T:20261103, T:20261104, T:20261105 | 0.5 / 0.00467289719626179 |
| `ulist239.f142` | `tencent[9]` | 100.00% | 0/80 | T:20261102, T:20261103, T:20261104, T:20261105 | 0.5 / 0.00467289719626179 |
| `ulist239.f143` | `sina[21]` | 100.00% | 0/76 | T:20261102, T:20261103, T:20261104, T:20261105 | 0.05999999999994543 / 0.004629629629629736 |
| `ulist239.f143` | `sina[7]` | 100.00% | 0/76 | T:20261102, T:20261103, T:20261104, T:20261105 | 0.05999999999994543 / 0.004629629629629736 |
| `ulist239.f143` | `tencent[19]` | 100.00% | 0/76 | T:20261102, T:20261103, T:20261104, T:20261105 | 0.05999999999994543 / 0.004629629629629736 |
| `zhb.full.pe_lyr` | `ulist239.f114` | 100.00% | 1/59 | T:20261102, T:20261103, T:20261104 | 0.004899999999999238 / 0.00043661226044383074 |
| `zhb.stat.pe_lyr` | `ulist239.f114` | 100.00% | 1/59 | T:20261102, T:20261103, T:20261104 | 0.004899999999999238 / 0.00043661226044383074 |
| `sina[23]` | `tencent[19]` | 98.51% | 0/264 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 | 0.19000000000005457 / 0.0046511627906975755 |
| `tencent[21]` | `sina[21]` | 98.51% | 0/264 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 | 0.19000000000005457 / 0.0046511627906975755 |
| `tencent[21]` | `sina[7]` | 98.51% | 0/264 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 | 0.19000000000005457 / 0.0046511627906975755 |
| `sina[13]` | `tencent[9]` | 98.20% | 0/273 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 | 2.0 / 0.004975124378109473 |
| `tencent[11]` | `sina[11]` | 98.20% | 0/273 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 | 2.0 / 0.004975124378109473 |
| `tencent[11]` | `sina[6]` | 98.20% | 0/273 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 | 2.0 / 0.004975124378109473 |
| `ulist239.f143` | `ftshare_rest.close` | 97.37% | 0/74 | T:20261102, T:20261103, T:20261104, T:20261105 | 0.05999999999999872 / 0.004633204633204535 |
| `ulist239.f143` | `fuyao.snapshot.last_price` | 97.37% | 0/74 | T:20261102, T:20261103, T:20261104, T:20261105 | 0.05999999999999872 / 0.004633204633204535 |
| `ulist239.f143` | `sina[3]` | 97.37% | 0/74 | T:20261102, T:20261103, T:20261104, T:20261105 | 0.05999999999999872 / 0.004633204633204535 |
| `ulist239.f143` | `tencent[3]` | 97.37% | 0/74 | T:20261102, T:20261103, T:20261104, T:20261105 | 0.05999999999999872 / 0.004633204633204535 |
| `sina[13]` | `push2.f179` | 93.75% | 0/75 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.0 / 0.003878975950349163 |
| `sina[13]` | `push2.f43` | 93.75% | 0/75 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.0 / 0.003878975950349163 |
| `sina[13]` | `ulist239.f144` | 93.75% | 0/75 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.0 / 0.003878975950349163 |
| `sina[13]` | `ulist239.f2` | 93.75% | 0/75 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.0 / 0.003878975950349163 |
| `tencent[11]` | `push2.f179` | 93.75% | 0/75 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.0 / 0.003878975950349163 |
| `tencent[11]` | `push2.f43` | 93.75% | 0/75 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.0 / 0.003878975950349163 |
| `tencent[11]` | `ulist239.f144` | 93.75% | 0/75 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.0 / 0.003878975950349163 |
| `tencent[11]` | `ulist239.f2` | 93.75% | 0/75 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.0 / 0.003878975950349163 |
| `ulist239.f142` | `ftshare_rest.close` | 93.75% | 0/75 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.0 / 0.003878975950349163 |
| `ulist239.f142` | `fuyao.snapshot.last_price` | 93.75% | 0/75 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.0 / 0.003878975950349163 |
| `ulist239.f142` | `sina[3]` | 93.75% | 0/75 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.0 / 0.003878975950349163 |
| `ulist239.f142` | `tencent[3]` | 93.75% | 0/75 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.0 / 0.003878975950349163 |
| `push2.f192` | `tencent[50]` | 93.75% | 68/7 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.0 / 0.003937007874015748 |
| `sina[25]` | `tencent[19]` | 93.28% | 0/250 | T:20261015, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 | 0.38000000000010914 / 0.004920721705850184 |
| `tencent[23]` | `sina[21]` | 93.28% | 0/250 | T:20261015, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 | 0.38000000000010914 / 0.004920721705850184 |
| `tencent[23]` | `sina[7]` | 93.28% | 0/250 | T:20261015, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105 | 0.38000000000010914 / 0.004920721705850184 |
| `zhb.full.change_250k_bar` | `tencent[79]` | 92.74% | 122/44 | T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104 | 0.11999999999999744 / 0.004822446295484412 |
| `sina[15]` | `push2.f179` | 92.50% | 0/74 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.4300000000000637 / 0.00465838509316774 |
| `sina[15]` | `push2.f43` | 92.50% | 0/74 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.4300000000000637 / 0.00465838509316774 |
| `sina[15]` | `ulist239.f144` | 92.50% | 0/74 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.4300000000000637 / 0.00465838509316774 |
| `sina[15]` | `ulist239.f2` | 92.50% | 0/74 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.4300000000000637 / 0.00465838509316774 |
| `sina[23]` | `push2.f179` | 92.50% | 0/74 | T:20261103, T:20261104, T:20261105 | 0.05999999999999872 / 0.004633204633204535 |
| `sina[23]` | `push2.f43` | 92.50% | 0/74 | T:20261103, T:20261104, T:20261105 | 0.05999999999999872 / 0.004633204633204535 |
| `sina[23]` | `ulist239.f144` | 92.50% | 0/74 | T:20261103, T:20261104, T:20261105 | 0.05999999999999872 / 0.004633204633204535 |
| `sina[23]` | `ulist239.f2` | 92.50% | 0/74 | T:20261103, T:20261104, T:20261105 | 0.05999999999999872 / 0.004633204633204535 |
| `tencent[13]` | `push2.f179` | 92.50% | 0/74 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.4300000000000637 / 0.00465838509316774 |
| `tencent[13]` | `push2.f43` | 92.50% | 0/74 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.4300000000000637 / 0.00465838509316774 |
| `tencent[13]` | `ulist239.f144` | 92.50% | 0/74 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.4300000000000637 / 0.00465838509316774 |
| `tencent[13]` | `ulist239.f2` | 92.50% | 0/74 | T:20261102, T:20261103, T:20261104, T:20261105 | 1.4300000000000637 / 0.00465838509316774 |
| `tencent[21]` | `push2.f179` | 92.50% | 0/74 | T:20261103, T:20261104, T:20261105 | 0.05999999999999872 / 0.004633204633204535 |

_显示前 50 / 共 74 组；按报告 SHA 和完整字段路径分页读取 JSON。_


### 补足全局截断的字段候选（206）

| 未知字段 | 候选字段 | 方法 | 样本 | 日期 | 来源 |
|:--|:--|:--|--:|:--|:--|
| `axdata.data.float_shares` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula, semantic_label | 199 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.free_float_shares` | `ftshare_rest.shares` | robust_correlation, affine_formula | 199 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.limit_stat_days` | `ftshare_rest.change_rate_day5` | robust_correlation, per_stock_time_series | 37 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.limit_up_count_in_stat_days` | `ftshare_rest.prev_close` | per_stock_time_series | 37 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.limit_up_streak_days` | `ftshare_rest.change_rate_day5` | robust_correlation | 26 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.open_amount` | `ftshare_rest.volume` | robust_correlation | 199 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.open_prev_amount_ratio` | `ftshare_rest.turnover` | robust_correlation | 199 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.open_prev_seal_ratio` | `ftshare_rest.open` | robust_correlation | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261102 | axdata, ftshare_rest |
| `axdata.data.open_price` | `ftshare_rest.prev_close` | robust_correlation, affine_formula, per_stock_time_series | 199 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.open_turnover_z` | `ftshare_rest.turnover_rate` | robust_correlation | 199 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.open_volume_hand` | `ftshare_rest.volume` | robust_correlation | 199 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.open_volume_ratio` | `ftshare_rest.turnover` | robust_correlation | 199 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.pre_close` | `ftshare_rest.prev_close` | robust_correlation, affine_formula, per_stock_time_series | 199 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.prev2_seal_amount` | `ftshare_rest.change_rate_day5` | robust_correlation | 12 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.prev_amount` | `ftshare_rest.volume` | robust_correlation | 199 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.prev_open_amount` | `ftshare_rest.volume` | robust_correlation | 197 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.prev_open_volume_hand` | `ftshare_rest.volume` | robust_correlation | 197 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.prev_seal_amount` | `ftshare_rest.change_rate_day5` | robust_correlation | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261102 | axdata, ftshare_rest |
| `axdata.data.seal_prev_ratio` | `ftshare_rest.change_rate_day5` | robust_correlation | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261102 | axdata, ftshare_rest |
| `axdata.data.seal_to_float_ratio` | `ftshare_rest.turnover_rate` | robust_correlation | 199 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `axdata.data.year_limit_up_days` | `ftshare_rest.volume` | per_stock_time_series | 199 | T:20261020, T:20261023, T:20261026, T:20261028, T:20261029 | axdata, ftshare_rest |
| `eltdx.limit_ladder.auction_prev_volume_ratio` | `tencent[69]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.beta_60d` | `tencent[76]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.float_shares` | `tencent[76]` | robust_correlation, affine_formula | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.free_float_shares` | `tencent[76]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.ladder_level` | `tencent[70]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_amount` | `tencent[79]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_change_pct` | `tencent[73]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_prev_amount_ratio` | `tencent[67]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_price` | `tencent[9]` | robust_correlation, affine_formula | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_turnover_z` | `tencent[79]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_volume_hand` | `tencent[79]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_volume_ratio` | `tencent[67]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.pe_ttm` | `tencent[53]` | robust_correlation, affine_formula | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.pre_close` | `tencent[9]` | robust_correlation, affine_formula | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.prev_amount` | `tencent[71]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.prev_open_amount` | `tencent[79]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.prev_open_volume_hand` | `tencent[79]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.seal_amount` | `tencent[50]` | robust_correlation, affine_formula | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.seal_to_amount_ratio` | `tencent[50]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.seal_to_float_ratio` | `tencent[68]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.year_limit_up_days` | `tencent[79]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `em_fund_flow.f135` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 93 | T:20261019, T:20261102, T:20261103, T:20261104, T:20261105 | em_fund_flow, tencent |
| `em_fund_flow.f136` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 89 | T:20261019, T:20261102, T:20261103, T:20261104, T:20261105 | em_fund_flow, tencent |
| `em_fund_flow.f139` | `tencent[57]` | robust_correlation, per_stock_time_series | 78 | T:20261019, T:20261102, T:20261103, T:20261104, T:20261105 | em_fund_flow, tencent |
| `em_fund_flow.f149` | `zhb.tipinfo.div_amount` | per_stock_time_series | 40 | T:20261019, T:20261102, T:20261103, T:20261104 | em_fund_flow, zhb |
| `em_kline_f61.dktotal` | `tencent[30]` | per_stock_time_series | 80 | T:20261102, T:20261103, T:20261104, T:20261105 | em_kline_f61, tencent |
| `event_dc.AMPLITUDE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.CHANGE` | `ftshare_rest.change_rate` | robust_correlation, affine_formula, semantic_label | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.CHANGE_RATE` | `ftshare_rest.change_rate` | robust_correlation, affine_formula, semantic_label | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.CLOSE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.EACHBALLOT_SHARES` | `ftshare_rest.shares` | semantic_label | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.INDUSTRY_PE` | `ftshare_rest.ts_millis` | robust_correlation | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.INDUSTRY_PE_NEW` | `ftshare_rest.ts_millis` | robust_correlation | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.IPO_YIELD` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.ISSUE_NUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.ISSUE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LATELY_PRICE` | `ftshare_rest.close` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LD_AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LD_CLOSE_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LD_HIGH_CHANG` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LD_OPEN_PREMIUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LIMIT_UP_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.MZYQ_PAY_FUND` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.OD_HIGH_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.OPEN_AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.OPEN_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.PROFIT` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TCHANGE_RATE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TNEW_PRICE` | `ftshare_rest.close` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TOTAL_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TOTAL_ISSUE_NUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TOTAL_SHARES` | `ftshare_rest.shares` | robust_correlation, affine_formula, semantic_label | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TURNOVERRATE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.fetched_at` | `ftshare_rest.ts_millis` | robust_correlation, affine_formula | 22 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `fuyao.valuation.ps_ttm` | `ulist239.f130` | robust_correlation, affine_formula, per_stock_time_series | 80 | T:20261102, T:20261103, T:20261104, T:20261105 | fuyao, ulist239 |
| `kph.industry_limit_up_count` | `push2ex.limit_count` | semantic_label | 377 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028 | kph, push2ex |
| `kpl.amplitude` | `push2ex.limit_fund` | per_stock_time_series | 837 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.main_buy` | `push2ex.amount` | robust_correlation, per_stock_time_series | 837 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.main_sell` | `push2ex.amount` | robust_correlation, per_stock_time_series | 837 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.raw_columns.col_09` | `push2ex.amount` | robust_correlation, per_stock_time_series | 837 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.raw_columns.col_10` | `push2ex.amount` | robust_correlation, per_stock_time_series | 837 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.raw_columns.col_13` | `kph.turnover` | robust_correlation, per_stock_time_series | 420 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028 | kph, kpl |
| `kpl.raw_columns.col_16` | `push2ex.limit_fund` | per_stock_time_series | 837 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.raw_columns.col_17` | `push2ex.limit_fund` | per_stock_time_series | 837 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `push2.f103` | `zhb.tipinfo.hg_amount_yi` | robust_correlation, affine_formula | 28 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104 | push2, zhb |
| `push2.f108` | `tencent[9]` | robust_correlation, affine_formula | 134 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f109` | `tdx.finance_info.weifenlirun` | robust_correlation, affine_formula | 132 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102 | push2, tdx |
| `push2.f135` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f136` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 130 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f138` | `zhb.stat2.amount` | robust_correlation, per_stock_time_series | 70 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104 | push2, zhb |
| `push2.f139` | `tencent[57]` | robust_correlation, per_stock_time_series | 111 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f160` | `tencent[9]` | robust_correlation, affine_formula | 134 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f161` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102 | push2, sina |
| `push2.f176` | `tencent[46]` | robust_correlation, per_stock_time_series | 134 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f191` | `tencent[74]` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f192` | `tencent[50]` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f49` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 134 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102 | push2, sina |
| `push2.f62` | `zhb.tipinfo.report_period` | robust_correlation, affine_formula, per_stock_time_series | 86 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104 | push2, zhb |

_仅显示前 100 / 共 206 条字段前沿候选。_


### 双输入公式候选
本轮未发现通过留出筛选的公式候选；测试组合 9036 个。


### 已知映射与已证伪关系的候选校准

- 已登记正向对照：当前窗口有 166 组独立数值关系可评估，166 组被方法候选识别；样本不足 0 组。此计数仅检查方法覆盖，不是准确率。
- 已证伪负向对照：数值关系 0 组，其中仍有方法信号 0 组；这些信号被隔离，不进入普通候选。

### 采集覆盖异常源

- axdata: 20261021, 20261026 ({'failed': 1, 'ok': 12, 'partial': 1})
- baidu: 20261103, 20261104, 20261105 ({'deprecated': 2, 'pending_validation': 11})
- clist: 20261028, 20261029, 20261030 ({'ok': 4, 'partial': 8})
- em_fund_flow: 20261028, 20261029, 20261030 ({'ok': 4, 'partial': 9})
- em_hot: 20261103, 20261104, 20261105 ({'context_only': 12})
- em_kline_f61: 20261028, 20261029, 20261030 ({'ok': 4, 'partial': 9})
- exchange: 20261103, 20261104, 20261105 ({'context_only': 12})
- ftshare: 20261103, 20261104, 20261105 ({'deprecated': 11, 'failed': 3})
- market_sources: 20261026 ({'ok': 13, 'partial': 1})
- news_wscn_cctv: 20261015 ({'ok': 13, 'partial': 1})
- push2: 20261028, 20261029, 20261030 ({'failed': 4, 'ok': 4, 'partial': 4})
- slist: 20261028, 20261029, 20261030 ({'failed': 8, 'ok': 4})
- sse_e_interaction: 20261016 ({'ok': 13, 'partial': 1})
- st_list: 20261028, 20261029, 20261030 ({'ok': 5, 'partial': 8})
- tdx: 20261104, 20261105 ({'ok': 12, 'partial': 2})
- ulist239: 20261028, 20261029, 20261030 ({'failed': 10, 'ok': 4})
- zhb: 20261103, 20261104, 20261105 ({'ok': 4, 'partial': 10})

## 候选身份与人工审阅状态

- 候选身份：生成 6528 条，唯一候选 6528 个，重复身份 0，无效身份 0。
- 审阅台账：可用；当前状态 `pending`；已审 8，待处理 6520，覆盖率 0.1%。
- 重复归并组：0；每个成员均保留到代表候选的反向追溯。
- 处置计数：`accepted_for_adjudication` 0；`duplicate_grouped` 0；`insufficient_evidence` 3；`needs_external_evidence` 0；`rejected` 5；`unreviewed` 6520。
- `accepted_for_adjudication` 只表示可进入现有证据裁决流程；审阅台账不会修改主字典或字段注册表。

## 报告完整性与审阅范围

- 机器可读完整性：`complete`；方法候选生成 6463 条，完整明细保存 6463 条，缺失 0 条，多余 0 条，重复 0 条，身份无效 0 条。
- 全量方法候选位于同名 JSON 的 `method_candidate_inventory`；Markdown 的 Top-N 表格是导航摘要，不能代替全量 JSON 审阅。
- 候选审阅数据对账：`complete`；唯一候选 6528 个，审阅 8 个，待处理 6520 个；人工审阅进度与机器清单完整性分别统计。
- Markdown 未逐行展示、但 JSON 保留的部分：
  - `L4`：展示 60 / 62，摘要省略 2 条。
  - `method_candidates`：展示 100 / 500，摘要省略 400 条。
  - `method_candidate_inventory`：展示 0 / 6463，摘要省略 6463 条。
  - `method_candidate_frontier`：展示 100 / 206，摘要省略 106 条。
  - `candidate_triage.targets`：展示 50 / 328，摘要省略 278 条。
  - `diagnostics`：展示 100 / 281，摘要省略 181 条。
  - `candidate_triage.approximate_matches`：展示 50 / 74，摘要省略 24 条。
  - `candidate_review.human_review.reviewed_candidates`：展示 0 / 8，摘要省略 8 条。
- 完整性对账通过；逐目标复核仍须覆盖 JSON 的全部明细，并为每项记录已检查、重复归并、证据不足或需外部核验的处置。
