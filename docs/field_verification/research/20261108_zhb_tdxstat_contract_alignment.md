# ZHB `tdxstat` 字段契约与别名核验（2026-11-08）

## 范围与保留期

本次只核验 `ZHB-tdxstat` 的 `[2]`、`[26]`、`[31]`、`[32]`、`[33]`，以及解析器暴露的 `stat.unknown_2`、`stat.unknown_26`。只读取文件名日期不早于 2026-10-15 的 ZHB 样本；未用清理前数据回填。

ZHB 文件名日期是数据日期。ELTDX 每条短线统计记录另有 `stats_date`，比较时按该日期匹配 `zhb_YYYYMMDD.zip`，并核对包内股票行日期。不能按采集目录日期直接比较：采集批次可能包含前一交易日的统计值，会产生错位假差异。

## 上游资料

- 通达信官方 `get_more_info_batch` 字段表：<https://help.tdx.com.cn/quant/docs/markdown/mindoc-1hjbidnohpjn4/mindoc-1hlir5r0t9hgc.html>。文档列出 `BetaValue`（贝塔系数）、`YearZTDay`（年涨停天数）、`LastStartZT`（几天）、`LastZTHzNum`（几板）及 `EverZTCount`（连板天）。官方字段表没有公布 `tdxstat.cfg` 原始列号，也没有说明 `BetaValue` 的计算窗口、比较基准，或“几天几板”的窗口边界。
- ELTDX 对 `tdxstat.cfg` 的公开解析说明：<https://github.com/electkismet/eltdx/blob/main/docs/methods/7709-%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96.md> 与 <https://github.com/electkismet/eltdx/blob/main/docs/helpers/%E7%9F%AD%E7%BA%BF%E6%8C%87%E6%A0%87.md>。该项目将零基列 `[2]`、`[26]`、`[31]`、`[32]`、`[33]` 分别命名为 `beta_60d`、`year_limit_up_days`、`limit_stat_days`、`limit_up_count_in_stat_days`、`limit_up_streak_days`。ELTDX 是社区实现并读取同一类通达信数据，属于列位交叉参考，不视为独立数据提供方或官方字段名。
- 本项目解析器直接读取对应列：`core/zhb_client.py::_parse_tdxstat()` 中 `[2]` → `stat.unknown_2`、`[26]` → `stat.unknown_26`、`[31]` → `stat.zt_streak_cycle`、`[32]` → `stat.zt_count`、`[33]` → `stat.zt_lianban`。

## 日期对齐结果

比较范围为 11 个有效数据日期、每日期 20 只股票，共 220 个股票日配对：`20261016`、`20261019`、`20261022`、`20261023`、`20261027`、`20261028`、`20261030`、`20261102`、`20261103`、`20261104`、`20261106`。两批因目标日期超出保留期或缺少对应 ZHB 文件而未纳入分母。

| ZHB 列 | ELTDX 列名 | 精确相等 | 两边均空 | 差异 | 解释 |
|---|---|---:|---:|---:|---|
| `[2]` | `beta_60d` | 220 | 0 | 0 | 样本值对齐；官方语义只定为贝塔系数，不把 60 日窗口提升为官方定义 |
| `[26]` | `year_limit_up_days` | 220 | 0 | 0 | 与官方 `YearZTDay` 年涨停天数相符 |
| `[31]` | `limit_stat_days` | 39 | 181 | 0 | 39 组有值完全相等，其余 181 组两边均空；对应“几天” |
| `[32]` | `limit_up_count_in_stat_days` | 39 | 181 | 0 | 39 组有值完全相等，其余 181 组两边均空；对应“几板” |
| `[33]` | `limit_up_streak_days` | 28 | 192 | 0 | 28 组有值完全相等，其余 192 组两边均空；与现有已验证“连板数”一致 |

数值比较使用同一数据日的原始列值，不做舍入容差。该结果证明同日列值一致，不证明两个程序是独立数据源；`[31]/[32]` 的精确窗口起止条件仍未由官方文档公开。

## 裁决

1. `[2]` 的语义为通达信 `BetaValue`（贝塔系数）。`stat.unknown_2` 与同源 `[2]` 是解析器别名，保留路径身份，采用相同语义和单位；不再把 ELTDX 的 `60d` 名称写成官方计算周期。
2. `[26]` 的语义为 `YearZTDay`（年涨停天数）。`stat.unknown_26` 与同源 `[26]` 是解析器别名；将该遗留候选冲突按同源别名证据收敛为已验证。
3. `[31]`、`[32]` 分别登记为“几天几板”统计中的天数和板数，单位为“天”和“板”。不推断统计窗口边界、起点算法或非涨停日回填规则。
4. `[33]` 已是已验证字段，样本与官方 `EverZTCount`（连板天）及 ELTDX 对应列一致，本次不重复写入裁决。
5. 不新增跨源映射。以上字段同属 ZHB/通达信来源；对 ELTDX 的值相等只记录为同源列位与实现交叉核验。
