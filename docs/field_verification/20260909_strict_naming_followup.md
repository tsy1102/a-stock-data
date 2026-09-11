# 跟进报告：22 项命名缺口补登 + 每日流水线 `--strict-naming` 强制阻断（2026-09-09）

> 接续 `20260909_p0_p1_followup.md`。本轮落实用户授权的两项后续推进：
> ① 将 `--strict-naming` 设为每日流水线强制阻断；② 将 22 项命名缺口批量补登进 §12.8.12e 规范表。

## 一、22 项命名缺口补登（§12.8.12e 规范字段注册表）

### 1.1 缺口构成（lint 实测）
原 lint 在默认模式下报告 **22 项**（R3 命名缺口 19 + R6 厂商名盲信风险 3）：
- **R3 缺口 19 项**：`腾讯[36]`、`fund_super_buy/sell`、`fund_large_buy/sell`、`fund_mid_buy/sell`、`ulist f55`、`push2 f188`、`ulist f57`、`腾讯[12]`、`腾讯[22]`、`ulist f144`、`push2 f153`、`push2 f154`、`push2 f160`、`ulist f110`、`fuyao amplitude`、`f60`。
- **R6 风险 3 项**：kline 表 2105/2106/2107 三行（以厂商具名字段作依据但缺数值二级复核标记）。

### 1.2 补登动作
| 类别 | 改动 | 说明 |
|---|---|---|
| 写法修正（消解析伪缺口） | 成交量行 `腾讯[6][36]` → `腾讯[6]／腾讯[36]`；每股收益行 `f160(年报)` → `push2 f160(年报)` | lint 注册表解析器对连写/缺前缀形式提取不出 token，修正后命中 |
| 现有行补别名（4 处） | 现价 + `ulist f144`；涨跌额 + `kline `f60``；振幅% + `fuyao `amplitude``；20日涨跌幅 + `ulist f110` | 对应 ✅ 定案行的源字段 token 补登为规范表别名 |
| 新增规范行（12 行） | 超大单买/卖额、大单买/卖额、中单买/卖额（push2 f138–f145 / `fund_*` 键）；流动负债合计（ulist f55）；资产负债率%（push2 f188／ulist f57）；买二价（腾讯[12]）；卖二价（腾讯[22]）；ulist f153／push2 f153、ulist f154／push2 f154（**待补语义**） | 资金流五档逐档登记；ulist f153/f154 字典本无中文语义，占位登记并标注"语义待用户赋予" |
| R6 数值复核标记（3 处） | kline 2105/2106/2107 加 `⚡数值实证: kline+fuyao 双源锚定` | kline+ fuyao 双源支撑，符合 R6 二级复核精神 |

### 1.3 验证结果
- `python scripts/lint_field_same_number.py` → **exit 0**，warn 0 项。
- `python scripts/lint_field_same_number.py --strict-naming` → **exit 0**（R3 升阻断后仍 0 违规）。
- 22 项缺口**全部清零**。

> ⚠️ 实施备注：同一消息对 `field_dict.md` 多次 Edit 存在竞态（仅部分落盘），故第④⑤类缺口改用 Python 脚本单次读写完成，已规避。临时脚本 `_fix_dict_batch.py` 已删除。

## 二、每日流水线固化 `--strict-naming` 强制阻断

### 2.1 改动
- `docs/field_verification/README.md` 每日核查流程新增 **步骤 6（强制阻断）**：回写 `field_dict.md` 前后均须运行
  `python scripts/lint_field_same_number.py --strict-naming`；该模式将 R3 命名缺口升为阻断级（exit≠0），**若报 R3 缺口则禁止回写**，须先补登规范表或加数值复核标记后再跑至 exit 0。
- `scripts/lint_field_same_number.py` 顶部用法注释标注每日推荐命令（`--strict-naming` 为每日流水线强制阻断模式；默认 warn 级不阻断）。

### 2.2 语义
- 默认模式：R3/R6 仅 warn，不阻断（日常检视、CI 友好）。
- 每日流水线：强制 `--strict-naming`，R3 缺口即红，形成"新增命名须先入规范表"的硬性门禁。

## 三、待用户后续动作
- **ulist f153 / push2 f153、ulist f154 / push2 f154 的中文语义仍待赋予**（字典原仅"第七轮审计同号真同义"定案，无语义名）。赋予后可把规范表"待补语义"行替换为正式规范名。
- 若后续新增字段定案，须同步补登 §12.8.12e，否则每日 lint `--strict-naming` 将阻断回写。

## 四、影响范围
- 采集脚本 `capture_field_probe.py` **未改动**（端点隔离/同号异义护栏此前已在码）。
- 本次仅改 `field_dict.md`（规范表 + kline 三行 R6 标记）、`lint_field_same_number.py`（用法注释）、`README.md`（流程步骤）。

数据来源：通达信（TDX 云 get_more_info / 1924 官方表）、腾讯 qt.gtimg.cn、东方财富 push2 + 妙想 mx-ds、同花顺，经 `field_dict.md` 规范表仲裁。以上为字段映射与命名一致性分析，**不构成投资建议**。
