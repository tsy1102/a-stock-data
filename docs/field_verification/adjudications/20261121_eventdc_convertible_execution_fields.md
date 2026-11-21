# 东方财富可转债回售与赎回执行字段核验

核验日期：2026-11-21。范围限于 `东财-event_dc(可转债列表)` 的五条执行价格/日期路径；不解释原因编码，也不创建跨来源映射。

## 结论

按东方财富可转债详情页的业务标签和两只债券发行人公告，确认以下来源内含义：

| 完整路径 | 定义 | 单位 | 2026-11-19 保留记录覆盖 |
|:--|:--|:--|--:|
| `convertible_bonds[].EXECUTE_PRICE_HS` | 当前记录所指最近一次回售的执行价格 | 元/张 | 130/500 非空 |
| `convertible_bonds[].EXECUTE_PRICE_SH` | 当前记录所指最近一次赎回的执行价格 | 元/张 | 346/500 非空 |
| `convertible_bonds[].EXECUTE_START_DATEHS` | 最近一次回售申报期首日 | 日期 | 130/130 个非空回售价格配对 |
| `convertible_bonds[].EXECUTE_END_DATE` | 最近一次回售申报期末日 | 日期 | 130/130 个非空回售价格配对 |
| `convertible_bonds[].EXECUTE_START_DATESH` | 最近一次赎回执行日 | 日期 | 345/346 个非空赎回价格配对 |

Eastmoney 的[可转债详情页](https://data.eastmoney.com/kzz/detail/110003.html)分别列出“最新赎回执行日 / 赎回价格”和“最新回售执行日 / 最新回售截止日 / 回售价格”。项目的 [`_convertible.py`](../../../stock_common/sc_datasource/_convertible.py) 使用 Eastmoney `RPT_BOND_CB_LIST` 接口，保留响应字段原键；采集器将其写入 `raw_event_dc.convertible_bonds[]`。因此项目中的完整运行路径是上述 `convertible_bonds[].<FIELD>`。

## 发行人公告逐值核验

样本来自保留期内 `docs/field_verification/20261119/raw_event_dc.json`，该文件 SHA-256 为 `41fe019b29d038e1cf4726f69700af303aae0206a6fdb8d7399912290065b091`。该文件于 2026-11-20 接收，接口没有独立的来源数据日期；以下只按债券代码与历史发行人公告核对事件值，不把采集目录日或 `fetched_at` 当成事件日。

| 债券代码 / 来源市场 | `EXECUTE_PRICE_HS` | `EXECUTE_START_DATEHS` | `EXECUTE_END_DATE` | `EXECUTE_PRICE_SH` | `EXECUTE_START_DATESH` |
|:--|--:|:--|:--|--:|:--|
| 110003 新钢转债 / `CNSESH` | 104 | 2013-08-09 | 2013-08-15 | 107 | 2013-08-27 |
| 123001 蓝标转债 / `CNSESZ` | 100.1849 | 2019-02-01 | 2019-02-14 | 101.24 | 2019-10-16 |

- 新余钢铁 2013-08-05 回售提示公告确认新钢转债回售价格为 104 元/张、申报日为 8 月 9 日至 15 日，并列明到期兑付价 107 元/张；2013-08-22 公告确认未转股债券于 8 月 27 日兑付。[回售公告](https://static.cninfo.com.cn/finalpage/2013-08-05/62905486.PDF)；[到期兑付及摘牌公告](https://static.cninfo.com.cn/finalpage/2013-08-22/62973485.PDF)。
- 蓝色光标 2019-02-19 回售结果公告确认蓝标转债回售价格 100.1849 元/张，申报日为 2 月 1 日及 2 月 11 日至 14 日；2019-10-14 赎回实施公告确认赎回价格 101.24 元/张、赎回日为 10 月 16 日。[回售结果公告](https://static.cninfo.com.cn/finalpage/2019-02-19/1205840075.PDF)；[赎回实施公告](https://static.cninfo.com.cn/finalpage/2019-10-14/1206979085.PDF)。

两只债券分属沪市和深市，且每条原始记录都同时有 `HS` 与 `SH` 两类价格；两类路径分别命中回售与赎回公告。这排除了把后缀当作交易所标识的解释。该结论只确认五条字段的业务角色，不外推为两类事件的代码表。

## 全量结构核对及边界

500 条保留记录中，130 条有 `EXECUTE_PRICE_HS`，且这 130 条均有申报期首日和末日；346 条有 `EXECUTE_PRICE_SH`，其中 345 条有执行日。缺少执行日的一条为 113575 东时转债（赎回价格 108，原始执行日为空），作为数据缺失保留，不影响字段角色判断。`HS` 字段覆盖 124 条沪市、6 条深市记录；`SH` 字段覆盖 331 条沪市、15 条深市记录，进一步说明后缀不是交易所代码。

本裁决不解释 `EXECUTE_REASON_HS` / `EXECUTE_REASON_SH` 的具体数值代码，不定案 `NOTICE_DATE_HS` / `NOTICE_DATE_SH` 的公告日选择规则，也不推断执行价格的计息公式、税务扣缴或来源刷新时点。上述事项需要单独证据，不影响本次已确认的字段角色和单位。
