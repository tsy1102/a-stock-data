# 自动化修复流水线设计（Auto-Fix Pipeline v1.0）

> 目标：将"分析 v9.6 → 对比 v15 → 修改 → 测试 → 验证"的人工迭代过程自动化，
> 由 Agent（Reasonix）通过 CLI 驱动，每个修复**原子化、可回滚、可恢复**，
> 解决"每次修改都要单独对话、批准后才改"的低效问题。

---

## 一、为什么需要这套流水线（环境验证结论）

| # | 验证事实 | 对设计的影响 |
|:---:|:---|:---|
| 1 | GitHub 远程 + 本地 git 历史**仅到 v9.8**（30 commits），v10→v15.4 全部是未提交工作区 | git-archaeology 无法用 commit 历史，只能靠 `a-stock-data-v9.6/` 静态参照 + CHANGELOG + roadmap |
| 2 | `a-stock-data-v9.6/` 是**完整独立副本**（VERSION=9.6，无 data_provider.py，有 `tdx_get_qfq` 等 v15 已删函数） | v9.6 可作为静态字段提取的权威参照 |
| 3 | 报告章节骨架 v15 **保持甚至增强**（med/lng 新增"舆情与互动"），差异集中在章节内**字段值**（概念板块 16→0、总市值 981.8→0.00、PB 1.61→0.00） | 基线对比聚焦**数据字段值**而非章节结构 |
| 4 | v9.6 依赖旧包（easy_tdx 等），与 v15 同环境运行困难 | 基线捕获采用**双轨**：v9.6 静态源码提取 + v15 实跑输出提取 |
| 5 | 报告运行耗时长、有卡死风险（V15.4.1 修复前 sht 4 指数 240s） | 基线捕获支持 `--stocks/--reports` 子集 + `--timeout` 超时保护 |

---

## 二、整体架构：五阶段闭环

```
Phase 0  init      git 快照（把当前未提交工作区固化为 tag）+ 目录/配置初始化
Phase 1  analyze   基线捕获（v9.6 static + v15 runtime）→ 差异对比 → diff_specs/
Phase 2  fix       逐 spec 原子化修复（Agent 改代码 → 单测 → verify）
Phase 3  verify    基线对比 + 单元测试 + 实跑回归（回归守护）
Phase 4  report    汇总 fix_report.md + CHANGELOG/版本号建议
```

每个 Phase 之间由 `pipeline_state.json` 衔接，**可中断、可恢复**。
Agent 每次只做一件事（一个 spec），做完标记状态，天然适合多轮对话驱动。

---

## 三、数据契约（三个文件类型）

### 3.1 `baselines/<version>_<mode>_<ts>.json` — 基线快照

```json
{
  "meta": {
    "version": "v9.6",
    "mode": "static",              // static=源码静态提取 | runtime=实跑输出提取
    "captured_at": "2026-08-01T14:00:00",
    "stocks": ["000100"]
  },
  "reports": {
    "sht": {
      "sections": {
        "【五、概念板块、热点归因与板块共振】": {
          "concept_blocks": {"present": true, "count": 16, "names": ["华为概念", "..."]}
        }
      },
      "fields": {
        "mcap_yi":    {"value": 981.8, "source": "q.get('mcap_yi')", "line": 244},
        "change_pct": {"value": 3.2,   "source": "q.get('change_pct')", "line": 120}
      }
    }
  }
}
```

**static 模式**：从源码正则提取 `L(...)` 输出行的字段格式 + 数据源函数调用（不运行代码）。
**runtime 模式**：实跑 `python main.py --<report> <code> --no-upload`，解析 `reports/` 输出 txt，按"字段名: 值"模式提取。

### 3.2 `diff_specs/<id>.yaml` — 单个差异修复规格

