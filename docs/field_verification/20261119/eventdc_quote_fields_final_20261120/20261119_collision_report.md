# 全源对撞报告（20261119）

> 交易数据窗口配置：近 7 个交易日（`--window`），行情数据截至 20261119
> 行情窗口：20261111 ~ 20261119（7 个不同交易日）｜字段 1318 个｜样本值 360736 条
> 新闻/公告自然日窗口：20261113 ~ 20261119
> 主攻目标（unverified）=92｜可审定新候选=0｜首次发现新候选对=0｜已登记关系复验=0｜异号同义 0 / 同号镜像 0

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
| `kpl.raw_columns.col_02` | `push2ex.limit_count` | weak_exact_overlap | independent_cross_source_value_comparison | diagnostic_only | 42.35% | 5 | 170 | 170 |

## 五、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 六、主动方法候选（不直接定案）（81）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `kph.industry_limit_up_count` | `kpl.raw_columns.col_20` | robust_correlation, affine_formula | 103 | T:20261116, T:20261117, T:20261118 | kph, kpl | Pearson=0.9907, Spearman=0.9816, LOO稳号=True |
| `ulist239.f63` | `zhb.tipinfo.hg_amount_yi` | robust_correlation, affine_formula | 12 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.9976, Spearman=0.7492, LOO稳号=True |
| `kph.industry_limit_up_count` | `push2ex.limit_count` | semantic_label | 103 | T:20261116, T:20261117, T:20261118 | kph, push2ex | count, limit |
| `ulist239.f63` | `zhb.stat2.change_30k_bar_ref` | robust_correlation | 40 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.5071, Spearman=0.7204, LOO稳号=True |
| `ulist239.f63` | `zhb.stat2.change_30k_bar` | robust_correlation | 40 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.5176, Spearman=0.6977, LOO稳号=True |
| `ulist239.f63` | `zhb.stat2.change_250k_bar` | robust_correlation | 40 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.4677, Spearman=0.6218, LOO稳号=True |
| `ulist239.f63` | `zhb.stat2.amount_2d` | robust_correlation | 40 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.9246, Spearman=0.9477, LOO稳号=True |
| `ulist239.f63` | `zhb.stat2.amount_1d` | robust_correlation | 40 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.9196, Spearman=0.943, LOO稳号=True |
| `ulist239.f63` | `zhb.stat2.amount` | robust_correlation | 40 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.9189, Spearman=0.949, LOO稳号=True |
| `ulist239.f63` | `zhb.stat.employee_count` | robust_correlation | 40 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.2151, Spearman=0.7245, LOO稳号=True |
| `ulist239.f63` | `zhb.stat.change_ytd` | robust_correlation | 40 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.4548, Spearman=0.6712, LOO稳号=True |
| `ulist239.f63` | `zhb.stat.change_60k_bar` | robust_correlation | 40 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.4181, Spearman=0.7353, LOO稳号=True |
| `ulist239.f63` | `zhb.stat.change_60d` | robust_correlation | 40 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.42, Spearman=0.7411, LOO稳号=True |
| `ulist239.f63` | `zhb.stat.cash_reserve_wan` | robust_correlation | 40 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.1619, Spearman=0.7072, LOO稳号=True |
| `ulist239.f63` | `zhb.full.change_60k_bar` | robust_correlation | 40 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.4181, Spearman=0.7353, LOO稳号=True |
| `ulist239.f63` | `zhb.full.change_60d` | robust_correlation | 40 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.42, Spearman=0.7411, LOO稳号=True |
| `ulist239.f63` | `zhb.full.cash_reserve_wan` | robust_correlation | 40 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.1619, Spearman=0.7072, LOO稳号=True |
| `ulist239.f63` | `zhb.full.amount` | robust_correlation | 40 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.9189, Spearman=0.949, LOO稳号=True |
| `ulist239.f63` | `tencent[79]` | robust_correlation | 40 | T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.4677, Spearman=0.6209, LOO稳号=True |
| `ulist239.f63` | `tencent[76]` | robust_correlation | 40 | T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.1495, Spearman=0.6592, LOO稳号=True |
| `ulist239.f63` | `tencent[75]` | robust_correlation | 40 | T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.4719, Spearman=0.7189, LOO稳号=True |
| `ulist239.f63` | `tencent[73]` | robust_correlation | 40 | T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.1491, Spearman=0.6325, LOO稳号=True |
| `ulist239.f63` | `tencent[72]` | robust_correlation | 40 | T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.1495, Spearman=0.6592, LOO稳号=True |
| `ulist239.f63` | `tencent[71]` | robust_correlation | 40 | T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.42, Spearman=0.7411, LOO稳号=True |
| `ulist239.f63` | `tencent[62]` | robust_correlation | 40 | T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.4548, Spearman=0.6712, LOO稳号=True |
| `ulist239.f63` | `tencent[59]` | robust_correlation | 40 | T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.2542, Spearman=0.6135, LOO稳号=True |
| `ulist239.f63` | `tencent[58]` | robust_correlation | 40 | T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.3381, Spearman=0.8946, LOO稳号=True |
| `ulist239.f63` | `tencent[57]` | robust_correlation | 40 | T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.9189, Spearman=0.949, LOO稳号=True |
| `ulist239.f63` | `tencent[45]` | robust_correlation | 40 | T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.6127, Spearman=0.7862, LOO稳号=True |
| `ulist239.f63` | `tencent[44]` | robust_correlation | 40 | T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.6403, Spearman=0.7943, LOO稳号=True |
| `ulist239.f63` | `tencent[37]` | robust_correlation | 40 | T:20261117, T:20261118 | tencent, ulist239 | Pearson=0.9189, Spearman=0.949, LOO稳号=True |
| `ulist239.f63` | `tdx.s_vol` | robust_correlation | 40 | T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.2816, Spearman=0.6548, LOO稳号=True |
| `ulist239.f63` | `tdx.quote_raw.s_vol` | robust_correlation | 40 | T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.2816, Spearman=0.6548, LOO稳号=True |
| `ulist239.f63` | `tdx.quote_raw.b_vol` | robust_correlation | 40 | T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.2682, Spearman=0.678, LOO稳号=True |
| `ulist239.f63` | `tdx.quote_raw.amount` | robust_correlation | 40 | T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.9189, Spearman=0.949, LOO稳号=True |
| `ulist239.f63` | `tdx.quote_full.s_vol` | robust_correlation | 40 | T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.2816, Spearman=0.6548, LOO稳号=True |
| `ulist239.f63` | `tdx.quote_full.b_vol` | robust_correlation | 40 | T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.2682, Spearman=0.678, LOO稳号=True |
| `ulist239.f63` | `tdx.quote_full.amount_wan` | robust_correlation | 40 | T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.9189, Spearman=0.949, LOO稳号=True |
| `ulist239.f63` | `tdx.finance_info.zongzichan` | robust_correlation | 40 | T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.1533, Spearman=0.6644, LOO稳号=True |
| `ulist239.f63` | `tdx.finance_info.zhuyingshouru` | robust_correlation | 40 | T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.3262, Spearman=0.6314, LOO稳号=True |
| `ulist239.f63` | `tdx.finance_info.zhuyinglyrun` | robust_correlation | 40 | T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.1889, Spearman=0.6704, LOO稳号=True |
| `ulist239.f63` | `tdx.finance_info.zhongguben` | robust_correlation | 40 | T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.1491, Spearman=0.6325, LOO稳号=True |
| `ulist239.f63` | `tdx.finance_info.liutongguben` | robust_correlation | 40 | T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.1495, Spearman=0.6592, LOO稳号=True |
| `ulist239.f63` | `tdx.finance_info.gudongrenshu` | robust_correlation | 40 | T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.4794, Spearman=0.7801, LOO稳号=True |
| `ulist239.f63` | `tdx.finance_info.farengu` | robust_correlation | 40 | T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.3427, Spearman=0.6456, LOO稳号=True |
| `ulist239.f63` | `tdx.b_vol` | robust_correlation | 40 | T:20261117, T:20261118 | tdx, ulist239 | Pearson=0.2682, Spearman=0.678, LOO稳号=True |
| `ulist239.f63` | `sina[9]` | robust_correlation | 40 | T:20261117, T:20261118 | sina, ulist239 | Pearson=0.9189, Spearman=0.949, LOO稳号=True |
| `ulist239.f63` | `sina[8]` | robust_correlation | 40 | T:20261117, T:20261118 | sina, ulist239 | Pearson=0.275, Spearman=0.6707, LOO稳号=True |
| `ulist239.f63` | `fuyao.snapshot.volume` | robust_correlation | 40 | T:20261117, T:20261118 | fuyao, ulist239 | Pearson=0.275, Spearman=0.6707, LOO稳号=True |
| `ulist239.f63` | `fuyao.snapshot.turnover` | robust_correlation | 40 | T:20261117, T:20261118 | fuyao, ulist239 | Pearson=0.9189, Spearman=0.949, LOO稳号=True |
| `ulist239.f63` | `ftshare_rest.volume` | robust_correlation | 40 | T:20261117, T:20261118 | ftshare_rest, ulist239 | Pearson=0.275, Spearman=0.6707, LOO稳号=True |
| `ulist239.f63` | `ftshare_rest.turnover` | robust_correlation | 40 | T:20261117, T:20261118 | ftshare_rest, ulist239 | Pearson=0.9189, Spearman=0.949, LOO稳号=True |
| `ulist239.f63` | `ftshare_rest.shares` | robust_correlation | 40 | T:20261117, T:20261118 | ftshare_rest, ulist239 | Pearson=0.1491, Spearman=0.6325, LOO稳号=True |
| `ulist239.f63` | `ftshare_rest.float_a_shares` | robust_correlation | 40 | T:20261117, T:20261118 | ftshare_rest, ulist239 | Pearson=0.1495, Spearman=0.6592, LOO稳号=True |
| `ulist239.f63` | `ftshare_rest.change_rate_ytd` | robust_correlation | 40 | T:20261117, T:20261118 | ftshare_rest, ulist239 | Pearson=0.4506, Spearman=0.6386, LOO稳号=True |
| `ulist239.f63` | `ftshare_rest.change_rate_day60` | robust_correlation | 40 | T:20261117, T:20261118 | ftshare_rest, ulist239 | Pearson=0.4154, Spearman=0.7411, LOO稳号=True |
| `ulist239.f63` | `ftshare_rest.change_rate_day120` | robust_correlation | 40 | T:20261117, T:20261118 | ftshare_rest, ulist239 | Pearson=0.4985, Spearman=0.7638, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.prev_amount` | robust_correlation | 40 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.9196, Spearman=0.943, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.open_volume_ratio` | robust_correlation | 40 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.48, Spearman=0.7562, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.open_volume_hand` | robust_correlation | 40 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.4127, Spearman=0.8553, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.open_turnover_z` | robust_correlation | 40 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.3792, Spearman=0.6384, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.open_prev_amount_ratio` | robust_correlation | 40 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.3684, Spearman=0.778, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.open_amount` | robust_correlation | 40 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.7953, Spearman=0.9754, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.float_shares` | robust_correlation | 40 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.1495, Spearman=0.6592, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.total_hand` | robust_correlation | 40 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.275, Spearman=0.6707, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.outer_disc` | robust_correlation | 40 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.2682, Spearman=0.678, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.open_amount_yuan` | robust_correlation | 40 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.7953, Spearman=0.9754, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.open_amount_raw` | robust_correlation | 40 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.7953, Spearman=0.9754, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.inside_dish` | robust_correlation | 40 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.2816, Spearman=0.6548, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.current_hand` | robust_correlation | 40 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.1693, Spearman=0.7598, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.amount_raw` | robust_correlation | 40 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.6324, Spearman=0.949, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.amount` | robust_correlation | 40 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.9189, Spearman=0.949, LOO稳号=True |
| `ulist239.f63` | `eltdx.quote_snapshot.active1` | robust_correlation | 40 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.3993, Spearman=0.8707, LOO稳号=True |
| `ulist239.f63` | `zhb.stat2.main_net_buy_hands_1d` | robust_correlation | 39 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.2247, Spearman=0.7445, LOO稳号=True |
| `ulist239.f63` | `zhb.stat2.main_net_buy_hands` | robust_correlation | 39 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.409, Spearman=0.8472, LOO稳号=True |
| `ulist239.f63` | `zhb.stat2.main_net_buy_amount_1d` | robust_correlation | 39 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.568, Spearman=0.918, LOO稳号=True |
| `ulist239.f63` | `zhb.stat2.main_net_buy_amount` | robust_correlation | 39 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.7942, Spearman=0.9757, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.prev_open_volume_hand` | robust_correlation | 39 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.2247, Spearman=0.7445, LOO稳号=True |
| `ulist239.f63` | `eltdx.shortline.prev_open_amount` | robust_correlation | 39 | T:20261117, T:20261118 | eltdx, ulist239 | Pearson=0.568, Spearman=0.918, LOO稳号=True |
| `ulist239.f63` | `zhb.stat.pre_receive_zj` | robust_correlation | 36 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.2554, Spearman=0.72, LOO稳号=True |
| `ulist239.f63` | `zhb.full.pre_receive_zj` | robust_correlation | 36 | T:20261117, T:20261118 | ulist239, zhb | Pearson=0.2554, Spearman=0.72, LOO稳号=True |

