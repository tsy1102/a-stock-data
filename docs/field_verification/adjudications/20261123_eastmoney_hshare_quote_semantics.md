# 东方财富 H 股关联报价字段来源内实证（2026-11-23）

## 裁决范围

仅裁决以下完整来源身份，不把同编号字段语义推广到其他接口：

- `东财-push2(stock/get)::f250` → **H 股上一香港交易日收盘价**，单位 **HKD/股**。
- `东财-ulist239(np/get)::f185` → **H 股上一香港交易日收盘价**，单位 **HKD/股**。
- `东财-ulist239(np/get)::f186` → **H 股最新成交/行情价**，单位 **HKD/股**；收盘后的快照等于当日收盘价。
- `东财-ulist239(np/get)::f187` → **H 股当日涨跌幅**，单位 **%**；在本批收盘样本中按 `(f186 / f185 - 1) × 100` 四舍五入到两位小数。

字段样本位于东方财富对农业银行 A 股 `601288` 与 H 股 `01288` 的关联记录。HKEX 官方双重上市清单确认这两个代码属于同一农业银行发行人。结论仅确认这四条精确 Eastmoney 路径；不外推其他 A+H 公司、同源其他接口或同编号字段。

## 留存样本与日期锚

只读取 `MIN_CAPTURE_DATE=2026-10-15` 之后的留存 raw。15 个 Push2 非空观测跨 15 个数据目录；逐行已验证 Push2 `f86` 时间戳均解码为目录数据日。Ulist 有效观测为 9 日，逐行已验证 `f124` 时间戳均解码为目录数据日；存在的 `f297` 均与该日一致。日期沿同一证券、同一原始响应行继承，符合现行 `row_timestamp_witnesses`；目录名本身不替代来源日期。

这里分开“记录观测日”和“价格代表的交易日”：例如 Push2 `2026-11-19` 行的 `f86` 是当日 15:26:26，但 `f250=6.865` 对应 HKEX `2026-11-18` 收盘；当前行日期由 `f86` 定，字段内容所指前一港股交易日由 HKEX 日历及逐日收盘表确认。

样本中：

- Push2 `f250` 在 15/15 行等于该日之前最近一个 HKEX 交易日的收盘价。
- Ulist `f185` 在 9/9 行等于同一前一港股交易日收盘价；它与同日 Push2 `f250` 9/9 完全一致。
- Ulist `f186` 在 9/9 行等于当日港股收盘价。
- Ulist `f187` 在 9/9 行都等于按 `f186/f185` 计算并四舍五入到两位小数的涨跌幅。
- 非空样本中均无反例。详细数值、逐日港股交易日、原始响应文件 SHA-256 及逐项布尔核对见[逐行 CSV](../research/20261123_eastmoney_hshare_quote_samples.csv)。

## 公开证据

- HKEX 双重上市名单将 Agricultural Bank of China 的香港代码 `01288` 与上海代码 `601288` 列在同一公司行：[HKEX 名单 PDF](https://www.hkex.com.hk/-/media/HKEX-Market/Services/Market-Data-Services/Real-Time-Data-Services/Market-Data-Promotions/Marketing-Programmes-on-Securities-Market-Data/Mainland-Market-Data-Collaboration-Programme/Market-Data-Collaboration-Stock-List--SSE-%2820180720%29.pdf?la=en)。
- HKEX 官方 2026 假期通告列明 `2026-10-19` 香港证券市场休市，因此 `2026-10-20` 的上一港股交易日为 `2026-10-16`：[HKEX 2026 市场假期通告](https://www.hkex.com.hk/-/media/HKEX-Market/Services/Circulars-and-Notices/Participant-and-Members-Circulars/SEHK/2025/cc_SEHK_CT_075_2025.pdf)。
- [Cibo 农业银行 01288 历史行情页](https://cibo.hk/zh-CN/quote-01288.html)列出逐日 HKD 收盘价，并说明来源为 HKEX Daily Quotations、每个交易日 20:00 后更新。本证据以该公开表的逐日收盘值作为 HKEX 行情交叉核对，不把第三方字段名当作 Eastmoney 字段契约。
- 东方财富官方 Ulist 前端对 H 股关联价格使用 `f186` 及其显示精度 `f190`，并同时使用 `f187`；细节与脚本 SHA-256 见[既有 `f190` 来源契约核验](20261118_ulist239_f190_precision_contract.md)。东方财富官方农业银行行情页可见“最新价、昨收、涨跌幅”等业务角色：[东方财富 01288 行情页](https://quote.eastmoney.com/hk/01288.html)。

## 映射纠正

旧 `2026-09-24` hub 复议把缺少语义定义的数值候选扩展为传递闭包，将现价、涨幅、溢价/比价、关联 H 股代码和名称等异义路径合并成 `same_number_same_meaning`。本轮用同一 601288 的有效来源日期样本复算活动边：凡能得到非空同日值且在至少一天出现不等值的精确边，均从活动矩阵撤回；仅双方当前均为空/缺失且无有效可比值的边不据此声称已证伪，保留待核。逐边命中、反例与无信息边见[活动边审计 CSV](../research/20261123_eastmoney_hshare_mapping_edge_audit.csv)。

正确的 `push2.f250 ↔ ulist239.f185` 关系保留并由本轮 9/9 同日值和 HKEX 前收序列复核；`push2_full.f250` 的历史映射按原身份保留，不据 `push2` 自动推导其字段契约。被撤关系和原命中摘要见[结构化撤回清单](20261123_eastmoney_hshare_mapping_withdrawal.json)。

## 限制

有效样本只覆盖农业银行一个 A+H 发行人；因此字段释义依赖明确的行情角色、两组同源日期锚、官网代码映射及 15/9 个逐日公开收盘实证。它证明不了其他发行人的换算、港币显示精度变化、所有 `f250` 缺失情况或旧版 `push2_full` 未留存快照的当前行为。当前交易日继续由记录时间戳确认，前一香港交易日由香港交易日历和报价历史确认，两种日期不可混为一谈。
