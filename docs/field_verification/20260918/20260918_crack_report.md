# 20260918 未知字段破解分析报告

> 数据来源：通达信 / 项目字段对撞体系。以上为方法论梳理，不构成投资建议。

> 对撞窗口：20260912~20260918（7 天）｜L1 候选 901｜L4 候选 1338｜护栏拦截 11｜新增定案 5

> 本引擎只发现、不写字典；破解结论经 field_dict.md 订正后由 sanctioned 管线 ingest。

---

## 一、破解结论概览

- 跨号 L1 中「一端未知 + 一端已定案锚」的可破解候选：**49** 条（均满足 ≥3 独立日、命中率≥0.85、尚未入字典）。
- 本次升级为 confirmed 的跨号对（已入 registry 映射）：**278** 条。
- 字段空间已高度成熟：所有已定案锚的跨号碰撞均已记录，剩余未知数多为 fuyao/ZHB/TDX 适配层字段，经对撞可锚定到 EM f 编号语义。

## 二、高置信破解候选（未知字段 → 已定案 EM 锚语义）

| 未知字段 | 等价已定案锚 | 锚中文语义 | 等级 | 命中率 | 天数 | 比值 |
|:--|:--|:--|:--|--:|--:|:--|
| `fuyao.snapshot.price_change` | `push2.f169` | 涨跌额 | L1 | 1.0 | 5 | - |
| `fuyao.snapshot.price_change_ratio_pct` | `tdx.quote_full.change_pct` | 涨跌幅 | L1 | 1.0 | 5 | - |
| `fuyao.snapshot.turnover` | `push2.f48` | 成交额 | L1 | 1.0 | 5 | - |
| `fuyao.snapshot.volume` | `sina[8]` | change_pct_2d | L1 | 1.0 | 5 | - |
| `push2.f162` | `tencent[52]` | 市盈率(动态) | L1 | 1.0 | 5 | - |
| `push2.f163` | `tencent[53]` | 市盈率(静态/年报 LYR) | L1 | 1.0 | 5 | - |
| `push2.f51` | `tencent[47]` | 涨停价 | L1 | 1.0 | 5 | - |
| `push2.f52` | `tencent[48]` | 跌停价 | L1 | 1.0 | 5 | - |
| `push2.f71` | `tencent[51]` | 均价 | L1 | 1.0 | 5 | - |
| `push2_full.f162` | `tencent[52]` | 市盈率(动态) | L1 | 1.0 | 5 | - |
| `push2_full.f163` | `tencent[53]` | 市盈率(静态/年报 LYR) | L1 | 1.0 | 5 | - |
| `push2_full.f51` | `tencent[47]` | 涨停价 | L1 | 1.0 | 5 | - |
| `push2_full.f52` | `tencent[48]` | 跌停价 | L1 | 1.0 | 5 | - |
| `push2_full.f71` | `tencent[51]` | 均价 | L1 | 1.0 | 5 | - |
| `sina[23]` | `tencent[21]` | change_ytd | L1 | 1.0 | 5 | - |
| `tdx.quote_full.ask1` | `sina[7]` | change_pct_1d | L1 | 1.0 | 5 | - |
| `tdx.quote_full.bid1` | `sina[6]` | change_pct | L1 | 1.0 | 5 | - |
| `tdx.quote_full.change_amt` | `push2.f169` | 涨跌额 | L1 | 1.0 | 5 | - |
| `tencent[23]` | `sina[25]` | *(丢弃)* | L1 | 1.0 | 5 | - |
| `tencent[32]` | `push2.f170` | 涨跌幅 | L1 | 1.0 | 5 | - |
| `tencent[63]` | `push2.f119` | ulist:f109 | L1 | 1.0 | 5 | - |
| `tencent[68]` | `push2.f175` | tx[69] | L1 | 1.0 | 5 | - |
| `tencent[72]` | `push2.f85` | 流通股本 | L1 | 1.0 | 5 | - |
| `tencent[73]` | `push2.f84` | 总股本 | L1 | 1.0 | 5 | - |
| `tencent[76]` | `push2.f85` | 流通股本 | L1 | 1.0 | 5 | - |
| `ulist239.f10` | `tencent[49]` | 量比 | L1 | 1.0 | 5 | - |
| `ulist239.f114` | `tencent[53]` | 市盈率(静态/年报 LYR) | L1 | 1.0 | 5 | - |
| `ulist239.f13` | `push2.f110` | 市场标记（布尔 0/1，北交=0） | L1 | 1.0 | 5 | - |
| `ulist239.f19` | `push2.f112` | 板级枚举 | L1 | 1.0 | 5 | - |
| `ulist239.f27` | `push2.f110` | 市场标记（布尔 0/1，北交=0） | L1 | 1.0 | 5 | - |
| `ulist239.f7` | `tencent[43]` | 振幅% | L1 | 1.0 | 5 | - |
| `ulist239.f8` | `tencent[38]` | 换手率% | L1 | 1.0 | 5 | - |
| `zhb.full.low_52w` | `push2.f175` | tx[69] | L1 | 1.0 | 5 | - |
| `zhb.stat2.low_52w` | `push2.f175` | tx[69] | L1 | 1.0 | 5 | - |
| `eltdx.quote_snapshot.amount` | `push2.f48` | 成交额 | L1 | 1.0 | 4 | - |
| `tencent[69]` | `ulist239.f160` | f160=年报EPS(✅ fuyao basic_eps 年报 锚定，§五 17/20)；f190=每股未分配利润(✅ 可由 fuyao balance_sheets.undistributed_profit 总额 ÷ 总股本 f84 推导，非 push 独有)；f108=扣非EPS TTM(❌ 确为 push2 独有，fuyao 仅 basic_eps 无扣非EPS) | L1 | 0.99 | 5 | - |
| `tencent[70]` | `push2.f120` | ulist:f110 | L1 | 0.98 | 5 | - |
| `ulist239.f142` | `sina[13]` | board_count | L1 | 0.98 | 5 | - |
| `ulist239.f211` | `tencent[10]` | dividend_yield | L1 | 0.98 | 5 | - |
| `ulist239.f31` | `sina[6]` | change_pct | L1 | 0.98 | 5 | - |
| `push2.f164` | `tencent[39]` | PE(TTM) | L1 | 0.97 | 5 | - |
| `push2_full.f164` | `tencent[39]` | PE(TTM) | L1 | 0.97 | 5 | - |
| `ulist239.f115` | `tencent[39]` | PE(TTM) | L1 | 0.97 | 5 | - |
| `push2.f167` | `tencent[46]` | PB | L1 | 0.95 | 5 | - |
| `push2_full.f167` | `tencent[46]` | PB | L1 | 0.95 | 5 | - |
| `ulist239.f143` | `tencent[21]` | change_ytd | L1 | 0.94 | 5 | - |
| `ulist239.f212` | `tencent[20]` | change_60d_alt | L1 | 0.94 | 5 | - |
| `ulist239.f32` | `sina[7]` | change_pct_1d | L1 | 0.94 | 5 | - |
| `tencent[71]` | `push2.f121` | 资金流衍生指标(≡60日涨跌幅, 见[71]/ulist f24) | L1 | 0.92 | 5 | - |

