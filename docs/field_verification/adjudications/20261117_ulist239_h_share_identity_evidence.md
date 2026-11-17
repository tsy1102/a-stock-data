# Ulist239 H 股对应证券字段来源内实证

复核日期：2026-11-17（Asia/Shanghai）  
精确来源：`东财-ulist239(np/get)`，接口 `https://push2delay.eastmoney.com/api/qt/ulist.np/get`  
目标路径：`f191`、`f192`、`f193`。本记录只处理该接口；Push2 `stock/get` 中同号字段不属于本决定。

## 结论

将 Ulist239 的三个配套字段登记为：

| 完整来源路径 | 规范名 | 来源内含义 | 单位 |
|---|---|---|---|
| `东财-ulist239(np/get)::f191` | `h_share_code` | A 股记录所关联 H 股证券的代码 | — |
| `东财-ulist239(np/get)::f192` | `h_share_market_id` | 对应 H 股证券在东方财富 `secid` 中使用的市场编号；当前已观察的 `116` 对应港股 | — |
| `东财-ulist239(np/get)::f193` | `h_share_name` | A 股记录所关联 H 股证券的简称 | — |

这修正了旧的 `f192 = A+H 双上市布尔标记`解释。`116` 是市场编号值，不是布尔值。结论只确认上述三个精确来源路径，以及当前样本中 `601288 → 01288 / 116 / 农业银行` 这一配对；不提供其他市场编号的完整码表，不给 Push2 同号路径赋予这些含义，也不建立跨源映射。

## 官方资料及直接核验

