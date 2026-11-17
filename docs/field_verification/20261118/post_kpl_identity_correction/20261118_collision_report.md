# 全源对撞报告（20261118）

> 交易数据窗口配置：全部历史日期（`--all`），行情数据截至 20261117
> 行情窗口：20261015 ~ 20261117（22 个不同交易日）｜字段 1309 个｜样本值 1493955 条
> 新闻/公告自然日窗口：20261015 ~ 20261118
> 主攻目标（unverified）=138｜可审定新候选=0｜首次发现新候选对=0｜已登记关系复验=0｜异号同义 0 / 同号镜像 0

> **规则**：L1 每日需≥18 组有效配对，并至少有5 组信息配对；双方同时为 0 或同时缺失不计命中率，一侧为 0、另一侧非 0 按失配计。信息配对命中率≥90%，且覆盖至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。JSON `daily_sample_counts` 与 `daily_informative_sample_counts`分别保留每日有效配对数和 L1 信息配对数。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 新候选 — 异号同义（跨编号，高价值）(0)

_本轮无异号同义候选。_


## 二、L1 / L1-U 新候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、已登记映射的本窗口复验（0）

_这些关系已在主注册表登记，只用于观察当前样本是否仍支持既有映射；它们不是新的未知字段候选，也不能再次提交为新定案。_

_本轮没有已登记关系进入复验窗口。_


## 四、L4 存疑候选（2）

| 左字段 | 右字段 | 关系类别 | 证据依据 | 处理进度 | 命中率 | 天数 | 配对数 | 信息配对数 |
|:--|:--|:--|:--|:--|--:|--:|--:|--:|
| `kph.industry_limit_up_count` | `kpl.raw_columns.col_20` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 100.00% | 1 | 31 | 31 |
| `kpl.raw_columns.col_02` | `push2ex.limit_count` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 42.96% | 19 | 1122 | 1122 |

## 五、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 六、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `event_dc.TOTAL_SHARES` | `ftshare_rest.shares` | robust_correlation, affine_formula, semantic_label | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.CHANGE_RATE` | `ftshare_rest.change_rate` | robust_correlation, affine_formula, semantic_label | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `event_dc.CHANGE_RATE` | `ftshare_rest.change` | robust_correlation, affine_formula, semantic_label | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=0.993, Spearman=0.9984, LOO稳号=True |
| `event_dc.CHANGE` | `ftshare_rest.change_rate` | robust_correlation, affine_formula, semantic_label | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=0.993, Spearman=0.9985, LOO稳号=True |
| `event_dc.CHANGE` | `ftshare_rest.change` | robust_correlation, affine_formula, semantic_label | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.open_volume_ratio` | robust_correlation, per_stock_time_series | 160 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, ulist239 | Pearson=0.3496, Spearman=0.6809, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.open_volume_hand` | robust_correlation, per_stock_time_series | 160 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, ulist239 | Pearson=0.4152, Spearman=0.8155, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.open_prev_amount_ratio` | robust_correlation, per_stock_time_series | 160 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, ulist239 | Pearson=0.3585, Spearman=0.7014, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.open_amount` | robust_correlation, per_stock_time_series | 160 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, ulist239 | Pearson=0.9004, Spearman=0.9746, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.open_amount_yuan` | robust_correlation, per_stock_time_series | 160 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, ulist239 | Pearson=0.9004, Spearman=0.9746, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.open_amount_raw` | robust_correlation, per_stock_time_series | 160 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, ulist239 | Pearson=0.9004, Spearman=0.9746, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.current_hand` | robust_correlation, per_stock_time_series | 160 | T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109 | eltdx, ulist239 | Pearson=0.2633, Spearman=0.7015, LOO稳号=True |
| `ulist239.f63` | `zhb.stat2.main_net_buy_hands` | robust_correlation, per_stock_time_series | 100 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb | Pearson=0.4172, Spearman=0.8323, LOO稳号=True |
| `ulist239.f63` | `zhb.stat2.main_net_buy_amount` | robust_correlation, per_stock_time_series | 100 | T:20261102, T:20261103, T:20261104, T:20261106, T:20261109 | ulist239, zhb | Pearson=0.9146, Spearman=0.9724, LOO稳号=True |
| `event_dc.fetched_at` | `ftshare_rest.ts_millis` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=0.9988, Spearman=0.9992, LOO稳号=True |
| `event_dc.TURNOVERRATE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.TURNOVERRATE` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.TOTAL_SHARES` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.TOTAL_ISSUE_NUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.TOTAL_ISSUE_NUM` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.TOTAL_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.TOTAL_CHANGE` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.TNEW_PRICE` | `ftshare_rest.close` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.TCHANGE_RATE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-0.9959, Spearman=-0.8665, LOO稳号=True |
| `event_dc.TCHANGE_RATE` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-0.9959, Spearman=-0.8665, LOO稳号=True |
| `event_dc.PROFIT` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.PROFIT` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.OPEN_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.OPEN_PRICE` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.OPEN_AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.OPEN_AVERAGE_PRICE` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.OD_HIGH_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.OD_HIGH_CHANGE` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.MZYQ_PAY_FUND` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.MZYQ_PAY_FUND` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.LIMIT_UP_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.LIMIT_UP_PRICE` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.LD_OPEN_PREMIUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.LD_OPEN_PREMIUM` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.LD_HIGH_CHANG` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.LD_HIGH_CHANG` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.LD_CLOSE_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.LD_CLOSE_CHANGE` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.LD_AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.LD_AVERAGE_PRICE` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.LATELY_PRICE` | `ftshare_rest.close` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.ISSUE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.ISSUE_PRICE` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.ISSUE_NUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.ISSUE_NUM` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `event_dc.IPO_YIELD` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.IPO_YIELD` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.INDUSTRY_PE_NEW` | `ftshare_rest.ts_millis` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-0.9921, Spearman=-0.9967, LOO稳号=True |
| `event_dc.INDUSTRY_PE` | `ftshare_rest.ts_millis` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-0.9921, Spearman=-0.9967, LOO稳号=True |
| `event_dc.CLOSE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.CLOSE_PRICE` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.AVERAGE_PRICE` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.AMPLITUDE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `event_dc.AMPLITUDE` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula | 34 | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029 | event_dc, ftshare_rest | Pearson=-1.0, Spearman=-1.0, LOO稳号=True |
| `kph.industry_limit_up_count` | `kpl.raw_columns.col_20` | robust_correlation, affine_formula | 31 | T:20261116 | kph, kpl | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `tencent[9]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9983, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `tencent[85]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9985, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `tencent[5]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9992, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `tencent[51]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9987, Spearman=0.9956, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `tencent[4]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `tencent[48]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9974, Spearman=0.9956, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `tencent[47]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9983, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `tencent[42]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9976, Spearman=0.9956, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `tencent[41]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9983, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `tencent[3]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9983, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `tencent[34]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9976, Spearman=0.9956, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `tencent[33]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9983, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `tencent[17]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9984, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `tencent[15]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9984, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `tencent[13]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9984, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `tencent[11]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9983, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `sina[6]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina | Pearson=0.9983, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `sina[5]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina | Pearson=0.9976, Spearman=0.9956, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `sina[4]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina | Pearson=0.9983, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `sina[3]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina | Pearson=0.9983, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `sina[2]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `sina[1]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina | Pearson=0.9992, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `sina[19]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina | Pearson=0.9984, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `sina[17]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina | Pearson=0.9984, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `sina[15]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina | Pearson=0.9984, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `sina[13]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina | Pearson=0.9983, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pre_close` | `sina[11]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, sina | Pearson=0.9983, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.pe_ttm` | `tencent[39]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9983, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.open_price` | `tencent[9]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9965, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.open_price` | `tencent[85]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9967, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.open_price` | `tencent[5]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.open_price` | `tencent[51]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9984, Spearman=0.9956, LOO稳号=True |
| `eltdx.limit_ladder.open_price` | `tencent[4]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9992, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.open_price` | `tencent[48]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9978, Spearman=0.9956, LOO稳号=True |
| `eltdx.limit_ladder.open_price` | `tencent[47]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9965, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.open_price` | `tencent[42]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9992, Spearman=0.9956, LOO稳号=True |
| `eltdx.limit_ladder.open_price` | `tencent[41]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9965, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.open_price` | `tencent[3]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9965, Spearman=1.0, LOO稳号=True |
| `eltdx.limit_ladder.open_price` | `tencent[34]` | robust_correlation, affine_formula | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028 | eltdx, tencent | Pearson=0.9992, Spearman=0.9956, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 七、日期与数据质量告警（368）

