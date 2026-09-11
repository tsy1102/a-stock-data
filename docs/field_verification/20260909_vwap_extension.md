# VWAP 功能扩展实现与验证报告（2026-09-09）

> 承接 Round 13（tx[56] Beta 第四源锚）与 (a)/(b) 通用对撞器落地，本报告完成 **VWAP 指标的工程化扩展**：
> 计算逻辑补充、边界情况处理、独立锚重算对撞验证。数据来源：通达信 TDX K线（独立第四源）。

## 1. 背景与目标

`computed_collider.py` 在 (b) 阶段已注册 `("tdx_kline","beta")`，但 `("tdx_kline","vwap")` 因 K线缓存仅含 `closes` 而暂未启用。
本次目标：
1. 从 TDX K线原始文件提取**成交额/成交量（含原生与换算值）** 补全缓存；
2. 实现 VWAP 指标并在对撞器注册，覆盖所有边界；
3. 对 `tx[51]`（均价）与 `tx[85]`（价格类候选）做独立锚重算验证。

## 2. 计算逻辑补充

### 2.1 缓存补全
新增 `raw_tdx_kline_full.json`（替代仅含 closes 的 `raw_tdx_kline_beta.json` 作为对撞器默认缓存），每 code 含：
`dates/opens/highs/lows/closes/amounts/volumes/rawvolumes/rawamounts/unit/n_kept`。
来源：重新解析 `mcp-tdx-connector-tdx_kline-*.txt`（21 个文件，去重后 20 code，含 000300/000985 基准）。
实测每行结构含 `Amount`(元, 终值) / `Volume`(手, 按 Unit 换算) / `RawAmount` / `RawVolume`(未换算原生值)。

### 2.2 VWAP 公式与单位推导
逐股取**最新一根成交量>0 的 bar**，均价（元/股）：

```
VWAP = RawAmount / RawVolume              # 优先：原生值直接给出 元/股
     = Amount / (Volume × 100)            # 回退：Volume 单位=手, 1手=100股 → 元/股 = 元/(手×100)
```

单位推导依据（600519 实测）：`Amount/Volume = 131334`，而 `close ≈ 1309`，二者比值 ≈100。
说明 `Amount/Volume` 量纲为**元/手**，故 `元/股 = 元/(手×100)`；而 `RawAmount/RawVolume` 原生比值恰好为 元/股（与 tx[51] 残差 <0.005，见 §3）。
**结论**：优先采用 `RawAmount/RawVolume`，仅在原生值为 0 时回退 `Amount/(Volume×100)`。

## 3. 边界情况处理（已实现于 `_indicator_vwap` + `_latest_nonempty_idx`）

| 边界 | 处理 | 验证 |
|---|---|---|
| 盘前空量 bar（Volume=0） | `_latest_nonempty_idx` 从末尾向前跳过 Volume=0 根，取最新非空 bar | 全样本末根 20260909 为空量，正确回退至 20260908 |
| 原生 RawVolume=0 但 Volume>0 | 回退 `Amount/(Volume×100)` | 实证路径；本案原生值均>0，走优先分支 |
| 原生/换算值缺失或非数值 | `try/except` → 返回 `None`，该股票不参与对撞 | — |
| 个股不在 K线缓存 | 返回 `None`，对撞循环 `continue` | 北交所 920118/920508 等未取 K线，自动跳过 |
| 指数基准对 VWAP 无意义 | `benchmark` 参数占位忽略；结果 `benchmark='-'` | 避免误用基准 |
| 有效样本 < 5 | 返回 `ok=False` 并标注原因 | — |

## 4. 验证结果（系统 Python 3.12，`computed_collider.py`）

### 4.1 tx[51] 均价 —— 第四源精确定案 L1
```
n=18  Pearson=1.0000  Spearman=0.9995  R²=1.0000
slope=1.0000  intercept=0.0003  loo_min_pearson=1.0000  residual_max=0.0049
```
逐股吻合至 3 位小数（如 600519 tx51=1313.340 / VWAP=1313.345）。
依对撞铁律"同源精确数值命中"例外路径（独立第四源重算 Pearson=1.0、slope=1.0、残差<0.005），**tx[51]=成交额÷成交量 均价 升 L1 定案**，与既有内部 L1（20/20 命中）互为独立佐证。

### 4.2 tx[85] 价格类 —— VWAP 指标正确判别"非均价"
```
n=18  Pearson=1.0000  Spearman=0.9979  R²=1.0000
slope=0.9976  intercept=0.0531  residual_max=0.5365
```
Pearson=1.0 仅为跨股价格共变的伪相关（所有 OHLC/VWAP 派生量彼此 Pearson 均≈1，无法区分）；
**斜率 0.998≠1、截距 0.053、残差 max 0.537** 表明 tx[85] **不是**每日均价。
残差轮廓（对 close 残差 max 0.92、对 vwap 残差 max 3.12，均非零）吻合"近似当前价/最新价"特征——
单快照无法用已结算 K线收盘价精确复现（快照时刻价 ≠ 结算 close）。
→ **维持 L3 价格类候选强**；与 Round 12 TDX MCP 均价锚（HQInfo.Average）证伪结论一致。
此即 VWAP 扩展的判别价值：不只是"命中即定案"，也能"偏离即排除"。

### 4.3 tx[56] Beta —— 一致性复验
```
n=18  Pearson=0.9918  Spearman=0.9876  R²=0.9836  residual_max=0.1606
```
与 Round 13（Pearson=0.9918、R²=0.9836）完全一致；缓存窗口因本次重提取平移 1 日仍稳定，
证明 Beta 锚对数据窗口不敏感（留一法 min 0.988）。

## 5. 与对撞铁律的一致性
- tx[51]：独立重算**精确数值命中**（slope=1.000、残差<0.005）→ 可定 L1（铁律"精确对撞"路径）。
- tx[85]/tx[56]：仅相关量（slope≠1 或残差大）→ 仅身份确认级，不定案（铁律#5）。
- VWAP 指标现与 Beta 并列为一等方法，新增指标只需在 `INDICATORS` 注册 `(anchor_source, name)` 并在 `FIELD_INDICATOR` 映射字段号。

## 6. 复现命令
```bash
python scripts/computed_collider.py --field 51   # VWAP 验证 (期望 Pearson=1.0)
python scripts/computed_collider.py --field 85   # tx[85] 是否均价判别
python scripts/computed_collider.py --field 56   # Beta 一致性复验
python scripts/field_meta.py                     # 字段身份注册表自检
```

## 7. 交付文件
- `scripts/computed_collider.py`（VWAP 指标 + 边界 + 注册）
- `scripts/field_meta.py`（tx[51]/tx[85] 元数据升级）
- `docs/field_verification/raw_tdx_kline_full.json`（含 amount/volume 的 K线缓存）
- `docs/field_dict.md`（tx[51] L1 第四源注记、tx[85] 非均价注记）

> 注：以上为字段语义破解工程化能力交付，非投资建议。
