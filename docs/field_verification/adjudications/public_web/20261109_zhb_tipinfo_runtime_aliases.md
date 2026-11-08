# ZHB tipinfo 运行字段的公开网页核验

核验日期：2026-11-09。

通达信官方[批量获取实时行情快照接口文档](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html)将 `RecentHGDate` 描述为“最近回购预案日”，将 `ZTDate_Recent` 描述为“近 2 年最近涨停板日期”。因此，运行字段 `hg_date` 的标签采用“最近回购预案日”，不再使用容易混淆成实际公告时间的“回购预案公告日”；`zt_date_recent` 明确记为两年范围。

官方接口文档未列出 `RecentHGAmo`。所以本次不把 `hg_amount_yi` 宣称为该公开接口代码的映射。它与原始列 `[20]` 的逐行别名关系由保留包审计确认；“回购预案金额上限”及“亿元”只沿用注册表已有的 TdxW 本地二进制提示 `回购预案:上限%.2f亿元` 证据，并在机器可读裁决中保留该边界。

同一份官方快照文档中与本次相关的字段原文含义为 `RecentHGDate` 最近回购预案日、`ZTDate_Recent` 近 2 年最近涨停板日期。网页只支持字段语义与日期范围，不单独证明 ZHB `tipinfo.dat` 的列号；列号到运行路径的等价性由 2026-10-15 起的本地逐行审计证明。