- 20261017: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261018: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261031: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261101: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261107: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261114: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261118: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
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
- 另有 268 条告警，详见同名 JSON 报告。

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

策略状态：`ok`；逐源分类字段 75，保守默认未分类字段 1234。L1/L1-C 日期证据：来源日期已确认 0 条，跨源值见证推断 0 条，仅语义证据且日期未确认 0 条，其他日期未确认 0 条。

| 日期见证关系 | 结果 | 交易日 | 精确样本 | 非零精确样本 | 不同非零值 | 证据 SHA-256 |
|:--|:--|--:|--:|--:|--:|:--|
| `tdx.quote_raw.ask1_vol <- tencent[20]` | thresholds_met | 19 | 378/378 | 364/364 | 251 | `9f488224d9a95673bf751451c47a3fd1ae05090b51cf090dc014d66818252d69` |
| `tdx.quote_raw.bid1_vol <- tencent[10]` | thresholds_met | 19 | 378/378 | 370/370 | 243 | `9f488224d9a95673bf751451c47a3fd1ae05090b51cf090dc014d66818252d69` |

_本轮 L1/L1-C 没有仅凭静态或缓变字段、且来源日期未确认的关系。_

## 来源字段覆盖与碰撞参与

_窗口字段值样本是经日期筛选、重复折叠和快照择优后载入的非空值；右侧比较次数另受字段类型及来源规则筛选。官方契约字段须有逐字段审定证据，契约语义本身不证明底层数据来源独立。_

| 来源 | 已确认字段 | 契约已确认 | 契约锚 | 独立锚 | L1-C 锚 | 窗口字段 / 字段值样本 / 交易日 |
|:--|--:|--:|--:|--:|--:|--:|
| axdata | 34 | 0 | 0 | 0 | 0 | 34 / 10124 / 19 |
| clist | 20 | 0 | 0 | 20 | 0 | 33 / 57336 / 8 |
| cls | 4 | 0 | 0 | 4 | 0 | 5 / 4750 / 0 |
| cninfo | 6 | 0 | 0 | 6 | 0 | 0 / 0 / 0 |
| datacenter | 46 | 5 | 5 | 46 | 0 | 0 / 0 / 0 |
| eltdx | 237 | 163 | 163 | 237 | 0 | 116 / 21930 / 20 |
| em_fund_flow | 15 | 0 | 0 | 15 | 0 | 15 / 2595 / 9 |
| em_hot | 39 | 0 | 0 | 39 | 0 | 0 / 0 / 0 |
| em_kline_f61 | 11 | 1 | 1 | 11 | 0 | 2 / 320 / 8 |
| etf | 0 | 0 | 0 | 0 | 0 | 9 / 221956 / 19 |
| event_dc | 0 | 0 | 0 | 0 | 0 | 148 / 555514 / 18 |
| exchange | 4 | 0 | 0 | 4 | 0 | 0 / 0 / 0 |
| ftshare | 6 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| ftshare_rest | 32 | 31 | 31 | 0 | 31 | 32 / 10795 / 17 |
| fuyao | 117 | 99 | 99 | 117 | 0 | 20 / 7220 / 19 |
| kph | 12 | 0 | 0 | 12 | 0 | 15 / 465 / 1 |
| kpl | 19 | 0 | 0 | 19 | 0 | 28 / 39880 / 20 |
| market_sources | 15 | 0 | 0 | 0 | 0 | 74 / 148433 / 20 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 2 / 436 / 0 |
| push2 | 69 | 0 | 0 | 69 | 0 | 114 / 24396 / 12 |
| push2ex | 35 | 1 | 1 | 35 | 0 | 16 / 27072 / 19 |
| reports | 46 | 0 | 0 | 46 | 0 | 49 / 980 / 0 |
| research_sina | 0 | 0 | 0 | 0 | 0 | 6 / 7062 / 0 |
| sina | 33 | 0 | 0 | 33 | 0 | 39 / 13800 / 20 |
| sina_extended | 6 | 3 | 3 | 6 | 0 | 4 / 1440 / 18 |
| slist | 5 | 0 | 0 | 5 | 0 | 1 / 160 / 8 |
| sse_e_interaction | 0 | 0 | 0 | 0 | 0 | 8 / 1520 / 0 |
| st_list | 0 | 0 | 0 | 0 | 0 | 6 / 19610 / 11 |
| tdx | 240 | 107 | 107 | 240 | 0 | 63 / 25032 / 20 |
| tencent | 83 | 0 | 0 | 83 | 0 | 88 / 35160 / 20 |
| ulist239 | 70 | 4 | 4 | 70 | 0 | 240 / 38340 / 8 |
| zhb | 246 | 26 | 26 | 246 | 0 | 130 / 28799 / 13 |

