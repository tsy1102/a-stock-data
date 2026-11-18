# KPH `get_zttt` `limit_time` 来源内实证（2026-11-19）

## 定案结论

将以下两个精确来源身份定为 `limit_time`（涨停时间），单位为 Unix 秒：

- `市场源(market_sources)::limit_time`
- `开盘红(Levistock适配)::limit_time`

定义范围仅为采集路径 `market_sources.kph_limit_ladder[*].limit_time`。本次不声称该时点必然是首次封板或最后封板；也不定案 `open_time`。两条目标路径都归入 KPH 来源族的现有登记，不因此建立跨源 `mappings` 或宣称新的独立来源。

## 路径核实

1. [`scripts/capture_catalog.py`](../../../scripts/capture_catalog.py) 将 `market_sources.kph_limit_ladder` 登记为 `levistock.get_zttt`，返回路径为 `kph_limit_ladder`，提供方提示为 KPH。
2. [`stock_common/sc_datasource/_pools.py`](../../../stock_common/sc_datasource/_pools.py) 对字典行原样保留；对元组行将位置 `[3]` 映射为 `limit_time`。
3. [`stock_common/sc_datasource/_kph.py`](../../../stock_common/sc_datasource/_kph.py) 将 KPH 历史原始响应位置 `[6]` 映射到 `limit_time`。已验证的 `开盘红::limit_time` 与 KPL `zt_time` 在保留样本中 370/370 逐值相同，且既有裁决已确认单位为 Unix 秒，见 [`20261105_axdata_field_reverse.md`](20261105_axdata_field_reverse.md)。这为本次来源内实证提供已定案参照；不把同一 KPH 来源族重复计为独立来源。
4. 保留起点为 2026-10-15。扫描 21 个有 `raw_market_sources.json` 的保留采集目录，共见 1,225 条含 `limit_time` 的梯队记录；该字段均为可解析的 10 位 Unix 秒。扫描到的 `market_sources` `limit_time` 全部位于 `kph_limit_ladder` 返回行中。

## 交易日与样本资格

来源没有在梯队行中返回 `trade_date`，请求参数不能代替响应日期。逐行按已验证的 Unix 秒值转成东八区日期，再与 `meta.data_date`、`raw_kph.json::trade_date` 对照：

- 1,193/1,225 行的时间戳日期等于采集目录数据日。
- 采集目录 `20261117` 的 32 行请求日为 2026-11-17，但时间戳日期均为 2026-11-16。这 32 行与 2026-11-16 目录中相同股票的梯队记录逐字段一致（32/32），应按 2026-11-16 归日，不作 11 月 17 日样本。
- 按同一股票、同一来源数据日配对后，198 条有直接 KPH 历史记录可比；973 条没有同日 KPH 历史归档，22 条没有同日同股记录。这 1,027 条不进入实证比较，未当作反例或命中。

按以上资格得到 198 组同股同日比较，跨 5 个交易日、187 只不同股票：

| 数据日 | 同股同日配对 | 逐值相同 |
|---|---:|---:|
| 2026-10-16 | 48 | 48 |
| 2026-10-21 | 45 | 45 |
| 2026-10-30 | 44 | 44 |
| 2026-11-06 | 30 | 30 |
| 2026-11-16 | 31 | 31 |
| **合计** | **198** | **198** |

未见可比样本反例。逐行原始比较与排除原因见 [`20261119_kph_get_zttt_limit_time_samples.csv`](20261119_kph_get_zttt_limit_time_samples.csv)，SHA-256：`8b20d20e225f1b650d0b747228d7c6084a70b2b407fd7e618ee73ff1e3fd4395`。

## 辅助对照与结论边界

另将日期合格的梯队时间与 Eastmoney `push2ex.limit_up_pool` 同股同日对照：1,114 组中，1,058 组与 `first_limit_time` 完全相同，1,110 组差值不超过 60 秒；与 `last_limit_time` 完全相同的有 498 组。仍有 55 组不与 first/last 任一值完全相同。因此该辅助对照不能把字段进一步定为“首次封板时间”或“最后封板时间”，也不用于否定 KPH 两接口的 198 组精确同值证据。

`open_time` 是另一个完整字段路径；历史 KPH 对照中该列 370 组均为 0，当前仍无法从恒定占位值确认语义或单位，本裁决不触碰它。原始采集文件未修改。本轮盘前采集因 2026-11-18 目录所需数据已齐全而幂等跳过网络请求；上述研究只使用保留样本与项目内代码。
