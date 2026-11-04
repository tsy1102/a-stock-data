# 全源对撞报告（20261104）

> 交易数据窗口配置：近 7 个交易日（`--window`）
> 行情窗口：20261026 ~ 20261104（7 个不同交易日）｜字段 1296 个｜样本值 580814 条
> 新闻/公告自然日窗口：20261029 ~ 20261104
> 主攻目标（unverified）=339｜可审定新候选=0｜首次发现新候选对=0｜已登记关系复验=2｜异号同义 0 / 同号镜像 0

> **规则**：L1 每日需≥18 组有效配对，并至少有5 组信息配对；双方同时为 0 或同时缺失不计命中率，一侧为 0、另一侧非 0 按失配计。信息配对命中率≥90%，且覆盖至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。JSON `daily_sample_counts` 与 `daily_informative_sample_counts`分别保留每日有效配对数和 L1 信息配对数。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 新候选 — 异号同义（跨编号，高价值）(0)

_本轮无异号同义候选。_


## 二、L1 / L1-U 新候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、已登记映射的本窗口复验（2）

_这些关系已在主注册表登记，只用于观察当前样本是否仍支持既有映射；它们不是新的未知字段候选，也不能再次提交为新定案。_

| 左字段 | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|
| `zhb.full.change_pct` | `tencent[32]` | L1 | 100.00% | 4 | 80 | 80 | - |  | ✅ |
| `zhb.full.high_52w` | `tencent[67]` | L1 | 95.00% | 4 | 80 | 80 | - |  | ✅ |

## 四、L4 存疑候选（92）

| 左字段 | 右字段 | 命中率 | 天数 | 样本 |
|:--|:--|--:|--:|--:|
| `axdata.data.instrument_id` | `ftshare_rest.symbol` | 100.00% | 7 | 139 |
| `axdata.data.open_price` | `ftshare_rest.open` | 100.00% | 7 | 139 |
| `axdata.data.pre_close` | `ftshare_rest.prev_close` | 100.00% | 7 | 139 |
| `tdx.quote_raw.price` | `ftshare_rest.close` | 100.00% | 7 | 139 |
| `tdx.quote_raw.price` | `fuyao.snapshot.last_price` | 100.00% | 6 | 119 |
| `tdx.quote_raw.price` | `push2.f43` | 100.00% | 5 | 87 |
| `tdx.quote_raw.price` | `push2.f179` | 100.00% | 5 | 87 |
| `tdx.quote_raw.price` | `sina[3]` | 100.00% | 7 | 139 |
| `tdx.quote_raw.price` | `tencent[3]` | 100.00% | 7 | 139 |
| `tdx.quote_raw.price` | `ulist239.f2` | 100.00% | 3 | 59 |
| `tdx.quote_raw.bid1` | `sina[6]` | 100.00% | 7 | 139 |
| `tdx.quote_raw.bid1` | `sina[11]` | 100.00% | 7 | 139 |
| `tdx.quote_raw.bid1` | `tencent[9]` | 100.00% | 7 | 139 |
| `tdx.quote_raw.ask1` | `sina[7]` | 100.00% | 7 | 139 |
| `tdx.quote_raw.ask1` | `sina[21]` | 100.00% | 7 | 139 |
| `tdx.quote_raw.ask1` | `tencent[19]` | 100.00% | 7 | 139 |
| `ulist239.f144` | `eltdx.quote_snapshot.last_price` | 100.00% | 3 | 60 |
| `ulist239.f144` | `ftshare_rest.close` | 100.00% | 3 | 60 |
| `ulist239.f144` | `fuyao.snapshot.last_price` | 100.00% | 3 | 60 |
| `ulist239.f144` | `sina[3]` | 100.00% | 3 | 60 |
| `ulist239.f144` | `tdx.quote_full.price` | 100.00% | 3 | 59 |
| `ulist239.f144` | `tencent[3]` | 100.00% | 3 | 60 |
| `zhb.full.change_pct` | `push2.f170` | 100.00% | 2 | 40 |
| `zhb.full.change_pct` | `ulist239.f3` | 100.00% | 2 | 40 |
| `push2.f174` | `zhb.stat2.high_52w` | 90.00% | 2 | 40 |
| `zhb.full.change_ytd` | `push2.f122` | 90.00% | 2 | 40 |
| `zhb.full.other_qy_jzc` | `ulist239.f190` | 90.00% | 2 | 40 |
| `zhb.full.other_qy_jzc` | `ulist239.f231` | 90.00% | 2 | 40 |
| `push2.f174` | `tencent[67]` | 88.64% | 5 | 88 |
| `push2.f192` | `tencent[50]` | 84.09% | 5 | 88 |
| `zhb.full.other_qy_jzc` | `ulist239.f200` | 80.00% | 2 | 40 |
| `sina_extended.trade` | `fuyao.snapshot.last_price` | 78.33% | 6 | 120 |
| `zhb.full.dividend_yield` | `tencent[64]` | 77.50% | 4 | 80 |
| `sina_extended.trade` | `eltdx.quote_snapshot.last_price` | 77.14% | 7 | 140 |
| `sina_extended.trade` | `ftshare_rest.close` | 77.14% | 7 | 140 |
| `sina_extended.trade` | `tencent[3]` | 77.14% | 7 | 140 |
| `sina_extended.trade` | `tdx.quote_full.price` | 76.98% | 7 | 139 |
| `ulist239.f11` | `tencent[80]` | 76.67% | 3 | 60 |
| `sina_extended.trade` | `push2.f43` | 72.73% | 5 | 88 |
| `sina_extended.trade` | `push2.f179` | 72.73% | 5 | 88 |
| `zhb.full.change_ytd` | `tencent[62]` | 71.25% | 4 | 80 |
| `ulist239.f133` | `zhb.stat.dividend_yield` | 70.00% | 2 | 40 |
| `sina_extended.trade` | `ulist239.f2` | 68.33% | 3 | 60 |
| `zhb.full.change_250k_bar` | `tencent[79]` | 66.25% | 4 | 80 |
| `tdx.quote_raw.ask1` | `push2.f43` | 62.07% | 5 | 87 |
| `tdx.quote_raw.ask1` | `push2.f179` | 62.07% | 5 | 87 |
| `push2.f191` | `tencent[74]` | 61.36% | 5 | 88 |
| `ulist239.f13` | `zhb.stat.other_qy_jzc` | 60.00% | 2 | 40 |
| `ulist239.f27` | `zhb.stat.other_qy_jzc` | 60.00% | 2 | 40 |
| `zhb.full.other_qy_jzc` | `push2.f107` | 60.00% | 2 | 40 |
| `zhb.full.other_qy_jzc` | `push2.f110` | 60.00% | 2 | 40 |
| `ulist239.f13` | `tdx.finance_info.hgu` | 59.32% | 3 | 59 |
| `ulist239.f27` | `tdx.finance_info.hgu` | 59.32% | 3 | 59 |
| `ulist239.f97` | `eltdx.quote_snapshot.unknown_after_outer_raw` | 56.67% | 3 | 60 |
| `ulist239.f97` | `tdx.finance_info.hgu` | 55.93% | 3 | 59 |
| `ulist239.f133` | `tencent[64]` | 55.00% | 3 | 60 |
| `tdx.quote_raw.ask1` | `ulist239.f2` | 54.24% | 3 | 59 |
| `ulist239.f97` | `tdx.finance_info.bgu` | 54.24% | 3 | 59 |
| `ulist239.f144` | `tdx.quote_full.ask1` | 54.24% | 3 | 59 |
| `ulist239.f144` | `sina[7]` | 53.33% | 3 | 60 |

_（仅显示前 60 / 共 92）_

