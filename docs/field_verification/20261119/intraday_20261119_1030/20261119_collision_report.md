# 全源对撞报告（20261119）

> 交易数据窗口配置：近 7 个交易日（`--window`），行情数据截至 20261118
> 行情窗口：20261110 ~ 20261118（7 个不同交易日）｜字段 1300 个｜样本值 386361 条
> 新闻/公告自然日窗口：20261113 ~ 20261119
> 主攻目标（unverified）=107｜可审定新候选=0｜首次发现新候选对=0｜已登记关系复验=0｜异号同义 0 / 同号镜像 0

> **规则**：L1 每日需≥18 组有效配对，并至少有5 组信息配对；双方同时为 0 或同时缺失不计命中率，一侧为 0、另一侧非 0 按失配计。信息配对命中率≥90%，且覆盖至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。JSON `daily_sample_counts` 与 `daily_informative_sample_counts`分别保留每日有效配对数和 L1 信息配对数。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 新候选 — 异号同义（跨编号，高价值）(0)

_本轮无异号同义候选。_


## 二、L1 / L1-U 新候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、已登记映射的本窗口复验（0）

_这些关系已在主注册表登记，只用于观察当前样本是否仍支持既有映射；它们不是新的未知字段候选，也不能再次提交为新定案。_

_本轮没有已登记关系进入复验窗口。_


## 四、L4 存疑候选（3）

| 左字段 | 右字段 | 关系类别 | 证据依据 | 处理进度 | 命中率 | 天数 | 配对数 | 信息配对数 |
|:--|:--|:--|:--|:--|--:|--:|--:|--:|
| `kph.industry_limit_up_count` | `kpl.raw_columns.col_20` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 80.58% | 3 | 103 | 103 |
| `kpl.raw_columns.col_02` | `kph.limit_count` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 44.66% | 3 | 103 | 103 |
| `kpl.raw_columns.col_02` | `push2ex.limit_count` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 40.00% | 5 | 240 | 240 |

## 五、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 六、主动方法候选（不直接定案）（150）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `kph.industry_limit_up_count` | `kpl.raw_columns.col_20` | robust_correlation, affine_formula | 103 | T:20261116, T:20261117, T:20261118 | kph, kpl | Pearson=0.9907, Spearman=0.9816, LOO稳号=True |
| `ulist239.f63` | `tencent[71]` | robust_correlation, per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.4493, Spearman=0.7298, LOO稳号=True |
| `ulist239.f63` | `ftshare_rest.change_rate_day60` | robust_correlation, per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | ftshare_rest, ulist239 | Pearson=0.4445, Spearman=0.7297, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.open_volume_ratio` | robust_correlation, per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.5061, Spearman=0.6931, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.open_volume_hand` | robust_correlation, per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.4497, Spearman=0.8237, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.open_prev_amount_ratio` | robust_correlation, per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.4021, Spearman=0.7525, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.open_amount` | robust_correlation, per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.8086, Spearman=0.9751, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.beta_60d` | robust_correlation, per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | eltdx, ulist239 | Pearson=-0.5278, Spearman=-0.6051, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.open_amount_yuan` | robust_correlation, per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.8086, Spearman=0.9751, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.open_amount_raw` | robust_correlation, per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.8086, Spearman=0.9751, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.current_hand` | robust_correlation, per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.2356, Spearman=0.7089, LOO稳号=True |
| `ulist239.f63` | `zhb.tipinfo.hg_amount_yi` | robust_correlation, affine_formula | 12 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.9976, Spearman=0.7492, LOO稳号=True |
| `kph.industry_limit_up_count` | `push2ex.limit_count` | semantic_label | 103 | T:20261116, T:20261117, T:20261118 | kph, push2ex | count, limit |
| `ulist239.f99` | `tencent[70]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9625, 方向一致=0.8125 |
| `ulist239.f99` | `tencent[67]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9011, 方向一致=0.8571 |
| `ulist239.f99` | `ftshare_rest.change_rate_day20` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | ftshare_rest, ulist239 | 逐股相关=0.9621, 方向一致=0.8125 |
| `ulist239.f63` | `tencent[9]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.955, 方向一致=0.8 |
| `ulist239.f63` | `tencent[79]` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.4857, Spearman=0.6798, LOO稳号=True |
| `ulist239.f63` | `tencent[76]` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.1451, Spearman=0.6162, LOO稳号=True |
| `ulist239.f63` | `tencent[75]` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.4953, Spearman=0.7244, LOO稳号=True |
| `ulist239.f63` | `tencent[72]` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.1451, Spearman=0.6162, LOO稳号=True |
| `ulist239.f63` | `tencent[62]` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.4793, Spearman=0.678, LOO稳号=True |
| `ulist239.f63` | `tencent[5]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.944, 方向一致=0.8 |
| `ulist239.f63` | `tencent[58]` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.3876, Spearman=0.9145, LOO稳号=True |
| `ulist239.f63` | `tencent[57]` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.9098, Spearman=0.9585, LOO稳号=True |
| `ulist239.f63` | `tencent[51]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9313, 方向一致=0.8 |
| `ulist239.f63` | `tencent[4]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9257, 方向一致=0.85 |
| `ulist239.f63` | `tencent[48]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9259, 方向一致=0.85 |
| `ulist239.f63` | `tencent[47]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9255, 方向一致=0.85 |
| `ulist239.f63` | `tencent[45]` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.5442, Spearman=0.7844, LOO稳号=True |
| `ulist239.f63` | `tencent[44]` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.5675, Spearman=0.7936, LOO稳号=True |
| `ulist239.f63` | `tencent[42]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9438, 方向一致=0.8 |
| `ulist239.f63` | `tencent[41]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9382, 方向一致=0.85 |
| `ulist239.f63` | `tencent[37]` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.9098, Spearman=0.9585, LOO稳号=True |
| `ulist239.f63` | `tencent[34]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9438, 方向一致=0.8 |
| `ulist239.f63` | `tencent[33]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9382, 方向一致=0.85 |
| `ulist239.f63` | `tencent[27]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9563, 方向一致=0.8 |
| `ulist239.f63` | `tencent[25]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9574, 方向一致=0.8 |
| `ulist239.f63` | `tencent[23]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9546, 方向一致=0.8 |
| `ulist239.f63` | `tencent[21]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9546, 方向一致=0.8 |
| `ulist239.f63` | `tencent[20]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9348, 方向一致=0.8 |
| `ulist239.f63` | `tencent[19]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9535, 方向一致=0.8 |
| `ulist239.f63` | `tencent[17]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9641, 方向一致=0.8 |
| `ulist239.f63` | `tencent[15]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9563, 方向一致=0.8 |
| `ulist239.f63` | `tencent[13]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9565, 方向一致=0.8 |
| `ulist239.f63` | `tencent[11]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tencent, ulist239 | 逐股相关=0.9578, 方向一致=0.8 |
| `ulist239.f63` | `tdx.s_vol` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.3225, Spearman=0.6607, LOO稳号=True |
| `ulist239.f63` | `tdx.quote_raw.s_vol` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.3225, Spearman=0.6607, LOO稳号=True |
| `ulist239.f63` | `tdx.quote_raw.open` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | 逐股相关=0.944, 方向一致=0.8 |
| `ulist239.f63` | `tdx.quote_raw.low` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | 逐股相关=0.9438, 方向一致=0.8 |
| `ulist239.f63` | `tdx.quote_raw.last_close` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | 逐股相关=0.9257, 方向一致=0.85 |
| `ulist239.f63` | `tdx.quote_raw.high` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | 逐股相关=0.9382, 方向一致=0.85 |
| `ulist239.f63` | `tdx.quote_raw.bid1` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | 逐股相关=0.955, 方向一致=0.8 |
| `ulist239.f63` | `tdx.quote_raw.b_vol` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.309, Spearman=0.6832, LOO稳号=True |
| `ulist239.f63` | `tdx.quote_raw.ask1_vol` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | 逐股相关=0.9348, 方向一致=0.8 |
| `ulist239.f63` | `tdx.quote_raw.ask1` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | 逐股相关=0.9535, 方向一致=0.8 |
| `ulist239.f63` | `tdx.quote_raw.amount` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.9098, Spearman=0.9585, LOO稳号=True |
| `ulist239.f63` | `tdx.quote_full.s_vol` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.3225, Spearman=0.6607, LOO稳号=True |
| `ulist239.f63` | `tdx.quote_full.open` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | 逐股相关=0.944, 方向一致=0.8 |
| `ulist239.f63` | `tdx.quote_full.low` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | 逐股相关=0.9438, 方向一致=0.8 |
| `ulist239.f63` | `tdx.quote_full.last_close` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | 逐股相关=0.9257, 方向一致=0.85 |
| `ulist239.f63` | `tdx.quote_full.high` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | 逐股相关=0.9382, 方向一致=0.85 |
| `ulist239.f63` | `tdx.quote_full.bid1` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | 逐股相关=0.955, 方向一致=0.8 |
| `ulist239.f63` | `tdx.quote_full.b_vol` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.309, Spearman=0.6832, LOO稳号=True |
| `ulist239.f63` | `tdx.quote_full.ask1_vol` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | 逐股相关=0.9348, 方向一致=0.8 |
| `ulist239.f63` | `tdx.quote_full.ask1` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | 逐股相关=0.9535, 方向一致=0.8 |
| `ulist239.f63` | `tdx.quote_full.amount_wan` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.9098, Spearman=0.9585, LOO稳号=True |
| `ulist239.f63` | `tdx.finance_info.zongzichan` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.1485, Spearman=0.6127, LOO稳号=True |
| `ulist239.f63` | `tdx.finance_info.zhuyinglyrun` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.1754, Spearman=0.6285, LOO稳号=True |
| `ulist239.f63` | `tdx.finance_info.gudongrenshu` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.4292, Spearman=0.731, LOO稳号=True |
| `ulist239.f63` | `tdx.b_vol` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.309, Spearman=0.6832, LOO稳号=True |
| `ulist239.f63` | `sina_extended.trade` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina_extended, ulist239 | 逐股相关=0.8727, 方向一致=0.8 |
| `ulist239.f63` | `sina[9]` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | Pearson=0.9098, Spearman=0.9585, LOO稳号=True |
| `ulist239.f63` | `sina[8]` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | Pearson=0.3159, Spearman=0.671, LOO稳号=True |
| `ulist239.f63` | `sina[7]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.9535, 方向一致=0.8 |
| `ulist239.f63` | `sina[6]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.955, 方向一致=0.8 |
| `ulist239.f63` | `sina[5]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.9438, 方向一致=0.8 |
| `ulist239.f63` | `sina[4]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.9382, 方向一致=0.85 |
| `ulist239.f63` | `sina[2]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.9257, 方向一致=0.85 |
| `ulist239.f63` | `sina[29]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.9563, 方向一致=0.8 |
| `ulist239.f63` | `sina[27]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.9574, 方向一致=0.8 |
| `ulist239.f63` | `sina[25]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.9546, 方向一致=0.8 |
| `ulist239.f63` | `sina[23]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.9546, 方向一致=0.8 |
| `ulist239.f63` | `sina[21]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.9535, 方向一致=0.8 |
| `ulist239.f63` | `sina[20]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.9349, 方向一致=0.8 |
| `ulist239.f63` | `sina[1]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.944, 方向一致=0.8 |
| `ulist239.f63` | `sina[19]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.9641, 方向一致=0.8 |
| `ulist239.f63` | `sina[17]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.9563, 方向一致=0.8 |
| `ulist239.f63` | `sina[15]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.9565, 方向一致=0.8 |
| `ulist239.f63` | `sina[13]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.9578, 方向一致=0.8 |
| `ulist239.f63` | `sina[11]` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | sina, ulist239 | 逐股相关=0.955, 方向一致=0.8 |
| `ulist239.f63` | `fuyao.snapshot.volume` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | fuyao, ulist239 | Pearson=0.3159, Spearman=0.671, LOO稳号=True |
| `ulist239.f63` | `fuyao.snapshot.turnover` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | fuyao, ulist239 | Pearson=0.9098, Spearman=0.9585, LOO稳号=True |
| `ulist239.f63` | `fuyao.snapshot.prev_price` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | fuyao, ulist239 | 逐股相关=0.9257, 方向一致=0.85 |
| `ulist239.f63` | `fuyao.snapshot.open_price` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | fuyao, ulist239 | 逐股相关=0.944, 方向一致=0.8 |
| `ulist239.f63` | `fuyao.snapshot.low_price` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | fuyao, ulist239 | 逐股相关=0.9438, 方向一致=0.8 |
| `ulist239.f63` | `fuyao.snapshot.high_price` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | fuyao, ulist239 | 逐股相关=0.9382, 方向一致=0.85 |
| `ulist239.f63` | `ftshare_rest.volume` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | ftshare_rest, ulist239 | Pearson=0.3159, Spearman=0.671, LOO稳号=True |
| `ulist239.f63` | `ftshare_rest.turnover` | robust_correlation | 60 | T:20261110, T:20261117, T:20261118 | ftshare_rest, ulist239 | Pearson=0.9098, Spearman=0.9585, LOO稳号=True |
| `ulist239.f63` | `ftshare_rest.prev_close` | per_stock_time_series | 60 | T:20261110, T:20261117, T:20261118 | ftshare_rest, ulist239 | 逐股相关=0.9257, 方向一致=0.85 |

