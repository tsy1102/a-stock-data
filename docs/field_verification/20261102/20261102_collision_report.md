# 全源对撞报告（20261102）

> 交易数据窗口配置：近 7 个交易日（`--window`）
> 行情窗口：20261022 ~ 20261102（7 个不同交易日）｜字段 1296 个｜样本值 462253 条
> 新闻/公告自然日窗口：20261027 ~ 20261102
> 主攻目标（unverified）=495｜可审定新候选=0｜首次发现新候选对=0｜已登记关系复验=2｜异号同义 0 / 同号镜像 0

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
| `zhb.full.change_pct` | `tencent[32]` | L1 | 100.00% | 3 | 60 | 60 | - |  | ✅ |
| `zhb.full.high_52w` | `tencent[67]` | L1 | 95.00% | 3 | 60 | 60 | - |  | ✅ |

## 四、L4 存疑候选（149）

| 左字段 | 右字段 | 命中率 | 天数 | 样本 |
|:--|:--|--:|--:|--:|
| `axdata.data.instrument_id` | `ftshare_rest.symbol` | 100.00% | 6 | 119 |
| `axdata.data.open_price` | `ftshare_rest.open` | 100.00% | 6 | 119 |
| `axdata.data.pre_close` | `ftshare_rest.prev_close` | 100.00% | 6 | 119 |
| `axdata.data.float_shares` | `ftshare_rest.float_a_shares` | 100.00% | 6 | 119 |
| `push2.f57` | `tencent[2]` | 100.00% | 4 | 62 |
| `push2.f58` | `tencent[1]` | 100.00% | 4 | 62 |
| `push2.f60` | `eltdx.quote_snapshot.pre_close_price` | 100.00% | 4 | 62 |
| `push2.f60` | `eltdx.shortline.pre_close` | 100.00% | 4 | 62 |
| `push2.f60` | `ftshare_rest.prev_close` | 100.00% | 4 | 62 |
| `push2.f60` | `fuyao.snapshot.prev_price` | 100.00% | 3 | 48 |
| `push2.f60` | `sina[2]` | 100.00% | 4 | 62 |
| `push2.f60` | `tdx.quote_raw.last_close` | 100.00% | 4 | 62 |
| `push2.f60` | `tdx.quote_full.last_close` | 100.00% | 4 | 62 |
| `push2.f60` | `tencent[4]` | 100.00% | 4 | 62 |
| `push2.f119` | `zhb.full.change_5d` | 100.00% | 1 | 14 |
| `push2.f119` | `zhb.stat.change_5d` | 100.00% | 1 | 14 |
| `push2.f120` | `zhb.full.change_20d` | 100.00% | 1 | 14 |
| `push2.f120` | `zhb.stat.change_20d` | 100.00% | 1 | 14 |
| `push2.f162` | `tencent[52]` | 100.00% | 4 | 62 |
| `push2.f163` | `tencent[53]` | 100.00% | 4 | 62 |
| `push2.f164` | `zhb.full.pe_ttm` | 100.00% | 1 | 14 |
| `push2.f164` | `zhb.stat.pe_ttm` | 100.00% | 1 | 14 |
| `tdx.quote_raw.price` | `ftshare_rest.close` | 100.00% | 6 | 120 |
| `tdx.quote_raw.price` | `fuyao.snapshot.last_price` | 100.00% | 5 | 100 |
| `tdx.quote_raw.price` | `push2.f43` | 100.00% | 4 | 62 |
| `tdx.quote_raw.price` | `push2.f179` | 100.00% | 4 | 62 |
| `tdx.quote_raw.price` | `sina[3]` | 100.00% | 6 | 120 |
| `tdx.quote_raw.price` | `tencent[3]` | 100.00% | 6 | 120 |
| `tdx.quote_raw.price` | `ulist239.f2` | 100.00% | 1 | 20 |
| `tdx.quote_raw.bid1` | `sina[6]` | 100.00% | 6 | 120 |
| `tdx.quote_raw.bid1` | `sina[11]` | 100.00% | 6 | 120 |
| `tdx.quote_raw.bid1` | `tencent[9]` | 100.00% | 6 | 120 |
| `tdx.quote_raw.ask1` | `sina[7]` | 100.00% | 6 | 120 |
| `tdx.quote_raw.ask1` | `sina[21]` | 100.00% | 6 | 120 |
| `tdx.quote_raw.ask1` | `tencent[19]` | 100.00% | 6 | 120 |
| `ulist239.f7` | `tencent[43]` | 100.00% | 1 | 20 |
| `ulist239.f8` | `tencent[38]` | 100.00% | 1 | 20 |
| `ulist239.f10` | `tencent[49]` | 100.00% | 1 | 20 |
| `ulist239.f31` | `sina[6]` | 100.00% | 1 | 20 |
| `ulist239.f31` | `sina[11]` | 100.00% | 1 | 20 |
| `ulist239.f31` | `tdx.quote_full.bid1` | 100.00% | 1 | 20 |
| `ulist239.f31` | `tencent[9]` | 100.00% | 1 | 20 |
| `ulist239.f38` | `ftshare_rest.shares` | 100.00% | 1 | 20 |
| `ulist239.f38` | `tencent[73]` | 100.00% | 1 | 20 |
| `ulist239.f144` | `eltdx.quote_snapshot.last_price` | 100.00% | 1 | 20 |
| `ulist239.f144` | `ftshare_rest.close` | 100.00% | 1 | 20 |
| `ulist239.f144` | `fuyao.snapshot.last_price` | 100.00% | 1 | 20 |
| `ulist239.f144` | `sina[3]` | 100.00% | 1 | 20 |
| `ulist239.f144` | `tdx.quote_full.price` | 100.00% | 1 | 20 |
| `ulist239.f144` | `tencent[3]` | 100.00% | 1 | 20 |
| `zhb.full.change_pct` | `push2.f170` | 100.00% | 1 | 14 |
| `push2.f71` | `tencent[51]` | 98.39% | 4 | 62 |
| `push2.f119` | `tencent[63]` | 98.39% | 4 | 62 |
| `push2.f120` | `tencent[70]` | 98.39% | 4 | 62 |
| `push2.f164` | `tencent[39]` | 98.39% | 4 | 62 |
| `push2.f175` | `tencent[68]` | 95.16% | 4 | 62 |
| `zhb.full.change_ytd` | `push2.f122` | 92.86% | 1 | 14 |
| `push2.f167` | `tencent[46]` | 91.94% | 4 | 62 |
| `ulist239.f24` | `tencent[71]` | 90.00% | 1 | 20 |
| `push2.f58` | `sina[0]` | 87.10% | 4 | 62 |

_（仅显示前 60 / 共 149）_

