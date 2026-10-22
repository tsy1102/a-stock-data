# KPH 与 KPL 涨停明细核验

> **封单映射更正（2026-10-22）**：下方 2026-09-29/30 表格记录的是当时的解释，其中 `seal_amount` / `seal_money` 与 `max_seal` / `seal_amount` 两组关系发生了对调。三日原始样本、原因、修正后的定义和证据见[纠错定案记录](../field_verification/adjudications/20261022_kph_kpl_seal_mapping_correction.md)；当前主字典以该记录和 `field_registry.json` 为准。

核验日期：2026-10-10
证据来源：`docs/axdata_field_reconciliation_20261010.md` 的双交易日实测、AxData 0.1.4 本地接口目录、项目归档的 KPL 原始采集文件。

## 来源身份和采集边界

- `kph_limit_up_history` 是 AxData 目录中的历史接口，目录将提供方标为 KPH/开盘红。AxData 在本项目中只是调用框架；当前没有证据确认 KPH 上游服务自身的 GitHub 仓库。
- 项目 KPL 明细由 `stock_common.get_kpl_limit_up_detail()` 提供。采集器将原有响应从混合 `market_sources` 输出中另存为 `raw_kpl.json`，不重复请求。
- KPH 明细单独保存为 `raw_kph.json`。每个交易日最多发出一次 AxData 历史批量请求，`persist=False`，不重试。若同次采集的 KPH 天梯返回 403、429、封禁或限流标志，则跳过历史请求。
- 本功能不调用 Eastmoney push2，也不要求使用 `--all`。

## 双交易日逐股证据（历史记录；封单关系已被纠正）

| 交易日 | KPH 返回 | 项目 KPL 明细 | 重叠证券 | 六字段逐值相同 | KPH 多出 | KPL 多出 |
|---|---:|---:|---:|---:|---:|---:|
| 2026-09-29 | 50 | 47 | 45 | 45/45 × 6 | 5 | 2 |
| 2026-09-30 | 47 | 40 | 40 | 40/40 × 6 | 7 | 0 |

六个字段在 85 个重叠证券样本上逐项精确相同。KPH 两日行数都少于市场涨停总数 57、52，故它是 KPL 明细的补充数据，不能代替完整涨停名单。

| KPH 原始路径 | KPL 原始路径 | 规范含义 | 单位/约束 |
|---|---|---|---|
| `limit_time` | `zt_time` | 涨停时间 | Unix 秒时间戳 |
| `seal_amount` | `max_seal` | 封单量 | 两日值精确匹配；计量单位未由上游契约确认 |
| `seal_money` | `seal_amount` | 封单金额 | 元 |
| `net_inflow` | `main_inflow` | 主力净流入 | 元 |
| `turnover` | `amount` | 成交额 | 元 |
| `turnover_rate` | `turnover_real` | 实际换手率 | 百分比数值，例如 `0.37` 表示 `0.37%` |

这些映射登记为来源专属路径，不把同名或相似名称当作语义证据。除表中六项外，采集器可保留 KPH/KPL 响应中的其他数值叶字段以供后续研究；它们暂不进入 verified 字典记录。

## 日期、证券身份与碰撞约束

- KPL 的 `trade_date` 从每条记录的 `zt_time` 时间戳按上海时区推导；若一个响应无法确认唯一交易日，采集器不写入可碰撞的逐股记录。
- AxData KPH 历史接口要求请求日早于自然日“今天”。采集器按 ZHB 补充交易日历选择不晚于采集目标日、且严格早于自然今天的最近有效交易日；实际日期写入 raw 顶层 `trade_date` 和 `meta.source_as_of_dates.kph`。采集目录日期仍记录在 `capture_date`。
- KPH 曾将 `920779`/`920202` 报为 `.SH`/`SSE`。采集器以六位数值代码作为股票键，不将交易所字段并入碰撞值；异常原始标识写入 `identity_observations` 并产生告警，等待上游修正后再确认交易所归属。
- 交易日和来源族分别记录为 `kph` 与 `kpl`，碰撞时按各自实际交易日对齐；六组已核实对应关系进入 registry 映射，后续不再作为未知字段重复破解。

## 延后事项

KPH 涨停明细覆盖率和交易所标识仍需继续观察；KPH 跌停明细、1% 涨跌分布、市场情绪、封单量单位以及其余 AxData 接口仍按后续报告中的候选等级验证。本核验不把这些候选升级为主字典字段。
