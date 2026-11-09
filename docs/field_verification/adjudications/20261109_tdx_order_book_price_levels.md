# TDX 买卖盘口价格档位定案（2026-11-09）

## 结论

确认 `TDX(双命名源)::bid2` 至 `bid5` 分别为买二至买五价；`ask2` 至 `ask5` 分别为卖二至卖五价。八条记录此前均为 `unverified`，本次只确认来源内字段语义，不创建跨源映射，也不把 `quote_full.bidN/askN` 认作这些原始路径的逐值别名。

| 完整来源路径 | 含义 | 单位 |
|---|---|---|
| `TDX(双命名源)::bid2` | 买二价 | 官方文档未注明 |
| `TDX(双命名源)::bid3` | 买三价 | 官方文档未注明 |
| `TDX(双命名源)::bid4` | 买四价 | 官方文档未注明 |
| `TDX(双命名源)::bid5` | 买五价 | 官方文档未注明 |
| `TDX(双命名源)::ask2` | 卖二价 | 官方文档未注明 |
| `TDX(双命名源)::ask3` | 卖三价 | 官方文档未注明 |
| `TDX(双命名源)::ask4` | 卖四价 | 官方文档未注明 |
| `TDX(双命名源)::ask5` | 卖五价 | 官方文档未注明 |

## 证据链

1. 通达信官方 `get_market_snapshot_batch` 快照契约把 `Buyp` 定义为五档买价数组、把 `Sellp` 定义为五档卖价数组；官方样例分别给出五个按档位顺序排列的价格。文档未注明这两个数组的价格单位，故不补造单位。
2. 项目 `scripts/capture_tcp_collectors.py::collect_tdx` 通过 `core.tdx_client::tdx_get_quote_raw` 保存 TDX 适配器原始行。`_EltdxAdapter.quotes()` 把返回的 `buy_levels` / `sell_levels` 按顺序写为 `bid1..bid5` / `ask1..ask5`；`_EasyTdxAdapter.quotes()` 原样返回 `get_security_quotes()` 的行。采集规范化器会保留适配器行中实际存在的买卖档位键。
3. ELTDX 的字段手册说明 `get_snapshots()` 只含买一/卖一，`client.helpers.full_quotes()` 才返回五档；项目当前 ELTDX 主适配器使用 `get_snapshots()`。因此当前主路径只可观察第一档，不能把本次语义确认误报为当前五档采集覆盖已验证。EasyTdx 回退和上游响应若提供更深档位，项目保留对应顺序字段。
4. 对样本保留起点 `2026-10-15` 之后全部留存的 TDX 原始行情逐条扫描：300 条股票记录中，`quote_raw` 和 `quote_full` 都没有 `bid2..bid5` 或 `ask2..ask5`。所以本裁决不声称存在历史数值碰撞或交叉来源配对证据；结论来自官方字段契约及项目适配路径。

## 未作出的推断

- 不推断更深档位的价格单位；官方接口文档没有注明。
- 不推断当前 ELTDX `get_snapshots()` 已采到第二至第五档。
- 不将这些路径与 `quote_full.bid2..bid5`、`quote_full.ask2..ask5` 或腾讯/新浪盘口字段登记为逐值映射。
- 不新增未在注册表中的买卖量字段。

## 注册同步与回归

- 八条字段已写入主注册表并退出未验证队列；未验证候选由 129 条降为 121 条。
- 源契约定案使用独立 parity 分类，逐条重放决策文件并核对注册表定案及引用证据；字段矩阵从 1,576 个字段 / 1,717 条来源关系更新为 1,584 个字段 / 1,725 条来源关系。
- 完整离线验收通过：1,486 passed、1 skipped；52 个真实联网用例按默认规则未执行。

## 引用

- 通达信官方：[批量获取实时行情快照 `get_market_snapshot_batch`](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html)，2026-11-09 检索；字段表 `Buyp` / `Sellp` 与返回样例。
- 项目代码：`scripts/capture_tcp_collectors.py::collect_tdx`、`core/tdx_client.py::_EasyTdxAdapter.quotes` / `tdx_get_quote_raw`、`core/eltdx_adapter.py::_EltdxAdapter.quotes`、`scripts/capture_field_probe.py::_normalize_tdx_capture_quote`。
- ELTDX 上游：[字段手册](https://github.com/electkismet/eltdx/blob/main/docs/FIELD_REFERENCE.md#quotesnapshot)，2026-11-09 检索；`QuoteSnapshot.buy_levels/sell_levels` 档位数量说明。
- 机器裁决：[`20261109_tdx_order_book_price_levels.json`](20261109_tdx_order_book_price_levels.json)。
