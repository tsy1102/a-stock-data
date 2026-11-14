# Eastmoney 报价精度字段来源内实证

复核日期：2026-11-14（Asia/Shanghai）

适用路径：`东财-push2(stock/get)::f59`、`东财-ulist239(np/get)::f1`

证据类型：来源内经验实证；未发现 Eastmoney 发布这两个数字路径的逐字段正式释义，因此不称为官方字段契约。

## 定案结论

- `stock/get::f59` 表示该证券行情报价的显示小数位数，单位为“位”。
- `ulist.np/get::f1` 在其自身接口中也表示该证券行情报价的显示小数位数，单位为“位”。两项分别定案，不建立跨源 `mappings`。
- 两条路径都没有证明股票代码 `f152` 的含义。`stock/get::f152` 降回待核候选；`ulist.np/get::f152` 继续待核。
- 旧的 `stock/get::f152 ↔ ulist::f1` 和 `ulist::f152 ↔ stock/get::f59` 关系被 2026-11-14 的 B 股反例否定。旧历史报告保留为历史记录，当前对齐表和活动映射撤回这两条关系。

## 项目原始路径

[`scripts/capture_http_collectors.py`](../../../scripts/capture_http_collectors.py) 的 `collect_push2`（第 84 行起）请求 Eastmoney `stock/get` 并保存响应 `data` 对象；`collect_ulist239`（第 944 行起）请求 `ulist.np/get` 并保存 `diff` 行。两条路径均未在采集器中改名或计算，本决定针对原始响应键。

## 保留期 A 股样本

样本表：[20261114_eastmoney_price_precision_retained_samples.csv](../research/20261114_eastmoney_price_precision_retained_samples.csv)

SHA-256：`104f1d24096e556c633316cba5cd2aba91fca8134f65b6b579188a224ee1b4f3`

按仓库保留边界只读 `2026-10-15` 及之后样本。该表包含 7 个交易日（2026-11-02、03、04、05、06、09、10）×20 只 A 股，共 140 个股票日配对；每个来源状态为 `ok`，来源实际日期均与目录 `data_date` 相同。Push2 日期由 `f86` Unix 秒转换为北京时间日期；Ulist 优先用 `f297`，该字段缺失时使用已验证的 `f124` 日期。140 行中 `stock/get::f59=2`、`ulist.np/get::f1=2`，且两者数值相等。由于这批 A 股样本中的两个字段均为常量 2，这种相等本身不作为跨源等价证明。

## 官方接口差异样本

2026-11-14（星期六）17:36–17:38（Asia/Shanghai）只读查询 Eastmoney 官方接口。响应的 `f86` 与 `f297` 表明行情数据日为 2026-11-13，而非查询自然日。

| 股票 | 接口/参数 | `f59` 或 `f1` | `fltt=1` 价格字段 | `fltt=2` 价格字段 | `f152` |
|---|---|---:|---:|---:|---:|
| 贵州茅台 `600519` | [`stock/get`](https://push2.eastmoney.com/api/qt/stock/get?secid=1.600519&fltt=1&invt=2&fields=f43,f57,f58,f59,f60,f86,f152,f169,f170) | `f59=2` | `f43=143526` | `f43=1435.26` | `f152=2` |
| 云赛 B 股 `900901` | [`stock/get`](https://push2.eastmoney.com/api/qt/stock/get?secid=1.900901&fltt=1&invt=2&fields=f43,f57,f58,f59,f60,f86,f152,f169,f170) | `f59=3` | `f43=516` | `f43=0.516` | `f152=2` |
| 贵州茅台 `600519` | [`ulist.np/get`](https://push2.eastmoney.com/api/qt/ulist.np/get?secids=1.600519,1.900901&fltt=1&invt=2&fields=f1,f2,f12,f14,f152,f297) | `f1=2` | `f2=143526` | `f2=1435.26`（`fltt=2`） | `f152=2` |
| 云赛 B 股 `900901` | [`ulist.np/get`](https://push2.eastmoney.com/api/qt/ulist.np/get?secids=1.600519,1.900901&fltt=1&invt=2&fields=f1,f2,f12,f14,f152,f297) | `f1=3` | `f2=516` | `f2=0.516`（`fltt=2`） | `f152=2` |

两接口 `fltt=2` 查询分别于 17:36:17.414–17:36:17.597 和 17:38:01.006–17:38:01.485 完成；`fltt=1` 查询于 17:36:16.786–17:36:17.699 完成，HTTP 均为 200。Ulist 的 `f297` 为 `20261113`；Push2 的 `f86` 分别为 `1794557495`、`1794557501`，均落在 2026-11-13 的北京时间收盘后时段。

相同证券在 `fltt=1` 与 `fltt=2` 下的报价分别满足 `143526 / 10² = 1435.26` 和 `516 / 10³ = 0.516`；两条接口路径中的 `f59` / `f1` 分别随所需小数位从 2 变为 3。Eastmoney 官方行情页也展示了相同证券报价：[600519 贵州茅台](https://quote.eastmoney.com/sh600519.html)、[900901 云赛 B 股](https://quote.eastmoney.com/sh900901.html)。这组变化样本区分了“价格精度位数”与“全市场固定常量 2”。

## 旧关系复核

- 旧 `stock/get::f152 ↔ ulist::f1`：A 股历史样本中两值均为 2；在同日 B 股样本中 `stock/get::f152=2`、`ulist::f1=3`，旧精确相等关系不成立。`stock/get::f152` 的语义仍未确定，不能据此给它赋予精度含义。
- 旧 `ulist::f152 ↔ stock/get::f59`：同日 B 股样本为 `ulist::f152=2`、`stock/get::f59=3`，旧精确相等关系不成立。Ulist `f152` 的 140 条保留期 A 股值和本次两条实时值均为 2，但现有样本不能区分其含义，继续待核。
- `ulist::f1` 和 `stock/get::f59` 的来源内语义现均可确认，但正式跨源映射仍按映射裁决流程单独处理；本决定不把 A 股常量命中或单个 B 股同值当作跨源碰撞定案。

## 边界

结论由 140 个日期合格 A 股样本、同一数据日的 B 股实时变化样本及 Eastmoney 报价展示共同支持。已观测 A 股与该 B 股的报价精度行为；未外推到未观测证券类别或所有东财接口，也没有找到该字段编号的官方文字定义。f152 仍是待核字段。
