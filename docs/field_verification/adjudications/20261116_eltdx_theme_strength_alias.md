# ELTDX 题材强度重复 Helper 路径审查（2026-11-16）

## 结论

保留采集输出 `global_helpers.theme_strength_rank`，停止重复调用并输出 `global_helpers.stock_theme_strength_rank`。项目固定 `eltdx==3.3.2` 中，`stock_theme_strength_rank(codes, **kwargs)` 直接返回 `theme_strength_rank(codes, **kwargs)` 的结果；采集器对两者传入完全相同的 `codes=ecodes`。保留期内两份完整序列化对象在 19/19 个采集目录中完全相同，10 个非空日期重复产生了 310 行题材排行。

这只移除采集器中的重复 helper 调用，不退役 ELTDX 客户端兼容方法，不删改历史 raw，不建立跨源映射，也不据此改变 `rank` 的注册表语义。`TDX-eltdx(适配层)::rank` 仍是未限定路径；实时排行与题材排行的 `rank` 必须按完整对象路径分开处理。ELTDX 元数据未记录 `as_of_date`，本项只使用固定版本代码和样本证明调用/序列化重复，不把 ELTDX 目录日期当作来源实际日期，也不作数值碰撞。

## 证据

- `requirements.txt` 固定 `eltdx==3.3.2`。该版本的 `helpers/core.py` 中 `stock_theme_strength_rank` 是 `theme_strength_rank` 的委托别名；题材强度排序仅依据连板天梯与题材聚合逻辑生成。
- 采集器此前在 `scripts/capture_tcp_collectors.py` 中以同一股票池分别调用两个 helper。历史样本逐日比较完整 helper JSON（包括 `trade_date` 与 `rows`），19/19 相等；10 个有行日期分别保存 310 行，两边各 310 行；其余日期均为空表。2026-11-16 当日两张表也均为空。
- 逐目录样本日期、来源状态、两张表的行数/相等性及 raw/meta SHA-256 见 [`research/20261116_eltdx_theme_strength_alias_audit.csv`](../research/20261116_eltdx_theme_strength_alias_audit.csv)。规范 LF SHA-256：`e1e991442575fc092c4d15c170a3fa56dd9aaebad7d3a522fea10b6a2e7f9a03`。
- 同期新浪字段 `[32]` 的审计见 [`research/20261116_sina_field32_value_audit.csv`](../research/20261116_sina_field32_value_audit.csv)，用于解释本轮若干低质量 L4 数值重叠，不用于本次 Helper 调整。规范 LF SHA-256：`9d1a2f6870f06180acab99a6712c17161d09d3bd11aef7d78ea0ac24fd2b96aa`。

## 来源契约与变更范围

- 题材强度输出模型说明：[ELTDX v3.3.2 题材强度排行](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/helpers/%E9%A2%98%E6%9D%90%E5%BC%BA%E5%BA%A6%E6%8E%92%E8%A1%8C.md)。`ThemeStrengthRow.rank` 是题材聚合排序位置；它不是实时个股涨幅榜的同一字段语义。
- 实时排行输出模型说明：[ELTDX v3.3.2 实时榜单](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/helpers/%E5%AE%9E%E6%97%B6%E6%A6%9C%E5%8D%95.md)。实时排行的 `rank` 是按请求排序结果生成的列表位置。
- 保留历史 `stock_theme_strength_rank` 路径供考古与碰撞审查；自本次代码变更后，采集器只保存 `theme_strength_rank`。未发现其他运行时消费者依赖该重复路径，相关调用仅位于采集器与其测试桩。
- 测试在北交所股票池场景中断言题材强度 helper 只调用一次；若采集器再次调用别名，测试立即失败。

本地固定版本文档和源文件用于核实委托关系；本记录不声称本轮通过浏览器核验了上游网页或底层 TDX 协议字段。
