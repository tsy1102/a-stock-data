# 全源对撞报告（20261109）

> 交易数据窗口配置：全部历史日期（`--all`）
> 行情窗口：20261015 ~ 20261109（17 个不同交易日）｜字段 1303 个｜样本值 1103581 条
> 新闻/公告自然日窗口：20261015 ~ 20261109
> 主攻目标（unverified）=229｜可审定新候选=0｜首次发现新候选对=0｜已登记关系复验=0｜异号同义 0 / 同号镜像 0

> **规则**：L1 每日需≥18 组有效配对，并至少有5 组信息配对；双方同时为 0 或同时缺失不计命中率，一侧为 0、另一侧非 0 按失配计。信息配对命中率≥90%，且覆盖至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。JSON `daily_sample_counts` 与 `daily_informative_sample_counts`分别保留每日有效配对数和 L1 信息配对数。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 新候选 — 异号同义（跨编号，高价值）(0)

_本轮无异号同义候选。_


## 二、L1 / L1-U 新候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、已登记映射的本窗口复验（0）

_这些关系已在主注册表登记，只用于观察当前样本是否仍支持既有映射；它们不是新的未知字段候选，也不能再次提交为新定案。_

_本轮没有已登记关系进入复验窗口。_


## 四、L4 存疑候选（46）

| 左字段 | 右字段 | 命中率 | 天数 | 样本 |
|:--|:--|--:|--:|--:|
| `sina[32]` | `ulist239.f231` | 95.00% | 5 | 100 |
| `ulist239.f190` | `tdx.finance_info.hgu` | 94.90% | 5 | 98 |
| `sina[32]` | `tdx.finance_info.hgu` | 94.63% | 15 | 298 |
| `push2ex.zt_continuous` | `kph.limit_count` | 93.61% | 10 | 407 |
| `sina[32]` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 92.00% | 15 | 300 |
| `sina[32]` | `ulist239.f200` | 90.00% | 5 | 100 |
| `sina[32]` | `zhb.stat.other_qy_jzc` | 90.00% | 10 | 200 |
| `ulist239.f190` | `zhb.stat.other_qy_jzc` | 90.00% | 4 | 80 |
| `zhb.full.other_qy_jzc` | `ulist239.f231` | 90.00% | 4 | 80 |
| `sina[32]` | `tdx.finance_info.bgu` | 89.60% | 15 | 298 |
| `push2ex.zt_days` | `kpl.raw_columns.col_15` | 88.03% | 14 | 869 |
| `push2ex.zt_continuous` | `kpl.raw_columns.col_15` | 88.03% | 14 | 869 |
| `ulist239.f190` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 88.00% | 5 | 100 |
| `push2ex.zt_days` | `kph.limit_count` | 87.47% | 10 | 407 |
| `ulist239.f190` | `tdx.finance_info.bgu` | 84.69% | 5 | 98 |
| `zhb.full.other_qy_jzc` | `ulist239.f200` | 80.00% | 4 | 80 |
| `sina_extended.trade` | `fuyao.snapshot.last_price` | 76.67% | 12 | 240 |
| `sina_extended.trade` | `eltdx.quote_snapshot.last_price` | 76.15% | 13 | 260 |
| `sina_extended.trade` | `tencent[3]` | 76.15% | 13 | 260 |
| `sina_extended.trade` | `tdx.quote_raw.price` | 75.97% | 13 | 258 |
| `sina_extended.trade` | `tdx.quote_full.price` | 75.97% | 13 | 258 |
| `sina_extended.trade` | `ftshare_rest.close` | 75.00% | 12 | 240 |
| `sina_extended.trade` | `push2.f43` | 72.08% | 9 | 154 |
| `sina_extended.trade` | `push2.f179` | 72.08% | 9 | 154 |
| `sina_extended.trade` | `ulist239.f2` | 70.00% | 5 | 100 |
| `sina_extended.trade` | `ulist239.f144` | 70.00% | 5 | 100 |
| `ulist239.f11` | `tencent[80]` | 70.00% | 5 | 100 |
| `sina[32]` | `ulist239.f13` | 60.00% | 5 | 100 |
| `sina[32]` | `ulist239.f27` | 60.00% | 5 | 100 |
| `zhb.full.other_qy_jzc` | `ulist239.f13` | 60.00% | 4 | 80 |
| `zhb.full.other_qy_jzc` | `ulist239.f27` | 60.00% | 4 | 80 |
| `zhb.full.other_qy_jzc` | `push2.f107` | 57.55% | 6 | 106 |
| `zhb.full.other_qy_jzc` | `push2.f110` | 57.55% | 6 | 106 |
| `ulist239.f97` | `zhb.stat.other_qy_jzc` | 57.50% | 4 | 80 |
| `sina[32]` | `push2.f107` | 56.49% | 9 | 154 |
| `sina[32]` | `push2.f110` | 56.49% | 9 | 154 |
| `ulist239.f97` | `tdx.finance_info.hgu` | 55.10% | 5 | 98 |
| `ulist239.f97` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 54.00% | 5 | 100 |
| `ulist239.f97` | `tdx.finance_info.bgu` | 51.02% | 5 | 98 |
| `kpl.raw_columns.col_02` | `kph.limit_count` | 46.89% | 10 | 450 |
| `kpl.raw_columns.col_16` | `kph.limit_count` | 45.33% | 10 | 450 |
| `kpl.raw_columns.col_02` | `push2ex.limit_count` | 44.53% | 14 | 869 |
| `sina_extended.trade` | `tencent[9]` | 43.46% | 13 | 260 |
| `sina_extended.trade` | `tdx.quote_raw.bid1` | 43.41% | 13 | 258 |
| `sina_extended.trade` | `tdx.quote_full.bid1` | 43.41% | 13 | 258 |
| `kpl.raw_columns.col_16` | `push2ex.limit_count` | 42.92% | 14 | 869 |

