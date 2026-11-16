# KPH 历史涨停接口分页与 KPL 候选审查

核查时间：2026-11-17 00:22–00:42（Asia/Shanghai）
核查范围：保留期内 KPH/KPL 样本、项目锁定的 AxData/Levistock 客户端实现、KPH 与 KPL 的候选 `cc1_293ab69338919f64b9816ab8b74d02e1aa50d6a10192e79decd3b09a6697eaec`。

## 发现

项目原来的 KPH 历史采集调用 AxData 0.1.4 的 `kph_limit_up_history`。本机安装包 `axdata_core/adapters/kph/request.py` 中，`_request_limit_history` 固定发送 `st=50`、`Index=0`，只请求一次后直接解析返回列表；接口没有接收或处理后续页。AxData 0.1.4 的字段目录将 `industry_limit_up_count` 描述为“同行业涨停数”，其解析位置为原始行索引 27。PyPI 当前发布页列出的最新版本仍为 0.1.4，版本产物的 provenance 指向 AxData 提交 `0f7975277dff840f5bc3c8757897e1627e2e43ee`。

锁定的 Levistock 0.1.8 客户端实现 [`stock_daban_his_kph.py`](https://github.com/fleetinglife/levistock/blob/main/levistock/stock/stock_daban_his_kph.py) 使用同一 KPH 历史接口、每页 50 行，并在页满时递增 `Index` 继续请求，直到返回短页。它也把索引 27 映射为 `industry_zt`，注释为“同行业涨停数”。AxData 与 Levistock 是客户端实现，不是 KPH 提供方的官方字段契约；因此这些定义只作为路径映射与请求行为的参考。

已有 KPH 原始样本中，多日 `row_count` 恰为 50；例如 2026-10-16 与 2026-11-02。由于当时的 AxData 适配器只读第一页，这些恰好 50 行的归档不能证明覆盖了该日全部记录。KPH 字段值仍是有效的逐股观测，但样本池可能受第一页排序影响。KPH 返回行数也不能当作市场全体涨停数的完整分母。

## 对碰撞候选的裁决

该候选比较 `kph.industry_limit_up_count` 与 `kpl.raw_columns.col_20`：11 个来源数据日、500 个逐股配对，整体命中率 90%；9 日全匹配，2026-10-16 命中率 54%（27/50），2026-11-02 命中率 46%（23/50）。两个低命中日均出现成片差异，且当前 KPH 样本的分页完整性不成立。

因此本轮不确认跨来源等价关系，也不将候选标为已证伪：客户端字段说明只能提供猜测方向，现有跨源结果既有大量精确吻合，也有两个明确失配日，且 KPH 返回集合存在截断风险。候选需等待完整分页样本及能区分差异来源的外部证据。该处置不影响对 KPH 字段来源内语义的单独审查；`industry_limit_up_count` 仍保持未验证，不写入主字典，也不创建 `mappings`。

## 修复与证据边界

KPH 历史采集现由项目自有适配器请求同一来源接口，按 50 行翻页直到短页，所有页共用 KPH 跨进程每秒一次的请求限流。请求关闭环境代理、不缓存、不重试；任一页失败、重复页或达到页数保护上限时整批失败，不保存部分记录。成功结果在 `raw_kph.json` 中记录 `page_size`、`pages_fetched`、`returned_rows` 和 `complete`，供后续核查样本完整性。

下一步碰撞只把 `pagination.complete=true` 的 KPH 样本计入完整集合；已有历史原始文件不改写。需要重新确认历史跨源关系时，应在获得额外授权后对目标历史数据日用修复后的适配器补采，再按双方实际来源日期重新碰撞。此轮不进行历史回补。

## 参考资料

- [AxData PyPI 0.1.4 发布页](https://pypi.org/project/axdata/0.1.4/)：发布时间、版本和源码 provenance；本地固定依赖为 `axdata==0.1.4`。
- [AxData 源码仓库](https://github.com/electkismet/AxData)：框架仓库；本地 0.1.4 适配器代码只用于确认请求参数与字段映射，不作为 KPH 官方契约。
- [Levistock KPH 历史接口实现](https://github.com/fleetinglife/levistock/blob/main/levistock/stock/stock_daban_his_kph.py)：分页循环及 `industry_zt` 客户端字段说明。
- 项目证据：`requirements.txt`、`stock_common/sc_datasource/_kph.py`、`docs/field_verification/collision_research_20261116/exploratory/20261116/after_capture_20261116_followup/20261116_collision_report.json`。
