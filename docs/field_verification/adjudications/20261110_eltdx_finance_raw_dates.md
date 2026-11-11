# ELTDX 财务记录 raw 日期字段定案

日期：2026-11-10<br>
范围：仅 `TDX-eltdx(适配层)::updated_date_raw` 与 `::ipo_date_raw`。

## 来源契约

项目固定依赖 `eltdx==3.3.2`。`scripts/capture_tcp_collectors.py::collect_eltdx` 对 `client.corporate.finance_batch(..., include_raw=True)` 返回的 `FinanceRecord` 做 dataclass 序列化，raw 记录中的路径为 `stocks.<code>.finance_batch[0].<field>`。本机安装的 3.3.2 `FinanceRecord` 将 `updated_date_raw: int` 与 `updated_date: date | None`、`ipo_date_raw: int` 与 `ipo_date: date | None` 分别声明；这证明 raw 路径保留整数编码，配对属性是解析后的日期。

ELTDX v3.3.2 的 [FinanceRecord 字段手册](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md#financerecord)和[财务批量接口文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/METHOD_REFERENCE.md#财务基础信息)将 `updated_date` 定义为财务数据更新日期，将 `ipo_date` 定义为上市日期。本项目的 [0x0010 协议字段参考](../../field_source_reference.md)记录这两个日期字段的原始协议格式为 `YYYYMMDD`。因此，`updated_date_raw` 是财务记录更新日期的原始 `YYYYMMDD` 整数，`ipo_date_raw` 是上市日期的原始 `YYYYMMDD` 整数。

## 日期适用范围与样本边界

这两个值是单条财务记录的业务日期，不能代替运行自然日、交易日、采集目录目标数据日或 ELTDX 来源级 `as_of_date`。本次没有读取 raw 采集样本，也没有把它们用于样本日期归属、碰撞或定案；裁决依据限于固定版本模型、上游公开语义与 0x0010 日期编码契约。

## 注册表裁决

仅将上述两个完整身份设为 `verified` / `verified_by_source_contract`，规范名保留 raw 路径自身以区分整数编码和解析日期属性。字段含义标明 `YYYYMMDD` 编码，不新增跨源映射，也不改采集、缓存或运行时逻辑。决定记录见 [`20261110_eltdx_finance_raw_dates.json`](20261110_eltdx_finance_raw_dates.json)。
