# 对 Gemini 回复（第二轮）的逐条核实

- 核实对象：`user_query` 附 Gemini 回复（反驳"第三方 AI 审查报告"，主张 tipinfo Col[9]=业绩预告金额、f130/f131 等系既有 L1、f226 维持候选、tx[56]/[85]/[86] 实锤）
- 核实基准：权威仓库 `/c/Tencent/WorkBuddy/a-stock-data` @ `1e1233d` (V17.3.6)
- 核实时间：2026-09-21

## 总判定

| 维度 | 结论 |
|---|---|
| tipinfo Col[9] 反驳（张冠李戴论点） | ✅ **成立**——确实有两个不同文件的 Col[9]，Gemini 反驳"审查员"混淆是正确的 |
| 采纳 f130/f131/f142/f143 非"新发现" | ✅ **成立**——field_dict 早已定案（L6185） |
| 采纳 f226 维持 ⚠️ 候选+护栏 | ✅ **成立**——field_dict L1972 明文护栏 |
| 采纳 limit_count/open_volume 样本不足降 L4 | ✅ **成立**——符合四铁律 |
| "未改动任何生产代码 / zhb_client 仍含 div_amount 分红 bug" | ❌ **过时/错误**——V17.3.6(1e1233d) 已修复 `_parse_tipinfo` |
| "registry meaning 因提取脚本问题未同步(空)" | ⚠️ **定性不准**——registry 是确定性再生(no-op)，f130 实际=毛利率(push2 命名空间)，非"空/未同步" |
| tx[56]/[85]/[86] "100% 实锤定案" | ⚠️ **表述过度**——字典定级为 L2 机制确认，L1 仍待腾讯官方契约；其给出数值不可复现 |

## 逐条证据

### 1. tipinfo Col[9]：Gemini 反驳成立 ✅
- `field_dict.md` L528：`tdxstat.cfg` Col[9] ≡ push2 f164 ≡ fuyao `pe_ttm`（滚动市盈率）。
- `field_dict.md` L704：`tipinfo.dat` [9] = `div_amount` 业绩预告金额(万元,可负)，L731 决定性证据（3360 样本 2788 负=83.0%，分红恒非负→必为预告净利）。
- 二者确为**两个不同文件**的同名列，Gemini 反驳"审查员把 tdxstat 的 pe_ttm 定义套到 tipinfo"属张冠李戴——**此点 Gemini 正确**。

### 2. zhb_client.py 代码状态：Gemini 描述过时 ❌
- 当前 `core/zhb_client.py:1129` `_parse_tipinfo` 已在 V17.3.6(1e1233d) 校正：
  - `[5]→zt_date_recent`（旧误标 ex_date/除权除息日）
  - `[8]→div_date` 业绩预告日
  - `[9]→div_amount` 业绩预告净利润(万元,可负)
  - `[13]/[14]→unlock_date/unlock_shares_wan`
  - docstring 明确写 "V17.3.6 校正旧误标"。
- Gemini 回复称"代码 L1061 仍写 `[9] div_amount 分红金额(每10股,元)`、`未改动任何生产代码`"——**与权威仓库当前状态不符**。该描述对应 1e1233d 之前的旧代码。
- 推论：Gemini 所审副本（`d:\Google\Antigravity\a-stock-data`，见其命令路径）很可能未含 V17.3.6 提交，或停留在更早 commit。

### 3. f130/f131/f142/f143 系既有 L1：成立 ✅
- `field_dict.md` L6185：`ulist 盘口 f130=PS(TTM) / f142=买二 / f143=卖二 / f221=报告期`，标注 "L1 已定"。
- L1491–1492：f142/f143 跨源数值实证 ≥0.95 多日再确认（强化既有 ✅/L1）。
- 采纳"非本轮新突破"的批评正确。

### 4. f226 维持 ⚠️ 候选+护栏：成立 ✅
- `field_dict.md` L1972：与 `[f225(T-1)-f225(T)]` 池化 r=+0.9414，但精确等式仅 5.7% 命中(27/477) → **"强相关、非精确等式"**，护栏禁止 `f226==rank差分` 精确定案。完全一致。

### 5. limit_count / open_volume 降 L4：成立 ✅
- 仅 8 条样本（4 天×2），未达四铁律（≥18/20 且 ≥3 满命中日），退回 L4 弱候选符合纪律。

### 6. registry "未同步" 定性不准 ⚠️
- `field_registry.json`（`docs/field_verification/field_registry.json`，1806 条）经 V17.3.6 实测为 `extract_registry.py` **确定性再生（no-op，0 增删）**，忠实反映主字典抽取。
- 实测 registry 条目：
  - `code=f130` meaning=**毛利率**（来源 东财-push2 + 东财-ulist239），status=unverified。这实际是 **push2 命名空间的 f130**（field_dict L1572 `f130=毛利率 ⚠️`；L1885 注"ulist/push2 异索引，同号≠同义"），**并非"空/未同步"**。
  - `code=f131` meaning=**（空）**，status=unverified。
- 结论：registry 的 f130 非空而是"毛利率"，反映的是东财跨端点同号异义（push2 f130≠ulist f130），并非"提取脚本 bug 导致未同步"。Gemini 的"registry meaning 留空待同步"表述对 f130 不准、对 f131 部分属实。

### 7. tx[56]/[85]/[86] "100% 实锤定案" 表述过度 ⚠️
- `field_dict.md` L1304–1305 / L3594：tx[85]=收盘参考基准价、**L2 机制确认（L1 待腾讯官方契约）**；tx[86]=收盘集合竞价净未匹配手数、**L2 机制确认（L1 待官方契约）**；tx[56]=Beta 族（L1 已由自算 Beta 实证升格）。
- 语义方向（基准价/带符号净未匹配手数）**成立（L2）**，但"100% 实锤定案"暗示 L1 完全敲定属**过度表述**——字典明确"精确时点 L1 命名仍待腾讯官方契约"。
- 且 L1308/L3594 明记："报告所给 7 只具体数值表与本地快照不符（取自他日、不可复现）"——Gemini 回复中茅台 1252.43→1252.57、农行 7.00→6.91、300788 34.64→34.70 等**精确数值不可复现**，仅作机制示意，不可当作已对撞实证。

## 环境差异（重要）
- Gemini 回复命令路径指向 `d:\Google\Antigravity\a-stock-data`，与权威仓库 `/c/Tencent/WorkBuddy/a-stock-data` 为**两份独立副本**。
- 凡涉及"代码未改/仍含旧 bug"的断言，均应按权威副本（已含 1e1233d）比对，而非 Gemini 所见的 d:\ 副本。

## 处置建议
1. **无需回退或改动生产代码**：V17.3.6 的 `_parse_tipinfo` 校正已落地且通过，Gemini 的"代码仍含 bug"描述属副本滞后，不应据此再改。
2. **可补一处字典消歧脚注**（非必须，待确认）：在 field_dict §3 tipinfo 契约处，可加一句"代码已于 V17.3.6 对齐本契约，旧 `div_amount=每10股分红` 误标已废止"，避免后续审查者再次误读旧代码。
3. **registry f130 跨端点歧义**为已知项（L1885 已注同号异义），无需本次处理。
