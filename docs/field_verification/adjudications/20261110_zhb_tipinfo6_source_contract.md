# ZHB-tipinfo `[6]` 语义更正（2026-11-10）

## 定案范围

精确身份为 `ZHB-tipinfo::[6]`，即 `tipinfo.dat` 的原始第 `[6]` 列。本次只更正该路径的中文语义释义；规范名 `[6]`、已验证状态和空单位均保留，不新增跨源映射，也不改变解析器与缓存行为。

## 官方定义

通达信量化平台 `get_more_info_batch` 官方字段表将 `TopDate_Recent` 定义为“近 2 年最近龙虎榜日期”。页面没有把 `Top` 解释为价格顶部或阶段新高。此前将其释为“阶段新高日”属于从英文词面推断，现按官方定义更正。

官方文档：[通达信量化平台扩展信息字段表](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html)（2026-11-10 在线核验；页面无版本标记）。

## 原始列值与官方页面交叉核对

在留存的 `cache/zhb/zhb_20261109.zip` 的 `tipinfo.dat` 中按股票代码读取原始列 `[6]`，与东方财富官方个股龙虎榜页面“每日成交明细”的当前日期列表逐项核对：

| 股票 | ZHB 原始 `[6]` | 东方财富页面最近列示日期 | 页面 |
|---|---:|---:|---|
| 泸州老窖 `000568` | `20261030` | `2026年10月30日` | [个股龙虎榜](https://data.eastmoney.com/stock/lhb/000568.html) |
| 襄阳轴承 `000678` | `20261106` | `2026年11月06日` | [个股龙虎榜](https://data.eastmoney.com/stock/lhb/000678.html) |
| 新华传媒 `600825` | `20261019` | `2026年10月19日` | [个股龙虎榜](https://data.eastmoney.com/stock/lhb/600825.html) |

三条原始值均与页面最近一次上榜日期完全一致。东方财富页面用于值级交叉核对；字段语义依据通达信官方字段定义。页面值并未被当作独立碰撞锚。

## 结论与边界

`ZHB-tipinfo::[6]` 的语义更正为“近 2 年最近龙虎榜日期（通达信 `TopDate_Recent`）”。“阶段新高日”旧释义撤回。该日期是最近龙虎榜事件日期，不是 ZHB 包日期，也不是采集运行日期；包数据日仍以 `zhb_YYYYMMDD.zip` 文件名为准。

裁决文件：[`20261110_zhb_tipinfo6_source_contract.json`](20261110_zhb_tipinfo6_source_contract.json)。只读历史档案 `docs/field_source_reference.md` 保留原始旧记录，本次裁决及生成字典中的释义优先用于当前结论。
