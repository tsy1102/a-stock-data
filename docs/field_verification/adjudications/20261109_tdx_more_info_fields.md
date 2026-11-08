# TDX `get_more_info_batch` 字段核验与定案

核验日期：2026-11-09。

## 范围与结论

通达信量化平台官方文档在 [`get_more_info_batch` 字段表](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html) 列出 92 个扩展字段，均声明为字符串。逐个按 `TDX(双命名源)` 的完整 source/path 身份与项目注册表比对：88 个路径已登记，11 个已验证，77 个仍未验证；本次按官方接口字段表确认这 77 个来源内语义。

官方文档中 `ClearPrice`、`PreMinum`、`PreVolIn`、`VolInStock` 4 个期货/期权字段未登记在项目字典。本次不新建路径：当前没有项目采集证据证明这些路径实际存在于本项目数据。

本次定案仅确认该 TDX 接口的字段名称与官方文字说明。它不证明当前项目运行时调用了 `get_more_info_batch`，不建立 TDX 与 ZHB 或其他来源之间的逐值映射，也不把接口级语义接入统一业务字段。文档没有明确单位、枚举值或计算细节的字段仍保留相应未知说明。

## 已定案的 77 个来源字段

| 完整 code path | 官方说明 | 注册单位/边界 |
|---|---|---|
| `TDX(双命名源)::HqDate` | 行情日期 | 日期字符串（格式未说明） |
| `TDX(双命名源)::fHSL` | 换手率 | 官方文档未注明 |
| `TDX(双命名源)::fLianB` | 量比 | 官方文档未注明 |
| `TDX(双命名源)::Wtb` | 委比 | 官方文档未注明 |
| `TDX(双命名源)::Zsz` | 总市值(亿) | 亿（币种未注明） |
| `TDX(双命名源)::Ltsz` | 流通市值(亿) | 亿（币种未注明） |
| `TDX(双命名源)::BetaValue` | 贝塔系数 | 官方文档未注明 |
| `TDX(双命名源)::DynaPE` | 动态市盈率 | 官方文档未注明 |
| `TDX(双命名源)::MorePE` | 市盈率（港股:动, 其他扩展:静） | 官方文档未注明 |
| `TDX(双命名源)::StaticPE_TTM` | 市盈率(TTM) | 官方文档未注明 |
| `TDX(双命名源)::DYRatio` | 股息率 | 官方文档未注明 |
| `TDX(双命名源)::PB_MRQ` | 市净率(MRQ) | 官方文档未注明 |
| `TDX(双命名源)::More_YJL` | ETF/LOF 溢价率 | 官方文档未注明 |
| `TDX(双命名源)::FreeLtgb` | 自由流通股本(万) | 万股 |
| `TDX(双命名源)::Yield` | 应计利息(债券)/占款天数(回购) | 债券应计利息单位未注明 / 回购占款天数（天） |
| `TDX(双命名源)::MainBusiness` | 主营构成 | 官方文档未注明 |
| `TDX(双命名源)::SafeValue` | 安全分 | 官方文档未注明 |
| `TDX(双命名源)::ShineValue` | 亮点数 | 官方文档未注明 |
| `TDX(双命名源)::ShapeValue` | 短期形态+中期形态+长期形态编号 | 形态编号（编码未说明） |
| `TDX(双命名源)::TPFlag` | 停牌标识 | 标识值（编码未说明） |
| `TDX(双命名源)::ZTPrice` | 涨停价 | 官方文档未注明 |
| `TDX(双命名源)::DTPrice` | 跌停价 | 官方文档未注明 |
| `TDX(双命名源)::vzangsu` | 量涨速 | 官方文档未注明 |
| `TDX(双命名源)::Fzhsl` | 分钟换手率 | 官方文档未注明 |
| `TDX(双命名源)::FzAmo` | 2 分钟金额(万元) | 万元 |
| `TDX(双命名源)::VOpenZAF` | 抢筹涨幅 | 官方文档未注明 |
| `TDX(双命名源)::OpenZAF` | 开盘涨幅 | 官方文档未注明 |
| `TDX(双命名源)::ZAF` | 涨幅 | 官方文档未注明 |
| `TDX(双命名源)::ZAFYesterday` | 昨日涨幅 | 官方文档未注明 |
| `TDX(双命名源)::ZAFPre2D` | 前天涨幅 | 官方文档未注明 |
| `TDX(双命名源)::ZAFPre5` | 5 日涨幅 | 官方文档未注明 |
| `TDX(双命名源)::ZAFPre10` | 10 日涨幅 | 官方文档未注明 |
| `TDX(双命名源)::ZAFPre20` | 20 日涨幅 | 官方文档未注明 |
| `TDX(双命名源)::ZAFPre30` | 30 日涨幅 | 官方文档未注明 |
| `TDX(双命名源)::ZAFPre60` | 60 日涨幅 | 官方文档未注明 |
| `TDX(双命名源)::ZAFYear` | 年初至今涨幅 | 官方文档未注明 |
| `TDX(双命名源)::ZAFPreMyMonth` | 涨幅(本月来) | 官方文档未注明 |
| `TDX(双命名源)::ZAFPreOneYear` | 涨幅(一年来) | 官方文档未注明 |
| `TDX(双命名源)::Zjl` | 主买净额(万元) | 万元 |
| `TDX(双命名源)::Zjl_HB` | 主力净流入(万元) | 万元 |
| `TDX(双命名源)::TotalBVol` | 总买量 | 官方文档未注明 |
| `TDX(双命名源)::TotalSVol` | 总卖量 | 官方文档未注明 |
| `TDX(双命名源)::BCancel` | 总撤买量 | 官方文档未注明 |
| `TDX(双命名源)::SCancel` | 总撤卖量 | 官方文档未注明 |
| `TDX(双命名源)::L2TicNum` | L2 逐笔成交数 | 官方文档未注明 |
| `TDX(双命名源)::L2OrderNum` | L2 逐笔委托数 | 官方文档未注明 |
| `TDX(双命名源)::FCAmo` | 封单额(万元)，> 0为涨停 < 0为跌停 | 万元 |
| `TDX(双命名源)::FCb` | 封成比 | 官方文档未注明 |
| `TDX(双命名源)::OpenAmo` | 开盘金额(万元) | 万元 |
| `TDX(双命名源)::OpenZTBuy` | 竞价涨停买入金额(万元) | 万元 |
| `TDX(双命名源)::OpenAmoPre1` | 昨开盘金额(万元) | 万元 |
| `TDX(双命名源)::OpenVolPre1` | 昨开盘量 | 官方文档未注明 |
| `TDX(双命名源)::CJJEPre1` | 昨成交额(万元) | 万元 |
| `TDX(双命名源)::CJJEPre3` | 3 日成交额(万元) | 万元 |
| `TDX(双命名源)::FDEPre1` | 昨封单额(万元) | 万元 |
| `TDX(双命名源)::FDEPre2` | 前封单额(万元) | 万元 |
| `TDX(双命名源)::ZTGPNum` | 板块指数的涨停家数 | 家 |
| `TDX(双命名源)::LastStartZT` | 几天 | 天（参照起点未说明） |
| `TDX(双命名源)::LastZTHzNum` | 几板 | 板（统计窗口未说明） |
| `TDX(双命名源)::EverZTCount` | 连板天 | 天（连续口径未说明） |
| `TDX(双命名源)::ConZAFDateNum` | 连涨天数 | 天 |
| `TDX(双命名源)::YearZTDay` | 年涨停天数 | 天 |
| `TDX(双命名源)::MA5Value` | 5 日均价 | 官方文档未注明 |
| `TDX(双命名源)::HisHigh` | 52 周最高 | 官方文档未注明 |
| `TDX(双命名源)::HisLow` | 52 周最低 | 官方文档未注明 |
| `TDX(双命名源)::IPO_Price` | 发行价 | 官方文档未注明 |
| `TDX(双命名源)::IsT0Fund` | 是否是 T+0 基金 | 标志值（编码未说明） |
| `TDX(双命名源)::IsZCZGP` | 是否是注册制 A 股 | 标志值（编码未说明） |
| `TDX(双命名源)::IsKzz` | 是否是可转债 | 标志值（编码未说明） |
| `TDX(双命名源)::Kzz_HSCode` | 可转债对应的正股代码 | 证券代码 |
| `TDX(双命名源)::QHMainYYMM` | 主力合约关联的月份(期货) | 月份（字符串格式未说明） |
| `TDX(双命名源)::KfEarnMoney` | 扣非净利润(万元) | 万元 |
| `TDX(双命名源)::RDInputFee` | 研发费用(万元) | 万元 |
| `TDX(双命名源)::CashZJ` | 货币资金(万元) | 万元 |
| `TDX(双命名源)::PreReceiveZJ` | 合同负债(万元) | 万元 |
| `TDX(双命名源)::OtherQYJzc` | 其它权益工具(万元) | 万元 |
| `TDX(双命名源)::StaffNum` | 员工人数 | 人 |

