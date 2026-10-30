# 2026-10-29 字段候选复核与数据回放

## 结论

- `tencent[10]` 的线性拟合候选**不成立为可推广关系**：复放 120 个现有样本后，仅 29/120（24.2%）在 1% 相对误差内，103/120（85.8%）在 5% 内；中位相对误差 2.00%，最大 38.60%。原候选的 18 条验证集 `R²=0.999956`、归一化 RMSE `0.036975`，不足以证明稳定关系。
- 同一 120 条中，`tencent[10]` 与 `TDX bid1_vol`、`ELTDX quote_snapshot.buy_levels[0].volume` 均为 120/120 精确相等。ELTDX 的公共字段说明将盘口 `QuoteLevel.volume` 定义为挂单量、单位“手”。因此 `[10]` **强烈指向买一挂单量（手）**，而不是上述拟合公式的结果；由于腾讯没有找到可核验的官方索引字段表，本结论先作为高置信经验解释，不写成腾讯注册表的正式契约定义。
- **四组 L1-C 的字段语义等价现已定案为“确认”**：公开契约、锁定版本的 AxData 实际取数路径与逐值回放互相吻合。证券标识、开盘价、前收盘价分别在正式候选样本中 99/99 精确相同；流通股本 99/99 满足现行碰撞容差，扩展回放最大相对差为 `7.56e-7`。这是字段身份/含义结论，**不等于来源独立性结论，也不等于主注册表映射已登记**。注册表仍不写映射：报告 `actionable_L1=0`，`AxData` 是 `framework_reference` 且没有逐源字段记录，FTShare REST 的底层上游未公开确认；当前工作流不允许 L1-C 进入普通 L1/L1-U 定案器。

## 样本与复现方式

- 仅读取本地已留存快照，日期为 `20261020, 20261021, 20261023, 20261026, 20261028, 20261029`，每个日期 20 只股票；不运行采集器，也未调用行情 API 获取新样本。
- CSV 逐行保存六个来源（AxData、FTShare REST、TDX、ELTDX、腾讯、新浪）的原始候选值、来源日期/时间、重算公式和误差，便于逐值复核。
- 原始碰撞报告为 schema 5、`verified_anchor_only`、完整状态 `complete`；官方报告中的 4 条 L1-C 均为 99 对、5 个报告交易日。下面的 120 行是六个来源在本地快照中可直接交叉读取的扩展回放，不替代碰撞器的样本资格规则。
- AxData `stats_date` 与采集日不同；FTShare 样本的 `as_of_date` 在 120 行中均为空，`timestamp_ms` 只表示响应时间，不能替代数据有效日。CSV 保留两列原始日期信息；开盘/前收盘按行情日对照，流通股本的精确有效日无法从 FTShare 样本确认，故不将股本微小差异解释为严格同一时点值。

## 数值结果

| 对照 | 结果 | 解释 |
|---|---:|---|
| AxData `instrument_id` = FTShare `symbol` | 99/99 精确 | 代码与交易所后缀均相同 |
| AxData `open_price` = FTShare `open` | 99/99 精确 | 正式 L1-C 样本 99/99 精确 |
| AxData `pre_close` = FTShare `prev_close` | 99/99 精确 | 正式 L1-C 样本 99/99 精确 |
| FTShare 开盘价与 TDX / ELTDX / 腾讯 / 新浪 | tdx_open 120/120, eltdx_open 120/120, tencent_open 120/120, sina_open 120/120 | 120 条均精确 |
| FTShare 前收盘价与 TDX / ELTDX / 腾讯 / 新浪 | tdx_prev_close 120/120, eltdx_prev_close 120/120, tencent_prev_close 120/120, sina_prev_close 120/120 | 120 条均精确 |
| AxData `float_shares` 与 FTShare `float_a_shares` | 99/99 在相对误差 ≤1e-6 内；最大绝对差 9,223 股；最大相对差 7.56e-07 | 支持相同股本口径，但存在 TDX 精度/财务快照日期差异 |
| FTShare `float_a_shares` 与腾讯数组位置 `[72]` / `[76]` | `[72]`: 114/120 精确、最大差 1 股；`[76]`: 114/120 精确、最大差 1 股 | 仅为数值指纹；不把这两个腾讯路径赋予含义，也不据此断言 FTShare 上游来源 |
| 腾讯 `[10]` 与 TDX / ELTDX 买一挂单量 | TDX 120/120；ELTDX 120/120 精确 | 目标值直接等于可解释的盘口挂单量 |
| 旧拟合公式 | `tencent[10] ≈ 0.0098217574 × (eltdx.shortline.seal_to_amount_ratio × sina[8]) + 0.4137512` | 29/120 ≤1%；中位误差 2.00%；最大误差 38.60% |