## 三、升级为 confirmed 的跨号对（已入字典，作回归护栏）

（共 278 条，示前 20）

| 左字段 | 右字段 | 等级 | 命中率 | 天数 |
|:--|:--|:--|--:|--:|
| `em_fund_flow.f137` | `ulist239.f62` | L1 | 1.0 | 5 |
| `em_fund_flow.f140` | `ulist239.f66` | L1 | 1.0 | 5 |
| `em_fund_flow.f141` | `ulist239.f70` | L1 | 1.0 | 5 |
| `em_fund_flow.f142` | `ulist239.f71` | L1 | 1.0 | 5 |
| `em_fund_flow.f143` | `ulist239.f72` | L1 | 1.0 | 5 |
| `em_fund_flow.f144` | `ulist239.f76` | L1 | 1.0 | 5 |
| `em_fund_flow.f145` | `ulist239.f77` | L1 | 1.0 | 5 |
| `em_fund_flow.f146` | `ulist239.f78` | L1 | 1.0 | 5 |
| `em_fund_flow.f147` | `ulist239.f82` | L1 | 1.0 | 5 |
| `em_fund_flow.f148` | `ulist239.f83` | L1 | 1.0 | 5 |
| `em_fund_flow.f149` | `ulist239.f84` | L1 | 1.0 | 5 |
| `push2.f47` | `ulist239.f5` | L1 | 1.0 | 5 |
| `push2.f48` | `ulist239.f6` | L1 | 1.0 | 5 |
| `push2.f49` | `ulist239.f34` | L1 | 1.0 | 5 |
| `push2.f50` | `ulist239.f10` | L1 | 1.0 | 5 |
| `push2.f55` | `ulist239.f112` | L1 | 1.0 | 5 |
| `push2.f57` | `ulist239.f12` | L1 | 1.0 | 5 |
| `push2.f58` | `ulist239.f14` | L1 | 1.0 | 5 |
| `push2.f84` | `ulist239.f38` | L1 | 1.0 | 5 |
| `push2.f85` | `ulist239.f39` | L1 | 1.0 | 5 |

## 四、核查要点与后续动作

- **命名锚来源**：EM f 编号中文语义取自 `field_registry.json`（权威字典，status=verified 为主），属黄金锚（fuyao/东财官网）衍生真值。
- **同号异义警示**：f57 在 push2 端=股票代码、涨跌幅=f170；ulist 端 f57=涨跌幅等不同端点同号异义，跨端点对撞须显式区分 scheme（已在对撞血缘标注中固化）。
- **待人工复核**：护栏拦截 11 条（数值实证已证伪，未进 L1）；L4 存疑 1338 条需结合黄金锚逐一定名。
- **下一步**：将第二节候选经 `field_dict.md` 订正 → sanctioned 管线 ingest；fuyao/ZHB/TDX 适配层字段建议补 `meaning` 后标 verified。

---
> 数据来源：通达信 / 项目字段对撞体系。以上为方法论梳理，不构成投资建议。