## 七、日期与数据质量告警（98）

- 20261017: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261018: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261031: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261101: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261107: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261114: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 20261120: 日期目录没有 meta.json 或 raw_*.json，按报告/空目录跳过
- 行情窗口交易日 20261111 无对应采集目录；不会用更早交易日补位，需结合其他采集目录的来源日期检查实际覆盖
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
- 20261119/zhb: 采集状态 partial
- 20261119/push2: 采集状态 failed
- 20261119/em_kline_f61: 采集状态 partial
- 20261119/em_fund_flow: 采集状态 partial
- 20261119/ulist239: 采集状态 failed
- 20261119/clist: 采集状态 partial
- 20261119/slist: 采集状态 failed
- 20261119/clist: 来源状态为 partial，样本按部分快照参与
- 20261119/clist: 没有可用记录，快照跳过
- 20261119/em_fund_flow: 来源状态为 partial，样本按部分快照参与
- 20261119/em_fund_flow: 没有可用记录，快照跳过
- 20261119/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20261119/em_kline_f61: 没有可用记录，快照跳过
- 20261119/push2: 来源状态为 failed，快照跳过
- 20261119/slist: 来源状态为 failed，快照跳过
- 20261119/tdx_f10: 没有可用记录，快照跳过
- 20261119/tdx_f10_more: 没有可用记录，快照跳过
- 20261119/ulist239: 来源状态为 failed，快照跳过
- 20261119/zhb: 来源状态为 partial，样本按部分快照参与
- 重复快照 kph/20261118: 选择 20261119，忽略 20261118
- 重复快照 zhb/20261118: 保留 20261118，忽略 20261119
- 日常碰撞排除来源: ftshare=FTShare private hosted MCP
- 20261112/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1794496820051，response_timestamp_date='2026-11-12'（仅响应组装时间，不作为数据日期），记录数=20
- 20261116/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1794835664138，response_timestamp_date='2026-11-16'（仅响应组装时间，不作为数据日期），记录数=20
- 20261117/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1794901089674，response_timestamp_date='2026-11-17'（仅响应组装时间，不作为数据日期），记录数=20
- 20261118/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1794992253927，response_timestamp_date='2026-11-18'（仅响应组装时间，不作为数据日期），记录数=20
- 20261119/fuyao/stocks.*.auction_final: 竞价子树已排除；reason=source_data_date_unavailable，data_status='final'，source_data_date=None，source_data_date_basis='not_exposed_by_auction_snapshot_contract'，response_timestamp=1795073358203，response_timestamp_date='2026-11-19'（仅响应组装时间，不作为数据日期），记录数=20
- 20261112/kph: KPH 历史碰撞要求 pagination.complete=true；旧样本缺少完整分页证明，已排除
- 折叠 28439 条重复字段样本，按快照质量择优；示例: market_sources.code/600327/T:20261112, market_sources.name/600327/T:20261112, market_sources.code/601566/T:20261112, market_sources.name/601566/T:20261112, market_sources.code/688371/T:20261112, market_sources.name/688371/T:20261112, market_sources.market/688371/T:20261112, market_sources.time/688371/T:20261112, market_sources.change_pct/688371/T:20261112, market_sources.price/688371/T:20261112
- 20261112/cninfo: 66 条事件记录缺少可解析的自然日，已跳过
- 20261116/cninfo: 66 条事件记录缺少可解析的自然日，已跳过
- 20261117/cninfo: 67 条事件记录缺少可解析的自然日，已跳过
- 20261118/cninfo: 67 条事件记录缺少可解析的自然日，已跳过
- 20261119/cninfo: 67 条事件记录缺少可解析的自然日，已跳过
- 64 条 verified 源字段来源未确认独立性，作为已知字段跳过重解但不作锚
- 31 条官方契约语义锚可参与对撞；底层来源独立性未确认，强候选标为 L1-C
- 70 条 verified 源字段映射到重复运行时身份；相关运行时路径已退出破解目标，但身份消歧前不作锚
- 61 条 ZHB full-view 路径的所有注册 owner 均已 verified/disproved，但归属不唯一；不作锚，且不作为未知目标重复破解
- 160 条 verified 源字段元数据未达锚点条件（含义冲突 10 条、缺义/占位 159 条、单位冲突 2 条）；已退出破解目标，但保留在元数据补全队列且不作碰撞锚
- 东财-push2(stock/get) 行时间戳日期见证：确认 40 行，日期冲突 0 行，无效时间戳 0 行
- 东财-ulist239(np/get) 行时间戳日期见证：确认 40 行，日期冲突 0 行，无效时间戳 0 行
- 跨源值日期见证 tdx.quote_raw.bid1_vol <- tencent[10]: 97/100 精确，79/82 非零精确，4 个交易日满足日阈值；未达到门槛
- 跨源值日期见证 tdx.quote_raw.ask1_vol <- tencent[20]: 98/100 精确，89/91 非零精确，4 个交易日满足日阈值；未达到门槛
- 来源关系审阅队列: 21 组有同完整路径的来源对；仅作观测等价/互补线索，不自动认定同源或停采
- 字段时效分类: daily_market=37, intraday_sensitive=23, periodic_or_event=3, slow_changing=5, static_reference=7, unclassified=1243；未分类字段按来源日期严格门控
- 对撞模式：verified_anchor_only；待破解字段=92，verified 锚资格字段=1506，verified 目标排除身份=1725，可用独立锚=1418，官方契约字段=475，L1-C 契约锚=31，right 字段=597
- 1 条本地字段覆盖快照的 registry 状态已过期；候选展示已按当前逐源注册表状态校正。
- 跳过同一来源家族字段对：15242
- 跳过来源独立性未确认的字段对：2860
- 官方契约锚参与字段对撞 1612 对；底层来源独立性未确认，强匹配单列 L1-C

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

