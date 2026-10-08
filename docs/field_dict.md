# 主字段字典

> 本页是字段治理入口与权威规则索引。机器字段记录以 `field_registry.json` 为准；
> 字段状态、来源路径和证据均按 `(source, 完整 code path)` 登记。
> 本页及矩阵/待破解队列由 `scripts/gen_field_dict.py` 生成，请勿手改。

## 权威顺序

1. `field_verification/field_registry.json`：逐源字段、完整路径、状态与证据的机器权威。
2. `field_verification/source_lineage.json`：运行时来源别名、独立来源族与仓库关系。
3. 本页：治理入口；`field_matrix.md` 与 `unknown_fields.md` 是 registry 派生视图。
4. `field_source_reference.md`：重整前完整原文，逐字节保留作历史证据；不得用它覆盖当前状态。

## 状态与锚点规则

- `verified` 表示字段语义已经确认。只有来源谱系可确认、运行时来源匹配且完整路径精确相同时，才可作为碰撞锚点。
- `unverified`、`candidate` 是默认破解目标；`conflict` 可作为待复核目标但不能作锚，碰撞候选不能替代证据冲突复核。
- `disproved` 单独归档，不进入默认破解队列。
- 未登记来源、路径不完整或来源独立性未确认时，不参与默认 L1 定案。

## 当前覆盖

- 来源：28 个。
- 逐源字段路径：2469 条；verified 830、unverified 1548、candidate 1、conflict 90、disproved 0。
- 矩阵：[`field_matrix.md`](field_matrix.md)。
- 待破解与状态冲突：[`unknown_fields.md`](unknown_fields.md)。
- 来源与 GitHub 仓库映射：[`source_repository_map.md`](source_repository_map.md)。
- 已验证字段描述缺口：207 条缺少含义、47 条缺少规范名，见 [`field_metadata_gaps.md`](field_metadata_gaps.md)；缺口本身不自动改变状态。
- 完整历史正文：[`field_source_reference.md`](field_source_reference.md)。

## 规则和方法

- 对撞规则：[`field_verification/COLLISION_RULES.md`](field_verification/COLLISION_RULES.md)。
- 破解方法：[`field_verification/CRACKING_METHODOLOGY.md`](field_verification/CRACKING_METHODOLOGY.md)。
- 字段验证记录：[`field_verification/`](field_verification/)。每条结论须保留日期、样本、来源和证据。
- 已验证字段描述缺口：[`field_metadata_gaps.md`](field_metadata_gaps.md)。
- 对撞结果不会自动定案；人工复核和注册表同步流程见 [`field_verification/ADJUDICATION_WORKFLOW.md`](field_verification/ADJUDICATION_WORKFLOW.md)。
- 来源分组及 GitHub 对应关系以 `field_verification/source_lineage.json` 为准；未确认项明确标为 unconfirmed。

## 来源分字典

| 来源 | 分字典 | 主要章节 |
|:--|:--|:--|
| 东财-push2(stock/get) | [verify/push2_verify.md](verify/push2_verify.md) | 12.3.1 单股行情 `stock/get`（已由 get_em_quote_full 验证） |
| 东财-资金流(em_fund_flow) | [verify/push2_verify.md](verify/push2_verify.md) | 12.3.4 资金流四档层级 `stock/get` f135\~f149 **全量**（🆕 V17.0.16 **重定案** / V17.1.x **补登 f147/f148**） |
| 腾讯(qt.gtimg) | [verify/tencent_verify.md](verify/tencent_verify.md) | 12.1 腾讯 qt.gtimg.cn 完整字段字典（88 字段） |
| 同花顺-fuyao | [verify/fuyao_api_full.md](verify/fuyao_api_full.md) | 12.8.12c THS 官方金融数据 REST API（fuyao.aicubes.cn，2026-08-10 实测 7 接口 → V17.0.5 契约全量镜像 62 端点）🆕 |
| TDX(双命名源) | [verify/tdx_func_fields.md](verify/tdx_func_fields.md) | 12.13.2 财务批量（get_finance_batch，0x0010）文档确认 |
| AxData | [verify/axdata_verify.md](verify/axdata_verify.md) | 12.12.8 跨源接口实测确认（2026-08-05，axdata 0.1.3 local 模式） |
| 东财-push2_full | [verify/push2_verify.md](verify/push2_verify.md) | 12.3.1 单股行情 `stock/get`（已由 get_em_quote_full 验证） |
| ZHB-tdxstat | [verify/tdx_func_fields.md](verify/tdx_func_fields.md) | 1. `tdxstat.cfg` (个股综合统计快照，35 个字段，7,951 行) |
| ZHB-tdxstat2 | [verify/tdx_func_fields.md](verify/tdx_func_fields.md) | 2. `tdxstat2.cfg` (成交与资金流向表，21 个字段，7,951 行) |
| ZHB-tipinfo | [verify/tdx_func_fields.md](verify/tdx_func_fields.md) | 3. `tipinfo.dat` (财报日历与业绩快照，22 列，5,612 行) |
| levistock(ftshare) | [verify/levistock_field_verify.md](verify/levistock_field_verify.md) | 12.10.3 开盘红市场情绪（market_emotion_kph，**含历史**）🆕 |

## 维护命令

```powershell
python.exe scripts\gen_field_dict.py
python.exe scripts\gen_field_matrix.py
python.exe scripts\verify_sync_check.py
python.exe scripts\registry_parity.py
```