## 公开证据与限制

1. [FTShare A 股行情列表字段契约](https://market.ft.tech/gateway/doc/p/mdsj0xyo) 明确 `symbol`、`open`、`prev_close`、`float_a_shares` 的字段身份与定义；本地契约快照已登记这些字段为官方契约验证。
2. [FTShare-MCP 官方仓库说明](https://github.com/FTShare-Lab/FTShare-MCP/blob/main/README_EN.md) 说明仓库仅含接口文档/集成说明，不含 MCP 服务端代码。当前公开材料因此无法确认 REST 行情的底层上游提供方，不能推定 FTShare 与 TDX/腾讯彼此独立。
3. [AxData 0.1.4 PyPI 发布页](https://pypi.org/project/axdata/0.1.4/) 对应项目锁定版本；本机核验 wheel SHA-256 为 `eb4fba2ec53f8496d44d0b80e366c215816d290086bff9aad879924ecedd181c`。版本代码将项目实际调用的 `stock_shortline_indicators_tdx` 路由到 TDX 适配层；这可确认当前采集入口，不代表 AxData 的其他接口都来自 TDX。
4. [ELTDX 字段参考](https://github.com/electkismet/eltdx/blob/main/docs/FIELD_REFERENCE.md) 定义 `open_price`、`pre_close`、`float_shares`、买盘档位；[7709 快照字段文档](https://github.com/electkismet/eltdx/blob/main/docs/methods/7709-%E6%89%B9%E9%87%8F%E5%BF%AB%E7%85%A7.md) 将 `QuoteLevel.volume` 明确为挂单量、单位“手”。
5. [裁决工作流](ADJUDICATION_WORKFLOW.md) 规定 L1-C 不进入普通 L1/L1-U 裁决，也不因单源契约自动创建 `mappings`。当前 `AxData` 逐源字段记录数为 0；FTShare REST lineage 状态为 `unconfirmed`。按现有规则，不手工伪造映射。

## 本轮裁决

- 4 条 L1-C：研究结论为**语义等价确认**；机器审阅台账继续用 `needs_external_evidence` 表示“尚不具备正式注册表映射资格”，不是对字段含义存疑。唯一会改变这项映射资格判断的缺口，是 AxData 逐源登记/正式接入方式与 FTShare 上游谱系证据。
- 公式候选 `cc1_100c2e18527e7c42aceda98c01b1e2ddac9f35e44fad97640abee14c30153a75`：将人工审阅更新为 `rejected`，理由是扩展回放不满足 1% 稳定容差，且目标值与已定义的 TDX 买一挂单量直接相等。
- 本轮不改 `field_registry.json`、`source_lineage.json` 或采集代码。未将公开证据不足的来源独立性写成事实。

## 可追溯文件哈希

- 碰撞报告: `0e71f529f68b9fe99f93dcf1b043d93d785eb1082da655a3cfafa407ae8e29b6`
- 字段注册表: `3254b3d01218b552fb3d155682a9e4209cabb5e554aa32b07c422ae0d40b3114`
- 来源谱系: `fe4c778266604de73c79e169be707c1e065d7c7c27f22b776744e1460bf433bf`
- 当前碰撞工作流: `9316c75a7ffdc03dc8c0e1e118bd6f5dd6b3f86e80caf668b250525ca2675bca`