## 五、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 六、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `sina_extended.turnover` | `ftshare_rest.turnover_rate` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, sina_extended | Pearson=0.9997, Spearman=0.9964, LOO稳号=True |
| `zhb.full.high_52w` | `ftshare_rest.high` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 80 | T:20261028, T:20261030, T:20261102, T:20261103 | ftshare_rest, zhb | Pearson=0.9987, Spearman=0.9165, LOO稳号=True |
| `fuyao.valuation.pe_ttm` | `zhb.stat.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 80 | T:20261028, T:20261030, T:20261102, T:20261103 | fuyao, zhb | Pearson=0.9957, Spearman=0.998, LOO稳号=True |
| `fuyao.valuation.pe_ttm` | `zhb.full.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 80 | T:20261028, T:20261030, T:20261102, T:20261103 | fuyao, zhb | Pearson=0.9957, Spearman=0.998, LOO稳号=True |
| `tencent[27]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8603, LOO稳号=True |
| `tencent[27]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8738, LOO稳号=True |
| `tencent[27]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8687, LOO稳号=True |
| `tencent[27]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9997, Spearman=0.8673, LOO稳号=True |
| `tencent[27]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8745, LOO稳号=True |
| `tencent[27]` | `sina[11]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8603, LOO稳号=True |
| `tencent[27]` | `ftshare_rest.open` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8745, LOO稳号=True |
| `tencent[27]` | `ftshare_rest.low` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8738, LOO稳号=True |
| `tencent[27]` | `ftshare_rest.high` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8687, LOO稳号=True |
| `tencent[27]` | `ftshare_rest.close` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9997, Spearman=0.8673, LOO稳号=True |
| `tencent[27]` | `ftshare_rest.avg` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8688, LOO稳号=True |
| `tencent[27]` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9996, Spearman=0.8745, LOO稳号=True |
| `tencent[27]` | `eltdx.quote_snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9996, Spearman=0.8745, LOO稳号=True |
| `tencent[27]` | `eltdx.quote_snapshot.low_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9996, Spearman=0.8738, LOO稳号=True |
| `tencent[27]` | `eltdx.quote_snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9997, Spearman=0.8673, LOO稳号=True |
| `tencent[27]` | `eltdx.quote_snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9996, Spearman=0.8687, LOO稳号=True |
| `tencent[25]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[25]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8603, LOO稳号=True |
| `tencent[25]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8738, LOO稳号=True |
| `tencent[25]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8687, LOO稳号=True |
| `tencent[25]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9997, Spearman=0.8673, LOO稳号=True |
| `tencent[25]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[25]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8745, LOO稳号=True |
| `tencent[25]` | `sina[11]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8603, LOO稳号=True |
| `tencent[25]` | `ftshare_rest.open` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8745, LOO稳号=True |
| `tencent[25]` | `ftshare_rest.low` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8738, LOO稳号=True |
| `tencent[25]` | `ftshare_rest.high` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8687, LOO稳号=True |
| `tencent[25]` | `ftshare_rest.close` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9997, Spearman=0.8673, LOO稳号=True |
| `tencent[25]` | `ftshare_rest.avg` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8688, LOO稳号=True |
| `tencent[25]` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9996, Spearman=0.8745, LOO稳号=True |
| `tencent[25]` | `eltdx.quote_snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9996, Spearman=0.8745, LOO稳号=True |
| `tencent[25]` | `eltdx.quote_snapshot.low_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9996, Spearman=0.8738, LOO稳号=True |
| `tencent[25]` | `eltdx.quote_snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9997, Spearman=0.8673, LOO稳号=True |
| `tencent[25]` | `eltdx.quote_snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9996, Spearman=0.8687, LOO稳号=True |
| `tencent[23]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[23]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8603, LOO稳号=True |
| `tencent[23]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8738, LOO稳号=True |
| `tencent[23]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8687, LOO稳号=True |
| `tencent[23]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9997, Spearman=0.8673, LOO稳号=True |
| `tencent[23]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[23]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8745, LOO稳号=True |
| `tencent[23]` | `sina[11]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8603, LOO稳号=True |
| `tencent[23]` | `ftshare_rest.open` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8745, LOO稳号=True |
| `tencent[23]` | `ftshare_rest.low` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8738, LOO稳号=True |
| `tencent[23]` | `ftshare_rest.high` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8687, LOO稳号=True |
| `tencent[23]` | `ftshare_rest.close` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9997, Spearman=0.8673, LOO稳号=True |
| `tencent[23]` | `ftshare_rest.avg` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8688, LOO稳号=True |
| `tencent[23]` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9996, Spearman=0.8745, LOO稳号=True |
| `tencent[23]` | `eltdx.quote_snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9996, Spearman=0.8745, LOO稳号=True |
| `tencent[23]` | `eltdx.quote_snapshot.low_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9996, Spearman=0.8738, LOO稳号=True |
| `tencent[23]` | `eltdx.quote_snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9997, Spearman=0.8673, LOO稳号=True |
| `tencent[23]` | `eltdx.quote_snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9996, Spearman=0.8687, LOO稳号=True |
| `tencent[22]` | `sina[22]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[21]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[21]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8603, LOO稳号=True |
| `tencent[21]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8738, LOO稳号=True |
| `tencent[21]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8688, LOO稳号=True |
| `tencent[21]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9997, Spearman=0.8673, LOO稳号=True |
| `tencent[21]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[21]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8745, LOO稳号=True |
| `tencent[21]` | `sina[11]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8603, LOO稳号=True |
| `tencent[21]` | `ftshare_rest.open` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8745, LOO稳号=True |
| `tencent[21]` | `ftshare_rest.low` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8738, LOO稳号=True |
| `tencent[21]` | `ftshare_rest.high` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8688, LOO稳号=True |
| `tencent[21]` | `ftshare_rest.close` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9997, Spearman=0.8673, LOO稳号=True |
| `tencent[21]` | `ftshare_rest.avg` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8689, LOO稳号=True |
| `tencent[21]` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9996, Spearman=0.8745, LOO稳号=True |
| `tencent[21]` | `eltdx.quote_snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9996, Spearman=0.8745, LOO稳号=True |
| `tencent[21]` | `eltdx.quote_snapshot.low_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9996, Spearman=0.8738, LOO稳号=True |
| `tencent[21]` | `eltdx.quote_snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9997, Spearman=0.8673, LOO稳号=True |
| `tencent[21]` | `eltdx.quote_snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9996, Spearman=0.8688, LOO稳号=True |
| `tencent[20]` | `sina[20]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[17]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8602, LOO稳号=True |
| `tencent[17]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[17]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9999, Spearman=0.9903, LOO稳号=True |
| `tencent[17]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=1.0, Spearman=0.9917, LOO稳号=True |
| `tencent[17]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=1.0, Spearman=0.9927, LOO稳号=True |
| `tencent[17]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8602, LOO稳号=True |
| `tencent[17]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9998, Spearman=0.9897, LOO稳号=True |
| `tencent[17]` | `sina[11]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[17]` | `ftshare_rest.open` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9998, Spearman=0.9897, LOO稳号=True |
| `tencent[17]` | `ftshare_rest.low` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=0.9999, Spearman=0.9903, LOO稳号=True |
| `tencent[17]` | `ftshare_rest.high` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=1.0, Spearman=0.9917, LOO稳号=True |
| `tencent[17]` | `ftshare_rest.close` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=1.0, Spearman=0.9927, LOO稳号=True |
| `tencent[17]` | `ftshare_rest.avg` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | ftshare_rest, tencent | Pearson=1.0, Spearman=0.992, LOO稳号=True |
| `tencent[17]` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9998, Spearman=0.9897, LOO稳号=True |
| `tencent[17]` | `eltdx.quote_snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9998, Spearman=0.9897, LOO稳号=True |
| `tencent[17]` | `eltdx.quote_snapshot.low_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=0.9999, Spearman=0.9903, LOO稳号=True |
| `tencent[17]` | `eltdx.quote_snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=1.0, Spearman=0.9927, LOO稳号=True |
| `tencent[17]` | `eltdx.quote_snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | eltdx, tencent | Pearson=1.0, Spearman=0.9917, LOO稳号=True |
| `tencent[15]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9996, Spearman=0.8603, LOO稳号=True |
| `tencent[15]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[15]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=0.9999, Spearman=0.9904, LOO稳号=True |
| `tencent[15]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | sina, tencent | Pearson=1.0, Spearman=0.9918, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 七、日期与数据质量告警（139）

- 20261017: 旧式非交易日目录按前一交易日 20261016 归并；目录未改名
- 20261018: 旧式非交易日目录按前一交易日 20261016 归并；目录未改名
- 20261031: 旧式非交易日目录按前一交易日 20261030 归并；目录未改名
- 20261101: 旧式非交易日目录按前一交易日 20261030 归并；目录未改名
- 20261026/zhb: 采集状态 partial
- 20261026/push2: 采集状态 partial
- 20261026/axdata: 采集状态 partial
- 20261026/market_sources: 采集状态 partial
- 20261026/em_kline_f61: 采集状态 partial
- 20261026/em_fund_flow: 采集状态 partial
- 20261026/ulist239: 采集状态 failed
- 20261026/clist: 采集状态 partial
- 20261026/slist: 采集状态 failed
- 20261026/st_list: 采集状态 partial
- 20261026/axdata: 来源状态为 partial，样本按部分快照参与
- 20261026/clist: 来源状态为 partial，样本按部分快照参与
- 20261026/clist: 没有可用记录，快照跳过
- 20261026/em_fund_flow: 来源状态为 partial，样本按部分快照参与
- 20261026/em_fund_flow: 没有可用记录，快照跳过
- 20261026/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20261026/em_kline_f61: 没有可用记录，快照跳过
- 20261026/kph: 来源有效交易日 20261023 不在本轮行情交易日窗口，快照跳过
- 20261026/market_sources: 来源状态为 partial，样本按部分快照参与
- 20261026/push2: 来源状态为 partial，样本按部分快照参与
- 20261026/slist: 来源状态为 failed，快照跳过
- 20261026/st_list: 来源状态为 partial，样本按部分快照参与
- 20261026/st_list: 没有可用记录，快照跳过
- 20261026/tdx_f10: 没有可用记录，快照跳过
- 20261026/tdx_f10_more: 没有可用记录，快照跳过
- 20261026/ulist239: 来源状态为 failed，快照跳过
- 20261026/zhb: 来源状态为 partial，样本按部分快照参与
- 20261026/zhb: 来源有效交易日 20261023 不在本轮行情交易日窗口，快照跳过
- 20261028/zhb: 采集状态 partial
- 20261028/push2: 采集状态 failed
- 20261028/em_kline_f61: 采集状态 partial
- 20261028/em_fund_flow: 采集状态 partial
- 20261028/ulist239: 采集状态 failed
- 20261028/clist: 采集状态 partial
- 20261028/slist: 采集状态 failed
- 20261028/st_list: 采集状态 partial
- 20261028/clist: 来源状态为 partial，样本按部分快照参与
- 20261028/clist: 没有可用记录，快照跳过
- 20261028/em_fund_flow: 来源状态为 partial，样本按部分快照参与
- 20261028/em_fund_flow: 没有可用记录，快照跳过
- 20261028/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20261028/em_kline_f61: 没有可用记录，快照跳过
- 20261028/kph: 来源有效交易日 20261027 不在本轮行情交易日窗口，快照跳过
- 20261028/push2: 来源状态为 failed，快照跳过
- 20261028/slist: 来源状态为 failed，快照跳过
- 20261028/st_list: 来源状态为 partial，样本按部分快照参与
- 20261028/st_list: 没有可用记录，快照跳过
- 20261028/tdx_f10: 没有可用记录，快照跳过
- 20261028/tdx_f10_more: 没有可用记录，快照跳过
- 20261028/ulist239: 来源状态为 failed，快照跳过
- 20261028/zhb: 来源状态为 partial，样本按部分快照参与
- 20261028/zhb: 来源有效交易日 20261027 不在本轮行情交易日窗口，快照跳过
- 20261029/zhb: 采集状态 partial
- 20261029/push2: 采集状态 partial
- 20261029/em_kline_f61: 采集状态 partial
- 20261029/em_fund_flow: 采集状态 partial
- 20261029/ulist239: 采集状态 failed
- 20261029/clist: 采集状态 partial
- 20261029/slist: 采集状态 failed
- 20261029/st_list: 采集状态 partial
- 20261029/clist: 来源状态为 partial，样本按部分快照参与
- 20261029/clist: 没有可用记录，快照跳过
- 20261029/em_fund_flow: 来源状态为 partial，样本按部分快照参与
- 20261029/em_fund_flow: 没有可用记录，快照跳过
- 20261029/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20261029/em_kline_f61: 没有可用记录，快照跳过
- 20261029/push2: 来源状态为 partial，样本按部分快照参与
- 20261029/slist: 来源状态为 failed，快照跳过
- 20261029/st_list: 来源状态为 partial，样本按部分快照参与
- 20261029/st_list: 没有可用记录，快照跳过
- 20261029/tdx_f10: 没有可用记录，快照跳过
- 20261029/tdx_f10_more: 没有可用记录，快照跳过
- 20261029/ulist239: 来源状态为 failed，快照跳过
- 20261029/zhb: 来源状态为 partial，样本按部分快照参与
- 20261030/push2: 采集状态 failed
- 20261030/em_kline_f61: 采集状态 partial
- 20261030/em_fund_flow: 采集状态 partial
- 20261030/ulist239: 采集状态 failed
- 20261030/clist: 采集状态 partial
- 20261030/slist: 采集状态 failed
- 20261030/st_list: 采集状态 partial
- 20261030/clist: 来源状态为 partial，样本按部分快照参与
- 20261030/clist: 没有可用记录，快照跳过
- 20261030/em_fund_flow: 来源状态为 partial，样本按部分快照参与
- 20261030/em_fund_flow: 没有可用记录，快照跳过
- 20261030/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20261030/em_kline_f61: 没有可用记录，快照跳过
- 20261030/push2: 来源状态为 failed，快照跳过
- 20261030/slist: 来源状态为 failed，快照跳过
- 20261030/st_list: 来源状态为 partial，样本按部分快照参与
- 20261030/st_list: 没有可用记录，快照跳过
- 20261030/tdx_f10: 没有可用记录，快照跳过
- 20261030/tdx_f10_more: 没有可用记录，快照跳过
- 20261030/ulist239: 来源状态为 failed，快照跳过
- 20261102/zhb: 采集状态 partial
- 20261102/tdx_f10: 没有可用记录，快照跳过
- 另有 39 条告警，详见同名 JSON 报告。

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

策略状态：`ok`；逐源分类字段 13，保守默认未分类字段 1283。L1/L1-C 日期证据：来源日期已确认 2 条，仅语义证据且日期未确认 0 条，其他日期未确认 0 条。

_本轮 L1/L1-C 没有仅凭静态或缓变字段、且来源日期未确认的关系。_

## 来源字段覆盖与碰撞参与

_窗口字段值样本是经日期筛选、重复折叠和快照择优后载入的非空值；右侧比较次数另受字段类型及来源规则筛选。官方契约字段须有逐字段审定证据，契约语义本身不证明底层数据来源独立。_

| 来源 | 已确认字段 | 契约已确认 | 契约锚 | 独立锚 | L1-C 锚 | 窗口字段 / 字段值样本 / 交易日 |
|:--|--:|--:|--:|--:|--:|--:|
| axdata | 0 | 0 | 0 | 0 | 0 | 34 / 3722 / 7 |
| clist | 18 | 0 | 0 | 18 | 0 | 33 / 21501 / 3 |
| cls | 4 | 0 | 0 | 4 | 0 | 5 / 1250 / 0 |
| datacenter | 41 | 0 | 0 | 41 | 0 | 0 / 0 / 0 |
| eltdx | 64 | 0 | 0 | 64 | 0 | 116 / 7770 / 7 |
| em_fund_flow | 0 | 0 | 0 | 0 | 0 | 15 / 900 / 3 |
| em_hot | 39 | 0 | 0 | 39 | 0 | 0 / 0 / 0 |
| em_kline_f61 | 10 | 0 | 0 | 10 | 0 | 2 / 120 / 3 |
| etf | 0 | 0 | 0 | 0 | 0 | 9 / 81804 / 7 |
| event_dc | 0 | 0 | 0 | 0 | 0 | 148 / 216065 / 7 |
| exchange | 4 | 0 | 0 | 4 | 0 | 0 / 0 / 0 |
| ftshare | 6 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| ftshare_rest | 31 | 31 | 31 | 0 | 31 | 32 / 4445 / 7 |
| fuyao | 85 | 71 | 71 | 85 | 0 | 20 / 2420 / 7 |
| kph | 6 | 0 | 0 | 6 | 0 | 15 / 2775 / 4 |
| kpl | 6 | 0 | 0 | 6 | 0 | 28 / 17102 / 7 |
| market_sources | 14 | 0 | 0 | 0 | 0 | 73 / 59015 / 7 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 2 / 94 / 0 |
| push2 | 39 | 0 | 0 | 39 | 0 | 114 / 10032 / 5 |
| push2ex | 21 | 0 | 0 | 21 | 0 | 16 / 11264 / 7 |
| reports | 26 | 0 | 0 | 26 | 0 | 49 / 539 / 0 |
| research_sina | 0 | 0 | 0 | 0 | 0 | 6 / 1752 / 0 |
| sina | 19 | 0 | 0 | 19 | 0 | 39 / 4830 / 7 |
| sina_extended | 0 | 0 | 0 | 0 | 0 | 4 / 560 / 7 |
| slist | 5 | 0 | 0 | 5 | 0 | 1 / 60 / 3 |
| sse_e_interaction | 0 | 0 | 0 | 0 | 0 | 8 / 400 / 0 |
| st_list | 0 | 0 | 0 | 0 | 0 | 6 / 5954 / 3 |
| tdx | 80 | 0 | 0 | 80 | 0 | 62 / 8896 / 7 |
| tencent | 62 | 0 | 0 | 62 | 0 | 88 / 12306 / 7 |
| ulist239 | 44 | 0 | 0 | 44 | 0 | 239 / 14340 / 3 |
| zhb | 85 | 0 | 0 | 85 | 0 | 124 / 8800 / 4 |

| 来源 | 破解目标 | 比较字段 | 作目标比较 | 作右侧比较 | L1-C 锚比较 | L1 / L1-C / L4 关系 | 方法候选涉及 |
|:--|--:|--:|--:|--:|--:|--:|--:|
| axdata | 30 | 0 | 627 | 0 | 0 | 0 / 0 / 3 | 76 |
| clist | 11 | 16 | 2614 | 2400 | 0 | 0 / 0 / 0 | 0 |
| cls | 2 | 0 | 376 | 0 | 0 | 0 / 0 / 0 | 0 |
| datacenter | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| eltdx | 30 | 50 | 5970 | 6055 | 0 | 0 / 0 / 5 | 446 |
| em_fund_flow | 4 | 0 | 1040 | 0 | 0 | 0 / 0 / 0 | 175 |
| em_hot | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| em_kline_f61 | 1 | 0 | 260 | 0 | 0 | 0 / 0 / 0 | 13 |
| etf | 4 | 0 | 29 | 0 | 0 | 0 / 0 / 0 | 0 |
| event_dc | 61 | 0 | 1235 | 0 | 0 | 0 / 0 / 0 | 337 |
| exchange | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare_rest | 1 | 25 | 23 | 7125 | 7125 | 0 / 0 / 8 | 994 |
| fuyao | 4 | 10 | 1376 | 2180 | 0 | 0 / 0 / 5 | 518 |
| kph | 4 | 6 | 1066 | 1314 | 0 | 0 / 0 / 0 | 12 |
| kpl | 15 | 6 | 4810 | 2496 | 0 | 0 / 0 / 0 | 39 |
| market_sources | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| push2 | 18 | 34 | 3696 | 4671 | 0 | 0 / 0 / 15 | 1153 |
| push2ex | 10 | 2 | 2600 | 300 | 0 | 0 / 0 / 0 | 33 |
| reports | 11 | 6 | 2122 | 757 | 0 | 0 / 0 / 0 | 0 |
| research_sina | 2 | 0 | 358 | 0 | 0 | 0 / 0 / 0 | 0 |
| sina | 14 | 18 | 4746 | 3105 | 0 | 0 / 0 / 16 | 1350 |
| sina_extended | 3 | 0 | 1017 | 0 | 0 | 0 / 0 / 10 | 170 |
| slist | 1 | 0 | 260 | 0 | 0 | 0 / 0 / 0 | 6 |
| sse_e_interaction | 2 | 0 | 25 | 0 | 0 | 0 / 0 / 0 | 0 |
| st_list | 3 | 0 | 48 | 0 | 0 | 0 / 0 / 0 | 0 |
| tdx | 15 | 42 | 3604 | 5586 | 0 | 0 / 0 / 42 | 1046 |
| tencent | 22 | 56 | 6360 | 10512 | 0 | 2 / 0 / 22 | 2219 |
| ulist239 | 25 | 44 | 6254 | 6028 | 0 | 0 / 0 / 40 | 1164 |
| zhb | 44 | 55 | 9328 | 7315 | 0 | 2 / 0 / 18 | 1831 |

## AxData 每日接口核验

> 此处汇总采集目录已保存的本地证据，不发起网络请求、不改变注册表状态；AxData 是多源框架，不作为独立字段锚。

### AxData

窗口内有 7 个唯一数据日的轮验记录；重复目录合并 0 条。
静态接口队列：257 个接口，3343 个字段出现项，低于 E3 的字段出现项 3343；当前主动探针白名单 `tencent_realtime_snapshot`。
静态候选策略：static review only until route, parameters, date basis, and request safety are approved。

| 数据日 | 轮验状态 | 探针状态 / 请求数 | 来源身份状态 | 短线配对 | KPH/KPL 配对 | 证据文件 |
|:--|:--|:--|:--|--:|--:|:--|
| 20261026 | already_recorded | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | — | — | full |
| 20261028 | sampled | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261029 | sampled | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261030 | already_recorded | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | 44 | full |
| 20261102 | sampled | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261103 | sampled | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261104 | sampled | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |

被动逐字段比较中的差异计数（跨本窗口唯一数据日累加，不含原始值）：

| 比较路径 | 相同 | 不同 | 缺失/双方空值 |
|:--|--:|--:|--:|
| `axdata_shortline_vs_eltdx:alignment_status` | 0 | 120 | 0 |
| `axdata_shortline_vs_eltdx:beta_60d` | 0 | 120 | 0 |
| `axdata_shortline_vs_eltdx:code` | 0 | 120 | 0 |
| `axdata_shortline_vs_eltdx:full_code` | 0 | 120 | 0 |
| `axdata_shortline_vs_eltdx:instrument_id` | 0 | 120 | 0 |
| `axdata_shortline_vs_eltdx:limit_status` | 0 | 120 | 0 |
| `axdata_shortline_vs_eltdx:market_id` | 0 | 120 | 0 |
| `axdata_shortline_vs_eltdx:opening_rush` | 0 | 120 | 0 |
| `axdata_shortline_vs_eltdx:pe_ttm` | 0 | 120 | 0 |
| `axdata_shortline_vs_eltdx:previous_trade_date` | 0 | 120 | 0 |
| `axdata_shortline_vs_eltdx:symbol` | 0 | 120 | 0 |
| `axdata_shortline_vs_eltdx:target_trade_date` | 0 | 120 | 0 |
| `axdata_shortline_vs_eltdx:tdx_code` | 0 | 120 | 0 |
| `axdata_shortline_vs_eltdx:open_amount` | 23 | 97 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_hand` | 23 | 97 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_ratio` | 23 | 97 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_amount_ratio` | 27 | 93 | 0 |
| `axdata_shortline_vs_eltdx:auction_prev_volume_ratio` | 35 | 83 | 2 |
| `axdata_shortline_vs_eltdx:open_turnover_z` | 60 | 60 | 0 |
| `axdata_shortline_vs_eltdx:ladder_level` | 0 | 6 | 114 |
| `axdata_shortline_vs_eltdx:limit_board_text` | 11 | 5 | 104 |
| `axdata_shortline_vs_eltdx:open_prev_seal_ratio` | 2 | 5 | 113 |

