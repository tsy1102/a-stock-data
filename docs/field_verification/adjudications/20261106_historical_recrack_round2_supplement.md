# 2026-11-06 历史重破解补充定案

本补充承接 [历史重破解闭环](20261106_historical_recrack_closeout.md) 与 [源内语义定案补录](20261106_historical_recrack_semantic_adjudication.md)，记录按保留起点复核后的新增结论。没有重新运行行情采集。

## 结论

- 新增确认 `ZHB-tdxstat2::high_52w` 的源内语义为 **52 周最高价，单位元**；它是同一来源已验证路径 `ZHB-tdxstat2::stat2.high_52w` 在 `full_market_snapshot` 中的直接合并别名。
- 没有新增 ZHB 与 Eastmoney Push2 `f174` 或 Tencent `[67]` 的映射。两条精确映射候选仍为拒绝；高命中率只说明可继续作为线索，不能消除复权、精度和窗口口径差异。
- `东财-push2ex::zt_days` 与 `zt_continuous` 仍未定案。现有 `zt_continuous ↔ KPH limit_count` 日期对齐结果为 118/124 相等、6 个整数反例，不能登记映射；`zttj.days/ct` 的官方字段说明不足以单靠响应字段名确定完整语义。

## 历史窗口复跑

本轮本地复跑命令为 `collide.py --all --run-tag historical_recrack_followup_20261106`，没有发起行情采集请求。报告位于 [`historical_recrack_followup_20261106`](../20261106/historical_recrack_followup_20261106/20261106_collision_report.json)，SHA-256：`738d49c00d13df658754329c4868e9533e402e6bb7558751be1f589587ab670a`。报告状态为 `complete`，覆盖 20 个采集目录、16 个有效交易日、1,303 个字段及 1,026,686 个样本值；产生 2 个 actionable L1、59 个 L4、6,253 条方法候选、71 条近似线索，没有新首见候选或护栏拦截。

两个 actionable L1 都是 `ZHB full.high_52w` 的跨源关系，审阅状态为拒绝：

| 候选 ID | 字段对 | 样本 | 结论 |
|---|---|---:|---|
| `cc1_aa705e3e795e5f9347ddb3b7e09a8382020420c3a52b49fbd504cefe862fcaa2` | ZHB `full.high_52w` ↔ Push2 `f174` | 60 组 / 3 日 / 90% | 拒绝逐值映射 |
| `cc1_f4b80f5b49cd701dc4b1b07d450c23668325bee719aa15c7d9b77bf5563af777` | ZHB `full.high_52w` ↔ Tencent `[67]` | 180 组 / 9 日 / 95% | 拒绝逐值映射 |

完整方法候选仍有待审项；其内容主要是相关性、公式及低信息量配对，不等于可直接写入字典的字段定义。本补充只把来源内可独立证明的别名语义写入主字典。

## `high_52w` 源内证据

解析器将 `tdxstat2.cfg` 第 17 项解为 `high_52w`；`full_market_snapshot` 通过合并 `stat2` 保留同一数值，没有单位换算或舍入。已验证的 `stat2.high_52w` 定义为“52周最高价”、单位“元”。代码入口见 [`core/zhb_client.py`](../../../core/zhb_client.py) 的 `parse_tdxstat2_cfg`、`full_market_snapshot` 与 `get_high_52w`。

单独核对只读取来源数据日不早于保留起点 2026-10-15 的 ZHB 样本：13 个采集目录、10 个来源日期、260 组股票值，严格数值相等 260/260；不使用容差。每份原始文件的 SHA-256、数据日和逐目录计数见 [机器证据记录](20261106_zhb_high52_alias_evidence.json)。

保留起点边界也已核实：标准碰撞报告诊断明确记载 `20261015/zhb` 的来源数据日 `20261014` 不在报告窗口并已跳过。先前单独探针曾把该目录的 20 组值计入 280 组统计；该统计已撤销，不参与本定案。最终证据只采用上述 260 组起点内样本。

## 公开网页复核边界

只读访问了 [Eastmoney Push2 行情接口](https://push2.eastmoney.com/api/qt/stock/get?secid=1.600519&fields=f57%2Cf58%2Cf43%2Cf44%2Cf45%2Cf46%2Cf47%2Cf48%2Cf49%2Cf162%2Cf170%2Cf174%2Cf175%2Cf124&fltt=2&invt=2)：2026-11-06 23:19（Asia/Shanghai）贵州茅台返回 `f174=1539.98`、`f175=1151.01`。接口响应只给数字字段 ID，且是当前快照；它不证明与 ZHB 的历史值逐值同口径，本次不据此新建映射。

对 [Eastmoney Push2EX `getTopicZTPool`](https://push2ex.eastmoney.com/getTopicZTPool?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=100&sort=fbt%3Aasc&date=20261104) 的探索性查询中，请求参数为 2026-11-04，响应元数据显示 `qdate=20261106`。抽查五只股票的 `limit_count` 与价格和先前保存的 2026-11-04 日期证据一致，说明不能把 `qdate` 简单当作池数据日；但适配器只返回 `data.pool`，不保留响应外层日期元数据。此观察不用于推断 `zttj.days/ct` 定义。另一个 `getYesterdayZTPool` 端点对该请求返回空池，因它是不同接口且日期含义未厘清，没有用于定案。原始网页观察及响应摘录见 [公开网页记录](public_web/20261106_historical_round2_observations.json)。

## 注册表变更

`field_registry.json` 中只更新 `ZHB-tdxstat2::high_52w` 的状态和源内元数据，使用 `verified_by_empirical_addendum`；不写入 `mappings`。随即重生成 `field_dict.md`、`unknown_fields.md`、`source_repository_map.md` 与 `field_metadata_gaps.md`。时效策略将 `high_52w` 与 `stat2.high_52w` 一并标为 `daily_market`，碰撞仍须满足来源确认日条件。字段身份仍以完整 `(source, code path)` 为准。

本补充不改变采集路由、缓存键、限流、来源优先级或定案阈值。