## 五、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 六、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `sina_extended.turnover` | `ftshare_rest.turnover_rate` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 240 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | ftshare_rest, sina_extended | Pearson=0.9998, Spearman=0.9985, LOO稳号=True |
| `push2ex.turnover_rate` | `kph.turnover_rate` | robust_correlation, per_stock_time_series, semantic_label | 407 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028, T:20261030 | kph, push2ex | Pearson=0.8443, Spearman=0.8878, LOO稳号=True |
| `tencent[22]` | `sina[22]` | robust_correlation, affine_formula, per_stock_time_series | 300 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[18]` | `tencent[18]` | robust_correlation, affine_formula, per_stock_time_series | 300 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[16]` | `tencent[16]` | robust_correlation, affine_formula, per_stock_time_series | 300 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[14]` | `tencent[14]` | robust_correlation, affine_formula, per_stock_time_series | 300 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tdx.s_vol` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 278 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | sina, tdx | Pearson=0.9941, Spearman=0.9948, LOO稳号=True |
| `tdx.quote_raw.s_vol` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 278 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | sina, tdx | Pearson=0.9941, Spearman=0.9948, LOO稳号=True |
| `tdx.quote_raw.b_vol` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 278 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | sina, tdx | Pearson=0.9944, Spearman=0.9949, LOO稳号=True |
| `tdx.quote_full.s_vol` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 278 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | sina, tdx | Pearson=0.9941, Spearman=0.9948, LOO稳号=True |
| `tdx.quote_full.b_vol` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 278 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | sina, tdx | Pearson=0.9944, Spearman=0.9949, LOO稳号=True |
| `tdx.b_vol` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 278 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026 | sina, tdx | Pearson=0.9944, Spearman=0.9949, LOO稳号=True |
| `sina_extended.turnover` | `tencent[38]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=0.9998, Spearman=0.9986, LOO稳号=True |
| `sina_extended.trade` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=1.0, Spearman=0.9883, LOO稳号=True |
| `sina_extended.trade` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=0.9999, Spearman=0.8444, LOO稳号=True |
| `sina_extended.trade` | `tencent[5]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=0.9999, Spearman=0.9974, LOO稳号=True |
| `sina_extended.trade` | `tencent[51]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=1.0, Spearman=0.9993, LOO稳号=True |
| `sina_extended.trade` | `tencent[4]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=0.9998, Spearman=0.9968, LOO稳号=True |
| `sina_extended.trade` | `tencent[48]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=0.9998, Spearman=0.9874, LOO稳号=True |
| `sina_extended.trade` | `tencent[47]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=0.9998, Spearman=0.9921, LOO稳号=True |
| `sina_extended.trade` | `tencent[42]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=0.9999, Spearman=0.998, LOO稳号=True |
| `sina_extended.trade` | `tencent[41]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=1.0, Spearman=0.9991, LOO稳号=True |
| `sina_extended.trade` | `tencent[3]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina_extended.trade` | `tencent[34]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=0.9999, Spearman=0.998, LOO稳号=True |
| `sina_extended.trade` | `tencent[33]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=1.0, Spearman=0.9991, LOO稳号=True |
| `sina_extended.trade` | `tencent[27]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=0.9998, Spearman=0.904, LOO稳号=True |
| `sina_extended.trade` | `tencent[25]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=0.9998, Spearman=0.904, LOO稳号=True |
| `sina_extended.trade` | `tencent[23]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=0.9998, Spearman=0.904, LOO稳号=True |
| `sina_extended.trade` | `tencent[21]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=0.9998, Spearman=0.904, LOO稳号=True |
| `sina_extended.trade` | `tencent[19]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=0.9998, Spearman=0.904, LOO稳号=True |
| `sina_extended.trade` | `tencent[17]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=1.0, Spearman=0.9883, LOO稳号=True |
| `sina_extended.trade` | `tencent[15]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=1.0, Spearman=0.9883, LOO稳号=True |
| `sina_extended.trade` | `tencent[13]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=1.0, Spearman=0.9883, LOO稳号=True |
| `sina_extended.trade` | `tencent[11]` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tencent | Pearson=1.0, Spearman=0.9883, LOO稳号=True |
| `sina_extended.trade` | `eltdx.shortline.pre_close` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina_extended | Pearson=0.9998, Spearman=0.9968, LOO稳号=True |
| `sina_extended.trade` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina_extended | Pearson=0.9999, Spearman=0.9974, LOO稳号=True |
| `sina_extended.trade` | `eltdx.quote_snapshot.pre_close_price` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina_extended | Pearson=0.9998, Spearman=0.9968, LOO稳号=True |
| `sina_extended.trade` | `eltdx.quote_snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina_extended | Pearson=0.9999, Spearman=0.9974, LOO稳号=True |
| `sina_extended.trade` | `eltdx.quote_snapshot.low_price` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina_extended | Pearson=0.9999, Spearman=0.998, LOO稳号=True |
| `sina_extended.trade` | `eltdx.quote_snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina_extended | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina_extended.trade` | `eltdx.quote_snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 260 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina_extended | Pearson=1.0, Spearman=0.9991, LOO稳号=True |
| `tdx.s_vol` | `fuyao.snapshot.volume` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028 | fuyao, tdx | Pearson=0.9947, Spearman=0.9949, LOO稳号=True |
| `tdx.quote_raw.s_vol` | `fuyao.snapshot.volume` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028 | fuyao, tdx | Pearson=0.9947, Spearman=0.9949, LOO稳号=True |
| `tdx.quote_raw.b_vol` | `fuyao.snapshot.volume` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028 | fuyao, tdx | Pearson=0.9949, Spearman=0.9947, LOO稳号=True |
| `tdx.quote_full.s_vol` | `fuyao.snapshot.volume` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028 | fuyao, tdx | Pearson=0.9947, Spearman=0.9949, LOO稳号=True |
| `tdx.quote_full.b_vol` | `fuyao.snapshot.volume` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028 | fuyao, tdx | Pearson=0.9949, Spearman=0.9947, LOO稳号=True |
| `tdx.b_vol` | `fuyao.snapshot.volume` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028 | fuyao, tdx | Pearson=0.9949, Spearman=0.9947, LOO稳号=True |
| `sina_extended.trade` | `tdx.quote_raw.price` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tdx | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina_extended.trade` | `tdx.quote_raw.open` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tdx | Pearson=0.9999, Spearman=0.9973, LOO稳号=True |
| `sina_extended.trade` | `tdx.quote_raw.low` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tdx | Pearson=0.9999, Spearman=0.9979, LOO稳号=True |
| `sina_extended.trade` | `tdx.quote_raw.last_close` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tdx | Pearson=0.9998, Spearman=0.9967, LOO稳号=True |
| `sina_extended.trade` | `tdx.quote_raw.high` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tdx | Pearson=1.0, Spearman=0.9991, LOO稳号=True |
| `sina_extended.trade` | `tdx.quote_raw.bid1` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tdx | Pearson=1.0, Spearman=0.988, LOO稳号=True |
| `sina_extended.trade` | `tdx.quote_raw.ask1` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tdx | Pearson=0.9998, Spearman=0.9018, LOO稳号=True |
| `sina_extended.trade` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tdx | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina_extended.trade` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tdx | Pearson=0.9999, Spearman=0.9973, LOO稳号=True |
| `sina_extended.trade` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tdx | Pearson=0.9999, Spearman=0.9979, LOO稳号=True |
| `sina_extended.trade` | `tdx.quote_full.last_close` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tdx | Pearson=0.9998, Spearman=0.9967, LOO稳号=True |
| `sina_extended.trade` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tdx | Pearson=1.0, Spearman=0.9991, LOO稳号=True |
| `sina_extended.trade` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tdx | Pearson=1.0, Spearman=0.988, LOO稳号=True |
| `sina_extended.trade` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 258 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | sina_extended, tdx | Pearson=0.9998, Spearman=0.9018, LOO稳号=True |
| `sina_extended.trade` | `fuyao.snapshot.prev_price` | robust_correlation, affine_formula, per_stock_time_series | 240 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029 | fuyao, sina_extended | Pearson=0.9998, Spearman=0.9967, LOO稳号=True |
| `sina_extended.trade` | `fuyao.snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 240 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029 | fuyao, sina_extended | Pearson=0.9999, Spearman=0.9972, LOO稳号=True |
| `sina_extended.trade` | `fuyao.snapshot.low_price` | robust_correlation, affine_formula, per_stock_time_series | 240 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029 | fuyao, sina_extended | Pearson=0.9999, Spearman=0.9978, LOO稳号=True |
| `sina_extended.trade` | `fuyao.snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 240 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029 | fuyao, sina_extended | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina_extended.trade` | `fuyao.snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 240 | T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029 | fuyao, sina_extended | Pearson=1.0, Spearman=0.9989, LOO稳号=True |
| `sina_extended.trade` | `ftshare_rest.prev_close` | robust_correlation, affine_formula, per_stock_time_series | 240 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | ftshare_rest, sina_extended | Pearson=0.9998, Spearman=0.9966, LOO稳号=True |
| `sina_extended.trade` | `ftshare_rest.open` | robust_correlation, affine_formula, per_stock_time_series | 240 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | ftshare_rest, sina_extended | Pearson=0.9999, Spearman=0.9973, LOO稳号=True |
| `sina_extended.trade` | `ftshare_rest.low` | robust_correlation, affine_formula, per_stock_time_series | 240 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | ftshare_rest, sina_extended | Pearson=1.0, Spearman=0.9981, LOO稳号=True |
| `sina_extended.trade` | `ftshare_rest.high` | robust_correlation, affine_formula, per_stock_time_series | 240 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | ftshare_rest, sina_extended | Pearson=1.0, Spearman=0.999, LOO稳号=True |
| `sina_extended.trade` | `ftshare_rest.close` | robust_correlation, affine_formula, per_stock_time_series | 240 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | ftshare_rest, sina_extended | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina_extended.trade` | `ftshare_rest.avg` | robust_correlation, affine_formula, per_stock_time_series | 240 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | ftshare_rest, sina_extended | Pearson=1.0, Spearman=0.9991, LOO稳号=True |
| `tdx.s_vol` | `ftshare_rest.volume` | robust_correlation, affine_formula, per_stock_time_series | 238 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | ftshare_rest, tdx | Pearson=0.9963, Spearman=0.9948, LOO稳号=True |
| `tdx.quote_raw.s_vol` | `ftshare_rest.volume` | robust_correlation, affine_formula, per_stock_time_series | 238 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | ftshare_rest, tdx | Pearson=0.9963, Spearman=0.9948, LOO稳号=True |
| `tdx.quote_raw.b_vol` | `ftshare_rest.volume` | robust_correlation, affine_formula, per_stock_time_series | 238 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | ftshare_rest, tdx | Pearson=0.9962, Spearman=0.9961, LOO稳号=True |
| `tdx.quote_full.s_vol` | `ftshare_rest.volume` | robust_correlation, affine_formula, per_stock_time_series | 238 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | ftshare_rest, tdx | Pearson=0.9963, Spearman=0.9948, LOO稳号=True |
| `tdx.quote_full.b_vol` | `ftshare_rest.volume` | robust_correlation, affine_formula, per_stock_time_series | 238 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | ftshare_rest, tdx | Pearson=0.9962, Spearman=0.9961, LOO稳号=True |
| `tdx.b_vol` | `ftshare_rest.volume` | robust_correlation, affine_formula, per_stock_time_series | 238 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | ftshare_rest, tdx | Pearson=0.9962, Spearman=0.9961, LOO稳号=True |
| `zhb.full.change_60k_bar` | `tencent[71]` | robust_correlation, affine_formula, per_stock_time_series | 200 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=0.9945, Spearman=0.9782, LOO稳号=True |
| `zhb.full.change_20k_bar` | `tencent[70]` | robust_correlation, affine_formula, per_stock_time_series | 200 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030 | tencent, zhb | Pearson=0.9915, Spearman=0.9717, LOO稳号=True |
| `sina_extended.turnover` | `push2.f168` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, sina_extended | Pearson=0.9998, Spearman=0.9982, LOO稳号=True |
| `sina_extended.trade` | `push2.f45` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, sina_extended | Pearson=1.0, Spearman=0.9976, LOO稳号=True |
| `sina_extended.trade` | `push2.f44` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, sina_extended | Pearson=1.0, Spearman=0.9989, LOO稳号=True |
| `sina_extended.trade` | `push2.f43` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, sina_extended | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina_extended.trade` | `push2.f179` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, sina_extended | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `push2.f49` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, sina | Pearson=0.9948, Spearman=0.9948, LOO稳号=True |
| `push2.f49` | `ftshare_rest.volume` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | ftshare_rest, push2 | Pearson=0.9948, Spearman=0.9948, LOO稳号=True |
| `push2.f49` | `eltdx.quote_snapshot.total_hand` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | eltdx, push2 | Pearson=0.9948, Spearman=0.9948, LOO稳号=True |
| `push2.f49` | `eltdx.quote_snapshot.outer_disc` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | eltdx, push2 | Pearson=0.9981, Spearman=0.9981, LOO稳号=True |
| `push2.f49` | `eltdx.quote_snapshot.inside_dish` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | eltdx, push2 | Pearson=0.9835, Spearman=0.9829, LOO稳号=True |
| `push2.f161` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, sina | Pearson=0.9948, Spearman=0.994, LOO稳号=True |
| `push2.f161` | `ftshare_rest.volume` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | ftshare_rest, push2 | Pearson=0.9948, Spearman=0.994, LOO稳号=True |
| `push2.f161` | `eltdx.quote_snapshot.total_hand` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | eltdx, push2 | Pearson=0.9948, Spearman=0.994, LOO稳号=True |
| `push2.f161` | `eltdx.quote_snapshot.outer_disc` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | eltdx, push2 | Pearson=0.9834, Spearman=0.9823, LOO稳号=True |
| `push2.f161` | `eltdx.quote_snapshot.inside_dish` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | eltdx, push2 | Pearson=0.9981, Spearman=0.9981, LOO稳号=True |
| `push2.f135` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tencent | Pearson=0.9829, Spearman=0.9906, LOO稳号=True |
| `push2.f135` | `tencent[37]` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, tencent | Pearson=0.9829, Spearman=0.9906, LOO稳号=True |
| `push2.f135` | `sina[9]` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | push2, sina | Pearson=0.9829, Spearman=0.9906, LOO稳号=True |
| `push2.f135` | `ftshare_rest.turnover` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | ftshare_rest, push2 | Pearson=0.9829, Spearman=0.9906, LOO稳号=True |
| `push2.f135` | `eltdx.quote_snapshot.amount` | robust_correlation, affine_formula, per_stock_time_series | 154 | T:20261020, T:20261023, T:20261026, T:20261029, T:20261102, T:20261103 | eltdx, push2 | Pearson=0.9829, Spearman=0.9906, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 七、日期与数据质量告警（284）

