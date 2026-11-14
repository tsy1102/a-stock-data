# 2026-11-15 Public Web Research

## 候选：`东财-push2ex::sector`

- 当前注册状态：`unverified`，`aggregate_status_scope_unresolved`。
- 候选解释：涨停池记录中的所属行业板块标签。
- 替代解释：泛化的板块/行业标签，其分类体系、层级或版本可能不同于其他来源同名的 `sector`。
- 区分依据：核实项目输出 `sector` 是否精确来自同一 Push2EX 响应中的 `hybk`，并以东方财富个股官方页“所属板块”标签作语义佐证。
- 来源身份：`source_lineage.json` 与 `field_source_reference.md` §12.8.1 将 `东财-push2ex` 对应到东方财富 Push2EX 涨停池接口。

## 路径与适配器核对

- `stock_common/sc_datasource/_pools.py::_parse_limit_pool` 将 `item.get("hybk", "")` 原样赋给输出 `sector`。
- 同文件 `get_yesterday_limit_pool` 也将 `item.get("hybk", "")` 原样赋给输出 `sector`。
- `docs/field_source_reference.md` §12.8.1 列出 `hybk | 所属行业板块 | - | sector`；注册表中的精确同源路径 `东财-push2ex::hybk` 已为 `verified`，释义为“所属行业板块”。
- 所以这里核验的是 Push2EX 自身的输出别名关系，不建立跨来源映射。

## 官方页面观察

页面均为东方财富个股官方页，访问时间为 2026-11-15 01:36:31 Asia/Shanghai。页面未显示可用于历史对齐的有效日期；以下内容只作为标签语义佐证。

| 股票 | 官方页面 | 页面标签 | 页面显示 | 对应保留样本 |
|:---|:---|:---|:---|:---|
| 002623 亚玛顿 | <https://quote.eastmoney.com/concept/sz002623.html?jump_to_web=true> | 所属板块 | `[光伏设备]相关个股` | 20261112 `raw_push2ex.json`：`limit_up_pool[].sector = 光伏设备` |
| 603396 金辰股份 | <https://quote.eastmoney.com/concept/sh603396.html?jump_to_web=true> | 所属板块 | `[光伏设备]相关个股` | 20261112 `raw_push2ex.json`：`limit_up_pool[].sector = 光伏设备` |

官方页面说明东方财富把该标签呈现在“所属板块”区域。页面日期没有与历史样本对齐，因此不把这两条作为 2026-11-12 的逐日数值匹配。

## 历史样本与日期资格

- 样本目录：`docs/field_verification/20261112/`；`meta.json.data_date = 20261112`、`capture_date = 20261113`。
- `meta.json.source_as_of_dates.push2ex` 缺失。故该目录中的 Push2EX 值不作为来源日期合格的正式碰撞输入；本记录只用其中两条值作为字段类别的辅助线索。
- 样本另有 000573 粤宏远Ａ：`sector = 房地产开`。因缺少与该样本同来源日期对齐的官方记录，不将其解释为完整分类名称，也不据此推断截断规则。
- 尝试打开官方接口 <https://push2ex.eastmoney.com/getTopicZTPool> 的公开研究请求未能由网页核验工具访问。没有读取或保存实时 API 响应，本结论不覆盖接口版本、未见字段或服务端标签生成规则。

## 结论范围

结果：`inconclusive`（针对历史逐值核验：页面未提供可与 Push2EX 样本对齐的来源日期）。字段角色由项目中的精确同源映射及已验证的 `hybk` 定义支持；官网标签和两条样本值仅作语义佐证。已按来源契约流程将精确路径 `东财-push2ex::sector` 登记为 verified。

本次不确认行业分类体系、分类层级、版本、别名/缩写规则、历史标签有效期，也不确认其他来源中的 `sector` 与本字段等价；没有新增跨源 `mappings`。若后续需要处理这些问题，须补充可追溯的官方分类定义或来源日期合格的全样本记录。
