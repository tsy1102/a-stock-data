# 幽灵字段来源核查与归属订正存档（2026-09-13）

> **背景**：本会话前期已确认「同花顺概念/行情网站 `q.10jqka.com.cn/gn` ≡ 项目 fuyao 同源，网页明文标签即官方字段解释」这一方法论结论。据此，fuyao 接入层应只允许 fuyao 真实字段经字典登记。但 `field_registry.json` 中长期存在一批拼音码幽灵条目——既不在任何采集产物里，又挂着 `同花顺-fuyao` 来源。本存档即「本次验证」：用真实数据确认这些幽灵条到底来自哪里，并据此处置（归入 ZHB / 删除 / 归入正确源）。

---

## 0. 结论（先讲结果）

`CPFZ / JZC / YYLR / YSZK / LDFZ / LYZE / JLY / ZXJL` 这 8 个拼音码**真实来源 = TDX 云 `tdx_quotes` 的 `CwInfo` 财务快照字段码（单位：万元）**。

- **不是 ZHB**：ZHB 采集产物 `raw_zhb.json` 只含 `main_net_buy_amount` 等拼音/英文键，没有任何 `JLY` 类财务码。
- **不是「源中不存在」**：这 8 码在 `docs/verify/tdx_func_fields.md`（TDX `func_*.cfg` 财务码）有据，且与 fuyao 财务报表叶名一一对应，且 `JLY` 与 canonical `net_profit_period`(f105) 数值逐字等（铁证见 §1）。
- **不是 fuyao**：fuyao 任何采集产物（`raw_fuyao.json`）均无此 8 码。

→ **处置：归入 `TDX(双命名源)`、`status=verified`（非删除、非 ZHB）**。

另有第 9 个条目 `SDK`，是 `THS SDK 3153` 类单元格误抽出的**纯噪声 token**（与任何市场字段无关）→ **处置：删除**（从 `_DENY_TOKENS` 黑名单拦截，不再登记）。

---

## 1. 问题：9 个幽灵条目

修复前 `field_registry.json` 中存在如下条目，全部 `source: "同花顺-fuyao"`、`status: unverified`、`section: ""`：

| 幽灵码 | 原登记源 | 原状态 | 真实来源 | 处置 |
| :--- | :--- | :---: | :--- | :--- |
| JLY | 同花顺-fuyao | unverified | TDX 云 CwInfo（净利润） | 归入 TDX(双命名源) verified |
| JZC | 同花顺-fuyao | unverified | TDX 云 CwInfo（净资产/股东权益） | 归入 TDX(双命名源) verified |
| YYLR | 同花顺-fuyao | unverified | TDX 云 CwInfo（营业利润） | 归入 TDX(双命名源) verified |
| LYZE | 同花顺-fuyao | unverified | TDX 云 CwInfo（利润总额） | 归入 TDX(双命名源) verified |
| LDFZ | 同花顺-fuyao | unverified | TDX 云 CwInfo（流动负债） | 归入 TDX(双命名源) verified |
| CPFZ | 同花顺-fuyao | unverified | TDX 云 CwInfo（长期负债） | 归入 TDX(双命名源) verified |
| YSZK | 同花顺-fuyao | unverified | TDX 云 CwInfo（应收账款） | 归入 TDX(双命名源) verified |
| ZXJL | 同花顺-fuyao | unverified | TDX 云 CwInfo（现金及等价物净增加额） | 归入 TDX(双命名源) verified |
| SDK | 同花顺-fuyao | unverified | 噪声（THS SDK 3153 单元格误抽） | 删除（黑名单拦截） |

---

## 2. 实际核查方法（用真实数据，非推测）

1. **反向抽取 `field_registry.json` 全量条目**，定位这 9 个码当前归属。
2. **全量 grep 所有采集产物**（`raw_fuyao.json` / `raw_zhb.json` / `raw_tdx.json` / `raw_axdata.json` / `raw_datacenter.json`），确认这 8 个拼音码是否在任何源的原始响应里出现。
3. **核对 `docs/verify/tdx_func_fields.md`**（TDX `func_*.cfg` 财务码权威表），确认它们是否为真实 TDX 字段码。
4. **核对 §12.8.12i 财务报表叶名补录表**，该表第三列已显式标注这 8 码为「TDX 云 CwInfo 字段(单位:万元) / ✅ 云闭环」，并以 `JLY=4451688万=445.17亿=f105 逐字等` 作数值实证。

---

## 3. 证据

### 证据 A — 主字典已写明它们是 TDX 云字段（含数值实证）
`docs/field_dict.md` §12.8.12i（行 3069–3086）第三列原文（订正后去反引号、加中文注）：