- 20261017: 无 meta.data_date 的非交易日目录不符合数据日命名规则；行情快照跳过，不按运行日推断
- 20261018: 无 meta.data_date 的非交易日目录不符合数据日命名规则；行情快照跳过，不按运行日推断
- 20261031: 无 meta.data_date 的非交易日目录不符合数据日命名规则；行情快照跳过，不按运行日推断
- 20261101: 无 meta.data_date 的非交易日目录不符合数据日命名规则；行情快照跳过，不按运行日推断
- 20261107: 无 meta.data_date 的非交易日目录不符合数据日命名规则；行情快照跳过，不按运行日推断
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
- 另有 184 条告警，详见同名 JSON 报告。

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

策略状态：`invalid`；逐源分类字段 0，保守默认未分类字段 1303。L1/L1-C 日期证据：来源日期已确认 0 条，跨源值见证推断 0 条，仅语义证据且日期未确认 0 条，其他日期未确认 0 条。

_本轮 L1/L1-C 没有仅凭静态或缓变字段、且来源日期未确认的关系。_

## 来源字段覆盖与碰撞参与

_窗口字段值样本是经日期筛选、重复折叠和快照择优后载入的非空值；右侧比较次数另受字段类型及来源规则筛选。官方契约字段须有逐字段审定证据，契约语义本身不证明底层数据来源独立。_

| 来源 | 已确认字段 | 契约已确认 | 契约锚 | 独立锚 | L1-C 锚 | 窗口字段 / 字段值样本 / 交易日 |
|:--|--:|--:|--:|--:|--:|--:|
| axdata | 34 | 0 | 0 | 0 | 0 | 34 / 7459 / 14 |
| clist | 20 | 0 | 0 | 20 | 0 | 33 / 35835 / 5 |
| cls | 4 | 0 | 0 | 4 | 0 | 5 / 3500 / 0 |
| datacenter | 41 | 0 | 0 | 41 | 0 | 0 / 0 / 0 |
| eltdx | 69 | 0 | 0 | 69 | 0 | 116 / 16507 / 15 |
| em_fund_flow | 0 | 0 | 0 | 0 | 0 | 15 / 1695 / 6 |
| em_hot | 39 | 0 | 0 | 39 | 0 | 0 / 0 / 0 |
| em_kline_f61 | 10 | 0 | 0 | 10 | 0 | 2 / 200 / 5 |
| etf | 0 | 0 | 0 | 0 | 0 | 9 / 163368 / 14 |
| event_dc | 0 | 0 | 0 | 0 | 0 | 148 / 401211 / 13 |
| exchange | 4 | 0 | 0 | 4 | 0 | 0 / 0 / 0 |
| ftshare | 6 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| ftshare_rest | 31 | 31 | 31 | 0 | 31 | 32 / 7620 / 12 |
| fuyao | 88 | 74 | 74 | 88 | 0 | 20 / 5220 / 14 |
| kph | 12 | 0 | 0 | 12 | 0 | 15 / 7215 / 11 |
| kpl | 10 | 0 | 0 | 10 | 0 | 28 / 31278 / 15 |
| market_sources | 14 | 0 | 0 | 0 | 0 | 74 / 114026 / 15 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 2 / 336 / 0 |
| push2 | 50 | 0 | 0 | 50 | 0 | 114 / 17556 / 9 |
| push2ex | 24 | 0 | 0 | 24 | 0 | 16 / 20880 / 14 |
| reports | 26 | 0 | 0 | 26 | 0 | 49 / 784 / 0 |
| research_sina | 0 | 0 | 0 | 0 | 0 | 6 / 4788 / 0 |
| sina | 27 | 0 | 0 | 27 | 0 | 39 / 10350 / 15 |
| sina_extended | 0 | 0 | 0 | 0 | 0 | 4 / 1040 / 13 |
| slist | 5 | 0 | 0 | 5 | 0 | 1 / 100 / 5 |
| sse_e_interaction | 0 | 0 | 0 | 0 | 0 | 8 / 1120 / 0 |
| st_list | 0 | 0 | 0 | 0 | 0 | 6 / 11932 / 6 |
| tdx | 194 | 77 | 77 | 194 | 0 | 65 / 18632 / 15 |
| tencent | 76 | 0 | 0 | 76 | 0 | 88 / 26370 / 15 |
| ulist239 | 51 | 0 | 0 | 51 | 0 | 240 / 23940 / 5 |
| zhb | 201 | 18 | 18 | 201 | 0 | 124 / 21976 / 10 |

