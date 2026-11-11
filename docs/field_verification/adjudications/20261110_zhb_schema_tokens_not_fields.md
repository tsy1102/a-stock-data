# ZHB 注册表类型/格式标记与实际字段对应关系

日期：2026-11-10<br>
范围：以下 6 个精确注册身份：

- `ZHB-tdxstat::YYYYMMDD`
- `ZHB-tdxstat::float`
- `ZHB-tdxstat::int`
- `ZHB-tdxstat2::YYYYMMDD`
- `ZHB-tdxstat2::float`
- `ZHB-tipinfo::YYYYMMDD`

## 日期与样本资格

按每个 `meta.json` 的 ZHB 来源日期和对应 `zhb_YYYYMMDD.zip` 文件名筛选；仅读取来源数据日不早于 `20261015` 且有同名日期化归档的 raw 文件。15 个符合条件的采集文件对应 11 个不同来源数据日，11 日均通过项目本地 A 股交易日历校验。重复采集按来源数据日合并。

保留期内这些 raw 的对象键中，`YYYYMMDD`、`float`、`int` 均为 0 次。`20261015` 目录的来源日期为 `20261014`，在打开 raw 前排除；没有读取保留起点之前的 raw、ZHB 压缩包或解析缓存。

逐目录日期资格和键计数见 [`20261110_zhb_schema_tokens_audit.csv`](20261110_zhb_schema_tokens_audit.csv)。清单分别记录采集目录/元数据目标数据日、运行自然日、ZHB 实际 `as_of_date`、同名归档、交易日资格和 `raw_zhb.json` 中 `zhb_date` 副本；目录日期与来源数据日不混用。清单也记录了 `20261015` 目录：来源日为 `20261014`，明确未打开 raw。

## `YYYYMMDD` 对应的实际日期字段

`YYYYMMDD` 是日期值格式说明，不是无意义残留。它在不同 ZHB 来源中指向不同的真实日期字段；格式 token 自身不是返回路径，但对应日期数据仍由具名或位置式字段保存。

| 注册表中的格式 token | 实际字段路径 | 日期含义 | 项目输出路径 |
|---|---|---|---|
| `ZHB-tdxstat::YYYYMMDD` | `tdxstat[4]` / `date` | 该统计记录的数据快照日期 | `stat.date` |
| `ZHB-tdxstat2::YYYYMMDD` | `tdxstat2[2]` / `date` | 该统计记录的数据日期 | `stat2.date` |
| `ZHB-tipinfo::YYYYMMDD` | `tipinfo[2]` / `report_period` | 财报报告期截止日 | `report_period` |
| 同上 | `tipinfo[4]` / `disclose_date` | 财报预约披露日 | `disclose_date` |
| 同上 | `tipinfo[5]` / `zt_date_recent` | 近两年最近涨停日 | `zt_date_recent` |
| 同上 | `tipinfo[7]` / `suspend_major_event_date` | 重大事项停牌起始日 | `suspend_major_event_date` |
| 同上 | `tipinfo[8]` / `shareholder_change_date` | 股东持股变动记录关联日期；可能是交易日、区间截止日或协议签署日 | `shareholder_change_date` |
| 同上 | `tipinfo[10]` / `dt_date_recent` | 最近跌停日 | `dt_date_recent` |
| 同上 | `tipinfo[11]` / `forecast_date_recent` | 最新业绩预告发布日 | `forecast_date_recent` |
| 同上 | `tipinfo[13]` / `unlock_date` | 最新解禁日 | `unlock_date` |
| 同上 | `tipinfo[19]` / `hg_date` | 最近回购预案日 | `hg_date` |
| 同上 | `tipinfo[21]` / `equity_incentive_date` | 股权激励预案/草案公告日 | `equity_incentive_date` |

`tdxstat` 与 `tdxstat2` 中的值用于标识来源记录日期；`tipinfo` 中则是业务日期，可能早于采集日期多年。它们都不能统一替代采集目录目标数据日、运行自然日、交易日或来源级 `as_of_date`。

上表列出当前 `_parse_tipinfo()` 输出的日期路径。只读协议参考还记载 `[6]` 阶段新高日（`TopDate_Recent`）和 `[15]` 旧增发事件日期；当前解析器不输出这两列，因此它们是历史契约说明，不计入当前运行返回键。

`div_date` / `div_amount` 是 `[8]` / `[9]` 的旧输出别名，已因旧“业绩预告”解释不成立而弃用；原始 `[8]` 日期字段仍存在，当前键为 `shareholder_change_date`。详见 [`20261108 ZHB 股东持股变动字段定案`](../zhb_tipinfo_shareholder_change_adjudication_20261108.md)。这里证伪的是旧别名和旧语义，不是日期信息或原始列。

## 为什么格式 token 本身不是字段路径

- `float` 和 `int` 是数值类型/解析器转换器。当前 [`core/zhb_client.py`](../../../core/zhb_client.py) 把它们作为 `_safe_cast` 的转换参数；输出字典键是 `change_60d`、`employee_count` 等命名字段。
- [`docs/verify/zhb_verify.md`](../../verify/zhb_verify.md) 中的 ZHB 表列出实际位置式字段；日期格式和 Python 类型位于格式/取值描述中，不是来源字段名。
- 六条注册记录本身没有字段含义、规范名、单位、来源章节或参考证据。当前解析器、测试和保留 raw 均未将这些 token 作为对象键输出。

## 定案

这六条中，`float` / `int` 是类型或转换器标记，`YYYYMMDD` 是实际日期字段使用的值格式标记；它们都不是独立的返回字段路径。仅将这六个精确身份标记为 `disproved`，`status_resolution` 设为 `not_field_schema_token`。该状态不否认日期格式及其实际对应字段；上表已列出各来源对应关系。不为 token 虚构单一日期字段或跨源映射。

本决定不涵盖真实存在但暂时没有值的 `ZHB-tipinfo::[17]` 和 `ZHB-tipinfo::[18]`。它们仍是实际列路径，保留未知状态；当前样本全空不足以说明其用途。