| 来源 | 破解目标 | 比较字段 | 作目标比较 | 作右侧比较 | L1-C 锚比较 | L1 / L1-C / L4 关系 | 方法候选涉及 |
|:--|--:|--:|--:|--:|--:|--:|--:|
| axdata | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| clist | 10 | 17 | 3206 | 544 | 0 | 0 / 0 / 0 | 0 |
| cls | 2 | 0 | 566 | 0 | 0 | 0 / 0 / 0 | 0 |
| cninfo | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| datacenter | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| eltdx | 29 | 53 | 8870 | 1356 | 0 | 0 / 0 / 0 | 460 |
| em_fund_flow | 0 | 14 | 0 | 448 | 0 | 0 / 0 / 0 | 0 |
| em_hot | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| em_kline_f61 | 1 | 0 | 354 | 0 | 0 | 0 / 0 / 0 | 12 |
| etf | 4 | 0 | 29 | 0 | 0 | 0 / 0 / 0 | 0 |
| event_dc | 62 | 0 | 1258 | 0 | 0 | 0 / 0 / 0 | 202 |
| exchange | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare_rest | 0 | 25 | 0 | 2586 | 2586 | 0 / 0 / 0 | 299 |
| fuyao | 0 | 14 | 0 | 728 | 0 | 0 / 0 / 0 | 29 |
| kph | 1 | 11 | 522 | 456 | 0 | 0 / 0 / 1 | 3 |
| kpl | 3 | 19 | 577 | 1275 | 0 | 0 / 0 / 2 | 109 |
| market_sources | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| push2 | 4 | 66 | 80 | 1992 | 0 | 0 / 0 / 0 | 0 |
| push2ex | 0 | 12 | 0 | 384 | 0 | 0 / 0 / 1 | 34 |
| reports | 0 | 18 | 0 | 444 | 0 | 0 / 0 / 0 | 0 |
| research_sina | 2 | 0 | 532 | 0 | 0 | 0 / 0 / 0 | 0 |
| sina | 2 | 32 | 996 | 1451 | 0 | 0 / 0 / 0 | 57 |
| sina_extended | 0 | 3 | 0 | 147 | 0 | 0 / 0 / 0 | 12 |
| slist | 1 | 0 | 354 | 0 | 0 | 0 / 0 / 0 | 6 |
| sse_e_interaction | 1 | 0 | 23 | 0 | 0 | 0 / 0 / 0 | 0 |
| st_list | 3 | 0 | 48 | 0 | 0 | 0 / 0 / 0 | 0 |
| tdx | 0 | 52 | 0 | 1566 | 0 | 0 / 0 / 0 | 21 |
| tencent | 3 | 79 | 516 | 3770 | 0 | 0 / 0 / 0 | 202 |
| ulist239 | 10 | 67 | 3206 | 1980 | 0 | 0 / 0 / 0 | 105 |
| zhb | 0 | 76 | 0 | 2010 | 0 | 0 / 0 / 0 | 57 |

## 来源/接口重叠审阅（不自动停采）

此处按**完整规范路径**和来源实际日期对齐比较已采值，单独呈现同家族、不同仓库或血缘未明来源的重叠。数值一致只说明观测范围内的路径等价候选，不证明底层提供方相同、字段语义相同或整条路由可删除。只有接口字段覆盖、唯一字段、备用关系和复验策略均核实后，才可调整采集路由。
来源对 21 组；保留详情 21 组；路径身份歧义 5 项；采集自动停用：否。

