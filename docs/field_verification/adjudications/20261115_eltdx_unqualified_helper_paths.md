# ELTDX Helper 未限定字段路径退役核查（2026-11-15）

## 裁决

以下五个注册身份是旧 Helper 清单把不同对象中的叶名合并后留下的无前缀身份。当前序列化器没有把它们作为 `stocks.<ticker>` 记录根键输出。仅将这些精确无前缀身份设为 `disproved` / `retired_legacy_path`，移出未知字段破解队列。

| 旧身份 | 注册表规范路径指向 | 保留期观察到的完整序列化上下文 |
|---|---|---|
| `TDX-eltdx(适配层)::code` | `shortline.code` | `stocks.*.shortline.code`、`stocks.*.quote_snapshot.code`、`stocks.*.finance_batch[].code`、`stocks.*.limit_ladder.code`、`global_helpers.limit_ladder.rows[].code`、`global_helpers.market_stat_880005.code`、`global_helpers.realtime_rank.rows[].raw.code` |
| `TDX-eltdx(适配层)::exchange` | `shortline.exchange` | `stocks.*.shortline.exchange`、`stocks.*.quote_snapshot.exchange`、`stocks.*.finance_batch[].exchange`、`stocks.*.limit_ladder.exchange`、`global_helpers.limit_ladder.rows[].exchange`、`global_helpers.market_stat_880005.exchange`、`global_helpers.realtime_rank.rows[].raw.exchange` |
| `TDX-eltdx(适配层)::full_code` | `shortline.full_code` | `stocks.*.shortline.full_code`、`stocks.*.limit_ladder.full_code`、`global_helpers.limit_ladder.rows[].full_code`、`global_helpers.realtime_rank.rows[].full_code` |
| `TDX-eltdx(适配层)::market_id` | `shortline.market_id` | `stocks.*.shortline.market_id`、`stocks.*.quote_snapshot.market_id`、`stocks.*.finance_batch[].market_id`、`stocks.*.limit_ladder.market_id`、`global_helpers.limit_ladder.rows[].market_id`、`global_helpers.market_stat_880005.market_id`、`global_helpers.realtime_rank.rows[].raw.market_id` |
| `TDX-eltdx(适配层)::pre_close` | `shortline.pre_close` | `stocks.*.shortline.pre_close`、`stocks.*.limit_ladder.pre_close`、`global_helpers.limit_ladder.rows[].pre_close`、`global_helpers.realtime_rank.rows[].pre_close` |

“规范路径指向”只为历史未限定身份提供可追踪的代表路径；表中其他上下文仍按各自完整路径身份维护。本裁决不把多个上下文合并成一个活动字段，不从 `shortline.*` 向其他路径转移字段状态，也不新增跨源或跨路径 `mappings`。裸路径退役不否定相同叶名在各自完整对象中的业务含义。

`volume` 不在本批退役。历史来源表中的 `TradeTick.volume` 指逐笔成交量；当前采集样本观察到的则是 `quote_snapshot.buy_levels[].volume` 和 `sell_levels[].volume`。两者上下文不同，项目当前采集器也未调用 TradeTick 接口，不能把盘口档位量当作逐笔成交量。

## 采集器与序列化路径

`capture_field_probe.py::collect_eltdx()` 委托 `capture_tcp_collectors.py::collect_eltdx()`。采集器为每只股票构造 `rec`，将快照、K 线、财务记录、短线指标分别写入 `quote_snapshot`、`kline_day`、`finance_batch`、`shortline`；`limit_ladder` 由 `global_helpers.limit_ladder.rows` 按股票代码嵌入为独立对象。全局 helper 仍位于顶层 `global_helpers` 下。`_jfy()` 对 dataclass 使用 `dataclasses.asdict()`，保留字段所在对象，不会把属性提升到股票记录根层。现有 `tests/test_capture_field_probe.py` 也检查了快照、短线和财务记录的嵌套输出。

历史来源表 §12.13.10 将 ShortlineIndicator、实时排行、880005 统计、TradeTick 和竞价等多个对象的同名叶字段并列在表中。单个叶名并不等于唯一的 JSON 路径；注册表中的精确身份仍以来源加完整路径为准。

## 保留样本审计与资格边界

只检查 `scripts/capture_retention.py` 规定的 `2026-10-15` 起归档。共有 18 个含 `raw_eltdx.json` 的目标数据日目录；其中 17 个目录的 ELTDX 元数据为 `status=ok`、`n_expected=n_received=20`，共 340 条完整股票记录。`2026-10-19` 的 `n_received=0`，不计入完整样本。所有目录名与 `meta.data_date` 相符。

17 个完整目录的 340 条股票记录中，五个旧叶名作为 `stocks.<ticker>` 直接键的观察数均为 **0**；它们只出现在上表的完整嵌套路径中。逐目录的来源状态、接收数、路径计数及 raw/meta SHA-256 见 [`research/20261115_eltdx_unqualified_helper_path_inventory.csv`](../research/20261115_eltdx_unqualified_helper_path_inventory.csv)，该 CSV 规范 LF SHA-256 为 `329edf510c2917554c2cb852e5e10c23b0be7dc417106296a1bbb35e8b099929`。

ELTDX 的这些归档没有来源级 `as_of_date`。本审计只使用代码与样本确认 JSON 路径结构，不把目录日期当来源实际日期，不把这些记录用于数值碰撞或跨源语义定案。`2026-10-19` 的零接收目录同样不作路径样本。没有读取保留边界前的 raw、ZHB 压缩包或解析缓存；ZHB 与这些 ELTDX 路径身份无关，故未用于本项裁决。

## 注册表处理

五个无前缀身份保留原 `reference_evidence`、完整原状态快照和历史来源身份；状态改为 `disproved`，`status_resolution` 为 `retired_legacy_path`。每条记录附带本裁决文件、样本清单、采集器代码与相关测试作为审计证据。既有完整路径的状态与属性未改，原始归档未回写，采集逻辑和来源路由未改。
