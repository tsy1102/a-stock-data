# ZHB 20/60 根 K 线涨跌字段语义更正

复核日期：2026-11-12。范围仅为 `ZHB-tdxstat::stat.change_20k_bar` 与 `ZHB-tdxstat::stat.change_60k_bar`。本次纠正注册表中“20分钟/60分钟 K 线涨跌”的错误释义，不改变采集、解析或缓存行为，也不建立跨源映射。

## 精确路径与解析位置

项目的 [`_parse_tdxstat()`](../../../core/zhb_client.py) 将 `tdxstat.cfg` 的第 `[17]` 列解析为 `stat.change_20k_bar`，第 `[19]` 列解析为 `stat.change_60k_bar`。解析器注释将其说明为近 20/60 根 K 线涨跌幅，按交易日计算；第 `[17]` 明确包含当日。对应测试 [`test_data_zhb.py`](../../../tests/data/test_data_zhb.py) 验证两个返回键来自列 `[17]` 和 `[19]`。

可公开查阅的 [injoyai/tdx `TdxStat` 协议解析文档](https://pkg.go.dev/github.com/injoyai/tdx/protocol#TdxStat) 将第 `[17]` 和 `[19]` 描述为近 20/60 根的“含当日”变体，并与相邻第 `[18]`、`[20]` 截至前一交易日的字段区分。该资料是公开的协议解析/逆向研究，不是通达信官方字段字典；它作为独立字段语义佐证，不冒充官方契约。项目旧字段审计 [`field_source_reference.md`](../../field_source_reference.md) §2 中对列 `[17]`、`[19]` 的历史核验也已指出它们分别对应近 20/60 根 K 线，而不是分钟周期。

## 保留样本的来源路径核验

依根目录数据保留边界，仅使用 `20261015` 至 `20261110` 的 17 个保留 `raw_zhb.json`。每个采集日包含 20 只股票：

| 字段 | `full` 与 `stat` 完全相同 | `stat2` 同名值 | 可比观测 |
|---|---:|---:|---:|
| `change_20k_bar` | 340/340 | 0 | 340 |
| `change_60k_bar` | 340/340 | 0 | 340 |

因此，合并视图 `zhb.full.*` 的这两个叶字段在保留样本中唯一归属于 `ZHB-tdxstat::stat.*`，不是 `stat2` 字段，也不是 20/60 分钟 K 线。该逐样本比较仅用于确认 `full` 到 `stat` 的精确路径；字段周期语义由第 `[17]`/`[19]` 的解析映射和公开协议解析核验共同支持。

680 行逐股票、逐采集日的原值与路径比较保存在 [`20261112_zhb_kbar_full_stat_samples.csv`](20261112_zhb_kbar_full_stat_samples.csv)，SHA-256：`B59EB4DDD0B0B77EFBB93B87ACA0A2EFDBD6FB04E8215F08B7ADCE6A2C180961`。

## 定案范围与限制

- `stat.change_20k_bar`：近 20 根日 K 线涨跌幅，含当日，按交易日计，单位 `%`。
- `stat.change_60k_bar`：近 60 根日 K 线涨跌幅，含当日，按交易日计，单位 `%`。
- 结论只适用于本项目保留样本所用的精确解析路径。公开协议解析项目不是数据提供方官方字典，因此不据此声明通达信所有服务器版本的底层字段契约。
- `zhb.full.*` 只有在对应叶字段的注册来源唯一时才可按别名复用；`stat` 与 `stat2` 存在同名路径时，仍标记为歧义，不据此自动归属。
