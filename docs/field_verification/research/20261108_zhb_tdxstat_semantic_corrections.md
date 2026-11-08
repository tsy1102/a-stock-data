# ZHB tdxstat 元数据纠错与同源路径核验

核验日期：2026-11-08
样本保留下限：2026-10-15
裁定范围：修正 `stat.*` 当前字典释义中的历史录入冲突，并核验对应 `full.*` 路径别名

## 1. 发现的问题

`docs/field_source_reference.md` 的逐列协议段（§3.1）和当前 `core/zhb_client.py::_parse_tdxstat` 注释将字段解释为连涨/连跌、前一日涨幅、新股首次开板日、上市连板数及若干日 K 线根数；但其中较新的 `stat.*` 汇总表（§1.1，2026-09-18）把部分同路径记成了连板天数、解禁日期、所属板块数和分钟 K 线涨跌。代码列索引与历史逐列核验相互一致，因此当前注册表应以字段来源路径的原始列契约为准。旧协议表保留作历史记录，本次通过显式元数据更正记录消除其与当前主字典的冲突。

## 2. 语义更正

| ZHB 路径 | 旧注册表释义 | 更正后释义 | 更正依据 |
|---|---|---|---|
| `stat.streak_days` | 连板天数 | 连涨/连跌天数（正值为连涨，负值为连跌） | 原始列 `[5]` 的解析契约；218 组非零连续值与当日涨跌方向全部一致 |
| `stat.change_pct_1d` | 涨跌幅 | T-1 日涨跌幅 | 原始列 `[7]` 的解析契约 |
| `stat.change_pct_2d` | 涨跌幅 | T-2 日涨跌幅 | 原始列 `[8]` 的解析契约 |
| `stat.unseal_date` | 解禁日期 | 新股上市后首次开板日期（上市后首次不再涨停） | 原始列 `[12]` 的解析契约及保留样本、公开发行/交易资料交叉核对 |
| `stat.board_count` | 所属板块数 | 新股上市至首次开板前的连续涨停交易日数（首日开板为 0） | 原始列 `[13]` 的解析契约及保留样本交叉核对 |
| `stat.change_5k_bar` | 5 分钟 K 线涨跌 | 近 5 根 K 线涨跌幅（交易日口径） | 原始列 `[27]` 的解析契约；单位为百分比 |
| `stat.change_10k_bar` | 10 分钟 K 线涨跌 | 近 10 根 K 线涨跌幅（交易日口径） | 原始列 `[29]` 的解析契约；单位为百分比 |

`streak_days` 的方向核验使用 220 个去重股票日样本；218 组同时存在非零连续天数和非零当日涨跌幅，正负方向 218/218 一致，其余 2 组当日涨跌幅为零，不参与方向判断。

`300788` 的保留期记录为 `unseal_date=20190715`、`board_count=6`。深交所新上市证券月报记录其上市日为 2019-07-05；2019-07-15 的公开报道记录其首次打开连续涨停；其首开之前恰有 6 个交易日。中信出版实际限售股解禁日期则为 2022-07-05。因此该 ZHB 日期字段表示新股首次开板日期，不表示限售股解禁日期。相关来源：

- [深交所 2019 年 7 月新上市证券月报](https://docs.static.szse.cn/www/market/periodical/month/W020190801551188546384.html)
- [每日经济新闻：中信出版首次打开一字涨停（2019-07-15）](https://www.nbd.com.cn/articles/2019-07-15/1354052.html)
- [每日经济新闻：中信出版限售股份解禁（2022-07-05）](https://www.nbd.com.cn/articles/2022-06-30/2347004.html)

## 3. 同源别名样本

仅读取路径日期和 `zhb_date` 均不早于 `20261015` 的采集记录。共 16 份采集 JSON，11 个 ZHB 数据日期，按 `(数据日期, 股票代码)` 去重后为 220 组。重复采集行之间无值冲突；原始比较不做舍入或容差匹配。

| 待核路径 | 已验证锚路径 | 可比较股票日 | 非空且相同 | 双空 | 不一致 |
|---|---|---:|---:|---:|---:|
| `ZHB-tdxstat::streak_days` | `ZHB-tdxstat::stat.streak_days` | 220 | 220 | 0 | 0 |
| `ZHB-tdxstat::change_pct_1d` | `ZHB-tdxstat::stat.change_pct_1d` | 220 | 220 | 0 | 0 |
| `ZHB-tdxstat::change_pct_2d` | `ZHB-tdxstat::stat.change_pct_2d` | 220 | 220 | 0 | 0 |
| `ZHB-tdxstat::unseal_date` | `ZHB-tdxstat::stat.unseal_date` | 220 | 66 | 154 | 0 |
| `ZHB-tdxstat::board_count` | `ZHB-tdxstat::stat.board_count` | 220 | 55 | 165 | 0 |
| `ZHB-tdxstat::change_5k_bar` | `ZHB-tdxstat::stat.change_5k_bar` | 220 | 220 | 0 | 0 |
| `ZHB-tdxstat::change_10k_bar` | `ZHB-tdxstat::stat.change_10k_bar` | 220 | 220 | 0 | 0 |
| `ZHB-tdxstat2::ipo_price` | `ZHB-tdxstat2::stat2.ipo_price` | 220 | 220 | 0 | 0 |

这些关系只确认同一 ZHB 数据在合并路径和分组路径中的一致性，不产生跨来源映射。对 `unseal_date` 和 `board_count` 的空值不单独作为字段语义证据；定案依赖非空样本、原始列位置和公开上市/开板资料。

## 4. 公开契约与边界

通达信官方扩展接口列出 `ConZAFDateNum`、`IPO_Price` 等字段，可作连涨指标和发行价的上游语义参考；其文档没有公开上述 ZHB 解析路径之间的别名关系，也不定义 `board_count` 或 `unseal_date` 的 ZHB 列位置。ZHB 源列映射以项目解析器和保留期样本为依据，不把通达信官方字段标签扩大成未经证明的跨源逐值映射。

- [通达信 TdxQuant 扩展字段接口说明](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html)
- [本项目固定版本的 ZHB 列解析契约](https://github.com/tsy1102/a-stock-data/blob/1349365/core/zhb_client.py)
