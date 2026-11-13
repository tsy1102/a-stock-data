# ELTDX 财务批量字段路径核对（2026-11-11）

> 后续状态更新：两条原“发起人法人股/法人股”候选路径已按保留样本和公开报告定案为上年同期归母净利润、上年同期营业收入；完整证据见[来源内经验裁决](20261111_eltdx_share_slots_empirical_semantics.md)。

本记录将 `finance_batch[]` 返回对象中的完整字段路径登记到主注册表。叶字段名与实际采集路径是两个不同的记录口径；采集侧身份使用完整路径 `finance_batch[].<field>`。

| 完整采集路径 | 当前结论 | 说明 |
|---|---|---|
| `finance_batch[].gu_dong_ren_shu_raw_float` | 已核实 | 股东人数，单位户；官方三季报样本与字段值相符。 |
| `finance_batch[].zhu_ying_shou_ru_raw_float` | 已核实 | 主营收入，与报告“营业收入”行对应，单位千元；报表展示与原始值存在可解释的精度差异。 |
| `finance_batch[].zhu_ying_li_run_raw_float` | 已核实 | 保留样本中原始值对应 2026Q3 报告“营业成本”，单位千元；ELTDX v3.3.2 标签仍写“主营利润”，冲突单独记录。 |
| `finance_batch[].ying_ye_li_run_raw_float` | 已核实 | 营业利润，单位千元；报表展示与原始值存在可解释的精度差异。 |
| `finance_batch[].zong_xian_jin_liu_raw_float` | 已核实 | 总现金流；保留样本对应经营、投资、筹资活动净额之和，不含汇率变动影响，单位千元。 |
| `finance_batch[].fa_qi_ren_fa_ren_gu_raw_float` | 已定案：上年同期归母净利润，千元 | 拼音及 ELTDX 标签“发起人法人股”作为冲突证据保留；五家发行人 2025 年 1—9 月比较数及保留样本值转移核验见[来源内 E3 裁决](20261111_eltdx_share_slots_empirical_semantics.md)。服务端槽位为何与标签不同仍未定。 |
| `finance_batch[].fa_ren_gu_raw_float` | 已定案：上年同期营业收入，千元 | 拼音及 ELTDX 标签“法人股”作为冲突证据保留；五家发行人 2025 年 1—9 月比较数及保留样本值转移核验见[来源内 E3 裁决](20261111_eltdx_share_slots_empirical_semantics.md)。服务端槽位为何与标签不同仍未定。 |

五个已核实字段登记为完整采集路径，不建立它们与其他接口字段的映射。两项 `finance_batch[]` 股本字段已由后续实证裁决解决；无 `finance_batch[]` 前缀的同名叶路径仍是不同注册身份，不因完整采集路径的定案而自动升级。

`finance_batch[].zhu_ying_li_run_raw_float` 的逐股、逐报告期数值和上游标签冲突见[ELTDX `zhu_ying_li_run` 实际返回语义定案](20261111_eltdx_zhu_ying_li_run_empirical_semantics.md)。

日期格式 `YYYYMMDD` 与这里的财务数值字段无关。TDX 0x0010 的 `updated_date` 和 `ipo_date` 是真实日期信息字段，含义分别为财报更新日期和上市日期；`YYYYMMDD` 是它们的值格式，不是字段路径，也不是应从字段文档清理掉的残留。详见 [TDX 财务日期字段定案](20261111_tdx_finance_date_fields.md)。