## 字母字段名语义提示（仅候选）

窗口内观察到 191 条需审阅的字母字段路径：含词义线索 52 条，仅拆词 139 条。
完整逐条记录保存在碰撞 JSON；名称线索清单：`docs/field_verification/20261014/20261014_alphabetic_field_name_inventory.csv`。
> 拼音、英文、缩写和混合拆词只用于检索候选；必须结合原始值、接口定义和独立来源复核，不得据此定案或改写主字典。

| 逐源字段路径 | 状态/审阅范围 | 名称形式与拆词 | 词义线索（非释义） | 样本日期 |
|:--|:--|:--|:--|:--|
| `市场源(market_sources)::change_type` | unverified / unverified_semantics | snake_case_or_mixed: change type | 变化/涨跌 + 类型 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `市场源(market_sources)::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `东财-push2ex::change_pct` | unverified / unverified_semantics | recognized_english_word_candidate: change pct | 变化/涨跌 + 百分比 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `东财-push2ex::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `东财-push2ex::first_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: first limit time | 首次/第一 + 涨跌停限制 + 时间 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `东财-push2ex::last_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: last limit time | 最近/上一期 + 涨跌停限制 + 时间 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `东财-push2ex::limit_count` | unverified / unverified_semantics | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `东财-push2ex::name` | unverified / unverified_semantics | recognized_english_word_candidate: name | 名称 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `东财-push2ex::price` | unverified / unverified_semantics | recognized_english_word_candidate: price | 价格 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `东财-push2ex::total_value` | unverified / unverified_semantics | snake_case_or_mixed: total value | 总 + 值 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `市场源(market_sources)::limit_count` | verified / verified_metadata_gap | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `市场源(market_sources)::limit_time` | unverified / unverified_semantics | snake_case_or_mixed: limit time | 涨跌停限制 + 时间 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `市场源(market_sources)::plate_limit_up_count` | verified / verified_metadata_gap | snake_case_or_mixed: plate limit up count | 涨跌停限制 + 上/涨 + 数量/次数 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `财联社(cls)::time` | unverified / unverified_semantics | recognized_english_word_candidate: time | 时间 | C:20261029, C:20261031, C:20261102, C:20261103, C:20261104 |
| `开盘红(Levistock适配)::limit_count` | unverified / unverified_semantics | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261028, T:20261030, T:20261102, T:20261103 |
| `开盘红(Levistock适配)::open_time` | unverified / unverified_semantics | snake_case_or_mixed: open time | 开盘 + 时间 | T:20261028, T:20261030, T:20261102, T:20261103 |
| `新浪(扩展API)::turnover` | conflict / unverified_semantics | recognized_english_word_candidate: turnover | 换手/成交额（需看接口） | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::changqifuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: changqifuzhai | 长期负债 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::cunhuo` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: cunhuo | 存货 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::eps` | unverified / unverified_semantics | recognized_english_word_candidate: eps | 每股收益 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::fajirenfarengu` | unverified / unverified_semantics | recognized_pinyin_phrase_candidate: fajirenfarengu | 疑似 faqirenfarengu 的拼写变体；含义未证实 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::gudongrenshu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: gudongrenshu | 股东人数 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::ipodate` | unverified / unverified_semantics | recognized_english_phrase_candidate: ipodate | IPO/上市日期（字段语境候选） | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::jinglirun` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jinglirun | 净利润 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::jingyingxianjinliu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingyingxianjinliu | 经营现金流 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::jingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingzichan | 净资产 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::liudongfuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: liudongfuzhai | 流动负债 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::meigujingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: meigujingzichan | 每股净资产 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::price` | unverified / unverified_semantics | recognized_english_word_candidate: price | 价格 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::yingshouzhangkuan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: yingshouzhangkuan | 应收账款 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::zhuyingshouru` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zhuyingshouru | 主营收入 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::zibengongjijin` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zibengongjijin | 资本公积金 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::zongzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongzichan | 总资产 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `同花顺-fuyao::snapshot.open_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot open price | 开盘 + 价格 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `同花顺-fuyao::valuation.pb_mrq` | conflict / unverified_semantics | snake_case_or_mixed: valuation pb mrq | 市净率 + 最近报告期 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `同花顺-fuyao::valuation.pe_mrq` | conflict / unverified_semantics | snake_case_or_mixed: valuation pe mrq | 市盈率 + 最近报告期 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `同花顺-fuyao::valuation.pe_ttm` | conflict / unverified_semantics | snake_case_or_mixed: valuation pe ttm | 市盈率 + 滚动十二个月 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `ZHB-tdxstat::change_pct` | unverified / unverified_semantics | recognized_english_word_candidate: change pct | 变化/涨跌 + 百分比 | T:20261028, T:20261030, T:20261102, T:20261103 |
| `ZHB-tdxstat::change_pct_1d` | unverified / unverified_semantics | snake_case_or_mixed: change pct 1 d | 变化/涨跌 + 百分比 | T:20261028, T:20261030, T:20261102, T:20261103 |
| `ZHB-tdxstat::change_pct_2d` | unverified / unverified_semantics | snake_case_or_mixed: change pct 2 d | 变化/涨跌 + 百分比 | T:20261028, T:20261030, T:20261102, T:20261103 |
| `ZHB-tdxstat2::main_net_buy_amount` | unverified / unverified_semantics | snake_case_or_mixed: main net buy amount | 净 + 金额/成交额（需看接口） | T:20261028, T:20261030, T:20261102, T:20261103 |
| `ZHB-tdxstat2::main_net_buy_amount_1d` | unverified / unverified_semantics | snake_case_or_mixed: main net buy amount 1 d | 净 + 金额/成交额（需看接口） | T:20261028, T:20261030, T:20261102, T:20261103 |
| `reports::actualLastTwoYearEps` | unverified / unverified_semantics | camel_case_or_mixed: actual Last Two Year Eps | 最近/上一期 + 每股收益 | C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104 |
| `reports::actualLastYearEps` | unverified / unverified_semantics | camel_case_or_mixed: actual Last Year Eps | 最近/上一期 + 每股收益 | C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104 |
| `reports::count` | verified / verified_metadata_gap | recognized_english_word_candidate: count | 数量/次数 | C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104 |
| `reports::lastEmRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Code | 最近/上一期 + 代码 | C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104 |
| `reports::lastEmRatingName` | conflict / unverified_semantics | camel_case_or_mixed: last Em Rating Name | 最近/上一期 + 名称 | C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104 |
| `reports::lastEmRatingValue` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Value | 最近/上一期 + 值 | C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104 |
| `reports::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104 |
| `reports::predictLastYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Eps | 最近/上一期 + 每股收益 | C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104 |
| `reports::predictLastYearPe` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Pe | 最近/上一期 + 市盈率 | C:20261029, C:20261030, C:20261031, C:20261101, C:20261102, C:20261103, C:20261104 |
| `TDX-eltdx(适配层)::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `东财-push2ex::broken_count` | unverified / unverified_semantics | snake_case_or_mixed: broken count | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `东财-push2ex::circulating_value` | unverified / unverified_semantics | snake_case_or_mixed: circulating value | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `东财-push2ex::sector` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: sector | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `东财-push2ex::turnover_rate` | unverified / unverified_semantics | snake_case_or_mixed: turnover rate | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `东财-push2ex::zt_continuous` | unverified / unverified_semantics | snake_case_or_mixed: zt continuous | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `东财-push2ex::zt_days` | unverified / unverified_semantics | snake_case_or_mixed: zt days | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `市场源(market_sources)::one_word` | unverified / unverified_semantics | snake_case_or_mixed: one word | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `市场源(market_sources)::plate_amount` | verified / verified_metadata_gap | snake_case_or_mixed: plate amount | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `市场源(market_sources)::plate_code` | verified / verified_metadata_gap | snake_case_or_mixed: plate code | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `市场源(market_sources)::plate_name` | verified / verified_metadata_gap | snake_case_or_mixed: plate name | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `市场源(market_sources)::popular` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: popular | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `财联社(cls)::content` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: content | — | C:20261029, C:20261031, C:20261102, C:20261103, C:20261104 |
| `财联社(cls)::level` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: level | — | C:20261029, C:20261031, C:20261102, C:20261103, C:20261104 |
| `财联社(cls)::reading_num` | unverified / unverified_semantics | snake_case_or_mixed: reading num | — | C:20261029, C:20261031, C:20261102, C:20261103, C:20261104 |
| `财联社(cls)::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20261029, C:20261031, C:20261102, C:20261103, C:20261104 |
| `开盘红(Levistock适配)::industry_id` | unverified / unverified_semantics | snake_case_or_mixed: industry id | — | T:20261028, T:20261030, T:20261102, T:20261103 |
| `开盘红(Levistock适配)::limit_tag` | unverified / unverified_semantics | snake_case_or_mixed: limit tag | — | T:20261028, T:20261030, T:20261102, T:20261103 |
| `开盘红(Levistock适配)::reason` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: reason | — | T:20261028, T:20261030, T:20261102, T:20261103 |
| `开盘红(Levistock适配)::themes` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: themes | — | T:20261028, T:20261030, T:20261102, T:20261103 |
| `FTShare REST::amplitude` | verified / verified_metadata_gap | runtime_tokenization_only: amplitude | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `FTShare REST::avg` | verified / verified_metadata_gap | runtime_tokenization_only: avg | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `FTShare REST::bid_ask_ratio` | verified / verified_metadata_gap | runtime_tokenization_only: bid ask ratio | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `FTShare REST::board` | verified / verified_metadata_gap | runtime_tokenization_only: board | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `FTShare REST::listing_date` | verified / verified_metadata_gap | runtime_tokenization_only: listing date | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `FTShare REST::name` | verified / verified_metadata_gap | runtime_tokenization_only: name | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `FTShare REST::st` | verified / verified_metadata_gap | runtime_tokenization_only: st | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `FTShare REST::status` | verified / verified_metadata_gap | runtime_tokenization_only: status | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `FTShare REST::symbol` | verified / verified_metadata_gap | runtime_tokenization_only: symbol | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `FTShare REST::symbol_id` | unverified / unverified_semantics | runtime_tokenization_only: symbol id | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `FTShare REST::turnover_rate` | verified / verified_metadata_gap | runtime_tokenization_only: turnover rate | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `同花顺-fuyao::fin_report` | unverified / unverified_semantics | snake_case_or_mixed: fin report | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `市场源(market_sources)::big_order_300w_net` | unverified / unverified_semantics | runtime_tokenization_only: big order 300 w net | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `市场源(market_sources)::institution_add` | unverified / unverified_semantics | runtime_tokenization_only: institution add | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `市场源(market_sources)::main_inflow` | unverified / unverified_semantics | snake_case_or_mixed: main inflow | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `市场源(market_sources)::pe_next` | unverified / unverified_semantics | runtime_tokenization_only: pe next | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `市场源(market_sources)::pe_now` | unverified / unverified_semantics | runtime_tokenization_only: pe now | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `市场源(market_sources)::strength` | unverified / unverified_semantics | runtime_tokenization_only: strength | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `市场源(market_sources)::total_value` | unverified / unverified_semantics | runtime_tokenization_only: total value | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `新浪(扩展API)::netamount` | conflict / unverified_semantics | unsegmented_latin_pinyin_or_word: netamount | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `新浪(扩展API)::opendate` | conflict / unverified_semantics | unsegmented_latin_pinyin_or_word: opendate | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `新浪(扩展API)::trade` | conflict / unverified_semantics | unsegmented_latin_pinyin_or_word: trade | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::ask1` | unverified / unverified_semantics | mixed_alphanumeric: ask 1 | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::ask1_vol` | unverified / unverified_semantics | runtime_tokenization_only: ask 1 vol | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::b_vol` | unverified / unverified_semantics | snake_case_or_mixed: b vol | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::b_vol` | unverified / unverified_semantics | snake_case_or_mixed: b vol | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |
| `TDX(双命名源)::baoliu2` | unverified / unverified_semantics | mixed_alphanumeric: baoliu 2 | — | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 |

