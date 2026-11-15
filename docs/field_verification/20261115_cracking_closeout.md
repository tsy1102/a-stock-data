# 2026-11-14 至 2026-11-15 破解工作收口与复核

复核日期：2026-11-15。复核范围为 11 月 14–15 日已登记的裁决、研究记录、当前逐源注册表，以及 2026-10-15 起保留的 ELTDX 样本。没有运行采集。

## 最近成果

- **来源身份和采集路径**：修正 TDX 行情嵌套字段的来源血缘，区分当前原始字段、项目派生值和旧复合回退值；补查 TDX 股本及 XDXR 日期/类别字段，并记录字段没有精确路径证据时仍待核的边界。
- **来源契约和字段定案**：按已锁定版本或官方定义，处理 ELTDX 行情、日期、题材与 K 线系列字段，东财 Push2/Push2EX 字段，以及 Fuyao 竞价涨幅等来源内定义。已观察的近似数值按精度容差分析；未确认的来源日期、单位、枚举和跨源关系继续留空或待核。
- **旧路径和误报治理**：退役 Fuyao 未实际输出的旧根路径；将 Push2EX 时间 token 和列表容器从字段候选中分离；修正 Push2EX 的字段范围，避免把其他接口的字段误投到 `stock/get`。
- **采集与证据维护**：记录 Push2EX 昨日涨停池的采集缺口并补入接口采集；修正两份既有 E3 证据摘要。此类工作不自动构成字段语义定案。

逐项结论和边界见[近期裁决与研究索引](README.md#近期裁决与研究记录)及其链接的裁决文件。

## ELTDX 核心路径样本复核

新增逐行核验表覆盖保留边界内 18 个目标数据日、20 只股票，共 360 条股票日记录。表中每行保留 `raw_eltdx.json` SHA-256；CSV 规范 LF SHA-256 为 `16860d204259646d9b5af2a9b8daaf543f19cbb2864d8d695db931ea321ddacc`。

| 核查 | 结果 | 解释 |
|---|---:|---|
| `shortline.target_trade_date` 与目录目标数据日 | 360/360 一致 | 只说明这条 ELTDX helper 日期路径与目标数据日相符。 |
| `shortline.code` 与股票键；`exchange`/`market_id` 与代码前缀的组合 | 各 360/360 一致 | 支持当前模型行的标识一致性，不扩展到其他未定位的裸路径。 |
| `shortline.pre_close` 与同股票、同日 `quote_snapshot.pre_close_price` | 360/360 精确相同 | 是同一 ELTDX 来源族内的路径核对，不单独证明其他来源字段同义。 |
| `shortline.pre_close` 与同日 TDX `quote_raw.last_close` | 338/338 可比记录精确相同；22 条 TDX 值缺失 | 缺值不是数值冲突；现有样本没有观测到不匹配。 |

注册表已分别将 `shortline.pre_close`（昨收，元）、`shortline.code`、`shortline.full_code`、`shortline.exchange`、`shortline.market_id` 和 `quote_snapshot.pre_close_price` 按完整路径记录。新样本仅补充这些路径之间的实证关系，未产生新的语义裁决或跨源 `mappings`。

相同叶名的 `TDX-eltdx(适配层)::pre_close`、`::volume`、`::code`、`::full_code`、`::exchange`、`::market_id` 是独立注册身份；当前仍为 `unverified`。本 CSV 不含这些裸路径的来源定位证据，不能将嵌套路径的结论移植给它们。

逐行原值及 raw 哈希见 [`20261115_eltdx_core_helper_fields_samples.csv`](research/20261115_eltdx_core_helper_fields_samples.csv)。既有来源契约见 [ELTDX ShortlineIndicator 字段裁决](adjudications/20261109_eltdx_shortline_fields.md)和 [ELTDX 快照字段裁决](adjudications/20261109_eltdx_quote_snapshot_fields.md)。

## 收口后的 11 月 15 日补充核查

后续提交 `7a5ea85` 又完成新浪三表字段语义复核：覆盖 16 个归档目录、960 个报表包装对象和 91,168 行科目数据；`item_value` 按科目取报表值，单位随科目变化，`item_tongbi` 为小数同比比例（7/7 个公开财报页面复算通过），`report_type` 则是项目请求类别回显。完整样本和哈希见 [`新浪财报字段裁决`](adjudications/20261115_sina_financial_item_semantics.md)及其引用清单。

本次补充收口 Fuyao 财务指标结构：保留期 18 个目录、360 条记录中，17 日的 340 条有效指标记录均包含五类非空分组对象，`fin_report` 均记录项目选中的 `2026-2` 请求期。四个已登记分组根路径归类为采集输出容器，`fin_report` 归类为项目生成的请求标签；它们不再进入默认破解目标，但仍在“已证伪”审计分组留痕。这些结论不会改变分组内指标语义，也不把请求标签当作来源实际数据日或报告期内容证明。核验记录和逐目录 raw/meta 哈希见 [Fuyao 分组容器与请求期标签核查](adjudications/20261115_fuyao_container_and_report_label.md)。

以上收口没有运行采集，也没有新增跨源映射。黄金锚或来源内契约只支持其精确完整路径；未确认子字段覆盖与指标实际报告期仍留作后续独立核验。

## 注册表与闭环检查

- 截至本补充收口，2,633 条 `source_fields` 状态分布为：`verified` 1,506、`unverified` 1,017、`conflict` 28、`disproved` 81、`candidate` 1。未验证状态不等同于所有条目都在本轮碰撞队列中。
- [`../../scripts/registry_parity.py`](../../scripts/registry_parity.py) 通过：历史来源基线、聚合视图、字段矩阵一致；93 条来源契约、88 条来源实证、8 条裁决补充和 2 条采集路径补录均通过；181 条未验证候选列在 [`../unknown_fields.md`](../unknown_fields.md)。18 条类型/token、容器或已审计退役路径依规排除。
- Fuyao 补充裁决仅将四个分组根路径和一个请求期标签移出字段语义破解队列，保留其旧状态证据；未改变嵌套指标语义、采集代码或跨源映射。

## 后续边界

- 对剩余未验证项，继续先核对 `(source, 完整 code path)` 和采集器实际输出路径，再决定能否使用当前样本。
- TDX `quote_raw.last_close` 的 22 条缺值需与不匹配分开处理；当前 338 条精确相同只支持样本中观测到的关系，不替代接口契约。
- 未确认来源日期的采集值继续受证据资格规则约束；稳定的字段契约可作来源内释义，不据此补造跨源等价关系。