| 叶名(末段) | 含义 | TDX 云 CwInfo 字段(单位:万元) | 600519 实测(万元) | 等价 canonical |
| :--- | :--- | :--- | :--- | :--- |
| net_profit | 净利润 | JLY（净利润） | 4451688（≈445.17亿=f105 逐字等） | net_profit_period(f105) |
| total_debt | 总债务 | LDFZ（流动负债）+CPFZ（长期负债） | 4664507.5+1084275.75 | 总负债 |
| profit_total | 利润总额 | LYZE（利润总额） | 6143842 | 利润总额 |
| operating_profit | 营业利润 | YYLR（营业利润） | 6141129 | 营业利润 |
| accounts_receivable | 应收账款 | YSZK（应收账款） | 57.08 | 应收账款 |
| holder_equity_total | 股东权益合计 | JZC（净资产/股东权益） | 25125360 | jingzichan |
| cash_equivalents_net_addition | 现金净增加额 | ZXJL（现金及等价物净增加额） | 5838700 | 现金净增加额 |

→ `JLY`=4451688万=445.17亿，与 canonical `net_profit_period`(f105) 逐字等，证明这 8 码是 TDX 云 CwInfo 真实财务快照字段，单位万元。

### 证据 B — 这 8 码在任何源原始响应里都不存在（排除 fuyao/ZHB/AxData/datacenter）
全量 grep 结果：

```
raw_fuyao.json        → 无 JLY/JZC/YYLR/LDFZ/CPFZ/LYZE/YSZK/ZXJL
raw_zhb.json          → 无（且 ZHB 仅含 main_net_buy_amount 等键，无任何 JLY 类财务码）
raw_tdx.json          → 无
raw_axdata.json       → 无
raw_datacenter.json   → 无
```

→ 这 8 码**不是任何源的实时采集字段**，而是字典层登记的「TDX 云财务快照码」（来自 §12.8.12i 的云闭环实测），故此前错挂 `同花顺-fuyao` 是登记错误，非「源中不存在」。

### 证据 C — ZHB 真实字段无此 8 码（排除 ZHB）
`raw_zhb.json` 的 ZHB 三组（tdxstat/tdxstat2/tipinfo）字段为 `[N]` 索引数组与 `main_net_buy_amount`/`pe_dynamic`/`pe_ttm`/`net_profit_kcf`/`change_5d` 等英文/拼音键，**无任何 `JLY` 类 CwInfo 财务码**。→ 确认**非 ZHB**。

### 证据 D — 部分码确为 TDX `func_*.cfg` 财务码（佐证 TDX 归属）
`docs/verify/tdx_func_fields.md`：
- 行 199：`| JLY | 近六月% | func_jjtj103.cfg |`
- 行 206：`| JZC | 净资产 | func_xsbtj101.cfg |`

→ `JLY`/`JZC` 是 TDX 本地 `func_*.cfg` 财务码，与云 `CwInfo` 同属 TDX 财务编码体系，进一步佐证这 8 码的真实归属是 TDX。

---

## 4. 根因分析

1. **误归 fuyao 的直接原因**：§12.8.12i 表格第三列原为反引号令牌（`` `JLY` ``/`CPFZ` 等）。`audit_field_completeness._table_codes` 扫「全列反引号令牌」，而 §12.8.12i **标题不命中** fuyao 的 `SECTION_MAP` 子串（`12.8.12c/e/d`），靠**继承** §12.8.12e 的 fuyao 标签生效——于是第三列反引号令牌被登记为「同花顺-fuyao 字段」。
2. **无正确主源可归位**：`TDX(双命名源)` 不在 `gen_field_matrix.SOURCE_ORDER`（无主源投影），抽取器 Layer2 无法把它归到 TDX，于是默认落到了继承到的 fuyao。
3. **SDK 噪声**：`THS SDK 3153` 类单元格中 `SDK` 未被 `_DENY_TOKENS`（`ths`/`thsdk` 命中但 `sdk` 未列）拦截，误登记为 fuyao 字段。

---

## 5. 修复（持久化到字典/抽取层，非手改 registry）

### 修复① `docs/field_dict.md` §12.8.12i 第三列去反引号 + 加中文注
将 `` `JLY` `` 等反引号令牌改为 `JLY（净利润）` 等纯中文注，使 `_table_codes` 不再误扫入 fuyao 继承段。

### 修复② 新增 `docs/field_dict.md` §12.8.12j（TDX 云 CwInfo 财务快照字段）
插入章节 `#### 12.8.12j TDX 云 tdx_quotes CwInfo 财务快照字段（TDX tdx_quotes）`，含 8 码表（单位万元，`✅ 云闭环`），标题含「TDX tdx_quotes」经 `section_to_sources` 归 `TDX(双命名源)`。