Markdown 显示前 100 条；其余 91 条完整保留在 JSON。

## 探索候选持续跟踪

研究台账：`collision_research_state.json.gz`；累计历史跟踪候选对 2069，本报告候选对 735，历史复现 627，新发现 0。
台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，不会自动改变字段状态、碰撞锚或主字典。新报告只将 `actionable_L1`、L4 和主动方法候选写入待研究队列；已登记关系的复验单独展示，历史跟踪记录不会被删除。

## 候选覆盖、公式与下一步采样

本节用于定位证据缺口和安排后续取样。相关性、公式与样本优先级均为探索候选；不会改变 L1/L1-U 门槛、来源独立性或主字典。

- 未知目标 339 个；其中有方法候选 199 个、无候选 140 个；多候选目标 185 个。
- 方法候选生成 5791 条；全局详细项保留 500/500，另按目标字段保留 179 条；完整明细 5791 条在 JSON `method_candidate_inventory`；未归档明细 0 条。
- 字段覆盖详情：available；覆盖身份 1920，读取 7 份本地索引。

### 优先处理字段

| 未知字段 | 当前诊断 | 独立对比/候选数 | 独立锚家族/本源日期 | 建议复核股票 | 最强候选线索 |
|:--|:--|--:|:--|:--|:--|
| `sina_extended.trade` | 存在多个候选，需区分 | 316 / 119 | 6 家族 / 316 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[15]` | 存在多个候选，需区分 | 316 / 117 | 6 家族 / 316 对 / 本源 7 日 | 600519 (5.716604) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[17]` | 存在多个候选，需区分 | 316 / 117 | 6 家族 / 316 对 / 本源 7 日 | 600519 (5.709353) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[19]` | 存在多个候选，需区分 | 316 / 117 | 6 家族 / 316 对 / 本源 7 日 | 600519 (5.699539) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[13]` | 存在多个候选，需区分 | 316 / 116 | 6 家族 / 316 对 / 本源 7 日 | 600519 (5.719182) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[11]` | 存在多个候选，需区分 | 279 / 99 | 6 家族 / 279 对 / 本源 7 日 | 600519 (6.070289) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[13]` | 存在多个候选，需区分 | 279 / 99 | 6 家族 / 279 对 / 本源 7 日 | 600519 (6.066822) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[15]` | 存在多个候选，需区分 | 279 / 99 | 6 家族 / 279 对 / 本源 7 日 | 600519 (6.065979) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[17]` | 存在多个候选，需区分 | 279 / 99 | 6 家族 / 279 对 / 本源 7 日 | 600519 (6.064927) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[23]` | 存在多个候选，需区分 | 316 / 94 | 6 家族 / 316 对 / 本源 7 日 | 600519 (6.303361) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[25]` | 存在多个候选，需区分 | 316 / 94 | 6 家族 / 316 对 / 本源 7 日 | 600519 (6.305369) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[27]` | 存在多个候选，需区分 | 316 / 94 | 6 家族 / 316 对 / 本源 7 日 | 600519 (6.308766) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[29]` | 存在多个候选，需区分 | 316 / 94 | 6 家族 / 316 对 / 本源 7 日 | 600519 (6.309999) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `ulist239.f143` | 存在多个候选，需区分 | 237 / 91 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `fuyao.valuation.ps_ttm` | 存在多个候选，需区分 | 321 / 87 | 6 家族 / 321 对 / 本源 6 日 | 600519 (12.177484) | ulist239.f130 (robust_correlation,affine_formula,per_stock_time_series); tencent[46] (robust_correlation,per_stock_time_series) |
| `ulist239.f142` | 存在多个候选，需区分 | 237 / 86 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `ulist239.f144` | 存在多个候选，需区分 | 237 / 86 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f135` | 存在多个候选，需区分 | 237 / 83 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `fuyao.valuation.pb_mrq` | 存在多个候选，需区分 | 321 / 79 | 6 家族 / 321 对 / 本源 6 日 | 600519 (14.029514) | tencent[46] (robust_correlation,affine_formula,per_stock_time_series); ulist239.f23 (robust_correlation,affine_formula,per_stock_time_series) |
| `tdx.quote_raw.price` | 存在多个候选，需区分 | 189 / 79 | 6 家族 / 189 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[21]` | 存在多个候选，需区分 | 279 / 79 | 6 家族 / 279 对 / 本源 7 日 | 600519 (7.518341) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[23]` | 存在多个候选，需区分 | 279 / 79 | 6 家族 / 279 对 / 本源 7 日 | 600519 (7.521239) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[25]` | 存在多个候选，需区分 | 279 / 79 | 6 家族 / 279 对 / 本源 7 日 | 600519 (7.524635) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[27]` | 存在多个候选，需区分 | 279 / 79 | 6 家族 / 279 对 / 本源 7 日 | 600519 (7.5276) | sina[7] (robust_correlation,affine_formula,per_stock_time_series); sina[6] (robust_correlation,affine_formula,per_stock_time_series) |
| `ulist239.f63` | 存在多个候选，需区分 | 237 / 79 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[62] (robust_correlation,per_stock_time_series); tencent[57] (robust_correlation,per_stock_time_series) |
| `push2.f108` | 存在多个候选，需区分 | 237 / 78 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[68] (robust_correlation,affine_formula) |
| `push2.f160` | 存在多个候选，需区分 | 237 / 78 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[68] (robust_correlation,affine_formula) |
| `tdx.quote_raw.bid1` | 存在多个候选，需区分 | 189 / 78 | 6 家族 / 189 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.high_52w` | 存在多个候选，需区分 | 189 / 70 | 6 家族 / 189 对 / 本源 4 日 | 600519 (22.373952) | ftshare_rest.high (robust_correlation,affine_formula,per_stock_time_series,semantic_label); tencent[9] (robust_correlation,affine_formula,per_stock_time_series) |
| `em_fund_flow.f135` | 存在多个候选，需区分 | 237 / 69 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `ulist239.f133` | 存在多个候选，需区分 | 237 / 69 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[69] (robust_correlation,per_stock_time_series); tencent[64] (robust_correlation,per_stock_time_series) |
| `push2.f174` | 存在多个候选，需区分 | 237 / 67 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[68] (robust_correlation,affine_formula,per_stock_time_series); tencent[67] (robust_correlation,affine_formula,per_stock_time_series) |
| `tdx.quote_raw.ask1` | 存在多个候选，需区分 | 189 / 66 | 6 家族 / 189 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `em_fund_flow.f136` | 存在多个候选，需区分 | 237 / 62 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.pre_receive_zj` | 存在多个候选，需区分 | 189 / 62 | 6 家族 / 189 对 / 本源 0 日 | 600519 (52.146507) | tencent[64] (robust_correlation,per_stock_time_series); tencent[45] (robust_correlation,per_stock_time_series) |
| `push2.f136` | 存在多个候选，需区分 | 237 / 61 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `tdx.finance_info.eps` | 存在多个候选，需区分 | 189 / 59 | 6 家族 / 189 对 / 本源 0 日 | no_shared_stock_holdout | push2.f55 (robust_correlation,affine_formula,per_stock_time_series); tencent[9] (robust_correlation,affine_formula) |
| `push2.f49` | 存在多个候选，需区分 | 237 / 53 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | sina[8] (robust_correlation,affine_formula,per_stock_time_series); ftshare_rest.volume (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.change_ytd` | 存在多个候选，需区分 | 189 / 53 | 6 家族 / 189 对 / 本源 4 日 | 600825 (2.136245) | tencent[75] (robust_correlation,affine_formula,per_stock_time_series); tencent[62] (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.dividend_yield` | 存在多个候选，需区分 | 189 / 51 | 6 家族 / 189 对 / 本源 4 日 | 600519 (51.400001) | tencent[64] (robust_correlation,per_stock_time_series); tencent[9] (per_stock_time_series) |
| `push2.f161` | 存在多个候选，需区分 | 237 / 50 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | sina[8] (robust_correlation,affine_formula,per_stock_time_series); ftshare_rest.volume (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[26]` | 存在多个候选，需区分 | 316 / 48 | 6 家族 / 316 对 / 本源 7 日 | 600519 (6.594969) | tencent[9] (robust_correlation); tencent[68] (robust_correlation) |
| `tencent[26]` | 存在多个候选，需区分 | 279 / 45 | 6 家族 / 279 对 / 本源 7 日 | 600519 (17.875439) | sina[6] (robust_correlation); sina[5] (robust_correlation) |
| `em_fund_flow.f139` | 存在多个候选，需区分 | 237 / 44 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,per_stock_time_series); tencent[37] (robust_correlation,per_stock_time_series) |
| `zhb.full.change_60k_bar` | 存在多个候选，需区分 | 189 / 44 | 6 家族 / 189 对 / 本源 0 日 | 600519 (5.418373) | tencent[71] (robust_correlation,affine_formula,per_stock_time_series); tencent[79] (robust_correlation,per_stock_time_series) |
| `zhb.full.change_30k_bar` | 存在多个候选，需区分 | 189 / 43 | 6 家族 / 189 对 / 本源 4 日 | 600519 (5.105616) | tencent[71] (robust_correlation,affine_formula,per_stock_time_series); tencent[75] (robust_correlation,per_stock_time_series) |
| `zhb.full.change_250k_bar` | 存在多个候选，需区分 | 189 / 42 | 6 家族 / 189 对 / 本源 4 日 | 600519 (7.926155) | tencent[79] (robust_correlation,affine_formula,per_stock_time_series); tencent[75] (robust_correlation,per_stock_time_series) |
| `ulist239.f135` | 存在多个候选，需区分 | 237 / 41 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[76] (robust_correlation,affine_formula); tencent[73] (robust_correlation,affine_formula) |
| `zhb.full.change_5k_bar` | 存在多个候选，需区分 | 189 / 41 | 6 家族 / 189 对 / 本源 4 日 | 600519 (19.357754) | tencent[69] (robust_correlation,per_stock_time_series); tencent[63] (robust_correlation,per_stock_time_series) |
| `zhb.full.net_profit_kcf` | 存在多个候选，需区分 | 189 / 41 | 6 家族 / 189 对 / 本源 0 日 | 600519 (7.349424) | tencent[64] (robust_correlation,per_stock_time_series); ulist239.f47 (robust_correlation,affine_formula) |

