# 主字段字典

> 本页是字段治理入口与权威规则索引。机器字段记录以 `field_registry.json` 为准；
> 字段状态、来源路径和证据均按 `(source, 完整 code path)` 登记。
> 本页及矩阵/待破解队列由 `scripts/gen_field_dict.py` 生成，请勿手改。

## 权威顺序

1. `field_verification/field_registry.json`：逐源字段、完整路径、状态与证据的机器权威。
2. `field_verification/source_lineage.json`：运行时来源别名、独立来源族与仓库关系。
3. `field_verification/source_identity_reclassifications.json`：旧混合来源字段在历史档案与当前来源身份之间的显式映射。
4. 本页：治理入口；`field_matrix.md` 与 `unknown_fields.md` 是 registry 派生视图。
5. `field_source_reference.md`：重整前完整原文，逐字节保留作历史证据；不得用它覆盖当前状态。

## 状态与锚点规则

- 普通来源的 `verified` 字段要成为独立来源碰撞锚，还要求含义非空且非占位、含义/单位无冲突或对齐歧义、来源独立性已确认，并且运行时来源与完整路径精确匹配。
- `source_role=documented_contract_anchor` 且字段证据为 `official_contract` 时，官方文档可直接确认该来源字段含义；其多日强匹配单列 `L1-C`，不声称上游来源独立，也不自动定案。
- 规范名的别名差异不会单独阻止碰撞；字段含义缺失/占位或含义/单位存在冲突时，碰撞器会将该 verified 路径重新纳入待破解目标，并排除为锚。
- `unverified`、`candidate` 是默认破解目标；`conflict` 可作为待复核目标但不能作锚，碰撞候选不能替代证据冲突复核。
- `disproved` 单独归档，不进入默认破解队列。
- 未登记来源、路径不完整或来源独立性未确认时，不参与默认 L1 定案。
- AxData 是多提供方接口框架；当前 `stock_shortline_indicators_tdx` 属于 TDX 来源族。AxData 接口盘点只作框架参考，不能作为独立来源或锚；详见 [`axdata_field_reconciliation_20261010.md`](axdata_field_reconciliation_20261010.md)。
- Levistock 是多源客户端包装库。已归属的 KPH 记录映射到 KPH 来源族；FTShare 私有托管 MCP 集成已退役，其字段仅留作历史证据，底层来源未确认、不作独立锚。其余历史记录保留为未归属证据，不计为 Levistock 数据源；字段映射见 [`source_identity_reclassifications.json`](field_verification/source_identity_reclassifications.json) 与 [`levistock_source_reconciliation_20261010.md`](field_verification/levistock_source_reconciliation_20261010.md)。

## 当前覆盖

- 来源身份与参考登记：33 项；是否可作独立锚由来源谱系单独判定。
- 逐源字段路径：2550 条；verified 964、unverified 1502、candidate 1、conflict 81、disproved 2。
- 矩阵：[`field_matrix.md`](field_matrix.md)。
- 待破解与状态冲突：[`unknown_fields.md`](unknown_fields.md)。
- 来源与 GitHub 仓库映射：[`source_repository_map.md`](source_repository_map.md)。
- 已验证字段描述缺口：199 条含义为空/占位、45 条缺少规范名，见 [`field_metadata_gaps.md`](field_metadata_gaps.md)；质量问题会阻止其作为碰撞锚。
- 同短 code 的聚合歧义、缺失定义和疑似合并文本单独列在 [`field_aggregate_review.md`](field_aggregate_review.md)；该清单不覆盖逐源定义，也不自动拆分字段。
- 完整历史正文：[`field_source_reference.md`](field_source_reference.md)。

## 规则和方法

- 对撞规则：[`field_verification/COLLISION_RULES.md`](field_verification/COLLISION_RULES.md)。
- 破解方法：[`field_verification/CRACKING_METHODOLOGY.md`](field_verification/CRACKING_METHODOLOGY.md)。
- 字段验证记录：[`field_verification/`](field_verification/)。每条结论须保留日期、样本、来源和证据。
- 已验证字段描述缺口：[`field_metadata_gaps.md`](field_metadata_gaps.md)。
- 对撞结果不会自动定案；人工复核和注册表同步流程见 [`field_verification/ADJUDICATION_WORKFLOW.md`](field_verification/ADJUDICATION_WORKFLOW.md)。
- 无独立数值锚但有权威单源接口/协议定义的字段，可按上游契约流程核验；该结论不建立跨源映射或来源锚。
- 来源分组及 GitHub 对应关系以 `field_verification/source_lineage.json` 为准；未确认项明确标为 unconfirmed。

