# Ulist239 `f59` 历史释义撤回

## 裁决

只处理完整来源路径 `东财-ulist239(np/get)::f59`。原始 Ulist 响应持续返回该字段，因此路径有效；现有证据推翻了历史“收盘价/最新价”标签，但尚不能解释 `f59` 的真实含义。注册表状态从 `conflict / status_conflict` 调整为 `unverified / historical_meaning_withdrawn_unresolved`，清空含义和单位，保留旧 `reference_evidence` 供审计，并继续列入未知字段队列。不把其他接口的同号 `f59` 合并进本裁决，也不创建跨源映射。

## 日期合格样本

按项目当前保留边界及来源日期规则，使用 2026-11-05、11-06、11-09、11-10、11-17、11-18 六个 Ulist 来源数据日。每个日期均有 20 只股票完整记录，`f297` 与目录目标交易日一致，市场处于收盘阶段；共 120 个同股同日样本。逐行值、来源日期和原始文件哈希见[结构化样本 CSV](../research/20261119_ulist239_f59_close_claim_samples.csv)。CSV SHA-256（UTF-8/LF）为 `57baaa5370994ffefcf948c18c29fbe4815aae6e0861565301aa7511a7a12707`。

- `f59 == f2`：0/120；`f2` 是注册表已验证的 Ulist 最新价路径。
- 对 20 只股票逐只比较：`f59` 在六个来源日均不变（20/20），`f2` 均发生变化（20/20）。
- 2026-11-02 至 11-04 的记录不纳入正式比较：其 `f297` 为 Unix 秒形态，不符合当前已验证的 `YYYYMMDD` 日期口径。

这些样本足以否定“`f59` 是当前/最新收盘价”，但不能据此推出另一个业务语义或单位。

## 外部字段资料核查

2026-11-19 检查东方财富行情中心公开前端 bundle `https://quote.eastmoney.com/center/static/build/index.js`（HTTP 200，673,734 字节；SHA-256 `1224df21d3aa5cef8659acd9293b1f44047e0398080e6bce72fe881d755dc59b`）。bundle 可确认页面调用 `api/qt/ulist.np/get`，但在所检查的构建文件中没有发现 Ulist `np/get::f59` 的字段释义；唯一出现的 `f59` 位于 K 线字段参数列表。这个负向检索不能证明字段无含义，也不能把不同接口的同号字段视作同一字段。

第三方 efinance 将 `get_latest_quote` 路由到 Ulist，但其常用行情字段映射没有提供 Ulist `f59` 的定义，因此没有作为语义定案依据：[调用路径](https://github.com/Micro-sheep/efinance/blob/main/efinance/common/getter.py#L2218-L2261)、[字段配置](https://github.com/Micro-sheep/efinance/blob/main/efinance/common/config.py#L757-L797)。

## 注册表与视图

不覆写只读的历史来源参考表、其镜像或既往报告；它们保留旧标签作为审计记录。现行注册表清空该字段的语义与单位，新增本次状态纠错证据，并将精确来源路径继续保留在未知队列。没有可依据的新释义、单位或同义路径可写入。
