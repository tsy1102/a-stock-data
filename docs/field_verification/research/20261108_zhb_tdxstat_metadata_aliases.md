# ZHB tdxstat 元数据与月涨幅别名核验

核验日期：2026-11-08  
数据保留下限：2026-10-15  
证据类型：同一 ZHB 来源内的路径别名；不构成跨来源独立验证

## 1. 样本范围与方法

只读取路径日期不早于 `20261015` 且 `raw_zhb.json` 中 `zhb_date` 不早于该保留下限的采集记录。共检查 16 份采集 JSON，覆盖 11 个 ZHB 数据日期：

`20261016`、`20261019`、`20261020`、`20261023`、`20261027`、`20261028`、`20261030`、`20261102`、`20261103`、`20261104`、`20261106`。

按 `(ZHB 数据日期, 股票代码)` 去重后，每个待核路径均有 220 组有效记录。原始采集行数为 320，是因为部分数据日期有重复采集；重复行逐项一致，没有重复记录冲突。比较使用原始解析结果，不做数值舍入或模糊匹配。

## 2. 别名对照

| 待核来源路径 | 已验证同源锚路径 | 去重样本 | 不一致 | 裁定 |
|---|---|---:|---:|---|
| `ZHB-tdxstat::code` | `ZHB-tdxstat::stat.code` | 220 | 0 | 同源别名 |
| `ZHB-tdxstat::date` | `ZHB-tdxstat::stat.date` | 220 | 0 | 同源别名 |
| `ZHB-tdxstat::market` | `ZHB-tdxstat::stat.market` | 220 | 0 | 同源别名 |
| `ZHB-tdxstat2::code` | `ZHB-tdxstat2::stat2.code` | 220 | 0 | 同源别名 |
| `ZHB-tdxstat2::date` | `ZHB-tdxstat2::stat2.date` | 220 | 0 | 同源别名 |
| `ZHB-tdxstat2::market` | `ZHB-tdxstat2::stat2.market` | 220 | 0 | 同源别名 |
| `ZHB-tdxstat2::change_mtd` | `ZHB-tdxstat2::stat2.change_mtd` | 220 | 0 | 同源别名 |

以上锚路径在核验前已是注册表中的 `verified` 字段。前六项只继承锚字段的代码、统计日期和市场标签；不据此推断市场数字编码。`change_mtd` 只继承锚字段“月初至今涨跌幅”及 `%` 单位，不推断计算公式、复权基准或窗口端点。

## 3. 上游文档边界

通达信 `get_more_info_batch` 文档说明股票代码列表和外层证券代码键，并列出 `HqDate` 为行情日期；通达信公式函数文档将 `DYNAINFO(69)` 定义为月初至今涨幅。它们支持代码、日期和月涨幅的一般语义，但没有直接说明本项目的 `raw_zhb.json` 路径名。路径关系因此依据已验证同源锚与上述留存样本，不声称由上游文档直接给出了 ZHB 字段映射。

- [通达信 `get_more_info_batch` 文档](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html)
- [通达信公式函数列表（DYNAINFO(69)）](https://help.tdx.com.cn/gspt/docs/markdown/redword/functionlist.html)

