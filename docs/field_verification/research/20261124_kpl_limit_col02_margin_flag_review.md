# 开盘啦涨停明细 `col_02` 两融标记假设复核

审计日期：2026-11-24。字段身份为 `开盘啦(kpl)::kpl.raw_columns.col_02`，属于个股涨停明细 `DailyLimitPerformance`；它与 `market_sources.kpl_plate_strength.raw_columns.col_02` 是不同接口路径，后者已确认是板块强度，不可移用其释义。本轮仅检验“`col_02` 是否为全市场统一的两融标的标记”，未运行采集器。

## 日期合格样本

读取保留边界 `2026-10-15` 之后的 22 个 KPL 原始文件：其中 21 个含有效数据，共 1,259 条记录；`col_02` 有效 0/1 值 1,229 条（0 为 590 条、1 为 639 条），另 30 条缺值。覆盖 761 只证券，所有有值证券在其保留期重复观测中 `col_02` 均保持不变。原始输入文件及 SHA-256 见[采集文件清单](20261124_kpl_col02_capture_manifest.csv)。

KPL 同行 `zt_time` 是涨停事件时间，不等同接口更新时间；已有[逐行日期审计](20261123_kpl_row_timestamp_date_anchor_audit.md)确认其时间日期与记录交易日一致。本轮仅在 `zt_time` 对应的股票交易日上比对交易所两融状态，不把自然日或采集目录单独作为日期证据。

## 沪深季度名单：强线索但不完整

上交所 2026 年第三季度名单自 2026-10-19 生效，附件明确包含 1,000 只股票；注册制首次公开发行股票不适用该定期名单。深交所同日生效的附件包含 1,200 只非注册制股票，注册制首次公开发行股票及存托凭证按上市首日起适用规则。

按生效后 20 个交易日、1,168 条 KPL 行及 730 只沪深股票，与两所**季度定期名单中的股票清单**逐股比较：

| 市场 | 样本股票 | `col_02=1` 且在季度名单 | `col_02=0` 且不在季度名单 | `col_02=1` 但不在季度名单 | `col_02=0` 却在季度名单 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 深交所 | 380 | 166 | 155 | 59 | 0 |
| 上交所 | 339 | 140 | 148 | 51 | 0 |

沪深样本中未发现季度名单内的股票被 `col_02=0` 标记，形成了“可能与两融资格有关”的强线索。但 110 只 `col_02=1` 且不在季度名单的股票不能一概视为错误，也不能在没有逐股核对上市批次及生效规则前，全部归因为注册制例外。逐股清单和稳定性统计见[沪深名单审计 CSV](20261124_kpl_col02_exchange_membership_audit.csv)。

## 北交所同日官方反例

对 KPL 样本中 13 只北交所股票，按每条 KPL `zt_time` 的同一交易日查询北交所官方“标的股票信息”页面所用接口 `/rzrqbdzqController/infoResult.do`。官方返回列明确区分“融资标的”（`rzbd`）、“融券标的”（`rqbd`）、“当日可融资”（`drkrz`）和“当日可融券”（`drkrq`）。13/13 条均返回四项为 `Y`，但 KPL `col_02` 为 0 的有 11 条、为 1 的有 2 条，构成该两融标记假设的直接反例。逐条数据见[北交所同日审计 CSV](20261124_kpl_col02_bse_same_date_audit.csv)。

`col_02` 因此不能被定义为全市场统一的融资/融券标的资格标记。沪深名单呈现的关系可能是 KPL 对沪深市场的局部语义、不同市场标记口径，或样本区间的巧合；现有证据不能区分这些解释。

## 裁决

- 精确路径 `开盘啦(kpl)::kpl.raw_columns.col_02` 保持 `unverified`；不更新主字典、registry、跨源映射或采集路由。
- 拒绝“跨市场统一两融标的标记”这一具体假设，理由是北交所同日 13/13 官方反例；不外推为 `col_02` 在沪深局部语义也已证伪。
- 后续优先寻找开盘啦官方接口的列级说明，或取得同一批次沪深/北交所统一可比的状态定义与足以区分局部含义的样本。若找不到，不以相关性或季度名单的单向吻合定案。

## 来源与证据摘要

- 上交所[2026 年第三季度两融标的调整通知](https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/specific/margin/c/c_20261016_10834885.shtml)及其[股票名单附件](https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/specific/margin/c/c_20261016_10834885/files/4fa11ac0f0b94a5887414a9158adc1a8.docx)。通知说明股票名单为 1,000 只、不适用于注册制首次公开发行股票，自 2026-10-19 施行。附件 SHA-256：`E3FADDBC37AEEA43CF4016C4C17BABC641E5E5F295369A3B2B63B98CC93980BC`。
- 深交所[2026 年第三季度两融标的调整通知](https://www.szse.cn/www/disclosure/margin/business/t20261016_623333.html)及[股票名单附件](https://docs.static.szse.cn/www/disclosure/margin/business/W020261016550297828445.pdf)。附件 1 为 1,200 只股票且注明不含注册制股票。PDF SHA-256：`66BD3B6C16D409A9599D6153FC9BC25265DBB1EEA3BFDE5A4A9B5B42638CB246`。
- 上交所[融资融券交易实施细则](https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/specific/margin/c/c_20250616_10782015.shtml)第 24 条及深交所上述通知，说明注册制 IPO 标的的首日适用规则；这解释名单并非两融资格完整全集，但不能替代对 110 个未列证券逐一核验。
- 北交所[标的股票信息](https://www.bse.cn/disclosure/rzrq_bdzq_list.html)、该页加载的[官方查询脚本](https://www.bse.cn/template/6/bluewise/_files/js/disclosure/rzrq_information/rzrq_bdzq_list.min.js)和[标的证券信息技术规范](https://www.bse.cn/uploads/6/file/public/202209/20220902201701_kas8vw9r25.pdf)。同日结果 CSV SHA-256：`8CFAFFB5924F5B07E2D680D97EFC921D59758A4D021F99273762452104CBC53A`。
- 沪深逐股审计 CSV SHA-256：`7395030F827FAC1BD137FD6DE45A99A301FF1A546A01D42F3C55572B64DB5B33`；KPL 原始文件清单 SHA-256：`03C772C9AA314FCD8FEE8C3A4E4EC4950DC3652CCE6BFFE907D507073A6218EE`。
