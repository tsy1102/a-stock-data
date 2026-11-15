# ELTDX KlineSeries 周期与复权元数据来源契约定案

- 复核日期：2026-11-15
- 来源身份：`TDX-eltdx(适配层)`
- 保留样本边界：`MIN_CAPTURE_DATE = 2026-10-15`

## 裁决

| 注册 code path（相对 `KlineSeries`） | 规范名 | 含义 | 单位 |
|---|---|---|---|
| `period_raw` | `period_raw` | K 线周期底层类型编号；须与 `period_param_raw` 配对解释 | 协议编号 |
| `period_param_raw` | `period_param_raw` | 周期底层参数；扩展周期中的 N 表示 N 分钟、N 日或 N 秒 | 协议参数 |
| `period_name` | `period_name` | ELTDX SDK 规范化周期名，例如 `day`、`1m` | — |
| `start` | `start` | 分页请求起始位置，从 0 开始 | 条索引 |
| `request_count` | `request_count` | 请求条数；自动分页合并后更新为合并 K 线总数 | 条 |
| `adjust_mode_raw` | `adjust_mode_raw` | 复权模式底层编号：0 不复权、1 前复权、2 后复权、3 定点前复权、4 定点后复权 | 协议枚举码 |
| `adjust_mode` | `adjust_mode` | ELTDX SDK 规范化复权模式名 | — |
| `anchor_date_raw` | `anchor_date_raw` | 定点复权日期底层值；0 表示未使用，非零编码未在契约中说明 | — |
| `anchor_date` | `anchor_date` | 定点复权锚定日期，仅定点复权模式需要 | 日期 |

这些是 `KlineSeries` 的系列/请求元数据，不是市场行情值。注册表中的路径是 KlineSeries 模型字段；采集文件中的完整 JSON 路径为 `global_helpers.market_stat_880005.<field>`。项目通过 `client.bars.get("sh880005", period="day", count=1)` 获取该模型，再由 `_jfy()` 序列化。实现位于 [`capture_tcp_collectors.py`](../../../scripts/capture_tcp_collectors.py) 的 `collect_eltdx`。

## 上游契约

项目 `requirements.txt` 固定 `eltdx==3.3.2`。该版本的 [7709 K 线周期线文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-K%E7%BA%BF%E5%91%A8%E6%9C%9F%E7%BA%BF.md) 将返回模型明确为 `KlineSeries`，并列出周期编号与周期参数表、分页参数、复权模式编码和解析字段。其 [字段手册](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md) 独立定义 `period_name`、`adjust_mode`、`anchor_date`。

- 周期例：`4/1` 为日 K，`8/N` 为 N 分钟扩展周期，`9/N` 为 N 日扩展周期，`13/N` 为 N 秒周期。
- 复权枚举：`0=none`、`1=qfq`、`2=hfq`、`3=fixed_qfq`、`4=fixed_hfq`。
- `anchor_date_raw=0` 表示没有使用定点日期；不据此推断非零原始值的序列化格式。
- 普通前复权/后复权不需要 `anchor_date`；定点前复权/后复权需要该日期。
- 自动分页会把 `request_count` 更新为合并后的 K 线总数；该行为不影响本项目当前单页 `count=1` 调用。

## 保留样本核对

只读取 `MIN_CAPTURE_DATE` 之后包含 `raw_eltdx.json` 的 18 个日期目录，不使用更早样本。18 份文件均包含同一模型路径 `global_helpers.market_stat_880005`，并一致观察到：`period_raw=4`、`period_param_raw=1`、`period_name="day"`、`start=0`、`request_count=1`、`adjust_mode_raw=0`、`adjust_mode="none"`、`anchor_date_raw=0`、`anchor_date=null`。它们与当前代码中的 `period="day"`、默认 `start=0`、`count=1`、默认不复权参数相符。

逐目录运行时间、目录目标数据日、字段原值及 `raw_eltdx.json` SHA-256 见 [`20261115_eltdx_kline_series_metadata.csv`](../research/20261115_eltdx_kline_series_metadata.csv)。CSV 规范 LF SHA-256：`597002ccd29bd9b06c5fb3cac9fd6ea1f9cb8e4f1785ce2f07c8ab1bbd09c265`。

本样本核对只验证已知请求配置如何呈现在 ELTDX 返回模型中；没有将目录 `data_date`、运行自然日或这些静态参数当成行情 `as_of_date`，不构成跨源碰撞证据。本次不新增 `mappings`。完整结构化决定见 [`20261115_eltdx_kline_series_source_contract.json`](20261115_eltdx_kline_series_source_contract.json)。
