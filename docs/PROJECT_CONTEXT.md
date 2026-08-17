# 项目静态上下文(PROJECT_CONTEXT)

> **用途**: 长期不变的项目背景/架构/规范/约束——后续任务**按热/温/冷区分层按需读取**, 不整文档重读。
> **维护规则**: 仅当出现结构性变化(架构调整/新模块/版本发布)才更新; 字段级/字段字典类变化**不**更新本节(见文档体系)。
> **更新日期**: 2026-08-17(版本 V17.0.3)

## 0. 指引目录(每次任务先查此表, 按需读取)

| 任务类型 | 🔥热区(必读) | 🌤️温区(建议) | 🧊冷区(按需才读) |
|---|---|---|---|
| **字段破解/字典** | AGENTS.md(Shell 规则)+ §5 约束 | §6 文档体系 + CRACKING_METHODOLOGY.md | field_dict 相关节 + verify/ 存档 |
| **脚本修改/新功能** | AGENTS.md + §3 编码规范 | §2 架构 + script_data_dict(相关字段链) | field_dict 对应源/字段 |
| **测试/回归** | AGENTS.md §2.1 + §4 测试规则 | 改动的脚本/模块 | 测试文件本身 |
| **运行/报告核查** | AGENTS.md + §1 背景 | reports/ 最新报告 + session_notes 最新 | 历史报告对比 |
| **性能/限流** | §2 架构 + §5 限流 | sc_network 相关 | 历史性能记录(session_notes) |
| **git/发布** | §3 Git 规范 + §5 版本 | CHANGELOG.md + roadmap.md | 历史提交 |
| **数据采集/验证** | AGENTS.md + §1 | field_verification 当日 + capture_field_probe | 历史采集对比 |

**读取原则**: 热区=必须/每次(AGENTS + 本节); 温区=任务相关章节; 冷区=仅该任务需要时才读对应文件。
**不重复读取**: 完成一次读取后, 同会话内不再重读(除非文件被修改)。

## 1. 项目背景与目标(🌤️温区: 运行/采集任务)

- **A 股盘后分析报告系统**: 5 大脚本生成每日个股/全市场分析报告(markdown), 上传 Google Drive。
- 运行方式: `python main.py --sht 600519 --med 600519 --lng 600519 --val --mak`(批处理, 每批 1 并发, 三层防封: 线程锁+进程间文件协调+时间戳)。
- 数据: **ZHB 离线包优先**(T-1, 零网络)→ HTTP/TCP 多源兜底; 休市日=纯 ZHB 横截面(bypass 模式)。
- 输出: `reports/*.md`(V17.0.1 全量 md 化)+ `snapshots/*.json`; GD 上传。

## 2. 技术架构(🌤️温区: 脚本/性能/限流任务)

| 层 | 模块 | 说明 |
|---|---|---|
| 入口 | `main.py`(530 行) | 批处理调度, 输出活性检测(900s 无输出判卡死) |
| 报告脚本 | `get_sht_report.py`(1747)/`get_med_report.py`(1202)/`get_lng_report.py`(1117)/`get_val_report.py`(2286)/`get_mak_report.py`(1792) | sht=短线/med=中线/lng=长线/val=23 策略全市场/mak=市场全景 |
| 核心包 | `core/`(data_provider/tdx_client/zhb_client/zhb_sync/stock_cache) | 统一数据层+协议层+缓存 |
| 支撑 | `stock_common/`(sc_datasource/sc_network/sc_render/sc_schema/md_render 等) | 数据源/限流/渲染/合约 |
| 脚本工具 | `scripts/`(run_tests/run_with_system_python/capture_field_probe/sync_readme 等) | 测试/采集/文档同步 |
| 测试 | `tests/`(17 文件, **269 passed/45 deselected**) | pytest |

**数据源分层**(字典 §12.15 权威): L1 ZHB 静态 → L1.5 THS SDK → L2 TDX TCP → L3 腾讯 → L4 push2delay → L5 push2 → L6 datacenter。批量=push2delay ulist HTTP(secids 参数); 单股 canonical=prefetch→TDX→腾讯→push2delay→push2→ZHB。

## 3. 编码规范(🌤️温区: 脚本/git 任务), 详细见 AGENTS.md)

- Shell: **仅 Windows PowerShell 5.1**(原生, 不混 bash/cmd); 复杂/中文命令落盘 `.ps1`(UTF-8 with BOM 四行头); **禁止 python 输出接 PS 管道**(分块解码乱码); 外部程序全名+splatting+`$LASTEXITCODE`。
- Python: 类型注解(公开函数)/`_debug_log`(禁 print)/无裸 except/无可变默认参/`_safe_float` 等; 入口脚本顶部 `ensure_utf8_stdio`。
- Git: 凭据/密钥不入库(`credentials/*`/通用密钥模式); `cache/`/`reports/`/`raw_*.json`/`meta.json` 忽略。

## 4. 测试规则(🌤️温区: 测试任务)

- 统一入口: `scripts/run_tests.ps1`(禁止直接 `pytest`/`python -m pytest`)。
- Mode: all(默认)/module+Path/real(需 REAL_NETWORK=1)/skip_real/expression+ExtraArgs。
- 自定义 marker: `real_network`(需在 pyproject.toml 注册); conftest 自动跳过真网络。
- 回归基线: **269 passed / 45 deselected, 0 failed**。

## 5. 固定业务约束(🔥热区: 字段/版本相关任务)

- **字段破解纪律**: 每次破解必须遵循 `docs/field_verification/CRACKING_METHODOLOGY.md`(前置→七大思路→铁证分级 L1-L4→固化链条)。
- **固化链条**(改字段后强制): ①field_dict → ②矩阵(§12.15/§零·B+gen_field_matrix.py)→ ③5 脚本获取/fallback → ④script_data_dict → ⑤回归。
- **ZHB 解析缓存版本**: 字段结构变更必须升 `_ZHB_PARSE_SCHEMA`(当前=2), 否则旧 pickle 缺新键。
- **口径铁律**: 主力净额=f137+f140(特大+大单); ZHB main_net_buy_* 键=竞价额/量(非主力); 行业仅认 881 段(880=概念); 交易日口径涨幅; 单位: 万元/元 严格区分。
- **限流**: push2=0.4rps/push2delay=1.0/datacenter=1.0/腾讯=5.0; 熔断 3 连断→20h; 批量用 push2delay 镜像域。
- 版本: V17.0.1(CHANGELOG.md 权威); 报告输出 `.md`(md_render.py 渲染层转换)。

## 6. 文档体系(🧊冷区: 字段/文档任务)

| 文档 | 内容 |
|---|---|
| `docs/field_dict.md` | **主字段字典**(权威, 3600+ 行: 协议/字段表/矩阵/源优先级) |
| `docs/script_data_dict.md` | 脚本×源×字段链(双字典对照) |
| `docs/verify/` | 实证存档(939 指标/682 列 ID/1924 字段/470 X 码/对齐表) |
| `docs/field_verification/` | 方法论+每日采集产物(analysis 结论入库, raw_*.json/meta.json 忽略) |
| `docs/session_notes/` | 会话纪要(20260813/20260815/20260816——记忆锚点) |
| `docs/roadmap.md` | 决策记录(ADR, 破解收官/版本度量) |
| `docs/domain_glossary.md` | 术语口径 |

## 7. 动态信息(🧊冷区: 每次新读, 不静态化)

- 运行日志/报错/测试结果/报告内容(md 质量/数据核查)
- 采集数据(docs/field_verification/{YYYYMMDD}/)
- 会话进展(session_notes 每日追加)
- git 状态/提交历史
