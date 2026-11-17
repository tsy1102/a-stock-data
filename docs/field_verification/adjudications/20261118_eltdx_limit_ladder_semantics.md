# ELTDX `limit_ladder` 字段来源契约定案

复核日期：2026-11-18

来源身份：`TDX-eltdx(适配层)`

样本保留边界：2026-10-15

## 结论

为 `limit_ladder` 下本轮发现的 17 个完整路径分别建立来源内释义。ELTDX v3.3.2 的 `limit_ladder()` 返回 `ShortlineIndicator` 行并按涨停状态筛选；项目采集器将行字段原样写到 `stocks.<code>.limit_ladder.<field>`。因此注册的是这些完整路径，字段语义范围限定为项目固定版本 ELTDX Helper 输出，不声称它们是通达信线协议的原生字段，也不建立跨来源 `mappings`。

现有 `shortline.<field>` 是同一个上游模型中的另一条序列化路径。本报告同时按契约补全这 17 个已验证路径的含义与适用日期范围，以免两个路径的字典定义互相矛盾；其中 `seal_to_amount_ratio` 的单位由无量纲记号 `-` 更正为 `倍`。历史元数据和旧证据仍保留在注册表的裁决记录中。

## 精确字段路径

| 字段 | 含义 | 单位 | 来源口径或公式 |
|---|---|---|---|
| `auction_prev_volume_ratio` | 今日开盘竞价成交量相对上一实际交易日 09:25 竞价成交量的倍数 | 倍 | `open_volume_hand / prev_open_volume_hand` |
| `beta_60d` | 近 60 日 Beta；基准为 TDX 统计资源使用的市场基准，具体基准未公开 | - | `tdxstat.cfg` 直接值 |
| `open_amount` | 09:25 正式撮合的开盘成交金额 | 元 | ELTDX `0x054c` 快照字段 |
| `open_change_pct` | 开盘价相对昨收的涨跌幅 | % | `(open_price - pre_close) / pre_close × 100` |
| `open_prev_amount_ratio` | 今日 09:25 开盘竞价金额占上一实际交易日全天成交额的比例 | % | `open_amount / prev_amount × 100` |
| `open_price` | 当前目标交易日开盘价 | 元 | ELTDX `0x054c` 快照字段 |
| `open_turnover_z` | 09:25 竞价成交量占自由流通股本 Z 的比例；Z 为自由流通口径 | % | `open_volume_hand / (free_float_shares / 100) × 100` |
| `open_volume_hand` | 09:25 正式撮合成交量 | 手 | `open_amount / (open_price × 100)` |
| `open_volume_ratio` | 开盘成交量相对最近 5 个完整交易日平均每分钟成交量的倍数 | 倍 | `open_volume_hand / (近 5 日日 K 成交量合计 / 1200)`；需至少 5 根完整日 K |
| `pe_ttm` | 滚动市盈率；当前估值相对最近 12 个月利润的倍数 | 倍 | `tdxstat.cfg` 直接值 |
| `pre_close` | 当前目标交易日涨跌幅基准的昨收价 | 元 | ELTDX `0x054c` 快照字段 |
| `prev_amount` | 上一实际交易日全天成交金额 | 元 | 按交易日对齐 `tdxstat2.cfg` |
| `prev_open_amount` | 上一实际交易日 09:25 开盘竞价成交金额 | 元 | 按交易日对齐 `tdxstat2.cfg` |
| `prev_open_volume_hand` | 上一实际交易日 09:25 开盘竞价成交量 | 手 | 按交易日对齐 `tdxstat2.cfg` |
| `seal_to_amount_ratio` | 当前买一金额相对当日成交额的倍数；只有已封板时才按封单成交额比解释 | 倍 | `seal_amount / amount` |
| `seal_to_float_ratio` | 当前买一金额占自由流通市值 Z 的比例；只有已封板时才按封流比解释 | % | `seal_amount / free_float_market_value × 100` |
| `year_limit_up_days` | 截至统计文件日期记录的当年累计涨停天数；统计文件落后目标日时不包含目标日新增结果 | 天 | `tdxstat.cfg` 直接值 |

完整身份分别为 `TDX-eltdx(适配层)::limit_ladder.<字段>` 和 `TDX-eltdx(适配层)::shortline.<字段>`。相同叶名不合并身份，也不以此推定与其他供应商字段等价。

## 上游契约与项目路径

