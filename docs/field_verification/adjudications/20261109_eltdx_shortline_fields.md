# ELTDX 短线指标 32 个字段定案

## 定案范围

本裁决处理 `TDX-eltdx(适配层)` 的 32 个此前未验证字段。字段路径是 `stocks.<code>.shortline.<field>`；同一 ShortlineIndicator 模型还出现在 `global_helpers.limit_ladder.rows[].<field>`。这些路径语义一致，本次逐字段登记来源契约，不登记任何跨源映射，也不改变运行时取数。

依据项目固定的 ELTDX v3.3.2、其短线指标字段文档与本机安装的同版实现。16 个保留数据日包含 320 个股票日样本；字段键均在短线模型中出现。ZHB 对照只读取 2026-10-15 起的日期化归档，并按 ZHB 文件名作为包数据日。

## 上游契约与路径

`scripts/capture_field_probe.py::collect_eltdx` 经 `scripts/capture_tcp_collectors.py::collect_eltdx` 调用 `client.helpers.shortline_indicators(codes)`。上游字段模型明确分为统计资源直接字段、计算字段和实时行情/普通流通口径字段；日期对齐由 TDX 目标交易日、上一实际交易日和统计包主导日期共同决定。

- [ELTDX v3.3.2 短线指标字段与公式](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/helpers/%E7%9F%AD%E7%BA%BF%E6%8C%87%E6%A0%87.md)
- [ELTDX v3.3.2 通用字段参考](https://github.com/electkismet/eltdx/blob/v3.3.2/docs/FIELD_REFERENCE.md)

## 历史样本核验

### 公式与运行时

公式字段按上游 v3.3.2 运行时代码回算。以下非空样本均在项目采用的舍入容差内一致：

| 字段 | 样本核对 |
|---|---:|
| `open_change_pct` | 保留样本公式重算320/320一致。 |
| `open_turnover_z` | 319个非空分子/分母样本重算319/319一致。 |
| `open_prev_amount_ratio` | 319个非空样本重算319/319一致。 |
| `auction_prev_volume_ratio` | 314个非空样本重算314/314一致。 |
| `open_prev_seal_ratio` | 16个非空样本重算16/16一致。 |
| `seal_to_float_ratio` | 319个非空样本重算319/319一致。 |
| `seal_prev_ratio` | 16个非空样本重算16/16一致。 |
| `seal_to_amount_ratio` | 319个非空样本重算319/319一致。 |
| `free_float_market_value` | 319个非空样本重算319/319一致。 |
| `float_market_value` | 320/320一致。 |
| `open_volume_hand` | 320/320按开盘金额/(开盘价×100)重算一致。 |
| `limit_board_text` | 320/320按统计日期、当前封板状态及窗口字段重算一致。 |
| `ladder_level` | 320/320按统计日期、当前封板状态及文件连板值重算一致。 |

`open_volume_ratio` 按上游明示公式“09:25 开盘成交量 ÷ 最近 5 个目标日前完整交易日平均每分钟成交量”定案。运行时代码请求 6 根日 K、排除目标日后取 5 根；字段采集归档中的独立 `kline_day` 仅保留 5 根且包含目标日，因此不能独立复算此值。按目标日前筛选后 319 个非空字段均缺少第 5 根对齐日 K；该样本限制不构成字段矛盾。

`limit_board_text` 与 `ladder_level` 的日期边界分别经源代码回算 320/320 一致：当统计文件日期为上一交易日且当前状态为 sealed 时，窗口天数/次数与连板高度计入目标日；直接字段 `limit_up_streak_days`、`year_limit_up_days` 仍保留统计文件原值。百分比字段按上游约定已经乘以 100，倍数字段的 1.0 表示相等。

### ZHB 统计资源对照

按文件名日期处理 11 个保留 ZHB 包，共完成 280 个股票日对照。`beta_60d`、`prev_amount`、`prev_seal_amount`、`prev2_seal_amount`、`prev_open_volume_hand`、`prev_open_amount`、`limit_stat_days`、`limit_up_count_in_stat_days`、`limit_up_streak_days`、`year_limit_up_days` 均为 280/280 相符。金额字段经十进制/浮点转换后最大差值分别不超过 2.38e-7 和 2.98e-8（仅 `prev2_seal_amount`、`prev_open_amount` 有可见微差）。

保留两项单日数值差异：2026-10-30 的 `pe_ttm`（代码 920508：ELTDX 205.03，ZHB 378.86）和 `free_float_shares`（代码 688553：ELTDX 376,263,800 股，ZHB 377,665,400 股）各有 1 条不一致，其余各 279/280 相符。2026-11-02 的对应输出与 2026-10-30 ZHB 包值相符。现有材料无法确定该单日差异是统计快照版本还是采样时点造成，因此保留为值级证据差异；它不推翻 ELTDX 明确的来源契约，也不建立跨源逐值映射。

对照跳过 2026-10-14 统计日期（早于保留起点）及缺少 `zhb_20261021.zip` 的数据日；不回补或读取保留起点之前材料。

## 字段裁决

| 字段 | 定案含义 | 单位 | 证据/边界 |
|---|---|---|---|
| `alignment_status` | 统计资源日期对齐状态 | — | 按统计资源主导日期与目标/上一交易日的关系标记对齐状态。 |
| `auction_prev_volume_ratio` | 竞价成交量昨比 | 倍 | 314个非空样本重算314/314一致。 |
| `beta_60d` | 近60日 Beta | 无量纲 | 历史ZHB交叉核对280/280相符。 |
| `float_market_value` | 普通流通市值 | 元 | 320/320一致。 |
| `float_shares` | 普通流通股本 | 股 | 来自FinanceRecord.circulating_shares，按股计。 |
| `free_float_market_value` | 流通市值Z | 元 | 319个非空样本重算319/319一致。 |
| `free_float_shares` | 流通股本Z | 股 | 历史ZHB交叉核对279/280相符；2026-10-30代码688553为ELTDX 376,263,800股、同日ZHB归档377,665,400股。 |
| `ladder_level` | 当前连板高度 | 板 | 320/320按统计日期、当前封板状态及文件连板值重算一致。 |
| `limit_board_text` | 几天几板文本 | 文本 | 320/320按统计日期、当前封板状态及窗口字段重算一致。 |
| `limit_stat_days` | 涨停统计窗口天数 | 天 | 历史ZHB交叉核对280/280相符。 |
| `limit_status` | 当前涨停状态 | — | 当前涨停判别状态；ELTDX定义sealed、touched、none、unknown状态。 |
| `limit_up_count_in_stat_days` | 统计窗口内涨停次数 | 次 | 历史ZHB交叉核对280/280相符。 |
| `limit_up_streak_days` | 统计文件记录的连续涨停天数 | 天 | 历史ZHB交叉核对280/280相符。 |
| `open_change_pct` | 开盘涨幅 | % | 保留样本公式重算320/320一致。 |
| `open_prev_amount_ratio` | 开盘成交额昨比 | % | 319个非空样本重算319/319一致。 |
| `open_prev_seal_ratio` | 开盘昨封比 | % | 16个非空样本重算16/16一致。 |
| `open_turnover_z` | 自由流通口径开盘换手率 | % | 319个非空分子/分母样本重算319/319一致。 |
| `open_volume_hand` | 开盘成交量 | 手 | 320/320按开盘金额/(开盘价×100)重算一致。 |
| `open_volume_ratio` | 开盘量比 | 倍 | 上游公式已核；独立五根日K窗口不含完整的五个目标日前样本。 |
| `pe_ttm` | 滚动市盈率 | 倍 | 历史ZHB交叉核对279/280相符；2026-10-30代码920508为ELTDX 205.03、同日ZHB归档378.86。 |
| `prev2_seal_amount` | 前两实际交易日封单额 | 元 | 历史ZHB交叉核对280/280相符，最大差值约2.38e-7。 |
| `prev_amount` | 上一实际交易日成交额 | 元 | 历史ZHB交叉核对280/280相符。 |
| `prev_open_amount` | 上一实际交易日开盘竞价金额 | 元 | 历史ZHB交叉核对280/280相符，最大差值约2.98e-8。 |
| `prev_open_volume_hand` | 上一实际交易日开盘竞价成交量 | 手 | 历史ZHB交叉核对280/280相符。 |
| `prev_seal_amount` | 上一实际交易日涨停封单额 | 元 | 历史ZHB交叉核对280/280相符。 |
| `previous_trade_date` | 上一实际交易日日期 | 日期 | 来自上证指数实际日K，不按本机自然日倒推。 |
| `seal_prev_ratio` | 当前买一金额相对上一日封单额倍数 | 倍 | 16个非空样本重算16/16一致。 |
| `seal_to_amount_ratio` | 当前买一金额占当日成交额比 | 倍 | 319个非空样本重算319/319一致。 |
| `seal_to_float_ratio` | 当前买一金额占自由流通市值Z比 | % | 319个非空样本重算319/319一致。 |
| `stats_date` | 统计资源主导日期 | 日期 | tdxstat.cfg与tdxstat2.cfg共同使用的主导统计日期。 |
| `target_trade_date` | 目标交易日日期 | 日期 | 来自TDX握手，表示当前行情对应交易日。 |
| `year_limit_up_days` | 截至统计文件日期的年内涨停天数 | 天 | 历史ZHB交叉核对280/280相符。 |

## 注册表结果与剩余边界

本裁决将 32 个 ELTDX 来源字段从 `unverified` 更新为 `verified`，填写来源内含义和有明确依据的单位。`pe_ttm` 和 `free_float_shares` 的单日数值差异已保留；`open_volume_ratio` 的独立重算受日 K 窗口覆盖限制；没有新增映射、统一层字段或运行时改动。

决定文件：[`20261109_eltdx_shortline_fields.json`](20261109_eltdx_shortline_fields.json)。
