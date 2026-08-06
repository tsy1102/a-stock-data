# scratch/ — 调研沙盒目录

> 本目录是**一次性调研/实验沙盒**，不参与生产代码运行，**不承诺稳定性**。

## 定位（与 tests/、scripts/ 的区别）

| 目录 | 定位 | 内容 |
|:---|:---|:---|
| `tests/` | 自动化验证 | pytest 用例（run_tests.ps1 驱动，防退化守护）|
| `scripts/` | 可复用运维命令 | run_tests.ps1 / update_calendar / clean_cache / backtest 等 |
| `scratch/` | 一次性调研沙盒 | 字段破解、协议探索、临时验证脚本（用完即弃）|

## 使用约定

- **git 策略**：`scratch/*` 已被 `.gitignore` 忽略（除历史跟踪文件）；调研产物**不入库**
- **结论落库**：调研结论必须写入 `docs/field_dict.md` / `docs/roadmap.md` 等正式文档，scratch 脚本用完即删
- **引用路径**：不要引用 `scratch/` 内的相对路径（目录随时清空）；ZHB 数据请用 `cache/zhb/`

## 历史清理记录

- 2026-08-05：13 个子目录 + 39 个字段破解实验产物删除（结论已落库 field_dict V16.3 D2）
- 2026-08-06：早期调研脚本（get_real_data/parse_zhb/query_tipinfo/sample_all/search_mcap，引用已删路径）与审计过程产物（bug_scan*）删除；审计结论见 `docs/CODE_AUDIT_REPORT.md`

## 何时可以删除整个目录

所有调研迁移到主仓库后整体删除；当前保留作为快速实验区。
