# 全源对撞报告（20261021）

> 交易数据窗口配置：近 7 个交易日（`--window`）
> 行情窗口：20261013 ~ 20261021（7 个不同交易日）｜字段 985 个｜样本值 340978 条
> 新闻/公告自然日窗口：20261015 ~ 20261021
> 主攻目标（unverified）=350｜可审定新候选=4｜首次发现新候选对=4｜已登记关系复验=2｜异号同义 4 / 同号镜像 0

> **规则**：L1 每日需≥18 组有效配对，并至少有5 组信息配对；双方同时为 0 或同时缺失不计命中率，一侧为 0、另一侧非 0 按失配计。信息配对命中率≥90%，且覆盖至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。JSON `daily_sample_counts` 与 `daily_informative_sample_counts`分别保留每日有效配对数和 L1 信息配对数。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 新候选 — 异号同义（跨编号，高价值）(4)

| 左字段(unverified) | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|
| `kpl.raw_columns.col_04` | `kph.limit_time` | L1 | 100.00% | 3 | 135 | 135 | - |  | — |
| `kpl.raw_columns.col_07` | `kph.seal_money` | L1 | 100.00% | 3 | 135 | 135 | - |  | — |
| `kpl.raw_columns.col_08` | `kph.net_inflow` | L1 | 100.00% | 3 | 135 | 133 | - |  | — |
| `kpl.raw_columns.col_14` | `kph.turnover_rate` | L1 | 100.00% | 3 | 135 | 135 | - |  | — |

## 二、L1 / L1-U 新候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、已登记映射的本窗口复验（2）

_这些关系已在主注册表登记，只用于观察当前样本是否仍支持既有映射；它们不是新的未知字段候选，也不能再次提交为新定案。_

| 左字段 | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|
| `zhb.full.change_pct` | `tencent[32]` | L1 | 97.96% | 5 | 100 | 98 | - |  | ✅ |
| `zhb.full.high_52w` | `tencent[67]` | L1 | 95.00% | 5 | 100 | 100 | - |  | ✅ |

## 四、L4 存疑候选（97）

| 左字段 | 右字段 | 命中率 | 天数 | 样本 |
|:--|:--|--:|--:|--:|
| `axdata.data.instrument_id` | `ftshare_rest.symbol` | 100.00% | 1 | 20 |
| `axdata.data.open_price` | `ftshare_rest.open` | 100.00% | 1 | 20 |
| `axdata.data.pre_close` | `ftshare_rest.prev_close` | 100.00% | 1 | 20 |
| `axdata.data.float_shares` | `ftshare_rest.float_a_shares` | 100.00% | 1 | 20 |
| `push2.f57` | `tencent[2]` | 100.00% | 1 | 12 |
| `push2.f58` | `tencent[1]` | 100.00% | 1 | 12 |
| `push2.f60` | `eltdx.quote_snapshot.pre_close_price` | 100.00% | 1 | 12 |
| `push2.f60` | `eltdx.shortline.pre_close` | 100.00% | 1 | 12 |
| `push2.f60` | `ftshare_rest.prev_close` | 100.00% | 1 | 12 |
| `push2.f60` | `fuyao.snapshot.prev_price` | 100.00% | 1 | 12 |
| `push2.f60` | `sina[2]` | 100.00% | 1 | 12 |
| `push2.f60` | `tdx.quote_full.last_close` | 100.00% | 1 | 12 |
| `push2.f60` | `tdx.quote_raw.last_close` | 100.00% | 1 | 12 |
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
| `push2.f164` | `tencent[39]` | 100.00% | 1 | 12 |
| `push2.f164` | `zhb.full.pe_ttm` | 100.00% | 1 | 12 |
| `push2.f164` | `zhb.stat.pe_ttm` | 100.00% | 1 | 12 |
| `sina[11]` | `tdx.quote_full.bid1` | 100.00% | 5 | 100 |
| `sina[11]` | `tencent[9]` | 100.00% | 7 | 140 |
| `tdx.quote_raw.price` | `ftshare_rest.close` | 100.00% | 2 | 40 |
| `tdx.quote_raw.price` | `fuyao.snapshot.last_price` | 100.00% | 4 | 80 |
| `tdx.quote_raw.price` | `push2.f43` | 100.00% | 1 | 12 |
| `tdx.quote_raw.price` | `push2.f179` | 100.00% | 1 | 12 |
| `tdx.quote_raw.price` | `sina[3]` | 100.00% | 4 | 80 |
| `tdx.quote_raw.price` | `tencent[3]` | 100.00% | 4 | 80 |
| `tdx.quote_raw.bid1` | `sina[6]` | 100.00% | 4 | 80 |
| `tdx.quote_raw.bid1` | `tencent[9]` | 100.00% | 4 | 80 |
| `tdx.quote_raw.ask1` | `sina[7]` | 100.00% | 4 | 80 |
| `tdx.quote_raw.ask1` | `sina[21]` | 100.00% | 4 | 80 |
| `tdx.quote_raw.ask1` | `tencent[19]` | 100.00% | 4 | 80 |
| `zhb.full.change_pct` | `push2.f170` | 100.00% | 1 | 12 |
| `sina[32]` | `tdx.finance_info.hgu` | 93.33% | 6 | 120 |
| `push2.f58` | `sina[0]` | 91.67% | 1 | 12 |
| `push2.f175` | `tencent[68]` | 91.67% | 1 | 12 |
| `push2.f175` | `zhb.full.low_52w` | 91.67% | 1 | 12 |
| `push2.f175` | `zhb.stat2.low_52w` | 91.67% | 1 | 12 |
| `zhb.full.change_ytd` | `push2.f122` | 91.67% | 1 | 12 |
| `sina[32]` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 89.17% | 6 | 120 |
| `sina[32]` | `tdx.finance_info.bgu` | 88.33% | 6 | 120 |
| `sina[32]` | `zhb.stat.other_qy_jzc` | 88.00% | 5 | 100 |
| `push2.f167` | `tencent[46]` | 83.33% | 1 | 12 |
| `push2.f174` | `tencent[67]` | 83.33% | 1 | 12 |
| `push2.f174` | `zhb.stat2.high_52w` | 83.33% | 1 | 12 |
| `push2.f192` | `tencent[50]` | 83.33% | 1 | 12 |
| `sina_extended.trade` | `push2.f43` | 83.33% | 1 | 12 |
| `sina_extended.trade` | `push2.f179` | 83.33% | 1 | 12 |
| `sina_extended.trade` | `eltdx.quote_snapshot.last_price` | 80.00% | 3 | 60 |
| `sina_extended.trade` | `fuyao.snapshot.last_price` | 80.00% | 3 | 60 |
| `sina_extended.trade` | `tdx.quote_full.price` | 80.00% | 3 | 60 |
| `sina_extended.trade` | `tencent[3]` | 80.00% | 3 | 60 |
| `push2.f126` | `zhb.stat.dividend_yield` | 75.00% | 1 | 12 |

_（仅显示前 60 / 共 97）_