策略状态：`ok`；逐源分类字段 75，保守默认未分类字段 1243。L1/L1-C 日期证据：来源日期已确认 0 条，跨源值见证推断 0 条，仅语义证据且日期未确认 0 条，其他日期未确认 0 条。

| 日期见证关系 | 结果 | 交易日 | 精确样本 | 非零精确样本 | 不同非零值 | 证据 SHA-256 |
|:--|:--|--:|--:|--:|--:|:--|
| `tdx.quote_raw.ask1_vol <- tencent[20]` | thresholds_not_met | 4 | 98/100 | 89/91 | 77 | `9f488224d9a95673bf751451c47a3fd1ae05090b51cf090dc014d66818252d69` |
| `tdx.quote_raw.bid1_vol <- tencent[10]` | thresholds_not_met | 4 | 97/100 | 79/82 | 67 | `9f488224d9a95673bf751451c47a3fd1ae05090b51cf090dc014d66818252d69` |

_本轮 L1/L1-C 没有仅凭静态或缓变字段、且来源日期未确认的关系。_

## 来源字段覆盖与碰撞参与

_窗口字段值样本是经日期筛选、重复折叠和快照择优后载入的非空值；右侧比较次数另受字段类型及来源规则筛选。官方契约字段须有逐字段审定证据，契约语义本身不证明底层数据来源独立。_

| 来源 | 已确认字段 | 契约已确认 | 契约锚 | 独立锚 | L1-C 锚 | 窗口字段 / 字段值样本 / 交易日 |
|:--|--:|--:|--:|--:|--:|--:|
| axdata | 34 | 0 | 0 | 0 | 0 | 34 / 2686 / 5 |
| clist | 20 | 0 | 0 | 20 | 0 | 33 / 14334 / 2 |
| cls | 6 | 1 | 1 | 6 | 0 | 5 / 1000 / 0 |
| cninfo | 6 | 0 | 0 | 6 | 0 | 0 / 0 / 0 |
| datacenter | 46 | 5 | 5 | 46 | 0 | 0 / 0 / 0 |
| eltdx | 259 | 185 | 185 | 259 | 0 | 116 / 5483 / 5 |
| em_fund_flow | 15 | 0 | 0 | 15 | 0 | 15 / 600 / 2 |
| em_hot | 39 | 0 | 0 | 39 | 0 | 0 / 0 / 0 |
| em_kline_f61 | 12 | 1 | 1 | 12 | 0 | 2 / 80 / 2 |
| etf | 5 | 0 | 0 | 5 | 0 | 14 / 58612 / 6 |
| event_dc | 13 | 12 | 12 | 13 | 0 | 164 / 155232 / 5 |
| exchange | 5 | 0 | 0 | 5 | 0 | 0 / 0 / 0 |
| ftshare | 6 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| ftshare_rest | 32 | 31 | 31 | 0 | 31 | 32 / 3175 / 5 |
| fuyao | 117 | 99 | 99 | 117 | 0 | 20 / 2000 / 5 |
| kph | 12 | 0 | 0 | 12 | 0 | 15 / 1545 / 3 |
| kpl | 19 | 0 | 0 | 19 | 0 | 28 / 5780 / 5 |
| market_sources | 16 | 0 | 0 | 0 | 0 | 69 / 24522 / 5 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 2 / 88 / 0 |
| push2 | 69 | 0 | 0 | 69 | 0 | 114 / 4560 / 2 |
| push2ex | 35 | 1 | 1 | 35 | 0 | 16 / 4624 / 5 |
| reports | 46 | 0 | 0 | 46 | 0 | 49 / 49 / 0 |
| research_sina | 0 | 0 | 0 | 0 | 0 | 6 / 1020 / 0 |
| sina | 33 | 0 | 0 | 33 | 0 | 39 / 3450 / 5 |
| sina_extended | 6 | 3 | 3 | 6 | 0 | 4 / 400 / 5 |
| slist | 5 | 0 | 0 | 5 | 0 | 1 / 40 / 2 |
| sse_e_interaction | 0 | 0 | 0 | 0 | 0 | 8 / 312 / 0 |
| st_list | 0 | 0 | 0 | 0 | 0 | 6 / 6958 / 5 |
| tdx | 241 | 107 | 107 | 241 | 0 | 58 / 6400 / 5 |
| tencent | 84 | 0 | 0 | 84 | 0 | 88 / 8790 / 5 |
| ulist239 | 79 | 4 | 4 | 79 | 0 | 240 / 9600 / 2 |
| zhb | 246 | 26 | 26 | 246 | 0 | 128 / 11399 / 5 |