## 既有日期字段来源修正

上一版 [`20261109_tdx_snapshot_dates.md`](20261109_tdx_snapshot_dates.md) 将 11 个日期字段误归入 `get_market_snapshot_batch`。官方文档将这 11 个字段列在 `get_more_info_batch` 的扩展字段表中；字段语义与状态不变，已修正报告、公开网页证据及注册表中的证据出处。日期值仍只确认类型为字符串，格式未公开。

## 特殊边界

- `Yield` 对债券表示应计利息，对回购表示占款天数；量纲随证券类型变化，官方未给出债券量纲。
- `MorePE` 的官方说明区分港股与其他扩展品种；不将其简化为全市场统一的静态或动态市盈率。
- `vzangsu` 的官方说明只有“量涨速”；撤回旧登记的 `%` 单位，计算公式、单位和窗口仍未知。
- `LastStartZT`、`LastZTHzNum`、`EverZTCount` 等官方说明过于简略；仅按原文登记单位提示，不推断参照区间或算法。
- `PreReceiveZJ` 和 `OtherQYJzc` 的 TDX 官方定义分别为合同负债（万元）和其它权益工具（万元）；其与 ZHB 路径分开裁决。
- ZHB 原始列 `[25]`、`[34]` 的独立财报对照见 [`20261109_zhb_accounting_metadata_corrections.md`](20261109_zhb_accounting_metadata_corrections.md)；该裁决不建立 TDX 与 ZHB 逐值映射。

## 验证文件

- 决策记录：`docs/field_verification/adjudications/20261109_tdx_more_info_fields.json`。
- 官方网页摘录及证券报告交叉核验：[`public_web/20261109_tdx_more_info_fields.md`](public_web/20261109_tdx_more_info_fields.md)。