## 五、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 六、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `fuyao.valuation.pe_ttm` | `zhb.stat.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 80 | T:20261014, T:20261016, T:20261019, T:20261020 | fuyao, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `fuyao.valuation.pe_ttm` | `zhb.full.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 80 | T:20261014, T:20261016, T:20261019, T:20261020 | fuyao, zhb | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9951, LOO稳号=True |
| `tencent[27]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9433, LOO稳号=True |
| `tencent[27]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9439, LOO稳号=True |
| `tencent[27]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.944, LOO稳号=True |
| `tencent[27]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9152, LOO稳号=True |
| `tencent[27]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9951, LOO稳号=True |
| `tencent[25]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9952, LOO稳号=True |
| `tencent[25]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9433, LOO稳号=True |
| `tencent[25]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9439, LOO稳号=True |
| `tencent[25]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.944, LOO稳号=True |
| `tencent[25]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9152, LOO稳号=True |
| `tencent[25]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9952, LOO稳号=True |
| `tencent[23]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9952, LOO稳号=True |
| `tencent[23]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9434, LOO稳号=True |
| `tencent[23]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9439, LOO稳号=True |
| `tencent[23]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.944, LOO稳号=True |
| `tencent[23]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9152, LOO稳号=True |
| `tencent[23]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9952, LOO稳号=True |
| `tencent[22]` | `sina[22]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[21]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9952, LOO稳号=True |
| `tencent[21]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9434, LOO稳号=True |
| `tencent[21]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9439, LOO稳号=True |
| `tencent[21]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.944, LOO稳号=True |
| `tencent[21]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9152, LOO稳号=True |
| `tencent[21]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9952, LOO稳号=True |
| `tencent[20]` | `sina[20]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[17]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9476, LOO稳号=True |
| `tencent[17]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[17]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.997, LOO稳号=True |
| `tencent[17]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9979, LOO稳号=True |
| `tencent[17]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9726, LOO稳号=True |
| `tencent[17]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9476, LOO稳号=True |
| `tencent[17]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9953, LOO稳号=True |
| `tencent[15]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9476, LOO稳号=True |
| `tencent[15]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[15]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.997, LOO稳号=True |
| `tencent[15]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9979, LOO稳号=True |
| `tencent[15]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9726, LOO稳号=True |
| `tencent[15]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9476, LOO稳号=True |
| `tencent[15]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9952, LOO稳号=True |
| `tencent[13]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9476, LOO稳号=True |
| `tencent[13]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[13]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.997, LOO稳号=True |
| `tencent[13]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9979, LOO稳号=True |
| `tencent[13]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9727, LOO稳号=True |
| `tencent[13]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9476, LOO稳号=True |
| `tencent[13]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9953, LOO稳号=True |
| `tencent[12]` | `sina[12]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[11]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9476, LOO稳号=True |
| `tencent[11]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[11]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.997, LOO稳号=True |
| `tencent[11]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.998, LOO稳号=True |
| `tencent[11]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9727, LOO稳号=True |
| `tencent[11]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9476, LOO稳号=True |
| `tencent[10]` | `sina[10]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `sina[29]` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9433, LOO稳号=True |
| `sina[29]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9998, Spearman=0.7532, LOO稳号=True |
| `sina[29]` | `tencent[51]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.944, LOO稳号=True |
| `sina[29]` | `tencent[42]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9439, LOO稳号=True |
| `sina[29]` | `tencent[41]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.944, LOO稳号=True |
| `sina[29]` | `tencent[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9152, LOO稳号=True |
| `sina[29]` | `tencent[34]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9439, LOO稳号=True |
| `sina[29]` | `tencent[33]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.944, LOO稳号=True |
| `sina[29]` | `tencent[19]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9951, LOO稳号=True |
| `sina[27]` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9433, LOO稳号=True |
| `sina[27]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9998, Spearman=0.7532, LOO稳号=True |
| `sina[27]` | `tencent[51]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.944, LOO稳号=True |
| `sina[27]` | `tencent[42]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9439, LOO稳号=True |
| `sina[27]` | `tencent[41]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.944, LOO稳号=True |
| `sina[27]` | `tencent[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9152, LOO稳号=True |
| `sina[27]` | `tencent[34]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9439, LOO稳号=True |
| `sina[27]` | `tencent[33]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.944, LOO稳号=True |
| `sina[27]` | `tencent[19]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9952, LOO稳号=True |
| `sina[25]` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9434, LOO稳号=True |
| `sina[25]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9998, Spearman=0.7534, LOO稳号=True |
| `sina[25]` | `tencent[51]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.944, LOO稳号=True |
| `sina[25]` | `tencent[42]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9439, LOO稳号=True |
| `sina[25]` | `tencent[41]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.944, LOO稳号=True |
| `sina[25]` | `tencent[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9152, LOO稳号=True |
| `sina[25]` | `tencent[34]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9439, LOO稳号=True |
| `sina[25]` | `tencent[33]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.944, LOO稳号=True |
| `sina[25]` | `tencent[19]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9952, LOO稳号=True |
| `sina[23]` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9434, LOO稳号=True |
| `sina[23]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9998, Spearman=0.7537, LOO稳号=True |
| `sina[23]` | `tencent[51]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.944, LOO稳号=True |
| `sina[23]` | `tencent[42]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9439, LOO稳号=True |
| `sina[23]` | `tencent[41]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.944, LOO稳号=True |
| `sina[23]` | `tencent[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9152, LOO稳号=True |
| `sina[23]` | `tencent[34]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9439, LOO稳号=True |
| `sina[23]` | `tencent[33]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.944, LOO稳号=True |
| `sina[23]` | `tencent[19]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9952, LOO稳号=True |
| `sina[19]` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `sina[19]` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9998, Spearman=0.8119, LOO稳号=True |
| `sina[19]` | `tencent[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=0.9999, Spearman=0.9953, LOO稳号=True |
| `sina[19]` | `tencent[51]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9985, LOO稳号=True |
| `sina[19]` | `tencent[42]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.997, LOO稳号=True |
| `sina[19]` | `tencent[41]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9979, LOO稳号=True |
| `sina[19]` | `tencent[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020 | sina, tencent | Pearson=1.0, Spearman=0.9726, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 七、日期与数据质量告警（154）

- 20260920: 旧式非交易日目录按前一交易日 20260918 归并；目录未改名
- 20261005: 旧式非交易日目录按前一交易日 20260930 归并；目录未改名
- 20261011: 旧式非交易日目录按前一交易日 20261009 归并；目录未改名
- 20261017: 旧式非交易日目录按前一交易日 20261016 归并；目录未改名
- 20261018: 旧式非交易日目录按前一交易日 20261016 归并；目录未改名
- 20260814: 行情数据日 20260814 属于配置的异常日，行情快照排除
- 20261013/ftshare: 采集状态 failed
- 20261013/ftshare: 来源状态为 failed，快照跳过
- 20261013/zhb: 来源有效交易日 20261012 不在本轮行情交易日窗口，快照跳过
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
- 另有 54 条告警，详见同名 JSON 报告。

---

> 数据来源：通达信 / 项目字段对撞体系。以上为方法论梳理，不构成投资建议。

## 来源身份状态（不参与字段语义定案）

_FTShare 公共 REST 接口已进入日常采集；官方字段契约作为语义锚，底层数据提供方仍未确认。与其匹配的强候选列在 L1-C，不混入独立来源 L1。_
_旧私有托管 MCP 采集器已退役，历史样本仅供 `--all` / `--exploratory` 追溯。_

## 官方契约锚候选 L1-C（0）

_L1-C 使用逐字段审定的官方接口契约语义作锚，并满足多日数值匹配门槛；仅当该接口底层数据来源独立性未确认时才列入此处，不属于独立来源 L1，也不自动定案。_

_本轮无达到多日门槛的官方契约锚候选。_

## 来源字段覆盖与碰撞参与

_窗口字段值样本是经日期筛选、重复折叠和快照择优后载入的非空值；右侧比较次数另受字段类型及来源规则筛选。官方契约字段须有逐字段审定证据，契约语义本身不证明底层数据来源独立。_

| 来源 | 已确认字段 | 契约已确认 | 契约锚 | 独立锚 | L1-C 锚 | 窗口字段 / 字段值样本 / 交易日 |
|:--|--:|--:|--:|--:|--:|--:|
| axdata | 0 | 0 | 0 | 0 | 0 | 34 / 2655 / 5 |
| clist | 18 | 0 | 0 | 18 | 0 | 0 / 0 / 0 |
| cls | 4 | 0 | 0 | 4 | 0 | 5 / 750 / 0 |
| datacenter | 41 | 0 | 0 | 41 | 0 | 0 / 0 / 0 |
| eltdx | 64 | 0 | 0 | 64 | 0 | 116 / 6523 / 6 |
| em_fund_flow | 0 | 0 | 0 | 0 | 0 | 15 / 195 / 1 |
| em_hot | 39 | 0 | 0 | 39 | 0 | 0 / 0 / 0 |
| em_kline_f61 | 10 | 0 | 0 | 10 | 0 | 0 / 0 / 0 |
| etf | 0 | 0 | 0 | 0 | 0 | 9 / 69556 / 6 |
| event_dc | 0 | 0 | 0 | 0 | 0 | 148 / 123422 / 4 |
| exchange | 4 | 0 | 0 | 4 | 0 | 0 / 0 / 0 |
| ftshare | 6 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| ftshare_rest | 31 | 31 | 31 | 0 | 31 | 32 / 1270 / 2 |
| fuyao | 83 | 69 | 69 | 83 | 0 | 20 / 1994 / 5 |
| kph | 6 | 0 | 0 | 6 | 0 | 15 / 2525 / 4 |
| kpl | 6 | 0 | 0 | 6 | 0 | 32 / 8146 / 7 |
| market_sources | 14 | 0 | 0 | 0 | 0 | 73 / 37027 / 6 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 2 / 116 / 0 |
| push2 | 39 | 0 | 0 | 39 | 0 | 114 / 1368 / 1 |
| push2ex | 21 | 0 | 0 | 21 | 0 | 16 / 6224 / 5 |
| reports | 26 | 0 | 0 | 26 | 0 | 0 / 0 / 0 |
| research_sina | 0 | 0 | 0 | 0 | 0 | 6 / 930 / 0 |
| sina | 18 | 0 | 0 | 18 | 0 | 39 / 4830 / 7 |
| sina_extended | 0 | 0 | 0 | 0 | 0 | 4 / 240 / 3 |
| slist | 5 | 0 | 0 | 5 | 0 | 0 / 0 / 0 |
| sse_e_interaction | 0 | 0 | 0 | 0 | 0 | 8 / 320 / 0 |
| st_list | 0 | 0 | 0 | 0 | 0 | 6 / 2046 / 1 |
| tdx | 80 | 0 | 0 | 80 | 0 | 75 / 7197 / 6 |
| tencent | 62 | 0 | 0 | 62 | 0 | 88 / 12306 / 7 |
| ulist239 | 44 | 0 | 0 | 44 | 0 | 0 / 0 / 0 |
| zhb | 85 | 0 | 0 | 85 | 0 | 124 / 10976 / 5 |

| 来源 | 破解目标 | 比较字段 | 作目标比较 | 作右侧比较 | L1-C 锚比较 | L1 / L1-C / L4 关系 | 方法候选涉及 |
|:--|--:|--:|--:|--:|--:|--:|--:|
| axdata | 30 | 0 | 627 | 0 | 0 | 0 / 0 / 5 | 63 |
| clist | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| cls | 2 | 0 | 310 | 0 | 0 | 0 / 0 / 0 | 0 |
| datacenter | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| eltdx | 30 | 50 | 3978 | 6580 | 0 | 0 / 0 / 5 | 634 |
| em_fund_flow | 15 | 0 | 3654 | 0 | 0 | 0 / 0 / 0 | 593 |
| em_hot | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| em_kline_f61 | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| etf | 4 | 0 | 29 | 0 | 0 | 0 / 0 / 0 | 0 |
| event_dc | 62 | 0 | 1258 | 0 | 0 | 0 / 0 / 0 | 0 |
| exchange | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare_rest | 1 | 25 | 23 | 7399 | 7399 | 0 / 0 / 11 | 555 |
| fuyao | 4 | 10 | 1132 | 2290 | 0 | 0 / 0 / 6 | 465 |
| kph | 4 | 6 | 878 | 1380 | 0 | 4 / 0 / 0 | 19 |
| kpl | 19 | 6 | 5147 | 1720 | 0 | 4 / 0 / 0 | 60 |
| market_sources | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| push2 | 57 | 34 | 13836 | 4863 | 0 | 0 / 0 / 49 | 2415 |
| push2ex | 10 | 2 | 2600 | 312 | 0 | 0 / 0 / 0 | 47 |
| reports | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| research_sina | 2 | 0 | 293 | 0 | 0 | 0 / 0 / 0 | 0 |
| sina | 17 | 17 | 4743 | 3007 | 0 | 0 / 0 / 26 | 1280 |
| sina_extended | 3 | 0 | 837 | 0 | 0 | 0 / 0 / 9 | 136 |
| slist | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| sse_e_interaction | 3 | 0 | 27 | 0 | 0 | 0 / 0 / 0 | 0 |
| st_list | 3 | 0 | 48 | 0 | 0 | 0 / 0 / 0 | 0 |
| tdx | 15 | 47 | 2482 | 6815 | 0 | 0 / 0 / 36 | 1266 |
| tencent | 23 | 56 | 5087 | 11072 | 0 | 2 / 0 / 29 | 2070 |
| ulist239 | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| zhb | 44 | 55 | 6424 | 7975 | 0 | 2 / 0 / 18 | 1653 |

## AxData 每日接口核验

> 此处汇总采集目录已保存的本地证据，不发起网络请求、不改变注册表状态；AxData 是多源框架，不作为独立字段锚。

### AxData

窗口内有 7 个唯一数据日的轮验记录；重复目录合并 0 条。
静态接口队列：257 个接口，3343 个字段出现项，低于 E3 的字段出现项 3343；当前主动探针白名单 `tencent_realtime_snapshot`。
静态候选策略：static review only until route, parameters, date basis, and request safety are approved。

| 数据日 | 轮验状态 | 探针状态 / 请求数 | 来源身份状态 | 短线配对 | KPH/KPL 配对 | 证据文件 |
|:--|:--|:--|:--|--:|--:|:--|
| 20261013 | not_eligible | not_run / 0 (字段相同/不同 0/0) | 未记录 | — | — | meta_summary |
| 20261014 | sampled | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 0 | — | full |
| 20261015 | probe_skipped | skipped_project_counterpart_failed / 0 (字段相同/不同 0/0) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 0 | — | full |
| 20261016 | already_recorded | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | — | 50 | full |
| 20261019 | sampled | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261020 | already_recorded | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | — | — | full |
| 20261021 | sampled | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | — | 45 | full |

被动逐字段比较中的差异计数（跨本窗口唯一数据日累加，不含原始值）：

| 比较路径 | 相同 | 不同 | 缺失/双方空值 |
|:--|--:|--:|--:|
| `kph_limit_up_history_vs_kpl_detail:seal_amount` | 0 | 95 | 0 |
| `kph_limit_up_history_vs_kpl_detail:seal_money` | 0 | 95 | 0 |
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

## 字母字段名语义提示（仅候选）

窗口内观察到 142 条需审阅的字母字段路径：含词义线索 43 条，仅拆词 99 条。
完整逐条记录保存在碰撞 JSON；名称线索清单：`docs/field_verification/20261014/20261014_alphabetic_field_name_inventory.csv`。
> 拼音、英文、缩写和混合拆词只用于检索候选；必须结合原始值、接口定义和独立来源复核，不得据此定案或改写主字典。

| 逐源字段路径 | 状态/审阅范围 | 名称形式与拆词 | 词义线索（非释义） | 样本日期 |
|:--|:--|:--|:--|:--|
| `市场源(market_sources)::change_type` | unverified / unverified_semantics | snake_case_or_mixed: change type | 变化/涨跌 + 类型 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `市场源(market_sources)::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `东财-push2ex::change_pct` | unverified / unverified_semantics | recognized_english_word_candidate: change pct | 变化/涨跌 + 百分比 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `东财-push2ex::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `东财-push2ex::first_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: first limit time | 首次/第一 + 涨跌停限制 + 时间 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `东财-push2ex::last_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: last limit time | 最近/上一期 + 涨跌停限制 + 时间 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `东财-push2ex::limit_count` | unverified / unverified_semantics | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `东财-push2ex::name` | unverified / unverified_semantics | recognized_english_word_candidate: name | 名称 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `东财-push2ex::price` | unverified / unverified_semantics | recognized_english_word_candidate: price | 价格 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `东财-push2ex::total_value` | unverified / unverified_semantics | snake_case_or_mixed: total value | 总 + 值 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `市场源(market_sources)::limit_count` | verified / verified_metadata_gap | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `市场源(market_sources)::limit_time` | unverified / unverified_semantics | snake_case_or_mixed: limit time | 涨跌停限制 + 时间 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `市场源(market_sources)::plate_limit_up_count` | verified / verified_metadata_gap | snake_case_or_mixed: plate limit up count | 涨跌停限制 + 上/涨 + 数量/次数 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `开盘红(Levistock适配)::limit_count` | unverified / unverified_semantics | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261013, T:20261016, T:20261019, T:20261021 |
| `开盘红(Levistock适配)::open_time` | unverified / unverified_semantics | snake_case_or_mixed: open time | 开盘 + 时间 | T:20261013, T:20261016, T:20261019, T:20261021 |
| `财联社(cls)::time` | unverified / unverified_semantics | recognized_english_word_candidate: time | 时间 | C:20261016, C:20261019, C:20261020 |
| `TDX(双命名源)::changqifuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: changqifuzhai | 长期负债 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::cunhuo` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: cunhuo | 存货 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::eps` | unverified / unverified_semantics | recognized_english_word_candidate: eps | 每股收益 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::fajirenfarengu` | unverified / unverified_semantics | recognized_pinyin_phrase_candidate: fajirenfarengu | 疑似 faqirenfarengu 的拼写变体；含义未证实 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::gudongrenshu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: gudongrenshu | 股东人数 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::ipodate` | unverified / unverified_semantics | recognized_english_phrase_candidate: ipodate | IPO/上市日期（字段语境候选） | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::jinglirun` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jinglirun | 净利润 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::jingyingxianjinliu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingyingxianjinliu | 经营现金流 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::jingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingzichan | 净资产 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::liudongfuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: liudongfuzhai | 流动负债 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::meigujingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: meigujingzichan | 每股净资产 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::yingshouzhangkuan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: yingshouzhangkuan | 应收账款 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::zhuyingshouru` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zhuyingshouru | 主营收入 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::zibengongjijin` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zibengongjijin | 资本公积金 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::zongzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongzichan | 总资产 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `ZHB-tdxstat::change_pct` | unverified / unverified_semantics | recognized_english_word_candidate: change pct | 变化/涨跌 + 百分比 | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat::change_pct_1d` | unverified / unverified_semantics | snake_case_or_mixed: change pct 1 d | 变化/涨跌 + 百分比 | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat::change_pct_2d` | unverified / unverified_semantics | snake_case_or_mixed: change pct 2 d | 变化/涨跌 + 百分比 | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `同花顺-fuyao::valuation.pb_mrq` | conflict / unverified_semantics | snake_case_or_mixed: valuation pb mrq | 市净率 + 最近报告期 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `同花顺-fuyao::valuation.pe_mrq` | conflict / unverified_semantics | snake_case_or_mixed: valuation pe mrq | 市盈率 + 最近报告期 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `同花顺-fuyao::valuation.pe_ttm` | conflict / unverified_semantics | snake_case_or_mixed: valuation pe ttm | 市盈率 + 滚动十二个月 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `ZHB-tdxstat2::main_net_buy_amount_1d` | unverified / unverified_semantics | snake_case_or_mixed: main net buy amount 1 d | 净 + 金额/成交额（需看接口） | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `同花顺-fuyao::snapshot.open_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot open price | 开盘 + 价格 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `ZHB-tdxstat2::main_net_buy_amount` | unverified / unverified_semantics | snake_case_or_mixed: main net buy amount | 净 + 金额/成交额（需看接口） | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `TDX(双命名源)::price` | unverified / unverified_semantics | recognized_english_word_candidate: price | 价格 | T:20261016, T:20261019, T:20261020, T:20261021 |
| `新浪(扩展API)::turnover` | conflict / unverified_semantics | recognized_english_word_candidate: turnover | 换手/成交额（需看接口） | T:20261019, T:20261020, T:20261021 |
| `TDX-eltdx(适配层)::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `东财-push2ex::broken_count` | unverified / unverified_semantics | snake_case_or_mixed: broken count | — | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `东财-push2ex::circulating_value` | unverified / unverified_semantics | snake_case_or_mixed: circulating value | — | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `东财-push2ex::sector` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: sector | — | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `东财-push2ex::turnover_rate` | unverified / unverified_semantics | snake_case_or_mixed: turnover rate | — | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `东财-push2ex::zt_continuous` | unverified / unverified_semantics | snake_case_or_mixed: zt continuous | — | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `东财-push2ex::zt_days` | unverified / unverified_semantics | snake_case_or_mixed: zt days | — | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `开盘啦(kpl_limit_up_detail)::max_seal` | verified / verified_metadata_gap | snake_case_or_mixed: max seal | — | T:20261013, T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `市场源(market_sources)::one_word` | unverified / unverified_semantics | snake_case_or_mixed: one word | — | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `市场源(market_sources)::plate_amount` | verified / verified_metadata_gap | snake_case_or_mixed: plate amount | — | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `市场源(market_sources)::plate_code` | verified / verified_metadata_gap | snake_case_or_mixed: plate code | — | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `市场源(market_sources)::plate_name` | verified / verified_metadata_gap | snake_case_or_mixed: plate name | — | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `市场源(market_sources)::popular` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: popular | — | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `财联社(cls)::content` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: content | — | C:20261016, C:20261019, C:20261020 |
| `财联社(cls)::level` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: level | — | C:20261016, C:20261019, C:20261020 |
| `财联社(cls)::reading_num` | unverified / unverified_semantics | snake_case_or_mixed: reading num | — | C:20261016, C:20261019, C:20261020 |
| `财联社(cls)::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20261016, C:20261019, C:20261020 |
| `开盘红(Levistock适配)::industry_id` | unverified / unverified_semantics | snake_case_or_mixed: industry id | — | T:20261016, T:20261019, T:20261021 |
| `开盘红(Levistock适配)::limit_tag` | unverified / unverified_semantics | snake_case_or_mixed: limit tag | — | T:20261016, T:20261019, T:20261021 |
| `开盘红(Levistock适配)::reason` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: reason | — | T:20261016, T:20261019, T:20261021 |
| `开盘红(Levistock适配)::themes` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: themes | — | T:20261016, T:20261019, T:20261021 |
| `TDX(双命名源)::baoliu2` | unverified / unverified_semantics | mixed_alphanumeric: baoliu 2 | — | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::ipo_date` | verified / verified_metadata_gap | snake_case_or_mixed: ipo date | — | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::updated_date` | verified / verified_metadata_gap | snake_case_or_mixed: updated date | — | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::updateddate` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: updateddate | — | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::zhuyinglyrun` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: zhuyinglyrun | — | T:20261014, T:20261015, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::b_vol` | unverified / unverified_semantics | snake_case_or_mixed: b vol | — | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::s_vol` | unverified / unverified_semantics | snake_case_or_mixed: s vol | — | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `ZHB-tdxstat::change_10k_bar` | unverified / unverified_semantics | snake_case_or_mixed: change 10 k bar | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat::change_5k_bar` | unverified / unverified_semantics | snake_case_or_mixed: change 5 k bar | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat::change_ytd` | unverified / unverified_semantics | snake_case_or_mixed: change ytd | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat::dividend_yield` | unverified / unverified_semantics | snake_case_or_mixed: dividend yield | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat::employee_count` | unverified / unverified_semantics | snake_case_or_mixed: employee count | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat::pe_lyr` | unverified / unverified_semantics | snake_case_or_mixed: pe lyr | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat::stat.unknown_2` | candidate / unverified_semantics | snake_case_or_mixed: stat unknown 2 | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat::stat.unknown_26` | conflict / unverified_semantics | snake_case_or_mixed: stat unknown 26 | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat::streak_days` | unverified / unverified_semantics | snake_case_or_mixed: streak days | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat::unseal_date` | unverified / unverified_semantics | snake_case_or_mixed: unseal date | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat2::amount_1d` | unverified / unverified_semantics | snake_case_or_mixed: amount 1 d | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat2::amount_2d` | unverified / unverified_semantics | snake_case_or_mixed: amount 2 d | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat2::change_250k_bar` | unverified / unverified_semantics | snake_case_or_mixed: change 250 k bar | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat2::change_30k_bar` | unverified / unverified_semantics | snake_case_or_mixed: change 30 k bar | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat2::change_30k_bar_ref` | unverified / unverified_semantics | snake_case_or_mixed: change 30 k bar ref | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat2::change_mtd` | unverified / unverified_semantics | snake_case_or_mixed: change mtd | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat2::high_52w` | unverified / unverified_semantics | snake_case_or_mixed: high 52 w | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat2::industry_code` | unverified / unverified_semantics | snake_case_or_mixed: industry code | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat2::ipo_price` | unverified / unverified_semantics | snake_case_or_mixed: ipo price | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `同花顺-fuyao::fin_report` | unverified / unverified_semantics | snake_case_or_mixed: fin report | — | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `同花顺-fuyao::snapshot.prev_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot prev price | — | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `同花顺-fuyao::valuation.ps_ttm` | conflict / unverified_semantics | snake_case_or_mixed: valuation ps ttm | — | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 |
| `ZHB-tdxstat2::main_net_buy_hands_1d` | unverified / unverified_semantics | snake_case_or_mixed: main net buy hands 1 d | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `ZHB-tdxstat2::main_net_buy_hands` | unverified / unverified_semantics | snake_case_or_mixed: main net buy hands | — | T:20261013, T:20261014, T:20261016, T:20261019, T:20261020 |
| `TDX(双命名源)::ask1` | unverified / unverified_semantics | mixed_alphanumeric: ask 1 | — | T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::ask1_vol` | unverified / unverified_semantics | runtime_tokenization_only: ask 1 vol | — | T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::b_vol` | unverified / unverified_semantics | snake_case_or_mixed: b vol | — | T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::bid1` | unverified / unverified_semantics | mixed_alphanumeric: bid 1 | — | T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::bid1_vol` | unverified / unverified_semantics | snake_case_or_mixed: bid 1 vol | — | T:20261016, T:20261019, T:20261020, T:20261021 |
| `TDX(双命名源)::s_vol` | unverified / unverified_semantics | snake_case_or_mixed: s vol | — | T:20261016, T:20261019, T:20261020, T:20261021 |

Markdown 显示前 100 条；其余 42 条完整保留在 JSON。

## 探索候选持续跟踪

研究台账：`collision_research_state.json.gz`；累计历史跟踪候选对 1663，本报告候选对 727，历史复现 426，新发现 0。
台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，不会自动改变字段状态、碰撞锚或主字典。新报告只将 `actionable_L1`、L4 和主动方法候选写入待研究队列；已登记关系的复验单独展示，历史跟踪记录不会被删除。

## 候选覆盖、公式与下一步采样

本节用于定位证据缺口和安排后续取样。相关性、公式与样本优先级均为探索候选；不会改变 L1/L1-U 门槛、来源独立性或主字典。

- 未知目标 350 个；其中有方法候选 196 个、无候选 154 个；多候选目标 192 个。
- 方法候选生成 5628 条；全局详细项保留 500/500，另按目标字段保留 175 条；完整明细 5628 条在 JSON `method_candidate_inventory`；未归档明细 0 条。
- 字段覆盖详情：available；覆盖身份 2006，读取 6 份本地索引。

### 优先处理字段

| 未知字段 | 当前诊断 | 独立对比/候选数 | 独立锚家族/本源日期 | 建议复核股票 | 最强候选线索 |
|:--|:--|--:|:--|:--|:--|
| `zhb.full.change_pct` | 公式候选待独立复核 | 123 / 16 | 6 家族 / 123 对 / 本源 5 日 | 600519 (9.540292) | fuyao.snapshot.price_change_ratio_pct (robust_correlation,affine_formula,per_stock_time_series); tencent[32] (robust_correlation,per_stock_time_series); zhb.full.change_pct ≈ 100.0068 × (fuyao.snapshot.price_change ÷ fuyao.snapshot.prev_pri |
| `push2.f108` | 存在多个候选，需区分 | 237 / 100 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.tipinfo.eps (robust_correlation,affine_formula); zhb.stat2.low_52w (robust_correlation,affine_formula) |
| `push2.f190` | 存在多个候选，需区分 | 237 / 99 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.tipinfo.eps (robust_correlation,affine_formula); zhb.stat2.low_52w (robust_correlation,affine_formula) |
| `push2.f92` | 存在多个候选，需区分 | 237 / 96 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.tipinfo.eps (robust_correlation,affine_formula); zhb.stat2.low_52w (robust_correlation,affine_formula) |
| `push2.f160` | 存在多个候选，需区分 | 237 / 94 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.tipinfo.eps (robust_correlation,affine_formula); zhb.stat2.low_52w (robust_correlation,affine_formula) |
| `push2.f193` | 存在多个候选，需区分 | 237 / 88 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat2.main_net_buy_amount_1d (robust_correlation); zhb.stat2.main_net_buy_amount (robust_correlation) |
| `sina[11]` | 存在多个候选，需区分 | 256 / 85 | 6 家族 / 256 对 / 本源 0 日 | 600519 (6.235886) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[13]` | 存在多个候选，需区分 | 256 / 85 | 6 家族 / 256 对 / 本源 0 日 | 600519 (6.223944) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[15]` | 存在多个候选，需区分 | 256 / 85 | 6 家族 / 256 对 / 本源 0 日 | 600519 (6.215416) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[17]` | 存在多个候选，需区分 | 256 / 85 | 6 家族 / 256 对 / 本源 0 日 | 600519 (6.213895) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[19]` | 存在多个候选，需区分 | 256 / 85 | 6 家族 / 256 对 / 本源 0 日 | 600519 (6.212457) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina_extended.trade` | 存在多个候选，需区分 | 256 / 78 | 6 家族 / 256 对 / 本源 0 日 | 600519 (6.857547) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f103` | 存在多个候选，需区分 | 237 / 77 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat.employee_count (robust_correlation,affine_formula); zhb.stat.cash_reserve_wan (robust_correlation,affine_formula) |
| `sina[23]` | 存在多个候选，需区分 | 256 / 77 | 6 家族 / 256 对 / 本源 0 日 | 600519 (6.362616) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[25]` | 存在多个候选，需区分 | 256 / 76 | 6 家族 / 256 对 / 本源 0 日 | 600519 (6.364531) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[27]` | 存在多个候选，需区分 | 256 / 76 | 6 家族 / 256 对 / 本源 0 日 | 600519 (6.367587) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[29]` | 存在多个候选，需区分 | 256 / 76 | 6 家族 / 256 对 / 本源 0 日 | 600519 (6.368923) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f183` | 存在多个候选，需区分 | 237 / 72 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tdx.finance_info.zhuyingshouru (robust_correlation,affine_formula); tdx.finance_info.farengu (robust_correlation,affine_formula) |
| `push2.f135` | 存在多个候选，需区分 | 237 / 71 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat2.main_net_buy_amount (robust_correlation,affine_formula); zhb.stat2.amount_1d (robust_correlation,affine_formula) |
| `push2.f141` | 存在多个候选，需区分 | 237 / 70 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat2.amount_1d (robust_correlation,affine_formula); zhb.stat2.amount (robust_correlation,affine_formula) |
| `push2.f175` | 存在多个候选，需区分 | 237 / 70 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.tipinfo.eps (robust_correlation,affine_formula); zhb.stat2.low_52w (robust_correlation,affine_formula) |
| `push2.f109` | 存在多个候选，需区分 | 237 / 69 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat.net_profit_kcf (robust_correlation,affine_formula); tdx.finance_info.yingyelirun (robust_correlation,affine_formula) |
| `push2.f142` | 存在多个候选，需区分 | 237 / 69 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat2.main_net_buy_amount (robust_correlation,affine_formula); zhb.stat2.amount_1d (robust_correlation,affine_formula) |
| `push2.f144` | 存在多个候选，需区分 | 237 / 69 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat2.amount_2d (robust_correlation,affine_formula); zhb.stat2.amount_1d (robust_correlation,affine_formula) |
| `push2.f60` | 存在多个候选，需区分 | 237 / 69 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.tipinfo.eps (robust_correlation,affine_formula); zhb.stat2.low_52w (robust_correlation,affine_formula) |
| `push2.f71` | 存在多个候选，需区分 | 237 / 69 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.tipinfo.eps (robust_correlation,affine_formula); zhb.stat2.low_52w (robust_correlation,affine_formula) |
| `push2.f136` | 存在多个候选，需区分 | 237 / 68 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat2.main_net_buy_amount (robust_correlation,affine_formula); zhb.stat2.amount_1d (robust_correlation,affine_formula) |
| `push2.f145` | 存在多个候选，需区分 | 237 / 66 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat2.amount_2d (robust_correlation,affine_formula); zhb.stat2.amount_1d (robust_correlation,affine_formula) |
| `tencent[11]` | 存在多个候选，需区分 | 218 / 66 | 6 家族 / 218 对 / 本源 0 日 | 600519 (2.138805) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[13]` | 存在多个候选，需区分 | 218 / 66 | 6 家族 / 218 对 / 本源 0 日 | 600519 (2.138315) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[15]` | 存在多个候选，需区分 | 218 / 66 | 6 家族 / 218 对 / 本源 0 日 | 600519 (2.138478) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[17]` | 存在多个候选，需区分 | 218 / 66 | 6 家族 / 218 对 / 本源 0 日 | 600519 (2.138724) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `em_fund_flow.f140` | 存在多个候选，需区分 | 237 / 65 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[58] (robust_correlation,affine_formula); zhb.tipinfo.eps (robust_correlation) |
| `push2.f174` | 存在多个候选，需区分 | 237 / 64 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.tipinfo.eps (robust_correlation,affine_formula); zhb.stat2.low_52w (robust_correlation,affine_formula) |
| `push2.f119` | 存在多个候选，需区分 | 237 / 62 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat.change_5d (robust_correlation,affine_formula); zhb.full.change_5d (robust_correlation,affine_formula) |
| `push2.f186` | 存在多个候选，需区分 | 237 / 60 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat2.low_52w (robust_correlation); zhb.stat2.ipo_price (robust_correlation) |
| `tencent[21]` | 存在多个候选，需区分 | 218 / 60 | 6 家族 / 218 对 / 本源 0 日 | 600519 (1.673768) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[23]` | 存在多个候选，需区分 | 218 / 60 | 6 家族 / 218 对 / 本源 0 日 | 600519 (1.672965) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[25]` | 存在多个候选，需区分 | 218 / 60 | 6 家族 / 218 对 / 本源 0 日 | 600519 (1.672291) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[27]` | 存在多个候选，需区分 | 218 / 60 | 6 家族 / 218 对 / 本源 0 日 | 600519 (1.671508) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `em_fund_flow.f137` | 存在多个候选，需区分 | 237 / 59 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat2.amount (robust_correlation,affine_formula); zhb.full.amount (robust_correlation,affine_formula) |
| `em_fund_flow.f144` | 存在多个候选，需区分 | 237 / 59 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat2.amount_2d (robust_correlation,affine_formula); zhb.stat2.amount_1d (robust_correlation,affine_formula) |
| `em_fund_flow.f142` | 存在多个候选，需区分 | 237 / 58 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat2.amount_2d (robust_correlation,affine_formula); zhb.stat2.amount_1d (robust_correlation,affine_formula) |
| `em_fund_flow.f145` | 存在多个候选，需区分 | 237 / 58 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat2.amount_2d (robust_correlation,affine_formula); zhb.stat2.amount_1d (robust_correlation,affine_formula) |
| `em_fund_flow.f135` | 存在多个候选，需区分 | 237 / 56 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat2.amount_2d (robust_correlation,affine_formula); zhb.stat2.amount_1d (robust_correlation,affine_formula) |
| `tdx.quote_raw.price` | 存在多个候选，需区分 | 123 / 56 | 6 家族 / 123 对 / 本源 0 日 | 600519 (6.602655) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `tdx.quote_raw.ask1` | 存在多个候选，需区分 | 123 / 55 | 6 家族 / 123 对 / 本源 0 日 | 600519 (6.813487) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `tdx.quote_raw.bid1` | 存在多个候选，需区分 | 123 / 54 | 6 家族 / 123 对 / 本源 0 日 | 600519 (6.581018) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `em_fund_flow.f141` | 存在多个候选，需区分 | 237 / 51 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | zhb.stat2.amount_2d (robust_correlation,affine_formula); zhb.stat2.amount_1d (robust_correlation,affine_formula) |
| `fuyao.valuation.ps_ttm` | 存在多个候选，需区分 | 260 / 51 | 6 家族 / 260 对 / 本源 5 日 | 600519 (9.771789) | tencent[46] (robust_correlation,per_stock_time_series); tencent[9] (per_stock_time_series) |

_此表显示优先级最高的 50 / 共 350 个目标；完整清单见 JSON。_


### 补足全局截断的字段候选（175）

| 未知字段 | 候选字段 | 方法 | 样本 | 日期 | 来源 |
|:--|:--|:--|--:|:--|:--|
| `axdata.data.float_shares` | `ftshare_rest.shares` | robust_correlation, affine_formula | 20 | T:20261020 | axdata, ftshare_rest |
| `axdata.data.free_float_shares` | `ftshare_rest.shares` | robust_correlation, affine_formula | 20 | T:20261020 | axdata, ftshare_rest |
| `axdata.data.open_amount` | `ftshare_rest.volume` | robust_correlation | 20 | T:20261020 | axdata, ftshare_rest |
| `axdata.data.open_prev_amount_ratio` | `ftshare_rest.change_rate_day60` | robust_correlation | 20 | T:20261020 | axdata, ftshare_rest |
| `axdata.data.open_price` | `ftshare_rest.prev_close` | robust_correlation, affine_formula | 20 | T:20261020 | axdata, ftshare_rest |
| `axdata.data.open_turnover_z` | `ftshare_rest.turnover_rate` | robust_correlation | 20 | T:20261020 | axdata, ftshare_rest |
| `axdata.data.open_volume_hand` | `ftshare_rest.volume` | robust_correlation | 20 | T:20261020 | axdata, ftshare_rest |
| `axdata.data.open_volume_ratio` | `ftshare_rest.change_rate_day60` | robust_correlation | 20 | T:20261020 | axdata, ftshare_rest |
| `axdata.data.pre_close` | `ftshare_rest.prev_close` | robust_correlation, affine_formula | 20 | T:20261020 | axdata, ftshare_rest |
| `axdata.data.prev_amount` | `ftshare_rest.volume` | robust_correlation | 20 | T:20261020 | axdata, ftshare_rest |
| `axdata.data.prev_open_amount` | `ftshare_rest.volume` | robust_correlation | 20 | T:20261020 | axdata, ftshare_rest |
| `axdata.data.prev_open_volume_hand` | `ftshare_rest.volume` | robust_correlation | 20 | T:20261020 | axdata, ftshare_rest |
| `axdata.data.seal_amount` | `ftshare_rest.volume` | robust_correlation | 20 | T:20261020 | axdata, ftshare_rest |
| `axdata.data.seal_to_float_ratio` | `ftshare_rest.turnover_rate` | robust_correlation | 20 | T:20261020 | axdata, ftshare_rest |
| `em_fund_flow.f135` | `zhb.stat2.amount_2d` | robust_correlation, affine_formula | 13 | T:20261019 | em_fund_flow, zhb |
| `em_fund_flow.f136` | `zhb.stat2.amount_2d` | robust_correlation, affine_formula | 13 | T:20261019 | em_fund_flow, zhb |
| `em_fund_flow.f137` | `zhb.stat2.amount` | robust_correlation, affine_formula | 13 | T:20261019 | em_fund_flow, zhb |
| `em_fund_flow.f140` | `tencent[58]` | robust_correlation, affine_formula | 13 | T:20261019 | em_fund_flow, tencent |
| `em_fund_flow.f141` | `zhb.stat2.amount_2d` | robust_correlation, affine_formula | 13 | T:20261019 | em_fund_flow, zhb |
| `em_fund_flow.f142` | `zhb.stat2.amount_2d` | robust_correlation, affine_formula | 13 | T:20261019 | em_fund_flow, zhb |
| `em_fund_flow.f143` | `tencent[9]` | robust_correlation | 13 | T:20261019 | em_fund_flow, tencent |
| `em_fund_flow.f144` | `zhb.stat2.amount_2d` | robust_correlation, affine_formula | 13 | T:20261019 | em_fund_flow, zhb |
| `em_fund_flow.f145` | `zhb.stat2.amount_2d` | robust_correlation, affine_formula | 13 | T:20261019 | em_fund_flow, zhb |
| `em_fund_flow.f146` | `zhb.stat2.low_52w` | affine_formula | 13 | T:20261019 | em_fund_flow, zhb |
| `em_fund_flow.f147` | `zhb.stat2.main_net_buy_hands_1d` | robust_correlation | 13 | T:20261019 | em_fund_flow, zhb |
| `em_fund_flow.f148` | `zhb.stat2.main_net_buy_hands_1d` | robust_correlation | 13 | T:20261019 | em_fund_flow, zhb |
| `em_fund_flow.f149` | `zhb.stat.change_5d` | robust_correlation | 13 | T:20261019 | em_fund_flow, zhb |
| `fuyao.valuation.pb_mrq` | `tencent[9]` | per_stock_time_series | 100 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 | fuyao, tencent |
| `fuyao.valuation.pe_mrq` | `tencent[39]` | robust_correlation, per_stock_time_series | 100 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 | fuyao, tencent |
| `fuyao.valuation.pe_ttm` | `tencent[52]` | robust_correlation, per_stock_time_series | 100 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 | fuyao, tencent |
| `fuyao.valuation.ps_ttm` | `tencent[46]` | robust_correlation, per_stock_time_series | 100 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 | fuyao, tencent |
| `kpl.amplitude` | `push2ex.limit_fund` | per_stock_time_series | 232 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 | kpl, push2ex |
| `kpl.main_buy` | `kph.seal_money` | robust_correlation | 181 | T:20261013, T:20261016, T:20261019, T:20261021 | kph, kpl |
| `kpl.main_sell` | `kph.turnover` | robust_correlation | 181 | T:20261013, T:20261016, T:20261019, T:20261021 | kph, kpl |
| `kpl.raw_columns.col_04` | `kph.limit_time` | robust_correlation, affine_formula | 135 | T:20261016, T:20261019, T:20261021 | kph, kpl |
| `kpl.raw_columns.col_07` | `kph.seal_money` | robust_correlation, affine_formula | 135 | T:20261016, T:20261019, T:20261021 | kph, kpl |
| `kpl.raw_columns.col_08` | `kph.net_inflow` | robust_correlation, affine_formula | 135 | T:20261016, T:20261019, T:20261021 | kph, kpl |
| `kpl.raw_columns.col_09` | `kph.turnover` | robust_correlation, affine_formula | 135 | T:20261016, T:20261019, T:20261021 | kph, kpl |
| `kpl.raw_columns.col_10` | `kph.turnover` | robust_correlation | 135 | T:20261016, T:20261019, T:20261021 | kph, kpl |
| `kpl.raw_columns.col_13` | `push2ex.amount` | robust_correlation | 211 | T:20261016, T:20261019, T:20261020, T:20261021 | kpl, push2ex |
| `kpl.raw_columns.col_14` | `kph.turnover_rate` | robust_correlation, affine_formula | 135 | T:20261016, T:20261019, T:20261021 | kph, kpl |
| `kpl.raw_columns.col_16` | `push2ex.limit_fund` | per_stock_time_series | 211 | T:20261016, T:20261019, T:20261020, T:20261021 | kpl, push2ex |
| `kpl.raw_columns.col_17` | `push2ex.limit_fund` | per_stock_time_series | 211 | T:20261016, T:20261019, T:20261020, T:20261021 | kpl, push2ex |
| `push2.f103` | `zhb.stat.employee_count` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f108` | `zhb.tipinfo.eps` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f109` | `zhb.stat.net_profit_kcf` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f119` | `zhb.stat.change_5d` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f120` | `zhb.stat.change_20k_bar` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f135` | `zhb.stat2.main_net_buy_amount` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f136` | `zhb.stat2.main_net_buy_amount` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f137` | `zhb.stat2.main_net_buy_amount_1d` | robust_correlation | 12 | T:20261020 | push2, zhb |
| `push2.f140` | `ftshare_rest.ts_millis` | robust_correlation | 12 | T:20261020 | ftshare_rest, push2 |
| `push2.f141` | `zhb.stat2.amount_1d` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f142` | `zhb.stat2.main_net_buy_amount` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f143` | `tdx.finance_info.cunhuo` | robust_correlation | 12 | T:20261020 | push2, tdx |
| `push2.f144` | `zhb.stat2.amount_2d` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f145` | `zhb.stat2.amount_2d` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f146` | `zhb.stat.change_pct_1d` | robust_correlation | 12 | T:20261020 | push2, zhb |
| `push2.f148` | `zhb.stat2.main_net_buy_hands_1d` | robust_correlation | 12 | T:20261020 | push2, zhb |
| `push2.f149` | `zhb.stat.change_20k_bar` | robust_correlation | 12 | T:20261020 | push2, zhb |
| `push2.f160` | `zhb.tipinfo.eps` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f161` | `zhb.stat2.main_net_buy_hands_1d` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f162` | `tencent[52]` | robust_correlation, affine_formula | 12 | T:20261020 | push2, tencent |
| `push2.f163` | `tencent[53]` | robust_correlation, affine_formula | 12 | T:20261020 | push2, tencent |
| `push2.f164` | `zhb.stat.pe_ttm` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f165` | `tencent[46]` | robust_correlation | 12 | T:20261020 | push2, tencent |
| `push2.f166` | `fuyao.valuation.pcf_ttm` | robust_correlation, affine_formula | 12 | T:20261020 | fuyao, push2 |
| `push2.f167` | `tencent[46]` | robust_correlation, affine_formula | 12 | T:20261020 | push2, tencent |
| `push2.f174` | `zhb.tipinfo.eps` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f175` | `zhb.tipinfo.eps` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f176` | `tencent[46]` | robust_correlation | 12 | T:20261020 | push2, tencent |
| `push2.f177` | `zhb.tipinfo.eps` | robust_correlation | 12 | T:20261020 | push2, zhb |
| `push2.f181` | `tencent[6]` | robust_correlation | 12 | T:20261020 | push2, tencent |
| `push2.f183` | `tdx.finance_info.zhuyingshouru` | robust_correlation, affine_formula | 12 | T:20261020 | push2, tdx |
| `push2.f184` | `tencent[74]` | robust_correlation | 12 | T:20261020 | push2, tencent |
| `push2.f185` | `tencent[74]` | robust_correlation | 12 | T:20261020 | push2, tencent |
| `push2.f186` | `zhb.stat2.low_52w` | robust_correlation | 12 | T:20261020 | push2, zhb |
| `push2.f187` | `zhb.tipinfo.eps` | robust_correlation | 12 | T:20261020 | push2, zhb |
| `push2.f188` | `zhb.stat.pe_ttm` | robust_correlation | 12 | T:20261020 | push2, zhb |
| `push2.f190` | `zhb.tipinfo.eps` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f191` | `tencent[74]` | robust_correlation, affine_formula | 12 | T:20261020 | push2, tencent |
| `push2.f192` | `tencent[50]` | robust_correlation, affine_formula | 12 | T:20261020 | push2, tencent |
| `push2.f193` | `zhb.stat2.main_net_buy_amount_1d` | robust_correlation | 12 | T:20261020 | push2, zhb |
| `push2.f194` | `zhb.stat.other_qy_jzc` | robust_correlation | 12 | T:20261020 | push2, zhb |
| `push2.f195` | `zhb.stat2.change_30k_bar_ref` | robust_correlation | 12 | T:20261020 | push2, zhb |
| `push2.f196` | `tencent[80]` | robust_correlation | 12 | T:20261020 | push2, tencent |
| `push2.f197` | `zhb.stat2.change_mtd` | robust_correlation | 12 | T:20261020 | push2, zhb |
| `push2.f49` | `zhb.stat2.main_net_buy_hands_1d` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f57` | `tencent[2]` | robust_correlation, affine_formula | 12 | T:20261020 | push2, tencent |
| `push2.f60` | `zhb.tipinfo.eps` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f71` | `zhb.tipinfo.eps` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2.f92` | `zhb.tipinfo.eps` | robust_correlation, affine_formula | 12 | T:20261020 | push2, zhb |
| `push2ex.broken_count` | `kpl.turnover_real` | per_stock_time_series | 232 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 | kpl, push2ex |
| `push2ex.circulating_value` | `kpl.zt_time` | per_stock_time_series | 232 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 | kpl, push2ex |
| `push2ex.first_limit_time` | `kpl.seal_amount` | per_stock_time_series | 232 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 | kpl, push2ex |
| `push2ex.limit_count` | `kpl.zt_time` | per_stock_time_series | 232 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 | kpl, push2ex |
| `push2ex.price` | `kpl.zt_time` | per_stock_time_series | 232 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 | kpl, push2ex |
| `push2ex.total_value` | `kpl.zt_time` | per_stock_time_series | 232 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 | kpl, push2ex |
| `push2ex.turnover_rate` | `kph.turnover_rate` | robust_correlation, semantic_label | 135 | T:20261016, T:20261019, T:20261021 | kph, push2ex |
| `push2ex.zt_continuous` | `kpl.zt_time` | per_stock_time_series | 232 | T:20261014, T:20261016, T:20261019, T:20261020, T:20261021 | kpl, push2ex |

_仅显示前 100 / 共 175 条字段前沿候选。_


### 双输入公式候选（1）

公式使用按股票代码分组的留出样本验证；至少 3 个留出股票，验证 R²≥0.985、误差不超过训练目标标准差的 5%，并要求优于最佳单输入线性模型至少 0.05。这些阈值只筛选探索候选，不构成语义证明。

| 目标字段 | 候选公式 | 留出 R² | 相对误差尺度 | 验证样本/股票 |
|:--|:--|--:|--:|--:|
| `zhb.full.change_pct` | `zhb.full.change_pct ≈ 100.0068 × (fuyao.snapshot.price_change ÷ fuyao.snapshot.prev_price) + -0.00045955135` | 1.0 | 0.000687 | 11/3 |

### 已知映射与已证伪关系的候选校准

- 已登记正向对照：当前窗口有 105 组独立数值关系可评估，104 组被方法候选识别；样本不足 1 组。此计数仅检查方法覆盖，不是准确率。
- 已证伪负向对照：数值关系 0 组，其中仍有方法信号 0 组；这些信号被隔离，不进入普通候选。

### 采集覆盖异常源

- axdata: 20261021 ({'failed': 1, 'ok': 5})
- baidu: 20261016, 20261020, 20261021 ({'deprecated': 4, 'pending_validation': 2})
- clist: 20261015, 20261020, 20261021 ({'partial': 4})
- em_fund_flow: 20261019, 20261020, 20261021 ({'partial': 5})
- em_hot: 20261015, 20261020, 20261021 ({'context_only': 4})
- em_kline_f61: 20261019, 20261020, 20261021 ({'partial': 5})
- exchange: 20261015, 20261020, 20261021 ({'context_only': 4})
- ftshare: 20261019, 20261020, 20261021 ({'deprecated': 2, 'failed': 5})
- news_wscn_cctv: 20261015 ({'ok': 6, 'partial': 1})
- push2: 20261015, 20261020, 20261021 ({'failed': 3, 'partial': 1})
- slist: 20261015, 20261020, 20261021 ({'failed': 4})
- sse_e_interaction: 20261014, 20261016 ({'ok': 5, 'partial': 2})
- st_list: 20261015, 20261020, 20261021 ({'ok': 1, 'partial': 4})
- ulist239: 20261019, 20261020, 20261021 ({'failed': 5})
- zhb: 20261019, 20261020, 20261021 ({'ok': 3, 'partial': 3})

## 候选身份与人工审阅状态

- 候选身份：生成 5730 条，唯一候选 5730 个，重复身份 0，无效身份 0。
- 审阅台账：可用；当前状态 `pending`；已审 0，待处理 5730，覆盖率 0.0%。
- 重复归并组：0；每个成员均保留到代表候选的反向追溯。
- 处置计数：`accepted_for_adjudication` 0；`duplicate_grouped` 0；`insufficient_evidence` 0；`needs_external_evidence` 0；`rejected` 0；`unreviewed` 5730。
- `accepted_for_adjudication` 只表示可进入现有证据裁决流程；审阅台账不会修改主字典或字段注册表。

## 报告完整性与审阅范围

- 机器可读完整性：`complete`；方法候选生成 5628 条，完整明细保存 5628 条，缺失 0 条，多余 0 条，重复 0 条，身份无效 0 条。
- 全量方法候选位于同名 JSON 的 `method_candidate_inventory`；Markdown 的 Top-N 表格是导航摘要，不能代替全量 JSON 审阅。
- 候选审阅数据对账：`complete`；唯一候选 5730 个，审阅 0 个，待处理 5730 个；人工审阅进度与机器清单完整性分别统计。
- Markdown 未逐行展示、但 JSON 保留的部分：
  - `L4`：展示 60 / 97，摘要省略 37 条。
  - `method_candidates`：展示 100 / 500，摘要省略 400 条。
  - `method_candidate_inventory`：展示 0 / 5628，摘要省略 5628 条。
  - `method_candidate_frontier`：展示 100 / 175，摘要省略 75 条。
  - `candidate_triage.targets`：展示 50 / 350，摘要省略 300 条。
  - `diagnostics`：展示 100 / 154，摘要省略 54 条。
- 完整性对账通过；逐目标复核仍须覆盖 JSON 的全部明细，并为每项记录已检查、重复归并、证据不足或需外部核验的处置。
