# Eastmoney IPO `MAIN_BUSINESS` 来源契约核验

复核日期：2026-11-21。

## 裁决

将 `东财-event_dc(IPO发行记录)::ipo_calendar[].MAIN_BUSINESS` 登记为 IPO 发行记录附带的发行人主营业务文字描述，规范名 `ipo_record_main_business_description`，无计量单位。该字段与 `BUSINESS_SCOPE`（经营范围）是不同字段。

边界：`RPTA_APP_IPOAPPLY` 未为该文本单独返回更新时间或有效日期。目录目标数据日和采集自然日不能替代字段有效日；本裁决不把描述解释为 IPO 时点或当前时点的经营状态，也不推断其历史版本或更新机制。

## 官方字段与项目路径

- 东方财富官方新股申购前端脚本 [`xglist.js`](https://data.eastmoney.com/newstatic/js/xg/xglist.js) 的列表请求使用 `reportName: RPTA_APP_IPOAPPLY`，请求列包含 `MAIN_BUSINESS`；`rowattributes` 将 `row.MAIN_BUSINESS` 格式化后用作该行提示文本。该代码把字段精确关联到 IPO 发行记录响应，但没有独立标注其业务有效日。
- 东方财富官方详情脚本 [`xgdetail.js`](https://data.eastmoney.com/newstatic/js/xg/xgdetail.js) 在另一接口 `RPT_HSF9_BASIC_ORGINFO` 中请求 `BUSINESS_SCOPE,MAIN_BUSINESS`，并分别把两键显示为“经营范围”和“主营业务”。这是同一官方提供方的语义佐证，属于不同报表端点，不能据此声称两个端点具有完全相同的更新契约。
- 项目 [`_events.py`](../../../stock_common/sc_datasource/_events.py) 将 `ipo_calendar` 路由到 `RPTA_APP_IPOAPPLY`；数据中心适配器返回行记录后，采集器将其保存到 `raw_event_dc.ipo_calendar[]`。目标路径为 `RPTA_APP_IPOAPPLY response.data[*].MAIN_BUSINESS -> ipo_calendar() -> raw_event_dc.ipo_calendar[].MAIN_BUSINESS`，项目不对该值重命名或换算。

## 公开报告与留存样本

- 2026-11-19 目标数据日留存的 `raw_event_dc.json` 中，IPO 记录 20 条，`MAIN_BUSINESS` 非空 20/20，20 个值互不相同。样本内容都是发行人的业务描述文本；全量原值保留在原始归档中，不另复制长文本。
- 平安银行（000001）归档文本列出吸收公众存款、发放贷款、国内外结算等商业银行业务；巨潮资讯网发布的[平安银行 2025 年年度报告](https://static.cninfo.com.cn/finalpage/2026-03-21/1225022887.PDF)在“报告期内公司从事的主要业务”部分列出对应业务，支持该记录的“主营业务”角色。
- 万科 A（000002）归档值为“房地产开发及相关资产经营和物业服务”；巨潮资讯网于 2024-11-26 发布的[万科担保公告](https://static.cninfo.com.cn/finalpage/2024-11-27/1221854561.PDF)在“被担保人基本情况”中将万科主营业务列为“房地产开发及相关资产经营、物业服务”。业务项一致，连接符不同；此处不声称字符级相等。
- 公司报告用于核对公开业务描述，不把报告发布日期当成 `RPTA_APP_IPOAPPLY` 字段的生效日期，也不替代官方接口路径核验。

样本边界与文件摘要：

- 归档目录目标数据日：2026-11-19；采集自然日：2026-11-20。
- `event_dc` 状态为 `ok`，但该来源没有 `as_of_date`；因此不能把样本当作 2026-11-19 当日更新的业务描述。
- 原始响应 SHA-256：`41fe019b29d038e1cf4726f69700af303aae0206a6fdb8d7399912290065b091`
- 核查时官方 `xglist.js` SHA-256：`e4fec5ac510df518f434fb050319e46ad3598c77fb536f72dd82fdf18f8b0655`
- 核查时官方 `xgdetail.js` SHA-256：`e681def470ece2ae827fd9a870baf108e692f8020d48d316ef45d5108c9aeeef`

## 适用范围

本决定只验证东方财富 IPO 发行记录中的该完整来源路径，不创建跨来源字段映射，不外推其他报表端点、其他提供方或未来接口版本。若响应文本与官方定义或发行人材料持续冲突，应重新核查来源路径和字段有效期。
