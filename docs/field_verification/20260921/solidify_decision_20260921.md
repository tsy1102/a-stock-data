# 固化决策记录 · 20260921（7 映射 vs f88-f95 命名）

> 背景：用户指令「7 个高置信映射固化进 field_dict.md，f88-f95 命名」。
> 本记录固化实际执行结果与偏离原因（诚信留痕）。

## 一、f88-f95 命名（✅ 已固化，黄金锚路径）

经东方财富官方 **F参数表**（黄金锚，与 §12.3.2.3 f62–f87 资金流块同表、编号空间一致、内部自洽）定名：

| 字段 | 命名 | 性质 |
|---|---|---|
| f88 | 当日DDX（大单动向指标） | ✅ 黄金锚 |
| f89 | 当日DDY（大单意愿指标） | ✅ 黄金锚 |
| f90 | 当日DDZ（大单强度指标，z-score 型） | ✅ 黄金锚 |
| f91 | 5日DDX | ✅ 黄金锚 |
| f92 | 5日DDY | ✅ 黄金锚 |
| f93 | 恒空占位（块内保留空位） | ⚠️ 无信息量 |
| f94 | 10日DDX | ✅ 黄金锚 |
| f95 | 10日DDY | ✅ 黄金锚 |

佐证：crack 统计中 f90 跨日 std 异常偏大（±172 区间）恰为 DDZ 的 z-score 宽值域特征；零跨源对撞命中因 DDX 族非外部同名源，依治理范式走黄金锚订正（crack 脚本结论原文即「须走黄金锚」）。改动：field_dict.md §12.3.2.3 + 统计行 + 排除说明、ulist_verify.md 镜像（gen_ulist_subdict.py 重生成，parity OK）、field_registry.json 重抽（extract_registry --check-baseline G1 PASS）。

## 二、7 个「高置信映射」**未固化**（主动拦截，防止字典污染）

`field_crack_summary.md` §一 所列 7 项经核查**不实**，全部未写入 field_dict.md：

| 声称 NEW | 实际证据 | 处置 |
|---|---|---|
| `tx[64]→change_5d` | 底层 `zhb_anchored_crack.md` 标 **L4候选(精确存疑)/待多日复核**；且 `field_dict.md §12.1` 已 L1 定 `tx[64]=股息率(TTM)`（茅台3.98=f126 精确）。真 change_5d=`tx[63]`。 | ❌ 索引/语义均错，未写 |
| `tx[70]→change_10d` | 同上 L4候选；dict 已 L1 定 `tx[70]=20日涨跌幅`；真 change_10d=`tx[69]`。 | ❌ 索引/语义均错 |
| `tx[58]→amount` | 同上 L4候选；dict 已 L1 定 `tx[58]=最新逐笔成交金额`；amount=`tx[37]`/`tx[57]`。 | ❌ 语义错 |
| `push2:f121→change_60d` | dict 已 L1 交叉引用 `f121≡tx[71]`（60日涨跌幅）。 | ⚠️ 字典早已收录，非新 |
| `push2:f122→change_ytd` | dict 已 L1 交叉引用 `f122≡tx[62]`（YTD）。 | ⚠️ 早已收录 |
| `push2:f126→dividend_yield` | dict §12.8/§12.9.1 已载 `f126=股息率`。 | ⚠️ 早已收录 |
| `push2:f180→streak_days` | 命中率仅 0.533（L4候选）；dict 已 ✅ 定 `f180≡ulist:f29` 枚举器（且 push2_statuscode_crack 自身记 `f180=1(恒)`）。 | ❌ 与已定 ✅ 冲突 |

**根因**：§一 摘要与自己的底层证据文件（`zhb_anchored_crack.md` 全部标 L4候选/待多日复核）自相矛盾，属过度声称；且腾讯索引解析存在 off-by-one（change_5d 应为 tx[63] 而非 tx[64]、change_10d 应为 tx[69] 而非 tx[70]）。

**铁律**：凡 L4候选/待多日复核、或与既有 L1 定案冲突者，一律**不写字典**。故 7 项全部拦截。

## 三、本次提交范围

- `docs/field_dict.md`（f88-f95 命名 + 统计/说明）
- `docs/verify/ulist_verify.md`（镜像重生成）
- `docs/field_verification/field_registry.json`（G1 重抽）
- 本记录文件

> 注：field_crack_summary.md §一 的「7 高置信 NEW」表述应据本记录订正，避免后续误读。
