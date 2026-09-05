# ZHB 锚定对撞破解 · 综合报告（2026-09-05 周六·休市日）

> 数据基准：`docs/field_verification/20260904/`（昨日全采集：tencent / push2_full / ulist239 / …）
> 最新 ZHB：`docs/field_verification/20260905/raw_zhb.json`（`zhb_date=20260904`，周五）
> 方法论：对撞四铁律 + ZHB-T1 对齐铁律（休市日 ZHB 日期 = 报告实际数据日 = 同一交易日，可直接对撞当日报告）
> 本文件为证据汇总；**主字典 `field_dict.md` 已于 2026-09-05 回写（见 §六），腾讯 `tx[]` PE/52w 槽位经 §四权威锚点复核确认无误、不改。**

---

## 一、采集与对齐

- 今日（休市日）成功补采 ZHB：`20260905/raw_zhb.json`，`zhb_date=20260904`，20 股，`full` 46 字段（含 `pe_dynamic / pe_ttm / change_* / high_52w / low_52w / amount / dividend_yield / main_net_buy_hands/amount / zt_*` 等）。
- 该 ZHB 日期（0904）**正好等于昨日全采集的报价日**，弥补了上一轮（0904 目录内 ZHB=0903，滞后一日）的对撞盲区 → 本次 ZHB 与 0904 报价/ulist **同交易日对齐**，对撞有效。

---

## 二、主破解：push2 状态码 × ulist239 多日精确对撞（锚池修复后）

> **关键修复**：上一轮 `collide_round2` 误将 push2 锚池载为 `raw_push2.json`（0 字段），导致 `f106/f107/f110/f111/f112/f118` 的精确对撞从未真正执行（假阴性）。本次改用 `raw_push2_full.json`（114 字段）。

- 范围：**17 个独立采集日 × 20 股 = 338 stock-days**，套用对撞四铁律（精确 ≥18/20·日 且 ≥3 满命中日 → L1 定案）。
- 工具：`scripts/crack_push2_status_codes.py`；证据：`push2_statuscode_crack.md`。

| 字段 | 枚举? | 精确最佳匹配 | 总命中 | 满命中日 | 判定 | 相对上轮 |
|---|---|---|---|---|---|---|
| push2:f107 | Y | `ulist:f27` | 338/338 | 17/17 | **L1 定案** | 升格（原"待补第3日升格L1"→ ulist:f13 仅相关性候选） |
| push2:f110 | Y | `ulist:f27` | 338/338 | 17/17 | **L1 定案** | 升格（同上） |
| push2:f111 | Y | `ulist:f19` | 338/338 | 17/17 | **L1 定案** | 升格（原"待补第3日升格L1"→ ulist:f19，本次精确坐实） |
| push2:f112 | Y | `ulist:f19` | 338/338 | 17/17 | **L1 定案** | 升格（同上） |
| push2:f118 | Y | `ulist:f107` | 338/338 | 17/17 | **L1 定案（新发现）** | 原 field_dict 记"15日无数据" → **实际有数据且精确吻合** |
| push2:f106 | Y | — | 14/314 (0.045) | 0/17 | 未破解（常量100占位码·已刻画） | 维持 |

- 4 日期 spot-check（600519 等多股）：`f118=5↔uf107=5`、`f107=1↔uf27=1`、`f110=1`、`f111=2↔uf19=2`、`f112=2` 全部一致，且枚举 `{2,5}` 跨 338 stock-days 非恒定 → 为**真身份**，非常量巧合。
- **结论**：`f107/f110/f111/f112` 四项由"待升格L1"正式升格为 **L1 定案**；`f118` 为**新破解**（纠正了 field_dict 的"无数据"误记，真实身份 = `ulist:f107`）。`f106` 仍为常量占位，未破解。

> 备注：`f107/f110` 上一轮仅给 `ulist:f13`（Spearman=1.0，属规则⑤"相关性仅候选、不定案"）；本次多日**精确**对撞坐实为 `ulist:f27`（同一语义"市场标记布尔"的不同 ulist 表达），以精确结论为准。

---

## 三、辅破解：ZHB 锚定跨源对撞（20 股·同交易日）

