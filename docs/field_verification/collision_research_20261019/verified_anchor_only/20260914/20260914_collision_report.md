# 全源对撞报告（20260914）

> 交易数据窗口配置：近 7 个交易日（`--window`）
> 行情窗口：20260904 ~ 20260914（7 个不同交易日）｜字段 1006 个｜样本值 204975 条
> 新闻/公告自然日窗口：20260908 ~ 20260914
> 主攻目标（unverified）=458｜可审定新候选=61｜首次发现新候选对=61｜已登记关系复验=51｜异号同义 61 / 同号镜像 0

> **规则**：L1 每日需≥18 组有效配对，并至少有5 组信息配对；双方同时为 0 或同时缺失不计命中率，一侧为 0、另一侧非 0 按失配计。信息配对命中率≥90%，且覆盖至少 3 个独立交易日/自然事件日；同一来源族不作为跨源证据；盘中快照不计入 L1。JSON `daily_sample_counts` 与 `daily_informative_sample_counts`分别保留每日有效配对数和 L1 信息配对数。（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、L1 / L1-U 新候选 — 异号同义（跨编号，高价值）(61)

| 左字段(unverified) | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|
| `fuyao.auction_final.pre_close_price` | `sina[2]` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `fuyao.auction_final.pre_close_price` | `tdx.quote_full.last_close` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `fuyao.auction_final.pre_close_price` | `tencent[4]` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `fuyao.auction_final.pre_close_price` | `ulist239.f18` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `fuyao.auction_final.open_price` | `sina[1]` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `fuyao.auction_final.open_price` | `tdx.quote_full.open` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `fuyao.auction_final.open_price` | `tencent[5]` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `fuyao.auction_final.open_price` | `ulist239.f17` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `push2_full.f44` | `fuyao.snapshot.high_price` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `push2_full.f45` | `fuyao.snapshot.low_price` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `push2_full.f46` | `fuyao.snapshot.open_price` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `push2_full.f46` | `tdx.quote_full.open` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `push2_full.f47` | `fuyao.snapshot.volume` | L1-U | 100.00% | 7 | 140 | — | 100 |  | — |
| `push2_full.f47` | `sina[8]` | L1-U | 100.00% | 7 | 140 | — | 100 |  | — |
| `push2_full.f48` | `fuyao.snapshot.turnover` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `push2_full.f58` | `tencent[1]` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `push2_full.f60` | `fuyao.snapshot.prev_price` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `push2_full.f60` | `tdx.quote_full.last_close` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `push2_full.f84` | `tdx.finance_info.zongguben` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `push2_full.f85` | `tdx.finance_info.liutongguben` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `push2_full.f105` | `tdx.finance_info.jinglirun` | L1-U | 100.00% | 7 | 140 | — | 10 |  | — |
| `push2_full.f169` | `fuyao.snapshot.price_change` | L1 | 100.00% | 7 | 140 | 138 | - |  | — |
| `tdx.finance_info.liutong_guben` | `tencent[72]` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `tdx.finance_info.liutong_guben` | `tencent[76]` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `tdx.finance_info.liutong_guben` | `ulist239.f39` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `tdx.finance_info.zong_guben` | `tencent[73]` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `tdx.finance_info.zong_zichan` | `ulist239.f50` | L1-U | 100.00% | 7 | 140 | — | 0.1 |  | — |
| `tdx.finance_info.liudong_zichan` | `ulist239.f51` | L1-U | 100.00% | 7 | 133 | — | 0.1 |  | — |
| `tdx.finance_info.guding_zichan` | `ulist239.f52` | L1-U | 100.00% | 7 | 140 | — | 0.1 |  | — |
| `tdx.finance_info.liudong_fuzhai` | `ulist239.f55` | L1-U | 100.00% | 7 | 133 | — | 0.1 |  | — |
| `tdx.finance_info.ziben_gongjijin` | `ulist239.f60` | L1-U | 100.00% | 7 | 140 | — | 0.1 |  | — |
| `tdx.finance_info.yingye_lirun` | `ulist239.f42` | L1-U | 100.00% | 7 | 140 | — | 0.1 |  | — |
| `tdx.finance_info.lirun_zonghe` | `ulist239.f44` | L1-U | 100.00% | 7 | 140 | — | 0.1 |  | — |
| `tdx.finance_info.weifen_lirun` | `ulist239.f47` | L1-U | 100.00% | 7 | 140 | — | 0.1 |  | — |
| `ulist239.f38` | `tdx.finance_info.zongguben` | L1 | 100.00% | 7 | 140 | 140 | - |  | — |
| `ulist239.f45` | `tdx.finance_info.jinglirun` | L1-U | 100.00% | 7 | 140 | — | 10 |  | — |
| `push2_full.f119` | `zhb.stat.change_5d` | L1 | 100.00% | 5 | 100 | 114 | - |  | — |
| `push2_full.f120` | `zhb.stat.change_20d` | L1 | 100.00% | 5 | 100 | 115 | - |  | — |
| `push2_full.f170` | `zhb.stat.change_pct` | L1 | 100.00% | 5 | 100 | 114 | - |  | — |
| `push2_full.f175` | `zhb.stat2.low_52w` | L1 | 100.00% | 5 | 100 | 115 | - |  | — |
| `ulist239.f109` | `zhb.stat.change_5d` | L1 | 100.00% | 5 | 100 | 114 | - |  | — |
| `ulist239.f110` | `zhb.stat.change_20d` | L1 | 100.00% | 5 | 100 | 115 | - |  | — |
| `ulist239.f160` | `zhb.stat.change_10d` | L1 | 100.00% | 5 | 100 | 115 | - |  | — |
| `push2_full.f44` | `tdx.quote_full.high` | L1 | 99.29% | 7 | 140 | 140 | - |  | — |
| `fuyao.auction_final.auction_price` | `sina[1]` | L1 | 99.25% | 7 | 134 | 134 | - |  | — |
| `fuyao.auction_final.auction_price` | `tdx.quote_full.open` | L1 | 99.25% | 7 | 134 | 134 | - |  | — |
| `fuyao.auction_final.auction_price` | `tencent[5]` | L1 | 99.25% | 7 | 134 | 134 | - |  | — |
| `fuyao.auction_final.auction_price` | `ulist239.f17` | L1 | 99.25% | 7 | 134 | 134 | - |  | — |
| `push2_full.f164` | `zhb.stat.pe_dynamic` | L1 | 99.00% | 5 | 100 | 115 | - |  | — |
| `zhb.full.pe_dynamic` | `ulist239.f115` | L1 | 99.00% | 5 | 100 | 115 | - |  | — |
| `zhb.full.pe_dynamic` | `tencent[39]` | L1 | 98.00% | 5 | 100 | 115 | - |  | — |
| `push2_full.f45` | `tdx.quote_full.low` | L1 | 97.86% | 7 | 140 | 140 | - |  | — |
| `tdx.quote_full.limit_down` | `tencent[48]` | L1 | 97.50% | 6 | 120 | 120 | - |  | — |
| `tdx.quote_full.limit_up` | `tencent[47]` | L1 | 96.67% | 6 | 120 | 120 | - |  | — |
| `push2_full.f121` | `zhb.stat.change_60d` | L1 | 95.92% | 5 | 100 | 112 | - |  | — |
| `ulist239.f24` | `zhb.stat.change_60d` | L1 | 95.92% | 5 | 100 | 112 | - |  | — |
| `push2_full.f122` | `zhb.stat.change_ytd` | L1 | 95.00% | 5 | 100 | 115 | - |  | — |
| `ulist239.f25` | `zhb.stat.change_ytd` | L1 | 95.00% | 5 | 100 | 115 | - |  | — |
| `fuyao.valuation.ps_ttm` | `ulist239.f130` | L1 | 90.00% | 7 | 140 | 140 | - |  | — |
| `push2_full.f58` | `sina[0]` | L1 | 90.00% | 7 | 140 | 140 | - |  | — |
| `push2_full.f174` | `tencent[67]` | L1 | 90.00% | 7 | 140 | 140 | - |  | — |