_仅显示前 100 / 共 150 条。_


## 七、日期与数据质量告警（84）

- 20261017: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261018: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261031: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261101: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261107: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261114: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261119: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 行情窗口交易日 20261111 无对应采集目录；不会用更早交易日补位，需结合其他采集目录的来源日期检查实际覆盖
- 20261110/zhb: 采集状态 partial
- 20261110/kph: 来源有效交易日 20261109 不在本轮行情交易日窗口，快照跳过
- 20261110/tdx_f10: 没有可用记录，快照跳过
- 20261110/tdx_f10_more: 没有可用记录，快照跳过
- 20261110/zhb: 来源状态为 partial，样本按部分快照参与
- 20261110/zhb: 来源有效交易日 20261109 不在本轮行情交易日窗口，快照跳过
- 20261112/zhb: 采集状态 partial
- 20261112/push2: 采集状态 failed
- 20261112/em_kline_f61: 采集状态 partial
- 20261112/em_fund_flow: 采集状态 partial
- 20261112/ulist239: 采集状态 failed
- 20261112/clist: 采集状态 partial
- 20261112/slist: 采集状态 failed
- 20261112/clist: 来源状态为 partial，样本按部分快照参与
- 20261112/clist: 没有可用记录，快照跳过
- 20261112/em_fund_flow: 来源状态为 partial，样本按部分快照参与
- 20261112/em_fund_flow: 没有可用记录，快照跳过
- 20261112/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20261112/em_kline_f61: 没有可用记录，快照跳过
- 20261112/push2: 来源状态为 failed，快照跳过
- 20261112/slist: 来源状态为 failed，快照跳过
- 20261112/tdx_f10: 没有可用记录，快照跳过
- 20261112/tdx_f10_more: 没有可用记录，快照跳过
- 20261112/ulist239: 来源状态为 failed，快照跳过
- 20261112/zhb: 来源状态为 partial，样本按部分快照参与
- 20261116/push2: 采集状态 failed
- 20261116/em_kline_f61: 采集状态 partial
- 20261116/em_fund_flow: 采集状态 partial
- 20261116/ulist239: 采集状态 failed
- 20261116/clist: 采集状态 partial
- 20261116/slist: 采集状态 failed
- 20261116/clist: 来源状态为 partial，样本按部分快照参与
- 20261116/clist: 没有可用记录，快照跳过
- 20261116/em_fund_flow: 来源状态为 partial，样本按部分快照参与
- 20261116/em_fund_flow: 没有可用记录，快照跳过
- 20261116/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20261116/em_kline_f61: 没有可用记录，快照跳过
- 20261116/push2: 来源状态为 failed，快照跳过
- 20261116/slist: 来源状态为 failed，快照跳过
- 20261116/tdx_f10: 没有可用记录，快照跳过
- 20261116/tdx_f10_more: 没有可用记录，快照跳过
- 20261116/ulist239: 来源状态为 failed，快照跳过
- 20261117/tdx_f10: 没有可用记录，快照跳过
- 20261117/tdx_f10_more: 没有可用记录，快照跳过
- 20261118/tdx_f10: 没有可用记录，快照跳过
- 20261118/tdx_f10_more: 没有可用记录，快照跳过
- 日常碰撞排除来源: ftshare=FTShare private hosted MCP
- 20261110/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1794315883118，response_timestamp_date='2026-11-10'（仅响应组装时间，不作为数据日期），记录数=20
- 20261112/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1794496820051，response_timestamp_date='2026-11-12'（仅响应组装时间，不作为数据日期），记录数=20
- 20261116/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1794835664138，response_timestamp_date='2026-11-16'（仅响应组装时间，不作为数据日期），记录数=20
- 20261117/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1794901089674，response_timestamp_date='2026-11-17'（仅响应组装时间，不作为数据日期），记录数=20
- 20261118/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1794992253927，response_timestamp_date='2026-11-18'（仅响应组装时间，不作为数据日期），记录数=20
- 20261112/kph: KPH 历史碰撞要求 pagination.complete=true；旧样本缺少完整分页证明，已排除
- 折叠 35820 条重复字段样本，按快照质量择优；示例: market_sources.code/603278/T:20261110, market_sources.name/603278/T:20261110, market_sources.code/301510/T:20261110, market_sources.name/301510/T:20261110, market_sources.market/301510/T:20261110, market_sources.time/301510/T:20261110, market_sources.change_pct/301510/T:20261110, market_sources.price/301510/T:20261110, market_sources.change_type/301510/T:20261110, market_sources.date/301510/T:20261110
- 20261110/cninfo: 77 条事件记录缺少可解析的自然日，已跳过
- 20261112/cninfo: 66 条事件记录缺少可解析的自然日，已跳过
- 20261116/cninfo: 66 条事件记录缺少可解析的自然日，已跳过
- 20261117/cninfo: 67 条事件记录缺少可解析的自然日，已跳过
- 20261118/cninfo: 67 条事件记录缺少可解析的自然日，已跳过
- 20261110/etf: 923 条市场记录不在所选交易日窗口内，已跳过
- 64 条 verified 源字段来源未确认独立性，作为已知字段跳过重解但不作锚
- 31 条官方契约语义锚可参与对撞；底层来源独立性未确认，强候选标为 L1-C
- 70 条 verified 源字段映射到重复运行时身份；相关运行时路径已退出破解目标，但身份消歧前不作锚
- 61 条 ZHB full-view 路径的所有注册 owner 均已 verified/disproved，但归属不唯一；不作锚，且不作为未知目标重复破解
- 160 条 verified 源字段元数据未达锚点条件（含义冲突 10 条、缺义/占位 159 条、单位冲突 2 条）；已退出破解目标，但保留在元数据补全队列且不作碰撞锚
- 东财-push2(stock/get) 行时间戳日期见证：确认 60 行，日期冲突 0 行，无效时间戳 0 行
- 东财-ulist239(np/get) 行时间戳日期见证：确认 60 行，日期冲突 0 行，无效时间戳 0 行
- 跨源值日期见证 tdx.quote_raw.bid1_vol <- tencent[10]: 100/100 精确，94/94 非零精确，5 个交易日满足日阈值；未达到门槛
- 跨源值日期见证 tdx.quote_raw.ask1_vol <- tencent[20]: 100/100 精确，98/98 非零精确，5 个交易日满足日阈值；未达到门槛
- 来源关系审阅队列: 21 组有同完整路径的来源对；仅作观测等价/互补线索，不自动认定同源或停采
- 字段时效分类: daily_market=37, intraday_sensitive=23, periodic_or_event=3, slow_changing=5, static_reference=7, unclassified=1225；未分类字段按来源日期严格门控
- 对撞模式：verified_anchor_only；待破解字段=107，verified 锚资格字段=1484，verified 目标排除身份=1703，可用独立锚=1396，官方契约字段=459，L1-C 契约锚=31，right 字段=571
- 220 条本地字段覆盖快照的 registry 状态已过期；候选展示已按当前逐源注册表状态校正。
- 跳过同一来源家族字段对：4372
- 跳过来源独立性未确认的字段对：38766
- 官方契约锚参与字段对撞 1831 对；底层来源独立性未确认，强匹配单列 L1-C

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

