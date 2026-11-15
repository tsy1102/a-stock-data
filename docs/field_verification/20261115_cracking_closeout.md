# 2026-11-14 至 2026-11-15 破解工作收口与复核

收口日期：2026-11-15；本次复核日期：2026-11-16。复核范围为 11 月 14–15 日已登记的裁决、研究记录、当前逐源注册表，以及 2026-10-15 起保留的 ELTDX 样本。没有运行采集。

## 最近成果

- **来源身份和采集路径**：修正 TDX 行情嵌套字段的来源血缘，区分当前原始字段、项目派生值和旧复合回退值；补查 TDX 股本及 XDXR 日期/类别字段，并记录字段没有精确路径证据时仍待核的边界。
- **来源契约和字段定案**：按已锁定版本或官方定义，处理 ELTDX 行情、日期、题材与 K 线系列字段，东财 Push2/Push2EX 字段，以及 Fuyao 竞价涨幅等来源内定义。已观察的近似数值按精度容差分析；未确认的来源日期、单位、枚举和跨源关系继续留空或待核。
- **旧路径和误报治理**：退役 Fuyao 未实际输出的旧根路径及 5 个 ELTDX Helper 未限定叶名；将 Push2EX 时间 token 和列表容器从字段候选中分离；修正 Push2EX 的字段范围，避免把其他接口的字段误投到 `stock/get`。
- **采集与证据维护**：记录 Push2EX 昨日涨停池的采集缺口并补入接口采集；修正两份既有 E3 证据摘要。此类工作不自动构成字段语义定案。