```yaml
id: sht.concept_blocks.count      # <report>.<field>.<dimension>
report: sht
field: concept_blocks
dimension: count
v9_expected: 16                   # 从 v9.6 基线读
v15_actual: 0                     # 从 v15 基线读
status: pending                   # pending → analyzing → fixing → verifying → resolved | blocked
priority: P0                      # P0 数据归零 > P1 字段缺失 > P2 精度下降 > P3 格式
root_cause: |
  v9.6: get_concept_blocks(code) HTTP 直取 → blocks['concept'] 16 个
  v15 : get_concept_blocks + ZHB fallback，TDX concept 常空 → 0 个
fix_target: stock_common/sc_datasource.py::get_concept_blocks
related_files: [stock_common/sc_datasource.py, get_sht_report.py]
verified_by:                      # verify 时回填
  test: ""
  baseline_diff: ""
```

### 3.3 `pipeline_state.json` — 流水线状态（单一事实源）

```json
{
  "phase": "analyze",             // init → analyze → fix → verify → report
  "specs_total": 5,
  "specs_resolved": 0,
  "specs_blocked": 0,
  "current_spec": null,
  "last_run": "2026-08-01T14:00:00",
  "history": [
    {"ts": "2026-08-01T14:00:00", "action": "init",   "detail": "git tag v15-snapshot-... created"},
    {"ts": "2026-08-01T14:05:00", "action": "analyze","detail": "5 diff_specs generated"}
  ]
}
```

---

## 四、CLI 设计

### 4.1 `scripts/auto_fix_pipeline.py` — 总入口

```text
usage: auto_fix_pipeline.py <command> [options]

commands:
  init            初始化：git 快照当前工作区 + 创建 baselines/ diff_specs/ 目录
  analyze         基线捕获 + 对比 → 生成 diff_specs/*.yaml
                  --stocks 000100,600519  默认 000100
                  --reports sht,med,lng,ful
  fix             --spec <id>   标记 spec 进入 fixing 状态（Agent 开始改代码）
                  --result ok|fail --note "..."   标记修复结果
  verify          --spec <id>   运行验证：单测 + 基线对比 → resolved/blocked
  status          查看 pipeline_state.json 摘要
  report          生成 docs/fix_report.md（含 CHANGELOG 建议）
```

### 4.2 `scripts/capture_baseline.py` — 基线捕获

```text
usage: capture_baseline.py --mode static|runtime --version <v>
       [--stocks 000100] [--reports sht,med,lng,ful] [--out baselines/]
       [--no-upload] [--timeout 900]
```

- static 模式：读取 `a-stock-data-v9.6/` 或当前工作区源码 → 提取字段契约（**不运行**）
- runtime 模式：实跑当前工作区报告脚本 → 提取字段实际值（**验证数据精度**）

### 4.3 `scripts/compare_baseline.py` — 差异分析

```text
usage: compare_baseline.py --v9 <v9.6_baseline.json> --v15 <v15_baseline.json>
       [--out diff_specs/] [--min-priority P0]
```

对比规则（按优先级）：
1. **present 翻转**：v9.6 有字段 / v15 无 → P0
2. **值归零**：v9.6 非零 / v15 为 0 或空 → P0
3. **精度下降**：v9.6 值 > v15 值（如 16 vs 3）→ P1
4. **格式差异**：语义等价但格式不同 → P3

---

## 五、Agent 协作协议（核心：去掉逐项人工审批）

```
循环（对每个 diff_spec，按 priority 排序）：
  1. Agent 运行:  python scripts/auto_fix_pipeline.py fix --spec <id>
     → spec 状态 pending → fixing，current_spec 锁定
  2. Agent 读取 diff_specs/<id>.yaml 的 root_cause 和 v9.6 参照代码
  3. Agent 修改 v15 代码（一次只改这一个 spec 涉及的文件）
  4. Agent 运行单元测试:  pytest tests/ -k <相关>
  5. Agent 运行:  python scripts/auto_fix_pipeline.py verify --spec <id>
     → 自动重跑基线对比 + 单测 → 通过则 resolved / 失败则 blocked
  6. blocked 时:  Agent 回滚本次改动（git checkout -- <files>），记录失败原因
  7. 全部 resolved → 运行 report → 生成 fix_report.md + CHANGELOG 建议
```

