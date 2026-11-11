# TDX 财务更新日与上市日字段定案

日期：2026-11-11<br>
范围：`TDX(双命名源)::updated_date`、`TDX(双命名源)::ipo_date`；同时澄清 `YYYYMMDD` 的格式标记身份。

## 证据

[`field_source_reference.md`](../../field_source_reference.md) §2.1 明确标注为 0x0010 协议完整字段表，并逐字段给出：`updated_date` = 财报更新日期、`ipo_date` = 上市日期；两者类型均为 `uint`，值格式均为 `YYYYMMDD`。这直接区分了字段路径、日期语义与值编码。

上游 ELTDX v3.3.2 的 [FinanceRecord 字段手册](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md#financerecord)将 `updated_date` 定义为财务数据更新日期、`ipo_date` 定义为上市日期；[财务批量接口文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/METHOD_REFERENCE.md#财务基础信息)确认该记录来自 TDX `0x0010`。上游协议解码器将两个原始 `u32` 分别交给 `DateParts::from_yyyymmdd`，并同时保留解析日期属性，支持“原始整数编码 / 日期对象”这一区分。

## 对冲突登记的处理

注册表原先将这两个字段的 `canonical`、`meaning`、`unit` 留空，因为参考资料中还存在较弱的聚合描述：§2.6 把多个字段名拼成一条列表，§12.13.2 将两个日期并列描述，均没有比 §2.1 更具体的逐字段定义。此次采用明确标为权威定义的 §2.1 行，并保留原始 `reference_evidence` 与冲突快照供追溯。

## 定案

| 来源路径 | 规范名 | 含义 | 值格式 |
|---|---|---|---|
| `TDX(双命名源)::updated_date` | `updated_date` | 财报更新日期 | `YYYYMMDD` 整数日期 |
| `TDX(双命名源)::ipo_date` | `ipo_date` | 股票上市日期 | `YYYYMMDD` 整数日期 |

`YYYYMMDD` 不是独立返回字段路径，也不是无意义残留；它是这两个实际日期字段的编码说明。它们记录的是财务记录自身的业务日期，不代表运行自然日、采集目录目标数据日、交易日或来源级 `as_of_date`。本次不创建两个日期字段之间或与其他来源的跨源映射，也不改变采集、解析、路由或缓存。
