# docs/backups/ — 历史备份归档

> 本目录存放**历史备份快照**, 用于重大重构前后的可逆回滚与差异比对。备份文件为参考性质, **不参与生产运行**, 不应被报告脚本或数据源模块 import。

## 当前内容

| 文件 | 说明 |
|:---|:---|
| `_sc_datasource_singlefile_backup.py` (~330KB) | **V17.2 拆包前** `stock_common/sc_datasource.py` 单文件完整备份。V17.2 已将其按数据源拆分为 `stock_common/sc_datasource/` 子包(见 `stock_common/sc_datasource/README.md`)。此备份仅用于回溯拆分前的函数实现, 切勿在新代码中引用。 |

## 维护约定

- 重大重构(包拆分 / 字段治理批次)前, 可在此归档旧实现快照, 命名 `<module>_singlefile_backup.py` 或 `<module>_<date>_backup.py`。
- 备份为只读参考; 生产代码一律引用当前 `stock_common/sc_datasource/` 子包。
- 过期备份(超过 2 个主版本)可整体删除, 不影响运行。