策略状态：`ok`；逐源分类字段 75，保守默认未分类字段 1225。L1/L1-C 日期证据：来源日期已确认 0 条，跨源值见证推断 0 条，仅语义证据且日期未确认 0 条，其他日期未确认 0 条。

| 日期见证关系 | 结果 | 交易日 | 精确样本 | 非零精确样本 | 不同非零值 | 证据 SHA-256 |
|:--|:--|--:|--:|--:|--:|:--|
| `tdx.quote_raw.ask1_vol <- tencent[20]` | thresholds_not_met | 5 | 100/100 | 98/98 | 86 | `9f488224d9a95673bf751451c47a3fd1ae05090b51cf090dc014d66818252d69` |
| `tdx.quote_raw.bid1_vol <- tencent[10]` | thresholds_not_met | 5 | 100/100 | 94/94 | 77 | `9f488224d9a95673bf751451c47a3fd1ae05090b51cf090dc014d66818252d69` |

_本轮 L1/L1-C 没有仅凭静态或缓变字段、且来源日期未确认的关系。_

## 来源字段覆盖与碰撞参与

_窗口字段值样本是经日期筛选、重复折叠和快照择优后载入的非空值；右侧比较次数另受字段类型及来源规则筛选。官方契约字段须有逐字段审定证据，契约语义本身不证明底层数据来源独立。_

| 来源 | 已确认字段 | 契约已确认 | 契约锚 | 独立锚 | L1-C 锚 | 窗口字段 / 字段值样本 / 交易日 |
|:--|--:|--:|--:|--:|--:|--:|
| axdata | 34 | 0 | 0 | 0 | 0 | 34 / 2683 / 5 |
| clist | 20 | 0 | 0 | 20 | 0 | 33 / 21501 / 3 |
| cls | 6 | 1 | 1 | 6 | 0 | 5 / 750 / 0 |
| cninfo | 6 | 0 | 0 | 6 | 0 | 0 / 0 / 0 |
| datacenter | 46 | 5 | 5 | 46 | 0 | 0 / 0 / 0 |
| eltdx | 255 | 181 | 181 | 255 | 0 | 113 / 5440 / 5 |
| em_fund_flow | 15 | 0 | 0 | 15 | 0 | 15 / 900 / 3 |
| em_hot | 39 | 0 | 0 | 39 | 0 | 0 / 0 / 0 |
| em_kline_f61 | 12 | 1 | 1 | 12 | 0 | 2 / 120 / 3 |
| etf | 5 | 0 | 0 | 5 | 0 | 14 / 53062 / 6 |
| event_dc | 0 | 0 | 0 | 0 | 0 | 148 / 154317 / 5 |
| exchange | 5 | 0 | 0 | 5 | 0 | 0 / 0 / 0 |
| ftshare | 6 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| ftshare_rest | 32 | 31 | 31 | 0 | 31 | 32 / 3175 / 5 |
| fuyao | 117 | 99 | 99 | 117 | 0 | 20 / 2000 / 5 |
| kph | 12 | 0 | 0 | 12 | 0 | 15 / 1545 / 3 |
| kpl | 19 | 0 | 0 | 19 | 0 | 28 / 8160 / 5 |
| market_sources | 16 | 0 | 0 | 0 | 0 | 70 / 30692 / 5 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 2 / 62 / 0 |
| push2 | 69 | 0 | 0 | 69 | 0 | 114 / 6840 / 3 |
| push2ex | 35 | 1 | 1 | 35 | 0 | 16 / 5664 / 5 |
| reports | 46 | 0 | 0 | 46 | 0 | 49 / 49 / 0 |
| research_sina | 0 | 0 | 0 | 0 | 0 | 6 / 780 / 0 |
| sina | 33 | 0 | 0 | 33 | 0 | 39 / 3450 / 5 |
| sina_extended | 6 | 3 | 3 | 6 | 0 | 4 / 400 / 5 |
| slist | 5 | 0 | 0 | 5 | 0 | 1 / 60 / 3 |
| sse_e_interaction | 0 | 0 | 0 | 0 | 0 | 8 / 232 / 0 |
| st_list | 0 | 0 | 0 | 0 | 0 | 6 / 7670 / 5 |
| tdx | 241 | 107 | 107 | 241 | 0 | 58 / 6400 / 5 |
| tencent | 84 | 0 | 0 | 84 | 0 | 88 / 8790 / 5 |
| ulist239 | 74 | 4 | 4 | 74 | 0 | 240 / 14400 / 3 |
| zhb | 246 | 26 | 26 | 246 | 0 | 128 / 11399 / 5 |