逐项结论和边界见[近期裁决与研究索引](README.md#近期裁决与研究记录)及其链接的裁决文件。

## ELTDX 核心路径样本复核

逐行表保留 18 个目标数据日目录中的 360 条归档记录。按 `meta.sources.eltdx` 接收计数，17 个目录为 `status=ok` 且 `n_expected=n_received=20`，共 340 条完整来源记录；2026-10-19 的 `n_received=0`，该日 20 行保留作审计但不计入有效样本。CSV 每行保留 raw/meta SHA-256、来源状态、接收数和资格标记，规范 LF SHA-256 为 `2bfec3a7ef0ff89bceb96bc3e7276f6fbee51e16bd1986a84a276e6bd5736e9a`。

| 核查 | 结果 | 解释 |
|---|---:|---|
| `shortline.target_trade_date` 与目录目标数据日 | 340/340 一致 | 只说明有效归档中这条 helper 日期路径与目录日期相符；ELTDX 没有来源级 `as_of_date`，不据此确认来源实际数据日。 |
| `shortline.code` 与股票键；`exchange`/`market_id` 与代码前缀的组合 | 各 340/340 一致 | 支持当前 ShortlineIndicator 路径的标识一致性，不扩展到其他上下文路径。 |
| `shortline.pre_close` 与同股票、同日 `quote_snapshot.pre_close_price` | 340/340 精确相同 | 是同一 ELTDX 来源族内的路径核对，不单独证明其他来源字段同义。 |
| `shortline.pre_close` 与同日 TDX `quote_raw.last_close` | 318/318 可比记录精确相同；22 条 TDX 值缺失 | 10-19 的 20 行不计入完整来源样本；缺值不是数值冲突，ELTDX 来源日期仍未确认。 |

注册表已分别将 `shortline.pre_close`（昨收，元）、`shortline.code`、`shortline.full_code`、`shortline.exchange`、`shortline.market_id` 和 `quote_snapshot.pre_close_price` 按完整路径记录。新样本仅补充这些路径之间的实证关系，未产生新的语义裁决或跨源 `mappings`。

其中 `code`、`exchange`、`full_code`、`market_id`、`pre_close` 的无前缀注册身份已按单独的路径审计退役；这不把各嵌套路径合并或升级。无前缀 `volume` 仍为 `unverified`：历史表指向 `TradeTick.volume`，而保留样本出现的是盘口档位量，不能混为一谈。详见 [ELTDX Helper 未限定路径裁决](adjudications/20261115_eltdx_unqualified_helper_paths.md)。

逐行原值、资格标记及 raw/meta 哈希见 [`20261115_eltdx_core_helper_fields_samples.csv`](research/20261115_eltdx_core_helper_fields_samples.csv)。逐路径序列化位置审计见 [`20261115_eltdx_unqualified_helper_path_inventory.csv`](research/20261115_eltdx_unqualified_helper_path_inventory.csv)。既有来源契约见 [ELTDX ShortlineIndicator 字段裁决](adjudications/20261109_eltdx_shortline_fields.md)和 [ELTDX 快照字段裁决](adjudications/20261109_eltdx_quote_snapshot_fields.md)。

## 收口后的 11 月 15 日补充核查

后续提交 `7a5ea85` 又完成新浪三表字段语义复核：覆盖 16 个归档目录、960 个报表包装对象和 91,168 行科目数据；`item_value` 按科目取报表值，单位随科目变化，`item_tongbi` 为小数同比比例（7/7 个公开财报页面复算通过），`report_type` 则是项目请求类别回显。完整样本和哈希见 [`新浪财报字段裁决`](adjudications/20261115_sina_financial_item_semantics.md)及其引用清单。

本次补充收口 Fuyao 财务指标结构：保留期 18 个目录、360 条记录中，17 日的 340 条有效指标记录均包含五类非空分组对象，`fin_report` 均记录项目选中的 `2026-2` 请求期。四个已登记分组根路径归类为采集输出容器，`fin_report` 归类为项目生成的请求标签；它们不再进入默认破解目标，但仍在“已证伪”审计分组留痕。这些结论不会改变分组内指标语义，也不把请求标签当作来源实际数据日或报告期内容证明。核验记录和逐目录 raw/meta 哈希见 [Fuyao 分组容器与请求期标签核查](adjudications/20261115_fuyao_container_and_report_label.md)。

本次再补查 ELTDX Helper 历史无前缀路径：18 个目录中只有 17 个满足完整接收条件，340 条有效股票记录里五个旧 token 均未作为 `stocks.<ticker>` 根键出现，只存在于带对象上下文的完整路径。故将 5 个旧注册身份标为 `disproved / retired_legacy_path`；不改变已验证完整路径的状态，不创建映射。另有 2026-10-19 归档虽保留 20 行数据，但来源元数据 `n_received=0`；这些行已从有效比较数排除。ELTDX 无 `as_of_date`，本轮只作路径身份裁决，不作日期敏感碰撞或语义推断。

以上收口没有运行采集，也没有新增跨源映射。黄金锚或来源内契约只支持其精确完整路径；未确认子字段覆盖与指标实际报告期仍留作后续独立核验。

## 注册表与闭环检查

- 截至本补充收口，2,633 条 `source_fields` 状态分布为：`verified` 1,506、`unverified` 1,017、`conflict` 28、`disproved` 81、`candidate` 1。未验证状态不等同于所有条目都在本轮碰撞队列中。
- 上述数量是 Fuyao 路径复核前的收口快照。随后核查 Fuyao 5 个精确身份后，注册表为 `verified` 1,507、`unverified` 1,012、`conflict` 28、`disproved` 85、`candidate` 1。Fuyao 的 `date_ms`、`probe_trading_day` 是项目派生请求元数据，`financials`、`market` 是采集容器，`indicators` 仅确认官方接口数组结构；详情见 [Fuyao 采集日期元数据与输出容器路径核查](adjudications/20261115_fuyao_capture_path_disambiguation.md)。
- 再退役 5 个 ELTDX 无前缀路径身份后，当前 2,633 条 `source_fields` 为：`verified` 1,507、`unverified` 1,007、`conflict` 28、`disproved` 90、`candidate` 1。五项仅为路径身份纠正，没有新定案业务字段；`volume` 仍待核。
- [`../../scripts/registry_parity.py`](../../scripts/registry_parity.py) 通过：历史来源基线、聚合视图、字段矩阵一致；93 条来源契约、88 条来源实证、8 条裁决补充和 2 条采集路径补录均通过；181 条未验证候选列在 [`../unknown_fields.md`](../unknown_fields.md)。18 条类型/token、容器或已审计退役路径依规排除。
- Fuyao 补充裁决仅将四个分组根路径和一个请求期标签移出字段语义破解队列，保留其旧状态证据；未改变嵌套指标语义、采集代码或跨源映射。

## 后续边界

- 对剩余未验证项，继续先核对 `(source, 完整 code path)` 和采集器实际输出路径，再决定能否使用当前样本。
- TDX `quote_raw.last_close` 的 22 条缺值需与不匹配分开处理；当前 318 条完整样本精确相同只支持样本中观测到的关系，不替代接口契约。ELTDX 来源级日期仍未确认。
- 未确认来源日期的采集值继续受证据资格规则约束；稳定的字段契约可作来源内释义，不据此补造跨源等价关系。