| 来源 A / 仓库 | 来源 B / 仓库 | 血缘关系 | 观测关系 | 共同路径 | 强匹配路径 | 失配路径/失配样本/近似样本/未对齐样本 | A/B 独有路径 | 强匹配完整路径样例 |
|:--|:--|:--|:--|--:|--:|--:|:--|:--|
| `sina` / https://github.com/shidenggui/easyquotation | `tencent` / https://github.com/shidenggui/easyquotation | different_confirmed_provider_families | observed_value_differences | 39 | 1 | 38/13152/3403/0 | 0/49 | `[3]` |
| `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | provider_relation_unconfirmed | insufficient_aligned_evidence | 17 | 0 | 0/0/0/1158 | 11/57 | — |
| `em_fund_flow` / https://github.com/fleetinglife/levistock | `ulist239` / https://github.com/fleetinglife/levistock | same_confirmed_provider_family | insufficient_aligned_evidence | 15 | 0 | 0/0/0/2400 | 0/225 | — |
| `em_fund_flow` / https://github.com/fleetinglife/levistock | `push2` / https://github.com/fleetinglife/levistock | same_confirmed_provider_family | insufficient_aligned_evidence | 15 | 0 | 0/0/0/2400 | 0/99 | — |
| `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `push2ex` / https://github.com/fleetinglife/levistock | provider_relation_unconfirmed | insufficient_aligned_evidence | 7 | 0 | 0/0/0/8156 | 67/9 | — |
| `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | provider_relation_unconfirmed | insufficient_aligned_evidence | 4 | 0 | 0/0/0/93 | 11/70 | — |
| `push2ex` / https://github.com/fleetinglife/levistock | `tdx` / https://github.com/yanwei99521/easy-tdx, https://github.com/electkismet/eltdx | different_confirmed_provider_families | insufficient_aligned_evidence | 3 | 0 | 0/0/0/54 | 13/60 | — |
| `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `tdx` / https://github.com/yanwei99521/easy-tdx, https://github.com/electkismet/eltdx | provider_relation_unconfirmed | insufficient_aligned_evidence | 3 | 0 | 0/0/0/163 | 71/60 | — |
| `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `push2ex` / https://github.com/fleetinglife/levistock | different_confirmed_provider_families | insufficient_aligned_evidence | 3 | 0 | 0/0/0/2244 | 25/13 | — |
| `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | `push2ex` / https://github.com/fleetinglife/levistock | different_confirmed_provider_families | insufficient_aligned_evidence | 3 | 0 | 0/0/0/93 | 12/13 | — |
| `ftshare_rest` / — | `tdx` / https://github.com/yanwei99521/easy-tdx, https://github.com/electkismet/eltdx | provider_relation_unconfirmed | insufficient_aligned_evidence | 3 | 0 | 0/0/0/1014 | 29/60 | — |
| `ftshare_rest` / — | `push2ex` / https://github.com/fleetinglife/levistock | provider_relation_unconfirmed | insufficient_aligned_evidence | 2 | 0 | 0/0/0/28 | 30/14 | — |
| `ftshare_rest` / — | `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | provider_relation_unconfirmed | insufficient_aligned_evidence | 2 | 0 | 0/0/0/73 | 30/72 | — |
| `push2ex` / https://github.com/fleetinglife/levistock | `zhb` / https://github.com/yanwei99521/easy-tdx, https://github.com/yanwei99521/easy-tdx | different_confirmed_provider_families | insufficient_aligned_evidence | 1 | 0 | 0/0/0/8 | 15/129 | — |
| `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `zhb` / https://github.com/yanwei99521/easy-tdx, https://github.com/yanwei99521/easy-tdx | provider_relation_unconfirmed | insufficient_aligned_evidence | 1 | 0 | 0/0/0/41 | 73/129 | — |
| `ftshare_rest` / — | `sina_extended` / https://github.com/mpquant/Ashare | provider_relation_unconfirmed | insufficient_aligned_evidence | 1 | 0 | 0/0/0/340 | 31/3 | — |
| `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | different_confirmed_provider_families | observed_value_differences | 3 | 0 | 1/1/0/0 | 12/25 | — |
| `ftshare_rest` / — | `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | provider_relation_unconfirmed | observed_value_differences | 2 | 0 | 1/12/0/0 | 30/26 | — |
| `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `zhb` / https://github.com/yanwei99521/easy-tdx, https://github.com/yanwei99521/easy-tdx | different_confirmed_provider_families | observed_value_differences | 1 | 0 | 1/6/0/0 | 27/129 | — |
| `ftshare_rest` / — | `zhb` / https://github.com/yanwei99521/easy-tdx, https://github.com/yanwei99521/easy-tdx | provider_relation_unconfirmed | observed_value_differences | 1 | 0 | 1/120/0/0 | 31/129 | — |
| `push2` / https://github.com/fleetinglife/levistock | `ulist239` / https://github.com/fleetinglife/levistock | same_confirmed_provider_family | observed_value_differences | 113 | 0 | 107/16898/4/320 | 1/127 | — |

强匹配路径不得有值失配、未对齐样本或低信息常量，并达到每条路径至少 5 个信息样本、3 个不同样本日期、3 只证券；宽松舍入窗口只列为独立近似样本数，不计强匹配；该筛选只产生路由复核候选，不取代现有接口专用退出和复验规则。

## AxData 每日接口核验

> 此处汇总采集目录已保存的本地证据，不发起网络请求、不改变注册表状态；AxData 是多源框架，不作为独立字段锚。

### AxData

窗口内有 22 个唯一数据日的轮验记录；重复目录合并 0 条。
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
| 20261113 | not_eligible | not_run / 0 (字段相同/不同 0/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing | — | — | meta_summary |
| 20261116 | already_recorded | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261117 | already_recorded | sampled / 1 (字段相同/不同 0/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |

被动逐字段比较中的差异计数（跨本窗口唯一数据日累加，不含原始值）：

| 比较路径 | 相同 | 不同 | 缺失/双方空值 |
|:--|--:|--:|--:|
| `axdata_shortline_vs_eltdx:alignment_status` | 0 | 300 | 0 |
| `axdata_shortline_vs_eltdx:beta_60d` | 0 | 300 | 0 |
| `axdata_shortline_vs_eltdx:code` | 0 | 300 | 0 |
| `axdata_shortline_vs_eltdx:full_code` | 0 | 300 | 0 |
| `axdata_shortline_vs_eltdx:instrument_id` | 0 | 300 | 0 |
| `axdata_shortline_vs_eltdx:limit_status` | 0 | 300 | 0 |
| `axdata_shortline_vs_eltdx:market_id` | 0 | 300 | 0 |
| `axdata_shortline_vs_eltdx:opening_rush` | 0 | 300 | 0 |
| `axdata_shortline_vs_eltdx:pe_ttm` | 0 | 300 | 0 |
| `axdata_shortline_vs_eltdx:previous_trade_date` | 0 | 300 | 0 |
| `axdata_shortline_vs_eltdx:symbol` | 0 | 300 | 0 |
| `axdata_shortline_vs_eltdx:target_trade_date` | 0 | 300 | 0 |
| `axdata_shortline_vs_eltdx:tdx_code` | 0 | 300 | 0 |
| `axdata_shortline_vs_eltdx:open_amount` | 58 | 242 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_hand` | 58 | 242 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_ratio` | 58 | 242 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_amount_ratio` | 70 | 230 | 0 |
| `axdata_shortline_vs_eltdx:auction_prev_volume_ratio` | 82 | 214 | 4 |
| `axdata_shortline_vs_eltdx:open_turnover_z` | 157 | 143 | 0 |
| `kph_limit_up_history_vs_kpl_detail:seal_amount` | 74 | 95 | 0 |
| `kph_limit_up_history_vs_kpl_detail:seal_money` | 74 | 95 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_seal_ratio` | 5 | 15 | 280 |
| `axdata_shortline_vs_eltdx:ladder_level` | 0 | 9 | 291 |
| `axdata_shortline_vs_eltdx:limit_board_text` | 23 | 8 | 269 |

### FTShare 退役来源历史记录（显式历史研究）

窗口内保留 3 个唯一数据日的旧元数据；重复目录合并 0 条。

| 数据日 | 历史状态 | 旧接口状态计数 |
|:--|:--|:--|
| 20261015 | ok | pending: 6 |
| 20261016 | ok | pending: 6 |
| 20261019 | ok | pending: 6 |

## 字母字段名语义提示（仅候选）

窗口内观察到 97 条需审阅的字母字段路径：含词义线索 24 条，仅拆词 73 条。
完整逐条记录保存在碰撞 JSON；名称线索清单：`docs/field_verification/20261014/20261014_alphabetic_field_name_inventory.csv`。
> 拼音、英文、缩写和混合拆词只用于检索候选；必须结合原始值、接口定义和独立来源复核，不得据此定案或改写主字典。

| 逐源字段路径 | 状态/审阅范围 | 名称形式与拆词 | 词义线索（非释义） | 样本日期 |
|:--|:--|:--|:--|:--|
| `市场源(market_sources)::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `东财-push2ex::code` | verified / verified_metadata_gap | recognized_english_word_candidate: code | 代码 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `东财-push2ex::name` | verified / verified_metadata_gap | recognized_english_word_candidate: name | 名称 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `市场源(market_sources)::limit_count` | verified / verified_metadata_gap | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `市场源(market_sources)::limit_time` | unverified / unverified_semantics | snake_case_or_mixed: limit time | 涨跌停限制 + 时间 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `市场源(market_sources)::plate_limit_up_count` | verified / verified_metadata_gap | snake_case_or_mixed: plate limit up count | 涨跌停限制 + 上/涨 + 数量/次数 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `财联社(cls)::time` | unverified / unverified_semantics | recognized_english_word_candidate: time | 时间 | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110, C:20261112, C:20261116, C:20261117 |
| `TDX(双命名源)::changqifuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: changqifuzhai | 长期负债 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `TDX(双命名源)::cunhuo` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: cunhuo | 存货 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `TDX(双命名源)::jingyingxianjinliu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingyingxianjinliu | 经营现金流 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `TDX(双命名源)::jingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingzichan | 净资产 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `TDX(双命名源)::liudongfuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: liudongfuzhai | 流动负债 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `TDX(双命名源)::meigujingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: meigujingzichan | 每股净资产 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `TDX(双命名源)::yingshouzhangkuan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: yingshouzhangkuan | 应收账款 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `TDX(双命名源)::zibengongjijin` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zibengongjijin | 资本公积金 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `TDX(双命名源)::zongzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongzichan | 总资产 | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `同花顺-fuyao::snapshot.open_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot open price | 开盘 + 价格 | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `reports::count` | verified / verified_metadata_gap | recognized_english_word_candidate: count | 数量/次数 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::lastEmRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Code | 最近/上一期 + 代码 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::lastEmRatingName` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Name | 最近/上一期 + 名称 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::lastEmRatingValue` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Value | 最近/上一期 + 值 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::predictLastYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Eps | 最近/上一期 + 每股收益 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::predictLastYearPe` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Pe | 最近/上一期 + 市盈率 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `市场源(market_sources)::one_word` | unverified / unverified_semantics | snake_case_or_mixed: one word | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `市场源(market_sources)::plate_amount` | verified / verified_metadata_gap | snake_case_or_mixed: plate amount | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `市场源(market_sources)::plate_code` | verified / verified_metadata_gap | snake_case_or_mixed: plate code | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `市场源(market_sources)::plate_name` | verified / verified_metadata_gap | snake_case_or_mixed: plate name | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `市场源(market_sources)::popular` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: popular | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `开盘啦(kpl_limit_up_detail)::raw_columns.col_19` | verified / verified_metadata_gap | runtime_tokenization_only: col 19 | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `财联社(cls)::content` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: content | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110, C:20261112, C:20261116, C:20261117 |
| `财联社(cls)::level` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: level | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110, C:20261112, C:20261116, C:20261117 |
| `财联社(cls)::reading_num` | unverified / unverified_semantics | snake_case_or_mixed: reading num | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110, C:20261112, C:20261116, C:20261117 |
| `财联社(cls)::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20261016, C:20261019, C:20261020, C:20261022, C:20261023, C:20261026, C:20261028, C:20261029, C:20261031, C:20261102, C:20261103, C:20261104, C:20261105, C:20261107, C:20261108, C:20261109, C:20261110, C:20261112, C:20261116, C:20261117 |
| `市场源(market_sources)::big_order_300w_net` | unverified / unverified_semantics | runtime_tokenization_only: big order 300 w net | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `市场源(market_sources)::institution_add` | unverified / unverified_semantics | runtime_tokenization_only: institution add | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `市场源(market_sources)::main_inflow` | unverified / unverified_semantics | snake_case_or_mixed: main inflow | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `市场源(market_sources)::pe_next` | unverified / unverified_semantics | runtime_tokenization_only: pe next | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `市场源(market_sources)::pe_now` | unverified / unverified_semantics | runtime_tokenization_only: pe now | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `市场源(market_sources)::strength` | unverified / unverified_semantics | runtime_tokenization_only: strength | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `市场源(market_sources)::total_value` | unverified / unverified_semantics | runtime_tokenization_only: total value | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `同花顺-fuyao::snapshot.prev_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot prev price | — | T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `FTShare REST::amplitude` | verified / verified_metadata_gap | runtime_tokenization_only: amplitude | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `FTShare REST::avg` | verified / verified_metadata_gap | runtime_tokenization_only: avg | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `FTShare REST::bid_ask_ratio` | verified / verified_metadata_gap | runtime_tokenization_only: bid ask ratio | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `FTShare REST::board` | verified / verified_metadata_gap | runtime_tokenization_only: board | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `FTShare REST::listing_date` | verified / verified_metadata_gap | runtime_tokenization_only: listing date | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `FTShare REST::name` | verified / verified_metadata_gap | runtime_tokenization_only: name | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `FTShare REST::st` | verified / verified_metadata_gap | runtime_tokenization_only: st | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `FTShare REST::status` | verified / verified_metadata_gap | runtime_tokenization_only: status | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `FTShare REST::symbol` | verified / verified_metadata_gap | runtime_tokenization_only: symbol | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `FTShare REST::symbol_id` | verified / verified_metadata_gap | runtime_tokenization_only: symbol id | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `FTShare REST::turnover_rate` | verified / verified_metadata_gap | runtime_tokenization_only: turnover rate | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `ZHB-tdxstat::stat.unknown_2` | verified / verified_metadata_gap | snake_case_or_mixed: stat unknown 2 | — | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104, T:20261106, T:20261109, T:20261113, T:20261116 |
| `ZHB-tdxstat::stat.unknown_26` | verified / verified_metadata_gap | snake_case_or_mixed: stat unknown 26 | — | T:20261016, T:20261019, T:20261020, T:20261023, T:20261028, T:20261030, T:20261102, T:20261103, T:20261104, T:20261106, T:20261109, T:20261113, T:20261116 |
| `FTShare REST::pe_ttm` | verified / verified_metadata_gap | runtime_tokenization_only: pe ttm | — | T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `市场源(market_sources)::rank` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: rank | — | T:20261019, T:20261020, T:20261021, T:20261023, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `开盘红::industry_limit_up_count` | unverified / unverified_semantics | runtime_tokenization_only: industry limit up count | — | T:20261116 |
| `TDX-eltdx(适配层)::adjust_mode` | verified / verified_metadata_gap | snake_case_or_mixed: adjust mode | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `TDX-eltdx(适配层)::anchor_date_raw` | verified / verified_metadata_gap | snake_case_or_mixed: anchor date raw | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `TDX-eltdx(适配层)::category` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: category | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `TDX-eltdx(适配层)::period_name` | verified / verified_metadata_gap | snake_case_or_mixed: period name | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `TDX-eltdx(适配层)::raw_payload` | unverified / unverified_semantics | snake_case_or_mixed: raw payload | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `TDX-eltdx(适配层)::sort_by` | unverified / unverified_semantics | snake_case_or_mixed: sort by | — | T:20261015, T:20261016, T:20261019, T:20261020, T:20261021, T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104, T:20261105, T:20261106, T:20261109, T:20261110, T:20261112, T:20261116, T:20261117 |
| `reports::attachType` | verified / verified_metadata_gap | camel_case_or_mixed: attach Type | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::column` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: column | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::emIndustryCode` | unverified / unverified_semantics | camel_case_or_mixed: em Industry Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::emRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: em Rating Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::emRatingName` | verified / verified_metadata_gap | camel_case_or_mixed: em Rating Name | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::emRatingValue` | verified / verified_metadata_gap | camel_case_or_mixed: em Rating Value | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::encodeUrl` | conflict / unverified_semantics | camel_case_or_mixed: encode Url | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::industryCode` | verified / verified_metadata_gap | camel_case_or_mixed: industry Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::industryName` | verified / verified_metadata_gap | camel_case_or_mixed: industry Name | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::indvInduCode` | verified / verified_metadata_gap | camel_case_or_mixed: indv Indu Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::indvInduName` | verified / verified_metadata_gap | camel_case_or_mixed: indv Indu Name | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::indvIsNew` | verified / verified_metadata_gap | camel_case_or_mixed: indv Is New | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::infoCode` | verified / verified_metadata_gap | camel_case_or_mixed: info Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::newPurchaseDate` | verified / verified_metadata_gap | camel_case_or_mixed: new Purchase Date | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::orgCode` | verified / verified_metadata_gap | camel_case_or_mixed: org Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::orgName` | verified / verified_metadata_gap | camel_case_or_mixed: org Name | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::orgSName` | verified / verified_metadata_gap | camel_case_or_mixed: org S Name | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::orgType` | unverified / unverified_semantics | camel_case_or_mixed: org Type | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::predictNextTwoYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Next Two Year Eps | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::predictNextYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Next Year Eps | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::predictThisYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict This Year Eps | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::publishDate` | verified / verified_metadata_gap | camel_case_or_mixed: publish Date | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::ratingChange` | verified / verified_metadata_gap | camel_case_or_mixed: rating Change | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::reportType` | verified / verified_metadata_gap | camel_case_or_mixed: report Type | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::researcher` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: researcher | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::sRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: s Rating Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::sRatingName` | verified / verified_metadata_gap | camel_case_or_mixed: s Rating Name | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::stockCode` | verified / verified_metadata_gap | camel_case_or_mixed: stock Code | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::stockName` | verified / verified_metadata_gap | camel_case_or_mixed: stock Name | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `reports::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104, C:20261105, C:20261108, C:20261110, C:20261111, C:20261113 |
| `市场源(market_sources)::reason` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: reason | — | T:20261016, T:20261106 |

## 探索候选持续跟踪

研究台账：`collision_research_state.json.gz`；累计历史跟踪候选对 4206，本报告候选对 513，历史复现 456，新发现 0。
台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，不会自动改变字段状态、碰撞锚或主字典。新报告只将 `actionable_L1`、L4 和主动方法候选写入待研究队列；已登记关系的复验单独展示，历史跟踪记录不会被删除。

## 候选覆盖、公式与下一步采样

本节用于定位证据缺口和安排后续取样。相关性、公式与样本优先级均为探索候选；不会改变 L1/L1-U 门槛、来源独立性或主字典。

- 未知目标 138 个；其中有方法候选 58 个、无候选 80 个；多候选目标 53 个；有官方契约锚强匹配 0 个、诊断命中 0 个，日期值候选 0 个。
- 方法候选生成 804 条；全局详细项保留 500/500，另按目标字段保留 12 条；完整明细 804 条在 JSON `method_candidate_inventory`；未归档明细 0 条。
- 字段覆盖详情：available；覆盖身份 1999，读取 22 份本地索引。

### 优先处理字段

| 未知字段 | 核验入口 | 当前诊断 | 官方锚强/诊断 | 独立对比/候选数 | 独立锚家族/本源日期 | 建议复核股票 | 最强候选线索 |
|:--|:--|:--|--:|--:|:--|:--|:--|
| `ulist239.f63` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 331 / 75 | 6 家族 / 331 对 / 本源 0 日 | no_shared_stock_holdout | eltdx.shortline.open_volume_ratio (robust_correlation,per_stock_time_series); eltdx.shortline.open_volume_hand (robust_correlation,per_stock_time_series) |
| `kpl.raw_columns.col_02` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 482 / 53 | 6 家族 / 482 对 / 本源 0 日 | no_shared_stock_holdout | tencent[8] (robust_correlation); tencent[76] (robust_correlation) |
| `eltdx.limit_ladder.open_price` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 52 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[85] (robust_correlation,affine_formula) |
| `eltdx.limit_ladder.pre_close` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 52 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[85] (robust_correlation,affine_formula) |
| `eltdx.limit_ladder.prev_amount` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 36 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | tencent[8] (robust_correlation); tencent[7] (robust_correlation) |
| `eltdx.limit_ladder.open_amount` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 29 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | tencent[8] (robust_correlation); tencent[7] (robust_correlation) |
| `eltdx.limit_ladder.open_prev_amount_ratio` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 27 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | tencent[67] (robust_correlation); tencent[50] (robust_correlation) |
| `eltdx.limit_ladder.open_volume_hand` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 26 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | tencent[8] (robust_correlation); tencent[79] (robust_correlation) |
| `eltdx.limit_ladder.prev_open_volume_hand` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 26 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | tencent[79] (robust_correlation); tencent[75] (robust_correlation) |
| `eltdx.limit_ladder.open_turnover_z` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 25 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | tencent[8] (robust_correlation); tencent[79] (robust_correlation) |
| `eltdx.limit_ladder.prev_open_amount` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 23 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | tencent[79] (robust_correlation); tencent[76] (robust_correlation) |
| `eltdx.limit_ladder.year_limit_up_days` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 21 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | tencent[79] (robust_correlation); tencent[75] (robust_correlation) |
| `eltdx.limit_ladder.seal_to_amount_ratio` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 20 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | tencent[50] (robust_correlation); tencent[18] (robust_correlation) |
| `eltdx.limit_ladder.open_volume_ratio` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 19 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | tencent[50] (robust_correlation); tencent[43] (robust_correlation) |
| `eltdx.limit_ladder.seal_to_float_ratio` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 19 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | tencent[68] (robust_correlation); tencent[50] (robust_correlation) |
| `eltdx.limit_ladder.beta_60d` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 12 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | tencent[76] (robust_correlation); tencent[73] (robust_correlation) |
| `em_kline_f61.dktotal` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 331 / 12 | 6 家族 / 331 对 / 本源 0 日 | no_shared_stock_holdout | tencent[30] (per_stock_time_series); tencent[2] (robust_correlation) |
| `ulist239.f148` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 331 / 11 | 6 家族 / 331 对 / 本源 0 日 | 600825 (0.97708) | tencent[71] (robust_correlation); ftshare_rest.change_rate_day60 (robust_correlation) |
| `eltdx.limit_ladder.pe_ttm` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 10 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | tencent[39] (robust_correlation,affine_formula); fuyao.valuation.pe_ttm (robust_correlation,affine_formula) |
| `eltdx.limit_ladder.ladder_level` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 9 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | push2ex.limit_count (robust_correlation,affine_formula); kpl.raw_columns.col_15 (robust_correlation,affine_formula) |
| `event_dc.AMPLITUDE` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 9 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.CLOSE_PRICE` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 9 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.LATELY_PRICE` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 9 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.close (robust_correlation,affine_formula); ftshare_rest.prev_close (robust_correlation) |
| `event_dc.OPEN_PRICE` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 9 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.TNEW_PRICE` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 9 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.close (robust_correlation,affine_formula); ftshare_rest.prev_close (robust_correlation) |
| `event_dc.TOTAL_CHANGE` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 9 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.AVERAGE_PRICE` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.CHANGE_RATE` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.change_rate (robust_correlation,affine_formula,semantic_label); ftshare_rest.change (robust_correlation,affine_formula,semantic_label) |
| `event_dc.IPO_YIELD` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.ISSUE_NUM` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.ISSUE_PRICE` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.LD_AVERAGE_PRICE` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.LD_CLOSE_CHANGE` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.LD_HIGH_CHANG` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.LD_OPEN_PREMIUM` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.LIMIT_UP_PRICE` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.MZYQ_PAY_FUND` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.OD_HIGH_CHANGE` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.OPEN_AVERAGE_PRICE` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.PROFIT` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.TOTAL_ISSUE_NUM` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.TOTAL_SHARES` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula,semantic_label); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `event_dc.TURNOVERRATE` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 8 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `ulist239.f99` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 331 / 8 | 6 家族 / 331 对 / 本源 0 日 | 000678 (4.202929) | tencent[67] (per_stock_time_series); eltdx.shortline.limit_up_count_in_stat_days (robust_correlation) |
| `eltdx.limit_ladder.open_change_pct` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 327 / 7 | 6 家族 / 327 对 / 本源 0 日 | no_shared_stock_holdout | tencent[43] (robust_correlation); tencent[12] (robust_correlation) |
| `tencent[86]` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 435 / 7 | 6 家族 / 435 对 / 本源 20 日 | no_shared_stock_holdout | eltdx.shortline.prev2_seal_amount (robust_correlation); zhb.stat2.zt_seal_amount (robust_correlation) |
| `event_dc.TCHANGE_RATE` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 0 / 6 | 0 家族 / 0 对 / 本源 0 日 | no_shared_stock_holdout | ftshare_rest.shares (robust_correlation,affine_formula); ftshare_rest.float_a_shares (robust_correlation,affine_formula) |
| `slist.n_boards` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 331 / 6 | 6 家族 / 331 对 / 本源 0 日 | no_shared_stock_holdout | tencent[45] (robust_correlation); tencent[44] (robust_correlation) |
| `ulist239.f59` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 331 / 5 | 6 家族 / 331 对 / 本源 0 日 | 301190 (34.197251) | fuyao.valuation.ps_ttm (robust_correlation); fuyao.valuation.pcf_ttm (robust_correlation) |
| `ulist239.f98` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 331 / 5 | 6 家族 / 331 对 / 本源 0 日 | 000678 (3.467692) | zhb.stat.zt_streak_cycle (robust_correlation); zhb.stat.zt_count (robust_correlation) |

_此表显示优先级最高的 50 / 共 138 个目标；完整清单见 JSON。_


### 舍入近似数值线索（仅研究，不算 L1/L1-U；0 组）

近似窗口只用于提示复核：需核对双方原始单位、展示精度和来源口径；不得把该命中率当作字段语义结论或注册表写回依据。完整明细在 JSON `candidate_triage.approximate_matches`。

_本轮没有达到近似筛查门槛的关系。_


### 补足全局截断的字段候选（12）

| 未知字段 | 候选字段 | 方法 | 样本 | 日期 | 来源 |
|:--|:--|:--|--:|:--|:--|
| `eltdx.limit_ladder.auction_prev_volume_ratio` | `tencent[2]` | robust_correlation | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.beta_60d` | `tencent[76]` | robust_correlation | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.ladder_level` | `tencent[68]` | robust_correlation | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_amount` | `tencent[8]` | robust_correlation | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_change_pct` | `tencent[43]` | robust_correlation | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_prev_amount_ratio` | `tencent[67]` | robust_correlation | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_turnover_z` | `tencent[8]` | robust_correlation | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.open_volume_hand` | `tencent[8]` | robust_correlation | 14 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, tencent |
| `eltdx.limit_ladder.pe_ttm` | `kpl.raw_columns.col_20` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, kpl |
| `eltdx.limit_ladder.seal_to_amount_ratio` | `push2ex.limit_fund` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | eltdx, push2ex |
| `kpl.raw_columns.col_02` | `tencent[8]` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, tencent |
| `tencent[86]` | `kpl.raw_columns.col_21` | robust_correlation | 13 | T:20261016, T:20261020, T:20261021, T:20261023, T:20261026 | kpl, tencent |

