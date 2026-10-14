# 2026-10-14 财务字段定案记录

## 结论

本次依据碰撞报告的 3 个有效交易日（2026-09-28、2026-09-30、2026-10-08）完成 9 个 Eastmoney `ulist239(np/get)` 财务字段的语义/单位补全；各字段每天至少 19 只股票，稳定比例命中率为 100%。比例按报告定义为右侧字段除以左侧字段：股本为 10,000，其余 8 项为 0.1。TDX `weifenlirun` 原为未定状态，现根据协议定义与通达信公式文档确认语义，并由同一碰撞验证 Ulist `f47` 对应关系。另将腾讯 `[72]`、`[76]` 两条流通股本路径关联到 TDX；只补齐 `[76]` 先前为空的规范名，保留其既有含义和单位。

本轮应用了 12 项可复核决定，新增 11 条跨源映射；包括 9 条 Ulist↔TDX 关系和 2 条 Tencent↔TDX 关系。字段来源数量未增加，生产采集请求数量不变。

| Ulist 字段 | 规范名 | 含义 | 单位 | 对照 TDX 字段 | 右/左比例 |
|:--|:--|:--|:--|:--|--:|
| `f39` | `liutongguben` | 流通股本 | 股 | `liutongguben` | 10,000 |
| `f50` | `zongzichan` | 总资产 | 元 | `zongzichan` | 0.1 |
| `f51` | `liudongzichan` | 流动资产 | 元 | `liudongzichan` | 0.1 |
| `f52` | `gudingzichan` | 固定资产 | 元 | `gudingzichan` | 0.1 |
| `f55` | `liudongfuzhai` | 流动负债 | 元 | `liudongfuzhai` | 0.1 |
| `f60` | `zibengongjijin` | 资本公积金 | 元 | `zibengongjijin` | 0.1 |
| `f42` | `yingyelirun` | 营业利润 | 元 | `yingyelirun` | 0.1 |
| `f44` | `lirunzonghe` | 利润总额 | 元 | `lirunzonghe` | 0.1 |
| `f47` | `weifenlirun` | 未分配利润 | 元 | `weifenlirun` | 0.1 |

原始快照可独立复算单位比例。2026-10-08 贵州茅台的 TDX `liutongguben` 为 125008.15625 万股，Ulist `f39` 为 1250081601 股；TDX `zongzichan` 为 3090507840000 角，Ulist `f50` 为 309050784569.31 元。差异处于接口精度范围内，量级和换算方向一致。

## 同花顺/腾讯额外核对

同一份碰撞报告另有 `tencent[72]` 与 `tencent[76]` 对 TDX `liutongguben` 的匹配。两项各有 6 个有效交易日、每天 20 只股票、120 组配对，比例均为 10,000。主字典此前已把腾讯 `[72]` 定义为“A股流通股本（股）”，并将 `[76]` 定义为与 `[72]` 相同；本次将 `[72]` 登记为映射、为 `[76]` 补齐指向 `[72]` 的规范名后登记映射，均保留已有含义和单位。

报告中的 H 股、B 股零值候选未定案：命中来自常量零样本，缺少稳定的非零比率，不能据此赋予字段含义。

## `lirunzonghe` 的中文含义

按拼音逐字拆解，`lirunzonghe` 的字面中文确实是“利润总和”，你的拼音判断成立；但这只能解释历史变量名，不足以决定会计字段语义。通达信公式文档将 `FINANCE(28)` 定义为“利润总额”，TDX FinanceInfo 协议也把 `LiRunZongHe` 注释为“利润总额”。因此项目字段语义应登记为“利润总额”，字段代码仍保留 `lirunzonghe`。本次只更正当前 registry，并把旧值保存在定案记录和历史原文中。

证据：

- [通达信公式函数表：FINANCE(28)](https://help.tdx.com.cn/gspt/docs/markdown/redword/functionlist.html)
- [TDX FinanceInfo 协议定义：LiRunZongHe](https://pkg.go.dev/github.com/injoyai/tdx/protocol)
- [通达信 FINANCE(31)：未分配利润](https://help.tdx.com.cn/gspt/docs/markdown/redword/functionlist.html)
- [TDX FinanceInfo 协议定义：WeiFenLiRun](https://pkg.go.dev/github.com/injoyai/tdx/protocol)

## 对采集与五大报告的影响

- 这 9 个 Ulist 字段和两个腾讯路径本来就在采集/字段登记中，本次只补充语义、单位和跨源映射，不增加每日请求。
- 映射进入 registry 的 `mappings` 后，后续碰撞可直接跳过已定案的字段对，并保留其作为已知锚点的资格。Ulist `f47` 的语义由独立协议定义确认；碰撞证据负责验证数值关系。
- 五大报告的字段路由和报告指标不需要改变：这些字段为字段破解采集与跨源验证提供锚点，当前没有证据要求把它们加入 SHT/MED/LNG/VAL/MAK 的计算或展示链。
- `field_source_reference.md` 是不可覆盖的历史原文，本次保持不变；当前解释由 registry 的人工定案证据覆盖并可追溯。

机器可读决定见 [`adjudications/20261014_finance_fields.json`](../adjudications/20261014_finance_fields.json)；数值证据来自 [`20261014_collision_report.json`](20261014_collision_report.json) 与 [`20261008` 原始采集快照](../20261008/)。