| 来源 | 破解目标 | 比较字段 | 作目标比较 | 作右侧比较 | L1-C 锚比较 | L1 / L1-C / L4 关系 | 方法候选涉及 |
|:--|--:|--:|--:|--:|--:|--:|--:|
| axdata | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| clist | 10 | 17 | 3021 | 1394 | 0 | 0 / 0 / 0 | 0 |
| cls | 2 | 0 | 476 | 0 | 0 | 0 / 0 / 0 | 0 |
| datacenter | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| eltdx | 28 | 53 | 6732 | 4390 | 0 | 0 / 0 / 4 | 496 |
| em_fund_flow | 4 | 0 | 1336 | 0 | 0 | 0 / 0 / 0 | 194 |
| em_hot | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| em_kline_f61 | 1 | 0 | 334 | 0 | 0 | 0 / 0 / 0 | 49 |
| etf | 4 | 0 | 29 | 0 | 0 | 0 / 0 / 0 | 0 |
| event_dc | 62 | 0 | 1258 | 0 | 0 | 0 / 0 / 0 | 246 |
| exchange | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare_rest | 1 | 25 | 23 | 4637 | 4637 | 0 / 0 / 1 | 498 |
| fuyao | 1 | 13 | 439 | 1807 | 0 | 0 / 0 / 1 | 266 |
| kph | 1 | 9 | 444 | 1129 | 0 | 0 / 0 / 4 | 42 |
| kpl | 11 | 10 | 4384 | 2080 | 0 | 0 / 0 / 6 | 66 |
| market_sources | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| push2 | 13 | 49 | 3066 | 3718 | 0 | 0 / 0 / 6 | 930 |
| push2ex | 7 | 5 | 2338 | 410 | 0 | 0 / 0 / 6 | 327 |
| reports | 11 | 6 | 2398 | 417 | 0 | 0 / 0 / 0 | 0 |
| research_sina | 2 | 0 | 450 | 0 | 0 | 0 / 0 / 0 | 0 |
| sina | 8 | 26 | 3432 | 2992 | 0 | 0 / 0 / 10 | 476 |
| sina_extended | 3 | 0 | 1287 | 0 | 0 | 0 / 0 / 13 | 196 |
| slist | 1 | 0 | 334 | 0 | 0 | 0 / 0 / 0 | 6 |
| sse_e_interaction | 2 | 0 | 25 | 0 | 0 | 0 / 0 / 0 | 0 |
| st_list | 3 | 0 | 48 | 0 | 0 | 0 / 0 / 0 | 0 |
| tdx | 8 | 52 | 2670 | 4860 | 0 | 0 / 0 / 10 | 707 |
| tencent | 8 | 70 | 2722 | 8842 | 0 | 0 / 0 / 3 | 1103 |
| ulist239 | 21 | 50 | 6695 | 3800 | 0 | 0 / 0 / 19 | 572 |
| zhb | 15 | 83 | 4005 | 7470 | 0 | 0 / 0 / 9 | 1072 |

## AxData 每日接口核验

> 此处汇总采集目录已保存的本地证据，不发起网络请求、不改变注册表状态；AxData 是多源框架，不作为独立字段锚。

### AxData

窗口内有 16 个唯一数据日的轮验记录；重复目录合并 0 条。
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

被动逐字段比较中的差异计数（跨本窗口唯一数据日累加，不含原始值）：

| 比较路径 | 相同 | 不同 | 缺失/双方空值 |
|:--|--:|--:|--:|
| `axdata_shortline_vs_eltdx:alignment_status` | 0 | 200 | 0 |
| `axdata_shortline_vs_eltdx:beta_60d` | 0 | 200 | 0 |
| `axdata_shortline_vs_eltdx:code` | 0 | 200 | 0 |
| `axdata_shortline_vs_eltdx:full_code` | 0 | 200 | 0 |
| `axdata_shortline_vs_eltdx:instrument_id` | 0 | 200 | 0 |
| `axdata_shortline_vs_eltdx:limit_status` | 0 | 200 | 0 |
| `axdata_shortline_vs_eltdx:market_id` | 0 | 200 | 0 |
| `axdata_shortline_vs_eltdx:opening_rush` | 0 | 200 | 0 |
| `axdata_shortline_vs_eltdx:pe_ttm` | 0 | 200 | 0 |
| `axdata_shortline_vs_eltdx:previous_trade_date` | 0 | 200 | 0 |
| `axdata_shortline_vs_eltdx:symbol` | 0 | 200 | 0 |
| `axdata_shortline_vs_eltdx:target_trade_date` | 0 | 200 | 0 |
| `axdata_shortline_vs_eltdx:tdx_code` | 0 | 200 | 0 |
| `axdata_shortline_vs_eltdx:open_amount` | 40 | 160 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_hand` | 40 | 160 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_ratio` | 40 | 160 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_amount_ratio` | 50 | 150 | 0 |
| `axdata_shortline_vs_eltdx:auction_prev_volume_ratio` | 56 | 141 | 3 |
| `kph_limit_up_history_vs_kpl_detail:seal_amount` | 74 | 95 | 0 |
| `kph_limit_up_history_vs_kpl_detail:seal_money` | 74 | 95 | 0 |
| `axdata_shortline_vs_eltdx:open_turnover_z` | 106 | 94 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_seal_ratio` | 4 | 8 | 188 |
| `axdata_shortline_vs_eltdx:ladder_level` | 0 | 7 | 193 |
| `axdata_shortline_vs_eltdx:limit_board_text` | 18 | 6 | 176 |

### FTShare 退役来源历史记录（显式历史研究）

窗口内保留 3 个唯一数据日的旧元数据；重复目录合并 0 条。

| 数据日 | 历史状态 | 旧接口状态计数 |
|:--|:--|:--|
| 20261015 | ok | pending: 6 |
| 20261016 | ok | pending: 6 |
| 20261019 | ok | pending: 6 |

## 字母字段名语义提示（仅候选）

窗口内观察到 149 条需审阅的字母字段路径：含词义线索 38 条，仅拆词 111 条。
完整逐条记录保存在碰撞 JSON；名称线索清单：`docs/field_verification/20261014/20261014_alphabetic_field_name_inventory.csv`。
> 拼音、英文、缩写和混合拆词只用于检索候选；必须结合原始值、接口定义和独立来源复核，不得据此定案或改写主字典。