1. **HKEX 官方双重上市名册**：列出中国农业银行 H 股 `01288` 和 SSE A 股 `601288`。该名册证明样本中的两只证券属于同一双重上市公司。来源：[HKEX SSE 双重上市名单（PDF）](https://www.hkex.com.hk/-/media/HKEX-Market/Services/Market-Data-Services/Real-Time-Data-Services/Market-Data-Promotions/Marketing-Programmes-on-Securities-Market-Data/Mainland-Market-Data-Collaboration-Programme/MarketDataCollaborationStockListSSE20181116.pdf?la=zh-HK)，表格第 1 行。
2. **HKEX 官方发行人公告**：农业银行 2026 年第三季度报告标示港股代码 `1288`，并列出 A 股代码 `601288`。[HKEX News 公告 PDF](https://www.hkexnews.hk/listedco/listconews/sehk/2026/1030/2026103001999_c.pdf)。
3. **东方财富官方 H 股页面**：页面标题为“农业银行(01288)最新价格”。[东方财富 01288 行情页](https://quote.eastmoney.com/hk/01288.html)。东方财富发行人公告也把 H 类股份标记为“于香港联交所上市”，并给出证券代码 `01288`：[农业银行月报公告](https://data.eastmoney.com/notices/detail/601288/AN202607031826697768.html)。
4. **东方财富行情 API 的市场编号核验**：2026-11-17 13:05（Asia/Shanghai）对官方 `stock/get` 只读查询 `secid=116.01288`，请求 `f57,f58`，响应为 `{"f57":"01288","f58":"农业银行"}`。可复核链接：[东方财富 stock/get 查询](https://push2.eastmoney.com/api/qt/stock/get?secid=116.01288&fields=f57%2Cf58&invt=2&fltt=2)。这确认 `116` 作为 `secid` 市场前缀时解析到农业银行 H 股；`f192` 到字段角色的判断来自与 Ulist 同记录 `f191/f193` 配套值及下述全量样本，而非将其他接口的短字段号直接迁移过来。

本轮没有找到东方财富官方发布的 Ulist239 `f191/f192/f193` 字段字典。因此本决定属于**来源内实证**，不是正式字段 Schema 契约。第三方字段表仅作为搜索线索，没有用作最终裁决依据。

## 留存样本与逐项核对

仅使用 2026-10-15 保留边界之后的成功归档。7 个归档的 Ulist239 采集状态均为 `ok`，每份预期及实际收齐 20 只证券。每次的 `601288` 记录都返回相同配套值：

| 采集归档目录 / `meta.data_date` | Ulist `f297` | `f191` | `f192` | `f193` | `raw_ulist239.json` SHA-256 |
|---|---:|---|---:|---|---|
| `20261102` | 未返回 | `01288` | `116` | `农业银行` | `8DF028EDBCC2725EDF0280D741E6B146DC777532DEC2D7C368EA655431D22718` |
| `20261103` | 未返回 | `01288` | `116` | `农业银行` | `AD26B1F24B3A74B95647EF97FA89E41284932FBA38936C4A4746F331850AC034` |
| `20261104` | 未返回 | `01288` | `116` | `农业银行` | `A6E6706884616BC349F29440A9708026BAB9F42F985A19639BE4129050B3B79D` |
| `20261105` | `20261105` | `01288` | `116` | `农业银行` | `10A6F6EBA28A406799CCF73D366482CE23913234DA33020C752858EA9140CF68` |
| `20261106` | `20261106` | `01288` | `116` | `农业银行` | `FD4A54C15FC2AECD4EDADBAB8E50BFED75F610E989490D33CCB16676049FEAC2` |
| `20261109` | `20261109` | `01288` | `116` | `农业银行` | `7D8BFC4B6D12E4D8BCE1AA1CB1E93B5FBE6ABBF4B3B05126887775C9838AFA4C` |
| `20261110` | `20261110` | `01288` | `116` | `农业银行` | `386416EAAF7A3E4146E5679F47E86DC8F6EC08DD117BB3C6D4F2E62845A396C0` |

范围说明：前 3 份 Ulist 数据没有 `f297`；不得用目录名或尚未定义的 `f124` 代替来源实际日期。此处使用这些文件只核对静态证券身份，不将其当作 7 个独立的行情数据日。后 4 份的 `f297` 与各自归档目标数据日一致。

在上述 7 份、共 140 条完整记录中，非占位组合只出现 7 次，全部属于同一证券 `601288` 且全部与官方 `601288 ↔ 01288` 配对吻合。其余 133 条均为 `f191="-"`、`f192=-1`、`f193="-"`；这些是未提供对应证券信息的占位样本，按不可比较项排除，不能把 `-1` 当作一个市场编号，也不作为反例。故每个目标字段的实证样本为 7 条可比记录、7 条吻合、0 条反例、1 只独立正样本，另排除 133 条占位记录。重复采集提高了持续性证据，但不增加独立证券数量。

2026-11-17 本轮采集没有得到新的 Ulist239 响应：该来源被此前的 `ip_banned` 熔断在发出请求前拦截。新一轮没有把午间归档日或其他来源数据伪装成 Ulist 来源数据日；上述 7 份是当前能用于该身份核验的成功归档。

## 可复核归档路径

```text
docs/field_verification/20261102/raw_ulist239.json
docs/field_verification/20261103/raw_ulist239.json
docs/field_verification/20261104/raw_ulist239.json
docs/field_verification/20261105/raw_ulist239.json
docs/field_verification/20261106/raw_ulist239.json
docs/field_verification/20261109/raw_ulist239.json
docs/field_verification/20261110/raw_ulist239.json
```

## 裁决边界

- 结论适用完整身份 `东财-ulist239(np/get)::f191/f192/f193`，不是裸 `f191/f192/f193`。
- `f192` 的旧布尔标记解释不成立；市场编号字段角色现由对应 H 股证券及官方接口 `secid` 交叉验证。
- 样本中只有一只实际出现 H 股配对值的股票，因此不据此宣称已经覆盖所有 H 股代码、市场编号或退市/更名边界。
- 不新增 `mappings`；Push2 `f191=委比`、`f192=委差` 等来源内语义保持不变。
