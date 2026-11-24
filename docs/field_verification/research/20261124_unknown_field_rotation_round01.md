# 2026-11-24 未知字段轮动收尾（第 1 轮）

## 范围与结论

- 本轮没有运行采集器；只复核保留期内样本、近期专项审计和公开页面。主报告为 [`exhaustive_goal_round01`](../collision_research_20261124/exploratory/20261124/exhaustive_goal_round01/20261124_collision_report.json)，schema 5、完整性 `complete`，覆盖 25 个交易日键，生成 10 个优先目标、122 个低信息字段和 182 条方法候选。
- 10 个优先目标均完成本轮轮动。`ulist239.f63`、`kpl.raw_columns.col_02` 的相关候选只补充了相关性线索，没有形成可区分语义的公式或字段身份；其余 8 个目标在本轮已有 11/24 专项审计，未发现值得重复执行的新证据入口。
- 122 个低信息字段由 91 个恒值、26 个恒 0、5 个恒空/空白组成。依项目规则，待出现有效变化后再复核；恒值或恒空本身不作为字段无意义的证据。
- 注册表仍有 822 条 `unverified` 精确来源路径。25 日覆盖快照均能按 `(source, 完整 code path)` 找到这些身份；逐条日期资格为：76 条同时有来源日期和候选日期，13 条只有候选侧日期，733 条两侧都没有合格日期，来源日期单侧为 0。候选侧单有日期不能为目标字段建立同日碰撞资格。完整逐路径清单见[822 条身份轮动清单](20261124_unknown_field_rotation_identity_inventory.csv)；89 条至少有一侧日期的样本值与轮动判断见[日期覆盖明细](20261124_unknown_field_rotation_coverage.csv)。全量身份覆盖不等于全量定案；未决字段保持未知。

## 10 个优先目标轮动结果

| 精确路径/运行路径 | 本轮判断 | 后续触发条件 |
|---|---|---|
| `kpl.raw_columns.col_02` | 近期 1,229 个非空值审计已排除“全市场统一两融标记”；本报告新增的 Fuyao 数值相关及 KPH/Push2EX 涨停数字段弱重叠不足以定义该列。仍未知。 | KPL 官方字段定义，或能区分候选的有日期资格样本。 |
| `ulist239.f63` | 保留期 180 条公式审计未命中。与 Fuyao 竞价字段出现新的时序相关，但未发现稳定等值/单位换算；`auction_amount` 旧关系已被拒绝，不能把高相关当成语义。仍未知。 | `f63` 的 Eastmoney 精确字段定义，或可区分资金值与竞价值的同日公式证据。 |
| `st_list.pct_change` | 沿实现追到 `stock_common/sc_datasource/_st_list.py`：Eastmoney `clist/get` 的 `f3` 映射为输出 `pct_change`；沪深主源失败时 Baostock 兜底不提供该值。11/17 留存记录 313 条均为空，且该批归档没有保留实际路由，不能作逐值核对。 | 只有取得带实际提供方/路由来源的非空归档时，才用于来源内核验；不是主字典中已登记的上游字段身份。 |
| `st_list.price` | 同一实现将 Eastmoney `f2` 映射为 `price`，Baostock 兜底同样置空。11/17 留存记录 313 条均为空，具体路由未保留。 | 同上。 |
| `st_list.st_type` | 实现明确由 `name` 派生：名称以 `*` 开头时为 `*ST`，否则为 `ST`。这是项目输出规则，不是独立上游未知字段；路径也不在主字典的逐源注册身份中。 | 无需再作为上游字段破解目标；若要纳入注册表，应先定义项目派生字段身份。 |
| `event_dc.ipo_calendar[].CURRENT_ONEWORD_NUM` | 近期 20 批 400 行审计仍有反例，日期锚不解释该业务字段；没有新证据。仍未知。 | 能区分候选释义的发行记录或官方字段定义。 |
| `event_dc.ipo_calendar[].PE_TTM` | 近期 157 个非空值未匹配官方同日或可比日期的 PE(TTM)，也未匹配 IPO 页面 `AFTER_ISSUE_PE`；只排除了这些具体候选。仍未知。 | Eastmoney 对该 IPO 路径的精确定义/计算基准。 |
| `sina[36]` | 当前报告仍提示覆盖身份未映射；旧的 `sina[36] ↔ push2.f62` 审阅没有形成字段身份。无新日期合格样本或官方映射。 | 精确来源路径映射和日期合格的新证据。 |
| `东财-push2(stock/get)::f131` | 11/24 全保留期审计已排除市现率 TTM 与做市商数假设；未出现新数据。仍未知。 | Eastmoney 对 `f131` 的精确接口定义或新的区分性证据。 |
| `东财-ulist239(np/get)::f145` | 11/24 北交所、创新层、基础层审计已排除与官方证券层级码等义；未出现新数据。仍未知。 | Eastmoney 对 `f145` 的精确接口定义或新的区分性证据。 |

## 本轮新增候选审阅

以下 7 条是报告中尚未审阅的候选身份，均已单独审阅为 `insufficient_evidence`。该结论只表示关系证据不足，不表示两字段已证伪，也不改变两端字段状态。