**人工介入点**（保留但不阻塞）：
- `status` 随时可看进度
- `fix --result blocked --note "需要人工决策"` 可把疑难 spec 挂起给人类
- 每个 fix 独立 commit（`--no-commit` 可关闭），可单独 revert

---

## 六、子项目拆分（对应用户 5 个子项目需求）

| 子项目 | 对应脚本 | 说明 |
|:---|:---|:---|
| baseline-capture | `capture_baseline.py` | 双轨基线快照（static 源码 / runtime 实跑） |
| diff-engine | `compare_baseline.py` | 差异分析 → diff_specs（4 级优先级） |
| git-archaeology | 降级为 `docs/` 手工梳理 | git 历史仅到 v9.8，无法考古 v10-v15；改为读取 CHANGELOG + roadmap 版本意图 |
| fix-pipeline | `auto_fix_pipeline.py fix/verify` | 原子化修复 + 状态机 |
| regression-guard | `auto_fix_pipeline.py verify` + 单测 | 每次修复后自动回归基线对比 |

> ⚠️ **git-archaeology 的降级说明**（重要）：
> 验证发现远程 + 本地 git 历史均止于 v9.8，v10→v15.4 无任何 commit。
> 因此"在最新 GitHub 仓库寻找升级线索"只能获取到 v9.8 为止的代码；
> v9→v15 的版本意图线索以 **CHANGELOG.md + docs/roadmap.md** 为唯一可靠来源。
> 建议用户在合适时机把当前工作区提交为一个新 tag（`init` 命令会自动做 git 快照），
> 让后续版本拥有可回溯历史。

---

## 七、验收标准

- [ ] `python scripts/auto_fix_pipeline.py init` 生成 git 快照 tag + 目录结构
- [ ] `python scripts/auto_fix_pipeline.py analyze --stocks 000100` 生成 ≥1 个 diff_spec
- [ ] 每个 diff_spec 的 v9_expected / v15_actual 与 roadmap 实测记录一致
- [ ] `fix → verify` 状态机流转正确（pending→fixing→resolved/blocked）
- [ ] blocked 后可回滚且 pipeline_state 不损坏
- [ ] `report` 生成可读的 fix_report.md

---

## 八、快速开始（Quick Start）

```bash
# 1. 初始化（可选 --snapshot 把当前未提交工作区固化为 git tag）
python scripts/auto_fix_pipeline.py init

# 2. 一键分析：采集 v9.6 + v15 基线 → 生成 diff_specs/
python scripts/auto_fix_pipeline.py analyze --reports sht,med,lng,ful

# 3. 查看差异清单
python scripts/auto_fix_pipeline.py status

# 4. 修复循环（Agent 执行）：
python scripts/auto_fix_pipeline.py fix --spec <id>          # 锁定开始修复
#   ...Agent 修改代码、跑单元测试...
python scripts/auto_fix_pipeline.py fix --spec <id> --result ok   # 标记修复完成
python scripts/auto_fix_pipeline.py verify --spec <id>            # 自动验证 → resolved/blocked

# 5. 全部完成后生成报告
python scripts/auto_fix_pipeline.py report
```

---

## 九、Agent 协作手册（Reasonix 会话模板）

> 用户启动新会话时，把下面这段发给 Agent，即可进入流水线驱动模式。

```text
你是本项目的修复 Agent。项目已配置 Auto-Fix Pipeline（docs/auto-fix-pipeline.md）。

工作方式（无需每步人工审批，按流水线推进）：
1. 先运行 python scripts/auto_fix_pipeline.py status 查看待修复 diff_specs
2. 对每个 pending 的 spec（按优先级 P0→P1→P2）：
   a. python scripts/auto_fix_pipeline.py fix --spec <id>
   b. 读取 diff_specs/<id>.yaml 的 detail 与 v9.6 参照代码
      （a-stock-data-v9.6/ 目录，同文件同名函数）
   c. 修改 v15 代码，只改该 spec 涉及的文件
   d. 运行相关单元测试（pytest tests/）
   e. python scripts/auto_fix_pipeline.py fix --spec <id> --result ok
   f. python scripts/auto_fix_pipeline.py verify --spec <id>
      → resolved: 继续下一个；blocked: 回滚改动并记录原因
3. 疑难问题（需要用户决策的）：
   python scripts/auto_fix_pipeline.py fix --spec <id> --result blocked --note "原因"
   然后向用户汇报，用户决策后继续
4. 全部 P0/P1 resolved 后运行 report，按建议更新 CHANGELOG + VERSION

铁律：
- 一次只修一个 spec（原子化，可回滚）
- 修改前先 git status 确认工作区干净（或用 init --snapshot 固化基线）
- 修改后必须跑测试 + verify，不允许"改了就算完"
- v9.6 代码是参照不是目标：架构演进（dict→cdata、HTTP→ZHB）是既定方向，
  目标是恢复**数据精度与丰富度**，不是回退架构
```

