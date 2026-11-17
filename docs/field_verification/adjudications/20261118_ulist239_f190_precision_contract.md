# 东方财富 Ulist `f190` 官方显示精度契约

核验日期：2026-11-18。目标身份为 `东财-ulist239(np/get)::f190`。

## 项目路径和官方实现

项目 [`collect_ulist239`](../../../scripts/capture_http_collectors.py#L945) 请求 `api/qt/ulist.np/get` 并把 `data.diff` 的原始键直接保存。项目采集参数使用 `fltt=2`；保留的 2026-11-17 快照中，601288 的 `f186=6.905`、`f190=3`，其关联证券字段为 `f191=01288`、`f192=116`、`f193=农业银行`。同日其他 19 条股票的 `f190=0`。

东方财富行情中心官方前端脚本 [`index.js`](https://quote.eastmoney.com/center/static/build/index.js)（本轮取得版本 UTF-8 SHA-256：`1224df21d3aa5cef8659acd9293b1f44047e0398080e6bce72fe881d755dc59b`）定义 `H股对应的A股最新价` 使用字段 `fid:["f186","f190","f187"]`，把 `f190` 作为 `f186` 的第二个格式器参数。该脚本格式器在第二参数 `t > 0` 时执行 `e / 10**t` 并显示 `t` 位小数；官方 `getListQuoteNPList` 通过 `api/qt/ulist.np/get` 请求列表数据，使用 `fltt=1`。因此 `f190` 的直接职责是 `f186` 价格字段的十进制缩放/显示精度参数，不是 H 股股数、股本量或其换算系数。

项目采集器使用 `fltt=2`，保存样本中的 `f186=6.905` 已是小数价格形式；不得再按 `f190=3` 对 `f186` 做二次除法。未据此推断 `f186` 在全部证券类型中的价格来源或交易时点。

## 裁决及对旧候选的影响

- `f190` 定案为 **H 股关联 A 股价格的十进制缩放/显示精度位数**；单位留空，因为它是格式参数，不是物理量。
- 此定义解释了旧样本中仅农业银行 `f190=3`、其余记录为 0 的特征。旧候选 `ulist239.f190 ↔ TDX hgu` 把格式参数与 H 股股数作比较，38/40 的 0/0 命中不构成等价证据；正式跨源候选复核单独追加拒绝决定。
- 该结论仅适用于 `东财-ulist239(np/get)::f190`；不外推到其他来源或同编号字段，不增加 `mappings`。

## 留存样本

使用 [`2026-11-17 Ulist 原始快照`](../20261117/raw_ulist239.json)，SHA-256：`d8f0cd0092412ab8f33fc0cbdccc9643e10367001c667857ec6a16ea73b033bf`。字段的 A/H 关联值与低信息候选背景另见[旧候选复核](20261117_ulist239_f190_hgu_low_information_review.md)。

## 来源

- 东方财富[行情中心官方前端脚本](https://quote.eastmoney.com/center/static/build/index.js)。
- 项目[采集器实现](../../../scripts/capture_http_collectors.py#L945)与[保留原始样本](../20261117/raw_ulist239.json)。
