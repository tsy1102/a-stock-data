# Eastmoney 日 K 字段注册范围审计（2026-11-11）

## 结论

`东财-em_kline_f61` 的真实字段路径为 `f51`–`f61`。之前的注册提取器把同一说明小节中用于比较其他接口的编号也归到了日 K 来源，形成三条错误身份：`f43`、`f85`、`f168`。本次修复了提取范围，并从权威 `source_fields` 移除这三条错误配对；其他来源下同名字段均保留。

## 证据

- 采集器 `scripts/capture_http_collectors.py::collect_em_kline_f61` 调用 `/api/qt/stock/kline/get`，请求 `fields2=f51..f61`；每行 K 线是按固定位置解析的 11 列记录。
- [`docs/field_source_reference.md` §12.3.3](../field_source_reference.md) 的字段表以 `fields2 列` 为表头，逐项列出 `f51` 到 `f61`。这些行是日 K 来源自己的字段契约。
- 同小节的端点编号说明提到实时行情 `stock/get` 的 `f43..f85`，目的是警告编号空间不同；它不表示这些是日 K 字段。
- `f168` 出现在描述实时 `stock/get` 当日快照换手率的对照表中，不属于日 K 的 `fields2` 表。
- 当前 `scripts/audit_field_completeness.py::reg_tokens_for_section` 曾对整个说明小节搜索所有 `f数字`。因此它把警告中的 `f43`、`f85` 和对照表中的 `f168` 当成日 K 注册项；其中前两项没有日 K 证据，`f168` 的参考证据也实际指向另一接口。

## 修复与影响

- `东财-em_kline_f61` 现在只从表头为 `fields2 列` 的日 K 字段表提取路径。
- `东财-em_kline_f61::f51`–`::f61` 保持不变；移除 `东财-em_kline_f61::f43`、`::f85`、`::f168`。
- `东财-push2(stock/get)`、`东财-ulist239(np/get)` 等其他来源的同名路径、状态及证据没有改动。
- 这是注册表身份纠错；未改采集、运行时路由、缓存、原始样本或只读 `field_source_reference.md`。
- `source_fields` 从 2,608 条减至 2,605 条；verified 从 1,395 减至 1,394，unverified 从 1,131 减至 1,129。解析状态 `matched` 减 1，`aggregate_status_scope_unresolved` 减 2。

回归覆盖真实 §12.3.3 小节与带有跨接口警告/对照表的最小样例。范围模块 9/9、注册表 parity 模块 20/20 通过；完整离线验收通过：语法检查 293 个文件、Mypy 271 个文件、Black 检查 276 个文件、注册表核心 parity `1872/2486/347`，离线测试 1,514 passed、1 skipped、52 deselected、12 subtests。