### 双输入公式候选
本轮未发现通过留出筛选的公式候选；测试组合 123 个。


### 已知映射与已证伪关系的候选校准

- 已登记正向对照：当前窗口有 158 组独立数值关系可评估，157 组被方法候选识别；样本不足 0 组。此计数仅检查方法覆盖，不是准确率。
- 已证伪负向对照：数值关系 0 组，其中仍有方法信号 0 组；这些信号被隔离，不进入普通候选。

### 采集覆盖异常源

- axdata: 20261021, 20261026 ({'failed': 1, 'ok': 18, 'partial': 1})
- baidu: 20261112, 20261116, 20261117 ({'deprecated': 2, 'pending_validation': 17})
- clist: 20261030, 20261112, 20261116 ({'ok': 8, 'partial': 10})
- em_fund_flow: 20261030, 20261112, 20261116 ({'ok': 8, 'partial': 11})
- em_hot: 20261112, 20261116, 20261117 ({'context_only': 18})
- em_kline_f61: 20261030, 20261112, 20261116 ({'ok': 8, 'partial': 11})
- exchange: 20261112, 20261116, 20261117 ({'context_only': 18})
- ftshare: 20261112, 20261116, 20261117 ({'deprecated': 17, 'failed': 3})
- market_sources: 20261026 ({'ok': 19, 'partial': 1})
- news_wscn_cctv: 20261015 ({'ok': 19, 'partial': 1})
- push2: 20261030, 20261112, 20261116 ({'failed': 6, 'ok': 8, 'partial': 4})
- slist: 20261030, 20261112, 20261116 ({'failed': 10, 'ok': 8})
- sse_e_interaction: 20261016 ({'ok': 19, 'partial': 1})
- st_list: 20261028, 20261029, 20261030 ({'ok': 11, 'partial': 8})
- tdx: 20261104, 20261105 ({'ok': 18, 'partial': 2})
- ulist239: 20261030, 20261112, 20261116 ({'failed': 12, 'ok': 8})
- zhb: 20261110, 20261112, 20261117 ({'ok': 7, 'partial': 14})