---

## 十、已知限制与后续演进

| 限制 | 说明 | 后续方向 |
|:---|:---|:---|
| static 提取无法验证数据精度 | static 基线只证明"字段存在"，值是否正确需 runtime 实跑 | 定期跑 `capture_baseline.py --mode runtime` 做值级对比 |
| git 历史止于 v9.8 | v10-v15 无 commit，无法考古版本意图 | `init --snapshot` 固化当前态，此后每轮修复独立 commit |
| 标签名可能含 emoji/截断 | 如 `⚠️ 盘前模式（9`（遇到 `:` 截断） | 提取逻辑可放宽标签长度上限 |
| 部分"数据源调用差异"是调用位置移动 | 如 tdx_get_quote_full 移入 data_provider 内部 | diff_spec detail 会引导 Agent 验证 fallback 链是否真生效 |
| diff_spec 只有存在性 | 需要人工/Agent 判断是否真实缺陷 | 结合 roadmap 实测记录（v9.6 vs v15 值对比）辅助判断 |

---

## 十一、V16 五维加固记录（2026-08-01 用户补充需求）

> 用户补充："防止限流（参考 simonlin1212/a-stock-data）、缓存污染/TTL 缺陷、
> 端口优先级 ZHB 优先 push2 减少、连续 ZHB 补字段、授权联网测试"

### 11.1 限流增强（sc_network.py）

| 改动 | 说明 |
|:---|:---|
| push2 专属更严限流 | `_DOMAIN_LIMITS` push2: sleep_ms 1000→**1500ms**, rps 1.0→**0.6**（风控最严）|
| 403 风控检测 | `_do_request` 新增 403 分支：`em_403_count` 统计 + 指数退避（base=2.0, max 60s）+ 熔断器 Open + `_biz_logger.warning` |
| HTTP 000 退避 | 连接异常分支 `exponential_backoff` max_wait 32→**60s** |
| `RateLimitBlockedError` | 连续 3 次 403 抛异常（提示停止 30-60min/换网络/调大 EM_MIN_INTERVAL/切换备胎源），成功响应重置计数 |
| Session 复用 | 新增 `_HTTP_SESSION`，`_do_request` 全路径 keep-alive（em_get 原用 EM_SESSION）|
| push2 审计 | `requires_push2` 装饰器（WARNING 日志 + `push2_call_count`），已装饰 11 个 push2 函数 |
| 域名全覆盖 | np-weblist 补入 `_DOMAIN_LIMITS`；全局扫描确认东财系直连 requests **0 处** |

### 11.2 缓存 TTL 修复（stock_cache.py）

| 改动 | 说明 |
|:---|:---|
| **软过期窗口** | `_SOFT_EXPIRY_WINDOW`（15 分类）：硬过期后窗口内返回旧值（stale-while-revalidate），防"集体过期→并发重拉→限流"；`_SOFT_STATS` 统计 |
| 研报 TTL 校准 | reports/industry_reports 3 天/1 天 → **3600s**（避免新研报滞后）|
| 实时行情确认 | get_stock_price TTL **15s**（ZHB→TDX→腾讯，优于建议 30s）|
| 估值确认 | pe_ttm/pb ZHB-only（V12.6 决策，无 HTTP fallback）|

### 11.3 端口优先级（data_provider.py）