_此表显示优先级最高的 50 / 共 339 个目标；完整清单见 JSON。_


### 舍入近似数值线索（仅研究，不算 L1/L1-U；36 组）

近似窗口只用于提示复核：需核对双方原始单位、展示精度和来源口径；不得把该命中率当作字段语义结论或注册表写回依据。完整明细在 JSON `candidate_triage.approximate_matches`。

| 左字段 | 右字段 | 近似命中率 | 精确/舍入命中 | 有效日期 | 最大误差（绝对/相对） |
|:--|:--|--:|:--|:--|:--|
| `fuyao.valuation.pe_mrq` | `tencent[52]` | 100.00% | 0/120 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 0.005737000000067383 / 0.0005025219112378634 |
| `fuyao.valuation.pe_ttm` | `tencent[39]` | 100.00% | 0/120 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 0.006250999999906526 / 0.0005666189719405212 |
| `zhb.full.change_pct` | `fuyao.snapshot.price_change_ratio_pct` | 100.00% | 1/79 | T:20261028, T:20261030, T:20261102, T:20261103 | 0.0049759999999999804 / 0.027601166878599738 |
| `zhb.full.pe_lyr` | `tencent[53]` | 100.00% | 1/79 | T:20261028, T:20261030, T:20261102, T:20261103 | 0.0060000000000854925 / 0.0005447531378891637 |
| `zhb.stat.pe_lyr` | `tencent[53]` | 100.00% | 1/79 | T:20261028, T:20261030, T:20261102, T:20261103 | 0.0060000000000854925 / 0.0005447531378891637 |
| `sina[13]` | `tencent[9]` | 99.28% | 0/138 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 1.7699999999999818 / 0.004975124378109473 |
| `tencent[11]` | `sina[11]` | 99.28% | 0/138 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 1.7699999999999818 / 0.004975124378109473 |
| `tencent[11]` | `sina[6]` | 99.28% | 0/138 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 1.7699999999999818 / 0.004975124378109473 |
| `sina[23]` | `tencent[19]` | 98.50% | 0/131 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 0.19000000000005457 / 0.0046511627906975755 |
| `tencent[21]` | `sina[21]` | 98.50% | 0/131 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 0.19000000000005457 / 0.0046511627906975755 |
| `tencent[21]` | `sina[7]` | 98.50% | 0/131 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 0.19000000000005457 / 0.0046511627906975755 |
| `fuyao.valuation.pb_mrq` | `tencent[46]` | 98.33% | 0/118 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 0.0049479999999999524 / 0.005378313253011943 |
| `sina[13]` | `fuyao.snapshot.last_price` | 94.17% | 0/113 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 2.0 / 0.004694835680751074 |
| `tencent[11]` | `fuyao.snapshot.last_price` | 94.17% | 0/113 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 2.0 / 0.004694835680751074 |
| `sina[25]` | `tencent[19]` | 93.23% | 0/124 | T:20261026, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 0.22000000000002728 / 0.004700352526439383 |
| `tencent[23]` | `sina[21]` | 93.23% | 0/124 | T:20261026, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 0.22000000000002728 / 0.004700352526439383 |
| `tencent[23]` | `sina[7]` | 93.23% | 0/124 | T:20261026, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 0.22000000000002728 / 0.004700352526439383 |
| `sina[13]` | `ftshare_rest.close` | 92.86% | 0/130 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 2.0 / 0.004975124378109473 |
| `sina[13]` | `tencent[3]` | 92.86% | 0/130 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 2.0 / 0.004975124378109473 |
| `tencent[11]` | `ftshare_rest.close` | 92.86% | 0/130 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 2.0 / 0.004975124378109473 |
| `tencent[11]` | `sina[3]` | 92.86% | 0/130 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103, T:20261104 | 2.0 / 0.004975124378109473 |
| `sina[15]` | `tencent[9]` | 92.81% | 0/129 | T:20261026, T:20261028, T:20261029, T:20261102, T:20261103, T:20261104 | 2.7100000000000364 / 0.00465838509316774 |
| `tencent[13]` | `sina[11]` | 92.81% | 0/129 | T:20261026, T:20261028, T:20261029, T:20261102, T:20261103, T:20261104 | 2.7100000000000364 / 0.00465838509316774 |
| `tencent[13]` | `sina[6]` | 92.81% | 0/129 | T:20261026, T:20261028, T:20261029, T:20261102, T:20261103, T:20261104 | 2.7100000000000364 / 0.00465838509316774 |
| `zhb.full.change_250k_bar` | `tencent[79]` | 92.50% | 53/21 | T:20261028, T:20261030, T:20261102, T:20261103 | 0.11999999999999744 / 0.004822446295484412 |
| `fuyao.valuation.pe_ttm` | `zhb.full.pe_ttm` | 91.25% | 0/73 | T:20261028, T:20261102, T:20261103 | 0.004889999999999617 / 0.00040195104644553015 |
| `fuyao.valuation.pe_ttm` | `zhb.stat.pe_ttm` | 91.25% | 0/73 | T:20261028, T:20261102, T:20261103 | 0.004889999999999617 / 0.00040195104644553015 |
| `sina[27]` | `tencent[19]` | 90.98% | 0/121 | T:20261026, T:20261029, T:20261103, T:20261104 | 0.2300000000000182 / 0.004940014114326061 |
| `tencent[25]` | `sina[21]` | 90.98% | 0/121 | T:20261026, T:20261029, T:20261103, T:20261104 | 0.2300000000000182 / 0.004940014114326061 |
| `tencent[25]` | `sina[7]` | 90.98% | 0/121 | T:20261026, T:20261029, T:20261103, T:20261104 | 0.2300000000000182 / 0.004940014114326061 |
| `sina[23]` | `ftshare_rest.close` | 90.71% | 0/127 | T:20261026, T:20261029, T:20261030, T:20261103, T:20261104 | 0.21000000000003638 / 0.0049504950495049705 |
| `sina[23]` | `tencent[3]` | 90.71% | 0/127 | T:20261026, T:20261029, T:20261030, T:20261103, T:20261104 | 0.21000000000003638 / 0.0049504950495049705 |
| `tencent[21]` | `ftshare_rest.close` | 90.71% | 0/127 | T:20261026, T:20261029, T:20261030, T:20261103, T:20261104 | 0.21000000000003638 / 0.0049504950495049705 |
| `tencent[21]` | `sina[3]` | 90.71% | 0/127 | T:20261026, T:20261029, T:20261030, T:20261103, T:20261104 | 0.21000000000003638 / 0.0049504950495049705 |
| `sina[23]` | `fuyao.snapshot.last_price` | 90.00% | 0/108 | T:20261029, T:20261030, T:20261103, T:20261104 | 0.21000000000003638 / 0.004719764011799309 |
| `tencent[21]` | `fuyao.snapshot.last_price` | 90.00% | 0/108 | T:20261029, T:20261030, T:20261103, T:20261104 | 0.21000000000003638 / 0.004719764011799309 |

