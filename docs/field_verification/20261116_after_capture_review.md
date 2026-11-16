# 2026-11-16 采集后破解复核

本记录补充 [`20261116_cracking_closeout.md`](20261116_cracking_closeout.md) 中当时“未运行采集”的历史状态；该文件描述的是本次新采集之前的工作，不作回写。

## 采集结果

- 按 [`DAILY_RUNBOOK.md`](DAILY_RUNBOOK.md) 执行 `scripts/capture_field_probe.py`，运行时间 2026-11-16 21:24:50 至 21:33:33；目标数据日和运行自然日均为 2026-11-16，默认股票池 20 只。原始采集 raw 与 `meta.json` 保存在本机 `docs/field_verification/20261116/`，按 [`../.gitignore`](../../.gitignore) 的可重采产物规则不纳入版本控制；AxData 与 Levistock 的验证摘要单独提交。
- 采集进程退出码为 0，总耗时 522.9 秒；报告异常源 9/36。ZHB 有 20/20 条，但包文件/解析日期为 `20261113`，落后目标交易日 2026-11-16；保留为旧来源日，不补采也不用于 11 月 16 日新样本。
- Eastmoney Push2 首批请求遇到 `RemoteDisconnected`。元数据记录 3 次实际尝试、4 次熔断前未发出请求；本地限流器随后将相关 Push2 域标记为 `ip_banned` 并抑制后续请求。该标签是本地熔断状态，不能据此断言远端已封禁。本轮没有重试；`em_kline_f61`、`em_fund_flow`、`ulist239`、`clist`、`slist` 相关结果均按各自失败/部分快照状态处理。ST 主源与 baostock 兜底均不可用。百度源按 `pending_validation` 策略跳过。
- `tdx`、`eltdx`、`tencent`、`sina`、`sina_extended`、`axdata`、`market_sources`、`kpl`、`push2ex`、`cls`、`datacenter`、`tdx_f10_more`、`fuyao`、`cninfo`、`reports`、`ftshare_rest`、`event_dc`、`macro_dc`、`research_sina`、`etf`、`news_wscn_cctv`、`sse_e_interaction` 等来源完成采集。AxData 对腾讯快照的单样本核验为 16/19 字段相等、来源身份仍为 observing；Levistock 为 observed，不能当作来源契约定案。
- `audit_source_date_mapping.py` 复核 129 条有效日期观察。11 月 16 日可明确确认的来源日期包括 Fuyao、KPL、新浪、腾讯及 FTShare REST；KPH 与 ZHB 实际来源日为 11 月 13 日。ELTDX 没有来源级 `as_of_date`；不得把目录日替代为 ELTDX 实际来源日。
- 当日采集证据覆盖审计：目标 1,548 个身份中 464 个有样本，只有 53 个身份覆盖至少 3 个精确来源日期；此覆盖不能支持大多数未知字段进入定案。

## 新样本碰撞

运行全保留期探索碰撞：

```powershell
.\scripts\run_with_system_python.ps1 scripts\collide.py --all --exploratory --run-tag after_capture_20261116
```

碰撞使用 21 个采集目录、21 个有效交易日、1,309 个字段和 1,419,007 条样本值；主攻目标 157 个、探索字段 881 个。新报告机器完整性为 `complete`，共有 L1=0、L1-C=0、L4=37、首次发现候选对=0。方法层候选 1,418 条仍是待复核线索，不是字典定案；报告保留在 [`collision_research_20261116/exploratory/20261116/after_capture_20261116/`](collision_research_20261116/exploratory/20261116/after_capture_20261116/)。

本轮没有新增可写入主字典的语义定案。尤其 L4 中 `sina[32]` 与多个财务/行情数字重叠不能当作同义证据：保留期内 380 条日期合格新浪样本中，379 条值为字符串 `00`，仅 2026-10-15 的 600825“新华传媒”为 `03`；注册表当前将该字段标注为未验证的“状态码”。它是低变化离散值，与多数为零的数值字段重叠属于弱证据，不能据此建立映射。逐条样本和文件摘要见 [`research/20261116_sina_field32_value_audit.csv`](research/20261116_sina_field32_value_audit.csv)。

## ELTDX 路径结果

本轮核查了未限定身份 `TDX-eltdx(适配层)::rank`。保留期 ELTDX raw 中实际出现的是 `global_helpers.realtime_rank.rows[].rank`、`global_helpers.theme_strength_rank.rows[].rank` 和 `global_helpers.stock_theme_strength_rank.rows[].rank` 三种完整路径。前者是实时排序列表序号；后两者来自同一题材强度模型，历史输出完全重复。2026-11-16 题材行为空，实时榜为 80 行、序号 1 至 80；ELTDX 来源日期缺失，因此只把实时榜结果视为结构/路径证据，不计作来源日期合格的跨源数值样本。

依据上述契约与历史 raw 重复性，采集器已停止重复调用 `stock_theme_strength_rank`，保留 `theme_strength_rank`，不删除历史文件。调整及证据见 [`ELTDX 题材强度 Helper 审查`](adjudications/20261116_eltdx_theme_strength_alias.md)。未将一个裸 `rank` 语义转移到其他完整路径；注册表不会因本次采集变更而把其他 rank 路径标为已验证。

## Registry parity 缺口

完整离线验收发现只读基线中有一条尚未进入 `source_fields` 的身份：`东财-push2ex::yesterday_limit_pool`。追查确认它与前三个 Push2EX 池根路径相同，是采集器 `output_paths` 中的数组容器，而非列表项字段。已按 [`昨日涨停池容器裁决`](adjudications/20261116_push2ex_yesterday_pool_container.md) 登记为 `disproved` / `collector_output_container`，保留原生 parity 身份并从未知字段队列移出；池内字段的日期和语义仍待核验。
