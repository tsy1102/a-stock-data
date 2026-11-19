# Ulist `f63` 对 ELTDX 开盘竞价字段候选的身份更正与复核

## 候选 ID 对照

核对碰撞报告的完整字段路径后，候选 ID 对应关系为：

| 候选 ID | 左字段 | 右字段 |
| --- | --- | --- |
| `cc1_9790941bc04f6efd5ed3820a6273b9b5d13989c78d8a72b9bb02bf3a8520cc43` | `ulist239.f63` | `eltdx.shortline.open_amount` |
| `cc1_88194337fb11d855b262460672bf3fd415a8eef0f7680290c9d578d184f111b4` | `ulist239.f63` | `eltdx.shortline.open_volume_hand` |
| `cc1_52682e639052b2f97ed470f93320e2da0006ad18b0054f83eb19429c6db687e2` | `ulist239.f63` | `eltdx.shortline.open_volume_ratio` |

先前的 `20261119_ulist239_f63_eltdx_open_amount.md` 把第一行的开盘金额理由误用于第二行的候选 ID。台账会保留原审阅事件；本文件及后续决定更正当前审阅状态。此前对 ZHB 开盘金额候选的独立审阅不受影响。

## 对齐样本

从 `20261102`、`03`、`04`、`05`、`06`、`09`、`10`、`17`、`18` 共 9 个交易日，按 Ulist `f124` 北京时间日期和 ELTDX `target_trade_date` 对齐 20 只股票，共 180 组。Ulist 可选 `f297` 日期也与样本日一致；无日期错配。

| ELTDX 字段 | 报告相关性 (Pearson / Spearman) | 原值相等 | 固定比例诊断 |
| --- | ---: | ---: | --- |
| `shortline.open_amount` | 0.8953 / 0.9764 | 1 / 180 | 非零金额比例中位数 2.7974，范围 0.9997–30.9268；最佳固定比例绝对相对误差中位数 31.39%、P90 70.10% |
| `shortline.open_volume_hand` | 0.4177 / 0.8244 | 0 / 180 | 非零量比中位数 4,845.055，范围 281.838–806,603.353；最佳固定比例误差中位数 54.36%、P90 84.80% |
| `shortline.open_volume_ratio` | 0.3608 / 0.7050 | 0 / 180 | 非零量比中位数 5,346,016.141，范围 20,599.227–209,586,598.173；最佳固定比例误差中位数 71.97%、P90 95.22% |

ELTDX 契约把 `open_volume_hand` 定义为 09:25 正式撮合成交量（手），把 `open_volume_ratio` 定义为该成交量相对于最近 5 个完整交易日平均每分钟成交量的倍数。它们的尺度和含义不同；总体相关不能替代逐值/换算校验。

## 处置与边界

- 更正并分别拒绝上述三个候选的同义/固定比例映射。对金额字段只有 1 组原值相等；量与量比字段没有原值相等。固定比例误差均远大于舍入可能造成的偏差。
- 高频共同变化说明这些量可能共同受股票规模或交易活跃度影响，不说明 `f63` 的业务语义，也不排除未测试的其他数学关系。
- `f63` 仍保持 `unverified`；本次不改注册表或主字典。
- Efinance 仓库在 `stock/fflow/kline/get` 请求中也使用了 `f63`，而它的行情快照另走 `ulist.np/get`；这只作为路径隔离线索，不作为本项目字段释义。参考：[Efinance `getter.py`](https://github.com/Micro-sheep/efinance/blob/main/efinance/common/getter.py#L2005-L2014)。
- 本次检索到的东方财富官方材料没有提供 `ulist.np/get::f63` 的精确字段契约；官方对“主力净流入”的计算说明不能用来认定此字段：[东方财富金融终端常见问题](https://emdesk.eastmoney.com/pc_activity/Pages/VIPTrade/pages/link/gnjs.html)。