| 候选关系 | 可复核结果 | 处理 |
|---|---|---|
| `ulist239.f63` ↔ `fuyao.auction_final.auction_yesterday_ratio_pct` | 179 对；Pearson 0.3484、Spearman 0.7214；每股时序中位绝对 Pearson 0.7989。无直接相等或稳定换算证据。 | `insufficient_evidence` |
| `ulist239.f63` ↔ `fuyao.auction_final.auction_volume` | 179 对；Pearson 0.4173、Spearman 0.8218；每股时序中位绝对 Pearson 0.8887。相关不等于同义，且原始量纲不同。 | `insufficient_evidence` |
| `ulist239.f63` ↔ `fuyao.auction_final.auction_turnover_pct` | 179 对；每股时序中位绝对 Pearson 0.8890、20 股同向。未出现精确匹配或稳定换算。 | `insufficient_evidence` |
| `kpl.raw_columns.col_02` ↔ `fuyao.auction_final.auction_volume` | 报告 13 对；Pearson 0.6169、Spearman 0.6831。样本量小，二值列与数值规模共变不能识别字段含义。 | `insufficient_evidence` |
| `kpl.raw_columns.col_02` ↔ `fuyao.auction_final.auction_amount` | 报告 13 对；Pearson 0.5816、Spearman 0.7319。没有公式/身份映射证据。 | `insufficient_evidence` |
| `kpl.raw_columns.col_02` ↔ `kph.limit_count` | 103 对、3 日，精确重叠率 44.66%，0 日达到阈值。碰撞报告的 `kph.limit_count` 是短别名；本项目留存的 KPH 样本对应 `HisDaBanList`，而未知注册路径 `开盘红(Levistock适配)::limit_count` 对应 `GetPlateInfo_w38`。端点不同，不能把该弱重叠解释成目标字段映射；KPL 与 KPH 也保持不同来源身份。 | `insufficient_evidence` |
| `kpl.raw_columns.col_02` ↔ `push2ex.limit_count` | 1,186 对、21 日，精确重叠率 43.42%，0 日达到阈值。弱重叠不足以确认字段身份。 | `insufficient_evidence` |

Fuyao 竞价终态的 19 个保留批次有独立批次日期见证，以上 Fuyao 样本仅使用该见证覆盖的批次。该日期资格提升了相关性比较的可用性，但没有把相关性提升为语义证据。

## KPH `HisDaBanList` `limit_tag` / `limit_count` 路径复核

- 项目当前 `_kph.py::get_kph_limit_up_history()` 使用 `HisDaBanList/HisHomeDingPan`；其 `row[9]`、`row[10]` 分别进入 `开盘红::limit_tag/limit_count`。此路径不同于 Levistock `get_his_limit_resumption()` 的 `GetPlateInfo_w38/HisLimitResumption`，因此样本不能用于定案 `开盘红(Levistock适配)::limit_tag/limit_count`。
- 21 个非空批次共 885 条观测，按来源日期和证券代码去重后为 723 条（551 只证券、17 个来源数据日）；来源日期按响应请求和逐行身份验证，不使用采集目录日期替代。162 条重复记录完全一致。
- `首板=1`、`N连板=N`、`N天M板=M` 与 `limit_count` 在 723/723 条唯一记录中吻合，0 反例。该结果作为现有 KPH `HisDaBanList` 来源记录的追加实证；不把它包装成官方字段契约，也不外推 `N天` 窗口算法。
- 这批数据只补强已验证的 `开盘红` 当前适配路径，作为追加实证记录，不改变字段释义；不合并到 `get_zttt` 梯队的 `市场源(market_sources)::limit_count`，不映射到开盘啦 KPL，也不外推到 Levistock 的另一端点。详见[路径复核记录](20261124_kph_his_daban_list_tag_count_audit.md)、[逐行审计](20261124_kph_history_limit_count_audit.csv)与[输入清单](20261124_kph_history_limit_count_manifest.csv)。

## KPH `sjzt` / `sjdt` 旁支核验

- 精确注册身份分别是 `开盘红(Levistock适配)::sjzt/sjdt` 与聚合路径 `市场源(market_sources)::sjzt/sjdt`；只研究开盘红路径，不把 KPH 与开盘啦 KPL 合并。
- Levistock 0.1.8 的第三方封装把 KPH 响应 `SJZT/SJDT` 映射为 `sjzt/sjdt`，并称其为非 ST 实际涨停/跌停数。该封装不是开盘红官方字段契约。
- 两个留存请求日样本中均满足 `zt = sjzt + stzt`、`dt = sjdt + stdt`；Eastmoney `limit_up_pool` 行数分别与 KPH `sjzt` 82/82、37/37 相同，且两批列表无 ST 简称。这是有价值的交叉线索，但 KPH 元数据为 `request_parameter_match`、`eligible_for_date_comparison=false`，Eastmoney 池响应也没有可独立确认的来源日期；因此该比较不作为正式同日裁决证据。
- 今天查阅的[开盘红官网](https://www.kaipanhong.com/)、[官方联系页](https://www.kaipanhong.com/contact)可确认产品/运营主体，但公开页面未提供这两个 API 字段的精确定义。`sjzt/sjdt` 暂不更新主字典；`market_sources` 聚合身份也不继承 KPH 结论。
- Push2EX `yesterday_limit_pool` 保留期 4 次响应均为空，不含字段值或来源日期；停止从空响应重复推断。

## 收尾条件

本轮已完成 822 条未知路径的身份/日期资格轮动、碰撞报告给出的 10 个优先目标、122 个低信息字段和 184 条候选身份审阅（原已审阅 177 条，本次补完 7 条）。KPH 当前 `HisDaBanList` 路径的核验只为既有已验证字段追加来源内样本，不改变 822 条未知身份中的状态；Levistock 的另一端点字段仍按其自身证据保持未知。剩余日期可用路径没有新增可区分语义的候选；13 条仅候选侧有日期、733 条两侧无日期，当前不能形成目标字段的合格同日碰撞。重复运行相同材料不会增加证据；所有未知精确路径均已轮动，本轮目标据此收尾。只有新非空样本、目标侧明确来源日期、精确接口字段定义或可区分旧候选的新证据出现时，再重开对应字段。
