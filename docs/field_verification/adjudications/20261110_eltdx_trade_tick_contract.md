# ELTDX TradeTick 来源契约裁决

日期：2026-11-10<br>
裁决方式：固定版本 API 契约与模型核验；未读取采集样本。

## 裁决

| 来源字段 | 已确认含义 | 保留的未知边界 |
|---|---|---|
| `absolute_index` | 分页合并时的全局原始序号 | 不等同于合并列表下标 |
| `event_kind` | `trade`、`auction_snapshot`、`opening_match` 三类事件标签 | 客户端分类，不是服务器原始字段 |
| `auction_matched_volume` | 成交明细中的竞价匹配量占位字段，固定为 `None` | 真实竞价量来自独立 `auctions.series` 接口 |
| `auction_unmatched_signed_volume` | 成交明细中的带符号未匹配量占位字段，固定为 `None` | 真实未匹配数据来自独立 `auctions.series` 接口 |
| `order_count` | 成交明细中的原始笔数字段 | 不代表集合竞价未匹配量；文档未给出更细计数口径 |
| `side` | 方向或状态标签，可见 `buy`、`sell`、`neutral` 或状态名 | 未推导完整数值状态码映射 |
| `status_raw` | 方向 / 状态原始值 | 完整状态码表未在本批确认 |

七项路径均来自 ELTDX v3.3.2 的 `TradeTick` 返回模型和成交明细契约。固定版本方法手册区分普通成交、竞价快照和正式开盘撮合，并明确说明 `order_count` 不应解释为竞价未匹配量；两个 `auction_*_volume` 字段在成交明细中固定为 `None`，实际竞价过程由 `client.auctions.series()` 返回。[METHOD_REFERENCE.md v3.3.2](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/METHOD_REFERENCE.md)

本批未读取历史采集值，因此不依赖目录目标数据日或自然日推定来源数据日，也不建立任何跨源数值映射。以下相邻字段继续单独待核：`trade_datetime`、`trading_date` 涉及日期资格；`volume`、`index`、`time_label` 在多个模型类型中出现，当前扁平身份不足以确认唯一语义。

项目代码边界另行核实：当前 `scripts/capture_field_probe.py::collect_eltdx` 委托 `scripts/capture_tcp_collectors.py::collect_eltdx`，该采集器调用快照、ShortlineIndicator 和全局 Helpers，没有调用 `client.trades` 或 `client.auctions`。所以本裁决只确认 ELTDX v3.3.2 上游模型字段契约；不声称这些字段当前由项目采集，不恢复接口路由，也不将其作为本项目当前碰撞锚。
