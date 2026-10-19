# 历史字段定案复核（2026-10-19）

## 复核范围

正式碰撞报告的审阅版：[20260914_collision_report.md](20260914_collision_report.md)。完整结构化报告 `20260914_collision_report.json` 保留在本机供复核；仓库 `.gitignore` 按既定规则排除该类原始碰撞 JSON，因此不纳入提交。该报告模式为 `verified_anchor_only`，探索配对数为 0。
有效窗口为 2026-09-04 至 2026-09-14 的连续 7 个项目交易日。原始目录只在仓库 .tmp/ 隔离副本上运行碰撞；报告已归档到本目录。

## 提交预览的决定

| 数量 | 目标 | 动作 | 证据摘要 |
|---:|---|---|---|
| 1 | TDX(双命名源)::lirun_zonghe | verify | 7 日，140 对，命中 100%，比例 0.1 |
| 1 | TDX(双命名源)::yingye_lirun | verify | 7 日，140 对，命中 100%，比例 0.1 |
| 1 | TDX(双命名源)::weifen_lirun | verify | 7 日，140 对，命中 100%，比例 0.1 |
| 1 | TDX(双命名源)::zong_zichan | verify | 7 日，140 对，命中 100%，比例 0.1 |
| 1 | TDX(双命名源)::liudong_zichan | verify | 7 日，133 对，命中 100%，比例 0.1 |
| 1 | TDX(双命名源)::guding_zichan | verify | 7 日，140 对，命中 100%，比例 0.1 |
| 1 | TDX(双命名源)::liudong_fuzhai | verify | 7 日，133 对，命中 100%，比例 0.1 |
| 1 | TDX(双命名源)::ziben_gongjijin | verify | 7 日，140 对，命中 100%，比例 0.1 |
| 1 | 东财-ulist239(np/get)::f109 | enrich_metadata | 5 日，100 对，命中 100% |
| 1 | 东财-ulist239(np/get)::f110 | enrich_metadata | 5 日，100 对，命中 100% |
| 1 | 东财-ulist239(np/get)::f160 | enrich_metadata | 5 日，100 对，命中 100% |

决策细节、previous 快照、完整字段身份与理由见 ../../../adjudications/20261019_historical_field_candidates.json。11 项决策的只读预览全部通过，并已于 2026-10-19 应用：8 个 TDX 路径升级为 verified，3 个 Ulist239 字段补齐元数据；注册表生成视图已重建。

## 暂不定案

- ulist239.f45 与 TDX jinglirun 在部分窗口表现为净利润候选，但历史扩展记录有 599/620 命中并存在早期口径差异；另有同数字段跨 push2 路径的来源身份冲突。需逐日复核错配样本、财报期与来源映射，当前不写回。
- push2_full 归档路由的 f84/f85/f105/f119/f120/f175 虽出现强候选，但该运行身份已停用且 source_lineage.json 标记为不可作锚；f105 还涉及归母净利润与净利润口径差异。本轮不把历史路由的结果混入活动字段定案。
- push2_full.f58/f60/f121/f130 等现存定义冲突属于纠错/证伪问题，不是新字段的 verify 或元数据补全；按完整来源路径另行处理，不能由本次 L1 候选覆盖。

## 应用与验证

- 注册表共 2,518 个逐源字段身份，应用前后数量不变；仅 11 个目标身份的状态/元数据发生变化，新增 11 条精确来源映射。
- 再次只读预览得到 already_applied=11、mappings_added=0，确认决策可幂等重放且没有重复映射。
- registry_parity 通过：当前 1,878 / 2,518 / 376 与基线及 E3 补录一致；field matrix 和聚合视图均通过。
- verify_sync_check 通过：HARD FAIL=0、WARN=0；生成的治理报告位于 ../../../sync_check_reports/20261019_154943_810048_verify_sync_report.md。
