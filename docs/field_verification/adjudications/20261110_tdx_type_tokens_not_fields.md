# TDX 类型/格式 token 注册身份清理

日期：2026-11-10<br>
范围：仅 `TDX(双命名源)::YYYYMMDD`、`::float`、`::str`、`::byte`、`::uint` 五个完整身份。

## 文档位置证据

[`field_source_reference.md`](../../field_source_reference.md) §2.1 的 0x0010 财务记录表明确区分字段键、类型和格式：`market` 的类型为 `byte`，`code` 的类型为 `str`；`liutongguben`、`zongguben` 等具名字段的类型为 `float`；`updated_date`、`ipo_date` 是 `uint` 字段，取值格式为 `YYYYMMDD`。这些 token 出现在类型/格式列，不是返回字段名。

独立的公开 [`injoyai/tdx` 协议实现](https://pkg.go.dev/github.com/injoyai/tdx/protocol)明确将 `TypeFinance` 定义为 `0x0010`，并在 `FinanceInfo` 中将 `Market` / `Code` 标为 `uint8` / `string`、将 `UpdatedDate` / `IPODate` 标为 `uint32`。这与本项目参考表的 `byte` / `str` / `uint` 类型角色相符；它是独立交叉核验，不作为本项目字段命名或包装层的一一映射依据。

逐身份文档位置与结论见 [`20261110_tdx_type_tokens_audit.csv`](20261110_tdx_type_tokens_audit.csv)。

## 解析器与样本边界

对仓库所有 Python 文件执行字典键字面量扫描，未发现键名为 `YYYYMMDD`、`float` 或 `str` 的字典构造；当前 TDX 解析器和 `tests/data/test_data_tdx.py` 使用具名字段路径。该结论针对代码结构，不依赖行情样本值。

近期采集元数据中的 TDX `as_of_date` 未确认。为遵守来源日期准入规则，本次没有用这些 raw 样本进行碰撞或定案，也没有用运行自然日或采集目录目标数据日替代来源日期。字段类型/格式表和当前解析器契约足以判断这三个字符串在该来源中是类型/格式 token。

## 定案与边界

只将上述五个完整身份标记为 `disproved`、`status_resolution: not_field_schema_token`；保留原状态快照和空的字段语义/单位，不创建映射、不修改 TDX 数据获取或缓存。`TDX-eltdx(适配层)` 中同名或相似的类型 token 属于其他来源身份，本次未处理。