| 逐源字段路径 | 状态/审阅范围 | 名称形式与拆词 | 词义线索（非释义） | 样本日期 |
|:--|:--|:--|:--|:--|
| `市场源(market_sources)::change_type` | unverified / unverified_semantics | snake_case_or_mixed: change type | 变化/涨跌 + 类型 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `东财-push2ex::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `东财-push2ex::first_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: first limit time | 首次/第一 + 涨跌停限制 + 时间 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `东财-push2ex::last_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: last limit time | 最近/上一期 + 涨跌停限制 + 时间 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `东财-push2ex::name` | unverified / unverified_semantics | recognized_english_word_candidate: name | 名称 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `东财-push2ex::total_value` | unverified / unverified_semantics | snake_case_or_mixed: total value | 总 + 值 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::limit_count` | verified / verified_metadata_gap | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::limit_time` | unverified / unverified_semantics | snake_case_or_mixed: limit time | 涨跌停限制 + 时间 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::plate_limit_up_count` | verified / verified_metadata_gap | snake_case_or_mixed: plate limit up count | 涨跌停限制 + 上/涨 + 数量/次数 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `财联社(cls)::time` | unverified / unverified_semantics | recognized_english_word_candidate: time | 时间 | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108 |
| `TDX(双命名源)::changqifuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: changqifuzhai | 长期负债 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::cunhuo` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: cunhuo | 存货 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::eps` | unverified / unverified_semantics | recognized_english_word_candidate: eps | 每股收益 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::fajirenfarengu` | unverified / unverified_semantics | recognized_pinyin_phrase_candidate: fajirenfarengu | 疑似 faqirenfarengu 的拼写变体；含义未证实 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::gudongrenshu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: gudongrenshu | 股东人数 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::ipodate` | unverified / unverified_semantics | recognized_english_phrase_candidate: ipodate | IPO/上市日期（字段语境候选） | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::jinglirun` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jinglirun | 净利润 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::jingyingxianjinliu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingyingxianjinliu | 经营现金流 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::jingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingzichan | 净资产 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::liudongfuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: liudongfuzhai | 流动负债 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::meigujingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: meigujingzichan | 每股净资产 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::yingshouzhangkuan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: yingshouzhangkuan | 应收账款 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::zhuyingshouru` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zhuyingshouru | 主营收入 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::zibengongjijin` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zibengongjijin | 资本公积金 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::zongzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongzichan | 总资产 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `同花顺-fuyao::snapshot.open_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot open price | 开盘 + 价格 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `新浪(扩展API)::turnover` | conflict / unverified_semantics | recognized_english_word_candidate: turnover | 换手/成交额（需看接口） | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `reports::actualLastTwoYearEps` | unverified / unverified_semantics | camel_case_or_mixed: actual Last Two Year Eps | 最近/上一期 + 每股收益 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::actualLastYearEps` | unverified / unverified_semantics | camel_case_or_mixed: actual Last Year Eps | 最近/上一期 + 每股收益 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::count` | verified / verified_metadata_gap | recognized_english_word_candidate: count | 数量/次数 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::lastEmRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Code | 最近/上一期 + 代码 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::lastEmRatingName` | conflict / unverified_semantics | camel_case_or_mixed: last Em Rating Name | 最近/上一期 + 名称 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::lastEmRatingValue` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Value | 最近/上一期 + 值 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::predictLastYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Eps | 最近/上一期 + 每股收益 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::predictLastYearPe` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Pe | 最近/上一期 + 市盈率 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `TDX-eltdx(适配层)::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `东财-push2ex::broken_count` | unverified / unverified_semantics | snake_case_or_mixed: broken count | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `东财-push2ex::circulating_value` | unverified / unverified_semantics | snake_case_or_mixed: circulating value | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `东财-push2ex::sector` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: sector | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `东财-push2ex::turnover_rate` | unverified / unverified_semantics | snake_case_or_mixed: turnover rate | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `东财-push2ex::zt_continuous` | unverified / unverified_semantics | snake_case_or_mixed: zt continuous | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `东财-push2ex::zt_days` | unverified / unverified_semantics | snake_case_or_mixed: zt days | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::one_word` | unverified / unverified_semantics | snake_case_or_mixed: one word | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::plate_amount` | verified / verified_metadata_gap | snake_case_or_mixed: plate amount | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::plate_code` | verified / verified_metadata_gap | snake_case_or_mixed: plate code | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::plate_name` | verified / verified_metadata_gap | snake_case_or_mixed: plate name | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::popular` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: popular | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `开盘啦(kpl_limit_up_detail)::raw_columns.col_19` | verified / verified_metadata_gap | runtime_tokenization_only: col 19 | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `财联社(cls)::content` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: content | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108 |
| `财联社(cls)::level` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: level | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108 |
| `财联社(cls)::reading_num` | unverified / unverified_semantics | snake_case_or_mixed: reading num | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108 |
| `财联社(cls)::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108 |
| `开盘红::industry_limit_up_count` | unverified / unverified_semantics | runtime_tokenization_only: industry limit up count | — | T:20261016, T:20261019, T:20261021, T:20261022, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104, T:20261106 |
| `TDX(双命名源)::baoliu2` | unverified / unverified_semantics | mixed_alphanumeric: baoliu 2 | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::ipo_date` | verified / verified_metadata_gap | snake_case_or_mixed: ipo date | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::updated_date` | verified / verified_metadata_gap | snake_case_or_mixed: updated date | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::updateddate` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: updateddate | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::zhuyinglyrun` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: zhuyinglyrun | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `同花顺-fuyao::fin_report` | unverified / unverified_semantics | snake_case_or_mixed: fin report | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::big_order_300w_net` | unverified / unverified_semantics | runtime_tokenization_only: big order 300 w net | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::institution_add` | unverified / unverified_semantics | runtime_tokenization_only: institution add | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::main_inflow` | unverified / unverified_semantics | snake_case_or_mixed: main inflow | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::pe_next` | unverified / unverified_semantics | runtime_tokenization_only: pe next | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::pe_now` | unverified / unverified_semantics | runtime_tokenization_only: pe now | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::strength` | unverified / unverified_semantics | runtime_tokenization_only: strength | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::total_value` | unverified / unverified_semantics | runtime_tokenization_only: total value | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::b_vol` | unverified / unverified_semantics | snake_case_or_mixed: b vol | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::b_vol` | unverified / unverified_semantics | snake_case_or_mixed: b vol | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::s_vol` | unverified / unverified_semantics | snake_case_or_mixed: s vol | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX(双命名源)::s_vol` | unverified / unverified_semantics | snake_case_or_mixed: s vol | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `同花顺-fuyao::snapshot.prev_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot prev price | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `同花顺-fuyao::valuation.ps_ttm` | conflict / unverified_semantics | snake_case_or_mixed: valuation ps ttm | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `新浪(扩展API)::netamount` | conflict / unverified_semantics | unsegmented_latin_pinyin_or_word: netamount | — | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `新浪(扩展API)::opendate` | conflict / unverified_semantics | unsegmented_latin_pinyin_or_word: opendate | — | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `新浪(扩展API)::trade` | conflict / unverified_semantics | unsegmented_latin_pinyin_or_word: trade | — | T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `FTShare REST::amplitude` | verified / verified_metadata_gap | runtime_tokenization_only: amplitude | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `FTShare REST::avg` | verified / verified_metadata_gap | runtime_tokenization_only: avg | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `FTShare REST::bid_ask_ratio` | verified / verified_metadata_gap | runtime_tokenization_only: bid ask ratio | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `FTShare REST::board` | verified / verified_metadata_gap | runtime_tokenization_only: board | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `FTShare REST::listing_date` | verified / verified_metadata_gap | runtime_tokenization_only: listing date | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `FTShare REST::name` | verified / verified_metadata_gap | runtime_tokenization_only: name | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `FTShare REST::st` | verified / verified_metadata_gap | runtime_tokenization_only: st | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `FTShare REST::status` | verified / verified_metadata_gap | runtime_tokenization_only: status | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `FTShare REST::symbol` | verified / verified_metadata_gap | runtime_tokenization_only: symbol | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `FTShare REST::symbol_id` | unverified / unverified_semantics | runtime_tokenization_only: symbol id | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `FTShare REST::turnover_rate` | verified / verified_metadata_gap | runtime_tokenization_only: turnover rate | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `ZHB-tdxstat::stat.unknown_2` | verified / verified_metadata_gap | snake_case_or_mixed: stat unknown 2 | — | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104, T:20261106 |
| `ZHB-tdxstat::stat.unknown_26` | verified / verified_metadata_gap | snake_case_or_mixed: stat unknown 26 | — | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104, T:20261106 |
| `FTShare REST::pe_ttm` | verified / verified_metadata_gap | runtime_tokenization_only: pe ttm | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `市场源(market_sources)::rank` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: rank | — | T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `TDX-eltdx(适配层)::trade_date` | unverified / unverified_semantics | snake_case_or_mixed: trade date | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 |
| `reports::attachPages` | conflict / unverified_semantics | camel_case_or_mixed: attach Pages | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::attachSize` | conflict / unverified_semantics | camel_case_or_mixed: attach Size | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::attachType` | unverified / unverified_semantics | camel_case_or_mixed: attach Type | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::column` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: column | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |
| `reports::emIndustryCode` | unverified / unverified_semantics | camel_case_or_mixed: em Industry Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105 |

Markdown 显示前 100 条；其余 49 条完整保留在 JSON。

## 探索候选持续跟踪

研究台账：`collision_research_state.json.gz`；累计历史跟踪候选对 2595，本报告候选对 640，历史复现 503，新发现 0。
台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，不会自动改变字段状态、碰撞锚或主字典。新报告只将 `actionable_L1`、L4 和主动方法候选写入待研究队列；已登记关系的复验单独展示，历史跟踪记录不会被删除。

## 候选覆盖、公式与下一步采样

本节用于定位证据缺口和安排后续取样。相关性、公式与样本优先级均为探索候选；不会改变 L1/L1-U 门槛、来源独立性或主字典。

- 未知目标 229 个；其中有方法候选 134 个、无候选 95 个；多候选目标 125 个。
- 方法候选生成 3623 条；全局详细项保留 500/500，另按目标字段保留 113 条；完整明细 3623 条在 JSON `method_candidate_inventory`；未归档明细 0 条。
- 字段覆盖详情：available；覆盖身份 1972，读取 16 份本地索引。

