# Fuyao 采集日期元数据与输出容器路径核查

复核日期：2026-11-15。未运行采集。本次只核对精确来源路径身份，不解释财务叶字段，不创建跨源映射。

## 结论

| 注册表身份 | 处置 | 核查结论 |
|---|---|---|
| `同花顺-fuyao::date_ms` | `disproved` / `project_derived_capture_output` | 项目由 `probe_trading_day` 生成上海时区零点毫秒戳，并把它作为限价池请求参数；不是 Fuyao 响应字段，也不是来源实际数据日。 |
| `同花顺-fuyao::probe_trading_day` | `disproved` / `project_derived_capture_output` | 项目从 `last_completed_trading_day()` 生成的请求日期标记；不能独立证明 Fuyao 响应实际对应的日期。 |
| `同花顺-fuyao::financials` | `disproved` / `collector_output_container` | `stocks.<ticker>.financials` 是采集器归并四个报表输出路径的对象容器；四组表值仍由各自叶路径维护。 |
| `同花顺-fuyao::market` | `disproved` / `collector_output_container` | 顶层 `market` 是市场类采集输出容器，承载基准、涨跌停池、异动等独立路径。 |
| `同花顺-fuyao::indicators` | `verified` / `verified_by_source_contract` | Fuyao 指标接口的 `data.abilities[].indicators[]` 是包含 `index_id` 与 `value` 的条目数组，不是单一财务指标。项目解析器读取后按能力和指标 ID 展平到 `fin_indicators`。 |

`disproved` 在前四项表示这些精确注册路径不是提供方的独立业务字段，并不表示采集结果错误。`indicators` 的 verified 仅确认上游数组容器契约；不会把数组容器当成业务指标，也不外推其子项语义。

## 代码与接口对应

- [`capture_verified_collectors.py`](../../../scripts/capture_verified_collectors.py) 在 `collect_fuyao()` 中先取 `td = deps.last_completed_trading_day()`，再生成 `probe_trading_day = td.isoformat()` 和 `date_ms = datetime.combine(td, 00:00).timestamp() * 1000`。这两个值写入采集输出根部；`date_ms` 又作为 `limit_up_pool`、`limit_down_pool`、`limit_break_pool` 的请求参数。
- [`capture_catalog.py`](../../../scripts/capture_catalog.py) 将四类财报分别登记到 `stocks.*.financials.income_q/income_a`、`balance_q`、`cashflow_q` 等叶路径；指标接口输出登记为 `stocks.*.fin_indicators`、`fin_report` 及两个市场级辅助路径。它没有将 `financials` 或 `market` 根对象定义为接口字段。
- [`sc_fuyao.py`](../../../stock_common/sc_fuyao.py) 的 `get_fuyao_fin_indicators()` 遍历 `data.abilities[]`，从每个能力项读取 `indicators[]`，再把每个条目的 `index_id` 映射到 `value`。因此上游数组路径和项目序列化的 `fin_indicators.<ability>.<index_id>` 是不同层级，不能混为同一个标量字段。
- 项目保存的 [Fuyao 官方接口契约镜像](../../verify/fuyao_api_full.md) 在财务指标响应表中定义 `data.abilities[].indicators[]` 为指标列表，并定义条目 `index_id` / `value`。该接口镜像固定于项目登记的 V17.0.5 契约版本。

## 保留样本审计

逐目录结构与哈希清单见 [`20261115_fuyao_capture_path_inventory.csv`](../research/20261115_fuyao_capture_path_inventory.csv)。CSV 规范 LF SHA-256：`ee01272f4c7c42a2ada8bda8bcf526fd0870ba5f0556babfeec9f595ed78fdf1`。审计只读取 [`capture_retention.py`](../../../scripts/capture_retention.py) 指定的 `2026-10-15` 起的 18 个 Fuyao raw/meta 归档：

- 18/18 个目录的 `meta.data_date`、`meta.sources.fuyao.as_of_date`、根部 `probe_trading_day` 相互对应；18/18 个 Fuyao 状态为 `ok`，每目录 20 条股票记录，共 360 条。
- 根部 `date_ms` 在 18/18 个目录均解码为对应 `probe_trading_day` 的 Asia/Shanghai 零点。
- 顶层 `market` 在 18/18 个 raw 中都是对象。采集目录列出的业务内容位于它的子路径。
- `stocks.<ticker>.financials` 在 360/360 条记录中为对象，包含 `income_q`、`balance_q`、`cashflow_q`、`income_a` 四个子路径。每个子路径在 338/360 条记录中有非空列表；空列表不改变父路径的容器性质，也不表示数值 0。
- 18 个保留 raw 中均没有独立键 `indicators`。这是因为适配器消费上游 `indicators[]` 后展平；原始响应数组未被单独序列化。该缺键只用于确认项目输出结构，不当作接口失败或数值证据。

本次未使用 ZHB 样本：这些路径属于 Fuyao 请求元数据、项目对象容器或接口响应容器，不是待建立的行情/财务字段关系。没有改动采集代码、采集路由、叶字段状态或 `mappings`。

## 注册表处理

四条非业务路径保留原状态快照、代码路径和逐日期证据，移出默认字段释义目标；`indicators` 登记其上游数组路径及项目展平关系。报告和 CSV 是本次决定的审计证据。所有结论均按精确 `(source, code path)` 限定，不传播至其他来源的同名 `market`、`financials`、`date_ms` 或 `indicators`。
