# 字段字典运营闭环记录（2026-10-06）

本文件补充 `FIELD_DICTIONARY_RESTRUCTURE_PLAN_20261005.md` 的交付后流程。原计划完成了主字典重整、逐源状态和来源谱系；本闭环补上“碰撞候选经人工复核后同步注册表”以及“GitHub 对应关系的对话确认状态”。

## 本轮完成

- 主字典入口直接链接碰撞规则、破解方法论、状态队列、矩阵、来源映射和人工定案流程；历史原文继续作为只读证据，不覆盖当前状态。
- 新增 `scripts/apply_collision_adjudications.py`。它默认只预览，验证报告模式、L1/L1-U 级别、完整运行时字段身份、注册表来源和独立锚；只有显式 `--apply` 才写入。
- 人工 `verify` 决定同步更新 `source_fields`、`fields` 兼容聚合视图、`mappings`、字段证据和派生字典/队列/来源映射。无法确认的单个候选不写回，字段保留原状态；冲突字段不会被碰撞结果覆盖。
- 将来源仓库的“项目证据状态”与“用户对话确认状态”分开。用户于 2026-10-06 确认下列 7 个来源关系；确认范围不扩展成底层数据所有权或独立来源结论：

  | 来源 | 对应仓库 | 已确认关系范围 |
  |---|---|---|
  | 同花顺-fuyao | `HiThink-Tech/Financial-API` | 官方 API 合约/客户端 |
  | TDX(双命名源) | `yanwei99521/easy-tdx` | 本项目使用的运行时客户端 fork |
  | ZHB-tdxstat / ZHB-tdxstat2 / ZHB-tipinfo | `yanwei99521/easy-tdx` | 仅下载/读取缓存的传输客户端，不是 ZHB 数据本体仓库 |
  | TDX-eltdx(适配层) | `electkismet/eltdx` | 通达信协议客户端适配层 |
  | levistock(ftshare) | `fleetinglife/levistock` | 多源包装库，不作为独立数据提供方 |

- 其余 21 个来源的对话确认状态保持 `pending`。有项目证据的仓库关系仍可显示 `repository_mapping_status=confirmed`；这不等于用户已确认。需要先取得仓库候选证据，再逐项通过对话确认。
- 新增生成式 `field_metadata_gaps.md`：当前可见 239 条 verified 记录缺少规范名或含义（207 缺含义、47 缺规范名、15 两者皆缺）。此报告只暴露展示元数据缺口，不自动降级状态或更改锚点资格。

## 持续操作顺序

1. 运行 `collide.py` 产生只读候选报告。
2. 依据 `field_verification/CRACKING_METHODOLOGY.md` 和 `field_verification/COLLISION_RULES.md` 检查来源、完整路径、样本日期、语义及原始证据。
3. 将明确决定写入 `field_verification/adjudications/`，并先运行定案工具预览。
4. 审阅后使用 `--apply`；随后运行定向测试、`gen_field_dict.py --check`、`gen_field_matrix.py --check`、`registry_parity.py`、`verify_sync_check.py`。
5. 来源仓库确认只更新 `source_lineage.json` 的 `dialog_confirmation`；重新生成 `source_repository_map.md`。不因确认客户端仓库而改变独立来源族。

## 未关闭项

- 21 个来源映射仍需后续证据和用户对话确认；本轮没有猜测仓库。
- 定案工具不自动解释字段语义，也不自动把碰撞候选晋级。每次结论仍由复核人提供明确语义、规范名、单位（如适用）和理由。
- 本轮不修改采集器、缓存键、交易日判断或碰撞发现算法。

## 2026-10-08 追加：来源仓库对话确认

用户确认此前列出的第 1–5 组候选仓库关系。本次在 `source_lineage.json` 中新增确认 16 个来源行，并重生成 `source_repository_map.md`：

- Eastmoney 的 10 个接口来源行（`push2(stock/get)`、`em_fund_flow`、`ulist239(np/get)`、`push2ex`、`datacenter`、`slist`、`clist`、`push2_full`、`em_kline_f61`、`em_hot`）登记为 [`fleetinglife/levistock`](https://github.com/fleetinglife/levistock) 的来源族/客户端参考。此映射不表示 levistock 是底层数据提供方，也不表示本项目每个端点或字段都来自该仓库。
- 腾讯实时行情和新浪 `hq.sinajs` 登记为 [`shidenggui/easyquotation`](https://github.com/shidenggui/easyquotation) 的客户端参考；新浪扩展 API 登记为 [`mpquant/Ashare`](https://github.com/mpquant/Ashare) 的历史 K 线参考，范围不扩展到该来源记录中的其他 API。
- AxData 登记为 [`electkismet/AxData`](https://github.com/electkismet/AxData) 包仓库；这不确认其底层数据来源或独立性。财联社接口登记为 levistock 的实现参考。
- 开盘啦/KPL 同时登记 [`LowellLee/kpl`](https://github.com/LowellLee/kpl) 与 [`Rainynitesky/kaipanla-data-parser`](https://github.com/Rainynitesky/kaipanla-data-parser) 两个并列参考；现有信息不能确定本项目代码的唯一来源。
- [`simonlin1212/a-stock-data`](https://github.com/simonlin1212/a-stock-data) 登记为项目级最早历史参考基线，不分配给任何具体采集源作为上游。

尚未确认具体仓库的 5 个来源仍保持 `unconfirmed` / `pending`：百度、沪深交易所、巨潮、`reports`、`market_sources`。用户表示其他仓库对应关系不清楚，因此未把项目级参考基线扩展成这些来源的映射。此次不改变来源族、独立性状态或锚点资格。
