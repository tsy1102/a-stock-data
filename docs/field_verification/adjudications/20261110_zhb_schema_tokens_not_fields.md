# ZHB 注册表类型/格式占位符清理

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

## 为什么它们不是字段路径

- `YYYYMMDD` 在来源文档中用于日期值格式，例如报告期、披露日或快照日期；对应的实际字段路径是 `report_period`、`disclose_date`、`date` 等，不是 `YYYYMMDD`。
- `float` 和 `int` 是数值类型/解析器转换器。当前 [`core/zhb_client.py`](../../../core/zhb_client.py) 把它们作为 `_safe_cast` 的转换参数；输出字典键是 `change_60d`、`employee_count` 等命名字段。
- [`docs/verify/zhb_verify.md`](../../verify/zhb_verify.md) 中的 ZHB 表列出实际位置式字段；日期格式和 Python 类型位于格式/取值描述中，不是来源字段名。
- 六条注册记录本身没有字段含义、规范名、单位、来源章节或参考证据。当前解析器、测试和保留 raw 均未将这些 token 作为对象键输出。

## 定案

这六条是从类型/格式说明混入的注册表占位符，不是可破解的来源字段路径。仅将这六个精确身份标记为 `disproved`，`status_resolution` 设为 `not_field_schema_token`；不为它们虚构字段名、单位或跨源映射。

本决定不涵盖真实存在但暂时没有值的 `ZHB-tipinfo::[17]` 和 `ZHB-tipinfo::[18]`。它们仍是实际列路径，保留未知状态；当前样本全空不足以说明其用途。
