# 全源对撞报告（20261019）

> 交易数据窗口配置：近 7 个交易日（`--window`）
> 行情窗口：20261009 ~ 20261019（7 个不同交易日）｜字段 968 个｜样本值 291024 条
> 新闻/公告自然日窗口：20261013 ~ 20261019
> 主攻目标（unverified）=372｜可审定新候选=1｜首次发现新候选对=1｜已登记关系复验=2｜异号同义 1 / 同号镜像 0

> **规则**：L1 每日需≥18 组有效配对，并至少有5 组信息配对；双方同时为 0 或同时缺失不计命中率，一侧为 0、另一侧非 0 按失配计。信息配对命中率≥90%，且覆盖至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。JSON `daily_sample_counts` 与 `daily_informative_sample_counts`分别保留每日有效配对数和 L1 信息配对数。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 新候选 — 异号同义（跨编号，高价值）(1)

| 左字段(unverified) | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|
| `push2ex.limit_fund` | `kpl.seal_amount` | L1 | 100.00% | 3 | 128 | 128 | - |  | — |

## 二、L1 / L1-U 新候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、已登记映射的本窗口复验（2）

_这些关系已在主注册表登记，只用于观察当前样本是否仍支持既有映射；它们不是新的未知字段候选，也不能再次提交为新定案。_

| 左字段 | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|
| `zhb.full.change_pct` | `tencent[32]` | L1 | 97.98% | 5 | 100 | 99 | - |  | ✅ |
| `zhb.full.high_52w` | `tencent[67]` | L1 | 95.00% | 5 | 100 | 100 | - |  | ✅ |

## 四、L4 存疑候选（100）

| 左字段 | 右字段 | 命中率 | 天数 | 样本 |
|:--|:--|--:|--:|--:|
| `kpl.raw_columns.col_04` | `kph.limit_time` | 100.00% | 1 | 50 |
| `kpl.raw_columns.col_06` | `kph.seal_amount` | 100.00% | 1 | 50 |
| `kpl.raw_columns.col_07` | `kph.seal_money` | 100.00% | 1 | 50 |
| `kpl.raw_columns.col_08` | `kph.net_inflow` | 100.00% | 1 | 50 |
| `kpl.raw_columns.col_11` | `kph.turnover` | 100.00% | 1 | 50 |
| `kpl.raw_columns.col_11` | `push2ex.amount` | 100.00% | 2 | 107 |
| `kpl.raw_columns.col_14` | `kph.turnover_rate` | 100.00% | 1 | 50 |
| `push2.f57` | `tencent[2]` | 100.00% | 1 | 12 |
| `push2.f58` | `tencent[1]` | 100.00% | 1 | 12 |
| `push2.f60` | `eltdx.quote_snapshot.pre_close_price` | 100.00% | 1 | 12 |
| `push2.f60` | `eltdx.shortline.pre_close` | 100.00% | 1 | 12 |
| `push2.f60` | `sina[2]` | 100.00% | 1 | 12 |
| `push2.f60` | `tdx.quote_full.last_close` | 100.00% | 1 | 12 |
| `push2.f60` | `tencent[4]` | 100.00% | 1 | 12 |
| `push2.f71` | `tencent[51]` | 100.00% | 1 | 12 |
| `push2.f119` | `tencent[63]` | 100.00% | 1 | 12 |
| `push2.f119` | `zhb.full.change_5d` | 100.00% | 1 | 12 |
| `push2.f119` | `zhb.stat.change_5d` | 100.00% | 1 | 12 |
| `push2.f120` | `tencent[70]` | 100.00% | 1 | 12 |
| `push2.f120` | `zhb.full.change_20d` | 100.00% | 1 | 12 |
| `push2.f120` | `zhb.stat.change_20d` | 100.00% | 1 | 12 |
| `push2.f162` | `tencent[52]` | 100.00% | 1 | 12 |
| `push2.f163` | `tencent[53]` | 100.00% | 1 | 12 |
| `push2.f175` | `tencent[68]` | 100.00% | 1 | 12 |
| `push2.f175` | `zhb.full.low_52w` | 100.00% | 1 | 12 |
| `push2.f175` | `zhb.stat2.low_52w` | 100.00% | 1 | 12 |
| `push2ex.limit_fund` | `kph.seal_amount` | 100.00% | 1 | 50 |
| `sina[11]` | `tdx.quote_full.bid1` | 100.00% | 5 | 100 |
| `sina[11]` | `tencent[9]` | 100.00% | 7 | 140 |
| `tdx.quote_raw.price` | `fuyao.snapshot.last_price` | 100.00% | 2 | 40 |
| `tdx.quote_raw.price` | `sina[3]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.price` | `tencent[3]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.last_close` | `fuyao.snapshot.prev_price` | 100.00% | 2 | 40 |
| `tdx.quote_raw.last_close` | `sina[2]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.last_close` | `tencent[4]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.open` | `fuyao.snapshot.open_price` | 100.00% | 2 | 40 |
| `tdx.quote_raw.open` | `sina[1]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.open` | `tencent[5]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.high` | `fuyao.snapshot.high_price` | 100.00% | 2 | 40 |
| `tdx.quote_raw.high` | `sina[4]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.high` | `tencent[33]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.high` | `tencent[41]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.low` | `fuyao.snapshot.low_price` | 100.00% | 2 | 40 |
| `tdx.quote_raw.low` | `sina[5]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.low` | `tencent[34]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.low` | `tencent[42]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.amount` | `fuyao.snapshot.turnover` | 100.00% | 2 | 40 |
| `tdx.quote_raw.amount` | `sina[9]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.bid1` | `sina[6]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.bid1` | `tencent[9]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.ask1` | `sina[7]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.ask1` | `sina[21]` | 100.00% | 2 | 40 |
| `tdx.quote_raw.ask1` | `tencent[19]` | 100.00% | 2 | 40 |
| `zhb.full.change_pct` | `push2.f170` | 100.00% | 1 | 12 |
| `sina[32]` | `tdx.finance_info.hgu` | 93.33% | 6 | 120 |
| `push2.f58` | `sina[0]` | 91.67% | 1 | 12 |
| `push2.f164` | `tencent[39]` | 91.67% | 1 | 12 |
| `push2.f164` | `zhb.full.pe_ttm` | 91.67% | 1 | 12 |
| `push2.f164` | `zhb.stat.pe_ttm` | 91.67% | 1 | 12 |
| `push2.f167` | `tencent[46]` | 91.67% | 1 | 12 |

