# AxData 全字段逆向登记与字典定案（2026-11-05）

## 结论先行

可以从 AxData 的接口目录、路由入口和解析代码逆向确认其输出字段，并与本项目逐源字典比对。本轮已将 257 个接口、3,343 个字段出现项逐项登记；每项带有接口、输出字段定义、上游代码入口，以及按本项目当前完整来源路径生成的候选匹配。机器对照表见 [`axdata_field_reverse_register_20261105.json`](../../axdata_field_reverse_register_20261105.json)。

逆向能证明 AxData **输出了什么、由哪个接口处理、项目字典里有哪些同名或同义词候选**。字段名相同本身不能证明它与另一源的原始字段等价。全量清单中，1,550 个字段出现项找到至少一个词面候选，共 6,906 个候选链接；这些均按 E0 处理，不自动写入主字典。

## 覆盖范围与版本边界

| 项目 | 核查结果 |
|---|---|
| GitHub 源码 | `electkismet/AxData`，HEAD `f8ce3cee989717d79c7ad8f73b42f93c6dbd87e8`；本机检出的 HEAD 与远端 HEAD 一致 |
| 本项目运行时依赖 | `axdata==0.1.4` |
| 上游接口字段 | 256 个 source request 接口、3,334 个字段出现项；另有 Web UI 展示的 1 个 stream 项、9 个字段；合计 257 / 3,343 |
| 字典比对基数 | `field_registry.json::source_fields` 当前 2,560 个 `(source, 完整路径)` 身份 |
| 字典候选覆盖 | 1,550 / 3,343 个字段出现项命中当前字典的 `code`、完整 `path`、路径叶名或 `canonical`；6,906 条候选关系 |
| 代码入口覆盖 | 3,334 个请求接口字段可回到上游接口代码入口；9 个 stream 字段只有 Web UI 目录定义，没有对应的请求适配器代码入口 |

AxData 上游当前源码与项目安装的 0.1.4 在实现文件上并非逐字相同；已比对 KPH catalog/parser 与 TDX interface/dispatch/derived-row/request 方法文件，内容哈希均不同。另一方面，256 个请求接口的 ID 和 3,334 个输出字段名与本项目安装版目录逐项一致。全量登记因此使用上游当前源码的接口代码入口，并明确记录它只是字段到接口的逆向；项目实际调用的 KPH、TDX 解析路径则另外按已安装的 0.1.4 源码复核。

本轮没有为其余未调用的 AxData 接口请求网络数据。它们在登记表中保留输出字段、接口路由入口和本项目字典候选，候选不升格为语义定案。9 个 stream 字段也单独标记为目录项。

## 本项目实际调用的 AxData 路径

1. `scripts/capture_verified_collectors.py` 请求 `kph_limit_up_history`，将 AxData 归一化结果写入 `raw_kph.json`。项目使用的 0.1.4 解析器将 KPH 返回数组的位置转为 14 个业务字段。
2. `stock_common/sc_datasource/_quotes.py` 请求 `stock_shortline_indicators_tdx`，并传入本地 ZHB 统计 ZIP 路径。该结果由 TDX 实时行情、TDX 财务数据、ZHB 统计行和计算公式共同组成。

## KPH 涨停历史：14 个业务字段逐项核验

样本只取保留范围内的 8 个交易日；逐日按 KPH/KPL JSON 内的 `trade_date` 和股票代码配对，共 370 组同日同股。目录日期不是配对依据。AxData 0.1.4 解析器位于 `axdata_core/adapters/kph/request.py::_parse_limit_history_row`，将数组位置转成下表输出；KPL 原始行顺序由 `stock_common/sc_kpl.py` 解析器记录。

| AxData 输出字段 | AxData 原始行位置 | KPL 对照字段/原始位置 | 样本结果 | 字典结论 |
|---|---:|---|---:|---|
| `limit_time` | `[6]` | `zt_time` / `[4]` | 370/370 逐值一致 | 保持已验证，更新为 8 日证据 |
| `open_time` | `[7]` | 无可用对照 | 370/370 均为 0 | 登记为未验证；样本没有非零值，暂不能验证含义或单位 |
| `seal_amount` | `[8]` | `seal_amount` / `[6]` | 370/370 逐值一致 | 保持已验证；单位仍未确认 |
| `seal_money` | `[23]` | `max_seal` / `[7]` | 370/370 逐值一致 | 保持已验证；单位元 |
| `limit_tag` | `[9]` | KPL 原始 `[18]` | KPL 33 条非空值中 33/33 一致 | 定案为连板标签；注明仅覆盖有值样本 |
| `limit_count` | `[10]` | 从 KPL 原始 `[18]` 的“`N天M板`”解析 `M` | 30/30 个可解析值一致 | 定案为连板数，单位板 |
| `themes` | `[11]` | `sector` / `[12]` | 完整列表 360/370 一致；369/370 至少一项重合 | 定案为题材标签列表；保留来源标签口径差异 |
| `reason` | `[16]` | `reason` / `[5]` | 367/370 逐字一致 | 定案为涨停原因，映射到 `limit_up_reason`；3 组不同文本保留来源原值 |
| `net_inflow` | `[12]` | `main_inflow` / `[8]` | 370/370 逐值一致 | 保持已验证，更新为 8 日证据 |
| `turnover` | `[13]` | `amount` / `[11]` | 370/370 逐值一致 | 保持已验证，更新为 8 日证据 |
| `turnover_rate` | `[14]` | `turnover_real` / `[14]` | 370/370 逐值一致 | 保持已验证，更新为 8 日证据 |
| `market_cap` | `[15]` | KPL“实际流通” / `[13]` | 369/370 逐值一致 | 定案为流通市值，映射到 `float_market_value`；1 组相差约 0.8025%，不将其解释成四舍五入 |
| `industry_id` | `[26]` | `sector_code` / `[19]` | 367/370 逐值一致 | 定案为行业分类 ID；3 组代码差异保留来源原值，不承诺跨源代码完全可替换 |
| `industry_limit_up_count` | `[27]` | KPL 原始 `[20]` | 320/370 一致；差异包含 `+15`、`-27` 等 | 登记为未验证；计数口径/分类范围尚未收敛 |

