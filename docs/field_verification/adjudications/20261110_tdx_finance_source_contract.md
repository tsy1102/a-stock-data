# TDX 0x0010 财务字段来源契约定案

审阅日期：2026-11-10<br>
审阅范围：`TDX(双命名源)` 中 `get_finance_batch` / `0x0010` 的 9 条未验证路径。

## 结论

依据项目锁定的 ELTDX v3.3.2 上游 `FinanceRecord` 文档，确认以下字段的来源内含义和单位。只更新各自的 `(source, 完整 code path)` 状态和元数据，不创建跨源映射。

| 完整路径 | 定案含义 | 单位 | 上游依据 |
|:---|:---|:---|:---|
| `eps_raw` | 每股收益原始值；接口未区分基本与稀释口径 | 元/股 | `FinanceRecord.eps_raw` |
| `liu_tong_gu_ben_raw_float` | 流通股本原始值 | 万股 | 财务基础信息字段表 |
| `zong_gu_ben_raw_float` | 总股本原始值 | 万股 | 财务基础信息字段表 |
| `zong_zi_chan_raw_float` | 总资产原始值 | 千元 | 财务基础信息字段表 |
| `jing_li_run_raw_float` | 净利润原始值；留存样本对应报告期累计值 | 千元 | 财务基础信息字段表 |
| `circulating_shares` | 流通股本；`liu_tong_gu_ben_raw_float × 10,000` | 股 | 派生字段公式 |
| `total_shares` | 总股本；`zong_gu_ben_raw_float × 10,000` | 股 | 派生字段公式 |
| `total_assets_yuan` | 总资产金额；`zong_zi_chan_raw_float × 1,000` | 元 | 派生字段公式 |
| `net_profit_yuan` | 净利润金额；`jing_li_run_raw_float × 1,000` | 元 | 派生字段公式 |

上游文档将 `finance_batch` 标为 TDX `0x0010`。字段定义见 [ELTDX v3.3.2 METHOD_REFERENCE.md §财务基础信息](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/METHOD_REFERENCE.md) 与 [FIELD_REFERENCE.md §FinanceRecord](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md)。项目依赖固定为 `eltdx==3.3.2`。

## 留存样本交叉检查

对 16 组同日 `raw_tdx.json` / `raw_eltdx.json` 档案，按股票代码配对 320 条股票日记录。比较旧式 TDX `finance_info` 与 ELTDX `finance_batch[]` 的对应原始数值：

| 对照路径 | 配对数 | 完全相同 | 差异 | 对照方式 |
|:---|---:|---:|---:|:---|
| `finance_info.zhongguben` / `finance_batch[].zong_gu_ben_raw_float` | 320 | 320 | 0 | 原值 |
| `finance_info.liutongguben` / `finance_batch[].liu_tong_gu_ben_raw_float` | 320 | 320 | 0 | 原值 |
| `finance_info.eps` / `finance_batch[].eps_raw` | 320 | 320 | 0 | 原值 |
| `finance_info.jinglirun` / `finance_batch[].jing_li_run_raw_float` | 320 | 320 | 0 | 后者 × 10,000 |
| `finance_info.zongzichan` / `finance_batch[].zong_zi_chan_raw_float` | 320 | 320 | 0 | 后者 × 10,000 |

逐日期汇总见 [`20261110_tdx_finance_raw_alias_audit.csv`](20261110_tdx_finance_raw_alias_audit.csv)。这是同一 TDX 协议返回的两种适配/序列化结果，作为数值一致性佐证；不将这些旧键注册为别名，也不作为独立来源证据。

四个派生路径 `circulating_shares`、`total_shares`、`total_assets_yuan`、`net_profit_yuan` 没有单独出现在留存 `finance_batch` 原始序列化对象中。本次只依据上游明确写出的公式定案，没有声称做过派生值的逐条样本对撞。

## 范围限制

- 不推断 `eps_raw` 的基本/稀释子口径。
- `jing_li_run_raw_float` 保持上游较宽的“净利润”表述；不依据字段名进一步推断会计归属。
- 仅核验上述 TDX 来源路径；不变更 `TDX-eltdx(适配层)` 已有的来源内裁决，也不新增 TDX、东财、ZHB 等来源间映射。
- 不改变任何运行时解析、单位换算、数据返回结构或缓存行为。