- `get_canonical_stock_data` 行情 fallback 链：~~TDX→push2→腾讯~~ → **TDX→腾讯→push2→calculated**（push2 降为最后手段）
- 原则落实：ZHB 优先（盘前 100% ZHB）> mootdx TCP > 腾讯 HTTP > push2（风控最严）

### 11.4 连续 ZHB 回溯（stock_common/sc_zhb.py 新建）

| 函数 | 说明 |
|:---|:---|
| `backtrack_field(code, field)` | 单字段回溯：先当前包，缺失回溯更早 zip（默认 5 个）|
| `backtrack_stats(code)` | 整只股票合并：缺失字段从旧包补齐（实测 000100 合并 31 字段，缺字段从 3 包前补齐）|
| `backtrack_with_extractor` | 通用自定义提取器版 |
| 实时字段黑名单 | price/change_pct/amount 等禁用回溯（旧值误导）|
| 来源标记 | `logs/fallback.log` 记录 `zhb backtrack: ... <- zhb_2026xxxx.zip (steps=N)` |

字段字典：`docs/zhb_field_dict.md`（可回溯字段表 + AI 核实记录：腾讯 43=振幅/46=PB、pe_ttm ZHB-only、industry push2 f128 更准、北交所老号段作废）

### 11.5 联网验证（scripts/verify_ports.py）

实测 600519（2026-08-01）：腾讯 ✅ / 新浪 ✅ / datacenter ✅；push2 ❌（RemoteDisconnected 连接级风控，验证降末位必要性）；mootdx ❌（TCP 探测失败，V15.5 换台计划必要性）。报告：`docs/port_verification.md`

### 11.6 回归

- `pytest tests/test_cache.py tests/test_field_routing.py tests/test_sc_schema.py tests/test_scoring.py` → **72 passed**
- 新增 `tests/test_sc_zhb_backtrack.py`（真实 zip 回溯验证）

---

## 十二、V15.5 easy_tdx 稳定性改造（2026-08-01）

> 用户反馈："全部更换为 mootdx 接口后数据获取并不稳定"。实证研究 + 落地改造。

### 12.1 研究结论（实证）

| 发现 | 证据 |
|:---|:---|
| mootdx 0.11.7 **停更**（2024-07），BESTIP bug 无修复 | pip show + 参考仓库 FAQ |
| easy_tdx 1.17.10（旧版）K 线**直接崩溃** | `TdxDecodeError: day datetime: 数据不足`（V15.4.3 已记录）|
| easy_tdx **1.20.4** K 线**优雅降级**（空数据换台机制真实生效）| 升级后实测打印换台日志、返回空不崩溃 |
| **"不稳定"根因 = 服务器选择**（TCP 通但数据返空的静默空表）| 180.153.18.170 显式指定后两库都取到真实 K 线（1350.6 与腾讯一致）|
| easy_tdx 1.20.4 内置：健康分引擎 + 空数据换台 + **52 候选服务器** + 前复权 + 34 指标 + 缠论 | CHANGELOG v1.20.4 + inspect |

### 12.2 落地改造（tdx_client.py）

| 改动 | 说明 |
|:---|:---|
| `easy-tdx` 升级 1.17.10 → **1.20.4** | pip 完成（requirements 已有 `easy-tdx>=1.0,<2.0`）|
| `_EasyTdxAdapter` 适配层 | 把 easy_tdx API 包装成 mootdx 兼容（bars/index_bars/quotes/finance/close），**下游零改动** |
| 字段对齐 | bars vol **股→手**（/100）、datetime 列（date+' 00:00'）；quotes pre_close→**last_close**；finance 列名**去下划线**（jing_lirun→jinglirun）|
| 服务器白名单 | `_EASY_TDX_PRIMARY_HOST=180.153.18.170`（实测可用）+ 3 台候选；首选主服务器失败 → `from_best_host(hosts=白名单)` 内置换台 |
| 双通道 | `_get_tdx_client`：**easy_tdx 首选**（内置 health+换台）+ **mootdx 备胎** |
| `_check_tdx` | easy_tdx 优先探测，失败回退 mootdx |

