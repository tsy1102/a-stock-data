# ELTDX 类型 token 注册身份清理

日期：2026-11-10<br>
范围：仅 `TDX-eltdx(适配层)::bool`、`::float`、`::int`、`::str` 四个完整身份。

## 来源契约证据

项目依赖固定为 `eltdx==3.3.2`，当前 Python 环境安装版本也为 3.3.2。`scripts/capture_tcp_collectors.py::collect_eltdx` 收集快照、短线指标、连板天梯和财务记录；其 `_jfy` 对 dataclass 使用 `dataclasses.asdict()`，因此输出对象键来自模型声明的属性名，而不是 Python 类型名。

在本机 3.3.2 包中，`QuoteSnapshot` 有 23 个属性、`FinanceRecord` 有 42 个属性、`ShortlineIndicator` 有 41 个属性；逐一检查后没有任何属性名等于 `bool`、`float`、`int` 或 `str`。对全部 134 个 ELTDX 包 Python 文件及项目采集器进行静态扫描，也未发现这四个名称作为类属性或字典字面量键。这些字符串是 Python 标量类型/注记，不是该来源返回对象的字段路径。ELTDX 上游字段手册同样以 `QuoteSnapshot`、`FinanceRecord` 和 `ShortlineIndicator` 的具名属性列出返回契约：[字段手册](https://github.com/electkismet/eltdx/blob/main/docs/FIELD_REFERENCE.md#quotesnapshot)、[FinanceRecord](https://github.com/electkismet/eltdx/blob/main/docs/FIELD_REFERENCE.md#financerecord)、[ShortlineIndicator](https://github.com/electkismet/eltdx/blob/main/docs/FIELD_REFERENCE.md#shortlineindicatortable--shortlineindicator)。

## 样本边界

本次没有读取或使用采集 raw、采集目录日期或来源数据样本。裁决依据是固定版本的返回模型和本项目序列化路径；`sample_as_of_dates` 为空、`sample_count_per_path` 为 0。未以自然日或目录目标数据日推断来源实际数据日，也没有把样本用于碰撞或定案。

逐身份证据与结果见 [`20261110_eltdx_type_tokens_audit.csv`](20261110_eltdx_type_tokens_audit.csv)。

## 定案与边界

仅将上述四个 `TDX-eltdx(适配层)` 完整身份标记为 `disproved`，`status_resolution: not_field_schema_token`；保留原状态快照和空的字段语义、规范名及单位，不创建字段映射，也不修改采集、缓存或运行时逻辑。其他来源下的同名 `float`、`int`、`str` 等身份不在本次范围内，状态保持原样。
