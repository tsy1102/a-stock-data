# docs/backups/ — 历史备份归档

> 本目录存放**历史备份快照**, 用于重大重构前后的可逆回滚与差异比对。备份文件为参考性质, **不参与生产运行**, 不应被报告脚本或数据源模块 import。

## 当前内容

| 文件 | 说明 |
|:---|:---|
| `_sc_datasource_singlefile_backup.py` | `stock_common/sc_datasource.py` 拆包前的单文件快照；只用于历史实现比对，不参与运行。 |
| `unified_layer_20260901_2045/` | 2026-09-01 统一层快照，包含 `data_provider.py`、`sc_datasource.py`、`sc_schema.py`、`tdx_client.py`，用于回溯当时的统一层结构。 |

## 维护约定

- 重大重构前可在此归档旧实现快照，目录名或文件名应包含模块名和日期。
- 备份为只读参考; 生产代码一律引用当前 `stock_common/sc_datasource/` 子包。
- 备份不会参与生产运行。清理前须检查是否仍有独有实现、字段身份或历史决策，并确认其他归档已保留所需证据；不能仅按版本年龄删除。
