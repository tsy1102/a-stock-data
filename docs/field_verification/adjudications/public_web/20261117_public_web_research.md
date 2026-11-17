# 2026-11-17 官方网页核验：Ulist `f11` 与 `f63`

核验时间：2026-11-17 09:44–10:15 +08:00。字段身份按完整来源路径记录；产品页面标签只作提供方佐证，不自动等于接口字段契约。

## Eastmoney Ulist `f11`：涨速候选，仍缺精确路径映射

- 项目采集器 [`capture_http_collectors.py`](../../../../scripts/capture_http_collectors.py) 请求 `https://push2delay.eastmoney.com/api/qt/ulist.np/get`，原样保留返回对象的 `f11`；本次全历史碰撞的精确身份为 `东财-ulist239(np/get)::f11`。项目登记的 `f124` 是行情更新时间戳；当 `f297` 缺失时，本审计按 `f124` 的中国时区日期确认样本日，没有用目录名替代来源实际时间。
- 碰撞报告 [`preopen_all_history_0950/20261117_collision_report.json`](../../20261117/preopen_all_history_0950/20261117_collision_report.json)，SHA-256 `8621ba049737900a708f4fa7edfd7ef7fda666b7ca6e7c8137cda4fd9ae16e44`，含候选 `ulist239.f11 ↔ tencent[80]`（`cc1_25aa1fb7bb4504e28c28ed1e5bcf386c4b576891bf95217f17af9b2e6c09e3bc`）。7 个来源日期确认的交易日、140 对样本中有 122 对信息样本；80 对精确相等，81 对差值不超过 0.01，99 对不超过 0.05，115 对不超过 0.1。Pearson 为 0.987，Spearman 为 0.9721。逐股逐日值、原始时间戳和 raw 哈希见 [`research/20261117_ulist239_f11_tencent_candidate_audit.csv`](../../research/20261117_ulist239_f11_tencent_candidate_audit.csv)，SHA-256 `b598b005aaf8815118ba2b41d038edf4a5a93943b0f39039d1818be149e56d8f`。
- 样本时间并非完全同步：绝对时间差中位数 1,294 秒、范围 0–2,460 秒；时间戳相差不超过 300 秒的 59 对中，54 对精确相等、55 对差值不超过 0.01。两对相反方向值来自约 40 分钟时间差的 11 月 2 日样本；另有零值与非零值差异。近似关系支持同类短周期涨速假设，但不能把全部误差都归为异步或舍入。
- 东方财富终端官方 FAQ 第 21 问称，列表默认“涨速”为 3 分钟涨速，并允许选择 1–5 分钟区间：[东方财富终端常见问题](https://emdesk.eastmoney.com/pc_activity/pages/viptrade/pages/answer.html)。东方财富涨停板页面也显示“涨速(%)”；其页面脚本将该列绑定到 `zs`，提示为“三分钟涨跌幅”，页面行读取 `zs`，而未将其标为 `f11`：[涨停板行情页](https://quote.eastmoney.com/ztb/)、[该页官方前端脚本](https://quote.eastmoney.com/ztb/newstatic/build/index.js)。在检查到的脚本中没有 `f11` 字符串；其中两条 `ulist.np/get` 查询的字段列表也都没有请求 `f11`。这确认东方财富产品里存在该标签与时间窗，但没有证明 Ulist 响应 `f11` 就是该列表字段。
- 腾讯注册表路径 `腾讯(qt.gtimg)::[80]` 已标为“涨速（%）”。这为跨源候选提供有力参照，但 Ulist `f11` 当前仅为 L4，精确值并非全部相等；不能据此登记跨源同义映射。11 月 17 日开盘前 Eastmoney 接口因既有 `ip_banned` 熔断在请求前拦截（`attempts=0`），没有本日新的 Ulist 值可与官网行情页同日对照。

**结论：**`涨速（%）` 是强候选解释；具体 Ulist `f11` 的官方标签映射及其时间窗尚未确认，因此结果为 `inconclusive`，候选转为 `needs_external_evidence`，字段仍保持 `unverified`。可退出待核的证据是：Eastmoney 正式接口材料/页面脚本明确把 `ulist.np/get` 响应路径 `f11` 映射到涨速标签；或取得同一来源日期、同一交易阶段的 Ulist `f11` 与东方财富有标签页面值，核对全部可比样本并报告反例。

## Eastmoney Ulist `f63`：资金流相关线索，暂不能释义

- 逐值审计 [`research/20261117_ulist239_f63_recent_window_audit.csv`](../../research/20261117_ulist239_f63_recent_window_audit.csv)，SHA-256 `3a57f249ac549200d1d4e00e3fdaafb41d968763532d8f24f80c1e9e24281772`，覆盖 2026-11-06、11-09、11-10 共 60 个股票样本（20 只股票，`f297` 与目录目标数据日一致）。`f63` 60/60 为正数；与成交额 `f6` 同尺度计算的比例范围为 0.178831%–10.274375%，中位数 2.755442%。该比例仅是诊断值，不确认 `f63` 单位或业务含义。对照同日 Eastmoney `em_fund_flow` 原始路径 `f135–f149`，60 条记录没有一条与 `f63` 精确相等。
- 2026-11-10 东方财富个股资金流页面显示贵州茅台主力净流入 9,923.09 万元；同日 Ulist `f62=99,230,912`，换算为万元后落在页面两位小数显示精度内。页面的超大单、大单、中单、小单值也与 Ulist 对应净额路径相符；`f63=84,885,292` 不等于该页面显示的这些指标。[东方财富贵州茅台资金流页面](https://data.eastmoney.com/zjlx/600519.html)。该页面核验支持 `f62` 及已知分档路径，不能据此把 `f63` 命名为另一个资金流口径。

**结论：**`东财-ulist239(np/get)::f63` 仍为 `unverified`，没有足够证据选定流入额、净额、比例或其他替代释义；不更新主字典、不建立映射。需要找到 Eastmoney 对该响应键的正式定义，或从另一官方页面/端点取得能区分上述解释的完整同日样本。