| 来源 | 破解目标 | 比较字段 | 作目标比较 | 作右侧比较 | L1-C 锚比较 | L1 / L1-C / L4 关系 | 方法候选涉及 |
|:--|--:|--:|--:|--:|--:|--:|--:|
| axdata | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| clist | 10 | 17 | 3384 | 102 | 0 | 0 / 0 / 0 | 0 |
| cls | 1 | 1 | 38 | 65 | 0 | 0 / 0 / 0 | 0 |
| cninfo | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| datacenter | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| eltdx | 1 | 72 | 32 | 4460 | 0 | 0 / 0 / 0 | 18 |
| em_fund_flow | 0 | 15 | 0 | 96 | 0 | 0 / 0 / 0 | 0 |
| em_hot | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| em_kline_f61 | 0 | 1 | 0 | 6 | 0 | 0 / 0 / 0 | 0 |
| etf | 4 | 0 | 1188 | 0 | 0 | 0 / 0 / 0 | 0 |
| event_dc | 56 | 12 | 18452 | 72 | 0 | 0 / 0 / 0 | 0 |
| exchange | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| ftshare_rest | 0 | 25 | 0 | 1612 | 1612 | 0 / 0 / 0 | 7 |
| fuyao | 0 | 14 | 0 | 910 | 0 | 0 / 0 / 0 | 2 |
| kph | 1 | 9 | 548 | 534 | 0 | 0 / 0 / 2 | 2 |
| kpl | 3 | 19 | 607 | 1600 | 0 | 0 / 0 / 3 | 1 |
| market_sources | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| news_wscn_cctv | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| push2 | 4 | 66 | 72 | 408 | 0 | 0 / 0 / 0 | 0 |
| push2ex | 0 | 12 | 0 | 72 | 0 | 0 / 0 / 1 | 1 |
| reports | 0 | 5 | 0 | 45 | 0 | 0 / 0 / 0 | 0 |
| research_sina | 2 | 0 | 560 | 0 | 0 | 0 / 0 / 0 | 0 |
| sina | 1 | 32 | 524 | 1869 | 0 | 0 / 0 / 0 | 2 |
| sina_extended | 0 | 3 | 0 | 189 | 0 | 0 / 0 / 0 | 0 |
| slist | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |
| sse_e_interaction | 2 | 0 | 25 | 0 | 0 | 0 / 0 / 0 | 0 |
| st_list | 3 | 0 | 48 | 0 | 0 | 0 / 0 / 0 | 0 |
| tdx | 0 | 51 | 0 | 3705 | 0 | 0 / 0 / 0 | 15 |
| tencent | 2 | 80 | 62 | 4885 | 0 | 0 / 0 / 0 | 13 |
| ulist239 | 2 | 76 | 392 | 471 | 0 | 0 / 0 / 0 | 79 |
| zhb | 0 | 75 | 0 | 4831 | 0 | 0 / 0 / 0 | 22 |

## 来源/接口重叠审阅（不自动停采）

此处按**完整规范路径**和来源实际日期对齐比较已采值，单独呈现同家族、不同仓库或血缘未明来源的重叠。数值一致只说明观测范围内的路径等价候选，不证明底层提供方相同、字段语义相同或整条路由可删除。只有接口字段覆盖、唯一字段、备用关系和复验策略均核实后，才可调整采集路由。
来源对 21 组；保留详情 21 组；路径身份歧义 5 项；采集自动停用：否。

