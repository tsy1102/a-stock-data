# 公开网页核验记录（2026-11-23）

访问时间：2026-11-23 00:17:50 Asia/Shanghai。仅核验公开产品页面与公开的第三方协议资料；未登录、未访问账户信息、未调用采集接口。

## KPL 涨停明细 `raw_columns.col_02`

- 本轮没有新的碰撞报告或 candidate_id；线索来自留存原始行审计。`source_lineage.json` 将 `开盘啦(kpl_limit_up_detail)` 对应到开盘啦 KPL、运行别名 `kpl`。本地样本范围为 2026-10-15 至 2026-11-19，网页核验时未取得可与历史单股 raw 对齐的官方值。
- 本地线索：[`research/20261122_kpl_col02_col03_raw_audit.md`](../../research/20261122_kpl_col02_col03_raw_audit.md)，规范 LF SHA-256：`3ca7969e35459fe4a074fe75b165735bfa8f70f12400b42e0f94ecc6657b81b5`。保留期内 1,229 条非空原始观测为 0/1；同一证券跨日不变，但目前没有能唯一解释该标志的对照关系。
- 精确路径状态：KPL 原始归档中可见 `raw_columns.col_02`，但当前注册表没有 `开盘啦(kpl_limit_up_detail)::raw_columns.col_02`；现有 `市场源(market_sources)::col_02` 是聚合身份，不能直接代表 KPL 独立接口字段。
- [开盘啦官方涨停板复盘页](https://apppage.longhuvip.com/w26/community/plateReplay.html?type=2)提供日期选择，并标示个股/板块数据 15:05 更新、龙虎榜 17:00 更新。页面没有展示原始 API 字段路径、`col_02` 标签或单股对应值，因此只确认这是按日期浏览的产品页，不支持 `col_02` 的字段语义（`label_only`）。
- [开盘啦官网](https://www.kaipanla.com/omain/)将“涨停板复盘”列为产品功能；同样没有原始字段定义，不能单独作为接口契约。
- 第三方 [LowellLee/KPL 接口整理](https://github.com/LowellLee/kpl/blob/master/KPL%E6%8E%A5%E5%8F%A3.md)说明其内容来源于非官方私有 API 材料。历史 `DailyLimitPerformance` 示例将 `[4]` 标为“涨停时间”，但 `[2]` 仅展示示例值 `0`、`[3]` 展示空值，没有 `[2]` 的标签；另一个 `DailyLimitPerformance2` 示例的数组布局不同。该资料只能作为端点结构线索，不能据此定案 `[2]` 或跨接口类推。
- 待区分的假设至少包括“证券/板块分类标志”和“仅供客户端协议使用的状态位”；需要官方标签或同一精确接口中与带名分类字段逐行对照才能区分。官网页面未提供股票代码、字段名、值与有效日期的联合观测，结果不能升级为 `value_corroborated`。
- 结论：`col_02` 保持未知，公开核验状态 `inconclusive`。二值形态和跨日稳定性不足以确定业务含义；后续先补齐精确 KPL 字段身份，再以能区分替代解释的公开或接口级证据继续验证。当前不改主字典，不建跨来源映射。

## KPL `zt_time` 日期锚的网页边界

官方涨停板复盘页的日期选择和 15:05 更新提示与 KPL 的按交易日复盘场景相符，但网页不定义原始 `zt_time` 的字段契约，也不证明它是接口更新时间。`zt_time` 被用作 `record.event_date` 的依据来自项目已验证的 KPL 字段身份和本地逐行审计 [`research/20261123_kpl_row_timestamp_date_anchor_audit.md`](../../research/20261123_kpl_row_timestamp_date_anchor_audit.md)，不是来自该网页。结论仅限同一 KPL 记录行的事件日期；不得据网页内容将其扩展成来源全局刷新时间。
