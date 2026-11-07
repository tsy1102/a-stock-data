# AxData TDX 短线接口历史字段定案（2026-11-07）

## 结论

对项目实际调用的 AxData `stock_shortline_indicators_tdx` 接口，按完整输出路径 `AxData::data.<field>` 登记并确认 34 个来源内字段的公开语义与单位。主字典同步这 34 条逐源身份；`float_shares`、`free_float_shares` 等通过 `field_matrix` 接入对应语义字段。

该登记确认的是 **AxData 接口怎样命名和定义自己的输出**。来源谱系仍把 AxData 标为 TDX 框架适配层、独立性未确认、不可作独立锚；本次不改来源独立性，也不把同族相等值作为独立来源证据。

## 样本与接口证据

- 官方接口文档将该接口归于 `axdata.source.tdx_external` / 通达信，说明其会请求实时快照、日 K、财务快照，并结合 TDX 统计缓存计算一行短线指标；字段定义、单位和公式见[公开文档快照](public_web/20261107_axdata_shortline_interface.md)及[AxData 在线接口页](https://electkismet.github.io/AxData/interfaces/stock_shortline_indicators_tdx.html)。
- 项目依赖及运行环境均为 `axdata==0.1.4`。生产采集器经 `stock_common.get_shortline_indicators_result` 调用接口，将响应字段原样置于 `stocks[code].data`；这与候选身份 `axdata.data.<field>` 一致。
- 保留区间内共有 14 个采集日期目录、280 条股票槽位记录；13 个日期有有效 AxData 数据，覆盖 259 条非空记录。34 个字段均在样本中有非空值；常见字段覆盖 258–259 条记录，稀疏的封单历史字段覆盖 15 条，统计天数与连板文字字段覆盖 27–46 条。稀疏只限制数值复核量，不影响官方文档对该接口输出字段的定义。
- AxData 的 `stats_date` 是统计分母所用日期。多数有效样本记录为采集日前一交易日，故只解释其历史统计基准；不把它误作实时行情、开盘价或 `pre_close` 的共同来源日期。

## 对照结果与裁决

历史碰撞报告：[`historical_recrack_second_20261107`](../20261107/historical_recrack_second_20261107/20261107_collision_report.md)，JSON SHA-256：`e451e84163dba41d8e9da7f5a47b3d9ad69eac705938baae1b236b4c2b540c5f`。该报告覆盖 2026-10-15 至 2026-11-06 的 16 个交易日窗口；原始目录缺 2026-10-22 和 2026-11-06，实际使用 2026-10-15 至 2026-11-05 留存样本。全报告 L1=0、L1-C=0、L4=58、方法候选 5,635；本次在完整历史和官方契约基础上人工复核其中 8 个高价值关系。

| 候选关系 | 历史观测 | 裁决 |
|:--|:--|:--|
| `data.pre_close` ↔ FTShare REST `prev_close` | 10 个数据日、199 组，199/199 精确相等；AxData 文档定义昨收价，FTShare 契约定义前收盘价 | 接受语义映射；AxData 来源身份登记到 `pre_close`。FTShare 底层来源独立性仍未确认，不把这一关系升级为独立源证据 |
| `data.open_price` ↔ FTShare REST `open` | 10 个数据日、199 组，199/199 精确相等；双方契约均定义开盘价 | 接受语义映射；AxData 来源身份登记到 `open_price` |
| `data.float_shares` ↔ FTShare REST `float_a_shares` | 10 个数据日、199 组；10 组精确，179/199 组差值不超过 100 股，中位绝对差 36.1875 股，最大 9,223 股，最大相对差 `7.56e-7` | 接受为普通流通股的同一语义类别，允许来源精度/更新时间带来的微小偏差；**不**登记逐值严格映射、不放宽 L1 精确命中门槛。AxData 该字段另由官方接口定义直接定案 |
| `data.float_shares` ↔ FTShare REST `shares` | `shares` 的契约语义为总股本；199 组中位绝对差 1,251,375 股，最大差约 307.4 亿股 | 拒绝：普通流通股不等于总股本 |
| `data.free_float_shares` ↔ FTShare REST `float_a_shares` | 199 组中位绝对差约 1.398 亿股；AxData 文档指自由流通 Z 口径，FTShare 契约指 A 股流通股数 | 拒绝：口径不同 |
| `data.free_float_shares` ↔ FTShare REST `shares` | 199 组中位绝对差约 2.354 亿股；后者是总股本 | 拒绝：口径不同 |
| `data.free_float_shares` ↔ FTShare REST `ts_millis` | 报告出现每股时间序列相关性，但一侧是股数、一侧是毫秒 Unix 时间戳 | 拒绝：字段类型与量纲不同，相关性属时序巧合 |
| `data.open_price` ↔ FTShare REST `prev_close` | 10 个数据日、199 组；仅 13 组精确，中位绝对差 0.10 元，最大 19.24 元 | 拒绝：开盘价与前收盘价是不同字段；高相关不能代替语义相同 |

另外，AxData 与本项目 ELTDX `shortline` 同属 TDX 族的路径一致性检查，在 199 组中观察到 `float_shares`、`free_float_shares`、两种市值、`pre_close`、`open_price`、`seal_amount` 及封单比率均 199/199 精确相等。这支持本地适配路径和口径一致，但不作独立来源证据。`open_amount`、`open_volume_hand`、`open_volume_ratio`、`open_turnover_z` 有轻微差异或精确重合不足；依照接口各自定义登记语义，不据此强行合并逐值关系。

8 条候选审阅决定已通过项目审阅工具写入 `collision_candidate_reviews.json`；3 条接受语义关系进入定案，5 条拒绝错误同义候选。近似差值仅作为旁证记录，未改 L1/L1-C 阈值。

## 注册表与时间分类

- 新增 34 个 `AxData::data.<field>` E3 来源字段身份，语义、单位、样本证据见 `field_registry.json` 和本文件；字段矩阵加入对应的 `AxData` 来源。
- 34 个路径都有逐源时间分类：证券标识用 `static_reference`，统计分母日期用 `periodic_or_event`，股数用 `slow_changing`，当日行情/开盘统计用 `daily_market`，实时封单及其派生比率用 `intraday_sensitive`。
- `daily_market` / `intraday_sensitive` 分类描述字段变化频率，不证明原始 AxData 快照具备可核验的逐字段来源日期。除 `stats_date` 所描述的历史分母日期外，不从采集目录日期推造 AxData 字段日期，也不因此让 AxData 成为碰撞锚。

## 留存边界

这轮覆盖的是项目实际调用的一个 TDX 短线接口，不把结论推广到 AxData 其余 256 个接口。报告中剩余的 5,635 个候选不等于已人工审阅关系；完整队列仍按候选报告和人工审阅台账跟踪。`2026-11-06` 没有原始采集目录，因此未声称覆盖该日。