| 来源 A / 仓库 | 来源 B / 仓库 | 血缘关系 | 观测关系 | 共同路径 | 强匹配路径 | 失配路径/失配样本/近似样本/未对齐样本 | A/B 独有路径 | 强匹配完整路径样例 |
|:--|:--|:--|:--|--:|--:|--:|:--|:--|
| `sina` / https://github.com/shidenggui/easyquotation | `tencent` / https://github.com/shidenggui/easyquotation | different_confirmed_provider_families | observed_value_differences | 39 | 1 | 38/3018/684/0 | 0/49 | `[3]` |
| `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | provider_relation_unconfirmed | insufficient_aligned_evidence | 16 | 0 | 0/0/0/156 | 12/53 | — |
| `em_fund_flow` / https://github.com/fleetinglife/levistock | `ulist239` / https://github.com/fleetinglife/levistock | same_confirmed_provider_family | insufficient_aligned_evidence | 15 | 0 | 0/0/0/600 | 0/225 | — |
| `em_fund_flow` / https://github.com/fleetinglife/levistock | `push2` / https://github.com/fleetinglife/levistock | same_confirmed_provider_family | insufficient_aligned_evidence | 15 | 0 | 0/0/0/600 | 0/99 | — |
| `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `push2ex` / https://github.com/fleetinglife/levistock | provider_relation_unconfirmed | insufficient_aligned_evidence | 7 | 0 | 0/0/0/1156 | 62/9 | — |
| `push2ex` / https://github.com/fleetinglife/levistock | `tdx` / https://github.com/yanwei99521/easy-tdx, https://github.com/electkismet/eltdx | different_confirmed_provider_families | insufficient_aligned_evidence | 3 | 0 | 0/0/0/18 | 13/55 | — |
| `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `tdx` / https://github.com/yanwei99521/easy-tdx, https://github.com/electkismet/eltdx | provider_relation_unconfirmed | insufficient_aligned_evidence | 3 | 0 | 0/0/0/20 | 66/55 | — |
| `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `push2ex` / https://github.com/fleetinglife/levistock | different_confirmed_provider_families | insufficient_aligned_evidence | 3 | 0 | 0/0/0/340 | 25/13 | — |
| `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | `push2ex` / https://github.com/fleetinglife/levistock | different_confirmed_provider_families | insufficient_aligned_evidence | 3 | 0 | 0/0/0/309 | 12/13 | — |
| `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | provider_relation_unconfirmed | insufficient_aligned_evidence | 3 | 0 | 0/0/0/235 | 12/66 | — |
| `ftshare_rest` / — | `tdx` / https://github.com/yanwei99521/easy-tdx, https://github.com/electkismet/eltdx | provider_relation_unconfirmed | insufficient_aligned_evidence | 3 | 0 | 0/0/0/300 | 29/55 | — |
| `ftshare_rest` / — | `push2ex` / https://github.com/fleetinglife/levistock | provider_relation_unconfirmed | insufficient_aligned_evidence | 2 | 0 | 0/0/0/12 | 30/14 | — |
| `ftshare_rest` / — | `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | provider_relation_unconfirmed | insufficient_aligned_evidence | 2 | 0 | 0/0/0/11 | 30/67 | — |
| `market_sources` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | `zhb` / https://github.com/yanwei99521/easy-tdx, https://github.com/yanwei99521/easy-tdx | provider_relation_unconfirmed | insufficient_aligned_evidence | 1 | 0 | 0/0/0/3 | 68/127 | — |
| `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | `sina_extended` / https://github.com/mpquant/Ashare | different_confirmed_provider_families | insufficient_aligned_evidence | 1 | 0 | 0/0/0/1 | 14/3 | — |
| `ftshare_rest` / — | `sina_extended` / https://github.com/mpquant/Ashare | provider_relation_unconfirmed | insufficient_aligned_evidence | 1 | 0 | 0/0/0/100 | 31/3 | — |
| `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | different_confirmed_provider_families | observed_value_differences | 3 | 0 | 1/4/0/0 | 12/25 | — |
| `ftshare_rest` / — | `kpl` / https://github.com/LowellLee/kpl, https://github.com/Rainynitesky/kaipanla-data-parser | provider_relation_unconfirmed | observed_value_differences | 2 | 0 | 1/3/0/0 | 30/26 | — |
| `ftshare_rest` / — | `zhb` / https://github.com/yanwei99521/easy-tdx, https://github.com/yanwei99521/easy-tdx | provider_relation_unconfirmed | observed_value_differences | 1 | 0 | 1/36/0/0 | 31/127 | — |
| `ftshare_rest` / — | `kph` / https://github.com/electkismet/AxData, https://github.com/fleetinglife/levistock | provider_relation_unconfirmed | observed_value_differences | 4 | 0 | 3/3/1/0 | 28/11 | — |
| `push2` / https://github.com/fleetinglife/levistock | `ulist239` / https://github.com/fleetinglife/levistock | same_confirmed_provider_family | observed_value_differences | 113 | 0 | 107/4218/1/80 | 1/127 | — |

强匹配路径不得有值失配、未对齐样本或低信息常量，并达到每条路径至少 5 个信息样本、3 个不同样本日期、3 只证券；宽松舍入窗口只列为独立近似样本数，不计强匹配；该筛选只产生路由复核候选，不取代现有接口专用退出和复验规则。

## AxData 每日接口核验

> 此处汇总采集目录已保存的本地证据，不发起网络请求、不改变注册表状态；AxData 是多源框架，不作为独立字段锚。

### AxData

窗口内有 6 个唯一数据日的轮验记录；重复目录合并 0 条。
静态接口队列：257 个接口，3343 个字段出现项，低于 E3 的字段出现项 3343；当前主动探针白名单 `tencent_realtime_snapshot`。
静态候选策略：static review only until route, parameters, date basis, and request safety are approved。

| 数据日 | 轮验状态 | 探针状态 / 请求数 | 来源身份状态 | 短线配对 | KPH/KPL 配对 | 证据文件 |
|:--|:--|:--|:--|--:|--:|:--|
| 20261112 | already_recorded | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261113 | not_eligible | not_run / 0 (字段相同/不同 0/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing | — | — | meta_summary |
| 20261116 | already_recorded | sampled / 1 (字段相同/不同 16/2) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |
| 20261117 | already_recorded | sampled / 1 (字段相同/不同 0/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | 34 | full |
| 20261118 | already_recorded | sampled / 1 (字段相同/不同 18/0) | kph_limit_up_history: observing；待核 10 字段；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | 38 | full |
| 20261119 | already_recorded | sampled / 1 (字段相同/不同 0/0) | kph_limit_up_history: observing；stock_shortline_indicators_tdx: observing；tencent_realtime_snapshot: observing；待核 16 字段 | 20 | — | full |

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
| `axdata_shortline_vs_eltdx:open_amount` | 16 | 84 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_hand` | 16 | 84 | 0 |
| `axdata_shortline_vs_eltdx:open_volume_ratio` | 17 | 83 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_amount_ratio` | 20 | 80 | 0 |
| `axdata_shortline_vs_eltdx:auction_prev_volume_ratio` | 21 | 76 | 3 |
| `axdata_shortline_vs_eltdx:open_turnover_z` | 45 | 55 | 0 |
| `axdata_shortline_vs_eltdx:open_prev_seal_ratio` | 2 | 9 | 89 |
| `axdata_shortline_vs_eltdx:seal_amount` | 96 | 4 | 0 |
| `axdata_shortline_vs_eltdx:seal_to_amount_ratio` | 96 | 4 | 0 |
| `axdata_shortline_vs_eltdx:seal_to_float_ratio` | 96 | 4 | 0 |
| `axdata_shortline_vs_eltdx:ladder_level` | 0 | 3 | 97 |
| `axdata_shortline_vs_eltdx:limit_board_text` | 4 | 3 | 93 |
| `axdata_shortline_vs_eltdx:seal_prev_ratio` | 10 | 1 | 89 |

## 字母字段名语义提示（仅候选）

窗口内观察到 95 条需审阅的字母字段路径：含词义线索 22 条，仅拆词 73 条。
完整逐条记录保存在碰撞 JSON；名称线索清单：`docs/field_verification/20261014/20261014_alphabetic_field_name_inventory.csv`。
> 拼音、英文、缩写和混合拆词只用于检索候选；必须结合原始值、接口定义和独立来源复核，不得据此定案或改写主字典。

| 逐源字段路径 | 状态/审阅范围 | 名称形式与拆词 | 词义线索（非释义） | 样本日期 |
|:--|:--|:--|:--|:--|
| `市场源(market_sources)::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `东财-push2ex::code` | verified / verified_metadata_gap | recognized_english_word_candidate: code | 代码 | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `东财-push2ex::name` | verified / verified_metadata_gap | recognized_english_word_candidate: name | 名称 | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `市场源(market_sources)::limit_count` | verified / verified_metadata_gap | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20261112, T:20261116, T:20261118 |
| `市场源(market_sources)::plate_limit_up_count` | verified / verified_metadata_gap | snake_case_or_mixed: plate limit up count | 涨跌停限制 + 上/涨 + 数量/次数 | T:20261112, T:20261116, T:20261118 |
| `TDX(双命名源)::changqifuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: changqifuzhai | 长期负债 | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `TDX(双命名源)::cunhuo` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: cunhuo | 存货 | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `TDX(双命名源)::jingyingxianjinliu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingyingxianjinliu | 经营现金流 | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `TDX(双命名源)::jingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingzichan | 净资产 | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `TDX(双命名源)::liudongfuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: liudongfuzhai | 流动负债 | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `TDX(双命名源)::meigujingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: meigujingzichan | 每股净资产 | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `TDX(双命名源)::yingshouzhangkuan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: yingshouzhangkuan | 应收账款 | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `TDX(双命名源)::zibengongjijin` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zibengongjijin | 资本公积金 | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `TDX(双命名源)::zongzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongzichan | 总资产 | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `同花顺-fuyao::snapshot.open_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot open price | 开盘 + 价格 | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `reports::count` | verified / verified_metadata_gap | recognized_english_word_candidate: count | 数量/次数 | C:20261113 |
| `reports::lastEmRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Code | 最近/上一期 + 代码 | C:20261113 |
| `reports::lastEmRatingName` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Name | 最近/上一期 + 名称 | C:20261113 |
| `reports::lastEmRatingValue` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Value | 最近/上一期 + 值 | C:20261113 |
| `reports::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | C:20261113 |
| `reports::predictLastYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Eps | 最近/上一期 + 每股收益 | C:20261113 |
| `reports::predictLastYearPe` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Pe | 最近/上一期 + 市盈率 | C:20261113 |
| `东财-event_dc(可转债列表)::convertible_bonds[].PBV_RATIO` | verified / verified_metadata_gap | runtime_tokenization_only: PBV RATIO | — | T:20261119 |
| `财联社(cls)::content` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: content | — | C:20261116, C:20261117, C:20261118, C:20261119 |
| `财联社(cls)::level` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: level | — | C:20261116, C:20261117, C:20261118, C:20261119 |
| `财联社(cls)::reading_num` | verified / verified_metadata_gap | snake_case_or_mixed: reading num | — | C:20261116, C:20261117, C:20261118, C:20261119 |
| `财联社(cls)::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20261116, C:20261117, C:20261118, C:20261119 |
| `开盘啦(kpl_limit_up_detail)::raw_columns.col_19` | verified / verified_metadata_gap | runtime_tokenization_only: col 19 | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `开盘啦(kpl_limit_up_detail)::seal_amount` | verified / verified_metadata_gap | snake_case_or_mixed: seal amount | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `市场源(market_sources)::one_word` | unverified / unverified_semantics | snake_case_or_mixed: one word | — | T:20261112, T:20261116, T:20261118 |
| `市场源(market_sources)::plate_amount` | verified / verified_metadata_gap | snake_case_or_mixed: plate amount | — | T:20261112, T:20261116, T:20261118 |
| `市场源(market_sources)::plate_code` | verified / verified_metadata_gap | snake_case_or_mixed: plate code | — | T:20261112, T:20261116, T:20261118 |
| `市场源(market_sources)::plate_name` | verified / verified_metadata_gap | snake_case_or_mixed: plate name | — | T:20261112, T:20261116, T:20261118 |
| `市场源(market_sources)::popular` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: popular | — | T:20261112, T:20261116, T:20261118 |
| `开盘红::industry_limit_up_count` | unverified / unverified_semantics | runtime_tokenization_only: industry limit up count | — | T:20261116, T:20261117, T:20261118 |
| `FTShare REST::amplitude` | verified / verified_metadata_gap | runtime_tokenization_only: amplitude | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `FTShare REST::avg` | verified / verified_metadata_gap | runtime_tokenization_only: avg | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `FTShare REST::bid_ask_ratio` | verified / verified_metadata_gap | runtime_tokenization_only: bid ask ratio | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `FTShare REST::board` | verified / verified_metadata_gap | runtime_tokenization_only: board | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `FTShare REST::listing_date` | verified / verified_metadata_gap | runtime_tokenization_only: listing date | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `FTShare REST::name` | verified / verified_metadata_gap | runtime_tokenization_only: name | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `FTShare REST::st` | verified / verified_metadata_gap | runtime_tokenization_only: st | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `FTShare REST::status` | verified / verified_metadata_gap | runtime_tokenization_only: status | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `FTShare REST::symbol` | verified / verified_metadata_gap | runtime_tokenization_only: symbol | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `FTShare REST::symbol_id` | verified / verified_metadata_gap | runtime_tokenization_only: symbol id | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `FTShare REST::turnover_rate` | verified / verified_metadata_gap | runtime_tokenization_only: turnover rate | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `ZHB-tdxstat::stat.unknown_2` | verified / verified_metadata_gap | snake_case_or_mixed: stat unknown 2 | — | T:20261111, T:20261113, T:20261116, T:20261117, T:20261118 |
| `ZHB-tdxstat::stat.unknown_26` | verified / verified_metadata_gap | snake_case_or_mixed: stat unknown 26 | — | T:20261111, T:20261113, T:20261116, T:20261117, T:20261118 |
| `同花顺-fuyao::snapshot.prev_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot prev price | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `市场源(market_sources)::big_order_300w_net` | unverified / unverified_semantics | runtime_tokenization_only: big order 300 w net | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `市场源(market_sources)::institution_add` | unverified / unverified_semantics | runtime_tokenization_only: institution add | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `市场源(market_sources)::main_inflow` | unverified / unverified_semantics | snake_case_or_mixed: main inflow | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `市场源(market_sources)::pe_next` | unverified / unverified_semantics | runtime_tokenization_only: pe next | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `市场源(market_sources)::pe_now` | unverified / unverified_semantics | runtime_tokenization_only: pe now | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `市场源(market_sources)::strength` | unverified / unverified_semantics | runtime_tokenization_only: strength | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `市场源(market_sources)::total_value` | unverified / unverified_semantics | runtime_tokenization_only: total value | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `FTShare REST::pe_ttm` | verified / verified_metadata_gap | runtime_tokenization_only: pe ttm | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `市场源(market_sources)::rank` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: rank | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `TDX-eltdx(适配层)::adjust_mode` | verified / verified_metadata_gap | snake_case_or_mixed: adjust mode | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `TDX-eltdx(适配层)::anchor_date_raw` | verified / verified_metadata_gap | snake_case_or_mixed: anchor date raw | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `TDX-eltdx(适配层)::category` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: category | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `TDX-eltdx(适配层)::period_name` | verified / verified_metadata_gap | snake_case_or_mixed: period name | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `TDX-eltdx(适配层)::raw_payload` | unverified / unverified_semantics | snake_case_or_mixed: raw payload | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
| `TDX-eltdx(适配层)::sort_by` | unverified / unverified_semantics | snake_case_or_mixed: sort by | — | T:20261112, T:20261116, T:20261117, T:20261118, T:20261119 |
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

研究台账：`collision_research_state.json.gz`；累计历史跟踪候选对 4291，本报告候选对 83，历史复现 71，新发现 0。
台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，不会自动改变字段状态、碰撞锚或主字典。新报告只将 `actionable_L1`、L4 和主动方法候选写入待研究队列；已登记关系的复验单独展示，历史跟踪记录不会被删除。

## 候选覆盖、公式与下一步采样

本节用于定位证据缺口和安排后续取样。相关性、公式与样本优先级均为探索候选；不会改变 L1/L1-U 门槛、来源独立性或主字典。

- 未知目标 92 个；其中有方法候选 2 个、无候选 90 个；多候选目标 2 个；有官方契约锚强匹配 0 个、诊断命中 0 个，日期值候选 0 个。
- 方法候选生成 81 条；全局详细项保留 81/500，另按目标字段保留 0 条；完整明细 81 条在 JSON `method_candidate_inventory`；未归档明细 0 条。
- 字段覆盖详情：available；覆盖身份 1563，读取 6 份本地索引。

### 优先处理字段

| 未知字段 | 核验入口 | 当前诊断 | 官方锚强/诊断 | 独立对比/候选数 | 独立锚家族/本源日期 | 建议复核股票 | 最强候选线索 |
|:--|:--|:--|--:|--:|:--|:--|:--|
| `ulist239.f63` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 351 / 79 | 7 家族 / 351 对 / 本源 2 日 | 601288 (31.310773) | zhb.tipinfo.hg_amount_yi (robust_correlation,affine_formula); zhb.stat2.change_30k_bar_ref (robust_correlation) |
| `kph.industry_limit_up_count` | 检查官方锚对撞 | 存在多个候选，需区分 | 0/0 | 525 / 2 | 7 家族 / 525 对 / 本源 4 日 | no_shared_stock_holdout | kpl.raw_columns.col_20 (robust_correlation,affine_formula); push2ex.limit_count (semantic_label) |
| `sse_e_interaction.answer_time` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `sse_e_interaction.id` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `st_list.pct_change` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `st_list.price` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `st_list.st_type` | 检查官方锚对撞 | 来源血缘缺口 | 0/0 | 0 / 0 | 0 家族 / 0 对 / 本源 0 日 | — | — |
| `clist._board_type` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 16 / 0 | 4 家族 / 16 对 / 本源 0 日 | — | — |
| `clist.f208` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `clist.f209` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `clist.f258` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `clist.f259` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `clist.n` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `clist.total` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `etf.etf_sh.etf_type` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 36 / 0 | 5 家族 / 36 对 / 本源 0 日 | — | — |
| `etf.etf_sh.shares_10k` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 533 / 0 | 8 家族 / 533 对 / 本源 0 日 | — | — |
| `etf.etf_sz.fund_category` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 36 / 0 | 5 家族 / 36 对 / 本源 0 日 | — | — |
| `etf.etf_sz.shares_10k` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 533 / 0 | 8 家族 / 533 对 / 本源 0 日 | — | — |
| `event_dc.convertible_bonds[].EXECUTE_PRICE_HS` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.convertible_bonds[].EXECUTE_PRICE_SH` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.convertible_bonds[].EXECUTE_REASON_HS` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.convertible_bonds[].EXECUTE_REASON_SH` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.convertible_bonds[].FIRST_PER_PREPLACING` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.convertible_bonds[].FIRST_PROFIT` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.convertible_bonds[].ISSUE_TYPE` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.convertible_bonds[].ISSUE_YEAR` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.convertible_bonds[].IS_CONVERT_STOCK` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 16 / 0 | 4 家族 / 16 对 / 本源 0 日 | — | — |
| `event_dc.convertible_bonds[].ONLINE_GENERAL_AAU` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.convertible_bonds[].ONLINE_GENERAL_LWR` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.convertible_bonds[].PAYDAYNEW` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.convertible_bonds[].RATING` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 16 / 0 | 4 家族 / 16 对 / 本源 0 日 | — | — |
| `event_dc.convertible_bonds[].fetched_at` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].AFTER_ISSUE_PE` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].AMPLITUDE` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].AVERAGE_PRICE` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].CHANGE` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].CHANGE_RATE` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].CLOSE_PRICE` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].DEC_SUMFINA` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].EACHBALLOT_SHARES` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].INDUSTRY_PE` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].INDUSTRY_PE_NEW` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].IPO_YIELD` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].ISSUE_NUM` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].ISSUE_PRICE` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].ISSUE_WAY_EXPLAIN` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 16 / 0 | 4 家族 / 16 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].IS_RISKWARNING` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].LATELY_PRICE` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].LD_AVERAGE_PRICE` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |
| `event_dc.ipo_calendar[].LD_CLOSE_CHANGE` | 检查官方锚对撞 | 覆盖字段未映射到运行路径 | 0/0 | 351 / 0 | 7 家族 / 351 对 / 本源 0 日 | — | — |

_此表显示优先级最高的 50 / 共 92 个目标；完整清单见 JSON。_


### 舍入近似数值线索（仅研究，不算 L1/L1-U；0 组）

近似窗口只用于提示复核：需核对双方原始单位、展示精度和来源口径；不得把该命中率当作字段语义结论或注册表写回依据。完整明细在 JSON `candidate_triage.approximate_matches`。

_本轮没有达到近似筛查门槛的关系。_


### 双输入公式候选
本轮未发现通过留出筛选的公式候选；测试组合 0 个。


### 已知映射与已证伪关系的候选校准

- 已登记正向对照：当前窗口有 159 组独立数值关系可评估，157 组被方法候选识别；样本不足 2 组。此计数仅检查方法覆盖，不是准确率。
- 已证伪负向对照：数值关系 0 组，其中仍有方法信号 0 组；这些信号被隔离，不进入普通候选。

### 采集覆盖异常源

- baidu: 20261117, 20261118, 20261119 ({'pending_validation': 5})
- clist: 20261112, 20261116, 20261119 ({'ok': 2, 'partial': 3})
- em_fund_flow: 20261112, 20261116, 20261119 ({'ok': 2, 'partial': 3})
- em_hot: 20261117, 20261118, 20261119 ({'context_only': 5})
- em_kline_f61: 20261112, 20261116, 20261119 ({'ok': 2, 'partial': 3})
- exchange: 20261117, 20261118, 20261119 ({'context_only': 5})
- ftshare: 20261117, 20261118, 20261119 ({'deprecated': 5})
- push2: 20261112, 20261116, 20261119 ({'failed': 3, 'ok': 2})
- slist: 20261112, 20261116, 20261119 ({'failed': 3, 'ok': 2})
- ulist239: 20261112, 20261116, 20261119 ({'failed': 3, 'ok': 2})
- zhb: 20261112, 20261119 ({'ok': 4, 'partial': 2})

## 低信息与日期语义专项队列

恒空、恒零或当前恒定字段不参与普通碰撞；状态表示当前样本没有区分力，新采样出现有效变化后重新纳入。日期形状只代表值可解析为日期，必须查清业务角色，不能拿字段值代替来源 `as_of_date`。
低信息未知路径 153 项，状态分布 `{'all_missing_or_blank': 5, 'constant_zero': 32, 'constant_value': 116}`。

### 等待新信息的字段

| 完整字段路径 | 状态 | 观测/非空/缺失或空白/不同值 | 样本日期数 | 示例值 |
|:--|:--|--:|--:|:--|
| `reports.emIndustryCode` | all_missing_or_blank | 1/0/1/0 | 1 | `` |
| `eltdx.limit_ladder.limit_up_streak_days` | constant_zero | 2/2/0/1 | 2 | `0` |
| `eltdx.limit_ladder.market_id` | constant_zero | 3/3/0/1 | 2 | `0` |
| `eltdx.raw_payload` | all_missing_or_blank | 5/0/5/0 | 5 | `` |
| `sina[34]` | constant_zero | 10/10/0/1 | 5 | `0.0000` |
| `sina[35]` | constant_zero | 10/10/0/1 | 5 | `0` |
| `event_dc.ipo_calendar[].PREDICT_RAISE_FUNDS` | constant_zero | 35/35/0/1 | 5 | `0` |
| `push2.f123` | constant_zero | 40/40/0/1 | 2 | `0.0` |
| `push2.f124` | constant_zero | 40/40/0/1 | 2 | `0.0` |
| `push2.f125` | constant_zero | 40/40/0/1 | 2 | `0.0` |
| `push2.f134` | constant_zero | 40/40/0/1 | 2 | `0` |
| `ulist239.f120` | constant_zero | 40/40/0/1 | 2 | `0` |
| `ulist239.f125` | constant_zero | 40/40/0/1 | 2 | `0` |
| `ulist239.f126` | constant_zero | 40/40/0/1 | 2 | `0` |
| `ulist239.f137` | constant_zero | 40/40/0/1 | 2 | `0.0` |
| `ulist239.f138` | constant_zero | 40/40/0/1 | 2 | `0.0` |
| `ulist239.f194` | constant_zero | 40/40/0/1 | 2 | `0` |
| `ulist239.f216` | constant_zero | 40/40/0/1 | 2 | `0` |
| `ulist239.f223` | constant_zero | 40/40/0/1 | 2 | `0` |
| `event_dc.ipo_calendar[].CURRENT_ONEWORD_NUM` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.ipo_calendar[].IS_1YEAR` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.ipo_calendar[].IS_1YEAR_APPLY` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.ipo_calendar[].IS_BALLOT_NUM` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.ipo_calendar[].IS_BEIJING` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.ipo_calendar[].IS_CALENDAR_DATA` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.ipo_calendar[].IS_PROFIT` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.ipo_calendar[].IS_REGISTRATION` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.ipo_calendar[].IS_REGISTRATION_NEW` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.ipo_calendar[].IS_UNOPEN` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.ipo_calendar[].OPEN_CHANGERATE` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.ipo_calendar[].PREDICT_ISSUE_PRICE` | constant_zero | 100/100/0/1 | 5 | `0` |
| `event_dc.ipo_calendar[].PREDICT_ISSUE_PRICE2` | constant_zero | 100/100/0/1 | 5 | `0` |
| `sina[32]` | constant_zero | 100/100/0/1 | 5 | `00` |
| `tencent[29]` | all_missing_or_blank | 100/0/100/0 | 5 | `` |
| `tencent[55]` | all_missing_or_blank | 100/0/100/0 | 5 | `` |
| `kph.open_time` | constant_zero | 103/103/0/1 | 3 | `0` |
| `kpl.raw_columns.col_03` | all_missing_or_blank | 170/0/170/0 | 5 | `` |
| `eltdx.limit_ladder.open_prev_seal_ratio` | constant_value | 1/1/0/1 | 1 | `-96.568727` |
| `eltdx.limit_ladder.prev_seal_amount` | constant_value | 1/1/0/1 | 1 | `-177681300.0` |
| `eltdx.limit_ladder.seal_prev_ratio` | constant_value | 1/1/0/1 | 1 | `-0.095414` |
| `market_sources.request_params.fetch_all` | constant_value | 1/1/0/1 | 1 | `false` |
| `market_sources.request_params.stock_code` | constant_value | 1/1/0/1 | 1 | `000007` |
| `market_sources.request_params.zs_type` | constant_value | 1/1/0/1 | 1 | `7` |
| `market_sources.stock_code` | constant_value | 1/1/0/1 | 1 | `000007` |
| `reports.encodeUrl` | constant_value | 1/1/0/1 | 1 | `VF/Aff6xS5JKqu72ctdLoJssK3pKDYRhowFXLzIoI44=` |
| `reports.orgType` | constant_value | 1/1/0/1 | 1 | `white` |
| `eltdx.limit_ladder.alignment_status` | constant_value | 3/3/0/1 | 2 | `previous_trading_day` |
| `eltdx.limit_ladder.exchange` | constant_value | 3/3/0/1 | 2 | `sz` |
| `eltdx.limit_ladder.limit_status` | constant_value | 3/3/0/1 | 2 | `sealed` |
| `eltdx.category` | constant_value | 5/5/0/1 | 5 | `沪深A股` |