## 五、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 六、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `sina_extended.turnover` | `ftshare_rest.turnover_rate` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, sina_extended | Pearson=0.9996, Spearman=0.9959, LOO稳号=True |
| `fuyao.valuation.pe_ttm` | `zhb.stat.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 60 | T:20261023, T:20261028, T:20261030 | fuyao, zhb | Pearson=0.9942, Spearman=0.9974, LOO稳号=True |
| `fuyao.valuation.pe_ttm` | `zhb.full.pe_ttm` | robust_correlation, affine_formula, per_stock_time_series, semantic_label | 60 | T:20261023, T:20261028, T:20261030 | fuyao, zhb | Pearson=0.9942, Spearman=0.9974, LOO稳号=True |
| `tencent[27]` | `tdx.quote_raw.open` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[27]` | `tdx.quote_raw.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8723, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8648, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.8648, LOO稳号=True |
| `tencent[27]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[27]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.8723, LOO稳号=True |
| `tencent[27]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[27]` | `sina[11]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.8648, LOO稳号=True |
| `tencent[27]` | `ftshare_rest.open` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[27]` | `ftshare_rest.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[27]` | `ftshare_rest.close` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8723, LOO稳号=True |
| `tencent[27]` | `ftshare_rest.avg` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8725, LOO稳号=True |
| `tencent[27]` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | eltdx, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[27]` | `eltdx.quote_snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | eltdx, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[27]` | `eltdx.quote_snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | eltdx, tencent | Pearson=0.9996, Spearman=0.8723, LOO稳号=True |
| `tencent[27]` | `eltdx.quote_snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | eltdx, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[25]` | `tdx.quote_raw.open` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[25]` | `tdx.quote_raw.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8723, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8648, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[25]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[25]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.8648, LOO稳号=True |
| `tencent[25]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[25]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.8723, LOO稳号=True |
| `tencent[25]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[25]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[25]` | `sina[11]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.8648, LOO稳号=True |
| `tencent[25]` | `ftshare_rest.open` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[25]` | `ftshare_rest.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[25]` | `ftshare_rest.close` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8723, LOO稳号=True |
| `tencent[25]` | `ftshare_rest.avg` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8725, LOO稳号=True |
| `tencent[25]` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | eltdx, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[25]` | `eltdx.quote_snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | eltdx, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[25]` | `eltdx.quote_snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | eltdx, tencent | Pearson=0.9996, Spearman=0.8723, LOO稳号=True |
| `tencent[25]` | `eltdx.quote_snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | eltdx, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[23]` | `tdx.quote_raw.open` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[23]` | `tdx.quote_raw.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[23]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8723, LOO稳号=True |
| `tencent[23]` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[23]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[23]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8648, LOO稳号=True |
| `tencent[23]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[23]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[23]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.8648, LOO稳号=True |
| `tencent[23]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[23]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.8723, LOO稳号=True |
| `tencent[23]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[23]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[23]` | `sina[11]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.8648, LOO稳号=True |
| `tencent[23]` | `ftshare_rest.open` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[23]` | `ftshare_rest.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[23]` | `ftshare_rest.close` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8723, LOO稳号=True |
| `tencent[23]` | `ftshare_rest.avg` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8725, LOO稳号=True |
| `tencent[23]` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | eltdx, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[23]` | `eltdx.quote_snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | eltdx, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[23]` | `eltdx.quote_snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | eltdx, tencent | Pearson=0.9996, Spearman=0.8723, LOO稳号=True |
| `tencent[23]` | `eltdx.quote_snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | eltdx, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[22]` | `sina[22]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[21]` | `tdx.quote_raw.open` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[21]` | `tdx.quote_raw.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[21]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8723, LOO稳号=True |
| `tencent[21]` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[21]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[21]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8648, LOO稳号=True |
| `tencent[21]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[21]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[21]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.8648, LOO稳号=True |
| `tencent[21]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[21]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.8723, LOO稳号=True |
| `tencent[21]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[21]` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[21]` | `sina[11]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=0.9996, Spearman=0.8648, LOO稳号=True |
| `tencent[21]` | `ftshare_rest.open` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[21]` | `ftshare_rest.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[21]` | `ftshare_rest.close` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8723, LOO稳号=True |
| `tencent[21]` | `ftshare_rest.avg` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | ftshare_rest, tencent | Pearson=0.9996, Spearman=0.8725, LOO稳号=True |
| `tencent[21]` | `eltdx.shortline.open_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | eltdx, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[21]` | `eltdx.quote_snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | eltdx, tencent | Pearson=0.9996, Spearman=0.8786, LOO稳号=True |
| `tencent[21]` | `eltdx.quote_snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | eltdx, tencent | Pearson=0.9996, Spearman=0.8723, LOO稳号=True |
| `tencent[21]` | `eltdx.quote_snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | eltdx, tencent | Pearson=0.9996, Spearman=0.874, LOO稳号=True |
| `tencent[20]` | `sina[20]` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[17]` | `tdx.quote_raw.open` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9999, Spearman=0.9891, LOO稳号=True |
| `tencent[17]` | `tdx.quote_raw.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=1.0, Spearman=0.9917, LOO稳号=True |
| `tencent[17]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=1.0, Spearman=0.9921, LOO稳号=True |
| `tencent[17]` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9999, Spearman=0.9891, LOO稳号=True |
| `tencent[17]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=1.0, Spearman=0.9917, LOO稳号=True |
| `tencent[17]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[17]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 120 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 | tdx, tencent | Pearson=0.9996, Spearman=0.8644, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 七、日期与数据质量告警（147）

