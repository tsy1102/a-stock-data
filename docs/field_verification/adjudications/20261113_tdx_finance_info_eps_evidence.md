# TDX `finance_info.eps` 来源内语义定案

核验日：2026-11-13。只裁决 `(TDX(双命名源), eps)`；不把同名字段扩展到其他来源，不创建跨来源映射。

## 字段身份和采集路径

注册表身份为 `TDX(双命名源)::eps`，注册表 `path` 为 `eps`。实际归档位置是 `raw_tdx.json:stocks[代码].finance_info.eps`。`scripts/capture_tcp_collectors.py::collect_tdx` 将 `tdx_get_finance_info()` 的返回值写入该对象；采集过程不改写此值。

当前 ELTDX 适配器的 `_FIN_MAP` 将上游 `FinanceRecord.eps_raw` 直接放到兼容列 `eps`，配置的 `yuan` 分支不做数值换算。项目锁定的 ELTDX v3.3.2 上游文档说明 `finance_batch()` 对应 TDX `0x0010`，并把 `FinanceRecord.eps_raw` 定义为“每股收益原始值”。该文档是适配器的上游模型契约，不是通达信公开的完整字段代码表；它没有指定基本/稀释子口径、报告期选择规则或精度/舍入方式。

保留期内 `2026-10-15` 至 `2026-11-12` 有 18 个 `meta.data_date` 与目录一致、同时保存 TDX 和 ELTDX 数据的日期目录。逐股票比较 `finance_info.eps` 与 `finance_batch[].eps_raw`，共 360 条配对记录，360/360 完全相同，20 只股票，差异 0。该比较证明项目旧式字段与 `0x0010` 已有契约字段的同源对应；两条序列化路径不算独立数据商证据，也不把 360 条重复快照当成 360 份财报。

## 报告锚和日期资格

另从 `2026-11-10` 与 `2026-11-12` 两个目标数据日重算 20 只股票的 TDX 字段与 Fuyao 财务行。两日的 TDX、Fuyao 来源状态均为 `ok`；Fuyao `as_of_date` 分别等于 `2026-11-10` 和 `2026-11-12`。每只股票的财务行均是 2026 年 Q3、报告期末 `2026-09-30`、币种 CNY；Fuyao 行记录的披露日期不晚于对应样本日。TDX `updated_date` 保留为财务记录更新日，未替代采集目录 `data_date`，也未把它强行解释成报告披露日。

40 个股票日比较覆盖 20 份不同股票的 Q3 财务行；两个数据日重复的是同一批报告，不作为新增独立财报。TDX EPS 与 `basic_eps` 的绝对差在 40/40 条中均不超过半分（`0.005 元/股`），最大差为 `0.005`。38/40 条 TDX 原值落在百分之一元的刻度上；其余两条是同一股票 600519 在两个日期的 `51.529998779296875`，与 `51.53` 的差约 `0.00000122`，符合浮点表示误差。逐行值和报告日期见 [`20261113_tdx_eps_financial_samples.csv`](../research/20261113_tdx_eps_financial_samples.csv)；原始输入为两个数据日的 `raw_tdx.json`、`raw_fuyao.json` 和 `meta.json`。

两个区分力样本以发行人三季报复核：

| 股票 | TDX `finance_info.eps` | 报告披露值 | 结论 |
|:---|---:|---:|:---|
| 旺能环境 002034 | `1.3200000524520874` | 基本 / 稀释 EPS 均为 `1.32 元/股` | 与报告值相符；东方财富 F10 的基本 EPS 计算值另为 `1.2531`，不能把它与披露 EPS 混为一谈。 |
| 深南电 A 000037 | `0` | 年初至报告期末基本 / 稀释 EPS 均为 `0.0050 元/股` | 恰为半分边界；与按分表示的 `0.00` 相容，但不能据此确定上游采用截断、银行家舍入或其他规则。 |

旺能环境三季报镜像标示公告日期为 `2026-10-27`，发行人公告列表将该报告列在 `2026-11-02`。两者均早于 `2026-11-10` 首个样本日；本结论只用“报告已在样本日之前公开”作准入判断，不据此裁定两种列表日期差异的根因。深南电 A 三季报报告日期为 `2026-10-28`，同样早于样本日。

东方财富旺能环境 F10 对基本每股收益明确区分“计算值”和“披露值”：计算值按最新报告期归母净利润除以最新总股本，披露值来自上市公司财报。002034 的 TDX 值与报告披露值 `1.32` 相符，而 Push2 `f55=1.253127235` 是公式计算值。该黄金锚进一步排除了把 TDX EPS 与 `f55` 当成同一字段的高相关误配。此处只作语义区分，不建立 TDX—Push2 映射。

## 结论与边界

将精确路径 `TDX(双命名源)::eps` 定案为 `eps_raw`，单位 `元/股`，来源内含义为：

> 每股收益原始值；上游契约及现有可区分样本未确认基本/稀释子口径、报告期选择规则或小数精度/舍入规则。

“每股收益”类别和单位已由上游 `0x0010` 模型契约、项目逐路径映射、保留原始样本及发行人报告相互印证。基本/稀释子口径和精度机制继续保留为未决边界，不因此阻止本次较宽字段类别的来源内定案。TDX 与 Push2、ZHB 均不新增 `mappings`。

## 公开资料

- [ELTDX v3.3.2 METHOD_REFERENCE.md §财务基础信息](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/METHOD_REFERENCE.md)：`finance_batch()` 对应 `0x0010`，`eps_raw` 为每股收益原始值。
- [ELTDX v3.3.2 FIELD_REFERENCE.md §FinanceRecord](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md)：`FinanceRecord.eps_raw` 字段契约。
- [东方财富旺能环境 F10 最新指标说明](https://emweb.eastmoney.com/PC_HSF10/OperationsRequired/Index?code=sz002034&type=web)：区分基本 EPS 计算值与财报披露值。
- [旺能环境 2026 年第三季度报告](https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=12660359&stockid=002034)：报告列出 2026 年前三季度基本与稀释 EPS 均为 1.32 元/股。
- [旺能环境发行人公告列表](https://www.wannaenergy.com/investor/announcement?page=1)：列有 2026 年三季度报告；公告列表日期与报告镜像页面标示日期不一致，二者均先于样本日。
- [深南电 A 2026 年第三季度报告](https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=12666251&stockid=000037)：报告列出前三季度基本与稀释 EPS 均为 0.0050 元/股。
