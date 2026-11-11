# ZHB tipinfo 日期运行别名核验（2026-11-10）

## 裁决范围

本次只处理解析器运行键 `forecast_date_recent` 与 `equity_incentive_date`。它们分别直接复制 ZHB-tipinfo 原始列 `[11]`、`[21]`；不变换日期、不处理枚举、不创建跨源映射。

## 保留样本审计

- 数据保留起点：`2026-10-15`；日期化 ZHB 包：15 个，覆盖 `20261015` 至 `20261106`，详见 [`20261110_zhb_tipinfo_date_alias_audit.csv`](20261110_zhb_tipinfo_date_alias_audit.csv)。
- 原始股票行：84,815；两条别名均各有 84,815 个逐行配对，重复代码 0、值不匹配 0。
- `[11]` 非空 1,454 行；所有非空值均为 8 位日期串。`[21]` 非空 22,248 行；所有非空值均为 8 位日期串。
- 审计使用项目实际 `ZhbData.tip_info` 解析结果对照同一压缩包内的原始列，不做数值容差或日期归一化。

## 公开语义核验

- 通达信官方 `get_more_info_batch` 字段表将 `NoticeDate_Recent` 定义为“最近业绩预告日”，将 `RecentIncentDate` 定义为“最近股权激励预案日”。这与已核验的 ZHB 原始列说明一致。官方文档仅作语义佐证；本裁决不声称 ZHB 原始文件字段与另一份 TDX API 响应逐值映射。
- 代表样本：立讯精密 `002475` 在 `zhb_20261106.zip` 的 `[11]` 为 `20261030`；东方财富个股日历/业绩预告页列出 2026-10-30 预告，业绩大全明细也列出公告日 2026-10-30。
- 代表样本：晶华微 `688130` 在同一 ZHB 包的 `[21]` 为 `20240920`；巨潮资讯披露的文件标题为“2024 年限制性股票激励计划（草案）摘要公告”，落款公告日为 2024-09-20。

## 定案结论

`forecast_date_recent` 定义为“最新业绩预告发布日”，同源锚为 `ZHB-tipinfo::[11]`；`equity_incentive_date` 定义为“股权激励预案/草案公告日”，同源锚为 `ZHB-tipinfo::[21]`。单位沿用原始锚字段的空值，不从字符串格式推导单位。均按来源内别名定案，不新增 `mappings`。

尚未定案：`forecast_type` 对应 `[12]` 的枚举含义/代码表；`suspend_major_event_date` 与 `[7]` 的精确关系；`[17]`、`[18]` 的全空状态背后的协议语义。它们不因本次别名定案而自动关闭。

## 证据链接

- [通达信 TdxQuant 官方扩展信息字段文档](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html)（2026-11-10 核验）。
- [东方财富立讯精密个股日历](https://data.eastmoney.com/stockcalendar/002475.html) 与 [业绩大全](https://datapc.eastmoney.com/emdatacenter/profit/report?code=002475)（字段值/公告日样本）。
- [巨潮资讯晶华微 2024 年限制性股票激励计划（草案）摘要公告](https://static.cninfo.com.cn/finalpage/2024-09-20/1221246300.PDF)。

正式决定：[`20261110_zhb_tipinfo_date_aliases.json`](20261110_zhb_tipinfo_date_aliases.json)。
