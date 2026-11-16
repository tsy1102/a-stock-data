# TDX 快照模型衍生行情字段语义核验

复核日期：2026-11-16。本记录核定 `TDX(双命名源)::change`、`change_pct`、`amplitude_pct`、`rise_speed` 四个精确注册表路径在 AxData TDX 实时快照模型中的含义。它不把 AxData 字段表当作通达信官方 wire 字段表，也不认定这些裸路径是本项目当前采集输出。

## 裁决

| 完整来源身份 | 核定含义 | 单位 | 尚未确认 |
|---|---|---|---|
| `TDX(双命名源)::change` | 最新价减前收盘价的涨跌额 | 未注明 | 通用模型涵盖股票/指数，未证明统一单位或项目 raw 路径 |
| `TDX(双命名源)::change_pct` | `(最新价－前收盘价) / 前收盘价 × 100` | `%` | 未映射到项目的嵌套 `quote_full.change_pct` |
| `TDX(双命名源)::amplitude_pct` | `(最高价－最低价) / 前收盘价 × 100` | `%` | 当前项目 TDX raw 未出现该精确模型路径 |
| `TDX(双命名源)::rise_speed` | 涨速百分比指标 | `%` | 具体窗口、刷新口径及 wire 字节槽与官方函数的对应关系 |

四项均按来源内模型语义登记为 `verified`，没有新增 `mappings`。`rise_speed` 的 verified 范围仅到“涨速百分比指标”，不包含其窗口或协议槽位。前收盘价为零时，AxData 的 `change_pct`、`amplitude_pct` 属性返回空值。

AxData 的股票专用 `stock_realtime_snapshot_tdx` 字段目录将该接口的 `change` 标成元；TDX 指数快照使用不同的点位语境，而注册身份没有绑定某个具体接口/证券类别，所以这里不把“元”扩展成整个 `TDX(双命名源)::change` 的统一单位。

## 官方定义与模型实现

- 通达信[公式系统函数目录](https://help.tdx.com.cn/gspt/docs/markdown/redword/functionlist.html)定义 `DYNAINFO(12)` 为日涨跌、`DYNAINFO(13)` 为振幅、`DYNAINFO(14)` 为涨跌幅、`DYNAINFO(24)` 为涨速；其中振幅、涨跌幅和涨速按目录要求乘以 100 表示为百分数值。
- AxData 固定提交 [`f8ce3cee989717d79c7ad8f73b42f93c6dbd87e8` 的 TDX quote model](https://github.com/electkismet/AxData/blob/f8ce3cee989717d79c7ad8f73b42f93c6dbd87e8/packages/axdata-source-tdx/src/axdata_source_tdx/_tdx_wire/models/quote.py#L107-L124)直接由 `last_price`、`pre_close`、`high`、`low` 计算涨跌额、涨跌幅和振幅；前收盘为零时百分比属性为空。
- 同一固定版的 [`stock_realtime_snapshot_tdx` 字段目录](https://github.com/electkismet/AxData/blob/f8ce3cee989717d79c7ad8f73b42f93c6dbd87e8/packages/axdata-source-tdx/src/axdata_source_tdx/axdata-provider.json#L7960-L8175)将上述模型输出标注为涨跌额（元）、百分比数值、振幅百分数和涨速百分数；[`snapshot_normalize.py`](https://github.com/electkismet/AxData/blob/f8ce3cee989717d79c7ad8f73b42f93c6dbd87e8/packages/axdata-source-tdx/src/axdata_source_tdx/snapshot_normalize.py#L168-L196)把相应属性写入规范化快照。
- AxData [`quotes.py` 协议解析器](https://github.com/electkismet/AxData/blob/f8ce3cee989717d79c7ad8f73b42f93c6dbd87e8/packages/axdata-source-tdx/src/axdata_source_tdx/_tdx_wire/protocol/commands/quotes.py#L608-L617)从一个签名 16 位值按 100 缩放得到 `rise_speed`。此实现与字段目录的百分数标签相符，但没有证明该 wire 槽位等于官方 `DYNAINFO(24)`，也没有说明计算窗口；因此不外推这两点。

## 项目采集路径核查

按 [`capture_retention.py`](../../../scripts/capture_retention.py) 的 2026-10-15 保留边界，重新核对既有 561 文件清单中的 raw/meta SHA-256；全部哈希匹配。新审计表 [`20261116_tdx_quote_model_derived_capture_path_audit.csv`](../research/20261116_tdx_quote_model_derived_capture_path_audit.csv) 记录每份文件的哈希、目标键出现次数及完整 JSON 路径：

- 561 份 raw 中有 18 份 `raw_tdx.json`。TDX raw 中，`change` 为 0 次、`amplitude_pct` 为 0 次、`rise_speed` 为 0 次。
- TDX raw 中有 358 次 `change_pct`，完整路径均为 `stocks.*.quote_full.change_pct`；注册表目标是裸路径 `change_pct`。路径不同，不能因叶名相同而合并身份或映射。
- TDX 来源元数据没有提供可用 `as_of_date`。这份清单只验证留存文件与完整路径，不作为数值碰撞、来源日期或跨源关系证据。

项目此前的 [`20261115_tdx_quote_capture_provenance.md`](20261115_tdx_quote_capture_provenance.md) 已将嵌套 `quote_full.change_pct` 单独识别为项目派生路径；本记录不覆盖该结论。

## 结论边界

这次完成四条 AxData TDX 模型路径的字段语义登记，不代表本项目已调用相同接口、保存相同模型键或获得相同源端字段。`change` 的通用单位仍空缺；`rise_speed` 的具体窗口和协议映射继续待核；不修改采集、缓存或路由，也不建立跨源映射。逐字段前后状态、外部证据及审计表 SHA-256 保存在同名 JSON 决策文件中。