## 来源身份与框架参考索引

登记类别说明：框架、包装适配器、服务接口与历史未归属记录均明确标注；跨源定案仍按来源谱系的 `independence_family` 和 `anchor_eligible` 判定。

| 来源身份 | 登记性质 | 分字典 | 主要章节 |
|:--|:--|:--|:--|
| AxData | 多源框架参考（非独立来源） | [verify/axdata_verify.md](verify/axdata_verify.md) | 12.12.8 跨源接口实测确认（2026-08-05，axdata 0.1.3 local 模式） |
| TDX(双命名源) | 运行时来源身份（独立性按来源谱系判定） | [verify/tdx_func_fields.md](verify/tdx_func_fields.md) | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| ZHB-tdxstat | 运行时来源身份（独立性按来源谱系判定） | [verify/tdx_func_fields.md](verify/tdx_func_fields.md) | 1. `tdxstat.cfg` (个股综合统计快照，35 个字段，7,951 行) |
| ZHB-tdxstat2 | 运行时来源身份（独立性按来源谱系判定） | [verify/tdx_func_fields.md](verify/tdx_func_fields.md) | 2. `tdxstat2.cfg` (成交与资金流向表，21 个字段，7,951 行) |
| ZHB-tipinfo | 运行时来源身份（独立性按来源谱系判定） | [verify/tdx_func_fields.md](verify/tdx_func_fields.md) | 3. `tipinfo.dat` (财报日历与业绩快照，22 列，5,612 行) |
| FTShare | 已退役的托管服务（仅保留历史证据） | [verify/ftshare_fields_mirror.md](verify/ftshare_fields_mirror.md) | 12.20.1 FTShare 股吧/评论原始字段补录（V17.1.1 全量登记） |
| Levistock历史未归属 | 历史未归属（不作来源锚） | [verify/levistock_field_verify.md](verify/levistock_field_verify.md) | 未能按逐字段证据归属的历史接口记录 |
| 开盘红(Levistock适配) | 已映射提供方的接口组件 | [verify/levistock_field_verify.md](verify/levistock_field_verify.md) | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |
| 东财-push2(stock/get) | 运行时来源身份（独立性按来源谱系判定） | [verify/push2_verify.md](verify/push2_verify.md) | 12.3.1 单股行情 `stock/get`（已由 get_em_quote_full 验证） |
| 东财-push2_full | 已停用的重复采集入口（历史身份；由 东财-push2(stock/get) 覆盖） | [verify/push2_verify.md](verify/push2_verify.md) | 12.3.1 单股行情 `stock/get`（已由 get_em_quote_full 验证） |
| 东财-资金流(em_fund_flow) | 运行时来源身份（独立性按来源谱系判定） | [verify/push2_verify.md](verify/push2_verify.md) | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 同花顺-fuyao | 运行时来源身份（独立性按来源谱系判定） | [verify/fuyao_api_full.md](verify/fuyao_api_full.md) | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| 开盘啦(kpl_limit_up_detail) | 运行时来源身份（独立性按来源谱系判定） | [verify/kph_kpl_history_verify.md](verify/kph_kpl_history_verify.md) | KPH 与 KPL 涨停明细核验（2026-09-29/30 双交易日） |
| 开盘红 | 运行时来源身份（独立性按来源谱系判定） | [verify/kph_kpl_history_verify.md](verify/kph_kpl_history_verify.md) | KPH 与 KPL 涨停明细核验（2026-09-29/30 双交易日） |
| 腾讯(qt.gtimg) | 运行时来源身份（独立性按来源谱系判定） | [verify/tencent_verify.md](verify/tencent_verify.md) | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |
| FTShare REST | 官方文档定义字段语义的契约锚（底层数据来源未确认） | [verify/ftshare_rest_contract.md](verify/ftshare_rest_contract.md) | — |

## 维护命令

```powershell
.\scripts\run_with_system_python.ps1 scripts\gen_field_dict.py
.\scripts\run_with_system_python.ps1 scripts\gen_field_matrix.py
.\scripts\run_with_system_python.ps1 scripts\verify_sync_check.py
.\scripts\run_with_system_python.ps1 scripts\registry_parity.py
.\scripts\run_with_system_python.ps1 scripts\refresh_field_registry_projection.py --check
```