_显示前 50 / 共 153 项；完整清单在 JSON。_

日期值候选 6 项；应先查官方定义和完整路径，再确定上市日、记录更新日、报告期、公告/事件日、生效日或来源数据日。

### 日期形状字段待核业务含义

| 完整字段路径 | 日期样本比例 | 编码 | 样本键日期数 | 日期值/来源日/样本日/股票样例 |
|:--|--:|:--|--:|:--|
| `etf.etf_sh.date` | 100.0% | YYYY-MM-DD | 5 | 2026-11-12(来源日=20261112;样本日=T:20261112;股票=510010), 2026-11-12(来源日=20261112;样本日=T:20261112;股票=510020), 2026-11-12(来源日=20261112;样本日=T:20261112;股票=510030), 2026-11-12(来源日=20261112;样本日=T:20261112;股票=510040), 2026-11-12(来源日=20261112;样本日=T:20261112;股票=510050) |
| `etf.etf_sz.date` | 100.0% | YYYY-MM-DD | 5 | 2026-11-12(来源日=20261112;样本日=T:20261112;股票=158000), 2026-11-12(来源日=20261112;样本日=T:20261112;股票=158001), 2026-11-12(来源日=20261112;样本日=T:20261112;股票=158003), 2026-11-12(来源日=20261112;样本日=T:20261112;股票=158005), 2026-11-12(来源日=20261112;样本日=T:20261112;股票=158006) |
| `research_sina.date` | 100.0% | YYYY-MM-DD | 6 | 2026-11-13(来源日=20261113;样本日=C:20261113;股票=600309#event0), 2026-11-13(来源日=20261113;样本日=C:20261113;股票=600309#event1), 2026-11-13(来源日=20261113;样本日=C:20261113;股票=600519#event0), 2026-11-13(来源日=20261113;样本日=C:20261113;股票=600519#event1), 2026-11-14(来源日=20261114;样本日=C:20261114;股票=601288#event2) |
| `news_wscn_cctv.date` | 100.0% | YYYY-MM-DD | 3 | 2026-11-16(来源日=20261116;样本日=C:20261116;股票=__0), 2026-11-16(来源日=20261116;样本日=C:20261116;股票=__1), 2026-11-16(来源日=20261116;样本日=C:20261116;股票=__10), 2026-11-16(来源日=20261116;样本日=C:20261116;股票=__11), 2026-11-16(来源日=20261116;样本日=C:20261116;股票=__12) |
| `market_sources.data_date` | 100.0% | YYYY-MM-DD | 5 | 2026-11-12(来源日=20261112;样本日=T:20261112;股票=000007), 2026-11-16(来源日=20261116;样本日=T:20261116;股票=levistock_daily_candidate), 2026-11-17(来源日=20261117;样本日=T:20261117;股票=levistock_daily_candidate), 2026-11-18(来源日=20261118;样本日=T:20261118;股票=levistock_daily_candidate), 2026-11-19(来源日=20261119;样本日=T:20261119;股票=levistock_daily_candidate) |
| `market_sources.requested_trade_date` | 100.0% | YYYY-MM-DD | 5 | 2026-11-12(来源日=20261112;样本日=T:20261112;股票=kph_limit_ladder), 2026-11-16(来源日=20261116;样本日=T:20261116;股票=kph_limit_ladder), 2026-11-17(来源日=20261117;样本日=T:20261117;股票=kph_limit_ladder), 2026-11-18(来源日=20261118;样本日=T:20261118;股票=kph_limit_ladder), 2026-11-19(来源日=20261119;样本日=T:20261119;股票=kph_limit_ladder) |

## 候选身份与人工审阅状态

- 候选身份：生成 84 条，唯一候选 84 个，重复身份 0，无效身份 0。
- 审阅台账：可用；当前状态 `pending`；已审 0，待处理 84，覆盖率 0.0%。
- 重复归并组：0；每个成员均保留到代表候选的反向追溯。
- 处置计数：`accepted_for_adjudication` 0；`duplicate_grouped` 0；`insufficient_evidence` 0；`needs_external_evidence` 0；`rejected` 0；`unreviewed` 84。
- `accepted_for_adjudication` 只表示可进入现有证据裁决流程；审阅台账不会修改主字典或字段注册表。

## 报告完整性与审阅范围

- 机器可读完整性：`complete`；方法候选生成 81 条，完整明细保存 81 条，缺失 0 条，多余 0 条，重复 0 条，身份无效 0 条。
- 全量方法候选位于同名 JSON 的 `method_candidate_inventory`；Markdown 的 Top-N 表格是导航摘要，不能代替全量 JSON 审阅。
- 候选审阅数据对账：`complete`；唯一候选 84 个，审阅 0 个，待处理 84 个；人工审阅进度与机器清单完整性分别统计。
- Markdown 未逐行展示、但 JSON 保留的部分：
  - `method_candidate_inventory`：展示 0 / 81，摘要省略 81 条。
  - `candidate_triage.targets`：展示 50 / 92，摘要省略 42 条。
  - `candidate_triage.low_information_fields`：展示 50 / 153，摘要省略 103 条。
- 完整性对账通过；逐目标复核仍须覆盖 JSON 的全部明细，并为每项记录已检查、重复归并、证据不足或需外部核验的处置。
