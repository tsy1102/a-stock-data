# TDX 快照日期字段网页核验

核验日期：2026-11-09。

通达信官方[批量获取实时行情快照接口文档](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html)将日期字段列为字符串，并逐项说明 `DTDate_Recent`、`NoticeDate_Recent`、`RecentDZDate`、`RecentGGJYDate`、`RecentHGDate`、`RecentIncentDate`、`RecentReleaseDate`、`ReportDate`、`StopJYDate_Recent`、`TopDate_Recent` 和 `ZTDate_Recent` 的业务含义。文档对 `TopDate_Recent`、`ZTDate_Recent`、`DTDate_Recent` 明确标出近两年范围。

该文档没有给这些日期值的字符串格式。故注册表保留“日期字符串（官方文档未注明格式）”，不根据字段名猜成 `YYYYMMDD`。本次只登记官方接口契约；项目现有代码未调用这些 TDX 字段名，也没有把它们与 ZHB 历史列或采集日期建立映射。