### 补足全局截断的字段候选（179）

| 未知字段 | 候选字段 | 方法 | 样本 | 日期 | 来源 |
|:--|:--|:--|--:|:--|:--|
| `axdata.data.float_shares` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula, semantic_label | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.free_float_shares` | `ftshare_rest.shares` | robust_correlation, affine_formula | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.limit_stat_days` | `ftshare_rest.change_rate_day5` | robust_correlation | 24 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.limit_up_count_in_stat_days` | `ftshare_rest.change_rate_day5` | robust_correlation | 24 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.limit_up_streak_days` | `ftshare_rest.change_rate_day5` | robust_correlation | 17 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.open_amount` | `ftshare_rest.volume` | robust_correlation | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.open_change_pct` | `ftshare_rest.change_rate` | per_stock_time_series | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.open_prev_amount_ratio` | `ftshare_rest.turnover` | robust_correlation | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.open_price` | `ftshare_rest.prev_close` | robust_correlation, affine_formula, per_stock_time_series | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.open_turnover_z` | `ftshare_rest.turnover_rate` | robust_correlation | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.open_volume_hand` | `ftshare_rest.volume` | robust_correlation | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.open_volume_ratio` | `ftshare_rest.turnover` | robust_correlation | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.pre_close` | `ftshare_rest.prev_close` | robust_correlation, affine_formula, per_stock_time_series | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.prev_amount` | `ftshare_rest.volume` | robust_correlation | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.prev_open_amount` | `ftshare_rest.volume` | robust_correlation | 137 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.prev_open_volume_hand` | `ftshare_rest.volume` | robust_correlation | 137 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.seal_to_float_ratio` | `ftshare_rest.turnover_rate` | robust_correlation | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `axdata.data.year_limit_up_days` | `ftshare_rest.turnover` | per_stock_time_series | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | axdata, ftshare_rest |
| `em_fund_flow.f135` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 60 | T:20261102, T:20261103, T:20261104 | em_fund_flow, tencent |
| `em_fund_flow.f136` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 57 | T:20261102, T:20261103, T:20261104 | em_fund_flow, tencent |
| `em_fund_flow.f139` | `tencent[57]` | robust_correlation, per_stock_time_series | 49 | T:20261102, T:20261103, T:20261104 | em_fund_flow, tencent |
| `em_kline_f61.dktotal` | `tencent[30]` | per_stock_time_series | 60 | T:20261102, T:20261103, T:20261104 | em_kline_f61, tencent |
| `event_dc.AMPLITUDE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.CHANGE` | `ftshare_rest.change_rate` | robust_correlation, affine_formula, semantic_label | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.CHANGE_RATE` | `ftshare_rest.change_rate` | robust_correlation, affine_formula, semantic_label | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.CLOSE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.EACHBALLOT_SHARES` | `ftshare_rest.shares` | semantic_label | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.INDUSTRY_PE` | `ftshare_rest.ts_millis` | robust_correlation | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.INDUSTRY_PE_NEW` | `ftshare_rest.ts_millis` | robust_correlation | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.IPO_YIELD` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.ISSUE_NUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.ISSUE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.LATELY_PRICE` | `ftshare_rest.close` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.LD_AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.LD_CLOSE_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.LD_HIGH_CHANG` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.LD_OPEN_PREMIUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.LIMIT_UP_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.MZYQ_PAY_FUND` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.OD_HIGH_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.OPEN_AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.OPEN_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.PROFIT` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.TCHANGE_RATE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.TNEW_PRICE` | `ftshare_rest.close` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.TOTAL_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.TOTAL_ISSUE_NUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.TOTAL_SHARES` | `ftshare_rest.shares` | robust_correlation, affine_formula, semantic_label | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.TURNOVERRATE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `event_dc.fetched_at` | `ftshare_rest.ts_millis` | robust_correlation, affine_formula | 14 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | event_dc, ftshare_rest |
| `fuyao.valuation.pb_mrq` | `tencent[46]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | fuyao, tencent |
| `fuyao.valuation.pe_mrq` | `tencent[52]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | fuyao, tencent |
| `fuyao.valuation.pe_ttm` | `tencent[39]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | fuyao, tencent |
| `fuyao.valuation.ps_ttm` | `ulist239.f130` | robust_correlation, affine_formula, per_stock_time_series | 60 | T:20261102, T:20261103, T:20261104 | fuyao, ulist239 |
| `kpl.main_buy` | `push2ex.amount` | robust_correlation, per_stock_time_series | 460 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | kpl, push2ex |
| `kpl.main_sell` | `push2ex.amount` | robust_correlation, per_stock_time_series | 460 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | kpl, push2ex |
| `kpl.raw_columns.col_09` | `push2ex.amount` | robust_correlation, per_stock_time_series | 460 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | kpl, push2ex |
| `kpl.raw_columns.col_10` | `push2ex.amount` | robust_correlation, per_stock_time_series | 460 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | kpl, push2ex |
| `kpl.raw_columns.col_13` | `push2ex.amount` | robust_correlation | 460 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | kpl, push2ex |
| `kpl.raw_columns.col_16` | `push2ex.limit_fund` | per_stock_time_series | 460 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | kpl, push2ex |
| `push2.f103` | `zhb.stat.net_profit_kcf` | robust_correlation, affine_formula | 40 | T:20261102, T:20261103 | push2, zhb |
| `push2.f108` | `tencent[9]` | robust_correlation, affine_formula | 88 | T:20261026, T:20261029, T:20261102, T:20261103, T:20261104 | push2, tencent |
| `push2.f109` | `tdx.finance_info.weifenlirun` | robust_correlation, affine_formula | 87 | T:20261026, T:20261029, T:20261102, T:20261103, T:20261104 | push2, tdx |
| `push2.f135` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 88 | T:20261026, T:20261029, T:20261102, T:20261103, T:20261104 | push2, tencent |
| `push2.f136` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 85 | T:20261026, T:20261029, T:20261102, T:20261103, T:20261104 | push2, tencent |
| `push2.f160` | `tencent[9]` | robust_correlation, affine_formula | 88 | T:20261026, T:20261029, T:20261102, T:20261103, T:20261104 | push2, tencent |
| `push2.f161` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 88 | T:20261026, T:20261029, T:20261102, T:20261103, T:20261104 | push2, sina |
| `push2.f174` | `tencent[68]` | robust_correlation, affine_formula, per_stock_time_series | 88 | T:20261026, T:20261029, T:20261102, T:20261103, T:20261104 | push2, tencent |
| `push2.f176` | `tencent[46]` | robust_correlation, per_stock_time_series | 88 | T:20261026, T:20261029, T:20261102, T:20261103, T:20261104 | push2, tencent |
| `push2.f191` | `tencent[74]` | robust_correlation, affine_formula, per_stock_time_series | 88 | T:20261026, T:20261029, T:20261102, T:20261103, T:20261104 | push2, tencent |
| `push2.f192` | `tencent[50]` | robust_correlation, affine_formula, per_stock_time_series | 88 | T:20261026, T:20261029, T:20261102, T:20261103, T:20261104 | push2, tencent |
| `push2.f49` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 88 | T:20261026, T:20261029, T:20261102, T:20261103, T:20261104 | push2, sina |
| `push2.f62` | `tencent[71]` | per_stock_time_series | 88 | T:20261026, T:20261029, T:20261102, T:20261103, T:20261104 | push2, tencent |
| `push2ex.broken_count` | `kpl.seal_amount` | per_stock_time_series | 460 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | kpl, push2ex |
| `push2ex.circulating_value` | `kpl.zt_time` | per_stock_time_series | 460 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | kpl, push2ex |
| `push2ex.first_limit_time` | `kph.limit_time` | semantic_label | 160 | T:20261028, T:20261030, T:20261102, T:20261103 | kph, push2ex |
| `push2ex.limit_count` | `kpl.zt_time` | per_stock_time_series | 460 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | kpl, push2ex |
| `push2ex.price` | `kpl.zt_time` | per_stock_time_series | 460 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | kpl, push2ex |
| `push2ex.total_value` | `kpl.zt_time` | per_stock_time_series | 460 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | kpl, push2ex |
| `push2ex.turnover_rate` | `kpl.turnover_real` | robust_correlation, per_stock_time_series | 460 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | kpl, push2ex |
| `push2ex.zt_continuous` | `kpl.zt_time` | per_stock_time_series | 460 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | kpl, push2ex |
| `push2ex.zt_days` | `kpl.zt_time` | per_stock_time_series | 460 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | kpl, push2ex |
| `sina[14]` | `tencent[68]` | robust_correlation | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent |
| `sina[16]` | `tencent[68]` | robust_correlation | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent |
| `sina[18]` | `tencent[68]` | robust_correlation | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent |
| `sina[24]` | `tencent[67]` | robust_correlation | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent |
| `sina[26]` | `tencent[9]` | robust_correlation | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent |
| `sina[28]` | `tencent[68]` | robust_correlation | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent |
| `sina_extended.netamount` | `tencent[32]` | robust_correlation, per_stock_time_series | 140 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina_extended, tencent |
| `sina_extended.turnover` | `push2.f168` | robust_correlation, affine_formula, per_stock_time_series | 88 | T:20261026, T:20261029, T:20261102, T:20261103, T:20261104 | push2, sina_extended |
| `slist.n_boards` | `tencent[45]` | robust_correlation | 60 | T:20261102, T:20261103, T:20261104 | slist, tencent |
| `tdx.b_vol` | `fuyao.snapshot.volume` | robust_correlation, affine_formula, per_stock_time_series | 119 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | fuyao, tdx |
| `tdx.finance_info.baoliu2` | `tencent[30]` | robust_correlation, per_stock_time_series | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent |
| `tdx.finance_info.eps` | `push2.f55` | robust_correlation, affine_formula, per_stock_time_series | 87 | T:20261026, T:20261029, T:20261102, T:20261103, T:20261104 | push2, tdx |
| `tdx.finance_info.fajirenfarengu` | `push2.f105` | robust_correlation, affine_formula, per_stock_time_series | 87 | T:20261026, T:20261029, T:20261102, T:20261103, T:20261104 | push2, tdx |
| `tdx.finance_info.zhuyinglyrun` | `tencent[76]` | robust_correlation | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent |
| `tdx.quote_full.ask1_vol` | `sina[22]` | robust_correlation | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tdx |
| `tdx.quote_full.b_vol` | `fuyao.snapshot.volume` | robust_correlation, affine_formula, per_stock_time_series | 119 | T:20261028, T:20261029, T:20261030, T:20261102, T:20261103 | fuyao, tdx |
| `tdx.quote_full.bid1_vol` | `tencent[68]` | robust_correlation | 139 | T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent |

_仅显示前 100 / 共 179 条字段前沿候选。_


### 双输入公式候选
本轮未发现通过留出筛选的公式候选；测试组合 6169 个。


### 已知映射与已证伪关系的候选校准

- 已登记正向对照：当前窗口有 170 组独立数值关系可评估，168 组被方法候选识别；样本不足 1 组。此计数仅检查方法覆盖，不是准确率。
- 已证伪负向对照：数值关系 0 组，其中仍有方法信号 0 组；这些信号被隔离，不进入普通候选。

### 采集覆盖异常源

- axdata: 20261026 ({'ok': 6, 'partial': 1})
- baidu: 20261102, 20261103, 20261104 ({'pending_validation': 7})
- clist: 20261028, 20261029, 20261030 ({'ok': 3, 'partial': 4})
- em_fund_flow: 20261028, 20261029, 20261030 ({'ok': 3, 'partial': 4})
- em_hot: 20261102, 20261103, 20261104 ({'context_only': 7})
- em_kline_f61: 20261028, 20261029, 20261030 ({'ok': 3, 'partial': 4})
- exchange: 20261102, 20261103, 20261104 ({'context_only': 7})
- ftshare: 20261102, 20261103, 20261104 ({'deprecated': 7})
- market_sources: 20261026 ({'ok': 6, 'partial': 1})
- push2: 20261028, 20261029, 20261030 ({'failed': 2, 'ok': 3, 'partial': 2})
- slist: 20261028, 20261029, 20261030 ({'failed': 4, 'ok': 3})
- st_list: 20261028, 20261029, 20261030 ({'ok': 3, 'partial': 4})
- tdx: 20261104 ({'ok': 6, 'partial': 1})
- ulist239: 20261028, 20261029, 20261030 ({'failed': 4, 'ok': 3})
- zhb: 20261102, 20261103, 20261104 ({'ok': 1, 'partial': 6})