### 优先处理字段

| 未知字段 | 当前诊断 | 独立对比/候选数 | 独立锚家族/本源日期 | 建议复核股票 | 最强候选线索 |
|:--|:--|--:|:--|:--|:--|
| `kpl.raw_columns.col_13` | 公式候选待独立复核 | 413 / 6 | 6 家族 / 413 对 / 本源 0 日 | 300296 (1.673004) | push2ex.amount (robust_correlation,per_stock_time_series); kph.turnover (robust_correlation,per_stock_time_series); kpl.raw_columns.col_13 ≈ 104.81606 × (kph.turnover ÷ kph.turnover_rate) + 16988117 |
| `sina_extended.trade` | 存在多个候选，需区分 | 406 / 141 | 6 家族 / 406 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `fuyao.valuation.ps_ttm` | 存在多个候选，需区分 | 416 / 130 | 6 家族 / 416 对 / 本源 13 日 | 600519 (10.881821) | ulist239.f130 (robust_correlation,affine_formula,per_stock_time_series); tencent[46] (robust_correlation,per_stock_time_series) |
| `push2.f160` | 存在多个候选，需区分 | 311 / 103 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[68] (robust_correlation,affine_formula) |
| `push2.f108` | 存在多个候选，需区分 | 311 / 101 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[68] (robust_correlation,affine_formula) |
| `push2.f176` | 存在多个候选，需区分 | 311 / 94 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | tencent[46] (robust_correlation,per_stock_time_series); fuyao.valuation.pb_mrq (robust_correlation,per_stock_time_series) |
| `zhb.full.change_20k_bar` | 存在多个候选，需区分 | 244 / 93 | 6 家族 / 244 对 / 本源 0 日 | 600519 (6.691252) | tencent[70] (robust_correlation,affine_formula,per_stock_time_series); ftshare_rest.change_rate_day20 (robust_correlation,per_stock_time_series) |
| `push2ex.circulating_value` | 存在多个候选，需区分 | 311 / 87 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | tencent[45] (robust_correlation,affine_formula); tencent[44] (robust_correlation,affine_formula) |
| `push2ex.total_value` | 存在多个候选，需区分 | 311 / 87 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | kph.turnover (robust_correlation,per_stock_time_series); tencent[45] (robust_correlation,affine_formula) |
| `zhb.full.change_60k_bar` | 存在多个候选，需区分 | 244 / 82 | 6 家族 / 244 对 / 本源 0 日 | 600825 (3.786388) | tencent[71] (robust_correlation,affine_formula,per_stock_time_series); push2.f121 (robust_correlation,affine_formula,per_stock_time_series) |
| `tdx.finance_info.eps` | 存在多个候选，需区分 | 244 / 81 | 6 家族 / 244 对 / 本源 0 日 | no_shared_stock_holdout | push2.f55 (robust_correlation,affine_formula,per_stock_time_series); tencent[9] (robust_correlation,affine_formula) |
| `push2.f135` | 存在多个候选，需区分 | 311 / 79 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.unknown_26` | 存在多个候选，需区分 | 244 / 79 | 6 家族 / 244 对 / 本源 0 日 | 600519 (13.795108) | tencent[38] (robust_correlation,per_stock_time_series); tencent[9] (per_stock_time_series) |
| `em_fund_flow.f135` | 存在多个候选，需区分 | 311 / 77 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `ulist239.f63` | 存在多个候选，需区分 | 311 / 74 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | eltdx.shortline.open_volume_ratio (robust_correlation,per_stock_time_series); eltdx.shortline.open_volume_hand (robust_correlation,per_stock_time_series) |
| `push2.f136` | 存在多个候选，需区分 | 311 / 72 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `em_fund_flow.f136` | 存在多个候选，需区分 | 311 / 68 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.zt_streak_cycle` | 存在多个候选，需区分 | 244 / 64 | 6 家族 / 244 对 / 本源 0 日 | 000568 (6.311273) | ftshare_rest.change_rate_day5 (robust_correlation,per_stock_time_series); tencent[9] (per_stock_time_series) |
| `push2.f49` | 存在多个候选，需区分 | 311 / 55 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | sina[8] (robust_correlation,affine_formula,per_stock_time_series); ftshare_rest.volume (robust_correlation,affine_formula,per_stock_time_series) |
| `ulist239.f149` | 存在多个候选，需区分 | 311 / 54 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | tencent[63] (robust_correlation,per_stock_time_series); ftshare_rest.change_rate_day5 (robust_correlation,per_stock_time_series) |
| `zhb.full.zt_count` | 存在多个候选，需区分 | 244 / 54 | 6 家族 / 244 对 / 本源 0 日 | 000568 (7.400371) | ftshare_rest.change_rate_day5 (robust_correlation,per_stock_time_series); tencent[9] (per_stock_time_series) |
| `em_fund_flow.f139` | 存在多个候选，需区分 | 311 / 49 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,per_stock_time_series); tencent[37] (robust_correlation,per_stock_time_series) |
| `em_kline_f61.dktotal` | 存在多个候选，需区分 | 311 / 49 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | tencent[4] (per_stock_time_series); tencent[48] (per_stock_time_series) |
| `ulist239.f127` | 存在多个候选，需区分 | 311 / 49 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat.change_pct_2d (robust_correlation,per_stock_time_series); zhb.stat.change_5k_bar (robust_correlation,per_stock_time_series) |
| `sina[26]` | 存在多个候选，需区分 | 406 / 47 | 6 家族 / 406 对 / 本源 15 日 | 600519 (12.600474) | tencent[68] (robust_correlation); tencent[67] (robust_correlation) |
| `tdx.b_vol` | 存在多个候选，需区分 | 244 / 43 | 6 家族 / 244 对 / 本源 0 日 | no_shared_stock_holdout | sina[8] (robust_correlation,affine_formula,per_stock_time_series); fuyao.snapshot.volume (robust_correlation,affine_formula,per_stock_time_series) |
| `tdx.quote_full.b_vol` | 存在多个候选，需区分 | 244 / 43 | 6 家族 / 244 对 / 本源 0 日 | no_shared_stock_holdout | sina[8] (robust_correlation,affine_formula,per_stock_time_series); fuyao.snapshot.volume (robust_correlation,affine_formula,per_stock_time_series) |
| `tdx.quote_raw.b_vol` | 存在多个候选，需区分 | 244 / 43 | 6 家族 / 244 对 / 本源 0 日 | no_shared_stock_holdout | sina[8] (robust_correlation,affine_formula,per_stock_time_series); fuyao.snapshot.volume (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[26]` | 存在多个候选，需区分 | 363 / 42 | 6 家族 / 363 对 / 本源 15 日 | 601288 (3.825279) | sina[22] (robust_correlation); sina[20] (robust_correlation) |
| `push2.f161` | 存在多个候选，需区分 | 311 / 40 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | sina[8] (robust_correlation,affine_formula,per_stock_time_series); ftshare_rest.volume (robust_correlation,affine_formula,per_stock_time_series) |
| `sina_extended.turnover` | 存在多个候选，需区分 | 406 / 40 | 6 家族 / 406 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.turnover_rate (robust_correlation,affine_formula,per_stock_time_series,semantic_label); tencent[38] (robust_correlation,affine_formula,per_stock_time_series) |
| `ulist239.f135` | 存在多个候选，需区分 | 311 / 40 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | tencent[76] (robust_correlation,affine_formula); tencent[73] (robust_correlation,affine_formula) |
| `ulist239.f45` | 存在多个候选，需区分 | 311 / 37 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | tdx.finance_info.yingyelirun (robust_correlation,affine_formula); tdx.finance_info.weifenlirun (robust_correlation,affine_formula) |
| `eltdx.limit_ladder.open_price` | 存在多个候选，需区分 | 244 / 34 | 6 家族 / 244 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[85] (robust_correlation,affine_formula) |
| `eltdx.limit_ladder.pre_close` | 存在多个候选，需区分 | 244 / 34 | 6 家族 / 244 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[85] (robust_correlation,affine_formula) |
| `tencent[7]` | 存在多个候选，需区分 | 363 / 34 | 6 家族 / 363 对 / 本源 15 日 | 601288 (0.067281) | sina[8] (robust_correlation,per_stock_time_series); eltdx.quote_snapshot.total_hand (robust_correlation,per_stock_time_series) |
| `push2.f103` | 存在多个候选，需区分 | 311 / 33 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | zhb.tipinfo.hg_amount_yi (robust_correlation,affine_formula); tencent[65] (robust_correlation) |
| `tdx.finance_info.zhuyinglyrun` | 存在多个候选，需区分 | 244 / 33 | 6 家族 / 244 对 / 本源 0 日 | no_shared_stock_holdout | tencent[76] (robust_correlation); tencent[72] (robust_correlation) |
| `tdx.quote_full.s_vol` | 存在多个候选，需区分 | 244 / 33 | 6 家族 / 244 对 / 本源 0 日 | no_shared_stock_holdout | sina[8] (robust_correlation,affine_formula,per_stock_time_series); fuyao.snapshot.volume (robust_correlation,affine_formula,per_stock_time_series) |
| `tdx.quote_raw.s_vol` | 存在多个候选，需区分 | 244 / 33 | 6 家族 / 244 对 / 本源 0 日 | no_shared_stock_holdout | sina[8] (robust_correlation,affine_formula,per_stock_time_series); fuyao.snapshot.volume (robust_correlation,affine_formula,per_stock_time_series) |
| `tdx.s_vol` | 存在多个候选，需区分 | 244 / 33 | 6 家族 / 244 对 / 本源 0 日 | no_shared_stock_holdout | sina[8] (robust_correlation,affine_formula,per_stock_time_series); fuyao.snapshot.volume (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f109` | 存在多个候选，需区分 | 311 / 32 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | tdx.finance_info.weifenlirun (robust_correlation,affine_formula); zhb.tipinfo.hg_amount_yi (robust_correlation,affine_formula) |
| `zhb.full.cash_reserve_wan` | 存在多个候选，需区分 | 244 / 32 | 6 家族 / 244 对 / 本源 0 日 | 601288 (8.934448) | tencent[76] (robust_correlation,affine_formula); tencent[73] (robust_correlation,affine_formula) |
| `zhb.full.free_ltgb` | 存在多个候选，需区分 | 244 / 32 | 6 家族 / 244 对 / 本源 0 日 | 601288 (22.930866) | tencent[76] (robust_correlation,affine_formula); tencent[73] (robust_correlation,affine_formula) |
| `tencent[8]` | 存在多个候选，需区分 | 363 / 31 | 6 家族 / 363 对 / 本源 15 日 | 601288 (0.076541) | sina[8] (robust_correlation,per_stock_time_series); eltdx.quote_snapshot.total_hand (robust_correlation,per_stock_time_series) |
| `zhb.full.pre_receive_zj` | 存在多个候选，需区分 | 244 / 31 | 6 家族 / 244 对 / 本源 0 日 | 600519 (30.729277) | tencent[76] (robust_correlation); tencent[73] (robust_correlation) |
| `sina[16]` | 存在多个候选，需区分 | 406 / 29 | 6 家族 / 406 对 / 本源 15 日 | 600519 (15.313449) | tencent[16] (robust_correlation,affine_formula,per_stock_time_series); tencent[68] (robust_correlation) |
| `zhb.full.rd_input_fee` | 存在多个候选，需区分 | 244 / 29 | 6 家族 / 244 对 / 本源 0 日 | 600519 (35.93039) | push2.f105 (robust_correlation,per_stock_time_series); ulist239.f52 (robust_correlation,affine_formula) |
| `push2ex.turnover_rate` | 存在多个候选，需区分 | 311 / 28 | 6 家族 / 311 对 / 本源 0 日 | no_shared_stock_holdout | kph.turnover_rate (robust_correlation,per_stock_time_series,semantic_label); kpl.turnover_real (robust_correlation,per_stock_time_series) |
| `tencent[28]` | 存在多个候选，需区分 | 363 / 26 | 6 家族 / 363 对 / 本源 15 日 | 601288 (4.086216) | sina[22] (robust_correlation); sina[20] (robust_correlation) |

_此表显示优先级最高的 50 / 共 229 个目标；完整清单见 JSON。_


### 舍入近似数值线索（仅研究，不算 L1/L1-U；0 组）

近似窗口只用于提示复核：需核对双方原始单位、展示精度和来源口径；不得把该命中率当作字段语义结论或注册表写回依据。完整明细在 JSON `candidate_triage.approximate_matches`。

_本轮没有达到近似筛查门槛的关系。_


### 补足全局截断的字段候选（113）

| 未知字段 | 候选字段 | 方法 | 样本 | 日期 | 来源 |
|:--|:--|:--|--:|:--|:--|
| `eltdx.limit_ladder.auction_prev_volume_ratio` | `tencent[69]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.beta_60d` | `tencent[76]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
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
| `eltdx.limit_ladder.seal_to_amount_ratio` | `tencent[50]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.seal_to_float_ratio` | `tencent[68]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.year_limit_up_days` | `tencent[79]` | robust_correlation | 12 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `em_fund_flow.f139` | `tencent[57]` | robust_correlation, per_stock_time_series | 95 | T:20261019, T:20261102, T:20261103, T:20261104, T:20261105 | em_fund_flow, tencent |
| `em_kline_f61.dktotal` | `tencent[4]` | per_stock_time_series | 100 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | em_kline_f61, tencent |
| `event_dc.AMPLITUDE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.CHANGE_RATE` | `ftshare_rest.change_rate_ytd` | semantic_label | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.CLOSE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.EACHBALLOT_SHARES` | `ftshare_rest.shares` | semantic_label | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.INDUSTRY_PE` | `ftshare_rest.ts_millis` | robust_correlation | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.INDUSTRY_PE_NEW` | `ftshare_rest.ts_millis` | robust_correlation | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.IPO_YIELD` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.ISSUE_NUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.ISSUE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LATELY_PRICE` | `ftshare_rest.close` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LD_AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LD_CLOSE_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LD_HIGH_CHANG` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LD_OPEN_PREMIUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.LIMIT_UP_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.MZYQ_PAY_FUND` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.OD_HIGH_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.OPEN_AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.OPEN_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.PROFIT` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TCHANGE_RATE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TNEW_PRICE` | `ftshare_rest.close` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TOTAL_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TOTAL_ISSUE_NUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TOTAL_SHARES` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.TURNOVERRATE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `event_dc.fetched_at` | `ftshare_rest.ts_millis` | robust_correlation, affine_formula | 24 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | event_dc, ftshare_rest |
| `fuyao.valuation.ps_ttm` | `ulist239.f23` | robust_correlation, per_stock_time_series | 100 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | fuyao, ulist239 |
| `kph.industry_limit_up_count` | `push2ex.limit_count` | semantic_label | 407 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028 | kph, push2ex |
| `kpl.amplitude` | `push2ex.limit_fund` | per_stock_time_series | 869 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.main_buy` | `push2ex.price` | per_stock_time_series | 869 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.main_sell` | `push2ex.price` | per_stock_time_series | 869 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.raw_columns.col_09` | `push2ex.price` | per_stock_time_series | 869 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.raw_columns.col_10` | `push2ex.price` | per_stock_time_series | 869 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.raw_columns.col_13` | `push2ex.price` | per_stock_time_series | 869 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.raw_columns.col_16` | `push2ex.limit_fund` | per_stock_time_series | 869 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `kpl.raw_columns.col_17` | `push2ex.limit_fund` | per_stock_time_series | 869 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `push2.f103` | `zhb.tipinfo.hg_amount_yi` | robust_correlation, affine_formula | 34 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104 | push2, zhb |
| `push2.f109` | `zhb.tipinfo.hg_amount_yi` | robust_correlation, affine_formula | 34 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104 | push2, zhb |
| `push2.f176` | `fuyao.valuation.pb_mrq` | robust_correlation, per_stock_time_series | 140 | T:20261020, T:20261023, T:20261029, T:20261102, T:20261103 | fuyao, push2 |
| `push2ex.broken_count` | `kpl.turnover_real` | per_stock_time_series | 869 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `push2ex.circulating_value` | `tencent[45]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | push2ex, tencent |
| `push2ex.first_limit_time` | `kph.limit_time` | semantic_label | 407 | T:20261016, T:20261019, T:20261021, T:20261023, T:20261028 | kph, push2ex |
| `push2ex.total_value` | `tencent[45]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | push2ex, tencent |
| `push2ex.turnover_rate` | `tencent[38]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | push2ex, tencent |
| `push2ex.zt_continuous` | `kpl.raw_columns.col_21` | per_stock_time_series | 869 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `push2ex.zt_days` | `kpl.raw_columns.col_21` | per_stock_time_series | 869 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023 | kpl, push2ex |
| `sina[14]` | `tencent[68]` | robust_correlation | 300 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[16]` | `tencent[68]` | robust_correlation | 300 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[18]` | `tencent[68]` | robust_correlation | 300 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[24]` | `tencent[67]` | robust_correlation | 300 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[26]` | `tencent[68]` | robust_correlation | 300 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `sina[28]` | `tencent[20]` | robust_correlation | 300 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `slist.n_boards` | `tencent[45]` | robust_correlation | 100 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | slist, tencent |
| `tdx.finance_info.fajirenfarengu` | `ulist239.f47` | robust_correlation, affine_formula | 98 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tdx, ulist239 |
| `tdx.finance_info.zhuyinglyrun` | `tencent[76]` | robust_correlation | 298 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | tdx, tencent |
| `tencent[22]` | `sina[20]` | robust_correlation | 300 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `tencent[24]` | `sina[22]` | robust_correlation | 300 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `tencent[26]` | `sina[22]` | robust_correlation | 300 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `tencent[28]` | `sina[22]` | robust_correlation | 300 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 | sina, tencent |
| `tencent[7]` | `ulist239.f5` | robust_correlation, per_stock_time_series | 100 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `tencent[86]` | `eltdx.shortline.prev2_seal_amount` | robust_correlation | 16 | T:20261016, T:20261019, T:20261020, T:20261023, T:20261026 | eltdx, tencent |
| `tencent[8]` | `ulist239.f5` | robust_correlation, per_stock_time_series | 100 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f111` | `zhb.tipinfo.hg_amount_yi` | robust_correlation | 24 | T:20261102, T:20261103, T:20261104, T:20261106 | ulist239, zhb |
| `ulist239.f127` | `zhb.stat.change_pct_2d` | robust_correlation, per_stock_time_series | 80 | T:20261102, T:20261103, T:20261104, T:20261106 | ulist239, zhb |
| `ulist239.f135` | `tencent[76]` | robust_correlation, affine_formula | 100 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f139` | `tencent[76]` | robust_correlation | 100 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f148` | `tencent[71]` | robust_correlation | 100 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f149` | `tencent[63]` | robust_correlation, per_stock_time_series | 100 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f190` | `tdx.finance_info.hgu` | robust_correlation, affine_formula | 98 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tdx, ulist239 |
| `ulist239.f192` | `tdx.finance_info.hgu` | robust_correlation, affine_formula | 98 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tdx, ulist239 |
| `ulist239.f297` | `tencent[30]` | robust_correlation, affine_formula | 40 | T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f45` | `tdx.finance_info.yingyelirun` | robust_correlation, affine_formula | 98 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tdx, ulist239 |
| `ulist239.f46` | `zhb.stat.board_count` | robust_correlation | 20 | T:20261102, T:20261103, T:20261104, T:20261106 | ulist239, zhb |
| `ulist239.f59` | `tencent[39]` | robust_correlation | 100 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | tencent, ulist239 |
| `ulist239.f63` | `eltdx.shortline.open_volume_ratio` | robust_correlation, per_stock_time_series | 100 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | eltdx, ulist239 |
| `ulist239.f98` | `zhb.stat2.high_52w` | per_stock_time_series | 80 | T:20261102, T:20261103, T:20261104, T:20261106 | ulist239, zhb |
| `ulist239.f99` | `eltdx.shortline.limit_up_count_in_stat_days` | robust_correlation | 19 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106 | eltdx, ulist239 |
| `zhb.full.cash_reserve_wan` | `push2.f85` | robust_correlation, affine_formula | 106 | T:20261020, T:20261023, T:20261102, T:20261103, T:20261104 | push2, zhb |

_仅显示前 100 / 共 113 条字段前沿候选。_


### 双输入公式候选（1）

公式使用按股票代码分组的留出样本验证；至少 3 个留出股票，验证 R²≥0.985、误差不超过训练目标标准差的 5%，并要求优于最佳单输入线性模型至少 0.05。这些阈值只筛选探索候选，不构成语义证明。

| 目标字段 | 候选公式 | 留出 R² | 相对误差尺度 | 验证样本/股票 |
|:--|:--|--:|--:|--:|
| `kpl.raw_columns.col_13` | `kpl.raw_columns.col_13 ≈ 104.81606 × (kph.turnover ÷ kph.turnover_rate) + 16988117` | 0.997351 | 0.015159 | 77/65 |

### 已知映射与已证伪关系的候选校准

- 已登记正向对照：当前窗口有 166 组独立数值关系可评估，166 组被方法候选识别；样本不足 0 组。此计数仅检查方法覆盖，不是准确率。
- 已证伪负向对照：数值关系 0 组，其中仍有方法信号 0 组；这些信号被隔离，不进入普通候选。

### 采集覆盖异常源

- axdata: 20261021, 20261026 ({'failed': 1, 'ok': 13, 'partial': 1})
- baidu: 20261104, 20261105, 20261106 ({'deprecated': 2, 'pending_validation': 12})
- clist: 20261028, 20261029, 20261030 ({'ok': 5, 'partial': 8})
- em_fund_flow: 20261028, 20261029, 20261030 ({'ok': 5, 'partial': 9})
- em_hot: 20261104, 20261105, 20261106 ({'context_only': 13})
- em_kline_f61: 20261028, 20261029, 20261030 ({'ok': 5, 'partial': 9})
- exchange: 20261104, 20261105, 20261106 ({'context_only': 13})
- ftshare: 20261104, 20261105, 20261106 ({'deprecated': 12, 'failed': 3})
- market_sources: 20261026 ({'ok': 14, 'partial': 1})
- news_wscn_cctv: 20261015 ({'ok': 14, 'partial': 1})
- push2: 20261028, 20261029, 20261030 ({'failed': 4, 'ok': 5, 'partial': 4})
- slist: 20261028, 20261029, 20261030 ({'failed': 8, 'ok': 5})
- sse_e_interaction: 20261016 ({'ok': 14, 'partial': 1})
- st_list: 20261028, 20261029, 20261030 ({'ok': 6, 'partial': 8})
- tdx: 20261104, 20261105 ({'ok': 13, 'partial': 2})
- ulist239: 20261028, 20261029, 20261030 ({'failed': 10, 'ok': 5})
- zhb: 20261103, 20261104, 20261105 ({'ok': 5, 'partial': 10})

## 候选身份与人工审阅状态

- 候选身份：生成 3670 条，唯一候选 3670 个，重复身份 0，无效身份 0。
- 审阅台账：可用；当前状态 `pending`；已审 7，待处理 3663，覆盖率 0.2%。
- 重复归并组：0；每个成员均保留到代表候选的反向追溯。
- 处置计数：`accepted_for_adjudication` 0；`duplicate_grouped` 0；`insufficient_evidence` 0；`needs_external_evidence` 1；`rejected` 6；`unreviewed` 3663。
- `accepted_for_adjudication` 只表示可进入现有证据裁决流程；审阅台账不会修改主字典或字段注册表。

## 报告完整性与审阅范围

- 机器可读完整性：`complete`；方法候选生成 3623 条，完整明细保存 3623 条，缺失 0 条，多余 0 条，重复 0 条，身份无效 0 条。
- 全量方法候选位于同名 JSON 的 `method_candidate_inventory`；Markdown 的 Top-N 表格是导航摘要，不能代替全量 JSON 审阅。
- 候选审阅数据对账：`complete`；唯一候选 3670 个，审阅 7 个，待处理 3663 个；人工审阅进度与机器清单完整性分别统计。
- Markdown 未逐行展示、但 JSON 保留的部分：
  - `method_candidates`：展示 100 / 500，摘要省略 400 条。
  - `method_candidate_inventory`：展示 0 / 3623，摘要省略 3623 条。
  - `method_candidate_frontier`：展示 100 / 113，摘要省略 13 条。
  - `candidate_triage.targets`：展示 50 / 229，摘要省略 179 条。
  - `diagnostics`：展示 100 / 284，摘要省略 184 条。
  - `candidate_review.human_review.reviewed_candidates`：展示 0 / 7，摘要省略 7 条。
- 完整性对账通过；逐目标复核仍须覆盖 JSON 的全部明细，并为每项记录已检查、重复归并、证据不足或需外部核验的处置。