## 低信息与日期语义专项队列

恒空、恒零或当前恒定字段不参与普通碰撞；状态表示当前样本没有区分力，新采样出现有效变化后重新纳入。日期形状只代表值可解析为日期，必须查清业务角色，不能拿字段值代替来源 `as_of_date`。
低信息未知路径 141 项，状态分布 `{'constant_zero': 29, 'all_missing_or_blank': 5, 'constant_value': 107}`。

### 等待新信息的字段

| 完整字段路径 | 状态 | 观测/非空/缺失或空白/不同值 | 样本日期数 | 示例值 |
|:--|:--|--:|--:|:--|
| `market_sources.request_params.offset` | constant_zero | 3/3/0/1 | 3 | `0` |
| `eltdx.raw_payload` | all_missing_or_blank | 20/0/20/0 | 20 | `` |
| `reports.emIndustryCode` | all_missing_or_blank | 20/0/20/0 | 14 | `` |
| `kph.open_time` | constant_zero | 31/31/0/1 | 1 | `0` |
| `sina[34]` | constant_zero | 40/40/0/1 | 20 | `0.0000` |
| `sina[35]` | constant_zero | 40/40/0/1 | 20 | `0` |
| `event_dc.PREDICT_RAISE_FUNDS` | constant_zero | 129/129/0/1 | 18 | `0` |
| `ulist239.f120` | constant_zero | 160/160/0/1 | 8 | `0` |
| `ulist239.f125` | constant_zero | 160/160/0/1 | 8 | `0` |
| `ulist239.f126` | constant_zero | 160/160/0/1 | 8 | `0` |
| `ulist239.f137` | constant_zero | 160/160/0/1 | 8 | `0.0` |
| `ulist239.f138` | constant_zero | 160/160/0/1 | 8 | `0.0` |
| `ulist239.f194` | constant_zero | 160/160/0/1 | 8 | `0` |
| `ulist239.f216` | constant_zero | 160/160/0/1 | 8 | `0` |
| `ulist239.f223` | constant_zero | 160/160/0/1 | 8 | `0` |
| `push2.f123` | constant_zero | 214/214/0/1 | 12 | `0.0` |
| `push2.f124` | constant_zero | 214/214/0/1 | 12 | `0.0` |
| `push2.f125` | constant_zero | 214/214/0/1 | 12 | `0.0` |
| `push2.f134` | constant_zero | 214/214/0/1 | 12 | `0` |
| `event_dc.OPEN_CHANGERATE` | constant_zero | 357/357/0/1 | 18 | `0` |
| `event_dc.IS_1YEAR` | constant_zero | 360/360/0/1 | 18 | `0` |
| `event_dc.IS_1YEAR_APPLY` | constant_zero | 360/360/0/1 | 18 | `0` |
| `event_dc.IS_BALLOT_NUM` | constant_zero | 360/360/0/1 | 18 | `0` |
| `event_dc.IS_BEIJING` | constant_zero | 360/360/0/1 | 18 | `0` |
| `event_dc.IS_CALENDAR_DATA` | constant_zero | 360/360/0/1 | 18 | `0` |
| `event_dc.IS_PROFIT` | constant_zero | 360/360/0/1 | 18 | `0` |
| `event_dc.IS_REGISTRATION` | constant_zero | 360/360/0/1 | 18 | `0` |
| `event_dc.IS_REGISTRATION_NEW` | constant_zero | 360/360/0/1 | 18 | `0` |
| `event_dc.IS_UNOPEN` | constant_zero | 360/360/0/1 | 18 | `0` |
| `event_dc.PREDICT_ISSUE_PRICE` | constant_zero | 360/360/0/1 | 18 | `0` |
| `event_dc.PREDICT_ISSUE_PRICE2` | constant_zero | 360/360/0/1 | 18 | `0` |
| `tencent[29]` | all_missing_or_blank | 400/0/400/0 | 20 | `` |
| `tencent[55]` | all_missing_or_blank | 400/0/400/0 | 20 | `` |
| `kpl.raw_columns.col_03` | all_missing_or_blank | 1165/0/1165/0 | 19 | `` |
| `market_sources.reason` | constant_value | 2/2/0/1 | 2 | `candidate_sample_already_exists_for_data_date` |
| `market_sources.request_params.days` | constant_value | 2/2/0/1 | 2 | `4` |
| `market_sources.request_params.fetch_all` | constant_value | 2/2/0/1 | 2 | `false` |
| `market_sources.request_params.zs_type` | constant_value | 2/2/0/1 | 2 | `7` |
| `market_sources.request_params.kline_type` | constant_value | 3/3/0/1 | 3 | `daily` |
| `market_sources.request_params.limit` | constant_value | 3/3/0/1 | 3 | `5` |
| `market_sources.request_params.stock_code` | constant_value | 6/6/0/1 | 6 | `000007` |
| `market_sources.stock_code` | constant_value | 6/6/0/1 | 6 | `000007` |
| `eltdx.limit_ladder.limit_status` | constant_value | 14/14/0/1 | 11 | `sealed` |
| `eltdx.category` | constant_value | 20/20/0/1 | 20 | `沪深A股` |
| `eltdx.sort_by` | constant_value | 20/20/0/1 | 20 | `涨幅` |
| `market_sources.expected_package_version` | constant_value | 20/20/0/1 | 20 | `0.1.8` |
| `market_sources.package` | constant_value | 20/20/0/1 | 20 | `levistock` |
| `market_sources.package_version` | constant_value | 20/20/0/1 | 20 | `0.1.8` |
| `market_sources.version_matches_requirement` | constant_value | 20/20/0/1 | 20 | `true` |
| `reports.orgType` | constant_value | 20/20/0/1 | 14 | `white` |