- 20261017: 旧式非交易日目录按前一交易日 20261016 归并；目录未改名
- 20261018: 旧式非交易日目录按前一交易日 20261016 归并；目录未改名
- 20261031: 旧式非交易日目录按前一交易日 20261030 归并；目录未改名
- 20261101: 旧式非交易日目录按前一交易日 20261030 归并；目录未改名
- 20261022/ulist239: 采集状态 failed
- 20261022/ulist239: 来源状态为 failed，快照跳过
- 20261023/push2: 采集状态 partial
- 20261023/em_kline_f61: 采集状态 partial
- 20261023/em_fund_flow: 采集状态 partial
- 20261023/ulist239: 采集状态 failed
- 20261023/clist: 采集状态 partial
- 20261023/slist: 采集状态 failed
- 20261023/st_list: 采集状态 partial
- 20261023/clist: 来源状态为 partial，样本按部分快照参与
- 20261023/clist: 没有可用记录，快照跳过
- 20261023/em_fund_flow: 来源状态为 partial，样本按部分快照参与
- 20261023/em_fund_flow: 没有可用记录，快照跳过
- 20261023/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20261023/em_kline_f61: 没有可用记录，快照跳过
- 20261023/push2: 来源状态为 partial，样本按部分快照参与
- 20261023/slist: 来源状态为 failed，快照跳过
- 20261023/st_list: 来源状态为 partial，样本按部分快照参与
- 20261023/st_list: 没有可用记录，快照跳过
- 20261023/tdx_f10: 没有可用记录，快照跳过
- 20261023/tdx_f10_more: 没有可用记录，快照跳过
- 20261023/ulist239: 来源状态为 failed，快照跳过
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
- 20261026/market_sources: 来源状态为 partial，样本按部分快照参与
- 20261026/push2: 来源状态为 partial，样本按部分快照参与
- 20261026/slist: 来源状态为 failed，快照跳过
- 20261026/st_list: 来源状态为 partial，样本按部分快照参与
- 20261026/st_list: 没有可用记录，快照跳过
- 20261026/tdx_f10: 没有可用记录，快照跳过
- 20261026/tdx_f10_more: 没有可用记录，快照跳过
- 20261026/ulist239: 来源状态为 failed，快照跳过
- 20261026/zhb: 来源状态为 partial，样本按部分快照参与
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
- 另有 47 条告警，详见同名 JSON 报告。

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
| axdata | 0 | 0 | 0 | 0 | 0 | 34 / 3181 / 6 |
| clist | 18 | 0 | 0 | 18 | 0 | 33 / 7167 / 1 |
| cls | 4 | 0 | 0 | 4 | 0 | 5 / 1000 / 0 |
| datacenter | 41 | 0 | 0 | 41 | 0 | 0 / 0 / 0 |
| eltdx | 64 | 0 | 0 | 64 | 0 | 116 / 6695 / 6 |
| em_fund_flow | 0 | 0 | 0 | 0 | 0 | 15 / 300 / 1 |
| em_hot | 39 | 0 | 0 | 39 | 0 | 0 / 0 / 0 |
| em_kline_f61 | 10 | 0 | 0 | 10 | 0 | 2 / 40 / 1 |
| etf | 0 | 0 | 0 | 0 | 0 | 9 / 70080 / 6 |
| event_dc | 0 | 0 | 0 | 0 | 0 | 148 / 185204 / 6 |
| exchange | 4 | 0 | 0 | 4 | 0 | 0 / 0 / 0 |
| ftshare | 6 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| ftshare_rest | 31 | 31 | 31 | 0 | 31 | 32 / 3810 / 6 |
| fuyao | 85 | 71 | 71 | 85 | 0 | 20 / 2020 / 6 |
| kph | 6 | 0 | 0 | 6 | 0 | 15 / 2625 / 4 |
| kpl | 6 | 0 | 0 | 6 | 0 | 28 / 14246 / 6 |
| market_sources | 14 | 0 | 0 | 0 | 0 | 73 / 48883 / 6 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 2 / 90 / 0 |
| push2 | 39 | 0 | 0 | 39 | 0 | 114 / 7068 / 4 |
| push2ex | 21 | 0 | 0 | 21 | 0 | 16 / 9328 / 6 |
| reports | 26 | 0 | 0 | 26 | 0 | 49 / 441 / 0 |
| research_sina | 0 | 0 | 0 | 0 | 0 | 6 / 1446 / 0 |
| sina | 19 | 0 | 0 | 19 | 0 | 39 / 4140 / 6 |
| sina_extended | 0 | 0 | 0 | 0 | 0 | 4 / 480 / 6 |
| slist | 5 | 0 | 0 | 5 | 0 | 1 / 20 / 1 |
| sse_e_interaction | 0 | 0 | 0 | 0 | 0 | 8 / 320 / 0 |
| st_list | 0 | 0 | 0 | 0 | 0 | 6 / 1984 / 1 |
| tdx | 80 | 0 | 0 | 80 | 0 | 62 / 7680 / 6 |
| tencent | 62 | 0 | 0 | 62 | 0 | 88 / 10548 / 6 |
| ulist239 | 44 | 0 | 0 | 44 | 0 | 239 / 4780 / 1 |
| zhb | 85 | 0 | 0 | 85 | 0 | 124 / 6590 / 3 |

| 来源 | 破解目标 | 比较字段 | 作目标比较 | 作右侧比较 | L1-C 锚比较 | L1 / L1-C / L4 关系 | 方法候选涉及 |
|:--|--:|--:|--:|--:|--:|--:|--:|
| axdata | 30 | 0 | 627 | 0 | 0 | 0 / 0 / 5 | 70 |
| clist | 11 | 16 | 2614 | 2416 | 0 | 0 / 0 / 0 | 0 |
| cls | 2 | 0 | 376 | 0 | 0 | 0 / 0 / 0 | 0 |
| datacenter | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| eltdx | 30 | 50 | 5970 | 12275 | 0 | 0 / 0 / 11 | 1075 |
| em_fund_flow | 15 | 0 | 3900 | 0 | 0 | 0 / 0 / 0 | 393 |
| em_hot | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| em_kline_f61 | 1 | 0 | 260 | 0 | 0 | 0 / 0 / 0 | 1 |
| etf | 4 | 0 | 29 | 0 | 0 | 0 / 0 / 0 | 0 |
| event_dc | 61 | 0 | 1235 | 0 | 0 | 0 / 0 / 0 | 380 |
| exchange | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare_rest | 1 | 25 | 23 | 10293 | 10293 | 0 / 0 / 15 | 1350 |
| fuyao | 4 | 10 | 1376 | 3540 | 0 | 0 / 0 / 9 | 650 |
| kph | 4 | 6 | 1066 | 2130 | 0 | 0 / 0 / 0 | 14 |
| kpl | 15 | 6 | 4810 | 4128 | 0 | 0 / 0 / 0 | 43 |
| market_sources | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| push2 | 58 | 34 | 13850 | 4702 | 0 | 0 / 0 / 41 | 2589 |
| push2ex | 10 | 2 | 2600 | 302 | 0 | 0 / 0 / 0 | 35 |
| reports | 12 | 6 | 2382 | 762 | 0 | 0 / 0 / 0 | 0 |
| research_sina | 2 | 0 | 358 | 0 | 0 | 0 / 0 / 0 | 0 |
| sina | 15 | 18 | 5085 | 5190 | 0 | 0 / 0 / 24 | 1580 |
| sina_extended | 3 | 0 | 1017 | 0 | 0 | 0 / 0 / 12 | 178 |
| slist | 1 | 0 | 260 | 0 | 0 | 0 / 0 / 0 | 10 |
| sse_e_interaction | 2 | 0 | 25 | 0 | 0 | 0 / 0 / 0 | 0 |
| st_list | 3 | 0 | 48 | 0 | 0 | 0 / 0 / 0 | 0 |
| tdx | 15 | 42 | 3604 | 11298 | 0 | 0 / 0 / 50 | 1681 |
| tencent | 22 | 56 | 6360 | 17664 | 0 | 2 / 0 / 48 | 2951 |
| ulist239 | 128 | 44 | 28360 | 6068 | 0 | 0 / 0 / 67 | 1903 |
| zhb | 44 | 55 | 9328 | 14795 | 0 | 2 / 0 / 16 | 1941 |

## AxData 每日接口核验

> 此处汇总采集目录已保存的本地证据，不发起网络请求、不改变注册表状态；AxData 是多源框架，不作为独立字段锚。

### AxData

窗口内有 7 个唯一数据日的轮验记录；重复目录合并 0 条。
静态接口队列：257 个接口，3343 个字段出现项，低于 E3 的字段出现项 3343；当前主动探针白名单 `tencent_realtime_snapshot`。
静态候选策略：static review only until route, parameters, date basis, and request safety are approved。