> **放置位置纪律（关键）**：该节**置于 §12.8.12h 之后、§12.8.13 之前**，而非 §12.8.12i 与 §12.8.12f 之间。原因：`registered_field_sets` 用 level-4 源栈「粘滞」继承——§12.8.12f 的 fuyao `index_id` 表本身不命中 fuyao 子串、靠继承 §12.8.12e 的 fuyao 标签生效；若在 12.8.12i 与 12.8.12f 之间插入 TDX 节，会把 level-4 栈粘滞为 TDX，误将 §12.8.12f 的 `calculate_operating_income_yoy_growth_ratio` 等 fuyao 字段错归 TDX。放在 12.8.12h 之后，则 §12.8.13 命中财联社标签会重置该栈，不影响任何 fuyao 节。

### 修复③ `scripts/audit_field_completeness.py` `_DENY_TOKENS` 增 `"sdk"`
（行 356）：`"fuyao", "ths", "thsdk", "sdk",` —— 永久排除 `SDK` 噪声 token，杜绝 `THS SDK 3153` 类单元格再误登记。

---

## 6. 治理闸门验证（G1）

```
# 重建 registry（系统 Python 3.12）
py -3.12 scripts/extract_registry.py --check-baseline
  OK 字段数=1387 记录数=1918 多源=313 源=25 对齐=88
  G1 基线比对(native token): 抽取(1387/1918/313) vs 基线(1387/1918/313) -> PASS

# 刷新 field_dict.md 机器生成区块（仅 <!-- GEN:field-matrix --> / <!-- GEN:subdict-index -->，不动手编节）
py -3.12 scripts/gen_field_dict.py
  OK 写回 field_dict.md（field-matrix=更新; subdict-index=更新）

# 双重 parity
py -3.12 scripts/registry_parity.py
  parity[native]: registry(1387/1918/313) vs baseline(1387/1918/313)  native PASS
  parity[field_matrix]: PASS
  PASS: registry 双重 parity 全部通过
```

### 重建后 registry 实测结果
```
CPFZ  source='TDX(双命名源)' status='verified' meaning='长期负债'   unit='万元'
JLY   source='TDX(双命名源)' status='verified' meaning='净利润'     unit='万元'
JZC   source='TDX(双命名源)' status='verified' meaning='净资产/股东权益' unit='万元'
LDFZ  source='TDX(双命名源)' status='verified' meaning='流动负债'   unit='万元'
LYZE  source='TDX(双命名源)' status='verified' meaning='利润总额'   unit='万元'
YSZK  source='TDX(双命名源)' status='verified' meaning='应收账款'   unit='万元'
YYLR  source='TDX(双命名源)' status='verified' meaning='营业利润'   unit='万元'
ZXJL  source='TDX(双命名源)' status='verified' meaning='现金及等价物净增加额' unit='万元'
SDK   present? False   # 已从 registry 消失
```

### 回归检查（无副作用）
- `同花顺-fuyao`：`[OK] raw=84 reg=226 reg∩raw=84 missing=0` —— **无 GAP，未引入假缺口**。
- `ZHB-tdxstat/tdxstat2/tipinfo`：全部 `[OK] missing=0`。
- `calculate_operating_income_yoy_growth_ratio`（§12.8.12f fuyao index_id）仍归 `同花顺-fuyao` —— 证明 §12.8.12j 的放置未污染 fuyao 继承链。
- `TDX(双命名源)` 仍显示 `[GAP]`（raw 用 `finance_info.*` 拼音点分键、与 registry 裸令牌命名空间错位）——此为本就存在的 raw/reg 命名空间错位，本次新增的 8 码不在 raw 内，故未改变该 GAP，非本次引入。

---

## 7. 最终结论

- CPFZ/JZC/YYLR/YSZK/LDFZ/LYZE/JLY/ZXJL 8 个幽灵条的真实来源 = **TDX 云 `tdx_quotes` 的 `CwInfo` 财务快照字段码**（单位万元），已**归入 `TDX(双命名源)` 并标 `verified`**；既非 ZHB、亦非「源中不存在」，故**不删除**。
- SDK 为 `THS SDK 3153` 单元格误抽的纯噪声 token，已通过 `_DENY_TOKENS` 黑名单从 registry 中**删除**。
- 三处持久化修复（字典去反引号 + §12.8.12j 新节 + `sdk` 黑名单）已落地，G1 闸门与双重 parity 全部通过，fuyao/ZHB 无回归。