_显示前 50 / 共 141 项；完整清单在 JSON。_

日期值候选 7 项；应先查官方定义和完整路径，再确定上市日、记录更新日、报告期、公告/事件日、生效日或来源数据日。

### 日期形状字段待核业务含义

| 完整字段路径 | 日期样本比例 | 编码 | 样本键日期数 | 日期值/来源日/样本日/股票样例 |
|:--|--:|:--|--:|:--|
| `etf.date` | 100.0% | YYYY-MM-DD | 19 | 2026-10-15(来源日=20261015;样本日=T:20261015;股票=158000), 2026-10-15(来源日=20261015;样本日=T:20261015;股票=158001), 2026-10-15(来源日=20261015;样本日=T:20261015;股票=158003), 2026-10-15(来源日=20261015;样本日=T:20261015;股票=158005), 2026-10-15(来源日=20261015;样本日=T:20261015;股票=158006) |
| `etf.listing_date` | 100.0% | YYYY-MM-DD | 19 | 2026-08-26(来源日=20261015;样本日=T:20261015;股票=158000), 2026-08-27(来源日=20261015;样本日=T:20261015;股票=158001), 2026-08-19(来源日=20261015;样本日=T:20261015;股票=158003), 2026-08-24(来源日=20261015;样本日=T:20261015;股票=158005), 2026-08-07(来源日=20261015;样本日=T:20261015;股票=158006) |
| `research_sina.date` | 100.0% | YYYY-MM-DD | 28 | 2026-10-16(来源日=20261016;样本日=C:20261016;股票=__0), 2026-10-16(来源日=20261016;样本日=C:20261016;股票=__1), 2026-10-16(来源日=20261016;样本日=C:20261016;股票=__10), 2026-10-16(来源日=20261016;样本日=C:20261016;股票=__11), 2026-10-16(来源日=20261016;样本日=C:20261016;股票=__12) |
| `news_wscn_cctv.date` | 100.0% | YYYY-MM-DD | 17 | 2026-10-15(来源日=20261015;样本日=C:20261015;股票=__0), 2026-10-15(来源日=20261015;样本日=C:20261015;股票=__1), 2026-10-15(来源日=20261015;样本日=C:20261015;股票=__10), 2026-10-15(来源日=20261015;样本日=C:20261015;股票=__11), 2026-10-15(来源日=20261015;样本日=C:20261015;股票=__12) |
| `market_sources.data_date` | 100.0% | YYYY-MM-DD | 20 | 2026-10-15(来源日=20261015;样本日=T:20261015;股票=levistock_daily_candidate), 2026-10-16(来源日=20261016;样本日=T:20261016;股票=levistock_daily_candidate), 2026-10-19(来源日=20261019;样本日=T:20261019;股票=000007), 2026-10-20(来源日=20261020;样本日=T:20261020;股票=000007), 2026-10-21(来源日=20261021;样本日=T:20261021;股票=levistock_daily_candidate) |
| `market_sources.requested_trade_date` | 100.0% | YYYY-MM-DD | 20 | 2026-10-15(来源日=20261015;样本日=T:20261015;股票=kph_limit_ladder), 2026-10-16(来源日=20261016;样本日=T:20261016;股票=kph_limit_ladder), 2026-10-19(来源日=20261019;样本日=T:20261019;股票=kph_limit_ladder), 2026-10-20(来源日=20261020;样本日=T:20261020;股票=kph_limit_ladder), 2026-10-21(来源日=20261021;样本日=T:20261021;股票=kph_limit_ladder) |
| `market_sources.request_params.date` | 100.0% | YYYY-MM-DD | 5 | 2026-10-15(来源日=20261015;样本日=T:20261015;股票=levistock_daily_candidate), 2026-10-23(来源日=20261023;样本日=T:20261023;股票=levistock_daily_candidate), 2026-10-28(来源日=20261028;样本日=T:20261028;股票=levistock_daily_candidate), 2026-11-04(来源日=20261104;样本日=T:20261104;股票=levistock_daily_candidate), 2026-11-17(来源日=20261117;样本日=T:20261117;股票=levistock_daily_candidate) |