| 数据日 | 轮验状态 | 探针状态 / 请求数 | 来源身份状态 | 短线配对 | KPH/KPL 配对 | 证据文件 |
|:--|:--|:--|:--|--:|--:|:--|
| 20261022 | not_eligible | not_run / 0 (字段相同/不同 0/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing | — | — | meta_summary |
| 20261023 | already_recorded | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261026 | already_recorded | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | — | — | full |
| 20261028 | sampled | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261029 | sampled | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261030 | already_recorded | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | 44 | full |
| 20261102 | sampled | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |

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
| `axdata_shortline_vs_eltdx:open_volume_ratio` | 16 | 84 | 0 |
| `axdata_shortline_vs_eltdx:open_amount` | 17 | 83 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_hand` | 17 | 83 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_amount_ratio` | 19 | 81 | 0 |
| `axdata_shortline_vs_eltdx:auction_prev_volume_ratio` | 26 | 73 | 1 |
| `axdata_shortline_vs_eltdx:open_turnover_z` | 49 | 51 | 0 |
| `axdata_shortline_vs_eltdx:ladder_level` | 0 | 6 | 94 |
| `axdata_shortline_vs_eltdx:limit_board_text` | 5 | 5 | 90 |
| `axdata_shortline_vs_eltdx:open_prev_seal_ratio` | 3 | 4 | 93 |

## 字母字段名语义提示（仅候选）

窗口内观察到 191 条需审阅的字母字段路径：含词义线索 52 条，仅拆词 139 条。
完整逐条记录保存在碰撞 JSON；名称线索清单：`docs/field_verification/20261014/20261014_alphabetic_field_name_inventory.csv`。
> 拼音、英文、缩写和混合拆词只用于检索候选；必须结合原始值、接口定义和独立来源复核，不得据此定案或改写主字典。

| 逐源字段路径 | 状态/审阅范围 | 名称形式与拆词 | 词义线索（非释义） | 样本日期 |
|:--|:--|:--|:--|:--|
| `市场源(market_sources)::change_type` | unverified / unverified_semantics | snake_case_or_mixed: change type | 变化/涨跌 + 类型 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `市场源(market_sources)::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `东财-push2ex::change_pct` | unverified / unverified_semantics | recognized_english_word_candidate: change pct | 变化/涨跌 + 百分比 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `东财-push2ex::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `东财-push2ex::first_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: first limit time | 首次/第一 + 涨跌停限制 + 时间 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `东财-push2ex::last_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: last limit time | 最近/上一期 + 涨跌停限制 + 时间 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `东财-push2ex::limit_count` | unverified / unverified_semantics | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `东财-push2ex::name` | unverified / unverified_semantics | recognized_english_word_candidate: name | 名称 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `东财-push2ex::price` | unverified / unverified_semantics | recognized_english_word_candidate: price | 价格 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `东财-push2ex::total_value` | unverified / unverified_semantics | snake_case_or_mixed: total value | 总 + 值 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `市场源(market_sources)::limit_count` | verified / verified_metadata_gap | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `市场源(market_sources)::limit_time` | unverified / unverified_semantics | snake_case_or_mixed: limit time | 涨跌停限制 + 时间 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `市场源(market_sources)::plate_limit_up_count` | verified / verified_metadata_gap | snake_case_or_mixed: plate limit up count | 涨跌停限制 + 上/涨 + 数量/次数 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `财联社(cls)::time` | unverified / unverified_semantics | recognized_english_word_candidate: time | 时间 | C:20261028, C:20261029, C:20261031, C:20261102 |
| `开盘红(Levistock适配)::limit_count` | unverified / unverified_semantics | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261022, T:20261023, T:20261028, T:20261030 |
| `开盘红(Levistock适配)::open_time` | unverified / unverified_semantics | snake_case_or_mixed: open time | 开盘 + 时间 | T:20261022, T:20261023, T:20261028, T:20261030 |
| `TDX(双命名源)::changqifuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: changqifuzhai | 长期负债 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::cunhuo` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: cunhuo | 存货 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::eps` | unverified / unverified_semantics | recognized_english_word_candidate: eps | 每股收益 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::fajirenfarengu` | unverified / unverified_semantics | recognized_pinyin_phrase_candidate: fajirenfarengu | 疑似 faqirenfarengu 的拼写变体；含义未证实 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::gudongrenshu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: gudongrenshu | 股东人数 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::ipodate` | unverified / unverified_semantics | recognized_english_phrase_candidate: ipodate | IPO/上市日期（字段语境候选） | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::jinglirun` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jinglirun | 净利润 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::jingyingxianjinliu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingyingxianjinliu | 经营现金流 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::jingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingzichan | 净资产 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::liudongfuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: liudongfuzhai | 流动负债 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::meigujingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: meigujingzichan | 每股净资产 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::price` | unverified / unverified_semantics | recognized_english_word_candidate: price | 价格 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::yingshouzhangkuan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: yingshouzhangkuan | 应收账款 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::zhuyingshouru` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zhuyingshouru | 主营收入 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::zibengongjijin` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zibengongjijin | 资本公积金 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::zongzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongzichan | 总资产 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `新浪(扩展API)::turnover` | conflict / unverified_semantics | recognized_english_word_candidate: turnover | 换手/成交额（需看接口） | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `同花顺-fuyao::snapshot.open_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot open price | 开盘 + 价格 | T:20261023, T:20261028, T:20261029, T:20261030, T:20261102 |
| `同花顺-fuyao::valuation.pb_mrq` | conflict / unverified_semantics | snake_case_or_mixed: valuation pb mrq | 市净率 + 最近报告期 | T:20261023, T:20261028, T:20261029, T:20261030, T:20261102 |
| `同花顺-fuyao::valuation.pe_mrq` | conflict / unverified_semantics | snake_case_or_mixed: valuation pe mrq | 市盈率 + 最近报告期 | T:20261023, T:20261028, T:20261029, T:20261030, T:20261102 |
| `同花顺-fuyao::valuation.pe_ttm` | conflict / unverified_semantics | snake_case_or_mixed: valuation pe ttm | 市盈率 + 滚动十二个月 | T:20261023, T:20261028, T:20261029, T:20261030, T:20261102 |
| `ZHB-tdxstat::change_pct` | unverified / unverified_semantics | recognized_english_word_candidate: change pct | 变化/涨跌 + 百分比 | T:20261023, T:20261028, T:20261030 |
| `ZHB-tdxstat::change_pct_1d` | unverified / unverified_semantics | snake_case_or_mixed: change pct 1 d | 变化/涨跌 + 百分比 | T:20261023, T:20261028, T:20261030 |
| `ZHB-tdxstat::change_pct_2d` | unverified / unverified_semantics | snake_case_or_mixed: change pct 2 d | 变化/涨跌 + 百分比 | T:20261023, T:20261028, T:20261030 |
| `ZHB-tdxstat2::main_net_buy_amount` | unverified / unverified_semantics | snake_case_or_mixed: main net buy amount | 净 + 金额/成交额（需看接口） | T:20261023, T:20261028, T:20261030 |
| `ZHB-tdxstat2::main_net_buy_amount_1d` | unverified / unverified_semantics | snake_case_or_mixed: main net buy amount 1 d | 净 + 金额/成交额（需看接口） | T:20261023, T:20261028, T:20261030 |
| `reports::actualLastTwoYearEps` | unverified / unverified_semantics | camel_case_or_mixed: actual Last Two Year Eps | 最近/上一期 + 每股收益 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102 |
| `reports::actualLastYearEps` | unverified / unverified_semantics | camel_case_or_mixed: actual Last Year Eps | 最近/上一期 + 每股收益 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102 |
| `reports::count` | verified / verified_metadata_gap | recognized_english_word_candidate: count | 数量/次数 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102 |
| `reports::lastEmRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Code | 最近/上一期 + 代码 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102 |
| `reports::lastEmRatingName` | conflict / unverified_semantics | camel_case_or_mixed: last Em Rating Name | 最近/上一期 + 名称 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102 |
| `reports::lastEmRatingValue` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Value | 最近/上一期 + 值 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102 |
| `reports::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102 |
| `reports::predictLastYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Eps | 最近/上一期 + 每股收益 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102 |
| `reports::predictLastYearPe` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Pe | 最近/上一期 + 市盈率 | C:20261027, C:20261028, C:20261029, C:20261030, C:20261031, C:20261101, C:20261102 |
| `TDX-eltdx(适配层)::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `东财-push2ex::broken_count` | unverified / unverified_semantics | snake_case_or_mixed: broken count | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `东财-push2ex::circulating_value` | unverified / unverified_semantics | snake_case_or_mixed: circulating value | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `东财-push2ex::sector` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: sector | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `东财-push2ex::turnover_rate` | unverified / unverified_semantics | snake_case_or_mixed: turnover rate | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `东财-push2ex::zt_continuous` | unverified / unverified_semantics | snake_case_or_mixed: zt continuous | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `东财-push2ex::zt_days` | unverified / unverified_semantics | snake_case_or_mixed: zt days | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `市场源(market_sources)::one_word` | unverified / unverified_semantics | snake_case_or_mixed: one word | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `市场源(market_sources)::plate_amount` | verified / verified_metadata_gap | snake_case_or_mixed: plate amount | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `市场源(market_sources)::plate_code` | verified / verified_metadata_gap | snake_case_or_mixed: plate code | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `市场源(market_sources)::plate_name` | verified / verified_metadata_gap | snake_case_or_mixed: plate name | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `市场源(market_sources)::popular` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: popular | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `财联社(cls)::content` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: content | — | C:20261028, C:20261029, C:20261031, C:20261102 |
| `财联社(cls)::level` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: level | — | C:20261028, C:20261029, C:20261031, C:20261102 |
| `财联社(cls)::reading_num` | unverified / unverified_semantics | snake_case_or_mixed: reading num | — | C:20261028, C:20261029, C:20261031, C:20261102 |
| `财联社(cls)::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20261028, C:20261029, C:20261031, C:20261102 |
| `开盘红(Levistock适配)::industry_id` | unverified / unverified_semantics | snake_case_or_mixed: industry id | — | T:20261022, T:20261023, T:20261028, T:20261030 |
| `开盘红(Levistock适配)::limit_tag` | unverified / unverified_semantics | snake_case_or_mixed: limit tag | — | T:20261022, T:20261023, T:20261028, T:20261030 |
| `开盘红(Levistock适配)::reason` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: reason | — | T:20261022, T:20261023, T:20261028, T:20261030 |
| `开盘红(Levistock适配)::themes` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: themes | — | T:20261022, T:20261023, T:20261028, T:20261030 |
| `FTShare REST::amplitude` | verified / verified_metadata_gap | runtime_tokenization_only: amplitude | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `FTShare REST::avg` | verified / verified_metadata_gap | runtime_tokenization_only: avg | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `FTShare REST::bid_ask_ratio` | verified / verified_metadata_gap | runtime_tokenization_only: bid ask ratio | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `FTShare REST::board` | verified / verified_metadata_gap | runtime_tokenization_only: board | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `FTShare REST::listing_date` | verified / verified_metadata_gap | runtime_tokenization_only: listing date | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `FTShare REST::name` | verified / verified_metadata_gap | runtime_tokenization_only: name | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `FTShare REST::st` | verified / verified_metadata_gap | runtime_tokenization_only: st | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `FTShare REST::status` | verified / verified_metadata_gap | runtime_tokenization_only: status | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `FTShare REST::symbol` | verified / verified_metadata_gap | runtime_tokenization_only: symbol | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `FTShare REST::symbol_id` | unverified / unverified_semantics | runtime_tokenization_only: symbol id | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `FTShare REST::turnover_rate` | verified / verified_metadata_gap | runtime_tokenization_only: turnover rate | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::ask1` | unverified / unverified_semantics | mixed_alphanumeric: ask 1 | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::ask1_vol` | unverified / unverified_semantics | runtime_tokenization_only: ask 1 vol | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::b_vol` | unverified / unverified_semantics | snake_case_or_mixed: b vol | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::b_vol` | unverified / unverified_semantics | snake_case_or_mixed: b vol | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::baoliu2` | unverified / unverified_semantics | mixed_alphanumeric: baoliu 2 | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::bid1` | unverified / unverified_semantics | mixed_alphanumeric: bid 1 | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::bid1_vol` | unverified / unverified_semantics | snake_case_or_mixed: bid 1 vol | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::ipo_date` | verified / verified_metadata_gap | snake_case_or_mixed: ipo date | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::s_vol` | unverified / unverified_semantics | snake_case_or_mixed: s vol | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::s_vol` | unverified / unverified_semantics | snake_case_or_mixed: s vol | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::updated_date` | verified / verified_metadata_gap | snake_case_or_mixed: updated date | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::updateddate` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: updateddate | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `TDX(双命名源)::zhuyinglyrun` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: zhuyinglyrun | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `同花顺-fuyao::fin_report` | unverified / unverified_semantics | snake_case_or_mixed: fin report | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `市场源(market_sources)::big_order_300w_net` | unverified / unverified_semantics | runtime_tokenization_only: big order 300 w net | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |
| `市场源(market_sources)::institution_add` | unverified / unverified_semantics | runtime_tokenization_only: institution add | — | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030, T:20261102 |

Markdown 显示前 100 条；其余 91 条完整保留在 JSON。

## 探索候选持续跟踪

研究台账：`collision_research_state.json.gz`；累计历史跟踪候选对 2069，本报告候选对 882，历史复现 693，新发现 0。
台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，不会自动改变字段状态、碰撞锚或主字典。新报告只将 `actionable_L1`、L4 和主动方法候选写入待研究队列；已登记关系的复验单独展示，历史跟踪记录不会被删除。

## 候选覆盖、公式与下一步采样

本节用于定位证据缺口和安排后续取样。相关性、公式与样本优先级均为探索候选；不会改变 L1/L1-U 门槛、来源独立性或主字典。

- 未知目标 495 个；其中有方法候选 309 个、无候选 186 个；多候选目标 281 个。
- 方法候选生成 8422 条；全局详细项保留 500/500，另按目标字段保留 289 条；完整明细 8422 条在 JSON `method_candidate_inventory`；未归档明细 0 条。
- 字段覆盖详情：available；覆盖身份 1921，读取 7 份本地索引。

### 优先处理字段

| 未知字段 | 当前诊断 | 独立对比/候选数 | 独立锚家族/本源日期 | 建议复核股票 | 最强候选线索 |
|:--|:--|--:|:--|:--|:--|
| `sina[13]` | 存在多个候选，需区分 | 316 / 113 | 6 家族 / 316 对 / 本源 0 日 | 600519 (6.304742) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[15]` | 存在多个候选，需区分 | 316 / 113 | 6 家族 / 316 对 / 本源 0 日 | 600519 (6.30239) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[17]` | 存在多个候选，需区分 | 316 / 113 | 6 家族 / 316 对 / 本源 0 日 | 600519 (6.293705) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina_extended.trade` | 存在多个候选，需区分 | 316 / 113 | 6 家族 / 316 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[19]` | 存在多个候选，需区分 | 316 / 112 | 6 家族 / 316 对 / 本源 0 日 | 600519 (6.650831) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f135` | 存在多个候选，需区分 | 237 / 94 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[25]` | 存在多个候选，需区分 | 316 / 94 | 6 家族 / 316 对 / 本源 0 日 | 600519 (12.975898) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[27]` | 存在多个候选，需区分 | 316 / 94 | 6 家族 / 316 对 / 本源 0 日 | 600519 (12.982044) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `sina[29]` | 存在多个候选，需区分 | 316 / 94 | 6 家族 / 316 对 / 本源 0 日 | 600519 (12.988787) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[11]` | 存在多个候选，需区分 | 279 / 94 | 6 家族 / 279 对 / 本源 0 日 | no_shared_stock_holdout | tdx.quote_raw.open (robust_correlation,affine_formula,per_stock_time_series); tdx.quote_raw.low (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[13]` | 存在多个候选，需区分 | 279 / 94 | 6 家族 / 279 对 / 本源 0 日 | no_shared_stock_holdout | tdx.quote_raw.open (robust_correlation,affine_formula,per_stock_time_series); tdx.quote_raw.low (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[15]` | 存在多个候选，需区分 | 279 / 94 | 6 家族 / 279 对 / 本源 0 日 | no_shared_stock_holdout | tdx.quote_raw.open (robust_correlation,affine_formula,per_stock_time_series); tdx.quote_raw.low (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f120` | 存在多个候选，需区分 | 237 / 93 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[70] (robust_correlation,affine_formula,per_stock_time_series); tencent[57] (robust_correlation,per_stock_time_series) |
| `sina[23]` | 存在多个候选，需区分 | 316 / 93 | 6 家族 / 316 对 / 本源 0 日 | 600519 (12.97017) | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[17]` | 存在多个候选，需区分 | 279 / 93 | 6 家族 / 279 对 / 本源 0 日 | no_shared_stock_holdout | tdx.quote_raw.open (robust_correlation,affine_formula,per_stock_time_series); tdx.quote_raw.high (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f141` | 存在多个候选，需区分 | 237 / 91 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f142` | 存在多个候选，需区分 | 237 / 85 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f108` | 存在多个候选，需区分 | 237 / 84 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[68] (robust_correlation,affine_formula) |
| `push2.f145` | 存在多个候选，需区分 | 237 / 84 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f71` | 存在多个候选，需区分 | 237 / 83 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f92` | 存在多个候选，需区分 | 237 / 82 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tdx.finance_info.meigujingzichan (robust_correlation,affine_formula,per_stock_time_series); fuyao.snapshot.last_price (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f138` | 存在多个候选，需区分 | 237 / 80 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[70] (robust_correlation,per_stock_time_series); tencent[69] (robust_correlation,per_stock_time_series) |
| `push2.f160` | 存在多个候选，需区分 | 237 / 80 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[68] (robust_correlation,affine_formula) |
| `tencent[23]` | 存在多个候选，需区分 | 279 / 80 | 6 家族 / 279 对 / 本源 0 日 | no_shared_stock_holdout | tdx.quote_raw.open (robust_correlation,affine_formula,per_stock_time_series); tdx.quote_raw.high (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[25]` | 存在多个候选，需区分 | 279 / 80 | 6 家族 / 279 对 / 本源 0 日 | no_shared_stock_holdout | tdx.quote_raw.open (robust_correlation,affine_formula,per_stock_time_series); tdx.quote_raw.high (robust_correlation,affine_formula,per_stock_time_series) |
| `tencent[27]` | 存在多个候选，需区分 | 279 / 80 | 6 家族 / 279 对 / 本源 0 日 | no_shared_stock_holdout | tdx.quote_raw.open (robust_correlation,affine_formula,per_stock_time_series); tdx.quote_raw.high (robust_correlation,affine_formula,per_stock_time_series) |
| `fuyao.valuation.pb_mrq` | 存在多个候选，需区分 | 321 / 79 | 6 家族 / 321 对 / 本源 5 日 | 600519 (14.523453) | tencent[46] (robust_correlation,affine_formula,per_stock_time_series); ulist239.f23 (robust_correlation,affine_formula) |
| `push2.f190` | 存在多个候选，需区分 | 237 / 79 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tdx.finance_info.meigujingzichan (robust_correlation,affine_formula,per_stock_time_series); tencent[9] (robust_correlation,affine_formula) |
| `tencent[21]` | 存在多个候选，需区分 | 279 / 79 | 6 家族 / 279 对 / 本源 0 日 | no_shared_stock_holdout | tdx.quote_raw.open (robust_correlation,affine_formula,per_stock_time_series); tdx.quote_raw.high (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f136` | 存在多个候选，需区分 | 237 / 77 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[57] (robust_correlation,affine_formula,per_stock_time_series); tencent[37] (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f175` | 存在多个候选，需区分 | 237 / 77 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[68] (robust_correlation,affine_formula,per_stock_time_series); tencent[5] (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f139` | 存在多个候选，需区分 | 237 / 74 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[70] (robust_correlation,per_stock_time_series); tencent[57] (robust_correlation,per_stock_time_series) |
| `tdx.quote_raw.bid1` | 存在多个候选，需区分 | 189 / 73 | 6 家族 / 189 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `tdx.quote_raw.price` | 存在多个候选，需区分 | 189 / 73 | 6 家族 / 189 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `push2.f60` | 存在多个候选，需区分 | 237 / 71 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[5] (robust_correlation,affine_formula,per_stock_time_series); tencent[51] (robust_correlation,affine_formula,per_stock_time_series) |
| `ulist239.f37` | 存在多个候选，需区分 | 237 / 69 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation); tencent[68] (robust_correlation) |
| `push2.f119` | 存在多个候选，需区分 | 237 / 66 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[63] (robust_correlation,affine_formula,per_stock_time_series); ftshare_rest.change_rate_day5 (robust_correlation,affine_formula,per_stock_time_series) |
| `tdx.quote_raw.ask1` | 存在多个候选，需区分 | 189 / 66 | 6 家族 / 189 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula,per_stock_time_series); tencent[85] (robust_correlation,affine_formula,per_stock_time_series) |
| `ulist239.f48` | 存在多个候选，需区分 | 237 / 66 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[68] (robust_correlation,affine_formula) |
| `ulist239.f143` | 存在多个候选，需区分 | 237 / 65 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[85] (robust_correlation,affine_formula) |
| `ulist239.f32` | 存在多个候选，需区分 | 237 / 65 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[85] (robust_correlation,affine_formula) |
| `ulist239.f36` | 存在多个候选，需区分 | 237 / 65 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation); tencent[76] (affine_formula) |
| `zhb.full.change_20k_bar` | 存在多个候选，需区分 | 189 / 65 | 6 家族 / 189 对 / 本源 0 日 | 600519 (7.071637) | tencent[70] (robust_correlation,affine_formula,per_stock_time_series); tencent[75] (robust_correlation,per_stock_time_series) |
| `push2.f174` | 存在多个候选，需区分 | 237 / 63 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[67] (robust_correlation,affine_formula,per_stock_time_series); tencent[48] (robust_correlation,affine_formula,per_stock_time_series) |
| `zhb.full.change_mtd` | 存在多个候选，需区分 | 189 / 63 | 6 家族 / 189 对 / 本源 3 日 | 600519 (9.785155) | tencent[70] (robust_correlation,per_stock_time_series); tencent[69] (robust_correlation,per_stock_time_series) |
| `tdx.finance_info.eps` | 存在多个候选，需区分 | 189 / 61 | 6 家族 / 189 对 / 本源 0 日 | no_shared_stock_holdout | fuyao.snapshot.last_price (robust_correlation,affine_formula,per_stock_time_series); push2.f55 (robust_correlation,affine_formula,per_stock_time_series) |
| `ulist239.f142` | 存在多个候选，需区分 | 237 / 61 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[85] (robust_correlation,affine_formula) |
| `ulist239.f144` | 存在多个候选，需区分 | 237 / 61 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[85] (robust_correlation,affine_formula) |
| `ulist239.f31` | 存在多个候选，需区分 | 237 / 61 | 6 家族 / 237 对 / 本源 0 日 | no_shared_stock_holdout | tencent[9] (robust_correlation,affine_formula); tencent[85] (robust_correlation,affine_formula) |
| `zhb.full.change_ytd` | 存在多个候选，需区分 | 189 / 59 | 6 家族 / 189 对 / 本源 3 日 | 600825 (3.982324) | tencent[75] (robust_correlation,affine_formula,per_stock_time_series); tencent[62] (robust_correlation,affine_formula,per_stock_time_series) |

_此表显示优先级最高的 50 / 共 495 个目标；完整清单见 JSON。_


### 补足全局截断的字段候选（289）

| 未知字段 | 候选字段 | 方法 | 样本 | 日期 | 来源 |
|:--|:--|:--|--:|:--|:--|
| `axdata.data.float_shares` | `ftshare_rest.float_a_shares` | robust_correlation, affine_formula, semantic_label | 119 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `axdata.data.free_float_shares` | `ftshare_rest.shares` | robust_correlation, affine_formula | 119 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `axdata.data.limit_stat_days` | `ftshare_rest.turnover` | robust_correlation | 19 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `axdata.data.limit_up_count_in_stat_days` | `ftshare_rest.turnover` | robust_correlation | 19 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `axdata.data.limit_up_streak_days` | `ftshare_rest.change_rate_day5` | robust_correlation | 15 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `axdata.data.open_amount` | `ftshare_rest.volume` | robust_correlation | 119 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `axdata.data.open_prev_amount_ratio` | `ftshare_rest.turnover` | robust_correlation | 119 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `axdata.data.open_price` | `ftshare_rest.prev_close` | robust_correlation, affine_formula, per_stock_time_series | 119 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `axdata.data.open_turnover_z` | `ftshare_rest.turnover_rate` | robust_correlation | 119 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `axdata.data.open_volume_hand` | `ftshare_rest.volume` | robust_correlation | 119 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `axdata.data.open_volume_ratio` | `ftshare_rest.turnover` | robust_correlation | 119 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `axdata.data.pre_close` | `ftshare_rest.prev_close` | robust_correlation, affine_formula, per_stock_time_series | 119 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `axdata.data.prev_amount` | `ftshare_rest.volume` | robust_correlation | 119 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `axdata.data.prev_open_amount` | `ftshare_rest.volume` | robust_correlation | 117 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `axdata.data.prev_open_volume_hand` | `ftshare_rest.volume` | robust_correlation | 117 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `axdata.data.seal_to_float_ratio` | `ftshare_rest.turnover_rate` | robust_correlation | 119 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `axdata.data.year_limit_up_days` | `ftshare_rest.turnover` | per_stock_time_series | 119 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | axdata, ftshare_rest |
| `em_fund_flow.f135` | `tencent[57]` | robust_correlation, affine_formula | 20 | T:20261102 | em_fund_flow, tencent |
| `em_fund_flow.f136` | `tencent[57]` | robust_correlation, affine_formula | 19 | T:20261102 | em_fund_flow, tencent |
| `em_fund_flow.f137` | `tencent[74]` | robust_correlation | 20 | T:20261102 | em_fund_flow, tencent |
| `em_fund_flow.f138` | `tencent[70]` | robust_correlation | 17 | T:20261102 | em_fund_flow, tencent |
| `em_fund_flow.f139` | `tencent[70]` | robust_correlation | 17 | T:20261102 | em_fund_flow, tencent |
| `em_fund_flow.f140` | `tencent[74]` | robust_correlation | 20 | T:20261102 | em_fund_flow, tencent |
| `em_fund_flow.f141` | `tencent[57]` | robust_correlation, affine_formula | 20 | T:20261102 | em_fund_flow, tencent |
| `em_fund_flow.f142` | `tencent[57]` | robust_correlation, affine_formula | 19 | T:20261102 | em_fund_flow, tencent |
| `em_fund_flow.f143` | `tencent[80]` | robust_correlation | 20 | T:20261102 | em_fund_flow, tencent |
| `em_fund_flow.f144` | `tencent[57]` | robust_correlation, affine_formula | 20 | T:20261102 | em_fund_flow, tencent |
| `em_fund_flow.f145` | `tencent[57]` | robust_correlation, affine_formula | 20 | T:20261102 | em_fund_flow, tencent |
| `em_fund_flow.f146` | `eltdx.shortline.seal_amount` | robust_correlation | 20 | T:20261102 | eltdx, em_fund_flow |
| `em_fund_flow.f147` | `tencent[57]` | robust_correlation, affine_formula | 19 | T:20261102 | em_fund_flow, tencent |
| `em_fund_flow.f148` | `tencent[70]` | robust_correlation | 20 | T:20261102 | em_fund_flow, tencent |
| `em_fund_flow.f149` | `tencent[38]` | robust_correlation | 20 | T:20261102 | em_fund_flow, tencent |
| `em_kline_f61.dktotal` | `tencent[2]` | robust_correlation | 20 | T:20261102 | em_kline_f61, tencent |
| `event_dc.AMPLITUDE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.CHANGE` | `ftshare_rest.change_rate` | robust_correlation, affine_formula, semantic_label | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.CHANGE_RATE` | `ftshare_rest.change_rate` | robust_correlation, affine_formula, semantic_label | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.CLOSE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.EACHBALLOT_SHARES` | `ftshare_rest.shares` | semantic_label | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.INDUSTRY_PE` | `ftshare_rest.ts_millis` | robust_correlation | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.INDUSTRY_PE_NEW` | `ftshare_rest.ts_millis` | robust_correlation | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.IPO_YIELD` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.ISSUE_NUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.ISSUE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.LATELY_PRICE` | `ftshare_rest.close` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.LD_AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.LD_CLOSE_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.LD_HIGH_CHANG` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.LD_OPEN_PREMIUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.LIMIT_UP_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.MZYQ_PAY_FUND` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.OD_HIGH_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.OPEN_AVERAGE_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.OPEN_PRICE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.PROFIT` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.TCHANGE_RATE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.TNEW_PRICE` | `ftshare_rest.close` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.TOTAL_CHANGE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.TOTAL_ISSUE_NUM` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.TOTAL_SHARES` | `ftshare_rest.shares` | robust_correlation, affine_formula, semantic_label | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.TURNOVERRATE` | `ftshare_rest.shares` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `event_dc.fetched_at` | `ftshare_rest.ts_millis` | robust_correlation, affine_formula | 12 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | event_dc, ftshare_rest |
| `fuyao.valuation.pb_mrq` | `tencent[46]` | robust_correlation, affine_formula, per_stock_time_series | 100 | T:20261023, T:20261028, T:20261029, T:20261030, T:20261102 | fuyao, tencent |
| `fuyao.valuation.pe_mrq` | `tencent[52]` | robust_correlation, affine_formula, per_stock_time_series | 100 | T:20261023, T:20261028, T:20261029, T:20261030, T:20261102 | fuyao, tencent |
| `fuyao.valuation.pe_ttm` | `tencent[39]` | robust_correlation, affine_formula, per_stock_time_series | 100 | T:20261023, T:20261028, T:20261029, T:20261030, T:20261102 | fuyao, tencent |
| `fuyao.valuation.ps_ttm` | `tencent[46]` | robust_correlation, per_stock_time_series | 100 | T:20261023, T:20261028, T:20261029, T:20261030, T:20261102 | fuyao, tencent |
| `kpl.amplitude` | `push2ex.limit_fund` | per_stock_time_series | 394 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | kpl, push2ex |
| `kpl.main_buy` | `push2ex.amount` | robust_correlation, per_stock_time_series | 394 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | kpl, push2ex |
| `kpl.main_sell` | `push2ex.amount` | robust_correlation, per_stock_time_series | 394 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | kpl, push2ex |
| `kpl.raw_columns.col_09` | `push2ex.amount` | robust_correlation, per_stock_time_series | 394 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | kpl, push2ex |
| `kpl.raw_columns.col_10` | `push2ex.amount` | robust_correlation, per_stock_time_series | 394 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | kpl, push2ex |
| `kpl.raw_columns.col_13` | `push2ex.amount` | robust_correlation | 394 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | kpl, push2ex |
| `kpl.raw_columns.col_16` | `push2ex.limit_fund` | per_stock_time_series | 394 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | kpl, push2ex |
| `kpl.raw_columns.col_17` | `push2ex.limit_fund` | per_stock_time_series | 394 | T:20261023, T:20261026, T:20261028, T:20261029, T:20261030 | kpl, push2ex |
| `push2.f103` | `tdx.finance_info.jingzichan` | robust_correlation, affine_formula | 62 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tdx |
| `push2.f108` | `tencent[9]` | robust_correlation, affine_formula | 62 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f109` | `tdx.finance_info.weifenlirun` | robust_correlation, affine_formula | 62 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tdx |
| `push2.f119` | `tencent[63]` | robust_correlation, affine_formula, per_stock_time_series | 62 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f120` | `tencent[70]` | robust_correlation, affine_formula, per_stock_time_series | 62 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f135` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 62 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f136` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 61 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f137` | `zhb.stat2.change_250k_bar` | robust_correlation | 14 | T:20261023 | push2, zhb |
| `push2.f138` | `tencent[70]` | robust_correlation, per_stock_time_series | 53 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f139` | `tencent[70]` | robust_correlation, per_stock_time_series | 51 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f140` | `zhb.stat.change_pct` | robust_correlation | 14 | T:20261023 | push2, zhb |
| `push2.f141` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 62 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f142` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 61 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f143` | `zhb.stat2.low_52w` | affine_formula | 14 | T:20261023 | push2, zhb |
| `push2.f144` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 62 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f145` | `tencent[57]` | robust_correlation, affine_formula, per_stock_time_series | 62 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f146` | `zhb.stat.streak_days` | robust_correlation | 14 | T:20261023 | push2, zhb |
| `push2.f147` | `tencent[57]` | robust_correlation, per_stock_time_series | 59 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f148` | `tencent[57]` | robust_correlation, per_stock_time_series | 62 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f149` | `zhb.stat.free_ltgb` | robust_correlation | 14 | T:20261023 | push2, zhb |
| `push2.f160` | `tencent[9]` | robust_correlation, affine_formula | 62 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f161` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 62 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, sina |
| `push2.f162` | `tencent[52]` | robust_correlation, affine_formula, per_stock_time_series | 62 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f163` | `tencent[53]` | robust_correlation, affine_formula, per_stock_time_series | 62 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f164` | `tencent[39]` | robust_correlation, affine_formula, per_stock_time_series | 62 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |
| `push2.f165` | `tencent[9]` | per_stock_time_series | 62 | T:20261023, T:20261026, T:20261029, T:20261102 | push2, tencent |

_仅显示前 100 / 共 289 条字段前沿候选。_


### 双输入公式候选
本轮未发现通过留出筛选的公式候选；测试组合 5395 个。


### 已知映射与已证伪关系的候选校准

- 已登记正向对照：当前窗口有 170 组独立数值关系可评估，159 组被方法候选识别；样本不足 10 组。此计数仅检查方法覆盖，不是准确率。
- 已证伪负向对照：数值关系 0 组，其中仍有方法信号 0 组；这些信号被隔离，不进入普通候选。

### 采集覆盖异常源

- axdata: 20261026 ({'ok': 5, 'partial': 1})
- baidu: 20261029, 20261030, 20261102 ({'pending_validation': 6})
- clist: 20261028, 20261029, 20261030 ({'ok': 1, 'partial': 5})
- em_fund_flow: 20261028, 20261029, 20261030 ({'ok': 1, 'partial': 5})
- em_hot: 20261029, 20261030, 20261102 ({'context_only': 6})
- em_kline_f61: 20261028, 20261029, 20261030 ({'ok': 1, 'partial': 5})
- exchange: 20261029, 20261030, 20261102 ({'context_only': 6})
- ftshare: 20261029, 20261030, 20261102 ({'deprecated': 6})
- market_sources: 20261026 ({'ok': 5, 'partial': 1})
- push2: 20261028, 20261029, 20261030 ({'failed': 2, 'ok': 1, 'partial': 3})
- slist: 20261028, 20261029, 20261030 ({'failed': 5, 'ok': 1})
- st_list: 20261028, 20261029, 20261030 ({'ok': 1, 'partial': 5})
- ulist239: 20261028, 20261029, 20261030 ({'failed': 6, 'ok': 1})
- zhb: 20261028, 20261029, 20261102 ({'ok': 2, 'partial': 4})

## 候选身份与人工审阅状态

- 候选身份：生成 8571 条，唯一候选 8571 个，重复身份 0，无效身份 0。
- 审阅台账：可用；当前状态 `pending`；已审 4，待处理 8567，覆盖率 0.0%。
- 重复归并组：0；每个成员均保留到代表候选的反向追溯。
- 处置计数：`accepted_for_adjudication` 0；`duplicate_grouped` 0；`insufficient_evidence` 4；`needs_external_evidence` 0；`rejected` 0；`unreviewed` 8567。
- `accepted_for_adjudication` 只表示可进入现有证据裁决流程；审阅台账不会修改主字典或字段注册表。

## 报告完整性与审阅范围

- 机器可读完整性：`complete`；方法候选生成 8422 条，完整明细保存 8422 条，缺失 0 条，多余 0 条，重复 0 条，身份无效 0 条。
- 全量方法候选位于同名 JSON 的 `method_candidate_inventory`；Markdown 的 Top-N 表格是导航摘要，不能代替全量 JSON 审阅。
- 候选审阅数据对账：`complete`；唯一候选 8571 个，审阅 4 个，待处理 8567 个；人工审阅进度与机器清单完整性分别统计。
- Markdown 未逐行展示、但 JSON 保留的部分：
  - `L4`：展示 60 / 149，摘要省略 89 条。
  - `method_candidates`：展示 100 / 500，摘要省略 400 条。
  - `method_candidate_inventory`：展示 0 / 8422，摘要省略 8422 条。
  - `method_candidate_frontier`：展示 100 / 289，摘要省略 189 条。
  - `candidate_triage.targets`：展示 50 / 495，摘要省略 445 条。
  - `diagnostics`：展示 100 / 147，摘要省略 47 条。
  - `candidate_review.human_review.reviewed_candidates`：展示 0 / 4，摘要省略 4 条。
- 完整性对账通过；逐目标复核仍须覆盖 JSON 的全部明细，并为每项记录已检查、重复归并、证据不足或需外部核验的处置。
