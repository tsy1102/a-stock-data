# 依赖适配兼容性整改计划（2026-10-08）

## 状态

**已完成。** 本计划聚焦核验 `levistock` 适配器的实际调用契约，以及 `axdata_core` 经 `axdata` 包读取项目本地 ZHB ZIP 的路径；确认兼容后固定经回归验证的依赖版本。

## 目标

1. 明确项目实际调用的 `levistock` 方法、参数和返回结构，确认候选新版本兼容。
2. 验证 `get_shortline_indicators()` 将项目本地 ZHB ZIP 传给 AxData，并由新版 AxData 从该 ZIP 加载统计资源。
3. 不触发真实行情请求、不提高请求量或并发、不更改交易与报告逻辑。
4. 将已验证版本写入运行时依赖约束；由于 `requirements-dev.txt` 使用 `-r requirements.txt`，开发安装自动继承同一约束。
5. 为实际适配调用与本地 ZIP 读取补充离线回归，并同步维护计划、兼容记录、README、CHANGELOG 和版本号。

## 基线与影响面

### 当前调用点和返回契约

| 项目适配器 | 实际依赖调用 | 消费契约 | 项目缓存/调用方 |
|---|---|---|---|
| `get_cls_market_emotion()` | `levistock.market_emotion_cls()` | 非空字典；失败或空响应回 `{}` | `market_emotion` TTL；被涨停数量多源交叉核验调用 |
| `get_kph_limit_ladder(date)` | `levistock.get_zttt(date=date_str)` | `{ "StockList": [...] }`；11 列序列行转换为规范键，兼容字典行；返回字典列表 | `limit_pool` TTL；`get_mak_report.py` 调用 |
| `get_fupan_zttt()` | `levistock.stock.stock_fupanla_kph.get_zttt()` | 原样返回复盘字典，异常回 `{}` | `fupan_review` TTL；当前未发现生产调用点 |
| `get_fupan_pmsl()` | `levistock.stock.stock_fupanla_kph.get_pmsl()` | 原样返回含 `List` 的事件字典，异常回 `{}` | `fupan_review` TTL；当前未发现生产调用点 |
| `get_shortline_indicators(code)` | `axdata_core.request_interface("stock_shortline_indicators_tdx", ...)` | 读取 `result.records[0]` 字典；空值或异常回 `{}` | `basic_info` TTL；采集脚本 `scripts/capture_field_probe.py` 调用 |

`get_cls_market_emotion()`、`get_kph_limit_ladder()`、两个复盘适配器均有项目缓存装饰器；`get_shortline_indicators()` 的缓存分类为 `basic_info`，按交易日控制。更新所审查依赖没有改变这些缓存键或项目返回结构的依据。

### 本地 ZHB 路径

`stock_common/sc_datasource/_quotes.py` 由自身文件位置计算 `<项目根>/stock_common/cache/zhb`，匹配 `zhb_*.zip` 并按名称排序取最后一个；将完整 ZIP 文件路径作为 `stats_root` 传入接口。AxData `ensure_tdx_stats_resource_for_params()` 读取 `params["stats_root"]`，显式路径进入 `ensure_tdx_stats_resource(root=...)`；该分支直接加载 ZIP 并返回 `refreshed=False`，不会刷新或下载统计包。短线指标计算仍可能请求实时快照、日 K 和财务数据，因此本轮只用注入适配器与本地 ZIP 验证，不执行真实 TDX 请求。

当前工作区没有 `stock_common/cache/zhb`，本地 ZIP 读取回归使用临时目录中的最小合成 ZIP，不覆盖或生成项目缓存数据。

### 版本差异

- 当前系统安装：`levistock 0.1.7`、`axdata 0.1.3`。
- 独立临时环境候选：`levistock 0.1.8`、`axdata 0.1.4`。
- `levistock 0.1.8` 保留本项目调用的方法与签名；上游 Python 源码差异只涉及项目未调用的东财分页请求延迟。
- `axdata 0.1.4` 随包提供 `axdata_core` 和 `axdata_source_tdx`；统计 ZIP 解析/显式 `stats_root` 逻辑与 0.1.3 一致，其他差异包括多代码行情快照并行分发。本项目传入单只股票，当前调用不满足其大批量并行分支条件。
- 拟定版本约束：`levistock==0.1.8`、`axdata==0.1.4`；以阶段二隔离回归通过为落地条件。