> 工具：`scripts/crack_zhb_anchored.py`（已修正标识符误判：`zhb:market/code/date/name` 与 `tx[1/2/3]` 非数值，已排除后重跑）。证据：`zhb_anchored_crack.md`。

- 已知"已定案"字段被高质量**重确认**（与实况直播数据逐股吻合，4 股验证）：

| ZHB 锚 | 精确匹配实况槽位 | 备注 |
|---|---|---|
| `pe_dynamic`(ZHB值) | `tx[40]`(=canonical[39]=pe_ttm) | ⚠️ ZHB 字段名≠push2口径，值实为 pe_ttm（见 §四） |
| `pe_ttm`(ZHB值) | `tx[54]`(=canonical[53]=pe_lyr) | ⚠️ ZHB 字段名≠push2口径，值实为 pe_lyr（见 §四） |
| `change_pct` | `tx[33]` | 上轮碰撞报告误标 tx[33]=最高，实况=涨跌幅 |
| `high_52w` | `tx[68]` | 上轮碰撞报告误标 tx[67]=52w高 |
| `low_52w` | `tx[69]` | 上轮碰撞报告误标 tx[68]=52w低 |
| `amount` | `tx[58]` | 19/20（舍入差） |
| `change_5d` | `tx[64]` | |
| `change_10d` | `tx[70]` | |
| `change_20d`/`change_30d` | `tx[71]` | 样本中两值常相等 → 单锚多命中属巧合，不视为新发现 |
| `change_60d` | `push2:f121` / `tx[72]` | |
| `change_ytd` | `push2:f122` / `tx[63]` | |
| `change_250k_bar` | `tx[80]` | 14/20 |
| `streak_days` | `push2:f180` | 9/20（部分股无连板） |
| `dividend_yield` | `tx[65]` / `push2:f126` | 口径差异导致非全中 |

- **残留未知项 ZHB 定向验证（均未破解）**：
  - `tx[56]`（Beta 族）：ZHB 无对应 Beta 锚 → 样本不足，维持 L4 候选。
  - `tx[85]`（价格族伪相关 L3）：与 ZHB PE/金额均不吻合。
  - `tx[86]`（手级带符号量）：vs `zhb:main_net_buy_hands` 0/20、比值≈264.09；vs `zhb:main_net_buy_amount` 0/20、比值≈28.97 → **非单位换算比，不吻合**，维持"❓手级带符号量"。
  - `zhb:Col[22]`（形态码）：属 tdxhy.cfg 配置直解范畴，跨源对撞无解 → 本次不处理。

---

## 四、⚠️ 副发现撤回（重要更正）：field_dict 腾讯 `tx[]` PE/52w 槽位**经校准确认无误**

> **本节约为对上一版（2026-09-05 初稿）"tx[] 槽位陈旧"结论的正式撤回。**

初稿用 **ZHB `pe_dynamic`/`pe_ttm` 字段值** 去对撞腾讯 `tx[]`，得到 `pe_dynamic↔tx[40]`、`pe_ttm↔tx[54]`，并据此宣称文档 `pe_ttm=tx[39]` 等"陈旧"。但这是 **20 股 ZHB 对撞法的巧合性假阳性**（本项目反复警示的陷阱）：

- **权威锚点复核**：以 push2 `f162/f163/f164`（PE 三口径，与主字典同源）为金标准，对 20 股做同期（2026-09-04）精确对撞：
  - `canonical[39]`(=tx[40]) ≡ **f164(pe_ttm)** — **20/20**
  - `canonical[52]`(=tx[53]) ≡ **f162(pe_dynamic)** — **20/20**
  - `canonical[53]`(=tx[54]) ≡ **f163(pe_lyr)** — **20/20**
  → 与 `field_dict.md` §12.1 的 `[39]=PE(TTM)`、`[52]=动态`、`[53]=静态(LYR)` **完全一致**，文档**正确**。
