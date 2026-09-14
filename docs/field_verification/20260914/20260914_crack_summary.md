# 20260914 字段破解摘要（最新采集 + ZHB 锚）

> 数据源：通达信(TDX)/东方财富(push2·ulist239·fuyao)/腾讯/新浪/ZHB/DataCenter 等 23 源；
> 采集日 20260914（ZHB 本地快照 20260911）；对撞窗口 7 日（20260908–20260914）。
> 共 39 条本轮首现 L1 映射，本摘要聚焦**高价值异号同义**与 **ZHB 锚定**项。本引擎只发现、不写字典；新定案需经 field_dict.md 订正 + sanctioned 管线 ingest。

## 一、ZHB 锚定破解（用户指定锚源，7 条）

  - `zhb.stat2.zt_seal_amount_1d` ⇔ `zhb.full.zt_seal_amount_1d`  [L1] 命中100% · 5日 · 100对
  - `zhb.full.zt_seal_amount_1d` ⇔ `zhb.full.zt_seal_amount`  [L1] 命中92% · 5日 · 100对
  - `zhb.stat2.zt_seal_amount_1d` ⇔ `zhb.full.zt_seal_amount`  [L1] 命中92% · 5日 · 100对
  - `zhb.stat2.zt_seal_amount` ⇔ `zhb.full.zt_seal_amount_1d`  [L1] 命中92% · 5日 · 100对
  - `zhb.stat2.zt_seal_amount_1d` ⇔ `zhb.stat2.zt_seal_amount`  [L1] 命中92% · 5日 · 100对
  - `zhb.full.high_52w` ⇔ `tencent[67]`  [L1] 命中90% · 5日 · 100对
  - `zhb.stat2.high_52w` ⇔ `tencent[67]`  [L1] 命中90% · 5日 · 100对

> 结论：**腾讯 qt.gtimg idx67 ≡ ZHB.high_52w（52 周最高价）**，双向独立源佐证（90% 命中 / 5 日）。
> 反向亦证 ZHB.full.high_52w 与 ZHB.stat2.high_52w 取值一致（同源冗余，可二选一）。

## 二、ulist239 盘口五档定位（东财 ulist.np 独立 f 编号族，5 条）

  - `ulist239.f4` ⇔ `tdx.quote_full.change_amt`  [L1] 命中100% · 5日 · 100对
  - `ulist239.f31` ⇔ `tdx.quote_full.bid1`  [L1] 命中99% · 5日 · 100对
  - `ulist239.f142` ⇔ `tdx.quote_full.bid2`  [L1] 命中99% · 5日 · 100对
  - `ulist239.f32` ⇔ `tdx.quote_full.ask1`  [L1] 命中96% · 5日 · 100对
  - `ulist239.f143` ⇔ `tdx.quote_full.ask2`  [L1] 命中96% · 5日 · 100对

> 结论：ulist239 **f31=买一价 / f32=卖一价 / f142=买二价 / f143=卖二价**（与 TDX bid1/ask1/bid2/ask2 异源吻合 96–99%）。

## 三、push2 f 编号语义补全（em.stock_get 体系，1 条）

  - `tdx.quote_full.change_amt` ⇔ `push2_full.f169`  [L1] 命中100% · 5日 · 100对

> 结论：**push2_full.f169 ≡ 涨跌额**（与 TDX change_amt 100% 吻合）；为 f169 在字典中的语义定案提供 L1 异源证据。

## 四、fuyao 官方语义终判（同花顺 fuyao REST，2 条）

  - `tdx.quote_full.change_amt` ⇔ `fuyao.snapshot.price_change`  [L1] 命中100% · 5日 · 100对
  - `tdx.quote_full.change_pct` ⇔ `fuyao.snapshot.price_change_ratio_pct`  [L1] 命中100% · 5日 · 100对

> 结论：**fuyao.snapshot.price_change=涨跌额 / price_change_ratio_pct=涨跌幅%**，与 TDX change_amt/change_pct 双向吻合（100% / 5 日）。

## 五、其余（含标准位序映射的异源复验，24 条，节选前 20）

  - `tdx.quote_full.bid1` ⇔ `sina[6]`  [L1] 命中100% · 5日 · 100对
  - `tdx.quote_full.ask1` ⇔ `sina[7]`  [L1] 命中100% · 5日 · 100对
  - `tdx.quote_full.bid1` ⇔ `sina[11]`  [L1] 命中100% · 5日 · 100对
  - `tdx.quote_full.bid2` ⇔ `sina[13]`  [L1] 命中100% · 5日 · 100对
  - `tdx.quote_full.bid3` ⇔ `sina[15]`  [L1] 命中100% · 5日 · 100对
  - `tdx.quote_full.bid4` ⇔ `sina[17]`  [L1] 命中100% · 5日 · 100对
  - `tdx.quote_full.bid5` ⇔ `sina[19]`  [L1] 命中100% · 5日 · 100对
  - `tdx.quote_full.ask1` ⇔ `sina[21]`  [L1] 命中100% · 5日 · 100对
  - `tdx.quote_full.ask2` ⇔ `sina[23]`  [L1] 命中100% · 5日 · 100对
  - `tdx.quote_full.ask3` ⇔ `sina[25]`  [L1] 命中100% · 5日 · 100对
  - `tdx.quote_full.ask4` ⇔ `sina[27]`  [L1] 命中100% · 5日 · 100对
  - `tdx.quote_full.ask5` ⇔ `sina[29]`  [L1] 命中100% · 5日 · 100对
  - `tencent[57]` ⇔ `tdx.quote_full.amount_wan`  [L1] 命中100% · 5日 · 100对
  - `tencent[31]` ⇔ `tdx.quote_full.change_amt`  [L1] 命中100% · 5日 · 100对
  - `tencent[9]` ⇔ `tdx.quote_full.bid1`  [L1] 命中100% · 5日 · 100对
  - `tencent[19]` ⇔ `tdx.quote_full.ask1`  [L1] 命中100% · 5日 · 100对
  - `tencent[11]` ⇔ `tdx.quote_full.bid2`  [L1] 命中100% · 5日 · 100对
  - `tencent[21]` ⇔ `tdx.quote_full.ask2`  [L1] 命中100% · 5日 · 100对
  - `tencent[13]` ⇔ `tdx.quote_full.bid3`  [L1] 命中100% · 5日 · 100对
  - `tencent[23]` ⇔ `tdx.quote_full.ask3`  [L1] 命中100% · 5日 · 100对

> 注：tencent[9]/[19]… 与 sina[6]…[29] 对 TDX 五档的映射属**已知标准位序**（已载 tencent_verify.md / sina 文档），本轮为异源复验（100% 吻合），非新发现。

---

> 数据来源：通达信 / 项目字段对撞体系。以上为方法论梳理与异源对撞证据，**不构成投资建议**。
