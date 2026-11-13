# ELTDX `limit_ladder` 日期字段来源契约定案

复核日期：2026-11-14  
来源身份：`TDX-eltdx(适配层)`  
保留样本起点：2026-10-15

## 结论

为 `limit_ladder` 下的三个完整路径分别建立来源内字段身份。字段名与既有 `shortline` 路径相同，但输出路径不同，不能用短字段名合并身份。

| 完整路径 | 规范名 | 含义 | 单位 |
|---|---|---|---|
| `limit_ladder.target_trade_date` | `target_trade_date` | 当前行情对应的目标交易日日期 | 日期 |
| `limit_ladder.previous_trade_date` | `previous_trade_date` | 上一实际交易日日期 | 日期 |
| `limit_ladder.stats_date` | `stats_date` | 统计资源主导日期 | 日期 |

这里的 `stats_date` 是 ZHB 统计资源的业务日期，不能替代采集目录的 `data_date` 或 ELTDX 行情的目标交易日。

## 路径和上游契约

项目采集器在 `scripts/capture_tcp_collectors.py` 中调用 `client.helpers.limit_ladder(codes=_ecodes)`，把 `LimitLadderTable` 转成 JSON 写入 `global_helpers.limit_ladder`；随后将每行原样复制到相应股票的 `stocks.<code>.limit_ladder`。生产适配器 `core/eltdx_adapter.py` 也将 Helper 行序列化为采集结果。登记路径因此是 `TDX-eltdx(适配层)::limit_ladder.<field>`。

锁定上游为项目固定的 ELTDX v3.3.2。其 [`连板天梯 Helper 文档`](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/helpers/%E8%BF%9E%E6%9D%BF%E5%A4%A9%E6%A2%AF.md)说明 `LimitLadderTable.rows` 是 `ShortlineIndicator` 行，并逐项列出三个日期字段；`limit_ladder()` 的实现只按 `limit_status` 筛选这些行，返回 `trade_date=table.target_trade_date`，不改写行内日期。固定版本的 [`短线指标文档`](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/helpers/%E7%9F%AD%E7%BA%BF%E6%8C%87%E6%A0%87.md)与 [`ShortlineIndicator` 实现](https://github.com/electkismet/eltdx/blob/v3.3.2/src/eltdx/helpers/shortline.py)给出日期含义和类型：目标日来自 TDX 握手；上一交易日取自上证指数实际日 K；统计日是 `tdxstat.cfg` 与 `tdxstat2.cfg` 的共同主导日期，且只能等于目标交易日或上一实际交易日，并由 `alignment_status` 标记。

## 留存样本核对

仅检查 `2026-10-15` 起的 `raw_eltdx.json`。`meta.json.data_date` 使用 `YYYYMMDD`，已先规范化后与行内 ISO 日期比较。13 条 `limit_ladder` 行覆盖 10 个目标数据日、6 只股票；所有行的 `target_trade_date` 均等于表级 `trade_date` 和目录 `data_date`，所有 `stats_date` 均符合其 `alignment_status`，没有样本反例。

| 采集目录 | 行数 | `same_day` | `previous_trading_day` |
|---|---:|---:|---:|
| `20261016` | 2 | 2 | 0 |
| `20261020` | 1 | 0 | 1 |
| `20261021` | 1 | 1 | 0 |
| `20261023` | 1 | 0 | 1 |
| `20261026` | 1 | 0 | 1 |
| `20261028` | 1 | 0 | 1 |
| `20261030` | 1 | 1 | 0 |
| `20261102` | 3 | 0 | 3 |
| `20261104` | 1 | 0 | 1 |
| `20261110` | 1 | 0 | 1 |
| **合计** | **13** | **4** | **9** |

官方固定版本的返回模型和项目精确采集映射是定案依据；历史行用于检查项目序列化和日期关系，没有把同一来源的重复输出当作独立来源证据。当前结论只确认三个 ELTDX 适配层路径，不建立跨源映射，也不声称统计资源日期等同于行情 `as_of_date`。