| 来源 | 破解目标 | 比较字段 | 作目标比较 | 作右侧比较 | L1-C 锚比较 | L1 / L1-C / L4 关系 | 方法候选涉及 |
|:--|--:|--:|--:|--:|--:|--:|--:|
| axdata | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| clist | 10 | 17 | 3356 | 102 | 0 | 0 / 0 / 0 | 0 |
| cls | 1 | 1 | 32 | 21 | 0 | 0 / 0 / 0 | 0 |
| cninfo | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| datacenter | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| eltdx | 1 | 68 | 27 | 1400 | 0 | 0 / 0 / 0 | 26 |
| em_fund_flow | 0 | 13 | 0 | 78 | 0 | 0 / 0 / 0 | 0 |
| em_hot | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| em_kline_f61 | 0 | 1 | 0 | 6 | 0 | 0 / 0 / 0 | 0 |
| etf | 4 | 0 | 1136 | 0 | 0 | 0 / 0 / 0 | 0 |
| event_dc | 61 | 0 | 1235 | 0 | 0 | 0 / 0 / 0 | 0 |
| exchange | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare_rest | 0 | 25 | 0 | 1831 | 1831 | 0 / 0 / 0 | 13 |
| fuyao | 0 | 14 | 0 | 294 | 0 | 0 / 0 / 0 | 6 |
| kph | 1 | 9 | 528 | 175 | 0 | 0 / 0 / 2 | 2 |
| kpl | 3 | 19 | 575 | 500 | 0 | 0 / 0 / 3 | 1 |
| market_sources | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| news_wscn_cctv | 1 | 0 | 2 | 0 | 0 | 0 / 0 / 0 | 0 |
| push2 | 4 | 64 | 68 | 390 | 0 | 0 / 0 / 0 | 0 |
| push2ex | 0 | 12 | 0 | 72 | 0 | 0 / 0 / 1 | 1 |
| reports | 0 | 5 | 0 | 45 | 0 | 0 / 0 / 0 | 0 |
| research_sina | 2 | 0 | 534 | 0 | 0 | 0 / 0 / 0 | 0 |
| sina | 1 | 32 | 504 | 579 | 0 | 0 / 0 / 0 | 19 |
| sina_extended | 0 | 3 | 0 | 57 | 0 | 0 / 0 / 0 | 1 |
| slist | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| sse_e_interaction | 6 | 0 | 33 | 0 | 0 | 0 / 0 / 0 | 0 |
| st_list | 3 | 0 | 48 | 0 | 0 | 0 / 0 / 0 | 0 |
| tdx | 0 | 51 | 0 | 1197 | 0 | 0 / 0 / 0 | 25 |
| tencent | 2 | 80 | 50 | 1624 | 0 | 0 / 0 / 0 | 34 |
| ulist239 | 7 | 70 | 2243 | 432 | 0 | 0 / 0 / 0 | 148 |
| zhb | 0 | 75 | 0 | 1568 | 0 | 0 / 0 / 0 | 24 |

## 来源/接口重叠审阅（不自动停采）

此处按**完整规范路径**和来源实际日期对齐比较已采值，单独呈现同家族、不同仓库或血缘未明来源的重叠。数值一致只说明观测范围内的路径等价候选，不证明底层提供方相同、字段语义相同或整条路由可删除。只有接口字段覆盖、唯一字段、备用关系和复验策略均核实后，才可调整采集路由。
来源对 21 组；保留详情 21 组；路径身份歧义 5 项；采集自动停用：否。

| 来源 A / 仓库 | 来源 B / 仓库 | 血缘关系 | 观测关系 | 共同路径 | 强匹配路径 | 失配路径/失配样本/近似样本/未对齐样本 | A/B 独有路径 | 强匹配完整路径样例 |
|:--|:--|:--|:--|--:|--:|--:|:--|:--|
| `sina` / https://github.com/shidenggui/easyquotation | `tencent` / https://github.com/shidenggui/easyquotation | different_confirmed_provider_families | observed_value_differences | 39 | 1 | 38/3265/836/0 | 0/49 | `[3]` |
| `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | provider_relation_unconfirmed | insufficient_aligned_evidence | 16 | 0 | 0/0/0/232 | 12/54 | — |
| `em_fund_flow` / https://github.com/fleetinglife/levistock | `ulist239` / https://github.com/fleetinglife/levistock | same_confirmed_provider_family | insufficient_aligned_evidence | 15 | 0 | 0/0/0/900 | 0/225 | — |
| `em_fund_flow` / https://github.com/fleetinglife/levistock | `push2` / https://github.com/fleetinglife/levistock | same_confirmed_provider_family | insufficient_aligned_evidence | 15 | 0 | 0/0/0/900 | 0/99 | — |
| `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `push2ex` / https://github.com/fleetinglife/levistock | provider_relation_unconfirmed | insufficient_aligned_evidence | 7 | 0 | 0/0/0/1626 | 63/9 | — |
| `push2ex` / https://github.com/fleetinglife/levistock | `tdx` / https://github.com/yanwei99521/easy-tdx, https://github.com/electkismet/eltdx | different_confirmed_provider_families | insufficient_aligned_evidence | 3 | 0 | 0/0/0/15 | 13/55 | — |
| `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `tdx` / https://github.com/yanwei99521/easy-tdx, https://github.com/electkismet/eltdx | provider_relation_unconfirmed | insufficient_aligned_evidence | 3 | 0 | 0/0/0/25 | 67/55 | — |
| `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `push2ex` / https://github.com/fleetinglife/levistock | different_confirmed_provider_families | insufficient_aligned_evidence | 3 | 0 | 0/0/0/480 | 25/13 | — |
| `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | `push2ex` / https://github.com/fleetinglife/levistock | different_confirmed_provider_families | insufficient_aligned_evidence | 3 | 0 | 0/0/0/309 | 12/13 | — |
| `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | provider_relation_unconfirmed | insufficient_aligned_evidence | 3 | 0 | 0/0/0/233 | 12/67 | — |
| `ftshare_rest` / — | `tdx` / https://github.com/yanwei99521/easy-tdx, https://github.com/electkismet/eltdx | provider_relation_unconfirmed | insufficient_aligned_evidence | 3 | 0 | 0/0/0/300 | 29/55 | — |
| `ftshare_rest` / — | `push2ex` / https://github.com/fleetinglife/levistock | provider_relation_unconfirmed | insufficient_aligned_evidence | 2 | 0 | 0/0/0/10 | 30/14 | — |
| `ftshare_rest` / — | `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | provider_relation_unconfirmed | insufficient_aligned_evidence | 2 | 0 | 0/0/0/14 | 30/68 | — |
| `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `zhb` / https://github.com/yanwei99521/easy-tdx, https://github.com/yanwei99521/easy-tdx | provider_relation_unconfirmed | insufficient_aligned_evidence | 1 | 0 | 0/0/0/3 | 69/127 | — |
| `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | `sina_extended` / https://github.com/mpquant/Ashare | different_confirmed_provider_families | insufficient_aligned_evidence | 1 | 0 | 0/0/0/1 | 14/3 | — |
| `ftshare_rest` / — | `sina_extended` / https://github.com/mpquant/Ashare | provider_relation_unconfirmed | insufficient_aligned_evidence | 1 | 0 | 0/0/0/100 | 31/3 | — |
| `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | different_confirmed_provider_families | observed_value_differences | 3 | 0 | 1/4/0/0 | 12/25 | — |
| `ftshare_rest` / — | `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | provider_relation_unconfirmed | observed_value_differences | 2 | 0 | 1/2/0/0 | 30/26 | — |
| `ftshare_rest` / — | `zhb` / https://github.com/yanwei99521/easy-tdx, https://github.com/yanwei99521/easy-tdx | provider_relation_unconfirmed | observed_value_differences | 1 | 0 | 1/36/0/0 | 31/127 | — |
| `ftshare_rest` / — | `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | provider_relation_unconfirmed | observed_value_differences | 4 | 0 | 3/3/1/0 | 28/11 | — |
| `push2` / https://github.com/fleetinglife/levistock | `ulist239` / https://github.com/fleetinglife/levistock | same_confirmed_provider_family | observed_value_differences | 113 | 0 | 107/6332/1/120 | 1/127 | — |

