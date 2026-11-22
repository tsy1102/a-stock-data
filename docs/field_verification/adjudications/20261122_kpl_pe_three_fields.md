# 开盘啦 W8 三个 PE 字段来源内定案

复核日期：2026-11-22。目标为 `开盘啦(kpl)::pe_dynamic`、`pe_ttm`、`pe_static`。本次只确认这三个完整来源路径，不把 KPL 与东财视为同一供应方，也不据一次同日对照建立跨源采集替代或删除关系。

## 字段定义

项目调用 `stock_common/sc_datasource/_pools.py::kpl_get_stock_list_w8()`，向 `apphis.longhuvip.com` 请求 `ZhiShuStockList_W8`，返回数组位置 60、61、62 分别映射为 `pe_dynamic`、`pe_ttm`、`pe_static`。公开的 KPL API 没有找到官方键级 schema；固定版本的第三方解析仓库记录了这三个应用字段标签及数组位置，故它只用于定位，不单独作为语义定案依据。

| KPL 完整路径 | 数组位置与应用标签 | 定案含义 | 对照锚 |
|:--|:--|:--|:--|
| `开盘啦(kpl)::pe_dynamic` | `[60]` 市盈率动 | 动态市盈率；东方财富解释为总市值除以全年预估净利润，盈利预测可依据最新报告期推算年化。 | Eastmoney `stock/get` `f162` / 项目 `pe_dynamic` |
| `开盘啦(kpl)::pe_ttm` | `[61]` 市盈率 TTM | 滚动市盈率；东方财富解释为最新价除以最近四个季度每股收益。 | Eastmoney `stock/get` `f164` / 项目 `pe_ttm` |
| `开盘啦(kpl)::pe_static` | `[62]` PE 静 | 静态市盈率；东方财富解释为总市值除以上一年度净利润，对应 LYR 口径。 | Eastmoney `stock/get` `f163` / 项目 `pe_lyr` |

东方财富个股页面给出了动态、静态和滚动市盈率的上述定义。KPL 第三方字段表将位置 60/61/62 命名为“市盈率动 / 市盈率 TTM / PE 静”；项目实际接口调用和字段映射由本项目代码确定。引用和版本固定信息见下方来源记录。

## 同日样本对照

按 KPL 日期参数 `2026-11-20` 请求 `PlateID=801821, Type=0`，响应 `Day` 为 `2026-11-20`，共 23 条有效个股记录。逐股调用项目 Eastmoney `push2delay` 适配器底层 `stock/get` 路由，对照项目映射的 `f162/f164/f163`。东方财富估值页显示的数据日期也是 `2026-11-20`；该 `stock/get` 响应本身不提供来源日期，因此另以两端现价逐股精确相同作为时点佐证。

| 检查项 | 命中 | 规则 | 最大差 |
|:--|--:|:--|--:|
| 个股现价 | 23/23 | 精确相同 | 0 |
| 动态 PE | 23/23 | 两位小数容差 ≤ 0.01 | 0.01 |
| PE TTM | 23/23 | 两位小数容差 ≤ 0.01 | 0.01 |
| 静态 PE | 23/23 | 两位小数容差 ≤ 0.01 | 0.01 |

逐股原值、映射路径及舍入差见 [`20261122_kpl_pe_eastmoney_anchor_pairs.csv`](../research/20261122_kpl_pe_eastmoney_anchor_pairs.csv)，规范 LF SHA-256：`195fd09aa36aca910dc22da7c0b898e3ef62c5b79b5c39a078b886a35768cb8e`。未纳入日常采集目录，也没有运行每日采集脚本。

## 裁决与边界

- 三条 KPL 来源路径均恢复为 `verified`，保留现有 canonical 和单位“倍”；将 PE TTM 的含义补全为明确的四季度滚动口径，并将动态、静态含义按东方财富的公开定义写清。
- 原 `status_conflict` 是“来源参考已验证”与“跨来源聚合未验证”冲突；后者不能覆盖有精确身份的 KPL 路径。本裁决只解除这三条 KPL 路径的状态冲突，不改变其他来源状态。
- 一组同日样本证明字段类别、映射和显示精度一致；没有据此认定 KPL 和 Eastmoney 是同一上游，也没有新增 `mappings` 或建议退役任一接口。要裁决采集替代关系，仍需按项目各自源字段覆盖和采集目的单独评估。
- KPL 没有可查到的官方公开键级公式说明；本次不对其内部计算实现作超出应用标签、同日锚点和公开 PE 定义的断言。

## 来源

- 项目路由：`stock_common/sc_datasource/_pools.py::kpl_get_stock_list_w8()` 和 `stock_common/sc_datasource/_quotes.py::_em_quote_full_impl()`。
- KPL 字段位置及标签参考：[Rainynitesky/kaipanla-data-parser README（固定提交 `7bfae30ab420e10af816584b7aa77e21c25c9e14`）](https://github.com/Rainynitesky/kaipanla-data-parser/blob/7bfae30ab420e10af816584b7aa77e21c25c9e14/README.md)。该仓库是第三方反向解析资料，不是开盘啦官方 schema。
- PE 定义及数据日期：[东方财富个股行情与估值说明](https://quote.eastmoney.com/sz000835.html)；[东方财富估值分析页](https://data.eastmoney.com/gzfx)。
