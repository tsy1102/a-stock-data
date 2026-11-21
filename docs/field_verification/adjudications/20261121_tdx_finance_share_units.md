# TDX 0x0010 股本槽位与兼容输出单位核查（2026-11-21）

## 裁决范围

核对 `TDX(双命名源)` 当前兼容输出中的五个股本路径：`liutongguben`、`zongguben`、`guojiagu`、`bgu`、`hgu`。字段含义不变；注册表的 `unit` 记录适配器交给项目消费者的输出单位，应为“股”。本记录不把 `ELTDX` 原始 FinanceRecord 路径的“万股”改成“股”。

`zhigonggu` 不在本次范围内：项目固定的 ELTDX v3.3.2 FinanceRecord 文档没有 `zhi_gong_gu_raw_float`，当前 `_FIN_MAP` 也没有对应映射；不能因为 0x0010 历史解析表里有该槽位就推断当前适配器会输出它。

## 上游字段、项目变换与消费路径

固定版本 [ELTDX v3.3.2 7709 财务基础信息文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/methods/7709-%E8%B4%A2%E5%8A%A1%E5%9F%BA%E7%A1%80%E4%BF%A1%E6%81%AF.md)将 `liu_tong_gu_ben_raw_float`、`zong_gu_ben_raw_float`、`guo_jia_gu_raw_float`、`b_gu_raw_float`、`h_gu_raw_float` 标为原始“万股”；文档还将 `circulating_shares`、`total_shares` 定义为相应原始值乘 10,000。项目 `core/eltdx_adapter.py::_FIN_MAP` 将这五个字段归一到 TDX 兼容路径，`finance()` 对 `scale == "shares"` 统一乘 10,000。`core/data_provider.py` 与 `stock_common/sc_capital_cache.py` 按“股”消费 `zongguben`、`liutongguben`，再在各自统一层按需要转换。

总股本映射曾把 `zong_gu_ben_raw_float` 错写为 `zhongguben`，而项目消费者读取 `zongguben`。本次修正适配器键名，并将 `TDX(双命名源)::zongguben` 的 canonical 补为 `zongguben`。历史拼写 `zhongguben` 不再由当前 ELTDX 适配器输出；留存 raw 文件不改写。

## 留存样本的适配器版本边界

对 22 个同时留有 `raw_tdx.json` 和 `raw_eltdx.json` 的日期目录、每目录 20 只股票，将 TDX 兼容输出与同次 ELTDX `finance_batch[0]` 原始字段逐项比较。逐日逐字段计数见 [`research/20261121_tdx_share_unit_transition.csv`](../research/20261121_tdx_share_unit_transition.csv)：五个路径合计 1,386 组非零配对，全部无差异。

- 17 个数据目录（2026-10-15 至 2026-11-10）：TDX 输出与 ELTDX 原始万股数值相同，适配器当时直出原值。
- 5 个数据目录（2026-11-12 至 2026-11-19）：TDX 输出逐项等于 ELTDX 原值乘 10,000，输出单位为股。首个该类样本的 `data_date` 为 2026-11-12，TDX 来源采集开始时间为 2026-11-12 23:17:30；这是留存样本观测到的边界，不代表精确代码部署时刻。
- 例如农业银行 601288：2026-11-10 的 `liutongguben` 为 31,924,422，`zhongguben` 为 34,998,304，`hgu` 为 3,073,882.25；2026-11-12 起对应输出为 319,244,220,000、349,983,040,000、30,738,822,500。两个时期的 raw_tdx 值不可直接当作同单位历史序列。

2026-11-19 碰撞报告的七交易日窗口为 11-11 至 11-19；该窗口内留有的 TDX 财务样本从 11-12 开始，均处于乘 10,000 的输出口径。本核查不重写任何旧样本，也不把 11-10 及更早的 raw_tdx 股本值当作当前“股”口径；跨越这条边界的历史比较须先按采集版本归一。

样本汇总 CSV 的规范 LF SHA-256：`0379048e8d927ba51a59a243addaa59df7bfc664b2f3b716379c6df396be841b`。

## 官方发行人资料交叉核验

农业银行发行人募集说明书列明截至 2026-06-30 普通股总数 349,983,033,873 股，其中人民币普通股（A 股）319,244,210,777 股、境外上市外资股（H 股）30,738,823,096 股（[上交所披露的发行人募集说明书](https://static.sse.com.cn/stock/disclosure/announcement/c/202610/601288_20261008_VHEH.pdf)，股权结构表）。与 2026-11-12 TDX 兼容输出同量级，且三项差值均小于协议原始“万股”值乘 10,000 后的单个万股刻度；文件日期与 TDX 财务更新日不相同，所以该资料只作单位量级交叉核验，不声称数值同日精确相等，也不把细小差额归因于某一种舍入算法。

## 定案

当前 TDX 兼容输出的五个注册路径单位统一为“股”；ELTDX 原始 FinanceRecord 路径仍为“万股”。注册表更新只改当前兼容输出元数据及其错误总股本 key，不改原始归档、来源身份或跨源 mappings。旧键 `zhongguben` 的历史样本跨越上述两种适配器输出尺度，仅供按目录/来源采集时点解释，不作为当前接口键。