_（仅显示前 60 / 共 100）_

## 五、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 六、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `fuyao.valuation.pe_ttm` | `eltdx.shortline.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 77 | T:20261009, T:20261014, T:20261016, T:20261019 | eltdx, fuyao | Pearson=0.9998, Spearman=0.9994, LOO稳号=True |
| `fuyao.valuation.pe_ttm` | `zhb.stat.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 60 | T:20261009, T:20261014, T:20261016 | fuyao, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `fuyao.valuation.pe_ttm` | `zhb.full.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 60 | T:20261009, T:20261014, T:20261016 | fuyao, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `tencent[27]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9383, LOO稳号=True |
| `tencent[27]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9452, LOO稳号=True |
| `tencent[27]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9466, LOO稳号=True |
| `tencent[27]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9168, LOO稳号=True |
| `tencent[27]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9284, LOO稳号=True |
| `tencent[27]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `tencent[27]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9438, LOO稳号=True |
| `tencent[25]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `tencent[25]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9383, LOO稳号=True |
| `tencent[25]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9451, LOO稳号=True |
| `tencent[25]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9466, LOO稳号=True |
| `tencent[25]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9168, LOO稳号=True |
| `tencent[25]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9284, LOO稳号=True |
| `tencent[25]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `tencent[25]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9438, LOO稳号=True |
| `tencent[23]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `tencent[23]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9383, LOO稳号=True |
| `tencent[23]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9451, LOO稳号=True |
| `tencent[23]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9467, LOO稳号=True |
| `tencent[23]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9168, LOO稳号=True |
| `tencent[23]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9284, LOO稳号=True |
| `tencent[23]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `tencent[23]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9438, LOO稳号=True |
| `tencent[22]` | `sina[22]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[21]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `tencent[21]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9383, LOO稳号=True |
| `tencent[21]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.945, LOO稳号=True |
| `tencent[21]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9467, LOO稳号=True |
| `tencent[21]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9168, LOO稳号=True |
| `tencent[21]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9284, LOO稳号=True |
| `tencent[21]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `tencent[21]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9438, LOO稳号=True |
| `tencent[20]` | `sina[20]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[17]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9423, LOO稳号=True |
| `tencent[17]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[17]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9907, LOO稳号=True |
| `tencent[17]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9929, LOO稳号=True |
| `tencent[17]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9682, LOO稳号=True |
| `tencent[17]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9618, LOO稳号=True |
| `tencent[17]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9423, LOO稳号=True |
| `tencent[17]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9909, LOO稳号=True |
| `tencent[15]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9423, LOO稳号=True |
| `tencent[15]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[15]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9907, LOO稳号=True |
| `tencent[15]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9929, LOO稳号=True |
| `tencent[15]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9683, LOO稳号=True |
| `tencent[15]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9617, LOO稳号=True |
| `tencent[15]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9423, LOO稳号=True |
| `tencent[15]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9909, LOO稳号=True |
| `tencent[13]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9423, LOO稳号=True |
| `tencent[13]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[13]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9907, LOO稳号=True |
| `tencent[13]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9929, LOO稳号=True |
| `tencent[13]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9683, LOO稳号=True |
| `tencent[13]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9618, LOO稳号=True |
| `tencent[13]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9423, LOO稳号=True |
| `tencent[13]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9909, LOO稳号=True |
| `tencent[12]` | `sina[12]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[11]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9423, LOO稳号=True |
| `tencent[11]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[11]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9907, LOO稳号=True |
| `tencent[11]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9929, LOO稳号=True |
| `tencent[11]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9683, LOO稳号=True |
| `tencent[11]` | `sina[2]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9618, LOO稳号=True |
| `tencent[11]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9423, LOO稳号=True |
| `tencent[11]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9909, LOO稳号=True |
| `tencent[10]` | `sina[10]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[29]` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9383, LOO稳号=True |
| `sina[29]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9998, Spearman=0.7437, LOO稳号=True |
| `sina[29]` | `tencent[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9438, LOO稳号=True |
| `sina[29]` | `tencent[51]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9434, LOO稳号=True |
| `sina[29]` | `tencent[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9284, LOO稳号=True |
| `sina[29]` | `tencent[48]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9998, Spearman=0.9024, LOO稳号=True |
| `sina[29]` | `tencent[47]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.932, LOO稳号=True |
| `sina[29]` | `tencent[42]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9452, LOO稳号=True |
| `sina[29]` | `tencent[41]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9466, LOO稳号=True |
| `sina[29]` | `tencent[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9168, LOO稳号=True |
| `sina[29]` | `tencent[34]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9452, LOO稳号=True |
| `sina[29]` | `tencent[33]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9466, LOO稳号=True |
| `sina[29]` | `tencent[19]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `sina[27]` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9383, LOO稳号=True |
| `sina[27]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9998, Spearman=0.7437, LOO稳号=True |
| `sina[27]` | `tencent[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9438, LOO稳号=True |
| `sina[27]` | `tencent[51]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9434, LOO稳号=True |
| `sina[27]` | `tencent[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9284, LOO稳号=True |
| `sina[27]` | `tencent[48]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9998, Spearman=0.9023, LOO稳号=True |
| `sina[27]` | `tencent[47]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.932, LOO稳号=True |
| `sina[27]` | `tencent[42]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9451, LOO稳号=True |
| `sina[27]` | `tencent[41]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9466, LOO稳号=True |
| `sina[27]` | `tencent[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9168, LOO稳号=True |
| `sina[27]` | `tencent[34]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9451, LOO稳号=True |
| `sina[27]` | `tencent[33]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9466, LOO稳号=True |
| `sina[27]` | `tencent[19]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=1.0, Spearman=0.9953, LOO稳号=True |
| `sina[25]` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9383, LOO稳号=True |
| `sina[25]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9998, Spearman=0.7441, LOO稳号=True |
| `sina[25]` | `tencent[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016 | sina, tencent | Pearson=0.9999, Spearman=0.9438, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 七、日期与数据质量告警（135）

- 20260920: 旧式非交易日目录按前一交易日 20260918 归并；目录未改名
- 20261005: 旧式非交易日目录按前一交易日 20260930 归并；目录未改名
- 20261011: 旧式非交易日目录按前一交易日 20261009 归并；目录未改名
- 20261017: 旧式非交易日目录按前一交易日 20261016 归并；目录未改名
- 20261018: 旧式非交易日目录按前一交易日 20261016 归并；目录未改名
- 20260814: 行情数据日 20260814 属于配置的异常日，行情快照排除
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
- 另有 35 条告警，详见同名 JSON 报告。

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

窗口内有 7 个唯一数据日的轮验记录；重复目录合并 0 条。
静态接口队列：257 个接口，3343 个字段出现项，低于 E3 的字段出现项 3343；当前主动探针白名单 `tencent_realtime_snapshot`。
静态候选策略：static review only until route, parameters, date basis, and request safety are approved。

| 数据日 | 轮验状态 | 探针状态 / 请求数 | 来源身份状态 | 短线配对 | KPH/KPL 配对 | 证据文件 |
|:--|:--|:--|:--|--:|--:|:--|
| 20261009 | not_eligible | not_run / 0 (字段相同/不同 0/0) | 未记录 | — | — | meta_summary |
| 20261012 | not_eligible | not_run / 0 (字段相同/不同 0/0) | 未记录 | — | — | meta_summary |
| 20261013 | not_eligible | not_run / 0 (字段相同/不同 0/0) | 未记录 | — | — | meta_summary |
| 20261014 | sampled | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 0 | — | full |
| 20261015 | probe_skipped | skipped_project_counterpart_failed / 0 (字段相同/不同 0/0) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 0 | — | full |
| 20261016 | already_recorded | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | — | 50 | full |
| 20261019 | sampled | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |

被动逐字段比较中的差异计数（跨本窗口唯一数据日累加，不含原始值）：

| 比较路径 | 相同 | 不同 | 缺失/双方空值 |
|:--|--:|--:|--:|
| `kph_limit_up_history_vs_kpl_detail:seal_amount` | 0 | 50 | 0 |
| `kph_limit_up_history_vs_kpl_detail:seal_money` | 0 | 50 | 0 |
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
| `axdata_shortline_vs_eltdx:open_amount` | 7 | 13 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_hand` | 7 | 13 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_ratio` | 7 | 13 | 0 |
| `axdata_shortline_vs_eltdx:auction_prev_volume_ratio` | 7 | 12 | 1 |
| `axdata_shortline_vs_eltdx:open_prev_amount_ratio` | 8 | 12 | 0 |
| `axdata_shortline_vs_eltdx:open_turnover_z` | 13 | 7 | 0 |

### FTShare 每日身份核验记录

窗口内保留 6 个唯一数据日的采集时记录；重复目录合并 0 条。

| 数据日 | 核验状态 | 接口状态计数 |
|:--|:--|:--|
| 20261012 | ok | pending: 6 |
| 20261013 | ok | pending: 6 |
| 20261014 | ok | pending: 6 |
| 20261015 | ok | pending: 6 |
| 20261016 | ok | pending: 6 |
| 20261019 | ok | pending: 6 |

## 字母字段名语义提示（仅候选）

窗口内观察到 125 条需审阅的字母字段路径：含词义线索 43 条，仅拆词 82 条。
完整逐条记录保存在碰撞 JSON；名称线索清单：`docs/field_verification/20261014/20261014_alphabetic_field_name_inventory.csv`。
> 拼音、英文、缩写和混合拆词只用于检索候选；必须结合原始值、接口定义和独立来源复核，不得据此定案或改写主字典。

| 逐源字段路径 | 状态/审阅范围 | 名称形式与拆词 | 词义线索（非释义） | 样本日期 |
|:--|:--|:--|:--|:--|
| `市场源(market_sources)::change_type` | unverified / unverified_semantics | snake_case_or_mixed: change type | 变化/涨跌 + 类型 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `市场源(market_sources)::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `市场源(market_sources)::limit_count` | verified / verified_metadata_gap | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `市场源(market_sources)::limit_time` | unverified / unverified_semantics | snake_case_or_mixed: limit time | 涨跌停限制 + 时间 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `市场源(market_sources)::plate_limit_up_count` | verified / verified_metadata_gap | snake_case_or_mixed: plate limit up count | 涨跌停限制 + 上/涨 + 数量/次数 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `东财-push2ex::change_pct` | unverified / unverified_semantics | recognized_english_word_candidate: change pct | 变化/涨跌 + 百分比 | T:20261014, T:20261016, T:20261019 |
| `东财-push2ex::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261014, T:20261016, T:20261019 |
| `东财-push2ex::first_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: first limit time | 首次/第一 + 涨跌停限制 + 时间 | T:20261014, T:20261016, T:20261019 |
| `东财-push2ex::last_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: last limit time | 最近/上一期 + 涨跌停限制 + 时间 | T:20261014, T:20261016, T:20261019 |
| `东财-push2ex::limit_count` | unverified / unverified_semantics | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261014, T:20261016, T:20261019 |
| `东财-push2ex::name` | unverified / unverified_semantics | recognized_english_word_candidate: name | 名称 | T:20261014, T:20261016, T:20261019 |
| `东财-push2ex::price` | unverified / unverified_semantics | recognized_english_word_candidate: price | 价格 | T:20261014, T:20261016, T:20261019 |
| `东财-push2ex::total_value` | unverified / unverified_semantics | snake_case_or_mixed: total value | 总 + 值 | T:20261014, T:20261016, T:20261019 |
| `开盘红(Levistock适配)::limit_count` | unverified / unverified_semantics | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261009, T:20261013, T:20261016 |
| `开盘红(Levistock适配)::open_time` | unverified / unverified_semantics | snake_case_or_mixed: open time | 开盘 + 时间 | T:20261009, T:20261013, T:20261016 |
| `财联社(cls)::time` | unverified / unverified_semantics | recognized_english_word_candidate: time | 时间 | C:20261014, C:20261016, C:20261019 |
| `TDX(双命名源)::changqifuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: changqifuzhai | 长期负债 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::cunhuo` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: cunhuo | 存货 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::eps` | unverified / unverified_semantics | recognized_english_word_candidate: eps | 每股收益 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::fajirenfarengu` | unverified / unverified_semantics | recognized_pinyin_phrase_candidate: fajirenfarengu | 疑似 faqirenfarengu 的拼写变体；含义未证实 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::gudongrenshu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: gudongrenshu | 股东人数 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::ipodate` | unverified / unverified_semantics | recognized_english_phrase_candidate: ipodate | IPO/上市日期（字段语境候选） | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::jinglirun` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jinglirun | 净利润 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::jingyingxianjinliu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingyingxianjinliu | 经营现金流 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::jingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingzichan | 净资产 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::liudongfuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: liudongfuzhai | 流动负债 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::meigujingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: meigujingzichan | 每股净资产 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::yingshouzhangkuan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: yingshouzhangkuan | 应收账款 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::zhongguben` | unverified / unverified_semantics | recognized_pinyin_phrase_candidate: zhongguben | 疑似 zongguben 的拼写差异；含义未证实 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::zhuyingshouru` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zhuyingshouru | 主营收入 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::zibengongjijin` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zibengongjijin | 资本公积金 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::zongzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongzichan | 总资产 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `ZHB-tdxstat::change_pct` | unverified / unverified_semantics | recognized_english_word_candidate: change pct | 变化/涨跌 + 百分比 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::change_pct_1d` | unverified / unverified_semantics | snake_case_or_mixed: change pct 1 d | 变化/涨跌 + 百分比 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::change_pct_2d` | unverified / unverified_semantics | snake_case_or_mixed: change pct 2 d | 变化/涨跌 + 百分比 | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::main_net_buy_amount_1d` | unverified / unverified_semantics | snake_case_or_mixed: main net buy amount 1 d | 净 + 金额/成交额（需看接口） | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::main_net_buy_amount` | unverified / unverified_semantics | snake_case_or_mixed: main net buy amount | 净 + 金额/成交额（需看接口） | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `同花顺-fuyao::valuation.pb_mrq` | conflict / unverified_semantics | snake_case_or_mixed: valuation pb mrq | 市净率 + 最近报告期 | T:20261009, T:20261014, T:20261016, T:20261019 |
| `同花顺-fuyao::valuation.pe_mrq` | conflict / unverified_semantics | snake_case_or_mixed: valuation pe mrq | 市盈率 + 最近报告期 | T:20261009, T:20261014, T:20261016, T:20261019 |
| `同花顺-fuyao::valuation.pe_ttm` | conflict / unverified_semantics | snake_case_or_mixed: valuation pe ttm | 市盈率 + 滚动十二个月 | T:20261009, T:20261014, T:20261016, T:20261019 |
| `同花顺-fuyao::snapshot.open_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot open price | 开盘 + 价格 | T:20261009, T:20261014, T:20261016, T:20261019 |
| `新浪(扩展API)::turnover` | conflict / unverified_semantics | recognized_english_word_candidate: turnover | 换手/成交额（需看接口） | T:20261019 |
| `TDX-eltdx(适配层)::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `市场源(market_sources)::one_word` | unverified / unverified_semantics | snake_case_or_mixed: one word | — | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `市场源(market_sources)::plate_amount` | verified / verified_metadata_gap | snake_case_or_mixed: plate amount | — | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `市场源(market_sources)::plate_code` | verified / verified_metadata_gap | snake_case_or_mixed: plate code | — | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `市场源(market_sources)::plate_name` | verified / verified_metadata_gap | snake_case_or_mixed: plate name | — | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `市场源(market_sources)::popular` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: popular | — | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `开盘啦(kpl_limit_up_detail)::max_seal` | verified / verified_metadata_gap | snake_case_or_mixed: max seal | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261015, T:20261016, T:20261019 |
| `东财-push2ex::broken_count` | unverified / unverified_semantics | snake_case_or_mixed: broken count | — | T:20261014, T:20261016, T:20261019 |
| `东财-push2ex::circulating_value` | unverified / unverified_semantics | snake_case_or_mixed: circulating value | — | T:20261014, T:20261016, T:20261019 |
| `东财-push2ex::limit_fund` | unverified / unverified_semantics | snake_case_or_mixed: limit fund | — | T:20261014, T:20261016, T:20261019 |
| `东财-push2ex::sector` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: sector | — | T:20261014, T:20261016, T:20261019 |
| `东财-push2ex::turnover_rate` | unverified / unverified_semantics | snake_case_or_mixed: turnover rate | — | T:20261014, T:20261016, T:20261019 |
| `东财-push2ex::zt_continuous` | unverified / unverified_semantics | snake_case_or_mixed: zt continuous | — | T:20261014, T:20261016, T:20261019 |
| `东财-push2ex::zt_days` | unverified / unverified_semantics | snake_case_or_mixed: zt days | — | T:20261014, T:20261016, T:20261019 |
| `财联社(cls)::content` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: content | — | C:20261014, C:20261016, C:20261019 |
| `财联社(cls)::level` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: level | — | C:20261014, C:20261016, C:20261019 |
| `财联社(cls)::reading_num` | unverified / unverified_semantics | snake_case_or_mixed: reading num | — | C:20261014, C:20261016, C:20261019 |
| `财联社(cls)::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20261014, C:20261016, C:20261019 |
| `TDX(双命名源)::baoliu2` | unverified / unverified_semantics | mixed_alphanumeric: baoliu 2 | — | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::ipo_date` | verified / verified_metadata_gap | snake_case_or_mixed: ipo date | — | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::updated_date` | verified / verified_metadata_gap | snake_case_or_mixed: updated date | — | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::updateddate` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: updateddate | — | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::zhuyinglyrun` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: zhuyinglyrun | — | T:20261009, T:20261012, T:20261014, T:20261015, T:20261016, T:20261019 |
| `TDX(双命名源)::b_vol` | unverified / unverified_semantics | snake_case_or_mixed: b vol | — | T:20261009, T:20261012, T:20261014, T:20261016, T:20261019 |
| `TDX(双命名源)::s_vol` | unverified / unverified_semantics | snake_case_or_mixed: s vol | — | T:20261009, T:20261012, T:20261014, T:20261016, T:20261019 |
| `ZHB-tdxstat::change_10k_bar` | unverified / unverified_semantics | snake_case_or_mixed: change 10 k bar | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::change_5k_bar` | unverified / unverified_semantics | snake_case_or_mixed: change 5 k bar | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::change_ytd` | unverified / unverified_semantics | snake_case_or_mixed: change ytd | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::dividend_yield` | unverified / unverified_semantics | snake_case_or_mixed: dividend yield | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::employee_count` | unverified / unverified_semantics | snake_case_or_mixed: employee count | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::pe_lyr` | unverified / unverified_semantics | snake_case_or_mixed: pe lyr | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::stat.unknown_2` | candidate / unverified_semantics | snake_case_or_mixed: stat unknown 2 | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::stat.unknown_26` | conflict / unverified_semantics | snake_case_or_mixed: stat unknown 26 | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::streak_days` | unverified / unverified_semantics | snake_case_or_mixed: streak days | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat::unseal_date` | unverified / unverified_semantics | snake_case_or_mixed: unseal date | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::amount_1d` | unverified / unverified_semantics | snake_case_or_mixed: amount 1 d | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::amount_2d` | unverified / unverified_semantics | snake_case_or_mixed: amount 2 d | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::change_250k_bar` | unverified / unverified_semantics | snake_case_or_mixed: change 250 k bar | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::change_30k_bar` | unverified / unverified_semantics | snake_case_or_mixed: change 30 k bar | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::change_30k_bar_ref` | unverified / unverified_semantics | snake_case_or_mixed: change 30 k bar ref | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::change_mtd` | unverified / unverified_semantics | snake_case_or_mixed: change mtd | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::high_52w` | unverified / unverified_semantics | snake_case_or_mixed: high 52 w | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::industry_code` | unverified / unverified_semantics | snake_case_or_mixed: industry code | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::ipo_price` | unverified / unverified_semantics | snake_case_or_mixed: ipo price | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::main_net_buy_hands_1d` | unverified / unverified_semantics | snake_case_or_mixed: main net buy hands 1 d | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `ZHB-tdxstat2::main_net_buy_hands` | unverified / unverified_semantics | snake_case_or_mixed: main net buy hands | — | T:20261009, T:20261012, T:20261013, T:20261014, T:20261016 |
| `同花顺-fuyao::fin_report` | unverified / unverified_semantics | snake_case_or_mixed: fin report | — | T:20261009, T:20261014, T:20261016, T:20261019 |
| `同花顺-fuyao::snapshot.prev_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot prev price | — | T:20261009, T:20261014, T:20261016, T:20261019 |
| `同花顺-fuyao::valuation.ps_ttm` | conflict / unverified_semantics | snake_case_or_mixed: valuation ps ttm | — | T:20261009, T:20261014, T:20261016, T:20261019 |
| `开盘红(Levistock适配)::industry_id` | unverified / unverified_semantics | snake_case_or_mixed: industry id | — | T:20261016 |
| `开盘红(Levistock适配)::limit_tag` | unverified / unverified_semantics | snake_case_or_mixed: limit tag | — | T:20261016 |
| `开盘红(Levistock适配)::reason` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: reason | — | T:20261016 |
| `开盘红(Levistock适配)::themes` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: themes | — | T:20261016 |
| `市场源(market_sources)::big_order_300w_net` | unverified / unverified_semantics | runtime_tokenization_only: big order 300 w net | — | T:20261016, T:20261019 |
| `市场源(market_sources)::institution_add` | unverified / unverified_semantics | runtime_tokenization_only: institution add | — | T:20261016, T:20261019 |
| `市场源(market_sources)::main_inflow` | unverified / unverified_semantics | snake_case_or_mixed: main inflow | — | T:20261016, T:20261019 |
| `市场源(market_sources)::pe_next` | unverified / unverified_semantics | runtime_tokenization_only: pe next | — | T:20261016, T:20261019 |
| `市场源(market_sources)::pe_now` | unverified / unverified_semantics | runtime_tokenization_only: pe now | — | T:20261016, T:20261019 |

Markdown 显示前 100 条；其余 25 条完整保留在 JSON。

## 探索候选持续跟踪

研究台账：`collision_research_state.json.gz`；累计历史跟踪候选对 1663，本报告候选对 594，历史复现 573，新发现 0。
台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，不会自动改变字段状态、碰撞锚或主字典。新报告只将 `actionable_L1`、L4 和主动方法候选写入待研究队列；已登记关系的复验单独展示，历史跟踪记录不会被删除。