## 分阶段实施

### 阶段一：事实与调用契约确认

- [x] 记录所有项目适配调用点、上层调用者、返回结构和缓存分类。
- [x] 对比当前安装版本与 PyPI 候选版本中的实际 Python 源码，而非仅依据版本号或 README。
- [x] 追踪 AxData 请求接口、TDX 适配器、`stats_root` 参数和 ZIP 加载分支。
- [x] 确认 `requirements-dev.txt` 通过 `-r requirements.txt` 继承运行时约束。

### 阶段二：候选版本隔离回归

- [x] 仅在系统站点包可见的临时 venv 中安装候选 wheel，不修改用户 Python 环境。
- [x] 用离线替身核对 Levistock 项目适配调用的函数路径、日期参数和返回归一化。
- [x] 生成包含 `tdxstat.cfg` 与 `tdxstat2.cfg` 的最小临时 ZIP，验证 AxData 新版从传入 `stats_root` 加载并保留统计日期。
- [x] 验证项目适配器选中 `stock_common/cache/zhb/zhb_*.zip` 中名称排序最新的本地 ZIP，并将完整路径传给 AxData。
- [x] 回归通过后固定候选版本 `levistock==0.1.8`、`axdata==0.1.4`。

### 阶段三：版本约束与回归测试

- [x] 将 `requirements.txt` 的宽范围改为通过阶段二回归的精确版本；不在 `requirements-dev.txt` 重复声明。
- [x] 新增离线适配器回归：Levistock 方法名/参数/返回结构与项目转换；AxData 本地 ZIP 路径及统计资源解析。
- [x] 使用临时 ZIP、替身网络适配器和项目临时缓存，不发送真实行情请求。

### 阶段四：文档与版本同步

- [x] 更新 `docs/UPSTREAM_COMPATIBILITY.md`，记录候选版本采用结论、已确认接口契约、AxData 本地路径与网络边界。
- [x] 在 README 增加依赖兼容计划和约束入口说明。
- [x] 在 CHANGELOG 记录此次依赖约束与离线回归变化。
- [x] 将项目最小补丁版本从 `17.4.27` 升至 `17.4.28`，同步 `docs/PROJECT_CONTEXT.md`。
- [x] 回填本计划实施结果和实测度量。

### 阶段五：验证与清理

- [x] 运行适配器专项测试，再运行仓库完整离线测试套件。
- [x] 对改动 Python 文件执行编译、Black、mypy 和敏感信息检查。
- [x] 运行数据访问 A1 与字典同步 A7 闸门、`git diff --check`，检查最终 diff。
- [x] 确认测试过程没有真实网络请求；清理临时探针与临时安装目录，保留原有用户改动。

## 不在本轮实施

- 不改五大报告脚本、采集/碰撞算法、字段字典、数据日期判定和 TDX 限流策略。
- 不因 AxData 的多股票并行能力增加项目批量请求或并发。
- 不更新全局 Python 包，不运行真实源测试，不修改本机缓存和采集数据。
- 不提交 Git；本次仓库已有未提交内容，需保留供用户后续审阅。

## 验收标准

1. 新环境运行 `pip install -r requirements.txt` 与 `pip install -r requirements-dev.txt` 时得到同一对已验证版本。
2. Levistock 适配器使用的实际方法、日期入参和返回形态都有离线回归证明。
3. AxData 接收到项目本地 `zhb_*.zip` 完整路径，使用该 ZIP 加载两份 CFG，且不进入统计包刷新/下载分支。
4. 无新增真实网络请求、限流变化或报告/采集业务逻辑变化。
5. 全量离线测试、静态检查与 A1/A7 闸门通过，未引入新高优先级问题。

## 实施结果与度量

依赖版本：`levistock 0.1.7 → 0.1.8`、`axdata 0.1.3 → 0.1.4`；新增 1 个离线测试模块、3 项回归；全量离线测试 `699 passed, 1 skipped, 47 deselected`（125.89 秒），定向测试 3 项通过；真实行情请求 0 次；本计划涉及 10 个项目文件。语法、Black、mypy、A1/A7 和 `git diff --check` 均通过。全量测试使用仓库内独立 `--basetemp`，因为执行环境的系统 `%TEMP%` pytest 默认目录不可写；生成的临时目录已清理。