### 12.3 验证

- 实跑：bars 600519 vol=55127.52 手（5512752 股/100 ✅）、close=1350.6 与腾讯一致；quotes/finance(37列)/index_bars(上证 3832.26) 全通
- 单测：`tests/test_tdx_health.py` **21 passed**（映射/市场判断/字段对齐/空表降级/异常降级）
- 回归：cache/field_routing/sc_schema + tdx_health = **72 passed**

### 12.4 说明与后续

- **未做**：跨进程健康分共享（15.150，file_lock 持久化）——单进程报告场景收益有限，留给 V15.5.1
- **可选增强**：easy_tdx 前复权（`--adjust QFQ`）+ 34 技术指标 → ful 报告技术分析段（V15.7 计划）
- 白名单 IP 可能随网络环境失效——`verify_tdx_host.py` 可重测更新

---

## 十三、V15.5.x 数据精度回归修复（2026-08-01，对照 v9.6）

> 用户要求："按照流程，至少实现 v9 版本的功能数据精度，可联网测试、发现问题自行修改直至达标"
> 实测 000100 四报告 vs v9.6 预期，逐项修复：

### 13.1 实测差距（修复前）

| 报告 | v9.6 预期 | 修复前实测 |
|:---|:---|:---|
| sht 概念板块 | 16 个 | **0 个** |
| sht 同业对比 | 4 家 | **无法获取（板块空）** |
| med/lng 总市值 | 981.80 亿 | **0.00** |
| med/lng PB | 1.61 | **0.00** |
| ful 技术分析 | MA5/10/20/60 + MACD/RSI/BOLL | **全部缺失** |

### 13.2 根因与修复（4 个补丁）

| # | 根因 | 修复 | 文件 |
|:---|:---|:---|:---|
| V15.5.1 | V12.0 把 `tdx_get_belong_boards` 从 easy_tdx **MacClient（TCP）** 误改为 **push2 HTTP** → push2 连接级风控挂 → 概念/行业空 | 恢复 v9.6 MacClient 路径（`_get_mac_client` + type_map 补 board_type=2）| tdx_client.py |
| V15.5.2 | `get_board_members`/`get_board_by_name` 同样委托 push2 → 同业空 | 恢复 v9.6 MacClient 实现（+ push2 fallback）| tdx_client.py |
| V15.5.3 | 周六 `need_realtime_quote=False` + **ZHB tdxstat 无 price/股本/pb 字段** → med/lng 全 0 | `get_canonical_stock_data` 补 3 处兜底：price→`get_stock_price` 完整链、股本→`sc_capital_cache`、pb→TDX 每股净资产计算 | data_provider.py |
| V15.5.4/5 | `get_stock_info` 直接调 `client.get_finance_info`（easy_tdx 列名带下划线 `zong_guben`）取 `zongguben` 失败 + 旧缓存污染 | 改用适配器 `finance()`（列去下划线）+ `sc_capital_cache` 兜底 + ipo_date/ipodate 列名兼容 + 清 basic_info 缓存 | sc_datasource.py |

### 13.3 达标验证（修复后 000100 四报告）

| 字段 | v9.6 预期 | 实测 | 状态 |
|:---|:---|:---|:---:|
| sht 概念板块 | 16 个 | **16 个**（AI手机PC/光伏/折叠屏/...）| ✅ |
| sht 同业对比 | 4 家 | 3 家（立讯精密/生益科技/三环集团）+ 本股 | ✅ |
| med 总市值 | 981.80 亿 | **983.88 亿** | ✅ |
| med/lng PB | 1.61 | **1.57**（price/每股净资产计算）| ✅ |
| lng 总股本 | 有 | **208.01 亿股** | ✅ |
| ful MA5/10/20/60 | 有 | ¥4.88/5.01/5.05/4.85 | ✅ |
| ful MACD/RSI/BOLL/KDJ | 有 | DIF=-0.05 RSI14=42.5 BOLL中轨=5.05 | ✅ |
| ful 同行 | 6 家 | 8 只（国星光电/星光股份/...）| ✅ |
| 市值排名 | 有 | 14/312 | ✅ |