强匹配路径不得有值失配、未对齐样本或低信息常量，并达到每条路径至少 5 个信息样本、3 个不同样本日期、3 只证券；宽松舍入窗口只列为独立近似样本数，不计强匹配；该筛选只产生路由复核候选，不取代现有接口专用退出和复验规则。

## AxData 每日接口核验

> 此处汇总采集目录已保存的本地证据，不发起网络请求、不改变注册表状态；AxData 是多源框架，不作为独立字段锚。

### AxData

窗口内有 6 个唯一数据日的轮验记录；重复目录合并 0 条。
静态接口队列：257 个接口，3343 个字段出现项，低于 E3 的字段出现项 3343；当前主动探针白名单 `tencent_realtime_snapshot`。
静态候选策略：static review only until route, parameters, date basis, and request safety are approved。

| 数据日 | 轮验状态 | 探针状态 / 请求数 | 来源身份状态 | 短线配对 | KPH/KPL 配对 | 证据文件 |
|:--|:--|:--|:--|--:|--:|:--|
| 20261110 | already_recorded | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261112 | already_recorded | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261113 | not_eligible | not_run / 0 (字段相同/不同 0/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing | — | — | meta_summary |
| 20261116 | already_recorded | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261117 | already_recorded | sampled / 1 (字段相同/不同 0/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | 34 | full |
| 20261118 | already_recorded | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |

被动逐字段比较中的差异计数（跨本窗口唯一数据日累加，不含原始值）：

| 比较路径 | 相同 | 不同 | 缺失/双方空值 |
|:--|--:|--:|--:|
| `axdata_shortline_vs_eltdx:alignment_status` | 0 | 100 | 0 |
| `axdata_shortline_vs_eltdx:beta_60d` | 0 | 100 | 0 |
| `axdata_shortline_vs_eltdx:code` | 0 | 100 | 0 |
| `axdata_shortline_vs_eltdx:full_code` | 0 | 100 | 0 |
| `axdata_shortline_vs_eltdx:instrument_id` | 0 | 100 | 0 |
| `axdata_shortline_vs_eltdx:limit_status` | 0 | 100 | 0 |
| `axdata_shortline_vs_eltdx:market_id` | 0 | 100 | 0 |
| `axdata_shortline_vs_eltdx:opening_rush` | 0 | 100 | 0 |
| `axdata_shortline_vs_eltdx:pe_ttm` | 0 | 100 | 0 |
| `axdata_shortline_vs_eltdx:previous_trade_date` | 0 | 100 | 0 |
| `axdata_shortline_vs_eltdx:symbol` | 0 | 100 | 0 |
| `axdata_shortline_vs_eltdx:target_trade_date` | 0 | 100 | 0 |
| `axdata_shortline_vs_eltdx:tdx_code` | 0 | 100 | 0 |
| `axdata_shortline_vs_eltdx:open_amount` | 20 | 80 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_hand` | 20 | 80 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_ratio` | 20 | 80 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_amount_ratio` | 24 | 76 | 0 |
| `axdata_shortline_vs_eltdx:auction_prev_volume_ratio` | 25 | 73 | 2 |
| `axdata_shortline_vs_eltdx:open_turnover_z` | 49 | 51 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_seal_ratio` | 2 | 8 | 90 |
| `axdata_shortline_vs_eltdx:ladder_level` | 0 | 2 | 98 |
| `axdata_shortline_vs_eltdx:limit_board_text` | 5 | 2 | 93 |

## 字母字段名语义提示（仅候选）

窗口内观察到 94 条需审阅的字母字段路径：含词义线索 22 条，仅拆词 72 条。
完整逐条记录保存在碰撞 JSON；名称线索清单：`docs/field_verification/20261014/20261014_alphabetic_field_name_inventory.csv`。
> 拼音、英文、缩写和混合拆词只用于检索候选；必须结合原始值、接口定义和独立来源复核，不得据此定案或改写主字典。

| 逐源字段路径 | 状态/审阅范围 | 名称形式与拆词 | 词义线索（非释义） | 样本日期 |
|:--|:--|:--|:--|:--|
| `市场源(market_sources)::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `东财-push2ex::code` | verified / verified_metadata_gap | recognized_english_word_candidate: code | 代码 | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `东财-push2ex::name` | verified / verified_metadata_gap | recognized_english_word_candidate: name | 名称 | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `市场源(market_sources)::limit_count` | verified / verified_metadata_gap | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261110, T:20261112, T:20261116, T:20261118 |
| `市场源(market_sources)::plate_limit_up_count` | verified / verified_metadata_gap | snake_case_or_mixed: plate limit up count | 涨跌停限制 + 上/涨 + 数量/次数 | T:20261110, T:20261112, T:20261116, T:20261118 |
| `TDX(双命名源)::changqifuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: changqifuzhai | 长期负债 | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `TDX(双命名源)::cunhuo` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: cunhuo | 存货 | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `TDX(双命名源)::jingyingxianjinliu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingyingxianjinliu | 经营现金流 | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `TDX(双命名源)::jingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingzichan | 净资产 | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `TDX(双命名源)::liudongfuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: liudongfuzhai | 流动负债 | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `TDX(双命名源)::meigujingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: meigujingzichan | 每股净资产 | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `TDX(双命名源)::yingshouzhangkuan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: yingshouzhangkuan | 应收账款 | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `TDX(双命名源)::zibengongjijin` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zibengongjijin | 资本公积金 | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `TDX(双命名源)::zongzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongzichan | 总资产 | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `同花顺-fuyao::snapshot.open_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot open price | 开盘 + 价格 | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `reports::count` | verified / verified_metadata_gap | recognized_english_word_candidate: count | 数量/次数 | C:20261113 |
| `reports::lastEmRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Code | 最近/上一期 + 代码 | C:20261113 |
| `reports::lastEmRatingName` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Name | 最近/上一期 + 名称 | C:20261113 |
| `reports::lastEmRatingValue` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Value | 最近/上一期 + 值 | C:20261113 |
| `reports::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | C:20261113 |
| `reports::predictLastYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Eps | 最近/上一期 + 每股收益 | C:20261113 |
| `reports::predictLastYearPe` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Pe | 最近/上一期 + 市盈率 | C:20261113 |
| `开盘啦(kpl_limit_up_detail)::raw_columns.col_19` | verified / verified_metadata_gap | runtime_tokenization_only: col 19 | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `市场源(market_sources)::one_word` | unverified / unverified_semantics | snake_case_or_mixed: one word | — | T:20261110, T:20261112, T:20261116, T:20261118 |
| `市场源(market_sources)::plate_amount` | verified / verified_metadata_gap | snake_case_or_mixed: plate amount | — | T:20261110, T:20261112, T:20261116, T:20261118 |
| `市场源(market_sources)::plate_code` | verified / verified_metadata_gap | snake_case_or_mixed: plate code | — | T:20261110, T:20261112, T:20261116, T:20261118 |
| `市场源(market_sources)::plate_name` | verified / verified_metadata_gap | snake_case_or_mixed: plate name | — | T:20261110, T:20261112, T:20261116, T:20261118 |
| `市场源(market_sources)::popular` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: popular | — | T:20261110, T:20261112, T:20261116, T:20261118 |
| `财联社(cls)::content` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: content | — | C:20261116, C:20261117, C:20261118 |
| `财联社(cls)::level` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: level | — | C:20261116, C:20261117, C:20261118 |
| `财联社(cls)::reading_num` | verified / verified_metadata_gap | snake_case_or_mixed: reading num | — | C:20261116, C:20261117, C:20261118 |
| `财联社(cls)::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20261116, C:20261117, C:20261118 |
| `开盘红::industry_limit_up_count` | unverified / unverified_semantics | runtime_tokenization_only: industry limit up count | — | T:20261116, T:20261117, T:20261118 |
| `FTShare REST::amplitude` | verified / verified_metadata_gap | runtime_tokenization_only: amplitude | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `FTShare REST::avg` | verified / verified_metadata_gap | runtime_tokenization_only: avg | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `FTShare REST::bid_ask_ratio` | verified / verified_metadata_gap | runtime_tokenization_only: bid ask ratio | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `FTShare REST::board` | verified / verified_metadata_gap | runtime_tokenization_only: board | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `FTShare REST::listing_date` | verified / verified_metadata_gap | runtime_tokenization_only: listing date | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `FTShare REST::name` | verified / verified_metadata_gap | runtime_tokenization_only: name | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `FTShare REST::st` | verified / verified_metadata_gap | runtime_tokenization_only: st | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `FTShare REST::status` | verified / verified_metadata_gap | runtime_tokenization_only: status | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `FTShare REST::symbol` | verified / verified_metadata_gap | runtime_tokenization_only: symbol | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `FTShare REST::symbol_id` | verified / verified_metadata_gap | runtime_tokenization_only: symbol id | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `FTShare REST::turnover_rate` | verified / verified_metadata_gap | runtime_tokenization_only: turnover rate | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `ZHB-tdxstat::stat.unknown_2` | verified / verified_metadata_gap | snake_case_or_mixed: stat unknown 2 | — | T:20261111, T:20261113, T:20261116, T:20261117, T:20261118 |
| `ZHB-tdxstat::stat.unknown_26` | verified / verified_metadata_gap | snake_case_or_mixed: stat unknown 26 | — | T:20261111, T:20261113, T:20261116, T:20261117, T:20261118 |
| `同花顺-fuyao::snapshot.prev_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot prev price | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `市场源(market_sources)::big_order_300w_net` | unverified / unverified_semantics | runtime_tokenization_only: big order 300 w net | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `市场源(market_sources)::institution_add` | unverified / unverified_semantics | runtime_tokenization_only: institution add | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `市场源(market_sources)::main_inflow` | unverified / unverified_semantics | snake_case_or_mixed: main inflow | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `市场源(market_sources)::pe_next` | unverified / unverified_semantics | runtime_tokenization_only: pe next | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `市场源(market_sources)::pe_now` | unverified / unverified_semantics | runtime_tokenization_only: pe now | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `市场源(market_sources)::strength` | unverified / unverified_semantics | runtime_tokenization_only: strength | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `市场源(market_sources)::total_value` | unverified / unverified_semantics | runtime_tokenization_only: total value | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `FTShare REST::pe_ttm` | verified / verified_metadata_gap | runtime_tokenization_only: pe ttm | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `市场源(market_sources)::rank` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: rank | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `TDX-eltdx(适配层)::adjust_mode` | verified / verified_metadata_gap | snake_case_or_mixed: adjust mode | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `TDX-eltdx(适配层)::anchor_date_raw` | verified / verified_metadata_gap | snake_case_or_mixed: anchor date raw | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `TDX-eltdx(适配层)::category` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: category | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `TDX-eltdx(适配层)::period_name` | verified / verified_metadata_gap | snake_case_or_mixed: period name | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `TDX-eltdx(适配层)::raw_payload` | unverified / unverified_semantics | snake_case_or_mixed: raw payload | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `TDX-eltdx(适配层)::sort_by` | unverified / unverified_semantics | snake_case_or_mixed: sort by | — | T:20261110, T:20261112, T:20261116, T:20261117, T:20261118 |
| `reports::attachType` | verified / verified_metadata_gap | camel_case_or_mixed: attach Type | — | C:20261113 |
| `reports::column` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: column | — | C:20261113 |
| `reports::emIndustryCode` | unverified / unverified_semantics | camel_case_or_mixed: em Industry Code | — | C:20261113 |
| `reports::emRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: em Rating Code | — | C:20261113 |
| `reports::emRatingName` | verified / verified_metadata_gap | camel_case_or_mixed: em Rating Name | — | C:20261113 |
| `reports::emRatingValue` | verified / verified_metadata_gap | camel_case_or_mixed: em Rating Value | — | C:20261113 |
| `reports::encodeUrl` | conflict / unverified_semantics | camel_case_or_mixed: encode Url | — | C:20261113 |
| `reports::industryCode` | verified / verified_metadata_gap | camel_case_or_mixed: industry Code | — | C:20261113 |
| `reports::industryName` | verified / verified_metadata_gap | camel_case_or_mixed: industry Name | — | C:20261113 |
| `reports::indvInduCode` | verified / verified_metadata_gap | camel_case_or_mixed: indv Indu Code | — | C:20261113 |
| `reports::indvInduName` | verified / verified_metadata_gap | camel_case_or_mixed: indv Indu Name | — | C:20261113 |
| `reports::indvIsNew` | verified / verified_metadata_gap | camel_case_or_mixed: indv Is New | — | C:20261113 |
| `reports::infoCode` | verified / verified_metadata_gap | camel_case_or_mixed: info Code | — | C:20261113 |
| `reports::newPurchaseDate` | verified / verified_metadata_gap | camel_case_or_mixed: new Purchase Date | — | C:20261113 |
| `reports::orgCode` | verified / verified_metadata_gap | camel_case_or_mixed: org Code | — | C:20261113 |
| `reports::orgName` | verified / verified_metadata_gap | camel_case_or_mixed: org Name | — | C:20261113 |
| `reports::orgSName` | verified / verified_metadata_gap | camel_case_or_mixed: org S Name | — | C:20261113 |
| `reports::orgType` | unverified / unverified_semantics | camel_case_or_mixed: org Type | — | C:20261113 |
| `reports::predictNextTwoYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Next Two Year Eps | — | C:20261113 |
| `reports::predictNextYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Next Year Eps | — | C:20261113 |
| `reports::predictThisYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict This Year Eps | — | C:20261113 |
| `reports::publishDate` | verified / verified_metadata_gap | camel_case_or_mixed: publish Date | — | C:20261113 |
| `reports::ratingChange` | verified / verified_metadata_gap | camel_case_or_mixed: rating Change | — | C:20261113 |
| `reports::reportType` | verified / verified_metadata_gap | camel_case_or_mixed: report Type | — | C:20261113 |
| `reports::researcher` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: researcher | — | C:20261113 |
| `reports::sRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: s Rating Code | — | C:20261113 |
| `reports::sRatingName` | verified / verified_metadata_gap | camel_case_or_mixed: s Rating Name | — | C:20261113 |
| `reports::stockCode` | verified / verified_metadata_gap | camel_case_or_mixed: stock Code | — | C:20261113 |
| `reports::stockName` | verified / verified_metadata_gap | camel_case_or_mixed: stock Name | — | C:20261113 |
| `reports::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20261113 |

## 探索候选持续跟踪

研究台账：`collision_research_state.json.gz`；累计历史跟踪候选对 4287，本报告候选对 152，历史复现 73，新发现 0。
台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，不会自动改变字段状态、碰撞锚或主字典。新报告只将 `actionable_L1`、L4 和主动方法候选写入待研究队列；已登记关系的复验单独展示，历史跟踪记录不会被删除。

## 候选覆盖、公式与下一步采样

本节用于定位证据缺口和安排后续取样。相关性、公式与样本优先级均为探索候选；不会改变 L1/L1-U 门槛、来源独立性或主字典。

- 未知目标 107 个；其中有方法候选 5 个、无候选 102 个；多候选目标 3 个；有官方契约锚强匹配 0 个、诊断命中 0 个，日期值候选 0 个。
- 方法候选生成 150 条；全局详细项保留 150/500，另按目标字段保留 0 条；完整明细 150 条在 JSON `method_candidate_inventory`；未归档明细 0 条。
- 字段覆盖详情：available；覆盖身份 1688，读取 6 份本地索引。

### 优先处理字段

| 未知字段 | 核验入口 | 当前诊断 | 官方锚强/诊断 | 独立对比/候选数 | 独立锚家族/本源日期 | 建议复核股票 | 最强候选线索 |
|:--|:--|:--|--:|--:|:--|:--|:--|
| `ulist239.f63` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 348 / 143 | 7 家族 / 348 对 / 本源 0 日 | 002242 (0.091613) | tencent[71] (robust_correlation,per_stock_time_series); ftshare_rest.change_rate_day60 (robust_correlation,per_stock_time_series) |
| `ulist239.f99` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 348 / 3 | 7 家族 / 348 对 / 本源 0 日 | 000678 (1.285719) | tencent[70] (per_stock_time_series); tencent[67] (per_stock_time_series) |
| `kph.industry_limit_up_count` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 505 / 2 | 7 家族 / 505 对 / 本源 4 日 | no_shared_stock_holdout | kpl.raw_columns.col_20 (robust_correlation,affine_formula); push2ex.limit_count (semantic_label) |
| `ulist239.f111` | 检查官方锚对撞 | 单候选，需外部证据 | 0/0 | 348 / 1 | 7 家族 / 348 对 / 本源 0 日 | — | zhb.tipinfo.hg_amount_yi (robust_correlation) |
| `ulist239.f30` | 检查官方锚对撞 | 单候选，需外部证据 | 0/0 | 348 / 1 | 7 家族 / 348 对 / 本源 0 日 | — | zhb.tipinfo.hg_amount_yi (robust_correlation) |
| `event_dc.ACTUAL_ISSUE_SCALE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.AFTER_ISSUE_PE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.AMPLITUDE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.AVERAGE_PRICE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.BOND_EXPIRE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.CHANGE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.CHANGE_RATE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.CLOSE_PRICE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.COUPON_IR` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.DEC_SUMFINA` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.EACHBALLOT_SHARES` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.EXECUTE_PRICE_HS` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.EXECUTE_PRICE_SH` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.EXECUTE_REASON_HS` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.EXECUTE_REASON_SH` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.FIRST_PER_PREPLACING` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.FIRST_PROFIT` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.INDUSTRY_PE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.INDUSTRY_PE_NEW` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.INITIAL_TRANSFER_PRICE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.IPO_YIELD` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.ISSUE_NUM` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.ISSUE_PRICE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.ISSUE_TYPE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.ISSUE_WAY_EXPLAIN` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.ISSUE_YEAR` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.IS_CONVERT_STOCK` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.IS_RISKWARNING` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.LATELY_PRICE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.LD_AVERAGE_PRICE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.LD_CLOSE_CHANGE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.LD_HIGH_CHANG` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.LD_OPEN_PREMIUM` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.LIMIT_UP_PRICE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.MAIN_BUSINESS` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.MZYQ_PAY_FUND` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.NETSUMFINA` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.OD_HIGH_CHANGE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.ONLINE_GENERAL_AAU` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.ONLINE_GENERAL_LWR` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.OPEN_AVERAGE_PRICE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.OPEN_PRICE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.ORG_TYPE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.PAR_VALUE` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `event_dc.PAYDAYNEW` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |

_此表显示优先级最高的 50 / 共 107 个目标；完整清单见 JSON。_


### 舍入近似数值线索（仅研究，不算 L1/L1-U；0 组）

近似窗口只用于提示复核：需核对双方原始单位、展示精度和来源口径；不得把该命中率当作字段语义结论或注册表写回依据。完整明细在 JSON `candidate_triage.approximate_matches`。

_本轮没有达到近似筛查门槛的关系。_


### 双输入公式候选
本轮未发现通过留出筛选的公式候选；测试组合 20 个。


### 已知映射与已证伪关系的候选校准

- 已登记正向对照：当前窗口有 159 组独立数值关系可评估，156 组被方法候选识别；样本不足 2 组。此计数仅检查方法覆盖，不是准确率。
- 已证伪负向对照：数值关系 0 组，其中仍有方法信号 0 组；这些信号被隔离，不进入普通候选。

### 采集覆盖异常源

- baidu: 20261116, 20261117, 20261118 ({'pending_validation': 5})
- clist: 20261112, 20261116 ({'ok': 3, 'partial': 2})
- em_fund_flow: 20261112, 20261116 ({'ok': 3, 'partial': 2})
- em_hot: 20261116, 20261117, 20261118 ({'context_only': 5})
- em_kline_f61: 20261112, 20261116 ({'ok': 3, 'partial': 2})
- exchange: 20261116, 20261117, 20261118 ({'context_only': 5})
- ftshare: 20261116, 20261117, 20261118 ({'deprecated': 5})
- push2: 20261112, 20261116 ({'failed': 2, 'ok': 3})
- slist: 20261112, 20261116 ({'failed': 2, 'ok': 3})
- ulist239: 20261112, 20261116 ({'failed': 2, 'ok': 3})
- zhb: 20261110, 20261112 ({'ok': 4, 'partial': 2})

## 低信息与日期语义专项队列

恒空、恒零或当前恒定字段不参与普通碰撞；状态表示当前样本没有区分力，新采样出现有效变化后重新纳入。日期形状只代表值可解析为日期，必须查清业务角色，不能拿字段值代替来源 `as_of_date`。
低信息未知路径 152 项，状态分布 `{'constant_zero': 35, 'all_missing_or_blank': 5, 'constant_value': 112}`。

### 等待新信息的字段

| 完整字段路径 | 状态 | 观测/非空/缺失或空白/不同值 | 样本日期数 | 示例值 |
|:--|:--|--:|--:|:--|
| `eltdx.limit_ladder.limit_stat_days` | constant_zero | 1/1/0/1 | 1 | `0` |
| `eltdx.limit_ladder.limit_up_count_in_stat_days` | constant_zero | 1/1/0/1 | 1 | `0` |
| `eltdx.limit_ladder.limit_up_streak_days` | constant_zero | 1/1/0/1 | 1 | `0` |
| `market_sources.request_params.offset` | constant_zero | 1/1/0/1 | 1 | `0` |
| `reports.emIndustryCode` | all_missing_or_blank | 1/0/1/0 | 1 | `` |
| `eltdx.limit_ladder.market_id` | constant_zero | 2/2/0/1 | 2 | `0` |
| `eltdx.raw_payload` | all_missing_or_blank | 5/0/5/0 | 5 | `` |
| `sina[34]` | constant_zero | 10/10/0/1 | 5 | `0.0000` |
| `sina[35]` | constant_zero | 10/10/0/1 | 5 | `0` |
| `event_dc.PREDICT_RAISE_FUNDS` | constant_zero | 35/35/0/1 | 5 | `0` |
| `push2.f123` | constant_zero | 60/60/0/1 | 3 | `0.0` |
| `push2.f124` | constant_zero | 60/60/0/1 | 3 | `0.0` |
| `push2.f125` | constant_zero | 60/60/0/1 | 3 | `0.0` |
| `push2.f134` | constant_zero | 60/60/0/1 | 3 | `0` |
| `ulist239.f120` | constant_zero | 60/60/0/1 | 3 | `0` |
| `ulist239.f125` | constant_zero | 60/60/0/1 | 3 | `0` |
| `ulist239.f126` | constant_zero | 60/60/0/1 | 3 | `0` |
| `ulist239.f137` | constant_zero | 60/60/0/1 | 3 | `0.0` |
| `ulist239.f138` | constant_zero | 60/60/0/1 | 3 | `0.0` |
| `ulist239.f194` | constant_zero | 60/60/0/1 | 3 | `0` |
| `ulist239.f216` | constant_zero | 60/60/0/1 | 3 | `0` |
| `ulist239.f223` | constant_zero | 60/60/0/1 | 3 | `0` |
| `event_dc.CURRENT_ONEWORD_NUM` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.IS_1YEAR` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.IS_1YEAR_APPLY` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.IS_BALLOT_NUM` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.IS_BEIJING` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.IS_CALENDAR_DATA` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.IS_PROFIT` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.IS_REGISTRATION` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.IS_REGISTRATION_NEW` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.IS_UNOPEN` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.OPEN_CHANGERATE` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.PREDICT_ISSUE_PRICE` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.PREDICT_ISSUE_PRICE2` | constant_zero | 100/100/0/1 | 5 | `0` |
| `sina[32]` | constant_zero | 100/100/0/1 | 5 | `00` |
| `tencent[29]` | all_missing_or_blank | 100/0/100/0 | 5 | `` |
| `tencent[55]` | all_missing_or_blank | 100/0/100/0 | 5 | `` |
| `kph.open_time` | constant_zero | 103/103/0/1 | 3 | `0` |
| `kpl.raw_columns.col_03` | all_missing_or_blank | 240/0/240/0 | 5 | `` |
| `eltdx.limit_ladder.prev2_seal_amount` | constant_value | 1/1/0/1 | 1 | `-182112300.0` |
| `market_sources.request_params.date` | constant_value | 1/1/0/1 | 1 | `2026-11-17` |
| `market_sources.request_params.kline_type` | constant_value | 1/1/0/1 | 1 | `daily` |
| `market_sources.request_params.limit` | constant_value | 1/1/0/1 | 1 | `5` |
| `reports.encodeUrl` | constant_value | 1/1/0/1 | 1 | `VF/Aff6xS5JKqu72ctdLoJssK3pKDYRhowFXLzIoI44=` |
| `reports.orgType` | constant_value | 1/1/0/1 | 1 | `white` |
| `eltdx.limit_ladder.alignment_status` | constant_value | 2/2/0/1 | 2 | `previous_trading_day` |
| `eltdx.limit_ladder.exchange` | constant_value | 2/2/0/1 | 2 | `sz` |
| `eltdx.limit_ladder.limit_board_text` | constant_value | 2/2/0/1 | 2 | `1天1板` |
| `eltdx.limit_ladder.limit_status` | constant_value | 2/2/0/1 | 2 | `sealed` |

_显示前 50 / 共 152 项；完整清单在 JSON。_

日期值候选 6 项；应先查官方定义和完整路径，再确定上市日、记录更新日、报告期、公告/事件日、生效日或来源数据日。

### 日期形状字段待核业务含义

| 完整字段路径 | 日期样本比例 | 编码 | 样本键日期数 | 日期值/来源日/样本日/股票样例 |
|:--|--:|:--|--:|:--|
| `etf.etf_sz.date` | 100.0% | YYYY-MM-DD | 5 | 2026-11-10(来源日=20261110;样本日=T:20261110;股票=158000), 2026-11-10(来源日=20261110;样本日=T:20261110;股票=158001), 2026-11-10(来源日=20261110;样本日=T:20261110;股票=158003), 2026-11-10(来源日=20261110;样本日=T:20261110;股票=158005), 2026-11-10(来源日=20261110;样本日=T:20261110;股票=158006) |
| `etf.etf_sh.date` | 100.0% | YYYY-MM-DD | 4 | 2026-11-12(来源日=20261112;样本日=T:20261112;股票=510010), 2026-11-12(来源日=20261112;样本日=T:20261112;股票=510020), 2026-11-12(来源日=20261112;样本日=T:20261112;股票=510030), 2026-11-12(来源日=20261112;样本日=T:20261112;股票=510040), 2026-11-12(来源日=20261112;样本日=T:20261112;股票=510050) |
| `research_sina.date` | 100.0% | YYYY-MM-DD | 5 | 2026-11-13(来源日=20261113;样本日=C:20261113;股票=600309#event0), 2026-11-13(来源日=20261113;样本日=C:20261113;股票=600309#event1), 2026-11-13(来源日=20261113;样本日=C:20261113;股票=600519#event0), 2026-11-13(来源日=20261113;样本日=C:20261113;股票=600519#event1), 2026-11-14(来源日=20261114;样本日=C:20261114;股票=601288#event2) |
| `news_wscn_cctv.date` | 100.0% | YYYY-MM-DD | 2 | 2026-11-16(来源日=20261116;样本日=C:20261116;股票=__0), 2026-11-16(来源日=20261116;样本日=C:20261116;股票=__1), 2026-11-16(来源日=20261116;样本日=C:20261116;股票=__10), 2026-11-16(来源日=20261116;样本日=C:20261116;股票=__11), 2026-11-16(来源日=20261116;样本日=C:20261116;股票=__12) |
| `market_sources.data_date` | 100.0% | YYYY-MM-DD | 5 | 2026-11-10(来源日=20261110;样本日=T:20261110;股票=000007), 2026-11-12(来源日=20261112;样本日=T:20261112;股票=000007), 2026-11-16(来源日=20261116;样本日=T:20261116;股票=levistock_daily_candidate), 2026-11-17(来源日=20261117;样本日=T:20261117;股票=levistock_daily_candidate), 2026-11-18(来源日=20261118;样本日=T:20261118;股票=levistock_daily_candidate) |
| `market_sources.requested_trade_date` | 100.0% | YYYY-MM-DD | 5 | 2026-11-10(来源日=20261110;样本日=T:20261110;股票=kph_limit_ladder), 2026-11-12(来源日=20261112;样本日=T:20261112;股票=kph_limit_ladder), 2026-11-16(来源日=20261116;样本日=T:20261116;股票=kph_limit_ladder), 2026-11-17(来源日=20261117;样本日=T:20261117;股票=kph_limit_ladder), 2026-11-18(来源日=20261118;样本日=T:20261118;股票=kph_limit_ladder) |

## 候选身份与人工审阅状态

- 候选身份：生成 153 条，唯一候选 153 个，重复身份 0，无效身份 0。
- 审阅台账：可用；当前状态 `pending`；已审 0，待处理 153，覆盖率 0.0%。
- 重复归并组：0；每个成员均保留到代表候选的反向追溯。
- 处置计数：`accepted_for_adjudication` 0；`duplicate_grouped` 0；`insufficient_evidence` 0；`needs_external_evidence` 0；`rejected` 0；`unreviewed` 153。
- `accepted_for_adjudication` 只表示可进入现有证据裁决流程；审阅台账不会修改主字典或字段注册表。

## 报告完整性与审阅范围

- 机器可读完整性：`complete`；方法候选生成 150 条，完整明细保存 150 条，缺失 0 条，多余 0 条，重复 0 条，身份无效 0 条。
- 全量方法候选位于同名 JSON 的 `method_candidate_inventory`；Markdown 的 Top-N 表格是导航摘要，不能代替全量 JSON 审阅。
- 候选审阅数据对账：`complete`；唯一候选 153 个，审阅 0 个，待处理 153 个；人工审阅进度与机器清单完整性分别统计。
- Markdown 未逐行展示、但 JSON 保留的部分：
  - `method_candidates`：展示 100 / 150，摘要省略 50 条。
  - `method_candidate_inventory`：展示 0 / 150，摘要省略 150 条。
  - `candidate_triage.targets`：展示 50 / 107，摘要省略 57 条。
  - `candidate_triage.low_information_fields`：展示 50 / 152，摘要省略 102 条。
- 完整性对账通过；逐目标复核仍须覆盖 JSON 的全部明细，并为每项记录已检查、重复归并、证据不足或需外部核验的处置。