## 候选身份与人工审阅状态

- 候选身份：生成 5883 条，唯一候选 5883 个，重复身份 0，无效身份 0。
- 审阅台账：可用；当前状态 `pending`；已审 4，待处理 5879，覆盖率 0.1%。
- 重复归并组：0；每个成员均保留到代表候选的反向追溯。
- 处置计数：`accepted_for_adjudication` 0；`duplicate_grouped` 0；`insufficient_evidence` 1；`needs_external_evidence` 3；`rejected` 0；`unreviewed` 5879。
- `accepted_for_adjudication` 只表示可进入现有证据裁决流程；审阅台账不会修改主字典或字段注册表。

## 报告完整性与审阅范围

- 机器可读完整性：`complete`；方法候选生成 5791 条，完整明细保存 5791 条，缺失 0 条，多余 0 条，重复 0 条，身份无效 0 条。
- 全量方法候选位于同名 JSON 的 `method_candidate_inventory`；Markdown 的 Top-N 表格是导航摘要，不能代替全量 JSON 审阅。
- 候选审阅数据对账：`complete`；唯一候选 5883 个，审阅 4 个，待处理 5879 个；人工审阅进度与机器清单完整性分别统计。
- Markdown 未逐行展示、但 JSON 保留的部分：
  - `L4`：展示 60 / 92，摘要省略 32 条。
  - `method_candidates`：展示 100 / 500，摘要省略 400 条。
  - `method_candidate_inventory`：展示 0 / 5791，摘要省略 5791 条。
  - `method_candidate_frontier`：展示 100 / 179，摘要省略 79 条。
  - `candidate_triage.targets`：展示 50 / 339，摘要省略 289 条。
  - `diagnostics`：展示 100 / 139，摘要省略 39 条。
  - `candidate_review.human_review.reviewed_candidates`：展示 0 / 4，摘要省略 4 条。
- 完整性对账通过；逐目标复核仍须覆盖 JSON 的全部明细，并为每项记录已检查、重复归并、证据不足或需外部核验的处置。