### 13.4 回归

- `pytest tests/test_cache.py tests/test_field_routing.py tests/test_sc_schema.py tests/test_tdx_health.py` → **72 passed**

---

## 十四、V15.5.x val/mak 性能与数据修复（2026-08-03）

> 用户："mak 和 val 两个大头问题没有按流程修改；先运行 v9/v15 对比差异再修改；
> 后台留驻迭代；测试策略时严格按阈值限流避免 IP 封禁"

### 14.1 实测差距（修复前）

| 报告 | 问题 |
|:---|:---|
| val（全市场选股）| **卡死数小时**：main.py 600s 超时强制 kill；数据加载对 7957 只逐股调 push2（`get_em_quote_full`）→ 连接级风控 + 1.5s 限流 |
| val 策略20【主力资金】| ZHB 判定 `max_delay_days=2`（延迟 3 天 → False）→ 1000 只逐股 `tdx_get_fund_flow` → 10+ 分钟 |
| mak A 段情绪看板 | **涨停0/跌停0**：ZHB T-1 change_pct 不反映今日盘中；name 解析失败（`get_stock_name_from_zhb` 返回 None）→ all_stocks 0 只 |

### 14.2 修复清单（V15.5.6 - V15.5.17）

| # | 改动 | 文件 |
|:---|:---|:---|
| 15.5.6 | main.py 子进程超时分级：val/mak 1800s（30 分钟），单股 600s | main.py |
| 15.5.7 | `tdx_get_finance_info` 加 @cached(financial, 24h)——val strategy_10 300 次逐股 TDX 去重 | tdx_client.py |
| 15.5.8 | `_fast_kline()`：TDX 优先（0.2s/只）+ 百度 fallback——val 5/6/12/15 策略 1300 只 K 线提速 4.5 倍 | get_val_report.py |
| 15.5.9 | val 数据加载 mcap 补全：逐股 push2 → **腾讯批量**（不封 IP，含 mcap_yi/pe/price） | get_val_report.py |
| 15.5.10 | `_tencent_batch_fallback` 分批（60 只/批，URL 长度限制）——7957 只拼单 URL 被拒 | tdx_client.py |
| 15.5.12 | val 盘中 `_price_map` 复用腾讯批量（原 push2 批量卡死） | get_val_report.py |
| 15.5.13 | 移除腾讯缺失时的逐股 push2 兜底（mcap=0 由策略过滤） | get_val_report.py |
| 15.5.14 | strategy_20：tdxstat2 全市场资金流 O(1) 读 + use_zhb 放宽 3 天（1000 只逐股 TDX → 0） | get_val_report.py |
| 15.5.15/16 | mak A 段实时化：腾讯批量覆盖 T-1 change_pct（统一覆盖两分支） | get_mak_report.py |
| 15.5.17 | `tdx_get_market_abnormal_data`：unified_name_map 优先 + name/price 缺失不跳过（7941 只恢复） | tdx_client.py |

### 14.3 达标验证

| 指标 | 修复前 | 修复后 |
|:---|:---|:---|
| val 总耗时 | 卡死数小时（push2 7957 次）| **4.5 分钟**（数据加载 2min + 扫描 77s）|
| val 策略20 | 10+ 分钟卡死 | **12s** |
| val 报告 | 无输出 | ✅ `get_val_report_*.txt`（20 策略 78 次选择）|
| mak A 段 | 涨停0/跌停0/广度0:0 | **涨停74/跌停10/异动13，广度 5287:2352 偏多** |
| mak all_stocks | 0 只 | **7941 只** |

### 14.4 限流合规（用户要求）

- 所有 push2 调用已从 val/mak 主路径移除（腾讯批量替代，不封 IP）
- TDX 请求保留 `_tdx_throttle`（TDX_MIN_INTERVAL）+ finance/K线 磁盘缓存（跨进程）
- 腾讯批量 60 只/批（URL 安全上限），全市场 ~133 批自然间隔
- 逐策略计时改为**运行时 profiling**（策略完成即打印耗时，零额外请求）