8 个日期的配对数量依次为：2026-10-16 50、10-19 40、10-21 45、10-23 50、10-28 50、10-30 44、11-02 50、11-03 41。所有样本均不早于 2026-10-15。`market_cap` 的 0.8025% 差值明显大于普通显示舍入，已保留为差异；`industry_id` 的 3 组分类代码不一致也没有被当作精确别名。

既有 6 个 KPH 字段继续验证通过，并将原有 2—3 日证据扩展为 8 日证据。另将 `limit_tag`、`limit_count`、`themes`、`reason`、`market_cap`、`industry_id` 纳入 E3 语义定案，精确值差异和稀疏覆盖均写入字段含义/证据说明。`open_time` 与 `industry_limit_up_count` 保留在未知字段队列。

## TDX 短线指标：34 个输出字段的输入与计算路径

实际路径为 `stock_shortline_indicators_tdx` → TDX `request_stock_auction_indicators()` → `normalize_auction_indicator_row()`。下面 34 个字段均已在全量 JSON 中逐项列出，并按 0.1.4 运行时代码还原：

| 字段类别 | AxData 输出字段 | 逆向来源/计算 |
|---|---|---|
| 标识与日期（5） | `instrument_id`, `symbol`, `tdx_code`, `exchange`, `stats_date` | 证券代码转换/规范化快照；统计日期取对齐后的 `stat2_row` 或 `stat_row` |
| TDX 快照字段（6） | `open_price`, `pre_close`, `open_change_pct`, `open_amount`, `opening_rush`, `seal_amount` | 分别取规范化快照的开盘价、昨收、开盘涨幅、开盘成交额、竞价抢筹值、锁定金额 |
| 竞价派生值（6） | `open_volume_hand`, `open_volume_ratio`, `open_turnover_z`, `open_prev_amount_ratio`, `auction_prev_volume_ratio`, `open_prev_seal_ratio` | 由开盘成交额/开盘价、近期日线、自由流通股数、前日成交额/封单额及换算后的比率公式计算 |
| 历史成交与封单统计（5） | `prev_amount`, `prev_seal_amount`, `prev2_seal_amount`, `prev_open_volume_hand`, `prev_open_amount` | 取对齐后的 ZHB `stat2_row` 字段；金额类十万元/万元口径按代码转换为元，集合竞价成交量保持手 |
| 股本与市值（4） | `float_shares`, `float_market_value`, `free_float_shares`, `free_float_market_value` | 总流通股取 TDX finance；自由流通股取 ZHB `free_float_shares_10k`；市值由股数乘最新价计算 |
| 封单比值（3） | `seal_to_amount_ratio`, `seal_to_float_ratio`, `seal_prev_ratio` | 由快照锁定金额分别与当日成交额、自由流通市值、前日封单额相除 |
| 涨停统计（5） | `limit_stat_days`, `limit_up_count_in_stat_days`, `limit_board_text`, `limit_up_streak_days`, `year_limit_up_days` | 取 ZHB 统计行；`limit_board_text` 由统计天数和涨停数格式化 |

本项目字典中的 `TDX-eltdx(适配层)::shortline.*` 已覆盖这些短线字段。AxData 该路由复用 TDX 与本地 ZHB 输入，属于派生层；不增加一个重复的独立来源锚。保留样本中 239 组同股输出对照支持 `open_price`、`pre_close`、`open_change_pct`、`float_shares`、`float_market_value`、`seal_amount` 等字段逐值一致；若干竞价比值受统计日期、缓存日期或采集时点影响，`opening_rush` 在 ELTDX 对照样本中没有对应值。因此本轮不以 AxData/ELTDX 同源重复值新增 E3 字段映射。

## 主字典写回结果

- `source_fields` 新增完整 KPH 业务输出路径 8 条；加上既有 6 条，`开盘红` 的 14 个业务字段均有登记。
- 6 条新增 E3：`limit_tag`、`limit_count`、`themes`、`reason`、`market_cap`、`industry_id`。其中 `market_cap` 归入 `float_market_value`，`reason` 归入 `limit_up_reason`，避免与本项目其他来源的总市值和泛化 `reason` 混用。
- 2 条保留未验证：`open_time`、`industry_limit_up_count`。
- 既有 6 条 KPH E3 证据更新为上述 8 个交易日；`seal_amount` 单位仍保持未知。
- AxData 的 `trade_date`、`instrument_id`、`symbol`、`exchange`、`name` 是接口标识/关联字段，已列入全量接口登记，不作为本轮 14 个业务指标定案对象。

本次修改只登记字段身份、语义、单位和证据，不改采集路由、缓存键、事件锁或网络请求。没有发起 AxData、KPH、KPL 的新联网采集请求。
