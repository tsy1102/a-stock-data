# ELTDX `chang_qi_fu_zhai_raw_float` 字段定案

## 结论

`TDX-eltdx(适配层)::chang_qi_fu_zhai_raw_float` 是**少数股东权益原始值**，合并资产负债表口径，单位为千元，反映最近一期财务数据。此结论只写入该完整 ELTDX 来源路径，不建立跨源映射。

ELTDX v3.3.2 文档将该路径标注为“长期负债原始值”。这一语义与通达信官方字段定义和保留期财报数值不符，视为上游文档误标；单位“千元”则得到字段文档及样本换算支持。

## 字段路径与来源契约

- ELTDX 调用：`client.corporate.finance_batch(codes, include_raw=True)`，底层 TDX 0x0010；返回 `FinanceRecord.chang_qi_fu_zhai_raw_float`。
- ELTDX v3.3.2 文档列出该字段原始值单位为千元，但把含义写作长期负债。`FinanceRecord` 中该字段位于流动负债后、资本公积金前。
- 通达信官方函数表将 FINANCE(15)、FINANCE(16)、FINANCE(17) 分别定义为流动负债、少数股东权益、资本公积金。官方 TQ `get_stock_info` 又将 `J_cqfz` 明确列为少数股东权益（万元）。
- 项目 `core/eltdx_adapter.py` 将该 ELTDX 原始键映射为 TDX `changqifuzhai`，执行 `qy2jiao` 转换。TDX 原始样本与 ELTDX 样本的比例符合千元转角的换算；该同族来源关系只用于确认适配转换，不作为独立外部证据。

官方定义：

- [通达信公式系统函数列表](https://help.tdx.com.cn/gspt/docs/markdown/redword/functionlist.html)：FINANCE(15–17) 的字段定义。
- [通达信量化平台 get_stock_info](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/mindoc-1h10jj7r7jol4.html)：`J_cqfz` 为少数股东权益（万元）。
- [ELTDX v3.3.2 财务基础信息文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-%E8%B4%A2%E5%8A%A1%E5%9F%BA%E7%A1%80%E4%BF%A1%E6%81%AF.md) 与 [FinanceRecord 模型](https://github.com/electkismet/eltdx/blob/v3.3.2/src/eltdx/models/corporate.py)：确认 API 路径、原始字段位置和单位；其“长期负债”标签被样本与官方定义反证。

## 留存样本与发行人报表核对

2026-10-15 样本对应当时最近披露的 2026 年半年度报告；2026-11-02/06 样本对应随后披露的 2026 年第三季度报告。将 ELTDX 原始值乘以 1,000 换算为元：

| 股票 | 报告期 | ELTDX 原始值（千元） | 换算为元 | 官方报表少数股东权益（元） | 换算差额（元） |
|---|---:|---:|---:|---:|---:|
| 贵州茅台 600519 | 2026-06-30 | 10,842,758 | 10,842,758,000 | 10,842,757,754.86 | +245.14 |
| 万华化学 600309 | 2026-06-30 | 12,933,088 | 12,933,088,000 | 12,933,087,240.25 | +759.75 |
| 泸州老窖 000568 | 2026-06-30 | 150,056.5 | 150,056,500 | 150,056,579.80 | -79.80 |
| 贵州茅台 600519 | 2026-09-30 | 9,216,876 | 9,216,876,000 | 9,216,876,481.22 | -481.22 |
| 万华化学 600309 | 2026-09-30 | 13,325,574 | 13,325,574,000 | 13,325,573,321.86 | +678.14 |
| 泸州老窖 000568 | 2026-09-30 | 161,781.203125 | 161,781,203.125 | 161,781,272.04 | -68.915 |

半年报：

- [贵州茅台 2026 年半年度报告](https://static.cninfo.com.cn/finalpage/2026-08-15/1225475868.PDF)
- [万华化学 2026 年半年度报告](https://static.cninfo.com.cn/finalpage/2026-08-25/1225497561.PDF)
- [泸州老窖 2026 年半年度报告](https://disc.static.szse.cn/download/disc/disk03/finalpage/2026-08-26/dddd84cb-a0dd-4ceb-89c3-840c16ceafda.PDF)

三季报：

- [贵州茅台 2026 年第三季度报告](https://static.cninfo.com.cn/finalpage/2026-10-31/1225649896.PDF)
- [万华化学 2026 年第三季度报告](https://static.cninfo.com.cn/finalpage/2026-10-27/1225622843.PDF)
- [泸州老窖 2026 年第三季度报告](https://static.cninfo.com.cn/finalpage/2026-10-30/1225639079.PDF)

六组差额的绝对值均低于 1,000 元，即低于一个千元原始单位。差额兼容原始 float 精度与来源取整；不将其表述为精确到元相等。各报告资产负债表列示的少数股东权益与换算值接近，而上游文档所称长期负债与该数值不符。

## 边界

- 报告期归属由采集时已公布的财报和发行人资产负债表确认；源字段更新日期不被当作公告时间或财报日期。
- 直接 TDX `changqifuzhai` 数值与此路径呈适配转换关系，但它与 ELTDX 属同一 TDX 家族，不能算独立来源验证。
- TDX `changqifuzhai` 现有注册项仍有历史 canonical 属性冲突；本次不绕过 `correct_verified_metadata` 的冲突闸门，也不更改该项。该项后续须先依现行工作流拆清冲突再纠正。