## 候选身份与人工审阅状态

- 候选身份：生成 806 条，唯一候选 806 个，重复身份 0，无效身份 0。
- 审阅台账：可用；当前状态 `pending`；已审 1，待处理 805，覆盖率 0.1%。
- 重复归并组：0；每个成员均保留到代表候选的反向追溯。
- 处置计数：`accepted_for_adjudication` 0；`duplicate_grouped` 0；`insufficient_evidence` 0；`needs_external_evidence` 1；`rejected` 0；`unreviewed` 805。
- `accepted_for_adjudication` 只表示可进入现有证据裁决流程；审阅台账不会修改主字典或字段注册表。

## 报告完整性与审阅范围

- 机器可读完整性：`complete`；方法候选生成 804 条，完整明细保存 804 条，缺失 0 条，多余 0 条，重复 0 条，身份无效 0 条。
- 全量方法候选位于同名 JSON 的 `method_candidate_inventory`；Markdown 的 Top-N 表格是导航摘要，不能代替全量 JSON 审阅。
- 候选审阅数据对账：`complete`；唯一候选 806 个，审阅 1 个，待处理 805 个；人工审阅进度与机器清单完整性分别统计。
- Markdown 未逐行展示、但 JSON 保留的部分：
  - `method_candidates`：展示 100 / 500，摘要省略 400 条。
  - `method_candidate_inventory`：展示 0 / 804，摘要省略 804 条。
  - `candidate_triage.targets`：展示 50 / 138，摘要省略 88 条。
  - `candidate_triage.low_information_fields`：展示 50 / 141，摘要省略 91 条。
  - `diagnostics`：展示 100 / 368，摘要省略 268 条。
  - `candidate_review.human_review.reviewed_candidates`：展示 0 / 1，摘要省略 1 条。
- 完整性对账通过；逐目标复核仍须覆盖 JSON 的全部明细，并为每项记录已检查、重复归并、证据不足或需外部核验的处置。
