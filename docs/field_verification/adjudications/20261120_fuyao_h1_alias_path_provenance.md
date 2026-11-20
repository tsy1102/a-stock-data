# Fuyao H1 摘要路径来源审计

复核日期：2026-11-20。未运行采集。本次审计从保留起点 `2026-10-15` 起检查 Fuyao 输出路径、采集器构造方式和财报期样本；最新已有目录 `20261119` 的 `data_date` 与 Fuyao `as_of_date` 均为 2026-11-19，运行日期为 2026-11-20。

## 裁决

以下四个未验证身份都不是 Fuyao 响应中的独立原始字段，将其移出上游字段破解队列：

| 精确注册身份 | 裁决 | 实际输出身份 |
| --- | --- | --- |
| `同花顺-fuyao::h1_indicators` | `disproved` / `collector_output_container` | 项目 JSON 容器 `market.h1_indicators`，按股票代码保存 H1 摘要对象 |
| `同花顺-fuyao::h1_indicators_ready` | `disproved` / `project_derived_capture_output` | 项目布尔哨兵 `market.h1_indicators_ready`，取决于对首只股票的 H1 请求是否返回 |
| `同花顺-fuyao::ded_weighted_roe` | `disproved` / `project_derived_capture_output` | 项目别名 `market.h1_indicators.<code>.ded_weighted_roe`，复制 `profitability.index_deduct_weighted_avg_roe` |
| `同花顺-fuyao::weighted_roe` | `disproved` / `project_derived_capture_output` | 项目别名 `market.h1_indicators.<code>.weighted_roe`，复制 `profitability.index_weighted_avg_roe` |

这里的 `disproved` 只否定这四个短键是 Fuyao 上游原始字段的身份，不否定项目输出值，也不撤销完整 Fuyao 字段路径的既有释义。完整路径 `profitability.index_deduct_weighted_avg_roe` 与 `profitability.index_weighted_avg_roe` 仍分别保留在[总资产指标裁决](20261114_fuyao_asset_metrics_source_contract_evidence.md)和[盈利比率裁决](20261114_fuyao_ratio_source_contract_evidence.md)中。本次不新增跨源 `mappings`，不改变生产采集和来源路由。

## 调用链与字段完整路径

- [`capture_catalog.py`](../../../scripts/capture_catalog.py) 将 `market.h1_indicators_ready` 和 `market.h1_indicators` 声明为采集器输出路径，而非 Fuyao 接口响应键。
- [`capture_verified_collectors.py`](../../../scripts/capture_verified_collectors.py) 先按 `2026-2`、`2026-1` 的顺序获取每只股票的财务指标；另对首只股票单独请求当年 `-2` 报告期作为哨兵。哨兵有返回时，采集器再将该期 `profitability` 中的两个完整字段复制到按股票代码组织的 `market.h1_indicators` 对象；`h1_indicators_ready` 是 `bool(sentinel)`，不代表所有股票都完整返回。
- Fuyao 完整字段的官方定义及百分数单位见[官方财务指标契约镜像](../../verify/fuyao_api_full.md)和既有裁决 `20261114-fuyao-index_deduct_weighted_avg_roe-contract`、`20261114-fuyao-profitability-index_weighted_avg_roe-contract`。本次仅确认项目输出血缘，不重新裁决这两个完整路径的语义或单位。

## 保留样本审计

逐目录路径和状态见[输出路径清单](../research/20261120_fuyao_h1_output_path_inventory.csv)；逐股票、逐完整字段的上游值、项目别名值、报告期、来源日期及对应 raw/meta SHA-256 见[逐样本清单](../research/20261120_fuyao_h1_alias_samples.csv)。两份 CSV 均使用规范 LF 摘要：

- 输出路径清单 SHA-256：`704b608f10da3f7e87ac449c217f01e9ce86e54ca82e55db7462622e24b4e10a`
- 逐样本清单 SHA-256：`f1eb34842fb47794dfe71425702256fbd45b86df3b2ece9386449c678facfa6c`

审计覆盖 2026-10-15 至 2026-11-19 的 22 个保留目录、440 条股票记录。Fuyao 来源状态 22/22 为 `ok`；将 `as_of_date` 的连字符规范化后，22/22 与 `meta.data_date` 相同。

- 2026-10-15 的目录中，`h1_indicators_ready=false`、摘要容器为空；两个完整字段和两个别名各有 20 条缺值。缺值不作零值或反例处理。
- 其后 21 个目录各有 20 条股票记录；`fin_report` 均为 `2026-2`。每个完整路径与其对应摘要别名均有 420 个成对非空值，420/420 精确相等，0 个不匹配。项目将上游字段值原样复制，未发现单位转换或额外计算。
- 最新 `20261119` 目录的运行日是 2026-11-20，目标数据日和 Fuyao 来源实际日期均为 2026-11-19。此前目录也是同一 `2026-2` 财报期的重复快照；它们证明序列化路径和拷贝关系，不是 21 个独立报告期，也不构成跨源独立证据。
- 最近四个目录的 `meta.capture_units.fuyao.fin_indicators.request_parameters.h1_report_period` 明确记录 `2026-2`；较早目录未记录该参数，但每只股票的 `fin_report` 均记录同一期间。未用自然日差异推断财报日期。

## 注册表处理

将以上四个精确 `(source, code path)` 标记为 `disproved`，并分别使用 `collector_output_container` 或 `project_derived_capture_output`。四条原始 `unverified` 状态快照写入 `superseded_status_evidence`；不改写原始采集归档、完整 Fuyao 业务字段状态或历史证据。
