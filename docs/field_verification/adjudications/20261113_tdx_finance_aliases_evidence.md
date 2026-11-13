# TDX 财务输出别名 `zhuyinglyrun`、`ipodate`、`updateddate` 实证定案

核验日期：2026-11-13。裁决只针对注册表中的三个完整身份：`TDX(双命名源)::zhuyinglyrun`、`TDX(双命名源)::ipodate`、`TDX(双命名源)::updateddate`。采集 JSON 的实际字段位置均为 `stocks.<code>.finance_info.<field>`。

## 路径还原与结论

`capture_tcp_collectors.py::collect_tdx` 通过 `tdx_get_finance_info` 把 TDX 适配器结果写入 `finance_info`。主适配器 [`core/eltdx_adapter.py`](../../../core/eltdx_adapter.py) 的 `_FIN_MAP` 将 `zhu_ying_li_run_raw_float` 映射为 `zhuyinglyrun`，比例 `qy2jiao` 把原始千元值乘 10,000，转换成角。该精确字段不是拼写相似的 `zhuyinglirun`（注册表已定案为主营业务利润），也不是 `yingyelirun`（营业利润）。

同一 ELTDX 适配器直接从记录对象写出 `updated_date`、`ipo_date`，再按代码规则生成去下划线兼容键 `updateddate`、`ipodate`。两条规范字段已由 2026-11-11 的 TDX 0x0010 逐字段契约核为“财报更新日期”和“上市日期”；`updated_date` 不代表采集自然日、采集目录目标数据日或报告期末。对于双适配器输出格式，主 ELTDX 适配器序列化为 `YYYY-MM-DD` 字符串；项目锁定 Easy-TDX 兜底解析器将两个原始日期保留为 `YYYYMMDD` 整数，兼容层生成的别名沿用相同值。因此别名单位同时记录两种适配器格式。本次未调用 Easy-TDX 兜底；其格式判断来自锁定 wheel 的解析模型和适配器代码。

## 保留期路径样本

使用采集目录 `data_date=20261112`、运行日 `20261113` 的保留样本；没有运行任何采集。TDX 与 ELTDX 分别在 `2026-11-12 23:17:30` 和 `2026-11-12 23:17:36` 完成采集。20 只股票逐行核验：

- `TDX.finance_info.zhuyinglyrun` 与 `ELTDX.finance_batch[0].zhu_ying_li_run_raw_float × 10,000` **20/20 精确相等**，最大角差为 0。
- `finance_info.ipodate` 与 `finance_info.ipo_date` **20/20 完全相同**；`finance_info.updateddate` 与 `finance_info.updated_date` **20/20 完全相同**。本批是同一输出对象内的别名核验，不把同一股票或同一日期重复计为独立来源。

逐股原值、转换值、日期值和采集数据日列于[样本 CSV](20261113_tdx_finance_alias_samples.csv)。该目录的 `meta.json` 将运行日与目标数据日分开记录；财务数据的更新日期按股票单独变化，故不将采集时间用作财务报告期。

## 营业成本官方报告锚点

沿用精确原始槽位的四份发行人 2026 年第三季度报告核验。ELTDX v3.3.2 字段说明将 `zhu_ying_li_run_raw_float` 标为“主营利润原始值”，但以下样本实际贴合合并利润表的“营业成本”行；此处保留该标签冲突，不把拼音或上游注释当作实测语义。

| 股票 | ELTDX 原值（千元） | 原值换算元 | 报告“营业成本”（元） | 差值（换算值−报告值） |
|---|---:|---:|---:|---:|
| 贵州茅台 600519 | 13,645,719 | 13,645,719,000 | 13,645,718,932.90 | +67.10 |
| 万华化学 600309 | 155,233,312 | 155,233,312,000 | 155,233,319,413.52 | −7,413.52 |
| 泸州老窖 000568 | 2,399,983.5 | 2,399,983,500 | 2,399,983,662.33 | −162.33 |
| 殷图网联 920508 | 24,220.19921875 | 24,220,199.21875 | 24,220,280.59 | −81.37125 |

四家不同规模发行人的相对误差均低于既有证据采用的 `1×10⁻⁵` 判读上界，最大为 `3.36×10⁻⁶`。残差原样保留，不将所有差异归因为同一种舍入机制。原始四份财报对照见 [`20261111_eltdx_zhu_ying_li_run_empirical_semantics.md`](20261111_eltdx_zhu_ying_li_run_empirical_semantics.md)。

## 裁决边界

1. `TDX(双命名源)::zhuyinglyrun`：财务输出值对应发行人合并利润表“营业成本”；适用输出单位为角，来源槽位单位为千元且转换系数为 10,000。
2. `TDX(双命名源)::ipodate`：`ipo_date` 的无下划线兼容别名，表示上市日期；输出编码随所用适配器而异，分别为 ISO 日期字符串与 `YYYYMMDD` 整数。
3. `TDX(双命名源)::updateddate`：`updated_date` 的无下划线兼容别名，表示财务记录更新日期；它不是自然日、目标交易日、报告期末或公告披露日。
4. 以上只确认精确 TDX 输出路径，不创建跨来源 `mappings`。此前 ELTDX 原始路径的定案不被重写或外推；本次补上其独立 TDX 兼容输出身份。

证据输入 SHA-256：

- `raw_tdx.json`: `3509AC9406AEBC0B85DD7F06A01321D3A9E630F293794D911AAA26C28388F266`
- `raw_eltdx.json`: `C7C466C3E0BF0DE4DC2827A556192CF1EC29E22A48898E6074C61C011EB4DDC5`
- `meta.json`: `661247674E17F5F69917B8D4424304D01F328B24E830AB0C3A86D336574C90F1`
- 样本 CSV: `52208BD1CA7D2A8BBFECCA3FE6C3E946F340A0510E70E900F4857E4A85B5393D`

上游及逐样本来源：

- [ELTDX v3.3.2 7709 财务基础信息字段表](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-%E8%B4%A2%E5%8A%A1%E5%9F%BA%E7%A1%80%E4%BF%A1%E6%81%AF.md#L253-L329)。
- [贵州茅台 2026 年第三季度报告](https://static.cninfo.com.cn/finalpage/2026-10-31/1225649896.PDF)。
- [万华化学 2026 年第三季度报告](https://static.cninfo.com.cn/finalpage/2026-10-27/1225622843.PDF)。
- [泸州老窖 2026 年第三季度报告](https://static.cninfo.com.cn/finalpage/2026-10-30/1225639079.PDF)。
- [殷图网联 2026 年第三季度报告](https://static.cninfo.com.cn/finalpage/2026-10-30/1225649649.PDF)。
- 规范日期路径契约见 [`20261111_tdx_finance_date_fields.md`](20261111_tdx_finance_date_fields.md)；日期别名转换代码见 `core/eltdx_adapter.py::_EltdxAdapter.finance`、`core/tdx_client.py::_EasyTdxAdapter.finance` 与锁定的 Easy-TDX 1.20.8 `FinanceInfo` 模型。