项目固定 `eltdx==3.3.2`。项目采集器在 `scripts/capture_tcp_collectors.py` 调用 `client.helpers.limit_ladder(codes=ecodes)`，将结果放入 `global_helpers.limit_ladder`，再把每条 `LimitLadderTable.rows` 记录写入相应股票的 `stocks.<code>.limit_ladder`。没有对 `ShortlineIndicator` 行内字段做重命名或单位换算。

ELTDX v3.3.2 的[连板天梯 Helper 文档](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/helpers/%E8%BF%9E%E6%9D%BF%E5%A4%A9%E6%A2%AF.md)说明 `limit_ladder()` 基于 `shortline_indicators()`，返回 `ShortlineIndicator` 行并筛选封板/可选触板股票；[短线指标字段契约](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/helpers/%E7%9F%AD%E7%BA%BF%E6%8C%87%E6%A0%87.md)列明上述字段的含义、单位、直接来源、日期对齐和计算公式；[固定版本实现](https://github.com/electkismet/eltdx/blob/v3.3.2/src/eltdx/helpers/shortline.py)用于核对模型和公式。这里引用的是 ELTDX 客户端公开输出契约，不把它扩大解释为 TDX 官方线协议字段表。

通达信官方快照文档将 `Open` 定义为开盘价、`LastClose` 定义为前收盘价；这与 Helper 文档中 `open_price`、`pre_close` 的字段角色一致。官方定义用于核对底层快照字段角色，项目最终登记仍以确切 ELTDX Helper 输出路径为准。

## 留存样本与日期资格

2026-11-18 04:46（北京时间）的开盘前采集命令正常结束。`20261117` 已存在完整收盘目录，采集器按幂等规则跳过重复请求；8 点前未补采 ZHB。当天没有新增 ELTDX raw 样本。本裁决使用既有保留样本，并通过本轮碰撞报告确认候选仍在待核清单。

审计仅读取 `2026-10-15` 起且 `meta.data_date` 与目录名一致的 20 个归档目录。ELTDX 行内 `target_trade_date` 与目录 `data_date` 一致的记录共 14 条，覆盖 6 只股票、11 个目标交易日：2026-10-16、10-20、10-21、10-23、10-26、10-28、10-30、11-02、11-04、11-10、11-17。每个 `limit_ladder` 字段均有 14 条非空值，并与同一 raw 中同股同日 `shortline.<field>` 的值 14/14 精确一致。此比较验证固定 Helper 模型在两条项目序列化路径上的一致性；它不是两个独立来源，也不单独决定语义。

七个可用归档输入复算的计算字段均在 14/14 行精确吻合 Helper 值（比较前按 Helper 输出的 6 位小数精度规范化）：`open_change_pct`、`open_volume_hand`、`open_turnover_z`、`open_prev_amount_ratio`、`auction_prev_volume_ratio`、`seal_to_float_ratio`、`seal_to_amount_ratio`。`open_volume_ratio` 需要最近 5 根完整日 K；Beta、TTM PE、上一日统计值和年内涨停统计是统计资源直接值，raw 归档没有相应底层文件或中间列，故不伪造独立复算结果。其语义按固定版本契约确认。

逐字段逐股票值、公式复算、目录数据日、短线路径对照及 raw/meta SHA-256 见 [`research/20261118_eltdx_limit_ladder_path_samples.csv`](../research/20261118_eltdx_limit_ladder_path_samples.csv)。本轮完整碰撞报告见 [`20261118/preopen_0446_latest/20261118_collision_report.md`](../20261118/preopen_0446_latest/20261118_collision_report.md)。

## `open_amount` 的跨路径差异

`limit_ladder.open_amount` 与 `shortline.open_amount` 在 14/14 条同源同日样本中完全相等；与另一个项目路径 `quote_snapshot.open_amount_yuan` 对比时，仅 3/14 完全相等，最大绝对差为 40 元，最大相对差为 0.00185%。差异原因没有被证明，因此不标注为舍入或时点差；保留两条完整路径、差异和原始哈希，不建立别名或跨路径映射。该差异不推翻 Helper 对其输出字段的明确语义，但后续若需要证明两个快照路径可互换，仍须另行追查其底层响应时点/字段来源。

## 裁决边界

- 17 个 `limit_ladder.*` 精确路径及其对应 `shortline.*` 路径均在逐源注册表中标记为 `verified`，核验依据为 ELTDX v3.3.2 Helper 输出契约。
- 同源重复输出只作为路径映射与序列化佐证，不登记 `mappings`，不把它们计成独立来源或独立日期证据。
- 不依据这些 Helper 名称宣称底层 TDX 原始字段 ID；`beta_60d` 使用的具体市场基准仍未公开，`open_amount` 两种快照路径的小额差异原因仍未定。