## 二、L1 / L1-U 新候选 — 同号镜像（同编号，低优先级）(0)

_本轮无同号镜像候选。_


## 三、已登记映射的本窗口复验（51）

_这些关系已在主注册表登记，只用于观察当前样本是否仍支持既有映射；它们不是新的未知字段候选，也不能再次提交为新定案。_

| 左字段 | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |
|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|
| `push2_full.f44` | `sina[4]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f44` | `tencent[33]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f44` | `tencent[41]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f45` | `sina[5]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f45` | `tencent[34]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f45` | `tencent[42]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f46` | `sina[1]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f46` | `tencent[5]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f48` | `sina[9]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f50` | `tencent[49]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f51` | `tencent[47]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f52` | `tencent[48]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f57` | `tencent[2]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f60` | `sina[2]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f60` | `tencent[4]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f71` | `tencent[51]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f84` | `tencent[73]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f85` | `tencent[72]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f85` | `tencent[76]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f119` | `tencent[63]` | L1 | 100.00% | 7 | 140 | 139 | - |  | ✅ |
| `push2_full.f168` | `tencent[38]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f169` | `tencent[31]` | L1 | 100.00% | 7 | 140 | 138 | - |  | ✅ |
| `push2_full.f170` | `tencent[32]` | L1 | 100.00% | 7 | 140 | 138 | - |  | ✅ |
| `push2_full.f171` | `tencent[43]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f175` | `tencent[68]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `ulist239.f7` | `tencent[43]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `ulist239.f8` | `tencent[38]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `ulist239.f10` | `tencent[49]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `ulist239.f38` | `tencent[73]` | L1 | 100.00% | 7 | 140 | 140 | - |  | ✅ |
| `ulist239.f109` | `tencent[63]` | L1 | 100.00% | 7 | 140 | 139 | - |  | ✅ |
| `push2_full.f119` | `zhb.full.change_5d` | L1 | 100.00% | 5 | 100 | 114 | - |  | ✅ |
| `push2_full.f120` | `zhb.full.change_20d` | L1 | 100.00% | 5 | 100 | 115 | - |  | ✅ |
| `push2_full.f175` | `zhb.full.low_52w` | L1 | 100.00% | 5 | 100 | 115 | - |  | ✅ |
| `ulist239.f109` | `zhb.full.change_5d` | L1 | 100.00% | 5 | 100 | 114 | - |  | ✅ |
| `ulist239.f110` | `zhb.full.change_20d` | L1 | 100.00% | 5 | 100 | 115 | - |  | ✅ |
| `ulist239.f160` | `zhb.full.change_10d` | L1 | 100.00% | 5 | 100 | 115 | - |  | ✅ |
| `zhb.full.change_pct` | `tencent[32]` | L1 | 100.00% | 5 | 100 | 114 | - |  | ✅ |
| `zhb.full.change_pct` | `ulist239.f3` | L1 | 100.00% | 5 | 100 | 114 | - |  | ✅ |
| `push2_full.f162` | `tencent[52]` | L1 | 99.29% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f163` | `tencent[53]` | L1 | 98.57% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f164` | `tencent[39]` | L1 | 98.57% | 7 | 140 | 140 | - |  | ✅ |
| `ulist239.f160` | `tencent[69]` | L1 | 98.57% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f120` | `tencent[70]` | L1 | 97.86% | 7 | 140 | 140 | - |  | ✅ |
| `ulist239.f110` | `tencent[70]` | L1 | 97.86% | 7 | 140 | 140 | - |  | ✅ |
| `ulist239.f32` | `sina[7]` | L1 | 96.43% | 7 | 140 | 140 | - |  | ✅ |
| `ulist239.f32` | `sina[21]` | L1 | 96.43% | 7 | 140 | 140 | - |  | ✅ |
| `ulist239.f32` | `tencent[19]` | L1 | 96.43% | 7 | 140 | 140 | - |  | ✅ |
| `push2_full.f121` | `zhb.full.change_60d` | L1 | 95.92% | 5 | 100 | 112 | - |  | ✅ |
| `ulist239.f24` | `zhb.full.change_60d` | L1 | 95.92% | 5 | 100 | 112 | - |  | ✅ |
| `zhb.full.high_52w` | `tencent[67]` | L1 | 95.00% | 5 | 100 | 115 | - |  | ✅ |
| `push2_full.f167` | `tencent[46]` | L1 | 90.00% | 7 | 140 | 140 | - |  | ✅ |

## 四、L4 存疑候选（181）

| 左字段 | 右字段 | 命中率 | 天数 | 样本 |
|:--|:--|--:|--:|--:|
| `fuyao.auction_final.open_price` | `push2.f46` | 100.00% | 1 | 20 |
| `fuyao.auction_final.last_price` | `push2.f43` | 100.00% | 1 | 20 |
| `fuyao.auction_final.last_price` | `push2.f179` | 100.00% | 1 | 20 |
| `fuyao.auction_final.last_price` | `sina[3]` | 100.00% | 7 | 140 |
| `fuyao.auction_final.last_price` | `tencent[3]` | 100.00% | 7 | 140 |
| `fuyao.auction_final.last_price` | `ulist239.f2` | 100.00% | 7 | 140 |
| `push2.f57` | `tencent[2]` | 100.00% | 1 | 20 |
| `push2.f58` | `tencent[1]` | 100.00% | 1 | 20 |
| `push2.f60` | `fuyao.snapshot.prev_price` | 100.00% | 1 | 20 |
| `push2.f60` | `sina[2]` | 100.00% | 1 | 20 |
| `push2.f60` | `tdx.quote_full.last_close` | 100.00% | 1 | 20 |
| `push2.f60` | `tencent[4]` | 100.00% | 1 | 20 |
| `push2.f71` | `tencent[51]` | 100.00% | 1 | 20 |
| `push2.f119` | `tencent[63]` | 100.00% | 1 | 20 |
| `push2.f162` | `tencent[52]` | 100.00% | 1 | 20 |
| `push2.f163` | `tencent[53]` | 100.00% | 1 | 20 |
| `push2.f175` | `tencent[68]` | 100.00% | 1 | 20 |
| `push2_full.f43` | `fuyao.snapshot.last_price` | 100.00% | 7 | 140 |
| `push2_full.f43` | `sina[3]` | 100.00% | 7 | 140 |
| `push2_full.f43` | `tencent[3]` | 100.00% | 7 | 140 |
| `push2_full.f179` | `fuyao.snapshot.last_price` | 100.00% | 7 | 140 |
| `push2_full.f179` | `sina[3]` | 100.00% | 7 | 140 |
| `push2_full.f179` | `tencent[3]` | 100.00% | 7 | 140 |
| `sina[11]` | `tencent[9]` | 100.00% | 7 | 140 |
| `tdx.finance_info.liutong_guben` | `push2.f85` | 100.00% | 1 | 20 |
| `tdx.finance_info.zong_guben` | `push2.f84` | 100.00% | 1 | 20 |
| `tdx.quote_full.turnover_pct` | `push2.f168` | 100.00% | 1 | 20 |
| `tdx.quote_full.amplitude_pct` | `push2.f171` | 100.00% | 1 | 20 |
| `tdx.quote_full.limit_down_price` | `push2.f52` | 100.00% | 1 | 20 |
| `tdx.quote_full.limit_down_price` | `tencent[48]` | 100.00% | 2 | 40 |
| `tdx.quote_full.vol_ratio` | `push2.f50` | 100.00% | 1 | 20 |
| `ulist239.f144` | `fuyao.snapshot.last_price` | 100.00% | 7 | 140 |
| `ulist239.f144` | `sina[3]` | 100.00% | 7 | 140 |
| `ulist239.f144` | `tencent[3]` | 100.00% | 7 | 140 |
| `ulist239.f31` | `sina[6]` | 99.29% | 7 | 140 |
| `ulist239.f31` | `tencent[9]` | 99.29% | 7 | 140 |
| `push2.f120` | `tencent[70]` | 95.00% | 1 | 20 |
| `push2.f164` | `tdx.quote_full.pe_ttm` | 95.00% | 1 | 20 |
| `push2.f164` | `tencent[39]` | 95.00% | 1 | 20 |
| `push2.f167` | `tencent[46]` | 95.00% | 1 | 20 |
| `push2.f174` | `tencent[67]` | 95.00% | 1 | 20 |
| `tdx.finance_info.b_gu` | `ulist239.f200` | 95.00% | 7 | 140 |
| `tdx.finance_info.h_gu` | `ulist239.f190` | 95.00% | 7 | 140 |
| `tdx.quote_full.limit_up` | `push2.f51` | 95.00% | 1 | 20 |
| `tdx.quote_full.limit_down` | `push2.f52` | 95.00% | 1 | 20 |
| `fuyao.auction_final.auction_price` | `push2.f46` | 94.74% | 1 | 19 |
| `push2.f58` | `sina[0]` | 90.00% | 1 | 20 |
| `tdx.finance_info.b_gu` | `ulist239.f190` | 90.00% | 7 | 140 |
| `tdx.finance_info.b_gu` | `ulist239.f231` | 90.00% | 7 | 140 |
| `tdx.finance_info.h_gu` | `ulist239.f200` | 90.00% | 7 | 140 |
| `tdx.finance_info.h_gu` | `ulist239.f231` | 90.00% | 7 | 140 |
| `tdx.quote_full.amplitude_pct` | `tencent[43]` | 90.00% | 2 | 40 |
| `fuyao.auction_final.last_price` | `tdx.quote_full.price` | 87.86% | 7 | 140 |
| `push2_full.f43` | `tdx.quote_full.price` | 87.86% | 7 | 140 |
| `push2_full.f169` | `tdx.quote_full.change_amt` | 87.86% | 7 | 140 |
| `push2_full.f179` | `tdx.quote_full.price` | 87.86% | 7 | 140 |
| `sina[17]` | `tdx.quote_full.bid4` | 87.86% | 7 | 140 |
| `sina[19]` | `tdx.quote_full.bid5` | 87.86% | 7 | 140 |
| `sina[25]` | `tdx.quote_full.ask3` | 87.86% | 7 | 140 |
| `sina[27]` | `tdx.quote_full.ask4` | 87.86% | 7 | 140 |

_（仅显示前 60 / 共 181）_

## 五、已证伪护栏命中（被拦截的伪结论候选）（0）

_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_


## 六、主动方法候选（不直接定案）（500）

_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；每项保留样本日期和来源，仍需人工复核并以独立证据终判。_

| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |
|:--|:--|:--|--:|:--|:--|:--|
| `ulist239.f8` | `tencent[38]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f7` | `tencent[43]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f35` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, ulist239 | Pearson=0.9934, Spearman=0.9948, LOO稳号=True |
| `ulist239.f35` | `fuyao.snapshot.volume` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | fuyao, ulist239 | Pearson=0.9934, Spearman=0.9948, LOO稳号=True |
| `ulist239.f34` | `sina[8]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, ulist239 | Pearson=0.993, Spearman=0.9912, LOO稳号=True |
| `ulist239.f34` | `fuyao.snapshot.volume` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | fuyao, ulist239 | Pearson=0.993, Spearman=0.9912, LOO稳号=True |
| `ulist239.f33` | `tencent[74]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f25` | `tencent[75]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=0.9917, Spearman=0.9656, LOO稳号=True |
| `ulist239.f25` | `tencent[62]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f24` | `tencent[71]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f160` | `tencent[69]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f144` | `tencent[9]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=1.0, Spearman=0.9993, LOO稳号=True |
| `ulist239.f144` | `tencent[85]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=0.9998, Spearman=0.8397, LOO稳号=True |
| `ulist239.f144` | `tencent[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=0.9999, Spearman=0.9963, LOO稳号=True |
| `ulist239.f144` | `tencent[51]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=1.0, Spearman=0.9992, LOO稳号=True |
| `ulist239.f144` | `tencent[42]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=1.0, Spearman=0.9979, LOO稳号=True |
| `ulist239.f144` | `tencent[41]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=1.0, Spearman=0.9986, LOO稳号=True |
| `ulist239.f144` | `tencent[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f144` | `tencent[34]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=1.0, Spearman=0.9979, LOO稳号=True |
| `ulist239.f144` | `tencent[33]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=1.0, Spearman=0.9986, LOO稳号=True |
| `ulist239.f144` | `tencent[19]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=0.9997, Spearman=0.9205, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.open` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, ulist239 | Pearson=0.9999, Spearman=0.9963, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, ulist239 | Pearson=1.0, Spearman=0.9978, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, ulist239 | Pearson=1.0, Spearman=0.9986, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.bid5` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, ulist239 | Pearson=1.0, Spearman=0.9992, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.bid4` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, ulist239 | Pearson=1.0, Spearman=0.9992, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.bid3` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, ulist239 | Pearson=1.0, Spearman=0.9992, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.bid2` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, ulist239 | Pearson=1.0, Spearman=0.9993, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, ulist239 | Pearson=1.0, Spearman=0.9993, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.ask5` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, ulist239 | Pearson=0.9997, Spearman=0.9204, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.ask4` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, ulist239 | Pearson=0.9997, Spearman=0.9204, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.ask3` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, ulist239 | Pearson=0.9997, Spearman=0.9204, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.ask2` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, ulist239 | Pearson=0.9997, Spearman=0.9204, LOO稳号=True |
| `ulist239.f144` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, ulist239 | Pearson=0.9997, Spearman=0.9205, LOO稳号=True |
| `ulist239.f144` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, ulist239 | Pearson=0.9997, Spearman=0.9205, LOO稳号=True |
| `ulist239.f144` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, ulist239 | Pearson=1.0, Spearman=0.9993, LOO稳号=True |
| `ulist239.f144` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, ulist239 | Pearson=1.0, Spearman=0.9979, LOO稳号=True |
| `ulist239.f144` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, ulist239 | Pearson=1.0, Spearman=0.9986, LOO稳号=True |
| `ulist239.f144` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f144` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, ulist239 | Pearson=0.9997, Spearman=0.9205, LOO稳号=True |
| `ulist239.f144` | `sina[1]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, ulist239 | Pearson=0.9999, Spearman=0.9963, LOO稳号=True |
| `ulist239.f144` | `fuyao.snapshot.open_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | fuyao, ulist239 | Pearson=0.9999, Spearman=0.9963, LOO稳号=True |
| `ulist239.f144` | `fuyao.snapshot.low_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | fuyao, ulist239 | Pearson=1.0, Spearman=0.9979, LOO稳号=True |
| `ulist239.f144` | `fuyao.snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | fuyao, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f144` | `fuyao.snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | fuyao, ulist239 | Pearson=1.0, Spearman=0.9986, LOO稳号=True |
| `ulist239.f110` | `tencent[70]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f11` | `tencent[80]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=0.9909, Spearman=0.9595, LOO稳号=True |
| `ulist239.f109` | `tencent[63]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `ulist239.f10` | `tencent[49]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `ulist239.f2` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=0.9997, Spearman=0.9204, LOO稳号=True |
| `tencent[27]` | `ulist239.f16` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=0.9997, Spearman=0.924, LOO稳号=True |
| `tencent[27]` | `ulist239.f15` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=0.9997, Spearman=0.9215, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=0.9997, Spearman=0.9204, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=0.9997, Spearman=0.9242, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=0.9997, Spearman=0.9215, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.bid5` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=0.9997, Spearman=0.9191, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.bid4` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=0.9997, Spearman=0.9192, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.bid3` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=0.9997, Spearman=0.9191, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.bid2` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=0.9997, Spearman=0.9196, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=0.9997, Spearman=0.9196, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.ask5` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.ask4` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.ask3` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.ask2` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[27]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[27]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[27]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, tencent | Pearson=0.9997, Spearman=0.9197, LOO稳号=True |
| `tencent[27]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, tencent | Pearson=0.9997, Spearman=0.924, LOO稳号=True |
| `tencent[27]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, tencent | Pearson=0.9997, Spearman=0.9215, LOO稳号=True |
| `tencent[27]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, tencent | Pearson=0.9997, Spearman=0.9204, LOO稳号=True |
| `tencent[27]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[27]` | `fuyao.snapshot.low_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | fuyao, tencent | Pearson=0.9997, Spearman=0.924, LOO稳号=True |
| `tencent[27]` | `fuyao.snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | fuyao, tencent | Pearson=0.9997, Spearman=0.9204, LOO稳号=True |
| `tencent[27]` | `fuyao.snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | fuyao, tencent | Pearson=0.9997, Spearman=0.9215, LOO稳号=True |
| `tencent[25]` | `ulist239.f2` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=0.9997, Spearman=0.9204, LOO稳号=True |
| `tencent[25]` | `ulist239.f16` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=0.9997, Spearman=0.924, LOO稳号=True |
| `tencent[25]` | `ulist239.f15` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tencent, ulist239 | Pearson=0.9997, Spearman=0.9215, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=0.9997, Spearman=0.9204, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.low` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=0.9997, Spearman=0.9241, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.high` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=0.9997, Spearman=0.9215, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.bid5` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=0.9997, Spearman=0.9191, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.bid4` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=0.9997, Spearman=0.9191, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.bid3` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=0.9997, Spearman=0.9191, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.bid2` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=0.9997, Spearman=0.9196, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.bid1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=0.9997, Spearman=0.9196, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.ask5` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.ask4` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.ask3` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.ask2` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=1.0, Spearman=1.0, LOO稳号=True |
| `tencent[25]` | `tdx.quote_full.ask1` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | tdx, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[25]` | `sina[7]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[25]` | `sina[6]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, tencent | Pearson=0.9997, Spearman=0.9197, LOO稳号=True |
| `tencent[25]` | `sina[5]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, tencent | Pearson=0.9997, Spearman=0.924, LOO稳号=True |
| `tencent[25]` | `sina[4]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, tencent | Pearson=0.9997, Spearman=0.9215, LOO稳号=True |
| `tencent[25]` | `sina[3]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, tencent | Pearson=0.9997, Spearman=0.9204, LOO稳号=True |
| `tencent[25]` | `sina[21]` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | sina, tencent | Pearson=1.0, Spearman=0.9999, LOO稳号=True |
| `tencent[25]` | `fuyao.snapshot.low_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | fuyao, tencent | Pearson=0.9997, Spearman=0.924, LOO稳号=True |
| `tencent[25]` | `fuyao.snapshot.last_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | fuyao, tencent | Pearson=0.9997, Spearman=0.9204, LOO稳号=True |
| `tencent[25]` | `fuyao.snapshot.high_price` | robust_correlation, affine_formula, per_stock_time_series | 140 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 | fuyao, tencent | Pearson=0.9997, Spearman=0.9215, LOO稳号=True |

_仅显示前 100 / 共 500 条。_


## 七、日期与数据质量告警（69）

- 20260904/em_kline_f61: 没有可用记录，快照跳过
- 20260904/push2: 没有可用记录，快照跳过
- 20260904/zhb: 来源有效交易日 20260903 不在本轮行情交易日窗口，快照跳过
- 20260907/em_kline_f61: 没有可用记录，快照跳过
- 20260907/push2: 没有可用记录，快照跳过
- 20260908/push2: 没有可用记录，快照跳过
- 20260909/em_kline_f61: 没有可用记录，快照跳过
- 20260909/push2: 没有可用记录，快照跳过
- 20260910/push2: 没有可用记录，快照跳过
- 20260910/tdx_f10_more: 没有可用记录，快照跳过
- 20260911/em_kline_f61: 采集状态 failed
- 20260911/em_kline_f61: 来源状态为 failed，快照跳过
- 20260911/push2: 没有可用记录，快照跳过
- 20260911/tdx_f10_more: 没有可用记录，快照跳过
- 20260914/em_kline_f61: 采集状态 partial
- 20260914/em_kline_f61: 来源状态为 partial，样本按部分快照参与
- 20260914/em_kline_f61: 没有可用记录，快照跳过
- 20260914/tdx_f10_more: 没有可用记录，快照跳过
- 20260904/em_hot: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260907/em_hot: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260908/em_hot: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260909/em_hot: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260910/em_hot: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260911/em_hot: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260914/em_hot: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260911/exchange: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260914/exchange: 纯市场上下文源已按默认策略排除；如需研究性碰撞请使用 --include-context
- 20260904/ftshare/market.limit_up_pool_yesterday: 默认碰撞已排除上下文记录（0 条）
- 20260907/ftshare/market.limit_up_pool_yesterday: 默认碰撞已排除上下文记录（0 条）
- 20260908/ftshare/market.limit_up_pool_yesterday: 默认碰撞已排除上下文记录（0 条）
- 20260909/ftshare/market.limit_up_pool_yesterday: 默认碰撞已排除上下文记录（0 条）
- 20260910/ftshare/market.limit_up_pool_yesterday: 默认碰撞已排除上下文记录（0 条）
- 20260911/ftshare/market.limit_up_pool_yesterday: 默认碰撞已排除上下文记录（0 条）
- 20260914/ftshare/market.limit_up_pool_yesterday: 默认碰撞已排除上下文记录（0 条）
- 20260904/fuyao/market.dragon_tiger: 默认碰撞已排除上下文记录（0 条）
- 20260904/fuyao/market.hot_list_hour: 默认碰撞已排除上下文记录（30 条）
- 20260907/fuyao/market.dragon_tiger: 默认碰撞已排除上下文记录（0 条）
- 20260907/fuyao/market.hot_list_hour: 默认碰撞已排除上下文记录（30 条）
- 20260908/fuyao/market.dragon_tiger: 默认碰撞已排除上下文记录（0 条）
- 20260908/fuyao/market.hot_list_hour: 默认碰撞已排除上下文记录（30 条）
- 20260909/fuyao/market.dragon_tiger: 默认碰撞已排除上下文记录（0 条）
- 20260909/fuyao/market.hot_list_hour: 默认碰撞已排除上下文记录（30 条）
- 20260910/fuyao/market.dragon_tiger: 默认碰撞已排除上下文记录（0 条）
- 20260910/fuyao/market.hot_list_hour: 默认碰撞已排除上下文记录（30 条）
- 20260911/fuyao/market.dragon_tiger: 默认碰撞已排除上下文记录（0 条）
- 20260911/fuyao/market.hot_list_hour: 默认碰撞已排除上下文记录（30 条）
- 20260914/fuyao/market.dragon_tiger: 默认碰撞已排除上下文记录（0 条）
- 20260914/fuyao/market.hot_list_hour: 默认碰撞已排除上下文记录（30 条）
- 20260904/market_sources/dragon_tiger_today: 默认碰撞已排除上下文记录（0 条）
- 20260907/market_sources/dragon_tiger_today: 默认碰撞已排除上下文记录（0 条）
- 20260908/market_sources/dragon_tiger_today: 默认碰撞已排除上下文记录（0 条）
- 20260909/market_sources/dragon_tiger_today: 默认碰撞已排除上下文记录（0 条）
- 20260910/market_sources/dragon_tiger_today: 默认碰撞已排除上下文记录（0 条）
- 20260911/market_sources/dragon_tiger_today: 默认碰撞已排除上下文记录（0 条）
- 20260914/market_sources/dragon_tiger_today: 默认碰撞已排除上下文记录（0 条）
- 折叠 42419 条重复字段样本，按快照质量择优；示例: market_sources.code/002571/T:20260904, market_sources.name/002571/T:20260904, market_sources.market/002571/T:20260904, market_sources.time/002571/T:20260904, market_sources.change_pct/002571/T:20260904, market_sources.price/002571/T:20260904, market_sources.change_type/002571/T:20260904, market_sources.date/002571/T:20260904, market_sources.code/603400/T:20260904, market_sources.name/603400/T:20260904
- 20260908/cninfo: 76 条事件记录缺少可解析的自然日，已跳过
- 20260909/cninfo: 76 条事件记录缺少可解析的自然日，已跳过
- 20260910/cninfo: 76 条事件记录缺少可解析的自然日，已跳过
- 20260911/cninfo: 76 条事件记录缺少可解析的自然日，已跳过
- 20260914/cninfo: 87 条事件记录缺少可解析的自然日，已跳过
- 20 条 verified 源字段来源未确认独立性，作为已知字段跳过重解但不作锚
- 58 条 verified 源字段映射到重复运行时身份，未作为已知字段或锚
- 203 条 verified 源字段元数据未达锚点条件（含义冲突 15 条、缺义/占位 202 条、单位冲突 6 条），已重新纳入待破解目标且不作碰撞锚
- 对撞模式：verified_anchor_only；待破解字段=458，verified 字段=657，可用独立锚=637，right 字段=284
- 主动方法候选共 8418 条，报告保留优先级最高的 500 条
- 跳过同一来源家族字段对：39657
- 跳过来源独立性未确认的字段对：1988
- 来源身份核验单独使用完整记录匹配；结果不会进入字段语义定案或独立锚

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

窗口内有 0 个唯一数据日的轮验记录；重复目录合并 0 条。
静态接口队列：未知 个接口，未知 个字段出现项，低于 E3 的字段出现项 未知；当前主动探针白名单 `未知`。

| 数据日 | 轮验状态 | 探针状态 / 请求数 | 来源身份状态 | 短线配对 | KPH/KPL 配对 | 证据文件 |
|:--|:--|:--|:--|--:|--:|:--|
| — | 当前窗口没有 AxData 日轮验证据 | — | — | — | — | — |

### FTShare 每日身份核验记录

窗口内保留 0 个唯一数据日的采集时记录；重复目录合并 0 条。

| 数据日 | 核验状态 | 接口状态计数 |
|:--|:--|:--|
| — | 当前窗口没有 FTShare 日轮验据 | — |

## 字母字段名语义提示（仅候选）

窗口内观察到 168 条需审阅的字母字段路径：含词义线索 63 条，仅拆词 105 条。
完整逐条记录保存在碰撞 JSON；名称线索清单：`docs/field_verification/20261014/20261014_alphabetic_field_name_inventory.csv`。
> 拼音、英文、缩写和混合拆词只用于检索候选；必须结合原始值、接口定义和独立来源复核，不得据此定案或改写主字典。

| 逐源字段路径 | 状态/审阅范围 | 名称形式与拆词 | 词义线索（非释义） | 样本日期 |
|:--|:--|:--|:--|:--|
| `市场源(market_sources)::change_type` | unverified / unverified_semantics | snake_case_or_mixed: change type | 变化/涨跌 + 类型 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `市场源(market_sources)::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `东财-push2ex::change_pct` | unverified / unverified_semantics | recognized_english_word_candidate: change pct | 变化/涨跌 + 百分比 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `东财-push2ex::code` | unverified / unverified_semantics | recognized_english_word_candidate: code | 代码 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `东财-push2ex::first_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: first limit time | 首次/第一 + 涨跌停限制 + 时间 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `东财-push2ex::last_limit_time` | unverified / unverified_semantics | snake_case_or_mixed: last limit time | 最近/上一期 + 涨跌停限制 + 时间 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `东财-push2ex::limit_count` | unverified / unverified_semantics | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `东财-push2ex::name` | unverified / unverified_semantics | recognized_english_word_candidate: name | 名称 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `东财-push2ex::price` | unverified / unverified_semantics | recognized_english_word_candidate: price | 价格 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `东财-push2ex::total_value` | unverified / unverified_semantics | snake_case_or_mixed: total value | 总 + 值 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `市场源(market_sources)::limit_count` | verified / verified_metadata_gap | snake_case_or_mixed: limit count | 涨跌停限制 + 数量/次数 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `市场源(market_sources)::limit_time` | unverified / unverified_semantics | snake_case_or_mixed: limit time | 涨跌停限制 + 时间 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `市场源(market_sources)::plate_limit_up_count` | verified / verified_metadata_gap | snake_case_or_mixed: plate limit up count | 涨跌停限制 + 上/涨 + 数量/次数 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `财联社(cls)::time` | unverified / unverified_semantics | recognized_english_word_candidate: time | 时间 | C:20260908, C:20260909, C:20260910, C:20260911, C:20260914 |
| `TDX(双命名源)::b_gu` | unverified / unverified_semantics | snake_case_or_mixed: b gu | B股 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::changqifuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: changqifuzhai | 长期负债 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::cunhuo` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: cunhuo | 存货 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::faren_gu` | unverified / unverified_semantics | snake_case_or_mixed: faren gu | 法人股 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::guding_zichan` | unverified / unverified_semantics | snake_case_or_mixed: guding zichan | 固定资产 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::gudongrenshu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: gudongrenshu | 股东人数 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::h_gu` | unverified / unverified_semantics | snake_case_or_mixed: h gu | H股 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::ipodate` | unverified / unverified_semantics | recognized_english_phrase_candidate: ipodate | IPO/上市日期（字段语境候选） | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::jing_lirun` | unverified / unverified_semantics | snake_case_or_mixed: jing lirun | 净利润 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::jing_zichan` | unverified / unverified_semantics | snake_case_or_mixed: jing zichan | 净资产 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::jinglirun` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jinglirun | 净利润 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::jingying_xianjinliu` | unverified / unverified_semantics | snake_case_or_mixed: jingying xianjinliu | 经营现金流（不确定净额/总额口径） | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::jingyingxianjinliu` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingyingxianjinliu | 经营现金流 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::jingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: jingzichan | 净资产 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::liudong_fuzhai` | unverified / unverified_semantics | snake_case_or_mixed: liudong fuzhai | 流动负债 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::liudong_zichan` | unverified / unverified_semantics | snake_case_or_mixed: liudong zichan | 流动资产 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::liudongfuzhai` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: liudongfuzhai | 流动负债 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::liutong_guben` | unverified / unverified_semantics | snake_case_or_mixed: liutong guben | 流通股本 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::meigujing_zichan` | unverified / unverified_semantics | snake_case_or_mixed: meigujing zichan | 每股净资产 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::meigujingzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: meigujingzichan | 每股净资产 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::yingshouzhangkuan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: yingshouzhangkuan | 应收账款 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::yingye_lirun` | unverified / unverified_semantics | snake_case_or_mixed: yingye lirun | 营业利润 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::zhuying_lirun` | unverified / unverified_semantics | snake_case_or_mixed: zhuying lirun | 主营利润（候选） | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::zhuying_shouru` | unverified / unverified_semantics | snake_case_or_mixed: zhuying shouru | 主营收入 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::zhuyingshouru` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zhuyingshouru | 主营收入 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::zibengongjijin` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zibengongjijin | 资本公积金 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::zong_guben` | unverified / unverified_semantics | snake_case_or_mixed: zong guben | 总股本 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::zong_xianjinliu` | unverified / unverified_semantics | snake_case_or_mixed: zong xianjinliu | 总现金流（接口口径待核） | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::zong_zichan` | unverified / unverified_semantics | snake_case_or_mixed: zong zichan | 总资产 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::zongguben` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongguben | 总股本 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::zongzichan` | verified / verified_metadata_gap | recognized_pinyin_phrase_candidate: zongzichan | 总资产 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `同花顺-fuyao::snapshot.open_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot open price | 开盘 + 价格 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `同花顺-fuyao::valuation.pb_mrq` | conflict / unverified_semantics | snake_case_or_mixed: valuation pb mrq | 市净率 + 最近报告期 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `同花顺-fuyao::valuation.pe_mrq` | conflict / unverified_semantics | snake_case_or_mixed: valuation pe mrq | 市盈率 + 最近报告期 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `同花顺-fuyao::valuation.pe_ttm` | conflict / unverified_semantics | snake_case_or_mixed: valuation pe ttm | 市盈率 + 滚动十二个月 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `ZHB-tdxstat::change_pct` | unverified / unverified_semantics | recognized_english_word_candidate: change pct | 变化/涨跌 + 百分比 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 |
| `ZHB-tdxstat::change_pct_1d` | unverified / unverified_semantics | snake_case_or_mixed: change pct 1 d | 变化/涨跌 + 百分比 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 |
| `ZHB-tdxstat::change_pct_2d` | unverified / unverified_semantics | snake_case_or_mixed: change pct 2 d | 变化/涨跌 + 百分比 | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 |
| `ZHB-tdxstat2::main_net_buy_amount` | unverified / unverified_semantics | snake_case_or_mixed: main net buy amount | 净 + 金额/成交额（需看接口） | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 |
| `ZHB-tdxstat2::main_net_buy_amount_1d` | unverified / unverified_semantics | snake_case_or_mixed: main net buy amount 1 d | 净 + 金额/成交额（需看接口） | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911 |
| `reports::actualLastTwoYearEps` | unverified / unverified_semantics | camel_case_or_mixed: actual Last Two Year Eps | 最近/上一期 + 每股收益 | C:20260909 |
| `reports::actualLastYearEps` | unverified / unverified_semantics | camel_case_or_mixed: actual Last Year Eps | 最近/上一期 + 每股收益 | C:20260909 |
| `reports::count` | verified / verified_metadata_gap | recognized_english_word_candidate: count | 数量/次数 | C:20260909 |
| `reports::lastEmRatingCode` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Code | 最近/上一期 + 代码 | C:20260909 |
| `reports::lastEmRatingName` | conflict / unverified_semantics | camel_case_or_mixed: last Em Rating Name | 最近/上一期 + 名称 | C:20260909 |
| `reports::lastEmRatingValue` | verified / verified_metadata_gap | camel_case_or_mixed: last Em Rating Value | 最近/上一期 + 值 | C:20260909 |
| `reports::market` | verified / verified_metadata_gap | recognized_english_word_candidate: market | 市场 | C:20260909 |
| `reports::predictLastYearEps` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Eps | 最近/上一期 + 每股收益 | C:20260909 |
| `reports::predictLastYearPe` | verified / verified_metadata_gap | camel_case_or_mixed: predict Last Year Pe | 最近/上一期 + 市盈率 | C:20260909 |
| `东财-push2ex::broken_count` | unverified / unverified_semantics | snake_case_or_mixed: broken count | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `东财-push2ex::circulating_value` | unverified / unverified_semantics | snake_case_or_mixed: circulating value | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `东财-push2ex::limit_fund` | unverified / unverified_semantics | snake_case_or_mixed: limit fund | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `东财-push2ex::sector` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: sector | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `东财-push2ex::turnover_rate` | unverified / unverified_semantics | snake_case_or_mixed: turnover rate | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `东财-push2ex::zt_continuous` | unverified / unverified_semantics | snake_case_or_mixed: zt continuous | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `东财-push2ex::zt_days` | unverified / unverified_semantics | snake_case_or_mixed: zt days | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `市场源(market_sources)::one_word` | unverified / unverified_semantics | snake_case_or_mixed: one word | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `市场源(market_sources)::plate_amount` | verified / verified_metadata_gap | snake_case_or_mixed: plate amount | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `市场源(market_sources)::plate_code` | verified / verified_metadata_gap | snake_case_or_mixed: plate code | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `市场源(market_sources)::plate_name` | verified / verified_metadata_gap | snake_case_or_mixed: plate name | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `市场源(market_sources)::popular` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: popular | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `财联社(cls)::content` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: content | — | C:20260908, C:20260909, C:20260910, C:20260911, C:20260914 |
| `财联社(cls)::level` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: level | — | C:20260908, C:20260909, C:20260910, C:20260911, C:20260914 |
| `财联社(cls)::reading_num` | unverified / unverified_semantics | snake_case_or_mixed: reading num | — | C:20260908, C:20260909, C:20260910, C:20260911, C:20260914 |
| `财联社(cls)::title` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: title | — | C:20260908, C:20260909, C:20260910, C:20260911, C:20260914 |
| `TDX(双命名源)::changqi_fuzhai` | unverified / unverified_semantics | snake_case_or_mixed: changqi fuzhai | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::faqiren_faren_gu` | unverified / unverified_semantics | snake_case_or_mixed: faqiren faren gu | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::gudong_renshu` | unverified / unverified_semantics | snake_case_or_mixed: gudong renshu | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::guojia_gu` | unverified / unverified_semantics | snake_case_or_mixed: guojia gu | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::industry` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: industry | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::ipo_date` | verified / verified_metadata_gap | snake_case_or_mixed: ipo date | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::lirun_zonghe` | unverified / unverified_semantics | snake_case_or_mixed: lirun zonghe | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::province` | verified / verified_metadata_gap | unsegmented_latin_pinyin_or_word: province | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::reserve2` | unverified / unverified_semantics | mixed_alphanumeric: reserve 2 | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::shuihou_lirun` | unverified / unverified_semantics | snake_case_or_mixed: shuihou lirun | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::touzi_shouyu` | unverified / unverified_semantics | snake_case_or_mixed: touzi shouyu | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::updated_date` | verified / verified_metadata_gap | snake_case_or_mixed: updated date | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::updateddate` | unverified / unverified_semantics | unsegmented_latin_pinyin_or_word: updateddate | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::weifen_lirun` | unverified / unverified_semantics | snake_case_or_mixed: weifen lirun | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::wuxing_zichan` | unverified / unverified_semantics | snake_case_or_mixed: wuxing zichan | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::yingshou_zhangkuan` | unverified / unverified_semantics | snake_case_or_mixed: yingshou zhangkuan | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::zhigong_gu` | unverified / unverified_semantics | snake_case_or_mixed: zhigong gu | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `TDX(双命名源)::ziben_gongjijin` | unverified / unverified_semantics | snake_case_or_mixed: ziben gongjijin | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `同花顺-fuyao::fin_report` | unverified / unverified_semantics | snake_case_or_mixed: fin report | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `同花顺-fuyao::snapshot.prev_price` | verified / verified_metadata_gap | snake_case_or_mixed: snapshot prev price | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |
| `同花顺-fuyao::valuation.ps_ttm` | conflict / unverified_semantics | snake_case_or_mixed: valuation ps ttm | — | T:20260904, T:20260907, T:20260908, T:20260909, T:20260910, T:20260911, T:20260914 |

Markdown 显示前 100 条；其余 68 条完整保留在 JSON。

## 探索候选持续跟踪

研究台账：`collision_research_state.json.gz`；累计历史跟踪候选对 0，本报告候选对 715，历史复现 0，新发现 0。
台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，不会自动改变字段状态、碰撞锚或主字典。新报告只将 `actionable_L1`、L4 和主动方法候选写入待研究队列；已登记关系的复验单独展示，历史跟踪记录不会被删除。