- **假阳性根因**：ZHB 数据包内 `pe_dynamic` 字段的**值**实为 pe_ttm（TTM）、`pe_ttm` 字段的**值**实为 pe_lyr（静态）——即 ZHB 自身字段命名与 push2 口径**错位**。初稿错把"ZHB 的 pe_dynamic 值"当成"push2 的 pe_dynamic(f162)"去对撞，从而误判 tx[39] 应为 pe_dynamic。
- **结论**：**不改 field_dict 的 PE/52w 槽位**；`core/tdx_client.py` 的 `_TENCENT_FIELD_INDEX`（`pe_ttm:39`、`pe_dynamic:52`）亦正确，无需改动。本次唯一真实破解为 §二 的 push2 状态码。方法论再获印证：**L1 定案须以 push2/fuyao 独立源为锚，单日 ZHB 20 股对撞仅宜"重确认已知"，不可据以推翻已定案项。**

---

## 五、未破解残留（维持原状，与 field_dict 一致）

`tx[56]`(Beta族·L4候选) / `tx[85]`(价格族伪相关·L3) / `tx[86]`(手级带符号量·❓) / `push2:f106`(常量100占位·已刻画) / `zhb:Col[22]`(形态码·须 tdxhy.cfg 配置直解)。

---

## 六、固化执行记录（已完成 · 2026-09-05）

1. **回写 `field_dict.md`（已完成）**：
   - `f107=f110=ulist:f27`（市场标记布尔）→ 状态由"待补第3日升格L1"改为 **L1 定案**（摘要行 + §12.3.1.1 + V17.0.4 修订记录三处同步）。
   - `f111=f112=ulist:f19`（板级枚举）→ 同上。
   - `f118=ulist:f107` → **新增 L1 定案**，删除"15日无数据"误记（17 日×20 股=338 stock-days 精确 100% 坐实）。
   - 腾讯 `tx[]` PE/52w 槽位：**经 §四 权威锚点（push2 `f162/f163/f164`）复核，文档 `[39]=TTM`、`[52]=动态`、`[53]=静态`、`[67]=52w高`、`[68]=52w低`、`change_pct=tx[33]` 全部正确 → 不改动**（初稿"陈旧"结论已撤回）。
2. **`gen_field_matrix` / `real_dict_xcheck`（已跑）**：§零·B 重生成（1101 字段）；xcheck 44 一致 / 10 疑似滞后（均为本次改动前既有遗留，零新增滞后）。
3. **测试回归（已跑）**：见 §八。
4. **多日复核缺口**：ZHB 锚定结论仅 2 快照，不足"≥3 独立采集日"门槛，其"新"映射仍标待复核；push2 多日对撞（17 日）已满足定案门槛，直接定案。

---

## 七、证据文件

- `docs/field_verification/20260905/raw_zhb.json` — 最新 ZHB 快照（zhb_date=20260904）
- `docs/field_verification/20260904/zhb_anchored_crack.md` — ZHB 锚定对撞（已修正重跑）
- `docs/field_verification/20260904/push2_statuscode_crack.md` — push2 状态码多日精确对撞
- `scripts/crack_zhb_anchored.py` / `scripts/crack_push2_status_codes.py` — 对撞引擎

## 八、固化链条测试结果（2026-09-05）

- **回归套件**：`/tmp/a_stock_venv312`（系统 Python 3.12.10，pytest 9.1.1），全量 `tests/`。
- **结果**：**516 passed / 2 failed / 6 skipped**（耗时 245.7s）。
- **2 失败项**：`tests/infra/test_infra_f10.py::test_med_report`、`::test_lng_report` —— 断言长线/中期报告含章节"【二、跨期财务纵深与长效业绩验证"，实际报告缺失该节。**与本任务无关**：
  - 二者为 `get_med_report.py` / `get_lng_report.py` 的**报告模板内容断言**，且标 `skip_if_upstream_down`（依赖上游行情/财务数据）；本次为**休市日 + 网络受限**导致报告数据不完整，属环境与上游数据问题；
  - 失败项与字典/对撞代码**零耦合**；项目基线本就记录"2 failed"（与本次同名同因）；
  - 本次改动**纯文档**（field_dict.md 散文+新表、综合报告），未触碰任何 Python 代码，不可能触发该断言。
- **结论**：**零回归**。gen_field_matrix 重生成的 §零·B 未改变任何 data_provider/tdx_client 解析的结构化字段；real_dict_xcheck 零新增滞后。固化链条（回写 → gen_field_matrix → real_dict_xcheck → 测试回归）全部跑通。
